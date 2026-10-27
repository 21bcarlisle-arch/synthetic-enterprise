"""A gas supplier pays for Unidentified Gas on top of its metered volume, at the cap's own allowance.

Subject: `simulation.policy_costs.get_gas_uig_uplift`, `simulation.gas_settlement.run_gas_term`.
Knowledge: `docs/market_research/unbilled_energy_and_revenue_assurance.md`, "The cap's own UIG
allowance, cap period by cap period".

The defect each test catches is named in its docstring. Until 2026-10-27 the world charged the
supplier for its customers' metered gas only, while the cap it priced against carried a 1.8-8.2%
UIG uplift, so every gas leg kept a margin no real supplier had.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from simulation.gas_settlement import run_gas_term
from simulation.policy_costs import (
    PRE_CAP_UIG_UPLIFT_BELIEF,
    PRE_CAP_UIG_UPLIFT_RANGE,
    get_gas_uig_uplift,
)

ARTEFACT = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory" / "ofgem_cap_uig_allowance.json"
)
PERIODS = json.loads(ARTEFACT.read_text())["periods"]


def _day_before(iso: str) -> str:
    return (date.fromisoformat(iso) - timedelta(days=1)).isoformat()


def test_every_cap_period_is_charged_its_own_allowance_from_its_first_day_to_its_last():
    """Defect: a period served its neighbour's figure (an off-by-one at a boundary, or a lookup
    keyed by year). Each period's first and last day must read that period's row, both methods."""
    for p in PERIODS:
        ppm = p["ppm"] if p["ppm"] is not None else p["non_ppm"]
        for day in (p["starts"], _day_before(p["ends_before"])):
            assert get_gas_uig_uplift(day) == pytest.approx(p["non_ppm"]), (p["cap_period"], day)
            assert get_gas_uig_uplift(day, True) == pytest.approx(ppm), (p["cap_period"], day)


def test_the_prepayment_row_can_differ_from_the_credit_row_and_can_equal_it():
    """Defect: the prepayment flag ignored (always the credit row), or the PPM row read for both.
    The partition must hold both sides, or the flag is untestable."""
    differ = [p for p in PERIODS if p["ppm"] is not None and p["ppm"] != p["non_ppm"]]
    same = [p for p in PERIODS if p["ppm"] in (None, p["non_ppm"])]
    assert differ and same
    jan_2023 = "2023-01-15"
    assert get_gas_uig_uplift(jan_2023, True) > 4 * get_gas_uig_uplift(jan_2023)


def test_no_gas_day_in_the_world_is_charged_zero_unidentified_gas():
    """Defect (K2): omission asserts zero. The world runs from 2016, three years before any
    allowance; a pre-cap day must carry the stated belief, inside its stated range."""
    lo, hi = PRE_CAP_UIG_UPLIFT_RANGE
    assert lo <= PRE_CAP_UIG_UPLIFT_BELIEF <= hi
    day = date(2016, 1, 1)
    while day < date(2026, 1, 1):
        assert get_gas_uig_uplift(day.isoformat()) > 0, day
        day += timedelta(days=30)
    assert get_gas_uig_uplift("2016-06-01") == PRE_CAP_UIG_UPLIFT_BELIEF


def _term(start: str, days: int, *, prepayment: bool, hedge_fraction: float = 0.6):
    first = date.fromisoformat(start)
    prices = [{"settlementDate": (first + timedelta(days=i)).isoformat(), "systemSellPrice": 150.0}
              for i in range(days)]
    return run_gas_term(
        "TEST-UIG", start, (first + timedelta(days=days)).isoformat(), 12_000, 90.0,
        hedge_fraction, 110.0, 0.0, prices, segment="I&C", prepayment=prepayment,
    )


def test_the_settled_cost_is_the_metered_cost_uplifted_by_the_days_allowance():
    """Defect: the uplift computed and not charged (a field written beside a cost that ignores it),
    or charged on the hedged or unhedged half only. Cost must be the whole metered cost x (1 + u),
    and the margin must carry it."""
    for rec in _term("2023-01-01", 10, prepayment=False):
        metered = rec["hedged_mwh"] * 110.0 + rec["unhedged_mwh"] * 150.0
        u = get_gas_uig_uplift(rec["settlement_date"])
        # The record rounds its volumes to 6 dp, so the rebuild from them is good to ~1e-5;
        # a missing or half-applied uplift is off by about 1e-2.
        assert rec["wholesale_cost_gbp"] == pytest.approx(metered * (1 + u), rel=1e-4)
        uig = rec["gas_uig_cost_gbp"]
        assert uig / (rec["wholesale_cost_gbp"] - uig) == pytest.approx(u, rel=1e-5)
        assert rec["margin_gbp"] == pytest.approx(rec["revenue_gbp"] - rec["wholesale_cost_gbp"], abs=1e-5)


def test_a_prepayment_leg_in_the_crisis_pays_the_prepayment_rows_uig():
    """Defect: `prepayment=` accepted by run_gas_term and never reaching the lookup."""
    credit = sum(r["gas_uig_cost_gbp"] for r in _term("2023-01-01", 10, prepayment=False))
    ppm = sum(r["gas_uig_cost_gbp"] for r in _term("2023-01-01", 10, prepayment=True))
    assert ppm == pytest.approx(credit * 0.08185 / 0.018261, rel=1e-4)
