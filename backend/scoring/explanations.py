"""
Generate opinionated regime explanations
"""

from typing import Dict, Any


def generate_explanation(
    regime: str,
    scores: Dict[str, Any],
    metrics: Dict[str, Any],
    regime_info: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generate opinionated explanation for current regime.

    Returns dict with:
    - headline: Short regime summary
    - body: Detailed explanation
    - posture: Action recommendation
    - warnings: Any cautionary notes
    """
    individual = scores.get("individual", {})
    total = scores.get("total", 0)

    # Build explanation based on regime
    if regime == "aggressive":
        return _explain_aggressive(individual, metrics, regime_info, total)
    elif regime == "defensive":
        return _explain_defensive(individual, metrics, regime_info, total)
    else:
        return _explain_balanced(individual, metrics, regime_info, total)


def _explain_aggressive(
    individual: Dict,
    metrics: Dict,
    regime_info: Dict,
    total: float
) -> Dict[str, str]:
    """Generate aggressive regime explanation."""

    # Build body from strongest signals
    body_parts = []

    walcl = individual.get("walcl", {})
    if walcl.get("score", 0) > 0:
        walcl_data = metrics.get("walcl", {})
        delta = walcl_data.get("delta_4w", 0) or 0
        accel = walcl_data.get("acceleration")
        accel_str = " and accelerating" if accel and accel > 0 else ""
        body_parts.append(
            f"Fed liquidity expanding at {delta*100:+.1f}% over 4 weeks{accel_str}."
        )

    rrp = individual.get("rrp", {})
    if rrp.get("score", 0) > 0:
        body_parts.append(
            "Reverse repo drawdown continues — capital returning to risk markets."
        )

    hy = individual.get("hy_spread", {})
    if hy.get("score", 0) > 0:
        body_parts.append("Credit spreads tightening, signaling risk appetite.")

    stable = individual.get("stablecoin", {})
    if stable.get("score", 0) > 0:
        stable_data = metrics.get("stablecoin", {})
        delta = stable_data.get("delta_21d", 0) or 0
        body_parts.append(f"Stablecoin supply growing {delta*100:+.1f}% over 21 days.")

    btc = metrics.get("btc", {})
    distance = btc.get("distance_from_200dma")
    if distance:
        body_parts.append(f"BTC trading {distance*100:.1f}% above 200DMA.")

    body = " ".join(body_parts) if body_parts else "Multiple liquidity indicators aligned bullish."

    # Check for any negative signals
    warnings = []
    for name, data in individual.items():
        if data.get("score", 0) < 0:
            warnings.append(f"{name.upper()}: {data.get('reason', 'bearish')}")

    warning_str = " However, watch: " + "; ".join(warnings) if warnings else ""

    days = regime_info.get("days_in_regime")
    days_str = f" (Day {days} of regime)" if days else ""

    return {
        "headline": f"AGGRESSIVE{days_str}",
        "body": body + warning_str,
        "posture": "Full risk-on appropriate. Consider max exposure to quality assets.",
        "warnings": _get_overlay_warnings(metrics),
    }


def _explain_defensive(
    individual: Dict,
    metrics: Dict,
    regime_info: Dict,
    total: float
) -> Dict[str, str]:
    """Generate defensive regime explanation."""

    body_parts = []

    walcl = individual.get("walcl", {})
    if walcl.get("score", 0) < 0:
        walcl_data = metrics.get("walcl", {})
        delta = walcl_data.get("delta_4w", 0) or 0
        body_parts.append(f"Fed balance sheet contracting {delta*100:.1f}% over 4 weeks.")

    rrp = individual.get("rrp", {})
    if rrp.get("score", 0) < 0:
        body_parts.append("Reverse repo building — capital fleeing risk markets for safety.")

    hy = individual.get("hy_spread", {})
    if hy.get("score", 0) < 0:
        hy_data = metrics.get("hy_spread", {})
        current = hy_data.get("current")
        level_str = f" now at {current*100:.0f}bps" if current else ""
        body_parts.append(f"Credit spreads widening{level_str}, signaling stress.")

    dxy = individual.get("dxy", {})
    if dxy.get("score", 0) < 0:
        body_parts.append("Dollar strengthening, adding pressure to risk assets.")

    stable = individual.get("stablecoin", {})
    if stable.get("score", 0) < 0:
        body_parts.append("Stablecoin supply contracting — capital exiting crypto ecosystem.")

    btc = metrics.get("btc", {})
    if not btc.get("above_200dma"):
        distance = btc.get("distance_from_200dma")
        if distance:
            body_parts.append(f"BTC trading {abs(distance)*100:.1f}% below 200DMA.")

    body = " ".join(body_parts) if body_parts else "Multiple liquidity indicators aligned bearish."

    days = regime_info.get("days_in_regime")
    days_str = f" (Day {days} of regime)" if days else ""

    return {
        "headline": f"DEFENSIVE{days_str}",
        "body": body,
        "posture": "Risk-off posture. Reduce exposure, raise cash, avoid leverage.",
        "warnings": _get_overlay_warnings(metrics),
    }


def _explain_balanced(
    individual: Dict,
    metrics: Dict,
    regime_info: Dict,
    total: float
) -> Dict[str, str]:
    """Generate balanced regime explanation."""

    # Count bullish vs bearish signals
    bullish = []
    bearish = []
    neutral = []

    for name, data in individual.items():
        score = data.get("score", 0)
        reason = data.get("reason", "")
        if score > 0:
            bullish.append(f"{name.upper()}: {reason}")
        elif score < 0:
            bearish.append(f"{name.upper()}: {reason}")
        else:
            neutral.append(f"{name.upper()}: {reason}")

    body_parts = []

    if bullish:
        body_parts.append(f"Bullish: {'; '.join(bullish)}.")
    if bearish:
        body_parts.append(f"Bearish: {'; '.join(bearish)}.")

    if not body_parts:
        body_parts.append("Mixed signals across liquidity indicators.")

    # Trend context
    trend = regime_info.get("score_trend", "flat")
    if trend == "improving":
        body_parts.append("Overall trend improving.")
    elif trend == "deteriorating":
        body_parts.append("Overall trend deteriorating.")

    # Pending flip context
    if regime_info.get("pending_flip"):
        proposed = regime_info.get("proposed_regime", "").upper()
        days_until = regime_info.get("days_until_flip", 0)
        if days_until and days_until > 0:
            body_parts.append(f"Potential flip to {proposed} in {days_until} day(s) if trend continues.")

    body = " ".join(body_parts)

    days = regime_info.get("days_in_regime")
    days_str = f" (Day {days} of regime)" if days else ""

    return {
        "headline": f"BALANCED{days_str}",
        "body": body,
        "posture": "Neutral posture. Maintain moderate exposure, be selective.",
        "warnings": _get_overlay_warnings(metrics),
    }


def _get_overlay_warnings(metrics: Dict) -> str:
    """Generate overlay warnings (funding, vol, etc.)."""
    warnings = []

    # BTC volatility warning could be added here
    btc = metrics.get("btc", {})
    distance = btc.get("distance_from_200dma")
    if distance and abs(distance) > 0.3:
        if distance > 0:
            warnings.append("BTC extended >30% above 200DMA — consider scaling out")
        else:
            warnings.append("BTC deeply oversold >30% below 200DMA — potential bounce zone")

    return " | ".join(warnings) if warnings else ""
