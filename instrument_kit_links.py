"""Kits no YouTube por instrumento (bateria, guitarra, violão, teclado) e voz."""

from __future__ import annotations

from urllib.parse import quote_plus

from voice_kit_links import ROLE_TO_NIPE, vocal_nipe_from_roles, voice_kit_youtube_url

# (rótulo curto, prefixo de busca no YouTube)
INSTRUMENT_KITS: dict[str, tuple[str, str]] = {
    "Baterista": ("Bateria", "kit bateria"),
    "Guitarrista": ("Guitarra", "kit guitarra"),
    "Violonista": ("Violão", "kit violao"),
    "Tecladista": ("Teclado", "kit teclado"),
    "Baixista": ("Baixo", "kit baixo"),
}


def _roles_list(roles: str) -> list[str]:
    return [p.strip() for p in str(roles).split(",") if p.strip()]


def instrument_kits_from_roles(roles: str, bio: str = "") -> list[tuple[str, str, str]]:
    """
    Retorna lista (rótulo exibido, tipo kit, url) para cada função do integrante.
    Inclui Kit Voz quando houver nipe vocal.
    """
    out: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for role in _roles_list(roles):
        if role in INSTRUMENT_KITS:
            label, prefix = INSTRUMENT_KITS[role]
            key = f"inst:{role}"
            if key not in seen:
                seen.add(key)
                out.append((f"Kit {label}", key, prefix))
        elif role in ROLE_TO_NIPE:
            nipe = ROLE_TO_NIPE[role]
            key = f"voz:{nipe}"
            if key not in seen:
                seen.add(key)
                out.append((f"Kit Voz ({nipe})", key, f"kit voz {nipe.lower()}"))
    nipe = vocal_nipe_from_roles(roles, bio=bio)
    if nipe and f"voz:{nipe}" not in seen:
        out.append((f"Kit Voz ({nipe})", f"voz:{nipe}", f"kit voz {nipe.lower()}"))
    return out


def kit_youtube_url(kit_prefix: str, song_title: str = "") -> str:
    title = str(song_title).strip()
    if title:
        query = f"{kit_prefix} - {title}"
    else:
        query = kit_prefix
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def voice_kit_url_for_song(nipe: str, song_title: str) -> str:
    return voice_kit_youtube_url(nipe, song_title)
