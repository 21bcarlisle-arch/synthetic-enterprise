"""The world's standing charge must BE the cap model's standing charge for the period in force.

Subject: `simulation/policy_costs.get_electricity_standing_charge_per_day` /
`get_gas_standing_charge_per_day`, which read `_CAP_SC_PENCE_PER_DAY`.

Until 2026-10-27 the readers served a calendar-year table, each row the day-weighted blend of the
cap periods in force that year, and this file pinned the blend. The pin held and the charge was
wrong on almost every day: a blend is right for a year's total and not for any day in it. Jan-Mar
2022 electricity read 40.22p against a 23.68p cap (1.70x), Apr-Dec 2022 0.87-0.89x, gas 0.95-1.07x
(SEAT_FINDING_THE_BLIND_INVARIANT_SUITE_ON_THE_67A893E749_BOOK_..._2026-10-26, breach class 2).
A pin keyed to the table's own statistic could not see that; these are keyed to the charge on
the day.

The pin is `docs/domain_artefact_library/regulatory/ofgem_cap_standing_charges.json`, which
carries the model's per-PERIOD figures. The ceiling the charge is graded against is the blind
suite's own rows (`docs/design/DOMAIN_INVARIANTS.yaml`), written without reading this code.

Mutations that must fire: restore the calendar-year blend (both day tests and the ceiling test);
change any period by 0.01p (day test); let the EARLIER of two overlapping periods win does not
fire, and that is an equivalence: in v1.31 the Oct 2018-Mar 2019 and Jan-Mar 2019 columns carry
identical values for both fuels.
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

_READERS = {
    "electricity": policy_costs.get_electricity_standing_charge_per_day,
    "gas": policy_costs.get_gas_standing_charge_per_day,
}
_INVARIANTS = _ROOT / "docs" / "design" / "DOMAIN_INVARIANTS.yaml"
_CEILING_IDS = {"electricity": "INV_STANDING_CHARGE_SVT_ELEC", "gas": "INV_STANDING_CHARGE_SVT_GAS"}


def _periods(fuel: str) -> list[dict]:
    periods = json.loads(_ARTEFACT.read_text())["periods"][fuel]
    assert periods, f"{_ARTEFACT.name} carries no {fuel} periods"
    return periods


def _in_force(periods: list[dict], day: dt.date) -> dict | None:
    """The period in force on `day`: of those covering it, the one that STARTS latest (see above)."""
    covering = [p for p in periods if p["starts"] <= day.isoformat() < p["ends_before"]]
    return max(covering, key=lambda p: p["starts"]) if covering else None


def _run_days():
    day = dt.date(SIM_START_YEAR, 1, 1)
    while day.year <= SIM_END_YEAR:
        yield day
        day += dt.timedelta(days=1)


@pytest.mark.parametrize("fuel", sorted(_READERS))
def test_every_day_the_world_runs_is_charged_the_cap_period_in_force_not_a_year_blend(fuel):
    periods = _periods(fuel)
    wrong = {}
    for day in _run_days():
        period = _in_force(periods, day)
        assert period is not None, f"{fuel}: no cap period covers {day}"
        charged = round(_READERS[fuel](day.isoformat(), "resi") * 100, 3)
        if charged != period["p_per_day_ex_vat"]:
            wrong.setdefault(period["cap_period"], (charged, period["p_per_day_ex_vat"]))
    assert not wrong, f"{fuel} standing charge (charged p/day, cap period p/day): {wrong}"


def _ceiling_rows(fuel: str) -> list[dict]:
    yaml = pytest.importorskip("yaml")
    invariants = {i["id"]: i for i in yaml.safe_load(_INVARIANTS.read_text())["invariants"]}
    inv = invariants[_CEILING_IDS[fuel]]
    tol = float(inv["tolerance"]["upper_absolute_gbp_per_day"])
    return [dict(r, _tol=tol) for r in inv["rows"] if r.get("upper") is not None]


@pytest.mark.parametrize("fuel", sorted(_READERS))
def test_no_default_tariff_day_is_charged_above_its_windows_cap(fuel):
    """Graded against the blind suite's DD ceiling, every day of every capped window it lists."""
    rows = [r for r in _ceiling_rows(fuel) if int(r["from"][:4]) <= SIM_END_YEAR]
    # Reachability: the crisis window and every capped window the world runs must be graded.
    assert len(rows) >= 21 and any(r["from"] == "2021-10-01" for r in rows), rows
    over = {}
    for row in rows:
        day, end = dt.date.fromisoformat(row["from"]), dt.date.fromisoformat(row["to"])
        while day <= end:
            charged = _READERS[fuel](day.isoformat(), "resi")
            if charged > row["upper"] + row["_tol"]:
                over.setdefault(row["from"], (day.isoformat(), round(charged, 5), row["upper"]))
            day += dt.timedelta(days=1)
    assert not over, f"{fuel} standing charge above the cap (window: first day, charged, cap): {over}"


def test_the_jan_to_mar_2022_electricity_charge_is_not_the_april_rise_three_months_early():
    """The defect's own instance, named: 40.22p/day against a 23.682p cap on 538 bill periods."""
    for day in ("2022-01-01", "2022-02-15", "2022-03-31"):
        assert policy_costs.get_electricity_standing_charge_per_day(day) <= 0.23682 + 0.0001, day
    assert policy_costs.get_electricity_standing_charge_per_day("2022-04-01") > 0.45


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
