import json
import os
import time
import pandas as pd
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.student_sim.multi_agent_gps import run_multi_agent_tutor

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/v1"
STUDENT_MODEL = "qwen2.5:7b"
DATA_PATH = "data/processed/probabilities_questions.json"
OUTPUT_PATH = "data/processed/multi_agent_sim_final.csv"

student_llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=STUDENT_MODEL,
    temperature=0.4
)

PERSONA_CONFIGS = {
    "HS0001": {"prompt": "BẠN LÀ HỌC SINH (EM) GIỎI. Bạn tư duy nhanh, giải bài quyết đoán. Xưng em - gọi thầy."},
    "HS0002": {"prompt": "BẠN LÀ HỌC SINH (EM) KHÁ. Bạn cẩn thận, làm theo gợi ý. Xưng em - gọi thầy."},
    "HS0003": {"prompt": "BẠN LÀ HỌC SINH (EM) TRUNG BÌNH. Bạn hơi lúng túng. Xưng em - gọi thầy."},
    "HS0004": {"prompt": "BẠN LÀ HỌC SINH (EM) YẾU. Bạn hay bối rối, sợ toán. Xưng em - gọi thầy."},
    "HS0005": {"prompt": "BẠN LÀ HỌC SINH (EM) LƯỜI. Bạn hay xin đáp án. Xưng em - gọi thầy."}
}

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def log_to_csv(data):
    file_exists = os.path.isfile(OUTPUT_PATH)
    df = pd.DataFrame([data])
    df.to_csv(OUTPUT_PATH, mode='a', index=False, header=not file_exists, encoding='utf-8')

def simulate_multi_agent_session(qid, persona_id):
    data = load_data()
    q_data = next((q for q in data if q['id'] == int(qid)), None)
    
    print(f"\n🚀 [MULTI-AGENT] SIMULATING: {persona_id} | QID: {qid}")
    
    history = []
    current_student_msg = f"Chào thầy, em đang làm bài này: {q_data['question']}. Thầy hướng dẫn em với ạ."
    max_turns = 20
    
    for turn in range(1, max_turns + 1):
        # 1. Multi-Agent Tutor Response
        tutor_resp, intent = run_multi_agent_tutor(str(qid), current_student_msg, history=[{"role": "user" if i%2==0 else "assistant", "content": m.content} for i, m in enumerate(history)])
        
        # Log to CSV
        log_to_csv({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Architecture": "Multi-Agent",
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
            print(f"✅ Success at Turn {turn}")
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

def run_chunk(start_q, end_q):
    personas = list(PERSONA_CONFIGS.keys())
    qids = range(start_q, end_q + 1)
    
    print(f"\n=== CHẠY CỤM CÂU HỎI {start_q} ĐẾN {end_q} ===")
    
    for qid in qids:
        for pid in personas:
            simulate_multi_agent_session(qid, pid)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=5)
    args = parser.parse_args()
    
    run_chunk(args.start, args.end)
    print(f"\n✅ ĐÃ HOÀN THÀNH CỤM {args.start}-{args.end}. HÃY KIỂM TRA CHẤT LƯỢNG TRƯỚC KHI TIẾP TỤC.")
