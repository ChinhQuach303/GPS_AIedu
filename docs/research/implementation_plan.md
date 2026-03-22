# Kế hoạch triển khai: Web Chat (Next.js + OpenAI) + Auto-log về `Raw Data`

Mục tiêu: thay quy trình thủ công (chat ngoài → copy/paste → Google Form) bằng **1 trang Web Chat duy nhất**, trong đó mọi lượt hỏi/đáp được tự động ghi vào Google Sheet tab `Raw Data` để Dashboard/Alerts hoạt động như cũ.

## 1) Công nghệ & Kiến trúc đã chốt

**Option B (khuyến nghị)**: Web App có backend riêng + GAS chỉ nhận log.

- **Web Chat**: Next.js (deploy Vercel), source ở `webchat/`
- **LLM**: OpenAI API (model mặc định `gpt-4o-mini`, cấu hình bằng env)
- **Logging**: Google Apps Script Web App `doPost(e)` (source ở `src/tools/gas_script.js`)

Luồng:
`Browser` → `Next.js /api/chat` → `OpenAI API` → trả lời → `Next.js` POST → `GAS doPost` → append `Raw Data` → auto `Label/Hash` → Dashboard cập nhật.

## 2) Hợp đồng dữ liệu (không làm gãy Dashboard)

Hệ thống log đúng schema **A..M (13 cột)** của `Raw Data` (xem `src/tools/setup_form_and_sheet.js`):
- A `Timestamp` (server-set)
- B `Student ID`
- C `Class`
- D `Topic`
- E `Profile`
- F `Question`
- G `AI Response`
- H `Notes`
- I `Satisfaction (1-5)`
- J `Difficulty (1-5)`
- K `GPS Step (Truth)`
- L `Auto Label` (tự sinh)
- M `Student Hash` (tự sinh)

Sau khi append, GAS gọi lại `processSubmissionRow()` để ghi:
- Cột `L`: auto label `G/P/S/Unknown`
- Cột `M`: **SHA-256** của `SALT + student_id` (64 hex)

MVP: nếu web UI chưa thu `Satisfaction/Difficulty` thì backend gửi mặc định `3`/`3` để dashboard không bị lỗi trung bình.

## 3) Bảo mật tối thiểu cho endpoint log

- `LOG_TOKEN`: secret lưu trong `src/tools/gas_script.js` (`CONFIG.LOG_TOKEN`)
- Backend Next.js gửi `token` trong JSON body (Apps Script Web App không đọc header ổn định)
- Học sinh chỉ gọi `/api/chat` (không gọi trực tiếp GAS), nên token không lộ ra client

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
    - Mức độ hài lòng và độ khó trung bình.
