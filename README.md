# FlowState 🌊

Real-time crypto liquidity regime tracker.

[![Live Demo](https://img.shields.io/badge/Live_Demo-flowstate.streamlit.app-3B82F6?style=for-the-badge)](https://flowstate.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## What is FlowState?

FlowState tracks 5 macro liquidity indicators to classify crypto market conditions into risk regimes. Know when conditions favor risk-taking vs playing defense.

| Regime | What It Means |
|--------|--------------|
| 🚀 **Aggressive** | Liquidity expanding. Conditions favor risk-on positioning. |
| ⚖️ **Balanced** | Mixed signals. Be selective, don't go all-in. |
| 🛡️ **Defensive** | Liquidity headwinds. Consider reducing exposure. |

## The Five Forces

FlowState monitors these liquidity indicators:

| Force | What It Tracks | Why It Matters |
|-------|---------------|----------------|
| **Fed Balance Sheet** | Federal Reserve assets (WALCL) | QE = more liquidity for risk assets |
| **Reverse Repo** | Cash parked at the Fed | Money leaving RRP enters markets |
| **Credit Spreads** | High-yield bond risk premium | Tight spreads = risk-on behavior |
| **Dollar Strength** | Trade-weighted USD index | Weaker dollar = easier global conditions |
| **Stablecoin Supply** | USDT + USDC market cap | Capital ready to deploy into crypto |

Plus a **BTC Gate**: Aggressive regime requires Bitcoin above its 200-day moving average.

## Features

- **Real-time regime classification** with anti-whipsaw logic
- **Plain English mode** - no finance jargon required
- **90-day sparkline charts** for each indicator
- **Mobile responsive** design
- **Email alerts** when the regime changes

## Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/flowstate.git
cd flowstate

# Install dependencies
pip install -r requirements.txt

# Set your FRED API key (free at fred.stlouisfed.org)
# Windows:
set FRED_API_KEY=your_key_here
# Mac/Linux:
export FRED_API_KEY=your_key_here

# Run
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## How Scoring Works

1. Each indicator scores **+1** (bullish), **0** (neutral), or **-1** (bearish)
2. Scores are weighted and summed
3. Total ≥ +4 = Aggressive, ≤ -4 = Defensive, between = Balanced
4. Regime changes require 2 consecutive days above threshold (anti-whipsaw)

## Data Sources

- **FRED** (Federal Reserve Economic Data) - Macro indicators
- **CoinGecko** - Bitcoin price data
- **DefiLlama** - Stablecoin supply

## Disclaimer

**Not financial advice.** FlowState is an educational tool for understanding macro-crypto conditions. Past correlations don't guarantee future results. Always do your own research.

## License

MIT - Use it, fork it, improve it.

---

Built by [Elijah Wilbanks](https://www.linkedin.com/in/elijah-wilbanks/)
