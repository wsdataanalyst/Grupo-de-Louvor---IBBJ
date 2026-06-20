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
import os
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

TABLE_NAME = "data_files"

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


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    if text in ("0", "false", "no", "off", "nao", "não", ""):
        return False
    return text in ("1", "true", "yes", "on", "sim")


def _normalize_url(url: str) -> str:
    return str(url or "").strip().rstrip("/")


def _persistence_secrets() -> dict:
    """Lê [persistence] ou chaves planas no secrets / variáveis de ambiente."""
    merged: dict = {}

    try:
        import streamlit as st

        raw = st.secrets.get("persistence", None)
        if raw is not None:
            try:
                merged.update(dict(raw))
            except Exception:
                pass

        for key in ("enabled", "supabase_url", "supabase_key"):
            if key not in merged or not str(merged.get(key, "")).strip():
                val = st.secrets.get(key, None)
                if val is not None and str(val).strip():
                    merged[key] = val

        if not merged.get("supabase_url"):
            alt_url = st.secrets.get("SUPABASE_URL")
            if alt_url:
                merged["supabase_url"] = alt_url
        if not merged.get("supabase_key"):
            alt_key = st.secrets.get("SUPABASE_SERVICE_KEY") or st.secrets.get(
                "SUPABASE_KEY"
            )
            if alt_key:
                merged["supabase_key"] = alt_key
        if "enabled" not in merged:
            pe = st.secrets.get("persistence_enabled") or st.secrets.get(
                "PERSISTENCE_ENABLED"
            )
            if pe is not None:
                merged["enabled"] = pe
    except Exception:
        pass

    if not merged.get("supabase_url"):
        merged["supabase_url"] = os.environ.get("SUPABASE_URL", "")
    if not merged.get("supabase_key"):
        merged["supabase_key"] = os.environ.get("SUPABASE_SERVICE_KEY", "") or os.environ.get(
            "SUPABASE_KEY", ""
        )
    if "enabled" not in merged:
        merged["enabled"] = os.environ.get("PERSISTENCE_ENABLED", "")

    return merged


def is_remote_enabled() -> bool:
    p = _persistence_secrets()
    if not _truthy(p.get("enabled")):
        return False
    url = _normalize_url(str(p.get("supabase_url", "")))
    key = str(p.get("supabase_key", "")).strip()
    return bool(url and key and url.startswith("http"))


def _get_credentials() -> tuple[str, str]:
    p = _persistence_secrets()
    return _normalize_url(str(p.get("supabase_url", ""))), str(p.get("supabase_key", "")).strip()


def _get_client():
    from supabase import create_client

    url, key = _get_credentials()
    return create_client(url, key)


def remote_config_hint() -> str:
    """Texto curto sobre o que falta na configuração."""
    p = _persistence_secrets()
    if not _truthy(p.get("enabled")):
        return (
            "Adicione no Secrets do Streamlit a seção `[persistence]` com "
            "`enabled = true` (veja CONFIGURAR_SUPABASE.md)."
        )
    url, key = _get_credentials()
    if not url:
        return "Falta `supabase_url` em `[persistence]`."
    if not key:
        return "Falta `supabase_key` (use a chave **service_role**, não a anon)."
    if not url.startswith("http"):
        return "`supabase_url` inválida — deve começar com https://"
    if len(key) < 40:
        return "A `supabase_key` parece curta demais — confira se copiou a **service_role** inteira."
    return ""


def test_remote_connection() -> tuple[bool, str]:
    if not is_remote_enabled():
        hint = remote_config_hint()
        return False, hint or "Persistência na nuvem desativada."

    try:
        client = _get_client()
        client.table(TABLE_NAME).select("name").limit(1).execute()
        probe = {
            "name": "__connection_test__",
            "content": "ok",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        client.table(TABLE_NAME).upsert(probe).execute()
        client.table(TABLE_NAME).delete().eq("name", "__connection_test__").execute()
        return True, "Conexão OK — Supabase respondeu e a tabela data_files existe."
    except Exception as exc:
        msg = str(exc).strip() or exc.__class__.__name__
        low = msg.lower()
        if "data_files" in low and ("does not exist" in low or "pgrst205" in low):
            return (
                False,
                "Tabela `data_files` não existe. Rode o SQL de `supabase/schema.sql` no "
                "Supabase (SQL Editor → Run).",
            )
        if "invalid" in low and ("api key" in low or "jwt" in low):
            return (
                False,
                "Chave inválida — use a **service_role** em Project Settings → API "
                "(não use a chave anon).",
            )
        if "401" in low or "unauthorized" in low:
            return False, "Não autorizado (401) — chave errada ou expirada."
        return False, f"Erro ao conectar: {msg}"


def remote_status_message() -> str:
    if not _truthy(_persistence_secrets().get("enabled")):
        return "Nuvem desativada — `[persistence] enabled = true` não está no Secrets."
    if not is_remote_enabled():
        return f"Nuvem incompleta — {remote_config_hint()}"
    ok, detail = test_remote_connection()
    if ok:
        return "Nuvem conectada (Supabase) — cadastros sincronizam automaticamente."
    return f"Supabase desconectado — {detail}"


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


def should_sync_file(file_path: Path) -> bool:
    """Retorna True para arquivos CSV que devem ser sincronizados com Supabase."""
    return file_path.name in SYNC_CSV_NAMES


def store_csv_text(name: str, content: str) -> None:
    if name not in SYNC_CSV_NAMES:
        return
    payload = {
        "name": name,
        "content": content,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _get_client().table(TABLE_NAME).upsert(payload).execute()


def _local_file_has_data(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return path.stat().st_size > 0
    except OSError:
        return False


def pull_file_to_disk(file_path: Path) -> bool:
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
    count = 0
    for path in sorted(data_dir.glob("*.csv")):
        if path.name in SYNC_CSV_NAMES and push_file_from_disk(path):
            count += 1
    return count
