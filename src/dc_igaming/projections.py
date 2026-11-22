"""Figure: DC's gambling revenue projections vs. what actually arrived.

Groups of bars on one $M axis:
  GambetDC FY2021  - 2018 projection, Feb. 2021 revision, actual net transfer ($0)
  GambetDC FY2022  - projection, actual net transfer (the single red emphasis)
  Online casino    - committee projection, and a dashed "?" box for the unknown actual
Every value comes from data/claims.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from dc_igaming.sources import Claim, Source
from dc_igaming.svg import Theme, document, el, fit_font_size, footer, text, wrap


@dataclass(frozen=True)
class Bar:
    key: str
    label: tuple[str, ...]  # one or two lines under the bar
    value: float | None  # None = unknown actual
    kind: str  # projection | actual | unknown
    emphasis: bool = False
    note: str | None = None  # small line above the value label


@dataclass(frozen=True)
class BarGroup:
    title: str
    subtitle: str
    bars: tuple[Bar, ...]


def build_groups(claims: dict[str, Claim]) -> list[BarGroup]:
    v = {k: c.value for k, c in claims.items()}
    hit = v["gambetdc_fy2022_actual"] / v["gambetdc_fy2022_projection"]
    return [
        BarGroup("GambetDC sports betting", "FY2021", (
            Bar("gambetdc_fy2021_projection_2018", ("Projected", "Nov. 2018"),
                v["gambetdc_fy2021_projection_2018"], "projection"),
            Bar("gambetdc_fy2021_projection_2021", ("Revised", "Feb. 2021"),
                v["gambetdc_fy2021_projection_2021"], "projection"),
            Bar("gambetdc_fy2021_actual", ("Actual",), v["gambetdc_fy2021_actual"], "actual",
                note=f"lost ${v['gambetdc_fy2021_loss'] / 1e6:.0f}M"),
        )),
        BarGroup("GambetDC sports betting", "FY2022", (
            Bar("gambetdc_fy2022_projection", ("Projected",), v["gambetdc_fy2022_projection"], "projection"),
            Bar("gambetdc_fy2022_actual", ("Actual",), v["gambetdc_fy2022_actual"], "actual",
                emphasis=True, note=f"{hit:.1%} of estimate"),
        )),
        BarGroup("Online casino (B26-0656)", "fiscal 2030", (
            Bar("fis_net_impact_fy2030", ("Projected", "(DC CFO)"), v["fis_net_impact_fy2030"], "projection"),
            Bar("igaming_actual", ("Actual",), None, "unknown"),
        )),
    ]


def hit_rate(claims: dict[str, Claim]) -> float:
    return claims["gambetdc_fy2022_actual"].value / claims["gambetdc_fy2022_projection"].value


def default_title(claims: dict[str, Claim]) -> str:
    cents = f"{hit_rate(claims) * 100:.1f}".rstrip("0").rstrip(".")
    return f"DC’s last gambling forecast delivered {cents} cents on the dollar"


def _money(v: float) -> str:
    """$27M, $6.2M, $0. Rounds half up, so $18.25M prints as $18.3M (as in the flow model)."""
    if v == 0:
        return "$0"
    m = Decimal(str(v)) / Decimal(1_000_000)
    tenth = m.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"${tenth:.0f}M" if tenth == tenth.to_integral_value() and m >= 10 else f"${tenth}M"


def render_projections_svg(claims: dict[str, Claim], sources: dict[str, Source],
                           theme: Theme | None = None, width: float = 1600) -> str:
    theme = theme or Theme()
    groups = build_groups(claims)
    sans = dict(font_family=theme.sans)
    mx = 100
    body: list[str] = []

    # Title: shrink (down to 42px) to stay on one line, wrap only if it still won't fit.
    title = default_title(claims)
    size = fit_font_size(title, width - 2 * mx, theme.serif_font_file, start=50, minimum=42)
    y = 112
    for line in wrap(title, width - 2 * mx, size, theme.serif_font_file):
        body.append(text(mx, y, line, font_family=theme.serif, font_weight=700, font_size=size, fill=theme.ink))
        y += size * 1.2
    body.append(text(mx, y - 6, "Projected vs. actual gambling revenue to the District, millions of dollars",
                     font_size=23, fill=theme.muted, **sans))

    # Axis
    top, base = y + 90, y + 520
    x0, x1 = mx + 80, width - mx
    y_max = 30e6
    tick = 10e6

    def ypos(val: float) -> float:
        return base - (base - top) * val / y_max

    t = 0.0
    while t <= y_max + 1:
        yy = ypos(t)
        body.append(el("line", x1=x0, x2=x1, y1=yy, y2=yy, stroke=theme.rule, stroke_width=2))
        body.append(text(x0 - 14, yy + 6, _money(t), font_size=18, fill=theme.muted, text_anchor="end", **sans))
        t += tick

    # Bars
    bar_w, bar_gap, group_gap = 120, 18, 110
    n_bars = sum(len(g.bars) for g in groups)
    total = n_bars * bar_w + sum(len(g.bars) - 1 for g in groups) * bar_gap + (len(groups) - 1) * group_gap
    x = x0 + ((x1 - x0) - total) / 2
    for g in groups:
        gx0 = x
        for b in g.bars:
            cx = x + bar_w / 2
            if b.kind == "unknown":
                ref = next(bb for bb in g.bars if bb.kind == "projection").value
                h = base - ypos(ref)
                body.append(el("rect", x=x + 1.5, y=base - h + 1.5, width=bar_w - 3, height=h - 1.5, fill="none",
                               stroke=theme.ink, stroke_width=3, stroke_dasharray="10 8", data_key=b.key))
                body.append(text(cx, base - h / 2 + 30, "?", font_family=theme.serif, font_weight=700,
                                 font_size=96, fill=theme.ink, text_anchor="middle", data_key=b.key))
                body.append(text(cx, base - h - 14, "Unknown", font_size=22, font_weight=600, fill=theme.ink,
                                 text_anchor="middle", **sans))
            else:
                color = theme.red if b.emphasis else (theme.ink if b.kind == "actual" else theme.players)
                h = max(base - ypos(b.value), 3)
                body.append(el("rect", x=x, y=base - h, width=bar_w, height=h, fill=color, data_key=b.key))
                label_color = theme.red if b.emphasis else theme.ink
                body.append(text(cx, base - h - 14, _money(b.value), font_size=26, font_weight=600,
                                 fill=label_color, text_anchor="middle", data_key=b.key, **sans))
                if b.note:
                    body.append(text(cx, base - h - 46, b.note, font_size=17, fill=label_color,
                                     text_anchor="middle", **sans))
            for i, line in enumerate(b.label):
                body.append(text(cx, base + 30 + i * 21, line, font_size=17, fill=theme.muted,
                                 text_anchor="middle", **sans))
            x += bar_w + bar_gap
        x -= bar_gap
        gcx = (gx0 + x) / 2
        body.append(text(gcx, base + 92, g.title, font_size=20, font_weight=600, fill=theme.ink,
                         text_anchor="middle", **sans))
        body.append(text(gcx, base + 116, g.subtitle, font_size=18, fill=theme.muted, text_anchor="middle", **sans))
        x += group_gap
    body.append(el("line", x1=x0, x2=x1, y1=base, y2=base, stroke=theme.ink, stroke_width=2))

    # Footer
    c = claims
    notes = [
        "GambetDC actuals are net transfers to the District reported by the DC Office of Lottery and "
        f"Gaming. In FY2021 GambetDC made no net transfer and lost ${c['gambetdc_fy2021_loss'].value / 1e6:.0f}M. "
        "Projections are as reported at the time. The online casino figure is the DC Chief Financial "
        "Officer\u2019s projected net impact on District resources in fiscal 2030, from its fiscal impact "
        "statement on the committee print. Lawmakers have cited $73M in tax over four years, and another "
        f"analysis cited at markup put it near {_money(c['igaming_other_estimate'].value)} a year.",
        "GambetDC was a lottery-run monopoly. B26-0656 licenses competing national operators, so it may "
        "come closer to its estimate, which would mean residents lose more. This compares DC's track "
        "record; it is not a forecast.",
    ]
    used = dict.fromkeys(claims[k].source for g in groups for b in g.bars if b.key in claims for k in [b.key])
    used.update(dict.fromkeys([c["gambetdc_fy2021_loss"].source, c["igaming_committee_estimate"].source,
                               c["igaming_other_estimate"].source]))
    notes.append("Sources: " + "; ".join(sources[s].short_citation() for s in used) + ".")
    foot, end_y = footer(notes, base + 180, mx, width - 2 * mx, theme)
    body += foot
    return document(body, width, end_y + 30, title, theme)
