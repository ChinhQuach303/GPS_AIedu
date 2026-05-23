# GPS-Agent: A State-Graph Tutoring Framework for Process Control in Vietnamese Mathematics Dialogue

This repository contains the finalized source code, data processing pipelines, evaluation metrics, regression tests, and paper-compilation packages for **GPS-Agent**—a state-graph framework designed to enforce a structured **Guide–Practice–Solve (GPS)** Socratic tutoring protocol.

---

## 1. Project Overview

### The Socratic Tutoring Control Problem
Large Language Models (LLMs) excel at solving math problems, but when deployed as conversational tutors, they frequently fall into the **Answer-Giving Trap**: providing the final numerical answer or a fully worked step-by-step solution before the student has had an opportunity to reason through the problem. This bypasses the student's own cognitive struggle.

GPS-Agent addresses this failure mode by treating pedagogical control as an **architectural routing problem** rather than purely a prompting problem. 

### State-Graph Architecture
The system models Socratic tutoring as a state graph orchestrated by a stateful **Supervisor** routing between three specialized agent nodes:
1. **Guide (G)**: Elicits the student's conceptual interpretation, prior knowledge, and problem understanding without disclosing numerical solutions or calculations.
2. **Practice (P)**: Decomposes the mathematical problem into one sequential reasoning or calculation step at a time, checking intermediate student responses.
3. **Solve (S)**: Verifies the final student calculations, chokes answer disclosure, and prompts self-reflection/metacognition only after conceptual and calculation evidence has been established.

```
       [ Student Input ]
               │
               ▼
       ┌───────────────┐
       │  Supervisor   │◄───────┐
       └───────┬───────┘        │
               │                │ Stored State &
       ┌───────┼───────┐        │ Trajectory Trace
       ▼       ▼       ▼        │
    [Guide] [Practice] [Solve]  │
       │       │       │        │
       └───────┴───────┴────────┘
```

The Supervisor logs a persistent trajectory trace (e.g. `G-P-S`) in the session state. By evaluating this trace, we can verify whether the tutor complies with Socratic constraints (e.g., verifying that `Solve` was only reached after conceptual `Guide` and intermediate `Practice` steps).

---

## 2. Core Terminology & Metrics

The metrics and data layers are mapped to match the terms evaluated in our paper:

### Evaluation Metrics
* **`direct_answer_leakage`** (`direct_answer_leakage_rate`): The primary Answer-Giving Trap failure metric. Measures whether the tutor exposes numerical answers, formulas, or final worked steps before a valid `Solve` state.
* **`phase_validity`** (`phase_validity_rate`): Verifies whether the interaction follows Socratic sequencing (e.g., conceptual guidance and practice steps occur prior to final solution validation).
* **`gps_completion`** (`gps_completion_rate`): A strict completion metric requiring that the dialogue trajectory successfully logs at least one transition into each of the three phases: Guide, Practice, and Solve.
* **`stall`** (`stall_rate`): Scaffolding pressure indicator; flags cases where a student gets stuck in more than 3 consecutive identical states (e.g., repeating Practice four times).
* **`vai`** (Verifiable Autonomy Index): The proportion of mathematical tokens/expressions contributed by the student versus the tutor:
  $$\mathrm{VAI} = \frac{M_{\mathrm{student}}}{M_{\mathrm{student}} + M_{\mathrm{tutor}}}$$

### Dataset Layers
* **`human_pilot`**: Real feasibility data collected from **5 human students** across **45 questions**, yielding **225 sessions** and **810 annotated turns**.
* **`controlled_comparison`**: A matched dataset of **100 GPS-Agent** sessions and **100 single-agent baseline** sessions generated using simulated student personas.
* **`cross_model_stress_test`**: Robustness test involving **49 sessions** where a Phi-3-mini model acts as the student simulator.
* **`expanded_exploratory_corpus`**: An expanded augmented corpus containing **2824 session rows**, reserved for diagnostic audits.

---

## 3. Experimental Results

All paper-facing results are deterministically computed from raw dialogue logs using the repository's evaluation scripts.

### Controlled and Stress-Test Process-Control Metrics
The following table summarizes the system performance across our controlled comparisons and stress tests:

| System | $N$ | Questions | Leakage (%) | Phase-Valid (%) | GPS Comp. (%) | Solve (%) | Stall (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GPS-Agent** | 100 | 25 | 9.0% | 75.0% | 62.0% | 87.0% | 41.0% |
| **Single-Agent (Baseline)** | 100 | 25 | 54.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| **Cross-Model (Phi-3)** | 49 | 25 | 42.9% | 100.0% | 8.2% | 8.2% | 79.6% |

**Key Findings**:
1. **Pedagogical Control**: GPS-Agent reduces direct-answer leakage from **54.0% to 9.0%** (Fisher exact $p = 3.83 \times 10^{-12}$) and increases phase validity from **0.0% to 75.0%** ($p = 2.87 \times 10^{-33}$).
2. **Scaffolding Pressure (Stall)**: While the baseline has a 0.0% stall rate (because it gives answers away immediately), GPS-Agent records a **41.0% stall rate**, showing a clear usability risk where students get stuck in scaffolding loops.
3. **Robustness**: Under the Phi-3 student simulator, phase validity remains at 100.0%, but completion drops to 8.2% and stall rises to 79.6%, highlighting high model-sensitivity.

---

## 4. Repository Layout

```text
├── src/
│   ├── agents/             # Tutor nodes & student-simulator templates
│   ├── evaluation/         # Metric implementations and question bank recovery
│   ├── utils/              # Model factory, logging, and I/O utilities
│   └── tools/              # GAS logging and dashboard setup scripts
├── scripts/
│   ├── run_full_metrics_pipeline.py   # Computes full metrics and compiles full statistics
│   ├── run_final_revision.py          # Regenerates revision assets and separates pilot layer
│   ├── run_optimized_pipeline.py      # Quick manifest write and Overleaf ZIP packager
│   ├── audit_question_bank.py         # Recovers answer keys and checks options typography
│   ├── final_paper_audit.py           # Runs final check on LaTeX text validity
│   ├── calculate_irr.py               # Computes rater reliability diagnostics (diagnostic only)
│   └── clean_data_pipeline.py         # Standardizes and cleans raw dialogue logs
├── tests/
│   └── Regression tests for metric/parser/question-bank logic
├── data/
│   ├── raw/                # Source examinations and solution keys
│   ├── processed/          # Cleaned dialogue logs and probabilities questions
│   └── outputs/            # Simulation outputs and research stats
├── reports/
│   ├── full_metrics/       # Statistical summary tables and evaluation figures
│   ├── final_revision/     # Tables and figures for final paper revision
│   └── evaluation/         # manifest files and generated evaluation report
├── paper/
│   ├── final/              # Primary LaTeX paper files
│   ├── final_revision/     # LaTeX files matching the revised paper draft
│   ├── full_metrics/       # LaTeX source files for the full metrics set
│   └── overleaf/           # Directory zipped for Overleaf package compilation
├── webchat/
│   └── nextjs/             # Web interface for teacher/student live tutoring logs
├── LICENSE                 # MIT License details
├── CONTRIBUTING.md         # Developer code style guidelines
├── pyproject.toml          # Project environment properties
└── requirements.txt        # Python dependency manifest
```

---

## 5. Setup & Running Instructions

### 1. Python Environment Setup
Activate a virtual environment and install the required dependencies:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Quality Gates (Unit Tests)
Verify the core metric engines, math verifiers, and regex parsing pipelines:
```bash
$env:PYTHONPATH="."; python -m pytest -v
```

### 3. Run Reproducible Pipelines
Every reported table and figure is regenerated from local logs using these pipelines:

* **Run Optimized Pipeline** (Fast regeneration of paper assets and zipping):
  ```bash
  $env:PYTHONPATH="."; python scripts/run_optimized_pipeline.py
  ```
  *Output*: Generates the Overleaf package `GPS_Agent_Overleaf.zip` under the root directory.

* **Run Full Metrics Pipeline** (Calculates Welch and Fisher exact tests for all secondary metrics):
  ```bash
  $env:PYTHONPATH="."; python scripts/run_full_metrics_pipeline.py
  ```
  *Output*: Generates the full tables, charts under `reports/full_metrics/` and packages `GPS_AIedu_Full_Metrics_Package.zip`.

* **Run Final Revision Pipeline** (Builds the final paper revision separating human pilot data):
  ```bash
  $env:PYTHONPATH="."; python scripts/run_final_revision.py
  ```
  *Output*: Generates reports in `reports/final_revision/` and builds the revised zip `GPS_Agent_Final_Revision_Overleaf.zip`.

### 4. Run Audits & Diagnostics
* **Audit Question Bank**:
  ```bash
  $env:PYTHONPATH="."; python scripts/audit_question_bank.py
  ```
* **Audit TeX Source File**:
  ```bash
  $env:PYTHONPATH="."; python scripts/final_paper_audit.py
  ```

---

## 6. Overleaf / LaTeX Paper Submission
To compile the LaTeX source and prepare your submission:
1. Locate the generated Overleaf ZIP (e.g. `GPS_Agent_Final_Revision_Overleaf.zip`).
2. Upload it directly to Overleaf.
3. Set the compiler to **pdfLaTeX** and compile using `main.tex`.
4. *Important note*: The output package includes a local fallback `acl.sty` and `acl_natbib.bst` to compile immediately. Before submitting to a conference portal, make sure to replace these files with the official ACL style sheets provided by the conference venue.
