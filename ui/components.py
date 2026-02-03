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
        /* Import distinctive fonts - Outfit for headers, JetBrains Mono for data */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* CSS Variables for FlowState brand */
        :root {
            --fs-blue: #3B82F6;
            --fs-blue-light: #60A5FA;
            --fs-blue-dark: #2563EB;
            --fs-green: #22C55E;
            --fs-amber: #FBBF24;
            --fs-red: #EF4444;
            --fs-slate-900: #0F172A;
            --fs-slate-800: #1E293B;
            --fs-slate-700: #334155;
            --fs-slate-600: #475569;
            --fs-slate-500: #64748B;
            --fs-slate-400: #94A3B8;
            --fs-slate-300: #CBD5E1;
            --fs-slate-200: #E2E8F0;
        }

        /* Dark theme base - deep slate */
        .stApp {
            background: var(--fs-slate-900);
            font-family: 'Outfit', system-ui, -apple-system, sans-serif;
        }

        /* Hide default header */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* ===== WAVE ANIMATION FOR HERO ===== */
        @keyframes wave-flow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes wave-drift {
            0%, 100% { transform: translateX(0) translateY(0); }
            25% { transform: translateX(5px) translateY(-3px); }
            50% { transform: translateX(0) translateY(-5px); }
            75% { transform: translateX(-5px) translateY(-3px); }
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

        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }

        /* ===== HERO SECTION WITH WAVE EFFECT ===== */
        .hero-section {
            text-align: center;
            padding: 56px 24px 44px;
            border-radius: 20px;
            margin-bottom: 28px;
            position: relative;
            animation: fadeInUp 0.5s ease-out;
            overflow: hidden;
        }

        /* Animated wave background overlay */
        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            opacity: 0.4;
            background:
                radial-gradient(ellipse 80% 50% at 20% 40%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse 60% 40% at 80% 60%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
            animation: wave-drift 8s ease-in-out infinite;
            pointer-events: none;
        }

        /* Subtle wave pattern */
        .hero-section::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,60 C200,100 400,20 600,60 C800,100 1000,20 1200,60 L1200,120 L0,120 Z' fill='rgba(15,23,42,0.3)'/%3E%3C/svg%3E");
            background-size: 1200px 100%;
            animation: wave-flow 15s ease-in-out infinite;
            pointer-events: none;
        }

        .hero-section.aggressive {
            background: linear-gradient(180deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.03) 60%, transparent 100%);
            border: 1px solid rgba(34, 197, 94, 0.25);
        }

        .hero-section.balanced {
            background: linear-gradient(180deg, rgba(251, 191, 36, 0.1) 0%, rgba(251, 191, 36, 0.03) 60%, transparent 100%);
            border: 1px solid rgba(251, 191, 36, 0.25);
        }

        .hero-section.defensive {
            background: linear-gradient(180deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.03) 60%, transparent 100%);
            border: 1px solid rgba(239, 68, 68, 0.25);
        }

        .regime-indicator {
            width: 96px;
            height: 96px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 44px;
            margin: 0 auto 24px;
            position: relative;
            z-index: 1;
        }

        .regime-indicator.aggressive {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.1) 100%);
            border: 3px solid #22C55E;
            animation: pulse-aggressive 2s ease-in-out infinite;
            box-shadow: 0 0 40px rgba(34, 197, 94, 0.2);
        }

        .regime-indicator.balanced {
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%);
            border: 3px solid #FBBF24;
            animation: pulse-balanced 2.5s ease-in-out infinite;
            box-shadow: 0 0 40px rgba(251, 191, 36, 0.2);
        }

        .regime-indicator.defensive {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%);
            border: 3px solid #EF4444;
            animation: pulse-defensive 1.5s ease-in-out infinite;
            box-shadow: 0 0 40px rgba(239, 68, 68, 0.2);
        }

        .hero-regime-name {
            font-size: 56px;
            font-weight: 800;
            letter-spacing: -2px;
            margin: 8px 0;
            line-height: 1.1;
            position: relative;
            z-index: 1;
            text-transform: uppercase;
        }

        .hero-regime-name.aggressive {
            color: #22C55E;
            text-shadow: 0 0 60px rgba(34, 197, 94, 0.4);
        }
        .hero-regime-name.balanced {
            color: #FBBF24;
            text-shadow: 0 0 60px rgba(251, 191, 36, 0.4);
        }
        .hero-regime-name.defensive {
            color: #EF4444;
            text-shadow: 0 0 60px rgba(239, 68, 68, 0.4);
        }

        .hero-score {
            font-size: 18px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            color: var(--fs-slate-400);
            margin-bottom: 16px;
            position: relative;
            z-index: 1;
            letter-spacing: 0.5px;
        }

        .hero-tagline {
            font-size: 17px;
            color: var(--fs-slate-300);
            margin: 0 auto 24px;
            max-width: 480px;
            line-height: 1.6;
            position: relative;
            z-index: 1;
        }

        .hero-posture {
            display: inline-block;
            padding: 14px 24px;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(59, 130, 246, 0.25);
            border-radius: 10px;
            font-size: 14px;
            color: var(--fs-slate-200);
            font-weight: 500;
            position: relative;
            z-index: 1;
            backdrop-filter: blur(8px);
        }

        .hero-duration {
            margin-top: 20px;
            font-size: 12px;
            color: var(--fs-slate-500);
            position: relative;
            z-index: 1;
            letter-spacing: 0.3px;
        }

        /* ===== FIVE FORCES STRIP ===== */
        .forces-strip {
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
            padding: 24px 20px;
            margin-bottom: 24px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(30, 41, 59, 0.2) 100%);
            border-radius: 16px;
            border: 1px solid rgba(59, 130, 246, 0.15);
            backdrop-filter: blur(8px);
        }

        .force-pill {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 18px;
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(71, 85, 105, 0.3);
            border-radius: 28px;
            font-size: 13px;
            color: var(--fs-slate-200);
            font-weight: 500;
            transition: all 0.25s ease;
        }

        .force-pill:hover {
            border-color: var(--fs-blue);
            background: rgba(59, 130, 246, 0.1);
            transform: translateY(-2px);
        }

        .signal-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }

        .signal-dot.bullish {
            background: var(--fs-green);
            box-shadow: 0 0 12px rgba(34, 197, 94, 0.5);
            animation: signal-pulse 2s ease-in-out infinite;
        }

        .signal-dot.bearish {
            background: var(--fs-red);
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.5);
            animation: signal-pulse 2s ease-in-out infinite;
        }

        .signal-dot.neutral {
            background: var(--fs-slate-500);
            opacity: 0.6;
        }

        /* ===== METRIC CARDS ===== */
        .metric-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(30, 41, 59, 0.3) 100%);
            border: 1px solid rgba(71, 85, 105, 0.25);
            border-radius: 14px;
            padding: 22px;
            margin: 8px 0;
            transition: all 0.25s ease;
            animation: fadeInUp 0.4s ease-out;
        }

        .metric-card:hover {
            border-color: var(--fs-blue);
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
        }

        .metric-card.bullish {
            border-left: 3px solid var(--fs-green);
        }

        .metric-card.bearish {
            border-left: 3px solid var(--fs-red);
        }

        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 6px;
        }

        .metric-title {
            font-size: 10px;
            font-weight: 700;
            color: var(--fs-slate-500);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .metric-source {
            font-size: 10px;
            color: var(--fs-slate-400);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 3px 8px;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 4px;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .metric-source:hover {
            background: rgba(59, 130, 246, 0.2);
            border-color: rgba(59, 130, 246, 0.4);
            color: var(--fs-blue-light);
        }

        .metric-why {
            font-size: 13px;
            color: var(--fs-slate-400);
            margin-bottom: 14px;
            font-style: italic;
            line-height: 1.5;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 600;
            color: var(--fs-slate-200);
            margin-bottom: 8px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -1px;
        }

        .metric-delta {
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 6px;
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.3px;
        }

        .metric-delta.positive {
            background: rgba(34, 197, 94, 0.15);
            color: var(--fs-green);
            border: 1px solid rgba(34, 197, 94, 0.25);
        }

        .metric-delta.negative {
            background: rgba(239, 68, 68, 0.15);
            color: var(--fs-red);
            border: 1px solid rgba(239, 68, 68, 0.25);
        }

        .metric-delta.neutral {
            background: rgba(100, 116, 139, 0.15);
            color: var(--fs-slate-400);
            border: 1px solid rgba(100, 116, 139, 0.25);
        }

        /* ===== HEADER CONTROLS ===== */
        .header-controls {
            display: flex;
            align-items: center;
            gap: 12px;
            justify-content: flex-end;
            padding-top: 16px;
        }

        .header-btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(71, 85, 105, 0.3);
            border-radius: 8px;
            font-size: 12px;
            font-weight: 500;
            color: var(--fs-slate-300);
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
        }

        .header-btn:hover {
            background: rgba(59, 130, 246, 0.15);
            border-color: rgba(59, 130, 246, 0.3);
            color: var(--fs-blue-light);
        }

        .header-btn.active {
            background: rgba(59, 130, 246, 0.2);
            border-color: rgba(59, 130, 246, 0.4);
            color: var(--fs-blue-light);
        }

        /* ===== ALERTS SECTION ===== */
        .alerts-section {
            padding: 16px 20px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0.03) 100%);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            margin-bottom: 12px;
        }

        .alerts-header {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .alerts-icon {
            font-size: 20px;
        }

        .alerts-text {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .alerts-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--fs-slate-200);
        }

        .alerts-desc {
            font-size: 12px;
            color: var(--fs-slate-500);
        }

        /* ===== SETTINGS ROW ===== */
        .settings-row {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 24px;
            padding: 16px 0;
            margin-top: 8px;
            border-top: 1px solid rgba(71, 85, 105, 0.15);
        }

        .settings-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: var(--fs-slate-400);
        }

        /* ===== SECTION HEADERS ===== */
        .section-header {
            font-size: 11px;
            font-weight: 700;
            color: var(--fs-blue);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 32px 0 18px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(59, 130, 246, 0.2);
            position: relative;
        }

        .section-header::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 60px;
            height: 2px;
            background: linear-gradient(90deg, var(--fs-blue), transparent);
        }

        /* ===== POPOVER STYLING ===== */
        [data-testid="stPopover"] > div {
            background: var(--fs-slate-800) !important;
            border: 1px solid rgba(59, 130, 246, 0.2) !important;
            border-radius: 12px !important;
        }

        [data-testid="stPopoverBody"] {
            padding: 16px !important;
        }

        /* Style the popover trigger button */
        [data-testid="stPopover"] > button {
            background: rgba(59, 130, 246, 0.1) !important;
            border: 1px solid rgba(59, 130, 246, 0.25) !important;
            border-radius: 8px !important;
            color: var(--fs-blue-light) !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stPopover"] > button:hover {
            background: rgba(59, 130, 246, 0.2) !important;
            border-color: rgba(59, 130, 246, 0.4) !important;
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
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: 500;
            color: #3B82F6;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: rgba(59, 130, 246, 0.25);
            border-color: rgba(59, 130, 246, 0.5);
        }

        /* Chart containers - tighter spacing, hide scrollbars */
        [data-testid="stPlotlyChart"] {
            margin-top: 4px;
        }

        [data-testid="stPlotlyChart"] > div {
            overflow: hidden !important;
        }

        .js-plotly-plot .plotly .scrollbar {
            display: none !important;
        }

        /* Hide any scrollbars in chart area */
        .stPlotlyChart iframe,
        .stPlotlyChart > div > div {
            scrollbar-width: none;
            -ms-overflow-style: none;
        }

        .stPlotlyChart iframe::-webkit-scrollbar,
        .stPlotlyChart > div > div::-webkit-scrollbar {
            display: none;
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
            color: #3B82F6;
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

        /* ===== DISCLAIMER MODAL ===== */
        .disclaimer-container {
            max-width: 640px;
            margin: 60px auto;
            padding: 44px;
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 20px;
            animation: fadeInUp 0.5s ease-out;
            position: relative;
            overflow: hidden;
        }

        /* Decorative wave in disclaimer */
        .disclaimer-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--fs-blue), var(--fs-blue-light), var(--fs-blue));
            background-size: 200% 100%;
            animation: shimmer 3s ease-in-out infinite;
        }

        .disclaimer-title {
            font-size: 32px;
            font-weight: 800;
            color: var(--fs-slate-200);
            margin-bottom: 8px;
            text-align: center;
            letter-spacing: -1px;
        }

        .disclaimer-subtitle {
            font-size: 15px;
            color: var(--fs-blue);
            text-align: center;
            margin-bottom: 28px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        .disclaimer-content {
            color: var(--fs-slate-300);
            font-size: 15px;
            line-height: 1.9;
            margin-bottom: 28px;
        }

        .disclaimer-content p {
            margin-bottom: 16px;
        }

        .disclaimer-content ul {
            margin: 20px 0;
            padding-left: 24px;
        }

        .disclaimer-content li {
            margin-bottom: 14px;
            color: var(--fs-slate-300);
        }

        .disclaimer-content strong {
            color: var(--fs-slate-100);
            font-weight: 600;
        }

        /* ===== BTC GATE SECTION ===== */
        .btc-gate-section {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.6) 100%);
            border: 1px solid rgba(71, 85, 105, 0.25);
            border-radius: 14px;
            padding: 20px 28px;
            margin: 24px 0;
            display: flex;
            align-items: center;
            gap: 24px;
            animation: fadeInUp 0.4s ease-out;
            position: relative;
            overflow: hidden;
        }

        /* Bitcoin orange accent glow */
        .btc-gate-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(ellipse at 10% 50%, rgba(247, 147, 26, 0.08) 0%, transparent 50%);
            pointer-events: none;
        }

        .btc-gate-section.passed {
            border-left: 4px solid var(--fs-green);
        }

        .btc-gate-section.failed {
            border-left: 4px solid var(--fs-red);
        }

        .btc-gate-label {
            font-size: 10px;
            font-weight: 700;
            color: var(--fs-slate-500);
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btc-gate-label .lock-icon {
            font-size: 16px;
        }

        .btc-gate-price {
            font-size: 24px;
            font-weight: 600;
            color: #F7931A;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.5px;
        }

        .btc-gate-status {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .gate-badge {
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            letter-spacing: 0.3px;
        }

        .gate-badge.passed {
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: var(--fs-green);
        }

        .gate-badge.failed {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: var(--fs-red);
        }

        .btc-gate-why {
            font-size: 12px;
            color: var(--fs-slate-500);
            font-style: italic;
        }

        /* ===== COMING SOON BADGE ===== */
        .coming-soon-badge {
            padding: 10px 20px;
            background: rgba(100, 116, 139, 0.2);
            border: 1px solid rgba(100, 116, 139, 0.3);
            border-radius: 6px;
            color: #94A3B8;
            font-weight: 600;
            font-size: 14px;
            cursor: default;
        }

        /* ===== TOGGLE SETTINGS BAR ===== */
        .settings-toggle-bar {
            display: flex;
            justify-content: center;
            padding: 8px 0 16px 0;
        }

        /* ===== MOBILE RESPONSIVENESS ===== */
        @media (max-width: 768px) {
            .forces-strip {
                flex-direction: column;
                gap: 10px;
                padding: 18px 14px;
            }

            .force-pill {
                width: 100%;
                justify-content: center;
                padding: 14px 18px;
            }

            .hero-regime-name {
                font-size: 40px;
                letter-spacing: -1.5px;
            }

            .hero-section {
                padding: 36px 18px 28px;
                border-radius: 16px;
            }

            .hero-section::after {
                height: 40px;
            }

            .hero-tagline {
                font-size: 15px;
            }

            .hero-posture {
                padding: 12px 18px;
                font-size: 13px;
            }

            .btc-gate-section {
                flex-direction: column;
                text-align: center;
                gap: 14px;
                padding: 18px 20px;
            }

            .btc-gate-status {
                justify-content: center;
                flex-wrap: wrap;
            }

            .disclaimer-container {
                margin: 20px 12px;
                padding: 28px 22px;
            }

            .disclaimer-title {
                font-size: 26px;
            }

            .metric-card {
                padding: 18px;
            }

            .metric-value {
                font-size: 24px;
            }

            .section-header {
                font-size: 10px;
                letter-spacing: 1.5px;
            }
        }

        /* Tablet adjustments */
        @media (min-width: 769px) and (max-width: 1024px) {
            .hero-regime-name {
                font-size: 48px;
            }
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


def render_disclaimer_modal():
    """Render disclaimer that must be accepted before viewing dashboard."""
    st.markdown("""
    <div class="disclaimer-container">
        <div class="disclaimer-title">🌊 FlowState</div>
        <div class="disclaimer-subtitle">Real-time crypto liquidity regime tracker</div>
        <div class="disclaimer-content">
            <p><strong>Important Disclaimer</strong></p>
            <p>This dashboard is provided for <strong>educational and informational purposes only</strong>. By using this tool, you acknowledge that:</p>
            <ul>
                <li>This is <strong>not financial advice</strong>. Nothing presented here constitutes a recommendation to buy, sell, or hold any asset.</li>
                <li>Past performance and historical correlations <strong>do not guarantee future results</strong>.</li>
                <li>The regime classification is based on a simplified model with <strong>known limitations</strong>.</li>
                <li>You should <strong>consult a qualified financial advisor</strong> before making investment decisions.</li>
                <li>The creator assumes <strong>no liability</strong> for any losses incurred.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Methodology expander
    with st.expander("📖 How This Works — Methodology"):
        st.markdown("""
**The Core Thesis**

Crypto markets are heavily influenced by global liquidity conditions. When there's abundant cheap money in the system, risk assets (including crypto) tend to perform well. When liquidity tightens, they struggle.

**The Five Forces We Track:**

1. **Fed Balance Sheet (WALCL)** — When the Fed expands its balance sheet, it injects liquidity. More money tends to flow into risk assets.

2. **Reverse Repo (RRP)** — Cash parked here is "on the sidelines." When it drains, that money often enters markets.

3. **High Yield Spreads** — The gap between junk bonds and Treasuries. Tight spreads = risk-on behavior.

4. **Dollar Index (DXY)** — A strong dollar tightens global conditions. Dollar weakness is typically bullish for crypto.

5. **Stablecoin Supply** — Proxy for capital on crypto's sidelines. Growth suggests capital ready to deploy.

**The BTC Gate**

Even with favorable liquidity conditions, we require Bitcoin to be above its 200-day moving average to confirm trend strength before signaling "Aggressive."

**Scoring**

Each indicator scores +1 (bullish), 0 (neutral), or -1 (bearish), multiplied by its weight. The weighted sum determines the regime:
- **Aggressive**: Score ≥ +4.0 AND BTC above 200 DMA
- **Balanced**: Score between -3.9 and +3.9
- **Defensive**: Score ≤ -4.0

**Anti-Whipsaw Logic**

To prevent false signals, regime changes require 2 consecutive days of threshold breach OR a margin > 1.0 point.
        """)

    # Accept button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("I Understand and Accept", use_container_width=True, type="primary"):
            st.session_state.disclaimer_accepted = True
            st.rerun()


def render_btc_gate_section(
    current_price: float,
    above_200dma: bool,
    plain_english: bool = True,
):
    """Render the BTC trend gate as a horizontal status bar."""
    status_class = "passed" if above_200dma else "failed"

    if plain_english:
        status_text = "Above trend ✓" if above_200dma else "Below trend ✗"
        why_text = "Bitcoin above its 200-day average confirms the uptrend" if above_200dma else "Bitcoin below its 200-day average — blocks Aggressive regime"
    else:
        status_text = "Above 200 DMA ✓" if above_200dma else "Below 200 DMA ✗"
        why_text = "BTC above 200 DMA confirms trend strength" if above_200dma else "BTC below 200 DMA — Aggressive regime blocked"

    price_str = f"${current_price:,.0f}" if current_price else "N/A"

    st.markdown(f"""
    <div class="btc-gate-section {status_class}">
        <div class="btc-gate-label">
            <span class="lock-icon">{"🔓" if above_200dma else "🔒"}</span>
            <span>Trend Gate</span>
        </div>
        <div class="btc-gate-price">{price_str}</div>
        <div class="btc-gate-status">
            <span class="gate-badge {status_class}">{status_text}</span>
            <span class="btc-gate-why">{why_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_email_signup():
    """Render email signup form for regime alerts - compact for popover."""
    from subscribers import add_subscriber, send_confirmation_email

    st.markdown("""
    <p style="font-size: 13px; color: #94A3B8; margin-bottom: 16px; line-height: 1.5;">
        Get notified when market conditions change. Choose your preferred frequency.
    </p>
    """, unsafe_allow_html=True)

    email = st.text_input(
        "Email",
        placeholder="your@email.com",
        label_visibility="collapsed",
        key="alert_email",
    )

    cadence = st.selectbox(
        "Frequency",
        options=["daily", "on_change", "weekly"],
        format_func=lambda x: {
            "daily": "Daily briefing (recommended)",
            "weekly": "Weekly summary",
            "on_change": "Regime changes only"
        }.get(x, x),
        label_visibility="collapsed",
        key="alert_cadence",
    )

    if st.button("Subscribe", use_container_width=True, type="primary", key="alert_subscribe"):
        if email:
            success, message = add_subscriber(email, cadence)
            if success:
                st.success("✓ Subscribed!")
                send_confirmation_email(email, cadence)
            else:
                st.warning(message)
        else:
            st.warning("Enter your email")


def render_notifications_cta():
    """Render the notifications CTA. Now shows email signup form."""
    render_email_signup()


def render_discord_cta(discord_url: str = "#"):
    """Render the Discord call-to-action card. DEPRECATED: Use render_notifications_cta() instead."""
    # Redirect to new function
    render_notifications_cta()


def render_feedback_form():
    """Render a delightful feedback form."""
    st.markdown("""
    <p style="font-size: 14px; color: #CBD5E1; margin-bottom: 16px; line-height: 1.6;">
        I built FlowState to help people make sense of crypto market conditions.
        <strong style="color: #3B82F6;">Your feedback shapes what comes next.</strong>
    </p>
    """, unsafe_allow_html=True)

    feedback_type = st.selectbox(
        "What's on your mind?",
        options=["feature", "bug", "general", "love"],
        format_func=lambda x: {
            "feature": "💡 Feature request",
            "bug": "🐛 Something's broken",
            "general": "💬 General feedback",
            "love": "💙 Just want to say thanks"
        }.get(x, x),
        label_visibility="collapsed",
        key="feedback_type",
    )

    feedback_text = st.text_area(
        "Tell me more",
        placeholder="What would make FlowState more useful for you?",
        height=100,
        label_visibility="collapsed",
        key="feedback_text",
    )

    email = st.text_input(
        "Email (optional)",
        placeholder="your@email.com (optional, for follow-up)",
        label_visibility="collapsed",
        key="feedback_email",
    )

    if st.button("Send Feedback", use_container_width=True, type="primary", key="feedback_submit"):
        if feedback_text.strip():
            success = save_feedback(feedback_type, feedback_text, email)
            if success:
                if feedback_type == "love":
                    st.success("🥹 That means a lot, thank you!")
                else:
                    st.success("✨ Thanks! Your feedback has been saved.")
                st.balloons()
        else:
            st.warning("Please share your thoughts!")


def save_feedback(feedback_type: str, text: str, email: str = "") -> bool:
    """Save feedback to a local JSON file."""
    import json
    from pathlib import Path
    from datetime import datetime

    feedback_file = Path(__file__).parent.parent / "feedback.json"

    try:
        if feedback_file.exists():
            with open(feedback_file, "r") as f:
                data = json.load(f)
        else:
            data = {"feedback": []}

        data["feedback"].append({
            "type": feedback_type,
            "text": text,
            "email": email,
            "timestamp": datetime.now().isoformat(),
        })

        with open(feedback_file, "w") as f:
            json.dump(data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False


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


SOURCE_URLS = {
    "FRED": "https://fred.stlouisfed.org/",
    "DefiLlama": "https://defillama.com/stablecoins",
    "CoinGecko": "https://www.coingecko.com/en/coins/bitcoin",
}


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
    source: Optional[str] = None,
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
        weight_html = f'<span style="color: #475569; font-size: 10px; margin-left: 8px;">({weight}x)</span>'

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

    source_html = ""
    if source:
        source_url = SOURCE_URLS.get(source, "#")
        source_html = f'<a href="{source_url}" target="_blank" class="metric-source">{source} ↗</a>'

    st.markdown(f"""<div class="metric-card {card_class}">
<div class="metric-header">
    <div class="metric-title"><span class="metric-name-with-info">{title}{info_html}</span>{weight_html}</div>
    {source_html}
</div>
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
        # Keep it simple - just show the percentage with arrow
        if pct > 0:
            return f"↑ {abs(pct):.1f}%"
        elif pct < 0:
            return f"↓ {abs(pct):.1f}%"
        else:
            return "0%"
    elif include_sign:
        return f"{pct:+.1f}%"
    else:
        return f"{pct:.1f}%"
