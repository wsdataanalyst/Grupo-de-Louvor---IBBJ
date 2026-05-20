"""Aplica correções ortográficas leves em data/louvores.csv."""
import pandas as pd
from pathlib import Path

from app import fix_louvor_display_title, LOUVORES_FILE

from catalog_sanitize import prepare_louvores_df

df = prepare_louvores_df(pd.read_csv(LOUVORES_FILE))
df["title"] = df["title"].astype(str).apply(fix_louvor_display_title)
# Corrigir títulos partidos conhecidos
fixes = {
    "A começar em": "A começar em mim",
    "Autor da": "Autor da minha fé",
    "Andam de procurando 3": "Andam de pé procurando",
}
for old, new in fixes.items():
    df.loc[df["title"] == old, "title"] = new
df.to_csv(LOUVORES_FILE, index=False)
print(f"Atualizado {len(df)} louvores em {LOUVORES_FILE}")
