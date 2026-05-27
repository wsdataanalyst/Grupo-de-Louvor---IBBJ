"""Mobile Lab — Sugestões de louvor premium."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


def mobile_sugestoes_css() -> str:
    return r"""
    body:has(#ml-sugestoes-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-sugestoes-page) .ig-sug-header,
    body:has(#ml-sugestoes-page) .ig-m-hdr-row{ display: none !important; }
    body:has(#ml-sugestoes-page) .ig-m-layout-stack [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
      flex: 1 1 100% !important;
      width: 100% !important;
      max-width: 100% !important;
    }
    body:has(#ml-sugestoes-page) .ig-sug-kpi-row{
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
    body:has(#ml-sugestoes-page) [data-testid="stTabs"] [data-baseweb="tab-list"]{
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
    }
    body:has(#ml-sugestoes-page) .stTextInput > div > div > input,
    body:has(#ml-sugestoes-page) .stTextArea textarea,
    body:has(#ml-sugestoes-page) .stSelectbox > div > div{
      border-radius: 18px !important;
      background: rgba(30,30,30,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    body:has(#ml-sugestoes-page) [class*="st-key-ml_sug_nova"] .stButton > button[kind="primary"]{
      width: 100% !important;
      min-height: 3rem !important;
      border-radius: 22px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #facc15, #eab308) !important;
      color: #0f172a !important;
    }
    """


def _render_header(*, pending: int) -> None:
    badge = (
        f'<span style="color:#fde68a;font-weight:800;"> · {pending} pendente(s)</span>'
        if pending > 0
        else ""
    )
    st.markdown(
        f"""
        <div id="ml-sugestoes-page" class="ml-page">
          <div class="ml-rep-header-card" style="margin-bottom:0.85rem;border-color:rgba(250,204,21,.22);">
            <div class="ml-rep-header-icon" style="background:linear-gradient(135deg,#facc15,#ca8a04);">💡</div>
            <h1 class="ml-rep-header-title" style="font-size:1.5rem;">Sugestões de louvor</h1>
            <p class="ml-rep-header-sub">Envie músicas para análise da liderança{badge}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mobile_sugestoes_page(
    sugestoes_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    from app import count_pending_sugestoes, is_scale_manager, show_sugestao_louvor
    from sugestao_louvor_ui import render_sugestao_nova_button

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_sugestoes_css()}</style>", unsafe_allow_html=True)

    mgr = is_scale_manager(st.session_state.get("user_roles", []))
    pending = (
        count_pending_sugestoes(sugestoes_df) if mgr else 0
    )
    _render_header(pending=pending)

    with st.container(key="ml_sug_nova"):
        render_sugestao_nova_button()

    from mobile_ui import mobile_stack_close, mobile_stack_open

    mobile_stack_open()
    show_sugestao_louvor(sugestoes_df, louvores_df)
    mobile_stack_close()
