"""
SQLite caching for API data
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any, Dict
import pickle

from config import CACHE_TTL


class CacheManager:
    """Manages SQLite-based caching for API data."""

    def __init__(self, db_path: str = "cache.db"):
        self.db_path = Path(__file__).parent.parent / db_path
        self._init_db()

    def _init_db(self):
        """Initialize the cache database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    timestamp TEXT,
                    ttl INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    path TEXT NOT NULL,
                    referrer TEXT,
                    visitor TEXT,
                    utm_source TEXT,
                    utm_campaign TEXT
                )
            """)
            conn.commit()

    def get(self, key: str) -> Optional[Any]:
        """
        Get cached data if not expired.
        Returns None if not found or expired.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data, timestamp, ttl FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            data_blob, timestamp_str, ttl = row
            cached_time = datetime.fromisoformat(timestamp_str)

            if datetime.now() - cached_time > timedelta(seconds=ttl):
                # Expired
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                return None

            return pickle.loads(data_blob)

    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """
        Cache data with optional TTL (seconds).
        Defaults to 1 hour TTL.
        """
        if ttl is None:
            ttl = 3600

        data_blob = pickle.dumps(data)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache (key, data, timestamp, ttl)
                VALUES (?, ?, ?, ?)
            """, (key, data_blob, datetime.now().isoformat(), ttl))
            conn.commit()

    def get_age(self, key: str) -> Optional[timedelta]:
        """Get the age of a cached item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            cached_time = datetime.fromisoformat(row[0])
            return datetime.now() - cached_time

    def invalidate(self, key: str):
        """Remove a specific cache entry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()

    def invalidate_all(self):
        """Clear entire cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()

    def log_hit(self, path: str, referrer: str = "", visitor: str = "",
                utm_source: str = "", utm_campaign: str = ""):
        """Log a page hit for analytics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO hits (ts, path, referrer, visitor, utm_source, utm_campaign) VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), path, referrer, visitor, utm_source, utm_campaign),
            )
            conn.commit()

    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for the last N days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            total = conn.execute(
                "SELECT COUNT(*) as c FROM hits WHERE ts >= ?", (cutoff,)
            ).fetchone()["c"]

            unique = conn.execute(
                "SELECT COUNT(DISTINCT visitor) as c FROM hits WHERE ts >= ? AND visitor != ''", (cutoff,)
            ).fetchone()["c"]

            by_path = conn.execute(
                "SELECT path, COUNT(*) as c FROM hits WHERE ts >= ? GROUP BY path ORDER BY c DESC",
                (cutoff,),
            ).fetchall()

            by_referrer = conn.execute(
                "SELECT referrer, COUNT(*) as c FROM hits WHERE ts >= ? AND referrer != '' GROUP BY referrer ORDER BY c DESC LIMIT 20",
                (cutoff,),
            ).fetchall()

            by_utm = conn.execute(
                "SELECT utm_source, utm_campaign, COUNT(*) as c FROM hits WHERE ts >= ? AND utm_source != '' GROUP BY utm_source, utm_campaign ORDER BY c DESC",
                (cutoff,),
            ).fetchall()

            by_day = conn.execute(
                "SELECT DATE(ts) as day, COUNT(*) as c, COUNT(DISTINCT visitor) as u FROM hits WHERE ts >= ? GROUP BY DATE(ts) ORDER BY day",
                (cutoff,),
            ).fetchall()

            return {
                "period_days": days,
                "total_hits": total,
                "unique_visitors": unique,
                "by_path": [{"path": r["path"], "hits": r["c"]} for r in by_path],
                "by_referrer": [{"referrer": r["referrer"], "hits": r["c"]} for r in by_referrer],
                "by_utm": [{"source": r["utm_source"], "campaign": r["utm_campaign"], "hits": r["c"]} for r in by_utm],
                "by_day": [{"date": r["day"], "hits": r["c"], "unique": r["u"]} for r in by_day],
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key, timestamp, ttl FROM cache")
            rows = cursor.fetchall()

            stats = {
                "total_entries": len(rows),
                "entries": {}
            }

            for key, timestamp_str, ttl in rows:
                cached_time = datetime.fromisoformat(timestamp_str)
                age = datetime.now() - cached_time
                expires_in = timedelta(seconds=ttl) - age

                stats["entries"][key] = {
                    "age_seconds": age.total_seconds(),
                    "age_human": _format_timedelta(age),
                    "expires_in_seconds": max(0, expires_in.total_seconds()),
                    "expires_in_human": _format_timedelta(expires_in) if expires_in.total_seconds() > 0 else "expired"
                }

            return stats


def _format_timedelta(td: timedelta) -> str:
    """Format timedelta as human-readable string."""
    total_seconds = int(td.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes}m"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
