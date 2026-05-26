"""Layout premium — Playlist pessoal (IBBJ Louvor v3)."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from louvor_meta import parse_duracao_min
from ui_html import inject_ui_html

PL_PAGE_SIZE_DEFAULT = 10

PRESET_PLAYLISTS = (
    ("Treino Domingo", "ig-pl-pl--purple"),
    ("Ensaio da Semana", "ig-pl-pl--blue"),
    ("Culto da Família", "ig-pl-pl--gold"),
    ("Pré Culto", "ig-pl-pl--green"),
)


def playlist_page_css() -> str:
    return """
        [data-testid="stAppViewContainer"]:has(.ig-pl-page) {
            background: #030712 !important;
        }
        .ig-pl-page {
            max-width: 1320px;
            margin: 0 auto 5rem;
            font-family: Manrope, "Segoe UI", sans-serif;
        }
        .ig-pl-header {
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
        .ig-pl-header-left {
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
        }
        .ig-pl-header-ico {
            width: 2.6rem;
            height: 2.6rem;
            border-radius: 12px;
            flex-shrink: 0;
            background: rgba(139, 92, 246, 0.4)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23c4b5fd' stroke-width='2'%3E%3Cpath d='M3 18v-6a9 9 0 0 1 18 0v6'/%3E%3Cpath d='M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z'/%3E%3C/svg%3E")
                center/20px no-repeat;
            box-shadow: 0 0 32px rgba(139, 92, 246, 0.5);
        }
        .ig-pl-header-title {
            margin: 0 0 0.15rem;
            font-size: 1.45rem;
            font-weight: 800;
            color: #f8fafc !important;
        }
        .ig-pl-header-sub {
            margin: 0;
            font-size: 0.82rem;
            color: #94a3b8 !important;
        }
        .ig-pl-banner {
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
        .ig-pl-banner-left { display: flex; gap: 0.65rem; flex: 1; }
        .ig-pl-banner-ico {
            width: 1.35rem;
            height: 1.35rem;
            flex-shrink: 0;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2360a5fa' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-pl-banner-msg {
            margin: 0;
            font-size: 0.84rem;
            line-height: 1.45;
            color: #cbd5e1 !important;
        }
        .ig-pl-banner-sub {
            display: block;
            margin-top: 0.25rem;
            font-size: 0.76rem;
            color: #94a3b8 !important;
        }
        .ig-pl-banner-link {
            font-size: 0.78rem;
            font-weight: 600;
            color: #60a5fa !important;
            white-space: nowrap;
        }
        .ig-pl-kpi-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.85rem;
            margin-bottom: 1rem;
        }
        @media (max-width: 1100px) {
            .ig-pl-kpi-row { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 480px) {
            .ig-pl-kpi-row { grid-template-columns: 1fr; }
        }
        .ig-pl-kpi {
            position: relative;
            padding: 1.1rem 1rem;
            border-radius: 14px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.06);
            overflow: hidden;
            min-height: 96px;
        }
        .ig-pl-kpi-val {
            font-size: 1.65rem;
            font-weight: 800;
            color: #f8fafc !important;
            line-height: 1.1;
        }
        .ig-pl-kpi-lbl {
            display: block;
            margin-top: 0.3rem;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #94a3b8 !important;
        }
        .ig-pl-kpi-ico {
            display: inline-block;
            width: 1.1rem;
            height: 1.1rem;
            margin-bottom: 0.35rem;
        }
        .ig-pl-kpi--tracks .ig-pl-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238b5cf6' stroke-width='2'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-pl-kpi--time .ig-pl-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%232563eb' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 6v6l4 2'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-pl-kpi--lists .ig-pl-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23a78bfa' stroke-width='2'%3E%3Cpath d='M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-pl-kpi--fav .ig-pl-kpi-ico {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Cpath d='M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-pl-card {
            padding: 1.1rem 1.15rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .ig-pl-card-title {
            margin: 0 0 0.25rem;
            font-size: 1rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-pl-card-sub {
            margin: 0 0 0.85rem;
            font-size: 0.76rem;
            color: #94a3b8 !important;
        }
        .ig-pl-search-hint {
            padding: 0.75rem 1rem;
            margin: 0.75rem 0;
            border-radius: 12px;
            background: rgba(37, 99, 235, 0.12);
            border: 1px solid rgba(37, 99, 235, 0.3);
            font-size: 0.8rem;
            color: #93c5fd !important;
        }
        .ig-pl-tracks-card {
            min-height: 220px;
            padding: 1.25rem 1.15rem;
        }
        .ig-pl-empty {
            text-align: center;
            padding: 2.5rem 1rem;
        }
        .ig-pl-empty-art {
            width: 88px;
            height: 88px;
            margin: 0 auto 1rem;
            border-radius: 18px;
            background: rgba(139, 92, 246, 0.2)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 24 24' fill='none' stroke='%23c4b5fd' stroke-width='1.5'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E")
                center/44px no-repeat;
            box-shadow: 0 0 48px rgba(139, 92, 246, 0.35);
        }
        .ig-pl-empty-title {
            margin: 0 0 0.35rem;
            font-size: 1rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-pl-empty-sub {
            margin: 0;
            font-size: 0.8rem;
            color: #94a3b8 !important;
        }
        .ig-pl-table-wrap {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .ig-pl-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
        }
        .ig-pl-table thead th {
            text-align: left;
            padding: 0.65rem 0.6rem;
            font-size: 0.62rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #94a3b8 !important;
            background: rgba(3, 7, 18, 0.6);
        }
        .ig-pl-table tbody tr {
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            transition: background 0.15s, box-shadow 0.15s;
        }
        .ig-pl-table tbody tr:hover {
            background: rgba(139, 92, 246, 0.08);
            box-shadow: inset 0 0 20px rgba(139, 92, 246, 0.06);
        }
        .ig-pl-table td {
            padding: 0.6rem;
            color: #e2e8f0 !important;
            vertical-align: middle;
        }
        .ig-pl-cover {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.4), rgba(37, 99, 235, 0.3));
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }
        .ig-pl-song { font-weight: 600; color: #f8fafc !important; }
        .ig-pl-artist { color: #94a3b8 !important; }
        .ig-pl-ico-ok { color: #22c55e; }
        .ig-pl-ico-yt { color: #ef4444; text-decoration: none; }
        .ig-pl-side-card {
            padding: 0.95rem 1rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .ig-pl-side-title {
            margin: 0 0 0.65rem;
            font-size: 0.92rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-pl-pl-item {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.55rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .ig-pl-pl-item:last-child { border-bottom: none; }
        .ig-pl-pl-thumb {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            flex-shrink: 0;
        }
        .ig-pl-pl-thumb.ig-pl-pl--purple {
            background: linear-gradient(135deg, #6d28d9, #4c1d95);
        }
        .ig-pl-pl-thumb.ig-pl-pl--blue {
            background: linear-gradient(135deg, #2563eb, #1e3a8a);
        }
        .ig-pl-pl-thumb.ig-pl-pl--gold {
            background: linear-gradient(135deg, #d4a017, #92400e);
        }
        .ig-pl-pl-thumb.ig-pl-pl--green {
            background: linear-gradient(135deg, #22c55e, #166534);
        }
        .ig-pl-pl-info { flex: 1; min-width: 0; }
        .ig-pl-pl-name {
            font-size: 0.78rem;
            font-weight: 600;
            color: #f8fafc !important;
        }
        .ig-pl-pl-meta { font-size: 0.65rem; color: #64748b !important; }
        .ig-pl-tip {
            display: flex;
            align-items: flex-start;
            gap: 0.55rem;
            padding: 0.55rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .ig-pl-tip:last-child { border-bottom: none; }
        .ig-pl-tip-ico {
            width: 1.75rem;
            height: 1.75rem;
            border-radius: 8px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
        }
        .ig-pl-tip-ico--blue { background: rgba(37, 99, 235, 0.25); }
        .ig-pl-tip-ico--gold { background: rgba(212, 160, 23, 0.25); }
        .ig-pl-tip-ico--green { background: rgba(34, 197, 94, 0.2); }
        .ig-pl-tip-text {
            flex: 1;
            font-size: 0.74rem;
            color: #cbd5e1 !important;
            line-height: 1.4;
        }
        .ig-pl-help-link {
            display: block;
            padding: 0.4rem 0;
            font-size: 0.74rem;
            color: #94a3b8 !important;
        }
        .ig-pl-player {
            position: fixed;
            bottom: 0;
            left: 280px;
            right: 0;
            z-index: 999;
            padding: 0.65rem 1.25rem;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(16px);
            border-top: 1px solid rgba(139, 92, 246, 0.25);
            box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.4);
        }
        @media (max-width: 900px) {
            .ig-pl-player { left: 0; }
        }
        .ig-pl-player-inner {
            display: flex;
            align-items: center;
            gap: 1rem;
            max-width: 900px;
            margin: 0 auto;
        }
        .ig-pl-player-cover {
            width: 44px;
            height: 44px;
            border-radius: 10px;
            background: linear-gradient(135deg, #8b5cf6, #2563eb);
            flex-shrink: 0;
        }
        .ig-pl-player-info { flex: 1; min-width: 0; }
        .ig-pl-player-title {
            font-size: 0.82rem;
            font-weight: 600;
            color: #f8fafc !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .ig-pl-player-artist {
            font-size: 0.68rem;
            color: #94a3b8 !important;
        }
        .ig-pl-player-bar {
            flex: 2;
            height: 4px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.1);
            overflow: hidden;
        }
        .ig-pl-player-bar-fill {
            width: 35%;
            height: 100%;
            background: linear-gradient(90deg, #8b5cf6, #2563eb);
            border-radius: 999px;
        }
        .ig-pl-player-ctrl {
            color: #f8fafc;
            font-size: 1.1rem;
            letter-spacing: 0.35rem;
        }
        [class*="st-key-ig_pl_nova_playlist"] .stButton > button {
            background: linear-gradient(135deg, #8b5cf6, #6d28d9) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 6px 24px rgba(139, 92, 246, 0.45) !important;
        }
        [class*="st-key-ig_pl_clear_filters"] .stButton > button {
            background: transparent !important;
            color: #94a3b8 !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
        }
        [class*="st-key-ig_pl_buscar"] .stButton > button {
            background: rgba(37, 99, 235, 0.25) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(37, 99, 235, 0.45) !important;
            border-radius: 10px !important;
        }
        [data-testid="stMain"]:has(.ig-pl-page) .music-pagination {
            display: none !important;
        }
        [data-testid="stMain"]:has(.ig-pl-page) [data-testid="stTextInput"] input {
            background: rgba(3, 7, 18, 0.55) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
        }
    """


def render_playlist_page_open() -> None:
    inject_ui_html('<div class="ig-pl-page">')


def render_playlist_page_close() -> None:
    inject_ui_html("</div>")


def render_playlist_header() -> None:
    inject_ui_html(
        """
        <div class="ig-pl-header">
            <div class="ig-pl-header-left">
                <span class="ig-pl-header-ico" aria-hidden="true"></span>
                <div>
                    <div class="ig-pl-header-title">Sua playlist pessoal</div>
                    <div class="ig-pl-header-sub">Ministério • Sua playlist de treino</div>
                </div>
            </div>
        </div>
        """
    )


def render_playlist_nova_button() -> None:
    if st.button("+ Nova playlist", key="ig_pl_nova_playlist", type="primary"):
        st.session_state["pl_nova_open"] = True
        st.rerun()


def render_playlist_banner() -> None:
    inject_ui_html(
        """
        <div class="ig-pl-banner">
            <div class="ig-pl-banner-left">
                <span class="ig-pl-banner-ico" aria-hidden="true"></span>
                <p class="ig-pl-banner-msg">
                    Monte sua playlist pessoal a partir do repertório da igreja — com YouTube,
                    Kit Voz e cifra para treinar.
                    <span class="ig-pl-banner-sub">Cadastre sua função vocal e use o kit em cada música do culto.</span>
                </p>
            </div>
            <span class="ig-pl-banner-link">Saiba mais sobre o kit →</span>
        </div>
        """
    )


def format_duration_hours(total_min: float) -> str:
    if total_min < 1:
        return "0m"
    hours = int(total_min // 60)
    mins = int(total_min % 60)
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def compute_playlist_stats(
    mine: pd.DataFrame,
    louvores_df: pd.DataFrame,
    favorite_ids: set[str],
) -> dict:
    n_tracks = len(mine)
    total_min = 0.0
    if not mine.empty:
        title_map: dict[str, float] = {}
        if not louvores_df.empty:
            for _, row in louvores_df.iterrows():
                t = str(row.get("title", "")).strip().lower()
                if t:
                    title_map[t] = parse_duracao_min(row.get("duracao_min", ""))
        for _, tr in mine.iterrows():
            t = str(tr.get("title", "")).strip().lower()
            total_min += title_map.get(t, 4.5)

    n_fav = len(favorite_ids)
    n_lists = len(PRESET_PLAYLISTS) if n_tracks else 1

    return {
        "tracks": n_tracks,
        "hours": format_duration_hours(total_min),
        "playlists": n_lists,
        "favorites": n_fav,
    }


def render_playlist_kpis(stats: dict) -> None:
    inject_ui_html(
        f"""
        <div class="ig-pl-kpi-row">
            <div class="ig-pl-kpi ig-pl-kpi--tracks">
                <span class="ig-pl-kpi-ico"></span>
                <span class="ig-pl-kpi-val">{stats["tracks"]}</span>
                <span class="ig-pl-kpi-lbl">faixas salvas</span>
            </div>
            <div class="ig-pl-kpi ig-pl-kpi--time">
                <span class="ig-pl-kpi-ico"></span>
                <span class="ig-pl-kpi-val">{html.escape(stats["hours"])}</span>
                <span class="ig-pl-kpi-lbl">horas de reprodução</span>
            </div>
            <div class="ig-pl-kpi ig-pl-kpi--lists">
                <span class="ig-pl-kpi-ico"></span>
                <span class="ig-pl-kpi-val">{stats["playlists"]}</span>
                <span class="ig-pl-kpi-lbl">playlists criadas</span>
            </div>
            <div class="ig-pl-kpi ig-pl-kpi--fav">
                <span class="ig-pl-kpi-ico"></span>
                <span class="ig-pl-kpi-val">{stats["favorites"]}</span>
                <span class="ig-pl-kpi-lbl">favoritas</span>
            </div>
        </div>
        """
    )


def render_add_music_card_open() -> None:
    inject_ui_html(
        """
        <div class="ig-pl-card">
            <div class="ig-pl-card-title">+ Adicionar música</div>
            <p class="ig-pl-card-sub">Busque no repertório</p>
        """
    )


def render_add_music_card_close() -> None:
    inject_ui_html("</div>")


def render_search_hint() -> None:
    inject_ui_html(
        '<div class="ig-pl-search-hint">'
        "Digite e busque para adicionar músicas à sua playlist."
        "</div>"
    )


def render_tracks_section_open() -> None:
    inject_ui_html(
        '<div class="ig-pl-card ig-pl-tracks-card">'
        '<div class="ig-pl-card-title">Suas faixas</div>'
    )


def render_tracks_empty_state() -> None:
    inject_ui_html(
        """
        <div class="ig-pl-empty">
            <div class="ig-pl-empty-art" aria-hidden="true"></div>
            <p class="ig-pl-empty-title">Nenhuma música na sua playlist.</p>
            <p class="ig-pl-empty-sub">Use a busca acima para adicionar do repertório.</p>
        </div>
        """
    )


def render_tracks_section_close() -> None:
    inject_ui_html("</div>")


def build_playlist_table_html(page_df: pd.DataFrame) -> str:
    from catalog_sanitize import sanitize_catalog_text

    rows = []
    for _, tr in page_df.iterrows():
        titulo = html.escape(sanitize_catalog_text(str(tr.get("title", ""))))
        artista = html.escape(sanitize_catalog_text(str(tr.get("artist", ""))) or "—")
        tom = html.escape(sanitize_catalog_text(str(tr.get("key", ""))) or "—")
        ritmo = sanitize_catalog_text(str(tr.get("ritmo", "")))
        dur = "4:30" if ritmo else "—"
        yt = str(tr.get("youtube_url", "")).strip()
        cif = str(tr.get("cifra_url", "")).strip()
        yt_cell = (
            f'<a class="ig-pl-ico-yt" href="{html.escape(yt)}" target="_blank" rel="noopener">▶</a>'
            if yt.startswith("http")
            else '<span class="ig-pl-ico-miss">—</span>'
        )
        cif_ok = cif.startswith("http")
        cif_cell = '<span class="ig-pl-ico-ok">✓</span>' if cif_ok else "—"
        rows.append(
            "<tr>"
            '<td><span class="ig-pl-cover">🎵</span></td>'
            f'<td class="ig-pl-song">{titulo}</td>'
            f'<td class="ig-pl-artist">{artista}</td>'
            f"<td>{tom}</td><td>{html.escape(dur)}</td>"
            f"<td>{yt_cell}</td>"
            f"<td>{cif_cell}</td>"
            f'<td><span class="ig-pl-ico-ok">♪</span></td>'
            f'<td><span style="color:#64748b">⋯</span></td>'
            "</tr>"
        )
    return (
        '<div class="ig-pl-table-wrap"><table class="ig-pl-table">'
        "<thead><tr>"
        "<th></th><th>Música</th><th>Artista</th><th>Tom</th><th>Duração</th>"
        "<th>YouTube</th><th>Cifra</th><th>Kit Voz</th><th>Ações</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def distribute_preset_playlists(mine: pd.DataFrame) -> list[tuple[str, str, int, str]]:
    """Nome, classe thumb, qtd faixas, duração label."""
    n = len(mine)
    names = PRESET_PLAYLISTS
    if n == 0:
        return [(name, cls, 0, "0 faixas · 0m") for name, cls in names]

    chunks: list[int] = []
    base, rem = divmod(n, len(names))
    chunks = [base + (1 if i < rem else 0) for i in range(len(names))]

    out = []
    idx = 0
    for (name, cls), cnt in zip(names, chunks):
        slice_df = mine.iloc[idx : idx + cnt]
        idx += cnt
        mins = cnt * 4.5
        out.append((name, cls, cnt, f"{cnt} faixas · {format_duration_hours(mins)}"))
    return out


def render_playlist_sidebar(mine: pd.DataFrame) -> None:
    presets = distribute_preset_playlists(mine)
    pl_html = "".join(
        f'<div class="ig-pl-pl-item">'
        f'<span class="ig-pl-pl-thumb {cls}" aria-hidden="true"></span>'
        f'<div class="ig-pl-pl-info">'
        f'<div class="ig-pl-pl-name">{html.escape(name)}</div>'
        f'<div class="ig-pl-pl-meta">{html.escape(meta)}</div>'
        f"</div></div>"
        for name, cls, _cnt, meta in presets
    )
    inject_ui_html(
        f"""
        <div class="ig-pl-side-card">
            <div class="ig-pl-side-title">Minhas playlists</div>
            {pl_html}
        </div>
        """
    )
    if st.button("Ver todas as playlists", key="ig_pl_all_playlists", use_container_width=True):
        st.session_state["pl_nova_open"] = True
        st.rerun()

    inject_ui_html(
        """
        <div class="ig-pl-side-card">
            <div class="ig-pl-side-title">Dicas rápidas</div>
            <div class="ig-pl-tip">
                <span class="ig-pl-tip-ico ig-pl-tip-ico--blue">🎤</span>
                <span class="ig-pl-tip-text">Cadastre sua função vocal no Perfil para liberar o Kit Voz.</span>
            </div>
            <div class="ig-pl-tip">
                <span class="ig-pl-tip-ico ig-pl-tip-ico--gold">🎵</span>
                <span class="ig-pl-tip-text">Use o Kit Voz em cada música para ensaiar seu nipe.</span>
            </div>
            <div class="ig-pl-tip">
                <span class="ig-pl-tip-ico ig-pl-tip-ico--green">✓</span>
                <span class="ig-pl-tip-text">Treine com propósito — monte listas por culto ou ensaio.</span>
            </div>
        </div>
        <div class="ig-pl-side-card">
            <div class="ig-pl-side-title">Ajuda</div>
            <span class="ig-pl-help-link">📋 Como montar uma playlist</span>
            <span class="ig-pl-help-link">🎤 Entenda o Kit Voz</span>
            <span class="ig-pl-help-link">❓ Dúvidas frequentes</span>
            <span class="ig-pl-help-link">💬 Fale com o suporte</span>
        </div>
        """
    )


def render_sticky_player(track: pd.Series | None) -> None:
    if track is None:
        return
    from catalog_sanitize import sanitize_catalog_text

    titulo = html.escape(sanitize_catalog_text(str(track.get("title", ""))))
    artista = html.escape(sanitize_catalog_text(str(track.get("artist", ""))))
    inject_ui_html(
        f"""
        <div class="ig-pl-player">
            <div class="ig-pl-player-inner">
                <span class="ig-pl-player-cover" aria-hidden="true"></span>
                <div class="ig-pl-player-info">
                    <div class="ig-pl-player-title">{titulo}</div>
                    <div class="ig-pl-player-artist">{artista}</div>
                </div>
                <div class="ig-pl-player-bar"><div class="ig-pl-player-bar-fill"></div></div>
                <span class="ig-pl-player-ctrl">⏮ ▶ ⏭</span>
            </div>
        </div>
        """
    )


def get_favorite_ids() -> set[str]:
    raw = st.session_state.get("pl_favorite_ids")
    if isinstance(raw, set):
        return raw
    if isinstance(raw, list):
        return set(raw)
    return set()


def toggle_favorite(track_id: str) -> None:
    fav = get_favorite_ids()
    tid = str(track_id)
    if tid in fav:
        fav.discard(tid)
    else:
        fav.add(tid)
    st.session_state["pl_favorite_ids"] = fav
