import { NextResponse } from "next/server";
import { fetchWithTimeout } from "@/lib/fetchWithTimeout";

export async function POST(req: Request) {
  const body = await req.json().catch(() => null);
  if (!body || !body.messageId || (body.satisfaction === undefined && body.difficulty === undefined)) {
    return NextResponse.json({ ok: false, error: "Missing messageId or ratings." }, { status: 400 });
  }

  const gasUrl = process.env.GAS_LOG_URL;
  const gasToken = process.env.GAS_LOG_TOKEN;

  if (!gasUrl || !gasToken) {
    return NextResponse.json({ ok: true, note: "Rating is disabled because GAS logging is not configured." });
  }

  try {
    const payload = {
      action: "rate",
      token: gasToken,
      messageId: body.messageId,
      satisfaction: body.satisfaction,
      difficulty: body.difficulty
    };

    const response = await fetchWithTimeout(gasUrl, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload)
    }, 10000);

    if (!response.ok) {
      throw new Error(`GAS rejected rate: ${response.status}`);
    }

    const result = await response.json().catch(() => null);
    return NextResponse.json({ ok: true, result });
  } catch (err) {
    return NextResponse.json({ ok: false, error: String(err) }, { status: 500 });
  }
}
