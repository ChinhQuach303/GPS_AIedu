import { ChatRequest } from "./types";
import { fetchWithTimeout } from "./fetchWithTimeout";
import { classifyGpsStepLLM } from "./gpsClassifier";
import { behaviorFlagsToString, detectBehaviorSignals } from "./behavior";

export async function logTurnToGas(params: {
  request: ChatRequest;
  aiResponse: string;
  messageId: string;
}): Promise<void> {
  const gasUrl = process.env.GAS_LOG_URL;
  const gasToken = process.env.GAS_LOG_TOKEN;
  if (!gasUrl || !gasToken) return;
  const timeoutMs = Number(process.env.GAS_LOG_TIMEOUT_MS || 15_000);

  let gpsAuto = "";
  try {
    gpsAuto = await classifyGpsStepLLM({ message: params.request.message });
  } catch {
    gpsAuto = "";
  }

  const behavior = detectBehaviorSignals({
    history: params.request.history || [],
    message: params.request.message
  });
  const behaviorFlags = behaviorFlagsToString(behavior);

  const payload = {
    token: gasToken,
    messageId: params.messageId,
    studentId: params.request.studentId,
    className: params.request.className,
    topic: params.request.topic,
    profile: params.request.profile || "",
    question: params.request.message,
    aiResponse: params.aiResponse,
    notes: params.request.notes || "",
    satisfaction: params.request.satisfaction ?? 3,
    difficulty: params.request.difficulty ?? 3,
    gpsTruth: params.request.gpsTruth ?? "",
    gpsAuto,
    behaviorFlags
  };

  const response = await fetchWithTimeout(
    gasUrl,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload)
    },
    timeoutMs
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(`GAS log failed: ${response.status} ${text}`);
  }

  const result = (await response.json().catch(() => null)) as { ok?: boolean; error?: string } | null;
  if (result && result.ok === false) {
    throw new Error(`GAS log rejected: ${result.error || "unknown error"}`);
  }
}
