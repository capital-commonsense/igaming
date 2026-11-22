"""Load and validate the YAML parameter file.

Every parameter carries a value plus provenance (source, status). Loading fails loudly
if any parameter lacks a source, so no number can reach an output untraced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

VALID_STATUSES = frozenset({"verified", "reported", "assumption"})

FLOW_SCENARIO_KEYS = (
    "tax_revenue",
    "community_impact",
    "regulatory_assessment",
    "olg_regulatory_costs",
    "license_fees",
    "lottery_loss",
    "sports_wagering_loss",
    "hold",
    "jobs",
    "comp_per_job",
    "local_vendor_spend",
)
CONSTANT_KEYS = (
    "tax_rate",
    "live_dealer_tax_rate",
    "assessment_rate",
    "treatment_setaside",
    "union_dues_per_member",
    "dc_population",
    "fy26_individual_income_tax",
)


class ParamError(ValueError):
    """Raised when the parameter file is missing data or provenance."""


@dataclass(frozen=True)
class Param:
    name: str
    value: float
    unit: str
    source: str
    status: str
    todo: str | None = None

    @classmethod
    def from_mapping(cls, name: str, raw: Any) -> Param:
        if not isinstance(raw, dict):
            raise ParamError(f"{name}: expected a mapping with value/source/status, got {raw!r}")
        missing = [k for k in ("value", "unit", "source", "status") if k not in raw]
        if missing:
            raise ParamError(f"{name}: missing {', '.join(missing)}")
        source = str(raw["source"]).strip()
        if not source:
            raise ParamError(f"{name}: source must not be empty")
        status = str(raw["status"]).strip()
        if status not in VALID_STATUSES:
            raise ParamError(f"{name}: status {status!r} not in {sorted(VALID_STATUSES)}")
        try:
            value = float(raw["value"])
        except (TypeError, ValueError) as exc:
            raise ParamError(f"{name}: value {raw['value']!r} is not numeric") from exc
        return cls(
            name=name,
            value=value,
            unit=str(raw["unit"]),
            source=source,
            status=status,
            todo=(str(raw["todo"]).strip() if raw.get("todo") else None),
        )


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    params: dict[str, Param]

    def __getitem__(self, key: str) -> float:
        return self.params[key].value


@dataclass(frozen=True)
class SensitivitySpec:
    name: str
    values: tuple[float, ...]
    source: str


@dataclass(frozen=True)
class ModelParams:
    constants: dict[str, Param]
    scenarios: dict[str, Scenario]
    sensitivity: dict[str, SensitivitySpec] = field(default_factory=dict)

    def const(self, key: str) -> float:
        return self.constants[key].value

    def all_params(self) -> list[tuple[str, Param]]:
        """Every parameter with a qualified name, for the provenance table."""
        rows = [(f"constants.{k}", p) for k, p in self.constants.items()]
        for sname, sc in self.scenarios.items():
            rows += [(f"scenarios.{sname}.{k}", p) for k, p in sc.params.items()]
        return rows


def _check_ranges(qualified: str, p: Param) -> None:
    key = qualified.rsplit(".", 1)[-1]
    v = p.value
    if key in {"tax_rate", "live_dealer_tax_rate", "assessment_rate", "hold"} and not 0 < v < 1:
        raise ParamError(f"{qualified}: {v} must be between 0 and 1 (exclusive)")
    if v < 0:
        raise ParamError(f"{qualified}: {v} must be non-negative")


def parse_params(raw: dict[str, Any]) -> ModelParams:
    if not isinstance(raw, dict):
        raise ParamError("parameter file must be a mapping")
    raw_consts = raw.get("constants") or {}
    missing = [k for k in CONSTANT_KEYS if k not in raw_consts]
    if missing:
        raise ParamError(f"constants: missing {', '.join(missing)}")
    constants = {k: Param.from_mapping(f"constants.{k}", v) for k, v in raw_consts.items()}

    raw_scen = raw.get("scenarios") or {}
    if not raw_scen:
        raise ParamError("at least one scenario is required")
    scenarios: dict[str, Scenario] = {}
    for sname, sraw in raw_scen.items():
        sraw = dict(sraw or {})
        description = str(sraw.pop("description", "")).strip()
        missing = [k for k in FLOW_SCENARIO_KEYS if k not in sraw]
        if missing:
            raise ParamError(f"scenarios.{sname}: missing {', '.join(missing)}")
        params = {k: Param.from_mapping(f"scenarios.{sname}.{k}", v) for k, v in sraw.items()}
        scenarios[sname] = Scenario(sname, description, params)

    sensitivity = {
        k: SensitivitySpec(k, tuple(float(x) for x in v["values"]), str(v.get("source", "")))
        for k, v in (raw.get("sensitivity") or {}).items()
    }
    mp = ModelParams(constants, scenarios, sensitivity)
    for qualified, p in mp.all_params():
        _check_ranges(qualified, p)
    return mp


def load_params(path: str | Path) -> ModelParams:
    with open(path, encoding="utf-8") as f:
        return parse_params(yaml.safe_load(f))
