"""Closed-loop tests for DD1 (atom DD_seasonal_cashflow_physics) --
simulation/dd_level_collection_book.py: the LEVEL (fixed) DD collection made
first-class, where the standing monthly amount SIZES the collection (not the
bill), landing on the customer's staggered payment day.

R15 both-ways coverage is explicit below: the FAIL-OPEN guard is that a level
collection must be FIXED within a year even though the bills vary (a bill-sized
collection would fail it); the both-ways partner is that a genuine re-estimate
at a year boundary DOES move the fixed amount, and the _windows_fixed guard
itself flips False on a hand-built varying schedule.
"""
from __future__ import annotations

from company.billing.direct_debit import staggered_payment_day
from company.billing.dd_review import _recommended_monthly
from simulation.dd_balance_book import build_dd_balance_book
from simulation.dd_level_collection_book import (
    build_dd_level_collection_book,
    DDLevelCollectionBook,
    LevelCollection,
    _SAMPLE_SCHEDULE_CUSTOMERS,
)


def _bill(cid, period_end, amount, segment="resi", commodity="electricity"):
    return {
        "customer_id": cid,
        "period_end": period_end,
        "total_amount_gbp": amount,
        "segment": segment,
        "commodity": commodity,
    }


def _monthly_bills(cid, monthly_amounts, segment="resi", start_year=2016):
    """12*N monthly bills for one customer, one amount per consecutive month."""
    out = []
    y, m = start_year, 1
    for amt in monthly_amounts:
        out.append(_bill(cid, f"{y:04d}-{m:02d}-28", amt, segment=segment))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def _pick_ids(n, want_dd=True):
    """Real resi customer ids whose payment_method resolves to direct_debit
    (or non-DD when want_dd=False) -- mirrors dd_balance_book's own gate."""
    from simulation.arrears_engine import payment_method

    ids, i = [], 0
    while len(ids) < n and i < 5000:
        cid = f"C{i}"
        is_dd = payment_method("resi", 90.0, cid, "electricity") == "direct_debit"
        if is_dd == want_dd:
            ids.append(cid)
        i += 1
    assert len(ids) == n, "could not find enough ids of the requested method"
    return ids


_DD_ID = _pick_ids(1, want_dd=True)[0]
_NON_DD_ID = _pick_ids(1, want_dd=False)[0]


def _level_book(bills):
    return build_dd_level_collection_book(build_dd_balance_book(bills))


# ---- the standing amount SIZES the collection, not the bill (R15 FAIL-OPEN) --

def test_collection_is_fixed_within_year_though_bills_vary():
    """The defining DD1 property: under a level DD the collection is the SAME
    fixed amount every month even though consumption (the bill) swings
    seasonally. A collection wired to the bill would vary -- this asserts it
    does NOT, and that the underlying bills genuinely differ so the test can
    actually fail."""
    # Seasonal bills: low summer, high winter, 12 months.
    seasonal = [40, 45, 60, 80, 110, 130, 120, 100, 70, 55, 45, 40]
    book = _level_book(_monthly_bills(_DD_ID, seasonal))
    cols = book.schedules[_DD_ID]
    assert len(cols) == 12
    amounts = {round(c.amount_gbp, 2) for c in cols}
    assert len(amounts) == 1, "level collection must be FIXED within the year"
    # And the bills it is decoupled from genuinely vary (guards a degenerate
    # fixture where a fixed collection would be trivially true).
    consumed = {round(c.consumed_gbp, 2) for c in cols}
    assert len(consumed) > 1, "fixture bills must vary or the test is vacuous"
    # The fixed amount is the year-0 standing DD == the first bill (DD2 chain).
    assert round(cols[0].amount_gbp, 2) == 40.0
    assert book.summary()["all_schedules_level_fixed"] is True


def test_re_estimation_moves_the_fixed_amount_between_years():
    """Both-ways partner: the fixed amount is NOT frozen forever -- at the
    12-month boundary the standing DD resets to the prior year's actual/12
    recommendation, so year-2 collections differ from year-1 when spend drifted."""
    # Year 0: first bill 100, other 11 months 200 -> annual 2300.
    # Year 1 standing = _recommended_monthly(2300) != 100.
    y0 = [100] + [200] * 11
    y1 = [150] * 12
    book = _level_book(_monthly_bills(_DD_ID, y0 + y1))
    cols = book.schedules[_DD_ID]
    year0_amt = round(cols[0].amount_gbp, 2)
    year1_amt = round(cols[12].amount_gbp, 2)
    assert year0_amt == 100.0
    assert year1_amt == float(_recommended_monthly(sum(y0)))
    assert year1_amt != year0_amt, "re-estimate must move the fixed amount"
    # Still fixed WITHIN each year.
    assert len({round(c.amount_gbp, 2) for c in cols[:12]}) == 1
    assert len({round(c.amount_gbp, 2) for c in cols[12:24]}) == 1


def test_amount_equals_dd2_collected_by_construction():
    """Consistency contract: every collection amount is IDENTICALLY DD2's
    collected_gbp for that customer-month -- the single-source guarantee that
    DD1/DD2/DD4a cannot drift apart."""
    bills = _monthly_bills(_DD_ID, [50, 60, 90, 120, 80, 55, 50, 60, 90, 120, 80, 55])
    bb = build_dd_balance_book(bills)
    book = build_dd_level_collection_book(bb)
    dd2_collected = [round(p.collected_gbp, 2) for p in bb.trajectories[_DD_ID]]
    dd1_collected = [round(c.amount_gbp, 2) for c in book.schedules[_DD_ID]]
    assert dd1_collected == dd2_collected


# ---- staggered payment day ---------------------------------------------------

def test_collection_lands_on_staggered_payment_day():
    book = _level_book(_monthly_bills(_DD_ID, [70] * 12))
    day = staggered_payment_day(_DD_ID)
    assert 1 <= day <= 28
    for c in book.schedules[_DD_ID]:
        assert c.payment_day == day
        assert int(c.collection_date[8:10]) == day
        # A valid, in-every-month date (<=28), one per billed month.
        assert c.collection_date[:7] in {f"2016-{m:02d}" for m in range(1, 13)}


# ---- population gate (inherited from DD2) ------------------------------------

def test_only_direct_debit_customers_get_a_schedule():
    """A non-DD customer carries no level-DD balance in DD2, so DD1 emits no
    schedule for them -- the gate is inherited, not re-implemented."""
    bills = _monthly_bills(_NON_DD_ID, [70] * 12)
    book = _level_book(bills)
    assert _NON_DD_ID not in book.schedules
    assert book.summary()["n_customers"] == 0


# ---- determinism / idempotence (C-S2) ----------------------------------------

def test_deterministic_idempotent_replay():
    bills = _monthly_bills(_DD_ID, [40, 45, 60, 80, 110, 130, 120, 100, 70, 55, 45, 40])
    a = _level_book(bills).serialise()
    b = _level_book(list(reversed(bills))).serialise()  # order-insensitive input
    assert a == b


def test_empty_book_is_measurable_not_crash():
    book = build_dd_level_collection_book(build_dd_balance_book([]))
    s = book.summary()
    assert s["n_customers"] == 0
    assert s["n_collections"] == 0
    assert s["total_level_collected_gbp"] == 0.0
    assert s["all_schedules_level_fixed"] is True
    assert book.serialise()["sample_schedules"] == {}


# ---- summary + R15 mutation on the _windows_fixed guard itself ---------------

def test_summary_totals_and_count():
    book = _level_book(_monthly_bills(_DD_ID, [70] * 12))
    cols = book.schedules[_DD_ID]
    s = book.summary()
    assert s["n_customers"] == 1
    assert s["n_collections"] == 12
    assert s["total_level_collected_gbp"] == round(sum(c.amount_gbp for c in cols), 2)


def test_windows_fixed_guard_flips_false_on_a_varying_schedule():
    """R15 mutation: the level-fixed flag must actually FIRE. Hand-build a
    schedule whose amounts vary within one year -> the guard reports NOT fixed
    (proves all_schedules_level_fixed is a real check, not fail-open True)."""
    varying = DDLevelCollectionBook(schedules={
        "X": [
            LevelCollection("2016-01-14", 70.0, 14, 40.0),
            LevelCollection("2016-02-14", 95.0, 14, 120.0),  # amount changed mid-year
        ]
    })
    assert varying.summary()["all_schedules_level_fixed"] is False
    # ...and a genuinely fixed one reports True.
    fixed = DDLevelCollectionBook(schedules={
        "X": [
            LevelCollection("2016-01-14", 70.0, 14, 40.0),
            LevelCollection("2016-02-14", 70.0, 14, 120.0),
        ]
    })
    assert fixed.summary()["all_schedules_level_fixed"] is True


def test_sample_schedules_bounded():
    ids = _pick_ids(_SAMPLE_SCHEDULE_CUSTOMERS + 3, want_dd=True)
    bills = []
    for cid in ids:
        bills += _monthly_bills(cid, [70] * 12)
    book = _level_book(bills)
    assert len(book.serialise()["sample_schedules"]) == _SAMPLE_SCHEDULE_CUSTOMERS
