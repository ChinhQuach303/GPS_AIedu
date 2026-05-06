
from src.utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class StudentSimulatorV2:
    def __init__(self, level="Trung bình"):
        self.llm = get_llm(temperature=0.8) # Tăng randomness để đa dạng hành vi
        self.level = level
        self.persona_prompt = self._get_persona(level)

    def _get_persona(self, level):
        personas = {
            "Giỏi": "Bạn là học sinh xuất sắc, nắm vững công thức, thích giải bài nhanh nhưng vẫn tôn trọng gợi ý của thầy.",
            "Khá": "Bạn hiểu bài nhưng đôi khi nhầm lẫn các bước tổ hợp phức tạp. Cần thầy nhắc nhở mới nhận ra lỗi sai.",
            "Trung bình": "Bạn hay quên công thức, thường bế tắc ở bước lập luận ban đầu. Bạn hay hỏi 'Tại sao lại như vậy?'",
            "Yêu": "Bạn rất sợ toán, thường trả lời 'Em không biết' hoặc tính toán sai số cơ bản. Bạn cần thầy dẫn dắt rất chậm."
        }
        return personas.get(level, personas["Trung bình"])

    async def respond(self, history):
        system_msg = (
            f"{self.persona_prompt}\n"
            "NHIỆM VỤ: Hãy đóng vai học sinh hội thoại với Thầy giáo dạy toán.\n"
            "- Nếu thầy đang gợi ý hướng đi hoặc giải thích khái niệm, hãy nói về suy nghĩ hoặc thắc mắc của bạn.\n"
            "- Nếu thầy yêu cầu tính toán hoặc kiểm tra các bước trung gian, hãy thực hiện tính toán (bạn có thể tính sai nếu năng lực là Yếu/Trung bình).\n"
            "- Hãy phản hồi ngắn gọn, tự nhiên bằng TIẾNG VIỆT như một học sinh thật.\n"
            "- TUYỆT ĐỐI KHÔNG dùng tiếng Trung.\n"
            "- KHÔNG bao giờ tự đưa ra đáp số cuối cùng ngay lập tức trừ khi thầy yêu cầu hoặc bài toán đã đi đến bước cuối."
        )
        
        response = await self.llm.ainvoke([SystemMessage(content=system_msg)] + history)
        import random
        # Xử lý chuỗi rỗng hoặc bị xóa sạch sau lọc
        content = response.content.strip()
        if not content or len(content) < 2:
            fallbacks = [
                "Dạ thưa thầy, em vẫn chưa rõ lắm, thầy hướng dẫn thêm cho em được không ạ?",
                "Dạ em đang nghe ạ, thầy giải thích tiếp bước tiếp theo đi thầy.",
                "Em hơi bối rối chỗ công thức, thầy nói kỹ hơn một chút được không ạ?",
                "Dạ, vậy bước tiếp theo mình cần làm gì hả thầy?",
                "Em đang suy nghĩ ạ... thầy gợi ý thêm cho em một chút nhé."
            ]
            return random.choice(fallbacks)
            
        return content
