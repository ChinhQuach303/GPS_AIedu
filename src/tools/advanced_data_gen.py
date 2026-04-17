import pandas as pd
import random
import uuid
import hashlib
from datetime import datetime, timedelta

def generate_hash(text, salt="GPS-AIedu-2026"):
    return hashlib.sha256((text + salt).encode()).hexdigest()

def generate_advanced_mock_data(n_students=30, logs_per_student=15):
    topics = [
        "Đạo hàm ứng dụng (Tối ưu hóa)", 
        "Tích phân xác định (Diện tích)", 
        "Xác suất Bayes (Nâng cao)", 
        "Dãy số & Giới hạn", 
        "Nhị thức Newton (Hệ số phức hợp)"
    ]
    
    classes = ["11A1", "12A1", "12A2"]
    
    # Behavior Profiles
    profiles = {
        "Fast-Learner": {"G": 0.05, "P": 0.15, "S": 0.80, "think": (1, 3)},
        "Backtracker": {"G": 0.30, "P": 0.40, "S": 0.30, "think": (5, 12)}, # Often goes S -> G
        "Misconception-Prone": {"G": 0.40, "P": 0.40, "S": 0.20, "think": (8, 15)},
        "Normal": {"G": 0.20, "P": 0.50, "S": 0.30, "think": (3, 8)}
    }

    questions_pool = {
        "G": [
            "Tại sao trong bài toán tối ưu diện tích ta phải xét đạo hàm f'(x)=0?",
            "Phân biệt ý nghĩa của tích phân và diện tích hình phẳng.",
            "Khi nào dùng công thức Bayes thay vì xác suất cổ điển?",
            "Điều kiện để một dãy số có giới hạn hữu hạn là gì?",
            "Giải thích công thức số hạng tổng quát của Nhị thức Newton."
        ],
        "P": [
            "Em đã lập được hàm f(x) = x(20-2x), giờ tính đạo hàm thế nào AI?",
            "Tính diện tích giới hạn bởi y=x^2 và y=x, em kẹt ở bước tìm cận.",
            "Bài toán xét nghiệm bệnh: P(A)=0.01, P(B|A)=0.99. Bước tiếp theo tính gì?",
            "Chứng minh dãy u(n) = (n+1)/n bị chặn dưới bởi 1 thế nào?",
            "Tìm hệ số x^5 trong (2x - 1/x)^10, em viết khai triển rồi nhưng chưa rút gọn được."
        ],
        "S": [
            "Kết quả diện tích lớn nhất là 50m2 đúng không AI?",
            "Đáp số tích phân em ra là 1/3, AI xem logic em đúng chưa?",
            "Xác suất mắc bệnh là 0.091, đáp án này hợp lý không ạ?",
            "Giới hạn của dãy là 1. Em làm đúng chưa?",
            "Hệ số là -8064, AI chốt đáp án giúp em."
        ]
    }

    data = []
    base_time = datetime(2026, 4, 1, 8, 0, 0)
    
    for i in range(n_students):
        student_id = f"HS{1000+i}"
        student_hash = generate_hash(student_id)
        cls = random.choice(classes)
        p_name = random.choice(list(profiles.keys()))
        p_cfg = profiles[p_name]
        
        current_time = base_time + timedelta(days=random.randint(0, 10), hours=random.randint(0, 8))
        
        last_step = None
        for j in range(logs_per_student):
            # Markov-ish state selection based on profile
            if last_step == "S" and p_name == "Backtracker" and random.random() < 0.6:
                step = "G" # Forced backtracking
            else:
                step = random.choices(["G", "P", "S"], weights=[p_cfg["G"], p_cfg["P"], p_cfg["S"]])[0]
            
            topic = random.choice(topics)
            question = random.choice(questions_pool[step])
            
            think_time = random.uniform(p_cfg["think"][0], p_cfg["think"][1])
            sat = random.randint(3, 5) if p_name != "Misconception-Prone" else random.randint(2, 4)
            diff = random.randint(1, 3) if p_name == "Fast-Learner" else random.randint(3, 5)
            
            row = {
                "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Student ID": student_id,
                "Class": cls,
                "Topic": topic,
                "Profile": p_name,
                "Question": question,
                "AI Response": f"Phản hồi AI giả lập cho bước {step}...",
                "Notes": "Auto-generated Phase 2",
                "Satisfaction (1-5)": sat,
                "Difficulty (1-5)": diff,
                "GPS Step (Truth)": step,
                "Auto Label": "Solve" if step == "S" else ("Practice" if step == "P" else "Guide"),
                "Student Hash": student_hash,
                "Thinking Time (minutes)": round(think_time, 2),
                "Group": "Experimental",
                "Message ID": f"MSG_{uuid.uuid4().hex[:8]}"
            }
            data.append(row)
            current_time += timedelta(minutes=random.randint(20, 60))
            last_step = step

    df = pd.DataFrame(data)
    output_path = "/home/chinh303/code/aiedu/data/processed/advanced_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(data)} logs to {output_path}")

if __name__ == "__main__":
    generate_advanced_mock_data(n_students=30, logs_per_student=20)
