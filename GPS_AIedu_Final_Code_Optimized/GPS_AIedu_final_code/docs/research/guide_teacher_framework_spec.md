# GUIDE Framework Specification: AI-Assisted Teacher Intervention

Tài liệu này đặc tả khung **GUIDE** dành riêng cho giáo viên để quản lý lớp học và tối ưu hóa hiệu quả sư phạm của GPS-Agent.

---

## 1. Overview: The Role of the Teacher
Trong hệ thống GPS-AIedu, giáo viên không còn là người truyền thụ kiến thức duy nhất mà đóng vai trò là **Facilitator** (Người điều phối) và **Specialist** (Chuyên gia can thiệp). Khung GUIDE cung cấp quy trình 5 bước để giáo viên tận dụng dữ liệu từ AI nhằm cá nhân hóa việc học.

---

## 2. The G.U.I.D.E Protocol (Quy trình 5 bước)

### G - Gather (Thu thập dữ liệu)
*   **Mục tiêu**: Thu thập toàn bộ vết (traces) hội thoại và các metrics từ các phiên học của học sinh.
*   **Kỹ thuật**: 
    - Truy vấn dữ liệu từ SQLite/Logs (`Independence_Index`, `Math_Density`, `GPS_Step`).
    - Ghi nhận các phản hồi (Ratings) của học sinh về độ khó và chất lượng gợi ý của AI.

### U - Understand (Thấu hiểu hành vi)
*   **Mục tiêu**: Chuyển đổi dữ liệu thô thành thông tin sư phạm (Insights) cấp cao.
*   **Kỹ thuật nâng cao**: 
    - **Student Segmentation (PCA Clustering)**: Sử dụng thuật toán phân cụm (như K-Means) trên các đặc trưng `II`, `MD`, và `Post-Score` để chia học sinh thành các nhóm hành vi (Archetypes) như "Independent Mastery", "Diligent Scaffolder", hoặc "Passive Consumer".
    - **Markov Chain Transition Analysis**: Xây dựng ma trận chuyển trạng thái (G→P, P→S, G→S) cho từng cụm học sinh. Việc này giúp xác nhận "Cognitive Friction" (Ma sát tư duy) nằm ở giai đoạn nào (ví dụ: nhóm Yếu thường bị kẹt ở vòng lặp G→G).

### I - Intervene (Can thiệp kịp thời)
*   **Mục tiêu**: Hỗ trợ học sinh dựa trên đặc điểm của từng cụm hành vi.
*   **Kỹ thuật**: 
    - **Early Warning System (EWS)**: Tự động phát cảnh báo SOS nếu Markov Trace của một học sinh cho thấy các vòng lặp bế tắc (v.d. quay lại [G]uide quá 3 lần).
    - **Cluster-based Intervention**: 
        - Nhóm "Dependent": Giáo viên tập trung vào việc khích lệ (Motivate) để tăng II.
        - Nhóm "Struggling": Giáo viên can thiệp vào kiến thức nền (Knowledge Gap) dựa trên các bước [P] bị lỗi.

### D - Discuss (Thảo luận & Kết nối)
*   **Mục tiêu**: Chuyển đổi tương tác AI-Người sang Người-Người để củng cố kiến thức.
*   **Kỹ thuật**: 
    - Sử dụng các ví dụ hay (High II) từ hệ thống để thảo luận trước lớp.
    - Tổ chức thảo luận nhóm dựa trên các chiến lược giải bài khác nhau mà học sinh đã dùng trong bước `[S]olve`.

### E - Evaluate (Đánh giá & Điều chỉnh)
*   **Mục tiêu**: Đo lường hiệu quả của cả quá trình học và quá trình can thiệp.
*   **Kỹ thuật**: 
    - So sánh `Hake's Gain` trước và sau khi giáo viên can thiệp.
    - Điều chỉnh System Prompt của các Agent nếu dữ liệu cho thấy tỷ lệ học sinh bị "kẹt" (loops) quá cao.

---

## 3. Teacher Dashboard Specifications (Yêu cầu bảng điều khiển)

Bảng điều khiển dành cho giáo viên phải hiển thị các thành phần sau:

1.  **Lớp học thời gian thực (Live View)**: Danh sách học sinh kèm nhãn trạng thái GPS hiện tại.
2.  **Heatmap tự chủ (Autonomy Heatmap)**: Thể hiện sự biến thiên của II qua các tuần.
3.  **Knowledge Gap Cloud**: Các từ khóa/dạng bài học sinh thường xuyên phải quay lại bước `[G]`.
4.  **Actionable Alerts**: Nút "Yêu cầu giáo viên" xuất hiện khi EWS kích hoạt.

---

## 4. Synergy between GPS and GUIDE

| G.U.I.D.E Step | Corresponding GPS Trace | Teacher Action |
| :--- | :--- | :--- |
| **Understand** | High [G] frequency | Review the core concept of that QID. |
| **Intervene** | Repeated [P] failures | Direct 1-1 scaffolding for the student. |
| **Evaluate** | [S] response quality | Check for plagiarism or deep understanding. |

---

Bản đặc tả này sẽ giúp bài báo EMNLP có thêm một phần quan trọng về **"Human-AI Collaboration"**, chứng minh rằng AI không thay thế giáo viên mà làm tăng năng lực của họ. Bạn có muốn tôi tích hợp thêm phần này vào bản thảo chính không?
