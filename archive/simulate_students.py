import json
import random
import uuid
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.gps_langgraph import app as tutor_app

# --- CONFIGURATION ---
student_llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2-math:1.5b-instruct-q5_K_M", # Dùng model có sẵn
    temperature=0.8   # Tăng tính sáng tạo/ngẫu nhiên cho học sinh
)

def load_questions():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

QUESTIONS = load_questions()

# --- STUDENT PERSONAS ---
PERSONAS = {
    "yếu": "Em là học sinh trung bình yếu, rất sợ môn Toán. Em hay dùng từ 'em không biết', 'thầy ơi khó quá'. Em hay viết không dấu hoặc viết tắt. Khi trả lời thường rất ngắn và hay hỏi xin đáp án luôn.",
    "khá": "Em là học sinh ham học nhưng hay tính toán nhầm. Em lễ phép, hay dùng 'vâng ạ', 'thưa thầy'. Em cố gắng làm theo hướng dẫn nhưng thỉnh thoảng bị kẹt ở các bước tính tổ hợp/chỉnh hợp.",
    "giỏi": "Em học giỏi toán, tự tin. Em thường muốn nhảy bước hoặc hỏi các cách giải nhanh hơn. Em trả lời gãy gọn, đúng trọng tâm."
}

def simulate_conversation(student_profile, question):
    student_persona = PERSONAS.get(student_profile, PERSONAS["khá"])
    qid = str(question['id'])
    
    system_prompt = f"""
    BẠN LÀ MỘT HỌC SINH THỰC THẾ. 
    Đặc điểm: {student_persona}
    Nhiệm vụ: Bạn đang nhắn tin với thầy giáo AI để giải một bài toán xác suất.
    Đề bài: {question['question']}
    
    QUY TẮC:
    1. Chỉ trả lời 1 câu mỗi lần nhắn.
    2. Không được tự giải bài toán ngay lập tức nếu bạn là học sinh yếu/khá.
    3. Đóng vai đúng tính cách (có thể mắc lỗi, có thể than phiền).
    4. Nếu đã hiểu hoàn toàn và ra đáp số, hãy viết bài giải đầy đủ ở cuối.
    """
    
    history = []
    tutor_state = {"student_msg": "", "qid": qid, "history": [], "intent": "G", "response": ""}
    
    logs = []
    
    # Bắt đầu bằng câu hỏi đầu tiên của học sinh
    current_msg = "Thầy ơi bài này làm thế nào ạ?"
    
    for turn in range(10): # Giới hạn tối đa 10 lượt hội thoại
        # 1. Gọi Tutor Agent
        tutor_input = {
            "student_msg": current_msg,
            "qid": qid,
            "history": history
        }
        tutor_response = tutor_app.invoke(tutor_input)
        ai_reply = tutor_response['response']
        
        logs.append({"role": "user", "content": current_msg})
        logs.append({"role": "assistant", "content": ai_reply})
        history.append({"role": "user", "content": current_msg})
        history.append({"role": "assistant", "content": ai_reply})
        
        print(f"Học sinh ({student_profile}): {current_msg}")
        print(f"Gia sư GPS: {ai_reply}\n")
        
        # Nếu AI đã chốt giai đoạn [S] thành công, dừng hội thoại
        if "[S]" in ai_reply and ("Chính xác" in ai_reply or "Đúng rồi" in ai_reply):
            break
            
        # 2. Gọi Student Agent để phản hồi lại dựa trên gợi ý của Tutor
        student_response = student_llm.invoke([
            SystemMessage(content=system_prompt),
            *[HumanMessage(content=m['content']) if m['role']=='assistant' else SystemMessage(content=m['content']) for m in history]
        ])
        current_msg = student_response.content

    return logs

if __name__ == "__main__":
    import sys
    # Fix Windows Unicode Output
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Chạy thử nghiệm 1 kịch bản cho học sinh Yếu
    sample_q = QUESTIONS[0]
    print(f"--- BẮT ĐẦU MÔ PHỎNG: CÂU {sample_q['id']} ---\n")
    conv_logs = simulate_conversation("yếu", sample_q)
    
    with open(f"data/processed/simulation_HS_YEU_Q1.json", "w", encoding="utf-8") as f:
        json.dump(conv_logs, f, ensure_ascii=False, indent=2)
    print("\nĐã lưu log hội thoại mô phỏng vào data/processed/simulation_HS_YEU_Q1.json")
