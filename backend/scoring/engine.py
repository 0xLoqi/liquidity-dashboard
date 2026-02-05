"""
Core scoring logic for each metric
"""

from typing import Dict, Any, Tuple
from config import WEIGHTS, METRIC_THRESHOLDS


def score_walcl(metrics: Dict[str, Any]) -> Tuple[int, str]:
    """
    Score Fed Balance Sheet (WALCL).
    Bullish: Expansion (positive delta, accelerating)
    Bearish: Contraction
    """
    walcl = metrics.get("walcl", {})
    delta = walcl.get("delta_4w")
    accel = walcl.get("acceleration")

    if delta is None:
        return 0, "No data"

    if delta >= METRIC_THRESHOLDS["walcl_delta_bullish"]:
        if accel and accel > 0:
            return 1, f"Expanding +{delta*100:.1f}% (accelerating)"
        return 1, f"Expanding +{delta*100:.1f}%"
    elif delta <= METRIC_THRESHOLDS["walcl_delta_bearish"]:
        if accel and accel < 0:
            return -1, f"Contracting {delta*100:.1f}% (accelerating)"
        return -1, f"Contracting {delta*100:.1f}%"
    else:
        return 0, f"Flat ({delta*100:+.1f}%)"


def score_rrp(metrics: Dict[str, Any]) -> Tuple[int, str]:
    """
    Score Reverse Repo (RRP).
    Bullish: Drawdown (money leaving RRP = entering markets)
    Bearish: Buildup (money parking in RRP = leaving markets)
    """
    rrp = metrics.get("rrp", {})
    delta = rrp.get("delta_4w")
    accel = rrp.get("acceleration")

    if delta is None:
        return 0, "No data"

    # Note: RRP is inverted - decrease is bullish
    if delta <= METRIC_THRESHOLDS["rrp_delta_bullish"]:
        if accel and accel < 0:
            return 1, f"Draining {delta*100:.1f}% (accelerating)"
        return 1, f"Draining {delta*100:.1f}%"
    elif delta >= METRIC_THRESHOLDS["rrp_delta_bearish"]:
        if accel and accel > 0:
            return -1, f"Building +{delta*100:.1f}% (accelerating)"
        return -1, f"Building +{delta*100:.1f}%"
    else:
        return 0, f"Stable ({delta*100:+.1f}%)"


def score_hy_spread(metrics: Dict[str, Any]) -> Tuple[int, str]:
    """
    Score High Yield Credit Spreads.
    Bullish: Tightening (spreads narrowing = risk-on)
    Bearish: Widening (spreads widening = risk-off)
    """
    hy = metrics.get("hy_spread", {})
    delta = hy.get("delta_4w")
    current = hy.get("current")

    if delta is None:
        return 0, "No data"

    level_str = f" ({current*100:.0f}bps)" if current else ""

    if delta <= METRIC_THRESHOLDS["hy_spread_bullish"]:
        return 1, f"Tightening {delta*100:.1f}%{level_str}"
    elif delta >= METRIC_THRESHOLDS["hy_spread_bearish"]:
        return -1, f"Widening +{delta*100:.1f}%{level_str}"
    else:
        return 0, f"Stable ({delta*100:+.1f}%){level_str}"


def score_dxy(metrics: Dict[str, Any]) -> Tuple[int, str]:
    """
    Score Dollar Index (DXY).
    Bullish: Weakening dollar
    Bearish: Strengthening dollar
    """
    dxy = metrics.get("dxy", {})
    delta = dxy.get("delta_4w")
    current = dxy.get("current")

    if delta is None:
        return 0, "No data"

    level_str = f" ({current:.1f})" if current else ""

    if delta <= METRIC_THRESHOLDS["dxy_bullish"]:
        return 1, f"Weakening {delta*100:.1f}%{level_str}"
    elif delta >= METRIC_THRESHOLDS["dxy_bearish"]:
        return -1, f"Strengthening +{delta*100:.1f}%{level_str}"
    else:
        return 0, f"Stable ({delta*100:+.1f}%){level_str}"


def score_stablecoin(metrics: Dict[str, Any]) -> Tuple[int, str]:
    """
    Score Stablecoin Supply (USDT + USDC).
    Bullish: Growing supply = capital inflows
    Bearish: Shrinking supply = capital outflows
    """
    stable = metrics.get("stablecoin", {})
    delta = stable.get("delta_21d")
    current = stable.get("current")

    if delta is None:
        return 0, "No data"

    level_str = f" (${current/1e9:.0f}B)" if current else ""

    if delta >= METRIC_THRESHOLDS["stablecoin_bullish"]:
        return 1, f"Growing +{delta*100:.1f}%{level_str}"
    elif delta <= METRIC_THRESHOLDS["stablecoin_bearish"]:
        return -1, f"Shrinking {delta*100:.1f}%{level_str}"
    else:
        return 0, f"Flat ({delta*100:+.1f}%){level_str}"


def calculate_scores(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all individual scores and weighted total.
    Returns dict with scores, reasons, and total.
    """
    scores = {}

    # Calculate each metric score
    score, reason = score_walcl(metrics)
    scores["walcl"] = {
        "score": score,
        "weighted": score * WEIGHTS["walcl"],
        "reason": reason,
        "weight": WEIGHTS["walcl"],
    }

    score, reason = score_rrp(metrics)
    scores["rrp"] = {
        "score": score,
        "weighted": score * WEIGHTS["rrp"],
        "reason": reason,
        "weight": WEIGHTS["rrp"],
    }

    score, reason = score_hy_spread(metrics)
    scores["hy_spread"] = {
        "score": score,
        "weighted": score * WEIGHTS["hy_spread"],
        "reason": reason,
        "weight": WEIGHTS["hy_spread"],
    }

    score, reason = score_dxy(metrics)
    scores["dxy"] = {
        "score": score,
        "weighted": score * WEIGHTS["dxy"],
        "reason": reason,
        "weight": WEIGHTS["dxy"],
    }

    score, reason = score_stablecoin(metrics)
    scores["stablecoin"] = {
        "score": score,
        "weighted": score * WEIGHTS["stablecoin"],
        "reason": reason,
        "weight": WEIGHTS["stablecoin"],
    }

    # Calculate total weighted score
    total = sum(s["weighted"] for s in scores.values())

    # BTC gate check
    btc = metrics.get("btc", {})
    btc_above_200dma = btc.get("above_200dma", False)
    btc_distance = btc.get("distance_from_200dma")

    return {
        "individual": scores,
        "total": total,
        "max_possible": sum(WEIGHTS.values()),
        "min_possible": -sum(WEIGHTS.values()),
        "btc_above_200dma": btc_above_200dma,
        "btc_distance_from_200dma": btc_distance,
    }
