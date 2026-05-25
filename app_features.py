"""Funcionalidades estendidas: feed, escalas, notificações, repertório."""

from __future__ import annotations  # compatível com Python 3.9+ no Streamlit Cloud

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


def inject_hidden_sidebar_script(html_fragment: str) -> None:
    """HTML/JS na sidebar — não ocupa colunas na área principal (layout desktop)."""
    import streamlit as st

    body = html_fragment.strip()
    if not body:
        return
    with st.sidebar:
        try:
            st.html(body, unsafe_allow_javascript=True)
        except Exception:
            import streamlit.components.v1 as components

            wrapped = (
                '<div aria-hidden="true" style="position:fixed;left:0;top:0;'
                'width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none;">'
                f"{body}</div>"
            )
            components.html(wrapped, height=0, scrolling=False)


def count_pending_sugestoes(sugestoes_df: pd.DataFrame) -> int:
    """Sugestões novas (pendente) para a liderança receber."""
    if sugestoes_df.empty:
        return 0
    status = sugestoes_df["status"].astype(str).str.strip().str.lower()
    status = status.replace(
        {"em análise": "em_analise", "em_analise": "em_analise", "aprovado": "aprovada"}
    )
    return int((status == "pendente").sum())


def inject_app_notification_badges(
    chat_unread: int,
    sugestoes_pending: int = 0,
    swap_pending: int = 0,
) -> None:
    """Badges estilo WhatsApp no emoji do menu + bolinha lateral vermelha."""
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

    inject_hidden_sidebar_script(
        f"""
        <div id="app-bell-notif" style="display:{show_bell}" title="Novidades">
          🔔<span class="nav-wa-badge">{html.escape(total_label)}</span>
        </div>
        <script>
        (function () {{
          var badges = {badges_json};
          var doc = window.parent.document;

          function badgeForLabel(raw) {{
            if (!raw) return 0;
            var keys = Object.keys(badges).sort(function (a, b) {{
              return b.length - a.length;
            }});
            for (var i = 0; i < keys.length; i++) {{
              var menuName = keys[i];
              if (menuName === "Chat" && raw.toLowerCase().indexOf("ensaio") >= 0) continue;
              if (menuName === "Escalas" && raw.indexOf("Gerenciar") >= 0) continue;
              if (raw.indexOf(menuName) >= 0) return badges[menuName];
            }}
            return 0;
          }}

          function setWaBadge(host, n) {{
            host.querySelectorAll(".nav-wa-badge").forEach(function (b) {{ b.remove(); }});
            if (n <= 0) return;
            var badge = doc.createElement("span");
            badge.className = "nav-wa-badge";
            badge.textContent = n > 99 ? "99+" : String(n);
            badge.setAttribute("aria-label", n + " novidades");
            host.style.position = "relative";
            host.appendChild(badge);
          }}

          function attachSidebar() {{
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            sidebar.querySelectorAll('[class*="st-key-ig_nav_"]').forEach(function (wrap) {{
              var raw = (wrap.innerText || "").trim();
              var n = badgeForLabel(raw);
              setWaBadge(wrap, n);
            }});
            sidebar.querySelectorAll('[data-testid="stRadio"] label').forEach(function (el) {{
              var raw = (el.innerText || "").trim();
              setWaBadge(el, badgeForLabel(raw));
            }});
          }}

          function attachQuickNav() {{
            doc.querySelectorAll(".quick-nav-btn").forEach(function (wrap) {{
              var raw = (wrap.innerText || "").trim();
              var n = badgeForLabel(raw);
              setWaBadge(wrap, n);
            }});
          }}

          function attach() {{
            attachSidebar();
            attachQuickNav();
          }}
          attach();
          setTimeout(attach, 280);
          setTimeout(attach, 900);
          setTimeout(attach, 1800);
          if (!window.__igbjBadgePoll) {{
            window.__igbjBadgePoll = setInterval(attach, 3000);
          }}
        }})();
        </script>
        """
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
        '<p class="planner-title"><span class="planner-icon-gold">📅</span>Painel do mês</p>'
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
