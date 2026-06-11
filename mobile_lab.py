"""Layout mobile do app — rollout para usuários autenticados."""

from __future__ import annotations

import streamlit as st

# Beta legado (testes pontuais antes do rollout geral)
_DEFAULT_MOBILE_LAB_BETA_EMAILS: tuple[str, ...] = ("teste@gmail.com",)
_MOBILE_OPT_OUT_KEY = "_mobile_lab_beta_opt_out"


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in ("1", "true", "yes", "on", "sim")


def mobile_lab_beta_emails() -> frozenset[str]:
    """E-mails beta extras (além do rollout geral)."""
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


def mobile_lab_rollout_enabled() -> bool:
    """
    Rollout geral do app mobile para todos os logados.
    Desligue temporariamente com `mobile_lab_rollout = false` nos secrets.
    """
    try:
        if st.secrets.get("mobile_lab_rollout") is not None:
            return _truthy(st.secrets.get("mobile_lab_rollout"))
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    return True


def _activate_mobile_lab_session() -> bool:
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


def apply_mobile_lab_for_beta_user(email: str | None = None) -> bool:
    """Liga mobile lab para e-mails beta (legado / testes)."""
    if not is_mobile_lab_beta_user(email):
        return False
    if st.session_state.get(_MOBILE_OPT_OUT_KEY):
        return False
    return _activate_mobile_lab_session()


def apply_mobile_lab_for_authenticated_user(email: str | None = None) -> bool:
    """Liga o layout mobile após login para qualquer usuário cadastrado."""
    em = str(email or st.session_state.get("user_email", "")).strip()
    if not em or not st.session_state.get("authenticated"):
        return False
    if st.session_state.get(_MOBILE_OPT_OUT_KEY):
        return False
    if mobile_lab_rollout_enabled():
        return _activate_mobile_lab_session()
    return apply_mobile_lab_for_beta_user(email)


def is_mobile_lab_enabled() -> bool:
    """
    Layout mobile ativo quando:
    - sessão mobile_lab ligada (padrão após login)
    - URL: ?mobile_lab=1
    - secrets: mobile_lab = true
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
    """Toggle do layout clássico — apenas desenvolvedores."""
    from user_feedback import is_dev_viewer

    if not is_dev_viewer():
        return
    with st.sidebar.expander("Layout do app", expanded=False):
        st.caption(
            "O app mobile é o padrão para todos os usuários. "
            "Desligue abaixo para testar o layout desktop clássico."
        )
        on = st.toggle(
            "Usar app mobile",
            value=bool(st.session_state.get("mobile_lab")),
            key="mobile_lab_toggle",
        )
        if on != bool(st.session_state.get("mobile_lab")):
            st.session_state.mobile_lab = on
            if on:
                st.session_state.pop(_MOBILE_OPT_OUT_KEY, None)
                try:
                    st.query_params["mobile_lab"] = "1"
                except Exception:
                    pass
                from mobile_lab_nav import sync_ml_can_gerenciar

                sync_ml_can_gerenciar()
            else:
                st.session_state[_MOBILE_OPT_OUT_KEY] = True
                try:
                    del st.query_params["mobile_lab"]
                except Exception:
                    pass
            st.rerun()
