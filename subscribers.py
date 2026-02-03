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
            "from": "FlowState <onboarding@resend.dev>",  # Use your verified domain, or resend.dev for testing
            "to": email,
            "subject": "🌊 Welcome to FlowState",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="margin: 0; padding: 0; background-color: #0F172A; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;">
                <div style="max-width: 560px; margin: 0 auto; padding: 40px 20px;">
                    <!-- Header -->
                    <div style="text-align: center; margin-bottom: 32px;">
                        <span style="font-size: 36px;">🌊</span>
                        <h1 style="margin: 12px 0 0 0; font-size: 28px; font-weight: 800; color: #E2E8F0; letter-spacing: -0.5px;">
                            FlowState
                        </h1>
                        <p style="margin: 8px 0 0 0; font-size: 13px; color: #3B82F6; font-weight: 500; letter-spacing: 0.5px;">
                            REAL-TIME CRYPTO LIQUIDITY TRACKER
                        </p>
                    </div>

                    <!-- Main Card -->
                    <div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 16px; padding: 32px; margin-bottom: 24px;">
                        <h2 style="margin: 0 0 20px 0; font-size: 22px; font-weight: 700; color: #E2E8F0;">
                            You're in! 🎉
                        </h2>

                        <p style="margin: 0 0 20px 0; font-size: 15px; line-height: 1.7; color: #CBD5E1;">
                            You'll receive regime updates <strong style="color: #3B82F6;">{cadence_text}</strong>.
                        </p>

                        <p style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.7; color: #CBD5E1;">
                            Each update includes the current regime (🚀 Aggressive, ⚖️ Balanced, or 🛡️ Defensive),
                            the composite score, and what's driving conditions.
                        </p>

                        <!-- CTA Button -->
                        <a href="https://flowstate.streamlit.app" style="display: inline-block; background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); color: white; font-weight: 600; font-size: 14px; padding: 14px 28px; border-radius: 8px; text-decoration: none; letter-spacing: 0.3px;">
                            View Dashboard →
                        </a>
                    </div>

                    <!-- What to Expect -->
                    <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(71, 85, 105, 0.25); border-radius: 12px; padding: 24px; margin-bottom: 24px;">
                        <h3 style="margin: 0 0 16px 0; font-size: 14px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">
                            What We Track
                        </h3>
                        <div style="font-size: 14px; line-height: 1.8; color: #94A3B8;">
                            <div style="margin-bottom: 8px;">📊 Fed Balance Sheet & Reverse Repo</div>
                            <div style="margin-bottom: 8px;">💵 Dollar Strength & Credit Spreads</div>
                            <div style="margin-bottom: 8px;">🪙 Stablecoin Flows & BTC Trend</div>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div style="text-align: center; padding-top: 20px; border-top: 1px solid rgba(71, 85, 105, 0.25);">
                        <p style="margin: 0 0 12px 0; font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 1px;">
                            FlowState
                        </p>
                        <p style="margin: 0; font-size: 12px; color: #64748B; line-height: 1.6;">
                            Reply to this email to unsubscribe or share feedback.<br>
                            Not financial advice. For educational purposes only.
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
