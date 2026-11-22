"""Branded "share" versions of any figure.

Follows the brand kit's social template: Capital Commonsense wordmark top-left, the CC
avatar badge top-right, and a rule with the site URL at the bottom. The figure itself is
nested unchanged, so the share version can never drift from the plain one.

Brand rule: keep the nested CC clear of other elements by at least 20% of its width.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

from dc_igaming.svg import PROJECT_ROOT, Theme, attrs, el, text

LOGO_DIR = PROJECT_ROOT / "brand_kit" / "Logos"
WORDMARK = LOGO_DIR / "Capital_Commonsense_Wordmark.svg"
AVATAR = LOGO_DIR / "Capital_Commonsense_Avatar.svg"
SITE_URL = "capitalcommonsense.com"
CLEAR_SPACE = 0.20  # fraction of the CC badge width


@dataclass(frozen=True)
class ShareLayout:
    margin_x: float = 100
    header_h: float = 130
    fig_top_trim: float = 50  # figure's own top padding hidden under the header
    fig_bottom_trim: float = 10
    wordmark_h: float = 46
    badge: float = 84
    footer_h: float = 92
    url_size: float = 22


def _viewbox(svg: str) -> tuple[float, float, float, float]:
    m = re.search(r'viewBox="([^"]+)"', svg)
    if not m:
        raise ValueError("SVG has no viewBox")
    x, y, w, h = (float(v) for v in m.group(1).split())
    return x, y, w, h


def nest(svg: str, x: float, y: float, width: float, height: float, id_prefix: str = "") -> str:
    """Re-root a standalone SVG document at (x, y) with the given size.

    Drops the XML declaration and the root's own width/height, keeps its viewBox.
    `id_prefix` namespaces ids so nested documents can't collide.
    """
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
    if id_prefix:
        ids = set(re.findall(r'\bid="([^"]+)"', svg))
        for i in sorted(ids, key=len, reverse=True):
            svg = re.sub(rf'\bid="{re.escape(i)}"', f'id="{id_prefix}{i}"', svg)
            svg = svg.replace(f'"#{i}"', f'"#{id_prefix}{i}"').replace(f"url(#{i})", f"url(#{id_prefix}{i})")
    m = re.match(r"<svg\b([^>]*)>", svg)
    if not m:
        raise ValueError("not an SVG document")
    root_attrs = re.sub(r'\s(width|height|x|y)="[^"]*"', "", m.group(1))
    placed = f"<svg{root_attrs} {attrs(x=x, y=y, width=width, height=height)}>"
    return placed + svg[m.end():]


def brand_frame(figure_svg: str, theme: Theme | None = None, lay: ShareLayout | None = None,
                wordmark: Path = WORDMARK, avatar: Path = AVATAR) -> str:
    """Wrap a rendered figure in the Capital Commonsense header and footer."""
    theme = theme or Theme()
    lay = lay or ShareLayout()
    _, _, fig_w, fig_h = _viewbox(figure_svg)
    width = fig_w
    shown_h = fig_h - lay.fig_top_trim - lay.fig_bottom_trim
    height = lay.header_h + shown_h + lay.footer_h

    wm_svg = wordmark.read_text(encoding="utf-8")
    _, _, wm_vw, wm_vh = _viewbox(wm_svg)
    wm_w = lay.wordmark_h * wm_vw / wm_vh
    badge_y = (lay.header_h - lay.badge) / 2 + 10
    wm_y = badge_y + (lay.badge - lay.wordmark_h) / 2
    # Optical alignment: shift left by the first glyph's offset so the C sits on the margin.
    first = re.search(r'<use[^>]*\bx="([\d.]+)"', wm_svg)
    wm_x = lay.margin_x - (float(first.group(1)) if first else 0) * lay.wordmark_h / wm_vh

    title = re.search(r"<title>(.*?)</title>", figure_svg, re.S)
    label = html.unescape(title.group(1) if title else "Capital Commonsense chart") + " | Capital Commonsense"

    rule_y = lay.header_h + shown_h + 8
    parts = [
        f'<svg {attrs(xmlns="http://www.w3.org/2000/svg", viewBox=f"0 0 {width:g} {height:g}", width=width, height=height, role="img", aria_label=label)}>',
        f"<title>{html.escape(label, quote=False)}</title>",
        el("rect", width=width, height=height, fill=theme.paper),
        '<g id="figure">' + nest(figure_svg, 0, lay.header_h - lay.fig_top_trim, fig_w, fig_h, "fig-") + "</g>",
        f'<g id="brand-wordmark" data-x="{lay.margin_x:g}" data-w="{wm_w:.2f}">'
        + nest(wm_svg, wm_x, wm_y, wm_w, lay.wordmark_h, "wm-") + "</g>",
        f'<g id="brand-badge" data-x="{width - lay.margin_x - lay.badge:g}" data-w="{lay.badge:g}">'
        + nest(avatar.read_text(encoding="utf-8"), width - lay.margin_x - lay.badge, badge_y,
               lay.badge, lay.badge, "av-") + "</g>",
        el("line", x1=lay.margin_x, x2=width - lay.margin_x, y1=rule_y, y2=rule_y, stroke=theme.ink,
           stroke_width=2),
        text(lay.margin_x, rule_y + 46, SITE_URL, font_size=lay.url_size, fill=theme.ink,
             font_family=theme.sans),
        "</svg>",
    ]
    return "\n".join(parts)
