"""CSS e utilitários mobile-first — prioridade smartphone (IBBJ Louvor)."""

from __future__ import annotations

import streamlit as st

from ui_html import inject_ui_html

# Breakpoints alinhados ao app_theme (mobile ≤768px)
MOBILE_MAX_PX = 768
MOBILE_SM_MAX_PX = 480


def mobile_first_css() -> str:
    return f"""
        /* ========== Mobile-first (≤{MOBILE_MAX_PX}px) ========== */
        @media (max-width: {MOBILE_MAX_PX}px) {{
            :root {{
                --ig-content-pad-x: 0.75rem;
                --ig-mobile-pad-bottom: calc(1.5rem + env(safe-area-inset-bottom, 0px));
            }}

            [data-testid="stAppViewContainer"]:not(:has(.login-page)) .main .block-container,
            [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMain"] .block-container {{
                padding-left: var(--ig-content-pad-x) !important;
                padding-right: var(--ig-content-pad-x) !important;
                padding-bottom: var(--ig-mobile-pad-bottom) !important;
                max-width: 100% !important;
            }}

            /* Sidebar em gaveta — não roubar largura do conteúdo */
            section[data-testid="stSidebar"] {{
                min-width: 0 !important;
                max-width: min(18rem, 88vw) !important;
                width: min(18rem, 88vw) !important;
            }}

            /* Colunas Streamlit: empilhar (conteúdo principal primeiro) */
            [data-testid="stAppViewContainer"]:not(:has(.login-page))
                [data-testid="stMain"] [data-testid="stHorizontalBlock"] {{
                flex-wrap: wrap !important;
                gap: 0.65rem !important;
                width: 100% !important;
            }}
            [data-testid="stAppViewContainer"]:not(:has(.login-page))
                [data-testid="stMain"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                flex: 1 1 100% !important;
                width: 100% !important;
                min-width: 0 !important;
                max-width: 100% !important;
            }}

            /* Mobile Lab: bottom nav — 5 itens em linha (não empilhar) */
            body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] [data-testid="stHorizontalBlock"] {{
                flex-wrap: nowrap !important;
                width: 100% !important;
            }}
            body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                flex: 1 1 0 !important;
                width: 20% !important;
                max-width: 20% !important;
                min-width: 0 !important;
            }}

            /* Mobile Lab Escalas: abas horizontais */
            body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stHorizontalBlock"] {{
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
            }}
            body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                flex: 0 0 auto !important;
                width: auto !important;
                max-width: none !important;
                min-width: max-content !important;
            }}

            /* Linhas que devem ficar lado a lado (2 colunas no máximo) */
            .ig-m-row-2 [data-testid="stHorizontalBlock"] {{
                flex-wrap: nowrap !important;
            }}
            .ig-m-row-2 [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                flex: 1 1 50% !important;
                width: auto !important;
                max-width: 50% !important;
            }}

            /* Cabeçalhos título + botão */
            .ig-m-hdr-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {{
                flex: 0 0 auto !important;
                width: 100% !important;
                max-width: 100% !important;
            }}
            .ig-m-hdr-row [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child .stButton > button {{
                width: 100% !important;
            }}

            /* Dashboard: painel direito não fixo */
            [data-testid="column"]:has(.ig-right-panel) {{
                position: static !important;
                top: auto !important;
            }}

            /* Chat: ordem mobile — conversa → lista → info */
            .ig-chat-mobile-order > [data-testid="stHorizontalBlock"] {{
                display: flex !important;
                flex-direction: column !important;
            }}
            .ig-chat-mobile-order > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {{
                order: 2;
            }}
            .ig-chat-mobile-order > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {{
                order: 1;
            }}
            .ig-chat-mobile-order > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {{
                order: 3;
            }}
            .ig-chat-col--list {{
                min-height: auto !important;
                max-height: 42vh;
            }}
            #chat-scroll-box.ig-chat-feed {{
                min-height: 38vh !important;
                max-height: 50vh !important;
            }}

            /* Páginas premium — largura total */
            .ig-sug-page, .ig-pl-page, .ig-chat-page, .ig-rep-page,
            .ig-esc-ge-page, .ig-escalas-page, .ig-feed-page {{
                max-width: 100% !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
                padding-left: 0 !important;
                padding-right: 0 !important;
            }}

            /* KPIs e grids */
            .ig-sug-kpi-row, .ig-pl-kpi-row, .ig-rep-kpi-row {{
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
                gap: 0.55rem !important;
            }}
            [data-testid="stHorizontalBlock"]:has([class*="st-key-ig_metric"]) {{
                flex-wrap: wrap !important;
            }}
            [data-testid="stHorizontalBlock"]:has([class*="st-key-ig_metric"])
                > [data-testid="stColumn"] {{
                flex: 1 1 calc(50% - 0.35rem) !important;
                width: calc(50% - 0.35rem) !important;
                max-width: calc(50% - 0.35rem) !important;
            }}

            /* Hero e títulos */
            .ig-hero-title, .ig-sug-header-title, .ig-pl-header-title,
            .ig-chat-header-title, .ig-rep-header-title {{
                font-size: 1.2rem !important;
            }}
            .ig-hero-card, .ig-sug-header, .ig-pl-header, .ig-chat-header {{
                padding: 1rem !important;
            }}
            .ig-hero-verse {{
                max-width: 100% !important;
                margin-top: 0.65rem;
            }}

            /* Abas e rádios */
            [data-testid="stTabs"] [data-baseweb="tab-list"] {{
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
                gap: 0.25rem !important;
            }}
            div[data-testid="stRadio"] > div {{
                flex-wrap: wrap !important;
                gap: 0.35rem !important;
            }}

            /* Toque confortável */
            [data-testid="stMain"] .stButton > button,
            [data-testid="stMain"] button[kind="primary"],
            [data-testid="stMain"] [data-testid="stLinkButton"] > a {{
                min-height: 2.75rem !important;
            }}
            input, textarea, select, [data-testid="stChatInput"] textarea {{
                font-size: 16px !important;
            }}

            /* Tabelas e dataframes */
            [data-testid="stDataFrame"] {{
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
            }}

            /* Acesso rápido — 2 colunas */
            .ig-quick-grid-open [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                flex: 1 1 calc(50% - 0.35rem) !important;
                width: calc(50% - 0.35rem) !important;
                max-width: calc(50% - 0.35rem) !important;
            }}

            /* Player / faixas playlist */
            .ig-pl-track-row, .ig-rep-table-row {{
                flex-wrap: wrap !important;
            }}
        }}

        @media (max-width: {MOBILE_SM_MAX_PX}px) {{
            .ig-sug-kpi-row, .ig-pl-kpi-row, .ig-rep-kpi-row {{
                grid-template-columns: 1fr !important;
            }}
            [data-testid="stHorizontalBlock"]:has([class*="st-key-ig_metric"])
                > [data-testid="stColumn"] {{
                flex: 1 1 100% !important;
                width: 100% !important;
                max-width: 100% !important;
            }}
            .ig-quick-grid-open [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
                flex: 1 1 100% !important;
                width: 100% !important;
                max-width: 100% !important;
            }}
        }}
    """


def mobile_stack_open() -> None:
    """Marca bloco cujas colunas Streamlit devem empilhar no celular."""
    inject_ui_html('<div class="ig-m-layout-stack">')


def mobile_stack_close() -> None:
    inject_ui_html("</div>")


def mobile_hdr_open() -> None:
    inject_ui_html('<div class="ig-m-hdr-row">')


def mobile_hdr_close() -> None:
    inject_ui_html("</div>")


def mobile_row2_open() -> None:
    """Duas colunas lado a lado no celular (ex.: anterior/próximo)."""
    inject_ui_html('<div class="ig-m-row-2">')


def mobile_row2_close() -> None:
    inject_ui_html("</div>")
