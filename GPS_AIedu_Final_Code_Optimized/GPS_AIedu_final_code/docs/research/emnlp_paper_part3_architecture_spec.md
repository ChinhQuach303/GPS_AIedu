# GPS-Agent Research Paper: Part 3 - System Architecture & Multi-Agent Design

Tài liệu này trình bày chi tiết về kiến trúc kỹ thuật của hệ thống GPS-Agent, tập trung vào cách điều phối các mô hình ngôn ngữ lớn (LLMs) để thực hiện các mục tiêu sư phạm.

---

## 1. Multi-Agent Framework: LangGraph Orchestration

Thay vì sử dụng một luồng hội thoại tuyến tính (Linear Chat), GPS-Agent được xây dựng dựa trên kiến trúc **State Graph** (Đồ thị trạng thái). Điều này cho phép hệ thống duy trì tính nhất quán của lộ trình sư phạm qua nhiều lượt hội thoại.

### 1.1. State Management (Quản lý trạng thái)
Toàn bộ thông tin được đóng gói trong một cấu trúc `AgentState` bao gồm:
*   **Messages**: Lịch sử hội thoại đầy đủ giữa AI và học sinh.
*   **Current Intent**: Ý định sư phạm hiện tại do Supervisor xác định.
*   **Trace Labels**: Nhật ký hành trình (ví dụ: `G -> P1 -> P2 -> S`) để theo dõi tiến trình của học sinh.
*   **Student Profile**: Cấp độ năng lực (Giỏi/Khá/TB/Yếu) để cá nhân hóa phản hồi.

---

## 2. The Supervisor: The Pedagogical Router

Supervisor đóng vai trò là "não bộ" điều phối, chịu trách nhiệm phân tích phản hồi của học sinh và quyết định bước tiếp theo.

*   **Cơ chế hoạt động**: Supervisor sử dụng một mô hình LLM với `temperature=0.1` để thực hiện **Intent Classification** (Phân loại ý định). 
*   **Logic điều hướng (Conditional Edges)**: 
    - Nếu học sinh bế tắc hoặc chưa hiểu đề bài -> Chuyển hướng sang `Guide Node`.
    - Nếu học sinh đã hiểu hướng đi nhưng cần hỗ trợ tính toán -> Chuyển hướng sang `Practice Node`.
    - Nếu học sinh đã hoàn thành các bước trung gian -> Cho phép `Solve Node` xác nhận kết quả.
*   **Pedagogical Constraints (Ràng buộc sư phạm)**: Supervisor ngăn chặn việc đi thẳng tới `Solve Node` nếu học sinh chưa trải qua các bước tư duy cần thiết.

---

## 3. Specialized Pedagogical Agents (Nodes)

Mỗi Node trong đồ thị là một Agent chuyên biệt được tối ưu hóa bằng Prompt Engineering:

### 3.1. Guide Agent (Dẫn dắt khái niệm)
*   **Nhiệm vụ**: Giải thích lý thuyết, gợi ý hướng tiếp cận bằng các câu hỏi gợi mở (Socratic Method).
*   **Ràng buộc**: Tuyệt đối không thực hiện bất kỳ phép tính nào hoặc đưa ra các con số cụ thể.

### 3.2. Practice Agent (Giàn giáo luyện tập)
*   **Nhiệm vụ**: Cung cấp **Scaffolding**. Chia nhỏ bài toán thành các câu hỏi phụ (sub-questions). 
*   **Ràng buộc**: Chỉ hướng dẫn từng bước một. Không được giải quyết toàn bộ bài toán trong một lượt phản hồi.

### 3.3. Solve Agent (Xác nhận & Phản tư)
*   **Nhiệm vụ**: Kiểm tra đáp án cuối cùng của học sinh. 
*   **Tính năng bổ sung**: Kích hoạt bước **Self-Reflection**. Yêu cầu học sinh giải thích logic đằng sau đáp án để đảm bảo sự hiểu biết thực chất.

---

## 4. Implementation Details

*   **In-memory Persistence**: Sử dụng `MemorySaver` để lưu trữ trạng thái phiên, cho phép hệ thống "nhớ" học sinh đang ở bước nào ngay cả khi có gián đoạn.
*   **Model Agnostic**: Hệ thống có thể chạy linh hoạt với các mô hình khác nhau (Qwen-2.5, GPT-4) thông qua lớp `llm_factory`.
*   **Language Enforcement**: Tích hợp các lớp lọc (filters) để đảm bảo ngôn ngữ phản hồi luôn là tiếng Việt và tuân thủ định dạng LaTeX cho các công thức toán học.

---

Kiến trúc này giúp bài báo chứng minh được khả năng **"Control & Trustworthiness"** – một trong những tiêu chí quan trọng nhất của EMNLP 2026. Bạn có muốn tôi vẽ thêm sơ đồ Mermaid chi tiết về luồng dữ liệu (Data Flow) giữa các Agent để chèn vào bài báo không?
