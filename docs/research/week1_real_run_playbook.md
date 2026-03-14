# Real Run Playbook – Tuần 1 GPS AIedu
*Phiên bản tuần 1 (Webchat Next.js → Google Apps Script Webhook → Raw Data → Dashboard → Alerts)*

Mục tiêu: triển khai workflow định tuyến học sinh dùng chung một trang Webchat duy nhất. AI tự nhận diện System Prompt GPS và hệ thống tự động lưu log ngầm về Google Sheet.

---

## 0) Tổng quan luồng chạy thực tế (Tuần 1)

```text
Học sinh (hoặc persona giả lập)
  └─► Truy cập Webchat (nhập ID, Class, Topic)
         │
         ├─► Chat trực tiếp với AI (đã nạp sẵn System Prompt)
         │
         └─► Hệ thống tự động đẩy dữ liệu ngầm sau mỗi lượt chat
                │
                ▼ Google Apps Script (doPost Webhook)
         Google Sheet "Raw Data"
                │  cột L = Auto Label (G/P/S/Unknown)
                │  cột M = Student Hash (SHA-256(salt + student_id))
                ▼
         Dashboard (Per Student / GPS Tracker / Alerts)
                │
                ▼ checkInactivity (trigger hằng ngày, tuỳ chọn)
         Email cảnh báo → Giáo viên → Can thiệp
```

Quy chuẩn hỏi–đáp để dữ liệu “sạch” và đúng G→P→S: `docs/research/gps_qna_standard.md`.

---

## Bước 1 – Thiết lập CSDL và Webhook log (chạy 1 lần, ~10 phút)

Thay vì tạo Google Form, chúng ta sẽ biến Google Sheet thành một API nhận dữ liệu ngầm (Webhook).

### 1.1. Tạo Google Sheet và mở Apps Script
1. Tạo Google Sheet mới (gợi ý tên: **`GPS_AIedu_Data`**).
2. Tạo trước một tab đặt tên là **`Raw Data`** (nếu chưa có).
3. Trong Sheet: **Extensions → Apps Script**.
4. Tạo 1 file trong Apps Script project:

| File Apps Script | Nội dung từ repo |
|---|---|
| `Code.gs` | `src/tools/gas_script.js` |

### 1.2. Chỉnh CONFIG trước khi chạy
Trong `Code.gs` (`gas_script.js`), cấu hình các tham số sau:
```javascript
const CONFIG = {
  SPREADSHEET_ID: "ID_CUA_FILE_GOOGLE_SHEET_HIEN_TAI", // Để đảm Web App ghi đúng Sheet
  SHEET_NAME: "Raw Data",
  QA_SHEET_NAME: "QA - Raw Data",
  QA_RESULTS_SHEET_NAME: "QA - Results",
  SALT: "THAY_BANG_CHUOI_BI_MAT_TUY_Y",
  LOG_TOKEN: "CHUOI_BI_MAT_CHO_WEBHOOK", // Đặt 1 chuỗi bí mật bất kỳ
  ADMIN_EMAIL: "email_giaovien@truong.edu.vn",
  ENABLE_EMAIL_ALERTS: false,
  // ...
};
```

### 1.3. Chuẩn hoá schema tab `Raw Data` (A..M)
1. Trong Apps Script, chạy hàm **`initRawDataSchema()`** (Run ▶) để tạo/chuẩn hoá header 13 cột A..M trên tab `Raw Data`.
2. Kiểm tra tab `Raw Data` có đủ các cột: `Timestamp`, `Student ID`, `Class`, `Topic`, `Profile`, `Question`, `AI Response`, `Notes`, `Satisfaction`, `Difficulty`, `GPS Step (Truth)`, `Auto Label`, `Student Hash`.

### 1.4. Deploy Web App để lấy Endpoint (GAS_LOG_URL)
1. Bấm nút **Deploy → New deployment**.
2. Chọn Type: **Web app**.
   - Execute as: **Me**.
   - Who has access: **Anyone**.
3. Bấm **Deploy**. Sao chép **Web app URL** (Đây là `GAS_LOG_URL` cài cho Webchat bên dưới).

Ví dụ format URL:
`https://script.google.com/macros/s/<DEPLOYMENT_ID>/exec`
---

## Bước 2 – Khởi chạy Giao diện Webchat (Next.js)

Giao diện học sinh giờ đây nằm tại source code `webchat/`, không cần dùng Poe nữa.

1. Mở Terminal, đi vào thư mục webchat:
   ```bash
   cd webchat
   cp .env.example .env.local
   ```
2. Mở file `.env.local` và cấu hình tối thiểu:
   - `LLM_PROVIDER=openai`
   - `OPENAI_API_KEY=...`
   - (tuỳ chọn) `OPENAI_BASE_URL=...` nếu dùng OpenAI-compatible provider khác
   - `GAS_LOG_URL=...` (từ Bước 1.4)
   - `GAS_LOG_TOKEN=...` (giống `CONFIG.LOG_TOKEN`)

   Nếu bạn muốn chạy miễn phí local (không dùng API): đặt `LLM_PROVIDER=ollama` và cấu hình `OLLAMA_MODEL` (gợi ý: `qwen2-math:1.5b-instruct-q5_K_M`).
3. Chạy môi trường local (hoặc upload qua Vercel để lấy link public):
   ```bash
   npm.cmd install
   npm.cmd run dev
   ```
4. Truy cập `http://localhost:3000` kiểm tra chat. Khi chat, dữ liệu sẽ tự động đồng bộ thời gian thực về tab `Raw Data` của bạn.

---

## Bước 3 – Tạo Form MSLQ (Pre/Post) (chạy 1 lần, ~3–5 phút)

1. Tạo file mới trong Apps Script tên **`SetupMSLQ.gs`**.
2. Dán toàn bộ nội dung từ:
   ```
   src/tools/setup_mslq_form.js
   ```
3. Chọn hàm **`createMslqForm`** → Run ▶.
4. Copy **Form link** từ alert hoặc Logs.

---

## Bước 4 – Thiết lập Dashboard (chạy 1 lần, ~5–10 phút)

### Cách nhanh (khuyến nghị): chạy script tự tạo dashboard
1. Tạo file mới trong Apps Script tên **`SetupDashboard.gs`**.
2. Dán toàn bộ nội dung từ:
   ```
   src/tools/setup_dashboard.js
   ```
3. Chạy hàm **`setupDashboard()`** (Run ▶) để tự tạo các tab `Per Student`, `GPS Tracker`, `Alerts` và điền công thức.

Nếu bạn muốn tự kiểm soát công thức: tham khảo `src/analysis/dashboard_formulas.md`.

---

## Bước 5 – Tự giả lập dữ liệu (khi CHƯA có học sinh)

Mục tiêu: bạn tự đóng vai 5 kiểu học sinh để tạo dữ liệu thật qua Webchat (Webchat → GAS → `Raw Data` → Dashboard).

### 5.1. 5 persona giả lập (khuyến nghị)
- `HS0001` **Advanced/Fast**: hay đi nhanh (P→S hoặc S), tự giải phần lớn.
- `HS0002` **Typical/Normal**: đa số đi đúng **G→P→S**.
- `HS0003` **Struggling/Slow**: G nhiều, P lặp (G→P→P), đôi khi không lên S.
- `HS0004` **Offtrack**: hay xin đáp án/giải giúp, lệch quy trình.
- `HS0005` **Inactive**: làm 1 ngày rồi dừng (để test cảnh báo).

### 5.2. Quy trình chạy giả lập trên Webchat
1. Mở Webchat (`http://localhost:3000` hoặc link Vercel).
2. Nhập đúng `Student ID` theo persona (HS0001…HS0005). Giữ `Class` cố định (vd `11A1`) để dễ lọc.
3. Với mỗi persona, thực hiện **24 lượt hỏi** (gợi ý: 8 vòng **G→P→S** = 24).
4. Sau mỗi lượt, đợi AI trả lời xong rồi mới gửi câu tiếp theo.

### 5.3. Bộ câu hỏi mẫu (copy/paste)
Toàn bộ 24 câu cho từng persona nằm ở: `docs/research/week1_persona_question_scripts.md`.

Gợi ý cách dùng nhanh:
- Mỗi persona: mở 1 tab trình duyệt riêng, nhập đúng `Student ID`, rồi copy lần lượt 01→24.
- Bạn không cần điền Google Form nữa: hệ thống tự log vào `Raw Data` sau mỗi lượt chat.

### 5.4. Check ngay sau mỗi lượt để chắc hệ thống hoạt động
Vào tab `Raw Data` kiểm tra:
- Có dòng mới sau mỗi lượt chat.
- Cột `L` tự có nhãn `G/P/S/Unknown`.
- Cột `M` tự có hash **64 ký tự hex** (SHA-256).

### 5.5. Test cảnh báo “Inactive” (persona HS0005)
- Chỉ thực hiện 6 lượt ở phần HS0005 (Ngày 1) rồi dừng hẳn.
- Để test nhanh, tạm đặt `CONFIG.DAYS_INACTIVE_LIMIT = 0.01` (~15 phút) trong `src/tools/gas_script.js`, chạy `checkInactivity()`, sau đó đặt lại `3`.
