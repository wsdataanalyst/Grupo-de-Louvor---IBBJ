#!/usr/bin/env python3
"""Remove nan/nam do CSV do catálogo e regrava data/louvores.csv."""

from pathlib import Path

import pandas as pd

from catalog_sanitize import prepare_louvores_df
from app import fix_louvor_display_title, LOUVORES_FILE


def main() -> int:
    if not LOUVORES_FILE.exists():
        print("Arquivo não encontrado:", LOUVORES_FILE)
        return 1
    df = pd.read_csv(LOUVORES_FILE)
    before = df.astype(str).apply(lambda c: c.str.contains(r"\bnan\b", case=False, na=False)).any(axis=1).sum()
    df = prepare_louvores_df(df)
    df["title"] = df["title"].astype(str).apply(fix_louvor_display_title)
    df.to_csv(LOUVORES_FILE, index=False)
    after = df.astype(str).apply(lambda c: c.str.contains(r"\bnan\b", case=False, na=False)).any(axis=1).sum()
    print(f"Limpo {len(df)} louvores. Linhas com 'nan': {before} -> {after}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
