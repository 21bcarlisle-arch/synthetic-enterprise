"""The N18 rows (eighth cold read, 2026-11-04), written blind: a pre-cap default's all-in rate sits at
or above the cheapest region's pass-through cost, and the book's default dual-fuel cost moves the way
the published default bill moved.

The defects these tests name:
  * a floor row that compares the energy line rather than the all-in rate, so a 2017 gas SVT priced
    at 2.67p all-in under a 2.73p pass-through floor passes (the b3ce2a4e73 book: every 2017 bill);
  * a year-on-year row that cannot fire, cannot pass, or reads a year it never priced as a pass;
  * a direction row that weighs prepayment or multi-register terms into a series published for
    single-rate direct debit.
"""
from __future__ import annotations

from tests.tools.test_the_domain_invariant_runner_reads_only_the_raw_export_and_every_evaluator_can_fire import (
    _account,
)
from tools import domain_invariant_runner as runner

GAS_FLOOR = {"id": "INV_UNIT_RATE_SVT_GAS_PRE_CAP_ALL_IN_FLOOR",
             "rows": [{"from": "2017-04-01", "to": "2017-09-30", "lower": 2.7264, "upper": None}]}
ELEC_FLOOR = {"id": "INV_UNIT_RATE_SVT_ELEC_PRE_CAP_ALL_IN_FLOOR",
              "rows": [{"from": "2017-04-01", "to": "2017-09-30", "lower": 11.5284, "upper": None}]}
DIRECTION = {"id": "INV_DEFAULT_DUAL_FUEL_COST_FOLLOWS_THE_PUBLISHED_DEFAULT_BILL",
             "benchmark_kwh": {"electricity": 3100, "gas": 12000},
             "rows": [{"from": "2017-01-01", "to": "2017-12-31", "lower": 1.0, "upper": None,
                       "published_change": "+4.30%"},
                      {"from": "2019-01-01", "to": "2019-12-31", "lower": 1.0, "upper": None,
                       "published_change": "+2.6%"}]}


def _status(invs, book):
    return {r["id"]: r for r in runner.run(invs, book)}


def _years(cid, fuel, rates, **kw):
    """One account on SVT across consecutive years, one term per year at that year's rate."""
    acct = None
    for year, rate in rates.items():
        a = _account(cid, fuel, rate=rate, year=year, **kw)
        if acct is None:
            acct = a
        else:
            acct["periods"] += a["periods"]
            acct["payments"] += a["payments"]
    return acct


def test_the_all_in_floor_flags_a_default_under_pass_through_and_passes_one_over_it():
    under = {"G": _account("G", "gas", rate=2.6667, year=2017, kwh_per_month=900.0),
             "E": _account("E", "electricity", rate=13.3333, year=2017)}
    over = {"G": _account("G", "gas", rate=3.8095, year=2017, kwh_per_month=900.0),
            "E": _account("E", "electricity", rate=11.0, year=2017)}
    a, b = _status([GAS_FLOOR, ELEC_FLOOR], under), _status([GAS_FLOOR, ELEC_FLOOR], over)
    assert a[GAS_FLOOR["id"]]["status"] == "FLAGGED" and b[GAS_FLOOR["id"]]["status"] == "CLEAN"
    assert a[ELEC_FLOOR["id"]]["status"] == "CLEAN" and b[ELEC_FLOOR["id"]]["status"] == "FLAGGED"


def test_the_direction_row_can_flag_pass_and_leave_an_unpriced_year_unbounded():
    def book(g2016, g2017):
        return {"E": _years("E", "electricity", {2016: 13.3333, 2017: 13.3333}),
                "G": _years("G", "gas", {2016: g2016, 2017: g2017}, kwh_per_month=900.0)}
    fell, rose = _status([DIRECTION], book(3.8095, 2.6667)), _status([DIRECTION], book(3.8095, 4.2))
    f, r = fell[DIRECTION["id"]], rose[DIRECTION["id"]]
    assert (f["status"], f["flagged"], f["checked"]) == ("FLAGGED", 1, 1)
    assert (r["status"], r["checked"]) == ("CLEAN", 1)
    # 2019 has neither itself nor 2018 priced: counted unbounded, never passed.
    assert f["unbounded"] == 1 and r["unbounded"] == 1


def test_only_single_rate_direct_debit_defaults_price_the_series():
    base = {"E": _years("E", "electricity", {2016: 13.3333, 2017: 13.3333}),
            "G": _years("G", "gas", {2016: 3.8095, 2017: 4.2}, kwh_per_month=900.0)}
    # A prepayment gas default and an Economy 7 default that fell would flag if they were read.
    base["PG"] = _years("PG", "gas", {2016: 9.0, 2017: 1.0}, kwh_per_month=900.0, method="prepayment")
    base["M"] = _years("M", "electricity", {2016: 40.0, 2017: 1.0}, registers=("1", "2"))
    assert _status([DIRECTION], base)[DIRECTION["id"]]["status"] == "CLEAN"
