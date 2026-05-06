import json
import os
import random
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/v1"
MODEL = "qwen2.5:7b"
OUTPUT_PATH = "data/processed/augmented_sessions_sample.csv"

llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=MODEL,
    temperature=0.7
)

# --- PERSONA GENERATOR (Vietnam Distribution) ---
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

# --- FEW-SHOT EXAMPLE (GOLD STANDARD) ---
FEW_SHOT_GPS = """
Ví dụ mẫu GPS:
Thầy: [G] Chào Em! Bài toán này yêu cầu tìm xác suất... Em thử liệt kê xem có bao nhiêu kết quả trong không gian mẫu?
Em: Dạ thưa thầy, mỗi lần gieo súc sắc có 6 mặt nên tổng số kết quả là 6x6=36 ạ.
Thầy: [P] Rất tốt! Bây giờ em tính biến cố đối 'Không xuất hiện mặt 6 nào' nhé.
Em: Dạ, mỗi lần có 5 cách không ra mặt 6, nên là 5x5=25 cách ạ.
Thầy: [S] Chính xác! Vậy xác suất ít nhất một lần mặt 6 là 1 - 25/36 = 11/36. Em đã hiểu bài rồi đó!
"""

# --- RAPID SESSION GENERATOR PROMPTS ---
def generate_gps_session_prompt(persona, question_data):
    return (
        f"{FEW_SHOT_GPS}\n\n"
        f"Hãy đóng vai hai nhân vật: THẦY GIÁO (Tutor) và HỌC SINH (Em).\n"
        f"HỌC SINH: {persona['behavior']}\n"
        f"BÀI TOÁN: {question_data['question']}\n"
        f"LỜI GIẢI CHUẨN: {question_data['solution']}\n"
        f"ĐÁP ÁN ĐÚNG: {question_data['answer']}\n\n"
        "YÊU CẦU NGHIÊM NGẶT:\n"
        "1. NGÔN NGỮ: CHỈ SỬ DỤNG TIẾNG VIỆT 100%. TUYỆT ĐỐI KHÔNG DÙNG TIẾNG ANH (anymore, thank you, teacher...).\n"
        "2. QUY TRÌNH GPS: Thầy dẫn dắt từng bước [G], bắt học sinh làm [P], rồi mới chốt [S].\n"
        "3. ĐỘ DÀI: Khoảng 6-10 lượt chat.\n"
        "4. Xưng hô: Thầy - Em.\n"
        "HÃY VIẾT TOÀN BỘ CUỘC ĐỐI THOẠI."
    )

def generate_non_gps_session_prompt(persona, question_data):
    return (
        f"Hãy đóng vai hai nhân vật: THẦY GIÁO (Tutor) và HỌC SINH (Em).\n"
        f"BÀI TOÁN: {question_data['question']}\n"
        f"LỜI GIẢI CHI TIẾT: {question_data['solution']}\n"
        f"ĐÁP ÁN ĐÚNG: {question_data['answer']}\n\n"
        "YÊU CẦU NGHIÊM NGẶT (PHONG CÁCH BÀI GIẢNG):\n"
        "1. NGÔN NGỮ: CHỈ SỬ DỤNG TIẾNG VIỆT 100%.\n"
        "2. PHƯƠNG PHÁP: Thầy trình bày toàn bộ lời giải và đáp án trong 1 lượt nói duy nhất. KHÔNG ĐẶT CÂU HỎI NGƯỢC LẠI.\n"
        "3. Lượt tiếp theo: Học sinh xác nhận đã hiểu và cảm ơn.\n"
        "4. Cuộc đối thoại cực kỳ ngắn gọn (chỉ 2-3 lượt chat).\n"
        "HÃY VIẾT TOÀN BỘ CUỘC ĐỐI THOẠI."
    )

def run_full_campaign(batch_size=50):
    # 1. Setup 60 students (30 GPS, 30 Non-GPS)
    gps_students = get_persona_distribution(30)
    nongps_students = get_persona_distribution(30)
    
    # 2. Setup questions (45 questions)
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    output_file = "data/processed/augmented_conversations_final.csv"
    
    # Initialize CSV with headers
    if not os.path.exists(output_file):
        pd.DataFrame(columns=["Group", "Student_ID", "Level", "QID", "Dialogue"]).to_csv(output_file, index=False)
    
    print(f"--- BẮT ĐẦU CHIẾN DỊCH AUGMENTATION TOÀN DIỆN: 2700 PHIÊN ---")
    
    count = 0
    batch_results = []
    
    for q in questions:
        # Group GPS
        for s in gps_students:
            try:
                print(f"🔄 Đang sinh GPS: {s['id']} | QID: {q['id']} (Tổng: {count+1}/2700)...")
                gps_resp = llm.invoke([SystemMessage(content=generate_gps_session_prompt(s, q))]).content
                batch_results.append({"Group": "GPS", "Student_ID": f"GPS_{s['id']}", "Level": s['level'], "QID": q['id'], "Dialogue": gps_resp})
                count += 1
            except Exception as e:
                print(f"❌ Lỗi tại GPS {s['id']} QID {q['id']}: {e}")
            
            # Save batch
            if len(batch_results) >= batch_size:
                pd.DataFrame(batch_results).to_csv(output_file, mode='a', header=False, index=False)
                batch_results = []
                print(f"💾 Đã lưu đợt dữ liệu (Tổng tích lũy: {count})")

        # Group Non-GPS
        for s in nongps_students:
            try:
                print(f"🔄 Đang sinh Non-GPS: {s['id']} | QID: {q['id']} (Tổng: {count+1}/2700)...")
                non_gps_resp = llm.invoke([SystemMessage(content=generate_non_gps_session_prompt(s, q))]).content
                batch_results.append({"Group": "Non-GPS", "Student_ID": f"NON_{s['id']}", "Level": s['level'], "QID": q['id'], "Dialogue": non_gps_resp})
                count += 1
            except Exception as e:
                print(f"❌ Lỗi tại Non-GPS {s['id']} QID {q['id']}: {e}")
            
            # Save batch
            if len(batch_results) >= batch_size:
                pd.DataFrame(batch_results).to_csv(output_file, mode='a', header=False, index=False)
                batch_results = []
                print(f"💾 Đã lưu đợt dữ liệu (Tổng tích lũy: {count})")
                
    # Final save
    if batch_results:
        pd.DataFrame(batch_results).to_csv(output_file, mode='a', header=False, index=False)
        
    print(f"\n🎉 CHIẾN DỊCH HOÀN TẤT. Tổng số: {count} phiên học.")

if __name__ == "__main__":
    run_full_campaign()
