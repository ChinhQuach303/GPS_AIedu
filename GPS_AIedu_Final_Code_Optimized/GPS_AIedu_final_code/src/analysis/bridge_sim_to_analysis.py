import pandas as pd
import re
from behavior_analysis import GPSBehaviorAnalysis

def extract_label(response):
    if not isinstance(response, str): return "P"
    match = re.search(r'\[([GPS])\]', response)
    return match.group(1) if match else "P" # Fallback to P if not found

def run_sim_analysis():
    sim_path = 'data/processed/simulated_conversations.csv'
    if not os.path.exists(sim_path):
        print("Simulated data not found.")
        return

    df = pd.read_csv(sim_path)
    
    # Map simulator columns to analyzer columns
    df['Student Hash'] = df['Student ID']
    df['Auto Label'] = df['AI Response'].apply(extract_label)
    df['Topic'] = 'Probability' # Default topic since we are doing probability questions
    
    # Add mock numeric scores for satisfaction/difficulty for plotting
    df['Satisfaction (1-5)'] = 4.0
    df['Difficulty (1-5)'] = 3.0
    df['Thinking Time (minutes)'] = 1.0 # Mock value
    
    # Save processed data for analyzer
    processed_path = 'data/processed/sim_data_for_analysis.csv'
    df.to_csv(processed_path, index=False)
    
    print(f"Running GPSBehaviorAnalysis on {len(df)} rows of simulated data...")
    analyzer = GPSBehaviorAnalysis(processed_path)
    report = analyzer.generate_report('reports/simulated_data_analysis')
    print("Analysis Report Summary:")
    print(report)

if __name__ == "__main__":
    import os
    run_sim_analysis()
