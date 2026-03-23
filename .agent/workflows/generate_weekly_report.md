---
description: Tự động chạy báo cáo phân tích hành vi hàng tuần (behavior analysis)
---
# Báo cáo hàng tuần (Weekly Behavior Analysis Report)

Quy trình này sẽ tự động tải log mới nhất từ Google Sheets và dùng script Python để phân tích chuyên sâu (Markov Chain, K-Means Clustering), sau đó xuất kết quả vào các biểu đồ và báo cáo.

1. Chạy quá trình tải dữ liệu thô từ Google Sheets ẩn danh về file `raw_data.csv` (nếu script hỗ trợ, hoặc lấy từ snapshot hệ thống).
// turbo
2. Chạy thư viện phân tích hành vi bằng Python 3, đầu ra là các file đồ thị (PNG) và file phân nhóm (CSV).
```bash
python3 src/analysis/behavior_analysis.py
```
3. Tổng hợp báo cáo vào `docs/research/bao_cao_tuan_X.md` với các file hình ảnh đính kèm.
