"""Mobile Lab — Central de conversas estilo WhatsApp (ministério IBBJ)."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

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
    render_thread_header_html,
    role_badge_meta,
)
from chat_whatsapp import mark_chat_scroll_bottom
from mobile_lab_ui import inject_mobile_lab_theme

_CHAT_VIEWS = frozenset({"list", "thread", "info", "stats"})

QUICK_REPLIES: tuple[str, ...] = (
    "Combinado! ✅",
    "Estou a caminho do ensaio",
    "Não poderei estar desta vez",
    "Vou conferir na escala",
    "Obrigado pela informação!",
)


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _chat_view() -> str:
    v = str(st.session_state.get("ml_chat_view", "list")).strip()
    return v if v in _CHAT_VIEWS else "list"


def _set_chat_view(view: str) -> None:
    if view in _CHAT_VIEWS:
        st.session_state.ml_chat_view = view


def mobile_chat_css() -> str:
    return (
        chat_page_css()
        + r"""
    body:has(#ml-chat-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.2rem !important;
      padding-bottom: 7.25rem !important;
      max-width: 100% !important;
    }
    body:has(#ml-chat-page) .ig-chat-header{ display: none !important; }
    body:has(#ml-chat-page) .ig-chat-page{ max-width: 100%; }
    body:has(#ml-chat-page) .ml-chat-ticker{
      overflow: hidden;
      margin: 0 0 0.65rem;
      padding: 8px 12px;
      border-radius: 14px;
      background: rgba(30,58,138,.35);
      border: 1px solid rgba(59,130,246,.25);
    }
    body:has(#ml-chat-page) .ml-chat-ticker-track{
      display: inline-flex;
      gap: 2.5rem;
      white-space: nowrap;
      animation: ml-chat-ticker 28s linear infinite;
    }
    @keyframes ml-chat-ticker{
      from { transform: translateX(0); }
      to { transform: translateX(-50%); }
    }
    body:has(#ml-chat-page) .ml-chat-topbar{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 0.65rem;
    }
    body:has(#ml-chat-page) .ml-chat-topbar h1{
      margin: 0;
      font-size: 1.35rem;
      font-weight: 800;
      color: #f8fafc;
      flex: 1;
    }
    body:has(#ml-chat-page) .ml-chat-stat-grid{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 0.75rem;
    }
    body:has(#ml-chat-page) .ml-chat-stat{
      padding: 10px 12px;
      border-radius: 16px;
      background: rgba(15,23,42,.78);
      border: 1px solid rgba(255,255,255,.08);
    }
    body:has(#ml-chat-page) .ml-chat-stat strong{
      display: block;
      font-size: 1.1rem;
      color: #f8fafc;
    }
    body:has(#ml-chat-page) .ml-chat-stat span{
      font-size: 0.68rem;
      color: #94a3b8;
    }
    body:has(#ml-chat-page) .ml-chat-list-shell{
      border-radius: 18px;
      background: rgba(8,17,32,.88);
      border: 1px solid rgba(255,255,255,.07);
      overflow: hidden;
      margin-bottom: 0.5rem;
    }
    body:has(#ml-chat-page) .ml-chat-list-shell .ig-chat-tabs{
      padding-top: 0.5rem;
    }
    body:has(#ml-chat-page) .ml-chat-list-shell .ig-chat-conv-list{
      max-height: 38vh;
      overflow-y: auto;
    }
    body:has(#ml-chat-page) .ml-chat-thread-shell{
      border-radius: 18px;
      background: rgba(3,7,18,.65);
      border: 1px solid rgba(255,255,255,.08);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      min-height: calc(100vh - 220px);
      max-height: calc(100vh - 200px);
    }
    body:has(#ml-chat-page) .ml-chat-thread-shell .ig-chat-thread-head{
      flex-shrink: 0;
    }
    body:has(#ml-chat-page) .ml-chat-thread-shell #chat-scroll-box.ig-chat-feed{
      flex: 1;
      min-height: 0;
      max-height: none;
      overflow-y: auto !important;
      -webkit-overflow-scrolling: touch;
    }
    body:has(#ml-chat-page) .ml-chat-thread-shell .ig-chat-compose-wrap{
      flex-shrink: 0;
      position: sticky;
      bottom: 0;
      z-index: 2;
    }
    body:has(#ml-chat-page) .ml-chat-quick-row{
      display: flex;
      flex-wrap: nowrap;
      gap: 6px;
      overflow-x: auto;
      padding: 0.35rem 0 0.5rem;
      -webkit-overflow-scrolling: touch;
    }
    body:has(#ml-chat-page) .ml-chat-quick-row .stButton > button{
      border-radius: 999px !important;
      min-height: 2rem !important;
      padding: 0.25rem 0.75rem !important;
      font-size: 0.72rem !important;
      white-space: nowrap !important;
      background: rgba(15,23,42,.9) !important;
      border: 1px solid rgba(139,92,246,.35) !important;
      color: #e9d5ff !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_back"] .stButton > button,
    body:has(#ml-chat-page) [class*="st-key-ml_chat_info_btn"] .stButton > button{
      min-height: 2.5rem !important;
      border-radius: 14px !important;
      font-weight: 700 !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_open_"] .stButton > button{
      width: 100% !important;
      min-height: 4.2rem !important;
      text-align: left !important;
      justify-content: flex-start !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      padding: 0 !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_open_"] .stButton > button p{
      display: none !important;
    }
    body:has(#ml-chat-page) .ml-chat-info-shell .ig-chat-col--info{
      min-height: auto;
      border-radius: 18px;
      border: 1px solid rgba(255,255,255,.08);
    }
    body:has(#ml-chat-page) [data-testid="stRadio"] > div{
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 0.35rem !important;
    }
    body:has(#ml-chat-page) [data-testid="stRadio"] label{
      padding: 0.35rem 0.65rem !important;
      border-radius: 999px !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      font-size: 0.72rem !important;
    }
    body:has(#ml-chat-page) [data-testid="stRadio"] label[data-checked="true"]{
      background: rgba(124,58,237,.45) !important;
      border-color: rgba(139,92,246,.5) !important;
      color: #fff !important;
    }
    """
    )


def _ticker_line() -> str:
    parts: list[str] = []
    try:
        from verse_of_day import verse_for_date

        v = verse_for_date()
        txt = str(v.get("text", "")).strip()
        ref = str(v.get("ref", "")).strip()
        if txt:
            parts.append(f"📖 {txt}" + (f" — {ref}" if ref else ""))
    except Exception:
        pass
    parts.extend(
        [
            "💬 Respeite a equipe nas mensagens do grupo",
            "📅 Confira ensaios e cultos em Escalas",
            "🎵 Dúvidas sobre música? Use Sugestões de louvor",
        ]
    )
    line = "   •   ".join(parts)
    safe = _esc(line)
    return (
        f'<div class="ml-chat-ticker" role="marquee">'
        f'<div class="ml-chat-ticker-track">'
        f'<span>{safe}</span><span aria-hidden="true">{safe}</span>'
        f"</div></div>"
    )


def _render_topbar(*, title: str, show_back: bool = False) -> None:
    c_back, c_title, c_act = st.columns([1, 4, 1])
    with c_back:
        if show_back:
            with st.container(key="ml_chat_back"):
                if st.button("←", key="ml_chat_back_btn", help="Voltar"):
                    _set_chat_view("list")
                    st.rerun()
    with c_title:
        st.markdown(
            f'<div class="ml-chat-topbar"><h1>{_esc(title)}</h1></div>',
            unsafe_allow_html=True,
        )
    with c_act:
        if _chat_view() == "thread":
            with st.container(key="ml_chat_info_btn"):
                if st.button("ℹ️", key="ml_chat_info_open", help="Informações"):
                    _set_chat_view("info")
                    st.rerun()


def _render_stats_row(*, n_members: int, unread: int, n_msgs: int) -> None:
    st.markdown(
        f"""
        <div class="ml-chat-stat-grid">
          <div class="ml-chat-stat"><strong>{n_members}</strong><span>Integrantes</span></div>
          <div class="ml-chat-stat"><strong>{unread}</strong><span>Não lidas</span></div>
          <div class="ml-chat-stat"><strong>{n_msgs}</strong><span>Mensagens</span></div>
          <div class="ml-chat-stat"><strong>{min(6, n_members)}</strong><span>Online agora*</span></div>
        </div>
        <p style="font-size:0.62rem;color:#64748b;margin:-0.35rem 0 0.5rem;">*estimativa visual</p>
        """,
        unsafe_allow_html=True,
    )


def _render_list_view(
    *,
    preview: str,
    prev_time: str,
    unread: int,
    n_members: int,
    chat_df: pd.DataFrame,
) -> None:
    _render_topbar(title="Conversas", show_back=False)
    st.markdown(_ticker_line(), unsafe_allow_html=True)

    n_msgs = len(chat_df) if chat_df is not None and not chat_df.empty else 0
    _render_stats_row(n_members=n_members, unread=unread, n_msgs=n_msgs)

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

    st.markdown('<div class="ml-chat-list-shell">', unsafe_allow_html=True)
    render_conv_items_after_search(
        preview=preview,
        time_str=prev_time,
        unread=unread,
        list_tab=list_tab,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    label = f"💬 Abrir — {GROUP_CHAT_TITLE}"
    if unread > 0:
        label += f" ({unread} nova(s))"
    if st.button(label, key="ml_chat_open_equipe_btn", type="primary", use_container_width=True):
        _set_chat_view("thread")
        st.rerun()

    if st.button("📊 Resumo do atendimento", key="ml_chat_go_stats", use_container_width=True):
        _set_chat_view("stats")
        st.rerun()


def _render_quick_replies(*, key_prefix: str) -> None:
    st.markdown('<div class="ml-chat-quick-row">', unsafe_allow_html=True)
    cols = st.columns(len(QUICK_REPLIES))
    for i, (col, text) in enumerate(zip(cols, QUICK_REPLIES)):
        with col:
            if st.button(text, key=f"ml_chat_qr_{key_prefix}_{i}"):
                st.session_state[f"{key_prefix}_pending_text"] = text
                mark_chat_scroll_bottom()
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_thread_view(members_df: pd.DataFrame) -> None:
    from app import _chat_group_live

    _render_topbar(title=GROUP_CHAT_TITLE, show_back=True)
    st.markdown('<div class="ml-chat-thread-shell">', unsafe_allow_html=True)
    render_thread_header_html(len(members_df) if members_df is not None else 0)
    _render_quick_replies(key_prefix="group_chat")
    _chat_group_live(members_df, premium=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_info_view(
    members_df: pd.DataFrame,
    *,
    imgs: int,
    auds: int,
) -> None:
    from app import member_display_name, member_photo_html, members_visible_to_group

    _render_topbar(title="Informações", show_back=True)
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

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    if not visible.empty and "email" in visible.columns:
        me = visible[visible["email"].astype(str).str.lower() == my_email]
        if not me.empty:
            r = me.iloc[0]
            st.markdown("#### Seu cadastro no grupo")
            st.caption(f"**E-mail:** {r.get('email', '')}")
            phone = str(r.get("phone", "")).strip()
            if phone:
                st.caption(f"**WhatsApp / telefone:** {phone}")
            bio = str(r.get("bio", "")).strip()
            if bio:
                st.caption(f"**Sobre:** {bio}")

    if st.button("← Voltar ao chat", key="ml_chat_info_back_thread", use_container_width=True):
        _set_chat_view("thread")
        st.rerun()


def _render_stats_view(
    *,
    n_members: int,
    unread: int,
    chat_df: pd.DataFrame,
) -> None:
    _render_topbar(title="Resumo", show_back=True)
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
        <div class="ml-chat-stat-grid">
          <div class="ml-chat-stat"><strong>{n_members}</strong><span>Integrantes ativos</span></div>
          <div class="ml-chat-stat"><strong>{unread}</strong><span>Mensagens não lidas</span></div>
          <div class="ml-chat-stat"><strong>{n_today}</strong><span>Mensagens hoje</span></div>
          <div class="ml-chat-stat"><strong>1</strong><span>Grupo oficial</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Central de conversas do **ministério de louvor**. "
        "Use o grupo **Equipe de Louvor** para avisos de ensaio, culto e alinhamentos. "
        "Anexe fotos, PDFs e áudios pelo botão ➕ na conversa."
    )
    if st.button("Abrir Equipe de Louvor", type="primary", use_container_width=True):
        _set_chat_view("thread")
        st.rerun()
    if st.button("← Voltar", use_container_width=True):
        _set_chat_view("list")
        st.rerun()


def render_mobile_chat_page(chat_df: pd.DataFrame, members_df: pd.DataFrame) -> None:
    from app import (
        append_chat_message,
        count_unread_chat_messages,
        load_chat_df,
        mark_chat_seen,
        members_visible_to_group,
        pending_text_key,
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
    st.markdown(
        f"""
        <div id="ml-chat-page" class="ml-page">
          <p style="margin:0 0 0.5rem;font-size:0.78rem;color:#94a3b8;">
            Central de conversas · {_esc(GROUP_CHAT_SUB)}
          </p>
        </div>
        """,
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
        _render_list_view(
            preview=preview,
            prev_time=prev_time,
            unread=unread,
            n_members=n_members,
            chat_df=chat_df,
        )

    render_chat_page_close()
