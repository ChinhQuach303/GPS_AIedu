import { NextResponse } from "next/server";
import { randomUUID } from "node:crypto";
import { StreamingTextResponse } from "ai";
import { getSystemPrompt } from "@/lib/systemPrompt";
import { generateReply, generateReplyStream } from "@/lib/llm";
import { logTurnToGas } from "@/lib/gasLog";
import { detectBehaviorSignals } from "@/lib/behavior";
import type { ChatRequest, ChatResponse } from "@/lib/types";

export const runtime = "nodejs";

function validateRequest(body: ChatRequest): string | null {
  if (!body.studentId || body.studentId.trim().length < 3) return "Missing studentId.";
  if (!body.className || body.className.trim().length < 2) return "Missing className.";
  if (!body.topic || body.topic.trim().length < 2) return "Missing topic.";
  if (!body.message || body.message.trim().length < 1) return "Missing message.";
  if (body.message.length > 6000) return "Message too long.";
  return null;
}

export async function POST(req: Request) {
  const body = (await req.json().catch(() => null)) as ChatRequest | null;
  if (!body) return NextResponse.json<ChatResponse>({ ok: false, error: "Invalid JSON." }, { status: 400 });

  const validationError = validateRequest(body);
  if (validationError) return NextResponse.json<ChatResponse>({ ok: false, error: validationError }, { status: 400 });

  const history = Array.isArray(body.history) ? body.history.slice(-20) : [];
  const behavior = detectBehaviorSignals({ history, message: body.message });
  const systemPrompt = getSystemPrompt({ profile: body.profile, behavior });
  const messageId = randomUUID();
  const streamRequested = body.stream === true;

  try {
    if (streamRequested) {
      const canLog = Boolean(process.env.GAS_LOG_URL && process.env.GAS_LOG_TOKEN);
      const result = await generateReplyStream({
        systemPrompt,
        history,
        message: body.message
      });
      if (!result.stream) {
        throw new Error("LLM does not support streaming.");
      }
      if (canLog) {
        void result.replyPromise
          .then((reply) => {
            if (reply) {
              void logTurnToGas({ request: body, aiResponse: reply, messageId }).catch((err) => {
                console.error("logTurnToGas failed", err);
              });
            }
          })
          .catch((err) => {
            console.error("Unable to capture LLM reply for logging", err);
          });
      }

      return new StreamingTextResponse(result.stream, {
        headers: {
          "content-type": "text/plain; charset=utf-8",
          "x-message-id": messageId
        }
      });
    }

    const { reply } = await generateReply({
      systemPrompt,
      history,
      message: body.message
    });

    const canLog = Boolean(process.env.GAS_LOG_URL && process.env.GAS_LOG_TOKEN);
    const logged = canLog;
    let logError: string | undefined;
    if (canLog) {
      void Promise.resolve(logTurnToGas({ request: body, aiResponse: reply, messageId })).catch((err) => {
        logError = String(err instanceof Error ? err.message : err);
        console.error("logTurnToGas failed", err);
      });
    }

    return NextResponse.json<ChatResponse>({
      ok: true,
      reply,
      messageId,
      logged,
      logError
    });
  } catch (err) {
    const raw = String(err instanceof Error ? err.message : err);
    const isQuota = /\\b429\\b/.test(raw) || /RESOURCE_EXHAUSTED/i.test(raw) || /quota/i.test(raw);
    const isAbort = /aborted/i.test(raw) || /abort/i.test(raw) || /timeout/i.test(raw);
    const error = isQuota
      ? `${raw}\n\nGợi ý: Bạn đang bị quota/rate-limit. Có thể chuyển sang model open-weight chạy local bằng Ollama (set LLM_PROVIDER=ollama trong .env.local).`
      : isAbort
        ? `${raw}\n\nGợi ý: LLM đang bị timeout hoặc không phản hồi. Nếu dùng Ollama, mở /api/health để kiểm tra Ollama có chạy không.`
      : raw;
    return NextResponse.json<ChatResponse>(
      { ok: false, error, messageId },
      { status: 500 }
    );
  }
}
