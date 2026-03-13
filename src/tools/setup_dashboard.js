/**
 * GPS AIedu - Dashboard Setup Script (Tuần 1 Real Run)
 * ===================================================
 * Chạy hàm `setupDashboard()` MỘT LẦN để:
 *   - Tạo các tab: Per Student, GPS Tracker, Alerts
 *   - Tự điền header + công thức cơ bản theo `src/analysis/dashboard_formulas.md`
 *
 * Lưu ý: Công thức phụ thuộc tên tab dữ liệu là `Raw Data`.
 */

const DASHBOARD_CONFIG = {
  RAW_TAB: "Raw Data",
  PER_STUDENT_TAB: "Per Student",
  GPS_TRACKER_TAB: "GPS Tracker",
  ALERTS_TAB: "Alerts",
  MAX_ROWS_PREPARE: 2000 // số dòng chuẩn bị sẵn cho Per Student (dễ kéo/auto-fill)
};

function setupDashboard() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const locale = ss.getSpreadsheetLocale();
  const argSep = locale && locale.toLowerCase().startsWith("vi") ? ";" : ",";

  const raw = ss.getSheetByName(DASHBOARD_CONFIG.RAW_TAB);
  if (!raw) {
    throw new Error("Không tìm thấy tab 'Raw Data'. Hãy chạy setupFormAndSheet() trước.");
  }

  const perStudent = getOrCreateSheet_(ss, DASHBOARD_CONFIG.PER_STUDENT_TAB);
  const gpsTracker = getOrCreateSheet_(ss, DASHBOARD_CONFIG.GPS_TRACKER_TAB);
  const alerts = getOrCreateSheet_(ss, DASHBOARD_CONFIG.ALERTS_TAB);

  setupPerStudent_(perStudent, argSep);
  setupGpsTracker_(gpsTracker, argSep);
  setupAlerts_(alerts, argSep);

  SpreadsheetApp.getUi().alert(
    "✅ Dashboard setup hoàn tất!\n\n" +
    "- Per Student: công thức theo hash\n" +
    "- GPS Tracker: tổng quan G/P/S + biểu đồ\n" +
    "- Alerts: lọc Satisfaction thấp + Unknown\n\n" +
    "Nếu bạn đổi tên tab 'Raw Data', hãy cập nhật công thức tương ứng."
  );
}

function getOrCreateSheet_(ss, name) {
  let sh = ss.getSheetByName(name);
  if (!sh) sh = ss.insertSheet(name);
  sh.clear();
  return sh;
}

function toLocaleFormula_(formula, argSep) {
  if (argSep === ",") return formula;
  // Replace argument separators only (commas) outside quotes.
  let out = "";
  let inQuotes = false;
  for (let i = 0; i < formula.length; i++) {
    const ch = formula[i];
    if (ch === '"') {
      inQuotes = !inQuotes;
      out += ch;
      continue;
    }
    if (!inQuotes && ch === ",") {
      out += ";";
      continue;
    }
    out += ch;
  }
  return out;
}

function setupPerStudent_(sheet, argSep) {
  const headers = [
    "Student Hash",
    "Total Logs",
    "G Count",
    "P Count",
    "S Count",
    "%G",
    "%P",
    "%S",
    "Avg Satisfaction",
    "Avg Difficulty",
    "Last Active",
    "Days Since Last",
    "Status"
  ];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");

  // Unique hashes list in A2 (skip header row by using M2:M)
  const uniqueHashes = toLocaleFormula_(
    "=UNIQUE(FILTER('Raw Data'!M2:M,'Raw Data'!M2:M<>\"\"))",
    argSep
  );
  sheet.getRange(2, 1).setFormula(uniqueHashes);

  // Formulas in row 2; prepare down to a large number of rows so user doesn't need to drag immediately.
  const formulas = [
    null,
    "=COUNTIF('Raw Data'!M:M,A2)",
    "=COUNTIFS('Raw Data'!M:M,A2,'Raw Data'!L:L,\"G\")",
    "=COUNTIFS('Raw Data'!M:M,A2,'Raw Data'!L:L,\"P\")",
    "=COUNTIFS('Raw Data'!M:M,A2,'Raw Data'!L:L,\"S\")",
    "=IFERROR(C2/B2,0)",
    "=IFERROR(D2/B2,0)",
    "=IFERROR(E2/B2,0)",
    "=AVERAGEIF('Raw Data'!M:M,A2,'Raw Data'!I:I)",
    "=AVERAGEIF('Raw Data'!M:M,A2,'Raw Data'!J:J)",
    "=MAXIFS('Raw Data'!A:A,'Raw Data'!M:M,A2)",
    "=IFERROR(TODAY()-K2,\"–\")",
    "=IF(L2=\"–\",\"–\",IF(L2>=3,\"⚠️ Inactive\",IF(H2<0.1,\"📘 G-Heavy\",\"✅ OK\")))"
  ];

  // Apply localized formulas and set in row 2
  for (let col = 2; col <= headers.length; col++) {
    const f = formulas[col - 1];
    if (!f) continue;
    sheet.getRange(2, col).setFormula(toLocaleFormula_(f, argSep));
  }

  // Copy formulas down to MAX_ROWS_PREPARE so it "just works" for a while.
  const maxRows = DASHBOARD_CONFIG.MAX_ROWS_PREPARE;
  const fillRows = Math.max(2, maxRows);
  const sourceRange = sheet.getRange(2, 2, 1, headers.length - 1);
  const destRange = sheet.getRange(2, 2, fillRows - 1, headers.length - 1);
  sourceRange.copyTo(destRange);

  sheet.getRange(2, 6, fillRows - 1, 3).setNumberFormat("0.00%"); // %G/%P/%S
}

function setupGpsTracker_(sheet, argSep) {
  sheet.getRange(1, 1, 10, 2).setValues([
    ["Metric", "Value"],
    ["Total Logs", ""],
    ["G Total", ""],
    ["P Total", ""],
    ["S Total", ""],
    ["Unknown", ""],
    ["%G", ""],
    ["%P", ""],
    ["%S", ""],
    ["Avg Satisfaction", ""]
  ]);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, 2).setFontWeight("bold");

  const formulas = {
    B2: "=COUNTA('Raw Data'!A:A)-1",
    B3: "=COUNTIF('Raw Data'!L:L,\"G\")",
    B4: "=COUNTIF('Raw Data'!L:L,\"P\")",
    B5: "=COUNTIF('Raw Data'!L:L,\"S\")",
    B6: "=COUNTIF('Raw Data'!L:L,\"Unknown\")",
    B7: "=IFERROR(B3/B2,0)",
    B8: "=IFERROR(B4/B2,0)",
    B9: "=IFERROR(B5/B2,0)",
    B10: "=AVERAGEIF('Raw Data'!L:L,\"<>\",'Raw Data'!I:I)"
  };

  for (const a1 in formulas) {
    sheet.getRange(a1).setFormula(toLocaleFormula_(formulas[a1], argSep));
  }

  sheet.getRange("B7:B9").setNumberFormat("0.00%");

  // Create a simple pie chart for G/P/S counts if possible.
  // Data range: rows 3..5 (G/P/S) in column A (labels) and B (values)
  const chartRange = sheet.getRange("A3:B5");
  const chart = sheet.newChart()
    .setChartType(Charts.ChartType.PIE)
    .addRange(chartRange)
    .setPosition(2, 4, 0, 0)
    .setOption("title", "Phân bố G/P/S")
    .build();
  sheet.insertChart(chart);
}

function setupAlerts_(sheet, argSep) {
  sheet.getRange(1, 1, 1, 1).setValue("Alerts – Bản ghi cần chú ý");
  sheet.getRange(1, 1).setFontWeight("bold");

  sheet.getRange(3, 1).setValue("Satisfaction ≤ 2");
  sheet.getRange(3, 1).setFontWeight("bold");
  sheet.getRange(4, 1).setFormula(
    toLocaleFormula_("=FILTER('Raw Data'!A:M,'Raw Data'!I:I<=2)", argSep)
  );

  sheet.getRange(20, 1).setValue("Unknown Label");
  sheet.getRange(20, 1).setFontWeight("bold");
  sheet.getRange(21, 1).setFormula(
    toLocaleFormula_("=FILTER('Raw Data'!A:M,'Raw Data'!L:L=\"Unknown\")", argSep)
  );
}

