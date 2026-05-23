#!/usr/bin/env python3
"""Run the optimized reproducible asset pipeline.

This script intentionally does not run new LLM simulations. It regenerates all
metric tables, figures, audits, and the Overleaf/LaTeX project from existing CSV
logs so the paper numbers are reproducible and fast to verify.
"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import time

import pandas as pd

from src.evaluation.pipeline.dataset_registry import CONTROLLED_DATASETS, SUPPORT_DATASETS, manifest_rows
from scripts.generate_conference_assets import main as generate_conference_assets

ROOT = Path.cwd()
REPORT_DIR = ROOT / "reports" / "evaluation"
MANIFEST_DIR = ROOT / "reports" / "evaluation" / "tables"


def run_step(name: str, fn) -> None:
    started = time.time()
    print(f"[pipeline] {name} ...", flush=True)
    fn()
    print(f"[pipeline] {name} done in {time.time() - started:.2f}s", flush=True)


def write_manifest() -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    rows = manifest_rows([*CONTROLLED_DATASETS.values(), *SUPPORT_DATASETS.values()])
    pd.DataFrame(rows).to_csv(MANIFEST_DIR / "dataset_manifest.csv", index=False)
    (REPORT_DIR / "dataset_manifest.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def build_latex() -> None:
    subprocess.run([sys.executable, "scripts/build_latex_project.py"], check=True)


def main() -> None:
    run_step("write dataset manifest", write_manifest)
    run_step("regenerate evaluation assets", generate_conference_assets)
    run_step("build LaTeX project", build_latex)
    print("[pipeline] optimized pipeline completed")


if __name__ == "__main__":
    main()
