# Dashboard Formulas – GPS AIedu
*Dựa trên column layout của `gas_script.js`: B=StudentID, F=Question, I=Satisfaction, J=Difficulty, L=AutoLabel, M=Hash*

---

## Tab: Per Student

Đặt header ở hàng 1, dữ liệu bắt đầu từ A2.

| Cột | Header | Công thức (ví dụ cho A2) |
|-----|--------|--------------------------|
| A | Student Hash | Điền tay hoặc lấy từ danh sách `Raw Data` |
| B | Total Logs | `=COUNTIF('Raw Data'!M:M, A2)` |
| C | G Count | `=COUNTIFS('Raw Data'!M:M, A2, 'Raw Data'!L:L, "G")` |
| D | P Count | `=COUNTIFS('Raw Data'!M:M, A2, 'Raw Data'!L:L, "P")` |
| E | S Count | `=COUNTIFS('Raw Data'!M:M, A2, 'Raw Data'!L:L, "S")` |
| F | %G | `=IFERROR(C2/B2, 0)` → Format as % |
| G | %P | `=IFERROR(D2/B2, 0)` → Format as % |
| H | %S | `=IFERROR(E2/B2, 0)` → Format as % |
| I | Avg Satisfaction | `=AVERAGEIF('Raw Data'!M:M, A2, 'Raw Data'!I:I)` |
| J | Avg Difficulty | `=AVERAGEIF('Raw Data'!M:M, A2, 'Raw Data'!J:J)` |
| K | Last Active | `=MAXIFS('Raw Data'!A:A, 'Raw Data'!M:M, A2)` → Format as Date |
| L | Days Since Last | `=IFERROR(TODAY()-K2, "–")` |
| M | Status | `=IF(L2="–","–",IF(L2>=3,"⚠️ Inactive",IF(H2<0.1,"📘 G-Heavy","✅ OK")))` |

> **Để lấy danh sách unique hash:**
> Tab Per Student, ô A2:
> `=UNIQUE(FILTER('Raw Data'!M:M, 'Raw Data'!M:M<>"", 'Raw Data'!M:M<>"Student Hash"))`

---

## Tab: GPS Tracker

| Ô | Nội dung | Công thức |
|---|----------|-----------|
| A1 | Total Logs | `=COUNTA('Raw Data'!A:A)-1` |
| A2 | G Total | `=COUNTIF('Raw Data'!L:L,"G")` |
| A3 | P Total | `=COUNTIF('Raw Data'!L:L,"P")` |
| A4 | S Total | `=COUNTIF('Raw Data'!L:L,"S")` |
| A5 | Unknown | `=COUNTIF('Raw Data'!L:L,"Unknown")` |
| A6 | %G | `=IFERROR(A2/A1,0)` → Format % |
| A7 | %P | `=IFERROR(A3/A1,0)` → Format % |
| A8 | %S | `=IFERROR(A4/A1,0)` → Format % |
| A9 | Avg Satisfaction | `=AVERAGEIF('Raw Data'!L:L,"<>",  'Raw Data'!I:I)` |
| A10 | Avg Difficulty | `=AVERAGEIF('Raw Data'!L:L,"<>", 'Raw Data'!J:J)` |

### Biểu đồ phân bố G/P/S (Pie Chart)
- Chọn vùng `A2:A4` (G/P/S counts) + label G, P, S
- Insert → Chart → Pie chart
- Đặt tên: "Phân bố bước học G/P/S toàn khoá"

### Biểu đồ hoạt động theo ngày (Line Chart)
1. Thêm cột phụ trong GPS Tracker:

| Ngày | Số logs |
|------|---------|
| `=TEXT('Raw Data'!A2,"YYYY-MM-DD")` | (dùng COUNTIFS với cột ngày) |

Hoặc dùng Pivot Table trực tiếp:
- Data → Pivot Table, rows = `Timestamp` (group by Day), values = COUNTA.

---

## Tab: Alerts

Lọc bản ghi cần chú ý:

| Mục | Công thức (đặt trong cột A) |
|-----|----------------------------|
| Satisfaction ≤ 2 | `=FILTER('Raw Data'!A:M, 'Raw Data'!I:I<=2)` |
| Unknown Label | `=FILTER('Raw Data'!A:M, 'Raw Data'!L:L="Unknown")` |

> Đặt mỗi nhóm trên một vùng riêng, thêm header thủ công.

**Cách đơn giản hơn:** Dùng Conditional Formatting trên tab Raw Data:
- Cột I (Satisfaction): tô đỏ nếu ≤ 2
- Cột L (Auto Label): tô vàng nếu = "Unknown"
- Cột `Days Since Last` trong Per Student: tô cam nếu ≥ 3

---

## Lưu ý
- Công thức `AVERAGEIF`, `COUNTIFS`, `MAXIFS` chỉ chạy đúng khi tab tên đúng là `Raw Data`.
- Nếu đổi tên tab, thay `'Raw Data'` trong tất cả công thức.
- Cột M (Student Hash) là key để join giữa các tab – **không sửa cột này tay**.
