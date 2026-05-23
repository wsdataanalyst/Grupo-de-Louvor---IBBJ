"""Agendamento de posts no feed (orações diárias, escala da semana)."""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime, time, timedelta

import pandas as pd

FEED_QUEUE_COLUMNS = (
    "id",
    "kind",
    "title",
    "body",
    "youtube_url",
    "image_url",
    "ref_id",
    "publish_at",
    "published",
    "author_email",
    "author_name",
)

_PRAYER_VERSES = [
    ("Segunda", "Salmo 5:3", "Senhor, pela manhã ouves a minha voz; à tarde apresento minha oração."),
    ("Terça", "Filipenses 4:6", "Em tudo, por oração e súplica, com ação de graças, apresentem os pedidos a Deus."),
    ("Quarta", "Salmo 27:4", "Uma coisa peço ao Senhor: habitar no santuário para contemplar a beleza do Senhor."),
    ("Quinta", "Colossenses 3:16", "Habite ricamente em vocês a palavra de Cristo; com louvor cantem ao Senhor."),
    ("Sexta", "Isaías 40:31", "Os que esperam no Senhor renovam as forças e sobem com asas como águias."),
    ("Sábado", "Salmo 150:6", "Tudo o que tem fôlego louve ao Senhor. Prepare o coração para o culto."),
    ("Domingo", "João 4:23-24", "Os verdadeiros adoradores adoram o Pai em espírito e em verdade."),
]


def _new_id() -> str:
    return str(uuid.uuid4())


def schedule_culto_prayers(
    *,
    escala_id: str,
    event: str,
    culto_date: date,
    themes: list[str],
    louvor_titles: list[str],
) -> list[dict]:
    """7 orações: uma por dia até o culto, publicar às 06:00."""
    rows = []
    tema_txt = ", ".join(themes[:3]) if themes else "adoração"
    musicas = ", ".join(louvor_titles[:4]) if louvor_titles else "louvores do culto"
    days_until = (culto_date - date.today()).days
    if days_until < 0:
        return rows
    span = min(7, max(1, days_until + 1))
    for i in range(span):
        pub_day = date.today() + timedelta(days=i)
        if pub_day > culto_date:
            break
        dia_nome, ref, texto = _PRAYER_VERSES[i % 7]
        publish_at = datetime.combine(pub_day, time(6, 0)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append(
            {
                "id": _new_id(),
                "kind": "oracao_culto",
                "title": f"🙏 Oração do dia — {event} ({dia_nome})",
                "body": (
                    f"**{ref}** — {texto}\n\n"
                    f"Culto *{event}* em {culto_date.strftime('%d/%m/%Y')}. "
                    f"Temas: {tema_txt}. Louvores: {musicas}.\n\n"
                    f"Ore com a equipe e prepare o coração para adorar."
                ),
                "youtube_url": "",
                "image_url": "",
                "ref_id": escala_id,
                "publish_at": publish_at,
                "published": "0",
                "author_email": "sistema@gdl.ibbj",
                "author_name": "Ministério de Louvor",
            }
        )
    return rows


def schedule_weekly_team_post(
    *,
    escala_id: str,
    event: str,
    culto_date: date,
    ensaio_txt: str,
    team_html_body: str,
) -> dict:
    publish_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "id": _new_id(),
        "kind": "escala_semana",
        "title": f"📋 Time escalado — {event}",
        "body": (
            f"**Culto:** {culto_date.strftime('%d/%m/%Y')}\n\n"
            f"**Ensaio:** {ensaio_txt or 'a confirmar'}\n\n"
            f"{team_html_body}\n\n"
            "Deixe o grupo animado — confirme presença no ensaio!"
        ),
        "youtube_url": "",
        "image_url": "",
        "ref_id": escala_id,
        "publish_at": publish_at,
        "published": "0",
        "author_email": "sistema@gdl.ibbj",
        "author_name": "Ministério de Louvor",
    }


def merge_queue(existing: pd.DataFrame, new_rows: list[dict]) -> pd.DataFrame:
    if not new_rows:
        return existing
    df_new = pd.DataFrame(new_rows)
    if existing.empty:
        return df_new
    ref_ids = {str(r.get("ref_id", "")) + str(r.get("kind", "")) for r in new_rows}
    if "ref_id" in existing.columns and "kind" in existing.columns:
        mask = existing.apply(
            lambda row: (str(row.get("ref_id", "")) + str(row.get("kind", ""))) not in ref_ids,
            axis=1,
        )
        existing = existing[mask]
    return pd.concat([existing, df_new], ignore_index=True)


def process_due_posts(
    queue_df: pd.DataFrame,
    append_feed_post_fn,
) -> pd.DataFrame:
    """Publica itens com publish_at <= agora e published=0."""
    if queue_df.empty:
        return queue_df
    now = datetime.now()
    for idx, row in queue_df.iterrows():
        if str(row.get("published", "0")).strip() in ("1", "true", "sim"):
            continue
        pub = pd.to_datetime(row.get("publish_at"), errors="coerce")
        if pd.isna(pub) or pub.to_pydatetime() > now:
            continue
        append_feed_post_fn(
            post_type=str(row.get("kind", "comunicado")),
            title=str(row.get("title", "")),
            body=str(row.get("body", "")),
            youtube_url=str(row.get("youtube_url", "")),
            author_email=str(row.get("author_email", "")),
            author_name=str(row.get("author_name", "Ministério")),
            image_url=str(row.get("image_url", "")),
            ref_id=str(row.get("ref_id", "")),
        )
        queue_df.at[idx, "published"] = "1"
    return queue_df
