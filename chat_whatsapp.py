"""Integração do compositor estilo WhatsApp com o chat Streamlit."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from chat_media import save_audio_upload, save_image_upload
from components.whatsapp_composer import whatsapp_composer


def _payload_id(payload: dict[str, Any]) -> str:
    return str(payload.get("id", "")).strip()


def _already_handled(key_prefix: str, payload: dict[str, Any]) -> bool:
    pid = _payload_id(payload)
    if not pid:
        return True
    state_key = f"{key_prefix}_wa_last_id"
    if st.session_state.get(state_key) == pid:
        return True
    st.session_state[state_key] = pid
    return False


class _BytesUpload:
    """Adapta bytes gravados para save_audio_upload / save_image_upload."""

    def __init__(self, raw: bytes, name: str):
        self._raw = raw
        self.name = name

    def getvalue(self) -> bytes:
        return self._raw


def process_whatsapp_payload(
    payload: dict[str, Any] | None,
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> bool:
    """Processa retorno do componente. True se enviou mensagem."""
    if not payload or not isinstance(payload, dict):
        return False
    if _already_handled(key_prefix, payload):
        return False

    action = str(payload.get("action", "")).strip().lower()
    b64 = str(payload.get("b64", "")).strip()
    text = str(payload.get("text", "")).strip()

    try:
        if action == "text" and text:
            append_fn(message=text, message_type="text", media_file="")
            return True

        if action in ("audio", "audio_file") and b64:
            raw = base64.b64decode(b64)
            ext = str(payload.get("ext", ".webm")).strip() or ".webm"
            if not ext.startswith("."):
                ext = f".{ext}"
            upload = _BytesUpload(raw, f"gravacao{ext}")
            rel = save_audio_upload(
                upload, audio_dir, prefix=audio_prefix, data_dir=data_dir
            )
            append_fn(
                message="🎤 Áudio",
                message_type="audio",
                media_file=rel,
            )
            return True

        if action == "image" and b64:
            raw = base64.b64decode(b64)
            fname = str(payload.get("filename", "foto.jpg"))
            upload = _BytesUpload(raw, fname)
            rel = save_image_upload(
                upload, images_dir, prefix=image_prefix, data_dir=data_dir
            )
            append_fn(
                message="📷 Foto",
                message_type="image",
                media_file=rel,
            )
            return True
    except Exception as exc:
        st.error(f"Não foi possível enviar: {exc}")
        return False

    return False


def render_whatsapp_chat_composer(
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> None:
    """Barra inferior estilo WhatsApp: + anexos, texto, segurar para gravar."""
    st.markdown('<div class="wa-composer-shell">', unsafe_allow_html=True)
    payload = whatsapp_composer(key=key_prefix, default=None)
    if process_whatsapp_payload(
        payload,
        key_prefix=key_prefix,
        append_fn=append_fn,
        audio_dir=audio_dir,
        audio_prefix=audio_prefix,
        images_dir=images_dir,
        image_prefix=image_prefix,
        data_dir=data_dir,
    ):
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
