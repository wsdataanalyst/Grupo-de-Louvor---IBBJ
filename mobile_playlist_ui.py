"""Mobile Lab — Playlist premium."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


def mobile_playlist_css() -> str:
    return r"""
    body:has(#ml-playlist-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-playlist-page) .ig-pl-header,
    body:has(#ml-playlist-page) .ig-m-hdr-row{ display: none !important; }
    body:has(#ml-playlist-page) .ig-m-layout-stack [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
      flex: 1 1 100% !important;
      width: 100% !important;
      max-width: 100% !important;
    }
    body:has(#ml-playlist-page) .ig-pl-kpi-row{
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
    """


def render_mobile_playlist_page(
    louvores_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> None:
    from app import show_playlist_page
    from mobile_ui import mobile_stack_close, mobile_stack_open

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_playlist_css()}</style>", unsafe_allow_html=True)
    st.markdown(
        """
        <div id="ml-playlist-page" class="ml-page">
          <div class="ml-rep-header-card" style="margin-bottom:0.85rem;border-color:rgba(139,92,246,.22);">
            <div class="ml-rep-header-icon">🎧</div>
            <h1 class="ml-rep-header-title" style="font-size:1.5rem;">Minha playlist</h1>
            <p class="ml-rep-header-sub">Favoritos e músicas para ensaio</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    mobile_stack_open()
    show_playlist_page(louvores_df, playlist_df, members_df)
    mobile_stack_close()
