"""The world's standing-charge tables must BE the cap model's standing charge, blended by date.

Subject: `simulation/policy_costs._ELEC_SC_PENCE_PER_DAY_BY_YEAR` / `_GAS_SC_PENCE_PER_DAY_BY_YEAR`.

Until 2026-10-01 the tables carried figures that were derived once, by hand, from the gitignored
cap level model, and their comment described a statistic (the regional median) that does not
reproduce them: they are the median of 15 Total rows, the model's own "GB average" row included.
2025 was missing and clamped silently to 2024. Nothing could notice either, because the only
pin was the comment.

The pin is `docs/domain_artefact_library/regulatory/ofgem_cap_standing_charges.json`, which
carries the model's per-PERIOD figures and no yearly blend. This file does the blend, so the
reading (day-weighted, the cap column winning where it overlaps the model's historical column)
is under test rather than copied. The electricity periods are also carried, independently, by
`ofgem_cap_unit_rate_composition.json`; the two extractions must agree.

Mutations that must fire: change any row by 0.01p (equality); drop the 2025 row (coverage);
count the early-2019 overlap twice (equality, gas 2019 moves 25.14 -> 25.03). Letting the EARLIER
column win instead does not fire, and that is an equivalence, not a missing test: in v1.31 the two
overlapping columns carry identical values for both fuels, so only counting the quarter once binds.
"""
from __future__ import annotations

import datetime as dt
import json
import statistics
from pathlib import Path

import pytest

from simulation import policy_costs
from simulation.household_demand import SIM_END_YEAR, SIM_START_YEAR

_ROOT = Path(__file__).resolve().parent.parent.parent
_COMMONS = _ROOT / "docs" / "domain_artefact_library" / "regulatory"
_ARTEFACT = _COMMONS / "ofgem_cap_standing_charges.json"
_COMPOSITION = _COMMONS / "ofgem_cap_unit_rate_composition.json"
_MODEL = _ROOT / "sim" / "cache" / "ofgem_cap_level_models" / "Default-tariff-cap-level-v1.31.xlsx"

_TABLES = {
    "electricity": policy_costs._ELEC_SC_PENCE_PER_DAY_BY_YEAR,
    "gas": policy_costs._GAS_SC_PENCE_PER_DAY_BY_YEAR,
}


def _periods(fuel: str) -> list[dict]:
    periods = json.loads(_ARTEFACT.read_text())["periods"][fuel]
    assert periods, f"{_ARTEFACT.name} carries no {fuel} periods"
    return periods


def _in_force(periods: list[dict], day: dt.date) -> dict | None:
    """The period in force on `day`: of those covering it, the one that STARTS latest (see above)."""
    covering = [p for p in periods if p["starts"] <= day.isoformat() < p["ends_before"]]
    return max(covering, key=lambda p: p["starts"]) if covering else None


def _calendar_year_blend(periods: list[dict], year: int) -> float | None:
    day, total, days = dt.date(year, 1, 1), 0.0, 0
    while day.year == year:
        period = _in_force(periods, day)
        if period is None:
            return None
        total += period["p_per_day_ex_vat"]
        days += 1
        day += dt.timedelta(days=1)
    return total / days


@pytest.mark.parametrize("fuel", sorted(_TABLES))
def test_every_tabled_year_is_the_day_weighted_blend_of_the_cap_periods(fuel):
    periods = _periods(fuel)
    wrong = {
        year: (pence, round(_calendar_year_blend(periods, year), 2))
        for year, pence in _TABLES[fuel].items()
        if _calendar_year_blend(periods, year) is None
        or round(_calendar_year_blend(periods, year), 2) != pence
    }
    assert not wrong, f"{fuel} standing charge (tabled, blended from the cap model): {wrong}"


@pytest.mark.parametrize("fuel", sorted(_TABLES))
def test_no_year_the_world_runs_is_served_by_a_clamp(fuel):
    missing = [y for y in range(SIM_START_YEAR, SIM_END_YEAR + 1) if y not in _TABLES[fuel]]
    assert not missing, f"{fuel} standing charge clamps to a neighbouring year for {missing}"


def test_the_overlap_rule_is_reachable():
    """The latest-start rule only matters where two periods cover one day; assert one does."""
    periods = _periods("gas")
    overlapping = [
        day for day in (dt.date(2019, 1, 1) + dt.timedelta(days=n) for n in range(90))
        if sum(p["starts"] <= day.isoformat() < p["ends_before"] for p in periods) > 1
    ]
    assert overlapping, "no day is covered by two periods, so the overlap rule is untested"


def test_the_electricity_periods_agree_with_the_independent_composition_extraction():
    composition = {
        p["cap_period"]: p["standing_charge_p_per_day_ex_vat"]
        for p in json.loads(_COMPOSITION.read_text())["by_payment_method"]["direct_debit"]["periods"]
    }
    ours = {p["cap_period"]: p["p_per_day_ex_vat"] for p in _periods("electricity")}
    assert set(ours) == set(composition)
    off = {k: (ours[k], composition[k]) for k in ours if abs(ours[k] - composition[k]) > 0.0015}
    assert not off, f"two extractions of one model disagree: {off}"


@pytest.mark.skipif(not _MODEL.exists(), reason="cap level model is gitignored and not cached here")
def test_the_artefact_is_the_cached_model():
    openpyxl = pytest.importorskip("openpyxl")
    workbook = openpyxl.load_workbook(_MODEL, read_only=True, data_only=True)
    try:
        for fuel, sheet in json.loads(_ARTEFACT.read_text())["basis"]["sheets"].items():
            rows = list(workbook[sheet].iter_rows(values_only=True))
            column = {label: j for j, label in enumerate(rows[11]) if label}
            totals = [r for r in rows if r[1] == "Total"]
            for period in _periods(fuel):
                values = [r[column[period["cap_period"]]] for r in totals]
                assert len(values) == period["rows"]
                assert round(statistics.median(values) / 365 * 100, 3) == period["p_per_day_ex_vat"]
    finally:
        workbook.close()
