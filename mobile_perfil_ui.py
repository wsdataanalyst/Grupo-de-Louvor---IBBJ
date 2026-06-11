"""Mobile Lab — Perfil (layout premium V2)."""

from __future__ import annotations

import html
from datetime import date, datetime

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme

PERF_VIEWS = frozenset({"hub", "edit", "password", "help", "prefs"})

ACCOUNT_MENU: tuple[tuple[str, str, str, str], ...] = (
    ("edit", "✏️", "Editar perfil", "Altere suas informações pessoais"),
    ("password", "🔒", "Alterar senha", "Mantenha sua conta segura"),
    ("prefs", "⚙️", "Preferências", "Notificações, tema e privacidade"),
    ("help", "💬", "Ajuda e suporte", "Tire dúvidas ou fale com nossa equipe"),
)


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _view() -> str:
    v = str(st.session_state.get("ml_perf_view", "hub")).strip()
    return v if v in PERF_VIEWS else "hub"


def _set_view(view: str) -> None:
    st.session_state.ml_perf_view = view


def _time_ago(value: object) -> str:
    try:
        dt = pd.to_datetime(value)
        if pd.isna(dt):
            return "—"
        delta = datetime.now() - dt.to_pydatetime()
        if delta.days > 0:
            return f"há {delta.days}d"
        h = delta.seconds // 3600
        if h > 0:
            return f"há {h}h"
        m = max(1, delta.seconds // 60)
        if m < 2:
            return "Agora"
        return f"há {m}min"
    except (ValueError, TypeError):
        return "—"


def mobile_perfil_css() -> str:
    return r"""
    body:has(#ml-perfil-page) .music-panel-title,
    body:has(#ml-perfil-page) .voice-kit-banner{ display: none !important; }

    body:has(#ml-perfil-page) [data-testid="stMain"] .block-container{
      padding-top: 0.35rem !important;
      max-width: 900px !important;
    }

    .ml-perf-header, .profile-header{
      display: flex; gap: 20px; align-items: flex-start;
      background: #071633; border-radius: 24px; padding: 20px;
      margin-bottom: 20px;
    }
    .ml-perf-avatar-wrap{ position: relative; flex-shrink: 0; }
    .ml-perf-header img, .profile-header img,
    .ml-perf-avatar, .ml-perf-avatar-ph{
      width: 90px; height: 90px; border-radius: 50%;
      object-fit: cover; border: 3px solid #6f4cff;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.8rem; font-weight: 900; color: #e9d5ff;
      background: rgba(111,76,255,.18);
    }
    .ml-perf-cam{
      position: absolute; right: -2px; bottom: -2px;
      width: 28px; height: 28px; border-radius: 50%;
      background: linear-gradient(135deg, #7c3aed, #5b21b6);
      border: 2px solid #071633; display: flex; align-items: center;
      justify-content: center; font-size: 0.72rem;
    }
    .ml-perf-body{ flex: 1; min-width: 0; }
    .ml-perf-name{ margin: 0; font-size: 1.15rem; font-weight: 800; line-height: 1.2; }
    .ml-perf-badges{
      display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.35rem;
      align-items: center;
    }
    .ml-perf-badge{
      display: inline-block; padding: 0.18rem 0.55rem; border-radius: 999px;
      font-size: 0.62rem; font-weight: 700;
    }
    .ml-perf-badge--membro{ background: #3b0764; color: #f3e8ff; }
    .ml-perf-badge--lider{ background: #7c2d12; color: #ffedd5; }
    .ml-perf-badge--coord{ background: #1e3a8a; color: #dbeafe; }
    .ml-perf-badge--dev{ background: #134e4a; color: #ccfbf1; }
    .ml-perf-online{
      font-size: 0.62rem; font-weight: 700; color: #22c55e;
      display: inline-flex; align-items: center; gap: 0.25rem;
    }
    .ml-perf-online-dot{
      width: 7px; height: 7px; border-radius: 50%; background: #22c55e;
    }
    .ml-perf-email{
      margin: 0.4rem 0 0; font-size: 0.72rem; color: #94a3b8;
      display: flex; align-items: center; gap: 0.3rem;
    }
    .ml-perf-roles{
      margin: 0.25rem 0 0; font-size: 0.74rem; color: #cbd5e1; line-height: 1.4;
    }

    .ml-perf-stat-grid{
      display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 0.45rem; margin-bottom: 0.85rem;
    }
    @media (max-width: 420px){
      .ml-perf-stat-grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    .ml-perf-stat{
      background: #091633; border-radius: 18px; padding: 0.65rem 0.3rem;
      text-align: center; border: 1px solid rgba(255,255,255,.06);
    }
    .ml-perf-stat-ico{ font-size: 0.95rem; margin-bottom: 0.15rem; }
    .ml-perf-stat h2{ margin: 0; font-size: 1.15rem; font-weight: 800; }
    .ml-perf-stat span{
      display: block; margin-top: 0.25rem; font-size: 0.58rem; font-weight: 700;
      color: #94a3b8; text-transform: uppercase; letter-spacing: 0.03em;
    }

    .ml-perf-kit, .kitvoz-card{
      background: linear-gradient(90deg, #4026a7, #1f2b6f);
      border-radius: 18px; padding: 18px;
      margin-top: 15px; margin-bottom: 20px;
      font-weight: 600;
      display: flex; align-items: center; gap: 0.65rem;
    }
    .ml-perf-kit small, .kitvoz-card small{
      display: block; font-weight: 600; color: rgba(226,232,240,.9);
      font-size: 0.82rem; margin-top: 0.2rem;
    }

    .ml-perf-level{
      background: rgba(7,20,50,.75); border: 1px solid rgba(255,255,255,.08);
      border-radius: 22px; padding: 0.95rem 1rem; margin-bottom: 0.85rem;
    }
    .ml-perf-level-top{
      display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem;
    }
    .ml-perf-level h3{ margin: 0 0 0.2rem; font-size: 0.9rem; font-weight: 800; }
    .ml-perf-level p{ margin: 0; font-size: 0.72rem; color: #94a3b8; line-height: 1.35; }
    .ml-perf-level-num{
      font-size: 0.72rem; font-weight: 800; color: #c4b5fd; white-space: nowrap;
    }
    .ml-perf-level-bar{
      margin-top: 0.65rem; height: 7px; border-radius: 999px;
      background: rgba(255,255,255,.08); overflow: hidden;
    }
    .ml-perf-level-fill{
      height: 100%; border-radius: 999px;
      background: linear-gradient(90deg, #7c3aed, #a78bfa);
    }
    .ml-perf-level-xp{
      margin-top: 0.35rem; text-align: right; font-size: 0.65rem; color: #94a3b8;
      font-weight: 700;
    }

    .ml-perf-section{
      margin: 0.55rem 0 0.4rem; font-size: 0.92rem; font-weight: 800;
      display: flex; align-items: center; justify-content: space-between;
    }
    .ml-perf-section a{ font-size: 0.72rem; color: #a78bfa; font-weight: 700; text-decoration: none; }

    .ml-perf-activity{
      display: flex; align-items: center; gap: 0.7rem;
      background: rgba(7,20,50,.55); border: 1px solid rgba(255,255,255,.06);
      border-radius: 18px; padding: 0.7rem 0.8rem; margin-bottom: 0.45rem;
    }
    .ml-perf-act-ico{
      width: 38px; height: 38px; border-radius: 12px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center; font-size: 1rem;
    }
    .ml-perf-act-ico--orange{ background: rgba(249,115,22,.18); }
    .ml-perf-act-ico--green{ background: rgba(34,197,94,.18); }
    .ml-perf-act-ico--purple{ background: rgba(124,58,237,.18); }
    .ml-perf-act-ico--blue{ background: rgba(37,99,235,.18); }
    .ml-perf-act-body{ flex: 1; min-width: 0; }
    .ml-perf-act-title{ font-size: 0.8rem; font-weight: 700; margin: 0; }
    .ml-perf-act-sub{ font-size: 0.68rem; color: #94a3b8; margin-top: 0.1rem; }
    .ml-perf-act-time{ font-size: 0.65rem; color: #64748b; flex-shrink: 0; }

    .ml-perf-menu{
      background: rgba(7,20,50,.55); border: 1px solid rgba(255,255,255,.06);
      border-radius: 22px; overflow: hidden; margin-bottom: 0.85rem;
    }
    .ml-perf-menu-item{
      display: flex; align-items: center; gap: 0.75rem;
      padding: 0.85rem 0.95rem; border-bottom: 1px solid rgba(255,255,255,.05);
    }
    .ml-perf-menu-item:last-child{ border-bottom: none; }
    .ml-perf-menu-ico{
      width: 36px; height: 36px; border-radius: 12px; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      background: rgba(124,58,237,.16); font-size: 1rem;
    }
    .ml-perf-menu-text{ flex: 1; min-width: 0; }
    .ml-perf-menu-text b{ display: block; font-size: 0.82rem; font-weight: 800; }
    .ml-perf-menu-text span{ font-size: 0.68rem; color: #94a3b8; }
    .ml-perf-menu-chev{ color: #64748b; font-size: 0.9rem; }

    .ml-perf-logout{
      display: flex; align-items: center; gap: 0.65rem;
      padding: 0.85rem 0.95rem; border-radius: 18px;
      background: rgba(127,29,29,.18); border: 1px solid rgba(239,68,68,.22);
      color: #fca5a5; font-weight: 800; font-size: 0.85rem;
      margin-top: 0.35rem;
    }

    .ml-perf-empty{
      padding: 1rem; border-radius: 18px; text-align: center;
      background: rgba(15,23,42,.55); border: 1px dashed rgba(255,255,255,.1);
      color: #94a3b8; font-size: 0.82rem; margin-bottom: 0.5rem;
    }

    body:has(#ml-perfil-page) [class*="st-key-ml_perf_edit_btn"] .stButton > button,
    body:has(#ml-perfil-page) [class*="st-key-ml_perf_save"] .stButton > button,
    body:has(#ml-perfil-page) [class*="st-key-ml_perf_menu_"] .stButton > button{
      border-radius: 16px !important; font-weight: 800 !important;
      text-align: left !important; justify-content: flex-start !important;
      background: rgba(7,20,50,.55) !important;
      border: 1px solid rgba(255,255,255,.06) !important;
      min-height: 3.1rem !important; margin-bottom: 0.35rem !important;
    }
    body:has(#ml-perfil-page) [class*="st-key-ml_perf_logout_wrap"] .stButton > button{
      border-radius: 16px !important; font-weight: 800 !important;
      background: rgba(127,29,29,.28) !important;
      border: 1px solid rgba(239,68,68,.28) !important;
      color: #fca5a5 !important;
    }
    body:has(#ml-perfil-page) [class*="st-key-ml_perf_save"] .stButton > button[kind="primary"],
    body:has(#ml-perfil-page) [class*="st-key-ml_perf_edit_hdr"] .stButton > button{
      background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
      color: #fff !important; border: none !important;
    }
    body:has(#ml-perfil-page) .stTextInput > div > div > input,
    body:has(#ml-perfil-page) .stTextArea textarea,
    body:has(#ml-perfil-page) .stMultiSelect > div > div{
      border-radius: 18px !important;
      background: rgba(7,21,45,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    """


def _badge_for_roles(leadership: list[str]) -> tuple[str, str]:
    from app import ROLE_DESENVOLVEDOR, ROLE_LIDER, ROLE_ORG_MUSICAL, ROLE_ORG_VOCAL

    if ROLE_LIDER in leadership:
        return "Líder", "ml-perf-badge--lider"
    if ROLE_ORG_VOCAL in leadership or ROLE_ORG_MUSICAL in leadership:
        return "Coordenador", "ml-perf-badge--coord"
    if ROLE_DESENVOLVEDOR in leadership:
        return "Desenvolvedor", "ml-perf-badge--dev"
    return "Membro", "ml-perf-badge--membro"


def _profile_stats(
    mine: pd.DataFrame,
    louvores_df: pd.DataFrame,
    fav_ids: set[str],
    escala_stats,
) -> dict[str, object]:
    from playlist_ui import compute_playlist_stats

    pl = compute_playlist_stats(mine, louvores_df, fav_ids)
    return {
        "playlists": pl["playlists"],
        "musicas": pl["tracks"],
        "escalas": escala_stats.year_count,
        "ensaios": pl["hours"],
    }


def _gamification(stats: dict[str, object]) -> tuple[int, int, int]:
    xp = (
        int(stats["escalas"]) * 30
        + int(stats["musicas"]) * 8
        + int(stats["playlists"]) * 15
    )
    level = min(10, max(1, 1 + xp // 200))
    xp_in_level = xp % 1000
    return level, xp_in_level, 1000


def _recent_activities(
    email: str,
    mine: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
) -> list[dict]:
    from escala_member_stats import format_date_br, member_escala_occurrences

    items: list[dict] = []
    if not mine.empty:
        sorted_mine = mine.copy()
        sorted_mine["_sort"] = pd.to_datetime(sorted_mine["added_at"], errors="coerce")
        sorted_mine = sorted_mine.sort_values("_sort", ascending=False).head(4)
        for _, tr in sorted_mine.iterrows():
            title = str(tr.get("title", "")).strip() or "música"
            items.append(
                {
                    "ico": "🎵",
                    "ico_cls": "green",
                    "title": f'Adicionou "{title}"',
                    "sub": "Na sua playlist",
                    "time": _time_ago(tr.get("added_at")),
                    "sort": pd.to_datetime(tr.get("added_at"), errors="coerce"),
                }
            )

    occ = member_escala_occurrences(email, escalas_df, equipe_df)
    for d, _eid, ev in occ[:4]:
        items.append(
            {
                "ico": "📅",
                "ico_cls": "orange",
                "title": f"Escala: {ev}",
                "sub": format_date_br(d),
                "time": _time_ago(d),
                "sort": pd.Timestamp(d),
            }
        )

    items = [it for it in items if pd.notna(it.get("sort"))]
    items.sort(key=lambda x: x["sort"], reverse=True)
    return items[:6]


def _activity_html(item: dict) -> str:
    return (
        f'<div class="ml-perf-activity">'
        f'<div class="ml-perf-act-ico ml-perf-act-ico--{_esc(item["ico_cls"])}">'
        f'{item["ico"]}</div>'
        f'<div class="ml-perf-act-body">'
        f'<p class="ml-perf-act-title">{_esc(item["title"])}</p>'
        f'<div class="ml-perf-act-sub">{_esc(item["sub"])}</div>'
        f"</div>"
        f'<div class="ml-perf-act-time">{_esc(item["time"])}</div>'
        f"</div>"
    )


def _render_profile_header(
    *,
    name: str,
    email: str,
    photo_uri: str,
    leadership: list[str],
    musician: list[str],
    show_edit: bool,
) -> None:
    badge, badge_cls = _badge_for_roles(leadership)
    initial = (name.strip()[:1] or "?").upper()
    if photo_uri:
        av = (
            f'<img class="ml-perf-avatar" src="{_esc(photo_uri)}" alt="" />'
        )
    else:
        av = f'<div class="ml-perf-avatar-ph">{_esc(initial)}</div>'

    lead_txt = ", ".join(leadership) if leadership else ""
    mus_txt = ", ".join(musician) if musician else "Integrante"
    roles_html = ""
    if lead_txt:
        roles_html += f'<div class="ml-perf-roles">{_esc(lead_txt)}</div>'
    roles_html += f'<div class="ml-perf-roles">{_esc(mus_txt)}</div>'

    edit_btn = ""
    if show_edit:
        edit_btn = """
        <div style="flex-shrink:0;">
          <!-- botão Streamlit abaixo -->
        </div>
        """

    st.markdown(
        f"""
        <div class="ml-perf-header profile-header">
          <div class="ml-perf-avatar-wrap">
            {av}
            <div class="ml-perf-cam">📷</div>
          </div>
          <div class="ml-perf-body">
            <h2 class="ml-perf-name">{_esc(name)}</h2>
            <div class="ml-perf-badges">
              <span class="ml-perf-badge {badge_cls}">{_esc(badge)}</span>
              <span class="ml-perf-online">
                <span class="ml-perf-online-dot"></span> Online
              </span>
            </div>
            <p class="ml-perf-email">✉ {_esc(email)}</p>
            {roles_html}
          </div>
          {edit_btn}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if show_edit:
        c1, c2 = st.columns([3, 1])
        with c2:
            with st.container(key="ml_perf_edit_hdr"):
                if st.button("Editar", key="ml_perf_edit_open", use_container_width=True):
                    _set_view("edit")
                    st.rerun()


def _render_stats_grid(stats: dict[str, object]) -> None:
    items = [
        ("🎵", stats["playlists"], "Playlists"),
        ("🎤", stats["musicas"], "Músicas"),
        ("📅", stats["escalas"], "Escalas"),
        ("⏱", stats["ensaios"], "Ensaios"),
    ]
    parts = ['<div class="ml-perf-stat-grid">']
    for ico, val, lbl in items:
        parts.append(
            f'<div class="ml-perf-stat">'
            f'<div class="ml-perf-stat-ico">{ico}</div>'
            f"<h2>{_esc(val)}</h2><span>{_esc(lbl)}</span></div>"
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def _render_kit_voz(roles: str, bio: str) -> None:
    from voice_kit_links import vocal_nipe_from_roles, voice_kit_youtube_url

    nipe = vocal_nipe_from_roles(roles, bio=bio)
    if not nipe:
        return
    url = voice_kit_youtube_url(nipe)
    st.markdown(
        f"""
        <a href="{_esc(url)}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;color:inherit;">
          <div class="ml-perf-kit kitvoz-card">
            <span style="font-size:1.35rem;">🎤</span>
            <div>
              Kit Voz configurado
              <small>{_esc(nipe)}</small>
            </div>
          </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


def _render_level_card(stats: dict[str, object]) -> None:
    level, xp, xp_max = _gamification(stats)
    pct = min(100, max(8, int(xp / xp_max * 100)))
    st.markdown(
        f"""
        <div class="ml-perf-level">
          <div class="ml-perf-level-top">
            <div style="display:flex;gap:0.65rem;align-items:flex-start;">
              <span style="font-size:1.35rem;">🛡️</span>
              <div>
                <h3>Seu comprometimento inspira!</h3>
                <p>Você está entre os membros mais ativos do ministério.</p>
              </div>
            </div>
            <div class="ml-perf-level-num">Nível {level}</div>
          </div>
          <div class="ml-perf-level-bar">
            <div class="ml-perf-level-fill" style="width:{pct}%;"></div>
          </div>
          <div class="ml-perf-level-xp">{xp} / {xp_max} XP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_activities(activities: list[dict]) -> None:
    show_all = bool(st.session_state.get("ml_perf_show_all_act"))
    visible = activities if show_all else activities[:4]
    label = "Ocultar" if show_all else "Ver todas"
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            '<div class="ml-perf-section"><span>Atividades recentes</span></div>',
            unsafe_allow_html=True,
        )
    with c2:
        if st.button(label, key="ml_perf_toggle_act", use_container_width=True):
            st.session_state.ml_perf_show_all_act = not show_all
            st.rerun()
    if not visible:
        st.markdown(
            '<div class="ml-perf-empty">Nenhuma atividade recente ainda.</div>',
            unsafe_allow_html=True,
        )
        return
    for item in visible:
        st.markdown(_activity_html(item), unsafe_allow_html=True)


def _render_account_menu() -> None:
    st.markdown('<div class="ml-perf-section"><span>Minha conta</span></div>', unsafe_allow_html=True)
    for key, ico, title, sub in ACCOUNT_MENU:
        with st.container(key=f"ml_perf_menu_{key}"):
            if st.button(
                f"{ico}  {title}",
                key=f"ml_perf_menu_btn_{key}",
                help=sub,
                use_container_width=True,
            ):
                _set_view(key)
                st.rerun()


def _render_logout() -> None:
    with st.container(key="ml_perf_logout_wrap"):
        if st.button("🚪 Sair da conta", key="ml_perf_logout", use_container_width=True):
            from app import logout_user

            logout_user()
            st.rerun()


def _save_profile_photo_mobile(
    members_df: pd.DataFrame,
    idx,
    email: str,
    uploaded,
) -> bool:
    from app import MEMBERS_FILE, save_data, save_profile_photo, show_exception_error, show_form_error

    if uploaded is None:
        return False
    pending = {
        "name": uploaded.name or "photo.jpg",
        "bytes": uploaded.getvalue(),
    }
    blob_key = f"{email}:{pending.get('name')}:{len(pending.get('bytes') or b'')}"
    if st.session_state.get("_profile_photo_saved_key") == blob_key:
        return False
    try:
        filename = save_profile_photo(email, pending)
        members_df.at[idx, "profile_photo"] = str(filename).strip()
        if save_data(members_df, MEMBERS_FILE):
            st.session_state.user_profile_photo = filename
            st.session_state._profile_photo_saved_key = blob_key
            st.session_state.pop("_pending_profile_photo", None)
            st.success("Foto salva!")
            return True
    except ValueError as exc:
        show_form_error(str(exc))
    except Exception as exc:
        show_exception_error(
            exc,
            context="Salvar foto do perfil (mobile)",
            user_hint="Não foi possível salvar a foto. Tente outra imagem.",
        )
    return False


def _render_hub(
    row: pd.Series,
    idx,
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    photo_uri: str,
    leadership: list[str],
    musician: list[str],
    stats: dict[str, object],
    activities: list[dict],
) -> None:
    from app import member_display_name

    email = str(row["email"]).strip().lower()
    name = member_display_name(row)
    roles = str(row.get("roles", ""))
    bio = str(row.get("bio", ""))

    _render_profile_header(
        name=name,
        email=email,
        photo_uri=photo_uri,
        leadership=leadership,
        musician=musician,
        show_edit=True,
    )
    _render_stats_grid(stats)
    _render_kit_voz(roles, bio)
    _render_level_card(stats)
    _render_activities(activities)
    _render_account_menu()
    _render_logout()


def _render_edit(
    row: pd.Series,
    idx,
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    photo_uri: str,
    leadership: list[str],
    musician: list[str],
) -> None:
    from app import (
        ESCALAS_FILE,
        EQUIPE_FILE,
        MEMBERS_FILE,
        MUSICIAN_ROLES,
        merge_member_roles,
        save_data,
        set_user_session,
        show_form_error,
        sync_member_name_in_records,
    )

    from app import member_display_name

    email = str(row["email"]).strip().lower()
    name = member_display_name(row)

    if st.button("← Voltar", key="ml_perf_back_edit"):
        _set_view("hub")
        st.rerun()

    _render_profile_header(
        name=name,
        email=email,
        photo_uri=photo_uri,
        leadership=leadership,
        musician=musician,
        show_edit=False,
    )

    st.markdown('<div class="ml-perf-section"><span>Informações</span></div>', unsafe_allow_html=True)

    initial = (name.strip()[:1] or "?").upper()
    if photo_uri:
        st.image(photo_uri, width=120)
    else:
        st.markdown(f'<div class="ml-perf-avatar-ph" style="width:90px;height:90px;">{_esc(initial)}</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Enviar foto (JPG, PNG ou WebP)",
        type=["jpg", "jpeg", "png", "webp"],
        key="ml_perf_photo_upload",
    )
    if uploaded is not None:
        st.session_state["_pending_profile_photo"] = {
            "name": uploaded.name or "photo.jpg",
            "bytes": uploaded.getvalue(),
        }
        if _save_profile_photo_mobile(members_df, idx, email, uploaded):
            st.rerun()

    with st.form(key="ml_perf_data_form"):
        first_name = st.text_input("Nome", value=str(row.get("first_name", "")))
        last_name = st.text_input("Sobrenome", value=str(row.get("last_name", "")))
        st.text_input("Email", value=email, disabled=True)
        phone = st.text_input("Telefone / WhatsApp", value=str(row.get("phone", "")))
        bio = st.text_area(
            "Sobre você (opcional)",
            value=str(row.get("bio", "")),
            height=90,
            placeholder="Ex.: ministro há 3 anos, vocal barítono...",
        )
        if leadership:
            st.caption("Funções de liderança: " + ", ".join(leadership))
        role_label = (
            "Função(ões) no ministério (opcional para líderes)"
            if leadership
            else "Função(ões) no ministério"
        )
        new_musician = st.multiselect(
            role_label,
            MUSICIAN_ROLES,
            default=[r for r in musician if r in MUSICIAN_ROLES],
        )
        salvar = st.form_submit_button("💾 Salvar perfil", type="primary", use_container_width=True)

    if salvar:
        if not first_name.strip() or not last_name.strip():
            show_form_error("Nome e sobrenome são obrigatórios.")
        elif not leadership and not new_musician:
            show_form_error("Selecione pelo menos uma função (música ou técnico de som).")
        else:
            fn = first_name.strip().title()
            ln = last_name.strip().title()
            members_df.at[idx, "first_name"] = fn
            members_df.at[idx, "last_name"] = ln
            members_df.at[idx, "phone"] = phone.strip()
            members_df.at[idx, "bio"] = bio.strip()
            members_df.at[idx, "roles"] = merge_member_roles(leadership, new_musician)
            save_data(members_df, MEMBERS_FILE)

            full_name = f"{fn} {ln}".strip()
            escalas_df, equipe_df = sync_member_name_in_records(
                email, full_name, escalas_df, equipe_df
            )
            save_data(escalas_df, ESCALAS_FILE)
            save_data(equipe_df, EQUIPE_FILE)

            updated = members_df.loc[idx]
            set_user_session(updated)
            st.success("Perfil atualizado!")
            _set_view("hub")
            st.rerun()


def _render_password(row: pd.Series, idx, members_df: pd.DataFrame) -> None:
    from app import MEMBERS_FILE, hash_password, save_data, show_form_error

    if st.button("← Voltar", key="ml_perf_back_pwd"):
        _set_view("hub")
        st.rerun()

    st.markdown('<div class="ml-perf-section"><span>🔒 Alterar senha</span></div>', unsafe_allow_html=True)

    with st.form(key="ml_perf_password_form"):
        senha_atual = st.text_input("Senha atual", type="password")
        senha_nova = st.text_input("Nova senha", type="password")
        senha_conf = st.text_input("Confirmar nova senha", type="password")
        trocar = st.form_submit_button("Atualizar senha", use_container_width=True)

    if trocar:
        if not senha_atual or not senha_nova:
            show_form_error("Preencha a senha atual e a nova senha.")
        elif len(senha_nova) < 6:
            show_form_error("A nova senha deve ter pelo menos 6 caracteres.")
        elif senha_nova != senha_conf:
            show_form_error("A confirmação não coincide com a nova senha.")
        elif hash_password(senha_atual) != str(row.get("password_hash", "")):
            show_form_error("Senha atual incorreta.")
        else:
            members_df.at[idx, "password_hash"] = hash_password(senha_nova)
            save_data(members_df, MEMBERS_FILE)
            st.success("Senha alterada com sucesso!")
            _set_view("hub")
            st.rerun()


def _render_help() -> None:
    if st.button("← Voltar", key="ml_perf_back_help"):
        _set_view("hub")
        st.rerun()
    st.markdown('<div class="ml-perf-section"><span>💬 Ajuda e suporte</span></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="ml-perf-empty" style="text-align:left;">
          <p><b>Dúvidas frequentes</b></p>
          <p>• Atualize sua função vocal no perfil para liberar o Kit Voz.</p>
          <p>• Use a playlist pessoal para treinar com YouTube e cifra.</p>
          <p>• Escalas e trocas ficam no menu Escalas.</p>
          <p style="margin-top:0.75rem;"><b>Fale com a liderança</b></p>
          <p>Entre em contato com o organizador vocal ou musical do ministério.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_prefs() -> None:
    if st.button("← Voltar", key="ml_perf_back_prefs"):
        _set_view("hub")
        st.rerun()
    st.markdown('<div class="ml-perf-section"><span>⚙️ Preferências</span></div>', unsafe_allow_html=True)
    st.info(
        "Notificações e tema seguem as configurações do app. "
        "Em breve você poderá personalizar alertas por tipo de aviso."
    )


def render_mobile_perfil_page(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
) -> None:
    from app import (
        PLAYLIST_COLUMNS,
        PLAYLIST_FILE,
        get_current_member_row,
        load_data,
        playlist_for_user,
        prepare_members,
        prepare_playlist,
        profile_photo_to_data_uri,
        split_member_roles,
        sync_user_profile_photo_field,
    )
    from escala_member_stats import member_escala_stats
    from playlist_ui import get_favorite_ids

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_perfil_css()}</style>", unsafe_allow_html=True)
    st.markdown('<div id="ml-perfil-page" class="ml-page">', unsafe_allow_html=True)

    members_df = prepare_members(members_df)
    members_df = sync_user_profile_photo_field(members_df)
    idx, row = get_current_member_row(members_df)
    if row is None:
        st.error("Não foi possível carregar o perfil.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    email = str(row["email"]).strip().lower()
    photo_uri = profile_photo_to_data_uri(
        email, str(row.get("profile_photo", "")).strip()
    )
    leadership, musician = split_member_roles(row.get("roles", ""))

    playlist_df = prepare_playlist(load_data(PLAYLIST_FILE, PLAYLIST_COLUMNS))
    mine = playlist_for_user(playlist_df, email)
    fav_ids = get_favorite_ids()
    if not mine.empty:
        fav_ids = fav_ids & set(mine["id"].astype(str))
        st.session_state["pl_favorite_ids"] = fav_ids

    louvores_df = pd.DataFrame()
    try:
        from app import LOUVORES_FILE, prepare_louvores_with_meta

        louvores_df = prepare_louvores_with_meta(
            load_data(
                LOUVORES_FILE,
                (
                    "title",
                    "artist",
                    "key",
                    "youtube_url",
                    "cifra_url",
                    "ritmo",
                    "letter",
                    "source",
                    "temas",
                    "ref_biblica",
                    "duracao_min",
                ),
            )
        )
    except Exception:
        pass

    escala_stats = member_escala_stats(email, escalas_df, equipe_df, ref=date.today())
    stats = _profile_stats(mine, louvores_df, fav_ids, escala_stats)
    activities = _recent_activities(email, mine, escalas_df, equipe_df)

    view = _view()
    if view == "edit":
        _render_edit(
            row, idx, members_df, escalas_df, equipe_df,
            photo_uri=photo_uri, leadership=leadership, musician=musician,
        )
    elif view == "password":
        _render_password(row, idx, members_df)
    elif view == "help":
        _render_help()
    elif view == "prefs":
        _render_prefs()
    else:
        _render_hub(
            row, idx, members_df, escalas_df, equipe_df,
            photo_uri=photo_uri, leadership=leadership, musician=musician,
            stats=stats, activities=activities,
        )

    st.markdown("</div>", unsafe_allow_html=True)
