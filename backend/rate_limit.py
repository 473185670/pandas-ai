"""
Simple in-memory IP-based rate limiter.

Free tier: 5 queries/day per IP. For production, swap the dict for Redis
(the interface stays the same). Kept dependency-free for the MVP.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


FREE_TIER_DAILY_LIMIT = 5
# Window in seconds (24h)
WINDOW = 24 * 60 * 60


@dataclass
class _Bucket:
    count: int = 0
    reset_at: float = field(default_factory=lambda: time.time() + WINDOW)


class RateLimiter:
    def __init__(self, limit: int = FREE_TIER_DAILY_LIMIT, window: int = WINDOW):
        self.limit = limit
        self.window = window
        self._buckets: dict[str, _Bucket] = {}

    def check(self, key: str) -> tuple[bool, int, int]:
        """Return (allowed, remaining, seconds_until_reset)."""
        now = time.time()
        bucket = self._buckets.get(key)
        if bucket is None or now >= bucket.reset_at:
            bucket = _Bucket()
            self._buckets[key] = bucket
        if bucket.count >= self.limit:
            return False, 0, int(bucket.reset_at - now)
        bucket.count += 1
        return True, self.limit - bucket.count, int(bucket.reset_at - now)

    def reset(self, key: str) -> None:
        self._buckets.pop(key, None)


# Module-level singleton for the FastAPI app
limiter = RateLimiter()
