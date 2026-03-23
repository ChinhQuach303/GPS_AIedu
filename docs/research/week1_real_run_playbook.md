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

## Bước 1 – Thiết lập CSDL và Webhook log (Chạy 1 lần, ~5 phút)

Hệ thống ghi log vào Google Sheets tự động cần một Endpoint (Webhook) được cấu hình chuẩn qua Google Apps Script. 

### 1.1 Tạo Nền tảng Google Sheet
1. Mở Google Drive cá nhân, tạo một file Google Sheet mới (Đặt tên: **`GPS_AIedu_Data`**).
2. Xóa hết các tab cũ đi, tạo một tab duy nhất mang tên đúng chuẩn: **`Raw Data`**.
3. Trên thanh công cụ, nhấn vào **Extensions (Tiện ích mở rộng)** -> chọn **Apps Script**.

### 1.2 Dán Mã Nguồn
1. Trong màn hình Apps Script vừa mở, bạn sẽ thấy file mặc định là `Code.gs`.
2. Truy cập vào bộ code trên máy của bạn tại tệp: `src/tools/gas_script.js`.
3. Nhấn `Ctrl + A` copy toàn bộ mã nguồn của file đó.
4. Xóa chữ `function myFunction() {...}` có sẵn trong `Code.gs` và dán toàn bộ đoạn code vừa copy vào. Sau đó, bấm tổ hợp `Ctrl + S` để lưu (hoặc hình đĩa mềm trên thanh công cụ).

### 1.3 Cấu hình Bảo mật (Script Properties) - Cực kì quan trọng
Bạn bắt buộc phải thực hiện bước này để hệ thống có mật mã bảo vệ và băm danh tính học sinh.
1. Nhìn sang Tùy chọn Menu phía bên tay trái màn hình Apps Script, nhấn vào biểu tượng **bánh răng ⚙️ (Project Settings / Cài đặt dự án)**.
2. Kéo xuống dưới cùng tìm mục **Script Properties (Thuộc tính tập lệnh)**.
3. Nhấn vào nút **Add script property (Thêm tập lệnh)** 2 lần để tạo 2 hàng mới:
   * **Hàng thứ nhất:**
     * *Property (Thuộc tính):* `GPS_LOG_TOKEN`
     * *Value (Giá trị):* Nhập một mật khẩu tự tạo bất kỳ (Ví dụ: `mat-khau-webchat-gps-123`)
   * **Hàng thứ hai:**
     * *Property:* `GPS_STUDENT_SALT`
     * *Value:* Nhập một mã băm bí mật tự tạo (Ví dụ: `chuoi-bam-danh-tinh-gps-456`)
4. Bấm **Save script properties (Lưu)**.

### 1.4 Khởi tạo 16 Cột trên Giao diện Trang tính
1. Trở lại tab biên tập code (`<> Editor`) ở menu trái.
2. Ở thanh công cụ trên cùng (cạnh nút Run), có một hộp thả xuống tên chức năng đang hiện `doPost` hoặc `checkInactivity`. Hãy bấm vào hộp này -> **Tìm và chọn dòng `initRawDataSchema`**.
3. Nhấn nút **Run (Chạy) ▶**. Lần đầu chạy Google sẽ yêu cầu "Review permissions", hãy nhấn *Cho phép -> Chọn Tài khoản -> Advanced -> Đi tới Project (unsafe)*.
4. Trở lại trang Google Sheet ban đầu, bạn sẽ thấy nó vừa tự động tạo 16 cột (A đến P) làm tiêu đề in đậm.

### 1.5 Phát hành Web App để lấy Link nối với Website
1. Vẫn ở màn hình Apps Script, góc trên bên phải, bấm nút xanh **Deploy** -> chọn **New deployment**.
2. Phía bên trái bảng điều khiển mới, nhấp vào **bánh răng (Select type)** -> Đánh dấu vào hộp **Web app**.
3. Tại ô điền thông tin:
   * **Description:** API cho dự án GPS
   * **Execute as:** `Me` (Tài khoản của bạn)
   * **Who has access:** `Anyone` (Bất kỳ ai)
4. Bấm **Deploy**.
5. Đợi 1 lúc, hộp thông báo sẽ sinh ra một URL rất dài nằm dưới phần **Web app**. Bấm nút "Copy" nó lại. 
   *(Đây chính là biến `GAS_LOG_URL` để bạn kết nối với webchat trong Bước 2)*.
---
AKfycbyngEQdvo_AxMDpRYKUPy67y8vgHpk0nq9z122CDTgEn2CsZHvjgPQa98pCToWnCsLg
https://script.google.com/macros/s/AKfycbyngEQdvo_AxMDpRYKUPy67y8vgHpk0nq9z122CDTgEn2CsZHvjgPQa98pCToWnCsLg/exec

## Bước 2 – Tải Model và Khởi chạy Hệ thống Local (Next.js + vLLM)

Vì bạn đang sử dụng môi trường GPU nội bộ (NVIDIA RTX 3060 12GB), chúng ta sẽ chạy model **Qwen2.5-Math-7B-Instruct** thông qua server **vLLM** ở định dạng nén **AWQ** để tránh lỗi tràn RAM (OOM).

### 2.1. Tải Model AWQ về máy dự phòng
Mở terminal và kích hoạt môi trường ảo đang cài `vllm_env`. Chạy lệnh để tải model về đúng thư mục ổ đĩa của bạn:
```bash
/home/chinh303/vllm_env/bin/huggingface-cli download \
  adriszmar/Qwen2.5-Math-7B-Instruct-AWQ \
  --local-dir "/media/chinh303/New Volume1/ai_models/Qwen2.5-Math-7B-Instruct-AWQ" \
  --local-dir-use-symlinks False
```

### 2.2. Khởi động AI Server (vLLM)
Khi tải xong, chạy lệnh sau để bật Server suy luận của AI:
```bash
VLLM_USE_V1=0 \
/home/chinh303/vllm_env/bin/python -m vllm.entrypoints.openai.api_server \
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
*Lưu ý: Bạn để treo màn hình Terminal này. Khi nào báo chữ `Uvicorn running on http://0.0.0.0:8001` tức là Server đã sẵn sàng!*

### 2.3. Cấu hình Frontend (Webchat)
Mở một Terminal thứ 2, đi vào thư mục webchat:
```bash
cd /home/chinh303/code/aiedu/webchat
cp .env.example .env.local
```
Mở tệp `.env.local` và đảm bảo cấu hình như sau (để Frontend gọi đúng tới localhost:8000):
```env
LLM_PROVIDER=vllm
OPENAI_API_KEY=vllm-token-dummy
OPENAI_MODEL=Qwen2.5-Coder-7B-Instruct-AWQ
OPENAI_BASE_URL=http://localhost:8001/v1
GAS_LOG_URL=https://script.google.com/.../exec    <-- (Dán link Web App của bạn ở bước 1)
GAS_LOG_TOKEN=CHUOI_BI_MAT_CUA_BAN                <-- (Dán chuỗi đã cấu hình trong Script Properties)
```

### 2.4. Chạy Giao diện người dùng
Tại chính Terminal thứ 2 này, tiến hành chạy web:
```bash
npm install
npm run dev
```
Truy cập `http://localhost:3000` để kiểm tra chat. Khi chat, dữ liệu sẽ tự động đồng bộ thời gian thực về tab `Raw Data` trên Google Sheet.

---

## Bước 3 – Tạo bảng khảo sát động lực học tập (Form MSLQ) (Chạy 1 lần, ~2 phút)

Để đo lường hiệu quả trước và sau khi dùng AI, chúng ta thiết lập tự động Form khảo sát MSLQ.

1. Tại màn hình **Apps Script**, nhìn sang bên trái chỗ danh sách file (Files), nhấn vào dấu cộng **(+)** -> Chọn **Script (Tập lệnh)**.
2. Đặt tên file mới là: **`SetupMSLQ`** (không cần gõ đuôi .gs).
3. Mở file `src/tools/setup_mslq_form.js` nằm trong thư mục code dự án trên máy tính của bạn, nhấn `Ctrl + A` để copy toàn bộ nội dung trong đó.
4. Trở lại tab Apps Script trên trình duyệt, dán toàn bộ đoạn code vừa copy đè lên file `SetupMSLQ.gs`. Ấn biểu tượng đĩa mềm (`Ctrl + S`) để lưu.
5. Ở thanh chức năng thả xuống phía trên cùng, chọn tên hàm là `createMslqForm`.
6. Nhấn nút Run **(Chạy) ▶**. (Nếu hỏi quyền truy cập, hãy nhấn Allow).
7. Khi lệnh chạy hoàn tất, hãy nhìn vào cửa sổ **Execution log (Nhật ký thực thi)** phía dưới màn hình, bạn sẽ thấy 2 dòng chứa: `Edit URL` (Link để bạn sửa form) và `Published URL` (Link để gửi cho học sinh làm). Hãy Copy link để gửi cho học sinh.

---

## Bước 4 – Khởi tạo Dashboard Quản lý lớp học (Chạy 1 lần, ~3 phút)

Đây là chức năng quan trọng nhất cho giáo viên để theo dõi tiến độ của học sinh.

1. Tương tự Bước 3, trong màn hình Apps Script, nhấn dấu cộng **(+)** tạo file Script mới. Đặt tên là **`SetupDashboard`**.
2. Mở file `src/tools/setup_dashboard.js` từ mã nguồn trên máy của bạn và copy toàn bộ nội dung.
3. Dán đè lên file tab `SetupDashboard.gs` trên trình duyệt và nhấn Lưu (`Ctrl + S`).
4. Ở thanh chức năng thả xuống phía trên cùng, chọn tên hàm `setupDashboard`.
5. Nhấn nút Run **(Chạy) ▶**.
6. **Mở lại Google Sheet (GPS_AIedu_Data)**, bạn sẽ thấy cực kì bất ngờ khi hệ thống tự động sinh ra thêm 3 tab mới với đầy đủ giao diện màu sắc rực rỡ và công thức nhảy tự động:
   * **`Dashboard - Per Student`**: Dùng để tra cứu chi tiết 1 học sinh cụ thể (Xem tỷ lệ G/P/S của em đó).
   * **`Dashboard - GPS Tracker`**: Dùng để theo dõi mức độ tương tác tổng thể của toàn lớp (Có biểu đồ).
   * **`Dashboard - Alerts`**: Cảnh báo tức thời (Màu đỏ) những học sinh đang cần giáo viên can thiệp.

---

## Bước 5 – Tự đóng vai học sinh để kiểm thử (Giả lập Dữ liệu)

Chỉ khi có dữ liệu thật, Dashboard mới hiển thị đẹp và chính xác. Trước khi gửi cho học sinh, bạn hãy tự đóng vai 5 kiểu học sinh để kiểm tra hệ thống.

### 5.1. Nhận diện 5 kiểu học sinh (Personas)
Trong hệ thống, chúng ta phân loại 5 kiểu tính cách mẫu:
* **`HS0001` (Advanced)**: Thông minh, đi tắt các bước, tự giải.
* **`HS0002` (Typical)**: Hoc sinh bình thường, làm ngoan ngoãn đúng quy trình **Guide → Practice → Solve**.
* **`HS0003` (Struggling)**: Chậm hiểu, hỏi lại các bước G rất nhiều, loay hoay mãi ở bước P.
* **`HS0004` (Offtrack)**: Lên mạng chỉ để vòi AI đưa đáp án để chép.
* **`HS0005` (Inactive)**: Chỉ nhắn 1 - 2 tin rồi bỏ 2 ngày không làm bài.

### 5.2. Cách giả lập tương tác
1. Đảm bảo bạn đang bật vLLM Server và Frontend như đã hướng dẫn ở **Bước 2**.
2. Mở trình duyệt Web truy cập `http://localhost:3000`.
3. Giao diện hiện ra, tại ô **Student ID**, nhập mã `HS0001`. Mục **Class** (Lớp) bạn gõ `11A1`. Mục **Topic** (Chủ đề) gõ `Toán xác suất`. 
4. Bấm **Bắt đầu**.
5. Mở file `docs/research/week1_persona_question_scripts.md` trong mã nguồn. Tại đây tôi đã soạn sẵn kịch bản 24 dòng tin nhắn mẫu cho từng Persona. 
6. Chỉ việc copy từng dòng tin nhắn đó, dán vào Webchat, và chờ AI (Qwen2.5-Math) suy nghĩ và trả lời.
   *(Nhớ đánh giá số Sao ⭐ và độ khó 🤔 sau mỗi câu trả lời của AI nhé)*.

### 5.3. Kiểm tra phép màu tự động
Sau khi nhắn xong vài câu, hãy lập tức mở màn hình **Google Sheet** (Tab `Raw Data`). 
Bạn sẽ thấy điều kỳ diệu:
* Dữ liệu tự động nhảy vào Sheet theo thời gian thực như có ma thuật.
* Cột `Auto Label` tự động được AI gắn nhãn xem học sinh kia đang ở bước [G], [P] hay [S].
* Cột `Student Hash` băm ID `HS0001` thành 1 chuỗi ký tự khó hiểu (Ẩn danh học sinh tuyệt đối).
* Cột `Thinking Time` tự động tính thời gian phản hồi giữa bạn và AI.

Qua tab **`Dashboard - Alerts`**, bạn thậm chí sẽ thấy `HS0004` bị bôi đỏ cảnh báo giáo viên vì có dấu hiệu chép phạt (vòi đáp án)!
