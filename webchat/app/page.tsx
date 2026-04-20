"use client";

import React, { useEffect, useMemo, useState, useRef } from "react";
import type { CSSProperties } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import type { ChatMessage, ChatResponse } from "@/lib/types";

type SessionInfo = {
  studentId: string;
  className: string;
  group: "Experimental" | "Control";
  topic: string;
  profile: string;
};

export default function HomePage() {
  const [session, setSession] = useState<SessionInfo>({
    studentId: "",
    className: "11A1",
    group: "Experimental",
    topic: "Xác suất cơ bản",
    profile: ""
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string>("");

  const canChat = useMemo(() => session.studentId.trim().length >= 3, [session.studentId]);
  const storageKey = "gps_aiedu_chat_v1";
  const maxStoredMessages = 200;

  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return;
      const parsed = JSON.parse(raw) as { session?: SessionInfo; messages?: ChatMessage[] };
      if (parsed.session) setSession(parsed.session);
      if (Array.isArray(parsed.messages)) setMessages(parsed.messages);
    } catch {
      // ignore storage errors
    }
  }, []);

  useEffect(() => {
    try {
      const payload = {
        session,
        messages: messages.slice(-maxStoredMessages)
      };
      localStorage.setItem(storageKey, JSON.stringify(payload));
    } catch {
      // ignore storage errors
    }
  }, [session, messages]);

  async function fetchStudentInfo(id: string) {
    if (id.length < 3) return;
    try {
      const res = await fetch(`/api/student/${id}`);
      const data = await res.json();
      if (data.ok) {
        setSession(data.student);
        if (data.history) setMessages(data.history);
        setStatus("Đã nạp hồ sơ học tập.");
      }
    } catch (err) {
      console.error("Failed to fetch student info", err);
    }
  }

  async function sendMessage() {
    if (!canChat || busy) return;
    const text = input.trim();
    if (!text) return;

    setStatus("");
    setBusy(true);
    setInput("");

    const nextMessages = [...messages, { role: "user", content: text } as const];
    setMessages([...nextMessages, { role: "assistant", content: "" }]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          studentId: session.studentId.trim(),
          className: session.className.trim(),
          group: session.group as any,
          topic: session.topic.trim(),
          profile: session.profile.trim(),
          message: text,
          history: messages,
          stream: true
        })
      });

      const messageId = response.headers.get("x-message-id") || undefined;
      const contentType = response.headers.get("content-type") || "";

      if (!contentType.includes("application/json")) {
        if (!response.ok || !response.body) {
          const text = await response.text().catch(() => "");
          setStatus(text || "Chat failed.");
          setMessages(nextMessages);
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let acc = "";

        while (true) {
          const { value, done } = await reader.read();
          if (value) {
            acc += decoder.decode(value, { stream: !done });
            setMessages((prev: ChatMessage[]) => {
              if (prev.length === 0) return prev;
              const next = [...prev];
              const last = next[next.length - 1];
              if (last.role !== "assistant") {
                next.push({ role: "assistant", content: acc, messageId });
              } else {
                next[next.length - 1] = { ...last, content: acc, messageId };
              }
              return next;
            });
          }
          if (done) break;
        }
        return;
      }

      const data = (await response.json()) as ChatResponse;
      if (!data.ok || !data.reply) {
        setStatus(data.error || "Chat failed.");
        setMessages(nextMessages);
        return;
      }

      setMessages([...nextMessages, { role: "assistant", content: data.reply, messageId: data.messageId }]);
      if (data.logError) setStatus(`Đã trả lời, nhưng log lỗi: ${data.logError}`);
    } catch (err) {
      setStatus(String(err instanceof Error ? err.message : err));
      setMessages(nextMessages);
    } finally {
      setBusy(false);
    }
  }

  async function handleRate(messageId: string, idx: number, ratingType: "satisfaction" | "difficulty", value: number) {
    if (!messageId) return;
    try {
      const payload: any = { messageId };
      payload[ratingType] = value;

      const res = await fetch("/api/rate", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.ok) {
        setMessages((prev: ChatMessage[]) => {
          const next = [...prev];
          next[idx] = { ...next[idx], [ratingType]: value };
          return next;
        });
        setStatus(`Đã ghi nhận ${value} điểm cho ${ratingType === "satisfaction" ? "sự hài lòng" : "độ khó"}.`);
      } else {
        setStatus(`Lỗi khi đánh giá: ${data.error}`);
      }
    } catch (err) {
      setStatus(`Lỗi kết nối khi đánh giá: ${String(err)}`);
    }
  }

  const progressStats = useMemo(() => {
    let G = 0, P = 0, S = 0;
    messages.forEach((m) => {
      if (m.role === "assistant") {
        if (/^\s*\[G\]/i.test(m.content)) G++;
        else if (/^\s*\[P\]/i.test(m.content)) P++;
        else if (/^\s*\[S\]/i.test(m.content)) S++;
      }
    });
    return { G, P, S };
  }, [messages]);

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
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                const id = e.target.value;
                setSession({ ...session, studentId: id });
                if (id.length >= 4) fetchStudentInfo(id);
              }}
              placeholder="HS01"
              style={inputStyle}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Class</span>
            <input
              value={session.className}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSession({ ...session, className: e.target.value })}
              style={inputStyle}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Topic</span>
            <input
              value={session.topic}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSession({ ...session, topic: e.target.value })}
              style={inputStyle}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Profile (optional)</span>
            <input
              value={session.profile}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSession({ ...session, profile: e.target.value })}
              placeholder="Typical"
              style={inputStyle}
            />
          </label>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ color: "var(--muted)" }}>Group</span>
            <select
              value={session.group}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSession({ ...session, group: e.target.value as any })}
              style={inputStyle}
            >
              <option value="Experimental">Experimental (GPS)</option>
              <option value="Control">Control (Free AI)</option>
            </select>
          </label>
        </div>

        {!canChat ? (
          <p style={{ margin: "10px 0 0", color: "var(--muted)" }}>Nhập Student ID để bắt đầu chat.</p>
        ) : null}
      </section>

      {canChat && (
        <div style={{
          marginTop: 16, display: "flex", flexDirection: "column", gap: 8,
          background: "#1f3b7430", border: "1px solid #1f3b74", borderRadius: 8, padding: "12px 16px"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontWeight: "bold", fontSize: 13 }}>TIẾN TRÌNH G.P.S</span>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>{progressStats.G + progressStats.P + progressStats.S} lượt hội thoại</span>
          </div>
          <div style={{ display: "flex", height: 8, gap: 4 }}>
            <div style={{ flex: progressStats.G || 1, background: "#ffd48a", borderRadius: 4, transition: "flex 0.5s ease" }} title="Guide" />
            <div style={{ flex: progressStats.P || 1, background: "#8effa8", borderRadius: 4, transition: "flex 0.5s ease" }} title="Practice" />
            <div style={{ flex: progressStats.S || 1, background: "#8ac8ff", borderRadius: 4, transition: "flex 0.5s ease" }} title="Solve" />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--muted)" }}>
            <span>HƯỚNG DẪN (G)</span>
            <span>LUYỆN TẬP (P)</span>
            <span>HOÀN THÀNH (S)</span>
          </div>
        </div>
      )}

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
          {messages.map((m: ChatMessage, idx: number) => (
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
              <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                {m.content}
              </ReactMarkdown>
              {m.role === "assistant" && idx === messages.length - 1 && !busy && (
                <div style={{ marginTop: 10, borderTop: "1px solid #1e2d4d", paddingTop: 8 }}>
                  <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
                    <div>
                      <span style={{ fontSize: 12, color: "var(--muted)", marginRight: 8 }}>
                        {m.satisfaction ? `Độ hài lòng: ${m.satisfaction}/5` : "Hài lòng:"}
                      </span>
                      {!m.satisfaction && [1, 2, 3, 4, 5].map((s) => (
                        <button
                          key={s}
                          onClick={() => m.messageId && handleRate(m.messageId, idx, "satisfaction", s)}
                          style={{
                            background: "none", border: "none", cursor: "pointer",
                            fontSize: 16, padding: "0 2px"
                          }}
                        >⭐</button>
                      ))}
                    </div>
                    <div>
                      <span style={{ fontSize: 12, color: "var(--muted)", marginRight: 8 }}>
                        {m.difficulty ? `Độ khó: ${m.difficulty}/5` : "Độ khó:"}
                      </span>
                      {!m.difficulty && [1, 2, 3, 4, 5].map((s) => (
                        <button
                          key={s}
                          onClick={() => m.messageId && handleRate(m.messageId, idx, "difficulty", s)}
                          style={{
                            background: "none", border: "none", cursor: "pointer",
                            fontSize: 16, padding: "0 2px"
                          }}
                        >🤔</button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 12 }}>
        <div style={{ display: "flex", gap: 10 }}>
          <textarea
            value={input}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
            placeholder="Nhập câu hỏi..."
            rows={3}
            style={{
              ...inputStyle,
              resize: "vertical",
              width: "100%"
            }}
            disabled={!canChat || busy}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
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
          {status || "Mẹo: Nhấn Enter để gửi, Shift+Enter để xuống dòng."}
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
