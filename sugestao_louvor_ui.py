"""Layout premium — Sugestão de Louvor (IBBJ Louvor v3)."""

from __future__ import annotations

import html
from datetime import datetime

import pandas as pd
import streamlit as st

from ui_html import inject_ui_html

SUGESTAO_TAB_LABELS = (
    "📋  Todas",
    "🔵  Pendentes",
    "🟡  Em análise",
    "🟢  Aprovadas",
    "🔴  Recusadas",
)

STATUS_CSS = {
    "pendente": "ig-sug--pend",
    "em_analise": "ig-sug--analise",
    "aprovada": "ig-sug--ok",
    "recusada": "ig-sug--rej",
}


def sugestao_louvor_page_css() -> str:
    return """
        [data-testid="stAppViewContainer"]:has(.ig-sug-page) {
            background: #030712 !important;
        }
        .ig-sug-page {
            max-width: 1320px;
            margin: 0 auto;
            font-family: Manrope, "Segoe UI", sans-serif;
        }
        .ig-sug-header {
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
        .ig-sug-header-left {
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
        }
        .ig-sug-header-ico {
            width: 2.6rem;
            height: 2.6rem;
            border-radius: 12px;
            flex-shrink: 0;
            background: rgba(212, 160, 23, 0.35)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23fde68a' stroke-width='2'%3E%3Cpath d='M9 18h6'/%3E%3Cpath d='M10 22h4'/%3E%3Cpath d='M12 2a7 7 0 0 0-4 12v2h8v-2a7 7 0 0 0-4-12z'/%3E%3C/svg%3E")
                center/20px no-repeat;
            box-shadow: 0 0 32px rgba(212, 160, 23, 0.45);
        }
        .ig-sug-header-title {
            margin: 0 0 0.15rem;
            font-size: 1.45rem;
            font-weight: 800;
            color: #f8fafc !important;
        }
        .ig-sug-header-sub {
            margin: 0;
            font-size: 0.82rem;
            color: #94a3b8 !important;
        }
        .ig-sug-banner {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.1rem 1.2rem;
            margin-bottom: 1rem;
            border-radius: 14px;
            background: rgba(37, 99, 235, 0.12);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(37, 99, 235, 0.32);
            box-shadow: 0 0 40px rgba(37, 99, 235, 0.08);
        }
        .ig-sug-banner-left {
            display: flex;
            gap: 0.65rem;
            flex: 1;
            min-width: 220px;
        }
        .ig-sug-banner-ico {
            width: 1.35rem;
            height: 1.35rem;
            flex-shrink: 0;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2360a5fa' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-sug-banner-msg {
            margin: 0;
            font-size: 0.84rem;
            line-height: 1.5;
            color: #cbd5e1 !important;
        }
        .ig-sug-banner-hero {
            width: 120px;
            height: 64px;
            border-radius: 10px;
            flex-shrink: 0;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.3), rgba(139, 92, 246, 0.2)),
                radial-gradient(ellipse at 50% 80%, rgba(212, 160, 23, 0.4), transparent 65%);
            position: relative;
        }
        .ig-sug-banner-hero::after {
            content: "✝";
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.4rem;
            color: rgba(212, 160, 23, 0.9);
            text-shadow: 0 0 16px rgba(212, 160, 23, 0.6);
        }
        .ig-sug-kpi-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.85rem;
            margin-bottom: 1rem;
        }
        @media (max-width: 1000px) {
            .ig-sug-kpi-row { grid-template-columns: repeat(2, 1fr); }
        }
        .ig-sug-kpi {
            padding: 1.1rem 1rem;
            border-radius: 14px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.06);
            position: relative;
            overflow: hidden;
        }
        .ig-sug-kpi--pend { border-color: rgba(37, 99, 235, 0.35); }
        .ig-sug-kpi--analise { border-color: rgba(212, 160, 23, 0.35); }
        .ig-sug-kpi--ok { border-color: rgba(34, 197, 94, 0.35); }
        .ig-sug-kpi--rej { border-color: rgba(239, 68, 68, 0.35); }
        .ig-sug-kpi-val {
            font-size: 1.75rem;
            font-weight: 800;
            color: #f8fafc !important;
            line-height: 1;
        }
        .ig-sug-kpi-lbl {
            display: block;
            margin-top: 0.35rem;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #94a3b8 !important;
        }
        .ig-sug-kpi-ico {
            display: inline-block;
            width: 1.1rem;
            height: 1.1rem;
            margin-bottom: 0.35rem;
        }
        .ig-sug-card {
            padding: 1.15rem 1.2rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .ig-sug-card-title {
            margin: 0 0 0.25rem;
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-sug-card-sub {
            margin: 0 0 1rem;
            font-size: 0.76rem;
            color: #94a3b8 !important;
        }
        .ig-sug-checks {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem 1rem;
            margin: 0.75rem 0 1rem;
            font-size: 0.78rem;
            color: #94a3b8 !important;
        }
        .ig-sug-check { display: inline-flex; align-items: center; gap: 0.3rem; }
        .ig-sug-check--cifra { color: #60a5fa !important; }
        .ig-sug-check--play { color: #22c55e !important; }
        .ig-sug-check--kit { color: #a78bfa !important; }
        .ig-sug-check--cong { color: #d4a017 !important; }
        .ig-sug-row {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.7rem 0.65rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: background 0.15s;
        }
        .ig-sug-row:hover {
            background: rgba(139, 92, 246, 0.06);
        }
        .ig-sug-row:last-child { border-bottom: none; }
        .ig-sug-item {
            padding: 0.65rem 0.7rem;
            margin-bottom: 0.5rem;
            border-radius: 12px;
            background: rgba(3, 7, 18, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .ig-sug-item:hover {
            border-color: rgba(139, 92, 246, 0.25);
            background: rgba(139, 92, 246, 0.05);
        }
        .ig-sug-item-note {
            margin: 0.35rem 0 0;
            padding: 0.45rem 0.55rem;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.04);
            font-size: 0.72rem;
            color: #94a3b8 !important;
            line-height: 1.4;
        }
        [data-testid="stMain"]:has(.ig-sug-page) .ig-sug-item + div[data-testid="stHorizontalBlock"] {
            margin-top: -0.25rem !important;
        }
        .ig-sug-cover {
            width: 42px;
            height: 42px;
            border-radius: 8px;
            flex-shrink: 0;
            background: linear-gradient(135deg, #6d28d9, #2563eb);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }
        .ig-sug-row-info { flex: 1; min-width: 0; }
        .ig-sug-row-title {
            font-size: 0.82rem;
            font-weight: 600;
            color: #f8fafc !important;
        }
        .ig-sug-row-meta {
            font-size: 0.68rem;
            color: #64748b !important;
        }
        .ig-sug-badge {
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            font-size: 0.62rem;
            font-weight: 600;
        }
        .ig-sug-badge.ig-sug--pend {
            color: #93c5fd !important;
            background: rgba(37, 99, 235, 0.2);
            border: 1px solid rgba(37, 99, 235, 0.4);
        }
        .ig-sug-badge.ig-sug--analise {
            color: #fde68a !important;
            background: rgba(212, 160, 23, 0.2);
            border: 1px solid rgba(212, 160, 23, 0.4);
        }
        .ig-sug-badge.ig-sug--ok {
            color: #86efac !important;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.35);
        }
        .ig-sug-badge.ig-sug--rej {
            color: #fca5a5 !important;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.35);
        }
        .ig-sug-side-card {
            padding: 0.95rem 1rem;
            margin-bottom: 0.85rem;
            border-radius: 16px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .ig-sug-side-title {
            margin: 0 0 0.65rem;
            font-size: 0.92rem;
            font-weight: 700;
            color: #f8fafc !important;
        }
        .ig-sug-side-item {
            display: flex;
            gap: 0.55rem;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        .ig-sug-side-item:last-child { border-bottom: none; }
        .ig-sug-side-cover {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: linear-gradient(135deg, #22c55e, #166534);
            flex-shrink: 0;
        }
        .ig-sug-timeline-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-top: 0.35rem;
            flex-shrink: 0;
        }
        .ig-sug-tip {
            display: flex;
            gap: 0.5rem;
            padding: 0.45rem 0;
            font-size: 0.74rem;
            color: #cbd5e1 !important;
            line-height: 1.4;
        }
        .ig-sug-tip-ico {
            width: 1.25rem;
            height: 1.25rem;
            border-radius: 50%;
            flex-shrink: 0;
            background: rgba(139, 92, 246, 0.25);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            color: #c4b5fd;
        }
        .ig-sug-footer-banner {
            padding: 0.85rem 1.1rem;
            margin-top: 0.75rem;
            border-radius: 14px;
            background: rgba(139, 92, 246, 0.15);
            border: 1px solid rgba(139, 92, 246, 0.35);
            box-shadow: 0 0 28px rgba(139, 92, 246, 0.12);
            font-size: 0.8rem;
            color: #c4b5fd !important;
            text-align: center;
        }
        [class*="st-key-ig_sug_nova"] .stButton > button {
            background: linear-gradient(135deg, #8b5cf6, #6d28d9) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 6px 24px rgba(139, 92, 246, 0.45) !important;
        }
        [class*="st-key-ig_sug_enviar"] .stFormSubmitButton > button,
        [class*="st-key-ig_sug_enviar"] .stButton > button {
            background: linear-gradient(135deg, #d4a017, #b45309) !important;
            color: #030712 !important;
            border: none !important;
            font-weight: 800 !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 28px rgba(212, 160, 23, 0.35) !important;
        }
        [data-testid="stMain"]:has(.ig-sug-page) div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            gap: 0.3rem !important;
            padding: 0.4rem !important;
            border-radius: 12px !important;
            background: rgba(15, 23, 42, 0.65) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
        }
        [data-testid="stMain"]:has(.ig-sug-page) div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(139, 92, 246, 0.28) !important;
            color: #f8fafc !important;
            border-radius: 8px !important;
        }
        .sugestao-status-pill { display: none !important; }
    """


def render_sugestao_page_open() -> None:
    inject_ui_html('<div class="ig-sug-page">')


def render_sugestao_page_close() -> None:
    inject_ui_html("</div>")


def render_sugestao_header() -> None:
    inject_ui_html(
        """
        <div class="ig-sug-header">
            <div class="ig-sug-header-left">
                <span class="ig-sug-header-ico" aria-hidden="true"></span>
                <div>
                    <div class="ig-sug-header-title">Sugerir música ao repertório</div>
                    <div class="ig-sug-header-sub">Ministério • Sugestões para o repertório</div>
                </div>
            </div>
        </div>
        """
    )


def render_sugestao_nova_button() -> None:
    if st.button("+ Nova sugestão", key="ig_sug_nova", type="primary"):
        st.session_state["sug_focus_form"] = True
        st.rerun()


def render_sugestao_banner() -> None:
    inject_ui_html(
        """
        <div class="ig-sug-banner">
            <div class="ig-sug-banner-left">
                <span class="ig-sug-banner-ico" aria-hidden="true"></span>
                <p class="ig-sug-banner-msg">
                    Envie links do YouTube e o nome da música.<br>
                    Acompanhe abaixo o status da sua sugestão:
                    <strong>pendente</strong>, <strong>em análise</strong>,
                    <strong>aprovada</strong> ou <strong>recusada</strong>.
                </p>
            </div>
            <span class="ig-sug-banner-hero" aria-hidden="true"></span>
        </div>
        """
    )


def compute_sugestao_stats(sugestoes_df: pd.DataFrame, normalize_status) -> dict[str, int]:
    counts = {k: 0 for k in STATUS_CSS}
    if sugestoes_df.empty:
        return counts
    for _, row in sugestoes_df.iterrows():
        st_key = normalize_status(str(row.get("status", "")))
        if st_key in counts:
            counts[st_key] += 1
    return counts


def render_sugestao_kpis(counts: dict[str, int], labels: dict[str, str]) -> None:
    cards = [
        ("pend", counts.get("pendente", 0), "Sugestões pendentes", "ig-sug-kpi--pend", "📄"),
        ("analise", counts.get("em_analise", 0), "Em análise", "ig-sug-kpi--analise", "🔍"),
        ("ok", counts.get("aprovada", 0), "Aprovadas", "ig-sug-kpi--ok", "✓"),
        ("rej", counts.get("recusada", 0), "Recusadas", "ig-sug-kpi--rej", "✕"),
    ]
    parts = ['<div class="ig-sug-kpi-row">']
    for _k, val, lbl, cls, ico in cards:
        parts.append(
            f'<div class="ig-sug-kpi {cls}">'
            f'<span class="ig-sug-kpi-ico">{ico}</span>'
            f'<span class="ig-sug-kpi-val">{val}</span>'
            f'<span class="ig-sug-kpi-lbl">{html.escape(lbl)}</span></div>'
        )
    parts.append("</div>")
    inject_ui_html("".join(parts))


def render_form_card_open() -> None:
    inject_ui_html(
        """
        <div class="ig-sug-card" id="sug-form-anchor">
            <div class="ig-sug-card-title">Sugerir louvor</div>
        """
    )


def render_form_card_checks_hint() -> None:
    inject_ui_html(
        """
        <div class="ig-sug-checks">
            <span class="ig-sug-check ig-sug-check--cifra">🎸 Tem cifra</span>
            <span class="ig-sug-check ig-sug-check--play">▶ Tem playback</span>
            <span class="ig-sug-check ig-sug-check--kit">🎤 Tem kit voz</span>
            <span class="ig-sug-check ig-sug-check--cong">👥 Versão congregacional</span>
        </div>
        """
    )


def render_form_card_close() -> None:
    inject_ui_html("</div>")


def badge_html(status_key: str, label: str) -> str:
    cls = STATUS_CSS.get(status_key, "ig-sug--pend")
    return (
        f'<span class="ig-sug-badge {cls}">{html.escape(label)}</span>'
    )


def build_suggestion_row_html(
    title: str,
    artist: str,
    suggester: str,
    date_str: str,
    status_key: str,
    status_label: str,
) -> str:
    artist = artist or "—"
    return (
        f'<div class="ig-sug-row">'
        f'<span class="ig-sug-cover">🎵</span>'
        f'<div class="ig-sug-row-info">'
        f'<div class="ig-sug-row-title">{html.escape(title)}</div>'
        f'<div class="ig-sug-row-meta">{html.escape(artist)} · Sugerido por {html.escape(suggester)} · {html.escape(date_str)}</div>'
        f"</div>"
        f"{badge_html(status_key, status_label)}"
        f"</div>"
    )


def user_facing_review_note(notes: str) -> str:
    """Texto livre para exibir (sem metadados Artista/Tema embutidos no envio)."""
    n = str(notes or "").strip()
    if not n:
        return ""
    meta_prefixes = (
        "Artista:",
        "Tema:",
        "Categoria:",
        "Ministração:",
        "Tom:",
        "Recursos:",
    )
    parts = [p.strip() for p in n.split("|")]
    free = [p for p in parts if p and not any(p.startswith(m) for m in meta_prefixes)]
    return " ".join(free).strip()


def render_gestao_card_open() -> None:
    inject_ui_html(
        """
        <div class="ig-sug-card">
            <div class="ig-sug-card-title">Gestão de sugestões (liderança)</div>
            <p class="ig-sug-card-sub">Acompanhe, analise e gerencie as sugestões enviadas pelos integrantes.</p>
        """
    )


def render_gestao_card_close() -> None:
    inject_ui_html("</div>")


def _time_ago(created: str) -> str:
    try:
        dt = pd.to_datetime(created)
        if pd.isna(dt):
            return created
        delta = datetime.now() - dt.to_pydatetime()
        if delta.days > 0:
            return f"há {delta.days}d"
        h = delta.seconds // 3600
        if h > 0:
            return f"há {h}h"
        m = max(1, delta.seconds // 60)
        return f"há {m}min"
    except (ValueError, TypeError):
        return created


def render_sugestao_sidebar(
    sugestoes_df: pd.DataFrame,
    *,
    normalize_status,
    status_labels: dict[str, str],
) -> None:
    if sugestoes_df.empty:
        inject_ui_html('<div class="ig-sug-side-card"><p class="ig-sug-card-sub">Nenhuma sugestão ainda.</p></div>')
        return

    df = sugestoes_df.copy()
    df["_st"] = df["status"].astype(str).map(normalize_status)
    df["_ord"] = pd.to_datetime(df["created_at"], errors="coerce")

    aprovadas = df[df["_st"] == "aprovada"].sort_values("_ord", ascending=False).head(5)
    items_ap = []
    for _, s in aprovadas.iterrows():
        items_ap.append(
            f'<div class="ig-sug-side-item">'
            f'<span class="ig-sug-side-cover"></span>'
            f'<div><div class="ig-sug-row-title">{html.escape(str(s["title"]))}</div>'
            f'<div class="ig-sug-row-meta">{html.escape(str(s.get("created_at", "")))}</div>'
            f'{badge_html("aprovada", status_labels.get("aprovada", "Aprovada"))}</div></div>'
        )
    inject_ui_html(
        f"""
        <div class="ig-sug-side-card">
            <div class="ig-sug-side-title">Top sugestões aprovadas</div>
            {"".join(items_ap) if items_ap else '<p class="ig-sug-card-sub">Nenhuma aprovada ainda.</p>'}
        </div>
        """
    )

    recentes = df.sort_values("_ord", ascending=False).head(6)
    items_rec = []
    dot_colors = {
        "pendente": "#2563eb",
        "em_analise": "#d4a017",
        "aprovada": "#22c55e",
        "recusada": "#ef4444",
    }
    for _, s in recentes.iterrows():
        sk = str(s["_st"])
        items_rec.append(
            f'<div class="ig-sug-side-item">'
            f'<span class="ig-sug-timeline-dot" style="background:{dot_colors.get(sk, "#64748b")}"></span>'
            f'<div><div class="ig-sug-row-title">{html.escape(str(s["title"]))}</div>'
            f'<div class="ig-sug-row-meta">{_time_ago(str(s.get("created_at", "")))} · '
            f'{badge_html(sk, status_labels.get(sk, sk))}</div></div></div>'
        )
    inject_ui_html(
        f"""
        <div class="ig-sug-side-card">
            <div class="ig-sug-side-title">Sugestões recentes</div>
            {"".join(items_rec)}
        </div>
        <div class="ig-sug-side-card">
            <div class="ig-sug-side-title">Dicas para sugestões</div>
            <div class="ig-sug-tip"><span class="ig-sug-tip-ico">1</span>Escolha músicas congregacionais</div>
            <div class="ig-sug-tip"><span class="ig-sug-tip-ico">2</span>Verifique a letra bíblica</div>
            <div class="ig-sug-tip"><span class="ig-sug-tip-ico">3</span>Evite músicas fora da identidade do ministério</div>
            <div class="ig-sug-tip"><span class="ig-sug-tip-ico">4</span>Envie o máximo de informações possível</div>
        </div>
        """
    )


def render_footer_banner() -> None:
    inject_ui_html(
        '<div class="ig-sug-footer-banner">'
        "✨ As sugestões aprovadas podem entrar automaticamente no repertório oficial."
        "</div>"
    )


def pack_extra_notes(
    *,
    artista: str,
    tema: str,
    categoria: str,
    ministracao: str,
    tom: str,
    observacoes: str,
    tem_cifra: bool,
    tem_playback: bool,
    tem_kit: bool,
    tem_cong: bool,
) -> str:
    parts = []
    if artista.strip():
        parts.append(f"Artista: {artista.strip()}")
    if tema.strip():
        parts.append(f"Tema: {tema.strip()}")
    if categoria.strip():
        parts.append(f"Categoria: {categoria.strip()}")
    if ministracao.strip():
        parts.append(f"Ministração: {ministracao.strip()}")
    if tom.strip():
        parts.append(f"Tom: {tom.strip()}")
    flags = []
    if tem_cifra:
        flags.append("cifra")
    if tem_playback:
        flags.append("playback")
    if tem_kit:
        flags.append("kit_voz")
    if tem_cong:
        flags.append("congregacional")
    if flags:
        parts.append("Recursos: " + ", ".join(flags))
    if observacoes.strip():
        parts.append(observacoes.strip())
    return " | ".join(parts)


def parse_extra_from_notes(notes: str) -> str:
    """Extrai artista das notas para exibição na lista."""
    n = str(notes or "")
    if "Artista:" in n:
        seg = n.split("Artista:", 1)[1].split("|")[0].strip()
        return seg
    return ""
