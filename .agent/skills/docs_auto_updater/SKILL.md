---
name: Docs Auto-Updater
description: Tự động hóa việc cập nhật tài liệu dự án (docs/research/ và README.md) dựa trên codebase hiện tại.
---

# Docs Auto-Updater Skill (GPS-AIedu)

Skill này được thiết kế để duy trì tính nhất quán giữa mã nguồn (Web Chat, Analysis Scripts) và tài liệu nghiên cứu kỹ thuật.

## Quy trình Thực hiện (Workflow)

### 1. Thu thập Context Codebase

- Quét thư mục `webchat/` để cập nhật cấu trúc API và các state quản lý hội thoại.
- Kiểm tra `src/ai/` để đảm bảo tài liệu phản ánh phiên bản System Prompt mới nhất.
- Đọc `src/analysis/` để cập nhật các chỉ số đánh giá hiệu năng (Markov, Clustering).

### 2. Cập nhật Thư mục `docs/research/`

- Cập nhật `docs/research/implementation_plan.md` khi có thay đổi trong kiến trúc logging hoặc tool calling (nếu có).
- Chỉnh sửa các hướng dẫn pilot (`WEEK2_PILOT_GUIDE.md`) để khớp với logic thực tế của webchat.
- Đảm bảo các chỉ dẫn cài đặt (GAS Setup, Next.js Env) là chính xác và bảo mật.

### 3. Đồng bộ hóa `README.md`

- Viết lại phần Overview để nêu bật tiến độ nghiên cứu của dự án (Pilot tuần 1, tuần 2...).
- Cập nhật bảng "Chỉ số Phân tích" (MAE/R2 hoặc tỷ lệ % G/P/S) từ báo cáo phân tích mới nhất.
- Kiểm tra các link dẫn tới tài liệu chi tiết trong `docs/research/`.

## Lưu ý Quan trọng
- **README.md là bộ mặt của Repo**: Mọi thông tin cập nhật công khai phải được đẩy vào `README.md`.
- **Hạn chế push các tài liệu nội bộ**: Luôn tuân thủ quy tắc git_workflow: không push `.agent/` và phần lớn các file `.md` mới (đã bị `.gitignore` chặn).
- **GitHub alerts & formatting**: Sử dụng GitHub alerts để nhấn mạnh các cảnh báo về thay đổi Breaking Changes trong API hoặc Schema logging. 
- Giữ phong cách chuyên nghiêp, cô đọng phục vụ cả mục tiêu kỹ thuật và nghiên cứu thực nghiệm.

---
**Reviewer**: Antigravity Agent  
**Version**: GPS-AIedu updated 2026-03-23
