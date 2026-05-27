"""Mobile Lab — Sequência do Culto (marcações, cifra, lista premium)."""

from __future__ import annotations

import html
from typing import Any

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme

SUB_TABS: tuple[tuple[str, str, str], ...] = (
    ("lista", "🎶", "Sequência"),
    ("vocal", "🎤", "Vocal"),
    ("banda", "🎹", "Banda"),
    ("cifra", "🎸", "Cifra"),
    ("editar", "✏️", "Editar"),
)

def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _view() -> str:
    v = str(st.session_state.get("ml_seq_view", "lista")).strip()
    return v if v in ("lista", "musica") else "lista"


def _set_view(view: str) -> None:
    st.session_state.ml_seq_view = view


def _sub() -> str:
    s = str(st.session_state.get("ml_seq_sub", "lista")).strip()
    return s if s in {k for k, _, _ in SUB_TABS} else "lista"


def _set_sub(sub: str) -> None:
    st.session_state.ml_seq_sub = sub


def mobile_sequencia_css() -> str:
    return r"""
    body:has(#ml-sequencia-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-sequencia-page) .ml-seq-header{
      background: rgba(11,18,39,.75);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 28px;
      padding: 1.25rem 1.1rem;
      margin-bottom: 1rem;
      position: relative;
      overflow: hidden;
    }
    body:has(#ml-sequencia-page) .ml-seq-header::before{
      content: '';
      position: absolute;
      width: 140px;
      height: 140px;
      background: rgba(139,92,246,.15);
      border-radius: 50%;
      top: -50px;
      right: -40px;
    }
    body:has(#ml-sequencia-page) .ml-seq-header h1{
      margin: 0;
      font-size: 1.65rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }
    body:has(#ml-sequencia-page) .ml-seq-header p{
      margin: 0.4rem 0 0;
      color: #9ca3af;
      font-size: 0.9rem;
    }
    body:has(#ml-sequencia-page) .ml-seq-card{
      background: rgba(7,14,35,.88);
      border: 1px solid rgba(255,255,255,.05);
      border-radius: 24px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
    body:has(#ml-sequencia-page) .ml-seq-section-title{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 1.15rem;
      font-weight: 800;
      margin-bottom: 0.65rem;
    }
    body:has(#ml-sequencia-page) .ml-seq-subtitle{
      color: #94a3b8;
      font-size: 0.86rem;
      line-height: 1.5;
      margin-bottom: 0.85rem;
    }
    body:has(#ml-sequencia-page) .ml-seq-music{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      background: #0f172a;
      border-radius: 18px;
      padding: 1rem;
      margin-bottom: 0.65rem;
      border: 1px solid rgba(255,255,255,.04);
    }
    body:has(#ml-sequencia-page) .ml-seq-music h3{
      margin: 0 0 0.25rem;
      font-size: 1rem;
      font-weight: 800;
    }
    body:has(#ml-sequencia-page) .ml-seq-music span{
      color: #94a3b8;
      font-size: 0.82rem;
    }
    body:has(#ml-sequencia-page) .ml-seq-num{
      width: 36px;
      height: 36px;
      border-radius: 12px;
      background: #7c3aed;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.9rem;
      flex-shrink: 0;
    }
    body:has(#ml-sequencia-page) .ml-seq-dur{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 0.9rem;
      border-radius: 16px;
      background: rgba(15,23,42,.72);
      border: 1px solid rgba(255,255,255,.06);
      margin: 0.5rem 0 0.85rem;
      font-size: 0.88rem;
      color: rgba(226,232,240,.92);
    }
    body:has(#ml-sequencia-page) .ml-seq-cifra-box{
      background: #111827;
      border-radius: 24px;
      padding: 1rem;
      border: 1px solid rgba(255,255,255,.05);
      margin-top: 0.75rem;
    }
    body:has(#ml-sequencia-page) .ml-seq-cifra-box .seq-cifra-view{
      font-size: 0.95rem;
    }
    body:has(#ml-sequencia-page) .ml-seq-cifra-box .cifra-chord{
      color: #facc15 !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_pick"] .stSelectbox > div > div,
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_pick"] .stSelectbox label{
      font-weight: 700 !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_sub_"] .stButton > button{
      border-radius: 16px !important;
      min-height: 2.45rem !important;
      font-weight: 700 !important;
      font-size: 0.72rem !important;
      white-space: nowrap !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(148,163,184,.95) !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_sub_"] .stButton > button[kind="primary"]{
      background: linear-gradient(135deg, #7c3aed, #9333ea) !important;
      border: none !important;
      color: #fff !important;
      box-shadow: 0 8px 24px rgba(124,58,237,.3) !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_song_"] .stButton > button{
      width: 100% !important;
      text-align: left !important;
      justify-content: flex-start !important;
      min-height: 4.2rem !important;
      padding: 0.65rem 0.85rem !important;
      border-radius: 18px !important;
      background: rgba(15,23,42,.55) !important;
      border: 1px solid rgba(255,255,255,.06) !important;
      margin-bottom: 0.35rem !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_song_"] .stButton > button p{
      margin: 0 !important;
      text-align: left !important;
      white-space: normal !important;
      font-size: 0.82rem !important;
      line-height: 1.3 !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_back"] .stButton > button{
      border-radius: 16px !important;
      font-weight: 700 !important;
      background: rgba(15,23,42,.65) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_btn_primary"] .stButton > button[kind="primary"]{
      width: 100% !important;
      min-height: 3.1rem !important;
      border-radius: 18px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #7c3aed, #9333ea) !important;
      border: none !important;
      box-shadow: 0 10px 30px rgba(124,58,237,.35) !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_btn_green"] .stButton > button{
      width: 100% !important;
      min-height: 3.1rem !important;
      border-radius: 18px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #047857, #10b981) !important;
      color: #fff !important;
      border: none !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_btn_wa"] .stButton > button{
      width: 100% !important;
      min-height: 3.1rem !important;
      border-radius: 18px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #15803d, #22c55e) !important;
      color: #fff !important;
      border: none !important;
    }
    body:has(#ml-sequencia-page) [class*="st-key-ml_seq_btn_danger"] .stButton > button{
      width: 100% !important;
      min-height: 2.8rem !important;
      border-radius: 18px !important;
      font-weight: 700 !important;
      background: #111827 !important;
      border: 1px solid rgba(239,68,68,.4) !important;
      color: #ef4444 !important;
    }
  """


def _render_page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="ml-seq-header">
          <h1>{_esc(title)}</h1>
          <p>{_esc(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_sub_tabs(active: str, *, can_edit: bool) -> None:
    tabs = [t for t in SUB_TABS if t[0] != "editar" or can_edit]
    with st.container(key="ml_seq_sub_tabs"):
        cols = st.columns(len(tabs))
        for col, (key, icon, label) in zip(cols, tabs):
            with col:
                with st.container(key=f"ml_seq_sub_{key}"):
                    if st.button(
                        f"{icon}\n{label}",
                        key=f"ml_seq_sub_btn_{key}",
                        use_container_width=True,
                        type="primary" if active == key else "secondary",
                    ):
                        _set_sub(key)
                        st.rerun()


def _culto_options(
    *,
    minhas: list[dict],
    escalas_df: pd.DataFrame,
    all_escalas: bool,
) -> dict[str, str]:
    from app import escalas_ordenadas, escala_label

    if all_escalas:
        todas = escalas_ordenadas(escalas_df)
        if todas.empty:
            return {}
        return {escala_label(r): str(r["id"]) for _, r in todas.iterrows()}

    if not minhas:
        return {}
    out: dict[str, str] = {}
    for item in minhas:
        row = item["escala"]
        eid = str(row.get("id", ""))
        lbl = f"{row.get('event', 'Culto')} · {str(row.get('date', ''))[:10]}"
        out[lbl] = eid
    return out


def _pick_escala_id(options: dict[str, str]) -> str | None:
    if not options:
        return None
    keys = list(options.keys())
    saved = str(st.session_state.get("ml_seq_escala_id", "")).strip()
    default_lbl = keys[0]
    for lbl, eid in options.items():
        if eid == saved:
            default_lbl = lbl
            break
    with st.container(key="ml_seq_pick"):
        pick = st.selectbox("Culto", keys, index=keys.index(default_lbl), key="ml_seq_culto_sel")
    eid = options[pick]
    st.session_state.ml_seq_escala_id = eid
    return eid


def _render_music_card_html(
    *,
    num: int,
    title: str,
    parte: str,
    tom: str,
    active: bool = False,
) -> str:
    border = "1px solid rgba(139,92,246,.35)" if active else "1px solid rgba(255,255,255,.04)"
    return f"""
    <div class="ml-seq-music" style="border:{border};">
      <div style="flex:1;min-width:0;">
        <h3>{_esc(title)}</h3>
        <span>{_esc(parte or "Louvor")}{f' · Tom {_esc(tom)}' if tom and tom != '—' else ''}</span>
      </div>
      <div class="ml-seq-num">{num}</div>
    </div>
    """


def _load_song_bundle(
    *,
    escala_id: str,
    programa_id: str,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
) -> dict[str, Any] | None:
    from app import (
        default_cifra_from_louvor,
        default_lyrics_from_louvor,
        enrich_programa_from_catalog,
        hydrate_escala_sequencia_content,
        integrantes_escalados,
        is_scale_manager,
        load_programa_sequencia_df,
        programa_por_escala,
    )
    from catalog_sanitize import format_louvor_display, sanitize_catalog_text
    from sequencia_culto import (
        get_sequencia_row,
        split_lyrics_paragraphs,
        trechos_banda_from_markup,
        trechos_from_markup,
    )

    prog = programa_por_escala(programa_df, escala_id)
    if prog.empty:
        return None
    if louvores_df is not None and not louvores_df.empty:
        prog = enrich_programa_from_catalog(prog, louvores_df)

    row_match = prog[prog["id"].astype(str) == str(programa_id)]
    if row_match.empty:
        return None
    item = row_match.iloc[0]

    hydrate_escala_sequencia_content(escala_id, programa_df, louvores_df)
    seq_df = load_programa_sequencia_df()

    louvor_t = sanitize_catalog_text(item.get("louvor_title", ""))
    artist_t = sanitize_catalog_text(item.get("artist", ""))
    tom_base = sanitize_catalog_text(item.get("key", "")) or "C"
    seq_row = get_sequencia_row(seq_df, str(programa_id))
    lyrics_default = str(seq_row.get("lyrics_text", "")).strip() or default_lyrics_from_louvor(
        louvores_df, louvor_t, artist_t
    )
    cifra_default = str(seq_row.get("cifra_text", "")).strip() or default_cifra_from_louvor(
        louvores_df, louvor_t, artist_t
    )
    tom_prog = str(seq_row.get("tom_programa", "")).strip() or tom_base
    capo_val = int(pd.to_numeric(seq_row.get("capo", 0), errors="coerce") or 0)
    paragraphs = split_lyrics_paragraphs(lyrics_default)
    trechos_v = trechos_from_markup(str(seq_row.get("lyrics_markup", "")), max(len(paragraphs), 1))
    trechos_b = trechos_banda_from_markup(str(seq_row.get("cifra_markup", "")), max(len(paragraphs), 1))

    todas = escalas_df[escalas_df["id"].astype(str) == str(escala_id)]
    row_esc = todas.iloc[0] if not todas.empty else None
    team = integrantes_escalados(row_esc, equipe_df, members_df) if row_esc is not None else []
    from app import banda_escala, integrantes_marcacao_opts

    vocal_opts = integrantes_marcacao_opts(team)
    banda_opts = banda_escala(team) or integrantes_marcacao_opts(team)
    title, artist = format_louvor_display(item)

    return {
        "item": item,
        "programa_id": str(programa_id),
        "title": title,
        "artist": artist,
        "parte": str(item.get("parte", "")).strip(),
        "tom_base": tom_base,
        "tom_prog": tom_prog,
        "capo_val": capo_val,
        "lyrics_default": lyrics_default,
        "cifra_default": cifra_default,
        "paragraphs": paragraphs,
        "trechos_v": trechos_v,
        "trechos_b": trechos_b,
        "seq_df": seq_df,
        "vocal_opts": vocal_opts,
        "banda_opts": banda_opts,
        "can_edit": is_scale_manager(st.session_state.get("user_roles", "")),
        "louvor_t": louvor_t,
        "artist_t": artist_t,
        "louvores_df": louvores_df,
        "cifra_url": sanitize_catalog_text(item.get("cifra_url", "")),
    }


def _render_lista(
    *,
    escala_id: str,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
) -> None:
    from app import enrich_programa_from_catalog, programa_por_escala
    from catalog_sanitize import format_louvor_display
    from louvor_meta import parse_duracao_min

    prog = programa_por_escala(programa_df, escala_id)
    if louvores_df is not None and not louvores_df.empty:
        prog = enrich_programa_from_catalog(prog, louvores_df)

    _render_page_header("Sequência do Culto", "Ordem das músicas · tom e parte")

    if prog.empty:
        st.info("Programação ainda não montada para este culto.")
        st.caption("Monte em **Gerenciar Escalas → Montar / editar escala**.")
        return

    total_min = 0.0
    for idx, (_, r) in enumerate(prog.iterrows()):
        title, artist = format_louvor_display(r)
        parte = str(r.get("parte", "") or "Louvor").strip()
        tom = str(r.get("key", "") or r.get("tom_programa", "") or "").strip() or "—"
        pid = str(r.get("id", ""))
        st.markdown(
            _render_music_card_html(num=idx + 1, title=title, parte=parte, tom=tom),
            unsafe_allow_html=True,
        )
        with st.container(key=f"ml_seq_song_{pid}"):
            sub = f"{parte} · {_esc(artist)}" if artist else parte
            if st.button(
                f"Abrir · {title}\n{sub}",
                key=f"ml_seq_open_{pid}",
                use_container_width=True,
            ):
                st.session_state.ml_seq_programa_id = pid
                _set_view("musica")
                _set_sub("vocal")
                st.rerun()
        try:
            total_min += float(parse_duracao_min(str(r.get("duration", "") or "")) or 0)
        except Exception:
            pass

    if total_min > 0:
        st.markdown(
            f'<div class="ml-seq-dur">⏱ <b>DURAÇÃO TOTAL:</b> {int(total_min)} min</div>',
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns(2)
    with c1:
        with st.container(key="ml_seq_btn_green"):
            if st.button("📄 Exportar sequência (PDF)", use_container_width=True):
                from mobile_lab import is_mobile_lab_enabled
                from mobile_lab_nav import navigate_ml_page

                if is_mobile_lab_enabled():
                    from mobile_lab_nav import navigate_ml_page

                    navigate_ml_page("Gerenciar Escalas", pin=True)
                else:
                    st.session_state.app_menu = "Gerenciar Escalas"
                st.session_state["_ml_ger_open_tab"] = "pdf"
                st.rerun()
    with c2:
        with st.container(key="ml_seq_btn_wa"):
            if st.button("💬 Enviar para WhatsApp", use_container_width=True):
                from mobile_lab import is_mobile_lab_enabled
                from mobile_lab_nav import navigate_ml_page

                if is_mobile_lab_enabled():
                    from mobile_lab_nav import navigate_ml_page

                    navigate_ml_page("Gerenciar Escalas", pin=True)
                else:
                    st.session_state.app_menu = "Gerenciar Escalas"
                st.session_state["_ml_ger_open_tab"] = "whatsapp"
                st.rerun()
    st.caption("PDF e WhatsApp completos em **Gerenciar Escalas**.")


def _render_vocal(b: dict[str, Any]) -> None:
    from sequencia_culto import build_trechos_vocal_ui

    st.markdown(
        """
        <div class="ml-seq-card">
          <div class="ml-seq-section-title">🎤 Marcação Vocal</div>
          <div class="ml-seq-subtitle">Defina como a voz entrará em cada parte da música.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    paragraphs = b["paragraphs"]
    if not paragraphs:
        st.warning("Letra ainda não carregada — abra **Editar** ou busque na internet.")
        return
    if not b["can_edit"]:
        from sequencia_culto import render_lyrics_annotated_html

        st.markdown(
            render_lyrics_annotated_html(paragraphs, b["trechos_v"], b["trechos_b"]),
            unsafe_allow_html=True,
        )
        st.caption("Somente leitura. Líderes podem editar marcações.")
        return
    trechos_v_new = build_trechos_vocal_ui(
        st,
        paragraphs,
        b["vocal_opts"],
        b["trechos_v"],
        f"mlseqv_{b['programa_id']}",
    )
    _autosave_markups(b, trechos_v_new, b["trechos_b"])


def _render_banda(b: dict[str, Any]) -> None:
    from sequencia_culto import build_trechos_banda_ui

    st.markdown(
        """
        <div class="ml-seq-card">
          <div class="ml-seq-section-title">🎹 Marcação da Banda</div>
          <div class="ml-seq-subtitle">Controle entrada instrumental e dinâmica por estrofe.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    paragraphs = b["paragraphs"]
    if not paragraphs:
        st.warning("Letra ainda não carregada — abra **Editar** ou busque na internet.")
        return
    if not b["can_edit"]:
        st.caption("Somente leitura para integrantes.")
        return
    trechos_b_new = build_trechos_banda_ui(
        st,
        paragraphs,
        b["banda_opts"],
        b["trechos_b"],
        f"mlseqb_{b['programa_id']}",
    )
    _autosave_markups(b, b["trechos_v"], trechos_b_new)
    with st.container(key="ml_seq_btn_danger"):
        if st.button("Limpar marcações da banda", use_container_width=True):
            n = len(paragraphs)
            cleared = [
                {"paragrafo": i, "tipo": "—", "integrantes": [], "nota": ""} for i in range(n)
            ]
            state_key = f"mlseqb_{b['programa_id']}_bstate"
            st.session_state[state_key] = cleared
            _autosave_markups(b, b["trechos_v"], cleared)
            st.rerun()


def _autosave_markups(b: dict[str, Any], trechos_v: list, trechos_b: list) -> None:
    from app import autosave_sequencia_trabalho, save_programa_sequencia_df
    from cifra_fetch import normalize_cifra_text

    seq_df = b["seq_df"]
    seq_df, saved = autosave_sequencia_trabalho(
        seq_df,
        b["programa_id"],
        lyrics_text=b["lyrics_default"],
        cifra_text=normalize_cifra_text(b["cifra_default"]),
        trechos_v=trechos_v,
        trechos_b=trechos_b,
        tom_programa=str(b["tom_prog"]),
        capo=int(b["capo_val"]),
    )
    if saved:
        save_programa_sequencia_df(seq_df)


def _render_cifra(b: dict[str, Any]) -> None:
    from sequencia_culto import (
        display_cifra_transposed,
        effective_tom,
        render_cifra_direcoes_html,
        render_cifra_html,
    )

    tom_show = b["tom_prog"]
    capo_show = b["capo_val"]
    cifra_show = display_cifra_transposed(b["cifra_default"], b["tom_base"], tom_show) or b["cifra_default"]
    eff = effective_tom(b["tom_base"], tom_show)

    st.markdown(
        f"""
        <div class="ml-seq-card">
          <div class="ml-seq-section-title">🎸 Cifra</div>
          <div class="ml-seq-subtitle">Tom do culto: <b style="color:#facc15;">{_esc(tom_show or eff)}</b>
          {f' · Capo {capo_show}ª' if capo_show else ''}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    direcoes = render_cifra_direcoes_html(b["paragraphs"], b["trechos_v"], b["trechos_b"])
    if direcoes:
        st.markdown(direcoes, unsafe_allow_html=True)
    if cifra_show:
        st.markdown(
            f'<div class="ml-seq-cifra-box">{render_cifra_html(cifra_show, eff, capo_show)}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Cifra indisponível. Use **Editar** para buscar ou colar.")


def _render_editar(b: dict[str, Any]) -> None:
    from app import TOM_OPCOES, save_programa_sequencia_df, upsert_sequencia_row
    from cifra_fetch import normalize_cifra_text
    from louvor_content import apply_content_to_louvores_df, ensure_sequencia_louvor_content
    from sequencia_culto import (
        build_trechos_banda_ui,
        build_trechos_vocal_ui,
        display_cifra_transposed,
        markup_to_json,
        render_cifra_html,
        split_lyrics_paragraphs,
    )

    st.markdown(
        """
        <div class="ml-seq-card">
          <div class="ml-seq-section-title">✏️ Edição completa</div>
          <div class="ml-seq-subtitle">Tom, capotraste, letra e cifra — salve na sequência do culto.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not b["can_edit"]:
        st.warning("Edição restrita à liderança do ministério.")
        return

    pid = b["programa_id"]
    seq_df = b["seq_df"]
    tom_base = b["tom_base"]
    idx_tom = list(TOM_OPCOES).index(b["tom_prog"]) if b["tom_prog"] in TOM_OPCOES else 0

    if st.button("🔄 Atualizar letra/cifra da internet", key=f"ml_seq_fetch_{pid}"):
        with st.spinner("Buscando…"):
            seq_df, louvores_df, msg, _web = ensure_sequencia_louvor_content(
                seq_df,
                pid,
                b["louvor_t"],
                b["artist_t"],
                b["cifra_url"],
                tom_base,
                b["louvores_df"],
                use_web=True,
                save_to_catalog=True,
                force_web_refresh=True,
            )
            if _web:
                from app import LOUVORES_FILE, save_data

                save_programa_sequencia_df(seq_df)
                save_data(louvores_df, LOUVORES_FILE)
                st.success(msg or "Atualizado.")
                st.rerun()
            else:
                st.warning(msg or "Não foi possível buscar.")

    c1, c2 = st.columns(2)
    with c1:
        tom_view = st.selectbox("Tom do culto", TOM_OPCOES, index=idx_tom, key=f"ml_seq_tom_{pid}")
    with c2:
        capo_view = st.number_input(
            "Capotraste",
            min_value=0,
            max_value=11,
            value=b["capo_val"],
            key=f"ml_seq_capo_{pid}",
        )
    st.caption(f"Tom no repertório: **{tom_base or '—'}**")

    lyrics_edit = st.text_area(
        "Letra completa",
        value=b["lyrics_default"],
        height=160,
        key=f"ml_seq_ly_{pid}",
    )
    paragraphs = split_lyrics_paragraphs(lyrics_edit)
    trechos_v = b["trechos_v"]
    trechos_b = b["trechos_b"]
    if paragraphs:
        with st.expander("🎤 Marcações vocais", expanded=True):
            trechos_v = build_trechos_vocal_ui(
                st, paragraphs, b["vocal_opts"], trechos_v, f"mlseqe_v_{pid}"
            )
        with st.expander("🎹 Marcações da banda", expanded=False):
            trechos_b = build_trechos_banda_ui(
                st, paragraphs, b["banda_opts"], trechos_b, f"mlseqe_b_{pid}"
            )

    cifra_edit = st.text_area(
        "Cifra (texto)",
        value=b["cifra_default"],
        height=200,
        key=f"ml_seq_cf_{pid}",
    )
    cifra_prev = display_cifra_transposed(cifra_edit, tom_base, str(tom_view))
    if cifra_prev:
        st.markdown(
            f'<div class="ml-seq-cifra-box">{render_cifra_html(cifra_prev, str(tom_view), int(capo_view))}</div>',
            unsafe_allow_html=True,
        )

    salvar_rep = st.checkbox(
        "Salvar letra e cifra no **Repertório**",
        value=True,
        key=f"ml_seq_rep_{pid}",
    )
    with st.container(key="ml_seq_btn_primary"):
        if st.button("💾 Salvar alterações", type="primary", use_container_width=True):
            from app import LOUVORES_FILE, save_data

            cifra_save = normalize_cifra_text(cifra_edit)
            seq_df = upsert_sequencia_row(
                seq_df,
                pid,
                lyrics_text=lyrics_edit.strip(),
                lyrics_markup=markup_to_json(trechos_v),
                cifra_text=cifra_save,
                tom_programa=str(tom_view),
                capo=int(capo_view),
                cifra_markup=markup_to_json(trechos_b),
            )
            save_programa_sequencia_df(seq_df)
            if salvar_rep and b["louvor_t"]:
                louvores_df = apply_content_to_louvores_df(
                    b["louvores_df"],
                    b["louvor_t"],
                    b["artist_t"],
                    lyrics_edit,
                    cifra_save,
                    source_tag="sequencia_culto",
                )
                save_data(louvores_df, LOUVORES_FILE)
            st.success("Sequência salva.")
            st.rerun()


def _render_musica(
    *,
    escala_id: str,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
) -> None:
    pid = str(st.session_state.get("ml_seq_programa_id", "")).strip()
    if not pid:
        _set_view("lista")
        return

    b = _load_song_bundle(
        escala_id=escala_id,
        programa_id=pid,
        programa_df=programa_df,
        louvores_df=louvores_df,
        equipe_df=equipe_df,
        members_df=members_df,
        escalas_df=escalas_df,
    )
    if not b:
        st.warning("Música não encontrada.")
        if st.button("Voltar à lista"):
            _set_view("lista")
            st.rerun()
        return

    with st.container(key="ml_seq_back"):
        if st.button("← Voltar à sequência", use_container_width=True):
            _set_view("lista")
            _set_sub("lista")
            st.rerun()

    sub = _sub()
    if sub == "lista":
        sub = "vocal"
    _render_page_header(
        str(b["title"]),
        f"{b['artist']} · {b['parte'] or 'Louvor'}",
    )
    _render_sub_tabs(sub, can_edit=b["can_edit"])

    if sub == "vocal":
        _render_vocal(b)
    elif sub == "banda":
        _render_banda(b)
    elif sub == "cifra":
        _render_cifra(b)
    elif sub == "editar":
        _render_editar(b)


def render_mobile_sequencia_tab(
    *,
    minhas: list[dict],
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    escalas_df: pd.DataFrame | None = None,
    equipe_df: pd.DataFrame | None = None,
    members_df: pd.DataFrame | None = None,
    all_escalas: bool = False,
) -> None:
    """Aba Sequência (Escalas mobile) ou página completa (Gerenciar)."""
    inject_mobile_lab_theme()
    st.markdown(
        f'<span id="ml-sequencia-page" aria-hidden="true"></span>'
        f"<style>{mobile_sequencia_css()}</style>",
        unsafe_allow_html=True,
    )

    escalas_df = escalas_df if escalas_df is not None else pd.DataFrame()
    equipe_df = equipe_df if equipe_df is not None else pd.DataFrame()
    members_df = members_df if members_df is not None else pd.DataFrame()

    options = _culto_options(minhas=minhas, escalas_df=escalas_df, all_escalas=all_escalas)
    if not options:
        if all_escalas:
            st.info("Nenhuma escala cadastrada ainda.")
        else:
            st.markdown(
                """
                <div class="ml-seq-card">
                  <div class="ml-seq-section-title">🎵 Sequência do culto</div>
                  <div class="ml-seq-subtitle">
                    Você não está escalado nesta semana. Quando estiver, a sequência do culto aparece aqui.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    escala_id = _pick_escala_id(options)
    if not escala_id:
        return

    if _view() == "musica":
        _render_musica(
            escala_id=escala_id,
            programa_df=programa_df,
            louvores_df=louvores_df,
            equipe_df=equipe_df,
            members_df=members_df,
            escalas_df=escalas_df,
        )
    else:
        _render_lista(
            escala_id=escala_id,
            programa_df=programa_df,
            louvores_df=louvores_df,
            escalas_df=escalas_df,
        )


def render_mobile_sequencia_page(
    *,
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    escala_id_pref: str | None = None,
) -> None:
    """Substitui show_sequencia_culto_page no Mobile Lab (todos os cultos)."""
    if escala_id_pref:
        st.session_state.ml_seq_escala_id = str(escala_id_pref)
    render_mobile_sequencia_tab(
        minhas=[],
        programa_df=programa_df,
        louvores_df=louvores_df,
        escalas_df=escalas_df,
        equipe_df=equipe_df,
        members_df=members_df,
        all_escalas=True,
    )
