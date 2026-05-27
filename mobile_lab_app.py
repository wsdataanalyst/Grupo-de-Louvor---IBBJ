"""App shell do Mobile Lab (modo testes): navegação + telas."""

from __future__ import annotations

import html
from datetime import datetime

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
            ("Repertório", "🎵", 0),
            ("Perfil", "👤", 0),
        ]
    return [
        ("Início", "🏠", 0),
        ("Escalas", "📅", 0),
        ("Repertório", "🎵", 0),
        ("Chat", "💬", max(0, int(chat_unread))),
        ("Perfil", "👤", 0),
    ]


def _drawer_sections() -> list[tuple[str, list[tuple[str, str]]]]:
    """Seções do menu lateral alinhadas ao app web (NAV_GROUP_ORDER)."""
    from app import NAV_GROUP_ORDER, get_menu_items_for_user

    roles = st.session_state.get("user_roles", [])
    items, _, icons = get_menu_items_for_user(roles)
    allowed = {name for name, _, _ in items}
    sections: list[tuple[str, list[tuple[str, str]]]] = []
    for group_label, names in NAV_GROUP_ORDER:
        links: list[tuple[str, str]] = []
        for name in names:
            if name not in allowed:
                continue
            ml_page = _WEB_MENU_TO_ML_PAGE.get(name)
            if not ml_page or ml_page not in LAB_PAGES:
                continue
            links.append((icons.get(name, "•"), ml_page))
        if links:
            sections.append((group_label, links))
    return sections


def _esc(x: object) -> str:
    return html.escape(str(x) if x is not None else "")


def _set_page(p: str) -> None:
    navigate_ml_page(p)


def _drawer_open() -> bool:
    return bool(st.session_state.get("ml_drawer_open"))


def _set_drawer(opened: bool) -> None:
    st.session_state.ml_drawer_open = bool(opened)

def _render_drawer_streamlit(current: str, *, can_gerenciar: bool = False) -> None:
    if not _drawer_open():
        return
    sections = _drawer_sections()

    with st.container(key="ml_drawer_overlay"):
        with st.container(key="ml_drawer_panel"):
            st.markdown(
                "<div style='font-weight:900;font-size:16px;margin:4px 0 10px 0;'>Menu</div>",
                unsafe_allow_html=True,
            )
            if st.button("✕  Fechar", key="ml_drawer_close", use_container_width=True):
                _set_drawer(False)
                st.rerun()

            for group_label, links in sections:
                st.markdown(
                    f"<div style='font-size:0.72rem;font-weight:800;color:rgba(148,163,184,.9);"
                    f"text-transform:uppercase;letter-spacing:0.05em;margin:12px 0 6px 0;'>"
                    f"{_esc(group_label)}</div>",
                    unsafe_allow_html=True,
                )
                for icon, page in links:
                    is_ger = page == "Gerenciar Escalas"
                    wrap_key = (
                        "ml_drawer_gerenciar_active"
                        if is_ger and page == current
                        else "ml_drawer_gerenciar_item"
                        if is_ger
                        else "ml_drawer_active"
                        if page == current
                        else "ml_drawer_item"
                    )
                    btn_type = "primary" if page == current else "secondary"
                    with st.container(key=f"{wrap_key}_{page.replace(' ', '_')}"):
                        if st.button(
                            f"{icon}  {page}",
                            key=f"ml_drawer_nav_{page.replace(' ', '_')}",
                            use_container_width=True,
                            type=btn_type,
                        ):
                            navigate_ml_page(
                                page,
                                pin=(page == "Gerenciar Escalas"),
                            )
                            _set_drawer(False)
                            st.rerun()

            with st.container(key="ml_drawer_logout"):
                if st.button("🚪  Sair do sistema", key="ml_drawer_logout_btn", use_container_width=True):
                    st.session_state._ml_logout = True
                    _set_drawer(False)
                    st.rerun()


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
              Mobile Lab (teste) · {datetime.now().strftime("%d/%m %H:%M")}
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
) -> None:
    """
    Bottom navigation premium — um único nível (botões Streamlit estilizados).

    Navegação interna via session_state (sem links / sem abrir outro navegador).
    """
    from mobile_lab_ui import inject_mobile_lab_hide_streamlit_chrome

    inject_mobile_lab_theme()
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
        for col, (page, icon, badge) in zip(cols, items):
            with col:
                short = {
                    "Início": "Início",
                    "Gerenciar Escalas": "Gerenciar",
                    "Escalas": "Escalas",
                    "Repertório": "Música",
                    "Chat": "Chat",
                    "Perfil": "Perfil",
                }.get(page, page)
                btn_type = "primary" if current == page else "secondary"
                if page == "Gerenciar Escalas" and current != page:
                    btn_type = "secondary"
                label = f"{icon}\n{short}"
                if page == "Chat" and badge > 0:
                    label = f"{icon}\n{short}"
                if page == "Gerenciar Escalas" and current != page:
                    label = f"🎯\n{short}"
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
    inject_mobile_lab_theme()
    _render_page_header("Repertório")
    q = st.text_input("Buscar", placeholder="Nome da música, artista...", key="ml_rep_search")
    df = louvores_df.copy() if louvores_df is not None else pd.DataFrame()
    if not df.empty and q.strip():
        qq = q.strip().lower()
        df = df[
            df.get("title", "").astype(str).str.lower().str.contains(qq)
            | df.get("artist", "").astype(str).str.lower().str.contains(qq)
        ]
    if df.empty:
        st.info("Nenhum louvor encontrado.")
        return
    df = df.head(30)
    for _, r in df.iterrows():
        title = str(r.get("title", "")).strip()
        artist = str(r.get("artist", "")).strip()
        st.markdown(
            f"""
            <div class="ml-page" style="padding-bottom:12px;">
              <div class="ml-glass ml-card" style="display:flex;gap:12px;align-items:center;padding:12px 12px;border-radius:22px;">
                <div style="width:46px;height:46px;border-radius:16px;background:rgba(139,92,246,.14);border:1px solid rgba(139,92,246,.18);display:flex;align-items:center;justify-content:center;font-size:18px;">
                  🎵
                </div>
                <div style="flex:1;min-width:0;">
                  <div style="font-weight:900;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{_esc(title)}</div>
                  <div style="color:rgba(148,163,184,.92);font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{_esc(artist)}</div>
                </div>
                <div style="width:38px;height:38px;border-radius:16px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.10);background:rgba(15,23,42,.55);">❤</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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

