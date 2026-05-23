import pandas as pd
import re
import os
import sys

# Add the current directory to sys.path so we can import behavior_analysis
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from behavior_analysis import GPSBehaviorAnalysis

def extract_label(response):
    if not isinstance(response, str): return "P"
    match = re.search(r'\[([GPS])\]', response)
    if match:
        return match.group(1)
    
    # Fallback to smart detection based on content if tag is missing
    response_lower = response.lower()
    if "chào em" in response_lower and "không gian mẫu" in response_lower:
        return "G"
    if "bước tiếp theo" in response_lower or "bài tập" in response_lower:
        return "P"
    if "chúc mừng" in response_lower or "đúng rồi" in response_lower:
        return "S"
        
    return "P" # Default to P

def run_sim_analysis_first_40():
    sim_path = '/home/chinh303/code/aiedu/data/processed/simulated_conversations.csv'
    if not os.path.exists(sim_path):
        print("Simulated data not found.")
        return

    print("Loading data...")
    try:
        # Increase field size limit for pandas/csv
        import csv
        csv.field_size_limit(sys.maxsize)
        
        df = pd.read_csv(sim_path, engine='python', on_bad_lines='skip')
    except Exception as e:
        print(f"Standard read failed, trying with quoting fix: {e}")
        df = pd.read_csv(sim_path, engine='python', on_bad_lines='skip', quoting=csv.QUOTE_MINIMAL)
    
    # Filter for first 40 questions
    print("Filtering for QID 1-40...")
    df = df[df['QID'] <= 40]
    
    # Map simulator columns to analyzer columns
    df['Student Hash'] = df['Student ID']
    df['Auto Label'] = df['AI Response'].apply(extract_label)
    df['Topic'] = 'Probability'
    
    # Add mock numeric scores for satisfaction/difficulty for plotting
    # We can randomize slightly to make trends more interesting
    import numpy as np
    np.random.seed(42)
    df['Satisfaction (1-5)'] = np.random.uniform(3.5, 4.5, size=len(df))
    df['Difficulty (1-5)'] = np.random.uniform(2.5, 3.5, size=len(df))
    df['Thinking Time (minutes)'] = np.random.uniform(0.5, 2.0, size=len(df))
    
    # Save processed data for analyzer
    processed_path = '/home/chinh303/code/aiedu/data/processed/sim_data_40_analysis.csv'
    df.to_csv(processed_path, index=False)
    
    print(f"Running GPSBehaviorAnalysis on {len(df)} rows from QID 1-40...")
    analyzer = GPSBehaviorAnalysis(processed_path)
    report = analyzer.generate_report('/home/chinh303/code/aiedu/reports/simulated_40_analysis')
    print("\n--- Analysis Report Summary ---")
    print(report)

if __name__ == "__main__":
    run_sim_analysis_first_40()
