# Chiến lược Làm sạch Dữ liệu Hội thoại (Data Cleaning Pipeline)

Mục tiêu: Chuyển đổi dữ liệu hội thoại từ dạng "AI sinh thô" sang dạng "Hội thoại Sư phạm chuyên nghiệp", loại bỏ các dấu vết máy móc (AI artifacts).

## 1. Chuẩn hóa Định dạng (Format Normalization)
- **Thống nhất nhãn xưng hô**: Chuyển toàn bộ các nhãn như `AI:`, `Tutor:`, `Thầy giáo:` thành `Thầy:`. Chuyển `Student:`, `Học sinh:`, `Hội thoại:` thành `Em:`.
- **Cấu trúc dòng**: Mỗi lượt thoại bắt đầu bằng `Thầy:` hoặc `Em:` và xuống dòng rõ ràng.

## 2. Làm sạch Ngôn ngữ (Linguistic Cleaning)
- **Loại bỏ Chào hỏi lặp lại**: 
    - Giữ lại câu chào "Chào em", "Thầy chào em" ở lượt thoại đầu tiên.
    - Tự động xóa bỏ các câu chào này nếu chúng xuất hiện từ lượt thoại thứ 2 trở đi để hội thoại diễn ra tự nhiên hơn.
- **Xóa bỏ Văn bản thừa (Clutter Removal)**:
    - Loại bỏ các đoạn như "Dưới đây là...", "Câu hỏi:", "Hãy cùng thực hiện...", "Em có thắc mắc gì không?" ở cuối các lượt thoại nếu chúng mang tính chất máy móc.
    - Cắt bỏ các câu bị dở dang (truncated sentences) do giới hạn token.
- **Xử lý "AI Meta-talk"**: Xóa các câu AI tự nhận xét về bản thân như "Thầy hiểu rồi, em làm đúng rồi" nếu nó xuất hiện lặp lại quá 2 lần trong một session.

## 3. Bảo toàn Tri thức (Knowledge Integrity)
- **Giữ nguyên LaTeX**: Sử dụng Regex để bảo vệ các khối lệnh `$...$`, `$$...$$`, `\[...\]`. Tuyệt đối không thay đổi nội dung bên trong các khối này.
- **Xử lý Nhãn GPS**: 
    - Đối với tập GPS, loại bỏ các nhãn `[G]`, `[P]`, `[S]` trong nội dung text nhưng lưu trữ chúng vào một cột riêng (`pedagogical_label`) để phục vụ phân tích. Điều này giúp hội thoại trông giống người thật hơn.

## 4. Kiểm soát Chất lượng (Quality Filtering)
- **Lọc Session lỗi**: Loại bỏ các phiên hội thoại:
    - Có số lượt chat < 3 (quá ngắn, chưa kịp học).
    - Có số lượt chat > 15 (có dấu hiệu bị loop).
    - Chứa ký tự lạ (Tiếng Trung, Tiếng Anh bị lẫn vào).

## 5. Quy trình Thực hiện
1. Viết script `scripts/clean_data_pipeline.py`.
2. Chạy thử nghiệm trên 5 mẫu của mỗi tập dữ liệu (GPS và Baseline).
3. Sau khi User phê duyệt mẫu đã clean, sẽ tiến hành chạy hàng loạt (Batch process).
4. Xuất file kết quả ra: `data/outputs/cleaned_massive_results.csv` và `data/outputs/cleaned_baseline_results.csv`.
