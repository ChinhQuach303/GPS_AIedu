import asyncio
import json
import os
import pandas as pd
from src.agents.tutor_gps.graph import gps_tutor_app
from src.agents.student_sim.behavioral_simulator_v2 import StudentSimulatorV2
from langchain_core.messages import HumanMessage, AIMessage

async def simulate_session(question_obj, student_level, session_id):
    """
    Mô phỏng một phiên hội thoại trọn vẹn giữa Multi-Agent AI và Student Simulator.
    """
    question_text = question_obj["question"]
    simulator = StudentSimulatorV2(level=student_level)
    
    state = {
        "messages": [HumanMessage(content=question_text)],
        "student_level": student_level,
        "student_id": f"SIM_{student_level}_{session_id}",
        "trace_labels": [],
        "metadata": {"question_id": question_obj.get("id", "N/A")}
    }
    
    config = {"configurable": {"thread_id": f"thread_{session_id}"}}
    
    # Chạy tối đa 10 lượt để tránh loop vô tận
    for turn in range(10):
        # AI lượt
        async for event in gps_tutor_app.astream(state, config):
            for node_name, output in event.items():
                if node_name != "supervisor":
                    ai_msg = output["messages"][-1]
                    state["messages"].append(ai_msg)
                    state["trace_labels"] = output.get("trace_labels", [])
        
        # Kiểm tra nếu AI đã Solve xong
        if state["trace_labels"] and state["trace_labels"][-1] == "S":
            break
            
        # Học sinh lượt
        student_resp = await simulator.respond(state["messages"])
        state["messages"].append(HumanMessage(content=student_resp))
        
    return state

async def main():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)[:25] # Chạy 25 câu hỏi x 4 level = 100 sessions
    
    levels = ["Giỏi", "Khá", "Trung bình", "Yêu"]
    all_sessions = []
    
    print(f"🚀 Bắt đầu Massive Simulation cho {len(questions) * len(levels)} phiên...")
    
    for q in questions:
        for level in levels:
            print(f"  - Đang mô phỏng: Q_{q.get('id')} | Học sinh: {level}")
            
            try:
                session_state = await simulate_session(q, level, len(all_sessions))
                
                # Lưu log
                dialogue = "\n".join([f"{'AI' if isinstance(m, AIMessage) else 'Student'}: {m.content}" for m in session_state["messages"]])
                all_sessions.append({
                    "session_id": session_state["student_id"],
                    "question": q["question"],
                    "level": level,
                    "trace": "-".join(session_state["trace_labels"]),
                    "dialogue": dialogue
                })
                
                # Lưu kết quả ra CSV ngay lập tức (Incremental Save)
                df = pd.DataFrame(all_sessions)
                os.makedirs("data/outputs", exist_ok=True)
                df.to_csv("data/outputs/massive_simulation_results.csv", index=False)

                # In snapshot mỗi 5 phiên
                if len(all_sessions) % 5 == 0:
                    print(f"\n--- SNAPSHOT PHIÊN {len(all_sessions)} ({level}) ---")
                    print(dialogue[:500] + "...") 
                    print("-" * 30 + "\n")
                    
            except Exception as e:
                print(f"    ⚠️ Lỗi session: {e}")
            
    print(f"✅ Đã hoàn thành! Kết quả lưu tại: data/outputs/massive_simulation_results.csv")

if __name__ == "__main__":
    asyncio.run(main())
