# Claude Code Instructions for FlowState

## Project Overview

FlowState is a macro-crypto regime classification dashboard. Fetches data from FRED, CoinGecko, and DefiLlama, scores liquidity conditions, and classifies into Aggressive/Balanced/Defensive regimes.

## Tech Stack

- **Backend**: FastAPI (Python 3.11+) - `backend/`
- **Frontend**: Next.js 16 + React 19 + Tailwind 4 - `frontend/`
- **Charts**: Recharts
- **Data fetching**: SWR (frontend), requests (backend)
- **Caching**: SQLite
- **APIs**: FRED (macro), CoinGecko (BTC), DefiLlama (stablecoins)

## Architecture

```
backend/
├── main.py              → FastAPI app, all endpoints
├── config.py            → Thresholds, weights, API config
├── data/                → Fetchers, cache, transforms
├── scoring/             → Engine, regime logic, explanations
├── regime_state.json    → Current regime state (THIS IS THE ACTIVE ONE)
├── subscribers.json     → Email subscribers
└── cache.db             → SQLite cache

frontend/
├── src/app/             → Next.js app router (page.tsx, layout.tsx)
├── src/components/      → React components
├── src/hooks/           → Custom hooks
└── src/lib/             → Utilities

(Legacy - NOT ACTIVE)
app.py                   → Old Streamlit version
ui/                      → Old Streamlit components
```

## Running Locally

```bash
# Backend (from backend/)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (from frontend/)
cd frontend
npm install
npm run dev
```

Backend needs `FRED_API_KEY` in `backend/.env`.

## Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /regime` | Current regime, score, all metrics |
| `GET /chart-data/{metric}` | Historical data for sparklines |
| `POST /subscribe` | Add email subscriber |
| `POST /feedback` | Submit user feedback |
| `GET /admin/subscribers` | List subscribers (auth required) |

## Deployment

- **Frontend**: Vercel (https://flowstate.vercel.app)
- **Backend**: Needs hosting (Railway, Render, etc.)
- **GitHub Actions**: Still runs daily briefings via Discord

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

Located in `backend/scoring/regime.py`.

### BTC Gate

Aggressive regime requires BTC above 200-day MA. Even with high score, regime caps at Balanced if BTC below MA.

### Scoring weights

Edit `backend/config.py`:
```python
WEIGHTS = {
    "walcl": 1.5,      # Fed Balance Sheet
    "rrp": 1.5,        # Reverse Repo
    "hy_spread": 1.5,  # Credit Spreads
    "dxy": 1.0,        # Dollar Index
    "stablecoin": 1.0, # Stablecoin Supply
}
```

## Debugging

- Check `backend/regime_state.json` for current state (score, consecutive days)
- Query `backend/cache.db` for cached API data
- Frontend fetches from backend - check CORS if issues
- API issues? Check cache TTL in `backend/config.py`

## Don't

- Don't hardcode API keys - use environment variables
- Don't bypass hysteresis - it prevents false signals
- Don't change delta windows without understanding impact on scoring
- Don't cache indefinitely - data needs to refresh
- Don't confuse root-level files (old Streamlit) with backend/ (active)
