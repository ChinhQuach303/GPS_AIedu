import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def evaluate_metrics(file_path):
    df = pd.read_csv(file_path)
    
    print(f"--- FINAL EVALUATION: HYPER-REALISTIC DATASET (N=60) ---")
    print(f"Total records: {len(df)}")
    
    # 1. Independence Index (II)
    student_stats = df.groupby('Student ID')['GPS Step (Truth)'].value_counts().unstack(fill_value=0)
    for col in ['G', 'P', 'S']:
        if col not in student_stats.columns: student_stats[col] = 0
            
    student_stats['II'] = student_stats['S'] / (student_stats['G'] + student_stats['P'] + 0.1)
    median_ii = student_stats['II'].median()
    
    # 2. Pearson Correlation (Diff vs Time) - Proof of Cognitive Effort
    corr, _ = pearsonr(df['Difficulty (1-5)'], df['Thinking Time (minutes)'])
    
    # 3. Learning Curve Proof (Thinking time vs Progress Factor)
    learning_corr, _ = pearsonr(df['Progress Factor'], df['Thinking Time (minutes)'])
    
    # 4. Markov Transition (P -> S)
    transitions = []
    for (sid, q), group in df.groupby(['Student ID', 'Question']):
        steps = group['GPS Step (Truth)'].tolist()
        for i in range(len(steps)-1):
            if steps[i] == 'P' and steps[i+1] == 'S': transitions.append(1)
            elif steps[i] == 'P': transitions.append(0)
    p_to_s_rate = np.mean(transitions) if transitions else 0
    
    # RESULTS
    print(f"\n1. Median Independence Index (II): {median_ii:.2f} (Target: 0.86)")
    print(f"2. Cognitive Effort Correlation (Diff vs Time): {corr:.2f} (Target: 0.68)")
    print(f"3. Learning Effect (Progress vs Time): {learning_corr:.2f} (Negative is good: More progress = Less time)")
    print(f"4. Markov Transition (P -> S): {p_to_s_rate:.2f} (Target: 0.65)")
    
    # Breakdown by Profile
    print(f"\n--- Median II by Profile ---")
    student_profiles = df[['Student ID', 'Profile']].drop_duplicates().set_index('Student ID')
    profile_ii = student_stats.join(student_profiles).groupby('Profile')['II'].median()
    vn_to_en = {"giỏi": "Excellent", "khá": "Good", "trung bình": "Average", "yêu": "Weak"}
    profile_ii.index = [vn_to_en.get(idx, idx) for idx in profile_ii.index]
    print(profile_ii)

if __name__ == "__main__":
    evaluate_metrics("c:/Users/quach/code/GPS_AIedu/data/processed/GPS_AIedu_Expanded_60.csv")
