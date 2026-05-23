from src.evaluation.metrics.pedagogy_metrics import (
    direct_answer_leakage,
    math_density,
    phase_validity,
    split_turns,
    stall,
    vai,
)
from src.evaluation.metrics.math_verifier import MathVerifier


def test_split_turns_accepts_multiple_speaker_aliases():
    dialogue = "AI: Hãy thử nhé.\nStudent: Em tính \\(1/2\\).\nThầy: Tốt.\nEm: Dạ."
    turns = split_turns(dialogue)
    assert [speaker for speaker, _ in turns] == ["Tutor", "Student", "Tutor", "Student"]


def test_vai_and_math_density_use_student_math():
    dialogue = "Thầy: Gợi ý thôi.\nEm: Em tính \\(1/2\\) và \\(1/4\\)."
    assert vai(dialogue) == 1.0
    assert math_density(dialogue) == 2.0


def test_direct_answer_leakage_flags_early_tutor_solution():
    dialogue = "Thầy: Kết quả là \\(1/16\\), đáp án là C.\nEm: Dạ."
    assert direct_answer_leakage(dialogue, "SINGLE_AGENT") == 1


def test_direct_answer_leakage_does_not_flag_solve_tag():
    dialogue = "Thầy: [S] Kết quả là \\(1/16\\), em giải thích lại vì sao nhé.\nEm: Dạ."
    assert direct_answer_leakage(dialogue, "G-P-S") == 0


def test_phase_validity_requires_g_and_p_before_s():
    assert phase_validity("G-P-S") == 1
    assert phase_validity("G-S") == 0
    assert phase_validity("S") == 0


def test_stall_detects_four_consecutive_same_phase():
    assert stall("G-G-G-G") == 1
    assert stall("G-P-P-P-S") == 0


def test_math_verifier_accepts_ai_student_labels():
    dialogue = "AI: Xác suất là \\(1/2\\).\nStudent: Em tính \\(1/4\\)."
    result = MathVerifier().calculate_vai(dialogue)
    assert result["student_valid_math"] == 1
    assert result["tutor_valid_math"] == 1
    assert result["vai"] == 0.5
