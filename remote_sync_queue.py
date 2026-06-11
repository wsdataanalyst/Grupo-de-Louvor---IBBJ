"""Fila de upload Supabase — grava local primeiro, nuvem em background (Fase 6)."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

_QUEUE_KEY = "_remote_push_queue"
_FAILED_KEY = "_remote_push_last_failures"
_QUEUE_FILE = Path("data") / ".remote_push_queue"


def _read_queue_file() -> list[str]:
    if not _QUEUE_FILE.is_file():
        return []
    try:
        lines = _QUEUE_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    return sorted({line.strip() for line in lines if line.strip()})


def _write_queue_file(names: list[str]) -> None:
    unique = sorted({str(n).strip() for n in names if str(n).strip()})
    try:
        _QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if unique:
            _QUEUE_FILE.write_text("\n".join(unique) + "\n", encoding="utf-8")
        elif _QUEUE_FILE.is_file():
            _QUEUE_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def init_remote_push_queue_from_disk() -> None:
    """Restaura fila pendente após reboot do Streamlit (session state vazio)."""
    disk = _read_queue_file()
    if not disk:
        return
    queued = set(st.session_state.get(_QUEUE_KEY, []))
    queued.update(disk)
    st.session_state[_QUEUE_KEY] = sorted(queued)


def enqueue_remote_push(file_path: Path) -> None:
    path = Path(file_path)
    if not path.name:
        return
    queued = set(st.session_state.get(_QUEUE_KEY, []))
    queued.add(path.name)
    merged = sorted(queued)
    st.session_state[_QUEUE_KEY] = merged
    _write_queue_file(merged)


def dequeue_remote_push(file_name: str) -> None:
    """Remove arquivo da fila após upload síncrono bem-sucedido."""
    name = str(file_name).strip()
    if not name:
        return
    queued = [n for n in st.session_state.get(_QUEUE_KEY, []) if n != name]
    st.session_state[_QUEUE_KEY] = queued
    disk = [n for n in _read_queue_file() if n != name]
    _write_queue_file(disk if disk else queued)


def flush_remote_push_queue(*, max_items: int = 4) -> int:
    """Envia até max_items CSVs pendentes. Retorna quantos subiram com sucesso."""
    from remote_store import is_remote_enabled, push_file_from_disk, should_sync_file

    init_remote_push_queue_from_disk()

    if not is_remote_enabled():
        st.session_state[_QUEUE_KEY] = []
        _write_queue_file([])
        return 0

    names = list(st.session_state.get(_QUEUE_KEY, []))
    if not names:
        names = _read_queue_file()
        if names:
            st.session_state[_QUEUE_KEY] = names
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
    _write_queue_file(remaining)
    if failures:
        st.session_state[_FAILED_KEY] = failures[:3]
    elif pushed:
        st.session_state.pop(_FAILED_KEY, None)
    return pushed


def pending_remote_push_count() -> int:
    init_remote_push_queue_from_disk()
    session_n = len(st.session_state.get(_QUEUE_KEY, []))
    disk_n = len(_read_queue_file())
    return max(session_n, disk_n)
