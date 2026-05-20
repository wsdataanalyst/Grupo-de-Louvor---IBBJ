"""
Persistência na nuvem (Supabase) — fonte oficial dos CSV em produção.

Configure em .streamlit/secrets.toml:

[persistence]
enabled = true
supabase_url = "https://xxxx.supabase.co"
supabase_key = "sua-service-role-key"
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

TABLE_NAME = "data_files"

# Dados do ministério (não versiona louvores do Git por padrão)
SYNC_CSV_NAMES = frozenset(
    {
        "members.csv",
        "escalas.csv",
        "trocas_escalas.csv",
        "programa_culto.csv",
        "escala_equipe.csv",
        "playlist.csv",
        "eventos.csv",
        "sugestoes_louvor.csv",
        "chat.csv",
        "chat_ensaio.csv",
        "password_reset_tokens.csv",
    }
)


def _persistence_secrets() -> dict:
    try:
        import streamlit as st

        raw = st.secrets.get("persistence", {})
        if isinstance(raw, dict):
            return raw
    except Exception:
        pass
    return {}


def is_remote_enabled() -> bool:
    p = _persistence_secrets()
    if not p.get("enabled"):
        return False
    url = str(p.get("supabase_url", "")).strip()
    key = str(p.get("supabase_key", "")).strip()
    return bool(url and key)


def should_sync_file(file_path: Path) -> bool:
    return file_path.name in SYNC_CSV_NAMES


def remote_status_message() -> str:
    if not is_remote_enabled():
        return "Nuvem desativada (só disco local)."
    try:
        _get_client().table(TABLE_NAME).select("name").limit(1).execute()
        return "Nuvem conectada (Supabase) — cadastros sincronizam automaticamente."
    except Exception as exc:
        return f"Nuvem configurada, mas falhou ao conectar: {exc}"


def _get_client():
    from supabase import create_client

    p = _persistence_secrets()
    return create_client(
        str(p["supabase_url"]).strip(),
        str(p["supabase_key"]).strip(),
    )


def fetch_csv_text(name: str) -> str | None:
    if name not in SYNC_CSV_NAMES:
        return None
    res = (
        _get_client()
        .table(TABLE_NAME)
        .select("content")
        .eq("name", name)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    if not rows:
        return None
    content = rows[0].get("content")
    if content is None:
        return None
    return str(content)


def store_csv_text(name: str, content: str) -> None:
    if name not in SYNC_CSV_NAMES:
        return
    payload = {
        "name": name,
        "content": content,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _get_client().table(TABLE_NAME).upsert(payload, on_conflict="name").execute()


def _local_file_has_data(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return path.stat().st_size > 0
    except OSError:
        return False


def pull_file_to_disk(file_path: Path) -> bool:
    """Baixa CSV da nuvem para o disco local. Retorna True se trouxe dados."""
    name = file_path.name
    try:
        text = fetch_csv_text(name)
    except Exception as exc:
        logger.warning("pull %s: %s", name, exc)
        return False
    if not text or not str(text).strip():
        return False
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")
    return True


def push_file_from_disk(file_path: Path) -> bool:
    """Envia CSV local para a nuvem."""
    if not _local_file_has_data(file_path):
        return False
    try:
        store_csv_text(file_path.name, file_path.read_text(encoding="utf-8"))
        return True
    except Exception as exc:
        logger.warning("push %s: %s", file_path.name, exc)
        return False


def dataframe_from_remote(columns: tuple, name: str) -> pd.DataFrame | None:
    try:
        text = fetch_csv_text(name)
    except Exception:
        return None
    if not text or not str(text).strip():
        return None
    try:
        df = pd.read_csv(StringIO(text))
    except Exception:
        return None
    empty = pd.DataFrame(columns=list(columns))
    if df.empty:
        return empty
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    return df[list(columns)].copy()


def sync_all_local_to_remote(data_dir: Path) -> int:
    """Envia todos os CSV locais com dados para a nuvem (migração inicial)."""
    count = 0
    for path in sorted(data_dir.glob("*.csv")):
        if path.name in SYNC_CSV_NAMES and push_file_from_disk(path):
            count += 1
    return count
