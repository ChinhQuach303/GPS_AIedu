
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Luồng tin nhắn hội thoại
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Intent hiện tại của học sinh và Agent đang xử lý
    current_intent: str
    active_agent: str
    
    # Nhãn chi tiết cho từng lượt thoại (e.g., [G], [P1], [P2])
    trace_labels: list[str]
    
    # Kết quả xác thực từng bước (True/False)
    step_history: list[dict]
    
    # Trình độ và ID học sinh
    student_level: str
    student_id: str
    
    # Dữ liệu hiệu năng (Latency, Tokens)
    metadata: dict
