"""
Backtesting script that uses cached data + free APIs.
Works without API keys using available data.
"""

import sqlite3
import pickle
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import METRIC_THRESHOLDS, WEIGHTS


def load_from_cache() -> Dict[str, Any]:
    """Load whatever data is in the cache."""
    db_path = Path(__file__).parent / "cache.db"

    data = {}
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT key, data, timestamp FROM cache")
        rows = cursor.fetchall()

        for key, data_blob, timestamp in rows:
            try:
                data[key] = {
                    "data": pickle.loads(data_blob),
                    "timestamp": timestamp
                }
            except Exception as e:
                print(f"Error loading {key}: {e}")

    return data


def fetch_btc_free(days: int = 365) -> pd.DataFrame:
    """Fetch BTC price from CoinGecko free tier (max ~365 days without key)."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": min(days, 365),  # Free tier limit
        "interval": "daily"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        prices = data.get("prices", [])
        if not prices:
            return pd.DataFrame(columns=["date", "price"])

        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.normalize()
        df = df[["date", "price"]]
        df = df.sort_values("date").reset_index(drop=True)

        return df

    except Exception as e:
        print(f"Error fetching BTC: {e}")
        return pd.DataFrame(columns=["date", "price"])


def fetch_stablecoins_free() -> pd.DataFrame:
    """Fetch stablecoin data from DefiLlama (no auth required)."""
    try:
        response = requests.get(
            "https://stablecoins.llama.fi/stablecoincharts/all",
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return pd.DataFrame(columns=["date", "supply"])

        records = []
        for item in data:
            try:
                date_val = item.get("date", 0)
                if isinstance(date_val, str):
                    date_val = int(date_val)
                date = datetime.fromtimestamp(date_val)

                total_circ = item.get("totalCirculatingUSD", {})
                if isinstance(total_circ, dict):
                    total = sum(v for v in total_circ.values() if isinstance(v, (int, float)))
                else:
                    total = 0

                records.append({"date": date, "supply": total})
            except (ValueError, TypeError):
                continue

        df = pd.DataFrame(records)
        df = df.sort_values("date").reset_index(drop=True)

        return df

    except Exception as e:
        print(f"Error fetching stablecoins: {e}")
        return pd.DataFrame(columns=["date", "supply"])


def calculate_delta_at_date(df: pd.DataFrame, target_date: datetime,
                            days_back: int, value_col: str = "value") -> Optional[float]:
    """Calculate the delta that would have been computed on a given date."""
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


def calculate_ma_at_date(df: pd.DataFrame, target_date: datetime,
                         window: int, value_col: str = "price") -> Optional[float]:
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


def extract_fred_from_cache(cache_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """Extract FRED data from cache if available."""
    fred_data = {}

    all_data = cache_data.get("all_data", {}).get("data")
    if all_data:
        fred = all_data.get("fred", {})
        for key, df in fred.items():
            if isinstance(df, pd.DataFrame) and len(df) > 0:
                fred_data[key.lower()] = df

    return fred_data


def run_analysis_with_available_data():
    """Run analysis with whatever data is available."""
    print("="*70)
    print("LIQUIDITY REGIME THRESHOLD ANALYSIS")
    print("="*70)

    # Load cached data
    print("\nLoading cached data...")
    cache_data = load_from_cache()

    if cache_data:
        print(f"Found {len(cache_data)} cached entries")
        for key in cache_data.keys():
            print(f"  - {key}")

    # Extract FRED data from cache
    fred_data = extract_fred_from_cache(cache_data)
    if fred_data:
        print(f"\nFRED data available from cache:")
        for key, df in fred_data.items():
            if len(df) > 0:
                print(f"  {key}: {len(df)} records, {df['date'].min().date()} to {df['date'].max().date()}")

    # Fetch fresh data from free APIs
    print("\nFetching BTC data (free API)...")
    btc_df = fetch_btc_free(days=365)
    if len(btc_df) > 0:
        print(f"  BTC: {len(btc_df)} records, {btc_df['date'].min().date()} to {btc_df['date'].max().date()}")

    print("\nFetching stablecoin data (free API)...")
    stable_df = fetch_stablecoins_free()
    if len(stable_df) > 0:
        print(f"  Stablecoins: {len(stable_df)} records, {stable_df['date'].min().date()} to {stable_df['date'].max().date()}")

    # Analyze delta distributions
    print("\n" + "="*70)
    print("HISTORICAL DELTA ANALYSIS")
    print("="*70)

    # Stablecoin analysis - filter to last 2 years for relevance
    if len(stable_df) > 21:
        cutoff = datetime.now() - timedelta(days=730)
        stable_recent = stable_df[stable_df["date"] >= cutoff].copy()
        print(f"\n--- STABLECOIN SUPPLY (21-day delta, last 2 years) ---")
        analyze_metric_deltas(stable_recent, 21, "supply", "stablecoin")

    # FRED data analysis if available
    for metric, key in [("WALCL (Fed Balance Sheet)", "walcl"),
                        ("RRP (Reverse Repo)", "rrpontsyd"),
                        ("HY Spreads", "bamlh0a0hym2"),
                        ("DXY", "dtwexbgs")]:
        df = fred_data.get(key)
        if df is not None and len(df) > 28:
            print(f"\n--- {metric} (28-day delta) ---")
            analyze_metric_deltas(df, 28, "value", key)

    # BTC return analysis by stablecoin regime (use recent data)
    if len(btc_df) > 0 and len(stable_df) > 0:
        print("\n" + "="*70)
        print("STABLECOIN SIGNAL VS BTC RETURNS")
        print("="*70)
        # Filter to overlapping period
        cutoff = datetime.now() - timedelta(days=365)
        stable_recent = stable_df[stable_df["date"] >= cutoff].copy()
        analyze_stablecoin_vs_btc(stable_recent, btc_df)

    # Threshold recommendations
    print("\n" + "="*70)
    print("THRESHOLD RECOMMENDATIONS")
    print("="*70)
    generate_recommendations(stable_df, fred_data)


def analyze_metric_deltas(df: pd.DataFrame, window: int, value_col: str, metric_name: str):
    """Analyze the distribution of deltas for a metric."""
    if len(df) < window + 30:
        print(f"  Not enough data for {metric_name}")
        return

    df = df.sort_values("date")

    # Calculate rolling deltas
    deltas = []
    for i in range(window, len(df)):
        target_date = df["date"].iloc[i]
        delta = calculate_delta_at_date(df.iloc[:i+1].copy(), target_date, window, value_col)
        if delta is not None:
            deltas.append({
                "date": target_date,
                "delta": delta
            })

    if not deltas:
        print(f"  Could not calculate deltas for {metric_name}")
        return

    deltas_df = pd.DataFrame(deltas)
    delta_series = deltas_df["delta"]

    print(f"  Period: {deltas_df['date'].min().date()} to {deltas_df['date'].max().date()}")
    print(f"  Data points: {len(delta_series)}")
    print(f"\n  Delta Distribution (as %):")
    print(f"    Mean:   {delta_series.mean()*100:>7.2f}%")
    print(f"    Std:    {delta_series.std()*100:>7.2f}%")
    print(f"    Min:    {delta_series.min()*100:>7.2f}%")
    print(f"    Max:    {delta_series.max()*100:>7.2f}%")
    print(f"    P5:     {delta_series.quantile(0.05)*100:>7.2f}%")
    print(f"    P10:    {delta_series.quantile(0.10)*100:>7.2f}%")
    print(f"    P25:    {delta_series.quantile(0.25)*100:>7.2f}%")
    print(f"    P50:    {delta_series.quantile(0.50)*100:>7.2f}%")
    print(f"    P75:    {delta_series.quantile(0.75)*100:>7.2f}%")
    print(f"    P90:    {delta_series.quantile(0.90)*100:>7.2f}%")
    print(f"    P95:    {delta_series.quantile(0.95)*100:>7.2f}%")

    # Current thresholds analysis
    current_bullish = METRIC_THRESHOLDS.get(f"{metric_name}_bullish") or METRIC_THRESHOLDS.get(f"{metric_name}_delta_bullish")
    current_bearish = METRIC_THRESHOLDS.get(f"{metric_name}_bearish") or METRIC_THRESHOLDS.get(f"{metric_name}_delta_bearish")

    if current_bullish is not None:
        # Check if this is an inverted metric
        inverted = metric_name in ["rrpontsyd", "bamlh0a0hym2", "dtwexbgs", "hy_spread", "dxy", "rrp"]

        if inverted:
            bullish_pct = (delta_series <= current_bullish).mean() * 100
            bearish_pct = (delta_series >= current_bearish).mean() * 100
        else:
            bullish_pct = (delta_series >= current_bullish).mean() * 100
            bearish_pct = (delta_series <= current_bearish).mean() * 100

        neutral_pct = 100 - bullish_pct - bearish_pct

        print(f"\n  Current Thresholds:")
        print(f"    Bullish: {current_bullish*100:+.1f}% -> triggers {bullish_pct:.1f}% of time")
        print(f"    Bearish: {current_bearish*100:+.1f}% -> triggers {bearish_pct:.1f}% of time")
        print(f"    Neutral: {neutral_pct:.1f}% of time")


def analyze_stablecoin_vs_btc(stable_df: pd.DataFrame, btc_df: pd.DataFrame):
    """Analyze stablecoin signals vs subsequent BTC returns."""

    # Calculate stablecoin deltas for each date
    stable_df = stable_df.sort_values("date")
    btc_df = btc_df.sort_values("date")

    results = []

    for i in range(21, len(stable_df) - 30):  # Need 21 days back, 30 days forward
        target_date = stable_df["date"].iloc[i]

        # Calculate stablecoin delta
        delta = calculate_delta_at_date(stable_df.iloc[:i+1].copy(), target_date, 21, "supply")
        if delta is None:
            continue

        # Find BTC price at this date
        btc_at_date = btc_df[btc_df["date"] <= target_date]
        if len(btc_at_date) == 0:
            continue
        start_price = btc_at_date["price"].iloc[-1]

        # Find BTC price 30 days later
        future_date = target_date + timedelta(days=30)
        btc_future = btc_df[(btc_df["date"] >= future_date - timedelta(days=3)) &
                           (btc_df["date"] <= future_date + timedelta(days=3))]
        if len(btc_future) == 0:
            continue
        end_price = btc_future["price"].iloc[0]

        btc_return = (end_price - start_price) / start_price

        # Score the signal with current thresholds
        score = score_metric(delta, 0.02, -0.02, inverted=False)

        results.append({
            "date": target_date,
            "stable_delta": delta,
            "score": score,
            "btc_return_30d": btc_return
        })

    if not results:
        print("  Not enough overlapping data")
        return

    results_df = pd.DataFrame(results)

    print(f"\n  Analysis period: {results_df['date'].min().date()} to {results_df['date'].max().date()}")
    print(f"  Data points: {len(results_df)}")

    # Returns by signal
    print("\n  BTC 30-day returns by stablecoin signal:")
    print(f"  {'Signal':<12} {'Count':>6} {'Avg Return':>12} {'Win Rate':>10}")
    print("  " + "-"*44)

    for signal_name, signal_val in [("Bullish", 1), ("Neutral", 0), ("Bearish", -1)]:
        subset = results_df[results_df["score"] == signal_val]
        if len(subset) > 0:
            avg_ret = subset["btc_return_30d"].mean() * 100
            win_rate = (subset["btc_return_30d"] > 0).mean() * 100
            print(f"  {signal_name:<12} {len(subset):>6} {avg_ret:>11.1f}% {win_rate:>9.1f}%")

    # Test different thresholds
    print("\n  Testing different thresholds...")
    print(f"  {'Threshold':>10} {'Bull%':>7} {'Bear%':>7} {'Bull Ret':>10} {'Bear Ret':>10} {'Spread':>10}")
    print("  " + "-"*60)

    for thresh in [0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05]:
        results_df["test_score"] = results_df["stable_delta"].apply(
            lambda x: 1 if x >= thresh else (-1 if x <= -thresh else 0)
        )

        bull = results_df[results_df["test_score"] == 1]
        bear = results_df[results_df["test_score"] == -1]

        bull_pct = len(bull) / len(results_df) * 100
        bear_pct = len(bear) / len(results_df) * 100

        bull_ret = bull["btc_return_30d"].mean() * 100 if len(bull) > 0 else 0
        bear_ret = bear["btc_return_30d"].mean() * 100 if len(bear) > 0 else 0
        spread = bull_ret - bear_ret

        print(f"  {thresh*100:>9.1f}% {bull_pct:>6.1f}% {bear_pct:>6.1f}% {bull_ret:>9.1f}% {bear_ret:>9.1f}% {spread:>9.1f}%")


def generate_recommendations(stable_df: pd.DataFrame, fred_data: Dict[str, pd.DataFrame]):
    """Generate threshold recommendations based on analysis."""

    print("\nBased on the analysis:")

    # Stablecoin recommendation
    if len(stable_df) > 21:
        stable_df = stable_df.sort_values("date")
        deltas = []
        for i in range(21, len(stable_df)):
            target_date = stable_df["date"].iloc[i]
            delta = calculate_delta_at_date(stable_df.iloc[:i+1].copy(), target_date, 21, "supply")
            if delta is not None:
                deltas.append(delta)

        if deltas:
            delta_series = pd.Series(deltas)
            p75 = delta_series.quantile(0.75)
            p25 = delta_series.quantile(0.25)

            suggested = max(abs(p25), abs(p75)) * 0.6
            current = 0.02

            print(f"\n  STABLECOINS (Crypto Dry Powder):")
            print(f"    Current threshold: {current*100:.1f}%")
            print(f"    Historical P25-P75 range: {p25*100:.2f}% to {p75*100:.2f}%")

            if suggested < current * 0.7:
                print(f"    Recommendation: Lower to ~{suggested*100:.1f}% (would trigger more often)")
            elif suggested > current * 1.3:
                print(f"    Recommendation: Raise to ~{suggested*100:.1f}% (more selective)")
            else:
                print(f"    Current threshold is reasonable for this data")

    # FRED recommendations if available
    for metric, key, inverted, thresh_key in [
        ("HY SPREADS (Risk Appetite)", "bamlh0a0hym2", True, "hy_spread"),
        ("DXY (Dollar Strength)", "dtwexbgs", True, "dxy"),
        ("RRP (Sideline Cash)", "rrpontsyd", True, "rrp"),
        ("WALCL (Fed Printing)", "walcl", False, "walcl"),
    ]:
        df = fred_data.get(key)
        if df is not None and len(df) > 28:
            df = df.sort_values("date")
            deltas = []
            for i in range(28, len(df)):
                target_date = df["date"].iloc[i]
                delta = calculate_delta_at_date(df.iloc[:i+1].copy(), target_date, 28, "value")
                if delta is not None:
                    deltas.append(delta)

            if deltas:
                delta_series = pd.Series(deltas)
                p10 = delta_series.quantile(0.10)
                p90 = delta_series.quantile(0.90)

                current_bullish = METRIC_THRESHOLDS.get(f"{thresh_key}_bullish") or METRIC_THRESHOLDS.get(f"{thresh_key}_delta_bullish")
                current_bearish = METRIC_THRESHOLDS.get(f"{thresh_key}_bearish") or METRIC_THRESHOLDS.get(f"{thresh_key}_delta_bearish")

                if inverted:
                    bullish_pct = (delta_series <= current_bullish).mean() * 100
                    bearish_pct = (delta_series >= current_bearish).mean() * 100
                else:
                    bullish_pct = (delta_series >= current_bullish).mean() * 100
                    bearish_pct = (delta_series <= current_bearish).mean() * 100

                print(f"\n  {metric}:")
                print(f"    Current thresholds: {current_bullish*100:+.1f}% / {current_bearish*100:+.1f}%")
                print(f"    Historical P10-P90: {p10*100:.2f}% to {p90*100:.2f}%")
                print(f"    Signal frequency: Bullish {bullish_pct:.1f}%, Bearish {bearish_pct:.1f}%")

                if bullish_pct + bearish_pct < 15:
                    suggested = max(abs(p10), abs(p90)) * 0.5
                    print(f"    ⚠️ Only {bullish_pct + bearish_pct:.1f}% of days have signals!")
                    print(f"    Consider: {suggested*100:.2f}% threshold (based on P10/P90)")


if __name__ == "__main__":
    run_analysis_with_available_data()
