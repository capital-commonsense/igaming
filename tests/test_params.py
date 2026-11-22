import copy

import pytest
import yaml

from dc_igaming.params import ParamError, parse_params
from tests.conftest import PARAMS_PATH


@pytest.fixture
def raw():
    return yaml.safe_load(PARAMS_PATH.read_text())


def test_project_params_load_and_every_param_has_source(params):
    rows = params.all_params()
    assert rows, "no parameters loaded"
    for name, p in rows:
        assert p.source.strip(), name
        assert p.status in {"verified", "reported", "assumption"}, name


def test_verified_params_are_backed_by_checked_claims(raw):
    # A parameter may be marked "verified" only if it lists claims in data/claims.yaml,
    # whose quotes tests/test_claims.py checks against the saved primary source.
    from dc_igaming.sources import load_claims

    claims = load_claims()
    blocks = [("constants", k, v) for k, v in raw["constants"].items()]
    for sname, sc in raw["scenarios"].items():
        blocks += [(sname, k, v) for k, v in sc.items() if isinstance(v, dict)]
    verified = [(where, k, v) for where, k, v in blocks if v.get("status") == "verified"]
    assert verified, "expected at least one verified parameter"
    for where, k, v in verified:
        assert v.get("claims"), f"{where}.{k} is verified but lists no claims"
        for c in v["claims"]:
            assert c in claims, f"{where}.{k} cites unknown claim {c}"


def test_union_dues_matches_lm2(params):
    from dc_igaming.sources import load_claims

    c = load_claims()
    lo, hi = c["local25_dues_rate_2025"].value
    assert params.const("union_dues_per_member") == pytest.approx(hi * 12)
    per_member = c["local25_dues_receipts_2025"].value / c["local25_members_2025"].value
    assert per_member == pytest.approx(1274, abs=1)
    assert abs(per_member - hi * 12) / per_member < 0.02  # published rate and receipts agree


def test_scientific_notation_strings_parse_as_floats(params):
    # PyYAML reads `3.0e6` as a string; the loader must still coerce it.
    assert params.scenarios["central"]["local_vendor_spend"] == pytest.approx(3.0e6)


def test_missing_source_rejected(raw):
    bad = copy.deepcopy(raw)
    del bad["constants"]["tax_rate"]["source"]
    with pytest.raises(ParamError, match="tax_rate: missing source"):
        parse_params(bad)


def test_empty_source_rejected(raw):
    bad = copy.deepcopy(raw)
    bad["scenarios"]["central"]["hold"]["source"] = "  "
    with pytest.raises(ParamError, match="source must not be empty"):
        parse_params(bad)


def test_bad_status_rejected(raw):
    bad = copy.deepcopy(raw)
    bad["constants"]["tax_rate"]["status"] = "probably"
    with pytest.raises(ParamError, match="status"):
        parse_params(bad)


def test_missing_scenario_key_rejected(raw):
    bad = copy.deepcopy(raw)
    del bad["scenarios"]["central"]["jobs"]
    with pytest.raises(ParamError, match="central: missing jobs"):
        parse_params(bad)


@pytest.mark.parametrize(("path", "value"), [
    (("constants", "tax_rate"), 1.5),
    (("scenarios", "central", "hold"), 0),
    (("scenarios", "central", "hold"), 1.0),
    (("scenarios", "central", "jobs"), -1),
])
def test_out_of_range_values_rejected(raw, path, value):
    bad = copy.deepcopy(raw)
    node = bad
    for k in path:
        node = node[k]
    node["value"] = value
    with pytest.raises(ParamError):
        parse_params(bad)
