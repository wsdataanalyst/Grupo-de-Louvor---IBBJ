"""Layout premium da página Escalas — conforme mockup IBBJ Louvor v3."""

from __future__ import annotations

import streamlit as st

from ui_html import inject_ui_html

# Rótulos das abas com ícones (Streamlit renderiza nativamente — evita CSS ::before quebrado)
ESCALAS_TAB_KEYS: tuple[tuple[str, str], ...] = (
    ("equipe", "👥  Minha equipe"),
    ("todas", "📅  Todas minhas escalas"),
    ("sequencia", "🎵  Sequência do Culto"),
    ("trocas", "🔄  Trocar escala"),
    ("pedidos", "📬  Solicitações"),
    ("ensaio", "💬  Chat do ensaio"),
)

ESCALAS_TAB_LABELS = tuple(label for _, label in ESCALAS_TAB_KEYS)

_VALID_ESCALAS_TABS = frozenset(k for k, _ in ESCALAS_TAB_KEYS)


def get_escalas_tab() -> str:
    t = str(st.session_state.get("ig_escalas_tab", "equipe")).strip()
    return t if t in _VALID_ESCALAS_TABS else "equipe"


def set_escalas_tab(tab: str) -> None:
    if tab in _VALID_ESCALAS_TABS:
        st.session_state.ig_escalas_tab = tab
        st.session_state.ml_escalas_tab = tab


def apply_pending_escalas_tab() -> None:
    """Atalhos de outras telas (ex.: abrir Sequência do Culto)."""
    if st.session_state.pop("_open_sequencia_tab", False):
        set_escalas_tab("sequencia")
    pending = str(st.session_state.pop("ig_escalas_open_tab", "")).strip()
    if pending in _VALID_ESCALAS_TABS:
        set_escalas_tab(pending)


def render_escalas_tab_bar(active: str) -> None:
    """Abas lazy — só a aba ativa renderiza o corpo (Fase 1 performance)."""
    cols = st.columns(len(ESCALAS_TAB_KEYS))
    for col, (key, label) in zip(cols, ESCALAS_TAB_KEYS):
        with col:
            if st.button(
                label,
                key=f"ig_esc_tab_{key}",
                use_container_width=True,
                type="primary" if active == key else "secondary",
            ):
                set_escalas_tab(key)
                st.rerun()


def escalas_page_css() -> str:
    from culto_programa_css import culto_programa_css

    return culto_programa_css() + """
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
            margin-bottom: 0.75rem;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(37, 99, 235, 0.2);
        }
        .ig-escalas-info-ico {
            flex-shrink: 0;
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 8px;
            background: rgba(212, 160, 23, 0.2)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='6'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E")
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
        .ig-escalas-tabs-gap {
            height: 0.35rem;
            margin: 0;
            padding: 0;
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
        /* Abas — só cores e sublinhado roxo (sem ::before) */
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            gap: 0.25rem 0.5rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab"] {
            color: #94a3b8 !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
            padding: 0.5rem 0.55rem !important;
            background: transparent !important;
            white-space: nowrap !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            color: #c4b5fd !important;
            border-bottom: 3px solid #8b5cf6 !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) [class*="st-key-ig_esc_go_gerenciar"] {
            margin-bottom: 0.5rem !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) [class*="st-key-ig_esc_tab_"] .stButton > button {
            margin: 0 !important;
            padding: 0.45rem 0.35rem !important;
            min-height: 2.35rem !important;
            font-size: 0.72rem !important;
            border-radius: 8px !important;
            white-space: normal !important;
            line-height: 1.25 !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) [class*="st-key-ig_esc_tab_"] .stButton > button[kind="primary"] {
            background: rgba(139, 92, 246, 0.28) !important;
            border: 1px solid rgba(139, 92, 246, 0.45) !important;
            color: #e9d5ff !important;
            box-shadow: 0 0 16px rgba(139, 92, 246, 0.15) !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) [class*="st-key-ig_esc_tab_"] .stButton > button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #94a3b8 !important;
        }
        [data-testid="stMain"]:has(.ig-escalas-page) [class*="st-key-ig_esc_go_gerenciar"] .stButton > button {
            margin: 0 !important;
            padding: 0.4rem 0.9rem !important;
            min-height: 2.15rem !important;
            font-size: 0.8rem !important;
            border-radius: 8px !important;
            background: rgba(37, 99, 235, 0.15) !important;
            border: 1px solid rgba(37, 99, 235, 0.4) !important;
            color: #93c5fd !important;
        }
    """


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


def render_escalas_tabs_spacer() -> None:
    inject_ui_html('<div class="ig-escalas-tabs-gap" aria-hidden="true"></div>')


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
    if st.button("🎯  Abrir Gerenciar Escalas", key="ig_esc_go_gerenciar", type="secondary"):
        from mobile_lab_nav import navigate_app_menu

        navigate_app_menu("Gerenciar Escalas")
        st.rerun()
