"""Check every figure claim against the text of its saved source document.

Each quote in data/claims.yaml must appear verbatim (after normalization) in the
source. Sources marked `manual` in the manifest, or not yet downloaded, are skipped
with a message saying how to get them.
"""

import pytest

from dc_igaming.sources import (
    contains_quote,
    extract_text,
    load_claims,
    load_manifest,
    normalize,
    sha256,
)

MANIFEST = load_manifest()
CLAIMS = load_claims()


def _source_text_or_skip(source_id: str) -> str:
    src = MANIFEST[source_id]
    path = src.path()
    if not path.exists():
        how = ("publisher blocks automated downloads; save the page from a browser"
               if src.status == "manual" else "run `uv run dc-igaming fetch-sources`")
        pytest.skip(f"{source_id}: {path.name} missing ({how}): {src.url}")
    return extract_text(path)


@pytest.mark.parametrize(
    ("claim_id", "quote"),
    [(cid, q) for cid, c in CLAIMS.items() for q in c.quotes],
    ids=lambda v: v if len(v) < 40 else v[:37] + "...",
)
def test_quote_appears_in_source(claim_id, quote):
    claim = CLAIMS[claim_id]
    text = _source_text_or_skip(claim.source)
    assert contains_quote(text, quote), (
        f"{claim_id}: quote not found in {MANIFEST[claim.source].file}: {quote!r}"
    )


def test_every_claim_cites_a_manifest_source():
    for cid, c in CLAIMS.items():
        assert c.source in MANIFEST, f"{cid} cites unknown source {c.source}"
        assert c.quotes, f"{cid} has no supporting quote"


def test_every_downloaded_source_is_cited():
    cited = {c.source for c in CLAIMS.values()}
    assert set(MANIFEST) == cited, f"uncited: {set(MANIFEST) - cited}; missing: {cited - set(MANIFEST)}"


@pytest.mark.parametrize("source_id", sorted(MANIFEST))
def test_source_file_matches_pinned_hash(source_id):
    src = MANIFEST[source_id]
    if not src.path().exists():
        pytest.skip(f"{src.file} not downloaded")
    if src.sha256 is None:
        pytest.fail(f"{source_id}: file present but no sha256 pinned in manifest; add it")
    assert sha256(src.path()) == src.sha256, (
        f"{src.file} changed since claims were checked; re-verify quotes, then update sha256"
    )


# Official documents that are short by nature (a one-page schedule, a two-page memo).
SHORT_DOCUMENTS = {"dccouncil_2026_calendar": 1500, "ocfo_fis_fy27_budget": 2000, "ga_2026_dc": 250}


@pytest.mark.parametrize("source_id", sorted(MANIFEST))
def test_extracted_text_is_substantial(source_id):
    # Guards against saving a bot-block / paywall page instead of the article.
    text = _source_text_or_skip(source_id)
    minimum = SHORT_DOCUMENTS.get(source_id, 3000)
    assert len(text) > minimum, f"{source_id}: only {len(text)} chars extracted"
    assert "access denied" not in text.lower()[:2000]


# --- figure values are consistent with their own quotes --------------------------------

def test_gambetdc_values_match_quotes():
    assert CLAIMS["gambetdc_fy2022_actual"].value == 2.7e6
    assert CLAIMS["gambetdc_fy2022_projection"].value == 20e6
    assert CLAIMS["gambetdc_fy2021_projection_2018"].value == 27e6
    assert CLAIMS["gambetdc_fy2021_projection_2021"].value == 6.2e6
    assert CLAIMS["gambetdc_fy2021_actual"].value == 0


def test_igaming_estimates(params):
    assert CLAIMS["igaming_committee_estimate"].value == pytest.approx(73e6 / 4)
    # The model uses the CFO's fiscal impact statement, which projects less tax than lawmakers cited.
    assert params.scenarios["central"]["tax_revenue"] == CLAIMS["fis_tax_fy2030"].value
    assert CLAIMS["fis_tax_fy2030"].value < CLAIMS["igaming_committee_estimate"].value


@pytest.mark.parametrize(("raw", "expected"), [
    ("eﬀect", "effect"),
    ("“quoted” — dash", '"quoted" - dash'),
    ("a  b\n\nc", "a b c"),
])
def test_normalize(raw, expected):
    assert normalize(raw) == expected



def test_pa_live_dealer_share_vs_cfo_implied(params):
    """Pennsylvania's live-dealer share is 2-3 times the share implied by the CFO's DC tax figures."""
    from dc_igaming.flow import FlowInputs, compute_flows

    total = CLAIMS["pa_igaming_total_fy2425"].value
    _, tables, _ = CLAIMS["pa_igaming_mix_fy2425"].value
    floor = CLAIMS["pa_live_dealer_share"].value / 100 * tables / total
    ceiling = tables / total
    assert floor == pytest.approx(0.1446, abs=0.0005)
    assert ceiling == pytest.approx(0.2410, abs=0.0005)
    dc = compute_flows(FlowInputs.from_scenario(params, "central")).live_dealer_share
    assert dc == pytest.approx(0.0757, abs=0.0005)
    assert round(floor / dc, 1) == 1.9 and round(ceiling / dc, 1) == 3.2
