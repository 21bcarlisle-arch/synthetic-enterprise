"""EP1's point-in-time belief series — the thing a coupled-triad gap needs and did not have.

WHY THIS FILE EXISTS (R15: a control counts as evidence only once a mutation proves it
fires on its own named defect).

`company.analytics.customer_value_view.build_three_horizon_clv_snapshots` records EP1's
estimate at each year end from the records observable AT that year end. Everything that
makes it worth having is a property no type checker sees:

1. **The blindfold.** Year Y's belief must contain no fact from year Y+1. The defect is
   not a crash, it is a better-looking number — the exact shape of the 2026-07-10
   hedge-volatility foresight bug, which passed every test it had.
2. **A blank is not a zero.** Constraint 3 of the estimator. A series that flattened
   `None` to `0.0`, or dropped the named reason on the way out, would republish the
   defect the estimator was built to remove, one layer further from anyone who would
   notice.
3. **The basis travels.** A valuation series whose horizon and discount rate are not
   stated is uninterpretable, and a grader would have to guess about the thing it grades.
   With no years there is no book and therefore no basis, and the empty branch must say
   so rather than name a horizon nothing was computed on — the empty branch being where
   pass 16 found this atom's last fail-open.
4. **A partial year is a shorter period, not a smaller number.** Publishing the two as
   comparable is what produced a £3,255,946 "fall" that never happened in the sibling
   series.

Each `test_mutation_*` PERFORMS the named defect against the control's own predicate and
requires it to go red. Pass 17's lesson is aimed at rather than restated: the mutations
here hit the SUBJECT (the series) and not only the checker, because a battery aimed only
at a checker fires perfectly while measuring the wrong thing.
"""

from __future__ import annotations

import copy

import pytest

from company.analytics.clv_three_horizon import Horizon
from company.analytics.customer_value_view import (
    BLANK_WITHOUT_REASON,
    build_customer_value_view,
    build_three_horizon_clv_snapshots,
)

PRICE_DIFFERENTIAL_PCT = 0.0  # the run module's own value, at its own name

HORIZONS = tuple(h.value for h in Horizon)


# ---------------------------------------------------------------------------
# Fixtures.
#
# `build_churn_risk` needs 12+ months before an account has a renewal point at all,
# and an account with no renewal points never reaches EP1 — so the book must be
# several years deep or every assertion below compares {} against {}. C3 is acquired
# LATE on purpose: it is the subject of the blindfold control, and a fixture in which
# every customer exists from the start could not fail that control.
# ---------------------------------------------------------------------------

_EARLY = ("C1", "C2")
_LATE = "C3"


def _customers() -> list[dict]:
    return [
        {
            "customer_id": "C1",
            "segment": "resi",
            "acquisition_date": "2019-03-10",
            "contract_type": "fixed_1yr",
            "epc_rating": "C",
        },
        {
            "customer_id": "C2",
            "segment": "SME",
            "acquisition_date": "2019-05-02",
            "contract_type": "fixed_2yr",
            "epc_rating": "E",
        },
        {
            "customer_id": _LATE,
            "segment": "resi",
            "acquisition_date": "2023-02-01",
            "contract_type": "fixed_1yr",
            "epc_rating": "D",
        },
    ]


#: Records settle on the LAST day of each month, not a mid-month day. This is a
#: property the controls depend on rather than a cosmetic choice: `covers_full_year`
#: asks whether the run observed a settlement at or after 31-Dec, so a fixture
#: settling on the 14th would read every year as partial and the flag's vacuity
#: guard could never fire. The real book settles half-hourly and does reach 31-Dec.
_MONTH_END = {
    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
}


def _records(include_late: bool = True) -> list[dict]:
    """Monthly settled records, 2019-2024, with a year-2 step change on C1 so the
    yoy bill-shock signal actually fires — a book in which no shock ever triggers
    gives every account the same churn probability and makes half of these controls
    unobservable."""
    records: list[dict] = []
    plan = [("C1", 120.0, "2019"), ("C2", 300.0, "2019")]
    if include_late:
        plan.append((_LATE, 90.0, "2023"))
    for customer_id, base, first_year in plan:
        for year in range(int(first_year), 2025):
            for month in range(1, 13):
                shock = 1.6 if (customer_id == "C1" and year >= 2020) else 1.0
                revenue = round(base * shock * (1 + 0.02 * (year - 2019)), 2)
                wholesale = round(revenue * 0.62, 2)
                records.append(
                    {
                        "customer_id": customer_id,
                        "settlement_date": f"{year}-{month:02d}-{_MONTH_END[month]:02d}",
                        "settlement_period": 1,
                        "commodity": "electricity",
                        "revenue_gbp": revenue,
                        "wholesale_cost_gbp": wholesale,
                        "margin_gbp": round(revenue - wholesale, 2),
                        "net_margin_gbp": round((revenue - wholesale) * 0.24, 2),
                        "consumption_kwh": 400.0,
                    }
                )
    return records


@pytest.fixture()
def series() -> dict:
    return build_three_horizon_clv_snapshots(
        _records(), _customers(), PRICE_DIFFERENTIAL_PCT
    )


# ---------------------------------------------------------------------------
# Vacuity guards. Every control below is a statement about a population; if the
# population were empty they would all pass for free, which is the FAIL-OPEN
# pattern R15 names.
# ---------------------------------------------------------------------------


def test_the_fixture_produces_a_multi_year_series_with_accounts_in_it(series):
    years = series["years"]
    assert len(years) >= 5, years.keys()
    assert all(y["accounts"] for y in years.values()), {
        y: len(v["accounts"]) for y, v in years.items()
    }


def test_the_fixture_contains_both_a_real_value_and_a_real_blank(series):
    """Controls 2 and 4 are about blanks and about values. A fixture with only one
    kind cannot fail either of them."""
    values, blanks = 0, 0
    for year in series["years"].values():
        for account in year["accounts"].values():
            for horizon in HORIZONS:
                if account[horizon]["value_gbp"] is None:
                    blanks += 1
                else:
                    values += 1
    assert values > 0 and blanks > 0, (values, blanks)


# ---------------------------------------------------------------------------
# Control 1 — THE BLINDFOLD.
# ---------------------------------------------------------------------------


def _early_years(series: dict) -> dict:
    return {y: v for y, v in series["years"].items() if y < "2023"}


def test_a_customer_acquired_later_does_not_appear_in_an_earlier_snapshot(series):
    for year, snapshot in _early_years(series).items():
        assert _LATE not in snapshot["accounts"], (year, snapshot["accounts"].keys())


def test_adding_a_late_customer_leaves_every_earlier_snapshot_identical():
    """The strong form of the blindfold, and the only one that catches a leak that
    changes an EXISTING account's number rather than adding a row.

    C3 settles from 2023. Its arrival changes the resi cohort and therefore the
    portfolio-cohort horizon of C1 — from 2023 onwards. If a 2021 snapshot moves
    when a 2023 customer is added, year 2021's belief was built with 2023 in it.
    """
    without = build_three_horizon_clv_snapshots(
        _records(include_late=False), _customers(), PRICE_DIFFERENTIAL_PCT
    )
    with_late = build_three_horizon_clv_snapshots(
        _records(include_late=True), _customers(), PRICE_DIFFERENTIAL_PCT
    )
    assert _early_years(without) == _early_years(with_late)


def test_the_late_customer_does_change_a_later_snapshot():
    """The null control for the test above. If C3's arrival moved NOTHING at all, the
    equality assertion would be satisfied by an estimator that ignores its inputs, and
    the blindfold control would be vacuous rather than passing."""
    without = build_three_horizon_clv_snapshots(
        _records(include_late=False), _customers(), PRICE_DIFFERENTIAL_PCT
    )
    with_late = build_three_horizon_clv_snapshots(
        _records(include_late=True), _customers(), PRICE_DIFFERENTIAL_PCT
    )
    assert without["years"]["2024"] != with_late["years"]["2024"]


def test_mutation_a_snapshot_built_from_the_untruncated_book_fails_the_blindfold():
    """PERFORM the leak: build every year's snapshot from the WHOLE record set, which
    is what a caller that forgot the `as_of` bound would get — and it is the natural
    mistake, because `build_customer_value_view` deliberately takes no bound.
    """
    leaky_without = build_three_horizon_clv_snapshots(
        _records(include_late=False),
        _customers(),
        PRICE_DIFFERENTIAL_PCT,
        years=["2021"],
    )
    # The leak: year 2021's "snapshot" computed over records through 2024.
    leaked = build_customer_value_view(
        _records(include_late=True), _customers(), PRICE_DIFFERENTIAL_PCT
    ).three_horizon_clv
    leaky_2021 = {
        account.account_id: {
            h.value: {"value_gbp": account.horizon(h).value_gbp} for h in Horizon
        }
        for account in leaked.accounts
    }
    honest_2021 = {
        acct: {h: {"value_gbp": v[h]["value_gbp"]} for h in HORIZONS}
        for acct, v in leaky_without["years"]["2021"]["accounts"].items()
    }
    assert leaky_2021 != honest_2021, (
        "the mutation did not move the numbers, so the blindfold control it is "
        "aimed at could not have failed on it"
    )


# ---------------------------------------------------------------------------
# Control 2 — A BLANK CARRIES ITS NAMED REASON, AND IS NEVER A ZERO.
# ---------------------------------------------------------------------------


def _blank_reason_violations(series: dict) -> list[tuple]:
    bad = []
    for year, snapshot in series["years"].items():
        for account_id, account in snapshot["accounts"].items():
            for horizon in HORIZONS:
                cell = account[horizon]
                blank = cell["value_gbp"] is None
                reason = cell["reason"]
                if blank and (not reason or reason == BLANK_WITHOUT_REASON):
                    bad.append((year, account_id, horizon, "blank without reason"))
                if not blank and reason is not None:
                    bad.append((year, account_id, horizon, "value carrying a reason"))
    return bad


def test_every_blank_in_the_series_carries_a_named_reason(series):
    assert _blank_reason_violations(series) == []


def test_a_blank_stays_null_and_never_becomes_the_number_zero(series):
    """`0.0` and `None` are different facts about a customer. This asserts the
    stronger thing: no cell in the series is the float zero at all, so a flattening
    bug cannot hide behind an account that genuinely rounds to nothing."""
    zeros = [
        (year, account_id, horizon)
        for year, snapshot in series["years"].items()
        for account_id, account in snapshot["accounts"].items()
        for horizon in HORIZONS
        if account[horizon]["value_gbp"] == 0.0
    ]
    assert zeros == [], zeros


def test_mutation_flattening_blanks_to_zero_reds_the_blank_control(series):
    mutated = copy.deepcopy(series)
    flattened = 0
    for snapshot in mutated["years"].values():
        for account in snapshot["accounts"].values():
            for horizon in HORIZONS:
                if account[horizon]["value_gbp"] is None:
                    account[horizon] = {"value_gbp": 0.0, "reason": None}
                    flattened += 1
    assert flattened > 0, "nothing to flatten -- the mutation is vacuous"
    zeros = [
        1
        for snapshot in mutated["years"].values()
        for account in snapshot["accounts"].values()
        for horizon in HORIZONS
        if account[horizon]["value_gbp"] == 0.0
    ]
    assert zeros, "the zero control would not have fired on the flattened series"


def test_mutation_dropping_the_reason_reds_the_blank_control(series):
    mutated = copy.deepcopy(series)
    dropped = 0
    for snapshot in mutated["years"].values():
        for account in snapshot["accounts"].values():
            for horizon in HORIZONS:
                if account[horizon]["value_gbp"] is None:
                    account[horizon]["reason"] = None
                    dropped += 1
    assert dropped > 0, "no blanks to strip -- the mutation is vacuous"
    assert _blank_reason_violations(mutated) != []


# ---------------------------------------------------------------------------
# Control 3 — THE BASIS TRAVELS, AND THE EMPTY BRANCH FAILS CLOSED.
# ---------------------------------------------------------------------------


def test_the_series_states_the_horizon_and_discount_rate_it_was_built_on(series):
    book = build_customer_value_view(
        _records(), _customers(), PRICE_DIFFERENTIAL_PCT
    ).three_horizon_clv
    assert series["aggregate_horizon"] == book.aggregate_horizon.value
    assert series["discount_rate"] == book.discount_rate


def test_an_empty_book_publishes_no_basis_rather_than_a_fabricated_one():
    """The empty branch, which is where this atom's last fail-open was found. No
    records means no book was built, so naming a horizon here would be naming one
    nothing was computed on."""
    empty = build_three_horizon_clv_snapshots([], _customers(), PRICE_DIFFERENTIAL_PCT)
    assert empty["years"] == {}
    assert empty["aggregate_horizon"] is None
    assert empty["discount_rate"] is None


# ---------------------------------------------------------------------------
# Control 4 — A PARTIAL YEAR SAYS SO.
# ---------------------------------------------------------------------------


def test_the_observation_edge_never_runs_past_its_own_cutoff(series):
    for year, snapshot in series["years"].items():
        assert snapshot["observation_edge"] <= snapshot["cutoff"], (year, snapshot)


def test_a_run_that_stops_mid_year_marks_that_year_as_not_fully_covered():
    partial = [r for r in _records() if r["settlement_date"] <= "2024-06-30"]
    out = build_three_horizon_clv_snapshots(
        partial, _customers(), PRICE_DIFFERENTIAL_PCT
    )
    assert out["years"]["2024"]["covers_full_year"] is False
    assert out["years"]["2024"]["observation_edge"] == "2024-06-30"
    # ...and the vacuity guard: a year the run DID reach reads the other way, so the
    # flag is not simply False everywhere.
    assert out["years"]["2023"]["covers_full_year"] is True


# ---------------------------------------------------------------------------
# Control 5 — THE SERIES IS THE ESTIMATOR, NOT A SECOND IMPLEMENTATION OF IT.
# ---------------------------------------------------------------------------


def test_the_final_full_year_snapshot_equals_the_end_of_run_table(series):
    """The identity that makes this a SNAPSHOT of EP1 rather than a lookalike. The
    fixture's records stop inside 2024, so the 2024 snapshot's window is the whole
    record set — its numbers must be bit-identical to the table the run publishes.
    A re-derivation would drift here and nowhere else.
    """
    book = build_customer_value_view(
        _records(), _customers(), PRICE_DIFFERENTIAL_PCT
    ).three_horizon_clv
    end_of_run = {
        account.account_id: {
            h.value: account.horizon(h).value_gbp for h in Horizon
        }
        for account in book.accounts
    }
    snapshot = {
        account_id: {h: cell[h]["value_gbp"] for h in HORIZONS}
        for account_id, cell in series["years"]["2024"]["accounts"].items()
    }
    assert snapshot == end_of_run
