import pandas as pd
import json
import asyncio
from src.evaluation.metrics.math_verifier import MathVerifier
from src.utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

import os

# Thêm path hiện tại để tránh lỗi import khi chạy
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def classify_failure(dialogue, llm):
    """
    Sử dụng LLM để dán nhãn loại lỗi dựa trên nội dung hội thoại bị fail.
    """
    prompt = """
    Bạn là một nhà nghiên cứu giáo dục. Hãy phân tích đoạn hội thoại gia sư Toán này và phân loại nó vào 1 trong 3 nhóm lỗi sau:
    1. ROUTING_ERROR: Thầy (Tutor) chuyển trạng thái sai. Ví dụ: Học sinh đã làm xong tính toán nhưng Thầy vẫn bắt làm lại, hoặc Thầy kết thúc bài quá sớm khi học sinh chưa hiểu.
    2. SCAFFOLDING_PRESSURE: Thầy chia bước quá nhỏ, hỏi quá dai dẳng, ép buộc học sinh phải tính những cái cơ bản không cần thiết, khiến học sinh bị mắc kẹt hoặc chán nản.
    3. MATH_HALLUCINATION: Bản thân Thầy tính sai, đưa ra công thức sai, hoặc bảo học sinh tính sai dù học sinh đã làm đúng.
    
    Hãy trả về ĐÚNG MỘT TỪ KHOÁ tương ứng: ROUTING_ERROR, SCAFFOLDING_PRESSURE, hoặc MATH_HALLUCINATION.
    Nếu không rõ ràng, trả về OTHER.
    """
    
    try:
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=dialogue[-2000:]) # Cắt bớt nếu quá dài
        ]
        response = await llm.ainvoke(messages)
        content = response.content.strip().upper()
        
        if "ROUTING_ERROR" in content: return "ROUTING_ERROR"
        if "SCAFFOLDING_PRESSURE" in content: return "SCAFFOLDING_PRESSURE"
        if "MATH_HALLUCINATION" in content: return "MATH_HALLUCINATION"
        return "OTHER"
    except Exception as e:
        print(f"LLM Classification Error: {e}")
        return "ERROR"

async def main():
    input_file = "data/outputs/cleaned_massive_results.csv"
    output_file = "data/outputs/failure_cases_analysis.csv"
    
    if not os.path.exists(input_file):
        print(f"❌ File không tồn tại: {input_file}")
        return
        
    print(f"🔍 Đang nạp dữ liệu từ {input_file}...")
    df = pd.read_csv(input_file)
    
    verifier = MathVerifier()
    llm = get_llm(temperature=0.0) # Nhiệt độ 0 để phân loại chính xác
    
    failures = []
    
    print("⚙️ Bắt đầu quét các anomaly sessions...")
    
    # Chỉ quét 500 dòng đầu để tiết kiệm thời gian chạy mẫu, bạn có thể xóa [:500] để quét toàn bộ
    for idx, row in df.head(500).iterrows():
        dialogue = str(row.get("dialogue", ""))
        if not dialogue or dialogue == "nan":
            continue
            
        # Đếm lượt (số dòng bắt đầu bằng Thầy: hoặc Em:)
        turns = sum(1 for line in dialogue.split('\n') if line.strip().startswith("Thầy:") or line.strip().startswith("Em:"))
        
        # Tính VAI
        vai_result = verifier.calculate_vai(dialogue)
        vai_score = vai_result.get("vai", 0.0) if isinstance(vai_result, dict) else 0.0
        
        # Đánh giá tiêu chí
        is_loop = turns > 15
        is_low_autonomy = vai_score < 0.2
        
        if is_loop or is_low_autonomy:
            print(f"  -> Phát hiện lỗi tại Session {idx}: Turns={turns}, VAI={vai_score:.2f}")
            
            # Phân loại nguyên nhân bằng LLM
            failure_type = await classify_failure(dialogue, llm)
            
            failures.append({
                "original_index": idx,
                "student_level": row.get("student_level", "Unknown"),
                "turns": turns,
                "vai": vai_score,
                "trigger": "LOOP" if is_loop else "LOW_AUTONOMY",
                "failure_type": failure_type,
                "dialogue": dialogue
            })
            
    if failures:
        out_df = pd.DataFrame(failures)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        out_df.to_csv(output_file, index=False)
        print(f"✅ Đã quét xong! Tìm thấy {len(failures)} sessions lỗi.")
        print(f"Lưu báo cáo tại: {output_file}")
        
        # In ra thống kê nhỏ
        print("\n📊 Thống kê lỗi:")
        print(out_df["failure_type"].value_counts())
    else:
        print("✅ Đã quét xong! Không tìm thấy sessions lỗi nào theo tiêu chí trên.")

if __name__ == "__main__":
    asyncio.run(main())
