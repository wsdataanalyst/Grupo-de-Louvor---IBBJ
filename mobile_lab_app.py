"""App shell do Mobile Lab (modo testes): navegação + telas."""

from __future__ import annotations

import html
from datetime import date, datetime

import pandas as pd
import streamlit as st

from mobile_lab_nav import (
    navigate_ml_page,
    read_ml_page,
    user_can_gerenciar_escalas,
)
from mobile_lab_ui import inject_mobile_lab_theme


LAB_PAGES = (
    "Início",
    "Gerenciar Escalas",
    "Escalas",
    "Repertório",
    "Playlist",
    "Chat",
    "Sugestões",
    "Notificações",
    "Perfil",
    "Eventos",
    "Membros",
)


# Mesmos nomes do menu web → páginas do mobile lab
_WEB_MENU_TO_ML_PAGE: dict[str, str] = {
    "Dashboard": "Início",
    "Feed": "Notificações",
    "Escalas": "Escalas",
    "Gerenciar Escalas": "Gerenciar Escalas",
    "Repertório": "Repertório",
    "Playlist": "Playlist",
    "Sugestão de louvor": "Sugestões",
    "Chat": "Chat",
    "Perfil": "Perfil",
    "Eventos": "Eventos",
    "Membros": "Membros",
}


def _lab_nav_items(
    *, can_gerenciar: bool, chat_unread: int
) -> list[tuple[str, str, int]]:
    """
    Bottom nav (5 itens). Liderança: Gerenciar em 2º lugar (destaque dourado).
    """
    if can_gerenciar:
        return [
            ("Início", "🏠", 0),
            ("Gerenciar Escalas", "🎯", 0),
            ("Escalas", "📅", 0),
            ("Chat", "💬", max(0, int(chat_unread))),
            ("Notificações", "📰", 0),
        ]
    return [
        ("Início", "🏠", 0),
        ("Escalas", "📅", 0),
        ("Repertório", "🎵", 0),
        ("Chat", "💬", max(0, int(chat_unread))),
        ("Notificações", "📰", 0),
    ]


# (ícone, rótulo, página ML, permissão web, ação especial)
_DrawerItem = tuple[str, str, str, str | None, str | None]

DRAWER_MENU_SPEC: tuple[tuple[str, tuple[_DrawerItem, ...]], ...] = (
    (
        "NAVEGAÇÃO",
        (
            ("🏠", "Início", "Início", "Dashboard", None),
            ("🎯", "Gerenciar Escalas", "Gerenciar Escalas", "Gerenciar Escalas", None),
            ("📅", "Escalas", "Escalas", "Escalas", None),
            ("🎵", "Música", "Repertório", "Repertório", None),
            ("👥", "Membros", "Membros", "Membros", None),
            ("📖", "Repertório", "Repertório", "Repertório", None),
            ("🎼", "Playlist", "Playlist", "Playlist", None),
            ("💬", "Chat", "Chat", "Chat", None),
            ("📰", "Feed", "Notificações", "Feed", None),
        ),
    ),
    (
        "FERRAMENTAS",
        (
            ("🎤", "Ministração", "Escalas", "Escalas", None),
            ("🎙", "Kit Voz", "", None, "kit_voz"),
            ("⭐", "Favoritas", "Playlist", "Playlist", "favoritas"),
            ("💡", "Sugestões", "Sugestões", "Sugestão de louvor", None),
        ),
    ),
    (
        "COMUNICAÇÃO",
        (
            ("📆", "Eventos", "Eventos", "Eventos", None),
        ),
    ),
    (
        "CONTA",
        (
            ("👤", "Meu Perfil", "Perfil", "Perfil", None),
            ("⚙", "Configurações", "Perfil", "Perfil", "prefs"),
        ),
    ),
)


def mobile_drawer_css() -> str:
    return r"""
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_overlay"]{
      position: fixed !important;
      inset: 0 !important;
      z-index: 2147483500 !important;
      background: rgba(0,0,0,.58) !important;
      backdrop-filter: blur(6px) !important;
      -webkit-backdrop-filter: blur(6px) !important;
      padding: 0 !important;
      margin: 0 !important;
      display: flex !important;
      align-items: stretch !important;
      justify-content: flex-start !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_scrim"]{
      position: fixed !important;
      inset: 0 !important;
      left: min(420px, 85vw) !important;
      z-index: 2147483501 !important;
      width: auto !important;
      height: auto !important;
      margin: 0 !important;
      padding: 0 !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_scrim"] .stButton > button{
      width: 100% !important;
      height: 100vh !important;
      min-height: 100vh !important;
      opacity: 0 !important;
      border: none !important;
      background: transparent !important;
      box-shadow: none !important;
      padding: 0 !important;
      margin: 0 !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"]{
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 85vw !important;
      max-width: 420px !important;
      height: 100vh !important;
      max-height: 100vh !important;
      overflow-y: auto !important;
      -webkit-overflow-scrolling: touch !important;
      background: linear-gradient(180deg, #071633, #091a40, #140f3d) !important;
      border-right: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 0 30px 30px 0 !important;
      box-shadow: 0 10px 40px rgba(0,0,0,.45) !important;
      padding: 18px 18px 24px !important;
      z-index: 2147483502 !important;
      box-sizing: border-box !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_close_wrap"]{
      position: absolute !important;
      top: 14px !important;
      right: 14px !important;
      z-index: 5 !important;
      width: auto !important;
      margin: 0 !important;
      padding: 0 !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_close_wrap"] .stButton > button{
      width: 36px !important;
      height: 36px !important;
      min-height: 36px !important;
      padding: 0 !important;
      border-radius: 50% !important;
      background: rgba(255,255,255,.08) !important;
      border: 1px solid rgba(255,255,255,.12) !important;
      color: #fff !important;
      font-size: 1rem !important;
      font-weight: 700 !important;
      box-shadow: none !important;
    }
    .ml-dr-profile{
      display: flex;
      gap: 14px;
      align-items: flex-start;
      margin: 4px 0 18px;
      padding-right: 2.5rem;
    }
    .ml-dr-avatar{
      width: 72px;
      height: 72px;
      border-radius: 50%;
      flex-shrink: 0;
      object-fit: cover;
      border: 3px solid #6f4cff;
      background: #5f42ff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.75rem;
      font-weight: 800;
      color: #fff;
    }
    .ml-dr-name{
      color: #fff;
      font-size: 1.25rem;
      font-weight: 800;
      line-height: 1.15;
      margin: 0;
    }
    .ml-dr-meta{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.35rem;
      margin-top: 0.35rem;
    }
    .ml-dr-badge{
      display: inline-block;
      padding: 0.12rem 0.5rem;
      border-radius: 999px;
      font-size: 0.62rem;
      font-weight: 700;
      background: #3b0764;
      color: #f3e8ff;
    }
    .ml-dr-online{
      color: #4ade80;
      font-size: 0.72rem;
      font-weight: 700;
    }
    .ml-dr-roles{
      color: #d0d0d0;
      font-size: 0.78rem;
      line-height: 1.45;
      margin: 0.45rem 0 0;
    }
    .ml-dr-level{
      background: linear-gradient(90deg, rgba(120,80,255,.35), rgba(70,40,200,.15));
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 20px;
      padding: 16px 18px;
      margin-bottom: 8px;
    }
    .ml-dr-level-title{
      color: #fff;
      font-size: 1.05rem;
      font-weight: 800;
      margin: 0;
    }
    .ml-dr-level-xp{
      color: #cfcfcf;
      font-size: 0.82rem;
      margin-top: 4px;
    }
    .ml-dr-progress{
      width: 100%;
      height: 10px;
      border-radius: 50px;
      background: #071633;
      margin-top: 12px;
      overflow: hidden;
    }
    .ml-dr-progress-fill{
      height: 100%;
      border-radius: 50px;
      background: linear-gradient(90deg, #7c3aed, #a855f7);
    }
    .ml-dr-section{
      color: #8e9bbd;
      font-size: 0.68rem;
      letter-spacing: 0.14em;
      font-weight: 800;
      margin: 22px 0 10px;
      text-transform: uppercase;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_item_"] .stButton > button,
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_active_"] .stButton > button,
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_gerenciar_"] .stButton > button{
      width: 100% !important;
      min-height: 52px !important;
      padding: 14px 18px !important;
      margin: 0 0 10px !important;
      border-radius: 18px !important;
      background: rgba(255,255,255,.03) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #fff !important;
      font-weight: 700 !important;
      font-size: 0.88rem !important;
      text-align: left !important;
      justify-content: space-between !important;
      box-shadow: none !important;
      transition: transform .2s ease, background .2s ease !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_active_"] .stButton > button{
      background: linear-gradient(90deg, rgba(124,58,237,.6), rgba(124,58,237,.15)) !important;
      border: 1px solid #7c3aed !important;
      box-shadow: 0 0 18px rgba(124,58,237,.18) !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_gerenciar_item_"] .stButton > button{
      border-color: rgba(250,204,21,.28) !important;
      color: #fde68a !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_gerenciar_active_"] .stButton > button{
      background: linear-gradient(135deg, #facc15, #ca8a04) !important;
      color: #0f172a !important;
      border-color: rgba(250,204,21,.45) !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_item_"] .stButton > button::after,
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_active_"] .stButton > button::after,
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_gerenciar_"] .stButton > button::after{
      content: "›";
      font-size: 1.15rem;
      font-weight: 400;
      color: rgba(255,255,255,.55);
      margin-left: 0.5rem;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_logout"] .stButton > button{
      width: 100% !important;
      min-height: 52px !important;
      margin-top: 18px !important;
      border-radius: 18px !important;
      background: linear-gradient(90deg, rgba(160,30,30,.45), rgba(255,50,50,.15)) !important;
      border: 1px solid rgba(255,80,80,.4) !important;
      color: #ff7a7a !important;
      font-weight: 800 !important;
      text-align: center !important;
      justify-content: center !important;
      box-shadow: none !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_kit_link"] .stLinkButton > a{
      display: flex !important;
      align-items: center !important;
      justify-content: space-between !important;
      width: 100% !important;
      min-height: 52px !important;
      padding: 14px 18px !important;
      margin: 0 0 10px !important;
      border-radius: 18px !important;
      background: rgba(255,255,255,.03) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: #fff !important;
      font-weight: 700 !important;
      text-decoration: none !important;
    }
    body:has(#ml-drawer-open) [class*="st-key-ml_drawer_kit_link"] .stLinkButton > a::after{
      content: "›";
      font-size: 1.15rem;
      color: rgba(255,255,255,.55);
    }
    .ml-dr-footer{
      text-align: center;
      color: #8f8f8f;
      margin-top: 18px;
      font-size: 0.72rem;
      line-height: 1.4;
    }
    """


def _drawer_allowed_menus() -> set[str]:
    from app import get_menu_items_for_user

    roles = st.session_state.get("user_roles", [])
    items, _, _ = get_menu_items_for_user(roles)
    allowed = {name for name, _, _ in items}
    if user_can_gerenciar_escalas():
        allowed.add("Gerenciar Escalas")
    return allowed


def _drawer_menu_sections() -> list[tuple[str, list[_DrawerItem]]]:
    allowed = _drawer_allowed_menus()
    sections: list[tuple[str, list[_DrawerItem]]] = []
    for title, items in DRAWER_MENU_SPEC:
        visible: list[_DrawerItem] = []
        for icon, label, ml_page, gate, action in items:
            if action == "kit_voz":
                visible.append((icon, label, ml_page, gate, action))
                continue
            if gate and gate not in allowed:
                continue
            if ml_page and ml_page not in LAB_PAGES and action != "kit_voz":
                continue
            visible.append((icon, label, ml_page, gate, action))
        if visible:
            sections.append((title, visible))
    return sections


def _drawer_user_context() -> dict[str, object]:
    from app import (
        LOUVORES_FILE,
        MEMBER_COLUMNS,
        MEMBERS_FILE,
        PLAYLIST_COLUMNS,
        PLAYLIST_FILE,
        get_current_member_row,
        load_data,
        member_display_name,
        playlist_for_user,
        prepare_members,
        prepare_playlist,
        profile_photo_to_data_uri,
        split_member_roles,
    )
    from escala_member_stats import member_escala_stats
    from mobile_perfil_ui import _badge_for_roles, _gamification, _profile_stats
    from playlist_ui import get_favorite_ids

    members_df = prepare_members(pd.DataFrame(columns=list(MEMBER_COLUMNS)))
    try:
        members_df = prepare_members(load_data(MEMBERS_FILE, MEMBER_COLUMNS))
    except Exception:
        pass

    idx, row = get_current_member_row(members_df)
    kit_url = ""
    photo_uri = ""
    if row is None:
        name = str(
            st.session_state.get("user_full_name")
            or st.session_state.get("user_name")
            or "Integrante"
        )
        photo_uri = profile_photo_to_data_uri(
            str(st.session_state.get("user_email", "")),
            str(st.session_state.get("user_profile_photo", "")).strip(),
        )
        leadership, musician = [], []
        badge = "Membro"
        roles_lines: list[str] = []
        level, xp, xp_max, pct = 1, 0, 1000, 8
    else:
        email = str(row["email"]).strip().lower()
        name = member_display_name(row)
        photo_uri = profile_photo_to_data_uri(
            email, str(row.get("profile_photo", "")).strip()
        )
        leadership, musician = split_member_roles(row.get("roles", ""))
        badge, _ = _badge_for_roles(leadership)
        roles_lines = leadership + musician
        try:
            from voice_kit_links import vocal_nipe_from_roles, voice_kit_youtube_url

            nipe = vocal_nipe_from_roles(str(row.get("roles", "")), bio=str(row.get("bio", "")))
            kit_url = voice_kit_youtube_url(nipe) if nipe else ""
        except Exception:
            kit_url = ""

        playlist_df = prepare_playlist(load_data(PLAYLIST_FILE, PLAYLIST_COLUMNS))
        mine = playlist_for_user(playlist_df, email)
        fav_ids = get_favorite_ids()
        louvores_df = pd.DataFrame()
        try:
            from app import prepare_louvores_with_meta

            louvores_df = prepare_louvores_with_meta(
                load_data(
                    LOUVORES_FILE,
                    ("title", "artist", "key", "youtube_url", "cifra_url", "ritmo", "letter", "source"),
                )
            )
        except Exception:
            pass
        escalas_df = st.session_state.get("_escalas_bundle", (pd.DataFrame(),))[0]
        if not isinstance(escalas_df, pd.DataFrame):
            escalas_df = pd.DataFrame()
        equipe_df = st.session_state.get("_escalas_bundle", (None, None, pd.DataFrame()))[2]
        if not isinstance(equipe_df, pd.DataFrame):
            equipe_df = pd.DataFrame()
        escala_stats = member_escala_stats(email, escalas_df, equipe_df, ref=date.today())
        stats = _profile_stats(mine, louvores_df, fav_ids, escala_stats)
        level, xp, xp_max = _gamification(stats)
        pct = min(100, max(8, int(xp / xp_max * 100))) if xp_max else 8

    initial = (name.strip()[:1] or "?").upper()
    if photo_uri:
        avatar_html = f'<img class="ml-dr-avatar" src="{html.escape(photo_uri)}" alt="" />'
    else:
        avatar_html = f'<div class="ml-dr-avatar">{html.escape(initial)}</div>'

    roles_html = (
        "<br>".join(html.escape(r) for r in roles_lines[:6])
        if roles_lines
        else "Integrante do ministério"
    )

    return {
        "name": name,
        "badge": badge,
        "avatar_html": avatar_html,
        "roles_html": roles_html,
        "level": level,
        "xp": xp,
        "xp_max": xp_max,
        "pct": pct,
        "kit_url": kit_url,
    }


def _drawer_profile_html(ctx: dict[str, object]) -> str:
    return f"""
    <div class="ml-dr-profile">
      {ctx["avatar_html"]}
      <div>
        <p class="ml-dr-name">{html.escape(str(ctx["name"]))}</p>
        <div class="ml-dr-meta">
          <span class="ml-dr-badge">{html.escape(str(ctx["badge"]))}</span>
          <span class="ml-dr-online">● Online</span>
        </div>
        <p class="ml-dr-roles">{ctx["roles_html"]}</p>
      </div>
    </div>
    <div class="ml-dr-level">
      <p class="ml-dr-level-title">⭐ Nível {html.escape(str(ctx["level"]))}</p>
      <p class="ml-dr-level-xp">{html.escape(str(ctx["xp"]))} / {html.escape(str(ctx["xp_max"]))} XP</p>
      <div class="ml-dr-progress">
        <div class="ml-dr-progress-fill" style="width:{int(ctx["pct"])}%;"></div>
      </div>
    </div>
    """


def _esc(x: object) -> str:
    return html.escape(str(x) if x is not None else "")


def _set_page(p: str) -> None:
    navigate_ml_page(p)


def _drawer_open() -> bool:
    return bool(st.session_state.get("ml_drawer_open"))


def _set_drawer(opened: bool) -> None:
    st.session_state.ml_drawer_open = bool(opened)

def _drawer_nav_action(action: str | None, ml_page: str) -> None:
    if action == "favoritas":
        st.session_state.ml_pl_filter = "favoritas"
        st.session_state.ml_pl_view = "hub"
        navigate_ml_page("Playlist")
        return
    if action == "prefs":
        st.session_state.ml_perf_view = "prefs"
        navigate_ml_page("Perfil")
        return
    if ml_page:
        navigate_ml_page(ml_page, pin=(ml_page == "Gerenciar Escalas"))


def _render_drawer_streamlit(current: str, *, can_gerenciar: bool = False) -> None:
    if not _drawer_open():
        return

    ctx = _drawer_user_context()
    st.markdown(
        f"<style>{mobile_drawer_css()}</style>"
        '<span id="ml-drawer-open" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )

    with st.container(key="ml_drawer_overlay"):
        with st.container(key="ml_drawer_scrim"):
            if st.button("Fechar menu", key="ml_drawer_scrim_close"):
                _set_drawer(False)
                st.rerun()

        with st.container(key="ml_drawer_panel"):
            with st.container(key="ml_drawer_close_wrap"):
                if st.button("✕", key="ml_drawer_close"):
                    _set_drawer(False)
                    st.rerun()

            st.markdown(_drawer_profile_html(ctx), unsafe_allow_html=True)

            for section_title, items in _drawer_menu_sections():
                st.markdown(
                    f'<div class="ml-dr-section">{_esc(section_title)}</div>',
                    unsafe_allow_html=True,
                )
                for icon, label, ml_page, _gate, action in items:
                    slug = label.replace(" ", "_").replace("/", "_")
                    is_ger = ml_page == "Gerenciar Escalas"
                    is_active = ml_page == current and action is None
                    if action == "prefs":
                        is_active = current == "Perfil" and str(
                            st.session_state.get("ml_perf_view", "hub")
                        ) == "prefs"
                    if action == "favoritas":
                        is_active = (
                            current == "Playlist"
                            and str(st.session_state.get("ml_pl_filter", "")) == "favoritas"
                        )

                    if action == "kit_voz":
                        url = str(ctx.get("kit_url", "")).strip()
                        if not url:
                            continue
                        with st.container(key=f"ml_drawer_kit_link_{slug}"):
                            st.link_button(
                                f"{icon}  {label}",
                                url,
                                use_container_width=True,
                            )
                        continue

                    if is_ger:
                        wrap = (
                            f"ml_drawer_gerenciar_active_{slug}"
                            if is_active
                            else f"ml_drawer_gerenciar_item_{slug}"
                        )
                    else:
                        wrap = (
                            f"ml_drawer_active_{slug}"
                            if is_active
                            else f"ml_drawer_item_{slug}"
                        )

                    btn_type = "primary" if is_active else "secondary"
                    with st.container(key=wrap):
                        if st.button(
                            f"{icon}  {label}",
                            key=f"ml_drawer_nav_{slug}",
                            use_container_width=True,
                            type=btn_type,
                        ):
                            _drawer_nav_action(action, ml_page)
                            _set_drawer(False)
                            st.rerun()

            with st.container(key="ml_drawer_logout"):
                if st.button(
                    "🚪  Sair da conta",
                    key="ml_drawer_logout_btn",
                    use_container_width=True,
                ):
                    st.session_state._ml_logout = True
                    _set_drawer(False)
                    st.rerun()

            st.markdown(
                '<div class="ml-dr-footer">Versão 2.1.0 • 👑 GDL Gestão de Louvor</div>',
                unsafe_allow_html=True,
            )


def _render_drawer(current: str) -> None:
    if not _drawer_open():
        return
    links = [
        ("🏠", "Início"),
        ("📅", "Escalas"),
        ("🎵", "Repertório"),
        ("🎧", "Playlist"),
        ("💬", "Chat"),
        ("💡", "Sugestões"),
        ("🔔", "Notificações"),
        ("👤", "Perfil"),
    ]
    items = "\n".join(
        f'<button class="ml-drawer-btn { "active" if name == current else "" }" type="button" data-page="{_esc(name)}">{icon} { _esc(name) }</button>'
        for icon, name in links
    )
    st.markdown(
        f"""
        <div class="ml-drawer-overlay" id="ml-drawer">
          <div class="ml-drawer">
            <h3>Menu</h3>
            {items}
            <button class="ml-drawer-btn ml-logout" type="button" data-page="logout">🚪 Sair do sistema</button>
            <div style="margin-top:10px;color:rgba(148,163,184,.92);font-size:12px;">
              Grupo de Louvor IBBJ · {datetime.now().strftime("%d/%m %H:%M")}
            </div>
          </div>
        </div>
        <script>
          (function() {{
            var root = window.parent.document;
            var overlay = root.getElementById("ml-drawer");
            if (!overlay) return;
            overlay.addEventListener("click", function(ev) {{
              if (ev.target === overlay) {{
                var qs = new URLSearchParams(window.parent.location.search);
                qs.set("mobile_lab", "1");
                qs.delete("ml_page");
                window.parent.location.search = qs.toString();
              }}
            }});
            var btns = overlay.querySelectorAll("[data-page]");
            btns.forEach(function(el) {{
              el.addEventListener("click", function(ev) {{
                ev.preventDefault();
                ev.stopPropagation();
                var page = el.getAttribute("data-page");
                if (!page) return;
                var qs = new URLSearchParams(window.parent.location.search);
                qs.set("mobile_lab", "1");
                qs.set("ml_page", page);
                window.parent.location.search = qs.toString();
              }});
            }});
          }})();
        </script>
        """,
        unsafe_allow_html=True,
    )


def mobile_lab_current_page() -> str:
    return read_ml_page()


def render_mobile_lab_nav(
    current: str,
    *,
    chat_unread: int = 0,
    can_gerenciar: bool | None = None,
    badge_pulse: bool = False,
) -> None:
    """
    Bottom navigation premium — um único nível (botões Streamlit estilizados).

    Navegação interna via session_state (sem links / sem abrir outro navegador).
    """
    from mobile_lab_ui import inject_mobile_lab_hide_streamlit_chrome
    from notification_badge import chat_notification_counter_html, notification_badge_css

    inject_mobile_lab_theme()
    st.markdown(f"<style>{notification_badge_css()}</style>", unsafe_allow_html=True)
    inject_mobile_lab_hide_streamlit_chrome()

    # Toggle drawer (menu ☰) sempre disponível
    with st.container(key="ml_drawer_toggle"):
        if st.button("☰", key="ml_drawer_toggle_btn"):
            _set_drawer(not _drawer_open())
            st.rerun()
    if can_gerenciar is None:
        can_gerenciar = bool(st.session_state.get("ml_can_gerenciar"))
        if not can_gerenciar:
            can_gerenciar = user_can_gerenciar_escalas()

    _render_drawer_streamlit(current, can_gerenciar=can_gerenciar)

    items = _lab_nav_items(can_gerenciar=can_gerenciar, chat_unread=chat_unread)

    st.markdown(
        '<span id="ml-bottom-nav-start" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )
    with st.container(key="ml_bottom_nav"):
        cols = st.columns(5, gap="small")
        nav_unread = max(0, int(chat_unread))
        for col, (page, icon, _badge_unused) in zip(cols, items):
            with col:
                short = {
                    "Início": "Início",
                    "Gerenciar Escalas": "Gerenciar",
                    "Escalas": "Escalas",
                    "Repertório": "Música",
                    "Chat": "Chat",
                    "Notificações": "Feed",
                    "Perfil": "Perfil",
                }.get(page, page)
                btn_type = "primary" if current == page else "secondary"
                if page == "Gerenciar Escalas" and current != page:
                    btn_type = "secondary"
                label = f"{icon}\n{short}"
                if page == "Gerenciar Escalas" and current != page:
                    label = f"🎯\n{short}"
                wrap_key = (
                    "ml_nav_chat_wrap"
                    if page == "Chat"
                    else f"ml_nav_{page.replace(' ', '_')}_wrap"
                )
                with st.container(key=wrap_key):
                    if st.button(
                        label,
                        key=f"ml_nav_{page.replace(' ', '_')}",
                        use_container_width=True,
                        type=btn_type,
                    ):
                        navigate_ml_page(
                            page,
                            pin=(page == "Gerenciar Escalas"),
                        )
                        st.rerun()
                    if page == "Chat" and nav_unread > 0:
                        st.markdown(
                            chat_notification_counter_html(
                                nav_unread, pulse=badge_pulse
                            ),
                            unsafe_allow_html=True,
                        )


def _render_page_header(title: str) -> None:
    st.markdown(
        f"""
        <div class="ml-page">
          <div class="ml-top" style="margin-bottom:10px;">
            <div class="ml-user">
              <div class="ml-hello">
                <h1>{_esc(title)}</h1>
                <p>Mobile Lab · visual premium</p>
              </div>
            </div>
            <div class="ml-actions">
              <div class="ml-glass ml-iconbtn" onclick="void(0)">☰</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mobile_lab_escalas(
    *,
    escalas_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    chat_ensaio_df: pd.DataFrame,
) -> None:
    """Delega para o layout premium de Escalas."""
    from mobile_escalas_ui import render_mobile_escalas_page

    render_mobile_escalas_page(
        escalas_df=escalas_df,
        trocas_df=trocas_df,
        members_df=members_df,
        programa_df=programa_df,
        equipe_df=equipe_df,
        louvores_df=louvores_df,
        chat_ensaio_df=chat_ensaio_df,
    )


def render_mobile_lab_repertorio(*, louvores_df: pd.DataFrame) -> None:
    """Delega para o layout premium de Repertório."""
    from mobile_repertorio_ui import render_mobile_repertorio_page

    render_mobile_repertorio_page(louvores_df)


def render_mobile_lab_playlist(*, playlist_df: pd.DataFrame) -> None:
    inject_mobile_lab_theme()
    _render_page_header("Playlist")
    df = playlist_df.copy() if playlist_df is not None else pd.DataFrame()
    if df.empty:
        st.info("Nenhuma playlist encontrada.")
        return
    df = df.head(20)
    for _, r in df.iterrows():
        title = str(r.get("title", "") or r.get("name", "") or "Playlist").strip()
        n = str(r.get("n_items", "") or "").strip()
        meta = f"{n} músicas" if n else "Playlist"
        st.markdown(
            f"""
            <div class="ml-page" style="padding-bottom:12px;">
              <div class="ml-glass ml-card" style="display:flex;gap:12px;align-items:center;padding:12px 12px;border-radius:24px;">
                <div style="width:54px;height:54px;border-radius:18px;background:rgba(37,99,235,.14);border:1px solid rgba(37,99,235,.20);display:flex;align-items:center;justify-content:center;font-size:20px;">
                  🎧
                </div>
                <div style="flex:1;min-width:0;">
                  <div style="font-weight:900;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{_esc(title)}</div>
                  <div style="color:rgba(148,163,184,.92);font-size:12px;">{_esc(meta)}</div>
                </div>
                <div class="ml-glow-purple" style="width:42px;height:42px;border-radius:18px;display:flex;align-items:center;justify-content:center;background:linear-gradient(90deg, rgba(124,58,237,1), rgba(139,92,246,1));font-weight:900;">
                  ▶
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_mobile_lab_chat_list(*, chat_df: pd.DataFrame) -> None:
    inject_mobile_lab_theme()
    _render_page_header("Chat")
    df = chat_df.copy() if chat_df is not None else pd.DataFrame()
    # Mock simples: mostra últimas mensagens
    if df.empty:
        st.info("Sem mensagens ainda.")
        return
    df = df.tail(10)
    for _, r in df.iloc[::-1].iterrows():
        sender = str(r.get("name", "") or r.get("email", "") or "Equipe").strip()
        msg = str(r.get("message", "")).strip()
        st.markdown(
            f"""
            <div class="ml-page" style="padding-bottom:12px;">
              <div class="ml-glass ml-card" style="display:flex;gap:12px;align-items:center;padding:12px;border-radius:24px;">
                <div style="width:46px;height:46px;border-radius:18px;background:rgba(34,197,94,.10);border:1px solid rgba(34,197,94,.18);display:flex;align-items:center;justify-content:center;">👥</div>
                <div style="flex:1;min-width:0;">
                  <div style="font-weight:900;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{_esc(sender)}</div>
                  <div style="color:rgba(148,163,184,.92);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{_esc(msg)}</div>
                </div>
                <div style="min-width:22px;height:22px;border-radius:999px;background:rgba(139,92,246,1);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:900;">•</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def mobile_lab_request_logout() -> bool:
    return bool(st.session_state.pop("_ml_logout", False))

