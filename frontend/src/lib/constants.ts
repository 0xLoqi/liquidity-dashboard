import type { DisplayMode } from "./types";

type CopyMap = Record<string, Record<DisplayMode, string>>;

export const REGIME_TAGLINES: CopyMap = {
  aggressive: {
    plain: "Conditions are favorable for crypto right now",
    finance: "Liquidity conditions favor risk-on positioning",
  },
  balanced: {
    plain: "Mixed signals \u2014 be selective, don\u2019t go all-in",
    finance: "Mixed signals suggest selective exposure",
  },
  defensive: {
    plain: "Warning signs suggest playing it safe",
    finance: "Liquidity headwinds warrant caution",
  },
};

export const REGIME_POSTURES: CopyMap = {
  aggressive: {
    plain: "Good conditions for investing in crypto",
    finance: "Full risk-on appropriate. Consider max exposure to quality assets.",
  },
  balanced: {
    plain: "Be picky about what you invest in",
    finance: "Neutral posture. Maintain moderate exposure, be selective.",
  },
  defensive: {
    plain: "Consider reducing exposure and holding cash",
    finance: "Risk-off posture. Reduce exposure, raise cash, avoid leverage.",
  },
};

export const METRIC_TITLES: CopyMap = {
  walcl: { plain: "Fed Money Printing", finance: "Fed Balance Sheet (WALCL)" },
  rrp: { plain: "Sideline Cash", finance: "Reverse Repo (RRP)" },
  hy_spread: { plain: "Risk Appetite", finance: "HY Credit Spreads" },
  dxy: { plain: "Dollar Strength", finance: "Dollar Index (DXY)" },
  stablecoin: { plain: "Crypto Dry Powder", finance: "Stablecoin Supply" },
};

export const METRIC_WHY: CopyMap = {
  walcl: {
    plain: "When the Fed prints money, crypto tends to go up",
    finance: "QE expansion injects liquidity into risk assets",
  },
  rrp: {
    plain: "Money leaving the sidelines is looking for returns",
    finance: "RRP drawdown releases capital into markets",
  },
  hy_spread: {
    plain: "When investors chase risky bonds, they\u2019ll chase crypto too",
    finance: "Tight spreads indicate risk-seeking behavior",
  },
  dxy: {
    plain: "A weaker dollar makes crypto more attractive globally",
    finance: "Dollar weakness eases global financial conditions",
  },
  stablecoin: {
    plain: "More stablecoins = more money ready to buy crypto",
    finance: "Stablecoin growth signals capital inflows to crypto",
  },
};

export const METRIC_SOURCES: Record<string, string> = {
  walcl: "FRED",
  rrp: "FRED",
  hy_spread: "FRED",
  dxy: "FRED",
  stablecoin: "DefiLlama",
};

export const METRIC_CHART_KEYS: Record<string, string> = {
  walcl: "walcl",
  rrp: "rrpontsyd",
  hy_spread: "bamlh0a0hym2",
  dxy: "dtwexbgs",
  stablecoin: "stablecoins",
};

export const REGIME_COLORS = {
  aggressive: "#10B981",
  balanced: "#F59E0B",
  defensive: "#EF4444",
} as const;

export const REGIME_ICONS = {
  aggressive: "\uD83D\uDE80",
  balanced: "\u2696\uFE0F",
  defensive: "\uD83D\uDEE1\uFE0F",
} as const;

export const FORCE_NAMES: CopyMap = {
  walcl: { plain: "Money Supply", finance: "WALCL" },
  rrp: { plain: "Sideline Cash", finance: "RRP" },
  hy_spread: { plain: "Risk Mood", finance: "HY Spread" },
  dxy: { plain: "Dollar", finance: "DXY" },
  stablecoin: { plain: "Crypto Cash", finance: "Stablecoin" },
};

export const METRIC_DESCRIPTIONS: Record<string, Record<DisplayMode, string>> = {
  walcl: {
    plain: "The Federal Reserve's balance sheet tracks how much money the central bank has pumped into the economy. When the Fed buys bonds (\"prints money\"), banks get more cash to lend, which eventually flows into investments including crypto. A growing balance sheet is bullish; shrinking means the Fed is pulling money out.",
    finance: "WALCL (Weighted Average of Loans at Commercial Banks) tracks the Fed's balance sheet size. Expansion via QE injects reserves into the banking system, increasing broad money supply and risk asset valuations. Contraction (QT) reverses this effect.",
  },
  rrp: {
    plain: "The Reverse Repo facility is like a parking lot for cash. Banks and money funds park money here overnight when they have nowhere better to put it. When money leaves this facility, it means investors are putting it to work in markets — which tends to be good for crypto.",
    finance: "The ON RRP facility absorbs excess liquidity from the banking system. Drawdowns release capital into money markets and risk assets, effectively increasing available liquidity. Rising RRP balances indicate excess reserves with no productive deployment.",
  },
  hy_spread: {
    plain: "This measures how much extra interest investors demand to buy risky corporate bonds vs. safe government bonds. When the gap is small, investors are feeling confident and willing to take risks — that same confidence usually spills over into crypto. A widening gap means fear is rising.",
    finance: "High-yield credit spreads (OAS) measure the risk premium over Treasuries for below-investment-grade debt. Tight spreads reflect risk-seeking behavior and easy financial conditions. Widening spreads signal credit stress and risk-off sentiment.",
  },
  dxy: {
    plain: "The Dollar Index measures how strong the US dollar is compared to other major currencies. When the dollar weakens, it makes assets priced in dollars (like Bitcoin) relatively cheaper for global buyers, and it usually means easier financial conditions worldwide.",
    finance: "The DXY (Dollar Index) measures USD against a basket of major currencies. Dollar weakness eases global financial conditions, reduces EM debt burdens, and is historically correlated with crypto strength. A rising DXY tightens global liquidity.",
  },
  stablecoin: {
    plain: "Stablecoins (like USDT and USDC) are dollars that live on the blockchain. When the total supply of stablecoins grows, it means more money has entered the crypto ecosystem and is sitting on the sidelines, ready to buy. Think of it as dry powder for crypto markets.",
    finance: "Aggregate stablecoin market cap serves as a proxy for fiat capital on-ramped into the crypto ecosystem. Growing supply indicates net capital inflows and available buying power. Contraction suggests capital outflows and reduced market depth.",
  },
};
