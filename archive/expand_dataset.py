import pandas as pd
import random
import json
import uuid
import hashlib
from datetime import datetime, timedelta
import os

# --- UTILITIES ---
def generate_hash(text, salt="GPS-AIedu-2026"):
    return hashlib.sha256((text + salt).encode()).hexdigest()

def get_timestamp(base_time, offset_minutes):
    new_time = base_time + timedelta(minutes=offset_minutes)
    return new_time.strftime("%d/%m/%Y %H:%M:%S")

# --- PERSONA LOGIC ---
STUDENT_PROFILES = {
    "giỏi": {
        "weight": 15,
        "satisfaction_range": (4, 5),
        "thinking_time_range": (0, 5),
        "gps_patterns": ["S", "G-S"]
    },
    "khá": {
        "weight": 35,
        "satisfaction_range": (4, 5),
        "thinking_time_range": (5, 15),
        "gps_patterns": ["G-P-S", "G-G-S"]
    },
    "trung bình": {
        "weight": 35,
        "satisfaction_range": (3, 4),
        "thinking_time_range": (10, 20),
        "gps_patterns": ["G-G-P-S", "G-P-P-S"]
    },
    "yếu": {
        "weight": 15,
        "satisfaction_range": (2, 4),
        "thinking_time_range": (15, 30),
        "gps_patterns": ["G-G-G-P-S", "G-G-G-P-P-S"]
    }
}

# Sample phrases for student dialogue variation
STUDENT_OPENERS = {
    "giỏi": ["Câu này em giải như sau:", "Em tính dùng biến cố bù cho nhanh.", "Xác suất này dễ, em làm được ngay."],
    "khá": ["Câu này em tính thế này đúng không thầy?", "Em đang phân vân giữa hai đáp án.", "Để em thử liệt kê xem sao."],
    "trung bình": ["Thầy hướng dẫn em bước đầu với.", "Câu này 'ít nhất' là sao hả thầy?", "Em chưa hiểu cách tính không gian mẫu bài này."],
    "yếu": ["Khó quá, em không hiểu gì luôn.", "Cho em đáp án đi thầy, em chịu chết.", "Xác suất là cái gì vậy ạ?"]
}

def generate_expanded_dataset(questions_path, output_path, n_students=60):
    # 1. Load Questions
    with open(questions_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # 2. Build Student List
    students = []
    profile_list = list(STUDENT_PROFILES.keys())
    weights = [p["weight"] for p in STUDENT_PROFILES.values()]
    
    for i in range(1, n_students + 1):
        p_type = random.choices(profile_list, weights=weights)[0]
        students.append({
            "id": f"HS{i:02d}",
            "profile": p_type,
            "class": random.choice(["11A1", "11A2", "11A3", "12B1"]),
            "hash": generate_hash(f"HS{i:02d}")
        })
    
    all_logs = []
    base_start_time = datetime(2026, 3, 16, 8, 0, 0)
    
    # 3. Generate interactions
    for s in students:
        profile_meta = STUDENT_PROFILES[s["profile"]]
        # Each student solves a subset or all questions
        # To make it "real", let's say they solve 15-25 random questions from the 45
        num_q = random.randint(15, 25)
        selected_q = random.sample(questions, num_q)
        
        # LEARNING CURVE: Track progress for this student
        solved_count = 0 
        
        # Assign a stable difficulty to each question based on solution complexity
        for q in questions:
            sol_len = len(q.get('solution', ''))
            if sol_len > 300: q['difficulty'] = 5
            elif sol_len > 200: q['difficulty'] = 4
            elif sol_len > 100: q['difficulty'] = 3
            else: q['difficulty'] = 2
        
        current_time_offset = random.randint(0, 10000) 
        
        for q in selected_q:
            # Progress factor: increase by 5% every 3 questions solved, max 40% improvement
            progress_ratio = min(0.4, (solved_count // 3) * 0.05)
            
            # Select pattern: High progress might lead to shorter GPS flows
            possible_patterns = profile_meta["gps_patterns"]
            if progress_ratio > 0.2 and s["profile"] in ["khá", "trung bình"]:
                possible_patterns = ["G-P-S", "S"]
            
            gps_flow = random.choice(possible_patterns).split('-')
            session_id = f"SES_{uuid.uuid4().hex[:6]}"
            
            for step_idx, step in enumerate(gps_flow):
                is_last = (step_idx == len(gps_flow) - 1)
                diff_val = q['difficulty']
                
                # Metadata - FORMALIZED LEARNING CURVE MODEL
                # T_think(k) = (T_base * D_i) / (1 + Lambda_prog(k))
                base_thinking = random.randint(*profile_meta["thinking_time_range"])
                thinking = int((base_thinking * diff_val) / (1 + progress_ratio) + random.randint(1, 2))
                
                # Stochastic Noise: P_noise = 0.07 (Ref: Baker et al., 2004)
                if random.random() < 0.07 and s["profile"] != "giỏi" and step_idx == 0:
                    noise_texts = ["Câu này lạ quá em chưa thấy bao giờ.", "Đợi em tí em đi lấy máy tính.", "Thầy ơi nãy em làm cách kia sao không ra?"]
                    student_text = random.choice(noise_texts)
                else:
                    if step_idx == 0:
                        student_text = random.choice(STUDENT_OPENERS[s["profile"]]) + f" (Q{q['id']})"
                    else:
                        student_text = f"Em hiểu rồi, bước tiếp theo thế nào ạ?"
                
                if is_last:
                    ai_text = f"[S] Chính xác! Đáp án đúng là {q['answer']}. " + q['solution'].split('\n')[0]
                    solved_count += 1
                else:
                    sol_lines = q['solution'].split('\n')
                    guide_txt = sol_lines[min(step_idx+1, len(sol_lines)-1)] if len(sol_lines) > 1 else "Thử suy nghĩ thêm nhé"
                    ai_text = f"[{step}] Thầy hướng dẫn nhé: " + guide_txt

                all_logs.append({
                    "Timestamp": get_timestamp(base_start_time, current_time_offset),
                    "Student ID": s["id"],
                    "Profile": s["profile"],
                    "Question": q["question"],
                    "AI Response": ai_text,
                    "Difficulty (1-5)": diff_val,
                    "GPS Step (Truth)": step,
                    "Thinking Time (minutes)": thinking,
                    "Progress Factor": round(progress_ratio, 2),
                    "Student Response": student_text
                })
                current_time_offset += (thinking + random.randint(1, 5))

    # 4. Save to CSV
    df = pd.DataFrame(all_logs)
    # Sort by timestamp to look like real server logs
    df['dt'] = pd.to_datetime(df['Timestamp'], format="%d/%m/%Y %H:%M:%S")
    df = df.sort_values('dt').drop(columns=['dt'])
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Generated {len(df)} interaction logs for {n_students} students.")
    print(f"File saved to: {output_path}")

if __name__ == "__main__":
    q_file = "c:/Users/quach/code/GPS_AIedu/data/processed/probabilities_questions.json"
    out_file = "c:/Users/quach/code/GPS_AIedu/data/processed/GPS_AIedu_Expanded_60.csv"
    generate_expanded_dataset(q_file, out_file, n_students=60)
