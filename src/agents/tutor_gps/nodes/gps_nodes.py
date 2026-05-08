
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.tutor_gps.state import AgentState
from src.utils.llm_factory import get_llm

llm = get_llm()

def load_prompt(filename):
    with open(f"config/prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read().strip()

async def guide_node(state: AgentState):
    prompt_content = load_prompt("guide.txt")
    prompt = SystemMessage(content=prompt_content)
    lang_remind = HumanMessage(content="BẮT BUỘC trả lời bằng tiếng Việt. TUYỆT ĐỐI KHÔNG dùng tiếng Trung.")
    response = await llm.ainvoke([prompt] + list(state["messages"]) + [lang_remind])
    return {
        "messages": [response], 
        "trace_labels": state.get("trace_labels", []) + ["G"],
        "active_agent": "guide"
    }

async def practice_node(state: AgentState):
    prompt_content = load_prompt("practice.txt")
    prompt = SystemMessage(content=prompt_content)
    lang_remind = HumanMessage(content="BẮT BUỘC trả lời bằng tiếng Việt. TUYỆT ĐỐI KHÔNG dùng tiếng Trung.")
    response = await llm.ainvoke([prompt] + list(state["messages"]) + [lang_remind])
    
    # Đếm số bước P đã thực hiện để gán nhãn P1, P2...
    p_count = len([l for l in state.get("trace_labels", []) if "P" in l]) + 1
    return {
        "messages": [response], 
        "trace_labels": state.get("trace_labels", []) + [f"P{p_count}"],
        "active_agent": "practice"
    }

async def solve_node(state: AgentState):
    prompt_content = load_prompt("solve.txt")
    prompt = SystemMessage(content=prompt_content)
    lang_remind = HumanMessage(content="BẮT BUỘC trả lời bằng tiếng Việt. TUYỆT ĐỐI KHÔNG dùng tiếng Trung.")
    response = await llm.ainvoke([prompt] + list(state["messages"]) + [lang_remind])
    return {
        "messages": [response], 
        "trace_labels": state.get("trace_labels", []) + ["S"],
        "active_agent": "solve"
    }
