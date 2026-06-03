"""CSS da Sequência do Culto (módulo leve, sem Streamlit)."""


def sequencia_culto_css() -> str:
    """Estilos da letra com chave direita — web, tablet (iPad) e Mobile Lab."""
    return r"""
    .seq-lyrics-view {
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      margin: 0.35rem 0 0.5rem;
    }
    .seq-legend, .seq-legend-banda {
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem 0.65rem;
      margin-bottom: 0.35rem;
    }
    .seq-legend-chip {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.72rem;
      font-weight: 600;
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,.12);
      color: #cbd5e1;
    }
    .seq-legend-chip i {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
    }
    .seq-lyric-block, .seq-inline-lyric {
      position: relative;
      padding: 0.75rem 0.85rem 0.75rem 2.35rem;
      border-radius: 12px;
      margin: 0.25rem 0;
      background: rgba(15, 23, 42, 0.45);
      overflow: visible !important;
    }
    .seq-trecho-num {
      position: absolute;
      left: 0.55rem;
      top: 0.7rem;
      width: 1.35rem;
      height: 1.35rem;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.72rem;
      font-weight: 800;
      color: #0f172a;
    }
    .seq-trecho-row {
      display: flex !important;
      flex-direction: row !important;
      align-items: stretch !important;
      gap: 0.65rem;
      width: 100%;
    }
    .seq-lyric-lines {
      flex: 1 1 auto;
      min-width: 0;
      line-height: 1.55;
      font-size: 0.95rem;
      white-space: normal;
      word-break: break-word;
    }
    .seq-marc-rail {
      display: flex !important;
      align-items: stretch;
      gap: 0.2rem;
      flex: 0 0 auto;
      flex-shrink: 0;
      min-width: 4.25rem;
      max-width: min(46%, 11.5rem);
      padding-left: 0.15rem;
      visibility: visible !important;
      opacity: 1 !important;
    }
    .seq-brace-glyph {
      display: inline-block !important;
      font-family: 'Inter', 'Segoe UI', Georgia, serif !important;
      font-size: clamp(1.75rem, 4.5vw, 2.65rem);
      font-weight: 200;
      line-height: 1;
      color: var(--seq-brace-color, #a78bfa) !important;
      align-self: center;
      user-select: none;
      margin-right: 0.1rem;
      flex-shrink: 0;
    }
    section.main [data-testid="stMarkdownContainer"] .seq-brace-glyph,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] .seq-brace-glyph {
      color: var(--seq-brace-color, #a78bfa) !important;
    }
    .seq-marc-stack {
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 0.35rem;
      min-width: 0;
      flex: 1 1 auto;
    }
    .seq-marc-label {
      font-size: 0.72rem;
      font-weight: 700;
      line-height: 1.35;
      color: var(--seq-marc-color, #e2e8f0) !important;
      text-align: left;
      word-break: break-word;
    }
    section.main [data-testid="stMarkdownContainer"] .seq-marc-label,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] .seq-marc-label {
      color: var(--seq-marc-color, #e2e8f0) !important;
    }
    .seq-marc-rail--empty .seq-marc-empty {
      font-size: 0.8rem;
      color: #64748b !important;
      align-self: center;
    }
    .seq-empty {
      color: #94a3b8;
      font-style: italic;
    }
    body:has(.seq-lyrics-view) [data-testid="stRadio"] > div,
    body:has(#ml-sequencia-page) [data-testid="stRadio"] > div {
      display: flex !important;
      flex-wrap: wrap !important;
      gap: 0.35rem 0.55rem !important;
    }
    body:has(.seq-lyrics-view) [data-testid="stRadio"] label,
    body:has(#ml-sequencia-page) [data-testid="stRadio"] label {
      margin-right: 0 !important;
      padding: 0.2rem 0.45rem !important;
    }
    /* Celular */
    @media (max-width: 520px) {
      .seq-trecho-row {
        flex-direction: row !important;
        align-items: flex-start !important;
      }
      .seq-marc-rail {
        min-width: 3.5rem;
        max-width: min(44%, 9.5rem);
      }
      .seq-brace-glyph {
        font-size: clamp(1.55rem, 6vw, 2.1rem);
      }
      .seq-marc-label {
        font-size: 0.68rem;
      }
    }
    /* Tablet / iPad */
    @media (min-width: 521px) and (max-width: 1024px) {
      .seq-marc-rail {
        min-width: 4.75rem;
        max-width: min(36%, 10.5rem);
      }
      .seq-brace-glyph {
        font-size: 2.15rem;
      }
      .seq-marc-label {
        font-size: 0.74rem;
      }
    }
    /* Desktop */
    @media (min-width: 1025px) {
      .seq-marc-rail {
        min-width: 5.5rem;
        max-width: 13rem;
      }
      .seq-brace-glyph {
        font-size: 2.75rem;
      }
      .seq-marc-label {
        font-size: 0.78rem;
      }
      .seq-lyric-lines {
        font-size: 1rem;
      }
    }
    """


def inject_sequencia_culto_css() -> None:
    """Injeta CSS globalmente (st.markdown — mesmo padrão do app_theme)."""
    import streamlit as st

    st.markdown(f"<style>{sequencia_culto_css()}</style>", unsafe_allow_html=True)
