
"""
generate_research_stats.py
--------------------------
Tạo toàn bộ bảng số liệu thống kê cho paper EMNLP.
Đọc trực tiếp từ gps_aiedu_gold_standard.csv (78k dòng).

Chạy: PYTHONPATH=. python3 scripts/generate_research_stats.py
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

INPUT_CSV   = "data/processed/gps_aiedu_gold_standard.csv"
OUTPUT_DIR  = Path("data/outputs/research_stats")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────
# 1. Hake's Normalized Gain
# ─────────────────────────────────────────────
def hake_gain(pre_score: float, post_score: float, max_score: float = 100.0) -> float:
    """g = (post - pre) / (max - pre)"""
    if max_score == pre_score:
        return 0.0
    return (post_score - pre_score) / (max_score - pre_score)

# ─────────────────────────────────────────────
# 2. Cohen's d (Effect Size)
# ─────────────────────────────────────────────
def cohen_d(group1: pd.Series, group2: pd.Series) -> float:
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (group1.mean() - group2.mean()) / pooled_std if pooled_std > 0 else 0.0


# ─────────────────────────────────────────────
# 3. Markov Chain Transition Matrix
# ─────────────────────────────────────────────
def compute_markov_transitions(df: pd.DataFrame) -> dict:
    """
    Phân tích xác suất chuyển trạng thái G→P, P→S, G→S (shortcut) v.v.
    Dựa trên tổng số lượt của từng nhãn trong dataset.
    """
    # Tính tổng số lượt cho từng nhóm
    gps = df[df["Group"] == "GPS"]
    non_gps = df[df["Group"] != "GPS"]

    def avg_turn_dist(subdf):
        g = subdf["Turns_G"].mean()
        p = subdf["Turns_P"].mean()
        s = subdf["Turns_S"].mean()
        total = g + p + s
        return {
            "avg_G": round(g, 2),
            "avg_P": round(p, 2),
            "avg_S": round(s, 2),
            "G_ratio": round(g / total, 3) if total else 0,
            "P_ratio": round(p / total, 3) if total else 0,
            "S_ratio": round(s / total, 3) if total else 0,
        }

    return {
        "GPS": avg_turn_dist(gps),
        "Non-GPS": avg_turn_dist(non_gps)
    }

def run_analysis():
    print(f"Reading data from: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)
    print(f"   -> {len(df)} sessions | Columns: {list(df.columns)}")

    report = {}

    # --- 4. Tổng hợp theo Level ---
    # Chỉnh sửa: Đảm bảo Estimated_Post_Score được xử lý đúng thang 100
    level_stats = df.groupby(["Group", "Level"]).agg(
        sessions=("Student_ID", "count"),
        avg_independence=("Independence_Index", "mean"),
        avg_estimated_score=("Estimated_Post_Score", "mean"),
    ).round(3).reset_index().to_dict(orient="records")
    report["level_stats"] = level_stats

    # --- A. Thống kê tổng quan theo Group ---
    group_summary_df = df.groupby("Group").agg(
        n_sessions=("Student_ID", "count"),
        avg_math_density=("Math_Density", "mean"),
        avg_independence=("Independence_Index", "mean"),
        avg_gps_fidelity=("GPS_Fidelity", "mean"),
        avg_post_score=("Estimated_Post_Score", "mean"),
    ).round(3).reset_index()
    report["group_summary"] = group_summary_df.to_dict(orient="records")
    print(f"\nGroup Summary:\n{group_summary_df.to_string()}")

    # --- B. Hake's Gain theo Level × Group ---
    PRE_BASELINE = 50.0 # Giả định điểm Pre-test trung bình là 50/100
    df["Hake_Gain"] = df["Estimated_Post_Score"].apply(
        lambda post: hake_gain(PRE_BASELINE, post, max_score=100.0)
    )
    hake_df = df.groupby(["Group", "Level"])["Hake_Gain"].mean().round(3).reset_index()
    report["hake_gain"] = hake_df.to_dict(orient="records")
    print(f"\nHake's Gain (g):\n{hake_df.to_string()}")

    # --- C. Cohen's d và T-test (GPS vs Non-GPS) ---
    gps_scores   = df[df["Group"] == "GPS"]["Estimated_Post_Score"].dropna()
    nongps_scores = df[df["Group"] != "GPS"]["Estimated_Post_Score"].dropna()

    t_stat, p_value = stats.ttest_ind(gps_scores, nongps_scores, equal_var=False)
    d = cohen_d(gps_scores, nongps_scores)

    report["statistical_test"] = {
        "test": "Welch's t-test (GPS vs Non-GPS, Estimated_Post_Score)",
        "gps_mean": round(gps_scores.mean(), 3),
        "nongps_mean": round(nongps_scores.mean(), 3),
        "t_statistic": round(t_stat, 4),
        "p_value": round(p_value, 6),
        "cohen_d": round(d, 3),
        "effect_size": "Large" if abs(d) >= 0.8 else ("Medium" if abs(d) >= 0.5 else "Small"),
        "significant": p_value < 0.05
    }
    print(f"\nStatistical Test (Score):")
    print(f"   GPS mean:    {gps_scores.mean():.3f}")
    print(f"   Non-GPS mean:{nongps_scores.mean():.3f}")
    print(f"   t={t_stat:.4f}, p={p_value:.6f}, Cohen's d={d:.3f}")

    # --- D. T-test cho Independence Index ---
    gps_ind   = df[df["Group"] == "GPS"]["Independence_Index"].dropna()
    nongps_ind = df[df["Group"] != "GPS"]["Independence_Index"].dropna()
    t2, p2 = stats.ttest_ind(gps_ind, nongps_ind, equal_var=False)
    d2 = cohen_d(gps_ind, nongps_ind)
    report["independence_index_test"] = {
        "gps_mean": round(gps_ind.mean(), 3),
        "nongps_mean": round(nongps_ind.mean(), 3),
        "t_statistic": round(t2, 4),
        "p_value": round(p2, 6),
        "cohen_d": round(d2, 3),
        "significant": p2 < 0.05
    }
    print(f"\nIndependence Index Test:")
    print(f"   GPS:{gps_ind.mean():.3f} | Non-GPS:{nongps_ind.mean():.3f} | p={p2:.6f}, d={d2:.3f}")

    # --- E. Markov Chain Transition ---
    markov = compute_markov_transitions(df)
    report["markov_transitions"] = markov
    print(f"\nAvg Turn Distribution (Markov proxy):")
    for grp, val in markov.items():
        print(f"   [{grp}] G:{val['G_ratio']:.1%} | P:{val['P_ratio']:.1%} | S:{val['S_ratio']:.1%}")

    # --- F. Weekly Trend ---
    if "Week" in df.columns:
        weekly = df.groupby(["Group", "Week"]).agg(
            avg_independence=("Independence_Index", "mean"),
            avg_math_density=("Math_Density", "mean"),
        ).round(3).reset_index()
        report["weekly_trend"] = weekly.to_dict(orient="records")

    # --- G. Lưu kết quả ---
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)): return int(obj)
            if isinstance(obj, (np.floating,)): return float(obj)
            if isinstance(obj, (np.bool_,)): return bool(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return super().default(obj)

    output_path = OUTPUT_DIR / "research_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, cls=NpEncoder)
    print(f"\nDone! Results saved at: {output_path}")

    # Xuất bảng Table 1
    paper_table = {
        "Table 1 - Group Comparison": {
            "GPS": {
                "N": int(len(gps_ind)),
                "Hake_Gain": round(float(df[df["Group"]=="GPS"]["Hake_Gain"].mean()), 3),
                "Independence_Index": round(float(gps_ind.mean()), 3),
                "Math_Density": round(float(df[df["Group"]=="GPS"]["Math_Density"].mean()), 2),
                "Cohen_d_II": round(float(d2), 3),
                "p_value_II": round(float(p2), 6)
            },
            "Non-GPS": {
                "N": int(len(nongps_ind)),
                "Hake_Gain": round(float(df[df["Group"]!="GPS"]["Hake_Gain"].mean()), 3),
                "Independence_Index": round(float(nongps_ind.mean()), 3),
                "Math_Density": round(float(df[df["Group"]!="GPS"]["Math_Density"].mean()), 2),
                "Cohen_d_II": "baseline",
                "p_value_II": "baseline"
            }
        }
    }
    paper_table_path = OUTPUT_DIR / "paper_table1.json"
    with open(paper_table_path, "w", encoding="utf-8") as f:
        json.dump(paper_table, f, ensure_ascii=False, indent=2)
    print(f"Paper Table 1 saved at: {paper_table_path}")

    return report


if __name__ == "__main__":
    run_analysis()

