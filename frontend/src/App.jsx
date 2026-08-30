import { useEffect, useRef, useState } from "react";

const SUGGESTIONS = [
  "What are the fundamental rights in the Indian Constitution?",
  "What is the minimum age for employment under the Child Labour Act?",
  "How is maternity benefit calculated?",
];

function Sources({ sources }) {
  const [open, setOpen] = useState(false);
  if (!sources.length) return null;

  return (
    <div className="sources">
      <button
        type="button"
        className="sources-toggle"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? "▾" : "▸"} {sources.length} source
        {sources.length === 1 ? "" : "s"}
      </button>

      {open && (
        <ul className="sources-list">
          {sources.map((s, i) => (
            <li key={i}>
              <span className="source-name">{s.source}</span>
              <span className="source-meta">
                page {s.page + 1} · {s.category} · distance {s.score}
              </span>
              <p className="source-excerpt">{s.excerpt}…</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Message({ message }) {
  const isUser = message.role === "user";
  return (
    <article className={`message ${isUser ? "message-user" : "message-bot"}`}>
      <div className="bubble">
        <p className="message-text">{message.content}</p>
        {!isUser && message.error && <p className="message-error">{message.error}</p>}
      </div>
      {!isUser && message.sources && <Sources sources={message.sources} />}
      {!isUser && message.latencyMs != null && (
        <span className="latency">{(message.latencyMs / 1000).toFixed(1)}s</span>
      )}
    </article>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function ask(question) {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    // Send the conversation so far (before this question) as history.
    const history = messages.map(({ role, content }) => ({ role, content }));

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed, history }),
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `Request failed (${res.status})`);
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          latencyMs: data.latency_ms,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong answering that.",
          error: String(err.message || err),
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Indian Legal AI Assistant</h1>
        <p className="tagline">
          Plain-English answers grounded in real Indian legal documents, with citations.
        </p>
      </header>

      <main className="chat" aria-live="polite">
        {messages.length === 0 && (
          <section className="empty">
            <p>Ask a question about Indian law. For example:</p>
            <ul className="suggestions">
              {SUGGESTIONS.map((s) => (
                <li key={s}>
                  <button type="button" onClick={() => ask(s)}>
                    {s}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {messages.map((m, i) => (
          <Message key={i} message={m} />
        ))}

        {loading && (
          <article className="message message-bot">
            <div className="bubble">
              <p className="message-text thinking">Searching the documents…</p>
            </div>
          </article>
        )}

        <div ref={bottomRef} />
      </main>

      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
      >
        <label className="sr-only" htmlFor="question">
          Your legal question
        </label>
        <input
          id="question"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask your legal question…"
          autoComplete="off"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Ask
        </button>
      </form>

      <footer className="footer">
        For informational purposes only — this is not legal advice.
      </footer>
    </div>
  );
}
