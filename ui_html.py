"""Injeção de HTML no Streamlit — dedent para não virar código; markdown para o CSS global aplicar."""

from __future__ import annotations

import textwrap

import streamlit as st


def html_block(raw: str) -> str:
    """Remove indentação de strings multilinha (evita bloco de código no Markdown)."""
    return textwrap.dedent(raw).strip()


def inject_page_script(javascript: str) -> None:
    """
    Executa JavaScript no app (documento pai no iframe do Streamlit).

    st.markdown(..., unsafe_allow_html=True) remove <script> e pode exibir o código
  na tela; use esta função para scroll, lightbox e listeners.
    """
    js = javascript.strip()
    if not js:
        return
    wrapped = f"<script>\n{js}\n</script>"
    try:
        st.html(wrapped, unsafe_allow_javascript=True)
        return
    except Exception:
        pass
    import streamlit.components.v1 as components

    components.html(
        "<!DOCTYPE html><html><head>"
        "<style>html,body{margin:0;padding:0;width:0;height:0;overflow:hidden;"
        "opacity:0;visibility:hidden;}</style></head>"
        f"<body>{wrapped}</body></html>",
        height=0,
        scrolling=False,
    )


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
