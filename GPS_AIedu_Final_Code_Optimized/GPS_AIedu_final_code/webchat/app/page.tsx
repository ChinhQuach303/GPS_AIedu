"use client";

import React, { useEffect, useMemo, useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  intent?: string;
};

type StudentProfile = {
  id: string;
  level: string;
  class: string;
};

export default function GPSPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [qid, setQid] = useState("1");
  const [student, setStudent] = useState<StudentProfile>({
    id: "HS001",
    level: "Trung bình",
    class: "11A1"
  });

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const progress = useMemo(() => {
    const stats = { G: 0, P: 0, S: 0 };
    messages.forEach(m => {
      if (m.intent === "G") stats.G++;
      else if (m.intent === "P") stats.P++;
      else if (m.intent === "S") stats.S++;
    });
    const total = stats.G + stats.P + stats.S || 1;
    return {
      G: (stats.G / total) * 100,
      P: (stats.P / total) * 100,
      S: (stats.S / total) * 100,
      counts: stats
    };
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || busy) return;
    const text = input;
    setInput("");
    setBusy(true);

    const newMessages = [...messages, { role: "user", content: text } as const];
    setMessages(newMessages);

    try {
      // Calling the Python FastAPI Backend directly
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          qid: qid,
          message: text,
          history: messages.map(m => ({ role: m.role, content: m.content })),
          student_level: student.level
        })
      });

      if (!response.ok) throw new Error("Backend connection failed.");

      const data = await response.json();
      setMessages([...newMessages, { role: "assistant", content: data.reply, intent: data.intent }]);
    } catch (err) {
      console.error(err);
      setMessages([...newMessages, { role: "assistant", content: "⚠️ Có lỗi kết nối tới máy chủ AI. Vui lòng thử lại." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-80 glass border-r flex flex-col p-6 gap-8 hidden md:flex">
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            GPS AIedu
          </h1>
          <p className="text-sm text-slate-400 mt-2">Gia sư Xác suất Thống kê thông minh</p>
        </div>

        <div className="flex flex-col gap-4">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Hồ sơ học sinh</h3>
          <div className="space-y-4">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-slate-500">Mã học sinh</span>
              <input 
                className="bg-white/5 border border-white/10 rounded-lg p-2 text-sm outline-none focus:border-blue-500/50"
                value={student.id}
                onChange={e => setStudent({...student, id: e.target.value})}
              />
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-slate-500">Trình độ</span>
              <select 
                className="bg-white/5 border border-white/10 rounded-lg p-2 text-sm outline-none focus:border-blue-500/50"
                value={student.level}
                onChange={e => setStudent({...student, level: e.target.value})}
              >
                <option value="Giỏi">Giỏi</option>
                <option value="Khá">Khá</option>
                <option value="Trung bình">Trung bình</option>
                <option value="Yếu">Yếu</option>
              </select>
            </div>
          </div>
        </div>

        <div className="mt-auto">
          <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300">
            Hệ thống đang sử dụng kiến trúc Multi-Agent ReAct (Qwen-2.5 7B).
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col relative">
        {/* Header / Progress bar */}
        <header className="p-6 glass border-b flex flex-col gap-4 z-10">
          <div className="flex justify-between items-center">
            <h2 className="font-semibold text-lg">Bài tập #{qid}</h2>
            <div className="text-xs text-slate-400 font-mono">
              STATUS: {busy ? "THINKING..." : "READY"}
            </div>
          </div>
          
          <div className="flex flex-col gap-2">
            <div className="flex h-2 w-full bg-white/5 rounded-full overflow-hidden gap-1">
              <div className="progress-segment bg-amber-400" style={{ width: `${progress.G}%` }} />
              <div className="progress-segment bg-emerald-400" style={{ width: `${progress.P}%` }} />
              <div className="progress-segment bg-blue-500" style={{ width: `${progress.S}%` }} />
            </div>
            <div className="flex justify-between text-[10px] font-bold text-slate-500 uppercase tracking-tighter">
              <span className={progress.counts.G > 0 ? "text-amber-400" : ""}>Guide</span>
              <span className={progress.counts.P > 0 ? "text-emerald-400" : ""}>Practice</span>
              <span className={progress.counts.S > 0 ? "text-blue-500" : ""}>Solve</span>
            </div>
          </div>
        </header>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 flex flex-col scroll-smooth">
          {messages.length === 0 && (
            <div className="m-auto text-center space-y-4 max-w-md">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto border border-blue-500/40">
                ✨
              </div>
              <h3 className="text-xl font-bold">Bắt đầu phiên học</h3>
              <p className="text-sm text-slate-400">
                Hãy đặt câu hỏi về bài tập toán. Thầy sẽ hướng dẫn em từng bước một theo lộ trình G-P-S.
              </p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role === 'user' ? 'user' : 'assistant'}`}>
              <div className="text-[10px] opacity-50 uppercase font-bold mb-1 tracking-wider">
                {m.role === 'user' ? 'Học sinh' : 'Gia sư GPS'}
              </div>
              <ReactMarkdown 
                remarkPlugins={[remarkMath]} 
                rehypePlugins={[rehypeKatex]}
                className="prose prose-invert max-w-none text-sm md:text-base"
              >
                {m.content}
              </ReactMarkdown>
            </div>
          ))}
          {busy && (
            <div className="chat-bubble assistant animate-pulse">
              <div className="flex gap-1 py-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '200ms' }} />
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '400ms' }} />
              </div>
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="p-6 glass border-t mt-auto">
          <div className="relative flex items-center max-w-4xl mx-auto">
            <textarea 
              className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 pr-16 text-sm outline-none focus:border-blue-500/50 resize-none transition-all"
              rows={2}
              placeholder="Hỏi Thầy về bài toán này..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
            />
            <button 
              className="absolute right-4 bg-blue-500 hover:bg-blue-600 p-2 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={sendMessage}
              disabled={busy || !input.trim()}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
            </button>
          </div>
          <p className="text-[10px] text-center text-slate-500 mt-3">
            Nhấn Enter để gửi • Nhấn Shift+Enter để xuống dòng
          </p>
        </div>
      </main>

      <style jsx global>{`
        .prose p { margin-bottom: 0.5rem; }
        .prose ul { margin-left: 1rem; list-style-type: disc; }
        .prose ol { margin-left: 1rem; list-style-type: decimal; }
      `}</style>
    </div>
  );
}
