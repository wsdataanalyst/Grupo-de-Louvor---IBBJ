"""Helpers para rerun parcial (Fase 5 — fragments)."""

from __future__ import annotations


def rerun_scope_fragment() -> None:
    import streamlit as st

    try:
        st.rerun(scope="fragment")
    except (TypeError, ValueError):
        st.rerun()
