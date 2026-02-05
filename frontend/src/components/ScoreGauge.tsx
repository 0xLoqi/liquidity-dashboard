"use client";

import { REGIME_COLORS } from "@/lib/constants";

interface ScoreGaugeProps {
  score: number;
  min: number;
  max: number;
  thresholds: { aggressive: number; defensive: number };
}

export function ScoreGauge({ score, min, max, thresholds }: ScoreGaugeProps) {
  const range = max - min;
  const normalize = (val: number) => ((val - min) / range) * 100;

  const scorePos = Math.max(2, Math.min(98, normalize(score)));
  const defEnd = normalize(thresholds.defensive);
  const aggStart = normalize(thresholds.aggressive);

  const scoreColor =
    score >= thresholds.aggressive
      ? REGIME_COLORS.aggressive
      : score <= thresholds.defensive
        ? REGIME_COLORS.defensive
        : REGIME_COLORS.balanced;

  return (
    <div
      className="boot-in w-full px-4 md:px-0"
      style={{ animationDelay: "0.2s" }}
    >
      {/* Labels */}
      <div className="flex justify-between items-center mb-2 text-[10px] font-medium uppercase tracking-wider text-muted/50">
        <span>Defensive</span>
        <span>Balanced</span>
        <span>Aggressive</span>
      </div>

      {/* Gauge bar */}
      <div className="relative h-8 w-full rounded-lg overflow-hidden bg-surface-raised border border-border">
        {/* Zones */}
        <div
          className="absolute inset-y-0 left-0 opacity-30"
          style={{
            width: `${defEnd}%`,
            background: `linear-gradient(90deg, ${REGIME_COLORS.defensive}20, ${REGIME_COLORS.defensive}08)`,
          }}
        />
        <div
          className="absolute inset-y-0 opacity-30"
          style={{
            left: `${aggStart}%`,
            right: 0,
            background: `linear-gradient(90deg, ${REGIME_COLORS.aggressive}08, ${REGIME_COLORS.aggressive}20)`,
          }}
        />

        {/* Threshold lines */}
        <div
          className="absolute inset-y-0 w-px"
          style={{
            left: `${defEnd}%`,
            background: `${REGIME_COLORS.defensive}40`,
          }}
        />
        <div
          className="absolute inset-y-0 w-px"
          style={{
            left: `${aggStart}%`,
            background: `${REGIME_COLORS.aggressive}40`,
          }}
        />

        {/* Center line */}
        <div
          className="absolute inset-y-0 w-px bg-border"
          style={{ left: "50%" }}
        />

        {/* Score marker */}
        <div
          className="gauge-marker absolute top-1/2 -translate-y-1/2 -translate-x-1/2 z-10"
          style={{ left: `${scorePos}%` }}
        >
          {/* Glow */}
          <div
            className="absolute inset-0 -m-2 rounded-full blur-md opacity-60"
            style={{ background: scoreColor }}
          />
          {/* Diamond */}
          <div
            className="relative w-3.5 h-3.5 rotate-45 rounded-[2px] border-2"
            style={{
              background: scoreColor,
              borderColor: `${scoreColor}`,
              boxShadow: `0 0 8px ${scoreColor}80`,
            }}
          />
        </div>
      </div>

      {/* Scale numbers */}
      <div
        className="flex justify-between mt-1 text-[9px] tabular-nums text-muted/40"
        style={{ fontFamily: "var(--font-mono)" }}
      >
        <span>{min.toFixed(1)}</span>
        <span>{thresholds.defensive.toFixed(1)}</span>
        <span>0.0</span>
        <span>+{thresholds.aggressive.toFixed(1)}</span>
        <span>+{max.toFixed(1)}</span>
      </div>
    </div>
  );
}
