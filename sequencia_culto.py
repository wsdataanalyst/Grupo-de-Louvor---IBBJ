"""Sequência do Culto: letras com marcações e cifras por trecho."""

from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

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

TIPO_BANDA_CORE = (
    "—",
    "Solo instrumento",
    "Entrada banda",
    "Harmonia instrumental",
    "Todos (banda)",
)

TIPO_BANDA_COLORS = {
    "Solo instrumento": "#fbbf24",
    "Entrada banda": "#60a5fa",
    "Harmonia instrumental": "#c084fc",
    "Todos (banda)": "#2dd4bf",
    "Dinâmica / volume": "#fb7185",
    "Silêncio": "#64748b",
}

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


def _append_nota(label: str, nota: str) -> str:
    """Garante que observações opcionais apareçam na visualização final."""
    nota = str(nota or "").strip()
    if not nota:
        return label
    if nota in label:
        return label
    return f"{label} — {nota}" if label else f"💬 {nota}"


def _tipo_label(
    tipo: str,
    integrantes: list[str],
    nota: str,
    *,
    tom_trecho: str = "",
) -> str:
    tipo = str(tipo or "").strip()
    nota = str(nota or "").strip()
    tom = str(tom_trecho or "").strip()
    tom_suffix = f" · Tom {tom}" if tom else ""
    if tipo in ("—", ""):
        return _append_nota("", nota)
    names = ", ".join(integrantes) if integrantes else ""
    if tipo == "Solo" and names:
        return _append_nota(f"🎤 Solo: {names}", nota)
    if tipo == "Harmonia de voz":
        base = f"🎵 Harmonia de voz{f': {names}' if names else ''}"
        return _append_nota(base, nota)
    if tipo == "Uníssono":
        return _append_nota("👥 Uníssono", nota)
    if tipo == "Todos juntos":
        return _append_nota("👥 Todos juntos", nota)
    if tipo == "Solo instrumento" and names:
        return _append_nota(f"🎸 Solo: {names}{tom_suffix}", nota)
    if tipo == "Entrada banda":
        base = f"🎹 Entrada banda{f' ({names})' if names else ''}{tom_suffix}"
        return _append_nota(base, nota)
    if tipo == "Harmonia instrumental":
        base = f"🎶 Harmonia{f' ({names})' if names else ''}{tom_suffix}"
        return _append_nota(base, nota)
    if tipo == "Todos (banda)":
        return _append_nota(f"🎹 Todos (banda){tom_suffix}", nota)
    base = f"{tipo}{f': {names}' if names else ''}{tom_suffix}"
    return _append_nota(base, nota)


def _trecho_tem_marcacao(t: dict) -> bool:
    tipo = str(t.get("tipo", "")).strip()
    nota = str(t.get("nota", "")).strip()
    tom = str(t.get("tom_trecho", "")).strip()
    integrantes = t.get("integrantes") or []
    return bool(
        (tipo and tipo != "—")
        or nota
        or tom
        or (integrantes and integrantes != [])
    )


def _badge_html(label: str, border: str, css_class: str = "seq-lyric-badge") -> str:
    if not label:
        return ""
    return (
        f'<span class="{css_class}" style="border-left-color:{border}">'
        f"{html.escape(label)}</span>"
    )


def render_lyrics_annotated_html(
    paragraphs: list[str],
    trechos_v: list[dict],
    trechos_b: list[dict] | None = None,
) -> str:
    """HTML da letra com vocal, banda e observações por trecho."""
    if not paragraphs:
        return '<p class="seq-empty">Cole a letra completa acima e salve.</p>'

    trechos_b = trechos_b or []
    blocks = ['<div class="seq-lyrics-view">']
    blocks.append(render_legend_vocal_html())
    if trechos_b:
        blocks.append(render_legend_banda_html())
    for i, para in enumerate(paragraphs):
        tv = next((x for x in trechos_v if int(x.get("paragrafo", -1)) == i), {})
        tb = next((x for x in trechos_b if int(x.get("paragrafo", -1)) == i), {})
        tipo_v = str(tv.get("tipo", ""))
        tipo_b = str(tb.get("tipo", ""))
        int_v = tv.get("integrantes") or []
        int_b = tb.get("integrantes") or []
        if isinstance(int_v, str):
            int_v = [int_v] if int_v else []
        if isinstance(int_b, str):
            int_b = [int_b] if int_b else []
        nota_v = str(tv.get("nota", ""))
        nota_b = str(tb.get("nota", ""))
        tom_b = str(tb.get("tom_trecho", ""))
        label_v = _tipo_label(tipo_v, list(int_v), nota_v)
        label_b = _tipo_label(tipo_b, list(int_b), nota_b, tom_trecho=tom_b)
        border = TIPO_CORE_COLORS.get(tipo_v) or TIPO_BANDA_COLORS.get(tipo_b, "#6b7280")
        badges: list[str] = []
        if label_v:
            badges.append(_badge_html(f"Vocal: {label_v}", TIPO_CORE_COLORS.get(tipo_v, "#8b5cf6")))
        if label_b:
            badges.append(
                _badge_html(
                    f"Banda: {label_b}",
                    TIPO_BANDA_COLORS.get(tipo_b, "#60a5fa"),
                    "seq-lyric-badge seq-badge-banda",
                )
            )
        if not badges:
            badges.append(
                '<span class="seq-lyric-badge seq-lyric-badge-empty">sem marcação</span>'
            )
        badges_html = f'<div class="seq-badges-col">{"".join(badges)}</div>'
        safe_para = html.escape(para).replace("\n", "<br>")
        num = i + 1
        blocks.append(
            f'<div class="seq-lyric-block" style="border-left:4px solid {border}" id="trecho-{num}">'
            f'<span class="seq-trecho-num" style="background:{border}">{num}</span>'
            f"{badges_html}<div class=\"seq-lyric-lines\">{safe_para}</div></div>"
        )
    blocks.append("</div>")
    return "".join(blocks)


def render_cifra_direcoes_html(
    paragraphs: list[str],
    trechos_v: list[dict],
    trechos_b: list[dict],
) -> str:
    """Direcionamentos por trecho acima da cifra (vocal + banda + obs.)."""
    if not paragraphs:
        return ""
    rows: list[str] = []
    for i, para in enumerate(paragraphs):
        tv = next((x for x in trechos_v if int(x.get("paragrafo", -1)) == i), {})
        tb = next((x for x in trechos_b if int(x.get("paragrafo", -1)) == i), {})
        if not _trecho_tem_marcacao(tv) and not _trecho_tem_marcacao(tb):
            continue
        tipo_v = str(tv.get("tipo", ""))
        tipo_b = str(tb.get("tipo", ""))
        int_v = tv.get("integrantes") or []
        int_b = tb.get("integrantes") or []
        if isinstance(int_v, str):
            int_v = [int_v] if int_v else []
        if isinstance(int_b, str):
            int_b = [int_b] if int_b else []
        lv = _tipo_label(tipo_v, list(int_v), str(tv.get("nota", "")))
        lb = _tipo_label(
            tipo_b,
            list(int_b),
            str(tb.get("nota", "")),
            tom_trecho=str(tb.get("tom_trecho", "")),
        )
        border = TIPO_CORE_COLORS.get(tipo_v) or TIPO_BANDA_COLORS.get(tipo_b, "#6b7280")
        parts = [p for p in (lv, lb) if p]
        if not parts:
            continue
        preview = html.escape(_trecho_preview_line(para, 56))
        direcao = " · ".join(html.escape(p) for p in parts)
        rows.append(
            f'<div class="seq-cifra-dir" style="border-left:3px solid {border}">'
            f'<span class="seq-cifra-dir-num">{i + 1}</span>'
            f'<span class="seq-cifra-dir-text"><b>{direcao}</b></span>'
            f'<span class="seq-cifra-dir-lyric">{preview}</span></div>'
        )
    if not rows:
        return ""
    return (
        '<div class="seq-cifra-direcoes">'
        '<p class="seq-cifra-direcoes-title">Direcionamento por trecho</p>'
        + "".join(rows)
        + "</div>"
    )


def render_legend_banda_html() -> str:
    chips = [
        ("Solo inst.", "#fbbf24"),
        ("Entrada", "#60a5fa"),
        ("Harmonia", "#c084fc"),
        ("Todos", "#2dd4bf"),
    ]
    parts = ['<div class="seq-legend seq-legend-banda">']
    for name, color in chips:
        parts.append(
            f'<span class="seq-legend-chip" style="border-color:{color}">'
            f'<i style="background:{color}"></i>{html.escape(name)}</span>'
        )
    parts.append("</div>")
    return "".join(parts)


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


def _line_is_chord_row(line: str) -> bool:
    from chord_transpose import _CHORD_RE

    tokens = [t for t in line.strip().split() if t]
    if not tokens:
        return False
    chord_n = sum(1 for t in tokens if _CHORD_RE.match(t))
    return chord_n >= max(2, int(len(tokens) * 0.55))


def _format_chord_line_html(line: str) -> str:
    from chord_transpose import _CHORD_RE

    parts: list[str] = []
    for token in line.split():
        if _CHORD_RE.match(token):
            parts.append(f'<b class="cifra-chord">{html.escape(token)}</b>')
        elif token:
            parts.append(f'<span class="cifra-space">&nbsp;</span>')
    return " ".join(parts) if parts else "&nbsp;"


def _format_cifra_line_html(line: str) -> str:
    from chord_transpose import _CHORD_RE

    out: list[str] = []
    pos = 0
    for m in _CHORD_RE.finditer(line):
        before = line[pos : m.start()]
        if before:
            out.append(html.escape(before))
        out.append(f'<b class="cifra-chord">{html.escape(m.group(0))}</b>')
        pos = m.end()
    if pos < len(line):
        out.append(html.escape(line[pos:]))
    return "".join(out) if out else "&nbsp;"


def render_cifra_html(cifra: str, tom: str, capo: int) -> str:
    """Visual estilo Cifra Club: acordes acima da letra, linha a linha."""
    from cifra_fetch import normalize_cifra_text

    capo = max(0, min(11, int(capo or 0)))
    header = f"Tom: <b>{html.escape(tom or '—')}</b>"
    if capo:
        header += f" · Capotraste: <b>{capo}ª casa</b>"

    raw = normalize_cifra_text(str(cifra or "")).replace("\r\n", "\n").strip()
    if not raw:
        return (
            f'<div class="seq-cifra-view"><p class="seq-cifra-meta">{header}</p>'
            f'<p class="seq-cifra-empty">(sem cifra cadastrada)</p></div>'
        )

    lines = raw.split("\n")
    rows: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if _line_is_chord_row(line):
            chord_html = _format_chord_line_html(line)
            lyric = ""
            if i + 1 < len(lines) and lines[i + 1].strip() and not _line_is_chord_row(lines[i + 1]):
                lyric = html.escape(lines[i + 1].strip())
                i += 2
            else:
                i += 1
            rows.append(
                f'<div class="cifra-strophe">'
                f'<div class="cifra-chord-line">{chord_html}</div>'
                f'<div class="cifra-lyric-line">{lyric or "&nbsp;"}</div>'
                f"</div>"
            )
        else:
            rows.append(
                f'<div class="cifra-strophe cifra-strophe-inline">'
                f'<div class="cifra-lyric-line">{_format_cifra_line_html(line)}</div>'
                f"</div>"
            )
            i += 1

    body = "".join(rows) if rows else f'<pre class="seq-cifra-pre">{html.escape(raw)}</pre>'
    return (
        f'<div class="seq-cifra-view cifra-club-view"><p class="seq-cifra-meta">{header}</p>'
        f'<div class="cifra-club-body">{body}</div></div>'
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


def sequencia_work_signature(
    lyrics_text: str,
    cifra_text: str,
    trechos_v: list[dict],
    trechos_b: list[dict],
    tom: str,
    capo: int,
) -> str:
    import hashlib

    payload = json.dumps(
        {
            "lyrics": str(lyrics_text or "").strip(),
            "cifra": str(cifra_text or "").strip(),
            "v": trechos_v,
            "b": trechos_b,
            "tom": str(tom or "").strip(),
            "capo": int(capo or 0),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def autosave_sequencia_trabalho(
    seq_df: pd.DataFrame,
    programa_id: str,
    *,
    lyrics_text: str,
    cifra_text: str,
    trechos_v: list[dict],
    trechos_b: list[dict],
    tom_programa: str,
    capo: int,
) -> tuple[pd.DataFrame, bool]:
    """
    Salva rascunho da sequência (letra, cifra, marcações) sem exigir botão manual.
    Evita perder marcações ao sair do app ou atualizar a página.
    """
    pid = str(programa_id)
    sig = sequencia_work_signature(
        lyrics_text, cifra_text, trechos_v, trechos_b, tom_programa, capo
    )
    sig_key = f"seq_autosave_sig_{pid}"
    try:
        if st.session_state.get(sig_key) == sig:
            return seq_df, False
    except Exception:
        pass

    seq_df = upsert_sequencia_row(
        seq_df,
        pid,
        lyrics_text=str(lyrics_text or "").strip(),
        cifra_text=str(cifra_text or "").strip(),
        lyrics_markup=markup_to_json(trechos_v),
        cifra_markup=markup_to_json(trechos_b),
        tom_programa=str(tom_programa or "").strip(),
        capo=int(capo or 0),
    )
    try:
        st.session_state[sig_key] = sig
        st.session_state[f"seq_autosave_at_{pid}"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except Exception:
        pass
    return seq_df, True


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


def integrantes_marcacao_opts(team: list[dict]) -> list[tuple[str, str]]:
    """(label, email) — todos os integrantes da escala, para marcações vocais."""
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for p in team:
        nome = str(p.get("nome", "")).strip()
        if not nome:
            continue
        em = str(p.get("email", "")).strip()
        func = str(p.get("funcao", "")).strip()
        key = em.lower() if em else nome.lower()
        if key in seen:
            continue
        seen.add(key)
        label = f"{nome} ({func})" if func else nome
        out.append((label, em))
    return out


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


def _empty_trecho_banda(i: int) -> dict:
    return {
        "paragrafo": i,
        "tipo": "—",
        "integrantes": [],
        "tom_trecho": "",
        "nota": "",
    }


def _normalize_trechos_banda_state(state: list[dict], n: int) -> list[dict]:
    by_i = {int(x.get("paragrafo", -1)): x for x in state}
    out = []
    for i in range(n):
        t = by_i.get(i, _empty_trecho_banda(i))
        integrantes = t.get("integrantes") or []
        if isinstance(integrantes, str):
            integrantes = [integrantes] if integrantes else []
        out.append(
            {
                "paragrafo": i,
                "tipo": str(t.get("tipo", "—")),
                "integrantes": list(integrantes),
                "tom_trecho": str(t.get("tom_trecho", "")),
                "nota": str(t.get("nota", "")),
            }
        )
    return out


def trechos_banda_from_markup(raw: str, n_paragraphs: int) -> list[dict]:
    parsed = parse_markup(raw)
    by_idx = {int(x.get("paragrafo", -1)): x for x in parsed if "paragrafo" in x}
    state = []
    for i in range(n_paragraphs):
        state.append(by_idx.get(i, _empty_trecho_banda(i)))
    return _normalize_trechos_banda_state(state, n_paragraphs)


def _apply_banda_preset(
    state: list[dict],
    preset: str,
    banda_labels: list[str],
) -> list[dict]:
    n = len(state)
    if preset == "todos_banda":
        for i in range(n):
            state[i] = {
                **state[i],
                "tipo": "Todos (banda)",
                "integrantes": banda_labels[:],
            }
    elif preset == "primeiro_solo":
        for i in range(n):
            if i == 0:
                state[i] = {
                    **state[i],
                    "tipo": "Solo instrumento",
                    "integrantes": banda_labels[:1] if banda_labels else [],
                }
            else:
                state[i] = {
                    **state[i],
                    "tipo": "Entrada banda",
                    "integrantes": banda_labels[:],
                }
    elif preset == "limpar":
        for i in range(n):
            state[i] = _empty_trecho_banda(i)
    return state


def _render_inline_lyric_text(para: str, border: str, num: int) -> None:
    safe = html.escape(para).replace("\n", "<br>")
    st.markdown(
        f'<div class="seq-inline-lyric" style="border-left:4px solid {border}">'
        f'<span class="seq-trecho-num" style="background:{border}">{num}</span>'
        f'<div class="seq-inline-lines">{safe}</div></div>',
        unsafe_allow_html=True,
    )


def build_trechos_vocal_ui(
    st,
    paragraphs: list[str],
    vocal_opts: list[tuple[str, str]],
    existing: list[dict],
    key_prefix: str,
) -> list[dict]:
    """Marcação vocal rápida: letra completa + um clique por estrofe."""
    n = len(paragraphs)
    if n == 0:
        st.caption("Separe estrofes com uma linha em branco na letra.")
        return []

    labels = [x[0] for x in vocal_opts]
    state_key = f"{key_prefix}_vstate"

    if state_key not in st.session_state or len(st.session_state[state_key]) != n:
        st.session_state[state_key] = _normalize_trechos_state(existing, n)

    state: list[dict] = st.session_state[state_key]

    st.info(
        "Clique no tipo abaixo de cada estrofe. Use os atalhos para marcar tudo de uma vez. "
        "Salve no final da página."
    )

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        if st.button("👥 Tudo uníssono", key=f"{key_prefix}_pre_uni", use_container_width=True):
            st.session_state[state_key] = _apply_vocal_preset(state, "todos_unissono", labels)
            st.rerun()
    with p2:
        if st.button("🎤 1º solo", key=f"{key_prefix}_pre_s1", use_container_width=True):
            st.session_state[state_key] = _apply_vocal_preset(state, "primeiro_solo", labels)
            st.rerun()
    with p3:
        if st.button("👥 Todos juntos", key=f"{key_prefix}_pre_todos", use_container_width=True):
            st.session_state[state_key] = _apply_vocal_preset(state, "todos_juntos", labels)
            st.rerun()
    with p4:
        if st.button("↺ Limpar", key=f"{key_prefix}_pre_clr", use_container_width=True):
            st.session_state[state_key] = _apply_vocal_preset(state, "limpar", labels)
            st.rerun()

    radio_opts = list(TIPO_VOCAL_CORE)
    extra_tipos = [t for t in TIPOS_VOCAL if t not in TIPO_VOCAL_CORE]

    for i, para in enumerate(paragraphs):
        prev = state[i]
        tipo_prev = str(prev.get("tipo", "—"))
        border = TIPO_CORE_COLORS.get(tipo_prev, "#4b5563")

        with st.container(border=True):
            _render_inline_lyric_text(para, border, i + 1)
            if tipo_prev not in ("—", "") and tipo_prev not in radio_opts:
                st.caption(f"Atual: **{tipo_prev}**")

            tipo = st.radio(
                "Tipo",
                radio_opts,
                index=radio_opts.index(tipo_prev)
                if tipo_prev in radio_opts
                else 0,
                key=f"{key_prefix}_vtipo_{i}",
                horizontal=True,
                label_visibility="collapsed",
            )

            integrantes: list[str] = []
            if tipo == "Solo" and labels:
                prev_names = [x for x in (prev.get("integrantes") or []) if x in labels]
                default_solo = prev_names[0] if prev_names else labels[0]
                sel = st.selectbox(
                    "Solo",
                    labels,
                    index=labels.index(default_solo) if default_solo in labels else 0,
                    key=f"{key_prefix}_vsolo_{i}",
                    label_visibility="collapsed",
                )
                integrantes = [sel]
            elif tipo == "Harmonia de voz" and labels:
                integrantes = st.multiselect(
                    "Harmonia",
                    labels,
                    default=[x for x in (prev.get("integrantes") or []) if x in labels],
                    key=f"{key_prefix}_vharm_{i}",
                    label_visibility="collapsed",
                )
            elif tipo in ("Uníssono", "Todos juntos"):
                integrantes = labels[:]

            if extra_tipos:
                with st.expander("Outro tipo (fala, instrumental…)", expanded=False):
                    tipo_extra = st.selectbox(
                        "Tipo extra",
                        ["—"] + extra_tipos,
                        index=0
                        if tipo_prev in radio_opts
                        else (extra_tipos.index(tipo_prev) + 1
                              if tipo_prev in extra_tipos
                              else 0),
                        key=f"{key_prefix}_vextra_{i}",
                    )
                    if tipo_extra != "—":
                        tipo = tipo_extra

            nota = st.text_input(
                "Direcionamento",
                value=str(prev.get("nota", "")),
                key=f"{key_prefix}_vnota_{i}",
                placeholder="Direcionamento opcional (aparece na letra e na cifra)",
                label_visibility="collapsed",
            )

        state[i] = {
            "paragrafo": i,
            "tipo": tipo,
            "integrantes": integrantes,
            "nota": str(nota).strip(),
        }

    st.session_state[state_key] = state
    return state


def build_trechos_banda_ui(
    st,
    paragraphs: list[str],
    banda_opts: list[tuple[str, str]],
    existing: list[dict],
    key_prefix: str,
) -> list[dict]:
    """Marcação da banda no mesmo padrão da vocal: estrofe + um clique por trecho."""
    n = len(paragraphs)
    if n == 0:
        st.caption("Separe estrofes com linha em branco na letra (mesmos trechos da vocal).")
        return []

    labels = [x[0] for x in banda_opts]
    state_key = f"{key_prefix}_bstate"

    if state_key not in st.session_state or len(st.session_state[state_key]) != n:
        st.session_state[state_key] = _normalize_trechos_banda_state(existing, n)

    state: list[dict] = st.session_state[state_key]

    st.info(
        "Mesmo formato da marcação vocal: escolha o tipo em cada estrofe. "
        "Tom e observações aparecem na cifra e na letra ao salvar."
    )

    p1, p2, p3 = st.columns(3)
    with p1:
        if st.button("🎹 Todos (banda)", key=f"{key_prefix}_pre_tb", use_container_width=True):
            st.session_state[state_key] = _apply_banda_preset(state, "todos_banda", labels)
            st.rerun()
    with p2:
        if st.button("🎸 1º solo", key=f"{key_prefix}_pre_bs", use_container_width=True):
            st.session_state[state_key] = _apply_banda_preset(state, "primeiro_solo", labels)
            st.rerun()
    with p3:
        if st.button("↺ Limpar banda", key=f"{key_prefix}_pre_bc", use_container_width=True):
            st.session_state[state_key] = _apply_banda_preset(state, "limpar", labels)
            st.rerun()

    radio_opts = list(TIPO_BANDA_CORE)
    extra_tipos = [t for t in TIPOS_BANDA if t not in TIPO_BANDA_CORE]

    for i, para in enumerate(paragraphs):
        prev = state[i]
        tipo_prev = str(prev.get("tipo", "—"))
        border = TIPO_BANDA_COLORS.get(tipo_prev, "#4b5563")

        with st.container(border=True):
            _render_inline_lyric_text(para, border, i + 1)
            if tipo_prev not in ("—", "") and tipo_prev not in radio_opts:
                st.caption(f"Atual: **{tipo_prev}**")

            tipo = st.radio(
                "Tipo banda",
                radio_opts,
                index=radio_opts.index(tipo_prev) if tipo_prev in radio_opts else 0,
                key=f"{key_prefix}_btipo_{i}",
                horizontal=True,
                label_visibility="collapsed",
            )

            integrantes: list[str] = []
            if tipo == "Solo instrumento" and labels:
                prev_names = [x for x in (prev.get("integrantes") or []) if x in labels]
                default_solo = prev_names[0] if prev_names else labels[0]
                sel = st.selectbox(
                    "Solo instrumento",
                    labels,
                    index=labels.index(default_solo) if default_solo in labels else 0,
                    key=f"{key_prefix}_bsolo_{i}",
                    label_visibility="collapsed",
                )
                integrantes = [sel]
            elif tipo in ("Entrada banda", "Harmonia instrumental") and labels:
                integrantes = st.multiselect(
                    "Quem",
                    labels,
                    default=[x for x in (prev.get("integrantes") or []) if x in labels],
                    key=f"{key_prefix}_bband_{i}",
                    label_visibility="collapsed",
                )
            elif tipo == "Todos (banda)":
                integrantes = labels[:]

            tom_prev = str(prev.get("tom_trecho", ""))
            tom_opts = [""] + list(TOM_OPCOES)
            tom_idx = tom_opts.index(tom_prev) if tom_prev in tom_opts else 0
            c_tom, c_nota = st.columns([1, 2])
            with c_tom:
                tom_trecho = st.selectbox(
                    "Tom do trecho",
                    tom_opts,
                    index=tom_idx,
                    key=f"{key_prefix}_btom_{i}",
                    label_visibility="visible",
                )
            with c_nota:
                nota = st.text_input(
                    "Direcionamento",
                    value=str(prev.get("nota", "")),
                    key=f"{key_prefix}_bnota_{i}",
                    placeholder="Direcionamento opcional (aparece na letra e na cifra)",
                    label_visibility="collapsed",
                )

            if extra_tipos:
                with st.expander("Outro tipo (dinâmica, silêncio…)", expanded=False):
                    tipo_extra = st.selectbox(
                        "Tipo extra banda",
                        ["—"] + extra_tipos,
                        index=0
                        if tipo_prev in radio_opts
                        else (
                            extra_tipos.index(tipo_prev) + 1
                            if tipo_prev in extra_tipos
                            else 0
                        ),
                        key=f"{key_prefix}_bextra_{i}",
                    )
                    if tipo_extra != "—":
                        tipo = tipo_extra

        state[i] = {
            "paragrafo": i,
            "tipo": tipo,
            "integrantes": integrantes,
            "tom_trecho": str(tom_trecho or ""),
            "nota": str(nota).strip(),
        }

    st.session_state[state_key] = state
    return state
