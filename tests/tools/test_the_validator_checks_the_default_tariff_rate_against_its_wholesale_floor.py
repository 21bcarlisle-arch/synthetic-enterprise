"""The curtained validator grades each default-tariff term's rate from below as well as above.

The cap check bounds the rate from above only; a rate set too low passed it (every one of 27,197
graded SVT periods sits exactly at the cap). The floor is the commodity (DF+CM) allowance in
Ofgem's cap model, `ofgem_cap_unit_rate_composition.json`, lowest over payment methods and regions.
It omits network and policy costs, which the commons does not separate: a stated GAP.
"""
from __future__ import annotations

from tools import bill_validation_comparison as cmp
from tools import independent_bill_validator as v

# Jan-Mar 2023: lowest commodity allowance 51.06p; the cap level is 64.2571p ex-VAT.
JAN_2023_FLOOR = 51.06
JAN_2023_CAP = 64.2571


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
        _line(_period([_term(JAN_2023_CAP)], commodity="gas"))["status"],
    }
    assert seen == {v.CAP_CHECKED, v.NOT_APPLICABLE, v.UNCHECKABLE}
    verdicts = {_claim(_period([_term(JAN_2023_CAP)]))["verdict"],
                _claim(_period([_term(JAN_2023_FLOOR - 1.0)]))["verdict"],
                _claim(_period([_term(JAN_2023_CAP)], commodity="gas"))["verdict"]}
    assert verdicts == {cmp.AGREED, cmp.DISAGREED, cmp.UNCHECKABLE}


def test_a_rate_under_the_commodity_allowance_disagrees_and_names_the_window():
    """Mutation: a default term struck a pound under the lowest Jan 2023 commodity allowance."""
    claim = _claim(_period([_term(JAN_2023_FLOOR - 1.0)]))
    assert claim["verdict"] == cmp.DISAGREED
    assert abs(claim["validator_says"] - JAN_2023_FLOOR) < 0.05
    assert "2023-01-01..2023-03-31" in claim["how"]


def test_a_rate_at_the_cap_clears_the_floor_with_room():
    line = _line(_period([_term(JAN_2023_CAP)]))
    assert line["above"] and line["lowest_ratio"] > 1.2


def test_gas_and_multi_register_name_the_gap_rather_than_pass():
    for period in (_period([_term(30.0)], commodity="gas"),
                   _period([_term(30.0)], registers=2)):
        line = _line(period)
        assert line["status"] == v.UNCHECKABLE and "single-rate electricity only" in line["why"]


def test_a_day_after_the_last_window_is_blind_not_carried_forward():
    line = _line(_period([_term(30.0, "2027-01-01", "2027-04-01")], "2027-01-01", "2027-01-31"))
    assert line["status"] == v.UNCHECKABLE and "no published cap window" in line["why"]
