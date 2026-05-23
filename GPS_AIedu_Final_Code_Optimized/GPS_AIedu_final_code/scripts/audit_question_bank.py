#!/usr/bin/env python3
"""Audit and repair the 45-question probability/combinatorics bank.

This script intentionally audits two dimensions separately:
1. answer-key coverage, recovered from the raw solution text;
2. option/formula typography, still requiring manual repair for release.
"""
from __future__ import annotations
from pathlib import Path
import json

from src.evaluation.metrics.question_bank_recovery import audit_question_bank_with_recovery

ROOT = Path(__file__).resolve().parents[1]
QUESTION_JSON = ROOT / "data/processed/probabilities_questions.json"
RAW_EXAM_TEXT = ROOT / "data/raw/exam_text.txt"
OUT_DIR = ROOT / "data/outputs/research_stats"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    table, summary, repaired_questions = audit_question_bank_with_recovery(QUESTION_JSON, RAW_EXAM_TEXT)
    table.to_csv(OUT_DIR / "recovered_question_answer_key.csv", index=False)
    (OUT_DIR / "question_bank_recovery_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "probabilities_questions_answer_repaired.json").write_text(
        json.dumps(repaired_questions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
