# GPS-Agent Research Paper: Part 1 - Introduction & Methodology

Tài liệu này trình bày chi tiết phần nội dung cốt lõi đầu tiên của bài báo nghiên cứu nộp EMNLP 2026.

---

## 1. Introduction & Problem Statement (Mở đầu & Đặt vấn đề)

### 1.1. Bối cảnh: Nghịch lý của AI trong Giáo dục
Sự bùng nổ của các mô hình ngôn ngữ lớn (LLMs) như GPT-4, Qwen đã mở ra kỷ nguyên gia sư AI (AI Tutors). Tuy nhiên, một vấn đề nghiêm trọng nảy sinh: **"The Answer-Giving Trap"** (Bẫy trả lời trực tiếp). Các mô hình này thường được tối ưu hóa để làm hài lòng người dùng bằng cách đưa ra đáp án nhanh nhất có thể.

### 1.2. Vấn đề nghiên cứu (Research Problem)
Trong môi trường giáo dục, đặc biệt là Toán học, việc nhận đáp án ngay lập tức triệt tiêu quá trình tư duy (Cognitive processing). Điều này dẫn đến:
- **Sự phụ thuộc (Answer-dependency)**: Học sinh mất khả năng tự giải quyết vấn đề khi không có AI.
- **Mất kiểm soát sư phạm**: AI không tuân theo các lý thuyết giáo dục (như Scaffolding hay Bloom's Taxonomy) mà chỉ phản hồi theo dữ liệu xác suất.
- **Khó định lượng sự tiến bộ**: Điểm số không còn phản ánh đúng năng lực nếu học sinh "mượn" trí tuệ của AI.

### 1.3. Mục tiêu nghiên cứu
Chúng tôi đề xuất **GPS-Agent**, một framework đa đại lý (Multi-agent) được thiết kế để điều soát quá trình giảng dạy, đảm bảo AI chỉ đóng vai trò "người dẫn đường" (Guide) thay vì "người làm hộ".

---

## 2. Proposed Solution: The GPS Framework (Giải pháp đề xuất)

Chúng tôi chuyển đổi quy trình sư phạm truyền thống thành một luồng xử lý trạng thái (Stateful Flow) gồm 3 giai đoạn chính:

1.  **[G] Guide (Dẫn dắt)**: AI không tính toán. Nhiệm vụ là thu thập thông tin và giúp học sinh hiểu bản chất vấn đề thông qua các câu hỏi chiến lược (Socratic questioning).
2.  **[P] Practice (Luyện tập)**: AI cung cấp các "giàn giáo" (Scaffolding) – chia nhỏ bài toán thành các bước trung gian, yêu cầu học sinh thực hiện các phép tính cụ thể.
3.  **[S] Solve (Giải quyết & Phản tư)**: Chỉ sau khi học sinh đã đi qua [G] và [P], AI mới xác nhận đáp án cuối cùng và bắt buộc bước **Reflection** (Giải thích tại sao làm như vậy).

**Nguyên lý cốt lõi**: **Faded Scaffolding** (Giàn giáo mờ dần). Khi hệ thống nhận thấy `Independence Index` của học sinh tăng lên, mức độ gợi ý ở bước [P] sẽ tự động giảm xuống.

---

## 3. Methodology: Multi-Agent System Architecture (Phương pháp luận)

Để hiện thực hóa framework GPS, chúng tôi xây dựng kiến trúc **Multi-Agent Orchestration** dựa trên đồ thị trạng thái (State Graph).

### 3.1. Các thực thể Đại lý (Agents Roles)
- **Supervisor Agent (Người điều phối)**: Sử dụng kỹ thuật Intent Classification để phân tích phản hồi của học sinh. Nó quyết định luồng hội thoại nên tiếp tục ở bước [G], chuyển sang [P] hay cho phép bước [S].
- **Pedagogical Agents (Guide, Practice, Solve)**: Mỗi đại lý được cấu hình với một System Prompt chuyên biệt, giới hạn phạm vi kiến thức và phong cách phản hồi để tránh "leak" đáp án quá sớm.

### 3.2. Quy trình kỹ thuật (Technical Pipeline)
1.  **State Management**: Toàn bộ lịch sử hội thoại, nhãn trạng thái (G/P/S) và các chỉ số hành vi được lưu trữ trong `AgentState`.
2.  **Logic Logic Control**: Supervisor Agent áp dụng các "luật cứng" sư phạm (ví dụ: Không được chuyển sang [S] nếu chưa qua ít nhất một lượt [G]).
3.  **Independence Measurement**: Hệ thống tích hợp một module tính toán thời gian thực chỉ số tự chủ học sinh.

### 3.3. Các chỉ số đo lường mới (Novel Metrics)
Điểm khác biệt của nghiên cứu này là việc đưa ra các chỉ số NLP-based để đo lường giáo dục:
- **Independence Index (II)**: Tỷ lệ thành công tự thân của học sinh.
- **Math Density (MD)**: Đo lường mật độ ký tự toán học (LaTeX) trong câu trả lời của học sinh để xác định mức độ tham gia vào bài toán.
- **Sequence Chaos Index (SCI)**: Đo lường mức độ hỗn loạn/nhảy cóc trong tư duy của học sinh.

---

## Tóm tắt đóng góp của bài báo (Key Contributions)
1.  Thiết kế framework **G.P.S** giúp kiểm soát hành vi của AI Tutor.
2.  Xây dựng hệ thống **Multi-agent** có khả năng điều phối sư phạm linh hoạt.
3.  Đề xuất bộ metrics mới giúp định lượng **Autonomy** thay vì chỉ định lượng **Accuracy**.
4.  Cung cấp bộ dữ liệu 2,800+ phiên hội thoại đã gán nhãn cho cộng đồng nghiên cứu AIED (AI in Education).

---

Tiếp theo, tôi sẽ bắt đầu chuẩn bị phần **4. Experiments & Results** dựa trên số liệu thực tế bạn đã có. Bạn có muốn điều chỉnh hay nhấn mạnh thêm "Keyword" nào trong phần Methodology này không?
