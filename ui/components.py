"""
Streamlit UI components with polished styling
Redesigned for LinkedIn-shareable, educational presentation
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from config import REGIME_COLORS, REGIME_ICONS


def inject_custom_css():
    """Inject custom CSS for refined terminal aesthetic with animations."""
    st.markdown("""
    <style>
        /* Import clean system fonts */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap');

        /* Dark theme base - deep slate */
        .stApp {
            background: #0F172A;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* Hide default header */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* ===== PULSING ANIMATIONS ===== */
        @keyframes pulse-aggressive {
            0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.6); }
            50% { box-shadow: 0 0 0 24px rgba(34, 197, 94, 0); }
        }

        @keyframes pulse-balanced {
            0%, 100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.6); }
            50% { box-shadow: 0 0 0 24px rgba(251, 191, 36, 0); }
        }

        @keyframes pulse-defensive {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
            50% { box-shadow: 0 0 0 24px rgba(239, 68, 68, 0); }
        }

        @keyframes signal-pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.15); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ===== HERO SECTION ===== */
        .hero-section {
            text-align: center;
            padding: 48px 24px 36px;
            border-radius: 16px;
            margin-bottom: 24px;
            position: relative;
            animation: fadeInUp 0.5s ease-out;
        }

        .hero-section.aggressive {
            background: linear-gradient(180deg, rgba(34, 197, 94, 0.08) 0%, rgba(34, 197, 94, 0.02) 50%, transparent 100%);
            border: 1px solid rgba(34, 197, 94, 0.2);
        }

        .hero-section.balanced {
            background: linear-gradient(180deg, rgba(251, 191, 36, 0.08) 0%, rgba(251, 191, 36, 0.02) 50%, transparent 100%);
            border: 1px solid rgba(251, 191, 36, 0.2);
        }

        .hero-section.defensive {
            background: linear-gradient(180deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.02) 50%, transparent 100%);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .regime-indicator {
            width: 88px;
            height: 88px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            margin: 0 auto 20px;
        }

        .regime-indicator.aggressive {
            background: rgba(34, 197, 94, 0.15);
            border: 3px solid #22C55E;
            animation: pulse-aggressive 2s ease-in-out infinite;
        }

        .regime-indicator.balanced {
            background: rgba(251, 191, 36, 0.15);
            border: 3px solid #FBBF24;
            animation: pulse-balanced 2.5s ease-in-out infinite;
        }

        .regime-indicator.defensive {
            background: rgba(239, 68, 68, 0.15);
            border: 3px solid #EF4444;
            animation: pulse-defensive 1.5s ease-in-out infinite;
        }

        .hero-regime-name {
            font-size: 52px;
            font-weight: 800;
            letter-spacing: -1.5px;
            margin: 8px 0;
            line-height: 1.1;
        }

        .hero-regime-name.aggressive { color: #22C55E; }
        .hero-regime-name.balanced { color: #FBBF24; }
        .hero-regime-name.defensive { color: #EF4444; }

        .hero-score {
            font-size: 20px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            color: #94A3B8;
            margin-bottom: 12px;
        }

        .hero-tagline {
            font-size: 18px;
            color: #CBD5E1;
            margin: 0 auto 20px;
            max-width: 500px;
            line-height: 1.5;
        }

        .hero-posture {
            display: inline-block;
            padding: 12px 20px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(71, 85, 105, 0.4);
            border-radius: 8px;
            font-size: 15px;
            color: #E2E8F0;
            font-weight: 500;
        }

        .hero-duration {
            margin-top: 16px;
            font-size: 13px;
            color: #64748B;
        }

        /* ===== FIVE FORCES STRIP ===== */
        .forces-strip {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            padding: 20px 16px;
            margin-bottom: 20px;
            background: rgba(30, 41, 59, 0.3);
            border-radius: 12px;
            border: 1px solid rgba(71, 85, 105, 0.2);
        }

        .force-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(71, 85, 105, 0.3);
            border-radius: 24px;
            font-size: 13px;
            color: #E2E8F0;
            font-weight: 500;
            transition: border-color 0.2s;
        }

        .force-pill:hover {
            border-color: rgba(129, 140, 248, 0.4);
        }

        .signal-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }

        .signal-dot.bullish {
            background: #22C55E;
            animation: signal-pulse 2s ease-in-out infinite;
        }

        .signal-dot.bearish {
            background: #EF4444;
            animation: signal-pulse 2s ease-in-out infinite;
        }

        .signal-dot.neutral {
            background: #64748B;
            opacity: 0.6;
        }

        /* ===== METRIC CARDS ===== */
        .metric-card {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(71, 85, 105, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin: 8px 0;
            transition: border-color 0.2s ease;
            animation: fadeInUp 0.4s ease-out;
        }

        .metric-card:hover {
            border-color: rgba(129, 140, 248, 0.4);
        }

        .metric-card.bullish {
            border-left: 3px solid #22C55E;
        }

        .metric-card.bearish {
            border-left: 3px solid #EF4444;
        }

        .metric-title {
            font-size: 11px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .metric-why {
            font-size: 13px;
            color: #94A3B8;
            margin-bottom: 12px;
            font-style: italic;
        }

        .metric-value {
            font-size: 26px;
            font-weight: 600;
            color: #E2E8F0;
            margin-bottom: 6px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.5px;
        }

        .metric-delta {
            font-size: 13px;
            font-weight: 500;
            padding: 3px 10px;
            border-radius: 4px;
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
        }

        .metric-delta.positive {
            background: rgba(34, 197, 94, 0.12);
            color: #22C55E;
        }

        .metric-delta.negative {
            background: rgba(239, 68, 68, 0.12);
            color: #EF4444;
        }

        .metric-delta.neutral {
            background: rgba(100, 116, 139, 0.12);
            color: #94A3B8;
        }

        /* ===== DISCORD CTA ===== */
        .discord-cta {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 20px 24px;
            background: linear-gradient(135deg, rgba(88, 101, 242, 0.1) 0%, rgba(88, 101, 242, 0.05) 100%);
            border: 1px solid rgba(88, 101, 242, 0.25);
            border-radius: 12px;
            margin: 24px 0;
        }

        .discord-cta-icon {
            font-size: 32px;
        }

        .discord-cta-text {
            flex: 1;
        }

        .discord-cta-text h4 {
            margin: 0 0 4px 0;
            font-size: 16px;
            font-weight: 600;
            color: #E2E8F0;
        }

        .discord-cta-text p {
            margin: 0;
            font-size: 13px;
            color: #94A3B8;
        }

        .discord-cta-button {
            padding: 10px 20px;
            background: #5865F2;
            border: none;
            border-radius: 6px;
            color: white;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            text-decoration: none;
            transition: background 0.2s;
        }

        .discord-cta-button:hover {
            background: #4752C4;
        }

        /* ===== SECTION HEADERS ===== */
        .section-header {
            font-size: 13px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 28px 0 14px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
        }

        /* ===== TOGGLE STYLING ===== */
        .toggle-container {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #94A3B8;
        }

        /* ===== WARNING BANNER ===== */
        .warning-banner {
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 8px;
            padding: 14px 18px;
            margin: 14px 0;
            font-size: 13px;
            color: #EF4444;
        }

        /* ===== PENDING FLIP ===== */
        .pending-flip {
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.25);
            border-radius: 6px;
            padding: 10px 14px;
            margin-top: 14px;
            font-size: 13px;
            color: #FBBF24;
        }

        /* ===== REFRESH BUTTON ===== */
        .stButton > button {
            background: rgba(129, 140, 248, 0.15);
            border: 1px solid rgba(129, 140, 248, 0.3);
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: 500;
            color: #818CF8;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: rgba(129, 140, 248, 0.25);
            border-color: rgba(129, 140, 248, 0.5);
        }

        /* Chart containers - tighter spacing */
        [data-testid="stPlotlyChart"] {
            margin-top: 4px;
        }

        /* Info icon and tooltip */
        .metric-name-with-info {
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .info-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            font-size: 11px;
            color: #475569;
            cursor: help;
            transition: color 0.2s ease;
            position: relative;
        }

        .info-icon:hover {
            color: #818CF8;
        }

        .info-icon::after {
            content: attr(title);
            position: absolute;
            left: 50%;
            bottom: calc(100% + 8px);
            transform: translateX(-50%);
            background: #1E293B;
            border: 1px solid rgba(71, 85, 105, 0.4);
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 11px;
            line-height: 1.5;
            color: #94A3B8;
            white-space: pre-line;
            width: 260px;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.15s ease, visibility 0.15s ease;
            z-index: 1000;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            pointer-events: none;
        }

        .info-icon:hover::after {
            opacity: 1;
            visibility: visible;
        }

        /* Table refinements */
        table {
            font-size: 13px;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 14px !important;
            color: #94A3B8 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_regime_hero(
    regime: str,
    score: float,
    tagline: str,
    posture: str,
    days_in_regime: int = 0,
    regime_start_date: str = "",
):
    """Render the hero section with prominent pulsing regime indicator."""
    icon = REGIME_ICONS.get(regime, "⚖️")

    duration_html = ""
    if days_in_regime > 0:
        duration_html = f'<div class="hero-duration">In this regime for <strong>{days_in_regime} days</strong>{f" (since {regime_start_date})" if regime_start_date else ""}</div>'

    st.markdown(f"""
    <div class="hero-section {regime}">
        <div class="regime-indicator {regime}">
            <span>{icon}</span>
        </div>
        <div class="hero-regime-name {regime}">{regime.upper()}</div>
        <div class="hero-score">Score: {score:+.1f}</div>
        <div class="hero-tagline">{tagline}</div>
        <div class="hero-posture">{posture}</div>
        {duration_html}
    </div>
    """, unsafe_allow_html=True)


def render_five_forces_strip(scores: Dict[str, Any], plain_english: bool = True):
    """Render the Five Forces of Liquidity summary strip."""

    # Define force names for both modes
    forces = [
        {
            "key": "walcl",
            "name_plain": "Fed Printing",
            "name_finance": "Fed Balance Sheet",
        },
        {
            "key": "rrp",
            "name_plain": "Sideline Cash",
            "name_finance": "Reverse Repo",
        },
        {
            "key": "hy_spread",
            "name_plain": "Risk Appetite",
            "name_finance": "Credit Spreads",
        },
        {
            "key": "dxy",
            "name_plain": "Dollar Strength",
            "name_finance": "Dollar Index",
        },
        {
            "key": "stablecoin",
            "name_plain": "Crypto Dry Powder",
            "name_finance": "Stablecoin Supply",
        },
    ]

    pills_html = ""
    for force in forces:
        name = force["name_plain"] if plain_english else force["name_finance"]
        individual = scores.get("individual", {}).get(force["key"], {})
        signal = individual.get("score", 0)

        if signal > 0:
            dot_class = "bullish"
        elif signal < 0:
            dot_class = "bearish"
        else:
            dot_class = "neutral"

        pills_html += f'<div class="force-pill"><span class="signal-dot {dot_class}"></span>{name}</div>'

    st.markdown(f"""
    <div class="forces-strip">
        {pills_html}
    </div>
    """, unsafe_allow_html=True)


def render_discord_cta(discord_url: str = "#"):
    """Render the Discord call-to-action card."""
    st.markdown(f"""
    <div class="discord-cta">
        <div class="discord-cta-icon">🔔</div>
        <div class="discord-cta-text">
            <h4>Get Daily Regime Alerts</h4>
            <p>Join our Discord for automated updates when conditions change</p>
        </div>
        <a href="{discord_url}" class="discord-cta-button" target="_blank">Join Discord</a>
    </div>
    """, unsafe_allow_html=True)


def render_regime_banner(
    explanation: Dict[str, str],
    regime_info: Dict[str, Any],
    scores: Dict[str, Any],
):
    """Render the main regime banner (legacy - use render_regime_hero instead)."""
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
    delta_direction: str = "neutral",
    reason: Optional[str] = None,
    weight: Optional[float] = None,
    chart: Optional[Any] = None,
    info: Optional[Dict[str, str]] = None,
    why: Optional[str] = None,
):
    """Render a metric card with optional chart, info tooltip, and 'why it matters' micro-copy."""

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
        weight_html = f'<span style="color: #475569; font-size: 10px; margin-left: 8px;">({weight}x weight)</span>'

    reason_html = ""
    if reason:
        reason_html = f'<div style="color: #64748B; font-size: 12px; margin-top: 8px;">{reason}</div>'

    why_html = ""
    if why:
        why_html = f'<div class="metric-why">{why}</div>'

    info_html = ""
    if info:
        tooltip_text = f"{info.get('desc', '')}&#10;&#10;Bullish: {info.get('bullish', 'N/A')}&#10;Bearish: {info.get('bearish', 'N/A')}"
        info_html = f'<span class="info-icon" title="{tooltip_text}">?</span>'

    st.markdown(f"""<div class="metric-card {card_class}">
<div class="metric-title"><span class="metric-name-with-info">{title}{info_html}</span>{weight_html}</div>
{why_html}
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


def format_percentage(value: float, include_sign: bool = True, plain_english: bool = False) -> str:
    """Format percentage for display."""
    if value is None:
        return "N/A"

    pct = value * 100
    if plain_english:
        direction = "up" if pct > 0 else "down"
        return f"{direction} {abs(pct):.1f}% this month"
    elif include_sign:
        return f"{pct:+.1f}%"
    else:
        return f"{pct:.1f}%"
