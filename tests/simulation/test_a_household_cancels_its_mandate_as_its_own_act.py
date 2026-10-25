"""W2_41: a household cancels its Direct Debit mandate as its own act, and the supplier learns of it
the way Bacs tells it -- an ADDACS 1 record on the next working day, ahead of any failed collection.

Knowledge: docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md section 4a.
"""
from __future__ import annotations

import dataclasses
import random
from datetime import date

import pytest

from simulation import bacs_rails as br

FRIDAY = date(2022, 10, 7)
MONDAY = date(2022, 10, 10)


def test_a_cancellation_can_be_drawn_and_can_be_not_drawn():
    """Defect caught: a draw that never fires (or always fires) passes every shape test below."""
    rng = random.Random(41)
    draws = [br.draw_payer_cancellation(f"r{i}", "h1", MONDAY, rng.random(), probability=0.3) for i in range(400)]
    cancelled = [d for d in draws if d is not None]
    assert cancelled and len(cancelled) < len(draws)
    assert 0.2 < len(cancelled) / len(draws) < 0.4


def test_the_unpublished_rate_refuses_by_name_rather_than_drawing_a_number():
    """Defect caught: a placeholder rate standing in for the GAP."""
    assert br.PAYER_CANCELLATION_PROBABILITY is None
    with pytest.raises(ValueError, match="no published rate"):
        br.draw_payer_cancellation("r", "h1", MONDAY, 0.0)


def test_it_crosses_the_seam_only_as_an_addacs_record():
    """Defect caught: the household's act date or private state riding on what the supplier reads."""
    rec = br.draw_payer_cancellation("r1", "h1", FRIDAY, 0.5, probability=1.0)
    assert isinstance(rec, br.AddacsRecord) and not isinstance(rec, br.BacsSubmission)
    assert {f.name for f in dataclasses.fields(rec)} == {
        "reference", "customer_id", "reason_code", "reason", "available_date"}
    assert rec.reason_code == br.ADDACS_PAYER_CANCELLED == 1
    assert "cancelled by payer" in rec.reason.lower()


def test_it_lands_the_next_working_day_before_any_collection_fails():
    """Defect caught: the cancellation found out only through the ARUDD return, a calendar-day lag."""
    rec = br.payer_cancellation("r1", "h1", FRIDAY)
    assert rec.available_date == MONDAY
    # The earliest a collection submitted the same day could come back failed.
    collection = br.submit_collection("c1", "h1", 120.0, FRIDAY)
    returned = br.resolve_submission(collection, "failed", rng=random.Random(0))
    assert rec.available_date < collection.expected_outcome_date <= returned.expected_outcome_date
