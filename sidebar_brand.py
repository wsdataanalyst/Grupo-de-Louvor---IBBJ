"""Marca IBBJ Louvor na sidebar — cruz dourada sobre equalizador (layout da referência)."""

from __future__ import annotations


def sidebar_brand_mark_html(cross_html: str) -> str:
    """Equalizador simétrico (barras prateadas) com cruz centralizada por cima."""
    return f"""
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
