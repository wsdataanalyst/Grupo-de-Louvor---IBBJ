"""Imagens simples para posts do feed."""

from __future__ import annotations

import io
from pathlib import Path


def generate_novo_louvor_banner(title: str, out_dir: Path) -> str:
    """Gera PNG e retorna caminho relativo em data/feed_images/."""
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in title[:40])
    rel = f"feed_images/novo_louvor_{safe}.png"
    path = out_dir.parent / rel if str(out_dir).endswith("feed_images") else out_dir / rel.split("/")[-1]

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return ""

    w, h = 900, 480
    img = Image.new("RGB", (w, h), color=(30, 20, 50))
    draw = ImageDraw.Draw(img)
    try:
        font_l = ImageFont.truetype("arial.ttf", 42)
        font_s = ImageFont.truetype("arial.ttf", 26)
    except OSError:
        font_l = ImageFont.load_default()
        font_s = font_l

    draw.rectangle([(0, 0), (w, 8)], fill=(251, 191, 36))
    draw.text((40, 60), "Tem louvor novo na área!!", fill=(251, 191, 36), font=font_l)
    draw.text(
        (40, 140),
        "Clique e confira a nova música do",
        fill=(233, 213, 255),
        font=font_s,
    )
    draw.text((40, 180), "repertório do GDL.", fill=(233, 213, 255), font=font_s)
    draw.text((40, 260), title[:55], fill=(255, 255, 255), font=font_s)
    draw.text((40, h - 50), "🎶 Grupo de Louvor - IBBJ", fill=(167, 139, 250), font=font_s)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    full = out_dir / f"novo_louvor_{safe}.png"
    full.write_bytes(buf.getvalue())
    return f"feed_images/{full.name}"
