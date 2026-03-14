"use client";

import { useMemo, useState } from "react";
import type { CSSProperties } from "react";
import type { ChatMessage, ChatResponse } from "@/lib/types";

type SessionInfo = {
  studentId: string;
  className: string;
  topic: string;
  profile: string;
};

export default function HomePage() {
  const [session, setSession] = useState<SessionInfo>({
    studentId: "",
    className: "11A1",
    topic: "Xác suất cơ bản",
    profile: ""
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string>("");

  const canChat = useMemo(() => session.studentId.trim().length >= 3, [session.studentId]);

  async function sendMessage() {
    if (!canChat || busy) return;
    const text = input.trim();
    if (!text) return;

    setStatus("");
    setBusy(true);
    setInput("");

    const nextMessages = [...messages, { role: "user", content: text } as const];
    setMessages(nextMessages);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          studentId: session.studentId.trim(),
          className: session.className.trim(),
          topic: session.topic.trim(),
          profile: session.profile.trim(),
          message: text,
          history: messages
        })
      });

      const data = (await response.json()) as ChatResponse;
      if (!data.ok || !data.reply) {
        setStatus(data.error || "Chat failed.");
        return;
      }

      setMessages([...nextMessages, { role: "assistant", content: data.reply }]);
      if (data.logError) setStatus(`Đã trả lời, nhưng log lỗi: ${data.logError}`);
    } catch (err) {
      setStatus(String(err instanceof Error ? err.message : err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: 20 }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 20 }}>GPS AIedu Web Chat</h1>
          <p style={{ margin: "6px 0 0", color: "var(--muted)" }}>
            Chat với gia sư GPS và tự động log vào Google Sheet <code>Raw Data</code>.
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <a href="/api/health" target="_blank" rel="noreferrer">
            Health
          </a>
          <a href="/api/models" target="_blank" rel="noreferrer">
            Models
          </a>
        </div>
      </header>

      <section
        style={{
          marginTop: 16,
          background: "var(--panel)",
          border: "1px solid var(--border)",
          borderRadius: 12,
          padding: 12
        }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 10 }}>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Student ID</span>
            <input
              value={session.studentId}
              onChange={(e) => setSession({ ...session, studentId: e.target.value })}
              placeholder="HS0001"
              style={inputStyle}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Class</span>
            <input
              value={session.className}
              onChange={(e) => setSession({ ...session, className: e.target.value })}
              style={inputStyle}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Topic</span>
            <input
              value={session.topic}
              onChange={(e) => setSession({ ...session, topic: e.target.value })}
              style={inputStyle}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Profile (optional)</span>
            <input
              value={session.profile}
              onChange={(e) => setSession({ ...session, profile: e.target.value })}
              placeholder="Typical"
              style={inputStyle}
            />
          </label>
        </div>

        {!canChat ? (
          <p style={{ margin: "10px 0 0", color: "var(--muted)" }}>Nhập Student ID để bắt đầu chat.</p>
        ) : null}
      </section>

      <section
        style={{
          marginTop: 16,
          background: "var(--panel)",
          border: "1px solid var(--border)",
          borderRadius: 12,
          padding: 12,
          minHeight: 420
        }}
      >
        <div style={{ display: "grid", gap: 10 }}>
          {messages.length === 0 ? (
            <div style={{ color: "var(--muted)" }}>
              Gợi ý: hỏi theo GPS. Ví dụ: “(G) Giải thích giúp em xác suất có điều kiện là gì?”
            </div>
          ) : null}
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                padding: 10,
                borderRadius: 10,
                border: "1px solid var(--border)",
                background: m.role === "user" ? "#0f244d" : "#0e1a2f",
                whiteSpace: "pre-wrap"
              }}
            >
              <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 6 }}>
                {m.role === "user" ? "Học sinh" : "Gia sư GPS"}
              </div>
              {m.content}
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 12 }}>
        <div style={{ display: "flex", gap: 10 }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Nhập câu hỏi..."
            rows={3}
            style={{
              ...inputStyle,
              resize: "vertical",
              width: "100%"
            }}
            disabled={!canChat || busy}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                void sendMessage();
              }
            }}
          />
          <button
            onClick={() => void sendMessage()}
            disabled={!canChat || busy}
            style={{
              padding: "10px 14px",
              borderRadius: 10,
              border: "1px solid var(--border)",
              background: busy ? "#1b2a47" : "#1f3b74",
              color: "var(--text)",
              minWidth: 120,
              cursor: busy ? "not-allowed" : "pointer"
            }}
          >
            {busy ? "Đang..." : "Gửi"}
          </button>
        </div>
        <div style={{ marginTop: 8, color: status ? "#ffd48a" : "var(--muted)" }}>
          {status || "Mẹo: Ctrl/Cmd + Enter để gửi."}
        </div>
      </section>
    </main>
  );
}

const inputStyle: CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid var(--border)",
  background: "#0b1323",
  color: "var(--text)",
  outline: "none"
};
