from pathlib import Path

from src.evaluation.metrics.question_bank_recovery import audit_question_bank_with_recovery, recover_answers

ROOT = Path(__file__).resolve().parents[1]


def test_recover_all_45_answers_from_raw_exam_text():
    answers = recover_answers(ROOT / "data/raw/exam_text.txt")
    assert len(answers) == 45
    assert set(answers.values()).issubset({"A", "B", "C", "D"})


def test_audit_separates_answer_coverage_from_option_typography():
    table, summary, _ = audit_question_bank_with_recovery(
        ROOT / "data/processed/probabilities_questions.json",
        ROOT / "data/raw/exam_text.txt",
    )
    assert summary["n_questions"] == 45
    assert summary["recovered_answers_from_raw_solution"] == 45
    assert summary["answer_key_coverage_after_recovery"] == 1.0
    assert summary["original_json_missing_answers"] > 0
    assert summary["options_need_typesetting_repair"] > 0
    assert table["answer_recovered"].all()
