"""Tests for company.interfaces.sim_interface."""

import datetime as _dt

import pytest

from company.interfaces.sim_interface import (
    FlexVenueUnreachable,
    LiveSimInterface,
    SimInterface,
    StubSimInterface,
    build_sim_interface,
)
from company.market.flex_participation import FlexEnrolmentRefused
from interface.contracts.flex_observable_seam import (
    FlexDirection,
    FlexEnrolment,
    FlexEnrolmentOutcome,
    FlexVenue,
)


def test_stub_interface_get_settlement_returns_stub_flag():
    iface = StubSimInterface()
    result = iface.get_settlement_data("1234567890123", "2016-01-01")
    assert result["_stub"] is True
    assert result["mpan"] == "1234567890123"


def test_stub_interface_get_forward_price_electricity():
    iface = StubSimInterface()
    assert iface.get_forward_price("electricity", "2016-01-01") == 120.0


def test_stub_interface_get_forward_price_gas():
    iface = StubSimInterface()
    assert iface.get_forward_price("gas", "2016-01-01") == 50.0


def test_stub_interface_get_customer_status_defaults_active():
    iface = StubSimInterface()
    assert iface.get_customer_status("C1") == "active"


def test_stub_interface_notify_churn_updates_status():
    iface = StubSimInterface()
    iface.notify_churn("C3", "2020-06-30")
    assert iface.get_customer_status("C3") == "churned"
    assert len(iface.churn_notifications) == 1
    assert iface.churn_notifications[0]["account_id"] == "C3"


def test_stub_interface_notify_acquisition_updates_status():
    iface = StubSimInterface()
    iface.notify_acquisition("C3_3", "2020-07-01")
    assert iface.get_customer_status("C3_3") == "active"
    assert len(iface.acquisition_notifications) == 1


def test_stub_churn_then_reactivation():
    iface = StubSimInterface()
    iface.notify_churn("C1", "2021-12-30")
    assert iface.get_customer_status("C1") == "churned"
    iface.notify_acquisition("C1_2", "2021-12-30")
    assert iface.get_customer_status("C1_2") == "active"


def test_base_interface_raises_not_implemented():
    iface = SimInterface()
    with pytest.raises(NotImplementedError):
        iface.get_settlement_data("mpan", "2016-01-01")
    with pytest.raises(NotImplementedError):
        iface.get_forward_price("electricity", "2016-01-01")
    with pytest.raises(NotImplementedError):
        iface.get_customer_status("C1")


def test_build_sim_interface_returns_stub():
    iface = build_sim_interface(live=False)
    assert isinstance(iface, StubSimInterface)


def test_build_sim_interface_live_returns_live_interface():
    from company.interfaces.sim_interface import LiveSimInterface
    iface = build_sim_interface(live=True)
    assert isinstance(iface, LiveSimInterface)


def test_stub_interface_notify_retention_attempt_stores_notification():
    iface = StubSimInterface()
    iface.notify_retention_attempt("C1", "2021-01-01", 0.42, 0.05)
    assert len(iface.retention_notifications) == 1
    n = iface.retention_notifications[0]
    assert n["account_id"] == "C1"
    assert n["event_date"] == "2021-01-01"
    assert abs(n["company_churn_estimate"] - 0.42) < 1e-6
    assert abs(n["discount_pct"] - 0.05) < 1e-6
    assert n["outcome"] == "pending"


def test_stub_interface_notify_retention_attempt_with_outcome():
    iface = StubSimInterface()
    iface.notify_retention_attempt("C2", "2022-06-30", 0.55, 0.05, outcome="retained")
    assert iface.retention_notifications[0]["outcome"] == "retained"


def test_stub_interface_retention_notifications_returns_copy():
    iface = StubSimInterface()
    iface.notify_retention_attempt("C1", "2021-01-01", 0.3, 0.05)
    copy1 = iface.retention_notifications
    copy2 = iface.retention_notifications
    assert copy1 == copy2
    assert copy1 is not copy2


def test_live_interface_notify_retention_records_to_event_log():
    from company.crm.event_log import RetentionEvent
    from company.interfaces.sim_interface import LiveSimInterface
    iface = LiveSimInterface()
    iface.notify_retention_attempt("C3", "2021-12-30", 0.48, 0.05, outcome="churned_despite_offer")
    ret_events = iface.event_log.retention_events()
    assert len(ret_events) == 1
    assert ret_events[0].customer_id == "C3"
    assert ret_events[0].outcome == "churned_despite_offer"


# --- Phase MO depth tests ---

def test_churn_notification_stores_reason():
    iface = StubSimInterface()
    iface.notify_churn("C1", "2020-06-30", reason="price-increase")
    assert iface.churn_notifications[0]["reason"] == "price-increase"


def test_churn_notification_stores_sim_churn_probability():
    iface = StubSimInterface()
    iface.notify_churn("C1", "2020-06-30", sim_churn_probability=0.72)
    assert iface.churn_notifications[0]["sim_churn_probability"] == pytest.approx(0.72)


def test_acquisition_notification_stores_channel():
    iface = StubSimInterface()
    iface.notify_acquisition("C2", "2020-07-01", channel="home-move-win")
    assert iface.acquisition_notifications[0]["channel"] == "home-move-win"


def test_acquisition_notification_stores_predecessor_id():
    iface = StubSimInterface()
    iface.notify_acquisition("C1_2", "2020-07-01", predecessor_id="C1")
    assert iface.acquisition_notifications[0]["predecessor_id"] == "C1"


def test_settlement_data_returns_period():
    iface = StubSimInterface()
    result = iface.get_settlement_data("1234567890123", "2016-06-01")
    assert result["period"] == "2016-06-01"


def test_settlement_data_returns_consumption_kwh():
    iface = StubSimInterface()
    result = iface.get_settlement_data("1234567890123", "2016-06-01")
    assert "consumption_kwh" in result


def test_get_churn_estimate_returns_float_in_range():
    iface = StubSimInterface()
    est = iface.get_churn_estimate("C1", 100.0, 120.0, 3.0, 2800.0)
    assert isinstance(est, float)
    assert 0.0 <= est <= 0.95


def test_base_interface_raises_for_notify_churn():
    iface = SimInterface()
    with pytest.raises(NotImplementedError):
        iface.notify_churn("C1", "2020-01-01")


def test_base_interface_raises_for_get_churn_estimate():
    iface = SimInterface()
    with pytest.raises(NotImplementedError):
        iface.get_churn_estimate("C1", 100.0, 120.0, 3.0)


def test_get_forward_price_unknown_fuel_returns_100():
    iface = StubSimInterface()
    assert iface.get_forward_price("wind", "2020-01-01") == pytest.approx(100.0)


# ===========================================================================
# EP6 pass 54 -- THE FLEX ENROLMENT DOOR ON THE SEAM.
#
# WHAT WAS WRONG. `enrol_flex` was the one declared COMPANY -> WORLD crossing
# for flex and it crossed nothing: the stub built a request envelope with its
# own private id grammar, appended it to a list nothing read, and handed the
# company back its OWN question; `LiveSimInterface` did not implement the
# method at all. So the venue settled `FLEX_UNIT_1` -- a keyword default --
# whether or not anybody had enrolled it. No test in this repository called
# `enrol_flex`, which is why none of that was ever visible.
#
# The round trip below is driven through the SHIPPED pieces on both sides
# (company encoder -> venue's independently-written decoder -> company reader).
# A seam test that asserted this module agrees with a fixture written here is
# the R15 TAUTOLOGY for the one question a seam is asked.
# ===========================================================================

#: The venue reads the request well before the window opens, so a refusal in
#: any test below is about the thing that test names and never about the clock.
_VENUE_CLOCK = _dt.datetime(2026, 2, 20, 10, 0)
_ASOF = _dt.datetime(2026, 2, 20, 9, 0)


def _enrolment(
    unit_id="UNIT-A",
    venue=FlexVenue.BALANCING_MECHANISM,
    mw=5.0,
    start=_dt.datetime(2026, 3, 1, 16, 0),
    end=_dt.datetime(2026, 3, 1, 19, 0),
):
    return FlexEnrolment(
        unit_id=unit_id,
        venue=venue,
        offered_mw=mw,
        direction=FlexDirection.TURN_DOWN,
        window_start=start,
        window_end=end,
    )


def test_the_seam_enrols_END_TO_END_and_hands_back_the_VENUES_OWN_reference():
    """THE SUCCESS CASE, and the null control every refusal below needs: if this
    did not pass, a test asserting a refusal would prove only that the door
    never works."""
    iface = build_sim_interface(flex_venue_clock=_VENUE_CLOCK)

    outcome = iface.enrol_flex(_enrolment(), as_of=_ASOF)

    assert isinstance(outcome, FlexEnrolmentOutcome)
    assert outcome.unit_id == "UNIT-A"
    assert outcome.venue is FlexVenue.BALANCING_MECHANISM
    # The reference is minted by the VENUE's own sequence -- the one field in
    # this answer the company could not have assumed.
    assert outcome.enrolment_reference == "BALANCING_MECHANISM-REG-000001"
    assert iface.flex_registrations == ("BALANCING_MECHANISM-REG-000001",)


def test_the_door_no_longer_hands_the_company_back_its_OWN_outbound_question():
    """The regression that named this pass. A door returning the request
    envelope leaves 'did the venue register us?' unanswered anywhere in the
    build, so the old `flex_enrolments` list -- things we SAID, published as if
    they were things that HAPPENED -- is gone rather than kept alongside."""
    iface = build_sim_interface(flex_venue_clock=_VENUE_CLOCK)
    outcome = iface.enrol_flex(_enrolment(), as_of=_ASOF)

    assert not hasattr(iface, "flex_enrolments")
    assert not hasattr(outcome, "request_type")  # not an envelope
    assert not hasattr(outcome, "correlation_id")


def test_MUTATION_a_seam_with_NO_VENUE_CLOCK_refuses_instead_of_using_the_SUBMITTERS():
    """FAIL-CLOSED (R15). The obvious convenience -- default the venue's read
    time to the sender's `as_of` -- makes WINDOW_ALREADY_CLOSED a refusal the
    sender can switch off, which is the defect `sim.flex_dispatch` names in its
    own registration-desk comment.

    The second half is what makes this a control rather than an assertion about
    an error message: the SAME already-closed window that the fallback would
    have accepted is REFUSED once a real world clock is present."""
    closed = _enrolment(start=_dt.datetime(2025, 1, 1, 0, 0),
                        end=_dt.datetime(2025, 1, 1, 3, 0))

    with pytest.raises(FlexVenueUnreachable):
        build_sim_interface().enrol_flex(closed, as_of=_dt.datetime(2024, 12, 1, 9, 0))

    with pytest.raises(FlexEnrolmentRefused) as exc:
        build_sim_interface(flex_venue_clock=_VENUE_CLOCK).enrol_flex(
            closed, as_of=_dt.datetime(2024, 12, 1, 9, 0))
    assert exc.value.code == "WINDOW_ALREADY_CLOSED"


def test_a_venue_REFUSAL_raises_and_leaves_the_company_holding_NOTHING():
    """A rejected registration read as a quiet 'no flex this window' is a
    company that goes on forecasting revenue from a venue with no record of
    it."""
    iface = build_sim_interface(flex_venue_clock=_VENUE_CLOCK)

    with pytest.raises(FlexEnrolmentRefused) as exc:
        iface.enrol_flex(_enrolment(mw=0.0), as_of=_ASOF)

    assert exc.value.code == "OFFER_NOT_DELIVERABLE"
    assert iface.flex_registrations == ()
    assert iface.flex_awaiting_answer == ()


def test_the_SAME_enrolment_resubmitted_gets_ONE_reference_not_two():
    """C-S2 idempotency across the seam: the correlation id is the key, and a
    desk that recomputed would hand this company two references for one
    registration and let it quote either."""
    iface = build_sim_interface(flex_venue_clock=_VENUE_CLOCK)

    first = iface.enrol_flex(_enrolment(), as_of=_ASOF)
    second = iface.enrol_flex(_enrolment(), as_of=_ASOF)

    assert first.enrolment_reference == second.enrolment_reference
    assert iface.flex_registrations == (first.enrolment_reference,)


def test_ONE_unit_into_TWO_venues_over_ONE_day_gets_TWO_registrations():
    """The stub's private id grammar was `flex-{unit}-{date}` with no venue in
    the key, so exactly this -- the legitimate multi-venue book the L3 stacking
    model runs on -- collided on a single correlation id."""
    iface = build_sim_interface(flex_venue_clock=_VENUE_CLOCK)

    bm = iface.enrol_flex(_enrolment(venue=FlexVenue.BALANCING_MECHANISM), as_of=_ASOF)
    dfs = iface.enrol_flex(_enrolment(venue=FlexVenue.DFS_TURN_DOWN), as_of=_ASOF)

    assert bm.enrolment_reference != dfs.enrolment_reference
    assert len(set(iface.flex_registrations)) == 2


def test_an_enrolment_is_LISTED_as_awaiting_an_answer_only_until_it_is_answered():
    """What a real party chases. A response-driven company could not produce
    this list: it would learn the crossing existed from the message that ended
    it."""
    iface = build_sim_interface(flex_venue_clock=_VENUE_CLOCK)
    assert iface.flex_awaiting_answer == ()

    iface.enrol_flex(_enrolment(), as_of=_ASOF)
    assert iface.flex_awaiting_answer == ()  # answered synchronously by this desk
    assert len(iface.flex_registrations) == 1


def test_the_seam_publishes_no_door_onto_the_VENUES_OWN_book():
    """Both books live in one process because this counterparty is a mock --
    which is the thing EP6 exists to make invisible to the company. So the
    check is on the PUBLIC surface: nothing the company can reach hands out the
    venue's registrations."""
    from sim.flex_dispatch import VenueRegistrations

    iface = build_sim_interface(flex_venue_clock=_VENUE_CLOCK)
    iface.enrol_flex(_enrolment(), as_of=_ASOF)

    for name in [n for n in dir(iface) if not n.startswith("_")]:
        value = getattr(iface, name)
        assert not isinstance(value, VenueRegistrations), (
            f"{name} publishes the VENUE's own book to the company side")


def test_the_LIVE_seam_runs_the_SAME_exchange_as_the_stub():
    """`LiveSimInterface` did not implement `enrol_flex` at all, so a live
    company could not enrol into a flex venue -- the base class's
    NotImplementedError was the whole implementation."""
    live = LiveSimInterface(flex_venue_clock=_VENUE_CLOCK)
    stub = StubSimInterface(flex_venue_clock=_VENUE_CLOCK)

    assert (live.enrol_flex(_enrolment(), as_of=_ASOF)
            == stub.enrol_flex(_enrolment(), as_of=_ASOF))


def test_the_base_interface_still_refuses_to_enrol():
    with pytest.raises(NotImplementedError):
        SimInterface().enrol_flex(_enrolment(), as_of=_ASOF)
