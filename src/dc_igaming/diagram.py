"""Render the "Follow one dollar" hero graphic as a brand-styled SVG (and PNG).

Left panel: $1 lost by a DC player fans out into ribbons sized in cents. The
out-of-state ribbon runs off the panel edge in ink.
Right panel: $1 of income tax reaches DC in full, drawn at the same scale.
Red, the single brand emphasis, marks DC tax revenue in both panels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape

from dc_igaming.flow import Flows, Group, IncomeTaxEquivalent, Share
from dc_igaming.layout import Slice, ribbon_path, spread_labels, stack
from dc_igaming.svg import FONT_DIR, PROJECT_ROOT, Theme, format_usd, format_usd_precise, svg_to_png  # noqa: F401 (re-exported)
from dc_igaming.svg import attrs as _attrs
from dc_igaming.svg import text as _text
from dc_igaming.svg import wrap as _wrap
from dc_igaming.textmetrics import measurer


@dataclass(frozen=True)
class Layout:
    width: float = 1600
    height: float = 1000
    margin_x: float = 100
    title_y: float = 116
    subtitle_y: float = 166
    panel_header_y: float = 262
    flow_top: float = 310
    flow_height: float = 500  # pixels for 100 cents
    source_x: float = 200
    bar_width: float = 24
    term_x: float = 720
    term_width: float = 10
    label_pad: float = 22
    panel_a_right: float = 1110
    divider_x: float = 1160
    panel_b_x: float = 1210
    panel_b_term_x: float = 1390
    group_gap: float = 22
    item_gap: float = 6
    min_ribbon: float = 1.5
    label_min_gap: float = 30
    value_size: float = 24
    label_size: float = 20
    note_size: float = 17

    @property
    def px_per_cent(self) -> float:
        return self.flow_height / 100


@dataclass(frozen=True)
class ChartText:
    title: str
    subtitle: str
    notes: list[str] = field(default_factory=list)
    source: str = ""
    panel_a: str = "$1 lost by a DC player"
    panel_b: str = "Or: $1 of income tax"


def format_cents(v: float) -> str:
    """55¢, 21.6¢, 10¢, 0.9¢, 0.12¢: precision falls as the slice grows."""
    if v >= 30:
        s = f"{v:.0f}"
    elif v >= 0.5:
        s = f"{v:.1f}"
        s = s[:-2] if s.endswith(".0") else s
    else:
        s = f"{v:.2f}"
    return f"{s}¢"


def default_text(flows: Flows, iit: IncomeTaxEquivalent, scenario: str,
                 dues_note: str | None = None) -> ChartText:
    """Headline and fine print. Every figure here is computed from the model's inputs."""
    inp = flows.inputs
    net = flows.net_impact_cents()
    usable = 100 * (flows.public_receipts - flows.regulatory) / flows.net_loss
    lost = 100 * (inp.lottery_loss + inp.sports_wagering_loss) / flows.net_loss
    return ChartText(
        title=f"For every dollar DC residents lose, the city nets {net:.0f} cents",
        subtitle=(
            "Where DC residents\u2019 net online casino losses would go under B26-0656, cents per $1 "
            "(DC CFO estimate for fiscal 2030)"
        ),
        panel_a="$1 lost by DC players, net of winnings",
        notes=[
            "How the money is counted: the $1 is DC players\u2019 combined net loss, meaning everything wagered "
            "minus everything paid back as winnings, including to players who finish ahead. That equals operators\u2019 "
            "adjusted gross revenue, the tax base; the committee print doesn\u2019t count promotional credits as "
            f"wagers. The CFO\u2019s fiscal 2030 figures imply {format_usd(flows.net_loss)} a year (each "
            f"{inp.assessment_rate:.0%} assessment is {format_usd_precise(inp.community_impact)}). Every cent is accounted "
            "for: the out-of-state share is what remains.",
            f"What the city gets: a {inp.tax_rate:.0%} tax ({inp.live_dealer_tax_rate:.1%} on live-dealer games; "
            f"the CFO\u2019s figures imply {flows.blended_tax_rate:.2%} overall), with the first "
            f"{format_usd(inp.treatment_setaside)} for addiction services; a {inp.assessment_rate:.0%} community "
            "impact assessment for debt counseling, domestic-violence services, gambling research and youth tech "
            f"training; license fees; and a {inp.assessment_rate:.0%} regulatory assessment that only pays for "
            f"regulating the market. The red slices total {format_cents(usable)}. The CFO also projects the city "
            f"loses {format_usd_precise(inp.lottery_loss + inp.sports_wagering_loss)} a year in lottery and sports-betting "
            f"revenue ({format_cents(lost)} per $1), for a net gain of {format_usd_precise(flows.net_impact)}: "
            f"{net:.1f}\u00a2 per $1.",
            f"Assumes {inp.jobs:.0f} union dealer jobs (the committee\u2019s estimate; the bill requires live-dealer "
            f"games in a DC studio) at {format_usd(inp.comp_per_job)} each, fully loaded, and "
            f"{format_usd(inp.local_vendor_spend)} a year in DC vendor spending. Raising the same "
            f"{format_usd_precise(flows.net_impact)} through income tax would take a {iit.pct_increase:.2f}% increase.",
            *([dues_note] if dues_note else []),
        ],
        source=(
            "Sources: DC Chief Financial Officer, fiscal impact statement on the B26-0656 committee print "
            "(Nov. 18, 2026); committee print racial equity impact assessment; committee jobs estimate via Axios DC "
            "(Nov. 18, 2026); UNITE HERE Local 25 2025 LM-2 filing (U.S. Dept. of Labor); DC CFO June 2026 "
            "revenue estimate."
        ),
    )


def dues_basis_note(flows: Flows, claims: dict) -> str:
    """Fine print for the union-dues slice, built from the LM-2 claims so it can't drift."""
    lo, hi = claims["local25_dues_rate_2025"].value
    receipts = claims["local25_dues_receipts_2025"].value
    members = claims["local25_members_2025"].value
    inp = flows.inputs
    return (
        f"Union dues: ${hi:.0f} a month (${inp.union_dues_per_member:,.0f} a year) per dealer, the top of the "
        f"regular dues range (${lo:.2f}\u2013${hi:.2f} a month) UNITE HERE Local 25 reported to the U.S. "
        f"Department of Labor for 2025. That matches the local's actual 2025 dues receipts: "
        f"{format_usd(receipts)} from {members:,.0f} members, or ${receipts / members:,.0f} each. "
        f"{inp.jobs:.0f} dealers would pay {format_usd(flows.dues)} a year, "
        f"{format_cents(flows.cents()['union_dues'])} of each $1 residents lose."
    )


# Tax ribbons are solid so the red emphasis reads at full strength; out-of-state is
# slightly softened ink; everything else is a translucent tint of its terminal color.
RIBBON_OPACITY = {Group.DC_PUBLIC: 1.0, Group.LEAVES_DC: 0.88, Group.DC_REGULATION: 0.9}


# --------------------------------------------------------------------------- geometry


@dataclass(frozen=True)
class OneDollarGeometry:
    left: list[Slice]
    right: list[Slice]
    label_y: dict[str, float]
    shares: list[Share]


def compute_geometry(shares: list[Share], lay: Layout) -> OneDollarGeometry:
    keys = [s.key for s in shares]
    heights = [max(s.cents * lay.px_per_cent, lay.min_ribbon) for s in shares]
    left = stack(keys, heights, lay.flow_top)
    gaps = [0.0] + [
        lay.group_gap if shares[i].group != shares[i - 1].group else lay.item_gap
        for i in range(1, len(shares))
    ]
    right_total = sum(heights) + sum(gaps)
    right_top = lay.flow_top + (sum(heights) - right_total) / 2
    right = stack(keys, heights, right_top, gaps)

    # Labels for every slice except the red one (labelled inside its ribbon).
    labelled = [sl for sl, sh in zip(right, shares, strict=True) if sh.group != Group.LEAVES_DC]
    leaves = [sl for sl, sh in zip(right, shares, strict=True) if sh.group == Group.LEAVES_DC]
    lo = (max(sl.bottom for sl in leaves) if leaves else lay.flow_top) + lay.label_min_gap * 0.6
    hi = lay.flow_top + lay.flow_height + 2 * lay.label_min_gap
    ys = spread_labels([sl.mid for sl in labelled], lay.label_min_gap, lo, hi)
    return OneDollarGeometry(left, right, {sl.key: y for sl, y in zip(labelled, ys, strict=True)}, shares)


# --------------------------------------------------------------------------- render


def render_one_dollar_svg(
    flows: Flows,
    iit: IncomeTaxEquivalent,
    text: ChartText,
    theme: Theme | None = None,
    lay: Layout | None = None,
) -> str:
    theme = theme or Theme()
    lay = lay or Layout()
    shares = flows.shares()
    geo = compute_geometry(shares, lay)
    bold_m = measurer(str(theme.sans_bold_font_file))

    sans = dict(font_family=theme.sans)

    def red_if_public(group: Group) -> str:
        return theme.red if group == Group.DC_PUBLIC else theme.ink

    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" {_attrs(viewBox=f"0 0 {lay.width:g} {lay.height:g}", width=lay.width, height=lay.height, role="img")} aria-label="{escape(text.title)}">',
        f"<title>{escape(text.title)}</title>",
        "<defs>"
        f'<linearGradient id="offEdge" x1="0" x2="1" y1="0" y2="0">'
        f'<stop offset="0" stop-color="{theme.ink}" stop-opacity="{RIBBON_OPACITY[Group.LEAVES_DC]}"/>'
        f'<stop offset="1" stop-color="{theme.ink}" stop-opacity="0"/>'
        "</linearGradient></defs>",
        f'<rect {_attrs(width=lay.width, height=lay.height, fill=theme.paper)}/>',
    ]

    # Title block
    out.append(_text(lay.margin_x, lay.title_y, text.title, font_family=theme.serif,
                     font_weight=700, font_size=50, fill=theme.ink))
    out.append(_text(lay.margin_x, lay.subtitle_y, text.subtitle, font_size=23, fill=theme.muted, **sans))

    # Panel headers and divider
    out.append(_text(lay.margin_x, lay.panel_header_y, text.panel_a, font_size=22, font_weight=600,
                     fill=theme.ink, **sans))
    out.append(_text(lay.panel_b_x, lay.panel_header_y, text.panel_b, font_size=22, font_weight=600,
                     fill=theme.ink, **sans))
    out.append(f'<line {_attrs(x1=lay.divider_x, x2=lay.divider_x, y1=lay.panel_header_y - 24, y2=lay.flow_top + lay.flow_height + 70, stroke=theme.rule, stroke_width=2)}/>')

    # Source bar + "$1"
    x0 = lay.source_x + lay.bar_width
    out.append(f'<rect {_attrs(x=lay.source_x, y=lay.flow_top, width=lay.bar_width, height=lay.flow_height, fill=theme.ink)}/>')
    out.append(_text(lay.source_x - 16, lay.flow_top + lay.flow_height / 2 + 22, "$1",
                     font_family=theme.serif, font_weight=700, font_size=64, fill=theme.ink,
                     text_anchor="end"))

    # Ribbons
    out.append('<g id="ribbons">')
    for sh, l_sl, r_sl in zip(shares, geo.left, geo.right, strict=True):
        color = theme.group_color(sh.group)
        opacity = RIBBON_OPACITY.get(sh.group, 0.55)
        d = ribbon_path(x0, l_sl.top, l_sl.bottom, lay.term_x, r_sl.top, r_sl.bottom)
        out.append(f'<path {_attrs(d=d, fill=color, fill_opacity=opacity, data_key=sh.key)}/>')
    out.append("</g>")

    # Terminals, labels, and the off-edge run for the out-of-state slice
    value_col = max(bold_m.width(format_cents(s.cents), lay.value_size)
                    for s in shares if s.group != Group.LEAVES_DC)
    label_x = lay.term_x + lay.term_width + lay.label_pad
    out.append('<g id="terminals">')
    for sh, r_sl in zip(shares, geo.right, strict=True):
        color = theme.group_color(sh.group)
        if sh.group == Group.LEAVES_DC:
            out.append(f'<rect {_attrs(x=lay.term_x, y=r_sl.top, width=lay.panel_a_right - lay.term_x, height=r_sl.height, fill="url(#offEdge)", data_key=sh.key)}/>')
            out.extend(_inside_label(sh, geo.left[0], r_sl, x0, lay, theme))
            continue
        out.append(f'<rect {_attrs(x=lay.term_x, y=r_sl.top, width=lay.term_width, height=max(r_sl.height, lay.min_ribbon), fill=color, data_key=sh.key)}/>')
        ly = geo.label_y[sh.key]
        if abs(ly - r_sl.mid) > 2:
            out.append(f'<polyline {_attrs(points=f"{lay.term_x + lay.term_width + 3:.1f},{r_sl.mid:.1f} {label_x - 6:.1f},{ly:.1f}", fill="none", stroke=theme.muted, stroke_width=1)}/>')
        baseline = ly + lay.value_size * 0.35
        out.append(_text(label_x + value_col, baseline, format_cents(sh.cents), font_size=lay.value_size,
                         font_weight=600, fill=red_if_public(sh.group), text_anchor="end",
                         data_key=sh.key, **sans))
        out.append(_text(label_x + value_col + 12, baseline, sh.label, font_size=lay.label_size,
                         fill=theme.muted, **sans))
    out.append("</g>")

    # Panel B: income tax, same scale, all of it reaches DC
    bx0 = lay.panel_b_x
    bx1 = lay.panel_b_term_x
    top, bot = lay.flow_top, lay.flow_top + lay.flow_height
    out.append('<g id="income-tax">')
    out.append(f'<rect {_attrs(x=bx0, y=top, width=lay.bar_width, height=lay.flow_height, fill=theme.ink)}/>')
    out.append(f'<path {_attrs(d=ribbon_path(bx0 + lay.bar_width, top, bot, bx1, top, bot), fill=theme.red, data_key="income_tax")}/>')
    out.append(f'<rect {_attrs(x=bx1, y=top, width=lay.term_width, height=lay.flow_height, fill=theme.red, data_key="income_tax")}/>')
    mid = (top + bot) / 2
    tx = bx1 + lay.term_width + 18
    out.append(_text(tx, mid - 6, format_cents(iit.cents_to_dc), font_size=40, font_weight=600,
                     fill=theme.red, data_key="income_tax", **sans))
    out.append(_text(tx, mid + 26, "to DC", font_size=lay.label_size, fill=theme.muted, **sans))
    out.append("</g>")

    # Footer notes + source; the canvas grows to fit them.
    y = lay.flow_top + lay.flow_height + 110
    max_w = lay.width - 2 * lay.margin_x
    blocks = [*text.notes, text.source] if text.source else list(text.notes)
    for i, block in enumerate(blocks):
        if i > 0:
            y += 8
        for line in _wrap(block, max_w, lay.note_size, theme.sans_font_file):
            out.append(_text(lay.margin_x, y, line, font_size=lay.note_size, fill=theme.muted, **sans))
            y += lay.note_size * 1.45
    height = max(lay.height, y + 40)
    out[0] = out[0].replace(f"0 0 {lay.width:g} {lay.height:g}", f"0 0 {lay.width:g} {height:g}")
    out[0] = out[0].replace(f'height="{lay.height:g}"', f'height="{height:g}"')
    out[3] = out[3].replace(f'height="{lay.height:g}"', f'height="{height:g}"')

    out.append("</svg>")
    return "\n".join(out)


def _inside_label(sh: Share, left: Slice, right: Slice, x0: float, lay: Layout, theme: Theme) -> list[str]:
    """White '55¢ / leaves DC' set inside the out-of-state ribbon, near the start of the curve."""
    cx = x0 + (lay.term_x - x0) * 0.42
    # Ribbon edges at cx are close to the average of the two ends; good enough for centering.
    top = (left.top + right.top) / 2
    bot = (left.bottom + right.bottom) / 2
    mid = (top + bot) / 2
    sans = dict(font_family=theme.sans, fill=theme.paper, text_anchor="middle")
    return [
        _text(cx, mid + 10, format_cents(sh.cents), font_size=76, font_weight=600, data_key=sh.key, **sans),
        _text(cx, mid + 50, "leaves DC", font_size=26, font_weight=600, **sans),
        _text(cx, mid + 80, "out-of-state operators & suppliers", font_size=18, **sans),
    ]
