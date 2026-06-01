"""Ambiente de testes do layout mobile (nao afeta producao sem ativar)."""

from __future__ import annotations

import streamlit as st

# Usuários que entram automaticamente no layout mobile (experiência de membro comum)
_DEFAULT_MOBILE_LAB_BETA_EMAILS: tuple[str, ...] = ("teste@gmail.com",)
_BETA_OPT_OUT_KEY = "_mobile_lab_beta_opt_out"


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in ("1", "true", "yes", "on", "sim")


def mobile_lab_beta_emails() -> frozenset[str]:
    """E-mails com laboratório mobile ligado automaticamente ao entrar."""
    emails = [e.strip().lower() for e in _DEFAULT_MOBILE_LAB_BETA_EMAILS if e.strip()]
    try:
        raw = st.secrets.get("mobile_lab_beta_emails", [])
        if isinstance(raw, str):
            emails.extend(x.strip() for x in raw.split(",") if x.strip())
        elif isinstance(raw, list):
            emails.extend(str(x).strip() for x in raw if str(x).strip())
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    return frozenset(e.lower() for e in emails if e)


def is_mobile_lab_beta_user(email: str | None = None) -> bool:
    em = str(email or st.session_state.get("user_email", "")).strip().lower()
    return bool(em) and em in mobile_lab_beta_emails()


def apply_mobile_lab_for_beta_user(email: str | None = None) -> bool:
    """Liga mobile lab na sessão para usuários beta (ex.: teste@gmail.com)."""
    if not is_mobile_lab_beta_user(email):
        return False
    if st.session_state.get(_BETA_OPT_OUT_KEY):
        return False
    st.session_state.mobile_lab = True
    try:
        st.query_params["mobile_lab"] = "1"
    except Exception:
        pass
    try:
        from mobile_lab_nav import sync_ml_can_gerenciar

        sync_ml_can_gerenciar()
    except Exception:
        pass
    return True


def is_mobile_lab_enabled() -> bool:
    """
    Ativa preview mobile quando:
    - URL: ?mobile_lab=1
    - secrets.toml: mobile_lab = true
    - session: usuario ligou o toggle na sidebar (dev)
    - session mobile_lab ligada (incl. beta apos login)
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
    """Toggle para devs e usuários beta testarem o layout mobile."""
    from user_feedback import is_dev_viewer

    beta = is_mobile_lab_beta_user()
    if not is_dev_viewer() and not beta:
        return
    with st.sidebar.expander("Laboratorio mobile", expanded=beta):
        if beta and not is_dev_viewer():
            st.caption(
                "Você está no **preview mobile** (mesma experiência dos membros). "
                "Desligue abaixo para voltar ao layout clássico."
            )
        else:
            st.caption("Preview do dashboard estilo app. Oficial continua no layout atual.")
        on = st.toggle(
            "Ativar preview mobile",
            value=bool(st.session_state.get("mobile_lab")),
            key="mobile_lab_toggle",
        )
        if on != bool(st.session_state.get("mobile_lab")):
            st.session_state.mobile_lab = on
            if on:
                st.session_state.pop(_BETA_OPT_OUT_KEY, None)
                try:
                    st.query_params["mobile_lab"] = "1"
                except Exception:
                    pass
                from mobile_lab_nav import sync_ml_can_gerenciar

                sync_ml_can_gerenciar()
            else:
                if beta:
                    st.session_state[_BETA_OPT_OUT_KEY] = True
                try:
                    del st.query_params["mobile_lab"]
                except Exception:
                    pass
            st.rerun()
        st.caption("Ou abra com `?mobile_lab=1` na URL.")
