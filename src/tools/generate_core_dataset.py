import pandas as pd
import json
import random
import uuid
import hashlib
from datetime import datetime, timedelta

# Load real questions
with open('c:/Users/quach/code/GPS_AIedu/data/processed/probabilities_questions.json', 'r', encoding='utf-8') as f:
    questions_pool = json.load(f)

def generate_hash(text, salt="GPS-AIedu-2026"):
    return hashlib.sha256((text + salt).encode()).hexdigest()

# Student Personas
STUDENTS = [
    {"id": "HS_AN", "name": "An", "profile": "Advanced (giỏi)", "style": "speed", "sat_range": (5, 5)},
    {"id": "HS_BINH", "name": "Bình", "profile": "Struggling (chậm)", "style": "struggle", "sat_range": (3, 4)},
    {"id": "HS_CHI", "name": "Chi", "profile": "Offtrack (hay xin đáp án)", "style": "impatient", "sat_range": (2, 4)},
    {"id": "HS_DUONG", "name": "Dương", "profile": "Typical (đại trà)", "style": "reflective", "sat_range": (4, 5)},
    {"id": "HS_MAI", "name": "Mai", "profile": "Typical (đại trà)", "style": "standard", "sat_range": (4, 5)}
]

def get_dialogue_for_step(step, question_data, style):
    q_text = question_data['question']
    sol = question_data['solution']
    
    # Simple placeholders - In a real run, these would be rich LLM outputs.
    # Here we simulate high-quality interaction based on the solution logic.
    
    if step == "G":
        if style == "struggle":
            q = f"Thầy ơi câu này em chưa biết bắt đầu từ đâu. {q_text[:30]}..."
            a = f"[G] Chào Bình! Với bài này, trước hết em cần xác định không gian mẫu. Đề bài yêu cầu gì nhỉ?"
        elif style == "impatient":
            q = f"Đáp án câu này là gì dạ thầy? {q_text[:30]}..."
            a = f"[G] Thầy không cho đáp án ngay đâu. Em hãy thử phân tích xem đây là bài toán chọn mẫu hay gieo xúc sắc?"
        else:
            q = f"Dạ thầy hướng dẫn em hướng giải bài này với ạ: {q_text[:50]}..."
            a = f"[G] Để giải bài này, em cần xác định hai yếu tố: Số phần tử không gian mẫu và số kết quả thuận lợi. Em tính không gian mẫu trước nhé."
            
    elif step == "P":
        if style == "speed":
            q = "Em tính được |Ω| rồi, giờ áp dụng công thức xác suất cổ điển đúng không thầy?"
            a = "[P] Đúng rồi An. Em liệt kê các trường hợp thuận lợi ra nhé."
        elif style == "struggle":
            q = "Em tính |Ω| mãi không ra, thầy gợi ý bước này được không?"
            a = f"[P] Hãy nhìn vào dữ kiện này: {sol.split('.')[0]}. Em thử nhân các khả năng lại xem."
        else:
            q = "Em đã có không gian mẫu, giờ tìm số biến cố thuận lợi thế nào ạ?"
            a = "[P] Em hãy chia bài toán thành các trường hợp nhỏ như trong lời giải nhé. Thử liệt kê TH1 xem nào."

    elif step == "S":
        q = f"Em tính ra đáp án là {question_data['answer']}. Thầy kiểm tra giúp em logic này: {sol[:50]}..."
        a = f"[S] Chính xác rồi! Logic của em rất chặt chẽ. Kết quả là {question_data['answer']} với xác suất như trong giải chi tiết. Tốt lắm!"
    
    return q, a

def generate_core_dataset():
    data = []
    base_time = datetime(2026, 4, 10, 8, 0, 0)
    
    for student in STUDENTS:
        current_time = base_time + timedelta(hours=random.randint(0, 48))
        
        # Each student does all 45 questions for maximum "Real Power"
        for q_item in questions_pool:
            session_id = f"SES_{uuid.uuid4().hex[:6]}"
            
            # Determine flow based on style
            if student['style'] == "speed":
                flow = ["G", "P", "S"]
            elif student['style'] == "struggle":
                flow = ["G", "G", "P", "P", "S"]
            elif student['style'] == "impatient":
                flow = ["G", "G", "P", "S"]
            else:
                flow = ["G", "P", "S"]

            for step in flow:
                q, a = get_dialogue_for_step(step, q_item, student['style'])
                
                think_time = random.uniform(2, 5) if student['style'] != "struggle" else random.uniform(6, 12)
                sat = random.randint(student['sat_range'][0], student['sat_range'][1])
                
                row = {
                    "Timestamp": current_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "Student ID": student['id'],
                    "Class": "11A1",
                    "Topic": "Xác suất phổ thông",
                    "Profile": student['profile'],
                    "Question": q,
                    "AI Response": a,
                    "Notes": f"Q_ID: {q_item['id']} | Session: {session_id}",
                    "Satisfaction (1-5)": sat,
                    "Difficulty (1-5)": random.randint(2, 4),
                    "GPS Step (Truth)": step,
                    "Auto Label": step,
                    "Student Hash": generate_hash(student['id']),
                    "Thinking Time (minutes)": round(think_time, 2)
                }
                data.append(row)
                current_time += timedelta(minutes=int(think_time) + 2)

    df = pd.DataFrame(data)
    output_path = "c:/Users/quach/code/GPS_AIedu/data/processed/GPS_AIedu_Data - QA - Raw Data.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Generated {len(df)} entries for 5 students across 45 questions.")

if __name__ == "__main__":
    generate_core_dataset()
