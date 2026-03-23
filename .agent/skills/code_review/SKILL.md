---
name: code_review
description: Quy trình thực hiện review code hệ thống, so sánh với kế hoạch triển khai (implementation_plan.md) và đảm bảo các tiêu chuẩn kỹ thuật (G.P.S. steps, Prompt safety, Logging format).
---

# Code Review Skill (GPS-AIedu)

Skill này hướng dẫn Assistant cách thực hiện đánh giá code chuyên nghiệp trước khi kết thúc một version (Pilot Week 1, 2...) hoặc phase công việc.

## Quy trình Thực hiện

### 1. Phân tích Hiện trạng (Context Analysis)
- Đọc `docs/research/implementation_plan.md` để nắm bắt mục tiêu của phase (VD: Pilot, Setup Dashboard).
- Kiểm tra các thay đổi gần đây (`git status`, `git diff`).
- Đọc `Claude.md` (GPS-AIedu version) để hiểu các ràng buộc về mô hình sư phạm và bảo mật dữ liệu.

### 2. Tiêu chí Đánh giá (Review Criteria)
- **Mô hình G.P.S.**: AI có tuyệt đối tuân thủ nguyên tắc không giải hộ? Các gợi ý (Guide/Practice) có đủ dễ hiểu cho học sinh lớp 11 không?
- **Prompt Safety**: System prompt có đảm bảo không bị prompt injection hoặc rò rỉ đáp án?
- **Logging Integrity**: Mọi hội thoại có được POST về GAS đúng định dạng JSON không? Có dữ liệu `student_id` và `timestamp` không?
- **Bảo mật (GAS)**: `LOG_TOKEN` có được truyền an toàn và có đang sử dụng SHA-256 để hash ID học sinh không?
- **Phân tích Behavior**: `src/analysis/behavior_analysis.py` có xử lý tốt các trường hợp dữ liệu rỗng hoặc sai định dạng ngày tháng không?
- **Hiệu năng Web**: Next.js Server Components vs Client Components có được sử dụng hợp lý để tối ưu latency?

### 3. Tạo file Review
- Tạo file review mới: `.agent/review_v[VERSION].md`.
- Cấu trúc:
    - **1. Overview**: Tóm tắt tổng quan.
    - **2. Đã hoàn thành (Pros)**: Những gì đã làm tốt (VD: Log ổn định, Chat mượt).
    - **3. Vấn đề (Issues/Gap)**: Những gì chưa khớp với plan hoặc có lỗi tiềm tàng (VD: Thiếu cột Difficulty).
    - **4. Khuyến nghị (Recommendations)**: Các bước fix cụ thể.
    - **5. Kết luận (Verdict)**: Pass / In Progress / Fail.

## Lưu ý Quan trọng
- Luôn giữ thái độ khách quan và xây dựng.
- Tập trung vào tính chính xác của dữ liệu nghiên cứu và trải nghiệm học tập của học sinh.
- **Không bao giờ push file review này lên repository** (đã bị `.gitignore` chặn).

---
**Reviewer**: Antigravity Agent
**Version**: 1.0.0 (GPS-AIedu)
