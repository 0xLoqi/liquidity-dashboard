# Claude Code Instructions for FlowState

## Project Overview

FlowState is a Streamlit dashboard for macro-crypto regime classification. Fetches data from FRED, CoinGecko, and DefiLlama, scores liquidity conditions, and classifies into Aggressive/Balanced/Defensive regimes.

## Tech Stack

- **Python 3.9+** with Streamlit
- **SQLite** for caching
- **Plotly** for charts
- **APIs**: FRED (macro), CoinGecko (BTC), DefiLlama (stablecoins)

## Architecture

```
app.py          → Main entry, orchestrates everything
config.py       → All thresholds, weights, endpoints
data/           → Fetching & transforms (fetchers.py, cache.py, transforms.py)
scoring/        → Regime logic (engine.py, regime.py, explanations.py)
ui/             → Components & charts (components.py, charts.py)
```

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit app entry point |
| `config.py` | Thresholds, weights, API config - edit here for tuning |
| `data/fetchers.py` | API clients for FRED, CoinGecko, DefiLlama |
| `scoring/engine.py` | Per-metric scoring logic (-1, 0, +1) |
| `scoring/regime.py` | Hysteresis and regime classification |
| `regime_state.json` | Persisted state (current regime, consecutive days) |

## Running Locally

```bash
# Set API key
set FRED_API_KEY=your_key

# Run dashboard
streamlit run app.py --server.port 8501
```

Or use `run.bat` on Windows.

## Common Tasks

### Add a new indicator

1. Add fetcher in `data/fetchers.py`
2. Add transform in `data/transforms.py` if needed
3. Add scoring logic in `scoring/engine.py`
4. Add weight in `config.py`
5. Add UI component in `ui/components.py`
6. Wire up in `app.py`

### Change regime thresholds

Edit `config.py`:
```python
AGGRESSIVE_THRESHOLD = +4.0  # Score to enter Aggressive
DEFENSIVE_THRESHOLD = -4.0   # Score to enter Defensive
```

### Adjust indicator weights

Edit `config.py` WEIGHTS dict:
```python
WEIGHTS = {
    "walcl": 1.5,
    "rrp": 1.5,
    "hy_spread": 1.5,
    "dxy": 1.0,
    "stablecoin": 1.0,
}
```

### Clear cache

Delete `cache.db` or run:
```python
from data.cache import clear_cache
clear_cache()
```

## Important Patterns

### Inverted signals

Some metrics are inverted (lower = bullish):
- **RRP**: Lower reverse repo = more liquidity available
- **DXY**: Weaker dollar = crypto bullish
- **HY Spreads**: Tighter spreads = risk-on

### Hysteresis logic

Prevents whipsaw regime changes:
- Requires **2 consecutive days** above/below threshold, OR
- Score margin **> 1.0 point** from threshold

Located in `scoring/regime.py`.

### BTC Gate

Aggressive regime requires BTC above 200-day MA. Even with high score, regime caps at Balanced if BTC below MA. Logic in `scoring/regime.py`.

### Date-based deltas

Uses actual calendar days, not data point indices. Handles weekly FRED data correctly. See `data/transforms.py`.

## Debugging

- Check `regime_state.json` for current state
- Query `cache.db` with SQLite for cached data
- Streamlit reruns on file save - use `st.session_state` for persistence
- API issues? Check cache TTL in `config.py`

## Testing

Run the app and verify:
1. All 6 metrics load without errors
2. Sparklines render
3. Regime banner displays
4. Score gauge shows correctly
5. Refresh works (sidebar button)

## Don't

- Don't hardcode API keys - use environment variables
- Don't bypass hysteresis - it prevents false signals
- Don't change delta windows without understanding impact on scoring
- Don't cache indefinitely - data needs to refresh
