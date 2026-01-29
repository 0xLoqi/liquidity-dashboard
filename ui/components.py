"""
Streamlit UI components with polished styling
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from config import REGIME_COLORS, REGIME_ICONS


def inject_custom_css():
    """Inject custom CSS for polished styling."""
    st.markdown("""
    <style>
        /* Dark theme base */
        .stApp {
            background: linear-gradient(180deg, #0f0f0f 0%, #1a1a2e 100%);
        }

        /* Hide default header */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, rgba(30, 30, 46, 0.8) 0%, rgba(20, 20, 35, 0.9) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 20px;
            margin: 8px 0;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            border-color: rgba(99, 102, 241, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
        }

        .metric-card.bullish {
            border-color: rgba(16, 185, 129, 0.4);
        }

        .metric-card.bearish {
            border-color: rgba(239, 68, 68, 0.4);
        }

        .metric-title {
            font-size: 12px;
            font-weight: 600;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #f3f4f6;
            margin-bottom: 4px;
        }

        .metric-delta {
            font-size: 14px;
            font-weight: 500;
            padding: 4px 10px;
            border-radius: 20px;
            display: inline-block;
        }

        .metric-delta.positive {
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
        }

        .metric-delta.negative {
            background: rgba(239, 68, 68, 0.15);
            color: #EF4444;
        }

        .metric-delta.neutral {
            background: rgba(107, 114, 128, 0.15);
            color: #9ca3af;
        }

        /* Regime banner */
        .regime-banner {
            padding: 32px;
            border-radius: 20px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }

        .regime-banner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 50%);
            pointer-events: none;
        }

        .regime-banner.aggressive {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.05) 100%);
            border: 2px solid rgba(16, 185, 129, 0.4);
        }

        .regime-banner.balanced {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%);
            border: 2px solid rgba(245, 158, 11, 0.4);
        }

        .regime-banner.defensive {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.05) 100%);
            border: 2px solid rgba(239, 68, 68, 0.4);
        }

        .regime-title {
            font-size: 14px;
            font-weight: 600;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        .regime-name {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .regime-name.aggressive { color: #10B981; }
        .regime-name.balanced { color: #F59E0B; }
        .regime-name.defensive { color: #EF4444; }

        .regime-body {
            font-size: 16px;
            color: #d1d5db;
            line-height: 1.6;
            max-width: 800px;
        }

        .regime-posture {
            font-size: 18px;
            font-weight: 600;
            color: #f3f4f6;
            margin-top: 16px;
            padding: 12px 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            display: inline-block;
        }

        /* Score indicator */
        .score-badge {
            position: absolute;
            top: 24px;
            right: 24px;
            background: rgba(0,0,0,0.3);
            padding: 12px 20px;
            border-radius: 12px;
            text-align: center;
        }

        .score-label {
            font-size: 11px;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .score-value {
            font-size: 32px;
            font-weight: 700;
            color: #f3f4f6;
        }

        /* Pending flip warning */
        .pending-flip {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 16px;
            font-size: 14px;
            color: #F59E0B;
        }

        /* Data freshness */
        .freshness-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .freshness-badge.fresh {
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
        }

        .freshness-badge.stale {
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
        }

        .freshness-badge.old {
            background: rgba(239, 68, 68, 0.15);
            color: #EF4444;
        }

        /* Section headers */
        .section-header {
            font-size: 20px;
            font-weight: 700;
            color: #f3f4f6;
            margin: 32px 0 16px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        }

        /* Warning banner */
        .warning-banner {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            margin: 16px 0;
            font-size: 14px;
            color: #EF4444;
        }

        /* Refresh button */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            border: none;
            border-radius: 10px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }

        /* Plotly chart styling */
        .js-plotly-plot .plotly {
            border-radius: 12px;
        }

        /* Info icon and tooltip */
        .metric-name-with-info {
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .info-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            font-size: 12px;
            color: #6B7280;
            cursor: help;
            transition: color 0.2s ease;
            position: relative;
        }

        .info-icon:hover {
            color: #6366f1;
        }

        .info-icon::after {
            content: attr(title);
            position: absolute;
            left: 50%;
            bottom: calc(100% + 8px);
            transform: translateX(-50%);
            background: #1e1e2e;
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 12px;
            line-height: 1.5;
            color: #d1d5db;
            white-space: pre-line;
            width: 280px;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s ease, visibility 0.2s ease;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            pointer-events: none;
        }

        .info-icon:hover::after {
            opacity: 1;
            visibility: visible;
        }
    </style>
    """, unsafe_allow_html=True)


def render_regime_banner(
    explanation: Dict[str, str],
    regime_info: Dict[str, Any],
    scores: Dict[str, Any],
):
    """Render the main regime banner."""
    regime = regime_info.get("regime", "balanced")
    icon = REGIME_ICONS.get(regime, "⚖️")
    total_score = scores.get("total", 0)

    st.markdown(f"""<div class="regime-banner {regime}">
<div class="score-badge">
<div class="score-label">Score</div>
<div class="score-value">{total_score:+.1f}</div>
</div>
<div class="regime-title">Current Regime</div>
<div class="regime-name {regime}">
<span>{icon}</span>
<span>{explanation.get('headline', regime.upper())}</span>
</div>
<div class="regime-body">{explanation.get('body', '')}</div>
<div class="regime-posture">{explanation.get('posture', '')}</div>
{_render_pending_flip(regime_info)}
</div>""", unsafe_allow_html=True)

    # Warnings
    warnings = explanation.get("warnings", "")
    if warnings:
        st.markdown(f"""<div class="warning-banner">⚠️ {warnings}</div>""", unsafe_allow_html=True)


def _render_pending_flip(regime_info: Dict[str, Any]) -> str:
    """Render pending flip warning if applicable."""
    if not regime_info.get("pending_flip"):
        return ""

    proposed = regime_info.get("proposed_regime", "").upper()
    days = regime_info.get("days_until_flip", 0)
    consecutive = regime_info.get("consecutive_days", 0)

    return f"""
    <div class="pending-flip">
        ⏳ Potential flip to {proposed} — {consecutive} day(s) consecutive signal,
        {days} more day(s) needed to confirm.
    </div>
    """


def render_metric_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_direction: str = "neutral",  # "positive", "negative", "neutral"
    reason: Optional[str] = None,
    weight: Optional[float] = None,
    chart: Optional[Any] = None,
    info: Optional[Dict[str, str]] = None,
):
    """Render a metric card with optional chart and info tooltip."""

    card_class = ""
    if delta_direction == "positive":
        card_class = "bullish"
    elif delta_direction == "negative":
        card_class = "bearish"

    delta_html = ""
    if delta:
        delta_html = f'<span class="metric-delta {delta_direction}">{delta}</span>'

    weight_html = ""
    if weight:
        weight_html = f'<span style="color: #6B7280; font-size: 11px; margin-left: 8px;">({weight}x)</span>'

    reason_html = ""
    if reason:
        reason_html = f'<div style="color: #9ca3af; font-size: 13px; margin-top: 8px;">{reason}</div>'

    info_html = ""
    if info:
        tooltip_text = f"{info.get('desc', '')}&#10;&#10;🟢 Bullish: {info.get('bullish', 'N/A')}&#10;🔴 Bearish: {info.get('bearish', 'N/A')}"
        info_html = f'<span class="info-icon" title="{tooltip_text}">ⓘ</span>'

    st.markdown(f"""<div class="metric-card {card_class}">
<div class="metric-title"><span class="metric-name-with-info">{title}{info_html}</span>{weight_html}</div>
<div class="metric-value">{value}</div>
{delta_html}
{reason_html}
</div>""", unsafe_allow_html=True)

    if chart is not None:
        st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})


def render_data_freshness(cache_stats: Dict[str, Any]):
    """Render data freshness indicators."""
    entries = cache_stats.get("entries", {})

    st.markdown('<div class="section-header">Data Sources</div>', unsafe_allow_html=True)

    cols = st.columns(4)

    sources = [
        ("FRED (Fed/Treasury)", "fred_data"),
        ("CoinGecko (BTC)", "coingecko_data"),
        ("DefiLlama (Stables)", "defillama_data"),
    ]

    for i, (name, key) in enumerate(sources):
        with cols[i]:
            entry = entries.get(key, {})
            age = entry.get("age_human", "Unknown")
            expires = entry.get("expires_in_human", "Unknown")

            # Determine freshness class
            age_seconds = entry.get("age_seconds", float("inf"))
            if age_seconds < 3600:
                freshness = "fresh"
                status = "🟢"
            elif age_seconds < 7200:
                freshness = "stale"
                status = "🟡"
            else:
                freshness = "old"
                status = "🔴"

            st.markdown(f"""<div class="metric-card">
<div class="metric-title">{name}</div>
<div class="freshness-badge {freshness}">{status} Updated {age} ago</div>
</div>""", unsafe_allow_html=True)


def render_section_header(title: str):
    """Render a section header."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def format_large_number(value: float) -> str:
    """Format large numbers for display."""
    if value is None:
        return "N/A"

    if abs(value) >= 1e12:
        return f"${value/1e12:.2f}T"
    elif abs(value) >= 1e9:
        return f"${value/1e9:.1f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"${value/1e3:.1f}K"
    else:
        return f"${value:.2f}"


def format_percentage(value: float, include_sign: bool = True) -> str:
    """Format percentage for display."""
    if value is None:
        return "N/A"

    if include_sign:
        return f"{value*100:+.1f}%"
    else:
        return f"{value*100:.1f}%"
