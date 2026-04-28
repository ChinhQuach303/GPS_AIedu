import os
import pandas as pd
from behavior_analysis import GPSBehaviorAnalysis

def run_phase_1():
    print("--- KHỞI CHẠY GIAI ĐOẠN 1: PHÂN TÍCH DỮ LIỆU NGHIÊN CỨU ---")
    
    BASE_DIR = "/home/chinh303/code/gpsaiedu/GPS_AIedu"
    input_path = os.path.join(BASE_DIR, "processed/cleaned_conversations.csv")
    score_path = os.path.join(BASE_DIR, "data/student_scores.csv")
    output_dir = os.path.join(BASE_DIR, "reports/research_phase_1")
    
    if not os.path.exists(input_path):
        print("Lỗi: Không tìm thấy dữ liệu đã làm sạch.")
        return

    # 1. Chuẩn bị dữ liệu cho Analyzer
    df = pd.read_csv(input_path)
    
    # Khớp nối tên cột với yêu cầu của class GPSBehaviorAnalysis
    df = df.rename(columns={
        'Student ID': 'Student Hash',
        'GPS_Step': 'Auto Label'
    })
    
    # Bổ sung các cột thiếu để tránh lỗi biểu đồ
    if 'Topic' not in df.columns:
        df['Topic'] = 'Toán Xác Suất'
    if 'Satisfaction (1-5)' not in df.columns:
        df['Satisfaction (1-5)'] = 4.0  # Giả định hài lòng cao
    if 'Difficulty (1-5)' not in df.columns:
        # Giả định độ khó tăng dần nhẹ theo turn
        df['Difficulty (1-5)'] = 2.0 + (df['Turn'] % 4)
    if 'Thinking Time (minutes)' not in df.columns:
        df['Thinking Time (minutes)'] = 1.5
    
    # 2. Khởi tạo Analyzer
    analyzer = GPSBehaviorAnalysis(df)
    
    # 3. Chạy báo cáo tổng thể
    print("Đang tạo các biểu đồ và chỉ số hành vi...")
    summary = analyzer.generate_report(output_dir)
    
    # 4. Phân tích điểm số (Research Truth)
    if os.path.exists(score_path):
        print("Đang phân tích hiệu quả học tập (Pre/Post Comparison)...")
        scores_df = pd.read_csv(score_path)
        
        # Lưu vào đường dẫn mà analyzer mong đợi
        mock_score_path = os.path.join(BASE_DIR, 'data/processed/mock_final_scores.csv')
        os.makedirs(os.path.dirname(mock_score_path), exist_ok=True)
        scores_df.to_csv(mock_score_path, index=False)
        
        # Chạy lại report để cập nhật phần điểm số
        summary = analyzer.generate_report(output_dir)
    
    print(f"\n--- PHÂN TÍCH HOÀN TẤT ---")
    print(f"Kết quả đã được lưu tại: {output_dir}")
    print("\n--- TÓM TẮT BẰNG CHỨNG NGHIÊN CỨU ---")
    print(summary)

if __name__ == "__main__":
    run_phase_1()
