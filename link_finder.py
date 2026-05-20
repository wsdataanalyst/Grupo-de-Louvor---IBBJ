"""Busca links reais de YouTube e Cifra Club na internet."""

from __future__ import annotations

import re
import time
from urllib.parse import quote_plus, unquote, urlparse, parse_qs

SEARCH_DELAY_SEC = 0.35


def is_direct_url(value: str) -> bool:
    v = str(value).strip().lower()
    if not v.startswith("http"):
        return False
    if "search_query=" in v or "cifraclub.com.br/?q=" in v:
        return False
    return True


def _query(title: str, artist: str) -> str:
    from catalog_sanitize import sanitize_catalog_text

    parts = [sanitize_catalog_text(title), sanitize_catalog_text(artist)]
    return " ".join(p for p in parts if p)


def _normalize_youtube(url: str) -> str | None:
    u = unquote(str(url).strip())
    if "youtu.be/" in u:
        m = re.search(r"youtu\.be/([A-Za-z0-9_-]{6,})", u)
        if m:
            return f"https://www.youtube.com/watch?v={m.group(1)}"
    if "youtube.com" in u:
        parsed = urlparse(u)
        if parsed.path.startswith("/watch"):
            vid = parse_qs(parsed.query).get("v", [""])[0]
            if vid:
                return f"https://www.youtube.com/watch?v={vid}"
        m = re.search(r"/shorts/([A-Za-z0-9_-]{6,})", u)
        if m:
            return f"https://www.youtube.com/watch?v={m.group(1)}"
    return None


def _normalize_cifra(url: str) -> str | None:
    u = str(url).strip()
    if "cifraclub.com.br" not in u.lower():
        return None
    if "/?q=" in u or u.rstrip("/").endswith("cifraclub.com.br"):
        return None
    if any(
        seg in u.lower()
        for seg in ("/letra/", "/tabs-", "/blog/", "/aprenda/", "/professor/")
    ):
        return None
    return u.split("#")[0].rstrip("/") + "/" if "/letras" not in u else u


def _ddg_search(query: str, *, max_results: int = 10) -> list[str]:
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
    except ImportError:
        return []
    urls: list[str] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                href = str(item.get("href") or item.get("link") or "").strip()
                if href.startswith("http"):
                    urls.append(href)
    except Exception:
        pass
    return urls


def find_youtube_url(title: str, artist: str = "") -> str | None:
    q = _query(title, artist)
    if not q:
        return None
    for query in (f"{q} louvor gospel youtube", f"{q} youtube"):
        for url in _ddg_search(query, max_results=12):
            yt = _normalize_youtube(url)
            if yt:
                time.sleep(SEARCH_DELAY_SEC)
                return yt
        time.sleep(SEARCH_DELAY_SEC)
    return None


def find_cifra_url(title: str, artist: str = "") -> str | None:
    q = _query(title, artist)
    if not q:
        return None
    candidates: list[str] = []
    for query in (f"{q} cifra site:cifraclub.com.br", f"cifraclub {q} cifra"):
        candidates.extend(_ddg_search(query, max_results=12))
        time.sleep(SEARCH_DELAY_SEC)
    for url in candidates:
        cif = _normalize_cifra(url)
        if cif:
            return cif
    return None


def fallback_youtube_search(title: str, artist: str = "") -> str:
    q = quote_plus(_query(title, artist))
    return f"https://www.youtube.com/results?search_query={q}"


def fallback_cifra_search(title: str, artist: str = "") -> str:
    q = quote_plus(_query(title, artist))
    return f"https://www.cifraclub.com.br/?q={q}"
