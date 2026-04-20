import { ChatMessage } from "./types";
import { generateWithOpenAI, generateWithOpenAIStream } from "./openai";
import { generateWithOllama } from "./ollama";

export async function generateReply(params: {
  systemPrompt: string;
  history: ChatMessage[];
  message: string;
}): Promise<{ provider: string; reply: string }> {
  const provider = (process.env.LLM_PROVIDER || "openai").trim().toLowerCase();

  if (provider === "ollama") {
    const reply = await generateWithOllama(params);
    return { provider, reply };
  }

  if (provider === "langgraph") {
    const res = await fetch("http://127.0.0.1:8001/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
            message: params.message,
            qid: "1", // Trong thực tế lấy từ context/session
            history: params.history
        })
    });
    const data = await res.json();
    return { provider, reply: data.reply || "Error calling LangGraph" };
  }

  if (provider === "vllm" || provider === "openai") {
    const reply = await generateWithOpenAI(params);
    return { provider: provider, reply };
  }

  // default: openai
  const reply = await generateWithOpenAI(params);
  return { provider: "openai", reply };
}

export async function generateReplyStream(params: {
  systemPrompt: string;
  history: ChatMessage[];
  message: string;
}): Promise<{ provider: string; stream: ReadableStream<Uint8Array>; replyPromise: Promise<string>; streamed: boolean }> {
  const provider = (process.env.LLM_PROVIDER || "openai").trim().toLowerCase();

  if (provider === "ollama") {
    const reply = await generateWithOllama(params);
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(reply));
        controller.close();
      }
    });
    return { provider, stream, replyPromise: Promise.resolve(reply), streamed: false };
  }

  if (provider === "vllm" || provider === "openai") {
    const { stream, replyPromise } = await generateWithOpenAIStream(params);
    return { provider, stream, replyPromise, streamed: true };
  }

  // Fallback to OpenAI
  const { stream, replyPromise } = await generateWithOpenAIStream(params);
  return { provider: "openai", stream, replyPromise, streamed: true };
}
