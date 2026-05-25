"""Injeção de HTML no Streamlit — dedent para não virar código; markdown para o CSS global aplicar."""

from __future__ import annotations

import textwrap

import streamlit as st


def html_block(raw: str) -> str:
    """Remove indentação de strings multilinha (evita bloco de código no Markdown)."""
    return textwrap.dedent(raw).strip()


def inject_ui_html(fragment: str, *, sidebar: bool = False) -> None:
    """
    Renderiza HTML com estilos do app (app_theme.css).

    Usa st.markdown + unsafe_allow_html (não st.html), para o CSS global
    atingir marca, avatar, KPIs etc. st.html/isolamento quebrava sidebar e perfil.
    """
    body = fragment.strip() if "\n" not in fragment else html_block(fragment)
    if not body:
        return
    slot = st.sidebar if sidebar else st
    slot.markdown(body, unsafe_allow_html=True)
