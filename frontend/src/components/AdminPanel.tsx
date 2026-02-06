"use client";

import { useState, useEffect } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import * as Tabs from "@radix-ui/react-tabs";
import {
  adminLogin,
  getSubscribers,
  deleteSubscriber,
  getFeedback,
  sendTestBriefing,
  sendTestWelcome,
} from "@/lib/api";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function AdminPanel({ onRefresh }: { onRefresh?: () => void }) {
  const [open, setOpen] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [loading, setLoading] = useState(false);

  // Restore session
  useEffect(() => {
    const saved = sessionStorage.getItem("admin_token");
    if (saved) setToken(saved);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError("");
    try {
      const res = await adminLogin(password);
      setToken(res.token);
      sessionStorage.setItem("admin_token", res.token);
      setPassword("");
    } catch {
      setLoginError("Invalid password");
    }
    setLoading(false);
  };

  const handleLogout = () => {
    setToken(null);
    sessionStorage.removeItem("admin_token");
  };

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <button className="text-[10px] text-muted/30 hover:text-muted/60 transition-colors">
          Admin
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/80 z-50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg max-h-[80vh] glass-card rounded-2xl p-6 fade-in overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title
              className="text-base font-bold text-foreground"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Admin Panel
            </Dialog.Title>
            <Dialog.Close className="text-muted hover:text-foreground transition-colors p-1">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M1 1l12 12M1 13L13 1" />
              </svg>
            </Dialog.Close>
          </div>

          {!token ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="text-xs text-muted/60 block mb-1.5">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-surface-raised border border-border rounded-lg text-foreground focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors"
                  placeholder="Enter admin password"
                  autoFocus
                />
              </div>
              {loginError && (
                <p className="text-xs text-bearish">{loginError}</p>
              )}
              <button
                type="submit"
                disabled={loading || !password}
                className="w-full py-2 text-sm font-semibold bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50"
              >
                {loading ? "Authenticating..." : "Login"}
              </button>
            </form>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs text-bullish font-medium">Authenticated</span>
                <button
                  onClick={handleLogout}
                  className="text-[10px] text-muted/50 hover:text-bearish transition-colors"
                >
                  Logout
                </button>
              </div>
              <AdminTabs token={token} onRefresh={onRefresh} />
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function AdminTabs({ token, onRefresh }: { token: string; onRefresh?: () => void }) {
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch(`${API_URL}/api/refresh`, { method: "POST" });
      onRefresh?.();
    } catch { /* ignore */ }
    setRefreshing(false);
  };

  return (
    <Tabs.Root defaultValue="subscribers">
      <Tabs.List className="flex border-b border-border mb-4">
        <Tabs.Trigger
          value="subscribers"
          className="flex-1 py-2 text-xs font-medium text-muted/60 border-b-2 border-transparent transition-colors data-[state=active]:text-foreground data-[state=active]:border-accent"
        >
          Subscribers
        </Tabs.Trigger>
        <Tabs.Trigger
          value="emails"
          className="flex-1 py-2 text-xs font-medium text-muted/60 border-b-2 border-transparent transition-colors data-[state=active]:text-foreground data-[state=active]:border-accent"
        >
          Test Emails
        </Tabs.Trigger>
        <Tabs.Trigger
          value="feedback"
          className="flex-1 py-2 text-xs font-medium text-muted/60 border-b-2 border-transparent transition-colors data-[state=active]:text-foreground data-[state=active]:border-accent"
        >
          Feedback
        </Tabs.Trigger>
        <Tabs.Trigger
          value="tools"
          className="flex-1 py-2 text-xs font-medium text-muted/60 border-b-2 border-transparent transition-colors data-[state=active]:text-foreground data-[state=active]:border-accent"
        >
          Tools
        </Tabs.Trigger>
      </Tabs.List>
      <Tabs.Content value="subscribers">
        <SubscribersTab token={token} />
      </Tabs.Content>
      <Tabs.Content value="emails">
        <TestEmailsTab token={token} />
      </Tabs.Content>
      <Tabs.Content value="feedback">
        <FeedbackTab token={token} />
      </Tabs.Content>
      <Tabs.Content value="tools">
        <div className="space-y-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="w-full py-2 text-xs font-medium bg-surface-raised border border-border rounded-lg text-foreground hover:border-accent/30 transition-colors disabled:opacity-40"
          >
            {refreshing ? "Refreshing..." : "Force Refresh (clear cache + reload)"}
          </button>
        </div>
      </Tabs.Content>
    </Tabs.Root>
  );
}

function SubscribersTab({ token }: { token: string }) {
  const [subscribers, setSubscribers] = useState<
    Array<{ email: string; cadence: string; subscribed_at?: string }>
  >([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const res = await getSubscribers(token);
      setSubscribers(Array.isArray(res) ? res : res.subscribers || []);
    } catch {
      // ignore
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [token]);

  const handleDelete = async (email: string) => {
    try {
      await deleteSubscriber(email, token);
      setSubscribers((prev) => prev.filter((s) => s.email !== email));
    } catch {
      // ignore
    }
  };

  if (loading) {
    return <p className="text-xs text-muted/50 text-center py-4">Loading...</p>;
  }

  if (subscribers.length === 0) {
    return <p className="text-xs text-muted/50 text-center py-4">No subscribers yet.</p>;
  }

  return (
    <div className="space-y-2 max-h-60 overflow-y-auto">
      {subscribers.map((sub) => (
        <div
          key={sub.email}
          className="flex items-center justify-between px-3 py-2 bg-surface-raised rounded-lg"
        >
          <div className="min-w-0">
            <p className="text-xs text-foreground truncate">{sub.email}</p>
            <p className="text-[10px] text-muted/40">{sub.cadence}</p>
          </div>
          <button
            onClick={() => handleDelete(sub.email)}
            className="text-[10px] text-muted/40 hover:text-bearish transition-colors shrink-0 ml-2"
          >
            Remove
          </button>
        </div>
      ))}
    </div>
  );
}

function TestEmailsTab({ token }: { token: string }) {
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState<string | null>(null);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const send = async (type: "welcome" | "daily" | "regime_change") => {
    if (!email) return;
    setSending(type);
    setResult(null);
    try {
      let res;
      if (type === "welcome") {
        res = await sendTestWelcome(email, token);
      } else {
        res = await sendTestBriefing(email, type, token);
      }
      setResult(res);
    } catch {
      setResult({ success: false, message: "Request failed" });
    }
    setSending(null);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs text-muted/60 block mb-1.5">Recipient</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 text-sm bg-surface-raised border border-border rounded-lg text-foreground focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors"
          placeholder="email@example.com"
        />
      </div>
      <div className="space-y-2">
        <p className="text-[10px] text-muted/40 uppercase tracking-wider font-semibold">Send test email</p>
        <button
          onClick={() => send("welcome")}
          disabled={!email || sending !== null}
          className="w-full py-2 text-xs font-medium bg-surface-raised border border-border rounded-lg text-foreground hover:border-accent/30 transition-colors disabled:opacity-40"
        >
          {sending === "welcome" ? "Sending..." : "Welcome Email"}
        </button>
        <button
          onClick={() => send("daily")}
          disabled={!email || sending !== null}
          className="w-full py-2 text-xs font-medium bg-surface-raised border border-border rounded-lg text-foreground hover:border-accent/30 transition-colors disabled:opacity-40"
        >
          {sending === "daily" ? "Sending..." : "Daily Briefing (live data)"}
        </button>
        <button
          onClick={() => send("regime_change")}
          disabled={!email || sending !== null}
          className="w-full py-2 text-xs font-medium bg-surface-raised border border-border rounded-lg text-foreground hover:border-accent/30 transition-colors disabled:opacity-40"
        >
          {sending === "regime_change" ? "Sending..." : "Regime Change Alert (live data)"}
        </button>
      </div>
      {result && (
        <p className={`text-xs ${result.success ? "text-bullish" : "text-bearish"}`}>
          {result.message}
        </p>
      )}
    </div>
  );
}

function FeedbackTab({ token }: { token: string }) {
  const [feedback, setFeedback] = useState<
    Array<{ type: string; text: string; email?: string; timestamp?: string }>
  >([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await getFeedback(token);
        setFeedback(Array.isArray(res) ? res : res.feedback || []);
      } catch {
        // ignore
      }
      setLoading(false);
    };
    load();
  }, [token]);

  if (loading) {
    return <p className="text-xs text-muted/50 text-center py-4">Loading...</p>;
  }

  if (feedback.length === 0) {
    return <p className="text-xs text-muted/50 text-center py-4">No feedback yet.</p>;
  }

  return (
    <div className="space-y-2 max-h-60 overflow-y-auto">
      {feedback.map((fb, i) => (
        <div key={i} className="px-3 py-2 bg-surface-raised rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-medium text-accent uppercase">{fb.type}</span>
            {fb.email && (
              <span className="text-[10px] text-muted/40">{fb.email}</span>
            )}
          </div>
          <p className="text-xs text-foreground/80 leading-relaxed">{fb.text}</p>
        </div>
      ))}
    </div>
  );
}
