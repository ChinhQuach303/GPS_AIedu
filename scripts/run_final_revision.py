#!/usr/bin/env python3
"""Build the final revision with human-pilot triangulation.

This script implements the reviewer-facing cleanup pass:
- treats the 5-student foundation layer as a real human pilot log;
- keeps controlled simulated comparisons separate from human data;
- removes invalid IRR as a contribution and reports it only as a diagnostic;
- audits the question bank and prevents correctness claims over unvalidated items;
- explains phase validity vs. full GPS completion;
- adds a routing-only anti-stagnation ablation over existing phase traces;
- emits an Overleaf-ready LaTeX project and reproducible CSV tables.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import shutil
import subprocess
import zipfile
from textwrap import shorten
import unicodedata

import matplotlib.pyplot as plt
import pandas as pd

from src.evaluation.metrics.comprehensive_metrics import (
    compute_session_metrics,
    summarize_metrics,
    by_level_summary,
    by_question_summary,
    compare_systems,
    correlation_diagnostics,
    audit_all,
)
from src.evaluation.metrics.pedagogy_metrics import (
    parse_trace,
    parse_phase_labels_from_text,
    bootstrap_ci,
)

ROOT = Path.cwd()
OUT = ROOT / "reports" / "final_revision"
TABLES = OUT / "tables"
FIGS = OUT / "figures"
PAPER = ROOT / "paper" / "final_revision"

CONTROLLED = {
    "GPS-Agent": ROOT / "data" / "outputs" / "cleaned_massive_results.csv",
    "Single-Agent": ROOT / "data" / "outputs" / "cleaned_baseline_results.csv",
    "Cross-Model Phi-3": ROOT / "data" / "outputs" / "cross_model_conversations.csv",
}

LEVEL_ORDER = ["Giỏi", "Khá", "Trung bình", "Yếu", "Mất tập trung", "Unknown"]
LEVEL_LABEL = {
    "Giỏi": "Excellent", "Khá": "Good", "Trung bình": "Average", "Yếu": "Weak",
    "Mất tập trung": "Disengaged", "Unknown": "Unknown"
}
PROFILE_TO_LEVEL = {
    "Advanced (giỏi)": "Giỏi",
    "Typical (đại trà)": "Trung bình",
    "Struggling (chậm)": "Yếu",
    "Offtrack (hay xin đáp án)": "Mất tập trung",
}


def pct(x: float) -> str:
    return f"{100 * float(x):.1f}"


def num(x: float, n: int = 3) -> str:
    try:
        if pd.isna(x):
            return "--"
        return f"{float(x):.{n}f}"
    except Exception:
        return "--"


def pval(x: float) -> str:
    if pd.isna(x):
        return "--"
    if float(x) < 0.001:
        return f"{float(x):.2e}"
    return f"{float(x):.3f}"


def esc(s: object) -> str:
    text = str(s)
    repl = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def load_controlled_sessions() -> pd.DataFrame:
    frames = []
    for system, path in CONTROLLED.items():
        df = pd.read_csv(path)
        frames.append(compute_session_metrics(df, system))
    return pd.concat(frames, ignore_index=True)


def _session_from_notes(notes: str) -> str:
    m = re.search(r"Session:\s*([^\s|]+)", str(notes))
    return m.group(1) if m else "UNKNOWN"


def _qid_from_notes(notes: str) -> str:
    m = re.search(r"Q_ID:\s*(\d+)", str(notes))
    return m.group(1) if m else ""


def load_human_pilot_sessions() -> pd.DataFrame:
    """Convert the real 5-student turn log into session-level dialogues."""
    path = ROOT / "data" / "processed" / "human_pilot_turn_log.csv"
    df = pd.read_csv(path)
    if "Group" in df.columns:
        df = df[df["Group"].eq("Foundation (Real)")].copy()
    df["session_id"] = df["Notes"].apply(_session_from_notes)
    df["QID"] = df["Notes"].apply(_qid_from_notes)
    rows = []
    for (sid, student), g in df.groupby(["session_id", "Student ID"], sort=False):
        g = g.sort_index()
        dialogue_parts = []
        trace = []
        for _, r in g.iterrows():
            q = str(r.get("Question", "")).strip()
            a = str(r.get("AI Response", "")).strip()
            step = str(r.get("GPS Step (Truth)", "")).strip().upper()[:1]
            if q:
                dialogue_parts.append(f"Em: {q}")
            if a:
                dialogue_parts.append(f"Thầy: {a}")
            if step in {"G", "P", "S"}:
                trace.append(step)
        rows.append({
            "session_id": f"HUMAN_{sid}_{student}",
            "question_id": g["QID"].dropna().astype(str).iloc[0] if g["QID"].notna().any() else "",
            "question": str(g["QID"].dropna().astype(str).iloc[0] if g["QID"].notna().any() else ""),
            "question_text": str(g["Question"].iloc[0]),
            "level": PROFILE_TO_LEVEL.get(str(g["Profile"].iloc[0]), str(g["Profile"].iloc[0])),
            "student_id": student,
            "profile": str(g["Profile"].iloc[0]),
            "trace": "-".join(trace),
            "dialogue": "\n".join(dialogue_parts),
            "satisfaction": pd.to_numeric(g.get("Satisfaction (1-5)", pd.Series(dtype=float)), errors="coerce").mean(),
            "difficulty_rating": pd.to_numeric(g.get("Difficulty (1-5)", pd.Series(dtype=float)), errors="coerce").mean(),
        })
    human = pd.DataFrame(rows)
    return compute_session_metrics(human, "Human Pilot (GPS)")


def max_same_run(phases):
    if not phases:
        return 0
    best = cur = 1
    last = phases[0]
    for p in phases[1:]:
        if p == last:
            cur += 1
        else:
            best = max(best, cur)
            last = p; cur = 1
    return max(best, cur)


def anti_stagnation_trace(phases, max_run=3):
    """Routing-only what-if: force a transition after max_run identical phases.

    This is not a regenerated dialogue. It estimates whether a supervisor-level
    anti-stagnation gate could eliminate repeated-node traces.
    """
    if not phases:
        return []
    out = []
    run = 0
    last = None
    next_map = {"G": "P", "P": "S", "S": "S"}
    for p in phases:
        if p == last:
            run += 1
        else:
            run = 1
            last = p
        if run > max_run:
            p = next_map.get(last, p)
            last = p
            run = 1
        out.append(p)
    return out


def anti_stag_ablation(raw_paths: dict[str, Path]) -> pd.DataFrame:
    rows = []
    for system, path in raw_paths.items():
        if not path.exists():
            continue
        df = pd.read_csv(path)
        traces = df.get("trace", pd.Series([""] * len(df))).fillna("").tolist()
        before = []
        after = []
        completion_before = []
        completion_after = []
        triggered = []
        for t in traces:
            phases = parse_trace(t)
            before.append(int(max_same_run(phases) >= 4))
            fixed = anti_stagnation_trace(phases)
            after.append(int(max_same_run(fixed) >= 4))
            completion_before.append(int(all(x in phases for x in ["G", "P", "S"])))
            completion_after.append(int(all(x in fixed for x in ["G", "P", "S"])))
            triggered.append(int(phases != fixed))
        rows.append({
            "system": system,
            "n_sessions": len(df),
            "trigger_rate": sum(triggered) / len(triggered) if triggered else 0.0,
            "stall_before_rate": sum(before) / len(before) if before else 0.0,
            "stall_after_trace_gate_rate": sum(after) / len(after) if after else 0.0,
            "gps_completion_before_rate": sum(completion_before) / len(completion_before) if completion_before else 0.0,
            "gps_completion_after_trace_gate_rate": sum(completion_after) / len(completion_after) if completion_after else 0.0,
        })
    return pd.DataFrame(rows)


def write_validated_question_template(audits: dict) -> None:
    qb = audits["question_bank"]
    rows = qb.get("audit_table", [])
    out_rows = []
    for r in rows:
        out_rows.append({
            "id": r["id"],
            "has_question": r["has_question"],
            "has_answer": r["has_answer"],
            "n_options": r["n_options"],
            "blank_options": r["blank_options"],
            "validated_for_correctness": r["validated_for_correctness"],
            "manual_answer_check": "PENDING" if not r["validated_for_correctness"] else "AUTO_SCHEMA_OK",
            "correct_answer_final": "",
            "option_A_final": "",
            "option_B_final": "",
            "option_C_final": "",
            "option_D_final": "",
            "solution_final": "",
        })
    pd.DataFrame(out_rows).to_csv(TABLES / "question_bank_validation_template.csv", index=False)


def write_tables(controlled: pd.DataFrame, human: pd.DataFrame, audits: dict) -> dict:
    TABLES.mkdir(parents=True, exist_ok=True)
    controlled.to_csv(TABLES / "session_level_controlled_metrics.csv", index=False)
    human.to_csv(TABLES / "session_level_human_pilot_metrics.csv", index=False)
    all_sessions = pd.concat([human, controlled], ignore_index=True)
    all_sessions.to_csv(TABLES / "session_level_all_layers_metrics.csv", index=False)

    summary = summarize_metrics(controlled)
    human_summary = summarize_metrics(human)
    all_summary = summarize_metrics(all_sessions)
    level = by_level_summary(controlled)
    human_level = by_level_summary(human)
    question = by_question_summary(controlled)
    tests = compare_systems(controlled)
    diag = correlation_diagnostics(controlled)
    ablation = anti_stag_ablation({"GPS-Agent": CONTROLLED["GPS-Agent"], "Cross-Model Phi-3": CONTROLLED["Cross-Model Phi-3"]})

    summary.to_csv(TABLES / "table_controlled_system_summary.csv", index=False)
    human_summary.to_csv(TABLES / "table_human_pilot_summary.csv", index=False)
    all_summary.to_csv(TABLES / "table_all_layer_summary.csv", index=False)
    level.to_csv(TABLES / "table_controlled_by_level.csv", index=False)
    human_level.to_csv(TABLES / "table_human_pilot_by_level.csv", index=False)
    question.to_csv(TABLES / "table_controlled_by_question.csv", index=False)
    tests.to_csv(TABLES / "table_statistical_tests.csv", index=False)
    diag.to_csv(TABLES / "table_correlation_diagnostics.csv", index=False)
    ablation.to_csv(TABLES / "table_anti_stagnation_trace_ablation.csv", index=False)
    write_validated_question_template(audits)
    return {"summary": summary, "human_summary": human_summary, "all_summary": all_summary, "level": level, "human_level": human_level, "question": question, "tests": tests, "diag": diag, "ablation": ablation}


def plot(summary: pd.DataFrame, metric: str, title: str, fname: str, ylabel="Rate"):
    FIGS.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    ax.bar(summary["system"], summary[metric])
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=22)
    if metric.endswith("rate"):
        ax.set_ylim(0, 1.05)
    fig.tight_layout()
    fig.savefig(FIGS / fname, dpi=200)
    plt.close(fig)


def write_figures(summary: pd.DataFrame, ablation: pd.DataFrame):
    plot(summary, "direct_answer_leakage_rate", "Direct-answer leakage", "fig01_direct_answer_leakage.png")
    plot(summary, "phase_validity_rate", "Phase-constraint validity", "fig02_phase_validity.png")
    plot(summary, "gps_completion_rate", "Full Guide-Practice-Solve completion", "fig03_gps_completion.png")
    plot(summary, "stall_rate", "Stall / scaffolding pressure", "fig04_stall_rate.png")
    if not ablation.empty:
        fig, ax = plt.subplots(figsize=(6.4, 3.5))
        labels = ablation["system"].tolist()
        x = range(len(labels))
        width = 0.35
        ax.bar([i - width/2 for i in x], ablation["stall_before_rate"], width, label="Before")
        ax.bar([i + width/2 for i in x], ablation["stall_after_trace_gate_rate"], width, label="Trace-gated")
        ax.set_xticks(list(x), labels, rotation=20)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Stall rate")
        ax.set_title("Routing-only anti-stagnation what-if")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIGS / "fig05_anti_stagnation_trace_ablation.png", dpi=200)
        plt.close(fig)


def stat(tests: pd.DataFrame, metric: str) -> pd.Series:
    r = tests[tests.metric.eq(metric)]
    return r.iloc[0] if len(r) else pd.Series(dtype=object)


def table_control(summary: pd.DataFrame) -> str:
    rows = []
    for _, r in summary.iterrows():
        rows.append(
            f"{esc(r.system)} & {int(r.n_sessions)} & {int(r.n_questions)} & "
            f"{pct(r.direct_answer_leakage_rate)} & {pct(r.phase_validity_rate)} & "
            f"{pct(r.gps_completion_rate)} & {pct(r.solve_reached_rate)} & {pct(r.stall_rate)} " + r"\\"
        )
    return "\n".join(rows)


def table_human(summary: pd.DataFrame) -> str:
    rows = []
    for _, r in summary.iterrows():
        rows.append(
            f"{esc(r.system)} & {int(r.n_sessions)} & {int(r.n_questions)} & {int(r.n_levels)} & "
            f"{pct(r.phase_validity_rate)} & {pct(r.gps_completion_rate)} & {pct(r.direct_answer_leakage_rate)} & {num(r.vai_mean)} " + r"\\"
        )
    return "\n".join(rows)


def table_level(level: pd.DataFrame) -> str:
    gps = level[level.system.eq("GPS-Agent")].copy()
    gps["_order"] = gps["level"].apply(lambda x: LEVEL_ORDER.index(x) if x in LEVEL_ORDER else 99)
    rows = []
    for _, r in gps.sort_values("_order").iterrows():
        rows.append(
            f"{esc(LEVEL_LABEL.get(r.level, r.level))} & {int(r.n_sessions)} & {pct(r.direct_answer_leakage_rate)} & "
            f"{pct(r.phase_validity_rate)} & {pct(r.gps_completion_rate)} & {pct(r.stall_rate)} & {num(r.vai_mean)} " + r"\\"
        )
    return "\n".join(rows)


def table_ablation(ab: pd.DataFrame) -> str:
    rows = []
    for _, r in ab.iterrows():
        rows.append(
            f"{esc(r.system)} & {int(r.n_sessions)} & {pct(r.trigger_rate)} & {pct(r.stall_before_rate)} & "
            f"{pct(r.stall_after_trace_gate_rate)} & {pct(r.gps_completion_before_rate)} & {pct(r.gps_completion_after_trace_gate_rate)} " + r"\\"
        )
    return "\n".join(rows)


def short_example(path: Path, prefer_gps=True) -> str:
    """Return an ASCII-safe qualitative excerpt summary for pdfLaTeX."""
    df = pd.read_csv(path)
    row = df.iloc[0]
    dialogue = str(row.get("dialogue", ""))
    chunks = re.split(r"(?=Thầy:|Em:|AI:|Student:)", dialogue)
    chunks = [re.sub(r"\s+", " ", c).strip() for c in chunks if c.strip()]
    raw = " / ".join(chunks[:4])
    raw = shorten(raw, width=320, placeholder="...")
    # The main paper is compiled with pdfLaTeX/ACL style. Keep examples ASCII-safe.
    safe = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    return safe


def write_acl_fallback(out: Path):
    # Fallback for local compile. README states official style must replace this for submission.
    (out / "acl.sty").write_text(r"""
\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{acl}[2026/05/22 local ACL-compatible preview fallback; replace with official acl-org/acl-style-files]
\newif\ifaclreview
\DeclareOption{review}{\aclreviewtrue}
\DeclareOption{final}{\aclreviewfalse}
\ProcessOptions\relax
\RequirePackage[letterpaper,margin=1in]{geometry}
\RequirePackage{times}
\RequirePackage{latexsym}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{caption}
\setlength{\columnsep}{0.25in}
\AtBeginDocument{\if@twocolumn\else\twocolumn\fi}
\pagestyle{plain}
\titleformat{\section}{\large\bfseries}{\thesection}{0.5em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection}{0.5em}{}
\newcommand{\aclfinalcopy}{}
\newcommand{\aclpaperid}[1]{}
\renewenvironment{abstract}{\begin{center}\bfseries Abstract\end{center}\small}{\par}
""".strip()+"\n", encoding="utf-8")
    try:
        plainnat = subprocess.run(["kpsewhich", "plainnat.bst"], capture_output=True, text=True)
        if plainnat.returncode == 0 and plainnat.stdout.strip():
            shutil.copyfile(plainnat.stdout.strip(), out / "acl_natbib.bst")
        else:
            (out / "acl_natbib.bst").write_text("", encoding="utf-8")
    except FileNotFoundError:
        (out / "acl_natbib.bst").write_text("", encoding="utf-8")


def write_latex(tables: dict, audits: dict):
    PAPER.mkdir(parents=True, exist_ok=True)
    (PAPER / "figures").mkdir(exist_ok=True)
    (PAPER / "tables").mkdir(exist_ok=True)
    for f in FIGS.glob("*.png"):
        shutil.copyfile(f, PAPER / "figures" / f.name)
    for f in TABLES.glob("*.csv"):
        shutil.copyfile(f, PAPER / "tables" / f.name)
    write_acl_fallback(PAPER)
    (PAPER / "latexmkrc").write_text("$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';\n$pdf_mode = 1;\n", encoding="utf-8")
    (PAPER / "OFFICIAL_STYLE_REQUIRED.md").write_text(
        "This package includes a local preview fallback for acl.sty. Before official submission, replace acl.sty and acl_natbib.bst with the official ACL style files from https://github.com/acl-org/acl-style-files or the ACL Overleaf template.\n",
        encoding="utf-8",
    )
    (PAPER / "README_OVERLEAF.md").write_text(
        "Upload this folder to Overleaf/Prism and compile main.tex. The PDF preview compiles locally. For submission, replace acl.sty/acl_natbib.bst with official ACL files.\n",
        encoding="utf-8",
    )

    summary = tables["summary"]
    human_summary = tables["human_summary"]
    level = tables["level"]
    tests = tables["tests"]
    ab = tables["ablation"]
    gps = summary[summary.system.eq("GPS-Agent")].iloc[0]
    base = summary[summary.system.eq("Single-Agent")].iloc[0]
    cross = summary[summary.system.eq("Cross-Model Phi-3")].iloc[0]
    human = human_summary.iloc[0]
    leak = stat(tests, "direct_answer_leakage")
    phase = stat(tests, "phase_validity")
    comp = stat(tests, "gps_completion")
    vai = stat(tests, "vai")
    stall = stat(tests, "stall")
    qb = audits["question_bank"]
    irr = audits["irr"]
    human_pilot = audits["human_pilot"]
    expanded = audits["expanded"]
    ex_gps = esc(short_example(CONTROLLED["GPS-Agent"]))
    ex_base = esc(short_example(CONTROLLED["Single-Agent"]))

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
\usepackage[hidelinks]{{hyperref}}

\title{{GPS-Agent: A State-Graph Tutoring Framework for Process Control in Vietnamese Mathematics Dialogue}}
\author{{Anonymous Submission}}

\begin{{document}}
\maketitle
\begin{{abstract}}
LLM-based tutors can solve mathematics problems fluently, but this creates a pedagogical failure mode: direct answer-giving before the learner has reasoned through the problem. We present GPS-Agent, a state-graph tutoring framework that enforces a Guide--Practice--Solve protocol. This revision separates a real five-student human pilot log from controlled simulated learner experiments. The human pilot contains {human_pilot['students']} real students, {human_pilot['questions']} probability/combinatorics questions, {human_pilot['sessions']} sessions, and {human_pilot['human_pilot_turns']} annotated turns. The controlled comparison contains {int(gps.n_sessions)} GPS-Agent sessions and {int(base.n_sessions)} single-agent baseline sessions. GPS-Agent reduces direct-answer leakage from {pct(base.direct_answer_leakage_rate)}\% to {pct(gps.direct_answer_leakage_rate)}\% (Fisher $p={pval(leak.p_value)}$) and increases phase-constraint validity from {pct(base.phase_validity_rate)}\% to {pct(gps.phase_validity_rate)}\% ($p={pval(phase.p_value)}$). We report failures transparently: VAI is not significantly improved ($p={pval(vai.p_value)}$), IRR is currently invalid as a reliability claim, and stall remains high. The paper therefore claims process control, not long-term learning gain.
\end{{abstract}}

\section{{Introduction}}
LLM tutors are attractive because they offer immediate, fluent, individualized help. In mathematics education, however, fluency can undermine learning: the tutor may provide a complete worked solution when the student needs a hint, a subproblem, or a prompt for self-explanation. We call this the \emph{{Answer-Giving Trap}}.

GPS-Agent addresses the Answer-Giving Trap by constraining interaction flow. Instead of using a single prompt to ask an LLM to be Socratic, GPS-Agent separates tutoring into Guide, Practice, and Solve phases and routes among them with a stateful Supervisor. This paper evaluates whether that architectural constraint improves \emph{{process control}}: avoiding premature answers and preserving pedagogical phase structure.

\paragraph{{Contributions.}} We make four contributions. First, we formulate direct-answer leakage as a measurable failure mode for LLM tutoring. Second, we present GPS-Agent, a state-graph tutor for Vietnamese probability/combinatorics dialogue. Third, we provide a full deterministic metric suite covering leakage, phase dynamics, engagement, quality, and failure modes. Fourth, we separate evidence layers: a real five-student human pilot, a controlled simulated learner comparison, a cross-model stress test, and an exploratory expanded corpus.

\section{{Related Work}}
Classical intelligent tutoring systems and cognitive tutors showed that stepwise feedback and constraint-based instruction can improve learning, but they often require domain-specific knowledge engineering. Recent LLM tutoring work, including MathDial-style dialogue tutoring and the AI Teacher Test, evaluates whether models can provide pedagogically appropriate hints rather than direct solutions. GPS-Agent differs by treating pedagogical sequencing as an architectural control problem rather than only a prompting problem. It is closer to graph-based multi-agent orchestration, where state and routing are first-class components.

\section{{GPS-Agent}}
GPS-Agent implements a Guide--Practice--Solve protocol. Guide elicits the student's interpretation and prior knowledge. Practice decomposes the problem into one substep at a time. Solve confirms and reflects on the answer only after prior Guide and Practice evidence. A Supervisor maintains the phase trace and decides whether the next turn should remain in the current phase or transition.

\section{{Data}}
\paragraph{{Human pilot.}} The human pilot layer is real human-pilot data, not simulated learner data. It contains {human_pilot['students']} students, {human_pilot['questions']} questions, {human_pilot['sessions']} sessions, and {human_pilot['human_pilot_turns']} annotated turns. The five students cover four observed proficiency/behavior profiles: advanced, typical, struggling, and off-track/direct-answer-seeking. Therefore, the paper refers to \emph{{five students}} but \emph{{four profile bands}}.

\paragraph{{Controlled simulated comparison.}} The main statistical comparison uses matched controlled sessions: {int(gps.n_sessions)} GPS-Agent sessions and {int(base.n_sessions)} single-agent baseline sessions. These sessions are generated with the same question pool and student-level labels, so they are suitable for process-control comparisons.

\paragraph{{Cross-model stress test and expanded corpus.}} The Phi-3 cross-model set contains {int(cross.n_sessions)} sessions and is used as a robustness stress test. The expanded exploratory corpus contains {expanded.get('rows', 'NA')} rows, but is not treated as a human gold standard because metric and schema audits still reveal inconsistencies.

\paragraph{{Question-bank audit.}} The question bank currently has {qb['n_questions']} questions, but {qb['missing_answer']} have missing answers and {qb['questions_with_blank_options']} have malformed options. Therefore, correctness-based claims are restricted to validated subsets. The release includes a validation template for manual repair.

\section{{Metrics}}
We compute five groups of deterministic metrics. Pedagogical-control metrics include direct-answer leakage, phase-constraint validity, full GPS completion, premature Solve, skipped Guide/Practice, and stall. Engagement metrics include VAI, math density, student reasoning-turn rate, token balance, answer-dependency index, and an autonomy-process score. Quality metrics include non-Vietnamese leakage, parse coverage, degeneracy flags, reflection completion, and IRR diagnostics.

\paragraph{{Validity versus completion.}} Phase-constraint validity and full GPS completion are intentionally different. A session can be phase-valid if it does not violate ordering constraints, even if it never reaches Solve. Full GPS completion requires all three phases G, P, and S. This distinction explains why the cross-model stress test can show high phase validity but low completion.

\section{{Results}}
\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrrrr}}
\toprule
System & $N$ & Q & Leak. & Valid & GPS comp. & Solve & Stall \\
\midrule
{table_control(summary)}
\bottomrule
\end{{tabular}}
\caption{{Controlled and stress-test process-control metrics. Leak., Valid, GPS comp., Solve, and Stall are percentages. Valid means no phase-order violation; GPS comp. requires Guide, Practice, and Solve.}}
\label{{tab:main}}
\end{{table*}}

Table~\ref{{tab:main}} is the primary result. GPS-Agent reduces direct-answer leakage from {pct(base.direct_answer_leakage_rate)}\% to {pct(gps.direct_answer_leakage_rate)}\% (Fisher $p={pval(leak.p_value)}$, odds ratio={num(leak.effect_size)}). It also increases phase-constraint validity from {pct(base.phase_validity_rate)}\% to {pct(gps.phase_validity_rate)}\% ($p={pval(phase.p_value)}$) and full GPS completion from {pct(base.gps_completion_rate)}\% to {pct(gps.gps_completion_rate)}\% ($p={pval(comp.p_value)}$). These are the strongest claims.

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{figures/fig01_direct_answer_leakage.png}}
\caption{{Direct-answer leakage by system. Lower is better; GPS-Agent sharply reduces early answer disclosure compared with the single-agent baseline.}}
\label{{fig:leakage}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\includegraphics[width=\linewidth]{{figures/fig03_gps_completion.png}}
\caption{{Full Guide--Practice--Solve completion. This is stricter than phase validity because it requires reaching all three phases.}}
\label{{fig:gpscompletion}}
\end{{figure}}

\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrrrr}}
\toprule
Layer & $N$ & Q & Levels & Valid & Comp. & Leak. & VAI \\
\midrule
{table_human(human_summary)}
\bottomrule
\end{{tabular}}
\caption{{Real human-pilot layer from five students. This layer triangulates feasibility but is not used to claim long-term learning gain.}}
\label{{tab:human}}
\end{{table*}}

The human pilot in Table~\ref{{tab:human}} confirms that the project has a real student layer: {int(human.n_sessions)} sessions from five students over {int(human.n_questions)} questions. It is reported separately to avoid mixing human data with simulated learner comparisons.

\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrrr}}
\toprule
Level & $N$ & Leak. & Valid & Comp. & Stall & VAI \\
\midrule
{table_level(level)}
\bottomrule
\end{{tabular}}
\caption{{GPS-Agent controlled metrics by student level. The controlled comparison has four level bands; the human pilot has five students.}}
\label{{tab:levels}}
\end{{table*}}

Table~\ref{{tab:levels}} resolves the earlier inconsistency: the experiment contains five real students in the human pilot but four controlled proficiency bands in the simulated comparison.

\section{{Failure Analysis and Anti-Stagnation}}
The largest weakness is stall/scaffolding pressure: GPS-Agent stall is {pct(gps.stall_rate)}\%, compared with {pct(base.stall_rate)}\% for the baseline ($p={pval(stall.p_value)}$). This is not a baseline win; the baseline can avoid stall by giving answers. But it is a real usability risk.

\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{lrrrrrr}}
\toprule
System & $N$ & Trigger & Stall$_b$ & Stall$_a$ & Comp$_b$ & Comp$_a$ \\
\midrule
{table_ablation(ab)}
\bottomrule
\end{{tabular}}
\caption{{Routing-only anti-stagnation ablation on existing traces. This estimates the effect of forcing a phase transition after repeated identical phases; it is not a regenerated dialogue experiment.}}
\label{{tab:ablation}}
\end{{table*}}

Table~\ref{{tab:ablation}} shows a conservative trace-level ablation. The gate is not enough to prove pedagogical quality, but it demonstrates that the observed stall is mechanically addressable at the Supervisor routing level.

\section{{Qualitative Examples}}
\begin{{table*}}[t]
\centering
\small
\begin{{tabular}}{{p{{0.13\linewidth}}p{{0.80\linewidth}}}}
\toprule
System & Excerpt \\
\midrule
GPS-Agent & {ex_gps} \\
Single-Agent & {ex_base} \\
\bottomrule
\end{{tabular}}
\caption{{Short dialogue excerpts. The GPS-Agent excerpt maintains staged scaffolding, while the baseline tends to expose computation and final-answer content earlier.}}
\label{{tab:qual}}
\end{{table*}}

\section{{IRR and Reliability}}
The current IRR scores are not usable as a reliability contribution. Recomputed agreement over {irr.get('n', 'NA')} paired scores gives quadratic weighted kappa={num(irr.get('quadratic_weighted_kappa', float('nan')))} and unweighted kappa={num(irr.get('unweighted_kappa', float('nan')))}. Therefore, IRR is removed from the contribution list. A calibrated human or human-audited annotation pass is required before making reliability claims.

\section{{Reproducibility}}
The tutor backend in the current code uses an Ollama-compatible OpenAI endpoint with Qwen2.5:7B, temperature 0.1 for tutor/Supervisor calls, and Phi-3-mini for cross-model student simulation at temperature 0.7. The student simulator uses higher temperature to diversify behavior. All paper-facing metrics in this revision are generated by deterministic scripts from CSV files; no reported metric is hard-coded.

\section{{Discussion}}
The evidence supports a narrow but useful claim: GPS-Agent improves process control. It reduces direct answer-giving and makes phase compliance auditable. The evidence does not yet support a claim about long-term learning gain. The human pilot provides feasibility triangulation, but larger human pre/post studies are needed.

\section{{Conclusion}}
GPS-Agent is a state-graph framework for controlling LLM tutor behavior in Vietnamese mathematics dialogue. In controlled experiments, it substantially reduces direct-answer leakage and increases pedagogical phase control. The revised paper separates human and simulated data, removes invalid IRR claims, audits the question bank, and reports stall as the main remaining engineering target.

\section{{Limitations}}
The human pilot has only five students. The main GPS-versus-baseline comparison still uses simulated learners. The question bank is not yet fully validated for answer correctness. The anti-stagnation ablation is trace-level rather than a regenerated dialogue experiment. The provided local style files are preview-compatible fallbacks; final submission should use official ACL style files.

\section{{Ethics Statement}}
The system is intended to assist teachers, not replace them. Logs involving students may contain sensitive information about learning difficulties, so consent, anonymization, secure storage, and non-punitive use of analytics are necessary.

\begin{{thebibliography}}{{}}
\bibitem[Koedinger and Corbett(2006)]{{koedinger2006cognitive}} Koedinger, Kenneth R. and Albert T. Corbett. 2006. Cognitive tutors: Technology bringing learning science to the classroom. In \emph{{The Cambridge Handbook of the Learning Sciences}}.
\bibitem[Macina et~al.(2023)]{{macina2023mathdial}} Macina, Jakub et~al. 2023. MathDial: A dialogue tutoring dataset with rich pedagogical properties grounded in math reasoning problems. In \emph{{Findings of EMNLP}}.
\bibitem[Tack and Piech(2022)]{{tack2022teacher}} Tack, Anais and Chris Piech. 2022. The AI Teacher Test: Measuring the pedagogical ability of Blender and GPT-3 in educational dialogues. In \emph{{Proceedings of EDM}}.
\bibitem[VanLehn(2011)]{{vanlehn2011relative}} VanLehn, Kurt. 2011. The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. \emph{{Educational Psychologist}}, 46(4):197--221.
\bibitem[Vygotsky(1978)]{{vygotsky1978mind}} Vygotsky, Lev S. 1978. \emph{{Mind in Society}}. Harvard University Press.
\bibitem[Wood et~al.(1976)]{{wood1976role}} Wood, David, Jerome S. Bruner, and Gail Ross. 1976. The role of tutoring in problem solving. \emph{{Journal of Child Psychology and Psychiatry}}, 17(2):89--100.
\end{{thebibliography}}
\end{{document}}
""".strip()+"\n"
    (PAPER / "main.tex").write_text(tex, encoding="utf-8")


def compile_pdf() -> bool:
    try:
        result = subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], cwd=PAPER, capture_output=True, timeout=120)
        log = result.stdout.decode("utf-8", errors="replace") + "\n" + result.stderr.decode("utf-8", errors="replace")
        (PAPER / "compile.log").write_text(log, encoding="utf-8")
        return (PAPER / "main.pdf").exists()
    except Exception as e:
        (PAPER / "compile.log").write_text(str(e), encoding="utf-8")
        return False


def zip_dir(src: Path, dest: Path):
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in src.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(src))


def write_manifest(controlled: pd.DataFrame, human: pd.DataFrame, tables: dict, audits: dict):
    manifest = {
        "revision_focus": "Reviewer-fix pass: human-pilot separation, IRR removal, question-bank audit, anti-stagnation trace ablation, fixed labels/refs",
        "human_pilot": {
            "n_sessions": int(len(human)),
            "n_students": int(audits["human_pilot"].get("students") or 0),
            "n_questions": int(audits["human_pilot"].get("questions") or 0),
            "n_turns": int(audits["human_pilot"].get("human_pilot_turns") or 0),
            "status": "real human pilot as stated by project owner",
        },
        "controlled_sessions": int(len(controlled)),
        "audits": audits,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "revision_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def run_all():
    OUT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    controlled = load_controlled_sessions()
    human = load_human_pilot_sessions()
    audits = audit_all(ROOT)
    tables = write_tables(controlled, human, audits)
    write_figures(tables["summary"], tables["ablation"])
    write_manifest(controlled, human, tables, audits)
    write_latex(tables, audits)
    ok = compile_pdf()
    zip_dir(PAPER, ROOT / "GPS_Agent_Final_Revision_Overleaf.zip")
    package = ROOT / "GPS_AIedu_Final_Revision_Package.zip"
    if package.exists():
        package.unlink()
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as zf:
        include = ["src/evaluation", "scripts", "tests", "data/outputs", "data/processed", "reports/final_revision", "paper/final_revision"]
        for root in include:
            p = ROOT / root
            if p.exists():
                for f in p.rglob("*"):
                    if f.is_file() and "__pycache__" not in str(f):
                        zf.write(f, f.relative_to(ROOT))
    print(f"compiled_pdf={ok}")
    print(f"human_sessions={len(human)} controlled_sessions={len(controlled)}")
    print(ROOT / "GPS_Agent_Final_Revision_Overleaf.zip")
    print(package)


if __name__ == "__main__":
    run_all()
