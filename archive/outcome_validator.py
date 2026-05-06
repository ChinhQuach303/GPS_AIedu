
import pandas as pd
import re
import requests

# Config
INPUT_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/gps_aiedu_labeled_v2.csv'
OUTPUT_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/gps_aiedu_validated.csv'
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"

def judge_learning(dialogue, ground_truth):
    prompt = f"""
    Bạn là một giám khảo độc lập. Hãy chấm điểm mức độ hiểu bài của học sinh dựa trên cuộc hội thoại sau.
    
    Hội thoại:
    {dialogue}
    
    Đáp án đúng (Ground Truth): {ground_truth}
    
    Tiêu chí chấm điểm (0-100):
    1. Độ chính xác: Học sinh có ra đáp án đúng không?
    2. Độ tự chủ: Học sinh tự giải hay AI giải hộ?
    3. Độ hiểu sâu: Học sinh có giải thích được tại sao không?
    
    Chỉ trả về DUY NHẤT một con số từ 0 đến 100.
    """
    
    try:
        payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        score_str = re.search(r'\d+', response.json()['response'])
        return int(score_str.group()) if score_str else 50
    except:
        return 50

def main():
    print("Starting Outcome Validation (Spec 3: LLM-as-a-Judge)...")
    df = pd.read_csv(INPUT_FILE)
    
    # We use a subset for demo
    subset = df.head(10).copy()
    
    # Mock ground truth for demo if not available
    subset['Validated_Score'] = subset.apply(lambda r: judge_learning(r['Dialogue'], "Dữ liệu mẫu"), axis=1)
    
    # Calculate Estimated Learning Gain (eLG)
    # eLG = (Validated_Score - Pre_Score) / (100 - Pre_Score)
    # Mock Pre_Score based on level
    pre_map = {'Giỏi': 70, 'Khá': 55, 'Trung bình': 40, 'Yêu': 25}
    subset['Pre_Score'] = subset['Level'].map(pre_map)
    subset['eLG'] = (subset['Validated_Score'] - subset['Pre_Score']) / (100 - subset['Pre_Score'])
    
    subset.to_csv(OUTPUT_FILE, index=False)
    print(f"Validated {len(subset)} sessions with LLM-as-a-Judge. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
