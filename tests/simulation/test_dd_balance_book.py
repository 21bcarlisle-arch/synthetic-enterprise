"""Closed-loop tests for DD2 (atom DD_seasonal_cashflow_physics) --
simulation/dd_balance_book.py: the per-customer level-DD seasonal
credit/debit balance and the portfolio held-credit LIABILITY it aggregates to.
"""
from __future__ import annotations

from simulation.dd_balance_book import (
    build_dd_balance_book,
    BalancePoint,
    _SAMPLE_TRAJECTORY_CUSTOMERS,
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
    """12*N monthly bills for one customer. `monthly_amounts` is a flat list,
    one per consecutive month."""
    out = []
    y, m = start_year, 1
    for amt in monthly_amounts:
        # last day of month is unimportant to the logic; use day 28 for safety
        out.append(_bill(cid, f"{y:04d}-{m:02d}-28", amt, segment=segment))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def _pick_ids(n, want_dd=True):
    """Real resi customer ids whose payment_method resolves to direct_debit
    (or standard_credit / non-DD when want_dd=False) -- for resi the method is
    ARCHETYPE-driven off the id, not the segment, so the fixture must select
    ids by their actual resolved method (mirrors dd_collection_book's own gate)."""
    from simulation.arrears_engine import payment_method

    ids = []
    i = 0
    while len(ids) < n and i < 5000:
        cid = f"C{i}"
        is_dd = payment_method("resi", 90.0, cid, "electricity") == "direct_debit"
        if is_dd == want_dd:
            ids.append(cid)
        i += 1
    assert len(ids) == n, "could not find enough ids of the requested method"
    return ids


# The DD balance book keys everything by customer_id, so a single fixed DD id
# is enough for the single-customer physics tests below.
_DD_ID = _pick_ids(1, want_dd=True)[0]


# ---- seasonal physics ------------------------------------------------------

def test_summer_credit_builds_winter_draws_down():
    """A perfectly seasonal customer whose annual spend equals its level DD
    ends a full year near zero, but PEAKS in credit mid-year (summer build)."""
    # Level DD in year 0 = first bill. Make month 1 (Jan) the standing DD and
    # give a summer trough of consumption so credit accrues, winter spike so it
    # draws back. Sum over the year == 12 * first bill so it returns ~level.
    jan = 100.0
    # 100,100 (Jan/Feb) then a summer dip to 40 for 6 months then winter 160.
    amounts = [jan, jan, 40, 40, 40, 40, 40, 40, 160, 160, 160, 160]
    bills = _monthly_bills(_DD_ID, amounts)
    book = build_dd_balance_book(bills)
    pts = book.trajectories[_DD_ID]
    balances = [p.balance_gbp for p in pts]
    # Credit builds during the summer dip (collect 100, consume 40 -> +60/mo).
    assert max(balances) > 0, "seasonal credit should build during summer"
    # ... and is drawn back down by the winter spike (consume 160 > collect 100).
    assert balances[-1] < max(balances), "winter should draw the credit down"


def test_balance_is_cumulative_collected_minus_consumed():
    amounts = [80.0, 50.0, 50.0]  # standing DD (year0) = 80 (first bill)
    bills = _monthly_bills(_DD_ID, amounts)
    book = build_dd_balance_book(bills)
    pts = book.trajectories[_DD_ID]
    # month1: 80-80=0 ; month2: +80-50=+30 ; month3: +80-50=+30 -> 60
    assert pts[0].balance_gbp == 0.0
    assert pts[1].balance_gbp == 30.0
    assert pts[2].balance_gbp == 60.0


def test_held_credit_is_positive_balance_only():
    """A customer in DEBIT (consumes more than collected) contributes to the
    portfolio balance but NOT to the held-credit liability (which is money OWED
    BACK -- positive balances only)."""
    # Standing DD (year0) = 50 (first bill), then consume 200/mo -> deep debit.
    amounts = [50.0, 200.0, 200.0]
    bills = _monthly_bills(_DD_ID, amounts)
    book = build_dd_balance_book(bills)
    s = book.summary()
    assert s["portfolio_final_balance_gbp"] < 0, "customer should be in debit"
    assert s["portfolio_final_held_credit_gbp"] == 0.0, (
        "a customer in debit holds no credit owed back"
    )


# ---- population gate -------------------------------------------------------

def test_non_direct_debit_customers_excluded():
    dd_id = _pick_ids(1, want_dd=True)[0]
    nondd_id = _pick_ids(1, want_dd=False)[0]
    # A non-DD resi customer AND an SME (bacs) -- both must be excluded.
    dd_bills = _monthly_bills(dd_id, [90.0] * 12)
    nondd_resi = _monthly_bills(nondd_id, [90.0] * 12)
    sme_bills = _monthly_bills("SME1", [90.0] * 12, segment="sme")
    book = build_dd_balance_book(dd_bills + nondd_resi + sme_bills)
    assert dd_id in book.trajectories
    assert nondd_id not in book.trajectories, "non-DD resi customer must not carry a DD balance"
    assert "SME1" not in book.trajectories, "SME (bacs) customer must not carry a DD balance"


# ---- determinism / idempotency (C-S2) --------------------------------------

def test_deterministic_and_order_insensitive():
    amounts = [90.0, 40.0, 40.0, 160.0, 90.0, 90.0]
    bills = _monthly_bills(_DD_ID, amounts)
    a = build_dd_balance_book(bills).serialise()
    b = build_dd_balance_book(list(reversed(bills))).serialise()
    assert a == b, "book must be a pure function of the bill SET, order-insensitive"


def test_replay_reproduces_identical_book():
    bills = _monthly_bills(_DD_ID, [90.0] * 24)
    assert build_dd_balance_book(bills).serialise() == build_dd_balance_book(bills).serialise()


# ---- year-on-year DD reset consistency with DD4a ---------------------------

def test_standing_dd_resets_from_prior_year_actual():
    """Year 1's standing level DD is the DD4a recommendation off year 0's actual
    -- the same chain dd_review_runner walks (mutual consistency)."""
    from company.billing.dd_review import _recommended_monthly
    # Year 0: first bill 100, rest 100 -> actual 1200 -> recommended 100.
    # Year 1: all 200 -> the collected each month in year1 should be the year0
    # recommendation, i.e. _recommended_monthly(1200) == 100, NOT 200.
    y0 = [100.0] * 12
    y1 = [200.0] * 12
    bills = _monthly_bills(_DD_ID, y0 + y1)
    book = build_dd_balance_book(bills)
    pts = book.trajectories[_DD_ID]
    expected_y1_dd = _recommended_monthly(sum(y0))
    for p in pts[12:24]:
        assert p.collected_gbp == round(expected_y1_dd, 2)


# ---- serialise shape -------------------------------------------------------

def test_serialise_shape_and_sample_cap():
    ids = _pick_ids(_SAMPLE_TRAJECTORY_CUSTOMERS + 4, want_dd=True)
    bills = []
    for cid in ids:
        bills += _monthly_bills(cid, [90.0] * 12)
    out = build_dd_balance_book(bills).serialise()
    assert set(out) == {
        "summary", "basis", "monthly_held_credit_series", "sample_trajectories",
    }
    assert len(out["sample_trajectories"]) == _SAMPLE_TRAJECTORY_CUSTOMERS, (
        "sample trajectories must be capped for the business surface"
    )
    s = out["summary"]
    for k in (
        "peak_held_credit_gbp", "peak_month", "trough_held_credit_gbp",
        "portfolio_final_held_credit_gbp", "n_customers", "n_ever_in_credit",
    ):
        assert k in s


def test_empty_bills_safe():
    book = build_dd_balance_book([])
    s = book.summary()
    assert s["n_customers"] == 0
    assert s["peak_held_credit_gbp"] == 0.0
    assert s["peak_month"] is None
    assert book.serialise()["monthly_held_credit_series"] == []


# ---- R15-style: the held-credit tell cannot silently read zero -------------

def test_held_credit_liability_is_actually_measured_not_fail_open():
    """Mutation guard: a customer who is genuinely IN CREDIT must move the
    portfolio held-credit liability off zero. If build_dd_balance_book ever
    fails open (drops the population, forces held credit to 0), this reds."""
    # Standing DD (year0) = 100, then a long summer of low consumption -> large
    # sustained credit that cannot round to zero.
    amounts = [100.0] + [20.0] * 8
    bills = _monthly_bills(_DD_ID, amounts)
    s = build_dd_balance_book(bills).summary()
    assert s["peak_held_credit_gbp"] > 100.0, (
        "a sustained-credit customer must register real held credit"
    )
    assert s["n_ever_in_credit"] == 1


# ---------------------------------------------------------------------------
# 2026-08-03 -- DD2 residual: the COLLECTION-OUTCOME overlay.
#
# Before this, the balance assumed every instructed level DD was banked. On the
# real 2016-2025 run 26 of 751 DD collections come back `failed` (ARUDD), so the
# held-credit LIABILITY was computed from money that never left the customer's
# bank. These tests hold the overlay to R15 BOTH WAYS: a failure must MOVE the
# liability (no fail-open), and an outcome that has not arrived must NOT be
# recoded as a failure (no fail-closed-on-silence artefact).
# ---------------------------------------------------------------------------
import math

import pytest

from simulation.dd_balance_book import (
    OUTCOME_ASSUMED,
    OUTCOME_COLLECTED,
    OUTCOME_FAILED,
    collection_outcomes_from_attempts,
)


def _attempt(cid, day, amount, outcome="collected"):
    return {
        "customer_id": cid,
        "attempt_date": day,
        "amount_gbp": amount,
        "outcome": outcome,
        "failure_reason": "" if outcome == "collected" else "ARUDD",
    }


def _summer_winter(n_years=1):
    """A seasonal shape: cheap summer, expensive winter, so a level DD genuinely
    builds credit through the warm months."""
    year = [130.0, 120.0, 100.0, 70.0, 50.0, 40.0, 40.0, 45.0, 60.0, 85.0, 110.0, 130.0]
    return year * n_years


def test_failed_collection_reduces_held_credit_and_is_labelled():
    """FAIL-OPEN guard: money instructed but never banked is NOT held credit."""
    bills = _monthly_bills(_DD_ID, _summer_winter())
    all_collected = build_dd_balance_book(bills)
    # Fail the June collection -- deep in the summer credit build.
    overlay = {(_DD_ID, "2016-06"): OUTCOME_FAILED}
    with_failure = build_dd_balance_book(bills, collection_outcomes=overlay)

    peak_all = all_collected.summary()["peak_held_credit_gbp"]
    peak_fail = with_failure.summary()["peak_held_credit_gbp"]
    assert peak_all > 0, "fixture must actually build credit or the test proves nothing"
    assert peak_fail < peak_all, (
        "a failed collection must LOWER the held-credit liability -- counting "
        "money that never reached the bank is the fail-open this closes"
    )

    june = [p for p in with_failure.trajectories[_DD_ID] if p.month == "2016-06"][0]
    assert june.collection_outcome == OUTCOME_FAILED
    assert june.banked_gbp == 0.0, "a failed collection banks nothing"
    assert june.collected_gbp > 0.0, (
        "the INSTRUCTED standing amount is unchanged by a bank failure -- DD1's "
        "level-fixed invariant reads this field"
    )
    s = with_failure.summary()
    assert s["n_failed_collections"] == 1
    assert s["uncollected_level_dd_gbp"] == june.collected_gbp


def test_unarrived_outcome_is_assumed_not_failed():
    """FAIL-CLOSED-ON-SILENCE guard (C-S1): an outcome that has not arrived is
    not a failure. Silence must leave the instructed treatment standing, or the
    liability would collapse to nothing the moment the attempt stream lagged."""
    bills = _monthly_bills(_DD_ID, _summer_winter())
    no_overlay = build_dd_balance_book(bills)
    all_known = build_dd_balance_book(
        bills,
        collection_outcomes={
            (_DD_ID, p.month): OUTCOME_COLLECTED for p in no_overlay.trajectories[_DD_ID]
        },
    )
    assert no_overlay.summary()["peak_held_credit_gbp"] == \
        all_known.summary()["peak_held_credit_gbp"], (
        "an absent outcome must behave exactly like a known success"
    )
    assert all(
        p.collection_outcome == OUTCOME_ASSUMED for p in no_overlay.trajectories[_DD_ID]
    )
    assert no_overlay.summary()["n_collections_with_known_outcome"] == 0
    assert all_known.summary()["n_collections_with_known_outcome"] == 12
    assert no_overlay.summary()["n_failed_collections"] == 0


def test_outcome_arrival_order_does_not_change_the_book():
    """C-S1 event-arrival tolerance + C-S2 replay: outcomes may arrive singly,
    late or out of order without changing the answer."""
    bills = _monthly_bills(_DD_ID, _summer_winter())
    full = {(_DD_ID, "2016-03"): OUTCOME_FAILED, (_DD_ID, "2016-09"): OUTCOME_FAILED}
    reversed_arrival = dict(sorted(full.items(), reverse=True))
    a = build_dd_balance_book(bills, collection_outcomes=full).summary()
    b = build_dd_balance_book(bills, collection_outcomes=reversed_arrival).summary()
    assert a == b, "outcome arrival ORDER must not change the book (C-S1/C-S2)"


def test_level_fixed_invariant_survives_a_failed_collection():
    """DD1's consumer contract: a bank failure must not make a level DD stop
    being level. The instructed amount is what DD1 reads."""
    from simulation.dd_level_collection_book import build_dd_level_collection_book

    bills = _monthly_bills(_DD_ID, _summer_winter())
    book = build_dd_balance_book(
        bills, collection_outcomes={(_DD_ID, "2016-06"): OUTCOME_FAILED}
    )
    lcb = build_dd_level_collection_book(book)
    assert lcb.summary()["all_schedules_level_fixed"] is True


def test_non_finite_bill_amount_is_rejected_not_absorbed():
    """R15 fail-open: NaN is comparison-blind (`nan > 0` is False), so a NaN
    bill would silently drop that customer out of the held-credit aggregate and
    leave a plausible, wrong liability. Reject FIRST, never coerce."""
    for bad in (float("nan"), float("inf"), float("-inf")):
        bills = _monthly_bills(_DD_ID, [90.0] * 6)
        bills[3]["total_amount_gbp"] = bad
        # Match the guard's OWN message. Without this the test would pass for
        # the WRONG REASON: with the finiteness check removed, a NaN still
        # blows up several frames later inside dd_review._recommended_monthly
        # (`round(nan)` raises ValueError too), so a bare `pytest.raises(
        # ValueError)` proves nothing about THIS module's guard.
        with pytest.raises(ValueError, match="must be finite"):
            build_dd_balance_book(bills)
    # ...and the reason it matters, stated as an executable fact rather than a
    # comment: this is the comparison blindness the finiteness check pre-empts.
    assert not (float("nan") > 0)
    assert math.isnan(float("nan") - 1.0)


def test_outcome_join_matches_bills_and_flags_a_slipped_walk():
    """The join between bills and Bacs attempts is positional; the amount on
    each side is an INDEPENDENT cross-check of it (two separate structures). A
    slipped walk must RAISE, never silently attribute one month's failure to
    another."""
    bills = _monthly_bills(_DD_ID, [90.0, 91.0, 92.0])
    attempts = [
        _attempt(_DD_ID, "2016-02-14", 90.0),
        _attempt(_DD_ID, "2016-03-14", 91.0, outcome="failed"),
        _attempt(_DD_ID, "2016-04-14", 92.0),
    ]
    overlay = collection_outcomes_from_attempts(bills, attempts)
    assert overlay == {
        (_DD_ID, "2016-01"): OUTCOME_COLLECTED,
        (_DD_ID, "2016-02"): OUTCOME_FAILED,
        (_DD_ID, "2016-03"): OUTCOME_COLLECTED,
    }

    slipped = [attempts[0], _attempt(_DD_ID, "2016-03-14", 999.99, outcome="failed")]
    with pytest.raises(ValueError, match="unsound"):
        collection_outcomes_from_attempts(bills, slipped)


def test_unknown_outcome_string_is_not_read_as_collected():
    """FAIL-CLOSED: only the literal success value banks the money. A renamed or
    corrupted outcome must not read as 'collected'."""
    bills = _monthly_bills(_DD_ID, [90.0])
    overlay = collection_outcomes_from_attempts(
        bills, [_attempt(_DD_ID, "2016-02-14", 90.0, outcome="C0LLECTED")]
    )
    assert overlay == {(_DD_ID, "2016-01"): OUTCOME_FAILED}


def test_short_attempt_stream_leaves_the_tail_assumed():
    """C-S1: outcomes still in flight. The covered months resolve; the tail
    stays `assumed` rather than being invented either way."""
    bills = _monthly_bills(_DD_ID, [90.0, 90.0, 90.0])
    overlay = collection_outcomes_from_attempts(
        bills, [_attempt(_DD_ID, "2016-02-14", 90.0, outcome="failed")]
    )
    assert overlay == {(_DD_ID, "2016-01"): OUTCOME_FAILED}
    book = build_dd_balance_book(bills, collection_outcomes=overlay)
    outcomes = [p.collection_outcome for p in book.trajectories[_DD_ID]]
    assert outcomes == [OUTCOME_FAILED, OUTCOME_ASSUMED, OUTCOME_ASSUMED]


def test_non_dd_customers_never_enter_the_overlay():
    """The overlay inherits the SAME population gate as the book itself."""
    non_dd = _pick_ids(1, want_dd=False)[0]
    bills = _monthly_bills(non_dd, [90.0, 90.0])
    assert collection_outcomes_from_attempts(
        bills, [_attempt(non_dd, "2016-02-14", 90.0, outcome="failed")]
    ) == {}


def test_held_credit_figures_carry_their_clock():
    """R14: no financial figure without its basis. The held-credit liability is
    billed-clock consumption against banked-clock collections -- and an
    unlabelled liability is a defect, not a formatting choice."""
    bills = _monthly_bills(_DD_ID, _summer_winter())
    out = build_dd_balance_book(bills).serialise()
    basis = out["basis"]
    for key in ("peak_held_credit_gbp", "portfolio_final_held_credit_gbp",
                "held_credit_gbp", "uncollected_level_dd_gbp"):
        assert key in basis, f"{key} is published without a clock"
        entry = basis[key]
        assert entry.get("clock"), f"{key} basis has no clock"
        assert "provisional" in entry
        assert entry.get("note"), f"{key} basis has no note"
    # The clock must actually NAME the banked half -- a basis label that does
    # not mention what changed is decoration, not a passport.
    assert "banked" in basis["peak_held_credit_gbp"]["clock"]
    assert "banked" in basis["peak_held_credit_gbp"]["note"]
