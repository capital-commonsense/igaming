import re
import xml.etree.ElementTree as ET

import pytest

from dc_igaming.projections import render_projections_svg
from dc_igaming.share import AVATAR, CLEAR_SPACE, SITE_URL, WORDMARK, ShareLayout, brand_frame, nest
from dc_igaming.sources import load_claims, load_manifest

NS = "{http://www.w3.org/2000/svg}"


@pytest.fixture(scope="module")
def figure():
    return render_projections_svg(load_claims(), load_manifest())


@pytest.fixture(scope="module")
def shared(figure):
    return brand_frame(figure)


def test_logo_files_exist():
    assert WORDMARK.exists() and AVATAR.exists()


def test_share_parses_and_includes_brand_and_url(shared):
    root = ET.fromstring(shared)
    labels = {e.get("aria-label") for e in root.iter(f"{NS}svg")}
    assert "Capital Commonsense Wordmark" in labels
    assert "Capital Commonsense Avatar" in labels
    assert SITE_URL in [t.text for t in root.iter(f"{NS}text")]
    assert root.get("aria-label").endswith("| Capital Commonsense")


def test_figure_is_nested_unchanged(figure, shared):
    # Every text label from the plain figure appears in the share version.
    plain = [t.text for t in ET.fromstring(figure).iter(f"{NS}text")]
    share = [t.text for t in ET.fromstring(shared).iter(f"{NS}text")]
    for t in plain:
        assert t in share


def test_logos_drawn_after_figure_so_they_are_not_covered(shared):
    order = [shared.index(f'id="{g}"') for g in ("figure", "brand-wordmark", "brand-badge")]
    assert order == sorted(order)


def test_badge_clear_space(shared):
    lay = ShareLayout()
    root = ET.fromstring(shared)
    width = float(root.get("width"))
    badge_x = width - lay.margin_x - lay.badge
    wm = next(g for g in root.iter(f"{NS}g") if g.get("id") == "brand-wordmark")
    wm_right = float(wm.get("data-x")) + float(wm.get("data-w"))
    assert badge_x - wm_right >= CLEAR_SPACE * lay.badge
    assert width - (badge_x + lay.badge) >= CLEAR_SPACE * lay.badge


def test_nested_ids_are_namespaced(shared):
    ids = re.findall(r'\bid="([^"]+)"', shared)
    assert len(ids) == len(set(ids)), "duplicate ids across nested documents"
    for ref in re.findall(r'href="#([^"]+)"', shared):
        assert ref in ids, ref


def test_nest_replaces_root_size():
    out = nest('<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" width="10pt" height="5pt" '
               'viewBox="0 0 10 5"><rect id="a" fill="url(#a)"/></svg>', 1, 2, 30, 15, "p-")
    assert out.startswith("<svg") and 'width="30"' in out and "10pt" not in out
    assert 'id="p-a"' in out and "url(#p-a)" in out


def test_no_analysis_attribution_in_any_graphic(params):
    from dc_igaming.diagram import default_text, render_one_dollar_svg
    from dc_igaming.flow import FlowInputs, compute_flows, income_tax_equivalent
    from dc_igaming.harms import render_harms_svg

    claims, manifest = load_claims(), load_manifest()
    flows = compute_flows(FlowInputs.from_scenario(params, "central"))
    iit = income_tax_equivalent(flows, params)
    figures = [
        render_one_dollar_svg(flows, iit, default_text(flows, iit, "central")),
        render_projections_svg(claims, manifest),
        render_harms_svg(claims, manifest),
    ]
    for svg in figures + [brand_frame(f) for f in figures]:
        assert not re.search(r"capital commonsense analysis|analysis: capital commonsense", svg, re.I)
