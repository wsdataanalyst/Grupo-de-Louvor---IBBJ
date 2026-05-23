"""Funcionalidades estendidas: feed, escalas, notificações, repertório."""

from __future__ import annotations

import json
from datetime import date

import pandas as pd

from escala_member_stats import format_date_br, member_escala_occurrences, member_escala_stats
from louvor_meta import (
    parse_duracao_min,
    suggest_biblical_refs,
    themes_from_csv,
)


def count_pending_sugestoes(sugestoes_df: pd.DataFrame) -> int:
    if sugestoes_df.empty:
        return 0
    return int(
        (sugestoes_df["status"].astype(str).str.lower() == "pendente").sum()
    )


def inject_app_notification_badges(
    chat_unread: int,
    sugestoes_pending: int = 0,
    swap_pending: int = 0,
) -> None:
    """Badges separados no menu lateral (não colados ao texto)."""
    from app import inject_page_html

    badges = {}
    if chat_unread > 0:
        badges["Chat"] = min(99, int(chat_unread))
    if sugestoes_pending > 0:
        badges["Sugestão de louvor"] = min(99, int(sugestoes_pending))
    if swap_pending > 0:
        badges["Escalas"] = min(99, int(swap_pending))
    total = sum(badges.values())
    show_bell = "flex" if total > 0 else "none"
    total_label = "99+" if total > 99 else str(total)
    badges_json = json.dumps(badges, ensure_ascii=False)

    inject_page_html(
        f"""
        <style>
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 0.5rem !important;
            position: relative !important;
        }}
        .nav-menu-badge {{
            flex-shrink: 0;
            min-width: 1.35rem;
            height: 1.35rem;
            padding: 0 0.35rem;
            border-radius: 999px;
            background: #ef4444;
            color: #fff !important;
            font-size: 0.7rem;
            font-weight: 800;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-left: 0.35rem;
            box-shadow: 0 2px 8px rgba(239,68,68,.45);
        }}
        .nav-menu-badge--sug {{
            background: #f59e0b;
            color: #1a0a2e !important;
        }}
        .nav-menu-badge--swap {{
            background: #60a5fa;
            color: #0f172a !important;
        }}
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
          var badges = {badges_json};
          var doc = window.parent.document;
          function attach() {{
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            sidebar.querySelectorAll('[data-testid="stRadio"] label').forEach(function (el) {{
              el.querySelectorAll('.nav-menu-badge').forEach(function (b) {{ b.remove(); }});
              var raw = (el.innerText || "").trim();
              Object.keys(badges).forEach(function (menuName) {{
                if (raw.indexOf(menuName) < 0) return;
                var n = badges[menuName];
                var badge = doc.createElement('span');
                badge.className = 'nav-menu-badge';
                if (menuName.indexOf('Sugest') >= 0) badge.className += ' nav-menu-badge--sug';
                if (menuName === 'Escalas') badge.className += ' nav-menu-badge--swap';
                badge.textContent = n > 99 ? '99+' : String(n);
                el.appendChild(badge);
              }});
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
    import streamlit as st

    futuras = user_future_escalas(email, escalas_df, equipe_df)
    if not futuras:
        return
    st.markdown('<p class="music-panel-title">📆 Suas próximas escalas</p>', unsafe_allow_html=True)
    cols = st.columns(min(4, len(futuras[:8])))
    for i, item in enumerate(futuras[:8]):
        d = item["date"].strftime("%d/%m/%Y")
        ev = str(item["event"])
        eid = str(item["escala_id"])
        with cols[i % len(cols)]:
            if st.button(
                f"📅 {d}\n{ev}",
                key=f"dash_fe_{eid}",
                use_container_width=True,
            ):
                st.session_state.app_menu = "Escalas"
                st.session_state.focus_escala_id = eid
                try:
                    culto = item["date"]
                    today = date.today()
                    st.session_state.week_offset = (culto - today).days // 7
                except Exception:
                    pass
                st.rerun()
    if len(futuras) > 8:
        st.caption(f"Mais {len(futuras) - 8} culto(s) — veja em **Escalas**.")


def render_escala_planner_panel(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    culto_ref: date,
):
    """Quem ainda não foi escalado no mês + última escala."""
    import html as html_mod
    import streamlit as st

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


def save_feed_image_file(uploaded, data_dir, feed_images_dir) -> str:
    from chat_media import save_image_upload

    feed_images_dir.mkdir(parents=True, exist_ok=True)
    rel = save_image_upload(
        uploaded, feed_images_dir, prefix="feed", data_dir=data_dir
    )
    return rel


def feed_image_display_path(image_url: str, data_dir) -> str | None:
    raw = str(image_url).strip()
    if raw.startswith("http"):
        return raw
    if not raw:
        return None
    p = data_dir / raw.replace("\\", "/")
    return str(p) if p.exists() else None
