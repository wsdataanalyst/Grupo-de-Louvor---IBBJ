"""Mensagens ao usuário: leves para o ministério; detalhes só para desenvolvedores."""

from __future__ import annotations

import os
import traceback

import streamlit as st

MSG_IMPROVEMENTS = (
    "Estamos trabalhando em melhorias. Tente novamente em instantes — "
    "obrigado pela paciência! 🎵"
)


def _developer_emails() -> frozenset[str]:
    emails = ["wsdataanalyst", "willsousaa7x@gmail.com"]
    extra = os.environ.get("DEVELOPER_EMAILS", "")
    if extra.strip():
        emails.extend(e.strip() for e in extra.split(",") if e.strip())
    try:
        from_secrets = st.secrets.get("developer_emails", [])
        if isinstance(from_secrets, str):
            emails.append(from_secrets)
        elif isinstance(from_secrets, list):
            emails.extend(from_secrets)
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    return frozenset(e.strip().lower() for e in emails if e and str(e).strip())


def is_dev_viewer() -> bool:
    """Desenvolvedor logado (wsdataanalyst, willsousaa7x@gmail.com ou papel Desenvolvedor)."""
    email = str(st.session_state.get("user_email", "")).strip().lower()
    if email and email in _developer_emails():
        return True
    roles = str(st.session_state.get("user_roles", "")).lower()
    return "desenvolvedor" in roles


def _show_explicit_errors() -> bool:
    """Na tela de login (sem sessão) ou desenvolvedor: mostrar erro real, não mensagem genérica."""
    if not st.session_state.get("authenticated"):
        return True
    return is_dev_viewer()


def show_technical_error(detail: str = "") -> None:
    """Falha de sistema / gravação."""
    text = (detail or "Erro técnico (sem detalhe).").strip()
    if _show_explicit_errors():
        st.error(text)
    else:
        st.info(MSG_IMPROVEMENTS)
        with st.expander("Detalhe do erro (envie ao suporte)", expanded=False):
            st.code(text)


def show_form_error(detail: str) -> None:
    """Validação de formulário."""
    detail = detail.strip()
    if not detail:
        return
    st.warning(detail)


def show_exception_error(
    exc: BaseException,
    *,
    context: str = "",
    user_hint: str = "",
) -> None:
    """Exceção inesperada."""
    detail = f"{context}: {exc}".strip(": ") if context else str(exc)
    hint = (user_hint or detail or type(exc).__name__).strip()
    if _show_explicit_errors():
        st.error(hint)
        with st.expander("Detalhes técnicos (traceback)", expanded=True):
            st.code(traceback.format_exc())
    else:
        st.info(user_hint.strip() or MSG_IMPROVEMENTS)
        with st.expander("Detalhe do erro (envie ao suporte)", expanded=False):
            st.code(traceback.format_exc())
