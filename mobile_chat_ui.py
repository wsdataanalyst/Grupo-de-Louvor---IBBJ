"""Mobile Lab — Chat premium (layout vertical)."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def mobile_chat_css() -> str:
    return r"""
    body:has(#ml-chat-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-chat-page) .ig-chat-header{ display: none !important; }
    body:has(#ml-chat-page) .ig-chat-mobile-order{
      display: block !important;
    }
    body:has(#ml-chat-page) .ig-chat-mobile-order > [data-testid="stHorizontalBlock"]{
      display: none !important;
    }
    body:has(#ml-chat-page) #ml-chat-thread{
      border-radius: 24px;
      padding: 12px;
      background: rgba(15,23,42,.72);
      border: 1px solid rgba(255,255,255,.08);
      margin-bottom: 12px;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_exp_"] [data-testid="stExpander"]{
      border-radius: 20px !important;
      background: rgba(7,18,45,.85) !important;
      border: 1px solid rgba(255,255,255,.06) !important;
    }
    body:has(#ml-chat-page) .stTextInput > div > div > input,
    body:has(#ml-chat-page) [data-testid="stChatInput"] textarea{
      border-radius: 18px !important;
      background: rgba(30,30,30,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      font-size: 16px !important;
    }
    body:has(#ml-chat-page) [data-testid="stTabs"] [data-baseweb="tab-list"]{
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
    }
  """


def _render_header(*, unread: int, n_members: int) -> None:
    badge = (
        f'<span style="margin-left:8px;padding:2px 8px;border-radius:10px;background:#facc15;color:#0f172a;font-size:0.72rem;font-weight:800;">{unread}</span>'
        if unread > 0
        else ""
    )
    st.markdown(
        f"""
        <div id="ml-chat-page" class="ml-page">
          <div class="ml-rep-header-card" style="margin-bottom:0.85rem;">
            <div class="ml-rep-header-icon" style="background:linear-gradient(135deg,#3b82f6,#2563eb);">💬</div>
            <h1 class="ml-rep-header-title" style="font-size:1.5rem;">Chat do ministério</h1>
            <p class="ml-rep-header-sub">Converse com a equipe · {n_members} integrantes{badge}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mobile_chat_page(chat_df: pd.DataFrame, members_df: pd.DataFrame) -> None:
    from app import (
        append_chat_message,
        count_unread_chat_messages,
        load_chat_df,
        mark_chat_seen,
        member_display_name,
        member_photo_html,
        members_visible_to_group,
        pending_text_key,
        _chat_group_live,
    )
    from chat_ui import (
        CHAT_LIST_TABS,
        count_chat_media,
        last_group_preview,
        render_chat_page_close,
        render_chat_page_open,
        render_conv_items_after_search,
        render_info_panel_html,
        render_thread_header_html,
        role_badge_meta,
    )

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_chat_css()}</style>", unsafe_allow_html=True)

    pending_key = pending_text_key("group_chat")
    pending = st.session_state.pop(pending_key, None)
    if pending and str(pending).strip():
        append_chat_message(message=str(pending).strip(), message_type="text", media_file="")

    chat_df = load_chat_df()
    mark_chat_seen(chat_df)
    unread = count_unread_chat_messages(chat_df)
    preview, prev_time = last_group_preview(chat_df)
    n_members = len(members_visible_to_group(members_df))
    imgs, auds, _ = count_chat_media(chat_df)

    render_chat_page_open()
    _render_header(unread=unread, n_members=n_members)

    st.markdown('<div id="ml-chat-thread">', unsafe_allow_html=True)
    render_thread_header_html(n_members)
    _chat_group_live(members_df, premium=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("🔍 Conversas e busca", expanded=False):
        with st.container(key="ml_chat_exp_conv"):
            list_tab = st.radio(
                "Filtro",
                list(CHAT_LIST_TABS),
                horizontal=True,
                label_visibility="collapsed",
                key="ml_chat_list_tab",
            )
            st.text_input(
                "Buscar conversas",
                placeholder="Buscar conversas...",
                key="ml_chat_search_conv",
                label_visibility="collapsed",
            )
            render_conv_items_after_search(
                preview=preview,
                time_str=prev_time,
                unread=unread,
                list_tab=list_tab,
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

    with st.expander("👥 Integrantes e mídia", expanded=False):
        with st.container(key="ml_chat_exp_info"):
            render_info_panel_html(
                member_rows,
                media_images=imgs,
                media_audio=auds,
                online_label=str(online_n) if online_n else "0",
            )

    render_chat_page_close()
