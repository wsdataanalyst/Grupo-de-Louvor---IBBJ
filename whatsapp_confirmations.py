"""Helpers para confirmações de escala e links seguros de aprovação."""
from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import quote_plus

CONFIRMATION_EXPIRATION_SECONDS = 24 * 3600


def _normalize_secret(secret: str) -> str:
    return str(secret or "").strip()


def generate_confirmation_token(
    escala_id: str,
    secret: str,
    timestamp: int | None = None,
) -> str:
    ts = int(timestamp if timestamp is not None else time.time())
    payload = f"{escala_id}:{ts}"
    signature = hmac.new(
        _normalize_secret(secret).encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{signature}"


def confirmation_token_is_valid(
    token: str,
    escala_id: str,
    secret: str,
    max_age_seconds: int = CONFIRMATION_EXPIRATION_SECONDS,
) -> bool:
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False
        token_escala_id, ts_str, signature = parts
        if str(token_escala_id) != str(escala_id):
            return False
        timestamp = int(ts_str)
        if time.time() - timestamp > max_age_seconds:
            return False
        expected = hmac.new(
            _normalize_secret(secret).encode("utf-8"),
            f"{token_escala_id}:{timestamp}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False


def build_approval_link(base_url: str, escala_id: str, token: str) -> str:
    query = quote_plus(f"escala_id={escala_id}&token={token}")
    return f"{base_url.rstrip('/')}/approve?{query}"
