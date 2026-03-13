# Kế hoạch Kiểm thử Nội bộ - Tuần 1 (v1.0)

## 1. Đối tượng kiểm thử
- Hệ thống thu thập dữ liệu (Google Form -> Sheet)
- Logic tự động gán nhãn (Apps Script)
- Logic cảnh báo (Email alerts)
- Dashboard hiển thị dữ liệu

## 2. Checklist kiểm thử (Pass/Fail)

| ID | Bước kiểm thử | Kết quả kỳ vọng | Trạng thái |
| :--- | :--- | :--- | :--- |
| **TC-01** | Nhập liệu đồng loạt | 20 bản ghi từ `mock_week1.csv` đổ về Sheet không lỗi. | [ ] |
| **TC-02** | Gán nhãn tự động | Apps Script gán nhãn đúng > 90% các mẫu G/P/S rõ ràng. | [ ] |
| **TC-03** | Tính ẩn danh | Student ID được thay thế bằng Hash+Salt trong Sheet công khai. | [ ] |
| **TC-04** | Cảnh báo 3 ngày | Giả lập 1 HS không nộp bài 3 ngày -> Kiểm tra email có gửi không. | [ ] |
| **TC-05** | Dashboard Update | Biểu đồ tự nhảy khi dữ liệu mới được nhập vào. | [ ] |

## 3. Dữ liệu Test (Mock Data)
Sử dụng file `data/raw/mock_week1.csv` chứa 20 mẫu tương tác phân bổ:
- 7 mẫu Guide (hỏi lý thuyết, phương pháp)
- 8 mẫu Practice (hỏi bước giải, gợi ý)
- 5 mẫu Solve (nhờ kiểm tra bài làm)

## 4. Pass Criteria
- Toàn bộ 5 test case trên đạt trạng thái passed.
- Độ chính xác Regex > 90% (nếu < 90% cần điều cập nhật `gas_script.js`).
