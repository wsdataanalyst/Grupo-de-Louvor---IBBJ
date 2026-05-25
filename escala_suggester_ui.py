"""UI Streamlit para sugestões de escala (import lazy de app para evitar ciclo)."""

from __future__ import annotations

import html as html_mod

import pandas as pd
import streamlit as st

from catalog_sanitize import format_louvor_display
from escala_suggester import (
    HorizonKind,
    culto_suggestion_payload,
    generate_escala_suggestions,
    horizon_label,
    louvores_count_for_culto,
)


def render_escala_suggestions_panel(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
):
    """Sugestões de equipe e louvores (líderes/organizadores) — não substitui decisão humana."""
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
