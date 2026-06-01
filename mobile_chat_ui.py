"""Mobile Lab — Chat estilo WhatsApp Business (ministério IBBJ)."""

from __future__ import annotations

import html
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from app_runtime import import_from_main_app
from chat_runtime import (
    CHAT_AUDIO_DIR,
    CHAT_IMAGES_DIR,
    is_user_viewing_chat_mobile,
    load_chat_df_live,
    pending_text_key,
)
from chat_ui import (
    CHAT_LIST_TABS,
    GROUP_CHAT_SUB,
    GROUP_CHAT_TITLE,
    chat_page_css,
    count_chat_media,
    last_group_preview,
    render_chat_page_close,
    render_chat_page_open,
    render_conv_items_after_search,
    render_info_panel_html,
    role_badge_meta,
)
from chat_whatsapp import mark_chat_scroll_bottom
from mobile_chat_whatsapp import (
    inject_wa_list_conv_styles,
    render_wa_list_header_html,
    render_wa_mobile_messages,
    render_wa_thread_header_html,
    wa_mobile_chat_css,
)
from mobile_lab_ui import inject_mobile_lab_theme
from notification_badge import notification_badge_css

_CHAT_VIEWS = frozenset({"list", "thread", "info", "stats"})


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _chat_view() -> str:
    if "ml_chat_view" not in st.session_state:
        st.session_state.ml_chat_view = "thread"
    v = str(st.session_state.get("ml_chat_view", "thread")).strip()
    return v if v in _CHAT_VIEWS else "thread"


def _set_chat_view(view: str) -> None:
    if view in _CHAT_VIEWS:
        st.session_state.ml_chat_view = view


def mobile_chat_css() -> str:
    return (
        notification_badge_css()
        + chat_page_css()
        + wa_mobile_chat_css()
        + r"""
    body:has(#ml-chat-page) .ig-chat-header,
    body:has(#ml-chat-page) .ml-chat-topbar { display: none !important; }
    body:has(#ml-chat-page) .ml-chat-thread-shell { display: none !important; }
    body:has(#ml-chat-page) .ml-chat-quick-row { display: none !important; }
    body:has(#ml-chat-page) #ml-chat-page > p { display: none !important; }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_open_equipe"] .stButton > button {
      border-radius: 0 !important;
      background: var(--wa-header) !important;
      color: var(--wa-text) !important;
      min-height: 3.5rem !important;
      font-weight: 600 !important;
    }
    body:has(#ml-chat-page) [data-testid="stRadio"] > div {
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 0.35rem !important;
      padding: 0 0.5rem !important;
    }
    body:has(#ml-chat-page) [data-testid="stRadio"] label {
      padding: 0.4rem 0.75rem !important;
      border-radius: 999px !important;
      background: #202c33 !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      font-size: 0.78rem !important;
      color: #8696a0 !important;
    }
    body:has(#ml-chat-page) [data-testid="stRadio"] label[data-checked="true"] {
      background: #00a884 !important;
      color: #fff !important;
      border-color: #00a884 !important;
    }
    body:has(#ml-chat-page) [data-testid="stTextInput"] input {
      background: #202c33 !important;
      border: none !important;
      border-radius: 8px !important;
      color: #e9edef !important;
    }
    """
    )


def _render_list_view(
    *,
    preview: str,
    prev_time: str,
    unread: int,
    n_members: int,
    chat_df: pd.DataFrame,
) -> None:
    st.markdown(
        render_wa_list_header_html(),
        unsafe_allow_html=True,
    )

    list_tab = st.radio(
        "Filtro",
        list(CHAT_LIST_TABS),
        horizontal=True,
        label_visibility="collapsed",
        key="ml_chat_list_tab",
    )
    st.text_input(
        "Buscar",
        placeholder="Buscar conversas ou mensagens...",
        key="ml_chat_search_conv",
        label_visibility="collapsed",
    )

    inject_wa_list_conv_styles()
    render_conv_items_after_search(
        preview=preview,
        time_str=prev_time,
        unread=unread,
        list_tab=list_tab,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    label = GROUP_CHAT_TITLE
    if unread > 0:
        label += f" · {unread} não lida(s)"
    if st.button(
        f"💬 {label}",
        key="ml_chat_open_equipe_btn",
        type="primary",
        use_container_width=True,
    ):
        _set_chat_view("thread")
        mark_chat_scroll_bottom()
        st.rerun()


@st.fragment(run_every=timedelta(seconds=4))
def _ml_chat_feed_fragment(members_df: pd.DataFrame) -> None:
    """Histórico ao vivo — sem importar app.py (evita AttributeError no Cloud)."""
    try:
        chat_df = load_chat_df_live()
    except Exception:
        chat_df = st.session_state.get("_chat_df_cache")
        if chat_df is None:
            chat_df = pd.DataFrame()

    st.session_state["_chat_df_cache"] = chat_df
    if is_user_viewing_chat_mobile():
        st.session_state.chat_unread_count = 0

    st.markdown('<div class="ml-chat-feed-area">', unsafe_allow_html=True)
    render_wa_mobile_messages(chat_df, members_df)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_chat_composer_bar() -> None:
    bundle = st.session_state.get("_ml_chat_bundle") or {}
    append_chat_message = bundle.get("append_chat_message")
    render_chat_composer = bundle.get("render_chat_composer")
    if not append_chat_message or not render_chat_composer:
        return

    def _append(**kwargs):
        append_chat_message(**kwargs)

    with st.container(key="ml_chat_composer"):
        render_chat_composer(
            key_prefix="group_chat",
            append_fn=_append,
            audio_dir=CHAT_AUDIO_DIR,
            audio_prefix="chat",
            images_dir=CHAT_IMAGES_DIR,
            image_prefix="chat",
        )


def _render_thread_view(members_df: pd.DataFrame) -> None:
    n = len(members_df) if members_df is not None else 0
    online = f"{min(6, n)} online" if n else "Grupo oficial"

    c_back, c_head, c_info = st.columns([0.5, 5, 0.5])
    with c_back:
        with st.container(key="ml_chat_back"):
            if st.button("←", key="ml_chat_back_btn", help="Conversas"):
                _set_chat_view("list")
                st.rerun()
    with c_head:
        st.markdown(
            render_wa_thread_header_html(member_count=n, online_hint=online),
            unsafe_allow_html=True,
        )
    with c_info:
        with st.container(key="ml_chat_info_btn"):
            if st.button("ℹ️", key="ml_chat_info_open", help="Informações do grupo"):
                _set_chat_view("info")
                st.rerun()

    st.markdown('<div class="wa-thread-layout">', unsafe_allow_html=True)
    _ml_chat_feed_fragment(members_df)
    st.markdown("</div>", unsafe_allow_html=True)
    _render_chat_composer_bar()


def _render_info_view(
    members_df: pd.DataFrame,
    *,
    imgs: int,
    auds: int,
) -> None:
    member_display_name, member_photo_html, members_visible_to_group = (
        import_from_main_app(
            "member_display_name",
            "member_photo_html",
            "members_visible_to_group",
        )
    )

    c_back, _ = st.columns([0.7, 5.3])
    with c_back:
        with st.container(key="ml_chat_back"):
            if st.button("←", key="ml_chat_info_back_list", help="Voltar"):
                _set_chat_view("thread")
                st.rerun()
    st.markdown(
        f'<h2 style="margin:0 0 0.75rem;font-size:1.2rem;color:#e9edef;">Informações</h2>',
        unsafe_allow_html=True,
    )

    member_rows: list[tuple[str, str, str, str]] = []
    visible = members_visible_to_group(members_df)
    online_n = min(6, len(visible)) if not visible.empty else 0
    if not visible.empty:
        for _, row in visible.sort_values(
            by=["first_name", "last_name"],
            key=lambda s: s.str.lower(),
        ).head(12).iterrows():
            email = str(row["email"]).strip().lower()
            nome = member_display_name(row)
            rl, rc = role_badge_meta(str(row.get("roles", "")))
            av = member_photo_html(email, members_df, 28)
            member_rows.append((av, nome, rl, rc))

    st.markdown('<div class="ml-chat-info-shell">', unsafe_allow_html=True)
    render_info_panel_html(
        member_rows,
        media_images=imgs,
        media_audio=auds,
        online_label=str(online_n) if online_n else "0",
    )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_stats_view(
    *,
    n_members: int,
    unread: int,
    chat_df: pd.DataFrame,
) -> None:
    c_back, _ = st.columns([0.7, 5.3])
    with c_back:
        with st.container(key="ml_chat_back"):
            if st.button("←", key="ml_chat_stats_back", help="Voltar"):
                _set_chat_view("list")
                st.rerun()

    today = datetime.now().date()
    n_today = 0
    if chat_df is not None and not chat_df.empty:
        try:
            ts = pd.to_datetime(chat_df["timestamp"], errors="coerce")
            n_today = int((ts.dt.date == today).sum())
        except Exception:
            n_today = 0

    st.markdown(
        f"""
        <div class="ml-chat-stat-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0.75rem 0;">
          <div class="ml-chat-stat" style="padding:12px;border-radius:12px;background:#202c33;">
            <strong style="color:#e9edef;font-size:1.1rem;">{n_members}</strong>
            <span style="font-size:0.68rem;color:#8696a0;">Integrantes</span>
          </div>
          <div class="ml-chat-stat" style="padding:12px;border-radius:12px;background:#202c33;">
            <strong style="color:#e9edef;font-size:1.1rem;">{unread}</strong>
            <span style="font-size:0.68rem;color:#8696a0;">Não lidas</span>
          </div>
          <div class="ml-chat-stat" style="padding:12px;border-radius:12px;background:#202c33;">
            <strong style="color:#e9edef;font-size:1.1rem;">{n_today}</strong>
            <span style="font-size:0.68rem;color:#8696a0;">Hoje</span>
          </div>
          <div class="ml-chat-stat" style="padding:12px;border-radius:12px;background:#202c33;">
            <strong style="color:#e9edef;font-size:1.1rem;">1</strong>
            <span style="font-size:0.68rem;color:#8696a0;">Grupo oficial</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Abrir conversa", type="primary", use_container_width=True):
        _set_chat_view("thread")
        mark_chat_scroll_bottom()
        st.rerun()


def render_mobile_chat_page(chat_df: pd.DataFrame, members_df: pd.DataFrame) -> None:
    try:
        (
            append_chat_message,
            count_unread_chat_messages,
            load_chat_df,
            mark_chat_seen,
            members_visible_to_group,
        ) = import_from_main_app(
            "append_chat_message",
            "count_unread_chat_messages",
            "load_chat_df",
            "mark_chat_seen",
            "members_visible_to_group",
        )
        render_chat_composer = import_from_main_app("render_chat_composer")[0]
    except (ImportError, AttributeError):
        append_chat_message = None
        count_unread_chat_messages = lambda _df=None: 0
        load_chat_df = load_chat_df_live
        mark_chat_seen = lambda _df: None
        members_visible_to_group = lambda m: m
        render_chat_composer = None

    st.session_state["_ml_chat_bundle"] = {
        "append_chat_message": append_chat_message,
        "render_chat_composer": render_chat_composer,
    }

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_chat_css()}</style>", unsafe_allow_html=True)

    pending_key = pending_text_key("group_chat")
    pending = st.session_state.pop(pending_key, None)
    if pending and str(pending).strip() and append_chat_message:
        append_chat_message(message=str(pending).strip(), message_type="text", media_file="")
        mark_chat_scroll_bottom()

    try:
        chat_df = load_chat_df()
    except Exception:
        chat_df = load_chat_df_live()
    st.session_state["_chat_df_cache"] = chat_df
    if _chat_view() == "thread":
        mark_chat_seen(chat_df)
    unread = count_unread_chat_messages(chat_df)
    preview, prev_time = last_group_preview(chat_df)
    n_members = len(members_visible_to_group(members_df))
    imgs, auds, _ = count_chat_media(chat_df)

    render_chat_page_open()
    st.markdown(
        '<div id="ml-chat-page" class="ml-page wa-chat-page"></div>',
        unsafe_allow_html=True,
    )

    view = _chat_view()
    if view == "thread":
        _render_thread_view(members_df)
    elif view == "info":
        _render_info_view(members_df, imgs=imgs, auds=auds)
    elif view == "stats":
        _render_stats_view(n_members=n_members, unread=unread, chat_df=chat_df)
    else:
        st.markdown('<div class="wa-chat-list-view">', unsafe_allow_html=True)
        _render_list_view(
            preview=preview,
            prev_time=prev_time,
            unread=unread,
            n_members=n_members,
            chat_df=chat_df,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    render_chat_page_close()
