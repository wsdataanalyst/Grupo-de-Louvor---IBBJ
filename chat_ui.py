"""Layout premium — Chat do Grupo (IBBJ Louvor v3)."""

from __future__ import annotations

import html
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from ui_html import inject_ui_html

GROUP_CHAT_ID = "equipe_louvor"
GROUP_CHAT_TITLE = "Equipe de Louvor"
GROUP_CHAT_SUB = "Grupo oficial da equipe de louvor da IBBJ."

CHAT_LIST_TABS = ("Conversas", "Grupos", "Não lidas")

# Conversas decorativas (visual mockup; só Equipe de Louvor é funcional)
DECOR_CONVERSATIONS = (
    {
        "id": "vocalistas",
        "title": "Vocalistas",
        "icon": "👥",
        "icon_cls": "ig-chat-av--blue",
        "preview": "Camila: Boa demais!",
        "time": "Ontem",
        "unread": 0,
        "active": False,
    },
    {
        "id": "audio",
        "title": "Ministério de Áudio",
        "icon": "🎧",
        "icon_cls": "ig-chat-av--purple",
        "preview": "Willame: O PA está pronto.",
        "time": "Sex",
        "unread": 0,
        "active": False,
    },
)


def chat_page_css() -> str:
    return """
        [data-testid="stAppViewContainer"]:has(.ig-chat-page) {
            background: #030712 !important;
        }
        [data-testid="stMain"]:has(.ig-chat-page) .block-container {
            padding-top: 0.75rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }
        .ig-chat-page {
            font-family: Manrope, "Segoe UI", sans-serif;
            max-width: 100%;
        }
        .ig-chat-page::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 8% 12%, rgba(37, 99, 235, 0.14), transparent 32%),
                radial-gradient(circle at 92% 88%, rgba(139, 92, 246, 0.12), transparent 30%);
            z-index: 0;
        }
        .ig-chat-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.1rem 1.25rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.78);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.07);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
            position: relative;
            z-index: 1;
        }
        .ig-chat-header-left {
            display: flex;
            align-items: flex-start;
            gap: 0.85rem;
        }
        .ig-chat-header-ico {
            width: 2.55rem;
            height: 2.55rem;
            border-radius: 12px;
            flex-shrink: 0;
            background: rgba(139, 92, 246, 0.42)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23ddd6fe' stroke-width='2'%3E%3Cpath d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'/%3E%3C/svg%3E")
                center/20px no-repeat;
            box-shadow: 0 0 28px rgba(139, 92, 246, 0.45);
        }
        .ig-chat-header-title {
            margin: 0 0 0.12rem;
            font-size: 1.42rem;
            font-weight: 800;
            color: #f8fafc !important;
        }
        .ig-chat-header-sub {
            margin: 0;
            font-size: 0.8rem;
            color: #94a3b8 !important;
        }
        .ig-chat-col {
            border-radius: 14px;
            background: rgba(8, 17, 32, 0.82);
            border: 1px solid rgba(255, 255, 255, 0.06);
            min-height: 72vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
            z-index: 1;
        }
        .ig-chat-col--list {
            background: rgba(8, 17, 32, 0.92);
        }
        .ig-chat-col--main {
            background: rgba(3, 7, 18, 0.65);
        }
        .ig-chat-col--info {
            background: rgba(15, 23, 42, 0.55);
        }
        .ig-chat-tabs {
            display: flex;
            gap: 0;
            padding: 0.65rem 0.75rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }
        .ig-chat-tab {
            flex: 1;
            text-align: center;
            font-size: 0.72rem;
            font-weight: 600;
            color: #64748b !important;
            padding: 0.45rem 0.25rem 0.55rem;
            border-bottom: 2px solid transparent;
            margin-bottom: -1px;
        }
        .ig-chat-tab.is-active {
            color: #c4b5fd !important;
            border-bottom-color: #8b5cf6;
        }
        .ig-chat-search-wrap {
            padding: 0.65rem 0.75rem;
        }
        .ig-chat-conv-list {
            flex: 1;
            overflow-y: auto;
            padding: 0.25rem 0.5rem 0.65rem;
        }
        .ig-chat-conv {
            display: flex;
            align-items: flex-start;
            gap: 0.65rem;
            padding: 0.7rem 0.65rem;
            border-radius: 12px;
            margin-bottom: 0.25rem;
            cursor: default;
            transition: background 0.15s;
        }
        .ig-chat-conv:hover {
            background: rgba(255, 255, 255, 0.04);
        }
        .ig-chat-conv.is-active {
            background: rgba(37, 99, 235, 0.14);
            border: 1px solid rgba(37, 99, 235, 0.35);
        }
        .ig-chat-conv.is-muted {
            opacity: 0.55;
        }
        .ig-chat-av {
            width: 2.35rem;
            height: 2.35rem;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }
        .ig-chat-av--green {
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid rgba(34, 197, 94, 0.35);
        }
        .ig-chat-av--blue {
            background: rgba(37, 99, 235, 0.2);
            border: 1px solid rgba(37, 99, 235, 0.35);
        }
        .ig-chat-av--purple {
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.35);
        }
        .ig-chat-conv-body { flex: 1; min-width: 0; }
        .ig-chat-conv-top {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.35rem;
        }
        .ig-chat-conv-name {
            font-size: 0.8rem;
            font-weight: 700;
            color: #f1f5f9 !important;
        }
        .ig-chat-conv-time {
            font-size: 0.62rem;
            color: #64748b !important;
            flex-shrink: 0;
        }
        .ig-chat-conv-preview {
            margin: 0.15rem 0 0;
            font-size: 0.68rem;
            color: #94a3b8 !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .ig-chat-unread {
            min-width: 1.15rem;
            height: 1.15rem;
            padding: 0 0.3rem;
            border-radius: 999px;
            background: #8b5cf6;
            color: #fff !important;
            font-size: 0.62rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-left: auto;
            flex-shrink: 0;
        }
        .ig-chat-thread-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            padding: 0.85rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            background: rgba(8, 17, 32, 0.9);
        }
        .ig-chat-thread-left {
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }
        .ig-chat-thread-title {
            margin: 0;
            font-size: 0.95rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-chat-thread-meta {
            margin: 0.1rem 0 0;
            font-size: 0.68rem;
            color: #94a3b8 !important;
        }
        .ig-chat-thread-actions {
            display: flex;
            gap: 0.35rem;
        }
        .ig-chat-act-btn {
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.04);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
        }
        #chat-scroll-box.ig-chat-feed {
            flex: 1;
            min-height: 42vh;
            max-height: 52vh;
            overflow-y: auto;
            padding: 1rem 1rem 0.5rem;
            background: transparent !important;
            border: none !important;
        }
        .ig-chat-msg {
            display: flex;
            gap: 0.55rem;
            margin-bottom: 1rem;
            max-width: 88%;
        }
        .ig-chat-msg--me {
            margin-left: auto;
            flex-direction: row-reverse;
        }
        .ig-chat-msg-avatar img,
        .ig-chat-msg-avatar .member-avatar {
            width: 34px !important;
            height: 34px !important;
            border-radius: 50% !important;
        }
        .ig-chat-msg-head {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.35rem;
            margin-bottom: 0.25rem;
        }
        .ig-chat-msg-name {
            font-size: 0.72rem;
            font-weight: 700;
            color: #e2e8f0 !important;
        }
        .ig-chat-msg--me .ig-chat-msg-name { color: #a7f3d0 !important; }
        .ig-chat-role {
            font-size: 0.58rem;
            font-weight: 600;
            padding: 0.1rem 0.4rem;
            border-radius: 6px;
        }
        .ig-chat-role--lider {
            color: #c4b5fd !important;
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.35);
        }
        .ig-chat-role--keys {
            color: #93c5fd !important;
            background: rgba(37, 99, 235, 0.2);
            border: 1px solid rgba(37, 99, 235, 0.35);
        }
        .ig-chat-role--vocal {
            color: #5eead4 !important;
            background: rgba(20, 184, 166, 0.15);
            border: 1px solid rgba(45, 212, 191, 0.35);
        }
        .ig-chat-role--band {
            color: #86efac !important;
            background: rgba(34, 197, 94, 0.12);
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .ig-chat-role--default {
            color: #94a3b8 !important;
            background: rgba(148, 163, 184, 0.12);
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        .ig-chat-bubble {
            padding: 0.65rem 0.85rem;
            border-radius: 14px;
            font-size: 0.8rem;
            line-height: 1.45;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(8px);
            color: #e2e8f0 !important;
        }
        .ig-chat-msg--me .ig-chat-bubble {
            background: linear-gradient(135deg, rgba(23, 143, 136, 0.95), rgba(32, 178, 170, 0.85)) !important;
            border-color: rgba(45, 212, 191, 0.35) !important;
            color: #fff !important;
        }
        .ig-chat-bubble .chat-text { margin: 0; color: inherit !important; }
        .ig-chat-bubble img { max-width: 100%; border-radius: 8px; }
        .ig-chat-bubble audio { width: min(100%, 260px); }
        .ig-chat-seq-card {
            margin-top: 0.35rem;
            padding: 0.65rem 0.75rem;
            border-radius: 12px;
            background: rgba(139, 92, 246, 0.12);
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        .ig-chat-seq-title {
            font-size: 0.78rem;
            font-weight: 700;
            color: #e9d5ff !important;
            margin: 0 0 0.2rem;
        }
        .ig-chat-seq-meta {
            font-size: 0.65rem;
            color: #94a3b8 !important;
            margin: 0;
        }
        .ig-chat-reaction {
            display: inline-flex;
            align-items: center;
            gap: 0.2rem;
            margin-top: 0.35rem;
            padding: 0.12rem 0.45rem;
            border-radius: 999px;
            font-size: 0.62rem;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #cbd5e1 !important;
        }
        .ig-chat-msg-foot {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            margin-top: 0.25rem;
            font-size: 0.62rem;
            color: #64748b !important;
        }
        .ig-chat-read { color: #60a5fa !important; }
        .ig-chat-compose-wrap {
            padding: 0.65rem 0.85rem 0.85rem;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            background: rgba(8, 17, 32, 0.92);
        }
        [data-testid="stMain"]:has(.ig-chat-page) .ig-chat-compose-wrap [data-testid="stChatInput"] {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 14px !important;
        }
        [data-testid="stMain"]:has(.ig-chat-page) .ig-chat-compose-wrap [data-testid="stChatInput"] textarea {
            color: #f1f5f9 !important;
        }
        .ig-chat-info-head {
            text-align: center;
            padding: 1.1rem 0.85rem 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }
        .ig-chat-info-av {
            width: 3.5rem;
            height: 3.5rem;
            margin: 0 auto 0.55rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid rgba(34, 197, 94, 0.35);
        }
        .ig-chat-info-title {
            margin: 0;
            font-size: 0.92rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-chat-info-sub, .ig-chat-info-desc {
            margin: 0.2rem 0 0;
            font-size: 0.68rem;
            color: #94a3b8 !important;
            line-height: 1.4;
        }
        .ig-chat-menu-item {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.55rem 0.85rem;
            font-size: 0.74rem;
            color: #cbd5e1 !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }
        .ig-chat-menu-item span { flex: 1; }
        .ig-chat-menu-meta {
            font-size: 0.62rem;
            color: #64748b !important;
        }
        .ig-chat-members-title {
            padding: 0.65rem 0.85rem 0.35rem;
            font-size: 0.68rem;
            font-weight: 700;
            color: #94a3b8 !important;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .ig-chat-member {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.4rem 0.85rem;
        }
        .ig-chat-member img, .ig-chat-member .member-avatar {
            width: 28px !important;
            height: 28px !important;
            border-radius: 50% !important;
        }
        .ig-chat-member-name {
            font-size: 0.72rem;
            font-weight: 600;
            color: #e2e8f0 !important;
        }
        .ig-chat-leave {
            margin: 0.75rem 0.85rem 1rem;
            text-align: center;
            font-size: 0.72rem;
            color: #f87171 !important;
        }
        [data-testid="stMain"]:has(.ig-chat-page) div[data-testid="column"] > div {
            height: 100%;
        }
        [data-testid="stMain"]:has(.ig-chat-page) .ig-chat-col--list [data-testid="stRadio"] {
            padding: 0.5rem 0.65rem 0 !important;
        }
        [data-testid="stMain"]:has(.ig-chat-page) .ig-chat-col--list [data-testid="stRadio"] label {
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            color: #64748b !important;
        }
        [data-testid="stMain"]:has(.ig-chat-page) .ig-chat-col--list [data-testid="stRadio"] label[data-checked="true"] {
            color: #c4b5fd !important;
        }
        [data-testid="stMain"]:has(.ig-chat-page) .ig-chat-col--list [data-testid="stTextInput"] input {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            color: #f1f5f9 !important;
            font-size: 0.78rem !important;
        }
    """


def render_chat_page_open() -> None:
    inject_ui_html('<div class="ig-chat-page">')


def render_chat_page_close() -> None:
    inject_ui_html("</div>")


def render_chat_header(*, show_new_group: bool = False) -> None:
    btn = ""
    if show_new_group:
        btn = (
            '<span class="ig-chat-new-grp-hint" style="font-size:0.72rem;color:#94a3b8;">'
            "+ Novo grupo (em breve)</span>"
        )
    inject_ui_html(
        f"""
        <div class="ig-chat-header">
            <div class="ig-chat-header-left">
                <div class="ig-chat-header-ico"></div>
                <div>
                    <h1 class="ig-chat-header-title">Chat</h1>
                    <p class="ig-chat-header-sub">Converse com sua equipe e ministério</p>
                </div>
            </div>
            {btn}
        </div>
        """
    )
    if show_new_group:
        st.button(
            "+ Novo grupo",
            key="chat_new_group_btn",
            disabled=True,
            help="Criação de novos grupos em breve.",
        )


def role_badge_meta(roles: str) -> tuple[str, str]:
    """(rótulo, classe CSS) para tag de função."""
    r = str(roles or "").lower()
    if "lider" in r or "líder" in r:
        return "Líder", "lider"
    if "organizador" in r or "org." in r:
        return "Org. Musical", "lider"
    if "vocal" in r:
        return "Vocalista", "vocal"
    if "teclad" in r:
        return "Tecladista", "keys"
    if "guitar" in r:
        return "Guitarrista", "band"
    if "baix" in r:
        return "Baixista", "band"
    if "bater" in r:
        return "Baterista", "band"
    if "viol" in r or "violão" in r:
        return "Violonista", "band"
    if "som" in r or "áudio" in r or "audio" in r:
        return "Áudio", "keys"
    return "Integrante", "default"


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _format_chat_time(ts: object) -> str:
    if ts is None or (isinstance(ts, float) and pd.isna(ts)):
        return ""
    try:
        dt = pd.to_datetime(ts)
        now = datetime.now()
        if dt.date() == now.date():
            return dt.strftime("%H:%M")
        if (now.date() - dt.date()).days == 1:
            return "Ontem"
        return dt.strftime("%d/%m")
    except (ValueError, TypeError):
        return str(ts)[:16]


def last_group_preview(chat_df: pd.DataFrame) -> tuple[str, str]:
    if chat_df is None or chat_df.empty:
        return "Nenhuma mensagem ainda — seja o primeiro!", ""
    try:
        df = chat_df.copy()
        df["_t"] = pd.to_datetime(df["timestamp"], errors="coerce")
        row = df.sort_values("_t").iloc[-1]
    except Exception:
        row = chat_df.iloc[-1]
    name = str(row.get("name", "Integrante")).strip()
    msg = str(row.get("message", "")).strip()
    mtype = str(row.get("message_type", "text") or "text").lower()
    if mtype == "image":
        msg = "📷 Foto"
    elif mtype == "audio":
        msg = "🎤 Áudio"
    preview = f"{name}: {msg}" if msg else f"{name} enviou uma mensagem"
    if len(preview) > 52:
        preview = preview[:49].rstrip() + "…"
    return preview, _format_chat_time(row.get("timestamp"))


def render_conv_list_html(
    *,
    active_id: str,
    preview: str,
    time_str: str,
    unread: int,
    list_tab: str,
) -> None:
    tabs_html = []
    for label in CHAT_LIST_TABS:
        cls = "ig-chat-tab is-active" if label == list_tab else "ig-chat-tab"
        tabs_html.append(f'<span class="{cls}">{_esc(label)}</span>')

    main_unread = f'<span class="ig-chat-unread">{unread}</span>' if unread > 0 else ""
    convs = [
        {
            "id": GROUP_CHAT_ID,
            "title": GROUP_CHAT_TITLE,
            "icon": "🎵",
            "icon_cls": "ig-chat-av--green",
            "preview": preview,
            "time": time_str or "Agora",
            "unread": unread,
            "active": active_id == GROUP_CHAT_ID,
            "muted": False,
        },
    ]
    for d in DECOR_CONVERSATIONS:
        convs.append({**d, "muted": list_tab == "Não lidas"})

    if list_tab == "Grupos":
        convs = [c for c in convs if c["id"] != "vocalistas" or c["id"] == GROUP_CHAT_ID]
    elif list_tab == "Não lidas":
        convs = [c for c in convs if c.get("unread", 0) > 0]
        if not convs:
            convs = [convs[0]] if convs else []

    items = []
    for c in convs:
        active = " is-active" if c.get("active") else ""
        muted = " is-muted" if c.get("muted") and not c.get("active") else ""
        badge = ""
        if c.get("unread", 0) > 0 and c["id"] == GROUP_CHAT_ID:
            n = c["unread"] if c["unread"] <= 99 else "99+"
            badge = f'<span class="ig-chat-unread">{n}</span>'
        items.append(
            f'<div class="ig-chat-conv{active}{muted}">'
            f'<div class="ig-chat-av {c["icon_cls"]}">{c["icon"]}</div>'
            f'<div class="ig-chat-conv-body">'
            f'<div class="ig-chat-conv-top">'
            f'<span class="ig-chat-conv-name">{_esc(c["title"])}</span>'
            f'<span class="ig-chat-conv-time">{_esc(c["time"])}</span>'
            f"{badge}</div>"
            f'<p class="ig-chat-conv-preview">{_esc(c["preview"])}</p>'
            f"</div></div>"
        )

    inject_ui_html(
        f"""
        <div class="ig-chat-col ig-chat-col--list">
            <div class="ig-chat-tabs">{"".join(tabs_html)}</div>
            <div class="ig-chat-conv-list">{"".join(items)}</div>
        </div>
        """
    )


def render_thread_header_html(member_count: int) -> None:
    inject_ui_html(
        f"""
        <div class="ig-chat-thread-head">
            <div class="ig-chat-thread-left">
                <div class="ig-chat-av ig-chat-av--green">🎵</div>
                <div>
                    <p class="ig-chat-thread-title">{_esc(GROUP_CHAT_TITLE)}</p>
                    <p class="ig-chat-thread-meta">{member_count} membros • Grupo</p>
                </div>
            </div>
            <div class="ig-chat-thread-actions">
                <span class="ig-chat-act-btn" title="Chamada de voz">📞</span>
                <span class="ig-chat-act-btn" title="Vídeo">🎥</span>
                <span class="ig-chat-act-btn" title="Informações">ℹ️</span>
            </div>
        </div>
        """
    )


def sequence_card_html(message: str) -> str:
    """Card de sequência de culto quando a mensagem menciona sequência/culto."""
    low = message.lower()
    if "sequência" not in low and "sequencia" not in low:
        return ""
    date_m = re.search(r"(\d{1,2}/\d{1,2})", message)
    date_label = date_m.group(1) if date_m else "próximo culto"
    return (
        f'<div class="ig-chat-seq-card">'
        f'<p class="ig-chat-seq-title">🎵 Sequência — Culto {html.escape(date_label)}</p>'
        f'<p class="ig-chat-seq-meta">Abra Gerenciar Escalas para ver músicas e duração.</p>'
        f"</div>"
    )


def premium_message_html(
    *,
    is_me: bool,
    display_name: str,
    role_label: str,
    role_cls: str,
    time_str: str,
    body_html: str,
    avatar_html: str,
    show_reaction: bool = False,
) -> str:
    side = "ig-chat-msg--me" if is_me else "ig-chat-msg--other"
    read = '<span class="ig-chat-read">✓✓</span>' if is_me else ""
    reaction = (
        '<span class="ig-chat-reaction">👍 1</span>'
        if show_reaction and not is_me
        else ""
    )
    seq = "" if is_me else sequence_card_html(
        re.sub(r"<[^>]+>", "", body_html)
    )
    return (
        f'<div class="ig-chat-msg {side}">'
        f'<div class="ig-chat-msg-avatar">{avatar_html}</div>'
        f'<div class="ig-chat-msg-content">'
        f'<div class="ig-chat-msg-head">'
        f'<span class="ig-chat-msg-name">{_esc(display_name)}</span>'
        f'<span class="ig-chat-role ig-chat-role--{role_cls}">{_esc(role_label)}</span>'
        f"</div>"
        f'<div class="ig-chat-bubble">{body_html}{seq}</div>'
        f"{reaction}"
        f'<div class="ig-chat-msg-foot"><span>{_esc(time_str)}</span>{read}</div>'
        f"</div></div>"
    )


def count_chat_media(chat_df: pd.DataFrame) -> tuple[int, int, int]:
    """(imagens, áudios, total anexos)"""
    if chat_df is None or chat_df.empty:
        return 0, 0, 0
    mt = chat_df.get("message_type", pd.Series(dtype=str)).astype(str).str.lower()
    img = int((mt == "image").sum())
    aud = int((mt == "audio").sum())
    return img, aud, img + aud


def render_info_panel_html(
    members_rows: list[tuple[str, str, str, str]],
    *,
    media_images: int,
    media_audio: int,
    online_label: str,
) -> None:
    menu = (
        ("🔔", "Notificações", ""),
        ("📄", "Arquivos compartilhados", f"{media_images + media_audio} anexos"),
        ("🖼️", "Mídias compartilhadas", f"{media_images} fotos • {media_audio} áudios"),
        ("🔗", "Links compartilhados", "No histórico do grupo"),
    )
    menu_html = "".join(
        f'<div class="ig-chat-menu-item"><span>{ico}</span><span>{_esc(lbl)}</span>'
        f'<span class="ig-chat-menu-meta">{_esc(meta)}</span></div>'
        for ico, lbl, meta in menu
    )
    members_html = "".join(
        f'<div class="ig-chat-member">{av}'
        f'<span class="ig-chat-member-name">{_esc(name)}</span>'
        f'<span class="ig-chat-role ig-chat-role--{cls}">{_esc(role)}</span></div>'
        for av, name, role, cls in members_rows[:8]
    )
    inject_ui_html(
        f"""
        <div class="ig-chat-col ig-chat-col--info">
            <div class="ig-chat-info-head">
                <div class="ig-chat-info-av">🎵</div>
                <p class="ig-chat-info-title">{_esc(GROUP_CHAT_TITLE)}</p>
                <p class="ig-chat-info-sub">{len(members_rows)} membros</p>
                <p class="ig-chat-info-desc">{_esc(GROUP_CHAT_SUB)}</p>
            </div>
            {menu_html}
            <p class="ig-chat-members-title">Membros online ({online_label})</p>
            {members_html}
            <p class="ig-chat-leave">Sair do grupo (em breve)</p>
        </div>
        """
    )


def render_list_column_shell() -> None:
    """Abre coluna esquerda (tabs + busca ficam em widgets Streamlit)."""
    inject_ui_html('<div class="ig-chat-col ig-chat-col--list" style="min-height:72vh;">')


def render_list_column_tabs_active(tab: str) -> None:
    tabs_html = []
    for label in CHAT_LIST_TABS:
        cls = "ig-chat-tab is-active" if label == tab else "ig-chat-tab"
        tabs_html.append(f'<span class="{cls}">{_esc(label)}</span>')
    inject_ui_html(f'<div class="ig-chat-tabs">{"".join(tabs_html)}</div>')


def render_conv_items_after_search(
    *,
    preview: str,
    time_str: str,
    unread: int,
    list_tab: str,
) -> None:
    """Lista de conversas (após campo de busca)."""
    convs = [
        {
            "id": GROUP_CHAT_ID,
            "title": GROUP_CHAT_TITLE,
            "icon": "🎵",
            "icon_cls": "ig-chat-av--green",
            "preview": preview,
            "time": time_str or "Agora",
            "unread": unread,
            "active": True,
            "muted": False,
        },
    ]
    for d in DECOR_CONVERSATIONS:
        convs.append({**d, "active": False, "muted": list_tab == "Não lidas"})

    if list_tab == "Não lidas" and unread <= 0:
        inject_ui_html(
            '<p style="padding:0.75rem;font-size:0.72rem;color:#64748b;">'
            "Nenhuma conversa não lida.</p>"
        )
        return

    items = []
    for c in convs:
        if list_tab == "Não lidas" and c.get("unread", 0) <= 0 and c["id"] != GROUP_CHAT_ID:
            continue
        active = " is-active" if c.get("active") else ""
        muted = " is-muted" if c.get("muted") and not c.get("active") else ""
        badge = ""
        if c.get("unread", 0) > 0 and c["id"] == GROUP_CHAT_ID:
            n = unread if unread <= 99 else "99+"
            badge = f'<span class="ig-chat-unread">{n}</span>'
        items.append(
            f'<div class="ig-chat-conv{active}{muted}">'
            f'<div class="ig-chat-av {c["icon_cls"]}">{c["icon"]}</div>'
            f'<div class="ig-chat-conv-body">'
            f'<div class="ig-chat-conv-top">'
            f'<span class="ig-chat-conv-name">{_esc(c["title"])}</span>'
            f'<span class="ig-chat-conv-time">{_esc(c["time"])}</span>'
            f"{badge}</div>"
            f'<p class="ig-chat-conv-preview">{_esc(c["preview"])}</p>'
            f"</div></div>"
        )
    inject_ui_html(f'<div class="ig-chat-conv-list">{"".join(items)}</div>')
