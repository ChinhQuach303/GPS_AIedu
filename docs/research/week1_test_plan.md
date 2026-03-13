# Kế hoạch kiểm thử nội bộ Tuần 1

## Mục tiêu
Kiểm thử luồng Form → Sheet → Apps Script → Dashboard trước khi pilot tuần 2.

## 1. Chuẩn bị
- Đã tạo Google Form theo schema.
- Đã có Google Sheet đích (Form Responses).
- Đã dán `src/tools/gas_script.js` vào Apps Script.
- Đã cấu hình `CONFIG` đúng tên sheet và cột thực tế.
- Tạo trigger thời gian cho `checkInactivity` (mỗi 15 phút hoặc mỗi ngày).

## 2. Bộ dữ liệu thử (20 bản ghi)
- File mẫu: `data/raw/mock_week1.csv`
- Phân bổ: 5 G, 5 P, 5 S, 5 mơ hồ.

## 3. Các bước kiểm thử chi tiết

### Bước 1: Kiểm Form → Sheet (Ingestion)
- Nhập 20 bản ghi mẫu vào Form.
- Pass nếu:
  - 100% bản ghi xuất hiện trong Sheet.
  - Cột dữ liệu không lệch (timestamp, student_id, question, response, gps_step, email, satisfaction, difficulty).

### Bước 2: Kiểm Script gán nhãn (Regex)
- Quan sát cột `gps_step` sau khi submit.
- So sánh nhãn với “ground truth” trong file mock.
- Pass nếu:
  - >= 90% đúng với mẫu rõ ràng (G/P/S).
  - >= 80% đúng với mẫu mơ hồ.

### Bước 3: Kiểm Trigger nhắc nhở
- Sửa thời gian trong 3 bản ghi thành cách đây > 3 ngày.
- Chạy `checkInactivity` thủ công hoặc chờ trigger.
- Pass nếu:
  - Email nhắc gửi đúng tới HS tương ứng.

### Bước 4: Kiểm Dashboard
- Mở Dashboard và kiểm:
  - Per Student: tổng số entry, last_entry_date, G/P/S count.
  - Alerts: HS >= 3 ngày không nộp.
  - GPS Tracker: biểu đồ phân bố G/P/S.
- Pass nếu:
  - Số liệu khớp 20 bản ghi đã nhập.

### Bước 5: Kiểm Quy trình nhãn thủ công
- 2 CTV gán nhãn 20 mẫu giống nhau.
- Tính Cohen’s Kappa.
- Pass nếu:
  - Kappa > 0.8.

## 4. Kết quả cần chốt
- Ghi lỗi phát hiện và sửa.
- Sau khi pass, đóng băng v1.0 cho tuần 2.
