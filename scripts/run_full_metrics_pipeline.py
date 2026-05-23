#!/usr/bin/env python3
"""Run the complete GPS-Agent metric suite and build paper-ready assets."""
from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import zipfile

import matplotlib.pyplot as plt
import pandas as pd

from src.evaluation.metrics.comprehensive_metrics import (
    BINARY_METRICS,
    CONTINUOUS_METRICS,
    PRIMARY_BINARY,
    PRIMARY_CONTINUOUS,
    audit_all,
    by_level_summary,
    by_question_summary,
    compare_systems,
    compute_session_metrics,
    correlation_diagnostics,
    summarize_metrics,
)

ROOT = Path.cwd()
OUT = ROOT / "reports" / "full_metrics"
TABLES = OUT / "tables"
FIGS = OUT / "figures"
PAPER = ROOT / "paper" / "full_metrics"

DATASETS = {
    "GPS-Agent": ROOT / "data" / "outputs" / "cleaned_massive_results.csv",
    "Single-Agent": ROOT / "data" / "outputs" / "cleaned_baseline_results.csv",
    "Cross-Model Phi-3": ROOT / "data" / "outputs" / "cross_model_conversations.csv",
}


def pct(x: float) -> str:
    return f"{100 * float(x):.1f}"


def num(x: float, n: int = 3) -> str:
    return "--" if pd.isna(x) else f"{float(x):.{n}f}"


def pval(x: float) -> str:
    if pd.isna(x):
        return "--"
    if x < 0.001:
        return f"{x:.2e}"
    return f"{x:.3f}"


def latex_escape(s: object) -> str:
    text = str(s)
    repl = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}
    return "".join(repl.get(ch, ch) for ch in text)


def load_sessions() -> pd.DataFrame:
    frames = []
    for system, path in DATASETS.items():
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_csv(path)
        frames.append(compute_session_metrics(df, system))
    return pd.concat(frames, ignore_index=True)


def write_tables(sessions: pd.DataFrame) -> dict:
    TABLES.mkdir(parents=True, exist_ok=True)
    sessions.to_csv(TABLES / "session_level_full_metrics.csv", index=False)
    summary = summarize_metrics(sessions)
    summary.to_csv(TABLES / "table_full_system_summary.csv", index=False)
    by_level = by_level_summary(sessions)
    by_level.to_csv(TABLES / "table_metrics_by_student_level.csv", index=False)
    by_question = by_question_summary(sessions)
    by_question.to_csv(TABLES / "table_metrics_by_question.csv", index=False)
    tests = compare_systems(sessions)
    tests.to_csv(TABLES / "table_all_statistical_tests.csv", index=False)
    diag = correlation_diagnostics(sessions)
    diag.to_csv(TABLES / "table_correlation_diagnostics.csv", index=False)

    # Paper-facing slices.
    core_cols = [
        "system", "n_sessions", "n_questions", "n_levels",
        "direct_answer_leakage_rate", "direct_answer_leakage_ci_low", "direct_answer_leakage_ci_high",
        "phase_validity_rate", "phase_validity_ci_low", "phase_validity_ci_high",
        "gps_completion_rate", "premature_solve_rate", "stall_rate",
    ]
    summary[[c for c in core_cols if c in summary.columns]].to_csv(TABLES / "paper_table_control_metrics.csv", index=False)
    engagement_cols = [
        "system", "vai_mean", "vai_sd", "math_density_mean", "student_reasoning_rate_mean",
        "token_balance_student_share_mean", "tutor_student_token_ratio_mean", "answer_dependency_index_mean",
        "autonomy_process_score_mean",
    ]
    summary[[c for c in engagement_cols if c in summary.columns]].to_csv(TABLES / "paper_table_engagement_metrics.csv", index=False)
    quality_cols = [
        "system", "non_vietnamese_leakage_rate", "reflection_completion_rate", "degeneracy_flag_rate",
        "parsed_turn_ratio_mean", "max_same_phase_run_mean", "phase_balance_entropy_mean",
    ]
    summary[[c for c in quality_cols if c in summary.columns]].to_csv(TABLES / "paper_table_quality_dynamics_metrics.csv", index=False)
    return {"summary": summary, "by_level": by_level, "by_question": by_question, "tests": tests, "diag": diag}


def plot_metric(summary: pd.DataFrame, metric: str, title: str, filename: str, ylabel: str = "Rate") -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    x = summary["system"].astype(str).tolist()
    y = summary[metric].astype(float).tolist()
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    ax.bar(x, y)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=20)
    if "rate" in metric or metric in ["phase_validity", "stall"]:
        ax.set_ylim(0, max(1.0, max(y) * 1.15 if y else 1.0))
    fig.tight_layout()
    fig.savefig(FIGS / filename, dpi=200)
    plt.close(fig)


def write_figures(summary: pd.DataFrame) -> None:
    plot_metric(summary, "direct_answer_leakage_rate", "Direct-answer leakage", "fig01_direct_answer_leakage.png")
    plot_metric(summary, "phase_validity_rate", "Phase validity", "fig02_phase_validity.png")
    plot_metric(summary, "gps_completion_rate", "Guide-Practice-Solve completion", "fig03_gps_completion.png")
    plot_metric(summary, "stall_rate", "Stall / scaffolding pressure", "fig04_stall_rate.png")
    plot_metric(summary, "vai_mean", "Verifiable Autonomy Index", "fig05_vai.png", ylabel="Mean VAI")
    plot_metric(summary, "student_reasoning_rate_mean", "Student reasoning-turn rate", "fig06_student_reasoning_rate.png", ylabel="Mean rate")


def write_acl_fallback(out: Path) -> None:
    (out / "acl.sty").write_text(r"""
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{acl}[2026/05/22 ACL-compatible fallback for local preview]
\newif\ifaclreview
\DeclareOption{review}{\aclreviewtrue}
\DeclareOption{final}{\aclreviewfalse}
\ProcessOptions\relax
\RequirePackage[letterpaper,margin=1in]{geometry}
\RequirePackage{times}
\RequirePackage{latexsym}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\setlength{\columnsep}{0.25in}
\AtBeginDocument{\if@twocolumn\else\twocolumn\fi}
\pagestyle{plain}
\titleformat{\section}{\large\bfseries}{\thesection}{0.5em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{0.5em}{}
\newcommand{\aclfinalcopy}{}
\newcommand{\aclpaperid}[1]{}
\renewenvironment{abstract}{\begin{center}\bfseries Abstract\end{center}\small}{\par}
""".strip() + "\n", encoding="utf-8")
    try:
        plainnat = subprocess.run(["kpsewhich", "plainnat.bst"], text=True, capture_output=True)
        if plainnat.returncode == 0 and plainnat.stdout.strip():
            shutil.copyfile(plainnat.stdout.strip(), out / "acl_natbib.bst")
        else:
            (out / "acl_natbib.bst").write_text("", encoding="utf-8")
    except FileNotFoundError:
        (out / "acl_natbib.bst").write_text("", encoding="utf-8")


def main_table_tex(summary: pd.DataFrame) -> str:
    rows = []
    for _, r in summary.iterrows():
        rows.append(
            f"{latex_escape(r['system'])} & {int(r['n_sessions'])} & {int(r['n_questions'])} & "
            f"{pct(r['direct_answer_leakage_rate'])} & {pct(r['phase_validity_rate'])} & "
            f"{pct(r['gps_completion_rate'])} & {pct(r['premature_solve_rate'])} & {pct(r['stall_rate'])} \\\\"
        )
    return "\n".join(rows)


def engagement_table_tex(summary: pd.DataFrame) -> str:
    rows = []
    for _, r in summary.iterrows():
        rows.append(
            f"{latex_escape(r['system'])} & {num(r['vai_mean'])} & {num(r['math_density_mean'])} & "
            f"{num(r['student_reasoning_rate_mean'])} & {num(r['token_balance_student_share_mean'])} & "
            f"{num(r['tutor_student_token_ratio_mean'])} & {num(r['answer_dependency_index_mean'])} & {num(r['autonomy_process_score_mean'])} \\\\"
        )
    return "\n".join(rows)


def level_table_tex(level: pd.DataFrame) -> str:
    gps = level[level.system.eq("GPS-Agent")].copy()
    order = ["Giỏi", "Khá", "Trung bình", "Yếu"]
    label_map = {"Giỏi": "Excellent", "Khá": "Good", "Trung bình": "Average", "Yếu": "Weak"}
    gps["_o"] = gps["level"].map({v: i for i, v in enumerate(order)}).fillna(99)
    rows = []
    for _, r in gps.sort_values("_o").iterrows():
        rows.append(
            f"{label_map.get(r['level'], latex_escape(r['level']))} & {int(r['n_sessions'])} & "
            f"{pct(r['direct_answer_leakage_rate'])} & {pct(r['phase_validity_rate'])} & {pct(r['gps_completion_rate'])} & "
            f"{pct(r['stall_rate'])} & {num(r['vai_mean'])} & {num(r['student_reasoning_rate_mean'])} \\\\"
        )
    return "\n".join(rows)


def stat_line(tests: pd.DataFrame, metric: str) -> pd.Series:
    row = tests[tests.metric.eq(metric)]
    if row.empty:
        raise KeyError(metric)
    return row.iloc[0]


def write_latex_project(tables: dict, audits: dict) -> None:
    summary, level, tests = tables["summary"], tables["by_level"], tables["tests"]
    PAPER.mkdir(parents=True, exist_ok=True)
    (PAPER / "figures").mkdir(exist_ok=True)
    (PAPER / "tables").mkdir(exist_ok=True)
    for fig in FIGS.glob("*.png"):
        shutil.copyfile(fig, PAPER / "figures" / fig.name)
    for csv in TABLES.glob("*.csv"):
        shutil.copyfile(csv, PAPER / "tables" / csv.name)
    write_acl_fallback(PAPER)
    (PAPER / "latexmkrc").write_text("$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';\n$pdf_mode = 1;\n", encoding="utf-8")
    (PAPER / "README_OVERLEAF.md").write_text("Upload this folder or ZIP to Overleaf/Prism and compile main.tex. Replace acl.sty with official ACL style for final submission.\n", encoding="utf-8")

    gps = summary[summary.system.eq("GPS-Agent")].iloc[0]
    base = summary[summary.system.eq("Single-Agent")].iloc[0]
    cross = summary[summary.system.eq("Cross-Model Phi-3")].iloc[0]
    leak = stat_line(tests, "direct_answer_leakage")
    phase = stat_line(tests, "phase_validity")
    complete = stat_line(tests, "gps_completion")
    vai = stat_line(tests, "vai")
    reasoning = stat_line(tests, "student_reasoning_rate")
    aps = stat_line(tests, "autonomy_process_score")
    stall = stat_line(tests, "stall")
    human_pilot = audits["human_pilot"]
    qb = audits["question_bank"]
    irr = audits["irr"]
    expanded = audits["expanded"]

    tex = rf"""
\documentclass[11pt]{{article}}
\usepackage[review]{{acl}}
\usepackage{{times}}
\usepackage{{latexsym}}
\usepackage{{amsmath}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{microtype}}
\usepackage{{url}}
\usepackage{{natbib}}
\usepackage[hidelinks]{{hyperref}}

\title{{GPS-Agent: Full-Metric Evaluation of a State-Graph Tutor for Reducing Direct Answer-Giving in Mathematics Dialogue}}
\author{{Anonymous Submission}}

\begin{{document}}
\maketitle
\begin{{abstract}}
Large language models are strong mathematical solvers, but this creates a pedagogical failure mode: direct answer-giving before the learner has reasoned through a problem. We present GPS-Agent, a Socratic tutoring framework that enforces a Guide--Practice--Solve protocol. This revision reports a full deterministic metric suite over Vietnamese probability/combinatorics tutoring logs: {human_pilot['students']} student profiles, {human_pilot['questions']} questions, {human_pilot['sessions']} human pilot sessions, {human_pilot['human_pilot_turns']} annotated turns, {int(gps['n_sessions'])} controlled GPS-Agent sessions, {int(base['n_sessions'])} single-agent baseline sessions, and {int(cross['n_sessions'])} cross-model stress-test sessions. GPS-Agent reduces direct-answer leakage from {pct(base['direct_answer_leakage_rate'])}\% to {pct(gps['direct_answer_leakage_rate'])}\% (Fisher $p={pval(leak['p_value'])}$) and increases phase-validity from {pct(base['phase_validity_rate'])}\% to {pct(gps['phase_validity_rate'])}\% ($p={pval(phase['p_value'])}$). We also report engagement, language, phase-dynamics, failure, data-quality, and IRR diagnostics. The evidence supports a process-control claim, not yet a long-term learning-gain claim.
\end{{abstract}}

\section{{Introduction}}
LLM tutors frequently optimize for helpfulness by solving the learner's problem directly. For mathematics education, this is problematic because the visible output can be correct while the learning process is weak. GPS-Agent addresses this issue by separating pedagogical functions into state-constrained Guide, Practice, and Solve phases.

Earlier drafts of this project reported only a narrow set of metrics. This version expands the evaluation suite to cover five groups: pedagogical control, phase dynamics, learner engagement, language/data quality, and statistical diagnostics. Every metric is regenerated from CSV logs by deterministic code; no paper number is hard-coded.

\section{{System}}
GPS-Agent uses a LangGraph-style state graph with specialized nodes. Guide elicits prior knowledge and problem interpretation. Practice decomposes the task into smaller computations. Solve confirms the final answer only after prior Guide and Practice evidence. The Supervisor routes turns and stores a phase trace. This trace makes phase validity auditable rather than purely prompt-dependent.

\section{{Data Layers}}
\paragraph{{Human pilot.}} The project contains a human pilot turn log with {human_pilot['students']} student profiles, {human_pilot['questions']} questions, {human_pilot['sessions']} sessions, and {human_pilot['human_pilot_turns']} annotated turns. Phase counts are Guide={human_pilot['phase_counts'].get('G', 0)}, Practice={human_pilot['phase_counts'].get('P', 0)}, Solve={human_pilot['phase_counts'].get('S', 0)}. This layer calibrates the protocol and supports data-quality analysis.

\paragraph{{Controlled comparison.}} The main comparison uses {int(gps['n_sessions'])} GPS-Agent sessions and {int(base['n_sessions'])} baseline sessions. Both share the same schema and are therefore used for statistical tests.

\paragraph{{Cross-model stress test.}} The cross-model layer contains {int(cross['n_sessions'])} Phi-3-style student-simulator sessions. It is used as a stress test, not as a success-only result, because stall and language leakage are higher than in the primary GPS-Agent condition.

\paragraph{{Expanded corpus.}} The expanded exploratory corpus has {expanded.get('rows', 'NA')} rows. It is not called a human gold standard because the audit still finds schema and metric-quality issues.

\paragraph{{Question-bank audit.}} The 45-question bank contains {qb['n_questions']} questions, with {qb['missing_answer']} missing answers and {qb['questions_with_blank_options']} malformed-option cases. Correctness-based claims are therefore restricted to validated subsets.

\section{{Metric Suite}}
\paragraph{{Pedagogical-control metrics.}} We compute direct-answer leakage, phase validity, GPS completion, premature Solve, skipped Guide, skipped Practice, and stall/scaffolding pressure.

\paragraph{{Phase-dynamics metrics.}} We compute Guide/Practice/Solve counts, maximum same-phase run, phase-balance entropy, guide-loop rate, and practice-pressure rate.

\paragraph{{Engagement metrics.}} We compute VAI, math density, student reasoning-turn rate, student/tutor token balance, tutor-student token ratio, answer-dependency index, and a secondary autonomy-process score. The autonomy-process score is not treated as a learning-outcome metric; it is a diagnostic aggregate of process behavior.

\paragraph{{Quality metrics.}} We compute non-Vietnamese leakage, parse coverage, degeneracy flags, reflection requirement/completion, and IRR diagnostics.

\section{{Results}}
\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrrrr}}
\toprule
System & $N$ & Q & Leak. & Valid & GPS comp. & Prem. S & Stall \\
\midrule
{main_table_tex(summary)}
\bottomrule
\end{{tabular}}
\caption{{Full pedagogical-control metrics. Leak., Valid, GPS comp., Prem. S, and Stall are percentages.}}
\label{{tab:control}}
\end{{table*}}

Table~\ref{{tab:control}} shows the central result. GPS-Agent reduces direct-answer leakage from {pct(base['direct_answer_leakage_rate'])}\% to {pct(gps['direct_answer_leakage_rate'])}\%, with odds ratio {num(leak['effect_size'])} and Fisher $p={pval(leak['p_value'])}$. It also increases phase validity from {pct(base['phase_validity_rate'])}\% to {pct(gps['phase_validity_rate'])}\% ($p={pval(phase['p_value'])}$) and GPS completion from {pct(base['gps_completion_rate'])}\% to {pct(gps['gps_completion_rate'])}\% ($p={pval(complete['p_value'])}$). These are the strongest defensible claims.

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{figures/fig01_direct_answer_leakage.png}}
\caption{{GPS-Agent substantially reduces direct-answer leakage.}}
\label{{fig:leakage}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{figures/fig02_phase_validity.png}}
\caption{{GPS-Agent makes pedagogical phase validity measurable and substantially higher than the single-agent baseline.}}
\label{{fig:phase}}
\end{{figure}}

\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrrrr}}
\toprule
System & VAI & Math dens. & Reason rate & Student tok. & Tutor/Stud tok. & Answer dep. & APS \\
\midrule
{engagement_table_tex(summary)}
\bottomrule
\end{{tabular}}
\caption{{Engagement and autonomy diagnostics. APS = autonomy-process score. These are secondary process metrics, not learning-outcome claims.}}
\label{{tab:engagement}}
\end{{table*}}

The engagement picture is more cautious. GPS-Agent VAI is {num(gps['vai_mean'])}, while the baseline VAI is {num(base['vai_mean'])}; Welch $p={pval(vai['p_value'])}$ and Cohen's $d={num(vai['effect_size'])}$. Student reasoning-turn rate is {num(gps['student_reasoning_rate_mean'])} for GPS-Agent and {num(base['student_reasoning_rate_mean'])} for the baseline ($p={pval(reasoning['p_value'])}$). The autonomy-process score is higher under GPS-Agent ({num(gps['autonomy_process_score_mean'])} vs. {num(base['autonomy_process_score_mean'])}, $p={pval(aps['p_value'])}$), but it remains a process diagnostic.

\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrrrr}}
\toprule
Level & $N$ & Leak. & Valid & GPS comp. & Stall & VAI & Reason \\
\midrule
{level_table_tex(level)}
\bottomrule
\end{{tabular}}
\caption{{GPS-Agent metrics by student level. Percentages are shown as 0--100 values.}}
\label{{tab:level}}
\end{{table*}}

\section{{Failure and Robustness}}
The main remaining weakness is scaffolding pressure. GPS-Agent stall is {pct(gps['stall_rate'])}\%, compared with {pct(base['stall_rate'])}\% for the baseline ($p={pval(stall['p_value'])}$). This should not be interpreted as a baseline advantage: the baseline avoids stalls partly by not enforcing structured tutoring. However, from a pedagogical perspective, long repeated Practice or Guide chains may frustrate students.

The cross-model stress test confirms this limitation. Cross-model direct-answer leakage is {pct(cross['direct_answer_leakage_rate'])}\%, stall is {pct(cross['stall_rate'])}\%, non-Vietnamese leakage is {pct(cross['non_vietnamese_leakage_rate'])}\%, and VAI is {num(cross['vai_mean'])}. This suggests partial robustness but also model-sensitivity in language and stagnation control.

\section{{IRR and Data Quality Diagnostics}}
The current IRR file should be treated as diagnostic only. Recomputed agreement over {irr.get('n', 'NA')} paired ratings gives quadratic weighted kappa={num(irr.get('quadratic_weighted_kappa', float('nan')))} and unweighted kappa={num(irr.get('unweighted_kappa', float('nan')))}. Therefore the paper does not claim substantial agreement until a calibrated human or human-audited rubric is added.

\section{{Discussion}}
The fuller metric suite changes the interpretation of the project. The strongest result is not that GPS-Agent already improves final learning outcomes; the strongest result is that it makes process control measurable and reduces answer-giving. This is important because a tutor that cannot avoid premature solution disclosure is unlikely to support independent mathematical reasoning.

The results also define the next engineering target. The Supervisor should learn to distinguish productive struggle from unproductive stagnation. In future versions, Anti-Stagnation should be based on student-state evidence, frustration cues, and history-aware fading rather than only consecutive phase counts.

\section{{Conclusion}}
We presented a full-metric evaluation of GPS-Agent. The system substantially reduces direct-answer leakage and improves Guide--Practice--Solve compliance compared with a single-agent baseline. Secondary engagement metrics are reported transparently, but do not yet justify claims about long-term learning gain. The deliverable is therefore best framed as a reproducible system paper on pedagogical process control in LLM tutoring.

\section{{Limitations}}
The human/foundation layer is small, the controlled comparison relies on simulated learners, the 45-question bank still requires answer and option cleaning, and IRR must be rerun with calibrated annotation. The local style files included here are compile-compatible fallbacks; final submission should use official ACL style files.

\section{{Ethics Statement}}
GPS-Agent should support teachers rather than replace them. Logs may contain sensitive indicators of learning difficulty and must be protected. Metrics such as autonomy, stall, and leakage should be used for system diagnosis and teacher support, not punitive evaluation of learners.

\begin{{thebibliography}}{{}}
\bibitem[Koedinger and Corbett(2006)]{{koedinger2006cognitive}}
Koedinger, Kenneth R. and Corbett, Albert T. 2006. Cognitive tutors: Technology bringing learning science to the classroom. In \emph{{The Cambridge Handbook of the Learning Sciences}}.
\bibitem[Macina et~al.(2023)]{{macina2023mathdial}}
Macina, Jakub, Nico Daheim, Saurabh Srivastava, Philipp Mondorf, Katja Markert, Mrinmaya Sachan, and Mirella Lapata. 2023. MathDial: A dialogue tutoring dataset with rich pedagogical properties grounded in math reasoning problems. In \emph{{Findings of EMNLP}}.
\bibitem[Ryan and Deci(2000)]{{ryan2000self}}
Ryan, Richard M. and Edward L. Deci. 2000. Self-determination theory and the facilitation of intrinsic motivation, social development, and well-being. \emph{{American Psychologist}}, 55(1):68--78.
\bibitem[Tack and Piech(2022)]{{tack2022teacher}}
Tack, Anais and Chris Piech. 2022. The AI Teacher Test: Measuring the pedagogical ability of Blender and GPT-3 in educational dialogues. In \emph{{Proceedings of EDM}}.
\bibitem[VanLehn(2011)]{{vanlehn2011relative}}
VanLehn, Kurt. 2011. The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. \emph{{Educational Psychologist}}, 46(4):197--221.
\bibitem[Vygotsky(1978)]{{vygotsky1978mind}}
Vygotsky, Lev S. 1978. \emph{{Mind in Society: The Development of Higher Psychological Processes}}. Harvard University Press.
\bibitem[Wood et~al.(1976)]{{wood1976role}}
Wood, David, Jerome S. Bruner, and Gail Ross. 1976. The role of tutoring in problem solving. \emph{{Journal of Child Psychology and Psychiatry}}, 17(2):89--100.
\end{{thebibliography}}
\end{{document}}
""".strip() + "\n"
    (PAPER / "main.tex").write_text(tex, encoding="utf-8")


def compile_pdf() -> bool:
    try:
        result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=PAPER, text=True, capture_output=True, timeout=120)
        (PAPER / "compile.log").write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
        return (PAPER / "main.pdf").exists()
    except Exception as exc:
        (PAPER / "compile.log").write_text(str(exc), encoding="utf-8")
        return False


def zip_dir(src: Path, dest: Path) -> None:
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in src.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(src))


def write_manifest(sessions: pd.DataFrame, tables: dict, audits: dict) -> None:
    manifest = {
        "metric_groups": {
            "binary_metrics": BINARY_METRICS,
            "continuous_metrics": CONTINUOUS_METRICS,
            "primary_binary_metrics": PRIMARY_BINARY,
            "primary_continuous_metrics": PRIMARY_CONTINUOUS,
        },
        "data_layers": {name: str(path) for name, path in DATASETS.items()},
        "n_total_sessions_evaluated": int(len(sessions)),
        "audits": audits,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "full_metrics_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def run_all() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sessions = load_sessions()
    tables = write_tables(sessions)
    write_figures(tables["summary"])
    audits = audit_all(ROOT)
    write_manifest(sessions, tables, audits)
    write_latex_project(tables, audits)
    compiled = compile_pdf()
    zip_dir(PAPER, ROOT / "GPS_Agent_Full_Metrics_Overleaf.zip")
    # Code patch / package.
    package = ROOT / "GPS_AIedu_Full_Metrics_Package.zip"
    if package.exists():
        package.unlink()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as zf:
        include_roots = ["src/evaluation", "scripts", "tests", "data/outputs", "data/processed", "reports/full_metrics", "paper/full_metrics"]
        for root in include_roots:
            p = ROOT / root
            if p.exists():
                for f in p.rglob("*"):
                    if f.is_file() and "__pycache__" not in str(f):
                        zf.write(f, f.relative_to(ROOT))
    print("Full metrics pipeline complete")
    print(f"sessions={len(sessions)} compiled_pdf={compiled}")
    print(f"latex_zip={ROOT / 'GPS_Agent_Full_Metrics_Overleaf.zip'}")
    print(f"package={package}")


if __name__ == "__main__":
    run_all()
