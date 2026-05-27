"""Mobile Lab — página Escalas premium (layout personalizado)."""

from __future__ import annotations

import html
from datetime import date, datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


ESCALAS_TABS: tuple[tuple[str, str, str], ...] = (
    ("equipe", "👥", "Minha equipe"),
    ("todas", "📅", "Todas"),
    ("sequencia", "🎵", "Sequência"),
    ("trocas", "🔄", "Trocas"),
    ("solicitacoes", "📬", "Solicitações"),
)


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _active_tab() -> str:
    t = str(st.session_state.get("ml_escalas_tab", "equipe")).strip()
    keys = {k for k, _, _ in ESCALAS_TABS}
    return t if t in keys else "equipe"


def _set_tab(tab: str) -> None:
    st.session_state.ml_escalas_tab = tab


def mobile_escalas_css() -> str:
    return r"""
    body:has(#ml-escalas-page) .ml-esc-header h1{
      font-size: 2rem !important;
      font-weight: 800 !important;
      margin: 0 !important;
      letter-spacing: -0.02em;
    }
    body:has(#ml-escalas-page) .ml-esc-header p{
      color: rgba(148,163,184,.95) !important;
      margin: 0.35rem 0 0 0 !important;
      font-size: 1rem !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="stHorizontalBlock"]{
      display: flex !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      gap: 0.5rem !important;
      padding-bottom: 0.25rem !important;
      -webkit-overflow-scrolling: touch;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tabs"] [data-testid="column"]{
      flex: 0 0 auto !important;
      width: auto !important;
      min-width: max-content !important;
      max-width: none !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tab_"] .stButton > button{
      border-radius: 16px !important;
      padding: 0.55rem 1rem !important;
      min-height: 2.5rem !important;
      font-weight: 700 !important;
      font-size: 0.82rem !important;
      white-space: nowrap !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(148,163,184,.95) !important;
      box-shadow: none !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_tab_"] .stButton > button[kind="primary"]{
      background: rgba(124,58,237,1) !important;
      border-color: rgba(139,92,246,.45) !important;
      color: #fff !important;
      box-shadow: 0 0 22px rgba(139,92,246,.22) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_quick_"] .stButton > button{
      min-height: 5.5rem !important;
      border-radius: 22px !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(226,232,240,.96) !important;
      font-size: 1.35rem !important;
      line-height: 1.2 !important;
      white-space: pre-line !important;
      box-shadow: 0 0 24px rgba(139,92,246,.08) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_quick_"] .stButton > button p{
      font-size: 0.88rem !important;
      font-weight: 800 !important;
      margin-top: 0.35rem !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_action_"] .stButton > button[kind="primary"]{
      width: 100% !important;
      min-height: 3rem !important;
      border-radius: 20px !important;
      font-weight: 800 !important;
      font-size: 1rem !important;
      background: linear-gradient(90deg, rgba(124,58,237,1), rgba(139,92,246,1)) !important;
      border: none !important;
      box-shadow: 0 0 28px rgba(139,92,246,.25) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_member_"] .stButton > button{
      width: 100% !important;
      text-align: left !important;
      justify-content: flex-start !important;
      min-height: 4.5rem !important;
      padding: 0.65rem 0.75rem !important;
      border-radius: 20px !important;
      background: rgba(15,23,42,.55) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      color: rgba(226,232,240,.95) !important;
    }
    body:has(#ml-escalas-page) [class*="st-key-ml_esc_member_"] .stButton > button p{
      margin: 0 !important;
      white-space: normal !important;
      text-align: left !important;
      font-size: 0.78rem !important;
      line-height: 1.25 !important;
    }
    .ml-esc-hero{
      border-radius: 28px;
      padding: 1rem;
      margin-bottom: 1rem;
      position: relative;
      overflow: hidden;
    }
    .ml-esc-hero-bg{
      position: absolute;
      inset: 0;
      opacity: 0.12;
      object-fit: cover;
      width: 100%;
      height: 100%;
    }
    .ml-esc-hero-inner{ position: relative; z-index: 1; }
    .ml-esc-team-row{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      border-radius: 20px;
      background: rgba(15,23,42,.55);
      border: 1px solid rgba(255,255,255,.08);
      margin-bottom: 10px;
    }
    .ml-esc-team-row img, .ml-esc-team-av{
      width: 52px;
      height: 52px;
      border-radius: 18px;
      object-fit: cover;
      flex-shrink: 0;
      border: 2px solid rgba(139,92,246,.35);
    }
    .ml-esc-team-av{
      display:flex;
      align-items:center;
      justify-content:center;
      font-weight: 900;
      background: rgba(59,130,246,.15);
      color: rgba(226,232,240,.95);
    }
    .ml-esc-song{
      border-radius: 22px;
      padding: 14px;
      background: rgba(15,23,42,.72);
      border: 1px solid rgba(255,255,255,.08);
      margin-bottom: 12px;
    }
    .ml-esc-song h4{ margin: 0; font-size: 1rem; font-weight: 800; }
    .ml-esc-song p{ margin: 4px 0 0; color: rgba(148,163,184,.92); font-size: 0.82rem; }
    .ml-esc-pill{
      display:inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      background: rgba(139,92,246,.14);
      border: 1px solid rgba(139,92,246,.25);
      font-size: 0.72rem;
      font-weight: 800;
      color: rgba(196,181,253,.98);
      margin-right: 6px;
    }
    """


def _render_header(*, search_key: str = "ml_esc_search") -> None:
    st.markdown(
        """
        <div id="ml-escalas-page" class="ml-page">
          <div class="ml-esc-header" style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:1rem;">
            <div>
              <h1>Escalas</h1>
              <p>Gerencie ensaios e cultos</p>
            </div>
            <div class="ml-glass ml-iconbtn" style="width:52px;height:52px;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:1.25rem;">🔍</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text_input(
        "Buscar escalas",
        placeholder="Buscar culto, função...",
        key=search_key,
        label_visibility="collapsed",
    )


def _render_tabs(active: str) -> None:
    with st.container(key="ml_esc_tabs"):
        cols = st.columns(len(ESCALAS_TABS), gap="small")
        for col, (key, icon, label) in zip(cols, ESCALAS_TABS):
            with col:
                txt = f"{icon} {label}"
                if st.button(
                    txt,
                    key=f"ml_esc_tab_{key}",
                    type="primary" if active == key else "secondary",
                ):
                    _set_tab(key)
                    st.rerun()


def _render_hero_hub(*, is_manager: bool) -> None:
    mgr_block = ""
    if is_manager:
        mgr_block = """
        <div class="ml-glass" style="border-radius:20px;padding:14px;margin:12px 0;border:1px solid rgba(250,204,21,.15);">
          <div style="display:flex;gap:12px;align-items:flex-start;">
            <div style="width:44px;height:44px;border-radius:16px;background:rgba(250,204,21,.12);display:flex;align-items:center;justify-content:center;font-size:1.35rem;">🎯</div>
            <div>
              <div style="font-weight:800;font-size:1rem;margin-bottom:4px;">Líderes e organizadores</div>
              <div style="color:rgba(148,163,184,.92);font-size:0.88rem;line-height:1.35;">
                Monte escalas, acompanhe ensaios e organize os cultos da semana.
              </div>
            </div>
          </div>
        </div>
        """
    st.markdown(
        f"""
        <div class="ml-glass ml-glow-purple ml-esc-hero">
          <img class="ml-esc-hero-bg" src="https://images.unsplash.com/photo-1504052434569-70ad5836ab65?q=80&w=1200&auto=format&fit=crop" alt="" />
          <div class="ml-esc-hero-inner">
            <div style="display:flex;gap:14px;align-items:center;margin-bottom:10px;">
              <div style="width:56px;height:56px;border-radius:20px;background:rgba(59,130,246,.18);border:1px solid rgba(59,130,246,.25);display:flex;align-items:center;justify-content:center;font-size:1.6rem;">🎤</div>
              <div>
                <div style="font-size:1.35rem;font-weight:900;letter-spacing:-0.02em;">Escalas, ensaios e trocas</div>
                <div style="color:rgba(148,163,184,.92);font-size:0.9rem;margin-top:4px;">Ministério · Escalas e trocas</div>
              </div>
            </div>
            {mgr_block}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if is_manager:
        with st.container(key="ml_esc_action_gerenciar"):
            if st.button("🎯 Abrir Gerenciar Escalas", type="primary", use_container_width=True):
                st.session_state.ml_escalas_gerenciar = True
                st.rerun()


def _render_quick_access() -> None:
    st.markdown(
        '<div style="font-size:1.15rem;font-weight:900;margin:0.5rem 0 0.75rem;">Acesso rápido</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="small")
    with c1:
        with st.container(key="ml_esc_quick_seq"):
            if st.button("🎵\nSequência", use_container_width=True):
                _set_tab("sequencia")
                st.rerun()
    with c2:
        with st.container(key="ml_esc_quick_trocas"):
            if st.button("🔄\nTrocas", use_container_width=True):
                _set_tab("trocas")
                st.rerun()
    c3, c4 = st.columns(2, gap="small")
    with c3:
        with st.container(key="ml_esc_quick_sol"):
            if st.button("📬\nSolicitações", use_container_width=True):
                _set_tab("solicitacoes")
                st.rerun()
    with c4:
        with st.container(key="ml_esc_quick_chat"):
            if st.button("💬\nChat ensaio", use_container_width=True):
                st.session_state.ml_page = "Chat"
                st.rerun()


def _render_not_scheduled_warning() -> None:
    st.markdown(
        """
        <div class="ml-glass ml-glow-gold" style="border-radius:24px;padding:16px;border:1px solid rgba(250,204,21,.2);margin:0.75rem 0;">
          <div style="display:flex;gap:14px;align-items:flex-start;">
            <div style="font-size:2rem;line-height:1;">⚠️</div>
            <div>
              <div style="font-size:1.1rem;font-weight:900;margin-bottom:4px;">Você não está escalado</div>
              <div style="color:rgba(148,163,184,.92);font-size:0.9rem;line-height:1.35;">
                Ou a escala ainda não foi publicada para sua equipe.
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _team_member_card_html(
    nome: str,
    funcao: str,
    photo_uri: str | None,
) -> str:
    initial = (nome.strip()[:1] or "?").upper()
    if photo_uri:
        av = f'<img class="ml-esc-team-av" src="{_esc(photo_uri)}" alt="" />'
    else:
        av = f'<div class="ml-esc-team-av">{_esc(initial)}</div>'
    return f"""
    <div class="ml-esc-team-row">
      {av}
      <div style="flex:1;min-width:0;">
        <div style="font-weight:900;font-size:0.95rem;">{_esc(nome)}</div>
        <div style="margin-top:6px;"><span class="ml-esc-pill">{_esc(funcao.upper())}</span></div>
      </div>
      <div style="color:rgba(148,163,184,.8);font-size:1.1rem;">›</div>
    </div>
    """


def _render_tab_equipe(
    *,
    minhas: list[dict],
    members_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    is_manager: bool,
    search_q: str,
) -> None:
    _render_hero_hub(is_manager=is_manager)
    _render_quick_access()
    if not minhas:
        _render_not_scheduled_warning()
        return

    st.markdown(
        '<div style="font-size:1.05rem;font-weight:900;margin:1rem 0 0.5rem;">Equipe escalada</div>',
        unsafe_allow_html=True,
    )
    from app import format_rehearsal_date_pt, profile_photo_to_data_uri, rehearsal_date_is_set

    q = search_q.strip().lower()
    for item in minhas:
        escala = item["escala"]
        funcao = str(item.get("funcao", "Integrante"))
        ev = str(escala.get("event", "Culto"))
        if q and q not in ev.lower() and q not in funcao.lower():
            continue
        dt = pd.to_datetime(escala.get("date"), errors="coerce")
        date_txt = dt.strftime("%d/%m/%Y") if pd.notna(dt) else ""
        ensaio = (
            format_rehearsal_date_pt(escala)
            if rehearsal_date_is_set(escala)
            else "Ensaio: a definir"
        )
        st.markdown(
            f"""
            <div class="ml-glass" style="border-radius:22px;padding:14px;margin-bottom:12px;">
              <div style="font-size:0.72rem;font-weight:800;color:rgba(148,163,184,.92);text-transform:uppercase;letter-spacing:0.04em;">
                Culto · { _esc(date_txt) }
              </div>
              <div style="font-size:1.2rem;font-weight:900;margin:6px 0 4px;">{_esc(ev)}</div>
              <div style="color:rgba(148,163,184,.92);font-size:0.85rem;">📅 {_esc(ensaio)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        from app import integrantes_escalados, profile_photo_to_data_uri as _photo_uri

        team = integrantes_escalados(escala, equipe_df, members_df)
        for p in team:
            nome = str(p.get("nome", ""))
            if q and q not in nome.lower():
                continue
            email = str(p.get("email", "")).strip().lower()
            foto = _photo_uri(email)
            st.markdown(
                _team_member_card_html(nome, str(p.get("funcao", "Integrante")), foto),
                unsafe_allow_html=True,
            )


def _render_tab_todas(
    *,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    search_q: str,
) -> None:
    from app import member_escala_occurrences, render_culto_programa

    occ = member_escala_occurrences(my_email, escalas_df, equipe_df)
    if not occ:
        st.info("Você ainda não aparece em nenhuma escala registrada.")
        return
    q = search_q.strip().lower()
    st.caption(f"{len(occ)} culto(s) no seu histórico.")
    for i, (_culto_d, eid, _ev) in enumerate(occ):
        row_match = escalas_df[escalas_df["id"].astype(str) == str(eid)]
        if row_match.empty:
            continue
        ev = str(row_match.iloc[0].get("event", ""))
        if q and q not in ev.lower():
            continue
        with st.expander(f"📅 {_esc(ev)}", expanded=(i == 0 and not q)):
            render_culto_programa(
                row_match.iloc[0],
                programa_df,
                equipe_df,
                members_df,
                louvores_df,
                ensaio_notice=True,
                widget_key_prefix=f"ml_todas_{i}_{eid}",
            )


def _render_tab_sequencia(
    *,
    minhas: list[dict],
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    from app import enrich_programa_from_catalog, programa_por_escala
    from catalog_sanitize import format_louvor_display

    if not minhas:
        _render_not_scheduled_warning()
        return

    labels: dict[str, str] = {}
    for item in minhas:
        row = item["escala"]
        eid = str(row.get("id", ""))
        labels[str(row.get("event", "Culto")) + " · " + str(row.get("date", ""))[:10]] = eid

    pick = st.selectbox("Culto", list(labels.keys()), key="ml_esc_seq_pick")
    escala_id = labels[pick]
    prog = programa_por_escala(programa_df, escala_id)
    if louvores_df is not None and not louvores_df.empty:
        prog = enrich_programa_from_catalog(prog, louvores_df)

    st.markdown(
        """
        <div class="ml-glass ml-glow-purple" style="border-radius:22px;padding:14px;margin:0.75rem 0;">
          <div style="font-size:1.5rem;margin-bottom:8px;">🎵</div>
          <div style="font-weight:900;">Sequência do culto</div>
          <div style="color:rgba(148,163,184,.92);font-size:0.88rem;margin-top:6px;">
            YouTube, Voz e Cifra por louvor.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if prog.empty:
        st.info("Programação ainda não montada para este culto.")
        return

    total_min = 0.0
    for idx, (_, r) in enumerate(prog.iterrows()):
        i = idx
        title, artist = format_louvor_display(r)
        tom = str(r.get("key", "") or r.get("tom_programa", "") or "—").strip() or "—"
        dur = str(r.get("duration", "") or "").strip()
        st.markdown(
            f"""
            <div class="ml-esc-song">
              <div style="display:flex;gap:10px;align-items:flex-start;">
                <div style="width:28px;height:28px;border-radius:12px;background:rgba(139,92,246,.18);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:0.82rem;">{i+1}</div>
                <div style="flex:1;min-width:0;">
                  <h4>{_esc(title)}</h4>
                  <p>{_esc(artist)}</p>
                  <div style="margin-top:8px;">
                    <span class="ml-esc-pill">Tom: {_esc(tom)}</span>
                    {f'<span style="color:rgba(148,163,184,.9);font-size:0.78rem;">⏱ {_esc(dur)}</span>' if dur else ''}
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            from app import parse_duracao_min

            total_min += float(parse_duracao_min(dur) or 0)
        except Exception:
            pass

    if total_min > 0:
        st.markdown(
            f'<div class="ml-glass" style="padding:12px 14px;border-radius:18px;margin-top:8px;">⏱ Duração estimada: <b>{int(total_min)} min</b></div>',
            unsafe_allow_html=True,
        )


def _render_tab_trocas(
    *,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> None:
    from app import user_escalas

    st.markdown(
        """
        <div class="ml-glass" style="border-radius:22px;padding:14px;margin-bottom:12px;">
          <div style="font-size:1.4rem;margin-bottom:6px;">🔄</div>
          <div style="font-weight:900;">Trocar escala</div>
          <p style="color:rgba(148,163,184,.92);font-size:0.88rem;margin:8px 0 0;line-height:1.35;">
            Divulgue para o grupo ou peça a um integrante. A escala atualiza após aceite.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    minhas = user_escalas(escalas_df, my_email, equipe_df)
    if minhas.empty:
        st.warning("Você não está em nenhuma escala para solicitar troca.")
        return
    st.dataframe(minhas[["event", "date"]].head(10), use_container_width=True, hide_index=True)
    st.caption("Use a versão web em Gerenciar Escalas para fluxo completo de troca (em breve no mobile).")


def _render_tab_solicitacoes(
    *,
    my_email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
) -> None:
    from app import accept_open_swap, escala_label, swap_alerts_for_user

    _, rec, env = swap_alerts_for_user(
        trocas_df, my_email, escalas_df=escalas_df, equipe_df=equipe_df
    )
    st.markdown("#### 📥 Recebidos")
    if rec.empty:
        st.info("Nenhum pedido direcionado a você.")
    for _, t in rec.iterrows():
        o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
        txt = escala_label(o.iloc[0]) if not o.empty else "—"
        st.markdown(f"**{t['requester_name']}** — {txt}")
        if t.get("message"):
            st.caption(str(t["message"]))
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Aceitar", key=f"ml_acc_{t['id']}", use_container_width=True):
                name = st.session_state.user_full_name or st.session_state.user_name
                escalas_df, equipe_df, trocas_df, ok = accept_open_swap(
                    t, my_email, name, escalas_df, equipe_df, trocas_df
                )
                if ok:
                    from app import EQUIPE_FILE, ESCALAS_FILE, TROCAS_FILE, save_data

                    save_data(escalas_df, ESCALAS_FILE)
                    save_data(equipe_df, EQUIPE_FILE)
                    save_data(trocas_df, TROCAS_FILE)
                    st.rerun()
                else:
                    st.error("Não foi possível aceitar (conflito de escala).")
        with c2:
            if st.button("❌ Recusar", key=f"ml_rec_{t['id']}", use_container_width=True):
                from app import TROCAS_FILE, prepare_trocas, save_data

                trocas_df = prepare_trocas(trocas_df)
                trocas_df.loc[trocas_df["id"].astype(str) == str(t["id"]), "status"] = "recusada"
                save_data(trocas_df, TROCAS_FILE)
                st.rerun()

    st.markdown("#### 📤 Enviados")
    if env.empty:
        st.info("Nenhum pedido enviado pendente.")
    for _, t in env.iterrows():
        o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
        alvo = t.get("target_name") or "o grupo"
        st.caption(
            f"Aguardando {alvo} · {escala_label(o.iloc[0]) if not o.empty else '—'}"
        )


def render_mobile_escalas_page(
    *,
    escalas_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    chat_ensaio_df: pd.DataFrame,
) -> None:
    """Página Escalas mobile premium com abas e funções do app web."""
    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_escalas_css()}</style>", unsafe_allow_html=True)

    if st.session_state.pop("ml_escalas_gerenciar", False):
        from app import show_gerenciar_escalas

        if st.button("← Voltar para Escalas", key="ml_esc_back_hub"):
            st.rerun()
        show_gerenciar_escalas(
            escalas_df,
            programa_df,
            equipe_df,
            louvores_df,
            members_df,
            chat_ensaio_df,
        )
        return

    from app import is_scale_manager, user_on_escala_semana, week_bounds

    my_email = str(st.session_state.get("user_email", "")).strip().lower()
    is_mgr = is_scale_manager(st.session_state.get("user_roles", []))
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0
    start, end = week_bounds(st.session_state.get("week_offset", 0))
    minhas = user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)

    active = _active_tab()
    _render_header()
    _render_tabs(active)

    search_q = str(st.session_state.get("ml_esc_search", "") or "")

    if active == "equipe":
        _render_tab_equipe(
            minhas=minhas,
            members_df=members_df,
            equipe_df=equipe_df,
            is_manager=is_mgr,
            search_q=search_q,
        )
    elif active == "todas":
        _render_tab_todas(
            my_email=my_email,
            escalas_df=escalas_df,
            equipe_df=equipe_df,
            members_df=members_df,
            programa_df=programa_df,
            louvores_df=louvores_df,
            search_q=search_q,
        )
    elif active == "sequencia":
        _render_tab_sequencia(
            minhas=minhas,
            programa_df=programa_df,
            louvores_df=louvores_df,
        )
    elif active == "trocas":
        _render_tab_trocas(
            my_email=my_email,
            escalas_df=escalas_df,
            equipe_df=equipe_df,
            trocas_df=trocas_df,
            members_df=members_df,
        )
    elif active == "solicitacoes":
        _render_tab_solicitacoes(
            my_email=my_email,
            escalas_df=escalas_df,
            equipe_df=equipe_df,
            trocas_df=trocas_df,
        )

    st.markdown("</div>", unsafe_allow_html=True)
