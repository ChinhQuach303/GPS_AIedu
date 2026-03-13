import argparse
import csv
import re
from pathlib import Path

from generate_mock_week1 import classify_gps_step, salted_sha256_hex


HEX64 = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local smoke test for Week 1 mock data (schema CSV).")
    parser.add_argument("--csv", type=Path, default=Path("data/raw/mock_week1_realistic.csv"))
    parser.add_argument("--salt", type=str, default="GPS_AI_MATH_2026")
    parser.add_argument("--min_accuracy", type=float, default=0.9)
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"Missing file: {args.csv}")
        return 2

    total = 0
    correct = 0
    unknown = 0
    bad_hash = 0
    out_of_range = 0
    step_counts: dict[str, int] = {"G": 0, "P": 0, "S": 0, "Unknown": 0}
    profile_counts: dict[str, int] = {}

    with args.csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1

            student_id = (row.get("student_id") or "").strip()
            student_hash = (row.get("student_id_hash") or "").strip()
            expected_hash = salted_sha256_hex(args.salt, student_id) if student_id else ""
            if (not HEX64.match(student_hash)) or (student_hash != expected_hash):
                bad_hash += 1

            gps_step = (row.get("gps_step") or "Unknown").strip() or "Unknown"
            step_counts[gps_step] = step_counts.get(gps_step, 0) + 1

            question_text = row.get("question_text") or ""
            pred = classify_gps_step(question_text)
            if pred == "Unknown":
                unknown += 1
            if pred == gps_step:
                correct += 1

            try:
                satisfaction = int(float(row.get("satisfaction") or "0"))
                difficulty = int(float(row.get("difficulty") or "0"))
                if not (1 <= satisfaction <= 5 and 1 <= difficulty <= 5):
                    out_of_range += 1
            except ValueError:
                out_of_range += 1

            notes = row.get("notes") or ""
            m = re.search(r"profile=([^;]+)", notes)
            if m:
                profile = m.group(1)
                profile_counts[profile] = profile_counts.get(profile, 0) + 1

    accuracy = (correct / total) if total else 0.0

    print(f"Rows: {total}")
    print(f"Accuracy (label vs truth): {accuracy:.4f}")
    print(f"Unknown predictions: {unknown}")
    print(f"Bad hashes: {bad_hash}")
    print(f"Out-of-range satisfaction/difficulty: {out_of_range}")
    print(f"Step counts: {step_counts}")
    if profile_counts:
        print(f"Profile counts: {dict(sorted(profile_counts.items()))}")

    ok = True
    if total == 0:
        ok = False
        print("FAIL: no rows")
    if accuracy < args.min_accuracy:
        ok = False
        print(f"FAIL: accuracy < {args.min_accuracy}")
    if bad_hash > 0:
        ok = False
        print("FAIL: bad hashes found")
    if out_of_range > 0:
        ok = False
        print("FAIL: out-of-range satisfaction/difficulty found")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
