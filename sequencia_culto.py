"""Sequência do Culto: letras com marcações e cifras por trecho."""

from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Any

import pandas as pd

from chord_transpose import key_to_semitone, transpose_cifra_text

# Tipos de marcação vocal
TIPOS_VOCAL = (
    "—",
    "Solo",
    "Harmonia de voz",
    "Uníssono",
    "Todos juntos",
    "Entrada gradual",
    "Ministrador fala",
    "Instrumental / sem vocal",
)

TIPO_VOCAL_CORE = ("—", "Solo", "Harmonia de voz", "Uníssono", "Todos juntos")

TIPO_CORE_COLORS = {
    "Solo": "#f472b6",
    "Harmonia de voz": "#a78bfa",
    "Uníssono": "#4ade80",
    "Todos juntos": "#34d399",
    "Entrada gradual": "#38bdf8",
    "Ministrador fala": "#fb923c",
    "Instrumental / sem vocal": "#94a3b8",
}

# Tipos de marcação banda
TIPOS_BANDA = (
    "—",
    "Solo instrumento",
    "Entrada banda",
    "Harmonia instrumental",
    "Todos (banda)",
    "Dinâmica / volume",
    "Silêncio",
)

PROGRAMA_SEQUENCIA_COLUMNS = (
    "programa_id",
    "lyrics_text",
    "lyrics_markup",
    "cifra_text",
    "tom_programa",
    "capo",
    "cifra_markup",
    "updated_at",
)


def _empty_sequencia_df() -> pd.DataFrame:
    return pd.DataFrame(columns=list(PROGRAMA_SEQUENCIA_COLUMNS))


def parse_markup(raw: str) -> list[dict[str, Any]]:
    if not str(raw).strip():
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "trechos" in data:
            return list(data["trechos"])
    except json.JSONDecodeError:
        pass
    return []


def markup_to_json(trechos: list[dict]) -> str:
    return json.dumps({"trechos": trechos}, ensure_ascii=False)


def split_lyrics_paragraphs(text: str) -> list[str]:
    raw = str(text or "").replace("\r\n", "\n").strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.split("\n\n") if p.strip()]
    if not parts and raw:
        parts = [ln.strip() for ln in raw.split("\n") if ln.strip()]
    return parts


def join_paragraphs(parts: list[str]) -> str:
    return "\n\n".join(p.strip() for p in parts if p.strip())


def _tipo_label(tipo: str, integrantes: list[str], nota: str) -> str:
    tipo = str(tipo or "").strip()
    if tipo in ("—", ""):
        return ""
    names = ", ".join(integrantes) if integrantes else ""
    extra = f" — {nota}" if nota else ""
    if tipo == "Solo" and names:
        return f"🎤 Solo: {names}{extra}"
    if tipo == "Harmonia de voz":
        return f"🎵 Harmonia de voz{f': {names}' if names else ''}{extra}"
    if tipo == "Uníssono":
        return "👥 Uníssono"
    if tipo == "Todos juntos":
        return "👥 Todos juntos"
    if tipo == "Solo instrumento" and names:
        return f"🎸 Solo: {names}{extra}"
    if tipo == "Entrada banda":
        return f"🎹 Entrada banda{f' ({names})' if names else ''}{extra}"
    return f"{tipo}{f': {names}' if names else ''}{extra}"


def render_lyrics_annotated_html(
    paragraphs: list[str],
    trechos: list[dict],
) -> str:
    """HTML da letra com margem colorida por trecho."""
    if not paragraphs:
        return '<p class="seq-empty">Cole a letra completa acima e salve.</p>'

    blocks = ['<div class="seq-lyrics-view">']
    blocks.append(render_legend_vocal_html())
    for i, para in enumerate(paragraphs):
        t = next((x for x in trechos if int(x.get("paragrafo", -1)) == i), {})
        tipo = str(t.get("tipo", ""))
        integrantes = t.get("integrantes") or []
        if isinstance(integrantes, str):
            integrantes = [integrantes] if integrantes else []
        nota = str(t.get("nota", ""))
        label = _tipo_label(tipo, integrantes, nota)
        border = TIPO_CORE_COLORS.get(tipo, "#6b7280")
        label_html = (
            f'<span class="seq-lyric-badge" style="border-left-color:{border}">'
            f"{html.escape(label)}</span>"
            if label
            else '<span class="seq-lyric-badge seq-lyric-badge-empty">sem marcação</span>'
        )
        safe_para = html.escape(para).replace("\n", "<br>")
        num = i + 1
        blocks.append(
            f'<div class="seq-lyric-block" style="border-left:4px solid {border}" id="trecho-{num}">'
            f'<span class="seq-trecho-num" style="background:{border}">{num}</span>'
            f"{label_html}<div class=\"seq-lyric-lines\">{safe_para}</div></div>"
        )
    blocks.append("</div>")
    return "".join(blocks)


def render_legend_vocal_html() -> str:
    chips = [
        ("Solo", "#f472b6"),
        ("Harmonia", "#a78bfa"),
        ("Uníssono", "#4ade80"),
        ("Todos", "#34d399"),
    ]
    parts = ['<div class="seq-legend">']
    for name, color in chips:
        parts.append(
            f'<span class="seq-legend-chip" style="border-color:{color}">'
            f'<i style="background:{color}"></i>{html.escape(name)}</span>'
        )
    parts.append("</div>")
    return "".join(parts)


def _empty_trecho(i: int) -> dict:
    return {"paragrafo": i, "tipo": "—", "integrantes": [], "nota": ""}


def _normalize_trechos_state(state: list[dict], n: int) -> list[dict]:
    by_i = {int(x.get("paragrafo", -1)): x for x in state}
    out = []
    for i in range(n):
        t = by_i.get(i, _empty_trecho(i))
        integrantes = t.get("integrantes") or []
        if isinstance(integrantes, str):
            integrantes = [integrantes] if integrantes else []
        out.append(
            {
                "paragrafo": i,
                "tipo": str(t.get("tipo", "—")),
                "integrantes": list(integrantes),
                "nota": str(t.get("nota", "")),
            }
        )
    return out


def _apply_vocal_preset(
    state: list[dict],
    preset: str,
    vocal_labels: list[str],
) -> list[dict]:
    n = len(state)
    if preset == "todos_unissono":
        for i in range(n):
            state[i] = {**state[i], "tipo": "Uníssono", "integrantes": vocal_labels[:]}
    elif preset == "todos_juntos":
        for i in range(n):
            state[i] = {**state[i], "tipo": "Todos juntos", "integrantes": vocal_labels[:]}
    elif preset == "primeiro_solo":
        for i in range(n):
            if i == 0:
                state[i] = {
                    **state[i],
                    "tipo": "Solo",
                    "integrantes": vocal_labels[:1] if vocal_labels else [],
                }
            else:
                state[i] = {**state[i], "tipo": "Uníssono", "integrantes": vocal_labels[:]}
    elif preset == "limpar":
        for i in range(n):
            state[i] = _empty_trecho(i)
    return state


def _apply_vocal_bulk(
    state: list[dict],
    de: int,
    ate: int,
    tipo: str,
    integrantes: list[str],
    nota: str,
) -> list[dict]:
    de = max(1, min(de, len(state)))
    ate = max(de, min(ate, len(state)))
    for i in range(de - 1, ate):
        state[i] = {
            "paragrafo": i,
            "tipo": tipo,
            "integrantes": list(integrantes),
            "nota": nota.strip(),
        }
    return state


def _trecho_preview_line(para: str, max_len: int = 72) -> str:
    line = para.replace("\n", " / ").strip()
    if len(line) > max_len:
        return line[: max_len - 1] + "…"
    return line or "(vazio)"


def render_cifra_html(cifra: str, tom: str, capo: int) -> str:
    capo = max(0, min(11, int(capo or 0)))
    header = f"Tom: <b>{html.escape(tom or '—')}</b>"
    if capo:
        header += f" · Capotraste: <b>{capo}ª casa</b>"
    body = html.escape(cifra or "(sem cifra cadastrada)")
    return (
        f'<div class="seq-cifra-view"><p class="seq-cifra-meta">{header}</p>'
        f'<pre class="seq-cifra-pre">{body}</pre></div>'
    )


def get_sequencia_row(seq_df: pd.DataFrame, programa_id: str) -> dict:
    if seq_df.empty:
        return {}
    m = seq_df[seq_df["programa_id"].astype(str) == str(programa_id)]
    if m.empty:
        return {}
    return m.iloc[0].to_dict()


def _sequencia_cell_value(column: str, value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if column == "capo":
        n = pd.to_numeric(value, errors="coerce")
        if pd.isna(n):
            n = 0
        return str(int(n))
    text = str(value).strip()
    if text.lower() in ("nan", "none", "<na>", "nat"):
        return ""
    return text


def upsert_sequencia_row(
    seq_df: pd.DataFrame,
    programa_id: str,
    **fields,
) -> pd.DataFrame:
    seq_df = seq_df.copy() if not seq_df.empty else _empty_sequencia_df()
    for col in PROGRAMA_SEQUENCIA_COLUMNS:
        if col not in seq_df.columns:
            seq_df[col] = ""
        seq_df[col] = seq_df[col].fillna("").astype(str)
    pid = str(programa_id)
    mask = seq_df["programa_id"].astype(str) == pid
    row = {c: "" for c in PROGRAMA_SEQUENCIA_COLUMNS}
    row["programa_id"] = pid
    row["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if mask.any():
        existing = seq_df[mask].iloc[0].to_dict()
        row.update({k: _sequencia_cell_value(k, v) for k, v in existing.items()})
    row.update(
        {k: _sequencia_cell_value(k, v) for k, v in fields.items() if k in PROGRAMA_SEQUENCIA_COLUMNS}
    )
    if mask.any():
        idx = seq_df[mask].index[0]
        for k, v in row.items():
            if k in seq_df.columns:
                seq_df.at[idx, k] = _sequencia_cell_value(k, v)
    else:
        clean_row = {k: _sequencia_cell_value(k, v) for k, v in row.items()}
        seq_df = pd.concat([seq_df, pd.DataFrame([clean_row])], ignore_index=True)
    return seq_df


def vocalistas_escala(team: list[dict]) -> list[tuple[str, str]]:
    """(label, email) cantores escalados."""
    vocal_kw = ("vocal", "ministrador", "soprano", "tenor", "contralto", "baritono", "mezzo")
    out = []
    for p in team:
        func = str(p.get("funcao", "")).lower()
        nome = str(p.get("nome", ""))
        em = str(p.get("email", ""))
        if any(k in func for k in vocal_kw) or "ministrador" in func:
            out.append((f"{nome} ({p.get('funcao', '')})", em))
    return out


def banda_escala(team: list[dict]) -> list[tuple[str, str]]:
    kw = ("baix", "guitar", "viol", "teclad", "bater", "técnico", "som")
    out = []
    for p in team:
        func = str(p.get("funcao", "")).lower()
        if any(k in func for k in kw):
            out.append((f"{p.get('nome', '')} — {p.get('funcao', '')}", str(p.get("email", ""))))
    return out


def effective_tom(base_key: str, tom_programa: str) -> str:
    t = str(tom_programa or "").strip()
    return t if t else str(base_key or "C").strip() or "C"


def display_cifra_transposed(
    cifra: str,
    original_key: str,
    tom_programa: str,
) -> str:
    orig = effective_tom(original_key, "")
    target = effective_tom(original_key, tom_programa)
    if not cifra.strip():
        return ""
    return transpose_cifra_text(cifra, orig, target)


TOM_OPCOES = (
    "C",
    "C#",
    "Db",
    "D",
    "D#",
    "Eb",
    "E",
    "F",
    "F#",
    "Gb",
    "G",
    "G#",
    "Ab",
    "A",
    "A#",
    "Bb",
    "B",
)


def default_lyrics_from_louvor(louvores_df, title: str, artist: str) -> str:
    if louvores_df is None or louvores_df.empty:
        return ""
    t = str(title or "").strip().lower()
    a = str(artist or "").strip().lower()
    for _, row in louvores_df.iterrows():
        rt = str(row.get("title", "")).strip().lower()
        ra = str(row.get("artist", "")).strip().lower()
        if rt == t and (not a or ra == a or not ra):
            return str(row.get("lyrics_text", "") or row.get("letter", "") or "").strip()
    return ""


def default_cifra_from_louvor(louvores_df, title: str, artist: str) -> str:
    if louvores_df is None or louvores_df.empty:
        return ""
    t = str(title or "").strip().lower()
    a = str(artist or "").strip().lower()
    for _, row in louvores_df.iterrows():
        rt = str(row.get("title", "")).strip().lower()
        ra = str(row.get("artist", "")).strip().lower()
        if rt == t and (not a or ra == a or not ra):
            return str(row.get("cifra_text", "") or "").strip()
    return ""


def trechos_from_markup(raw: str, n_paragraphs: int) -> list[dict]:
    parsed = parse_markup(raw)
    by_idx = {int(x.get("paragrafo", -1)): x for x in parsed if "paragrafo" in x}
    out = []
    for i in range(n_paragraphs):
        t = by_idx.get(i, {})
        integrantes = t.get("integrantes") or []
        if isinstance(integrantes, str):
            integrantes = [integrantes] if integrantes else []
        out.append(
            {
                "paragrafo": i,
                "tipo": str(t.get("tipo", "—")),
                "integrantes": list(integrantes),
                "nota": str(t.get("nota", "")),
            }
        )
    return out


def build_trechos_vocal_ui(
    st,
    paragraphs: list[str],
    vocal_opts: list[tuple[str, str]],
    existing: list[dict],
    key_prefix: str,
) -> list[dict]:
    """Editor rápido: prévia numerada, atalhos e tabela (sem expanders)."""
    n = len(paragraphs)
    if n == 0:
        st.caption("Separe estrofes com uma linha em branco na letra acima.")
        return []

    labels = [x[0] for x in vocal_opts]
    state_key = f"{key_prefix}_vstate"

    if state_key not in st.session_state or len(st.session_state[state_key]) != n:
        st.session_state[state_key] = _normalize_trechos_state(existing, n)

    state: list[dict] = st.session_state[state_key]

    with st.expander("📖 Como marcar em 3 passos", expanded=False):
        st.markdown(
            """
            1. **Letra** — cada bloco separado por linha em branco = um **trecho numerado** (1, 2, 3…).  
            2. **Atalhos** — use os botões ou o intervalo para marcar vários trechos de uma vez.  
            3. **Tabela** — ajuste trecho a trecho; a **prévia** no final mostra o resultado.
            """
        )

    st.markdown("**Marcação rápida**")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        if st.button("👥 Tudo uníssono", key=f"{key_prefix}_pre_uni", use_container_width=True):
            state = _apply_vocal_preset(state, "todos_unissono", labels)
            st.session_state[state_key] = state
            st.rerun()
    with p2:
        if st.button("🎤 1º solo · resto uníssono", key=f"{key_prefix}_pre_s1", use_container_width=True):
            state = _apply_vocal_preset(state, "primeiro_solo", labels)
            st.session_state[state_key] = state
            st.rerun()
    with p3:
        if st.button("👥 Todos juntos", key=f"{key_prefix}_pre_todos", use_container_width=True):
            state = _apply_vocal_preset(state, "todos_juntos", labels)
            st.session_state[state_key] = state
            st.rerun()
    with p4:
        if st.button("↺ Limpar", key=f"{key_prefix}_pre_clr", use_container_width=True):
            state = _apply_vocal_preset(state, "limpar", labels)
            st.session_state[state_key] = state
            st.rerun()

    st.caption("Ou marque um intervalo de trechos:")
    b1, b2, b3, b4, b5 = st.columns([0.7, 0.7, 1.4, 2, 2])
    with b1:
        de = st.number_input("De", min_value=1, max_value=n, value=1, key=f"{key_prefix}_bulk_de")
    with b2:
        ate = st.number_input("Até", min_value=1, max_value=n, value=n, key=f"{key_prefix}_bulk_ate")
    with b3:
        bulk_tipo = st.selectbox(
            "Tipo",
            TIPO_VOCAL_CORE,
            key=f"{key_prefix}_bulk_tipo",
            label_visibility="collapsed",
        )
    bulk_names: list[str] = []
    with b4:
        if bulk_tipo == "Solo" and labels:
            sel = st.selectbox("Cantor", labels, key=f"{key_prefix}_bulk_solo")
            bulk_names = [sel]
        elif bulk_tipo == "Harmonia de voz" and labels:
            bulk_names = st.multiselect(
                "Vozes",
                labels,
                key=f"{key_prefix}_bulk_harm",
                label_visibility="collapsed",
            )
        elif bulk_tipo in ("Uníssono", "Todos juntos"):
            bulk_names = labels[:]
    with b5:
        if st.button("✓ Aplicar no intervalo", key=f"{key_prefix}_bulk_go", use_container_width=True):
            state = _apply_vocal_bulk(
                state, int(de), int(ate), bulk_tipo, bulk_names, ""
            )
            st.session_state[state_key] = state
            st.rerun()

    st.markdown("**Trecho a trecho**")
    h1, h2, h3, h4, h5 = st.columns([0.35, 3.2, 1.5, 2, 1.3])
    h1.markdown("**#**")
    h2.markdown("**Linha da letra**")
    h3.markdown("**Tipo**")
    h4.markdown("**Cantor(es)**")
    h5.markdown("**Obs.**")

    for i, para in enumerate(paragraphs):
        prev = state[i]
        tipo_prev = str(prev.get("tipo", "—"))
        c1, c2, c3, c4, c5 = st.columns([0.35, 3.2, 1.5, 2, 1.3])
        with c1:
            st.markdown(f"**{i + 1}**")
        with c2:
            st.caption(_trecho_preview_line(para))
        with c3:
            tipo = st.selectbox(
                "tipo",
                TIPOS_VOCAL,
                index=TIPOS_VOCAL.index(tipo_prev) if tipo_prev in TIPOS_VOCAL else 0,
                key=f"{key_prefix}_vtipo_{i}",
                label_visibility="collapsed",
            )
        integrantes: list[str] = []
        with c4:
            if tipo == "Solo" and labels:
                prev_names = [x for x in (prev.get("integrantes") or []) if x in labels]
                default_solo = prev_names[0] if prev_names else labels[0]
                sel = st.selectbox(
                    "solo",
                    labels,
                    index=labels.index(default_solo) if default_solo in labels else 0,
                    key=f"{key_prefix}_vsolo_{i}",
                    label_visibility="collapsed",
                )
                integrantes = [sel]
            elif tipo == "Harmonia de voz" and labels:
                integrantes = st.multiselect(
                    "harm",
                    labels,
                    default=[x for x in (prev.get("integrantes") or []) if x in labels],
                    key=f"{key_prefix}_vharm_{i}",
                    label_visibility="collapsed",
                )
            elif tipo in ("Uníssono", "Todos juntos"):
                st.caption("Todos escalados")
                integrantes = labels[:]
            else:
                st.caption("—")
        with c5:
            nota = st.text_input(
                "obs",
                value=str(prev.get("nota", "")),
                key=f"{key_prefix}_vnota_{i}",
                label_visibility="collapsed",
                placeholder="opcional",
            )
        state[i] = {
            "paragrafo": i,
            "tipo": tipo,
            "integrantes": integrantes,
            "nota": nota.strip(),
        }

    st.session_state[state_key] = state

    st.markdown("**Prévia da letra (como no culto)**")
    st.markdown(
        render_lyrics_annotated_html(paragraphs, state),
        unsafe_allow_html=True,
    )
    return state


def build_trechos_banda_ui(
    st,
    paragraphs: list[str],
    banda_opts: list[tuple[str, str]],
    existing: list[dict],
    key_prefix: str,
) -> list[dict]:
    """Tabela compacta de anotações da banda (sem expanders)."""
    n = len(paragraphs)
    if n == 0:
        return []

    labels = [x[0] for x in banda_opts]
    state_key = f"{key_prefix}_bstate"
    if state_key not in st.session_state or len(st.session_state[state_key]) != n:
        by_i = {int(x.get("paragrafo", -1)): x for x in existing}
        st.session_state[state_key] = [
            {
                "paragrafo": i,
                "tipo": str(by_i.get(i, {}).get("tipo", "—")),
                "integrantes": list(by_i.get(i, {}).get("integrantes") or []),
                "tom_trecho": str(by_i.get(i, {}).get("tom_trecho", "")),
                "nota": str(by_i.get(i, {}).get("nota", "")),
            }
            for i in range(n)
        ]

    state: list[dict] = st.session_state[state_key]
    st.caption("Mesmos números de trecho da letra. Deixe em «—» se não houver anotação.")

    h1, h2, h3, h4, h5, h6 = st.columns([0.35, 2.5, 1.4, 1.6, 1.1, 1.3])
    h1.markdown("**#**")
    h2.markdown("**Trecho**")
    h3.markdown("**Tipo**")
    h4.markdown("**Quem**")
    h5.markdown("**Tom**")
    h6.markdown("**Obs.**")

    for i, para in enumerate(paragraphs):
        prev = state[i]
        tipo_prev = str(prev.get("tipo", "—"))
        tom_prev = str(prev.get("tom_trecho", ""))
        c1, c2, c3, c4, c5, c6 = st.columns([0.35, 2.5, 1.4, 1.6, 1.1, 1.3])
        with c1:
            st.markdown(f"**{i + 1}**")
        with c2:
            st.caption(_trecho_preview_line(para, 50))
        with c3:
            tipo = st.selectbox(
                "btipo",
                TIPOS_BANDA,
                index=TIPOS_BANDA.index(tipo_prev) if tipo_prev in TIPOS_BANDA else 0,
                key=f"{key_prefix}_btipo_{i}",
                label_visibility="collapsed",
            )
        integrantes: list[str] = []
        with c4:
            if tipo == "Solo instrumento" and labels:
                prev_names = [x for x in (prev.get("integrantes") or []) if x in labels]
                default_solo = prev_names[0] if prev_names else labels[0]
                sel = st.selectbox(
                    "bsolo",
                    labels,
                    index=labels.index(default_solo) if default_solo in labels else 0,
                    key=f"{key_prefix}_bsolo_{i}",
                    label_visibility="collapsed",
                )
                integrantes = [sel]
            elif tipo in ("Entrada banda", "Harmonia instrumental") and labels:
                integrantes = st.multiselect(
                    "bband",
                    labels,
                    default=[x for x in (prev.get("integrantes") or []) if x in labels],
                    key=f"{key_prefix}_bband_{i}",
                    label_visibility="collapsed",
                )
            else:
                st.caption("—")
        with c5:
            tom_opts = [""] + list(TOM_OPCOES)
            tom_idx = tom_opts.index(tom_prev) if tom_prev in tom_opts else 0
            tom_trecho = st.selectbox(
                "btom",
                tom_opts,
                index=tom_idx,
                key=f"{key_prefix}_btom_{i}",
                label_visibility="collapsed",
            )
        with c6:
            nota = st.text_input(
                "bnota",
                value=str(prev.get("nota", "")),
                key=f"{key_prefix}_bnota_{i}",
                label_visibility="collapsed",
                placeholder="opcional",
            )
        state[i] = {
            "paragrafo": i,
            "tipo": tipo,
            "integrantes": integrantes,
            "tom_trecho": tom_trecho,
            "nota": nota.strip(),
        }

    st.session_state[state_key] = state
    return state
