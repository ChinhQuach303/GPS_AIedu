import { ChatMessage } from "./types";
import { fetchWithTimeout } from "./fetchWithTimeout";
import { OpenAIStream } from "ai";
import { getOpenAIApiKey, getOpenAIBaseUrl, getOpenAIModelName } from "./env";

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
  const apiKey = getOpenAIApiKey();
  if (!apiKey) throw new Error("Missing OPENAI_API_KEY.");

  const model = getOpenAIModelName();
  const baseUrl = getOpenAIBaseUrl();
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
        max_tokens: 700,
        frequency_penalty: 1.1,
        presence_penalty: 1.1,
        stop: ["<|im_end|>", "<|endoftext|>"]
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

export async function generateWithOpenAIStream(params: {
  systemPrompt: string;
  history: ChatMessage[];
  message: string;
}): Promise<{ stream: ReadableStream<Uint8Array>; replyPromise: Promise<string> }> {
  const apiKey = getOpenAIApiKey();
  if (!apiKey) throw new Error("Missing OPENAI_API_KEY.");

  const model = getOpenAIModelName();
  const baseUrl = getOpenAIBaseUrl();
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
        max_tokens: 700,
        frequency_penalty: 1.1,
        presence_penalty: 1.1,
        stop: ["<|im_end|>", "<|endoftext|>"],
        stream: true
      })
    },
    timeoutMs
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`OpenAI API error: ${response.status} ${text}`);
  }

  let resolveReply: (value: string) => void;
  let rejectReply: (reason?: unknown) => void;
  const replyPromise = new Promise<string>((resolve, reject) => {
    resolveReply = resolve;
    rejectReply = reject;
  });
  let aggregated = "";

  try {
    const stream = OpenAIStream(response, {
      onToken(token) {
        aggregated += token;
      },
      onCompletion(finalText) {
        const finalValue = typeof finalText === "string" && finalText.length ? finalText : aggregated;
        resolveReply(finalValue);
      }
    });
    return { stream, replyPromise };
  } catch (err) {
    rejectReply(err);
    throw err;
  }
}
