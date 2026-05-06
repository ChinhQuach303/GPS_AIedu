
import json
import re
import pandas as pd
from src.utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class GPS_Evaluator:
    def __init__(self):
        self.llm = get_llm(temperature=0)

    @staticmethod
    def calculate_isi(turns_g, turns_p, turns_s):
        """ISI = (G + P) / Total. Cao → AI dẫn dắt tốt, không giải hộ."""
        total = turns_g + turns_p + turns_s
        if total == 0:
            return 0.0
        return round((turns_g + turns_p) / total, 3)

    @staticmethod
    def check_fidelity(dialogue_text):
        """
        Kiểm tra tính tuân thủ G -> P -> S bằng cách tìm pattern trong dialogue.
        Trả về True nếu xuất hiện đúng thứ tự G trước P trước S.
        """
        g_pos = dialogue_text.find("[G]")
        p_pos = dialogue_text.find("[P]")
        s_pos = dialogue_text.find("[S]")
        if g_pos == -1 or s_pos == -1:
            return False
        if p_pos == -1:
            # G -> S không qua P là shortcut
            return False
        return g_pos < p_pos < s_pos

    async def llm_judge_score(self, dialogue_text):
        """
        Dùng LLM chấm điểm chất lượng sư phạm 1-10.
        Trả về dict với score và reason.
        """
        eval_prompt = (
            "Bạn là chuyên gia sư phạm toán học. Đánh giá đoạn hội thoại gia sư dưới đây.\n"
            "Tiêu chí: (1) AI có tránh giải hộ không? (2) Học sinh có được tự tư duy không? "
            "(3) Có đúng trình tự Guide→Practice→Solve không?\n"
            "Thang điểm 1-10. Chỉ trả về JSON: {\"score\": float, \"reason\": string}"
        )
        try:
            resp = await self.llm.ainvoke([
                SystemMessage(content=eval_prompt),
                HumanMessage(content=dialogue_text[:2000])  # Giới hạn token
            ])
            content = resp.content
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            pass
        return {"score": 0.0, "reason": "parse_error"}


async def run_evaluation_report(
    csv_path: str = "data/processed/gps_aiedu_gold_standard.csv",
    output_path: str = "data/processed/evaluation_report.json",
    sample_n: int = 200,   # Chỉ chấm LLM trên sample để tiết kiệm thời gian
    use_llm_judge: bool = False  # Tắt mặc định vì tốn thời gian, bật khi cần
):
    """
    Pipeline đánh giá đầy đủ dựa trên gold_standard.csv.
    Tính ISI, Fidelity, và optionally LLM Judge Score.
    """
    df = pd.read_csv(csv_path)
    print(f"📊 Đang đánh giá {len(df)} phiên hội thoại từ: {csv_path}")

    evaluator = GPS_Evaluator()

    # --- 1. Tính ISI từ các cột đã có ---
    df["ISI"] = df.apply(
        lambda r: GPS_Evaluator.calculate_isi(
            r.get("Turns_G", 0), r.get("Turns_P", 0), r.get("Turns_S", 0)
        ), axis=1
    )

    # --- 2. Tính Fidelity từ nội dung Dialogue ---
    if "Dialogue" in df.columns:
        df["Fidelity_Check"] = df["Dialogue"].apply(
            lambda d: GPS_Evaluator.check_fidelity(str(d))
        )
    elif "GPS_Fidelity" in df.columns:
        df["Fidelity_Check"] = df["GPS_Fidelity"]

    # --- 3. Tổng hợp theo Group ---
    group_stats = df.groupby("Group").agg(
        sessions=("Student_ID", "count"),
        avg_ISI=("ISI", "mean"),
        avg_math_density=("Math_Density", "mean"),
        avg_independence=("Independence_Index", "mean"),
        fidelity_rate=("Fidelity_Check", "mean"),
        avg_estimated_score=("Estimated_Post_Score", "mean"),
    ).round(3).to_dict()

    # --- 4. Tổng hợp theo Level ---
    level_stats = df.groupby(["Group", "Level"]).agg(
        sessions=("Student_ID", "count"),
        avg_ISI=("ISI", "mean"),
        avg_independence=("Independence_Index", "mean"),
        avg_estimated_score=("Estimated_Post_Score", "mean"),
    ).round(3).to_dict()

    # --- 5. LLM Judge (optional) ---
    llm_scores = []
    if use_llm_judge and "Dialogue" in df.columns:
        sample_df = df.sample(min(sample_n, len(df)), random_state=42)
        print(f"  🤖 LLM Judge đang chấm {len(sample_df)} phiên mẫu...")
        for _, row in sample_df.iterrows():
            result = await evaluator.llm_judge_score(str(row["Dialogue"]))
            result["Student_ID"] = row["Student_ID"]
            result["Group"] = row["Group"]
            llm_scores.append(result)

    # --- 6. Xuất kết quả ---
    report = {
        "total_sessions": len(df),
        "groups": list(df["Group"].unique()),
        "group_stats": group_stats,
        "level_stats": level_stats,
        "llm_judge_sample": llm_scores if llm_scores else "not_run"
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Báo cáo đã lưu tại: {output_path}")
    print(f"\n📋 Group Stats:")
    for group, stats in group_stats["sessions"].items():
        isi = group_stats["avg_ISI"].get(group, 0)
        fidelity = group_stats["fidelity_rate"].get(group, 0)
        score = group_stats["avg_estimated_score"].get(group, 0)
        print(f"  [{group}] Sessions: {stats} | ISI: {isi:.3f} | Fidelity: {fidelity:.1%} | Score: {score:.2f}")

    return report


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_evaluation_report())
