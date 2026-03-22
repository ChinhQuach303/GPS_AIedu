# KẾ HOẠCH ĐÁNH GIÁ HIỆU QUẢ PHƯƠNG PHÁP (EFFECTIVENESS EVALUATION PLAN)

Để chứng minh phương pháp **G.P.S. (Học sinh)** và **G.U.I.D.E. (Giáo viên)** thực sự hiệu quả so với cách dùng AI tự do, chúng ta cần một khung đánh giá đa chiều dựa trên 3 trụ cột: **Kết quả học tập**, **Hành vi học tập**, và **Tâm lý học tập**.

---

## 1. Các chỉ số đo lường (Metrics)

### A. Chỉ số Kết quả (Outcome Metrics)
*   **Normalized Learning Gain (g)**: Đo mức độ tăng trưởng thực tế giữa Pre-test và Post-test.
    - Công thức: `g = (Post_Score - Pre_Score) / (Max_Score - Pre_Score)`
    - *Ý nghĩa*: Loại bỏ yếu tố học sinh giỏi đã có điểm cao sẵn.
*   **Problem Solving Accuracy**: Tỷ lệ giải đúng các bài toán ở bước **S (Solve)** sau khi đã qua bước G và P.

### B. Chỉ số Hành vi (Process & Fidelity Metrics)
*   **GPS Fidelity Score (Điểm tuân thủ)**: Điểm số cho mức độ tuân thủ quy trình G -> P -> S.
    - Chấm 1.0 cho chuỗi G-P-S hoàn chỉnh.
    - Chấm 0.5 cho chuỗi G-S (nhảy bước).
    - Chấm 0.1 cho chuỗi S (chỉ xin đáp án).
*   **Scaffolding Efficiency**: Số lượt chat cần thiết để học sinh tự hoàn thành bài giải ở bước S. (Ít lượt hơn nhưng hiệu quả hơn = AI giàn giáo tốt).
*   **Intervention Response**: Tỷ lệ học sinh quay lại đúng lộ trình sau khi giáo viên can thiệp (dựa trên Dashboard Alerts).

### C. Chỉ số Tâm lý (Psychological Metrics)
*   **SRL Score (Self-Regulated Learning)**: Sử dụng thang đo MSLQ (đã dịch) để so sánh các biến:
    - Metacognitive Self-Regulation (Tự điều chỉnh siêu nhận thức).
    - Effort Regulation (Điều chỉnh nỗ lực).
*   **AI Dependency Ratio**: Tỷ lệ các câu hỏi "cho em đáp án" giảm dần theo thời gian sử dụng G.P.S.

---

## 2. Thiết kế thực nghiệm (Experimental Design)

Để chứng minh tính hiệu quả, chúng ta cần so sánh:
1.  **Nhóm Thực nghiệm (Experimental Group)**: Sử dụng Webchat có System Prompt hướng dẫn theo G.P.S và giáo viên dùng Dashboard G.U.I.D.E.
2.  **Nhóm Đối chứng (Control Group)**: Sử dụng AI tự do (ChatGPT/Gemini thông thường) không có quy trình hướng dẫn.

### Các mốc dữ liệu cần thu thập:
- **T0 (Baseline)**: Điểm Pre-test + Khảo sát MSLQ Pre-test.
- **T1 (Process)**: Toàn bộ log tương tác GPS (Tuần 2 - Tuần 5).
- **T2 (Outcome)**: Điểm Post-test + Khảo sát MSLQ Post-test.

---

## 3. Bản đồ chứng minh (Proof Roadmap)

| Câu hỏi nghiên cứu | Metric chính | Công cụ phân tích | Chứng minh hiệu quả khi... |
| :--- | :--- | :--- | :--- |
| **Có giúp học tốt hơn không?** | Normalized Learning Gain | `perform_ancova()` | Nhóm thực nghiệm có `g` cao hơn đáng kể (p < 0.05). |
| **Có giảm phụ thuộc AI không?** | GPS Fidelity + Offtrack reduction | `calculate_markov_transitions()` | Xác suất từ G -> P -> S tăng dần, S -> S (nhắc lại đáp án) giảm dần. |
| **Học sinh có tự chủ hơn không?** | MSLQ Score Change | Paired T-test | Điểm Siêu nhận thức tăng sau 6 tuần thực nghiệm. |
| **Giáo viên có hỗ trợ tốt hơn?** | % Intervention Success | Alert vs Log sync | Các case "Inactivity" giảm nhanh sau khi có Alert trên Dashboard. |

---

## 4. Các bước triển khai để "Chứng minh" (Next Steps)

1.  **Tuần 2 (Pilot)**: Thiết lập nhóm đối chứng (Control Group) - cho các em này dùng AI tự do nhưng vẫn yêu cầu log lại câu hỏi/đáp án để so sánh.
2.  **Tuần 3**: Chạy code `behavior_analysis.py` để lấy Ma trận Markov của cả 2 nhóm.
    - Kỳ vọng: Nhóm GPS có ma trận tập trung ở đường chéo G-P-S; Nhóm tự do có ma trận lộn xộn.
3.  **Tuần 6**: Thực hiện Post-test và chạy full script báo cáo clustering để chỉ ra sự khác biệt về chân dung học tập giữa 2 nhóm.

---

## 5. Cấu trúc dữ liệu bổ sung (Data Schema Update)
Để chứng minh tốt nhất, tab `Raw Data` cần có thêm:
- Cột `Group`: `Experimental` hoặc `Control`.
- Cột `Session ID`: Để nhóm các câu hỏi cùng một bài toán (giúp tính `Scaffolding Efficiency`).
