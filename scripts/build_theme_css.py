#!/usr/bin/env python3
"""Gera CSS estático para cache do navegador (Fase 5)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    from app_theme import compile_ibbj_theme_css
    from mobile_lab_ui import mobile_lab_css

    STATIC.mkdir(parents=True, exist_ok=True)

    ibbj = compile_ibbj_theme_css()
    mobile = mobile_lab_css()

    (STATIC / "ibbj_theme.css").write_text(ibbj, encoding="utf-8")
    (STATIC / "mobile_lab_theme.css").write_text(mobile, encoding="utf-8")

    print(f"static/ibbj_theme.css — {len(ibbj) / 1024:.1f} KB")
    print(f"static/mobile_lab_theme.css — {len(mobile) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
