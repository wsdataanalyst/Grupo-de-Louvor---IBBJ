"""App shell do Mobile Lab (modo testes): navegação + telas."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


LAB_PAGES = (
    "Início",
    "Escalas",
    "Repertório",
    "Playlist",
    "Chat",
    "Sugestões",
    "Notificações",
    "Perfil",
)


def _esc(x: object) -> str:
    return html.escape(str(x) if x is not None else "")


def _get_page() -> str:
    p = str(st.session_state.get("ml_page", "")).strip()
    return p if p in LAB_PAGES else "Início"


def _set_page(p: str) -> None:
    st.session_state.ml_page = p


def _drawer_open() -> bool:
    return bool(st.session_state.get("ml_drawer_open"))


def _set_drawer(opened: bool) -> None:
    st.session_state.ml_drawer_open = bool(opened)

def _render_drawer_streamlit(current: str) -> None:
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

    with st.container(key="ml_drawer_overlay"):
        with st.container(key="ml_drawer_panel"):
            st.markdown(
                "<div style='font-weight:900;font-size:16px;margin:4px 0 10px 0;'>Menu</div>",
                unsafe_allow_html=True,
            )
            if st.button("✕  Fechar", key="ml_drawer_close", use_container_width=True):
                _set_drawer(False)
                st.rerun()

            for icon, page in links:
                wrap_key = "ml_drawer_active" if page == current else "ml_drawer_item"
                with st.container(key=f"{wrap_key}_{page}"):
                    if st.button(
                        f"{icon}  {page}",
                        key=f"ml_drawer_nav_{page.replace(' ', '_')}",
                        use_container_width=True,
                    ):
                        st.session_state.ml_page = page
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


def _sync_page_from_query() -> None:
    try:
        raw = st.query_params.get("ml_page", "")
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        page = str(raw or "").strip()
        if page and page in LAB_PAGES:
            st.session_state.ml_page = page
        if page == "logout":
            st.session_state._ml_logout = True
    except Exception:
        pass


def mobile_lab_current_page() -> str:
    _sync_page_from_query()
    return _get_page()


def render_mobile_lab_nav(current: str, *, chat_unread: int = 0) -> None:
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
    _render_drawer_streamlit(current)

    items = [
        ("Início", "🏠", 0),
        ("Escalas", "📅", 0),
        ("Repertório", "🎵", 0),
        ("Chat", "💬", max(0, int(chat_unread))),
        ("Perfil", "👤", 0),
    ]

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
                    "Escalas": "Escalas",
                    "Repertório": "Música",
                    "Chat": "Chat",
                    "Perfil": "Perfil",
                }.get(page, page)
                label = f"{icon}\n{short}"
                if page == "Chat" and badge > 0:
                    label = f"{icon}\n{short}"
                if st.button(
                    label,
                    key=f"ml_nav_{page.replace(' ', '_')}",
                    use_container_width=True,
                    type="primary" if current == page else "secondary",
                ):
                    st.session_state.ml_page = page
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


def render_mobile_lab_escalas(*, escalas_df: pd.DataFrame, my_role: str = "") -> None:
    inject_mobile_lab_theme()
    _render_page_header("Escalas")
    # Cards simples: próximos cultos
    df = escalas_df.copy() if escalas_df is not None else pd.DataFrame()
    if not df.empty:
        df["_dt"] = pd.to_datetime(df.get("date"), errors="coerce")
        df = df[df["_dt"].notna()].sort_values("_dt").head(8)
    if df.empty:
        st.info("Nenhuma escala encontrada.")
        return
    for _, r in df.iterrows():
        dt = r["_dt"].to_pydatetime()
        ev = str(r.get("event", "Culto")).strip() or "Culto"
        st.markdown(
            f"""
            <div class="ml-page" style="padding-bottom:16px;">
              <div class="ml-glass ml-card" style="padding:14px 14px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                  <span style="color:rgba(226,232,240,.92);font-weight:900;font-size:12px;">
                    {dt.strftime("%a").upper()} • {dt.strftime("%d/%m")}
                  </span>
                  <span class="ml-glass" style="padding:6px 10px;border-radius:14px;font-size:12px;color:rgba(134,239,172,.95);border-color:rgba(34,197,94,.18);">
                    Status
                  </span>
                </div>
                <div style="font-size:18px;font-weight:900;letter-spacing:-0.01em;">{_esc(ev)}</div>
                <div style="margin-top:6px;color:rgba(148,163,184,.92);font-size:13px;">
                  Você • {_esc(my_role or 'Integrante')}
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
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
    _sync_page_from_query()
    return bool(st.session_state.pop("_ml_logout", False))

