# Setup: Web Chat (Next.js + OpenAI) + Auto-log về Google Sheet `Raw Data`

Mục tiêu: học sinh chat trong 1 trang web; mỗi lượt hỏi/đáp được ghi tự động vào tab `Raw Data` để Dashboard/Alerts dùng lại như cũ.

Kế hoạch triển khai (đã chốt): `docs/research/implementation_plan.md`.

## 1) Chuẩn bị Google Sheet + Apps Script

1. Tạo/đã có Google Sheet theo playbook tuần 1 (`docs/research/week1_real_run_playbook.md`).
2. Trong Apps Script project của Sheet:
   - Dán/đồng bộ file `src/tools/gas_script.js` (phần `CONFIG` + `doPost(e)` đã có sẵn).
    - **QUAN TRỌNG**: Thiết lập biến bảo mật trong **Project Settings > Script Properties**:
      - `GPS_LOG_TOKEN`: Mật mã xác thực giữa Website và GAS.
      - `GPS_STUDENT_SALT`: Chuỗi ký tự dùng để băm ẩn danh danh tính học sinh.
    - Sửa `CONFIG` trong code GAS (nếu cần đổi tên Sheet hoặc cột).
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
   - Nếu dùng **vLLM** (Khuyến nghị): `LLM_PROVIDER=vllm`, `OPENAI_API_KEY=dummy`, `OPENAI_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct-AWQ`, `OPENAI_BASE_URL=http://localhost:8001/v1`
   - Nếu dùng OpenAI public chính thức: `LLM_PROVIDER=openai`, điền API Key thực tế.
   - Nếu dùng Ollama: `LLM_PROVIDER=ollama`.
   - `GAS_LOG_URL`, `GAS_LOG_TOKEN`, `GAS_LOG_TIMEOUT_MS`
4. `npm install`
5. `npm run dev`

Nếu chat bị treo ở “Đang trả lời…” khi dùng Ollama/vLLM:
- Mở `http://localhost:3000/api/health` để xem trạng thái provider.
- **Dành cho vLLM**: Bạn có thể chạy server bằng lệnh:
  ```bash
  VLLM_USE_V1=0 \
  python -m vllm.entrypoints.openai.api_server \
    --model "/media/chinh303/New Volume1/ai_models/huggingface/hub/models--Qwen--Qwen2.5-Coder-7B-Instruct-AWQ/snapshots/8e8ed243bbe6f9a5aff549a0924562fc719b2b8a" \
    --port 8001 \
    --trust-remote-code \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.85 \
    --quantization awq \
    --dtype half \
    --enforce-eager \
    --tool-call-parser hermes \
    --enable-auto-tool-choice
  ```

### Deploy Vercel
1. Tạo project mới trên Vercel
2. Root Directory: `webchat/`
3. Add Environment Variables giống `.env.example`
4. Deploy

`doPost(e)` sẽ append một dòng gồm **16 cột (A..P)**:
- A `Timestamp`
- B `Student ID`, C `Class`, D `Topic`, E `Profile`, F `Question`, G `AI Response`
- H `Notes` (chứa các hành vi như *looping*, *skipping*, *scaffolding*)
- I `Satisfaction`, J `Difficulty` (1-5 sao từ UI)
- K `Truth` (dành cho GV gán nhãn thủ công)
- L `Auto Label` (G/P/S), M `Student Hash` (64 hex)
- N `Thinking Time` (Phút), O `Group` (Nhóm), P `Message ID`

---
> [!TIP]
> **Khám phá thêm**: Đọc `docs/research/GPS_Framework_Guide.md` để hiểu sâu về quy trình sư phạm đã được lập trình sẵn trong Prompt.
