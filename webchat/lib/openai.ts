import { ChatMessage } from "./types";
import { fetchWithTimeout } from "./fetchWithTimeout";

type OpenAIChatCompletionsResponse = {
  choices?: Array<{
    message?: { content?: string };
  }>;
  error?: { message?: string };
};

export async function generateWithOpenAI(params: {
  systemPrompt: string;
  history: ChatMessage[];
  message: string;
}): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("Missing OPENAI_API_KEY.");

  const model = process.env.OPENAI_MODEL || "gpt-4o-mini";
  const baseUrl = (process.env.OPENAI_BASE_URL || "https://api.openai.com/v1").replace(/\/+$/, "");
  const timeoutMs = Number(process.env.OPENAI_TIMEOUT_MS || process.env.LLM_TIMEOUT_MS || 60_000);

  const messages = [
    { role: "system", content: params.systemPrompt },
    ...params.history.map((m) => ({
      role: m.role === "assistant" ? "assistant" : "user",
      content: m.content
    })),
    { role: "user", content: params.message }
  ];

  const response = await fetchWithTimeout(
    `${baseUrl}/chat/completions`,
    {
      method: "POST",
      headers: {
        authorization: `Bearer ${apiKey}`,
        "content-type": "application/json"
      },
      body: JSON.stringify({
        model,
        messages,
        temperature: 0.4,
        max_tokens: 700
      })
    },
    timeoutMs
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`OpenAI API error: ${response.status} ${text}`);
  }

  const data = (await response.json()) as OpenAIChatCompletionsResponse;
  const content = data.choices?.[0]?.message?.content;
  if (!content) {
    throw new Error(`OpenAI API returned empty response.${data.error?.message ? " " + data.error.message : ""}`);
  }
  return content;
}
