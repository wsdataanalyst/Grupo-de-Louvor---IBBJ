"""Sessão persistente no dispositivo (sobrevive a reload e segundo plano)."""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta
from pathlib import Path

import pandas as pd

from app_time import LOCAL_TZ, now_local

AUTH_TOKEN_QUERY_PARAM = "ibbj_auth"
AUTH_TOKEN_LS_KEY = "ibbj_auth_token"

DEVICE_SESSION_COLUMNS = (
    "token_hash",
    "email",
    "created_at",
    "expires_at",
    "last_used_at",
    "revoked_at",
)

# Permanece logado neste aparelho (volta do YouTube, aba em segundo plano, etc.)
DEVICE_SESSION_DAYS = 90


def _session_secret() -> str:
    try:
        import streamlit as st

        auth = st.secrets.get("auth", None)
        if isinstance(auth, dict) and auth.get("device_secret"):
            return str(auth["device_secret"]).strip()
        flat = st.secrets.get("device_secret", None)
        if flat:
            return str(flat).strip()
    except Exception:
        pass
    return "ibbj-louvor-device-session-v1"


def _hash_token(token: str) -> str:
    raw = f"{_session_secret()}:{token.strip()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def device_sessions_path(data_dir: Path) -> Path:
    return data_dir / "device_sessions.csv"


def load_device_sessions(path: Path) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame(columns=list(DEVICE_SESSION_COLUMNS))
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame(columns=list(DEVICE_SESSION_COLUMNS))
    for col in DEVICE_SESSION_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[list(DEVICE_SESSION_COLUMNS)]


def save_device_sessions(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df[list(DEVICE_SESSION_COLUMNS)].to_csv(path, index=False)


def purge_expired_device_sessions(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    now = now_local()
    keep = []
    for _, row in df.iterrows():
        if str(row.get("revoked_at", "")).strip():
            continue
        exp_raw = str(row.get("expires_at", "")).strip()
        if not exp_raw:
            keep.append(True)
            continue
        try:
            exp = pd.to_datetime(exp_raw).to_pydatetime()
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=LOCAL_TZ)
            keep.append(exp >= now)
        except Exception:
            keep.append(True)
    return df.loc[df.index[keep]].copy() if any(keep) else df.iloc[0:0].copy()


def create_device_session_token(email: str, data_dir: Path) -> str:
    """Gera token de uso prolongado neste aparelho."""
    email_l = str(email).strip().lower()
    token = secrets.token_urlsafe(32)
    path = device_sessions_path(data_dir)
    df = purge_expired_device_sessions(load_device_sessions(path))
    now = now_local()
    expires = now + timedelta(days=DEVICE_SESSION_DAYS)
    row = {
        "token_hash": _hash_token(token),
        "email": email_l,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires.strftime("%Y-%m-%d %H:%M:%S"),
        "last_used_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "revoked_at": "",
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_device_sessions(df, path)
    return token


def validate_device_session_token(token: str, data_dir: Path) -> str | None:
    """Retorna e-mail se o token for válido; atualiza last_used_at."""
    token = str(token or "").strip()
    if len(token) < 24:
        return None
    path = device_sessions_path(data_dir)
    df = purge_expired_device_sessions(load_device_sessions(path))
    th = _hash_token(token)
    match = df[df["token_hash"].astype(str) == th]
    if match.empty:
        return None
    idx = match.index[0]
    if str(df.at[idx, "revoked_at"]).strip():
        return None
    email = str(df.at[idx, "email"]).strip().lower()
    if not email:
        return None
    df.at[idx, "last_used_at"] = now_local().strftime("%Y-%m-%d %H:%M:%S")
    save_device_sessions(df, path)
    return email


def revoke_device_session_token(token: str, data_dir: Path) -> None:
    token = str(token or "").strip()
    if len(token) < 24:
        return
    path = device_sessions_path(data_dir)
    df = load_device_sessions(path)
    if df.empty:
        return
    th = _hash_token(token)
    mask = df["token_hash"].astype(str) == th
    if not mask.any():
        return
    df.loc[mask, "revoked_at"] = now_local().strftime("%Y-%m-%d %H:%M:%S")
    save_device_sessions(df, path)
