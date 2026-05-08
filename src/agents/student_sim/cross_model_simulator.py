import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

class CrossModelStudentSimulator:
    def __init__(self, level, model_name="phi3:mini"):
        """
        Simulator đóng vai học sinh, sử dụng một model khác biệt để phá vỡ circular evaluation.
        Mặc định dùng phi3:mini (3.8B) vì nhẹ và cấu trúc khác Qwen.
        """
        self.level = level
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            temperature=0.7, # Nhiệt độ cao hơn chút để đa dạng hóa hành vi học sinh
            timeout=120,
            model_kwargs={
                "stop": ["<|im_start|>", "<|im_end|>", "Thầy:"],
            }
        )
        
        # Load prompt theo level học sinh
        prompt_path = f"config/prompts/students/student_{level.lower().replace(' ', '_')}.txt"
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read().strip()
        else:
            # Fallback prompt nếu không tìm thấy file
            self.system_prompt = f"""Bạn đóng vai một học sinh trung học phổ thông đang nhờ giáo viên giải bài tập môn Toán.
Học lực của bạn: {level}.

Hướng dẫn hành vi:
1. LUÔN LUÔN dùng tiếng Việt. Xưng hô "Em" và gọi "Thầy".
2. Tương tác với Thầy từng bước một. KHÔNG tự giải nguyên bài toán nếu Thầy chưa yêu cầu.
3. Nếu Thầy bảo tính toán, hãy thực hiện phép tính và đưa ra kết quả. Nếu thấy khó, hãy hỏi lại Thầy.
4. Giữ câu trả lời ngắn gọn, tự nhiên như một đoạn chat thực tế. KHÔNG đóng vai Thầy.
"""

    async def respond(self, chat_history):
        """
        Nhận vào lịch sử hội thoại và sinh ra câu trả lời của học sinh.
        """
        # Bắt buộc nhắc lại tiếng Việt để các model nhỏ không bị trượt ngôn ngữ
        messages = [SystemMessage(content=self.system_prompt)] + chat_history
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"Lỗi Student Simulator ({self.model_name}): {e}")
            return "Em chưa hiểu lắm, thầy có thể giải thích lại được không ạ?"

