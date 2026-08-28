"""Tests for `company/analytics/household_value_share.py` — atom `A47`.

The subject is the household's side of the score: what a customer kept, in
pounds, against the published default tariff over its own metered volumes.

R15 — every test below names the defect it fires on, and three of them name a
defect this module ACTUALLY HAD, caught by printing the table at real Ofgem cap
levels before any test existed:

  * the first draft summed a household's payments over its WHOLE year and its
    counterfactual over only the COVERED part, so a year straddling the cap's
    start reported a coverage gap as a saving;
  * an uncovered customer-year reported `saving = 0 - paid`, a confident
    negative number where the truth is "we cannot say";
  * the portfolio row summed those Nones into a plausible total.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import pytest

from company.analytics.household_value_share import (
    HouseholdValueShare,
    build_household_value_share,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE = REPO_ROOT / "company" / "analytics" / "household_value_share.py"

#: Ofgem TDCV for a typical domestic electricity household, spread evenly.
TDCV_KWH_PER_YEAR = 2700.0
DAILY_KWH = TDCV_KWH_PER_YEAR / 365.0

#: A real published cap level (Ofgem, 2022 windows, £/MWh excl. standing charge).
CAP_2022 = 283.4
WHOLESALE = 180.0


def _fixed_rate(rate: float) -> callable:
    return lambda _d, _c="electricity": rate


def _records(
    *,
    year: int = 2022,
    days: int = 365,
    our_rate: float,
    customer_id: str = "C1",
    start_day: int = 0,
) -> list[dict]:
    out = []
    for i in range(start_day, start_day + days):
        d = dt.date(year, 1, 1) + dt.timedelta(days=i)
        out.append({
            "customer_id": customer_id,
            "settlement_date": d.isoformat(),
            "consumption_kwh": DAILY_KWH,
            "revenue_gbp": DAILY_KWH / 1000.0 * our_rate,
            "wholesale_cost_gbp": DAILY_KWH / 1000.0 * WHOLESALE,
            "margin_gbp": DAILY_KWH / 1000.0 * (our_rate - WHOLESALE),
        })
    return out


# ── the director's sentence, made arithmetic ────────────────────────────────

def test_pricing_at_the_counterfactual_shares_nothing():
    """DIRECTOR, 2026-08-28: "Charging someone the cap transfers value, it
    doesn't create it."

    Fires on: any formulation in which pricing AT the counterfactual still
    credits the supplier with a household saving — the defect that would make
    this figure agree with the one-sided score it exists to correct.
    """
    view = build_household_value_share(
        _records(our_rate=CAP_2022), svt_rate_for=_fixed_rate(CAP_2022))
    row = view.portfolio
    assert row.household_saving_gbp == pytest.approx(0.0, abs=1e-9)
    assert row.household_share_of_the_split_pct == pytest.approx(0.0, abs=1e-9)
    # And the supplier's own side is emphatically NOT zero — the surplus went
    # somewhere. Without this line the test would pass on a module that
    # returned zeros for everything.
    assert row.our_gross_margin_gbp > 0.0


def test_pricing_above_the_counterfactual_is_a_negative_saving_not_a_floor():
    """Fires on: clamping the saving at zero, which would hide the case where a
    household paid MORE than the published default — the one the maximiser
    finds."""
    view = build_household_value_share(
        _records(our_rate=CAP_2022 * 1.30),
        svt_rate_for=_fixed_rate(CAP_2022))
    assert view.portfolio.household_saving_gbp < 0.0
    assert view.portfolio.household_saving_pct_of_counterfactual == pytest.approx(-30.0, abs=1e-6)


def test_the_saving_tracks_the_position_linearly():
    """Fires on: a sign error or a scale error anywhere in the sum."""
    for position in (-0.30, -0.15, -0.05, 0.10):
        view = build_household_value_share(
            _records(our_rate=CAP_2022 * (1 + position)),
            svt_rate_for=_fixed_rate(CAP_2022))
        assert view.portfolio.household_saving_pct_of_counterfactual == pytest.approx(
            -100.0 * position, abs=1e-6)


# ── the three defects the module actually had ───────────────────────────────

def test_an_uncovered_period_is_excluded_from_BOTH_sides():
    """THE DEFECT THE PRINTED TABLE CAUGHT. Half a year with a published rate
    and half without must compare like with like.

    Fires on: accumulating revenue for a period whose counterfactual is missing
    — which reports the uncovered half's payments as money the household lost.
    """
    def half_covered(d: dt.date, _commodity: str) -> float | None:
        return CAP_2022 if d.month <= 6 else None

    view = build_household_value_share(
        _records(our_rate=CAP_2022, days=365), svt_rate_for=half_covered)
    row = view.portfolio
    # Priced exactly at the counterfactual for the whole year, so a correct
    # like-for-like comparison is zero however much of the year is covered.
    assert row.household_saving_gbp == pytest.approx(0.0, abs=1e-9)
    assert row.settled_rows_without_a_counterfactual > 0
    assert row.excluded_consumption_mwh > 0.0
    assert 40.0 < row.coverage_pct < 60.0


def test_a_wholly_uncovered_customer_year_is_None_and_never_zero():
    """FAIL-OPEN killer. "They saved nothing" and "we cannot say" must not be
    the same value.

    Fires on: returning 0.0 (or `0 - paid`) when no period in the year had a
    published counterfactual — 2016-2018 for every customer, since the Ofgem
    cap's published windows begin in 2019.
    """
    view = build_household_value_share(
        _records(our_rate=250.0), svt_rate_for=lambda _d, _c: None)
    row = view.by_customer_period[("C1", 2022)]
    assert row.household_saving_gbp is None
    assert row.household_saving_pct_of_counterfactual is None
    assert row.household_share_of_the_split_pct is None
    assert row.coverage_pct == pytest.approx(0.0)
    assert view.groups_without_any_counterfactual == [("C1", 2022)]


def test_the_portfolio_is_None_when_nothing_was_comparable():
    """POPULATION FLOOR. An empty book and a book whose counterfactual never
    resolved must not both report £0 saved.

    Fires on: summing an empty list of savings to 0.0 in the portfolio row.
    """
    view = build_household_value_share(
        _records(our_rate=250.0), svt_rate_for=lambda _d, _c: None)
    assert view.portfolio.household_saving_gbp is None
    assert view.groups == 1  # the row EXISTS; only its saving is unknown


def test_a_partly_blind_book_still_reports_the_customers_it_could_see():
    """Fires on: one uncovered customer-year suppressing the whole portfolio."""
    covered = _records(our_rate=CAP_2022 * 0.9, customer_id="SEEN")
    blind = _records(our_rate=CAP_2022 * 0.9, customer_id="BLIND", year=2016)

    def cap_from_2019(d: dt.date, _commodity: str) -> float | None:
        return CAP_2022 if d.year >= 2019 else None

    view = build_household_value_share(covered + blind, svt_rate_for=cap_from_2019)
    assert view.portfolio.household_saving_gbp > 0.0
    assert view.by_customer_period[("BLIND", 2016)].household_saving_gbp is None
    assert view.groups_without_any_counterfactual == [("BLIND", 2016)]


# ── basis discipline (R14) ──────────────────────────────────────────────────

def test_net_margin_is_absent_rather_than_quietly_the_gross_one():
    """R14 and the 2026-08-17 finding against `saas/cost_to_serve.py`: a
    contribution margin wearing a net margin's name valued the whole book.

    Fires on: defaulting `our_net_margin_gbp` to the gross figure when no
    cost-to-serve map is supplied.
    """
    view = build_household_value_share(
        _records(our_rate=CAP_2022 * 0.9), svt_rate_for=_fixed_rate(CAP_2022))
    row = view.portfolio
    assert row.our_net_margin_gbp is None
    assert row.our_gross_margin_gbp > 0.0


def test_the_net_margin_is_read_off_the_records_when_every_row_carries_one():
    """`net_margin_gbp` is on the settled rows themselves, after policy levies,
    network charges, capital and bad debt. Fires on: ignoring it."""
    records = _records(our_rate=CAP_2022 * 0.9)
    for r in records:
        r["net_margin_gbp"] = 0.5
    view = build_household_value_share(records, svt_rate_for=_fixed_rate(CAP_2022))
    assert view.portfolio.our_net_margin_gbp == pytest.approx(0.5 * len(records))


def test_a_single_row_without_a_net_margin_makes_the_whole_year_None():
    """Fires on: summing the rows that happen to carry the field, which is a
    smaller net margin wearing the whole year's name -- the 2026-08-17 defect
    against `saas/cost_to_serve.py` in a new place."""
    records = _records(our_rate=CAP_2022 * 0.9)
    for r in records[:-1]:
        r["net_margin_gbp"] = 0.5
    view = build_household_value_share(records, svt_rate_for=_fixed_rate(CAP_2022))
    assert view.by_customer_period[("C1", 2022)].our_net_margin_gbp is None
    assert view.portfolio.our_net_margin_gbp is None


def test_gas_volumes_are_never_valued_at_the_electricity_tariff():
    """THE DEFECT THE RECORD SHAPE CAUGHT. The settled book is dual fuel --
    `simulation/gas_settlement.py` writes gas rows into the same list, tagged
    `commodity`. Valuing them at the electricity default tariff overstates the
    counterfactual roughly four-fold, silently, in our favour.

    MUTATION: drop the `commodity` argument and pass the electricity rate to
    every row; the gas counterfactual jumps from 41.4 to 283.4 £/MWh and this
    reds.
    """
    def by_fuel(_d: dt.date, commodity: str) -> float | None:
        return {"electricity": 283.4, "gas": 73.7}.get(commodity)

    elec = _records(our_rate=283.4, days=10, customer_id="DUAL")
    gas = _records(our_rate=73.7, days=10, customer_id="DUAL")
    for r in elec:
        r["commodity"] = "electricity"
    for r in gas:
        r["commodity"] = "gas"

    view = build_household_value_share(elec + gas, svt_rate_for=by_fuel)
    # Each fuel priced exactly at its OWN published tariff, so the saving is zero.
    assert view.portfolio.household_saving_gbp == pytest.approx(0.0, abs=1e-9)


def test_a_commodity_with_no_published_reference_is_excluded_not_guessed():
    """Fires on: falling back to the other fuel's rate, or to zero, when the
    caller says it has no reference for this commodity."""
    def elec_only(_d: dt.date, commodity: str) -> float | None:
        return 283.4 if commodity == "electricity" else None

    gas = _records(our_rate=73.7, days=10, customer_id="GASONLY")
    for r in gas:
        r["commodity"] = "gas"
    view = build_household_value_share(gas, svt_rate_for=elec_only)
    row = view.by_customer_period[("GASONLY", 2022)]
    assert row.household_saving_gbp is None
    assert row.settled_rows_without_a_counterfactual == 10


def test_the_share_is_undefined_rather_than_zero_when_there_is_nothing_to_split():
    """Fires on: a divide-by-zero guard that returns 0.0, which reads as "the
    household got none of it" when the truth is that there was no surplus."""
    row = HouseholdValueShare(
        customer_id="C", period=2022, consumption_mwh=1.0, paid_gbp=100.0,
        counterfactual_gbp=0.0, household_saving_gbp=-100.0,
        our_gross_margin_gbp=0.0, our_net_margin_gbp=None)
    assert row.household_share_of_the_split_pct is None
    assert row.household_saving_pct_of_counterfactual is None


def test_the_portfolio_row_cannot_be_mistaken_for_a_customer():
    """Fires on: giving the portfolio row a plausible customer id or year, so a
    total that leaks into a per-customer table reads as an account."""
    view = build_household_value_share(
        _records(our_rate=CAP_2022 * 0.9), svt_rate_for=_fixed_rate(CAP_2022))
    assert view.portfolio.customer_id == "__portfolio__"
    assert view.portfolio.period == 0
    assert view.portfolio.customer_id not in {k[0] for k in view.by_customer_period}


# ── the wall ────────────────────────────────────────────────────────────────

def test_the_module_never_imports_the_world():
    """EPISTEMIC WALL. Every input is a supplier observable; the counterfactual
    rate arrives through the signature, exactly as `simulation/competitor_reference.py`
    takes its wholesale price.

    Fires on: importing `simulation`, `sim`, or reading a world constant — the
    class-(a) crossing that is at zero and stays there.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
    assert not (imported & {"simulation", "sim"}), (
        "household_value_share reaches into the world: " + ", ".join(sorted(imported)))


def test_the_counterfactual_is_injected_and_keyword_only():
    """Fires on: a positional or defaulted rate source, which is how an import
    of the world's `svt_rates` sneaks back in as a default argument."""
    import inspect

    sig = inspect.signature(build_household_value_share)
    param = sig.parameters["svt_rate_for"]
    assert param.kind is inspect.Parameter.KEYWORD_ONLY
    assert param.default is inspect.Parameter.empty


# ── the shape of a real settled book ────────────────────────────────────────

def test_a_row_this_view_cannot_value_is_skipped_and_COUNTED():
    """`simulation/settlement_daily.fold_to_days` passes any record WITHOUT a
    `settlement_date` through untouched, so a live `all_records` carries rows
    this view cannot value.

    Fires on: reaching into them (a KeyError mid-run, which is what the first
    draft would have done on the first real ladder rung) OR dropping them
    silently, which shrinks the book without saying so.
    """
    good = _records(our_rate=CAP_2022 * 0.9)
    junk = [
        {"customer_id": "C1", "note": "a non-settlement row fold_to_days passed through"},
        {"settlement_date": "2022-03-01", "consumption_kwh": 1.0},          # no customer
        {"customer_id": "C1", "settlement_date": "2022-03-01"},             # no volume
        {"customer_id": "C1", "settlement_date": "2022-03-01",
         "consumption_kwh": 1.0, "revenue_gbp": None, "margin_gbp": 1.0},   # revenue absent
    ]
    view = build_household_value_share(good + junk, svt_rate_for=_fixed_rate(CAP_2022))
    assert view.records_this_view_could_not_value == len(junk)
    # The valuable rows are still valued -- the skip must not take the book with it.
    assert view.portfolio.household_saving_gbp > 0.0
    assert view.groups == 1


def test_an_all_junk_book_reports_no_customer_years_rather_than_zero_pounds():
    """POPULATION FLOOR at the input. A book of rows this view cannot read must
    not look like a book that saved nothing."""
    view = build_household_value_share(
        [{"note": "unshaped"}] * 5, svt_rate_for=_fixed_rate(CAP_2022))
    assert view.groups == 0
    assert view.portfolio.household_saving_gbp is None
    assert view.records_this_view_could_not_value == 5
