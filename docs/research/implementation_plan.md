# Kế hoạch triển khai: Web Chat (Next.js + OpenAI) + Auto-log về `Raw Data`

Mục tiêu: thay quy trình thủ công (chat ngoài → copy/paste → Google Form) bằng **1 trang Web Chat duy nhất**, trong đó mọi lượt hỏi/đáp được tự động ghi vào Google Sheet tab `Raw Data` để Dashboard/Alerts hoạt động như cũ.

## 1) Công nghệ & Kiến trúc đã chốt

**Option B (khuyến nghị)**: Web App có backend riêng + GAS chỉ nhận log.

- **Web Chat**: Next.js (deploy Vercel hoặc local), source ở `webchat/`
- **LLM (Khuyến nghị)**: **vLLM** chạy model **Qwen2.5-Coder-7B-Instruct-AWQ** (local) để đạt hiệu năng toán học và lập trình cao nhất.
- **Dự phòng**: OpenAI API (model `gpt-4o-mini`).
- **Logging**: Google Apps Script Web App `doPost(e)` (source ở `src/tools/gas_script.js`)

Luồng:
`Browser` → `Next.js /api/chat` → `OpenAI API` → trả lời → `Next.js` POST → `GAS doPost` → append `Raw Data` → auto `Label/Hash` → Dashboard cập nhật.

## 2) Hợp đồng dữ liệu (không làm gãy Dashboard)

Hệ thống log đúng schema **A..P (16 cột)** của `Raw Data` (xem `src/tools/gas_script.js`):
- A `Timestamp` (server-set)
- B `Student ID`
- C `Class`
- D `Topic`
- E `Profile`
- F `Question`
- G `AI Response`
- H `Notes` (kèm behavior flags)
- I `Satisfaction (1-5)` - Thu thập từ UI ⭐
- J `Difficulty (1-5)` - Thu thập từ UI 🤔
- K `GPS Step (Truth)` (Dành cho gán nhãn thủ công)
- L `Auto Label` (tự sinh từ LLM Backend + Regex Fallback)
- M `Student Hash` (tự sinh SHA-256)
- N `Thinking Time` (tính toán chênh lệch giây/phút)
- O `Group` (Experimental vs Control)
- P `Message ID` (Unique ID để mapping đánh giá sau khi chat)

Sau khi append, GAS gọi lại `processSubmissionRow()` để ghi:
- Cột `L`: auto label `G/P/S/Unknown`
- Cột `M`: **SHA-256** của `SALT + student_id` (64 hex)

MVP: nếu web UI chưa thu `Satisfaction/Difficulty` thì backend gửi mặc định `3`/`3` để dashboard không bị lỗi trung bình.

## 3) Bảo mật tối thiểu cho endpoint log

- `GPS_LOG_TOKEN`: Secret lưu trong **Script Properties** của GAS.
- `GPS_STUDENT_SALT`: Secret dùng để băm ID, lưu trong **Script Properties**.
- Backend Next.js gửi `token` trong JSON body để xác thực quyền ghi log.
- Học sinh tương tác qua Webchat, Token không lộ ra phía Client (chỉ nằm ở Server-side API).

## 4) Cài đặt (Implementation)

### 4.1. GAS (Apps Script)
1) Dán/cập nhật `src/tools/gas_script.js` vào Apps Script project của Google Sheet.
2) Sửa `CONFIG`:
   - `SALT`: chuỗi bí mật
   - `LOG_TOKEN`: chuỗi bí mật
   - `SPREADSHEET_ID`: (khuyến nghị) ID của Sheet đích
3) Deploy Web App:
   - Execute as: **Me**
   - Access: **Anyone**
4) Lấy URL `/exec` → dùng làm `GAS_LOG_URL`.

### 4.2. Web Chat (Next.js)
Code: `webchat/`

Env vars (xem `webchat/.env.example`):
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional)
- `GAS_LOG_URL`
- `GAS_LOG_TOKEN`

Local:
- `cd webchat`
- `cp .env.example .env.local`
- `npm install`
- `npm run dev`

Deploy:
- Tạo Vercel project root = `webchat/`
- Thêm env vars tương ứng

## 5) Kiểm thử smoke test

1) Mở web chat, nhập `HS0001` (hoặc persona khác) và chat 3–5 lượt.
2) Mở Google Sheet tab `Raw Data`:
   - Có dòng mới cho mỗi lượt
   - Cột `L` có nhãn `G/P/S/Unknown`
   - Cột `M` có hash 64 ký tự hex
3) Mở Dashboard tabs để xác nhận công thức cập nhật.

## 6) Tài liệu liên quan

- Setup chi tiết: `docs/research/webchat_autolog_setup.md`
- Playbook tuần 1: `docs/research/week1_real_run_playbook.md`
- Phân tích nâng cao: `src/analysis/behavior_analysis.py` (Markov Chain & K-means Clustering)

## 7) Phân tích hành vi (Nâng cao cho Tuần 3+)

Hệ thống đã sẵn sàng cho phân tích chuyên sâu cho nhóm nghiên cứu:
1.  **Ma trận chuyển trạng thái (Markov Chain)**: Theo dõi xác suất học sinh đi từ G sang P, P sang S.
    - Công cụ: `src/analysis/behavior_analysis.py` hàm `calculate_markov_transitions()`.
2.  **Phân nhóm học sinh (K-means Clustering)**: Tự động phân loại học sinh thành 3 nhóm (Học sâu, Giải nhanh, Cần hỗ trợ) dựa trên:
    - Tỷ lệ %G, %P, %S.
    - Điểm trình tự (sequence score) của lộ trình G->P->S.
    - Mức độ hài lòng và độ khó trung bình thực tế từ người dùng.

## 8) Tính năng hỗ trợ học tập (Gamification & Scaffolding)
- **Widget Tiến độ**: Hiển thị số lượt G, P, S trực quan để khích lệ học sinh hoàn thành quy trình.
- **Adaptive Scaffolding**: Hệ thống tự động nhận diện Profile (Struggling/Advanced) để bẻ nhỏ bước giải hoặc cho phép tăng tốc.
