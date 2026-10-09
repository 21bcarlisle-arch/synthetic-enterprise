"""A kettle owner's year of boils is HES's 167 kWh, and the boil, not the count, carries it.

HES (Intertek R66141, 2012) Table 14: 167 kWh/yr per owning household, n=243. Fig 450: 65% of boils
use under 0.1 kWh, 98% under 0.2. Until 2026-10-08 the boil was 0.14 kWh and the world gave 223.
Until 2026-10-09 the kettle scaled (n/2.4)^0.6 with headcount; HES Table 23 says its year does not.
"""

import datetime as dt
import statistics

import pytest

import simulation.premise_trace as pt
from simulation.premise_population import draw_premise_from_joint

HES_KETTLE_KWH_PER_OWNER = 167.0
# HES Table 23 (p.326-327), kettle kWh/yr by household type. Cell n is not published.
HES_KETTLE_BY_HOUSEHOLD_TYPE = {
    "single pensioner": 141.0,
    "single non-pensioner": 153.0,
    "multiple pensioner": 185.0,
    "with children": 167.0,
    "multiple no-dependent": 178.0,
}


def _kettle() -> pt.ApplianceSpec:
    return next(s for s in pt.APPLIANCE_CATALOGUE if s.name == "kettle")


def _hes_household_type(p: pt.BehaviourProfile) -> str:
    # The world records only whether a pensioner is PRESENT, so a mixed-age couple reads as HES's
    # "multiple pensioner", which means every adult is one.
    if p.people_count == 1:
        return "single pensioner" if p.pensioner_present else "single non-pensioner"
    if p.children_count > 0:
        return "with children"
    return "multiple pensioner" if p.pensioner_present else "multiple no-dependent"


def _kettle_years(n: int = 200) -> list[tuple[str, float]]:
    """The catalogue's expected kettle year per home over the first `n` drawn residential premises,
    with its HES household type: boil x rate x the home's intensity (if the kettle scales) x the
    weekend uplift x days at home. The season factor averages to 1 over a year by construction."""
    k = _kettle()
    out = []
    for i in range(n):
        pid = f"SYN-S{i:04d}"
        hh = draw_premise_from_joint(pid, base_seed=17, as_of=dt.date(2022, 1, 1)).household
        if not hh.is_residential:
            continue
        p = pt.behaviour_profile_for(pid, hh, seed=17)
        intensity = p.appliance_intensity if k.scales_with_people else 1.0
        out.append((
            _hes_household_type(p),
            k.power_kw * k.duration_hours * k.events_per_day * intensity
            * (5 / 7 + 2 / 7 * 1.15) * (365 - p.away_days_per_year),
        ))
    return out


def _mean_kettle_kwh_per_owner(n: int = 200) -> float:
    return statistics.mean(kwh for _, kwh in _kettle_years(n))


def test_a_kettle_owners_year_is_hes_167_kwh():
    # Defect it catches: the boil drifting back to the 0.14 kWh nameplate guess (223 kWh/yr).
    assert _mean_kettle_kwh_per_owner() == pytest.approx(HES_KETTLE_KWH_PER_OWNER, rel=0.05)


def test_the_boil_sits_where_hes_measured_boils():
    # Defect it catches: hitting 167 by cutting the count and keeping a boil HES saw in under 1
    # in 3 cycles (Fig 450: 65% under 0.1 kWh, 98% under 0.2).
    k = _kettle()
    assert 0.08 <= k.power_kw * k.duration_hours <= 0.12
    assert k.events_per_day == 4.0


def test_every_hes_household_type_boils_inside_hes_own_spread():
    # Defect it catches: the kettle scaling with headcount again. (n/2.4)^0.6 gave a one-person home
    # 91 kWh and a home with children 200 against HES's 141-185 (2026-10-09, 3,000 homes).
    by_type: dict[str, list[float]] = {}
    for t, kwh in _kettle_years(1000):
        by_type.setdefault(t, []).append(kwh)
    assert set(by_type) == set(HES_KETTLE_BY_HOUSEHOLD_TYPE), "every HES type must be drawn"
    lo, hi = min(HES_KETTLE_BY_HOUSEHOLD_TYPE.values()), max(HES_KETTLE_BY_HOUSEHOLD_TYPE.values())
    means = {t: statistics.mean(v) for t, v in by_type.items()}
    assert all(lo <= m <= hi for m in means.values()), means
