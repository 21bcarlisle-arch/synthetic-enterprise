"""Each renewal row in the value test's sidecars says whether a retention offer was made and held.

THE_VALUE_TEST_REDESIGN s.12a attributed the value arm's GBP 1.21 loss on A's belief to retention
offers the twin made and A withdrew, by inference: the rows carried `p_retain` and the roll and
nothing about an offer, and an offered event's `p_retain` is already the post-offer figure. The
defect these tests name is a row that cannot tell a save from a plain stay. They build each event
with the world's own `retention_offer.answer_retention_offer`, so the row is graded on what the
run actually emits, not on a hand-written event.
"""

from __future__ import annotations

from simulation.customer_events import churn_roll_for_renewal
from simulation.retention_offer import answer_retention_offer
from tools.run_value_cycle_ab import _decisions_by_billing_account, retention_offer_fields

ACCOUNT, DATE = "SYN-2016-557", "2018-12-02"


def _event(p_stay: float, roll: float) -> dict:
    return {"customer_id": ACCOUNT, "event_date": DATE, "commodity": "electricity",
            "event_type": "renewed" if roll <= p_stay else "churned",
            "effective_retention_probability": p_stay, "random_roll": round(roll, 4),
            "realized_churn_probability": 1 - p_stay, "company_churn_estimate": None,
            "churn_estimate_error_pct": None, "retention_offered": False}


def _offered(p_full: float, p_offered: float) -> dict:
    roll = churn_roll_for_renewal(ACCOUNT, DATE)
    return answer_retention_offer(_event(p_full, roll), _event(p_offered, roll),
                                  discount_pct=5.0)


def _rows_for(p_full: float, p_offered: float) -> dict:
    roll = churn_roll_for_renewal(ACCOUNT, DATE)
    assert 0.02 < roll < 0.98, "the fixture needs room on both sides of its roll"
    return {
        "saved": retention_offer_fields(_offered(roll - 0.01, roll + 0.01)),
        "would_have_stayed": retention_offer_fields(_offered(roll + 0.01, roll + 0.02)),
        "left_despite_offer": retention_offer_fields(_offered(roll - 0.02, roll - 0.01)),
        "no_offer": retention_offer_fields(_event(p_full, roll)),
    }


def test_every_branch_of_offer_held_can_be_taken():
    """The control over the whole partition: a grade that never says True passes every refusal."""
    rows = _rows_for(0.5, 0.6)
    assert [r["offer_held"] for r in rows.values()] == [True, False, False, False]


def test_a_saved_household_carries_the_offer_and_both_stay_probabilities():
    roll = churn_roll_for_renewal(ACCOUNT, DATE)
    row = retention_offer_fields(_offered(roll - 0.01, roll + 0.01))
    assert row["retention_offered"] is True
    assert row["retention_discount_pct"] == 5.0
    assert row["p_stay_without_offer"] < roll < row["p_stay_at_offered_rate"]
    assert row["offer_held"] is True


def test_an_offer_to_a_household_that_would_have_stayed_is_not_a_save():
    roll = churn_roll_for_renewal(ACCOUNT, DATE)
    row = retention_offer_fields(_offered(roll + 0.01, roll + 0.02))
    assert row["retention_offered"] is True and row["offer_held"] is False


def test_an_event_without_the_offer_fields_is_unknown_not_no_offer():
    event = _event(0.5, 0.3)
    del event["retention_offered"]
    assert set(retention_offer_fields(event).values()) == {None}


def test_the_sidecar_renewal_row_carries_the_offer():
    """Through the per-account fold the member and control files are written from."""
    roll = churn_roll_for_renewal(ACCOUNT, DATE)
    result = {"phase2b": {"customer_events": [_offered(roll - 0.01, roll + 0.01)]}, "bills": []}
    (renewal,) = _decisions_by_billing_account(result)[ACCOUNT]["renewals"]
    assert renewal["outcome"] == "renewed"
    assert renewal["retention_offered"] is True and renewal["offer_held"] is True
