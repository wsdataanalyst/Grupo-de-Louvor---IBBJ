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

    colors = {
        "Solo": "#f472b6",
        "Harmonia de voz": "#a78bfa",
        "Uníssono": "#4ade80",
        "Todos juntos": "#34d399",
        "Solo instrumento": "#fbbf24",
        "Entrada banda": "#60a5fa",
    }
    blocks = ['<div class="seq-lyrics-view">']
    for i, para in enumerate(paragraphs):
        t = next((x for x in trechos if int(x.get("paragrafo", -1)) == i), {})
        tipo = str(t.get("tipo", ""))
        integrantes = t.get("integrantes") or []
        if isinstance(integrantes, str):
            integrantes = [integrantes] if integrantes else []
        nota = str(t.get("nota", ""))
        label = _tipo_label(tipo, integrantes, nota)
        border = colors.get(tipo, "#6b7280")
        label_html = (
            f'<span class="seq-lyric-badge" style="border-left-color:{border}">'
            f"{html.escape(label)}</span>"
            if label
            else ""
        )
        safe_para = html.escape(para).replace("\n", "<br>")
        blocks.append(
            f'<div class="seq-lyric-block" style="border-left:4px solid {border}">'
            f'{label_html}<div class="seq-lyric-lines">{safe_para}</div></div>'
        )
    blocks.append("</div>")
    return "".join(blocks)


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


def upsert_sequencia_row(
    seq_df: pd.DataFrame,
    programa_id: str,
    **fields,
) -> pd.DataFrame:
    seq_df = seq_df.copy() if not seq_df.empty else _empty_sequencia_df()
    for col in PROGRAMA_SEQUENCIA_COLUMNS:
        if col not in seq_df.columns:
            seq_df[col] = ""
    pid = str(programa_id)
    mask = seq_df["programa_id"].astype(str) == pid
    row = {c: "" for c in PROGRAMA_SEQUENCIA_COLUMNS}
    row["programa_id"] = pid
    row["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if mask.any():
        row.update(seq_df[mask].iloc[0].to_dict())
    row.update(fields)
    if mask.any():
        idx = seq_df[mask].index[0]
        for k, v in row.items():
            seq_df.at[idx, k] = v
    else:
        seq_df = pd.concat([seq_df, pd.DataFrame([row])], ignore_index=True)
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
    trechos = []
    for i, para in enumerate(paragraphs):
        prev = existing[i] if i < len(existing) else {}
        tipo_prev = str(prev.get("tipo", "—"))
        with st.expander(f"Trecho {i + 1}: {para[:55]}{'…' if len(para) > 55 else ''}", expanded=(tipo_prev not in ("—", ""))):
            tipo = st.selectbox(
                "Marcação vocal",
                TIPOS_VOCAL,
                index=TIPOS_VOCAL.index(tipo_prev) if tipo_prev in TIPOS_VOCAL else 0,
                key=f"{key_prefix}_vtipo_{i}",
            )
            labels = [x[0] for x in vocal_opts]
            emails = [x[1] for x in vocal_opts]
            integrantes: list[str] = []
            if tipo == "Solo":
                if labels:
                    sel = st.selectbox(
                        "Solo — integrante",
                        ["—"] + labels,
                        key=f"{key_prefix}_vsolo_{i}",
                    )
                    if sel != "—":
                        integrantes = [sel]
            elif tipo == "Harmonia de voz":
                if labels:
                    integrantes = st.multiselect(
                        "Harmonia — vozes",
                        labels,
                        default=[x for x in (prev.get("integrantes") or []) if x in labels],
                        key=f"{key_prefix}_vharm_{i}",
                    )
            elif tipo in ("Uníssono", "Todos juntos"):
                integrantes = labels[:]
            nota = st.text_input(
                "Anotação (opcional)",
                value=str(prev.get("nota", "")),
                key=f"{key_prefix}_vnota_{i}",
            )
            trechos.append(
                {
                    "paragrafo": i,
                    "tipo": tipo,
                    "integrantes": integrantes,
                    "integrantes_email": [
                        emails[labels.index(n)] for n in integrantes if n in labels
                    ],
                    "nota": nota.strip(),
                }
            )
    return trechos


def build_trechos_banda_ui(
    st,
    paragraphs: list[str],
    banda_opts: list[tuple[str, str]],
    existing: list[dict],
    key_prefix: str,
) -> list[dict]:
    trechos = []
    for i, para in enumerate(paragraphs):
        prev = existing[i] if i < len(existing) else {}
        tipo_prev = str(prev.get("tipo", "—"))
        with st.expander(
            f"Cifra — trecho {i + 1}: {para[:40]}{'…' if len(para) > 40 else ''}",
            expanded=(tipo_prev not in ("—", "")),
        ):
            tipo = st.selectbox(
                "Marcação banda",
                TIPOS_BANDA,
                index=TIPOS_BANDA.index(tipo_prev) if tipo_prev in TIPOS_BANDA else 0,
                key=f"{key_prefix}_btipo_{i}",
            )
            labels = [x[0] for x in banda_opts]
            integrantes: list[str] = []
            if tipo == "Solo instrumento" and labels:
                sel = st.selectbox(
                    "Instrumentista",
                    ["—"] + labels,
                    key=f"{key_prefix}_bsolo_{i}",
                )
                if sel != "—":
                    integrantes = [sel]
            elif tipo in ("Entrada banda", "Harmonia instrumental") and labels:
                integrantes = st.multiselect(
                    "Integrantes",
                    labels,
                    default=[x for x in (prev.get("integrantes") or []) if x in labels],
                    key=f"{key_prefix}_bband_{i}",
                )
            tom_trecho = st.selectbox(
                "Tom deste trecho (vazio = tom geral)",
                [""] + list(TOM_OPCOES),
                index=0,
                key=f"{key_prefix}_btom_{i}",
            )
            nota = st.text_input(
                "Ajuste / dinâmica",
                value=str(prev.get("nota", "")),
                key=f"{key_prefix}_bnota_{i}",
            )
            trechos.append(
                {
                    "paragrafo": i,
                    "tipo": tipo,
                    "integrantes": integrantes,
                    "tom_trecho": tom_trecho,
                    "nota": nota.strip(),
                }
            )
    return trechos
