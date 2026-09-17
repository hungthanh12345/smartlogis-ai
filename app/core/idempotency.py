# app/core/idempotency.py
"""
Hệ thống Quản lý Tính Bất Biến (Idempotency Management) & Chống Gửi Lặp (Deduplication):
1. Quản lý Idempotency Key với TTL tự động dọn dẹp.
2. Khóa chống race condition đa luồng (Thread-safe lock).
3. Hỗ trợ Debounce Fingerprint chống người dùng click đúp (Double-click) hoặc F5 gửi lặp.
"""

import time
import hashlib
import json
from typing import Optional, Any, Dict
from threading import Lock

class IdempotencyStore:
    def __init__(self, ttl_seconds: int = 600):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._ttl = ttl_seconds

    def _cleanup(self):
        now = time.time()
        expired = [k for k, v in self._store.items() if now - v.get("time", 0) > self._ttl]
        for k in expired:
            del self._store[k]

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._cleanup()
            entry = self._store.get(key)
            if entry and (time.time() - entry.get("time", 0) <= self._ttl):
                return entry.get("data")
            return None

    def set(self, key: str, data: Any):
        with self._lock:
            self._cleanup()
            self._store[key] = {
                "time": time.time(),
                "data": data
            }

    @staticmethod
    def generate_fingerprint(user_id: int, action: str, payload: dict) -> str:
        serialized = json.dumps(payload, sort_keys=True, default=str)
        raw = f"{user_id}:{action}:{serialized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

idempotency_store = IdempotencyStore(ttl_seconds=600)
