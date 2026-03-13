# BÁO CÁO CÔNG TÁC CHUẨN BỊ - TUẦN 1 (CHI TIẾT CHO GIÁO VIÊN)
**Dự án: Ứng dụng mô hình G.P.S. và quy trình G.U.I.D.E trong dạy học Toán 11 với AI**

**Kính gửi:** Ban Giám hiệu và Quý Thầy/Cô Giáo viên Toán,

Tài liệu này giải thích chi tiết những việc nhóm dự án đã hoàn thành trong **Tuần 1 (giai đoạn xây nền tảng)**, tập trung vào: (1) công cụ thu thập và theo dõi, (2) cách AI được “định hướng sư phạm” để không giải hộ, (3) cơ chế tự động gán nhãn – ẩn danh – cảnh báo, và (4) kiểm thử nội bộ để sẵn sàng bước sang **Tuần 2 (Pilot)**.

Quy trình vận hành đã được chuẩn hóa thành playbook để giáo viên/nhóm dự án triển khai nhất quán: `docs/research/week1_real_run_playbook.md`.

---

## 1. Mục tiêu tuần 1 và “đầu ra” cần có
Trong Tuần 1, nhóm tập trung chuẩn bị đủ 3 lớp nền tảng để giáo viên triển khai được Pilot:

1) **Nền tảng sư phạm (Pedagogy)**
- Mô hình G.P.S cho học sinh: **Guide → Practice → Solve**.
- Quy trình G.U.I.D.E cho giáo viên: **Generate Awareness → Understand → Intervene → Deepen → Evaluate**.

2) **Nền tảng kỹ thuật (Tools)**
- Form/Sheet để thu nhật ký tương tác AI.
- Apps Script để tự động: gán nhãn G/P/S, ẩn danh ID, cảnh báo “im lặng 3 ngày”.
- Dashboard để giáo viên theo dõi và can thiệp.

3) **Nền tảng pháp lý và đo lường (Ethics & Measurement)**
- Phiếu đồng thuận, cam kết bảo mật dữ liệu.
- Thang đo MSLQ (20 items) bản tiếng Việt (phục vụ đo biến tự điều chỉnh học tập).

---

## 2. Những việc đã làm trong tuần 1 (giải thích theo góc nhìn giáo viên)

### 2.0. Chuẩn hóa quy trình triển khai “1-link/1-dashboard” (giảm thao tác thủ công)
**Mục tiêu:** để giáo viên không phải tự lắp ghép thủ công từng phần (Form, Sheet, công thức Dashboard…), nhóm đã chuẩn hóa thành các bước cài đặt chạy một lần.

**Nhóm đã làm:**
- Hoàn thiện playbook triển khai Tuần 1: `docs/research/week1_real_run_playbook.md` (Bước 1–3 có thể tự động hoá).
- Cung cấp script setup chạy 1 lần để tạo Form + link Sheet + cài trigger: `src/tools/setup_form_and_sheet.js` (hàm `setupFormAndSheet()`).
- Cung cấp script setup dashboard chạy 1 lần để tạo các tab theo dõi và điền công thức: `src/tools/setup_dashboard.js` (hàm `setupDashboard()`).

**Giáo viên sẽ nhận được sau khi setup xong:**
- 01 **Form link** để học sinh điền nhật ký.
- 01 Google Sheet có tab `Raw Data` (dữ liệu), kèm các tab Dashboard (`Per Student`, `Alerts`, `GPS Tracker`).

---

### 2.1. Chuẩn hóa “luồng dữ liệu” để giáo viên theo dõi được theo thời gian thực
**Mục tiêu:** giáo viên không phải đọc từng đoạn chat; hệ thống tự tổng hợp để thấy nhanh học sinh đang “mắc kẹt ở đâu”.

**Nhóm đã làm:**
- Chuẩn hóa schema nhật ký tương tác theo các trường cốt lõi: thời gian, ID học sinh, nội dung hỏi/đáp, bước G/P/S, mức hài lòng, độ khó… (tham khảo `config/schema.json`).
- Thiết kế logic để dữ liệu từ Google Form chảy về Google Sheets (tab “Raw Data”), làm nguồn cho Dashboard. Việc tạo Form và liên kết về Sheet được chuẩn hóa bằng `setupFormAndSheet()` trong `src/tools/setup_form_and_sheet.js`.

**Ý nghĩa sư phạm cho giáo viên:**
- Giáo viên có thể xem tỷ lệ G/P/S của từng học sinh theo tuần, từ đó nhận diện “học sinh đang dừng ở đâu”:
  - Dừng ở **G**: hiểu khái niệm chưa chắc, cần củng cố định nghĩa/công thức.
  - Dừng ở **P**: đang cần giàn giáo theo bước, cần ví dụ tương tự hoặc gợi ý.
  - Dừng ở **S**: đã có lời giải, cần kiểm tra logic/diễn đạt/chuẩn hóa trình bày.

---

### 2.2. Xây dựng “GPS Tutor” (System Prompt) để AI không giải hộ
**Mục tiêu:** tránh tình trạng học sinh dùng AI “lấy đáp án”, đồng thời vẫn nhận được hỗ trợ đúng kiểu “gia sư hướng dẫn”.

**Nhóm đã làm:**
- Viết System Prompt cho AI theo cấu trúc G/P/S, quy định rõ:
  - Không đưa đáp án cuối ngay.
  - Ưu tiên câu hỏi gợi mở và gợi ý từng bước.
  - Học sinh phải trình bày lại cách làm/ý tưởng.
- File tham khảo: `src/ai/system_prompt.md`.

**Ý nghĩa sư phạm cho giáo viên:**
- Mô hình này biến AI thành “giàn giáo” (scaffolding) thay vì “máy giải bài”.
- Giáo viên có thể yêu cầu học sinh nộp **lời giải tự trình bày** (Solve) thay vì ảnh chụp câu trả lời.

---

### 2.3. Soạn ngân hàng prompt mẫu (45 mẫu) để tập huấn học sinh dùng đúng quy trình
**Mục tiêu:** giúp học sinh đặt câu hỏi theo đúng “bước học”, giảm tình trạng hỏi chung chung hoặc xin đáp án.

**Nhóm đã làm:**
- Tạo 45 prompt mẫu cho Toán 11 (Tổ hợp & Xác suất), chia đều:
  - 15 prompt **Guide**: hỏi khái niệm, công thức, phân biệt, “tại sao”.
  - 15 prompt **Practice**: xin gợi ý bước 1/2/3, hỏi sai ở đâu, chia nhỏ bài.
  - 15 prompt **Solve**: tự trình bày lời giải và nhờ AI kiểm tra logic/tính toán.
- File tham khảo: `src/ai/sample_prompts/sample_prompts_table.md`.

**Ý nghĩa sư phạm cho giáo viên:**
- Khi tập huấn, giáo viên chỉ cần đưa bộ mẫu và nhắc “đi theo thứ tự G→P→S”.
- Học sinh “học giỏi” có thể rút gọn (P/S nhiều hơn), nhưng vẫn giữ nguyên nguyên tắc: **tự trình bày** trước khi xin AI xác nhận.

---

### 2.4. Tự động gán nhãn G/P/S + ẩn danh dữ liệu (Hash+Salt)
**Mục tiêu:** giảm thao tác thủ công; đảm bảo dữ liệu học sinh được bảo vệ khi phân tích/chia sẻ.

**Nhóm đã làm (Apps Script):**
- Khi có submission mới (trigger `onFormSubmit`):
  1) Đọc câu hỏi của học sinh.
  2) Tự động gán nhãn **G/P/S** dựa trên rule (từ khóa; có chuẩn hóa chữ có dấu để tăng độ bền).
  3) Tạo `student_id_hash = SHA-256(salt + student_id)` để ẩn danh.
- File tham khảo: `src/tools/gas_script.js`.

**Điểm quan trọng để giáo viên nắm:**
- Giáo viên/học sinh **không cần gán nhãn bằng tay** trong vận hành thường ngày.
- Hệ thống vẫn có cột “GPS Step (Truth)” để đối chiếu khi cần kiểm chứng (giai đoạn QA hoặc khi học sinh tự báo bước đang làm).

**Giải thích để giáo viên hiểu “vì sao cần ẩn danh”:**
- Khi tổng hợp/đối chiếu số liệu (Dashboard/biểu đồ), chúng ta có thể làm trên **hash** thay vì ID thật.
- `SALT` cần được lưu offline (nhóm dự án quản lý), giảm rủi ro rò rỉ danh tính học sinh.

---

### 2.5. Cảnh báo tự động học sinh “im lặng 3 ngày” để giáo viên can thiệp (Intervene)
**Mục tiêu:** giúp giáo viên không bỏ sót học sinh “bỏ cuộc giữa chừng”.

**Nhóm đã làm:**
- Viết hàm `checkInactivity`:
  - Quét log theo học sinh.
  - Nếu không có log mới trong **≥ 3 ngày** → đưa vào danh sách cảnh báo và (khi bật cấu hình) gửi email tới giáo viên/phụ trách.
- Cấu hình an toàn:
  - `ENABLE_EMAIL_ALERTS` để **tắt/bật** gửi email (khuyến nghị tắt trong giai đoạn test).

**Gợi ý xử lý sư phạm khi nhận cảnh báo:**
- Nhắc học sinh quay lại bằng việc yêu cầu tối thiểu 1 chu kỳ **G→P→S** cho 1 bài cụ thể.
- Nếu học sinh thuộc nhóm “cá biệt/offtrack” (hay xin đáp án): giáo viên yêu cầu nộp “bản nháp” hoặc trình bày 3 ý: công thức dùng, lý do dùng, và phép biến đổi chính.

---

### 2.6. Dashboard theo dõi cho giáo viên (Understand → Evaluate)
**Mục tiêu:** giáo viên nhìn tổng quan và theo dõi theo cá nhân mà không phải lọc tay.

**Nhóm đã làm:**
- Thiết kế công thức/logic Dashboard (gợi ý 4 tab):
  - **Raw Data**: dữ liệu gốc từ Form.
  - **Per Student**: tổng log, %G/%P/%S, mức hài lòng trung bình.
  - **Alerts**: lọc các bản ghi hài lòng thấp / cảnh báo.
  - **GPS Tracker**: phân bố G/P/S và hoạt động theo thời gian.
- File tham khảo công thức: `src/analysis/dashboard_formulas.md` và `src/analysis/metrics.md`.
- Để giảm thao tác thủ công, nhóm cung cấp `setupDashboard()` trong `src/tools/setup_dashboard.js` để tạo sẵn các tab và điền công thức.

**Cách đọc nhanh cho giáo viên:**
- %G cao nhưng ít chuyển sang P/S: học sinh đang “đọc hiểu” nhưng chưa làm được bài.
- %P cao, hài lòng thấp: học sinh bị kẹt ở thao tác/biến đổi, cần ví dụ tương tự hoặc chữa mẫu.
- %S có nhưng khó cao: có thể học sinh làm được nhưng thiếu tự tin / sai sót trình bày, cần phản hồi chất lượng lời giải.

---

### 2.7. Kiểm thử nội bộ (Validation) và dữ liệu mock “như thật”
**Mục tiêu:** trước khi đưa vào lớp, nhóm phải chắc chắn hệ thống chạy được end‑to‑end.

**Nhóm đã làm:**
- Lập kế hoạch test tuần 1 (Pass/Fail): `docs/research/week1_test_plan.md`.
- Xây dựng **workflow QA tự động** ngay trong Google Sheets:
  - Tạo sheet QA riêng (`QA - Raw Data`) để không ảnh hưởng dữ liệu thật.
  - Có thể sinh dữ liệu mock “giống hành vi thật” theo nhiều kiểu học sinh (giỏi/đại trà/chậm/cá biệt) và có chuỗi hành vi theo session (đa số đi G→P→S).
  - Tự chạy “smoke test” và trả kết quả ở `QA - Results`.
- File hướng dẫn chạy: `docs/research/week1_workflow.md` và mã QA nằm trong `src/tools/gas_script.js`.

**Lưu ý về chỉ số độ chính xác gán nhãn:**
- Trong tuần 1, nhóm đặt mục tiêu **>90%** cho các mẫu câu hỏi “rõ ràng” (có từ khóa/đúng cấu trúc).
- Khi vào dữ liệu thật, nếu xuất hiện các câu hỏi mơ hồ hoặc viết tắt, rule gán nhãn sẽ được tinh chỉnh dần (không ảnh hưởng đến quyền riêng tư).

---

### 2.8. Hồ sơ pháp lý + công cụ đo lường (MSLQ)
**Nhóm đã làm:**
- Chuẩn bị tài liệu nghiên cứu và pháp lý (đồng thuận tham gia, bảo mật dữ liệu).
- Dịch/chuẩn hóa thang đo MSLQ 20 items phục vụ đo các thành phần liên quan đến tự điều chỉnh học tập.
- File tham khảo: `docs/research/mslq_survey_vn.md` và `docs/research/final_proposal.md`.
- Cung cấp script tạo Form MSLQ (Pre/Post) để triển khai nhanh: `src/tools/setup_mslq_form.js` (hàm `createMslqForm()`).

---

## 3. Tiến độ thực hiện tuần 1 (tóm tắt theo ngày)
- Đầu tuần: chốt đề cương, thống nhất quy trình G.P.S/G.U.I.D.E, chuẩn hóa dữ liệu.
- Giữa tuần: viết System Prompt + soạn prompt mẫu + thiết kế Form/Sheet.
- Cuối tuần: hoàn thiện Apps Script (gán nhãn/ẩn danh/cảnh báo) + công thức Dashboard + kiểm thử nội bộ + hoàn thiện tài liệu tập huấn.

---

## 4. Việc cần phối hợp ở tuần 2 (Pilot) – giáo viên cần làm gì?
1) **Tập huấn 1 buổi ngắn (15–25 phút)**:
- Giải thích mục tiêu: dùng AI để “học cách làm”, không phải “lấy đáp án”.
- Cho học sinh thực hành 1 bài theo chuỗi **G→P→S** bằng prompt mẫu.

2) **Quy định nộp bài (khuyến nghị)**:
- Học sinh phải nộp **lời giải tự trình bày** (ảnh vở hoặc gõ), kèm 1–2 dòng “em dùng công thức gì và vì sao”.
- Nếu học sinh chỉ hỏi “giải giúp em” → nhắc quay lại bước G/P.

3) **Theo dõi Dashboard (5–10 phút/ngày)**:
- Xem các học sinh “im lặng 3 ngày” (Alerts) để can thiệp.
- Chọn 3–5 học sinh có %P cao và hài lòng thấp để hỗ trợ (can thiệp trọng điểm).

4) **Phản hồi cho nhóm dự án**:
- Ghi nhận các câu AI trả lời “chưa đúng chương trình/lệch mức độ” hoặc các câu học sinh hỏi “mơ hồ” → nhóm sẽ tinh chỉnh prompt/rule.

---

## 5. Danh mục tài liệu/artefact tuần 1 (để thầy/cô tra cứu nhanh)
- Báo cáo tiến độ tuần 1 (nội bộ): `docs/research/bao_cao_tuan_1.md`
- Playbook triển khai thực tế (Tuần 1): `docs/research/week1_real_run_playbook.md`
- Workflow QA & vận hành: `docs/research/week1_workflow.md`
- Quy chuẩn hỏi–đáp chung (để tập huấn và giả lập HS): `docs/research/gps_qna_standard.md`
- Kế hoạch kiểm thử tuần 1: `docs/research/week1_test_plan.md`
- System Prompt (GPS Tutor): `src/ai/system_prompt.md`
- Prompt mẫu Toán 11: `src/ai/sample_prompts/sample_prompts_table.md`
- Apps Script (gán nhãn/ẩn danh/cảnh báo + QA): `src/tools/gas_script.js`
- Setup Form/Sheet (1 lần): `src/tools/setup_form_and_sheet.js`
- Setup Dashboard (1 lần): `src/tools/setup_dashboard.js`
- Setup Form MSLQ (1 lần): `src/tools/setup_mslq_form.js`
- Công thức Dashboard: `src/analysis/dashboard_formulas.md` và `src/analysis/metrics.md`
- Schema log tương tác: `config/schema.json`
- Hướng dẫn gán nhãn thủ công: `docs/research/manual_labeling_guide.md`
- MSLQ tiếng Việt: `docs/research/mslq_survey_vn.md`
- Đề cương tổng: `docs/research/final_proposal.md`

---
**Trân trọng cảm ơn sự đồng hành của Quý Thầy/Cô!**

*Ngày 14 tháng 03 năm 2026*  
**Nhóm Nghiên cứu GPS-AI**
