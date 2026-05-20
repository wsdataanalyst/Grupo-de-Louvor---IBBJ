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
