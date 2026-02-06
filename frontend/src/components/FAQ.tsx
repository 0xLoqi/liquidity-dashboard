"use client";

import * as Collapsible from "@radix-ui/react-collapsible";
import { useState } from "react";

const QUESTIONS = [
  {
    q: "What is FlowState?",
    a: "FlowState tracks 5 macro liquidity indicators to classify crypto market conditions into three regimes: Aggressive (risk-on), Balanced (mixed), and Defensive (risk-off). It's a framework for understanding whether the macro environment favors or hinders crypto.",
  },
  {
    q: "How often does the data update?",
    a: "The dashboard fetches fresh data every time you load it. Behind the scenes, a GitHub Actions job checks indicators every 4 hours and sends Discord alerts for regime changes. FRED data (Fed Balance Sheet, RRP, HY Spreads, DXY) updates weekly or daily depending on the series. BTC and stablecoin data updates daily.",
  },
  {
    q: "Why is the score positive when markets are crashing?",
    a: "FlowState tracks liquidity conditions, not price. Markets can crash on news, sentiment, or leverage unwinds while underlying liquidity conditions remain stable or improving. In fact, a positive score during a crash can be a contrarian signal\u2014the macro plumbing is intact even if prices panic.",
  },
  {
    q: "What triggers a regime change?",
    a: "The system uses hysteresis to prevent whipsawing. A regime change requires either 2 consecutive days above/below the threshold OR a score margin of more than 1.0 point from the threshold. This means the dashboard won't flip-flop on noise.",
  },
  {
    q: "What's the BTC Gate?",
    a: "Even if the liquidity score is high enough for Aggressive, the regime caps at Balanced unless Bitcoin is trading above its 200-day moving average. This prevents calling a risk-on environment when BTC's own trend is bearish.",
  },
  {
    q: "Is this financial advice?",
    a: "No. FlowState is an educational tool and analytical framework. It provides one lens for understanding macro conditions\u2014it's not a trading signal and should not be the sole basis for any investment decision.",
  },
  {
    q: "What APIs does this use?",
    a: "FRED (Federal Reserve Economic Data) for Fed Balance Sheet, Reverse Repo, HY Credit Spreads, and Dollar Index. CoinGecko for Bitcoin price data. DefiLlama for stablecoin supply data. All free-tier APIs.",
  },
  {
    q: "Can I get email alerts?",
    a: "Yes! Subscribe using the email form on the dashboard. You can choose daily briefings, weekly summaries, or alerts only when the regime changes.",
  },
];

export function FAQ() {
  const [open, setOpen] = useState(false);
  const [expandedQ, setExpandedQ] = useState<number | null>(null);

  return (
    <Collapsible.Root
      open={open}
      onOpenChange={setOpen}
      className="boot-in"
      style={{ animationDelay: "0.75s" }}
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
              <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zM7.25 11.5a.75.75 0 1 1 1.5 0 .75.75 0 0 1-1.5 0zm.41-6.59c-.78 0-1.41.44-1.41 1.09H5c0-1.46 1.23-2.34 2.66-2.34C9.14 3.66 10.25 4.5 10.25 6c0 1.07-.63 1.62-1.38 2.07-.62.38-.87.65-.87 1.18v.25H6.75v-.31c0-.9.5-1.4 1.19-1.83.63-.38.81-.62.81-1.12 0-.56-.44-.93-1.09-.93z" />
            </svg>
            Frequently Asked Questions
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

      <Collapsible.Content className="overflow-hidden data-[state=open]:animate-slideDown data-[state=closed]:animate-slideUp">
        <div className="glass-card rounded-xl p-4 mt-3">
          <div className="divide-y divide-border/30">
            {QUESTIONS.map((item, i) => (
              <button
                key={i}
                onClick={() => setExpandedQ(expandedQ === i ? null : i)}
                className="w-full text-left py-3 first:pt-0 last:pb-0"
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="text-sm text-foreground/90 font-medium leading-snug">
                    {item.q}
                  </span>
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 12 12"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    className={`shrink-0 mt-1 text-muted/40 transition-transform ${expandedQ === i ? "rotate-180" : ""}`}
                  >
                    <path d="M3 4.5l3 3 3-3" />
                  </svg>
                </div>
                {expandedQ === i && (
                  <p className="text-xs text-muted/70 leading-relaxed mt-2 pr-6">
                    {item.a}
                  </p>
                )}
              </button>
            ))}
          </div>
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
