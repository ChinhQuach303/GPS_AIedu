from src.evaluation.metrics.comprehensive_metrics import compute_session_metrics, compare_systems
import pandas as pd


def test_comprehensive_metrics_outputs_phase_and_engagement_columns():
    df = pd.DataFrame({
        "session_id": ["s1"],
        "question": ["q"],
        "level": ["Khá"],
        "trace": ["G-P-S"],
        "dialogue": ["Thầy: [G] Gợi ý.\nEm: Em tính \\(1/2\\).\nThầy: [S] Đúng, em giải thích lại vì sao nhé."],
    })
    out = compute_session_metrics(df, "GPS-Agent")
    assert out.loc[0, "phase_validity"] == 1
    assert out.loc[0, "gps_completion"] == 1
    assert out.loc[0, "vai"] > 0
    assert "autonomy_process_score" in out.columns


def test_compare_systems_includes_binary_and_continuous_tests():
    df = pd.DataFrame({
        "session_id": ["g1", "b1"],
        "question": ["q", "q"],
        "level": ["Khá", "Khá"],
        "trace": ["G-P-S", "SINGLE_AGENT"],
        "dialogue": [
            "Thầy: [G] Gợi ý.\nEm: Em tính \\(1/2\\).\nThầy: [S] Đúng, em giải thích lại.",
            "Thầy: Kết quả là \\(1/2\\), đáp án là A.\nEm: Dạ.",
        ],
    })
    g = compute_session_metrics(df.iloc[[0]], "GPS-Agent")
    b = compute_session_metrics(df.iloc[[1]], "Single-Agent")
    comp = compare_systems(pd.concat([g, b], ignore_index=True))
    assert "direct_answer_leakage" in set(comp.metric)
    assert "vai" in set(comp.metric)
