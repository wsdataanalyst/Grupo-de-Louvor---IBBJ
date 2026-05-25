"""Tema IGREJA Gestão Ministerial — dark elegante, ouro + teal, alto contraste."""

from __future__ import annotations


def ibbj_theme_css() -> str:
    return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --ig-bg: #121212;
            --ig-bg-elevated: #1a1a1a;
            --ig-bg-card: #1e1e1e;
            --ig-bg-input: #252525;
            --ig-gold: #d4af37;
            --ig-gold-soft: rgba(212, 175, 55, 0.15);
            --ig-gold-border: rgba(212, 175, 55, 0.55);
            --ig-teal: #20b2aa;
            --ig-cyan: #00c2cb;
            --ig-green: #34d399;
            --ig-text: #f5f5f5;
            --ig-text-muted: #9ca3af;
            --ig-text-dim: #6b7280;
            --ig-border: rgba(255, 255, 255, 0.08);
            --ig-border-strong: rgba(255, 255, 255, 0.14);
            --ig-radius: 12px;
            --ig-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
            --bg-deep: var(--ig-bg);
            --bg-surface: var(--ig-bg-card);
            --bg-elevated: var(--ig-bg-elevated);
            --text-primary: var(--ig-text);
            --text-secondary: var(--ig-text-muted);
            --accent-gold: var(--ig-gold);
            --accent-violet: var(--ig-teal);
            --border-subtle: var(--ig-border);
            --border-accent: var(--ig-gold-border);
            --radius-lg: var(--ig-radius);
            --radius-md: 10px;
            --shadow-card: var(--ig-shadow);
            --ig-content-max: 1280px;
            --ig-content-pad-x: 1.25rem;
            /* Login — mobile-first (sobrescreve por breakpoint) */
            --ig-login-card-w: calc(100% - 1.5rem);
            --ig-login-card-max: 100%;
            --ig-login-card-pad: 1.35rem 1rem 1.15rem;
            --ig-login-card-radius: 18px;
            --ig-login-main-pad: 0.65rem 0 1rem;
        }

        html {
            -webkit-text-size-adjust: 100%;
            text-size-adjust: 100%;
        }
        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
        }

        [data-testid="stAppViewContainer"] {
            background: var(--ig-bg) !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            border: none !important;
        }

        /* ========== App logado: NÃO alterar flex/width da sidebar (layout nativo Streamlit) ========== */
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) {
            overflow-x: hidden !important;
            max-width: 100vw !important;
        }
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) section.main,
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMain"],
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMainBlockContainer"] {
            min-width: 0 !important;
        }
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) .main .block-container,
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMain"] .block-container,
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMainBlockContainer"] .block-container {
            width: 100% !important;
            max-width: var(--ig-content-max) !important;
            padding-top: 0.5rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: var(--ig-content-pad-x) !important;
            padding-right: var(--ig-content-pad-x) !important;
            margin-left: auto !important;
            margin-right: auto !important;
            box-sizing: border-box !important;
        }
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: 0 !important;
        }
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) section.main img,
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMain"] img {
            max-width: 100% !important;
            height: auto !important;
        }
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stDataFrame"],
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stDataFrame"] > div {
            max-width: 100% !important;
        }

        /* Tablet — conteúdo + login */
        @media (min-width: 769px) and (max-width: 1100px) {
            :root {
                --ig-content-max: 100%;
                --ig-content-pad-x: 1.5rem;
                --ig-login-card-w: min(400px, 88vw);
                --ig-login-card-max: 400px;
                --ig-login-card-pad: 1.75rem 1.35rem 1.35rem;
                --ig-login-card-radius: 20px;
                --ig-login-main-pad: 1.25rem 0 1.5rem;
            }
        }
        /* Desktop */
        @media (min-width: 1101px) {
            :root {
                --ig-content-max: 1280px;
                --ig-content-pad-x: 2rem;
                --ig-login-card-w: 420px;
                --ig-login-card-max: 420px;
                --ig-login-card-pad: 2rem 1.65rem 1.5rem;
                --ig-login-card-radius: 22px;
                --ig-login-main-pad: 0 0 2rem;
            }
        }
        /* Smartphone — app logado: área principal em largura total; menu em gaveta (Streamlit) */
        @media (max-width: 768px) {
            :root {
                --ig-content-max: 100%;
                --ig-content-pad-x: 0.65rem;
            }
            [data-testid="stAppViewContainer"]:not(:has(.login-page)) section.main,
            [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMain"] {
                width: 100% !important;
                max-width: 100% !important;
            }
            [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
            }
            [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 100% !important;
                min-width: 0 !important;
            }
        }

        /* Só iframes de scripts (height 0/1) — não esconde widgets do Streamlit */
        section.main div[data-testid="element-container"]:has(iframe[height="0"]),
        section.main div[data-testid="element-container"]:has(iframe[height="1"]),
        [data-testid="stMain"] div[data-testid="element-container"]:has(iframe[height="0"]),
        [data-testid="stMain"] div[data-testid="element-container"]:has(iframe[height="1"]) {
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            border: none !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stHtml"] {
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        #app-bell-notif {
            position: fixed; top: 0.65rem; right: 0.75rem; z-index: 9999;
            width: 2.5rem; height: 2.5rem; border-radius: 50%;
            background: #1e1e1e;
            border: 1px solid rgba(212, 175, 55, 0.45);
            align-items: center; justify-content: center;
            font-size: 1.2rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
            pointer-events: none;
        }
        .nav-wa-badge {
            position: absolute; top: -3px; right: -3px;
            left: auto;
            min-width: 1.2rem; height: 1.2rem;
            padding: 0 0.34rem; border-radius: 999px;
            background: #ff453a; color: #fff;
            font-size: 0.62rem; font-weight: 800;
            display: flex; align-items: center; justify-content: center;
            border: 2px solid #121212;
            box-shadow: 0 2px 6px rgba(255, 69, 58, 0.45);
        }

        /* ========== Sidebar premium v2 (IBBJ Louvor) ========== */
        section[data-testid="stSidebar"] {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
            background: linear-gradient(180deg, #030712 0%, #0a0f1a 55%, #030712 100%) !important;
            border-right: 1px solid rgba(37, 99, 235, 0.12) !important;
            box-shadow: 4px 0 32px rgba(0, 0, 0, 0.45), inset -1px 0 0 rgba(37, 99, 235, 0.08) !important;
        }
        section[data-testid="stSidebar"] > div {
            padding: 0.5rem 0.45rem 1rem !important;
            margin: 0.35rem 0.25rem 0.35rem 0.35rem !important;
            border-radius: 24px !important;
            background: rgba(3, 7, 18, 0.88) !important;
            border: 1px solid rgba(37, 99, 235, 0.14) !important;
            box-shadow:
                0 0 48px rgba(37, 99, 235, 0.07),
                inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
        }
        section[data-testid="stSidebar"] .stCaption {
            color: #94a3b8 !important;
            font-size: 0.72rem !important;
        }

        .ig-sb-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            text-align: left;
            padding: 0.5rem 0.35rem 1rem;
            margin-bottom: 0.15rem;
        }
        /* Marca: equalizador prateado + cruz dourada centralizada (ref. UI) */
        .ig-sb-mark {
            position: relative;
            flex-shrink: 0;
            width: 54px;
            height: 50px;
        }
        .ig-sb-mark .ig-sb-eq {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 3px;
            height: 100%;
            padding: 0 2px 1px;
        }
        .ig-sb-mark .ig-sb-eq span {
            display: block;
            width: 4px;
            border-radius: 2px;
            background: linear-gradient(
                180deg,
                #f8fafc 0%,
                #e2e8f0 38%,
                #94a3b8 72%,
                rgba(148, 163, 184, 0.35) 100%
            );
            box-shadow: 0 0 8px rgba(248, 250, 252, 0.22);
        }
        .ig-sb-mark .ig-sb-eq span:nth-child(1) { height: 9px; }
        .ig-sb-mark .ig-sb-eq span:nth-child(2) { height: 15px; }
        .ig-sb-mark .ig-sb-eq span:nth-child(3) { height: 22px; }
        .ig-sb-mark .ig-sb-eq span:nth-child(4) { height: 28px; }
        .ig-sb-mark .ig-sb-eq span:nth-child(5) { height: 22px; }
        .ig-sb-mark .ig-sb-eq span:nth-child(6) { height: 15px; }
        .ig-sb-mark .ig-sb-eq span:nth-child(7) { height: 9px; }
        .ig-sb-mark .ig-sb-cross-overlay {
            position: absolute;
            left: 50%;
            top: 46%;
            transform: translate(-50%, -50%);
            z-index: 2;
            pointer-events: none;
            line-height: 0;
        }
        .ig-sb-mark .ig-sb-cross-overlay img.login-cross,
        .ig-sb-mark .ig-sb-cross-overlay .login-cross {
            display: block;
            width: 34px !important;
            height: auto !important;
            margin: 0 !important;
            filter: drop-shadow(0 2px 10px rgba(212, 175, 55, 0.55));
        }
        .ig-sb-brand-text { min-width: 0; flex: 1; }
        .ig-sb-app-name {
            margin: 0 0 0.2rem;
            font-size: 1.08rem;
            font-weight: 700;
            color: #f8fafc !important;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }
        .ig-sb-app-sub {
            margin: 0;
            font-size: 0.6rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #d4a017 !important;
        }

        .ig-sb-profile-card {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 0.85rem 0.75rem;
            margin: 0 0 0.65rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }
        .ig-sb-avatar-wrap {
            position: relative;
            flex-shrink: 0;
            width: 3.35rem;
            height: 3.35rem;
        }
        .ig-sb-avatar-glow {
            position: absolute;
            inset: -18px;
            border-radius: 50%;
            background: radial-gradient(
                circle,
                rgba(56, 189, 248, 0.7) 0%,
                rgba(37, 99, 235, 0.4) 40%,
                transparent 70%
            );
            filter: blur(12px);
            opacity: 1;
            z-index: 0;
        }
        .ig-sb-avatar-ring {
            position: absolute;
            inset: -2px;
            border-radius: 50%;
            border: 2.5px solid rgba(125, 211, 252, 1);
            box-shadow:
                0 0 0 1px rgba(224, 242, 254, 0.55),
                0 0 14px 4px rgba(56, 189, 248, 0.75),
                0 0 28px 10px rgba(37, 99, 235, 0.5),
                0 0 44px 16px rgba(37, 99, 235, 0.28);
            z-index: 2;
            pointer-events: none;
        }
        .ig-sb-avatar {
            position: relative;
            z-index: 1;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            overflow: hidden;
            border: none;
            background: linear-gradient(165deg, #1e3a5f 0%, #0c1929 55%, #0a0e1a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.35);
        }
        .ig-sb-avatar img { width: 100%; height: 100%; object-fit: cover; }
        .ig-sb-avatar-letter {
            font-size: 1.1rem;
            font-weight: 700;
            color: #7dd3fc;
        }
        .ig-sb-avatar-ph {
            display: block;
            width: 100%;
            height: 100%;
            opacity: 1;
        }
        .ig-sb-profile-text { min-width: 0; flex: 1; }
        .ig-sb-user-name {
            display: block;
            color: #f8fafc !important;
            font-size: 0.95rem;
            font-weight: 700;
            line-height: 1.25;
        }
        .ig-sb-user-role {
            display: block;
            color: #94a3b8 !important;
            font-size: 0.74rem;
            margin-top: 0.18rem;
            line-height: 1.35;
        }
        .ig-sb-role-badge {
            display: inline-block;
            margin-top: 0.4rem;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.64rem;
            font-weight: 600;
            color: #93c5fd !important;
            background: rgba(30, 58, 138, 0.92);
            border: 1px solid rgba(59, 130, 246, 0.45);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
        }

        .ig-sb-nav-group {
            color: #64748b !important;
            font-size: 0.58rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.14em !important;
            margin: 0.75rem 0 0.35rem 0.45rem !important;
            padding: 0 !important;
        }
        .ig-sb-nav { display: block; margin-bottom: 0.35rem; }

        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] {
            position: relative !important;
            margin-bottom: 0.2rem !important;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] .stButton > button {
            width: 100% !important;
            min-height: 2.55rem !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            text-align: left !important;
            padding: 0.55rem 2.1rem 0.55rem 0.65rem !important;
            border-radius: 12px !important;
            font-size: 0.84rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.01em !important;
            transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease !important;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] .stButton > button[kind="secondary"] {
            background: transparent !important;
            color: #cbd5e1 !important;
            border: 1px solid transparent !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] .stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.05) !important;
            border-color: rgba(255, 255, 255, 0.08) !important;
            color: #f8fafc !important;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] .stButton > button[kind="primary"] {
            background: linear-gradient(
                135deg,
                rgba(37, 99, 235, 0.55) 0%,
                rgba(37, 99, 235, 0.18) 100%
            ) !important;
            color: #93c5fd !important;
            border: 1px solid rgba(37, 99, 235, 0.45) !important;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.28), inset 0 1px 0 rgba(96, 165, 250, 0.2) !important;
            font-weight: 600 !important;
        }
        .ig-sb-tools-sep {
            height: 1px;
            margin: 0.75rem 0.5rem 0.55rem;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(37, 99, 235, 0.35) 50%,
                transparent 100%
            );
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] .nav-wa-badge {
            position: absolute !important;
            right: 0.5rem !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            border-color: #030712 !important;
            z-index: 6 !important;
        }

        .ig-sb-tools-card {
            margin: 0.85rem 0 0.5rem;
            padding: 0.65rem 0.55rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(255, 255, 255, 0.07);
        }
        .ig-sb-tools-title {
            color: #94a3b8 !important;
            font-size: 0.58rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.14em !important;
            text-transform: uppercase !important;
            margin: 0 0 0.4rem 0.35rem !important;
        }
        section[data-testid="stSidebar"] .ig-sb-tools-card [data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px !important;
            margin-bottom: 0.35rem !important;
        }
        section[data-testid="stSidebar"] .ig-sb-tools-card .streamlit-expanderHeader {
            background: transparent !important;
            border: none !important;
            color: #e2e8f0 !important;
            font-size: 0.78rem !important;
            padding: 0.45rem 0.5rem !important;
            border-radius: 12px !important;
        }
        section[data-testid="stSidebar"] .ig-sb-tools-card .streamlit-expanderHeader:hover {
            background: rgba(255, 255, 255, 0.04) !important;
        }

        section[data-testid="stSidebar"] [class*="st-key-ig_sidebar_logout"] .stButton > button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 2.6rem !important;
            border-radius: 12px !important;
            background: rgba(127, 29, 29, 0.35) !important;
            border: 1px solid rgba(239, 68, 68, 0.45) !important;
            color: #fca5a5 !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_sidebar_logout"] .stButton > button:hover {
            background: rgba(185, 28, 28, 0.45) !important;
            color: #fecaca !important;
        }

        .ig-sb-footer-verse {
            text-align: center;
            margin-top: 0.85rem;
            padding: 0.65rem 0.35rem 0.25rem;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
        }
        .ig-sb-footer-heart { color: #d4a017; font-size: 0.85rem; }
        .ig-sb-footer-text {
            margin: 0.35rem 0 0.15rem;
            font-size: 0.68rem;
            line-height: 1.45;
            color: #94a3b8 !important;
            font-style: italic;
        }
        .ig-sb-footer-ref {
            margin: 0;
            font-size: 0.72rem;
            font-weight: 600;
            color: #d4a017 !important;
        }

        /* ========== Área principal — dark ========== */
        section.main, [data-testid="stMain"] {
            color: var(--ig-text) !important;
        }
        section.main [data-testid="stMarkdownContainer"] p,
        section.main [data-testid="stMarkdownContainer"] li,
        section.main [data-testid="stMarkdownContainer"] span,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p {
            color: var(--ig-text) !important;
        }
        section.main h1, section.main h2, section.main h3, section.main h4,
        [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 {
            color: var(--ig-text) !important;
        }
        section.main .stCaption, [data-testid="stMain"] .stCaption {
            color: var(--ig-text-muted) !important;
        }

        /* KPI cards */
        .ig-kpi-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
            gap: 0.85rem;
            margin: 0 0 1.25rem;
        }
        .ig-kpi-card {
            background: var(--ig-bg-card);
            border: 1px solid var(--ig-border);
            border-radius: var(--ig-radius);
            padding: 1.1rem 1.15rem;
            box-shadow: var(--ig-shadow);
            min-height: 5.5rem;
        }
        .ig-kpi-icon {
            font-size: 1.35rem;
            display: block;
            margin-bottom: 0.55rem;
            line-height: 1;
        }
        .ig-kpi-card--0 .ig-kpi-icon { color: var(--ig-teal); }
        .ig-kpi-card--1 .ig-kpi-icon { color: var(--ig-cyan); }
        .ig-kpi-card--2 .ig-kpi-icon { color: var(--ig-green); }
        .ig-kpi-card--3 .ig-kpi-icon { color: #e5e7eb; }
        .ig-kpi-value {
            display: block;
            font-size: 2rem;
            font-weight: 800;
            color: #fff;
            line-height: 1;
            letter-spacing: -0.02em;
        }
        .ig-kpi-label {
            display: block;
            font-size: 0.7rem;
            font-weight: 600;
            color: var(--ig-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 0.35rem;
        }

        /* Cabeçalho de página */
        .music-hero {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: var(--ig-radius) !important;
            box-shadow: var(--ig-shadow) !important;
            padding: 1.1rem 1.25rem !important;
            margin-bottom: 1rem !important;
            position: relative;
            overflow: hidden;
        }
        .music-hero::after {
            content: "";
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 4px;
            background: var(--accent, var(--ig-gold));
            border-radius: 4px 0 0 4px;
        }
        .music-hero h2 {
            color: #fff !important;
            font-size: 1.35rem !important;
            font-weight: 700 !important;
        }
        .music-hero p {
            color: var(--ig-text-muted) !important;
        }

        .welcome-card {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-left: 4px solid var(--ig-gold) !important;
            border-radius: var(--ig-radius) !important;
            padding: 1.2rem 1.3rem !important;
            margin-bottom: 1rem !important;
        }
        .welcome-card h3 { color: #fff !important; }
        .welcome-card p { color: var(--ig-text-muted) !important; }

        /* Dashboard sections */
        .dash-section {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: var(--ig-radius) !important;
            margin-bottom: 1rem;
        }
        .dash-section-header {
            background: var(--ig-bg-elevated) !important;
            border-bottom: 1px solid var(--ig-border) !important;
            border-left: 4px solid var(--dash-accent, var(--ig-teal)) !important;
        }
        .dash-section-header h4 { color: #fff !important; }
        .dash-section-sub { color: var(--ig-text-muted) !important; }

        /* Abas — teal ativo */
        div[data-testid="stTabs"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            border-bottom: 1px solid var(--ig-border) !important;
            gap: 0.25rem;
        }
        div[data-testid="stTabs"] [data-baseweb="tab"] {
            color: var(--ig-text-muted) !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            background: transparent !important;
        }
        div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            color: var(--ig-teal) !important;
            border-bottom: 3px solid var(--ig-teal) !important;
        }

        /* Formulários */
        section.main label,
        section.main [data-testid="stWidgetLabel"] p,
        [data-testid="stMain"] label,
        [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
            color: #e5e7eb !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
        }
        section.main input, section.main textarea,
        [data-testid="stMain"] input, [data-testid="stMain"] textarea {
            background-color: var(--ig-bg-input) !important;
            color: #fff !important;
            -webkit-text-fill-color: #fff !important;
            border: 1px solid var(--ig-border-strong) !important;
            border-radius: var(--ig-radius) !important;
        }
        section.main [data-baseweb="input"],
        [data-testid="stMain"] [data-baseweb="input"] {
            background-color: var(--ig-bg-input) !important;
            border: 1px solid var(--ig-border-strong) !important;
            border-radius: var(--ig-radius) !important;
        }
        section.main [data-baseweb="input"] input,
        [data-testid="stMain"] [data-baseweb="input"] input {
            color: #fff !important;
            -webkit-text-fill-color: #fff !important;
        }
        section.main [data-baseweb="select"] > div,
        [data-testid="stMain"] [data-baseweb="select"] > div {
            background-color: var(--ig-bg-input) !important;
            color: #fff !important;
            border-color: var(--ig-border-strong) !important;
        }
        section.main [data-baseweb="tag"],
        [data-testid="stMain"] [data-baseweb="tag"] {
            background: #374151 !important;
            color: #f3f4f6 !important;
        }
        div[data-testid="stForm"] {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: var(--ig-radius) !important;
        }

        /* Botões */
        section.main .stButton > button[kind="primary"],
        section.main .stFormSubmitButton > button,
        section.main button[kind="primaryFormSubmit"],
        [data-testid="stMain"] .stButton > button[kind="primary"],
        [data-testid="stMain"] .stFormSubmitButton > button {
            background: linear-gradient(135deg, #c9a227 0%, var(--ig-gold) 100%) !important;
            color: #1a1208 !important;
            border: 1px solid #a88b2a !important;
            font-weight: 700 !important;
        }
        section.main .stButton > button[kind="secondary"],
        [data-testid="stMain"] .stButton > button[kind="secondary"] {
            background: var(--ig-bg-input) !important;
            color: var(--ig-text) !important;
            border: 1px solid var(--ig-border-strong) !important;
        }

        section.main .streamlit-expanderHeader,
        [data-testid="stMain"] .streamlit-expanderHeader {
            color: var(--ig-text) !important;
            background: var(--ig-bg-card) !important;
        }
        section.main a, [data-testid="stMain"] a {
            color: var(--ig-teal) !important;
        }

        /* Painéis e cards */
        .music-panel, .profile-card, .sugestao-track-card,
        .culto-week-card, .feed-post-card, .event-feed-card, .prog-card, .swap-card {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            color: var(--ig-text) !important;
        }
        .music-panel-title, .culto-week-card h3, .sugestao-track-title {
            color: var(--ig-gold) !important;
        }
        .sugestao-track-meta, .culto-week-card .culto-date, .prog-card .prog-meta {
            color: var(--ig-text-muted) !important;
        }
        .prog-card .prog-parte { color: var(--ig-teal) !important; }
        .prog-card .prog-louvor { color: #fff !important; }

        /* Painel do mês */
        .planner-panel-card {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: var(--ig-radius) !important;
            padding: 1rem 1.1rem !important;
            margin-bottom: 0.75rem !important;
        }
        .planner-title {
            color: #fff !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            margin: 0 0 0.25rem !important;
        }
        .planner-title .planner-icon-gold { color: var(--ig-gold); margin-right: 0.35rem; }
        .planner-sub {
            color: var(--ig-text-muted) !important;
            font-size: 0.75rem !important;
            margin: 0 !important;
        }
        .planner-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.35rem 0.5rem;
            padding: 0.55rem 0;
            border-bottom: 1px solid var(--ig-border);
        }
        .planner-name {
            color: #fff !important;
            font-weight: 500 !important;
            font-size: 0.84rem !important;
            flex: 1 1 100%;
        }
        .planner-badge-warn {
            display: inline-block;
            padding: 0.12rem 0.5rem;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 700;
            background: var(--ig-gold-soft);
            color: var(--ig-gold);
            border: 1px solid var(--ig-gold-border);
        }
        .planner-badge-ok {
            display: inline-block;
            padding: 0.12rem 0.5rem;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 700;
            background: rgba(52, 211, 153, 0.15);
            color: var(--ig-green);
            border: 1px solid rgba(52, 211, 153, 0.35);
        }
        .planner-date {
            color: var(--ig-text-dim) !important;
            font-size: 0.72rem !important;
        }

        .section-heading {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0 0 1rem;
        }
        .section-heading h3, .section-heading h4 {
            margin: 0 !important;
            color: #fff !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
        }
        .section-heading-icon { color: var(--ig-teal); font-size: 1.25rem; }

        .planner-column-wrap {
            background: var(--ig-bg-elevated);
            border: 1px solid var(--ig-border);
            border-radius: var(--ig-radius);
            padding: 0.65rem 0.75rem 1rem;
        }

        /* Chat */
        #chat-scroll-box {
            background: var(--ig-bg-elevated) !important;
            border: 1px solid var(--ig-border) !important;
        }
        .chat-row-name { color: #fff !important; }
        .chat-row-time, .chat-meta { color: var(--ig-text-muted) !important; }
        .chat-bubble.other {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
        }
        .chat-bubble.other .chat-text { color: var(--ig-text) !important; }
        .chat-bubble.me {
            background: linear-gradient(135deg, #178f88, var(--ig-teal)) !important;
        }
        .chat-bubble.me .chat-text { color: #fff !important; }

        .verse-of-day {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-left: 4px solid var(--ig-gold) !important;
        }
        .verse-of-day .verse-label { color: var(--ig-gold) !important; }
        .verse-of-day .verse-text { color: #fff !important; }
        .verse-of-day .verse-ref { color: var(--ig-text-muted) !important; }

        .status-escalado {
            background: rgba(52, 211, 153, 0.1) !important;
            border: 1px solid rgba(52, 211, 153, 0.35) !important;
            color: var(--ig-text) !important;
        }
        .status-escalado strong, .status-escalado .escala-evento { color: #a7f3d0 !important; }
        .status-nao-escalado {
            background: var(--ig-gold-soft) !important;
            border: 1px solid var(--ig-gold-border) !important;
            color: #fde68a !important;
        }

        .sugestao-status--pendente { background: rgba(251, 191, 36, 0.15) !important; color: #fcd34d !important; }
        .sugestao-status--em_analise { background: rgba(32, 178, 170, 0.15) !important; color: var(--ig-teal) !important; }
        .sugestao-status--aprovada { background: rgba(52, 211, 153, 0.15) !important; color: var(--ig-green) !important; }
        .sugestao-status--recusada { background: rgba(239, 68, 68, 0.15) !important; color: #fca5a5 !important; }

        .members-leader-wrap {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
        }
        .members-leader-table { color: var(--ig-text) !important; }
        .members-leader-table th {
            background: var(--ig-bg-elevated) !important;
            color: var(--ig-gold) !important;
        }
        .members-leader-table .mem-nome { color: #fff !important; }
        .members-leader-table .mem-funcao { color: var(--ig-text-muted) !important; }

        .music-pagination {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            color: var(--ig-text-muted) !important;
        }
        .music-pagination strong { color: var(--ig-gold) !important; }

        div[data-testid="stMetric"] {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
        }
        div[data-testid="stMetric"] label { color: var(--ig-text-muted) !important; }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; }

        .quick-nav-btn .stButton > button {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            color: var(--ig-text) !important;
        }
        .quick-nav-btn .stButton > button:hover {
            border-color: var(--ig-gold-border) !important;
            color: var(--ig-gold) !important;
        }

        .seq-cifra-panel, .seq-cifra-view, .seq-lyric-block {
            background: var(--ig-bg-card) !important;
            border-color: var(--ig-border) !important;
        }
        .seq-lyric-lines, .seq-cifra-pre { color: var(--ig-text) !important; }
        .seq-cifra-meta, .seq-empty { color: var(--ig-text-muted) !important; }
        .cifra-chord-line, .cifra-chord { color: var(--ig-gold) !important; }

        #app-bell-notif {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-gold-border) !important;
        }

        /* Alertas Streamlit no dark */
        .main .stSuccess { background: rgba(52, 211, 153, 0.12) !important; color: #6ee7b7 !important; }
        .main .stInfo { background: rgba(32, 178, 170, 0.12) !important; color: #5eead4 !important; }
        .main .stWarning { background: var(--ig-gold-soft) !important; color: #fde68a !important; }
        .main .stError { background: rgba(239, 68, 68, 0.12) !important; color: #fca5a5 !important; }

        /* Login */
        .login-hero {
            background: linear-gradient(165deg, #0f0f0f, var(--ig-bg-elevated)) !important;
            border: 1px solid var(--ig-border) !important;
        }
        .login-hero h1, .login-hero-quote { color: #fff !important; }
        .login-hero-ref { color: var(--ig-gold) !important; }
        .login-form-card {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
        }
        .login-panel-title { color: #fff !important; }
        .login-panel-sub { color: var(--ig-text-muted) !important; }
        .login-form-card label, .login-form-card [data-testid="stWidgetLabel"] p {
            color: #e5e7eb !important;
        }
        .login-form-card input {
            background: var(--ig-bg-input) !important;
            color: #fff !important;
        }
        .login-form-card .stButton > button[kind="primary"],
        .login-form-card .stFormSubmitButton > button {
            background: linear-gradient(135deg, #c9a227, var(--ig-gold)) !important;
            color: #1a1208 !important;
        }

        .ig-footer {
            text-align: center;
            color: var(--ig-text-dim);
            font-size: 0.72rem;
            margin-top: 2rem;
            padding: 1rem 0;
        }

        .ig-page-lead {
            color: var(--ig-text-muted);
            font-size: 0.88rem;
            margin: 0 0 1rem;
        }

        input::placeholder, textarea::placeholder {
            color: #6b7280 !important;
            opacity: 1 !important;
        }

        /* DataFrames e tabelas */
        [data-testid="stDataFrame"] {
            border: 1px solid var(--ig-border) !important;
            border-radius: var(--ig-radius) !important;
        }
        section.main div[data-testid="stRadio"] > label,
        [data-testid="stMain"] div[data-testid="stRadio"] > label {
            color: var(--ig-text) !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: var(--ig-border) !important;
        }

        @media (max-width: 768px) {
            .ig-kpi-row { grid-template-columns: 1fr 1fr; }
            input, textarea, select { font-size: 16px !important; }
        }
        @media (min-width: 1101px) {
            .music-hero h2 { font-size: 1.45rem !important; }
            .ig-kpi-row { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        }
    """


def ibbj_login_v2_css() -> str:
    """Login glassmorphism — IBBJ Louvor (repaginação fase 1)."""
    return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Great+Vibes&display=swap');

        [data-testid="stAppViewContainer"]:has(.login-page) section[data-testid="stSidebar"],
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stSidebarCollapsedControl"],
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) {
            background:
                linear-gradient(165deg, rgba(8, 12, 22, 0.94) 0%, rgba(11, 14, 20, 0.97) 45%, rgba(6, 10, 18, 0.98) 100%),
                radial-gradient(ellipse 80% 50% at 50% -10%, rgba(32, 178, 170, 0.18), transparent 55%),
                radial-gradient(ellipse 60% 40% at 80% 100%, rgba(212, 175, 55, 0.08), transparent 50%),
                #0b0e14 !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) {
            overflow-x: hidden !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: flex-start !important;
            min-height: 100dvh !important;
            min-height: 100vh !important;
            padding: var(--ig-login-main-pad) !important;
            box-sizing: border-box !important;
            overflow-x: hidden !important;
        }
        /* Card login: variáveis CSS mudam por breakpoint (celular / tablet / desktop) */
        [data-testid="stAppViewContainer"]:has(.login-page) .main .block-container,
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .block-container {
            width: var(--ig-login-card-w) !important;
            max-width: var(--ig-login-card-max) !important;
            min-width: 0 !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: var(--ig-login-card-pad) !important;
            box-sizing: border-box !important;
            background: rgba(15, 23, 42, 0.58) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: var(--ig-login-card-radius) !important;
            box-shadow:
                0 24px 64px rgba(0, 0, 0, 0.55),
                inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }
        @media (min-width: 769px) {
            [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] {
                justify-content: center !important;
            }
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="element-container"],
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stHorizontalBlock"],
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stForm"] {
            max-width: 100% !important;
            width: 100% !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            gap: 0.5rem !important;
        }
        .login-v2-header { text-align: center; margin-bottom: 1.35rem; }
        .login-logo-stack {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.35rem;
        }
        .login-logo-stack img.login-cross {
            width: 52px;
            height: auto;
            filter: drop-shadow(0 4px 14px rgba(212, 175, 55, 0.35));
        }
        .login-eq {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 5px;
            height: 32px;
            margin-top: 2px;
        }
        .login-eq span {
            display: block;
            width: 5px;
            border-radius: 3px;
            background: linear-gradient(180deg, #f7e7b6 0%, #d4af37 55%, rgba(212, 175, 55, 0.45) 100%);
            animation: loginEqPulse 1.4s ease-in-out infinite;
        }
        .login-eq span:nth-child(1) { height: 10px; animation-delay: 0s; }
        .login-eq span:nth-child(2) { height: 18px; animation-delay: 0.12s; }
        .login-eq span:nth-child(3) { height: 26px; animation-delay: 0.24s; }
        .login-eq span:nth-child(4) { height: 14px; animation-delay: 0.08s; }
        .login-eq span:nth-child(5) { height: 22px; animation-delay: 0.2s; }
        .login-eq span:nth-child(6) { height: 16px; animation-delay: 0.16s; }
        .login-eq span:nth-child(7) { height: 12px; animation-delay: 0.28s; }
        @keyframes loginEqPulse {
            0%, 100% { transform: scaleY(0.75); opacity: 0.75; }
            50% { transform: scaleY(1); opacity: 1; }
        }
        .login-v2-title {
            margin: 0.85rem 0 0.35rem;
            font-size: 1.65rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #fff !important;
            line-height: 1.2;
        }
        .login-v2-tagline {
            margin: 0;
            font-size: 0.92rem;
            color: rgba(255, 255, 255, 0.82) !important;
            line-height: 1.45;
        }
        .login-v2-script {
            font-family: 'Great Vibes', cursive;
            font-size: 1.35rem;
            color: #d4af37 !important;
            display: inline-block;
            margin-left: 0.15rem;
        }
        .login-panel-title {
            color: #fff !important;
            font-size: 1.05rem;
            font-weight: 600;
            margin: 0 0 0.25rem;
            text-align: center;
        }
        .login-panel-sub {
            color: rgba(156, 163, 175, 0.95) !important;
            font-size: 0.82rem;
            text-align: center;
            margin: 0 0 1rem;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
            max-width: 100% !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stTextInput"] label p,
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            color: rgba(209, 213, 219, 0.9) !important;
            margin-bottom: 0.25rem !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stTextInput"] > div > div {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 12px !important;
            min-height: 46px !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stTextInput"] input {
            background: transparent !important;
            color: #f9fafb !important;
            font-size: 0.9rem !important;
            padding: 0.65rem 0.85rem !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stTextInput"] input::placeholder {
            color: #6b7280 !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] [data-testid="stTextInput"]:focus-within > div > div {
            border-color: rgba(212, 175, 55, 0.55) !important;
            box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.12) !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stCheckbox label p {
            font-size: 0.75rem !important;
            color: rgba(156, 163, 175, 0.95) !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stFormSubmitButton > button,
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stButton > button[kind="primary"] {
            width: 100% !important;
            min-height: 48px !important;
            border: none !important;
            border-radius: 12px !important;
            background: linear-gradient(90deg, #9a7b1a 0%, #d4af37 42%, #f0d78c 100%) !important;
            color: #1a1208 !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 8px 24px rgba(212, 175, 55, 0.28) !important;
            margin-top: 0.35rem !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stFormSubmitButton > button:hover,
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stButton > button[kind="primary"]:hover {
            filter: brightness(1.06) !important;
            box-shadow: 0 10px 28px rgba(212, 175, 55, 0.38) !important;
        }
        .login-forgot-row {
            display: flex;
            justify-content: flex-end;
            margin: -0.35rem 0 0.15rem;
        }
        .login-forgot-row .stButton > button {
            background: transparent !important;
            border: none !important;
            color: #60a5fa !important;
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            padding: 0.2rem 0 !important;
            min-height: auto !important;
            box-shadow: none !important;
            width: auto !important;
        }
        .login-forgot-row .stButton > button:hover {
            color: #93c5fd !important;
            text-decoration: underline !important;
        }
        .login-divider {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 1.15rem 0 0.85rem;
            color: rgba(156, 163, 175, 0.85);
            font-size: 0.78rem;
        }
        .login-divider::before,
        .login-divider::after {
            content: "";
            flex: 1;
            height: 1px;
            background: rgba(255, 255, 255, 0.1);
        }
        .login-social-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .login-social-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            padding: 0.55rem 0.35rem;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #e5e7eb;
            font-size: 0.72rem;
            font-weight: 500;
            cursor: default;
            user-select: none;
        }
        .login-social-icon {
            width: 1.1rem;
            height: 1.1rem;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.62rem;
            font-weight: 700;
        }
        .login-social-g {
            background: #fff;
            color: #4285f4;
        }
        .login-social-f {
            background: #1877f2;
            color: #fff;
        }
        .login-social-a {
            background: #fff;
            color: #000;
        }
        .login-social-hint {
            text-align: center;
            font-size: 0.68rem;
            color: rgba(107, 114, 128, 0.95);
            margin: 0 0 0.75rem;
            line-height: 1.35;
        }
        .login-register-cta {
            text-align: center;
            font-size: 0.8rem;
            color: rgba(156, 163, 175, 0.95);
            margin: 0 0 1rem;
        }
        .login-register-cta a {
            color: #d4af37;
            text-decoration: none;
            font-weight: 600;
        }
        .login-register-cta a:hover { text-decoration: underline; }
        .login-v2-quote {
            text-align: center;
            margin: 0.5rem 0 0.35rem;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        .login-v2-quote-mark {
            color: #d4af37;
            font-size: 1.5rem;
            line-height: 1;
            font-family: Georgia, serif;
        }
        .login-v2-quote-text {
            margin: 0.35rem 0 0.25rem;
            font-size: 0.78rem;
            line-height: 1.5;
            color: rgba(229, 231, 235, 0.88) !important;
            font-style: italic;
        }
        .login-v2-quote-ref {
            margin: 0;
            font-size: 0.8rem;
            font-weight: 600;
            color: #d4af37 !important;
        }
        .login-v2-copy {
            text-align: center;
            font-size: 0.65rem;
            color: rgba(107, 114, 128, 0.9);
            margin: 0.85rem 0 0;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stTabs [data-baseweb="tab-list"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border-radius: 10px !important;
            padding: 0.2rem !important;
            gap: 0.25rem !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            color: rgba(156, 163, 175, 0.95) !important;
            font-size: 0.82rem !important;
        }
        [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stTabs [aria-selected="true"] {
            background: rgba(212, 175, 55, 0.18) !important;
            color: #f5f5f5 !important;
        }
        .login-back-row .stButton > button {
            background: rgba(255, 255, 255, 0.06) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #e5e7eb !important;
            border-radius: 10px !important;
        }
        /* Celular: botões sociais em 3 colunas compactas ou empilhados em telas muito estreitas */
        @media (max-width: 768px) {
            .login-v2-title { font-size: 1.5rem; }
            .login-v2-script { font-size: 1.2rem; }
            .login-social-row {
                grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
                gap: 0.4rem !important;
            }
            .login-social-btn {
                font-size: 0.62rem !important;
                padding: 0.5rem 0.2rem !important;
            }
            [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stFormSubmitButton > button,
            [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .stButton > button[kind="primary"] {
                min-height: 44px !important;
            }
            [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] input,
            [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] textarea,
            [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] select {
                font-size: 16px !important;
            }
        }
        @media (max-width: 380px) {
            .login-social-row { grid-template-columns: 1fr !important; }
            .login-v2-title { font-size: 1.35rem; }
        }
        @supports (padding: max(0px)) {
            [data-testid="stAppViewContainer"]:has(.login-page) .main .block-container,
            [data-testid="stAppViewContainer"]:has(.login-page) [data-testid="stMain"] .block-container {
                padding-left: max(1rem, env(safe-area-inset-left, 0px)) !important;
                padding-right: max(1rem, env(safe-area-inset-right, 0px)) !important;
            }
        }
    """


def inject_login_v2_theme() -> None:
    import streamlit as st

    st.markdown(f"<style>{ibbj_login_v2_css()}</style>", unsafe_allow_html=True)


def inject_ibbj_theme() -> None:
    import streamlit as st

    from app_theme_v3 import ibbj_v3_css
    from sidebar_icons import sidebar_nav_icons_css, sidebar_tool_icons_css

    st.markdown(
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        unsafe_allow_html=True,
    )
    extra = sidebar_nav_icons_css() + sidebar_tool_icons_css() + ibbj_v3_css()
    st.markdown(f"<style>{ibbj_theme_css()}{extra}</style>", unsafe_allow_html=True)


def inject_worship_theme() -> None:
    inject_ibbj_theme()
