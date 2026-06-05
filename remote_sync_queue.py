"""Fila de upload Supabase — grava local primeiro, nuvem em background (Fase 6)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

_QUEUE_KEY = "_remote_push_queue"
_FAILED_KEY = "_remote_push_last_failures"


def enqueue_remote_push(file_path: Path) -> None:
    path = Path(file_path)
    if not path.name:
        return
    queued = set(st.session_state.get(_QUEUE_KEY, []))
    queued.add(path.name)
    st.session_state[_QUEUE_KEY] = sorted(queued)


def flush_remote_push_queue(*, max_items: int = 4) -> int:
    """Envia até max_items CSVs pendentes. Retorna quantos subiram com sucesso."""
    from remote_store import is_remote_enabled, push_file_from_disk, should_sync_file

    if not is_remote_enabled():
        st.session_state[_QUEUE_KEY] = []
        return 0

    names = list(st.session_state.get(_QUEUE_KEY, []))
    if not names:
        return 0

    data_dir = Path("data")
    pushed = 0
    remaining: list[str] = []
    failures: list[str] = []

    for name in names[:max_items]:
        path = data_dir / name
        if not path.is_file() or not should_sync_file(path):
            continue
        try:
            if push_file_from_disk(path):
                pushed += 1
            else:
                failures.append(name)
                remaining.append(name)
        except Exception:
            failures.append(name)
            remaining.append(name)

    for name in names[max_items:]:
        remaining.append(name)

    st.session_state[_QUEUE_KEY] = remaining
    if failures:
        st.session_state[_FAILED_KEY] = failures[:3]
    elif pushed:
        st.session_state.pop(_FAILED_KEY, None)
    return pushed


def pending_remote_push_count() -> int:
    return len(st.session_state.get(_QUEUE_KEY, []))
