"""Tema visual IBBJ — sidebar preta, área clara, destaque vermelho, alto contraste."""

from __future__ import annotations


def ibbj_theme_css() -> str:
    return """
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        :root {
            --ibbj-black: #0a0a0a;
            --ibbj-black-soft: #141414;
            --ibbj-black-muted: #1f1f1f;
            --ibbj-red: #c41e3a;
            --ibbj-red-dark: #9a1830;
            --ibbj-red-light: #fce8ec;
            --ibbj-bg: #f3f4f6;
            --ibbj-bg-soft: #e8eaed;
            --ibbj-card: #ffffff;
            --ibbj-text: #111827;
            --ibbj-text-muted: #4b5563;
            --ibbj-text-label: #374151;
            --ibbj-input-bg: #ffffff;
            --ibbj-input-border: #9ca3af;
            --ibbj-border: rgba(0, 0, 0, 0.09);
            --ibbj-shadow: 0 4px 24px rgba(0, 0, 0, 0.07);
            --ibbj-radius: 14px;
            --bg-deep: var(--ibbj-bg);
            --bg-surface: var(--ibbj-card);
            --bg-elevated: var(--ibbj-card);
            --text-primary: var(--ibbj-text);
            --text-secondary: var(--ibbj-text-muted);
            --accent-gold: var(--ibbj-red);
            --accent-violet: var(--ibbj-red-dark);
            --border-subtle: var(--ibbj-border);
            --border-accent: rgba(196, 30, 58, 0.35);
            --radius-lg: var(--ibbj-radius);
            --radius-md: 10px;
            --shadow-card: var(--ibbj-shadow);
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
        }

        [data-testid="stAppViewContainer"] {
            background: var(--ibbj-bg) !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            border: none !important;
        }
        .block-container {
            max-width: 1200px !important;
            padding-top: 0.25rem !important;
            padding-bottom: 2.5rem !important;
        }

        /* ========== Barra superior (mockup) ========== */
        .ibbj-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: var(--ibbj-card);
            border: 1px solid var(--ibbj-border);
            border-radius: var(--ibbj-radius);
            box-shadow: var(--ibbj-shadow);
            padding: 0.85rem 1.25rem;
            margin-bottom: 1rem;
        }
        .ibbj-topbar-brand {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            min-width: 0;
        }
        .ibbj-topbar-cross {
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 8px;
            background: var(--ibbj-red);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1rem;
            flex-shrink: 0;
        }
        .ibbj-topbar-title {
            margin: 0;
            font-size: 1.05rem;
            font-weight: 800;
            color: var(--ibbj-text);
            line-height: 1.2;
        }
        .ibbj-topbar-sub {
            margin: 0.1rem 0 0;
            font-size: 0.72rem;
            color: var(--ibbj-text-muted);
            font-weight: 500;
        }
        .ibbj-topbar-user {
            text-align: right;
            flex-shrink: 0;
        }
        .ibbj-topbar-user strong {
            display: block;
            color: var(--ibbj-text);
            font-size: 0.88rem;
        }
        .ibbj-topbar-user span {
            color: var(--ibbj-text-muted);
            font-size: 0.75rem;
        }

        /* KPI cards */
        .ibbj-kpi-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 0.85rem;
            margin: 0 0 1.15rem;
        }
        .ibbj-kpi-card {
            background: var(--ibbj-card);
            border: 1px solid var(--ibbj-border);
            border-radius: var(--ibbj-radius);
            box-shadow: var(--ibbj-shadow);
            padding: 1rem 1.1rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        .ibbj-kpi-icon {
            font-size: 1.5rem;
            line-height: 1;
        }
        .ibbj-kpi-value {
            display: block;
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--ibbj-text);
            line-height: 1.1;
        }
        .ibbj-kpi-label {
            display: block;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--ibbj-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 0.15rem;
        }

        /* ========== Sidebar preta ========== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--ibbj-black) 0%, var(--ibbj-black-soft) 100%) !important;
            border-right: none !important;
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2) !important;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0.5rem !important;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stCaption {
            color: rgba(255, 255, 255, 0.78) !important;
        }
        .sidebar-brand {
            padding: 0.75rem 0.5rem 1rem !important;
            margin-bottom: 0.5rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .sidebar-brand-mark {
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }
        .sidebar-brand-icon {
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 8px;
            background: var(--ibbj-red);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            font-weight: 800;
            box-shadow: 0 4px 12px rgba(196, 30, 58, 0.45);
        }
        .sidebar-brand h3 {
            color: #fff !important;
            font-size: 0.92rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            line-height: 1.25 !important;
        }
        .sidebar-brand p {
            color: rgba(255, 255, 255, 0.55) !important;
            font-size: 0.7rem !important;
            margin: 0 !important;
        }
        .nav-group-label {
            color: rgba(255, 255, 255, 0.42) !important;
            font-size: 0.65rem !important;
            letter-spacing: 0.12em !important;
            margin: 1rem 0 0.35rem 0.35rem !important;
            font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
            color: rgba(255, 255, 255, 0.82) !important;
            border: 1px solid transparent !important;
            margin-bottom: 0.1rem !important;
            padding: 0.6rem 0.85rem 0.6rem 1.85rem !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label:hover {
            background: rgba(255, 255, 255, 0.06) !important;
            color: #fff !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-checked="true"],
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: var(--ibbj-red) !important;
            border-color: var(--ibbj-red-dark) !important;
            color: #fff !important;
            font-weight: 700 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label > div:first-child {
            background: rgba(255, 255, 255, 0.2) !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-nav-alert="1"] > div:first-child {
            background: #ff3b30 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label .nav-wa-badge {
            border-color: var(--ibbj-black) !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }

        /* ========== Área principal ========== */
        .main .block-container p,
        .main [data-testid="stMarkdownContainer"] p,
        section.main [data-testid="stMarkdownContainer"] p {
            color: var(--ibbj-text) !important;
        }
        .main h1, .main h2, .main h3, .main h4,
        section.main h1, section.main h2, section.main h3 {
            color: var(--ibbj-text) !important;
        }

        .welcome-card {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            border-radius: var(--ibbj-radius) !important;
            box-shadow: var(--ibbj-shadow) !important;
            padding: 1.25rem 1.35rem !important;
            margin-bottom: 1rem !important;
            border-left: 4px solid var(--ibbj-red) !important;
        }
        .welcome-card h3 { color: var(--ibbj-text) !important; margin: 0 0 0.35rem !important; }
        .welcome-card p { color: var(--ibbj-text-muted) !important; margin: 0 !important; }

        .music-hero {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            border-radius: var(--ibbj-radius) !important;
            box-shadow: var(--ibbj-shadow) !important;
            padding: 1.2rem 1.35rem !important;
            margin-bottom: 1rem !important;
            position: relative;
            overflow: hidden;
        }
        .music-hero::after {
            content: "";
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 4px;
            background: var(--accent, var(--ibbj-red));
            border-radius: 4px 0 0 4px;
        }
        .music-hero h2 {
            color: var(--ibbj-text) !important;
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
        }
        .music-hero p {
            color: var(--ibbj-text-muted) !important;
            margin: 0.3rem 0 0 !important;
        }

        .dash-section {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            box-shadow: var(--ibbj-shadow) !important;
            border-radius: var(--ibbj-radius) !important;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        .dash-section-header {
            background: var(--ibbj-bg-soft) !important;
            border-bottom: 1px solid var(--ibbj-border) !important;
            border-left: 4px solid var(--dash-accent, var(--ibbj-red)) !important;
            padding: 0.75rem 1rem !important;
        }
        .dash-section-header h4 {
            color: var(--ibbj-text) !important;
            font-weight: 700 !important;
        }
        .dash-section-sub { color: var(--ibbj-text-muted) !important; }

        .quick-nav-btn .stButton > button {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            color: var(--ibbj-text) !important;
            border-radius: 12px !important;
            min-height: 4rem !important;
        }
        .quick-nav-btn .stButton > button:hover {
            border-color: var(--ibbj-red) !important;
            background: var(--ibbj-red-light) !important;
        }

        .music-panel {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            box-shadow: var(--ibbj-shadow) !important;
            border-radius: var(--ibbj-radius) !important;
            padding: 1rem 1.25rem !important;
        }
        .music-panel-title {
            color: var(--ibbj-red-dark) !important;
            font-weight: 700 !important;
        }

        .music-stat, div[data-testid="stMetric"] {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            box-shadow: var(--ibbj-shadow) !important;
            border-radius: var(--ibbj-radius) !important;
        }
        .music-stat-value, div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: var(--ibbj-text) !important;
        }
        .music-stat-label, div[data-testid="stMetric"] label {
            color: var(--ibbj-text-muted) !important;
        }

        div[data-testid="stForm"],
        div[data-testid="stTabs"] {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            border-radius: var(--ibbj-radius) !important;
            box-shadow: var(--ibbj-shadow) !important;
        }
        section.main div[data-testid="stTabs"] [data-baseweb="tab"],
        [data-testid="stMain"] div[data-testid="stTabs"] [data-baseweb="tab"] {
            color: var(--ibbj-text-label) !important;
            font-weight: 600 !important;
        }
        section.main div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        [data-testid="stMain"] div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            color: var(--ibbj-red-dark) !important;
            border-bottom: 3px solid var(--ibbj-red) !important;
        }

        .profile-card, .planner-panel-card, .sugestao-track-card,
        .culto-week-card, .feed-post-card, .event-feed-card, .prog-card, .swap-card {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            box-shadow: var(--ibbj-shadow) !important;
            border-radius: var(--ibbj-radius) !important;
            color: var(--ibbj-text) !important;
        }
        .culto-week-card h3, .planner-title, .sugestao-track-title, .prog-card .prog-parte {
            color: var(--ibbj-red-dark) !important;
        }
        .culto-week-card .culto-date, .planner-sub, .sugestao-track-meta, .prog-card .prog-meta {
            color: var(--ibbj-text-muted) !important;
        }
        .prog-card .prog-louvor { color: var(--ibbj-text) !important; }
        .team-chip {
            background: var(--ibbj-red-light) !important;
            border: 1px solid rgba(196, 30, 58, 0.25) !important;
            color: var(--ibbj-text) !important;
        }
        .team-chip strong { color: var(--ibbj-red-dark) !important; }

        .verse-of-day {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            border-left: 4px solid var(--ibbj-red) !important;
            border-radius: var(--ibbj-radius) !important;
            padding: 1rem 1.2rem !important;
        }
        .verse-of-day .verse-label { color: var(--ibbj-red-dark) !important; font-weight: 700 !important; }
        .verse-of-day .verse-text { color: var(--ibbj-text) !important; }
        .verse-of-day .verse-ref { color: var(--ibbj-text-muted) !important; font-weight: 600 !important; }

        #chat-scroll-box {
            background: var(--ibbj-bg-soft) !important;
            border: 1px solid var(--ibbj-border) !important;
        }
        .chat-row-name { color: var(--ibbj-text) !important; }
        .chat-row-time, .chat-meta { color: var(--ibbj-text-muted) !important; }
        .chat-bubble.other {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
        }
        .chat-bubble.other .chat-text { color: var(--ibbj-text) !important; }
        .chat-bubble.me {
            background: linear-gradient(135deg, var(--ibbj-red), var(--ibbj-red-dark)) !important;
            border-color: var(--ibbj-red-dark) !important;
        }
        .chat-bubble.me .chat-text { color: #fff !important; }

        .status-escalado {
            background: #ecfdf5 !important;
            border: 1px solid #6ee7b7 !important;
            color: var(--ibbj-text) !important;
        }
        .status-escalado strong, .status-escalado .escala-evento { color: #065f46 !important; }
        .status-escalado .escala-data { color: #047857 !important; }
        .status-escalado .escala-funcao { color: #334155 !important; }
        .status-nao-escalado {
            background: #fffbeb !important;
            border: 1px solid #fbbf24 !important;
            color: #78350f !important;
        }
        .ensaio-aviso-banner {
            background: #fff7ed !important;
            border: 1px solid #fdba74 !important;
            color: #9a3412 !important;
        }

        .members-leader-wrap {
            border: 1px solid var(--ibbj-border) !important;
            background: var(--ibbj-card) !important;
        }
        .members-leader-table { color: var(--ibbj-text) !important; }
        .members-leader-table th {
            background: var(--ibbj-bg-soft) !important;
            color: var(--ibbj-text-label) !important;
        }
        .members-leader-table .mem-nome { color: var(--ibbj-text) !important; }
        .members-leader-table .mem-funcao { color: var(--ibbj-text-muted) !important; }
        .badge-escalado-sim { background: #d1fae5 !important; color: #065f46 !important; border-color: #6ee7b7 !important; }
        .badge-escalado-nao { background: #f3f4f6 !important; color: #4b5563 !important; }

        .sugestao-status--pendente { background: #fef3c7 !important; color: #92400e !important; border: 1px solid #fcd34d !important; }
        .sugestao-status--em_analise { background: #dbeafe !important; color: #1e40af !important; border: 1px solid #93c5fd !important; }
        .sugestao-status--aprovada { background: #d1fae5 !important; color: #065f46 !important; border: 1px solid #6ee7b7 !important; }
        .sugestao-status--recusada { background: #fee2e2 !important; color: #991b1b !important; border: 1px solid #fca5a5 !important; }

        .badge-sem-escala {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            background: var(--ibbj-red);
            color: #fff;
        }

        .music-pagination {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            color: var(--ibbj-text-muted) !important;
        }
        .music-pagination strong { color: var(--ibbj-red-dark) !important; }

        .profile-avatar-placeholder {
            background: var(--ibbj-bg-soft) !important;
            border: 2px dashed var(--ibbj-input-border) !important;
            color: var(--ibbj-text-muted) !important;
        }

        .seq-cifra-panel, .seq-cifra-view, .seq-lyric-block {
            background: var(--ibbj-card) !important;
            border-color: var(--ibbj-border) !important;
        }
        .seq-lyric-lines, .seq-cifra-pre { color: var(--ibbj-text) !important; }
        .seq-cifra-meta, .seq-empty { color: var(--ibbj-text-muted) !important; }
        .cifra-chord-line, .cifra-chord { color: var(--ibbj-red-dark) !important; }

        #app-bell-notif {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            box-shadow: var(--ibbj-shadow) !important;
        }

        /* Login */
        .login-wrap { max-width: 1080px !important; margin: 0 auto !important; }
        .login-hero {
            background: linear-gradient(165deg, var(--ibbj-black) 0%, var(--ibbj-black-soft) 100%) !important;
            border: none !important;
            border-radius: 20px !important;
            min-height: 420px !important;
            padding: 2rem 1.75rem !important;
        }
        .login-hero h1, .login-hero-quote { color: #fff !important; }
        .login-hero .tagline, .login-hero .features { color: rgba(255,255,255,0.75) !important; }
        .login-hero-ref, .login-hero-pill { color: var(--ibbj-red-light) !important; }
        .login-form-card {
            background: var(--ibbj-card) !important;
            border: 1px solid var(--ibbj-border) !important;
            border-radius: 20px !important;
            box-shadow: var(--ibbj-shadow) !important;
        }
        .login-panel-title { color: var(--ibbj-text) !important; }
        .login-panel-sub { color: var(--ibbj-text-muted) !important; }

        /* Formulários — contraste */
        section.main label,
        section.main [data-testid="stWidgetLabel"] p,
        [data-testid="stMain"] label,
        .login-form-card label {
            color: var(--ibbj-text-label) !important;
            font-weight: 600 !important;
        }
        section.main .stCaption, [data-testid="stMain"] .stCaption {
            color: var(--ibbj-text-muted) !important;
        }
        section.main input, section.main textarea,
        [data-testid="stMain"] input, [data-testid="stMain"] textarea,
        .login-form-card input {
            background: var(--ibbj-input-bg) !important;
            color: var(--ibbj-text) !important;
            -webkit-text-fill-color: var(--ibbj-text) !important;
            border: 1px solid var(--ibbj-input-border) !important;
        }
        section.main [data-baseweb="input"] input,
        [data-testid="stMain"] [data-baseweb="input"] input {
            color: var(--ibbj-text) !important;
        }
        section.main [data-baseweb="select"] > div,
        [data-testid="stMain"] [data-baseweb="select"] > div {
            background: var(--ibbj-input-bg) !important;
            color: var(--ibbj-text) !important;
        }
        section.main [data-baseweb="tag"],
        [data-testid="stMain"] [data-baseweb="tag"] {
            background: #e5e7eb !important;
            color: var(--ibbj-text) !important;
        }

        section.main .stButton > button[kind="primary"],
        section.main .stFormSubmitButton > button,
        section.main button[kind="primaryFormSubmit"],
        [data-testid="stMain"] .stButton > button[kind="primary"],
        [data-testid="stMain"] .stFormSubmitButton > button,
        .login-form-card .stButton > button[kind="primary"],
        .login-form-card .stFormSubmitButton > button {
            background: linear-gradient(135deg, var(--ibbj-red) 0%, var(--ibbj-red-dark) 100%) !important;
            color: #ffffff !important;
            border: 1px solid var(--ibbj-red-dark) !important;
            font-weight: 700 !important;
        }
        section.main .stButton > button[kind="secondary"],
        [data-testid="stMain"] .stButton > button[kind="secondary"] {
            background: #f9fafb !important;
            color: var(--ibbj-text) !important;
            border: 1px solid var(--ibbj-input-border) !important;
        }

        section.main .streamlit-expanderHeader,
        [data-testid="stMain"] .streamlit-expanderHeader {
            color: var(--ibbj-text) !important;
            font-weight: 600 !important;
        }
        section.main a, [data-testid="stMain"] a {
            color: var(--ibbj-red-dark) !important;
        }

        .main .stSuccess { background: #ecfdf5 !important; color: #065f46 !important; }
        .main .stInfo { background: #eff6ff !important; color: #1e40af !important; }
        .main .stWarning { background: #fffbeb !important; color: #92400e !important; }
        .main .stError { background: #fef2f2 !important; color: #991b1b !important; }

        .ibbj-footer {
            text-align: center;
            color: var(--ibbj-text-muted);
            font-size: 0.75rem;
            margin-top: 2rem;
            padding: 1rem 0;
        }

        @media (max-width: 768px) {
            .ibbj-topbar { flex-wrap: wrap; padding: 0.75rem 1rem; }
            .ibbj-kpi-row { grid-template-columns: 1fr 1fr; }
            .block-container { padding-left: 0.65rem !important; padding-right: 0.65rem !important; }
            input, textarea, select { font-size: 16px !important; }
        }
    """


def inject_ibbj_theme() -> None:
    import streamlit as st

    st.markdown(f"<style>{ibbj_theme_css()}</style>", unsafe_allow_html=True)


def inject_worship_theme() -> None:
    """Alias legado — tema atual é IBBJ."""
    inject_ibbj_theme()
