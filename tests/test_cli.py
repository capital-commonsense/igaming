import csv

import pytest

from dc_igaming.cli import main
from tests.conftest import PARAMS_PATH


def _rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def out_dir(tmp_path_factory):
    out = tmp_path_factory.mktemp("outputs")
    assert main(["flow", "--params", str(PARAMS_PATH), "--out", str(out)]) == 0
    return out


def test_writes_all_outputs(out_dir):
    for name in ("flows_usd.csv", "one_dollar_cents.csv", "flow_summary.csv",
                 "flow_sensitivity.csv", "parameter_provenance.csv"):
        assert (out_dir / name).stat().st_size > 0, name
    for scen in ("central",):
        assert (out_dir / "figures" / f"follow_one_dollar_{scen}.svg").exists()
        png = out_dir / "figures" / f"follow_one_dollar_{scen}.png"
        assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_cents_csv_includes_income_tax_row_and_sums(out_dir):
    rows = [r for r in _rows(out_dir / "one_dollar_cents.csv")
            if r["scenario"] == "central"]
    gamble = [r for r in rows if r["destination"] != "income_tax_comparison"]
    assert sum(float(r["cents_per_net_dollar_lost"]) for r in gamble) == pytest.approx(100, abs=0.01)
    iit = [r for r in rows if r["destination"] == "income_tax_comparison"]
    assert len(iit) == 1 and float(iit[0]["cents_per_net_dollar_lost"]) == 100


def test_provenance_covers_every_param(out_dir, params):
    rows = _rows(out_dir / "parameter_provenance.csv")
    assert len(rows) == len(params.all_params())
    assert all(r["source"] for r in rows)


def test_sensitivity_flags_infeasible_market(out_dir):
    rows = _rows(out_dir / "flow_sensitivity.csv")
    small = [r for r in rows if r["parameter"] == "market_multiplier" and float(r["value"]) == 0.135]
    assert small and all(r["feasible"] == "False" for r in small)
