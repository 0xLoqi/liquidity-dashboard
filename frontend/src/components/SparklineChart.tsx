"use client";

import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface SparklineChartProps {
  data: Array<Record<string, unknown>>;
  valueKey: string;
  height?: number;
}

export function SparklineChart({
  data,
  valueKey,
  height = 64,
}: SparklineChartProps) {
  if (!data || data.length < 2) return null;

  const first = Number(data[0]?.[valueKey]) || 0;
  const last = Number(data[data.length - 1]?.[valueKey]) || 0;
  const pctChange = first !== 0 ? (last - first) / Math.abs(first) : 0;

  const color =
    pctChange > 0.005
      ? "#10B981"
      : pctChange < -0.005
        ? "#EF4444"
        : "#64748B";

  const gradientId = `spark-${valueKey}-${Math.random().toString(36).slice(2, 6)}`;

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.15} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.[0]) return null;
              const val = Number(payload[0].value);
              const date = payload[0].payload?.date;
              return (
                <div className="px-2 py-1 rounded-md bg-surface-raised border border-border text-[10px]">
                  <div className="tabular-nums font-medium" style={{ fontFamily: "var(--font-mono)" }}>
                    {val.toLocaleString("en-US", { maximumFractionDigits: 2 })}
                  </div>
                  {date && <div className="text-muted">{date}</div>}
                </div>
              );
            }}
          />
          <Area
            type="monotone"
            dataKey={valueKey}
            stroke={color}
            strokeWidth={1.5}
            fill={`url(#${gradientId})`}
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
  );
}
