"""Sugestões de escalas e louvores para líderes/organizadores (não aplica automaticamente)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

import pandas as pd

from escala_member_stats import member_escala_stats

HorizonKind = Literal["semana", "mes", "2_meses", "trimestre"]

LOUVORES_POR_CULTO = 5
LOUVORES_SANTA_CEIA = 6

VOCAL_ROLES = {
    "Vocalista - Tenor",
    "Vocalista - Contralto",
    "Vocalista - Soprano",
    "Vocalista - Mezzo Soprano",
    "Vocalista - Baritono",
}
INSTRUMENT_ROLES = {
    "Baixista",
    "Guitarrista",
    "Violonista",
    "Baterista",
    "Tecladista",
}
TECH_ROLE = "Técnico de som"

FUNCAO_MINISTRADOR = "Ministrador"
FUNCAO_INTEGRANTE = "Integrante"
FUNCAO_BANDA = "Banda"
FUNCAO_TECNICO = "Técnico de som"

CULTO_PARTES_5 = [
    "Abertura / Entrada",
    "Louvor 1",
    "Louvor 2",
    "Louvor 3",
    "Oferta",
]
CULTO_PARTES_6 = [
    "Abertura / Entrada",
    "Louvor 1",
    "Louvor 2",
    "Louvor 3",
    "Momento de adoração",
    "Oferta",
]


@dataclass
class MemberCandidate:
    email: str
    name: str
    tracks: frozenset[str]
    default_funcao: str
    month_count: int
    year_count: int
    last_date: date | None


@dataclass
class LouvorPick:
    title: str
    artist: str
    key: str
    parte: str
    ordem: int


@dataclass
class EquipeSlot:
    email: str
    name: str
    funcao: str
    track: str


@dataclass
class CultoSuggestion:
    culto_date: date
    event_name: str
    is_santa_ceia: bool
    louvor_count: int
    ministrador: EquipeSlot
    equipe: list[EquipeSlot]
    louvores: list[LouvorPick]
    existing_escala_id: str | None = None
    notes: list[str] = field(default_factory=list)


def is_first_sunday(d: date) -> bool:
    return d.weekday() == 6 and d.day <= 7


def louvores_count_for_culto(d: date) -> int:
    return LOUVORES_SANTA_CEIA if is_first_sunday(d) else LOUVORES_POR_CULTO


def partes_for_culto(d: date) -> list[str]:
    n = louvores_count_for_culto(d)
    return (CULTO_PARTES_6 if n >= 6 else CULTO_PARTES_5)[:n]


def _parse_date(value) -> date | None:
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return None
    return dt.date()


def member_role_tracks(roles_str: str) -> frozenset[str]:
    parts = [p.strip() for p in str(roles_str).split(",") if p.strip()]
    tracks: set[str] = set()
    for p in parts:
        if p in VOCAL_ROLES:
            tracks.add("vocal")
        elif p in INSTRUMENT_ROLES:
            tracks.add("instrument")
        elif p == TECH_ROLE:
            tracks.add("tech")
    if not tracks:
        tracks.add("vocal")
    return frozenset(tracks)


def funcao_to_track(funcao: str) -> str:
    f = str(funcao).strip()
    if f == FUNCAO_BANDA:
        return "instrument"
    if f == FUNCAO_TECNICO:
        return "tech"
    return "vocal"


def default_funcao_for_member(tracks: frozenset[str]) -> str:
    if "tech" in tracks and len(tracks) == 1:
        return FUNCAO_TECNICO
    if "instrument" in tracks and "vocal" not in tracks:
        return FUNCAO_BANDA
    if "instrument" in tracks:
        return FUNCAO_BANDA
    return FUNCAO_INTEGRANTE


def next_sunday_on_or_after(ref: date) -> date:
    days = (6 - ref.weekday()) % 7
    return ref + timedelta(days=days)


def sundays_between(start: date, end: date) -> list[date]:
    if start > end:
        return []
    cur = next_sunday_on_or_after(start)
    if cur < start:
        cur += timedelta(days=7)
    out: list[date] = []
    while cur <= end:
        out.append(cur)
        cur += timedelta(days=7)
    return out


def horizon_date_range(horizon: HorizonKind, ref: date | None = None) -> tuple[date, date]:
    ref = ref or date.today()
    first = next_sunday_on_or_after(ref)

    if horizon == "semana":
        return first, first

    if horizon == "mes":
        y, m = first.year, first.month
        if m == 12:
            end = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(y, m + 1, 1) - timedelta(days=1)
        return first, end

    if horizon == "2_meses":
        m = first.month + 1
        y = first.year
        if m > 12:
            m -= 12
            y += 1
        if m == 12:
            end = date(y + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(y, m + 1, 1) - timedelta(days=1)
        return first, end

    # trimestre (~3 meses a partir do primeiro domingo)
    m = first.month + 2
    y = first.year
    while m > 12:
        m -= 12
        y += 1
    if m == 12:
        end = date(y + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(y, m + 1, 1) - timedelta(days=1)
    return first, end


def default_event_name(d: date) -> str:
    if is_first_sunday(d):
        return "Culto — Santa Ceia"
    return "Culto dominical"


def build_candidates(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    culto_ref: date,
) -> list[MemberCandidate]:
    if members_df.empty:
        return []
    out: list[MemberCandidate] = []
    for _, row in members_df.iterrows():
        email = str(row.get("email", "")).strip().lower()
        if not email:
            continue
        fn = str(row.get("first_name", "")).strip()
        ln = str(row.get("last_name", "")).strip()
        name = f"{fn} {ln}".strip() or email
        tracks = member_role_tracks(str(row.get("roles", "")))
        stats = member_escala_stats(email, escalas_df, equipe_df, ref=culto_ref)
        out.append(
            MemberCandidate(
                email=email,
                name=name,
                tracks=tracks,
                default_funcao=default_funcao_for_member(tracks),
                month_count=stats.month_count,
                year_count=stats.year_count,
                last_date=stats.last_date,
            )
        )
    return out


def _days_since(d: date | None, ref: date) -> int:
    if d is None:
        return 9999
    return max(0, (ref - d).days)


def _consecutive_same_track(
    email: str,
    track: str,
    culto_date: date,
    last_by_email_track: dict[tuple[str, str], date],
    member_tracks: frozenset[str],  # noqa: ARG001 — reservado para regras futuras
) -> bool:
    """True se o integrante já entrou no culto imediatamente anterior na mesma trilha."""
    prev = last_by_email_track.get((email, track))
    if prev is None:
        return False
    return (culto_date - prev).days <= 7


def _score_member(
    cand: MemberCandidate,
    culto_date: date,
    *,
    role: str,
    last_by_email_track: dict[tuple[str, str], date],
    already_picked: set[str],
    prefer_track: str | None = None,
) -> float:
    if cand.email in already_picked:
        return -1e9
    track = funcao_to_track(role)
    if prefer_track and prefer_track not in cand.tracks and track != "tech":
        if track == "instrument" and "instrument" not in cand.tracks:
            return -1e9
        if track == "vocal" and "vocal" not in cand.tracks and cand.default_funcao != FUNCAO_TECNICO:
            pass
    if _consecutive_same_track(
        cand.email, track, culto_date, last_by_email_track, cand.tracks
    ):
        return -5e8
    score = 1000.0
    score -= cand.month_count * 120
    score -= cand.year_count * 8
    score += min(_days_since(cand.last_date, culto_date), 365) * 2.5
    if prefer_track and prefer_track in cand.tracks:
        score += 40
    if role == FUNCAO_BANDA and "instrument" in cand.tracks:
        score += 30
    if role == FUNCAO_INTEGRANTE and "vocal" in cand.tracks:
        score += 25
    if role == FUNCAO_TECNICO and "tech" in cand.tracks:
        score += 50
    return score


def _seed_last_assignments(
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
) -> dict[tuple[str, str], date]:
    """Última data por (email, trilha) a partir do histórico."""
    last: dict[tuple[str, str], date] = {}
    if escalas_df.empty:
        return last

    escala_dates: dict[str, date] = {}
    for _, row in escalas_df.iterrows():
        eid = str(row.get("id", ""))
        d = _parse_date(row.get("date"))
        if d:
            escala_dates[eid] = d

    def touch(email: str, track: str, d: date):
        email = email.strip().lower()
        if not email:
            return
        key = (email, track)
        if key not in last or d > last[key]:
            last[key] = d

    for _, row in escalas_df.iterrows():
        eid = str(row.get("id", ""))
        d = escala_dates.get(eid)
        if not d:
            continue
        em = str(row.get("member_email", "")).strip().lower()
        touch(em, "vocal", d)

    if not equipe_df.empty:
        for _, row in equipe_df.iterrows():
            eid = str(row.get("escala_id", ""))
            d = escala_dates.get(eid)
            if not d:
                continue
            em = str(row.get("member_email", "")).strip().lower()
            tr = funcao_to_track(str(row.get("funcao", FUNCAO_INTEGRANTE)))
            touch(em, tr, d)

    return last


def _record_assignment(
    last: dict[tuple[str, str], date],
    email: str,
    funcao: str,
    culto_date: date,
    tracks: frozenset[str],
):
    tr = funcao_to_track(funcao)
    last[(email, tr)] = culto_date
    if len(tracks) > 1:
        for alt in tracks:
            if alt != tr:
                pass


def pick_equipe_for_culto(
    candidates: list[MemberCandidate],
    culto_date: date,
    last_by_email_track: dict[tuple[str, str], date],
    *,
    team_size: int = 6,
) -> tuple[EquipeSlot, list[EquipeSlot], list[str]]:
    notes: list[str] = []
    picked_emails: set[str] = set()

    minist_scores = [
        (
            _score_member(
                c,
                culto_date,
                role=FUNCAO_MINISTRADOR,
                last_by_email_track=last_by_email_track,
                already_picked=picked_emails,
                prefer_track="vocal",
            ),
            c,
        )
        for c in candidates
    ]
    minist_scores.sort(key=lambda x: x[0], reverse=True)
    minist = None
    for sc, c in minist_scores:
        if sc > -1e8:
            minist = c
            break
    if minist is None and candidates:
        minist = candidates[0]
        notes.append("Ministrador: regra de intercalação flexibilizada.")

    if minist is None:
        raise ValueError("Sem integrantes para sugerir escala.")

    min_slot = EquipeSlot(
        email=minist.email,
        name=minist.name,
        funcao=FUNCAO_MINISTRADOR,
        track="vocal",
    )
    picked_emails.add(minist.email)
    _record_assignment(
        last_by_email_track, minist.email, FUNCAO_MINISTRADOR, culto_date, minist.tracks
    )

    equipe: list[EquipeSlot] = []
    slots_plan = [
        (FUNCAO_BANDA, "instrument"),
        (FUNCAO_BANDA, "instrument"),
        (FUNCAO_INTEGRANTE, "vocal"),
        (FUNCAO_INTEGRANTE, "vocal"),
        (FUNCAO_TECNICO, "tech"),
    ]
    remaining = max(0, team_size - 1)
    plan = slots_plan[:remaining]

    for funcao, prefer in plan:
        best = None
        best_sc = -1e9
        for c in candidates:
            sc = _score_member(
                c,
                culto_date,
                role=funcao,
                last_by_email_track=last_by_email_track,
                already_picked=picked_emails,
                prefer_track=prefer,
            )
            if sc > best_sc:
                best_sc = sc
                best = c
        if best is None or best_sc <= -1e8:
            for c in candidates:
                sc = _score_member(
                    c,
                    culto_date,
                    role=FUNCAO_INTEGRANTE,
                    last_by_email_track=last_by_email_track,
                    already_picked=picked_emails,
                )
                if sc > best_sc:
                    best_sc = sc
                    best = c
                    funcao = FUNCAO_INTEGRANTE
        if best is None:
            continue
        tr = funcao_to_track(funcao)
        equipe.append(
            EquipeSlot(email=best.email, name=best.name, funcao=funcao, track=tr)
        )
        picked_emails.add(best.email)
        _record_assignment(
            last_by_email_track, best.email, funcao, culto_date, best.tracks
        )

    return min_slot, equipe, notes


def louvor_usage_recent(
    programa_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    *,
    within_days: int = 120,
    ref: date | None = None,
) -> dict[str, date]:
    ref = ref or date.today()
    escala_dates: dict[str, date] = {}
    for _, row in escalas_df.iterrows():
        eid = str(row.get("id", ""))
        d = _parse_date(row.get("date"))
        if d:
            escala_dates[eid] = d

    usage: dict[str, date] = {}
    if programa_df.empty:
        return usage
    for _, row in programa_df.iterrows():
        eid = str(row.get("escala_id", ""))
        d = escala_dates.get(eid)
        if not d or (ref - d).days > within_days:
            continue
        title = str(row.get("louvor_title", "")).strip().lower()
        if not title:
            continue
        if title not in usage or d > usage[title]:
            usage[title] = d
    return usage


def suggest_louvores_for_culto(
    culto_date: date,
    louvores_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    *,
    used_in_plan: set[str] | None = None,
) -> list[LouvorPick]:
    n = louvores_count_for_culto(culto_date)
    partes = partes_for_culto(culto_date)
    used_in_plan = used_in_plan or set()
    recent = louvor_usage_recent(programa_df, escalas_df, ref=culto_date)

    if louvores_df.empty:
        return [
            LouvorPick(title=f"(cadastre louvor {i+1})", artist="", key="", parte=partes[i], ordem=i + 1)
            for i in range(n)
        ]

    rows: list[tuple[float, dict]] = []
    for _, r in louvores_df.iterrows():
        title = str(r.get("title", "")).strip()
        if not title:
            continue
        key_l = title.lower()
        if key_l in used_in_plan:
            continue
        last = recent.get(key_l)
        days = (culto_date - last).days if last else 999
        score = days * 3.0
        if last and (culto_date - last).days < 14:
            score -= 500
        rows.append((score, r.to_dict()))

    rows.sort(key=lambda x: x[0], reverse=True)
    seed = culto_date.toordinal()
    picks: list[LouvorPick] = []
    pool = [d for _, d in rows]
    if len(pool) < n:
        pool = [d for _, d in rows] + [d for _, d in rows]

    idx = 0
    for i in range(n):
        pos = (seed + i * 7) % max(len(pool), 1)
        item = pool[pos] if pool else {}
        title = str(item.get("title", f"Louvor {i+1}")).strip()
        artist = str(item.get("artist", "")).strip()
        tom = str(item.get("key", "")).strip()
        used_in_plan.add(title.lower())
        picks.append(
            LouvorPick(
                title=title,
                artist=artist,
                key=tom,
                parte=partes[i] if i < len(partes) else f"Louvor {i+1}",
                ordem=i + 1,
            )
        )
        idx += 1
    return picks


def existing_escala_for_date(escalas_df: pd.DataFrame, culto_date: date) -> str | None:
    if escalas_df.empty:
        return None
    for _, row in escalas_df.iterrows():
        d = _parse_date(row.get("date"))
        if d == culto_date:
            return str(row.get("id", ""))
    return None


def generate_escala_suggestions(
    horizon: HorizonKind,
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    ref: date | None = None,
    team_size: int = 6,
) -> list[CultoSuggestion]:
    ref = ref or date.today()
    start, end = horizon_date_range(horizon, ref)
    culto_dates = sundays_between(start, end)
    if not culto_dates:
        return []

    last_track = _seed_last_assignments(escalas_df, equipe_df)
    candidates = build_candidates(members_df, escalas_df, equipe_df, culto_ref=start)
    used_louvores: set[str] = set()
    suggestions: list[CultoSuggestion] = []

    for culto_date in culto_dates:
        eid = existing_escala_for_date(escalas_df, culto_date)
        minist, equipe, notes = pick_equipe_for_culto(
            candidates,
            culto_date,
            last_track,
            team_size=team_size,
        )
        louvores = suggest_louvores_for_culto(
            culto_date,
            louvores_df,
            programa_df,
            escalas_df,
            used_in_plan=used_louvores,
        )
        for lv in louvores:
            used_louvores.add(lv.title.lower())

        if is_first_sunday(culto_date):
            notes.append("Santa Ceia: 6 louvores sugeridos.")
        if eid:
            notes.append("Já existe escala cadastrada nesta data.")

        suggestions.append(
            CultoSuggestion(
                culto_date=culto_date,
                event_name=default_event_name(culto_date),
                is_santa_ceia=is_first_sunday(culto_date),
                louvor_count=louvores_count_for_culto(culto_date),
                ministrador=minist,
                equipe=equipe,
                louvores=louvores,
                existing_escala_id=eid,
                notes=notes,
            )
        )

    return suggestions


def horizon_label(horizon: HorizonKind) -> str:
    return {
        "semana": "Próxima escala (semana)",
        "mes": "Mês inteiro",
        "2_meses": "2 meses",
        "trimestre": "Trimestre",
    }[horizon]


def culto_suggestion_payload(sug: CultoSuggestion, escala_id: str) -> dict:
    """Dicionários prontos para gravar em escalas / equipe / programa."""
    escala = {
        "id": escala_id,
        "date": sug.culto_date.strftime("%Y-%m-%d"),
        "event": sug.event_name,
        "responsible": sug.ministrador.name,
        "member_email": sug.ministrador.email,
        "member_name": sug.ministrador.name,
        "notes": "Sugestão automática — revise antes de publicar.",
        "rehearsal_date": "",
    }
    equipe = []
    for slot in sug.equipe:
        equipe.append(
            {
                "escala_id": escala_id,
                "member_email": slot.email,
                "member_name": slot.name,
                "funcao": slot.funcao,
            }
        )
    programa = []
    for lv in sug.louvores:
        programa.append(
            {
                "escala_id": escala_id,
                "ordem": lv.ordem,
                "parte": lv.parte,
                "louvor_title": lv.title,
                "artist": lv.artist,
                "key": lv.key,
                "leader_email": sug.ministrador.email,
                "leader_name": sug.ministrador.name,
            }
        )
    return {"escala": escala, "equipe": equipe, "programa": programa}
