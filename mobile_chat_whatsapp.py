"""Chat mobile — layout e comportamento estilo WhatsApp Business."""

from __future__ import annotations

import html
from datetime import timedelta

import pandas as pd
import streamlit as st

from chat_runtime import chat_media_html, sort_chat_messages
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
      max-width: 100% !important;
    }
    #ml-chat-page.wa-chat-page {
      display: flex;
      flex-direction: column;
      min-height: calc(100dvh - var(--ml-nav-height) - var(--ml-verse-height) - 2rem);
      background: var(--wa-bg);
      background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
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
      display: flex;
      flex-direction: column;
      flex: 1;
      min-height: 0;
      margin: 0 -0.5rem;
    }
    .wa-thread-header {
      position: sticky;
      top: 0;
      z-index: 100;
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
      flex: 1;
      width: 100%;
      max-width: 100%;
      min-height: calc(100dvh - var(--ml-nav-height) - var(--ml-verse-height) - 11rem);
      max-height: calc(100dvh - var(--ml-nav-height) - var(--ml-verse-height) - 11rem);
      overflow-y: auto !important;
      overflow-x: hidden;
      -webkit-overflow-scrolling: touch;
      scroll-behavior: smooth;
      padding: 0.5rem 0.55rem 0.75rem;
      margin: 0;
      background: transparent !important;
      border: none !important;
      display: flex;
      flex-direction: column;
      gap: 0;
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
      bottom: calc(var(--ml-nav-height) + var(--ml-verse-height) + var(--ml-nav-offset) + 5.5rem);
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
      padding: 0.35rem 0.5rem 0.45rem !important;
      box-sizing: border-box !important;
      background: var(--wa-compose) !important;
      border: none !important;
      border-top: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 0 !important;
      box-shadow: none !important;
    }
    body:has(#ml-chat-page) .wa-compose-bar [data-testid="stHorizontalBlock"] {
      align-items: flex-end !important;
      gap: 0.35rem !important;
    }
    body:has(#ml-chat-page) .wa-compose-bar [data-testid="stChatInput"] {
      background: #2a3942 !important;
      border: none !important;
      border-radius: 24px !important;
      flex: 1;
    }
    body:has(#ml-chat-page) .wa-compose-bar [data-testid="stChatInput"] textarea {
      color: var(--wa-text) !important;
      font-size: 0.95rem !important;
    }
    body:has(#ml-chat-page) .wa-compose-bar .stButton > button {
      min-height: 2.5rem !important;
      min-width: 2.5rem !important;
      border-radius: 50% !important;
      background: transparent !important;
      border: none !important;
      color: var(--wa-meta) !important;
      font-size: 1.2rem !important;
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

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
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
        body = _build_message_body(row, chat_media_html)
        show_name = not is_me and not grouped

        row_cls = f"wa-msg-row wa-msg-row--{side}"
        if grouped:
            row_cls += " is-grouped"

        name_html = (
            f'<div class="wa-sender-name">{_esc(display_name)}</div>' if show_name else ""
        )
        parts.append(
            f'<div class="{row_cls}">'
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


def render_wa_mobile_messages(chat_df: pd.DataFrame, members_df: pd.DataFrame) -> None:
    html_block = build_wa_messages_html(chat_df, members_df)
    st.markdown(
        f'<div id="chat-scroll-box" class="chat-feed wa-chat-feed">{html_block}'
        f'<div id="chat-scroll-end" style="height:1px;"></div></div>',
        unsafe_allow_html=True,
    )
    inject_wa_scroll_and_lightbox()


def render_wa_thread_header_html(*, member_count: int, online_hint: str = "") -> str:
    status = online_hint or f"{member_count} participantes"
    online_cls = " is-online" if online_hint and "online" in online_hint.lower() else ""
    return f"""
    <header class="wa-thread-header" aria-label="Cabeçalho do chat">
      <div class="wa-thread-header__avatar">{_WA_GROUP_AVATAR}</div>
      <div class="wa-thread-header__body">
        <p class="wa-thread-header__title">{_esc(GROUP_CHAT_TITLE)}</p>
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


def inject_wa_scroll_and_lightbox() -> None:
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
        """
    )

    inject_page_script(
        f"""
        (function () {{
          var doc = window.parent.document;
          var forceScroll = {force_js};
          var box = doc.getElementById("chat-scroll-box");
          var jumpBtn = doc.getElementById("wa-jump-bottom");
          var lb = doc.getElementById("wa-lightbox");
          if (!box) return;

          function nearBottom() {{
            return box.scrollHeight - box.scrollTop - box.clientHeight < 120;
          }}

          function scrollToEnd(smooth) {{
            box.scrollTop = box.scrollHeight + 9999;
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
              if (nearBottom() || forceScroll) scrollToEnd(false);
              else updateJump();
            }}).observe(box, {{ childList: true, subtree: true }});
          }}

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
        }})();
        """
    )


def inject_wa_list_conv_styles() -> None:
    inject_ui_html('<div class="wa-conv-list">')
