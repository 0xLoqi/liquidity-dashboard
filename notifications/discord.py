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


def send_daily_briefing(
    webhook_url: str,
    regime: str,
    score: float,
    metrics: Dict[str, Any],
    scores: Dict[str, Any],
    dashboard_url: str,
) -> bool:
    """Send daily regime briefing to Discord."""
    
    emoji = REGIME_EMOJIS.get(regime, "📊")
    color = REGIME_COLORS.get(regime, 0x6366F1)
    
    # Build metric summary
    metric_lines = []
    for name, data in scores.get("individual", {}).items():
        sig = data.get("score", 0)
        icon = "🟢" if sig > 0 else "🔴" if sig < 0 else "⚪"
        display = name.upper().replace("_", " ")
        metric_lines.append(f"{icon} **{display}**: {sig:+d}")
    
    metrics_text = "\n".join(metric_lines) if metric_lines else "No data"
    
    # BTC gate status
    btc_above = scores.get("btc_above_200dma", False)
    btc_status = "✅ Above 200 DMA" if btc_above else "❌ Below 200 DMA"
    
    embed = {
        "title": f"{emoji} Liquidity Regime: {regime.upper()}",
        "description": f"**Composite Score: {score:+.1f}**\n\nDaily macro-liquidity briefing",
        "color": color,
        "fields": [
            {
                "name": "📊 Indicator Signals",
                "value": metrics_text,
                "inline": False,
            },
            {
                "name": "₿ BTC Gate",
                "value": btc_status,
                "inline": True,
            },
            {
                "name": "📈 Dashboard",
                "value": f"[View Full Dashboard]({dashboard_url})",
                "inline": True,
            },
        ],
        "footer": {
            "text": "Liquidity Regime Dashboard • Auto-updated daily"
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
) -> bool:
    """Send urgent alert when regime changes."""
    
    old_emoji = REGIME_EMOJIS.get(old_regime, "❓")
    new_emoji = REGIME_EMOJIS.get(new_regime, "❓")
    color = REGIME_COLORS.get(new_regime, 0x6366F1)
    
    # Determine if this is bullish or bearish shift
    regime_order = {"defensive": 0, "balanced": 1, "aggressive": 2}
    old_rank = regime_order.get(old_regime, 1)
    new_rank = regime_order.get(new_regime, 1)
    
    if new_rank > old_rank:
        direction = "⬆️ BULLISH SHIFT"
    else:
        direction = "⬇️ BEARISH SHIFT"
    
    embed = {
        "title": f"🚨 REGIME CHANGE: {direction}",
        "description": f"{old_emoji} {old_regime.upper()} → {new_emoji} **{new_regime.upper()}**\n\n**Score: {score:+.1f}**",
        "color": color,
        "fields": [
            {
                "name": "📈 View Details",
                "value": f"[Open Dashboard]({dashboard_url})",
                "inline": False,
            },
        ],
        "footer": {
            "text": "Liquidity Regime Alert"
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Add @here mention for urgency
    payload = {
        "content": "||@here|| Regime change detected!",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"Discord webhook error: {e}")
        return False
