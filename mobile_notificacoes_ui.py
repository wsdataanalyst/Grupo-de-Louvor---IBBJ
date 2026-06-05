"""Mobile Lab — Feed do Ministério (rede social interna)."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme

FEED_FILTERS: tuple[tuple[str, str, str], ...] = (
    ("todas", "Todas", "▦"),
    ("avisos", "Avisos", "📢"),
    ("escalas", "Escalas", "📅"),
    ("ensaios", "Ensaios", "🎤"),
    ("devocionais", "Devocionais", "📖"),
    ("repertorio", "Repertório", "🎵"),
    ("pedidos", "Pedidos", "🙏"),
    ("sugestoes", "Sugestões", "💡"),
)

STORY_ITEMS: tuple[tuple[str, str, str], ...] = (
    ("criar", "Criar\npublicação", "➕"),
    ("avisos", "Avisos", "📢"),
    ("escalas", "Escalas", "📅"),
    ("ensaios", "Ensaios", "🎤"),
    ("devocionais", "Devocionais", "📖"),
    ("louvores", "Louvores", "🎵"),
    ("pedidos", "Pedidos", "🙏"),
    ("sugestoes", "Sugestões", "💡"),
)

_STORY_RING: dict[str, str] = {
    "criar": "linear-gradient(135deg,#7c3aed,#a855f7)",
    "avisos": "linear-gradient(135deg,#7c3aed,#6366f1)",
    "escalas": "linear-gradient(135deg,#3b82f6,#2563eb)",
    "ensaios": "linear-gradient(135deg,#22c55e,#16a34a)",
    "devocionais": "linear-gradient(135deg,#eab308,#ca8a04)",
    "louvores": "linear-gradient(135deg,#ec4899,#db2777)",
    "pedidos": "linear-gradient(135deg,#8b5cf6,#7c3aed)",
    "sugestoes": "linear-gradient(135deg,#f97316,#ea580c)",
}


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def feed_category_matches(row: pd.Series, category: str) -> bool:
    cat = str(category or "").strip().lower()
    if not cat or cat == "todas":
        return True
    pt = str(row.get("post_type", "")).strip().lower()
    blob = f"{row.get('title', '')} {row.get('body', '')}".lower()
    rules: dict[str, tuple[str, ...]] = {
        "avisos": ("comunicado",),
        "escalas": ("evento", "escala", "culto"),
        "ensaios": ("ensaio", "rehearsal"),
        "devocionais": ("devocional", "versículo", "versiculo", "palavra"),
        "repertorio": ("repertório", "repertorio", "louvor", "música", "musica"),
        "pedidos": ("oração", "oracao", "pedido"),
        "sugestoes": ("sugestão", "sugestao"),
    }
    if cat in rules:
        keys = rules[cat]
        return pt in keys or any(k in blob for k in keys)
    return True


def _time_ago(value: object) -> str:
    try:
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return "agora"
        py = dt.to_pydatetime()
        if py.tzinfo:
            py = py.replace(tzinfo=None)
        delta = datetime.now() - py
        mins = int(delta.total_seconds() // 60)
        if mins < 1:
            return "agora"
        if mins < 60:
            return f"há {mins} min"
        hrs = mins // 60
        if hrs < 24:
            return f"há {hrs} hora{'s' if hrs > 1 else ''}"
        days = hrs // 24
        if days < 7:
            return f"há {days} dia{'s' if days > 1 else ''}"
        return py.strftime("%d/%m/%Y")
    except Exception:
        return ""


def mobile_feed_css() -> str:
    return r"""
    body:has(#ml-feed-page) .ig-feed-header-card,
    body:has(#ml-feed-page) .ig-feed-verse { display: none !important; }
    body:has(#ml-feed-page) .ig-feed-page { max-width: 100% !important; margin: 0 !important; }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"]{
      position: sticky !important;
      top: max(0px, env(safe-area-inset-top, 0px)) !important;
      z-index: 2147483590 !important;
      width: 100% !important;
      margin: 0 0 0.45rem !important;
      padding: 0.15rem 0 0.35rem !important;
      background: linear-gradient(180deg, rgba(3,7,18,.96) 70%, rgba(3,7,18,0) 100%) !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      gap: 10px !important;
      width: 100% !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="stColumn"]:nth-child(1),
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="stColumn"]:nth-child(3),
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="column"]:nth-child(1),
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="column"]:nth-child(3){
      flex: 0 0 44px !important;
      width: 44px !important;
      max-width: 44px !important;
      min-width: 44px !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="stColumn"]:nth-child(2),
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="column"]:nth-child(2){
      flex: 1 1 auto !important;
      width: auto !important;
      min-width: 0 !important;
      max-width: none !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [class*="ml_feed_menu"] .stButton > button{
      width: 44px !important;
      min-width: 44px !important;
      height: 44px !important;
      min-height: 44px !important;
      padding: 0 !important;
      border-radius: 14px !important;
      background: rgba(15,23,42,.88) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #f8fafc !important;
      font-size: 1.15rem !important;
      box-shadow: 0 0 16px rgba(0,0,0,.18) !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [class*="ml_feed_new"] .stButton > button{
      width: 44px !important;
      min-width: 44px !important;
      height: 44px !important;
      min-height: 44px !important;
      padding: 0 !important;
      border-radius: 50% !important;
      background: linear-gradient(135deg,#7c3aed,#6d28d9) !important;
      border: none !important;
      color: #fff !important;
      font-size: 1.35rem !important;
      font-weight: 700 !important;
      box-shadow: 0 0 22px rgba(124,58,237,.4) !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="element-container"],
    body:has(#ml-feed-page) [class*="st-key-ml_feed_header_bar"] [data-testid="stButton"]{
      margin: 0 !important;
      padding: 0 !important;
    }
    body:has(#ml-feed-page) .ml-feed-header-inline{
      min-width: 0;
      padding: 0 0.15rem;
    }
    body:has(#ml-feed-page) .ml-feed-header-inline h1{
      margin: 0;
      font-size: 1.12rem;
      font-weight: 900;
      color: #f8fafc;
      letter-spacing: -0.03em;
      line-height: 1.15;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    body:has(#ml-feed-page) .ml-feed-header-inline p{
      margin: 0.12rem 0 0;
      font-size: 0.68rem;
      color: rgba(148,163,184,.95);
      line-height: 1.25;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_search_row"]{
      margin: 0 0 0.5rem !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_search_row"] [data-testid="stTextInput"] input{
      min-height: 42px !important;
      border-radius: 14px !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #e2e8f0 !important;
      font-size: 0.82rem !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_search_row"] [data-testid="stTextInput"] input::placeholder{
      color: rgba(148,163,184,.85) !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_drawer_toggle"]{ display: none !important; }
    body:has(#ml-feed-page) .ml-feed-shell{ margin-top: 0.05rem; }
    body:has(#ml-feed-page) .ml-feed-hscroll{
      display: flex;
      gap: 10px;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      padding: 0.15rem 0 0.65rem;
      margin: 0 -0.15rem 0.5rem;
    }
    body:has(#ml-feed-page) .ml-feed-hscroll::-webkit-scrollbar{ display: none; }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_filter_row"] [data-testid="stHorizontalBlock"]{
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 8px !important;
      padding-bottom: 4px !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_filter_row"] [data-testid="stColumn"],
    body:has(#ml-feed-page) [class*="st-key-ml_feed_filter_row"] [data-testid="column"]{
      flex: 0 0 auto !important;
      width: auto !important;
      min-width: max-content !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_filter_row"] .stButton > button{
      min-height: 2.35rem !important;
      padding: 0.35rem 0.85rem !important;
      border-radius: 999px !important;
      font-size: 0.74rem !important;
      font-weight: 800 !important;
      white-space: nowrap !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(203,213,225,.95) !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_filter_row"] .stButton > button[kind="primary"]{
      background: linear-gradient(135deg,#7c3aed,#6d28d9) !important;
      border: none !important;
      color: #fff !important;
      box-shadow: 0 0 20px rgba(124,58,237,.28) !important;
    }
    body:has(#ml-feed-page) .ml-feed-story{
      text-align: center;
      flex: 0 0 72px;
      min-width: 72px;
    }
    body:has(#ml-feed-page) .ml-feed-story-ring{
      width: 58px;
      height: 58px;
      margin: 0 auto 6px;
      border-radius: 50%;
      padding: 2px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    body:has(#ml-feed-page) .ml-feed-story-ico{
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: rgba(15,23,42,.95);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.35rem;
    }
    body:has(#ml-feed-page) .ml-feed-story span{
      display: block;
      font-size: 0.62rem;
      font-weight: 700;
      color: rgba(203,213,225,.92);
      line-height: 1.15;
      white-space: pre-line;
    }
    body:has(#ml-feed-page) .ml-feed-section-title{
      font-size: 0.92rem;
      font-weight: 900;
      color: #f1f5f9;
      margin: 0.65rem 0 0.55rem;
      letter-spacing: -0.02em;
    }
    body:has(#ml-feed-page) .ml-feed-highlight{
      flex: 0 0 210px;
      min-width: 210px;
      padding: 0.85rem;
      border-radius: 20px;
      background: rgba(12,18,40,.78);
      border: 1px solid rgba(255,255,255,.08);
      backdrop-filter: blur(14px);
      box-shadow: 0 0 24px rgba(88,28,135,.1);
    }
    body:has(#ml-feed-page) .ml-feed-highlight-k{
      font-size: 0.65rem;
      font-weight: 800;
      color: #a78bfa;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 0.35rem;
    }
    body:has(#ml-feed-page) .ml-feed-highlight h4{
      margin: 0 0 0.25rem;
      font-size: 0.88rem;
      font-weight: 800;
      color: #f8fafc;
      line-height: 1.25;
    }
    body:has(#ml-feed-page) .ml-feed-highlight p{
      margin: 0;
      font-size: 0.72rem;
      color: rgba(148,163,184,.95);
      line-height: 1.35;
    }
    body:has(#ml-feed-page) .ml-feed-empty{
      text-align: center;
      padding: 2rem 1.25rem;
      margin: 0.75rem 0 1rem;
      border-radius: 24px;
      background: rgba(12,18,40,.72);
      border: 1px dashed rgba(124,58,237,.28);
      box-shadow: inset 0 0 40px rgba(124,58,237,.06);
    }
    body:has(#ml-feed-page) .ml-feed-empty-ico{
      font-size: 2.5rem;
      margin-bottom: 0.65rem;
    }
    body:has(#ml-feed-page) .ml-feed-empty h3{
      margin: 0 0 0.45rem;
      font-size: 1.05rem;
      font-weight: 900;
      color: #f8fafc;
    }
    body:has(#ml-feed-page) .ml-feed-empty p{
      margin: 0;
      font-size: 0.82rem;
      color: rgba(148,163,184,.95);
      line-height: 1.45;
    }
    body:has(#ml-feed-page) .ig-feed-post-card{
      border-radius: 22px !important;
      background: rgba(12,18,40,.82) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      box-shadow: 0 8px 32px rgba(0,0,0,.22) !important;
      margin-bottom: 0.85rem !important;
      padding: 0.95rem 1rem 0.75rem !important;
    }
    body:has(#ml-feed-page) .ig-feed-post-badge{
      background: rgba(124,58,237,.18) !important;
      color: #c4b5fd !important;
      border-radius: 999px !important;
      padding: 0.18rem 0.55rem !important;
    }
    body:has(#ml-feed-page) .ig-feed-post-card h4{
      font-size: 0.98rem !important;
      font-weight: 800 !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ig_feed_maint"] [data-testid="stExpander"],
    body:has(#ml-feed-page) [class*="st-key-ig_feed_new"] [data-testid="stExpander"]{
      background: rgba(12,18,40,.78) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 20px !important;
    }
    body:has(#ml-feed-page) [class*="st-key-ml_feed_refresh"] .stButton > button{
      border-radius: 18px !important;
      font-weight: 700 !important;
      background: rgba(124,58,237,.12) !important;
      border: 1px solid rgba(124,58,237,.28) !important;
    }
    """


def render_feed_header(*, is_mgr: bool) -> str:
    mgr = " · você pode publicar" if is_mgr else ""
    with st.container(key="ml_feed_header_bar"):
        c_menu, c_title, c_plus = st.columns([0.52, 4.2, 0.52], gap="small")
        with c_menu:
            with st.container(key="ml_feed_menu"):
                if st.button("☰", key="ml_feed_menu_btn"):
                    st.session_state.ml_drawer_open = True
                    st.rerun()
        with c_title:
            st.markdown(
                f"""
                <div class="ml-feed-header-inline">
                  <h1>Feed do Ministério</h1>
                  <p>Acompanhe tudo o que acontece no ministério{mgr}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_plus:
            with st.container(key="ml_feed_new"):
                if st.button("➕", key="ml_feed_new_btn"):
                    st.session_state.ml_feed_new_open = True
                    st.rerun()
    with st.container(key="ml_feed_search_row"):
        st.text_input(
            "Buscar no feed",
            placeholder="🔍 Buscar publicações",
            key="ml_feed_search",
            label_visibility="collapsed",
        )
    return str(st.session_state.get("ml_feed_search", "")).strip()


def render_filters() -> None:
    active = str(st.session_state.get("ml_feed_filter", "todas")).strip().lower()
    with st.container(key="ml_feed_filter_row"):
        cols = st.columns(len(FEED_FILTERS), gap="small")
        for col, (fid, label, icon) in zip(cols, FEED_FILTERS):
            with col:
                btn_type = "primary" if fid == active else "secondary"
                if st.button(
                    f"{icon} {label}",
                    key=f"ml_feed_filt_{fid}",
                    type=btn_type,
                ):
                    st.session_state.ml_feed_filter = fid
                    st.rerun()


def render_story_bar() -> None:
    items_html = []
    for sid, label, icon in STORY_ITEMS:
        ring = _STORY_RING.get(sid, _STORY_RING["avisos"])
        items_html.append(
            f'<div class="ml-feed-story">'
            f'<div class="ml-feed-story-ring" style="background:{ring};">'
            f'<div class="ml-feed-story-ico">{icon}</div></div>'
            f"<span>{_esc(label)}</span></div>"
        )
    st.markdown(
        f'<div class="ml-feed-hscroll ml-feed-stories">{"".join(items_html)}</div>',
        unsafe_allow_html=True,
    )


def render_highlights(posts_df: pd.DataFrame | None) -> None:
    cards: list[str] = []
    try:
        from verse_of_day import verse_for_date

        v = verse_for_date()
        ref = _esc(v.get("ref", ""))
        txt = _esc(str(v.get("text", ""))[:80])
        if txt:
            cards.append(
                f'<div class="ml-feed-highlight">'
                f'<div class="ml-feed-highlight-k">📖 Palavra do dia</div>'
                f"<h4>{ref}</h4><p>{txt}…</p></div>"
            )
    except Exception:
        pass

    df = posts_df.copy() if posts_df is not None and not posts_df.empty else pd.DataFrame()
    if not df.empty:
        df = df.copy()
        df["_sort"] = pd.to_datetime(df.get("created_at"), errors="coerce")
        df = df.sort_values("_sort", ascending=False).head(4)
        for _, row in df.iterrows():
            pt = str(row.get("post_type", "")).strip().lower()
            title = _esc(row.get("title", "Publicação"))
            when = _esc(_time_ago(row.get("created_at")))
            if pt == "evento" or "escala" in str(row.get("title", "")).lower():
                kicker = "📅 Escala"
            elif pt == "comunicado":
                kicker = "📢 Aviso"
            else:
                kicker = "📰 Novidade"
            cards.append(
                f'<div class="ml-feed-highlight">'
                f'<div class="ml-feed-highlight-k">{kicker} · {when}</div>'
                f"<h4>{title}</h4>"
                f'<p>{_esc(str(row.get("body", ""))[:70])}…</p></div>'
            )

    if not cards:
        cards.append(
            '<div class="ml-feed-highlight">'
            '<div class="ml-feed-highlight-k">⭐ Destaques</div>'
            "<h4>Bem-vindo ao feed</h4>"
            "<p>Publicações e avisos aparecerão aqui.</p></div>"
        )

    st.markdown(
        '<div class="ml-feed-section-title">⭐ Destaques</div>'
        f'<div class="ml-feed-hscroll">{"".join(cards[:5])}</div>',
        unsafe_allow_html=True,
    )


def render_empty_feed() -> None:
    st.markdown(
        """
        <div class="ml-feed-empty">
          <div class="ml-feed-empty-ico">🚀</div>
          <h3>Nenhuma publicação ainda</h3>
          <p>Assim que líderes publicarem avisos, escalas, devocionais ou comunicados,
          eles aparecerão aqui.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_post_card(
    *,
    avatar: str,
    author: str,
    category: str,
    when: str,
    title: str,
    body: str = "",
) -> None:
    """Card HTML decorativo (posts reais usam render_feed_post_card do app)."""
    st.markdown(
        f"""
        <div class="ig-feed-post-card">
          <div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:8px;">
            <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#3b82f6);
              display:flex;align-items:center;justify-content:center;font-size:1.1rem;">{_esc(avatar)}</div>
            <div style="flex:1;min-width:0;">
              <div style="font-weight:800;color:#f8fafc;font-size:0.88rem;">{_esc(author)}</div>
              <div style="font-size:0.72rem;color:rgba(148,163,184,.95);">{_esc(when)} · {_esc(category)}</div>
            </div>
          </div>
          <h4>{_esc(title)}</h4>
          {f'<p style="margin:0.35rem 0 0;font-size:0.84rem;color:rgba(226,232,240,.92);line-height:1.45;">{_esc(body)}</p>' if body else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _filter_posts_df(
    posts_df: pd.DataFrame,
    *,
    category_filter: str,
    search: str,
) -> pd.DataFrame:
    df = posts_df.copy()
    if df.empty:
        return df
    q = str(search or "").strip().lower()
    if q:
        df = df[
            df.get("title", "").astype(str).str.lower().str.contains(q, na=False)
            | df.get("body", "").astype(str).str.lower().str.contains(q, na=False)
        ]
    cat = str(category_filter or "todas").strip().lower()
    if cat and cat != "todas":
        df = df[df.apply(lambda row: feed_category_matches(row, cat), axis=1)]
    df["_sort"] = pd.to_datetime(df.get("created_at"), errors="coerce")
    return df.sort_values("_sort", ascending=False)


def _render_mobile_feed_body(
    posts_df: pd.DataFrame,
    likes_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    *,
    category_filter: str,
    search: str,
) -> None:
    """Conteúdo interativo do feed mobile — não depende de show_feed_page(shell=...)."""
    from app import (
        DATA_DIR,
        FEED_IMAGES_DIR,
        append_feed_post,
        is_scale_manager,
        load_feed_bundle,
        paginate_dataframe,
        purge_all_feed_data,
        render_feed_post_card,
        save_feed_image_file,
        show_form_error,
    )

    if is_scale_manager(st.session_state.user_roles):
        with st.expander("Manutenção do feed (líderes)", expanded=False, key="ig_feed_maint"):
            st.caption(
                "Apaga **todos** os posts, curtidas e comentários. Use se o feed estiver "
                "duplicado ou deixando o app lento."
            )
            if st.button("🗑️ Apagar todo o feed agora", key="feed_purge_all_btn"):
                n = purge_all_feed_data()
                st.success(f"Feed limpo ({n} publicação(ões) removida(s)).")
                st.rerun()

    new_expanded = bool(st.session_state.pop("ml_feed_new_open", False))
    with st.expander("Nova publicação", expanded=new_expanded, key="ig_feed_new"):
        with st.form(key="feed_post_form"):
            titulo = st.text_input("Título")
            corpo = st.text_area("Mensagem")
            tipo_opts = ["comunicado", "evento"]
            tipo = st.selectbox(
                "Tipo",
                tipo_opts,
                format_func=lambda x: "📢 Comunicado" if x == "comunicado" else "📅 Evento",
            )
            yt = st.text_input("Link YouTube (opcional)")
            img_url = st.text_input("URL da imagem (opcional)")
            img_file = st.file_uploader(
                "Ou envie uma imagem",
                type=["jpg", "jpeg", "png", "webp"],
                key="feed_post_img_up",
            )
            pub = st.form_submit_button("Publicar no feed", type="primary")
            if pub:
                if not titulo.strip() or not corpo.strip():
                    show_form_error("Informe título e mensagem.")
                else:
                    image_ref = img_url.strip()
                    if img_file is not None:
                        image_ref = save_feed_image_file(img_file, DATA_DIR, FEED_IMAGES_DIR)
                    append_feed_post(
                        post_type=tipo,
                        title=titulo.strip(),
                        body=corpo.strip(),
                        youtube_url=yt.strip(),
                        author_email=st.session_state.user_email,
                        author_name=st.session_state.user_full_name
                        or st.session_state.user_name,
                        image_url=image_ref,
                    )
                    st.success("Publicado no feed!")
                    st.rerun()

    live_posts, live_likes, live_comments = load_feed_bundle()
    df = _filter_posts_df(
        live_posts if live_posts is not None else posts_df,
        category_filter=category_filter,
        search=search,
    )
    if df.empty:
        return

    page_df = paginate_dataframe(df, 8, "feed_posts")
    for _, post in page_df.iterrows():
        render_feed_post_card(
            post,
            live_likes if live_likes is not None else likes_df,
            live_comments if live_comments is not None else comments_df,
            key_prefix=f"feed_{post['id']}",
        )


def render_feed(
    posts_df: pd.DataFrame,
    likes_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    *,
    is_mgr: bool,
) -> None:
    search = render_feed_header(is_mgr=is_mgr)
    render_filters()
    render_story_bar()
    render_highlights(posts_df)

    n_posts = 0 if posts_df is None else len(posts_df)
    cat = str(st.session_state.get("ml_feed_filter", "todas"))
    if n_posts == 0:
        render_empty_feed()
    else:
        filtered = posts_df.copy()
        q = search.strip().lower()
        if q:
            filtered = filtered[
                filtered.get("title", "").astype(str).str.lower().str.contains(q, na=False)
                | filtered.get("body", "").astype(str).str.lower().str.contains(q, na=False)
            ]
        if cat != "todas":
            filtered = filtered[filtered.apply(lambda r: feed_category_matches(r, cat), axis=1)]
        if filtered.empty:
            render_empty_feed()

    with st.container(key="ml_feed_refresh"):
        if st.button("🔄 Atualizar feed", use_container_width=True):
            st.rerun()

    _render_mobile_feed_body(
        posts_df,
        likes_df,
        comments_df,
        category_filter=cat,
        search=search,
    )


def render_mobile_notificacoes_page(
    posts_df: pd.DataFrame,
    likes_df: pd.DataFrame,
    comments_df: pd.DataFrame,
) -> None:
    from app import is_scale_manager

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_feed_css()}</style>", unsafe_allow_html=True)
    st.markdown(
        '<div id="ml-feed-page" class="ml-page ml-feed-shell"></div>',
        unsafe_allow_html=True,
    )

    is_mgr = is_scale_manager(st.session_state.get("user_roles", []))
    render_feed(posts_df, likes_df, comments_df, is_mgr=is_mgr)
