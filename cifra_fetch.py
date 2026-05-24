"""Busca letra e cifra na web (Vagalume) para preencher a Sequência do Culto."""

from __future__ import annotations

import html as html_lib
import logging
import re
import ssl
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)

_FETCH_TIMEOUT = 18
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


@dataclass
class LouvorWebContent:
    lyrics_text: str = ""
    cifra_text: str = ""
    letra_url: str = ""
    cifra_url: str = ""
    source: str = ""


def text_to_slug(text: str) -> str:
    from catalog_sanitize import sanitize_catalog_text

    raw = sanitize_catalog_text(text)
    if not raw:
        return ""
    norm = unicodedata.normalize("NFKD", raw)
    ascii_txt = "".join(c for c in norm if not unicodedata.combining(c))
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_txt.lower())
    return slug.strip("-")


def slugs_from_cifraclub_url(url: str) -> tuple[str, str]:
    """Extrai artista/música de URL direta do Cifra Club."""
    u = str(url or "").strip().lower()
    if "cifraclub.com.br" not in u or "/?q=" in u:
        return "", ""
    try:
        path = urllib.parse.urlparse(u).path.strip("/")
    except ValueError:
        return "", ""
    skip = {
        "estilos",
        "blog",
        "aprenda",
        "professor",
        "letra",
        "letras",
        "tabs",
        "videos",
        "mais",
    }
    parts = [p for p in path.split("/") if p and p not in skip]
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return "", ""


def _http_get(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": _USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    with urllib.request.urlopen(req, context=_SSL_CTX, timeout=_FETCH_TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def _clean_lyrics_html(fragment: str) -> str:
    s = fragment
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</?p>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html_lib.unescape(s)
    lines = [ln.strip() for ln in s.splitlines()]
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln:
            blank += 1
            if blank <= 1 and out:
                out.append("")
            continue
        blank = 0
        out.append(ln)
    return "\n".join(out).strip()


def _clean_cifra_html(fragment: str) -> str:
    s = fragment
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<b>([^<]*)</b>", r"\1", s, flags=re.I)
    s = re.sub(r"</?b>", "", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html_lib.unescape(s)
    lines = [ln.rstrip() for ln in s.splitlines()]
    return "\n".join(lines).strip()


def _extract_vagalume_lyrics(html: str) -> str:
    # Página de letra: id=lyrics (sem class=cifra). Página cifrada usa class=cifra.
    m = re.search(
        r'<div id=lyrics(?![^>]*\bclass=cifra\b)[^>]*>(.*?)</div>',
        html,
        re.S | re.I,
    )
    if not m:
        return ""
    return _clean_lyrics_html(m.group(1))


_CHORD_TOKEN_RE = re.compile(
    r"\b[A-G](?:#|b)?(?:maj|min|dim|aug|sus|add)?[0-9]?(?:/[A-G](?:#|b)?)?\b",
    re.I,
)

_CIFRA_JUNK_LINE = re.compile(
    r"^(tom\b|capo|capotraste|afina[cç][aã]o|simplificar|rolagem|auto\s*scroll|"
    r"imprimir|compartilhar|reportar|dicion[aá]rio|acordes\s*:|vers[aã]o\b|"
    r"tablatura|video\b|v[ií]deo\b|arrastar|zoom|tuning|afinar)",
    re.I,
)

_CIFRA_STOP_SECTION = re.compile(
    r"(coment[aá]rios|aprenda a tocar|outras vers[oõ]es|ver\s+v[ií]deo|"
    r"letra da m[uú]sica|autoria|cifra\s*club|e-chords|enviar\s+cifra|"
    r"corrigir\s+cifra|imprimir\s+cifra|partitura|tablaturas\s+para)",
    re.I,
)


def _line_is_chord_row(line: str) -> bool:
    tokens = [t for t in line.strip().split() if t]
    if not tokens:
        return False
    chord_n = sum(1 for t in tokens if _CHORD_TOKEN_RE.match(t))
    return chord_n >= max(2, int(len(tokens) * 0.55))


def normalize_cifra_text(text: str) -> str:
    """
    Remove lixo do site e mantém só pares acorde/letra organizados (estilo Cifra Club).
    """
    raw = str(text or "").replace("\r\n", "\n").strip()
    if not raw:
        return ""

    cleaned: list[str] = []
    for ln in raw.splitlines():
        s = ln.rstrip()
        if not s.strip():
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        if _CIFRA_STOP_SECTION.search(s):
            break
        if _CIFRA_JUNK_LINE.match(s.strip()):
            continue
        if len(s.strip()) > 220 and not _line_is_chord_row(s):
            continue
        cleaned.append(s)

    paired: list[str] = []
    i = 0
    while i < len(cleaned):
        line = cleaned[i]
        if line == "":
            i += 1
            continue
        if _line_is_chord_row(line):
            paired.append(line)
            if i + 1 < len(cleaned) and cleaned[i + 1] and not _line_is_chord_row(cleaned[i + 1]):
                paired.append(cleaned[i + 1])
                i += 2
            else:
                paired.append("")
                i += 1
        else:
            paired.append(line)
            i += 1

    out: list[str] = []
    blank = 0
    for ln in paired:
        if not ln.strip():
            blank += 1
            if blank <= 1 and out:
                out.append("")
            continue
        blank = 0
        out.append(ln.rstrip())
    return "\n".join(out).strip()


def _extract_vagalume_page_title(html: str) -> str:
    for pat in (
        r'property="og:title"\s+content="([^"]+)"',
        r"<meta[^>]+name=\"title\"[^>]+content=\"([^\"]+)\"",
        r"<h1[^>]*>(.*?)</h1>",
    ):
        m = re.search(pat, html, re.S | re.I)
        if m:
            t = re.sub(r"<[^>]+>", "", m.group(1))
            return html_lib.unescape(t).strip()
    return ""


def _looks_like_cifra(text: str) -> bool:
    """Evita gravar letra pura no lugar da cifra."""
    if not str(text or "").strip():
        return False
    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    if len(lines) < 2:
        return False
    chord_lines = sum(1 for ln in lines if _CHORD_TOKEN_RE.search(ln))
    return chord_lines >= 2


def _extract_vagalume_cifra(html: str) -> str:
    m = re.search(
        r'<div id=lyrics[^>]*class=cifra[^>]*>(.*?)</div>',
        html,
        re.S | re.I,
    )
    if not m:
        return ""
    text = normalize_cifra_text(_clean_cifra_html(m.group(1)))
    return text if _looks_like_cifra(text) else ""


def _extract_echords_cifra(html: str) -> str:
    if "data-chord=" not in html:
        return ""
    start = html.find("data-chord=")
    if start < 0:
        return ""
    chunk = html[start : start + 120000]
    end_markers = ('<div class="footer"', "<footer", 'id="comments"')
    end = len(chunk)
    for marker in end_markers:
        pos = chunk.find(marker)
        if pos > 500:
            end = min(end, pos)
    chunk = chunk[:end]
    s = re.sub(
        r'<span[^>]*data-chord="([^"]*)"[^>]*>.*?</span>',
        r"\1",
        chunk,
        flags=re.S | re.I,
    )
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</?p>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html_lib.unescape(s)
    lines = [ln.rstrip() for ln in s.splitlines()]
    text = normalize_cifra_text("\n".join(lines).strip())
    return text if _looks_like_cifra(text) else ""


def _echords_urls(artist_slug: str, song_slug: str) -> list[str]:
    if not artist_slug or not song_slug:
        return []
    base = "https://www.e-chords.com/chords"
    urls = [f"{base}/{artist_slug}/{song_slug}"]
    if artist_slug.endswith("-music"):
        short = artist_slug[: -len("-music")].strip("-")
        if short:
            urls.append(f"{base}/{short}/{song_slug}")
    return list(dict.fromkeys(urls))


def _find_echords_via_search(title: str, artist: str) -> str:
    try:
        from link_finder import _ddg_search
    except ImportError:
        return ""
    q = f"{title} {artist} site:e-chords.com".strip()
    for url in _ddg_search(q, max_results=8):
        if "e-chords.com/chords/" in url.lower():
            return url.split("#")[0].rstrip("/")
    return ""


def fetch_from_echords(
    title: str,
    artist: str = "",
    *,
    cifra_club_url: str = "",
) -> LouvorWebContent:
    """Fallback quando Vagalume não tem página cifrada."""
    from catalog_sanitize import sanitize_catalog_text

    title = sanitize_catalog_text(title)
    artist = sanitize_catalog_text(artist)
    if not title:
        return LouvorWebContent()

    song_slug = text_to_slug(title)
    artist_slugs: list[str] = []
    cc_artist, cc_song = slugs_from_cifraclub_url(cifra_club_url)
    if cc_artist:
        artist_slugs.append(cc_artist)
    if cc_song:
        song_slug = cc_song
    if artist:
        artist_slugs.extend(_artist_slug_variants(artist))
    artist_slugs = list(dict.fromkeys(a for a in artist_slugs if a))
    if not artist_slugs:
        return LouvorWebContent()

    found_url = _find_echords_via_search(title, artist)
    out = LouvorWebContent(source="e-chords")
    tried: set[str] = set()
    if found_url:
        tried.add(found_url)
        try:
            html = _http_get(found_url)
            out.cifra_text = _extract_echords_cifra(html)
            from lyrics_validation import validate_fetched_cifra

            ok, _ = validate_fetched_cifra(
                title,
                out.cifra_text,
                source_url=found_url,
                expected_slug=song_slug,
            )
            if out.cifra_text and ok:
                out.cifra_url = found_url
                return out
            out.cifra_text = ""
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.info("e-chords %s: %s", found_url, exc)

    for artist_slug in artist_slugs:
        for url in _echords_urls(artist_slug, song_slug):
            if url in tried:
                continue
            tried.add(url)
            try:
                html = _http_get(url)
                out.cifra_text = _extract_echords_cifra(html)
                from lyrics_validation import validate_fetched_cifra

                ok, _ = validate_fetched_cifra(
                    title,
                    out.cifra_text,
                    source_url=url,
                    expected_slug=song_slug,
                )
                if out.cifra_text and ok:
                    out.cifra_url = url
                    return out
                out.cifra_text = ""
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                logger.info("e-chords %s: %s", url, exc)
    return out


def _vagalume_urls(artist_slug: str, song_slug: str) -> tuple[str, str]:
    if not artist_slug or not song_slug:
        return "", ""
    base = "https://www.vagalume.com.br"
    letra = f"{base}/{artist_slug}/{song_slug}.html"
    cifrada = f"{base}/{artist_slug}/{song_slug}-cifrada.html"
    return letra, cifrada


def _artist_slug_variants(artist: str) -> list[str]:
    base = text_to_slug(artist)
    if not base:
        return []
    variants = [base]
    for suffix in ("-music", "-oficial", "-brasil", "-br", "-gospel"):
        if base.endswith(suffix):
            variants.append(base[: -len(suffix)].strip("-"))
    parts = base.split("-")
    if len(parts) > 1 and len(parts[0]) >= 3:
        variants.append(parts[0])
    return list(dict.fromkeys(v for v in variants if v))


def _find_vagalume_via_search(title: str, artist: str) -> tuple[str, str]:
    try:
        from link_finder import _ddg_search
    except ImportError:
        return "", ""
    q = f"{title} {artist} site:vagalume.com.br letra".strip()
    for url in _ddg_search(q, max_results=8):
        if "vagalume.com.br" not in url.lower():
            continue
        if "-cifrada" in url:
            continue
        m = re.search(
            r"vagalume\.com\.br/([^/]+)/([^/.?]+)\.html",
            url,
            re.I,
        )
        if m:
            return m.group(1), m.group(2)
    return "", ""


def _find_vagalume_cifrada_url(title: str, artist: str) -> str:
    try:
        from link_finder import _ddg_search
    except ImportError:
        return ""
    q = f"{title} {artist} site:vagalume.com.br cifrada".strip()
    for url in _ddg_search(q, max_results=8):
        if "-cifrada.html" in url.lower() and "vagalume.com.br" in url.lower():
            return url.split("#")[0]
    return ""


def fetch_from_vagalume(
    title: str,
    artist: str = "",
    *,
    cifra_club_url: str = "",
) -> LouvorWebContent:
    """Baixa letra e cifra do Vagalume usando slugs do Cifra Club ou busca."""
    from catalog_sanitize import sanitize_catalog_text

    title = sanitize_catalog_text(title)
    artist = sanitize_catalog_text(artist)
    if not title:
        return LouvorWebContent()

    song_slug = text_to_slug(title)
    if not song_slug:
        return LouvorWebContent()

    artist_slugs: list[str] = []
    cc_artist, cc_song = slugs_from_cifraclub_url(cifra_club_url)
    if cc_artist and cc_song:
        artist_slugs.append(cc_artist)
        if cc_song != song_slug:
            song_slug = cc_song
    if artist:
        artist_slugs.extend(_artist_slug_variants(artist))
    va, vs = _find_vagalume_via_search(title, artist)
    if va:
        artist_slugs.insert(0, va)
    if vs:
        song_slug = vs
    artist_slugs = list(dict.fromkeys(a for a in artist_slugs if a))
    if not artist_slugs:
        return LouvorWebContent()

    from lyrics_validation import validate_fetched_cifra, validate_fetched_lyrics

    out = LouvorWebContent(source="vagalume")
    cifrada_extra = _find_vagalume_cifrada_url(title, artist)
    for artist_slug in artist_slugs:
        letra_url, cifrada_url = _vagalume_urls(artist_slug, song_slug)
        try:
            if not out.lyrics_text:
                html_letra = _http_get(letra_url)
                page_title = _extract_vagalume_page_title(html_letra)
                candidate = _extract_vagalume_lyrics(html_letra)
                ok, reason = validate_fetched_lyrics(
                    title,
                    artist,
                    candidate,
                    source_url=letra_url,
                    page_title=page_title,
                    expected_slug=song_slug,
                )
                if ok and candidate:
                    out.lyrics_text = candidate
                    out.letra_url = letra_url
                elif candidate:
                    logger.info(
                        "Vagalume letra rejeitada %s: %s", letra_url, reason
                    )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.info("Vagalume letra falhou %s: %s", letra_url, exc)
        for cf_url in (cifrada_url, cifrada_extra):
            if not cf_url or out.cifra_text:
                continue
            try:
                html_cifra = _http_get(cf_url)
                cifra = _extract_vagalume_cifra(html_cifra)
                ok_cf, reason_cf = validate_fetched_cifra(
                    title,
                    cifra,
                    source_url=cf_url,
                    expected_slug=song_slug,
                )
                if cifra and ok_cf:
                    out.cifra_text = cifra
                    out.cifra_url = cf_url
                elif cifra:
                    logger.info(
                        "Vagalume cifra rejeitada %s: %s", cf_url, reason_cf
                    )
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                logger.info("Vagalume cifra falhou %s: %s", cf_url, exc)
        if out.lyrics_text and out.cifra_text:
            break

    return out


def fetch_louvor_lyrics_and_cifra(
    title: str,
    artist: str = "",
    *,
    cifra_club_url: str = "",
    resolve_cifra_url: Callable[[str, str], str | None] | None = None,
) -> LouvorWebContent:
    """
    Obtém letra e cifra: tenta Vagalume (mais estável que scrape do Cifra Club).
    Opcionalmente resolve URL direta do Cifra Club via link_finder.
    """
    url = str(cifra_club_url or "").strip()
    if url and "/?q=" in url and resolve_cifra_url:
        found = resolve_cifra_url(title, artist)
        if found:
            url = found

    result = fetch_from_vagalume(title, artist, cifra_club_url=url)
    if not result.cifra_text:
        ec = fetch_from_echords(title, artist, cifra_club_url=url)
        if ec.cifra_text:
            result.cifra_text = ec.cifra_text
            result.cifra_url = ec.cifra_url or result.cifra_url
            if ec.source:
                result.source = f"{result.source}+{ec.source}".strip("+")

    if result.cifra_text:
        result.cifra_text = normalize_cifra_text(result.cifra_text)
    if result.lyrics_text or result.cifra_text:
        return result

    # Segunda tentativa: slugs só do título (louvor sem artista no catálogo)
    if artist:
        result = fetch_from_vagalume(title, "", cifra_club_url=url)
        if not result.cifra_text:
            ec = fetch_from_echords(title, "", cifra_club_url=url)
            if ec.cifra_text:
                result.cifra_text = ec.cifra_text
                result.cifra_url = ec.cifra_url
    if result.cifra_text:
        result.cifra_text = normalize_cifra_text(result.cifra_text)
    return result
