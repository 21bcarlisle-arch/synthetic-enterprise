# ARCHIVED LEGS of tests/company/crm/test_w2_12_tenancy_change_coupling.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/crm/test_w2_12_tenancy_change_coupling.py.
"""W2_12 — change-of-tenancy debt physics, COMPANY side.

Covers the coupling layer (`company.crm.change_of_tenancy_register.TenancyChangeCoupler`)
and the credit-risk exit observation side (`company.billing.account_closure`).

The atom's frame, director-verbatim: *every tenancy change is ONE credit-risk exit
PLUS TWO deemed-rate entries (double jeopardy), and simultaneously the prime
acquisition moment for high-value low-churn customers.*

R15 discipline: every control asserted here is also MUTATION-PROVEN — each guard is
shown FIRING on its own named defect, so a control that silently cannot fail is
caught. The three killer patterns are tested by name: TAUTOLOGY, FAIL-OPEN
(missing/zero/empty/malformed), FAIL-SILENT.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.billing.account_closure import (
    AccountClosureBook,
    ClosureReason,
    ClosureStatus,
    EpistemicWallBreach,
    FinalBillOutcome,
    FinalBillPaymentEvent,
    assert_observable_final_bill_event,
)
from company.crm.change_of_tenancy_register import (
    AcquisitionOutcome,
    ChangeOfTenancyRegister,
    CoTStatus,
    CoTType,
    DeemedLeg,
    ExitOutcome,
    TenancyChangeCoupler,
)

MOVE_OUT = dt.date(2024, 3, 1)
MOVE_IN = dt.date(2024, 3, 21)
AS_OF = dt.date(2024, 4, 1)


def _observable_event(**overrides) -> dict:
    event = {
        "account_id": "ACC-1",
        "resolved_on": "2024-05-01",
        "outcome": "unpaid",
        "billed_gbp": 240.0,
        "recovered_gbp": 0.0,
    }
    event.update(overrides)
    return event


# =====================================================================
# 1. The epistemic wall on the final-bill outcome event.
# =====================================================================


class TestFinalBillWallGuard:
    def test_a_purely_observable_event_passes(self):
        assert assert_observable_final_bill_event(_observable_event()) is not None

    @pytest.mark.parametrize(
        "leaked_key",
        [
            "gone_away_probability",   # the world-side probability itself
            "debt_archetype",          # the hidden household archetype
            "tenure",                  # household truth
            "payment_channel_truth",
            "fuel_poverty_flag",
            "true_switch_intent",
        ],
    )
    def test_r15_mutation_a_leaked_non_observable_field_FIRES_the_guard(self, leaked_key):
        """MUTATION: the world side grows a hidden field and leaks it across the
        wall. The allowlist must FIRE. This is the guard's named defect."""
        event = _observable_event(**{leaked_key: 0.42})
        with pytest.raises(EpistemicWallBreach) as exc:
            assert_observable_final_bill_event(event)
        assert leaked_key in str(exc.value)

    def test_allowlist_not_denylist_an_unknown_future_field_is_rejected(self):
        """A denylist would fail OPEN on a field nobody thought to forbid.
        An invented field name proves the check is an allowlist."""
        with pytest.raises(EpistemicWallBreach):
            assert_observable_final_bill_event(
                _observable_event(some_field_invented_tomorrow=1)
            )

    @pytest.mark.parametrize("empty", [None, {}, [], "", 0])
    def test_r15_fail_open_missing_or_empty_payload_is_a_FAILED_check(self, empty):
        """FAIL-OPEN pattern: a missing/empty/malformed payload must be rejected,
        never waved through as 'nothing wrong found'."""
        with pytest.raises(EpistemicWallBreach):
            assert_observable_final_bill_event(empty)

    @pytest.mark.parametrize(
        "missing", ["account_id", "resolved_on", "outcome", "billed_gbp", "recovered_gbp"]
    )
    def test_a_missing_required_field_is_rejected(self, missing):
        event = _observable_event()
        del event[missing]
        with pytest.raises(EpistemicWallBreach) as exc:
            assert_observable_final_bill_event(event)
        assert missing in str(exc.value)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    @pytest.mark.parametrize("key", ["billed_gbp", "recovered_gbp"])
    def test_r15_nan_blind_guard_non_finite_money_rejected_before_comparison(self, key, bad):
        """NaN compares False against every bound, so a guard that compares first
        fails open. Non-finite must be rejected on its own terms."""
        with pytest.raises(EpistemicWallBreach):
            assert_observable_final_bill_event(_observable_event(**{key: bad}))

    @pytest.mark.parametrize("key", ["billed_gbp", "recovered_gbp"])
    def test_negative_money_rejected(self, key):
        with pytest.raises(EpistemicWallBreach):
            assert_observable_final_bill_event(_observable_event(**{key: -1.0}))

    @pytest.mark.parametrize("key", ["billed_gbp", "recovered_gbp"])
    def test_bool_is_not_a_money_amount(self, key):
        """bool is a subclass of int — a True that slipped in must not read as £1."""
        with pytest.raises(EpistemicWallBreach):
            assert_observable_final_bill_event(_observable_event(**{key: True}))

    def test_unknown_outcome_rejected(self):
        with pytest.raises(EpistemicWallBreach):
            assert_observable_final_bill_event(_observable_event(outcome="probably_fine"))

    def test_zero_money_is_legitimate_not_swallowed(self):
        """Guard against over-rejection: £0 billed is a real, valid exit."""
        assert_observable_final_bill_event(
            _observable_event(billed_gbp=0.0, recovered_gbp=0.0, outcome="paid_on_time")
        )


class TestTypedMessageNotSharedObject:
    def test_company_and_world_outcome_vocabularies_match_by_value(self):
        """The wall is crossed by a typed message, not a shared object. If either
        side grows a value the other lacks, this FIRES — which is the point."""
        from simulation.final_bill_outcome import (
            FinalBillOutcome as WorldOutcome,
        )

        assert {o.value for o in FinalBillOutcome} == {o.value for o in WorldOutcome}

    def test_the_coupler_adds_exactly_one_company_side_state_pending(self):
        """The coupler mirrors every world outcome and adds PENDING — the C-S3
        'we have not been told yet' state, which exists only in front of the
        wall. Any OTHER divergence is a vocabulary drift and fires here."""
        assert {o.value for o in ExitOutcome} - {o.value for o in FinalBillOutcome} == {"pending"}
        assert {o.value for o in FinalBillOutcome} - {o.value for o in ExitOutcome} == set()



# =====================================================================
# 2. The credit-risk exit — observation side.
# =====================================================================


class TestCreditRiskExit:
    def _book_with_closure(self, debt=240.0):
        book = AccountClosureBook()
        book.initiate(
            account_id="ACC-1",
            supply_point_id="SP-1",
            reason=ClosureReason.CHANGE_OF_TENANCY,
            closure_date=dt.date(2024, 3, 1),
            debt_balance_gbp=debt,
        )
        return book

    def test_change_of_tenancy_is_a_first_class_closure_reason(self):
        assert ClosureReason.CHANGE_OF_TENANCY.value == "change_of_tenancy"

    def test_an_unanswered_exit_is_pending_not_paid(self):
        """C-S3: the outcome arrives LATER. 'We have not heard' must never read
        as 'settled' — that is the fail-open that hides all the bad debt."""
        book = self._book_with_closure()
        awaiting = book.awaiting_final_bill_outcome(AS_OF)
        assert [r.account_id for r in awaiting] == ["ACC-1"]
        assert awaiting[0].final_bill_outcome is None
        assert awaiting[0].final_bill_shortfall_gbp == 0.0

    def test_pending_stays_pending_past_the_due_date(self):
        """An answer that has not arrived is not an answer, however late."""
        book = self._book_with_closure()
        assert book.awaiting_final_bill_outcome(dt.date(2030, 1, 1))

    def test_exit_debt_summary_separates_exposure_from_observed_loss(self):
        book = self._book_with_closure()
        book.initiate(
            account_id="ACC-2",
            supply_point_id="SP-2",
            reason=ClosureReason.CHANGE_OF_TENANCY,
            closure_date=dt.date(2024, 3, 1),
            debt_balance_gbp=60.0,
        )
        book.record_final_bill_outcome(_observable_event())
        summary = book.exit_debt_summary(AS_OF)
        assert summary["resolved"] == 1
        assert summary["awaiting_outcome"] == 1
        assert summary["shortfall_gbp"] == 240.0, "observed loss only"
        assert summary["exposed_gbp"] == 60.0, "unanswered exit, reported separately"
        assert summary["unpaid"] == 1

    def test_r15_fail_open_an_empty_closure_book_summarises_to_explicit_zeros(self):
        summary = AccountClosureBook().exit_debt_summary(AS_OF)
        assert summary["resolved"] == 0
        assert summary["awaiting_outcome"] == 0
        assert summary["exposed_gbp"] == 0.0
        assert summary["shortfall_gbp"] == 0.0

    def test_unpaid_final_bill_refers_to_collections_and_books_the_shortfall(self):
        book = self._book_with_closure()
        updated = book.record_final_bill_outcome(_observable_event())
        assert updated.final_bill_outcome is FinalBillOutcome.UNPAID
        assert updated.status is ClosureStatus.DEBT_REFERRED
        assert updated.final_bill_shortfall_gbp == 240.0
        assert book.awaiting_final_bill_outcome(AS_OF) == []

    def test_partial_payment_books_only_the_unrecovered_part(self):
        book = self._book_with_closure()
        updated = book.record_final_bill_outcome(
            _observable_event(outcome="partially_paid", recovered_gbp=100.0)
        )
        assert updated.status is ClosureStatus.DEBT_REFERRED
        assert updated.final_bill_shortfall_gbp == 140.0

    def test_paid_settles_and_books_no_loss(self):
        book = self._book_with_closure()
        updated = book.record_final_bill_outcome(
            _observable_event(outcome="paid_on_time", recovered_gbp=240.0)
        )
        assert updated.status is ClosureStatus.CLOSED
        assert updated.final_bill_shortfall_gbp == 0.0

    def test_gone_away_is_observed_and_surfaced(self):
        """A supplier genuinely does observe returned post — this is observable,
        unlike the probability behind it."""
        book = self._book_with_closure()
        book.record_final_bill_outcome(_observable_event(gone_away=True))
        assert [r.account_id for r in book.gone_away_closures()] == ["ACC-1"]

    def test_c_s2_replaying_the_same_outcome_event_is_a_no_op(self):
        book = self._book_with_closure()
        first = book.record_final_bill_outcome(_observable_event())
        second = book.record_final_bill_outcome(_observable_event())
        assert first == second
        assert len(book.gone_away_closures()) == 0

    def test_r15_mutation_a_leaked_event_never_reaches_the_book(self):
        """MUTATION: the world side leaks its probability into the outcome event.
        The book must REJECT it, not sanitise and continue."""
        book = self._book_with_closure()
        with pytest.raises(EpistemicWallBreach):
            book.record_final_bill_outcome(
                _observable_event(gone_away_probability=0.31)
            )
        assert book.awaiting_final_bill_outcome(AS_OF), "rejected event must not settle the exit"

    def test_payment_event_shortfall_is_arithmetic_not_assertion(self):
        event = FinalBillPaymentEvent.from_observation(
            _observable_event(outcome="partially_paid", recovered_gbp=90.0)
        )
        assert event.shortfall_gbp == 150.0


# =====================================================================
# 3. The coupling layer — one change, three consequences.
# =====================================================================




