"""Mobile Lab — Sugestões de louvor (hub premium conforme mockup)."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme
from sugestao_louvor_ui import (
    _time_ago,
    compute_sugestao_stats,
    get_sugestao_gestao_tab,
    pack_extra_notes,
    parse_extra_from_notes,
    render_sugestao_gestao_tab_bar,
    sugestao_gestao_tab_filter,
    user_facing_review_note,
)

SUG_VIEWS = frozenset({"hub", "nova", "minhas", "gestao"})

MINHAS_FILTERS: tuple[tuple[str, str], ...] = (
    ("todas", "Todas"),
    ("pendente", "Pendentes"),
    ("em_analise", "Em análise"),
    ("aprovada", "Aprovadas"),
    ("recusada", "Recusadas"),
)

_STATUS_MSG = {
    "aprovada": "Aprovada pela liderança.",
    "em_analise": "Sua sugestão está sendo avaliada.",
    "pendente": "Aguardando análise da liderança.",
    "recusada": "Recusada pela liderança.",
}


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _view() -> str:
    v = str(st.session_state.get("ml_sug_view", "hub")).strip()
    return v if v in SUG_VIEWS else "hub"


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


def _status_badge(status_key: str, label: str) -> str:
    cls = {
        "aprovada": "ml-sug-badge--ok",
        "em_analise": "ml-sug-badge--analise",
        "recusada": "ml-sug-badge--rej",
        "pendente": "ml-sug-badge--pend",
    }.get(status_key, "ml-sug-badge--pend")
    return f'<span class="ml-sug-badge {cls}">{_esc(label)}</span>'


def _top_suggesters(sugestoes_df: pd.DataFrame, *, limit: int = 5) -> list[tuple[str, int]]:
    if sugestoes_df.empty or "suggester_name" not in sugestoes_df.columns:
        return []
    names = (
        sugestoes_df["suggester_name"]
        .astype(str)
        .str.strip()
        .replace("", "Integrante")
    )
    counts = names.value_counts().head(limit)
    return [(str(n), int(c)) for n, c in counts.items()]


def mobile_sugestoes_css() -> str:
    return r"""
    body:has(#ml-sugestoes-page) .ig-sug-page,
    body:has(#ml-sugestoes-page) .ig-sug-header,
    body:has(#ml-sugestoes-page) .ig-sug-banner,
    body:has(#ml-sugestoes-page) .ig-sug-footer-banner,
    body:has(#ml-sugestoes-page) .ig-m-hdr-row{ display: none !important; }

    body:has(#ml-sugestoes-page) [data-testid="stMain"] .block-container{
      padding-top: 0.5rem !important;
      max-width: 900px !important;
    }

    .ml-sug-titulo{
      font-size: 1.55rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      margin: 0;
      line-height: 1.1;
    }
    .ml-sug-sub{
      color: #b7bfd1;
      font-size: 0.82rem;
      margin: 0.35rem 0 0;
      line-height: 1.35;
    }
    .ml-sug-hero{
      background: linear-gradient(135deg, #5B21B6, #312E81);
      border-radius: 28px;
      padding: 1.15rem 1.1rem;
      margin: 0.75rem 0 0.85rem;
      border: 1px solid rgba(255,255,255,.1);
      box-shadow: 0 0 40px rgba(91,33,182,.25);
    }
    .ml-sug-hero h2{
      margin: 0 0 0.35rem;
      font-size: 1.05rem;
      font-weight: 800;
    }
    .ml-sug-hero p{
      margin: 0;
      font-size: 0.8rem;
      color: rgba(226,232,240,.92);
      line-height: 1.45;
    }
    .ml-sug-card{
      background: rgba(10,20,50,.70);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 24px;
      padding: 1rem 1.05rem;
      margin-bottom: 0.75rem;
      backdrop-filter: blur(20px);
    }
    .ml-sug-card h3{
      margin: 0 0 0.55rem;
      font-size: 0.95rem;
      font-weight: 800;
    }
    .ml-sug-card p, .ml-sug-card li{
      margin: 0;
      font-size: 0.78rem;
      color: rgba(203,213,225,.95);
      line-height: 1.5;
    }
    .ml-sug-steps{
      margin: 0.5rem 0 0.85rem;
      padding-left: 1.1rem;
    }
    .ml-sug-stat{
      background: #091633;
      border-radius: 20px;
      padding: 0.85rem 0.5rem;
      text-align: center;
      border: 1px solid rgba(255,255,255,.06);
    }
    .ml-sug-stat h1{
      margin: 0;
      font-size: 1.65rem;
      font-weight: 800;
      line-height: 1;
    }
    .ml-sug-stat span{
      display: block;
      margin-top: 0.35rem;
      font-size: 0.68rem;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .ml-sug-feed{
      background: #07152d;
      border-radius: 20px;
      padding: 0.95rem 1rem;
      margin-bottom: 0.65rem;
      border: 1px solid rgba(255,255,255,.06);
    }
    .ml-sug-feed h4{
      margin: 0 0 0.45rem;
      font-size: 0.92rem;
      font-weight: 700;
    }
    .ml-sug-feed-meta{
      font-size: 0.72rem;
      color: #94a3b8;
      margin: 0.35rem 0 0.5rem;
    }
    .ml-sug-feed-msg{
      font-size: 0.78rem;
      color: #cbd5e1;
      line-height: 1.4;
      margin: 0.5rem 0 0;
    }
    .ml-sug-badge{
      display: inline-block;
      padding: 0.28rem 0.65rem;
      border-radius: 999px;
      font-size: 0.68rem;
      font-weight: 700;
    }
    .ml-sug-badge--ok{ background:#064e3b; color:#6ee7b7; }
    .ml-sug-badge--analise{ background:#172554; color:#60a5fa; }
    .ml-sug-badge--rej{ background:#450a0a; color:#fca5a5; }
    .ml-sug-badge--pend{ background:#422006; color:#fde68a; }
    .ml-sug-rank{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      background: #07152d;
      border-radius: 18px;
      padding: 0.75rem 0.95rem;
      margin-bottom: 0.5rem;
      border: 1px solid rgba(255,255,255,.06);
      font-size: 0.84rem;
    }
    .ml-sug-rank b{ color: #a78bfa; font-weight: 800; }
    .ml-sug-section-title{
      margin: 0.85rem 0 0.55rem;
      font-size: 1rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }
    .ml-sug-empty{
      padding: 1rem;
      border-radius: 20px;
      background: rgba(15,23,42,.55);
      border: 1px dashed rgba(255,255,255,.1);
      color: #94a3b8;
      font-size: 0.82rem;
      text-align: center;
      line-height: 1.45;
    }
  body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_act_"] .stButton > button{
      min-height: 3.1rem !important;
      border-radius: 22px !important;
      font-weight: 800 !important;
      font-size: 0.82rem !important;
      background: rgba(10,20,50,.85) !important;
      border: 1px solid rgba(139,92,246,.28) !important;
      color: #e9d5ff !important;
      box-shadow: 0 0 24px rgba(91,33,182,.12) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_act_nova"] .stButton > button{
      background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
      color: #fff !important;
      border: none !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_enviar"] .stFormSubmitButton > button,
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_enviar"] .stButton > button{
      width: 100% !important;
      min-height: 3rem !important;
      border-radius: 22px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
      color: #fff !important;
      border: none !important;
      box-shadow: 0 0 28px rgba(124,58,237,.28) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_back"] .stButton > button{
      border-radius: 16px !important;
      font-weight: 700 !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      margin-bottom: 0.5rem !important;
    }
    body:has(#ml-sugestoes-page) .stTextInput > div > div > input,
    body:has(#ml-sugestoes-page) .stTextArea textarea,
    body:has(#ml-sugestoes-page) .stSelectbox > div > div{
      border-radius: 18px !important;
      background: rgba(7,21,45,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      min-height: 2.75rem !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_filter_"] .stButton > button{
      border-radius: 14px !important;
      min-height: 2rem !important;
      font-size: 0.7rem !important;
      font-weight: 700 !important;
      white-space: nowrap !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_filters"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 6px !important;
      scrollbar-width: none;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_filters"] [data-testid="stColumn"]{
      flex: 0 0 auto !important;
      width: auto !important;
      max-width: none !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_gestao_tabs"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 6px !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_gestao_tabs"] [data-testid="stColumn"]{
      flex: 0 0 auto !important;
      width: auto !important;
      max-width: none !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_yt_"] .stLinkButton > a{
      border-radius: 14px !important;
      min-height: 2.1rem !important;
      font-size: 0.74rem !important;
      font-weight: 700 !important;
    }
    """


def _render_page_open() -> None:
    st.markdown('<div id="ml-sugestoes-page" class="ml-page">', unsafe_allow_html=True)


def _render_header(*, pending: int) -> None:
    extra = (
        f' <span style="color:#fde68a;">· {pending} pendente(s)</span>'
        if pending > 0
        else ""
    )
    st.markdown(
        f"""
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:0.75rem;padding-right:2.5rem;">
          <div>
            <div class="ml-sug-titulo">🎵 Sugestões de Louvor</div>
            <p class="ml-sug-sub">Ajude a construir nosso repertório{extra}</p>
          </div>
          <div style="width:42px;height:42px;border-radius:14px;display:flex;align-items:center;justify-content:center;
            background:linear-gradient(135deg,#facc15,#ca8a04);font-size:1.2rem;flex-shrink:0;
            box-shadow:0 0 24px rgba(250,204,21,.25);">💡</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hero() -> None:
    st.markdown(
        """
        <div class="ml-sug-hero">
          <h2>Sua sugestão faz diferença!</h2>
          <p>Envie músicas para análise da liderança e acompanhe todo o processo.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_quick_actions(*, mgr: bool) -> None:
    cols = st.columns(3 if mgr else 2, gap="small")
    with cols[0]:
        with st.container(key="ml_sug_act_nova"):
            if st.button("➕ Nova sugestão", use_container_width=True, key="ml_sug_btn_nova"):
                _set_view("nova")
                st.rerun()
    with cols[1]:
        with st.container(key="ml_sug_act_minhas"):
            if st.button("📋 Minhas sugestões", use_container_width=True, key="ml_sug_btn_minhas"):
                _set_view("minhas")
                st.rerun()
    if mgr:
        with cols[2]:
            with st.container(key="ml_sug_act_gestao"):
                if st.button("⚙️ Gestão", use_container_width=True, key="ml_sug_btn_gestao"):
                    _set_view("gestao")
                    st.rerun()


def _render_como_funciona() -> None:
    st.markdown(
        """
        <div class="ml-sug-card">
          <h3>❓ Como funciona?</h3>
          <ol class="ml-sug-steps">
            <li>Informe a música e o artista</li>
            <li>Cole o link do YouTube</li>
            <li>A liderança avalia</li>
            <li>Você recebe o retorno aqui</li>
          </ol>
          <div style="margin-top:0.65rem;display:flex;flex-wrap:wrap;gap:0.35rem;">
            <span class="ml-sug-badge ml-sug-badge--pend">🟠 Pendente</span>
            <span class="ml-sug-badge ml-sug-badge--analise">🔵 Em análise</span>
            <span class="ml-sug-badge ml-sug-badge--ok">🟢 Aprovada</span>
            <span class="ml-sug-badge ml-sug-badge--rej">🔴 Recusada</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_stats(counts: dict[str, int]) -> None:
    st.markdown('<div class="ml-sug-section-title">📊 Suas estatísticas</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    items = [
        (a, counts.get("aprovada", 0), "Aprovadas"),
        (b, counts.get("em_analise", 0), "Em análise"),
        (c, counts.get("pendente", 0), "Pendentes"),
    ]
    for col, val, lbl in items:
        with col:
            st.markdown(
                f'<div class="ml-sug-stat"><h1>{val}</h1><span>{_esc(lbl)}</span></div>',
                unsafe_allow_html=True,
            )


def _feed_message(status: str, review_notes: str) -> str:
    if status == "recusada":
        note = user_facing_review_note(review_notes)
        if note:
            return note
    return _STATUS_MSG.get(status, "Acompanhe o status da sua sugestão.")


def _feed_card_html(
    *,
    title: str,
    artist: str,
    when: str,
    status_key: str,
    status_label: str,
    message: str,
) -> str:
    artist_line = _esc(artist) if artist else "—"
    return (
        f'<div class="ml-sug-feed">'
        f'<h4>🎵 {_esc(title)}</h4>'
        f"{_status_badge(status_key, status_label)}"
        f'<div class="ml-sug-feed-meta">{artist_line} · {_esc(when)}</div>'
        f'<p class="ml-sug-feed-msg">{_esc(message)}</p>'
        f"</div>"
    )


def _render_feed(
    sugestoes_df: pd.DataFrame,
    email: str,
    *,
    title: str = "📰 Suas sugestões recentes",
    limit: int = 6,
    use_filter: bool = False,
) -> None:
    from app import SUGESTAO_STATUS_LABELS, normalize_sugestao_status

    mine = _mine_df(sugestoes_df, email)
    st.markdown(f'<div class="ml-sug-section-title">{_esc(title)}</div>', unsafe_allow_html=True)

    if mine.empty:
        st.markdown(
            '<div class="ml-sug-empty">Nenhuma sugestão ainda.<br>'
            "Toque em <strong>Nova sugestão</strong> para começar.</div>",
            unsafe_allow_html=True,
        )
        return

    filt = _minhas_filter() if use_filter else "todas"
    mine = mine.copy()
    mine["_st"] = mine["status"].astype(str).map(normalize_sugestao_status)
    if filt != "todas":
        mine = mine[mine["_st"] == filt]
    mine["_ord"] = pd.to_datetime(mine["created_at"], errors="coerce")
    mine = mine.sort_values("_ord", ascending=False).head(limit)

    if mine.empty:
        st.markdown('<div class="ml-sug-empty">Nenhuma sugestão neste filtro.</div>', unsafe_allow_html=True)
        return

    for i, (_, s) in enumerate(mine.iterrows()):
        status = normalize_sugestao_status(str(s.get("status", "")))
        sid = str(s["id"])
        artist = parse_extra_from_notes(str(s.get("review_notes", "")))
        when = _time_ago(str(s.get("created_at", "")))
        msg = _feed_message(status, str(s.get("review_notes", "")))
        st.markdown(
            _feed_card_html(
                title=str(s["title"]),
                artist=artist,
                when=when,
                status_key=status,
                status_label=SUGESTAO_STATUS_LABELS.get(status, status),
                message=msg,
            ),
            unsafe_allow_html=True,
        )
        yt = str(s.get("youtube_url", "")).strip()
        if yt.startswith("http"):
            with st.container(key=f"ml_sug_yt_{sid}_{i}"):
                st.link_button("▶ YouTube", yt, use_container_width=True, key=f"ml_sug_yt_btn_{sid}_{i}")


def _render_ranking(sugestoes_df: pd.DataFrame) -> None:
    ranking = _top_suggesters(sugestoes_df, limit=5)
    if len(ranking) < 2:
        return
    st.markdown('<div class="ml-sug-section-title">🏆 Sugestores mais ativos</div>', unsafe_allow_html=True)
    parts = []
    for nome, total in ranking:
        parts.append(
            f'<div class="ml-sug-rank"><span>{_esc(nome)}</span>'
            f"<b>{total} sugestões</b></div>"
        )
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
        if st.button("← Voltar", use_container_width=True, key="ml_sug_back_btn"):
            _set_view("hub")
            st.rerun()

    st.markdown(
        '<div class="ml-sug-section-title">➕ Enviar nova sugestão</div>',
        unsafe_allow_html=True,
    )

    tema = categoria = ministracao = tom = observacoes = ""
    tem_cifra = tem_playback = tem_kit = tem_cong = False

    with st.form(key="ml_sugestao_form"):
        titulo = st.text_input("Nome da música *", placeholder="Nome da música")
        artista = st.text_input("Artista / Ministério", placeholder="Artista ou ministério")
        yt = st.text_input("Link YouTube *", placeholder="https://youtube.com/...")
        tema = st.text_input("Tema bíblico (opcional)", placeholder="Ex.: Adoração")
        with st.expander("Mais detalhes (opcional)", expanded=False):
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
                "🚀 Enviar sugestão",
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
            st.success("Sugestão enviada! Acompanhe em Minhas sugestões.")
            st.rerun()


def _render_gestao_panel(sugestoes_df: pd.DataFrame, louvores_df: pd.DataFrame) -> None:
    from app import _render_gestao_sugestoes_lideranca

    with st.container(key="ml_sug_back"):
        if st.button("← Voltar", use_container_width=True, key="ml_sug_gestao_back"):
            _set_view("hub")
            st.rerun()

    st.markdown(
        '<div class="ml-sug-section-title">⚙️ Gestão (liderança)</div>'
        '<p class="ml-sug-sub" style="margin-bottom:0.75rem;">'
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


def _render_hub(
    sugestoes_df: pd.DataFrame,
    email: str,
    counts: dict[str, int],
    *,
    mgr: bool,
) -> None:
    _render_hero()
    _render_quick_actions(mgr=mgr)
    _render_como_funciona()
    _render_stats(counts)
    _render_feed(sugestoes_df, email, limit=4)
    _render_ranking(sugestoes_df)


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
    stats_df = _mine_df(sugestoes_df, my_email)
    counts = compute_sugestao_stats(stats_df, normalize_sugestao_status)

    _render_page_open()
    _render_header(pending=pending)

    view = _view()
    if view == "nova":
        _render_nova_form(sugestoes_df)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if view == "gestao" and mgr:
        _render_gestao_panel(sugestoes_df, louvores_df)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if view == "gestao" and not mgr:
        _set_view("hub")
        view = "hub"

    if view == "minhas":
        with st.container(key="ml_sug_back"):
            if st.button("← Voltar", use_container_width=True, key="ml_sug_minhas_back"):
                _set_view("hub")
                st.rerun()
        _render_stats(counts)
        _render_minhas_filters()
        _render_feed(
            sugestoes_df,
            my_email,
            title="📋 Minhas sugestões",
            limit=12,
            use_filter=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    _render_hub(sugestoes_df, my_email, counts, mgr=mgr)
    st.markdown("</div>", unsafe_allow_html=True)
