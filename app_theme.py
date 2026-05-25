"""Tema visual Worship Collective — layout claro + sidebar navy + detalhes dourados."""

from __future__ import annotations


def worship_theme_overrides() -> str:
    """CSS de redesign (sobrescreve o tema escuro legado com !important)."""
    return """
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        :root {
            --wc-navy: #101d33;
            --wc-navy-soft: #162544;
            --wc-navy-muted: #1e3358;
            --wc-gold: #d4a056;
            --wc-gold-deep: #b07d3e;
            --wc-gold-light: #f0d9a8;
            --wc-bg: #f4f6f9;
            --wc-bg-soft: #eef1f6;
            --wc-card: #ffffff;
            --wc-text: #1a2332;
            --wc-text-muted: #5c6b7f;
            --wc-border: rgba(16, 29, 51, 0.1);
            --wc-shadow: 0 8px 32px rgba(16, 29, 51, 0.08);
            --wc-radius: 16px;
            --bg-deep: var(--wc-bg);
            --bg-surface: var(--wc-card);
            --bg-elevated: var(--wc-card);
            --text-primary: var(--wc-text);
            --text-secondary: var(--wc-text-muted);
            --accent-gold: var(--wc-gold);
            --accent-violet: var(--wc-gold-deep);
            --border-subtle: var(--wc-border);
            --border-accent: rgba(212, 160, 86, 0.45);
            --radius-lg: var(--wc-radius);
            --radius-md: 12px;
            --shadow-card: var(--wc-shadow);
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
        }

        /* Área principal clara */
        [data-testid="stAppViewContainer"] {
            background: var(--wc-bg) !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            border: none !important;
        }
        .block-container {
            max-width: 1140px !important;
            padding-top: 0.5rem !important;
            padding-bottom: 2.5rem !important;
        }
        .main .block-container p,
        .main .block-container li,
        .main .block-container span,
        .main [data-testid="stMarkdownContainer"] p,
        .main [data-testid="stMarkdownContainer"] li {
            color: var(--wc-text) !important;
        }
        .main h1, .main h2, .main h3, .main h4 {
            color: var(--wc-navy) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* Sidebar navy (referência Worship Collective) */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--wc-navy) 0%, #0d1829 100%) !important;
            border-right: none !important;
            box-shadow: 4px 0 24px rgba(16, 29, 51, 0.15) !important;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0.5rem !important;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stCaption {
            color: rgba(255, 255, 255, 0.72) !important;
        }
        .sidebar-brand {
            padding: 0.75rem 0.5rem 1rem !important;
            margin-bottom: 0.5rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        .sidebar-brand-mark {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin-bottom: 0.35rem;
        }
        .sidebar-brand-icon {
            width: 2.35rem;
            height: 2.35rem;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--wc-gold), var(--wc-gold-deep));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            box-shadow: 0 4px 14px rgba(212, 160, 86, 0.45);
        }
        .sidebar-brand h3 {
            color: #fff !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
            line-height: 1.25 !important;
        }
        .sidebar-brand p {
            color: rgba(255, 255, 255, 0.55) !important;
            font-size: 0.72rem !important;
            margin: 0 !important;
        }
        .nav-group-label {
            color: rgba(255, 255, 255, 0.45) !important;
            font-size: 0.65rem !important;
            letter-spacing: 0.14em !important;
            margin: 1.1rem 0 0.4rem 0.35rem !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
            color: rgba(255, 255, 255, 0.78) !important;
            border: 1px solid transparent !important;
            margin-bottom: 0.12rem !important;
            padding: 0.62rem 0.85rem 0.62rem 1.85rem !important;
            border-radius: 12px !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label:hover {
            background: rgba(255, 255, 255, 0.06) !important;
            color: #fff !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-checked="true"],
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(212, 160, 86, 0.35) 0%, rgba(212, 160, 86, 0.08) 100%) !important;
            border-color: rgba(212, 160, 86, 0.35) !important;
            color: #fff !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label > div:first-child {
            background: rgba(255, 255, 255, 0.18) !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-nav-alert="1"] > div:first-child {
            background: #ff3b30 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label .nav-wa-badge {
            border-color: var(--wc-navy) !important;
        }
        section[data-testid="stSidebar"] button {
            border-radius: 12px !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
        }

        /* Boas-vindas no Dashboard */
        .welcome-card {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            border-radius: var(--wc-radius) !important;
            box-shadow: var(--wc-shadow) !important;
            padding: 1.35rem 1.5rem !important;
            margin-bottom: 1.15rem !important;
            border-left: 5px solid var(--wc-gold) !important;
        }
        .welcome-card h3 {
            color: var(--wc-navy) !important;
            font-size: 1.35rem !important;
            margin: 0 0 0.35rem !important;
        }
        .welcome-card p {
            color: var(--wc-text-muted) !important;
            margin: 0 !important;
        }

        /* Cabeçalho de página — card branco */
        .music-hero {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            border-radius: var(--wc-radius) !important;
            box-shadow: var(--wc-shadow) !important;
            padding: 1.35rem 1.5rem !important;
        }
        .music-hero::before {
            background: linear-gradient(135deg, rgba(212, 160, 86, 0.12) 0%, transparent 55%) !important;
            opacity: 1 !important;
        }
        .music-hero::after {
            background: linear-gradient(180deg, var(--wc-gold), var(--wc-gold-deep)) !important;
            width: 5px !important;
        }
        .music-hero h2 {
            color: var(--wc-navy) !important;
            font-size: 1.5rem !important;
        }
        .music-hero p {
            color: var(--wc-text-muted) !important;
        }

        /* Dashboard */
        .dash-section {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: var(--wc-shadow) !important;
            border-radius: var(--wc-radius) !important;
        }
        .dash-section-header {
            background: var(--wc-bg-soft) !important;
            border-bottom: 1px solid var(--wc-border) !important;
            border-left: 4px solid var(--dash-accent, var(--wc-gold)) !important;
        }
        .dash-section-header h4 {
            color: var(--wc-navy) !important;
        }
        .dash-section-sub {
            color: var(--wc-text-muted) !important;
        }
        .quick-nav-btn .stButton > button {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            color: var(--wc-navy) !important;
            box-shadow: 0 2px 8px rgba(16, 29, 51, 0.06) !important;
            border-radius: 14px !important;
        }
        .quick-nav-btn .stButton > button:hover {
            border-color: var(--wc-gold) !important;
            background: #fffdf8 !important;
        }

        /* Painéis e métricas */
        .music-panel {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: var(--wc-shadow) !important;
        }
        .music-panel-title {
            color: var(--wc-gold-deep) !important;
        }
        .music-stat {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: 0 4px 16px rgba(16, 29, 51, 0.06) !important;
        }
        .music-stat:hover {
            box-shadow: 0 8px 24px rgba(212, 160, 86, 0.18) !important;
            border-color: rgba(212, 160, 86, 0.35) !important;
        }
        .music-stat-value { color: var(--wc-navy) !important; }
        .music-stat-label { color: var(--wc-text-muted) !important; }
        .music-pagination {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
        }
        .music-pagination span { color: var(--wc-text-muted) !important; }
        .music-pagination strong { color: var(--wc-gold-deep) !important; }

        div[data-testid="stMetric"] {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: 0 2px 12px rgba(16, 29, 51, 0.05) !important;
        }
        div[data-testid="stMetric"] label { color: var(--wc-text-muted) !important; }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--wc-navy) !important;
        }
        div[data-testid="stForm"] {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: var(--wc-shadow) !important;
        }
        div[data-testid="stTabs"] {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            border-radius: var(--wc-radius) !important;
            box-shadow: var(--wc-shadow) !important;
        }
        div[data-testid="stTabs"] button[data-baseweb="tab"] {
            color: var(--wc-text-muted) !important;
        }
        div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--wc-gold-deep) !important;
            border-bottom-color: var(--wc-gold) !important;
        }

        /* Botões primários — dourado */
        .main .stButton > button[kind="primary"],
        .main .stFormSubmitButton > button {
            background: linear-gradient(135deg, var(--wc-gold) 0%, var(--wc-gold-deep) 100%) !important;
            color: #fff !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(176, 125, 62, 0.35) !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
        }
        .main .stButton > button[kind="primary"]:hover,
        .main .stFormSubmitButton > button:hover {
            filter: brightness(1.05) !important;
            box-shadow: 0 6px 18px rgba(176, 125, 62, 0.45) !important;
        }
        .main .stButton > button[kind="secondary"] {
            background: var(--wc-card) !important;
            color: var(--wc-navy) !important;
            border: 1px solid var(--wc-border) !important;
        }

        /* Login — layout tipo Worship Collective */
        .login-wrap {
            max-width: 1080px !important;
            margin: 0 auto !important;
            padding: 1.5rem 1rem 2.5rem !important;
        }
        .login-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            align-items: stretch;
        }
        @media (max-width: 900px) {
            .login-layout { grid-template-columns: 1fr; }
        }
        .login-hero {
            background: linear-gradient(165deg, var(--wc-navy) 0%, var(--wc-navy-soft) 50%, #0d1829 100%) !important;
            border: none !important;
            border-radius: 20px !important;
            min-height: 480px !important;
            box-shadow: var(--wc-shadow) !important;
            text-align: left !important;
            padding: 2.5rem 2rem !important;
            align-items: flex-start !important;
            justify-content: flex-end !important;
        }
        .login-hero::before {
            content: "" !important;
            position: absolute;
            inset: 0;
            background: url('https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800') center/cover !important;
            opacity: 0.22 !important;
            letter-spacing: 0 !important;
            font-size: 0 !important;
            top: 0 !important;
        }
        .login-hero-quote {
            position: relative;
            z-index: 2;
            font-family: 'Playfair Display', Georgia, serif !important;
            color: #fff !important;
            font-size: 1.45rem !important;
            line-height: 1.45 !important;
            margin: 0 0 0.75rem !important;
            font-weight: 600 !important;
        }
        .login-hero-ref {
            position: relative;
            z-index: 2;
            color: var(--wc-gold-light) !important;
            font-size: 0.88rem !important;
            margin: 0 0 1.25rem !important;
        }
        .login-hero-pill {
            position: relative;
            z-index: 2;
            display: inline-block;
            padding: 0.4rem 0.85rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            color: #fff !important;
            font-size: 0.78rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .login-hero h1 {
            position: relative;
            z-index: 2;
            color: #fff !important;
            font-size: 1.35rem !important;
            margin-top: 1.5rem !important;
        }
        .login-hero .tagline,
        .login-hero .features {
            position: relative;
            z-index: 2;
            color: rgba(255, 255, 255, 0.75) !important;
        }
        .login-form-card {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            border-radius: 20px !important;
            padding: 2rem 1.75rem !important;
            box-shadow: var(--wc-shadow) !important;
        }
        .login-panel-title {
            color: var(--wc-navy) !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
        }
        .login-panel-sub {
            color: var(--wc-text-muted) !important;
        }

        /* Cards auxiliares na área principal */
        .profile-card,
        .planner-panel-card,
        .sugestao-track-card,
        .culto-week-card,
        .feed-post-card {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: 0 4px 20px rgba(16, 29, 51, 0.06) !important;
        }
        .planner-title, .sugestao-track-title { color: var(--wc-navy) !important; }
        .planner-sub, .sugestao-track-meta { color: var(--wc-text-muted) !important; }

        /* Chat / feed legíveis no fundo claro */
        #chat-scroll-box {
            background: var(--wc-bg-soft) !important;
            border: 1px solid var(--wc-border) !important;
        }
        .chat-row-name { color: var(--wc-navy) !important; }
        .chat-row-time, .chat-meta { color: var(--wc-text-muted) !important; }
        .chat-bubble.other {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            color: var(--wc-text) !important;
        }
        .chat-bubble.other .chat-text { color: var(--wc-text) !important; }
        .chat-bubble.me {
            background: linear-gradient(135deg, var(--wc-navy-soft), var(--wc-navy)) !important;
            border-color: var(--wc-navy) !important;
        }
        .feed-post-card { color: var(--wc-text) !important; }

        /* Inputs */
        .main input, .main textarea, .main select {
            background: var(--wc-card) !important;
            color: var(--wc-text) !important;
            border-color: var(--wc-border) !important;
            border-radius: 10px !important;
        }
        .main label { color: var(--wc-text) !important; }

        /* Alertas Streamlit */
        .main .stSuccess { background: #ecfdf5 !important; color: #065f46 !important; }
        .main .stInfo { background: #eff6ff !important; color: #1e40af !important; }
        .main .stWarning { background: #fffbeb !important; color: #92400e !important; }
        .main .stError { background: #fef2f2 !important; color: #991b1b !important; }

        #app-bell-notif {
            background: var(--wc-card) !important;
            border: 1px solid var(--wc-border) !important;
            box-shadow: var(--wc-shadow) !important;
        }

        /* Sequência do culto / cifras — legível no tema claro */
        .seq-cifra-panel,
        .seq-cifra-view,
        .seq-lyric-block,
        .seq-inline-lyric,
        .seq-cifra-direcoes {
            background: var(--wc-card) !important;
            border-color: var(--wc-border) !important;
        }
        .seq-lyric-lines,
        .seq-inline-lines,
        .seq-cifra-dir-text,
        .seq-cifra-pre {
            color: var(--wc-text) !important;
        }
        .seq-cifra-meta,
        .seq-empty,
        .seq-cifra-direcoes-title {
            color: var(--wc-text-muted) !important;
        }
        .cifra-chord-line,
        .cifra-chord-line .cifra-chord,
        .cifra-strophe-inline .cifra-lyric-line .cifra-chord {
            color: var(--wc-gold-deep) !important;
        }
    """


def inject_worship_theme() -> None:
    import streamlit as st

    st.markdown(
        f"<style>{worship_theme_overrides()}</style>",
        unsafe_allow_html=True,
    )
