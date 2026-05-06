
import json
import os
import pandas as pd
import asyncio
import time
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

# --- GPU OPTIMIZED CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/v1"
MODEL = "qwen2.5:7b"
OUTPUT_FILE = "data/processed/gpu_augmented_conversations.csv"
CONCURRENCY = 2 # Reduced for stability, increase slowly

llm = ChatOpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama",
    model=MODEL,
    temperature=0.7,
    timeout=120
)

# --- REUSE LOGIC FROM ORIGINAL SCRIPT ---
def get_persona_distribution(total=30):
    dist = {"Giỏi": 4, "Khá": 10, "Trung bình": 12, "Yêu": 4}
    personas = []
    idx = 1
    for level, count in dist.items():
        for _ in range(count):
            personas.append({
                "id": f"GPU_S_{idx:02d}",
                "level": level,
                "behavior": f"Bạn là học sinh lớp 12 có học lực {level}. " + 
                            ("Bạn giải bài rất nhanh và tự tin." if level == "Giỏi" else 
                             "Bạn hiểu bài nhưng cần thầy hướng dẫn các bước khó." if level == "Khá" else
                             "Bạn hay quên công thức và cần thầy nhắc lại khái niệm." if level == "Trung bình" else
                             "Bạn rất sợ toán xác suất, thường xuyên bế tắc.")
            })
            idx += 1
    return personas

def generate_prompt(persona, q, s_type):
    if s_type == "gps":
        return (
            f"Hãy viết một KỊCH BẢN hội thoại đầy đủ giữa THẦY và EM về bài toán sau:\n"
            f"Bài toán: {q['question']}\n"
            f"Học sinh ({persona['level']}): {persona['behavior']}\n\n"
            f"KỊCH BẢN PHẢI TUÂN THỦ CẤU TRÚC SAU:\n"
            f"Thầy: [G] (Hướng dẫn gợi mở đầu buổi)\n"
            f"Em: (Trả lời)\n"
            f"Thầy: [P] (Yêu cầu em tính toán bước 1)\n"
            f"Em: (Tính toán)\n"
            f"Thầy: [P] (Yêu cầu em tính toán bước 2 hoặc sửa lỗi)\n"
            f"Em: (Tính toán xong)\n"
            f"Thầy: [S] (Chốt đáp án cuối cùng và giải thích ngắn gọn)\n"
            f"Em: (Cảm ơn thầy)\n\n"
            f"YÊU CẦU: Chỉ dùng tiếng Việt. Viết toàn bộ các lượt thoại trên trong 1 lần trả lời duy nhất. Không được bỏ sót bước [P] và [S]."
        )
    else:
        return f"Kịch bản ngắn:\nThầy: Giải chi tiết bài {q['question']}\nEm: Cảm ơn thầy."

async def process_session(q, s, s_type, semaphore, pbar):
    async with semaphore:
        prompt = generate_prompt(s, q, s_type)
        try:
            start = time.perf_counter()
            resp = await llm.ainvoke([SystemMessage(content=prompt)])
            latency = time.perf_counter() - start
            pbar['count'] += 1
            print(f"✅ [{pbar['count']}/{pbar['total']}] Latency: {latency:.2f}s | Group: {s_type}")
            return {
                "Group": "GPS" if s_type == "gps" else "Non-GPS",
                "Student_ID": s['id'],
                "Level": s['level'],
                "QID": q['id'],
                "Dialogue": resp.content
            }
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

async def main():
    personas = get_persona_distribution(30)
    with open("data/processed/probabilities_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)[:5] # Test with 5 questions for benchmark
    
    tasks_to_run = []
    for q in questions:
        for s in personas:
            tasks_to_run.append((q, s, "gps"))
    
    total = len(tasks_to_run)
    pbar = {'count': 0, 'total': total}
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    print(f"🚀 Starting GPU Acceleration Benchmark (Target: {total} sessions)")
    start_time = time.perf_counter()
    
    # Process in batches of 10 to save incrementally
    all_valid_results = []
    batch_size = 10
    
    for i in range(0, total, batch_size):
        batch_tasks = tasks_to_run[i:i + batch_size]
        tasks = [process_session(q, s, st, semaphore, pbar) for q, s, st in batch_tasks]
        results = await asyncio.gather(*tasks)
        
        valid_results = [r for r in results if r is not None]
        all_valid_results.extend(valid_results)
        
        # Save incrementally
        df_batch = pd.DataFrame(valid_results)
        mode = 'a' if i > 0 else 'w'
        header = True if i == 0 else False
        df_batch.to_csv(OUTPUT_FILE, mode=mode, index=False, header=header)
        # print(f"💾 Saved batch {i//batch_size + 1}. Total: {len(all_valid_results)}")
    
    duration = time.perf_counter() - start_time
    
    if all_valid_results:
        print(f"\n📊 --- BENCHMARK RESULT ---")
        print(f"✅ Sessions Generated: {len(all_valid_results)}")
        print(f"⏱️ Total Time: {duration:.2f}s")
        print(f"🚀 Throughput: {len(all_valid_results)/duration*60:.2f} sessions/min")
        print(f"💾 Final dataset at {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
