"use client";

import { useState } from "react";
import { useDashboard } from "@/hooks/useDashboard";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import type { DisplayMode } from "@/lib/types";
import { METRIC_CHART_KEYS, REGIME_COLORS } from "@/lib/constants";

import { DisclaimerGate } from "@/components/DisclaimerGate";
import { Header } from "@/components/Header";
import { RegimeHero } from "@/components/RegimeHero";
import { ScoreGauge } from "@/components/ScoreGauge";
import { ForcesStrip } from "@/components/ForcesStrip";
import { MetricCard } from "@/components/MetricCard";
import { BtcGate } from "@/components/BtcGate";
import { TechDetails } from "@/components/TechDetails";
import { LearnMore } from "@/components/LearnMore";
import { ModeToggle } from "@/components/ModeToggle";
import { Footer } from "@/components/Footer";

const METRIC_ORDER = ["walcl", "rrp", "hy_spread", "dxy", "stablecoin"];

export default function Home() {
  const { dashboard, isLoading, isError, refresh } = useDashboard();
  const [disclaimerDismissed, setDisclaimerDismissed, hydrated] = useLocalStorage(
    "disclaimer_dismissed",
    false
  );
  const [sessionAccepted, setSessionAccepted] = useState(false);
  const [mode, setMode] = useLocalStorage<DisplayMode>("display_mode", "plain");

  // Wait for localStorage hydration before rendering
  if (!hydrated) return null;

  // Show disclaimer every session unless user checked "Don't show again"
  if (!disclaimerDismissed && !sessionAccepted) {
    return (
      <DisclaimerGate
        onAccept={(dontShowAgain) => {
          setSessionAccepted(true);
          if (dontShowAgain) {
            setDisclaimerDismissed(true);
          }
        }}
      />
    );
  }

  // Loading state
  if (isLoading && !dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center fade-in">
          <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center mx-auto mb-4 text-xl animate-pulse">
            🌊
          </div>
          <p className="text-sm text-muted">Loading FlowState...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (isError && !dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center fade-in max-w-sm">
          <p className="text-sm text-bearish mb-2">Failed to load dashboard data</p>
          <p className="text-xs text-muted/60 mb-4">
            The backend may be waking up. This can take up to 30 seconds on the free tier.
          </p>
          <button
            onClick={() => refresh()}
            className="px-4 py-2 text-sm font-medium bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!dashboard) return null;

  const {
    regime,
    score,
    max_possible,
    min_possible,
    days_in_regime,
    regime_start_date,
    thresholds,
    indicators,
    btc,
    charts,
    timestamp,
  } = dashboard;

  return (
    <div className="min-h-screen relative">
      {/* Flowing water background */}
      <div className="water-bg" aria-hidden="true">
        <div className="water-layer water-layer-1" />
        <div className="water-layer water-layer-2" />
        <div className="water-layer water-layer-3" />
      </div>

      {/* Regime-colored ambient glow at top */}
      <div
        className="ambient-glow"
        style={{ background: REGIME_COLORS[regime] }}
      />

      <div className="relative z-10 max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
        <Header onRefresh={refresh} />

        {/* Mode toggle */}
        <div className="flex justify-center mb-6">
          <ModeToggle mode={mode} onChange={setMode} />
        </div>

        {/* Regime Hero */}
        <RegimeHero
          regime={regime}
          score={score}
          daysInRegime={days_in_regime}
          regimeStartDate={regime_start_date}
          mode={mode}
        />

        {/* Score Gauge */}
        <div className="mt-6">
          <ScoreGauge
            score={score}
            min={min_possible}
            max={max_possible}
            thresholds={thresholds}
          />
        </div>

        {/* Forces Strip */}
        <div className="mt-6">
          <ForcesStrip indicators={indicators} mode={mode} />
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3 mt-8">
          {METRIC_ORDER.map((key, i) => {
            const indicator = indicators[key];
            if (!indicator) return null;

            const chartKey = METRIC_CHART_KEYS[key];
            const chartData =
              ((charts as unknown) as Record<string, Array<Record<string, unknown>>>)[
                chartKey
              ] ?? [];

            return (
              <MetricCard
                key={key}
                metricKey={key}
                indicator={indicator}
                chartData={chartData}
                mode={mode}
                delay={0.3 + i * 0.05}
              />
            );
          })}
        </div>

        {/* BTC Gate + Collapsible sections — side by side on wide screens */}
        <div className="mt-8 grid grid-cols-1 xl:grid-cols-[1fr_1fr] gap-6">
          <BtcGate btc={btc} chartData={charts.btc} mode={mode} />
          <div className="space-y-3">
            <TechDetails
              indicators={indicators}
              btcGatePassed={btc.above_200dma}
              thresholds={thresholds}
              totalScore={score}
            />
            <LearnMore />
          </div>
        </div>

        <Footer timestamp={timestamp} />
      </div>
    </div>
  );
}
