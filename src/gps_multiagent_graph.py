import operator
from typing import Annotated, List, Literal, TypedDict, Union

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

# --- 1. DATA LAYER (Reuse existing question data) ---
import json
def load_questions():
    try:
        with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
            return {str(q['id']): q for q in json.load(f)}
    except:
        return {}

QUESTIONS = load_questions()

# --- 2. STATE DEFINITION ---
class AgentState(TypedDict):
    # Annotated with operator.add to append messages to history
    messages: Annotated[List[BaseMessage], operator.add]
    qid: str
    student_level: str # 'Giỏi', 'Khá', 'Trung bình', 'Yếu'
    next_step: str # 'G', 'P', 'S', or 'End'
    ground_truth: dict
    current_phase: str # 'Guide', 'Practice', 'Solve'
    p_count: int # For Fading Scaffolding rule

# --- 3. MODELS & CONFIG ---
def load_system_prompt():
    with open("src/ai/system_prompt.md", "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PERSONA = load_system_prompt()

llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2.5:7b",
    temperature=0.1
)

# --- 4. TOOLS ---
from langchain_core.tools import tool

@tool
def verify_math_step(calculation: str, expected_result: str):
    """Checks if a student's calculation matches the expected result."""
    # Simple check for demo purposes
    if str(expected_result) in calculation:
        return "Correct step."
    return f"Incorrect. The expected result was related to {expected_result}."

@tool
def get_pedagogical_hint(qid: str, phase: str):
    """Retrieves a specific hint from the ground truth solution based on the current phase."""
    gt = QUESTIONS.get(qid, {})
    solution = gt.get('solution', 'No solution available.')
    if phase == 'Guide':
        return f"Concept: {solution[:100]}... Focus on explaining the definition."
    elif phase == 'Practice':
        return f"Step: Look at the intermediate calculation: {solution}."
    return "Final check: Verify if the answer matches the solution."

tools = [verify_math_step, get_pedagogical_hint]

# --- 5. SPECIALIZED AGENTS (ReAct) ---

# Guide Agent
guide_agent = create_react_agent(
    llm, 
    tools=tools,
    prompt=f"""{SYSTEM_PERSONA}
    
    BẠN ĐANG Ở BƯỚC: [G] GUIDE.
    NHIỆM VỤ: Dẫn dắt học sinh hiểu bản chất vấn đề.
    Dùng ReAct để tra cứu kiến thức hoặc gợi ý bước đầu tiên."""
)

# Practice Agent
practice_agent = create_react_agent(
    llm, 
    tools=tools,
    prompt=f"""{SYSTEM_PERSONA}
    
    BẠN ĐANG Ở BƯỚC: [P] PRACTICE.
    NHIỆM VỤ: Giàn giáo cho các bước tính toán.
    LƯU Ý: Nếu p_count >= 3, áp dụng quy tắc Fading Scaffolding (Concept Check).
    Dùng ReAct để xác minh các bước tính của học sinh."""
)

# Solve Agent
solve_agent = create_react_agent(
    llm, 
    tools=tools,
    prompt=f"""{SYSTEM_PERSONA}
    
    BẠN ĐANG Ở BƯỚC: [S] SOLVE.
    NHIỆM VỤ: Chốt đáp án và kiểm tra độ hiểu sâu (Metacognition).
    Dùng ReAct để hỏi 'Tại sao' và giải thích logic cuối cùng."""
)

# --- 6. SUPERVISOR NODE ---

def supervisor_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1].content
    history_len = len(messages)
    p_count = state.get("p_count", 0)
    
    # Advanced logic for breakthrough
    if history_len > 12:
        # Force breakthrough if session is too long
        return {"next_step": "Practice", "current_phase": "Breakthrough"}

    prompt = f"""Bạn là bộ não điều phối của Gia sư GPS. Hãy phân loại tin nhắn của học sinh:
    Tin nhắn: "{last_message}"
    
    1. 'G' (Guide): Học sinh mới bắt đầu, chưa biết hướng đi, hoặc hỏi về lý thuyết.
    2. 'P' (Practice): Học sinh đang giải, gửi phép tính, hoặc hỏi bước tiếp theo.
    3. 'S' (Solve): Học sinh gửi đáp án cuối cùng.
    
    Trả về DUY NHẤT 1 chữ cái G, P, hoặc S."""
    
    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        decision = response.content.strip().upper()
        if 'G' in decision: 
            next_agent = "Guide"
        elif 'S' in decision: 
            next_agent = "Solver"
        else: 
            next_agent = "Practice"
            p_count += 1 # Increment practice count
    except:
        next_agent = "Guide"
    
    return {"next_step": next_agent, "p_count": p_count}

# --- 7. GRAPH CONSTRUCTION ---

def create_gps_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("Supervisor", supervisor_node)
    builder.add_node("Guide", lambda state: guide_agent.invoke(state))
    builder.add_node("Practice", lambda state: practice_agent.invoke(state))
    builder.add_node("Solver", lambda state: solve_agent.invoke(state))
    
    builder.set_entry_point("Supervisor")
    
    builder.add_conditional_edges(
        "Supervisor",
        lambda state: state["next_step"],
        {
            "Guide": "Guide",
            "Practice": "Practice",
            "Solver": "Solver"
        }
    )
    
    builder.add_edge("Guide", END)
    builder.add_edge("Practice", END)
    builder.add_edge("Solver", END)
    
    return builder.compile()

gps_graph = create_gps_graph()

# --- 8. RUNNER ---
def run_tutor(qid: str, student_msg: str, history: List[BaseMessage] = []):
    gt = QUESTIONS.get(qid, {})
    input_messages = history + [HumanMessage(content=student_msg)]
    
    initial_state = {
        "messages": input_messages,
        "qid": qid,
        "student_level": "Trung bình", # Default
        "next_step": "",
        "ground_truth": gt,
        "current_phase": "Guide",
        "p_count": 0
    }
    
    final_state = gps_graph.invoke(initial_state)
    return final_state["messages"][-1].content

if __name__ == "__main__":
    # Test run
    msg = "Chào thầy, em không biết bắt đầu từ đâu với bài gieo đồng tiền này."
    response = run_tutor("1", msg)
    print(f"AI: {response}")
