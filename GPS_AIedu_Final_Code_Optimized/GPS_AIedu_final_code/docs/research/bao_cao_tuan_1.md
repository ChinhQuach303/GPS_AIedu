# BÁO CÁO TIẾN ĐỘ TUẦN 1 (tập trung quy trình)
**Dự án: GPS AIedu – Thu thập nhật ký học sinh khi học với AI**

---

## 1) Mục tiêu tuần 1
Chốt được luồng chạy “một link chat → tự ghi dữ liệu → dashboard theo dõi”, để khi vào lớp thật giáo viên chỉ cần phát link và theo dõi Sheet/Dashboard.

## 2) Quy trình vận hành hiện tại (end-to-end)
1. **Google Sheet** là kho dữ liệu trung tâm (tab `Raw Data`).
2. **Google Apps Script (GAS) dạng Web App** nhận log qua webhook `doPost(e)` và ghi vào `Raw Data`.
3. **Tự động xử lý ngay khi ghi**:
   - Gán nhãn lượt hỏi `G/P/S/Unknown` vào cột `L`.
   - Tạo hash ẩn danh theo `Student ID` vào cột `M` (SHA-256, 64 ký tự hex).
4. **Webchat (Next.js)** là UI cho học sinh:
   - Chat với LLM theo cấu hình `LLM_PROVIDER` (`openai` hoặc `ollama`).
   - Sau mỗi lượt chat, tự POST log về `GAS_LOG_URL` (không cần copy/paste sang Form).
5. **Dashboard/Alerts** đọc từ `Raw Data` để theo dõi tiến độ và phát hiện hành vi (đi nhanh, lặp P, offtrack, inactive…).

Ghi chú triển khai:
- `src/tools/gas_script.js` có menu/hàm `initRawDataSchema()` để tạo/chuẩn hóa header cho tab `Raw Data` trước khi chạy thật.
- Webchat có endpoint kiểm tra nhanh tình trạng hệ thống (`/api/health`) để xử lý tình huống chat “đang trả lời…” nhưng không ra nội dung (thường do provider/timeout).

## 3) Tự thử nghiệm khi CHƯA có lớp thật (giả lập dữ liệu)
Đã chuẩn hóa bộ persona để tạo dữ liệu “giống thật” trước khi vào lớp:
- `HS0001` Advanced/Fast: đi nhanh (P ít hoặc S sớm), tự giải phần lớn.
- `HS0002` Typical/Normal: đa số đi đúng GPS.
- `HS0003` Struggling/Slow: G nhiều, P lặp (GPP), đôi khi không lên S.
- `HS0004` Offtrack: hay xin đáp án/giải giúp, lệch quy trình.
- `HS0005` Inactive: làm 1 ngày rồi dừng (để test cảnh báo).

Bộ câu hỏi copy/paste theo persona (24 lượt/persona) để test trực tiếp trên Webchat:
- `docs/research/week1_persona_question_scripts.md`

Playbook vận hành “real run” tuần 1 (bao gồm Bước 4A/4B):
- `docs/research/week1_real_run_playbook.md`

## 4) Đầu ra đã bàn giao trong repo (tuần 1)
- Webchat + auto-log: `webchat/`
- GAS nhận log + gán nhãn/hash: `src/tools/gas_script.js`
- Hướng dẫn cài đặt nhanh: `docs/research/webchat_autolog_setup.md`
- Kế hoạch triển khai đã chốt: `docs/research/implementation_plan.md`
- Bộ kịch bản persona để tạo dữ liệu: `docs/research/week1_persona_question_scripts.md`

## 5) Rủi ro/điểm cần chú ý (để chủ động tuần 2)
- Nếu dùng API cloud (OpenAI/OpenAI-compatible) có thể gặp quota/billing/rate-limit; phương án ổn định khi pilot là chạy **Ollama local** (`LLM_PROVIDER=ollama`) với model nhỏ.
- Khi test “giả lập”, sau mỗi submit cần kiểm tra ngay trên `Raw Data`: cột `L` có nhãn và cột `M` có hash 64 ký tự hex (để chắc pipeline hoạt động).

## 6) Kế hoạch tuần 2 (pilot lớp thật)
- Tập huấn học sinh 20–30 phút theo GPS (không xin đáp án; đi đúng G→P→S).
- Chạy lớp thật, theo dõi Dashboard/Alerts hằng ngày, tinh chỉnh prompt mẫu + quy tắc cảnh báo dựa trên dữ liệu thực.

---
*Ngày cập nhật: 14/03/2026*  
*Người thực hiện: Nhóm GPS-AI*
