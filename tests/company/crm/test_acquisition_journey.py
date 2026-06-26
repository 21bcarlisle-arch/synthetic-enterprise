import pytest
from datetime import date
from company.crm.acquisition_journey import (
    AcquisitionStage, AcquisitionJourney, AcquisitionFunnel,
)


@pytest.fixture
def funnel():
    return AcquisitionFunnel()


@pytest.fixture
def journey(funnel):
    return funnel.start_journey("C001", "comparison_site", date(2022, 3, 1))


def test_start_journey_sets_quote_stage(journey):
    assert AcquisitionStage.QUOTE_REQUESTED in journey.stage_dates
    assert journey.current_stage == AcquisitionStage.QUOTE_REQUESTED
    assert journey.converted is False


def test_advance_moves_to_new_stage(funnel, journey):
    funnel.advance("C001", AcquisitionStage.APPLICATION_SUBMITTED, date(2022, 3, 2))
    assert journey.current_stage == AcquisitionStage.APPLICATION_SUBMITTED


def test_advance_returns_false_for_unknown_customer(funnel):
    result = funnel.advance("UNKNOWN", AcquisitionStage.SIGNED_UP, date(2022, 3, 5))
    assert result is False


def test_is_complete_false_midway(journey):
    assert journey.is_complete is False


def test_is_complete_true_on_onboarded(funnel, journey):
    funnel.advance("C001", AcquisitionStage.ONBOARDED, date(2022, 3, 10))
    assert journey.is_complete is True
    assert journey.converted is True


def test_credit_declined_is_terminal(funnel, journey):
    funnel.advance("C001", AcquisitionStage.CREDIT_DECLINED, date(2022, 3, 3))
    assert journey.is_complete is True
    assert journey.converted is False


def test_days_to_stage(funnel, journey):
    funnel.advance("C001", AcquisitionStage.SIGNED_UP, date(2022, 3, 8))
    assert journey.days_to_stage(AcquisitionStage.SIGNED_UP) == 7


def test_days_to_stage_none_if_not_reached(journey):
    assert journey.days_to_stage(AcquisitionStage.ONBOARDED) is None


def test_conversion_rate_quote_to_onboarded(funnel):
    j1 = funnel.start_journey("C001", "direct", date(2022, 1, 1))
    j1.advance(AcquisitionStage.ONBOARDED, date(2022, 1, 15))
    j2 = funnel.start_journey("C002", "direct", date(2022, 1, 5))
    funnel.advance("C002", AcquisitionStage.CREDIT_DECLINED, date(2022, 1, 7))
    rate = funnel.conversion_rate(
        AcquisitionStage.QUOTE_REQUESTED, AcquisitionStage.ONBOARDED
    )
    assert rate == pytest.approx(0.5)


def test_drop_off_at_stage(funnel):
    funnel.start_journey("C001", "web", date(2022, 2, 1))
    funnel.advance("C001", AcquisitionStage.APPLICATION_SUBMITTED, date(2022, 2, 2))
    funnel.start_journey("C002", "web", date(2022, 2, 1))
    funnel.advance("C002", AcquisitionStage.APPLICATION_SUBMITTED, date(2022, 2, 2))
    funnel.advance("C002", AcquisitionStage.CREDIT_APPROVED, date(2022, 2, 3))
    drop_off = funnel.drop_off_at(AcquisitionStage.APPLICATION_SUBMITTED)
    assert len(drop_off) == 1
    assert drop_off[0].customer_id == "C001"


def test_channel_summary(funnel):
    j1 = funnel.start_journey("C001", "comparison_site", date(2022, 1, 1))
    j1.advance(AcquisitionStage.ONBOARDED, date(2022, 1, 20))
    j2 = funnel.start_journey("C002", "comparison_site", date(2022, 1, 5))
    funnel.advance("C002", AcquisitionStage.CREDIT_DECLINED, date(2022, 1, 8))
    funnel.start_journey("C003", "direct", date(2022, 1, 10))
    summary = funnel.channel_summary("comparison_site")
    assert summary["total"] == 2
    assert summary["converted"] == 1
    assert summary["conversion_rate"] == pytest.approx(0.5)


def test_channel_summary_empty(funnel):
    summary = funnel.channel_summary("telemarketing")
    assert summary["total"] == 0
