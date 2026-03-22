/**
 * GPS Tutor Apps Script v1.0
 * Logic:
 * 1. onFormSubmit: Labels G, P, S using regex and hashes student IDs with salt.
 * 2. checkInactivity: Scans logs and sends emails if no log in 3 days.
 */

// --- CONFIGURATION ---
const CONFIG = {
  SPREADSHEET_ID: "", // Optional: set to target a specific spreadsheet when deployed as Web App.
  SHEET_NAME: "Raw Data",
  SUMMARY_SHEET_NAME: "Summary",
  QA_SHEET_NAME: "QA - Raw Data",
  QA_RESULTS_SHEET_NAME: "QA - Results",
  SALT_PROPERTY: "GPS_STUDENT_SALT", // Store real salt in Script Properties, not in source.
  SALT_FALLBACK: "CHANGE_ME_SALT", // Quick dev fallback; replace via Script Properties in production.
  LOG_TOKEN: "CHANGE_ME_LOG_TOKEN", // Shared secret for API logging (Web App -> GAS). Keep offline.
  TELEGRAM_BOT_TOKEN: "", // Set to send alerts via Telegram.
  TELEGRAM_CHAT_ID: "",
  TELEGRAM_SATISFACTION_THRESHOLD: 2,
  STUDENT_ID_COL: 2, // Column B
  QUESTION_COL: 6,   // Column F
  RESPONSE_COL: 7,   // Column G
  SATISFACTION_COL: 9, // Column I (used by dashboard formulas)
  DIFFICULTY_COL: 10,  // Column J
  GROUND_TRUTH_COL: 11, // Column K (QA only)
  LABEL_COL: 12,     // Column L (Destination for auto-label)
  HASH_COL: 13,      // Column M (Destination for Salted Hash)
  THINKING_COL: 14,  // Column N (Thinking time minutes)
  ADMIN_EMAIL: "22022518@vnu.edu.vn", // Replace with actual
  DAYS_INACTIVE_LIMIT: 3,
  ENABLE_EMAIL_ALERTS: false // Set true in production after testing
};

function getScriptSalt_() {
  const stored = PropertiesService.getScriptProperties().getProperty(CONFIG.SALT_PROPERTY);
  if (stored && stored.trim()) return stored.trim();
  const fallback = String(CONFIG.SALT_FALLBACK || "").trim();
  if (fallback && !fallback.toLowerCase().includes("change_me")) return fallback;
  throw new Error(
    "Student ID salt not configured. Set Script Property " + CONFIG.SALT_PROPERTY + " with a secret value."
  );
}

function getSummarySnapshot_() {
  const sheet = ensureSummarySheet_();
  const lastRow = sheet.getLastRow();
  const data = lastRow > 1 ? sheet.getRange(2, 1, lastRow - 1, 2).getValues() : [];
  return { sheet, data };
}

function findStudentSummaryRecord_(studentId, snapshot) {
  const normalized = String(studentId || "").trim();
  if (!normalized || !snapshot) return { rowIndex: 0, timestamp: null };
  for (let i = 0; i < snapshot.data.length; i++) {
    if (String(snapshot.data[i][0]) === normalized) {
      return { rowIndex: i + 2, timestamp: snapshot.data[i][1] };
    }
  }
  return { rowIndex: 0, timestamp: null };
}

function computeThinkingTimeMinutes_(studentId, refTimestamp, snapshot) {
  const previous = findStudentSummaryRecord_(studentId, snapshot).timestamp;
  if (!previous) return 0;
  const prevDate = previous instanceof Date ? previous : new Date(previous);
  if (isNaN(prevDate.getTime()) || !(refTimestamp instanceof Date)) return 0;
  const diffMs = Math.max(0, refTimestamp.getTime() - prevDate.getTime());
  return Math.round((diffMs / (1000 * 60)) * 10) / 10;
}

function autoLabelAndHash_(studentId, questionText, existingLabel) {
  const normalizedLabel = normalizeLabel_(existingLabel);
  const label = normalizedLabel || classifyGpsStep(questionText);
  const hash = hashStudentId(studentId);
  return { label, hash };
}

function maybeSendTelegramAlert_(payload, thinkingMinutes) {
  const token = String(CONFIG.TELEGRAM_BOT_TOKEN || "").trim();
  const chatId = String(CONFIG.TELEGRAM_CHAT_ID || "").trim();
  if (!token || !chatId) return;

  const profile = String(payload && payload.profile || "").toLowerCase();
  const satisfaction = to1to5OrDefault_(payload && payload.satisfaction, 3);
  const lowSatisfaction = satisfaction <= CONFIG.TELEGRAM_SATISFACTION_THRESHOLD;
  const offTrack = profile.includes("offtrack") || profile.includes("off-track");
  if (!lowSatisfaction && !offTrack) return;

  const parts = [
    "⚠️ GPS ALERT",
    `Student: ${payload.studentId || "N/A"}`,
    `Class: ${payload.className || "N/A"}`,
    `Profile: ${payload.profile || "N/A"}`,
    `Topic: ${payload.topic || "N/A"}`,
    `Satisfaction: ${satisfaction}`,
    `Thinking time: ${thinkingMinutes ? thinkingMinutes + " min" : "0 min"}`,
    `Flags: ${payload.behaviorFlags || "none"}`,
    `Question: ${payload.question || ""}`.trim()
  ];

  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  try {
    const response = UrlFetchApp.fetch(url, {
      method: "post",
      payload: {
        chat_id: chatId,
        text: parts.filter(Boolean).join("\n"),
        parse_mode: "HTML"
      },
      muteHttpExceptions: true
    });
    if (!response || response.getResponseCode() < 200 || response.getResponseCode() >= 300) {
      Logger.log("Telegram alert failed: " + (response.getContentText ? response.getContentText() : "no response"));
    }
  } catch (err) {
    Logger.log("Telegram alert error: " + err.message);
  }
}

/**
 * Web App endpoint for auto-logging (Option B).
 * Deploy this Apps Script as a Web App and POST JSON to it.
 *
 * Expected JSON:
 * {
 *   "token": "...",
 *   "studentId": "HS0001",
 *   "className": "11A1",
 *   "topic": "Xác suất cơ bản",
 *   "profile": "Typical ...",
 *   "question": "...",
 *   "aiResponse": "...",
 *   "notes": "",
 *   "satisfaction": 3,
 *   "difficulty": 3,
 *   "gpsTruth": "G" | "P" | "S" | "",
 *   "gpsAuto": "G" | "P" | "S" | "",
 *   "behaviorFlags": "skip_step,looping,prompt_injection"
 * }
 */
function doPost(e) {
  try {
    const payload = parseJsonBody_(e);
    assertToken_(payload);
    if (isDuplicateMessage_(payload)) {
      return jsonResponse_({ ok: true, deduped: true });
    }

    const ss = CONFIG.SPREADSHEET_ID
      ? SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID)
      : SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
    if (!sheet) throw new Error("Raw Data sheet not found: " + CONFIG.SHEET_NAME);

    const now = new Date();
    const summarySnapshot = getSummarySnapshot_();
    const thinkingMinutes = computeThinkingTimeMinutes_(payload.studentId, now, summarySnapshot);
    const rowWithExtras = buildRawRowFromPayload_(payload, now, thinkingMinutes);
    sheet.getRange(sheet.getLastRow() + 1, 1, 1, rowWithExtras.length).setValues([rowWithExtras]);
    const row = sheet.getLastRow();
    updateSummaryFromRow_(rowWithExtras, summarySnapshot);
    maybeSendTelegramAlert_(payload, thinkingMinutes);

    return jsonResponse_({ ok: true, row });
  } catch (err) {
    return jsonResponse_({ ok: false, error: String(err && err.message ? err.message : err) }, 400);
  }
}

function isDuplicateMessage_(payload) {
  const messageId = payload && payload.messageId ? String(payload.messageId).trim() : "";
  if (!messageId) return false;

  const cache = CacheService.getScriptCache();
  const key = "gps_msg_" + messageId;
  if (cache.get(key)) return true;
  cache.put(key, "1", 6 * 60 * 60); // 6 hours
  return false;
}

function parseJsonBody_(e) {
  if (!e || !e.postData || !e.postData.contents) return {};
  const raw = String(e.postData.contents || "").trim();
  if (!raw) return {};
  return JSON.parse(raw);
}

function assertToken_(payload) {
  const token = payload && (payload.token || payload.LOG_TOKEN || payload.secret);
  if (!CONFIG.LOG_TOKEN || CONFIG.LOG_TOKEN === "CHANGE_ME_LOG_TOKEN") {
    throw new Error("CONFIG.LOG_TOKEN not configured.");
  }
  if (!token || token !== CONFIG.LOG_TOKEN) {
    throw new Error("Unauthorized.");
  }
}

function buildRawRowFromPayload_(payload, timestamp, thinkingMinutes) {
  const now = timestamp instanceof Date ? timestamp : new Date();
  const studentId = String((payload && payload.studentId) || "").trim();
  const className = String((payload && payload.className) || "").trim();
  const topic = String((payload && payload.topic) || "").trim();
  const profile = String((payload && payload.profile) || "").trim();
  const question = String((payload && payload.question) || "").trim();
  const aiResponse = String((payload && payload.aiResponse) || "").trim();
  const notes = String((payload && payload.notes) || "").trim();
  const behaviorFlags = String((payload && payload.behaviorFlags) || "").trim();
  const notesCombined = behaviorFlags
    ? (notes ? (notes + " | behavior:" + behaviorFlags) : ("behavior:" + behaviorFlags))
    : notes;

  // Defaults: keep dashboard stable even when MVP skips ratings.
  const satisfaction = to1to5OrDefault_(payload && payload.satisfaction, 3);
  const difficulty = to1to5OrDefault_(payload && payload.difficulty, 3);

  const gpsTruth = normalizeLabel_(payload && payload.gpsTruth);
  const { label, hash } = autoLabelAndHash_(studentId, question, payload && payload.gpsAuto);
  const thinkingTime = typeof thinkingMinutes === "number" && isFinite(thinkingMinutes) ? thinkingMinutes : 0;

  // A..N (14 columns)
  return [
    now,        // A Timestamp
    studentId,  // B Student ID
    className,  // C Class
    topic,      // D Topic
    profile,    // E Profile
    question,   // F Question
    aiResponse, // G AI Response
    notesCombined, // H Notes
    satisfaction, // I Satisfaction (1-5)
    difficulty,   // J Difficulty (1-5)
    gpsTruth,     // K GPS Step (Truth)
    label,        // L Auto Label
    hash,         // M Student Hash
    thinkingTime  // N Thinking Time (minutes)
  ];
}

function to1to5OrDefault_(value, defaultValue) {
  if (value === null || value === undefined || value === "") return defaultValue;
  const n = Number(value);
  if (!isFinite(n)) return defaultValue;
  if (n < 1) return 1;
  if (n > 5) return 5;
  return Math.round(n);
}

function jsonResponse_(obj, statusCode) {
  const output = ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
  return output;
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("GPS QA")
    .addItem("Init Raw Data Schema", "initRawDataSchema")
    .addItem("Setup QA Sheets", "qaSetupSheets")
    .addItem("Seed Realistic Mock Data", "qaSeedRealisticMockData")
    .addItem("Run Week1 Smoke Test", "qaRunWeek1SmokeTest")
    .addToUi();
}

function initRawDataSchema() {
  const ss = CONFIG.SPREADSHEET_ID
    ? SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID)
    : SpreadsheetApp.getActiveSpreadsheet();

  const sheet = ss.getSheetByName(CONFIG.SHEET_NAME) || ss.insertSheet(CONFIG.SHEET_NAME);

  sheet.getRange(1, 1, 1, CONFIG.THINKING_COL).setValues([[
    "Timestamp",          // A
    "Student ID",         // B
    "Class",              // C
    "Topic",              // D
    "Profile",            // E
    "Question",           // F
    "AI Response",        // G
    "Notes",              // H
    "Satisfaction (1-5)", // I
    "Difficulty (1-5)",   // J
    "GPS Step (Truth)",   // K
    "Auto Label",         // L
    "Student Hash",       // M
    "Thinking Time (minutes)" // N
  ]]);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, CONFIG.THINKING_COL).setFontWeight("bold");
  sheet.setColumnWidth(6, 320);
  sheet.setColumnWidth(7, 320);
  sheet.setColumnWidth(CONFIG.THINKING_COL, 120);

  SpreadsheetApp.flush();
  Logger.log("Initialized schema for sheet: " + CONFIG.SHEET_NAME);
}

function normalizeForMatch(text) {
  if (text === null || text === undefined) return "";
  let t = String(text).toLowerCase().trim();
  t = t.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  t = t.replace(/đ/g, "d");
  t = t.replace(/\s+/g, " ");
  return t;
}

function classifyGpsStep(questionText) {
  const q = normalizeForMatch(questionText);

  // Guide: conceptual / definitions / explain-why
  if (/(giai thich|khai niem|cong thuc|la gi|tai sao|dinh nghia|phan biet|tom tat)/i.test(q)) return "G";

  // Practice: step-by-step guidance / hints / stuck
  if (/(huong dan|goi y|buoc|em bi ket|lam the nao|sai o dau|kiem tra buoc)/i.test(q)) return "P";

  // Solve: ask for final answer / verify result / "solve for me" (off-protocol)
  if (/(dap an|ket qua|dung khong|xong chua|kiem tra loi giai|giai giup|ra (ket qua|dap an))/i.test(q)) return "S";

  return "Unknown";
}

function hashStudentId(studentId) {
  if (!studentId) return "";
  const salt = getScriptSalt_();
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, salt + studentId)
    .map(b => (b < 0 ? b + 256 : b).toString(16).padStart(2, "0"))
    .join("");
}

function processSubmissionRow(sheet, row, values) {
  const studentId = values[CONFIG.STUDENT_ID_COL - 1] || "";
  const questionText = values[CONFIG.QUESTION_COL - 1] || "";

  const { label, hash } = autoLabelAndHash_(studentId, questionText, values[CONFIG.LABEL_COL - 1]);

  sheet.getRange(row, CONFIG.LABEL_COL, 1, 2).setValues([[label, hash]]);
}

function normalizeLabel_(value) {
  const raw = String(value || "").trim().toUpperCase();
  if (raw === "G" || raw === "P" || raw === "S") return raw;
  return "";
}

function ensureSummarySheet_() {
  const ss = CONFIG.SPREADSHEET_ID
    ? SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID)
    : SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(CONFIG.SUMMARY_SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(CONFIG.SUMMARY_SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, 2).setValues([["Student ID", "Last Timestamp"]]);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function updateSummaryFromRow_(values, snapshot) {
  const studentId = values[CONFIG.STUDENT_ID_COL - 1];
  if (!studentId) return;

  const tsRaw = values[0];
  const ts = tsRaw instanceof Date ? tsRaw : new Date(tsRaw);
  if (!(ts instanceof Date) || isNaN(ts.getTime())) return;

  const summaryInfo = snapshot || getSummarySnapshot_();
  const summary = summaryInfo.sheet;
  const data = summaryInfo.data;
  if (!data || data.length === 0) {
    summary.appendRow([studentId, ts]);
    return;
  }

  for (let i = 0; i < data.length; i++) {
    if (String(data[i][0]) === String(studentId)) {
      const existing = data[i][1];
      const existingTs = existing instanceof Date ? existing : new Date(existing);
      if (!(existingTs instanceof Date) || isNaN(existingTs.getTime()) || ts > existingTs) {
        summary.getRange(i + 2, 1, 1, 2).setValues([[studentId, ts]]);
      }
      return;
    }
  }

  summary.appendRow([studentId, ts]);
}

function rebuildSummaryFromRaw_() {
  const ss = CONFIG.SPREADSHEET_ID
    ? SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID)
    : SpreadsheetApp.getActiveSpreadsheet();
  const raw = ss.getSheetByName(CONFIG.SHEET_NAME);
  if (!raw) return;

  const data = raw.getDataRange().getValues();
  if (data.length < 2) return;

  const lastLogs = {}; // student_id -> last_timestamp
  for (let i = 1; i < data.length; i++) {
    const ts = data[i][0];
    const sid = data[i][CONFIG.STUDENT_ID_COL - 1];
    if (!sid || !(ts instanceof Date)) continue;
    if (!lastLogs[sid] || ts > lastLogs[sid]) {
      lastLogs[sid] = ts;
    }
  }

  const rows = Object.keys(lastLogs)
    .sort()
    .map(sid => [sid, lastLogs[sid]]);

  const summary = ensureSummarySheet_();
  summary.clear();
  summary.getRange(1, 1, 1, 2).setValues([["Student ID", "Last Timestamp"]]);
  if (rows.length > 0) {
    summary.getRange(2, 1, rows.length, 2).setValues(rows);
  }
  summary.setFrozenRows(1);
}

/**
 * Triggered on Form Submit
 */
function onFormSubmit(e) {
  if (!e || !e.range || !e.values) {
    throw new Error("onFormSubmit expects a Spreadsheet onFormSubmit trigger (event with range/values).");
  }

  const sheet = e.range.getSheet();
  if (!sheet || sheet.getName() !== CONFIG.SHEET_NAME) return;

  processSubmissionRow(sheet, e.range.getRow(), e.values);
  updateSummaryFromRow_(e.values);
}

/**
 * Weekly/Daily Trigger to check inactivity
 */
function checkInactivity() {
  const summary = ensureSummarySheet_();
  if (summary.getLastRow() < 2) {
    rebuildSummaryFromRaw_();
  }
  const lastRow = summary.getLastRow();
  if (lastRow < 2) {
    Logger.log("No summary data found.");
    return;
  }
  const data = summary.getRange(2, 1, lastRow - 1, 2).getValues();
  const now = new Date();

  // Check gaps
  const inactiveStudents = [];
  for (let i = 0; i < data.length; i++) {
    const sid = data[i][0];
    const tsRaw = data[i][1];
    const ts = tsRaw instanceof Date ? tsRaw : new Date(tsRaw);
    if (!sid || !(ts instanceof Date) || isNaN(ts.getTime())) continue;
    const diffDays = (now - ts) / (1000 * 60 * 60 * 24);
    if (diffDays >= CONFIG.DAYS_INACTIVE_LIMIT) {
      inactiveStudents.push(sid);
    }
  }

  if (!CONFIG.ENABLE_EMAIL_ALERTS) {
    Logger.log("Email alerts disabled. Inactive students: " + inactiveStudents.join(", "));
    return;
  }

  if (inactiveStudents.length > 0) {
    MailApp.sendEmail(CONFIG.ADMIN_EMAIL, "GPS ALERT: Inactive Students", 
      "The following students have not logged any activity in 3+ days: " + inactiveStudents.join(", "));
  }
}

// --------------------
// QA / Automation helpers (Week 1)
// --------------------

function qaSetupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const raw = ss.getSheetByName(CONFIG.QA_SHEET_NAME) || ss.insertSheet(CONFIG.QA_SHEET_NAME);
  raw.clear();
  raw.getRange(1, 1, 1, CONFIG.THINKING_COL).setValues([[
    "Timestamp",          // A
    "Student ID",         // B
    "Class",              // C
    "Topic",              // D
    "Profile",            // E (archetype)
    "Question",           // F
    "AI Response",        // G
    "Notes",              // H (optional)
    "Satisfaction (1-5)", // I
    "Difficulty (1-5)",   // J
    "GPS Step (Truth)",   // K (QA only)
    "Auto Label",         // L (written by script)
    "Student Hash",       // M (written by script)
    "Thinking Time (minutes)" // N
  ]]);
  raw.setFrozenRows(1);

  const results = ss.getSheetByName(CONFIG.QA_RESULTS_SHEET_NAME) || ss.insertSheet(CONFIG.QA_RESULTS_SHEET_NAME);
  results.clear();
  results.getRange(1, 1).setValue("QA Results (Week 1)");
  results.setFrozenRows(1);
}

function qaSeedRealisticMockData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.QA_SHEET_NAME);
  if (!sheet) throw new Error("QA sheet not found. Run qaSetupSheets() first.");

  const now = new Date();
  const start = new Date(now.getTime() - 6 * 24 * 60 * 60 * 1000);

  const students = qaGenerateStudents_(80);
  const rows = qaGenerateLogs_(students, start, now, 650);
  if (rows.length === 0) return;

  const startRow = sheet.getLastRow() + 1;
  sheet.getRange(startRow, 1, rows.length, CONFIG.THINKING_COL).setValues(rows);

  for (let i = 0; i < rows.length; i++) {
    processSubmissionRow(sheet, startRow + i, rows[i]);
  }
}

function qaRunWeek1SmokeTest() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.QA_SHEET_NAME);
  const results = ss.getSheetByName(CONFIG.QA_RESULTS_SHEET_NAME);
  if (!sheet || !results) throw new Error("QA sheets not found. Run qaSetupSheets() first.");

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) throw new Error("No QA data found. Run qaSeedRealisticMockData() first.");

  const data = sheet.getRange(2, 1, lastRow - 1, 13).getValues();

  let total = 0;
  let labeled = 0;
  let correct = 0;
  let hashOk = 0;
  const profileCounts = {};
  const truthCounts = { G: 0, P: 0, S: 0, Unknown: 0 };
  const predCounts = { G: 0, P: 0, S: 0, Unknown: 0 };
  const mismatches = [];

  for (let i = 0; i < data.length; i++) {
    const row = data[i];
    const profile = row[4] || "Unknown";
    const truth = row[CONFIG.GROUND_TRUTH_COL - 1] || "Unknown";
    const pred = row[CONFIG.LABEL_COL - 1] || "Unknown";
    const hash = row[CONFIG.HASH_COL - 1] || "";

    profileCounts[profile] = (profileCounts[profile] || 0) + 1;

    truthCounts[truth] = (truthCounts[truth] || 0) + 1;
    predCounts[pred] = (predCounts[pred] || 0) + 1;

    total += 1;
    if (pred !== "Unknown") labeled += 1;
    if (/^[a-f0-9]{64}$/i.test(hash)) hashOk += 1;
    if (truth === pred) correct += 1;
    else mismatches.push([i + 2, truth, pred, row[5]]); // row number, truth, pred, question
  }

  const accuracy = total ? (correct / total) : 0;
  const inactiveStudents = qaComputeInactiveStudents_(data, new Date(), CONFIG.DAYS_INACTIVE_LIMIT);

  results.clear();
  results.getRange(1, 1).setValue("QA Results (Week 1)");
  results.getRange(2, 1, 9, 2).setValues([
    ["Total logs", total],
    ["Labeled (pred != Unknown)", labeled],
    ["Correct labels", correct],
    ["Accuracy", accuracy],
    ["Hash OK (64 hex)", hashOk],
    ["Distinct students", Object.keys(qaDistinctStudents_(data)).length],
    ["Inactive students (>= limit)", inactiveStudents.length],
    ["DAYS_INACTIVE_LIMIT", CONFIG.DAYS_INACTIVE_LIMIT],
    ["ENABLE_EMAIL_ALERTS", CONFIG.ENABLE_EMAIL_ALERTS]
  ]);

  results.getRange(2, 4).setValue("Inactive student IDs (sample)");
  results.getRange(3, 4).setValue(inactiveStudents.slice(0, 30).join(", "));

  results.getRange(12, 1).setValue("Profile counts (rows)");
  qaWriteKeyValueTable_(results, 13, 1, profileCounts);

  results.getRange(12, 4).setValue("Truth step counts");
  qaWriteKeyValueTable_(results, 13, 4, truthCounts);

  results.getRange(12, 7).setValue("Pred step counts");
  qaWriteKeyValueTable_(results, 13, 7, predCounts);

  results.getRange(2, 7).setValue("Mismatches (first 30)");
  if (mismatches.length > 0) {
    results.getRange(3, 7, Math.min(30, mismatches.length), 4).setValues(
      mismatches.slice(0, 30).map(m => [m[0], m[1], m[2], m[3]])
    );
  }
}

function qaWriteKeyValueTable_(sheet, startRow, startCol, obj) {
  const entries = Object.keys(obj).sort().map(k => [k, obj[k]]);
  if (entries.length === 0) return;
  sheet.getRange(startRow, startCol, entries.length, 2).setValues(entries);
}

function qaDistinctStudents_(dataRows) {
  const students = {};
  for (let i = 0; i < dataRows.length; i++) {
    const sid = dataRows[i][CONFIG.STUDENT_ID_COL - 1];
    if (sid) students[sid] = true;
  }
  return students;
}

function qaComputeInactiveStudents_(dataRows, now, daysLimit) {
  const lastLogs = {};

  for (let i = 0; i < dataRows.length; i++) {
    const ts = dataRows[i][0];
    const sid = dataRows[i][CONFIG.STUDENT_ID_COL - 1];
    if (!sid || !(ts instanceof Date)) continue;
    if (!lastLogs[sid] || ts > lastLogs[sid]) lastLogs[sid] = ts;
  }

  const inactive = [];
  for (const sid in lastLogs) {
    const diffDays = (now - lastLogs[sid]) / (1000 * 60 * 60 * 24);
    if (diffDays >= daysLimit) inactive.push(sid);
  }
  inactive.sort();
  return inactive;
}

function qaWeightedPick_(items) {
  const total = items.reduce((sum, it) => sum + it.w, 0);
  let r = Math.random() * total;
  for (let i = 0; i < items.length; i++) {
    r -= items[i].w;
    if (r <= 0) return items[i].v;
  }
  return items[items.length - 1].v;
}

function qaRandInt_(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function qaChoose_(arr) {
  return arr[qaRandInt_(0, arr.length - 1)];
}

function qaGenerateStudents_(count) {
  const students = [];
  for (let i = 1; i <= count; i++) {
    const sid = "HS" + String(i).padStart(4, "0");
    const profile = qaWeightedPick_([
      { v: "advanced", w: 10 },
      { v: "typical", w: 75 },
      { v: "struggling", w: 10 },
      { v: "offtrack", w: 5 }
    ]);
    const speed = qaWeightedPick_([
      { v: "fast", w: 30 },
      { v: "normal", w: 55 },
      { v: "slow", w: 15 }
    ]);
    const clazz = qaChoose_(["11A1", "11A2", "11A3"]);
    students.push({ sid, profile, speed, clazz });
  }
  return students;
}

function qaGenerateLogs_(students, startDate, endDate, totalLogs) {
  const topics = [
    { topic: "Hoán vị", g: "Giải thích hoán vị là gì?", p: "Hướng dẫn từng bước tính hoán vị n!", s: "Em ra kết quả 120, đúng không?" },
    { topic: "Chỉnh hợp", g: "Phân biệt chỉnh hợp và tổ hợp giúp em.", p: "Em bị kẹt ở bước chọn k từ n, gợi ý giúp.", s: "Kiểm tra lời giải của em với A(n,k) được không?" },
    { topic: "Tổ hợp", g: "Diễn giải công thức C(n,k) theo cách dễ hiểu.", p: "Hướng dẫn em từng bước giải bài chọn 3 từ 10.", s: "C(5,2)=10 đúng không ạ?" },
    { topic: "Xác suất", g: "Xác suất là gì và công thức cơ bản?", p: "Gợi ý cách lập không gian mẫu cho bài này.", s: "Em ra P=0.5, đúng không?" },
    { topic: "Xác suất có điều kiện", g: "Giải thích xác suất có điều kiện là gì.", p: "Hướng dẫn em tính P(A|B) theo từng bước.", s: "Kết quả cuối cùng của em hợp lý chưa?" }
  ];

  const aiResponses = {
    G: [
      "Mình giải thích khái niệm và ý nghĩa trước nhé, rồi em thử áp dụng vào ví dụ.",
      "Ta nắm định nghĩa và công thức tổng quát, sau đó xác định n và k trong đề."
    ],
    P: [
      "Mình chia thành 3 bước: (1) xác định n,k (2) chọn công thức (3) thay số và tính. Em làm bước (1) trước nhé.",
      "Em thử viết không gian mẫu/đếm số cách trước. Nếu kẹt ở bước nào nói mình biết."
    ],
    S: [
      "Mình sẽ kiểm tra logic và tính toán của em. Em ghi rõ lập luận và phép tính giúp mình.",
      "Mình không giải hộ, nhưng có thể đối chiếu kết quả và chỉ ra chỗ sai nếu có."
    ]
  };

  let rows = [];
  if (students.length === 0 || totalLogs <= 0) return rows;

  const dayMs = 24 * 60 * 60 * 1000;
  const dayCount = Math.max(1, Math.floor((endDate.getTime() - startDate.getTime()) / dayMs) + 1);
  const sessionStartMin = 8 * 60;  // 08:00
  const sessionStartMax = 21 * 60; // 21:00

  function pickSessionCount(profile) {
    if (profile === "advanced") return qaRandInt_(2, 5);
    if (profile === "typical") return qaRandInt_(3, 8);
    if (profile === "struggling") return qaRandInt_(4, 10);
    return qaRandInt_(1, 4); // offtrack
  }

  function pickDayOffset(profile) {
    // Create a small group with early stop to exercise inactivity detection.
    if (profile === "offtrack") return qaRandInt_(0, Math.min(dayCount - 1, 2));
    if (profile === "struggling") return qaRandInt_(0, Math.min(dayCount - 1, 4));
    return qaRandInt_(0, dayCount - 1);
  }

  function pickStepSequence(profile) {
    if (profile === "advanced") {
      return qaWeightedPick_([
        { v: ["P", "S"], w: 50 },
        { v: ["S"], w: 30 },
        { v: ["G", "S"], w: 20 }
      ]);
    }
    if (profile === "typical") {
      return qaWeightedPick_([
        { v: ["G", "P", "S"], w: 70 },
        { v: ["G", "P", "P", "S"], w: 25 },
        { v: ["G", "P"], w: 5 }
      ]);
    }
    if (profile === "struggling") {
      return qaWeightedPick_([
        { v: ["G", "P", "P"], w: 55 },
        { v: ["G", "P", "P", "S"], w: 20 },
        { v: ["G", "P"], w: 25 }
      ]);
    }
    return qaWeightedPick_([
      { v: ["S"], w: 70 },
      { v: ["S", "S"], w: 25 },
      { v: ["G", "S"], w: 5 }
    ]);
  }

  function gapMinutes(speed) {
    if (speed === "fast") return qaRandInt_(1, 4);
    if (speed === "slow") return qaRandInt_(10, 25);
    return qaRandInt_(4, 12);
  }

  function pickQuestion(t, profile, step, stepIndex) {
    if (profile === "offtrack" && step === "S") {
      return qaChoose_([
        "Giải giúp em bài này với ạ.",
        "Cho em đáp án cuối cùng luôn được không?",
        "Em cần kết quả nhanh, cho em đáp án."
      ]);
    }
    if (step === "G") return t.g;
    if (step === "P") {
      if (stepIndex > 0) return qaChoose_([t.p, "Gợi ý bước 2 giúp em với.", "Em bị kẹt ở bước này, hướng dẫn em."]);
      return t.p;
    }
    return t.s;
  }

  function pickSatisfaction(profile, step) {
    if (profile === "advanced") return qaRandInt_(4, 5);
    if (profile === "typical") return step === "S" ? qaRandInt_(4, 5) : qaRandInt_(3, 5);
    if (profile === "struggling") return step === "S" ? qaRandInt_(3, 5) : qaRandInt_(2, 4);
    return qaRandInt_(1, 3);
  }

  function pickDifficulty(profile, step) {
    if (profile === "advanced") return qaRandInt_(1, 3);
    if (profile === "typical") return step === "S" ? qaRandInt_(2, 4) : qaRandInt_(2, 4);
    if (profile === "struggling") return step === "S" ? qaRandInt_(3, 5) : qaRandInt_(3, 5);
    return qaRandInt_(4, 5);
  }

  for (let si = 0; si < students.length; si++) {
    const st = students[si];
    const sessions = pickSessionCount(st.profile);

    for (let s = 0; s < sessions; s++) {
      const dayOffset = pickDayOffset(st.profile);
      const minuteOfDay = qaRandInt_(sessionStartMin, sessionStartMax);
      const sessionStart = new Date(startDate.getTime() + dayOffset * dayMs + minuteOfDay * 60 * 1000);
      const t = qaChoose_(topics);
      const seq = pickStepSequence(st.profile);

      let ts = sessionStart;
      for (let i = 0; i < seq.length; i++) {
        if (i > 0) ts = new Date(ts.getTime() + gapMinutes(st.speed) * 60 * 1000);
        const step = seq[i];
        const question = pickQuestion(t, st.profile, step, i);
        const aiResponse = qaChoose_(aiResponses[step]);

        rows.push([
          ts,                // A Timestamp
          st.sid,            // B Student ID
          st.clazz,          // C Class
          t.topic,           // D Topic
          st.profile,        // E Profile
          question,          // F Question
          aiResponse,        // G AI Response
          "",                // H Notes
          pickSatisfaction(st.profile, step), // I Satisfaction
          pickDifficulty(st.profile, step),   // J Difficulty
          step,              // K Ground truth step (QA)
          "",                // L Auto label (filled)
          "",                // M Hash (filled)
          0                  // N Thinking time placeholder
        ]);
      }
    }
  }

  rows.sort((a, b) => a[0].getTime() - b[0].getTime());
  if (rows.length > totalLogs) {
    rows = rows.slice(0, totalLogs);
  }

  // If we still need more rows, top up with additional random sessions.
  while (rows.length < totalLogs) {
    const st = qaChoose_(students);
    const t = qaChoose_(topics);
    const seq = pickStepSequence(st.profile);
    const dayOffset = pickDayOffset(st.profile);
    const minuteOfDay = qaRandInt_(sessionStartMin, sessionStartMax);
    const sessionStart = new Date(startDate.getTime() + dayOffset * dayMs + minuteOfDay * 60 * 1000);

    let ts = sessionStart;
    for (let i = 0; i < seq.length && rows.length < totalLogs; i++) {
      if (i > 0) ts = new Date(ts.getTime() + gapMinutes(st.speed) * 60 * 1000);
      const step = seq[i];
      rows.push([
        ts,
        st.sid,
        st.clazz,
        t.topic,
        st.profile,
        pickQuestion(t, st.profile, step, i),
        qaChoose_(aiResponses[step]),
        "",
        pickSatisfaction(st.profile, step),
        pickDifficulty(st.profile, step),
        step,
        "",
        "",
        0
      ]);
    }
  }

 assignThinkingTimeToRows(rows);
 return rows;
}

function assignThinkingTimeToRows(rows) {
  const lastSeen = {};
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const sid = row[CONFIG.STUDENT_ID_COL - 1];
    const tsRaw = row[0];
    const ts = tsRaw instanceof Date ? tsRaw : new Date(tsRaw);
    let thinking = 0;
    if (sid && lastSeen[sid] instanceof Date && ts instanceof Date && !isNaN(ts.getTime())) {
      const prev = lastSeen[sid];
      thinking = Math.max(0, (ts.getTime() - prev.getTime()) / (1000 * 60));
    }
    row[CONFIG.THINKING_COL - 1] = Math.round(thinking * 10) / 10;
    if (sid && ts instanceof Date && !isNaN(ts.getTime())) {
      lastSeen[sid] = ts;
    }
  }
}
