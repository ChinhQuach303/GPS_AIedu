import { NextResponse } from "next/server";
import { getOpenAIApiKey } from "@/lib/env";

export const runtime = "nodejs";

async function pingOllama() {
  const baseUrl = (process.env.OLLAMA_BASE_URL || "http://127.0.0.1:11434").replace(/\/+$/, "");
  try {
    const res = await fetch(`${baseUrl}/api/version`, { method: "GET" });
    if (!res.ok) return { ok: false as const, error: `HTTP ${res.status}` };
    const data = (await res.json().catch(() => null)) as { version?: string } | null;
    return { ok: true as const, version: data?.version || "unknown" };
  } catch (err) {
    return { ok: false as const, error: String(err instanceof Error ? err.message : err) };
  }
}

async function pingVLLM() {
  const baseUrl = (process.env.OPENAI_BASE_URL || "http://127.0.0.1:8000/v1").replace(/\/+$/, "");
  try {
    const res = await fetch(`${baseUrl}/models`, { method: "GET" });
    if (!res.ok) return { ok: false as const, error: `HTTP ${res.status}` };
    return { ok: true as const, status: "available" };
  } catch (err) {
    return { ok: false as const, error: String(err instanceof Error ? err.message : err) };
  }
}

export async function GET() {
  const provider = (process.env.LLM_PROVIDER || "openai").trim().toLowerCase();
  const ollama = provider === "ollama" ? await pingOllama() : null;
  const vllm = provider === "vllm" ? await pingVLLM() : null;
  
  return NextResponse.json({
    ok: true,
    provider,
    openaiConfigured: Boolean(getOpenAIApiKey()),
    gasLoggingConfigured: Boolean(process.env.GAS_LOG_URL && process.env.GAS_LOG_TOKEN),
    ollama,
    vllm
  });
}
