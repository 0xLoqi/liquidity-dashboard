"""
Supabase-backed subscriber storage for FlowState.
Replaces ephemeral JSON file storage with persistent database.
"""

import os
from datetime import datetime
from typing import Optional
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

_client: Optional[Client] = None


def get_client() -> Optional[Client]:
    """Get or create Supabase client."""
    global _client
    if _client is None and SUPABASE_URL and SUPABASE_KEY:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def is_configured() -> bool:
    """Check if Supabase is configured."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


def get_all_subscribers() -> list[dict]:
    """Get all active subscribers."""
    client = get_client()
    if not client:
        return []

    result = client.table("subscribers").select("*").eq("is_waitlist", False).execute()
    return result.data or []


def get_all_waitlist() -> list[dict]:
    """Get all waitlisted subscribers."""
    client = get_client()
    if not client:
        return []

    result = client.table("subscribers").select("*").eq("is_waitlist", True).execute()
    return result.data or []


def get_subscriber_count() -> int:
    """Get count of active subscribers."""
    client = get_client()
    if not client:
        return 0

    result = client.table("subscribers").select("id", count="exact").eq("is_waitlist", False).execute()
    return result.count or 0


def get_waitlist_count() -> int:
    """Get count of waitlisted subscribers."""
    client = get_client()
    if not client:
        return 0

    result = client.table("subscribers").select("id", count="exact").eq("is_waitlist", True).execute()
    return result.count or 0


def find_subscriber(email: str) -> Optional[dict]:
    """Find a subscriber by email."""
    client = get_client()
    if not client:
        return None

    result = client.table("subscribers").select("*").eq("email", email.lower()).execute()
    if result.data:
        return result.data[0]
    return None


def add_subscriber(email: str, cadence: str, is_waitlist: bool = False) -> dict:
    """Add a new subscriber or waitlist entry."""
    client = get_client()
    if not client:
        raise RuntimeError("Supabase not configured")

    data = {
        "email": email.lower(),
        "cadence": cadence,
        "is_waitlist": is_waitlist,
        "confirmed": False,
        "subscribed_at": datetime.now().isoformat(),
    }

    result = client.table("subscribers").insert(data).execute()
    return result.data[0] if result.data else data


def update_subscriber(email: str, updates: dict) -> bool:
    """Update a subscriber's data."""
    client = get_client()
    if not client:
        return False

    result = client.table("subscribers").update(updates).eq("email", email.lower()).execute()
    return bool(result.data)


def delete_subscriber(email: str) -> bool:
    """Delete a subscriber by email."""
    client = get_client()
    if not client:
        return False

    result = client.table("subscribers").delete().eq("email", email.lower()).execute()
    return bool(result.data)


def promote_from_waitlist(email: str) -> bool:
    """Promote a waitlisted user to active subscriber."""
    return update_subscriber(email, {"is_waitlist": False, "subscribed_at": datetime.now().isoformat()})
