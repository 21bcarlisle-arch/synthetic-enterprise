"""A term the company sells as ToU is clamped at the MULTI-REGISTER cap, never the single-rate one.

SLC 28AD.4 grades a Multi-Register Tariff, which includes any ToU tariff "regardless of the metering
equipment employed", against the multi-register benchmark at its assumed split. `tou_desk` strikes
the pair off the chain's flat rate, revenue-neutral at that split, so the pair is lawful only if the
flat rate is under the multi-register cap. Writer 4 used the single-rate cap for every term and let
15 of 27 ToU first terms sit above their ceiling
(`docs/staging/SEAT_FINDING_THE_IN_FORCE_28AD_GRADES_A_TOU_TARIFF_..._2026-10-01.md`).

Each test names the defect it catches.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from company.pricing import renewal_rate_chain as chain
from company.pricing.ofgem_price_cap import (
    get_cap_unit_rate_for_date,
    get_multi_register_cap_unit_rate_for_date,
)

ARTEFACT = (Path(__file__).resolve().parents[3] / "docs" / "domain_artefact_library"
            / "regulatory" / "ofgem_cap_multi_register_unit_rates.json")

TOU = {"metering": "NHH", "smart_meter": True}
FLAT = {"metering": "NHH", "smart_meter": False}

# A domestic fixed term struck far above any cap, so writer 4 decides the contracted rate.
TERM = dict(
    customer_id="C1", billing_account="C1", term_start="2021-06-01", tariff_type="fixed",
    term_index=0, struck_unit_rate_gbp_per_mwh=900.0, portfolio_margin_rates=[],
    prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0, is_domestic=True,
    segment="resi", settled_records=[],
)


def _contracted(commodity: str, customer: dict) -> float:
    return chain.decide_renewal_rate(commodity=commodity, customer=customer,
                                     **TERM).unit_rate_gbp_per_mwh


def test_both_benchmarks_are_reachable_and_they_differ():
    """Catches the guard that grades EVERY term one way: a chain that always takes single-rate
    (the defect) or always multi-register would make the two contracted rates equal."""
    flat, tou = _contracted("electricity", FLAT), _contracted("electricity", TOU)
    assert flat != tou, "the ToU and flat terms were clamped at the same ceiling"
    assert flat == pytest.approx(chain.cap_ceiling_ex_vat(
        "electricity", date(2021, 6, 1), multi_register=False))
    assert tou == pytest.approx(chain.cap_ceiling_ex_vat(
        "electricity", date(2021, 6, 1), multi_register=True))


def test_a_tou_term_falls_by_the_windows_multi_register_ratio():
    """Catches a ratio that does not reach the ceiling (ratio read as 1, or the wrong period's).
    April-September 2021 is 16.56 / 18.00 in the cap model v1.31."""
    ratio = _contracted("electricity", TOU) / _contracted("electricity", FLAT)
    assert ratio == pytest.approx(16.56 / 18.00, abs=5e-4)


def test_gas_is_never_graded_as_multi_register():
    """Catches a gas leg of a smart-metered household being clamped at an electricity ratio."""
    assert _contracted("gas", TOU) == _contracted("gas", FLAT)
    with pytest.raises(ValueError, match="no multi-register cap benchmark"):
        chain.cap_ceiling_ex_vat("gas", date(2021, 6, 1), multi_register=True)


def test_the_series_is_contiguous_from_the_cap_start():
    """Catches a gap or overlap in the commons artefact: a date in a gap falls through to the
    carried-forward last ratio, so a missing period would grade silently at the wrong one."""
    periods = json.loads(ARTEFACT.read_text())["periods"]
    assert periods[0]["from"] == "2019-01-01"
    for before, after in zip(periods, periods[1:]):
        assert date.fromisoformat(before["to"]) + timedelta(days=1) == date.fromisoformat(after["from"])


def test_no_ceiling_before_the_cap_and_one_after_the_last_period():
    """Catches the two fail-open edges: a multi-register ceiling that invents a cap before 2019,
    or one that returns None past the last carried period and so un-caps every ToU term."""
    assert get_multi_register_cap_unit_rate_for_date(date(2018, 12, 31)) is None
    last = json.loads(ARTEFACT.read_text())["periods"][-1]
    beyond = date.fromisoformat(last["to"]) + timedelta(days=400)
    carried = last["multi_register_p_per_kwh_ex_vat"] / last["single_rate_p_per_kwh_ex_vat"]
    assert get_multi_register_cap_unit_rate_for_date(beyond) == pytest.approx(
        get_cap_unit_rate_for_date("electricity", beyond) * carried)
