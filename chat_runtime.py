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
CHAT_FILE = DATA_DIR / "chat.csv"
CHAT_COLUMNS = ("timestamp", "email", "name", "message", "message_type", "media_file")
CHAT_AUDIO_DIR = DATA_DIR / "chat_audio"
CHAT_IMAGES_DIR = DATA_DIR / "chat_images"


def pending_text_key(key_prefix: str) -> str:
    return f"{key_prefix}_pending_text"


def prepare_chat_df(df: pd.DataFrame) -> pd.DataFrame:
    from app_time import normalize_chat_timestamp_str
    from chat_media import ensure_chat_media_columns

    df = ensure_chat_media_columns(df, CHAT_COLUMNS)
    if df.empty:
        return df
    df = df.copy()
    df["email"] = df["email"].astype(str).str.strip().str.lower()
    df["timestamp"] = df["timestamp"].apply(normalize_chat_timestamp_str)
    df = df[df["timestamp"].astype(str).str.strip() != ""].copy()
    df = df.drop_duplicates(subset=["email", "message", "timestamp"], keep="first")
    return sort_chat_messages(df)


def load_chat_df_live() -> pd.DataFrame:
    """Recarrega chat.csv sem importar app.py (seguro em @st.fragment no Cloud)."""
    from data_persistence import load_csv_preserve_rows

    try:
        from remote_store import dataframe_from_remote, is_remote_enabled, should_sync_file

        if should_sync_file(CHAT_FILE) and is_remote_enabled():
            df = dataframe_from_remote(CHAT_COLUMNS, CHAT_FILE.name)
            if df is not None:
                CHAT_FILE.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(CHAT_FILE, index=False)
                return prepare_chat_df(df)
    except Exception:
        pass

    raw = load_csv_preserve_rows(CHAT_FILE, CHAT_COLUMNS)
    return prepare_chat_df(raw)


def is_user_viewing_chat() -> bool:
    """Desktop (app_menu) ou mobile lab na thread do chat."""
    if str(st.session_state.get("app_menu", "")).strip() == "Chat":
        return True
    return is_user_viewing_chat_mobile()


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
