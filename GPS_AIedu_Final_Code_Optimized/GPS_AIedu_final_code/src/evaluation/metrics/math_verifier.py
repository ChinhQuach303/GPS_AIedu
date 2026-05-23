"""Backward-compatible math/VAI verifier.

The original verifier only recognized ``Thầy:`` and ``Em:``. Project logs now
contain several speaker conventions (AI/Student, Teacher/User, etc.), so this
wrapper delegates speaker parsing to ``pedagogy_metrics`` while preserving the
old ``MathVerifier.calculate_vai`` API used by existing scripts.
"""
from __future__ import annotations

import re
from typing import Dict, List

try:
    from sympy.parsing.latex import parse_latex
except Exception:  # pragma: no cover
    parse_latex = None

from src.evaluation.metrics.pedagogy_metrics import math_count, split_turns


class MathVerifier:
    def __init__(self):
        self.latex_pattern = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)|\$([^$]+)\$", re.DOTALL)

    def _clean_latex(self, latex_str: str) -> str:
        if not latex_str:
            return ""
        text = latex_str.strip()
        replacements = {
            r"\times": "*",
            r"\div": "/",
            r"\,": "",
            r"\;": "",
            r"\ ": "",
            r"\text{": r"\mathrm{",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def is_valid_math(self, latex_str: str) -> bool:
        cleaned = self._clean_latex(latex_str)
        if not cleaned:
            return False
        if parse_latex is None:
            return bool(math_count(cleaned))
        try:
            if "=" in cleaned:
                left, right = cleaned.split("=", 1)
                parse_latex(left.strip())
                parse_latex(right.strip())
            else:
                parse_latex(cleaned)
            return True
        except Exception:
            # The dataset contains many informal formulas. For evaluation we
            # accept obvious mathematical notation even when strict LaTeX parse
            # fails, because VAI is a behavioral metric, not a formal proof check.
            return bool(math_count(cleaned))

    def extract_math_blocks(self, text: str) -> List[str]:
        if not isinstance(text, str):
            return []
        blocks: List[str] = []
        for match in self.latex_pattern.findall(text):
            latex_content = next((part for part in match if part), "")
            if latex_content:
                blocks.append(latex_content)
        return blocks

    def calculate_vai(self, dialogue_text: str) -> Dict[str, float]:
        if not isinstance(dialogue_text, str):
            return {"vai": 0.0, "student_valid_math": 0, "tutor_valid_math": 0, "total_valid_math": 0}

        student_valid_math = 0
        tutor_valid_math = 0
        for speaker, text in split_turns(dialogue_text):
            blocks = self.extract_math_blocks(text)
            # Fallback for plain fractions/formulas not wrapped in LaTeX.
            valid_count = sum(1 for block in blocks if self.is_valid_math(block))
            valid_count = max(valid_count, math_count(text))
            if speaker == "Student":
                student_valid_math += valid_count
            elif speaker == "Tutor":
                tutor_valid_math += valid_count

        total = student_valid_math + tutor_valid_math
        vai = student_valid_math / total if total else 0.0
        return {
            "vai": vai,
            "student_valid_math": student_valid_math,
            "tutor_valid_math": tutor_valid_math,
            "total_valid_math": total,
        }


if __name__ == "__main__":
    verifier = MathVerifier()
    sample = """
AI: [G] Xác suất một lần là \\(1/2\\).
Student: Em tính \\( (1/2)^4 = 1/16 \\).
"""
    print(verifier.calculate_vai(sample))
