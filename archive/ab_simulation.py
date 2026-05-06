import json
import os
import time
import pandas as pd
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/v1"
GPS_MODEL = "qwen2.5:7b"
STUDENT_MODEL = "qwen2.5:7b"
DATA_PATH = "data/processed/probabilities_questions.json"
LOG_OUTPUT_PATH = "data/processed/ab_test_raw_data.csv"

# --- LLM INITIALIZATION ---
student_llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=STUDENT_MODEL,
    temperature=0.4
)

PERSONA_CONFIGS = {
    "HS0001": {"prompt": "BẠN LÀ HỌC SINH (EM) GIỎI. Bạn tư duy nhanh, giải bài quyết đoán. Xưng em - gọi thầy."},
    "HS0004": {"prompt": "BẠN LÀ HỌC SINH (EM) YẾU. Bạn hay bối rối, cần được thầy cầm tay chỉ việc. Xưng em - gọi thầy."}
}

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def log_to_csv(data):
    file_exists = os.path.isfile(LOG_OUTPUT_PATH)
    df = pd.DataFrame([data])
    df.to_csv(LOG_OUTPUT_PATH, mode='a', index=False, header=not file_exists, encoding='utf-8')

def run_ab_simulation(qid, persona_id, architecture_type="Single"):
    """
    architecture_type: "Single" hoặc "Multi"
    """
    data = load_data()
    q_data = next((q for q in data if q['id'] == int(qid)), None)
    
    # Import Tutor tương ứng
    if architecture_type == "Multi":
        from src.ai.multi_agent_gps import run_multi_agent_tutor as tutor_fn
    else:
        from src.gps_langgraph import run_gps_tutor as tutor_fn

    print(f"\n[A/B TEST] {architecture_type}-Agent | {persona_id} | QID: {qid}")
    
    history = []
    current_student_msg = f"Chào thầy, em đang làm bài này: {q_data['question']}. Thầy hướng dẫn em với ạ."
    max_turns = 15
    
    for turn in range(1, max_turns + 1):
        # 1. Tutor Response
        tutor_resp, intent = tutor_fn(str(qid), current_student_msg, history=[{"role": "user" if i%2==0 else "assistant", "content": m.content} for i, m in enumerate(history)])
        
        # Log to CSV
        log_to_csv({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Architecture": architecture_type,
            "Student ID": persona_id,
            "QID": qid,
            "Turn": turn,
            "Intent": intent,
            "Question": current_student_msg,
            "AI Response": tutor_resp
        })
        
        history.append(HumanMessage(content=current_student_msg))
        history.append(SystemMessage(content=tutor_resp))

        if "[S]" in tutor_resp:
            print(f"✅ Completed in {turn} turns.")
            return turn

        # 2. Student Response
        p_config = PERSONA_CONFIGS[persona_id]
        student_input = [
            SystemMessage(content=f"{p_config['prompt']}\nYÊU CẦU: Xưng 'em', gọi 'thầy'. Trình bày phép tính."),
            *history,
            HumanMessage(content="Hãy trả lời dưới vai trò Học sinh. Bắt đầu bằng 'Dạ thưa thầy, '.")
        ]
        try:
            current_student_msg = student_llm.invoke(student_input).content
        except:
            break
            
    return max_turns

if __name__ == "__main__":
    test_cases = [
        ("1", "HS0001"), ("1", "HS0004"),
        ("20", "HS0001"), ("20", "HS0004"),
        ("43", "HS0001"), ("43", "HS0004")
    ]
    
    final_results = []
    
    for qid, pid in test_cases:
        # Chạy Single
        s_turns = run_ab_simulation(qid, pid, "Single")
        # Chạy Multi
        m_turns = run_ab_simulation(qid, pid, "Multi")
        
        final_results.append({
            "QID": qid,
            "Persona": pid,
            "Single_Turns": s_turns,
            "Multi_Turns": m_turns
        })
        
    print("\n=== KẾT QUẢ SO SÁNH PILOT ===")
    print(pd.DataFrame(final_results))
