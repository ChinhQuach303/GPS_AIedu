
import json
import re
from src.utils.llm_factory import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class CognitiveJudge:
    def __init__(self):
        self.llm = get_llm(temperature=0) # Judge phải cực kỳ khách quan
        
    async def evaluate_session(self, dialogue_text):
        """
        Đánh giá ngữ nghĩa một phiên hội thoại.
        """
        prompt = (
            "Bạn là một chuyên gia khảo thí giáo dục toán học. Hãy đánh giá đoạn hội thoại giữa AI (Thầy) và Học sinh.\n"
            "Tiêu chí chấm điểm:\n"
            "1. spoon_feeding_rate: (0.0 đến 1.0) AI có cho đáp số ngay lập tức hoặc giải hộ các bước mà học sinh chưa thử làm không?\n"
            "2. student_mastery_score: (0-100) Dựa trên các phản hồi cuối cùng, học sinh có thực sự nắm được cách giải không?\n"
            "3. pedagogical_quality: (0-10) Đánh giá tổng quát mức độ dẫn dắt của AI.\n\n"
            "Đoạn hội thoại:\n"
            f"{dialogue_text[:3000]}\n\n"
            "CHỈ TRẢ VỀ JSON: {\"spoon_feeding_rate\": float, \"student_mastery_score\": int, \"pedagogical_quality\": int, \"reason\": \"string\"}"
        )
        
        try:
            resp = await self.llm.ainvoke([SystemMessage(content=prompt)])
            # Trích xuất JSON bằng regex để an toàn
            match = re.search(r'\{.*\}', resp.content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            print(f"Error judging session: {e}")
            return None

async def process_evaluation(input_csv, output_csv):
    """
    Đọc dữ liệu authentic và chạy Judge để gán nhãn điểm số thật.
    """
    import pandas as pd
    df = pd.read_csv(input_csv)
    judge = CognitiveJudge()
    
    print(f"⚖️ Đang bắt đầu chấm điểm ngữ nghĩa cho {len(df)} phiên...")
    
    results = []
    for i, row in df.iterrows():
        eval_data = await judge.evaluate_session(row["Dialogue"])
        if eval_data:
            row_result = {**row.to_dict(), **eval_data}
            results.append(row_result)
        
        if (i+1) % 10 == 0:
            print(f"✅ Đã chấm xong {i+1} phiên...")
            pd.DataFrame(results).to_csv(output_csv, index=False)
            
    print(f"🎉 Hoàn thành chấm điểm! Kết quả tại: {output_csv}")
