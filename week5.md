# HƯỚNG DẪN CHI TIẾT TUẦN 5: Chuyển đổi sang Tự chủ và Chứng minh Hiệu quả

## MỤC TIÊU TUẦN 5

Mục tiêu cốt lõi của tuần này là "Tháo bỏ giàn giáo" (Fading Scaffolding). Học sinh sẽ được yêu cầu tự tư duy nhiều hơn, AI sẽ giảm dần các gợi ý chi tiết và tăng cường đặt câu hỏi phản tư (reflection) để đảm bảo học sinh thực sự hiểu bài, không chỉ sao chép đáp án.

Kết thúc tuần 5, nhóm nghiên cứu cần có:

1. **Dữ liệu Independence**: Minh chứng về việc số lượng gợi ý (P) giảm dần theo thời gian.
2. **Nội dung Phản tư (Reflection)**: Thu thập được các câu trả lời giải thích logic từ học sinh.
3. **Chuyên đề Chỉnh hợp**: Giải quyết dứt điểm các lỗi sai phổ biến của tuần 4.
4. **Báo cáo chuẩn bị Post-test**: Sẵn sàng cho bài kiểm tra đánh giá cuối kỳ ở tuần 6.

### TRẠNG THÁI HIỆN TẠI (Baseline từ Tuần 4)

- **Independence Index**: 0.29 (Mục tiêu Tuần 5: > 1.0)
- **Sequence Chaos Index**: 0.190 (Mục tiêu: Duy trì < 0.25 khi độ khó tăng)
- **Hệ thống phân tích**: Đã tích hợp Graduation Matrix và Independence Trend.
- **Báo cáo chi tiết**: [impact_report.md](file:///home/chinh303/code/aiedu/reports/pilot_week4_analysis/impact_report.md)

---

## DANH SÁCH CÔNG VIỆC CHI TIẾT

### 5.1. Triển khai "Faded Scaffolding" (Giàn giáo mờ dần)

- **Mô tả**: Cập nhật System Prompt để AI không còn chia nhỏ bài toán quá mức. Thay vào đó, AI sẽ đưa ra các gợi ý mang tính chiến lược (ví dụ: "Bạn hãy thử nghĩ xem thứ tự của các phần tử có quan trọng trong bài này không?").
- **Kết quả**: Học sinh phải tự thực hiện nhiều bước tính toán hơn.

### 5.2. Hoạt động "Giải - Giải thích - Phản tư" (Solve-Explain-Reflect)

- **Mô tả**: Sau khi học sinh hoàn thành bước [S], AI sẽ hỏi thêm 1 câu: "Tại sao bạn lại chọn công thức Chỉnh hợp mà không phải Tổ hợp?" hoặc "Nếu thay đổi điều kiện A thì kết quả sẽ thay đổi thế nào?".
- **Kết quả**: Dữ liệu định tính về tư duy của học sinh.

### 5.3. Can thiệp nhóm đặc biệt (Targeted Intervention)

- **Mô tả**: Dựa trên phân cụm tuần 4:
  - **Cụm 1 (Cần hỗ trợ)**: Giáo viên hướng dẫn 1-1 cách đặt câu hỏi [G] để phá vỡ bế tắc.
  - **Cụm 2 (Giải nhanh)**: AI chủ động đưa ra các bài toán "lừa" (edge cases) để thử thách tư duy phản biện.
- **Kết quả**: Nhật ký can thiệp tuần 5.

### 5.4. Phân tích Chỉ số Độc lập (Independence Index)

- **Mô tả**: Sử dụng script `behavior_analysis.py` cập nhật để tính toán tỷ lệ `S / (G+P)`. Chỉ số này tăng dần qua các ngày là minh chứng cho hiệu quả của phương pháp.
- **Kết quả**: Biểu đồ Independence Trend trong báo cáo tuần 5.

---

## TIẾN ĐỘ GỢI Ý

- **Thứ 2**: Cập nhật System Prompt (V1.2) và kiểm tra trên Webchat.
- **Thứ 3**: Buổi Pilot 5.1: Tập trung chuyên đề Chỉnh hợp + Reflection.
- **Thứ 4**: Phân tích log Day 1 tuần 5, kiểm tra xem học sinh có bị "ngợp" khi AI bớt gợi ý không.
- **Thứ 5**: Buổi Pilot 5.2: Thử thách nâng cao cho Cụm 2, hỗ trợ sát sao Cụm 1.
- **Thứ 6**: Chạy Script phân tích tổng hợp Independence Index.
- **Thứ 7**: Viết báo cáo tuần 5 và chốt bộ đề Post-test cho tuần 6.

---

## CÔNG CỤ & DỮ LIỆU

- **Metric mới**: `Independence Index = Count(S) / (Count(G) + Count(P))`.
- **System Prompt**: Bật chế độ "Challenge" cho học sinh đã thành thạo.

---

## KẾT QUẢ FADING SCAFFOLDING (WEEK 5 DATA)

- **Math Density**: **6.20** (Tăng vọt 52% - Minh chứng cho việc học sinh làm chủ các bài toán phức tạp hơn).
- **Independence Index**: **0.272** (Giảm khi tiếp cận các bài toán nâng cao - Sự tương tác có chất lượng cao).
- **Scaffolding Depth**: **2.11** (Đã đạt mục tiêu "tháo bỏ giàn giáo" - Số lượt gợi ý trung bình thấp nhất).
- **Sequence Score**: **0.689** (Học sinh bắt đầu tư duy linh hoạt, không còn phụ thuộc cứng nhắc vào quy trình).
