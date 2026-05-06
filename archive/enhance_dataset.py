
import pandas as pd
import re
import numpy as np

# Path
INPUT_PATH = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/merged_conversations_research.csv'
OUTPUT_PATH = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/gps_aiedu_final_research_dataset.csv'

def compute_metrics(text):
    if not isinstance(text, str): return 0, 0, 0, 0
    
    turns_g = len(re.findall(r'\[G\]', text))
    turns_p = len(re.findall(r'\[P\]', text))
    turns_s = len(re.findall(r'\[S\]', text))
    
    # Math Density (LaTeX expressions)
    math_density = len(re.findall(r'\\\(.*?\\\)|\\\[.*?\\\]|\$[^$]+\$', text))
    
    # Independence Index
    independence_idx = turns_s / (turns_g + turns_p + 1)
    
    return turns_g, turns_p, turns_s, math_density, independence_idx

def get_difficulty(qid):
    # Mapping QIDs to difficulty based on topic complexity
    try:
        q = int(qid)
        if q in [1, 2, 5, 22, 31, 44]: return 'Easy'
        if q in [3, 4, 6, 12, 18, 20, 24, 25, 29, 30, 33, 40]: return 'Medium'
        return 'Hard' # Probability/Combinatorics is generally hard
    except:
        return 'Medium'

def enhance_data():
    print(f"Reading {INPUT_PATH}...")
    df = pd.read_csv(INPUT_PATH)
    
    print("Applying Spec 2 & 3: Calculating Pedagogical Metrics...")
    metrics_data = df['Dialogue'].apply(compute_metrics)
    df[['Turns_G', 'Turns_P', 'Turns_S', 'Math_Density', 'Independence_Index']] = pd.DataFrame(metrics_data.tolist(), index=df.index)
    
    print("Applying Spec 4: Mapping Difficulty Levels...")
    df['Difficulty'] = df['QID'].apply(get_difficulty)
    
    print("Applying Spec 5: Estimating Learning Outcome (Proxy)...")
    # This is a proxy for the 'Post-score' based on independence and math density
    # Logic: High independence + High math density = High understanding
    def estimate_outcome(row):
        base_score = {'Giỏi': 85, 'Khá': 70, 'Trung bình': 55, 'Yêu': 40}.get(row['Level'], 50)
        # Bonus for independence
        bonus = row['Independence_Index'] * 15
        # Penalty for too many Guide turns (excessive dependency)
        penalty = row['Turns_G'] * 2
        return min(100, max(0, base_score + bonus - penalty))
    
    df['Estimated_Post_Score'] = df.apply(estimate_outcome, axis=1)
    
    # Fidelity Check
    df['GPS_Fidelity'] = df.apply(lambda r: 1.0 if r['Turns_G'] > 0 and r['Turns_P'] > 0 and r['Turns_S'] > 0 else (0.5 if r['Turns_S'] > 0 else 0.1), axis=1)

    print(f"Saving final dataset to {OUTPUT_PATH}...")
    df.to_csv(OUTPUT_PATH, index=False)
    print("Done! Dataset is ready for EMNLP submission analysis.")

if __name__ == "__main__":
    enhance_data()
