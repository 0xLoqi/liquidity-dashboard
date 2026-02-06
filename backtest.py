"""
Backtesting script for regime threshold optimization.
Fetches 2+ years of historical data and analyzes signal quality.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import os

from data.fetchers import fetch_fred_series, fetch_btc_price_history, fetch_stablecoin_history_combined
from config import FRED_SERIES, METRIC_THRESHOLDS, WEIGHTS, REGIME_THRESHOLDS


def fetch_historical_data(days_back: int = 730) -> Dict[str, pd.DataFrame]:
    """Fetch 2+ years of historical data for backtesting."""
    print(f"Fetching {days_back} days of historical data...")

    data = {}

    # FRED series
    for name, series_id in FRED_SERIES.items():
        print(f"  Fetching {name}...")
        data[name.lower()] = fetch_fred_series(series_id, days_back=days_back)

    # BTC price (need extra for 200 DMA)
    print("  Fetching BTC...")
    data["btc"] = fetch_btc_price_history(days=days_back)

    # Stablecoins
    print("  Fetching stablecoins...")
    data["stablecoins"] = fetch_stablecoin_history_combined()

    return data


def calculate_delta_at_date(df: pd.DataFrame, target_date: datetime,
                            days_back: int, value_col: str = "value") -> float:
    """Calculate the delta that would have been computed on a given date."""
    if df is None or len(df) == 0:
        return None

    df = df.sort_values("date")

    # Get data up to target_date
    df_at_date = df[df["date"] <= target_date]
    if len(df_at_date) < 2:
        return None

    # Current value (at target_date)
    current = df_at_date[value_col].iloc[-1]

    # Past value (days_back before target_date)
    past_target = target_date - timedelta(days=days_back)
    past_df = df_at_date[df_at_date["date"] <= past_target]

    if len(past_df) == 0:
        return None

    past = past_df[value_col].iloc[-1]

    if past == 0 or pd.isna(past) or pd.isna(current):
        return None

    return (current - past) / abs(past)


def calculate_ma_at_date(df: pd.DataFrame, target_date: datetime,
                         window: int, value_col: str = "price") -> float:
    """Calculate moving average at a given date."""
    if df is None or len(df) == 0:
        return None

    df = df.sort_values("date")
    df_at_date = df[df["date"] <= target_date]

    if len(df_at_date) < window:
        return None

    return df_at_date[value_col].iloc[-window:].mean()


def score_metric(delta: float, bullish_thresh: float, bearish_thresh: float,
                 inverted: bool = False) -> int:
    """Score a metric based on thresholds."""
    if delta is None:
        return 0

    if inverted:
        # For metrics where lower is bullish (RRP, DXY, HY spreads)
        if delta <= bullish_thresh:
            return 1
        elif delta >= bearish_thresh:
            return -1
    else:
        # For metrics where higher is bullish (WALCL, stablecoins)
        if delta >= bullish_thresh:
            return 1
        elif delta <= bearish_thresh:
            return -1

    return 0


def calculate_regime_score_at_date(data: Dict[str, pd.DataFrame],
                                   target_date: datetime,
                                   thresholds: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Calculate what the regime score would have been on a given date.
    """
    if thresholds is None:
        thresholds = METRIC_THRESHOLDS

    scores = {}

    # WALCL (Fed Balance Sheet) - higher = bullish
    walcl_delta = calculate_delta_at_date(data.get("walcl"), target_date, 28)
    walcl_score = score_metric(
        walcl_delta,
        thresholds.get("walcl_delta_bullish", 0.005),
        thresholds.get("walcl_delta_bearish", -0.005),
        inverted=False
    )
    scores["walcl"] = {"delta": walcl_delta, "score": walcl_score}

    # RRP (Reverse Repo) - lower = bullish (inverted)
    rrp_delta = calculate_delta_at_date(data.get("rrpontsyd"), target_date, 28)
    rrp_score = score_metric(
        rrp_delta,
        thresholds.get("rrp_delta_bullish", -0.05),
        thresholds.get("rrp_delta_bearish", 0.05),
        inverted=True
    )
    scores["rrp"] = {"delta": rrp_delta, "score": rrp_score}

    # HY Spreads - lower = bullish (inverted)
    hy_delta = calculate_delta_at_date(data.get("bamlh0a0hym2"), target_date, 28)
    hy_score = score_metric(
        hy_delta,
        thresholds.get("hy_spread_bullish", -0.10),
        thresholds.get("hy_spread_bearish", 0.10),
        inverted=True
    )
    scores["hy_spread"] = {"delta": hy_delta, "score": hy_score}

    # DXY - lower = bullish (inverted)
    dxy_delta = calculate_delta_at_date(data.get("dtwexbgs"), target_date, 28)
    dxy_score = score_metric(
        dxy_delta,
        thresholds.get("dxy_bullish", -0.02),
        thresholds.get("dxy_bearish", 0.02),
        inverted=True
    )
    scores["dxy"] = {"delta": dxy_delta, "score": dxy_score}

    # Stablecoins - higher = bullish
    stable_delta = calculate_delta_at_date(
        data.get("stablecoins"), target_date, 21, value_col="supply"
    )
    stable_score = score_metric(
        stable_delta,
        thresholds.get("stablecoin_bullish", 0.02),
        thresholds.get("stablecoin_bearish", -0.02),
        inverted=False
    )
    scores["stablecoin"] = {"delta": stable_delta, "score": stable_score}

    # BTC vs 200 DMA
    btc_df = data.get("btc")
    if btc_df is not None and len(btc_df) > 0:
        btc_at_date = btc_df[btc_df["date"] <= target_date]
        if len(btc_at_date) > 0:
            btc_price = btc_at_date["price"].iloc[-1]
            btc_ma = calculate_ma_at_date(btc_df, target_date, 200, "price")
            scores["btc"] = {
                "price": btc_price,
                "ma_200": btc_ma,
                "above_ma": btc_price > btc_ma if btc_ma else None
            }

    # Calculate weighted total
    total = 0
    total += scores["walcl"]["score"] * WEIGHTS["walcl"]
    total += scores["rrp"]["score"] * WEIGHTS["rrp"]
    total += scores["hy_spread"]["score"] * WEIGHTS["hy_spread"]
    total += scores["dxy"]["score"] * WEIGHTS["dxy"]
    total += scores["stablecoin"]["score"] * WEIGHTS["stablecoin"]

    return {
        "date": target_date,
        "individual": scores,
        "total_score": total,
    }


def calculate_forward_returns(btc_df: pd.DataFrame, date: datetime,
                              windows: List[int] = [7, 30, 90]) -> Dict[int, float]:
    """Calculate forward BTC returns from a given date."""
    if btc_df is None or len(btc_df) == 0:
        return {w: None for w in windows}

    btc_df = btc_df.sort_values("date")
    at_date = btc_df[btc_df["date"] <= date]

    if len(at_date) == 0:
        return {w: None for w in windows}

    start_price = at_date["price"].iloc[-1]
    returns = {}

    for window in windows:
        future_date = date + timedelta(days=window)
        future_df = btc_df[(btc_df["date"] >= future_date - timedelta(days=3)) &
                           (btc_df["date"] <= future_date + timedelta(days=3))]

        if len(future_df) > 0:
            end_price = future_df["price"].iloc[0]
            returns[window] = (end_price - start_price) / start_price
        else:
            returns[window] = None

    return returns


def run_backtest(data: Dict[str, pd.DataFrame],
                 start_date: datetime = None,
                 end_date: datetime = None,
                 thresholds: Dict[str, float] = None) -> pd.DataFrame:
    """
    Run backtest over historical period.
    Returns DataFrame with scores and forward returns for each date.
    """
    # Determine date range from BTC data
    btc_df = data.get("btc")
    if btc_df is None or len(btc_df) == 0:
        print("No BTC data available")
        return pd.DataFrame()

    btc_dates = btc_df["date"].sort_values()

    if start_date is None:
        # Start 230 days in (to have enough history for 200 DMA + 28 day delta)
        start_date = btc_dates.iloc[0] + timedelta(days=230)

    if end_date is None:
        # End 90 days ago (to have forward return data)
        end_date = btc_dates.iloc[-1] - timedelta(days=90)

    print(f"Running backtest from {start_date.date()} to {end_date.date()}")

    results = []
    current_date = start_date

    while current_date <= end_date:
        # Calculate regime score
        score_data = calculate_regime_score_at_date(data, current_date, thresholds)

        # Calculate forward returns
        forward_returns = calculate_forward_returns(btc_df, current_date)

        # Combine results
        result = {
            "date": current_date,
            "total_score": score_data["total_score"],
            "walcl_delta": score_data["individual"]["walcl"]["delta"],
            "walcl_score": score_data["individual"]["walcl"]["score"],
            "rrp_delta": score_data["individual"]["rrp"]["delta"],
            "rrp_score": score_data["individual"]["rrp"]["score"],
            "hy_delta": score_data["individual"]["hy_spread"]["delta"],
            "hy_score": score_data["individual"]["hy_spread"]["score"],
            "dxy_delta": score_data["individual"]["dxy"]["delta"],
            "dxy_score": score_data["individual"]["dxy"]["score"],
            "stable_delta": score_data["individual"]["stablecoin"]["delta"],
            "stable_score": score_data["individual"]["stablecoin"]["score"],
            "btc_above_ma": score_data["individual"].get("btc", {}).get("above_ma"),
            "return_7d": forward_returns.get(7),
            "return_30d": forward_returns.get(30),
            "return_90d": forward_returns.get(90),
        }
        results.append(result)

        current_date += timedelta(days=1)

    return pd.DataFrame(results)


def analyze_results(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze backtest results and generate statistics."""
    if len(df) == 0:
        return {}

    analysis = {
        "period": {
            "start": df["date"].min().strftime("%Y-%m-%d"),
            "end": df["date"].max().strftime("%Y-%m-%d"),
            "days": len(df),
        },
        "score_distribution": {
            "mean": df["total_score"].mean(),
            "std": df["total_score"].std(),
            "min": df["total_score"].min(),
            "max": df["total_score"].max(),
        },
        "signal_frequency": {},
        "return_by_score": {},
        "delta_statistics": {},
    }

    # Signal frequency for each metric
    for metric in ["walcl", "rrp", "hy", "dxy", "stable"]:
        col = f"{metric}_score"
        if col in df.columns:
            counts = df[col].value_counts()
            total = len(df)
            analysis["signal_frequency"][metric] = {
                "bullish": counts.get(1, 0) / total * 100,
                "neutral": counts.get(0, 0) / total * 100,
                "bearish": counts.get(-1, 0) / total * 100,
            }

    # Delta statistics
    for metric, col in [("walcl", "walcl_delta"), ("rrp", "rrp_delta"),
                        ("hy", "hy_delta"), ("dxy", "dxy_delta"),
                        ("stable", "stable_delta")]:
        if col in df.columns:
            deltas = df[col].dropna()
            if len(deltas) > 0:
                analysis["delta_statistics"][metric] = {
                    "mean": deltas.mean() * 100,
                    "std": deltas.std() * 100,
                    "min": deltas.min() * 100,
                    "max": deltas.max() * 100,
                    "p10": deltas.quantile(0.10) * 100,
                    "p25": deltas.quantile(0.25) * 100,
                    "p50": deltas.quantile(0.50) * 100,
                    "p75": deltas.quantile(0.75) * 100,
                    "p90": deltas.quantile(0.90) * 100,
                }

    # Returns by score bucket
    df_with_returns = df.dropna(subset=["return_30d"])
    if len(df_with_returns) > 0:
        # Create score buckets
        df_with_returns = df_with_returns.copy()
        df_with_returns["score_bucket"] = pd.cut(
            df_with_returns["total_score"],
            bins=[-7, -4, -1, 1, 4, 7],
            labels=["Very Bearish", "Bearish", "Neutral", "Bullish", "Very Bullish"]
        )

        for bucket in ["Very Bearish", "Bearish", "Neutral", "Bullish", "Very Bullish"]:
            bucket_data = df_with_returns[df_with_returns["score_bucket"] == bucket]
            if len(bucket_data) > 0:
                analysis["return_by_score"][bucket] = {
                    "count": len(bucket_data),
                    "avg_return_7d": bucket_data["return_7d"].mean() * 100,
                    "avg_return_30d": bucket_data["return_30d"].mean() * 100,
                    "avg_return_90d": bucket_data["return_90d"].mean() * 100,
                    "win_rate_30d": (bucket_data["return_30d"] > 0).mean() * 100,
                }

    return analysis


def print_analysis(analysis: Dict[str, Any]):
    """Print formatted analysis results."""
    print("\n" + "="*70)
    print("BACKTEST ANALYSIS RESULTS")
    print("="*70)

    period = analysis.get("period", {})
    print(f"\nPeriod: {period.get('start')} to {period.get('end')} ({period.get('days')} days)")

    # Score distribution
    score_dist = analysis.get("score_distribution", {})
    print(f"\nScore Distribution:")
    print(f"  Mean: {score_dist.get('mean', 0):.2f}")
    print(f"  Std:  {score_dist.get('std', 0):.2f}")
    print(f"  Range: {score_dist.get('min', 0):.1f} to {score_dist.get('max', 0):.1f}")

    # Signal frequency
    print("\n" + "-"*70)
    print("SIGNAL FREQUENCY (% of days)")
    print("-"*70)
    print(f"{'Metric':<12} {'Bullish':>10} {'Neutral':>10} {'Bearish':>10}")
    print("-"*70)

    for metric, freq in analysis.get("signal_frequency", {}).items():
        print(f"{metric:<12} {freq.get('bullish', 0):>9.1f}% {freq.get('neutral', 0):>9.1f}% {freq.get('bearish', 0):>9.1f}%")

    # Delta statistics
    print("\n" + "-"*70)
    print("DELTA STATISTICS (% change over window)")
    print("-"*70)
    print(f"{'Metric':<10} {'Mean':>8} {'Std':>8} {'P10':>8} {'P50':>8} {'P90':>8}")
    print("-"*70)

    for metric, stats in analysis.get("delta_statistics", {}).items():
        print(f"{metric:<10} {stats.get('mean', 0):>7.2f}% {stats.get('std', 0):>7.2f}% "
              f"{stats.get('p10', 0):>7.2f}% {stats.get('p50', 0):>7.2f}% {stats.get('p90', 0):>7.2f}%")

    # Returns by score
    print("\n" + "-"*70)
    print("BTC FORWARD RETURNS BY REGIME SCORE")
    print("-"*70)
    print(f"{'Score Bucket':<15} {'Days':>6} {'7d Ret':>10} {'30d Ret':>10} {'90d Ret':>10} {'Win Rate':>10}")
    print("-"*70)

    for bucket, stats in analysis.get("return_by_score", {}).items():
        print(f"{bucket:<15} {stats.get('count', 0):>6} "
              f"{stats.get('avg_return_7d', 0):>9.1f}% "
              f"{stats.get('avg_return_30d', 0):>9.1f}% "
              f"{stats.get('avg_return_90d', 0):>9.1f}% "
              f"{stats.get('win_rate_30d', 0):>9.1f}%")

    # Threshold recommendations
    print("\n" + "="*70)
    print("THRESHOLD ANALYSIS")
    print("="*70)

    delta_stats = analysis.get("delta_statistics", {})
    current_thresholds = METRIC_THRESHOLDS

    recommendations = []

    # Analyze each metric
    for metric, col in [("HY Spreads", "hy"), ("DXY", "dxy"), ("Stablecoins", "stable")]:
        if col in delta_stats:
            stats = delta_stats[col]
            freq = analysis.get("signal_frequency", {}).get(col, {})

            # Check if signals are firing at all
            total_signals = freq.get("bullish", 0) + freq.get("bearish", 0)

            if total_signals < 10:  # Less than 10% of days have signals
                p25 = abs(stats.get("p25", 0))
                p75 = abs(stats.get("p75", 0))

                # Suggest threshold at roughly 75th percentile of moves
                suggested = max(p25, p75) * 0.75

                recommendations.append({
                    "metric": metric,
                    "issue": f"Only {total_signals:.1f}% of days have signals",
                    "current_threshold": current_thresholds.get(f"{col}_bullish" if col != "stable" else "stablecoin_bullish", "N/A"),
                    "suggested": suggested,
                    "rationale": f"P25={stats.get('p25', 0):.2f}%, P75={stats.get('p75', 0):.2f}%"
                })

    if recommendations:
        print("\nRecommendations based on historical delta distributions:")
        for rec in recommendations:
            print(f"\n  {rec['metric']}:")
            print(f"    Issue: {rec['issue']}")
            if isinstance(rec['current_threshold'], float):
                print(f"    Current threshold: {rec['current_threshold']*100:.1f}%")
            print(f"    Suggested threshold: ~{rec['suggested']:.1f}%")
            print(f"    Rationale: {rec['rationale']}")
    else:
        print("\nNo major threshold issues detected.")


def main():
    """Main entry point for backtesting."""
    print("="*70)
    print("LIQUIDITY REGIME BACKTEST")
    print("="*70)

    # Check for API key
    if not os.environ.get("FRED_API_KEY"):
        print("\nWARNING: FRED_API_KEY not set. FRED data will not be available.")
        print("Set it with: set FRED_API_KEY=your_key\n")

    # Fetch data
    data = fetch_historical_data(days_back=730)  # 2 years

    # Check data availability
    print("\nData availability:")
    for name, df in data.items():
        if isinstance(df, pd.DataFrame) and len(df) > 0:
            print(f"  {name}: {len(df)} records, {df['date'].min().date()} to {df['date'].max().date()}")
        else:
            print(f"  {name}: No data")

    # Run backtest
    results_df = run_backtest(data)

    if len(results_df) == 0:
        print("\nNo backtest results. Check data availability.")
        return

    # Save raw results
    results_df.to_csv("backtest_results.csv", index=False)
    print(f"\nRaw results saved to backtest_results.csv ({len(results_df)} rows)")

    # Analyze
    analysis = analyze_results(results_df)
    print_analysis(analysis)

    return results_df, analysis


if __name__ == "__main__":
    main()
