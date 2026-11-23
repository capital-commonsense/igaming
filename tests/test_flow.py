from dataclasses import replace

import pytest

from dc_igaming.flow import (
    DESTINATIONS,
    Group,
    InconsistentInputs,
    compute_flows,
    income_tax_equivalent,
)
from dc_igaming.sensitivity import sweep
from dc_igaming.sources import load_claims


# Golden values: the CFO's fiscal impact statement on the committee print, FY2030.
def test_agr_implied_by_both_assessments(central):
    assert central.ggr == pytest.approx(66.75e6)  # 1,335,000 / 2%
    assert central.net_loss == central.ggr
    assert central.inputs.regulatory_assessment / central.inputs.assessment_rate == pytest.approx(central.ggr)


def test_blended_tax_rate_between_live_dealer_and_standard_rates(central):
    assert central.blended_tax_rate == pytest.approx(0.2405, abs=0.0001)
    assert 0.125 < central.blended_tax_rate < 0.25
    assert central.live_dealer_share == pytest.approx(0.0757, abs=0.001)


def test_net_impact_reproduces_cfo_line(central):
    # The model's net gain must equal the CFO's own "Net Impact on Resources" for FY2030.
    assert central.net_impact == pytest.approx(load_claims()["fis_net_impact_fy2030"].value)
    assert central.net_impact_cents() == pytest.approx(23.8, abs=0.05)


def test_central_cents_per_net_dollar(central):
    c = central.cents()
    assert c["out_of_state"] == pytest.approx(56.7, abs=0.05)
    assert c["tax_general"] == pytest.approx(22.9, abs=0.05)
    assert c["tax_treatment"] == pytest.approx(1.12, abs=0.01)
    assert c["community_impact"] == pytest.approx(2.0)
    assert c["regulatory"] == pytest.approx(2.0)
    assert c["license_fees"] == pytest.approx(0.24, abs=0.005)
    assert c["dealer_take_home"] == pytest.approx(10.3, abs=0.05)
    assert c["local_vendors"] == pytest.approx(4.49, abs=0.01)
    assert c["union_dues"] == pytest.approx(0.189, abs=0.005)  # $126K / $66.75M


def test_public_receipts_and_reconciliation(central):
    agr = central.ggr
    usable = central.public_receipts - central.regulatory
    assert 100 * usable / agr == pytest.approx(26.3, abs=0.05)  # red slices
    lost = central.inputs.lottery_loss + central.inputs.sports_wagering_loss
    assert 100 * lost / agr == pytest.approx(2.47, abs=0.01)
    # red slices - lost lottery/sports revenue = net (regulatory assessment offsets OLG costs exactly)
    assert central.regulatory == central.inputs.olg_regulatory_costs
    assert usable - lost == pytest.approx(central.net_impact)


def test_no_winners_slice(central):
    assert "net_winners" not in central.cents()
    assert not hasattr(central.inputs, "winners_share")


def test_cents_sum_to_one_dollar(central):
    assert sum(central.cents().values()) == pytest.approx(100.0)


def test_every_dollar_of_net_loss_is_accounted_for(central):
    assert sum(central.usd_by_key().values()) == pytest.approx(central.net_loss)
    assert central.handle - central.winnings_paid == pytest.approx(central.net_loss)


def test_destination_order_and_groups(central):
    assert [s.key for s in central.shares()] == [d.key for d in DESTINATIONS]
    assert central.shares()[0].group is Group.LEAVES_DC
    assert {s.key for s in central.shares() if s.group is Group.DC_PUBLIC} == {
        "tax_general", "community_impact", "tax_treatment", "license_fees"}


def test_hold_changes_handle_but_not_cents(central_inputs):
    a = compute_flows(replace(central_inputs, hold=0.03))
    b = compute_flows(replace(central_inputs, hold=0.04))
    assert a.handle > b.handle
    assert a.cents() == pytest.approx(b.cents())


def test_fixed_dollar_items_shrink_as_market_grows(central_inputs):
    rows = sweep(central_inputs, "market_multiplier", [0.5, 1.0, 2.0, 3.0])
    by = {}
    for r in rows:
        by.setdefault(r.destination, []).append(r.cents)
    for key in ("dealer_take_home", "local_vendors", "tax_treatment", "union_dues", "license_fees"):
        assert by[key] == sorted(by[key], reverse=True), key
    assert by["out_of_state"] == sorted(by["out_of_state"])
    assert by["community_impact"] == pytest.approx([2.0] * 4)  # proportional item stays at 2¢


def test_gambetdc_scale_market_is_infeasible(central_inputs):
    f = compute_flows(central_inputs.scaled(0.135))
    assert not f.feasible
    assert f.out_of_state < 0


def test_treatment_setaside_capped_by_tax(central_inputs):
    small = replace(central_inputs, community_impact=30_000, regulatory_assessment=30_000)
    with pytest.raises(InconsistentInputs):  # 100K / 1.5M = 6.7%, below the 12.5% live-dealer rate
        compute_flows(replace(small, tax_revenue=100_000))
    f = compute_flows(replace(small, tax_revenue=360_000))  # 24% of 1.5M
    assert f.tax_treatment == 360_000 and f.tax_general == 0


def test_inconsistent_assessments_rejected(central_inputs):
    with pytest.raises(InconsistentInputs, match="different revenue"):
        compute_flows(replace(central_inputs, regulatory_assessment=2_000_000))


def test_blended_rate_out_of_bounds_rejected(central_inputs):
    with pytest.raises(InconsistentInputs, match="blended tax rate"):
        compute_flows(replace(central_inputs, tax_revenue=20_000_000))  # 30% > 25%


def test_sankey_rows_conserve_money(central):
    rows = central.sankey_rows()
    from_players = sum(v for s, _, v in rows if s == "DC players' net losses")
    from_operator = sum(v for s, _, v in rows if s == "Operator gross revenue")
    assert from_players == pytest.approx(central.net_loss)
    assert from_operator == pytest.approx(central.ggr)


def test_income_tax_equivalent_uses_net_gain(central, params):
    iit = income_tax_equivalent(central, params)
    assert iit.revenue == pytest.approx(central.net_impact)
    assert iit.cents_to_dc == 100


@pytest.mark.parametrize(("field", "value"), [("hold", 1), ("hold", 0), ("assessment_rate", 0),
                                              ("live_dealer_tax_rate", 0.3)])
def test_invalid_inputs_raise(central_inputs, field, value):
    with pytest.raises(ValueError):
        compute_flows(replace(central_inputs, **{field: value}))


def test_unknown_sweep_parameter(central_inputs):
    with pytest.raises(ValueError):
        sweep(central_inputs, "vibes", [1])
