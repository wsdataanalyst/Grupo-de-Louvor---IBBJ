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
        .block-container {
            max-width: 1280px !important;
            padding-top: 0.5rem !important;
            padding-bottom: 2.5rem !important;
        }

        /* ========== Sidebar ========== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0f0f 0%, var(--ig-bg-elevated) 100%) !important;
            border-right: 1px solid var(--ig-border) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.35) !important;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0.35rem !important;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
        section[data-testid="stSidebar"] label {
            color: rgba(255, 255, 255, 0.82) !important;
        }
        section[data-testid="stSidebar"] .stCaption {
            color: var(--ig-text-dim) !important;
            font-size: 0.72rem !important;
        }

        .sidebar-brand {
            padding: 1rem 0.65rem 1.1rem !important;
            margin-bottom: 0.25rem !important;
            border-bottom: 1px solid var(--ig-border) !important;
        }
        .sidebar-brand-mark {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .sidebar-brand-icon {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 50%;
            background: linear-gradient(145deg, #e8c547, var(--ig-gold));
            color: #1a1208;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            font-weight: 800;
            box-shadow: 0 4px 16px rgba(212, 175, 55, 0.35);
            flex-shrink: 0;
        }
        .sidebar-brand h3 {
            color: #fff !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            line-height: 1.15 !important;
            letter-spacing: 0.02em !important;
        }
        .sidebar-brand .brand-line2 {
            color: var(--ig-text-muted) !important;
            font-size: 0.68rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.14em !important;
            text-transform: uppercase !important;
            margin: 0.15rem 0 0 !important;
        }
        .sidebar-user-mini {
            padding: 0.5rem 0.65rem 0.75rem !important;
            border-bottom: 1px solid var(--ig-border) !important;
            margin-bottom: 0.35rem !important;
        }
        .sidebar-user-mini strong {
            color: var(--ig-text) !important;
            font-size: 0.85rem !important;
        }
        .sidebar-user-mini span {
            color: var(--ig-text-muted) !important;
            font-size: 0.72rem !important;
        }

        .nav-group-label {
            color: var(--ig-gold) !important;
            font-size: 0.62rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.16em !important;
            text-transform: uppercase !important;
            margin: 0.85rem 0 0.35rem 0.5rem !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
            color: rgba(255, 255, 255, 0.78) !important;
            border: 1px solid transparent !important;
            margin-bottom: 0.08rem !important;
            padding: 0.58rem 0.8rem 0.58rem 1.75rem !important;
            border-radius: var(--ig-radius) !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label:hover {
            background: rgba(255, 255, 255, 0.04) !important;
            color: #fff !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-checked="true"],
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: var(--ig-gold-soft) !important;
            border: 1px solid var(--ig-gold-border) !important;
            color: var(--ig-gold) !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label > div:first-child {
            background: rgba(255, 255, 255, 0.15) !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-nav-alert="1"] > div:first-child {
            background: #ff453a !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label .nav-wa-badge {
            border-color: var(--ig-bg-elevated) !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: var(--ig-bg-card) !important;
            color: var(--ig-text) !important;
            border: 1px solid var(--ig-border-strong) !important;
        }
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: var(--ig-radius) !important;
            color: var(--ig-text) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            background: var(--ig-bg-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: var(--ig-radius) !important;
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
            .block-container { padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
            input, textarea, select { font-size: 16px !important; }
        }
    """


def inject_ibbj_theme() -> None:
    import streamlit as st

    st.markdown(f"<style>{ibbj_theme_css()}</style>", unsafe_allow_html=True)


def inject_worship_theme() -> None:
    inject_ibbj_theme()
