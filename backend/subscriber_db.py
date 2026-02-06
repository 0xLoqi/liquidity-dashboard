"""
Supabase-backed subscriber storage for FlowState.
Replaces ephemeral JSON file storage with persistent database.
"""

import os
from datetime import datetime
from typing import Optional, Tuple
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

_client: Optional[Client] = None


class SupabaseError(Exception):
    """Raised when Supabase operations fail."""
    pass


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

    try:
        result = client.table("subscribers").select("*").eq("is_waitlist", False).execute()
        return result.data or []
    except Exception as e:
        raise SupabaseError(f"Failed to get subscribers: {e}")


def get_all_waitlist() -> list[dict]:
    """Get all waitlisted subscribers."""
    client = get_client()
    if not client:
        return []

    try:
        result = client.table("subscribers").select("*").eq("is_waitlist", True).execute()
        return result.data or []
    except Exception as e:
        raise SupabaseError(f"Failed to get waitlist: {e}")


def get_subscriber_count() -> int:
    """Get count of active subscribers."""
    client = get_client()
    if not client:
        return 0

    try:
        result = client.table("subscribers").select("id", count="exact").eq("is_waitlist", False).execute()
        return result.count or 0
    except Exception as e:
        raise SupabaseError(f"Failed to get subscriber count: {e}")


def get_waitlist_count() -> int:
    """Get count of waitlisted subscribers."""
    client = get_client()
    if not client:
        return 0

    try:
        result = client.table("subscribers").select("id", count="exact").eq("is_waitlist", True).execute()
        return result.count or 0
    except Exception as e:
        raise SupabaseError(f"Failed to get waitlist count: {e}")


def find_subscriber(email: str) -> Optional[dict]:
    """Find a subscriber by email."""
    client = get_client()
    if not client:
        return None

    try:
        result = client.table("subscribers").select("*").eq("email", email.lower()).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        raise SupabaseError(f"Failed to find subscriber: {e}")


def add_subscriber(email: str, cadence: str, is_waitlist: bool = False) -> dict:
    """Add a new subscriber or waitlist entry. Raises on duplicate."""
    client = get_client()
    if not client:
        raise SupabaseError("Supabase not configured")

    data = {
        "email": email.lower(),
        "cadence": cadence,
        "is_waitlist": is_waitlist,
        "confirmed": False,
        "subscribed_at": datetime.now().isoformat(),
    }

    try:
        result = client.table("subscribers").insert(data).execute()
        if result.data:
            return result.data[0]
        raise SupabaseError("Insert returned no data")
    except Exception as e:
        error_str = str(e).lower()
        if "duplicate" in error_str or "unique" in error_str or "23505" in error_str:
            raise SupabaseError("Email already exists")
        raise SupabaseError(f"Failed to add subscriber: {e}")


def atomic_subscribe(email: str, cadence: str, max_subscribers: int) -> Tuple[bool, str, dict]:
    """
    Atomically subscribe a user, handling race conditions.

    Returns: (success, message, data)
    - success: True if subscribed/waitlisted successfully
    - message: Human-readable result message
    - data: Dict with keys: waitlisted, spots_remaining, spot_number
    """
    client = get_client()
    if not client:
        raise SupabaseError("Supabase not configured")

    email = email.lower()

    try:
        # Check if already exists
        existing = find_subscriber(email)
        if existing:
            if existing.get("is_waitlist"):
                return True, "You're on the waitlist! We'll notify you when a spot opens.", {
                    "waitlisted": True, "already_existed": True
                }
            return True, "You're already subscribed!", {
                "waitlisted": False, "already_existed": True
            }

        # Get current count
        count = get_subscriber_count()
        spots_remaining = max(0, max_subscribers - count)
        is_waitlist = spots_remaining == 0

        # Try to insert - if race condition, unique constraint will catch it
        try:
            add_subscriber(email, cadence, is_waitlist=is_waitlist)
        except SupabaseError as e:
            if "already exists" in str(e).lower():
                # Race condition: someone else added this email
                existing = find_subscriber(email)
                if existing and existing.get("is_waitlist"):
                    return True, "You're on the waitlist!", {"waitlisted": True, "already_existed": True}
                return True, "You're already subscribed!", {"waitlisted": False, "already_existed": True}
            raise

        if is_waitlist:
            waitlist_pos = get_waitlist_count()
            return True, f"All spots taken! You're #{waitlist_pos} on the waitlist.", {
                "waitlisted": True,
                "spots_remaining": 0,
                "waitlist_position": waitlist_pos,
            }
        else:
            # Re-count to get accurate spot number (handles race condition)
            new_count = get_subscriber_count()
            return True, f"You're in! Spot #{new_count} of {max_subscribers}.", {
                "waitlisted": False,
                "spots_remaining": max(0, max_subscribers - new_count),
                "spot_number": new_count,
            }

    except SupabaseError:
        raise
    except Exception as e:
        raise SupabaseError(f"Subscribe failed: {e}")


def update_subscriber(email: str, updates: dict) -> bool:
    """Update a subscriber's data."""
    client = get_client()
    if not client:
        return False

    try:
        result = client.table("subscribers").update(updates).eq("email", email.lower()).execute()
        return bool(result.data)
    except Exception as e:
        raise SupabaseError(f"Failed to update subscriber: {e}")


def delete_subscriber(email: str) -> bool:
    """Delete a subscriber by email."""
    client = get_client()
    if not client:
        return False

    try:
        result = client.table("subscribers").delete().eq("email", email.lower()).execute()
        return bool(result.data)
    except Exception as e:
        raise SupabaseError(f"Failed to delete subscriber: {e}")


def promote_from_waitlist(email: str) -> bool:
    """Promote a waitlisted user to active subscriber."""
    return update_subscriber(email, {"is_waitlist": False, "subscribed_at": datetime.now().isoformat()})
