# Critical Research Refinement Plan: Addressing EMNLP Submission Risks

Tài liệu này đặc tả các hành động cần thiết để giải quyết 4 rủi ro lớn nhất mà bạn đã chỉ ra, nhằm đảm bảo tính khách quan và chiều sâu khoa học cho bài báo EMNLP 2026.

---

## 1. Dataset Validity: Transitioning from Simulation to Pilot (Real Students)

**Rủi ro**: Circular Evaluation (LLM dạy LLM).
**Giải pháp**: Thực hiện một nghiên cứu **Pilot thực tế (n=60 học sinh)**.

### 1.1. Thiết kế Pilot
*   **Đối tượng**: 60 học sinh lớp 11 (chia làm 2 lớp: 30 thực nghiệm, 30 đối chứng).
*   **Công cụ**: Sử dụng trực tiếp UI Webchat hiện tại kết nối với GPS-Agent.
*   **Dữ liệu thu thập**: Hội thoại thực tế, điểm Pre-test/Post-test thực tế và khảo sát MSLQ (Motivated Strategies for Learning Questionnaire).

### 1.2. So sánh tính xác thực (Authenticity Alignment)
*   So sánh phân bố các metrics (II, MD) giữa tập dữ liệu **Simulated** và **Real-world**.
*   Chứng minh rằng `StudentSimulatorV2` mô phỏng sát với hành vi thực tế (Pearson correlation > 0.7) để "cứu" bộ dữ liệu 2,824 phiên.

---

## 2. Strengthening the Baseline (Strong Baseline Setup)

**Rủi ro**: Baseline hiện tại (Non-GPS) quá yếu, không tạo ra sự so sánh công bằng.
**Giải pháp**: Thiết lập **Strong Baseline Agent**.

*   **Tên Agent**: `CoT-Tutor-Baseline`.
*   **Cấu hình**: Một Single-Agent sử dụng mô hình mạnh nhất (ví dụ: GPT-4o) kèm theo System Prompt phức tạp áp dụng kỹ thuật **Chain-of-Thought (CoT)** và hướng dẫn sư phạm tiêu chuẩn (không dùng đa đại lý).
*   **Mục tiêu**: Chứng minh rằng kiến trúc **Multi-Agent Orchestration** của GPS mang lại giá trị thực chất vượt trội hơn so với việc chỉ dùng "One-shot Prompting" thông thường.

---

## 3. Metric Validation & Inter-Rater Reliability (IRR)

**Rủi ro**: Chỉ số II và MD chưa được kiểm chứng độ tin cậy bởi chuyên gia.
**Giải pháp**: Xây dựng **Human Evaluation Protocol**.

### 3.1. Quy trình đánh giá (Rubric)
*   Mời 3 giáo viên toán chấm điểm độc lập trên 100 phiên hội thoại mẫu.
*   Tiêu chí chấm: Thang điểm 1-5 cho "Mức độ tự chủ của học sinh" (Autonomy level).

### 3.2. Tính toán độ tin cậy
*   Sử dụng chỉ số **Cohen's Kappa** hoặc **Fleiss' Kappa** để đo lường sự đồng thuận giữa các giáo viên (Inter-rater reliability).
*   Tính toán độ tương quan giữa điểm của giáo viên và chỉ số `Independence Index` tự động. Nếu tương quan > 0.8, bộ metric được coi là hợp lệ (Validated).

---

## 4. Comprehensive Error Analysis (Phân tích lỗi)

**Rủi ro**: Thiếu đánh giá về các trường hợp thất bại (Failure cases).
**Giải pháp**: Phân loại và phân tích 3 nhóm lỗi chính của GPS-Agent.

### 4.1. Supervisor Routing Errors
*   **Trường hợp**: Học sinh đã sẵn giải bài nhưng bị gửi ngược lại bước [G]uide (Over-scaffolding).
*   **Tác động**: Gây nản lòng và giảm Math Density.

### 4.2. Scaffolding Hallucinations
*   **Trường hợp**: AI đưa ra các bước trung gian sai logic toán học hoặc gợi ý không liên quan đến QID.
*   **Phân tích**: Sử dụng `math_verifier.py` để định lượng tỷ lệ lỗi này.

### 4.3. Behavioral Mismatch
*   **Trường hợp**: Agent không nhận diện được hành vi "Lười" và vô tình cung cấp đáp án quá sớm ở bước [P].

---

## 5. Timeline hoàn thiện (Next Steps)

| Hạng mục | Hành động | Thời hạn |
| :--- | :--- | :--- |
| **Data Validation** | Chạy Pilot với 60 học sinh lớp thật. | Tuần 1-2 |
| **Strong Baseline** | Chạy mô phỏng lại nhóm Baseline với GPT-4o + CoT. | Tuần 1 |
| **Human Eval** | Gửi 100 log cho giáo viên chấm theo Rubric. | Tuần 2 |
| **Error Analysis** | Trích xuất 50 case "Low II" để phân tích định tính. | Tuần 2 |

---

Kế hoạch này sẽ biến bài báo của bạn từ "mô hình thử nghiệm" thành một "nghiên cứu thực chứng" (Empirical study) thực thụ. Bạn muốn tôi bắt đầu bằng việc **thiết lập Strong Baseline** hay soạn **Rubric cho giáo viên** trước?
