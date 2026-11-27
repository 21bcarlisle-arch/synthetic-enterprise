"""A renewal re-asked at an offer is ONE decision in the capture, carrying the outcome the run kept.

Defect named: `tools/capture_departure_factors` appended a row per call of `roll_lifecycle_event`,
so a retention offer or a save re-ask on the same roll became a second decision. Capture r2
(2026-11-27) showed 22 accounts that "depart more than once", and the fitter refused the 2021 refit.
"""
from __future__ import annotations

from tools.capture_departure_factors import (
    REASK_RETENTION_OFFER,
    REASK_SAVE_ON_LOSS_NOTICE,
    DecisionCapture,
)
from tools.departure_population import account_denominator_refusal


def _event(rate: float, event_type: str, *, account="SYN-X", day="2017-12-10") -> dict:
    return {
        "customer_id": account, "event_date": day, "event_type": event_type,
        "churn_probability": 0.05, "company_churn_estimate": None,
        "realized_churn_probability": 0.83, "effective_retention_probability": (
            0.17 if event_type == "churned" else 0.67),
        "departure_cause": "price_position" if event_type == "churned" else None,
        "random_roll": 0.3841,
    }


def _world(answers):
    """A fake `roll_lifecycle_event` answering each successive call from `answers`."""
    it = iter(answers)

    def roll(cid, term_start, commodity, **kwargs):
        return next(it)
    return roll


def _offer(roll_fn, *args, **kwargs):
    """A fake `ask_world_at_offer`: re-asks the world through the roll it is handed."""
    return roll_fn("SYN-X", "2017-12-10", "electricity", new_rate_gbp_per_mwh=129.0)


def test_an_offer_and_a_save_on_one_renewal_are_one_decision_row():
    cap = DecisionCapture()
    roll = cap.wrap(_world([_event(135.7, "churned"), _event(129.0, "renewed"),
                            _event(125.0, "renewed")]))
    offer = cap.wrap_offer(_offer)
    roll("SYN-X", "2017-12-10", "electricity", new_rate_gbp_per_mwh=135.7)
    offer(roll)
    roll("SYN-X", "2017-12-10", "electricity", new_rate_gbp_per_mwh=125.0)
    rows = cap.rows_with_kept_outcome(None)
    assert len(rows) == 1
    assert [r["kind"] for r in rows[0]["reasked_at"]] == [
        REASK_RETENTION_OFFER, REASK_SAVE_ON_LOSS_NOTICE]
    assert rows[0]["new_rate_gbp_per_mwh"] == 135.7  # the decision is at the quoted rate


def test_a_household_kept_by_an_offer_does_not_read_as_a_departure():
    cap = DecisionCapture()
    roll = cap.wrap(_world([_event(135.7, "churned"), _event(129.0, "renewed"),
                            _event(190.0, "churned", day="2024-12-08")]))
    roll("SYN-X", "2017-12-10", "electricity", new_rate_gbp_per_mwh=135.7)
    cap.wrap_offer(_offer)(roll)
    roll("SYN-X", "2024-12-08", "electricity", new_rate_gbp_per_mwh=190.0)
    kept = [{"customer_id": "SYN-X", "event_date": "2017-12-10", "event_type": "renewed"},
            {"customer_id": "SYN-X", "event_date": "2024-12-08", "event_type": "churned"}]
    rows = cap.rows_with_kept_outcome(kept)
    first = rows[0]
    assert first["event_type"] == "renewed"
    assert first["event_type_at_quoted_rate"] == "churned"
    assert first["departure_cause"] is None
    # The SYN-2016-582 shape: left at the quoted rate, kept by the offer, left for real in 2024.
    # One departure. (The fixture's 2018-2023 gap is a different refusal and not this one.)
    assert "more than once" not in (account_denominator_refusal(rows, []) or "")
