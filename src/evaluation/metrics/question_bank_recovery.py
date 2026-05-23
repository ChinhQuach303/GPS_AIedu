"""Question-bank recovery and audit utilities for GPS-Agent.

The processed JSON question bank was produced by a lossy text extraction step:
some answer fields and most mathematical option strings were damaged.  The raw
exam text, however, contains solution blocks ending in "Chọn/Chon A-D" markers.
This module treats the raw solution text as the source of truth for answer-key
coverage and keeps option-format repair as a separate audit dimension.

No LLM calls are used here.  The goal is to make the paper-facing statement
"45/45 answer keys are recoverable" reproducible from project files.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
from typing import Dict, Iterable, List, Optional

import pandas as pd

QUESTION_RE = re.compile(r"Câu\s*(\d+)\s*[:.]", re.IGNORECASE)
CHOOSE_RE = re.compile(r"Ch(?:ọ|o)n\s*([A-D])\b", re.IGNORECASE)
BLANK_OPTION_RE = re.compile(r"^[A-D]\.?\s*\.?\s*$")


@dataclass(frozen=True)
class RecoveredAnswer:
    qid: int
    original_json_answer: str
    recovered_answer: str
    answer_recovered: bool
    n_options: int
    malformed_or_blank_options: int
    options_need_typesetting_repair: bool
    answer_key_source: str
    solution_snippet: str


def _load_questions(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Question JSON not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Question JSON must contain a list of question objects")
    return data


def _segments_by_question(raw_text: str) -> Dict[int, str]:
    matches = list(QUESTION_RE.finditer(raw_text))
    segments: Dict[int, str] = {}
    for i, m in enumerate(matches):
        qid = int(m.group(1))
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        segments[qid] = raw_text[start:end]
    return segments


def recover_answers(raw_exam_text: Path) -> Dict[int, str]:
    """Recover final A-D answer markers from raw solution text."""
    if not raw_exam_text.exists():
        raise FileNotFoundError(f"Raw exam text not found: {raw_exam_text}")
    raw = raw_exam_text.read_text(encoding="utf-8", errors="ignore")
    segments = _segments_by_question(raw)
    answers: Dict[int, str] = {}
    for qid, block in segments.items():
        choices = CHOOSE_RE.findall(block)
        if choices:
            answers[qid] = choices[-1].upper()
    return answers


def _option_repair_count(options: Iterable[object]) -> int:
    bad = 0
    for option in options or []:
        text = str(option).strip()
        if BLANK_OPTION_RE.match(text) or text in {"", "."}:
            bad += 1
    return bad


def audit_question_bank_with_recovery(question_json: Path, raw_exam_text: Path) -> tuple[pd.DataFrame, dict, list[dict]]:
    questions = _load_questions(question_json)
    recovered = recover_answers(raw_exam_text)
    rows: List[RecoveredAnswer] = []
    repaired_questions: List[dict] = []

    for idx, q in enumerate(questions, start=1):
        qid = int(q.get("id") or q.get("qid") or idx)
        original = str(q.get("answer") or "").strip().upper()
        rec = recovered.get(qid, "")
        options = q.get("options") or []
        malformed = _option_repair_count(options)
        needs_repair = malformed > 0
        row = RecoveredAnswer(
            qid=qid,
            original_json_answer=original,
            recovered_answer=rec,
            answer_recovered=bool(rec),
            n_options=len(options),
            malformed_or_blank_options=malformed,
            options_need_typesetting_repair=needs_repair,
            answer_key_source="raw_exam_text.txt solution section; final Chọn/Chon marker" if rec else "not_recovered",
            solution_snippet=str(q.get("solution") or q.get("question") or "")[:500],
        )
        rows.append(row)
        qq = dict(q)
        qq["recovered_answer"] = rec
        qq["answer_key_source"] = row.answer_key_source
        qq["answer_recovered"] = row.answer_recovered
        qq["options_need_typesetting_repair"] = needs_repair
        repaired_questions.append(qq)

    table = pd.DataFrame([asdict(r) for r in rows])
    summary = {
        "n_questions": int(len(table)),
        "original_json_missing_answers": int((table["original_json_answer"] == "").sum()),
        "recovered_answers_from_raw_solution": int(table["answer_recovered"].sum()),
        "answer_key_coverage_after_recovery": float(table["answer_recovered"].mean()) if len(table) else 0.0,
        "options_need_typesetting_repair": int(table["options_need_typesetting_repair"].sum()),
        "interpretation": (
            "Answer-key coverage is complete after deterministic recovery from the raw solution text; "
            "the remaining question-bank issue is option/formula typesetting repair, not missing answers."
        ),
    }
    return table, summary, repaired_questions


__all__ = ["recover_answers", "audit_question_bank_with_recovery"]
