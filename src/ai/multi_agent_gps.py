from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
import os

# --- STATE DEFINITION ---
class AgentState(TypedDict):
    student_msg: str
    history: List[dict]
    qid: str
    intent: str
    response: str
    ground_truth: dict
    iteration_count: int

# --- LLM INITIALIZATION ---
# Sử dụng 1.5b cho Intent để nhanh và tránh kẹt
intent_llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2.5:1.5b",
    temperature=0.0
)

# Sử dụng 1.5b cho Pedagogy (Tạm thời do 7b kẹt)
pedagogy_llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2.5:1.5b",
    temperature=0.2
)

def load_questions():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        return {str(q['id']): q for q in json.load(f)}

QUESTIONS = load_questions()

# --- AGENT 1: INTENT CLASSIFIER ---
def intent_agent(state: AgentState):
    """Phân tích ý định của học sinh và gán nhãn G, P, S kèm lý do."""
    gt = state['ground_truth']
    prompt = (
        "Bạn là chuyên gia phân tích bài làm Toán. Hãy so sánh câu trả lời của học sinh với ĐÁP ÁN CHUẨN.\n"
        "QUY TẮC PHÂN LOẠI:\n"
        "- Nếu học sinh đã đưa ra con số ĐÁP ÁN ĐÚNG (ví dụ: 1/16, 0.25...): Trả về 'S'.\n"
        "- Nếu học sinh đang tính toán dở dang hoặc sai số: Trả về 'P'.\n"
        "- Nếu học sinh nói không biết làm hoặc sai hoàn toàn: Trả về 'G'.\n\n"
        f"[ĐÁP ÁN CHUẨN]: {gt.get('answer', '')}\n"
        "CHỈ TRẢ VỀ DUY NHẤT 1 CHỮ CÁI G, P HOẶC S. KHÔNG GIẢI THÍCH."
    )
    
    try:
        response = intent_llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"Học sinh nói: {state['student_msg']}")
        ])
        intent = response.content.strip().upper()
        if len(intent) > 1:
            intent = intent[0] # Lấy chữ cái đầu tiên nếu AI viết dài
        if intent not in ['G', 'P', 'S']:
            intent = 'G'
    except Exception as e:
        intent = "G"
    
    return {"intent": intent}

# --- AGENT 2: PEDAGOGY EXECUTOR ---
def pedagogy_agent(state: AgentState):
    """Dựa trên Intent và Lịch sử, soạn thảo câu trả lời sư phạm đỉnh cao."""
    intent = state['intent']
    gt = state['ground_truth']
    history = state.get('history', [])
    total_turns = len(history)
    
    # Chiến thuật sư phạm nâng cao
    if intent == 'G':
        if total_turns >= 8:
            strategy = "BREAKTHROUGH: Học sinh kẹt quá lâu. Đưa ra CÔNG THỨC và số liệu cụ thể để lắp vào."
        else:
            strategy = "GUIDE: Giải thích khái niệm gốc, hỏi về dữ kiện đề bài."
    elif intent == 'P':
        if total_turns >= 12:
            strategy = "DIRECT HINT: Đưa ra 70% lời giải, yêu cầu tính nốt đáp án cuối."
        else:
            strategy = "PRACTICE: Yêu cầu thực hiện bước tính toán tiếp theo."
    else:
        strategy = "SOLVE: Chốt đáp án, khen ngợi và đặt câu hỏi 'Tại sao?' để kiểm tra độ sâu."

    prompt = (
        f"Bạn là Thầy giáo dạy Toán (GPS Protocol). Nhiệm vụ: Dẫn dắt học sinh tự tìm ra lời giải.\n"
        f"CHIẾN THUẬT: {strategy}\n\n"
        f"[ĐỀ BÀI]: {gt.get('question', '')}\n"
        f"[LỜI GIẢI CHUẨN]: {gt.get('solution', '')}\n"
        "QUY TẮC TỐI THƯỢNG (PHẢI TUÂN THỦ):\n"
        "1. CẤM TUYỆT ĐỐI đưa ra lời giải hoàn chỉnh hoặc đáp án cuối cùng.\n"
        "2. CHỈ đưa ra 01 câu hỏi hoặc 01 gợi ý nhỏ tại mỗi lượt chat.\n"
        "3. Nếu học sinh hỏi đáp án, hãy khéo léo từ chối và hỏi một câu hỏi gợi mở.\n"
        "4. Xưng Thầy - gọi Em.\n"
        "5. Dùng LaTeX cho công thức.\n"
        "Hành động: Hãy viết một câu phản hồi NGẮN GỌN (dưới 50 từ) để dẫn dắt học sinh."
    )
    
    temp = 0.7 if total_turns >= 10 else 0.2
    
    response = pedagogy_llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state['student_msg'])
    ], config={"temperature": temp})
    
    return {"response": f"[{intent}] {response.content}"}

# --- GRAPH CONSTRUCTION ---
def create_multi_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Thêm các nút tác tử
    workflow.add_node("classifier", intent_agent)
    workflow.add_node("executor", pedagogy_agent)
    
    # Thiết lập luồng: Classifier -> Executor -> End
    workflow.set_entry_point("classifier")
    workflow.add_edge("classifier", "executor")
    workflow.add_edge("executor", END)
    
    return workflow.compile()

multi_agent_tutor = create_multi_agent_graph()

# --- INTERFACE ---
def run_multi_agent_tutor(qid: str, student_msg: str, history: List[dict] = []):
    gt = QUESTIONS.get(qid, {})
    initial_state = {
        "student_msg": student_msg,
        "history": history,
        "qid": qid,
        "intent": "",
        "response": "",
        "ground_truth": gt,
        "iteration_count": 0
    }
    result = multi_agent_tutor.invoke(initial_state)
    return result['response'], result['intent']
