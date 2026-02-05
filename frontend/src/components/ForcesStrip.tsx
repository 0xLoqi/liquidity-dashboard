"use client";

import type { DisplayMode, IndicatorData } from "@/lib/types";
import { FORCE_NAMES, REGIME_COLORS } from "@/lib/constants";

interface ForcesStripProps {
  indicators: Record<string, IndicatorData>;
  mode: DisplayMode;
}

const FORCE_ORDER = ["walcl", "rrp", "hy_spread", "dxy", "stablecoin"];

export function ForcesStrip({ indicators, mode }: ForcesStripProps) {
  return (
    <div
      className="boot-in flex flex-wrap justify-center gap-2 px-4 md:px-0"
      style={{ animationDelay: "0.25s" }}
    >
      {FORCE_ORDER.map((key) => {
        const ind = indicators[key];
        if (!ind) return null;

        const score = ind.score;
        const dotColor =
          score > 0
            ? REGIME_COLORS.aggressive
            : score < 0
              ? REGIME_COLORS.defensive
              : "#64748B";

        return (
          <div
            key={key}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-raised border border-border text-xs"
          >
            <span
              className="w-2 h-2 rounded-full shrink-0"
              style={{
                background: dotColor,
                boxShadow: score !== 0 ? `0 0 6px ${dotColor}60` : "none",
              }}
            />
            <span className="text-foreground/70 font-medium">
              {FORCE_NAMES[key]?.[mode] ?? key}
            </span>
          </div>
        );
      })}
    </div>
  );
}
