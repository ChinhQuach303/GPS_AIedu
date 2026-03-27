import { NextResponse } from "next/server";
import { getOpenAIApiKey, getOpenAIBaseUrl } from "@/lib/env";

export const runtime = "nodejs";

type OpenAIListModelsResponse = {
  data?: Array<{ id?: string }>;
  error?: { message?: string };
};

export async function GET() {
  try {
    const provider = (process.env.LLM_PROVIDER || "openai").trim().toLowerCase();
    if (provider === "ollama") {
      return NextResponse.json({ ok: true, provider, models: [], note: "For Ollama, run `ollama list` locally." });
    }

    const apiKey = getOpenAIApiKey();
    const baseUrl = getOpenAIBaseUrl();
    const headers: Record<string, string> = {};
    if (apiKey && apiKey !== "vllm-not-needed") {
      headers["authorization"] = `Bearer ${apiKey}`;
    }

    const response = await fetch(`${baseUrl}/models`, {
      method: "GET",
      headers
    });
    if (!response.ok) {
      const text = await response.text().catch(() => "");
      return NextResponse.json({ ok: false, error: `${provider} models error: ${response.status} ${text}` }, { status: 500 });
    }
    const data = (await response.json()) as OpenAIListModelsResponse;
    const models = (data.data || []).map((m) => m.id).filter(Boolean);
    return NextResponse.json({ ok: true, provider, models });
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: String(err instanceof Error ? err.message : err) },
      { status: 500 }
    );
  }
}
