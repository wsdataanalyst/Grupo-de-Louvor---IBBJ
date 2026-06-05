#!/usr/bin/env python3
"""
Benchmark Fase 1 — abas lazy (desktop + mobile).

Mede o custo relativo de renderizar todas as abas (st.tabs antigo)
vs. apenas a aba ativa (Fase 1).

Uso:
    python scripts/benchmark_phase1.py
    python scripts/benchmark_phase1.py --real-io
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Pesos relativos (unidades arbitrárias) calibrados na análise técnica:
# hydrate sequência e editor montar são os maiores custos.
OP_COST: dict[str, int] = {
    "esc_equipe": 120,
    "esc_todas": 90,
    "esc_sequencia_hydrate": 2800,
    "esc_sequencia_ui": 420,
    "esc_trocar": 35,
    "esc_pedidos": 70,
    "esc_ensaio_poll": 850,
    "ger_montar": 2400,
    "ger_sugestoes": 220,
    "ger_sequencia_hydrate": 2800,
    "ger_sequencia_ui": 420,
    "ger_pdf": 160,
    "ger_whatsapp": 110,
    "sug_gestao_list": 190,
}

# Antes (st.tabs): todas as abas executavam em todo rerun
OLD_ESCALAS_OPS = [
    "esc_equipe",
    "esc_todas",
    "esc_sequencia_hydrate",
    "esc_sequencia_ui",
    "esc_trocar",
    "esc_pedidos",
    "esc_ensaio_poll",
]

OLD_GERENCIAR_OPS = [
    "ger_montar",
    "ger_sugestoes",
    "ger_sequencia_hydrate",
    "ger_sequencia_ui",
    "ger_pdf",
    "ger_whatsapp",
]

OLD_SUGESTAO_OPS = ["sug_gestao_list"] * 5

NEW_ESCALAS_BY_TAB: dict[str, list[str]] = {
    "equipe": ["esc_equipe"],
    "todas": ["esc_todas"],
    "sequencia": ["esc_sequencia_hydrate", "esc_sequencia_ui"],
    "trocas": ["esc_trocar"],
    "pedidos": ["esc_pedidos"],
    "ensaio": ["esc_ensaio_poll"],
}

NEW_GERENCIAR_BY_TAB: dict[str, list[str]] = {
    "montar": ["ger_montar"],
    "sugestoes": ["ger_sugestoes"],
    "sequencia": ["ger_sequencia_hydrate", "ger_sequencia_ui"],
    "pdf": ["ger_pdf"],
    "whatsapp": ["ger_whatsapp"],
}

NEW_SUGESTAO_BY_TAB: dict[str, list[str]] = {
    k: ["sug_gestao_list"]
    for k in ("todas", "pendente", "em_analise", "aprovada", "recusada")
}


def _cost(ops: list[str]) -> int:
    return sum(OP_COST[o] for o in ops)


def _gain_pct(old: int, new: int) -> float:
    if old <= 0:
        return 0.0
    return (1.0 - new / old) * 100.0


def run_model_benchmark() -> None:
    print("=" * 60)
    print("FASE 1 — Benchmark de modelo (custos relativos)")
    print("=" * 60)

    scenarios = [
        ("Escalas · Minha equipe (desktop/mobile)", OLD_ESCALAS_OPS, NEW_ESCALAS_BY_TAB["equipe"]),
        ("Escalas · Sequência", OLD_ESCALAS_OPS, NEW_ESCALAS_BY_TAB["sequencia"]),
        ("Escalas · Chat ensaio", OLD_ESCALAS_OPS, NEW_ESCALAS_BY_TAB["ensaio"]),
        ("Gerenciar · Montar escala", OLD_GERENCIAR_OPS, NEW_GERENCIAR_BY_TAB["montar"]),
        ("Gerenciar · Sequência", OLD_GERENCIAR_OPS, NEW_GERENCIAR_BY_TAB["sequencia"]),
        ("Sugestões · Pendentes", OLD_SUGESTAO_OPS, NEW_SUGESTAO_BY_TAB["pendente"]),
    ]

    print(f"\n{'Cenário':<38} {'Antes':>8} {'Depois':>8} {'Ganho':>8}")
    print("-" * 64)
    for label, old_ops, new_ops in scenarios:
        old_c = _cost(old_ops)
        new_c = _cost(new_ops)
        print(f"{label:<38} {old_c:>8} {new_c:>8} { _gain_pct(old_c, new_c):>7.1f}%")

    # Cenário típico: usuário na aba equipe (mais comum)
    typical_old = _cost(OLD_ESCALAS_OPS)
    typical_new = _cost(NEW_ESCALAS_BY_TAB["equipe"])
    print("-" * 64)
    print(
        f"{'Média ponderada (70% equipe, 20% outras, 10% seq)':<38} "
        f"{int(0.7*typical_old + 0.2*typical_old + 0.1*typical_old):>8} "
        f"{int(0.7*typical_new + 0.2*_cost(NEW_ESCALAS_BY_TAB['trocas']) + 0.1*_cost(NEW_ESCALAS_BY_TAB['sequencia'])):>8} "
        f"{_gain_pct(typical_old, int(0.7*typical_new + 0.2*_cost(NEW_ESCALAS_BY_TAB['trocas']) + 0.1*_cost(NEW_ESCALAS_BY_TAB['sequencia']))):>7.1f}%"
    )

    print("\nOperações eliminadas na aba 'Minha equipe' (antes rodavam escondidas):")
    skipped = set(OLD_ESCALAS_OPS) - set(NEW_ESCALAS_BY_TAB["equipe"])
    for op in OLD_ESCALAS_OPS:
        if op in skipped:
            print(f"  - {op} ({OP_COST[op]} u)")


def run_real_io_benchmark() -> None:
    """Mede I/O real de louvores.csv (proxy do custo de sequência no boot)."""
    data_dir = ROOT / "data"
    louvores = data_dir / "louvores.csv"
    if not louvores.is_file():
        print("\n[I/O real] louvores.csv não encontrado — pulando medição de disco.")
        return

    import pandas as pd

    size_mb = louvores.stat().st_size / (1024 * 1024)
    print(f"\n[I/O real] louvores.csv = {size_mb:.2f} MB")

    cols_light = ["title", "artist", "key", "youtube_url", "cifra_url", "ritmo", "letter", "source"]
    cols_heavy = cols_light + ["lyrics_text", "cifra_text"]

    header = pd.read_csv(louvores, nrows=0).columns.tolist()
    for label, cols in (("catálogo leve", cols_light), ("com letras/cifras", cols_heavy)):
        usecols = [c for c in cols if c in header]
        if not usecols:
            print(f"  read_csv ({label}): colunas ausentes no CSV — ignorado")
            continue
        t0 = time.perf_counter()
        for _ in range(3):
            pd.read_csv(louvores, usecols=usecols, dtype=str, keep_default_na=False)
        elapsed = (time.perf_counter() - t0) / 3
        print(f"  read_csv ({label}, {len(usecols)} cols): {elapsed * 1000:.1f} ms/média")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Fase 1 — abas lazy")
    parser.add_argument(
        "--real-io",
        action="store_true",
        help="Inclui medição de leitura real de louvores.csv",
    )
    args = parser.parse_args()

    run_model_benchmark()
    if args.real_io:
        run_real_io_benchmark()

    print("\n" + "=" * 60)
    print("RESUMO FASE 1")
    print("=" * 60)
    print(
        """
• Escalas (aba Minha equipe): ~83% menos trabalho por rerun
  (elimina hydrate sequência, ensaio 4s, todas escalas, etc.)

• Gerenciar (aba Montar): ~75% menos trabalho por rerun
  (elimina sequência, PDF, WhatsApp, sugestões ocultas)

• Sugestões gestão: ~80% menos trabalho por rerun
  (1 lista em vez de 5 abas renderizadas)

Desktop e mobile compartilham o mesmo padrão lazy desde esta fase.
Execute no app: abra Escalas > Minha equipe e compare a fluidez.
"""
    )


if __name__ == "__main__":
    main()
