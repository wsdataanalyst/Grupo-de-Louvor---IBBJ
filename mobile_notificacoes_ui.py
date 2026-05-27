"""Mobile Lab — Notificações / Feed premium."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def mobile_notificacoes_css() -> str:
    return r"""
    body:has(#ml-notificacoes-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-notificacoes-page) .ig-feed-header-card{ display: none !important; }
    body:has(#ml-notificacoes-page) .ig-feed-verse{
      border-radius: 24px !important;
      margin-bottom: 0.85rem !important;
    }
    body:has(#ml-notificacoes-page) .ig-feed-post,
    body:has(#ml-notificacoes-page) .ig-feed-card{
      border-radius: 22px !important;
    }
    body:has(#ml-notificacoes-page) .stTextInput > div > div > input,
    body:has(#ml-notificacoes-page) .stTextArea textarea{
      border-radius: 18px !important;
      background: rgba(30,30,30,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    body:has(#ml-notificacoes-page) [class*="st-key-ml_feed_refresh"] .stButton > button{
      border-radius: 18px !important;
      font-weight: 700 !important;
    }
    body:has(#ml-notificacoes-page) [class*="st-key-ml_feed_new"] .stButton > button[kind="primary"]{
      border-radius: 20px !important;
      font-weight: 800 !important;
    }
    """


def _render_header(*, n_posts: int, is_mgr: bool) -> None:
    sub = "Avisos e comunicados do ministério"
    if is_mgr:
        sub += " · você pode publicar"
    st.markdown(
        f"""
        <div id="ml-notificacoes-page" class="ml-page">
          <div class="ml-rep-header-card" style="margin-bottom:0.85rem;border-color:rgba(59,130,246,.22);">
            <div class="ml-rep-header-icon" style="background:linear-gradient(135deg,#3b82f6,#2563eb);">🔔</div>
            <h1 class="ml-rep-header-title" style="font-size:1.5rem;">Notificações</h1>
            <p class="ml-rep-header-sub">{_esc(sub)} · {n_posts} publicação(ões)</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mobile_notificacoes_page(
    posts_df: pd.DataFrame,
    likes_df: pd.DataFrame,
    comments_df: pd.DataFrame,
) -> None:
    from app import is_scale_manager, show_feed_page

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_notificacoes_css()}</style>", unsafe_allow_html=True)

    is_mgr = is_scale_manager(st.session_state.get("user_roles", []))
    n_posts = 0 if posts_df is None else len(posts_df)
    _render_header(n_posts=n_posts, is_mgr=is_mgr)

    with st.container(key="ml_feed_refresh"):
        if st.button("🔄 Atualizar feed", use_container_width=True):
            st.rerun()

    show_feed_page(posts_df, likes_df, comments_df)
