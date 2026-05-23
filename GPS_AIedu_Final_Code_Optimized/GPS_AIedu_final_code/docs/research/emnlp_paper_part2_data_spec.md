# GPS-Agent Research Paper: Part 2 - Data Specification & Augmentation

Tài liệu này trình bày chi tiết về quy trình xây dựng, mở rộng và chuẩn hóa dữ liệu cho nghiên cứu.

---

## 1. Initial Dataset: The Pilot Phase (Dữ liệu nền tảng)

Dữ liệu ban đầu được xây dựng dựa trên sự tương tác thực tế giữa hệ thống và 5 nguyên mẫu học sinh (Personas), đại diện cho các mức độ tiếp thu và thái độ học tập khác nhau:

### 1.1. Các nhóm Persona (Archetypes)
*   **Học sinh Giỏi**: Tự chủ cao, chỉ cần gợi ý chiến lược [G], Math Density lớn.
*   **Học sinh Khá**: Theo sát quy trình [P], ít mắc lỗi logic nhưng cần AI xác nhận.
*   **Học sinh Trung bình**: Cần chia nhỏ bài toán thành nhiều bước [P], hay hỏi "Tại sao?".
*   **Học sinh Yếu**: Bế tắc ngay từ bước [G], thường xuyên tính toán sai cơ bản.
*   **Học sinh Lười (Disengaged)**: Trả lời ngắn, hay yêu cầu AI đưa đáp án ngay, ít tham gia vào quá trình tính toán.

### 1.2. Nội dung kiến thức
*   **Chủ đề**: Xác suất và Tổ hợp (Xác suất cổ điển, Quy tắc cộng/nhân, Chỉnh hợp/Tổ hợp).
*   **Quy mô**: 45 câu hỏi (Q1-Q45) được thiết kế từ mức độ Nhận biết đến Vận dụng cao.
*   **Kết quả**: Tệp `simulated_conversations.csv` ghi lại các hội thoại đa lượt (Multi-turn) được gán nhãn thủ công theo cấu trúc G-P-S.

---

## 2. Data Augmentation: Scaling the Research (Mở rộng quy mô)

Để đảm bảo tính khách quan và độ tin cậy thống kê (Statistical significance), chúng tôi thực hiện quy trình **Behavioral Data Augmentation** bằng cách sử dụng "LLM-as-a-Student".

### 2.1. Thiết kế Thí nghiệm Đối chứng (A/B Testing Setup)
Dữ liệu được mở rộng thành 2 nhóm song song:
1.  **Nhóm Thực nghiệm (GPS Group)**: Học sinh tương tác với hệ thống Multi-Agent LangGraph (Supervisor điều phối Guide-Practice-Solve).
2.  **Nhóm Đối chứng (Non-GPS Group)**: Học sinh tương tác với một hệ thống Single-Agent (Chatbot truyền thống), không có cơ chế điều soát sư phạm và thường đưa ra đáp án trực tiếp.

### 2.2. Quy trình Augmentation
*   **Công cụ**: `scripts/generate_authentic_dataset.py`.
*   **Mô phỏng**: 
    - Mỗi câu hỏi trong bộ 45 câu được gán cho các cấp độ học sinh khác nhau.
    - Hệ thống mô phỏng tối đa **8 lượt trao đổi (turns)** cho mỗi phiên.
    - Sử dụng `StudentSimulatorV2` để duy trì tính nhất quán của Persona trong suốt phiên.
*   **Quy mô**: Tổng cộng **2,824 phiên hội thoại** (sessions) đã được sinh ra và đưa vào tập dữ liệu Gold Standard.

---

## 3. Data Processing & Quality Gate (Xử lý & Kiểm soát chất lượng)

Để dữ liệu đạt chuẩn nộp EMNLP, chúng tôi áp dụng các lớp lọc nghiêm ngặt:

1.  **Language Cleaning**: Loại bỏ hoàn toàn "Language Leakage" (ký tự tiếng Trung hoặc các đoạn text không phải tiếng Việt).
2.  **Response Validation**: Lọc bỏ các phiên có câu trả lời của học sinh quá ngắn (vô nghĩa) hoặc AI bị lặp (silent loops).
3.  **Gold Standard Alignment**: Ánh xạ dữ liệu Augment về cùng định dạng với dữ liệu Pilot để thực hiện phân tích so sánh chéo.

---

## 4. Đặc trưng dữ liệu (Dataset Features)

Mỗi phiên hội thoại trong tập dữ liệu cuối cùng bao gồm các đặc trưng:
- **Metadata**: Student ID, QID, Level, Group (GPS/Non-GPS).
- **Process Labels**: Trace của các bước (ví dụ: `G-P1-P2-S`).
- **Pedagogical Metrics**: Independence Index, Math Density, Hake's Gain, Latency.

---

Phần này sẽ là minh chứng cho tính "Scalability" và "Authenticity" của nghiên cứu. Bạn có muốn tôi bổ sung thêm thông tin về cách chúng ta xử lý nhóm **"Học sinh Lười"** trong quá trình Augmentation để làm nổi bật khả năng xử lý của GPS-Agent không?
