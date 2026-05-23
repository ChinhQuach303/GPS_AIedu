
from langchain_openai import ChatOpenAI

def get_llm(temperature=0.1): # Giảm temperature xuống tối đa để tránh sáng tạo ngôn ngữ
    """
    Khởi tạo và trả về instance của LLM (Ollama).
    """
    return ChatOpenAI(
        model="qwen2.5:7b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        temperature=temperature,
        timeout=120,
        model_kwargs={
            "stop": ["<|im_start|>", "<|im_end|>", "练习中文", "老师：", "Chinese", "中文", "提问"],
        }
    )
