"""Tests for simulation/bacs_rails.py -- the M2 "rails sim first" step
(THE_VALUE_CYCLE_FRAMING.md, W5_1_banking_payment_rails)."""
import random
from datetime import date

import pytest

from simulation.bacs_rails import (
    BACS_PROCESSING_DAYS, ARUDD_NOTIFICATION_LAG_DAYS, AUDDIS_CONFIRMATION_DAYS,
    ARUDD_REASON_CODES, AUDDIS_REASON_CODES,
    submit_mandate_setup, submit_amendment, submit_collection,
    resolve_submission, resolve_due_submissions, _add_working_days,
)


class TestSubmission:
    def test_collection_starts_pending_no_early_outcome(self):
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        assert sub.status == "pending"
        assert sub.reason_code is None

    def test_collection_expected_outcome_is_three_working_days_later(self):
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        assert sub.expected_outcome_date == date(2020, 6, 1) + __import__("datetime").timedelta(days=BACS_PROCESSING_DAYS)

    def test_mandate_setup_expected_outcome_uses_auddis_window(self):
        sub = submit_mandate_setup("REF2", "C1", date(2020, 6, 1))
        assert sub.expected_outcome_date == date(2020, 6, 1) + __import__("datetime").timedelta(days=AUDDIS_CONFIRMATION_DAYS)

    def test_amendment_expected_outcome_uses_auddis_window(self):
        sub = submit_amendment("REF3", "C1", date(2020, 6, 1))
        assert sub.expected_outcome_date == date(2020, 6, 1) + __import__("datetime").timedelta(days=AUDDIS_CONFIRMATION_DAYS)

    def test_collection_carries_amount(self):
        sub = submit_collection("REF1", "C1", 73.21, date(2020, 6, 1))
        assert sub.amount_gbp == 73.21

    def test_mandate_setup_has_no_amount(self):
        sub = submit_mandate_setup("REF2", "C1", date(2020, 6, 1))
        assert sub.amount_gbp is None


class TestResolveSuccess:
    def test_success_keeps_expected_outcome_date(self):
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "success")
        assert resolved.status == "success"
        assert resolved.expected_outcome_date == sub.expected_outcome_date
        assert resolved.reason_code is None

    def test_success_never_forges_data_earlier_than_submission(self):
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "success")
        assert resolved.expected_outcome_date >= sub.submission_date


class TestResolveFailureCollection:
    def test_failed_collection_gets_a_real_arudd_reason_code(self):
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed")
        assert resolved.status == "failed"
        assert resolved.reason_code in ARUDD_REASON_CODES

    def test_failed_collection_defaults_to_refer_to_payer(self):
        """The documented real-world dominant code -- deterministic without
        rng, not a fabricated distribution."""
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed")
        assert resolved.reason_code == 0
        assert ARUDD_REASON_CODES[0] == "Refer to Payer"

    def test_failed_collection_notification_lags_past_collection_day(self):
        """The actual "cash lands when the rails say" physics: a failure
        isn't known until AFTER the notional collection date, never on it."""
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed")
        assert resolved.expected_outcome_date >= sub.expected_outcome_date

    def test_failed_collection_lag_bounded_by_real_window(self):
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed")
        # The lag is measured in WORKING days -- the real ARUDD window.
        max_date = _add_working_days(sub.expected_outcome_date, ARUDD_NOTIFICATION_LAG_DAYS)
        assert sub.expected_outcome_date <= resolved.expected_outcome_date <= max_date

    def test_rng_picks_a_valid_lag_within_the_real_window(self):
        rng = random.Random(42)
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed", rng=rng)
        # Lag is 0..ARUDD_NOTIFICATION_LAG_DAYS WORKING days -- reconstruct
        # the working-day count rather than a raw calendar delta (which would
        # over-count any weekend the lag crosses).
        assert sub.expected_outcome_date <= resolved.expected_outcome_date
        assert resolved.expected_outcome_date <= _add_working_days(
            sub.expected_outcome_date, ARUDD_NOTIFICATION_LAG_DAYS)
        assert resolved.expected_outcome_date.weekday() < 5  # never a weekend

    def test_reason_code_stays_dominant_even_with_rng_supplied(self):
        """rng only ever affects the lag, never the reason-code choice --
        no sourced real-world frequency split exists to randomise over."""
        rng = random.Random(1)
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed", rng=rng)
        assert resolved.reason_code == 0


class TestResolveFailureMandateSetup:
    def test_failed_mandate_setup_gets_a_real_auddis_reason_code(self):
        sub = submit_mandate_setup("REF2", "C1", date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed")
        assert resolved.reason_code in AUDDIS_REASON_CODES

    def test_failed_mandate_setup_does_not_get_arudd_lag(self):
        """Only collections get the extra ARUDD notification lag -- a
        mandate-setup rejection is known on Day 2 (AUDDIS), not later."""
        sub = submit_mandate_setup("REF2", "C1", date(2020, 6, 1))
        resolved = resolve_submission(sub, "failed")
        assert resolved.expected_outcome_date == sub.expected_outcome_date


class TestWorkingDayCycle:
    """The Bacs cycle counts WORKING days, never calendar days. These are the
    mutation-kill tests for that control: reverting _outcome_date/
    resolve_submission to plain `timedelta(days=...)` calendar arithmetic
    (the prior, R10-defective behaviour) fails every weekend-crossing case
    below, while the pre-existing Monday-fixture tests would still pass."""

    def test_friday_collection_settles_the_following_wednesday(self):
        # 2020-06-05 is a Friday; 3 working days = Mon/Tue/Wed = 2020-06-10,
        # NOT the following Monday (2020-06-08) a calendar +3 would give.
        assert date(2020, 6, 5).weekday() == 4  # Friday
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 5))
        assert sub.expected_outcome_date == date(2020, 6, 10)

    def test_thursday_mandate_setup_skips_the_weekend(self):
        # 2020-06-04 is a Thursday; 2 working days = Fri/Mon = 2020-06-08,
        # NOT 2020-06-06 (a Saturday) a calendar +2 would give.
        assert date(2020, 6, 4).weekday() == 3  # Thursday
        sub = submit_mandate_setup("REF2", "C1", date(2020, 6, 4))
        assert sub.expected_outcome_date == date(2020, 6, 8)
        assert sub.expected_outcome_date.weekday() < 5

    def test_collection_outcome_date_is_never_a_weekend(self):
        # Sweep every submission day in a fortnight -- no rails outcome date
        # may ever land on a Saturday or Sunday.
        for offset in range(14):
            d = date(2020, 6, 1) + __import__("datetime").timedelta(days=offset)
            sub = submit_collection("R", "C", 10.0, d)
            assert sub.expected_outcome_date.weekday() < 5, d

    def test_failed_collection_notification_never_lands_on_a_weekend(self):
        for offset in range(14):
            d = date(2020, 6, 1) + __import__("datetime").timedelta(days=offset)
            sub = submit_collection("R", "C", 10.0, d)
            resolved = resolve_submission(sub, "failed")
            assert resolved.expected_outcome_date.weekday() < 5, d

    def test_add_working_days_helper_skips_weekends_and_never_returns_one(self):
        # Friday + 1 working day = Monday.
        assert _add_working_days(date(2020, 6, 5), 1) == date(2020, 6, 8)
        # n=0 is identity.
        assert _add_working_days(date(2020, 6, 5), 0) == date(2020, 6, 5)
        # No positive advance ever lands on a weekend.
        for start_off in range(9):
            start = date(2020, 6, 1) + __import__("datetime").timedelta(days=start_off)
            for n in range(1, 6):
                assert _add_working_days(start, n).weekday() < 5


class TestResolveDueSubmissions:
    def test_resolves_only_submissions_with_a_decided_outcome(self):
        subs = [
            submit_collection("REF1", "C1", 50.0, date(2020, 6, 1)),
            submit_collection("REF2", "C2", 30.0, date(2020, 6, 1)),
        ]
        resolved = resolve_due_submissions(subs, {"REF1": "success"})
        by_ref = {s.reference: s for s in resolved}
        assert by_ref["REF1"].status == "success"
        assert by_ref["REF2"].status == "pending"

    def test_preserves_submission_order(self):
        subs = [
            submit_collection("REF1", "C1", 50.0, date(2020, 6, 1)),
            submit_collection("REF2", "C2", 30.0, date(2020, 6, 1)),
            submit_collection("REF3", "C3", 20.0, date(2020, 6, 1)),
        ]
        resolved = resolve_due_submissions(subs, {"REF1": "success", "REF3": "failed"})
        assert [s.reference for s in resolved] == ["REF1", "REF2", "REF3"]

    def test_empty_decided_outcomes_leaves_everything_pending(self):
        subs = [submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))]
        resolved = resolve_due_submissions(subs, {})
        assert resolved[0].status == "pending"


class TestNoBehaviouralDecisionDuplicated:
    """Structural guard: this module must never independently decide
    success/failed -- that stays in simulation/arrears_engine.py::
    payment_outcome() (R13: baseline behavioural probability is anchored
    there, not duplicated for a second model here)."""

    def test_resolve_requires_an_explicit_outcome_argument(self):
        sub = submit_collection("REF1", "C1", 50.0, date(2020, 6, 1))
        with pytest.raises(TypeError):
            resolve_submission(sub)  # no decided_outcome -- must be supplied by the caller

    def test_module_has_no_own_probability_constants(self):
        import simulation.bacs_rails as mod
        source = open(mod.__file__).read()
        assert "random.random()" not in source
        assert "rng.random()" not in source
