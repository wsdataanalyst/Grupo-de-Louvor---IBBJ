"""Navegação do Mobile Lab — mantém ml_page e URL sincronizados."""

from __future__ import annotations

import streamlit as st

# Nomes do menu web → páginas do mobile lab
APP_MENU_TO_ML_PAGE: dict[str, str] = {
    "Dashboard": "Início",
    "Feed": "Notificações",
    "Avisos": "Notificações",
    "Escalas": "Escalas",
    "Gerenciar Escalas": "Gerenciar Escalas",
    "Repertório": "Repertório",
    "Playlist": "Playlist",
    "Sugestão de louvor": "Sugestões",
    "Chat": "Chat",
    "Perfil": "Perfil",
}

ML_PAGES = frozenset(APP_MENU_TO_ML_PAGE.values())

# Evita voltar para Escalas/Início após salvar dentro de Gerenciar
_PINNED_PAGE_KEY = "_ml_pinned_page"
_NAV_INITIALIZED_KEY = "_ml_nav_initialized"


def is_mobile_lab() -> bool:
    from mobile_lab import is_mobile_lab_enabled

    return is_mobile_lab_enabled()


def _force_gerenciar_from_secrets() -> bool:
    try:
        raw = st.secrets.get("mobile_lab_force_gerenciar", False)
        if isinstance(raw, bool):
            return raw
        return str(raw).strip().lower() in ("1", "true", "yes", "on", "sim")
    except Exception:
        return False


def user_can_gerenciar_escalas() -> bool:
    """Mesmo critério do menu web (líder, organizador, desenvolvedor)."""
    if _force_gerenciar_from_secrets():
        return True
    roles = str(st.session_state.get("user_roles", ""))
    try:
        from app import can_reset_member_passwords, get_menu_items_for_user, is_scale_manager

        if is_scale_manager(roles) or can_reset_member_passwords(roles):
            return True
        items, _, _ = get_menu_items_for_user(roles)
        return any(name == "Gerenciar Escalas" for name, _, _ in items)
    except Exception:
        return False


def sync_ml_can_gerenciar(*, quick_links: list[tuple[str, str]] | None = None) -> bool:
    """Grava na sessão para bottom nav e dashboard usarem o mesmo valor."""
    can = user_can_gerenciar_escalas()
    if not can and quick_links:
        can = any(name == "Gerenciar Escalas" for name, _ in quick_links)
    if quick_links is not None or can:
        st.session_state.ml_can_gerenciar = bool(can)
    return bool(st.session_state.get("ml_can_gerenciar", can))


def pin_ml_page(page: str) -> None:
    """Mantém a página ativa em reruns (ex.: salvar escala em Gerenciar)."""
    if page in ML_PAGES:
        st.session_state[_PINNED_PAGE_KEY] = page
        st.session_state.ml_page = page
        persist_ml_page_query(page)


def unpin_ml_page() -> None:
    st.session_state.pop(_PINNED_PAGE_KEY, None)


def get_pinned_ml_page() -> str:
    p = str(st.session_state.get(_PINNED_PAGE_KEY, "")).strip()
    return p if p in ML_PAGES else ""


def init_ml_navigation() -> None:
    """Inicializa ml_page uma vez por sessão (URL só na primeira carga)."""
    if st.session_state.get(_NAV_INITIALIZED_KEY):
        return
    st.session_state[_NAV_INITIALIZED_KEY] = True

    pinned = get_pinned_ml_page()
    if pinned:
        st.session_state.ml_page = pinned
        persist_ml_page_query(pinned)
        return

    session_p = str(st.session_state.get("ml_page", "")).strip()
    if session_p in ML_PAGES:
        persist_ml_page_query(session_p)
        return

    try:
        raw = st.query_params.get("ml_page", "")
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        qpage = str(raw or "").strip()
    except Exception:
        qpage = ""

    if qpage == "Gerenciar Escalas" and not user_can_gerenciar_escalas():
        qpage = "Início"

    page = qpage if qpage in ML_PAGES else "Início"
    st.session_state.ml_page = page
    persist_ml_page_query(page)


def persist_ml_page_query(page: str) -> None:
    """Grava ml_page na URL para reruns não voltarem à página errada."""
    if page not in ML_PAGES:
        return
    try:
        st.query_params["mobile_lab"] = "1"
        raw = st.query_params.get("ml_page", "")
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        if str(raw) != page:
            st.query_params["ml_page"] = page
    except Exception:
        pass


def navigate_ml_page(page: str, *, pin: bool = False) -> None:
    """Define a página ativa no mobile lab (sessão + URL)."""
    can_ger = bool(st.session_state.get("ml_can_gerenciar")) or user_can_gerenciar_escalas()
    if page == "Gerenciar Escalas" and not can_ger:
        page = "Início"
        unpin_ml_page()
    elif page != "Gerenciar Escalas":
        unpin_ml_page()
    if page not in ML_PAGES:
        page = "Início"
    st.session_state.ml_page = page
    persist_ml_page_query(page)
    if pin or page == "Gerenciar Escalas":
        pin_ml_page(page)


def navigate_app_menu(menu_name: str, **session_updates: object) -> None:
    """
    No mobile lab usa ml_page; no desktop usa app_menu.
    Use em botões que antes faziam st.session_state.app_menu = ...
    """
    if is_mobile_lab():
        target = APP_MENU_TO_ML_PAGE.get(menu_name)
        if target:
            navigate_ml_page(
                target,
                pin=(target == "Gerenciar Escalas"),
            )
        else:
            navigate_ml_page("Início")
    else:
        st.session_state.app_menu = menu_name
    for key, val in session_updates.items():
        st.session_state[key] = val


def read_ml_page() -> str:
    """Página atual: pin > sessão > URL (só se sessão vazia)."""
    init_ml_navigation()

    pinned = get_pinned_ml_page()
    if pinned == "Gerenciar Escalas":
        can_ger = bool(st.session_state.get("ml_can_gerenciar")) or user_can_gerenciar_escalas()
        if can_ger:
            st.session_state.ml_page = pinned
            persist_ml_page_query(pinned)
            return pinned
        unpin_ml_page()

    session_p = str(st.session_state.get("ml_page", "")).strip()

    try:
        raw = st.query_params.get("ml_page", "")
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        qpage = str(raw or "").strip()
    except Exception:
        qpage = ""

    can_ger = bool(st.session_state.get("ml_can_gerenciar")) or user_can_gerenciar_escalas()
    if qpage == "Gerenciar Escalas" and not can_ger:
        qpage = "Início"

    if session_p not in ML_PAGES:
        session_p = qpage if qpage in ML_PAGES else "Início"
        st.session_state.ml_page = session_p
    elif (
        session_p == "Gerenciar Escalas"
        and qpage
        and qpage in ML_PAGES
        and qpage != session_p
    ):
        # URL antiga (ex.: Escalas) não pode tirar o usuário de Gerenciar
        pass

    persist_ml_page_query(session_p)
    return session_p
