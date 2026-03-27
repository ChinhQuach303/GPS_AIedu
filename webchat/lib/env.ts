export function getOpenAIApiKey(): string | undefined {
  return process.env.OPENAI_API_KEY || process.env.LLM_API_KEY;
}

export function getOpenAIBaseUrl(): string {
  const base =
    process.env.OPENAI_BASE_URL || process.env.LLM_BASE_URL || "https://api.openai.com/v1";
  return base.replace(/\/+$/, "");
}

export function getOpenAIModelName(): string {
  return process.env.OPENAI_MODEL || process.env.LLM_MODEL_NAME || "gpt-4o-mini";
}
