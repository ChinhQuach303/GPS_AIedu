import pandas as pd
import re

def standardize_dialogue(text):
    if not isinstance(text, str):
        return text
    
    # 1. Standardize Speaker Labels
    text = re.sub(r'Thầy giáo:|Thầy Giáo:|Giáo viên:', 'Thầy:', text)
    text = re.sub(r'Học sinh:|Học Sinh:', 'Em:', text)
    
    # 2. Fix the "Thank you" logic error in Non-GPS Yếu
    # Pattern: Em: Thầy giải thích rõ hơn về cách tính nhé.\n\nThầy: Đã hiểu rồi, cảm ơn em!
    # We replace it with a more helpful Non-GPS direct response.
    error_pattern = r'Em: Thầy giải thích rõ hơn về cách tính nhé\.\s+Thầy: Đã hiểu rồi, cảm ơn em!'
    replacement = 'Em: Thầy giải thích rõ hơn về cách tính nhé.\nThầy: Để tính xác suất này, ta dùng công thức P(A) = n(A)/n(Omega). Trong đó n(A) là số kết quả thuận lợi và n(Omega) là tổng số kết quả có thể xảy ra. Em chỉ cần đếm đúng số trường hợp là sẽ ra kết quả.'
    text = re.sub(error_pattern, replacement, text, flags=re.IGNORECASE)
    
    # 3. Standardize LaTeX
    # Convert $...$ to \( ... \)
    text = re.sub(r'\$(.*?)\$', r'\( \1 \)', text)
    # Convert $$...$$ to \[ ... \]
    text = re.sub(r'\$\$(.*?)\$\$', r'\[ \1 \]', text)
    
    # 4. Cleanup
    text = text.replace('\n\n\n', '\n\n')
    text = text.strip()
    
    return text

def main():
    input_file = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/augmented_conversations_final.csv'
    output_file = '/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/augmented_conversations_standardized.csv'
    
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    print("Standardizing dialogues...")
    df['Dialogue'] = df['Dialogue'].apply(standardize_dialogue)
    
    # Also standardize student IDs if needed (GPS_S_01 vs S_01)
    # The user mentioned Group and Student_ID columns.
    # Let's ensure IDs are consistent within groups.
    
    print(f"Saving to {output_file}...")
    df.to_csv(output_file, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
