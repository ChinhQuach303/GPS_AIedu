import pandas as pd
import re
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from behavior_analysis import GPSBehaviorAnalysis

INPUT_FILE = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/augmented_conversations_final.csv"
PROCESSED_FILE = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/expanded_conversations_for_analysis.csv"
REPORT_DIR = "/home/chinh303/code/gpsaiedu/GPS_AIedu/reports/final_analysis"

def extract_turns(dialogue):
    if not isinstance(dialogue, str): return []
    # Split by "Thầy:"
    turns = re.split(r'Thầy:', dialogue)
    teacher_responses = []
    for turn in turns:
        turn = turn.strip()
        if not turn: continue
        # Only keep the part before "Em:" (which is the teacher's speech)
        teacher_speech = turn.split('Em:')[0].strip()
        if teacher_speech:
            teacher_responses.append(teacher_speech)
    return teacher_responses

def extract_label(response):
    match = re.search(r'\[([GPS])\]', response)
    if match:
        return match.group(1)
    
    # Fallback smart detection
    response_lower = response.lower()
    if "chào em" in response_lower or "không gian mẫu" in response_lower:
        return "G"
    if "bước tiếp theo" in response_lower or "tính toán" in response_lower or "công thức" in response_lower:
        return "P"
    if "chúc mừng" in response_lower or "đúng rồi" in response_lower or "kết quả là" in response_lower:
        return "S"
    return "P"

def prepare_data():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return False

    print(f"Loading {INPUT_FILE}...")
    # Use brute force read if pandas fails
    try:
        df = pd.read_csv(INPUT_FILE, on_bad_lines='skip', engine='python')
    except Exception as e:
        print(f"Pandas failed: {e}. Trying alternative...")
        # Manual parse if needed, but we'll try to stick to pandas first
        return False

    expanded_rows = []
    print("Expanding dialogues into individual turns...")
    
    for _, row in df.iterrows():
        dialogue = row['Dialogue']
        responses = extract_turns(dialogue)
        
        for i, resp in enumerate(responses):
            expanded_rows.append({
                'Student Hash': row['Student_ID'],
                'Group': row['Group'],
                'Level': row['Level'],
                'QID': row['QID'],
                'Response': resp,
                'Auto Label': extract_label(resp),
                'Timestamp': pd.Timestamp('2026-05-05 11:00') + pd.Timedelta(seconds=i*60), # Mock sequential timestamps
                'Topic': 'Probability'
            })
            
    expanded_df = pd.DataFrame(expanded_rows)
    
    # Add mock metrics for behavior analysis script
    import numpy as np
    np.random.seed(42)
    expanded_df['Satisfaction (1-5)'] = np.random.uniform(3.8, 4.8, size=len(expanded_df))
    expanded_df['Difficulty (1-5)'] = np.random.uniform(2.0, 3.5, size=len(expanded_df))
    
    expanded_df.to_csv(PROCESSED_FILE, index=False)
    print(f"Saved {len(expanded_df)} expanded turns to {PROCESSED_FILE}")
    return True

def run_analysis():
    if not prepare_data():
        return

    print("Running GPSBehaviorAnalysis...")
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
        
    analyzer = GPSBehaviorAnalysis(PROCESSED_FILE)
    
    # Generate behavior metrics
    # Note: behavior_analysis.py has generate_report method
    try:
        report = analyzer.generate_report(REPORT_DIR)
        print("\n--- Analysis Report Summary ---")
        print(report)
        
        # Calculate key metrics from Week 6 objectives
        # Math Density: Avg turns per session
        # Independence Index: Ratio of S/(G+P+S) or similar transition metrics
        
        df_clean = analyzer.df
        print("\n--- PROJECT PERFORMANCE METRICS ---")
        
        for group in df_clean['Group'].unique():
            group_df = df_clean[df_clean['Group'] == group]
            total_turns = len(group_df)
            total_students = group_df['Student Hash'].nunique()
            avg_turns = total_turns / total_students
            
            labels = group_df['Auto Label'].value_counts(normalize=True)
            independence_idx = labels.get('S', 0) # Simple proxy: ratio of S steps
            
            print(f"\nGroup: {group}")
            print(f"  Math Density (Avg Turns): {avg_turns:.2f}")
            print(f"  Independence Index: {independence_idx:.3f}")
            print(f"  G steps: {labels.get('G', 0):.1%}")
            print(f"  P steps: {labels.get('P', 0):.1%}")
            print(f"  S steps: {labels.get('S', 0):.1%}")
            
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_analysis()
