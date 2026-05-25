"""Dashboard premium IBBJ Louvor — layout 3 colunas (mockup v3)."""

from __future__ import annotations

import html
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from app_features import quick_nav_css_class


def _esc_html(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _parse_dt(value: object) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return pd.to_datetime(value).to_pydatetime()
    except (ValueError, TypeError):
        return None


def _time_ago(dt: datetime | None) -> str:
    if not dt:
        return ""
    now = datetime.now()
    delta = now - dt
    if delta.days > 0:
        return f"há {delta.days}d"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"há {hours}h"
    mins = max(1, delta.seconds // 60)
    return f"há {mins}min"


def top_louvores_ranking(
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    limit: int = 4,
) -> list[tuple[str, int]]:
    if programa_df.empty or "louvor_id" not in programa_df.columns:
        return []
    counts = programa_df["louvor_id"].astype(str).value_counts()
    titles: dict[str, str] = {}
    if not louvores_df.empty and "id" in louvores_df.columns:
        for _, row in louvores_df.iterrows():
            titles[str(row.get("id", ""))] = str(row.get("title", "")).strip()
    out: list[tuple[str, int]] = []
    for lid, cnt in counts.head(limit * 2).items():
        name = titles.get(str(lid), "").strip() or f"Louvor {lid[:6]}"
        out.append((name, int(cnt)))
        if len(out) >= limit:
            break
    return out


def recent_activities(
    escalas_df: pd.DataFrame,
    feed_posts_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    limit: int = 5,
) -> list[tuple[str, str, str, str]]:
    """(icon_class, title, meta, time_ago)"""
    items: list[tuple[datetime, str, str, str, str]] = []

    if not escalas_df.empty and "created_at" in escalas_df.columns:
        for _, row in escalas_df.tail(8).iterrows():
            dt = _parse_dt(row.get("created_at"))
            ev = str(row.get("event", "Culto"))
            items.append((dt or datetime.min, "scale", "Nova escala criada", ev, _time_ago(dt)))

    if not feed_posts_df.empty and "created_at" in feed_posts_df.columns:
        for _, row in feed_posts_df.tail(5).iterrows():
            dt = _parse_dt(row.get("created_at"))
            author = str(row.get("author_name", row.get("name", ""))).strip() or "Ministério"
            items.append(
                (
                    dt or datetime.min,
                    "feed",
                    "Publicação no feed",
                    author[:40],
                    _time_ago(dt),
                )
            )

    if not louvores_df.empty and "created_at" in louvores_df.columns:
        for _, row in louvores_df.tail(5).iterrows():
            dt = _parse_dt(row.get("created_at"))
            title = str(row.get("title", "Louvor")).strip()[:50]
            items.append(
                (
                    dt or datetime.min,
                    "music",
                    "Louvor no repertório",
                    title,
                    _time_ago(dt),
                )
            )

    items.sort(key=lambda x: x[0], reverse=True)
    seen: set[str] = set()
    out: list[tuple[str, str, str, str]] = []
    for _, kind, title, meta, ago in items:
        key = f"{title}|{meta}"
        if key in seen:
            continue
        seen.add(key)
        out.append((kind, title, meta, ago))
        if len(out) >= limit:
            break
    if not out:
        out.append(("music", "Bem-vindo ao painel", "Explore escalas e repertório", ""))
    return out


def next_upcoming_escala(
    escalas_df: pd.DataFrame,
    *,
    from_date: date | None = None,
) -> dict | None:
    from_date = from_date or date.today()
    if escalas_df.empty or "date" not in escalas_df.columns:
        return None
    df = escalas_df.copy()
    try:
        df["_d"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    except (ValueError, TypeError):
        return None
    df = df[df["_d"].notna() & (df["_d"] >= from_date)].sort_values("_d")
    if df.empty:
        return None
    row = df.iloc[0]
    d = row["_d"]
    return {
        "id": str(row.get("id", "")),
        "event": str(row.get("event", "Culto")),
        "date": d,
        "date_label": d.strftime("%d %b").upper().replace(".", ""),
        "time": str(row.get("time", row.get("hora", "19h00"))).strip() or "19h00",
        "location": str(row.get("location", row.get("local", "Templo IBBJ"))).strip()
        or "Templo IBBJ",
    }


def inject_dashboard_ambient() -> None:
    st.markdown(
        """
        <div class="ig-ambient ig-ambient--blue" aria-hidden="true"></div>
        <div class="ig-ambient ig-ambient--gold" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )


def render_global_header(
    *,
    user_name: str,
    photo_uri: str | None = None,
    notif_count: int = 0,
) -> None:
    badge = (
        f'<span class="ig-hdr-badge">{int(notif_count)}</span>'
        if notif_count > 0
        else ""
    )
    avatar = (
        f'<img src="{photo_uri}" alt="" />'
        if photo_uri
        else '<span class="ig-hdr-avatar-ph"></span>'
    )
    st.markdown(
        f"""
        <div class="ig-top-header">
            <div class="ig-hdr-search-wrap">
                <span class="ig-hdr-search-ico" aria-hidden="true"></span>
            </div>
            <div class="ig-hdr-actions">
                <span class="ig-hdr-action ig-hdr-action--bell" title="Notificações">{badge}</span>
                <span class="ig-hdr-action ig-hdr-action--chat" title="Chat"></span>
                <span class="ig-hdr-avatar-wrap">
                    <span class="ig-hdr-avatar">{avatar}</span>
                    <span class="ig-hdr-online" aria-hidden="true"></span>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([5.5, 1], gap="small")
    with c1:
        st.text_input(
            "Busca global",
            placeholder="Buscar louvores, membros, escalas...",
            key="ig_global_search",
            label_visibility="collapsed",
        )
    with c2:
        b_chat, b_bell, b_prof = st.columns(3)
        with b_bell:
            if st.button("🔔", key="hdr_go_notif", help="Notificações"):
                st.session_state.app_menu = "Chat"
                st.rerun()
        with b_chat:
            if st.button("💬", key="hdr_go_chat", help="Chat"):
                st.session_state.app_menu = "Chat"
                st.rerun()
        with b_prof:
            if st.button("👤", key="hdr_go_prof", help="Perfil"):
                st.session_state.app_menu = "Perfil"
                st.rerun()
    st.markdown('<div class="ig-hdr-spacer"></div>', unsafe_allow_html=True)


def render_dashboard_hero(*, user_name: str, group_name: str) -> None:
    nome = _esc_html(user_name)
    grupo = _esc_html(group_name)
    st.markdown(
        f"""
        <div class="ig-hero-card">
            <div class="ig-hero-left">
                <h1 class="ig-hero-title">Olá, {nome}! 👋</h1>
                <p class="ig-hero-sub">Bem-vindo ao painel do {grupo}.</p>
            </div>
            <blockquote class="ig-hero-verse">
                <span class="ig-hero-verse-label">Salmos 96:1</span>
                Cantai ao Senhor um <em>novo cântico</em>; cantai ao Senhor, toda a terra.
            </blockquote>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _inject_metric_html(fragment: str) -> None:
    try:
        st.html(fragment)
    except Exception:
        st.markdown(fragment, unsafe_allow_html=True)


def render_premium_metrics(stats: list[tuple[str, str, int, str]]) -> None:
    """(icon_key, label, value, link_label) — um card por coluna Streamlit."""
    menu_by_key = {
        "members": "Membros",
        "louvores": "Repertório",
        "escalas": "Escalas",
    }
    btn_keys = {
        "members": "ig_metric_members",
        "louvores": "ig_metric_louvores",
        "escalas": "ig_metric_escalas",
    }
    cols = st.columns(len(stats))
    for col, (icon_key, label, value, link_label) in zip(cols, stats):
        val = value if value > 0 else "—"
        card_html = (
            f'<div class="ig-metric-card ig-metric-card--{_esc_html(icon_key)}">'
            f'<div class="ig-metric-bg" aria-hidden="true"></div>'
            f'<span class="ig-metric-ico ig-metric-ico--{_esc_html(icon_key)}"></span>'
            f'<span class="ig-metric-value">{_esc_html(val)}</span>'
            f'<span class="ig-metric-label">{_esc_html(label)}</span>'
            f"</div>"
        )
        with col:
            _inject_metric_html(card_html)
            if st.button(
                f"{link_label} →",
                key=btn_keys.get(icon_key, f"ig_metric_{icon_key}"),
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.app_menu = menu_by_key.get(icon_key, "Dashboard")
                st.rerun()


def render_warning_card(*, escalado: bool) -> None:
    if escalado:
        return
    st.markdown(
        """
        <div class="ig-warn-card">
            <span class="ig-warn-ico" aria-hidden="true"></span>
            <p class="ig-warn-text">Você não está escalado(a) nesta semana.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Ver minhas escalas", key="ig_warn_escalas", type="primary"):
        st.session_state.app_menu = "Escalas"
        st.rerun()


def render_quick_access_v3(links: list[tuple[str, str]]) -> None:
    """links: [(menu_name, icon_char), ...]"""
    if not links:
        return

    st.markdown(
        '<h3 class="ig-section-title">Acesso rápido</h3>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="ig-quick-grid-open">', unsafe_allow_html=True)
    row_size = 4
    for row_start in range(0, len(links), row_size):
        row_links = links[row_start : row_start + row_size]
        cols = st.columns(row_size)
        for col, (name, icon) in zip(cols, row_links):
            nav_cls = quick_nav_css_class(name)
            with col:
                st.markdown(
                    f'<div class="ig-quick-card {nav_cls}">'
                    f'<span class="ig-quick-ico">{_esc_html(icon)}</span>'
                    f'<span class="ig-quick-label">{_esc_html(name)}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    name,
                    key=f"v3_qn_{name}",
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state.app_menu = name
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_right_panel(
    *,
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    feed_posts_df: pd.DataFrame,
    my_email: str,
    equipe_df: pd.DataFrame,
) -> None:
    st.markdown('<div class="ig-right-panel">', unsafe_allow_html=True)

    nxt = next_upcoming_escala(escalas_df)
    st.markdown('<div class="ig-rpanel-card ig-rpanel-card--hero">', unsafe_allow_html=True)
    if nxt:
        st.markdown(
            f"""
            <p class="ig-rpanel-kicker">Próximo culto</p>
            <div class="ig-rpanel-banner" aria-hidden="true"></div>
            <h4 class="ig-rpanel-event">{_esc_html(nxt["event"])}</h4>
            <p class="ig-rpanel-meta"><strong>{_esc_html(nxt["date_label"])}</strong> · {_esc_html(nxt["time"])}</p>
            <p class="ig-rpanel-loc">📍 {_esc_html(nxt["location"])}</p>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Ver detalhes da escala", key="ig_rp_escala", use_container_width=True):
            st.session_state.app_menu = "Escalas"
            st.session_state.focus_escala_id = nxt["id"]
            st.rerun()
    else:
        st.markdown(
            """
            <p class="ig-rpanel-kicker">Próximo culto</p>
            <div class="ig-rpanel-banner" aria-hidden="true"></div>
            <h4 class="ig-rpanel-event">Nenhum culto agendado</h4>
            <p class="ig-rpanel-meta">Confira a seção de escalas</p>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    activities = recent_activities(escalas_df, feed_posts_df, louvores_df)
    act_html = "".join(
        f"""
        <li class="ig-timeline-item ig-timeline-item--{kind}">
            <span class="ig-timeline-dot"></span>
            <div>
                <strong>{_esc_html(title)}</strong>
                <span>{_esc_html(meta)}</span>
                <em>{_esc_html(ago)}</em>
            </div>
        </li>
        """
        for kind, title, meta, ago in activities
    )
    st.markdown(
        f"""
        <div class="ig-rpanel-card">
            <h4 class="ig-rpanel-title">Atividades recentes</h4>
            <ul class="ig-timeline">{act_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top = top_louvores_ranking(programa_df, louvores_df)
    if top:
        rank_html = "".join(
            f"""
            <li class="ig-rank-item">
                <span class="ig-rank-n">{i}</span>
                <div>
                    <strong>{_esc_html(title)}</strong>
                    <span>{cnt} execuções</span>
                </div>
            </li>
            """
            for i, (title, cnt) in enumerate(top, 1)
        )
    else:
        rank_html = '<li class="ig-rank-item"><span>Sem dados de execução ainda</span></li>'

    st.markdown(
        f"""
        <div class="ig-rpanel-card">
            <h4 class="ig-rpanel-title">Top louvores da igreja</h4>
            <ol class="ig-rank-list">{rank_html}</ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Ver repertório completo", key="ig_rp_repertorio", use_container_width=True):
        st.session_state.app_menu = "Repertório"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_ministry_tip() -> None:
    if st.session_state.get("ig_tip_dismissed"):
        return
    st.markdown(
        """
        <div class="ig-tip-card">
            <span class="ig-tip-ico" aria-hidden="true"></span>
            <div class="ig-tip-body">
                <strong>Dica do ministério</strong>
                <p>Revise o repertório da próxima escala com antecedência e confirme presença no grupo.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Dispensar", key="ig_tip_dismiss"):
        st.session_state.ig_tip_dismissed = True
        st.rerun()


def render_week_culto_cards(
    semana: pd.DataFrame,
    *,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_full: pd.DataFrame,
    minhas_ids: set[str],
) -> None:
    if semana.empty:
        st.markdown(
            '<div class="ig-week-empty">Nenhum culto nesta semana por enquanto.</div>',
            unsafe_allow_html=True,
        )
        return

    for _, escala in semana.iterrows():
        eid = str(escala.get("id", ""))
        ev = str(escala.get("event", "Culto"))
        dt_raw = str(escala.get("date", ""))
        try:
            dt = pd.to_datetime(dt_raw)
            dow = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"][dt.weekday()]
            day_num = dt.strftime("%d")
            month = dt.strftime("%b").upper().replace(".", "")
        except (ValueError, TypeError):
            dow, day_num, month = "—", "—", ""
        hora = str(escala.get("time", escala.get("hora", ""))).strip()
        local = str(escala.get("location", escala.get("local", ""))).strip()
        st.markdown(
            f"""
            <div class="ig-week-card">
                <div class="ig-week-badge">
                    <span class="ig-week-dow">{_esc_html(dow)}</span>
                    <span class="ig-week-day">{_esc_html(day_num)}</span>
                    <span class="ig-week-mon">{_esc_html(month)}</span>
                </div>
                <div class="ig-week-body">
                    <h4>{_esc_html(ev)}</h4>
                    <p>{_esc_html(hora)} · {_esc_html(local or "Templo IBBJ")}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"Abrir escala · {ev[:24]}", key=f"ig_wk_{eid}", use_container_width=True):
            st.session_state.app_menu = "Escalas"
            st.session_state.focus_escala_id = eid
            st.rerun()
