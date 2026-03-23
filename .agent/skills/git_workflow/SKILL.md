---
name: git_workflow
description: Quy trình tự động commit và push sau mỗi phase công việc để đảm bảo tính an toàn và đồng bộ của codebase (GPS-AIedu).
---

# Git Workflow Skill (GPS-AIedu)

Quy trình này đảm bảo mọi thay đổi quan trọng trong mã nguồn (Webchat, Analysis, Scripts) đều được lưu vết và đồng bộ với repository.

## Hướng dẫn thực hiện

1. **Kiểm tra trạng thái**: Luôn chạy `git status` để xem các file bị thay đổi (Next.js, Python, GAS scripts).
2. **Tuân thủ .gitignore & .dockerignore**: 
    - Tuyệt đối không push thư mục `.agent/` (vì chứa kế hoạch, dữ liệu nội bộ của assistant).
    - Các file `.md` (markdown) trừ `README.md` và các exceptions khác (`docs/research/`) đều bị ignore. Để push file trong `docs/research/`, hãy kiểm tra `.gitignore`.
    - Tránh push các file dữ liệu thực tế (`data/raw/`, `data/processed/`), chỉ push `data/raw/mock_xxx.csv` nếu cần file mẫu cho CI/CD.
    - Không push các file bí mật (`.env`, `.env.local`).
3. **Phân loại thay đổi**: Chỉ stage các file thực sự liên quan đến phase công việc (VD: Sửa UI chat, thêm metric phân tích).
4. **Commit và Push**:
    - Commit với nội dung mô tả rõ về tiến độ tuần (VD: `feat: add MSLQ survey in webchat`, `fix: behavior_analysis regex for G/P/S`).
    - Chạy `git push` ngay sau khi commit thành công.
5. **Thời điểm thực hiện**: Thực hiện ngay sau khi hoàn thành một đầu việc lớn (feature mới, fix bug nghiêm trọng, hoặc sau khi tạo File Review).

> [!IMPORTANT]
> - **Chỉ push README.md** đối với các file markdown thông thường trừ khi có yêu cầu đặc biệt.
    - Tài liệu nghiên cứu trong `docs/research/` cần được push để đồng bộ giữa các thành viên nhóm nghiên cứu.
> - **Không bao giờ push .agent/** lên repository.
> - Luôn review kỹ `git status` trước khi `git add .`.

---
**Reviewer**: Antigravity Agent
**Version**: GPS-AIedu updated 2026-03-23
