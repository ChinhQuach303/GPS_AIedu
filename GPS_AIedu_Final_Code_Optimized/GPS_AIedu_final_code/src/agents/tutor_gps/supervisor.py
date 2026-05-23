
import json
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.tutor_gps.state import AgentState
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
        
        # --- CƠ CHẾ CHỐNG KẸT (ANTI-STAGNATION) ---
        # Nếu đã ở cùng một trạng thái trong 3 lượt liên tiếp, ép chuyển node
        if len(trace_labels) >= 3:
            last_3 = [str(t)[0] for t in trace_labels[-3:]]
            if last_3[0] == last_3[1] == last_3[2]:
                stuck_node = last_3[0]
                if stuck_node == 'P' and next_agent == 'practice':
                    print("⚠️ Supervisor: Phát hiện kẹt ở Practice. Ép chuyển sang Solve.")
                    next_agent = "solve"
                elif stuck_node == 'G' and next_agent == 'guide':
                    print("⚠️ Supervisor: Phát hiện kẹt ở Guide. Ép chuyển sang Practice.")
                    next_agent = "practice"
        # ------------------------------------------

        
        return {
            "current_intent": next_agent,
            "active_agent": "supervisor",
            "metadata": {"supervisor_latency": latency, "intent_category": intent_cat}
        }
    except Exception as e:
        print(f"⚠️ Error parsing supervisor output: {e}. Content: {content[:100]}...")
        return {"current_intent": "guide", "active_agent": "supervisor"}
