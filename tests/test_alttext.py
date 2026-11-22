"""Alt text is generated from the figure data, fits a CMS alt field, and reads cleanly aloud."""

import pytest

from dc_igaming.alttext import SHORT_LIMIT, harms_alt, one_dollar_alt, projections_alt, speakable, write_alt
from dc_igaming.diagram import default_text
from dc_igaming.flow import FlowInputs, compute_flows, income_tax_equivalent
from dc_igaming.harms import TILES
from dc_igaming.sources import load_claims

UNSPOKEN = (" ", "×", "−", "¢", " · ", "~")
NAMES = ["flow", "projections", "harms"]


@pytest.fixture(scope="module")
def claims():
    return load_claims()


@pytest.fixture(scope="module")
def alts(params, claims):
    flows = compute_flows(FlowInputs.from_scenario(params, "central"))
    iit = income_tax_equivalent(flows, params)
    return {
        "flow": one_dollar_alt(flows, iit, default_text(flows, iit, "central")),
        "projections": projections_alt(claims),
        "harms": harms_alt(claims),
    }


@pytest.mark.parametrize("name", NAMES)
def test_short_fits_alt_field_and_full_is_longer(alts, name):
    alt = alts[name]
    assert 40 < len(alt.short) <= SHORT_LIMIT
    assert len(alt.full) > len(alt.short)


@pytest.mark.parametrize("name", NAMES)
def test_no_symbols_screen_readers_mangle(alts, name):
    for text in (alts[name].short, alts[name].full):
        for sym in UNSPOKEN:
            assert sym not in text, (name, sym)


def test_flow_alt_states_headline_and_every_slice(alts):
    a = alts["flow"]
    assert "nets 24 cents" in a.short and "57 cents" in a.short
    for label in ("Out-of-state operators and suppliers", "DC general fund", "Dealers' pay", "Union dues"):
        assert label in a.full
    assert "23.8 cents per $1" in a.full and "0.43% increase" in a.full


def test_projections_alt_states_every_bar(alts):
    full = alts["projections"].full
    for v in ("$27M", "$6.2M", "$0", "$20M", "$2.7M", "$15.9M", "unknown", "13.5%"):
        assert v in full, v


def test_harms_alt_covers_every_tile(alts, claims):
    full = alts["harms"].full
    for t in TILES:
        assert speakable(t.headline(claims)) in full, t.claim
        assert t.harm in full, t.claim


def test_speakable():
    assert speakable("5× spike · ~7M") == "5 times spike, about 7M"
    assert speakable("−$0.99 and 2.5¢") == "minus $0.99 and 2.5 cents"


def test_write_alt_names_file_after_figure(alts, tmp_path):
    path = write_alt(alts["projections"], tmp_path / "projections_vs_actuals.svg")
    assert path.name == "projections_vs_actuals.alt.txt"
    body = path.read_text()
    assert "ALT TEXT (short" in body and "projections_vs_actuals_share.png" in body
