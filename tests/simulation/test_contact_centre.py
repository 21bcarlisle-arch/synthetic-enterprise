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
    contact_model = {
        "by_customer": {
            "C1": [
                {"customer_id": "C1", "period_end": "2020-01-31", "contact_probability": 0.0},
                {"customer_id": "C1", "period_end": "2020-02-29", "contact_probability": 1.0},
            ],
        }
    }
    log = generate_contact_centre_log([], contact_model)
    assert len(log) == 1
    assert log[0]["period_end"] == "2020-02-29"
    assert log[0]["channel"] in ("phone", "email", "webchat")


def test_generate_contact_centre_log_empty_contact_model():
    assert generate_contact_centre_log([], {}) == []
