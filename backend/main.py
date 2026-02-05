"""
FlowState API - FastAPI backend for the liquidity regime dashboard.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np

from data.fetchers import fetch_all_data, has_fred_api_key
from data.cache import CacheManager
from data.transforms import calculate_metrics, get_chart_data
from scoring.engine import calculate_scores
from scoring.regime import determine_regime
from scoring.explanations import generate_explanation
from config import CACHE_TTL, REGIME_THRESHOLDS, WEIGHTS

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="FlowState API", version="1.0.0")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "https://flowstate.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE = CacheManager()
STATE_FILE = Path(__file__).parent / "regime_state.json"
FEEDBACK_FILE = Path(__file__).parent / "feedback.json"
SUBSCRIBERS_FILE = Path(__file__).parent / "subscribers.json"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class SubscribeRequest(BaseModel):
    email: str
    cadence: str = "daily"


class FeedbackRequest(BaseModel):
    type: str
    text: str
    email: str = ""


class AdminLoginRequest(BaseModel):
    password: str


class TestEmailRequest(BaseModel):
    email: str
    cadence: str = "daily"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def convert_numpy(obj):
    """Recursively convert numpy types to native Python types."""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif pd.isna(obj) if isinstance(obj, float) else False:
        return None
    return obj


def serialize_chart_data(charts: dict) -> dict:
    """Convert DataFrames to JSON-serializable arrays."""
    result = {}
    for key, df in charts.items():
        if df is not None and isinstance(df, pd.DataFrame) and len(df) > 0:
            records = []
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    val = row[col]
                    if hasattr(val, "isoformat"):
                        record[col] = val.isoformat()[:10]
                    elif isinstance(val, (float, int)):
                        record[col] = round(float(val), 4)
                    else:
                        record[col] = val
                records.append(record)
            result[key] = records
        else:
            result[key] = []
    return result


def build_indicator_response(metrics: dict, scores: dict, mode: str = "plain") -> dict:
    """Build the indicators portion of the API response."""
    indicators = {}
    individual = scores.get("individual", {})

    for name, score_data in individual.items():
        metric_data = metrics.get(name, {})
        score_val = score_data.get("score", 0)

        if score_val > 0:
            direction = "positive"
        elif score_val < 0:
            direction = "negative"
        else:
            direction = "neutral"

        # Get the raw delta value
        delta = metric_data.get("delta_4w") or metric_data.get("delta_21d")

        indicators[name] = {
            "current": metric_data.get("current"),
            "delta": delta,
            "delta_direction": direction,
            "score": score_data.get("score", 0),
            "weighted": score_data.get("weighted", 0),
            "weight": score_data.get("weight", 1),
            "reason": score_data.get("reason", ""),
            "latest_date": metric_data.get("latest_date"),
        }

    return indicators


def load_json_file(path: Path) -> dict:
    """Load a JSON file, returning empty dict structure on failure."""
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_json_file(path: Path, data: dict):
    """Save data to a JSON file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def verify_admin(authorization: Optional[str]) -> bool:
    """Verify admin authorization header."""
    if not authorization:
        return False
    return authorization == f"Bearer {ADMIN_TOKEN}"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/dashboard")
async def get_dashboard(force_refresh: bool = False):
    """Primary endpoint - returns all dashboard data in one call."""

    if not has_fred_api_key():
        raise HTTPException(status_code=500, detail="FRED_API_KEY not configured")

    # Load data with caching
    if force_refresh:
        CACHE.invalidate_all()

    cached_data = CACHE.get("all_data")
    if cached_data:
        data = cached_data
    else:
        data = fetch_all_data()
        CACHE.set("all_data", data, ttl=min(CACHE_TTL.values()))

    metrics = calculate_metrics(data)
    scores = calculate_scores(metrics)
    regime, state, regime_info = determine_regime(scores, state_file=STATE_FILE)
    explanation = generate_explanation(regime, scores, metrics, regime_info)
    charts = get_chart_data(data)

    # Days in regime from state file
    days_in_regime = regime_info.get("days_in_regime", 0)
    regime_start_date = None
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                st = json.load(f)
                regime_start_date = st.get("regime_start_date")
    except Exception:
        pass

    btc = metrics.get("btc", {})

    response = {
        "regime": regime,
        "score": scores["total"],
        "max_possible": scores["max_possible"],
        "min_possible": scores["min_possible"],
        "btc_above_200dma": scores.get("btc_above_200dma", False),
        "btc_distance_from_200dma": scores.get("btc_distance_from_200dma"),
        "days_in_regime": days_in_regime or 0,
        "regime_start_date": regime_start_date,
        "regime_info": {
            "pending_flip": regime_info.get("pending_flip", False),
            "proposed_regime": regime_info.get("proposed_regime", "balanced"),
            "consecutive_days": regime_info.get("consecutive_days", 0),
            "score_trend": regime_info.get("score_trend", "flat"),
            "days_until_flip": regime_info.get("days_until_flip"),
        },
        "thresholds": {
            "aggressive": REGIME_THRESHOLDS["aggressive"],
            "defensive": REGIME_THRESHOLDS["defensive"],
        },
        "indicators": build_indicator_response(metrics, scores),
        "btc": {
            "current_price": btc.get("current_price"),
            "ma_200": btc.get("ma_200"),
            "above_200dma": btc.get("above_200dma", False),
        },
        "charts": serialize_chart_data(charts),
        "explanation": explanation,
        "timestamp": datetime.now().isoformat(),
    }

    return JSONResponse(content=convert_numpy(response))


MAX_SUBSCRIBERS = 100


@app.get("/api/spots")
async def get_spots():
    """Get remaining subscriber spots."""
    data = load_json_file(SUBSCRIBERS_FILE)
    if not data:
        data = {"subscribers": [], "waitlist": []}
    subscriber_count = len(data.get("subscribers", []))
    waitlist_count = len(data.get("waitlist", []))
    spots_remaining = max(0, MAX_SUBSCRIBERS - subscriber_count)
    return {
        "spots_remaining": spots_remaining,
        "total_spots": MAX_SUBSCRIBERS,
        "waitlist_count": waitlist_count,
    }


@app.post("/api/subscribe")
async def subscribe(req: SubscribeRequest):
    """Subscribe an email to regime alerts, or add to waitlist if full."""
    email = req.email.strip().lower()
    cadence = req.cadence

    if not email or "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")

    if cadence not in ("daily", "weekly", "on_change"):
        raise HTTPException(status_code=400, detail="Invalid cadence")

    data = load_json_file(SUBSCRIBERS_FILE)
    if not data:
        data = {"subscribers": [], "waitlist": []}

    existing = [s["email"] for s in data.get("subscribers", [])]
    waitlisted = [s["email"] for s in data.get("waitlist", [])]

    if email in existing:
        return {"success": True, "message": "You're already subscribed!", "waitlisted": False}

    if email in waitlisted:
        return {"success": True, "message": "You're on the waitlist! We'll notify you when a spot opens.", "waitlisted": True}

    subscriber_count = len(data.get("subscribers", []))
    spots_remaining = max(0, MAX_SUBSCRIBERS - subscriber_count)

    if spots_remaining > 0:
        # Active subscriber
        data.setdefault("subscribers", []).append({
            "email": email,
            "cadence": cadence,
            "subscribed_at": datetime.now().isoformat(),
            "confirmed": False,
        })
        save_json_file(SUBSCRIBERS_FILE, data)

        # Try sending confirmation email
        try:
            from subscribers import send_confirmation_email
            result = send_confirmation_email(email, cadence)
            if not result:
                print(f"Warning: Confirmation email to {email} was not sent")
        except Exception as e:
            print(f"Error sending confirmation email: {e}")

        return {
            "success": True,
            "message": f"You're in! Spot #{subscriber_count + 1} of {MAX_SUBSCRIBERS}.",
            "waitlisted": False,
            "spots_remaining": spots_remaining - 1,
        }
    else:
        # Waitlist
        data.setdefault("waitlist", []).append({
            "email": email,
            "cadence": cadence,
            "added_at": datetime.now().isoformat(),
        })
        save_json_file(SUBSCRIBERS_FILE, data)

        return {
            "success": True,
            "message": "All spots are taken! You've been added to the waitlist.",
            "waitlisted": True,
            "spots_remaining": 0,
        }


@app.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest):
    """Submit user feedback."""
    data = load_json_file(FEEDBACK_FILE)
    if not data:
        data = {"feedback": []}

    data.setdefault("feedback", []).append({
        "type": req.type,
        "text": req.text,
        "email": req.email,
        "timestamp": datetime.now().isoformat(),
    })
    save_json_file(FEEDBACK_FILE, data)

    return {"success": True}


@app.post("/api/admin/login")
async def admin_login(req: AdminLoginRequest):
    """Authenticate admin."""
    if req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"authenticated": True, "token": ADMIN_TOKEN}


@app.get("/api/admin/subscribers")
async def get_subscribers(authorization: Optional[str] = Header(None)):
    """List all subscribers (admin only)."""
    if not verify_admin(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = load_json_file(SUBSCRIBERS_FILE)
    return data.get("subscribers", [])


@app.delete("/api/admin/subscribers/{email}")
async def delete_subscriber(email: str, authorization: Optional[str] = Header(None)):
    """Remove a subscriber (admin only)."""
    if not verify_admin(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = load_json_file(SUBSCRIBERS_FILE)
    if not data:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    subscribers = data.get("subscribers", [])
    original_count = len(subscribers)
    data["subscribers"] = [s for s in subscribers if s["email"] != email]

    if len(data["subscribers"]) == original_count:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    save_json_file(SUBSCRIBERS_FILE, data)
    return {"success": True}


@app.get("/api/admin/feedback")
async def get_feedback(authorization: Optional[str] = Header(None)):
    """List all feedback (admin only)."""
    if not verify_admin(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = load_json_file(FEEDBACK_FILE)
    return data.get("feedback", [])


@app.post("/api/admin/test-email")
async def send_test_email(req: TestEmailRequest, authorization: Optional[str] = Header(None)):
    """Send a test email (admin only)."""
    if not verify_admin(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        from subscribers import send_confirmation_email
        success = send_confirmation_email(req.email, req.cadence)
        if success:
            return {"success": True, "message": f"Test email sent to {req.email}"}
        return {"success": False, "message": "Failed to send email (check RESEND_API_KEY)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refresh")
async def force_refresh():
    """Force cache invalidation and re-fetch."""
    CACHE.invalidate_all()
    return {"success": True, "message": "Cache cleared"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "fred_key_configured": has_fred_api_key(),
        "timestamp": datetime.now().isoformat(),
    }
