import pandas as pd
import os

# 1. Load data
file_path = "/home/chinh303/code/gpsaiedu/GPS_AIedu/data/processed/simulated_conversations.csv"
df = pd.read_csv(file_path)

# 2. Cleaning
df = df.dropna(subset=['Student ID', 'QID', 'Turn'])

# 3. Phân tích Macro: Số lượt hoàn thành trung bình
pivot_turns = df.groupby(['Profile', 'QID'])['Turn'].max().unstack()

# 4. Phân tích Micro: Tỷ lệ phân bổ GPS
def count_gps(text):
    text = str(text)
    if "[G]" in text: return "Guide"
    if "[P]" in text: return "Practice"
    if "[S]" in text: return "Solve"
    return "Other"

df['GPS_Stage'] = df['AI Response'].apply(count_gps)
gps_dist = df.groupby(['Profile', 'GPS_Stage']).size().unstack(fill_value=0)

# 5. Xuất báo cáo
print("\n=== BÁO CÁO PHÂN TÍCH SƠ BỘ ===")
print("\n1. Số lượt (Turns) để hoàn thành bài toán (Càng ít càng nhanh):")
print(pivot_turns)

print("\n2. Phân bổ các bước sư phạm (GPS Count):")
print(gps_dist)
