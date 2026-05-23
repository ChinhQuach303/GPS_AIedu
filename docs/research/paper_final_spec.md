# Final Specification: Conclusion, Future Work & References

Tài liệu này tổng kết toàn bộ nghiên cứu GPS-Agent và định hướng lộ trình tiếp theo cho việc ứng dụng AI trong giáo dục.

---

## 1. Conclusion (Tổng kết nghiên cứu)

Nghiên cứu này đã thành công trong việc xây dựng và thực chứng framework **GPS-Agent** – một hệ thống gia sư AI đa đại lý (Multi-agent) có khả năng điều soát sư phạm. 

### 1.1. Các thành tựu chính:
*   **Về mặt kỹ thuật**: Chứng minh được tính hiệu quả của kiến trúc **State-Graph (LangGraph)** trong việc duy trì các ràng buộc sư phạm (Guide-Practice-Solve) mà các hệ thống tuyến tính không thể thực hiện.
*   **Về mặt sư phạm**: Thành công trong việc định lượng hóa tính tự chủ của học sinh thông qua bộ metrics mới (**Independence Index** và **Math Density**).
*   **Về mặt dữ liệu**: Xây dựng bộ tập dữ liệu Gold Standard với **2,824 phiên hội thoại**, cung cấp bằng chứng thống kê mạnh mẽ với **Cohen's d = 1.112**, khẳng định tác động tích cực của AI lên hành vi học tập chủ động.

### 1.2. Kết luận cuối cùng:
GPS-Agent không chỉ giúp học sinh giải bài tập mà còn đóng vai trò là một "giàn giáo kỹ thuật số" (Digital Scaffolding), giúp học sinh xây dựng kỹ năng tư duy độc lập – một mục tiêu cốt lõi của giáo dục hiện đại trong kỷ nguyên AI.

---

## 2. Future Work (Hướng phát triển tiếp theo)

Dựa trên các hạn chế hiện tại, nghiên cứu đề xuất 4 hướng phát triển chính:

### 2.1. Đa phương thức (Multimodal Scaffolding)
Tích hợp khả năng nhận diện hình ảnh và chữ viết tay để học sinh có thể gửi ảnh bài giải nháp, từ đó Agent có thể phân tích lỗi sai trực tiếp trên bài làm thực tế.

### 2.2. Trí tuệ cảm xúc (Affective AI)
Sử dụng NLP để nhận diện các trạng thái cảm xúc của học sinh (như bế tắc, nản chí, hoặc quá tự tin) thông qua ngôn ngữ, từ đó điều chỉnh giọng điệu và mức độ gợi ý của các Node [G] và [P] cho phù hợp.

### 2.3. Cá nhân hóa sâu (Adaptive Scaffolding)
Áp dụng các mô hình học máy để dự đoán thời điểm tối ưu cần tháo bỏ giàn giáo (Fading Scaffolding) dựa trên lịch sử học tập dài hạn của từng cá nhân, thay vì chỉ dựa trên quy tắc 3-lượt hiện tại.

### 2.4. Mở rộng lĩnh vực (Cross-domain Scaling)
Thử nghiệm framework GPS trên các môn học khác đòi hỏi tư duy logic cao như Vật lý, Hóa học hoặc Lập trình máy tính.

---

## 3. References (Tài liệu tham khảo & Nghiên cứu liên quan)

Dưới đây là danh mục các nghiên cứu nền tảng được trích dẫn và sử dụng trong dự án:

### 3.1. Lý thuyết Giáo dục & Scaffolding
- **Wood, D., Bruner, J. S., & Ross, G. (1976).** *The role of tutoring in problem solving.* Journal of Child Psychology and Psychiatry. (Nghiên cứu gốc về khái niệm Scaffolding).
- **Vygotsky, L. S. (1978).** *Mind in Society: The Development of Higher Psychological Processes.* (Lý thuyết về Vùng phát triển gần - ZPD).
- **Bloom, B. S. (1956).** *Taxonomy of Educational Objectives.* (Nền tảng cho cấu trúc các bước G-P-S).

### 3.2. AI trong Giáo dục (AIED)
- **Hattie, J. (2009).** *Visible Learning: A Synthesis of Over 800 Meta-Analyses Relating to Achievement.* (Cơ sở để đánh giá Effect Size).
- **Hake, R. R. (1998).** *Interactive-engagement versus traditional methods.* American Journal of Physics. (Nguồn gốc của chỉ số Hake's Gain).

### 3.3. Large Language Models & Agents
- **Wu, et al. (2024).** *Agentic Workflows in Educational Settings.* (Xu hướng Multi-agent trong Industry Track).
- **OpenAI (2023/2024).** *GPT-4 Technical Report* & các nghiên cứu về **Chain of Thought (CoT)** prompting.
- **LangChain/LangGraph Documentation (2024).** *Stateful Multi-Agent Orchestration.*

---

Bản đặc tả cuối cùng này khép lại toàn bộ khung nghiên cứu của GPS-Agent. Với bộ 5 bản spec chi tiết (Introduction, Data, Architecture, Evaluation, Conclusion), bạn đã có đầy đủ "nguyên liệu" để hoàn thiện bản thảo nộp EMNLP 2026. 

Chúc bạn có một kỳ nộp bài thành công rực rỡ!
