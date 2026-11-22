"""Figure: a grid of research findings on harms from app-based gambling.

Nine tiles in three rows (money, violence & health, help-seeking). Each tile carries a
headline number computed from data/claims.yaml, the harm it measures, a one-sentence finding, what kind of
gambling the study covers, and a short citation. One tile (bankruptcy) gets the single
red emphasis.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from dc_igaming.sources import Claim, Source
from dc_igaming.svg import Theme, document, el, footer, text, wrap
from dc_igaming.textmetrics import measurer

TITLE = "What researchers find when gambling moves onto phones"
SUBTITLE = "Research and help-seeking data from outside DC"


@dataclass(frozen=True)
class Tile:
    claim: str
    headline: Callable[[dict[str, Claim]], str]
    harm: str  # names the harm, set under the number in the headline
    finding: str
    covers: str  # what kind of gambling the evidence is about
    extra_claims: tuple[str, ...] = ()
    emphasis: bool = False

    def sources(self, claims: dict[str, Claim]) -> list[str]:
        return list(dict.fromkeys(claims[c].source for c in (self.claim, *self.extra_claims)))


def _v(cid: str) -> Callable[[dict[str, Claim]], object]:
    return lambda c: c[cid].value


def _ratio_floor(cid: str) -> Callable[[dict[str, Claim]], str]:
    """'10×' from [before, after]. Rounded down so the tile never overstates."""
    def f(c: dict[str, Claim]) -> str:
        before, after = c[cid].value
        return f"{int(after // before)}×"
    return f


def _pct_increase_floor(cid: str) -> Callable[[dict[str, Claim]], str]:
    """'+87%' from [before, after]. Rounded down so the tile never overstates."""
    def f(c: dict[str, Claim]) -> str:
        before, after = c[cid].value
        return f"+{int(100 * (after - before) // before)}%"
    return f


TILES: tuple[Tile, ...] = (
    # Row 1: money
    Tile("bankruptcy",
         lambda c: f"+{c['bankruptcy'].value[0]:.0f}–{c['bankruptcy'].value[1]:.0f}%",
         "bankruptcy risk",
         "at the high end, three to four years after a state's online sports betting launch",
         "Online sports betting · ~7M consumers", extra_claims=("hollenbeck_sample",), emphasis=True),
    Tile("collections", lambda c: f"+{c['collections'].value:.0f}%",
         "debt in collections",
         "approximate rise in the average amount owed after online sports betting became legal",
         "Online sports betting · ~7M consumers", extra_claims=("hollenbeck_sample",)),
    Tile("investment_crowd_out", lambda c: f"−${c['investment_crowd_out'].value:.2f}",
         "investment/savings",
         "for every $1 bet on sports online. Among strapped households, card debt and overdrafts rise",
         "Online sports betting · bank transactions", extra_claims=("constrained_households", "baker_data")),
    # Row 2: violence, health, concentration
    Tile("ipv", lambda c: f"+{c['ipv'].value[0]:g}–{c['ipv'].value[1]:g}%",
         "domestic violence",
         "where sports betting is legal, in reported partner violence after NFL home-team upsets: a "
         "bigger spike than where betting isn't legal",
         "Sports betting · police reports, 2011–2022", extra_claims=("ipv_data",)),
    Tile("suicide", lambda c: f"{c['suicide'].value:.0f}×",
         "suicide mortality",
         "vs. the general population, among Swedish patients aged 20–74 with diagnosed gambling disorder",
         "Association · Swedish clinical cohort", extra_claims=("karlsson_data",)),
    Tile("anj_concentration", lambda c: f"{c['anj_concentration'].value[1]:.0f}%",
         "from problem gamblers",
         "of French online and account-based gambling revenue came from the 8.7% of players flagged "
         "as likely problem gamblers",
         "Online + account-based gambling · France, H2 2025"),
    # Row 3: problem gambling and help-seeking
    Tile("nj_venue_disorder", _ratio_floor("nj_venue_disorder"),
         "gambling-disorder rate",
         "among New Jersey gamblers who bet only online (11.3%) vs. only in person (1.1%)",
         "Association · New Jersey, 2020–21 survey", extra_claims=("nj_survey_dates",)),
    Tile("ct_helpline", _pct_increase_floor("ct_helpline"),
         "helpline calls",
         "and texts to Connecticut's problem-gambling helpline, Nov. 2021 vs. Nov. 2020",
         "Online casino + sports betting · Connecticut", extra_claims=("ct_products",)),
    Tile("pa_helpline", lambda c: f"{c['pa_helpline'].value:.0f}%+",
         "online-gambling calls",
         "of calls to Pennsylvania's problem-gambling helpline involved problematic online gambling",
         "Online casino + sports betting · Pennsylvania", extra_claims=("pa_products",)),
)

ROW_LABELS = ("Money", "Violence, health and who pays", "Problem gambling")


def render_harms_svg(claims: dict[str, Claim], sources: dict[str, Source],
                     theme: Theme | None = None, width: float = 1600) -> str:
    theme = theme or Theme()
    sans = dict(font_family=theme.sans)
    mx = 100
    body: list[str] = []
    body.append(text(mx, 112, TITLE, font_family=theme.serif, font_weight=700, font_size=50, fill=theme.ink))
    body.append(text(mx, 160, SUBTITLE, font_size=23, fill=theme.muted, **sans))

    cols, col_gap = 3, 48
    tile_w = (width - 2 * mx - (cols - 1) * col_gap) / cols
    finding_size, finding_max_lines = 19, 3
    harm_size = 36
    tile_h = 316
    y = 220
    for row in range(len(TILES) // cols):
        body.append(text(mx, y, ROW_LABELS[row].upper(), font_size=15, font_weight=600, fill=theme.muted,
                         letter_spacing=1.5, **sans))
        y += 18
        for col in range(cols):
            tile = TILES[row * cols + col]
            x = mx + col * (tile_w + col_gap)
            accent = theme.red if tile.emphasis else theme.ink
            body.append(el("line", x1=x, x2=x + tile_w, y1=y, y2=y, stroke=accent if tile.emphasis else theme.ink,
                           stroke_width=3))
            body.append(text(x, y + 78, tile.headline(claims), font_family=theme.serif, font_weight=700,
                             font_size=68, fill=accent, data_key=tile.claim))
            if measurer(str(theme.serif_font_file)).width(tile.harm, harm_size) > tile_w:
                raise ValueError(f"{tile.claim}: harm label too wide; shorten it")
            body.append(text(x, y + 124, tile.harm, font_family=theme.serif, font_weight=700,
                             font_size=harm_size, fill=accent, data_key=tile.claim))
            lines = wrap(tile.finding, tile_w, finding_size, theme.sans_font_file)
            if len(lines) > finding_max_lines:
                raise ValueError(f"{tile.claim}: finding wraps to {len(lines)} lines; shorten it")
            for i, line in enumerate(lines):
                body.append(text(x, y + 164 + i * 26, line, font_size=finding_size, fill=theme.ink, **sans))
            meta_y = y + 164 + finding_max_lines * 26 + 8
            body.append(text(x, meta_y, tile.covers, font_size=15, font_weight=600, fill=theme.muted, **sans))
            cite = "; ".join(sources[s].short_citation() for s in tile.sources(claims))
            for i, line in enumerate(wrap(cite, tile_w, 15, theme.sans_font_file)):
                body.append(text(x, meta_y + 21 + i * 20, line, font_size=15, fill=theme.muted,
                                 data_cite=tile.claim, **sans))
        y += tile_h

    notes = [
        "None of these are DC estimates. The financial and NFL findings cover sports betting; few studies "
        "isolate online casino games. Connecticut launched online casino games and sports betting together. "
        "Helpline figures measure service contacts. The New Jersey and Swedish results compare groups of "
        "people and do not show that gambling caused the differences.",
        "Sources as cited in each panel.",
    ]
    foot, end_y = footer(notes, y + 10, mx, width - 2 * mx, theme)
    body += foot
    return document(body, width, end_y + 30, TITLE, theme)
