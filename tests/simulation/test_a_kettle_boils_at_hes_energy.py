"""A kettle owner's year of boils is HES's 167 kWh, and the boil, not the count, carries it.

HES (Intertek R66141, 2012) Table 14: 167 kWh/yr per owning household, n=243. Fig 450: 65% of boils
use under 0.1 kWh, 98% under 0.2. Until 2026-10-08 the boil was 0.14 kWh and the world gave 223.
"""

import datetime as dt
import statistics

import pytest

import simulation.premise_trace as pt
from simulation.premise_population import draw_premise_from_joint

HES_KETTLE_KWH_PER_OWNER = 167.0


def _kettle() -> pt.ApplianceSpec:
    return next(s for s in pt.APPLIANCE_CATALOGUE if s.name == "kettle")


def _mean_kettle_kwh_per_owner(n: int = 200) -> float:
    """The catalogue's expected kettle year per home over the first `n` drawn residential premises:
    boil x rate x the home's intensity x the weekend uplift x days at home. The season factor
    averages to 1 over a year by construction."""
    k = _kettle()
    out = []
    for i in range(n):
        pid = f"SYN-S{i:04d}"
        hh = draw_premise_from_joint(pid, base_seed=17, as_of=dt.date(2022, 1, 1)).household
        if not hh.is_residential:
            continue
        p = pt.behaviour_profile_for(pid, hh, seed=17)
        out.append(
            k.power_kw * k.duration_hours * k.events_per_day * p.appliance_intensity
            * (5 / 7 + 2 / 7 * 1.15) * (365 - p.away_days_per_year)
        )
    return statistics.mean(out)


def test_a_kettle_owners_year_is_hes_167_kwh():
    # Defect it catches: the boil drifting back to the 0.14 kWh nameplate guess (223 kWh/yr).
    assert _mean_kettle_kwh_per_owner() == pytest.approx(HES_KETTLE_KWH_PER_OWNER, rel=0.05)


def test_the_boil_sits_where_hes_measured_boils():
    # Defect it catches: hitting 167 by cutting the count and keeping a boil HES saw in under 1
    # in 3 cycles (Fig 450: 65% under 0.1 kWh, 98% under 0.2).
    k = _kettle()
    assert 0.08 <= k.power_kw * k.duration_hours <= 0.12
    assert k.events_per_day == 4.0
