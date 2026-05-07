"use client";

import { useState } from "react";
import * as Popover from "@radix-ui/react-popover";
import { FeedbackForm } from "./FeedbackForm";
import { AdminPanel } from "./AdminPanel";

interface FooterProps {
  timestamp?: string;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

function formatRelative(timestamp?: string): string | null {
  if (!timestamp) return null;
  const then = new Date(timestamp).getTime();
  if (Number.isNaN(then)) return null;
  const diffSec = Math.max(0, Math.round((Date.now() - then) / 1000));
  if (diffSec < 60) return "just now";
  const diffMin = Math.round(diffSec / 60);
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `${diffHr} hr ago`;
  const diffDay = Math.round(diffHr / 24);
  return `${diffDay} day${diffDay === 1 ? "" : "s"} ago`;
}

export function Footer({ timestamp, onRefresh, isRefreshing }: FooterProps) {
  const [feedbackOpen, setFeedbackOpen] = useState(false);

  const relative = formatRelative(timestamp);
  const fullTime = timestamp
    ? new Date(timestamp).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
        timeZoneName: "short",
      })
    : null;

  return (
    <footer
      className="boot-in border-t border-border/50 mt-8 pt-6 pb-8 px-4 md:px-0"
      style={{ animationDelay: "0.7s" }}
    >
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-muted/50">
        <div className="flex items-center gap-3">
          <span>
            Data from{" "}
            <a
              href="https://fred.stlouisfed.org"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted/70 hover:text-foreground transition-colors"
            >
              FRED
            </a>
            ,{" "}
            <a
              href="https://www.coingecko.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted/70 hover:text-foreground transition-colors"
            >
              CoinGecko
            </a>
            ,{" "}
            <a
              href="https://defillama.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted/70 hover:text-foreground transition-colors"
            >
              DefiLlama
            </a>
          </span>
          <span className="text-muted/20">|</span>
          <Popover.Root open={feedbackOpen} onOpenChange={setFeedbackOpen}>
            <Popover.Trigger className="text-muted/50 hover:text-foreground transition-colors">
              Feedback
            </Popover.Trigger>
            <Popover.Portal>
              <Popover.Content
                side="top"
                align="start"
                sideOffset={8}
                className="z-50 w-80 p-4 glass-card rounded-xl shadow-2xl shadow-black/50 fade-in"
              >
                <FeedbackForm onSuccess={() => setFeedbackOpen(false)} />
                <Popover.Arrow className="fill-border" />
              </Popover.Content>
            </Popover.Portal>
          </Popover.Root>
          <span className="text-muted/20">|</span>
          <AdminPanel onRefresh={onRefresh} />
        </div>

        <div className="flex items-center gap-3">
          {relative && (
            <>
              <span
                className="tabular-nums"
                style={{ fontFamily: "var(--font-mono)" }}
                title={fullTime ?? undefined}
              >
                {isRefreshing ? "Refreshing..." : `Updated ${relative}`}
              </span>
              {onRefresh && (
                <button
                  type="button"
                  onClick={onRefresh}
                  disabled={isRefreshing}
                  aria-label="Refresh data"
                  className="text-muted/50 hover:text-foreground disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <svg
                    width="11"
                    height="11"
                    viewBox="0 0 16 16"
                    fill="currentColor"
                    className={isRefreshing ? "animate-spin" : ""}
                  >
                    <path d="M8 3a5 5 0 0 0-4.546 2.916.75.75 0 0 1-1.36-.633A6.5 6.5 0 0 1 14.5 8a.75.75 0 0 1-1.5 0A5 5 0 0 0 8 3zm6.75 4.25a.75.75 0 0 1 .75.75 6.5 6.5 0 0 1-12.406 2.717.75.75 0 0 1 1.36-.634A5 5 0 0 0 13 8a.75.75 0 0 1 .75-.75z" />
                    <path d="M2.5 1.75a.75.75 0 0 0-1.5 0v3a.75.75 0 0 0 .75.75h3a.75.75 0 0 0 0-1.5H2.5v-2.25zm11 13.5a.75.75 0 0 0 1.5 0v-3a.75.75 0 0 0-.75-.75h-3a.75.75 0 0 0 0 1.5h2.25v2.25z" />
                  </svg>
                </button>
              )}
              <span className="text-muted/20">|</span>
            </>
          )}
          <span>Not financial advice</span>
        </div>
      </div>
    </footer>
  );
}
