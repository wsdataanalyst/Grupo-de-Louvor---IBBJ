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
)

LIST_TABS: tuple[tuple[str, str], ...] = (
    ("todas", "Todas"),
    ("favoritas", "Favoritas"),
    ("recentes", "Recentes"),
    ("cifra", "Cifras"),
)

_HUB_PAGE_SIZE = 8


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
    body:has(#ml-repertorio-page) .main .block-container{
      padding-bottom: 7rem !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_import"] .stButton > button,
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_nova"] .stButton > button{
      min-height: 2.65rem !important;
      border-radius: 16px !important;
      font-weight: 700 !important;
      font-size: 0.82rem !important;
      white-space: nowrap !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_import"] .stButton > button{
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #e2e8f0 !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_nova"] .stButton > button{
      background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
      border: none !important;
      color: #fff !important;
      box-shadow: 0 0 24px rgba(124,58,237,.28) !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_search_wrap"] .stTextInput > div > div > input{
      min-height: 3rem !important;
      border-radius: 18px !important;
      background: #111827 !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #fff !important;
      font-size: 0.95rem !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_metric_"] .stButton > button{
      min-height: 4.2rem !important;
      border-radius: 18px !important;
      font-weight: 700 !important;
      font-size: 0.72rem !important;
      white-space: pre-line !important;
      line-height: 1.15 !important;
      background: #09163f !important;
      border: 1px solid rgba(255,255,255,.06) !important;
      color: #94a3b8 !important;
      padding: 0.55rem 0.35rem !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_metric_"] .stButton > button[kind="primary"]{
      background: linear-gradient(135deg, rgba(88,56,255,.55), rgba(10,22,65,.95)) !important;
      border-color: rgba(139,92,246,.35) !important;
      color: #fff !important;
      box-shadow: 0 0 20px rgba(124,58,237,.22) !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_metric_"] .stButton > button p{
      margin: 0.15rem 0 0 !important;
      font-size: 1.05rem !important;
      font-weight: 800 !important;
      color: inherit !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_song_btn_"] .stButton > button{
      width: 100% !important;
      min-height: 0 !important;
      height: 0 !important;
      padding: 0 !important;
      margin: 0 !important;
      border: none !important;
      background: transparent !important;
      box-shadow: none !important;
      opacity: 0 !important;
      position: absolute !important;
      inset: 0 !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_song_wrap_"]{
      position: relative !important;
      margin-bottom: 0.55rem !important;
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
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_fav_toggle"] .stButton > button{
      border-radius: 18px !important;
      font-weight: 700 !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_cat_"] .stButton > button,
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_res_"] .stButton > button,
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_act_"] .stButton > button,
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_res_"] .stLinkButton > a{
      min-height: 3.2rem !important;
      border-radius: 18px !important;
      font-weight: 700 !important;
      font-size: 0.78rem !important;
      background: #0f172a !important;
      border: 1px solid rgba(255,255,255,.06) !important;
      color: #e2e8f0 !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_load_more"] .stButton > button{
      width: 100% !important;
      min-height: 2.85rem !important;
      border-radius: 18px !important;
      font-weight: 700 !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #a78bfa !important;
    }
    body:has(#ml-repertorio-page) [class*="st-key-ml_rep_tool_"] .stButton > button{
      border-radius: 18px !important;
      font-weight: 700 !important;
    }
    body:has(#ml-repertorio-page) div[data-testid="stTabs"] [data-baseweb="tab-list"]{
      gap: 0.35rem !important;
    }
    body:has(#ml-repertorio-page) div[data-testid="stTabs"] [data-baseweb="tab"]{
      font-weight: 700 !important;
      font-size: 0.78rem !important;
    }
    body:has(#ml-repertorio-page) div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"]{
      color: #a78bfa !important;
    }
    .ml-rep-header-card{
      background: rgba(8,18,55,.92);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 22px;
      padding: 0.95rem 1rem;
      margin-bottom: 0.85rem;
    }
    .ml-rep-header-row{
      display:flex;
      align-items:center;
      gap:0.75rem;
      min-width:0;
    }
    .ml-rep-header-icon{
      width:48px;height:48px;border-radius:14px;
      background:linear-gradient(135deg,#6d28d9,#4f46e5);
      display:flex;align-items:center;justify-content:center;
      font-size:1.35rem;
      flex:0 0 auto;
      box-shadow:0 0 24px rgba(109,40,217,.35);
    }
    .ml-rep-header-title{
      font-size:1.35rem;font-weight:800;line-height:1.12;margin:0;
      letter-spacing:-0.025em;color:#fff;
    }
    .ml-rep-header-sub{
      color:#9ca3af;
      font-size:0.78rem;
      line-height:1.3;
      margin:0.2rem 0 0;
    }
    .ml-rep-section-title{
      margin:1rem 0 0.55rem;
      font-size:1.05rem;font-weight:800;letter-spacing:-0.02em;color:#f8fafc;
    }
    .ml-rep-song-card{
      background:linear-gradient(135deg, rgba(88,56,255,.35), rgba(10,22,65,.95));
      border-radius:18px;
      padding:12px 14px;
      border:1px solid rgba(255,255,255,.06);
      display:flex;
      align-items:center;
      gap:12px;
      min-height:72px;
    }
    .ml-rep-song-card.selected{
      border-color: rgba(139,92,246,.55);
      box-shadow: 0 0 22px rgba(124,58,237,.25);
    }
    .ml-rep-song-thumb{
      width:48px;height:48px;border-radius:14px;
      background:linear-gradient(135deg, rgba(124,58,237,.45), rgba(59,130,246,.25));
      display:flex;align-items:center;justify-content:center;
      font-size:1.2rem;flex-shrink:0;
      border:1px solid rgba(255,255,255,.08);
    }
    .ml-rep-song-body{flex:1;min-width:0;}
    .ml-rep-song-title{
      font-size:1rem;font-weight:700;color:#fff;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    }
    .ml-rep-song-sub{
      color:#9ca3af;font-size:0.76rem;margin-top:3px;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    }
    .ml-rep-song-meta{color:#9ca3af;font-size:0.72rem;margin-top:4px;}
    .ml-rep-song-star{color:#fbbf24;font-size:0.95rem;flex-shrink:0;}
    .ml-rep-editor-card{
      background:#07122e;
      border-radius:22px;
      padding:1.1rem 1.15rem;
      border:1px solid rgba(255,255,255,.08);
      margin-bottom:0.85rem;
    }
    .ml-rep-editor-card h2{
      margin:0;font-size:1.45rem;font-weight:900;color:#fff;
    }
    .ml-rep-editor-card p{
      margin:0.35rem 0 0;color:#9ca3af;font-size:0.92rem;
    }
    .ml-rep-grid3{
      display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:0.75rem 0 0.15rem;
    }
    .ml-rep-mini{
      border-radius:16px;padding:10px 6px;text-align:center;
      background:#09163f;border:1px solid rgba(255,255,255,.06);
    }
    .ml-rep-mini b{display:block;font-size:0.95rem;color:#fff;}
    .ml-rep-mini span{font-size:0.68rem;color:#9ca3af;}
    .ml-rep-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin:0.55rem 0;}
    .ml-rep-tag{
      display:inline-block;padding:6px 12px;border-radius:999px;
      background:#1e293b;font-size:0.72rem;font-weight:600;color:#cbd5e1;
    }
    .ml-rep-action-card{
      background:#0f172a;border-radius:18px;padding:14px 8px;text-align:center;
      border:1px solid rgba(255,255,255,.06);
    }
    .ml-rep-action-card .ico{font-size:1.25rem;margin-bottom:0.25rem;}
    .ml-rep-action-card .lbl{font-size:0.72rem;font-weight:700;color:#e2e8f0;}
    .ml-rep-audio-player{
      background:linear-gradient(90deg, #6d28d9, #4f46e5);
      border-radius:18px;padding:16px 18px;margin-top:1rem;
      color:#fff;font-weight:700;font-size:0.88rem;
    }
    .ml-rep-hist-item{
      background:rgba(8,18,55,.92);
      border:1px solid rgba(255,255,255,.08);
      border-radius:16px;padding:12px 14px;margin-bottom:8px;
      color:#cbd5e1;font-size:0.84rem;
    }
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
    elif list_tab == "recentes":
        if recent_titles:
            filtered = filtered[
                filtered["title"].astype(str).str.strip().str.lower().isin(recent_titles)
            ]
        else:
            filtered = filtered.iloc[0:0]
    return filtered


def _render_back(label: str = "← Voltar") -> None:
    with st.container(key="ml_rep_back"):
        if st.button(label, use_container_width=True):
            prev = str(st.session_state.pop("ml_rep_back_to", "hub"))
            _set_view(prev)
            st.rerun()


def _format_duracao_display(row) -> str:
    from louvor_meta import format_duracao_total, parse_duracao_min

    raw = str(row.get("duracao_min", "")).strip()
    if not raw:
        return "—"
    return format_duracao_total(parse_duracao_min(raw))


def _song_meta_line(row) -> str:
    from catalog_sanitize import sanitize_catalog_text

    tom = sanitize_catalog_text(str(row.get("key", ""))) or "—"
    ritmo = sanitize_catalog_text(str(row.get("ritmo", ""))) or "—"
    dur = _format_duracao_display(row)
    return f"Tom: {tom} • {ritmo} • {dur}"


def _render_top_bar(louvores_df: pd.DataFrame, *, is_mgr: bool) -> None:
    st.markdown(
        """
        <div id="ml-repertorio-page" class="ml-page">
          <div class="ml-rep-header-card">
            <div class="ml-rep-header-row">
              <div class="ml-rep-header-icon" aria-hidden="true">🎵</div>
              <div style="min-width:0;flex:1;">
                <h1 class="ml-rep-header-title">Repertório</h1>
                <p class="ml-rep-header-sub">Gerencie todas as músicas do ministério</p>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="small")
    with c1:
        with st.container(key="ml_rep_import"):
            if st.button("📥 Importar", use_container_width=True):
                st.session_state.ml_rep_back_to = "hub"
                st.session_state.ml_rep_tool_open_importar = True
                _set_view("ferramentas")
                st.rerun()
    with c2:
        with st.container(key="ml_rep_nova"):
            if st.button("➕ Nova música", use_container_width=True):
                st.session_state["rep_add_open"] = True
                st.rerun()
    if st.session_state.get("rep_add_open"):
        with st.expander("➕ Nova música", expanded=True):
            if is_mgr:
                from app import _render_louvores_edit_manager

                _render_louvores_edit_manager(louvores_df, key_prefix="edit_rep_ml_add")
            else:
                st.info(
                    "Envie sugestões em **Sugestão de louvor** — a liderança analisa e "
                    "inclui no repertório."
                )
                if st.button("Ir para Sugestão de louvor", key="ml_rep_go_sugestao"):
                    st.session_state.ml_page = "Sugestões"
                    st.session_state.pop("rep_add_open", None)
                    st.rerun()


def _render_metric_tabs(
    *,
    total: int,
    fav_n: int,
    recent_n: int,
    cifra_n: int,
    active: str,
) -> None:
    items = (
        ("todas", "Todas", total),
        ("favoritas", "Favoritas", fav_n),
        ("recentes", "Recentes", recent_n),
        ("cifra", "Cifras", cifra_n),
    )
    cols = st.columns(4, gap="small")
    for col, (key, label, n) in zip(cols, items):
        with col:
            with st.container(key=f"ml_rep_metric_{key}"):
                if st.button(
                    f"{label}\n{n}",
                    key=f"ml_rep_metric_btn_{key}",
                    type="primary" if active == key else "secondary",
                ):
                    st.session_state.ml_rep_list_tab = key
                    st.session_state.ml_rep_hub_limit = _HUB_PAGE_SIZE
                    st.rerun()


def _song_card_html(
    title: str,
    artist: str,
    meta: str,
    *,
    is_fav: bool = False,
    selected: bool = False,
) -> str:
    sel = " selected" if selected else ""
    star = "★" if is_fav else "☆"
    return f"""
    <div class="ml-rep-song-card{sel}">
      <div class="ml-rep-song-thumb">🎵</div>
      <div class="ml-rep-song-body">
        <div class="ml-rep-song-title">{_esc(title)}</div>
        <div class="ml-rep-song-sub">{_esc(artist)}</div>
        <div class="ml-rep-song-meta">{_esc(meta)}</div>
      </div>
      <div class="ml-rep-song-star">{star}</div>
    </div>
    """


def _render_search_bar() -> str:
    return st.text_input(
        "Buscar",
        key="ml_rep_search",
        placeholder="Buscar música ou artista...",
        label_visibility="collapsed",
    )


def _render_filters_expander(louvores_df: pd.DataFrame) -> None:
    letters = sorted(
        {letter for letter in louvores_df["letter"].dropna().astype(str) if letter}
    )
    ritmos = sorted(
        {ritmo for ritmo in louvores_df["ritmo"].dropna().astype(str) if ritmo.strip()}
    )
    toms = sorted(
        {str(t).strip() for t in louvores_df["key"].dropna().astype(str) if str(t).strip()}
    )
    with st.expander("🔽 Filtros avançados", expanded=False):
        st.selectbox("Letra", ["Todas"] + letters, key="ml_rep_f_letter")
        st.selectbox("Tom", ["Todos"] + toms, key="ml_rep_f_tom")
        st.selectbox("Ritmo", ["Todos"] + ritmos, key="ml_rep_f_ritmo")
        st.multiselect(
            "Categoria / tema",
            list(LOUVOR_THEMES),
            key="ml_rep_f_tema",
            placeholder="Todos",
        )
        if st.button("Limpar filtros", key="ml_rep_clear", use_container_width=True):
            for k in (
                "ml_rep_search",
                "ml_rep_f_letter",
                "ml_rep_f_tom",
                "ml_rep_f_ritmo",
                "ml_rep_f_tema",
                "ml_rep_f_fav",
                "ml_rep_novas",
            ):
                st.session_state.pop(k, None)
            st.rerun()


def _render_song_list_v4(
    df: pd.DataFrame,
    *,
    fav_titles: set[str],
    key_prefix: str,
    limit: int | None = None,
    selected_title: str = "",
) -> None:
    from catalog_sanitize import sanitize_catalog_text

    show = df.head(limit) if limit else df
    if show.empty:
        st.info("Nenhuma música encontrada.")
        return
    for i, (_, row) in enumerate(show.iterrows()):
        title = sanitize_catalog_text(str(row.get("title", "")))
        artist = sanitize_catalog_text(str(row.get("artist", "")))
        meta = _song_meta_line(row)
        is_fav = title.strip().lower() in fav_titles
        selected = title.strip().lower() == selected_title.strip().lower()
        with st.container(key=f"ml_rep_song_wrap_{key_prefix}_{i}"):
            st.markdown(
                _song_card_html(title, artist, meta, is_fav=is_fav, selected=selected),
                unsafe_allow_html=True,
            )
            with st.container(key=f"ml_rep_song_btn_{key_prefix}_{i}"):
                if st.button("Abrir", key=f"ml_rep_open_{key_prefix}_{i}"):
                    _open_song(title)
                    st.rerun()


def _render_categories_grid(louvores_df: pd.DataFrame, *, limit: int = 6) -> None:
    cats = category_counts(louvores_df, limit=limit)
    st.markdown(
        '<div class="ml-rep-section-title">Categorias</div>',
        unsafe_allow_html=True,
    )
    for i in range(0, len(cats), 3):
        cols = st.columns(3, gap="small")
        for col, (name, n) in zip(cols, cats[i : i + 3]):
            with col:
                with st.container(key=f"ml_rep_cat_{i}_{name}"):
                    if st.button(f"{name}\n({n})", key=f"ml_rep_cat_btn_{i}_{name}"):
                        st.session_state.ml_rep_f_tema = [name]
                        st.session_state.ml_rep_back_to = "hub"
                        st.session_state.ml_rep_list_tab = "todas"
                        _set_view("lista")
                        st.rerun()
    if st.button("Ver todas as categorias", key="ml_rep_all_cats", use_container_width=True):
        st.session_state.ml_rep_back_to = "hub"
        _set_view("categorias")
        st.rerun()


def _save_louvor_fields(
    louvores_df: pd.DataFrame,
    title: str,
    *,
    lyrics: str | None = None,
    cifra: str | None = None,
    meta: dict | None = None,
) -> pd.DataFrame:
    from app import LOUVORES_FILE, save_data
    from louvor_content import apply_content_to_louvores_df
    from louvor_sync import apply_repertoire_save_side_effects

    match = louvores_df[
        louvores_df["title"].astype(str).str.strip().str.lower() == title.strip().lower()
    ]
    if match.empty:
        return louvores_df
    idx = match.index[0]
    titulo = str(louvores_df.at[idx, "title"]).strip()
    artista = str(louvores_df.at[idx, "artist"]).strip()
    if meta:
        for field, val in meta.items():
            if field in louvores_df.columns:
                louvores_df.at[idx, field] = val
    if lyrics is not None or cifra is not None:
        louvores_df = apply_content_to_louvores_df(
            louvores_df,
            titulo,
            artista,
            lyrics if lyrics is not None else str(louvores_df.at[idx, "lyrics_text"]),
            cifra if cifra is not None else str(louvores_df.at[idx, "cifra_text"]),
            source_tag="repertorio_mobile",
        )
    save_data(louvores_df, LOUVORES_FILE)
    from app import PROGRAMA_COLUMNS, PROGRAMA_FILE, load_data, prepare_programa
    from sequencia_culto import load_programa_sequencia_df

    programa_df = prepare_programa(load_data(PROGRAMA_FILE, PROGRAMA_COLUMNS))
    seq_df = load_programa_sequencia_df()
    programa_df, seq_df, _stats = apply_repertoire_save_side_effects(
        programa_df,
        seq_df,
        louvores_df,
        old_title=titulo,
        old_artist=artista,
        new_title=str(louvores_df.at[idx, "title"]).strip(),
        new_artist=str(louvores_df.at[idx, "artist"]).strip(),
    )
    from app import save_data as _sd

    _sd(programa_df, PROGRAMA_FILE)
    from sequencia_culto import save_programa_sequencia_df

    save_programa_sequencia_df(seq_df)
    return louvores_df


def _open_song(title: str) -> None:
    st.session_state.ml_rep_selected_title = title
    st.session_state.ml_rep_back_to = _view()
    _set_view("detalhe")


def _filtered_repertorio(
    louvores_df: pd.DataFrame,
    *,
    sugestoes_df: pd.DataFrame | None,
    playlist_df: pd.DataFrame | None,
    list_tab: str | None = None,
) -> tuple[pd.DataFrame, set[str], set[str]]:
    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    fav = _fav_titles(playlist_df, my_email)
    recent = _recent_titles(sugestoes_df)
    tab = list_tab or _list_tab()
    return (
        _filter_df(
            louvores_df,
            search=str(st.session_state.get("ml_rep_search", "")),
            letter=str(st.session_state.get("ml_rep_f_letter", "Todas")),
            tom=str(st.session_state.get("ml_rep_f_tom", "Todos")),
            ritmo=str(st.session_state.get("ml_rep_f_ritmo", "Todos")),
            temas=st.session_state.get("ml_rep_f_tema", []),
            tags=st.session_state.get("ml_rep_f_tag", []),
            apenas_fav=bool(st.session_state.get("ml_rep_f_fav", False)),
            fav_titles=fav,
            novas_only=bool(st.session_state.get("ml_rep_novas", False)),
            recent_titles=recent,
            list_tab=tab,
        ),
        fav,
        recent,
    )


def _render_hub(
    louvores_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    sugestoes_df: pd.DataFrame | None,
    playlist_df: pd.DataFrame | None,
    *,
    is_mgr: bool,
) -> None:
    _render_top_bar(louvores_df, is_mgr=is_mgr)

    if louvores_df.empty:
        st.warning("Repertório ainda não gerado. Execute: `python build_louvores_db.py`")
        return

    stats = compute_repertorio_stats(louvores_df)
    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    fav = _fav_titles(playlist_df, my_email)
    recent = _recent_titles(sugestoes_df)
    fav_n = len(
        louvores_df[
            louvores_df["title"].astype(str).str.strip().str.lower().isin(fav)
        ]
    ) if fav else 0
    recent_n = len(
        louvores_df[
            louvores_df["title"].astype(str).str.strip().str.lower().isin(recent)
        ]
    ) if recent else 0

    with st.container(key="ml_rep_search_wrap"):
        _render_search_bar()
    _render_filters_expander(louvores_df)

    tab = _list_tab()
    _render_metric_tabs(
        total=stats["total"],
        fav_n=fav_n,
        recent_n=recent_n,
        cifra_n=stats["cifra"],
        active=tab,
    )

    filtered, fav, _recent = _filtered_repertorio(
        louvores_df,
        sugestoes_df=sugestoes_df,
        playlist_df=playlist_df,
        list_tab=tab,
    )

    st.markdown(
        f'<div class="ml-rep-section-title">Músicas ({len(filtered)})</div>',
        unsafe_allow_html=True,
    )

    hub_limit = int(st.session_state.get("ml_rep_hub_limit", _HUB_PAGE_SIZE))
    _render_song_list_v4(
        filtered,
        fav_titles=fav,
        key_prefix="hub",
        limit=hub_limit,
    )

    if hub_limit < len(filtered):
        with st.container(key="ml_rep_load_more"):
            if st.button("Carregar mais músicas", use_container_width=True):
                st.session_state.ml_rep_hub_limit = hub_limit + _HUB_PAGE_SIZE
                st.rerun()
    elif len(filtered) > _HUB_PAGE_SIZE:
        with st.container(key="ml_rep_load_more"):
            if st.button("Ver lista completa", use_container_width=True):
                st.session_state.ml_rep_back_to = "hub"
                _set_view("lista")
                st.rerun()

    _render_categories_grid(louvores_df)

    if is_mgr:
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
          <h2 style="margin:0 0 0.5rem;font-size:1.35rem;font-weight:800;">Músicas</h2>
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

    with st.container(key="ml_rep_search_wrap"):
        _render_search_bar()

    filtered, fav, _recent = _filtered_repertorio(
        louvores_df,
        sugestoes_df=sugestoes_df,
        playlist_df=playlist_df,
        list_tab=tab,
    )
    st.caption(f"{len(filtered)} músicas · repertório com {len(louvores_df)} louvores")
    _render_song_list_v4(filtered, fav_titles=fav, key_prefix="lista", limit=80)


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


def _render_detalhe(
    louvores_df: pd.DataFrame,
    playlist_df: pd.DataFrame | None,
    *,
    is_mgr: bool,
) -> None:
    from catalog_sanitize import sanitize_catalog_text

    c1, c2 = st.columns([3, 2], gap="small")
    with c1:
        _render_back()
    with c2:
        with st.container(key="ml_rep_fav_toggle"):
            my_email = str(st.session_state.get("user_email", "")).strip().lower()
            fav = _fav_titles(playlist_df, my_email)
            title_key = str(st.session_state.get("ml_rep_selected_title", "")).strip()
            is_fav = title_key.strip().lower() in fav
            if st.button(
                "★ Favorita" if is_fav else "☆ Favoritar",
                use_container_width=True,
            ):
                from app import PLAYLIST_FILE, add_louvor_to_playlist, prepare_playlist, save_data

                match = louvores_df[
                    louvores_df["title"].astype(str).str.strip().str.lower()
                    == title_key.lower()
                ]
                if match.empty:
                    return
                row = match.iloc[0]
                title = sanitize_catalog_text(str(row.get("title", "")))
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
    duracao = _format_duracao_display(row)
    temas = themes_from_csv(str(row.get("temas", "")))
    ref_bib = sanitize_catalog_text(str(row.get("ref_biblica", "")))
    yt = str(row.get("youtube_url", "")).strip()
    cifra_url = str(row.get("cifra_url", "")).strip()
    lyrics = str(row.get("lyrics_text", "")).strip()
    cifra_txt = str(row.get("cifra_text", "")).strip()
    valid_status = sanitize_catalog_text(str(row.get("validacao_status", "")))

    st.markdown(
        f"""
        <div class="ml-rep-editor-card">
          <h2>{_esc(title)}</h2>
          <p>{_esc(artist)}</p>
          <div class="ml-rep-grid3">
            <div class="ml-rep-mini"><b>{_esc(tom)}</b><span>Tom</span></div>
            <div class="ml-rep-mini"><b>{_esc(ritmo)}</b><span>Ritmo</span></div>
            <div class="ml-rep-mini"><b>{_esc(duracao)}</b><span>Duração</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_info, tab_letra, tab_cifra, tab_audio, tab_hist = st.tabs(
        ["Informações", "Letra", "Cifras", "Áudio", "Histórico"]
    )

    with tab_info:
        st.markdown('<div class="ml-rep-section-title">Dados da música</div>', unsafe_allow_html=True)
        if is_mgr:
            c1, c2 = st.columns(2, gap="small")
            with c1:
                n_title = st.text_input("Nome da música", value=title, key="ml_rep_ed_title")
                tom_opts = ["C", "D", "E", "F", "G", "A", "B"]
                if tom not in tom_opts and tom != "—":
                    tom_opts.append(tom)
                n_tom = st.selectbox(
                    "Tom",
                    tom_opts,
                    index=tom_opts.index(tom) if tom in tom_opts else 0,
                    key="ml_rep_ed_tom",
                )
                n_dur = st.text_input("Duração", value=str(row.get("duracao_min", "")), key="ml_rep_ed_dur")
                cat_opts = list(LOUVOR_THEMES)
                default_cat = temas[0] if temas else cat_opts[0]
                n_cat = st.selectbox(
                    "Categoria",
                    cat_opts,
                    index=cat_opts.index(default_cat) if default_cat in cat_opts else 0,
                    key="ml_rep_ed_cat",
                )
            with c2:
                n_artist = st.text_input("Artista", value=artist, key="ml_rep_ed_artist")
                n_ritmo = st.text_input("Ritmo", value=ritmo if ritmo != "—" else "", key="ml_rep_ed_ritmo")
                n_ref = st.text_input("Referência bíblica", value=ref_bib, key="ml_rep_ed_ref")
                n_yt = st.text_input("YouTube", value=yt, key="ml_rep_ed_yt")
            tags_txt = st.text_input(
                "Tags",
                value=", ".join(temas),
                key="ml_rep_ed_tags",
            )
            if st.button("💾 Salvar informações", key="ml_rep_save_info", type="primary"):
                _save_louvor_fields(
                    louvores_df,
                    title,
                    meta={
                        "title": n_title.strip(),
                        "artist": n_artist.strip(),
                        "key": n_tom.strip(),
                        "ritmo": n_ritmo.strip(),
                        "duracao_min": n_dur.strip(),
                        "temas": n_cat,
                        "ref_biblica": n_ref.strip(),
                        "youtube_url": n_yt.strip(),
                    },
                )
                st.session_state.ml_rep_selected_title = n_title.strip()
                st.success("Informações salvas.")
                st.rerun()
        else:
            st.markdown(
                f"""
                <p><b>Música:</b> {_esc(title)}</p>
                <p><b>Artista:</b> {_esc(artist)}</p>
                <p><b>Tom:</b> {_esc(tom)} · <b>Ritmo:</b> {_esc(ritmo)} · <b>Duração:</b> {_esc(duracao)}</p>
                """,
                unsafe_allow_html=True,
            )
            if temas:
                chips = "".join(f'<span class="ml-rep-tag">{_esc(t)}</span>' for t in temas)
                st.markdown(f'<div class="ml-rep-chip-row">{chips}</div>', unsafe_allow_html=True)

        st.markdown('<div class="ml-rep-section-title">Recursos</div>', unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4, gap="small")
        with r1:
            with st.container(key="ml_rep_res_letra"):
                if lyrics:
                    st.button("📄 Letra", key="ml_rep_go_letra", use_container_width=True)
                else:
                    st.button("📄 Letra", disabled=True, use_container_width=True)
        with r2:
            with st.container(key="ml_rep_res_cifra"):
                if cifra_txt or (cifra_url and is_direct_url(cifra_url)):
                    if cifra_url and is_direct_url(cifra_url):
                        st.link_button("🎼 Cifra", cifra_url, use_container_width=True)
                    else:
                        st.button("🎼 Cifra", key="ml_rep_go_cifra", use_container_width=True)
                else:
                    st.button("🎼 Cifra", disabled=True, use_container_width=True)
        with r3:
            with st.container(key="ml_rep_res_audio"):
                st.button("🎧 Áudio", disabled=True, use_container_width=True)
        with r4:
            with st.container(key="ml_rep_res_yt"):
                if yt and is_direct_url(yt):
                    st.link_button("▶ YouTube", yt, use_container_width=True)
                else:
                    st.button("▶ YouTube", disabled=True, use_container_width=True)

        st.markdown('<div class="ml-rep-section-title">Ações</div>', unsafe_allow_html=True)
        a1, a2 = st.columns(2, gap="small")
        with a1:
            with st.container(key="ml_rep_act_letra"):
                st.button("✏ Editar letra", key="ml_rep_act_ed_letra", use_container_width=True)
            with st.container(key="ml_rep_act_audio"):
                st.button("☁ Upload áudio", disabled=True, use_container_width=True)
        with a2:
            with st.container(key="ml_rep_act_cifra"):
                st.button("🎵 Editar cifra", key="ml_rep_act_ed_cifra", use_container_width=True)
            with st.container(key="ml_rep_act_hist"):
                st.button("🕒 Histórico", key="ml_rep_act_hist", use_container_width=True)

    with tab_letra:
        letra_val = lyrics or "Letra ainda não cadastrada no repertório."
        if is_mgr:
            letra_edit = st.text_area("Letra", value=lyrics, height=420, key="ml_rep_lyrics_edit")
            if st.button("💾 Salvar letra", key="ml_rep_save_lyrics", type="primary"):
                _save_louvor_fields(louvores_df, title, lyrics=letra_edit.strip())
                st.success("Letra salva no repertório.")
                st.rerun()
        else:
            st.text_area("Letra", value=letra_val, height=420, disabled=True, key="ml_rep_lyrics_view")

    with tab_cifra:
        cifra_val = cifra_txt or "Cifra ainda não cadastrada no repertório."
        if is_mgr:
            cifra_edit = st.text_area("Cifra", value=cifra_txt, height=420, key="ml_rep_cifra_edit")
            if st.button("💾 Salvar cifra", key="ml_rep_save_cifra", type="primary"):
                _save_louvor_fields(louvores_df, title, cifra=cifra_edit.strip())
                st.success("Cifra salva no repertório.")
                st.rerun()
        else:
            st.text_area("Cifra", value=cifra_val, height=420, disabled=True, key="ml_rep_cifra_view")
        if cifra_url and is_direct_url(cifra_url):
            st.link_button("Abrir cifra no Cifra Club", cifra_url, use_container_width=True)

    with tab_audio:
        st.info("Upload de áudio em breve — use YouTube ou Kit Voz por enquanto.")
        from voice_kit_links import vocal_nipe_from_roles, voice_kit_youtube_url

        nipe = vocal_nipe_from_roles(str(st.session_state.get("user_roles", "")))
        if nipe:
            kit_url = voice_kit_youtube_url(nipe, title)
            st.link_button("🎤 Abrir Kit Voz", kit_url, use_container_width=True)
        if yt and is_direct_url(yt):
            st.link_button("▶ Ouvir no YouTube", yt, use_container_width=True)
        st.markdown(
            f"""
            <div class="ml-rep-audio-player">
              🎵 {_esc(title)} · {_esc(duracao)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_hist:
        items: list[str] = []
        if lyrics:
            items.append("Letra disponível no repertório local")
        if cifra_txt:
            items.append("Cifra disponível no repertório local")
        if valid_status:
            items.append(f"Validação: {valid_status}")
        if yt:
            items.append("Link YouTube cadastrado")
        if not items:
            items.append("Nenhum histórico registrado para esta música.")
        for msg in items:
            st.markdown(f'<div class="ml-rep-hist-item">{_esc(msg)}</div>', unsafe_allow_html=True)


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
            if st.session_state.get("rep_add_open"):
                st.caption("O editor já está aberto em **Adicionar música**.")
            else:
                _render_louvores_edit_manager(louvores_df, key_prefix="edit_rep_ml_tool")

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
        _render_detalhe(louvores_df, playlist_df, is_mgr=is_mgr)
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
