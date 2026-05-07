# EMNLP 2026 Complete Specification: GPS-Agent Research

Tài liệu này cung cấp các thông số chi tiết (Specs) để bạn hoàn thiện bài báo và bài trình bày nộp cho hội thảo EMNLP 2026 (Industry Track).

---

## I. Research Paper Specification (Đặc tả Bài báo)

### 1. Thông tin chung
- **Title đề xuất**: *GPS-Agent: A Multi-Agent Framework for Controlled Scaffolding in Mathematical Education*
- **Target Track**: Industry Track (Focus on MLOps, Scalability & Trustworthy AI).
- **Core Narrative**: Thay vì chỉ cung cấp đáp án (Answer-giving), GPS-Agent sử dụng cơ chế Multi-Agent để điều phối quá trình giảng dạy theo 3 giai đoạn (Guide-Practice-Solve), giúp tăng tính tự chủ (Independence) của học sinh.

### 2. Danh sách Bảng biểu & Hình ảnh (Visual Specs)
| ID | Tên Visual | Mô tả kỹ thuật | Dữ liệu nguồn |
| :--- | :--- | :--- | :--- |
| **Fig 1** | System Architecture | Sơ đồ Multi-Agent LangGraph (Supervisor + 3 Nodes). | `src/core/graph.py` |
| **Fig 2** | Markov Transition State | Xác suất chuyển trạng thái G -> P -> S (GPS Group vs Non-GPS). | `research_results.json` |
| **Fig 3** | Independence Trend | Biểu đồ đường thể hiện sự tăng trưởng của Independence Index qua 6 tuần. | `weekly_trend` |
| **Table 1** | Benchmarking Results | So sánh GPS và Non-GPS (N, Hake's Gain, Math Density, Cohen's d). | `paper_table1.json` |
| **Table 2** | Persona Diversity | Thống kê hiệu quả của GPS trên 4 nhóm học sinh (Giỏi, Khá, TB, Yếu). | `level_stats` |

### 3. Các đoạn nội dung "vàng" (Technical Highlights)
- **Independence Index (II)**: Định nghĩa `II = S / (G + P)`. Kết quả thực tế: `GPS (0.292) vs Non-GPS (0.000)`.
- **Effect Size**: Nhấn mạnh Cohen's d = **1.112** trên chỉ số Độc lập, chứng minh tác động cực lớn của phương pháp.
- **Math Density**: Tăng gấp đôi từ **2.56** lên **5.03**, cho thấy tương tác toán học sâu hơn.

---

## II. Presentation Deck Specification (Đặc tả Bài thuyết trình)

Bộ Slide cần tập trung vào việc "WOW" hội đồng bằng cả công nghệ (Multi-agent) và kết quả (Stats).

| Slide | Chủ đề | Nội dung chính | Visual gợi ý |
| :--- | :--- | :--- | :--- |
| **1** | Title | GPS-Agent: Nâng tầm giáo dục toán học bằng AI Agents. | Hình ảnh UI Webchat hiện đại. |
| **2** | Problem | Vấn đề "Answer-dependency": Học sinh dùng LLM chỉ để chép đáp án. | Biểu đồ "Low Independence" của Non-GPS. |
| **3** | Solution | G.P.S Framework: Quy trình Sư phạm được mã hóa thành code. | Icon 3 bước Guide - Practice - Solve. |
| **4** | Tech Stack | LangGraph & Multi-agent Orchestration. | Sơ đồ các Agent đang "nói chuyện" với nhau. |
| **5** | Methodology | Behavioral Simulation: Cách chúng ta test hệ thống trên 2,800+ phiên. | Screenshot code simulation. |
| **6** | Key Result 1 | Sự bùng nổ của tính Tự chủ (Independence Index). | Chart Cohen's d = 1.112 (Cực lớn). |
| **7** | Key Result 2 | Chất lượng tương tác (Math Density). | Word cloud hoặc bar chart so sánh MD. |
| **8** | Case Study | Ví dụ một đoạn chat học sinh từ bế tắc đến tự giải. | Chat bubble minh họa [G] -> [P] -> [S]. |
| **9** | Scalability | Khả năng mở rộng cho 60+ học sinh và các môn học khác. | Benchmark Throughput/Latency. |
| **10** | Conclusion | Tầm nhìn về "Personalized AI Tutor" thực sự. | Hình ảnh tương lai của GPS-Agent. |

---

## III. Các "Spec" kỹ thuật cần bổ sung để "hoàn hảo" (EMNLP Standards)

1. **Ablation Study**: Bạn nên chuẩn bị spec để so sánh:
   - GPS với "One-shot Prompting".
   - GPS có Supervisor vs. GPS cố định (Fixed chain).
2. **Human Evaluation**: Mặc dù data simulation rất tốt, Industry Track thường yêu cầu một mẫu nhỏ (khoảng 50-100 phiên) được đánh giá bởi giáo viên thật để verify "Gold Standard".
3. **Safety & Bias**: Spec về việc lọc "Language Leakage" (tiếng Trung) và đảm bảo agent không đưa ra đáp án sai (Math Verifier).

### 4. Mandatory Sections (ACL/EMNLP Requirements)
- **Limitations**: Thừa nhận giới hạn của simulation (synthetic behavior) so với học sinh thật và ranh giới của môn Toán (chưa test môn Xã hội).
- **Ethics Statement**: Đảm bảo quyền riêng tư dữ liệu học sinh (nếu có dùng data thật) và tính minh bạch của AI (AI không thay thế giáo viên mà là trợ giảng).
- **Impact Statement**: Tác động tích cực đến việc bình đẳng hóa giáo dục (giúp học sinh yếu tiếp cận gia sư 1-1).

---

Tôi đã chuẩn bị sẵn các bộ lọc và script để xuất bảng biểu theo đúng định dạng này. Bạn muốn tôi tập trung vào việc **viết bản thảo (Abstract/Intro)** hay **tạo các chart/table** trước?
