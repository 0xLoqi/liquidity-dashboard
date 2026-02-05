"""
Discord webhook notifications for regime alerts and daily briefings.
"""

import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Regime colors for Discord embeds (decimal format)
REGIME_COLORS = {
    "aggressive": 0x10B981,  # Green
    "balanced": 0xF59E0B,    # Amber
    "defensive": 0xEF4444,   # Red
}

REGIME_EMOJIS = {
    "aggressive": "🚀",
    "balanced": "⚖️",
    "defensive": "🛡️",
}

# Plain English descriptions for each regime
REGIME_DESCRIPTIONS = {
    "aggressive": "Liquidity conditions look favorable. Macro tailwinds support risk-on positioning.",
    "balanced": "Mixed signals across indicators. Stay selective and avoid overexposure.",
    "defensive": "Liquidity headwinds present. Consider reducing risk and preserving capital.",
}

# Friendly names for metrics
METRIC_NAMES = {
    "walcl": "Fed Balance Sheet",
    "rrp": "Reverse Repo",
    "hy_spread": "Credit Spreads",
    "dxy": "Dollar Strength",
    "stablecoin": "Stablecoin Flows",
}


def send_daily_briefing(
    webhook_url: str,
    regime: str,
    score: float,
    metrics: Dict[str, Any],
    scores: Dict[str, Any],
    dashboard_url: str,
    btc_price: Optional[float] = None,
    btc_200dma: Optional[float] = None,
) -> bool:
    """Send daily regime briefing to Discord."""

    emoji = REGIME_EMOJIS.get(regime, "📊")
    color = REGIME_COLORS.get(regime, 0x6366F1)
    description = REGIME_DESCRIPTIONS.get(regime, "")

    # Build metric summary with friendly names
    metric_lines = []
    for name, data in scores.get("individual", {}).items():
        sig = data.get("score", 0)
        icon = "🟢" if sig > 0 else "🔴" if sig < 0 else "⚪"
        friendly_name = METRIC_NAMES.get(name, name.replace("_", " ").title())
        metric_lines.append(f"{icon} {friendly_name}")

    metrics_text = "\n".join(metric_lines) if metric_lines else "No data"

    # BTC info
    btc_above = scores.get("btc_above_200dma", False)
    btc_price_str = f"${btc_price:,.0f}" if btc_price else "N/A"
    btc_ma_str = f"${btc_200dma:,.0f}" if btc_200dma else "N/A"
    btc_vs_ma = "above" if btc_above else "below"
    btc_status = f"**{btc_price_str}** ({btc_vs_ma} {btc_ma_str} MA)"

    embed = {
        "title": f"{emoji} {regime.upper()} — Score: {score:+.1f}",
        "description": description,
        "color": color,
        "fields": [
            {
                "name": "₿ Bitcoin",
                "value": btc_status,
                "inline": True,
            },
            {
                "name": "📖 Learn More",
                "value": f"[Open Dashboard]({dashboard_url})",
                "inline": True,
            },
            {
                "name": "Signals",
                "value": metrics_text,
                "inline": False,
            },
        ],
        "footer": {
            "text": "Daily macro liquidity check"
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"Discord webhook error: {e}")
        return False


def send_regime_change_alert(
    webhook_url: str,
    old_regime: str,
    new_regime: str,
    score: float,
    dashboard_url: str,
    btc_price: Optional[float] = None,
) -> bool:
    """Send urgent alert when regime changes."""

    old_emoji = REGIME_EMOJIS.get(old_regime, "?")
    new_emoji = REGIME_EMOJIS.get(new_regime, "?")
    color = REGIME_COLORS.get(new_regime, 0x6366F1)
    new_description = REGIME_DESCRIPTIONS.get(new_regime, "")

    # Determine if this is bullish or bearish shift
    regime_order = {"defensive": 0, "balanced": 1, "aggressive": 2}
    old_rank = regime_order.get(old_regime, 1)
    new_rank = regime_order.get(new_regime, 1)

    if new_rank > old_rank:
        direction = "Conditions improving"
    else:
        direction = "Conditions deteriorating"

    btc_str = f"${btc_price:,.0f}" if btc_price else "N/A"

    embed = {
        "title": f"Regime Change: {old_regime.title()} → {new_regime.title()}",
        "description": f"**{direction}**\n\n{new_description}\n\n₿ BTC: **{btc_str}** | Score: **{score:+.1f}**",
        "color": color,
        "fields": [
            {
                "name": "📖 Learn More",
                "value": f"[Open Dashboard]({dashboard_url})",
                "inline": False,
            },
        ],
        "footer": {
            "text": "Liquidity regime shift detected"
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Add @here mention for urgency
    payload = {
        "content": "Heads up — macro liquidity regime just changed:",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"Discord webhook error: {e}")
        return False
