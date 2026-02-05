"use client";

import * as Collapsible from "@radix-ui/react-collapsible";
import { useState } from "react";
import type { IndicatorData } from "@/lib/types";
import { REGIME_COLORS } from "@/lib/constants";

interface TechDetailsProps {
  indicators: Record<string, IndicatorData>;
  btcGatePassed: boolean;
  thresholds: { aggressive: number; defensive: number };
  totalScore: number;
}

const DISPLAY_NAMES: Record<string, string> = {
  walcl: "Fed Balance Sheet",
  rrp: "Reverse Repo (RRP)",
  hy_spread: "HY Credit Spreads",
  dxy: "Dollar Index (DXY)",
  stablecoin: "Stablecoin Supply",
};

export function TechDetails({
  indicators,
  btcGatePassed,
  thresholds,
  totalScore,
}: TechDetailsProps) {
  const [open, setOpen] = useState(false);

  return (
    <Collapsible.Root
      open={open}
      onOpenChange={setOpen}
      className="boot-in"
      style={{ animationDelay: "0.6s" }}
    >
      <Collapsible.Trigger asChild>
        <button className="w-full flex items-center justify-between py-3 px-4 glass-card rounded-xl text-sm text-muted hover:text-foreground transition-colors group">
          <span className="flex items-center gap-2 font-medium">
            <svg
              width="14"
              height="14"
              viewBox="0 0 16 16"
              fill="currentColor"
              className="opacity-50"
            >
              <path d="M2 2h4v4H2V2zm8 0h4v4h-4V2zM2 10h4v4H2v-4zm8 0h4v4h-4v-4z" />
            </svg>
            Technical Details &amp; Scoring
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
        <div className="grid md:grid-cols-[2fr_1fr] gap-3 mt-3">
          {/* Scoring table */}
          <div className="glass-card rounded-xl overflow-hidden">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-surface-raised">
                  <th className="text-left py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px]">
                    Metric
                  </th>
                  <th className="text-center py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px]">
                    Signal
                  </th>
                  <th className="text-center py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px]">
                    Weight
                  </th>
                  <th className="text-center py-2.5 px-3 text-muted/60 font-semibold uppercase tracking-wider text-[10px]">
                    Contrib
                  </th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(indicators).map(([key, ind]) => {
                  const signalColor =
                    ind.score > 0
                      ? REGIME_COLORS.aggressive
                      : ind.score < 0
                        ? REGIME_COLORS.defensive
                        : "#64748B";
                  return (
                    <tr
                      key={key}
                      className="border-t border-border/30"
                    >
                      <td className="py-2.5 px-3 text-foreground/80">
                        {DISPLAY_NAMES[key] ?? key}
                      </td>
                      <td className="text-center py-2.5 px-3">
                        <span className="inline-flex items-center gap-1.5">
                          <span
                            className="w-1.5 h-1.5 rounded-full"
                            style={{ background: signalColor }}
                          />
                          <span
                            className="tabular-nums font-medium"
                            style={{
                              fontFamily: "var(--font-mono)",
                              color: signalColor,
                            }}
                          >
                            {ind.score > 0 ? "+" : ""}
                            {ind.score}
                          </span>
                        </span>
                      </td>
                      <td
                        className="text-center py-2.5 px-3 text-muted/50 tabular-nums"
                        style={{ fontFamily: "var(--font-mono)" }}
                      >
                        {ind.weight}x
                      </td>
                      <td
                        className="text-center py-2.5 px-3 font-semibold tabular-nums"
                        style={{
                          fontFamily: "var(--font-mono)",
                          color: signalColor,
                        }}
                      >
                        {ind.weighted > 0 ? "+" : ""}
                        {ind.weighted.toFixed(1)}
                      </td>
                    </tr>
                  );
                })}
                <tr className="border-t border-accent/20 bg-accent/5">
                  <td className="py-2.5 px-3 font-semibold text-foreground">
                    Total Score
                  </td>
                  <td />
                  <td />
                  <td
                    className="text-center py-2.5 px-3 font-bold text-base tabular-nums text-accent"
                    style={{ fontFamily: "var(--font-mono)" }}
                  >
                    {totalScore > 0 ? "+" : ""}
                    {totalScore.toFixed(1)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Thresholds + BTC gate */}
          <div className="glass-card rounded-xl p-4 text-xs">
            <h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted/60 mb-3">
              Regime Thresholds
            </h4>
            <div className="space-y-2 mb-4">
              {[
                {
                  label: "Aggressive",
                  value: `\u2265 +${thresholds.aggressive.toFixed(1)}`,
                  color: REGIME_COLORS.aggressive,
                },
                {
                  label: "Balanced",
                  value: `${(thresholds.defensive + 0.1).toFixed(1)} to +${(thresholds.aggressive - 0.1).toFixed(1)}`,
                  color: REGIME_COLORS.balanced,
                },
                {
                  label: "Defensive",
                  value: `\u2264 ${thresholds.defensive.toFixed(1)}`,
                  color: REGIME_COLORS.defensive,
                },
              ].map((t) => (
                <div
                  key={t.label}
                  className="flex items-center justify-between py-1.5 px-2.5 rounded"
                  style={{ background: `${t.color}08` }}
                >
                  <span style={{ color: t.color }} className="font-medium">
                    {t.label}
                  </span>
                  <span
                    className="tabular-nums text-muted/50"
                    style={{ fontFamily: "var(--font-mono)" }}
                  >
                    {t.value}
                  </span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-border/50">
              <h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted/60 mb-2">
                BTC Gate
              </h4>
              <div className="flex items-center gap-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{
                    background: btcGatePassed
                      ? REGIME_COLORS.aggressive
                      : REGIME_COLORS.defensive,
                  }}
                />
                <span
                  className="font-medium"
                  style={{
                    color: btcGatePassed
                      ? REGIME_COLORS.aggressive
                      : REGIME_COLORS.defensive,
                  }}
                >
                  {btcGatePassed ? "Passed" : "Failed"}
                </span>
              </div>
              <p className="text-muted/40 text-[10px] mt-1 leading-relaxed">
                Required for Aggressive: BTC must trade above 200-day moving average
              </p>
            </div>
          </div>
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
