"""
Standalone script to run briefings and alerts.
Called by GitHub Actions on schedule or manually.
"""

import os
import sys
import json
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetchers import fetch_all_data
from data.transforms import calculate_metrics
from scoring.engine import calculate_scores
from scoring.regime import determine_regime
from notifications.discord import send_daily_briefing, send_regime_change_alert

# State file to track previous regime
STATE_FILE = Path(__file__).parent.parent / "regime_state.json"


def load_previous_regime() -> str:
    """Load previous regime from state file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
                return state.get("regime", "balanced")
        except:
            pass
    return "balanced"


def run_briefing(daily: bool = True, check_change: bool = True):
    """Run the briefing/alert check."""
    
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    dashboard_url = os.environ.get("DASHBOARD_URL", "https://liquidity-dashboard.streamlit.app")
    
    if not webhook_url:
        print("ERROR: DISCORD_WEBHOOK_URL not set")
        sys.exit(1)
    
    print("Fetching data...")
    data = fetch_all_data()
    
    print("Calculating metrics...")
    metrics = calculate_metrics(data)
    
    print("Calculating scores...")
    scores = calculate_scores(metrics)
    
    print("Determining regime...")
    regime, state, regime_info = determine_regime(scores, state_file=STATE_FILE)
    
    total_score = scores.get("total", 0)
    previous_regime = load_previous_regime()

    # Get BTC data
    btc_data = metrics.get("btc", {})
    btc_price = btc_data.get("current_price")
    btc_200dma = btc_data.get("ma_200")

    print(f"Current regime: {regime} (score: {total_score:+.1f})")
    print(f"BTC: ${btc_price:,.0f}" if btc_price else "BTC: N/A")
    print(f"Previous regime: {previous_regime}")

    # Check for regime change
    if check_change and regime != previous_regime:
        print(f"ALERT: Regime changed from {previous_regime} to {regime}!")
        success = send_regime_change_alert(
            webhook_url=webhook_url,
            old_regime=previous_regime,
            new_regime=regime,
            score=total_score,
            dashboard_url=dashboard_url,
            btc_price=btc_price,
        )
        if success:
            print("[OK] Regime change alert sent!")
        else:
            print("[FAIL] Failed to send regime change alert")

    # Send daily briefing
    if daily:
        print("Sending daily briefing...")
        success = send_daily_briefing(
            webhook_url=webhook_url,
            regime=regime,
            score=total_score,
            metrics=metrics,
            scores=scores,
            dashboard_url=dashboard_url,
            btc_price=btc_price,
            btc_200dma=btc_200dma,
        )
        if success:
            print("[OK] Daily briefing sent!")
        else:
            print("[FAIL] Failed to send daily briefing")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", action="store_true", help="Send daily briefing")
    parser.add_argument("--check-only", action="store_true", help="Only check for regime change, no daily")
    args = parser.parse_args()
    
    if args.check_only:
        run_briefing(daily=False, check_change=True)
    else:
        run_briefing(daily=True, check_change=True)
