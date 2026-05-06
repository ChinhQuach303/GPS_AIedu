
import pandas as pd
import re
import os

# Paths
SIM_PATH = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/simulated_conversations.csv'
AUG_PATH = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/augmented_conversations_final.csv'
OUTPUT_PATH = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/merged_conversations_research.csv'

PROFILE_TO_LEVEL = {
    'HS0001': 'Giỏi',
    'HS0002': 'Khá',
    'HS0003': 'Yếu',
    'HS0004': 'Trung bình',
    'HS0005': 'Trung bình'
}

def qid_to_week(qid):
    try:
        q = int(qid)
        if q <= 6:   return 1
        if q <= 12:  return 2
        if q <= 18:  return 3
        if q <= 24:  return 4
        if q <= 30:  return 5
        return 6
    except:
        return 1

def merge_datasets():
    print("Loading datasets...")
    
    # 1. Process Turn-based Simulated Data
    df_sim = pd.read_csv(SIM_PATH)
    df_sim['Level'] = df_sim['Profile'].map(PROFILE_TO_LEVEL).fillna('Trung bình')
    df_sim['Group'] = 'GPS'
    df_sim['Week'] = df_sim['QID'].apply(qid_to_week)

    def build_dialogue(grp):
        turns = []
        for _, row in grp.sort_values('Turn').iterrows():
            turns.append(f"Em: {row['Question']}")
            turns.append(f"Thầy: {row['AI Response']}")
        return "\n".join(turns)

    print("Grouping simulated turns into sessions...")
    sim_sessions = (
        df_sim.groupby(['Student ID', 'QID', 'Level', 'Group', 'Week'])
        .apply(build_dialogue, include_groups=False)
        .reset_index()
    )
    sim_sessions.columns = ['Student_ID', 'QID', 'Level', 'Group', 'Week', 'Dialogue']

    # 2. Process Session-based Augmented Data
    df_aug = pd.read_csv(AUG_PATH)
    if 'Week' not in df_aug.columns:
        df_aug['Week'] = df_aug['QID'].apply(qid_to_week)
    
    # Standardize columns
    df_aug = df_aug[['Group', 'Student_ID', 'Level', 'QID', 'Week', 'Dialogue']]

    # 3. Merge
    print("Merging datasets...")
    merged_df = pd.concat([sim_sessions, df_aug], ignore_index=True)
    
    # 4. Apply Initial Cleaning (Spec 1)
    print("Applying Spec 1: Cleaning & Standardization...")
    CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]')
    
    initial_count = len(merged_df)
    # Remove rows with Chinese
    merged_df = merged_df[~merged_df['Dialogue'].str.contains(CHINESE_PATTERN, na=False)]
    print(f"  Removed {initial_count - len(merged_df)} sessions with Chinese characters.")

    def standardize_latex(text):
        if not isinstance(text, str): return text
        # Convert $...$ to \( ... \)
        text = re.sub(r'(?<!\\)\$([^$]+)\$', r'\( \1 \)', text)
        # Convert $$...$$ to \[ ... \]
        text = re.sub(r'(?<!\\)\$\$([^$]+)\$\$', r'\[ \1 \]', text)
        return text

    merged_df['Dialogue'] = merged_df['Dialogue'].apply(standardize_latex)
    
    # 5. Save
    merged_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Successfully merged {len(merged_df)} sessions to {OUTPUT_PATH}")

if __name__ == "__main__":
    merge_datasets()
