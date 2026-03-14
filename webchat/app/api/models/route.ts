import { NextResponse } from "next/server";

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

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) return NextResponse.json({ ok: false, error: "Missing OPENAI_API_KEY." }, { status: 500 });

    const baseUrl = (process.env.OPENAI_BASE_URL || "https://api.openai.com/v1").replace(/\/+$/, "");
    const response = await fetch(`${baseUrl}/models`, {
      method: "GET",
      headers: { authorization: `Bearer ${apiKey}` }
    });
    if (!response.ok) {
      const text = await response.text().catch(() => "");
      return NextResponse.json({ ok: false, error: `OpenAI models error: ${response.status} ${text}` }, { status: 500 });
    }
    const data = (await response.json()) as OpenAIListModelsResponse;
    const models = (data.data || []).map((m) => m.id).filter(Boolean);
    return NextResponse.json({ ok: true, provider: "openai", models });
  } catch (err) {
    return NextResponse.json(
      { ok: false, error: String(err instanceof Error ? err.message : err) },
      { status: 500 }
    );
  }
}
