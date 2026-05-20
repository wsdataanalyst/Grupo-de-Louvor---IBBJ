"""Compositor de chat estilo WhatsApp — componente Streamlit."""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

_FRONTEND_DIR = (Path(__file__).parent / "frontend").resolve()

_component = components.declare_component(
    "ibbj_wa_composer",
    path=str(_FRONTEND_DIR),
)


def whatsapp_composer(*, key: str | None = None, default=None):
    return _component(key=key, default=default)
