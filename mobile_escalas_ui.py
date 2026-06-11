"""Mobile Lab — página Escalas premium (layout personalizado)."""

from __future__ import annotations

import html
from datetime import date, datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


ESCALAS_TABS: tuple[tuple[str, str, str], ...] = (
    ("visao", "🏠", "Visão Geral"),
    ("escalas", "📅", "Escalas"),
    ("sequencia", "🎵", "Sequência"),
    ("disponibilidade", "👤", "Disponibilidade"),
)

_SECTOR_FILTERS = ("Todos", "Vocal", "Instrumental", "Técnico", "Produção", "Apoio")


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _active_tab() -> str:
    t = str(st.session_state.get("ml_escalas_tab", "visao")).strip()
    legacy = {
        "solicitacoes": "disponibilidade",
        "trocas": "disponibilidade",
        "equipe": "visao",
        "todas": "escalas",
    }
    if t in legacy:
        t = legacy[t]
        st.session_state.ml_escalas_tab = t
    keys = {k for k, _, _ in ESCALAS_TABS}
    return t if t in keys else "visao"


def _set_tab(tab: str) -> None:
    st.session_state.ml_escalas_tab = tab


def _classify_sector(funcao: str) -> str:
    f = str(funcao or "").lower()
    if "técnico" in f or "tecnico" in f or "som" in f:
        return "Técnico"
    if any(
        x in f
        for x in (
            "vocal",
            "ministrador",
            "contralto",
            "soprano",
            "tenor",
            "barit",
            "mezzo",
        )
    ):
        return "Vocal"
    if any(
        x in f
        for x in ("baix", "guitar", "bater", "teclad", "violon", "banda", "instrument")
    ):
        return "Instrumental"
    if "produ" in f or "mídia" in f or "midia" in f:
        return "Produção"
    return "Apoio"


def _group_team_sectors(team: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {s: [] for s in _SECTOR_FILTERS if s != "Todos"}
    for person in team:
        sector = _classify_sector(str(person.get("funcao", "")))
        grouped.setdefault(sector, []).append(person)
    return grouped


def _resolve_escala_row(
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    prefer_id: str | None = None,
) -> pd.Series | None:
    if prefer_id:
        match = escalas_df[escalas_df["id"].astype(str) == str(prefer_id)]
        if not match.empty:
            return match.iloc[0]

    from escala_member_stats import member_escala_occurrences

    today = date.today()
    for culto_d, eid, _ev in member_escala_occurrences(my_email, escalas_df, equipe_df):
        try:
            d = pd.Timestamp(culto_d).date()
        except (ValueError, TypeError):
            continue
        if d >= today:
            match = escalas_df[escalas_df["id"].astype(str) == str(eid)]
            if not match.empty:
                return match.iloc[0]

    from dashboard_ui import next_upcoming_escala

    nxt = next_upcoming_escala(escalas_df)
    if nxt:
        match = escalas_df[escalas_df["id"].astype(str) == str(nxt.get("id", ""))]
        if not match.empty:
            return match.iloc[0]
    if not escalas_df.empty:
        df = escalas_df.copy()
        df["_sort"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("_sort")
        if not df.empty:
            return df.iloc[0]
    return None


def _escala_metrics(
    escala_row: pd.Series,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> dict[str, object]:
    from app import (
        enrich_programa_from_catalog,
        integrantes_escalados,
        programa_por_escala,
    )
    from app_features import lookup_louvor_meta
    from louvor_meta import format_duracao_total, parse_duracao_min

    team = integrantes_escalados(escala_row, equipe_df, members_df)
    escala_id = str(escala_row.get("id", ""))
    prog = programa_por_escala(programa_df, escala_id)
    if not louvores_df.empty:
        prog = enrich_programa_from_catalog(prog, louvores_df)

    total_min = 0.0
    if not prog.empty:
        for _, item in prog.iterrows():
            meta = lookup_louvor_meta(
                louvores_df,
                str(item.get("louvor_title", "")),
                str(item.get("artist", "")),
            )
            total_min += parse_duracao_min(meta.get("duracao_min", ""))

    filled = min(100, int(len(team) * 100 / 12)) if team else 0

    return {
        "integrantes": len(team),
        "musicas": len(prog),
        "duracao": format_duracao_total(total_min) if total_min else "—",
        "preenchida": f"{filled}%",
        "prog": prog,
        "team": team,
    }


def _format_escala_datetime(escala_row: pd.Series) -> tuple[str, str, str]:
    from app import _DIAS_SEMANA_PT

    event = str(escala_row.get("event", "Culto"))
    location = (
        str(escala_row.get("location", escala_row.get("local", "Templo IBBJ"))).strip()
        or "Templo IBBJ"
    )
    try:
        dt = pd.to_datetime(escala_row.get("date"))
        date_txt = f"{_DIAS_SEMANA_PT[dt.weekday()]}, {dt.strftime('%d/%m/%Y')}"
    except (ValueError, TypeError):
        date_txt = str(escala_row.get("date", ""))
    time_txt = str(escala_row.get("time", escala_row.get("hora", "19:00"))).strip() or "19:00"
    return event, f"{date_txt} • {time_txt}", location


def _sector_avatar_html(members: list[dict], members_df: pd.DataFrame, limit: int = 4) -> str:
    from app import member_photo_html

    parts: list[str] = []
    extra = max(0, len(members) - limit)
    for person in members[:limit]:
        email = str(person.get("email", "")).strip()
        nome = str(person.get("nome", ""))
        if email:
            parts.append(member_photo_html(email, members_df, 28, name=nome))
        else:
            initial = (nome.strip()[:1] or "?").upper()
            parts.append(f'<span class="ml-esc-mini-ph">{_esc(initial)}</span>')
    html_av = "".join(parts)
    if extra:
        html_av += f'<span class="ml-esc-sector-more">+{extra}</span>'
    return html_av


def _render_proximo_culto_card(escala_row: pd.Series) -> None:
    event, when, location = _format_escala_datetime(escala_row)
    st.markdown(
        f"""
        <div class="ml-esc-card">
          <div class="ml-esc-card-top">
            <h3>Próximo culto</h3>
          </div>
          <p>📅 {_esc(when)}</p>
          <h2>🎵 {_esc(event)}</h2>
          <p>📍 {_esc(location)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metrics_grid(metrics: dict[str, object]) -> None:
    items = (
        ("👥", metrics["integrantes"], "Integrantes"),
        ("🎵", metrics["musicas"], "Músicas"),
        ("⏰", metrics["duracao"], "Duração"),
        ("✅", metrics["preenchida"], "Escala"),
    )
    parts = ['<div class="ml-esc-metric-grid">']
    for _ico, val, lbl in items:
        parts.append(
            f'<div class="ml-esc-metric"><b>{_esc(val)}</b><span>{_esc(lbl)}</span></div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def _render_equipes_escaladas(
    team: list[dict],
    members_df: pd.DataFrame,
    *,
    key_prefix: str,
) -> None:
    grouped = _group_team_sectors(team)
    st.markdown(
        '<div class="ml-esc-section-title">👥 Equipes escaladas</div>',
        unsafe_allow_html=True,
    )
    sector_filter = st.selectbox(
        "Setor",
        list(_SECTOR_FILTERS),
        key=f"{key_prefix}_sector_filter",
        label_visibility="collapsed",
    )

    sector_icons = {
        "Vocal": "🎤",
        "Instrumental": "🎸",
        "Técnico": "🎚️",
        "Produção": "📷",
        "Apoio": "🤝",
    }
    cards: list[tuple[str, list[dict]]] = []
    for sector, members in grouped.items():
        if not members:
            continue
        if sector_filter != "Todos" and sector != sector_filter:
            continue
        cards.append((sector, members))

    if not cards:
        st.info("Nenhuma equipe neste setor.")
        return

    for i in range(0, len(cards), 2):
        cols = st.columns(2, gap="small")
        for col, (sector, members) in zip(cols, cards[i : i + 2]):
            ico = sector_icons.get(sector, "👥")
            avatars = _sector_avatar_html(members, members_df)
            with col:
                st.markdown(
                    f"""
                    <div class="ml-esc-sector-card">
                      <h4>{ico} {_esc(sector)}</h4>
                      <p>{len(members)} integrante(s)</p>
                      <div class="ml-esc-sector-av">{avatars}</div>
                      <div class="ml-esc-sector-link">Ver detalhes →</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _render_cronograma(prog: pd.DataFrame, escala_row: pd.Series) -> None:
    from app import _normalize_parte
    from catalog_sanitize import format_louvor_display, sanitize_catalog_text

    st.markdown(
        '<div class="ml-esc-section-title">⏰ Cronograma do culto</div>',
        unsafe_allow_html=True,
    )
    if prog.empty:
        st.info("Programação ainda não montada.")
        return

    base_time = str(escala_row.get("time", escala_row.get("hora", "18:00"))).strip() or "18:00"
    try:
        cursor = pd.to_datetime(base_time, format="%H:%M", errors="coerce")
        if pd.isna(cursor):
            cursor = pd.to_datetime(base_time.replace("h", ":"), errors="coerce")
    except (ValueError, TypeError):
        cursor = None

    for _, item in prog.iterrows():
        if cursor is not None and not pd.isna(cursor):
            hora = cursor.strftime("%H:%M")
            cursor += pd.Timedelta(minutes=5)
        else:
            hora = str(item.get("ordem", "—"))
        parte = _normalize_parte(str(item.get("parte", "")))
        louvor = format_louvor_display(
            sanitize_catalog_text(item.get("louvor_title", "")),
            sanitize_catalog_text(item.get("artist", "")),
        )
        leader = sanitize_catalog_text(item.get("leader_name", ""))
        sub = f"{parte}" + (f" • {leader}" if leader else "")
        st.markdown(
            f"""
            <div class="ml-esc-crono-item">
              <div class="ml-esc-crono-time">{_esc(hora)}</div>
              <div class="ml-esc-crono-body">
                <b>{_esc(louvor)}</b>
                <small>{_esc(sub)}</small>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_sequencia_louvores(
    prog: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    escala_id: str,
    members_df: pd.DataFrame,
) -> None:
    from app import instrument_kits_from_roles, get_current_member_row, cifra_search_url
    from app_features import lookup_louvor_meta
    from catalog_sanitize import format_louvor_display, sanitize_catalog_text
    from cifra_fetch import resolve_letra_url
    from louvor_meta import format_duracao_total, parse_duracao_min

    st.markdown(
        '<div class="ml-esc-section-title">🎵 Sequência do culto</div>',
        unsafe_allow_html=True,
    )
    if prog.empty:
        return

    _idx, row_me = get_current_member_row(members_df)
    roles_me = str(row_me.get("roles", "")) if row_me is not None else str(
        st.session_state.get("user_roles", "")
    )
    bio_me = str(row_me.get("bio", "")) if row_me is not None else ""
    kits_me = instrument_kits_from_roles(roles_me, bio=bio_me)

    for i, (_, item) in enumerate(prog.iterrows(), start=1):
        louvor = sanitize_catalog_text(item.get("louvor_title", ""))
        artist = sanitize_catalog_text(item.get("artist", ""))
        titulo = format_louvor_display(louvor, artist)
        meta = lookup_louvor_meta(louvores_df, louvor, artist)
        dur = format_duracao_total(parse_duracao_min(meta.get("duracao_min", "")))
        yt = sanitize_catalog_text(item.get("youtube_url", ""))
        cifra_stored = sanitize_catalog_text(item.get("cifra_url", ""))
        cifra = cifra_stored if cifra_stored.startswith("http") else cifra_search_url(louvor, artist)
        letra = resolve_letra_url(louvor, artist, cifra_club_url=cifra_stored)
        ordem = str(item.get("ordem", i))
        slug = f"{escala_id}_{ordem}"

        st.markdown(
            f"""
            <div class="ml-esc-song-card">
              <h4>{i}. {_esc(titulo)}</h4>
              <p>⏱️ {_esc(dur)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2, gap="small")
        with c1:
            with st.container(key=f"ml_esc_song_yt_{slug}"):
                if yt:
                    st.link_button("🎥 YouTube", yt, use_container_width=True)
                else:
                    st.button("🎥 YouTube", key=f"ml_esc_yt_off_{slug}", disabled=True, use_container_width=True)
        with c2:
            kit_url = ""
            if kits_me:
                from app import kit_youtube_url

                kit_url = kit_youtube_url(kits_me[0][2], louvor)
            with st.container(key=f"ml_esc_song_kit_{slug}"):
                if kit_url:
                    st.link_button("🎤 Kit Voz", kit_url, use_container_width=True)
                else:
                    st.button("🎤 Kit Voz", key=f"ml_esc_kit_off_{slug}", disabled=True, use_container_width=True)
        c3, c4 = st.columns(2, gap="small")
        with c3:
            with st.container(key=f"ml_esc_song_cifra_{slug}"):
                st.link_button("🎼 Cifra", cifra, use_container_width=True)
        with c4:
            with st.container(key=f"ml_esc_song_letra_{slug}"):
                if letra:
                    st.link_button("📄 Letra", letra, use_container_width=True)
                else:
                    st.button("📄 Letra", key=f"ml_esc_letra_off_{slug}", disabled=True, use_container_width=True)


def _render_resumo_card(metrics: dict[str, object]) -> None:
    st.markdown(
        f"""
        <div class="ml-esc-card">
          <h3>Resumo</h3>
          <p>⏱️ {_esc(metrics["duracao"])}</p>
          <p>🎵 {_esc(metrics["musicas"])} música(s)</p>
          <p>👥 {_esc(metrics["integrantes"])} integrante(s)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_acoes_escala(
    escala_row: pd.Series,
    *,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    from app import collect_escala_whatsapp_message
    from whatsapp_share import whatsapp_share_url

    escala_id = str(escala_row.get("id", ""))
    st.markdown('<div class="ml-esc-section-title">🚀 Ações</div>', unsafe_allow_html=True)

    if st.button("📄 Abrir Sequência", key=f"ml_esc_act_seq_{escala_id}", use_container_width=True):
        st.session_state["focus_sequencia_escala_id"] = escala_id
        _set_tab("sequencia")
        st.rerun()

    from mobile_lab_nav import user_can_gerenciar_escalas

    if user_can_gerenciar_escalas() or bool(st.session_state.get("ml_can_gerenciar")):
        if st.button(
            "🎯 Gerenciar Escalas",
            key=f"ml_esc_act_ger_{escala_id}",
            use_container_width=True,
        ):
            from mobile_lab_nav import navigate_ml_page

            navigate_ml_page("Gerenciar Escalas", pin=True)
            st.rerun()

    msg = collect_escala_whatsapp_message(
        escala_row, programa_df, equipe_df, members_df, louvores_df
    )
    if msg:
        wa_url = whatsapp_share_url("Escala IBBJ", msg)
        with st.container(key=f"ml_esc_act_wa_{escala_id}"):
            st.link_button("📱 Enviar WhatsApp", wa_url, use_container_width=True)


def _render_culto_layout(
    escala_row: pd.Series,
    *,
    my_email: str,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    key_prefix: str,
    full: bool = True,
) -> None:
    metrics = _escala_metrics(
        escala_row, equipe_df, members_df, programa_df, louvores_df
    )
    escala_id = str(escala_row.get("id", ""))

    _render_proximo_culto_card(escala_row)
    _render_metrics_grid(metrics)
    _render_equipes_escaladas(metrics["team"], members_df, key_prefix=key_prefix)
    _render_cronograma(metrics["prog"], escala_row)

    if full:
        _render_sequencia_louvores(
            metrics["prog"],
            louvores_df,
            escala_id=escala_id,
            members_df=members_df,
        )
        _render_resumo_card(metrics)
        _render_acoes_escala(
            escala_row,
            programa_df=programa_df,
            equipe_df=equipe_df,
            members_df=members_df,
            louvores_df=louvores_df,
        )


def _user_escala_options(
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
) -> list[tuple[str, pd.Series]]:
    from app import escala_label_for_user, member_escala_occurrences

    rows: list[tuple[str, pd.Series]] = []
    seen: set[str] = set()
    for _d, eid, _ev in member_escala_occurrences(my_email, escalas_df, equipe_df):
        match = escalas_df[escalas_df["id"].astype(str) == str(eid)]
        if match.empty or str(eid) in seen:
            continue
        seen.add(str(eid))
        row = match.iloc[0]
        rows.append((escala_label_for_user(row, my_email, equipe_df), row))
    return rows


def _member_photo_uri(email: str, members_df: pd.DataFrame) -> str | None:
    from app import profile_photo_to_data_uri

    email_l = str(email or "").strip().lower()
    stored = ""
    if not members_df.empty and "email" in members_df.columns:
        match = members_df[members_df["email"].astype(str).str.lower() == email_l]
        if not match.empty:
            stored = str(match.iloc[0].get("profile_photo", "")).strip()
    return profile_photo_to_data_uri(email_l, stored)


def _render_week_nav() -> None:
    from app import week_bounds

    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0
    offset = int(st.session_state.get("week_offset", 0))
    start, end = week_bounds(offset)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("◀", key="ml_esc_week_prev", use_container_width=True):
            st.session_state.week_offset = offset - 1
            st.rerun()
    with c2:
        st.markdown(
            f'<div style="text-align:center;font-weight:800;font-size:0.88rem;padding:0.35rem 0;">'
            f"{start.strftime('%d/%m')} – {end.strftime('%d/%m/%Y')}</div>",
            unsafe_allow_html=True,
        )
    with c3:
        if st.button("▶", key="ml_esc_week_next", use_container_width=True):
            st.session_state.week_offset = offset + 1
            st.rerun()


def mobile_escalas_css() -> str:
    from culto_programa_css import culto_programa_css

    return culto_programa_css() + r"""
    body:has(#ml-escalas-page) .ml-esc-header h1{
      font-size: 2rem !important;
      font-weight: 800 !important;
      margin: 0 !important;
      letter-spacing: -0.02em;
    }
    body:has(#ml-escalas-page) .ml-esc-header p{
      color: rgba(148,163,184,.95) !important;
      margin: 0.35rem 0 0 0 !important;
      font-size: 1rem !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 6px !important;
      width: 100% !important;
      margin: 0 !important;
      padding: 0 0 4px !important;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar{
      display: none;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stColumn"],
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="column"]{
      flex: 0 0 auto !important;
      width: auto !important;
      min-width: 0 !important;
      max-width: none !important;
      padding: 0 !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stVerticalBlock"]{
      gap: 0 !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="element-container"],
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stButton"]{
      margin: 0 !important;
      padding: 0 !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tab_"] .stButton > button{
      border-radius: 14px !important;
      padding: 0.38rem 0.72rem !important;
      min-height: 2.15rem !important;
      height: auto !important;
      font-weight: 700 !important;
      font-size: 0.78rem !important;
      white-space: nowrap !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(148,163,184,.95) !important;
      box-shadow: none !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tab_"] .stButton > button[kind="primary"]{
      background: rgba(124,58,237,1) !important;
      border-color: rgba(139,92,246,.45) !important;
      color: #fff !important;
      box-shadow: 0 0 22px rgba(139,92,246,.22) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_quick_"] .stButton > button{
      min-height: 2.85rem !important;
      padding: 0.35rem 0.45rem 0.4rem !important;
      border-radius: 18px !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(226,232,240,.96) !important;
      font-size: 1.15rem !important;
      line-height: 1.1 !important;
      white-space: pre-line !important;
      box-shadow: 0 0 16px rgba(139,92,246,.06) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_quick_"] .stButton > button p{
      font-size: 0.78rem !important;
      font-weight: 800 !important;
      margin-top: 0.2rem !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_quick_"]{
      margin-bottom: 0.2rem !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_quick_"] [data-testid="element-container"]{
      margin: 0 0 0.25rem !important;
      padding: 0 !important;
    }
    body:has(#ml-esc-quick-start) [data-testid="stHorizontalBlock"]:has([class*="st-key-ml_esc_quick_seq_btn"]),
    body:has(#ml-esc-quick-start) [data-testid="stHorizontalBlock"]:has([class*="st-key-ml_esc_quick_sol_btn"]){
      flex-wrap: nowrap !important;
      gap: 8px !important;
      margin: 0 0 0.25rem !important;
    }
    body:has(#ml-esc-quick-start) [data-testid="stHorizontalBlock"]:has([class*="st-key-ml_esc_quick_seq_btn"]) > [data-testid="stColumn"],
    body:has(#ml-esc-quick-start) [data-testid="stHorizontalBlock"]:has([class*="st-key-ml_esc_quick_seq_btn"]) > [data-testid="column"],
    body:has(#ml-esc-quick-start) [data-testid="stHorizontalBlock"]:has([class*="st-key-ml_esc_quick_sol_btn"]) > [data-testid="stColumn"],
    body:has(#ml-esc-quick-start) [data-testid="stHorizontalBlock"]:has([class*="st-key-ml_esc_quick_sol_btn"]) > [data-testid="column"]{
      flex: 1 1 0 !important;
      width: 50% !important;
      max-width: 50% !important;
      min-width: 0 !important;
      padding: 0 !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_quick_gerenciar_btn"] .stButton > button{
      min-height: 3rem !important;
      background: linear-gradient(135deg, rgba(250,204,21,.22), rgba(124,58,237,.15)) !important;
      border: 1px solid rgba(250,204,21,.35) !important;
      color: #fde68a !important;
      font-weight: 900 !important;
      box-shadow: 0 0 18px rgba(250,204,21,.12) !important;
      margin-bottom: 0.35rem !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_action_"] .stButton > button[kind="primary"]{
      width: 100% !important;
      min-height: 3rem !important;
      border-radius: 20px !important;
      font-weight: 800 !important;
      font-size: 1rem !important;
      background: linear-gradient(90deg, rgba(124,58,237,1), rgba(139,92,246,1)) !important;
      border: none !important;
      box-shadow: 0 0 28px rgba(139,92,246,.25) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_member_"] .stButton > button{
      width: 100% !important;
      text-align: left !important;
      justify-content: flex-start !important;
      min-height: 4.5rem !important;
      padding: 0.65rem 0.75rem !important;
      border-radius: 20px !important;
      background: rgba(15,23,42,.55) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(226,232,240,.95) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_member_"] .stButton > button p{
      margin: 0 !important;
      white-space: normal !important;
      text-align: left !important;
      font-size: 0.78rem !important;
      line-height: 1.25 !important;
    }
    .ml-esc-hero{
      border-radius: 22px;
      padding: 0.65rem;
      margin-bottom: 0.35rem;
      position: relative;
      overflow: hidden;
    }
    .ml-esc-hero-bg{
      position: absolute;
      inset: 0;
      opacity: 0.12;
      object-fit: cover;
      width: 100%;
      height: 100%;
    }
    .ml-esc-hero-inner{ position: relative; z-index: 1; }
    .ml-esc-team-row{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 10px;
      border-radius: 16px;
      background: rgba(15,23,42,.55);
      border: 1px solid rgba(255,255,255,.08);
      margin-bottom: 6px;
    }
    .ml-esc-team-row img, .ml-esc-team-av{
      width: 52px;
      height: 52px;
      border-radius: 18px;
      object-fit: cover;
      flex-shrink: 0;
      border: 2px solid rgba(139,92,246,.35);
    }
    .ml-esc-team-av{
      display:flex;
      align-items:center;
      justify-content:center;
      font-weight: 900;
      background: rgba(59,130,246,.15);
      color: rgba(226,232,240,.95);
    }
    .ml-esc-song{
      border-radius: 18px;
      padding: 10px 12px;
      background: rgba(15,23,42,.72);
      border: 1px solid rgba(255,255,255,.08);
      margin-bottom: 6px;
    }
    .ml-esc-song h4{ margin: 0; font-size: 1rem; font-weight: 800; }
    .ml-esc-song p{ margin: 4px 0 0; color: rgba(148,163,184,.92); font-size: 0.82rem; }
    .ml-esc-pill{
      display:inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      background: rgba(139,92,246,.14);
      border: 1px solid rgba(139,92,246,.25);
      font-size: 0.72rem;
      font-weight: 800;
      color: rgba(196,181,253,.98);
      margin-right: 6px;
    }
    .ml-esc-card{
      background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 20px;
      padding: 18px 20px;
      margin-bottom: 14px;
    }
    .ml-esc-card h3{
      margin: 0 0 0.35rem;
      font-size: 0.92rem;
      font-weight: 800;
      color: #c4b5fd;
    }
    .ml-esc-card h2{
      margin: 0.15rem 0;
      font-size: 1.35rem;
      font-weight: 800;
      color: #fff;
      line-height: 1.15;
    }
    .ml-esc-card p{
      margin: 0.2rem 0 0;
      color: rgba(148,163,184,.95);
      font-size: 0.88rem;
      line-height: 1.4;
    }
    .ml-esc-card-top{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.65rem;
    }
    .ml-esc-card-link{
      color: #a78bfa;
      font-size: 0.78rem;
      font-weight: 700;
      white-space: nowrap;
    }
    .ml-esc-metric-grid{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin: 0.65rem 0 0.15rem;
    }
    .ml-esc-metric{
      background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 18px;
      padding: 14px 10px;
      text-align: center;
    }
    .ml-esc-metric b{
      display: block;
      font-size: 1.15rem;
      font-weight: 800;
      color: #fff;
      line-height: 1.1;
    }
    .ml-esc-metric span{
      display: block;
      margin-top: 0.25rem;
      font-size: 0.68rem;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .ml-esc-section-title{
      font-size: 1rem;
      font-weight: 800;
      margin: 1rem 0 0.55rem;
      color: #f8fafc;
    }
    .ml-esc-sector-grid{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 0.35rem;
    }
    .ml-esc-sector-card{
      background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 18px;
      padding: 14px;
      min-height: 118px;
    }
    .ml-esc-sector-card h4{
      margin: 0 0 0.35rem;
      font-size: 0.88rem;
      font-weight: 800;
      color: #fff;
    }
    .ml-esc-sector-card p{
      margin: 0;
      font-size: 0.75rem;
      color: #94a3b8;
    }
    .ml-esc-sector-av{
      display: flex;
      align-items: center;
      gap: 0;
      margin: 0.55rem 0 0.45rem;
      min-height: 28px;
    }
    .ml-esc-sector-av img, .ml-esc-sector-av .ml-esc-mini-ph{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid rgba(111,76,255,.45);
      margin-left: -6px;
      background: rgba(59,130,246,.2);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.62rem;
      font-weight: 800;
      color: #e9d5ff;
    }
    .ml-esc-sector-av img:first-child, .ml-esc-sector-av .ml-esc-mini-ph:first-child{
      margin-left: 0;
    }
    .ml-esc-sector-more{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      margin-left: -6px;
      background: rgba(124,58,237,.35);
      border: 2px solid rgba(111,76,255,.45);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.62rem;
      font-weight: 800;
      color: #fff;
    }
    .ml-esc-sector-link{
      font-size: 0.72rem;
      font-weight: 700;
      color: #a78bfa;
    }
    .ml-esc-crono-item{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 18px;
      padding: 14px 16px;
      margin-bottom: 10px;
    }
    .ml-esc-crono-time{
      flex-shrink: 0;
      min-width: 52px;
      padding: 8px 10px;
      border-radius: 14px;
      background: linear-gradient(135deg, rgba(124,58,237,.55), rgba(91,33,182,.35));
      border: 1px solid rgba(139,92,246,.35);
      text-align: center;
      font-size: 0.82rem;
      font-weight: 800;
      color: #fff;
    }
    .ml-esc-crono-body{
      flex: 1;
      min-width: 0;
    }
    .ml-esc-crono-body b{
      display: block;
      font-size: 0.9rem;
      color: #fff;
      margin-bottom: 0.2rem;
    }
    .ml-esc-crono-body small{
      color: #94a3b8;
      font-size: 0.76rem;
      line-height: 1.35;
    }
    .ml-esc-song-card{
      background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 18px;
      padding: 15px 16px;
      margin-bottom: 12px;
    }
    .ml-esc-song-card h4{
      margin: 0;
      font-size: 1rem;
      font-weight: 800;
      color: #fff;
    }
    .ml-esc-song-card p{
      margin: 0.35rem 0 0;
      color: #94a3b8;
      font-size: 0.82rem;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_song_"] .stButton > button{
      min-height: 2.35rem !important;
      border-radius: 14px !important;
      font-size: 0.76rem !important;
      font-weight: 700 !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #e2e8f0 !important;
      padding: 0.35rem 0.25rem !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_act_"] .stButton > button,
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_act_"] .stLinkButton > a{
      width: 100% !important;
      min-height: 2.85rem !important;
      border-radius: 16px !important;
      font-weight: 800 !important;
      margin-bottom: 0.35rem !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #e2e8f0 !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_visao_full"] .stButton > button{
      background: transparent !important;
      border: none !important;
      color: #a78bfa !important;
      font-weight: 700 !important;
      justify-content: flex-end !important;
      min-height: 2rem !important;
      padding: 0 !important;
      margin: -0.5rem 0 0.25rem !important;
      box-shadow: none !important;
    }
    """


def _render_header() -> None:
    st.markdown(
        """
        <div id="ml-escalas-page" class="ml-page">
          <div class="ml-esc-header" style="margin-bottom:0.35rem;">
            <h1>Escalas</h1>
            <p>Gerencie as escalas da sua equipe</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_tabs(active: str) -> None:
    with st.container(key="ml_esc_tabs"):
        cols = st.columns(len(ESCALAS_TABS), gap="small")
        for col, (key, icon, label) in zip(cols, ESCALAS_TABS):
            with col:
                txt = f"{icon} {label}"
                if st.button(
                    txt,
                    key=f"ml_esc_tab_{key}",
                    type="primary" if active == key else "secondary",
                ):
                    _set_tab(key)
                    st.rerun()


def _render_hero_hub() -> None:
    st.markdown(
        """
        <div class="ml-glass ml-glow-purple ml-esc-hero">
          <img class="ml-esc-hero-bg" src="https://images.unsplash.com/photo-1504052434569-70ad5836ab65?q=80&w=1200&auto=format&fit=crop" alt="" />
          <div class="ml-esc-hero-inner">
            <div style="display:flex;gap:14px;align-items:center;margin-bottom:10px;">
              <div style="width:56px;height:56px;border-radius:20px;background:rgba(59,130,246,.18);border:1px solid rgba(59,130,246,.25);display:flex;align-items:center;justify-content:center;font-size:1.6rem;">🎤</div>
              <div>
                <div style="font-size:1.35rem;font-weight:900;letter-spacing:-0.02em;">Escalas, ensaios e trocas</div>
                <div style="color:rgba(148,163,184,.92);font-size:0.9rem;margin-top:4px;">Consulte sua equipe, cultos e solicitações</div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_quick_access() -> None:
    from mobile_lab_nav import user_can_gerenciar_escalas

    st.markdown(
        '<span id="ml-esc-quick-start" aria-hidden="true"></span>'
        '<div style="font-size:1.05rem;font-weight:900;margin:0.2rem 0 0.35rem;">Acesso rápido</div>',
        unsafe_allow_html=True,
    )
    if user_can_gerenciar_escalas() or bool(st.session_state.get("ml_can_gerenciar")):
        if st.button(
            "🎯  Gerenciar Escalas\nMenu principal · montar cultos",
            key="ml_esc_quick_gerenciar_btn",
            use_container_width=True,
            type="primary",
        ):
            from mobile_lab_nav import navigate_ml_page

            navigate_ml_page("Gerenciar Escalas", pin=True)
            st.rerun()
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("🎵\nSequência", key="ml_esc_quick_seq_btn", use_container_width=True):
            _set_tab("sequencia")
            st.rerun()
    with c2:
        if st.button("🔄\nDisponibilidade", key="ml_esc_quick_trocas_btn", use_container_width=True):
            _set_tab("disponibilidade")
            st.rerun()


def _render_not_scheduled_warning() -> None:
    st.markdown(
        """
        <div class="ml-glass ml-glow-gold" style="border-radius:24px;padding:16px;border:1px solid rgba(250,204,21,.2);margin:0.75rem 0;">
          <div style="display:flex;gap:14px;align-items:flex-start;">
            <div style="font-size:2rem;line-height:1;">⚠️</div>
            <div>
              <div style="font-size:1.1rem;font-weight:900;margin-bottom:4px;">Você não está escalado</div>
              <div style="color:rgba(148,163,184,.92);font-size:0.9rem;line-height:1.35;">
                Ou a escala ainda não foi publicada para sua equipe.
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _team_member_card_html(
    nome: str,
    funcao: str,
    photo_uri: str | None,
) -> str:
    initial = (nome.strip()[:1] or "?").upper()
    if photo_uri:
        av = f'<img class="ml-esc-team-av" src="{_esc(photo_uri)}" alt="" />'
    else:
        av = f'<div class="ml-esc-team-av">{_esc(initial)}</div>'
    return f"""
    <div class="ml-esc-team-row">
      {av}
      <div style="flex:1;min-width:0;">
        <div style="font-weight:900;font-size:0.95rem;">{_esc(nome)}</div>
        <div style="margin-top:6px;"><span class="ml-esc-pill">{_esc(funcao.upper())}</span></div>
      </div>
      <div style="color:rgba(148,163,184,.8);font-size:1.1rem;">›</div>
    </div>
    """


def _render_tab_equipe(
    *,
    minhas: list[dict],
    members_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    from app import render_culto_programa

    _render_hero_hub()
    _render_quick_access()
    _render_week_nav()
    if not minhas:
        _render_not_scheduled_warning()
        return

    focus_id = str(st.session_state.get("ml_escalas_focus_id", "")).strip()
    if focus_id:
        row_f = None
        for item in minhas:
            if str(item["escala"].get("id", "")) == focus_id:
                row_f = item["escala"]
                break
        if row_f is not None:
            st.success("Programação do culto selecionado:")
            render_culto_programa(
                row_f,
                programa_df,
                equipe_df,
                members_df,
                louvores_df,
                ensaio_notice=True,
                widget_key_prefix=f"ml_eq_focus_{focus_id}",
            )
            st.markdown("---")

    for item in minhas:
        escala = item["escala"]
        if focus_id and str(escala.get("id", "")) == focus_id:
            continue
        eid = str(escala.get("id", ""))
        render_culto_programa(
            escala,
            programa_df,
            equipe_df,
            members_df,
            louvores_df,
            ensaio_notice=True,
            widget_key_prefix=f"ml_eq_{eid}",
        )


def _render_tab_visao(
    *,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    focus_id = str(st.session_state.get("ml_escalas_focus_id", "")).strip() or None
    row = _resolve_escala_row(
        my_email, escalas_df, equipe_df, prefer_id=focus_id
    )
    if row is None:
        st.info("Nenhuma escala disponível no momento.")
        return

    escala_id = str(row.get("id", ""))
    _render_proximo_culto_card(row)
    if st.button(
        "Ver escala completa →",
        key="ml_esc_visao_full",
        use_container_width=True,
    ):
        st.session_state["ml_esc_todas_escala_id"] = escala_id
        _set_tab("escalas")
        st.rerun()

    metrics = _escala_metrics(
        row, equipe_df, members_df, programa_df, louvores_df
    )
    _render_metrics_grid(metrics)
    _render_equipes_escaladas(
        metrics["team"], members_df, key_prefix="ml_visao"
    )
    _render_cronograma(metrics["prog"], row)


def _render_tab_escalas(
    *,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    from app import escala_label_for_user

    focus_id = str(st.session_state.get("ml_escalas_focus_id", "")).strip() or None
    pref = str(st.session_state.get("ml_esc_todas_escala_id", "")).strip() or focus_id

    options = _user_escala_options(my_email, escalas_df, equipe_df)
    if options:
        labels = [lbl for lbl, _ in options]
        default_idx = 0
        if pref:
            for i, (_, r) in enumerate(options):
                if str(r.get("id", "")) == pref:
                    default_idx = i
                    break
        escolha = st.selectbox(
            "Culto",
            labels,
            index=default_idx,
            key="ml_esc_escalas_sel",
        )
        row = next(r for lbl, r in options if lbl == escolha)
    else:
        row = _resolve_escala_row(
            my_email, escalas_df, equipe_df, prefer_id=pref
        )
        if row is None:
            st.info("Você ainda não aparece em nenhuma escala registrada.")
            return
        st.caption(escala_label_for_user(row, my_email, equipe_df))

    st.session_state["ml_esc_todas_escala_id"] = str(row.get("id", ""))
    _render_culto_layout(
        row,
        my_email=my_email,
        equipe_df=equipe_df,
        members_df=members_df,
        programa_df=programa_df,
        louvores_df=louvores_df,
        key_prefix="ml_esc",
        full=True,
    )


def _render_tab_sequencia(
    *,
    minhas: list[dict],
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> None:
    from mobile_sequencia_culto_ui import render_mobile_sequencia_tab

    if not minhas:
        _render_not_scheduled_warning()
        return

    render_mobile_sequencia_tab(
        minhas=minhas,
        programa_df=programa_df,
        louvores_df=louvores_df,
        escalas_df=escalas_df,
        equipe_df=equipe_df,
        members_df=members_df,
        all_escalas=False,
    )


def _render_tab_disponibilidade(
    *,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> None:
    from app import (
        TROCAS_FILE,
        escala_label_for_user,
        member_display_name,
        members_options_escala,
        new_id,
        save_data,
        user_escalas,
    )

    st.markdown(
        """
        <div class="ml-glass" style="border-radius:22px;padding:14px;margin-bottom:12px;">
          <div style="font-size:1.4rem;margin-bottom:6px;">🔄</div>
          <div style="font-weight:900;">Disponibilidade</div>
          <p style="color:rgba(148,163,184,.92);font-size:0.88rem;margin:8px 0 0;line-height:1.35;">
            Trocas, substituições e solicitações de disponibilidade.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_swap_tracking_section(
        my_email=my_email,
        escalas_df=escalas_df,
        equipe_df=equipe_df,
        trocas_df=trocas_df,
    )
    st.markdown(
        '<div style="font-size:0.95rem;font-weight:900;margin:0.85rem 0 0.45rem;">Nova solicitação</div>',
        unsafe_allow_html=True,
    )
    minhas = user_escalas(escalas_df, my_email, equipe_df)
    if minhas.empty:
        st.warning(
            "Não encontramos culto vinculado ao seu e-mail. "
            "Confira se você está escalado em **Escalas**."
        )
        return

    member_map = members_options_escala(members_df)
    minhas_opts = {
        escala_label_for_user(r, my_email, equipe_df): str(r["id"])
        for _, r in minhas.iterrows()
    }
    with st.form(key="ml_troca_form_v2"):
        minha = st.selectbox("Minha escala", list(minhas_opts.keys()))
        modo = st.radio(
            "Tipo de troca",
            [
                "Divulgar para qualquer integrante assumir",
                "Pedir que integrante específico assuma",
            ],
        )
        target_email = ""
        target_name = ""
        tipo = "aberta"
        outros = [label for label, email in member_map.items() if email != my_email]
        if modo.startswith("Pedir que integrante"):
            tipo = "direcionada"
            outro = st.selectbox("Integrante que deve assumir", outros)
            target_email = member_map[outro]
            tr = members_df[
                members_df["email"].astype(str).str.lower() == target_email
            ].iloc[0]
            target_name = member_display_name(tr)
        msg = st.text_input("Mensagem (opcional)")
        go = st.form_submit_button("📨 Enviar solicitação", type="primary")
    if go:
        oid = minhas_opts[minha]
        if not trocas_df[
            (trocas_df["status"] == "pendente")
            & (trocas_df["escala_id_origem"].astype(str) == str(oid))
        ].empty:
            st.warning("Já existe solicitação pendente para esta escala.")
        else:
            nova = {
                "id": new_id(),
                "escala_id_origem": oid,
                "escala_id_destino": "",
                "requester_email": my_email,
                "requester_name": st.session_state.user_full_name
                or st.session_state.user_name,
                "target_email": target_email,
                "target_name": target_name,
                "status": "pendente",
                "message": msg.strip(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "responded_at": "",
                "tipo": tipo,
                "accepter_email": "",
                "accepter_name": "",
            }
            save_data(
                pd.concat([trocas_df, pd.DataFrame([nova])], ignore_index=True),
                TROCAS_FILE,
            )
            st.success("Solicitação enviada! Acompanhe o status acima.")
            st.rerun()


def _render_swap_tracking_section(
    *,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
) -> None:
    from app import (
        TROCAS_FILE,
        accept_open_swap,
        escala_label,
        prepare_trocas,
        save_data,
        swap_alerts_for_user,
    )

    name = st.session_state.user_full_name or st.session_state.user_name
    abertas, rec, env = swap_alerts_for_user(
        trocas_df, my_email, escalas_df=escalas_df, equipe_df=equipe_df
    )
    if abertas.empty and rec.empty and env.empty:
        st.info("Nenhuma solicitação de troca no momento.")
        return

    st.markdown(
        """
        <div class="swap-priority-panel">
            <p class="swap-priority-title">🔄 Solicitações de troca de escala</p>
            <p class="swap-priority-sub">Prioridade do ministério — responda ou assuma abaixo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 📢 Abertas (qualquer integrante)")
    if abertas.empty:
        st.info("Nenhuma troca aberta no momento.")
    for _, t in abertas.iterrows():
        o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
        txt = escala_label(o.iloc[0]) if not o.empty else "—"
        st.markdown(f"**{t['requester_name']}** — {txt}")
        if t.get("message"):
            st.caption(str(t["message"]))
        if st.button(
            "✅ Assumir esta troca",
            key=f"ml_open_{t['id']}",
            use_container_width=True,
            type="primary",
        ):
            escalas_df, equipe_df, trocas_df, ok = accept_open_swap(
                t, my_email, name, escalas_df, equipe_df, trocas_df
            )
            if ok:
                from app import EQUIPE_FILE, ESCALAS_FILE

                save_data(escalas_df, ESCALAS_FILE)
                save_data(equipe_df, EQUIPE_FILE)
                save_data(trocas_df, TROCAS_FILE)
                st.rerun()
            else:
                st.error("Você já está escalado neste culto — não é possível assumir.")

    st.markdown("#### 📥 Recebidos")
    if rec.empty:
        st.info("Nenhum pedido direcionado a você.")
    for _, t in rec.iterrows():
        o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
        txt = escala_label(o.iloc[0]) if not o.empty else "—"
        st.markdown(f"**{t['requester_name']}** — {txt}")
        if t.get("message"):
            st.caption(str(t["message"]))
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Aceitar", key=f"ml_acc_{t['id']}", use_container_width=True):
                escalas_df, equipe_df, trocas_df, ok = accept_open_swap(
                    t, my_email, name, escalas_df, equipe_df, trocas_df
                )
                if ok:
                    from app import EQUIPE_FILE, ESCALAS_FILE

                    save_data(escalas_df, ESCALAS_FILE)
                    save_data(equipe_df, EQUIPE_FILE)
                    save_data(trocas_df, TROCAS_FILE)
                    st.rerun()
                else:
                    st.error("Não foi possível aceitar (conflito de escala).")
        with c2:
            if st.button("❌ Recusar", key=f"ml_rec_{t['id']}", use_container_width=True):
                trocas_df = prepare_trocas(trocas_df)
                trocas_df.loc[trocas_df["id"].astype(str) == str(t["id"]), "status"] = "recusada"
                trocas_df.loc[
                    trocas_df["id"].astype(str) == str(t["id"]), "responded_at"
                ] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_data(trocas_df, TROCAS_FILE)
                st.rerun()

    st.markdown("#### 📤 Enviados")
    if env.empty:
        st.info("Nenhum pedido enviado pendente.")
    for _, t in env.iterrows():
        o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
        alvo = t.get("target_name") or "o grupo"
        st.caption(
            f"Aguardando {alvo} · {escala_label(o.iloc[0]) if not o.empty else '—'}"
        )
        if st.button("Cancelar", key=f"ml_cancel_{t['id']}"):
            trocas_df.loc[trocas_df["id"] == t["id"], "status"] = "cancelada"
            save_data(trocas_df, TROCAS_FILE)
            st.rerun()


def render_mobile_escalas_page(
    *,
    escalas_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    **_: object,
) -> None:
    """Página Escalas mobile premium com abas e funções do app web."""
    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_escalas_css()}</style>", unsafe_allow_html=True)

    from app import user_on_escala_semana, week_bounds

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0
    start, end = week_bounds(st.session_state.get("week_offset", 0))
    minhas = user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)

    active = _active_tab()
    _render_header()
    _render_tabs(active)

    focus_id = str(st.session_state.get("ml_escalas_focus_id", "")).strip()
    if focus_id and not escalas_df.empty:
        m = escalas_df[escalas_df["id"].astype(str) == focus_id]
        if not m.empty:
            row = m.iloc[0]
            dt = pd.to_datetime(row.get("date"), errors="coerce")
            dt_txt = dt.strftime("%d/%m/%Y") if pd.notna(dt) else ""
            ev = str(row.get("event", "Culto"))
            st.success(f"📅 **{ev}** · Culto em {dt_txt}")

    if active == "visao":
        _render_tab_visao(
            my_email=my_email,
            escalas_df=escalas_df,
            equipe_df=equipe_df,
            members_df=members_df,
            programa_df=programa_df,
            louvores_df=louvores_df,
        )
    elif active == "escalas":
        _render_tab_escalas(
            my_email=my_email,
            escalas_df=escalas_df,
            equipe_df=equipe_df,
            members_df=members_df,
            programa_df=programa_df,
            louvores_df=louvores_df,
        )
    elif active == "sequencia":
        _render_tab_sequencia(
            minhas=minhas,
            programa_df=programa_df,
            louvores_df=louvores_df,
            escalas_df=escalas_df,
            equipe_df=equipe_df,
            members_df=members_df,
        )
    elif active == "disponibilidade":
        _render_tab_disponibilidade(
            my_email=my_email,
            escalas_df=escalas_df,
            equipe_df=equipe_df,
            trocas_df=trocas_df,
            members_df=members_df,
        )
