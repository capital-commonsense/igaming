"""Source documents and the claims drawn from them.

`data/sources/manifest.yaml` lists every source (URL, date, sha256). `data/claims.yaml`
lists every number the figures use, each with verbatim quotes that must appear in its
source. `extract_text` turns a saved PDF or HTML page into normalized plain text so
the quotes can be checked.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
import urllib.request
from dataclasses import dataclass
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCES_DIR = PROJECT_ROOT / "data" / "sources"
MANIFEST_PATH = SOURCES_DIR / "manifest.yaml"
CLAIMS_PATH = PROJECT_ROOT / "data" / "claims.yaml"

# Generic browser UA: some publishers reject non-browser clients. No user details.
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko)"


@dataclass(frozen=True)
class Source:
    id: str
    file: str
    url: str
    title: str
    publisher: str
    date: str
    kind: str
    sha256: str | None
    status: str
    short: str | None = None  # compact citation for figure footers

    def path(self, base: Path = SOURCES_DIR) -> Path:
        return base / self.file

    def short_citation(self) -> str:
        return self.short or f"{self.publisher} ({self.date})"

    def citation(self) -> str:
        return f"{self.publisher}, “{self.title}” ({self.date})"


@dataclass(frozen=True)
class Claim:
    id: str
    value: Any
    unit: str
    source: str
    quotes: tuple[str, ...]
    article: str | None = None  # set when the claim backs article text rather than a graphic


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Source]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {
        sid: Source(id=sid, **{k: (str(v) if v is not None else None) for k, v in s.items()})
        for sid, s in raw["sources"].items()
    }


def load_claims(path: Path = CLAIMS_PATH) -> dict[str, Claim]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    out = {}
    for cid, c in raw["claims"].items():
        value = c["value"]
        if isinstance(value, str):
            value = float(value)  # PyYAML reads "2.7e6" as a string
        elif isinstance(value, list):
            value = [float(v) for v in value]
        out[cid] = Claim(cid, value, str(c["unit"]), str(c["source"]), tuple(str(q) for q in c["quotes"]),
                         c.get("article"))
    return out


# --------------------------------------------------------------------------- text extraction

_SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in _SKIP_TAGS:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


_REPLACEMENTS = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    " ": " ", " ": " ",
}


def normalize(text: str) -> str:
    """NFKC (splits ligatures like 'ﬁ'), straighten quotes/dashes, collapse whitespace."""
    text = unicodedata.normalize("NFKC", text)
    for a, b in _REPLACEMENTS.items():
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip()


def _pdf_text(path: Path) -> str:
    import logging

    from pypdf import PdfReader

    logging.getLogger("pypdf").setLevel(logging.ERROR)
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _html_text(path: Path) -> str:
    p = _TextParser()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    return " ".join(p.parts)


@lru_cache(maxsize=64)
def extract_text(path: Path) -> str:
    path = Path(path)
    raw = _pdf_text(path) if path.suffix.lower() == ".pdf" else _html_text(path)
    return normalize(raw)


def contains_quote(text: str, quote: str) -> bool:
    return normalize(quote).lower() in text.lower()


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- fetching


def fetch(source: Source, base: Path = SOURCES_DIR, timeout: float = 60) -> Path:
    """Download one source. Raises on HTTP errors (e.g. 403 from bot-blocking publishers)."""
    req = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (URLs come from our manifest)
        data = resp.read()
    dest = source.path(base)
    dest.write_bytes(data)
    return dest
