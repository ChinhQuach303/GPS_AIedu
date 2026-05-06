
import pandas as pd
import re
import os

INPUT_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/gps_aiedu_final_research_dataset.csv'
OUTPUT_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/gps_aiedu_gold_standard.csv'
LOG_FILE = '/home/chinh303/code/gpsaiedu/GPS_AIedu/logs/integrity_report.txt'

# 1. Patterns
CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]')
# Catch generic AI filler that doesn't fit the teacher persona
ROBOTIC_PATTERNS = [
    r"Tôi là một mô hình ngôn ngữ",
    r"Xin lỗi, tôi không thể",
    r"Cảm ơn bạn đã hỏi",
    r"Rất vui được giúp đỡ"
]

def validate_integrity(text):
    if not isinstance(text, str): return False, "Empty content"
    
    # Check for Chinese
    if CHINESE_PATTERN.search(text):
        return False, "Chinese characters detected"
    
    # Check for robotic filler
    for p in ROBOTIC_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return False, "Robotic filler detected"
            
    # Logic Check: "Em đã hiểu" too early
    # If "Em đã hiểu" or "Cảm ơn thầy" appears in the first 2 turns
    turns = text.split('\n')
    if len(turns) < 4: # Minimum turn: Em hỏi -> Thầy G -> Em P -> Thầy P...
        return False, "Session too short"
    
    early_content = "\n".join(turns[:3]).lower()
    if "em đã hiểu" in early_content or "cảm ơn thầy" in early_content:
        return False, "Premature understanding (Logic error)"
        
    return True, "OK"

def standardize_latex_advanced(text):
    # 1. Convert display math $$...$$ to \[ ... \]
    text = re.sub(r'\$\$(.*?)\$\$', r'\[ \1 \]', text, flags=re.DOTALL)
    # 2. Convert inline math $...$ to \( ... \)
    # Be careful not to match existing \( or already converted ones
    text = re.sub(r'(?<!\\)\$([^$]+)\$', r'\( \1 \)', text)
    
    # 3. Cleanup spacing around LaTeX
    text = text.replace('  ', ' ')
    return text

def main():
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))

    print(f"Starting Gold Standard Validation on {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    
    initial_count = len(df)
    results = df['Dialogue'].apply(validate_integrity)
    
    df['Is_Valid'] = [r[0] for r in results]
    df['Reason'] = [r[1] for r in results]
    
    # Apply LaTeX standardization to valid ones
    df.loc[df['Is_Valid'], 'Dialogue'] = df.loc[df['Is_Valid'], 'Dialogue'].apply(standardize_latex_advanced)
    
    # Filter
    gold_df = df[df['Is_Valid']].drop(columns=['Is_Valid', 'Reason'])
    rejected_df = df[~df['Is_Valid']]
    
    # Logging
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"INTEGRITY VALIDATION REPORT\n")
        f.write(f"Total sessions processed: {initial_count}\n")
        f.write(f"Gold Standard sessions: {len(gold_df)}\n")
        f.write(f"Rejected sessions: {len(rejected_df)}\n\n")
        f.write("REJECTION BREAKDOWN:\n")
        f.write(rejected_df['Reason'].value_counts().to_string())
        
    gold_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Validation complete. Gold dataset saved to {OUTPUT_FILE}")
    print(f"Rejection breakdown: \n{rejected_df['Reason'].value_counts()}")

if __name__ == "__main__":
    main()
