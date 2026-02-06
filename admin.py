"""
FlowState Admin Panel
Run locally: streamlit run admin.py --server.port 8502
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="FlowState Admin",
    page_icon="⚙️",
    layout="centered",
)

# Simple password protection
ADMIN_PASSWORD = "nakamoto2026"  # Change this or use env var

SUBSCRIBERS_FILE = Path(__file__).parent / "subscribers.json"
FEEDBACK_FILE = Path(__file__).parent / "feedback.json"


def load_subscribers():
    if SUBSCRIBERS_FILE.exists():
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return {"subscribers": []}


def save_subscribers(data):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_feedback():
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    return {"feedback": []}


def main():
    st.markdown("""
    <style>
        .stApp { background: #0F172A; }
        h1, h2, h3 { color: #E2E8F0 !important; }
        p, li { color: #94A3B8; }
    </style>
    """, unsafe_allow_html=True)

    st.title("⚙️ FlowState Admin")

    # Initialize session state
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    # Password gate - show login form if not authenticated
    if not st.session_state.admin_authenticated:
        st.markdown("---")
        st.subheader("🔐 Login Required")

        with st.form("login_form"):
            password = st.text_input("Enter password:", type="password", placeholder="Password")
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Wrong password")

        st.stop()  # Stop execution here if not authenticated

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📧 Test Emails", "👥 Subscribers", "💬 Feedback", "🧪 Email Preview"])

    # ==========================================================================
    # TAB 1: Test Emails
    # ==========================================================================
    with tab1:
        st.header("Send Test Emails")

        from subscribers import send_confirmation_email

        test_email = st.text_input("Recipient email", value="elijah.wbanks@gmail.com")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Send Welcome Email", use_container_width=True):
                success = send_confirmation_email(test_email, "daily")
                if success:
                    st.success(f"✓ Sent to {test_email}")
                else:
                    st.error("Failed - check RESEND_API_KEY")

        with col2:
            if st.button("Send Weekly Variant", use_container_width=True):
                success = send_confirmation_email(test_email, "weekly")
                if success:
                    st.success(f"✓ Sent to {test_email}")
                else:
                    st.error("Failed - check RESEND_API_KEY")

        with col3:
            if st.button("Send On-Change Variant", use_container_width=True):
                success = send_confirmation_email(test_email, "on_change")
                if success:
                    st.success(f"✓ Sent to {test_email}")
                else:
                    st.error("Failed - check RESEND_API_KEY")

        st.divider()

        st.subheader("Send Regime Update (Coming Soon)")
        st.info("Regime update emails not implemented yet. This is where you'd test the daily/weekly digest.")

    # ==========================================================================
    # TAB 2: Subscribers
    # ==========================================================================
    with tab2:
        st.header("Subscriber Management")

        data = load_subscribers()
        subscribers = data.get("subscribers", [])

        st.metric("Total Subscribers", len(subscribers))

        if subscribers:
            for i, sub in enumerate(subscribers):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.text(sub["email"])
                with col2:
                    st.text(sub["cadence"])
                with col3:
                    st.text(sub["subscribed_at"][:10])
                with col4:
                    if st.button("🗑️", key=f"del_{i}"):
                        subscribers.pop(i)
                        save_subscribers({"subscribers": subscribers})
                        st.rerun()
        else:
            st.info("No subscribers yet")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear All Subscribers", type="secondary"):
                save_subscribers({"subscribers": []})
                st.success("Cleared!")
                st.rerun()

        with col2:
            new_email = st.text_input("Add test subscriber", placeholder="test@example.com")
            if st.button("Add"):
                if new_email:
                    subscribers.append({
                        "email": new_email,
                        "cadence": "daily",
                        "subscribed_at": datetime.now().isoformat(),
                        "confirmed": False,
                    })
                    save_subscribers({"subscribers": subscribers})
                    st.success(f"Added {new_email}")
                    st.rerun()

    # ==========================================================================
    # TAB 3: Feedback
    # ==========================================================================
    with tab3:
        st.header("User Feedback")

        feedback_data = load_feedback()
        feedback_list = feedback_data.get("feedback", [])

        st.metric("Total Feedback", len(feedback_list))

        if feedback_list:
            for fb in reversed(feedback_list):  # Most recent first
                type_emoji = {
                    "feature": "💡",
                    "bug": "🐛",
                    "general": "💬",
                    "love": "💙"
                }.get(fb.get("type", ""), "📝")

                with st.expander(f"{type_emoji} {fb.get('type', 'unknown').title()} — {fb.get('timestamp', '')[:10]}"):
                    st.write(fb.get("text", ""))
                    if fb.get("email"):
                        st.caption(f"From: {fb['email']}")
        else:
            st.info("No feedback yet")

    # ==========================================================================
    # TAB 4: Email Preview
    # ==========================================================================
    with tab4:
        st.header("Email HTML Preview")
        st.caption("See what the emails look like without sending")

        cadence = st.selectbox("Cadence variant", ["daily", "weekly", "on_change"])

        cadence_text = {
            "daily": "daily",
            "weekly": "weekly (every Monday)",
            "on_change": "when the regime changes",
        }.get(cadence, cadence)

        # The email HTML template (same as in subscribers.py)
        email_html = f"""
        <div style="background: #0a0f1a; padding: 20px; border-radius: 12px;">
            <div style="max-width: 520px; margin: 0 auto; padding: 48px 24px; background: #0a0f1a; font-family: 'Segoe UI', system-ui, sans-serif;">

                <!-- Header Bar -->
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
                        <div style="margin-bottom: 12px;">
                            <span style="font-size: 24px; margin-right: 12px;">🚀</span>
                            <span style="font-size: 18px; font-weight: 700; color: #22C55E;">AGGRESSIVE</span>
                            <span style="font-size: 12px; color: #86EFAC; margin-left: 8px;">Score: +5.2</span>
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
                    <a href="#" style="display: inline-block; background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); color: white; font-weight: 700; font-size: 15px; padding: 16px 40px; border-radius: 10px; text-decoration: none;">
                        Open Dashboard →
                    </a>
                </div>

                <!-- The Five Forces -->
                <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(71, 85, 105, 0.2); border-radius: 12px; padding: 20px; margin-bottom: 32px;">
                    <p style="margin: 0 0 14px 0; font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1.5px;">
                        The Five Forces We Track
                    </p>
                    <div style="color: #94A3B8; font-size: 13px; line-height: 2;">
                        📊 Fed Balance Sheet<br>
                        🏦 Reverse Repo<br>
                        💵 Dollar Index<br>
                        📉 Credit Spreads<br>
                        🪙 Stablecoin Flows
                    </div>
                </div>

                <!-- Footer -->
                <div style="text-align: center; padding-top: 24px; border-top: 1px solid rgba(71, 85, 105, 0.2);">
                    <p style="margin: 0 0 8px 0; font-size: 13px; color: #64748B;">
                        Built by <a href="#" style="color: #60A5FA; text-decoration: none; font-weight: 600;">Elijah Wilbanks</a>
                    </p>
                    <p style="margin: 0; font-size: 10px; color: #334155;">
                        Not financial advice. For educational purposes only.
                    </p>
                </div>

            </div>
        </div>
        """

        st.markdown(email_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
