"""A profiled home is billed on its meter and bought on its profile.

THE DEFECT (2026-10-22). The run priced each home's OWN half hours at SSP, which is MHHS-era
settlement applied to 2016-2025. A non-HH meter of the period was settled on its volume x its
registered Profile Class shape (SEAT_PREREGISTRATION_A_PROFILED_HOME_SETTLES_ITS_OWN_VOLUME_ON_ITS_
REGISTERED_PROFILE_2026-10-22.md, P15a).

One control per writer over the whole contract: the bought volume follows the profile, trued up to
the metered volume over the term; everything billed stays on the meter. A day-loaded home on a
night-loaded profile is chosen so the two shapes give different costs, which is asserted first --
without it every leg below passes with the settled shape ignored.

MUTATIONS, RUN 2026-10-22, all red:
  * the true-up factor dropped (k = 1) -> the volume leg reds.
  * `settle_hedged_period` handed the metered kWh again -> the cost legs red.
  * revenue left on the settled volume -> the billed leg reds.
  * `run_deemed_term` prices spot on the metered kWh -> its cost leg reds.
"""
from __future__ import annotations

import pytest

from simulation.hedged_settlement import run_deemed_term, run_hedged_term

DAYS = ("2019-03-01", "2019-03-02")
PRICES = [{"settlementDate": d, "settlementPeriod": p, "systemSellPrice": 20.0 + p}
          for d in DAYS for p in range(1, 49)]
DAY_HOME = lambda d: [0.1] * 14 + [0.5] * 34  # noqa: E731 -- own meter: day-loaded
NIGHT_PROFILE = lambda d: [3.0] * 14 + [1.0] * 34  # noqa: E731 -- registered shape, any scale


def _hedged(settled):
    return run_hedged_term("C1", DAYS[0], "2019-03-03", 150.0, 40.0, 0.25, 10.0, DAY_HOME,
                           PRICES, settled_shape=settled)


def _deemed(settled):
    return run_deemed_term("C1", DAYS[0], "2019-03-03", 0.2, DAY_HOME, PRICES,
                           settled_shape=settled)


def _sum(rows, key):
    return sum(r[key] for r in rows)


@pytest.mark.parametrize("run", [_hedged, _deemed])
def test_billed_on_the_meter_and_bought_on_the_trued_up_profile(run):
    own, prof = run(None), run(NIGHT_PROFILE)
    # The case can tell the two shapes apart: night power is cheaper here, so buying on the
    # night-loaded profile must cost less.
    assert _sum(prof, "wholesale_cost_gbp") < _sum(own, "wholesale_cost_gbp") - 0.01
    # Volume trued up: the profile buys exactly what the meter used.
    assert _sum(prof, "settled_kwh") == pytest.approx(_sum(own, "consumption_kwh"))
    assert "settled_kwh" not in own[0]
    # Bought on the profile, period by period.
    k = _sum(own, "consumption_kwh") / (2 * (14 * 3.0 + 34 * 1.0))
    assert prof[0]["settled_kwh"] == pytest.approx(3.0 * k)
    assert prof[0]["hedged_volume_kwh"] + prof[0]["unhedged_volume_kwh"] == pytest.approx(3.0 * k)
    # Everything billed stays on the meter, row for row.
    for a, b in zip(own, prof):
        for key in ("consumption_kwh", "revenue_gbp", "policy_cost_gbp", "network_cost_gbp",
                    "unit_rate_gbp_per_mwh"):
            assert a[key] == pytest.approx(b[key]), key
        assert b["margin_gbp"] == pytest.approx(
            a["margin_gbp"] + a["wholesale_cost_gbp"] - b["wholesale_cost_gbp"])
