"use client";

import { useState } from "react";
import { submitFeedback } from "@/lib/api";

export function FeedbackForm({ onSuccess }: { onSuccess?: () => void }) {
  const [type, setType] = useState("general");
  const [text, setText] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    setStatus("loading");
    try {
      const res = await submitFeedback(type, text.trim(), email || undefined);
      if (res.success || res.status === "ok") {
        setStatus("success");
        setMessage("Thanks for your feedback!");
        setText("");
        setEmail("");
        setTimeout(() => onSuccess?.(), 1500);
      } else {
        setStatus("error");
        setMessage(res.detail || "Something went wrong.");
      }
    } catch {
      setStatus("error");
      setMessage("Failed to submit. Try again.");
    }
  };

  if (status === "success") {
    return (
      <div className="text-center py-4">
        <div className="text-sm text-bullish font-medium">{message}</div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <h3
          className="text-sm font-semibold text-foreground mb-0.5"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Send Feedback
        </h3>
        <p className="text-[11px] text-muted/60">
          Bug reports, feature requests, or general thoughts.
        </p>
      </div>

      <div className="flex gap-2">
        {(["general", "bug", "feature", "data"] as const).map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => setType(opt)}
            className={`flex-1 px-2 py-1.5 text-[10px] font-medium rounded-md border transition-colors capitalize ${
              type === opt
                ? "border-accent/40 bg-accent/10 text-accent"
                : "border-border text-muted/60 hover:text-muted hover:border-border-bright"
            }`}
          >
            {opt}
          </button>
        ))}
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="What's on your mind?"
        required
        rows={3}
        className="w-full px-3 py-2 text-sm bg-surface-raised border border-border rounded-lg text-foreground placeholder:text-muted/40 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors resize-none"
      />

      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email (optional, for follow-up)"
        className="w-full px-3 py-2 text-sm bg-surface-raised border border-border rounded-lg text-foreground placeholder:text-muted/40 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors"
      />

      {status === "error" && (
        <p className="text-[11px] text-bearish">{message}</p>
      )}

      <button
        type="submit"
        disabled={status === "loading" || !text.trim()}
        className="w-full py-2 text-sm font-semibold bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {status === "loading" ? "Sending..." : "Send Feedback"}
      </button>
    </form>
  );
}
