# Claude.md — Hướng dẫn cho AI Assistant (Dự án GPS-AIedu)

Chào mừng bạn đến với dự án **GPS-AIedu**. Đây là hệ thống nghiên cứu giáo dục ứng dụng AI hỗ trợ dạy và học Toán lớp 11, sử dụng mô hình G.P.S. cho học sinh và quy trình G.U.I.D.E. cho giáo viên.

## 1. Kiến trúc Hệ thống (Hybrid Architecture)

Hệ thống kết hợp giữa Web App hiện đại và công cụ phân tích dữ liệu:
- **Web Chat**: Next.js (App Router) triển khai trên Vercel, sử dụng OpenAI API (`gpt-4o-mini`).
- **Data Collection**: Mọi lượt hội thoại được tự động log về Google Sheets thông qua **Google Apps Script (GAS)** Web App.
- **Analysis Layer**: Các script Python thực hiện phân tích hành vi học tập (Markov Chain, K-means Clustering) từ dữ liệu log.
- **Dashboard**: Google Sheets Dashboard sử dụng các công thức tính toán thời gian thực để báo cáo tiến độ.

## 2. Công nghệ Core

- **Frontend/API**: Next.js 14+, React, TailwindCSS.
- **LLM**: OpenAI SDK, tích hợp `ai` SDK cho Streaming.
- **Logging**: REST API POST sang GAS endpoint.
- **Analysis**: Python 3.10 (Pandas, Scikit-learn, Matplotlib, Seaborn).

## 3. Quy định Cấu trúc Code

- **webchat/**: Thư mục chứa mã nguồn giao diện chat.
  - `app/api/chat/`: Endpoint xử lý hội thoại và logging.
  - `lib/`: Logic hỗ trợ (detect behavior, prompt management, GAS logging).
- **src/ai/**: Chứa các phiên bản System Prompt và prompt mẫu (G/P/S).
- **src/analysis/**: Chứa mã nguồn phân tích dữ liệu nghiên cứu.
- **src/tools/**: Các script setup môi trường, script GAS, và generator dữ liệu mẫu.
- **docs/research/**: Tài liệu quan trọng về kế hoạch triển khai (Week 1, Week 2, ...), bộ tiêu chuẩn gán nhãn.

## 4. Hướng dẫn Phát triển cho AI

### 4.1. Nguyên tắc G.P.S. (Học sinh)
Khi tương tác hoặc viết prompt cho AI học sinh:
- **Guide (G)**: Chỉ giải thích khái niệm, không giải bài.
- **Practice (P)**: Chia nhỏ bài toán, gợi ý từng bước, không đưa đáp án.
- **Solve (S)**: Kiểm tra logic lời giải của học sinh, nhận xét và tóm tắt.
- **Tuyệt đối không giải hộ**: Nếu học sinh yêu cầu đáp án, AI phải khéo léo từ chối và đưa ra gợi ý/kế hoạch giải.

### 4.2. Giao thức Logging (Data Integrity)
- Mọi log gửi về GAS phải tuân thủ schema **13 cột (A-M)** như định nghĩa trong `docs/research/implementation_plan.md`.
- Đảm bảo có `student_id`, `topic`, `question`, `ai_response` và `timestamp`.
- Hệ thống tự động hash `student_id` bằng SHA-256 kèm `SALT` tại layer GAS để bảo mật danh tính.

### 4.3. Phân tích Hành vi
- Sử dụng `src/analysis/behavior_analysis.py` để đánh giá hiệu quả của mô hình G.P.S. qua các chỉ số: Transition probability (% G->P, % P->S) và Sequence score.

## 5. Các file quan trọng cần lưu ý
- `webchat/app/api/chat/route.ts`: Core logic điều phối hội thoại và log.
- `src/ai/system_prompt.md`: Định nghĩa vai trò của AI Tutor.
- `src/tools/gas_script.js`: Mã nguồn chạy trên Google Apps Script.
- `docs/research/implementation_plan.md`: Kế hoạch chi tiết của dự án.
- `docs/research/week1_real_run_playbook.md`: Hướng dẫn vận hành thực tế.

---
**Version hiện tại**: 1.0.0 (GPS-AIedu Template)
**Reviewer**: Antigravity Agent
