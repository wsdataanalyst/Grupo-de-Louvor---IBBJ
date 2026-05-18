"""Gera data/louvores.csv a partir dos PDFs do catálogo e da lista semestral."""
import re
import unicodedata
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "louvores.csv"

PDF_BASE = Path(
    r"c:\Users\wsana\AppData\Roaming\Cursor\User\workspaceStorage"
    r"\2336121169568b640079771c8b6c6cd9\pdfs"
)

COLUMNS = (
    "title",
    "artist",
    "key",
    "youtube_url",
    "cifra_url",
    "ritmo",
    "letter",
    "source",
)

URL_PATTERN = re.compile(r"https?://[^\s\)\],]+", re.I)
YOUTUBE_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s\)\],]*", re.I
)
CIFRA_PATTERN = re.compile(
    r"https?://(?:www\.)?cifraclub\.com\.br[^\s\)\],]*", re.I
)
KEY_PATTERN = re.compile(
    r"\b(\d{0,2})?(RÉ(?:/DÓ)?|DÓ|SOL|LÁ|LA|MI|MÍ|FA|FÁ|BB(?:/[BC])?|"
    r"BM|DB(?:/[C])?|C#M?|AM|FÁ|Fá|Ré|Dó|Sol|Lá|Mi|Mí)\b",
    re.I,
)
RITMO_PATTERN = re.compile(
    r"(Lento|Médio|Medio|Rápido|Rapido)(?:\s+ou\s+.*|\s*\(.*\)|\s+.*)?$",
    re.I,
)
LETTER_HEADER = re.compile(r"^LETRA\s*[-]?\s*([A-ZÁÉÍÓÚ])", re.I)
SKIP_LINE = re.compile(
    r"^(REPERT|Nome\s+Link|Página\s+\d|quinta-feira|#ERROR)", re.I
)


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.strip())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9\s]", "", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def clean_title(raw: str) -> str:
    title = raw.strip().lstrip("-").strip()
    title = re.sub(r"-+$", "", title).strip()
    title = re.sub(r"\s+", " ", title)
    return title


def split_title_artist(name: str) -> tuple[str, str]:
    name = clean_title(name)
    name = re.sub(r"\s*-\s*(?=\S)", " - ", name)
    if " - " in name:
        title, artist = name.split(" - ", 1)
        return title.strip(), artist.strip()
    return name, ""


def canonicalize_record(record: dict) -> dict:
    record = record.copy()
    title, parsed_artist = split_title_artist(record["title"])
    record["title"] = title
    if parsed_artist and not str(record.get("artist", "")).strip():
        record["artist"] = parsed_artist
    record["artist"] = str(record.get("artist", "")).strip()
    if record["title"]:
        record["letter"] = record["title"][0].upper()
    return record


def slug_hint(title: str) -> str:
    slug = normalize_text(title).replace(" ", "-")
    return slug[:12]


def cifra_matches_title(cifra_url: str, title: str) -> bool:
    if not cifra_url or cifra_url.upper() == "CIFRA DA IGREJA":
        return True
    hint = slug_hint(title)
    path = cifra_url.lower()
    return hint[:6] in path or normalize_text(title).replace(" ", "")[:8] in path.replace(
        "-", ""
    )


def merge_records(existing: dict, new: dict) -> dict:
    merged = existing.copy()
    for field in COLUMNS:
        if field == "source":
            sources = {s.strip() for s in f"{existing.get('source', '')},{new.get('source', '')}".split(",") if s.strip()}
            merged["source"] = ", ".join(sorted(sources))
            continue
        if not str(merged.get(field, "")).strip() and str(new.get(field, "")).strip():
            merged[field] = new[field]
    if not cifra_matches_title(merged.get("cifra_url", ""), merged["title"]):
        if cifra_matches_title(new.get("cifra_url", ""), merged["title"]):
            merged["youtube_url"] = new.get("youtube_url", "") or merged.get("youtube_url", "")
            merged["cifra_url"] = new.get("cifra_url", "")
    return merged


def parse_recent_list(text: str) -> list[dict]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lines = [line for line in lines if not SKIP_LINE.search(line)]
    if lines and "LOUVORES" in lines[0].upper():
        lines = lines[1:]
    if lines and lines[0].lower().startswith("nome link"):
        lines = lines[1:]

    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if URL_PATTERN.search(line) and current:
            blocks.append(" ".join(current))
            current = [line]
        elif current or URL_PATTERN.search(line):
            current.append(line)
        elif current:
            current.append(line)
    if current:
        blocks.append(" ".join(current))

    records: list[dict] = []
    for block in blocks:
        urls = URL_PATTERN.findall(block)
        if not urls:
            continue
        youtube_urls = [u.rstrip(".,;") for u in urls if YOUTUBE_PATTERN.match(u)]
        cifra_urls = [u.rstrip(".,;") for u in urls if CIFRA_PATTERN.match(u)]
        first_url_pos = block.find(urls[0])
        name_part = clean_title(block[:first_url_pos])
        name_part = re.sub(r"\s*-\s*(?=\S)", " - ", name_part)
        tail = block[block.find(urls[-1]) + len(urls[-1]) :]

        title, artist = split_title_artist(name_part)
        if not title:
            continue

        key_match = KEY_PATTERN.search(tail)
        ritmo_match = RITMO_PATTERN.search(tail)
        key = key_match.group(0).upper() if key_match else ""
        ritmo = ritmo_match.group(0).strip() if ritmo_match else ""

        cifra_url = cifra_urls[0] if cifra_urls else ""
        if not cifra_url and "cifraclub" in tail.lower():
            cifra_url = "CIFRA DA IGREJA"
        elif not cifra_url and "CIFRA DA IGREJA" in tail.upper():
            cifra_url = "CIFRA DA IGREJA"

        record = canonicalize_record(
            {
                "title": title,
                "artist": artist,
                "key": key,
                "youtube_url": youtube_urls[0] if youtube_urls else "",
                "cifra_url": cifra_url,
                "ritmo": ritmo,
                "letter": title[0].upper() if title else "",
                "source": "lista_semestral",
            }
        )
        if record["cifra_url"] and not cifra_matches_title(record["cifra_url"], record["title"]):
            record["youtube_url"] = ""
            record["cifra_url"] = ""
            record["key"] = record["key"] or key
        records.append(record)
    return records


def parse_catalog_line(line: str, letter: str) -> dict | None:
    line = re.sub(r"^[\d#]+", "", line).strip()
    if not line or len(line) < 3:
        return None

    match = re.match(
        r"^(.+?)\s+(\d{0,2})?"
        r"(RÉ(?:/DÓ)?|DÓ|SOL|LÁ|LA|MI|MÍ|FA|FÁ|BB|BM|DB(?:/[C])?|C#M?|AM)\s*(.*)$",
        line,
        re.I,
    )
    title = line
    key = ""
    artist = ""
    if match:
        title = match.group(1).strip()
        key = match.group(3).upper()
        artist = match.group(4).strip()

    title = clean_title(title)
    if not title or title.upper().startswith("LETRA"):
        return None
    if re.fullmatch(r"\d+", title) or len(title) < 4:
        return None
    if re.search(r",\s*m\s+\d+$", title, re.I):
        return None
    if not artist and " " in title:
        maybe_title, maybe_artist = title.rsplit(" ", 1)
        if maybe_artist[:1].isupper() and len(maybe_artist) > 3:
            title, artist = maybe_title, maybe_artist

    return {
        "title": title,
        "artist": artist,
        "key": key,
        "youtube_url": "",
        "cifra_url": "",
        "ritmo": "",
        "letter": letter or (title[0].upper() if title else ""),
        "source": "catalogo",
    }


def parse_catalog(text: str) -> list[dict]:
    records: list[dict] = []
    letter = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or SKIP_LINE.search(line):
            continue
        header = LETTER_HEADER.match(line)
        if header:
            letter = header.group(1).upper()
            continue
        if "LOUVORESCIFRAS" in line.upper():
            continue
        record = parse_catalog_line(line, letter)
        if record:
            records.append(record)
    return records


def dedupe_records(records: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for record in records:
        record = canonicalize_record(record)
        key = normalize_text(record["title"])
        if not key or len(key) < 3:
            continue
        if key in merged:
            merged[key] = merge_records(merged[key], record)
        else:
            merged[key] = record
    return sorted(merged.values(), key=lambda item: (item["letter"], item["title"]))


def read_pdf_text(folder_name: str) -> str:
    folder = PDF_BASE / folder_name
    pdf_files = list(folder.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"PDF não encontrado em {folder}")
    reader = PdfReader(str(pdf_files[0]))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def build_database() -> pd.DataFrame:
    catalog_dirs = list(PDF_BASE.iterdir())
    catalog_text = ""
    recent_text = ""
    for folder in catalog_dirs:
        if not folder.is_dir():
            continue
        pdfs = list(folder.glob("*.pdf"))
        if not pdfs:
            continue
        name = pdfs[0].name.lower()
        text = read_pdf_text(folder.name)
        if "catalogo" in name or "catálogo" in name or "catalog" in normalize_text(name):
            catalog_text = text
        elif "lista" in name or "recente" in name:
            recent_text = text

    recent_records = parse_recent_list(recent_text)
    catalog_records = parse_catalog(catalog_text)
    combined = dedupe_records(catalog_records + recent_records)
    return pd.DataFrame(combined, columns=list(COLUMNS))


def main():
    df = build_database()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Gerado {OUTPUT_FILE} com {len(df)} louvores únicos.")


if __name__ == "__main__":
    main()
