BÁO CÁO TUẦN 2
Trong tuần thứ hai, tôi tiếp tục hoàn thiện hệ thống thu thập dữ liệu tự động và tiến hành kiểm thử toàn bộ quy trình bằng dữ liệu giả lập. Mục tiêu là đảm bảo hệ thống hoạt động ổn định trước khi triển khai cho học sinh sử dụng thực tế. Dưới đây là các bước đã thực hiện.
Bước 1: Hoàn thiện kho dữ liệu trung tâm
Sử dụng Google Sheet làm nơi lưu trữ tương tác giữa học sinh và AI
Kiểm tra và điều chỉnh lại cấu trúc bảng để đảm bảo lưu trữ đầy đủ các thông tin như: thời gian, ID học sinh, câu hỏi, câu trả lời của AI, mức độ hài lòng, nhãn phân loại, v.v.
Đảm bảo dữ liệu được ghi nhận đúng định dạng để thuận tiện cho việc tổng hợp và phân tích sau này.
Bước 2: Kiểm thử bộ phận xử lý tự động bằng Google Apps Script
Kiểm tra lại script nhận dữ liệu từ webchat và ghi vào Google Sheet.
Thử nghiệm cơ chế phân loại câu hỏi thành ba dạng:
G (Hỏi để hiểu)


P (Hỏi để luyện tập)


S (Hỏi để kiểm tra)


Nếu hệ thống chưa xác định được thì tạm gán nhãn Unknown.
Đồng thời kiểm tra cơ chế mã hóa thông tin học sinh bằng mã số để đảm bảo khả năng ẩn danh khi cần.

Bước 3: Kiểm tra giao diện chat cho học sinh (Webchat)
Thử nghiệm trang webchat đã xây dựng:
Kiểm tra việc nhập ID học sinh và gửi câu hỏi cho AI.


Kiểm tra việc hệ thống tự động gửi toàn bộ nội dung cuộc trò chuyện về Google Sheet.


Đảm bảo học sinh không cần thao tác thủ công để ghi dữ liệu.


Thử nghiệm hai phương án sử dụng AI:
sử dụng API qua Internet


sử dụng AI chạy trên máy chủ cục bộ (Ollama)


Mục tiêu là đảm bảo hệ thống có thể hoạt động linh hoạt tùy theo điều kiện thiết bị.
Bước 4: Kiểm tra bảng theo dõi (Dashboard)
Rà soát lại các tab dashboard trong Google Sheet để đảm bảo dữ liệu hiển thị chính xác.
Các phần chính gồm:
tab hiển thị thông tin từng học sinh (số lần chat, tỷ lệ câu hỏi G-P-S, thời gian hoạt động gần nhất)


tab tổng hợp toàn lớp bằng biểu đồ


tab lọc ra các trường hợp cần lưu ý (ít tương tác, câu hỏi chưa phân loại, mức độ hài lòng thấp)


Các dashboard này giúp giáo viên có thể theo dõi nhanh tình hình học tập khi hệ thống được triển khai thực tế.
Bước 5: Kiểm thử quy trình với dữ liệu giả lập
Tiếp tục sử dụng các nhóm học sinh giả với các hành vi khác nhau (giỏi, trung bình, chậm, hay xin đáp án, nghỉ dài) để chạy thử hệ thống.
Thực hiện nhiều lượt hỏi qua webchat để mô phỏng quá trình học sinh tương tác với AI.
Kiểm tra toàn bộ quy trình:
dữ liệu có được ghi đúng vào Google Sheet không


phân loại câu hỏi có hoạt động không


dashboard có cập nhật đúng không


Kết quả cho thấy hệ thống hoạt động ổn định và dữ liệu được ghi nhận đầy đủ.
Bước 6: Hoàn thiện tài liệu hướng dẫn
Tiếp tục hoàn thiện bộ tài liệu hướng dẫn để nhà trường có thể triển khai hệ thống.
Bao gồm:
hướng dẫn cài đặt nhanh cho bộ phận kỹ thuật


kịch bản tập huấn học sinh (20–30 phút)


bộ 45 câu hỏi mẫu theo ba dạng G-P-S để học sinh tham khảo



Kết quả đạt được sau tuần 2
Sau hai tuần chuẩn bị, dự án đã xây dựng được:
Một quy trình hoàn chỉnh: học sinh chat → dữ liệu tự động lưu → giáo viên theo dõi qua bảng tổng hợp.


Một Google Sheet làm kho dữ liệu trung tâm kèm dashboard theo dõi.


Một trang webchat có thể triển khai ngay khi cần.


Hệ thống đã được kiểm thử bằng dữ liệu giả lập và hoạt động ổn định.


Bộ tài liệu hướng dẫn và kịch bản tập huấn đã được chuẩn bị.


Kế hoạch tuần 3
Trong tuần tới, dự án sẽ tiếp tục tập trung vào hoàn thiện hệ thống trước khi triển khai thực tế.
Các hoạt động dự kiến gồm:
Hoàn thiện các thành phần kỹ thuật của hệ thống webchat và Google Apps Script.


Kiểm tra lại toàn bộ quy trình ghi dữ liệu và phân loại câu hỏi.


Tiếp tục kiểm thử với dữ liệu giả lập để phát hiện và sửa lỗi nếu có.


Điều chỉnh dashboard để việc theo dõi dữ liệu thuận tiện hơn cho giáo viên.


Hoàn thiện tài liệu hướng dẫn triển khai.


Sau khi các bước này được hoàn tất và hệ thống hoạt động ổn định, dự án sẽ xem xét triển khai thử nghiệm với học sinh trong giai đoạn tiếp theo

