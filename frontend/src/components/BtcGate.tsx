"use client";

import type { DisplayMode, BtcData, BtcPoint } from "@/lib/types";
import { REGIME_COLORS } from "@/lib/constants";
import { formatPrice } from "@/lib/formatters";
import {
  AreaChart,
  Area,
  ReferenceLine,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface BtcGateProps {
  btc: BtcData;
  chartData: BtcPoint[];
  mode: DisplayMode;
}

export function BtcGate({ btc, chartData, mode }: BtcGateProps) {
  const passed = btc.above_200dma;
  const color = passed ? REGIME_COLORS.aggressive : REGIME_COLORS.defensive;
  const label = mode === "plain" ? "Bitcoin Trend" : "BTC vs 200 DMA (Gate)";

  return (
    <section className="boot-in" style={{ animationDelay: "0.55s" }}>
      {/* Status bar */}
      <div className="glass-card rounded-xl p-4 mb-3">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-3">
            <span className="text-lg">{passed ? "\uD83D\uDD13" : "\uD83D\uDD12"}</span>
            <div>
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                {label}
              </h3>
              <p className="text-[10px] text-muted/50">
                {mode === "plain"
                  ? "Bitcoin above its 200-day average confirms the uptrend"
                  : "BTC above 200 DMA required for Aggressive regime"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="text-base font-semibold tabular-nums"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              {formatPrice(btc.current_price)}
            </span>
            <span
              className="px-2 py-0.5 text-[10px] font-bold uppercase rounded-full"
              style={{
                color,
                background: `${color}15`,
                border: `1px solid ${color}30`,
              }}
            >
              {passed ? "Above" : "Below"}
            </span>
          </div>
        </div>
      </div>

      {/* BTC Chart */}
      {chartData && chartData.length > 2 && (
        <div className="glass-card rounded-xl p-4">
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={chartData}
                margin={{ top: 4, right: 4, bottom: 0, left: 4 }}
              >
                <defs>
                  <linearGradient id="btcGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={color} stopOpacity={0.1} />
                    <stop offset="100%" stopColor={color} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 9, fill: "#64748B" }}
                  tickLine={false}
                  axisLine={false}
                  interval="preserveStartEnd"
                  tickFormatter={(val: string) => {
                    const d = new Date(val);
                    return d.toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    });
                  }}
                />
                <YAxis
                  orientation="right"
                  tick={{ fontSize: 9, fill: "#64748B" }}
                  tickLine={false}
                  axisLine={false}
                  tickCount={4}
                  tickFormatter={(v: number) =>
                    `$${(v / 1000).toFixed(0)}K`
                  }
                  domain={["dataMin - 2000", "dataMax + 2000"]}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload?.[0]) return null;
                    return (
                      <div className="px-2 py-1 rounded-md bg-surface-raised border border-border text-[10px]">
                        <div
                          className="tabular-nums font-medium"
                          style={{ fontFamily: "var(--font-mono)" }}
                        >
                          {formatPrice(Number(payload[0].value))}
                        </div>
                        <div className="text-muted">{payload[0].payload?.date}</div>
                      </div>
                    );
                  }}
                />
                {btc.ma_200 && (
                  <ReferenceLine
                    y={btc.ma_200}
                    stroke="#3B82F6"
                    strokeDasharray="4 4"
                    strokeWidth={1}
                    label={{
                      value: "200 DMA",
                      position: "right",
                      fontSize: 9,
                      fill: "#3B82F6",
                    }}
                  />
                )}
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke={color}
                  strokeWidth={1.5}
                  fill="url(#btcGrad)"
                  dot={false}
                  activeDot={{
                    r: 3,
                    fill: color,
                    stroke: "var(--color-background)",
                    strokeWidth: 2,
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </section>
  );
}
