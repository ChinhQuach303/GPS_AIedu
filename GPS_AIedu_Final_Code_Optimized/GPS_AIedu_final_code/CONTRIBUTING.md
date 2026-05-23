# Contributing to GPS-AIedu

Thank you for your interest in contributing to the **GPS-AIedu / GPS-Agent** project! This repository contains the source code, data, evaluation pipelines, and LaTeX paper assets for our EMNLP system paper on process-controlled tutoring.

Here are the guidelines for contributing to this project.

---

## 1. Code of Conduct

Please be respectful, collaborative, and constructive in all communication and code reviews. Our goal is to maintain a high-quality codebase for reproducible educational research.

## 2. Development Setup

To set up the development environment:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd GPS_AIedu_final_code
   ```

2. **Create a virtual environment** and activate it:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify the installation** by running the tests:
   ```bash
   PYTHONPATH=. pytest
   ```

---

## 3. Code Standards & Style

We follow clean-code principles and Python best practices:

- **Style**: Adhere to [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
- **Type Hints**: Use type hints (`from __future__ import annotations` and standard type annotations) to ensure static analysis checks pass.
- **Docstrings**: Provide clear docstrings for all modules, classes, and public functions.
- **Socratic Tutoring Ethics**: Ensure that tutor prompts and routing models enforce the **Guide-Practice-Solve (GPS)** flow. Tutors should never leak direct answers or solve tasks on behalf of the student before the student completes the Guide and Practice phases.

---

## 4. Running the Pipelines

Any changes to metric calculation, parsing, or data ingestion must be validated by running the reproducibility pipelines.

### Run Tests
Make sure all regression and unit tests pass before submitting changes:
```bash
PYTHONPATH=. pytest -q
```

### Run Full Metrics Pipeline
To regenerate all tables, figures, manifest files, and compile local LaTeX assets:
```bash
PYTHONPATH=. python scripts/run_full_metrics_emnlp_pipeline.py
```

### Run Question Bank Audit
If you modify probabilities or question configurations:
```bash
PYTHONPATH=. python scripts/audit_question_bank.py
```

### Run Paper Consistency Audit
Check that the LaTeX paper source doesn't contain stale claims or formatting errors:
```bash
PYTHONPATH=. python scripts/final_paper_audit.py
```

---

## 5. Branching & Pull Requests

1. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Commit your changes** with clear and descriptive messages.
3. **Keep commits clean** and make sure you do not commit raw log cache files or temporary `.zip` files. (Verify your changes against `.gitignore`).
4. **Push to your fork** and submit a **Pull Request (PR)**.
5. In your PR description, explain:
   - What change was made.
   - Why the change is necessary.
   - How you verified the change (e.g., test output, pipeline run).

---

## 6. Contact & Citation

For questions regarding EMNLP paper compilation, Overleaf setup, or evaluation logic, please refer to [README.md](README.md) or open an issue in the repository.
