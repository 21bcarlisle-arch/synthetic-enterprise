"""DD1 (2026-07-27, DD_seasonal_cashflow_physics): per-customer STAGGERED
level-DD payment day.

Real level DD collects on each household's own fixed day-of-month (1-28), so a
supplier's collection book is spread across the whole month rather than every
mandate landing on one relative offset from its bill date. Before DD1 the book
had no day-of-month concept at all -- the collection date was the bill's due
date + Bacs lag, identical structure for every customer.

R15 discipline: each behavioural claim is asserted BOTH ways -- it holds on the
real code AND fires on a named mutation (staggering removed). A control that
cannot fail is worse than none.
"""
from datetime import date, timedelta

import pytest

from company.billing.direct_debit import (
    DirectDebitBook,
    _MAX_PAYMENT_DAY,
    _MIN_PAYMENT_DAY,
    next_collection_on_day,
)
from simulation.dd_collection_book import build_dd_collection_book
from simulation.dd_payment_day import staggered_payment_day


# --------------------------------------------------------------------------
# staggered_payment_day: deterministic, in-range, and actually staggering
# --------------------------------------------------------------------------

class TestStaggeredPaymentDay:
    def test_is_within_the_valid_1_to_28_range(self):
        for cid in (f"CUST{i:04d}" for i in range(500)):
            day = staggered_payment_day(cid)
            assert _MIN_PAYMENT_DAY <= day <= _MAX_PAYMENT_DAY

    def test_is_deterministic_across_replays_c_s2(self):
        # C-S2 idempotent replay: same customer id -> same day, every call.
        for cid in ("alice", "bob", "C-000123", "resi-9982"):
            assert staggered_payment_day(cid) == staggered_payment_day(cid)

    def test_draws_from_no_shared_rng_stream(self):
        # Pure function of the id -- importing/calling it must not perturb the
        # global random state (C-S2: a new draw never shifts another's output).
        import random
        random.seed(12345)
        before = [random.random() for _ in range(5)]
        random.seed(12345)
        [staggered_payment_day(f"C{i}") for i in range(50)]
        after = [random.random() for _ in range(5)]
        assert before == after

    def test_actually_staggers_the_book_across_the_month(self):
        # The whole point: a population's payment days spread across many
        # distinct days, not all bunched on one. (Mutation that returns a
        # constant day would collapse this set to size 1 and fire the assert.)
        days = {staggered_payment_day(f"CUST{i:04d}") for i in range(500)}
        assert len(days) >= 20, f"expected the book to spread across the month, got {sorted(days)}"


# --------------------------------------------------------------------------
# next_collection_on_day: snap a due date forward onto the anniversary
# --------------------------------------------------------------------------

class TestNextCollectionOnDay:
    def test_snaps_within_the_same_month_when_day_not_yet_passed(self):
        assert next_collection_on_day("2020-03-05", 15) == "2020-03-15"

    def test_lands_exactly_on_the_day_when_already_on_it(self):
        assert next_collection_on_day("2020-03-15", 15) == "2020-03-15"

    def test_rolls_to_next_month_when_the_day_has_passed(self):
        assert next_collection_on_day("2020-03-20", 15) == "2020-04-15"

    def test_rolls_across_the_year_boundary(self):
        assert next_collection_on_day("2020-12-20", 3) == "2021-01-03"

    def test_never_lands_before_the_due_date(self):
        base = date(2020, 6, 10)
        for day in range(_MIN_PAYMENT_DAY, _MAX_PAYMENT_DAY + 1):
            landed = date.fromisoformat(next_collection_on_day(base.isoformat(), day))
            assert landed >= base
            assert landed.day == day


# --------------------------------------------------------------------------
# create_mandate wiring + backward compatibility
# --------------------------------------------------------------------------

class TestMandateWiring:
    def test_payment_day_sets_the_next_collection_onto_the_anniversary(self):
        b = DirectDebitBook()
        m = b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-05", payment_day=20)
        assert m.payment_day == 20
        assert m.next_collection_date == "2024-01-20"

    def test_legacy_zero_payment_day_keeps_the_rolling_28_day_cycle(self):
        # Backward compatibility: every existing caller passes no payment_day
        # and must see byte-identical behaviour (rolling +28 from setup).
        b = DirectDebitBook()
        m = b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
        assert m.payment_day == 0
        assert m.next_collection_date == "2024-01-29"

    def test_out_of_range_payment_day_is_rejected(self):
        b = DirectDebitBook()
        with pytest.raises(ValueError):
            b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01", payment_day=31)


# --------------------------------------------------------------------------
# LIVE flow (build_dd_collection_book): staggering is real + observable,
# proven BOTH ways (R15)
# --------------------------------------------------------------------------

def _resi_bill(cid, period_end, amount=100.0, segment="resi"):
    return {
        "customer_id": cid, "period_end": period_end, "total_amount_gbp": amount,
        "segment": segment, "commodity": "electricity",
    }


class TestLiveStaggeringBothWays:
    """Two customers with the SAME bills but DIFFERENT staggered days must get
    DIFFERENT observed collection dates -- and removing the snap collapses
    them to the same date (the mutation the control must catch)."""

    # Two ids whose staggered days genuinely differ (precondition asserted
    # in-test so the fixture can never silently degrade to a tautology).
    CID_A = "STAG-A"
    CID_B = "STAG-B"

    def _bills(self):
        # Same bill calendar for both customers.
        return [
            _resi_bill(self.CID_A, "2020-01-31"),
            _resi_bill(self.CID_B, "2020-01-31"),
        ]

    def test_precondition_the_two_customers_have_distinct_days(self):
        assert staggered_payment_day(self.CID_A) != staggered_payment_day(self.CID_B)

    def test_distinct_customers_get_distinct_collection_dates(self, monkeypatch):
        import simulation.dd_collection_book as mod
        monkeypatch.setattr(mod, "payment_method", lambda *a, **k: "direct_debit")
        book = build_dd_collection_book(self._bills(), {})
        at_a = book.attempts_for_customer(self.CID_A)[0]
        at_b = book.attempts_for_customer(self.CID_B)[0]
        # Pin the precondition: a SUCCESSFUL collection's outcome date is a
        # deterministic function of the submission date (no rng lag), so any
        # date difference here is the staggering, not incidental rng noise.
        assert at_a.outcome == "collected" and at_b.outcome == "collected"
        assert at_a.attempt_date != at_b.attempt_date, "staggered payment days must produce distinct collection dates"

    def test_mutation_removing_the_snap_collapses_the_dates(self, monkeypatch):
        # MUTATION (R15): if the collection date is NOT snapped onto the
        # customer's staggered day (identity snap -> both use the raw due
        # date), the two customers land on the SAME date -- proving the test
        # above is actually load-bearing on the staggering, not passing for
        # some incidental reason.
        #
        # THE MUTATION'S TARGET MOVED, 2026-08-10 (KNIFE pass 3, B4's last edge).
        # It used to patch `next_collection_on_day` on the SIM module, which held the
        # name because the world snapped its own collection dates. It no longer does:
        # deciding when to collect is the supplier's, and the name now lives on
        # `company/billing/dd_collections_desk.py`. Re-pointing the patch is what
        # keeps this control aimed at its subject -- patching a name the world no
        # longer has would have made it fail-silent, catching nothing while looking
        # green (`a test isolates the paths it thought of`). The property under test
        # is unchanged: with the snap mutated out, staggering must collapse.
        import simulation.dd_collection_book as mod
        import company.billing.dd_collections_desk as desk_mod
        monkeypatch.setattr(mod, "payment_method", lambda *a, **k: "direct_debit")
        monkeypatch.setattr(desk_mod, "next_collection_on_day", lambda due_iso, day: due_iso)
        book = build_dd_collection_book(self._bills(), {})
        at_a = book.attempts_for_customer(self.CID_A)[0]
        at_b = book.attempts_for_customer(self.CID_B)[0]
        # Same success precondition as the positive test -- with both
        # succeeding, equal submission dates give equal outcome dates.
        assert at_a.outcome == "collected" and at_b.outcome == "collected"
        assert at_a.attempt_date == at_b.attempt_date, "with the snap mutated out, both customers should collapse to one date"
