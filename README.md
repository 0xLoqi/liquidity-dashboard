# Liquidity Regime Dashboard

A Streamlit-based dashboard that classifies macroeconomic and cryptocurrency market conditions into risk regimes by analyzing Federal Reserve liquidity metrics, crypto market indicators, and macro risk factors.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

The dashboard provides a data-driven, rule-based assessment of market conditions to inform portfolio positioning. It classifies the current environment into one of three regimes:

| Regime | Score | Meaning |
|--------|-------|---------|
| 🚀 **Aggressive** | ≥ +4.0 | Risk-on: Liquidity expanding, favorable conditions |
| ⚖️ **Balanced** | -4.0 to +4.0 | Neutral: Mixed signals, moderate positioning |
| 🛡️ **Defensive** | ≤ -4.0 | Risk-off: Liquidity contracting, caution advised |

## Features

- **Real-time regime classification** with anti-whipsaw hysteresis logic
- **6 key indicators** tracked with weighted scoring
- **90-day sparkline charts** for trend visualization
- **BTC gate mechanism** - Aggressive regime requires price above 200-day MA
- **SQLite caching** to minimize API calls
- **Persistent state** across restarts

## Indicators Tracked

| Indicator | Source | Weight | Signal |
|-----------|--------|--------|--------|
| Fed Balance Sheet (WALCL) | FRED | 1.5x | Higher = bullish |
| Reverse Repo (RRP) | FRED | 1.5x | Lower = bullish |
| HY Credit Spreads | FRED | 1.5x | Lower = bullish |
| Dollar Index (DXY) | FRED | 1.0x | Lower = bullish |
| Stablecoin Supply | DefiLlama | 1.0x | Higher = bullish |
| BTC 200-day MA | CoinGecko | Gate | Above = unlocks Aggressive |

## Installation

### Prerequisites

- Python 3.9+
- FRED API key ([get one free](https://fred.stlouisfed.org/docs/api/api_key.html))

### Setup

```bash
# Clone and navigate to the project
cd liquidity-dashboard

# Install dependencies
pip install -r requirements.txt

# Set your FRED API key
# Windows:
set FRED_API_KEY=your_key_here

# Mac/Linux:
export FRED_API_KEY=your_key_here
```

### Run

```bash
# Start the dashboard
streamlit run app.py --server.port 8501

# Or on Windows, use the batch script
run.bat
```

Then open http://localhost:8501 in your browser.

## Project Structure

```
liquidity-dashboard/
├── app.py                 # Main Streamlit application
├── config.py              # Thresholds, weights, API endpoints
├── requirements.txt       # Python dependencies
├── run.bat                # Windows startup script
│
├── data/                  # Data layer
│   ├── fetchers.py       # FRED, CoinGecko, DefiLlama clients
│   ├── cache.py          # SQLite cache management
│   └── transforms.py     # Delta & MA calculations
│
├── scoring/               # Scoring engine
│   ├── engine.py         # Per-metric scoring (-1, 0, +1)
│   ├── regime.py         # Regime classification + hysteresis
│   └── explanations.py   # Human-readable narratives
│
└── ui/                    # Frontend components
    ├── components.py     # Metric cards, banners
    └── charts.py         # Sparklines, gauges
```

## Configuration

Key settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `AGGRESSIVE_THRESHOLD` | +4.0 | Score needed for Aggressive regime |
| `DEFENSIVE_THRESHOLD` | -4.0 | Score threshold for Defensive regime |
| `DELTA_WINDOW_DAYS` | 28 | Lookback for macro delta calculations |
| `MA_WINDOW` | 200 | BTC moving average period |
| `CACHE_TTL_FRED` | 4 hours | How long to cache FRED data |

## How Scoring Works

1. **Fetch** latest data from APIs (cached)
2. **Calculate** 4-week deltas and acceleration
3. **Score** each metric: +1 (bullish), 0 (neutral), -1 (bearish)
4. **Weight** scores and sum to total
5. **Apply hysteresis** - requires 2 consecutive days or 1-point margin
6. **Classify** regime based on thresholds
7. **Gate check** - BTC must be above 200-day MA for Aggressive

## API Keys

| API | Required | Notes |
|-----|----------|-------|
| FRED | Yes | Free, required for macro data |
| CoinGecko | No | Demo tier works without key |
| DefiLlama | No | No key needed |

## License

MIT
