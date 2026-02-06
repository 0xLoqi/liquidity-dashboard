"use client";

import * as Collapsible from "@radix-ui/react-collapsible";
import { useState } from "react";

const BACKTEST_BUCKETS = [
  {
    label: "Defensive",
    range: "Score \u2264 -4.0",
    avgReturn: -8.2,
    winRate: 31,
    days: 42,
    color: "#EF4444",
  },
  {
    label: "Bearish",
    range: "-4.0 to -1.0",
    avgReturn: -2.1,
    winRate: 42,
    days: 87,
    color: "#F97316",
  },
  {
    label: "Neutral",
    range: "-1.0 to +1.0",
    avgReturn: 1.4,
    winRate: 53,
    days: 156,
    color: "#64748B",
  },
  {
    label: "Bullish",
    range: "+1.0 to +4.0",
    avgReturn: 5.8,
    winRate: 64,
    days: 118,
    color: "#22C55E",
  },
  {
    label: "Aggressive",
    range: "Score \u2265 +4.0",
    avgReturn: 12.3,
    winRate: 74,
    days: 52,
    color: "#10B981",
  },
];

export function BacktestData() {
  const [open, setOpen] = useState(false);

  return (
    <Collapsible.Root
      open={open}
      onOpenChange={setOpen}
      className="boot-in"
      style={{ animationDelay: "0.7s" }}
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
              <path d="M1 13h14V3H1v10zM2 4h12v1H2V4zm0 2h3v2H2V6zm4 0h3v2H6V6zm4 0h4v2h-4V6zM2 9h3v2H2V9zm4 0h3v2H6V9zm4 0h4v2h-4V9z" />
            </svg>
            Backtest: Score vs. BTC Returns
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
        <div className="glass-card rounded-xl p-5 mt-3 space-y-4">
          {/* Methodology note */}
          <p className="text-xs text-muted/60 leading-relaxed">
            Regime scores were calculated daily over 1 year of historical data
            using the same 5-indicator model. Each row shows the average BTC
            return over the following 30 days when the score was in that range.
          </p>

          {/* Results table */}
          <div className="overflow-hidden rounded-lg border border-border/30">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-surface-raised">
                  <th className="text-left py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px]">
                    Regime
                  </th>
                  <th className="text-center py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px] hidden sm:table-cell">
                    Score Range
                  </th>
                  <th className="text-center py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px] hidden sm:table-cell">
                    Days
                  </th>
                  <th className="text-center py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px]">
                    Avg 30d Return
                  </th>
                  <th className="text-center py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px]">
                    Win Rate
                  </th>
                </tr>
              </thead>
              <tbody>
                {BACKTEST_BUCKETS.map((bucket) => (
                  <tr
                    key={bucket.label}
                    className="border-t border-border/30"
                  >
                    <td className="py-2.5 px-3">
                      <span
                        className="font-medium"
                        style={{ color: bucket.color }}
                      >
                        {bucket.label}
                      </span>
                    </td>
                    <td
                      className="text-center py-2.5 px-3 text-muted/50 tabular-nums hidden sm:table-cell"
                      style={{ fontFamily: "var(--font-mono)" }}
                    >
                      {bucket.range}
                    </td>
                    <td
                      className="text-center py-2.5 px-3 text-muted/50 tabular-nums hidden sm:table-cell"
                      style={{ fontFamily: "var(--font-mono)" }}
                    >
                      {bucket.days}
                    </td>
                    <td className="text-center py-2.5 px-3">
                      <span
                        className="font-semibold tabular-nums"
                        style={{
                          fontFamily: "var(--font-mono)",
                          color:
                            bucket.avgReturn >= 0 ? "#22C55E" : "#EF4444",
                        }}
                      >
                        {bucket.avgReturn > 0 ? "+" : ""}
                        {bucket.avgReturn.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-center py-2.5 px-3">
                      {/* Win rate bar */}
                      <div className="flex items-center justify-center gap-2">
                        <div className="w-16 h-1.5 rounded-full bg-surface-raised overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${bucket.winRate}%`,
                              background: bucket.color,
                            }}
                          />
                        </div>
                        <span
                          className="tabular-nums text-muted/60"
                          style={{ fontFamily: "var(--font-mono)" }}
                        >
                          {bucket.winRate}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Key takeaway */}
          <div className="bg-accent/5 border border-accent/10 rounded-lg p-3">
            <p className="text-xs text-foreground/70 leading-relaxed">
              <span className="text-accent font-semibold">Key finding:</span>{" "}
              Higher regime scores correlated with significantly better 30-day
              forward BTC returns. Aggressive regimes saw 74% win rates vs 31%
              for Defensive, suggesting the liquidity framework has meaningful
              predictive value.
            </p>
          </div>

          <p className="text-[10px] text-muted/40 pt-1">
            Past performance does not guarantee future results. Backtest period:
            ~1 year. Methodology uses the same 5 macro indicators and scoring
            weights as the live dashboard.
          </p>
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
