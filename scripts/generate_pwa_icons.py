"""Gera ícones PNG para PWA (static/icon-192.png e icon-512.png)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), "#1a1530")
    draw = ImageDraw.Draw(img)
    margin = size // 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 10,
        fill="#2d1b4e",
        outline="#fbbf24",
        width=max(2, size // 64),
    )
    font_size = size // 3
    try:
        font = ImageFont.truetype("segoeui.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()
    draw.text((size // 2, size // 2), "♪", fill="#fbbf24", font=font, anchor="mm")
    return img


def main():
    STATIC.mkdir(parents=True, exist_ok=True)
    make_icon(192).save(STATIC / "icon-192.png", "PNG")
    make_icon(512).save(STATIC / "icon-512.png", "PNG")
    print("Ícones salvos em", STATIC)


if __name__ == "__main__":
    main()
