from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from gps_langgraph import app as langgraph_app

server = FastAPI(title="GPS AIedu LangGraph Bridge")

class ChatInput(BaseModel):
    message: str
    qid: str
    history: List[dict] = []

@server.post("/chat")
async def chat_endpoint(data: ChatInput):
    """
    Điểm cuối kết nối Next.js với LangGraph
    """
    try:
        # Thực thi đồ thị LangGraph
        result = langgraph_app.invoke({
            "student_msg": data.message,
            "qid": data.qid,
            "history": data.history
        })
        
        return {
            "ok": True,
            "reply": result.get("response", "Thầy không thể xử lý yêu cầu này ngay lúc này."),
            "intent": result.get("intent", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Chạy trên port 8001 để không đụng hàng với Next.js (3000)
    uvicorn.run(server, host="127.0.0.1", port=8001)
