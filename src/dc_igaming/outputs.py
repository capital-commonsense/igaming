"""Write tidy CSV outputs for each chart concept."""

from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence
from pathlib import Path

from dc_igaming.flow import FlowInputs, Flows, compute_flows, income_tax_equivalent
from dc_igaming.params import ModelParams
from dc_igaming.sensitivity import sweep


def _write(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


def scenario_flows(params: ModelParams) -> dict[str, Flows]:
    return {name: compute_flows(FlowInputs.from_scenario(params, name)) for name in params.scenarios}


def write_flow_outputs(params: ModelParams, out_dir: str | Path) -> list[Path]:
    out = Path(out_dir)
    flows = scenario_flows(params)
    written: list[Path] = []

    written.append(_write(
        out / "flows_usd.csv",
        ["scenario", "source", "target", "usd_per_year"],
        [(name, src, dst, round(v)) for name, f in flows.items() for src, dst, v in f.sankey_rows()],
    ))

    rows = []
    for name, f in flows.items():
        for s in f.shares():
            rows.append((name, s.key, s.label, s.group.value, round(s.usd), round(s.cents, 3)))
        iit = income_tax_equivalent(f, params)
        rows.append((name, "income_tax_comparison", "$1 of income tax: DC general fund",
                     "dc_public", round(iit.revenue), iit.cents_to_dc))
    written.append(_write(
        out / "one_dollar_cents.csv",
        ["scenario", "destination", "label", "group", "usd_per_year", "cents_per_net_dollar_lost"],
        rows,
    ))

    summary = []
    for name, f in flows.items():
        iit = income_tax_equivalent(f, params)
        pop = params.const("dc_population")
        summary += [
            (name, "handle_usd", round(f.handle)),
            (name, "winnings_paid_back_usd", round(f.winnings_paid)),
            (name, "net_player_loss_usd", round(f.net_loss)),
            (name, "tax_usd", round(f.tax)),
            (name, "out_of_state_usd", round(f.out_of_state)),
            (name, "blended_tax_rate", round(f.blended_tax_rate, 5)),
            (name, "implied_live_dealer_share", round(f.live_dealer_share, 4)),
            (name, "public_receipts_usd", round(f.public_receipts)),
            (name, "net_impact_usd", round(f.net_impact)),
            (name, "net_impact_cents_per_net_dollar", round(f.net_impact_cents(), 2)),
            (name, "retained_cents_per_net_dollar", round(100 * f.retained_in_dc / f.net_loss, 2)),
            (name, "net_losses_per_resident_usd", round(f.net_loss / pop, 2)),
            (name, "tax_per_resident_usd", round(f.tax / pop, 2)),
            (name, "net_losses_per_union_job_usd", round(f.net_loss / f.inputs.jobs)),
            (name, "income_tax_equiv_pct", round(iit.pct_increase, 3)),
            (name, "feasible", f.feasible),
        ]
    written.append(_write(out / "flow_summary.csv", ["scenario", "metric", "value"], summary))

    base = FlowInputs.from_scenario(params, "central")
    sens_rows = []
    for name, spec in params.sensitivity.items():
        for r in sweep(base, name, spec.values):
            sens_rows.append((r.parameter, r.value, r.destination, round(r.cents, 3), round(r.usd),
                              round(r.handle), round(r.ggr), r.feasible))
    written.append(_write(
        out / "flow_sensitivity.csv",
        ["parameter", "value", "destination", "cents_per_dollar", "usd_per_year", "handle_usd",
         "ggr_usd", "feasible"],
        sens_rows,
    ))

    written.append(_write(
        out / "parameter_provenance.csv",
        ["parameter", "value", "unit", "status", "source"],
        [(q, p.value, p.unit, p.status, p.source) for q, p in params.all_params()],
    ))
    return written
