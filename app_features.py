"""Funcionalidades estendidas: feed, escalas, notificações, repertório."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from escala_member_stats import format_date_br, member_escala_occurrences, member_escala_stats
from louvor_meta import (
    LOUVOR_THEMES,
    classify_themes,
    format_duracao_total,
    guia_ministracao_text,
    parse_duracao_min,
    suggest_biblical_refs,
    themes_from_csv,
    validate_louvor,
)


def count_pending_sugestoes(sugestoes_df: pd.DataFrame) -> int:
    if sugestoes_df.empty:
        return 0
    return int(
        (sugestoes_df["status"].astype(str).str.lower() == "pendente").sum()
    )


def inject_app_notification_badges(chat_unread: int, sugestoes_pending: int = 0) -> None:
    """Badge no menu Chat, Sugestão (líderes) e ícone 🔔 no app."""
    from app import inject_page_html

    chat_unread = max(0, int(chat_unread))
    sug = max(0, int(sugestoes_pending))
    chat_label = "99+" if chat_unread > 99 else str(chat_unread)
    sug_label = "99+" if sug > 99 else str(sug)
    total = chat_unread + sug
    total_label = "99+" if total > 99 else str(total)
    show_chat = "flex" if chat_unread > 0 else "none"
    show_sug = "flex" if sug > 0 else "none"
    show_bell = "flex" if total > 0 else "none"

    inject_page_html(
        f"""
        <style>
        .app-notif-badge {{
            position: absolute; top: 0.12rem; right: 0.3rem;
            min-width: 1.1rem; height: 1.1rem; padding: 0 0.28rem;
            border-radius: 999px; background: #ef4444; color: #fff !important;
            font-size: 0.62rem; font-weight: 800; display: flex;
            align-items: center; justify-content: center; z-index: 8;
            pointer-events: none; box-shadow: 0 2px 8px rgba(239,68,68,.5);
        }}
        .app-notif-badge--sug {{ background: #f59e0b; color: #1a0a2e !important; }}
        #app-bell-notif {{
            position: fixed; top: 0.65rem; right: 0.75rem; z-index: 9999;
            width: 2.25rem; height: 2.25rem; border-radius: 50%;
            background: rgba(30,20,50,.92); border: 1px solid rgba(251,191,36,.5);
            display: {show_bell}; align-items: center; justify-content: center;
            font-size: 1.15rem; box-shadow: 0 4px 16px rgba(0,0,0,.35);
            pointer-events: none;
        }}
        #app-bell-notif span {{
            position: absolute; top: -2px; right: -2px;
            min-width: 1rem; height: 1rem; border-radius: 999px;
            background: #ef4444; color: #fff; font-size: 0.58rem;
            font-weight: 800; display: flex; align-items: center; justify-content: center;
        }}
        </style>
        <div id="app-bell-notif" title="Novidades">🔔<span>{total_label}</span></div>
        <script>
        (function () {{
          var doc = window.parent.document;
          function attach() {{
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            sidebar.querySelectorAll('[data-testid="stRadio"] label').forEach(function (el) {{
              var t = el.innerText || "";
              if (t.indexOf("Chat") >= 0 && t.indexOf("ensaio") < 0) {{
                var b = el.querySelector(".app-notif-chat");
                if (!b) {{ b = doc.createElement("span"); b.className = "app-notif-badge app-notif-chat"; el.appendChild(b); }}
                b.textContent = {chat_label!r}; b.style.display = {show_chat!r};
              }}
              if (t.indexOf("Sugestão") >= 0 || t.indexOf("Sugestao") >= 0) {{
                var s = el.querySelector(".app-notif-sug");
                if (!s) {{ s = doc.createElement("span"); s.className = "app-notif-badge app-notif-sug"; el.appendChild(s); }}
                s.textContent = {sug_label!r}; s.style.display = {show_sug!r};
              }}
            }});
          }}
          attach(); setTimeout(attach, 400); setTimeout(attach, 1200);
        }})();
        </script>
        """,
        height=0,
    )


def user_future_escalas(
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    from_date: date | None = None,
) -> list[dict]:
    from_date = from_date or date.today()
    occ = member_escala_occurrences(email, escalas_df, equipe_df)
    out = []
    for culto_d, eid, ev in occ:
        if culto_d >= from_date:
            out.append({"date": culto_d, "escala_id": eid, "event": ev})
    return out


def render_dashboard_future_escalas(
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
):
    import html as html_mod

    futuras = user_future_escalas(email, escalas_df, equipe_df)
    if not futuras:
        return
    st.markdown('<p class="music-panel-title">📆 Suas próximas escalas</p>', unsafe_allow_html=True)
    cards = []
    for item in futuras[:8]:
        d = item["date"].strftime("%d/%m/%Y")
        ev = html_mod.escape(str(item["event"]))
        cards.append(
            f'<div class="future-escala-card">'
            f'<p class="fe-date">📅 {d}</p>'
            f'<p class="fe-event">{ev}</p></div>'
        )
    st.markdown(
        '<div class="future-escala-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )
    if len(futuras) > 8:
        st.caption(f"Mais {len(futuras) - 8} culto(s) agendado(s) — veja em **Escalas**.")


def render_escala_planner_panel(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    culto_ref: date,
):
    """Quem ainda não foi escalado no mês + última escala."""
    import html as html_mod
    from app import members_visible_to_group, member_display_name

    st.markdown(
        '<div class="planner-panel-card">'
        '<p class="planner-title">📋 Painel do mês</p>'
        '<p class="planner-sub">Última escala e quem ainda não entrou neste mês.</p></div>',
        unsafe_allow_html=True,
    )
    visible = members_visible_to_group(members_df)
    linhas = []
    for _, row in visible.sort_values(by=["first_name", "last_name"]).iterrows():
        em = str(row["email"]).strip().lower()
        stats = member_escala_stats(em, escalas_df, equipe_df, ref=culto_ref)
        ultima = format_date_br(stats.last_date)
        no_mes = stats.month_count
        linhas.append((no_mes, ultima, member_display_name(row), em))
    linhas.sort(key=lambda x: (x[0], x[1]))
    for no_mes, ultima, nome, _ in linhas[:25]:
        badge = (
            '<span class="planner-badge-ok">no mês</span>'
            if no_mes
            else '<span class="planner-badge-warn">sem escala no mês</span>'
        )
        st.markdown(
            f'<div class="planner-row"><span class="planner-name">{html_mod.escape(nome)}</span>'
            f'{badge}<span class="planner-date">última: {html_mod.escape(ultima)}</span></div>',
            unsafe_allow_html=True,
        )


def member_escala_option_label(
    label: str,
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    culto_ref: date,
) -> str:
    stats = member_escala_stats(email, escalas_df, equipe_df, ref=culto_ref)
    return f"{label} · última: {format_date_br(stats.last_date)} · mês: {stats.month_count}"


def lookup_louvor_meta(louvores_df: pd.DataFrame, title: str, artist: str = "") -> dict:
    if louvores_df.empty:
        return {}
    t = str(title).strip().lower()
    for _, r in louvores_df.iterrows():
        if str(r.get("title", "")).strip().lower() == t:
            return r.to_dict()
    return {}


def programa_duracao_total(programa_df: pd.DataFrame, escala_id: str, louvores_df: pd.DataFrame) -> float:
    from app import programa_por_escala

    prog = programa_por_escala(programa_df, escala_id)
    total = 0.0
    for _, item in prog.iterrows():
        meta = lookup_louvor_meta(
            louvores_df, str(item.get("louvor_title", "")), str(item.get("artist", ""))
        )
        total += parse_duracao_min(meta.get("duracao_min", ""))
    return total


def save_feed_image_file(uploaded, data_dir: Path, feed_images_dir: Path) -> str:
    from chat_media import save_image_upload

    feed_images_dir.mkdir(parents=True, exist_ok=True)
    rel = save_image_upload(
        uploaded, feed_images_dir, prefix="feed", data_dir=data_dir
    )
    return rel


def feed_image_display_path(image_url: str, data_dir: Path) -> str | None:
    raw = str(image_url).strip()
    if raw.startswith("http"):
        return raw
    if not raw:
        return None
    p = data_dir / raw.replace("\\", "/")
    return str(p) if p.exists() else None

