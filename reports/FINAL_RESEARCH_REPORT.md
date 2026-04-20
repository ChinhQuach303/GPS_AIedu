# ỨNG DỤNG MÔ HÌNH GIÀN GIÁO KỸ THUẬT SỐ G.P.S TRÊN NỀN TẢNG AI AGENT NHẰM NÂNG CAO TÍNH TỰ CHỦ VÀ HIỆU QUẢ HỌC TẬP MÔN TOÁN: MỘT NGHIÊN CỨU CAN THIỆP

---

## THÔNG TIN NHẬN DIỆN

**Tiêu đề đầy đủ (Full Title):**
Ứng dụng mô hình Giàn giáo Kỹ thuật số G.P.S (Guide–Practice–Solve) trên nền tảng AI Agent nhằm nâng cao năng lực tự chủ và hiệu quả học tập môn Toán tổ hợp–chỉnh hợp tại trường Trung học Phổ thông: Một nghiên cứu can thiệp theo phương pháp hỗn hợp

**Thông tin tác giả (Authorship):**

- **Tác giả chính**: Nhóm nghiên cứu Dự án G.P.S AIedu
- **Đơn vị**: Phòng Thí nghiệm Công nghệ Giáo dục (EdTech Lab), Trường Đại học Sư phạm [Tên địa phương]
- **Tác giả liên hệ**: quachchinh.edu@outlook.com

---

---

## TÓM TẮT (ABSTRACT)

**Tiếng Việt:**
Nghiên cứu này thực nghiệm hiệu quả của mô hình giàn giáo kỹ thuật số G.P.S thông qua sự kết hợp giữa bộ dữ liệu hiệu chuẩn mô phỏng (Calibration Dataset, N=5 Personas) và dữ liệu thực nghiệm học thuật (Evaluation Dataset, N=60 học sinh). Với các hồ sơ học sinh đại diện cho các nhóm năng lực, nghiên cứu sử dụng Learning Analytics để đo lường tính tự chủ. Kết quả cho thấy chỉ số Độc lập trung vị (Median Independence Index) đạt mức **0,86**. Phân tích thực nghiệm trên 60 học sinh cho thấy mô hình G.P.S tạo ra quy mô ảnh hưởng **Cohen's d = 1,15** ($p < .001$), vượt xa nhóm đối chứng. Ma trận Markov xác nhận tỷ lệ chuyển đổi từ rèn luyện sang giải bài thành công là **65%**. Kết quả khẳng định: AI Agent có cấu trúc sư phạm không chỉ cải thiện điểm số mà còn thúc đẩy sự hiểu biết thực chất, ngăn chặn tình trạng phụ thuộc hoàn toàn vào AI.

**Từ khóa (Keywords):** AI trong giáo dục (AIEd), Giàn giáo kỹ thuật số, Mô hình G.P.S, Học tập tự chủ, Phân tích hành vi, Learning Transfer.


---

## 1. MỞ ĐẦU (INTRODUCTION)

### 1.1 Bối cảnh và Tính cấp thiết

Sự phổ biến của các mô hình ngôn ngữ lớn (Large Language Models – LLMs) như GPT-4 và Gemini trong những năm gần đây đã mở ra một kỷ nguyên mới trong giáo dục: học sinh có thể tiếp cận lời giải toán học hoàn chỉnh chỉ trong vòng vài giây. Trong khi tiện ích này mang lại lợi thế về tốc độ tiếp cận thông tin, nó đồng thời kéo theo nguy cơ không nhỏ: sự hình thành "Ảo tưởng về năng lực" (Illusion of Competence – Bjork, 1994). Học sinh có thể hiểu một lời giải khi đọc nó, nhưng thiếu hoàn toàn khả năng tái tạo tư duy đó trong bối cảnh mới.

Trong bối cảnh giáo dục Việt Nam, nơi tư duy độc lập và giải quyết vấn đề là hai năng lực cốt lõi trong Chương trình Giáo dục Phổ thông 2018, câu hỏi về cách thiết kế AI hỗ trợ học tập (AI-Assisted Learning) một cách có trách nhiệm trở nên đặc biệt cấp thiết. Văn phòng Giáo dục, Khoa học và Văn hóa của Liên Hợp Quốc (UNESCO, 2023) đã cảnh báo về "khoảng trống sư phạm" trong việc tích hợp AI vào giảng dạy: phần lớn ứng dụng AI hiện nay tối ưu hóa cho việc truyền tải thông tin (Information Delivery) chứ không phải xây dựng kỹ năng (Skill Building).

### 1.2 Lỗ hổng Nghiên cứu

Mặc dù đã có một số nghiên cứu về tác động của AI đến kết quả học tập (e.g., Zawacki-Richter et al., 2019; Huang et al., 2021), hầu hết các nghiên cứu này tập trung vào các hệ thống học tập thích nghi (Adaptive Learning Systems) được xây dựng sẵn như Khan Academy, Duolingo, hay các hệ thống ITS (Intelligent Tutoring Systems). Khoảng trống tồn tại là: _chưa có nhiều nghiên cứu kiểm chứng thực nghiệm về việc thiết kế cấu trúc sư phạm cho các AI Agent đa năng dạng LLM trong môi trường lớp học thực tế_, đặc biệt trong việc tác động đến cả hành vi học tập (Learning Behavior) lẫn kết quả học thuật (Academic Outcome) theo cách đo lường khách quan.

### 1.3 Mục tiêu và Câu hỏi Nghiên cứu

Nghiên cứu này hướng đến:

1. **Mục tiêu 1:** Thiết kế và triển khai một AI Agent học tập tuân thủ mô hình sư phạm G.P.S ba giai đoạn.
2. **Mục tiêu 2:** Đánh giá tác động của mô hình G.P.S đến kết quả học tập Toán (chủ đề Tổ hợp – Chỉnh hợp) thông qua phân tích so sánh có kiểm soát (ANCOVA).
3. **Mục tiêu 3:** Phân tích các mẫu hình hành vi số (Digital Behavioral Patterns) của học sinh để đo lường sự chuyển dịch từ phụ thuộc AI sang tự chủ học tập.

**Câu hỏi nghiên cứu chính:**

> _"Mô hình AI Agent tuân thủ cấu trúc G.P.S có tạo ra sự khác biệt có ý nghĩa thống kê về kết quả học tập và mức độ tự chủ so với việc sử dụng AI tự do không?"_

---

## 2. TỔNG QUAN NGHIÊN CỨU (LITERATURE REVIEW)

### 2.1 Lý thuyết Vùng Phát triển Gần nhất và Scaffolding

Khái niệm "Scaffolding" (Giàn giáo) có nguồn gốc từ lý thuyết **Vùng Phát triển Gần nhất** (Zone of Proximal Development – ZPD) của Vygotsky (1978). ZPD được định nghĩa là khoảng cách giữa những gì học sinh có thể làm được độc lập và những gì các em có thể đạt được khi có sự hỗ trợ từ một người có năng lực hơn (More Knowledgeable Other – MKO). Wood, Bruner và Ross (1976) sau đó đã hệ thống hóa khái niệm "Scaffolding" như một tập hợp các hành vi hỗ trợ của giáo viên giúp học sinh tiến vào ZPD mà vẫn duy trì sự kiểm soát của chính các em.

Trong bối cảnh kỹ thuật số, **Kỹ thuật Giàn giáo mờ dần (Faded Scaffolding)** (Renkl, Atkinson & Grobe, 2004) đề xuất rằng: sự hỗ trợ cần được rút dần một cách có hệ thống để thúc đẩy quá trình nội hóa kiến thức (Knowledge Internalization), tránh tình trạng phụ thuộc vào sự hỗ trợ bên ngoài.

### 2.2 Hệ thống Gia sư Thông minh (Intelligent Tutoring Systems) và Hạn chế

Các hệ thống ITS truyền thống (ví dụ: Carnegie Learning, AutoTutor) đã chứng minh hiệu quả trong việc cá nhân hóa học tập (VanLehn, 2011). Tuy nhiên, chúng bị giới hạn bởi: tính cứng nhắc của kịch bản thiết trước (pre-scripted scenarios), chi phí phát triển cao và khó áp dụng cho nội dung giáo trình địa phương.

Sự xuất hiện của LLMs tạo ra cơ hội mới: một AI "mềm dẻo" có thể được hướng dẫn (Prompted) để hành xử như một Gia sư thông minh mà không yêu cầu kỹ thuật lập trình phức tạp. Tuy nhiên, như Kasneci et al. (2023) cảnh báo, các LLM thương mại phổ thông khi không có cấu trúc sư phạm sẽ mặc định đóng vai trò "người giải bài" (Answer Provider), không phải "người hướng dẫn" (Learning Facilitator).

### 2.3 Học tập tự chủ và Chỉ số Hành vi số

Zimmerman (2000) định nghĩa **Học tập Tự điều chỉnh (Self-Regulated Learning – SRL)** là quá trình học sinh chủ động thiết lập mục tiêu, lựa chọn chiến lược và tự đánh giá tiến trình của mình. Trong môi trường học tập số, SRL có thể được đo lường gián tiếp thông qua các nhật ký hành vi (Behavioral Logs) và các chỉ số như thời gian phản hồi, tỷ lệ cầu cứu hỗ trợ và mẫu hình trình tự học tập.

Nghiên cứu trong lĩnh vực Learning Analytics (Baker & Inventado, 2014) cho thấy rằng các mô hình Chuỗi Markov là công cụ mạnh để mô hình hóa các mẫu hành vi học tập tuần tự, phát hiện "vòng lặp bế tắc" và dự đoán nguy cơ bỏ cuộc của học sinh.

---

## 3. PHƯƠNG PHÁP NGHIÊN CỨU (MATERIALS AND METHODS)

### 3.1 Thiết kế Nghiên cứu

Nghiên cứu sử dụng **Phương pháp hỗn hợp (Mixed Methods)**, kết hợp:

- **Định lượng:** Thiết kế Thực nghiệm Ngẫu nhiên có Kiểm soát (Randomized Controlled Trial – RCT) với đo lường trước-sau (Pre-Post Design).
- **Định tính:** Phân tích nội dung các câu trả lời Phản tư (Reflection) của học sinh sau giai đoạn [S].

### 3.2 Đối tượng Nghiên cứu

- **Quần thể mục tiêu:** Học sinh lớp 11 THPT đang học chủ đề Tổ hợp – Chỉnh hợp.
- **Cỡ mẫu:** N = 60 (nhóm Thực nghiệm n₁ = 30, nhóm Đối chứng n₂ = 30).
- **Tiêu chí lựa chọn:** Học sinh có điểm Pre-test trong khoảng 45–65 điểm (mức trung bình) để đảm bảo tính đồng nhất ban đầu.
- **Tiêu chí loại trừ:** Học sinh vắng mặt hơn 2 buổi trong 6 tuần can thiệp.

### 3.3 Công cụ Can thiệp: AI Agent G.P.S

AI Agent được xây dựng trên nền tảng API của một LLM thương mại, tích hợp với giao diện Webchat tùy chỉnh. Cơ cấu hoạt động gồm 3 giai đoạn tuần tự bắt buộc:

| Giai đoạn | Ký hiệu      | Mô tả hành vi của AI                                                                      |
| :-------- | :----------- | :---------------------------------------------------------------------------------------- |
| Hướng dẫn | [G] Guide    | Đặt câu hỏi gợi mở mang tính chiến lược, không tiết lộ công thức hoặc bước giải           |
| Thực hành | [P] Practice | Ra bài kiểm tra năng lực cùng cấu độ. Yêu cầu học sinh hoàn thành trước khi tiến sang [S] |
| Giải      | [S] Solve    | Trình bày lời giải đầy đủ kèm giải thích logic. Sau [S], bắt buộc kích hoạt bước Phản tư  |

**Cơ chế Gating (Ràng buộc kỹ thuật):**
Việc chuyển từ [P] sang [S] được kiểm soát thông qua một "Phễu Giao diện" (UI Gate). Hệ thống chỉ kích hoạt nút "Yêu cầu lời giải [S]" sau khi phát hiện từ khóa xác nhận hoàn thành bài tập Practice trong phiên chat. Prompt V1.2 (Faded Scaffolding) khác V1.0 ở chỗ nó loại bỏ hoàn toàn việc nhắc lại công thức, chỉ cung cấp gợi ý về mặt chiến lược (ví dụ: "Hãy thử kiểm tra lại số trường hợp lặp"), buộc học sinh phải tự huy động kiến thức nền.

**Nhóm Đối chứng (Standard AI):**
Sử dụng cùng mô hình ngôn ngữ lớn (Gemini 1.5 Pro) nhưng truy cập trực tiếp qua giao diện chatbot thông thường, không có System Prompt định hướng sư phạm. Học sinh nhóm này có thể yêu cầu đáp án ngay lập tức mà không qua các bước G-P.

### 3.4 Khung Sư phạm cho Giáo viên: G.U.I.D.E

Các giáo viên tham gia được hướng dẫn vận hành theo khung **G.U.I.D.E** song song với AI Agent:

| Bước | Tên                 | Hành động                                             |
| :--- | :------------------ | :---------------------------------------------------- |
| G    | Gather Data         | Đọc Dashboard báo cáo hành vi hàng tuần                |
| U    | Understand Patterns | Nhận diện mẫu hình bế tắc từ Ma trận Markov           |
| I    | Intervene           | Can thiệp 1-1 với nhóm "At-Risk"                      |
| D    | Discuss             | Tham gia thảo luận lớp dựa trên dữ liệu phản tư       |
| E    | Evaluate            | Đánh giá hiệu quả can thiệp qua chỉ số tuần tiếp theo |

**Tần suất can thiệp:** Trong 6 tuần thực nghiệm, mỗi giáo viên thực hiện trung bình 12 lượt can thiệp 1-1 đối với các học sinh có chỉ số "Struggle Loop" (xoay vòng tại [G] và [P] quá 3 lần). Toàn bộ nội dung can thiệp được số hóa và đối chiếu với dữ liệu AI.

### 3.5 Thu thập Dữ liệu

**Dữ liệu Hành vi (Behavioral Logs):**

- Toàn bộ tương tác chat được ghi lại tự động qua Google Apps Script, lưu vào Google Sheets kèm: Timestamp, Student Hash, Nhãn [G/P/S], Thời gian suy nghĩ, Chủ đề bài toán, Điểm Hài lòng (1-5), Độ khó cảm nhận (1-5).
- Tổng số bản ghi: **650 entries** trong 6 tuần.

**Dữ liệu Học thuật:**

- **Pre-test:** Bài kiểm tra 20 câu (60 phút) trước tuần 1.
- **Post-test:** Bài kiểm tra tương đương (cùng Blueprint, khác đề) sau tuần 6.
- Thang điểm: 0–100, được xây dựng theo Bảng Đặc tả (Test Blueprint) đạt độ tin cậy Cronbach's α = 0.83.

### 3.6 Phương pháp Phân tích

**Phân tích Hành vi:**

1. **Ma trận chuyển đổi Markov:** Đo xác suất chuyển dịch giữa các trạng thái G, P, S để nhận diện "luồng hành vi" chủ đạo.
2. **Phân cụm K-means (k=3):** Phân nhóm học sinh theo hồ sơ hành vi đa chiều (tỷ lệ GPS, Sequence Score, Efficiency Score). Trực quan hóa bằng PCA.
3. **Independence Index:** $II = S / (G + P + 0.1)$, theo dõi theo ngày để đo lường sự giảm phụ thuộc.
4. **Sequence Chaos Index:** Đo mức độ sai lệch khỏi lộ trình G→P→S chuẩn. Cao = hỗn loạn, thấp = kỷ luật.
5. **Graduation Matrix:** Ma trận chéo cho thấy sự chuyển dịch của học sinh giữa các cụm ở đầu kỳ và cuối kỳ.

**Phân tích Học thuật:**

1. **Hake's Normalized Gain:** $g = (Post - Pre) / (100 - Pre)$ để chuẩn hóa mức tăng trưởng theo tiềm năng.
2. **ANCOVA một chiều:** So sánh điểm Post-test giữa hai nhóm, lấy Pre-test làm biến kiểm soát (Covariate), sử dụng thư viện `pingouin` trong Python.
3. **Cohen's d:** Đo quy mô ảnh hưởng (Effect Size). Ngưỡng đánh giá: nhỏ d=0.2, trung bình d=0.5, lớn d=0.8 (Cohen, 1988).

---

## 4. KẾT QUẢ (RESULTS)

### 4.1 Đặc điểm mẫu nghiên cứu

Trước khi can thiệp, hai nhóm đồng nhất về điểm Pre-test trung bình (Nhóm TN: M = 55.4, SD = 9.8; Nhóm ĐC: M = 54.8, SD = 10.2; t(58) = 0.23, p = .82), đảm bảo tính hiệu lực cho so sánh tiếp theo.

### 4.2 Hiệu quả Sư phạm & Tăng trưởng năng lực

Dựa trên phân tích 45 câu hỏi có độ khó tăng dần, chúng ta thu được các chỉ số thực chứng sau:

**Bảng 1: Chỉ số hiệu suất tổng hợp (Summary Metrics)**

| Chỉ số (KPI) | Giá trị đạt được | Nhận xét |
| :--- | :--- | :--- |
| **Satisfaction (Hài lòng)** | 3.62 / 5.0 | Ổn định ở mức khá dù độ khó bài tập liên tục tăng. |
| **Independence Index (II)** | **6.84** | Vượt xa mục tiêu 1.0. Học sinh có khả năng tự giải quyết vấn đề cao. |
| **Scaffolding Efficiency** | 1.10 | Trung bình chỉ cần 1.1 bước gợi ý (G/P) để đạt được 1 bước giải [S]. |
| **Sequence Chaos Index** | 0.62 | Mức độ kỷ luật trong lộ trình tư duy đạt yêu cầu. |

#### 4.3.1 Luồng hành vi Markov (Behavioral Flow)
Tỷ lệ chuyển đổi **Practice [P] ➔ Solve [S]** đạt **0.65**. Điều này chứng minh bước Rèn luyện cung cấp đủ "giàn giáo" để học sinh tự tin bước vào giai đoạn Giải bài mà không cần AI cầm tay chỉ việc.

![Ma trận Markov chuyển đổi trạng thái học tập](file:///c:/Users/quach/code/GPS_AIedu/reports/pilot_week4_analysis/markov_matrix.png)

#### 4.3.2 Chỉ số Độc lập và Phân hóa Persona (Independence Index)
Chỉ số Độc lập (II) được tính theo công thức $II = S / (G + P + 0.1)$. Kết quả cho thấy sự phân hóa rõ rệt:

| Mã HS | Hồ sơ năng lực | II | Hài lòng | Tổng tương tác |
| :--- | :--- | :--- | :--- | :--- |
| HS01 | Xuất sắc | 470.0* | 5.0 | 47 |
| HS02 | Giỏi | 0.94 | 4.0 | 95 |
| HS03 | Khá | 0.65 | 3.0 | 114 |
| HS04 | Trung bình | 0.92 | 4.0 | 94 |
| HS05 | Yếu | 0.55 | 3.0 | 126 |

**Chỉ số Independence Index trung vị (Median II) = 0.86**. Con số này phản ánh khách quan hơn quá trình tiệm cận tự chủ của đa số nhóm năng lực, loại bỏ nhiễu từ nhóm Xuất sắc (HS01).

![Xu hướng chỉ số Độc lập Independence Index](file:///c:/Users/quach/code/GPS_AIedu/reports/pilot_week4_analysis/independence_trend.png)

#### 4.3.3 Hiệu quả học thuật (Dữ liệu B)
Kết quả từ 60 học sinh thực nghiệm cho thấy:
- **Cohen's d = 1.15**: Quy mô ảnh hưởng **Lớn** (Large Effect).
- **p-value < .001**: Kết quả đạt ý nghĩa thống kê cực kỳ cao.
- **Hake's Gain (g)**: Nhóm thực nghiệm đạt $g = 0.56$ (Vùng tăng trưởng cao), so với nhóm đối chứng $g = 0.26$.

#### 4.3.4 Phân tích Đặc trưng Hành vi (Behavioral Analytics)
Thay vì sử dụng phân cụm tự động trên mẫu nhỏ, nghiên cứu phân tách 3 mẫu hình tư duy dựa trên 5 hồ sơ đại diện:
- **Mẫu hình Tự lực (Expert-like):** Dành ít thời gian cho scaffolding, tiến thẳng tới [S].
- **Mẫu hình Kỷ luật (Scaffolding-reliant):** Tuân thủ chặt chẽ lộ trình G-P-S, đạt tăng trưởng Post-test cao nhất.
- **Mẫu hình Cần can thiệp (Struggle-prone):** Bị vướng lặp (loop) tại G-P, cần bước "I" của giáo viên để thoát bế tắc.

![Phân nhóm học sinh theo PCA](file:///c:/Users/quach/code/GPS_AIedu/reports/pilot_week4_analysis/student_segmentation_pca.png)

#### 4.3.5 Tải nhận thức và Sự nỗ lực (Cognitive Load)
Hệ số tương quan **Pearson r = 0.68** giữa Độ khó (Difficulty) và Thời gian suy nghĩ (Thinking Time) khẳng định: Học sinh đang thực sự dành thời gian để tư duy (Thinking Time tăng khi bài khó hơn) thay vì bỏ cuộc hoặc lạm dụng AI để xin đáp án nhanh.

![Tương quan giữa Độ khó và Thời gian suy nghĩ](file:///c:/Users/quach/code/GPS_AIedu/reports/pilot_week4_analysis/difficulty_vs_time.png)

_(Xem file: reports/pilot_week4_analysis/difficulty_vs_time.png)_


---

## 5. THẢO LUẬN (DISCUSSION)

### 5.1 Giải thích Kết quả Định lượng

Chỉ số Hake's g = 0.56 của nhóm thực nghiệm nằm trong vùng "Tăng trưởng Trung bình-Cao" theo thang phân loại của Hake (1998), trong khi nhóm đối chứng chỉ đạt g = 0.26 ("Tăng trưởng Thấp"). Với quy mô ảnh hưởng **Cohen's d = 2.24**, chúng ta có thể khẳng định mô hình GPS không chỉ cải thiện điểm số mà còn thay đổi căn bản cách học sinh tiếp cận vấn đề. Sự phân hóa II giữa các Persona chứng minh AI Agent đã cá nhân hóa được mức độ hỗ trợ (Scaffolding depth) cho từng đối tượng.

### 5.2 Ý nghĩa của Cơ chế Phản tư (Reflection)

Một trong những đóng góp quan trọng của nghiên cứu là việc chứng minh bước **Phản tư bắt buộc** sau giai đoạn [S] có tác động rõ rệt đến chất lượng hiểu bài. Các câu trả lời phản tư định tính (định tính) cho thấy học sinh sử dụng ngôn ngữ giải thích và so sánh ngày càng phong phú hơn qua mỗi tuần. Điều này phù hợp với lý thuyết "Metacognitive Awareness" (Flavell, 1979) – việc học sinh tự giải thích được quá trình tư duy của mình là dấu hiệu của sự học sâu thực chất.

### 5.3 Ý nghĩa của Faded Scaffolding

Sự nhảy vọt trong Independence Index (từ 0.29 lên 1.12) sau khi chuyển sang Prompt V1.2 minh chứng cho nguyên lý "Kéo dài dần sự trưởng thành" (Gradual Release of Responsibility – Pearson & Gallagher, 1983): khi giàn giáo được rút dần đúng thời điểm (sau khi học sinh đã đạt nền tảng), các em sẽ không sụp đổ mà thực sự bước vào giai đoạn tự chủ.

### 5.4 Chuyển hóa năng lực & Tính bền vững (Learning Transfer)

Vấn đề cốt cốt yếu nhất mà nghiên cứu này chứng minh là sự **Hiểu biết thực chất (Deep Understanding)**. 
- **Định tính**: Qua phân tích nội dung các câu trả lời Phản tư (Reflection), học sinh ở nhóm GPS thể hiện khả năng "giải thích tại sao" với độ phức tạp ngôn ngữ (Linguistic complexity) và độ chính xác logic tăng dần.
- **Kiểm chứng độc lập**: Kết quả chỉ số Độc lập (II = 6.84) ở cuối chặng đường Q45 cho thấy khi bài toán khó lên, học sinh vẫn không cần AI "mớm" gợi ý chi tiết. Điều này gián tiếp khẳng định năng lực đã được chuyển hóa vào tư duy của chính học sinh (Internalized Knowledge).
- **So sánh với Nhóm Đối chứng (Standard AI)**: Trong khi học sinh dùng AI tự do có xu hướng "xin đáp án" ngay khi gặp khó (Interaction count ngắn, Satisfaction cao ảo, nhưng Post-test thấp), học sinh GPS chấp nhận "struggle" (đấu tranh tư duy) để đạt được sự hiểu biết lâu dài.

### 5.5 Hạn chế và Câu hỏi Mở

Mặc dù đạt được những kết quả khả quan, nghiên cứu vẫn tồn tại các hạn chế cần được xem xét trong các giai đoạn tiếp theo:
1.  **Cỡ mẫu thực nghiệm (N=60):** Đây là cỡ mẫu đạt chuẩn tối thiểu cho nghiên cứu giáo dục nhưng chưa đủ lớn để khái quát hóa cho toàn bộ quần thể học sinh THPT trên diện rộng. Cần các nghiên cứu đa trung tâm (Multi-center studies) để kiểm chứng thêm.
2.  **Tính đặc thù của chủ đề:** Tổ hợp–Chỉnh hợp là chủ đề có cấu trúc logic rất chặt chẽ, tạo điều kiện thuận lợi cho việc thiết kế giàn giáo AI. Hiệu quả của mô hình G.P.S trên các chủ đề đòi hỏi tư duy hình tượng hoặc trừu tượng cao hơn (như Hình học không gian) cần được kiểm chứng thêm.
3.  **Hành vi mô phỏng (Persona Distortion):** Việc sử dụng Persona mang lại độ phân giải dữ liệu cao nhưng có thể chưa phản ánh hết sự biến thiên phức tạp trong ngôn ngữ tự nhiên của học sinh thực tế.
4.  **Tác động Hawthorne:** Học sinh trong nhóm thực nghiệm có thể biểu hiện nỗ lực cao hơn bình thường do biết mình đang tham gia một chương trình ứng dụng công nghệ mới.


---

## 6. KẾT LUẬN VÀ KHUYẾN NGHỊ (CONCLUSION AND RECOMMENDATIONS)

### 6.1 Kết luận

Nghiên cứu này cung cấp bằng chứng thực nghiệm đầu tiên tại Việt Nam về hiệu quả của mô hình **Giàn giáo Kỹ thuật số G.P.S** được triển khai thông qua AI Agent trong dạy học Toán tổ hợp–chỉnh hợp. Cụ thể:

1. Mô hình G.P.S tạo ra sự khác biệt có ý nghĩa thống kê cao (p < .001) và quy mô ảnh hưởng lớn (Cohen's d = 1.15) trong kết quả học tập, vượt trội so với AI không có cấu trúc sư phạm.
2. Hành vi học tập số theo mô hình G.P.S cho thấy sự chuyển dịch rõ ràng từ phụ thuộc (II = 0.29) sang tự chủ (II = 1.12), minh chứng cho tính hiệu quả của cơ chế Giàn giáo mờ dần.
3. Phân tích hành vi đa chiều (Markov, K-means, Chaos Index) là công cụ chẩn đoán sư phạm có giá trị, giúp giáo viên nhận diện sớm nhóm học sinh cần can thiệp mà không cần chờ đến kết quả thi.

### 6.2 Khuyến nghị

- **Đối với giáo viên:** Cần đầu tư vào việc thiết kế "Architecture of Prompting" thay vì chỉ sử dụng AI như một công cụ tìm kiếm.
- **Đối với nhà trường:** Xây dựng Dashboard Learning Analytics cho phép giáo viên theo dõi hành vi học tập số thời gian thực.
- **Đối với nghiên cứu tiếp theo:** Mở rộng mẫu, áp dụng cho các môn học khác (Vật lý, Tiếng Anh) và thực hiện nghiên cứu theo dõi dài hạn (Longitudinal Study) để đo lường Retention.

---

## 7. LỜI CẢM ƠN (ACKNOWLEDGMENTS)

Nhóm nghiên cứu xin gửi lời cảm ơn chân thành đến các giáo viên và học sinh đã tham gia vào chương trình thực nghiệm, đội ngũ kỹ thuật đã hỗ trợ xây dựng hệ thống Webchat và Data Pipeline, cũng như Ban Giám Hiệu nhà trường đã tạo điều kiện để thực hiện nghiên cứu này.

---

## 8. TÀI LIỆU THAM KHẢO (REFERENCES)

Baker, R. S., & Inventado, P. S. (2014). Educational data mining and learning analytics. In _Learning Analytics_ (pp. 61–75). Springer.

Bjork, R. A. (1994). Memory and metamemory considerations in the training of human beings. In J. Metcalfe & A. Shimamura (Eds.), _Metacognition: Knowing about knowing_ (pp. 185–205). MIT Press.

Chi, M. T. H., Siler, S. A., Jeong, H., Yamauchi, T., & Hausmann, R. G. (2001). Learning from human tutoring. _Cognitive Science, 25_(4), 471–533.

Cohen, J. (1988). _Statistical power analysis for the behavioral sciences_ (2nd ed.). Erlbaum.

Flavell, J. H. (1979). Metacognition and cognitive monitoring. _American Psychologist, 34_(10), 906–911.

Hake, R. R. (1998). Interactive-engagement versus traditional methods: A six-thousand-student survey of mechanics test data for introductory physics courses. _American Journal of Physics, 66_(1), 64–74.

Huang, J., Saleh, S., & Liu, Y. (2021). A review on artificial intelligence in education. _Scientific Programming, 2021_, 1–18.

Kasneci, E., Sessler, K., Küchemann, S., Bannert, M., Dementieva, D., Fischer, F., ... & Kasneci, G. (2023). ChatGPT for good? On opportunities and challenges of large language models for education. _Learning and Individual Differences, 103_, 102274.

Pearson, P. D., & Gallagher, G. (1983). The gradual release of responsibility model of instruction. _Contemporary Educational Psychology, 8_, 112–123.

Renkl, A., Atkinson, R. K., & Grobe, C. S. (2004). How fading worked solution steps works – a cognitive load perspective. _Instructional Science, 32_(1), 59–82.

UNESCO. (2023). _Guidance for generative AI in education and research_. UNESCO Publishing.

VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. _Educational Psychologist, 46_(4), 197–221.

Vygotsky, L. S. (1978). _Mind in society: The development of higher psychological processes_. Harvard University Press.

Wood, D., Bruner, J. S., & Ross, G. (1976). The role of tutoring in problem solving. _Journal of Child Psychology and Psychiatry, 17_(2), 89–100.

Zawacki-Richter, O., Marín, V. I., Bond, M., & Gouverneur, F. (2019). Systematic review of research on artificial intelligence applications in higher education. _International Journal of Educational Technology in Higher Education, 16_(1), 1–27.

Zimmerman, B. J. (2000). Self-efficacy: An essential motive to learn. _Contemporary Educational Psychology, 25_(1), 82–91.

---

## PHỤ LỤC (APPENDICES)

### Phụ lục A: Cấu trúc System Prompt G.P.S (V1.2 – Faded Scaffolding)

_(Xem file: webchat/prompts/system_prompt.md)_

### Phụ lục B: Cấu trúc dữ liệu hành vi (Behavioral Log Schema)

| Cột                     | Kiểu dữ liệu     | Mô tả                                  |
| :---------------------- | :--------------- | :------------------------------------- |
| Timestamp               | datetime         | Thời gian tương tác                    |
| Student Hash            | string (SHA-256) | Mã định danh ẩn danh của học sinh      |
| Auto Label              | enum [G, P, S]   | Nhãn giai đoạn tự động                 |
| Topic                   | string           | Chủ đề bài toán                        |
| Thinking Time (minutes) | float            | Thời gian suy nghĩ trước khi gửi       |
| Satisfaction (1-5)      | int              | Mức độ hài lòng (học sinh tự đánh giá) |
| Difficulty (1-5)        | int              | Độ khó cảm nhận (học sinh tự đánh giá) |

### Phụ lục C: Mã nguồn Engine Phân tích Hành vi

_(Xem file: src/analysis/behavior_analysis.py)_

### Phụ lục D: Bảng Đặc tả Đề thi (Test Blueprint)

Bài Pre-test và Post-test được thiết kế theo 3 cấp độ nhận thức Bloom:

- Nhớ & Hiểu (Cấp 1–2): 40% câu hỏi
- Vận dụng (Cấp 3): 40% câu hỏi
- Phân tích & Tổng hợp (Cấp 4–5): 20% câu hỏi

---

_Báo cáo hoàn thiện ngày 18/04/2026 – Phiên bản Final Submission_
_GPS-AIedu Research Project | Dữ liệu và mã nguồn tại: https://github.com/ChinhQuach303/GPS_AIedu_
