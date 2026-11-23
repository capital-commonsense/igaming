"""LIST_OF_CLAIMS.md must match a fresh render, and must cover every claim and displayed number."""

import re

import pytest

from dc_igaming.claims_doc import OUTPUT_NAME
from dc_igaming.cli import build_claims_doc
from dc_igaming.diagram import PROJECT_ROOT, format_cents
from dc_igaming.harms import TILES
from dc_igaming.sources import load_claims, load_manifest

DOC_PATH = PROJECT_ROOT / OUTPUT_NAME


@pytest.fixture(scope="module")
def doc():
    return build_claims_doc()


def test_committed_doc_is_up_to_date(doc):
    assert DOC_PATH.exists(), "run `uv run dc-igaming claims-doc`"
    assert DOC_PATH.read_text(encoding="utf-8") == doc, (
        "LIST_OF_CLAIMS.md is stale: run `uv run dc-igaming claims-doc` and commit the result"
    )


def test_every_claim_and_quote_is_listed(doc):
    for cid, c in load_claims().items():
        assert f"### {cid}\n" in doc, cid
        for q in c.quotes:
            assert q in doc, (cid, q)


def test_every_source_is_listed_with_url(doc):
    for s in load_manifest().values():
        assert s.url in doc and s.file in doc, s.id


def test_every_claim_is_used_somewhere(doc):
    unused = re.findall(r"### (\w+)\n(?:.*\n){5,12}?- \*\*Used in:\*\* not displayed", doc)
    assert not unused, f"claims not used by any graphic: {unused}"


def test_sankey_numbers_listed(doc, central):
    for key, v in central.cents().items():
        assert format_cents(v) in doc, key
    assert "0.43%" not in doc and "$66.8M" in doc and "23.8¢" in doc


def test_tile_headlines_listed(doc):
    claims = load_claims()
    for t in TILES:
        assert t.headline(claims) in doc


def test_internal_links_resolve(doc):
    anchors = set(re.findall(r"^### (\w+)$", doc, re.M))
    for target in re.findall(r"\]\(#(\w+)\)", doc):
        assert target in anchors, target


def test_params_with_claims_reference_real_claims():
    import yaml

    raw = yaml.safe_load((PROJECT_ROOT / "model" / "params.yaml").read_text())
    claims = load_claims()
    entries = list(raw["constants"].values())
    for sc in raw["scenarios"].values():
        entries += [v for v in sc.values() if isinstance(v, dict)]
    for e in entries:
        for c in e.get("claims", []):
            assert c in claims, c
