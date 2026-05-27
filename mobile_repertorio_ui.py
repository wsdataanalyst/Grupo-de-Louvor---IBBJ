"""Mobile Lab — página Repertório premium (layout conforme mock HTML)."""

from __future__ import annotations

import html
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from link_finder import is_direct_url
from louvor_content import ensure_louvor_content_columns
from louvor_meta import LOUVOR_THEMES, themes_from_csv
from mobile_lab_ui import inject_mobile_lab_theme
from repertorio_ui import (
    category_counts,
    compute_repertorio_stats,
    count_added_this_month,
    top_louvores_usage,
)

LIST_TABS: tuple[tuple[str, str], ...] = (
    ("todas", "Todas"),
    ("favoritas", "Favoritas"),
    ("cifra", "Com cifra"),
    ("youtube", "Com YouTube"),
)

QUICK_ACTIONS: tuple[tuple[str, str, str, str], ...] = (
    ("filtros", "🔽", "Filtros", "rgba(124,58,237,.22)"),
    ("tags", "🏷", "Tags", "rgba(59,130,246,.18)"),
    ("favoritos", "❤", "Favoritos", "rgba(239,68,68,.16)"),
    ("novas", "✨", "Novas", "rgba(249,115,22,.16)"),
)


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _view() -> str:
    v = str(st.session_state.get("ml_rep_view", "hub")).strip()
    return v if v in ("hub", "lista", "detalhe", "categorias", "ferramentas") else "hub"


def _set_view(view: str) -> None:
    st.session_state.ml_rep_view = view


def _list_tab() -> str:
    t = str(st.session_state.get("ml_rep_list_tab", "todas")).strip()
    return t if t in {k for k, _ in LIST_TABS} else "todas"


def mobile_repertorio_css() -> str:
    return r"""
    body:has(#ml-repertorio-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_add"] .stButton > button{
      width: 100% !important;
      min-height: 3.1rem !important;
      border-radius: 22px !important;
      font-weight: 800 !important;
      font-size: 1rem !important;
      color: #0f172a !important;
      background: linear-gradient(135deg, #facc15, #eab308) !important;
      border: none !important;
      box-shadow: 0 0 32px rgba(250,204,21,.22) !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_filter_"] .stSelectbox > div > div,
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_search"] .stTextInput > div > div > input{
      min-height: 3rem !important;
      border-radius: 22px !important;
      background: rgba(30,30,30,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #fff !important;
      font-size: 0.95rem !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_quick_"] .stButton > button{
      min-height: 4.6rem !important;
      border-radius: 22px !important;
      font-weight: 800 !important;
      font-size: 0.82rem !important;
      white-space: pre-line !important;
      line-height: 1.2 !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      box-shadow: 0 0 20px rgba(124,58,237,.08) !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_quick_"] .stButton > button p{
      margin-top: 0.35rem !important;
      font-size: 0.78rem !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_cat_"] .stButton > button,
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_song_"] .stButton > button{
      width: 100% !important;
      text-align: left !important;
      justify-content: flex-start !important;
      min-height: 3.6rem !important;
      border-radius: 20px !important;
      background: rgba(7,18,45,.85) !important;
      border: 1px solid rgba(255,255,255,.06) !important;
      color: rgba(226,232,240,.96) !important;
      padding: 0.75rem 0.9rem !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_song_"] .stButton > button p{
      margin: 0 !important;
      white-space: normal !important;
      text-align: left !important;
      font-size: 0.82rem !important;
      line-height: 1.3 !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_list_tab_"] .stButton > button{
      border-radius: 16px !important;
      min-height: 2.4rem !important;
      font-weight: 700 !important;
      font-size: 0.78rem !important;
      white-space: nowrap !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(148,163,184,.95) !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_list_tab_"] .stButton > button[kind="primary"]{
      background: rgba(124,58,237,1) !important;
      color: #fff !important;
      box-shadow: 0 0 18px rgba(139,92,246,.25) !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_back"] .stButton > button,
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_tool_"] .stButton > button{
      border-radius: 18px !important;
      font-weight: 700 !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_apply"] .stButton > button[kind="primary"]{
      width: 100% !important;
      min-height: 3rem !important;
      border-radius: 22px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
      border: none !important;
      box-shadow: 0 0 28px rgba(124,58,237,.28) !important;
    }
    .ml-rep-header-card{
      background: rgba(12,18,40,.78);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 28px;
      padding: 1.25rem 1.1rem 1.1rem;
      position: relative;
      overflow: hidden;
      backdrop-filter: blur(14px);
      box-shadow: 0 0 40px rgba(88,28,135,.12), inset 0 0 0 1px rgba(255,255,255,.02);
      margin-bottom: 0.85rem;
    }
    .ml-rep-header-card::before{
      content:'';
      position:absolute;
      width:160px;height:160px;
      background:radial-gradient(circle, rgba(124,58,237,.28) 0%, transparent 70%);
      top:-70px;right:-70px;
      pointer-events:none;
    }
    .ml-rep-header-icon{
      width:56px;height:56px;border-radius:18px;
      background:linear-gradient(135deg,#7c3aed,#5b21b6);
      display:flex;align-items:center;justify-content:center;
      font-size:1.6rem;margin-bottom:0.85rem;
      box-shadow:0 0 28px rgba(124,58,237,.32);
    }
    .ml-rep-header-title{
      font-size:1.65rem;font-weight:800;line-height:1.05;margin:0 0 0.35rem;
      letter-spacing:-0.02em;
    }
    .ml-rep-header-sub{color:rgba(161,161,170,.95);font-size:0.92rem;line-height:1.35;}
    .ml-rep-info{
      margin-top:0.85rem;
      background:rgba(10,16,38,.88);
      border-radius:24px;
      padding:1rem;
      border:1px solid rgba(96,165,250,.2);
    }
    .ml-rep-stat{
      background:rgba(11,18,44,.92);
      border-radius:24px;
      padding:1rem 1.05rem;
      border:1px solid rgba(255,255,255,.05);
      position:relative;
      overflow:hidden;
      margin-bottom:0.65rem;
    }
    .ml-rep-stat::after{
      content:'';position:absolute;width:90px;height:90px;border-radius:50%;
      background:rgba(124,58,237,.08);right:-24px;bottom:-24px;
    }
    .ml-rep-stat-num{font-size:2rem;font-weight:800;line-height:1;}
    .ml-rep-stat-lbl{margin-top:0.35rem;color:#d4d4d8;font-weight:600;font-size:0.9rem;}
    .ml-rep-stat-sub{margin-top:0.25rem;color:#22c55e;font-size:0.82rem;}
    .ml-rep-section-title{
      margin:1rem 0 0.65rem;
      font-size:1.15rem;font-weight:800;letter-spacing:-0.02em;
    }
    .ml-rep-cat-card{
      background:rgba(7,18,45,.9);
      border-radius:24px;
      padding:0.35rem 0.9rem;
      border:1px solid rgba(255,255,255,.05);
    }
    .ml-rep-song-meta{color:rgba(148,163,184,.92);font-size:0.76rem;margin-top:2px;}
    .ml-rep-detail-hero{
      border-radius:28px;
      padding:1.1rem;
      margin-bottom:0.85rem;
      background:linear-gradient(180deg, rgba(124,58,237,.25), rgba(15,23,42,.9));
      border:1px solid rgba(255,255,255,.08);
    }
    .ml-rep-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:0.65rem;}
    .ml-rep-chip{
      display:inline-block;padding:6px 12px;border-radius:14px;
      background:rgba(124,58,237,.18);border:1px solid rgba(139,92,246,.28);
      font-size:0.72rem;font-weight:700;color:rgba(196,181,253,.98);
    }
    .ml-rep-grid4{
      display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:0.85rem 0;
    }
    .ml-rep-mini{
      border-radius:16px;padding:10px 6px;text-align:center;
      background:rgba(15,23,42,.72);border:1px solid rgba(255,255,255,.08);
    }
    .ml-rep-mini b{display:block;font-size:0.95rem;}
    .ml-rep-mini span{font-size:0.68rem;color:rgba(148,163,184,.92);}
    """


def _fav_titles(playlist_df: pd.DataFrame | None, email: str) -> set[str]:
    if playlist_df is None or playlist_df.empty or not email:
        return set()
    from app import playlist_for_user

    mine = playlist_for_user(playlist_df, email)
    return {
        str(t).strip().lower()
        for t in mine.get("title", pd.Series(dtype=str)).astype(str)
    }


def _recent_titles(sugestoes_df: pd.DataFrame | None, *, days: int = 30) -> set[str]:
    if sugestoes_df is None or sugestoes_df.empty:
        return set()
    cutoff = datetime.now() - timedelta(days=days)
    out: set[str] = set()
    for _, row in sugestoes_df.iterrows():
        st_status = str(row.get("status", "")).lower()
        if "aprov" not in st_status:
            continue
        created = str(row.get("created_at", ""))
        try:
            dt = pd.to_datetime(created)
            if pd.notna(dt) and dt.to_pydatetime() >= cutoff:
                title = str(row.get("title", "")).strip().lower()
                if title:
                    out.add(title)
        except (ValueError, TypeError):
            pass
    return out


def _has_cifra(row) -> bool:
    if is_direct_url(str(row.get("cifra_url", ""))):
        return True
    return bool(str(row.get("cifra_text", "")).strip())


def _has_yt(row) -> bool:
    return is_direct_url(str(row.get("youtube_url", "")))


def _filter_df(
    louvores_df: pd.DataFrame,
    *,
    search: str,
    letter: str,
    tom: str,
    ritmo: str,
    temas: list[str],
    tags: list[str],
    apenas_fav: bool,
    fav_titles: set[str],
    novas_only: bool,
    recent_titles: set[str],
    list_tab: str,
) -> pd.DataFrame:
    filtered = louvores_df.copy()
    if search.strip():
        term = search.strip().lower()
        mask = (
            filtered["title"].astype(str).str.lower().str.contains(term, na=False)
            | filtered["artist"].astype(str).str.lower().str.contains(term, na=False)
        )
        filtered = filtered[mask]
    if letter != "Todas":
        filtered = filtered[filtered["letter"].astype(str) == letter]
    if tom != "Todos":
        filtered = filtered[filtered["key"].astype(str) == tom]
    if ritmo != "Todos":
        filtered = filtered[filtered["ritmo"].astype(str) == ritmo]

    def _match_themes(row, tag_list: list[str]) -> bool:
        if not tag_list:
            return True
        ts = themes_from_csv(str(row.get("temas", "")))
        return any(t in ts for t in tag_list)

    if temas:
        filtered = filtered[filtered.apply(lambda r: _match_themes(r, temas), axis=1)]
    if tags:
        filtered = filtered[filtered.apply(lambda r: _match_themes(r, tags), axis=1)]
    if apenas_fav:
        if fav_titles:
            filtered = filtered[
                filtered["title"].astype(str).str.strip().str.lower().isin(fav_titles)
            ]
        else:
            filtered = filtered.iloc[0:0]
    if novas_only and recent_titles:
        filtered = filtered[
            filtered["title"].astype(str).str.strip().str.lower().isin(recent_titles)
        ]
    elif novas_only:
        filtered = filtered.iloc[0:0]

    if list_tab == "favoritas":
        if fav_titles:
            filtered = filtered[
                filtered["title"].astype(str).str.strip().str.lower().isin(fav_titles)
            ]
        else:
            filtered = filtered.iloc[0:0]
    elif list_tab == "cifra":
        filtered = filtered[filtered.apply(_has_cifra, axis=1)]
    elif list_tab == "youtube":
        filtered = filtered[filtered.apply(_has_yt, axis=1)]
    return filtered


def _render_back(label: str = "← Voltar") -> None:
    with st.container(key="ml_rep_back"):
        if st.button(label, use_container_width=True):
            prev = str(st.session_state.pop("ml_rep_back_to", "hub"))
            _set_view(prev)
            st.rerun()


def _render_header_card() -> None:
    st.markdown(
        """
        <div id="ml-repertorio-page" class="ml-page">
          <div class="ml-rep-header-card">
            <div class="ml-rep-header-icon" aria-hidden="true">♫</div>
            <h1 class="ml-rep-header-title">Repertório de Louvores</h1>
            <p class="ml-rep-header-sub">Ministério • Todas as músicas do ministério</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_info_card() -> None:
    st.markdown(
        """
        <div class="ml-rep-info">
          <div style="display:flex;gap:14px;align-items:flex-start;">
            <div style="width:48px;height:48px;border-radius:16px;background:rgba(96,165,250,.12);
              display:flex;align-items:center;justify-content:center;color:#60a5fa;font-size:1.2rem;">ⓘ</div>
            <div>
              <div style="font-size:0.9rem;line-height:1.45;font-weight:600;color:rgba(226,232,240,.96);">
                Navegue pelo repertório com busca, filtros inteligentes e validação bíblica.
              </div>
              <div style="color:#60a5fa;font-weight:700;margin-top:8px;font-size:0.82rem;">
                Saiba mais sobre o Kit Voz →
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_stats(stats: dict, added_month: int) -> None:
    month_txt = f"+{added_month} este mês" if added_month else "Acervo local"
    st.markdown(
        f"""
        <div class="ml-rep-stat">
          <div style="font-size:1.35rem;margin-bottom:0.35rem;">♫</div>
          <div class="ml-rep-stat-num">{stats['total']}</div>
          <div class="ml-rep-stat-lbl">músicas cadastradas</div>
          <div class="ml-rep-stat-sub">{_esc(month_txt)}</div>
        </div>
        <div class="ml-rep-stat">
          <div style="font-size:1.35rem;margin-bottom:0.35rem;">📄</div>
          <div class="ml-rep-stat-num">{stats['cifra']}</div>
          <div class="ml-rep-stat-lbl">com cifra</div>
        </div>
        <div class="ml-rep-stat">
          <div style="font-size:1.35rem;margin-bottom:0.35rem;">▶</div>
          <div class="ml-rep-stat-num">{stats['youtube']}</div>
          <div class="ml-rep-stat-lbl">com YouTube</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_quick_actions() -> None:
    cols = st.columns(4, gap="small")
    for col, (key, icon, label, bg) in zip(cols, QUICK_ACTIONS):
        with col:
            with st.container(key=f"ml_rep_quick_{key}"):
                if st.button(f"{icon}\n{label}", key=f"ml_rep_quick_btn_{key}"):
                    if key == "filtros":
                        st.session_state.ml_rep_show_filters = True
                    elif key == "tags":
                        st.session_state.ml_rep_show_tags = True
                    elif key == "favoritos":
                        st.session_state.ml_rep_f_fav = True
                        _set_view("lista")
                        st.session_state.ml_rep_list_tab = "favoritas"
                    elif key == "novas":
                        st.session_state.ml_rep_novas = True
                        _set_view("lista")
                    st.rerun()


def _render_filters_ui(louvores_df: pd.DataFrame) -> tuple[str, str, str, str, list[str], list[str], bool]:
    letters = sorted(
        {letter for letter in louvores_df["letter"].dropna().astype(str) if letter}
    )
    ritmos = sorted(
        {ritmo for ritmo in louvores_df["ritmo"].dropna().astype(str) if ritmo.strip()}
    )
    toms = sorted(
        {str(t).strip() for t in louvores_df["key"].dropna().astype(str) if str(t).strip()}
    )
    st.markdown('<div class="ml-rep-section-title">Buscar</div>', unsafe_allow_html=True)
    search = st.text_input(
        "Buscar música ou artista",
        key="ml_rep_search",
        placeholder="Buscar música ou artista...",
        label_visibility="collapsed",
    )
    show = st.session_state.get("ml_rep_show_filters", True)
    if show:
        st.markdown('<div class="ml-rep-section-title">Filtros</div>', unsafe_allow_html=True)
        with st.container(key="ml_rep_filter_letter"):
            letter = st.selectbox("Letra", ["Todas"] + letters, key="ml_rep_f_letter")
        with st.container(key="ml_rep_filter_tom"):
            tom = st.selectbox("Tom", ["Todos"] + toms, key="ml_rep_f_tom")
        with st.container(key="ml_rep_filter_ritmo"):
            ritmo = st.selectbox("Ritmo", ["Todos"] + ritmos, key="ml_rep_f_ritmo")
        with st.container(key="ml_rep_filter_tema"):
            temas = st.multiselect(
                "Tema",
                list(LOUVOR_THEMES),
                key="ml_rep_f_tema",
                placeholder="Todos",
            )
        if st.session_state.get("ml_rep_show_tags"):
            tags = st.multiselect(
                "Tag bíblica",
                list(LOUVOR_THEMES),
                key="ml_rep_f_tag",
                placeholder="Filtrar por tag",
            )
        else:
            tags = st.session_state.get("ml_rep_f_tag", [])
        apenas_fav = st.toggle("⭐ Apenas favoritas", key="ml_rep_f_fav")
        c1, c2 = st.columns(2)
        with c1:
            with st.container(key="ml_rep_apply"):
                if st.button("Aplicar filtros", type="primary", use_container_width=True):
                    _set_view("lista")
                    st.rerun()
        with c2:
            if st.button("Limpar filtros", use_container_width=True, key="ml_rep_clear"):
                for k in (
                    "ml_rep_search",
                    "ml_rep_f_letter",
                    "ml_rep_f_tom",
                    "ml_rep_f_ritmo",
                    "ml_rep_f_tema",
                    "ml_rep_f_tag",
                    "ml_rep_f_fav",
                    "ml_rep_novas",
                ):
                    st.session_state.pop(k, None)
                st.session_state.ml_rep_show_tags = False
                st.rerun()
    else:
        letter = str(st.session_state.get("ml_rep_f_letter", "Todas"))
        tom = str(st.session_state.get("ml_rep_f_tom", "Todos"))
        ritmo = str(st.session_state.get("ml_rep_f_ritmo", "Todos"))
        temas = st.session_state.get("ml_rep_f_tema", [])
        tags = st.session_state.get("ml_rep_f_tag", [])
        apenas_fav = bool(st.session_state.get("ml_rep_f_fav", False))
    return search, letter, tom, ritmo, temas, tags, apenas_fav


def _song_button_label(title: str, artist: str, key: str, ritmo: str, bpm: str) -> str:
    meta = " · ".join(x for x in (key, ritmo, bpm) if x and x != "—")
    return f"**{title}**\n{artist}\n{meta}" if meta else f"**{title}**\n{artist}"


def _open_song(title: str) -> None:
    st.session_state.ml_rep_selected_title = title
    st.session_state.ml_rep_back_to = _view()
    _set_view("detalhe")


def _render_song_list(
    df: pd.DataFrame,
    *,
    key_prefix: str,
    limit: int | None = None,
) -> None:
    from catalog_sanitize import sanitize_catalog_text

    show = df.head(limit) if limit else df
    if show.empty:
        st.info("Nenhuma música encontrada.")
        return
    for i, (_, row) in enumerate(show.iterrows()):
        title = sanitize_catalog_text(str(row.get("title", "")))
        artist = sanitize_catalog_text(str(row.get("artist", "")))
        tom = sanitize_catalog_text(str(row.get("key", ""))) or "—"
        ritmo = sanitize_catalog_text(str(row.get("ritmo", ""))) or "—"
        bpm = sanitize_catalog_text(str(row.get("duracao_min", ""))) or "—"
        label = _song_button_label(title, artist, tom, ritmo, bpm)
        with st.container(key=f"ml_rep_song_{key_prefix}_{i}"):
            if st.button(label, key=f"ml_rep_song_btn_{key_prefix}_{i}"):
                _open_song(title)
                st.rerun()


def _render_categories_preview(louvores_df: pd.DataFrame) -> None:
    cats = category_counts(louvores_df, limit=6)
    st.markdown('<div class="ml-rep-section-title">Categorias</div>', unsafe_allow_html=True)
    st.markdown('<div class="ml-rep-cat-card">', unsafe_allow_html=True)
    for i, (name, n) in enumerate(cats):
        with st.container(key=f"ml_rep_cat_{i}"):
            if st.button(f"{name}  ·  {n} músicas", key=f"ml_rep_cat_btn_{i}"):
                st.session_state.ml_rep_f_tema = [name]
                st.session_state.ml_rep_back_to = "hub"
                _set_view("lista")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Ver todas as categorias", key="ml_rep_all_cats", use_container_width=True):
        st.session_state.ml_rep_back_to = "hub"
        _set_view("categorias")
        st.rerun()


def _render_top_used(louvores_df: pd.DataFrame, programa_df: pd.DataFrame) -> None:
    ranking = top_louvores_usage(programa_df, limit=8)
    if not ranking:
        return
    st.markdown('<div class="ml-rep-section-title">Mais utilizadas</div>', unsafe_allow_html=True)
    title_to_row: dict[str, pd.Series] = {}
    for _, row in louvores_df.iterrows():
        t = str(row.get("title", "")).strip().lower()
        if t:
            title_to_row[t] = row
    rows = []
    for title, cnt in ranking:
        key = title.strip().lower()
        if key in title_to_row:
            rows.append(title_to_row[key])
    if rows:
        _render_song_list(pd.DataFrame(rows), key_prefix="top", limit=5)


def _render_hub(
    louvores_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    sugestoes_df: pd.DataFrame | None,
    playlist_df: pd.DataFrame | None,
    *,
    is_mgr: bool,
) -> None:
    _render_header_card()
    with st.container(key="ml_rep_add"):
        if st.button("+ Adicionar música", use_container_width=True):
            st.session_state["rep_add_open"] = True
            st.rerun()

    if st.session_state.get("rep_add_open"):
        with st.expander("➕ Adicionar música ao repertório", expanded=True):
            if is_mgr:
                from app import _render_louvores_edit_manager

                _render_louvores_edit_manager(louvores_df)
            else:
                st.info(
                    "Envie sugestões em **Sugestão de louvor** — a liderança analisa e "
                    "inclui no repertório."
                )
                if st.button("Ir para Sugestão de louvor", key="ml_rep_go_sugestao"):
                    st.session_state.ml_page = "Sugestões"
                    st.session_state.pop("rep_add_open", None)
                    st.rerun()

    _render_info_card()
    from app import render_voice_kit_link

    render_voice_kit_link()

    stats = compute_repertorio_stats(louvores_df)
    added_month = count_added_this_month(sugestoes_df)
    _render_stats(stats, added_month)
    _render_quick_actions()

    if louvores_df.empty:
        st.warning("Repertório ainda não gerado. Execute: `python build_louvores_db.py`")
        return

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    fav = _fav_titles(playlist_df, my_email)
    recent = _recent_titles(sugestoes_df)

    search, letter, tom, ritmo, temas, tags, apenas_fav = _render_filters_ui(louvores_df)
    novas = bool(st.session_state.get("ml_rep_novas", False))

    filtered = _filter_df(
        louvores_df,
        search=search,
        letter=letter,
        tom=tom,
        ritmo=ritmo,
        temas=temas,
        tags=tags,
        apenas_fav=apenas_fav,
        fav_titles=fav,
        novas_only=novas,
        recent_titles=recent,
        list_tab="todas",
    )

    _render_top_used(louvores_df, programa_df)
    _render_categories_preview(louvores_df)

    st.markdown(
        f'<div class="ml-rep-section-title">Resultados ({len(filtered)})</div>',
        unsafe_allow_html=True,
    )
    if st.button(f"Ver todas as músicas ({len(louvores_df)})", key="ml_rep_ver_todas"):
        st.session_state.ml_rep_back_to = "hub"
        _set_view("lista")
        st.rerun()
    _render_song_list(filtered, key_prefix="hub", limit=12)

    if is_mgr:
        st.markdown('<div class="ml-rep-section-title">Ferramentas</div>', unsafe_allow_html=True)
        if st.button("Abrir ferramentas do repertório", key="ml_rep_open_tools"):
            st.session_state.ml_rep_back_to = "hub"
            _set_view("ferramentas")
            st.rerun()


def _render_lista(
    louvores_df: pd.DataFrame,
    sugestoes_df: pd.DataFrame | None,
    playlist_df: pd.DataFrame | None,
) -> None:
    _render_back()
    st.markdown(
        """
        <div class="ml-page">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <h2 style="margin:0;font-size:1.35rem;font-weight:800;">Todas as músicas</h2>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tab = _list_tab()
    cols = st.columns(len(LIST_TABS), gap="small")
    for col, (key, label) in zip(cols, LIST_TABS):
        with col:
            with st.container(key=f"ml_rep_list_tab_{key}"):
                if st.button(
                    label,
                    key=f"ml_rep_list_tab_btn_{key}",
                    type="primary" if tab == key else "secondary",
                ):
                    st.session_state.ml_rep_list_tab = key
                    st.rerun()

    search = str(st.session_state.get("ml_rep_search", ""))
    letter = str(st.session_state.get("ml_rep_f_letter", "Todas"))
    tom = str(st.session_state.get("ml_rep_f_tom", "Todos"))
    ritmo = str(st.session_state.get("ml_rep_f_ritmo", "Todos"))
    temas = st.session_state.get("ml_rep_f_tema", [])
    tags = st.session_state.get("ml_rep_f_tag", [])
    apenas_fav = bool(st.session_state.get("ml_rep_f_fav", False))
    novas = bool(st.session_state.get("ml_rep_novas", False))

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    fav = _fav_titles(playlist_df, my_email)
    recent = _recent_titles(sugestoes_df)

    filtered = _filter_df(
        louvores_df,
        search=search,
        letter=letter,
        tom=tom,
        ritmo=ritmo,
        temas=temas,
        tags=tags,
        apenas_fav=apenas_fav,
        fav_titles=fav,
        novas_only=novas,
        recent_titles=recent,
        list_tab=tab,
    )
    st.caption(f"{len(filtered)} músicas · repertório com {len(louvores_df)} louvores")
    _render_song_list(filtered, key_prefix="lista", limit=50)


def _render_categorias(louvores_df: pd.DataFrame) -> None:
    _render_back()
    st.markdown(
        '<div class="ml-rep-section-title" style="margin-top:0;">Categorias</div>',
        unsafe_allow_html=True,
    )
    cats = category_counts(louvores_df, limit=50)
    for i, (name, n) in enumerate(cats):
        with st.container(key=f"ml_rep_cat_full_{i}"):
            if st.button(f"{name}  ·  {n} músicas", key=f"ml_rep_cat_full_btn_{i}"):
                st.session_state.ml_rep_f_tema = [name]
                st.session_state.ml_rep_back_to = "categorias"
                _set_view("lista")
                st.rerun()


def _render_detalhe(louvores_df: pd.DataFrame, playlist_df: pd.DataFrame | None) -> None:
    from catalog_sanitize import sanitize_catalog_text

    _render_back()
    title_key = str(st.session_state.get("ml_rep_selected_title", "")).strip()
    if not title_key:
        _set_view("hub")
        st.rerun()
        return
    match = louvores_df[
        louvores_df["title"].astype(str).str.strip().str.lower() == title_key.lower()
    ]
    if match.empty:
        st.warning("Música não encontrada.")
        return
    row = match.iloc[0]
    title = sanitize_catalog_text(str(row.get("title", "")))
    artist = sanitize_catalog_text(str(row.get("artist", "")))
    tom = sanitize_catalog_text(str(row.get("key", ""))) or "—"
    ritmo = sanitize_catalog_text(str(row.get("ritmo", ""))) or "—"
    bpm = sanitize_catalog_text(str(row.get("duracao_min", ""))) or "—"
    compasso = sanitize_catalog_text(str(row.get("compasso", ""))) or "4/4"
    temas = themes_from_csv(str(row.get("temas", "")))
    yt = str(row.get("youtube_url", "")).strip()
    cifra_url = str(row.get("cifra_url", "")).strip()

    st.markdown(
        f"""
        <div class="ml-rep-detail-hero">
          <div style="font-size:0.78rem;color:rgba(148,163,184,.92);margin-bottom:6px;">Detalhes</div>
          <h2 style="margin:0;font-size:1.45rem;font-weight:900;">{_esc(title)}</h2>
          <p style="margin:6px 0 0;color:rgba(148,163,184,.95);font-size:0.92rem;">{_esc(artist)}</p>
        </div>
        <div class="ml-rep-grid4">
          <div class="ml-rep-mini"><b>{_esc(tom)}</b><span>Tom</span></div>
          <div class="ml-rep-mini"><b>{_esc(ritmo)}</b><span>Ritmo</span></div>
          <div class="ml-rep-mini"><b>{_esc(bpm)}</b><span>BPM</span></div>
          <div class="ml-rep-mini"><b>{_esc(compasso)}</b><span>Compasso</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ml-rep-section-title">Recursos</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        if yt and is_direct_url(yt):
            st.link_button("▶ YouTube", yt, use_container_width=True)
        else:
            st.button("▶ YouTube", disabled=True, use_container_width=True)
    with r2:
        from voice_kit_links import vocal_nipe_from_roles, voice_kit_youtube_url

        nipe = vocal_nipe_from_roles(str(st.session_state.get("user_roles", "")))
        if nipe:
            kit_url = voice_kit_youtube_url(nipe, title)
            st.link_button("♪ Kit Voz", kit_url, use_container_width=True)
        else:
            st.button("♪ Kit Voz", disabled=True, use_container_width=True)
    with r3:
        if cifra_url and is_direct_url(cifra_url):
            st.link_button("📄 Cifra", cifra_url, use_container_width=True)
        elif _has_cifra(row):
            st.button("📄 Cifra ✓", disabled=True, use_container_width=True)
        else:
            st.button("📄 Cifra", disabled=True, use_container_width=True)
    with r4:
        st.button("⏵ Playback", disabled=True, use_container_width=True)

    if temas:
        chips = "".join(f'<span class="ml-rep-chip">{_esc(t)}</span>' for t in temas[:8])
        st.markdown(
            f'<div class="ml-rep-section-title">Tags bíblicas</div><div class="ml-rep-chip-row">{chips}</div>',
            unsafe_allow_html=True,
        )

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    fav = _fav_titles(playlist_df, my_email)
    is_fav = title.strip().lower() in fav
    if st.button(
        "Remover da playlist" if is_fav else "Adicionar à playlist",
        type="primary",
        use_container_width=True,
        key="ml_rep_playlist_toggle",
    ):
        from app import PLAYLIST_FILE, add_louvor_to_playlist, prepare_playlist, save_data

        pl = playlist_df if playlist_df is not None else pd.DataFrame()
        if is_fav and not pl.empty:
            rest = pl[
                ~(
                    (pl["member_email"].astype(str).str.lower() == my_email)
                    & (
                        pl["title"].astype(str).str.strip().str.lower()
                        == title.strip().lower()
                    )
                )
            ]
            save_data(prepare_playlist(rest), PLAYLIST_FILE)
        else:
            add_louvor_to_playlist(pl, row.to_dict())
        st.rerun()


def _render_ferramentas(louvores_df: pd.DataFrame, *, is_mgr: bool) -> None:
    _render_back()
    st.markdown(
        """
        <div class="ml-rep-section-title" style="margin-top:0;">Ferramentas</div>
        <p style="color:rgba(148,163,184,.92);font-size:0.88rem;margin:0 0 1rem;">Repertório</p>
        """,
        unsafe_allow_html=True,
    )
    if not is_mgr:
        st.info("Ferramentas avançadas disponíveis para líderes do ministério.")
        return
    from app import _render_louvor_validation_search, _render_louvores_edit_manager
    from louvor_content import count_louvores_missing_content, count_louvores_with_full_content

    tools = (
        ("validacao", "✅ Validação bíblica"),
        ("relatorio", "📊 Relatório completo"),
        ("sugestoes", "💡 Sugestões"),
        ("importar", "📥 Importar músicas"),
    )
    for key, label in tools:
        with st.container(key=f"ml_rep_tool_{key}"):
            if st.button(label, key=f"ml_rep_tool_btn_{key}", use_container_width=True):
                st.session_state[f"ml_rep_tool_open_{key}"] = True
                st.rerun()

    if st.session_state.get("ml_rep_tool_open_validacao"):
        with st.expander("Validação bíblica", expanded=True):
            _render_louvor_validation_search(louvores_df)
    if st.session_state.get("ml_rep_tool_open_importar"):
        with st.expander("Editar / importar louvores", expanded=True):
            _render_louvores_edit_manager(louvores_df)

    completas = count_louvores_with_full_content(louvores_df)
    faltam = count_louvores_missing_content(louvores_df)
    st.caption(
        f"Banco local: **{completas}** de **{len(louvores_df)}** com letra e cifra · "
        f"**{faltam}** pendente(s)."
    )


def render_mobile_repertorio_page(
    louvores_df: pd.DataFrame,
    *,
    programa_df: pd.DataFrame | None = None,
    sugestoes_df: pd.DataFrame | None = None,
    playlist_df: pd.DataFrame | None = None,
) -> None:
    """Página Repertório mobile premium com dados reais do ministério."""
    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_repertorio_css()}</style>", unsafe_allow_html=True)

    louvores_df = ensure_louvor_content_columns(
        louvores_df.copy() if louvores_df is not None else pd.DataFrame()
    )
    programa_df = programa_df if programa_df is not None else pd.DataFrame()

    from app import is_scale_manager

    is_mgr = is_scale_manager(st.session_state.get("user_roles", []))
    view = _view()

    if view == "detalhe":
        _render_detalhe(louvores_df, playlist_df)
    elif view == "lista":
        _render_lista(louvores_df, sugestoes_df, playlist_df)
    elif view == "categorias":
        _render_categorias(louvores_df)
    elif view == "ferramentas":
        _render_ferramentas(louvores_df, is_mgr=is_mgr)
    else:
        _render_hub(
            louvores_df,
            programa_df,
            sugestoes_df,
            playlist_df,
            is_mgr=is_mgr,
        )
