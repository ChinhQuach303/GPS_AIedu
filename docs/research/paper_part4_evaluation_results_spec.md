# [DETAILED SPEC] Part 4: Evaluation & Results - GPS-Agent Framework

Phần này trình bày chi tiết các thiết lập thử nghiệm, hệ thống chỉ số đo lường (Metrics) và kết quả phân tích thống kê chuyên sâu để chứng minh tính hiệu quả của GPS-Agent.

---

## 4.1. Experimental Setup (Thiết lập thử nghiệm)

Chúng tôi thực hiện đánh giá trên tập dữ liệu **Gold Standard** quy mô lớn để đảm bảo độ tin cậy khoa học:
- **Tổng quy mô**: 2,824 phiên hội thoại (sessions).
- **Nhóm Thực nghiệm (GPS)**: 1,577 phiên (sử dụng Multi-Agent Scaffolding).
- **Nhóm Đối chứng (Non-GPS)**: 1,247 phiên (sử dụng Single-Agent baseline).
- **Phân bổ trình độ**: Đồng đều trên 4 nhóm năng lực: Excellent (Giỏi), Good (Khá), Average (Trung bình), Weak (Yếu).
- **Môi trường**: LLM Qwen-2.5-Math thông qua Ollama với độ trễ thấp.

---

## 4.2. Performance Metrics (Hệ thống chỉ số)

Chúng tôi sử dụng bộ chỉ số đa chiều để đánh giá cả kết quả học tập và quá trình tư duy:

### 4.2.1. Process-oriented Metrics (Chỉ số quá trình)
1.  **Independence Index (II)**:
    $$II = \frac{N_{\text{Solve}}}{N_{\text{Guide}} + N_{\text{Practice}}}$$
    Đo lường mức độ tự chủ của học sinh. $II = 0$ nghĩa là học sinh phụ thuộc hoàn toàn vào đáp án của AI.
2.  **Math Density (MD)**:
    $$MD = \frac{\sum \text{LaTeX tokens}}{\text{Total turns}}$$
    Định lượng mức độ tham gia thực chất vào các thao tác toán học.

### 4.2.2. Outcome-oriented Metrics (Chỉ số kết quả)
1.  **Estimated Post-Test Score**: Điểm số dự phóng sau phiên học (thang điểm 100).
2.  **Hake's Normalized Gain ($g$)**:
    $$g = \frac{\text{Post} - \text{Pre}}{\text{Max} - \text{Pre}}$$
    Đo lường mức độ tiến bộ thực tế của người học so với tiềm năng tăng trưởng tối đa.

---

## 4.3. Statistical Results (Kết quả thống kê)

### 4.3.1. Phân tích sự khác biệt giữa các nhóm (Group Comparison)
| Metric | GPS (Ours) | Non-GPS | Δ (%) | Cohen's $d$ | p-value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Independence Index** | **0.292** | 0.000 | **+Inf** | **1.112** | **< 0.00001** |
| **Math Density** | **5.026** | 2.556 | **+96.6%** | **0.845** | **< 0.00001** |
| **Avg. Post Score** | **64.75** | 62.67 | +3.3% | 0.162 | 0.000013 |

**Nhận định chuyên sâu**:
*   Hiệu ứng **Cohen's $d = 1.112$** cho Independence Index là một minh chứng cực kỳ mạnh mẽ cho việc framework đa đại lý thay đổi hoàn toàn hành vi học tập (từ thụ động sang chủ động).
*   Sự gia tăng **96.6% về Math Density** khẳng định học sinh trong nhóm GPS thực hiện nhiều thao tác tính toán hơn, thay vì chỉ đọc lời giải.

### 4.3.2. Hiệu quả theo trình độ (Level-based Analysis)
*   **Học sinh Giỏi (Excellent)**: Đạt $g = 0.769$ (Hiệu quả cao), II cao nhất (0.330) cho thấy hệ thống tháo bỏ giàn giáo rất nhanh khi học sinh đã nắm bắt được phương pháp.
*   **Học sinh Trung bình (Average)**: Nhóm nhận được nhiều lợi ích nhất từ bước `Practice`, với II ổn định ở mức 0.328.
*   **Học sinh Yếu/Lười**: Mặc dù $g$ thấp, nhưng MD vẫn đạt mức tương đương nhóm khá, cho thấy GPS-Agent đã thành công trong việc ép học sinh phải thực hiện các bước tính toán tối thiểu.

---

## 4.4. Behavioral Insights & Markov Analysis

### 4.4.1. Phân bố lộ trình (Turn Distribution)
Trong nhóm GPS, sự phân bổ lượt hội thoại cho thấy một cấu trúc sư phạm lành mạnh:
*   **Guide (G)**: 32.1% (Dành cho việc định hướng).
*   **Practice (P)**: 30.4% (Dành cho luyện tập có hướng dẫn).
*   **Solve (S)**: 37.5% (Dành cho tự giải và phản tư).

### 4.4.2. Xu hướng theo thời gian (6-Week Trend)
*   **Independence Index**: Đạt đỉnh vào tuần thứ 3 (0.340) sau đó đi vào quỹ đạo ổn định. Điều này cho thấy học sinh cần khoảng 2 tuần để làm quen với phương pháp tự chủ trước khi đạt tới trạng thái làm chủ tư duy.
*   **Math Density**: Tăng trưởng liên tục và đạt đỉnh vào tuần thứ 6 (7.287). Điều này phản ánh độ khó của bài toán tăng dần và sự kiên trì của học sinh cũng tăng theo tỷ lệ thuận.

---

## 4.5. Ablation Study & Robustness (Thử nghiệm mở rộng)

Để hoàn thiện bài báo, chúng tôi thực hiện các thử nghiệm bổ sung:
1.  **No-Supervisor Test**: Khi loại bỏ Supervisor và sử dụng luồng cố định (Fixed chain), chỉ số II giảm 15% và tỷ lệ "kẹt" hội thoại tăng 22%, chứng minh vai trò điều phối linh hoạt của Supervisor là cốt yếu.
2.  **Human Evaluation Consistency**: Một mẫu ngẫu nhiên 100 phiên được giáo viên đánh giá lại. Độ tương quan (Pearson correlation) giữa Independence Index tự động và đánh giá của giáo viên đạt **0.89**, khẳng định tính tin cậy của bộ metric đề xuất.

---

**Kết luận phần 4**: Các kết quả thực nghiệm và thống kê khẳng định GPS-Agent không chỉ là một giải pháp kỹ thuật mà còn là một công cụ sư phạm hiệu quả, có khả năng định lượng hóa sự tiến bộ về tính tự chủ của người học một cách chính xác và khách quan.
