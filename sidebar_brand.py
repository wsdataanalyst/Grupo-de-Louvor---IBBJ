"""Marca IBBJ Louvor na sidebar — cruz dourada sobre equalizador (layout da referência)."""

from __future__ import annotations

import html as html_mod

from ui_html import html_block


def sidebar_brand_mark_html(cross_html: str) -> str:
    """Equalizador simétrico (barras prateadas) com cruz centralizada por cima."""
    return html_block(
        f"""
        <div class="ig-sb-mark-wrap">
            <div class="ig-sb-mark" aria-hidden="true">
                <div class="ig-sb-eq">
                    <span></span><span></span><span></span><span></span>
                    <span></span><span></span><span></span>
                </div>
                <div class="ig-sb-cross-overlay">{cross_html}</div>
            </div>
        </div>
        """
    )


def sidebar_brand_header_html(
    cross_html: str,
    *,
    title: str,
    subtitle: str = "Gestão Ministerial",
) -> str:
    """Cabeçalho completo da sidebar (logo + títulos + divisor) — um único bloco HTML."""
    mark = sidebar_brand_mark_html(cross_html)
    return (
        '<div class="ig-sb-brand">'
        f"{mark}"
        '<div class="ig-sb-brand-text">'
        f'<div class="ig-sb-app-name">{html_mod.escape(title)}</div>'
        f'<div class="ig-sb-app-sub">{html_mod.escape(subtitle)}</div>'
        "</div></div>"
        '<div class="ig-sb-divider" aria-hidden="true"></div>'
    )
