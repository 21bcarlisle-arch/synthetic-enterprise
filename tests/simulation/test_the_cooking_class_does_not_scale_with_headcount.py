"""No cooking appliance's year grows with headcount, because HES's does not.

HES (Intertek R66141, 2012) ch.11.2, Figs 414-418: the cooking total per household by type is 429
(single pensioner), 505 (single non-pensioner), 452 (multiple pensioner), 422 (with children) and
497 (multiple, no dependent children), against 460 for all households. Table 23 shows no headcount
gradient in any cooking cell either: the oven reads 183 in a home with children and 375 for a single
non-pensioner. Until 2026-10-09 the world scaled every cooking appliance by (n/2.4)^0.6.
docs/market_research/what_a_cooking_appliance_uses_in_a_year_hes_2012.md.
"""

import datetime as dt
import statistics

import simulation.premise_trace as pt
from simulation.premise_population import draw_premise_from_joint

HES_COOKING_TOTAL_BY_HOUSEHOLD_TYPE = {
    "single pensioner": 429.0,
    "single non-pensioner": 505.0,
    "multiple pensioner": 452.0,
    "with children": 422.0,
    "multiple no-dependent": 497.0,
}
HES_COOKING_TOTAL_ALL_HOUSEHOLDS = 460.0


def _cooking() -> list[pt.ApplianceSpec]:
    return [s for s in pt.APPLIANCE_CATALOGUE if s.name in pt._HES_SEASON_GROUP
            and pt._HES_SEASON_GROUP[s.name] == "cooking"]


def _hes_household_type(p: pt.BehaviourProfile) -> str:
    # The world records only whether a pensioner is PRESENT, so a mixed-age couple reads as HES's
    # "multiple pensioner", which means every adult is one.
    if p.people_count == 1:
        return "single pensioner" if p.pensioner_present else "single non-pensioner"
    if p.children_count > 0:
        return "with children"
    return "multiple pensioner" if p.pensioner_present else "multiple no-dependent"


def _years_by_type(n: int = 1000) -> dict[str, dict[str, list[float]]]:
    """appliance -> HES type -> each drawn home's expected year: energy per use x rate x intensity (if
    the appliance scales) x the weekend uplift x days at home. Ownership and cooking fuel are left
    out: this asks the SHAPE of the term by type, not an owner's level."""
    out: dict[str, dict[str, list[float]]] = {s.name: {} for s in _cooking()}
    for i in range(n):
        pid = f"SYN-S{i:04d}"
        hh = draw_premise_from_joint(pid, base_seed=17, as_of=dt.date(2022, 1, 1)).household
        if not hh.is_residential:
            continue
        p = pt.behaviour_profile_for(pid, hh, seed=17)
        days = (5 / 7 + 2 / 7 * 1.15) * (365 - p.away_days_per_year)
        for s in _cooking():
            intensity = p.appliance_intensity if s.scales_with_people else 1.0
            out[s.name].setdefault(_hes_household_type(p), []).append(
                s.power_kw * s.duration_hours * s.events_per_day * intensity * days
            )
    return out


def test_the_cooking_class_is_the_five_hes_appliances():
    # Defect it catches: the class going empty, which would leave both legs below vacuously green.
    assert {s.name for s in _cooking()} == {"kettle", "toaster", "microwave", "oven", "hob"}


def test_the_cooking_total_by_household_type_sits_inside_hes_own_spread():
    # Defect it catches: cooking scaling with headcount again. Scaled, a one-person home's total read
    # about 0.74 of the all-household figure and a home with children about 1.27, against HES's
    # 0.92-1.10 (2026-10-09, 3,000 homes).
    years = _years_by_type()
    types = set(HES_COOKING_TOTAL_BY_HOUSEHOLD_TYPE)
    assert all(set(by_type) == types for by_type in years.values()), "every HES type must be drawn"
    total = {t: sum(statistics.mean(years[a][t]) for a in years) for t in types}
    everyone = sum(statistics.mean(sum(years[a].values(), [])) for a in years)
    lo = min(HES_COOKING_TOTAL_BY_HOUSEHOLD_TYPE.values()) / HES_COOKING_TOTAL_ALL_HOUSEHOLDS
    hi = max(HES_COOKING_TOTAL_BY_HOUSEHOLD_TYPE.values()) / HES_COOKING_TOTAL_ALL_HOUSEHOLDS
    assert all(lo <= v / everyone <= hi for v in total.values()), (total, everyone)


def test_no_cooking_appliance_spreads_by_household_type_wider_than_hes_cooking_total():
    # Defect it catches: ONE appliance put back on headcount, which the total above dilutes (the
    # toaster or microwave alone moves it under 2%). Scaled, any appliance spreads about 2.2x
    # across types; HES's cooking total spreads 505/422 = 1.20x.
    bound = max(HES_COOKING_TOTAL_BY_HOUSEHOLD_TYPE.values()) / min(
        HES_COOKING_TOTAL_BY_HOUSEHOLD_TYPE.values())
    spreads = {}
    for name, by_type in _years_by_type().items():
        means = [statistics.mean(v) for v in by_type.values()]
        spreads[name] = max(means) / min(means)
    assert all(v <= bound for v in spreads.values()), spreads
