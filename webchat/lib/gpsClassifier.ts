import { fetchWithTimeout } from "./fetchWithTimeout";

export type GpsLabel = "G" | "P" | "S";

export async function classifyGpsStepLLM(params: {
  message: string;
}): Promise<GpsLabel | ""> {
  const enabledRaw = (process.env.GPS_CLASSIFY_ENABLED || "true").trim().toLowerCase();
  const enabled = enabledRaw !== "false" && enabledRaw !== "0";

  const apiKey = process.env.OPENAI_API_KEY;
  if (!enabled || !apiKey) return "";

  const model =
    process.env.GPS_CLASSIFIER_MODEL ||
    process.env.OPENAI_CLASSIFIER_MODEL ||
    process.env.OPENAI_MODEL ||
    "gpt-4o-mini";
  const baseUrl = (process.env.OPENAI_BASE_URL || "https://api.openai.com/v1").replace(/\/+$/, "");
  const timeoutMs = Number(process.env.GPS_CLASSIFIER_TIMEOUT_MS || 12_000);

  const systemPrompt =
    "You are a strict classifier. Label the student's latest message as one of:\n" +
    "G: seeking concepts/definitions/why\n" +
    "P: seeking guidance/steps/hints\n" +
    "S: seeking final answer/verification/solution\n" +
    'Return only one letter: G, P, or S. If unclear, return "Unknown".';

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
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: params.message || "" }
        ],
        temperature: 0,
        max_tokens: 5
      })
    },
    timeoutMs
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`OpenAI classifier error: ${response.status} ${text}`);
  }

  const data = (await response.json()) as {
    choices?: Array<{ message?: { content?: string } }>;
  };
  const content = String(data.choices?.[0]?.message?.content || "").trim().toUpperCase();

  if (content.startsWith("G")) return "G";
  if (content.startsWith("P")) return "P";
  if (content.startsWith("S")) return "S";
  return "";
}
