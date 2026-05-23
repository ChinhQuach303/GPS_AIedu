"""Comprehensive deterministic metrics for GPS-Agent evaluation.

This module is deliberately LLM-free. It converts heterogeneous tutoring logs
into a shared session-level representation and computes a fuller metric suite:

- pedagogical control: leakage, phase validity, premature solve, completion;
- phase dynamics: G/P/S counts, loop pressure, max repeated phase run;
- learner engagement: VAI, math density, reasoning turns, token balance;
- language/data quality: non-Vietnamese leakage, parse coverage, degeneracy;
- statistics: Welch tests for continuous metrics and Fisher exact tests for
  binary metrics.

The intent is to make every paper-facing number reproducible from CSV files.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import math
import re

import numpy as np
import pandas as pd
from scipy import stats

from src.evaluation.metrics.pedagogy_metrics import (
    analyze_dialogue,
    bootstrap_ci,
    cohen_d,
    non_vietnamese_leakage,
    normalize_level,
    parse_phase_labels_from_text,
    parse_trace,
    parse_turns_cached,
    question_bank_audit,
    human_pilot_summary,
    expanded_corpus_quality,
    compute_irr_from_file,
)

TOKEN_RE = re.compile(r"\w+", re.UNICODE)


@dataclass(frozen=True)
class SessionMetricRow:
    system: str
    session_id: str
    question_id: str
    question: str
    level: str
    trace: str
    n_turns: int
    tutor_turns: int
    student_turns: int
    parsed_turn_ratio: float
    student_tokens: int
    tutor_tokens: int
    token_balance_student_share: float
    tutor_student_token_ratio: float
    student_math: int
    tutor_math: int
    total_math: int
    vai: float
    vai_observable: int
    math_density: float
    student_reasoning_turns: int
    student_reasoning_rate: float
    direct_answer_leakage: int
    non_vietnamese_leakage: int
    reflection_required: int
    reflection_completed: int
    reflection_completion: int
    phase_validity: int
    solve_reached: int
    gps_completion: int
    premature_solve: int
    skipped_guide: int
    skipped_practice: int
    stall: int
    guide_loop: int
    practice_pressure: int
    max_same_phase_run: int
    n_guide: int
    n_practice: int
    n_solve: int
    phase_balance_entropy: float
    degeneracy_flag: int
    answer_dependency_index: float
    autonomy_process_score: float


def _safe_text(x: object) -> str:
    if pd.isna(x):
        return ""
    return str(x)


def _token_count(text: str) -> int:
    return len(TOKEN_RE.findall(text or ""))


def _max_same_run(phases: Sequence[str]) -> int:
    if not phases:
        return 0
    best = cur = 1
    last = phases[0]
    for p in phases[1:]:
        if p == last:
            cur += 1
        else:
            last = p
            cur = 1
        best = max(best, cur)
    return best


def _phase_entropy(phases: Sequence[str]) -> float:
    if not phases:
        return 0.0
    counts = np.array([phases.count("G"), phases.count("P"), phases.count("S")], dtype=float)
    probs = counts[counts > 0] / counts.sum()
    if len(probs) == 0:
        return 0.0
    return float(-(probs * np.log2(probs)).sum() / math.log2(3))


def _phase_metrics(trace: object, dialogue: str) -> Dict[str, int | float]:
    phases = parse_trace(trace) or parse_phase_labels_from_text(dialogue)
    n_g, n_p, n_s = phases.count("G"), phases.count("P"), phases.count("S")
    solve_reached = int(n_s > 0)
    if solve_reached:
        first_s = phases.index("S")
        before_s = phases[:first_s]
        phase_validity = int("G" in before_s and "P" in before_s)
        premature_solve = int(not phase_validity)
        skipped_guide = int("G" not in before_s)
        skipped_practice = int("P" not in before_s)
    else:
        phase_validity = int(bool(phases) and phases[0] == "G")
        premature_solve = 0
        skipped_guide = 0
        skipped_practice = 0
    max_run = _max_same_run(phases)
    return {
        "phase_validity": phase_validity,
        "solve_reached": solve_reached,
        "gps_completion": int(n_g > 0 and n_p > 0 and n_s > 0),
        "premature_solve": premature_solve,
        "skipped_guide": skipped_guide,
        "skipped_practice": skipped_practice,
        "stall": int(max_run >= 4),
        "guide_loop": int(_max_same_run([p for p in phases if p == "G"]) >= 4) if n_g >= 4 else 0,
        "practice_pressure": int(_max_same_run([p for p in phases if p == "P"]) >= 4) if n_p >= 4 else 0,
        "max_same_phase_run": int(max_run),
        "n_guide": int(n_g),
        "n_practice": int(n_p),
        "n_solve": int(n_s),
        "phase_balance_entropy": _phase_entropy(phases),
    }


def compute_session_metrics(df: pd.DataFrame, system: str) -> pd.DataFrame:
    """Return a session-level metric table for one system/data layer."""
    rows: List[dict] = []
    d = df.copy()
    if "dialogue" not in d.columns and "Dialogue" in d.columns:
        d["dialogue"] = d["Dialogue"]
    if "trace" not in d.columns and "Trace" in d.columns:
        d["trace"] = d["Trace"]
    if "trace" not in d.columns:
        d["trace"] = ""
    if "level" not in d.columns and "Level" in d.columns:
        d["level"] = d["Level"]
    if "level" not in d.columns:
        d["level"] = "Unknown"
    if "question" not in d.columns and "Question" in d.columns:
        d["question"] = d["Question"]
    if "question" not in d.columns:
        d["question"] = ""
    if "session_id" not in d.columns:
        d["session_id"] = [f"{system}_{i}" for i in range(len(d))]

    for i, r in d.iterrows():
        dialogue = _safe_text(r.get("dialogue", ""))
        trace = _safe_text(r.get("trace", ""))
        turns = parse_turns_cached(dialogue)
        tutor_turns = [t for t in turns if t.speaker == "Tutor"]
        student_turns = [t for t in turns if t.speaker == "Student"]
        student_tokens = sum(_token_count(t.text) for t in student_turns)
        tutor_tokens = sum(_token_count(t.text) for t in tutor_turns)
        total_tokens = student_tokens + tutor_tokens
        base = analyze_dialogue(dialogue, trace)
        phase = _phase_metrics(trace, dialogue)
        total_math = base.student_math + base.tutor_math
        vai_observable = int(total_math > 0)
        student_reasoning_rate = base.student_reasoning_turns / len(student_turns) if student_turns else 0.0
        token_share = student_tokens / total_tokens if total_tokens else 0.0
        ratio = tutor_tokens / max(student_tokens, 1)
        answer_dependency = base.tutor_math / max(base.student_math, 1)
        reflection_completion = int(base.reflection_required and base.reflection_completed)
        # Bounded process score for secondary analysis only: combines student math share,
        # reasoning-rate, phase validity, and answer-leakage penalty.
        autonomy_process_score = float(
            np.mean([
                base.vai,
                student_reasoning_rate,
                float(phase["phase_validity"]),
                1.0 - float(base.direct_answer_leakage),
            ])
        )
        row = SessionMetricRow(
            system=system,
            session_id=_safe_text(r.get("session_id", f"{system}_{i}")),
            question_id=_safe_text(r.get("QID", r.get("question_id", r.get("question", i)))),
            question=_safe_text(r.get("question", "")),
            level=normalize_level(r.get("level", "Unknown")),
            trace=trace,
            n_turns=base.n_turns,
            tutor_turns=base.tutor_turns,
            student_turns=base.student_turns,
            parsed_turn_ratio=(base.n_turns / max(dialogue.count("\n") + 1, 1)),
            student_tokens=student_tokens,
            tutor_tokens=tutor_tokens,
            token_balance_student_share=token_share,
            tutor_student_token_ratio=ratio,
            student_math=base.student_math,
            tutor_math=base.tutor_math,
            total_math=total_math,
            vai=base.vai,
            vai_observable=vai_observable,
            math_density=base.math_density,
            student_reasoning_turns=base.student_reasoning_turns,
            student_reasoning_rate=student_reasoning_rate,
            direct_answer_leakage=base.direct_answer_leakage,
            non_vietnamese_leakage=base.non_vietnamese_leakage,
            reflection_required=base.reflection_required,
            reflection_completed=base.reflection_completed,
            reflection_completion=reflection_completion,
            degeneracy_flag=int(base.n_turns == 0 or (student_tokens + tutor_tokens) < 10),
            answer_dependency_index=answer_dependency,
            autonomy_process_score=autonomy_process_score,
            **phase,
        )
        rows.append(asdict(row))
    return pd.DataFrame(rows)


BINARY_METRICS = [
    "direct_answer_leakage",
    "phase_validity",
    "solve_reached",
    "gps_completion",
    "premature_solve",
    "skipped_guide",
    "skipped_practice",
    "stall",
    "guide_loop",
    "practice_pressure",
    "reflection_completion",
    "non_vietnamese_leakage",
    "degeneracy_flag",
]

CONTINUOUS_METRICS = [
    "n_turns",
    "tutor_turns",
    "student_turns",
    "parsed_turn_ratio",
    "student_tokens",
    "tutor_tokens",
    "token_balance_student_share",
    "tutor_student_token_ratio",
    "student_math",
    "tutor_math",
    "total_math",
    "vai",
    "math_density",
    "student_reasoning_turns",
    "student_reasoning_rate",
    "max_same_phase_run",
    "n_guide",
    "n_practice",
    "n_solve",
    "phase_balance_entropy",
    "answer_dependency_index",
    "autonomy_process_score",
]

PRIMARY_BINARY = ["direct_answer_leakage", "phase_validity", "gps_completion", "premature_solve", "stall"]
PRIMARY_CONTINUOUS = ["vai", "math_density", "student_reasoning_rate", "token_balance_student_share", "autonomy_process_score"]


def summarize_metrics(sessions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for system, g in sessions.groupby("system", sort=False):
        row: Dict[str, object] = {
            "system": system,
            "n_sessions": len(g),
            "n_questions": g["question"].nunique() if "question" in g.columns else np.nan,
            "n_levels": g["level"].nunique() if "level" in g.columns else np.nan,
        }
        for m in BINARY_METRICS:
            if m in g:
                row[f"{m}_rate"] = float(g[m].mean())
                lo, hi = bootstrap_ci(g[m], n_boot=2000)
                row[f"{m}_ci_low"] = lo
                row[f"{m}_ci_high"] = hi
        for m in CONTINUOUS_METRICS:
            if m in g:
                row[f"{m}_mean"] = float(g[m].mean())
                row[f"{m}_sd"] = float(g[m].std(ddof=1)) if len(g) > 1 else 0.0
                lo, hi = bootstrap_ci(g[m], n_boot=2000)
                row[f"{m}_ci_low"] = lo
                row[f"{m}_ci_high"] = hi
        rows.append(row)
    return pd.DataFrame(rows)


def by_level_summary(sessions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (system, level), g in sessions.groupby(["system", "level"], dropna=False):
        rows.append({
            "system": system,
            "level": level,
            "n_sessions": len(g),
            "direct_answer_leakage_rate": float(g["direct_answer_leakage"].mean()),
            "phase_validity_rate": float(g["phase_validity"].mean()),
            "gps_completion_rate": float(g["gps_completion"].mean()),
            "stall_rate": float(g["stall"].mean()),
            "vai_mean": float(g["vai"].mean()),
            "math_density_mean": float(g["math_density"].mean()),
            "student_reasoning_rate_mean": float(g["student_reasoning_rate"].mean()),
            "autonomy_process_score_mean": float(g["autonomy_process_score"].mean()),
            "token_balance_student_share_mean": float(g["token_balance_student_share"].mean()),
        })
    return pd.DataFrame(rows)


def by_question_summary(sessions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (system, question), g in sessions.groupby(["system", "question"], dropna=False):
        rows.append({
            "system": system,
            "question": question,
            "n_sessions": len(g),
            "n_levels": g["level"].nunique(),
            "direct_answer_leakage_rate": float(g["direct_answer_leakage"].mean()),
            "phase_validity_rate": float(g["phase_validity"].mean()),
            "gps_completion_rate": float(g["gps_completion"].mean()),
            "stall_rate": float(g["stall"].mean()),
            "vai_mean": float(g["vai"].mean()),
            "math_density_mean": float(g["math_density"].mean()),
            "student_reasoning_rate_mean": float(g["student_reasoning_rate"].mean()),
            "autonomy_process_score_mean": float(g["autonomy_process_score"].mean()),
        })
    return pd.DataFrame(rows)


def _fisher(a: Sequence[int], b: Sequence[int]) -> Tuple[float, float]:
    a = pd.Series(a).dropna().astype(int)
    b = pd.Series(b).dropna().astype(int)
    table = [[int(a.sum()), int(len(a) - a.sum())], [int(b.sum()), int(len(b) - b.sum())]]
    odds, p = stats.fisher_exact(table)
    return float(odds), float(p)


def _welch(a: Sequence[float], b: Sequence[float]) -> Tuple[float, float]:
    a = pd.Series(a).dropna().astype(float)
    b = pd.Series(b).dropna().astype(float)
    if len(a) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return float(t), float(p)


def compare_systems(sessions: pd.DataFrame, a_system: str = "GPS-Agent", b_system: str = "Single-Agent") -> pd.DataFrame:
    a = sessions[sessions.system.eq(a_system)]
    b = sessions[sessions.system.eq(b_system)]
    rows: List[dict] = []
    for m in BINARY_METRICS:
        odds, p = _fisher(a[m], b[m]) if len(a) and len(b) else (float("nan"), float("nan"))
        a_mean, b_mean = float(a[m].mean()), float(b[m].mean())
        rows.append({
            "comparison": f"{a_system} vs {b_system}",
            "metric": m,
            "metric_type": "binary",
            "a_mean": a_mean,
            "b_mean": b_mean,
            "delta": a_mean - b_mean,
            "relative_delta_pct": ((a_mean - b_mean) / b_mean * 100.0) if b_mean else np.nan,
            "p_value": p,
            "effect_size": odds,
            "effect_size_name": "fisher_odds_ratio",
            "a_ci_low": bootstrap_ci(a[m], n_boot=2000)[0],
            "a_ci_high": bootstrap_ci(a[m], n_boot=2000)[1],
            "b_ci_low": bootstrap_ci(b[m], n_boot=2000)[0],
            "b_ci_high": bootstrap_ci(b[m], n_boot=2000)[1],
        })
    for m in CONTINUOUS_METRICS:
        t, p = _welch(a[m], b[m]) if len(a) and len(b) else (float("nan"), float("nan"))
        a_mean, b_mean = float(a[m].mean()), float(b[m].mean())
        rows.append({
            "comparison": f"{a_system} vs {b_system}",
            "metric": m,
            "metric_type": "continuous",
            "a_mean": a_mean,
            "b_mean": b_mean,
            "delta": a_mean - b_mean,
            "relative_delta_pct": ((a_mean - b_mean) / b_mean * 100.0) if b_mean else np.nan,
            "p_value": p,
            "effect_size": cohen_d(a[m], b[m]),
            "effect_size_name": "cohen_d",
            "a_ci_low": bootstrap_ci(a[m], n_boot=2000)[0],
            "a_ci_high": bootstrap_ci(a[m], n_boot=2000)[1],
            "b_ci_low": bootstrap_ci(b[m], n_boot=2000)[0],
            "b_ci_high": bootstrap_ci(b[m], n_boot=2000)[1],
        })
    return pd.DataFrame(rows)


def correlation_diagnostics(sessions: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("stall", "vai"),
        ("stall", "student_reasoning_rate"),
        ("direct_answer_leakage", "vai"),
        ("phase_validity", "autonomy_process_score"),
        ("tutor_student_token_ratio", "answer_dependency_index"),
    ]
    rows = []
    for system, g in sessions.groupby("system"):
        for x, y in pairs:
            xs = pd.to_numeric(g[x], errors="coerce")
            ys = pd.to_numeric(g[y], errors="coerce")
            ok = xs.notna() & ys.notna()
            if ok.sum() < 3 or xs[ok].nunique() < 2 or ys[ok].nunique() < 2:
                rho, p = np.nan, np.nan
            else:
                rho, p = stats.spearmanr(xs[ok], ys[ok])
            rows.append({"system": system, "x": x, "y": y, "spearman_rho": rho, "p_value": p, "n": int(ok.sum())})
    return pd.DataFrame(rows)


def audit_all(root: Path) -> Dict[str, object]:
    return {
        "human_pilot": human_pilot_summary(root / "data/processed/GPS_AIedu.csv"),
        "expanded": expanded_corpus_quality(root / "data/processed/gps_aiedu_gold_standard.csv"),
        "question_bank": question_bank_audit(root / "data/processed/probabilities_questions.json"),
        "irr": compute_irr_from_file(root / "data/outputs/irr_scores.csv"),
    }
