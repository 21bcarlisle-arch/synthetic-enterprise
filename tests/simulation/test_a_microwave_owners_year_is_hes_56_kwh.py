"""A microwave owner's year is HES's 56 kWh, and the use count, not the use, carries it.

HES (Intertek R66141, 2012) §11.8 and Table 14: 56 kWh/yr per owning household, n=219. Until
2026-10-09 the world gave 0.8 six-minute uses a day at 0.9 kW, 26 kWh. HES publishes no uses a day
and no energy per use, so the split is a judgement: the six-minute use is already long for a reheat.
docs/staging/SEAT_FINDING_THE_MICROWAVE_LEVEL_IS_TIME_IN_USE_AGAINST_HES_56_2026-10-09.md.
"""

import datetime as dt
import statistics

import pytest

import simulation.premise_trace as pt
from simulation.premise_population import draw_premise_from_joint

HES_MICROWAVE_KWH_PER_OWNER = 56.0


def _microwave() -> pt.ApplianceSpec:
    return next(s for s in pt.APPLIANCE_CATALOGUE if s.name == "microwave")


def _mean_microwave_kwh_per_owner(n: int = 200) -> float:
    """use x rate x the home's intensity (if it scales) x the weekend uplift x days at home, over
    the first `n` drawn residential premises. The season factor averages to 1 over a year."""
    m = _microwave()
    years = []
    for i in range(n):
        pid = f"SYN-S{i:04d}"
        hh = draw_premise_from_joint(pid, base_seed=17, as_of=dt.date(2022, 1, 1)).household
        if not hh.is_residential:
            continue
        p = pt.behaviour_profile_for(pid, hh, seed=17)
        intensity = p.appliance_intensity if m.scales_with_people else 1.0
        years.append(
            m.power_kw * m.duration_hours * m.events_per_day * intensity
            * (5 / 7 + 2 / 7 * 1.15) * (365 - p.away_days_per_year)
        )
    return statistics.mean(years)


def test_a_microwave_owners_year_is_hes_56_kwh():
    # Defect it catches: the use count drifting back to the unsourced 0.8 a day (26 kWh/yr).
    assert _mean_microwave_kwh_per_owner() == pytest.approx(HES_MICROWAVE_KWH_PER_OWNER, rel=0.05)


def test_a_use_is_no_longer_than_a_reheat():
    # Defect it catches: reaching 56 by stretching each use to 13 minutes, which HES's stated
    # dominant use (reheating drinks and food) does not support.
    assert _microwave().duration_hours <= 0.10
