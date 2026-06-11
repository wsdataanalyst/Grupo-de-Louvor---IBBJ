"""Chat mobile — layout e comportamento estilo WhatsApp Business."""

from __future__ import annotations

import html
from datetime import timedelta

import pandas as pd
import streamlit as st

from chat_runtime import (
    _FEED_HTML_KEY,
    _FEED_REV_KEY,
    chat_media_html_cached,
    sort_chat_messages,
)
from chat_ui import GROUP_CHAT_SUB, GROUP_CHAT_TITLE
from notification_badge import notification_badge_css
from ui_html import inject_page_script, inject_ui_html

_WA_GROUP_AVATAR = "🎵"


def wa_mobile_chat_css() -> str:
    return (
        notification_badge_css()
        + """
    :root {
      --wa-bg: #0b141a;
      --wa-header: #202c33;
      --wa-compose: #202c33;
      --ml-compose-clearance: 5.75rem;
      --ml-thread-header: 3.25rem;
      --wa-bubble-in: #202c33;
      --wa-bubble-out: #005c4b;
      --wa-text: #e9edef;
      --wa-meta: #8696a0;
      --wa-accent: #00a884;
      --wa-unread: #25d366;
    }
    body:has(#ml-chat-page) [data-testid="stAppViewContainer"] .main .block-container {
      padding-top: 0 !important;
      padding-left: 0 !important;
      padding-right: 0 !important;
      padding-bottom: 0 !important;
      max-width: 100% !important;
    }
    body:has(#ml-chat-page) [data-testid="stMain"] > div {
      padding-top: 0 !important;
    }
    #ml-chat-page.wa-chat-thread-shell {
      display: none !important;
      height: 0 !important;
      min-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
    }
    body:has(#ml-chat-page) #chat-scroll-box.wa-chat-feed {
      position: fixed !important;
      top: calc(var(--ml-thread-header) + env(safe-area-inset-top, 0px)) !important;
      left: 0 !important;
      right: 0 !important;
      bottom: calc(
        var(--ml-nav-height) + var(--ml-verse-height) + var(--ml-nav-offset)
        + var(--ml-compose-clearance, 5.75rem)
      ) !important;
      width: 100% !important;
      max-width: 100% !important;
      min-height: 0 !important;
      max-height: none !important;
      height: auto !important;
      z-index: 50 !important;
      background: var(--wa-bg) !important;
      background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_thread_top"] {
      position: fixed !important;
      top: env(safe-area-inset-top, 0px) !important;
      left: 0 !important;
      right: 0 !important;
      z-index: 120 !important;
      background: var(--wa-header) !important;
      border-bottom: 1px solid rgba(255,255,255,.08) !important;
      padding: 0.15rem 0.25rem 0.1rem !important;
      margin: 0 !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_thread_top"] [data-testid="stHorizontalBlock"] {
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      gap: 0 !important;
      margin: 0 !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_thread_top"] [data-testid="stColumn"]:nth-child(1),
    body:has(#ml-chat-page) [class*="st-key-ml_chat_thread_top"] [data-testid="stColumn"]:nth-child(3) {
      flex: 0 0 2.5rem !important;
      width: 2.5rem !important;
      max-width: 2.5rem !important;
      min-width: 2.5rem !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_thread_top"] [data-testid="stColumn"]:nth-child(2) {
      flex: 1 1 auto !important;
      width: auto !important;
      min-width: 0 !important;
      max-width: none !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_feed_wrap"] {
      height: 0 !important;
      min-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: visible !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_feed_wrap"] .ml-chat-feed-area {
      margin: 0 !important;
      padding: 0 !important;
    }
    .wa-chat-list-view {
      padding: 0 0.5rem 0.75rem;
    }
    .wa-chat-list-header {
      background: var(--wa-header);
      padding: 0.85rem 1rem 0.65rem;
      margin: 0 -0.5rem 0.5rem;
      border-bottom: 1px solid rgba(255,255,255,.06);
    }
    .wa-chat-list-header h1 {
      margin: 0;
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--wa-text);
    }
    .wa-chat-list-header p {
      margin: 0.15rem 0 0;
      font-size: 0.72rem;
      color: var(--wa-meta);
    }
    .wa-conv-list {
      background: var(--wa-header);
      border-radius: 0;
      overflow: hidden;
    }
    .wa-conv-list .ig-chat-conv {
      padding: 0.75rem 1rem;
      margin: 0;
      border-radius: 0;
      border-bottom: 1px solid rgba(255,255,255,.04);
      align-items: center;
    }
    .wa-conv-list .ig-chat-conv.is-unread {
      background: rgba(0, 168, 132, 0.08) !important;
      border: none !important;
      border-bottom: 1px solid rgba(255,255,255,.04) !important;
    }
    .wa-conv-list .ig-chat-conv-name {
      color: var(--wa-text) !important;
      font-size: 1rem !important;
    }
    .wa-conv-list .ig-chat-conv-preview {
      color: var(--wa-meta) !important;
      font-size: 0.8rem !important;
    }
    .wa-conv-list .ig-unread-badge--conv {
      background: var(--wa-unread) !important;
      border-color: var(--wa-header) !important;
    }
    .wa-thread-layout {
      display: none;
    }
    .wa-thread-header {
      position: relative;
      z-index: 1;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.45rem 0.65rem;
      background: var(--wa-header);
      border-bottom: 1px solid rgba(255,255,255,.08);
      min-height: 3.25rem;
    }
    .wa-thread-header__avatar {
      width: 2.5rem;
      height: 2.5rem;
      border-radius: 50%;
      background: rgba(0, 168, 132, 0.25);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      flex-shrink: 0;
      overflow: hidden;
    }
    .wa-thread-header__avatar img,
    .wa-thread-header__avatar .member-avatar {
      width: 100% !important;
      height: 100% !important;
      border-radius: 50% !important;
      object-fit: cover;
    }
    .wa-thread-header__body { flex: 1; min-width: 0; }
    .wa-thread-header__title {
      margin: 0;
      font-size: 1rem;
      font-weight: 600;
      color: var(--wa-text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .wa-thread-header__status {
      margin: 0;
      font-size: 0.72rem;
      color: var(--wa-meta);
    }
    .wa-thread-header__status.is-online { color: #25d366; }
    .wa-thread-header__actions {
      display: flex;
      gap: 0.35rem;
      flex-shrink: 0;
    }
    .wa-icon-btn {
      width: 2.25rem;
      height: 2.25rem;
      border: none;
      border-radius: 50%;
      background: transparent;
      color: var(--wa-meta);
      font-size: 1.05rem;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: default;
    }
    .ml-chat-feed-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      position: relative;
    }
    #chat-scroll-box.wa-chat-feed {
      overflow-y: auto !important;
      overflow-x: hidden;
      -webkit-overflow-scrolling: touch;
      scroll-behavior: smooth;
      box-sizing: border-box !important;
      padding: 0.45rem 0.5rem 0.5rem !important;
      margin: 0;
      border: none !important;
      display: flex;
      flex-direction: column;
      gap: 0;
    }
    #chat-scroll-end.wa-feed-bottom-spacer {
      flex-shrink: 0;
      width: 100%;
      min-height: var(--ml-compose-clearance);
      height: var(--ml-compose-clearance);
      pointer-events: none;
    }
    .wa-msg-row {
      display: flex;
      width: 100%;
      margin-bottom: 0.12rem;
      animation: wa-msg-in 0.22s ease-out;
    }
    @keyframes wa-msg-in {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .wa-msg-row--out { justify-content: flex-end; }
    .wa-msg-row--in { justify-content: flex-start; }
    .wa-msg-row.is-grouped { margin-bottom: 0.04rem; }
    .wa-msg-row.is-grouped .wa-bubble-wrap { margin-top: 0; }
    .wa-msg-row.is-grouped .wa-bubble--in { border-top-left-radius: 6px; }
    .wa-msg-row.is-grouped .wa-bubble--out { border-top-right-radius: 6px; }
    .wa-bubble-wrap {
      max-width: 75%;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }
    .wa-msg-row--out .wa-bubble-wrap { align-items: flex-end; }
    .wa-sender-name {
      font-size: 0.72rem;
      font-weight: 600;
      color: #53bdeb;
      margin: 0 0 0.15rem 0.35rem;
      padding: 0;
    }
    .wa-bubble {
      position: relative;
      padding: 0.4rem 0.55rem 0.3rem 0.6rem;
      border-radius: 8px;
      font-size: 0.875rem;
      line-height: 1.35;
      word-wrap: break-word;
      box-shadow: 0 1px 0.5px rgba(0,0,0,.13);
    }
    .wa-bubble--in {
      background: var(--wa-bubble-in);
      color: var(--wa-text);
      border-top-left-radius: 0;
    }
    .wa-bubble--out {
      background: var(--wa-bubble-out);
      color: var(--wa-text);
      border-top-right-radius: 0;
    }
    .wa-bubble .chat-text { margin: 0; color: inherit; }
    .wa-bubble img.wa-media-img,
    .wa-bubble img {
      max-width: 100%;
      border-radius: 6px;
      display: block;
      cursor: pointer;
      margin: 0.15rem 0;
    }
    .wa-bubble audio { width: min(100%, 240px); max-width: 100%; }
    .wa-bubble-meta {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 0.2rem;
      margin-top: 0.15rem;
      float: right;
      margin-left: 0.5rem;
      position: relative;
      top: 0.2rem;
    }
    .wa-bubble-time {
      font-size: 0.65rem;
      color: var(--wa-meta);
      white-space: nowrap;
    }
    .wa-bubble--out .wa-bubble-time { color: rgba(255,255,255,.55); }
    .wa-ticks {
      font-size: 0.72rem;
      line-height: 1;
      letter-spacing: -0.12em;
      color: var(--wa-meta);
    }
    .wa-ticks--read { color: #53bdeb; }
    .wa-msg-row[data-can-delete="1"] .wa-bubble {
      -webkit-user-select: none;
      user-select: none;
      touch-action: manipulation;
    }
    .wa-msg-row.wa-msg-hold .wa-bubble {
      filter: brightness(1.08);
      box-shadow: 0 0 0 2px rgba(0, 168, 132, 0.4);
    }
    #wa-msg-actions {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 2147483646;
      align-items: flex-end;
      justify-content: center;
    }
    #wa-msg-actions.is-open { display: flex; }
    .wa-msg-actions-backdrop {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.55);
    }
    .wa-msg-actions-sheet {
      position: relative;
      width: 100%;
      max-width: 480px;
      background: #1f2c34;
      border-radius: 14px 14px 0 0;
      padding: 0.85rem 1rem calc(1rem + env(safe-area-inset-bottom, 0px));
      box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.35);
    }
    .wa-msg-actions-preview {
      margin: 0 0 0.75rem;
      font-size: 0.8rem;
      color: #8696a0;
      line-height: 1.35;
      max-height: 3.2em;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .wa-msg-actions-btn {
      display: block;
      width: 100%;
      margin: 0.35rem 0;
      padding: 0.75rem 1rem;
      border: none;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      background: #2a3942;
      color: #e9edef;
    }
    .wa-msg-actions-btn--danger {
      background: rgba(234, 67, 53, 0.18);
      color: #ea4335;
    }
    .wa-doc-card {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      padding: 0.5rem;
      background: rgba(0,0,0,.15);
      border-radius: 8px;
      min-width: 200px;
      cursor: pointer;
    }
    .wa-doc-icon {
      width: 2.5rem;
      height: 2.5rem;
      border-radius: 8px;
      background: #ef4444;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      flex-shrink: 0;
    }
    .wa-doc-body { min-width: 0; flex: 1; }
    .wa-doc-name {
      font-size: 0.8rem;
      font-weight: 600;
      color: inherit;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .wa-doc-meta { font-size: 0.65rem; color: var(--wa-meta); margin-top: 0.1rem; }
    .wa-jump-bottom {
      position: fixed;
      right: 1rem;
      bottom: calc(
        var(--ml-nav-height) + var(--ml-verse-height) + var(--ml-nav-offset)
        + var(--ml-compose-clearance, 5.75rem) + 0.25rem
      );
      z-index: 2147483648;
      display: none;
      align-items: center;
      gap: 0.35rem;
      padding: 0.45rem 0.85rem;
      border-radius: 999px;
      background: #233138;
      color: var(--wa-accent);
      font-size: 0.78rem;
      font-weight: 600;
      border: 1px solid rgba(255,255,255,.1);
      box-shadow: 0 4px 16px rgba(0,0,0,.35);
      cursor: pointer;
      animation: wa-fade-in 0.2s ease;
    }
    .wa-jump-bottom.is-visible { display: inline-flex; }
    @keyframes wa-fade-in {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    #wa-lightbox {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 2147483647;
      background: #0b141a;
      flex-direction: column;
    }
    #wa-lightbox.is-open { display: flex; }
    .wa-lightbox-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.65rem 0.85rem;
      background: rgba(0,0,0,.5);
      color: var(--wa-text);
      flex-shrink: 0;
    }
    .wa-lightbox-top button {
      background: transparent;
      border: none;
      color: var(--wa-text);
      font-size: 1.25rem;
      padding: 0.35rem 0.5rem;
      cursor: pointer;
    }
    .wa-lightbox-stage {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      touch-action: none;
    }
    .wa-lightbox-stage img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      transition: transform 0.15s ease;
    }
    .wa-lightbox-foot {
      padding: 0.65rem 1rem 1rem;
      background: rgba(0,0,0,.45);
      color: var(--wa-text);
      font-size: 0.8rem;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_composer"] {
      position: fixed !important;
      left: 0 !important;
      right: 0 !important;
      transform: none !important;
      width: 100% !important;
      max-width: 100% !important;
      bottom: calc(var(--ml-nav-height) + var(--ml-verse-height) + var(--ml-nav-offset)) !important;
      z-index: 2147483650 !important;
      margin: 0 !important;
      padding: 0.25rem 0.4rem 0.35rem !important;
      box-sizing: border-box !important;
      background: var(--wa-compose) !important;
      border: none !important;
      border-top: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 0 !important;
      box-shadow: none !important;
      max-height: 42vh !important;
      overflow-y: auto !important;
      -webkit-overflow-scrolling: touch;
    }
    /* Barra principal: uma linha [+][😊][mensagem][🎤] */
    body:has(#ml-chat-page) [class*="st-key-ml_chat_compose_main"] [data-testid="stHorizontalBlock"] {
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      align-items: flex-end !important;
      gap: 0.25rem !important;
      width: 100% !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_compose_main"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1),
    body:has(#ml-chat-page) [class*="st-key-ml_chat_compose_main"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2),
    body:has(#ml-chat-page) [class*="st-key-ml_chat_compose_main"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) {
      flex: 0 0 2.45rem !important;
      width: 2.45rem !important;
      max-width: 2.45rem !important;
      min-width: 2.45rem !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_compose_main"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {
      flex: 1 1 auto !important;
      width: auto !important;
      max-width: none !important;
      min-width: 0 !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_attach_sheet"] [data-testid="stHorizontalBlock"],
    body:has(#ml-chat-page) [class*="st-key-ml_chat_emoji_strip"] [data-testid="stHorizontalBlock"] {
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      gap: 0.2rem !important;
      width: 100% !important;
      margin-bottom: 0.2rem !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_attach_sheet"] [data-testid="stColumn"],
    body:has(#ml-chat-page) [class*="st-key-ml_chat_emoji_strip"] [data-testid="stColumn"] {
      flex: 1 1 0 !important;
      min-width: 0 !important;
      max-width: 2.6rem !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_attach_panel"] {
      max-height: 26vh !important;
      overflow-y: auto !important;
      margin-bottom: 0.3rem !important;
      padding: 0.25rem !important;
      background: rgba(0,0,0,.22) !important;
      border-radius: 10px !important;
      -webkit-overflow-scrolling: touch;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_attach_panel"] [data-testid="stFileUploader"] section {
      padding: 0.35rem !important;
      min-height: 0 !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_attach_panel"] [data-testid="stFileUploader"] small,
    body:has(#ml-chat-page) [class*="st-key-ml_chat_attach_panel"] [data-testid="stCameraInput"] small {
      display: none !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_composer"] [data-testid="stPopover"],
    body:has(#ml-chat-page) [class*="st-key-ml_chat_composer"] [data-baseweb="popover"] {
      display: none !important;
    }
    body:has(#ml-chat-page) .wa-compose-bar [data-testid="stChatInput"] {
      background: #2a3942 !important;
      border: none !important;
      border-radius: 24px !important;
      flex: 1;
      min-height: 0 !important;
    }
    body:has(#ml-chat-page) .wa-compose-bar [data-testid="stChatInput"] textarea {
      color: var(--wa-text) !important;
      font-size: 0.9rem !important;
      min-height: 2.25rem !important;
      max-height: 4.5rem !important;
      padding: 0.45rem 0.75rem !important;
    }
    body:has(#ml-chat-page) .wa-compose-bar .stButton > button {
      min-height: 2.35rem !important;
      max-height: 2.35rem !important;
      min-width: 2.35rem !important;
      max-width: 2.35rem !important;
      padding: 0 !important;
      border-radius: 50% !important;
      background: transparent !important;
      border: none !important;
      color: var(--wa-meta) !important;
      font-size: 1.15rem !important;
      line-height: 1 !important;
    }
    body:has(#ml-chat-page) [class*="st-key-ml_chat_back"] .stButton > button {
      background: transparent !important;
      border: none !important;
      color: var(--wa-accent) !important;
      font-size: 1.35rem !important;
      min-height: 2.5rem !important;
      padding: 0 0.35rem !important;
    }
    """
    )


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _message_ticks(*, is_me: bool, msg_ts: str, chat_df: pd.DataFrame, my_email: str) -> str:
    if not is_me:
        return ""
    try:
        from app_time import parse_timestamp

        my_dt = parse_timestamp(msg_ts)
        if my_dt is None:
            return '<span class="wa-ticks">✓✓</span>'
        others = chat_df[
            chat_df["email"].astype(str).str.strip().str.lower() != my_email
        ]
        if others.empty:
            return '<span class="wa-ticks">✓</span>'
        for _, o in others.iterrows():
            odt = parse_timestamp(str(o.get("timestamp", "")))
            if odt and odt > my_dt:
                return '<span class="wa-ticks wa-ticks--read">✓✓</span>'
        return '<span class="wa-ticks">✓✓</span>'
    except Exception:
        return '<span class="wa-ticks">✓✓</span>'


def _bubble_time_str(ts: object) -> str:
    from app_time import format_local

    return format_local(ts, "%H:%M")


def _is_pdf_message(message: str, mtype: str) -> bool:
    low = (message or "").lower()
    return mtype == "text" and (
        ".pdf" in low or low.startswith("📄") or "boleto" in low or "comprovante" in low
    )


def _document_bubble_html(message: str) -> str:
    name = message.strip() or "Documento.pdf"
    if len(name) > 48:
        name = name[:45] + "…"
    return (
        f'<div class="wa-doc-card" role="button" title="Abrir documento">'
        f'<div class="wa-doc-icon">📄</div>'
        f'<div class="wa-doc-body">'
        f'<div class="wa-doc-name">{_esc(name)}</div>'
        f'<div class="wa-doc-meta">PDF · Toque para baixar</div>'
        f"</div></div>"
    )


def _build_message_body(row: pd.Series, chat_media_html) -> str:
    mtype = str(row.get("message_type", "text") or "text").strip().lower()
    msg = str(row.get("message", ""))
    if _is_pdf_message(msg, mtype):
        return _document_bubble_html(msg)
    if mtype == "audio":
        return chat_media_html("audio", str(row.get("media_file", "")))
    if mtype == "image":
        body = chat_media_html("image", str(row.get("media_file", "")))
        return body.replace("<img ", '<img class="wa-media-img" ')
    body = msg.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    return f'<p class="chat-text">{body}</p>'


def build_wa_messages_html(chat_df: pd.DataFrame, members_df: pd.DataFrame) -> str:
    if chat_df is None or chat_df.empty:
        return (
            '<div class="wa-chat-empty" style="text-align:center;padding:2rem;color:#8696a0;">'
            "<strong style='color:#e9edef;display:block;margin-bottom:0.35rem;'>Nenhuma mensagem</strong>"
            "Envie a primeira mensagem para o grupo.</div>"
        )

    from chat_runtime import can_delete_chat_message

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    roles = str(st.session_state.get("user_roles", ""))
    chat_sorted = sort_chat_messages(chat_df)
    parts: list[str] = []
    prev_email = ""
    prev_side = ""
    prev_ts = None

    for _, row in chat_sorted.iterrows():
        email = str(row.get("email", "")).strip().lower()
        is_me = email == my_email
        side = "out" if is_me else "in"
        ts_raw = str(row.get("timestamp", ""))
        grouped = email == prev_email and side == prev_side and prev_ts is not None
        cur = None
        try:
            from app_time import parse_timestamp

            cur = parse_timestamp(ts_raw)
            if grouped and cur and prev_ts:
                grouped = grouped and (cur - prev_ts) < timedelta(minutes=15)
        except Exception:
            pass

        display_name = "Você" if is_me else str(row.get("name", "Integrante"))
        time_lbl = _bubble_time_str(row.get("timestamp"))
        ticks = _message_ticks(is_me=is_me, msg_ts=ts_raw, chat_df=chat_df, my_email=my_email)
        body = _build_message_body(row, chat_media_html_cached)
        show_name = not is_me and not grouped

        row_cls = f"wa-msg-row wa-msg-row--{side}"
        if grouped:
            row_cls += " is-grouped"

        name_html = (
            f'<div class="wa-sender-name">{_esc(display_name)}</div>' if show_name else ""
        )
        can_del = (
            "1"
            if can_delete_chat_message(email, roles=roles, my_email=my_email)
            else "0"
        )
        parts.append(
            f'<div class="{row_cls}" data-msg-ts="{_esc(ts_raw)}" data-msg-email="{_esc(email)}" '
            f'data-can-delete="{can_del}" data-sender-name="{_esc(display_name)}">'
            f'<div class="wa-bubble-wrap">'
            f"{name_html}"
            f'<div class="wa-bubble wa-bubble--{side}">'
            f"{body}"
            f'<div class="wa-bubble-meta">'
            f'<span class="wa-bubble-time">{_esc(time_lbl)}</span>'
            f"{ticks}"
            f"</div></div></div></div>"
        )
        prev_email = email
        prev_side = side
        prev_ts = cur

    return "\n".join(parts)


def build_wa_messages_html_cached(
    chat_df: pd.DataFrame, members_df: pd.DataFrame, *, rev: str
) -> str:
    if (
        st.session_state.get(_FEED_REV_KEY) == rev
        and st.session_state.get(_FEED_HTML_KEY)
    ):
        return str(st.session_state[_FEED_HTML_KEY])
    html_block = build_wa_messages_html(chat_df, members_df)
    st.session_state[_FEED_HTML_KEY] = html_block
    st.session_state[_FEED_REV_KEY] = rev
    return html_block


def render_wa_mobile_messages(
    chat_df: pd.DataFrame,
    members_df: pd.DataFrame,
    *,
    rev: str | None = None,
) -> None:
    feed_rev = rev if rev is not None else str(st.session_state.get("_chat_rev", ""))
    html_block = build_wa_messages_html_cached(chat_df, members_df, rev=feed_rev)
    st.markdown(
        f'<div id="chat-scroll-box" class="chat-feed wa-chat-feed">{html_block}'
        f'<div id="chat-scroll-end" class="wa-feed-bottom-spacer" aria-hidden="true"></div></div>',
        unsafe_allow_html=True,
    )
    inject_wa_scroll_and_lightbox()


def render_wa_feed_from_cache(members_df: pd.DataFrame) -> bool:
    """
    Reexibe feed do cache sem reconstruir HTML.
    Retorna False se precisa render completo.
    """
    rev = str(st.session_state.get("_chat_rev", ""))
    if st.session_state.get(_FEED_REV_KEY) != rev:
        return False
    html_block = st.session_state.get(_FEED_HTML_KEY)
    if not html_block:
        return False
    st.markdown(
        f'<div id="chat-scroll-box" class="chat-feed wa-chat-feed">{html_block}'
        f'<div id="chat-scroll-end" class="wa-feed-bottom-spacer" aria-hidden="true"></div></div>',
        unsafe_allow_html=True,
    )
    return True


def render_wa_thread_header_html(
    *,
    member_count: int | None = None,
    online_hint: str = "",
    title: str | None = None,
    subtitle: str | None = None,
    avatar: str | None = None,
) -> str:
    header_title = title or GROUP_CHAT_TITLE
    status = subtitle or online_hint
    if not status and member_count is not None:
        status = f"{member_count} participantes"
    status = status or ""
    online_cls = (
        " is-online"
        if status and "online" in status.lower()
        else ""
    )
    avatar_display = avatar or _WA_GROUP_AVATAR
    return f"""
    <header class="wa-thread-header" aria-label="Cabeçalho do chat">
      <div class="wa-thread-header__avatar">{avatar_display}</div>
      <div class="wa-thread-header__body">
        <p class="wa-thread-header__title">{_esc(header_title)}</p>
        <p class="wa-thread-header__status{online_cls}">{_esc(status)}</p>
      </div>
      <div class="wa-thread-header__actions">
        <span class="wa-icon-btn" title="Ligação">📞</span>
        <span class="wa-icon-btn" title="Vídeo">🎥</span>
        <span class="wa-icon-btn" title="Menu">⋮</span>
      </div>
    </header>
    """


def render_wa_list_header_html() -> str:
    return f"""
    <div class="wa-chat-list-header">
      <h1>Conversas</h1>
      <p>{_esc(GROUP_CHAT_SUB)}</p>
    </div>
    """


def inject_wa_scroll_nudge_only() -> None:
    """Só rola ao fim após enviar — sem reinjetar todo o script."""
    if not st.session_state.pop("_chat_scroll_bottom", False):
        return
    inject_page_script(
        """
        (function () {
          var doc = document;
          try {
            if (window.parent && window.parent.document) doc = window.parent.document;
          } catch (e) {}
          function syncComposeClearance() {
            var box = doc.getElementById("chat-scroll-box");
            var comp = doc.querySelector('[class*="st-key-ml_chat_composer"]');
            if (!box) return;
            var h = 92;
            if (comp) h = Math.max(72, comp.getBoundingClientRect().height);
            var clearance = Math.ceil(h + 14) + "px";
            doc.documentElement.style.setProperty("--ml-compose-clearance", clearance);
            box.style.paddingBottom = clearance;
            var end = doc.getElementById("chat-scroll-end");
            if (end) end.style.height = clearance;
          }
          syncComposeClearance();
          var box = doc.getElementById("chat-scroll-box");
          if (box) box.scrollTop = box.scrollHeight + 9999;
          var end = doc.getElementById("chat-scroll-end");
          if (end) end.scrollIntoView({ block: "end", behavior: "auto" });
        })();
        """
    )


def inject_wa_scroll_and_lightbox() -> None:
    if st.session_state.get("_wa_chat_js_ready"):
        inject_wa_scroll_nudge_only()
        return

    st.session_state["_wa_chat_js_ready"] = True
    force = st.session_state.pop("_chat_scroll_bottom", False)
    force_js = "true" if force else "false"

    inject_ui_html(
        """
        <button type="button" class="wa-jump-bottom" id="wa-jump-bottom" aria-label="Ir para última mensagem">
          ↓ Última mensagem
        </button>
        <div id="wa-lightbox" aria-hidden="true">
          <div class="wa-lightbox-top">
            <button type="button" id="wa-lb-close" aria-label="Fechar">✕</button>
            <span id="wa-lb-actions">☆ ⬇ ↗ ⋮</span>
          </div>
          <div class="wa-lightbox-stage" id="wa-lb-stage">
            <img id="wa-lb-img" alt="" />
          </div>
          <div class="wa-lightbox-foot">
            <div id="wa-lb-sender"></div>
            <div id="wa-lb-meta"></div>
            <div id="wa-lb-caption"></div>
          </div>
        </div>
        <div id="wa-msg-actions" role="dialog" aria-hidden="true" aria-label="Ações da mensagem">
          <div class="wa-msg-actions-backdrop"></div>
          <div class="wa-msg-actions-sheet">
            <p class="wa-msg-actions-preview" id="wa-msg-actions-preview"></p>
            <button type="button" id="wa-msg-actions-delete" class="wa-msg-actions-btn wa-msg-actions-btn--danger">
              Apagar mensagem
            </button>
            <button type="button" id="wa-msg-actions-cancel" class="wa-msg-actions-btn">Cancelar</button>
          </div>
        </div>
        """
    )

    inject_page_script(
        f"""
        (function () {{
          var doc = document;
          try {{
            if (window.parent && window.parent.document) doc = window.parent.document;
          }} catch (e) {{}}
          var forceScroll = {force_js};
          var box = doc.getElementById("chat-scroll-box");
          var jumpBtn = doc.getElementById("wa-jump-bottom");
          var lb = doc.getElementById("wa-lightbox");
          if (!box) return;

          function syncComposeClearance() {{
            var comp = doc.querySelector('[class*="st-key-ml_chat_composer"]');
            var h = 92;
            if (comp) h = Math.max(72, comp.getBoundingClientRect().height);
            var clearance = Math.ceil(h + 16) + "px";
            doc.documentElement.style.setProperty("--ml-compose-clearance", clearance);
            box.style.paddingBottom = clearance;
            var end = doc.getElementById("chat-scroll-end");
            if (end) end.style.height = clearance;
          }}

          function nearBottom() {{
            return box.scrollHeight - box.scrollTop - box.clientHeight < 160;
          }}

          function scrollToEnd(smooth) {{
            syncComposeClearance();
            box.scrollTop = box.scrollHeight + 99999;
            var end = doc.getElementById("chat-scroll-end");
            if (end) end.scrollIntoView({{ block: "end", behavior: smooth ? "smooth" : "auto" }});
            if (jumpBtn) jumpBtn.classList.remove("is-visible");
          }}

          function updateJump() {{
            if (!jumpBtn) return;
            if (nearBottom()) jumpBtn.classList.remove("is-visible");
            else jumpBtn.classList.add("is-visible");
          }}

          if (jumpBtn && !jumpBtn.dataset.bound) {{
            jumpBtn.dataset.bound = "1";
            jumpBtn.addEventListener("click", function () {{ scrollToEnd(true); }});
          }}

          box.addEventListener("scroll", updateJump, {{ passive: true }});

          if (forceScroll || nearBottom()) scrollToEnd(false);
          else updateJump();

          if (!box.dataset.waObs) {{
            box.dataset.waObs = "1";
            new MutationObserver(function () {{
              syncComposeClearance();
              if (nearBottom() || forceScroll) scrollToEnd(false);
              else updateJump();
            }}).observe(box, {{ childList: true, subtree: true }});
          }}

          var comp = doc.querySelector('[class*="st-key-ml_chat_composer"]');
          if (comp && !comp.dataset.waPadObs) {{
            comp.dataset.waPadObs = "1";
            new ResizeObserver(function () {{
              syncComposeClearance();
              if (nearBottom()) scrollToEnd(false);
            }}).observe(comp);
          }}

          syncComposeClearance();

          [100, 300, 700, 1200].forEach(function (ms) {{
            setTimeout(function () {{
              if (nearBottom() || forceScroll) scrollToEnd(ms > 300);
              else updateJump();
            }}, ms);
          }});

          var imgs = box.querySelectorAll("img.wa-media-img, .wa-bubble img");
          var gallery = [];
          imgs.forEach(function (img, idx) {{
            gallery.push({{ src: img.src, alt: img.alt || "" }});
            img.style.cursor = "pointer";
            if (img.dataset.lb) return;
            img.dataset.lb = "1";
            img.addEventListener("click", function () {{
              if (!lb) return;
              var stage = doc.getElementById("wa-lb-img");
              var sender = doc.getElementById("wa-lb-sender");
              var meta = doc.getElementById("wa-lb-meta");
              var cap = doc.getElementById("wa-lb-caption");
              if (stage) stage.src = img.src;
              var row = img.closest(".wa-msg-row");
              var nameEl = row && row.querySelector(".wa-sender-name");
              var timeEl = row && row.querySelector(".wa-bubble-time");
              if (sender) sender.textContent = nameEl ? nameEl.textContent : "";
              if (meta) meta.textContent = timeEl ? timeEl.textContent : "";
              if (cap) cap.textContent = img.alt || "";
              lb.classList.add("is-open");
              lb.setAttribute("aria-hidden", "false");
              lb._gallery = gallery;
              lb._idx = idx;
            }});
          }});

          var closeBtn = doc.getElementById("wa-lb-close");
          if (closeBtn && !closeBtn.dataset.bound) {{
            closeBtn.dataset.bound = "1";
            closeBtn.addEventListener("click", function () {{
              if (lb) {{
                lb.classList.remove("is-open");
                lb.setAttribute("aria-hidden", "true");
              }}
            }});
          }}

          if (lb && !lb.dataset.swipe) {{
            lb.dataset.swipe = "1";
            var startX = 0;
            lb.addEventListener("touchstart", function (e) {{
              startX = e.touches[0].clientX;
            }}, {{ passive: true }});
            lb.addEventListener("touchend", function (e) {{
              var dx = e.changedTouches[0].clientX - startX;
              if (!lb._gallery || Math.abs(dx) < 50) return;
              var n = lb._gallery.length;
              if (!n) return;
              lb._idx = (lb._idx + (dx < 0 ? 1 : -1) + n) % n;
              var item = lb._gallery[lb._idx];
              var stage = doc.getElementById("wa-lb-img");
              if (stage && item) stage.src = item.src;
            }}, {{ passive: true }});
          }}

          var msgSheet = doc.getElementById("wa-msg-actions");
          var HOLD_MS = 520;

          function bindMessageLongPress() {{
            if (!msgSheet) return;
            var rows = box.querySelectorAll('.wa-msg-row[data-can-delete="1"] .wa-bubble');
            rows.forEach(function (bubble) {{
              if (bubble.dataset.waHoldBound) return;
              bubble.dataset.waHoldBound = "1";
              var row = bubble.closest(".wa-msg-row");
              if (!row) return;
              var timer = null;
              var blockClick = false;
              var startX = 0;
              var startY = 0;

              function clearHold() {{
                if (timer) clearTimeout(timer);
                timer = null;
                if (row) row.classList.remove("wa-msg-hold");
              }}

              function openMsgSheet() {{
                var ts = row.dataset.msgTs;
                var em = row.dataset.msgEmail;
                if (!ts || !em) return;
                msgSheet.dataset.msgTs = ts;
                msgSheet.dataset.msgEmail = em;
                msgSheet.dataset.senderName = row.dataset.senderName || "";
                var preview = doc.getElementById("wa-msg-actions-preview");
                var name = row.dataset.senderName || "Mensagem";
                var txt = row.querySelector(".chat-text");
                var snippet = "Mensagem";
                if (txt && txt.textContent) snippet = txt.textContent.trim().slice(0, 72);
                else if (row.querySelector("img.wa-media-img, .wa-bubble img")) snippet = "Foto";
                else if (row.querySelector("audio")) snippet = "Áudio";
                else if (row.querySelector(".wa-doc-card")) snippet = "Documento";
                if (preview) preview.textContent = name + ": " + snippet;
                msgSheet.classList.add("is-open");
                msgSheet.setAttribute("aria-hidden", "false");
              }}

              function onStart(e) {{
                if (e.type === "mousedown" && e.button !== 0) return;
                blockClick = false;
                startX = e.touches ? e.touches[0].clientX : e.clientX;
                startY = e.touches ? e.touches[0].clientY : e.clientY;
                clearHold();
                timer = setTimeout(function () {{
                  row.classList.add("wa-msg-hold");
                  blockClick = true;
                  if (navigator.vibrate) {{
                    try {{ navigator.vibrate(15); }} catch (err) {{}}
                  }}
                  openMsgSheet();
                }}, HOLD_MS);
              }}

              function onMove(e) {{
                if (!timer) return;
                var x = e.touches ? e.touches[0].clientX : e.clientX;
                var y = e.touches ? e.touches[0].clientY : e.clientY;
                if (Math.abs(x - startX) > 14 || Math.abs(y - startY) > 14) clearHold();
              }}

              bubble.addEventListener("touchstart", onStart, {{ passive: true }});
              bubble.addEventListener("touchmove", onMove, {{ passive: true }});
              bubble.addEventListener("touchend", clearHold);
              bubble.addEventListener("touchcancel", clearHold);
              bubble.addEventListener("mousedown", onStart);
              bubble.addEventListener("mouseup", clearHold);
              bubble.addEventListener("mouseleave", clearHold);
              bubble.addEventListener("click", function (e) {{
                if (blockClick) {{
                  e.preventDefault();
                  e.stopPropagation();
                  blockClick = false;
                }}
              }}, true);
            }});
          }}

          function closeMsgSheet() {{
            if (!msgSheet) return;
            msgSheet.classList.remove("is-open");
            msgSheet.setAttribute("aria-hidden", "true");
            box.querySelectorAll(".wa-msg-hold").forEach(function (r) {{
              r.classList.remove("wa-msg-hold");
            }});
          }}

          if (msgSheet && !msgSheet.dataset.bound) {{
            msgSheet.dataset.bound = "1";
            var cancelBtn = doc.getElementById("wa-msg-actions-cancel");
            var delBtn = doc.getElementById("wa-msg-actions-delete");
            var backdrop = msgSheet.querySelector(".wa-msg-actions-backdrop");
            if (cancelBtn) cancelBtn.addEventListener("click", closeMsgSheet);
            if (backdrop) backdrop.addEventListener("click", closeMsgSheet);
            if (delBtn) delBtn.addEventListener("click", function () {{
              var ts = msgSheet.dataset.msgTs;
              var em = msgSheet.dataset.msgEmail;
              if (!ts || !em) return;
              var who = msgSheet.dataset.senderName || "esta mensagem";
              var prompt = who === "Você"
                ? "Apagar sua mensagem?"
                : "Apagar mensagem de " + who + "?";
              if (!confirm(prompt)) return;
              closeMsgSheet();
              var url = new URL(window.parent.location.href);
              url.searchParams.set(
                "ml_del",
                encodeURIComponent(ts) + "|" + encodeURIComponent(em)
              );
              window.parent.location.href = url.toString();
            }});
          }}

          bindMessageLongPress();

          if (!box.dataset.waMsgDelObs) {{
            box.dataset.waMsgDelObs = "1";
            new MutationObserver(function () {{
              bindMessageLongPress();
            }}).observe(box, {{ childList: true, subtree: true }});
          }}
        }})();
        """
    )


def inject_wa_list_conv_styles() -> None:
    inject_ui_html('<div class="wa-conv-list">')
