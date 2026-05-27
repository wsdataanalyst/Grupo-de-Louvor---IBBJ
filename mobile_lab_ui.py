"""Mobile Lab UI: dashboard premium (modo testes)."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st


def mobile_lab_css() -> str:
    return r"""
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    :root{
      --ml-bg:#030712;
      --ml-glass: rgba(15,23,42,.72);
      --ml-border: rgba(255,255,255,.08);
      --ml-blue: rgba(37,99,235,.20);
      --ml-purple: rgba(139,92,246,.25);
      --ml-gold: rgba(212,160,23,.20);
      --ml-text-dim: rgba(148,163,184,.92);
      --ml-nav-height: 60px;
      --ml-nav-offset: max(16px, env(safe-area-inset-bottom, 0px));
      --ml-verse-height: 56px;
    }

    /* Hide Streamlit chrome for "app" feel */
    body:has(#ml-mobile-lab-mode) [data-testid="stSidebar"],
    body:has(#ml-bottom-nav-start) [data-testid="stSidebar"],
    body:has(.ml-page) [data-testid="stSidebar"] { display:none !important; }
    body:has(#ml-mobile-lab-mode) [data-testid="stHeader"],
    body:has(#ml-bottom-nav-start) [data-testid="stHeader"],
    body:has(.ml-page) [data-testid="stHeader"] { display:none !important; }
    body:has(#ml-mobile-lab-mode) [data-testid="stToolbar"],
    body:has(#ml-bottom-nav-start) [data-testid="stToolbar"],
    body:has(.ml-page) [data-testid="stToolbar"] { display:none !important; }
    /* Widgets Streamlit (somente chrome — sem header/footer genéricos) */
    body:has(#ml-mobile-lab-mode) [data-testid="stStatusWidget"],
    body:has(#ml-mobile-lab-mode) [data-testid="stDecoration"],
    body:has(#ml-mobile-lab-mode) .stAppDeployButton,
    body:has(#ml-mobile-lab-mode) .stDeployButton,
    body:has(#ml-mobile-lab-mode) [class*="stAppDeployButton"],
    body:has(#ml-mobile-lab-mode) [class*="stDeployButton"],
    body:has(#ml-mobile-lab-mode) [data-testid="stToolbarActions"],
    body:has(#ml-mobile-lab-mode) #MainMenu {
      display: none !important;
      visibility: hidden !important;
      opacity: 0 !important;
      pointer-events: none !important;
    }
    /* Escudo pequeno no canto (só cobre ícones Cloud/GitHub) */
    body:has(#ml-mobile-lab-mode) #ml-streamlit-shield{
      position: fixed !important;
      right: 0 !important;
      bottom: 0 !important;
      width: 56px !important;
      height: calc(64px + env(safe-area-inset-bottom, 0px)) !important;
      z-index: 2147483644 !important;
      background: var(--ml-bg, #030712) !important;
      pointer-events: none !important;
      box-sizing: border-box !important;
    }
    /* Faixa do versículo do dia (cobre ícones do Cloud no rodapé) */
    body:has(#ml-mobile-lab-mode) #ml-verse-strip{
      position: fixed !important;
      left: 0 !important;
      right: 0 !important;
      bottom: 0 !important;
      height: calc(var(--ml-verse-height) + env(safe-area-inset-bottom, 0px)) !important;
      padding: 10px 14px calc(10px + env(safe-area-inset-bottom, 0px)) 14px !important;
      background: rgba(3,7,18,.92) !important;
      backdrop-filter: blur(14px) !important;
      -webkit-backdrop-filter: blur(14px) !important;
      border-top: 1px solid rgba(255,255,255,.06) !important;
      z-index: 2147483600 !important;
      box-sizing: border-box !important;
      display: flex !important;
      align-items: center !important;
      gap: 12px !important;
    }
    body:has(#ml-mobile-lab-mode) #ml-verse-strip .ml-verse-ico{
      width: 34px; height: 34px;
      border-radius: 14px;
      display:flex; align-items:center; justify-content:center;
      background: rgba(139,92,246,.16);
      border: 1px solid rgba(139,92,246,.30);
      color: rgba(233,213,255,.98);
      flex: 0 0 auto;
      font-size: 16px;
    }
    body:has(#ml-mobile-lab-mode) #ml-verse-strip .ml-verse-txt{
      min-width: 0;
      color: rgba(226,232,240,.96);
      font-family: 'Manrope', system-ui, sans-serif;
      font-size: 12px;
      line-height: 1.15;
      font-weight: 700;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    body:has(#ml-mobile-lab-mode) #ml-verse-strip .ml-verse-ref{
      color: rgba(148,163,184,.92);
      font-size: 11px;
      font-weight: 800;
      margin-left: 8px;
      white-space: nowrap;
      flex: 0 0 auto;
    }
    body:has(#ml-bottom-nav-start) [data-testid="stAppViewContainer"],
    body:has(.ml-page) [data-testid="stAppViewContainer"] {
      background:
        radial-gradient(circle at top left, var(--ml-blue), transparent 30%),
        radial-gradient(circle at top right, var(--ml-purple), transparent 30%),
        var(--ml-bg) !important;
    }
    body:has(#ml-bottom-nav-start) [data-testid="stAppViewContainer"] .main .block-container,
    body:has(.ml-page) [data-testid="stAppViewContainer"] .main .block-container{
      max-width: 28rem !important;
      margin: 0 auto !important;
      padding: 0.2rem 0.75rem calc(var(--ml-nav-height) + var(--ml-verse-height) + var(--ml-nav-offset) + 24px) !important;
    }
    /* fixed relativo à viewport (evita corte no fim do .main do Streamlit) */
    body:has(#ml-bottom-nav-start) [data-testid="stAppViewContainer"],
    body:has(#ml-bottom-nav-start) [data-testid="stAppViewContainer"] > section,
    body:has(#ml-bottom-nav-start) [data-testid="stMain"],
    body:has(#ml-bottom-nav-start) .main {
      transform: none !important;
      filter: none !important;
      perspective: none !important;
    }

    /* Page container */
    .ml-page {
      color: #fff;
      background:
        radial-gradient(circle at top left, var(--ml-blue), transparent 30%),
        radial-gradient(circle at top right, var(--ml-purple), transparent 30%),
        var(--ml-bg);
      border-radius: 28px;
      padding: 12px 14px 96px 14px;
      max-width: 420px;
      margin: 0 auto;
    }

    .ml-glass{
      background: var(--ml-glass);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--ml-border);
    }
    .ml-glow-blue{ box-shadow: 0 0 30px rgba(37,99,235,.20); }
    .ml-glow-purple{ box-shadow: 0 0 30px rgba(139,92,246,.25); }
    .ml-glow-gold{ box-shadow: 0 0 30px rgba(212,160,23,.20); }

    .ml-top{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom: 12px; }
    .ml-user{ display:flex; align-items:center; gap:12px; min-width: 0; }
    .ml-avatar{
      width: 56px; height: 56px; border-radius: 999px;
      border: 2px solid rgba(59,130,246,.85);
      overflow:hidden;
      background: rgba(59,130,246,.12);
      flex: 0 0 auto;
    }
    .ml-avatar img{ width:100%; height:100%; object-fit:cover; display:block; }
    .ml-hello{ min-width:0; }
    .ml-hello h1{ font-size: 22px; line-height: 1.05; margin: 0; font-weight: 800; letter-spacing: -0.02em;}
    .ml-hello p{ margin: 6px 0 0 0; color: var(--ml-text-dim); font-size: 14px; }

    .ml-actions{ display:flex; gap:10px; }
    .ml-iconbtn{
      width: 44px; height: 44px; border-radius: 18px;
      display:flex; align-items:center; justify-content:center;
      font-size: 18px; position: relative;
    }
    .ml-badge{
      position:absolute; top:-6px; right:-6px;
      width: 22px; height: 22px;
      border-radius: 999px;
      background: #facc15;
      color: #000;
      display:flex; align-items:center; justify-content:center;
      font-size: 12px; font-weight: 800;
      border: 2px solid var(--ml-bg);
    }

    .ml-card{ border-radius: 26px; padding: 16px; }
    .ml-hero{ border-radius: 28px; overflow:hidden; position:relative; margin-bottom: 16px; }
    .ml-hero img{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity: .25; }
    .ml-hero .ml-hero-inner{ position:relative; padding: 16px; }
    .ml-pill{
      display:inline-flex; gap:8px; align-items:center;
      padding: 8px 12px; border-radius: 16px;
      background: rgba(139,92,246,.18);
      color: rgba(196,181,253,.95);
      font-weight: 800; font-size: 12px;
      margin-bottom: 10px;
    }
    .ml-hero h2{ margin:0; font-size: 26px; font-weight: 900; letter-spacing:-0.02em; }
    .ml-meta{ margin-top: 8px; display:flex; gap:12px; color: rgba(226,232,240,.9); font-size: 13px; }
    .ml-hero-row{ margin-top: 12px; display:flex; gap:10px; align-items:center; justify-content:space-between; flex-wrap: wrap;}
    .ml-mini{ padding: 10px 12px; border-radius: 18px; font-size: 13px; white-space: nowrap;}
    .ml-cta{
      border: 0;
      padding: 11px 14px;
      border-radius: 18px;
      font-weight: 900;
      font-size: 13px;
      background: linear-gradient(90deg, rgba(124,58,237,1), rgba(139,92,246,1));
      color:#fff;
    }

    .ml-grid2{ display:grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
    .ml-metric .ml-emoji{ font-size: 26px; margin-bottom: 8px; }
    .ml-metric .ml-val{ font-size: 20px; font-weight: 900; letter-spacing:-0.02em; }
    .ml-metric .ml-lbl{ margin-top: 6px; color: var(--ml-text-dim); font-size: 13px; }

    .ml-section-h{ display:flex; align-items:center; justify-content:space-between; margin: 10px 0 10px 0; }
    .ml-section-h h3{ margin:0; font-size: 16px; font-weight: 900; }
    .ml-link{ color: rgba(167,139,250,.95); font-weight: 800; font-size: 13px; }

    .ml-quick{ display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .ml-quick .ml-q{ padding: 16px; text-align:center; border-radius: 26px; }
    .ml-quick .ml-q .ml-qe{ font-size: 26px; margin-bottom: 10px; }
    .ml-quick .ml-q .ml-qt{ font-size: 14px; font-weight: 900; }
    /* Quick access: botões Streamlit com cara de card */
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_quick_"] .stButton > button{
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 26px !important;
      min-height: 96px !important;
      padding: 12px 10px !important;
      color: rgba(226,232,240,.96) !important;
      box-shadow: 0 0 24px rgba(139,92,246,.10) !important;
      font-family: 'Manrope', system-ui, sans-serif !important;
      white-space: normal !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_quick_"] .stButton > button p{
      margin: 0 !important;
      font-size: 14px !important;
      font-weight: 900 !important;
      line-height: 1.1 !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_quick_"] .stButton > button:hover{
      border-color: rgba(139,92,246,.28) !important;
      box-shadow: 0 0 30px rgba(139,92,246,.18) !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_quick_"] .stButton > button:active{
      transform: translateY(1px) !important;
    }

    /* Bottom nav — container fixo; 5 colunas iguais (override mobile stack) */
    #ml-bottom-nav-start{
      display: none !important;
      height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"]{
      position: fixed !important;
      left: 50% !important;
      right: auto !important;
      bottom: auto !important;
      top: calc(100vh - var(--ml-nav-height) - var(--ml-verse-height) - var(--ml-nav-offset)) !important;
      top: calc(100svh - var(--ml-nav-height) - var(--ml-verse-height) - var(--ml-nav-offset)) !important;
      transform: translateX(-50%) !important;
      width: min(420px, calc(100vw - 16px)) !important;
      max-width: 420px !important;
      z-index: 2147483000 !important;
      margin: 0 !important;
      padding: 6px max(10px, env(safe-area-inset-right, 0px)) 6px 8px !important;
      box-sizing: border-box !important;
      background: rgba(15,23,42,.88) !important;
      backdrop-filter: blur(20px) !important;
      -webkit-backdrop-filter: blur(20px) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 30px !important;
      box-shadow: 0 0 30px rgba(139,92,246,.12) !important;
      pointer-events: auto !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      align-items: stretch !important;
      gap: 0 !important;
      width: 100% !important;
      margin: 0 !important;
      padding: 0 !important;
      position: static !important;
      transform: none !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] [data-testid="stHorizontalBlock"] > [data-testid="column"]{
      flex: 1 1 0 !important;
      width: 20% !important;
      max-width: 20% !important;
      min-width: 0 !important;
      padding: 0 1px !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] [data-testid="stVerticalBlock"]{
      gap: 0 !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] [data-testid="stButton"]{
      margin: 0 !important;
      width: 100% !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] .stButton > button{
      width: 100% !important;
      min-height: 46px !important;
      height: auto !important;
      padding: 5px 2px 6px !important;
      margin: 0 !important;
      border: none !important;
      border-radius: 14px !important;
      background: transparent !important;
      box-shadow: none !important;
      color: rgba(148,163,184,.95) !important;
      font-family: 'Manrope', system-ui, sans-serif !important;
      font-size: 1.15rem !important;
      line-height: 1.05 !important;
      white-space: pre-line !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] .stButton > button p{
      font-size: 0.62rem !important;
      font-weight: 800 !important;
      margin: 0.15rem 0 0 0 !important;
      line-height: 1 !important;
      letter-spacing: -0.02em !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] .stButton > button[kind="primary"],
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] .stButton > button[kind="secondary"]{
      background: transparent !important;
      border: none !important;
      color: rgba(148,163,184,.95) !important;
      box-shadow: none !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_nav_Gerenciar_Escalas"] .stButton > button:not([kind="primary"]){
      background: rgba(250,204,21,.14) !important;
      border: 1px solid rgba(250,204,21,.32) !important;
      color: #fde68a !important;
      box-shadow: 0 0 18px rgba(250,204,21,.12) !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_nav_Gerenciar_Escalas"] .stButton > button[kind="primary"]{
      background: linear-gradient(135deg, #facc15, #ca8a04) !important;
      color: #0f172a !important;
      font-weight: 900 !important;
      box-shadow: 0 0 22px rgba(250,204,21,.28) !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_drawer_gerenciar_item"] .stButton > button{
      border: 1px solid rgba(250,204,21,.28) !important;
      color: #fde68a !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_drawer_gerenciar_active"] .stButton > button{
      background: linear-gradient(135deg, #facc15, #ca8a04) !important;
      color: #0f172a !important;
      font-weight: 800 !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_quick_gerenciar"] .stButton > button,
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_quick_gerenciar"] .stButton > button{
      min-height: 4.2rem !important;
      background: linear-gradient(135deg, rgba(250,204,21,.22), rgba(124,58,237,.15)) !important;
      border: 1px solid rgba(250,204,21,.35) !important;
      color: #fde68a !important;
      font-weight: 900 !important;
      box-shadow: 0 0 28px rgba(250,204,21,.15) !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] .stButton > button[kind="primary"]{
      color: rgba(196,181,253,.98) !important;
      background: rgba(139,92,246,.16) !important;
      border: 1px solid rgba(139,92,246,.32) !important;
      box-shadow: 0 0 16px rgba(139,92,246,.18) !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_bottom_nav"] .stButton > button[kind="primary"] p{
      color: rgba(233,213,255,.98) !important;
    }
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_nav_Gerenciar_Escalas"] .stButton > button[kind="primary"],
    body:has(#ml-bottom-nav-start) [class*="st-key-ml_nav_Gerenciar_Escalas"] .stButton > button[kind="primary"] p{
      background: linear-gradient(135deg, #facc15, #ca8a04) !important;
      color: #0f172a !important;
      border: 1px solid rgba(250,204,21,.45) !important;
      box-shadow: 0 0 22px rgba(250,204,21,.28) !important;
    }

    /* Drawer overlay */
    .ml-drawer-overlay{
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,.55);
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      z-index: 1200;
      display:flex;
      align-items: stretch;
    }
    .ml-drawer{
      width: min(320px, 86vw);
      height: 100%;
      padding: 14px 14px 18px;
      border-top-right-radius: 26px;
      border-bottom-right-radius: 26px;
      background: rgba(15,23,42,.88);
      border-right: 1px solid rgba(255,255,255,.10);
      box-shadow: 0 20px 60px rgba(0,0,0,.5);
    }
    .ml-drawer h3{ margin: 6px 0 12px 0; font-size: 16px; font-weight: 900; }
    .ml-drawer-btn{
      display:flex;
      align-items:center;
      gap:10px;
      padding: 12px 12px;
      border-radius: 18px;
      color: rgba(226,232,240,.95);
      border: 1px solid rgba(255,255,255,.08);
      margin-bottom: 10px;
      background: rgba(15,23,42,.55);
      width: 100%;
      text-align: left;
      cursor: pointer;
    }
    .ml-drawer-btn.active{
      border-color: rgba(139,92,246,.55);
      box-shadow: 0 0 20px rgba(139,92,246,.20);
      color: rgba(233,213,255,.98);
    }
    .ml-drawer .ml-logout{
      margin-top: 10px;
      border-color: rgba(239,68,68,.35);
      background: rgba(239,68,68,.10);
    }

    /* Drawer (Streamlit) — overlay fixo e painel à esquerda */
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_drawer_overlay"]{
      position: fixed !important;
      inset: 0 !important;
      z-index: 2147483500 !important;
      background: rgba(0,0,0,.55) !important;
      backdrop-filter: blur(6px) !important;
      -webkit-backdrop-filter: blur(6px) !important;
      padding: 12px !important;
      box-sizing: border-box !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_drawer_panel"]{
      width: min(320px, 86vw) !important;
      height: calc(100vh - 24px) !important;
      background: rgba(15,23,42,.92) !important;
      border: 1px solid rgba(255,255,255,.10) !important;
      border-radius: 26px !important;
      box-shadow: 0 20px 60px rgba(0,0,0,.50) !important;
      padding: 14px !important;
      overflow: auto !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_drawer_panel"] .stButton > button{
      width: 100% !important;
      text-align: left !important;
      justify-content: flex-start !important;
      background: rgba(15,23,42,.55) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      border-radius: 18px !important;
      min-height: 46px !important;
      padding: 10px 12px !important;
      color: rgba(226,232,240,.95) !important;
      font-weight: 800 !important;
      box-shadow: none !important;
      white-space: nowrap !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_active"] .stButton > button{
      border-color: rgba(139,92,246,.55) !important;
      box-shadow: 0 0 20px rgba(139,92,246,.20) !important;
      color: rgba(233,213,255,.98) !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_drawer_panel"] [class*="st-key-ml_drawer_logout"] .stButton > button{
      border-color: rgba(239,68,68,.35) !important;
      background: rgba(239,68,68,.10) !important;
    }
    /* Botão ☰ fixo no topo */
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_drawer_toggle"]{
      position: fixed !important;
      top: max(10px, env(safe-area-inset-top, 0px)) !important;
      right: max(10px, env(safe-area-inset-right, 0px)) !important;
      z-index: 2147483601 !important;
    }
    body:has(#ml-mobile-lab-mode) [class*="st-key-ml_drawer_toggle"] .stButton > button{
      width: 44px !important;
      height: 44px !important;
      min-height: 44px !important;
      padding: 0 !important;
      border-radius: 18px !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(226,232,240,.95) !important;
      box-shadow: 0 0 18px rgba(139,92,246,.10) !important;
    }
    """


_ML_CHROME_HIDE_JS = r"""
(function () {
  if (window.__mlChromeHideInit) return;
  window.__mlChromeHideInit = true;

  var SHIELD_ID = "ml-streamlit-shield";
  var BG = "#030712";
  var SEL =
    '[data-testid="stStatusWidget"],' +
    '[data-testid="stDecoration"],' +
    '.stAppDeployButton,.stDeployButton,' +
    '[class*="stAppDeployButton"],[class*="stDeployButton"],' +
    '[data-testid="stToolbarActions"],#MainMenu';

  function hideKnown() {
    document.querySelectorAll(SEL).forEach(function (el) {
      el.style.setProperty("display", "none", "important");
      el.style.setProperty("visibility", "hidden", "important");
    });
    document.querySelectorAll('a[href*="github.com"],a[href*="streamlit.io"]').forEach(function (a) {
      if (a.closest('[class*="st-key-ml_bottom_nav"]')) return;
      a.style.setProperty("display", "none", "important");
    });
  }

  function ensureShield() {
    if (!document.body) return;
    var el = document.getElementById(SHIELD_ID);
    if (!el) {
      el = document.createElement("div");
      el.id = SHIELD_ID;
      el.setAttribute("aria-hidden", "true");
      document.body.appendChild(el);
    }
    el.style.cssText =
      "position:fixed;right:0;bottom:0;width:56px;" +
      "height:calc(64px + env(safe-area-inset-bottom,0px));" +
      "z-index:2147483644;background:" + BG + ";pointer-events:none;";
  }

  function liftNav() {
    document.querySelectorAll('[class*="st-key-ml_bottom_nav"]').forEach(function (el) {
      el.style.setProperty("z-index", "2147483000", "important");
    });
  }

  function run() {
    hideKnown();
    ensureShield();
    liftNav();
  }

  run();
  [100, 400, 1200].forEach(function (ms) { setTimeout(run, ms); });
  try {
    new MutationObserver(run).observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  } catch (e) {}
})();
"""


def inject_mobile_lab_hide_streamlit_chrome() -> None:
    """CSS + JS: remove status/deploy do Streamlit (iframe e parent no Cloud)."""
    try:
        st.html(
            f"<script>{_ML_CHROME_HIDE_JS}</script>",
            unsafe_allow_javascript=True,
        )
    except Exception:
        import streamlit.components.v1 as components

        components.html(
            f'<div aria-hidden="true" style="display:none"><script>{_ML_CHROME_HIDE_JS}</script></div>',
            height=0,
            scrolling=False,
        )


def inject_mobile_lab_app_shell() -> None:
    """Marca o modo mobile lab cedo e injeta CSS (widgets Streamlit fora da nav)."""
    verse_text = ""
    verse_ref = ""
    try:
        from verse_of_day import verse_for_date

        v = verse_for_date()
        verse_text = str(v.get("text", "")).strip()
        verse_ref = str(v.get("ref", "")).strip()
    except Exception:
        verse_text = ""
        verse_ref = ""

    strip_html = ""
    if verse_text:
        safe_txt = verse_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_ref = verse_ref.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        strip_html = (
            '<div id="ml-verse-strip" aria-label="Versículo do dia">'
            '<div class="ml-verse-ico">📖</div>'
            f'<div class="ml-verse-txt">{safe_txt}</div>'
            f'<div class="ml-verse-ref">{safe_ref}</div>'
            "</div>"
        )

    st.markdown(
        '<span id="ml-mobile-lab-mode" aria-hidden="true"></span>'
        '<div id="ml-streamlit-shield" aria-hidden="true"></div>'
        f"{strip_html}",
        unsafe_allow_html=True,
    )
    inject_mobile_lab_theme()
    inject_mobile_lab_hide_streamlit_chrome()


def inject_mobile_lab_theme() -> None:
    st.markdown(f"<style>{mobile_lab_css()}</style>", unsafe_allow_html=True)


def _pt_weekday(d: date) -> str:
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    return dias[d.weekday()]


def _next_culto(escalas_df: pd.DataFrame) -> dict:
    if escalas_df is None or escalas_df.empty:
        return {}
    df = escalas_df.copy()
    df["_dt"] = pd.to_datetime(df.get("date"), errors="coerce")
    df = df[df["_dt"].notna()].sort_values("_dt")
    now = datetime.now()
    df = df[df["_dt"] >= now]
    if df.empty:
        return {}
    row = df.iloc[0]
    dt = row["_dt"].to_pydatetime()
    return {
        "event": str(row.get("event", "Culto")).strip() or "Culto",
        "weekday": _pt_weekday(dt.date()),
        "time": dt.strftime("%Hh%M"),
        "date": dt.date(),
    }


_ML_MENU_TO_PAGE: dict[str, str] = {
    "Gerenciar Escalas": "Gerenciar Escalas",
    "Escalas": "Escalas",
    "Repertório": "Repertório",
    "Playlist": "Playlist",
    "Chat": "Chat",
    "Sugestão de louvor": "Sugestões",
    "Sugestões": "Sugestões",
    "Notificações": "Notificações",
    "Feed": "Notificações",
    "Perfil": "Perfil",
}


def render_mobile_lab_dashboard(
    *,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    chat_unread: int = 0,
    user_full_name: str = "",
    photo_uri: str = "",
    notif_count: int = 0,
    is_manager: bool = False,
    quick_links: list[tuple[str, str]] | None = None,
    can_gerenciar: bool | None = None,
) -> None:
    inject_mobile_lab_theme()

    first = (str(user_full_name).strip().split(" ") or [""])[:1][0]
    hello = first or "bem-vindo"
    next_culto = _next_culto(escalas_df)

    n_louvores = 0 if louvores_df is None else int(len(louvores_df))
    n_membros = 0 if members_df is None else int(len(members_df))

    # cultos semana (próximos 7 dias)
    cultos_semana = 0
    if escalas_df is not None and not escalas_df.empty:
        dt = pd.to_datetime(escalas_df.get("date"), errors="coerce")
        start = datetime.now()
        end = start + timedelta(days=7)
        cultos_semana = int(((dt >= start) & (dt <= end)).sum())

    pendencias = int(max(0, chat_unread))

    avatar_html = ""
    if photo_uri:
        avatar_html = f'<img src="{photo_uri}" alt="avatar" />'
    else:
        initial = (first[:1] or "•").upper()
        avatar_html = (
            f'<div style="width:100%;height:100%;display:flex;align-items:center;'
            f'justify-content:center;font-weight:900;color:rgba(226,232,240,.95);'
            f'font-family:Manrope,system-ui,sans-serif;font-size:18px;">{initial}</div>'
        )

    hero_title = next_culto.get("event", "Próximo culto")
    hero_weekday = next_culto.get("weekday", "")
    hero_time = next_culto.get("time", "")

    st.markdown(
        f"""
        <div class="ml-page">
          <div class="ml-top">
            <div class="ml-user">
              <div class="ml-avatar">{avatar_html}</div>
              <div class="ml-hello">
                <h1>Olá, {hello} 👋</h1>
                <p>Que bom te ver por aqui!</p>
              </div>
            </div>
            <div class="ml-actions">
              <div class="ml-glass ml-iconbtn ml-glow-purple">🔔</div>
              <div class="ml-glass ml-iconbtn">☰</div>
            </div>
          </div>

          <div class="ml-glass ml-hero ml-glow-purple">
            <img src="https://images.unsplash.com/photo-1504052434569-70ad5836ab65?q=80&w=1200&auto=format&fit=crop" />
            <div class="ml-hero-inner">
              <div class="ml-pill">📅 PRÓXIMO CULTO</div>
              <h2>{hero_title}</h2>
              <div class="ml-meta">
                <span>📆 {hero_weekday}</span>
                <span>🕘 {hero_time}</span>
              </div>
              <div class="ml-hero-row">
                <div class="ml-glass ml-mini">👥 Escala no app</div>
                <button class="ml-cta">Ver escala completa</button>
              </div>
            </div>
          </div>

          <div class="ml-grid2">
            <div class="ml-glass ml-card ml-metric ml-glow-purple">
              <div class="ml-emoji">🎵</div>
              <div class="ml-val">{n_louvores}</div>
              <div class="ml-lbl">Louvores cadastrados</div>
            </div>
            <div class="ml-glass ml-card ml-metric ml-glow-blue">
              <div class="ml-emoji">👥</div>
              <div class="ml-val">{n_membros}</div>
              <div class="ml-lbl">Membros ativos</div>
            </div>
            <div class="ml-glass ml-card ml-metric ml-glow-gold">
              <div class="ml-emoji">📅</div>
              <div class="ml-val">{cultos_semana}</div>
              <div class="ml-lbl">Cultos esta semana</div>
            </div>
            <div class="ml-glass ml-card ml-metric" style="border:1px solid rgba(34,197,94,.18);">
              <div class="ml-emoji">✅</div>
              <div class="ml-val">{pendencias}</div>
              <div class="ml-lbl">Pendências para você</div>
            </div>
          </div>

          <div class="ml-section-h">
            <h3>Acesso rápido</h3>
            <div class="ml-link">Ver tudo</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    from mobile_lab_nav import navigate_ml_page, user_can_gerenciar_escalas

    ha1, ha2 = st.columns([1, 1], gap="small")
    with ha1:
        with st.container(key="ml_dash_bell"):
            if st.button(
                f"🔔\n{max(0, int(notif_count))}",
                key="ml_dash_bell_btn",
                use_container_width=True,
            ):
                navigate_ml_page("Notificações")
                st.rerun()
    with ha2:
        with st.container(key="ml_dash_menu"):
            if st.button("☰\nMenu", key="ml_dash_menu_btn", use_container_width=True):
                st.session_state.ml_drawer_open = True
                st.rerun()

    if can_gerenciar is None:
        can_gerenciar = bool(st.session_state.get("ml_can_gerenciar"))
    if not can_gerenciar:
        can_gerenciar = bool(is_manager) or user_can_gerenciar_escalas()
    if not can_gerenciar and quick_links:
        can_gerenciar = any(name == "Gerenciar Escalas" for name, _ in quick_links)

    if can_gerenciar:
        with st.container(key="ml_quick_gerenciar"):
            if st.button(
                "🎯  Gerenciar Escalas\nMenu separado · como no app web",
                key="ml_quick_gerenciar_btn",
                use_container_width=True,
                type="primary",
            ):
                navigate_ml_page("Gerenciar Escalas", pin=True)
                st.rerun()

    # Acesso rápido: itens do menu web (quick_links) ou padrão para membros
    default_quick: list[tuple[str, str]] = [
        ("Repertório", "🎵"),
        ("Playlist", "🎧"),
        ("Chat", "💬"),
        ("Sugestões", "💡"),
    ]
    links: list[tuple[str, str, str]] = []
    seen_pages: set[str] = set()
    for name, icon in list(quick_links or []) + default_quick:
        if name == "Gerenciar Escalas":
            continue
        page = _ML_MENU_TO_PAGE.get(name)
        if not page or page in seen_pages:
            continue
        seen_pages.add(page)
        links.append((name, icon, page))

    for i in range(0, len(links), 2):
        pair = links[i : i + 2]
        cols = st.columns(2, gap="small")
        for j, (name, icon, page) in enumerate(pair):
            label = f"{icon}\n{name}"
            if page == "Chat" and int(chat_unread) > 0:
                label = f"{icon} ({min(99, int(chat_unread))})\nChat"
            if name == "Sugestão de louvor":
                label = f"{icon}\nSugestões"
            key = f"ml_quick_{i + j}_{page.replace(' ', '_')}"
            with cols[j]:
                if st.button(label, key=key, use_container_width=True):
                    navigate_ml_page(page)
                    st.rerun()

