"""
Configuration for FlowState - Real-time crypto liquidity regime tracker
"""

# =============================================================================
# API ENDPOINTS
# =============================================================================

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DEFILLAMA_BASE_URL = "https://stablecoins.llama.fi"

# FRED series IDs
FRED_SERIES = {
    "WALCL": "WALCL",           # Fed Balance Sheet (Weekly)
    "RRPONTSYD": "RRPONTSYD",   # Reverse Repo (Daily)
    "BAMLH0A0HYM2": "BAMLH0A0HYM2",  # HY Spread (Daily)
    "DTWEXBGS": "DTWEXBGS",     # DXY Trade Weighted Dollar Index (Daily)
}

# =============================================================================
# SCORING WEIGHTS
# =============================================================================

WEIGHTS = {
    "walcl": 1.5,          # Fed Balance Sheet
    "rrp": 1.5,            # Reverse Repo
    "hy_spread": 1.5,      # High Yield Spreads
    "dxy": 1.0,            # Dollar Index (confirming)
    "stablecoin": 1.0,     # Stablecoin Supply
}

# =============================================================================
# THRESHOLDS
# =============================================================================

# Regime score thresholds
REGIME_THRESHOLDS = {
    "aggressive": 4.0,     # Score >= this AND BTC > 200DMA
    "defensive": -4.0,     # Score <= this
}

# Individual metric thresholds
METRIC_THRESHOLDS = {
    "walcl_delta_bullish": 0.005,      # 0.5% 4-week increase
    "walcl_delta_bearish": -0.005,     # 0.5% 4-week decrease
    "rrp_delta_bullish": -0.05,        # 5% 4-week decrease (drawdown = bullish)
    "rrp_delta_bearish": 0.05,         # 5% 4-week increase
    "hy_spread_bullish": -0.10,        # 10% tightening
    "hy_spread_bearish": 0.10,         # 10% widening
    "dxy_bullish": -0.008,             # 0.8% decline (based on P25-P75 range of historical data)
    "dxy_bearish": 0.008,              # 0.8% increase
    "stablecoin_bullish": 0.035,       # 3.5% 21-day increase (raised from 2% to filter baseline growth)
    "stablecoin_bearish": -0.035,      # 3.5% 21-day decrease
}

# =============================================================================
# HYSTERESIS / ANTI-WHIPSAW
# =============================================================================

HYSTERESIS = {
    "consecutive_days_required": 2,    # Days above threshold before flip
    "margin_override": 1.0,            # Score margin that bypasses day requirement
}

# =============================================================================
# CACHE SETTINGS
# =============================================================================

CACHE_TTL = {
    "fred": 3600 * 4,          # 4 hours for FRED data
    "coingecko": 3600,         # 1 hour for price data
    "defillama": 3600 * 2,     # 2 hours for stablecoin data
}

# =============================================================================
# CALCULATION WINDOWS
# =============================================================================

WINDOWS = {
    "delta_days": 28,          # 4-week delta calculation
    "stablecoin_days": 21,     # 21-day stablecoin delta
    "ma_days": 200,            # 200-day moving average
    "chart_days": 90,          # Days to show in charts
}

# =============================================================================
# UI SETTINGS
# =============================================================================

REGIME_COLORS = {
    "aggressive": "#10B981",   # Emerald green
    "balanced": "#F59E0B",     # Amber
    "defensive": "#EF4444",    # Red
}

REGIME_ICONS = {
    "aggressive": "🚀",
    "balanced": "⚖️",
    "defensive": "🛡️",
}
