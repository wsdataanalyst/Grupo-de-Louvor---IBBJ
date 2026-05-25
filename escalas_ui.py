"""Layout premium da página Escalas — conforme mockup IBBJ Louvor v3."""

from __future__ import annotations

import streamlit as st

from sidebar_icons import _NAV_PATHS, svg_icon_uri
from ui_html import inject_ui_html

# Ícones das abas (mockup Escalas) — ordem igual a st.tabs em show_escalas_page
_ESCALAS_TAB_ICON_PATHS: tuple[str, ...] = (
    _NAV_PATHS["membros"],  # Minha equipe — pessoas
    _NAV_PATHS["escalas"],  # Todas minhas escalas — calendário
    _NAV_PATHS["repertorio"],  # Sequência do Culto — música
    (
        '<path d="M7 16V4"/>'
        '<path d="M17 8v8"/>'
        '<path d="M17 16l3 3-3 3"/>'
        '<path d="M7 8 4 5 4 5"/>'
    ),  # Trocar escala
    (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="3"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),  # Solicitações — grupo
    _NAV_PATHS["chat"],  # Chat do ensaio
)


def escalas_tab_icons_css() -> str:
    """Ícone Lucide antes do rótulo de cada aba."""
    rules: list[str] = []
    tab_sel = (
        '[data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] '
        '[data-baseweb="tab-list"] [data-baseweb="tab"], '
        '[data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] '
        '[data-baseweb="tab-list"] button, '
        '[data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [role="tab"]'
    )
    for i, paths in enumerate(_ESCALAS_TAB_ICON_PATHS, start=1):
        uri = svg_icon_uri(paths, stroke="#94a3b8", size=16)
        uri_on = svg_icon_uri(paths, stroke="#a78bfa", size=16)
        block = f"""
        {tab_sel}:nth-child({i}) {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.42rem !important;
            text-shadow: none !important;
            -webkit-font-smoothing: antialiased !important;
        }}
        {tab_sel}:nth-child({i})::before {{
            content: "";
            display: inline-block;
            width: 1.1rem;
            height: 1.1rem;
            flex-shrink: 0;
            background: url("{uri}") center / contain no-repeat;
            vertical-align: middle;
        }}
        {tab_sel}:nth-child({i})[aria-selected="true"]::before {{
            background-image: url("{uri_on}");
        }}
        """
        rules.append(block)
    return "\n".join(rules)


def escalas_page_css() -> str:
    gerenciar_ico = svg_icon_uri(_NAV_PATHS["gerenciar_escalas"], stroke="#93c5fd", size=16)
    gerenciar_btn_css = f"""
        [data-testid="stMain"]:has(.ig-escalas-page) [class*="st-key-ig_esc_go_gerenciar"] .stButton > button::before {{
            content: "";
            width: 1rem;
            height: 1rem;
            background: url("{gerenciar_ico}") center/contain no-repeat;
        }}
    """
    return """
        .ig-escalas-page { max-width: 960px; margin: 0 auto; }
        .ig-escalas-header-card {
            display: flex;
            align-items: flex-start;
            gap: 0.85rem;
            padding: 1.1rem 1.2rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.28);
        }
        .ig-escalas-header-ico {
            flex-shrink: 0;
            width: 2.35rem;
            height: 2.35rem;
            border-radius: 10px;
            background: rgba(37, 99, 235, 0.22)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2393c5fd' stroke-width='2'%3E%3Cpath d='M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z'/%3E%3Cpath d='M19 10v1a7 7 0 0 1-14 0v-1'/%3E%3Cpath d='M12 18v4'/%3E%3C/svg%3E")
                center/18px no-repeat;
        }
        .ig-escalas-header-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #f8fafc !important;
            margin: 0 0 0.2rem;
        }
        .ig-escalas-header-sub {
            font-size: 0.8rem;
            color: #94a3b8 !important;
            margin: 0;
        }
        .ig-escalas-info {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(37, 99, 235, 0.2);
        }
        .ig-escalas-info-ico {
            flex-shrink: 0;
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 50%;
            background: rgba(37, 99, 235, 0.35)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%2393c5fd' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E")
                center/12px no-repeat;
        }
        .ig-escalas-info p {
            margin: 0;
            font-size: 0.86rem;
            line-height: 1.45;
            color: #cbd5e1 !important;
        }
        .ig-escalas-info strong.ig-escalas-link {
            color: #60a5fa !important;
            font-weight: 600;
        }
        .ig-escalas-info-sub {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.8rem;
            color: #94a3b8 !important;
        }
        .ig-escalas-warn {
            display: flex;
            align-items: flex-start;
            gap: 0.85rem;
            padding: 1.15rem 1.2rem;
            margin: 0.75rem 0 1rem;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(212, 160, 23, 0.55);
            box-shadow: 0 0 24px rgba(212, 160, 23, 0.08);
        }
        .ig-escalas-warn-ico {
            flex-shrink: 0;
            width: 1.5rem;
            height: 1.5rem;
            margin-top: 0.1rem;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Cpath d='M12 9v4'/%3E%3Cpath d='M12 17h.01'/%3E%3Cpath d='M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/%3E%3C/svg%3E")
                center/contain no-repeat;
        }
        .ig-escalas-warn-title {
            margin: 0 0 0.2rem;
            font-size: 0.95rem;
            font-weight: 700;
            color: #d4a017 !important;
        }
        .ig-escalas-warn-sub {
            margin: 0;
            font-size: 0.82rem;
            color: #94a3b8 !important;
        }
        /* Abas Escalas — sublinhado roxo no ativo */
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] {
            margin-top: 0.25rem;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0.35rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding-bottom: 0.15rem !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab"],
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab-list"] button {
            color: #94a3b8 !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            padding: 0.55rem 0.75rem 0.55rem 0.55rem !important;
            background: transparent !important;
            text-shadow: none !important;
            letter-spacing: 0.01em !important;
            -webkit-font-smoothing: antialiased !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab-list"] button[aria-selected="true"] {
            color: #c4b5fd !important;
            border-bottom: 3px solid #8b5cf6 !important;
        }
        .ig-escalas-warn-title,
        .ig-escalas-warn-sub,
        .ig-escalas-header-title,
        .ig-escalas-header-sub {
            text-shadow: none !important;
            -webkit-font-smoothing: antialiased !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) [class*="st-key-ig_esc_go_gerenciar"] .stButton > button {
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.4rem !important;
            margin: -0.5rem 0 1rem !important;
            padding: 0.35rem 0.85rem 0.35rem 0.65rem !important;
            min-height: 2rem !important;
            font-size: 0.78rem !important;
            border-radius: 8px !important;
            background: rgba(37, 99, 235, 0.15) !important;
            border: 1px solid rgba(37, 99, 235, 0.4) !important;
            color: #93c5fd !important;
            text-shadow: none !important;
        }
    """ + gerenciar_btn_css + escalas_tab_icons_css()


def render_escalas_page_open() -> None:
    inject_ui_html('<div class="ig-escalas-page">')


def render_escalas_page_close() -> None:
    inject_ui_html("</div>")


def render_escalas_header() -> None:
    inject_ui_html(
        """
        <div class="ig-escalas-header-card">
            <span class="ig-escalas-header-ico" aria-hidden="true"></span>
            <div>
                <div class="ig-escalas-header-title">Escalas, ensaio e trocas</div>
                <div class="ig-escalas-header-sub">Ministério · Escalas, ensaio e trocas</div>
            </div>
        </div>
        """
    )


def render_escalas_info_banner() -> None:
    inject_ui_html(
        """
        <div class="ig-escalas-info">
            <span class="ig-escalas-info-ico" aria-hidden="true"></span>
            <div>
                <p>
                    Líderes e organizadores montam escalas em
                    <strong class="ig-escalas-link">Gerenciar Escalas</strong>.
                </p>
                <span class="ig-escalas-info-sub">
                    Aqui você solicita trocas e acompanha o chat do ensaio.
                </span>
            </div>
        </div>
        """
    )


def render_escalas_not_scheduled_warning() -> None:
    inject_ui_html(
        """
        <div class="ig-escalas-warn">
            <span class="ig-escalas-warn-ico" aria-hidden="true"></span>
            <div>
                <p class="ig-escalas-warn-title">Você não está escalado(a) nesta semana</p>
                <p class="ig-escalas-warn-sub">ou a escala ainda não foi publicada.</p>
            </div>
        </div>
        """
    )


def render_escalas_gerenciar_button() -> None:
    if st.button("Abrir Gerenciar Escalas", key="ig_esc_go_gerenciar", type="secondary"):
        st.session_state.app_menu = "Gerenciar Escalas"
        st.rerun()
