import pandas as pd
import random
import json
import time
from src.gps_multiagent_graph import run_tutor
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# --- CONFIG ---
llm_student = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2.5:7b", # Use 7b for student too for better variety
    temperature=0.8
)

def load_questions():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

QUESTIONS = load_questions()

def simulate_student(level, history, question):
    prompts = {
        "Giỏi": "Bạn là học sinh Giỏi. Bạn hiểu nhanh, tự giải được các bước khó, nhưng vẫn muốn thầy hướng dẫn hướng đi tối ưu.",
        "Khá": "Bạn là học sinh Khá. Bạn nắm vững cơ bản nhưng thỉnh thoảng nhầm lẫn ở các bước tính toán phức tạp.",
        "Trung bình": "Bạn là học sinh Trung bình. Bạn cần nhiều gợi ý, hay quên công thức và cần thầy giải thích chi tiết hơn.",
        "Yếu": "Bạn là học sinh Yếu. Bạn rất bối rối, không biết bắt đầu từ đâu, hay xin đáp án và cần thầy cầm tay chỉ việc."
    }
    
    system_prompt = f"{prompts[level]}\nĐề bài: {question}\nQUY TẮC: Trả lời ngắn gọn, tự nhiên như một học sinh đang chat. Không được tự giải xong bài trong 1 câu."
    
    messages = [SystemMessage(content=system_prompt)]
    for m in history:
        if m['role'] == 'user':
            messages.append(HumanMessage(content=m['content']))
        else:
            messages.append(AIMessage(content=m['content']))
            
    response = llm_student.invoke(messages)
    return response.content

def run_session(qid, level, group):
    question_data = next(q for q in QUESTIONS if str(q['id']) == str(qid))
    question_text = question_data['question']
    
    history = []
    # Initial student message
    student_msg = f"Chào thầy, em đang làm bài #{qid}. Thầy hướng dẫn em với ạ."
    
    for _ in range(10): # Limit to 10 turns for augmentation efficiency
        # Teacher response
        # Note: run_tutor handles history as BaseMessage objects
        history_msgs = []
        for h in history:
            if h['role'] == 'user': history_msgs.append(HumanMessage(content=h['content']))
            else: history_msgs.append(AIMessage(content=h['content']))
            
        teacher_reply = run_tutor(str(qid), student_msg, history_msgs)
        history.append({"role": "assistant", "content": teacher_reply})
        
        # Check if solved
        if "[S]" in teacher_reply and ("Chính xác" in teacher_reply or "Đúng rồi" in teacher_reply):
            break
            
        # Student response
        student_msg = simulate_student(level, history, question_text)
        history.append({"role": "user", "content": student_msg})
        
    # Format dialogue
    dialogue = ""
    for h in history:
        label = "Thầy: " if h['role'] == 'assistant' else "Em: "
        dialogue += f"{label}{h['content']}\n"
        
    return dialogue

def main():
    target_count = 550
    levels = ["Giỏi", "Khá", "Trung bình", "Yếu"]
    groups = ["GPS", "Non-GPS"]
    
    results = []
    
    print(f"Starting augmentation of {target_count} sessions...")
    
    for i in range(target_count):
        level = random.choice(levels)
        group = random.choice(groups)
        qid = random.randint(1, 15) # Assuming 15 questions
        
        print(f"[{i+1}/{target_count}] Generating {group} - {level} for QID {qid}...")
        try:
            dialogue = run_session(qid, level, group)
            results.append({
                "Group": group,
                "Student_ID": f"AUG_{int(time.time())}_{i}",
                "Level": level,
                "QID": qid,
                "Dialogue": dialogue
            })
        except Exception as e:
            print(f"Error in session {i}: {e}")
            
        # Save every 10 sessions to avoid data loss
        if (i + 1) % 10 == 0:
            df = pd.DataFrame(results)
            df.to_csv("data/processed/augmented_batch_new.csv", index=False)
            
    # Final append
    df_final = pd.DataFrame(results)
    existing_df = pd.read_csv("data/processed/augmented_conversations_final.csv")
    total_df = pd.concat([existing_df, df_final], ignore_index=True)
    total_df.to_csv("data/processed/augmented_conversations_final.csv", index=False)
    print("Augmentation complete!")

if __name__ == "__main__":
    main()
