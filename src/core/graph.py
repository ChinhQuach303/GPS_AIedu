
from langgraph.graph import StateGraph, END
from src.core.state import AgentState
from src.core.nodes.gps_nodes import guide_node, practice_node, solve_node
from src.core.supervisor import supervisor_node

from langgraph.checkpoint.memory import MemorySaver

def create_gps_graph():
    # Khởi tạo bộ nhớ (In-memory State Persistence)
    memory = MemorySaver()
    
    workflow = StateGraph(AgentState)
    
    # Thêm các Nodes
    workflow.add_node("guide", guide_node)
    workflow.add_node("practice", practice_node)
    workflow.add_node("solve", solve_node)
    workflow.add_node("supervisor", supervisor_node)
    
    # Luồng điều hướng động
    workflow.set_entry_point("supervisor")
    
    # Supervisor quyết định đi đâu tiếp theo
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["current_intent"],
        {
            "guide": "guide",
            "practice": "practice",
            "solve": "solve",
            "__end__": END
        }
    )
    
    # Sau mỗi agent, kết thúc lượt để chờ input mới từ học sinh
    workflow.add_edge("guide", END)
    workflow.add_edge("practice", END)
    workflow.add_edge("solve", END)
    
    return workflow.compile(checkpointer=memory)

# Khởi tạo instance của graph
gps_tutor_app = create_gps_graph()
