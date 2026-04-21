import json
import os
import time
import pandas as pd
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11435/v1"
GPS_MODEL = "qwen2.5:7b"
STUDENT_MODEL = "qwen2.5:1.5b"
DATA_PATH = "data/processed/probabilities_questions.json"
SYSTEM_PROMPT_PATH = "src/ai/system_prompt.md"
LOG_OUTPUT_PATH = "data/processed/simulated_conversations.csv"

# --- LLM INITIALIZATION ---
tutor_llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=GPS_MODEL,
    temperature=0.2
)

student_llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=STUDENT_MODEL,
    temperature=0.7
)

# --- PERSONA DEFINITIONS (Aligned with Research Docs) ---
PERSONA_CONFIGS = {
    "HS0001": {
        "desc": "Học sinh GIỎI / TĂNG TỐC (Advanced/Fast)",
        "prompt": "Bạn là học sinh GIỎI. Bạn nắm chắc kiến thức và muốn kiểm tra kết quả nhanh. Bạn hay dùng thuật ngữ toán học chính xác. Nếu thầy gợi ý chậm, bạn sẽ chủ động đưa ra hướng giải của mình (bước S) để thầy xác nhận ngay. Tuyệt đối không đóng vai thầy giáo."
    },
    "HS0002": {
        "desc": "Học sinh TRUNG BÌNH / QUY CHUẨN (Typical/Normal)",
        "prompt": "Bạn là học sinh TRUNG BÌNH. Bạn học khá và rất ngoan, luôn tuân thủ hướng dẫn. Bạn đi theo lộ trình: hỏi khái niệm (G) -> xin gợi ý thực hành (P) -> giải bài (S). Bạn trả lời lịch sự và đầy đủ."
    },
    "HS0003": {
        "desc": "Học sinh YẾU / HAY QUÊN (Struggling/Slow)",
        "prompt": "Bạn là học sinh YẾU và hay SỢ TOÁN. Bạn thường xuyên quên kiến thức cũ và dễ bối rối. Hãy hỏi những câu như 'Xác suất là gì?', 'Tại sao lại là mẫu số đó?'. Thường xuyên yêu cầu thầy giải thích lại (Backtracking) dù thầy đã gợi ý sang bước tiếp theo."
    },
    "HS0004": {
        "desc": "Học sinh LƯỜI / XIN ĐÁP ÁN (Offtrack/Shortcut)",
        "prompt": "Bạn là học sinh MUỐN LẤY ĐÁP ÁN NHANH. Bạn lười tư duy và chỉ muốn hoàn thành bài tập sớm để đi chơi. Hãy liên tục hỏi 'Đáp án là bao nhiêu?', 'Thầy giải hộ em luôn đi', 'Em cần kết quả thôi'. Thể hiện sự thiếu kiên trì."
    },
    "HS0005": {
        "desc": "Học sinh NGẮT QUÃNG (Inactive)",
        "prompt": "Bạn là học sinh KHÔNG TẬP TRUNG. Bạn chỉ chat 2-3 câu ngắn rồi sẽ âm thầm biến mất không trả lời nữa."
    }
}

# --- HELPERS ---
def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def log_to_csv(data):
    file_exists = os.path.isfile(LOG_OUTPUT_PATH)
    df = pd.DataFrame([data])
    df.to_csv(LOG_OUTPUT_PATH, mode='a', index=False, header=not file_exists, encoding='utf-8')

# --- SIMULATION CORE ---
def simulate_session(question_id, persona_id, auto_mode=False):
    data = load_data()
    q_data = next((q for q in data if q['id'] == question_id), None)
    if not q_data:
        print(f"Question ID {question_id} not found.")
        return

    system_prompt = load_system_prompt()
    p_config = PERSONA_CONFIGS.get(persona_id, PERSONA_CONFIGS["HS0002"])
    
    print(f"\n==========================================================")
    print(f"🚀 START SIMULATION: {persona_id} ({p_config['desc']})")
    print(f"📝 Question {question_id}: {q_data['question']}")
    print(f"==========================================================\n")
    
    history = []
    current_student_msg = f"Chào thầy, em đang làm bài này: {q_data['question']}. Thầy hướng dẫn em với ạ."
    
    print(f"👨‍🎓 Student ({persona_id}): {current_student_msg}")
    
    max_turns = 8 if persona_id != "HS0005" else 3
    
    for turn in range(1, max_turns + 1):
        # 1. GPS Tutor Response
        tutor_input = [
            SystemMessage(content=f"{system_prompt}\n\nDỮ LIỆU ĐỐI CHỨNG: {q_data['solution']}\n\nLưu ý: Chỉ dùng dữ liệu trên để gợi ý. Luôn bắt đầu phản hồi bằng [G], [P] hoặc [S]."),
            *history,
            HumanMessage(content=current_student_msg)
        ]
        
        tutor_resp = tutor_llm.invoke(tutor_input).content
        print(f"👨‍🏫 Tutor: {tutor_resp}")
        
        # Log to CSV
        log_to_csv({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Student ID": persona_id,
            "Question": current_student_msg,
            "AI Response": tutor_resp,
            "Profile": persona_id,
            "QID": question_id,
            "Turn": turn
        })
        
        # Interjection logic
        if not auto_mode:
            user_input = input("\n[Tiếp tục: Enter | Can thiệp HS: 'H' | Can thiệp Tutor: 'T' | Dừng: 'S']: ").strip().upper()
            if user_input == 'S': break
            elif user_input == 'H':
                current_student_msg = input("Vai Học sinh: ")
                history.append(HumanMessage(content=current_student_msg))
                history.append(SystemMessage(content=tutor_resp))
                continue
            elif user_input == 'T':
                tutor_resp = input("Vai Gia sư (gồm nhãn [G/P/S]): ")

        history.append(HumanMessage(content=current_student_msg))
        history.append(SystemMessage(content=tutor_resp))
        
        # Check termination
        if "[S]" in tutor_resp and any(word in tutor_resp.lower() for word in ["chính xác", "hợp lý", "chúc mừng"]):
            print("\n✅ GOAL REACHED: Student correctly solved the problem.")
            break
            
        # 2. Student Response
        student_input = [
            SystemMessage(content=(
                f"{p_config['prompt']}\n"
                "QUY TẮC PHÁT NGÔN:\n"
                "- Bạn là HỌC SINH. Tuyệt đối KHÔNG xưng là thầy cô/trợ lý.\n"
                "- Trả lời ngắn gọn (1-3 câu).\n"
                "- Nếu thầy khen ở bước [S], hãy cảm ơn và hỏi bài mới hoặc kết thúc.\n"
                "- Tuyệt đối KHÔNG tự chào hỏi hay giải thích kiểu AI Assistant.\n"
                "- Nếu bạn đang ở vai HS0003, hãy thỉnh thoảng nói 'em chưa hiểu' dù thầy giải thích kỹ."
            )),
            *history
        ]
        
        current_student_msg = student_llm.invoke(student_input).content
        print(f"👨‍🎓 Student ({persona_id}): {current_student_msg}")
        
    print(f"\n✨ SIMULATION COMPLETED: {persona_id}")
    print(f"----------------------------------------------------------\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--qid", type=int, default=1, help="Question ID from JSON")
    parser.add_argument("--persona", type=str, default="ALL", help="Persona ID or 'ALL'")
    parser.add_argument("--auto", action="store_true", help="Run without user interjection")
    args = parser.parse_args()
    
    if args.persona == "ALL":
        for p_id in PERSONA_CONFIGS.keys():
            simulate_session(args.qid, p_id, auto_mode=True)
            time.sleep(2) # Cooldown
    else:
        simulate_session(args.qid, args.persona, auto_mode=args.auto)
