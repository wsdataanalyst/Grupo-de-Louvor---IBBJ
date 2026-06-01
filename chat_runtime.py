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
CHAT_LIVE_FILE_NAMES = frozenset({"chat.csv"})
_FEED_HTML_KEY = "_wa_feed_html"
_FEED_REV_KEY = "_ml_feed_rev"
_MEDIA_HTML_KEY = "_chat_media_html_cache"


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


def chat_data_revision() -> str:
    """Fingerprint de chat.csv (local ou nuvem) — igual conceito ao app.py."""
    try:
        from remote_store import fetch_sync_revisions, is_remote_enabled

        if is_remote_enabled():
            remote = fetch_sync_revisions(CHAT_LIVE_FILE_NAMES)
            if remote:
                return f"remote:{remote}"
    except Exception:
        pass
    try:
        stat = CHAT_FILE.stat()
        return f"local:{stat.st_mtime_ns}:{stat.st_size}"
    except OSError:
        return "local:missing"


def is_chat_moderator(roles: str | None = None) -> bool:
    """Líder, organizador musical/vocal ou desenvolvedor (mesma regra da escala)."""
    r = str(roles if roles is not None else st.session_state.get("user_roles", ""))
    try:
        from app_runtime import import_from_main_app

        is_scale_manager = import_from_main_app("is_scale_manager")[0]
        return bool(is_scale_manager(r))
    except Exception:
        low = r.lower()
        if "desenvolvedor" in low:
            return True
        if "lider" in low or "líder" in low:
            return True
        if "organizador musical" in low or "organizador vocal" in low:
            return True
        return False


def can_delete_chat_message(
    msg_email: str,
    *,
    roles: str | None = None,
    my_email: str | None = None,
) -> bool:
    """Membro apaga só as próprias; líderes/organizadores apagam qualquer uma."""
    mine = str(my_email or st.session_state.get("user_email", "")).strip().lower()
    target = str(msg_email or "").strip().lower()
    if not target:
        return False
    if mine and mine == target:
        return True
    return is_chat_moderator(roles)


def delete_chat_message_row(timestamp: str, email: str) -> bool:
    """Remove mensagem do CSV (quem chama deve validar permissão antes)."""
    ts = str(timestamp).strip()
    em = str(email).strip().lower()
    if not ts or not em:
        return False
    from data_persistence import load_csv_preserve_rows

    raw = load_csv_preserve_rows(CHAT_FILE, CHAT_COLUMNS)
    df = prepare_chat_df(raw)
    if df.empty:
        return False
    mask = ~(
        (df["timestamp"].astype(str) == ts)
        & (df["email"].astype(str).str.strip().str.lower() == em)
    )
    if len(df[mask]) == len(df):
        return False
    out = df[mask]
    saved = False
    try:
        from app_runtime import import_from_main_app

        save_data = import_from_main_app("save_data")[0]
        saved = bool(save_data(out, CHAT_FILE))
    except Exception:
        saved = False
    if not saved:
        CHAT_FILE.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(CHAT_FILE, index=False)
    st.session_state["_chat_df_cache"] = out
    try:
        st.session_state["_chat_rev"] = chat_data_revision()
    except Exception:
        pass
    invalidate_chat_feed_cache()
    return True


def invalidate_chat_feed_cache() -> None:
    """Força reconstruir HTML do feed após enviar/editar mensagem."""
    st.session_state.pop(_FEED_HTML_KEY, None)
    st.session_state.pop(_FEED_REV_KEY, None)
    try:
        st.session_state["_chat_rev"] = chat_data_revision()
    except Exception:
        pass


def load_chat_df_live(*, force: bool = False) -> pd.DataFrame:
    """Recarrega chat.csv; usa cache de sessão se a revisão não mudou."""
    try:
        new_rev = chat_data_revision()
    except Exception:
        new_rev = ""
    cached = st.session_state.get("_chat_df_cache")
    old_rev = st.session_state.get("_chat_rev")
    if (
        not force
        and cached is not None
        and old_rev is not None
        and new_rev == old_rev
    ):
        return cached

    from data_persistence import load_csv_preserve_rows

    try:
        from remote_store import dataframe_from_remote, is_remote_enabled, should_sync_file

        if should_sync_file(CHAT_FILE) and is_remote_enabled():
            df = dataframe_from_remote(CHAT_COLUMNS, CHAT_FILE.name)
            if df is not None:
                CHAT_FILE.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(CHAT_FILE, index=False)
                out = prepare_chat_df(df)
                st.session_state["_chat_df_cache"] = out
                st.session_state["_chat_rev"] = new_rev
                invalidate_chat_feed_cache()
                return out
    except Exception:
        pass

    raw = load_csv_preserve_rows(CHAT_FILE, CHAT_COLUMNS)
    out = prepare_chat_df(raw)
    st.session_state["_chat_df_cache"] = out
    st.session_state["_chat_rev"] = new_rev
    invalidate_chat_feed_cache()
    return out


def chat_media_html_cached(mtype: str, media_file: str, *, data_dir: Path | None = None) -> str:
    """Cache de miniaturas/base64 — evita reprocessar PIL a cada 4s."""
    rel = str(media_file or "").strip()
    if not rel:
        return chat_media_html(mtype, media_file, data_dir=data_dir)
    key = f"{mtype}:{rel}"
    bag = st.session_state.get(_MEDIA_HTML_KEY)
    if isinstance(bag, dict) and key in bag:
        return bag[key]
    html = chat_media_html(mtype, media_file, data_dir=data_dir)
    if not isinstance(bag, dict):
        bag = {}
    bag[key] = html
    st.session_state[_MEDIA_HTML_KEY] = bag
    return html


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
