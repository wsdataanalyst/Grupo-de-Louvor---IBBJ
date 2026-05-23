"""Letras e cifras no repertório e cópia automática para a sequência do culto."""

from __future__ import annotations

import time
from typing import Callable

import pandas as pd

from sequencia_culto import (
    PROGRAMA_SEQUENCIA_COLUMNS,
    default_cifra_from_louvor,
    default_lyrics_from_louvor,
    get_sequencia_row,
    upsert_sequencia_row,
)


def ensure_louvor_content_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("lyrics_text", "cifra_text"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
    return df


def count_louvores_missing_content(louvores_df: pd.DataFrame) -> int:
    df = ensure_louvor_content_columns(louvores_df)
    if df.empty:
        return 0
    miss = 0
    for _, row in df.iterrows():
        ly = str(row.get("lyrics_text", "")).strip()
        cf = str(row.get("cifra_text", "")).strip()
        if not ly or not cf:
            miss += 1
    return miss


def enrich_louvores_letras_cifras(
    louvores_df: pd.DataFrame,
    *,
    use_web: bool = True,
    limit: int | None = None,
    only_missing: bool = True,
    delay_sec: float = 0.35,
) -> tuple[pd.DataFrame, int]:
    """
    Preenche lyrics_text e cifra_text no repertório (uma vez; depois tudo é local).
    """
    from catalog_sanitize import sanitize_catalog_text
    from cifra_fetch import fetch_louvor_lyrics_and_cifra
    from link_finder import find_cifra_url

    df = ensure_louvor_content_columns(louvores_df.copy())
    updated = 0
    processed = 0

    for idx, row in df.iterrows():
        if limit is not None and processed >= limit:
            break
        title = sanitize_catalog_text(row.get("title", ""))
        if not title:
            continue
        artist = sanitize_catalog_text(row.get("artist", ""))
        has_ly = str(row.get("lyrics_text", "")).strip()
        has_cf = str(row.get("cifra_text", "")).strip()
        if only_missing and has_ly and has_cf:
            continue

        processed += 1
        if not use_web:
            continue

        cifra_url = sanitize_catalog_text(row.get("cifra_url", ""))
        try:
            content = fetch_louvor_lyrics_and_cifra(
                title,
                artist,
                cifra_club_url=cifra_url,
                resolve_cifra_url=find_cifra_url,
            )
        except Exception:
            content = None

        if content is None:
            if delay_sec:
                time.sleep(delay_sec)
            continue

        changed = False
        if content.lyrics_text.strip() and (not has_ly or only_missing):
            df.at[idx, "lyrics_text"] = content.lyrics_text.strip()
            changed = True
        if content.cifra_text.strip() and (not has_cf or only_missing):
            df.at[idx, "cifra_text"] = content.cifra_text.strip()
            changed = True
        if changed:
            src = str(row.get("source", "")).strip()
            tag = "letras_web"
            df.at[idx, "source"] = f"{src}, {tag}".strip(", ") if src else tag
            updated += 1
        if delay_sec:
            time.sleep(delay_sec)

    return df, updated


def sync_programa_sequencia_from_louvores(
    seq_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    escala_id: str,
) -> tuple[pd.DataFrame, int]:
    """Copia letra/cifra do repertório para cada música da escala (sem internet)."""
    from catalog_sanitize import sanitize_catalog_text

    escala_id = str(escala_id)
    prog = programa_df[programa_df["escala_id"].astype(str) == escala_id].copy()
    if prog.empty:
        return seq_df, 0

    louvores_df = ensure_louvor_content_columns(louvores_df)
    updated = 0

    for _, item in prog.iterrows():
        programa_id = str(item.get("id", ""))
        if not programa_id:
            continue
        louvor_t = sanitize_catalog_text(item.get("louvor_title", ""))
        artist_t = sanitize_catalog_text(item.get("artist", ""))
        cifra_url = sanitize_catalog_text(item.get("cifra_url", ""))

        catalog_ly = default_lyrics_from_louvor(louvores_df, louvor_t, artist_t)
        catalog_cf = default_cifra_from_louvor(louvores_df, louvor_t, artist_t)
        if not catalog_ly and not catalog_cf:
            continue

        row = get_sequencia_row(seq_df, programa_id)
        cur_ly = str(row.get("lyrics_text", "")).strip()
        cur_cf = str(row.get("cifra_text", "")).strip()

        new_ly = catalog_ly if catalog_ly and (not cur_ly or len(catalog_ly) > len(cur_ly)) else cur_ly
        new_cf = catalog_cf if catalog_cf and (not cur_cf or len(catalog_cf) > len(cur_cf)) else cur_cf

        if new_ly == cur_ly and new_cf == cur_cf:
            continue

        tom = str(row.get("tom_programa", "")).strip() or sanitize_catalog_text(
            item.get("key", "")
        )
        seq_df = upsert_sequencia_row(
            seq_df,
            programa_id,
            lyrics_text=new_ly,
            cifra_text=new_cf,
            tom_programa=tom,
        )
        updated += 1

    return seq_df, updated


def hydrate_escala_sequencia(
    escala_id: str,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    load_seq: Callable[[], pd.DataFrame],
    save_seq: Callable[[pd.DataFrame], None],
) -> int:
    """Carrega sequência, preenche do catálogo e grava se houve mudança."""
    seq_df = load_seq()
    seq_df, n = sync_programa_sequencia_from_louvores(
        seq_df, programa_df, louvores_df, escala_id
    )
    if n:
        save_seq(seq_df)
    return n
