"""Layout premium — Repertório de Louvores (IBBJ Louvor v3)."""

from __future__ import annotations

import html
import math
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from link_finder import is_direct_url
from louvor_content import ensure_louvor_content_columns
from ui_html import inject_ui_html

REP_PAGE_SIZE_DEFAULT = 25


def repertorio_page_css() -> str:
    return """
        [data-testid="stAppViewContainer"]:has(.ig-rep-page) {
            background: #030712 !important;
        }
        .ig-rep-page {
            max-width: 1320px;
            margin: 0 auto;
            font-family: Manrope, "Segoe UI", sans-serif;
        }
        .ig-rep-header {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.25rem 1.35rem;
            margin-bottom: 0.9rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.72);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.07);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        }
        .ig-rep-header-left {
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
        }
        .ig-rep-header-ico {
            width: 2.6rem;
            height: 2.6rem;
            border-radius: 12px;
            flex-shrink: 0;
            background: rgba(139, 92, 246, 0.4)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23c4b5fd' stroke-width='2'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E")
                center/20px no-repeat;
            box-shadow: 0 0 32px rgba(139, 92, 246, 0.5);
        }
        .ig-rep-header-title {
            margin: 0 0 0.15rem;
            font-size: 1.45rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #f8fafc !important;
        }
        .ig-rep-header-sub {
            margin: 0;
            font-size: 0.82rem;
            color: #94a3b8 !important;
        }
        .ig-rep-banner {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
            border-radius: 14px;
            background: rgba(37, 99, 235, 0.1);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(37, 99, 235, 0.28);
        }
        .ig-rep-banner-left {
            display: flex;
            gap: 0.65rem;
            flex: 1;
            min-width: 200px;
        }
        .ig-rep-banner-ico {
            width: 1.35rem;
            height: 1.35rem;
            flex-shrink: 0;
            margin-top: 0.1rem;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2360a5fa' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-rep-banner-msg {
            margin: 0;
            font-size: 0.84rem;
            line-height: 1.45;
            color: #cbd5e1 !important;
        }
        .ig-rep-banner-sub {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.76rem;
            color: #94a3b8 !important;
        }
        .ig-rep-banner-link {
            font-size: 0.78rem;
            font-weight: 600;
            color: #60a5fa !important;
            white-space: nowrap;
        }
        .ig-rep-kpi-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.85rem;
            margin-bottom: 1rem;
        }
        @media (max-width: 1100px) {
            .ig-rep-kpi-row { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 480px) {
            .ig-rep-kpi-row { grid-template-columns: 1fr; }
        }
        .ig-rep-kpi {
            position: relative;
            padding: 1.1rem 1rem;
            border-radius: 14px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.06);
            overflow: hidden;
            min-height: 100px;
        }
        .ig-rep-kpi::after {
            content: "";
            position: absolute;
            right: -6px;
            bottom: -10px;
            width: 64px;
            height: 64px;
            opacity: 0.1;
            background: center/contain no-repeat;
            pointer-events: none;
        }
        .ig-rep-kpi--music::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 24 24' fill='none' stroke='%238b5cf6' stroke-width='1.5'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E");
        }
        .ig-rep-kpi--cifra::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 24 24' fill='none' stroke='%23a78bfa' stroke-width='1.5'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpath d='M14 2v6h6'/%3E%3Cpath d='M9 13h6M9 17h6'/%3E%3C/svg%3E");
        }
        .ig-rep-kpi--yt::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 24 24' fill='none' stroke='%23ef4444' stroke-width='1.5'%3E%3Cpolygon points='5 3 19 12 5 21 5 3'/%3E%3C/svg%3E");
        }
        .ig-rep-kpi--kit::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56' viewBox='0 0 24 24' fill='none' stroke='%238b5cf6' stroke-width='1.5'%3E%3Cpath d='M3 18v-6a9 9 0 0 1 18 0v6'/%3E%3Cpath d='M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z'/%3E%3C/svg%3E");
        }
        .ig-rep-kpi-val {
            font-size: 1.75rem;
            font-weight: 800;
            color: #f8fafc !important;
            line-height: 1;
        }
        .ig-rep-kpi-lbl {
            display: block;
            margin-top: 0.3rem;
            font-size: 0.7rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-rep-kpi-desc {
            display: block;
            margin-top: 0.12rem;
            font-size: 0.68rem;
            color: #94a3b8 !important;
        }
        .ig-rep-kpi-desc--green { color: #22c55e !important; }
        .ig-rep-kpi-ico {
            display: inline-block;
            width: 1.1rem;
            height: 1.1rem;
            margin-bottom: 0.35rem;
        }
        .ig-rep-kpi--music .ig-rep-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238b5cf6' stroke-width='2'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-rep-kpi--cifra .ig-rep-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23a78bfa' stroke-width='2'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpath d='M14 2v6h6'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-rep-kpi--yt .ig-rep-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23ef4444' stroke-width='2'%3E%3Cpolygon points='5 3 19 12 5 21 5 3'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-rep-kpi--kit .ig-rep-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238b5cf6' stroke-width='2'%3E%3Cpath d='M3 18v-6a9 9 0 0 1 18 0v6'/%3E%3Cpath d='M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-rep-filter-card {
            padding: 1.1rem 1.15rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .ig-rep-toolbar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            font-size: 0.78rem;
            color: #94a3b8 !important;
        }
        .ig-rep-toolbar strong { color: #f8fafc !important; }
        .ig-rep-table-wrap {
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.06);
            background: #0f172a;
            margin-bottom: 0.85rem;
        }
        .ig-rep-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
        }
        .ig-rep-table thead th {
            text-align: left;
            padding: 0.7rem 0.65rem;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #94a3b8 !important;
            background: rgba(3, 7, 18, 0.6);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }
        .ig-rep-table tbody tr {
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            transition: background 0.15s, box-shadow 0.15s;
        }
        .ig-rep-table tbody tr:hover {
            background: rgba(37, 99, 235, 0.08);
            box-shadow: inset 0 0 24px rgba(37, 99, 235, 0.06);
        }
        .ig-rep-table tbody td {
            padding: 0.65rem 0.65rem;
            color: #e2e8f0 !important;
            vertical-align: middle;
        }
        .ig-rep-table .ig-rep-song {
            font-weight: 600;
            color: #f8fafc !important;
        }
        .ig-rep-table .ig-rep-artist {
            color: #94a3b8 !important;
        }
        .ig-rep-ico-ok {
            display: inline-flex;
            width: 1.35rem;
            height: 1.35rem;
            border-radius: 50%;
            background: rgba(34, 197, 94, 0.2);
            align-items: center;
            justify-content: center;
            color: #22c55e;
            font-size: 0.75rem;
        }
        .ig-rep-ico-miss {
            color: #64748b;
            font-size: 0.85rem;
        }
        .ig-rep-ico-yt {
            color: #ef4444;
            font-size: 1rem;
            text-decoration: none;
        }
        .ig-rep-ico-kit {
            color: #a78bfa;
            font-size: 0.9rem;
        }
        .ig-rep-tag {
            display: inline-block;
            padding: 0.1rem 0.4rem;
            margin: 0.1rem 0.15rem 0.1rem 0;
            border-radius: 999px;
            font-size: 0.58rem;
            color: #94a3b8 !important;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .ig-rep-cat {
            font-size: 0.72rem;
            color: #c4b5fd !important;
        }
        .ig-rep-side-card {
            padding: 0.95rem 1rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .ig-rep-side-title {
            margin: 0 0 0.5rem;
            font-size: 0.92rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-rep-valid {
            background: rgba(34, 197, 94, 0.08);
            border-color: rgba(34, 197, 94, 0.25);
        }
        .ig-rep-valid-msg {
            margin: 0 0 0.65rem;
            font-size: 0.76rem;
            line-height: 1.45;
            color: #86efac !important;
        }
        .ig-rep-cat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.45rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.76rem;
        }
        .ig-rep-cat-row:last-child { border-bottom: none; }
        .ig-rep-cat-name { color: #e2e8f0 !important; }
        .ig-rep-cat-count { color: #64748b !important; font-size: 0.68rem; }
        .ig-rep-rank-row {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.74rem;
        }
        .ig-rep-rank-row:last-child { border-bottom: none; }
        .ig-rep-rank-ico {
            color: #d4a017;
            font-size: 0.85rem;
        }
        .ig-rep-rank-info { flex: 1; min-width: 0; }
        .ig-rep-rank-title {
            color: #f8fafc !important;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .ig-rep-rank-meta { color: #64748b !important; font-size: 0.65rem; }
        .ig-rep-suggest {
            background: linear-gradient(145deg, rgba(139, 92, 246, 0.25), rgba(15, 23, 42, 0.95));
            border: 1px solid rgba(139, 92, 246, 0.4);
            box-shadow: 0 0 32px rgba(139, 92, 246, 0.15);
        }
        .ig-rep-suggest p {
            margin: 0 0 0.65rem;
            font-size: 0.78rem;
            color: #cbd5e1 !important;
            line-height: 1.45;
        }
        .ig-rep-pagination {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            padding: 0.85rem;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.06);
            margin-top: 0.5rem;
        }
        .ig-rep-pagination span {
            font-size: 0.78rem;
            color: #94a3b8 !important;
            margin-right: 0.5rem;
        }
        [class*="st-key-ig_rep_add_music"] .stButton > button {
            background: linear-gradient(135deg, #8b5cf6, #6d28d9) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 6px 24px rgba(139, 92, 246, 0.45) !important;
        }
        [class*="st-key-ig_rep_clear_filters"] .stButton > button {
            background: transparent !important;
            color: #94a3b8 !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
        }
        [class*="st-key-ig_rep_side_valid"] .stButton > button,
        [class*="st-key-ig_rep_side_rank"] .stButton > button,
        [class*="st-key-ig_rep_side_cats"] .stButton > button,
        [class*="st-key-ig_rep_suggest_btn"] .stButton > button {
            background: transparent !important;
            color: #60a5fa !important;
            border: 1px solid rgba(37, 99, 235, 0.4) !important;
            border-radius: 10px !important;
            font-size: 0.76rem !important;
            width: 100% !important;
        }
        [class*="st-key-ig_rep_suggest_btn"] .stButton > button {
            color: #f8fafc !important;
            border-color: rgba(139, 92, 246, 0.5) !important;
            background: rgba(139, 92, 246, 0.2) !important;
        }
        [data-testid="stMain"]:has(.ig-rep-page) .music-pagination {
            display: none !important;
        }
        [data-testid="stMain"]:has(.ig-rep-page) [data-testid="stTextInput"] input,
        [data-testid="stMain"]:has(.ig-rep-page) [data-testid="stSelectbox"] > div {
            background: rgba(3, 7, 18, 0.55) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
        }
    """


def render_repertorio_page_open() -> None:
    inject_ui_html('<div class="ig-rep-page">')


def render_repertorio_page_close() -> None:
    inject_ui_html("</div>")


def render_repertorio_header() -> None:
    inject_ui_html(
        """
        <div class="ig-rep-header">
            <div class="ig-rep-header-left">
                <span class="ig-rep-header-ico" aria-hidden="true"></span>
                <div>
                    <div class="ig-rep-header-title">Repertório de Louvores</div>
                    <div class="ig-rep-header-sub">Ministério • Todas as músicas do ministério</div>
                </div>
            </div>
        </div>
        """
    )


def render_repertorio_add_button() -> None:
    if st.button("+ Adicionar música", key="ig_rep_add_music", type="primary"):
        st.session_state["rep_add_open"] = True
        st.rerun()


def render_repertorio_banner() -> None:
    inject_ui_html(
        """
        <div class="ig-rep-banner">
            <div class="ig-rep-banner-left">
                <span class="ig-rep-banner-ico" aria-hidden="true"></span>
                <p class="ig-rep-banner-msg">
                    Navegue pelo repertório com busca, filtros inteligentes e validação bíblica para liderança.
                    <span class="ig-rep-banner-sub">Cadastre sua função vocal e utilize Kit Voz para ensaios.</span>
                </p>
            </div>
            <span class="ig-rep-banner-link">Saiba mais sobre o Kit Voz →</span>
        </div>
        """
    )


def compute_repertorio_stats(louvores_df: pd.DataFrame) -> dict:
    df = ensure_louvor_content_columns(louvores_df)
    total = len(df)
    if total == 0:
        return {
            "total": 0,
            "cifra": 0,
            "cifra_pct": 0,
            "youtube": 0,
            "yt_pct": 0,
            "kit": 0,
            "kit_pct": 0,
            "added_month": 0,
            "local": 0,
        }

    def _has_cifra(row) -> bool:
        if is_direct_url(str(row.get("cifra_url", ""))):
            return True
        return bool(str(row.get("cifra_text", "")).strip())

    def _has_yt(row) -> bool:
        return is_direct_url(str(row.get("youtube_url", "")))

    cifra_n = sum(1 for _, r in df.iterrows() if _has_cifra(r))
    yt_n = sum(1 for _, r in df.iterrows() if _has_yt(r))
    kit_n = yt_n
    local_n = sum(
        1
        for _, r in df.iterrows()
        if str(r.get("lyrics_text", "")).strip() and str(r.get("cifra_text", "")).strip()
    )

    return {
        "total": total,
        "cifra": cifra_n,
        "cifra_pct": int(round(100 * cifra_n / total)),
        "youtube": yt_n,
        "yt_pct": int(round(100 * yt_n / total)),
        "kit": kit_n,
        "kit_pct": int(round(100 * kit_n / total)),
        "added_month": 0,
        "local": local_n,
    }


def count_added_this_month(sugestoes_df: pd.DataFrame | None) -> int:
    if sugestoes_df is None or sugestoes_df.empty:
        return 0
    cutoff = datetime.now() - timedelta(days=30)
    n = 0
    for _, row in sugestoes_df.iterrows():
        st_status = str(row.get("status", "")).lower()
        if "aprov" not in st_status:
            continue
        created = str(row.get("created_at", ""))
        try:
            dt = pd.to_datetime(created)
            if pd.notna(dt) and dt.to_pydatetime() >= cutoff:
                n += 1
        except (ValueError, TypeError):
            pass
    return n


def render_repertorio_kpis(stats: dict, *, added_month: int = 0) -> None:
    month_txt = f"+{added_month} este mês" if added_month else "Acervo local"
    inject_ui_html(
        f"""
        <div class="ig-rep-kpi-row">
            <div class="ig-rep-kpi ig-rep-kpi--music">
                <span class="ig-rep-kpi-ico"></span>
                <span class="ig-rep-kpi-val">{stats["total"]}</span>
                <span class="ig-rep-kpi-lbl">músicas cadastradas</span>
                <span class="ig-rep-kpi-desc ig-rep-kpi-desc--green">{html.escape(month_txt)}</span>
            </div>
            <div class="ig-rep-kpi ig-rep-kpi--cifra">
                <span class="ig-rep-kpi-ico"></span>
                <span class="ig-rep-kpi-val">{stats["cifra"]}</span>
                <span class="ig-rep-kpi-lbl">com cifra</span>
                <span class="ig-rep-kpi-desc">{stats["cifra_pct"]}% do repertório</span>
            </div>
            <div class="ig-rep-kpi ig-rep-kpi--yt">
                <span class="ig-rep-kpi-ico"></span>
                <span class="ig-rep-kpi-val">{stats["youtube"]}</span>
                <span class="ig-rep-kpi-lbl">com YouTube</span>
                <span class="ig-rep-kpi-desc">{stats["yt_pct"]}% do repertório</span>
            </div>
            <div class="ig-rep-kpi ig-rep-kpi--kit">
                <span class="ig-rep-kpi-ico"></span>
                <span class="ig-rep-kpi-val">{stats["kit"]}</span>
                <span class="ig-rep-kpi-lbl">com Kit Voz</span>
                <span class="ig-rep-kpi-desc">Disponíveis para treino</span>
            </div>
        </div>
        """
    )


def render_repertorio_filter_card_open() -> None:
    inject_ui_html('<div class="ig-rep-filter-card">')


def render_repertorio_filter_card_close() -> None:
    inject_ui_html("</div>")


def render_repertorio_toolbar(found: int, total: int, page: int, total_pages: int) -> None:
    inject_ui_html(
        f"""
        <div class="ig-rep-toolbar">
            <span><strong>{found}</strong> músicas encontradas · repertório com <strong>{total}</strong> louvores</span>
            <span>Página <strong>{page}</strong> de <strong>{total_pages}</strong></span>
        </div>
        """
    )


def _status_icon(ok: bool, ok_char: str = "✓", miss: str = "—") -> str:
    if ok:
        return f'<span class="ig-rep-ico-ok" title="Disponível">{ok_char}</span>'
    return f'<span class="ig-rep-ico-miss">{miss}</span>'


def _tags_html(temas: list[str], limit: int = 3) -> str:
    if not temas:
        return '<span class="ig-rep-tag">—</span>'
    parts = []
    for t in temas[:limit]:
        parts.append(f'<span class="ig-rep-tag">{html.escape(t)}</span>')
    if len(temas) > limit:
        parts.append(f'<span class="ig-rep-tag">+{len(temas) - limit}</span>')
    return "".join(parts)


def build_repertorio_table_html(page_df: pd.DataFrame) -> str:
    from catalog_sanitize import sanitize_catalog_text
    from louvor_meta import themes_from_csv

    rows = []
    for _, r in page_df.iterrows():
        titulo = html.escape(sanitize_catalog_text(str(r.get("title", ""))))
        artista = html.escape(sanitize_catalog_text(str(r.get("artist", ""))))
        tom = html.escape(sanitize_catalog_text(str(r.get("key", ""))) or "—")
        ritmo = html.escape(sanitize_catalog_text(str(r.get("ritmo", ""))) or "—")
        bpm = html.escape(sanitize_catalog_text(str(r.get("duracao_min", ""))) or "—")
        yt = str(r.get("youtube_url", "")).strip()
        cifra_ok = is_direct_url(str(r.get("cifra_url", ""))) or bool(
            str(r.get("cifra_text", "")).strip()
        )
        yt_ok = is_direct_url(yt)
        kit_ok = yt_ok
        temas = themes_from_csv(str(r.get("temas", "")))
        cat = temas[0] if temas else "Louvor"
        yt_cell = (
            f'<a class="ig-rep-ico-yt" href="{html.escape(yt)}" target="_blank" rel="noopener" title="YouTube">▶</a>'
            if yt_ok
            else _status_icon(False)
        )
        rows.append(
            "<tr>"
            f'<td class="ig-rep-song">{titulo}</td>'
            f'<td class="ig-rep-artist">{artista}</td>'
            f"<td>{tom}</td><td>{ritmo}</td><td>{bpm}</td>"
            f"<td>{_status_icon(cifra_ok)}</td>"
            f"<td>{yt_cell}</td>"
            f'<td>{_status_icon(kit_ok, "♪", "—")}</td>'
            f'<td class="ig-rep-cat">{html.escape(cat)}</td>'
            f"<td>{_tags_html(temas)}</td>"
            f'<td><span class="ig-rep-ico-miss">⋯</span></td>'
            "</tr>"
        )
    if not rows:
        rows.append(
            '<tr><td colspan="11" style="text-align:center;padding:1.5rem;color:#64748b">'
            "Nenhuma música encontrada com os filtros atuais.</td></tr>"
        )
    return (
        '<div class="ig-rep-table-wrap"><table class="ig-rep-table">'
        "<thead><tr>"
        "<th>Música</th><th>Artista</th><th>Tom</th><th>Ritmo</th><th>BPM</th>"
        "<th>Cifra</th><th>YouTube</th><th>Kit Voz</th><th>Categoria</th><th>Tags</th><th>Ações</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_repertorio_pagination(
    total_rows: int,
    page_size: int,
    key: str = "repertorio",
) -> tuple[int, int, int]:
    """Retorna (page, start_idx, end_idx) e renderiza controles premium."""
    total_pages = max(1, math.ceil(total_rows / page_size)) if total_rows else 1
    state_key = f"page_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 1
    page = min(max(1, st.session_state[state_key]), total_pages)
    st.session_state[state_key] = page

    c_prev, c_nums, c_next = st.columns([1, 4, 1])
    with c_prev:
        if st.button("‹", key=f"rep_prev_{key}", disabled=page <= 1, use_container_width=True):
            st.session_state[state_key] = page - 1
            st.rerun()
    with c_next:
        if st.button("›", key=f"rep_next_{key}", disabled=page >= total_pages, use_container_width=True):
            st.session_state[state_key] = page + 1
            st.rerun()
    with c_nums:
        slots = st.columns(min(7, total_pages))
        window_start = max(1, page - 3)
        window_end = min(total_pages, window_start + 6)
        window_start = max(1, window_end - 6)
        for i, p in enumerate(range(window_start, window_end + 1)):
            if i >= len(slots):
                break
            with slots[i]:
                label = f"·{p}·" if p == page else str(p)
                if st.button(label, key=f"rep_pg_{key}_{p}", use_container_width=True):
                    st.session_state[state_key] = p
                    st.rerun()

    start = (page - 1) * page_size
    end = start + page_size
    return page, start, end


def category_counts(louvores_df: pd.DataFrame, *, limit: int = 8) -> list[tuple[str, int]]:
    from louvor_meta import themes_from_csv

    counts: dict[str, int] = {}
    for _, row in louvores_df.iterrows():
        temas = themes_from_csv(str(row.get("temas", "")))
        cat = temas[0] if temas else "Louvor"
        counts[cat] = counts.get(cat, 0) + 1
    return sorted(counts.items(), key=lambda x: -x[1])[:limit]


def top_louvores_usage(
    programa_df: pd.DataFrame,
    *,
    limit: int = 5,
) -> list[tuple[str, int]]:
    if programa_df.empty:
        return []
    col = "louvor_title" if "louvor_title" in programa_df.columns else None
    if not col:
        return []
    vc = programa_df[col].astype(str).str.strip()
    vc = vc[vc != ""]
    if vc.empty:
        return []
    out = []
    for title, cnt in vc.value_counts().head(limit).items():
        out.append((str(title), int(cnt)))
    return out


def validation_summary(louvores_df: pd.DataFrame) -> tuple[int, int]:
    if louvores_df.empty:
        return 0, 0
    col = "validacao_status"
    if col not in louvores_df.columns:
        return len(louvores_df), len(louvores_df)
    ok = 0
    for _, row in louvores_df.iterrows():
        st_val = str(row.get(col, "")).strip().lower()
        if st_val and st_val not in ("pendente", "revisar", ""):
            ok += 1
    return ok, len(louvores_df)


def render_repertorio_sidebar(
    louvores_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    *,
    is_manager: bool,
) -> None:
    ok_val, total_val = validation_summary(louvores_df)
    all_ok = ok_val >= total_val * 0.85 if total_val else True
    msg = (
        "Todas as músicas estão alinhadas às Escrituras."
        if all_ok
        else f"{ok_val} de {total_val} com validação registrada no repertório."
    )
    inject_ui_html(
        f"""
        <div class="ig-rep-side-card ig-rep-valid">
            <div class="ig-rep-side-title">✓ Validação bíblica</div>
            <p class="ig-rep-valid-msg">{html.escape(msg)}</p>
        </div>
        """
    )
    if is_manager:
        if st.button("Ver relatório completo", key="ig_rep_side_valid", use_container_width=True):
            st.session_state["rep_show_validation"] = True
            st.rerun()

    cats = category_counts(louvores_df)
    cat_rows = "".join(
        f'<div class="ig-rep-cat-row">'
        f'<span class="ig-rep-cat-name">{html.escape(name)}</span>'
        f'<span class="ig-rep-cat-count">{n} músicas</span></div>'
        for name, n in cats
    ) or '<p class="ig-rep-valid-msg">Sem categorias ainda.</p>'
    inject_ui_html(
        f"""
        <div class="ig-rep-side-card">
            <div class="ig-rep-side-title">Categorias</div>
            {cat_rows}
        </div>
        """
    )
    if st.button("Ver todas categorias", key="ig_rep_side_cats", use_container_width=True):
        st.session_state["rep_show_categories"] = True
        st.rerun()

    ranking = top_louvores_usage(programa_df)
    rank_rows = "".join(
        f'<div class="ig-rep-rank-row">'
        f'<span class="ig-rep-rank-ico">♪</span>'
        f'<div class="ig-rep-rank-info">'
        f'<div class="ig-rep-rank-title">{html.escape(title)}</div>'
        f'<div class="ig-rep-rank-meta">{cnt} execuções</div></div></div>'
        for title, cnt in ranking
    ) or '<p class="ig-rep-valid-msg">Sem execuções registradas ainda.</p>'
    inject_ui_html(
        f"""
        <div class="ig-rep-side-card">
            <div class="ig-rep-side-title">Mais utilizadas</div>
            {rank_rows}
        </div>
        """
    )
    if st.button("Ver ranking completo", key="ig_rep_side_rank", use_container_width=True):
        from mobile_lab_nav import navigate_app_menu

        navigate_app_menu("Escalas")
        st.rerun()

    inject_ui_html(
        """
        <div class="ig-rep-side-card ig-rep-suggest">
            <div class="ig-rep-side-title">💡 Sugestão de novos louvores</div>
            <p>Sugira novos louvores para enriquecer o repertório do ministério.</p>
        </div>
        """
    )
    if st.button("Enviar sugestão", key="ig_rep_suggest_btn", use_container_width=True):
        from mobile_lab_nav import navigate_app_menu

        navigate_app_menu("Sugestão de louvor")
        st.rerun()
