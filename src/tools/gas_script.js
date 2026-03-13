/**
 * GPS Tutor Apps Script v1.0
 * Logic:
 * 1. onFormSubmit: Labels G, P, S using regex and hashes student IDs with salt.
 * 2. checkInactivity: Scans logs and sends emails if no log in 3 days.
 */

// --- CONFIGURATION ---
const CONFIG = {
  SHEET_NAME: "Raw Data",
  QA_SHEET_NAME: "QA - Raw Data",
  QA_RESULTS_SHEET_NAME: "QA - Results",
  SALT: "GPS_AI_MATH_2026", // Change this and keep offline
  STUDENT_ID_COL: 2, // Column B
  QUESTION_COL: 6,   // Column F
  RESPONSE_COL: 7,   // Column G
  SATISFACTION_COL: 9, // Column I (used by dashboard formulas)
  DIFFICULTY_COL: 10,  // Column J
  GROUND_TRUTH_COL: 11, // Column K (QA only)
  LABEL_COL: 12,     // Column L (Destination for auto-label)
  HASH_COL: 13,      // Column M (Destination for Salted Hash)
  ADMIN_EMAIL: "chinh303@example.com", // Replace with actual
  DAYS_INACTIVE_LIMIT: 3,
  ENABLE_EMAIL_ALERTS: false // Set true in production after testing
};

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("GPS QA")
    .addItem("Setup QA Sheets", "qaSetupSheets")
    .addItem("Seed Realistic Mock Data", "qaSeedRealisticMockData")
    .addItem("Run Week1 Smoke Test", "qaRunWeek1SmokeTest")
    .addToUi();
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
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, CONFIG.SALT + studentId)
    .map(b => (b < 0 ? b + 256 : b).toString(16).padStart(2, "0"))
    .join("");
}

function processSubmissionRow(sheet, row, values) {
  const studentId = values[CONFIG.STUDENT_ID_COL - 1] || "";
  const questionText = values[CONFIG.QUESTION_COL - 1] || "";

  const label = classifyGpsStep(questionText);
  const hash = hashStudentId(studentId);

  sheet.getRange(row, CONFIG.LABEL_COL).setValue(label);
  sheet.getRange(row, CONFIG.HASH_COL).setValue(hash);
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
    if (!sid || !ts || isNaN(ts.getTime())) continue;
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
  raw.getRange(1, 1, 1, 13).setValues([[
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
    "Student Hash"        // M (written by script)
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
  sheet.getRange(startRow, 1, rows.length, 13).setValues(rows);

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

  const rows = [];
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
          ""                 // M Hash (filled)
        ]);
      }
    }
  }

  rows.sort((a, b) => a[0].getTime() - b[0].getTime());
  if (rows.length > totalLogs) return rows.slice(0, totalLogs);

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
        ""
      ]);
    }
  }

  return rows;
}
