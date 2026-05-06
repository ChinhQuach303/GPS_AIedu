
import asyncio
import time
from src.core.graph import gps_tutor_app
from langchain_core.messages import HumanMessage

async def run_single_simulation(student_id, question, thread_id):
    """
    Chạy một phiên hội thoại Multi-Agent thực tế.
    """
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "student_id": student_id,
        "student_level": "Trung bình",
        "trace_labels": [],
        "metadata": {}
    }
    
    start_time = time.time()
    # Chạy 1 lượt (lượt Guide đầu tiên)
    async for event in gps_tutor_app.astream(initial_state, config):
        pass # Chúng ta chỉ cần đo lường khả năng xử lý của graph
    
    latency = time.time() - start_time
    return latency

async def main():
    CONCURRENCY = 5 # Số lượng học sinh đồng thời
    question = "Gieo đồng tiền 4 lần, tính xác suất 4 lần sấp?"
    
    print(f"🚀 Bắt đầu Benchmark Scalability với {CONCURRENCY} học sinh song song...")
    
    tasks = []
    for i in range(CONCURRENCY):
        tasks.append(run_single_simulation(f"STUDENT_{i}", question, f"THREAD_{i}"))
    
    start_all = time.time()
    latencies = await asyncio.gather(*tasks)
    total_duration = time.time() - start_all
    
    print(f"\n📊 --- KẾT QUẢ BENCHMARK ---")
    print(f"✅ Tổng số phiên xử lý song song: {CONCURRENCY}")
    print(f"⏱️ Tổng thời gian: {total_duration:.2f}s")
    print(f"🚀 Throughput: {CONCURRENCY/total_duration*60:.2f} phiên/phút")
    print(f"⚡ Latency trung bình: {sum(latencies)/len(latencies):.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
