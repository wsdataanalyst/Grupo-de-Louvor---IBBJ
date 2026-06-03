"""Mobile Lab — Eventos do ministério (mesma lógica do app web)."""

from __future__ import annotations

import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


def render_mobile_eventos_page(
    eventos_df,
    members_df,
) -> None:
    inject_mobile_lab_theme()
    st.markdown('<span id="ml-eventos-page" aria-hidden="true"></span>', unsafe_allow_html=True)
    from app import show_eventos_page

    show_eventos_page(eventos_df, members_df)
