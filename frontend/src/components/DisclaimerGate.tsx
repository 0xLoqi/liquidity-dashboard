"use client";

import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";

interface DisclaimerGateProps {
  onAccept: (dontShowAgain: boolean) => void;
}

export function DisclaimerGate({ onAccept }: DisclaimerGateProps) {
  const [dontShow, setDontShow] = useState(false);

  return (
    <Dialog.Root open>
      <Dialog.Portal>
        {/* Water scene background */}
        <Dialog.Overlay className="fixed inset-0 z-50 water-scene">
          <div className="water-scene-fx" />
        </Dialog.Overlay>
        <Dialog.Content className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-md rounded-2xl p-8 disclaimer-enter relative overflow-hidden"
            style={{
              background: "linear-gradient(145deg, rgba(30, 41, 59, 0.92) 0%, rgba(15, 23, 42, 0.88) 100%)",
              border: "1px solid rgba(59, 130, 246, 0.25)",
              backdropFilter: "blur(20px)",
              boxShadow: "0 0 80px rgba(59, 130, 246, 0.08), 0 25px 50px rgba(0, 0, 0, 0.3)",
            }}
          >
            {/* Animated shimmer top bar */}
            <div
              className="absolute top-0 left-0 right-0 h-[3px]"
              style={{
                background: "linear-gradient(90deg, transparent, #3B82F6, #60A5FA, #3B82F6, transparent)",
                backgroundSize: "200% 100%",
                animation: "shimmer 3s ease-in-out infinite",
              }}
            />

            {/* Water emoji title */}
            <Dialog.Title
              className="text-3xl font-bold tracking-tight mb-2 disclaimer-text-1"
              style={{ fontFamily: "var(--font-display)" }}
            >
              <span className="mr-2">🌊</span> FlowState
            </Dialog.Title>

            <Dialog.Description className="text-sm text-muted mb-6 leading-relaxed disclaimer-text-2">
              A macro liquidity regime tracker for crypto markets. This tool classifies
              conditions into Aggressive, Balanced, or Defensive regimes based on five
              key liquidity indicators.
            </Dialog.Description>

            <div className="space-y-3 text-xs text-muted/80 mb-6 pl-4 border-l border-blue-500/30 disclaimer-text-3">
              <p>
                This is an educational tool, not financial advice. Past conditions
                do not predict future results.
              </p>
              <p>
                Data sourced from FRED, CoinGecko, and DefiLlama. Signals may be
                delayed and should not be used as sole basis for investment decisions.
              </p>
            </div>

            <label className="flex items-center gap-2.5 mb-6 cursor-pointer group disclaimer-text-4">
              <div className="relative">
                <input
                  type="checkbox"
                  checked={dontShow}
                  onChange={(e) => setDontShow(e.target.checked)}
                  className="peer sr-only"
                />
                <div className="w-4 h-4 rounded border border-border bg-surface-raised peer-checked:bg-accent peer-checked:border-accent transition-colors" />
                <svg
                  className="absolute inset-0 w-4 h-4 text-white opacity-0 peer-checked:opacity-100 transition-opacity pointer-events-none"
                  viewBox="0 0 16 16"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M4 8l3 3 5-5" />
                </svg>
              </div>
              <span className="text-xs text-muted/60 group-hover:text-muted transition-colors">
                Don&apos;t show this again
              </span>
            </label>

            <button
              onClick={() => onAccept(dontShow)}
              className="w-full py-3 px-4 text-white text-sm font-semibold rounded-lg transition-colors tracking-wide disclaimer-button"
              style={{
                background: "linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)",
                boxShadow: "0 4px 14px rgba(59, 130, 246, 0.4)",
              }}
            >
              I Understand — Enter Dashboard
            </button>

            <p className="text-[10px] text-muted/50 text-center mt-4 disclaimer-text-5">
              By continuing, you acknowledge this is not financial advice.
            </p>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
