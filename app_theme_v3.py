"""CSS do layout premium v3 — Manrope, glassmorphism, dashboard 3 colunas."""


def ibbj_v3_css() -> str:
    return """
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --ig-bg-deep: #030712;
            --ig-card: #0f172a;
            --ig-border: rgba(255, 255, 255, 0.08);
            --ig-blue: #2563eb;
            --ig-gold: #d4a017;
            --ig-text: #f8fafc;
            --ig-muted: #94a3b8;
            --ig-radius-xl: 24px;
            --ig-sidebar-w: 280px;
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', 'Segoe UI', system-ui, sans-serif !important;
        }

        [data-testid="stAppViewContainer"]:not(:has(.login-page)) {
            background: var(--ig-bg-deep) !important;
        }
        [data-testid="stAppViewContainer"]:not(:has(.login-page))::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            background:
                radial-gradient(ellipse 55% 40% at 12% 8%, rgba(37, 99, 235, 0.12), transparent),
                radial-gradient(ellipse 40% 35% at 88% 15%, rgba(212, 160, 23, 0.06), transparent);
        }

        /* Sidebar ~280px */
        section[data-testid="stSidebar"] {
            min-width: var(--ig-sidebar-w) !important;
            max-width: var(--ig-sidebar-w) !important;
            width: var(--ig-sidebar-w) !important;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] .stButton > button[kind="primary"] {
            position: relative !important;
            border-left: 3px solid var(--ig-gold) !important;
            padding-left: 0.75rem !important;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_nav_"] .stButton > button[kind="primary"]::after {
            content: "›";
            position: absolute;
            right: 0.65rem;
            top: 50%;
            transform: translateY(-50%);
            color: #93c5fd;
            font-size: 1.15rem;
            font-weight: 700;
        }
        section[data-testid="stSidebar"] [class*="st-key-ig_sidebar_logout"] .stButton > button {
            color: #fca5a5 !important;
        }
        .ig-sb-divider {
            height: 1px;
            margin: 0.5rem 0.65rem 0.75rem;
            background: var(--ig-border);
        }
        .ig-sb-mark-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(212, 160, 23, 0.22) 0%, transparent 68%);
            box-shadow: 0 0 28px rgba(212, 160, 23, 0.35);
        }

        /* Main layout */
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) .main .block-container,
        [data-testid="stAppViewContainer"]:not(:has(.login-page)) [data-testid="stMain"] .block-container {
            max-width: 100% !important;
            padding-top: 0.25rem !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }
        .ig-ambient {
            position: fixed;
            border-radius: 50%;
            pointer-events: none;
            z-index: 0;
            filter: blur(60px);
        }
        .ig-ambient--blue {
            width: 320px;
            height: 320px;
            top: 8%;
            left: 28%;
            background: rgba(37, 99, 235, 0.18);
        }
        .ig-ambient--gold {
            width: 200px;
            height: 200px;
            top: 22%;
            right: 18%;
            background: rgba(212, 160, 23, 0.1);
        }

        /* Global header */
        .ig-top-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.35rem;
        }
        .ig-hdr-spacer { height: 0.15rem; }
        div[data-testid="stTextInput"]:has(input[aria-label="Busca global"]) input {
            background: var(--ig-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: 999px !important;
            color: var(--ig-text) !important;
            padding: 0.65rem 1rem 0.65rem 2.5rem !important;
            font-size: 0.88rem !important;
        }
        div[data-testid="stTextInput"]:has(input[aria-label="Busca global"]) {
            position: relative;
        }
        div[data-testid="stTextInput"]:has(input[aria-label="Busca global"])::before {
            content: "";
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 1rem;
            height: 1rem;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cpath d='m21 21-4.3-4.3'/%3E%3C/svg%3E") center/contain no-repeat;
            z-index: 2;
            pointer-events: none;
        }
        /* Hero */
        .ig-hero-card {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.25rem;
            border-radius: var(--ig-radius-xl);
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid var(--ig-border);
            backdrop-filter: blur(12px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        }
        .ig-hero-title {
            margin: 0 0 0.35rem;
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--ig-text) !important;
        }
        .ig-hero-sub {
            margin: 0;
            color: var(--ig-muted) !important;
            font-size: 0.92rem;
        }
        .ig-hero-verse {
            margin: 0;
            max-width: 280px;
            padding: 0.65rem 0.85rem;
            border-left: 3px solid var(--ig-gold);
            font-size: 0.78rem;
            font-style: italic;
            color: var(--ig-muted) !important;
            line-height: 1.45;
        }
        .ig-hero-verse em { color: var(--ig-gold) !important; font-style: italic; }
        .ig-hero-verse-label {
            display: block;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--ig-gold) !important;
            margin-bottom: 0.25rem;
            font-style: normal;
        }

        /* Metrics — cards via st.columns + markdown HTML */
        [data-testid="stHorizontalBlock"]:has([class*="st-key-ig_metric"]) {
            gap: 1rem !important;
            margin-bottom: 1.1rem !important;
        }
        [data-testid="stHorizontalBlock"]:has([class*="st-key-ig_metric"]) [data-testid="stColumn"] {
            min-width: 0 !important;
        }
        .ig-metric-card {
            position: relative;
            width: 100%;
            box-sizing: border-box;
            padding: 1.15rem 1.1rem 0.65rem;
            margin-bottom: 0.35rem;
            border-radius: var(--ig-radius-xl);
            background: var(--ig-card);
            border: 1px solid var(--ig-border);
            overflow: hidden;
            min-height: 6.75rem;
        }
        .ig-metric-bg {
            position: absolute;
            right: -10%;
            bottom: -20%;
            width: 55%;
            height: 70%;
            opacity: 0.12;
            background: radial-gradient(circle, var(--ig-blue) 0%, transparent 70%);
        }
        .ig-metric-value {
            display: block;
            font-size: 2rem;
            font-weight: 800;
            color: var(--ig-text) !important;
            line-height: 1.1;
        }
        .ig-metric-label {
            display: block;
            font-size: 0.8rem;
            color: var(--ig-muted) !important;
            margin-top: 0.2rem;
        }
        .ig-metric-ico {
            display: inline-block;
            width: 1.35rem;
            height: 1.35rem;
            margin-bottom: 0.5rem;
            opacity: 0.9;
        }
        .ig-metric-ico--members {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%232563eb' stroke-width='2'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/%3E%3Ccircle cx='9' cy='7' r='4'/%3E%3Cpath d='M22 21v-2a4 4 0 0 0-3-3.87'/%3E%3Cpath d='M16 3.13a4 4 0 0 1 0 7.75'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-metric-ico--louvores {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Cpath d='M9 18V5l12-2v13'/%3E%3Ccircle cx='6' cy='18' r='3'/%3E%3Ccircle cx='18' cy='16' r='3'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-metric-ico--escalas {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2322c55e' stroke-width='2'%3E%3Crect x='3' y='4' width='18' height='18' rx='2'/%3E%3Cpath d='M16 2v4M8 2v4M3 10h18'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        [class*="st-key-ig_metric"] .stButton > button {
            font-size: 0.72rem !important;
            padding: 0.35rem 0.5rem 0.45rem 1rem !important;
            min-height: 2rem !important;
            justify-content: flex-start !important;
            text-align: left !important;
            background: transparent !important;
            border: none !important;
            color: var(--ig-blue) !important;
            font-weight: 600 !important;
            box-shadow: none !important;
        }
        [class*="st-key-ig_metric"] .stButton > button:hover {
            color: #93c5fd !important;
            background: rgba(37, 99, 235, 0.08) !important;
        }
        /* Warning */
        .ig-warn-card {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 1rem 1.15rem;
            margin-bottom: 1.25rem;
            border-radius: var(--ig-radius-xl);
            border: 1px solid rgba(212, 160, 23, 0.55);
            background: rgba(15, 23, 42, 0.65);
        }
        .ig-warn-ico {
            width: 1.5rem;
            height: 1.5rem;
            flex-shrink: 0;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%23d4a017' stroke-width='2'%3E%3Cpath d='M12 9v4'/%3E%3Cpath d='M12 17h.01'/%3E%3Cpath d='M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'/%3E%3C/svg%3E") center/contain no-repeat;
        }
        .ig-warn-text {
            margin: 0;
            flex: 1;
            color: var(--ig-text) !important;
            font-weight: 500;
        }
        [class*="st-key-ig_warn_escalas"] .stButton > button {
            border-radius: 999px !important;
            border: 1px solid var(--ig-gold) !important;
            background: transparent !important;
            color: var(--ig-gold) !important;
            font-weight: 600 !important;
        }

        /* Quick access */
        .ig-section-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--ig-text) !important;
            margin: 0 0 0.75rem;
        }
        .ig-quick-grid-open { margin-bottom: 1.25rem; }
        .ig-quick-card {
            text-align: center;
            padding: 0.35rem 0 0.15rem;
            pointer-events: none;
        }
        .ig-quick-ico { font-size: 1.35rem; display: block; }
        .ig-quick-label {
            display: block;
            font-size: 0.72rem;
            color: var(--ig-muted) !important;
            margin-top: 0.15rem;
        }
        [class*="st-key-v3_qn"] .stButton > button {
            margin-top: -2.6rem !important;
            min-height: 4.5rem !important;
            background: var(--ig-card) !important;
            border: 1px solid var(--ig-border) !important;
            border-radius: 16px !important;
            color: transparent !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
        }
        [class*="st-key-v3_qn"] .stButton > button:hover {
            border-color: rgba(37, 99, 235, 0.45) !important;
            box-shadow: 0 8px 28px rgba(37, 99, 235, 0.2) !important;
        }

        /* Right panel */
        .ig-right-panel { display: flex; flex-direction: column; gap: 1rem; }
        .ig-rpanel-card {
            padding: 1.1rem 1rem;
            border-radius: var(--ig-radius-xl);
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--ig-border);
            backdrop-filter: blur(10px);
        }
        .ig-rpanel-card--hero { padding-bottom: 0.85rem; }
        .ig-rpanel-kicker {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--ig-muted) !important;
            margin: 0 0 0.5rem;
        }
        .ig-rpanel-banner {
            height: 88px;
            border-radius: 14px;
            margin-bottom: 0.75rem;
            background:
                linear-gradient(180deg, rgba(3, 7, 18, 0.2) 0%, rgba(3, 7, 18, 0.85) 100%),
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='120' viewBox='0 0 400 120'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop stop-color='%232563eb'/%3E%3Cstop offset='1' stop-color='%23030712'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect fill='url(%23g)' width='400' height='120'/%3E%3C/svg%3E") center/cover;
        }
        .ig-rpanel-event {
            margin: 0 0 0.35rem;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--ig-text) !important;
        }
        .ig-rpanel-meta, .ig-rpanel-loc {
            margin: 0.15rem 0;
            font-size: 0.8rem;
            color: var(--ig-muted) !important;
        }
        .ig-rpanel-title {
            margin: 0 0 0.75rem;
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--ig-text) !important;
        }
        .ig-timeline {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        .ig-timeline-item {
            display: flex;
            gap: 0.65rem;
            padding: 0.55rem 0;
            border-bottom: 1px solid var(--ig-border);
            font-size: 0.78rem;
        }
        .ig-timeline-item:last-child { border-bottom: none; }
        .ig-timeline-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-top: 0.35rem;
            flex-shrink: 0;
            background: var(--ig-blue);
        }
        .ig-timeline-item--feed .ig-timeline-dot { background: var(--ig-gold); }
        .ig-timeline-item--music .ig-timeline-dot { background: #22c55e; }
        .ig-timeline-item strong {
            display: block;
            color: var(--ig-text) !important;
            font-weight: 600;
        }
        .ig-timeline-item span { color: var(--ig-muted) !important; }
        .ig-timeline-item em {
            display: block;
            font-size: 0.68rem;
            color: #64748b !important;
            font-style: normal;
            margin-top: 0.1rem;
        }
        .ig-rank-list {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        .ig-rank-item {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--ig-border);
            font-size: 0.8rem;
        }
        .ig-rank-n {
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 8px;
            background: rgba(37, 99, 235, 0.25);
            color: #93c5fd !important;
            font-weight: 700;
            font-size: 0.72rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .ig-rank-item strong {
            display: block;
            color: var(--ig-text) !important;
            font-size: 0.82rem;
        }
        .ig-rank-item span { color: var(--ig-muted) !important; font-size: 0.72rem; }
        [class*="st-key-ig_rp"] .stButton > button {
            border-radius: 12px !important;
            background: rgba(37, 99, 235, 0.2) !important;
            border: 1px solid rgba(37, 99, 235, 0.45) !important;
            color: #93c5fd !important;
            font-weight: 600 !important;
        }

        /* Week cultos */
        .ig-week-card {
            display: flex;
            gap: 1rem;
            align-items: center;
            padding: 1rem 1.1rem;
            margin-bottom: 0.65rem;
            border-radius: 18px;
            background: var(--ig-card);
            border: 1px solid var(--ig-border);
        }
        .ig-week-badge {
            text-align: center;
            min-width: 3.25rem;
            padding: 0.45rem 0.5rem;
            border-radius: 12px;
            background: rgba(37, 99, 235, 0.2);
            border: 1px solid rgba(37, 99, 235, 0.35);
        }
        .ig-week-dow {
            display: block;
            font-size: 0.58rem;
            font-weight: 700;
            color: #93c5fd !important;
            letter-spacing: 0.06em;
        }
        .ig-week-day {
            display: block;
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--ig-text) !important;
            line-height: 1.1;
        }
        .ig-week-mon {
            display: block;
            font-size: 0.58rem;
            color: var(--ig-muted) !important;
        }
        .ig-week-body h4 {
            margin: 0 0 0.2rem;
            color: var(--ig-text) !important;
            font-size: 0.95rem;
        }
        .ig-week-body p {
            margin: 0;
            font-size: 0.78rem;
            color: var(--ig-muted) !important;
        }
        .ig-week-sub {
            margin: -0.35rem 0 0.85rem;
            font-size: 0.78rem;
            color: var(--ig-muted) !important;
        }
        .ig-week-empty {
            padding: 1.25rem;
            text-align: center;
            color: var(--ig-muted) !important;
            border-radius: 18px;
            border: 1px dashed var(--ig-border);
        }

        /* Tip */
        .ig-tip-card {
            display: flex;
            gap: 0.85rem;
            align-items: flex-start;
            padding: 1.1rem 1.15rem;
            margin-top: 1.25rem;
            border-radius: var(--ig-radius-xl);
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid var(--ig-border);
        }
        .ig-tip-ico {
            width: 2rem;
            height: 2rem;
            flex-shrink: 0;
            border-radius: 10px;
            background: rgba(37, 99, 235, 0.25) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%2393c5fd' stroke-width='2'%3E%3Cpath d='M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83'/%3E%3C/svg%3E") center/16px no-repeat;
        }
        .ig-tip-body strong {
            display: block;
            color: var(--ig-text) !important;
            margin-bottom: 0.25rem;
        }
        .ig-tip-body p {
            margin: 0;
            font-size: 0.82rem;
            color: var(--ig-muted) !important;
            line-height: 1.45;
        }
        [class*="st-key-ig_tip_dismiss"] .stButton > button {
            font-size: 0.75rem !important;
            background: transparent !important;
            border: none !important;
            color: var(--ig-muted) !important;
        }

        /* Dashboard columns */
        [data-testid="column"]:has(.ig-right-panel) {
            position: sticky;
            top: 0.5rem;
            align-self: start;
        }
        .dash-section, .welcome-card, .status-escalado, .status-nao-escalado {
            border-radius: var(--ig-radius-xl) !important;
        }
    """
