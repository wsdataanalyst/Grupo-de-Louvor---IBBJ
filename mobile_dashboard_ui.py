"""Dashboard mobile premium (preview) — layout estilo app nativo."""

from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from dashboard_ui import next_upcoming_escala
from ui_html import inject_ui_html


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def mobile_dashboard_css() -> str:
    return """
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    body:has(.ig-mobile-app) [data-testid="stSidebar"] {
        display: none !important;
    }
    body:has(.ig-mobile-app) [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 28rem !important;
        margin: 0 auto !important;
        padding: 0.5rem 0.85rem 6.5rem !important;
    }
    body:has(.ig-mobile-app) [data-testid="stHeader"] {
        display: none !important;
    }

    .ig-mobile-app {
        font-family: 'Manrope', system-ui, sans-serif;
        color: #f8fafc;
    }
    .ig-m-lab-banner {
        background: linear-gradient(90deg, rgba(139,92,246,.35), rgba(37,99,235,.25));
        border: 1px solid rgba(139,92,246,.45);
        border-radius: 14px;
        padding: 0.5rem 0.75rem;
        font-size: 0.72rem;
        color: #e9d5ff;
        margin-bottom: 0.85rem;
        text-align: center;
    }
    .ig-m-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 0.65rem;
        margin-bottom: 1.1rem;
    }
    .ig-m-user {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-width: 0;
    }
    .ig-m-avatar-wrap {
        position: relative;
        flex-shrink: 0;
    }
    .ig-m-avatar {
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 999px;
        object-fit: cover;
        border: 2px solid #3b82f6;
    }
    .ig-m-avatar-ph {
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 999px;
        background: rgba(59,130,246,.15);
        border: 2px solid #3b82f6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    .ig-m-online {
        position: absolute;
        bottom: 2px;
        right: 2px;
        width: 0.75rem;
        height: 0.75rem;
        background: #4ade80;
        border-radius: 999px;
        border: 2px solid #030712;
    }
    .ig-m-greet h1 {
        font-size: 1.35rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
    }
    .ig-m-greet p {
        margin: 0.25rem 0 0;
        color: #94a3b8;
        font-size: 0.88rem;
    }
    .ig-m-top-actions {
        display: flex;
        gap: 0.45rem;
        flex-shrink: 0;
    }
    .ig-m-icon-btn {
        width: 2.75rem;
        height: 2.75rem;
        border-radius: 1rem;
        background: rgba(15,23,42,.72);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,.08);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        position: relative;
    }
    .ig-m-badge {
        position: absolute;
        top: -4px;
        right: -4px;
        min-width: 1.1rem;
        height: 1.1rem;
        padding: 0 0.2rem;
        border-radius: 999px;
        background: #facc15;
        color: #000;
        font-size: 0.62rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .ig-m-glass {
        background: rgba(15,23,42,.72);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 1.75rem;
    }
    .ig-m-glow-purple { box-shadow: 0 0 30px rgba(139,92,246,.22); }
    .ig-m-glow-blue { box-shadow: 0 0 30px rgba(37,99,235,.18); }
    .ig-m-glow-gold { box-shadow: 0 0 30px rgba(212,160,23,.18); }

    .ig-m-hero {
        position: relative;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .ig-m-hero-bg {
        position: absolute;
        inset: 0;
        background: url('https://images.unsplash.com/photo-1504052434569-70ad5836ab65?q=80&w=1200&auto=format&fit=crop') center/cover;
        opacity: 0.22;
    }
    .ig-m-hero-body { position: relative; padding: 1.15rem; }
    .ig-m-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(139,92,246,.2);
        color: #d8b4fe;
        padding: 0.35rem 0.75rem;
        border-radius: 0.75rem;
        font-size: 0.72rem;
        font-weight: 700;
        margin-bottom: 0.65rem;
    }
    .ig-m-hero h2 {
        font-size: 1.65rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0 0 0.5rem;
    }
    .ig-m-hero-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.85rem;
        color: #cbd5e1;
        font-size: 0.88rem;
        margin-bottom: 0.85rem;
    }
    .ig-m-hero-foot {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    .ig-m-pill {
        padding: 0.55rem 0.85rem;
        border-radius: 0.85rem;
        font-size: 0.82rem;
        background: rgba(15,23,42,.55);
        border: 1px solid rgba(255,255,255,.06);
    }

    .ig-m-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.65rem;
        margin-bottom: 1rem;
    }
    .ig-m-stat { padding: 0.9rem; }
    .ig-m-stat-ico { font-size: 1.6rem; margin-bottom: 0.25rem; }
    .ig-m-stat-val { font-size: 1.65rem; font-weight: 800; line-height: 1; }
    .ig-m-stat-lbl { color: #94a3b8; font-size: 0.78rem; margin-top: 0.25rem; }

    .ig-m-section-hdr {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0 0 0.65rem;
    }
    .ig-m-section-hdr h3 {
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0;
    }
    .ig-m-link { color: #c4b5fd; font-size: 0.82rem; font-weight: 600; }

    .ig-m-scale-card { padding: 1rem; margin-bottom: 1rem; position: relative; overflow: hidden; }
    .ig-m-scale-bg {
        position: absolute;
        inset: 0;
        background: url('https://images.unsplash.com/photo-1516280440614-37939bbacd81?q=80&w=1200&auto=format&fit=crop') center/cover;
        opacity: 0.08;
    }
    .ig-m-scale-body { position: relative; display: flex; gap: 0.85rem; align-items: flex-start; }
    .ig-m-scale-ico {
        width: 3.25rem;
        height: 3.25rem;
        border-radius: 1rem;
        background: rgba(59,130,246,.12);
        border: 1px solid rgba(59,130,246,.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .ig-m-scale-title { font-size: 1.05rem; font-weight: 800; margin: 0; }
    .ig-m-scale-sub { color: #94a3b8; font-size: 0.82rem; margin: 0.25rem 0 0; }
    .ig-m-status-ok {
        display: inline-flex;
        margin-top: 0.45rem;
        padding: 0.3rem 0.65rem;
        border-radius: 0.65rem;
        background: rgba(34,197,94,.18);
        color: #86efac;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .ig-m-quick {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.55rem;
        margin-bottom: 1rem;
    }
    .ig-m-quick-item {
        padding: 0.85rem;
        text-align: center;
        position: relative;
    }
    .ig-m-quick-item .ico { font-size: 1.65rem; margin-bottom: 0.35rem; }
    .ig-m-quick-item .lbl { font-size: 0.88rem; font-weight: 700; }

    .ig-m-alerts { padding: 0.85rem 1rem; margin-bottom: 1rem; }
    .ig-m-alert-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.55rem 0;
        border-bottom: 1px solid rgba(255,255,255,.06);
    }
    .ig-m-alert-row:last-child { border-bottom: none; }
    .ig-m-alert-ico {
        width: 2.75rem;
        height: 2.75rem;
        border-radius: 0.85rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    .ig-m-alert-body { flex: 1; min-width: 0; }
    .ig-m-alert-title { font-weight: 700; font-size: 0.9rem; margin: 0; }
    .ig-m-alert-sub { color: #94a3b8; font-size: 0.78rem; margin: 0.15rem 0 0; }
    .ig-m-alert-time { color: #64748b; font-size: 0.75rem; flex-shrink: 0; }

    .ig-m-nav-wrap {
        position: fixed;
        bottom: 0.65rem;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100% - 1.25rem);
        max-width: 26rem;
        z-index: 999;
        padding: 0.55rem 0.35rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ig-m-nav-item {
        flex: 1;
        text-align: center;
        color: #94a3b8;
        font-size: 0.62rem;
        font-weight: 600;
    }
    .ig-m-nav-item.active { color: #c4b5fd; }
    .ig-m-nav-item .ico { font-size: 1.15rem; display: block; margin-bottom: 0.15rem; }

    /* Botoes Streamlit escondidos — acionados pelo HTML visual */
    .ig-m-actions [data-testid="stHorizontalBlock"] {
        gap: 0.35rem !important;
    }
    .ig-m-actions .stButton > button {
        font-size: 0.72rem !important;
        min-height: 2.25rem !important;
        padding: 0.35rem 0.5rem !important;
        border-radius: 12px !important;
    }
    .ig-m-nav-btns [data-testid="stHorizontalBlock"] {
        position: fixed !important;
        bottom: 0.5rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: min(26rem, calc(100% - 1rem)) !important;
        z-index: 1000 !important;
        background: rgba(15,23,42,.88) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255,255,255,.1) !important;
        border-radius: 1.75rem !important;
        padding: 0.35rem 0.25rem !important;
        margin: 0 !important;
    }
    .ig-m-nav-btns .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        font-size: 0.62rem !important;
        min-height: 2.5rem !important;
        box-shadow: none !important;
    }
    .ig-m-nav-btns [data-testid="stColumn"]:first-child .stButton > button {
        color: #c4b5fd !important;
        font-weight: 700 !important;
    }
    """


@dataclass
class MobileDashboardCtx:
    user_name: str
    photo_uri: str | None
    notif_count: int
    chat_unread: int
    n_louvores: int
    n_members: int
    n_cultos_semana: int
    n_pendencias: int
    next_culto: dict | None
    my_scale: dict | None
    quick_links: list[tuple[str, str, str]]
    alerts: list[tuple[str, str, str, str, str]]


def _first_name(full: str) -> str:
    parts = str(full or "").strip().split()
    return parts[0] if parts else "Membro"


def _weekday_pt(d: date) -> str:
    names = ("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo")
    return names[d.weekday()]


def build_mobile_dashboard_ctx(
    *,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    feed_posts_df: pd.DataFrame,
    my_email: str,
    user_name: str,
    photo_uri: str | None,
    chat_unread: int,
    pendencias: int,
    quick_links: list[tuple[str, str]],
) -> MobileDashboardCtx:
    nxt = next_upcoming_escala(escalas_df)
    my_scale = None
    if nxt and not equipe_df.empty:
        eid = str(nxt.get("id", ""))
        eq = equipe_df[equipe_df["escala_id"].astype(str) == eid]
        mine = eq[eq["member_email"].astype(str).str.lower() == my_email.lower()]
        if not mine.empty:
            row = mine.iloc[0]
            my_scale = {
                "funcao": str(row.get("funcao", "Integrante")),
                "event": nxt["event"],
                "when": f"{_weekday_pt(nxt['date'])} • {nxt.get('time', '18h')}",
                "confirmed": True,
                "escala_id": eid,
            }

    today = date.today()
    week_end = today + timedelta(days=(6 - today.weekday()))
    cultos_sem = 0
    if not escalas_df.empty and "date" in escalas_df.columns:
        try:
            dts = pd.to_datetime(escalas_df["date"], errors="coerce").dt.date
            cultos_sem = int(((dts >= today) & (dts <= week_end)).sum())
        except (ValueError, TypeError):
            cultos_sem = 0

    alerts: list[tuple[str, str, str, str, str]] = []
    if my_scale:
        alerts.append(
            ("purple", "🔔", "Você foi escalado", f"{my_scale['event']} • {my_scale['when']}", "Agora")
        )
    if chat_unread > 0:
        alerts.append(
            ("blue", "💬", "Nova mensagem no chat", f"{chat_unread} não lida(s)", "Recente")
        )
    if not feed_posts_df.empty and "created_at" in feed_posts_df.columns:
        try:
            latest = feed_posts_df.sort_values("created_at", ascending=False).iloc[0]
            title = str(latest.get("title", latest.get("message", "Aviso"))).strip()[:48]
            alerts.append(("gold", "📢", "Aviso do ministério", title, "Feed"))
        except (IndexError, KeyError):
            pass
    if not alerts:
        alerts.append(("blue", "🎵", "Bem-vindo", "Explore repertório e escalas", ""))

    quick: list[tuple[str, str, str]] = []
    icon_map = {
        "Repertório": ("🎵", "ig-m-glow-purple"),
        "Playlist": ("🎧", ""),
        "Chat": ("💬", "ig-m-glow-blue"),
        "Sugestão de louvor": ("💡", "ig-m-glow-gold"),
        "Escalas": ("📅", "ig-m-glow-gold"),
    }
    for name, icon in quick_links[:4]:
        em, glow = icon_map.get(name, ("🎵", ""))
        quick.append((name, em, glow))

    return MobileDashboardCtx(
        user_name=_first_name(user_name),
        photo_uri=photo_uri,
        notif_count=min(9, pendencias + chat_unread),
        chat_unread=chat_unread,
        n_louvores=len(louvores_df),
        n_members=len(members_df),
        n_cultos_semana=cultos_sem,
        n_pendencias=pendencias,
        next_culto=nxt,
        my_scale=my_scale,
        quick_links=quick,
        alerts=alerts[:3],
    )


def render_mobile_dashboard_shell(ctx: MobileDashboardCtx) -> None:
    inject_ui_html('<div class="ig-mobile-app">')
    inject_ui_html(
        '<div class="ig-m-lab-banner">Modo teste mobile — layout preview. '
        "Desative em Laboratorio mobile ou remova <code>?mobile_lab=1</code>.</div>"
    )

    avatar = (
        f'<img class="ig-m-avatar" src="{_esc(ctx.photo_uri)}" alt="">'
        if ctx.photo_uri
        else '<div class="ig-m-avatar-ph">🎤</div>'
    )
    badge = (
        f'<span class="ig-m-badge">{ctx.notif_count}</span>' if ctx.notif_count > 0 else ""
    )

    inject_ui_html(
        f"""
        <div class="ig-m-top">
          <div class="ig-m-user">
            <div class="ig-m-avatar-wrap">{avatar}<span class="ig-m-online"></span></div>
            <div class="ig-m-greet">
              <h1>Olá, {_esc(ctx.user_name)} 👋</h1>
              <p>Que bom te ver por aqui!</p>
            </div>
          </div>
          <div class="ig-m-top-actions">
            <div class="ig-m-icon-btn ig-m-glow-purple">🔔{badge}</div>
            <div class="ig-m-icon-btn">☰</div>
          </div>
        </div>
        """
    )

    if ctx.next_culto:
        nc = ctx.next_culto
        when = f"{_weekday_pt(nc['date'])} • {_esc(nc.get('time', '18h'))}"
        inject_ui_html(
            f"""
            <div class="ig-m-glass ig-m-glow-purple ig-m-hero">
              <div class="ig-m-hero-bg"></div>
              <div class="ig-m-hero-body">
                <div class="ig-m-kicker">📅 PRÓXIMO CULTO</div>
                <h2>{_esc(nc['event'])}</h2>
                <div class="ig-m-hero-meta"><span>📆 {when}</span></div>
                <div class="ig-m-hero-foot">
                  <div class="ig-m-pill">👥 Equipe na escala</div>
                </div>
              </div>
            </div>
            """
        )

    inject_ui_html(
        f"""
        <div class="ig-m-stats">
          <div class="ig-m-glass ig-m-glow-purple ig-m-stat">
            <div class="ig-m-stat-ico">🎵</div>
            <div class="ig-m-stat-val">{ctx.n_louvores}</div>
            <div class="ig-m-stat-lbl">Louvores cadastrados</div>
          </div>
          <div class="ig-m-glass ig-m-glow-blue ig-m-stat">
            <div class="ig-m-stat-ico">👥</div>
            <div class="ig-m-stat-val">{ctx.n_members}</div>
            <div class="ig-m-stat-lbl">Membros ativos</div>
          </div>
          <div class="ig-m-glass ig-m-glow-gold ig-m-stat">
            <div class="ig-m-stat-ico">📅</div>
            <div class="ig-m-stat-val">{ctx.n_cultos_semana}</div>
            <div class="ig-m-stat-lbl">Cultos esta semana</div>
          </div>
          <div class="ig-m-glass ig-m-stat">
            <div class="ig-m-stat-ico">✅</div>
            <div class="ig-m-stat-val">{ctx.n_pendencias}</div>
            <div class="ig-m-stat-lbl">Pendências para você</div>
          </div>
        </div>
        """
    )

    if ctx.my_scale:
        ms = ctx.my_scale
        inject_ui_html(
            f"""
            <div class="ig-m-section-hdr"><h3>🎤 Sua escala</h3><span class="ig-m-link">ver todas</span></div>
            <div class="ig-m-glass ig-m-scale-card">
              <div class="ig-m-scale-bg"></div>
              <div class="ig-m-scale-body">
                <div class="ig-m-scale-ico">🎙️</div>
                <div>
                  <p class="ig-m-scale-title">{_esc(ms['funcao'])}</p>
                  <p class="ig-m-scale-sub">{_esc(ms['event'])} • {_esc(ms['when'])}</p>
                  <span class="ig-m-status-ok">Confirmado ✅</span>
                </div>
              </div>
            </div>
            """
        )

    if ctx.quick_links:
        items = "".join(
            f'<div class="ig-m-glass ig-m-quick-item {glow}">'
            f'<div class="ico">{_esc(ico)}</div><div class="lbl">{_esc(name)}</div></div>'
            for name, ico, glow in ctx.quick_links
        )
        inject_ui_html(
            f'<div class="ig-m-section-hdr"><h3>Acesso rápido</h3><span class="ig-m-link">Ver tudo</span></div>'
            f'<div class="ig-m-quick">{items}</div>'
        )

    alert_rows = ""
    for tone, ico, title, sub, when in ctx.alerts:
        bg = {
            "purple": "rgba(139,92,246,.12)",
            "blue": "rgba(59,130,246,.12)",
            "gold": "rgba(212,160,23,.12)",
        }.get(tone, "rgba(59,130,246,.12)")
        alert_rows += (
            f'<div class="ig-m-alert-row">'
            f'<div class="ig-m-alert-ico" style="background:{bg}">{ico}</div>'
            f'<div class="ig-m-alert-body"><p class="ig-m-alert-title">{_esc(title)}</p>'
            f'<p class="ig-m-alert-sub">{_esc(sub)}</p></div>'
            f'<span class="ig-m-alert-time">{_esc(when)}</span></div>'
        )
    inject_ui_html(
        f'<div class="ig-m-section-hdr"><h3>Avisos importantes</h3><span class="ig-m-link">ver todos</span></div>'
        f'<div class="ig-m-glass ig-m-alerts">{alert_rows}</div>'
    )
    inject_ui_html("</div>")


def render_mobile_dashboard_actions(ctx: MobileDashboardCtx) -> None:
    """Botoes reais (Streamlit) para navegar — abaixo do HTML visual."""
    st.markdown('<div class="ig-m-actions">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if ctx.next_culto and st.button(
            "Ver escala completa",
            key="m_lab_escala_hero",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.app_menu = "Escalas"
            st.session_state.focus_escala_id = str(ctx.next_culto.get("id", ""))
            st.rerun()
    with c2:
        if ctx.my_scale and st.button("Minhas escalas", key="m_lab_minhas", use_container_width=True):
            st.session_state.app_menu = "Escalas"
            st.rerun()

    if ctx.quick_links:
        qcols = st.columns(min(4, len(ctx.quick_links)))
        for col, (name, _, _) in zip(qcols, ctx.quick_links):
            with col:
                if st.button(name, key=f"m_lab_q_{name}", use_container_width=True):
                    st.session_state.app_menu = name
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="ig-m-nav-btns">', unsafe_allow_html=True)
    nav = [
        ("Dashboard", "🏠"),
        ("Escalas", "📅"),
        ("Repertório", "🎵"),
        ("Chat", "💬"),
        ("Perfil", "👤"),
    ]
    cols = st.columns(5)
    for col, (menu, icon) in zip(cols, nav):
        with col:
            label = f"{icon}\n{menu[:5]}"
            if menu == "Dashboard":
                label = f"{icon}\nInício"
            if st.button(label, key=f"m_lab_nav_{menu}", use_container_width=True):
                st.session_state.app_menu = menu
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def inject_mobile_dashboard_theme() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
          background:
            radial-gradient(circle at top left, rgba(37,99,235,.20), transparent 30%),
            radial-gradient(circle at top right, rgba(139,92,246,.20), transparent 30%),
            #030712 !important;
        }
        """
        + mobile_dashboard_css()
        + "</style>",
        unsafe_allow_html=True,
    )


def show_mobile_dashboard(
    *,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    feed_posts_df: pd.DataFrame,
    members_visible_count: int,
    user_name: str,
    my_email: str,
    photo_uri: str | None,
    chat_unread: int,
    pendencias: int,
    quick_links: list[tuple[str, str]],
) -> None:
    # Mobile Lab: layout "cara de app" inspirado no mock premium (teste).
    from mobile_lab_ui import render_mobile_lab_dashboard

    render_mobile_lab_dashboard(
        members_df=members_df,
        louvores_df=louvores_df,
        escalas_df=escalas_df,
        chat_unread=int(chat_unread),
        user_full_name=str(user_name or ""),
        photo_uri=str(photo_uri or ""),
        notif_count=int(pendencias),
    )
