"""Injeção de HTML no Streamlit sem virar bloco de código (sem indentação extra)."""

from __future__ import annotations

import textwrap

import streamlit as st


def html_block(raw: str) -> str:
    """Remove indentação de strings multilinha para o Markdown não tratar como código."""
    return textwrap.dedent(raw).strip()


def inject_ui_html(fragment: str, *, sidebar: bool = False) -> None:
    body = html_block(fragment) if "\n" in fragment else fragment.strip()
    if not body:
        return
    slot = st.sidebar if sidebar else st
    try:
        slot.html(body)
    except Exception:
        slot.markdown(body, unsafe_allow_html=True)
