"""Mobile Lab — Sugestões de louvor (layout compacto, abas)."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme
from sugestao_louvor_ui import (
    _time_ago,
    badge_html,
    compute_sugestao_stats,
    get_sugestao_gestao_tab,
    pack_extra_notes,
    parse_extra_from_notes,
    render_sugestao_gestao_tab_bar,
    sugestao_gestao_tab_filter,
    user_facing_review_note,
)

SUG_VIEWS: tuple[tuple[str, str], ...] = (
    ("minhas", "Minhas"),
    ("nova", "Nova"),
    ("gestao", "Gestão"),
)

MINHAS_FILTERS: tuple[tuple[str, str], ...] = (
    ("todas", "Todas"),
    ("pendente", "Pendentes"),
    ("em_analise", "Em análise"),
    ("aprovada", "Aprovadas"),
    ("recusada", "Recusadas"),
)


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _view() -> str:
    v = str(st.session_state.get("ml_sug_view", "minhas")).strip()
    valid = {k for k, _ in SUG_VIEWS}
    return v if v in valid else "minhas"


def _set_view(view: str) -> None:
    st.session_state.ml_sug_view = view


def _minhas_filter() -> str:
    f = str(st.session_state.get("ml_sug_minhas_filter", "todas")).strip()
    valid = {k for k, _ in MINHAS_FILTERS}
    return f if f in valid else "todas"


def _mine_df(sugestoes_df: pd.DataFrame, email: str) -> pd.DataFrame:
    if not email or sugestoes_df.empty:
        return sugestoes_df.iloc[0:0].copy()
    return sugestoes_df[
        sugestoes_df["suggester_email"].astype(str).str.strip().str.lower() == email
    ].copy()


def mobile_sugestoes_css() -> str:
    return r"""
    body:has(#ml-sugestoes-page) .ig-sug-page,
    body:has(#ml-sugestoes-page) .ig-sug-header,
    body:has(#ml-sugestoes-page) .ig-sug-banner,
    body:has(#ml-sugestoes-page) .ig-sug-footer-banner,
    body:has(#ml-sugestoes-page) .ig-m-hdr-row{ display: none !important; }

    body:has(#ml-sugestoes-page) .ml-rep-header-card{
      margin-top: 0 !important;
      padding-right: 3rem;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_tabs"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 6px !important;
      width: 100% !important;
      margin: 0 0 0.75rem !important;
      padding: 0 0 4px !important;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_tabs"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar{
      display: none;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_tabs"] [data-testid="stColumn"],
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_tabs"] [data-testid="column"]{
      flex: 0 0 auto !important;
      width: auto !important;
      min-width: 0 !important;
      max-width: none !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_tab_"] .stButton > button{
      border-radius: 16px !important;
      min-height: 2.35rem !important;
      padding: 0 0.9rem !important;
      font-weight: 700 !important;
      font-size: 0.78rem !important;
      white-space: nowrap !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(148,163,184,.95) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_tab_"] .stButton > button[kind="primary"]{
      background: rgba(234,179,8,.95) !important;
      color: #0f172a !important;
      border: none !important;
      box-shadow: 0 0 18px rgba(250,204,21,.22) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_filter_"] .stButton > button{
      border-radius: 14px !important;
      min-height: 2rem !important;
      font-size: 0.72rem !important;
      font-weight: 700 !important;
      white-space: nowrap !important;
      background: rgba(7,18,45,.85) !important;
      border: 1px solid rgba(255,255,255,.06) !important;
      color: rgba(148,163,184,.92) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_filter_"] .stButton > button[kind="primary"]{
      background: rgba(124,58,237,.85) !important;
      color: #fff !important;
      border-color: rgba(139,92,246,.35) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_filters"] [data-testid="stHorizontalBlock"],
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_gestao_tabs"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 6px !important;
      scrollbar-width: none;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_filters"] [data-testid="stColumn"],
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_gestao_tabs"] [data-testid="stColumn"]{
      flex: 0 0 auto !important;
      width: auto !important;
      max-width: none !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_gestao_tabs"] .stButton > button{
      border-radius: 14px !important;
      min-height: 2rem !important;
      font-size: 0.7rem !important;
      white-space: nowrap !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_nova"] .stButton > button[kind="primary"],
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_enviar"] .stFormSubmitButton > button,
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_enviar"] .stButton > button{
      width: 100% !important;
      min-height: 3rem !important;
      border-radius: 22px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #facc15, #eab308) !important;
      color: #0f172a !important;
      border: none !important;
      box-shadow: 0 0 28px rgba(250,204,21,.2) !important;
    }
    body:has(#ml-sugestoes-page) .stTextInput > div > div > input,
    body:has(#ml-sugestoes-page) .stTextArea textarea,
    body:has(#ml-sugestoes-page) .stSelectbox > div > div{
      border-radius: 18px !important;
      background: rgba(30,30,30,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      min-height: 2.75rem !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_back"] .stButton > button{
      border-radius: 16px !important;
      font-weight: 700 !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_yt_"] .stLinkButton > a{
      border-radius: 14px !important;
      min-height: 2.2rem !important;
      font-size: 0.75rem !important;
      font-weight: 700 !important;
      background: rgba(15,23,42,.88) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    .ml-sug-stat-grid{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.55rem;
      margin: 0 0 0.85rem;
    }
    .ml-sug-stat{
      background: rgba(11,18,44,.92);
      border-radius: 20px;
      padding: 0.75rem 0.85rem;
      border: 1px solid rgba(255,255,255,.06);
      position: relative;
      overflow: hidden;
    }
    .ml-sug-stat--pend{ border-color: rgba(37,99,235,.28); }
    .ml-sug-stat--analise{ border-color: rgba(234,179,8,.28); }
    .ml-sug-stat--ok{ border-color: rgba(34,197,94,.28); }
    .ml-sug-stat--rej{ border-color: rgba(239,68,68,.28); }
    .ml-sug-stat-num{ font-size: 1.45rem; font-weight: 800; line-height: 1; }
    .ml-sug-stat-lbl{
      margin-top: 0.25rem;
      font-size: 0.68rem;
      font-weight: 700;
      color: rgba(148,163,184,.95);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .ml-sug-section{
      margin: 0.15rem 0 0.55rem;
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }
    .ml-sug-card{
      display: flex;
      align-items: flex-start;
      gap: 0.65rem;
      padding: 0.8rem 0.85rem;
      margin-bottom: 0.55rem;
      border-radius: 20px;
      background: rgba(7,18,45,.88);
      border: 1px solid rgba(255,255,255,.06);
    }
    .ml-sug-cover{
      width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      background: linear-gradient(135deg, #6d28d9, #2563eb);
      font-size: 1rem;
    }
    .ml-sug-card-main{ flex: 1; min-width: 0; }
    .ml-sug-title{
      font-size: 0.88rem; font-weight: 700; line-height: 1.25;
      color: rgba(248,250,252,.98);
      margin: 0;
    }
    .ml-sug-meta{
      margin-top: 0.2rem;
      font-size: 0.72rem;
      color: rgba(148,163,184,.92);
      line-height: 1.35;
    }
    .ml-sug-note{
      margin-top: 0.45rem;
      padding: 0.45rem 0.55rem;
      border-radius: 10px;
      background: rgba(255,255,255,.04);
      font-size: 0.72rem;
      color: rgba(148,163,184,.95);
      line-height: 1.35;
    }
    .ml-sug-tip{
      margin: 0.5rem 0 0.75rem;
      padding: 0.7rem 0.85rem;
      border-radius: 18px;
      background: rgba(139,92,246,.1);
      border: 1px solid rgba(139,92,246,.22);
      font-size: 0.74rem;
      color: rgba(196,181,253,.95);
      line-height: 1.4;
    }
    .ml-sug-empty{
      padding: 1.1rem 0.9rem;
      border-radius: 20px;
      background: rgba(15,23,42,.55);
      border: 1px dashed rgba(255,255,255,.1);
      color: rgba(148,163,184,.95);
      font-size: 0.82rem;
      text-align: center;
      line-height: 1.45;
    }
    """


def _render_header(*, pending: int) -> None:
    badge = (
        f' · <span style="color:#fde68a;">{pending} pendente(s)</span>'
        if pending > 0
        else ""
    )
    st.markdown(
        f"""
        <div id="ml-sugestoes-page" class="ml-page">
          <div class="ml-rep-header-card" style="margin-bottom:0.65rem;border-color:rgba(250,204,21,.22);">
            <div class="ml-rep-header-row">
              <div class="ml-rep-header-icon" style="background:linear-gradient(135deg,#facc15,#ca8a04);">💡</div>
              <div class="ml-rep-header-text">
                <h1 class="ml-rep-header-title">Sugestões de louvor</h1>
                <p class="ml-rep-header-sub">Envie músicas para análise da liderança{badge}</p>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_view_tabs(*, mgr: bool) -> None:
    active = _view()
    tabs = list(SUG_VIEWS) if mgr else [t for t in SUG_VIEWS if t[0] != "gestao"]
    with st.container(key="ml_sug_tabs"):
        cols = st.columns(len(tabs))
        for col, (key, label) in zip(cols, tabs):
            with col:
                if st.button(
                    label,
                    key=f"ml_sug_tab_{key}",
                    use_container_width=True,
                    type="primary" if active == key else "secondary",
                ):
                    _set_view(key)
                    st.rerun()


def _render_kpis(counts: dict[str, int]) -> None:
    cards = [
        ("pend", counts.get("pendente", 0), "Pendentes", "ml-sug-stat--pend"),
        ("analise", counts.get("em_analise", 0), "Em análise", "ml-sug-stat--analise"),
        ("ok", counts.get("aprovada", 0), "Aprovadas", "ml-sug-stat--ok"),
        ("rej", counts.get("recusada", 0), "Recusadas", "ml-sug-stat--rej"),
    ]
    parts = ['<div class="ml-sug-stat-grid">']
    for _k, val, lbl, cls in cards:
        parts.append(
            f'<div class="ml-sug-stat {cls}">'
            f'<div class="ml-sug-stat-num">{val}</div>'
            f'<div class="ml-sug-stat-lbl">{_esc(lbl)}</div></div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def _render_minhas_filters() -> None:
    active = _minhas_filter()
    with st.container(key="ml_sug_filters"):
        cols = st.columns(len(MINHAS_FILTERS))
        for col, (key, label) in zip(cols, MINHAS_FILTERS):
            with col:
                if st.button(
                    label,
                    key=f"ml_sug_filter_{key}",
                    use_container_width=True,
                    type="primary" if active == key else "secondary",
                ):
                    st.session_state.ml_sug_minhas_filter = key
                    st.rerun()


def _suggestion_card_html(
    *,
    title: str,
    artist: str,
    when: str,
    status_key: str,
    status_label: str,
    note: str = "",
) -> str:
    artist_line = _esc(artist) if artist else "—"
    note_html = (
        f'<div class="ml-sug-note">{_esc(note)}</div>' if note else ""
    )
    return (
        f'<div class="ml-sug-card">'
        f'<div class="ml-sug-cover">🎵</div>'
        f'<div class="ml-sug-card-main">'
        f'<p class="ml-sug-title">{_esc(title)}</p>'
        f'<div class="ml-sug-meta">{artist_line} · {_esc(when)}</div>'
        f'<div style="margin-top:0.35rem;">{badge_html(status_key, status_label)}</div>'
        f"{note_html}"
        f"</div></div>"
    )


def _render_minhas_list(sugestoes_df: pd.DataFrame, email: str) -> None:
    mine = _mine_df(sugestoes_df, email)
    if mine.empty:
        st.markdown(
            '<div class="ml-sug-empty">Você ainda não enviou sugestões.<br>'
            'Toque em <strong>Nova</strong> para sugerir um louvor.</div>',
            unsafe_allow_html=True,
        )
        return

    from app import SUGESTAO_STATUS_LABELS, normalize_sugestao_status

    filt = _minhas_filter()
    mine["_st"] = mine["status"].astype(str).map(normalize_sugestao_status)
    if filt != "todas":
        mine = mine[mine["_st"] == filt]
    mine["_ord"] = pd.to_datetime(mine["created_at"], errors="coerce")
    mine = mine.sort_values("_ord", ascending=False).head(12)

    st.markdown('<div class="ml-sug-section">Suas sugestões</div>', unsafe_allow_html=True)
    if mine.empty:
        st.markdown(
            '<div class="ml-sug-empty">Nenhuma sugestão neste filtro.</div>',
            unsafe_allow_html=True,
        )
        return

    for i, (_, s) in enumerate(mine.iterrows()):
        status = normalize_sugestao_status(str(s.get("status", "")))
        sid = str(s["id"])
        artist = parse_extra_from_notes(str(s.get("review_notes", "")))
        when = _time_ago(str(s.get("created_at", "")))
        note = ""
        if status in ("recusada", "em_analise"):
            note = user_facing_review_note(str(s.get("review_notes", "")))
        st.markdown(
            _suggestion_card_html(
                title=str(s["title"]),
                artist=artist,
                when=when,
                status_key=status,
                status_label=SUGESTAO_STATUS_LABELS.get(status, status),
                note=note,
            ),
            unsafe_allow_html=True,
        )
        yt = str(s.get("youtube_url", "")).strip()
        if yt.startswith("http"):
            with st.container(key=f"ml_sug_yt_{sid}_{i}"):
                st.link_button("▶ YouTube", yt, use_container_width=True, key=f"ml_sug_yt_btn_{sid}_{i}")


def _render_nova_form(sugestoes_df: pd.DataFrame) -> None:
    from app import (
        SUGESTAO_STATUS_PENDENTE,
        SUGESTOES_FILE,
        new_id,
        prepare_sugestoes,
        save_data,
        show_form_error,
    )

    with st.container(key="ml_sug_back"):
        if st.button("← Voltar para Minhas", use_container_width=True, key="ml_sug_back_btn"):
            _set_view("minhas")
            st.rerun()

    st.markdown(
        '<div class="ml-sug-section">Nova sugestão</div>'
        '<p class="ml-rep-header-sub" style="margin:0 0 0.75rem;">'
        "Preencha o essencial. Detalhes extras ajudam a liderança na análise.</p>",
        unsafe_allow_html=True,
    )

    tema = categoria = ministracao = tom = observacoes = ""
    tem_cifra = tem_playback = tem_kit = tem_cong = False

    with st.form(key="ml_sugestao_form"):
        titulo = st.text_input("Nome da música *", placeholder="Nome da música")
        artista = st.text_input("Artista / Ministério", placeholder="Artista ou ministério")
        yt = st.text_input("Link YouTube *", placeholder="https://youtube.com/...")
        with st.expander("Mais detalhes (opcional)", expanded=False):
            tema = st.text_input("Tema bíblico", placeholder="Ex.: Adoração")
            categoria = st.selectbox(
                "Categoria",
                ["", "Adoração", "Louvor", "Missões", "Comunhão", "Outra"],
            )
            ministracao = st.text_input("Ministração sugerida", placeholder="Ex.: Abertura")
            tom = st.selectbox("Tom original", ["", "C", "D", "E", "F", "G", "A", "Bb"])
            observacoes = st.text_area(
                "Observações",
                placeholder="Contexto para a liderança.",
                height=72,
            )
            c1, c2 = st.columns(2)
            with c1:
                tem_cifra = st.checkbox("Tem cifra")
                tem_playback = st.checkbox("Tem playback")
            with c2:
                tem_kit = st.checkbox("Tem kit voz")
                tem_cong = st.checkbox("Versão congregacional")
        with st.container(key="ml_sug_enviar"):
            enviar = st.form_submit_button(
                "✈ Enviar sugestão",
                type="primary",
                use_container_width=True,
            )

    if enviar:
        if not titulo.strip() or not yt.strip():
            show_form_error("Informe nome e link do YouTube.")
        elif "youtube" not in yt.lower() and "youtu.be" not in yt.lower():
            st.warning("Use um link válido do YouTube.")
        else:
            extra = pack_extra_notes(
                artista=artista,
                tema=tema,
                categoria=categoria,
                ministracao=ministracao,
                tom=tom,
                observacoes=observacoes,
                tem_cifra=tem_cifra,
                tem_playback=tem_playback,
                tem_kit=tem_kit,
                tem_cong=tem_cong,
            )
            nova = {
                "id": new_id(),
                "title": titulo.strip().title(),
                "youtube_url": yt.strip(),
                "suggester_email": st.session_state.user_email,
                "suggester_name": st.session_state.user_full_name
                or st.session_state.user_name,
                "status": SUGESTAO_STATUS_PENDENTE,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "review_notes": extra,
            }
            save_data(
                prepare_sugestoes(
                    pd.concat([sugestoes_df, pd.DataFrame([nova])], ignore_index=True)
                ),
                SUGESTOES_FILE,
            )
            st.session_state.ml_sug_minhas_filter = "pendente"
            _set_view("minhas")
            st.success("Sugestão enviada! Acompanhe o status em Minhas.")
            st.rerun()


def _render_gestao_panel(sugestoes_df: pd.DataFrame, louvores_df: pd.DataFrame) -> None:
    from app import _render_gestao_sugestoes_lideranca

    st.markdown(
        '<div class="ml-sug-section">Gestão (liderança)</div>'
        '<p class="ml-rep-header-sub" style="margin:0 0 0.65rem;">'
        "Analise, aprove ou recuse sugestões da equipe.</p>",
        unsafe_allow_html=True,
    )

    @st.fragment
    def _gestao_fragment() -> None:
        sug_tab = get_sugestao_gestao_tab()
        with st.container(key="ml_sug_gestao_tabs"):
            render_sugestao_gestao_tab_bar(sug_tab, use_fragment=True)
        tf = sugestao_gestao_tab_filter(sug_tab)
        _render_gestao_sugestoes_lideranca(
            sugestoes_df,
            louvores_df,
            premium=False,
            tab_filter=tf,
            key_prefix=f"ml_gest_{tf}",
        )

    _gestao_fragment()


def render_mobile_sugestoes_page(
    sugestoes_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    from app import (
        count_pending_sugestoes,
        is_scale_manager,
        mark_user_sugestoes_seen,
        normalize_sugestao_status,
        prepare_sugestoes,
    )

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_sugestoes_css()}</style>", unsafe_allow_html=True)

    mgr = is_scale_manager(st.session_state.get("user_roles", []))
    my_email = str(st.session_state.get("user_email", "")).strip().lower()

    mark_user_sugestoes_seen(sugestoes_df, my_email)
    sugestoes_df = prepare_sugestoes(sugestoes_df)

    pending = count_pending_sugestoes(sugestoes_df) if mgr else 0
    _render_header(pending=pending)

    with st.container(key="ml_sug_nova"):
        if st.button("+ Nova sugestão", key="ml_sug_nova_btn", type="primary", use_container_width=True):
            _set_view("nova")
            st.rerun()

    _render_view_tabs(mgr=mgr)

    view = _view()
    if view == "nova":
        _render_nova_form(sugestoes_df)
        return

    if view == "gestao" and mgr:
        _render_gestao_panel(sugestoes_df, louvores_df)
        return

    if view == "gestao" and not mgr:
        _set_view("minhas")

    stats_df = _mine_df(sugestoes_df, my_email)
    counts = compute_sugestao_stats(stats_df, normalize_sugestao_status)
    _render_kpis(counts)
    _render_minhas_filters()
    _render_minhas_list(sugestoes_df, my_email)

    st.markdown(
        '<div class="ml-sug-tip">💡 Escolha músicas congregacionais, verifique a letra '
        "bíblica e envie o link do YouTube. Sugestões aprovadas podem entrar no repertório.</div>",
        unsafe_allow_html=True,
    )
