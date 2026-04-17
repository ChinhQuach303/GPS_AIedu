# NHẬT KÝ PHẢN BIỆN NGHIÊN CỨU (DEFENSE Q&A) - AIedu PROJECT

Tài liệu này tổng hợp toàn bộ các câu hỏi phản biện từ Giáo viên hướng dẫn (Supervisor) và câu trả lời của Nhà nghiên cứu trong suốt quá trình 6 tuần triển khai dự án.

---

## TUẦN 1: NỀN TẢNG VÀ THIẾT LẬP HÊ THỐNG

**Câu hỏi 1: Tại sao bạn lại chọn mô hình G.P.S gồm 3 bước G-P-S mà không phải là một mô hình gợi ý thông thường?**
**Trả lời:** Bước [P] Practice (Thực hành) là chốt chặn quan trọng. Nó bắt học sinh phải chứng minh năng lực tái tạo tư duy qua một bài toán tương tự trước khi nhận lời giải [S]. Điều này ngăn chặn việc học sinh chỉ đọc lời giải mà không thực sự hiểu bản chất.

**Câu hỏi 2: Làm thế nào bạn ngăn chặn được việc học sinh "jailbreak" (lách luật) để AI đưa ra đáp án ngay lập tức?**
**Trả lời:** Sử dụng "Negative Constraints" trong System Prompt và cơ chế giám sát nhãn [S]. Nếu AI đưa ra lời giải mà không có lịch sử bước [P], hệ thống sẽ đánh dấu là vi phạm quy trình sư phạm.

**Câu hỏi 3: Bạn định nghĩa thế nào là một "Gợi ý tốt" (Good Hint) trong bước [G] Guide?**
**Trả lời:** Là gợi ý chiến lược, tập trung vào bản chất logic (Ví dụ: "Thứ tự có quan trọng không?") thay vì gợi ý tính toán trực tiếp.

**Câu hỏi 4: Độ chi tiết (Granularity) của Prompt tuần 1 được thiết kế ra sao?**
**Trả lời:** Sử dụng "Few-shot Prompting" với các ví dụ mẫu cụ thể để AI hiểu ranh giới từng bước và cấu trúc Output Format bắt buộc.

**Câu hỏi 5: Tại sao dùng Student Hash thay vì tên thật?**
**Trả lời:** Đạo đức nghiên cứu (Research Ethics) và tính khách quan. Hash giúp bảo mật danh tính nhưng vẫn cho phép theo dõi lịch sử độc lập.

---

## TUẦN 2: TRIỂN KHAI PILOT VÀ DÒNG CHẢY DỮ LIỆU

**Câu hỏi 6: Tại sao dùng Google Apps Script (GAS) thay vì SQL?**
**Trả lời:** Tính linh hoạt (Agility) trong giai đoạn Pilot. GAS cho phép triển khai nhanh, tích hợp sẵn với Google Workspace mà giáo viên đang sử dụng.

**Câu hỏi 7: Xử lý lỗi "Nhãn nhầm" (Label Mismatch) như thế nào?**
**Trả lời:** Sử dụng Regex kiểm tra chéo độ dài tin nhắn và ngữ cảnh. Các nhãn không nhất quán sẽ bị đánh dấu "Inconsistent Flow".

**Câu hỏi 8: Xử lý vấn đề "Độ trễ" (Latency) dữ liệu?**
**Trả lời:** Sử dụng "Asynchronous Logging". Trải nghiệm chat không bị gián đoạn, giáo viên chỉ cần độ trễ 2-3 giây để theo dõi Dashboard.

**Câu hỏi 9: Học sinh có "mồi" AI để lấy gợi ý sát đáp án không?**
**Trả lời:** Có quan sát thấy hành vi này, nhưng bước [P] bắt buộc đã chặn đứng hiệu quả của việc "mồi". Học sinh vẫn phải tự giải bài tập thực hành.

---

## TUẦN 3: CÔNG CỤ PHÂN TÍCH HÀNH VI

**Câu hỏi 10: Tại sao dùng Python thay vì Google Sheets để phân tích?**
**Trả lời:** Để thực hiện các thuật toán phức tạp như Markov Chain và Clustering một cách tự động và chính xác, Sheets không đủ khả năng xử lý đa chiều dữ liệu.

**Câu hỏi 11: Tỷ lệ [S] chỉ chiếm 15% là cao hay thấp?**
**Trả lời:** Thấp là tích cực trong giai đoạn đầu, vì nó chứng minh học sinh đang dành nhiều thời gian cho chu kỳ G-P (Tư duy sâu) thay vì chỉ lấy đáp án.

**Câu hỏi 12: Xử lý "Dữ liệu nhiễu" (Noise) như thế nào?**
**Trả lời:** Bộ lọc Regex loại bỏ interact không gán nhãn [G/P/S] và loại bỏ các phiên chat có thời gian quá ngắn (Low Quality Data).

**Câu hỏi 13: Mẫu hình Markov tuần 3 hé lộ điều gì?**
**Trả lời:** Xác suất P -> G (25%) cho thấy học sinh gặp khó khăn ở thực hành. Việc quay lại [G] giúp giảm căng thẳng học tập và tăng tính kiên trì.

---

## TUẦN 4: PHÂN CỤM VÀ NHẬN DIỆN RỦI RO

**Câu hỏi 14: K-means Clustering phản ánh điều gì ngoài điểm số?**
**Trả lời:** Phản ánh "Trình độ tương tác" và "Thái độ học tập". Giúp nhận diện học sinh lười nhưng giỏi hoặc học sinh chăm nhưng bế tắc.

**Câu hỏi 15: Khác biệt Markov giữa Fast-Learner và Backtracker?**
**Trả lời:** Nhóm Fast-Learner có xác suất P -> S = 0.85. Nhóm Backtracker có xác suất P -> G hoặc P -> P > 50%.

**Câu hỏi 16: Biểu đồ PCA có ý nghĩa gì?**
**Trả lời:** Chỉ ra các nhân tố quan trọng nhất tạo nên sự khác biệt: Sự kết hợp giữa Thời gian suy nghĩ và Tỷ lệ vượt qua bước P.

**Câu hỏi 17: Tại sao can thiệp G.U.I.D.E ở tuần 4 lại hiệu quả?**
**Trả lời:** Vì giáo viên được cung cấp "Danh sách can thiệp" (Alerts) định hướng đúng đối tượng 20% học sinh At-risk, thay vì giám sát đại trà.

---

## TUẦN 5: TỰ CHỦ VÀ "RÚT GIÀN GIÁO"

**Câu hỏi 18: Rủi ro của Faded Scaffolding (Rút giàn giáo)?**
**Trả lời:** Nguy cơ học sinh nản lòng khi độ khó tăng. Giải pháp là giám sát chặt Independence Index và can thiệp kịp thời nếu nó giảm quá sâu.

**Câu hỏi 19: Tầm quan trọng của Reflection (Phản tư) bắt buộc?**
**Trả lời:** Phá vỡ sự "Hiểu giả tạo". Học sinh phải diễn đạt lại bằng ngôn ngữ cá nhân để chứng minh đã nội hóa kiến thức.

**Câu hỏi 20: Kỳ vọng Independence Index ở tuần 5?**
**Trả lời:** Kỳ vọng tăng từ 0.29 lên mức > 1.0 khi số lượng gợi ý [G] giảm và số lần giải quyết [S] độc lập tăng lên.

**Câu hỏi 21: Làm sao biết học sinh dùng AI khác để viết Phản tư?**
**Trả lời:** Kiểm tra Sequence Chaos Index. Sự hoàn hảo bất thường mà không có bước chuẩn bị trước đó sẽ bị đánh dấu là "Abnormal".

---

## TUẦN 6: TỔNG KẾT VÀ BẢO VỆ NGHIÊN CỨU

**Câu hỏi 22: Tại sao dùng ANCOVA thay vì t-test?**
**Trả lời:** Để loại bỏ sai số do trình độ đầu vào (Pre-test), đảm bảo sự tiến bộ thực sự là do mô hình G.P.S chứ không phải nền tảng sẵn có của học sinh.

**Câu hỏi 23: Ý nghĩa của Cohen's d lớn (> 1.0)?**
**Trả lời:** Khẳng định phương pháp G.P.S có tác động thực tiễn rất mạnh mẽ, vượt xa các biến động ngẫu nhiên trong dạy học thông thường.

**Câu hỏi 24: Ma trận Graduation chứng minh điều gì?**
**Trả lời:** 60% học sinh nhóm At-risk đã chuyển đổi hồ sơ thành công sang nhóm Normal/Independent. Đây là thành công lớn nhất về mặt nhân văn của dự án.

**Câu hỏi 25: Hạn chế và hướng phát triển?**
**Trả lời:** Hạn chế về mẫu nhỏ (N=60). Hướng tới AI có khả năng "Adaptive Scaffolding" — tự động rút giàn giáo theo tốc độ riêng của từng học sinh.
