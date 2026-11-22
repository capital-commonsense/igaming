"""One-at-a-time sensitivity sweeps for the money-flow model."""

from __future__ import annotations

from dataclasses import dataclass, replace

from dc_igaming.flow import FlowInputs, compute_flows


@dataclass(frozen=True)
class SweepRow:
    parameter: str
    value: float
    destination: str
    cents: float
    usd: float
    handle: float
    ggr: float
    feasible: bool


def sweep(base: FlowInputs, parameter: str, values: tuple[float, ...] | list[float]) -> list[SweepRow]:
    """Vary one parameter, holding the rest at `base`.

    `parameter` is a FlowInputs field name, or "market_multiplier" to scale the
    market (tax and GGR) while fixed-dollar items stay put.
    """
    rows: list[SweepRow] = []
    for v in values:
        if parameter == "market_multiplier":
            inp = base.scaled(v)
        elif parameter in FlowInputs.__dataclass_fields__:
            inp = replace(base, **{parameter: v})
        else:
            raise ValueError(f"unknown sweep parameter {parameter!r}")
        f = compute_flows(inp)
        for s in f.shares():
            rows.append(SweepRow(parameter, v, s.key, s.cents, s.usd, f.handle, f.ggr, f.feasible))
    return rows
