import pandas as pd
import re

file_path = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/simulated_conversations.csv"
df = pd.read_csv(file_path)

def fix_hallucination(text):
    if not isinstance(text, str): return text
    # Xóa các từ hallucinate phổ biến
    junk_words = ["ngubàngu", "sapphire", "apple", "ngubàngubàngupiap", "ELEEE", "EEEEL"]
    for word in junk_words:
        text = text.replace(word, "...")
    # Loại bỏ các ký tự Trung Quốc còn sót
    text = re.sub(r'[\u4e00-\u9fff]+', '', text)
    return text.strip()

# Áp dụng làm sạch
df['Question'] = df['Question'].apply(fix_hallucination)
df['AI Response'] = df['AI Response'].apply(fix_hallucination)

# Xóa các dòng bị loạn vai diễn nặng (Học sinh tự xưng Thầy và giải bài)
# Dấu hiệu: HS0004 nhưng nói "Chào Em" và đưa ra lời giải C_13^4
def is_confused_role(row):
    q = str(row['Question'])
    if "Chào Em!" in q and "HS00" in str(row['Profile']):
        return True
    return False

df = df[~df.apply(is_confused_role, axis=1)]

# Lưu lại file sạch
df.to_csv(file_path, index=False)
print(f"✅ Đã làm sạch dữ liệu. Số dòng còn lại: {len(df)}")
