"""
Chart components using Plotly - Refined Terminal aesthetic
Clean, purposeful data visualization with excellent clarity
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Optional


# Color palette - refined terminal aesthetic
COLORS = {
    "bullish": "#22C55E",       # Clean green
    "bearish": "#EF4444",       # Clean red
    "neutral": "#64748B",       # Slate gray
    "accent": "#818CF8",        # Soft indigo
    "muted": "#334155",         # Dark slate
    "text": "#94A3B8",          # Slate 400
    "text_bright": "#E2E8F0",   # Slate 200
    "grid": "rgba(71, 85, 105, 0.15)",  # Subtle grid
    "btc": "#F7931A",           # Bitcoin orange
}


def create_sparkline(
    df: pd.DataFrame,
    value_col: str = "value",
    date_col: str = "date",
    height: int = 80,
    show_range: bool = True,
) -> go.Figure:
    """
    Create a refined sparkline with min/max context markers.
    Clean, readable, with subtle gradient fill.
    """
    if df is None or len(df) == 0:
        fig = go.Figure()
        fig.update_layout(
            height=height,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Determine trend direction for color
    if len(df) >= 2:
        start_val = df[value_col].iloc[0]
        end_val = df[value_col].iloc[-1]
        pct_change = (end_val - start_val) / start_val if start_val != 0 else 0

        if pct_change > 0.01:
            line_color = COLORS["bullish"]
            fill_opacity = 0.08
        elif pct_change < -0.01:
            line_color = COLORS["bearish"]
            fill_opacity = 0.08
        else:
            line_color = COLORS["neutral"]
            fill_opacity = 0.05
    else:
        line_color = COLORS["neutral"]
        fill_opacity = 0.05

    fig = go.Figure()

    # Main line with subtle gradient fill
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[value_col],
        mode="lines",
        line=dict(
            color=line_color,
            width=2,
            shape="spline",  # Smooth curves
        ),
        fill="tozeroy",
        fillcolor=f"rgba({_hex_to_rgb(line_color)}, {fill_opacity})",
        hovertemplate="<b>%{y:,.2f}</b><br>%{x|%b %d}<extra></extra>",
    ))

    # Find min and max points for context
    if show_range and len(df) >= 3:
        min_idx = df[value_col].idxmin()
        max_idx = df[value_col].idxmax()

        min_row = df.loc[min_idx]
        max_row = df.loc[max_idx]

        # Add subtle min/max markers (small dots)
        fig.add_trace(go.Scatter(
            x=[min_row[date_col], max_row[date_col]],
            y=[min_row[value_col], max_row[value_col]],
            mode="markers",
            marker=dict(
                color=[COLORS["bearish"], COLORS["bullish"]],
                size=5,
                opacity=0.6,
            ),
            hoverinfo="skip",
        ))

    # Current value endpoint marker
    if len(df) > 0:
        fig.add_trace(go.Scatter(
            x=[df[date_col].iloc[-1]],
            y=[df[value_col].iloc[-1]],
            mode="markers",
            marker=dict(
                color=line_color,
                size=7,
                line=dict(color="rgba(15, 23, 42, 0.8)", width=2),
            ),
            hoverinfo="skip",
        ))

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=4, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(99, 102, 241, 0.3)",
            font=dict(color=COLORS["text_bright"], size=12),
        ),
    )

    return fig


def create_score_gauge(
    score: float,
    min_val: float = -6.5,
    max_val: float = 6.5,
    thresholds: dict = None,
) -> go.Figure:
    """
    Create a refined horizontal gauge with clear zone labels.
    Minimal, easy to interpret at a glance.
    """
    if thresholds is None:
        thresholds = {"defensive": -4, "aggressive": 4}

    # Normalize positions
    def normalize(val):
        return (val - min_val) / (max_val - min_val)

    score_pos = normalize(score)
    score_pos = max(0.02, min(0.98, score_pos))  # Keep marker visible

    def_end = normalize(thresholds["defensive"])
    agg_start = normalize(thresholds["aggressive"])

    fig = go.Figure()

    # Zone backgrounds - three distinct regions
    zones = [
        (0, def_end, COLORS["bearish"], 0.12),           # Defensive zone
        (def_end, agg_start, COLORS["neutral"], 0.06),   # Balanced zone
        (agg_start, 1, COLORS["bullish"], 0.12),         # Aggressive zone
    ]

    for x0, x1, color, opacity in zones:
        fig.add_shape(
            type="rect",
            x0=x0, x1=x1,
            y0=0, y1=1,
            fillcolor=f"rgba({_hex_to_rgb(color)}, {opacity})",
            line=dict(width=0),
            layer="below",
        )

    # Subtle border for the gauge track
    fig.add_shape(
        type="rect",
        x0=0, x1=1,
        y0=0, y1=1,
        fillcolor="rgba(0,0,0,0)",
        line=dict(color="rgba(71, 85, 105, 0.3)", width=1),
        layer="below",
    )

    # Threshold markers - subtle vertical lines
    for val in [thresholds["defensive"], thresholds["aggressive"]]:
        x_pos = normalize(val)
        fig.add_shape(
            type="line",
            x0=x_pos, x1=x_pos,
            y0=-0.1, y1=1.1,
            line=dict(color="rgba(148, 163, 184, 0.4)", width=1, dash="dot"),
        )

    # Score marker - prominent diamond
    marker_color = (
        COLORS["bearish"] if score <= thresholds["defensive"]
        else COLORS["bullish"] if score >= thresholds["aggressive"]
        else COLORS["accent"]
    )

    fig.add_trace(go.Scatter(
        x=[score_pos],
        y=[0.5],
        mode="markers",
        marker=dict(
            symbol="diamond",
            size=16,
            color=marker_color,
            line=dict(color="rgba(15, 23, 42, 1)", width=2),
        ),
        hovertemplate=f"<b>Score: {score:+.1f}</b><extra></extra>",
    ))

    # Zone labels
    zone_labels = [
        (def_end / 2, "Defensive", COLORS["bearish"]),
        ((def_end + agg_start) / 2, "Balanced", COLORS["text"]),
        ((agg_start + 1) / 2, "Aggressive", COLORS["bullish"]),
    ]

    for x, label, color in zone_labels:
        fig.add_annotation(
            x=x, y=0.5,
            text=label,
            showarrow=False,
            font=dict(size=9, color=color, family="system-ui, -apple-system, sans-serif"),
            opacity=0.7,
        )

    fig.update_layout(
        height=44,
        margin=dict(l=8, r=8, t=2, b=2),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            visible=False,
            range=[-0.02, 1.02],
        ),
        yaxis=dict(
            visible=False,
            range=[-0.2, 1.2],
        ),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(99, 102, 241, 0.3)",
            font=dict(color=COLORS["text_bright"], size=12),
        ),
    )

    return fig


def create_btc_chart(
    df: pd.DataFrame,
    ma_200: Optional[float] = None,
    height: int = 160,
) -> go.Figure:
    """
    Create a refined BTC price chart with 200DMA overlay.
    Clean grid, clear annotation, gradient fill for context.
    """
    if df is None or len(df) == 0:
        fig = go.Figure()
        fig.update_layout(height=height)
        return fig

    current_price = df["price"].iloc[-1] if len(df) > 0 else None
    above_ma = current_price and ma_200 and current_price > ma_200

    # Price line color based on position relative to MA
    line_color = COLORS["bullish"] if above_ma else COLORS["bearish"] if ma_200 else COLORS["btc"]

    fig = go.Figure()

    # Price area fill - subtle gradient effect
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["price"],
        mode="lines",
        name="BTC",
        line=dict(color=line_color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({_hex_to_rgb(line_color)}, 0.06)",
        hovertemplate="<b>$%{y:,.0f}</b><br>%{x|%b %d, %Y}<extra></extra>",
    ))

    # 200 DMA line - clean and subtle
    if ma_200:
        fig.add_hline(
            y=ma_200,
            line=dict(
                color=COLORS["accent"],
                width=2,
                dash="dash",
            ),
        )

        # Clean annotation positioned on the right
        fig.add_annotation(
            x=1.0,
            xref="paper",
            y=ma_200,
            text=f"200 DMA ${ma_200:,.0f}",
            showarrow=False,
            xanchor="left",
            font=dict(size=10, color=COLORS["accent"]),
            bgcolor="rgba(15, 23, 42, 0.8)",
            borderpad=4,
        )

    # Current price marker
    if len(df) > 0:
        fig.add_trace(go.Scatter(
            x=[df["date"].iloc[-1]],
            y=[df["price"].iloc[-1]],
            mode="markers",
            marker=dict(
                color=line_color,
                size=8,
                line=dict(color="rgba(15, 23, 42, 0.9)", width=2),
            ),
            hoverinfo="skip",
            showlegend=False,
        ))

    # Calculate nice y-axis range
    y_min = df["price"].min()
    y_max = df["price"].max()
    if ma_200:
        y_min = min(y_min, ma_200 * 0.95)
        y_max = max(y_max, ma_200 * 1.05)
    y_padding = (y_max - y_min) * 0.1

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=90, t=8, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            showline=False,
            tickformat="%b %d",
            tickfont=dict(
                color=COLORS["text"],
                size=10,
                family="system-ui, -apple-system, sans-serif",
            ),
            tickmode="auto",
            nticks=5,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["grid"],
            gridwidth=1,
            showline=False,
            tickformat="$,.0f",
            tickfont=dict(
                color=COLORS["text"],
                size=10,
                family="system-ui, -apple-system, sans-serif",
            ),
            range=[y_min - y_padding, y_max + y_padding],
            tickmode="auto",
            nticks=4,
            side="right",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(99, 102, 241, 0.3)",
            font=dict(color=COLORS["text_bright"], size=12),
        ),
    )

    return fig


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string for use in rgba()."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"{r}, {g}, {b}"
