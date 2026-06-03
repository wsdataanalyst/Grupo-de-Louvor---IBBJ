"""Mobile Lab — Chat do ensaio com layout WA igual ao chat geral."""

from __future__ import annotations

from datetime import timedelta
from urllib.parse import unquote

import pandas as pd
import streamlit as st

from chat_ui import chat_page_css
from chat_whatsapp import mark_chat_scroll_bottom, render_mobile_wa_composer
from mobile_chat_whatsapp import (
    render_wa_mobile_messages,
    render_wa_thread_header_html,
    wa_mobile_chat_css,
)
from mobile_lab_ui import inject_mobile_lab_theme
from notification_badge import notification_badge_css


def _feed_keys(escala_id: str) -> tuple[str, str]:
    eid = str(escala_id)
    return (f"_wa_ensaio_feed_html_{eid}", f"_wa_ensaio_feed_rev_{eid}")


def _ensaio_subset(escala_id: str) -> pd.DataFrame:
    from app import CHAT_ENSAIO_COLUMNS, CHAT_ENSAIO_FILE, load_data, prepare_chat_ensaio

    df = prepare_chat_ensaio(load_data(CHAT_ENSAIO_FILE, CHAT_ENSAIO_COLUMNS))
    return df[df["escala_id"].astype(str) == str(escala_id)].copy()


def _ensaio_rev(escala_id: str, subset: pd.DataFrame) -> str:
    if subset.empty:
        return f"ensaio_{escala_id}_0"
    ts_max = str(subset["timestamp"].astype(str).max())
    return f"ensaio_{escala_id}_{len(subset)}_{ts_max}"


def _process_mobile_ensaio_delete(escala_id: str) -> None:
    raw = st.query_params.get("ml_ensaio_del")
    if not raw:
        return
    if isinstance(raw, list):
        raw = raw[0]
    try:
        del st.query_params["ml_ensaio_del"]
    except Exception:
        pass
    parts = unquote(str(raw)).split("|", 1)
    if len(parts) != 2:
        return
    ts, em = parts[0].strip(), parts[1].strip().lower()
    if not ts or not em:
        return
    from app import delete_own_ensaio_message

    delete_own_ensaio_message(ts, escala_id, em)
    mark_chat_scroll_bottom()
    st.toast("Mensagem apagada.", icon="🗑️")
    st.rerun()


def mobile_ensaio_chat_css() -> str:
    return (
        notification_badge_css()
        + chat_page_css()
        + wa_mobile_chat_css()
        + r"""
    body:has(#ml-ensaio-chat-active) #ml-escalas-page .ml-esc-header,
    body:has(#ml-ensaio-chat-active) [class*="st-key-ml_esc_tabs"],
    body:has(#ml-ensaio-chat-active) .swap-priority-panel {
      display: none !important;
    }
    body:has(#ml-ensaio-chat-active) [data-testid="stCaptionContainer"],
    body:has(#ml-ensaio-chat-active) .stCaption {
      margin-bottom: 0.35rem !important;
    }
    body:has(#ml-ensaio-chat-active) [class*="st-key-ml_ensaio_thread_top"] {
      position: fixed !important;
      top: calc(var(--ml-ensaio-pick-height, 3.5rem) + env(safe-area-inset-top, 0px)) !important;
      left: 0 !important;
      right: 0 !important;
      z-index: 120 !important;
      background: var(--wa-header) !important;
      border-bottom: 1px solid rgba(255,255,255,.08) !important;
      padding: 0.15rem 0.25rem 0.1rem !important;
      margin: 0 !important;
    }
    body:has(#ml-ensaio-chat-active) #ml-ensaio-chat-scroll.wa-chat-feed {
      position: fixed !important;
      top: calc(
        var(--ml-ensaio-pick-height, 3.5rem) + var(--ml-thread-header, 3.25rem)
        + env(safe-area-inset-top, 0px)
      ) !important;
      left: 0 !important;
      right: 0 !important;
      bottom: calc(
        var(--ml-nav-height) + var(--ml-verse-height) + var(--ml-nav-offset)
        + var(--ml-compose-clearance, 5.75rem)
      ) !important;
      width: 100% !important;
      max-width: 100% !important;
      min-height: 0 !important;
      z-index: 50 !important;
      background: var(--wa-bg) !important;
      background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") !important;
      overflow-y: auto !important;
      -webkit-overflow-scrolling: touch !important;
    }
    body:has(#ml-ensaio-chat-active) [class*="st-key-ml_ensaio_feed_wrap"] {
      height: 0 !important;
      min-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: visible !important;
    }
    body:has(#ml-ensaio-chat-active) [class*="st-key-ml_ensaio_composer"] {
      position: fixed !important;
      left: 0 !important;
      right: 0 !important;
      bottom: calc(
        var(--ml-nav-height) + var(--ml-verse-height) + var(--ml-nav-offset)
      ) !important;
      z-index: 130 !important;
      background: var(--wa-compose) !important;
      border-top: 1px solid rgba(255,255,255,.08) !important;
      padding-bottom: env(safe-area-inset-bottom, 0px) !important;
    }
    body:has(#ml-ensaio-chat-active) [class*="st-key-ml_ensaio_pick"] {
      position: fixed !important;
      top: env(safe-area-inset-top, 0px) !important;
      left: 0 !important;
      right: 0 !important;
      z-index: 140 !important;
      background: rgba(11,18,39,.96) !important;
      padding: 0.35rem 0.65rem 0.25rem !important;
      border-bottom: 1px solid rgba(255,255,255,.06) !important;
    }
    """
    )


def _append_ensaio_factory(escala_id: str):
    from app import (
        CHAT_ENSAIO_COLUMNS,
        CHAT_ENSAIO_FILE,
        load_data,
        prepare_chat_ensaio,
        save_data,
        timestamp_now,
    )

    def _append(**kwargs):
        fresh = prepare_chat_ensaio(load_data(CHAT_ENSAIO_FILE, CHAT_ENSAIO_COLUMNS))
        base = {
            "timestamp": timestamp_now(),
            "escala_id": escala_id,
            "email": st.session_state.user_email,
            "name": st.session_state.user_full_name or st.session_state.user_name,
        }
        nova = {**base, **kwargs}
        subset_ids = fresh["escala_id"].astype(str) == str(escala_id)
        others = fresh[~subset_ids] if subset_ids.any() else fresh
        escala_rows = fresh[subset_ids] if subset_ids.any() else pd.DataFrame()
        updated = pd.concat(
            [others, escala_rows, pd.DataFrame([nova])], ignore_index=True
        )
        if save_data(updated, CHAT_ENSAIO_FILE):
            mark_chat_scroll_bottom()
            st.rerun()

    return _append


@st.fragment(run_every=timedelta(seconds=4))
def _ensaio_wa_thread_live(escala_id: str, members_df: pd.DataFrame) -> None:
    from app import CHAT_IMAGES_DIR, DATA_DIR, ENSAIO_AUDIO_DIR

    subset = _ensaio_subset(escala_id)
    html_key, rev_key = _feed_keys(escala_id)
    rev = _ensaio_rev(escala_id, subset)

    with st.container(key="ml_ensaio_feed_wrap"):
        render_wa_mobile_messages(
            subset,
            members_df,
            rev=rev,
            html_key=html_key,
            rev_key=rev_key,
            scroll_box_id="ml-ensaio-chat-scroll",
            delete_query_param="ml_ensaio_del",
            composer_selector='[class*="st-key-ml_ensaio_composer"]',
        )

    append_fn = _append_ensaio_factory(escala_id)
    ensaio_dir = ENSAIO_AUDIO_DIR / str(escala_id)
    ensaio_dir.mkdir(parents=True, exist_ok=True)

    with st.container(key="ml_ensaio_composer"):
        render_mobile_wa_composer(
            key_prefix=f"ensaio_{escala_id}",
            append_fn=append_fn,
            audio_dir=ensaio_dir,
            audio_prefix=f"ensaio_{escala_id}",
            images_dir=CHAT_IMAGES_DIR,
            image_prefix=f"ensaio_{escala_id}",
            data_dir=DATA_DIR,
        )


def render_mobile_ensaio_chat(
    escala_id: str,
    members_df: pd.DataFrame,
    *,
    title: str = "Chat do ensaio",
    subtitle: str = "Equipe deste culto",
) -> None:
    """Thread WA do ensaio — mesmo compositor, feed, scroll e apagar do chat geral."""
    from app import pending_text_key

    st.session_state.ml_ensaio_chat_id = str(escala_id)
    _process_mobile_ensaio_delete(str(escala_id))

    pending_key = pending_text_key(f"ensaio_{escala_id}")
    pending = st.session_state.pop(pending_key, None)
    if pending and str(pending).strip():
        _append_ensaio_factory(escala_id)(
            message=str(pending).strip(), message_type="text", media_file=""
        )
        return

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_ensaio_chat_css()}</style>", unsafe_allow_html=True)
    st.markdown(
        '<span id="ml-ensaio-chat-active" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )

    with st.container(key="ml_ensaio_thread_top"):
        st.markdown(
            render_wa_thread_header_html(
                title=title,
                subtitle=subtitle,
                avatar="🎤",
            ),
            unsafe_allow_html=True,
        )

    _ensaio_wa_thread_live(str(escala_id), members_df)
