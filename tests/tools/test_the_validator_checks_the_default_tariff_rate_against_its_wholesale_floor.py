"""The curtained validator grades each default-tariff term's rate from below as well as above.

The cap check bounds the rate from above only; a rate set too low passed it (every one of 27,197
graded SVT periods sits exactly at the cap). The floor is the commodity, network and policy
(DF+CM+NC+PC) allowance in Ofgem's cap model, `ofgem_cap_unit_rate_composition.json`, lowest over
payment methods and regions, for single-rate electricity and gas. Multi-register is a stated GAP.
"""
from __future__ import annotations

from tools import bill_validation_comparison as cmp
from tools import independent_bill_validator as v

# Jan-Mar 2023: lowest DF+CM+NC+PC allowance 57.60p; the cap level is 64.2571p ex-VAT.
JAN_2023_FLOOR = 57.60
JAN_2023_CAP = 64.2571
# Gas, same window: floor 15.09p, cap 16.27p ex-VAT. Commodity alone was 13.60p.
JAN_2023_GAS_FLOOR = 15.09
JAN_2023_GAS_CAP = 16.2667


def _term(rate, start="2023-01-01", end="2023-04-01", tariff="svt"):
    return {"tariff_effective_from": start, "tariff_effective_to": end, "tariff_type": tariff,
            "unit_rate_p_per_kwh": rate, "tou_unit_rates": None}


def _period(terms, start="2023-01-01", end="2023-01-31", commodity="electricity", registers=1):
    regs = [{"register_id": str(i), "register_label": label, "unit_rate_p_per_kwh": 1.0}
            for i, label in enumerate(["Peak", "Off-peak"])] if registers > 1 else []
    return {"period_start": start, "period_end": end, "commodity": commodity,
            "registers": regs, "contracted_terms": terms}


def _line(period, segment="resi"):
    return v.default_tariff_rate_against_wholesale_floor(period, segment=segment)


def _claim(period):
    built = {"period_start": "x", "period_end": "x", "lines": [_line(period)]}
    issued = {"period_start": "x", "period_end": "x", "lines": []}
    claims = cmp.compare_bill(built, issued, statutory_vat={}, read_volume_kwh=None)
    return next((c for c in claims if c["claim"] == "default_tariff_rate_above_wholesale_floor"),
                None)


def test_every_verdict_can_be_reached():
    """THE PARTITION, asserted whole: a check that only ever agreed passes every leg below."""
    seen = {
        _line(_period([_term(JAN_2023_CAP)]))["status"],
        _line(_period([_term(JAN_2023_CAP, tariff="fixed")]))["status"],
        _line(_period([_term(JAN_2023_CAP)], registers=2))["status"],
    }
    assert seen == {v.CAP_CHECKED, v.NOT_APPLICABLE, v.UNCHECKABLE}
    verdicts = {_claim(_period([_term(JAN_2023_CAP)]))["verdict"],
                _claim(_period([_term(JAN_2023_FLOOR - 0.01)]))["verdict"],
                _claim(_period([_term(JAN_2023_CAP)], registers=2))["verdict"]}
    assert verdicts == {cmp.AGREED, cmp.DISAGREED, cmp.UNCHECKABLE}


def test_a_rate_under_the_cost_floor_disagrees_and_names_the_window():
    """Mutation: a default term struck a penny under the lowest Jan 2023 pass-through allowance."""
    claim = _claim(_period([_term(JAN_2023_FLOOR - 0.01)]))
    assert claim["verdict"] == cmp.DISAGREED
    assert abs(claim["validator_says"] - JAN_2023_FLOOR) < 0.05
    assert "2023-01-01..2023-03-31" in claim["how"]


def test_the_floor_carries_network_and_policy_not_commodity_alone():
    """Mutation: a rate between the commodity allowance (50.68p) and the full floor. A commodity-only
    floor passes it; this one must not."""
    assert not _line(_period([_term(55.0)]))["above"]


def test_a_rate_at_the_cap_clears_the_floor_by_a_narrow_margin():
    line = _line(_period([_term(JAN_2023_CAP)]))
    assert line["above"] and 1.05 < line["lowest_ratio"] < 1.2


def test_gas_is_graded_both_ways():
    at_cap = _line(_period([_term(JAN_2023_GAS_CAP)], commodity="gas"))
    under = _line(_period([_term(JAN_2023_GAS_FLOOR - 0.01)], commodity="gas"))
    assert at_cap["status"] == under["status"] == v.CAP_CHECKED
    assert at_cap["above"] and not under["above"]
    assert abs(under["graded"][0]["floor_p_per_kwh"] - JAN_2023_GAS_FLOOR) < 0.01


def test_multi_register_names_the_gap_rather_than_pass():
    line = _line(_period([_term(30.0)], registers=2))
    assert line["status"] == v.UNCHECKABLE and "multi-register" in line["why"]


def test_a_day_after_the_last_window_is_blind_not_carried_forward():
    line = _line(_period([_term(30.0, "2027-01-01", "2027-04-01")], "2027-01-01", "2027-01-31"))
    assert line["status"] == v.UNCHECKABLE and "no published cap window" in line["why"]
