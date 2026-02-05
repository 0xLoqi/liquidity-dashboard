"""
Subscriber management for email alerts.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import os

SUBSCRIBERS_FILE = Path(__file__).parent / "subscribers.json"


def load_subscribers() -> dict:
    """Load subscribers from JSON file."""
    if SUBSCRIBERS_FILE.exists():
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return {"subscribers": []}


def save_subscribers(data: dict):
    """Save subscribers to JSON file."""
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_subscriber(email: str, cadence: str = "daily") -> tuple[bool, str]:
    """
    Add a new subscriber.
    Returns (success, message).
    """
    email = email.strip().lower()

    # Basic validation
    if not email or "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    data = load_subscribers()

    # Check for duplicates
    existing_emails = [s["email"] for s in data["subscribers"]]
    if email in existing_emails:
        return False, "You're already subscribed!"

    # Add subscriber
    data["subscribers"].append({
        "email": email,
        "cadence": cadence,
        "subscribed_at": datetime.now().isoformat(),
        "confirmed": False,
    })

    save_subscribers(data)
    return True, "You're subscribed! You'll receive updates based on your preference."


def send_confirmation_email(email: str, cadence: str) -> bool:
    """Send a confirmation email via Resend."""
    resend_api_key = os.environ.get("RESEND_API_KEY")

    if not resend_api_key:
        print("Warning: RESEND_API_KEY not set, skipping confirmation email")
        return False

    try:
        import resend
        resend.api_key = resend_api_key

        cadence_text = {
            "daily": "daily",
            "weekly": "weekly (every Monday)",
            "on_change": "when the regime changes",
        }.get(cadence, cadence)

        resend.Emails.send({
            "from": "FlowState <alerts@flowstate.markets>",
            "to": email,
            "subject": "Welcome to FlowState — You're in",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; background-color: #0a0f1a; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;">
                <div style="max-width: 520px; margin: 0 auto; padding: 48px 24px;">

                    <!-- Animated Header Bar -->
                    <div style="background: linear-gradient(90deg, #3B82F6 0%, #60A5FA 50%, #3B82F6 100%); height: 4px; border-radius: 2px; margin-bottom: 40px;"></div>

                    <!-- Logo + Title -->
                    <div style="text-align: center; margin-bottom: 40px;">
                        <div style="display: inline-block; background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 16px; padding: 16px 24px; margin-bottom: 20px;">
                            <span style="font-size: 42px;">🌊</span>
                        </div>
                        <h1 style="margin: 0; font-size: 32px; font-weight: 800; color: #F1F5F9; letter-spacing: -1px;">
                            FlowState
                        </h1>
                        <p style="margin: 8px 0 0 0; font-size: 12px; color: #60A5FA; font-weight: 600; letter-spacing: 2px; text-transform: uppercase;">
                            Macro Liquidity × Crypto Regimes
                        </p>
                    </div>

                    <!-- Welcome Message -->
                    <div style="text-align: center; margin-bottom: 36px;">
                        <h2 style="margin: 0 0 12px 0; font-size: 24px; font-weight: 700; color: #E2E8F0;">
                            Welcome aboard
                        </h2>
                        <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #94A3B8;">
                            You'll get updates <span style="color: #60A5FA; font-weight: 600;">{cadence_text}</span>
                        </p>
                    </div>

                    <!-- Sample Update Preview -->
                    <div style="background: linear-gradient(145deg, #1E293B 0%, #0F172A 100%); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 16px; padding: 24px; margin-bottom: 24px;">
                        <p style="margin: 0 0 16px 0; font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1.5px;">
                            Here's what your updates look like
                        </p>

                        <!-- Mock Regime Card -->
                        <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.02) 100%); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 20px; margin-bottom: 16px;">
                            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                                <span style="font-size: 24px; margin-right: 12px;">🚀</span>
                                <div>
                                    <div style="font-size: 18px; font-weight: 700; color: #22C55E;">AGGRESSIVE</div>
                                    <div style="font-size: 12px; color: #86EFAC;">Score: +5.2</div>
                                </div>
                            </div>
                            <p style="margin: 0; font-size: 13px; color: #94A3B8; line-height: 1.5;">
                                Fed liquidity expanding, dollar weakening, stablecoins flowing in. Risk-on conditions favor crypto exposure.
                            </p>
                        </div>

                        <!-- Force Pills -->
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            <span style="background: rgba(34, 197, 94, 0.15); color: #86EFAC; font-size: 11px; font-weight: 600; padding: 6px 12px; border-radius: 20px;">📈 Fed +1.5</span>
                            <span style="background: rgba(34, 197, 94, 0.15); color: #86EFAC; font-size: 11px; font-weight: 600; padding: 6px 12px; border-radius: 20px;">💵 DXY +1.0</span>
                            <span style="background: rgba(251, 191, 36, 0.15); color: #FCD34D; font-size: 11px; font-weight: 600; padding: 6px 12px; border-radius: 20px;">🪙 Stable 0</span>
                        </div>
                    </div>

                    <!-- CTA Button -->
                    <div style="text-align: center; margin-bottom: 36px;">
                        <a href="https://flowstate.markets" style="display: inline-block; background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); color: white; font-weight: 700; font-size: 15px; padding: 16px 40px; border-radius: 10px; text-decoration: none; letter-spacing: 0.3px; box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);">
                            Open Dashboard →
                        </a>
                    </div>

                    <!-- The Five Forces -->
                    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(71, 85, 105, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 32px;">
                        <p style="margin: 0 0 14px 0; font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1.5px;">
                            The Five Forces We Track
                        </p>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-size: 13px; color: #94A3B8; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">📊 Fed Balance Sheet</td>
                                <td style="padding: 8px 0; font-size: 12px; color: #64748B; text-align: right; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">WALCL</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-size: 13px; color: #94A3B8; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">🏦 Reverse Repo</td>
                                <td style="padding: 8px 0; font-size: 12px; color: #64748B; text-align: right; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">RRPONTSYD</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-size: 13px; color: #94A3B8; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">💵 Dollar Index</td>
                                <td style="padding: 8px 0; font-size: 12px; color: #64748B; text-align: right; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">DXY</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-size: 13px; color: #94A3B8; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">📉 Credit Spreads</td>
                                <td style="padding: 8px 0; font-size: 12px; color: #64748B; text-align: right; border-bottom: 1px solid rgba(71, 85, 105, 0.2);">HY OAS</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-size: 13px; color: #94A3B8;">🪙 Stablecoin Flows</td>
                                <td style="padding: 8px 0; font-size: 12px; color: #64748B; text-align: right;">DefiLlama</td>
                            </tr>
                        </table>
                    </div>

                    <!-- Footer -->
                    <div style="text-align: center; padding-top: 24px; border-top: 1px solid rgba(71, 85, 105, 0.2);">
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #64748B;">
                            Built by <a href="https://www.linkedin.com/in/elijah-wilbanks/" style="color: #60A5FA; text-decoration: none; font-weight: 600;">Elijah Wilbanks</a>
                        </p>
                        <p style="margin: 0 0 16px 0; font-size: 12px; color: #475569; line-height: 1.6;">
                            Reply to unsubscribe or share feedback
                        </p>
                        <p style="margin: 0; font-size: 10px; color: #334155; line-height: 1.5;">
                            Not financial advice. For educational purposes only.<br>
                            Past performance does not guarantee future results.
                        </p>
                    </div>

                </div>
            </body>
            </html>
            """
        })
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
