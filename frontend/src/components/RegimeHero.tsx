"use client";

import type { DisplayMode } from "@/lib/types";
import {
  REGIME_TAGLINES,
  REGIME_POSTURES,
  REGIME_COLORS,
  REGIME_ICONS,
} from "@/lib/constants";

interface RegimeHeroProps {
  regime: "aggressive" | "balanced" | "defensive";
  score: number;
  daysInRegime: number;
  regimeStartDate: string | null;
  mode: DisplayMode;
}

export function RegimeHero({
  regime,
  score,
  daysInRegime,
  mode,
}: RegimeHeroProps) {
  const color = REGIME_COLORS[regime];
  const icon = REGIME_ICONS[regime];
  const tagline = REGIME_TAGLINES[regime]?.[mode] ?? "";
  const posture = REGIME_POSTURES[regime]?.[mode] ?? "";
  const animClass =
    regime === "aggressive"
      ? "pulse-agg"
      : regime === "defensive"
        ? "pulse-def"
        : "pulse-bal";

  return (
    <section
      className="relative boot-in overflow-hidden rounded-2xl p-6 md:p-8"
      style={{ animationDelay: "0.1s" }}
    >
      {/* Ambient glow */}
      <div
        className="ambient-glow"
        style={{ background: color }}
      />

      {/* Border glow */}
      <div
        className="absolute inset-0 rounded-2xl pointer-events-none"
        style={{
          border: `1px solid ${color}20`,
          animation: `${
            regime === "aggressive"
              ? "pulse-aggressive"
              : regime === "defensive"
                ? "pulse-defensive"
                : "pulse-balanced"
          } 3s ease-in-out infinite`,
        }}
      />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center text-center">
        {/* Regime indicator */}
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mb-4"
          style={{
            background: `${color}12`,
            border: `1px solid ${color}30`,
          }}
        >
          {icon}
        </div>

        {/* Regime name */}
        <h2
          className="text-3xl md:text-4xl font-extrabold uppercase tracking-wider mb-1"
          style={{
            fontFamily: "var(--font-display)",
            color,
            textShadow: `0 0 40px ${color}40`,
          }}
        >
          {regime}
        </h2>

        {/* Score */}
        <div
          className="text-lg font-semibold tabular-nums mb-4"
          style={{
            fontFamily: "var(--font-mono)",
            color: `${color}cc`,
          }}
        >
          Score: {score >= 0 ? "+" : ""}
          {score.toFixed(1)}
        </div>

        {/* Tagline */}
        <p className="text-sm text-foreground/80 max-w-md mb-1">{tagline}</p>

        {/* Posture */}
        <p className="text-xs text-muted max-w-md mb-4">{posture}</p>

        {/* Days in regime */}
        {daysInRegime > 0 && (
          <div className="flex items-center gap-2 text-[11px] text-muted/60">
            <div
              className="w-1.5 h-1.5 rounded-full"
              style={{
                background: color,
                animation: "signal-blink 2s ease-in-out infinite",
              }}
            />
            In this regime for {daysInRegime} day{daysInRegime !== 1 ? "s" : ""}
          </div>
        )}
      </div>
    </section>
  );
}
