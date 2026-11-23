"""Alt text for every figure, built from the same data that draws it.

Each figure gets a short version (for a CMS alt field, kept under SHORT_LIMIT characters)
and a full version that states every number on the graphic, for screen-reader users who
can't see the chart. The same text applies to the plain and branded share versions: the
logo and site address carry no information that needs describing.

Text is written for screen readers: "×" becomes "times", the minus sign "minus", "¢"
"cents", "~" "about", "·" a comma, and non-breaking spaces ordinary spaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dc_igaming.diagram import ChartText, format_cents
from dc_igaming.flow import Flows, Group, IncomeTaxEquivalent
from dc_igaming.harms import ROW_LABELS, SUBTITLE, TILES, TITLE
from dc_igaming.projections import _money, build_groups, default_title, hit_rate
from dc_igaming.sources import Claim
from dc_igaming.svg import format_usd_precise

SHORT_LIMIT = 250


@dataclass(frozen=True)
class AltText:
    short: str
    full: str

    def render(self, stem: str) -> str:
        return (
            f"ALT TEXT (short, for the image's alt field):\n{self.short}\n\n"
            f"ALT TEXT (full, for a long description or caption):\n{self.full}\n\n"
            f"Applies to {stem}.png and {stem}_share.png (and the .svg versions).\n"
        )


def speakable(s: str) -> str:
    """Spell out symbols that screen readers say badly or not at all."""
    for a, b in (("\u00a0", " "), (" · ", ", "), ("×", " times"), ("−", "minus "), ("¢", " cents"),
                 ("’", "'"), ("–", " to "), ("~", "about "), (" & ", " and ")):
        s = s.replace(a, b)
    return " ".join(s.split())


def _cents(v: float) -> str:
    return speakable(format_cents(v))


def _check(alt: AltText) -> AltText:
    if len(alt.short) > SHORT_LIMIT:
        raise ValueError(f"short alt text is {len(alt.short)} chars (limit {SHORT_LIMIT}): {alt.short}")
    return alt


# ---------------------------------------------------------------- follow one dollar

def one_dollar_alt(flows: Flows, iit: IncomeTaxEquivalent, text: ChartText) -> AltText:
    c = flows.cents()
    shares = flows.shares()
    red = [s for s in shares if s.group is Group.DC_PUBLIC]
    usable = sum(s.cents for s in red)
    net = flows.net_impact_cents()
    lost = 100 * (flows.inputs.lottery_loss + flows.inputs.sports_wagering_loss) / flows.net_loss
    short = (
        f"Diagram: of each $1 DC residents would lose to online casinos, {_cents(c['out_of_state'])} leaves DC "
        f"and the city nets {net:.0f} cents. Every $1 of income tax goes to DC."
    )
    slices = "; ".join(f"{s.label}, {_cents(s.cents)}" for s in shares)
    full = (
        f"{speakable(text.title)}. A flow diagram splits $1 lost by DC players, net of winnings, into where "
        f"it would go under B26-0656, using the DC Chief Financial Officer's estimate for fiscal 2030. "
        f"The splits are: {slices}. "
        f"The slices that reach the city's budget are highlighted in red and total {_cents(usable)}: "
        f"{', '.join(s.label for s in red)}. The regulatory assessment only pays for regulating the market. "
        f"The CFO also expects the city to lose {_cents(lost)} per $1 in lottery and sports-betting revenue, "
        f"so the city nets {net:.1f} cents per $1, or {speakable(format_usd_precise(flows.net_impact))} a year. "
        f"Beside it, a second bar shows that all of $1 paid in income tax goes to DC. "
        f"Dealer pay, vendor spending and the {flows.inputs.jobs:.0f}-job count are assumptions explained in "
        f"the fine print."
    )
    return _check(AltText(speakable(short), speakable(full)))


# ---------------------------------------------------------------- projections

def projections_alt(claims: dict[str, Claim]) -> AltText:
    v = {k: cl.value for k, cl in claims.items()}
    pct = f"{hit_rate(claims):.1%}"
    short = (
        f"Bar chart: DC projected {_money(v['gambetdc_fy2022_projection'])} from its GambetDC sports-betting "
        f"app in FY2022 and got {_money(v['gambetdc_fy2022_actual'])} ({pct}). The CFO projects "
        f"{_money(v['fis_net_impact_fy2030'])} a year net from online casinos."
    )
    parts = []
    for g in build_groups(claims):
        bars = []
        for b in g.bars:
            label = " ".join(b.label)
            value = "unknown" if b.value is None else _money(b.value)
            bars.append(f"{label}: {value}" + (f" ({b.note})" if b.note else ""))
        parts.append(f"{g.title}, {g.subtitle}: " + "; ".join(bars) + ".")
    full = (
        f"{speakable(default_title(claims))}. Bar chart of projected vs. actual gambling revenue to the "
        f"District, in millions of dollars. " + " ".join(parts) + " "
        "GambetDC actuals are net transfers to the District; projections are as reported at the time. "
        "The online casino figure is the CFO's projected net impact on District resources. Lawmakers have "
        "cited $73M in tax over four years. GambetDC was a lottery-run monopoly, while B26-0656 licenses "
        "competing national operators. The chart compares DC's track record and is not a forecast."
    )
    return _check(AltText(speakable(short), speakable(full)))


# ---------------------------------------------------------------- research findings

def harms_alt(claims: dict[str, Claim]) -> AltText:
    lo, hi = claims["bankruptcy"].value
    short = (
        f"Nine research findings on mobile gambling, led by bankruptcy risk up {lo:.0f} to {hi:.0f}% after "
        "online sports betting became legal. Others cover debt, savings, online slots, suicide and "
        "problem gambling."
    )
    rows = []
    per_row = len(TILES) // len(ROW_LABELS)
    for i, label in enumerate(ROW_LABELS):
        tiles = TILES[i * per_row:(i + 1) * per_row]
        items = [f"{t.headline(claims)} {t.harm}, {t.finding} ({t.covers})" for t in tiles]
        rows.append(f"{label}: " + "; ".join(items) + ".")
    full = (
        f"{TITLE}. {SUBTITLE}. A grid of nine findings in three rows. " + " ".join(rows) + " "
        "None of these are DC estimates. The financial findings cover sports betting; few studies "
        "isolate online casino games. The British, New Jersey and Swedish results compare groups of people "
        "and do not show that gambling caused the differences."
    )
    return _check(AltText(speakable(short), speakable(full)))


def write_alt(alt: AltText, figure_path: Path) -> Path:
    """Write <stem>.alt.txt next to the figure."""
    path = figure_path.with_name(f"{figure_path.stem}.alt.txt")
    path.write_text(alt.render(figure_path.stem), encoding="utf-8")
    return path
