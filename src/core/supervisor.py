
import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.state import AgentState
from src.utils.llm_factory import get_llm

llm = get_llm(temperature=0.1) # Giảm temperature để phân loại intent chính xác hơn

def load_prompt(filename):
    with open(f"config/prompts/{filename}", "r", encoding="utf-8") as f:
        return f.read().strip()

import time

async def supervisor_node(state: AgentState) -> dict:
    """
    Phân loại intent đa tầng và đo lường hiệu năng.
    """
    trace_labels = state.get("trace_labels", [])
    
    # LUẬT CỨNG: Lượt đầu tiên luôn là Guide
    if not trace_labels:
        return {"current_intent": "guide", "active_agent": "supervisor"}

    prompt_content = load_prompt("supervisor.txt")
    prompt = SystemMessage(content=prompt_content)
    
    # Đo lường Latency
    start_time = time.time()
    
    # Ép model tập trung vào JSON và tiếng Việt bằng cách thêm chỉ dẫn cuối cùng
    instruction = HumanMessage(content="Hãy trả về kết quả phân loại dưới định dạng JSON ngay lập tức. BẮT BUỘC dùng tiếng Việt cho phần 'reason'. Tuyệt đối không dùng tiếng Trung. Không viết gì thêm.")
    response = await llm.ainvoke([prompt] + list(state["messages"]) + [instruction])
    latency = time.time() - start_time
    
    content = response.content
    
    try:
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
            
        result = json.loads(content)
        next_agent = result.get("next_agent", "guide")
        intent_cat = result.get("intent_category", "understanding")
        
        return {
            "current_intent": next_agent,
            "active_agent": "supervisor",
            "metadata": {"supervisor_latency": latency, "intent_category": intent_cat}
        }
    except Exception as e:
        print(f"⚠️ Error parsing supervisor output: {e}. Content: {content[:100]}...")
        return {"current_intent": "guide", "active_agent": "supervisor"}
