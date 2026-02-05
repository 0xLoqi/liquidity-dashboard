"""
Data transformations: deltas, acceleration, trends
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta

from config import WINDOWS, METRIC_THRESHOLDS


def calculate_delta_by_date(df: pd.DataFrame, days: int, value_col: str = "value", date_col: str = "date") -> Optional[float]:
    """
    Calculate percentage change over N days using actual dates.
    Works correctly for weekly, daily, or any frequency data.
    """
    if df is None or len(df) == 0:
        return None

    df = df.sort_values(date_col)
    current_date = df[date_col].iloc[-1]
    target_date = current_date - timedelta(days=days)

    # Find the closest date to target
    past_df = df[df[date_col] <= target_date]
    if len(past_df) == 0:
        return None

    current = df[value_col].iloc[-1]
    past = past_df[value_col].iloc[-1]

    if past == 0 or pd.isna(past) or pd.isna(current):
        return None

    return (current - past) / abs(past)


def calculate_delta(series: pd.Series, window: int) -> Optional[float]:
    """
    Calculate percentage change over window (index-based).
    For daily data or when you want N-point delta.
    """
    if len(series) < window + 1:
        return None

    current = series.iloc[-1]
    past = series.iloc[-window - 1]

    if past == 0 or pd.isna(past) or pd.isna(current):
        return None

    return (current - past) / abs(past)


def calculate_acceleration_by_date(df: pd.DataFrame, days: int, value_col: str = "value", date_col: str = "date") -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate delta and acceleration using date-based windows.
    """
    if df is None or len(df) < 3:
        return None, None

    # Current period delta
    current_delta = calculate_delta_by_date(df, days, value_col, date_col)

    # Previous period delta (ending 'days' ago)
    df = df.sort_values(date_col)
    current_date = df[date_col].iloc[-1]
    cutoff_date = current_date - timedelta(days=days)

    past_df = df[df[date_col] <= cutoff_date]
    if len(past_df) < 2:
        return current_delta, None

    previous_delta = calculate_delta_by_date(past_df, days, value_col, date_col)

    if current_delta is None or previous_delta is None:
        return current_delta, None

    acceleration = current_delta - previous_delta
    return current_delta, acceleration


def calculate_acceleration(series: pd.Series, window: int) -> Tuple[Optional[float], Optional[float]]:
    """
    Calculate delta and acceleration (2nd derivative) - index based.
    """
    if len(series) < window * 2:
        return None, None

    current_delta = calculate_delta(series, window)
    shifted = series.iloc[:-window]
    previous_delta = calculate_delta(shifted, window) if len(shifted) >= window + 1 else None

    if current_delta is None or previous_delta is None:
        return current_delta, None

    acceleration = current_delta - previous_delta
    return current_delta, acceleration


def calculate_trend(series: pd.Series, window: int = 14) -> str:
    """
    Determine if series is trending up, down, or flat.
    Uses simple linear regression slope.
    """
    if len(series) < window:
        return "unknown"

    recent = series.iloc[-window:].values
    x = np.arange(len(recent))

    # Simple linear regression
    slope = np.polyfit(x, recent, 1)[0]

    # Normalize slope by mean value
    mean_val = np.mean(recent)
    if mean_val == 0:
        return "flat"

    normalized_slope = slope / abs(mean_val) * window

    if normalized_slope > 0.02:
        return "up"
    elif normalized_slope < -0.02:
        return "down"
    else:
        return "flat"


def calculate_moving_average(series: pd.Series, window: int) -> Optional[float]:
    """Calculate simple moving average."""
    if len(series) < window:
        return None
    return series.iloc[-window:].mean()


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all derived metrics from raw data.
    Returns dict with metrics for scoring.
    """
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "walcl": {},
        "rrp": {},
        "hy_spread": {},
        "dxy": {},
        "stablecoin": {},
        "btc": {},
    }

    # WALCL (Fed Balance Sheet) - Weekly data, use date-based calculations
    walcl_df = data.get("fred", {}).get("WALCL")
    if walcl_df is not None and len(walcl_df) > 0:
        series = walcl_df["value"]
        delta, accel = calculate_acceleration_by_date(walcl_df, WINDOWS["delta_days"])
        metrics["walcl"] = {
            "current": series.iloc[-1] if len(series) > 0 else None,
            "delta_4w": delta,
            "acceleration": accel,
            "trend": calculate_trend(series, window=min(8, len(series))),  # Use fewer points for weekly data
            "latest_date": walcl_df["date"].iloc[-1].isoformat() if len(walcl_df) > 0 else None,
        }

    # RRP (Reverse Repo) - Daily data
    rrp_df = data.get("fred", {}).get("RRPONTSYD")
    if rrp_df is not None and len(rrp_df) > 0:
        series = rrp_df["value"]
        delta, accel = calculate_acceleration_by_date(rrp_df, WINDOWS["delta_days"])
        metrics["rrp"] = {
            "current": series.iloc[-1] if len(series) > 0 else None,
            "delta_4w": delta,
            "acceleration": accel,
            "trend": calculate_trend(series),
            "latest_date": rrp_df["date"].iloc[-1].isoformat() if len(rrp_df) > 0 else None,
        }

    # HY Spread - Daily data
    hy_df = data.get("fred", {}).get("BAMLH0A0HYM2")
    if hy_df is not None and len(hy_df) > 0:
        series = hy_df["value"]
        delta = calculate_delta_by_date(hy_df, WINDOWS["delta_days"])
        metrics["hy_spread"] = {
            "current": series.iloc[-1] if len(series) > 0 else None,
            "delta_4w": delta,
            "trend": calculate_trend(series),
            "latest_date": hy_df["date"].iloc[-1].isoformat() if len(hy_df) > 0 else None,
        }

    # DXY - Daily data
    dxy_df = data.get("fred", {}).get("DTWEXBGS")
    if dxy_df is not None and len(dxy_df) > 0:
        series = dxy_df["value"]
        delta = calculate_delta_by_date(dxy_df, WINDOWS["delta_days"])
        metrics["dxy"] = {
            "current": series.iloc[-1] if len(series) > 0 else None,
            "delta_4w": delta,
            "trend": calculate_trend(series),
            "latest_date": dxy_df["date"].iloc[-1].isoformat() if len(dxy_df) > 0 else None,
        }

    # Stablecoin Supply - Daily data
    stable_df = data.get("stablecoins")
    if stable_df is not None and len(stable_df) > 0:
        series = stable_df["supply"]
        delta = calculate_delta_by_date(stable_df, WINDOWS["stablecoin_days"], value_col="supply")
        metrics["stablecoin"] = {
            "current": series.iloc[-1] if len(series) > 0 else None,
            "delta_21d": delta,
            "trend": calculate_trend(series),
            "latest_date": stable_df["date"].iloc[-1].isoformat() if len(stable_df) > 0 else None,
        }

    # BTC vs 200 DMA
    btc_df = data.get("btc")
    if btc_df is not None and len(btc_df) > 0:
        series = btc_df["price"]
        ma_200 = calculate_moving_average(series, WINDOWS["ma_days"])
        current_price = series.iloc[-1] if len(series) > 0 else None

        metrics["btc"] = {
            "current_price": current_price,
            "ma_200": ma_200,
            "above_200dma": current_price > ma_200 if (current_price and ma_200) else None,
            "distance_from_200dma": ((current_price / ma_200) - 1) if (current_price and ma_200) else None,
            "latest_date": btc_df["date"].iloc[-1].isoformat() if len(btc_df) > 0 else None,
        }

    return metrics


def get_chart_data(data: Dict[str, Any], days: int = 90) -> Dict[str, pd.DataFrame]:
    """
    Extract chart-ready data for the last N days.
    Returns dict of DataFrames for each metric.
    """
    charts = {}
    cutoff = datetime.now() - timedelta(days=days)

    # FRED series
    for name in ["WALCL", "RRPONTSYD", "BAMLH0A0HYM2", "DTWEXBGS"]:
        df = data.get("fred", {}).get(name)
        if df is not None and len(df) > 0:
            df_recent = df[df["date"] >= cutoff].copy()
            charts[name.lower()] = df_recent

    # BTC
    btc_df = data.get("btc")
    if btc_df is not None and len(btc_df) > 0:
        btc_recent = btc_df[btc_df["date"] >= cutoff].copy()
        charts["btc"] = btc_recent

    # Stablecoins
    stable_df = data.get("stablecoins")
    if stable_df is not None and len(stable_df) > 0:
        stable_recent = stable_df[stable_df["date"] >= cutoff].copy()
        charts["stablecoins"] = stable_recent

    return charts
