import pandas as pd
import asyncio
import os
import re
from sklearn.metrics import cohen_kappa_score
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

async def get_llm_score(llm, dialogue):
    """
    Sử dụng LLM để dán nhãn điểm từ 1 đến 5 cho mức độ Tự chủ của học sinh.
    """
    prompt = """
    Bạn là một chuyên gia đánh giá sư phạm. Hãy đọc kỹ đoạn hội thoại sau giữa Thầy (Gia sư Toán) và Em (Học sinh).
    
    Hãy chấm điểm mức độ "Tự chủ của học sinh" (Student Autonomy) trên thang điểm từ 1 đến 5:
    1: Học sinh hoàn toàn thụ động, Thầy tự giải toàn bộ bài toán.
    2: Học sinh có tham gia một chút nhưng Thầy vẫn làm phần lớn công việc.
    3: Học sinh thực hiện được các phép tính cơ bản theo hướng dẫn chi tiết của Thầy.
    4: Học sinh hiểu vấn đề và tự thực hiện được nhiều bước giải quyết quan trọng.
    5: Học sinh hoàn toàn làm chủ bài toán, tự suy luận và tự giải quyết dưới sự hướng dẫn rất nhỏ của Thầy.
    
    LUẬT BẮT BUỘC: Bạn CHỈ ĐƯỢC PHÉP trả về MỘT CHỮ SỐ DUY NHẤT (1, 2, 3, 4, hoặc 5). Không giải thích, không viết thêm bất kỳ chữ nào khác.
    """
    
    try:
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=dialogue)
        ]
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        
        # Tìm số đầu tiên xuất hiện trong kết quả (đề phòng LLM vẫn cố giải thích)
        match = re.search(r'[1-5]', content)
        if match:
            return int(match.group())
        return 3 # Mặc định nếu không tìm thấy
    except Exception as e:
        print(f"Lỗi chấm điểm: {e}")
        return 3

async def main():
    input_file = "data/outputs/cleaned_massive_results.csv"
    output_file = "data/outputs/irr_scores.csv"
    
    if not os.path.exists(input_file):
        print(f"❌ File không tồn tại: {input_file}")
        return
        
    print(f"🔍 Đang nạp dữ liệu từ {input_file}...")
    df = pd.read_csv(input_file)
    
    # Lấy 100 sessions ngẫu nhiên
    sample_size = min(100, len(df))
    test_df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    
    # Khởi tạo 2 giám khảo bằng ChatOpenAI (API compatible with Ollama)
    rater_a = ChatOpenAI(model="qwen2.5:7b", base_url="http://localhost:11434/v1", api_key="ollama", temperature=0.0, timeout=120)
    rater_b = ChatOpenAI(model="phi3:mini", base_url="http://localhost:11434/v1", api_key="ollama", temperature=0.0, timeout=120)
    
    scores_a = []
    scores_b = []
    
    print(f"⚖️ Bắt đầu phiên tòa chấm điểm chéo cho {sample_size} sessions...")
    
    for idx, row in test_df.iterrows():
        dialogue = str(row.get("dialogue", ""))
        # Tránh đưa văn bản quá dài vào LLM
        truncated_dialogue = dialogue[-2000:] 
        
        print(f"  - Đang chấm Session {idx+1}/{sample_size} (ID: {row.get('session_id', idx)})")
        
        score_a = await get_llm_score(rater_a, truncated_dialogue)
        scores_a.append(score_a)
        
        score_b = await get_llm_score(rater_b, truncated_dialogue)
        scores_b.append(score_b)
        
    # Thêm cột điểm vào DataFrame
    test_df["score_rater_A_qwen"] = scores_a
    test_df["score_rater_B_phi3"] = scores_b
    
    # Lưu kết quả
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    test_df.to_csv(output_file, index=False)
    
    # Tính Cohen's Kappa có trọng số (phù hợp cho điểm Likert)
    kappa = cohen_kappa_score(scores_a, scores_b, weights='quadratic')
    
    print("\n" + "="*50)
    print("KẾT QUẢ INTER-RATER RELIABILITY (IRR)")
    print("="*50)
    print(f"🔹 Số lượng mẫu đánh giá: {sample_size} sessions")
    print(f"🔹 Giám khảo A: Qwen-2.5-7B")
    print(f"🔹 Giám khảo B: Phi-3-mini (3.8B)")
    print(f"🔹 Quadratic Weighted Cohen's Kappa: {kappa:.3f}")
    print("="*50)
    
    if kappa < 0.2:
        print("Nhận xét: Mức độ đồng thuận KÉM.")
    elif kappa < 0.4:
        print("Nhận xét: Mức độ đồng thuận TẠM ĐƯỢC (Fair).")
    elif kappa < 0.6:
        print("Nhận xét: Mức độ đồng thuận VỪA PHẢI (Moderate).")
    elif kappa < 0.8:
        print("Nhận xét: Mức độ đồng thuận ĐÁNG KỂ (Substantial) -> CHUẨN MỰC BÀI BÁO!")
    else:
        print("Nhận xét: Mức độ đồng thuận HOÀN HẢO (Almost perfect).")

if __name__ == "__main__":
    asyncio.run(main())
