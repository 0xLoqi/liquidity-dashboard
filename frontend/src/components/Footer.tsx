"use client";

import { useState } from "react";
import * as Popover from "@radix-ui/react-popover";
import { FeedbackForm } from "./FeedbackForm";
import { AdminPanel } from "./AdminPanel";

interface FooterProps {
  timestamp?: string;
}

export function Footer({ timestamp }: FooterProps) {
  const [feedbackOpen, setFeedbackOpen] = useState(false);

  const formattedTime = timestamp
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
          <AdminPanel />
        </div>

        <div className="flex items-center gap-3">
          {formattedTime && (
            <>
              <span
                className="tabular-nums"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                Updated {formattedTime}
              </span>
              <span className="text-muted/20">|</span>
            </>
          )}
          <span>Not financial advice</span>
        </div>
      </div>
    </footer>
  );
}
