import asyncio
import json
import os
import pandas as pd
from src.agents.tutor_gps.graph import gps_tutor_app
from src.agents.student_sim.cross_model_simulator import CrossModelStudentSimulator
from langchain_core.messages import HumanMessage, AIMessage

async def simulate_session(question_obj, student_level, session_id):
    """
    Mô phỏng một phiên hội thoại trọn vẹn giữa GPS-Agent (Qwen) và Phi-3 Student.
    """
    question_text = question_obj["question"]
    # Dùng Phi-3-mini làm học sinh
    simulator = CrossModelStudentSimulator(level=student_level, model_name="phi3:mini")
    
    state = {
        "messages": [HumanMessage(content=question_text)],
        "student_level": student_level,
        "student_id": f"SIM_PHI3_{student_level}_{session_id}",
        "trace_labels": [],
        "metadata": {"question_id": question_obj.get("id", "N/A")}
    }
    
    config = {"configurable": {"thread_id": f"thread_phi3_{session_id}"}}
    
    # Chạy tối đa 8 lượt để tránh loop vô tận
    for turn in range(8):
        # AI lượt (Tutor - Qwen)
        async for event in gps_tutor_app.astream(state, config):
            for node_name, output in event.items():
                if node_name != "supervisor":
                    ai_msg = output["messages"][-1]
                    state["messages"].append(ai_msg)
                    state["trace_labels"] = output.get("trace_labels", [])
        
        # Kiểm tra nếu AI đã Solve xong
        if state["trace_labels"] and state["trace_labels"][-1] == "S":
            break
            
        # Học sinh lượt (Phi-3)
        student_resp = await simulator.respond(state["messages"])
        state["messages"].append(HumanMessage(content=student_resp))
        
    return state

async def main():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        # Lấy 25 câu hỏi
        questions = json.load(f)[:25]
    
    # Chỉ tập trung test 2 nhóm Khá và Trung bình vì nhóm này tương tác toán học nhiều nhất
    levels = ["Khá", "Trung bình"]
    all_sessions = []
    
    print(f"🚀 Bắt đầu Cross-Model Simulation (Qwen teaches Phi-3) cho {len(questions) * len(levels)} phiên...")
    
    count = 0
    for q in questions:
        for level in levels:
            count += 1
            print(f"  - Đang mô phỏng ({count}/50): Q_{q.get('id', count)} | Học sinh: {level}")
            
            try:
                session_state = await simulate_session(q, level, count)
                
                # Định dạng chuẩn: Thầy và Em để MathVerifier đọc được
                dialogue_lines = []
                for m in session_state["messages"][1:]: # Bỏ qua tin nhắn gốc
                    speaker = "Thầy" if isinstance(m, AIMessage) else "Em"
                    dialogue_lines.append(f"{speaker}: {m.content}")
                
                dialogue = "\n".join(dialogue_lines)
                
                all_sessions.append({
                    "session_id": session_state["student_id"],
                    "question": q["question"],
                    "level": level,
                    "trace": "-".join(session_state["trace_labels"]),
                    "dialogue": dialogue
                })
                
                # In snapshot mỗi 5 phiên
                if count % 5 == 0:
                    print(f"\n--- SNAPSHOT CROSS-MODEL PHIÊN {count} ({level}) ---")
                    print(dialogue[:500] + "...") 
                    print("-" * 30 + "\n")
            except Exception as e:
                print(f"    ⚠️ Lỗi session: {e}")
            
    # Lưu kết quả ra CSV
    df = pd.DataFrame(all_sessions)
    os.makedirs("data/outputs", exist_ok=True)
    df.to_csv("data/outputs/cross_model_conversations.csv", index=False)
    print(f"✅ Đã hoàn thành! Kết quả lưu tại: data/outputs/cross_model_conversations.csv")

if __name__ == "__main__":
    asyncio.run(main())
