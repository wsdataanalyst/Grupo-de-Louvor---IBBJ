"""Ícones SVG (estilo Lucide) para sidebar — injetados via CSS nos botões Streamlit."""

from __future__ import annotations

import html
import urllib.parse


def svg_icon_uri(paths: str, *, stroke: str = "#94a3b8", size: int = 18) -> str:
    """URI data:image/svg para uso em CSS background."""
    return _svg_uri(paths, stroke=stroke, size=size)


def _svg_uri(paths: str, *, stroke: str = "#94a3b8", size: int = 18) -> str:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="1.85" '
        f'stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
    )
    return "data:image/svg+xml," + urllib.parse.quote(svg)


# Lucide-like paths (24 viewBox)
_NAV_PATHS: dict[str, str] = {
    "dashboard": (
        '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 10v10h14V10"/>'
    ),
    "feed": (
        '<path d="M4.9 4.9a10 10 0 0 1 14.2 0"/>'
        '<path d="M7.8 7.8a6 6 0 0 1 8.4 0"/>'
        '<circle cx="12" cy="12" r="2"/>'
    ),
    "escalas": (
        '<rect x="3" y="4" width="18" height="18" rx="2"/>'
        '<path d="M16 2v4M8 2v4M3 10h18"/>'
    ),
    "gerenciar_escalas": (
        '<circle cx="12" cy="12" r="10"/>'
        '<circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>'
    ),
    "repertorio": (
        '<path d="M9 18V5l12-2v13"/>'
        '<circle cx="6" cy="18" r="3"/>'
        '<circle cx="18" cy="16" r="3"/>'
    ),
    "playlist": (
        '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/>'
        '<path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>'
    ),
    "sugestao_louvor": (
        '<path d="M9 18h6"/>'
        '<path d="M10 22h4"/>'
        '<path d="M12 2a7 7 0 0 0-4 12.5V16h8v-1.5A7 7 0 0 0 12 2z"/>'
    ),
    "chat": (
        '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/>'
    ),
    "eventos": (
        '<rect x="3" y="4" width="18" height="18" rx="2"/>'
        '<path d="M16 2v4M8 2v4M3 10h18"/>'
        '<path d="m9 16 2 2 4-4"/>'
    ),
    "membros": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "perfil": (
        '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/>'
    ),
    "avisos": (
        '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>'
        '<path d="M13.7 21a2 2 0 0 1-3.4 0"/>'
    ),
}

_TOOL_PATHS: dict[str, tuple[str, str]] = {
    "lock": (
        '<rect x="5" y="11" width="14" height="10" rx="2"/>'
        '<path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
        "#3b82f6",
    ),
    "bell": (
        '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>'
        '<path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
        "#d4a017",
    ),
    "cloud": (
        '<path d="M17.5 19H9a7 7 0 1 1 6.7-9.1A5 5 0 1 1 17.5 19z"/>',
        "#a78bfa",
    ),
    "settings": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4'
        'M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/>',
        "#94a3b8",
    ),
    "mobile": (
        '<rect x="6" y="2" width="12" height="20" rx="2"/>'
        '<path d="M12 18h.01"/>',
        "#22d3ee",
    ),
}

_LOGOUT_PATH = (
    '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
    '<path d="M16 17l5-5-5-5"/><path d="M21 12H9"/>'
)

_USER_PLACEHOLDER = (
    '<circle cx="12" cy="8.5" r="3.75"/>'
    '<path d="M5.5 20.5c0-3.2 2.9-5.8 6.5-5.8s6.5 2.6 6.5 5.8"/>'
)


def sidebar_nav_icons_css() -> str:
    """CSS ::before nos botões ig_nav_* com ícones Lucide."""
    rules: list[str] = []
    for slug, paths in _NAV_PATHS.items():
        uri = _svg_uri(paths, stroke="#94a3b8")
        uri_active = _svg_uri(paths, stroke="#60a5fa")
        sel = f'section[data-testid="stSidebar"] [class*="st-key-ig_nav_{slug}"]'
        rules.append(
            f"""
        {sel} .stButton > button::before {{
            content: "";
            display: inline-block;
            width: 1.125rem;
            height: 1.125rem;
            margin-right: 0.65rem;
            flex-shrink: 0;
            background: url("{uri}") center / contain no-repeat;
            vertical-align: middle;
            opacity: 0.92;
        }}
        {sel} .stButton > button[kind="primary"]::before {{
            background-image: url("{uri_active}");
            opacity: 1;
        }}
        """
        )
    logout_uri = _svg_uri(_LOGOUT_PATH, stroke="#f87171")
    rules.append(
        f"""
        section[data-testid="stSidebar"] [class*="st-key-ig_sidebar_logout"] .stButton > button::before {{
            content: "";
            display: inline-block;
            width: 1.125rem;
            height: 1.125rem;
            margin-right: 0.5rem;
            background: url("{logout_uri}") center / contain no-repeat;
            vertical-align: middle;
        }}
        """
    )
    return "\n".join(rules)


def sidebar_tool_icons_css() -> str:
    """Ícones coloridos + seta nos expanders de ferramentas."""
    rules: list[str] = []
    for key, (paths, color) in _TOOL_PATHS.items():
        icon_uri = _svg_uri(paths, stroke="#f8fafc", size=16)
        bg = html.escape(color)
        rules.append(
            f"""
        section[data-testid="stSidebar"] [class*="st-key-ig_tool_{key}"] .streamlit-expanderHeader {{
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            padding-left: 0.35rem !important;
        }}
        section[data-testid="stSidebar"] [class*="st-key-ig_tool_{key}"] .streamlit-expanderHeader svg {{
            display: none !important;
        }}
        section[data-testid="stSidebar"] [class*="st-key-ig_tool_{key}"] .streamlit-expanderHeader::before {{
            content: "";
            flex-shrink: 0;
            width: 1.75rem;
            height: 1.75rem;
            border-radius: 8px;
            background: {bg} url("{icon_uri}") center / 14px no-repeat;
            opacity: 0.95;
        }}
        section[data-testid="stSidebar"] [class*="st-key-ig_tool_{key}"] .streamlit-expanderHeader::after {{
            content: "›";
            margin-left: auto;
            color: #64748b;
            font-size: 1.1rem;
            font-weight: 600;
        }}
        """
        )
    return "\n".join(rules)


def sidebar_user_placeholder_svg() -> str:
    return _svg_uri(_USER_PLACEHOLDER, stroke="#7dd3fc", size=32)
