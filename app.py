"""
Crypto Liquidity Regime Dashboard
A local Streamlit app that classifies macro + crypto environment into risk regimes.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime

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
    render_regime_banner,
    render_metric_card,
    render_data_freshness,
    render_section_header,
    format_large_number,
    format_percentage,
)
from ui.charts import create_sparkline, create_score_gauge, create_btc_chart
from config import CACHE_TTL, REGIME_THRESHOLDS, WEIGHTS

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


def load_data(force_refresh: bool = False):
    """Load data with caching."""

    if force_refresh:
        CACHE.invalidate_all()

    # Check cache
    cached_data = CACHE.get("all_data")
    if cached_data:
        return cached_data

    # Fetch fresh data
    with st.spinner("Fetching latest data..."):
        data = fetch_all_data()
        CACHE.set("all_data", data, ttl=min(CACHE_TTL.values()))

    return data


def main():
    """Main app function."""

    # Inject custom CSS
    inject_custom_css()

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <h1 style="margin: 0; padding: 24px 0; font-size: 32px; font-weight: 800; color: #f3f4f6;">
            📊 Liquidity Regime Dashboard
        </h1>
        <p style="color: #9ca3af; margin-top: -16px; margin-bottom: 24px;">
            Macro-driven crypto risk regime classification
        </p>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            load_data(force_refresh=True)
            st.rerun()

    # About section - collapsible
    with st.expander("ℹ️ What is this? Why these indicators?"):
        st.markdown("""
**The Thesis**: Crypto markets are heavily influenced by global liquidity conditions. When there's abundant cheap money in the system, risk assets (including crypto) tend to perform well. When liquidity tightens, they struggle.

**What we're measuring**:
- **Fed Balance Sheet** — When the Fed expands its balance sheet, it injects liquidity into the financial system
- **Reverse Repo (RRP)** — Cash parked here is "on the sidelines." When it drains, that money often flows into markets
- **High Yield Spreads** — The gap between junk bonds and Treasuries. Tight spreads = investors are risk-seeking
- **Dollar Index (DXY)** — A strong dollar tightens global financial conditions; weakness is typically bullish for crypto
- **Stablecoin Supply** — A proxy for capital sitting on crypto's sidelines, ready to deploy

**The Regimes**:
- 🚀 **Aggressive** — Liquidity tailwinds favor risk-on positioning (requires BTC above 200 DMA as confirmation)
- ⚖️ **Balanced** — Mixed signals; be selective, avoid overexposure
- 🛡️ **Defensive** — Liquidity headwinds suggest caution and capital preservation

**Not financial advice.** This is a framework for understanding macro conditions, not a trading signal.
        """)

    # Check for FRED API key
    if not has_fred_api_key():
        st.warning("""
        ⚠️ **FRED API Key Required**

        To get Fed Balance Sheet, Reverse Repo, HY Spreads, and DXY data, you need a free FRED API key:

        1. Get your free key at: https://fred.stlouisfed.org/docs/api/api_key.html
        2. Set it as an environment variable: `set FRED_API_KEY=your_key_here` (Windows) or `export FRED_API_KEY=your_key_here` (Mac/Linux)
        3. Restart the app

        Dashboard will run with BTC and Stablecoin data only until FRED key is configured.
        """)

    # Load and process data
    try:
        data = load_data()
        metrics = calculate_metrics(data)
        scores = calculate_scores(metrics)
        regime, state, regime_info = determine_regime(scores, state_file=STATE_FILE)
        explanation = generate_explanation(regime, scores, metrics, regime_info)
        charts = get_chart_data(data)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure you have an internet connection and try refreshing.")
        return

    # Main regime banner
    render_regime_banner(explanation, regime_info, scores)

    # Score gauge
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    gauge = create_score_gauge(
        scores["total"],
        min_val=-6.5,
        max_val=6.5,
        thresholds={"defensive": REGIME_THRESHOLDS["defensive"], "aggressive": REGIME_THRESHOLDS["aggressive"]}
    )
    st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar": False})

    # Metric cards
    render_section_header("Liquidity Indicators")

    col1, col2, col3 = st.columns(3)

    # WALCL Card
    with col1:
        walcl = metrics.get("walcl", {})
        walcl_score = scores["individual"].get("walcl", {})
        delta = walcl.get("delta_4w")
        direction = "positive" if walcl_score.get("score", 0) > 0 else (
            "negative" if walcl_score.get("score", 0) < 0 else "neutral"
        )

        # WALCL is reported in millions
        walcl_value = walcl.get("current")
        if walcl_value:
            walcl_value = walcl_value * 1e6  # Convert millions to dollars

        render_metric_card(
            title="Fed Balance Sheet (WALCL)",
            value=format_large_number(walcl_value),
            delta=format_percentage(delta) if delta else None,
            delta_direction=direction,
            reason=walcl_score.get("reason"),
            weight=WEIGHTS["walcl"],
            info=METRIC_INFO.get("walcl"),
        )

        if "walcl" in charts:
            chart = create_sparkline(charts["walcl"])
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # RRP Card
    with col2:
        rrp = metrics.get("rrp", {})
        rrp_score = scores["individual"].get("rrp", {})
        delta = rrp.get("delta_4w")
        # RRP is inverted - decrease is bullish
        direction = "positive" if rrp_score.get("score", 0) > 0 else (
            "negative" if rrp_score.get("score", 0) < 0 else "neutral"
        )

        # RRP is reported in billions
        rrp_value = rrp.get("current")
        if rrp_value:
            rrp_value = rrp_value * 1e9  # Convert billions to dollars

        render_metric_card(
            title="Reverse Repo (RRP)",
            value=format_large_number(rrp_value),
            delta=format_percentage(delta) if delta else None,
            delta_direction=direction,
            reason=rrp_score.get("reason"),
            weight=WEIGHTS["rrp"],
            info=METRIC_INFO.get("rrp"),
        )

        if "rrpontsyd" in charts:
            chart = create_sparkline(charts["rrpontsyd"])
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # HY Spread Card
    with col3:
        hy = metrics.get("hy_spread", {})
        hy_score = scores["individual"].get("hy_spread", {})
        delta = hy.get("delta_4w")
        # HY spread tightening is bullish
        direction = "positive" if hy_score.get("score", 0) > 0 else (
            "negative" if hy_score.get("score", 0) < 0 else "neutral"
        )

        # HY spread is reported as percentage (2.72 = 2.72% = 272 bps)
        current = hy.get("current")
        value_str = f"{current*100:.0f} bps" if current else "N/A"

        render_metric_card(
            title="HY Credit Spreads",
            value=value_str,
            delta=format_percentage(delta) if delta else None,
            delta_direction=direction,
            reason=hy_score.get("reason"),
            weight=WEIGHTS["hy_spread"],
            info=METRIC_INFO.get("hy_spread"),
        )

        if "bamlh0a0hym2" in charts:
            chart = create_sparkline(charts["bamlh0a0hym2"])
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # Second row
    col1, col2, col3 = st.columns(3)

    # DXY Card
    with col1:
        dxy = metrics.get("dxy", {})
        dxy_score = scores["individual"].get("dxy", {})
        delta = dxy.get("delta_4w")
        # DXY weakening is bullish for crypto
        direction = "positive" if dxy_score.get("score", 0) > 0 else (
            "negative" if dxy_score.get("score", 0) < 0 else "neutral"
        )

        current = dxy.get("current")
        value_str = f"{current:.2f}" if current else "N/A"

        render_metric_card(
            title="Dollar Index (DXY)",
            value=value_str,
            delta=format_percentage(delta) if delta else None,
            delta_direction=direction,
            reason=dxy_score.get("reason"),
            weight=WEIGHTS["dxy"],
            info=METRIC_INFO.get("dxy"),
        )

        if "dtwexbgs" in charts:
            chart = create_sparkline(charts["dtwexbgs"])
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
            title="Stablecoin Supply",
            value=format_large_number(stable.get("current")),
            delta=format_percentage(delta) if delta else None,
            delta_direction=direction,
            reason=stable_score.get("reason"),
            weight=WEIGHTS["stablecoin"],
            info=METRIC_INFO.get("stablecoin"),
        )

        if "stablecoins" in charts:
            chart = create_sparkline(charts["stablecoins"], value_col="supply")
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # BTC Gate Card
    with col3:
        btc = metrics.get("btc", {})
        current_price = btc.get("current_price")
        ma_200 = btc.get("ma_200")
        above = btc.get("above_200dma", False)
        distance = btc.get("distance_from_200dma")

        status = "✅ Above" if above else "❌ Below"
        direction = "positive" if above else "negative"

        value_str = f"${current_price:,.0f}" if current_price else "N/A"

        render_metric_card(
            title="BTC vs 200 DMA (Gate)",
            value=value_str,
            delta=f"{status} ({format_percentage(distance)})" if distance else status,
            delta_direction=direction,
            reason=f"200 DMA: ${ma_200:,.0f}" if ma_200 else None,
            info=METRIC_INFO.get("btc_gate"),
        )

        if "btc" in charts:
            chart = create_btc_chart(charts["btc"], ma_200=ma_200, height=120)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # Score breakdown
    render_section_header("Score Breakdown")

    breakdown_col1, breakdown_col2 = st.columns([2, 1])

    with breakdown_col1:
        # Build the entire table as a single HTML string
        total_contrib = 0
        rows_html = ""

        for name, data in scores["individual"].items():
            score = data.get("score", 0)
            weight = data.get("weight", 1)
            weighted = data.get("weighted", 0)
            total_contrib += weighted

            if score > 0:
                signal_color = "#10B981"
                signal_icon = "🟢"
            elif score < 0:
                signal_color = "#EF4444"
                signal_icon = "🔴"
            else:
                signal_color = "#6B7280"
                signal_icon = "⚪"

            # Get metric info for tooltip
            info = METRIC_INFO.get(name, {})
            display_name = info.get("name", name.upper().replace("_", " "))
            tooltip_text = f"{info.get('desc', '')}&#10;&#10;🟢 Bullish: {info.get('bullish', 'N/A')}&#10;🔴 Bearish: {info.get('bearish', 'N/A')}"

            rows_html += f'''<tr style="border-bottom: 1px solid rgba(55, 65, 81, 0.3);">
<td style="padding: 12px 8px; color: #f3f4f6;">
<span class="metric-name-with-info">{display_name}
<span class="info-icon" title="{tooltip_text}">ⓘ</span>
</span>
</td>
<td style="text-align: center; padding: 12px 8px;">{signal_icon} <span style="color: {signal_color};">{score:+d}</span></td>
<td style="text-align: center; padding: 12px 8px; color: #9ca3af;">{weight}x</td>
<td style="text-align: center; padding: 12px 8px; color: {signal_color}; font-weight: 600;">{weighted:+.1f}</td>
</tr>'''

        table_html = f'''<div class="metric-card">
<table style="width: 100%; border-collapse: collapse;">
<tr style="border-bottom: 1px solid rgba(99, 102, 241, 0.2);">
<th style="text-align: left; padding: 12px 8px; color: #9ca3af; font-size: 12px; font-weight: 600;">METRIC</th>
<th style="text-align: center; padding: 12px 8px; color: #9ca3af; font-size: 12px; font-weight: 600;">SIGNAL</th>
<th style="text-align: center; padding: 12px 8px; color: #9ca3af; font-size: 12px; font-weight: 600;">WEIGHT</th>
<th style="text-align: center; padding: 12px 8px; color: #9ca3af; font-size: 12px; font-weight: 600;">CONTRIBUTION</th>
</tr>
{rows_html}
<tr style="background: rgba(99, 102, 241, 0.1);">
<td style="padding: 12px 8px; color: #f3f4f6; font-weight: 700;">TOTAL</td>
<td style="text-align: center; padding: 12px 8px;"></td>
<td style="text-align: center; padding: 12px 8px;"></td>
<td style="text-align: center; padding: 12px 8px; color: #6366f1; font-weight: 700; font-size: 18px;">{total_contrib:+.1f}</td>
</tr>
</table>
</div>'''
        st.markdown(table_html, unsafe_allow_html=True)

    with breakdown_col2:
        btc_color = '#10B981' if scores.get('btc_above_200dma') else '#EF4444'
        btc_status = '✅ Passed' if scores.get('btc_above_200dma') else '❌ Failed'
        st.markdown(f"""<div class="metric-card">
<div class="metric-title">Thresholds</div>
<div style="margin-top: 16px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
<span style="color: #10B981;">🚀 Aggressive</span>
<span style="color: #9ca3af;">≥ +4.0 + BTC Gate</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
<span style="color: #F59E0B;">⚖️ Balanced</span>
<span style="color: #9ca3af;">-3.9 to +3.9</span>
</div>
<div style="display: flex; justify-content: space-between;">
<span style="color: #EF4444;">🛡️ Defensive</span>
<span style="color: #9ca3af;">≤ -4.0</span>
</div>
</div>
<div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(99, 102, 241, 0.2);">
<div class="metric-title">BTC Gate Status</div>
<div style="margin-top: 8px; color: {btc_color}; font-weight: 600;">{btc_status}</div>
<div style="color: #6B7280; font-size: 12px; margin-top: 4px;">BTC must be above 200 DMA for Aggressive regime</div>
</div>
</div>""", unsafe_allow_html=True)

    # Data freshness
    cache_stats = CACHE.get_stats()
    # render_data_freshness(cache_stats)

    # Footer
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""<div style="text-align: center; padding: 32px 0; color: #6B7280; font-size: 12px;">
Data sources: FRED (Federal Reserve) • CoinGecko • DefiLlama<br>
Auto-refresh: 4 hours • Last updated: {timestamp}
</div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
