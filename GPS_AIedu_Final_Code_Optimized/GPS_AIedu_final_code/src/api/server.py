from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from src.gps_multiagent_graph import run_tutor
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

app = FastAPI(title="GPS Tutor Brain API")

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    qid: str
    message: str
    history: List[ChatMessage] = []
    student_level: str = "Trung bình"

class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str] = None

def convert_history(history: List[ChatMessage]) -> List[BaseMessage]:
    converted = []
    for msg in history:
        if msg.role == "user":
            converted.append(HumanMessage(content=msg.content))
        else:
            converted.append(AIMessage(content=msg.content))
    return converted

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        history = convert_history(request.history)
        # Use the multi-agent graph to generate reply
        # Note: run_tutor currently returns just the content. 
        # We might want to modify it to return the full state if we need more info.
        reply = run_tutor(request.qid, request.message, history)
        
        # Simple intent extraction from reply if [G], [P], [S] are present
        intent = "G"
        if "[P]" in reply: intent = "P"
        elif "[S]" in reply: intent = "S"
        
        return ChatResponse(reply=reply, intent=intent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
