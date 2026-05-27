"""Ambiente de testes do layout mobile (nao afeta producao sem ativar)."""

from __future__ import annotations

import streamlit as st


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in ("1", "true", "yes", "on", "sim")


def is_mobile_lab_enabled() -> bool:
    """
    Ativa preview mobile quando:
    - URL: ?mobile_lab=1
    - secrets.toml: mobile_lab = true
    - session: usuario ligou o toggle na sidebar (dev)
    """
    if _truthy(st.session_state.get("mobile_lab")):
        return True
    try:
        raw = st.query_params.get("mobile_lab", "")
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        if _truthy(raw):
            return True
    except Exception:
        pass
    try:
        if _truthy(st.secrets.get("mobile_lab")):
            return True
    except Exception:
        pass
    return False


def render_mobile_lab_sidebar_toggle() -> None:
    """Toggle para desenvolvedores testarem no app oficial sem branch."""
    from user_feedback import is_dev_viewer

    if not is_dev_viewer():
        return
    with st.sidebar.expander("Laboratorio mobile", expanded=False):
        st.caption("Preview do dashboard estilo app. Oficial continua no layout atual.")
        on = st.toggle(
            "Ativar preview mobile",
            value=bool(st.session_state.get("mobile_lab")),
            key="mobile_lab_toggle",
        )
        if on != bool(st.session_state.get("mobile_lab")):
            st.session_state.mobile_lab = on
            if on:
                try:
                    st.query_params["mobile_lab"] = "1"
                except Exception:
                    pass
                from mobile_lab_nav import sync_ml_can_gerenciar

                sync_ml_can_gerenciar()
            st.rerun()
        st.caption("Ou abra com `?mobile_lab=1` na URL.")
