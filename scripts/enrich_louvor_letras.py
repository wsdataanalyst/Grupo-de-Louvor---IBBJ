#!/usr/bin/env python3
"""Preenche letras e cifras no repertório (data/louvores.csv) a partir da web."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from louvor_content import count_louvores_missing_content, enrich_louvores_letras_cifras

LOUVORES = ROOT / "data" / "louvores.csv"
COLS = (
    "title",
    "artist",
    "key",
    "youtube_url",
    "cifra_url",
    "ritmo",
    "letter",
    "source",
    "lyrics_text",
    "cifra_text",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Importar letras e cifras para o repertório")
    parser.add_argument("--limit", type=int, default=20, help="Máximo de músicas por execução")
    parser.add_argument("--all", action="store_true", help="Reprocessar mesmo as que já têm texto")
    args = parser.parse_args()

    if not LOUVORES.exists():
        print("Arquivo não encontrado:", LOUVORES)
        sys.exit(1)

    df = pd.read_csv(LOUVORES)
    for c in COLS:
        if c not in df.columns:
            df[c] = ""

    antes = count_louvores_missing_content(df)
    print(f"Faltam letra ou cifra em {antes} de {len(df)} louvores.")

    df, n = enrich_louvores_letras_cifras(
        df,
        use_web=True,
        limit=args.limit if args.limit > 0 else None,
        only_missing=not args.all,
    )
    df.to_csv(LOUVORES, index=False)
    depois = count_louvores_missing_content(df)
    print(f"Atualizados: {n}. Ainda faltam: {depois}.")
    if depois and args.limit:
        print("Execute de novo com --limit para continuar.")


if __name__ == "__main__":
    main()
