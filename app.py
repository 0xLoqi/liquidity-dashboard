"""
FlowState - Real-time crypto liquidity regime tracker
A local Streamlit app that classifies macro + crypto environment into risk regimes.
Designed for LinkedIn-shareable, educational presentation.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json

# Configure page
st.set_page_config(
    page_title="FlowState",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject Open Graph meta tags for LinkedIn previews
def inject_og_meta():
    """Inject Open Graph meta tags for social sharing."""
    st.markdown("""
    <head>
        <meta property="og:title" content="FlowState - Crypto Liquidity Regime Tracker" />
        <meta property="og:description" content="Track 5 macro liquidity indicators and their historical relationship with crypto markets. Educational tool by Elijah Wilbanks." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://flowstate.streamlit.app" />
        <meta property="og:image" content="https://flowstate.streamlit.app/og-image.png" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="FlowState - Crypto Liquidity Regime Tracker" />
        <meta name="twitter:description" content="Track 5 macro liquidity indicators and their historical relationship with crypto markets. Educational tool." />
    </head>
    """, unsafe_allow_html=True)

inject_og_meta()

# Local imports
from data.fetchers import fetch_all_data, has_fred_api_key
from data.cache import CacheManager
from data.transforms import calculate_metrics, get_chart_data
from scoring.engine import calculate_scores
from scoring.regime import determine_regime, RegimeState
from scoring.explanations import generate_explanation
from ui.components import (
    inject_custom_css,
    render_regime_hero,
    render_five_forces_strip,
    render_notifications_cta,
    render_disclaimer_modal,
    render_btc_gate_section,
    render_metric_card,
    render_section_header,
    render_feedback_form,
    format_large_number,
    format_percentage,
)
from ui.charts import create_sparkline, create_score_gauge, create_btc_chart
from config import CACHE_TTL, REGIME_THRESHOLDS, WEIGHTS

# =============================================================================
# COPY SYSTEM - Plain English vs Finance Mode
# =============================================================================

REGIME_TAGLINES = {
    "aggressive": {
        "plain": "Liquidity indicators are mostly positive",
        "finance": "Liquidity conditions are expansionary",
    },
    "balanced": {
        "plain": "Indicators are showing mixed signals",
        "finance": "Mixed liquidity signals across metrics",
    },
    "defensive": {
        "plain": "Liquidity indicators are mostly negative",
        "finance": "Liquidity conditions are contracting",
    },
}

REGIME_POSTURES = {
    "aggressive": {
        "plain": "Similar conditions have historically preceded crypto rallies",
        "finance": "Liquidity environment historically associated with risk asset strength",
    },
    "balanced": {
        "plain": "Indicators are sending conflicting signals",
        "finance": "Mixed liquidity signals across indicators",
    },
    "defensive": {
        "plain": "Similar conditions have historically preceded crypto weakness",
        "finance": "Liquidity environment historically associated with risk asset drawdowns",
    },
}

# Metric titles for both modes
METRIC_TITLES = {
    "walcl": {"plain": "Fed Money Printing", "finance": "Fed Balance Sheet (WALCL)"},
    "rrp": {"plain": "Sideline Cash", "finance": "Reverse Repo (RRP)"},
    "hy_spread": {"plain": "Risk Appetite", "finance": "HY Credit Spreads"},
    "dxy": {"plain": "Dollar Strength", "finance": "Dollar Index (DXY)"},
    "stablecoin": {"plain": "Crypto Dry Powder", "finance": "Stablecoin Supply"},
    "btc_gate": {"plain": "Bitcoin Trend", "finance": "BTC vs 200 DMA (Gate)"},
}

# "Why it matters" micro-copy for each metric
METRIC_WHY = {
    "walcl": {
        "plain": "When the Fed prints money, crypto tends to go up",
        "finance": "QE expansion injects liquidity into risk assets",
    },
    "rrp": {
        "plain": "Money leaving the sidelines is looking for returns",
        "finance": "RRP drawdown releases capital into markets",
    },
    "hy_spread": {
        "plain": "When investors chase risky bonds, they'll chase crypto too",
        "finance": "Tight spreads indicate risk-seeking behavior",
    },
    "dxy": {
        "plain": "A weaker dollar makes crypto more attractive globally",
        "finance": "Dollar weakness eases global financial conditions",
    },
    "stablecoin": {
        "plain": "More stablecoins = more money ready to buy crypto",
        "finance": "Stablecoin growth signals capital inflows to crypto",
    },
    "btc_gate": {
        "plain": "Bitcoin above its 200-day average confirms the uptrend",
        "finance": "BTC above 200 DMA confirms trend strength",
    },
}

# Metric explanations for info tooltips
METRIC_INFO = {
    "walcl": {
        "name": "Fed Balance Sheet",
        "desc": "Total assets held by the Federal Reserve. Expansion = more liquidity injected into the system.",
        "bullish": "Growing 0.5%+ over 4 weeks (Fed adding liquidity)",
        "bearish": "Shrinking 0.5%+ over 4 weeks (Fed tightening)",
    },
    "rrp": {
        "name": "Reverse Repo (RRP)",
        "desc": "Cash parked overnight at the Fed by money market funds. Money leaving RRP enters the market.",
        "bullish": "Draining 5%+ over 4 weeks (liquidity entering markets)",
        "bearish": "Building 5%+ over 4 weeks (liquidity leaving markets)",
    },
    "hy_spread": {
        "name": "High Yield Spreads",
        "desc": "Difference between junk bond yields and Treasuries. Measures credit risk appetite.",
        "bullish": "Tightening 10%+ (risk-on, investors buying junk bonds)",
        "bearish": "Widening 10%+ (risk-off, investors fleeing to safety)",
    },
    "dxy": {
        "name": "Dollar Index (DXY)",
        "desc": "Trade-weighted US dollar strength. Weaker dollar = easier financial conditions globally.",
        "bullish": "Weakening 2%+ over 4 weeks (easier conditions)",
        "bearish": "Strengthening 2%+ over 4 weeks (tighter conditions)",
    },
    "stablecoin": {
        "name": "Stablecoin Supply",
        "desc": "Combined USDT + USDC market cap. Proxy for capital flows into/out of crypto.",
        "bullish": "Growing 2%+ over 21 days (capital inflows)",
        "bearish": "Shrinking 2%+ over 21 days (capital outflows)",
    },
    "btc_gate": {
        "name": "BTC 200 DMA Gate",
        "desc": "Bitcoin price relative to its 200-day moving average. Acts as a gate for Aggressive regime.",
        "bullish": "BTC trading above 200 DMA (uptrend confirmed)",
        "bearish": "BTC trading below 200 DMA (blocks Aggressive regime)",
    },
}

# Initialize cache and state file paths
CACHE = CacheManager()
STATE_FILE = Path(__file__).parent / "regime_state.json"


def get_copy(key: str, mode: str, copy_dict: dict) -> str:
    """Get copy text based on mode (plain/finance)."""
    return copy_dict.get(key, {}).get(mode, "")


def load_data(force_refresh: bool = False):
    """Load data with caching."""
    if force_refresh:
        CACHE.invalidate_all()

    cached_data = CACHE.get("all_data")
    if cached_data:
        return cached_data

    with st.spinner("Fetching latest data..."):
        data = fetch_all_data()
        CACHE.set("all_data", data, ttl=min(CACHE_TTL.values()))

    return data


def get_days_in_regime(state_file: Path) -> tuple:
    """Get how many days we've been in the current regime."""
    try:
        if state_file.exists():
            with open(state_file, "r") as f:
                state = json.load(f)
                days = state.get("days_in_regime", 0)
                start_date = state.get("regime_start_date", "")
                return days, start_date
    except Exception:
        pass
    return 0, ""


def main():
    """Main app function."""

    # Initialize session state for disclaimer
    if "disclaimer_accepted" not in st.session_state:
        st.session_state.disclaimer_accepted = False

    # Inject custom CSS
    inject_custom_css()

    # ==========================================================================
    # DISCLAIMER GATE - Must accept before viewing
    # ==========================================================================
    if not st.session_state.disclaimer_accepted:
        render_disclaimer_modal()
        st.stop()

    # ==========================================================================
    # HEADER WITH ALERTS
    # ==========================================================================
    header_col1, header_col2 = st.columns([3, 1])

    with header_col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding: 16px 0 8px 0;">
            <span style="font-size: 28px;">🌊</span>
            <h1 style="margin: 0; font-size: 24px; font-weight: 800; color: #E2E8F0; letter-spacing: -0.5px; font-family: 'Outfit', sans-serif;">
                FlowState
            </h1>
            <span style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); color: #3B82F6; font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 12px; text-transform: uppercase; letter-spacing: 1px;">
                Live
            </span>
        </div>
        """, unsafe_allow_html=True)

    with header_col2:
        st.markdown('<div style="padding-top: 16px;"></div>', unsafe_allow_html=True)
        with st.popover("🔔 Get Alerts", use_container_width=True):
            render_notifications_cta()

    # Initialize plain_english mode from session state or default
    if "plain_english" not in st.session_state:
        st.session_state.plain_english = True
    plain_english = st.session_state.plain_english
    mode = "plain" if plain_english else "finance"

    # ==========================================================================
    # LOAD DATA
    # ==========================================================================
    try:
        data = load_data()
        metrics = calculate_metrics(data)
        scores = calculate_scores(metrics)
        regime, state, regime_info = determine_regime(scores, state_file=STATE_FILE)
        explanation = generate_explanation(regime, scores, metrics, regime_info)
        charts = get_chart_data(data)
        days_in_regime, regime_start_date = get_days_in_regime(STATE_FILE)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure you have an internet connection and try refreshing.")
        return

    # ==========================================================================
    # HERO SECTION - Prominent Regime Display
    # ==========================================================================
    render_regime_hero(
        regime=regime,
        score=scores["total"],
        tagline=get_copy(regime, mode, REGIME_TAGLINES),
        posture=get_copy(regime, mode, REGIME_POSTURES),
        days_in_regime=days_in_regime,
        regime_start_date=regime_start_date,
    )

    # ==========================================================================
    # SCORE GAUGE
    # ==========================================================================
    gauge = create_score_gauge(
        scores["total"],
        min_val=-6.5,
        max_val=6.5,
        thresholds={"defensive": REGIME_THRESHOLDS["defensive"], "aggressive": REGIME_THRESHOLDS["aggressive"]}
    )
    st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

    # ==========================================================================
    # FIVE FORCES STRIP - At-a-glance indicator summary
    # ==========================================================================
    render_five_forces_strip(scores, plain_english=plain_english)

    # ==========================================================================
    # INDICATOR CARDS - Row 1
    # ==========================================================================
    render_section_header("The Five Forces" if plain_english else "Liquidity Indicators")

    col1, col2, col3 = st.columns(3)

    # WALCL Card
    with col1:
        walcl = metrics.get("walcl", {})
        walcl_score = scores["individual"].get("walcl", {})
        score_val = walcl_score.get("score", 0)
        direction = "positive" if score_val > 0 else ("negative" if score_val < 0 else "neutral")

        walcl_value = walcl.get("current")
        if walcl_value:
            walcl_value = walcl_value * 1e6

        # Simple directional text instead of misleading percentages
        if score_val > 0:
            delta_text = "↑ Expanding" if plain_english else "↑ QE"
        elif score_val < 0:
            delta_text = "↓ Shrinking" if plain_english else "↓ QT"
        else:
            delta_text = "→ Flat"

        render_metric_card(
            title=get_copy("walcl", mode, METRIC_TITLES),
            value=format_large_number(walcl_value),
            delta=delta_text,
            delta_direction=direction,
            weight=WEIGHTS["walcl"],
            info=METRIC_INFO.get("walcl"),
            why=get_copy("walcl", mode, METRIC_WHY),
            source="FRED",
        )

        if "walcl" in charts:
            chart = create_sparkline(charts["walcl"], height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # RRP Card
    with col2:
        rrp = metrics.get("rrp", {})
        rrp_score = scores["individual"].get("rrp", {})
        score_val = rrp_score.get("score", 0)
        direction = "positive" if score_val > 0 else ("negative" if score_val < 0 else "neutral")

        rrp_value = rrp.get("current")
        if rrp_value:
            rrp_value = rrp_value * 1e9

        # Simple directional text - RRP draining is bullish
        if score_val > 0:
            delta_text = "↓ Draining" if plain_english else "↓ Draining"
        elif score_val < 0:
            delta_text = "↑ Building" if plain_english else "↑ Building"
        else:
            delta_text = "→ Stable"

        render_metric_card(
            title=get_copy("rrp", mode, METRIC_TITLES),
            value=format_large_number(rrp_value),
            delta=delta_text,
            delta_direction=direction,
            weight=WEIGHTS["rrp"],
            info=METRIC_INFO.get("rrp"),
            why=get_copy("rrp", mode, METRIC_WHY),
            source="FRED",
        )

        if "rrpontsyd" in charts:
            chart = create_sparkline(charts["rrpontsyd"], height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # HY Spread Card
    with col3:
        hy = metrics.get("hy_spread", {})
        hy_score = scores["individual"].get("hy_spread", {})
        delta = hy.get("delta_4w")
        direction = "positive" if hy_score.get("score", 0) > 0 else (
            "negative" if hy_score.get("score", 0) < 0 else "neutral"
        )

        current = hy.get("current")
        value_str = f"{current*100:.0f} bps" if current else "N/A"

        render_metric_card(
            title=get_copy("hy_spread", mode, METRIC_TITLES),
            value=value_str,
            delta=format_percentage(delta, plain_english=plain_english) if delta else None,
            delta_direction=direction,
            weight=WEIGHTS["hy_spread"],
            info=METRIC_INFO.get("hy_spread"),
            why=get_copy("hy_spread", mode, METRIC_WHY),
            source="FRED",
        )

        if "bamlh0a0hym2" in charts:
            chart = create_sparkline(charts["bamlh0a0hym2"], height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # ==========================================================================
    # INDICATOR CARDS - Row 2
    # ==========================================================================
    col1, col2 = st.columns(2)

    # DXY Card
    with col1:
        dxy = metrics.get("dxy", {})
        dxy_score = scores["individual"].get("dxy", {})
        delta = dxy.get("delta_4w")
        direction = "positive" if dxy_score.get("score", 0) > 0 else (
            "negative" if dxy_score.get("score", 0) < 0 else "neutral"
        )

        current = dxy.get("current")
        value_str = f"{current:.2f}" if current else "N/A"

        render_metric_card(
            title=get_copy("dxy", mode, METRIC_TITLES),
            value=value_str,
            delta=format_percentage(delta, plain_english=plain_english) if delta else None,
            delta_direction=direction,
            weight=WEIGHTS["dxy"],
            info=METRIC_INFO.get("dxy"),
            why=get_copy("dxy", mode, METRIC_WHY),
            source="FRED",
        )

        if "dtwexbgs" in charts:
            chart = create_sparkline(charts["dtwexbgs"], height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # Stablecoin Card
    with col2:
        stable = metrics.get("stablecoin", {})
        stable_score = scores["individual"].get("stablecoin", {})
        delta = stable.get("delta_21d")
        direction = "positive" if stable_score.get("score", 0) > 0 else (
            "negative" if stable_score.get("score", 0) < 0 else "neutral"
        )

        render_metric_card(
            title=get_copy("stablecoin", mode, METRIC_TITLES),
            value=format_large_number(stable.get("current")),
            delta=format_percentage(delta, plain_english=plain_english) if delta else None,
            delta_direction=direction,
            weight=WEIGHTS["stablecoin"],
            info=METRIC_INFO.get("stablecoin"),
            why=get_copy("stablecoin", mode, METRIC_WHY),
            source="DefiLlama",
        )

        if "stablecoins" in charts:
            chart = create_sparkline(charts["stablecoins"], value_col="supply", height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # ==========================================================================
    # BTC TREND GATE - Separate from Five Forces
    # ==========================================================================
    btc = metrics.get("btc", {})
    current_price = btc.get("current_price")
    ma_200 = btc.get("ma_200")
    above = btc.get("above_200dma", False)

    render_btc_gate_section(
        current_price=current_price,
        above_200dma=above,
        plain_english=plain_english,
    )

    # BTC Chart below the gate
    if "btc" in charts:
        btc_chart = create_btc_chart(charts["btc"], ma_200=ma_200, height=160)
        st.plotly_chart(btc_chart, use_container_width=True, config={"displayModeBar": False})

    # ==========================================================================
    # TECHNICAL DETAILS (Collapsible)
    # ==========================================================================
    with st.expander("📊 Technical Details & Scoring"):
        breakdown_col1, breakdown_col2 = st.columns([2, 1])

        with breakdown_col1:
            total_contrib = 0
            rows_html = ""

            for name, data in scores["individual"].items():
                score = data.get("score", 0)
                weight = data.get("weight", 1)
                weighted = data.get("weighted", 0)
                total_contrib += weighted

                if score > 0:
                    signal_color = "#22C55E"
                    signal_dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{signal_color};margin-right:8px;"></span>'
                elif score < 0:
                    signal_color = "#EF4444"
                    signal_dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{signal_color};margin-right:8px;"></span>'
                else:
                    signal_color = "#64748B"
                    signal_dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{signal_color};margin-right:8px;opacity:0.5;"></span>'

                info = METRIC_INFO.get(name, {})
                display_name = info.get("name", name.upper().replace("_", " "))

                rows_html += f'''<tr style="border-bottom: 1px solid rgba(71, 85, 105, 0.2);">
<td style="padding: 14px 12px; color: #E2E8F0; font-size: 13px;">{display_name}</td>
<td style="text-align: center; padding: 14px 12px; font-family: 'JetBrains Mono', monospace; font-size: 13px;">{signal_dot}<span style="color: {signal_color};">{score:+d}</span></td>
<td style="text-align: center; padding: 14px 12px; color: #64748B; font-size: 12px;">{weight}x</td>
<td style="text-align: center; padding: 14px 12px; color: {signal_color}; font-weight: 600; font-family: 'JetBrains Mono', monospace;">{weighted:+.1f}</td>
</tr>'''

            table_html = f'''<div class="metric-card" style="padding: 0; overflow: hidden;">
<table style="width: 100%; border-collapse: collapse;">
<tr style="background: rgba(30, 41, 59, 0.5);">
<th style="text-align: left; padding: 12px; color: #64748B; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Metric</th>
<th style="text-align: center; padding: 12px; color: #64748B; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Signal</th>
<th style="text-align: center; padding: 12px; color: #64748B; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Weight</th>
<th style="text-align: center; padding: 12px; color: #64748B; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Contrib</th>
</tr>
{rows_html}
<tr style="background: rgba(59, 130, 246, 0.1);">
<td style="padding: 14px 12px; color: #E2E8F0; font-weight: 600; font-size: 13px;">Total Score</td>
<td style="text-align: center; padding: 14px 12px;"></td>
<td style="text-align: center; padding: 14px 12px;"></td>
<td style="text-align: center; padding: 14px 12px; color: #3B82F6; font-weight: 700; font-size: 16px; font-family: 'JetBrains Mono', monospace;">{total_contrib:+.1f}</td>
</tr>
</table>
</div>'''
            st.markdown(table_html, unsafe_allow_html=True)

        with breakdown_col2:
            btc_passed = scores.get('btc_above_200dma')
            btc_color = '#22C55E' if btc_passed else '#EF4444'
            btc_status = 'Passed' if btc_passed else 'Failed'
            btc_dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{btc_color};margin-right:8px;"></span>'
            st.markdown(f"""<div class="metric-card">
<div class="metric-title">Regime Thresholds</div>
<div style="margin-top: 14px; font-size: 13px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 8px 10px; background: rgba(34, 197, 94, 0.06); border-radius: 4px;">
<span style="color: #22C55E; font-weight: 500;">Aggressive</span>
<span style="color: #64748B; font-family: 'JetBrains Mono', monospace; font-size: 12px;">≥ +4.0</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 8px 10px; background: rgba(251, 191, 36, 0.06); border-radius: 4px;">
<span style="color: #FBBF24; font-weight: 500;">Balanced</span>
<span style="color: #64748B; font-family: 'JetBrains Mono', monospace; font-size: 12px;">-3.9 to +3.9</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; background: rgba(239, 68, 68, 0.06); border-radius: 4px;">
<span style="color: #EF4444; font-weight: 500;">Defensive</span>
<span style="color: #64748B; font-family: 'JetBrains Mono', monospace; font-size: 12px;">≤ -4.0</span>
</div>
</div>
<div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(71, 85, 105, 0.3);">
<div class="metric-title">BTC Gate</div>
<div style="margin-top: 10px; display: flex; align-items: center; color: {btc_color}; font-weight: 500; font-size: 14px;">{btc_dot}{btc_status}</div>
<div style="color: #64748B; font-size: 11px; margin-top: 6px; line-height: 1.4;">Required for Aggressive regime: BTC must trade above 200-day moving average</div>
</div>
</div>""", unsafe_allow_html=True)

    # ==========================================================================
    # EDUCATIONAL SECTION (Collapsible)
    # ==========================================================================
    with st.expander("📚 Learn More: Why These Indicators?"):
        st.markdown("""
**The Core Thesis**

Crypto markets are heavily influenced by global liquidity conditions. When there's abundant cheap money in the system, risk assets (including crypto) tend to perform well. When liquidity tightens, they struggle.

**The Five Forces We Track:**

1. **Fed Balance Sheet** — When the Fed expands its balance sheet, it injects liquidity into the financial system. More money in the system tends to flow into risk assets like crypto.

2. **Reverse Repo (RRP)** — Cash parked here is "on the sidelines." When it drains, that money often flows into markets looking for returns.

3. **High Yield Spreads** — The gap between junk bonds and Treasuries. When investors are willing to buy risky bonds (tight spreads), they're likely to buy crypto too.

4. **Dollar Index (DXY)** — A strong dollar tightens global financial conditions. Dollar weakness is typically bullish for crypto as it makes USD-denominated assets cheaper globally.

5. **Stablecoin Supply** — A proxy for capital sitting on crypto's sidelines. Growing stablecoin supply suggests capital ready to deploy into crypto.

**The Three Regimes:**

- 🚀 **Aggressive** — Multiple indicators are bullish AND Bitcoin is above its 200-day average. Historically associated with crypto strength.

- ⚖️ **Balanced** — Mixed signals. Some indicators bullish, some bearish. No clear directional bias.

- 🛡️ **Defensive** — Multiple indicators are bearish. Historically associated with crypto weakness.

**This is not financial advice.** This tool is for educational purposes only — a framework for understanding macro conditions, not a trading signal. Past correlations do not guarantee future results.
        """)

    # ==========================================================================
    # SETTINGS ROW - Display mode toggle
    # ==========================================================================
    st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
    settings_col1, settings_col2, settings_col3 = st.columns([1, 2, 1])
    with settings_col2:
        st.markdown("""
        <div style="text-align: center; padding: 12px 0; border-top: 1px solid rgba(71, 85, 105, 0.15); border-bottom: 1px solid rgba(71, 85, 105, 0.15);">
            <span style="font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 1px;">Display Mode</span>
        </div>
        """, unsafe_allow_html=True)
        toggle_col1, toggle_col2, toggle_col3 = st.columns([1, 2, 1])
        with toggle_col2:
            new_plain_english = st.toggle(
                "Plain English",
                value=st.session_state.plain_english,
                help="Switch between simple explanations and finance terminology",
                key="plain_english_toggle"
            )
            if new_plain_english != st.session_state.plain_english:
                st.session_state.plain_english = new_plain_english
                st.rerun()

    # ==========================================================================
    # FOOTER
    # ==========================================================================
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Feedback popover
    footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
    with footer_col2:
        st.markdown('<div style="text-align: center; margin-bottom: 16px;"></div>', unsafe_allow_html=True)
        with st.popover("💬 Share Feedback", use_container_width=True):
            render_feedback_form()

    st.markdown(f"""<div style="text-align: center; padding: 24px 0; color: #475569; font-size: 11px; margin-top: 8px;">
<div style="margin-bottom: 8px;">
<span style="color: #3B82F6; font-weight: 600; letter-spacing: 1px; font-size: 10px; text-transform: uppercase;">FlowState</span>
</div>
Built by <a href="https://www.linkedin.com/in/elijah-wilbanks/" target="_blank" style="color: #3B82F6; text-decoration: none; font-weight: 500;">Elijah Wilbanks</a>&nbsp;&nbsp;|&nbsp;&nbsp;Sources: FRED • CoinGecko • DefiLlama&nbsp;&nbsp;|&nbsp;&nbsp;Updated: {timestamp}<br>
<span style="color: #64748B; margin-top: 4px; display: inline-block;">For educational purposes only. Not financial advice. Past performance does not indicate future results.</span>
</div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
