"""Propaga alterações do repertório para programação, sequência e demais referências."""

from __future__ import annotations

import pandas as pd

from sequencia_culto import get_sequencia_row, upsert_sequencia_row


def _norm_title(s: str) -> str:
    from catalog_sanitize import sanitize_catalog_text

    return sanitize_catalog_text(s).lower()


def _norm_artist(s: str) -> str:
    from catalog_sanitize import sanitize_catalog_text

    return sanitize_catalog_text(s).lower()


def louvor_matches_row(
    louvor_title: str,
    artist: str,
    catalog_title: str,
    catalog_artist: str,
) -> bool:
    """Mesma música no catálogo (título + artista compatível)."""
    t = _norm_title(louvor_title)
    ct = _norm_title(catalog_title)
    if not t or t != ct:
        return False
    a = _norm_artist(artist)
    ca = _norm_artist(catalog_artist)
    return not a or not ca or a == ca


def propagate_louvor_catalog_update(
    programa_df: pd.DataFrame,
    old_title: str,
    old_artist: str,
    *,
    new_title: str | None = None,
    new_artist: str | None = None,
    new_key: str | None = None,
    new_youtube: str | None = None,
    new_cifra_url: str | None = None,
) -> tuple[pd.DataFrame, int]:
    """
    Atualiza louvor_title, artista, tom e links em todas as linhas de programação
    que apontavam para o louvor antigo.
    """
    from catalog_sanitize import sanitize_catalog_text

    if programa_df.empty:
        return programa_df, 0
    df = programa_df.copy()
    changed = 0
    for idx, row in df.iterrows():
        if not louvor_matches_row(
            old_title,
            old_artist,
            str(row.get("louvor_title", "")),
            str(row.get("artist", "")),
        ):
            continue
        if new_title is not None:
            df.at[idx, "louvor_title"] = sanitize_catalog_text(new_title)
        if new_artist is not None:
            df.at[idx, "artist"] = sanitize_catalog_text(new_artist)
        if new_key is not None:
            df.at[idx, "key"] = sanitize_catalog_text(new_key)
        if new_youtube is not None:
            df.at[idx, "youtube_url"] = sanitize_catalog_text(new_youtube)
        if new_cifra_url is not None:
            df.at[idx, "cifra_url"] = sanitize_catalog_text(new_cifra_url)
        changed += 1
    return df, changed


def refresh_sequencia_content_for_louvor(
    seq_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    title: str,
    artist: str,
    *,
    overwrite: bool = False,
) -> tuple[pd.DataFrame, int]:
    """
    Copia letra/cifra do repertório para a sequência de cada música da programação
    vinculada a este louvor.
    """
    from catalog_sanitize import sanitize_catalog_text
    from louvor_content import ensure_louvor_content_columns
    from sequencia_culto import default_cifra_from_louvor, default_lyrics_from_louvor

    if programa_df.empty:
        return seq_df, 0
    louvores_df = ensure_louvor_content_columns(louvores_df)
    t = sanitize_catalog_text(title)
    a = sanitize_catalog_text(artist)
    catalog_ly = default_lyrics_from_louvor(louvores_df, t, a)
    catalog_cf = default_cifra_from_louvor(louvores_df, t, a)
    if not catalog_ly and not catalog_cf:
        return seq_df, 0

    updated = 0
    for _, item in programa_df.iterrows():
        if not louvor_matches_row(
            t, a, str(item.get("louvor_title", "")), str(item.get("artist", ""))
        ):
            continue
        pid = str(item.get("id", ""))
        if not pid:
            continue
        row = get_sequencia_row(seq_df, pid)
        cur_ly = str(row.get("lyrics_text", "")).strip()
        cur_cf = str(row.get("cifra_text", "")).strip()
        new_ly = catalog_ly if catalog_ly and (overwrite or not cur_ly) else cur_ly
        new_cf = catalog_cf if catalog_cf and (overwrite or not cur_cf) else cur_cf
        if new_ly == cur_ly and new_cf == cur_cf:
            continue
        tom = str(row.get("tom_programa", "")).strip() or sanitize_catalog_text(
            item.get("key", "")
        )
        seq_df = upsert_sequencia_row(
            seq_df,
            pid,
            lyrics_text=new_ly,
            cifra_text=new_cf,
            tom_programa=tom,
        )
        updated += 1
    return seq_df, updated


def apply_repertoire_save_side_effects(
    programa_df: pd.DataFrame,
    seq_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    old_title: str,
    old_artist: str,
    new_title: str,
    new_artist: str,
    *,
    refresh_sequencia: bool = True,
    overwrite_sequencia: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    """Propaga nomes/links na programação e copia letra/cifra do repertório para a sequência."""
    from catalog_sanitize import sanitize_catalog_text

    row_match = louvores_df[
        louvores_df["title"].astype(str).str.strip()
        == sanitize_catalog_text(new_title)
    ]
    new_key = str(row_match.iloc[0].get("key", "")) if not row_match.empty else ""
    new_yt = str(row_match.iloc[0].get("youtube_url", "")) if not row_match.empty else ""
    new_cf_url = str(row_match.iloc[0].get("cifra_url", "")) if not row_match.empty else ""

    programa_df, n_prog = propagate_louvor_catalog_update(
        programa_df,
        old_title,
        old_artist,
        new_title=new_title,
        new_artist=new_artist,
        new_key=new_key,
        new_youtube=new_yt,
        new_cifra_url=new_cf_url,
    )

    n_seq = 0
    if refresh_sequencia:
        seq_df, n_seq = refresh_sequencia_content_for_louvor(
            seq_df,
            programa_df,
            louvores_df,
            new_title,
            new_artist,
            overwrite=overwrite_sequencia,
        )

    return programa_df, seq_df, {"programa": n_prog, "sequencia": n_seq}
