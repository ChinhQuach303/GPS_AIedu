import pandas as pd
import numpy as np

def evaluate_data():
    conv_file = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/augmented_conversations_standardized.csv'
    score_file = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/mock_final_scores.csv'
    
    df_conv = pd.read_csv(conv_file)
    df_scores = pd.read_csv(score_file)
    
    # 1. Behavioral Analysis (from conversations)
    df_conv['Length'] = df_conv['Dialogue'].str.len()
    df_conv['Turns'] = df_conv['Dialogue'].apply(lambda x: str(x).count('Thầy:') + str(x).count('Em:'))
    df_conv['Math_Density'] = df_conv['Dialogue'].apply(lambda x: str(x).count('\(') + str(x).count('\[') + str(x).count('$'))
    
    conv_metrics = df_conv.groupby('Group').agg({
        'Length': 'mean',
        'Turns': 'mean',
        'Math_Density': 'mean'
    }).round(2)
    
    # 2. Learning Gain Analysis (from scores)
    # Map 'Experimental' -> 'GPS', 'Control' -> 'Non-GPS'
    df_scores['Group'] = df_scores['Group'].replace({'Experimental': 'GPS', 'Control': 'Non-GPS'})
    df_scores['Gain'] = df_scores['Post_Score'] - df_scores['Pre_Score']
    # Hake's Gain g = (post - pre) / (max - pre). Assume max is 100.
    df_scores['Hake_Gain'] = (df_scores['Post_Score'] - df_scores['Pre_Score']) / (100 - df_scores['Pre_Score'])
    
    score_metrics = df_scores.groupby('Group').agg({
        'Pre_Score': 'mean',
        'Post_Score': 'mean',
        'Gain': 'mean',
        'Hake_Gain': 'mean'
    }).round(2)
    
    # 3. Combine and Report
    print("=== PEDAGOGICAL EVALUATION REPORT ===")
    print("\n--- CONVERSATIONAL METRICS ---")
    print(conv_metrics)
    
    print("\n--- LEARNING OUTCOME METRICS ---")
    print(score_metrics)
    
    # 4. Effect Size (Cohen's d) for Learning Gain
    gps_gain = df_scores[df_scores['Group']=='GPS']['Gain']
    nongps_gain = df_scores[df_scores['Group']=='Non-GPS']['Gain']
    
    d = (np.mean(gps_gain) - np.mean(nongps_gain)) / np.sqrt((np.std(gps_gain)**2 + np.std(nongps_gain)**2) / 2)
    print(f"\n--- IMPACT ANALYSIS ---")
    print(f"Cohen's d (Effect Size): {d:.2f}")
    if d > 0.8:
        print("Interpretation: High Impact (Very Large)")
    elif d > 0.5:
        print("Interpretation: Medium Impact")
    else:
        print("Interpretation: Low Impact")

if __name__ == "__main__":
    evaluate_data()
