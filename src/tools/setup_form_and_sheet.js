/**
 * GPS AIedu - Auto Setup Script (Tuần 1 Real Run)
 * ================================================
 * Chạy hàm `setupFormAndSheet()` MỘT LẦN DUY NHẤT để:
 *   1. Tạo Google Form "Nhật Ký Tương Tác AI (G.P.S)"
 *   2. Liên kết Form → Sheet vào tab "Raw Data" (Form Responses sheet được đổi tên)
 *   3. Chuẩn hoá header 13 cột (A..M) đúng schema tuần 1
 *   4. Cài trigger onFormSubmit (Spreadsheet trigger) tự động ghi cột L/M
 *
 * SAU KHI chạy xong:
 *   - Dán nội dung src/tools/gas_script.js vào cùng project Apps Script
 *   - Kiểm tra CONFIG trong gas_script.js (SALT, ADMIN_EMAIL)
 *
 * LƯU Ý: Chạy script này từ Apps Script của Google Sheet đích.
 */

const SETUP_CONFIG = {
    FORM_TITLE: "Nhật Ký Tương Tác AI – G.P.S Toán 11",
    SHEET_TITLE: "GPS_AIedu_Data",   // Tên Sheet (thay đổi nếu cần)
    RAW_TAB: "Raw Data",
};

/**
 * Main entry point. Chạy 1 lần để setup toàn bộ.
 */
function setupFormAndSheet() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    Logger.log("=== GPS AIedu Setup ===");

    // 1. Tạo Google Form --------------------------------------------------
    const form = FormApp.create(SETUP_CONFIG.FORM_TITLE);
    form.setDescription(
        "Học sinh ghi lại mỗi lần tương tác với AI theo mô hình G.P.S.\n" +
        "G = Guide (hỏi khái niệm), P = Practice (luyện tập từng bước), S = Solve (tự giải & kiểm tra).\n\n" +
        "ĐỌC KỸ: Điền 1 lần cho MỖI câu hỏi bạn gửi AI."
    );
    form.setCollectEmail(false);
    form.setAllowResponseEdits(false);

    // Câu hỏi 1 – Student ID (tương ứng cột B)
    form.addTextItem()
        .setTitle("Mã số học sinh (Student ID)")
        .setHelpText("Ví dụ: HS0001. Dùng mã nhóm cấp, không nhập tên thật.")
        .setRequired(true);

    // Câu hỏi 2 – Class (cột C)
    const classItem = form.addMultipleChoiceItem();
    classItem.setTitle("Lớp")
        .setChoiceValues(["11A1", "11A2", "11A3", "11B1", "11B2", "Khác"])
        .setRequired(true);

    // Câu hỏi 3 – Topic (cột D)
    const topicItem = form.addMultipleChoiceItem();
    topicItem.setTitle("Chủ đề bài học")
        .setChoiceValues([
            "Hoán vị",
            "Chỉnh hợp",
            "Tổ hợp",
            "Xác suất cơ bản",
            "Xác suất có điều kiện",
            "Phân phối nhị thức",
            "Khác",
        ])
        .setRequired(true);

    // Câu hỏi 4 – Profile (cột E) – KHÔNG bắt buộc
    // Mục tiêu: tạo layout cột đúng schema (A..M) và hỗ trợ giáo viên phân tích nhẹ.
    form.addMultipleChoiceItem()
        .setTitle("Hồ sơ học tập (tự đánh giá, không bắt buộc)")
        .setHelpText("Bạn có thể bỏ qua. Nếu chọn, chỉ dùng cho phân tích tổng quan.")
        .setChoiceValues([
            "Advanced (giỏi – tự giải phần lớn)",
            "Typical (đại trà – theo G→P→S)",
            "Struggling (chậm – hay kẹt ở P)",
            "Offtrack (hay xin đáp án / lệch quy trình)",
            "Không chắc",
        ])
        .setRequired(false);

    // Câu hỏi 5 – Question (cột F)
    form.addParagraphTextItem()
        .setTitle("Câu hỏi bạn đã gửi cho AI")
        .setHelpText("Dán nguyên câu hỏi bạn gõ vào chatbot.")
        .setRequired(true);

    // Câu hỏi 6 – AI Response (cột G)
    form.addParagraphTextItem()
        .setTitle("Phần trả lời của AI")
        .setHelpText("Dán đoạn AI trả lời (hoặc tóm tắt ngắn nếu quá dài).")
        .setRequired(true);

    // Câu hỏi 7 – Notes (cột H) – tuỳ chọn
    form.addParagraphTextItem()
        .setTitle("Ghi chú thêm (không bắt buộc)")
        .setHelpText("Ví dụ: tôi thấy AI giải thích sai công thức này...");

    // Câu hỏi 8 – Satisfaction (cột I)
    const satisfactionItem = form.addScaleItem();
    satisfactionItem.setTitle("Mức độ hài lòng với câu trả lời AI")
        .setBounds(1, 5)
        .setLabels("Rất không hài lòng", "Rất hài lòng")
        .setRequired(true);

    // Câu hỏi 9 – Difficulty (cột J)
    const difficultyItem = form.addScaleItem();
    difficultyItem.setTitle("Mức độ khó của bài toán (theo cảm nhận của em)")
        .setBounds(1, 5)
        .setLabels("Rất dễ", "Rất khó")
        .setRequired(true);

    // Câu hỏi 10 – GPS Step Truth (cột K) – cho CTV check hoặc học sinh tự báo
    const gpsItem = form.addMultipleChoiceItem();
    gpsItem.setTitle("Câu hỏi này thuộc bước nào trong G.P.S?")
        .setChoiceValues([
            "G – Guide (Hỏi khái niệm / Giải thích / Công thức)",
            "P – Practice (Luyện tập từng bước / Xin gợi ý)",
            "S – Solve (Tự giải và nhờ AI kiểm tra)",
        ])
        .setRequired(true);

    // 2. Link Form → Spreadsheet ------------------------------------------
    form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

    // Lấy tab "Form Responses 1" vừa tạo, đổi tên thành "Raw Data"
    SpreadsheetApp.flush();
    Utilities.sleep(2000); // chờ Google tạo xong tab
    const responseSheet = findLatestFormResponsesSheet_(ss);
    if (!responseSheet) {
        throw new Error("Không tìm thấy sheet Form Responses sau khi link Form → Spreadsheet.");
    }

    ensureRawDataTabIsResponseSheet_(ss, responseSheet);
    const rawSheet = ss.getSheetByName(SETUP_CONFIG.RAW_TAB);
    if (!rawSheet) {
        throw new Error("Không tìm thấy tab 'Raw Data' sau khi rename Form Responses sheet.");
    }

    // 3. Chuẩn hoá header 13 cột (khớp gas_script.js CONFIG) ---------------
    rawSheet.getRange(1, 1, 1, 13).setValues([[
        "Timestamp",          // A (col 1) – tự điền bởi Form
        "Student ID",         // B (col 2) – CONFIG.STUDENT_ID_COL = 2
        "Class",              // C (col 3)
        "Topic",              // D (col 4)
        "Profile",            // E (col 5) – optional
        "Question",           // F (col 6) – CONFIG.QUESTION_COL = 6
        "AI Response",        // G (col 7) – CONFIG.RESPONSE_COL = 7
        "Notes",              // H (col 8)
        "Satisfaction (1-5)", // I (col 9)
        "Difficulty (1-5)",   // J (col 10)
        "GPS Step (Truth)",   // K (col 11)
        "Auto Label",         // L (col 12) – do not edit
        "Student Hash",       // M (col 13) – do not edit
    ]]);
    rawSheet.setFrozenRows(1);
    rawSheet.getRange(1, 1, 1, 13).setFontWeight("bold");
    rawSheet.setColumnWidth(6, 320); // Question wider
    rawSheet.setColumnWidth(7, 320); // AI Response wider
    Logger.log("Header đã được chuẩn hoá trên tab '" + SETUP_CONFIG.RAW_TAB + "'");

    // 4. Cài trigger onFormSubmit (Spreadsheet trigger) --------------------
    // Xoá trigger cũ (tránh duplicate)
    const triggers = ScriptApp.getProjectTriggers();
    for (const t of triggers) {
        if (t.getHandlerFunction() === "onFormSubmit") {
            ScriptApp.deleteTrigger(t);
        }
    }
    ScriptApp.newTrigger("onFormSubmit")
        .forSpreadsheet(ss)
        .onFormSubmit()
        .create();
    Logger.log("Trigger 'onFormSubmit' đã được cài đặt.");

    // 5. Log kết quả -------------------------------------------------------
    const formUrl = form.getPublishedUrl();
    const editUrl = form.getEditUrl();
    Logger.log("=== SETUP HOÀN TẤT ===");
    Logger.log("Form link (chia sẻ học sinh): " + formUrl);
    Logger.log("Form edit link (giáo viên):   " + editUrl);
    Logger.log("Sheet ID: " + ss.getId());
    Logger.log("Tab dữ liệu: '" + SETUP_CONFIG.RAW_TAB + "'");
    Logger.log("---");
    Logger.log("TIẾP THEO: Dán gas_script.js vào project này và chỉnh SALT + ADMIN_EMAIL.");

    // Hiện cửa sổ thông báo trong Sheet
    SpreadsheetApp.getUi().alert(
        "✅ Setup hoàn tất!\n\n" +
        "Form link (chia sẻ HS):\n" + formUrl + "\n\n" +
        "Bước tiếp theo: dán gas_script.js và chỉnh SALT + ADMIN_EMAIL."
    );
}

function findLatestFormResponsesSheet_(ss) {
    const sheets = ss.getSheets();
    for (let i = sheets.length - 1; i >= 0; i--) {
        const name = sheets[i].getName();
        if (name && name.toLowerCase().startsWith("form responses")) {
            return sheets[i];
        }
    }
    return null;
}

function ensureRawDataTabIsResponseSheet_(ss, responseSheet) {
    const existing = ss.getSheetByName(SETUP_CONFIG.RAW_TAB);
    if (existing && existing.getSheetId() !== responseSheet.getSheetId()) {
        const hasData = existing.getLastRow() > 1 || existing.getLastColumn() > 0;
        if (hasData) {
            const backupName = "Raw Data (backup " + new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-") + ")";
            existing.setName(backupName);
            Logger.log("Đã rename tab Raw Data cũ sang: " + backupName);
        } else {
            ss.deleteSheet(existing);
            Logger.log("Đã xoá tab Raw Data trống (template cũ).");
        }
    }

    if (responseSheet.getName() !== SETUP_CONFIG.RAW_TAB) {
        responseSheet.setName(SETUP_CONFIG.RAW_TAB);
        Logger.log("Đã đổi tên Form Responses sheet thành: " + SETUP_CONFIG.RAW_TAB);
    }
}
