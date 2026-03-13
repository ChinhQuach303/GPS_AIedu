# Bộ Q&A Chuẩn cho Giả lập (Chủ đề: Xác suất - Toán 11)

Tài liệu này cung cấp các kịch bản hỏi-đáp mẫu để bạn sử dụng khi đóng vai (simulate) các Persona học sinh trong Bước 4A của Playbook. Việc dùng chung một bộ câu hỏi giúp bạn dễ dàng đối chiếu dữ liệu giữa các "học sinh" khác nhau trên Dashboard.

---

## Session 1: Xác suất cơ bản (Rút bi)

**Chủ đề:** Tính xác suất lấy được bi cùng màu hoặc khác màu từ một hộp.

### [G] - Guide (Hỏi khái niệm/phương pháp)
- **Học sinh:** "Giải thích giúp mình xác suất là gì và làm sao để tính xác suất của một biến cố trong bài toán rút bi?"
- **AI (Dự kiến):** "[G] Xác suất của một biến cố là tỉ số giữa số kết quả thuận lợi và tổng số kết quả có thể xảy ra. Công thức là P(A) = n(A) / n(Ω). Bạn cần xác định: (1) Tổng số bi? (2) Số cách chọn bi bất kỳ? (3) Số cách chọn đúng loại bi yêu cầu? Bạn đã rõ cách đếm n(Ω) chưa?"

### [P] - Practice (Luyện tập từng bước)
- **Đề bài:** Hộp có 5 bi đỏ và 4 bi xanh. Rút ngẫu nhiên 2 bi. Tính xác suất để 2 bi cùng màu.
- **Học sinh:** "Mình có bài: Hộp 5 đỏ 4 xanh, rút 2 bi. Tính xác suất 2 bi cùng màu. Hướng dẫn mình từng bước với."
- **AI (Dự kiến):** "[P] Bước 1: Tính tổng số cách chọn 2 bi từ 9 bi (n(Ω)). Bước 2: Chia thành 2 trường hợp thuận lợi: (TH1) Cả 2 cùng đỏ, (TH2) Cả 2 cùng xanh. Bạn thử tính n(Ω) bằng tổ hợp xem ra bao nhiêu?"

### [S] - Solve (Tự giải & Kiểm tra)
- **Học sinh:** "Mình làm thế này: n(Ω) = C(9, 2) = 36. Lấy 2 bi cùng màu: TH1 chọn 2 đỏ là C(5, 2) = 10; TH2 chọn 2 xanh là C(4, 2) = 6. Vậy n(A) = 10 + 6 = 16. Xác suất P(A) = 16/36 = 4/9. Đúng không AI?"
- **AI (Dự kiến):** "[S] Chính xác! Logic của bạn rất tốt: đếm đúng không gian mẫu và chia đủ các trường hợp cùng màu. Phép tính C(5,2)=10 và C(4,2)=6 cũng hoàn toàn đúng. Bạn có muốn thử bài toán rút 3 bi không?"

---

## Session 2: Xác suất có điều kiện

**Chủ đề:** Rút bi không hoàn lại.

### [G] - Guide
- **Học sinh:** "Giải thích giúp mình xác suất có điều kiện là gì khi rút bi không hoàn lại?"
- **AI (Dự kiến):** "[G] Đó là xác suất của một biến cố dựa trên việc một biến cố khác đã xảy ra. Khi không hoàn lại, số lượng bi trong hộp sẽ giảm đi sau lần rút đầu, làm thay đổi mẫu số. Bạn có muốn xem một ví dụ cụ thể không?"

### [P] - Practice
- **Đề bài:** Hộp có 6 bi trắng và 4 bi đen. Rút lần lượt 2 bi không hoàn lại. Tính xác suất lần 2 rút được bi đen biết lần 1 đã rút được bi trắng.
- **Học sinh:** "Hộp có 6 trắng 4 đen. Rút 2 bi không hoàn lại. Tính xác suất lần 2 là đen biết lần 1 là trắng. Gợi ý mình bước đầu tiên."
- **AI (Dự kiến):** "[P] Hãy giả định lần 1 đã rút xong 1 bi trắng. Bây giờ trong hộp còn tổng cộng bao nhiêu bi? Và còn bao nhiêu bi đen? Từ đó bạn tính tỉ lệ bi đen còn lại."

### [S] - Solve
- **Học sinh:** "Sau lần 1 thì còn 9 bi (5 trắng, 4 đen). Vậy xác suất lần 2 rút được đen là 4/9. Mình giải vậy đúng chưa?"
- **AI (Dự kiến):** "[S] Hoàn toàn đúng. Bạn đã nắm rất chắc việc 'cập nhật' trạng thái của hộp sau lần rút đầu tiên. Đây chính là bản chất của xác suất có điều kiện trong thực tế."

---

## Session 3: Tình huống "Offtrack" (Học sinh xin đáp án)

**Dùng cho HS0004 để test tính nghiêm túc của AI.**

- **Học sinh:** "Giải giúp mình bài này luôn: Lớp có 10 nam 5 nữ, chọn 3 người có ít nhất 1 nữ. Cho mình đáp án cuối nhé."
- **AI (Dự kiến):** "[P] Mình sẽ không đưa đáp án ngay để bạn luyện tư duy nhé. Gợi ý: Bài này dùng 'biến cố đối' sẽ nhanh hơn nhiều. Bạn thử tìm số cách chọn 3 người bất kỳ trừ đi số cách chọn 3 người toàn nam xem?"

---

## Session 4: Tình huống "Struggling" (Học sinh kẹt ở P)

**Dùng cho HS0003 để tạo log Difficulty cao.**

- **Học sinh:** "Mình vẫn không hiểu tại sao mẫu số lại là 36 trong bài rút 2 bi từ 9 bi ban đầu. Giải thích lại giúp mình."
- **AI (Dự kiến):** "[G] Vì ta chọn 2 bi từ tổng số 9 bi và không quan trọng thứ tự bi nào trước bi nào sau, nên ta dùng tổ hợp C(9, 2). Công thức là 9! / (2! * 7!) = (9 * 8) / 2 = 36. Bạn đã học về công thức tổ hợp chưa?"

---

## Session 5: Phép thử Bernoulli (Công thức Bernoulli) - Nâng cao

**Chủ đề:** Tính xác suất có đúng k lần thành công trong n phép thử độc lập.

### [G] - Guide
- **Học sinh:** "Giải thích giúp mình khi nào thì dùng công thức Bernoulli và nó khác gì với quy tắc nhân thông thường?"
- **AI (Dự kiến):** "[G] Ta dùng công thức Bernoulli khi thực hiện n phép thử độc lập mà mỗi phép thử chỉ có 2 kết quả (Thành công/Thất bại) với xác suất p không đổi. Khác ở chỗ nó tính đến việc 'k lần thành công' có thể nằm ở bất kỳ thứ tự nào trong n lần. Bạn đã biết ký hiệu C(n, k) trong công thức này chưa?"

### [P] - Practice
- **Đề bài:** Một xạ thủ bắn mục tiêu với xác suất trúng là 0.7. Xạ thủ bắn 5 phát. Tính xác suất để xạ thủ bắn trúng đúng 3 phát.
- **Học sinh:** "Xạ thủ bắn 5 phát, xác suất trúng mỗi phát là 0.7. Tính xác suất trúng đúng 3 phát. Hướng dẫn mình áp dụng công thức."
- **AI (Dự kiến):** "[P] Bước 1: Xác định n = 5, k = 3, p = 0.7. Bước 2: Công thức là P = C(n, k) * p^k * (1-p)^(n-k). Bạn thử tính 1-p (xác suất trượt) và thay số vào xem?"

### [S] - Solve
- **Học sinh:** "Mình thay số: n=5, k=3, p=0.7, 1-p=0.3. Vậy P = C(5, 3) * 0.7^3 * 0.3^2 = 10 * 0.343 * 0.09 = 0.3087. Kết quả này đúng chưa AI?"
- **AI (Dự kiến):** "[S] Chúc mừng bạn, kết quả 0.3087 là hoàn toàn chính xác! Bạn đã hiểu cách kết hợp tổ hợp để đếm số cấu hình và nhân xác suất cho từng lượt bắn. Bài toán này rất quan trọng trong kiểm soát chất lượng đấy."

---

## Session 6: Biến cố hợp và Quy tắc cộng - Nâng cao

**Chủ đề:** Xác suất "ít nhất", "có ít nhất một".

### [G] - Guide
- **Học sinh:** "Khi nào mình nên dùng biến cố đối thay vì tính trực tiếp các trường hợp có lợi?"
- **AI (Dự kiến):** "[G] Khi bài toán yêu cầu 'ít nhất 1', 'ít nhất 2' mà số trường hợp thuận lợi quá nhiều, ta dùng biến cố đối (1 - xác suất trường hợp không xảy ra). Nó giúp giảm khối lượng tính toán và tránh sai sót. Bạn có ví dụ nào đang gặp khó không?"

### [P] - Practice
- **Đề bài:** Một hộp có 10 sản phẩm tốt và 2 sản phẩm lỗi. Lấy ngẫu nhiên 3 sản phẩm. Tính xác suất để có ít nhất 1 sản phẩm lỗi.
- **Học sinh:** "Hộp có 10 tốt 2 lỗi, lấy 3. Tính xác suất ít nhất 1 lỗi. Hướng dẫn mình dùng biến cố đối."
- **AI (Dự kiến):** "[P] Bước 1: Tính n(Ω) = C(12, 3). Bước 2: Biến cố đối của 'ít nhất 1 lỗi' là 'không có lỗi nào' (tức là 3 sản phẩm lấy ra đều tốt). Bạn hãy tính số cách chọn 3 sản phẩm từ 10 sản phẩm tốt."

### [S] - Solve
- **Học sinh:** "n(Ω) = C(12, 3) = 220. Chọn 3 tốt: C(10, 3) = 120. Vậy P(đối) = 120/220 = 6/11. Nên P(cần tìm) = 1 - 6/11 = 5/11. Đúng không?"
- **AI (Dự kiến):** "[S] Chính xác tuyệt đối! Bạn đã thực hiện đúng quy trình 2 bước với biến cố đối. Cách này nhanh hơn nhiều so với việc chia 2 trường hợp (1 lỗi và 2 lỗi) đúng không nào?"

---


## Gợi ý gán nhãn cho người thực hiện (User)

Khi điền Form cho các câu hỏi trên, bạn hãy chọn **GPS Step (Truth)** như sau:
- Câu hỏi thuộc phần **[G]** => Chọn **G - Guide**
- Câu hỏi thuộc phần **[P]** => Chọn **P - Practice**
- Câu hỏi thuộc phần **[S]** => Chọn **S - Solve**
- Câu hỏi "xin đáp án" => Bạn nên chọn **S** (vì học sinh đang yêu cầu lời giải cuối) để xem AI có từ chối đúng không.
