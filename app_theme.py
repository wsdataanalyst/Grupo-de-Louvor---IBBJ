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
            --wc-text-muted: #475569;
            --wc-text-label: #334155;
            --wc-input-bg: #ffffff;
            --wc-input-border: #94a3b8;
            --wc-btn-primary-top: #a86f25;
            --wc-btn-primary-bot: #7a5520;
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
        /* Abas — ver bloco de acessibilidade */

        /* Botões primários — ver bloco de acessibilidade no final */

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

        /* Inputs — ver bloco de acessibilidade */

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

        /* ========== Acessibilidade: contraste na área principal ========== */
        section.main,
        [data-testid="stMain"],
        .login-wrap,
        .login-form-card {
            color: var(--wc-text) !important;
        }

        /* Neutraliza texto claro do tema escuro legado */
        section.main [data-testid="stMarkdownContainer"] p,
        section.main [data-testid="stMarkdownContainer"] li,
        section.main [data-testid="stMarkdownContainer"] span,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
        .login-form-card [data-testid="stMarkdownContainer"] p,
        .login-form-card [data-testid="stMarkdownContainer"] li {
            color: var(--wc-text) !important;
        }
        section.main h1, section.main h2, section.main h3, section.main h4,
        [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 {
            color: var(--wc-navy) !important;
        }

        /* Labels de formulário (Email, Senha, etc.) */
        section.main label,
        section.main [data-testid="stWidgetLabel"] p,
        section.main [data-testid="stWidgetLabel"] label,
        section.main .stTextInput label,
        section.main .stTextArea label,
        section.main .stSelectbox label,
        section.main .stMultiSelect label,
        section.main .stNumberInput label,
        section.main .stDateInput label,
        section.main .stTimeInput label,
        [data-testid="stMain"] label,
        [data-testid="stMain"] [data-testid="stWidgetLabel"] p,
        .login-form-card label,
        .login-form-card [data-testid="stWidgetLabel"] p {
            color: var(--wc-text-label) !important;
            font-weight: 600 !important;
        }

        /* Checkbox e ajuda */
        section.main .stCheckbox label p,
        section.main .stCheckbox span,
        section.main .stCheckbox [data-testid="stMarkdownContainer"] p,
        [data-testid="stMain"] .stCheckbox label p,
        .login-form-card .stCheckbox label p {
            color: var(--wc-text-label) !important;
            font-weight: 500 !important;
        }
        section.main .stCaption,
        section.main small,
        [data-testid="stMain"] .stCaption {
            color: var(--wc-text-muted) !important;
        }

        /* Abas (Entrar / Cadastrar, etc.) */
        section.main div[data-testid="stTabs"] [data-baseweb="tab"],
        [data-testid="stMain"] div[data-testid="stTabs"] [data-baseweb="tab"],
        .login-form-card div[data-testid="stTabs"] [data-baseweb="tab"] {
            color: var(--wc-text-label) !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }
        section.main div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        [data-testid="stMain"] div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"],
        .login-form-card div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
            color: var(--wc-navy) !important;
            border-bottom: 3px solid var(--wc-gold-deep) !important;
        }
        section.main div[data-testid="stTabs"] [data-baseweb="tab-list"],
        [data-testid="stMain"] div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            border-bottom: 1px solid var(--wc-input-border) !important;
        }

        /* Campos de texto — fundo claro e texto escuro */
        section.main input,
        section.main textarea,
        section.main select,
        [data-testid="stMain"] input,
        [data-testid="stMain"] textarea,
        .login-form-card input,
        .login-form-card textarea {
            background-color: var(--wc-input-bg) !important;
            color: var(--wc-text) !important;
            -webkit-text-fill-color: var(--wc-text) !important;
            border: 1px solid var(--wc-input-border) !important;
            caret-color: var(--wc-navy) !important;
        }
        section.main [data-baseweb="input"],
        [data-testid="stMain"] [data-baseweb="input"],
        .login-form-card [data-baseweb="input"] {
            background-color: var(--wc-input-bg) !important;
            border: 1px solid var(--wc-input-border) !important;
        }
        section.main [data-baseweb="input"] > div,
        [data-testid="stMain"] [data-baseweb="input"] > div {
            background-color: #f8fafc !important;
            border-color: var(--wc-input-border) !important;
        }
        section.main [data-baseweb="input"] input,
        [data-testid="stMain"] [data-baseweb="input"] input,
        .login-form-card [data-baseweb="input"] input {
            color: var(--wc-text) !important;
            -webkit-text-fill-color: var(--wc-text) !important;
        }

        /* Botões primários — dourado mais escuro (texto branco legível) */
        section.main .stButton > button[kind="primary"],
        section.main .stFormSubmitButton > button,
        section.main button[kind="primaryFormSubmit"],
        [data-testid="stMain"] .stButton > button[kind="primary"],
        [data-testid="stMain"] .stFormSubmitButton > button,
        [data-testid="stMain"] button[kind="primaryFormSubmit"],
        .login-form-card .stButton > button[kind="primary"],
        .login-form-card .stFormSubmitButton > button,
        .login-form-card button[kind="primaryFormSubmit"] {
            background: linear-gradient(
                135deg,
                var(--wc-btn-primary-top) 0%,
                var(--wc-btn-primary-bot) 100%
            ) !important;
            color: #ffffff !important;
            border: 1px solid #6b4718 !important;
            font-weight: 700 !important;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.25) !important;
        }

        /* Botões secundários */
        section.main .stButton > button[kind="secondary"],
        [data-testid="stMain"] .stButton > button[kind="secondary"],
        .login-form-card .stButton > button[kind="secondary"] {
            background: #f1f5f9 !important;
            color: var(--wc-navy) !important;
            border: 1px solid var(--wc-input-border) !important;
            font-weight: 600 !important;
        }

        /* Select / multiselect na área principal */
        section.main [data-baseweb="select"] > div,
        [data-testid="stMain"] [data-baseweb="select"] > div {
            background-color: var(--wc-input-bg) !important;
            color: var(--wc-text) !important;
            border-color: var(--wc-input-border) !important;
        }
        section.main [data-baseweb="tag"],
        [data-testid="stMain"] [data-baseweb="tag"] {
            background: #e2e8f0 !important;
            color: var(--wc-navy) !important;
        }

        /* Radio/checkbox na área principal (não sidebar) */
        section.main div[data-testid="stRadio"] > label,
        [data-testid="stMain"] div[data-testid="stRadio"] > label {
            color: var(--wc-text) !important;
        }

        /* Expanders, links */
        section.main .streamlit-expanderHeader,
        [data-testid="stMain"] .streamlit-expanderHeader {
            color: var(--wc-navy) !important;
            font-weight: 600 !important;
        }
        section.main a,
        [data-testid="stMain"] a {
            color: #1d4ed8 !important;
        }

        /* Status escalado / avisos no dashboard */
        .status-escalado {
            background: #ecfdf5 !important;
            border: 1px solid #6ee7b7 !important;
            color: var(--wc-text) !important;
        }
        .status-escalado p,
        .status-escalado strong {
            color: #065f46 !important;
        }
        .status-escalado .escala-evento {
            color: var(--wc-navy) !important;
        }
        .status-escalado .escala-data {
            color: #047857 !important;
        }
        .status-escalado .escala-funcao {
            color: #334155 !important;
        }
        .status-escalado .ensaio-ok {
            color: #1d4ed8 !important;
        }
        .status-escalado .ensaio-pendente {
            color: #b45309 !important;
        }
        .status-nao-escalado {
            color: #92400e !important;
            background: #fffbeb !important;
            border: 1px solid #fbbf24 !important;
        }
        .status-nao-escalado strong {
            color: #78350f !important;
        }
        .ensaio-aviso-banner {
            color: #92400e !important;
            background: #fffbeb !important;
        }

        /* Dataframe */
        section.main [data-testid="stDataFrame"],
        [data-testid="stMain"] [data-testid="stDataFrame"] {
            color: var(--wc-text) !important;
        }

        /* Placeholder inputs */
        section.main input::placeholder,
        [data-testid="stMain"] input::placeholder {
            color: #64748b !important;
            opacity: 1 !important;
        }
    """


def inject_worship_theme() -> None:
    import streamlit as st

    st.markdown(
        f"<style>{worship_theme_overrides()}</style>",
        unsafe_allow_html=True,
    )
