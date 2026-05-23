import { NextResponse } from "next/server";
import { randomUUID } from "node:crypto";
import { StreamingTextResponse } from "ai";
import { getSystemPrompt } from "@/lib/systemPrompt";
import { generateReply, generateReplyStream } from "@/lib/llm";
import { logTurnToGas } from "@/lib/gasLog";
import { detectBehaviorSignals } from "@/lib/behavior";
import type { ChatRequest, ChatResponse } from "@/lib/types";
import db from "@/lib/db"; // Import DB

export const runtime = "nodejs";

export async function POST(req: Request) {
  const body = (await req.json().catch(() => null)) as ChatRequest | null;
  if (!body) return NextResponse.json<ChatResponse>({ ok: false, error: "Invalid JSON." }, { status: 400 });

  // 1. Fetch Student from DB
  const student = db.prepare("SELECT * FROM students WHERE id = ?").get(body.studentId) as any;
  if (!student) return NextResponse.json<ChatResponse>({ ok: false, error: "Mã học sinh không tồn tại." }, { status: 404 });

  // 2. Fetch History from DB (Instead of Client)
  const dbHistory = db.prepare("SELECT role, content FROM messages WHERE student_id = ? ORDER BY timestamp ASC LIMIT 10").all(body.studentId) as any[];
  
  // 3. Prepare Prompt
  const behavior = detectBehaviorSignals({ history: dbHistory, message: body.message });
  const systemPrompt = getSystemPrompt({
    profile: student.profile,
    group: student.research_group,
    behavior
  });
  
  const messageId = randomUUID();
  const streamRequested = body.stream === true;

  try {
    // Save student message to DB immediately
    db.prepare("INSERT INTO messages (id, student_id, role, content) VALUES (?, ?, ?, ?)").run(randomUUID(), body.studentId, 'user', body.message);

    if (streamRequested) {
      const result = await generateReplyStream({ systemPrompt, history: dbHistory, message: body.message });
      if (!result.stream) throw new Error("LLM does not support streaming.");

      // Capture stream to save to DB when finished
      const replyPromise = result.replyPromise.then(reply => {
          db.prepare("INSERT INTO messages (id, student_id, role, content, message_id) VALUES (?, ?, ?, ?, ?)").run(randomUUID(), body.studentId, 'assistant', reply, messageId);
          return reply;
      });

      // Background log to GAS
      const canLog = Boolean(process.env.GAS_LOG_URL && process.env.GAS_LOG_TOKEN);
      if (canLog) {
          replyPromise.then(reply => logTurnToGas({ request: { ...body, profile: student.profile, className: student.class }, aiResponse: reply, messageId }));
      }

      return new StreamingTextResponse(result.stream, {
        headers: { "content-type": "text/plain; charset=utf-8", "x-message-id": messageId }
      });
    }

    const { reply } = await generateReply({ systemPrompt, history: dbHistory, message: body.message });
    
    // Save AI response to DB
    db.prepare("INSERT INTO messages (id, student_id, role, content, message_id) VALUES (?, ?, ?, ?, ?)").run(randomUUID(), body.studentId, 'assistant', reply, messageId);

    // Background log to GAS
    const canLog = Boolean(process.env.GAS_LOG_URL && process.env.GAS_LOG_TOKEN);
    if (canLog) {
      void logTurnToGas({ request: { ...body, profile: student.profile, className: student.class }, aiResponse: reply, messageId }).catch(console.error);
    }

    return NextResponse.json<ChatResponse>({ ok: true, reply, messageId, logged: canLog });
  } catch (err) {
    const error = String(err instanceof Error ? err.message : err);
    return NextResponse.json<ChatResponse>({ ok: false, error, messageId }, { status: 500 });
  }
}
