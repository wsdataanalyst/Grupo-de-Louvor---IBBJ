"""Mobile Lab — Membros do ministério (layout premium)."""

from __future__ import annotations

import html
from datetime import date

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme

FILTERS: tuple[tuple[str, str], ...] = (
    ("todos", "Todos"),
    ("lideres", "Líderes"),
    ("coord", "Coord."),
    ("musicos", "Músicos"),
    ("inativos", "Inativos"),
)


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _filter_key() -> str:
    f = str(st.session_state.get("ml_membros_filter", "todos")).strip()
    valid = {k for k, _ in FILTERS}
    return f if f in valid else "todos"


def _search_query() -> str:
    return str(st.session_state.get("ml_membros_search", "")).strip().lower()


def _sort_key() -> str:
    s = str(st.session_state.get("ml_membros_sort", "nome")).strip()
    return s if s in ("nome", "escalas") else "nome"


def mobile_membros_css() -> str:
    return r"""
    body:has(#ml-membros-page) [data-testid="stMain"] .block-container{
      padding-top: 0.35rem !important;
      max-width: 900px !important;
    }
    body:has(#ml-membros-page) .music-panel-title,
    body:has(#ml-membros-page) .members-leader-wrap{ display: none !important; }

    .ml-mem-titulo{
      font-size: 1.45rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;
    }
    .ml-mem-sub{ color: #b7bfd1; font-size: 0.8rem; margin: 0.3rem 0 0; }

    .ml-mem-hero{
      background: linear-gradient(135deg, #5B21B6, #312E81);
      border-radius: 24px; padding: 1.1rem 1rem; margin: 0.7rem 0 0.85rem;
      border: 1px solid rgba(255,255,255,.1);
      box-shadow: 0 0 36px rgba(91,33,182,.22);
      display: flex; align-items: center; gap: 0.85rem;
    }
    .ml-mem-hero-ico{
      width: 52px; height: 52px; border-radius: 18px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      background: rgba(255,255,255,.12); font-size: 1.5rem;
    }
    .ml-mem-hero-text{ flex: 1; min-width: 0; }
    .ml-mem-hero-text h2{
      margin: 0 0 0.25rem; font-size: 0.98rem; font-weight: 800; line-height: 1.25;
    }
    .ml-mem-hero-text p{
      margin: 0; font-size: 0.74rem; color: rgba(226,232,240,.9); line-height: 1.4;
    }
    .ml-mem-hero-total{
      text-align: center; padding: 0.55rem 0.75rem; border-radius: 16px;
      background: rgba(0,0,0,.2); border: 1px solid rgba(255,255,255,.1);
      flex-shrink: 0;
    }
    .ml-mem-hero-total b{
      display: block; font-size: 1.45rem; font-weight: 800; line-height: 1;
    }
    .ml-mem-hero-total span{
      font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.04em;
      color: rgba(226,232,240,.85); font-weight: 700;
    }

    .ml-mem-stat-grid{
      display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.45rem; margin-bottom: 0.85rem;
    }
    @media (max-width: 400px){
      .ml-mem-stat-grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    .ml-mem-stat{
      background: #091633; border-radius: 18px; padding: 0.7rem 0.35rem;
      text-align: center; border: 1px solid rgba(255,255,255,.06);
    }
    .ml-mem-stat h2{ margin: 0; font-size: 1.35rem; font-weight: 800; line-height: 1; }
    .ml-mem-stat span{
      display: block; margin-top: 0.3rem; font-size: 0.62rem; font-weight: 700;
      color: #94a3b8; text-transform: uppercase; letter-spacing: 0.03em;
    }

    .ml-mem-card{
      display: flex; align-items: center; gap: 0.7rem;
      background: rgba(7,20,50,.75); border: 1px solid rgba(255,255,255,.08);
      border-radius: 22px; padding: 0.8rem 0.85rem; margin-bottom: 0.55rem;
    }
    .ml-mem-avatar-wrap{ position: relative; flex-shrink: 0; }
    .ml-mem-avatar-wrap img, .ml-mem-avatar-wrap .member-avatar-ph{
      border-radius: 50% !important; width: 48px !important; height: 48px !important;
    }
    .ml-mem-dot{
      position: absolute; right: 0; bottom: 0; width: 11px; height: 11px;
      border-radius: 50%; border: 2px solid #071432;
    }
    .ml-mem-dot--on{ background: #22c55e; }
    .ml-mem-dot--off{ background: #f59e0b; }
    .ml-mem-body{ flex: 1; min-width: 0; }
    .ml-mem-name-row{
      display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem;
    }
    .ml-mem-name{ font-size: 0.9rem; font-weight: 700; margin: 0; }
    .ml-mem-badge{
      display: inline-block; padding: 0.2rem 0.55rem; border-radius: 999px;
      font-size: 0.62rem; font-weight: 700;
    }
    .ml-mem-badge--lider{ background: #3b0764; color: #f3e8ff; }
    .ml-mem-badge--coord{ background: #78350f; color: #fef3c7; }
    .ml-mem-badge--musico{ background: #172554; color: #bfdbfe; }
    .ml-mem-badge--outro{ background: #1e293b; color: #cbd5e1; }
    .ml-mem-func{
      margin-top: 0.2rem; font-size: 0.74rem; color: #94a3b8;
    }
    .ml-mem-side{ text-align: right; flex-shrink: 0; }
    .ml-mem-status{ font-size: 0.72rem; font-weight: 700; }
    .ml-mem-status--on{ color: #22c55e; }
    .ml-mem-status--off{ color: #94a3b8; }
    .ml-mem-meta{ font-size: 0.65rem; color: #64748b; margin-top: 0.15rem; }

    .ml-mem-invite{
      background: linear-gradient(135deg, rgba(91,33,182,.45), rgba(49,46,129,.85));
      border-radius: 22px; padding: 1rem; margin: 0.85rem 0 0.5rem;
      border: 1px solid rgba(139,92,246,.28);
      display: flex; align-items: center; gap: 0.75rem;
    }
    .ml-mem-invite-text h3{ margin: 0 0 0.2rem; font-size: 0.92rem; font-weight: 800; }
    .ml-mem-invite-text p{ margin: 0; font-size: 0.74rem; color: #cbd5e1; line-height: 1.35; }
    .ml-mem-section{
      margin: 0.65rem 0 0.45rem; font-size: 0.95rem; font-weight: 800;
      display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
    }
    .ml-mem-empty{
      padding: 1rem; border-radius: 20px; text-align: center;
      background: rgba(15,23,42,.55); border: 1px dashed rgba(255,255,255,.1);
      color: #94a3b8; font-size: 0.82rem;
    }

    body:has(#ml-membros-page) [class*="st-key-ml_mem_filter_"] .stButton > button{
      border-radius: 14px !important; min-height: 2rem !important;
      font-size: 0.7rem !important; font-weight: 700 !important; white-space: nowrap !important;
    }
    body:has(#ml-membros-page) [class*="st-key-ml_mem_filters"] [data-testid="stHorizontalBlock"]{
      display: flex !important; flex-wrap: nowrap !important;
      overflow-x: auto !important; gap: 6px !important; scrollbar-width: none;
    }
    body:has(#ml-membros-page) [class*="st-key-ml_mem_filters"] [data-testid="stColumn"]{
      flex: 0 0 auto !important; width: auto !important; max-width: none !important;
    }
    body:has(#ml-membros-page) [class*="st-key-ml_mem_search"] .stTextInput > div > div > input{
      border-radius: 18px !important; min-height: 2.85rem !important;
      background: rgba(7,21,45,.92) !important; border: 1px solid rgba(255,255,255,.08) !important;
    }
    body:has(#ml-membros-page) [class*="st-key-ml_mem_invite_btn"] .stLinkButton > a,
    body:has(#ml-membros-page) [class*="st-key-ml_mem_add"] .stButton > button{
      border-radius: 16px !important; font-weight: 800 !important;
      background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
      color: #fff !important; border: none !important;
    }
    """


def _func_icon(roles_str: str) -> str:
    r = str(roles_str).lower()
    if "vocal" in r:
        return "🎤"
    if "guitar" in r:
        return "🎸"
    if "bater" in r:
        return "🥁"
    if "teclad" in r:
        return "🎹"
    if "baix" in r:
        return "🎸"
    if "violon" in r:
        return "🎻"
    if "técnico" in r or "tecnico" in r:
        return "🎚"
    return "🎵"


def _member_category(roles_str: str) -> str:
    from app import (
        ROLE_LIDER,
        ROLE_ORG_MUSICAL,
        ROLE_ORG_VOCAL,
        split_member_roles,
    )

    leadership, musician = split_member_roles(roles_str)
    if ROLE_LIDER in leadership:
        return "lider"
    if ROLE_ORG_MUSICAL in leadership or ROLE_ORG_VOCAL in leadership:
        return "coord"
    if musician:
        return "musico"
    return "outro"


def _badge_label(roles_str: str, category: str) -> str:
    from app import ROLE_ORG_MUSICAL, ROLE_ORG_VOCAL, split_member_roles

    if category == "lider":
        return "Líder"
    if category == "coord":
        leadership, _ = split_member_roles(roles_str)
        if ROLE_ORG_VOCAL in leadership:
            return "Coord. Vocal"
        if ROLE_ORG_MUSICAL in leadership:
            return "Coord. Musical"
        return "Coordenador"
    if category == "musico":
        return "Músico"
    return "Integrante"


def _status_for_member(
    email: str,
    stats,
    *,
    my_email: str,
) -> tuple[str, str, str]:
    """Retorna (dot_class, status_class, label)."""
    if email == my_email:
        return "ml-mem-dot--on", "ml-mem-status--on", "Online"
    if stats.escalado_agora:
        return "ml-mem-dot--on", "ml-mem-status--on", "Escalado"
    if stats.last_date:
        delta = (date.today() - stats.last_date).days
        if delta == 0:
            return "ml-mem-dot--on", "ml-mem-status--on", "Hoje"
        if delta < 7:
            return "ml-mem-dot--off", "ml-mem-status--off", f"Há {delta}d"
        if delta < 30:
            weeks = max(1, delta // 7)
            return "ml-mem-dot--off", "ml-mem-status--off", f"Há {weeks} sem"
        return "ml-mem-dot--off", "ml-mem-status--off", f"Há {delta // 30} mês"
    return "ml-mem-dot--off", "ml-mem-status--off", "Sem escala"


def _compute_stats(visible: pd.DataFrame) -> dict[str, int]:
    counts = {"total": len(visible), "lideres": 0, "coord": 0, "musicos": 0}
    for _, row in visible.iterrows():
        cat = _member_category(str(row.get("roles", "")))
        if cat == "lider":
            counts["lideres"] += 1
        elif cat == "coord":
            counts["coord"] += 1
        elif cat == "musico":
            counts["musicos"] += 1
    return counts


def _prepare_rows(
    visible: pd.DataFrame,
    *,
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    leader_view: bool,
) -> list[dict]:
    from app import member_display_name, member_photo_html, roles_for_public_display
    from escala_member_stats import member_escala_stats

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    ref = date.today()
    rows: list[dict] = []
    for _, row in visible.iterrows():
        email = str(row.get("email", "")).strip().lower()
        nome = member_display_name(row)
        roles_str = str(row.get("roles", ""))
        cat = _member_category(roles_str)
        funcao = roles_for_public_display(roles_str)
        stats = (
            member_escala_stats(email, escalas_df, equipe_df, ref=ref)
            if leader_view and email
            else None
        )
        dot_cls, st_cls, st_lbl = (
            _status_for_member(email, stats, my_email=my_email)
            if stats
            else ("ml-mem-dot--off", "ml-mem-status--off", "—")
        )
        rows.append(
            {
                "email": email,
                "nome": nome,
                "roles": roles_str,
                "category": cat,
                "badge": _badge_label(roles_str, cat),
                "funcao": funcao,
                "func_icon": _func_icon(roles_str),
                "avatar": member_photo_html(email, members_df, 48, name=nome),
                "dot_cls": dot_cls,
                "status_cls": st_cls,
                "status_lbl": st_lbl,
                "stats": stats,
                "year_count": stats.year_count if stats else 0,
            }
        )
    return rows


def _filter_rows(rows: list[dict], filt: str) -> list[dict]:
    if filt == "lideres":
        return [r for r in rows if r["category"] == "lider"]
    if filt == "coord":
        return [r for r in rows if r["category"] == "coord"]
    if filt == "musicos":
        return [r for r in rows if r["category"] == "musico"]
    if filt == "inativos":
        return [r for r in rows if r["year_count"] == 0 and r["category"] != "lider"]
    return rows


def _search_rows(rows: list[dict], query: str) -> list[dict]:
    if not query:
        return rows
    out = []
    for r in rows:
        blob = f"{r['nome']} {r['funcao']} {r['email']} {r['roles']}".lower()
        if query in blob:
            out.append(r)
    return out


def _sort_rows(rows: list[dict], sort: str) -> list[dict]:
    if sort == "escalas":
        return sorted(
            rows,
            key=lambda r: (-int(r["year_count"]), r["nome"].lower()),
        )
    return sorted(rows, key=lambda r: r["nome"].lower())


def _member_card_html(row: dict, *, leader_view: bool) -> str:
    meta = ""
    if leader_view and row.get("stats"):
        st = row["stats"]
        meta = (
            f'<div class="ml-mem-meta">{st.month_count} culto(s) no mês · '
            f"{st.year_count} no ano</div>"
        )
    return (
        f'<div class="ml-mem-card">'
        f'<div class="ml-mem-avatar-wrap">{row["avatar"]}'
        f'<span class="ml-mem-dot {row["dot_cls"]}"></span></div>'
        f'<div class="ml-mem-body">'
        f'<div class="ml-mem-name-row">'
        f'<p class="ml-mem-name">{_esc(row["nome"])}</p>'
        f'<span class="ml-mem-badge ml-mem-badge--{row["category"]}">'
        f'{_esc(row["badge"])}</span></div>'
        f'<div class="ml-mem-func">{row["func_icon"]} {_esc(row["funcao"])}</div>'
        f"{meta}</div>"
        f'<div class="ml-mem-side">'
        f'<div class="ml-mem-status {row["status_cls"]}">{_esc(row["status_lbl"])}</div>'
        f"</div></div>"
    )


def _render_header(*, total: int, leader_view: bool) -> None:
    st.markdown(
        f"""
        <div style="display:flex;align-items:flex-start;justify-content:space-between;
          gap:0.65rem;padding-right:2.5rem;">
          <div>
            <div class="ml-mem-titulo">👥 Membros</div>
            <p class="ml-mem-sub">Gerencie os integrantes do ministério</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if leader_view:
        with st.container(key="ml_mem_add"):
            if st.button("➕", key="ml_mem_add_btn", help="Convidar membro"):
                st.session_state.ml_membros_show_invite = True
                st.rerun()


def _render_hero(total: int) -> None:
    st.markdown(
        f"""
        <div class="ml-mem-hero">
          <div class="ml-mem-hero-ico">👥</div>
          <div class="ml-mem-hero-text">
            <h2>Nosso time faz a diferença</h2>
            <p>Cada ministério, um propósito.<br>Cada membro, um chamado.</p>
          </div>
          <div class="ml-mem-hero-total">
            <b>{total}</b>
            <span>Total</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_stat_grid(counts: dict[str, int]) -> None:
    items = [
        (counts["total"], "Membros"),
        (counts["lideres"], "Líderes"),
        (counts["coord"], "Coord."),
        (counts["musicos"], "Músicos"),
    ]
    parts = ['<div class="ml-mem-stat-grid">']
    for val, lbl in items:
        parts.append(
            f'<div class="ml-mem-stat"><h2>{val}</h2><span>{_esc(lbl)}</span></div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def _render_filters() -> None:
    active = _filter_key()
    with st.container(key="ml_mem_filters"):
        cols = st.columns(len(FILTERS))
        for col, (key, label) in zip(cols, FILTERS):
            with col:
                if st.button(
                    label,
                    key=f"ml_mem_filter_{key}",
                    use_container_width=True,
                    type="primary" if active == key else "secondary",
                ):
                    st.session_state.ml_membros_filter = key
                    st.rerun()


def _render_invite_block() -> None:
    from app import get_registration_url

    link = get_registration_url()
    st.markdown(
        """
        <div class="ml-mem-invite">
          <div style="font-size:1.5rem;">➕</div>
          <div class="ml-mem-invite-text">
            <h3>Convidar novo membro</h3>
            <p>Compartilhe o link de cadastro para alguém entrar no ministério.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="ml_mem_invite_btn"):
        st.link_button("Convidar", link, use_container_width=True, key="ml_mem_invite_link")
    st.caption(f"Link: {link}")


def render_mobile_membros_page(
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
) -> None:
    from app import (
        can_reset_member_passwords,
        members_visible_to_group,
        render_admin_password_reset,
    )

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_membros_css()}</style>", unsafe_allow_html=True)
    st.markdown('<div id="ml-membros-page" class="ml-page">', unsafe_allow_html=True)

    if members_df.empty:
        st.markdown(
            '<div class="ml-mem-empty">Nenhum membro cadastrado ainda.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    leader_view = can_reset_member_passwords() and escalas_df is not None and equipe_df is not None
    visible = members_visible_to_group(members_df)
    counts = _compute_stats(visible)

    _render_header(total=counts["total"], leader_view=leader_view)
    _render_hero(counts["total"])
    _render_stat_grid(counts)

    if leader_view:
        with st.expander("🔑 Redefinir senha de integrante", expanded=False):
            render_admin_password_reset(members_df)

    with st.container(key="ml_mem_search"):
        st.text_input(
            "Buscar",
            key="ml_membros_search",
            placeholder="🔎 Buscar membro...",
            label_visibility="collapsed",
        )

    _render_filters()

    sort = _sort_key()
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button(
            "↕ Escalas" if sort == "nome" else "↕ Nome",
            key="ml_mem_sort_toggle",
            use_container_width=True,
        ):
            st.session_state.ml_membros_sort = "escalas" if sort == "nome" else "nome"
            st.rerun()

    rows = _prepare_rows(
        visible,
        members_df=members_df,
        escalas_df=escalas_df if escalas_df is not None else pd.DataFrame(),
        equipe_df=equipe_df if equipe_df is not None else pd.DataFrame(),
        leader_view=leader_view,
    )
    rows = _filter_rows(rows, _filter_key())
    rows = _search_rows(rows, _search_query())
    rows = _sort_rows(rows, sort)

    st.markdown(
        f'<div class="ml-mem-section"><span>Membros ({len(rows)})</span>'
        f'<span style="font-size:0.72rem;color:#94a3b8;font-weight:600;">'
        f'Ordenar: {"Nome" if sort == "nome" else "Escalas"}</span></div>',
        unsafe_allow_html=True,
    )

    if not rows:
        st.markdown(
            '<div class="ml-mem-empty">Nenhum integrante neste filtro.</div>',
            unsafe_allow_html=True,
        )
    else:
        for row in rows[:40]:
            st.markdown(
                _member_card_html(row, leader_view=leader_view),
                unsafe_allow_html=True,
            )
        if len(rows) > 40:
            st.caption(f"Mostrando 40 de {len(rows)} integrantes. Refine a busca.")

    if leader_view or bool(st.session_state.get("ml_membros_show_invite")):
        _render_invite_block()

    st.caption(
        f"🎶 {len(louvores_df)} louvores no repertório · "
        "Status baseado em escalas recentes."
    )
    st.markdown("</div>", unsafe_allow_html=True)
