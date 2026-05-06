
from src.utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class SingleAgentTutor:
    def __init__(self):
        self.llm = get_llm()
        self.system_prompt = (
            "Bạn là một gia sư dạy toán tận tâm và hữu ích. "
            "Nhiệm vụ của bạn là hỗ trợ học sinh giải các bài toán một cách chi tiết và dễ hiểu. "
            "Bạn có thể giải thích lý thuyết, đưa ra các bước giải và cung cấp đáp án khi cần thiết để học sinh nắm bắt được vấn đề. "
            "Hãy trả lời một cách tự nhiên, thân thiện. "
            "Sử dụng tiếng Việt và LaTeX cho các biểu thức toán học. "
            "BẮT BUỘC dùng tiếng Việt. TUYỆT ĐỐI KHÔNG dùng tiếng Trung."
        )

    async def chat(self, messages):
        sys_msg = SystemMessage(content=self.system_prompt)
        response = await self.llm.ainvoke([sys_msg] + messages)
        return response
