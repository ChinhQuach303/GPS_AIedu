import pandas as pd
import numpy as np
import re

def normalize_real_data(df):
    # Mapping Profile to Level based on bao_cao_tuan_1.md
    mapping = {
        'HS0001': 'Giỏi',
        'HS0002': 'Khá',
        'HS0003': 'Yếu',
        'HS0004': 'Trung bình',
        'HS0005': 'Trung bình'
    }
    df['Level'] = df['Profile'].map(mapping).fillna('Trung bình')
    
    # Aggregate turns into sessions
    def aggregate_dialogue(group):
        dialogue = []
        for _, row in group.iterrows():
            dialogue.append(f"Em: {row['Question']}")
            dialogue.append(f"Thầy: {row['AI Response']}")
        return "\n".join(dialogue)
    
    sessions = df.groupby(['Student ID', 'QID', 'Level']).apply(aggregate_dialogue).reset_index()
    sessions.columns = ['Student_ID', 'QID', 'Level', 'Dialogue']
    sessions['Group'] = 'GPS' # Original data was GPS focused
    return sessions

def get_metrics(df):
    metrics = {}
    metrics['Total_Sessions'] = len(df)
    metrics['Avg_Length'] = df['Dialogue'].str.len().mean()
    metrics['Avg_Turns'] = df['Dialogue'].apply(lambda x: str(x).count('Thầy:') + str(x).count('Em:')).mean()
    metrics['Math_Density'] = df['Dialogue'].apply(lambda x: len(re.findall(r'\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\]', str(x)))).mean()
    
    # Distribution of levels
    level_dist = df['Level'].value_counts(normalize=True).to_dict()
    metrics['Level_Distribution'] = level_dist
    
    return metrics

def compare():
    real_path = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/simulated_conversations.csv'
    aug_path = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/augmented_conversations_final.csv'
    
    df_real_raw = pd.read_csv(real_path)
    df_aug = pd.read_csv(aug_path)
    
    # Normalize real data
    df_real = normalize_real_data(df_real_raw)
    
    # For fair comparison, filter augmented data to GPS group only (if real is all GPS)
    df_aug_gps = df_aug[df_aug['Group'] == 'GPS']
    
    real_metrics = get_metrics(df_real)
    aug_metrics = get_metrics(df_aug_gps)
    
    print("=== DATA COMPARISON: REAL VS AUGMENTED (GPS Group) ===")
    print(f"\n{'Metric':<25} | {'Real':<15} | {'Augmented':<15} | {'Diff (%)'}")
    print("-" * 75)
    
    for key in ['Total_Sessions', 'Avg_Length', 'Avg_Turns', 'Math_Density']:
        r = real_metrics[key]
        a = aug_metrics[key]
        diff = ((a - r) / r * 100) if r != 0 else 0
        print(f"{key:<25} | {r:<15.2f} | {a:<15.2f} | {diff:>+7.2f}%")
        
    print("\n--- Level Distribution ---")
    all_levels = set(real_metrics['Level_Distribution'].keys()) | set(aug_metrics['Level_Distribution'].keys())
    for lvl in sorted(all_levels):
        r = real_metrics['Level_Distribution'].get(lvl, 0) * 100
        a = aug_metrics['Level_Distribution'].get(lvl, 0) * 100
        print(f"{lvl:<25} | {r:>6.1f}% | {a:>6.1f}%")

if __name__ == "__main__":
    compare()
