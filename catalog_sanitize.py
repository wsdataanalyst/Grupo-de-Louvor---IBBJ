"""Remove artefatos nan/nam dos dados do catálogo de louvores."""

from __future__ import annotations

import re

import pandas as pd

_NAN_TOKENS = frozenset({"nan", "none", "nat", "<na>", "nam"})


def is_missing_catalog_token(value: str) -> bool:
    return str(value).strip().lower() in _NAN_TOKENS


def sanitize_catalog_text(value) -> str:
    """Limpa células vazias salvas como nan e sufixos +nan em URLs."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value).strip()
    if is_missing_catalog_token(s):
        return ""
    s = re.sub(r"\+nan\b", "", s, flags=re.I)
    s = re.sub(r"%20nan\b", "", s, flags=re.I)
    s = re.sub(r"\s+nan\b", "", s, flags=re.I)
    s = re.sub(r"\bnan\s+", "", s, flags=re.I)
    s = re.sub(r",\s*nha\s+fé", ", minha fé", s, flags=re.I)
    s = re.sub(r"\bm\s+1\b", "em mim", s, flags=re.I)
    return s.strip()


def prepare_louvores_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].apply(sanitize_catalog_text)
    return out


def format_louvor_display(title: str, artist: str = "") -> str:
    """Título para exibição, sem sufixo '— nan' quando artista está vazio."""
    t = sanitize_catalog_text(title)
    a = sanitize_catalog_text(artist)
    return f"{t} — {a}" if a else t


def louvor_title_artist_from_row_or_label(
    data: dict,
    label: str = "",
) -> tuple[str, str]:
    """Extrai título e artista do dict da linha ou do rótulo 'Música — Artista'."""
    titulo = sanitize_catalog_text(data.get("title", ""))
    artista = sanitize_catalog_text(data.get("artist", ""))
    if not titulo and label:
        if " — " in label:
            parts = label.split(" — ", 1)
            titulo = sanitize_catalog_text(parts[0])
            artista = sanitize_catalog_text(parts[1]) if len(parts) > 1 else artista
        else:
            titulo = sanitize_catalog_text(label)
    return titulo, artista


def format_louvor_search_button(
    title: str,
    artist: str = "",
    *,
    prefix: str = "➕ ",
) -> str:
    """Botão da busca: mostra música e artista; se faltar um, mostra o disponível."""
    t = sanitize_catalog_text(title)
    a = sanitize_catalog_text(artist)
    if t and a:
        body = f"{t} — {a}"
    elif t:
        body = t
    elif a:
        body = a
    else:
        body = "Louvor"
    return f"{prefix}{body}" if prefix else body


def fix_louvor_display_title(title: str) -> str:
    """Correções ortográficas leves para exibição de títulos de louvor."""
    t = sanitize_catalog_text(title)
    fixes = {
        "Aclame ao senhor": "Aclame ao Senhor",
        "a alegria esta no coracao": "A alegria está no coração",
        "A alegria esta no coracao": "A alegria está no coração",
        "Autor da,nha fé": "Autor da minha fé",
        "Autor da minha fé": "Autor da minha fé",
        "a começar em": "A começar em mim",
        "A começar em": "A começar em mim",
    }
    tl = t.lower()
    for wrong, right in fixes.items():
        if tl == wrong.lower():
            return right
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    return t
