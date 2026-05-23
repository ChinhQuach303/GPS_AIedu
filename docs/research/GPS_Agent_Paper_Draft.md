# [DRAFT] GPS-Agent: A Multi-Agent Scaffolding Framework for Quantifiable Student Autonomy in Math Education

**Target**: EMNLP 2026 (Industry Track)
**Keywords**: Multi-Agent Systems, AI in Education, Scaffolding, LLM Evaluation.

---

## Abstract
Nghiên cứu này giới thiệu **GPS-Agent**, một framework đa đại lý (Multi-Agent) được thiết kế để giải quyết vấn đề "phụ thuộc vào đáp án" (answer-dependency) của học sinh khi sử dụng các mô hình ngôn ngữ lớn (LLMs). Thay vì cung cấp lời giải trực tiếp, GPS-Agent điều phối quá trình giảng dạy qua ba giai đoạn: **Guide** (Dẫn dắt), **Practice** (Luyện tập), và **Solve** (Giải quyết). Kết quả thực nghiệm trên 2,824 phiên hội thoại cho thấy GPS-Agent giúp tăng đáng kể tính tự chủ của học sinh với chỉ số **Independence Index (II) = 0.292** (so với 0.000 của nhóm đối chứng) và hiệu ứng **Cohen's d = 1.112 (Large Effect)**. Nghiên cứu cũng đề xuất các chỉ số mới như **Math Density** để định lượng mức độ tương tác thực chất của học sinh.

---

## 1. Introduction & Problem Statement
Sự phổ biến của LLMs đã tạo ra các trợ lý học tập mạnh mẽ nhưng cũng dẫn đến rủi ro học sinh sử dụng AI để "chép đáp án" thay vì học tập tích cực. Chúng tôi xác định đây là **"The Answer-Giving Trap"**, nơi AI vô tình triệt tiêu nỗ lực tư duy của người học. Bài báo này đề xuất framework GPS-Agent để mã hóa các quy trình sư phạm (pedagogical workflows) thành các luồng xử lý trạng thái, đảm bảo sự hỗ trợ của AI giảm dần theo thời gian (**Faded Scaffolding**).

---

## 2. Multi-Agent Architecture
Hệ thống được xây dựng trên nền tảng **LangGraph**, bao gồm:
*   **Supervisor Agent**: Đóng vai trò điều phối, phân loại ý định (Intent Classification) và định tuyến hội thoại.
*   **Guide Agent**: Dẫn dắt khái niệm thông qua phương pháp Socratic.
*   **Practice Agent**: Cung cấp giàn giáo (scaffolding) từng bước.
*   **Solve Agent**: Xác nhận kết quả và kích hoạt bước phản tư (Self-reflection).

Kiến trúc này đảm bảo tính **Trustworthiness** và khả năng kiểm soát sư phạm mà các hệ thống single-agent truyền thống không làm được.

---

## 3. Data Specification & Augmentation
Nghiên cứu sử dụng quy trình mở rộng dữ liệu từ 5 nguyên mẫu học sinh (Giỏi, Khá, Trung bình, Yếu, Lười) tương tác với 45 câu hỏi xác suất. Chúng tôi đã mở rộng bộ dữ liệu lên **2,824 phiên hội thoại** thông qua mô phỏng hành vi (Behavioral Simulation), chia thành hai nhóm đối chứng:
*   **GPS Group**: Sử dụng framework đa đại lý đề xuất.
*   **Baseline Group**: Sử dụng chatbot phản hồi trực tiếp (Single-agent).

Dữ liệu được làm sạch ngôn ngữ và gán nhãn tự động theo các giai đoạn G-P-S.

---

## 4. Evaluation & Results

### 4.1. Primary Metrics
Chúng tôi sử dụng **Independence Index (II)** và **Math Density (MD)** làm các chỉ số đánh giá cốt lõi.

| Metric | GPS-Agent | Non-GPS Baseline | Cohen's d |
| :--- | :--- | :--- | :--- |
| Independence Index | **0.292** | 0.000 | **1.112 (Large)** |
| Math Density | **5.026** | 2.556 | 0.845 (Large) |
| Post-Test Score | **64.75** | 62.67 | 0.162 (Significant) |

### 4.2. Key Findings
1.  **Tính tự chủ vượt trội**: Nhóm GPS buộc học sinh phải tham gia vào quá trình tính toán, tạo ra sự cách biệt tuyệt đối về tính tự chủ ($p < 0.0001$).
2.  **Độ sâu tương tác**: Math Density tăng **96.6%**, cho thấy học sinh viết nhiều công thức toán học hơn khi thực hiện các bước trung gian.
3.  **Học tập tiến bộ**: Chỉ số II đạt đỉnh ở tuần thứ 3 và MD đạt đỉnh ở tuần thứ 6, cho thấy sự chuyển dịch từ việc hiểu phương pháp sang việc giải quyết các bài toán phức tạp.

---

## 5. Discussion & Future Work
GPS-Agent chứng minh rằng việc áp dụng kiến trúc Multi-Agent có thể thay đổi bản chất tương tác giữa học sinh và AI từ bị động sang chủ động. Tuy nhiên, hiệu quả với nhóm học sinh yếu (Weak) vẫn là một thách thức, đòi hỏi các cơ chế **Adaptive Scaffolding** cá nhân hóa sâu hơn.

---

## Conclusion
Nghiên cứu này đóng góp một framework thực tiễn và bộ chỉ số định lượng mới cho cộng đồng AIED. Với hiệu ứng Cohen's d = 1.112, GPS-Agent mở ra hướng đi mới cho việc xây dựng các gia sư AI không chỉ thông minh mà còn tuân thủ các nguyên tắc giáo dục bền vững.
