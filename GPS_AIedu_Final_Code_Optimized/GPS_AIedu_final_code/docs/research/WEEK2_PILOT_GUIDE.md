# HƯỚNG DẪN TRIỂN KHAI & HOÀN THIỆN TUẦN 2 (PILOT READY)

Tài liệu này tổng hợp các bước từ lúc "Code trên máy" đến khi "Học sinh dùng thật" và hoàn tất các mục tiêu nghiên cứu của Tuần 2.

---

## PHẦN 1: TRIỂN KHAI HỆ THỐNG (DEPLOYMENT)

Để hệ thống hoạt động ổn định cho cả lớp học, bạn cần đưa các thành phần lên môi trường Cloud.

### 1.1. Google Apps Script (Hệ thống Log & Phân tích)
1.  Mở Google Sheet dự án, vào **Extensions** > **Apps Script**.
2.  Copy toàn bộ nội dung file `src/tools/gas_script.js` vào file `.gs` trong Apps Script.
3.  **Cấu hình quan trọng**: Sửa các biến trong `CONFIG`:
    - `SALT`: Chuỗi bất kỳ (ví dụ: `gps_ai_secret_2026`).
    - `LOG_TOKEN`: Chuỗi bí mật dùng để xác thực từ Web (ví dụ: `my_secure_token_123`).
4.  **Deploy**: 
    - Chọn **Deploy** > **New Deployment** > **Web App**.
    - Execute as: **Me**.
    - Who has access: **Anyone**.
5.  **Lưu lại Web App URL** (Dạng `.../exec`). Đây là `GAS_LOG_URL`.

### 1.2. Webchat frontend (Next.js)
1.  Tạo tài khoản và dự án mới trên [Vercel](https://vercel.com).
2.  Kết nối với GitHub Repo của bạn, chọn **Root Directory** là `webchat/`.
3.  **Cấu hình Environment Variables**:
    - `OPENAI_API_KEY`: Key của bạn.
    - `GAS_LOG_URL`: URL vừa lấy ở bước 1.1.
    - `GAS_LOG_TOKEN`: Token bí mật bạn tự đặt ở bước 1.1 (`LOG_TOKEN`).
    - `LLM_PROVIDER`: `openai` (Khuyến nghị dùng OpenAI cho Pilot để ổn định).
4.  **Deploy** và lấy link web (ví dụ: `gps-tutor.vercel.app`).

---

## PHẦN 2: QUY TRÌNH 4 BƯỚC HOÀN THÀNH TUẦN 2

### Bước 1: Kiểm thử "Trắng" (Smoke Test)
Sử dụng dữ liệu từ [gps_qna_standard.md](file:///c:/Users/quach/code/GPS_AIedu/docs/research/gps_qna_standard.md) để chat thử.
- Mở link Webchat vừa deploy.
- Nhập ID: `TEST_HS01`.
- Thực hiện Session 1 (G -> P -> S đầy đủ).
- **Kiểm tra**: Mở Google Sheet, nếu thấy dòng mới xuất hiện với đầy đủ Auto Label [G], [P], [S] và mã Hash => **Thành công 50%**.

### Bước 2: Thiết lập nhóm đối chứng (Control Group Setup)
Dựa trên [effectiveness_evaluation_plan.md](file:///c:/Users/quach/code/GPS_AIedu/docs/research/effectiveness_evaluation_plan.md).
- Chia danh sách lớp Pilot thành 2 nhóm: **A (Experimental)** và **B (Control)**.
- **Nhóm A**: Dùng link Webchat GPS.
- **Nhóm B**: Dùng link Webchat thường (hoặc yêu cầu các em dùng ChatGPT/Gemini gốc nhưng vẫn nộp log vào Google Form thủ công).

### Bước 3: Chạy Pilot thực tế (Real Class Day)
1.  **Khảo sát Pre-test**: Gửi link Form MSLQ (đã dịch tại `mslq_survey_vn.md`) cho học sinh làm trong 10 phút đầu.
2.  **Training**: Dùng 15 phút hướng dẫn nhóm A về 3 bước **Guide - Practice - Solve**.
3.  **Thực hiện**: Cho học sinh thực hiện bài toán Xác xuất (Session 1 & 2 trong Q&A Standard).

### Bước 4: Phân tích kết quả đầu tiên (The Evidence)
Cuối tuần 2, bạn cần chạy script này để chứng minh hệ thống hoạt động:
1.  Mở terminal tại thư mục gốc dự án.
2.  Cài đặt thư viện: `pip install -r src/analysis/requirements.txt`.
3.  Tải dữ liệu `Raw Data` từ Google Sheets về thành file `pilot_week2.csv`.
4.  Chạy phân tích:
    ```bash
    python src/analysis/behavior_analysis.py pilot_week2.csv
    ```
5.  Kiểm tra thư mục `reports/` để xem hình ảnh ma trận Markov và phân nhóm học sinh.

---

## CHECKLIST HOÀN THÀNH TUẦN 2 (MỤC TIÊU CỐT LÕI)
- [ ] Website Webchat đã online và học sinh truy cập được.
- [ ] Google Sheet thu thập đủ ít nhất 50 lượt chat từ học sinh thật.
- [ ] Có kết quả khảo sát MSLQ Pre-test (dữ liệu Baseline).
- [ ] Ma trận Markov (từ bước 4) cho thấy một xu hướng chuyển dịch tích cực (ví dụ: tỷ lệ G -> P cao).
- [ ] Giáo viên đã nhận được cảnh báo (Alert) đầu tiên về học sinh gặp khó khăn trên Dashboard.

---
**Ghi chú**: Nếu gặp lỗi `GAS_LOG_URL` không nhận dữ liệu, hãy kiểm tra xem bạn đã bấm "Authorize" trong Apps Script và chọn "Anyone" khi deploy chưa.
