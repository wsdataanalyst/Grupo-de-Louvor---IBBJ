"""Notificações push (OneSignal) para chat e novas escalas."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def _secret_get(key: str, default: str = "") -> str:
    try:
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key]).strip()
        push = st.secrets.get("push")
        if push and key in push:
            return str(push[key]).strip()
    except Exception:
        pass
    return default


def push_is_enabled() -> bool:
    flag = _secret_get("push_notifications_enabled", "false").lower()
    has_keys = bool(onesignal_app_id() and _secret_get("onesignal_rest_api_key"))
    if flag in ("1", "true", "sim", "yes", "on"):
        return has_keys
    return has_keys and flag not in ("0", "false", "nao", "no", "off")


def onesignal_app_id() -> str:
    return _secret_get("onesignal_app_id")


def get_public_app_url() -> str:
    url = _secret_get("public_url")
    if url:
        return url.rstrip("/")
    try:
        import os

        url = os.environ.get("PUBLIC_APP_URL", os.environ.get("STREAMLIT_APP_URL", "")).strip()
        return url.rstrip("/")
    except Exception:
        return ""


def push_config_status() -> dict[str, Any]:
    app_id = onesignal_app_id()
    api_key = _secret_get("onesignal_rest_api_key")
    flag = _secret_get("push_notifications_enabled", "false").lower()
    return {
        "enabled": push_is_enabled(),
        "flag": flag,
        "app_id": app_id,
        "app_id_ok": len(app_id) >= 8,
        "has_api_key": bool(api_key),
        "public_url": get_public_app_url(),
        "https_ok": get_public_app_url().lower().startswith("https://"),
    }


def send_push(
    title: str,
    message: str,
    *,
    url: str | None = None,
    extra: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    """Envia push para inscritos. Retorna (sucesso, mensagem)."""
    if not push_is_enabled():
        return False, "Push desativado ou chaves OneSignal ausentes em secrets.toml"

    app_id = onesignal_app_id()
    api_key = _secret_get("onesignal_rest_api_key")
    if not app_id or not api_key:
        return False, "Configure onesignal_app_id e onesignal_rest_api_key"

    payload: dict[str, Any] = {
        "app_id": app_id,
        "included_segments": ["Subscribed Users"],
        "headings": {"en": title, "pt": title},
        "contents": {"en": message, "pt": message},
        "priority": 10,
    }
    target = url or get_public_app_url()
    if target:
        payload["url"] = target
    if extra:
        payload["data"] = extra

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://onesignal.com/api/v1/notifications",
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if 200 <= resp.status < 300:
                return True, body or "Notificação enviada."
            return False, body or f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return False, detail or f"Erro HTTP {exc.code}"
    except Exception as exc:
        return False, str(exc)


def notify_chat_message(author: str, text: str) -> bool:
    ok, _ = send_push(
        "💬 Novas mensagens no chat",
        f"{author} enviou uma nova mensagem no chat do grupo.",
        extra={"type": "chat"},
    )
    return ok


def notify_new_escala(event: str, culto_date: str, responsible: str = "") -> bool:
    msg = f"{culto_date} — {event}".strip(" —")
    if responsible:
        msg = f"{msg}\nResponsável: {responsible}"
    ok, _ = send_push(
        "📅 Nova escala no culto",
        msg,
        extra={"type": "escala"},
    )
    return ok


def send_test_notification() -> tuple[bool, str]:
    return send_push(
        "🎵 Louvor IBBJ",
        "Notificações ativas! Você receberá avisos de chat e novas escalas.",
        extra={"type": "test"},
    )
