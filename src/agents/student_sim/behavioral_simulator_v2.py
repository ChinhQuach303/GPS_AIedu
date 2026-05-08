
from src.utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class StudentSimulatorV2:
    def __init__(self, level="Trung bình"):
        self.llm = get_llm(temperature=0.8) # Tăng randomness để đa dạng hành vi
        self.level = level
        self.persona_prompt = self._get_persona(level)

    def _get_persona(self, level):
        personas = {
            "Giỏi": "Bạn là học sinh xuất sắc. Bạn LUÔN LUÔN chủ động tính toán và đưa ra biểu thức toán học khi thầy gợi mở.",
            "Khá": "Bạn nắm khá vững kiến thức nhưng đôi khi cần thầy nhắc nhở mới gõ đúng công thức LaTeX.",
            "Trung bình": "Bạn thường bế tắc nhưng sẽ cố gắng tính toán các con số nhỏ khi thầy yêu cầu.",
            "Yêu": "Bạn sợ toán và hay tính sai, nhưng vẫn sẽ gõ ra các con số hoặc phép tính cơ bản."
        }
        return personas.get(level, personas["Trung bình"])

    async def respond(self, history):
        system_msg = (
            f"{self.persona_prompt}\n"
            "NHIỆM VỤ QUAN TRỌNG:\n"
            "1. Nếu thầy yêu cầu tính toán, bạn PHẢI thực hiện phép tính và đưa ra kết quả hoặc biểu thức (ví dụ: 'Dạ là 1/2 ạ' hoặc 'Dạ có 6 trường hợp').\n"
            "2. KHÔNG ĐƯỢC chỉ hỏi 'Làm gì tiếp theo' nếu thầy đã đưa ra câu hỏi cụ thể.\n"
            "3. LUÔN LUÔN dùng tiếng Việt và xưng hô Em - Thầy.\n"
            "4. Sử dụng LaTeX cho công thức toán học nếu cần.\n"
        )
        
        response = await self.llm.ainvoke([SystemMessage(content=system_msg)] + history)
        content = response.content.strip()
        
        # Nếu output quá ngắn hoặc chỉ hỏi ngược, dùng fallback chủ động hơn
        if len(content) < 5 or "tiếp theo" in content.lower():
            import random
            fallbacks = [
                "Dạ để em tính thử... có phải là 1/2 không ạ?",
                "Em nghĩ không gian mẫu là 6, đúng không thầy?",
                "Dạ em đang tính, thầy chờ em một xíu nhé.",
                "Em nghĩ là dùng quy tắc nhân, kết quả là 1/4 ạ?"
            ]
            # Chỉ dùng fallback nếu content thực sự vô nghĩa
            if len(content) < 5:
                return random.choice(fallbacks)
            
        return content
