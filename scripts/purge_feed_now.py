#!/usr/bin/env python3
"""Apaga todos os posts do feed (local + Supabase se configurado)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
FEED_POSTS = DATA_DIR / "feed_posts.csv"
FEED_LIKES = DATA_DIR / "feed_likes.csv"
FEED_COMMENTS = DATA_DIR / "feed_comments.csv"
FEED_QUEUE = DATA_DIR / "feed_queue.csv"

POST_COLS = (
    "id",
    "post_type",
    "title",
    "body",
    "youtube_url",
    "cifra_url",
    "ref_id",
    "author_email",
    "author_name",
    "created_at",
    "image_url",
)
LIKE_COLS = ("id", "post_id", "email", "created_at")
COMMENT_COLS = ("id", "post_id", "email", "name", "message", "created_at")
QUEUE_COLS = (
    "id",
    "kind",
    "title",
    "body",
    "youtube_url",
    "image_url",
    "ref_id",
    "publish_at",
    "published",
    "author_email",
    "author_name",
)


def _count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return max(0, len(pd.read_csv(path, encoding="utf-8")) - 0)
    except Exception:
        return 0


def _write_empty(path: Path, columns: tuple[str, ...]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=list(columns)).to_csv(path, index=False, encoding="utf-8")


def _push_remote(path: Path) -> bool:
    try:
        from remote_store import is_remote_enabled, push_file_from_disk, should_sync_file

        if should_sync_file(path) and is_remote_enabled():
            return bool(push_file_from_disk(path))
    except Exception as exc:
        print(f"  aviso nuvem ({path.name}): {exc}")
    return False


def main() -> int:
    before = _count_rows(FEED_POSTS)
    print(f"Posts no feed antes: {before}")

    for path, cols in (
        (FEED_POSTS, POST_COLS),
        (FEED_LIKES, LIKE_COLS),
        (FEED_COMMENTS, COMMENT_COLS),
        (FEED_QUEUE, QUEUE_COLS),
    ):
        _write_empty(path, cols)
        ok = _push_remote(path)
        print(f"  {path.name}: limpo" + (" + nuvem" if ok else ""))

    after = _count_rows(FEED_POSTS)
    print(f"Posts no feed depois: {after}")
    print("Concluído.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
