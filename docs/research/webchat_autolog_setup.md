# Setup: Web Chat (Next.js + OpenAI) + Auto-log về Google Sheet `Raw Data`

Mục tiêu: học sinh chat trong 1 trang web; mỗi lượt hỏi/đáp được ghi tự động vào tab `Raw Data` để Dashboard/Alerts dùng lại như cũ.

Kế hoạch triển khai (đã chốt): `docs/research/implementation_plan.md`.

## 1) Chuẩn bị Google Sheet + Apps Script

1. Tạo/đã có Google Sheet theo playbook tuần 1 (`docs/research/week1_real_run_playbook.md`).
2. Trong Apps Script project của Sheet:
   - Dán/đồng bộ file `src/tools/gas_script.js` (phần `CONFIG` + `doPost(e)` đã có sẵn).
   - Sửa `CONFIG`:
     - `SALT`: chuỗi bí mật (không chia sẻ)
     - `LOG_TOKEN`: chuỗi bí mật (backend dùng để log)
     - `SPREADSHEET_ID`: (khuyến nghị) điền ID của Sheet đích
3. Deploy Web App:
   - Deploy → New deployment → Type: Web app
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Copy URL dạng `https://script.google.com/macros/s/.../exec` → đây là `GAS_LOG_URL`.

Kiểm tra nhanh: gọi POST từ Postman/curl (body JSON có `token`) và xem tab `Raw Data` có thêm dòng, cột `L/M` tự điền.

## 2) Chạy Web Chat (local hoặc deploy)

Code web chat nằm ở `webchat/`.

### Local
1. `cd webchat`
2. `cp .env.example .env.local`
3. Điền:
   - Nếu dùng OpenAI-compatible: `LLM_PROVIDER=openai`, điền `OPENAI_API_KEY`, `OPENAI_MODEL` và (tuỳ chọn) `OPENAI_BASE_URL`
   - Nếu muốn miễn phí: chuyển sang Ollama local `LLM_PROVIDER=ollama`, điền `OLLAMA_MODEL` (gợi ý: `qwen2-math:1.5b-instruct-q5_K_M`)
   - `GAS_LOG_URL`, `GAS_LOG_TOKEN`
4. `npm install`
5. `npm run dev`

Nếu chat bị treo ở “Đang trả lời…” khi dùng Ollama:
- Mở `http://localhost:3000/api/health` để xem `ollama.ok` có `true` không.
- Nếu `ollama.ok=false`: mở Ollama app hoặc chạy `ollama serve`, rồi thử lại.

### Deploy Vercel
1. Tạo project mới trên Vercel
2. Root Directory: `webchat/`
3. Add Environment Variables giống `.env.example`
4. Deploy

## 3) Những cột được log (giữ đúng schema A..M)

`doPost(e)` sẽ append một dòng gồm:
- A Timestamp (server time)
- B..K: theo payload
- L Auto Label, M Hash: được tính lại bằng `processSubmissionRow()`

MVP mặc định:
- `Satisfaction` và `Difficulty` sẽ log giá trị `3` nếu không gửi.
