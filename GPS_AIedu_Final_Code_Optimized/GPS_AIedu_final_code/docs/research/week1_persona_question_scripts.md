# Week 1 – Bộ câu hỏi giả lập theo Persona (24 lượt / 1 persona)

Mục tiêu: bạn copy từng **câu hỏi** dưới đây để hỏi Chat AI (đã dán `src/ai/system_prompt.md`), rồi dán **câu hỏi + trả lời AI** vào Google Form để tạo dữ liệu thật.

Gợi ý điền Form nhất quán:
- `Student ID`: đúng persona (`HS0001`…`HS0005`)
- `Class`: chọn 1 lớp cố định (vd `11A1`) để dễ lọc
- `Topic`: chọn theo nội dung câu hỏi (có thể giữ cố định `Xác suất cơ bản` nếu bạn muốn đơn giản hoá)
- `Profile`: chọn đúng persona
- `GPS Step (Truth)`: chọn theo nhãn `(G)/(P)/(S)` ở đầu mỗi dòng

Lưu ý: Auto label (cột `L`) đang dùng regex trong `src/tools/gas_script.js`, nên các câu hỏi (G/P/S) bên dưới đã cố tình chứa các từ khoá như “giải thích/khái niệm…”, “hướng dẫn/gợi ý/bước…”, “kết quả/đáp án/đúng không…”.

---

## Persona HS0001 – Advanced/Fast (đi nhanh, tự làm nhiều)

01. (S) Em ra **kết quả** bài rút 2 bi từ hộp 5 đỏ 4 xanh để “2 bi cùng màu” là `4/9`. **Đúng không**?
02. (S) Bài: Hộp 6 trắng 4 đen, rút 2 bi không hoàn lại. Em tính `P(lần 2 đen | lần 1 trắng) = 4/9`. **Đúng không**?
03. (G) **Tóm tắt** nhanh khi nào dùng **tổ hợp** `C(n,k)` trong bài xác suất rút bi (không hoàn lại)?
04. (S) Bài: Hộp 10 tốt 2 lỗi, lấy 3. Em tính “**ít nhất** 1 lỗi” = `1 - C(10,3)/C(12,3) = 5/11`. **Đúng không**?
05. (S) Xạ thủ bắn 5 phát, `p=0.7`. Em ra **kết quả** trúng đúng 3 phát = `0.3087`. **Đúng không**?
06. (P) Bài “ít nhất 1 lỗi” ở trên: **gợi ý** giúp em **bước** kiểm tra nhanh xem em chọn biến cố đối có hợp lý không.
07. (S) Bài: Gieo 2 xúc xắc, em ra **kết quả** `P(tổng = 7) = 6/36 = 1/6`. **Đúng không**?
08. (G) **Giải thích** ngắn gọn **tại sao** trong gieo 2 xúc xắc, không gian mẫu là 36 (không phải 21)?
09. (S) Bài: Rút 1 lá từ bộ 52 lá. Em ra **kết quả** `P(lá cơ hoặc lá hình) = 1/2` (vì cơ là hình). **Đúng không**?
10. (G) **Phân biệt** “biến cố độc lập” và “xung khắc” bằng 1 ví dụ ngắn trong xác suất.
11. (S) Bài: Hộp 5 đỏ 4 xanh, rút 2 bi. Em ra **kết quả** “2 bi khác màu” = `1 - 4/9 = 5/9`. **Đúng không**?
12. (S) Bài: Rút 3 bi từ hộp 5 đỏ 4 xanh (không hoàn lại). Em tính **kết quả** “đúng 2 đỏ 1 xanh” = `C(5,2)C(4,1)/C(9,3)`. Viết vậy **đúng không**?
13. (P) Với bài rút 3 bi ở trên: **hướng dẫn** giúp em cách bấm/tính nhanh ra số cụ thể (không cần trình bày dài).
14. (S) Bài: Trong 1 lớp có 20 HS, chọn ngẫu nhiên 2 bạn. Em ra **kết quả** xác suất “2 bạn cùng giới” = `C(10,2)+C(10,2) / C(20,2)` (giả sử 10 nam 10 nữ). Em lập biểu thức vậy **đúng không**?
15. (G) **Công thức** xác suất có điều kiện `P(A|B)` là gì và đọc nghĩa như thế nào?
16. (S) Bài: Rút 2 lá không hoàn lại. Em tính **kết quả** `P(lá 2 là Át | lá 1 là Át) = 3/51`. **Đúng không**?
17. (S) Bài: Gieo 3 đồng xu công bằng. Em ra **kết quả** “ít nhất 2 mặt ngửa” = `C(3,2)/8 + C(3,3)/8 = 4/8 = 1/2`. **Đúng không**?
18. (P) Bài 3 đồng xu: **gợi ý** 1 **bước** kiểm tra nhanh bằng biến cố đối để đối chiếu kết quả.
19. (S) Bài: Xạ thủ bắn 5 phát `p=0.7`. Em muốn tính “trúng **ít nhất** 4 phát” thì làm bằng `P(4)+P(5)`. Cách làm vậy **đúng không**?
20. (G) **Giải thích** khi nào nên dùng “**biến cố đối**” trong bài dạng “ít nhất 1”.
21. (S) Bài: Hộp 6 trắng 4 đen, rút 2 không hoàn lại. Em ra **kết quả** `P(2 bi cùng màu)= C(6,2)+C(4,2) / C(10,2)`. **Đúng không**?
22. (S) Bài: Rút 1 bi từ hộp có 3 đỏ 2 xanh. Em ra **kết quả** `P(đỏ)=3/5`. **Đúng không**?
23. (P) Với bài đơn giản `P(đỏ)=3/5`: **gợi ý** cách trình bày “tần suất” vs “xác suất” để em nói gọn mà đúng.
24. (S) Tổng hợp: em ra **kết quả** “ít nhất 1 lỗi” (10 tốt 2 lỗi, lấy 3) = `5/11` và “2 bi cùng màu” (5 đỏ 4 xanh, rút 2) = `4/9`. Hai kết quả này đều **đúng không**?

---

## Persona HS0002 – Typical/Normal (đi đúng G→P→S, đủ 24 lượt = 8 vòng)

### Vòng 1 – Rút bi (cơ bản)
01. (G) **Giải thích** giúp em **khái niệm** “không gian mẫu” và “biến cố” trong bài rút bi là **gì**?
02. (P) Hộp có 5 bi đỏ và 4 bi xanh, rút ngẫu nhiên 2 bi. **Hướng dẫn** em từng **bước** để tính xác suất “2 bi cùng màu”.
03. (S) Em làm: `n(Ω)=C(9,2)=36`, `n(A)=C(5,2)+C(4,2)=16` nên **kết quả** `P(A)=16/36=4/9`. **Đúng không**?

### Vòng 2 – Xác suất có điều kiện
04. (G) **Định nghĩa** xác suất có điều kiện `P(A|B)` và **tại sao** khi “không hoàn lại” thì mẫu số thay đổi?
05. (P) Hộp có 6 trắng 4 đen. Rút 2 bi không hoàn lại. **Gợi ý** em **bước** đầu để tính `P(lần 2 rút đen | lần 1 rút trắng)`.
06. (S) Em tính: sau lần 1 (trắng) còn 9 bi, trong đó 4 đen nên **kết quả** là `4/9`. **Đúng không**?

### Vòng 3 – Biến cố đối (“ít nhất 1”)
07. (G) **Giải thích** khi nào nên dùng **biến cố đối** trong bài xác suất dạng “ít nhất 1”.
08. (P) Hộp có 10 tốt và 2 lỗi, lấy 3. **Hướng dẫn** em theo **bước** dùng biến cố đối để tính xác suất “ít nhất 1 sản phẩm lỗi”.
09. (S) Em làm: `P(ít nhất 1 lỗi)=1 - C(10,3)/C(12,3)=1-120/220=5/11`. **Kết quả** vậy **đúng không**?

### Vòng 4 – Nhị thức Bernoulli (bắn mục tiêu)
10. (G) **Tóm tắt** **công thức** nhị thức Bernoulli và ý nghĩa của `C(n,k)` trong xác suất “trúng đúng k lần”.
11. (P) Xạ thủ bắn 5 phát, xác suất trúng mỗi phát `p=0.7`. **Hướng dẫn** em từng **bước** để tính xác suất trúng đúng 3 phát.
12. (S) Em tính: `C(5,3)*0.7^3*0.3^2=10*0.343*0.09=0.3087`. **Đúng không**?

### Vòng 5 – Xúc xắc (đếm trường hợp)
13. (G) **Phân biệt** “đếm bằng liệt kê” và “đếm bằng quy tắc nhân” trong bài gieo xúc xắc.
14. (P) Gieo 2 xúc xắc cân bằng. **Gợi ý** em **bước** đếm số cách để tổng bằng 7.
15. (S) Em liệt kê được 6 cặp nên **kết quả** `P=6/36=1/6`. **Đúng không**?

### Vòng 6 – Rút bài (hợp, giao)
16. (G) **Giải thích** quy tắc cộng `P(A ∪ B)` và **tại sao** phải trừ `P(A ∩ B)`.
17. (P) Rút 1 lá từ bộ 52 lá. Tính xác suất “lá cơ **hoặc** lá hình”. **Hướng dẫn** em theo **bước** dùng hợp-giao.
18. (S) Em làm: `P(cơ)=13/52`, `P(hình)=12/52`, `P(cơ ∩ hình)=12/52` nên **kết quả** là `13/52=1/4`. **Đúng không**?

### Vòng 7 – Rút 3 bi (tổ hợp)
19. (G) **Giải thích** **tại sao** bài rút nhiều bi “không xét thứ tự” thường dùng **tổ hợp**.
20. (P) Hộp 5 đỏ 4 xanh, rút 3 bi không hoàn lại. **Hướng dẫn** em từng **bước** để tính xác suất “đúng 2 đỏ 1 xanh”.
21. (S) Em lập: `P = C(5,2)C(4,1)/C(9,3)` và tính ra `= (10*4)/84 = 40/84 = 10/21`. **Đúng không**?

### Vòng 8 – Đồng xu (ít nhất)
22. (G) **Định nghĩa** “thành công/thất bại” trong mô hình Bernoulli và cách hiểu “ít nhất k”.
23. (P) Gieo 3 đồng xu công bằng. **Gợi ý** em **bước** tính xác suất “ít nhất 2 mặt ngửa”.
24. (S) Em tính: `P = (C(3,2)+C(3,3))/8 = (3+1)/8 = 1/2`. **Kết quả** **đúng không**?

---

## Persona HS0003 – Struggling/Slow (G nhiều, P lặp, đôi khi không lên S)

01. (G) **Giải thích** thật đơn giản “xác suất” **là gì** và cách hiểu `P(A)=n(A)/n(Ω)` giúp em với.
02. (P) Bài hộp 5 đỏ 4 xanh rút 2: **hướng dẫn** em **bước** 1 phải làm gì trước?
03. (P) Em bị kẹt ở **bước** đếm `n(Ω)`. Dùng `C(9,2)` hay `9*8`? **Gợi ý** giúp em.
04. (S) Em thử làm `n(Ω)=C(9,2)=36`, `n(A)=16` nên **kết quả** `4/9`. **Đúng không**?

05. (G) **Phân biệt** giúp em “rút có hoàn lại” và “không hoàn lại” khác nhau **tại sao**?
06. (P) Hộp 6 trắng 4 đen, rút 2 không hoàn lại: **hướng dẫn** em **bước** để tính `P(lần 2 đen | lần 1 trắng)`.
07. (P) Em bị kẹt: sau khi biết lần 1 là trắng thì mẫu số là 10 hay 9? **Sai ở đâu** nếu em vẫn dùng 10?
08. (S) Em sửa lại: còn 9 bi, 4 đen nên **kết quả** `4/9`. **Đúng không**?

09. (G) **Giải thích** “biến cố đối” **là gì** và dùng khi nào trong câu “ít nhất 1”.
10. (P) Bài 10 tốt 2 lỗi, lấy 3: **gợi ý** em **bước** viết biến cố đối cho “ít nhất 1 lỗi”.
11. (P) Em viết biến cố đối là “cả 3 đều tốt”. Đến đây em bị kẹt ở **bước** đếm số cách chọn 3 tốt. **Hướng dẫn** giúp em.
12. (S) Em tính được `1 - C(10,3)/C(12,3) = 5/11`. **Đúng không**?

13. (G) **Tóm tắt** giúp em công thức nhị thức Bernoulli (đúng k lần) và **khái niệm** `n, k, p`.
14. (P) Xạ thủ bắn 5 phát `p=0.7`: **hướng dẫn** em từng **bước** thay số vào biểu thức Bernoulli để ra xác suất trúng đúng 3.
15. (P) Em bị kẹt ở **bước** tính `0.7^3` và `0.3^2` (em hay nhầm). **Gợi ý** cách tránh sai.
16. (S) Em ra **kết quả** `0.3087`. **Đúng không**?

17. (G) **Giải thích** giúp em quy tắc cộng `P(A ∪ B)` **tại sao** phải trừ phần giao.
18. (P) Rút 1 lá từ 52 lá: “lá cơ hoặc lá hình”. **Hướng dẫn** em theo **bước** để không bị trùng.
19. (P) Em bị kẹt: `P(cơ ∩ hình)` là bao nhiêu? **Gợi ý** nhanh giúp em.
20. (S) Em ra **kết quả** `13/52 = 1/4`. **Đúng không**?

21. (P) Em không biết bắt đầu bài gieo 2 xúc xắc tính tổng 7. **Hướng dẫn** em từng **bước** liệt kê.
22. (P) Em liệt kê được vài cặp nhưng sợ thiếu. Có cách **kiểm tra bước** để chắc đủ 6 cặp không?
23. (S) Em chốt **kết quả** `1/6`. **Đúng không**?
24. (G) Em vẫn hay nhầm “tổ hợp” và “chỉnh hợp”. **Phân biệt** giúp em bằng 1 câu thật ngắn.

---

## Persona HS0004 – Offtrack (xin đáp án/giải giúp, lệch quy trình)

01. (S) Bài hộp 5 đỏ 4 xanh rút 2: cho em **đáp án** / **kết quả** xác suất 2 bi cùng màu luôn.
02. (S) AI **giải giúp** em toàn bộ bài trên, em cần **đáp án** để nộp.
03. (P) Nếu không cho đáp án thì **hướng dẫn** em **bước** 1 thôi: em phải tính gì trước?
04. (S) Em làm nhanh ra **kết quả** `4/9`. **Đúng không**? Nếu sai thì cho em **đáp án** đúng.

05. (S) Bài 10 tốt 2 lỗi lấy 3, xác suất “ít nhất 1 lỗi” **kết quả** bao nhiêu? Cho em **đáp án**.
06. (S) Em không cần trình bày, chỉ cần **đáp án** dạng phân số.
07. (P) Thôi AI **gợi ý** em đúng 1 **bước** để ra đáp án nhanh nhất.
08. (S) Em thấy người ta viết `1 - C(10,3)/C(12,3)` ra **kết quả** `5/11`. **Đúng không**?

09. (S) Xạ thủ bắn 5 phát `p=0.7`, trúng đúng 3 phát: cho em **kết quả** số thập phân luôn.
10. (S) Em nộp bài gấp, AI **giải giúp** em ra **đáp án**.
11. (P) OK, vậy **hướng dẫn** em **bước** thay số vào biểu thức thôi (đừng trình bày dài).
12. (S) Em ra **kết quả** `0.3087`. **Đúng không**?

13. (S) Rút 1 lá từ 52 lá: “cơ hoặc hình”. **Đáp án** là bao nhiêu?
14. (S) AI cho em **kết quả** cuối cùng, đừng giải.
15. (P) Nếu phải giải thì **gợi ý** em **bước** tính `P(A∩B)` nhanh.
16. (S) Em chốt **kết quả** `1/4`. **Đúng không**?

17. (S) Gieo 2 xúc xắc, tổng 7: **đáp án** là bao nhiêu?
18. (S) AI **giải giúp** em theo kiểu ra số luôn.
19. (P) Thôi, **hướng dẫn** em **bước** liệt kê nhanh 6 cặp tổng 7.
20. (S) Em ra **kết quả** `1/6`. **Đúng không**?

21. (S) Rút 3 bi từ 5 đỏ 4 xanh, đúng 2 đỏ 1 xanh: cho em **đáp án**.
22. (S) AI làm hộ em bài này, em cần **kết quả** ngay.
23. (P) Nếu không, **gợi ý** em **bước** viết biểu thức tổ hợp để tính.
24. (S) Em viết `C(5,2)C(4,1)/C(9,3)` và ra **kết quả** `10/21`. **Đúng không**?

---

## Persona HS0005 – Inactive (làm 1 ngày rồi dừng để test cảnh báo)

Mục tiêu persona này là tạo vài log rồi **dừng hẳn** để sau `DAYS_INACTIVE_LIMIT` ngày, tab `Alerts`/email (nếu bật) báo “inactive”.

### Ngày 1 (chỉ submit 6 lượt rồi dừng)
01. (G) **Giải thích** “không gian mẫu” trong bài rút bi **là gì**?
02. (P) Hộp 5 đỏ 4 xanh rút 2: **hướng dẫn** em từng **bước** để tính xác suất 2 bi cùng màu.
03. (S) Em ra **kết quả** `4/9`. **Đúng không**?
04. (G) **Định nghĩa** xác suất có điều kiện `P(A|B)` là gì?
05. (P) Hộp 6 trắng 4 đen rút 2 không hoàn lại: **gợi ý** em **bước** đầu để tính `P(lần 2 đen | lần 1 trắng)`.
06. (S) Em ra **kết quả** `4/9`. **Đúng không**?

### (Tuỳ chọn) Danh sách 18 câu còn lại nếu bạn muốn persona này “quay lại” sau vài ngày
07. (G) **Giải thích** khi nào dùng **biến cố đối** cho dạng “ít nhất 1”.
08. (P) 10 tốt 2 lỗi, lấy 3: **hướng dẫn** em theo **bước** để tính “ít nhất 1 lỗi”.
09. (S) Em ra **kết quả** `5/11`. **Đúng không**?
10. (G) **Tóm tắt** công thức nhị thức Bernoulli.
11. (P) Xạ thủ bắn 5 phát `p=0.7`: **hướng dẫn** em từng **bước** tính trúng đúng 3.
12. (S) Em ra **kết quả** `0.3087`. **Đúng không**?
13. (G) **Giải thích** quy tắc cộng `P(A∪B)` và phần giao.
14. (P) Rút 1 lá: “cơ hoặc hình”. **hướng dẫn** em theo **bước** hợp-giao.
15. (S) Em ra **kết quả** `1/4`. **Đúng không**?
16. (G) **Phân biệt** độc lập và xung khắc.
17. (P) Gieo 2 xúc xắc: **gợi ý** em **bước** đếm tổng 7.
18. (S) Em ra **kết quả** `1/6`. **Đúng không**?
19. (G) **Giải thích** vì sao rút 3 bi không xét thứ tự dùng tổ hợp.
20. (P) 5 đỏ 4 xanh, rút 3: **hướng dẫn** em **bước** tính đúng 2 đỏ 1 xanh.
21. (S) Em ra **kết quả** `10/21`. **Đúng không**?
22. (G) **Định nghĩa** “ít nhất 2 mặt ngửa” trong gieo 3 đồng xu.
23. (P) Gieo 3 đồng xu: **gợi ý** em **bước** tính “ít nhất 2 mặt ngửa”.
24. (S) Em ra **kết quả** `1/2`. **Đúng không**?
