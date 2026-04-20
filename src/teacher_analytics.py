import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

class TeacherAnalytics:
    def __init__(self, db_path="webchat/gps_aiedu.sqlite"):
        self.db_path = db_path
        
    def get_raw_data(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM messages", conn)
        ratings = pd.read_sql_query("SELECT * FROM ratings", conn)
        students = pd.read_sql_query("SELECT * FROM students", conn)
        conn.close()
        
        # Merge data
        df = df.merge(students, left_on="student_id", right_on="id", how="left")
        if not ratings.empty:
            df = df.merge(ratings, on="message_id", how="left")
        return df

    def generate_report(self):
        df = self.get_raw_data()
        if df.empty:
            return "No data available yet."
            
        report = []
        report.append("# GPS AIedu: BÁO CÁO PHÂN TÍCH SƯ PHẠM")
        report.append(f"Ngày lập báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        
        # 1. Tổng quan hệ thống
        report.append("## 1. Tổng quan hệ thống")
        report.append(f"- Tổng số tin nhắn: {len(df)}")
        report.append(f"- Số học sinh tham gia: {df['student_id'].nunique()}")
        report.append(f"- Tỷ lệ GPS: G({len(df[df['gps_step']=='G'])}) | P({len(df[df['gps_step']=='P'])}) | S({len(df[df['gps_step']=='S'])})\n")
        
        # 2. Independence Index (II) Ranking
        report.append("## 2. Chỉ số tự chủ (Independence Index - II)")
        report.append("| Học sinh | Lớp | Profile | Chỉ số II | Trạng thái |")
        report.append("| :--- | :--- | :--- | :--- | :--- |")
        
        for sid, group in df.groupby('student_id'):
            s_data = group.iloc[0]
            gps_counts = group['gps_step'].value_counts()
            s = gps_counts.get('S', 0)
            g = gps_counts.get('G', 0)
            p = gps_counts.get('P', 0)
            ii = s / (g + p + 0.1)
            
            status = "🔥 Cao" if ii > 1.0 else ("⚡ Trung bình" if ii > 0.5 else "🆘 Cần hỗ trợ")
            report.append(f"| {sid} | {s_data['class']} | {s_data['profile']} | {ii:.2f} | {status} |")
            
        # 3. Knowledge Gap Analysis
        report.append("\n## 3. Phân tích lỗ hổng kiến thức")
        report.append("Dựa trên tần suất học sinh phải quay lại bước [G]uide nhiều lần:")
        
        guide_freq = df[df['gps_step'] == 'G'].groupby('student_id').size().sort_values(ascending=False)
        for sid, count in guide_freq.head(5).items():
            report.append(f"- **{sid}**: Đang gặp khó khăn lớn (cần {count} lượt hướng dẫn).")
            
        return "\n".join(report)

if __name__ == "__main__":
    analytics = TeacherAnalytics()
    report_content = analytics.generate_report()
    
    with open("reports/TEACHER_INSIGHT_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("Báo cáo Insight cho giáo viên đã được tạo tại: reports/TEACHER_INSIGHT_REPORT.md")
