import { ChatMessage } from "./types";

export type BehaviorSignals = {
  skipStep: boolean;
  looping: boolean;
  promptInjection: boolean;
  consecutiveP: number;
  lastAssistantStep: "G" | "P" | "S" | "";
};

type DetectParams = {
  history: ChatMessage[];
  message: string;
};

export function detectBehaviorSignals(params: DetectParams): BehaviorSignals {
  const history = Array.isArray(params.history) ? params.history : [];
  const steps = history
    .filter((m) => m.role === "assistant")
    .map((m) => extractAssistantStep_(m.content));

  const lastAssistantStep = steps.length ? steps[steps.length - 1] : "";
  const consecutiveP = countConsecutive_(steps, "P");

  const normalizedMessage = normalizeText_(params.message || "");
  const isSolveRequest = ANSWER_REQUEST_RE_.test(normalizedMessage);
  const promptInjection = PROMPT_INJECTION_RE_.test(normalizedMessage);

  const skipStep = lastAssistantStep === "G" && isSolveRequest;
  const looping = consecutiveP >= 3;

  return {
    skipStep,
    looping,
    promptInjection,
    consecutiveP,
    lastAssistantStep
  };
}

export function behaviorFlagsToString(signals: BehaviorSignals): string {
  const flags: string[] = [];
  if (signals.skipStep) flags.push("skip_step");
  if (signals.looping) flags.push("looping");
  if (signals.promptInjection) flags.push("prompt_injection");
  return flags.join(",");
}

function extractAssistantStep_(content: string): "G" | "P" | "S" | "" {
  const match = String(content || "").trim().match(/^\s*\[([GPS])\]/i);
  if (!match) return "";
  const step = match[1].toUpperCase();
  return step === "G" || step === "P" || step === "S" ? step : "";
}

function countConsecutive_(steps: string[], target: string): number {
  let count = 0;
  for (let i = steps.length - 1; i >= 0; i--) {
    if (steps[i] !== target) break;
    count += 1;
  }
  return count;
}

function normalizeText_(text: string): string {
  let t = String(text || "").toLowerCase();
  t = t.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  t = t.replace(/\u0111/g, "d");
  t = t.replace(/\s+/g, " ").trim();
  return t;
}

const ANSWER_REQUEST_RE_ = /\b(dap an|ket qua|giai giup|giai ho|giai luon|giai nhanh|solve for me|final answer|answer only|full solution|loi giai day du)\b/i;
const PROMPT_INJECTION_RE_ = /\b(ignore|bypass|override|disregard).*(system|developer|instruction)|system prompt|jailbreak|act as|you are now|roleplay|break rules|reveal prompt\b/i;
