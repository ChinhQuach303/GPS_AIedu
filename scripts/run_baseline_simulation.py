import asyncio
import json
import os
import pandas as pd
from src.agents.tutor_baseline.single_agent import SingleAgentTutor
from src.agents.student_sim.behavioral_simulator_v2 import StudentSimulatorV2
from langchain_core.messages import HumanMessage, AIMessage

async def simulate_session(question_obj, student_level, session_id):
    """
    Mô phỏng một phiên hội thoại giữa Single-Agent AI và Student Simulator.
    """
    question_text = question_obj["question"]
    simulator = StudentSimulatorV2(level=student_level)
    tutor = SingleAgentTutor()
    
    messages = [HumanMessage(content=question_text)]
    
    # Chạy tối đa 8 lượt
    for turn in range(8):
        # AI lượt (Tutor)
        tutor_resp = await tutor.ainvoke(messages)
        messages.append(AIMessage(content=tutor_resp))
        
        # Nếu AI khen ngợi hoàn thành hoặc nói đáp án cuối cùng, có thể dừng sớm
        if "chính xác" in tutor_resp.lower() and turn > 1:
            break
            
        # Học sinh lượt
        student_resp = await simulator.respond(messages)
        messages.append(HumanMessage(content=student_resp))
        
    return messages, f"SIM_BASE_{student_level}_{session_id}"

async def main():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)[:25] # Chạy 25 câu hỏi x 4 level = 100 sessions
    
    levels = ["Giỏi", "Khá", "Trung bình", "Yếu"]
    all_sessions = []
    
    print(f"🚀 Bắt đầu Baseline Simulation cho {len(questions) * len(levels)} phiên...")
    
    count = 0
    for q in questions:
        for level in levels:
            count += 1
            print(f"  - Đang mô phỏng ({count}/100): Q_{q.get('id', count)} | Học sinh: {level}")
            
            try:
                messages, student_id = await simulate_session(q, level, count)
                
                # Định dạng chuẩn: Thầy và Em để MathVerifier đọc được
                dialogue_lines = []
                # Bỏ qua tin nhắn đầu tiên (câu hỏi)
                for m in messages[1:]:
                    speaker = "Thầy" if isinstance(m, AIMessage) else "Em"
                    dialogue_lines.append(f"{speaker}: {m.content}")
                
                dialogue = "\n".join(dialogue_lines)
                
                all_sessions.append({
                    "session_id": student_id,
                    "question": q["question"],
                    "level": level,
                    "trace": "SINGLE_AGENT", # Không có G-P-S trace
                    "dialogue": dialogue
                })
                
                # In snapshot mỗi 5 phiên
                if count % 5 == 0:
                    print(f"\n--- SNAPSHOT BASELINE PHIÊN {count} ({level}) ---")
                    print(dialogue[:500] + "...") 
                    print("-" * 30 + "\n")
            except Exception as e:
                print(f"    ⚠️ Lỗi session: {e}")
            
    # Lưu kết quả ra CSV
    df = pd.DataFrame(all_sessions)
    os.makedirs("data/outputs", exist_ok=True)
    df.to_csv("data/outputs/baseline_conversations.csv", index=False)
    print(f"✅ Đã hoàn thành! Kết quả lưu tại: data/outputs/baseline_conversations.csv")

if __name__ == "__main__":
    asyncio.run(main())
