# Workflow tự động cho Tuần 1 (QA + vận hành)

Mục tiêu: bạn có thể **bấm chạy** để (1) tạo dữ liệu mock “như thật”, (2) kiểm thử end‑to‑end (gán nhãn + ẩn danh + cảnh báo), và (3) chuyển sang vận hành thật mà không phải làm tay.

## 1) Workflow QA tự động ngay trong Google Sheets (khuyến nghị)

### 1.1. Setup 1 lần
1. Mở Google Sheets của dự án.
2. Extensions → Apps Script.
3. Dán nội dung file `src/tools/gas_script.js` vào project Apps Script (hoặc đồng bộ theo cách bạn đang dùng).
4. Chỉnh `CONFIG`:
   - `SALT`: đổi giá trị và lưu offline (không chia sẻ công khai).
   - `ADMIN_EMAIL`: email nhận cảnh báo.
   - Giữ `ENABLE_EMAIL_ALERTS: false` trong giai đoạn test.
5. Reload lại Google Sheets để menu **GPS QA** xuất hiện.

### 1.2. Chạy QA “1‑click”
Trong menu **GPS QA**:
1. `Setup QA Sheets`
2. `Seed Realistic Mock Data` (tạo dữ liệu theo nhiều kiểu học sinh: giỏi/đại trà/chậm/cá biệt)
3. `Run Week1 Smoke Test`

Kết quả sẽ nằm ở sheet `QA - Results`:
- `Accuracy` (nhãn tự động so với “truth” trong dữ liệu mock) nên ≥ 0.90
- `Hash OK` phải bằng `Total logs`
- Danh sách `Inactive students` phải ra được (không cần email ở giai đoạn QA)

Nếu Accuracy thấp: bạn chỉ cần mở `src/tools/gas_script.js` và tinh chỉnh rule trong `classifyGpsStep()`, rồi chạy lại 3 bước trên.

## 2) Workflow vận hành thật (Sau khi QA pass)

### 2.1. Kết nối Form → Sheet
- Google Form đổ dữ liệu về tab `Raw Data`.
- `onFormSubmit` tự động:
  - gán nhãn `G/P/S` vào cột `L`
  - tạo `student_id_hash` vào cột `M`

### 2.2. Dashboard tự cập nhật
Dashboard đọc từ `Raw Data`:
- cột `L` (Auto Label) và cột `M` (ID Hash)
- các chỉ số theo `src/analysis/metrics.md`

### 2.3. Cảnh báo tự động (inactivity)
1. Bật `CONFIG.ENABLE_EMAIL_ALERTS = true`
2. Tạo time‑driven trigger chạy `checkInactivity` (daily).
3. Khi học sinh không có log ≥ `DAYS_INACTIVE_LIMIT`, hệ thống gửi email tới `ADMIN_EMAIL`.

## 2.4) Playbook chạy thử khi chưa có học sinh
Nếu bạn chưa có lớp để chạy Pilot, bạn có thể tự đóng vai nhiều kiểu học sinh để tạo dữ liệu thực (Form → Sheet → Dashboard → Alerts): xem `docs/research/week1_real_run_playbook.md`.

## 3) Workflow tạo mock data “như thật” (local, phục vụ phân tích / demo)

Bạn có thể sinh mock data theo schema chuẩn ở `config/schema.json` để chạy phân tích offline:
- Generate: `C:\Python314\python.exe src/tools/generate_mock_week1.py --students 90 --days 7 --logs 900`
- Smoke test: `C:\Python314\python.exe src/tools/week1_smoke_test.py --csv data/raw/mock_week1_realistic.csv`

File output: `data/raw/mock_week1_realistic.csv` (đủ trường: hash, timestamp ISO, step G/P/S, satisfaction/difficulty…).
