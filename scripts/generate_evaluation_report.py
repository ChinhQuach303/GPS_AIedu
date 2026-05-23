#!/usr/bin/env python3
"""Generate reproducible evaluation report for the GPS-Agent paper.

This script replaces the earlier hard-coded report. It computes every reported
number from CSV logs and keeps claims conservative:
- primary: direct-answer leakage and GPS phase validity;
- secondary: VAI and Math Density;
- limitation: stall/scaffolding pressure and language leakage;
- IRR: computed from the observed rater score file, never hard-coded.
"""
from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd

from src.evaluation.metrics.pedagogy_metrics import (
    binary_fisher_test,
    compute_irr_from_file,
    expanded_corpus_quality,
    human_pilot_summary,
    question_bank_audit,
    summarize_dataframe,
    welch_test,
)

DATA_DIR = Path("data/outputs")
PROCESSED_DIR = Path("data/processed")
REPORT_DIR = Path("reports/evaluation")
REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR = REPORT_DIR / "figures"
TAB_DIR = REPORT_DIR / "tables"
FIG_DIR.mkdir(exist_ok=True)
TAB_DIR.mkdir(exist_ok=True)


def load_csv(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")
    return pd.read_csv(path)


def pct(x: float | None) -> str:
    return "NA" if x is None or pd.isna(x) else f"{100 * x:.1f}%"


def num(x: float | None, nd: int = 3) -> str:
    return "NA" if x is None or pd.isna(x) else f"{x:.{nd}f}"


def make_bar(path: Path, labels: list[str], values: list[float], title: str, ylabel: str, ymax: float | None = None):
    plt.figure(figsize=(7, 4.5))
    plt.bar(labels, values)
    plt.ylabel(ylabel)
    plt.title(title)
    if ymax is not None:
        plt.ylim(0, ymax)
    for i, v in enumerate(values):
        label = f"{100*v:.1f}%" if max(values, default=0) <= 1 else f"{v:.3f}"
        plt.text(i, v + (0.02 if max(values, default=0) <= 1 else 0.01), label, ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()


def generate_report() -> dict:
    print("Generating reproducible GPS-Agent evaluation report...")

    frames = {
        "GPS-Agent": load_csv(DATA_DIR / "cleaned_massive_results.csv", "GPS controlled results"),
        "Single-Agent": load_csv(DATA_DIR / "cleaned_baseline_results.csv", "single-agent baseline results"),
        "Cross-Model Phi-3": load_csv(DATA_DIR / "cross_model_conversations.csv", "cross-model results"),
    }

    summaries = []
    enriched = {}
    for system_name, df in frames.items():
        summary, enriched_df = summarize_dataframe(df, system_name)
        summaries.append(summary)
        enriched[system_name] = enriched_df
        enriched_df.to_csv(TAB_DIR / f"enriched_{system_name.lower().replace(' ', '_').replace('-', '_')}.csv", index=False)

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(TAB_DIR / "table_main_system_comparison.csv", index=False)

    gps = enriched["GPS-Agent"]
    baseline = enriched["Single-Agent"]
    cross = enriched["Cross-Model Phi-3"]

    tests = [
        welch_test(gps["vai"], baseline["vai"], "GPS-Agent vs Single-Agent", "VAI"),
        welch_test(gps["math_density"], baseline["math_density"], "GPS-Agent vs Single-Agent", "Math Density"),
        binary_fisher_test(gps["direct_answer_leakage"], baseline["direct_answer_leakage"], "GPS-Agent vs Single-Agent", "Direct-answer leakage"),
        binary_fisher_test(gps["phase_validity"], baseline["phase_validity"], "GPS-Agent vs Single-Agent", "Phase validity"),
        binary_fisher_test(gps["stall"], baseline["stall"], "GPS-Agent vs Single-Agent", "Stall rate"),
        binary_fisher_test(cross["direct_answer_leakage"], baseline["direct_answer_leakage"], "Cross-Model Phi-3 vs Single-Agent", "Direct-answer leakage"),
    ]
    tests_df = pd.DataFrame(tests)
    tests_df.to_csv(TAB_DIR / "table_statistical_tests.csv", index=False)

    # By-level table
    level_rows = []
    for system_name, df in enriched.items():
        if "level" not in df.columns:
            continue
        for level, group in df.groupby("level"):
            level_rows.append(
                {
                    "system": system_name,
                    "level": level,
                    "n_sessions": len(group),
                    "vai_mean": group["vai"].mean(),
                    "math_density_mean": group["math_density"].mean(),
                    "direct_answer_leakage_rate": group["direct_answer_leakage"].mean(),
                    "stall_rate": group["stall"].mean(),
                    "phase_validity_rate": group["phase_validity"].mean(),
                }
            )
    level_df = pd.DataFrame(level_rows)
    level_df.to_csv(TAB_DIR / "table_by_student_level.csv", index=False)

    irr = compute_irr_from_file(DATA_DIR / "irr_scores.csv")
    qb = question_bank_audit(PROCESSED_DIR / "probabilities_questions.json")
    human_pilot = human_pilot_summary(PROCESSED_DIR / "GPS_AIedu.csv")
    expanded = expanded_corpus_quality(PROCESSED_DIR / "gps_aiedu_gold_standard.csv")

    audit_payload = {
        "summary": summaries,
        "tests": tests,
        "irr": irr,
        "question_bank_audit": {k: v for k, v in qb.items() if k != "audit_table"},
        "human_pilot_summary": human_pilot,
        "expanded_corpus_quality": expanded,
    }
    with open(REPORT_DIR / "reproducible_report.json", "w", encoding="utf-8") as f:
        json.dump(audit_payload, f, ensure_ascii=False, indent=2)

    # Figures
    systems = summary_df["system"].tolist()
    make_bar(
        FIG_DIR / "fig_direct_answer_leakage.png",
        systems,
        summary_df["direct_answer_leakage_rate"].tolist(),
        "Direct-answer leakage by system",
        "Leakage rate",
        ymax=0.65,
    )
    make_bar(
        FIG_DIR / "fig_phase_validity.png",
        systems,
        summary_df["phase_validity_rate"].tolist(),
        "GPS phase validity by system",
        "Phase-valid session rate",
        ymax=1.05,
    )
    make_bar(
        FIG_DIR / "fig_vai.png",
        systems,
        summary_df["vai_mean"].tolist(),
        "VAI by system (secondary metric)",
        "Mean VAI",
        ymax=0.5,
    )
    make_bar(
        FIG_DIR / "fig_stall_rate.png",
        systems,
        summary_df["stall_rate"].tolist(),
        "Stall / scaffolding pressure by system",
        "Stall rate",
        ymax=1.05,
    )

    # Text report for paper drafting
    gps_summary = summary_df[summary_df.system == "GPS-Agent"].iloc[0]
    base_summary = summary_df[summary_df.system == "Single-Agent"].iloc[0]
    cross_summary = summary_df[summary_df.system == "Cross-Model Phi-3"].iloc[0]
    leakage_test = tests_df[tests_df.metric.eq("Direct-answer leakage") & tests_df.comparison.eq("GPS-Agent vs Single-Agent")].iloc[0]
    phase_test = tests_df[tests_df.metric.eq("Phase validity")].iloc[0]
    vai_test = tests_df[tests_df.metric.eq("VAI")].iloc[0]

    lines = []
    lines.append("GPS-AGENT REPRODUCIBLE EVALUATION REPORT")
    lines.append("=" * 48)
    lines.append("")
    lines.append("DATA LAYERS")
    lines.append(f"- Human pilot log: {human_pilot.get('students')} students, {human_pilot.get('questions')} questions, {human_pilot.get('sessions')} sessions, {human_pilot.get('human_pilot_turns')} G/P/S turns.")
    lines.append(f"- Expanded turn log: {human_pilot.get('total_rows')} total turns ({human_pilot.get('human_pilot_turns')} human pilot + {human_pilot.get('expanded_turns')} expanded).")
    lines.append(f"- Controlled evaluation: {int(gps_summary.n_sessions)} GPS-Agent sessions vs {int(base_summary.n_sessions)} Single-Agent sessions over {int(gps_summary.n_questions)} unique questions.")
    lines.append(f"- Cross-model validation: {int(cross_summary.n_sessions)} Phi-3 sessions.")
    lines.append("")
    lines.append("MAIN RESULTS")
    lines.append(f"- Direct-answer leakage: GPS-Agent {pct(gps_summary.direct_answer_leakage_rate)} vs Single-Agent {pct(base_summary.direct_answer_leakage_rate)}; Fisher p={num(leakage_test.p_value, 3)}, odds ratio={num(leakage_test.fisher_odds_ratio, 3)}.")
    lines.append(f"- Phase validity: GPS-Agent {pct(gps_summary.phase_validity_rate)} vs Single-Agent {pct(base_summary.phase_validity_rate)}; Fisher p={num(phase_test.p_value, 3)}.")
    lines.append(f"- VAI is secondary and not significant in the current controlled logs: GPS-Agent {num(gps_summary.vai_mean)} vs Single-Agent {num(base_summary.vai_mean)}; Welch p={num(vai_test.p_value, 3)}, Cohen's d={num(vai_test.cohen_d, 3)}.")
    lines.append(f"- Stall/scaffolding-pressure signal: GPS-Agent {pct(gps_summary.stall_rate)} vs Single-Agent {pct(base_summary.stall_rate)}; report as limitation, not as success.")
    lines.append(f"- Cross-model Phi-3 stress test: leakage {pct(cross_summary.direct_answer_leakage_rate)}, stall {pct(cross_summary.stall_rate)}, non-Vietnamese leakage {pct(cross_summary.non_vietnamese_leakage_rate)}.")
    lines.append("")
    lines.append("IRR")
    if irr.get("available"):
        lines.append(f"- Observed IRR from irr_scores.csv: quadratic weighted kappa={num(irr.get('quadratic_weighted_kappa'), 3)}, unweighted kappa={num(irr.get('unweighted_kappa'), 3)}, n={irr.get('n')}. Do not claim substantial agreement unless this improves after reannotation.")
    else:
        lines.append(f"- IRR unavailable: {irr.get('reason')}")
    lines.append("")
    lines.append("DATA QUALITY NOTES")
    lines.append(f"- Question bank: {qb.get('n_questions')} questions; missing answers={qb.get('missing_answer')}; questions with blank options={qb.get('questions_with_blank_options')}; validated for correctness={qb.get('validated_for_correctness')}.")
    lines.append(f"- Expanded corpus: {expanded.get('rows')} rows; Independence_Index > 1 count={expanded.get('independence_index_gt_1')}. Treat as exploratory/augmented corpus until audited.")
    (REPORT_DIR / "final_stats.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"Done. Report written to {REPORT_DIR}")
    return audit_payload


if __name__ == "__main__":
    generate_report()
