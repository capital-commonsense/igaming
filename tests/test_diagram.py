import re
import xml.etree.ElementTree as ET

import pytest

from dc_igaming.diagram import (
    FONT_DIR,
    Layout,
    Theme,
    compute_geometry,
    default_text,
    format_cents,
    render_one_dollar_svg,
)
from dc_igaming.flow import income_tax_equivalent
from dc_igaming.textmetrics import TextMeasurer

NS = {"s": "http://www.w3.org/2000/svg"}


@pytest.fixture(scope="module")
def svg(central, params):
    iit = income_tax_equivalent(central, params)
    return render_one_dollar_svg(central, iit, default_text(central, iit, "central"))


@pytest.fixture(scope="module")
def root(svg):
    return ET.fromstring(svg)


@pytest.mark.parametrize(("v", "s"), [
    (55.2, "55¢"), (21.58, "21.6¢"), (10.0, "10¢"), (8.48, "8.5¢"),
    (0.92, "0.9¢"), (0.123, "0.12¢"), (100, "100¢"),
])
def test_format_cents(v, s):
    assert format_cents(v) == s


def test_svg_is_well_formed_with_title(root, svg):
    assert root.tag.endswith("svg")
    assert "the city nets 24 cents" in root.find("s:title", NS).text


def test_every_destination_value_is_labelled(root, central):
    texts = {t.text for t in root.iter("{http://www.w3.org/2000/svg}text")}
    for s in central.shares():
        assert format_cents(s.cents) in texts, s.key
        if s.key != "out_of_state":
            assert s.label in texts, s.key
    assert "100¢" in texts
    assert any(t and t.startswith("Sources:") for t in texts)


def test_red_marks_only_dc_tax_revenue(svg, central):
    # Brand rule: red marks one point of emphasis, here DC tax revenue in both panels.
    public = {s.key for s in central.shares() if s.group.value == "dc_public"} | {"income_tax"}
    red_tags = re.findall(r"<(?:path|rect|text)[^>]*#D43D29[^>]*>", svg)
    assert red_tags
    for tag in red_tags:
        key = re.search(r'data-key="([^"]+)"', tag)
        assert key and key.group(1) in public, tag
    assert "stop-color=\"#D43D29\"" not in svg  # out-of-state fade is no longer red
    # Both headline figures are red.
    for value in (format_cents(central.cents()["tax_general"]), "100¢"):
        assert re.search(rf'<text[^>]*fill="#D43D29"[^>]*>{re.escape(value)}</text>', svg), value


def test_ribbon_heights_proportional_to_cents(central):
    lay = Layout()
    geo = compute_geometry(central.shares(), lay)
    for sh, sl in zip(central.shares(), geo.left, strict=True):
        expected = max(sh.cents * lay.px_per_cent, lay.min_ribbon)
        assert sl.height == pytest.approx(expected)
    # Left stack is contiguous and spans ~100 cents (plus hairline minimums).
    assert geo.left[0].top == lay.flow_top
    assert geo.left[-1].bottom == pytest.approx(lay.flow_top + lay.flow_height, abs=2)


def test_labels_do_not_overlap_and_stay_below_red_band(central):
    lay = Layout()
    geo = compute_geometry(central.shares(), lay)
    ys = list(geo.label_y.values())
    assert all(b - a >= lay.label_min_gap - 1e-6 for a, b in zip(ys, ys[1:], strict=False))
    red_bottom = geo.right[0].bottom
    assert min(ys) - lay.value_size > red_bottom


def test_labels_fit_inside_panel_a(central):
    lay, theme = Layout(), Theme()
    reg = TextMeasurer(theme.sans_font_file)
    bold = TextMeasurer(theme.sans_bold_font_file)
    value_col = max(bold.width(format_cents(s.cents), lay.value_size) for s in central.shares()[1:])
    x = lay.term_x + lay.term_width + lay.label_pad + value_col + 12
    for s in central.shares()[1:]:
        assert x + reg.width(s.label, lay.label_size) < lay.divider_x - 10, s.label


def test_canvas_grows_to_fit_footer(root):
    vb = [float(v) for v in root.get("viewBox").split()]
    last_text_y = max(float(t.get("y")) for t in root.iter("{http://www.w3.org/2000/svg}text"))
    assert vb[3] >= last_text_y + 20
    assert float(root.get("height")) == vb[3]


def test_brand_fonts_present_and_measured():
    assert FONT_DIR.is_dir()
    m = TextMeasurer(Theme().sans_font_file)
    assert m.uses_font
    assert m.width("WWW", 20) > m.width("iii", 20)


def test_measurer_falls_back_without_font():
    m = TextMeasurer(None)
    assert not m.uses_font
    assert m.width("abcd", 10) == pytest.approx(4 * 10 * 0.56)


def test_headline_is_collective_and_net(central, params):
    iit = income_tax_equivalent(central, params)
    t = default_text(central, iit, "central")
    assert t.title == "For every dollar DC residents lose, the city nets 24 cents"
    assert "net of winnings" in t.panel_a
    assert "fiscal 2030" in t.subtitle


def test_footnote_explains_accounting_and_reconciles_to_net(central, params):
    iit = income_tax_equivalent(central, params)
    note = " ".join(default_text(central, iit, "central").notes)
    assert "everything wagered minus everything paid back as winnings" in note
    assert "doesn’t count promotional credits as wagers" in note
    assert "$66.8M a year" in note and "$1.34M" in note
    assert "12.5% on live-dealer games" in note and "24.05% overall" in note
    assert "red slices total 26.3¢" in note
    assert "$1.65M a year in lottery and sports-betting revenue" in note
    assert "net gain of $15.90M: 23.8¢ per $1" in note
    assert "income tax would take" not in note
    for unsourced in ("UC San Diego", "96%", "house hold", "Pennsylvania", "come out ahead", "$73"):
        assert unsourced not in note, unsourced


def test_dues_note_states_lm2_basis(central):
    from dc_igaming.diagram import dues_basis_note
    from dc_igaming.sources import load_claims

    note = dues_basis_note(central, load_claims())
    for s in ("$105 a month", "$1,260 a year", "$59.92–$105.00", "UNITE HERE Local 25",
              "Department of Labor for 2025", "6,101 members", "$1,274 each", "0.19¢"):
        assert s in note, s


def test_sankey_has_no_internal_file_paths(central, params):
    iit = income_tax_equivalent(central, params)
    svg = render_one_dollar_svg(central, iit, default_text(central, iit, "central"))
    assert ".yaml" not in svg
