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

# Mặc định dùng Ollama cho tiết kiệm chi phí
llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="gemma2:9b", 
    temperature=0.3,
    timeout=60
)

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
    msg = state['student_msg'].lower()
    # Phân loại ý định
    if any(word in msg for word in ["đáp số", "kết quả", "là", "bằng"]):
        intent = "S"
    elif any(word in msg for word in ["hướng dẫn", "giải thích", "tại sao"]):
        intent = "G"
    else:
        intent = "P"
    return {"intent": intent, "ground_truth": QUESTIONS.get(state['qid'], {})}

def tool_guide(state: AgentState):
    gt = state['ground_truth']
    prompt = f"{SYSTEM_PERSONA}\n\nĐÂY LÀ GIAI ĐOẠN [G].\nGợi ý toán học chính xác: {gt.get('solution', '')}\nHãy viết phản hồi hướng dẫn học sinh theo đúng tone của bạn."
    
    try:
        content = get_response_with_cache(prompt, state['student_msg'])
        return {"response": content}
    except Exception as e:
        return {"response": f"[G] Thầy đang gặp chút trục trặc. Gợi ý nhanh: {gt.get('solution', '').split('.')[0]}."}

def tool_practice(state: AgentState):
    gt = state['ground_truth']
    prompt = f"{SYSTEM_PERSONA}\n\nĐÂY LÀ GIAI ĐOẠN [P].\nNội dung cần luyện tập dựa trên: {gt.get('question', '')}\nHãy đưa ra một câu hỏi phụ hoặc gợi ý giàn giáo."
    
    try:
        content = get_response_with_cache(prompt, state['student_msg'])
        return {"response": content}
    except Exception as e:
        return {"response": "[P] Thầy chưa kịp soạn câu hỏi phụ, nhưng em thử tính xác suất của biến cố đối xem sao?"}

def tool_solve(state: AgentState):
    gt = state['ground_truth']
    ans = gt.get('answer', 'N/A')
    prompt = f"{SYSTEM_PERSONA}\n\nĐÂY LÀ GIAI ĐOẠN [S].\nĐÁP ÁN ĐÚNG LÀ: {ans}. Lời giải chi tiết: {gt.get('solution', '')}\nHãy đối chiếu lời giải của học sinh, chốt đáp án và hỏi phản tư."
    
    try:
        content = get_response_with_cache(prompt, state['student_msg'])
        return {"response": content}
    except Exception as e:
        return {"response": f"[S] Rất tiếc thầy chưa kiểm tra kỹ được, nhưng đáp án chuẩn bài này là {ans}. Em đối chiếu thử nhé!"}

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
workflow.add_edge("G", END); workflow.add_edge("P", END); workflow.add_edge("S", END); workflow.add_edge("fallback", END)

app = workflow.compile()
