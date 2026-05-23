"""
pedagogy_metrics.py
===================
Deterministic, paper-reproducible metrics for GPS-Agent tutoring logs.

This module intentionally avoids LLM calls. It is optimized for the current
project data layout: each dialogue is parsed once, metrics are derived from the
same normalized turn representation, and all paper claims can be regenerated
from CSV logs without hidden constants.

Metric policy
-------------
1. Human/pilot, controlled simulation, cross-model, and expanded corpora are
   separate data layers.
2. Direct-answer leakage and phase validity are primary pedagogical-control
   metrics.
3. VAI and math density are secondary engagement metrics; they are not treated
   as learning-gain evidence unless supported by a validated pre/post design.
4. IRR is recomputed from observed rater columns when present. No kappa value is
   hard-coded.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import json
import math
import re

import numpy as np
import pandas as pd
from scipy import stats

try:  # sklearn is optional; only needed for IRR.
    from sklearn.metrics import cohen_kappa_score
except Exception:  # pragma: no cover
    cohen_kappa_score = None

# ---------------------------------------------------------------------------
# Regexes and controlled vocabularies
# ---------------------------------------------------------------------------
ROLE_RE = re.compile(
    r"(?m)^(Thầy|Thay|Em|AI|Student|Teacher|Tutor|Assistant|User|Học sinh|Hoc sinh|Gia sư|Giao vien|Giáo viên)\s*[:：]\s*"
)
MATH_RE = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)|\$([^$]+)\$", re.DOTALL)
FRACTION_OR_FORMULA_RE = re.compile(
    r"\\frac\s*\{|\d+\s*/\s*\d+|\d+\s*\^\s*\d+|\\binom|C_?\s*\{|P\s*\(|\\boxed",
    re.I,
)

TUTOR_ALIASES = {
    "thầy", "thay", "teacher", "tutor", "ai", "assistant", "gia sư", "giao vien", "giáo viên"
}
STUDENT_ALIASES = {"em", "học sinh", "hoc sinh", "student", "learner", "user"}

DIRECT_PATTERNS = [
    r"đáp\s*án\s*(là|:)",
    r"dap\s*an\s*(la|:)",
    r"kết\s*quả\s*(là|:)",
    r"ket\s*qua\s*(la|:)",
    r"vậy\s*(xác\s*suất|kết\s*quả)\s*(là|=)",
    r"vay\s*(xac\s*suat|ket\s*qua)\s*(la|=)",
    r"chúc\s*mừng\s*em.*(đúng|chính\s*xác)",
    r"loi\s*giai|lời\s*giải",
    r"ta\s*có\s*:\s*",
    r"do\s*đó\s*.*=",
    r"\\boxed\s*\{",
]
DIRECT_RE = re.compile("|".join(DIRECT_PATTERNS), re.I | re.S)
REFLECTION_RE = re.compile(
    r"giải\s*thích\s*lại|giai\s*thich\s*lai|vì\s*sao|vi\s*sao|lý\s*do|ly\s*do|"
    r"rút\s*ra|rut\s*ra|em\s*hiểu|em\s*hieu|tự\s*tóm\s*tắt|tu\s*tom\s*tat|reflection|phản\s*tư|phan\s*tu",
    re.I,
)
REASONING_RE = re.compile(
    r"vì|vi|do đó|do do|nên|nen|suy ra|em nghĩ|em nghi|ta có|ta co|bước|buoc|"
    r"không gian mẫu|khong gian mau|xác suất|xac suat|tổ hợp|to hop|chỉnh hợp|chinh hop|quy tắc|quy tac",
    re.I,
)
NON_VIETNAMESE_RE = re.compile(r"[\u4e00-\u9fff]")

LEVEL_MAP = {
    "Yêu": "Yếu",
    "yeu": "Yếu",
    "Weak": "Yếu",
    "Disengaged": "Mất tập trung",
    "Excellent": "Giỏi",
    "Good": "Khá",
    "Average": "Trung bình",
}


@dataclass(frozen=True)
class Turn:
    speaker: str
    text: str
    math_count: int
    has_direct_answer: bool
    has_reasoning: bool


@dataclass(frozen=True)
class DialogueMetrics:
    n_turns: int
    tutor_turns: int
    student_turns: int
    student_math: int
    tutor_math: int
    student_reasoning_turns: int
    vai: float
    math_density: float
    direct_answer_leakage: int
    reflection_required: int
    reflection_completed: int
    non_vietnamese_leakage: int


@dataclass(frozen=True)
class SystemSummary:
    system: str
    n_sessions: int
    n_questions: Optional[int]
    n_levels: Optional[int]
    vai_mean: float
    vai_sd: float
    math_density_mean: float
    student_reasoning_turns_mean: float
    direct_answer_leakage_rate: float
    stall_rate: float
    phase_validity_rate: float
    reflection_completion_rate: Optional[float]
    non_vietnamese_leakage_rate: float


@dataclass(frozen=True)
class StatisticalTest:
    comparison: str
    metric: str
    a_mean: float
    b_mean: float
    delta: float
    relative_delta_pct: Optional[float]
    welch_t: Optional[float]
    p_value: Optional[float]
    cohen_d: Optional[float]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
def normalize_level(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip()
    return LEVEL_MAP.get(text, text)


def normalize_speaker(speaker: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(speaker).strip().lower()).rstrip(":：")
    if cleaned in TUTOR_ALIASES:
        return "Tutor"
    if cleaned in STUDENT_ALIASES:
        return "Student"
    return str(speaker).strip().title() or "Unknown"


@lru_cache(maxsize=50000)
def math_count(text: str) -> int:
    """Count explicit mathematical expressions with a cheap deterministic heuristic."""
    if not isinstance(text, str) or not text:
        return 0
    latex_count = len([m for m in MATH_RE.findall(text) if any(m)])
    formula_count = len(FRACTION_OR_FORMULA_RE.findall(text))
    return max(latex_count, formula_count)


@lru_cache(maxsize=50000)
def parse_turns_cached(dialogue: str) -> Tuple[Turn, ...]:
    if not isinstance(dialogue, str) or not dialogue.strip():
        return tuple()
    parts = re.split(ROLE_RE, dialogue)
    turns: List[Turn] = []
    for i in range(1, len(parts) - 1, 2):
        speaker = normalize_speaker(parts[i])
        text = parts[i + 1].strip()
        if not text:
            continue
        turns.append(
            Turn(
                speaker=speaker,
                text=text,
                math_count=math_count(text),
                has_direct_answer=bool(DIRECT_RE.search(text)),
                has_reasoning=bool(REASONING_RE.search(text)) or math_count(text) > 0,
            )
        )
    return tuple(turns)


def split_turns(dialogue: str) -> List[Tuple[str, str]]:
    """Return [(speaker, utterance)] from mixed Vietnamese/English dialogue labels."""
    return [(turn.speaker, turn.text) for turn in parse_turns_cached(dialogue or "")]


def parse_trace(trace: object) -> List[str]:
    if not isinstance(trace, str):
        return []
    trace = trace.strip()
    if not trace or trace.upper() == "SINGLE_AGENT":
        return []
    out: List[str] = []
    for token in re.split(r"[-,>\s]+", trace):
        token = token.strip().upper()
        if not token:
            continue
        if token.startswith("G"):
            out.append("G")
        elif token.startswith("P"):
            out.append("P")
        elif token.startswith("S"):
            out.append("S")
    return out


def parse_phase_labels_from_text(dialogue: str) -> List[str]:
    if not isinstance(dialogue, str):
        return []
    return [m.group(1).upper() for m in re.finditer(r"\[(G|P|S)\]", dialogue, flags=re.I)]


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def student_tutor_math_counts(dialogue: str) -> Tuple[int, int]:
    student = 0
    tutor = 0
    for turn in parse_turns_cached(dialogue or ""):
        if turn.speaker == "Student":
            student += turn.math_count
        elif turn.speaker == "Tutor":
            tutor += turn.math_count
    return student, tutor


def vai(dialogue: str) -> float:
    student, tutor = student_tutor_math_counts(dialogue)
    total = student + tutor
    return float(student / total) if total else 0.0


def math_density(dialogue: str) -> float:
    turns = [t for t in parse_turns_cached(dialogue or "") if t.speaker == "Student"]
    if not turns:
        return 0.0
    return float(sum(t.math_count for t in turns) / len(turns))


def direct_answer_leakage(dialogue: str, trace: object = "") -> int:
    """Detect premature answer-giving.

    A session is flagged when the tutor gives answer-like or computation-heavy
    content in the first three tutor turns before a valid Solve state is reached.
    This preserves the core Answer-Giving Trap signal without penalizing normal
    Solve-phase confirmation.
    """
    # Focus on complete Solve-bypass behavior. If a session eventually enters a
    # Solve state, invalid shortcuts are captured by `phase_validity`; leakage
    # remains reserved for single-agent or no-Solve answer dumping.
    phases = parse_trace(trace)
    trace_has_solve = "S" in phases
    tutor_idx = 0
    for turn in parse_turns_cached(dialogue or ""):
        if turn.speaker != "Tutor":
            continue
        tutor_idx += 1
        early = tutor_idx <= 3
        has_solve_marker = bool(re.search(r"\[S\]", turn.text, flags=re.I))
        computation_heavy = turn.math_count >= 2
        if early and not trace_has_solve and not has_solve_marker and (turn.has_direct_answer or computation_heavy):
            return 1
    return 0


def reflection_required_completed(dialogue: str, trace: object = "") -> Tuple[int, int]:
    phases = parse_trace(trace) or parse_phase_labels_from_text(dialogue or "")
    required = int("S" in phases)
    completed = int(required and bool(REFLECTION_RE.search(dialogue or "")))
    return required, completed


def stall(trace: object, threshold: int = 4) -> int:
    phases = parse_trace(trace)
    if not phases:
        return 0
    run = 1
    last = phases[0]
    for phase in phases[1:]:
        if phase == last:
            run += 1
            if run >= threshold:
                return 1
        else:
            last = phase
            run = 1
    return 0


def phase_validity(trace: object, dialogue: str = "") -> int:
    phases = parse_trace(trace) or parse_phase_labels_from_text(dialogue or "")
    if not phases:
        return 0
    if "S" in phases:
        s_idx = phases.index("S")
        return int("G" in phases[:s_idx] and "P" in phases[:s_idx])
    return int(phases[0] == "G")


def non_vietnamese_leakage(dialogue: str) -> int:
    return int(bool(NON_VIETNAMESE_RE.search(dialogue or "")))


def analyze_dialogue(dialogue: str, trace: object = "") -> DialogueMetrics:
    turns = parse_turns_cached(dialogue or "")
    tutor_turns = [t for t in turns if t.speaker == "Tutor"]
    student_turns = [t for t in turns if t.speaker == "Student"]
    student_math = sum(t.math_count for t in student_turns)
    tutor_math = sum(t.math_count for t in tutor_turns)
    total_math = student_math + tutor_math
    required, completed = reflection_required_completed(dialogue, trace)
    return DialogueMetrics(
        n_turns=len(turns),
        tutor_turns=len(tutor_turns),
        student_turns=len(student_turns),
        student_math=student_math,
        tutor_math=tutor_math,
        student_reasoning_turns=sum(int(t.has_reasoning) for t in student_turns),
        vai=float(student_math / total_math) if total_math else 0.0,
        math_density=float(student_math / len(student_turns)) if student_turns else 0.0,
        direct_answer_leakage=direct_answer_leakage(dialogue, trace),
        reflection_required=required,
        reflection_completed=completed,
        non_vietnamese_leakage=non_vietnamese_leakage(dialogue),
    )


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if "dialogue" not in d.columns and "Dialogue" in d.columns:
        d["dialogue"] = d["Dialogue"]
    if "level" not in d.columns and "Level" in d.columns:
        d["level"] = d["Level"]
    if "trace" not in d.columns and "Trace" in d.columns:
        d["trace"] = d["Trace"]
    if "trace" not in d.columns:
        d["trace"] = ""
    if "level" in d.columns:
        d["level"] = d["level"].apply(normalize_level)
    if "dialogue" not in d.columns:
        d["dialogue"] = ""

    metric_dicts = [asdict(analyze_dialogue(str(row.dialogue), getattr(row, "trace", ""))) for row in d.itertuples(index=False)]
    metrics = pd.DataFrame(metric_dicts, index=d.index)
    for col in metrics.columns:
        d[col] = metrics[col]
    d["stall"] = d["trace"].apply(stall)
    d["phase_validity"] = d.apply(lambda r: phase_validity(r.get("trace", ""), r.get("dialogue", "")), axis=1)
    return d


def summarize_dataframe(df: pd.DataFrame, system_name: str) -> Tuple[Dict[str, float], pd.DataFrame]:
    d = enrich_dataframe(df)
    refl_required = float(d["reflection_required"].sum()) if len(d) else 0.0
    summary = SystemSummary(
        system=system_name,
        n_sessions=int(len(d)),
        n_questions=int(d["question"].nunique()) if "question" in d.columns else (int(d["QID"].nunique()) if "QID" in d.columns else None),
        n_levels=int(d["level"].nunique()) if "level" in d.columns else None,
        vai_mean=float(d["vai"].mean()) if len(d) else 0.0,
        vai_sd=float(d["vai"].std(ddof=1)) if len(d) > 1 else 0.0,
        math_density_mean=float(d["math_density"].mean()) if len(d) else 0.0,
        student_reasoning_turns_mean=float(d["student_reasoning_turns"].mean()) if len(d) else 0.0,
        direct_answer_leakage_rate=float(d["direct_answer_leakage"].mean()) if len(d) else 0.0,
        stall_rate=float(d["stall"].mean()) if len(d) else 0.0,
        phase_validity_rate=float(d["phase_validity"].mean()) if len(d) else 0.0,
        reflection_completion_rate=float(d["reflection_completed"].sum() / refl_required) if refl_required else None,
        non_vietnamese_leakage_rate=float(d["non_vietnamese_leakage"].mean()) if len(d) else 0.0,
    )
    return asdict(summary), d


# ---------------------------------------------------------------------------
# Statistics and data audits
# ---------------------------------------------------------------------------
def cohen_d(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    a = np.asarray(pd.Series(a).dropna(), dtype=float)
    b = np.asarray(pd.Series(b).dropna(), dtype=float)
    if len(a) < 2 or len(b) < 2:
        return None
    denom = len(a) + len(b) - 2
    pooled = math.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / denom)
    if pooled == 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled)


def bootstrap_ci(values: Sequence[float], n_boot: int = 5000, seed: int = 13, alpha: float = 0.05) -> Tuple[float, float]:
    s = pd.Series(values).dropna().astype(float).to_numpy()
    if len(s) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    samples = rng.choice(s, size=(n_boot, len(s)), replace=True).mean(axis=1)
    return (float(np.quantile(samples, alpha / 2)), float(np.quantile(samples, 1 - alpha / 2)))


def welch_test(a: Sequence[float], b: Sequence[float], comparison: str, metric: str) -> Dict[str, Optional[float]]:
    a = pd.Series(a).dropna().astype(float)
    b = pd.Series(b).dropna().astype(float)
    if len(a) < 2 or len(b) < 2:
        return asdict(StatisticalTest(comparison, metric, float(a.mean()), float(b.mean()), float(a.mean() - b.mean()), None, None, None, None))
    t_stat, p_value = stats.ttest_ind(a, b, equal_var=False)
    b_mean = float(b.mean())
    ci_lo, ci_hi = bootstrap_ci(a)
    return {
        **asdict(
            StatisticalTest(
                comparison=comparison,
                metric=metric,
                a_mean=float(a.mean()),
                b_mean=b_mean,
                delta=float(a.mean() - b.mean()),
                relative_delta_pct=float((a.mean() - b.mean()) / b_mean * 100) if b_mean else None,
                welch_t=float(t_stat),
                p_value=float(p_value),
                cohen_d=cohen_d(a, b),
            )
        ),
        "a_bootstrap_ci_low": ci_lo,
        "a_bootstrap_ci_high": ci_hi,
    }


def binary_fisher_test(a: Sequence[int], b: Sequence[int], comparison: str, metric: str) -> Dict[str, Optional[float]]:
    a = pd.Series(a).dropna().astype(int)
    b = pd.Series(b).dropna().astype(int)
    table = np.array([[int(a.sum()), int(len(a) - a.sum())], [int(b.sum()), int(len(b) - b.sum())]])
    odds_ratio, p_value = stats.fisher_exact(table)
    b_mean = float(b.mean()) if len(b) else 0.0
    a_ci_lo, a_ci_hi = bootstrap_ci(a)
    return {
        "comparison": comparison,
        "metric": metric,
        "a_mean": float(a.mean()) if len(a) else 0.0,
        "b_mean": b_mean,
        "delta": float(a.mean() - b.mean()) if len(a) and len(b) else 0.0,
        "relative_delta_pct": float((a.mean() - b.mean()) / b_mean * 100) if b_mean else None,
        "fisher_odds_ratio": float(odds_ratio),
        "p_value": float(p_value),
        "a_bootstrap_ci_low": a_ci_lo,
        "a_bootstrap_ci_high": a_ci_hi,
    }


def compute_irr_from_file(path: str | Path) -> Dict[str, object]:
    path = Path(path)
    if not path.exists():
        return {"available": False, "reason": f"Missing file: {path}"}
    df = pd.read_csv(path)
    required = ["score_rater_A_qwen", "score_rater_B_phi3"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        return {"available": False, "reason": f"Missing columns: {missing}"}
    a = pd.to_numeric(df[required[0]], errors="coerce")
    b = pd.to_numeric(df[required[1]], errors="coerce")
    valid = a.notna() & b.notna()
    if valid.sum() < 2:
        return {"available": False, "reason": "Not enough paired rater scores"}
    if cohen_kappa_score is None:
        return {"available": False, "reason": "sklearn is not installed"}
    a = a[valid].astype(int)
    b = b[valid].astype(int)
    return {
        "available": True,
        "n": int(valid.sum()),
        "rater_a_mean": float(a.mean()),
        "rater_b_mean": float(b.mean()),
        "quadratic_weighted_kappa": float(cohen_kappa_score(a, b, weights="quadratic")),
        "unweighted_kappa": float(cohen_kappa_score(a, b)),
    }


def question_bank_audit(path: str | Path) -> Dict[str, object]:
    path = Path(path)
    if not path.exists():
        return {"available": False, "reason": f"Missing file: {path}"}
    items = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in items:
        options = item.get("options") or []
        answer = item.get("answer")
        blank_options = sum(1 for opt in options if re.fullmatch(r"[A-D]\.?:?\s*\.??", str(opt).strip()))
        has_answer = bool(str(answer).strip()) and str(answer).strip().lower() not in {"nan", "none", "null"}
        rows.append(
            {
                "id": item.get("id"),
                "has_question": bool(str(item.get("question", "")).strip()),
                "has_answer": has_answer,
                "n_options": len(options),
                "blank_options": blank_options,
                "validated_for_correctness": bool(has_answer and blank_options == 0),
            }
        )
    audit = pd.DataFrame(rows)
    return {
        "available": True,
        "n_questions": int(len(audit)),
        "missing_answer": int((~audit["has_answer"]).sum()),
        "questions_with_blank_options": int((audit["blank_options"] > 0).sum()),
        "validated_for_correctness": int(audit["validated_for_correctness"].sum()),
        "audit_table": rows,
    }


def human_pilot_summary(path: str | Path) -> Dict[str, object]:
    path = Path(path)
    if not path.exists():
        return {"available": False, "reason": f"Missing file: {path}"}
    df = pd.read_csv(path)
    if "Notes" in df.columns:
        df["QID"] = df["Notes"].astype(str).str.extract(r"Q_ID:\s*(\d+)")
        df["Session"] = df["Notes"].astype(str).str.extract(r"Session:\s*([^\s]+)")
    human_pilot = df[df.get("Group", "").eq("Foundation (Real)")].copy() if "Group" in df.columns else df.iloc[0:0]
    expanded = df[df.get("Group", "").eq("Experimental (Expanded)")].copy() if "Group" in df.columns else df.iloc[0:0]
    phase_counts = human_pilot.get("GPS Step (Truth)", pd.Series(dtype=str)).value_counts().to_dict()
    return {
        "available": True,
        "total_rows": int(len(df)),
        "human_pilot_turns": int(len(human_pilot)),
        "expanded_turns": int(len(expanded)),
        "students": int(human_pilot["Student ID"].nunique()) if "Student ID" in human_pilot.columns else None,
        "questions": int(human_pilot["QID"].nunique()) if "QID" in human_pilot.columns else None,
        "sessions": int(human_pilot["Session"].nunique()) if "Session" in human_pilot.columns else None,
        "phase_counts": {k: int(v) for k, v in phase_counts.items()},
        "mean_satisfaction": float(human_pilot["Satisfaction (1-5)"].mean()) if "Satisfaction (1-5)" in human_pilot.columns and len(human_pilot) else None,
        "mean_difficulty": float(human_pilot["Difficulty (1-5)"].mean()) if "Difficulty (1-5)" in human_pilot.columns and len(human_pilot) else None,
    }


def expanded_corpus_quality(path: str | Path) -> Dict[str, object]:
    path = Path(path)
    if not path.exists():
        return {"available": False, "reason": f"Missing file: {path}"}
    df = pd.read_csv(path)
    result = {"available": True, "rows": int(len(df)), "columns": list(df.columns)}
    if "Group" in df.columns:
        result["groups"] = {str(k): int(v) for k, v in df["Group"].value_counts().items()}
    if "Independence_Index" in df.columns:
        ii = pd.to_numeric(df["Independence_Index"], errors="coerce")
        result["independence_index_gt_1"] = int((ii > 1).sum())
        result["independence_index_mean"] = float(ii.mean())
    if "GPS_Fidelity" in df.columns:
        gf = pd.to_numeric(df["GPS_Fidelity"], errors="coerce")
        result["gps_fidelity_mean"] = float(gf.mean())
    return result
