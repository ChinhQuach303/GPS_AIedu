# Real Run Playbook – Tuần 1 GPS AIedu
*Phiên bản tuần 1 (Google Form → Raw Data → auto label/hash → Dashboard → Alerts)*

Mục tiêu: triển khai workflow Tuần 1 ổn định và ít thao tác thủ công nhất (setup 1 lần). Khi chưa có học sinh, bạn có thể tự giả lập nhiều persona để tạo dữ liệu thật.

---

## 0) Tổng quan luồng chạy thực tế (Tuần 1)

```
Học sinh (hoặc persona giả lập)
  └─► Chat AI (đã dán System Prompt GPS Tutor)
         │
         └─► Google Form (nhật ký – 1 submit / 1 lần hỏi)
                │
                ▼ onFormSubmit (trigger Spreadsheet)
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

## Bước 1 – Tạo Form + liên kết Sheet + cài trigger (chạy 1 lần, ~10–15 phút)

### 1.1. Tạo Google Sheet và mở Apps Script
1. Tạo Google Sheet mới (gợi ý tên: **`GPS_AIedu_Data`**).
2. Trong Sheet: **Extensions → Apps Script**.
3. Tạo 2 file trong Apps Script project:

| File Apps Script | Nội dung từ repo |
|---|---|
| `Code.gs` | `src/tools/gas_script.js` |
| `SetupForm.gs` | `src/tools/setup_form_and_sheet.js` |

### 1.2. Chỉnh CONFIG trước khi chạy
Trong `Code.gs` (gas_script.js), chỉnh:
```javascript
const CONFIG = {
  SHEET_NAME: "Raw Data",
  SALT: "THAY_BANG_CHUOI_BI_MAT",
  ADMIN_EMAIL: "email_giaovien@truong.edu.vn",
  ENABLE_EMAIL_ALERTS: false,
  // ... các cột khác giữ nguyên
};
```

### 1.3. Chạy `setupFormAndSheet()`
1. Chọn hàm **`setupFormAndSheet`** → Run ▶.
2. Authorize lần đầu.
3. Script sẽ:
   - Tạo Google Form nhật ký (đúng thứ tự cột để tương thích dashboard)
   - Link Form → Sheet và đổi tên response sheet thành tab `Raw Data`
   - Chuẩn hoá header A..M và cài trigger `onFormSubmit`

✅ Bạn nhận được **Form link** để chia sẻ cho học sinh (hoặc dùng để tự giả lập).

---

## Bước 2 – Tạo Form MSLQ (Pre/Post) (chạy 1 lần, ~3–5 phút)

1. Tạo file mới trong Apps Script tên **`SetupMSLQ.gs`**.
2. Dán toàn bộ nội dung từ:
   ```
   src/tools/setup_mslq_form.js
   ```
3. Chọn hàm **`createMslqForm`** → Run ▶.
4. Copy **Form link** từ alert hoặc Logs.

---

## Bước 3 – Thiết lập Dashboard (chạy 1 lần, ~5–10 phút)

### Cách nhanh (khuyến nghị): chạy script tự tạo dashboard
1. Tạo file mới trong Apps Script tên **`SetupDashboard.gs`**.
2. Dán toàn bộ nội dung từ:
   ```
   src/tools/setup_dashboard.js
   ```
3. Chạy hàm **`setupDashboard()`** (Run ▶) để tự tạo các tab `Per Student`, `GPS Tracker`, `Alerts` và điền công thức.

Nếu bạn muốn tự kiểm soát công thức: tham khảo `src/analysis/dashboard_formulas.md`.

---

## Bước 4A – Chạy thử thực tế khi CHƯA có học sinh (tự giả lập dữ liệu)

Bạn sẽ tự đóng vai nhiều “kiểu học sinh” để tạo dữ liệu thật (Chat AI → Form → Sheet).

### 4A.1. Tạo 5 persona (khuyến nghị)
- `HS0001` – **Advanced/Fast**: hay đi nhanh (P→S hoặc S), tự giải phần lớn.
- `HS0002` – **Typical/Normal**: đa số đi đúng **G→P→S**.
- `HS0003` – **Struggling/Slow**: G nhiều, P lặp (G→P→P), đôi khi không lên S.
- `HS0004` – **Offtrack**: hay xin “đáp án/giải giúp”, lệch quy trình.
- `HS0005` – **Inactive**: làm 1 ngày rồi dừng (để test cảnh báo).

### 4A.2. Cách nhập 1 session “như thật”
Mỗi session (một bài/tình huống) nên tạo 2–4 lượt submit:
- **G**: “Giải thích…/Định nghĩa…/Phân biệt…”
- **P**: “Hướng dẫn…/Gợi ý bước…/Em bị kẹt ở bước…”
- **S**: “Em ra kết quả…, đúng không?/Kiểm tra lời giải…”

Template hỏi–đáp dùng chung xem `docs/research/gps_qna_standard.md`.

### 4A.3. Kiểm tra ngay sau mỗi submit
Vào tab `Raw Data` kiểm tra:
- Cột `L` tự có nhãn `G/P/S/Unknown`
- Cột `M` tự có hash (64 ký tự hex)

---

## Bước 4B – Tập huấn học sinh (khi có lớp thật, 20–30 phút)

1. Giới thiệu mô hình G.P.S (G→P→S) và “không xin đáp án”.
2. Demo 1 bài theo đúng G→P→S (dán system prompt `src/ai/system_prompt.md`).
3. Học sinh thực hành dùng prompt mẫu `src/ai/sample_prompts/sample_prompts_table.md`.
4. Học sinh điền Form ngay trong buổi để xác nhận hệ thống hoạt động.

---

## Bước 5 – Vận hành hằng ngày (5–10 phút/ngày)

- Mở `Alerts`: xem Satisfaction ≤ 2, Unknown.
- Mở `Per Student`: xem `Days Since Last` ≥ 3 để nhắc nhở.
- Mở `GPS Tracker`: xem phân bố %G/%P/%S (quá nhiều S có thể là xin đáp án).

---

## Bước 6 – Bật email cảnh báo (khi đã ổn định)

1. Trong `Code.gs`, đổi `ENABLE_EMAIL_ALERTS: true`.
2. Cài time-driven trigger cho `checkInactivity` (daily).
3. Test nhanh có thể tạm đặt `DAYS_INACTIVE_LIMIT: 0.01` (~15 phút), sau đó đặt lại 3.

---

## Tham khảo nhanh

| File | Tác dụng |
|------|----------|
| `src/tools/gas_script.js` | Logic chính: gán nhãn G/P/S + hash + inactivity + QA |
| `src/tools/setup_form_and_sheet.js` | Setup 1 lần: tạo Form + Raw Data + trigger |
| `src/tools/setup_dashboard.js` | Setup 1 lần: tạo Dashboard tabs + công thức |
| `src/tools/setup_mslq_form.js` | Setup 1 lần: tạo Form MSLQ Pre/Post |
| `docs/research/gps_qna_standard.md` | Quy chuẩn hỏi–đáp chung theo G/P/S |
| `src/analysis/dashboard_formulas.md` | Công thức chi tiết (nếu làm thủ công) |
| `docs/legal/consent_form.md` | Phiếu đồng thuận phụ huynh/học sinh |

