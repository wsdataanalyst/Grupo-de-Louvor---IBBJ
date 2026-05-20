"""Links de kit de voz no YouTube por nipe vocal e música do culto."""

from __future__ import annotations

from urllib.parse import quote_plus

ROLE_TO_NIPE: dict[str, str] = {
    "Vocalista - Contralto": "Contralto",
    "Vocalista - Soprano": "Soprano",
    "Vocalista - Tenor": "Tenor",
    "Vocalista - Baritono": "Baritono",
    "Vocalista - Mezzo Soprano": "Mezzo Soprano",
}

_BIO_NIPE_HINTS: tuple[tuple[str, str], ...] = (
    ("mezzo soprano", "Mezzo Soprano"),
    ("mezzo-soprano", "Mezzo Soprano"),
    ("contralto", "Contralto"),
    ("soprano", "Soprano"),
    ("baritono", "Baritono"),
    ("barítono", "Baritono"),
    ("tenor", "Tenor"),
)


def vocal_nipe_from_roles(roles: str, bio: str = "") -> str | None:
    parts = [p.strip() for p in str(roles).split(",") if p.strip()]
    for role in parts:
        if role in ROLE_TO_NIPE:
            return ROLE_TO_NIPE[role]
    low = str(roles).lower()
    for role, nipe in ROLE_TO_NIPE.items():
        tag = role.replace("Vocalista - ", "").lower()
        if tag in low:
            return nipe
    bio_low = str(bio).lower()
    for hint, nipe in _BIO_NIPE_HINTS:
        if hint in bio_low:
            return nipe
    return None


def voice_kit_search_query(nipe: str, song_title: str = "") -> str:
    """
    Monta busca no YouTube no padrão do ministério.
    Ex.: Kit Voz baritono - Santo pra Sempre
    """
    nipe_label = nipe.lower().strip()
    title = str(song_title).strip()
    if title:
        return f"Kit Voz {nipe_label} - {title}"
    return f"Kit Voz {nipe_label}"


def voice_kit_youtube_url(nipe: str, song_title: str = "") -> str:
    query = voice_kit_search_query(nipe, song_title)
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"
