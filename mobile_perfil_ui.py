"""Mobile Lab — Perfil premium."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from mobile_lab_ui import inject_mobile_lab_theme


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def mobile_perfil_css() -> str:
    return r"""
    body:has(#ml-perfil-page) [data-testid="stAppViewContainer"] .main .block-container{
      padding-top: 0.35rem !important;
      padding-bottom: 7.5rem !important;
    }
    body:has(#ml-perfil-page) .music-panel-title{ display: none !important; }
    body:has(#ml-perfil-page) [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
      flex: 1 1 100% !important;
      width: 100% !important;
      max-width: 100% !important;
      min-width: 0 !important;
    }
    body:has(#ml-perfil-page) .profile-card{
      border-radius: 24px !important;
      padding: 1rem !important;
      background: rgba(15,23,42,.72) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
      margin-bottom: 1rem !important;
    }
    body:has(#ml-perfil-page) .stTextInput > div > div > input,
    body:has(#ml-perfil-page) .stTextArea textarea,
    body:has(#ml-perfil-page) .stMultiSelect > div > div{
      border-radius: 18px !important;
      background: rgba(30,30,30,.92) !important;
      border: 1px solid rgba(255,255,255,.08) !important;
    }
    body:has(#ml-perfil-page) .stButton > button[kind="primary"]{
      border-radius: 20px !important;
      font-weight: 800 !important;
      background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    }
    """


def _render_header(*, name: str, email: str, photo_uri: str, roles_txt: str) -> None:
    initial = (name.strip()[:1] or "?").upper()
    if photo_uri:
        av = f'<img src="{_esc(photo_uri)}" alt="" style="width:72px;height:72px;border-radius:22px;object-fit:cover;border:2px solid rgba(139,92,246,.45);" />'
    else:
        av = (
            f'<div style="width:72px;height:72px;border-radius:22px;display:flex;align-items:center;'
            f'justify-content:center;font-size:1.6rem;font-weight:900;background:rgba(139,92,246,.18);'
            f'border:2px solid rgba(139,92,246,.35);">{_esc(initial)}</div>'
        )
    st.markdown(
        f"""
        <div id="ml-perfil-page" class="ml-page">
          <div class="ml-rep-header-card" style="margin-bottom:0.85rem;">
            <div style="display:flex;gap:14px;align-items:center;">
              {av}
              <div>
                <h1 class="ml-rep-header-title" style="font-size:1.35rem;margin:0;">{_esc(name)}</h1>
                <p class="ml-rep-header-sub" style="margin-top:4px;">{_esc(email)}</p>
                <p class="ml-rep-header-sub" style="margin-top:6px;font-size:0.82rem;">{_esc(roles_txt)}</p>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mobile_perfil_page(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
) -> None:
    from app import (
        get_current_member_row,
        member_display_name,
        prepare_members,
        profile_photo_to_data_uri,
        show_user_profile,
        split_member_roles,
    )

    inject_mobile_lab_theme()
    st.markdown(f"<style>{mobile_perfil_css()}</style>", unsafe_allow_html=True)

    members_df = prepare_members(members_df)
    _, row = get_current_member_row(members_df)
    if row is None:
        st.error("Não foi possível carregar o perfil.")
        return

    email = str(row["email"]).strip().lower()
    photo_uri = profile_photo_to_data_uri(
        email, str(row.get("profile_photo", "")).strip()
    )
    leadership, musician = split_member_roles(row.get("roles", ""))
    roles_parts = leadership + musician
    roles_txt = ", ".join(roles_parts) if roles_parts else "Integrante"
    name = member_display_name(row)

    _render_header(name=name, email=email, photo_uri=photo_uri, roles_txt=roles_txt)
    st.caption("Atualize foto, dados e senha. O grupo verá suas alterações nas escalas.")

    from mobile_ui import mobile_stack_open, mobile_stack_close

    mobile_stack_open()
    show_user_profile(members_df, escalas_df, equipe_df)
    mobile_stack_close()
