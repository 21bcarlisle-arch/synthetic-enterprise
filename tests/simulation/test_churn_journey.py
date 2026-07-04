"""Phase QL: churn journey state machine (docs/design/PROCESS_MODEL.md Section 2).

Tests the orchestration of the dormant Phase DZ/EA/EB/ED behavioral-physics
modules (resentment_ledger, reputation_index, activation_energy) into the
CONTENT -> IRRITATED -> IN_MARKET -> COMPARING -> (SWITCHED|STAYED_SVT) journey.
"""
import datetime as dt

import pytest

from company.core.activation_energy import ActionType, ActivationEnergyProfile
from company.core.reputation_index import GlobalReputationIndex
from company.core.resentment_ledger import FrictionEventType
from simulation.churn_journey import ChurnJourneyRegister, ChurnJourneyState


def test_new_customer_starts_content():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=2.0)
    assert reg.get_state("C1") == ChurnJourneyState.CONTENT


def test_no_friction_stays_content():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=2.0)
    state = reg.advance("C1", dt.date(2024, 6, 1))
    assert state == ChurnJourneyState.CONTENT


def test_friction_below_irritated_threshold_stays_content():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=2.0, churn_threshold=50.0)
    # CALL_WAIT_LONG = 6.0, well under 0.35 * 50 = 17.5
    reg.record_friction("C1", FrictionEventType.CALL_WAIT_LONG, dt.date(2024, 1, 1))
    state = reg.advance("C1", dt.date(2024, 1, 2))
    assert state == ChurnJourneyState.CONTENT


def test_friction_above_irritated_threshold_moves_to_irritated():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=2.0, churn_threshold=50.0)
    # BILL_SHOCK = 18.0 > 0.35 * 50 = 17.5
    reg.record_friction("C1", FrictionEventType.BILL_SHOCK, dt.date(2024, 1, 1))
    state = reg.advance("C1", dt.date(2024, 1, 2))
    assert state == ChurnJourneyState.IRRITATED


def test_irritated_customer_needs_renewal_window_to_enter_market():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=0.0, churn_threshold=50.0)
    reg.record_friction("C1", FrictionEventType.BILL_SHOCK, dt.date(2024, 1, 1))
    reg.advance("C1", dt.date(2024, 1, 2))  # -> IRRITATED
    # No renewal window open, no perceived saving -- stays IRRITATED
    state = reg.advance("C1", dt.date(2024, 1, 3), renewal_window_open=False)
    assert state == ChurnJourneyState.IRRITATED


def test_irritated_customer_with_renewal_window_and_saving_enters_market_then_comparing():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=0.0, churn_threshold=50.0)
    reg.record_friction("C1", FrictionEventType.BILL_SHOCK, dt.date(2024, 1, 1))
    reg.advance("C1", dt.date(2024, 1, 2))  # -> IRRITATED
    # Base switching AE with no tenure/PPM bonus = 100.0; a large perceived
    # saving must exceed it to enter the market.
    state = reg.advance(
        "C1", dt.date(2024, 1, 3), renewal_window_open=True,
        perceived_bill_saving_gbp=500.0,
    )
    assert state == ChurnJourneyState.IN_MARKET
    # Next period's advance moves IN_MARKET -> COMPARING
    state2 = reg.advance("C1", dt.date(2024, 2, 1))
    assert state2 == ChurnJourneyState.COMPARING


def test_high_tenure_raises_activation_energy_barrier():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=8.0, churn_threshold=50.0)  # tenure bonus capped at 40
    reg.record_friction("C1", FrictionEventType.BILL_SHOCK, dt.date(2024, 1, 1))
    reg.advance("C1", dt.date(2024, 1, 2))  # -> IRRITATED
    # A saving that would clear the base-AE=100 customer does not clear a
    # high-tenure customer's higher barrier (100 + 40 tenure bonus = 140).
    state = reg.advance(
        "C1", dt.date(2024, 1, 3), renewal_window_open=True,
        perceived_bill_saving_gbp=110.0,
    )
    assert state == ChurnJourneyState.IRRITATED


def test_strong_reputation_raises_barrier_via_gri_multiplier():
    gri = GlobalReputationIndex(starting_gri=80.0)  # STRONG band -> 1.3x AE multiplier
    reg = ChurnJourneyRegister(gri=gri)
    reg.register_customer("C1", tenure_years=0.0, churn_threshold=50.0)
    reg.record_friction("C1", FrictionEventType.BILL_SHOCK, dt.date(2024, 1, 1))
    reg.advance("C1", dt.date(2024, 1, 2))  # -> IRRITATED
    # Base AE=100; STRONG GRI multiplier 1.3x -> effective AE=130. A saving of
    # 110 clears the unmodified barrier but not the reputation-amplified one.
    state = reg.advance(
        "C1", dt.date(2024, 1, 3), renewal_window_open=True,
        perceived_bill_saving_gbp=110.0,
    )
    assert state == ChurnJourneyState.IRRITATED


def test_resentment_burn_forces_comparing_regardless_of_renewal_window():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=0.0, churn_threshold=20.0)
    reg.record_friction("C1", FrictionEventType.COMPLAINT_UNRESOLVED, dt.date(2024, 1, 1))  # +20
    journey = reg.get_journey("C1")
    assert journey.resentment.check_threshold(dt.date(2024, 1, 1)) is True
    state = reg.advance("C1", dt.date(2024, 1, 2), renewal_window_open=False)
    assert state == ChurnJourneyState.COMPARING


def test_record_decision_switched():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1")
    journey = reg.get_journey("C1")
    state = journey.record_decision(dt.date(2024, 3, 1), switched=True)
    assert state == ChurnJourneyState.SWITCHED
    assert journey.is_catchable() is True


def test_record_decision_stayed():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1")
    journey = reg.get_journey("C1")
    state = journey.record_decision(dt.date(2024, 3, 1), switched=False)
    assert state == ChurnJourneyState.STAYED_SVT


def test_terminal_state_does_not_advance_further():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1")
    journey = reg.get_journey("C1")
    journey.record_decision(dt.date(2024, 3, 1), switched=True)
    state = reg.advance("C1", dt.date(2024, 4, 1), renewal_window_open=True,
                         perceived_bill_saving_gbp=1000.0)
    assert state == ChurnJourneyState.SWITCHED


def test_home_move_is_not_catchable():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1")
    journey = reg.get_journey("C1")
    state = journey.record_home_move(dt.date(2024, 5, 1))
    assert state == ChurnJourneyState.HOME_MOVE_CHURNED
    assert journey.is_catchable() is False


def test_home_move_terminal_does_not_advance_further():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1")
    journey = reg.get_journey("C1")
    journey.record_home_move(dt.date(2024, 5, 1))
    state = reg.advance("C1", dt.date(2024, 6, 1), renewal_window_open=True,
                         perceived_bill_saving_gbp=1000.0)
    assert state == ChurnJourneyState.HOME_MOVE_CHURNED


def test_stayed_svt_resets_to_content_after_one_period():
    """Phase QL Part 2: STAYED_SVT is not permanently terminal -- a retained
    customer keeps renewing, so the journey must resume tracking, not freeze."""
    reg = ChurnJourneyRegister()
    reg.register_customer("C1")
    journey = reg.get_journey("C1")
    journey.record_decision(dt.date(2024, 3, 1), switched=False)
    assert journey.state == ChurnJourneyState.STAYED_SVT
    state = reg.advance("C1", dt.date(2024, 4, 1))
    assert state == ChurnJourneyState.CONTENT


def test_stayed_svt_reset_customer_can_re_enter_funnel():
    """After the post-decision reset, fresh friction can move the customer
    through the funnel again -- this is what lets a decayed-then-recurring
    risk (Phase QK's finding) show up in a later renewal cycle."""
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=0.0, churn_threshold=50.0)
    journey = reg.get_journey("C1")
    journey.record_decision(dt.date(2024, 3, 1), switched=False)
    reg.advance("C1", dt.date(2024, 4, 1))  # -> CONTENT (reset)
    reg.record_friction("C1", FrictionEventType.BILL_SHOCK, dt.date(2024, 5, 1))
    state = reg.advance("C1", dt.date(2024, 5, 2))
    assert state == ChurnJourneyState.IRRITATED


def test_burned_customer_returns_to_comparing_even_after_staying():
    """An irreversibly-burned customer who was nonetheless retained this cycle
    must resurface at COMPARING next period, not reset to CONTENT -- the
    resentment burn, unlike the funnel stage, does not un-happen."""
    reg = ChurnJourneyRegister()
    reg.register_customer("C1", tenure_years=0.0, churn_threshold=20.0)
    reg.record_friction("C1", FrictionEventType.COMPLAINT_UNRESOLVED, dt.date(2024, 1, 1))  # +20
    journey = reg.get_journey("C1")
    journey.resentment.check_threshold(dt.date(2024, 1, 1))
    assert journey.resentment.is_burned is True
    journey.record_decision(dt.date(2024, 1, 2), switched=False)
    assert journey.state == ChurnJourneyState.STAYED_SVT
    state = reg.advance("C1", dt.date(2024, 2, 1))
    assert state == ChurnJourneyState.COMPARING


def test_portfolio_summary_counts_states():
    reg = ChurnJourneyRegister()
    reg.register_customer("C1")
    reg.register_customer("C2")
    reg.get_journey("C2").record_decision(dt.date(2024, 1, 1), switched=True)
    summary = reg.portfolio_summary(dt.date(2024, 6, 1))
    assert "2 customers" in summary
    assert "content" in summary
    assert "switched" in summary
