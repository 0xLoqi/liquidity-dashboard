"""
Regime classification with hysteresis/anti-whipsaw logic
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import json
from pathlib import Path

from config import REGIME_THRESHOLDS, HYSTERESIS


@dataclass
class RegimeState:
    """Tracks regime state with history for hysteresis."""
    current_regime: str = "balanced"
    proposed_regime: str = "balanced"
    consecutive_days: int = 0
    last_score: float = 0.0
    regime_start_date: Optional[str] = None
    score_history: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "current_regime": self.current_regime,
            "proposed_regime": self.proposed_regime,
            "consecutive_days": self.consecutive_days,
            "last_score": self.last_score,
            "regime_start_date": self.regime_start_date,
            "score_history": self.score_history[-30:],  # Keep last 30 days
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RegimeState":
        return cls(
            current_regime=data.get("current_regime", "balanced"),
            proposed_regime=data.get("proposed_regime", "balanced"),
            consecutive_days=data.get("consecutive_days", 0),
            last_score=data.get("last_score", 0.0),
            regime_start_date=data.get("regime_start_date"),
            score_history=data.get("score_history", []),
        )


def load_regime_state(state_file: Path) -> RegimeState:
    """Load regime state from file."""
    if state_file.exists():
        try:
            with open(state_file) as f:
                data = json.load(f)
                return RegimeState.from_dict(data)
        except:
            pass
    return RegimeState()


def save_regime_state(state: RegimeState, state_file: Path):
    """Save regime state to file."""
    with open(state_file, "w") as f:
        json.dump(state.to_dict(), f, indent=2)


def classify_regime(score: float, btc_above_200dma: bool) -> str:
    """
    Classify raw score into regime (without hysteresis).
    """
    if score >= REGIME_THRESHOLDS["aggressive"] and btc_above_200dma:
        return "aggressive"
    elif score <= REGIME_THRESHOLDS["defensive"]:
        return "defensive"
    else:
        return "balanced"


def should_flip_regime(
    current: str,
    proposed: str,
    consecutive_days: int,
    score: float
) -> bool:
    """
    Determine if regime should flip based on hysteresis rules.
    Requires either:
    - N consecutive days above threshold, OR
    - Score margin > override threshold
    """
    if current == proposed:
        return False

    # Check consecutive days requirement
    if consecutive_days >= HYSTERESIS["consecutive_days_required"]:
        return True

    # Check margin override
    margin = HYSTERESIS["margin_override"]

    if proposed == "aggressive":
        if score >= REGIME_THRESHOLDS["aggressive"] + margin:
            return True
    elif proposed == "defensive":
        if score <= REGIME_THRESHOLDS["defensive"] - margin:
            return True
    else:  # balanced
        # For balanced, check distance from both thresholds
        distance_from_aggressive = REGIME_THRESHOLDS["aggressive"] - score
        distance_from_defensive = score - REGIME_THRESHOLDS["defensive"]
        if min(distance_from_aggressive, distance_from_defensive) >= margin:
            return True

    return False


def determine_regime(
    scores: dict,
    state: Optional[RegimeState] = None,
    state_file: Optional[Path] = None
) -> tuple[str, RegimeState, dict]:
    """
    Determine current regime with hysteresis.

    Returns:
        (regime_name, updated_state, regime_info)
    """
    if state is None:
        if state_file:
            state = load_regime_state(state_file)
        else:
            state = RegimeState()

    total_score = scores["total"]
    btc_gate = scores.get("btc_above_200dma", False)

    # Raw classification (what the score says right now)
    proposed = classify_regime(total_score, btc_gate)

    # Track score history
    state.score_history.append(total_score)
    state.last_score = total_score

    # Check if proposed matches previous proposed (building consecutive days)
    if proposed == state.proposed_regime:
        state.consecutive_days += 1
    else:
        state.proposed_regime = proposed
        state.consecutive_days = 1

    # Determine if we should flip
    flip = should_flip_regime(
        state.current_regime,
        proposed,
        state.consecutive_days,
        total_score
    )

    if flip:
        state.current_regime = proposed
        state.regime_start_date = datetime.now().isoformat()
        state.consecutive_days = 0

    # Calculate days in regime
    days_in_regime = None
    if state.regime_start_date:
        try:
            start = datetime.fromisoformat(state.regime_start_date)
            days_in_regime = (datetime.now() - start).days
        except:
            pass

    # Calculate score trend
    trend = "flat"
    if len(state.score_history) >= 5:
        recent = state.score_history[-5:]
        avg_recent = sum(recent[-3:]) / 3
        avg_prior = sum(recent[:2]) / 2
        if avg_recent > avg_prior + 0.5:
            trend = "improving"
        elif avg_recent < avg_prior - 0.5:
            trend = "deteriorating"

    regime_info = {
        "regime": state.current_regime,
        "proposed_regime": proposed,
        "score": total_score,
        "btc_gate_passed": btc_gate,
        "consecutive_days": state.consecutive_days,
        "days_in_regime": days_in_regime,
        "score_trend": trend,
        "pending_flip": proposed != state.current_regime,
        "days_until_flip": max(0, HYSTERESIS["consecutive_days_required"] - state.consecutive_days) if proposed != state.current_regime else None,
    }

    # Save state if file provided
    if state_file:
        save_regime_state(state, state_file)

    return state.current_regime, state, regime_info
