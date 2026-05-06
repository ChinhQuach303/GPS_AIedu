import json
import os
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
import time

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/v1"
MODEL = "qwen2.5:7b"
OUTPUT_FILE = "GPS_AIedu/data/processed/augmented_conversations_final.csv"
CONCURRENCY = 4  # Optimized for RTX 3060 (12GB)

llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=MODEL,
    temperature=0.7
)

# --- PERSONA GENERATOR ---
def get_persona_distribution(total=30):
    dist = {
        "Giỏi": int(total * 0.14),
        "Khá": int(total * 0.33),
        "Trung bình": int(total * 0.40),
        "Yếu": total - int(total * 0.14) - int(total * 0.33) - int(total * 0.40)
    }
    
    personas = []
    idx = 1
    for level, count in dist.items():
        for _ in range(count):
            personas.append({
                "id": f"S_{idx:02d}",
                "level": level,
                "behavior": f"Bạn là học sinh lớp 12 có học lực {level}. " + 
                            ("Bạn giải bài rất nhanh và tự tin." if level == "Giỏi" else 
                             "Bạn hiểu bài nhưng cần thầy hướng dẫn các bước khó." if level == "Khá" else
                             "Bạn hay quên công thức và cần thầy nhắc lại khái niệm." if level == "Trung bình" else
                             "Bạn rất sợ toán xác suất, thường xuyên bế tắc và cần được giảng giải tỉ mỉ.")
            })
            idx += 1
    return personas

# --- FEW-SHOT EXAMPLE ---
FEW_SHOT_GPS = """
Ví dụ mẫu GPS:
Thầy: [G] Chào Em! Bài toán này yêu cầu tìm xác suất... Em thử liệt kê xem có bao nhiêu kết quả trong không gian mẫu?
Em: Dạ thưa thầy, mỗi lần gieo súc sắc có 6 mặt nên tổng số kết quả là 6x6=36 ạ.
Thầy: [P] Rất tốt! Bây giờ em tính biến cố đối 'Không xuất hiện mặt 6 nào' nhé.
Em: Dạ, mỗi lần có 5 cách không ra mặt 6, nên là 5x5=25 cách ạ.
Thầy: [S] Chính xác! Vậy xác suất ít nhất một lần mặt 6 là 1 - 25/36 = 11/36. Em đã hiểu bài rồi đó!
"""

def generate_gps_session_prompt(persona, question_data):
    return (
        f"{FEW_SHOT_GPS}\n\n"
        f"Hãy đóng vai hai nhân vật: THẦY GIÁO (Tutor) và HỌC SINH (Em).\n"
        f"HỌC SINH: {persona['behavior']}\n"
        f"BÀI TOÁN: {question_data['question']}\n"
        f"LỜI GIẢI CHUẨN: {question_data['solution']}\n"
        f"ĐÁP ÁN ĐÚNG: {question_data['answer']}\n\n"
        "YÊU CẦU NGHIÊM NGẶT:\n"
        "1. NGÔN NGỮ: CHỈ SỬ DỤNG TIẾNG VIỆT 100%. TUYỆT ĐỐI KHÔNG DÙNG TIẾNG TRUNG (HÁN TỰ) VÀ TIẾNG ANH.\n"
        "2. CẤM TUYỆT ĐỐI các từ như: '简化', '后可以得到', 'teacher', 'anymore'... Yêu cầu dùng thuần tiếng Việt (Ví dụ: 'Sau khi đơn giản hóa ta được...').\n"
        "3. QUY TRÌNH GPS: Thầy dẫn dắt từng bước [G], bắt học sinh làm [P], rồi mới chốt [S].\n"
        "4. ĐỘ DÀI: Khoảng 6-10 lượt chat.\n"
        "5. Xưng hô: Thầy - Em.\n"
        "HÃY VIẾT TOÀN BỘ CUỘC ĐỐI THOẠI BẰNG TIẾNG VIỆT."
    )

def generate_non_gps_session_prompt(persona, question_data):
    return (
        f"Hãy đóng vai hai nhân vật: THẦY GIÁO (Tutor) và HỌC SINH (Em).\n"
        f"BÀI TOÁN: {question_data['question']}\n"
        f"LỜI GIẢI CHI TIẾT: {question_data['solution']}\n"
        f"ĐÁP ÁN ĐÚNG: {question_data['answer']}\n\n"
        "YÊU CẦU NGHIÊM NGẶT (PHONG CÁCH BÀI GIẢNG):\n"
        "1. NGÔN NGỮ: CHỈ SỬ DỤNG TIẾNG VIỆT 100%. TUYỆT ĐỐI KHÔNG DÙNG TIẾNG TRUNG HOẶC TIẾNG ANH.\n"
        "2. PHƯƠNG PHÁP: Thầy trình bày toàn bộ lời giải và đáp án trong 1 lượt nói duy nhất. KHÔNG ĐẶT CÂU HỎI NGƯỢC LẠI.\n"
        "3. Lượt tiếp theo: Học sinh xác nhận đã hiểu và cảm ơn.\n"
        "4. Cuộc đối thoại cực kỳ ngắn gọn (chỉ 2-3 lượt chat).\n"
        "HÃY VIẾT TOÀN BỘ CUỘC ĐỐI THOẠI BẰNG TIẾNG VIỆT."
    )

def get_existing_sessions():
    if not os.path.exists(OUTPUT_FILE):
        return set()
    existing = set()
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('GPS,') or line.startswith('Non-GPS,'):
                    parts = line.split(',')
                    if len(parts) >= 4:
                        existing.add((parts[0], parts[1], parts[3]))
        return existing
    except Exception as e:
        print(f"⚠️ Warning reading file manually: {e}")
        return set()

async def process_session(q, s, group, session_type, existing, progress_info):
    qid = str(q['id'])
    student_id = f"{'GPS' if session_type == 'gps' else 'NON'}_{s['id']}"
    group_name = "GPS" if session_type == "gps" else "Non-GPS"
    
    if (group_name, student_id, qid) in existing:
        return None

    try:
        prompt = generate_gps_session_prompt(s, q) if session_type == "gps" else generate_non_gps_session_prompt(s, q)
        # Use asyncio to run the blocking LLM call in a thread
        loop = asyncio.get_event_loop()
        
        resp = ""
        for attempt in range(3):
            resp = await loop.run_in_executor(None, lambda: llm.invoke([SystemMessage(content=prompt)]).content)
            # Check for Chinese characters (Hanzi)
            import re
            if not re.search(r'[\u4e00-\u9fff]', resp):
                break
            print(f"⚠️ Detected Chinese characters in response (QID: {qid}, {s['id']}). Retrying {attempt+1}/3...")
        
        progress_info['count'] += 1
        print(f"✅ [{progress_info['count']}/{progress_info['total']}] {group_name} | QID: {qid} | {s['id']}")
        
        return {
            "Group": group_name,
            "Student_ID": student_id,
            "Level": s['level'],
            "QID": qid,
            "Dialogue": resp
        }
    except Exception as e:
        print(f"❌ Error {group_name} {s['id']} QID {qid}: {e}")
        return None

async def main():
    gps_students = get_persona_distribution(30)
    nongps_students = get_persona_distribution(30)
    
    with open("GPS_AIedu/data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    existing = get_existing_sessions()
    print(f"--- PARALLEL RESUME (RTX 3060) ---")
    print(f"Found {len(existing)} existing sessions. Concurrency: {CONCURRENCY}")
    
    total_target = 45 * 60
    progress_info = {'count': len(existing), 'total': total_target}
    
    tasks = []
    # Create all tasks
    for q in questions:
        for s in gps_students:
            tasks.append((q, s, "gps"))
        for s in nongps_students:
            tasks.append((q, s, "nongps"))
    
    # Filter out existing
    tasks_to_run = []
    for q, s, s_type in tasks:
        student_id = f"{'GPS' if s_type == 'gps' else 'NON'}_{s['id']}"
        group_name = "GPS" if s_type == "gps" else "Non-GPS"
        if (group_name, student_id, str(q['id'])) not in existing:
            tasks_to_run.append((q, s, s_type))
            
    print(f"Remaining tasks: {len(tasks_to_run)}")
    
    # Run in batches of CONCURRENCY
    batch_results = []
    for i in range(0, len(tasks_to_run), CONCURRENCY):
        chunk = tasks_to_run[i:i + CONCURRENCY]
        chunk_tasks = [process_session(q, s, None, s_type, existing, progress_info) for q, s, s_type in chunk]
        results = await asyncio.gather(*chunk_tasks)
        
        # Filter None results
        valid_results = [r for r in results if r is not None]
        batch_results.extend(valid_results)
        
        # Save every 10 completions
        if len(batch_results) >= 10:
            pd.DataFrame(batch_results).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
            batch_results = []
            # print(f"💾 Saved batch. Total: {progress_info['count']}")

    if batch_results:
        pd.DataFrame(batch_results).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
        
    print(f"🎉 DONE. Final: {progress_info['count']}")

if __name__ == "__main__":
    asyncio.run(main())
