"""Layout da programação do culto (equipe + louvores) — web e mobile lab."""


def culto_programa_css() -> str:
    return r"""
    .culto-week-card {
      border-radius: 18px !important;
      padding: 0.85rem 0.95rem !important;
      margin-bottom: 0.65rem !important;
    }
    .culto-week-card h3 {
      margin: 0 0 0.25rem !important;
      font-size: 1.05rem !important;
      line-height: 1.25 !important;
    }
    .culto-week-card .culto-date {
      margin: 0 !important;
      font-size: 0.82rem !important;
      line-height: 1.35 !important;
    }

    .team-grid {
      display: grid !important;
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      gap: 0.5rem !important;
      margin: 0.45rem 0 0.85rem !important;
    }
    @media (min-width: 640px) {
      .team-grid {
        grid-template-columns: repeat(auto-fill, minmax(128px, 1fr)) !important;
      }
    }
    .team-member-card {
      display: flex !important;
      flex-direction: column !important;
      align-items: center !important;
      text-align: center !important;
      padding: 0.6rem 0.4rem !important;
      border-radius: 16px !important;
      background: rgba(15, 23, 42, 0.55) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      min-width: 0 !important;
    }
    .team-member-card img,
    .team-member-card .member-avatar {
      width: 52px !important;
      height: 52px !important;
      border-radius: 16px !important;
      object-fit: cover !important;
      margin: 0 0 0.35rem !important;
      border: 2px solid rgba(139, 92, 246, 0.35) !important;
      flex-shrink: 0 !important;
    }
    .team-member-card .member-avatar-ph {
      width: 52px !important;
      height: 52px !important;
      border-radius: 16px !important;
      margin: 0 0 0.35rem !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      background: rgba(124, 58, 237, 0.22) !important;
      border: 2px solid rgba(139, 92, 246, 0.35) !important;
      color: #e9d5ff !important;
      font-weight: 900 !important;
      font-size: 1.1rem !important;
      flex-shrink: 0 !important;
    }
    .team-member-card .tm-name {
      margin: 0 !important;
      font-size: 0.8rem !important;
      font-weight: 800 !important;
      line-height: 1.2 !important;
      color: #f1f5f9 !important;
      word-break: break-word !important;
      width: 100% !important;
    }
    .team-member-card .tm-role {
      margin: 0.22rem 0 0 !important;
      font-size: 0.65rem !important;
      font-weight: 700 !important;
      color: #94a3b8 !important;
      text-transform: uppercase !important;
      letter-spacing: 0.03em !important;
      line-height: 1.2 !important;
    }

    .prog-card {
      padding: 0.85rem 0.9rem !important;
      margin-bottom: 0.6rem !important;
      border-radius: 18px !important;
      overflow: hidden !important;
    }
    .prog-head {
      display: flex !important;
      align-items: center !important;
      gap: 0.45rem !important;
      margin-bottom: 0.35rem !important;
      flex-wrap: wrap !important;
    }
    .prog-card .seq-badge {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      min-width: 1.55rem !important;
      height: 1.55rem !important;
      padding: 0 0.35rem !important;
      border-radius: 10px !important;
      background: rgba(124, 58, 237, 0.35) !important;
      border: 1px solid rgba(139, 92, 246, 0.35) !important;
      font-weight: 800 !important;
      font-size: 0.76rem !important;
      color: #e9d5ff !important;
      flex-shrink: 0 !important;
    }
    .prog-card .prog-parte {
      font-size: 0.68rem !important;
      font-weight: 800 !important;
      text-transform: uppercase !important;
      letter-spacing: 0.04em !important;
      line-height: 1.2 !important;
    }
    .prog-card .prog-louvor {
      margin: 0 0 0.45rem !important;
      font-size: 0.94rem !important;
      font-weight: 800 !important;
      line-height: 1.3 !important;
      word-break: break-word !important;
    }
    .prog-meta-chips {
      display: flex !important;
      flex-wrap: wrap !important;
      gap: 0.35rem !important;
      margin-bottom: 0.55rem !important;
    }
    .prog-chip {
      display: inline-flex !important;
      align-items: center !important;
      padding: 0.22rem 0.5rem !important;
      border-radius: 999px !important;
      background: rgba(15, 23, 42, 0.85) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      font-size: 0.68rem !important;
      color: #94a3b8 !important;
      line-height: 1.25 !important;
      max-width: 100% !important;
      word-break: break-word !important;
    }
    .prog-chip-ref {
      flex: 1 1 100% !important;
      border-radius: 10px !important;
    }
    .prog-actions {
      display: grid !important;
      grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      gap: 0.4rem !important;
      width: 100% !important;
    }
    @media (min-width: 720px) {
      .prog-actions {
        grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)) !important;
      }
    }
    .prog-btn {
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      min-height: 2.35rem !important;
      padding: 0.4rem 0.45rem !important;
      border-radius: 12px !important;
      font-size: 0.7rem !important;
      font-weight: 700 !important;
      text-decoration: none !important;
      text-align: center !important;
      line-height: 1.2 !important;
      white-space: normal !important;
      word-break: break-word !important;
      box-sizing: border-box !important;
      border: 1px solid rgba(255, 255, 255, 0.1) !important;
      overflow: hidden !important;
    }
    .prog-btn-yt {
      background: rgba(220, 38, 38, 0.14) !important;
      color: #fca5a5 !important;
      border-color: rgba(239, 68, 68, 0.25) !important;
    }
    .prog-btn-kit {
      background: rgba(124, 58, 237, 0.14) !important;
      color: #c4b5fd !important;
      border-color: rgba(139, 92, 246, 0.25) !important;
    }
    .prog-btn-letra {
      background: rgba(14, 116, 144, 0.14) !important;
      color: #67e8f9 !important;
      border-color: rgba(34, 211, 238, 0.25) !important;
      grid-column: 1 / -1 !important;
    }

    body:has(#ml-escalas-page) .prog-card,
    body:has(#ml-escalas-page) .team-member-card {
      background: rgba(15, 23, 42, 0.72) !important;
    }
    body:has(#ml-escalas-page) [data-testid="stMarkdownContainer"]:has(.prog-card),
    body:has(#ml-escalas-page) [data-testid="stMarkdownContainer"]:has(.team-grid) {
      overflow: visible !important;
    }
    body:has(#ml-escalas-page) .prog-actions {
      padding-bottom: 0.15rem !important;
    }
    """
