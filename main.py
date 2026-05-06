
import asyncio
from src.core.graph import gps_tutor_app
from langchain_core.messages import HumanMessage

async def chat_with_tutor(user_input: str, thread_id: str = "test_1", student_level: str = "Trung bình", student_id: str = "S001"):
    """
    Hàm giao tiếp chính với hệ thống Multi-Agent GPS.
    """
    # Khởi tạo trạng thái đúng theo AgentState schema
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "trace_labels": [],
        "student_level": student_level,
        "student_id": student_id,
        "current_intent": "",
        "active_agent": "",
        "step_history": [],
        "metadata": {}
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    async for event in gps_tutor_app.astream(initial_state, config):
        for node_name, output in event.items():
            if node_name != "supervisor" and "messages" in output:
                labels = output.get("trace_labels", [])
                label = labels[-1] if labels else node_name
                print(f"\n--- Agent: {output.get('active_agent', node_name)} | Label: [{label}] ---")
                print(output["messages"][-1].content)

if __name__ == "__main__":
    question = "Bài toán: Gieo đồng tiền 4 lần. Tính xác suất để cả 4 lần ra mặt sấp?"
    asyncio.run(chat_with_tutor(question))
