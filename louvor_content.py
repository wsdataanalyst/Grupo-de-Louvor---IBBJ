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


def fetch_louvor_content_web(
    title: str,
    artist: str = "",
    *,
    cifra_club_url: str = "",
) -> tuple[str, str]:
    """Busca letra e cifra completas na web (Vagalume)."""
    from cifra_fetch import fetch_louvor_lyrics_and_cifra
    from link_finder import find_cifra_url

    try:
        result = fetch_louvor_lyrics_and_cifra(
            title,
            artist,
            cifra_club_url=cifra_club_url,
            resolve_cifra_url=find_cifra_url,
        )
        return result.lyrics_text.strip(), result.cifra_text.strip()
    except Exception:
        return "", ""


def _find_louvor_catalog_index(
    louvores_df: pd.DataFrame, title: str, artist: str
) -> int | None:
    from catalog_sanitize import sanitize_catalog_text

    t = sanitize_catalog_text(title).lower()
    a = sanitize_catalog_text(artist).lower()
    if not t or louvores_df.empty:
        return None
    for idx, row in louvores_df.iterrows():
        rt = sanitize_catalog_text(row.get("title", "")).lower()
        ra = sanitize_catalog_text(row.get("artist", "")).lower()
        if rt == t and (not a or ra == a or not ra):
            return int(idx)
    return None


def apply_content_to_louvores_df(
    louvores_df: pd.DataFrame,
    title: str,
    artist: str,
    lyrics: str,
    cifra: str,
) -> pd.DataFrame:
    """Grava letra/cifra no repertório para não precisar buscar de novo."""
    df = ensure_louvor_content_columns(louvores_df.copy())
    idx = _find_louvor_catalog_index(df, title, artist)
    if idx is None:
        return df
    if lyrics.strip():
        df.at[idx, "lyrics_text"] = lyrics.strip()
    if cifra.strip():
        df.at[idx, "cifra_text"] = cifra.strip()
    src = str(df.at[idx, "source"]).strip()
    tag = "letras_web"
    if tag not in src:
        df.at[idx, "source"] = f"{src}, {tag}".strip(", ") if src else tag
    return df


def ensure_sequencia_louvor_content(
    seq_df: pd.DataFrame,
    programa_id: str,
    louvor_title: str,
    artist: str,
    cifra_url: str,
    tom_base: str,
    louvores_df: pd.DataFrame,
    *,
    lyrics_hint: str = "",
    cifra_hint: str = "",
    use_web: bool = True,
    save_to_catalog: bool = True,
    force_web_refresh: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, str, bool]:
    """
    Garante letra e cifra: repertório → sequência salva → internet.
    Retorna (seq_df, louvores_df, mensagem, buscou_web).
    """
    from catalog_sanitize import sanitize_catalog_text

    louvor_t = sanitize_catalog_text(louvor_title)
    artist_t = sanitize_catalog_text(artist)
    cifra_url = sanitize_catalog_text(cifra_url)

    row = get_sequencia_row(seq_df, programa_id)
    if force_web_refresh:
        lyrics = ""
        cifra = ""
    else:
        lyrics = (lyrics_hint or str(row.get("lyrics_text", ""))).strip()
        cifra = (cifra_hint or str(row.get("cifra_text", ""))).strip()

    if not lyrics:
        lyrics = default_lyrics_from_louvor(louvores_df, louvor_t, artist_t)
    if not cifra:
        cifra = default_cifra_from_louvor(louvores_df, louvor_t, artist_t)

    fetched_web = False
    if use_web and (force_web_refresh or not lyrics or not cifra):
        web_ly, web_cf = fetch_louvor_content_web(
            louvor_t, artist_t, cifra_club_url=cifra_url
        )
        if web_ly and (force_web_refresh or not lyrics):
            lyrics = web_ly
            fetched_web = True
        if web_cf and (force_web_refresh or not cifra):
            cifra = web_cf
            fetched_web = True

    msg = ""
    if lyrics or cifra:
        tom = str(row.get("tom_programa", "")).strip() or tom_base
        seq_df = upsert_sequencia_row(
            seq_df,
            programa_id,
            lyrics_text=lyrics,
            cifra_text=cifra,
            tom_programa=tom,
        )
        if fetched_web:
            msg = "Letra e cifra importadas da internet e salvas neste culto."
            if save_to_catalog and (lyrics or cifra):
                louvores_df = apply_content_to_louvores_df(
                    louvores_df, louvor_t, artist_t, lyrics, cifra
                )
                msg += " Também gravadas no repertório."
        elif not lyrics_hint and not cifra_hint:
            msg = "Carregado do repertório."
    elif use_web:
        msg = (
            "Não encontramos letra/cifra na web para esta música. "
            "Cole manualmente em **Editar** ou ajuste o link de cifra no repertório."
        )

    return seq_df, louvores_df, msg, fetched_web


def hydrate_escala_sequencia_with_web(
    escala_id: str,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    load_seq: Callable[[], pd.DataFrame],
    save_seq: Callable[[pd.DataFrame], None],
    save_louvores: Callable[[pd.DataFrame], None] | None = None,
    use_web: bool = True,
) -> tuple[int, int]:
    """
    Sincroniza do catálogo e busca na web o que faltar.
    Retorna (itens_atualizados_sequencia, itens_buscados_web).
    """
    from catalog_sanitize import sanitize_catalog_text

    seq_df = load_seq()
    seq_df, n_cat = sync_programa_sequencia_from_louvores(
        seq_df, programa_df, louvores_df, escala_id
    )
    web_count = 0
    prog = programa_df[programa_df["escala_id"].astype(str) == str(escala_id)]
    louvores_work = ensure_louvor_content_columns(louvores_df.copy())

    for _, item in prog.iterrows():
        pid = str(item.get("id", ""))
        if not pid:
            continue
        row = get_sequencia_row(seq_df, pid)
        ly = str(row.get("lyrics_text", "")).strip()
        cf = str(row.get("cifra_text", "")).strip()
        if ly and cf:
            continue
        louvor_t = sanitize_catalog_text(item.get("louvor_title", ""))
        artist_t = sanitize_catalog_text(item.get("artist", ""))
        cifra_u = sanitize_catalog_text(item.get("cifra_url", ""))
        tom = sanitize_catalog_text(item.get("key", ""))
        seq_df, louvores_work, _, got_web = ensure_sequencia_louvor_content(
            seq_df,
            pid,
            louvor_t,
            artist_t,
            cifra_u,
            tom,
            louvores_work,
            use_web=use_web,
            save_to_catalog=save_louvores is not None,
        )
        if got_web:
            web_count += 1

    if n_cat or web_count:
        save_seq(seq_df)
    if save_louvores and web_count:
        save_louvores(louvores_work)

    return n_cat + web_count, web_count
