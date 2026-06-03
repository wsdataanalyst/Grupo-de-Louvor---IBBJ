"""CSS da Sequência do Culto (módulo leve, sem Streamlit)."""


def sequencia_culto_css() -> str:
    """Estilos da letra com chave direita — web e Mobile Lab."""
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
      display: flex;
      align-items: stretch;
      gap: 0.65rem;
    }
    .seq-lyric-lines {
      flex: 1;
      min-width: 0;
      line-height: 1.55;
      font-size: 0.95rem;
      white-space: normal;
      word-break: break-word;
    }
    .seq-marc-rail {
      display: flex;
      align-items: stretch;
      gap: 0.2rem;
      flex-shrink: 0;
      max-width: min(46%, 11.5rem);
      padding-left: 0.15rem;
    }
    .seq-brace-glyph {
      font-size: clamp(1.75rem, 5vw, 2.65rem);
      font-weight: 200;
      line-height: 1;
      color: var(--seq-brace-color, #a78bfa);
      align-self: center;
      user-select: none;
      margin-right: 0.1rem;
    }
    .seq-marc-stack {
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 0.35rem;
      min-width: 0;
    }
    .seq-marc-label {
      font-size: 0.72rem;
      font-weight: 700;
      line-height: 1.35;
      color: var(--seq-marc-color, #e2e8f0);
      text-align: left;
      word-break: break-word;
    }
    .seq-marc-rail--empty .seq-marc-empty {
      font-size: 0.8rem;
      color: #64748b;
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
    @media (max-width: 520px) {
      .seq-trecho-row {
        flex-direction: row;
        align-items: flex-start;
      }
      .seq-marc-rail {
        max-width: min(44%, 9.5rem);
      }
      .seq-marc-label {
        font-size: 0.68rem;
      }
    }
    """
