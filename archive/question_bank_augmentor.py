
import json
import requests

# Config
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"
OUTPUT_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/hard_questions_augmented.json'

def generate_hard_questions(count=5):
    prompt = f"""
    Bạn là một chuyên gia ra đề thi Toán THPT lớp 11.
    Hãy tạo ra {count} câu hỏi trắc nghiệm về chương XÁC SUẤT ở mức độ VẬN DỤNG CAO (Khó).
    
    Yêu cầu:
    - Chủ đề: Xác suất có điều kiện, Bayes, hoặc bài toán đếm phức tạp.
    - Ngôn ngữ: Tiếng Việt.
    - Định dạng JSON:
    [
      {{
        "id": "new_hard_1",
        "question": "...",
        "options": ["A.", "B.", "C.", "D."],
        "answer": "...",
        "solution": "..."
      }}
    ]
    
    Chỉ trả về DUY NHẤT mã JSON.
    """
    
    try:
        payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        content = response.json()['response']
        # Clean JSON
        json_str = re.search(r'\[.*\]', content, re.DOTALL).group()
        return json.loads(json_str)
    except:
        return []

def main():
    import re
    print("Augmenting Question Bank (Spec 4: Hard Tasks)...")
    questions = generate_hard_questions(3)
    if questions:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"Generated {len(questions)} hard questions. Saved to {OUTPUT_FILE}")
    else:
        print("Failed to generate questions.")

if __name__ == "__main__":
    main()
