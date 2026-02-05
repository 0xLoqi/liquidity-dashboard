"use client";

import { useState, useEffect } from "react";
import * as Popover from "@radix-ui/react-popover";
import { EmailSignup } from "./EmailSignup";
import { fetchSpots } from "@/lib/api";

export function Header({ onRefresh }: { onRefresh?: () => void }) {
  const [open, setOpen] = useState(false);
  const [spots, setSpots] = useState<number | null>(null);

  useEffect(() => {
    fetchSpots()
      .then((res) => setSpots(res.spots_remaining ?? null))
      .catch(() => {});
  }, []);

  return (
    <header className="flex items-center justify-between px-4 md:px-0 py-5 boot-in">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center text-xl">
          🌊
        </div>
        <h1
          className="text-lg font-bold tracking-tight text-foreground"
          style={{ fontFamily: "var(--font-display)" }}
        >
          FlowState
        </h1>
        <span className="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-accent bg-accent/8 border border-accent/20 rounded-full">
          Live
        </span>
      </div>

      <div className="flex items-center gap-2">
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 text-muted hover:text-foreground transition-colors rounded-lg hover:bg-surface-raised"
            title="Refresh data"
          >
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
              <path d="M1 1v5h5M15 15v-5h-5" />
              <path d="M13.5 6A6 6 0 0 0 3 3.5L1 6M2.5 10A6 6 0 0 0 13 12.5L15 10" />
            </svg>
          </button>
        )}
        <Popover.Root open={open} onOpenChange={setOpen}>
          <Popover.Trigger asChild>
            <button className="relative flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-accent bg-accent/8 border border-accent/20 rounded-lg hover:bg-accent/15 transition-colors">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1a2 2 0 0 1 2 2v.5a5.5 5.5 0 0 1 3 4.5v2l1.5 2H1.5L3 10V8a5.5 5.5 0 0 1 3-4.5V3a2 2 0 0 1 2-2zM6 13a2 2 0 1 0 4 0H6z" />
              </svg>
              Get Alerts
              {spots !== null && spots > 0 && spots <= 50 && (
                <span className="absolute -top-1.5 -right-1.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[9px] font-bold text-white bg-bearish rounded-full ring-2 ring-background animate-pulse">
                  {spots}
                </span>
              )}
              {spots !== null && spots <= 0 && (
                <span className="absolute -top-1.5 -right-1.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[9px] font-bold text-white bg-bearish rounded-full ring-2 ring-background">
                  !
                </span>
              )}
            </button>
          </Popover.Trigger>
          <Popover.Portal>
            <Popover.Content
              side="bottom"
              align="end"
              sideOffset={8}
              className="z-50 w-80 p-4 glass-card rounded-xl shadow-2xl shadow-black/50 fade-in"
            >
              <EmailSignup onSuccess={() => setOpen(false)} />
              <Popover.Arrow className="fill-border" />
            </Popover.Content>
          </Popover.Portal>
        </Popover.Root>
      </div>
    </header>
  );
}
