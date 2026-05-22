"""Preenche temas, referências e duração em data/louvores.csv (execute localmente)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from louvor_meta import ensure_louvor_row_metadata  # noqa: E402

LOUVORES = ROOT / "data" / "louvores.csv"


def main() -> None:
    if not LOUVORES.exists():
        print("Arquivo não encontrado:", LOUVORES)
        return
    df = pd.read_csv(LOUVORES)
    for col in ("temas", "ref_biblica", "duracao_min", "validacao_status", "validacao_nota"):
        if col not in df.columns:
            df[col] = ""
    updated = 0
    for idx, row in df.iterrows():
        meta = ensure_louvor_row_metadata(
            str(row.get("title", "")),
            str(row.get("artist", "")),
            str(row.get("temas", "")),
            str(row.get("ref_biblica", "")),
            str(row.get("duracao_min", "")),
        )
        changed = False
        for k, v in meta.items():
            if str(row.get(k, "")).strip() != v:
                df.at[idx, k] = v
                changed = True
        if not str(row.get("validacao_status", "")).strip():
            df.at[idx, "validacao_status"] = "classificado"
            changed = True
        if changed:
            updated += 1
    df.to_csv(LOUVORES, index=False)
    print(f"Atualizado: {updated} de {len(df)} louvores em {LOUVORES}")


if __name__ == "__main__":
    main()
