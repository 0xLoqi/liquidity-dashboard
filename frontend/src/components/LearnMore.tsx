"use client";

import * as Collapsible from "@radix-ui/react-collapsible";
import { useState } from "react";

export function LearnMore() {
  const [open, setOpen] = useState(false);

  return (
    <Collapsible.Root
      open={open}
      onOpenChange={setOpen}
      className="boot-in"
      style={{ animationDelay: "0.65s" }}
    >
      <Collapsible.Trigger asChild>
        <button className="w-full flex items-center justify-between py-3 px-4 glass-card rounded-xl text-sm text-muted hover:text-foreground transition-colors">
          <span className="flex items-center gap-2 font-medium">
            <svg
              width="14"
              height="14"
              viewBox="0 0 16 16"
              fill="currentColor"
              className="opacity-50"
            >
              <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4a.75.75 0 1 1 1.5 0 .75.75 0 0 1-1.5 0zM7 7.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v3.5a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5V7.5z" />
            </svg>
            Learn More: Why These Indicators?
          </span>
          <svg
            width="12"
            height="12"
            viewBox="0 0 12 12"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            className={`transition-transform ${open ? "rotate-180" : ""}`}
          >
            <path d="M3 4.5l3 3 3-3" />
          </svg>
        </button>
      </Collapsible.Trigger>

      <Collapsible.Content className="overflow-hidden">
        <div className="glass-card rounded-xl p-6 mt-3 text-sm text-foreground/70 leading-relaxed space-y-4">
          <div>
            <h4 className="text-foreground font-semibold mb-1">The Core Thesis</h4>
            <p>
              Crypto markets are heavily influenced by global liquidity conditions.
              When there&apos;s abundant cheap money in the system, risk assets
              (including crypto) tend to perform well. When liquidity tightens, they
              struggle.
            </p>
          </div>

          <div>
            <h4 className="text-foreground font-semibold mb-2">
              The Five Forces We Track
            </h4>
            <ol className="space-y-2 pl-4 list-decimal marker:text-muted/40">
              <li>
                <strong className="text-foreground/90">Fed Balance Sheet</strong> —
                When the Fed expands its balance sheet, it injects liquidity into the
                financial system.
              </li>
              <li>
                <strong className="text-foreground/90">Reverse Repo (RRP)</strong> —
                Cash parked here is &quot;on the sidelines.&quot; When it drains, that
                money often flows into markets.
              </li>
              <li>
                <strong className="text-foreground/90">High Yield Spreads</strong> —
                The gap between junk bonds and Treasuries. Tight spreads signal
                risk-seeking behavior.
              </li>
              <li>
                <strong className="text-foreground/90">Dollar Index (DXY)</strong> — A
                strong dollar tightens global financial conditions. Weakness is
                typically bullish for crypto.
              </li>
              <li>
                <strong className="text-foreground/90">Stablecoin Supply</strong> — A
                proxy for capital sitting on crypto&apos;s sidelines. Growing supply
                suggests capital ready to deploy.
              </li>
            </ol>
          </div>

          <div>
            <h4 className="text-foreground font-semibold mb-2">The Three Regimes</h4>
            <ul className="space-y-1.5">
              <li>
                <span className="text-[#10B981] font-semibold">Aggressive</span> —
                Multiple indicators bullish AND Bitcoin above 200-day average.
              </li>
              <li>
                <span className="text-[#F59E0B] font-semibold">Balanced</span> —
                Mixed signals. Be selective with investments.
              </li>
              <li>
                <span className="text-[#EF4444] font-semibold">Defensive</span> —
                Multiple indicators bearish. Consider reducing exposure.
              </li>
            </ul>
          </div>

          <p className="text-xs text-muted/50 pt-2 border-t border-border/30">
            Not financial advice. This is a framework for understanding macro
            conditions, not a trading signal.
          </p>
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
