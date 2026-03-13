/**
 * GPS Tutor Apps Script v1.0
 * Logic:
 * 1. onFormSubmit: Labels G, P, S using regex and hashes student IDs with salt.
 * 2. checkInactivity: Scans logs and sends emails if no log in 3 days.
 * 3. computeKappa: Utility to calculate agreement between two columns.
 */

// --- CONFIGURATION ---
const CONFIG = {
  SHEET_NAME: "Raw Data",
  SALT: "GPS_AI_MATH_2026", // Change this and keep offline
  STUDENT_ID_COL: 2, // Column B
  QUESTION_COL: 6,   // Column F
  RESPONSE_COL: 7,   // Column G
  LABEL_COL: 12,     // Column L (Destination for auto-label)
  HASH_COL: 13,      // Column M (Destination for Salted Hash)
  ADMIN_EMAIL: "chinh303@example.com", // Replace with actual
  DAYS_INACTIVE_LIMIT: 3
};

/**
 * Triggered on Form Submit
 */
function onFormSubmit(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  const range = e.range;
  const row = range.getRow();
  
  const studentId = e.values[CONFIG.STUDENT_ID_COL - 1];
  const question = e.values[CONFIG.QUESTION_COL - 1].toLowerCase();
  
  // 1. Labeling Logic (Regex)
  let label = "Unknown";
  if (/giải thích|khái niệm|công thức|là gì|tại sao/i.test(question)) label = "G";
  else if (/bước|hướng dẫn|kiểm tra giúp|sai ở đâu|gợi ý/i.test(question)) label = "P";
  else if (/giải|đáp án|kết quả|xong chưa|đúng không/i.test(question)) label = "S";
  
  // 2. Anonymization (Salted Hash)
  const hash = studentId ? Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, CONFIG.SALT + studentId)
    .map(b => (b < 0 ? b + 256 : b).toString(16).padStart(2, '0')).join('') : "";

  // Write to sheet
  sheet.getRange(row, CONFIG.LABEL_COL).setValue(label);
  sheet.getRange(row, CONFIG.HASH_COL).setValue(hash);
}

/**
 * Weekly/Daily Trigger to check inactivity
 */
function checkInactivity() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  const now = new Date();
  const lastLogs = {}; // student_id -> last_timestamp

  // Skip header
  for (let i = 1; i < data.length; i++) {
    const ts = new Date(data[i][0]);
    const sid = data[i][CONFIG.STUDENT_ID_COL - 1];
    if (!lastLogs[sid] || ts > lastLogs[sid]) {
      lastLogs[sid] = ts;
    }
  }

  // Check gaps
  const inactiveStudents = [];
  for (const sid in lastLogs) {
    const diffDays = (now - lastLogs[sid]) / (1000 * 60 * 60 * 24);
    if (diffDays >= CONFIG.DAYS_INACTIVE_LIMIT) {
      inactiveStudents.push(sid);
    }
  }

  if (inactiveStudents.length > 0) {
    MailApp.sendEmail(CONFIG.ADMIN_EMAIL, "GPS ALERT: Inactive Students", 
      "The following students have not logged any activity in 3+ days: " + inactiveStudents.join(", "));
  }
}
