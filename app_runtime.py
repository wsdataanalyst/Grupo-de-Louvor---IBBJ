"""Resolve funções do app principal quando Streamlit executa app.py como __main__."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any


def main_app_module() -> ModuleType:
    """
    Retorna o módulo carregado do app.

    Com `streamlit run app.py`, o código vive em ``__main__`` — não em ``app``.
    Imports ``from app import …`` em fragments podem falhar no Cloud; use este helper.
    """
    for key in ("app", "__main__"):
        mod = sys.modules.get(key)
        if mod is None:
            continue
        file_name = str(getattr(mod, "__file__", "") or "")
        if key == "__main__" and file_name and not file_name.replace("\\", "/").endswith(
            ("app.py", "/app.py")
        ):
            continue
        if hasattr(mod, "load_chat_df"):
            return mod
    raise ImportError(
        "Módulo principal do app não encontrado. Execute com: streamlit run app.py"
    )


def getattr_app(name: str) -> Any:
    return getattr(main_app_module(), name)


def import_from_main_app(*names: str) -> tuple[Any, ...]:
    mod = main_app_module()
    return tuple(getattr(mod, n) for n in names)
