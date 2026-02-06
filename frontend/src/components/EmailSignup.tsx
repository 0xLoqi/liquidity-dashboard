"use client";

import { useState, useEffect } from "react";
import { subscribe, fetchSpots } from "@/lib/api";

interface EmailSignupProps {
  onSuccess?: () => void;
  onSpotsChange?: (spots: number) => void;
}

export function EmailSignup({ onSuccess, onSpotsChange }: EmailSignupProps) {
  const [email, setEmail] = useState("");
  const [cadence, setCadence] = useState("daily");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [spots, setSpots] = useState<number | null>(null);
  const [waitlisted, setWaitlisted] = useState(false);

  useEffect(() => {
    fetchSpots()
      .then((res) => setSpots(res.spots_remaining ?? null))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus("loading");
    try {
      const res = await subscribe(email, cadence);
      if (res.success) {
        setStatus("success");
        setMessage(res.message);
        setWaitlisted(!!res.waitlisted);
        if (res.spots_remaining != null) {
          setSpots(res.spots_remaining);
          onSpotsChange?.(res.spots_remaining);
        }
        setEmail("");
        setTimeout(() => onSuccess?.(), 2000);
      } else {
        setStatus("error");
        setMessage(res.detail || "Something went wrong.");
      }
    } catch {
      setStatus("error");
      setMessage("Failed to subscribe. Try again.");
    }
  };

  if (status === "success") {
    return (
      <div className="text-center py-2">
        <div className={`text-sm font-medium mb-1 ${waitlisted ? "text-balanced" : "text-bullish"}`}>
          {message}
        </div>
        <p className="text-[10px] text-muted/50">
          {waitlisted
            ? "We'll email you when a spot opens up."
            : "Check your spam folder if you don't see the welcome email."}
        </p>
      </div>
    );
  }

  const spotsLow = spots !== null && spots <= 20 && spots > 0;
  const spotsFull = spots !== null && spots <= 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <h3
          className="text-sm font-semibold text-foreground mb-0.5"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Get Regime Alerts
        </h3>
        <p className="text-[11px] text-muted/60">
          {spotsFull
            ? "All 100 spots are taken. Join the waitlist to get notified."
            : "Receive updates when the liquidity regime changes."}
        </p>
      </div>

      {/* Spots remaining badge */}
      {spots !== null && !spotsFull && (
        <div
          className={`flex items-center justify-between px-3 py-2 rounded-lg border text-[11px] font-medium ${
            spotsLow
              ? "bg-bearish/8 border-bearish/20 text-bearish"
              : "bg-accent/5 border-accent/15 text-accent"
          }`}
        >
          <span>{spotsLow ? "Almost full!" : "Limited spots"}</span>
          <span
            className="tabular-nums font-bold"
            style={{ fontFamily: "var(--font-mono)" }}
          >
            {spots} / 100 left
          </span>
        </div>
      )}

      {spotsFull && (
        <div className="flex items-center justify-between px-3 py-2 rounded-lg border bg-balanced/8 border-balanced/20 text-[11px] font-medium text-balanced">
          <span>All spots claimed</span>
          <span className="font-bold">Waitlist open</span>
        </div>
      )}

      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        required
        className="w-full px-3 py-2 text-sm bg-surface-raised border border-border rounded-lg text-foreground placeholder:text-muted/40 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors"
      />

      {!spotsFull && (
        <div className="flex gap-2">
          {(["daily", "weekly", "on_change"] as const).map((opt) => (
            <button
              key={opt}
              type="button"
              onClick={() => setCadence(opt)}
              className={`flex-1 px-2 py-1.5 text-[10px] font-medium rounded-md border transition-colors ${
                cadence === opt
                  ? "border-accent/40 bg-accent/10 text-accent"
                  : "border-border text-muted/60 hover:text-muted hover:border-border-bright"
              }`}
            >
              {opt === "on_change" ? "On Change" : opt.charAt(0).toUpperCase() + opt.slice(1)}
            </button>
          ))}
        </div>
      )}

      {status === "error" && (
        <p className="text-[11px] text-bearish">{message}</p>
      )}

      <button
        type="submit"
        disabled={status === "loading" || !email}
        className="w-full py-2 text-sm font-semibold bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {status === "loading"
          ? "Subscribing..."
          : spotsFull
            ? "Join Waitlist"
            : "Subscribe"}
      </button>
    </form>
  );
}
