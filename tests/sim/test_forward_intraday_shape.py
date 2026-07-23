"""Failable control on the INTRADAY locus of the forward SSP settlement path (SPIKE_TAIL_SSP_RESIDUAL).

WHY THIS EXISTS (step-3 DIAGNOSIS, 2026-07-23 tick -- the redirected fix locus):
`test_scenario_forward_tail.py` already tripwires the *daily* generator (bimodal_generator). But tracing
the code established that the daily figure is NOT where the gap lives:

  simulation/run_scenario.py::_expand_daily_to_hh writes each daily generator price to ALL 48 settlement
  periods of the day, identically. So in forward/curriculum worlds every half-hour of a day carries the
  same number -- the residual settles at DAILY granularity with ZERO intraday shape.

That reframes the whole defect (recorded in the register + PROPOSE_SPIKE_TAIL_ATTACK_PLAN.md, step-3):
  - The real DAILY-MEAN SSP max is only GBP960 (never > GBP1,000); the GBP4,038 / 2.24%-negative figures
    the register cites are HALF-HOURLY (a single SP). Grading the *daily* generator against GBP4,038 is a
    category error -- a daily price tuned toward it would be LESS real (the R12 sibling-trap).
  - The real "bite" that killed suppliers in 2021-22 is INTRADAY: a flat block hedge meeting a spiky
    half-hourly SSP -- the block-vs-shape mismatch *within* the day. The flat-48 expansion means forward
    worlds have zero within-day shape, so that mismatch is STRUCTURALLY ABSENT regardless of the daily
    number. THIS is the truncation the redirected fix must remove (intraday SP-level shape whose worst
    periods can reach the scarcity regime, while the daily mean stays near daily_mean).

This control makes that intraday truncation a LIVE TRIPWIRE (R15), on the RIGHT locus:
  - test_forward_intraday_shape_is_flat_today  -- GREEN now (every forward day is flat across its 48 SPs);
    FAILS the moment the intraday-shape overlay lands, forcing SPIKE_TAIL_SSP_RESIDUAL close-review and
    this assertion flipped to an intraday-shape tolerance check in the SAME commit.
  - test_measurement_can_see_intraday_shape    -- R15 killer-mutation companion: a day WITH within-day
    variance IS reported as non-flat, so the GREEN above means "no intraday shape", not "measurement broken".
  - FAIL-CLOSED: an empty expansion RAISES, never silently passes.

BLIND TO COMPANY P&L (R12/R13): every number here is a structural property of the expansion step over the
baseline/curriculum generator's own seeds; no company outcome participates. The per-scenario SEVERITY of any
future intraday spike (events/year, magnitude) is director-reserved CURRICULUM (R13) -- this control asserts
only the *machinery's* current structural INABILITY to carry ANY intraday shape, which is a fidelity fact.

NOTE (debt flagged, not fixed this tick): `test_scenario_forward_tail.py::test_forward_tail_gap_is_real_today`
still frames its closure as "flips when the daily generator reaches the real tail". Per this diagnosis the
daily path should NOT reach the real HH tail (daily-mean max is GBP960); its `max < 1000` assertion happens to
stay true-to-real, but its stated closure condition is superseded by the intraday reframing here. Reconciling
that test's docstring is a follow-on (left green + untouched this tick to keep the change minimal).
"""
from __future__ import annotations

import pytest

from sim.scenario.bimodal_generator import generate_scenario_prices
from simulation.run_scenario import _expand_daily_to_hh


def _per_day_intraday_spread(hh_records: list[dict]) -> list[float]:
    """For each settlement day, the within-day SSP spread (max period price - min period price).
    A flat-expanded day has spread 0.0; any intraday shape makes it positive. FAIL-CLOSED on empty."""
    assert hh_records, "no half-hourly records to measure -- FAIL-CLOSED"
    by_day: dict[str, list[float]] = {}
    for r in hh_records:
        by_day.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
    assert by_day, "no days grouped -- FAIL-CLOSED"
    return [max(prices) - min(prices) for prices in by_day.values()]


def test_forward_intraday_shape_is_flat_today():
    """Every forward day currently carries ONE SSP flat-expanded across all 48 settlement periods, so the
    residual settles with ZERO intraday shape -- the block-vs-shape mismatch that bit real suppliers cannot
    occur. Real per-day intraday range routinely exceeds GBP1,000 (daily_max GBP4,038 vs daily_mean GBP78).

    Flip this the moment the intraday-shape overlay lands: set SPIKE_TAIL_SSP_RESIDUAL status: closed and
    replace this with an intraday-shape tolerance check (worst-SP exceedance vs spike_tail_real_target.json,
    daily mean preserved near spike_tail_real_target_daily.json) in the SAME commit (register closes_when)."""
    daily = generate_scenario_prices(2026, 2029, "stress_dunkelflaute_2027", seed="intraday_shape_control")
    hh = _expand_daily_to_hh(daily)
    spreads = _per_day_intraday_spread(hh)
    max_spread = max(spreads)
    assert max_spread == 0.0, (
        f"forward days now carry intraday shape (max within-day spread GBP{max_spread:.0f}) -- if the "
        "intraday-shape overlay has landed, set SPIKE_TAIL_SSP_RESIDUAL status: closed and flip this to a "
        "within-day-shape tolerance check in the SAME commit (register closes_when)"
    )
    # Corollary made explicit: 48 identical periods per day == exactly one distinct price per day.
    assert all(s == 0.0 for s in spreads), "at least one forward day already has within-day variance"


def test_measurement_can_see_intraday_shape():
    """R15 killer-mutation companion: the intraday-spread measurement is NOT fail-blind. A day whose 48
    periods DO vary (a spiky half-hour among calm ones) is reported with a positive spread -- so a GREEN
    'flat today' above means 'the expansion carries no intraday shape', never 'the measurement is broken'."""
    spiky_day = (
        [{"settlementDate": "2027-01-08", "settlementPeriod": p, "systemSellPrice": 50.0} for p in range(1, 39)]
        + [{"settlementDate": "2027-01-08", "settlementPeriod": 39, "systemSellPrice": 4000.0}]
        + [{"settlementDate": "2027-01-08", "settlementPeriod": p, "systemSellPrice": 50.0} for p in range(40, 49)]
    )
    spreads = _per_day_intraday_spread(spiky_day)
    assert len(spreads) == 1
    assert spreads[0] == pytest.approx(3950.0), "a within-day spike must register as a positive intraday spread"


def test_expansion_is_flat_by_construction():
    """Direct structural assertion on _expand_daily_to_hh itself (independent of any scenario preset): a
    single daily record expands to 48 periods all equal to the source price. This is the mechanism the
    intraday-shape fix must replace; when it produces varying periods, this fails as a close reminder."""
    hh = _expand_daily_to_hh([{"settlementDate": "2027-06-01", "systemSellPrice": 123.45}])
    assert len(hh) == 48
    assert {r["settlementPeriod"] for r in hh} == set(range(1, 49))
    assert {r["systemSellPrice"] for r in hh} == {123.45}, (
        "_expand_daily_to_hh no longer flat-expands -- the intraday-shape overlay has changed the "
        "expansion; close SPIKE_TAIL_SSP_RESIDUAL and flip test_forward_intraday_shape_is_flat_today"
    )
