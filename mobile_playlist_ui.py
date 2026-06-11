"""Mobile Lab — Playlist (layout premium V2)."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme

PL_VIEWS = frozenset({"hub", "detail", "add", "nova"})

QUICK_FILTERS: tuple[tuple[str, str, str], ...] = (
    ("todos", "Todos", "🎵"),
    ("treinos", "Treinos", "💪"),
    ("cultos", "Cultos", "🙏"),
    ("ensaios", "Ensaios", "📅"),
    ("favoritas", "Favoritas", "⭐"),
)

PRESET_META: dict[str, tuple[str, str, str]] = {
    "Treino Domingo": ("TREINO", "💪", "treinos"),
    "Ensaio da Semana": ("ENSAIO", "📅", "ensaios"),
    "Culto da Família": ("CULTO", "🙏", "cultos"),
    "Pré Culto": ("CULTO", "✨", "cultos"),
}


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _view() -> str:
    v = str(st.session_state.get("ml_pl_view", "hub")).strip()
    return v if v in PL_VIEWS else "hub"


def _set_view(view: str) -> None:
    st.session_state.ml_pl_view = view


def _filter_key() -> str:
    f = str(st.session_state.get("ml_pl_filter", "todos")).strip()
    valid = {k for k, _, _ in QUICK_FILTERS}
    return f if f in valid else "todos"


def _search_query() -> str:
    # Chave única do widget (evita colisão com containers legados ml_pl_search).
    legacy = str(st.session_state.get("ml_pl_search", "")).strip()
    cur = str(st.session_state.get("ml_pl_hub_search", legacy)).strip()
    return cur.lower()


def _sort_key() -> str:
    s = str(st.session_state.get("ml_pl_sort", "recent")).strip()
    return s if s in ("recent", "name", "tracks") else "recent"


def _time_ago(value: object) -> str:
    try:
        dt = pd.to_datetime(value)
        if pd.isna(dt):
            return "—"
        delta = datetime.now() - dt.to_pydatetime()
        if delta.days > 0:
            return f"Atualizada há {delta.days} dia(s)"
        h = delta.seconds // 3600
        if h > 0:
            return f"Atualizada há {h}h"
        m = max(1, delta.seconds // 60)
        return f"Atualizada há {m} min"
    except (ValueError, TypeError):
        return "—"


def mobile_playlist_css() -> str:
    return r"""
    body:has(#ml-playlist-page) .ig-pl-page,
    body:has(#ml-playlist-page) .ig-pl-header,
    body:has(#ml-playlist-page) .ig-m-hdr-row{ display: none !important; }

    body:has(#ml-playlist-page) [data-testid="stMain"] .block-container{
      padding-top: 0.35rem !important;
      max-width: 900px !important;
    }

    .ml-pl-titulo{
      font-size: 1.45rem; font-weight: 800; margin: 0; letter-spacing: -0.03em;
    }
    .ml-pl-sub{ color: #b7bfd1; font-size: 0.8rem; margin: 0.3rem 0 0; }

    .ml-pl-hero{
      background: linear-gradient(135deg, #5B21B6, #312E81);
      border-radius: 24px; padding: 1.1rem 1rem; margin: 0.7rem 0 0.85rem;
      border: 1px solid rgba(255,255,255,.1);
      box-shadow: 0 0 36px rgba(91,33,182,.22);
      display: flex; align-items: center; gap: 0.85rem;
    }
    .ml-pl-hero-ico{
      width: 52px; height: 52px; border-radius: 18px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      background: rgba(255,255,255,.12); font-size: 1.5rem;
    }
    .ml-pl-hero-text{ flex: 1; min-width: 0; }
    .ml-pl-hero-text h2{
      margin: 0 0 0.25rem; font-size: 0.98rem; font-weight: 800; line-height: 1.25;
    }
    .ml-pl-hero-text p{
      margin: 0; font-size: 0.74rem; color: rgba(226,232,240,.9); line-height: 1.4;
    }
    .ml-pl-hero-stats{
      text-align: right; padding: 0.55rem 0.7rem; border-radius: 16px;
      background: rgba(0,0,0,.2); border: 1px solid rgba(255,255,255,.1);
      flex-shrink: 0; font-size: 0.68rem; color: rgba(226,232,240,.9); line-height: 1.45;
    }
    .ml-pl-hero-stats b{ color: #fff; font-size: 0.78rem; }

    .ml-pl-stat-grid{
      display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.45rem; margin-bottom: 0.85rem;
    }
    @media (max-width: 420px){
      .ml-pl-stat-grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    .ml-pl-stat{
      background: #091633; border-radius: 18px; padding: 0.7rem 0.35rem;
      text-align: center; border: 1px solid rgba(255,255,255,.06);
    }
    .ml-pl-stat-ico{ font-size: 1rem; margin-bottom: 0.2rem; }
    .ml-pl-stat h2{ margin: 0; font-size: 1.2rem; font-weight: 800; line-height: 1; }
    .ml-pl-stat span{
      display: block; margin-top: 0.3rem; font-size: 0.6rem; font-weight: 700;
      color: #94a3b8; text-transform: uppercase; letter-spacing: 0.03em;
    }

    .ml-pl-card{
      display: flex; align-items: center; gap: 0.75rem;
      background: rgba(7,20,50,.75); border: 1px solid rgba(255,255,255,.08);
      border-radius: 22px; padding: 0.8rem 0.85rem; margin-bottom: 0.55rem;
    }
    .ml-pl-thumb-wrap{ position: relative; flex-shrink: 0; }
    .ml-pl-thumb{
      width: 54px; height: 54px; border-radius: 16px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.35rem;
    }
    .ml-pl-thumb--purple{ background: linear-gradient(135deg, #7c3aed, #5b21b6); }
    .ml-pl-thumb--blue{ background: linear-gradient(135deg, #2563eb, #1d4ed8); }
    .ml-pl-thumb--gold{ background: linear-gradient(135deg, #d97706, #b45309); }
    .ml-pl-thumb--green{ background: linear-gradient(135deg, #059669, #047857); }
    .ml-pl-thumb-label{
      position: absolute; top: -4px; left: -4px;
      font-size: 0.48rem; font-weight: 800; letter-spacing: 0.04em;
      padding: 0.15rem 0.35rem; border-radius: 6px;
      background: rgba(0,0,0,.55); color: #e2e8f0;
    }
    .ml-pl-body{ flex: 1; min-width: 0; }
    .ml-pl-name{ font-size: 0.92rem; font-weight: 800; margin: 0; }
    .ml-pl-meta{ font-size: 0.72rem; color: #94a3b8; margin-top: 0.2rem; }
    .ml-pl-updated{ font-size: 0.65rem; color: #64748b; margin-top: 0.15rem; }
    .ml-pl-tag{
      display: inline-block; margin-top: 0.35rem; padding: 0.18rem 0.5rem;
      border-radius: 999px; font-size: 0.62rem; font-weight: 700;
      background: rgba(124,58,237,.22); color: #ddd6fe;
    }
    .ml-pl-tag--gold{ background: rgba(217,119,6,.22); color: #fde68a; }
    .ml-pl-tag--blue{ background: rgba(37,99,235,.22); color: #bfdbfe; }

    .ml-pl-cta{
      background: linear-gradient(135deg, rgba(91,33,182,.45), rgba(49,46,129,.85));
      border-radius: 22px; padding: 1rem; margin: 0.85rem 0 0.5rem;
      border: 1px solid rgba(139,92,246,.28);
      display: flex; align-items: center; gap: 0.75rem;
    }
    .ml-pl-cta-text h3{ margin: 0 0 0.2rem; font-size: 0.92rem; font-weight: 800; }
    .ml-pl-cta-text p{ margin: 0; font-size: 0.74rem; color: #cbd5e1; line-height: 1.35; }

    .ml-pl-section{
      margin: 0.65rem 0 0.45rem; font-size: 0.95rem; font-weight: 800;
      display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
    }
    .ml-pl-empty{
      padding: 1rem; border-radius: 20px; text-align: center;
      background: rgba(15,23,42,.55); border: 1px dashed rgba(255,255,255,.1);
      color: #94a3b8; font-size: 0.82rem;
    }
    .ml-pl-filter-lbl{
      font-size: 0.72rem; font-weight: 700; color: #94a3b8;
      text-transform: uppercase; letter-spacing: 0.04em; margin: 0.5rem 0 0.35rem;
    }

    body:has(#ml-playlist-page) [class*="st-key-ml_pl_filter_"] .stButton > button{
      border-radius: 14px !important; min-height: 2rem !important;
      font-size: 0.68rem !important; font-weight: 700 !important; white-space: nowrap !important;
    }
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_filters"] [data-testid="stHorizontalBlock"]{
      display: flex !important; flex-wrap: nowrap !important;
      overflow-x: auto !important; gap: 6px !important; scrollbar-width: none;
    }
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_filters"] [data-testid="stColumn"]{
      flex: 0 0 auto !important; width: auto !important; max-width: none !important;
    }
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_hub_search"] .stTextInput > div > div > input,
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_add_box"] .stTextInput > div > div > input{
      border-radius: 18px !important; min-height: 2.85rem !important;
      background: rgba(7,21,45,.92) !important; border: 1px solid rgba(255,255,255,.08) !important;
    }
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_nova_btn"] .stButton > button,
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_cta_btn"] .stButton > button,
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_add_btn"] .stButton > button{
      border-radius: 16px !important; font-weight: 800 !important;
      background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
      color: #fff !important; border: none !important;
    }
    body:has(#ml-playlist-page) [class*="st-key-ml_pl_open_"] .stButton > button{
      border-radius: 50% !important; min-width: 2.4rem !important;
      min-height: 2.4rem !important; padding: 0 !important;
      background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
      color: #fff !important; border: none !important; font-size: 0.85rem !important;
    }
    """


def _thumb_class(css_cls: str) -> str:
    for token in ("purple", "blue", "gold", "green"):
        if token in css_cls:
            return f"ml-pl-thumb--{token}"
    return "ml-pl-thumb--purple"


def _louvor_lookup(louvores_df: pd.DataFrame) -> dict[str, pd.Series]:
    out: dict[str, pd.Series] = {}
    if louvores_df.empty:
        return out
    for _, row in louvores_df.iterrows():
        key = str(row.get("title", "")).strip().lower()
        if key:
            out[key] = row
    return out


def _duration_min_for_track(title: str, louvores_df: pd.DataFrame) -> float:
    from louvor_meta import parse_duracao_min

    key = str(title).strip().lower()
    if not key or louvores_df.empty:
        return 4.5
    hit = louvores_df[louvores_df["title"].astype(str).str.strip().str.lower() == key]
    if hit.empty:
        return 4.5
    return parse_duracao_min(hit.iloc[0].get("duracao_min", ""))


def _slice_duration(slice_df: pd.DataFrame, louvores_df: pd.DataFrame) -> str:
    from playlist_ui import format_duration_hours

    total = 0.0
    for _, tr in slice_df.iterrows():
        total += _duration_min_for_track(str(tr.get("title", "")), louvores_df)
    return format_duration_hours(total)


def _slice_tag(slice_df: pd.DataFrame, louvores_df: pd.DataFrame) -> tuple[str, str]:
    from app import themes_from_csv

    if slice_df.empty:
        return "Repertório", ""
    for _, tr in slice_df.iterrows():
        ritmo = str(tr.get("ritmo", "")).strip()
        if ritmo:
            return ritmo, ""
    key = str(slice_df.iloc[0].get("title", "")).strip().lower()
    lou = _louvor_lookup(louvores_df).get(key)
    if lou is not None:
        ritmo = str(lou.get("ritmo", "")).strip()
        if ritmo:
            return ritmo, "ml-pl-tag--blue"
        themes = themes_from_csv(str(lou.get("temas", "")))
        if themes:
            return themes[0], "ml-pl-tag--gold"
    return "Louvor", ""


def _distribute_presets(mine: pd.DataFrame, louvores_df: pd.DataFrame) -> list[dict]:
    from playlist_ui import PRESET_PLAYLISTS

    names = PRESET_PLAYLISTS
    n = len(mine)
    if n == 0:
        return [
            {
                "name": name,
                "cls": cls,
                "count": 0,
                "meta": "0 faixas · 0m",
                "slice": mine.iloc[0:0].copy(),
                "updated": "—",
                "tag": "Repertório",
                "tag_cls": "",
                "category": PRESET_META.get(name, ("", "", "todos"))[2],
                "emoji": PRESET_META.get(name, ("", "🎵", ""))[1],
                "label": PRESET_META.get(name, ("LISTA", "", ""))[0],
            }
            for name, cls in names
        ]

    sorted_mine = mine.copy()
    sorted_mine["_sort"] = pd.to_datetime(sorted_mine["added_at"], errors="coerce")
    sorted_mine = sorted_mine.sort_values("_sort", ascending=False)

    base, rem = divmod(n, len(names))
    chunks = [base + (1 if i < rem else 0) for i in range(len(names))]
    out: list[dict] = []
    idx = 0
    for (name, cls), cnt in zip(names, chunks):
        slice_df = sorted_mine.iloc[idx : idx + cnt].copy()
        idx += cnt
        dur = _slice_duration(slice_df, louvores_df)
        tag, tag_cls = _slice_tag(slice_df, louvores_df)
        updated = "—"
        if not slice_df.empty and "_sort" in slice_df.columns:
            updated = _time_ago(slice_df["_sort"].max())
        label, emoji, category = PRESET_META.get(name, ("LISTA", "🎵", "todos"))
        out.append(
            {
                "name": name,
                "cls": cls,
                "count": cnt,
                "meta": f"{cnt} faixas · {dur}",
                "slice": slice_df,
                "updated": updated,
                "tag": tag,
                "tag_cls": tag_cls,
                "category": category,
                "emoji": emoji,
                "label": label,
            }
        )
    return out


def _updated_today_count(mine: pd.DataFrame) -> int:
    if mine.empty:
        return 0
    today = datetime.now().date()
    n = 0
    for val in mine["added_at"]:
        try:
            if pd.to_datetime(val).date() == today:
                n += 1
        except (ValueError, TypeError):
            continue
    return n


def _match_catalog_filters(
    slice_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    ritmo: str,
    minist: list[str],
    tag: list[str],
) -> bool:
    from app import themes_from_csv

    if slice_df.empty:
        return ritmo == "Todos" and not minist and not tag
    lookup = _louvor_lookup(louvores_df)
    for _, tr in slice_df.iterrows():
        title = str(tr.get("title", "")).strip().lower()
        lou = lookup.get(title)
        rit = str(tr.get("ritmo", "")).strip()
        if not rit and lou is not None:
            rit = str(lou.get("ritmo", "")).strip()
        if ritmo != "Todos" and rit != ritmo:
            continue
        themes: list[str] = []
        if lou is not None:
            themes = themes_from_csv(str(lou.get("temas", "")))
        if minist and not any(t in themes for t in minist):
            continue
        if tag and not any(t in themes for t in tag):
            continue
        return True
    return ritmo == "Todos" and not minist and not tag


def _filter_presets(presets: list[dict], filt: str) -> list[dict]:
    if filt == "todos":
        return presets
    if filt == "favoritas":
        return []
    return [p for p in presets if p["category"] == filt]


def _search_presets(presets: list[dict], query: str) -> list[dict]:
    if not query:
        return presets
    return [p for p in presets if query in str(p["name"]).lower()]


def _sort_presets(presets: list[dict], sort: str) -> list[dict]:
    if sort == "name":
        return sorted(presets, key=lambda p: str(p["name"]).lower())
    if sort == "tracks":
        return sorted(presets, key=lambda p: (-int(p["count"]), str(p["name"]).lower()))
    return sorted(
        presets,
        key=lambda p: (
            -(
                pd.to_datetime(p["slice"]["added_at"], errors="coerce").max()
                if not p["slice"].empty
                else pd.Timestamp.min
            ).timestamp()
            if not p["slice"].empty
            else 0
        ),
    )


def _preset_card_html(preset: dict, idx: int) -> str:
    tag_cls = preset.get("tag_cls") or ""
    return (
        f'<div class="ml-pl-card">'
        f'<div class="ml-pl-thumb-wrap">'
        f'<span class="ml-pl-thumb-label">{_esc(preset["label"])}</span>'
        f'<div class="ml-pl-thumb {_thumb_class(preset["cls"])}">{preset["emoji"]}</div>'
        f"</div>"
        f'<div class="ml-pl-body">'
        f'<p class="ml-pl-name">{_esc(preset["name"])}</p>'
        f'<div class="ml-pl-meta">{_esc(preset["meta"])}</div>'
        f'<div class="ml-pl-updated">{_esc(preset["updated"])}</div>'
        f'<span class="ml-pl-tag {tag_cls}">{_esc(preset["tag"])}</span>'
        f"</div></div>"
    )


def _favorite_track_html(track: pd.Series, louvores_df: pd.DataFrame) -> str:
    from catalog_sanitize import sanitize_catalog_text

    title = sanitize_catalog_text(str(track.get("title", "")))
    artist = sanitize_catalog_text(str(track.get("artist", ""))) or "—"
    dur = _duration_min_for_track(title, louvores_df)
    mins = int(dur)
    return (
        f'<div class="ml-pl-card">'
        f'<div class="ml-pl-thumb-wrap">'
        f'<div class="ml-pl-thumb ml-pl-thumb--gold">⭐</div></div>'
        f'<div class="ml-pl-body">'
        f'<p class="ml-pl-name">{_esc(title)}</p>'
        f'<div class="ml-pl-meta">{_esc(artist)} · {mins} min</div>'
        f"</div></div>"
    )


def _prepare_mine(playlist_df: pd.DataFrame) -> tuple[pd.DataFrame, set[str]]:
    from app import playlist_for_user, prepare_playlist
    from playlist_ui import get_favorite_ids

    my_email = st.session_state.user_email.strip().lower()
    playlist_df = prepare_playlist(playlist_df)
    mine = playlist_for_user(playlist_df, my_email)
    fav_ids = get_favorite_ids()
    if mine.empty:
        fav_ids = set()
    else:
        mine_ids = set(mine["id"].astype(str))
        fav_ids = fav_ids & mine_ids
        st.session_state["pl_favorite_ids"] = fav_ids
    return mine, fav_ids


def _render_header(*, show_back: bool = False) -> None:
    back_col, title_col, act_col = st.columns([0.55, 4, 0.7])
    with back_col:
        if show_back:
            if st.button("←", key="ml_pl_back", help="Voltar"):
                _set_view("hub")
                st.session_state.pop("ml_pl_preset_idx", None)
                st.rerun()
    with title_col:
        st.markdown(
            """
            <div>
              <div class="ml-pl-titulo">🎧 Minhas Playlists</div>
              <p class="ml-pl-sub">Organize, gerencie e use suas playlists</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with act_col:
        with st.container(key="ml_pl_nova_btn"):
            if st.button("➕", key="ml_pl_nova_open", help="Nova playlist"):
                _set_view("nova")
                st.rerun()


def _render_hero(*, n_presets: int, n_tracks: int) -> None:
    st.markdown(
        f"""
        <div class="ml-pl-hero">
          <div class="ml-pl-hero-ico">🎵</div>
          <div class="ml-pl-hero-text">
            <h2>Suas músicas, sua missão</h2>
            <p>Monte listas para ensaios e cultos com YouTube, cifra e Kit Voz.</p>
          </div>
          <div class="ml-pl-hero-stats">
            <div><b>{n_presets}</b> playlists</div>
            <div><b>{n_tracks}</b> faixas cadastradas</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_stat_grid(stats: dict, *, updated_today: int) -> None:
    items = [
        ("🎧", stats["playlists"], "Playlists"),
        ("🎵", stats["tracks"], "Faixas"),
        ("⏱", stats["hours"], "Duração"),
        ("📅", updated_today, "Hoje"),
    ]
    parts = ['<div class="ml-pl-stat-grid">']
    for ico, val, lbl in items:
        parts.append(
            f'<div class="ml-pl-stat">'
            f'<div class="ml-pl-stat-ico">{ico}</div>'
            f"<h2>{_esc(val)}</h2><span>{_esc(lbl)}</span></div>"
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def _render_quick_filters() -> None:
    active = _filter_key()
    st.markdown('<div class="ml-pl-filter-lbl">Filtros rápidos</div>', unsafe_allow_html=True)
    with st.container(key="ml_pl_filters"):
        cols = st.columns(len(QUICK_FILTERS))
        for col, (key, label, ico) in zip(cols, QUICK_FILTERS):
            with col:
                if st.button(
                    f"{ico} {label}",
                    key=f"ml_pl_filter_{key}",
                    use_container_width=True,
                    type="primary" if active == key else "secondary",
                ):
                    st.session_state.ml_pl_filter = key
                    st.rerun()


def _render_catalog_filter_row(louvores_df: pd.DataFrame) -> tuple[str, list[str], list[str]]:
    from app import LOUVOR_THEMES

    pool = louvores_df.copy() if not louvores_df.empty else pd.DataFrame()
    ritmos = ["Todos"]
    if not pool.empty and "ritmo" in pool.columns:
        ritmos += sorted(
            {str(r).strip() for r in pool["ritmo"].dropna().astype(str) if str(r).strip()}
        )
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.7])
    with c1:
        ritmo = st.selectbox("Ritmo", ritmos, key="ml_pl_f_ritmo", label_visibility="collapsed")
    with c2:
        minist = st.multiselect(
            "Ministração",
            list(LOUVOR_THEMES)[:12],
            key="ml_pl_f_minist",
            placeholder="Ministração",
            label_visibility="collapsed",
        )
    with c3:
        tag = st.multiselect(
            "Tag bíblica",
            list(LOUVOR_THEMES),
            key="ml_pl_f_tag",
            placeholder="Tag bíblica",
            label_visibility="collapsed",
        )
    with c4:
        if st.button("🧹", key="ml_pl_clear_filters", help="Limpar filtros"):
            for k in ("ml_pl_f_ritmo", "ml_pl_f_minist", "ml_pl_f_tag"):
                st.session_state.pop(k, None)
            st.rerun()
    return ritmo, minist, tag


def _render_hub(
    mine: pd.DataFrame,
    fav_ids: set[str],
    louvores_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> None:
    from playlist_ui import compute_playlist_stats

    stats = compute_playlist_stats(mine, louvores_df, fav_ids)
    presets = _distribute_presets(mine, louvores_df)
    n_active = sum(1 for p in presets if p["count"] > 0) or 1

    _render_header()
    _render_hero(n_presets=n_active, n_tracks=len(mine))
    _render_stat_grid(stats, updated_today=_updated_today_count(mine))

    _render_quick_filters()
    ritmo, minist, tag = _render_catalog_filter_row(louvores_df)

    c_search, c_sort = st.columns([3, 1])
    with c_search:
        st.text_input(
            "Buscar playlist",
            key="ml_pl_hub_search",
            placeholder="🔎 Buscar playlist...",
            label_visibility="collapsed",
        )
    with c_sort:
        sort_labels = {"recent": "Recentes", "name": "Nome", "tracks": "Faixas"}
        cur = _sort_key()
        if st.button(f"↕ {sort_labels[cur]}", key="ml_pl_sort_cycle", use_container_width=True):
            order = ["recent", "name", "tracks"]
            st.session_state.ml_pl_sort = order[(order.index(cur) + 1) % len(order)]
            st.rerun()

    filt = _filter_key()
    visible = _filter_presets(presets, filt)
    visible = _search_presets(visible, _search_query())
    visible = [
        p
        for p in visible
        if _match_catalog_filters(p["slice"], louvores_df, ritmo=ritmo, minist=minist, tag=tag)
    ]
    visible = _sort_presets(visible, _sort_key())

    if filt == "favoritas":
        fav_mine = mine[mine["id"].astype(str).isin(fav_ids)].copy()
        if not fav_mine.empty:
            fav_mine["_sort"] = pd.to_datetime(fav_mine["added_at"], errors="coerce")
            fav_mine = fav_mine.sort_values("_sort", ascending=False)
        st.markdown(
            f'<div class="ml-pl-section"><span>⭐ Favoritas ({len(fav_mine)})</span></div>',
            unsafe_allow_html=True,
        )
        if fav_mine.empty:
            st.markdown(
                '<div class="ml-pl-empty">Nenhuma faixa favorita ainda. '
                "Toque em ☆ nas suas músicas.</div>",
                unsafe_allow_html=True,
            )
        else:
            for _, tr in fav_mine.iterrows():
                st.markdown(_favorite_track_html(tr, louvores_df), unsafe_allow_html=True)
                tid = str(tr["id"])
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    if st.button("★", key=f"ml_pl_fav_{tid}", help="Desfavoritar"):
                        from playlist_ui import toggle_favorite

                        toggle_favorite(tid)
                        st.rerun()
                with c2:
                    if st.button("🗑", key=f"ml_pl_rm_fav_{tid}", help="Remover"):
                        from app import PLAYLIST_FILE, save_data

                        updated = playlist_df[playlist_df["id"].astype(str) != tid]
                        save_data(updated, PLAYLIST_FILE)
                        st.rerun()
                with c3:
                    from app import render_playlist_track_links

                    with st.expander("Links", expanded=False):
                        render_playlist_track_links(tr, members_df)
    else:
        st.markdown(
            f'<div class="ml-pl-section"><span>Playlists ({len(visible)})</span></div>',
            unsafe_allow_html=True,
        )
        if not visible:
            st.markdown(
                '<div class="ml-pl-empty">Nenhuma playlist neste filtro. '
                "Adicione músicas do repertório.</div>",
                unsafe_allow_html=True,
            )
        else:
            for idx, preset in enumerate(visible):
                st.markdown(_preset_card_html(preset, idx), unsafe_allow_html=True)
                c_open, c_play = st.columns([4, 0.65])
                with c_open:
                    if st.button(
                        "Abrir playlist",
                        key=f"ml_pl_open_{idx}",
                        use_container_width=True,
                    ):
                        st.session_state.ml_pl_preset_idx = presets.index(preset)
                        _set_view("detail")
                        st.rerun()
                with c_play:
                    with st.container(key=f"ml_pl_open_play_{idx}"):
                        if st.button("▶", key=f"ml_pl_play_{idx}", help="Abrir"):
                            st.session_state.ml_pl_preset_idx = presets.index(preset)
                            _set_view("detail")
                            st.rerun()

    st.markdown(
        """
        <div class="ml-pl-cta">
          <div style="font-size:1.5rem;">🎵</div>
          <div class="ml-pl-cta-text">
            <h3>Adicionar músicas</h3>
            <p>Busque no repertório da igreja e monte sua lista para ensaio.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="ml_pl_add_btn"):
        if st.button("Buscar músicas", key="ml_pl_go_add", use_container_width=True):
            _set_view("add")
            st.rerun()

    st.markdown(
        """
        <div class="ml-pl-cta" style="margin-top:0.35rem;">
          <div style="font-size:1.5rem;">📋</div>
          <div class="ml-pl-cta-text">
            <h3>Criar nova playlist</h3>
            <p>Organize por culto, ensaio ou treino vocal.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="ml_pl_cta_btn"):
        if st.button("Criar playlist", key="ml_pl_go_nova", use_container_width=True):
            _set_view("nova")
            st.rerun()


def _render_detail(
    mine: pd.DataFrame,
    fav_ids: set[str],
    louvores_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> None:
    from app import PLAYLIST_FILE, save_data
    from playlist_ui import toggle_favorite

    presets = _distribute_presets(mine, louvores_df)
    idx = int(st.session_state.get("ml_pl_preset_idx", 0))
    idx = max(0, min(idx, len(presets) - 1))
    preset = presets[idx]
    slice_df = preset["slice"]

    _render_header(show_back=True)
    st.markdown(
        f"""
        <div class="ml-pl-section">
          <span>{_esc(preset["emoji"])} {_esc(preset["name"])}</span>
          <span style="font-size:0.72rem;color:#94a3b8;font-weight:600;">
            {_esc(preset["meta"])}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if slice_df.empty:
        st.markdown(
            '<div class="ml-pl-empty">Nenhuma faixa nesta lista ainda.</div>',
            unsafe_allow_html=True,
        )
        with st.container(key="ml_pl_add_btn"):
            if st.button("Adicionar músicas", key="ml_pl_detail_add", use_container_width=True):
                _set_view("add")
                st.rerun()
        return

    for _, track in slice_df.iterrows():
        st.markdown(_favorite_track_html(track, louvores_df), unsafe_allow_html=True)
        tid = str(track["id"])
        is_fav = tid in fav_ids
        c_fav, c_rm, c_links = st.columns([1, 1, 3])
        with c_fav:
            if st.button("★" if is_fav else "☆", key=f"ml_pl_det_fav_{tid}"):
                toggle_favorite(tid)
                st.rerun()
        with c_rm:
            if st.button("🗑", key=f"ml_pl_det_rm_{tid}"):
                updated = playlist_df[playlist_df["id"].astype(str) != tid]
                save_data(updated, PLAYLIST_FILE)
                st.rerun()
        with c_links:
            from app import render_playlist_track_links

            with st.expander("YouTube · Kit · Cifra", expanded=False):
                render_playlist_track_links(track, members_df)


def _render_add(
    louvores_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
) -> None:
    from app import render_playlist_add_search, themes_from_csv

    _render_header(show_back=True)
    st.markdown(
        '<div class="ml-pl-section"><span>🔍 Adicionar músicas</span></div>',
        unsafe_allow_html=True,
    )

    pool = louvores_df.copy()
    if not pool.empty:
        ritmo = str(st.session_state.get("ml_pl_f_ritmo", "Todos"))
        minist = st.session_state.get("ml_pl_f_minist", [])
        tag = st.session_state.get("ml_pl_f_tag", [])

        def _match_themes(row, tags: list[str]) -> bool:
            if not tags:
                return True
            ts = themes_from_csv(str(row.get("temas", "")))
            return any(t in ts for t in tags)

        if isinstance(minist, list) and minist:
            pool = pool[pool.apply(lambda r: _match_themes(r, minist), axis=1)]
        if isinstance(tag, list) and tag:
            pool = pool[pool.apply(lambda r: _match_themes(r, tag), axis=1)]
        if ritmo != "Todos":
            pool = pool[pool["ritmo"].astype(str) == ritmo]

    with st.container(key="ml_pl_add_box"):
        st.caption("Busque no repertório e toque em ➕ para incluir na playlist.")
    render_playlist_add_search(
        louvores_df,
        playlist_df,
        louvores_pool=pool,
        premium=True,
    )


def _render_nova() -> None:
    _render_header(show_back=True)
    st.markdown(
        '<div class="ml-pl-section"><span>📋 Nova playlist</span></div>',
        unsafe_allow_html=True,
    )
    nome = st.text_input(
        "Nome da playlist",
        placeholder="Ex.: Treino Domingo",
        key="ml_pl_nova_name",
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Criar", type="primary", use_container_width=True, key="ml_pl_nova_create"):
            if nome.strip():
                st.success(f'Playlist "{nome.strip()}" registrada para organização.')
            _set_view("hub")
            st.rerun()
    with c2:
        if st.button("Cancelar", use_container_width=True, key="ml_pl_nova_cancel"):
            _set_view("hub")
            st.rerun()
    st.caption(
        "As faixas ficam na sua playlist pessoal. Use os grupos sugeridos "
        "(Treino, Ensaio, Culto) para organizar o ensaio."
    )


def render_mobile_playlist_page(
    louvores_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> None:
    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_playlist_css()}</style>", unsafe_allow_html=True)
    st.markdown('<div id="ml-playlist-page" class="ml-page">', unsafe_allow_html=True)

    mine, fav_ids = _prepare_mine(playlist_df)
    view = _view()

    if view == "add":
        _render_add(louvores_df, playlist_df)
    elif view == "detail":
        _render_detail(mine, fav_ids, louvores_df, playlist_df, members_df)
    elif view == "nova":
        _render_nova()
    else:
        _render_hub(mine, fav_ids, louvores_df, playlist_df, members_df)

    st.markdown("</div>", unsafe_allow_html=True)
