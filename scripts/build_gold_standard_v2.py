
import asyncio
import pandas as pd
import re
from scripts.generate_authentic_dataset import main as run_generation
from src.eval.cognitive_judge import process_evaluation

def compute_math_independence(text):
    """
    Tính tỷ lệ token toán học (LaTeX) của học sinh so với toàn bộ phiên.
    Đây là metric công bằng cho cả GPS và Non-GPS.
    """
    if not isinstance(text, str): return 0.0
    
    # Tìm các đoạn LaTeX
    math_pattern = r'\\\(.*?\\\)|\\\[.*?\\\]|\$[^$]+\$'
    
    lines = text.split('\n')
    ai_math_count = 0
    student_math_count = 0
    
    for line in lines:
        math_tokens = len(re.findall(math_pattern, line))
        line_lower = line.lower()
        if line_lower.startswith('ai:') or line_lower.startswith('thầy:'):
            ai_math_count += math_tokens
        elif line_lower.startswith('student:') or line_lower.startswith('em:'):
            student_math_count += math_tokens
            
    total_math = ai_math_count + student_math_count
    if total_math == 0: return 0.0
    return round(student_math_count / total_math, 3)

async def build_gold_v2():
    raw_csv = "data/processed/authentic_research_data.csv"
    judged_csv = "data/processed/gps_aiedu_gold_v2.csv"
    
    # 1. Sinh dữ liệu thực (Resume tự động nếu file tồn tại)
    await run_generation()
    
    # 2. Chấm điểm ngữ nghĩa (LLM-as-a-Judge)
    await process_evaluation(raw_csv, judged_csv)
    
    # 3. Tính toán Behavioral Metrics cuối cùng
    print("📈 Đang tính toán Math Independence Index...")
    df = pd.read_csv(judged_csv)
    df["math_independence_index"] = df["Dialogue"].apply(compute_math_independence)
    
    # Lưu file cuối cùng
    df.to_csv(judged_csv, index=False)
    print(f"✨ HOÀN THÀNH! Tập dữ liệu Gold V2 đã sẵn sàng tại: {judged_csv}")

if __name__ == "__main__":
    import os
    asyncio.run(build_gold_v2())
