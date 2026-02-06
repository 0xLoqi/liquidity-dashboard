"""Run backtest with API key."""
import os
os.environ["FRED_API_KEY"] = "4574110873011811dc27f89e0eb20d61"

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from data.fetchers import fetch_fred_series, fetch_stablecoin_history_combined
from config import FRED_SERIES, METRIC_THRESHOLDS, WEIGHTS


def fetch_btc_free(days: int = 365) -> pd.DataFrame:
    """Fetch BTC price from CoinGecko free tier."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": min(days, 365), "interval": "daily"}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.normalize()
        return df[["date", "price"]].sort_values("date").reset_index(drop=True)
    except Exception as e:
        print(f"Error fetching BTC: {e}")
        return pd.DataFrame(columns=["date", "price"])


def calculate_delta_at_date(df, target_date, days_back, value_col="value"):
    if df is None or len(df) == 0:
        return None
    df = df.sort_values("date")
    df_at_date = df[df["date"] <= target_date]
    if len(df_at_date) < 2:
        return None
    current = df_at_date[value_col].iloc[-1]
    past_target = target_date - timedelta(days=days_back)
    past_df = df_at_date[df_at_date["date"] <= past_target]
    if len(past_df) == 0:
        return None
    past = past_df[value_col].iloc[-1]
    if past == 0 or pd.isna(past) or pd.isna(current):
        return None
    return (current - past) / abs(past)


def score_metric(delta, bullish_thresh, bearish_thresh, inverted=False):
    if delta is None:
        return 0
    if inverted:
        if delta <= bullish_thresh:
            return 1
        elif delta >= bearish_thresh:
            return -1
    else:
        if delta >= bullish_thresh:
            return 1
        elif delta <= bearish_thresh:
            return -1
    return 0


def main():
    print("="*70)
    print("LIQUIDITY REGIME THRESHOLD BACKTEST")
    print("="*70)

    # Fetch FRED data (2 years)
    print("\nFetching FRED data (2 years)...")
    fred_data = {}
    for name, series_id in FRED_SERIES.items():
        print(f"  {name}...", end=" ")
        df = fetch_fred_series(series_id, days_back=730)
        fred_data[name.lower()] = df
        if len(df) > 0:
            print(f"{len(df)} rows")
        else:
            print("NO DATA")

    # Fetch BTC (1 year max for free)
    print("\nFetching BTC (1 year)...")
    btc_df = fetch_btc_free(365)
    print(f"  {len(btc_df)} rows")

    # Fetch stablecoins (full history)
    print("\nFetching stablecoins...")
    stable_df = fetch_stablecoin_history_combined()
    # Filter to last 2 years for relevance
    cutoff = datetime.now() - timedelta(days=730)
    stable_df = stable_df[stable_df["date"] >= cutoff]
    print(f"  {len(stable_df)} rows (last 2 years)")

    # Analyze each metric's delta distribution
    print("\n" + "="*70)
    print("DELTA DISTRIBUTION ANALYSIS")
    print("="*70)

    results = {}

    for metric_name, key, value_col, window, inverted, thresh_key in [
        ("WALCL (Fed Printing)", "walcl", "value", 28, False, "walcl"),
        ("RRP (Sideline Cash)", "rrpontsyd", "value", 28, True, "rrp"),
        ("HY Spreads (Risk Appetite)", "bamlh0a0hym2", "value", 28, True, "hy_spread"),
        ("DXY (Dollar Strength)", "dtwexbgs", "value", 28, True, "dxy"),
        ("Stablecoins (Crypto Dry Powder)", "stable", "supply", 21, False, "stablecoin"),
    ]:
        df = stable_df if key == "stable" else fred_data.get(key)
        if df is None or len(df) < window + 30:
            print(f"\n{metric_name}: Not enough data")
            continue

        df = df.sort_values("date")
        deltas = []
        for i in range(window, len(df)):
            target_date = df["date"].iloc[i]
            delta = calculate_delta_at_date(df.iloc[:i+1].copy(), target_date, window, value_col)
            if delta is not None:
                deltas.append({"date": target_date, "delta": delta})

        if not deltas:
            continue

        deltas_df = pd.DataFrame(deltas)
        delta_series = deltas_df["delta"]

        # Get current thresholds
        bullish_key = f"{thresh_key}_bullish" if thresh_key in ["stablecoin", "hy_spread", "dxy"] else f"{thresh_key}_delta_bullish"
        bearish_key = f"{thresh_key}_bearish" if thresh_key in ["stablecoin", "hy_spread", "dxy"] else f"{thresh_key}_delta_bearish"
        current_bullish = METRIC_THRESHOLDS.get(bullish_key)
        current_bearish = METRIC_THRESHOLDS.get(bearish_key)

        # Calculate signal frequencies
        if inverted:
            bullish_pct = (delta_series <= current_bullish).mean() * 100
            bearish_pct = (delta_series >= current_bearish).mean() * 100
        else:
            bullish_pct = (delta_series >= current_bullish).mean() * 100
            bearish_pct = (delta_series <= current_bearish).mean() * 100

        neutral_pct = 100 - bullish_pct - bearish_pct

        print(f"\n{metric_name}")
        print(f"  Period: {deltas_df['date'].min().date()} to {deltas_df['date'].max().date()}")
        print(f"  Data points: {len(delta_series)}")
        print(f"\n  Delta Distribution:")
        print(f"    P5:   {delta_series.quantile(0.05)*100:>7.2f}%")
        print(f"    P25:  {delta_series.quantile(0.25)*100:>7.2f}%")
        print(f"    P50:  {delta_series.quantile(0.50)*100:>7.2f}%")
        print(f"    P75:  {delta_series.quantile(0.75)*100:>7.2f}%")
        print(f"    P95:  {delta_series.quantile(0.95)*100:>7.2f}%")
        print(f"\n  Current Threshold: {current_bullish*100:+.1f}% / {current_bearish*100:+.1f}%")
        print(f"  Signal Frequency: Bullish {bullish_pct:.1f}% | Neutral {neutral_pct:.1f}% | Bearish {bearish_pct:.1f}%")

        if bullish_pct + bearish_pct < 15:
            print(f"  ** WARNING: Only {bullish_pct + bearish_pct:.1f}% of days have signals!")

        results[metric_name] = {
            "p05": delta_series.quantile(0.05),
            "p25": delta_series.quantile(0.25),
            "p50": delta_series.quantile(0.50),
            "p75": delta_series.quantile(0.75),
            "p95": delta_series.quantile(0.95),
            "bullish_pct": bullish_pct,
            "bearish_pct": bearish_pct,
            "current_bullish": current_bullish,
            "current_bearish": current_bearish,
        }

    # Forward return analysis with BTC
    print("\n" + "="*70)
    print("REGIME SCORE VS BTC RETURNS")
    print("="*70)

    if len(btc_df) < 60:
        print("Not enough BTC data for return analysis")
        return

    # Calculate daily regime scores over BTC period
    btc_df = btc_df.sort_values("date")
    start_date = btc_df["date"].min() + timedelta(days=30)
    end_date = btc_df["date"].max() - timedelta(days=30)

    score_data = []
    current_date = start_date

    while current_date <= end_date:
        # Calculate each metric's score
        total_score = 0

        # WALCL
        walcl_delta = calculate_delta_at_date(fred_data.get("walcl"), current_date, 28)
        walcl_score = score_metric(walcl_delta, 0.005, -0.005, inverted=False)
        total_score += walcl_score * WEIGHTS["walcl"]

        # RRP
        rrp_delta = calculate_delta_at_date(fred_data.get("rrpontsyd"), current_date, 28)
        rrp_score = score_metric(rrp_delta, -0.05, 0.05, inverted=True)
        total_score += rrp_score * WEIGHTS["rrp"]

        # HY Spreads
        hy_delta = calculate_delta_at_date(fred_data.get("bamlh0a0hym2"), current_date, 28)
        hy_score = score_metric(hy_delta, -0.10, 0.10, inverted=True)
        total_score += hy_score * WEIGHTS["hy_spread"]

        # DXY
        dxy_delta = calculate_delta_at_date(fred_data.get("dtwexbgs"), current_date, 28)
        dxy_score = score_metric(dxy_delta, -0.02, 0.02, inverted=True)
        total_score += dxy_score * WEIGHTS["dxy"]

        # Stablecoins
        stable_delta = calculate_delta_at_date(stable_df, current_date, 21, "supply")
        stable_score = score_metric(stable_delta, 0.02, -0.02, inverted=False)
        total_score += stable_score * WEIGHTS["stablecoin"]

        # Forward BTC return (30 days)
        btc_at_date = btc_df[btc_df["date"] <= current_date]
        if len(btc_at_date) > 0:
            start_price = btc_at_date["price"].iloc[-1]
            future_date = current_date + timedelta(days=30)
            btc_future = btc_df[(btc_df["date"] >= future_date - timedelta(days=3)) &
                               (btc_df["date"] <= future_date + timedelta(days=3))]
            if len(btc_future) > 0:
                end_price = btc_future["price"].iloc[0]
                btc_return = (end_price - start_price) / start_price

                score_data.append({
                    "date": current_date,
                    "score": total_score,
                    "btc_return_30d": btc_return,
                })

        current_date += timedelta(days=1)

    if not score_data:
        print("No overlapping data for return analysis")
        return

    score_df = pd.DataFrame(score_data)

    # Bucket by score
    def bucket_score(s):
        if s <= -4:
            return "Defensive (<=-4)"
        elif s <= -1:
            return "Bearish (-4 to -1)"
        elif s <= 1:
            return "Neutral (-1 to 1)"
        elif s <= 4:
            return "Bullish (1 to 4)"
        else:
            return "Aggressive (>4)"

    score_df["bucket"] = score_df["score"].apply(bucket_score)

    print(f"\nPeriod: {score_df['date'].min().date()} to {score_df['date'].max().date()}")
    print(f"Data points: {len(score_df)}")

    print(f"\n{'Score Bucket':<22} {'Days':>6} {'Avg 30d Ret':>12} {'Win Rate':>10}")
    print("-"*54)

    for bucket in ["Defensive (<=-4)", "Bearish (-4 to -1)", "Neutral (-1 to 1)",
                   "Bullish (1 to 4)", "Aggressive (>4)"]:
        subset = score_df[score_df["bucket"] == bucket]
        if len(subset) > 0:
            avg_ret = subset["btc_return_30d"].mean() * 100
            win_rate = (subset["btc_return_30d"] > 0).mean() * 100
            print(f"{bucket:<22} {len(subset):>6} {avg_ret:>11.1f}% {win_rate:>9.1f}%")

    # Recommendations
    print("\n" + "="*70)
    print("THRESHOLD RECOMMENDATIONS")
    print("="*70)

    for metric_name, data in results.items():
        bullish_pct = data["bullish_pct"]
        bearish_pct = data["bearish_pct"]

        if bullish_pct + bearish_pct < 15:
            p25 = data["p25"]
            p75 = data["p75"]
            current = data["current_bullish"]

            print(f"\n{metric_name}:")
            print(f"  ISSUE: Only {bullish_pct + bearish_pct:.1f}% of days have signals")
            print(f"  Current threshold: {abs(current)*100:.1f}%")
            print(f"  Historical range (P25-P75): {p25*100:.2f}% to {p75*100:.2f}%")

            # Suggest threshold at P75 level
            suggested = max(abs(p25), abs(p75)) * 0.6
            print(f"  SUGGESTED: {suggested*100:.2f}% (would capture more tail events)")


if __name__ == "__main__":
    main()

