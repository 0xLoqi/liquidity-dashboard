export interface DashboardResponse {
  regime: "aggressive" | "balanced" | "defensive";
  score: number;
  max_possible: number;
  min_possible: number;
  btc_above_200dma: boolean;
  btc_distance_from_200dma: number | null;
  days_in_regime: number;
  regime_start_date: string | null;
  regime_info: RegimeInfo;
  thresholds: { aggressive: number; defensive: number };
  indicators: Record<string, IndicatorData>;
  btc: BtcData;
  charts: ChartsData;
  explanation: Explanation;
  timestamp: string;
}

export interface RegimeInfo {
  pending_flip: boolean;
  proposed_regime: string;
  consecutive_days: number;
  score_trend: "improving" | "deteriorating" | "flat";
  days_until_flip: number | null;
}

export interface IndicatorData {
  current: number | null;
  delta: number | null;
  delta_direction: "positive" | "negative" | "neutral";
  score: number;
  weighted: number;
  weight: number;
  reason: string;
  latest_date: string | null;
}

export interface BtcData {
  current_price: number | null;
  ma_200: number | null;
  above_200dma: boolean;
}

export interface ChartsData {
  walcl: ChartPoint[];
  rrpontsyd: ChartPoint[];
  bamlh0a0hym2: ChartPoint[];
  dtwexbgs: ChartPoint[];
  stablecoins: StablecoinPoint[];
  btc: BtcPoint[];
}

export interface ChartPoint {
  date: string;
  value: number;
}

export interface StablecoinPoint {
  date: string;
  supply: number;
}

export interface BtcPoint {
  date: string;
  price: number;
}

export interface Explanation {
  headline: string;
  body: string;
  posture: string;
  warnings: string;
}

export type DisplayMode = "plain" | "finance";
