/*
 * Google Apps Script for GPS study
 * - Auto label G/P/S based on regex
 * - Send reminder emails for inactivity (3 days)
 */

var CONFIG = {
  SHEET_NAME: "Form Responses 1",
  COL_TIMESTAMP: 1,
  COL_STUDENT_ID: 2,
  COL_QUESTION: 3,
  COL_RESPONSE: 4,
  COL_GPS_STEP: 5,
  COL_EMAIL: 6,
  INACTIVITY_DAYS: 3
};

function onFormSubmit(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) return;

  var row = e.range.getRow();
  var question = sheet.getRange(row, CONFIG.COL_QUESTION).getValue();
  var response = sheet.getRange(row, CONFIG.COL_RESPONSE).getValue();
  var label = classifyGPS(question + " " + response);

  sheet.getRange(row, CONFIG.COL_GPS_STEP).setValue(label);
}

function classifyGPS(text) {
  var t = (text || "").toLowerCase();

  var guidePatterns = [
    /giải thích/, /định nghĩa/, /khái niệm/, /công thức/, /khác nhau/, /khi nào/, /vì sao/, /như thế nào/
  ];
  var practicePatterns = [
    /từng bước/, /từng bước một/, /gợi ý/, /hướng dẫn/, /giúp em/, /dẫn dắt/, /walk me through/, /step by step/
  ];
  var solvePatterns = [
    /đáp án/, /kết quả/, /giải bài/, /giải giúp/, /trả lời cuối/, /tính giúp/, /làm hộ/
  ];

  if (matchesAny(t, guidePatterns)) return "G";
  if (matchesAny(t, practicePatterns)) return "P";
  if (matchesAny(t, solvePatterns)) return "S";

  return "P"; // default to Practice when unclear
}

function matchesAny(text, patterns) {
  for (var i = 0; i < patterns.length; i++) {
    if (patterns[i].test(text)) return true;
  }
  return false;
}

function checkInactivity() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) return;

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  var data = sheet.getRange(2, 1, lastRow - 1, 6).getValues();
  var now = new Date();
  var lastSeenByStudent = {};
  var emailByStudent = {};

  for (var i = 0; i < data.length; i++) {
    var ts = data[i][CONFIG.COL_TIMESTAMP - 1];
    var studentId = data[i][CONFIG.COL_STUDENT_ID - 1];
    var email = data[i][CONFIG.COL_EMAIL - 1];

    if (!studentId) continue;
    if (email) emailByStudent[studentId] = email;
    if (!lastSeenByStudent[studentId] || ts > lastSeenByStudent[studentId]) {
      lastSeenByStudent[studentId] = ts;
    }
  }

  for (var id in lastSeenByStudent) {
    var lastSeen = lastSeenByStudent[id];
    var diffDays = (now - lastSeen) / (1000 * 60 * 60 * 24);
    if (diffDays >= CONFIG.INACTIVITY_DAYS) {
      var to = emailByStudent[id];
      if (to) {
        MailApp.sendEmail(to, "Nhắc nhở học tập GPS", "Đã 3 ngày bạn chưa nộp nhật ký học tập. Vui lòng nộp lần tiếp theo.");
      }
    }
  }
}
