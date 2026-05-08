import os
from langchain_core.messages import SystemMessage, HumanMessage
from src.utils.llm_factory import get_llm

class SingleAgentTutor:
    def __init__(self):
        # Sử dụng cùng một model cấu hình như GPS-Agent
        self.llm = get_llm(temperature=0.1)
        
        prompt_path = "config/prompts/single_agent_baseline.txt"
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Missing prompt file at {prompt_path}")
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read().strip()

    async def ainvoke(self, messages):
        """
        Xử lý hội thoại một cách tuyến tính, không có routing.
        """
        prompt = SystemMessage(content=self.system_prompt)
        lang_remind = HumanMessage(content="BẮT BUỘC trả lời bằng tiếng Việt. TUYỆT ĐỐI KHÔNG dùng tiếng Trung.")
        
        # Nạp toàn bộ lịch sử tin nhắn cùng với system prompt
        full_messages = [prompt] + messages + [lang_remind]
        
        response = await self.llm.ainvoke(full_messages)
        return response.content

