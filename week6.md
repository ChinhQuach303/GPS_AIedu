# HƯỚNG DẪN CHI TIẾT TUẦN 6: Tổng hợp, Đánh giá và Bảo vệ Nghiên cứu

## MỤC TIÊU TUẦN 6

Tuần cuối cùng tập trung vào việc chuyển hóa toàn bộ dữ liệu thô thành tri thức khoa học. Chúng ta cần chứng minh rằng sự kết hợp giữa mô hình **G.P.S.** (cho học sinh) và khung **G.U.I.D.E.** (cho giáo viên) đã thực sự thay đổi tư duy học tập.

1. **Phân tích Đối chuẩn Cuối cùng**: Hoàn tất so sánh thống kê (ANCOVA) giữa nhóm Thực nghiệm và Đối chứng.
2. **Tổng kết Hành vi**: Vẽ lại bức tranh "sự thăng tiến" của học sinh từ phụ thuộc sang tự chủ.
3. **Viết Báo cáo Tổng kết**: Đóng gói các kết luận quan trọng về phương pháp sư phạm.
4. **Bảo vệ Dự án**: Chuẩn bị các luận điểm phản biện để chứng minh tính thực tiễn và bền vững.

---

## DANH SÁCH CÔNG VIỆC CHI TIẾT

### 6.1. Thu thập và Nhập liệu Post-test

- **Mô tả**: Sử dụng file `pre_post_comparison_template.csv` để nhập điểm của cả 2 nhóm.
- **Lưu ý**: Đảm bảo mã `Student Hash` trùng khớp hoàn toàn với dữ liệu hành vi.

### 6.2. Chạy Phân tích Thống kê Chuyên sâu

- **Hake's Gain ($g$)**: Tính toán mức độ tăng trưởng thực tế.
- **Cohen's d**: Xác định quy mô ảnh hưởng của phương pháp.
- **Giao thoa Dữ liệu**: Tìm mối tương quan giữa `Independence Index` (hành vi) và `Learning Gain` (điểm số).

### 6.3. Vẽ "Bản đồ Tư duy" (Sankey Diagram)

- **Mô tả**: Sử dụng Graduation Matrix để tạo sơ đồ dòng chảy, cho thấy sự di chuyển của học sinh giữa các Profile học tập từ Tuần 1 đến Tuần 6.
- **Mục tiêu**: Chứng minh phần lớn học sinh đã "graduation" thành công.

### 6.4. Viết Báo cáo Nghiên cứu Cuối cùng

- **Cấu trúc**:
  - Tóm tắt (Abstract)
  - Vấn đề nghiên cứu (Research Problem)
  - Phương pháp luận (G.P.S + G.U.I.D.E)
  - Kết quả (Behavioral vs Quantitative)
  - Thảo luận và Đề xuất.

---

## TIẾN ĐỘ TUẦN CUỐI

- **Thứ 2**: Tổ chức bài thi Post-test cho cả 2 nhóm.
- **Thứ 3**: Nhập điểm và chạy script `behavior_analysis.py`.
- **Thứ 4**: Phân tích các trường hợp đặc biệt (những học sinh không tiến bộ) để tìm nguyên nhân.
- **Thứ 5**: Hoàn thiện bộ biểu đồ và báo cáo impact.
- **Thứ 6**: Review nội bộ và diễn tập phản biện.

---

## CÂU HỎI PHẢN BIỆN CỐT LÕI (Chuẩn bị bảo vệ)

1. "Làm sao chúng ta biết sự tiến bộ là do mô hình G.P.S chứ không phải do sự thông minh vốn có của học sinh?" (Trả lời bằng ANCOVA).
2. "Nếu không có AI hỗ trợ, học sinh có duy trì được năng lực này không?" (Trả lời bằng Reflection data và Independence Index).
3. "Giáo viên tốn bao nhiêu thời gian để vận hành khung G.U.I.D.E?" (Trả lời bằng nhật ký can thiệp).

---

## KẾT QUẢ ĐÁNH GIÁ CUỐI KỲ (FINAL VERDICT)

Sau 6 tuần triển khai trên quy mô 2.375 phiên hội thoại:

- **Hiệu quả Học tập (Hake's Gain)**: GPS đạt **g ≥ 0.4** ở tất cả các trình độ (Vượt xa Non-GPS chỉ đạt ~0.2).
- **Chỉ số Tác động (Cohen's d)**: **1.209** (Mức độ tác động **CỰC LỚN** - Large Effect Size).
- **Math Density**: **14.02** (Đạt đỉnh cao ở tuần cuối, gấp gần 5 lần so với nhóm đối chứng).
- **Independence Index**: **0.335** (Sự phục hồi và làm chủ kiến thức sau giai đoạn thử thách ở tuần 5).
- **Scaffolding Depth**: **3.22** (Học sinh sẵn sàng tương tác sâu với AI để giải các bài toán tổng hợp khó nhất).
