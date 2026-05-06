
import asyncio
import json
from src.core.graph import gps_tutor_app
from src.core.baseline_agent import SingleAgentTutor
from langchain_core.messages import HumanMessage, AIMessage

async def test_multi_agent(question):
    print("\n🚀 --- TESTING MULTI-AGENT GPS ---")
    state = {
        "messages": [HumanMessage(content=question)],
        "gps_history": [],
        "student_level": "Trung bình",
        "question_id": "TEST_Q"
    }
    
    # Giả lập 3 lượt hội thoại
    for turn in range(3):
        print(f"\n[Turn {turn+1}]")
        config = {"configurable": {"thread_id": "test_multi"}}
        
        # Lấy kết quả cuối cùng từ stream
        final_output = None
        async for event in gps_tutor_app.astream(state, config):
            for node_name, output in event.items():
                if node_name != "supervisor":
                    final_output = output
                    print(f"Node: {node_name} | Response: {output['messages'][-1].content[:100]}...")
        
        if final_output:
            state["messages"].append(final_output["messages"][-1])
            state["gps_history"] = final_output.get("gps_history", [])
            
        # Giả lập học sinh trả lời đơn giản để AI đi tiếp
        student_reply = "Dạ em đã hiểu, bước tiếp theo là gì ạ?" if turn < 2 else "Dạ em tính ra là 1/16 ạ."
        state["messages"].append(HumanMessage(content=student_reply))

async def test_single_agent(question):
    print("\n🚀 --- TESTING SINGLE-AGENT BASELINE ---")
    tutor = SingleAgentTutor()
    messages = [HumanMessage(content=question)]
    
    for turn in range(3):
        print(f"\n[Turn {turn+1}]")
        response = await tutor.chat(messages)
        print(f"Response: {response.content[:100]}...")
        messages.append(response)
        
        student_reply = "Dạ em đã hiểu, bước tiếp theo là gì ạ?" if turn < 2 else "Dạ em tính ra là 1/16 ạ."
        messages.append(HumanMessage(content=student_reply))

async def main():
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    sample_q = questions[0]["question"] # Lấy câu 1: Gieo đồng tiền 4 lần
    print(f"Target Question: {sample_q}")
    
    await test_multi_agent(sample_q)
    await test_single_agent(sample_q)

if __name__ == "__main__":
    asyncio.run(main())
