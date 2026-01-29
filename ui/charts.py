"""
Chart components using Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


def create_sparkline(
    df: pd.DataFrame,
    value_col: str = "value",
    date_col: str = "date",
    color: str = "#6366f1",
    height: int = 60,
    show_current: bool = True,
) -> go.Figure:
    """
    Create a minimal sparkline chart.
    """
    if df is None or len(df) == 0:
        # Return empty figure
        fig = go.Figure()
        fig.update_layout(
            height=height,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Determine color based on trend
    if len(df) >= 2:
        start_val = df[value_col].iloc[0]
        end_val = df[value_col].iloc[-1]
        if end_val > start_val * 1.01:
            line_color = "#10B981"  # Green
        elif end_val < start_val * 0.99:
            line_color = "#EF4444"  # Red
        else:
            line_color = "#6B7280"  # Gray
    else:
        line_color = color

    fig = go.Figure()

    # Add area fill
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[value_col],
        mode="lines",
        line=dict(color=line_color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({int(line_color[1:3], 16)}, {int(line_color[3:5], 16)}, {int(line_color[5:7], 16)}, 0.1)",
        hovertemplate="%{y:,.2f}<extra></extra>",
    ))

    # Add current value marker
    if show_current and len(df) > 0:
        fig.add_trace(go.Scatter(
            x=[df[date_col].iloc[-1]],
            y=[df[value_col].iloc[-1]],
            mode="markers",
            marker=dict(color=line_color, size=8),
            hoverinfo="skip",
        ))

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            visible=False,
            showgrid=False,
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
        ),
        hovermode="x unified",
    )

    return fig


def create_score_gauge(
    score: float,
    min_val: float = -6.5,
    max_val: float = 6.5,
    thresholds: dict = None,
) -> go.Figure:
    """
    Create a horizontal gauge showing current score position.
    """
    if thresholds is None:
        thresholds = {"defensive": -4, "aggressive": 4}

    # Normalize score to 0-1 range for positioning
    normalized = (score - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))

    fig = go.Figure()

    # Background bar
    fig.add_trace(go.Bar(
        x=[1],
        y=["Score"],
        orientation="h",
        marker=dict(
            color="rgba(55, 65, 81, 0.3)",
        ),
        hoverinfo="skip",
    ))

    # Defensive zone
    defensive_width = (thresholds["defensive"] - min_val) / (max_val - min_val)
    fig.add_trace(go.Bar(
        x=[defensive_width],
        y=["Score"],
        orientation="h",
        marker=dict(color="rgba(239, 68, 68, 0.2)"),
        hoverinfo="skip",
    ))

    # Aggressive zone
    aggressive_start = (thresholds["aggressive"] - min_val) / (max_val - min_val)
    aggressive_width = 1 - aggressive_start
    fig.add_shape(
        type="rect",
        x0=aggressive_start,
        x1=1,
        y0=-0.4,
        y1=0.4,
        fillcolor="rgba(16, 185, 129, 0.2)",
        line=dict(width=0),
    )

    # Score marker
    marker_color = "#EF4444" if score <= thresholds["defensive"] else (
        "#10B981" if score >= thresholds["aggressive"] else "#F59E0B"
    )

    fig.add_trace(go.Scatter(
        x=[normalized],
        y=["Score"],
        mode="markers",
        marker=dict(
            symbol="diamond",
            size=20,
            color=marker_color,
            line=dict(color="white", width=2),
        ),
        hovertemplate=f"Score: {score:.1f}<extra></extra>",
    ))

    # Add threshold lines
    for name, val in thresholds.items():
        x_pos = (val - min_val) / (max_val - min_val)
        fig.add_vline(
            x=x_pos,
            line=dict(color="rgba(156, 163, 175, 0.5)", width=1, dash="dash"),
        )

    fig.update_layout(
        height=50,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        barmode="overlay",
        xaxis=dict(
            visible=False,
            range=[0, 1],
        ),
        yaxis=dict(
            visible=False,
        ),
    )

    return fig


def create_btc_chart(
    df: pd.DataFrame,
    ma_200: Optional[float] = None,
    height: int = 200,
) -> go.Figure:
    """
    Create BTC price chart with 200DMA overlay.
    """
    if df is None or len(df) == 0:
        fig = go.Figure()
        fig.update_layout(height=height)
        return fig

    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["price"],
        mode="lines",
        name="BTC Price",
        line=dict(color="#F7931A", width=2),
        hovertemplate="$%{y:,.0f}<extra></extra>",
    ))

    # 200 DMA line
    if ma_200:
        fig.add_hline(
            y=ma_200,
            line=dict(color="#6366f1", width=2, dash="dash"),
            annotation_text=f"200 DMA: ${ma_200:,.0f}",
            annotation_position="right",
        )

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=80, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            tickformat="%b %d",
            tickfont=dict(color="rgba(156, 163, 175, 0.8)", size=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(55, 65, 81, 0.3)",
            tickformat="$,.0f",
            tickfont=dict(color="rgba(156, 163, 175, 0.8)", size=10),
        ),
        hovermode="x unified",
    )

    return fig
