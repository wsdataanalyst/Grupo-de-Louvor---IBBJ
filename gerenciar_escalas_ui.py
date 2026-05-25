"""Layout premium rigoroso — Gerenciar Escalas (IBBJ Louvor v3 / Behance)."""

from __future__ import annotations

import calendar
import html
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from ui_html import inject_ui_html

GERENCIAR_TAB_LABELS = (
    "✨  Montar escala",
    "💡  Sugestões",
    "🎵  Sequência do Culto",
    "📄  Exportar PDF",
    "💬  WhatsApp integrantes",
)

NOVA_ESCALA_LABEL = "➕ Nova escala"


def gerenciar_escalas_page_css() -> str:
    return """
        [data-testid="stAppViewContainer"]:has(.ig-ger-page) {
            background: #030712 !important;
        }
        .ig-ger-page {
            max-width: 1280px;
            margin: 0 auto;
            font-family: Manrope, "Segoe UI", sans-serif;
        }
        .ig-ger-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.25rem 1.35rem;
            margin-bottom: 1.1rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.72);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.07);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        }
        .ig-ger-header-left {
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
        }
        .ig-ger-header-ico {
            width: 2.6rem;
            height: 2.6rem;
            border-radius: 12px;
            flex-shrink: 0;
            background: rgba(139, 92, 246, 0.35)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23c4b5fd' stroke-width='2'%3E%3Crect x='3' y='4' width='18' height='18' rx='2'/%3E%3Cpath d='M16 2v4M8 2v4M3 10h18'/%3E%3C/svg%3E")
                center/20px no-repeat;
            box-shadow: 0 0 28px rgba(139, 92, 246, 0.45);
        }
        .ig-ger-header-title {
            margin: 0 0 0.15rem;
            font-size: 1.45rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #f8fafc !important;
        }
        .ig-ger-header-sub {
            margin: 0;
            font-size: 0.82rem;
            color: #94a3b8 !important;
        }
        .ig-ger-kpi-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.85rem;
            margin-bottom: 1.1rem;
        }
        @media (max-width: 1100px) {
            .ig-ger-kpi-row { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 520px) {
            .ig-ger-kpi-row { grid-template-columns: 1fr; }
        }
        .ig-ger-kpi {
            position: relative;
            padding: 1.15rem 1rem 1rem;
            border-radius: 14px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.06);
            overflow: hidden;
            min-height: 108px;
        }
        .ig-ger-kpi::after {
            content: "";
            position: absolute;
            right: -8px;
            bottom: -12px;
            width: 72px;
            height: 72px;
            opacity: 0.12;
            background: center/contain no-repeat;
            pointer-events: none;
        }
        .ig-ger-kpi--members::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 24 24' fill='none' stroke='%238b5cf6' stroke-width='1.5'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='9' cy='7' r='4'/%3E%3C/svg%3E");
        }
        .ig-ger-kpi--louvores::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='1.5'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E");
        }
        .ig-ger-kpi--escalas::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 24 24' fill='none' stroke='%232563eb' stroke-width='1.5'%3E%3Crect x='3' y='4' width='18' height='18' rx='2'/%3E%3Cpath d='M16 2v4M8 2v4M3 10h18'/%3E%3C/svg%3E");
        }
        .ig-ger-kpi--cultos::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 24 24' fill='none' stroke='%23f472b6' stroke-width='1.5'%3E%3Cpath d='M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z'/%3E%3Cpath d='M19 10v1a7 7 0 0 1-14 0v-1'/%3E%3Cpath d='M12 18v4'/%3E%3C/svg%3E");
        }
        .ig-ger-kpi-val {
            display: block;
            font-size: 1.85rem;
            font-weight: 800;
            color: #f8fafc !important;
            line-height: 1;
        }
        .ig-ger-kpi-lbl {
            display: block;
            margin-top: 0.35rem;
            font-size: 0.72rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-ger-kpi-desc {
            display: block;
            margin-top: 0.15rem;
            font-size: 0.68rem;
            color: #94a3b8 !important;
        }
        .ig-ger-kpi-ico {
            display: inline-block;
            width: 1.15rem;
            height: 1.15rem;
            margin-bottom: 0.4rem;
        }
        .ig-ger-kpi--members .ig-ger-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238b5cf6' stroke-width='2'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='9' cy='7' r='4'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-ger-kpi--louvores .ig-ger-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-ger-kpi--escalas .ig-ger-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%232563eb' stroke-width='2'%3E%3Crect x='3' y='4' width='18' height='18' rx='2'/%3E%3Cpath d='M16 2v4M8 2v4M3 10h18'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-ger-kpi--cultos .ig-ger-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23f472b6' stroke-width='2'%3E%3Cpath d='M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z'/%3E%3Cpath d='M19 10v1a7 7 0 0 1-14 0v-1'/%3E%3Cpath d='M12 18v4'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        [data-testid="stMain"]:has(.ig-ger-page) div[data-testid="stTabs"] {
            margin-bottom: 1.15rem !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            gap: 0.35rem !important;
            padding: 0.45rem 0.55rem !important;
            border-radius: 14px !important;
            background: rgba(15, 23, 42, 0.65) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) div[data-testid="stTabs"] [data-baseweb="tab"] {
            color: #94a3b8 !important;
            font-weight: 600 !important;
            font-size: 0.78rem !important;
            padding: 0.55rem 0.75rem !important;
            border-radius: 10px !important;
            background: transparent !important;
            white-space: nowrap !important;
            transition: color 0.15s, background 0.15s !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
            color: #e2e8f0 !important;
            background: rgba(37, 99, 235, 0.12) !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            color: #f8fafc !important;
            background: rgba(139, 92, 246, 0.28) !important;
            border-bottom: none !important;
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.2) !important;
        }
        [class*="st-key-ig_ger_nova_escala_hdr"] .stButton > button {
            background: linear-gradient(135deg, #8b5cf6, #6d28d9) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 0.55rem 1.1rem !important;
            box-shadow: 0 6px 24px rgba(139, 92, 246, 0.45) !important;
        }
        [class*="st-key-ig_ger_nova_escala_outline"] .stButton > button {
            background: transparent !important;
            color: #c4b5fd !important;
            border: 1px solid rgba(139, 92, 246, 0.55) !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            width: 100% !important;
        }
        [class*="st-key-ig_ger_nova_escala_outline"] .stButton > button:hover {
            background: rgba(139, 92, 246, 0.15) !important;
        }
        .ig-ger-form-card {
            padding: 1.15rem 1.2rem 1.25rem;
            margin-bottom: 1rem;
            border-radius: 16px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.07);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        }
        .ig-ger-form-title {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            margin: 0 0 1rem;
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-ger-form-title-ico {
            width: 1.1rem;
            height: 1.1rem;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Crect x='3' y='4' width='18' height='18' rx='2'/%3E%3Cpath d='M16 2v4M8 2v4M3 10h18'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-ger-section-title {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            margin: 0 0 0.35rem;
            font-size: 1.02rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-ger-section-sub {
            margin: 0 0 0.85rem;
            font-size: 0.78rem;
            color: #94a3b8 !important;
        }
        .ig-ger-tip {
            display: flex;
            align-items: flex-start;
            gap: 0.65rem;
            padding: 0.85rem 1rem;
            margin: 0.85rem 0 1rem;
            border-radius: 12px;
            background: rgba(37, 99, 235, 0.12);
            border: 1px solid rgba(37, 99, 235, 0.35);
        }
        .ig-ger-tip-ico {
            flex-shrink: 0;
            width: 1.25rem;
            height: 1.25rem;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2360a5fa' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-ger-tip p {
            margin: 0;
            font-size: 0.8rem;
            line-height: 1.45;
            color: #93c5fd !important;
        }
        .ig-ger-side-card {
            padding: 0;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.07);
            overflow: hidden;
        }
        .ig-ger-side-hero {
            height: 88px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.35), rgba(139, 92, 246, 0.25)),
                radial-gradient(ellipse at 50% 80%, rgba(212, 160, 23, 0.35), transparent 60%),
                #0f172a;
            position: relative;
        }
        .ig-ger-side-hero::after {
            content: "✝";
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.75rem;
            color: rgba(212, 160, 23, 0.85);
            text-shadow: 0 0 24px rgba(212, 160, 23, 0.6);
        }
        .ig-ger-side-body { padding: 0.95rem 1rem 1rem; }
        .ig-ger-planner-title {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            margin: 0 0 0.35rem;
            font-size: 0.95rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-ger-planner-sub {
            margin: 0 0 0.65rem;
            font-size: 0.76rem;
            color: #94a3b8 !important;
            line-height: 1.45;
        }
        .ig-ger-mini-cal {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 2px;
            margin-bottom: 0.65rem;
            font-size: 0.58rem;
            text-align: center;
            color: #64748b !important;
        }
        .ig-ger-mini-cal span.ig-ger-day-on {
            color: #f8fafc !important;
            background: rgba(139, 92, 246, 0.35);
            border-radius: 4px;
        }
        .ig-ger-upcoming {
            font-size: 0.72rem;
            color: #cbd5e1 !important;
            margin-bottom: 0.5rem;
            padding: 0.45rem 0.5rem;
            border-radius: 8px;
            background: rgba(37, 99, 235, 0.1);
            border-left: 3px solid #2563eb;
        }
        .ig-ger-member-row {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.6rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }
        .ig-ger-member-row:last-child { border-bottom: none; }
        .ig-ger-member-avatar img,
        .ig-ger-member-avatar span {
            width: 36px !important;
            height: 36px !important;
            border-radius: 50% !important;
            flex-shrink: 0;
        }
        .ig-ger-member-info { flex: 1; min-width: 0; }
        .ig-ger-member-name {
            display: block;
            font-size: 0.78rem;
            font-weight: 600;
            color: #f8fafc !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .ig-ger-member-role {
            display: block;
            font-size: 0.65rem;
            color: #94a3b8 !important;
        }
        .ig-ger-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .ig-ger-status-dot--warn { background: #d4a017; box-shadow: 0 0 8px rgba(212, 160, 23, 0.6); }
        .ig-ger-status-dot--ok { background: #22c55e; box-shadow: 0 0 8px rgba(34, 197, 94, 0.5); }
        .ig-ger-status-dot--pend { background: #f97316; }
        .ig-ger-badge-warn {
            display: inline-block;
            padding: 0.12rem 0.45rem;
            border-radius: 999px;
            font-size: 0.58rem;
            font-weight: 600;
            color: #d4a017 !important;
            background: rgba(212, 160, 23, 0.18);
            border: 1px solid rgba(212, 160, 23, 0.4);
        }
        .ig-ger-badge-ok {
            display: inline-block;
            padding: 0.12rem 0.45rem;
            border-radius: 999px;
            font-size: 0.58rem;
            font-weight: 600;
            color: #86efac !important;
            background: rgba(34, 197, 94, 0.12);
        }
        .ig-ger-member-menu {
            color: #64748b;
            font-size: 1rem;
            letter-spacing: 0.1em;
            flex-shrink: 0;
        }
        .ig-ger-insight-row {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.74rem;
        }
        .ig-ger-insight-row:last-child { border-bottom: none; }
        .ig-ger-insight-lbl {
            color: #64748b !important;
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        .ig-ger-insight-val {
            color: #f8fafc !important;
            font-weight: 600;
            margin-top: 0.1rem;
        }
        [data-testid="stMain"]:has(.ig-ger-page) [class*="st-key-nova_esc_save"] .stButton > button,
        [data-testid="stMain"]:has(.ig-ger-page) [class*="st-key-ig_ger_save_full"] .stButton > button {
            background: linear-gradient(135deg, #d4a017, #b45309) !important;
            color: #030712 !important;
            border: none !important;
            font-weight: 800 !important;
            font-size: 0.95rem !important;
            padding: 0.75rem 1rem !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 28px rgba(212, 160, 23, 0.4) !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) .louvor-selected-box,
        [data-testid="stMain"]:has(.ig-ger-page) .louvor-dropdown {
            background: rgba(3, 7, 18, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) .louvor-selected-title {
            color: #f8fafc !important;
            font-weight: 700 !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) [data-testid="stTextInput"] input,
        [data-testid="stMain"]:has(.ig-ger-page) [data-testid="stTextArea"] textarea,
        [data-testid="stMain"]:has(.ig-ger-page) [data-testid="stDateInput"] input {
            background: rgba(3, 7, 18, 0.6) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
            color: #f8fafc !important;
            border-radius: 10px !important;
        }
        [data-testid="stMain"]:has(.ig-ger-page) .planner-column-wrap {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        [class*="st-key-ig_ger_go_calendar"] .stButton > button,
        [class*="st-key-ig_ger_ver_integrantes"] .stButton > button {
            background: transparent !important;
            color: #60a5fa !important;
            border: 1px solid rgba(37, 99, 235, 0.45) !important;
            border-radius: 10px !important;
            font-size: 0.76rem !important;
            font-weight: 600 !important;
            width: 100% !important;
        }
    """


def render_gerenciar_page_open() -> None:
    inject_ui_html('<div class="ig-ger-page">')


def render_gerenciar_page_close() -> None:
    inject_ui_html("</div>")


def render_gerenciar_header() -> None:
    inject_ui_html(
        """
        <div class="ig-ger-header">
            <div class="ig-ger-header-left">
                <span class="ig-ger-header-ico" aria-hidden="true"></span>
                <div>
                    <div class="ig-ger-header-title">Gerenciar Escalas</div>
                    <div class="ig-ger-header-sub">Ministério • Escalas, ensaio e trocas</div>
                </div>
            </div>
        </div>
        """
    )


def render_gerenciar_kpis(
    *,
    n_members: int,
    n_louvores: int,
    n_escalas: int,
    n_cultos: int,
) -> None:
    cards = [
        ("members", n_members, "Integrantes", "Ativos no ministério"),
        ("louvores", n_louvores, "Louvores", "No repertório"),
        ("escalas", n_escalas, "Escalas", "Publicadas"),
        ("cultos", n_cultos, "Cultos programados", "Esta semana"),
    ]
    parts = ['<div class="ig-ger-kpi-row">']
    for cls, val, lbl, desc in cards:
        parts.append(
            f'<div class="ig-ger-kpi ig-ger-kpi--{cls}">'
            f'<span class="ig-ger-kpi-ico" aria-hidden="true"></span>'
            f'<span class="ig-ger-kpi-val">{html.escape(str(val))}</span>'
            f'<span class="ig-ger-kpi-lbl">{html.escape(lbl)}</span>'
            f'<span class="ig-ger-kpi-desc">{html.escape(desc)}</span>'
            f"</div>"
        )
    parts.append("</div>")
    inject_ui_html("".join(parts))


def trigger_nova_escala() -> None:
    st.session_state["editor_escala_sel"] = NOVA_ESCALA_LABEL
    st.rerun()


def render_gerenciar_nova_escala_button(*, key: str = "ig_ger_nova_escala_hdr") -> None:
    if st.button("+ Nova Escala", key=key, type="primary"):
        trigger_nova_escala()


def render_gerenciar_nova_escala_outline() -> None:
    if st.button("+ Nova Escala", key="ig_ger_nova_escala_outline", use_container_width=True):
        trigger_nova_escala()


def render_gerenciar_culto_section_open() -> None:
    inject_ui_html(
        '<div class="ig-ger-form-card" style="padding-bottom:0.65rem;margin-bottom:0.75rem">'
        '<div class="ig-ger-section-title">'
        '<span class="ig-ger-form-title-ico" aria-hidden="true"></span>'
        "Culto / Escala</div>"
    )


def render_gerenciar_form_card_open(title: str, *, icon_class: str = "ig-ger-form-title-ico") -> None:
    inject_ui_html(
        f'<div class="ig-ger-form-card">'
        f'<div class="ig-ger-form-title">'
        f'<span class="{icon_class}" aria-hidden="true"></span>'
        f"{html.escape(title)}</div>"
    )


def render_gerenciar_form_card_close() -> None:
    inject_ui_html("</div>")


def render_gerenciar_louvores_section_header() -> None:
    inject_ui_html(
        """
        <div class="ig-ger-form-card" style="margin-top:0.25rem">
            <div class="ig-ger-section-title">
                <span class="ig-ger-form-title-ico" style="background-image:url('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%2716%27 height=%2716%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27%23d4a017%27 stroke-width=%272%27%3E%3Cpath d=%27M9 18V5l12-2v13%27/%3E%3Ccircle cx=%276%27 cy=%2718%27 r=%273%27/%3E%3Ccircle cx=%2718%27 cy=%2716%27 r=%273%27/%3E%3C/svg%3E')" aria-hidden="true"></span>
                Louvores do Culto
            </div>
            <p class="ig-ger-section-sub">Escolha e organize os louvores da escala.</p>
        """
    )


def render_gerenciar_louvores_tip() -> None:
    inject_ui_html(
        """
        <div class="ig-ger-tip">
            <span class="ig-ger-tip-ico" aria-hidden="true"></span>
            <p>Arraste os itens para reorganizar a sequência do culto ou use os botões de mover.</p>
        </div>
        """
    )


def cultos_esta_semana(escalas_df: pd.DataFrame) -> int:
    if escalas_df.empty or "date" not in escalas_df.columns:
        return 0
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    n = 0
    for _, row in escalas_df.iterrows():
        dt = pd.to_datetime(row.get("date"), errors="coerce")
        if pd.notna(dt) and start <= dt.date() <= end:
            n += 1
    return n


def culto_ref_for_planner() -> date:
    if "nova_esc_data" in st.session_state:
        try:
            return st.session_state["nova_esc_data"]
        except (TypeError, ValueError):
            pass
    return date.today()


def _mini_calendar_html(ref: date) -> str:
    cells = ["D", "S", "T", "Q", "Q", "S", "S"]
    for week in calendar.monthcalendar(ref.year, ref.month):
        for d in week:
            if d == 0:
                cells.append("\u00a0")
            elif d == ref.day:
                cells.append(f'<span class="ig-ger-day-on">{d}</span>')
            else:
                cells.append(str(d))
    return '<div class="ig-ger-mini-cal">' + "".join(f"<span>{c}</span>" for c in cells) + "</div>"


def compute_gerenciar_insights(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    culto_ref: date | None = None,
) -> tuple[str, str, str]:
    from app import member_display_name, members_visible_to_group
    from escala_member_stats import member_escala_stats

    culto_ref = culto_ref or date.today()
    top_name = "—"
    top_count = 0
    visible = members_visible_to_group(members_df)
    for _, row in visible.iterrows():
        em = str(row["email"]).strip().lower()
        stats = member_escala_stats(em, escalas_df, equipe_df, ref=culto_ref)
        if stats.month_count > top_count:
            top_count = stats.month_count
            top_name = member_display_name(row)
    if top_count == 0:
        top_name = "Nenhum escalado no mês"

    top_song = "—"
    if not programa_df.empty and "louvor_title" in programa_df.columns:
        vc = programa_df["louvor_title"].astype(str).str.strip()
        vc = vc[vc != ""]
        if not vc.empty:
            top_song = vc.value_counts().index[0]

    upcoming = "Nenhum culto agendado"
    if not escalas_df.empty:
        hoje = date.today()
        futuros: list[tuple[date, str]] = []
        for _, row in escalas_df.iterrows():
            dt = pd.to_datetime(row.get("date"), errors="coerce")
            if pd.notna(dt) and dt.date() >= hoje:
                futuros.append((dt.date(), str(row.get("event", "Culto"))))
        if futuros:
            futuros.sort(key=lambda x: x[0])
            d, ev = futuros[0]
            upcoming = f"{d.strftime('%d/%m/%Y')} · {ev}"

    return top_name, top_song, upcoming


def render_gerenciar_sidebar(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    culto_ref: date | None = None,
) -> None:
    from app import member_display_name, member_photo_html, members_visible_to_group, roles_for_public_display
    from escala_member_stats import member_escala_stats

    culto_ref = culto_ref or date.today()
    top_mus, top_song, upcoming = compute_gerenciar_insights(
        members_df, escalas_df, equipe_df, programa_df, louvores_df, culto_ref=culto_ref
    )

    inject_ui_html(
        f"""
        <div class="ig-ger-side-card">
            <div class="ig-ger-side-hero" aria-hidden="true"></div>
            <div class="ig-ger-side-body">
                <div class="ig-ger-planner-title">Painel do mês</div>
                <p class="ig-ger-planner-sub">Otimize escalas e garanta que nada se perca.</p>
                {_mini_calendar_html(culto_ref)}
                <div class="ig-ger-upcoming">Próximo: {html.escape(upcoming)}</div>
            </div>
        </div>
        """
    )
    if st.button("Ver calendário completo →", key="ig_ger_go_calendar", use_container_width=True):
        st.session_state.app_menu = "Escalas"
        st.rerun()

    visible = members_visible_to_group(members_df)
    linhas: list[tuple[int, str, str, str, str]] = []
    for _, row in visible.sort_values(by=["first_name", "last_name"]).iterrows():
        em = str(row["email"]).strip().lower()
        stats = member_escala_stats(em, escalas_df, equipe_df, ref=culto_ref)
        ultima = stats.last_date.strftime("%d/%m/%Y") if stats.last_date else "—"
        role = roles_for_public_display(str(row.get("roles", "")))
        avatar = member_photo_html(em, members_df, size=36)
        linhas.append((stats.month_count, ultima, member_display_name(row), role, avatar))

    sem_mes = [x for x in linhas if x[0] == 0]
    com_mes = [x for x in linhas if x[0] > 0]
    display = (sem_mes + com_mes)[:12]

    rows_html = []
    for no_mes, ultima, nome, role, avatar in display:
        dot_cls = "ig-ger-status-dot--ok" if no_mes else "ig-ger-status-dot--warn"
        badge = (
            '<span class="ig-ger-badge-ok">Escalado</span>'
            if no_mes
            else '<span class="ig-ger-badge-warn">Sem escala</span>'
        )
        rows_html.append(
            f'<div class="ig-ger-member-row">'
            f'<span class="ig-ger-member-avatar">{avatar}</span>'
            f'<div class="ig-ger-member-info">'
            f'<span class="ig-ger-member-name">{html.escape(nome)}</span>'
            f'<span class="ig-ger-member-role">{html.escape(role)} · Última {html.escape(ultima)}</span>'
            f"</div>"
            f'<span class="ig-ger-status-dot {dot_cls}" title="status"></span>'
            f"{badge}"
            f'<span class="ig-ger-member-menu" aria-hidden="true">⋯</span>'
            f"</div>"
        )

    inject_ui_html(
        f"""
        <div class="ig-ger-side-card">
            <div class="ig-ger-side-body">
                <div class="ig-ger-planner-title">Integrantes</div>
                <p class="ig-ger-planner-sub">Quem ainda não entrou na escala do mês.</p>
                <div class="ig-ger-planner-list">
                    {"".join(rows_html) if rows_html else '<p class="ig-ger-planner-sub">Nenhum integrante.</p>'}
                </div>
            </div>
        </div>
        """
    )
    if st.button("Ver todos os integrantes →", key="ig_ger_ver_integrantes", use_container_width=True):
        st.session_state.app_menu = "Membros"
        st.rerun()

    inject_ui_html(
        f"""
        <div class="ig-ger-side-card">
            <div class="ig-ger-side-body">
                <div class="ig-ger-planner-title">Quick Insights</div>
                <div class="ig-ger-insight-row">
                    <div class="ig-ger-insight-lbl">Mais ativo no mês</div>
                    <div class="ig-ger-insight-val">{html.escape(top_mus)}</div>
                </div>
                <div class="ig-ger-insight-row">
                    <div class="ig-ger-insight-lbl">Louvor mais usado</div>
                    <div class="ig-ger-insight-val">{html.escape(top_song)}</div>
                </div>
                <div class="ig-ger-insight-row">
                    <div class="ig-ger-insight-lbl">Próximo evento</div>
                    <div class="ig-ger-insight-val">{html.escape(upcoming)}</div>
                </div>
            </div>
        </div>
        """
    )


# Alias para compatibilidade
render_gerenciar_planner_panel = render_gerenciar_sidebar
