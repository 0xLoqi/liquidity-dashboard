"use client";

import { useState } from "react";
import type { DisplayMode, IndicatorData } from "@/lib/types";
import {
  METRIC_TITLES,
  METRIC_WHY,
  METRIC_SOURCES,
  METRIC_CHART_KEYS,
  METRIC_DESCRIPTIONS,
  REGIME_COLORS,
} from "@/lib/constants";
import { formatLargeNumber, formatPercentage } from "@/lib/formatters";
import { SparklineChart } from "./SparklineChart";

interface MetricCardProps {
  metricKey: string;
  indicator: IndicatorData;
  chartData: Array<Record<string, unknown>>;
  mode: DisplayMode;
  delay?: number;
}

export function MetricCard({
  metricKey,
  indicator,
  chartData,
  mode,
  delay = 0,
}: MetricCardProps) {
  const [expanded, setExpanded] = useState(false);
  const title = METRIC_TITLES[metricKey]?.[mode] ?? metricKey;
  const why = METRIC_WHY[metricKey]?.[mode] ?? "";
  const description = METRIC_DESCRIPTIONS?.[metricKey]?.[mode] ?? "";
  const source = METRIC_SOURCES[metricKey] ?? "";

  const score = indicator.score;
  const signalColor =
    score > 0
      ? REGIME_COLORS.aggressive
      : score < 0
        ? REGIME_COLORS.defensive
        : "#64748B";

  // Format value based on metric type
  let displayValue: string;
  if (metricKey === "walcl") {
    displayValue = formatLargeNumber(
      indicator.current != null ? indicator.current * 1e6 : null
    );
  } else if (metricKey === "rrp") {
    displayValue = formatLargeNumber(
      indicator.current != null ? indicator.current * 1e9 : null
    );
  } else if (metricKey === "hy_spread") {
    displayValue =
      indicator.current != null
        ? `${(indicator.current * 100).toFixed(0)} bps`
        : "N/A";
  } else if (metricKey === "dxy") {
    displayValue =
      indicator.current != null ? indicator.current.toFixed(2) : "N/A";
  } else if (metricKey === "stablecoin") {
    displayValue = formatLargeNumber(indicator.current);
  } else {
    displayValue = indicator.current?.toString() ?? "N/A";
  }

  // Delta text
  const deltaText = indicator.delta != null
    ? formatPercentage(indicator.delta, mode === "plain")
    : null;

  // Chart value key
  const chartKey = METRIC_CHART_KEYS[metricKey];
  const valueKey = metricKey === "stablecoin" ? "supply" : "value";

  return (
    <div
      className="boot-in glass-card rounded-xl p-4 flex flex-col"
      style={{ animationDelay: `${delay}s` }}
    >
      {/* Header row */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span
              className="w-1.5 h-1.5 rounded-full shrink-0"
              style={{ background: signalColor }}
            />
            <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted truncate">
              {title}
            </h3>
          </div>
          <p className="text-[10px] text-muted/50 leading-relaxed line-clamp-1">
            {why}
          </p>
        </div>
        <div className="flex items-center gap-1.5 shrink-0 ml-2">
          <span
            className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-surface-raised text-muted/60"
            style={{ fontFamily: "var(--font-mono)" }}
          >
            {indicator.weight}x
          </span>
          {description && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="w-5 h-5 rounded-full flex items-center justify-center text-muted/40 hover:text-accent hover:bg-accent/10 transition-colors"
              title="More info"
            >
              <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1a7 7 0 1 0 0 14A7 7 0 0 0 8 1zm-.75 4a.75.75 0 1 1 1.5 0 .75.75 0 0 1-1.5 0zM7 7.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v3.5a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5V7.5z" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Expanded description */}
      {expanded && description && (
        <div className="mb-3 p-2.5 rounded-lg bg-accent/5 border border-accent/10 text-[11px] text-foreground/70 leading-relaxed fade-in">
          {description}
        </div>
      )}

      {/* Value + delta */}
      <div className="flex items-baseline gap-2 mb-3">
        <span
          className="text-xl font-semibold tabular-nums text-foreground"
          style={{ fontFamily: "var(--font-mono)" }}
        >
          {displayValue}
        </span>
        {deltaText && (
          <span
            className="text-xs font-medium tabular-nums"
            style={{
              fontFamily: "var(--font-mono)",
              color: signalColor,
            }}
          >
            {indicator.delta_direction === "positive"
              ? "\u2191"
              : indicator.delta_direction === "negative"
                ? "\u2193"
                : "\u2192"}{" "}
            {deltaText}
          </span>
        )}
      </div>

      {/* Sparkline */}
      <div className="flex-1 -mx-1 min-h-0">
        <SparklineChart data={chartData} valueKey={valueKey} height={64} />
      </div>

      {/* Source */}
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-border/50">
        <span className="text-[9px] text-muted/40">{source}</span>
        <span className="text-[9px] text-muted/30">{indicator.reason}</span>
      </div>
    </div>
  );
}
