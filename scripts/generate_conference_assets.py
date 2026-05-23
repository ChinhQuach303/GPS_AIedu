#!/usr/bin/env python3
"""Generate paper-ready tables/figures from current GPS-Agent logs.

This is a convenience wrapper around `scripts/generate_evaluation_report.py` and
`scripts/generate_research_stats.py`. It does not run simulations or LLM judges;
it only regenerates reproducible assets from existing data files.
"""
from __future__ import annotations

from scripts.generate_evaluation_report import generate_report
from scripts.generate_research_stats import run_analysis
from scripts.audit_question_bank import main as audit_question_bank


def main():
    generate_report()
    run_analysis()
    audit_question_bank()
    print("Conference assets regenerated under reports/evaluation and data/outputs/research_stats.")


if __name__ == "__main__":
    main()
