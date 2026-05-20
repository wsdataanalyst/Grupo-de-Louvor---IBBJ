"""Barra de composição estilo WhatsApp (áudio segurar, anexos sob demanda)."""

from __future__ import annotations

import os

import streamlit.components.v1 as components

_DIR = os.path.dirname(os.path.abspath(__file__))
whatsapp_composer = components.declare_component(
    "whatsapp_composer",
    path=_DIR,
)
