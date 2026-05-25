"""Funcionalidades estendidas: feed, escalas, notificações, repertório."""

from __future__ import annotations

import html
import json
import re
from datetime import date

import pandas as pd

from escala_member_stats import format_date_br, member_escala_occurrences, member_escala_stats
from louvor_meta import (
    parse_duracao_min,
    suggest_biblical_refs,
    themes_from_csv,
)


def count_pending_sugestoes(sugestoes_df: pd.DataFrame) -> int:
    if sugestoes_df.empty:
        return 0
    return int(
        (sugestoes_df["status"].astype(str).str.lower() == "pendente").sum()
    )


def inject_app_notification_badges(
    chat_unread: int,
    sugestoes_pending: int = 0,
    swap_pending: int = 0,
) -> None:
    """Badge vermelho flutuante sobre o ícone do menu (não ao lado do texto)."""
    from app import inject_page_html

    badges: dict[str, int] = {}
    if chat_unread > 0:
        badges["Chat"] = min(99, int(chat_unread))
    if sugestoes_pending > 0:
        badges["Sugestão de louvor"] = min(99, int(sugestoes_pending))
    if swap_pending > 0:
        badges["Escalas"] = min(99, int(swap_pending))

    total = sum(badges.values())
    show_bell = "flex" if total > 0 else "none"
    total_label = "99+" if total > 99 else str(total)
    badges_json = json.dumps(badges, ensure_ascii=False)

    inject_page_html(
        f"""
        <style>
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
            position: relative !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.45rem !important;
            padding-left: 0.15rem !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label .nav-icon-badge {{
            position: absolute;
            left: 0.95rem;
            top: -0.05rem;
            min-width: 1.05rem;
            height: 1.05rem;
            padding: 0 0.28rem;
            border-radius: 999px;
            background: #ef4444 !important;
            color: #fff !important;
            font-size: 0.58rem;
            font-weight: 800;
            display: none;
            align-items: center;
            justify-content: center;
            line-height: 1;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.65);
            z-index: 12;
            pointer-events: none;
            border: 1.5px solid rgba(18, 10, 30, 0.9);
        }}
        #app-bell-notif {{
            position: fixed; top: 0.65rem; right: 0.75rem; z-index: 9999;
            width: 2.25rem; height: 2.25rem; border-radius: 50%;
            background: rgba(30,20,50,.92); border: 1px solid rgba(251,191,36,.5);
            display: {show_bell}; align-items: center; justify-content: center;
            font-size: 1.15rem; box-shadow: 0 4px 16px rgba(0,0,0,.35);
            pointer-events: none;
        }}
        #app-bell-notif span {{
            position: absolute; top: -2px; right: -2px;
            min-width: 1rem; height: 1rem; border-radius: 999px;
            background: #ef4444; color: #fff; font-size: 0.58rem;
            font-weight: 800; display: flex; align-items: center; justify-content: center;
        }}
        </style>
        <div id="app-bell-notif" title="Novidades">🔔<span>{total_label}</span></div>
        <script>
        (function () {{
          var badges = {badges_json};
          var doc = window.parent.document;
          function matchMenu(raw, menuName) {{
            if (!raw || raw.indexOf(menuName) < 0) return false;
            if (menuName === "Chat" && raw.toLowerCase().indexOf("ensaio") >= 0) return false;
            if (menuName === "Escalas" && raw.indexOf("Gerenciar") >= 0) return false;
            return true;
          }}
          function attach() {{
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            sidebar.querySelectorAll('[data-testid="stRadio"] label').forEach(function (el) {{
              el.querySelectorAll('.nav-icon-badge').forEach(function (b) {{ b.remove(); }});
              var raw = (el.innerText || "").trim();
              Object.keys(badges).forEach(function (menuName) {{
                if (!matchMenu(raw, menuName)) return;
                var n = badges[menuName];
                var badge = doc.createElement('span');
                badge.className = 'nav-icon-badge';
                badge.textContent = n > 99 ? '99+' : String(n);
                badge.style.display = 'flex';
                el.appendChild(badge);
              }});
            }});
            doc.querySelectorAll('.quick-nav-btn').forEach(function (wrap) {{
              wrap.querySelectorAll('.nav-icon-badge').forEach(function (b) {{ b.remove(); }});
              var raw = (wrap.innerText || "").trim();
              Object.keys(badges).forEach(function (menuName) {{
                if (!matchMenu(raw, menuName)) return;
                var n = badges[menuName];
                var badge = doc.createElement('span');
                badge.className = 'nav-icon-badge';
                badge.textContent = n > 99 ? '99+' : String(n);
                badge.style.display = 'flex';
                wrap.style.position = 'relative';
                wrap.appendChild(badge);
              }});
            }});
          }}
          attach();
          setTimeout(attach, 300);
          setTimeout(attach, 900);
        }})();
        </script>
        """,
        height=0,
    )


def render_dashboard_section_start(
    title: str,
    icon: str,
    accent: str,
    subtitle: str = "",
) -> None:
    """Abre card de seção do Dashboard (título + conteúdo abaixo)."""
    import streamlit as st

    sub_html = (
        f'<p class="dash-section-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    )
    st.markdown(
        f'<div class="dash-section">'
        f'<div class="dash-section-header" style="--dash-accent:{html.escape(accent)}">'
        f'<span class="dash-section-icon">{icon}</span>'
        f"<div><h4>{html.escape(title)}</h4>{sub_html}</div>"
        f"</div>"
        f'<div class="dash-section-content">',
        unsafe_allow_html=True,
    )


def render_dashboard_section_end() -> None:
    import streamlit as st

    st.markdown("</div></div>", unsafe_allow_html=True)


def quick_nav_css_class(menu_name: str) -> str:
    known = {
        "Escalas": "escalas",
        "Chat": "chat",
        "Eventos": "eventos",
        "Playlist": "playlist",
        "Feed": "feed",
        "Repertório": "repertorio",
        "Perfil": "perfil",
    }
    slug = known.get(menu_name) or re.sub(r"[^a-z0-9]+", "-", menu_name.lower()).strip("-")
    return f"quick-nav--{slug or 'item'}"


def user_future_escalas(
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    from_date: date | None = None,
) -> list[dict]:
    from_date = from_date or date.today()
    occ = member_escala_occurrences(email, escalas_df, equipe_df)
    out = []
    for culto_d, eid, ev in occ:
        if culto_d >= from_date:
            out.append({"date": culto_d, "escala_id": eid, "event": ev})
    return out


def render_dashboard_future_escalas(
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
):
    import streamlit as st

    futuras = user_future_escalas(email, escalas_df, equipe_df)
    if not futuras:
        return
    render_dashboard_section_start(
        "Suas próximas escalas",
        "📆",
        "#60a5fa",
    )
    cols = st.columns(min(4, len(futuras[:8])))
    for i, item in enumerate(futuras[:8]):
        d = item["date"].strftime("%d/%m/%Y")
        ev = str(item["event"])
        eid = str(item["escala_id"])
        with cols[i % len(cols)]:
            st.markdown('<div class="quick-nav-btn quick-nav--escalas">', unsafe_allow_html=True)
            if st.button(
                f"📅 {d}\n{ev}",
                key=f"dash_fe_{eid}",
                use_container_width=True,
            ):
                st.session_state.app_menu = "Escalas"
                st.session_state.focus_escala_id = eid
                try:
                    culto = item["date"]
                    today = date.today()
                    st.session_state.week_offset = (culto - today).days // 7
                except Exception:
                    pass
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    if len(futuras) > 8:
        st.caption(f"Mais {len(futuras) - 8} culto(s) — veja em **Escalas**.")
    render_dashboard_section_end()


def render_escala_planner_panel(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    culto_ref: date,
):
    """Quem ainda não foi escalado no mês + última escala."""
    import html as html_mod
    import streamlit as st

    from app import members_visible_to_group, member_display_name

    st.markdown(
        '<div class="planner-panel-card">'
        '<p class="planner-title">📋 Painel do mês</p>'
        '<p class="planner-sub">Última escala e quem ainda não entrou neste mês.</p></div>',
        unsafe_allow_html=True,
    )
    visible = members_visible_to_group(members_df)
    linhas = []
    for _, row in visible.sort_values(by=["first_name", "last_name"]).iterrows():
        em = str(row["email"]).strip().lower()
        stats = member_escala_stats(em, escalas_df, equipe_df, ref=culto_ref)
        ultima = format_date_br(stats.last_date)
        no_mes = stats.month_count
        linhas.append((no_mes, ultima, member_display_name(row), em))
    linhas.sort(key=lambda x: (x[0], x[1]))
    for no_mes, ultima, nome, _ in linhas[:25]:
        badge = (
            '<span class="planner-badge-ok">no mês</span>'
            if no_mes
            else '<span class="planner-badge-warn">sem escala no mês</span>'
        )
        st.markdown(
            f'<div class="planner-row"><span class="planner-name">{html_mod.escape(nome)}</span>'
            f'{badge}<span class="planner-date">última: {html_mod.escape(ultima)}</span></div>',
            unsafe_allow_html=True,
        )


def member_escala_option_label(
    label: str,
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    culto_ref: date,
) -> str:
    stats = member_escala_stats(email, escalas_df, equipe_df, ref=culto_ref)
    return f"{label} · última: {format_date_br(stats.last_date)} · mês: {stats.month_count}"


def lookup_louvor_meta(louvores_df: pd.DataFrame, title: str, artist: str = "") -> dict:
    if louvores_df.empty:
        return {}
    t = str(title).strip().lower()
    for _, r in louvores_df.iterrows():
        if str(r.get("title", "")).strip().lower() == t:
            return r.to_dict()
    return {}


def programa_duracao_total(programa_df: pd.DataFrame, escala_id: str, louvores_df: pd.DataFrame) -> float:
    from app import programa_por_escala

    prog = programa_por_escala(programa_df, escala_id)
    total = 0.0
    for _, item in prog.iterrows():
        meta = lookup_louvor_meta(
            louvores_df, str(item.get("louvor_title", "")), str(item.get("artist", ""))
        )
        total += parse_duracao_min(meta.get("duracao_min", ""))
    return total


def save_feed_image_file(uploaded, data_dir, feed_images_dir) -> str:
    from chat_media import save_image_upload

    feed_images_dir.mkdir(parents=True, exist_ok=True)
    rel = save_image_upload(
        uploaded, feed_images_dir, prefix="feed", data_dir=data_dir
    )
    return rel


def feed_image_display_path(image_url: str, data_dir) -> str | None:
    raw = str(image_url).strip()
    if raw.startswith("http"):
        return raw
    if not raw:
        return None
    p = data_dir / raw.replace("\\", "/")
    return str(p) if p.exists() else None


def render_escala_suggestions_panel(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
):
    """Sugestões de equipe e louvores (líderes/organizadores) — não substitui decisão humana."""
    import html as html_mod
    import streamlit as st

    from catalog_sanitize import format_louvor_display
    from escala_suggester import (
        HorizonKind,
        generate_escala_suggestions,
        horizon_label,
        louvores_count_for_culto,
    )

    from app import members_visible_to_group

    st.markdown(
        '<p class="music-panel-title">💡 Sugestões de escala</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Sugestão com base no **histórico** de escalas e no repertório. "
        "Evita repetir o mesmo integrante em **cultos seguidos** na mesma função (vocal ou instrumento); "
        "quem canta e toca pode aparecer em cultos consecutivos em funções diferentes. "
        "No mês, a mesma pessoa pode voltar se houver **intercalação**. "
        "Santa Ceia (1º domingo do mês): **6 louvores**; demais cultos: **5**."
    )

    horizon_map = {
        "Próxima escala (semana)": "semana",
        "Mês inteiro": "mes",
        "2 meses": "2_meses",
        "Trimestre": "trimestre",
    }
    col_h, col_g = st.columns([2, 1])
    with col_h:
        horizon_ui = st.radio(
            "Período",
            list(horizon_map.keys()),
            horizontal=True,
            key="sug_esc_horizon",
        )
    with col_g:
        gerar = st.button("🔄 Gerar sugestões", type="primary", use_container_width=True)

    horizon: HorizonKind = horizon_map[horizon_ui]  # type: ignore[assignment]

    if gerar or st.session_state.get("_sug_esc_last_horizon") != horizon:
        visible = members_visible_to_group(members_df)
        st.session_state["_sug_esc_plan"] = generate_escala_suggestions(
            horizon,
            visible,
            escalas_df,
            equipe_df,
            programa_df,
            louvores_df,
        )
        st.session_state["_sug_esc_last_horizon"] = horizon

    plan: list = st.session_state.get("_sug_esc_plan", [])
    if not plan:
        st.info("Toque em **Gerar sugestões** para montar o plano do período escolhido.")
        return

    st.success(
        f"**{horizon_label(horizon)}** — {len(plan)} culto(s) sugerido(s). "
        "Revise e use **Criar escala** só nas datas que ainda não têm cadastro."
    )

    for i, sug in enumerate(plan):
        d_fmt = sug.culto_date.strftime("%d/%m/%Y")
        n_lv = louvores_count_for_culto(sug.culto_date)
        badge = " · Santa Ceia (6 louvores)" if sug.is_santa_ceia else f" · {n_lv} louvores"
        tit = f"📅 {d_fmt} — {sug.event_name}{badge}"
        if sug.existing_escala_id:
            tit += " · ✅ já cadastrada"

        with st.expander(tit, expanded=(i == 0 and horizon == "semana")):
            if sug.notes:
                for note in sug.notes:
                    st.caption(f"ℹ️ {note}")

            st.markdown(
                f"**{sug.ministrador.funcao}:** "
                f"{html_mod.escape(sug.ministrador.name)}"
            )
            if sug.equipe:
                st.markdown("**Equipe sugerida**")
                for slot in sug.equipe:
                    st.markdown(
                        f"- {html_mod.escape(slot.name)} — "
                        f"{html_mod.escape(slot.funcao)}"
                    )

            st.markdown("**Louvores sugeridos**")
            for lv in sug.louvores:
                titulo = format_louvor_display(lv.title, lv.artist)
                tom = f" · tom {lv.key}" if lv.key else ""
                st.markdown(
                    f"{lv.ordem}. **{html_mod.escape(lv.parte)}** — "
                    f"{html_mod.escape(titulo)}{html_mod.escape(tom)}"
                )

            if sug.existing_escala_id:
                st.caption("Esta data já tem escala — edite em **Montar / editar escala**.")
            else:
                if st.button(
                    "➕ Criar escala nesta data",
                    key=f"sug_apply_{sug.culto_date.isoformat()}",
                    use_container_width=True,
                ):
                    st.session_state["_sug_esc_apply_one"] = sug.culto_date.isoformat()
                    st.rerun()

    apply_iso = st.session_state.pop("_sug_esc_apply_one", None)
    if apply_iso:
        from escala_suggester import culto_suggestion_payload

        from app import (
            EQUIPE_FILE,
            ESCALAS_FILE,
            PROGRAMA_FILE,
            PROGRAMA_COLUMNS,
            get_escalas_bundle,
            hydrate_escala_sequencia_content,
            load_data,
            new_id,
            prepare_equipe,
            prepare_programa,
            save_data,
        )

        target = next((s for s in plan if s.culto_date.isoformat() == apply_iso), None)
        if target and not target.existing_escala_id:
            escala_id = new_id()
            payload = culto_suggestion_payload(target, escala_id)
            escalas_df, programa_df, equipe_df, _ = get_escalas_bundle()
            escalas_df = pd.concat(
                [escalas_df, pd.DataFrame([payload["escala"]])], ignore_index=True
            )
            save_data(escalas_df, ESCALAS_FILE)

            eq_rows = []
            for row in payload["equipe"]:
                eq_rows.append({"id": new_id(), **row})
            if eq_rows:
                equipe_df = pd.concat(
                    [equipe_df, pd.DataFrame(eq_rows)], ignore_index=True
                )
                save_data(prepare_equipe(equipe_df), EQUIPE_FILE)

            prog_rows = []
            for row in payload["programa"]:
                prog_rows.append(
                    {
                        "id": new_id(),
                        "youtube_url": "",
                        "cifra_url": "",
                        "notes": "",
                        **row,
                    }
                )
            if prog_rows:
                programa_df = load_data(PROGRAMA_FILE, PROGRAMA_COLUMNS)
                programa_df = prepare_programa(programa_df)
                programa_df = pd.concat(
                    [programa_df, pd.DataFrame(prog_rows)], ignore_index=True
                )
                save_data(programa_df, PROGRAMA_FILE)
                hydrate_escala_sequencia_content(escala_id, programa_df, louvores_df)

            st.session_state["editor_escala_sel"] = None
            st.success(
                f"Escala criada para {target.culto_date.strftime('%d/%m/%Y')}. "
                "Ajuste ensaio e detalhes em **Montar / editar escala**."
            )
            st.rerun()
