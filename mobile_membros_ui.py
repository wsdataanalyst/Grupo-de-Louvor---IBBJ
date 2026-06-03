"""Mobile Lab — Integrantes do ministério (mesma lógica do app web)."""

from __future__ import annotations

import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


def render_mobile_membros_page(
    members_df,
    louvores_df,
    escalas_df,
    equipe_df,
) -> None:
    inject_mobile_lab_theme()
    st.markdown('<span id="ml-membros-page" aria-hidden="true"></span>', unsafe_allow_html=True)
    from app import show_members_overview

    show_members_overview(members_df, louvores_df, escalas_df, equipe_df)
