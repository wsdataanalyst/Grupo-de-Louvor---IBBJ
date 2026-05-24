"""Validação de letra/cifra importadas da web — critérios fixos (memória do app)."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

# Regras gravadas: só aceitar conteúdo que bate com título/URL da música pedida.
LYRICS_FETCH_RULES: dict[str, Any] = {
    "min_chars": 80,
    "min_lines": 4,
    "min_title_overlap": 0.45,
    "min_slug_overlap": 0.55,
    "max_chord_line_ratio": 0.35,
    "reject_if_looks_like_cifra_only": True,
}


def _norm_words(text: str) -> set[str]:
    raw = unicodedata.normalize("NFKD", str(text or "").lower())
    ascii_txt = "".join(c for c in raw if not unicodedata.combining(c))
    return {w for w in re.findall(r"[a-z0-9]{3,}", ascii_txt) if w not in _STOPWORDS}


_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "de",
        "da",
        "do",
        "dos",
        "das",
        "uma",
        "uns",
        "para",
        "por",
        "com",
        "que",
        "letra",
        "cifra",
        "musica",
        "music",
        "feat",
        "part",
    }
)


def slug_tokens(slug: str) -> set[str]:
    return {p for p in str(slug or "").split("-") if len(p) >= 2}


def title_overlap(expected_title: str, found_text: str) -> float:
    exp = _norm_words(expected_title)
    if not exp:
        return 1.0
    found = _norm_words(found_text)
    return len(exp & found) / len(exp)


def slug_overlap(expected_slug: str, url_slug: str) -> float:
    a = slug_tokens(expected_slug)
    b = slug_tokens(url_slug)
    if not a:
        return 1.0
    if not b:
        return 0.0
    return len(a & b) / len(a)


def song_slug_from_url(url: str) -> str:
    m = re.search(
        r"vagalume\.com\.br/[^/]+/([^/.?]+?)(?:-cifrada)?\.html",
        str(url or ""),
        re.I,
    )
    if m:
        return m.group(1).lower()
    m2 = re.search(r"e-chords\.com/chords/[^/]+/([^/?#]+)", str(url or ""), re.I)
    if m2:
        return m2.group(1).lower()
    return ""


def _chord_line_ratio(text: str) -> float:
    from cifra_fetch import _CHORD_TOKEN_RE

    lines = [ln.strip() for ln in str(text or "").splitlines() if ln.strip()]
    if not lines:
        return 0.0
    chord_lines = sum(1 for ln in lines if _CHORD_TOKEN_RE.search(ln))
    return chord_lines / len(lines)


def validate_fetched_lyrics(
    title: str,
    artist: str,
    lyrics: str,
    *,
    source_url: str = "",
    page_title: str = "",
    expected_slug: str = "",
) -> tuple[bool, str]:
    """
    Retorna (ok, motivo). Rejeita letra de música errada ou lixo de página.
    """
    text = str(lyrics or "").strip()
    if len(text) < LYRICS_FETCH_RULES["min_chars"]:
        return False, "letra muito curta"
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < LYRICS_FETCH_RULES["min_lines"]:
        return False, "poucas linhas de letra"

    try:
        from cifra_fetch import _looks_like_cifra

        if LYRICS_FETCH_RULES["reject_if_looks_like_cifra_only"] and _looks_like_cifra(text):
            return False, "conteúdo parece cifra, não letra"
    except ImportError:
        pass

    if _chord_line_ratio(text) > LYRICS_FETCH_RULES["max_chord_line_ratio"]:
        return False, "muitas linhas de acordes na letra"

    meta = str(page_title or "").strip()
    if meta:
        ov = title_overlap(title, meta)
        if ov < LYRICS_FETCH_RULES["min_title_overlap"]:
            return False, f"título da página não confere ({meta[:60]})"

    url_slug = song_slug_from_url(source_url)
    exp_slug = (expected_slug or "").strip().lower()
    if url_slug and exp_slug:
        so = slug_overlap(exp_slug, url_slug)
        if so < LYRICS_FETCH_RULES["min_slug_overlap"]:
            return False, f"URL não corresponde à música ({url_slug})"

    if title and not meta and not url_slug:
        ov_body = title_overlap(title, text[:600])
        if ov_body < 0.25 and len(_norm_words(title)) >= 2:
            return False, "letra não contém palavras do título da música"

    if artist:
        art_words = _norm_words(artist)
        if art_words and len(art_words) >= 2:
            body = _norm_words(text[:400])
            meta_words = _norm_words(meta)
            if art_words.isdisjoint(body) and art_words.isdisjoint(meta_words):
                pass

    return True, ""


def validate_fetched_cifra(
    title: str,
    cifra: str,
    *,
    source_url: str = "",
    expected_slug: str = "",
) -> tuple[bool, str]:
    text = str(cifra or "").strip()
    if len(text) < 40:
        return False, "cifra muito curta"
    try:
        from cifra_fetch import _looks_like_cifra

        if not _looks_like_cifra(text):
            return False, "texto não parece cifra"
    except ImportError:
        pass

    url_slug = song_slug_from_url(source_url)
    exp_slug = (expected_slug or "").strip().lower()
    if url_slug and exp_slug:
        so = slug_overlap(exp_slug, url_slug)
        if so < LYRICS_FETCH_RULES["min_slug_overlap"]:
            return False, f"URL da cifra não confere ({url_slug})"

    if title:
        ov = title_overlap(title, text[:400])
        if ov < 0.15 and len(_norm_words(title)) >= 2:
            return False, "cifra sem referência ao título"

    return True, ""
