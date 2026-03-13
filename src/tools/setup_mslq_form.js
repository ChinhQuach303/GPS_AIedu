/**
 * GPS AIedu - MSLQ Survey Form Setup
 * ====================================
 * Chạy hàm `createMslqForm()` để tạo Google Form khảo sát MSLQ tiếng Việt
 * (20 items) dùng cho đo lường baseline (trước Pilot) và post-test (sau Pilot).
 *
 * Đầu ra: URL của Form để chia sẻ cho học sinh làm trước khi bắt đầu Pilot.
 */

const MSLQ_ITEMS = [
    "Tôi tự đặt mục tiêu học tập rõ ràng cho bản thân.",
    "Tôi thường lập kế hoạch trước khi bắt đầu học.",
    "Tôi kiểm tra xem mình đã hiểu bài đến đâu trong quá trình học.",
    "Tôi điều chỉnh cách học khi nhận thấy mình chưa hiểu.",
    "Tôi tự hỏi bản thân về những ý chính sau khi học xong.",
    "Tôi biết cách lựa chọn chiến lược học phù hợp với từng dạng bài.",
    "Tôi quản lý thời gian học tập một cách hiệu quả.",
    "Tôi học theo thời khóa biểu đã đặt ra.",
    "Tôi cố gắng hoàn thành bài tập đúng hạn.",
    "Tôi hạn chế các yếu tố gây xao nhãng khi học.",
    "Tôi chủ động tìm kiếm nguồn tài liệu bổ sung khi cần.",
    "Tôi tự đánh giá mức độ tiến bộ của mình theo thời gian.",
    "Tôi theo dõi lỗi sai để tránh lặp lại ở các bài sau.",
    "Tôi dành thời gian xem lại kiến thức trước khi làm bài mới.",
    "Tôi tự tin khi bắt đầu giải một bài toán mới.",
    "Khi gặp khó, tôi tìm cách khác thay vì bỏ cuộc.",
    "Tôi ghi chú lại những điểm quan trọng khi học.",
    "Tôi biết cách chia nhỏ nhiệm vụ học tập để dễ thực hiện.",
    "Tôi thường tự kiểm tra lại kết quả sau khi làm bài.",
    "Tôi tin rằng nỗ lực học tập sẽ giúp tôi cải thiện kết quả.",
];

function createMslqForm() {
    const form = FormApp.create("Khảo sát Phong cách Học tập – MSLQ (Toán 11)");
    form.setDescription(
        "Khảo sát này giúp chúng tôi hiểu cách bạn tự quản lý việc học.\n" +
        "Không có câu trả lời đúng hay sai. Hãy trả lời theo cảm nhận thực tế của bạn.\n\n" +
        "Thang điểm: 1 = Hoàn toàn KHÔNG đồng ý → 5 = Hoàn toàn ĐỒNG Ý"
    );
    form.setCollectEmail(false);
    form.setAllowResponseEdits(false);

    // Header: Student ID
    form.addTextItem()
        .setTitle("Mã số học sinh (Student ID)")
        .setHelpText("Nhập mã số học sinh nhóm đã cấp (ví dụ: HS0001). Không nhập tên thật.")
        .setRequired(true);

    // Header: Class
    form.addMultipleChoiceItem()
        .setTitle("Lớp")
        .setChoiceValues(["11A1", "11A2", "11A3", "11B1", "11B2", "Khác"])
        .setRequired(true);

    // Header: Round (pre/post)
    form.addMultipleChoiceItem()
        .setTitle("Thời điểm làm khảo sát")
        .setChoiceValues(["Trước thử nghiệm (Pre-test)", "Sau thử nghiệm (Post-test)"])
        .setRequired(true);

    // Separator
    form.addSectionHeaderItem().setTitle("Phần A: Nhận định về bản thân");

    // Add 20 MSLQ items
    for (let i = 0; i < MSLQ_ITEMS.length; i++) {
        const scaleItem = form.addScaleItem();
        scaleItem.setTitle((i + 1) + ". " + MSLQ_ITEMS[i])
            .setBounds(1, 5)
            .setLabels("Hoàn toàn không đồng ý", "Hoàn toàn đồng ý")
            .setRequired(true);
    }

    // Optional open comment
    form.addParagraphTextItem()
        .setTitle("Câu 21. Bạn có muốn chia sẻ thêm gì về cách học của mình không? (Không bắt buộc)");

    const formUrl = form.getPublishedUrl();
    const editUrl = form.getEditUrl();

    Logger.log("=== MSLQ Form Created ===");
    Logger.log("Form link (chia sẻ HS): " + formUrl);
    Logger.log("Form edit link:         " + editUrl);

    SpreadsheetApp.getUi().alert(
        "✅ MSLQ Form đã được tạo!\n\n" +
        "Link chia sẻ học sinh:\n" + formUrl + "\n\n" +
        "Cho học sinh làm TRƯỚC Pilot (Pre-test) và SAU Pilot (Post-test) để đo biến SRL."
    );
}
