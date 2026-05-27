"""Mobile Lab — Gerenciar Escalas (menu principal separado de Escalas)."""

from __future__ import annotations

import streamlit as st

from mobile_lab_nav import pin_ml_page, user_can_gerenciar_escalas
from mobile_lab_ui import inject_mobile_lab_theme

GERENCIAR_TAB_KEYS = ("montar", "sugestoes", "sequencia", "pdf", "whatsapp")


def mobile_gerenciar_css() -> str:
    return r"""
    body:has(#ml-gerenciar-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-gerenciar-page) .ig-ger-page{
      max-width: 100% !important;
      margin: 0 !important;
    }
    body:has(#ml-gerenciar-page) .ig-ger-header{ display: none !important; }
    body:has(#ml-gerenciar-page) .ig-m-hdr-row{ display: none !important; }
    body:has(#ml-gerenciar-page) .ig-ger-kpi-row{
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      gap: 0.55rem !important;
    }
    body:has(#ml-gerenciar-page) .ig-m-layout-stack [data-testid="stHorizontalBlock"]{
      flex-wrap: wrap !important;
    }
    body:has(#ml-gerenciar-page) .ig-m-layout-stack [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
      flex: 1 1 100% !important;
      width: 100% !important;
      max-width: 100% !important;
      min-width: 0 !important;
    }
    body:has(#ml-gerenciar-page) .ig-ger-page [data-testid="stHorizontalBlock"] > [data-testid="column"]{
      flex: 1 1 100% !important;
      width: 100% !important;
      max-width: 100% !important;
      min-width: 0 !important;
    }
    body:has(#ml-gerenciar-page) .ig-ger-page [data-testid="stForm"]{
      border: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 16px !important;
      padding: 0.75rem !important;
      background: rgba(15,23,42,.55) !important;
    }
    body:has(#ml-gerenciar-page) [class*="st-key-ml_ger_tab_"] .stButton > button{
      border-radius: 16px !important;
      min-height: 2.55rem !important;
      font-weight: 700 !important;
      font-size: 0.7rem !important;
      white-space: pre-line !important;
      line-height: 1.15 !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(148,163,184,.95) !important;
    }
    body:has(#ml-gerenciar-page) [class*="st-key-ml_ger_tab_"] .stButton > button[kind="primary"]{
      background: linear-gradient(135deg, #facc15, #ca8a04) !important;
      color: #0f172a !important;
      border: none !important;
      box-shadow: 0 0 20px rgba(250,204,21,.22) !important;
    }
    body:has(#ml-gerenciar-page) [class*="st-key-ml_ger_back"] .stButton > button,
    body:has(#ml-gerenciar-page) [class*="st-key-ml_ger_nova"] .stButton > button[kind="primary"]{
      border-radius: 18px !important;
      font-weight: 800 !important;
    }
    body:has(#ml-gerenciar-page) [class*="st-key-ml_ger_nova"] .stButton > button[kind="primary"]{
      background: linear-gradient(135deg, #facc15, #eab308) !important;
      color: #0f172a !important;
      border: none !important;
      box-shadow: 0 0 24px rgba(250,204,21,.2) !important;
    }
    .ml-ger-hero{
      border-radius: 28px;
      padding: 1.15rem 1rem;
      margin-bottom: 0.75rem;
      background: linear-gradient(135deg, rgba(212,175,55,.28), rgba(124,58,237,.2));
      border: 2px solid rgba(250,204,21,.42);
      box-shadow: 0 0 42px rgba(212,175,55,.2);
    }
    .ml-ger-hero h2{ margin: 0; font-size: 1.4rem; font-weight: 900; }
    .ml-ger-hero p{
      margin: 0.35rem 0 0;
      color: rgba(148,163,184,.95);
      font-size: 0.86rem;
      line-height: 1.35;
    }
    .ml-ger-badge{
      display: inline-block;
      margin-bottom: 0.45rem;
      padding: 0.35rem 0.75rem;
      border-radius: 12px;
      background: rgba(250,204,21,.22);
      border: 1px solid rgba(250,204,21,.5);
      color: #fde68a;
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    """


def _render_mobile_header() -> None:
    st.markdown(
        """
        <div id="ml-gerenciar-page" class="ml-page">
          <div class="ml-ger-hero">
            <span class="ml-ger-badge">Menu principal · como no app web</span>
            <h2>🎯 Gerenciar Escalas</h2>
            <p>Montar cultos, equipe, louvores, sequência, PDF e WhatsApp.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_mobile_ger_tab() -> str:
    t = str(st.session_state.get("ml_ger_tab", "montar")).strip()
    return t if t in GERENCIAR_TAB_KEYS else "montar"


def set_mobile_ger_tab(tab: str) -> None:
    if tab in GERENCIAR_TAB_KEYS:
        st.session_state.ml_ger_tab = tab


def apply_pending_ger_tab() -> None:
    """Abre aba PDF/WhatsApp após atalho em outra tela."""
    pending = str(st.session_state.pop("_ml_ger_open_tab", "")).strip().lower()
    if pending in GERENCIAR_TAB_KEYS:
        set_mobile_ger_tab(pending)


def render_mobile_gerenciar_tab_bar() -> str:
    """Barra de abas estilo app (substitui st.tabs no mobile)."""
    from gerenciar_escalas_ui import GERENCIAR_TAB_LABELS

    active = get_mobile_ger_tab()
    short = [
        ("montar", "✨\nMontar"),
        ("sugestoes", "💡\nSugestões"),
        ("sequencia", "🎵\nSequência"),
        ("pdf", "📄\nPDF"),
        ("whatsapp", "💬\nZap"),
    ]
    cols = st.columns(len(short))
    for col, (key, label) in zip(cols, short):
        with col:
            with st.container(key=f"ml_ger_tab_{key}"):
                if st.button(
                    label,
                    key=f"ml_ger_tab_btn_{key}",
                    use_container_width=True,
                    type="primary" if active == key else "secondary",
                ):
                    set_mobile_ger_tab(key)
                    pin_ml_page("Gerenciar Escalas")
                    st.rerun()
    return active


def render_mobile_gerenciar_escalas_page(
    *,
    escalas_df,
    programa_df,
    equipe_df,
    louvores_df,
    members_df,
    chat_ensaio_df,
) -> None:
    """Entrada Mobile Lab — página fixa Gerenciar Escalas."""
    if not user_can_gerenciar_escalas():
        st.warning("Acesso restrito à liderança do ministério.")
        return

    pin_ml_page("Gerenciar Escalas")
    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_gerenciar_css()}</style>", unsafe_allow_html=True)
    apply_pending_ger_tab()

    c_back, c_nova = st.columns([1, 2])
    with c_back:
        with st.container(key="ml_ger_back"):
            if st.button("← Início", use_container_width=True):
                from mobile_lab_nav import navigate_ml_page

                navigate_ml_page("Início")
                st.rerun()
    with c_nova:
        with st.container(key="ml_ger_nova"):
            from gerenciar_escalas_ui import trigger_nova_escala

            if st.button("+ Nova escala", type="primary", use_container_width=True):
                set_mobile_ger_tab("montar")
                pin_ml_page("Gerenciar Escalas")
                trigger_nova_escala()

    _render_mobile_header()
    render_mobile_gerenciar_tab_bar()

    from gerenciar_escalas_ui import gerenciar_escalas_page_css

    st.markdown(
        f"<style>{gerenciar_escalas_page_css()}</style>",
        unsafe_allow_html=True,
    )

    from app import show_gerenciar_escalas

    _ger_kwargs = dict(
        escalas_df=escalas_df,
        programa_df=programa_df,
        equipe_df=equipe_df,
        louvores_df=louvores_df,
        members_df=members_df,
        chat_ensaio_df=chat_ensaio_df,
    )
    try:
        show_gerenciar_escalas(**_ger_kwargs, mobile_shell=True)
    except TypeError:
        # Deploy parcial: app.py antigo sem mobile_shell — is_mobile_lab_enabled() no app trata o mobile
        show_gerenciar_escalas(**_ger_kwargs)
