# Danh mục tài liệu Nghiên cứu & Triển khai (Docs Index)
**Dự án: GPS-AIedu (Instructional Scaffolding with AI)**

Tài liệu này giúp bạn điều hướng nhanh qua các file hướng dẫn trong thư mục `docs/research/` theo cấu trúc dự án hiện tại (Tuần 2+).

---

## 1. Hướng dẫn Triển khai kỹ thuật (Technical Setup)
*   [Kế hoạch triển khai (Master)](./implementation_plan.md): Toàn bộ kiến trúc hệ thống, tech stack (Next.js, GAS, OpenAI/Ollama) và hợp đồng dữ liệu.
*   [Hướng dẫn cài đặt chi tiết](./webchat_autolog_setup.md): Các bước cấu hình biến môi trường (Environment Variables), Script Properties và Deploy Vercel/GAS.
*   [Thiết lập Khảo sát MSLQ](./mslq_survey_vn.md): Bản dịch tiếng Việt bộ công cụ khảo sát động lực học tập Motivated Strategies for Learning Questionnaire.

## 2. Hướng dẫn Chuyên môn & Sư phạm (Pedagogical Frameworks)
*   [Quy trình G.P.S. (Học sinh)](./GPS_Framework_Guide.md): Hướng dẫn 3 bước **Guide - Practice - Solve** để học sinh tương tác hiệu quả với AI mà không bị phụ thuộc vào đáp án.
*   [Hướng dẫn G.U.I.D.E. (Giáo viên)](./GUIDE_Instructional_Design.md): Khung thiết kế bài giảng 5 bước dành cho giáo viên để quản trị lớp học có tích hợp trợ lý AI.
*   [Bộ Q&A chuẩn (Xác suất)](./gps_qna_standard.md): Tổng hợp các kịch bản hỏi-đáp mẫu theo chủ đề Toán 11 để giả lập dữ liệu hoặc đào tạo AI.

## 3. Playbook & Vận hành (Operations)
*   [Playbook Vận hành thực tế](./week1_real_run_playbook.md): Quy trình từng bước từ thiết lập CSDL đến chạy Pilot lớp thật.
*   [Kịch bản Persona giả lập](./week1_persona_question_scripts.md): Bộ câu hỏi cho 5 nhóm học sinh (Advanced, Typical, Struggling, Offtrack, Inactive) để tạo dữ liệu kiểm thử.
*   [Hướng dẫn gán nhãn thủ công](./manual_labeling_guide.md): Cách đối soát giữa nhãn tự động của AI và nhãn thực tế do giáo viên đánh giá (Ground Truth).

## 4. Báo cáo & Phân tích (Reports & Evidence)
*   [Báo cáo tiến độ Tuần 1](./bao_cao_tuan_1.md): Tổng kết giai đoạn xây dựng nền tảng log tự động.
*   [Báo cáo cho Giáo viên (Tuần 2)](./Bao_Cao_Giao_Vien_Tuan_1.md): Mẫu báo cáo phân tích hành vi gửi cho giáo viên hướng dẫn.
*   [Kế hoạch đánh giá hiệu quả](./effectiveness_evaluation_plan.md): Phương pháp nghiên cứu thực nghiệm, so sánh nhóm Experimental vs Control sử dụng ANCOVA.

---
> [!NOTE]
> Tất cả các file trong thư mục này đều liên kết trực tiếp với mã nguồn tại `src/tools/` (GAS) và `webchat/` (Next.js). Cần cập nhật đồng bộ khi có thay đổi Schema.
