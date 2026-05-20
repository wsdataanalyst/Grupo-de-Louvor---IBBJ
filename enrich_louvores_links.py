#!/usr/bin/env python3
"""Preenche links de YouTube e Cifra Club (busca na internet ou links de pesquisa)."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from link_finder import (
    fallback_cifra_search,
    fallback_youtube_search,
    find_cifra_url,
    find_youtube_url,
    is_direct_url,
)

DATA_DIR = Path("data")
LOUVORES_FILE = DATA_DIR / "louvores.csv"


def _append_source(src: str, tag: str) -> str:
    src = str(src).strip()
    if tag in src:
        return src
    return f"{src}, {tag}".strip(", ") if src else tag


def enrich_dataframe(
    df: pd.DataFrame,
    *,
    use_web: bool = False,
    limit: int | None = None,
    only_missing: bool = True,
) -> tuple[pd.DataFrame, int]:
    updated = 0
    processed = 0
    for idx, row in df.iterrows():
        if limit is not None and processed >= limit:
            break
        title = str(row.get("title", "")).strip()
        artist = str(row.get("artist", "")).strip()
        if not title:
            continue
        yt = str(row.get("youtube_url", "")).strip()
        cif = str(row.get("cifra_url", "")).strip()
        src = str(row.get("source", "")).strip()
        need_yt = not is_direct_url(yt)
        need_cif = not is_direct_url(cif)
        if only_missing and not need_yt and not need_cif:
            continue
        processed += 1
        changed = False
        tag = "links_busca"
        if need_yt:
            if use_web:
                found = find_youtube_url(title, artist)
                df.at[idx, "youtube_url"] = found or fallback_youtube_search(title, artist)
                if found:
                    tag = "links_web"
            else:
                df.at[idx, "youtube_url"] = fallback_youtube_search(title, artist)
            changed = True
        if need_cif:
            if use_web:
                found = find_cifra_url(title, artist)
                df.at[idx, "cifra_url"] = found or fallback_cifra_search(title, artist)
                if found:
                    tag = "links_web"
            else:
                df.at[idx, "cifra_url"] = fallback_cifra_search(title, artist)
            changed = True
        if changed:
            df.at[idx, "source"] = _append_source(src, tag)
            updated += 1
            if use_web:
                time.sleep(0.15)
    return df, updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Enriquecer catálogo com links.")
    parser.add_argument(
        "--web",
        action="store_true",
        help="Buscar na internet (YouTube e Cifra Club reais).",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--all",
        action="store_true",
        help="Reprocessar músicas sem link direto.",
    )
    args = parser.parse_args()
    if not LOUVORES_FILE.exists():
        print("Arquivo não encontrado:", LOUVORES_FILE)
        return 1
    df = pd.read_csv(LOUVORES_FILE)
    df, n = enrich_dataframe(
        df,
        use_web=args.web,
        limit=args.limit,
        only_missing=not args.all,
    )
    df.to_csv(LOUVORES_FILE, index=False)
    modo = "internet" if args.web else "pesquisa"
    print(f"Atualizado: {n} louvor(es) ({modo}). Total: {len(df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
