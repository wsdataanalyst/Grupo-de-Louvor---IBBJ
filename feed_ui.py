"""Layout premium da página Feed — conforme mockup IBBJ Louvor v3."""

from __future__ import annotations

import html

import streamlit as st

from ui_html import inject_ui_html
from verse_of_day import verse_for_date


def feed_page_css() -> str:
    return """
        .ig-feed-page { max-width: 920px; margin: 0 auto; }
        .ig-feed-header-card {
            display: flex;
            align-items: flex-start;
            gap: 0.85rem;
            padding: 1.1rem 1.2rem;
            margin-bottom: 1rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .ig-feed-header-ico {
            flex-shrink: 0;
            width: 2.25rem;
            height: 2.25rem;
            border-radius: 10px;
            background: rgba(37, 99, 235, 0.2)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2393c5fd' stroke-width='2'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpath d='M14 2v6h6M16 13H8M16 17H8M10 9H8'/%3E%3C/svg%3E")
                center/18px no-repeat;
        }
        .ig-feed-header-title {
            font-size: 1.12rem;
            font-weight: 700;
            color: #f8fafc !important;
            margin: 0 0 0.2rem;
        }
        .ig-feed-header-sub {
            font-size: 0.8rem;
            color: #94a3b8 !important;
            margin: 0;
        }
        .ig-feed-verse {
            display: flex;
            flex-wrap: wrap;
            align-items: stretch;
            gap: 1rem;
            padding: 1.25rem 1.2rem;
            margin-bottom: 1rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            overflow: hidden;
        }
        .ig-feed-verse-left { flex: 1 1 240px; min-width: 0; }
        .ig-feed-verse-kicker {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.78rem;
            font-weight: 700;
            color: #d4a017 !important;
            margin-bottom: 0.65rem;
        }
        .ig-feed-verse-kicker-ico {
            width: 1.1rem;
            height: 1.1rem;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Cpath d='M4 19.5A2.5 2.5 0 0 1 6.5 17H20'/%3E%3Cpath d='M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'/%3E%3C/svg%3E")
                center/contain no-repeat;
        }
        .ig-feed-quote-mark {
            font-size: 2rem;
            line-height: 1;
            color: #d4a017 !important;
            margin-bottom: 0.15rem;
        }
        .ig-feed-verse-text {
            font-size: 0.92rem;
            line-height: 1.55;
            color: #f8fafc !important;
            margin: 0 0 0.5rem;
        }
        .ig-feed-verse-ref {
            font-size: 0.82rem;
            font-weight: 600;
            color: #d4a017 !important;
            margin: 0;
        }
        .ig-feed-verse-art {
            flex: 0 1 200px;
            min-height: 120px;
            border-radius: 12px;
            background:
                radial-gradient(ellipse 70% 60% at 50% 45%, rgba(56, 189, 248, 0.25), transparent),
                linear-gradient(145deg, rgba(30, 58, 138, 0.4), rgba(3, 7, 18, 0.9));
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .ig-feed-verse-art svg {
            width: 88%;
            max-width: 180px;
            height: auto;
            filter: drop-shadow(0 8px 24px rgba(212, 160, 23, 0.35));
        }
        .ig-feed-empty {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 1rem 1.15rem;
            margin: 1rem 0;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 3px solid #2563eb;
            box-shadow: -4px 0 20px rgba(37, 99, 235, 0.25);
        }
        .ig-feed-empty-ico {
            flex-shrink: 0;
            width: 1.75rem;
            height: 1.75rem;
            border-radius: 50%;
            background: rgba(37, 99, 235, 0.25)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2393c5fd' stroke-width='2'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E")
                center/16px no-repeat;
        }
        .ig-feed-empty p {
            margin: 0;
            font-size: 0.88rem;
            color: #94a3b8 !important;
        }
        /* Expanders do feed */
        [class*="st-key-ig_feed_maint"] [data-testid="stExpander"],
        [class*="st-key-ig_feed_new"] [data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.85) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 14px !important;
            margin-bottom: 0.65rem !important;
        }
        [class*="st-key-ig_feed_maint"] .streamlit-expanderHeader,
        [class*="st-key-ig_feed_new"] .streamlit-expanderHeader {
            background: transparent !important;
            font-weight: 600 !important;
            color: #e2e8f0 !important;
            padding: 0.75rem 1rem !important;
        }
        [class*="st-key-ig_feed_maint"] .streamlit-expanderHeader svg,
        [class*="st-key-ig_feed_new"] .streamlit-expanderHeader svg {
            color: #94a3b8 !important;
        }
        [class*="st-key-ig_feed_maint"] .streamlit-expanderHeader::before {
            content: "";
            display: inline-block;
            width: 1.25rem;
            height: 1.25rem;
            margin-right: 0.5rem;
            vertical-align: middle;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Cpath d='M12 9v4M12 17h.01'/%3E%3Cpath d='M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/%3E%3C/svg%3E")
                center/contain no-repeat;
        }
        [class*="st-key-ig_feed_new"] .streamlit-expanderHeader::before {
            content: "";
            display: inline-block;
            width: 1.35rem;
            height: 1.35rem;
            margin-right: 0.5rem;
            vertical-align: middle;
            border-radius: 8px;
            background: rgba(139, 92, 246, 0.35)
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23c4b5fd' stroke-width='2.5'%3E%3Cpath d='M12 5v14M5 12h14'/%3E%3C/svg%3E")
                center/14px no-repeat;
        }
        .ig-feed-post-card {
            padding: 1.1rem 1.15rem 0.85rem;
            margin-bottom: 1rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
        }
        .ig-feed-post-card h4 {
            margin: 0.35rem 0 0.25rem;
            color: #f8fafc !important;
            font-size: 1rem;
            font-weight: 700;
        }
        .ig-feed-post-badge {
            display: inline-block;
            padding: 0.12rem 0.45rem;
            border-radius: 6px;
            font-size: 0.68rem;
            font-weight: 600;
            background: rgba(37, 99, 235, 0.2);
            color: #93c5fd !important;
        }
        .ig-feed-post-meta {
            font-size: 0.75rem;
            color: #94a3b8 !important;
            margin: 0;
        }
        .ig-feed-refresh-wrap { margin: 0.5rem 0 1rem; }
        [class*="st-key-ig_feed_refresh"] .stButton > button {
            border-radius: 10px !important;
            background: rgba(37, 99, 235, 0.15) !important;
            border: 1px solid rgba(37, 99, 235, 0.35) !important;
            color: #93c5fd !important;
            font-size: 0.8rem !important;
        }
    """


_BIBLE_ART_SVG = """
<svg viewBox="0 0 200 140" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="pg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e3a5f"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <path d="M30 25 L100 15 L170 25 L170 115 L100 125 L30 115 Z" fill="url(#pg)" stroke="#334155" stroke-width="1"/>
  <path d="M100 15 L100 125" stroke="#475569" stroke-width="1"/>
  <path d="M45 40 Q100 50 155 40" fill="none" stroke="#64748b" stroke-width="0.8"/>
  <path d="M45 95 Q100 105 155 95" fill="none" stroke="#64748b" stroke-width="0.8"/>
  <g filter="url(#glow)">
    <rect x="92" y="42" width="16" height="52" rx="2" fill="#d4a017"/>
    <rect x="72" y="58" width="56" height="14" rx="2" fill="#d4a017"/>
  </g>
  <ellipse cx="100" cy="68" rx="35" ry="28" fill="rgba(56,189,248,0.15)"/>
</svg>
"""


def render_feed_page_open() -> None:
    inject_ui_html('<div class="ig-feed-page">')


def render_feed_page_close() -> None:
    inject_ui_html("</div>")


def render_feed_header() -> None:
    inject_ui_html(
        """
        <div class="ig-feed-header-card">
            <span class="ig-feed-header-ico" aria-hidden="true"></span>
            <div>
                <div class="ig-feed-header-title">Feed do ministério</div>
                <div class="ig-feed-header-sub">Principal · Novidades, músicas e comunicados</div>
            </div>
        </div>
        """
    )


def render_feed_verse_card() -> None:
    v = verse_for_date()
    text = html.escape(v["text"])
    ref = html.escape(v["ref"])
    inject_ui_html(
        f"""
        <div class="ig-feed-verse">
            <div class="ig-feed-verse-left">
                <div class="ig-feed-verse-kicker">
                    <span class="ig-feed-verse-kicker-ico" aria-hidden="true"></span>
                    Versículo do dia
                </div>
                <div class="ig-feed-quote-mark">"</div>
                <p class="ig-feed-verse-text">{text}</p>
                <p class="ig-feed-verse-ref">{ref}</p>
            </div>
            <div class="ig-feed-verse-art">{_BIBLE_ART_SVG}</div>
        </div>
        """
    )


def render_feed_empty_state() -> None:
    inject_ui_html(
        """
        <div class="ig-feed-empty">
            <span class="ig-feed-empty-ico" aria-hidden="true"></span>
            <p>Nenhuma publicação ainda. Músicas aprovadas aparecem aqui automaticamente.</p>
        </div>
        """
    )


def render_feed_post_header(
    *,
    badge: str,
    title: str,
    author: str,
    created: str,
) -> None:
    inject_ui_html(
        f"""
        <div class="ig-feed-post-card">
            <span class="ig-feed-post-badge">{html.escape(badge)}</span>
            <h4>{html.escape(title)}</h4>
            <p class="ig-feed-post-meta">{html.escape(author)} · {html.escape(created)}</p>
        </div>
        """
    )
