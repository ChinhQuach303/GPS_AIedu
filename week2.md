# HƯỚNG DẪN CHI TIẾT TUẦN 2: Triển khai Pilot và Thu thập dữ liệu thực tế

## MỤC TIÊU TUẦN 2
Chuyển từ môi trường giả lập sang triển khai thực tế trên lớp học (Pilot). Tập trung vào việc huấn luyện học sinh dùng đúng quy trình G.P.S, theo dõi dữ liệu thời gian thực và tinh chỉnh hệ thống dựa trên phản hồi thực tế.

Kết thúc tuần 2, nhóm nghiên cứu cần có:
1. **Dữ liệu thực tế**: Ít nhất 100-200 lượt log từ học sinh thật.
2. **Dashboard cập nhật**: Biểu đồ phân bố G/P/S và chỉ số hài lòng của lớp Pilot.
3. **Kết quả khảo sát đầu kỳ**: Hoàn thành Form MSLQ (Pre-test) cho toàn bộ học sinh Pilot.
4. **System Prompt v1.1**: Bản cập nhật dựa trên các tình huống học sinh "bẻ lái" hoặc AI trả lời chưa khớp.
5. **Báo cáo sơ bộ Tuần 2**: Nhận diện các nhóm hành vi (Fast, Slow, Offtrack) trong lớp thật.

---

## DANH SÁCH CÔNG VIỆC CHI TIẾT

### 2.1. Tập huấn học sinh và Khảo sát đầu kỳ (Pre-test)
- **Mô tả**: Tổ chức 20-30 phút giới thiệu mô hình G.P.S. Hướng dẫn học sinh cách truy cập Webchat và nộp khảo sát MSLQ đầu khóa.
- **Quan trọng**: Phân chia ngẫu nhiên học sinh vào 2 nhóm (Experimental vs Control) để chuẩn bị cho việc chứng minh hiệu quả sau này.
- **Kết quả**: Danh sách học sinh đã làm Pre-test; học sinh nắm vững quy trình G -> P -> S.

### 2.2. Triển khai Pilot hằng ngày (Real Run)
- **Mô tả**: Học sinh sử dụng Webchat thực hiện bài tập Toán 11 (Tổ hợp & Xác suất) ít nhất 2 buổi/tuần.
- **Kết quả**: Dữ liệu đổ về tab `Raw Data` trong Google Sheets ổn định.

### 2.3. Theo dõi Dashboard & Can thiệp (G.U.I.D.E)
- **Mô tả**: Giáo viên/Nhóm dự án kiểm tra Dashboard hằng ngày (Understand). 
    - Nhận diện các học sinh bị kẹt ở bước P quá lâu.
    - Phát hiện học sinh "xin đáp án" (Offtrack) để nhắc nhở trực tiếp (Intervene).
- **Kết quả**: Nhật ký can thiệp (Intervention Log) sơ bộ.

### 2.4. Tinh chỉnh Prompt và Quy tắc gán nhãn
- **Mô tả**: Rà soát các câu hỏi AI trả lời chưa đúng tinh thần G.P.S hoặc các lượt hỏi học sinh dùng tiếng lóng khiến hệ thống không gán được nhãn (Unknown).
- **Kết quả**: Cập nhật `system_prompt.md` và các quy tắc Regex trong `gas_script.js`.

### 2.5. Kiểm tra tính ổn định của hạ tầng
- **Mô tả**: Kiểm tra lỗi timeout, quota API (nếu dùng OpenAI) hoặc hiệu năng máy trạm (nếu dùng Ollama local) khi có nhiều học sinh truy cập cùng lúc.
- **Kết quả**: Log lỗi (nếu có) và phương án khắc phục cho tuần 3.

---

## TIẾN ĐỘ GỢI Ý (MẪU)

- **Thứ 2**: 
    - Gửi Link khảo sát MSLQ (Pre-test) cho học sinh.
    - Kiểm tra lần cuối link Webchat và GAS URL.
- **Thứ 3**: 
    - Buổi Pilot 1: Tập huấn nhanh + Cho học sinh giải 2 bài tập theo chuỗi G-P-S.
    - Cuối ngày: Kiểm tra Dashboard xem dữ liệu có đổ về mặt đầy đủ không.
- **Thứ 4**: 
    - Rà soát log `Unknown` để cập nhật quy tắc gán nhãn tự động.
    - Họp rút kinh nghiệm buổi Pilot đầu tiên.
- **Thứ 5**: 
    - Buổi Pilot 2: Học sinh tự học có sự giám sát của giáo viên.
    - Giáo viên thực hiện can thiệp (Intervene) với nhóm học sinh có chỉ số hài lòng thấp.
- **Thứ 6**: 
    - Tổng hợp dữ liệu từ Dashboard.
    - Chốt phiên bản System Prompt v1.1 (fix các lỗi "giải hộ" nếu có).
- **Thứ 7**: 
    - Viết báo cáo tuần 2.
    - Chuẩn bị nội dung cho tuần 3 (mở rộng chủ đề hoặc tăng độ khó bài tập).
- **Chủ nhật**: Nghỉ ngơi & Lên kế hoạch chi tiết cho tuần tiếp theo.

---

## CÔNG CỤ SỬ DỤNG
- **Webchat**: `https://your-pilot-link.vercel.app`
- **Dashboard**: Link Google Sheet (tab `Alerts` và `GPS Tracker`).
- **Feedback**: Nhóm Zalo/Messenger hỗ trợ kỹ thuật nhanh cho giáo viên.

## TÓM TẮT CODE TUẦN 2

- Giao diện Webchat lưu session/message vào `localStorage`, hiển thị thanh tiến độ [G/P/S] và bật các nút đánh giá chỉ sau khi bài toán được trả lời; luồng gửi/nhận cũng bảo đảm trạng thái `busy` để tránh gửi chồng (xem `webchat/app/page.tsx:38`, `webchat/app/page.tsx:141`, `webchat/app/page.tsx:168`).
- API `/api/chat` kiểm tra payload, phán đoán hành vi, áp prompt phù hợp rồi trả về stream kèm header `x-message-id` để front-end và GAS log theo dõi, đồng thời ghi log bất kể sử dụng stream hay đơn lẻ (xem `webchat/app/api/chat/route.ts:12`, `webchat/app/api/chat/route.ts:29`, `webchat/app/api/chat/route.ts:41`, `webchat/app/api/chat/route.ts:53`).
- `webchat/lib/gasLog.ts` gọi `classifyGpsStepLLM` và `detectBehaviorSignals` để nhồi nhét tag vào payload trước khi gọi Apps Script, còn `src/tools/gas_script.js` kiểm tra token, dedup, tự gắn nhãn, băm ID và cảnh báo Telegram khi cần (xem `webchat/lib/gasLog.ts:6`, `src/tools/gas_script.js:73`, `src/tools/gas_script.js:80`, `src/tools/gas_script.js:143`).
- Stack prompt/behavior được neo vào `webchat/prompts/system_prompt.md` và `webchat/lib/systemPrompt.ts`/`webchat/lib/behavior.ts` để điều chỉnh nhắc nhở theo profile, nhóm nghiên cứu và cờ skip/looping (xem `webchat/prompts/system_prompt.md:1`, `webchat/lib/systemPrompt.ts:7`, `webchat/lib/behavior.ts:16`).
- Quy trình Option B (Next.js + GAS) và bước triển khai Apps Script đã được ghi lại để đảm bảo mọi thành phần tự động cùng chạy (xem `docs/research/implementation_plan.md:7`, `docs/research/webchat_autolog_setup.md:7`).
