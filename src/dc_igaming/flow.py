"""Follow-one-dollar money-flow model for DC iGaming (B26-0656).

Annual steady state, built on the DC CFO's fiscal impact statement (FIS) for the draft
committee print. The CFO doesn't publish adjusted gross revenue (AGR) directly, but each
of the two 2% assessments is reported, so:

    AGR (operator revenue)     = community impact assessment / 2%
                                 (cross-checked against the regulatory assessment, and the
                                 implied blended tax rate must lie between 12.5% and 25%)
    handle (total wagered)     = AGR / hold   (CSV only; churn, mostly paid back as winnings)

AGR is also DC players' combined net loss: everything wagered minus everything paid back,
with every player's winnings netted out. Under the committee print, promotional credits are
not counted as wagers, so there is no gap between the tax base and players' net cash loss.
Every share is per $1 of net player losses.

AGR splits into: DC tax (general fund + the $750K addiction set-aside), the community
impact assessment, the regulatory assessment (which pays for regulating the market), license
fees, union dealer pay (take-home + dues), DC local vendors, and the remainder, which goes
to out-of-state operators and suppliers.

The District's *net* gain also subtracts OLG's regulatory costs and the lottery and
sports-betting revenue the CFO expects DC to lose. That equals the CFO's own "net impact on
resources" line, and it is the headline number.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from dc_igaming.params import ModelParams, Scenario


class Group(StrEnum):
    LEAVES_DC = "leaves_dc"
    DC_PUBLIC = "dc_public"
    DC_REGULATION = "dc_regulation"
    DC_PRIVATE = "dc_private"


@dataclass(frozen=True)
class DestinationInfo:
    key: str
    label: str
    group: Group


# Display order, top to bottom, for every chart and table.
DESTINATIONS: tuple[DestinationInfo, ...] = (
    DestinationInfo("out_of_state", "Out-of-state operators & suppliers", Group.LEAVES_DC),
    DestinationInfo("tax_general", "DC general fund (tax)", Group.DC_PUBLIC),
    DestinationInfo("community_impact", "DC community impact fund", Group.DC_PUBLIC),
    DestinationInfo("tax_treatment", "DC addiction services", Group.DC_PUBLIC),
    DestinationInfo("license_fees", "DC license fees", Group.DC_PUBLIC),
    DestinationInfo("regulatory", "Regulating the market (OLG)", Group.DC_REGULATION),
    DestinationInfo("dealer_take_home", "Dealers' pay", Group.DC_PRIVATE),
    DestinationInfo("union_dues", "Union dues (UNITE HERE Local 25)", Group.DC_PRIVATE),
    DestinationInfo("local_vendors", "DC local vendors", Group.DC_PRIVATE),
)
DESTINATION_BY_KEY = {d.key: d for d in DESTINATIONS}


class InconsistentInputs(ValueError):
    """The CFO line items don't imply a coherent revenue base."""


@dataclass(frozen=True)
class FlowInputs:
    tax_revenue: float
    community_impact: float
    regulatory_assessment: float
    olg_regulatory_costs: float
    license_fees: float
    lottery_loss: float
    sports_wagering_loss: float
    hold: float
    jobs: float
    comp_per_job: float
    local_vendor_spend: float
    tax_rate: float
    live_dealer_tax_rate: float
    assessment_rate: float
    treatment_setaside: float
    union_dues_per_member: float

    @classmethod
    def from_scenario(cls, params: ModelParams, scenario: str | Scenario) -> FlowInputs:
        sc = params.scenarios[scenario] if isinstance(scenario, str) else scenario
        scenario_fields = ("tax_revenue", "community_impact", "regulatory_assessment",
                           "olg_regulatory_costs", "license_fees", "lottery_loss",
                           "sports_wagering_loss", "hold", "jobs", "comp_per_job", "local_vendor_spend")
        constant_fields = ("tax_rate", "live_dealer_tax_rate", "assessment_rate",
                           "treatment_setaside", "union_dues_per_member")
        return cls(**{f: sc[f] for f in scenario_fields}, **{f: params.const(f) for f in constant_fields})

    def scaled(self, market_multiplier: float) -> FlowInputs:
        """Scale the market: revenue-proportional items move, fixed-dollar items stay put."""
        if market_multiplier <= 0:
            raise ValueError("market_multiplier must be positive")
        m = market_multiplier
        return replace(self, tax_revenue=self.tax_revenue * m, community_impact=self.community_impact * m,
                       regulatory_assessment=self.regulatory_assessment * m,
                       olg_regulatory_costs=self.olg_regulatory_costs * m)


@dataclass(frozen=True)
class Share:
    key: str
    label: str
    group: Group
    usd: float
    cents: float  # cents per $1 of DC players' net losses


@dataclass(frozen=True)
class Flows:
    inputs: FlowInputs
    ggr: float
    handle: float
    tax_general: float
    tax_treatment: float
    community_impact: float
    regulatory: float
    license_fees: float
    wages: float
    dues: float
    local_vendors: float
    out_of_state: float

    @property
    def net_loss(self) -> float:
        """DC players' combined net loss: wagers minus everything paid back (= AGR)."""
        return self.ggr

    @property
    def tax(self) -> float:
        return self.tax_general + self.tax_treatment

    @property
    def blended_tax_rate(self) -> float:
        return self.tax / self.ggr

    @property
    def live_dealer_share(self) -> float:
        """Share of AGR from live-dealer games implied by the CFO's blended tax rate."""
        i = self.inputs
        return (i.tax_rate - self.blended_tax_rate) / (i.tax_rate - i.live_dealer_tax_rate)

    @property
    def public_receipts(self) -> float:
        """Everything paid to the District: tax, both assessments, license fees."""
        return self.tax + self.community_impact + self.regulatory + self.license_fees

    @property
    def offsets(self) -> float:
        """OLG's regulatory costs plus lottery and sports-betting revenue the District loses."""
        i = self.inputs
        return i.olg_regulatory_costs + i.lottery_loss + i.sports_wagering_loss

    @property
    def net_impact(self) -> float:
        """The District's net gain: the CFO's 'net impact on resources'."""
        return self.public_receipts - self.offsets

    @property
    def winnings_paid(self) -> float:
        """Handle that is returned to players as winnings (churn)."""
        return self.handle - self.ggr

    @property
    def dealer_take_home(self) -> float:
        return self.wages - self.dues

    @property
    def retained_in_dc(self) -> float:
        """Public receipts + dealer pay + local vendors."""
        return self.public_receipts + self.wages + self.local_vendors

    @property
    def feasible(self) -> bool:
        """False when DC's take + payroll + vendors exceed operator revenue (out-of-state < 0)."""
        return self.out_of_state >= 0

    def usd_by_key(self) -> dict[str, float]:
        return {
            "out_of_state": self.out_of_state,
            "tax_general": self.tax_general,
            "community_impact": self.community_impact,
            "tax_treatment": self.tax_treatment,
            "license_fees": self.license_fees,
            "regulatory": self.regulatory,
            "dealer_take_home": self.dealer_take_home,
            "union_dues": self.dues,
            "local_vendors": self.local_vendors,
        }

    def shares(self) -> list[Share]:
        """Cents per $1 of DC players' net losses to each destination. Sums to 100."""
        usd = self.usd_by_key()
        return [
            Share(key=d.key, label=d.label, group=d.group, usd=usd[d.key],
                  cents=100 * usd[d.key] / self.net_loss)
            for d in DESTINATIONS
        ]

    def cents(self) -> dict[str, float]:
        return {s.key: s.cents for s in self.shares()}

    def net_impact_cents(self) -> float:
        return 100 * self.net_impact / self.net_loss

    def sankey_rows(self) -> list[tuple[str, str, float]]:
        """(source, target, usd) rows for a dollar-scale Sankey."""
        op = "Operator gross revenue"
        players = "DC players' net losses"
        return [(players, op, self.ggr)] + [
            (op, DESTINATION_BY_KEY[k].label, v) for k, v in self.usd_by_key().items()
        ]


def compute_flows(inp: FlowInputs, tolerance: float = 0.01) -> Flows:
    if not 0 < inp.live_dealer_tax_rate <= inp.tax_rate < 1:
        raise ValueError("need 0 < live_dealer_tax_rate <= tax_rate < 1")
    if not 0 < inp.hold < 1:
        raise ValueError("hold must be in (0, 1)")
    if not 0 < inp.assessment_rate < 1:
        raise ValueError("assessment_rate must be in (0, 1)")
    ggr = inp.community_impact / inp.assessment_rate
    if ggr <= 0:
        raise ValueError("community_impact must be positive")
    cross = inp.regulatory_assessment / inp.assessment_rate
    if abs(cross - ggr) / ggr > tolerance:
        raise InconsistentInputs(f"assessments imply different revenue: {ggr:,.0f} vs {cross:,.0f}")
    blended = inp.tax_revenue / ggr
    if not inp.live_dealer_tax_rate * (1 - tolerance) <= blended <= inp.tax_rate * (1 + tolerance):
        bounds = f"[{inp.live_dealer_tax_rate:.1%}, {inp.tax_rate:.0%}]"
        raise InconsistentInputs(f"implied blended tax rate {blended:.2%} outside {bounds}")
    treatment = min(inp.treatment_setaside, inp.tax_revenue)
    wages = inp.jobs * inp.comp_per_job
    dues = inp.jobs * inp.union_dues_per_member
    public = inp.tax_revenue + inp.community_impact + inp.regulatory_assessment + inp.license_fees
    return Flows(
        inputs=inp,
        ggr=ggr,
        handle=ggr / inp.hold,
        tax_general=inp.tax_revenue - treatment,
        tax_treatment=treatment,
        community_impact=inp.community_impact,
        regulatory=inp.regulatory_assessment,
        license_fees=inp.license_fees,
        wages=wages,
        dues=dues,
        local_vendors=inp.local_vendor_spend,
        out_of_state=ggr - public - wages - inp.local_vendor_spend,
    )


@dataclass(frozen=True)
class IncomeTaxEquivalent:
    revenue: float

    @property
    def cents_to_dc(self) -> float:
        """Cents of each $1 paid that reach DC. All of it."""
        return 100.0


def income_tax_equivalent(flows: Flows, params: ModelParams) -> IncomeTaxEquivalent:
    """Income-tax comparison for the District's *net* gain from the bill."""
    return IncomeTaxEquivalent(flows.net_impact)
