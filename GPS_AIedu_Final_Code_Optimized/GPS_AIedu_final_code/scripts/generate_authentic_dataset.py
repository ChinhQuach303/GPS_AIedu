
import asyncio
import json
import os
import pandas as pd
import time
from src.agents.tutor_gps.graph import gps_tutor_app
from src.agents.tutor_gps.baseline_agent import SingleAgentTutor
from src.agents.student_sim.behavioral_simulator_v2 import StudentSimulatorV2
from langchain_core.messages import HumanMessage, AIMessage
import re

def clean_chinese(text):
    """Xóa bỏ các ký tự tiếng Trung khỏi văn bản."""
    if not isinstance(text, str): return text
    # Regex cho dải ký tự Trung Quốc
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return chinese_pattern.sub('', text).strip()

# CONFIG
CONCURRENCY = int(os.getenv("CONCURRENCY", 2))
TOTAL_SESSIONS_PER_GROUP = int(os.getenv("TOTAL_SESSIONS_PER_GROUP", 500))
OUTPUT_FILE = "data/processed/authentic_research_data.csv"

async def run_gps_session(question, level, session_id, semaphore):
    """Mô phỏng 1 phiên với Multi-Agent GPS"""
    async with semaphore:
        simulator = StudentSimulatorV2(level=level)
        state = {
            "messages": [HumanMessage(content=question)],
            "student_level": level,
            "student_id": f"GPS_{level}_{session_id}",
            "trace_labels": [],
            "metadata": {}
        }
        config = {"configurable": {"thread_id": f"gps_thread_{session_id}"}}
        
        dialogue_history = []
        # Chạy tối đa 8 lượt trao đổi
        for turn in range(8):
            # AI turn
            ai_resp = ""
            async for event in gps_tutor_app.astream(state, config):
                for node, output in event.items():
                    if node != "supervisor" and "messages" in output:
                        msg = output["messages"][-1]
                        ai_resp = clean_chinese(msg.content)
                        msg.content = ai_resp # Cập nhật lại nội dung tin nhắn để state cũng sạch
                        state["messages"].append(msg)
                        state["trace_labels"] = output.get("trace_labels", [])
            
            dialogue_history.append(f"AI: {ai_resp}")
            print(f"   [GPS-{session_id}] AI Turn {turn+1} done.")
            
            # Kiểm tra kết thúc
            if state["trace_labels"] and state["trace_labels"][-1] == "S":
                break
                
            # Student turn
            student_resp = ""
            for retry in range(3):
                resp = await simulator.respond(state["messages"])
                student_resp = clean_chinese(resp)
                if student_resp and len(student_resp) > 5:
                    break
                print(f"⚠️ [GPS] Student response empty/short. Retrying {retry+1}/3...")
            
            if not student_resp:
                student_resp = "Dạ thưa thầy, em vẫn chưa hiểu lắm, thầy có thể giải thích kỹ hơn được không ạ?"

            dialogue_history.append(f"Student: {student_resp}")
            print(f"   [GPS-{session_id}] Student Turn {turn+1} done.")
            state["messages"].append(HumanMessage(content=student_resp))
            
        return {
            "Group": "GPS",
            "Student_ID": state["student_id"],
            "Level": level,
            "Dialogue": "\n".join(dialogue_history),
            "Trace": "-".join(state["trace_labels"])
        }

async def run_baseline_session(question, level, session_id, semaphore):
    """Mô phỏng 1 phiên với Single-Agent Baseline"""
    async with semaphore:
        tutor = SingleAgentTutor()
        simulator = StudentSimulatorV2(level=level)
        messages = [HumanMessage(content=question)]
        dialogue_history = []
        
        for turn in range(8):
            # AI turn
            resp = await tutor.chat(messages)
            ai_content = clean_chinese(resp.content)
            resp.content = ai_content # Cập nhật lại nội dung tin nhắn
            dialogue_history.append(f"AI: {ai_content}")
            print(f"   [Base-{session_id}] AI Turn {turn+1} done.")
            messages.append(resp)
            
            if "[S]" in ai_content or "kết thúc" in ai_content.lower():
                break
                
            # Student turn
            student_resp = ""
            for retry in range(3):
                resp = await simulator.respond(messages)
                student_resp = clean_chinese(resp)
                if student_resp and len(student_resp) > 5:
                    break
                print(f"⚠️ [Baseline] Student response empty/short. Retrying {retry+1}/3...")

            if not student_resp:
                student_resp = "Dạ, thầy nói tiếp đi ạ, em đang nghe."

            dialogue_history.append(f"Student: {student_resp}")
            print(f"   [Base-{session_id}] Student Turn {turn+1} done.")
            messages.append(HumanMessage(content=student_resp))
            
        return {
            "Group": "Baseline",
            "Student_ID": f"BASE_{level}_{session_id}",
            "Level": level,
            "Dialogue": "\n".join(dialogue_history),
            "Trace": "N/A"
        }

async def main():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    levels = ["Giỏi", "Khá", "Trung bình", "Yêu"]
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    # 1. Cơ chế Resume: Đọc file cũ nếu có
    all_results = []
    processed_ids = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_csv(OUTPUT_FILE)
            all_results = df_existing.to_dict(orient="records")
            # Trích xuất số ID từ chuỗi "GPS_Giỏi_5" -> 5
            for sid in df_existing["Student_ID"]:
                try:
                    num = int(sid.split("_")[-1])
                    processed_ids.add(num)
                except: pass
            print(f"🔄 Đã tìm thấy file cũ. Resume từ {len(processed_ids)} phiên đã hoàn thành...")
        except Exception as e:
            print(f"Không thể đọc file cũ: {e}")

    tasks = []
    print(f"🚀 Bắt đầu sinh đến mốc {TOTAL_SESSIONS_PER_GROUP} phiên/nhóm (Output: {OUTPUT_FILE})...")
    start_time = time.time()
    
    # 2. Chỉ tạo Task cho những ID chưa chạy
    for i in range(TOTAL_SESSIONS_PER_GROUP):
        if i in processed_ids:
            continue
            
        q = questions[i % len(questions)]["question"]
        lvl = levels[i % 4]
        tasks.append(run_gps_session(q, lvl, i, semaphore))
        tasks.append(run_baseline_session(q, lvl, i, semaphore))
    
    if not tasks:
        print("✅ Toàn bộ dữ liệu đã được sinh đủ! Không cần chạy thêm.")
        return

    # 3. Chạy và lưu theo batch 10
    for i in range(0, len(tasks), 10):
        batch = tasks[i:i+10]
        results = await asyncio.gather(*batch)
        all_results.extend(results)
        
        # Save incremental
        df = pd.DataFrame(all_results)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"💾 Đã lưu tiến độ: Hoàn thành thêm {len(results)} lượt. Tổng số dòng CSV: {len(all_results)}")

    duration = time.time() - start_time
    print(f"🎉 Hoàn thành! Tổng thời gian: {duration/60:.2f} phút.")

if __name__ == "__main__":
    asyncio.run(main())
