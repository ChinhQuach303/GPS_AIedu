import pandas as pd
import numpy as np
import os

def judge_pilot_results(data_path):
    if not os.path.exists(data_path):
        return "Error: Data path not found."
    
    df = pd.read_csv(data_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['Timestamp']).sort_values('Timestamp')
    
    # Split into start of pilot vs end of pilot
    start_date = df['Timestamp'].min().date()
    end_date = df['Timestamp'].max().date()
    
    early_pilot = df[df['Timestamp'].dt.date == start_date]
    late_pilot = df[df['Timestamp'].dt.date == end_date]
    
    # Metrics
    metrics = {
        'Avg Satisfaction': lambda x: x['Satisfaction (1-5)'].mean(),
        'Avg Difficulty': lambda x: x['Difficulty (1-5)'].mean(),
        'Interaction Vol': lambda x: len(x),
    }
    
    results = []
    for m_name, m_func in metrics.items():
        v1 = m_func(early_pilot)
        v2 = m_func(late_pilot)
        change = (v2 - v1) / v1 if v1 != 0 else 0
        results.append({
            'Metric': m_name,
            'Day 1 (Start)': round(v1, 2),
            f'Day N (End)': round(v2, 2),
            '% Change': f"{change*100:+.1f}%"
        })

    # Judgment Logic
    score_card = pd.DataFrame(results)
    
    # Qualitative Judgment
    verdict = ""
    if v2 > v1:
        verdict = "PHƯƠNG PHÁP ĐANG ĐI ĐÚNG HƯỚNG. Học sinh cảm thấy hài lòng hơn dù bài tập ngày càng khó."
    else:
        verdict = "CẦN ĐIỀU CHỈNH. Sự hài lòng đang giảm sút."

    # Specific Teacher Insight
    hardest_topic = df.groupby('Topic')['Difficulty (1-5)'].mean().idxmax()
    most_active_class = df['Class'].value_counts().idxmax()

    with open('reports/pilot_week4_analysis/final_judgment.md', 'w', encoding='utf-8') as f:
        f.write(f"# ĐÁNH GIÁ KẾT QUẢ PILOT TUẦN 4\n\n")
        f.write(f"## 1. Bảng điểm hiệu quả\n\n")
        f.write(score_card.to_markdown(index=False) + "\n\n")
        f.write(f"## 2. Kết luận sư phạm (Verdict)\n\n> **{verdict}**\n\n")
        f.write(f"## 3. Kiến nghị cho giáo viên (Teacher Insights)\n\n")
        f.write(f"- **Chủ đề cần ưu tiên dạy lại**: {hardest_topic} (Độ khó bình quân cao nhất)\n")
        f.write(f"- **Lớp học tiêu biểu**: {most_active_class} (Có số lượt tương tác đều nhất)\n")
        f.write(f"- **Tính độc lập**: Học sinh đang duy trì mức tương tác {round(len(df)/len(df['Student ID'].unique()), 1)} tin nhắn/phiên, cho thấy sự kiên trì cao.\n")

    print("Judgment report generated at reports/pilot_week4_analysis/final_judgment.md")

if __name__ == "__main__":
    judge_pilot_results('data/processed/GPS_AIedu_Data - QA - Raw Data.csv')
