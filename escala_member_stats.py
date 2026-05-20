"""Estatísticas de escala por integrante (histórico, mês, ano)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class MemberEscalaStats:
    month_count: int
    year_count: int
    last_date: date | None
    escalado_agora: bool
    month_cultos: list[tuple[date, str]]


def _parse_culto_date(value) -> date | None:
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return None
    return dt.date()


def member_escala_occurrences(
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    exclude_escala_id: str | None = None,
) -> list[tuple[date, str, str]]:
    """Lista (data_culto, escala_id, evento) em que o integrante participou."""
    email = email.strip().lower()
    if not email:
        return []

    escala_dates: dict[str, tuple[date, str]] = {}
    if not escalas_df.empty and "id" in escalas_df.columns:
        for _, row in escalas_df.iterrows():
            eid = str(row.get("id", ""))
            culto = _parse_culto_date(row.get("date"))
            if culto is None:
                continue
            escala_dates[eid] = (culto, str(row.get("event", "Culto")))

    found: list[tuple[date, str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(eid: str, em: str):
        if em != email:
            return
        if exclude_escala_id and str(eid) == str(exclude_escala_id):
            return
        key = (str(eid), em)
        if key in seen:
            return
        seen.add(key)
        if eid in escala_dates:
            d, ev = escala_dates[eid]
            found.append((d, eid, ev))

    if not escalas_df.empty:
        for _, row in escalas_df.iterrows():
            eid = str(row.get("id", ""))
            em = str(row.get("member_email", "")).strip().lower()
            add(eid, em)

    if not equipe_df.empty:
        for _, row in equipe_df.iterrows():
            eid = str(row.get("escala_id", ""))
            em = str(row.get("member_email", "")).strip().lower()
            add(eid, em)

    found.sort(key=lambda x: x[0], reverse=True)
    return found


def member_escala_stats(
    email: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    ref: date | None = None,
    exclude_escala_id: str | None = None,
) -> MemberEscalaStats:
    ref = ref or date.today()
    occ = member_escala_occurrences(
        email, escalas_df, equipe_df, exclude_escala_id=exclude_escala_id
    )
    month_count = sum(1 for d, _, _ in occ if d.year == ref.year and d.month == ref.month)
    year_count = sum(1 for d, _, _ in occ if d.year == ref.year)
    last_date = occ[0][0] if occ else None
    escalado_agora = any(d >= ref for d, _, _ in occ)
    month_cultos = [(d, ev) for d, _, ev in occ if d.year == ref.year and d.month == ref.month]
    return MemberEscalaStats(
        month_count=month_count,
        year_count=year_count,
        last_date=last_date,
        escalado_agora=escalado_agora,
        month_cultos=month_cultos,
    )


def format_date_br(d: date | None) -> str:
    if d is None:
        return "—"
    return d.strftime("%d/%m/%Y")
