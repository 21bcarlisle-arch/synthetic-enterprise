"""Tests for Customer Onboarding Journey Tracker (Phase FE)."""
import datetime as dt
import pytest
from company.crm.onboarding_journey import (
    OnboardingStage, OnboardingEvent, OnboardingJourney,
    OnboardingJourneyTracker,
)

SWITCH_DATE = dt.date(2024, 1, 5)
SUPPLY_DATE = dt.date(2024, 2, 1)
AS_OF = dt.date(2024, 6, 1)
ACCT = "C1"


def make_journey_with_supply(tracker, supply_date=SUPPLY_DATE):
    tracker.start_journey(ACCT, SWITCH_DATE)
    return tracker.advance_stage(ACCT, OnboardingStage.SUPPLY_START, supply_date)


class TestOnboardingJourney:
    def test_current_stage_after_start(self):
        tracker = OnboardingJourneyTracker()
        j = tracker.start_journey(ACCT, SWITCH_DATE)
        assert j.current_stage == OnboardingStage.SWITCH_REQUESTED

    def test_supply_start_date(self):
        tracker = OnboardingJourneyTracker()
        j = make_journey_with_supply(tracker)
        assert j.supply_start_date == SUPPLY_DATE

    def test_welcome_pack_deadline(self):
        tracker = OnboardingJourneyTracker()
        j = make_journey_with_supply(tracker)
        assert j.welcome_pack_deadline() > SUPPLY_DATE

    def test_first_bill_deadline(self):
        tracker = OnboardingJourneyTracker()
        j = make_journey_with_supply(tracker)
        assert j.first_bill_deadline() == SUPPLY_DATE + dt.timedelta(days=92)

    def test_welcome_pack_overdue(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker, supply_date=dt.date(2023, 1, 1))
        j = tracker.journey_for(ACCT)
        assert j.is_welcome_pack_overdue(AS_OF)

    def test_welcome_pack_not_overdue_when_issued(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker, supply_date=dt.date(2023, 1, 1))
        tracker.advance_stage(ACCT, OnboardingStage.WELCOME_PACK_ISSUED, dt.date(2023, 1, 15))
        j = tracker.journey_for(ACCT)
        assert not j.is_welcome_pack_overdue(AS_OF)

    def test_first_bill_overdue(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker, supply_date=dt.date(2023, 1, 1))
        j = tracker.journey_for(ACCT)
        assert j.is_first_bill_overdue(AS_OF)

    def test_onboarding_complete(self):
        tracker = OnboardingJourneyTracker()
        tracker.start_journey(ACCT, SWITCH_DATE)
        tracker.advance_stage(ACCT, OnboardingStage.ONBOARDING_COMPLETE, AS_OF)
        j = tracker.journey_for(ACCT)
        assert j.is_onboarding_complete()

    def test_journey_summary(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker)
        j = tracker.journey_for(ACCT)
        s = j.journey_summary()
        assert ACCT in s


class TestOnboardingJourneyTracker:
    def test_start_and_retrieve(self):
        tracker = OnboardingJourneyTracker()
        tracker.start_journey(ACCT, SWITCH_DATE)
        assert tracker.journey_for(ACCT) is not None

    def test_advance_stage(self):
        tracker = OnboardingJourneyTracker()
        tracker.start_journey(ACCT, SWITCH_DATE)
        j = tracker.advance_stage(ACCT, OnboardingStage.SUPPLY_START, SUPPLY_DATE)
        assert j.current_stage == OnboardingStage.SUPPLY_START

    def test_incomplete_journeys(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker)
        assert len(tracker.incomplete_journeys()) == 1

    def test_overdue_welcome_packs(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker, dt.date(2023, 1, 1))
        assert len(tracker.overdue_welcome_packs(AS_OF)) == 1

    def test_overdue_first_bills(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker, dt.date(2023, 1, 1))
        assert len(tracker.overdue_first_bills(AS_OF)) == 1

    def test_onboarding_summary(self):
        tracker = OnboardingJourneyTracker()
        make_journey_with_supply(tracker)
        s = tracker.onboarding_summary(AS_OF)
        assert "Onboarding" in s


# --- Phase MP depth tests ---

def test_account_id_stored():
    tracker = OnboardingJourneyTracker()
    j = tracker.start_journey("C5", SWITCH_DATE)
    assert j.account_id == "C5"


def test_switch_request_date_stored():
    tracker = OnboardingJourneyTracker()
    j = tracker.start_journey(ACCT, SWITCH_DATE)
    assert j.switch_request_date == SWITCH_DATE


def test_onboarding_stage_count():
    assert len(list(OnboardingStage)) == 10


def test_events_tuple():
    tracker = OnboardingJourneyTracker()
    j = tracker.start_journey(ACCT, SWITCH_DATE)
    assert isinstance(j.events, tuple)
    assert len(j.events) == 1


def test_supply_start_date_none_without_supply_event():
    tracker = OnboardingJourneyTracker()
    j = tracker.start_journey(ACCT, SWITCH_DATE)
    assert j.supply_start_date is None


def test_welcome_pack_deadline_none_without_supply():
    tracker = OnboardingJourneyTracker()
    j = tracker.start_journey(ACCT, SWITCH_DATE)
    assert j.welcome_pack_deadline() is None


def test_smart_meter_offer_deadline():
    tracker = OnboardingJourneyTracker()
    j = make_journey_with_supply(tracker)
    assert j.smart_meter_offer_deadline() == SUPPLY_DATE + dt.timedelta(days=365)


def test_onboarding_event_stage_stored():
    event = OnboardingEvent(stage=OnboardingStage.SUPPLY_START, occurred_at=SUPPLY_DATE)
    assert event.stage == OnboardingStage.SUPPLY_START


def test_onboarding_event_occurred_at_stored():
    event = OnboardingEvent(stage=OnboardingStage.SUPPLY_START, occurred_at=SUPPLY_DATE)
    assert event.occurred_at == SUPPLY_DATE


def test_start_journey_returns_onboarding_journey():
    tracker = OnboardingJourneyTracker()
    result = tracker.start_journey(ACCT, SWITCH_DATE)
    assert isinstance(result, OnboardingJourney)
