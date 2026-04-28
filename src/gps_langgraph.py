import json
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

# --- DATA LAYER ---
def load_questions():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        return {str(q['id']): q for q in json.load(f)}

QUESTIONS = load_questions()

# --- STATE DEFINITION ---
class AgentState(TypedDict):
    student_msg: str
    history: List[dict]
    qid: str
    intent: str # 'G', 'P', 'S', or 'Fallback'
    response: str
    ground_truth: dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

# --- CONFIGURATION & CACHE ---
import functools
import hashlib

# Sử dụng model 7B cho Thầy giáo để có tư duy sư phạm tốt nhất
llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2.5:7b", 
    temperature=0.1, # Giảm nhiệt độ để ổn định nhãn [G, P, S]
    timeout=60
)

# --- AI INTENT CLASSIFIER ---
def classify_intent(student_msg: str, history: List[dict]) -> str:
    prompt = f"""Bạn là bộ não điều phối của Gia sư GPS. Hãy phân loại tin nhắn của học sinh vào 1 trong 3 giai đoạn:
1. [G]uide: Khi học sinh mới bắt đầu, chưa biết làm gì, hoặc hỏi về khái niệm/phương pháp.
2. [P]ractice: Khi học sinh đã biết hướng đi nhưng đang thực hiện phép tính, xin gợi ý bước tiếp theo hoặc tính toán dở dang.
3. [S]olve: Khi học sinh đưa ra đáp số cuối cùng hoặc yêu cầu chốt kết quả.

Tin nhắn học sinh: "{student_msg}"
Lịch sử gần nhất: {history[-2:] if history else "Không có"}

Chỉ trả ra đúng 1 chữ cái: G hoặc P hoặc S. KHÔNG giải thích."""
    
    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        intent = response.content.strip().upper()
        return intent if intent in ['G', 'P', 'S'] else 'P'
    except:
        return 'P'

# Cache đơn giản lưu trong bộ nhớ
CACHE = {}

def get_response_with_cache(prompt, msg):
    cache_key = hashlib.md5((prompt + msg).encode()).hexdigest()
    if cache_key in CACHE:
        return CACHE[cache_key]
    
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=msg)
    ])
    CACHE[cache_key] = response.content
    return response.content

def load_system_prompt():
    with open("src/ai/system_prompt.md", "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PERSONA = load_system_prompt()

# --- NODES & TOOLS ---

def intent_router(state: AgentState):
    intent = classify_intent(state['student_msg'], state.get('history', []))
    return {"intent": intent, "ground_truth": QUESTIONS.get(state['qid'], {})}

def tool_guide(state: AgentState):
    gt = state['ground_truth']
    history = state.get('history', [])
    g_count = sum(1 for m in history if "[G]" in m.get('content', ''))
    total_turns = len(history)
    last_ai_msg = history[-1]['content'] if history and history[-1]['role'] == 'assistant' else ""
    
    # Trigger breakout if G count is high OR total turns are high (preventing hidden loops)
    if g_count >= 3 or total_turns >= 10:
        prompt = (
            f"{SYSTEM_PERSONA}\n\n"
            f"[DỮ LIỆU ĐỀ BÀI]: {gt.get('question', '')}\n"
            f"[LỜI GIẢI CHUẨN]: {gt.get('solution', '')}\n\n"
            f"[CẢNH BÁO]: Phiên học đang kéo dài ({total_turns} lượt). Học sinh đang bị kẹt.\n"
            "QUY TẮC PHÁ VỠ VÒNG LẶP: \n"
            "1. KHÔNG ĐƯỢC hỏi lại câu cũ.\n"
            "2. Hãy đưa ra CÔNG THỨC CỰC KỲ CỤ THỂ hoặc một VÍ DỤ SỐ LIỆU thay cho biến số.\n"
            "3. Hướng dẫn học sinh bấm máy tính để ra một con số cụ thể.\n"
            "Ví dụ: 'Để tính không gian mẫu, em dùng công thức C(30,3). Em thử bấm máy tính xem nó ra bao nhiêu?'\n"
            "Xưng Thầy - gọi Em."
        )
    else:
        prompt = f"{SYSTEM_PERSONA}\n\n[DỮ LIỆU ĐỀ BÀI]: {gt.get('question', '')}\n[LỜI GIẢI CHUẨN]: {gt.get('solution', '')}\n\n[QUY TẮC]: Bạn đang ở bước [G]. Hãy dựa vào LỜI GIẢI CHUẨN để giải thích ngắn gọn khái niệm cốt lõi. KẾT THÚC bằng 1 câu hỏi nhỏ dẫn dắt học sinh. Xưng Thầy - gọi Em."
    
    try:
        temp = 0.7 if (g_count >= 3 or total_turns >= 10) else 0.2
        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=state['student_msg'])
        ], config={"temperature": temp})
        content = response.content
        content = content.replace("Bạn", "Em").replace("bạn", "em").replace("Cháu", "Em").replace("cháu", "em")
        return {"response": f"[G] {content.replace('[G]', '').strip()}"}
    except Exception as e:
        return {"response": f"[G] Chào em, với bài toán này ta cần xác định không gian mẫu trước. Em hãy tính thử xem số cách chọn là bao nhiêu nhé?"}

def tool_practice(state: AgentState):
    gt = state['ground_truth']
    history = state.get('history', [])
    p_count = sum(1 for m in history if "[P]" in m.get('content', ''))
    total_turns = len(history)
    last_ai_msg = history[-1]['content'] if history and history[-1]['role'] == 'assistant' else ""
    
    if p_count >= 5 or total_turns >= 15:
        prompt = (
            f"{SYSTEM_PERSONA}\n\n"
            f"[DỮ LIỆU LỜI GIẢI CHUẨN]: {gt.get('solution', '')}\n"
            f"[CẢNH BÁO]: Học sinh hoàn toàn bế tắc sau {total_turns} lượt.\n"
            "[QUY TẮC PHÁ VỠ VÒNG LẶP]: Hãy cung cấp 70% phép tính hoặc gợi ý cực sát (Breakthrough). \n"
            "Ví dụ: Thay vì hỏi công thức, hãy viết hẳn: 'Ta có P = C(10,2)/C(30,3). Em hãy tính nốt giá trị này nhé.'\n"
            "KHÔNG ĐƯỢC ĐƯA ĐÁP ÁN CHỐT. Xưng Thầy - gọi Em."
        )
        prefix = "[P - Breakthrough]"
    elif p_count >= 2:
        prompt = (
            f"{SYSTEM_PERSONA}\n\n"
            f"[DỮ LIỆU LỜI GIẢI CHUẨN]: {gt.get('solution', '')}\n"
            "[QUY TẮC]: Học sinh kẹt ở [P]. Hãy dùng Concept Check để hỏi về định nghĩa cơ bản liên quan đến lời giải này. "
            "Xưng Thầy - gọi Em."
        )
        prefix = "[P - Concept Check]"
    else:
        prompt = (
            f"{SYSTEM_PERSONA}\n\n"
            f"[DỮ LIỆU LỜI GIẢI CHUẨN]: {gt.get('solution', '')}\n"
            "[QUY TẮC]: Bạn ở bước [P]. Hãy đưa ra gợi ý giàn giáo (Scaffolding). KHÔNG ĐƯỢC CUNG CẤP LỜI GIẢI TRỰC TIẾP. Xưng Thầy - gọi Em."
        )
        prefix = "[P]"
    
    try:
        temp = 0.5 if p_count >= 2 else 0.2
        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=state['student_msg'])
        ])
        content = response.content
        content = content.replace("Bạn", "Em").replace("bạn", "em").replace("Cháu", "Em").replace("cháu", "em")
        return {"response": f"{prefix} {content.replace('[P]', '').strip()}"}
    except Exception as e:
        return {"response": "[P] Em thử xem lại bước tính toán này nhé, có vẻ chưa chính xác lắm."}

def tool_solve(state: AgentState):
    gt = state['ground_truth']
    ans = gt.get('answer', 'N/A')
    prompt = f"{SYSTEM_PERSONA}\n\n[QUY TẮC]: Bạn đang ở bước [S]. Đáp án đúng: {ans}. Hãy xác nhận đáp án của học sinh và hỏi 'Tại sao?' để chốt bài."
    
    try:
        response = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=state['student_msg'])
        ])
        content = response.content
        content = content.replace("Bạn", "Em").replace("bạn", "em")
        return {"response": f"[S] {content.replace('[S]', '').strip()}"}
    except Exception as e:
        return {"response": f"[S] Chính xác! Kết quả là {ans}. Nhưng tại sao em lại ra được con số đó?"}

def fallback_node(state: AgentState):
    response = llm.invoke([
        SystemMessage(content=f"{SYSTEM_PERSONA}\n\nHọc sinh đang nói gì đó chưa rõ ràng. Hãy hỏi thăm và định hướng các em quay lại bài toán."),
        HumanMessage(content=state['student_msg'])
    ])
    return {"response": response.content}

# --- GRAPH CONSTRUCTION ---
workflow = StateGraph(AgentState)
workflow.add_node("router", intent_router)
workflow.add_node("G", tool_guide)
workflow.add_node("P", tool_practice)
workflow.add_node("S", tool_solve)
workflow.add_node("fallback", fallback_node)

workflow.set_entry_point("router")
workflow.add_conditional_edges("router", lambda x: x["intent"], {"G": "G", "P": "P", "S": "S", "Fallback": "fallback"})
workflow.add_edge("G", END)
workflow.add_edge("P", END)
workflow.add_edge("S", END)
workflow.add_edge("fallback", END)

app = workflow.compile()

# --- INTERFACE ---
def run_gps_tutor(qid: str, student_msg: str, history: List[dict] = []):
    gt = QUESTIONS.get(qid, {})
    initial_state = {
        "student_msg": student_msg,
        "history": history,
        "qid": qid,
        "intent": "",
        "response": "",
        "ground_truth": gt
    }
    result = app.invoke(initial_state)
    # Trích xuất nhãn từ response [G], [P], [S]
    resp = result.get("response", "")
    intent = "G"
    if "[P]" in resp: intent = "P"
    elif "[S]" in resp: intent = "S"
    
    return resp, intent
