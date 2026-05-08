import pandas as pd
import time
import sys
import os

# Giả lập môi trường để import các module từ src
sys.path.append(os.getcwd())

from src.gps_langgraph import run_gps_tutor as run_single_agent
from src.agents.student_sim.multi_agent_gps import run_multi_agent_tutor
from src.agents.student_sim.agent_to_agent_sim import simulate_session

def run_ab_test(qids: list, profiles: list):
    results = []
    
    for qid in qids:
        for profile in profiles:
            print(f"\n--- TESTING QID {qid} | PROFILE {profile} ---")
            
            # 1. Chạy Single Agent
            print("Running Single-Agent...")
            start_time = time.time()
            # Giả sử ta có hàm simulate_session đã được cập nhật để nhận tutor_fn
            single_turns, _ = simulate_session(qid, profile, tutor_fn=run_single_agent)
            single_time = time.time() - start_time
            
            # 2. Chạy Multi Agent
            print("Running Multi-Agent...")
            start_time = time.time()
            multi_turns, _ = simulate_session(qid, profile, tutor_fn=run_multi_agent_tutor)
            multi_time = time.time() - start_time
            
            results.append({
                "QID": qid,
                "Profile": profile,
                "Single_Turns": single_turns,
                "Multi_Turns": multi_turns,
                "Single_Time": single_time,
                "Multi_Time": multi_time,
                "Efficiency_Gain": (single_turns - multi_turns) / single_turns if single_turns > 0 else 0
            })
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    # Test mẫu trên 3 câu tiêu biểu: 1 (Dễ), 20 (TB), 43 (Khó)
    test_qids = ["1", "20", "43"]
    test_profiles = ["HS0001", "HS0004"] # So sánh Giỏi vs Yếu
    
    comparison_df = run_ab_test(test_qids, test_profiles)
    comparison_df.to_csv("data/processed/ab_test_results.csv", index=False)
    print("\n=== KẾT QUẢ SO SÁNH A/B TESTING ===")
    print(comparison_df)
