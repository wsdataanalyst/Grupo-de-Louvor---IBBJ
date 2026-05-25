"""Proteção de dados locais (CSVs) — backups e gravação segura."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

MAX_BACKUPS_PER_FILE = 15
MEMBERS_GUARD_MIN_ROWS = 1
MEMBERS_DROP_RATIO_LIMIT = 0.5

MEMBER_STRING_COLUMNS = (
    "first_name",
    "last_name",
    "email",
    "roles",
    "password_hash",
    "created_at",
    "profile_photo",
    "phone",
    "bio",
)

MEMBER_STRING_COLUMNS = (
    "first_name",
    "last_name",
    "email",
    "roles",
    "password_hash",
    "created_at",
    "profile_photo",
    "phone",
    "bio",
)


def prepare_members(df: pd.DataFrame) -> pd.DataFrame:
    """Garante colunas de texto (evita profile_photo como float64 / NaN)."""
    if df.empty:
        return pd.DataFrame(columns=list(MEMBER_STRING_COLUMNS))
    out = df.copy()
    for column in MEMBER_STRING_COLUMNS:
        if column not in out.columns:
            out[column] = ""
        out[column] = out[column].fillna("").astype(str).str.strip()
    out["email"] = out["email"].str.lower()
    return out[list(MEMBER_STRING_COLUMNS)].copy()


def backup_dir_for(data_dir: Path) -> Path:
    return data_dir / "backups"


def backup_csv_if_exists(file_path: Path, data_dir: Path) -> Path | None:
    """Cópia datada antes de sobrescrever um CSV."""
    if not file_path.exists():
        return None
    try:
        if file_path.stat().st_size == 0:
            return None
    except OSError:
        return None

    dest_root = backup_dir_for(data_dir)
    dest_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = dest_root / f"{file_path.stem}_{stamp}{file_path.suffix}"
    shutil.copy2(file_path, dest)
    _prune_old_backups(dest_root, file_path.stem, file_path.suffix)
    return dest


def _prune_old_backups(folder: Path, stem: str, suffix: str) -> None:
    pattern = f"{stem}_*{suffix}"
    files = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in files[MAX_BACKUPS_PER_FILE:]:
        try:
            old.unlink(missing_ok=True)
        except OSError:
            pass


def latest_backup(file_path: Path, data_dir: Path) -> Path | None:
    folder = backup_dir_for(data_dir)
    if not folder.exists():
        return None
    files = sorted(
        folder.glob(f"{file_path.stem}_*{file_path.suffix}"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def _member_cell_to_str(value) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    return "" if text.lower() in ("nan", "none", "<na>") else text


def prepare_members(df: pd.DataFrame) -> pd.DataFrame:
    """Garante colunas de texto (evita profile_photo como float64 por células vazias)."""
    if df.empty:
        return pd.DataFrame(columns=list(MEMBER_STRING_COLUMNS))
    out = df.copy()
    for column in MEMBER_STRING_COLUMNS:
        if column not in out.columns:
            out[column] = ""
        else:
            out[column] = out[column].map(_member_cell_to_str)
    out["email"] = out["email"].astype(str).str.strip().str.lower()
    return out[list(MEMBER_STRING_COLUMNS)].copy()


def load_csv_preserve_rows(file_path: Path, columns: tuple) -> pd.DataFrame:
    """
    Carrega CSV sem descartar linhas por erro de coluna.
    Em falha de leitura, tenta o backup mais recente.
    """
    empty = pd.DataFrame(columns=list(columns))
    if not file_path.exists():
        return empty

    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return empty
        for column in columns:
            if column not in df.columns:
                df[column] = ""
        return df[list(columns)].copy()

    try:
        return _normalize(pd.read_csv(file_path))
    except pd.errors.EmptyDataError:
        return empty
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError):
        backup = latest_backup(file_path, file_path.parent)
        if backup and backup.exists():
            try:
                return _normalize(pd.read_csv(backup))
            except Exception:
                pass
        try:
            return _normalize(pd.read_csv(file_path, on_bad_lines="skip"))
        except Exception:
            return empty


def members_save_allowed(
    new_df: pd.DataFrame,
    file_path: Path,
    *,
    force: bool = False,
) -> tuple[bool, str]:
    """
    Impede gravar members.csv com muito menos contas por engano
    (ex.: leitura vazia após deploy).
    """
    if force:
        return True, ""
    new_count = len(new_df)
    if new_count >= MEMBERS_GUARD_MIN_ROWS:
        if not file_path.exists():
            return True, ""
        try:
            old = pd.read_csv(file_path)
        except Exception:
            return True, ""
        old_count = len(old)
        if old_count <= MEMBERS_GUARD_MIN_ROWS:
            return True, ""
        if new_count < old_count * MEMBERS_DROP_RATIO_LIMIT:
            return (
                False,
                f"Proteção de dados: o arquivo tinha {old_count} conta(s) e a gravação "
                f"só teria {new_count}. Nada foi apagado. Recarregue a página ou "
                "restaure de data/backups/.",
            )
    return True, ""


def snapshot_data_folder(data_dir: Path, label: str = "startup") -> Path | None:
    """Backup leve de todos os CSVs na pasta data/ (início do app)."""
    if not data_dir.exists():
        return None
    csv_files = [p for p in data_dir.glob("*.csv") if p.is_file()]
    if not csv_files:
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = backup_dir_for(data_dir) / f"snapshot_{label}_{stamp}"
    folder.mkdir(parents=True, exist_ok=True)
    for src in csv_files:
        shutil.copy2(src, folder / src.name)
    return folder
