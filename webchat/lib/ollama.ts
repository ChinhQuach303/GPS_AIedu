import { ChatMessage } from "./types";
import { fetchWithTimeout } from "./fetchWithTimeout";

type OllamaChatResponse = {
  message?: { role?: string; content?: string };
};

export async function generateWithOllama(params: {
  systemPrompt: string;
  history: ChatMessage[];
  message: string;
}): Promise<string> {
  const baseUrl = (process.env.OLLAMA_BASE_URL || "http://127.0.0.1:11434").replace(/\/+$/, "");
  // Default to a small math-tuned model for weak machines.
  const model = process.env.OLLAMA_MODEL || "qwen2-math:1.5b-instruct-q5_K_M";
  const timeoutMs = Number(process.env.OLLAMA_TIMEOUT_MS || process.env.LLM_TIMEOUT_MS || 120_000);

  const url = `${baseUrl}/api/chat`;
  const messages = [
    { role: "system", content: params.systemPrompt },
    ...params.history.map((m) => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.content })),
    { role: "user", content: params.message }
  ];

  const response = await fetchWithTimeout(
    url,
    {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      model,
      stream: false,
      messages,
      options: {
        temperature: 0.4
      }
    })
    },
    timeoutMs
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`Ollama API error: ${response.status} ${text}`);
  }

  const data = (await response.json()) as OllamaChatResponse;
  const content = data.message?.content;
  if (!content) throw new Error("Ollama API returned empty response.");
  return content;
}
