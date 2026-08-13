"""Phase 3 (CORE_FIDELITY_PHASES.md item 4): contact-centre first-response
time model.

Tests simulation/contact_centre.py: deterministic dispatch, channel split,
phone/webchat never breaching (live channels), email breach against the SLA
target.
"""
from simulation.contact_centre import (
    EMAIL_FIRST_RESPONSE_SLA_HOURS,
    generate_contact_centre_log,
    simulate_contact,
)
from simulation.household_segments import (
    EngagementLevel,
    engagement_level_for_customer,
)


def _customer_of(level: EngagementLevel) -> str:
    """First synthetic id landing in `level` -- resolved, never hardcoded, so a
    re-draw of the archetype assignment cannot silently make this test about a
    different archetype than it names."""
    for index in range(2000):
        customer_id = f"CC{index:04d}"
        if engagement_level_for_customer(customer_id) == level:
            return customer_id
    raise AssertionError(f"no synthetic customer resolved to {level}")


def test_no_contact_when_probability_zero():
    event = simulate_contact("C1", "2020-01-31", 0.0)
    assert event.occurred is False
    assert event.channel is None
    assert event.first_response_hours is None


def test_contact_is_deterministic():
    e1 = simulate_contact("C1", "2020-01-31", 0.9)
    e2 = simulate_contact("C1", "2020-01-31", 0.9)
    assert e1 == e2


def test_contact_varies_by_period():
    occurred_flags = {
        simulate_contact("C1", f"20{yr}-01-31", 0.3).occurred for yr in range(16, 30)
    }
    assert len(occurred_flags) > 1


def test_channel_is_one_of_known_set():
    for yr in range(16, 40):
        event = simulate_contact("C2", f"20{yr}-01-31", 0.9)
        if event.occurred:
            assert event.channel in ("phone", "email", "webchat")


def test_phone_and_webchat_never_breach_sla():
    for yr in range(16, 60):
        event = simulate_contact("C3", f"20{yr}-01-31", 0.95)
        if event.occurred and event.channel in ("phone", "webchat"):
            assert event.breached_sla is False


def test_email_can_breach_sla():
    found_breach = False
    for yr in range(16, 200):
        event = simulate_contact("C4", f"2016-{(yr % 12) + 1:02d}-{(yr % 27) + 1:02d}", 0.95)
        if event.occurred and event.channel == "email" and event.breached_sla:
            found_breach = True
            assert event.first_response_hours > EMAIL_FIRST_RESPONSE_SLA_HOURS
            break
    assert found_breach, "expected at least one email SLA breach across many trials"


def test_first_response_hours_non_negative():
    for yr in range(16, 40):
        event = simulate_contact("C5", f"20{yr}-01-31", 0.9)
        if event.occurred:
            assert event.first_response_hours >= 0


def test_generate_contact_centre_log_only_includes_occurred_contacts():
    """The log is a filter over BILLS, and the filter is the world's propensity.

    Rewritten 2026-08-13 with the §3k cut: this used to hand in a hand-written
    `contact_model` (the supplier's estimate) with an empty `bills` list, which
    is exactly the inversion the cut removed -- a log built from the company's
    numbers while the actual documents played no part. It now drives the real
    path: a perfectly clear bill with no shock against a disengaged household
    is the world's quiet case, an illegible doubled bill to an engaged one its
    loud case.

    Asserted as a PROPERTY over the whole fixture rather than by naming which
    quiet bill happens not to fire: a specific (customer, period) seed landing
    below the base rate is a fact about one draw, and a test tuned to it has the
    seed as its subject rather than the filter.
    """
    loud_customer = _customer_of(EngagementLevel.ACTIVE)
    quiet_customer = _customer_of(EngagementLevel.DISENGAGED)
    loud = [
        {
            "customer_id": loud_customer,
            "period_end": f"2020-{month:02d}-28",
            "clarity_score": 0.0,
            "bill_shock_pct": 1.0,
        }
        for month in range(1, 13)
    ]
    quiet = [
        {
            "customer_id": quiet_customer,
            "period_end": f"2020-{month:02d}-28",
            "clarity_score": 1.0,
            "bill_shock_pct": None,
        }
        for month in range(1, 13)
    ]
    log = generate_contact_centre_log(quiet + loud)
    contacted = {(entry["customer_id"], entry["period_end"]) for entry in log}

    # An illegible, doubled bill to an ACTIVE household saturates the world's
    # propensity at 1.0 -- every one of these is a contact, whatever the draw.
    assert all((loud_customer, bill["period_end"]) in contacted for bill in loud)
    # A perfectly clear bill with no shock to a DISENGAGED household sits near
    # the base rate; most of these must be silent, or the propensity is not
    # reaching the filter.
    quiet_contacts = sum(
        1 for bill in quiet if (quiet_customer, bill["period_end"]) in contacted
    )
    assert quiet_contacts < len(quiet) / 2

    assert all(entry["channel"] in ("phone", "email", "webchat") for entry in log)


def test_generate_contact_centre_log_is_empty_for_no_bills():
    """Replaces `test_generate_contact_centre_log_empty_contact_model`, whose
    subject (an empty supplier estimate) no longer exists on this signature."""
    assert generate_contact_centre_log([]) == []
