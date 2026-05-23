"""Transposição simples de acordes em cifras (formato texto)."""

from __future__ import annotations

import re

# Ordem cromática para transposição
_CHROMATIC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_FLAT_EQUIV = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B", "Fb": "E"}

_CHORD_RE = re.compile(
    r"\b([A-G](?:#|b)?)"
    r"((?:maj|min|m|M|dim|aug|sus|add|maj7|min7|m7|7|9|11|13|º|°|\+)?)"
    r"((?:\/[A-G](?:#|b)?)?)\b",
    re.IGNORECASE,
)


def normalize_chord_root(root: str) -> str:
    r = root.strip()
    if not r:
        return "C"
    letter = r[0].upper()
    rest = r[1:]
    if rest.lower() == "b" and len(r) == 2:
        flat = letter + "b"
        return _FLAT_EQUIV.get(flat, letter)
    if "#" in rest.upper():
        return letter + "#"
    return letter


def chord_to_semitone(root: str) -> int:
    n = normalize_chord_root(root)
    try:
        return _CHROMATIC.index(n)
    except ValueError:
        return 0


def semitone_to_chord(n: int, prefer_flats: bool = False) -> str:
    n = n % 12
    if prefer_flats and n in (1, 3, 6, 8, 10):
        flats = {1: "Db", 3: "Eb", 6: "Gb", 8: "Ab", 10: "Bb"}
        return flats.get(n, _CHROMATIC[n])
    return _CHROMATIC[n]


def transpose_chord_symbol(chord: str, semitones: int) -> str:
    m = _CHORD_RE.match(chord.strip())
    if not m:
        return chord
    root, qual, bass = m.group(1), m.group(2) or "", m.group(3) or ""
    new_root = semitone_to_chord(chord_to_semitone(root) + semitones)
    if bass:
        bass_root = bass.lstrip("/")
        new_bass = semitone_to_chord(chord_to_semitone(bass_root) + semitones)
        bass = f"/{new_bass}"
    return f"{new_root}{qual}{bass}"


def key_to_semitone(key: str) -> int:
    k = str(key or "C").strip().upper()
    mapping = {
        "DO": 0, "DÓ": 0, "C": 0,
        "DO#": 1, "DÓ#": 1, "C#": 1,
        "RE": 2, "RÉ": 2, "D": 2,
        "RE#": 3, "RÉ#": 3, "D#": 3, "MIB": 3,
        "MI": 4, "E": 4,
        "FA": 5, "F": 5,
        "FA#": 6, "F#": 6,
        "SOL": 7, "G": 7,
        "SOL#": 8, "G#": 8,
        "LA": 9, "A": 9,
        "LA#": 10, "A#": 10,
        "SI": 11, "B": 11,
    }
    return mapping.get(k, 0)


def transpose_cifra_text(text: str, from_key: str, to_key: str) -> str:
    if not str(text).strip():
        return ""
    semi = key_to_semitone(to_key) - key_to_semitone(from_key)
    if semi == 0:
        return text

    def repl(m: re.Match) -> str:
        return transpose_chord_symbol(m.group(0), semi)

    return _CHORD_RE.sub(repl, text)
