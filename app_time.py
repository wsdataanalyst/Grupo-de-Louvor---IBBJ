"""Horário local (Brasil) e sessão do usuário."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

LOCAL_TZ = ZoneInfo("America/Sao_Paulo")
SESSION_MINUTES = 20
REMEMBER_EMAIL_KEY = "ibbj_remember_email"


def now_local() -> datetime:
    return datetime.now(LOCAL_TZ)


def timestamp_now() -> str:
    return now_local().strftime("%Y-%m-%d %H:%M:%S.%f")


def parse_timestamp(value: str) -> datetime | None:
    if not value or str(value).strip() in ("", "nan", "NaT"):
        return None
    raw = str(value).strip()
    try:
        if raw[:4].isdigit() and raw[4:5] == "-":
            dt = pd.to_datetime(raw, errors="coerce")
        else:
            dt = pd.to_datetime(raw, dayfirst=True, errors="coerce")
    except Exception:
        return None
    if pd.isna(dt):
        return None
    if hasattr(dt, "to_pydatetime"):
        dt = dt.to_pydatetime()
    if dt.tzinfo is None:
        return dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(LOCAL_TZ)


def normalize_chat_timestamp_str(value) -> str:
    """Gravação uniforme no CSV para ordenação correta do chat."""
    ts = parse_timestamp(str(value))
    if ts:
        return ts.strftime("%Y-%m-%d %H:%M:%S.%f")
    return ""


def to_local_timestamps(values) -> pd.Series:
    """Normaliza timestamps para America/Sao_Paulo (comparações no pandas)."""
    if isinstance(values, pd.Series):
        ts = pd.to_datetime(values, errors="coerce")
    else:
        ts = pd.Series(pd.to_datetime(values, errors="coerce"))
    if not pd.api.types.is_datetime64_any_dtype(ts):
        ts = pd.to_datetime(ts, errors="coerce")
    if ts.dt.tz is None:
        return ts.dt.tz_localize(LOCAL_TZ)
    return ts.dt.tz_convert(LOCAL_TZ)


def format_local(value, fmt: str = "%d/%m/%Y %H:%M") -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, str):
        dt = parse_timestamp(value)
    else:
        try:
            dt = pd.to_datetime(value)
            if hasattr(dt, "to_pydatetime"):
                dt = dt.to_pydatetime()
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=LOCAL_TZ)
            else:
                dt = dt.astimezone(LOCAL_TZ)
        except Exception:
            return ""
    if not dt:
        return ""
    return dt.strftime(fmt)


def session_touch(session_state) -> None:
    session_state.session_expires_at = (
        now_local() + timedelta(minutes=SESSION_MINUTES)
    ).isoformat()


def session_is_valid(session_state) -> bool:
    if not session_state.get("authenticated"):
        return False
    exp_raw = session_state.get("session_expires_at")
    if not exp_raw:
        session_touch(session_state)
        return True
    try:
        exp = datetime.fromisoformat(str(exp_raw))
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=LOCAL_TZ)
    except ValueError:
        session_touch(session_state)
        return True
    if now_local() > exp:
        return False
    session_touch(session_state)
    return True


def session_logout(session_state) -> None:
    for key in (
        "authenticated",
        "user_name",
        "user_full_name",
        "user_email",
        "user_roles",
        "user_primary_role",
        "user_profile_photo",
        "session_expires_at",
        "app_menu",
    ):
        session_state.pop(key, None)
    session_state.authenticated = False
