# Kế hoạch Kiểm thử Nội bộ - Tuần 1 (v1.0)

> Gợi ý tự động hóa: dùng menu **GPS QA** (Apps Script) để tạo dữ liệu mock “như thật” và chạy smoke test tự động. Xem thêm `docs/research/week1_workflow.md`.

## 1. Đối tượng kiểm thử
- Hệ thống thu thập dữ liệu (Google Form -> Sheet)
- Logic tự động gán nhãn (Apps Script)
- Logic cảnh báo (Email alerts)
- Dashboard hiển thị dữ liệu

## 2. Checklist kiểm thử (Pass/Fail)

| ID | Bước kiểm thử | Kết quả kỳ vọng | Trạng thái |
| :--- | :--- | :--- | :--- |
| **TC-01** | Nhập liệu đồng loạt | Dùng `GPS QA → Seed Realistic Mock Data` để tạo dữ liệu trực tiếp trong Sheet (hoặc tự nhập/bơm dữ liệu test). | [ ] |
| **TC-02** | Gán nhãn tự động | Apps Script gán nhãn đúng > 90% các mẫu G/P/S rõ ràng. | [ ] |
| **TC-03** | Tính ẩn danh | Student ID được thay thế bằng Hash+Salt trong Sheet công khai. | [ ] |
| **TC-04** | Cảnh báo 3 ngày | Giả lập 1 HS không nộp bài 3 ngày -> Kiểm tra email có gửi không. | [ ] |
| **TC-05** | Dashboard Update | Biểu đồ tự nhảy khi dữ liệu mới được nhập vào. | [ ] |

## 3. Dữ liệu Test (Mock Data)
Có 2 cách tạo dữ liệu test:
1) **Trong Google Sheets (khuyến nghị)**: dùng menu **GPS QA → Seed Realistic Mock Data** để sinh dữ liệu “như thật” (nhiều kiểu học sinh) và chạy **GPS QA → Run Week1 Smoke Test**.
2) **Local (phục vụ demo/phân tích)**: sinh dữ liệu theo schema bằng `src/tools/generate_mock_week1.py` và kiểm thử bằng `src/tools/week1_smoke_test.py`.

## 4. Pass Criteria
- Toàn bộ 5 test case trên đạt trạng thái passed.
- Độ chính xác gán nhãn > 90% (nếu < 90% cần cập nhật rule trong `src/tools/gas_script.js`).
