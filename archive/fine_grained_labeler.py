
import pandas as pd
import re
import os
import json
import requests

# Config
INPUT_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/gps_aiedu_gold_standard.csv'
OUTPUT_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/gps_aiedu_labeled_v2.csv'
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

def get_sub_strategy(teacher_response):
    prompt = f"""
    Bạn là một chuyên gia sư phạm. Hãy phân tích câu trả lời của giáo viên dưới đây và gán nhãn chiến thuật sư phạm:
    Câu trả lời: "{teacher_response}"
    
    Các nhãn:
    1. 'Concept Explanation': Giải thích khái niệm, định nghĩa.
    2. 'Scaffolding Hint': Gợi ý từng bước, không cho đáp án ngay.
    3. 'Error Correction': Phát hiện và sửa lỗi sai cho học sinh.
    4. 'Metacognitive Prompting': Đặt câu hỏi để học sinh tự suy nghĩ (Ví dụ: "Tại sao?", "Em nghĩ sao?").
    5. 'Direct Answer': Cho đáp án trực tiếp (Nên tránh).
    
    Chỉ trả về DUY NHẤT tên nhãn.
    """
    
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        return response.json()['response'].strip()
    except:
        return "Scaffolding Hint" # Fallback

def label_dataset(limit=50): # Limit for demo
    print(f"Starting Fine-grained Labeling (Spec 2) on first {limit} sessions...")
    df = pd.read_csv(INPUT_FILE)
    
    # We only process the teacher turns
    def label_session(dialogue):
        # Extract teacher turns
        teacher_turns = re.findall(r'Thầy: (.*?)(?=\nEm:|$)', dialogue, re.DOTALL)
        labels = []
        for turn in teacher_turns:
            label = get_sub_strategy(turn.strip())
            labels.append(label)
        return "|".join(labels)

    # Process a subset for demo
    subset = df.head(limit).copy()
    subset['Sub_Strategies'] = subset['Dialogue'].apply(label_session)
    
    subset.to_csv(OUTPUT_FILE, index=False)
    print(f"Labeled {limit} sessions saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    label_dataset(limit=20) # Just 20 for quick result
