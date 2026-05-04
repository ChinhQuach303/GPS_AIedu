"""
Comprehensive Pedagogical Evaluation Pipeline
Combines real simulated data + augmented data
Outputs weekly metrics for both GPS and Non-GPS groups
"""

import pandas as pd
import numpy as np
import re

# ─────────────────────────────────────────────
# 1. DATA LOADING & NORMALIZATION
# ─────────────────────────────────────────────

PROFILE_TO_LEVEL = {
    'HS0001': 'Giỏi',
    'HS0002': 'Khá',
    'HS0003': 'Yếu',
    'HS0004': 'Trung bình',
    'HS0005': 'Trung bình'
}

# Assign simulated "week" based on QID ranges
# Weeks 1-6, QIDs 1-45 (pilot had QIDs 1-15 approx.)
def qid_to_week(qid):
    try:
        q = int(qid)
        if q <= 6:   return 1
        if q <= 12:  return 2
        if q <= 18:  return 3
        if q <= 24:  return 4
        if q <= 30:  return 5
        return 6
    except:
        return 1

def load_real_data(path):
    df = pd.read_csv(path)
    df['Level'] = df['Profile'].map(PROFILE_TO_LEVEL).fillna('Trung bình')
    df['Group'] = 'GPS'
    df['Week'] = df['QID'].apply(qid_to_week)

    # Build session-level dialogue
    def build_dialogue(grp):
        turns = []
        for _, row in grp.iterrows():
            turns.append(f"Em: {row['Question']}")
            turns.append(f"Thầy: {row['AI Response']}")
        return "\n".join(turns)

    sessions = (
        df.groupby(['Student ID', 'QID', 'Level', 'Group', 'Week'])
        .apply(build_dialogue, include_groups=False)
        .reset_index()
    )
    sessions.columns = ['Student_ID', 'QID', 'Level', 'Group', 'Week', 'Dialogue']
    return sessions


def load_aug_data(path):
    df = pd.read_csv(path)
    df['Week'] = df['QID'].apply(qid_to_week)
    return df


# ─────────────────────────────────────────────
# 2. METRICS PER SESSION
# ─────────────────────────────────────────────

def compute_metrics(df):
    df = df.copy()
    text = df['Dialogue'].fillna('')

    df['Turns_G']     = text.apply(lambda x: len(re.findall(r'\[G\]', x)))
    df['Turns_P']     = text.apply(lambda x: len(re.findall(r'\[P\]', x)))
    df['Turns_S']     = text.apply(lambda x: len(re.findall(r'\[S\]', x)))
    df['Total_Turns'] = text.apply(lambda x: x.count('Thầy:') + x.count('Em:'))

    # Independence Index: S / (G + P + 1) — higher means student solved with less scaffolding
    df['Independence_Index'] = df['Turns_S'] / (df['Turns_G'] + df['Turns_P'] + 1)

    # Scaffolding Depth: average G+P turns before first S
    df['Scaffolding_Depth'] = df['Turns_G'] + df['Turns_P']

    # Sequence Adherence: GPS order (G appears before P before S)
    def sequence_ok(d):
        g = d.find('[G]')
        p = d.find('[P]')
        s = d.find('[S]')
        if g == -1 and p == -1 and s == -1:
            return 0.5  # no labels, neutral
        defined = [(v, k) for k, v in [('G', g), ('P', p), ('S', s)] if v != -1]
        defined.sort()
        order = [k for _, k in defined]
        ideal = ['G', 'P', 'S']
        score = sum(a == b for a, b in zip(order, ideal[:len(order)])) / max(len(order), 1)
        return score

    df['Sequence_Score'] = text.apply(sequence_ok)

    # Math Density: count of LaTeX/math expressions
    df['Math_Density'] = text.apply(lambda x: len(re.findall(
        r'\$[^$]+\$|\\\([^)]+\\\)|\\\[[^\]]+\\\]|C_\{?\d|P_\{?\d|\bC\d|\bP\d', x
    )))

    # Engagement: average length per turn
    df['Avg_Turn_Length'] = df.apply(
        lambda r: len(r['Dialogue']) / (r['Total_Turns'] + 1), axis=1
    )

    return df


# ─────────────────────────────────────────────
# 3. WEEKLY AGGREGATION
# ─────────────────────────────────────────────

METRICS = [
    'Total_Turns', 'Independence_Index', 'Scaffolding_Depth',
    'Sequence_Score', 'Math_Density', 'Avg_Turn_Length'
]

def weekly_summary(df, label=""):
    df = compute_metrics(df)
    summary = (
        df.groupby(['Week', 'Group'])[METRICS]
        .mean()
        .round(3)
        .reset_index()
    )
    summary['Dataset'] = label
    return summary, df


def level_summary(df):
    df = compute_metrics(df)
    return (
        df.groupby(['Level', 'Group'])[METRICS]
        .mean()
        .round(3)
        .reset_index()
    )


# ─────────────────────────────────────────────
# 4. LEARNING GAIN (simulated from mock scores)
# ─────────────────────────────────────────────

LEVEL_PRE  = {'Giỏi': 70, 'Khá': 55, 'Trung bình': 40, 'Yếu': 25}
LEVEL_POST = {
    'GPS':     {'Giỏi': 92, 'Khá': 82, 'Trung bình': 70, 'Yếu': 55},
    'Non-GPS': {'Giỏi': 80, 'Khá': 65, 'Trung bình': 52, 'Yếu': 38}
}

def learning_gain_table():
    rows = []
    for lvl in LEVEL_PRE:
        for grp in ['GPS', 'Non-GPS']:
            pre  = LEVEL_PRE[lvl]
            post = LEVEL_POST[grp][lvl]
            gain = post - pre
            hake = gain / (100 - pre) if pre < 100 else 0
            rows.append({'Level': lvl, 'Group': grp,
                         'Pre': pre, 'Post': post,
                         'Gain': gain, 'Hake_g': round(hake, 3)})
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 5. MAIN REPORT
# ─────────────────────────────────────────────

def main():
    REAL_PATH = 'data/processed/simulated_conversations.csv'
    AUG_PATH  = 'data/processed/augmented_conversations_final.csv'

    print("Loading datasets...")
    df_real = load_real_data(REAL_PATH)
    df_aug  = load_aug_data(AUG_PATH)

    # Combine
    df_all = pd.concat([df_real, df_aug], ignore_index=True)

    print(f"  → Real sessions:      {len(df_real)}")
    print(f"  → Augmented sessions: {len(df_aug)}")
    print(f"  → Total sessions:     {len(df_all)}")

    # ── Weekly report ──────────────────────────────
    weekly, df_computed = weekly_summary(df_all, "Combined")

    print("\n" + "═"*85)
    print("  WEEKLY COMPARISON: GPS vs Non-GPS (Average Metrics)")
    print("═"*85)

    for week in sorted(weekly['Week'].unique()):
        w = weekly[weekly['Week'] == week]
        print(f"\n── Week {week} ─────────────────────────────────────────────────────────")
        print(f"  {'Metric':<25} {'GPS':>10} {'Non-GPS':>12}  {'Δ':>8}")
        print(f"  {'─'*25} {'─'*10} {'─'*12}  {'─'*8}")
        for m in METRICS:
            gps_row = w[w['Group'] == 'GPS'][m]
            non_row = w[w['Group'] == 'Non-GPS'][m]
            gps_val = gps_row.values[0] if len(gps_row) else float('nan')
            non_val = non_row.values[0] if len(non_row) else float('nan')
            delta = gps_val - non_val if not (np.isnan(gps_val) or np.isnan(non_val)) else float('nan')
            sign = "+" if delta > 0 else ""
            print(f"  {m:<25} {gps_val:>10.3f} {non_val:>12.3f}  {sign}{delta:>7.3f}")

    # ── Level breakdown ────────────────────────────
    lvl_sum = level_summary(df_all)
    print("\n" + "═"*85)
    print("  PROFICIENCY LEVEL BREAKDOWN (Independence Index & Math Density)")
    print("═"*85)
    for lvl in ['Giỏi', 'Khá', 'Trung bình', 'Yếu']:
        sub = lvl_sum[lvl_sum['Level'] == lvl]
        gps = sub[sub['Group']=='GPS']
        non = sub[sub['Group']=='Non-GPS']
        gps_ii = gps['Independence_Index'].values[0] if len(gps) else float('nan')
        non_ii = non['Independence_Index'].values[0] if len(non) else float('nan')
        gps_md = gps['Math_Density'].values[0] if len(gps) else float('nan')
        non_md = non['Math_Density'].values[0] if len(non) else float('nan')
        print(f"\n  [{lvl}]")
        print(f"    Independence Index → GPS: {gps_ii:.3f}   Non-GPS: {non_ii:.3f}   Δ={gps_ii-non_ii:+.3f}")
        print(f"    Math Density       → GPS: {gps_md:.2f}     Non-GPS: {non_md:.2f}     Δ={gps_md-non_md:+.2f}")

    # ── Learning Gain ──────────────────────────────
    lg = learning_gain_table()
    print("\n" + "═"*85)
    print("  LEARNING OUTCOME METRICS (Simulated Pre/Post Scores)")
    print("═"*85)
    print(f"\n  {'Level':<12} {'Group':<10} {'Pre':>5} {'Post':>6} {'Gain':>6} {'Hake g':>8}")
    print(f"  {'─'*12} {'─'*10} {'─'*5} {'─'*6} {'─'*6} {'─'*8}")
    for _, r in lg.iterrows():
        print(f"  {r.Level:<12} {r.Group:<10} {r.Pre:>5} {r.Post:>6} {r.Gain:>+6} {r.Hake_g:>8.3f}")

    # Cohen's d on Independence Index (GPS vs Non-GPS)
    gps_ii_all = df_computed[df_computed['Group']=='GPS']['Independence_Index'].dropna()
    non_ii_all = df_computed[df_computed['Group']=='Non-GPS']['Independence_Index'].dropna()
    pooled_sd  = np.sqrt((gps_ii_all.std()**2 + non_ii_all.std()**2) / 2)
    cohens_d   = (gps_ii_all.mean() - non_ii_all.mean()) / (pooled_sd + 1e-9)

    print(f"\n  → Cohen's d (Independence Index): {cohens_d:.3f}")
    magnitude = "Large" if abs(cohens_d) > 0.8 else ("Medium" if abs(cohens_d) > 0.5 else "Small")
    print(f"  → Effect Size Magnitude: {magnitude}")

    # Save summary
    out_path = "data/processed/weekly_evaluation_report.csv"
    weekly.to_csv(out_path, index=False)
    print(f"\n  ✅ Weekly summary saved → {out_path}")

    return weekly, lvl_sum, lg, df_computed


if __name__ == "__main__":
    main()
