"""Rendering tests for the projections and research-findings figures."""

import re
import xml.etree.ElementTree as ET

import pytest

from dc_igaming.harms import TILES, TITLE, render_harms_svg
from dc_igaming.projections import _money, build_groups, default_title, hit_rate, render_projections_svg
from dc_igaming.sources import load_claims, load_manifest

NS = "{http://www.w3.org/2000/svg}"
RED = "#D43D29"


@pytest.fixture(scope="module")
def claims():
    return load_claims()


@pytest.fixture(scope="module")
def manifest():
    return load_manifest()


def _texts(svg):
    return [t.text or "" for t in ET.fromstring(svg).iter(f"{NS}text")]


def _red_keys(svg):
    tags = re.findall(rf"<(?:rect|text|path)[^>]*{RED}[^>]*>", svg)
    return {m.group(1) for t in tags if (m := re.search(r'data-key="([^"]+)"', t))}, tags


# ---------------------------------------------------------------- projections

@pytest.fixture(scope="module")
def proj_svg(claims, manifest):
    return render_projections_svg(claims, manifest)


@pytest.mark.parametrize(("v", "s"), [
    (27e6, "$27M"), (20e6, "$20M"), (6.2e6, "$6.2M"), (2.7e6, "$2.7M"), (0, "$0"),
    (18.25e6, "$18.3M"), (50e6, "$50M"), (10e6, "$10M"),
])
def test_money_format_rounds_half_up(v, s):
    assert _money(v) == s


def test_hit_rate_and_title(claims):
    assert hit_rate(claims) == pytest.approx(0.135)
    assert "13.5 cents on the dollar" in default_title(claims)


def test_projections_svg_parses_and_shows_every_value(proj_svg):
    texts = _texts(proj_svg)
    for label in ("$27M", "$6.2M", "$0", "$20M", "$2.7M", "$15.9M", "?", "Unknown", "13.5% of estimate"):
        assert label in texts, label


def test_projection_bars_are_proportional(claims, proj_svg):
    root = ET.fromstring(proj_svg)
    heights = {r.get("data-key"): float(r.get("height")) for r in root.iter(f"{NS}rect") if r.get("data-key")}
    ratio = heights["gambetdc_fy2022_actual"] / heights["gambetdc_fy2022_projection"]
    assert ratio == pytest.approx(0.135, abs=0.005)
    assert heights["gambetdc_fy2021_projection_2018"] > heights["gambetdc_fy2022_projection"]
    # The unknown box is drawn at the projection's height.
    assert heights["igaming_actual"] == pytest.approx(heights["fis_net_impact_fy2030"], abs=2)


def test_projections_red_marks_only_fy2022_actual(proj_svg):
    keys, tags = _red_keys(proj_svg)
    assert keys == {"gambetdc_fy2022_actual"}


def test_projections_footer_cites_every_source_used(claims, manifest, proj_svg):
    body = " ".join(_texts(proj_svg))
    used = {claims[b.key].source for g in build_groups(claims) for b in g.bars if b.key in claims}
    for sid in used:
        first_words = manifest[sid].short_citation().split(",")[0]
        assert first_words in body, sid


# ---------------------------------------------------------------- harms

@pytest.fixture(scope="module")
def harms_svg(claims, manifest):
    return render_harms_svg(claims, manifest)


EXPECTED_HEADLINES = {
    "bankruptcy": "+25–30%", "collections": "+8%", "investment_crowd_out": "−$0.99",
    "uk_online_slots_pgsi": "5×", "suicide": "15×", "anj_concentration": "60%",
    "nj_venue_disorder": "10×", "ct_helpline": "+87%", "pa_helpline": "50%+",
}


@pytest.mark.parametrize(("claim", "headline"), EXPECTED_HEADLINES.items())
def test_tile_headlines_computed_from_claims(claims, claim, headline):
    tile = next(t for t in TILES if t.claim == claim)
    assert tile.headline(claims) == headline


def test_nj_ratio_rounds_down(claims):
    before, after = claims["nj_venue_disorder"].value
    assert after / before == pytest.approx(10.27, abs=0.01)  # displayed as 10×, never 11×


def test_ct_helpline_increase_rounds_down(claims):
    before, after = claims["ct_helpline"].value
    assert 100 * (after - before) / before == pytest.approx(87.5, abs=0.1)  # shown as +87%


def test_tiles_avoid_superseded_wording(claims):
    words = " ".join(t.finding for t in TILES)
    assert "20% to 30%" not in words  # source says "up to 30%"; participation dropped
    assert "within four months" not in words  # no source gives that window
    assert "+10 pts" not in {t.headline(claims) for t in TILES}  # paper's estimates disagree


def test_every_headline_names_its_harm(harms_svg):
    texts = _texts(harms_svg)
    for t in TILES:
        assert t.harm and t.harm in texts, t.claim


def test_uk_slots_ratio_rounds_down(claims):
    assert claims["uk_online_slots_pgsi"].value == 5.9  # displayed as 5×, never 6×


def test_title_avoids_banned_phrase():
    assert "social ills" not in TITLE.lower()


def test_harms_svg_shows_all_tiles_with_citations(harms_svg, claims, manifest):
    texts = _texts(harms_svg)
    for h in EXPECTED_HEADLINES.values():
        assert h in texts
    root = ET.fromstring(harms_svg)
    cited = {t.get("data-cite") for t in root.iter(f"{NS}text") if t.get("data-cite")}
    assert cited == {t.claim for t in TILES}
    body = " ".join(texts)
    for tile in TILES:
        for sid in tile.sources(claims):
            assert manifest[sid].short_citation().split(",")[0] in body, (tile.claim, sid)


def test_every_tile_claim_has_quotes_and_is_covered_by_both_gambling_types(claims):
    covers = " ".join(t.covers.lower() for t in TILES)
    assert "casino" in covers and "sports" in covers
    for t in TILES:
        for c in (t.claim, *t.extra_claims):
            assert claims[c].quotes, c


def test_harms_single_red_emphasis(harms_svg):
    keys, _ = _red_keys(harms_svg)
    assert keys == {"bankruptcy"}


def test_long_finding_raises(claims, manifest, monkeypatch):
    import dc_igaming.harms as h
    long_tile = h.Tile("collections", lambda c: "x", "harm", "word " * 200, "covers")
    monkeypatch.setattr(h, "TILES", (long_tile,) * 9)
    with pytest.raises(ValueError, match="shorten"):
        h.render_harms_svg(claims, manifest)
