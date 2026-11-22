"""Measure text width from the brand TTFs, so label layout matches the rendered output."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont

FALLBACK_EM_RATIO = 0.56  # average advance / em for a humanist sans


class TextMeasurer:
    def __init__(self, font_path: str | Path | None):
        self._font = None
        if font_path and Path(font_path).exists():
            font = TTFont(str(font_path), lazy=True)
            self._cmap = font.getBestCmap()
            self._hmtx = font["hmtx"]
            self._upem = font["head"].unitsPerEm
            self._font = font

    @property
    def uses_font(self) -> bool:
        return self._font is not None

    def width(self, text: str, size: float) -> float:
        if self._font is None:
            return len(text) * size * FALLBACK_EM_RATIO
        total = 0
        for ch in text:
            glyph = self._cmap.get(ord(ch))
            if glyph is None:
                total += self._upem * FALLBACK_EM_RATIO
            else:
                total += self._hmtx[glyph][0]
        return total * size / self._upem


@lru_cache(maxsize=8)
def measurer(font_path: str | None) -> TextMeasurer:
    return TextMeasurer(font_path)
