"""Áudio, imagem e mídia para chats (grupo e ensaio)."""

from __future__ import annotations

import io
import uuid
from pathlib import Path

CHAT_MEDIA_COLUMNS_EXTRA = ("message_type", "media_file")

AUDIO_EXTS = {".webm", ".ogg", ".mp3", ".m4a", ".wav", ".mp4", ".aac"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif"}


def ensure_chat_media_columns(df, base_columns: tuple):
    import pandas as pd

    cols = list(base_columns)
    for c in CHAT_MEDIA_COLUMNS_EXTRA:
        if c not in cols:
            cols.append(c)
    if df.empty:
        return pd.DataFrame(columns=cols)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df[list(cols)].copy()


def _save_bytes(
    raw: bytes,
    target_dir: Path,
    *,
    prefix: str,
    ext: str,
    data_dir: Path,
) -> str:
    target_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{prefix}_{uuid.uuid4().hex[:12]}{ext}"
    path = target_dir / fname
    path.write_bytes(raw)
    rel = path.relative_to(data_dir)
    return str(rel).replace("\\", "/")


def save_audio_upload(
    uploaded_file,
    target_dir: Path,
    *,
    prefix: str,
    data_dir: Path,
) -> str:
    """Salva upload de áudio e retorna caminho relativo à pasta data/."""
    name = uploaded_file.name or "audio.webm"
    ext = Path(name).suffix.lower() or ".webm"
    if ext not in AUDIO_EXTS:
        ext = ".webm"
    return _save_bytes(
        uploaded_file.getvalue(), target_dir, prefix=prefix, ext=ext, data_dir=data_dir
    )


def save_image_upload(
    uploaded_file,
    target_dir: Path,
    *,
    prefix: str,
    data_dir: Path,
) -> str:
    """Salva foto (galeria ou câmera) em JPEG quando possível."""
    raw = uploaded_file.getvalue()
    name = getattr(uploaded_file, "name", None) or "foto.jpg"
    ext = Path(name).suffix.lower() or ".jpg"
    if ext not in IMAGE_EXTS:
        ext = ".jpg"
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(raw))
        img = img.convert("RGB")
        img.thumbnail((1600, 1600))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=88, optimize=True)
        return _save_bytes(
            buf.getvalue(), target_dir, prefix=prefix, ext=".jpg", data_dir=data_dir
        )
    except Exception:
        return _save_bytes(raw, target_dir, prefix=prefix, ext=ext, data_dir=data_dir)


def media_absolute_path(relative_path: str, data_dir: Path) -> Path | None:
    rel = str(relative_path).strip().replace("\\", "/")
    if not rel:
        return None
    if rel.startswith("data/"):
        rel = rel[5:]
    p = data_dir / rel
    return p if p.exists() else None
