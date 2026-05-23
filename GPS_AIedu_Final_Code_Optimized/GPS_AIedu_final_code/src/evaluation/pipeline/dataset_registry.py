"""Dataset registry for reproducible GPS-Agent evaluation.

The project contains several generations of CSV artifacts. This registry keeps
paper-facing scripts from silently mixing human/pilot data, controlled
simulation, cross-model stress tests, and exploratory augmented corpora.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable

import pandas as pd


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    path: Path
    layer: str
    role: str
    required_columns: tuple[str, ...]


CONTROLLED_DATASETS: Dict[str, DatasetSpec] = {
    "gps": DatasetSpec(
        name="GPS-Agent",
        path=Path("data/outputs/cleaned_massive_results.csv"),
        layer="controlled_simulation",
        role="experimental multi-agent tutoring condition",
        required_columns=("session_id", "question", "level", "trace", "dialogue"),
    ),
    "baseline": DatasetSpec(
        name="Single-Agent",
        path=Path("data/outputs/cleaned_baseline_results.csv"),
        layer="controlled_simulation",
        role="single-agent baseline condition",
        required_columns=("session_id", "question", "level", "trace", "dialogue"),
    ),
    "cross_model": DatasetSpec(
        name="Cross-Model Phi-3",
        path=Path("data/outputs/cross_model_conversations.csv"),
        layer="cross_model_stress_test",
        role="independent student-simulator stress test",
        required_columns=("session_id", "question", "level", "trace", "dialogue"),
    ),
}

SUPPORT_DATASETS: Dict[str, DatasetSpec] = {
    "human_pilot": DatasetSpec(
        name="Human Pilot Turn Log",
        path=Path("data/processed/GPS_AIedu.csv"),
        layer="human_pilot",
        role="5-student x 45-question GPS calibration/human pilot layer",
        required_columns=("Student ID", "Question", "AI Response", "GPS Step (Truth)", "Group"),
    ),
    "expanded": DatasetSpec(
        name="Expanded Behavioral Corpus",
        path=Path("data/processed/gps_aiedu_gold_standard.csv"),
        layer="exploratory_augmented_corpus",
        role="large augmented corpus; not treated as human gold standard until audited",
        required_columns=("Student_ID", "QID", "Level", "Group", "Dialogue"),
    ),
}


def load_dataset(spec: DatasetSpec) -> pd.DataFrame:
    if not spec.path.exists():
        raise FileNotFoundError(f"Missing dataset {spec.name}: {spec.path}")
    df = pd.read_csv(spec.path)
    missing = [col for col in spec.required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset {spec.name} missing required columns: {missing}")
    return df


def load_controlled_frames() -> dict[str, pd.DataFrame]:
    return {spec.name: load_dataset(spec) for spec in CONTROLLED_DATASETS.values()}


def manifest_rows(specs: Iterable[DatasetSpec] | None = None) -> list[dict[str, object]]:
    specs = list(specs or [*CONTROLLED_DATASETS.values(), *SUPPORT_DATASETS.values()])
    rows = []
    for spec in specs:
        row = {
            "name": spec.name,
            "path": str(spec.path),
            "layer": spec.layer,
            "role": spec.role,
            "exists": spec.path.exists(),
            "required_columns": ";".join(spec.required_columns),
        }
        if spec.path.exists():
            try:
                df = pd.read_csv(spec.path, nrows=0)
                row["columns"] = ";".join(df.columns)
            except Exception as exc:  # pragma: no cover
                row["columns"] = f"ERROR: {exc}"
        rows.append(row)
    return rows
