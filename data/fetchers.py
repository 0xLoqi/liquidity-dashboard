"""
Data fetchers for FRED, CoinGecko, and DefiLlama APIs
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

from config import (
    FRED_BASE_URL, FRED_SERIES,
    COINGECKO_BASE_URL, DEFILLAMA_BASE_URL,
    WINDOWS
)


def _get_secret(key: str) -> Optional[str]:
    """Get secret from environment or Streamlit secrets."""
    # First try environment variable
    value = os.environ.get(key)
    if value:
        return value

    # Then try Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return None


def get_fred_api_key() -> Optional[str]:
    """Get FRED API key from environment or Streamlit secrets."""
    return _get_secret("FRED_API_KEY")


def has_fred_api_key() -> bool:
    """Check if FRED API key is configured."""
    return get_fred_api_key() is not None


def fetch_fred_series(series_id: str, days_back: int = 365) -> pd.DataFrame:
    """
    Fetch a FRED series.
    Returns DataFrame with 'date' and 'value' columns.
    Requires FRED_API_KEY environment variable.
    """
    api_key = get_fred_api_key()

    if not api_key:
        # Return empty DataFrame - FRED requires API key
        return pd.DataFrame(columns=["date", "value"])

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "observation_start": start_date.strftime("%Y-%m-%d"),
        "observation_end": end_date.strftime("%Y-%m-%d"),
        "file_type": "json",
    }

    try:
        response = requests.get(FRED_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        observations = data.get("observations", [])
        if not observations:
            return pd.DataFrame(columns=["date", "value"])

        df = pd.DataFrame(observations)
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df[["date", "value"]].dropna()
        df = df.sort_values("date").reset_index(drop=True)

        return df

    except Exception as e:
        print(f"Error fetching FRED series {series_id}: {e}")
        return pd.DataFrame(columns=["date", "value"])


def get_coingecko_api_key() -> Optional[str]:
    """Get CoinGecko API key from environment or Streamlit secrets."""
    return _get_secret("COINGECKO_API_KEY")


def fetch_btc_price_history(days: int = 250) -> pd.DataFrame:
    """
    Fetch BTC price history from CoinGecko.
    Returns DataFrame with 'date' and 'price' columns.
    """
    api_key = get_coingecko_api_key()

    url = f"{COINGECKO_BASE_URL}/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }

    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
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
        print(f"Error fetching BTC price: {e}")
        return pd.DataFrame(columns=["date", "price"])


def fetch_stablecoin_supply() -> Dict[str, Any]:
    """
    Fetch USDT and USDC supply from DefiLlama.
    Returns dict with current supply and history.
    """
    try:
        # Get all stablecoins
        response = requests.get(f"{DEFILLAMA_BASE_URL}/stablecoins", timeout=30)
        response.raise_for_status()
        data = response.json()

        stablecoins = data.get("peggedAssets", [])

        result = {
            "usdt": {"supply": 0, "history": []},
            "usdc": {"supply": 0, "history": []},
            "total": {"supply": 0},
            "timestamp": datetime.now().isoformat()
        }

        for coin in stablecoins:
            symbol = coin.get("symbol", "").upper()
            if symbol in ["USDT", "USDC"]:
                current_supply = coin.get("circulating", {}).get("peggedUSD", 0)
                coin_id = coin.get("id")

                if symbol == "USDT":
                    result["usdt"]["supply"] = current_supply
                elif symbol == "USDC":
                    result["usdc"]["supply"] = current_supply

                # Fetch history for this stablecoin
                if coin_id:
                    try:
                        hist_response = requests.get(
                            f"{DEFILLAMA_BASE_URL}/stablecoincharts/all",
                            params={"stablecoin": coin_id},
                            timeout=30
                        )
                        if hist_response.ok:
                            hist_data = hist_response.json()
                            if symbol == "USDT":
                                result["usdt"]["history"] = hist_data
                            elif symbol == "USDC":
                                result["usdc"]["history"] = hist_data
                    except:
                        pass

        result["total"]["supply"] = result["usdt"]["supply"] + result["usdc"]["supply"]

        return result

    except Exception as e:
        print(f"Error fetching stablecoin data: {e}")
        return {
            "usdt": {"supply": 0, "history": []},
            "usdc": {"supply": 0, "history": []},
            "total": {"supply": 0},
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


def fetch_stablecoin_history_combined() -> pd.DataFrame:
    """
    Fetch combined USDT + USDC supply history.
    Returns DataFrame with 'date' and 'supply' columns.
    """
    try:
        # DefiLlama aggregated stablecoin chart
        response = requests.get(
            f"{DEFILLAMA_BASE_URL}/stablecoincharts/all",
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return pd.DataFrame(columns=["date", "supply"])

        records = []
        for item in data:
            try:
                # Date can be string or int
                date_val = item.get("date", 0)
                if isinstance(date_val, str):
                    date_val = int(date_val)
                date = datetime.fromtimestamp(date_val)

                # Get total circulating USD value
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
        print(f"Error fetching stablecoin history: {e}")
        return pd.DataFrame(columns=["date", "supply"])


def fetch_all_data() -> Dict[str, Any]:
    """
    Fetch all required data from all sources.
    Returns dict with all data organized by source/metric.
    """
    data = {
        "timestamp": datetime.now().isoformat(),
        "fred": {},
        "btc": None,
        "stablecoins": None,
    }

    # Fetch FRED data
    for name, series_id in FRED_SERIES.items():
        data["fred"][name] = fetch_fred_series(series_id)

    # Fetch BTC price
    data["btc"] = fetch_btc_price_history(days=WINDOWS["ma_days"] + 30)

    # Fetch stablecoin data
    data["stablecoins"] = fetch_stablecoin_history_combined()
    data["stablecoin_current"] = fetch_stablecoin_supply()

    return data
