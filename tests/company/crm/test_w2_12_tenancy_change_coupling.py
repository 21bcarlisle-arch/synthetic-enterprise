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

    def test_company_module_does_not_import_the_simulation(self):
        """Epistemic wall, structurally: the company module must not reach into
        simulation internals to get its answer."""
        import company.crm.change_of_tenancy_register as mod

        source = open(mod.__file__).read()
        assert "import simulation" not in source
        assert "from simulation" not in source


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


class TestTenancyChangeCoupling:
    def test_one_change_yields_two_deemed_legs(self):
        """The director's 'TWO deemed-rate entries' — the void occupier account
        and the new occupant's day-1 deemed contract."""
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        assert change.deemed_legs() == [DeemedLeg.VOID_OCCUPIER]
        c.observe_move_in("SP-1", "electricity", MOVE_IN)
        assert change.deemed_legs() == [DeemedLeg.VOID_OCCUPIER, DeemedLeg.NEW_OCCUPANT]
        assert change.is_complete

    def test_the_two_legs_are_one_change_not_two(self):
        c = TenancyChangeCoupler()
        c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        c.observe_move_in("SP-1", "electricity", MOVE_IN)
        assert len(c.all_changes()) == 1, "the join is the whole point of the atom"

    def test_deemed_leg_start_dates(self):
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        c.observe_move_in("SP-1", "electricity", MOVE_IN)
        assert change.deemed_start(DeemedLeg.VOID_OCCUPIER) == MOVE_OUT
        assert change.deemed_start(DeemedLeg.NEW_OCCUPANT) == MOVE_IN

    # -- C-S1: singly, late, out of order, duplicated ------------------

    def test_c_s1_a_void_property_is_a_normal_state_not_an_error(self):
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        assert change.is_void
        assert not change.is_complete
        assert c.void_properties(AS_OF) == [change]
        assert change.void_days(AS_OF) == 31

    def test_c_s1_move_in_observed_first_is_the_ofgem_occupier_case(self):
        """A customer who registers only after moving in produces MOVE_IN first.
        That is Ofgem's occupier case, not a malformed stream."""
        c = TenancyChangeCoupler()
        change = c.observe_move_in("SP-1", "electricity", MOVE_IN)
        assert change.has_entry and not change.has_exit
        assert change.void_days(AS_OF) is None, "we cannot know when a void we never saw began"

    def test_c_s1_out_of_order_legs_still_join_into_one_change(self):
        c = TenancyChangeCoupler()
        c.observe_move_in("SP-1", "electricity", MOVE_IN)
        c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        assert len(c.all_changes()) == 1
        assert c.all_changes()[0].is_complete

    def test_c_s2_a_replayed_event_id_is_idempotent(self):
        c = TenancyChangeCoupler()
        c.observe_move_out("SP-1", "electricity", MOVE_OUT, event_id="EV-1")
        c.observe_move_out("SP-1", "electricity", MOVE_OUT, event_id="EV-1")
        assert len(c.all_changes()) == 1

    def test_r15_mutation_without_event_ids_a_duplicate_would_double_count(self):
        """MUTATION showing the idempotency key is load-bearing, not decorative:
        drop the event id and the same physical event opens a second change."""
        c = TenancyChangeCoupler()
        c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        assert len(c.all_changes()) == 2

    def test_successive_tenancies_at_one_property_are_distinct_changes(self):
        c = TenancyChangeCoupler()
        c.observe_move_out("SP-1", "electricity", MOVE_OUT, event_id="E1")
        c.observe_move_in("SP-1", "electricity", MOVE_IN, event_id="E2")
        c.observe_move_out("SP-1", "electricity", dt.date(2025, 3, 1), event_id="E3")
        assert len(c.all_changes()) == 2

    def test_fuel_agnostic_the_same_premise_couples_per_fuel(self):
        """Portability constraint: keyed by (supply point, fuel), never MPAN."""
        c = TenancyChangeCoupler()
        c.observe_move_out("SP-1", "electricity", MOVE_OUT, event_id="E1")
        c.observe_move_out("SP-1", "gas", MOVE_OUT, event_id="E2")
        assert len(c.all_changes()) == 2

    # -- fan-out into the register that already exists ------------------

    def test_move_out_raises_a_void_period_cot_on_the_existing_register(self):
        """Fold, do not duplicate: the coupler drives the register that exists."""
        register = ChangeOfTenancyRegister()
        c = TenancyChangeCoupler(register=register)
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        assert change.cot_id is not None
        assert register.by_type(CoTType.VOID_PERIOD)[0].cot_id == change.cot_id

    def test_move_in_with_an_account_takes_supply_on_the_register(self):
        register = ChangeOfTenancyRegister()
        c = TenancyChangeCoupler(register=register)
        c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        change = c.observe_move_in("SP-1", "electricity", MOVE_IN, account_id="ACC-2")
        record = register.history_for_mpan("SP-1")[0]
        assert record.status is CoTStatus.SUPPLY_TAKEN
        assert record.account_id == "ACC-2"

    def test_a_lost_acquisition_declines_supply_on_the_register(self):
        register = ChangeOfTenancyRegister()
        c = TenancyChangeCoupler(register=register)
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        c.observe_move_in("SP-1", "electricity", MOVE_IN, account_id="ACC-2")
        c.record_acquisition_outcome(change.change_id, won=False)
        assert register.history_for_mpan("SP-1")[0].status is CoTStatus.SUPPLY_DECLINED

    def test_the_coupler_works_without_a_register(self):
        """The join must not REQUIRE the register — no fail-silent dependency."""
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT)
        assert change.cot_id is None
        assert change.is_void

    # -- double jeopardy + acquisition value ---------------------------

    def test_double_jeopardy_is_a_shortfall_plus_a_deemed_leg(self):
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT, exit_balance_gbp=240.0)
        c.observe_move_in("SP-1", "electricity", MOVE_IN)
        assert not change.is_double_jeopardy, "pending is not yet a loss"
        c.record_exit_outcome(change.change_id, ExitOutcome.UNPAID, dt.date(2024, 5, 1))
        assert change.is_double_jeopardy
        assert change.exit_shortfall_gbp == 240.0

    def test_a_paid_exit_is_not_double_jeopardy(self):
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT, exit_balance_gbp=240.0)
        c.record_exit_outcome(
            change.change_id, ExitOutcome.PAID_ON_TIME, dt.date(2024, 5, 1), recovered_gbp=240.0
        )
        assert not change.is_double_jeopardy
        assert change.exit_shortfall_gbp == 0.0

    def test_exposure_and_shortfall_are_never_conflated(self):
        """An unresolved exit is neither a loss nor a settlement. Booking it as
        either is the defect; they are reported on separate lines."""
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT, exit_balance_gbp=240.0)
        assert change.exit_exposure_gbp == 240.0
        assert change.exit_shortfall_gbp == 0.0
        c.record_exit_outcome(change.change_id, ExitOutcome.UNPAID, dt.date(2024, 5, 1))
        assert change.exit_exposure_gbp == 0.0
        assert change.exit_shortfall_gbp == 240.0

    def test_the_prime_acquisition_moment_carries_landed_clv(self):
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT, exit_balance_gbp=100.0)
        c.observe_move_in("SP-1", "electricity", MOVE_IN, account_id="ACC-2")
        c.record_acquisition_outcome(change.change_id, won=True, occupant_clv_gbp=900.0)
        c.record_exit_outcome(change.change_id, ExitOutcome.UNPAID, dt.date(2024, 5, 1))
        assert change.net_value_gbp == 800.0

    def test_a_lost_acquisition_carries_no_clv_only_the_loss(self):
        c = TenancyChangeCoupler()
        change = c.observe_move_out("SP-1", "electricity", MOVE_OUT, exit_balance_gbp=100.0)
        c.record_acquisition_outcome(change.change_id, won=False, occupant_clv_gbp=900.0)
        c.record_exit_outcome(change.change_id, ExitOutcome.UNPAID, dt.date(2024, 5, 1))
        assert change.occupant_clv_gbp == 0.0
        assert change.net_value_gbp == -100.0

    def test_awaiting_exit_outcome_lists_only_exposed_unanswered_exits(self):
        c = TenancyChangeCoupler()
        exposed = c.observe_move_out("SP-1", "electricity", MOVE_OUT, exit_balance_gbp=240.0)
        c.observe_move_out("SP-2", "electricity", MOVE_OUT, exit_balance_gbp=0.0)
        assert [x.change_id for x in c.awaiting_exit_outcome()] == [exposed.change_id]


class TestDoubleJeopardySummary:
    def _populated(self):
        c = TenancyChangeCoupler()
        won = c.observe_move_out("SP-1", "electricity", MOVE_OUT, exit_balance_gbp=240.0)
        c.observe_move_in("SP-1", "electricity", MOVE_IN, account_id="ACC-2")
        c.record_exit_outcome(won.change_id, ExitOutcome.UNPAID, dt.date(2024, 5, 1))
        c.record_acquisition_outcome(won.change_id, won=True, occupant_clv_gbp=900.0)
        c.observe_move_out("SP-2", "electricity", MOVE_OUT, exit_balance_gbp=60.0)
        return c

    def test_summary_reports_the_frame(self):
        s = self._populated().double_jeopardy_summary(AS_OF)
        assert s["tenancy_changes"] == 2
        assert s["complete"] == 1
        assert s["void_now"] == 1
        assert s["deemed_legs"] == 3
        assert s["double_jeopardy"] == 1
        assert s["acquisitions_won"] == 1

    def test_summary_keeps_unanswered_exposure_off_the_loss_line(self):
        s = self._populated().double_jeopardy_summary(AS_OF)
        assert s["exit_shortfall_gbp"] == 240.0, "only the observed loss"
        assert s["exit_exposure_gbp"] == 60.0, "the unanswered exit, reported separately"

    def test_net_value_nets_landed_clv_against_observed_loss(self):
        s = self._populated().double_jeopardy_summary(AS_OF)
        assert s["net_value_gbp"] == 660.0

    def test_r15_fail_open_an_empty_coupler_summarises_to_zero_not_to_silence(self):
        """FAIL-OPEN: an empty book must report explicit zeros/None, never a
        shape a consumer would read as 'nothing wrong'."""
        s = TenancyChangeCoupler().double_jeopardy_summary(AS_OF)
        assert s["tenancy_changes"] == 0
        assert s["mean_void_days"] is None
        assert s["exit_shortfall_gbp"] == 0.0
        assert s["exit_exposure_gbp"] == 0.0

    def test_mean_void_days_is_measured_from_real_dates(self):
        s = self._populated().double_jeopardy_summary(AS_OF)
        assert s["mean_void_days"] == 31.0
