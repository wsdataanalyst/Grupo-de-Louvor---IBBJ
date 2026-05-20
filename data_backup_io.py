"""Exportar e restaurar a pasta data/ (cadastros, escalas, chat, etc.)."""

from __future__ import annotations

import io
import zipfile
from datetime import datetime
from pathlib import Path

from data_persistence import backup_csv_if_exists, snapshot_data_folder


def list_data_csv_files(data_dir: Path) -> list[Path]:
    return sorted(p for p in data_dir.glob("*.csv") if p.is_file())


def build_data_backup_zip(data_dir: Path) -> bytes:
    """ZIP com CSVs e fotos de perfil para download manual."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in list_data_csv_files(data_dir):
            zf.write(path, arcname=f"data/{path.name}")
        photos = data_dir / "profile_photos"
        if photos.is_dir():
            for photo in sorted(photos.iterdir()):
                if photo.is_file():
                    zf.write(photo, arcname=f"data/profile_photos/{photo.name}")
        readme = (
            "Backup do Grupo de Louvor IBBJ\n"
            f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "Restaure pelo menu desenvolvedor: Backup / restaurar dados.\n"
        )
        zf.writestr("LEIA-ME.txt", readme)
    buf.seek(0)
    return buf.getvalue()


def restore_data_from_zip(data_dir: Path, zip_bytes: bytes) -> tuple[int, list[str]]:
    """
    Restaura arquivos do ZIP em data/.
    Aceita caminhos data/arquivo.csv, profile_photos/foto.jpg ou só o nome do CSV.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    snapshot_data_folder(data_dir, label="antes_restaurar")
    restored = 0
    notes: list[str] = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if "__MACOSX" in name or name.endswith("/"):
                continue

            lower = name.lower()
            if "profile_photos/" in lower:
                idx = lower.rfind("profile_photos/")
                fname = name[idx + len("profile_photos/") :]
                if not fname or "/" in fname:
                    notes.append(f"Ignorado: {name}")
                    continue
                dest = data_dir / "profile_photos" / fname
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(info))
                restored += 1
                continue

            base = Path(name).name
            if not base.endswith(".csv"):
                notes.append(f"Ignorado: {name}")
                continue

            dest = data_dir / base
            if dest.exists():
                backup_csv_if_exists(dest, data_dir)
            dest.write_bytes(zf.read(info))
            restored += 1

    return restored, notes
