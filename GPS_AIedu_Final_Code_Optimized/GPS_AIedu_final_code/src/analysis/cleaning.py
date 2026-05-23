import pandas as pd
import re
import os
from datetime import datetime

def extract_gps_label(text):
    """
    Trích xuất nhãn [G], [P], hoặc [S] từ văn bản phản hồi của AI.
    Sử dụng Regex và Keyword Matching.
    """
    if not isinstance(text, str):
        return None
    
    # 1. Ưu tiên tìm nhãn trong ngoặc vuông [G], [P], [S]
    match = re.search(r'\[\s*([GPS])\s*\]', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # 2. Tìm ký tự đứng đầu dòng (quy ước phổ biến)
    lines = text.split('\n')
    first_line = lines[0].strip() if lines else ""
    if first_line.startswith('G:'): return 'G'
    if first_line.startswith('P:'): return 'P'
    if first_line.startswith('S:'): return 'S'

    # 3. Keyword-based fallback (Heuristic)
    text_lower = text.lower()
    
    # Thứ tự ưu tiên: S > P > G
    # Nếu có khen ngợi hoặc xác nhận kết quả -> S
    if any(kw in text_lower for kw in ['đúng rồi', 'chính xác', 'kết quả là', 'hoàn toàn đúng', 'tốt lắm']):
        return 'S'
    
    # Nếu có yêu cầu tính toán hoặc gợi ý -> P
    if any(kw in text_lower for kw in ['thử tính', 'tính xem', 'hãy tính', 'gợi ý', 'bao nhiêu']):
        return 'P'
    
    # Nếu có giải thích khái niệm -> G
    if any(kw in text_lower for kw in ['hướng dẫn', 'khái niệm', 'định nghĩa', 'phương pháp']):
        return 'G'
    
    return None

def clean_and_evaluate(input_path, output_path):
    print(f"--- Bắt đầu làm sạch dữ liệu: {input_path} ---")
    
    if not os.path.exists(input_path):
        print(f"Lỗi: Không tìm thấy file tại {input_path}")
        return

    # 1. Đọc dữ liệu
    try:
        # Sử dụng engine='python' và on_bad_lines='skip' để xử lý file CSV có format không chuẩn
        df = pd.read_csv(input_path, engine='python', on_bad_lines='skip')
    except Exception as e:
        print(f"Lỗi khi đọc CSV: {e}")
        return

    # 2. Chuẩn hóa tên cột
    df.columns = [c.strip() for c in df.columns]
    
    # 3. Trích xuất nhãn GPS
    print("Đang trích xuất nhãn GPS từ AI Response...")
    df['GPS_Step'] = df['AI Response'].apply(extract_gps_label)
    
    # 4. Xử lý thời gian
    print("Đang chuẩn hóa định dạng thời gian...")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['Timestamp'])
    
    # 5. Sắp xếp dữ liệu theo học sinh và thời gian
    df = df.sort_values(by=['Student ID', 'Timestamp'])
    
    # 6. Đánh giá sơ bộ
    total_rows = len(df)
    gps_counts = df['GPS_Step'].value_counts()
    unique_students = df['Student ID'].nunique()
    unique_questions = df['QID'].nunique()
    
    print("\n--- KẾT QUẢ ĐÁNH GIÁ SƠ BỘ ---")
    print(f"1. Tổng số bản ghi: {total_rows}")
    print(f"2. Số học sinh duy nhất: {unique_students}")
    print(f"3. Số câu hỏi (QID) duy nhất: {unique_questions}")
    print(f"4. Phân bổ các bước GPS:")
    for step, count in gps_counts.items():
        percentage = (count / total_rows) * 100
        print(f"   - [{step}]: {count} ({percentage:.2f}%)")
    
    # 7. Kiểm tra dữ liệu lỗi (không có nhãn)
    none_labels = df[df['GPS_Step'].isna()]
    if len(none_labels) > 0:
        print(f"⚠️ Cảnh báo: Có {len(none_labels)} dòng không trích xuất được nhãn GPS.")
        
    # 8. Lưu dữ liệu đã làm sạch
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n--- Đã lưu dữ liệu sạch tại: {output_path} ---")
    
    return df

if __name__ == "__main__":
    # Sử dụng đường dẫn tuyệt đối để đảm bảo an toàn
    BASE_DIR = "/home/chinh303/code/gpsaiedu/GPS_AIedu"
    INPUT_FILE = os.path.join(BASE_DIR, "simulated_conversations.csv")
    OUTPUT_FILE = os.path.join(BASE_DIR, "processed/cleaned_conversations.csv")
    
    clean_and_evaluate(INPUT_FILE, OUTPUT_FILE)
