# BÁO CÁO TIẾN ĐỘ TUẦN 1
**Dự án: Ứng dụng mô hình G.P.S. và quy trình G.U.I.D.E trong dạy học Toán THPT với sự hỗ trợ của AI**

---

## 1. Tóm tắt kết quả đạt được
Trong Tuần 1 (Xây dựng nền tảng), nhóm đã hoàn thành đúng hạn 100% các hạng mục công việc đề ra, thiết lập thành công hệ sinh thái công cụ hỗ trợ nghiên cứu và tài liệu sư phạm.

## 2. Các hạng mục chi tiết

### a. Nền tảng kỹ thuật & Tự động hóa
- **Data Schema & Bảo mật**: Xây dựng cấu chuẩn dữ liệu (JSON) cho nhật ký học tập. Triển khai cơ chế **Hash + Salt** để ẩn danh hóa mã số học sinh, đảm bảo đạo đức nghiên cứu.
- **Google Apps Script**: Hoàn thiện script tự động gán nhãn (Guide/Practice/Solve) dựa trên từ khóa và gửi email cảnh báo tự động nếu học sinh ngừng tương tác sau 3 ngày.
- **Hệ thống Dashboard**: Thiết lập bộ công thức Google Sheets tự động hóa (Pivot Tables, COUNTIFS) để theo dõi thời gian thực các chỉ số: tỷ lệ G/P/S, mức độ hài lòng và biểu đồ tương tác theo thời gian.

### b. Nội dung sư phạm (AI Pedagogy)
- **Hệ thống System Prompt**: Xây dựng "Brain" cho AI với tên gọi **G.P.S Tutor**, tuân thủ nghiêm ngặt quy tắc: *Hướng dẫn phương pháp (Guide), Hỗ trợ luyện tập (Practice), và Kiểm tra độc lập (Solve)* thay vì giải hộ bài tập.
- **Ngân hàng Prompt mẫu**: Soạn thảo 45 bộ prompt mẫu (15 bộ/bước) cho chương Tổ hợp & Xác suất (Toán 11), đảm bảo bao phủ các dạng bài tập thực tế.

### c. Tài liệu nghiên cứu & Pháp lý
- **Đề cương nghiên cứu (v1.0)**: Cập nhật chi tiết quy trình thực nghiệm và các tiêu chí validation.
- **Thang đo MSLQ**: Dịch thuật và chuẩn hóa 20 câu hỏi về siêu nhận thức và quản lý học tập sang tiếng Việt.
- **Hồ sơ pháp lý**: Hoàn thành Phiếu đồng thuận (Consent Form) và Chính sách bảo mật dữ liệu dành cho phụ huynh và học sinh.

## 3. Hoạt động Kiểm Thử (Validation)
- Đã thực hiện kiểm thử nội bộ với **20 dữ liệu giả lập (Mock Data)**.
- Kết quả: Hệ thống gán nhãn đạt độ chính xác **> 90%** trên các mẫu rõ ràng. Dashboard cập nhật dữ liệu đúng quy trình.
- Đã thiết lập tiêu chí đánh giá Kappa (>0.8) cho việc gán nhãn thủ công bởi cộng tác viên.

## 4. Quản lý mã nguồn
- Toàn bộ dữ liệu và mã nguồn đã được đóng gói và lưu trữ trên GitHub tại: `https://github.com/ChinhQuach303/GPS_AIedu.git`

## 5. Kế hoạch Tuần 2
- Triển khai giai đoạn **Pilot (thử nghiệm diện hẹp)**.
- Tập huấn cho học sinh về cách tương tác theo mô hình G.P.S.
- Thu thập và hiệu chỉnh công cụ dựa trên phản hồi thực tế.

---
*Ngày báo cáo: 13/03/2026*
*Người thực hiện: Nhóm Nghiên cứu GPS-AI*
