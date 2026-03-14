import { ChatMessage } from "./types";
import { generateWithOpenAI } from "./openai";
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

  // default: openai
  const reply = await generateWithOpenAI(params);
  return { provider: "openai", reply };
}
