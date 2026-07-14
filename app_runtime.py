"""Resolve funções do app principal quando Streamlit executa app.py como __main__."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any


def _candidate_app_modules() -> list[ModuleType]:
    """
    Módulos que podem ser o app.py principal.

    Preferimos __main__ (streamlit run app.py) antes de app, porque no Cloud
    ``import app`` pode ficar incompleto e faltar funções como save_data.
    """
    found: list[ModuleType] = []
    for key in ("__main__", "app"):
        mod = sys.modules.get(key)
        if mod is None:
            continue
        file_name = str(getattr(mod, "__file__", "") or "").replace("\\", "/")
        if key == "__main__" and file_name and not file_name.endswith("app.py"):
            continue
        if mod not in found:
            found.append(mod)
    return found


def main_app_module() -> ModuleType:
    for mod in _candidate_app_modules():
        if hasattr(mod, "save_data"):
            return mod
    raise ImportError(
        "Módulo principal do app não encontrado. Execute com: streamlit run app.py"
    )


def getattr_app(name: str) -> Any:
    for mod in _candidate_app_modules():
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AttributeError(
        f"Nenhum módulo app/__main__ define '{name}'. "
        "Confira se o deploy usa a branch mobile-lab atualizada."
    )


def import_from_main_app(*names: str) -> tuple[Any, ...]:
    out: list[Any] = []
    for n in names:
        out.append(getattr_app(n))
    return tuple(out)
