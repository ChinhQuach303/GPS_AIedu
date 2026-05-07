import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze simulated_conversations.csv by week and by student, and output reports."
    )
    parser.add_argument(
        "--input",
        default="simulated_conversations.csv",
        help="Path to input CSV (default: simulated_conversations.csv)",
    )
    parser.add_argument(
        "--outdir",
        default=os.path.join("reports", "weekly_student"),
        help="Output directory (default: reports/weekly_student)",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=3,
        help="Max example questions per student-week (default: 3)",
    )
    return parser.parse_args()


def parse_timestamp(value: str) -> datetime:
    value = (value or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unrecognized timestamp format: {value!r}")


def week_start_monday(dt: datetime) -> datetime:
    # Monday as start of week (0=Mon)
    return datetime(dt.year, dt.month, dt.day) - timedelta(days=dt.weekday())


def norm_text(value: str) -> str:
    return (value or "").replace("\r", "\n").strip()


TOPIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "xác suất / tổ hợp",
        re.compile(r"\b(xác\s*suất|tổ\s*hợp|chỉnh\s*hợp|biến\s*cố|gieo|đồng\s*tiền)\b", re.I),
    ),
    ("hình học", re.compile(r"\b(tam\s*giác|đường\s*tròn|hình|góc|vector|tọa\s*độ)\b", re.I)),
    (
        "đại số",
        re.compile(r"\b(phương\s*trình|bất\s*phương\s*trình|hàm\s*số|đa\s*thức|ma\s*trận)\b", re.I),
    ),
    (
        "giải tích",
        re.compile(r"\b(đạo\s*hàm|tích\s*phân|giới\s*hạn|cực\s*trị|tiệm\s*cận)\b", re.I),
    ),
    ("số học", re.compile(r"\b(nguyên\s*tố|ước|bội|chẵn|lẻ|chia\s*hết)\b", re.I)),
]

ISSUE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("chưa hiểu / mơ hồ", re.compile(r"\b(chưa\s*hiểu|không\s*hiểu|mơ\s*hồ|rối)\b", re.I)),
    ("khó / cần gợi ý", re.compile(r"\b(khó|gợi\s*ý|hướng\s*dẫn|từng\s*bước|chi\s*tiết|giải\s*giúp)\b", re.I)),
    ("sai / nhầm", re.compile(r"\b(sai|nhầm|không\s*đúng)\b", re.I)),
    ("lỗi / trục trặc", re.compile(r"\b(lỗi|bug|trục\s*trặc)\b", re.I)),
]

RESOLVED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(em\s+hiểu\s+rồi|hiểu\s+rồi|cảm\s+ơn|ok(ay)?|đã\s+hiểu)\b", re.I),
    re.compile(r"\b(hoàn\s*thành|xong\s*rồi)\b", re.I),
    re.compile(r"^\s*\[S\]", re.I),
]


def detect_topics(text: str) -> list[str]:
    found: list[str] = []
    for name, pat in TOPIC_PATTERNS:
        if pat.search(text):
            found.append(name)
    return found


def detect_issues(text: str) -> list[str]:
    found: list[str] = []
    for name, pat in ISSUE_PATTERNS:
        if pat.search(text):
            found.append(name)
    return found


def is_resolved(question: str, response: str) -> bool:
    combined = f"{question}\n{response}"
    return any(p.search(combined) for p in RESOLVED_PATTERNS)


@dataclass
class StudentWeekAgg:
    interactions: int = 0
    qids: set[str] = field(default_factory=set)
    resolved_interactions: int = 0
    topic_counts: Counter = field(default_factory=Counter)
    issue_counts: Counter = field(default_factory=Counter)
    example_questions: list[str] = field(default_factory=list)


def read_rows(path: str):
    # Try utf-8 then utf-8-sig (BOM)
    last_err = None
    for enc in ("utf-8", "utf-8-sig"):
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                yield from csv.DictReader(f)
            return
        except UnicodeDecodeError as e:
            last_err = e
            continue
    raise last_err or RuntimeError("Failed to read CSV")


def main() -> int:
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    # Some rows can contain very long multi-line responses.
    csv.field_size_limit(min(10_000_000, sys.maxsize))

    by_student_week: dict[tuple[str, datetime], StudentWeekAgg] = defaultdict(StudentWeekAgg)
    all_students: set[str] = set()
    min_dt: datetime | None = None
    max_dt: datetime | None = None

    for row in read_rows(args.input):
        ts = parse_timestamp(row.get("Timestamp", ""))
        student_id = (row.get("Student ID") or "").strip()
        question = norm_text(row.get("Question", ""))
        response = norm_text(row.get("AI Response", ""))
        qid = str(row.get("QID") or "").strip()

        if not student_id:
            continue

        all_students.add(student_id)
        min_dt = ts if (min_dt is None or ts < min_dt) else min_dt
        max_dt = ts if (max_dt is None or ts > max_dt) else max_dt

        wk = week_start_monday(ts)
        agg = by_student_week[(student_id, wk)]
        agg.interactions += 1
        if qid:
            agg.qids.add(qid)

        combined_for_topics = f"{question}\n{response}"
        for t in detect_topics(combined_for_topics):
            agg.topic_counts[t] += 1
        for issue in detect_issues(question):
            agg.issue_counts[issue] += 1

        if is_resolved(question, response):
            agg.resolved_interactions += 1

        if len(agg.example_questions) < args.max_examples:
            q = question.replace("\n", " ").strip()
            if q:
                agg.example_questions.append(q[:240])

    # Write CSV summary (one row per student-week)
    csv_out = os.path.join(args.outdir, "weekly_by_student.csv")
    # Use UTF-8 with BOM for Windows-friendly viewing (Excel/Notepad).
    with open(csv_out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "student_id",
                "week_start",
                "week_end",
                "interactions",
                "unique_qids",
                "resolved_interactions_est",
                "top_topics",
                "top_issues",
                "example_questions",
            ]
        )
        for (student_id, wk), agg in sorted(by_student_week.items(), key=lambda x: (x[0][0], x[0][1])):
            week_end = wk + timedelta(days=6)
            top_topics = ", ".join([k for k, _ in agg.topic_counts.most_common(3)])
            top_issues = ", ".join([k for k, _ in agg.issue_counts.most_common(3)])
            examples = " | ".join(agg.example_questions)
            w.writerow(
                [
                    student_id,
                    wk.strftime("%Y-%m-%d"),
                    week_end.strftime("%Y-%m-%d"),
                    agg.interactions,
                    len(agg.qids),
                    agg.resolved_interactions,
                    top_topics,
                    top_issues,
                    examples,
                ]
            )

    # Write Markdown report grouped by student
    md_out = os.path.join(args.outdir, "weekly_by_student.md")
    with open(md_out, "w", encoding="utf-8-sig") as f:
        f.write("# Báo cáo theo tuần (mỗi học sinh)\n\n")
        f.write(f"- Nguồn: `{args.input}`\n")
        f.write(f"- Số học sinh: {len(all_students)}\n")
        if min_dt and max_dt:
            f.write(f"- Khoảng thời gian: {min_dt.strftime('%Y-%m-%d')} → {max_dt.strftime('%Y-%m-%d')}\n")
        f.write("\n")

        current_student = None
        for (student_id, wk), agg in sorted(by_student_week.items(), key=lambda x: (x[0][0], x[0][1])):
            if student_id != current_student:
                current_student = student_id
                f.write(f"## {student_id}\n\n")

            week_end = wk + timedelta(days=6)
            f.write(f"### Tuần {wk.strftime('%Y-%m-%d')} → {week_end.strftime('%Y-%m-%d')}\n\n")
            f.write(f"- Lượt tương tác: {agg.interactions}\n")
            f.write(f"- Bài/Chủ đề (QID) đã đụng tới: {len(agg.qids)}\n")
            f.write(f"- Tín hiệu đã hiểu/xong (ước lượng): {agg.resolved_interactions}\n")
            if agg.interactions:
                ratio = 100.0 * agg.resolved_interactions / agg.interactions
                f.write(f"- Tỉ lệ đã hiểu/xong (ước lượng): {ratio:.1f}%\n")

            if agg.topic_counts:
                topics = ", ".join([f"{k} ({v})" for k, v in agg.topic_counts.most_common(5)])
                f.write(f"- Chủ đề nổi bật: {topics}\n")
            if agg.issue_counts:
                issues = ", ".join([f"{k} ({v})" for k, v in agg.issue_counts.most_common(5)])
                f.write(f"- Vấn đề hay gặp: {issues}\n")

            if agg.example_questions:
                f.write("- Ví dụ câu hỏi:\n")
                for q in agg.example_questions:
                    f.write(f"  - {q}\n")
            f.write("\n")

    meta_out = os.path.join(args.outdir, "run_meta.txt")
    with open(meta_out, "w", encoding="utf-8-sig") as f:
        f.write(f"input={os.path.abspath(args.input)}\n")
        f.write(f"outdir={os.path.abspath(args.outdir)}\n")
        f.write(f"students={len(all_students)}\n")
        if min_dt and max_dt:
            f.write(f"min_timestamp={min_dt.isoformat(sep=' ')}\n")
            f.write(f"max_timestamp={max_dt.isoformat(sep=' ')}\n")

    print(md_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
