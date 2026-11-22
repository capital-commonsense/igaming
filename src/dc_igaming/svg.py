"""Shared brand theme and SVG helpers for every Capital Commonsense figure."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from dc_igaming.flow import Group
from dc_igaming.textmetrics import measurer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FONT_DIR = PROJECT_ROOT / "brand_kit" / "Fonts"
SVG_NS = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class Theme:
    red: str = "#D43D29"
    ink: str = "#111111"
    paper: str = "#FFFFFF"
    muted: str = "#5B5B5B"
    rule: str = "#DDDCD8"
    private: str = "#8C8B87"
    players: str = "#C9C8C4"
    serif: str = "'Newsreader 72pt', Newsreader, Georgia, serif"
    sans: str = "'IBM Plex Sans', Arial, sans-serif"
    sans_font_file: Path = FONT_DIR / "IBMPlexSans-Regular.ttf"
    sans_bold_font_file: Path = FONT_DIR / "IBMPlexSans-SemiBold.ttf"
    serif_font_file: Path = FONT_DIR / "Newsreader72pt-Bold.ttf"

    def group_color(self, group: Group) -> str:
        return {
            Group.LEAVES_DC: self.ink,
            Group.DC_PUBLIC: self.red,
            Group.DC_REGULATION: self.players,
            Group.DC_PRIVATE: self.private,
        }[group]


def format_usd(v: float) -> str:
    if abs(v) >= 1e9:
        return f"${v / 1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v / 1e6:.1f}M"
    if abs(v) >= 1e3:
        return f"${v / 1e3:.0f}K"
    return f"${v:.0f}"


def format_usd_precise(v: float) -> str:
    """$1.65M, $1.34M: two decimals, half-up, for figures traced line by line to a source table."""
    from decimal import ROUND_HALF_UP, Decimal

    m = (Decimal(str(v)) / Decimal(1_000_000)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"${m}M"


def attrs(**kw: object) -> str:
    """Keyword args to SVG attributes: font_size -> font-size, class_ -> class."""
    parts = []
    for k, v in kw.items():
        if v is None:
            continue
        name = k.rstrip("_").replace("_", "-")
        if isinstance(v, float):
            v = f"{v:.2f}".rstrip("0").rstrip(".")
        parts.append(f'{name}="{escape(str(v), {chr(34): "&quot;"})}"')
    return " ".join(parts)


def text(x: float, y: float, s: str, **kw: object) -> str:
    return f"<text {attrs(x=x, y=y, **kw)}>{escape(s)}</text>"


def el(tag: str, **kw: object) -> str:
    return f"<{tag} {attrs(**kw)}/>"


def wrap(s: str, max_width: float, size: float, font_file: Path) -> list[str]:
    """Greedy word wrap using real glyph advances from the brand font."""
    m = measurer(str(font_file))
    lines: list[str] = []
    cur = ""
    for word in re.split(r"[ \t\r\n]+", s):  # not U+00A0, so non-breaking spaces hold
        if not word:
            continue
        trial = f"{cur} {word}".strip(" ")
        if m.width(trial, size) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font_size(s: str, max_width: float, font_file: Path, start: float, minimum: float,
                  step: float = 1.0) -> float:
    """Largest size from `start` down to `minimum` at which `s` fits on one line."""
    m = measurer(str(font_file))
    size = start
    while size > minimum and m.width(s, size) > max_width:
        size -= step
    return size


def document(body: list[str], width: float, height: float, title: str, theme: Theme,
             defs: str = "") -> str:
    """Wrap body elements in an <svg> root with a paper background and accessible title."""
    root = attrs(xmlns=SVG_NS, viewBox=f"0 0 {width:g} {height:g}", width=width, height=height,
                 role="img", aria_label=title)
    head = [
        f"<svg {root}>",
        f"<title>{escape(title)}</title>",
    ]
    if defs:
        head.append(f"<defs>{defs}</defs>")
    head.append(el("rect", width=width, height=height, fill=theme.paper))
    return "\n".join([*head, *body, "</svg>"])


def footer(lines_of_text: list[str], y: float, x: float, max_width: float, theme: Theme,
           size: float = 17, gap_before_last: float = 8) -> tuple[list[str], float]:
    """Wrapped grey footer paragraphs (notes, then source). Returns elements and end y."""
    out: list[str] = []
    for i, para in enumerate(lines_of_text):
        if i == len(lines_of_text) - 1 and len(lines_of_text) > 1:
            y += gap_before_last
        for line in wrap(para, max_width, size, theme.sans_font_file):
            out.append(text(x, y, line, font_size=size, fill=theme.muted, font_family=theme.sans))
            y += size * 1.45
    return out, y


def svg_to_png(svg: str, path: str | Path, zoom: float = 2.0) -> Path:
    import resvg_py

    png = resvg_py.svg_to_bytes(svg_string=svg, zoom=zoom, font_dirs=[str(FONT_DIR)],
                                text_rendering="optimize_legibility")
    path = Path(path)
    path.write_bytes(bytes(png))
    return path
