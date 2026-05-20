"""Links de kit de voz no YouTube por nipe vocal."""

from __future__ import annotations

from urllib.parse import quote_plus

ROLE_TO_NIPE: dict[str, str] = {
    "Vocalista - Contralto": "Contralto",
    "Vocalista - Soprano": "Soprano",
    "Vocalista - Tenor": "Tenor",
    "Vocalista - Baritono": "Baritono",
    "Vocalista - Mezzo Soprano": "Mezzo Soprano",
}

KIT_YOUTUBE_SEARCH: dict[str, str] = {
    "Contralto": "kit voz contralto gospel",
    "Soprano": "kit voz soprano gospel",
    "Tenor": "kit voz tenor gospel",
    "Baritono": "kit voz baritono gospel",
    "Mezzo Soprano": "kit voz mezzo soprano gospel",
}


def vocal_nipe_from_roles(roles: str) -> str | None:
    parts = [p.strip() for p in str(roles).split(",") if p.strip()]
    for role in parts:
        if role in ROLE_TO_NIPE:
            return ROLE_TO_NIPE[role]
    low = str(roles).lower()
    for role, nipe in ROLE_TO_NIPE.items():
        tag = role.replace("Vocalista - ", "").lower()
        if tag in low:
            return nipe
    return None


def voice_kit_youtube_url(nipe: str) -> str:
    query = KIT_YOUTUBE_SEARCH.get(nipe, f"kit voz {nipe.lower()} gospel")
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"
