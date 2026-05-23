#!/usr/bin/env python3
"""Generate exploratory statistics for the expanded GPS-AIEdu corpus.

Important: this script does not call the expanded file a validated gold
standard. It audits metric ranges and writes a conservative report that can be
used in appendices or exploratory analysis sections.
"""
from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy import stats

from src.evaluation.metrics.pedagogy_metrics import cohen_d, expanded_corpus_quality

INPUT_CSV = Path("data/processed/expanded_exploratory_corpus.csv")
OUTPUT_DIR = Path("data/outputs/research_stats")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def hake_gain(pre_score: float, post_score: float, max_score: float = 100.0) -> float:
    if pd.isna(pre_score) or pd.isna(post_score) or max_score == pre_score:
        return np.nan
    return (post_score - pre_score) / (max_score - pre_score)


def run_analysis() -> dict:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing expanded corpus: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)
    quality = expanded_corpus_quality(INPUT_CSV)

    # Normalize numeric columns conservatively. Keep both raw and bounded II so
    # reviewers can see the cleaning decision.
    for col in ["Independence_Index", "Math_Density", "GPS_Fidelity", "Estimated_Post_Score", "Turns_G", "Turns_P", "Turns_S"]:
        if col in df.columns:
            df[col] = safe_numeric(df[col])
    if "Independence_Index" in df.columns:
        df["Independence_Index_Bounded"] = df["Independence_Index"].clip(lower=0, upper=1)

    report: dict = {
        "corpus_name": "Expanded GPS-AIEdu Corpus (exploratory, not human-validated gold standard)",
        "quality": quality,
    }

    if "Group" in df.columns:
        agg_map = {}
        if "Independence_Index" in df.columns:
            agg_map["avg_independence_raw"] = ("Independence_Index", "mean")
            agg_map["ii_gt_1"] = ("Independence_Index", lambda x: int((x > 1).sum()))
        if "Independence_Index_Bounded" in df.columns:
            agg_map["avg_independence_bounded"] = ("Independence_Index_Bounded", "mean")
        if "Math_Density" in df.columns:
            agg_map["avg_math_density"] = ("Math_Density", "mean")
        if "GPS_Fidelity" in df.columns:
            agg_map["avg_gps_fidelity"] = ("GPS_Fidelity", "mean")
        if "Estimated_Post_Score" in df.columns:
            agg_map["avg_estimated_post_score"] = ("Estimated_Post_Score", "mean")
        group_summary = df.groupby("Group").agg(n_sessions=("Group", "size"), **agg_map).round(4).reset_index()
        report["group_summary"] = group_summary.to_dict(orient="records")
        group_summary.to_csv(OUTPUT_DIR / "expanded_group_summary.csv", index=False)

    if {"Group", "Level"}.issubset(df.columns):
        level_summary = df.groupby(["Group", "Level"]).agg(
            n_sessions=("Group", "size"),
            avg_independence_bounded=("Independence_Index_Bounded", "mean") if "Independence_Index_Bounded" in df else ("Group", "size"),
            avg_math_density=("Math_Density", "mean") if "Math_Density" in df else ("Group", "size"),
            avg_estimated_post_score=("Estimated_Post_Score", "mean") if "Estimated_Post_Score" in df else ("Group", "size"),
        ).round(4).reset_index()
        report["level_summary"] = level_summary.to_dict(orient="records")
        level_summary.to_csv(OUTPUT_DIR / "expanded_level_summary.csv", index=False)

    # Statistical tests are exploratory only because Estimated_Post_Score is a
    # heuristic in the expanded corpus.
    tests = []
    if "Group" in df.columns and "Estimated_Post_Score" in df.columns:
        gps_scores = df[df["Group"].eq("GPS")]["Estimated_Post_Score"].dropna()
        nongps_scores = df[~df["Group"].eq("GPS")]["Estimated_Post_Score"].dropna()
        if len(gps_scores) > 1 and len(nongps_scores) > 1:
            t, p = stats.ttest_ind(gps_scores, nongps_scores, equal_var=False)
            tests.append(
                {
                    "comparison": "GPS vs Non-GPS",
                    "metric": "Estimated_Post_Score (heuristic)",
                    "gps_mean": float(gps_scores.mean()),
                    "nongps_mean": float(nongps_scores.mean()),
                    "p_value": float(p),
                    "cohen_d": cohen_d(gps_scores, nongps_scores),
                    "interpretation": "exploratory_only_not_learning_outcome",
                }
            )
    report["exploratory_tests"] = tests

    with open(OUTPUT_DIR / "research_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Paper-safe markdown summary.
    lines = [
        "# Expanded Corpus Exploratory Statistics",
        "",
        "This file is generated from `data/processed/expanded_exploratory_corpus.csv`, but the corpus should be described as an expanded/augmented behavioral corpus, not as a human-validated gold standard.",
        "",
        "## Quality audit",
        f"- Rows: {quality.get('rows')}",
        f"- Independence_Index > 1: {quality.get('independence_index_gt_1')}",
        f"- Groups: {quality.get('groups')}",
        "",
    ]
    if "group_summary" in report:
        lines.append("## Group summary")
        lines.append(pd.DataFrame(report["group_summary"]).to_markdown(index=False))
        lines.append("")
    if tests:
        lines.append("## Exploratory tests")
        lines.append(pd.DataFrame(tests).to_markdown(index=False))
        lines.append("")
    (OUTPUT_DIR / "expanded_corpus_exploratory_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"Exploratory results saved at: {OUTPUT_DIR}")
    return report


if __name__ == "__main__":
    run_analysis()
