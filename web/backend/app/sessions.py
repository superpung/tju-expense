"""In-memory store of authenticated TJU sessions, keyed by an opaque token."""
from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass, field

from .tju.client import TJUWebClient


@dataclass
class Session:
    client: TJUWebClient
    created_at: float = field(default_factory=time.time)
    authenticated: bool = False


class SessionStore:
    """Thread-safe token → session map with lazy TTL eviction.

    Sessions live only in memory: restarting the backend logs everyone out, and
    nothing about a user's campus-card credentials is ever persisted to disk.
    """

    def __init__(self, ttl_minutes: int) -> None:
        self._ttl = ttl_minutes * 60
        self._data: dict[str, Session] = {}
        self._lock = threading.Lock()

    def create(self, client: TJUWebClient) -> str:
        token = secrets.token_urlsafe(24)
        with self._lock:
            self._evict()
            self._data[token] = Session(client=client)
        return token

    def get(self, token: str | None) -> Session | None:
        if not token:
            return None
        with self._lock:
            self._evict()
            return self._data.get(token)

    def drop(self, token: str | None) -> None:
        if not token:
            return
        with self._lock:
            self._data.pop(token, None)

    def _evict(self) -> None:
        cutoff = time.time() - self._ttl
        stale = [t for t, s in self._data.items() if s.created_at < cutoff]
        for t in stale:
            del self._data[t]
