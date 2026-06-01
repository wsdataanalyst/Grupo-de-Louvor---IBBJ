"""Funções de chat sem importar app.py (fragments / mobile lab)."""

from __future__ import annotations

import base64
import io
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from chat_media import media_absolute_path

DATA_DIR = Path("data")


def is_user_viewing_chat_mobile() -> bool:
    """Usuário na tela ativa do chat mobile (thread)."""
    try:
        from mobile_lab import is_mobile_lab_enabled

        if not is_mobile_lab_enabled():
            return False
        if str(st.session_state.get("ml_page", "")).strip() != "Chat":
            return False
        return str(st.session_state.get("ml_chat_view", "thread")).strip() == "thread"
    except Exception:
        return False


def sort_chat_messages(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    from app_time import LOCAL_TZ, parse_timestamp

    out = df.copy().reset_index(drop=True)
    keys: list[tuple[datetime, int]] = []
    for i, row in out.iterrows():
        ts = parse_timestamp(str(row.get("timestamp", "")))
        if ts is None:
            keys.append((datetime(1970, 1, 1, tzinfo=LOCAL_TZ), int(i)))
        else:
            keys.append((ts, int(i)))
    keys.sort()
    order = [i for _, i in keys]
    return out.iloc[order].reset_index(drop=True)


def chat_media_html(mtype: str, media_file: str, *, data_dir: Path | None = None) -> str:
    """HTML de imagem/áudio para bolhas do chat (sem depender de app.py)."""
    root = data_dir or DATA_DIR
    path = media_absolute_path(str(media_file).strip(), root)
    if not path:
        return '<p class="chat-text"><em>Mídia indisponível</em></p>'
    try:
        size = path.stat().st_size
    except OSError:
        return '<p class="chat-text"><em>Mídia indisponível</em></p>'
    if mtype == "image":
        if size > 900_000:
            return '<p class="chat-text">📷 Foto</p>'
        try:
            from PIL import Image

            img = Image.open(path).convert("RGB")
            img.thumbnail((720, 720))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=82)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return (
                f'<img class="wa-media-img" src="data:image/jpeg;base64,{b64}" alt="foto" />'
            )
        except Exception:
            return '<p class="chat-text">📷 Foto</p>'
    if mtype == "audio":
        if size > 2_000_000:
            return '<p class="chat-text">🎤 Áudio</p>'
        ext = path.suffix.lower()
        mime = {
            ".webm": "audio/webm",
            ".ogg": "audio/ogg",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".wav": "audio/wav",
        }.get(ext, "audio/webm")
        b64 = base64.b64encode(path.read_bytes()).decode()
        return (
            f'<audio controls preload="metadata" style="width:min(100%,280px);">'
            f'<source src="data:{mime};base64,{b64}" type="{mime}"></audio>'
        )
    return ""
