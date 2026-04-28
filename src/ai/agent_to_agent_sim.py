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
STUDENT_MODEL = "qwen2.5:7b" # Nâng cấp lên 7B để tránh 'ngáo' vai
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

# Khởi tạo LLM cho Học sinh - Hạ temp xuống 0.4
student_llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=STUDENT_MODEL,
    temperature=0.4
)

# --- PERSONA DEFINITIONS (Aligned with Research Docs) ---
PERSONA_CONFIGS = {
    "HS0001": {
        "desc": "Học sinh GIỎI / TĂNG TỐC (Advanced/Fast)",
        "prompt": "BẠN LÀ HỌC SINH (EM), ĐANG HỌC BÀI VỚI THẦY GIÁO. Bạn tư duy nhanh, hay nhảy cóc bước. CẤM: Không được đóng vai giáo viên, không đưa lời khuyên. Nếu thầy gợi ý đúng hướng, hãy giải luôn toàn bộ bài toán ngay lập tức. Xưng em - gọi thầy."
    },
    "HS0002": {
        "desc": "Học sinh KHÁ / QUY CHUẨN (Good/Proactive)",
        "prompt": "BẠN LÀ HỌC SINH (EM). Bạn thuộc bài, làm theo gợi ý của thầy một cách cẩn thận. Bạn trình bày phép tính của mình và hỏi bước tiếp theo. Nếu đã hiểu khái niệm, hãy chủ động đề xuất cách tính tiếp theo. Xưng em - gọi thầy."
    },
    "HS0003": {
        "desc": "Học sinh TRUNG BÌNH / BỊ ĐỘNG (Typical/Normal)",
        "prompt": "BẠN LÀ HỌC SINH (EM). Bạn hơi lúng túng với công thức. Nếu sau 3 lần thầy hướng dẫn mà vẫn chưa rõ, hãy mạnh dạn chọn một phương án (C hay A) và hỏi 'Có phải dùng cái này không thầy?' để phá vỡ bế tắc. Xưng em - gọi thầy."
    },
    "HS0004": {
        "desc": "Học sinh YẾU / HAY QUÊN (Struggling/Slow)",
        "prompt": "BẠN LÀ HỌC SINH (EM). Bạn sợ toán và hay quên. Tuy nhiên, nếu thầy đã giải thích cùng một vấn đề trên 3 lần, hãy yêu cầu thầy 'Cho em một ví dụ cực kỳ đơn giản với số nhỏ' hoặc 'Ghi công thức cho em lắp số vào' để chúng ta có thể bước tiếp. Đừng chỉ lặp lại 'Em không hiểu'. Xưng em - gọi thầy."
    },
    "HS0005": {
        "desc": "Học sinh LƯỜI / XIN ĐÁP ÁN (Offtrack/Shortcut)",
        "prompt": "BẠN LÀ HỌC SINH (EM). Bạn chỉ muốn xin đáp án. Nếu thầy không cho, hãy thử nịnh hoặc giả vờ đã hiểu một nửa để thầy 'buông' đáp án ra. Xưng em - gọi thầy."
    }
}

# --- HELPERS ---
def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def clean_text(text):
    """Loại bỏ ký tự Trung Quốc và các ký tự lạ formatting."""
    import re
    # Loại bỏ dải ký tự Trung Quốc
    text = re.sub(r'[\u4e00-\u9fff]+', '', text)
    # Loại bỏ các ký tự formatting lỗi
    text = text.replace("]% ", "").replace("]%", "")
    return text.strip()

def log_to_csv(data):
    file_exists = os.path.isfile(LOG_OUTPUT_PATH)
    df = pd.DataFrame([data])
    df.to_csv(LOG_OUTPUT_PATH, mode='a', index=False, header=not file_exists, encoding='utf-8')

# --- SIMULATION CORE ---
def is_already_done(question_id, persona_id):
    if not os.path.isfile(LOG_OUTPUT_PATH):
        return False
    try:
        df = pd.read_csv(LOG_OUTPUT_PATH)
        # Kiểm tra xem đã có bản ghi [S] (kết thúc) cho cặp này chưa
        # Hoặc đơn giản là đã có dữ liệu lượt cuối cùng
        done = df[(df['QID'] == question_id) & (df['Student ID'] == persona_id)]
        return len(done) > 0 and any("[S]" in str(row) for row in done['AI Response'])
    except:
        return False

# --- SIMULATION CORE ---
def simulate_session(question_id, persona_id, learned_concepts=None, auto_mode=False):
    if is_already_done(question_id, persona_id):
        print(f"⏩ Skipping {persona_id} for Question {question_id} (Already completed)")
        return learned_concepts

    if learned_concepts is None:
        learned_concepts = []
    data = load_data()
    q_data = next((q for q in data if q['id'] == question_id), None)
    if not q_data:
        print(f"Question ID {question_id} not found.")
        return learned_concepts

    system_prompt = load_system_prompt()
    p_config = PERSONA_CONFIGS.get(persona_id, PERSONA_CONFIGS["HS0002"])
    
    print(f"\n🚀 START SIMULATION: {persona_id} | QID: {question_id}")
    
    # Tích hợp LangGraph App để chạy logic GPS chuẩn
    from gps_langgraph import app as gps_app

    history = []
    current_student_msg = f"Chào thầy, em đang làm bài này: {q_data['question']}. Thầy hướng dẫn em với ạ."
    
    # Thiết lập max_turns dựa trên độ khó
    if question_id in [1, 2, 3]:
        max_turns = 8
    elif question_id in [4, 5, 8, 9]:
        max_turns = 12
    else:
        max_turns = 20
    
    for turn in range(1, max_turns + 1):
        # 1. GPS Tutor Response
        inputs = {
            "student_msg": current_student_msg,
            "qid": str(question_id),
            "history": [{"role": "user" if i%2==0 else "assistant", "content": m.content} for i, m in enumerate(history)]
        }
        
        try:
            result = gps_app.invoke(inputs)
            tutor_resp = clean_text(result.get("response", "Thầy chưa rõ ý em."))
        except Exception as e:
            print(f"❌ Error in Tutor LLM: {e}")
            break
            
        # Hậu xử lý xưng hô Thầy
        tutor_resp = tutor_resp.replace("Bạn", "Em").replace("bạn", "em")
        
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
        
        # Cập nhật lịch sử
        history.append(HumanMessage(content=current_student_msg))
        history.append(SystemMessage(content=tutor_resp))

        # 2. Kiểm tra điều kiện dừng
        if "[S]" in tutor_resp and turn > 2:
            break

        # 3. Student Response
        knowledge_context = f"\n[KINH NGHIỆM ĐÃ CÓ]: {'. '.join(learned_concepts)}." if learned_concepts else ""
        student_system_prompt = (
            f"{p_config['prompt']}\n"
            f"{knowledge_context}\n"
            "YÊU CẦU BẮT BUỘC: 1. CHỈ DÙNG TIẾNG VIỆT. 2. Xưng 'em', gọi 'thầy'. 3. PHẢI tính toán. 4. Trình bày lời giải hoàn chỉnh khi hiểu."
        )

        for attempt in range(2): # Giảm attempt để nhanh hơn
            student_input = [
                SystemMessage(content=student_system_prompt),
                *history,
                HumanMessage(content="Hãy trả lời dưới vai trò Học sinh. Bắt đầu bằng 'Dạ thưa thầy, '.")
            ]
            try:
                raw_student_msg = student_llm.invoke(student_input).content
            except Exception as e:
                print(f"❌ Error in Student LLM: {e}")
                break

            if not raw_student_msg.strip().startswith("Dạ thưa thầy"):
                raw_student_msg = "Dạ thưa thầy, " + raw_student_msg
                
            current_student_msg = clean_text(raw_student_msg)
            
            hallucination_triggers = ["Chào em", "Chào Em", "Thầy hướng dẫn", "Thầy sẽ giúp"]
            if not any(trigger in current_student_msg for trigger in hallucination_triggers):
                break

        current_student_msg = current_student_msg.replace("Bạn", "Em").replace("bạn", "em").replace("tôi", "em").replace("Tôi", "Em")
        
    return learned_concepts

def run_batch(qids, personas, max_workers=3):
    from concurrent.futures import ThreadPoolExecutor
    
    print(f"🔥 Starting Batch Simulation with {max_workers} workers")
    
    tasks = []
    for p_id in personas:
        for qid in qids:
            tasks.append((qid, p_id))
            
    # Sắp xếp để chạy theo cụm câu hỏi (tối ưu cache Ollama)
    tasks.sort()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Lưu ý: learned_concepts trong chế độ song song sẽ khó đồng bộ 
        # nên mỗi phiên sẽ bắt đầu với bộ nhớ trống hoặc được load từ file riêng.
        # Ở đây ta ưu tiên chạy độc lập để tối ưu GPU.
        futures = [executor.submit(simulate_session, qid, pid) for qid, pid in tasks]
        for future in futures:
            future.result()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--range", type=str, help="Question range, e.g. 1-45")
    parser.add_argument("--qids", type=str, default="1,2,6", help="List of Question IDs")
    parser.add_argument("--personas", type=str, default="HS0001,HS0002,HS0003,HS0004,HS0005", help="Comma separated Persona IDs")
    parser.add_argument("--workers", type=int, default=3, help="Number of parallel workers")
    args = parser.parse_args()
    
    if args.range:
        start, end = map(int, args.range.split("-"))
        target_qids = list(range(start, end + 1))
    else:
        target_qids = [int(x.strip()) for x in args.qids.split(",")]
        
    target_personas = [x.strip() for x in args.personas.split(",")]
    
    print(f"🚀 BẮT ĐẦU CHIẾN DỊCH MÔ PHỎNG: {len(target_qids)} câu hỏi x {len(target_personas)} học sinh")
    
    # Chạy theo từng nhóm học sinh để đảm bảo learned_concepts nếu chạy tuần tự
    # Hoặc chạy song song hoàn toàn nếu ưu tiên tốc độ
    if args.workers > 1:
        run_batch(target_qids, target_personas, max_workers=args.workers)
    else:
        for p_id in target_personas:
            concepts_memory = []
            for qid in target_qids:
                concepts_memory = simulate_session(qid, p_id, learned_concepts=concepts_memory)
                time.sleep(1)
            
    print("\n🏁 CHIẾN DỊCH MÔ PHỎNG ĐÃ HOÀN TẤT.")

