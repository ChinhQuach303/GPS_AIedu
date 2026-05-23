#!/usr/bin/env python3
"""Lightweight final audit for the EMNLP paper source.

The checks are intentionally conservative and local: they do not claim external
plagiarism detection, but they catch repeated wording, stale claims, broken refs,
and common template mistakes before Overleaf submission.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_TEX = [
    ROOT / "paper/final/main.tex",
    ROOT / "paper/final_revision/main.tex",
    ROOT / "main.tex",
]
TEX = next((candidate for candidate in CANDIDATE_TEX if candidate.exists()), CANDIDATE_TEX[0])

BANNED = [
    "Anonymous ACL submission",
    "15/45 questions lack answers",
    "kappa=0.68",
    "substantial agreement",
    "long-term learning gain",
]


def strip_tex_commands(text: str) -> str:
    text = re.sub(r"%.*", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", text)
    text = re.sub(r"[^A-Za-z0-9\- ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def repeated_ngrams(text: str, n: int = 7, min_count: int = 3):
    words = strip_tex_commands(text).split()
    grams = Counter(tuple(words[i:i+n]) for i in range(max(0, len(words)-n+1)))
    return [(" ".join(k), v) for k, v in grams.items() if v >= min_count]


def main() -> int:
    if not TEX.exists():
        print(f"Missing TeX source: {TEX}", file=sys.stderr)
        return 2
    text = TEX.read_text(encoding="utf-8")
    errors = []
    for phrase in BANNED:
        if phrase.lower() in text.lower():
            errors.append(f"Banned/stale phrase found: {phrase}")
    if "Anonymous Submission" not in text:
        errors.append("Title page does not identify anonymous submission")
    if "Table~\\ref" not in text:
        errors.append("No table references found; check cross-reference formatting")
    reps = repeated_ngrams(text)
    if len(reps) > 8:
        errors.append(f"Many repeated long phrases detected: {reps[:5]}")
    if errors:
        print("FINAL PAPER AUDIT FAILED")
        for e in errors:
            print(f"- {e}")
        return 1
    print("FINAL PAPER AUDIT PASSED")
    print(f"Repeated long-phrase count: {len(reps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
