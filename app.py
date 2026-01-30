"""
Crypto Liquidity Regime Dashboard
A local Streamlit app that classifies macro + crypto environment into risk regimes.
Redesigned for LinkedIn-shareable, educational presentation.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json

# Configure page
st.set_page_config(
    page_title="Liquidity Regime Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
    render_discord_cta,
    render_metric_card,
    render_section_header,
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
        "plain": "Conditions are favorable for crypto right now",
        "finance": "Liquidity conditions favor risk-on positioning",
    },
    "balanced": {
        "plain": "Mixed signals — be selective, don't go all-in",
        "finance": "Mixed signals suggest selective exposure",
    },
    "defensive": {
        "plain": "Warning signs suggest playing it safe",
        "finance": "Liquidity headwinds warrant caution",
    },
}

REGIME_POSTURES = {
    "aggressive": {
        "plain": "Good conditions for investing in crypto",
        "finance": "Full risk-on appropriate. Consider max exposure to quality assets.",
    },
    "balanced": {
        "plain": "Be picky about what you invest in",
        "finance": "Neutral posture. Maintain moderate exposure, be selective.",
    },
    "defensive": {
        "plain": "Consider reducing exposure and holding cash",
        "finance": "Risk-off posture. Reduce exposure, raise cash, avoid leverage.",
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
DISCORD_URL = "#"  # Placeholder - replace with actual Discord invite


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

    # Inject custom CSS
    inject_custom_css()

    # ==========================================================================
    # HEADER WITH PLAIN ENGLISH TOGGLE
    # ==========================================================================
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

    with header_col1:
        st.markdown("""
        <h1 style="margin: 0; padding: 16px 0 4px 0; font-size: 22px; font-weight: 700; color: #E2E8F0; letter-spacing: -0.5px;">
            Liquidity Regime Dashboard
        </h1>
        """, unsafe_allow_html=True)

    with header_col2:
        plain_english = st.toggle("Plain English", value=True, help="Switch between simple explanations and finance terminology")
        mode = "plain" if plain_english else "finance"

    with header_col3:
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            load_data(force_refresh=True)
            st.rerun()

    # ==========================================================================
    # CHECK FOR FRED API KEY
    # ==========================================================================
    if not has_fred_api_key():
        st.warning("""
        **FRED API Key Required** — Get a free key at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) and set it as `FRED_API_KEY` environment variable.
        """)

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
        delta = walcl.get("delta_4w")
        direction = "positive" if walcl_score.get("score", 0) > 0 else (
            "negative" if walcl_score.get("score", 0) < 0 else "neutral"
        )

        walcl_value = walcl.get("current")
        if walcl_value:
            walcl_value = walcl_value * 1e6

        render_metric_card(
            title=get_copy("walcl", mode, METRIC_TITLES),
            value=format_large_number(walcl_value),
            delta=format_percentage(delta, plain_english=plain_english) if delta else None,
            delta_direction=direction,
            weight=WEIGHTS["walcl"],
            info=METRIC_INFO.get("walcl"),
            why=get_copy("walcl", mode, METRIC_WHY),
        )

        if "walcl" in charts:
            chart = create_sparkline(charts["walcl"], height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # RRP Card
    with col2:
        rrp = metrics.get("rrp", {})
        rrp_score = scores["individual"].get("rrp", {})
        delta = rrp.get("delta_4w")
        direction = "positive" if rrp_score.get("score", 0) > 0 else (
            "negative" if rrp_score.get("score", 0) < 0 else "neutral"
        )

        rrp_value = rrp.get("current")
        if rrp_value:
            rrp_value = rrp_value * 1e9

        render_metric_card(
            title=get_copy("rrp", mode, METRIC_TITLES),
            value=format_large_number(rrp_value),
            delta=format_percentage(delta, plain_english=plain_english) if delta else None,
            delta_direction=direction,
            weight=WEIGHTS["rrp"],
            info=METRIC_INFO.get("rrp"),
            why=get_copy("rrp", mode, METRIC_WHY),
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
        )

        if "bamlh0a0hym2" in charts:
            chart = create_sparkline(charts["bamlh0a0hym2"], height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # ==========================================================================
    # INDICATOR CARDS - Row 2
    # ==========================================================================
    col1, col2, col3 = st.columns(3)

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
        )

        if "stablecoins" in charts:
            chart = create_sparkline(charts["stablecoins"], value_col="supply", height=70)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # BTC Gate Card
    with col3:
        btc = metrics.get("btc", {})
        current_price = btc.get("current_price")
        ma_200 = btc.get("ma_200")
        above = btc.get("above_200dma", False)
        distance = btc.get("distance_from_200dma")

        if plain_english:
            status = "Above trend ✓" if above else "Below trend ✗"
        else:
            status = "✅ Above 200 DMA" if above else "❌ Below 200 DMA"
        direction = "positive" if above else "negative"

        value_str = f"${current_price:,.0f}" if current_price else "N/A"

        render_metric_card(
            title=get_copy("btc_gate", mode, METRIC_TITLES),
            value=value_str,
            delta=f"{status}",
            delta_direction=direction,
            info=METRIC_INFO.get("btc_gate"),
            why=get_copy("btc_gate", mode, METRIC_WHY),
        )

        if "btc" in charts:
            chart = create_btc_chart(charts["btc"], ma_200=ma_200, height=140)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # ==========================================================================
    # DISCORD CTA
    # ==========================================================================
    render_discord_cta(discord_url=DISCORD_URL)

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
<tr style="background: rgba(129, 140, 248, 0.08);">
<td style="padding: 14px 12px; color: #E2E8F0; font-weight: 600; font-size: 13px;">Total Score</td>
<td style="text-align: center; padding: 14px 12px;"></td>
<td style="text-align: center; padding: 14px 12px;"></td>
<td style="text-align: center; padding: 14px 12px; color: #818CF8; font-weight: 700; font-size: 16px; font-family: 'JetBrains Mono', monospace;">{total_contrib:+.1f}</td>
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

- 🚀 **Aggressive** — Multiple indicators are bullish AND Bitcoin is above its 200-day average. Conditions favor risk-taking.

- ⚖️ **Balanced** — Mixed signals. Some indicators bullish, some bearish. Be selective with investments.

- 🛡️ **Defensive** — Multiple indicators are bearish. Consider reducing exposure and preserving capital.

**Not financial advice.** This is a framework for understanding macro conditions, not a trading signal.
        """)

    # ==========================================================================
    # FOOTER
    # ==========================================================================
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""<div style="text-align: center; padding: 28px 0; color: #475569; font-size: 11px; border-top: 1px solid rgba(71, 85, 105, 0.2); margin-top: 24px;">
Sources: FRED (Federal Reserve) • CoinGecko • DefiLlama&nbsp;&nbsp;|&nbsp;&nbsp;Auto-refresh: 4h&nbsp;&nbsp;|&nbsp;&nbsp;Updated: {timestamp}<br>
<span style="color: #64748B;">Not financial advice. For educational purposes only.</span>
</div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
