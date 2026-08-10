"""The supplier's DD collections desk — the routines the world used to run.

WHAT MOVED, AND WHY IT NEEDS ITS OWN SUITE
-------------------------------------------
KNIFE pass 3, design `B4_billing_mechanics_reached_directly`, last edge. Mandate
registration, the re-estimation that decides when a standing amount has drifted far
enough to write to the customer's bank, and the snap of a collection onto the
customer's own anniversary all used to happen inside
`simulation/dd_collection_book.py`'s loop, against a `DirectDebitBook` the world
opened for itself. They are the supplier's routines and they now live on the
supplier's side, where these tests can reach them directly — before the cut, every
one of them could only be observed through a full world-side rails run.

THE PROPERTY THIS SUITE EXISTS FOR, above the ordinary behaviour checks: **the desk
must not be able to decide whether the money arrived.** A collections desk that
concluded its own outcomes would be the B2 inversion in miniature — the company's
belief constituting the fact it is a belief about — and it would silently flatter
every collection-success figure derived from the register. `record_collection_outcome`
therefore takes `collected` as an argument and has no other route to it; test 9 is
the vacuity guard proving both answers are reachable and the register records what it
was told rather than what it would have guessed.

WHAT IS NOT TESTED HERE. That the desk's arithmetic still matches the pre-cut world
loop is an EQUIVALENCE claim about a moment in history, not a standing property, and
it was proven the way equivalence claims have to be — by running both and comparing
the whole register (74 mandates / 2,220 attempts over a 140-customer, 30-month
population, sha256 identical). Pinning that hash in a test here would be pinning a
generated value: it would fail on the next legitimate change to the routine and would
prove nothing about the routine's correctness. The evidence lives in the register's
§3h and the ledger entry.
"""

from __future__ import annotations

import pytest

from company.billing.dd_collections_desk import (
    AMENDMENT_MATERIALITY_THRESHOLD_GBP,
    AMENDMENT_WINDOW_BILLS,
    DirectDebitCollectionsDesk,
)
from company.interfaces.dd_collection_instructions import open_collections_desk

CID = "CUST-0001"


def _confirmed_desk(monthly=100.0, setup="2024-01-15", payment_day=8, confirmed="2024-01-17"):
    desk = open_collections_desk()
    setup_instruction = desk.open_mandate(CID, monthly, setup, payment_day)
    desk.confirm_mandate(setup_instruction, confirmed)
    return desk


# ── 1-3. A mandate exists when the rails confirm it, and not before ─────────


def test_issuing_a_setup_instruction_registers_nothing():
    """A real mandate exists once AUDDIS confirms it. Registering on issue would make
    the supplier's own record disagree with the bank's."""
    desk = open_collections_desk()
    desk.open_mandate(CID, 100.0, "2024-01-15", 8)
    assert desk.has_mandate(CID) is False


def test_confirmation_registers_the_mandate_with_what_the_rails_reported():
    desk = _confirmed_desk()
    mandate = desk.collection_register().get_mandate(CID)
    assert mandate is not None
    assert mandate.monthly_amount_gbp == 100.0
    assert mandate.payment_day == 8
    assert mandate.setup_date == "2024-01-15"
    assert mandate.setup_rails_reference == f"MANDATE-{CID}-2024-01-15"
    assert mandate.setup_confirmed_date == "2024-01-17"


def test_the_setup_reference_is_the_suppliers_own():
    desk = open_collections_desk()
    instruction = desk.open_mandate(CID, 100.0, "2024-01-15", 8)
    assert instruction.reference == f"MANDATE-{CID}-2024-01-15"
    assert instruction.requested_date == "2024-01-15"


# ── 4-7. The re-estimation routine ──────────────────────────────────────────


def test_no_amendment_without_a_mandate_or_without_history():
    desk = open_collections_desk()
    assert desk.review_amendment(CID, "2024-01-31") is None  # no mandate
    desk = _confirmed_desk()
    assert desk.review_amendment(CID, "2024-01-31") is None  # mandate, no bills yet


def test_one_seasonal_spike_inside_a_steady_window_does_not_amend():
    """The Expert-Hour finding this routine was rebuilt around: comparing a single
    raw bill fired an amendment almost every month for a seasonal customer, which
    models on-demand billing rather than smoothed Variable DD. A median ignores one
    anomalous bill entirely."""
    desk = _confirmed_desk(monthly=100.0)
    for _ in range(8):
        desk.note_billed_amount(CID, 100.0)
    desk.note_billed_amount(CID, 400.0)  # one hard winter
    assert desk.review_amendment(CID, "2024-10-31") is None


def test_a_sustained_step_change_amends_to_the_median_not_the_triggering_bill():
    desk = _confirmed_desk(monthly=100.0)
    for _ in range(3):
        desk.note_billed_amount(CID, 100.0)
    for _ in range(5):  # a majority of the window at the new level
        desk.note_billed_amount(CID, 160.0)
    desk.note_billed_amount(CID, 900.0)  # a wild final bill the amendment must ignore
    amendment = desk.review_amendment(CID, "2024-09-30")
    assert amendment is not None
    assert amendment.new_monthly_amount_gbp == 160.0
    assert amendment.reference.startswith("AMEND-")
    assert amendment.reference.endswith("-2024-09-30")

    desk.confirm_amendment(amendment, "2024-10-02")
    mandate = desk.collection_register().get_mandate(CID)
    assert mandate.monthly_amount_gbp == 160.0
    assert mandate.last_amendment_rails_reference == amendment.reference
    assert mandate.last_amendment_confirmed_date == "2024-10-02"


def test_the_window_is_trailing_so_old_levels_stop_counting():
    """An unbounded all-time average chases a sustained step change forever without
    converging, which is not what an annual re-estimate does."""
    desk = _confirmed_desk(monthly=100.0)
    for _ in range(40):
        desk.note_billed_amount(CID, 100.0)
    for _ in range(AMENDMENT_WINDOW_BILLS):
        desk.note_billed_amount(CID, 175.0)
    amendment = desk.review_amendment(CID, "2026-01-31")
    assert amendment is not None and amendment.new_monthly_amount_gbp == 175.0


def test_the_materiality_floor_binds_in_both_directions():
    """A control whose threshold nothing can reach is vacuously true. Drift just
    inside the floor must NOT fire; drift just outside it must."""
    inside = AMENDMENT_MATERIALITY_THRESHOLD_GBP / 2
    outside = AMENDMENT_MATERIALITY_THRESHOLD_GBP * 2

    quiet = _confirmed_desk(monthly=100.0)
    for _ in range(5):
        quiet.note_billed_amount(CID, 100.0 + inside)
    assert quiet.review_amendment(CID, "2024-06-30") is None

    moved = _confirmed_desk(monthly=100.0)
    for _ in range(5):
        moved.note_billed_amount(CID, 100.0 + outside)
    assert moved.review_amendment(CID, "2024-06-30") is not None


# ── 8. Collection dates snap onto the customer's anniversary ────────────────


@pytest.mark.parametrize("earliest,expected", [
    ("2024-03-01", "2024-03-08"),   # before the day this month
    ("2024-03-08", "2024-03-08"),   # on the day
    ("2024-03-09", "2024-04-08"),   # past it — roll forward, never back
    ("2024-12-20", "2025-01-08"),   # year boundary
])
def test_a_collection_is_never_pulled_earlier_than_the_bill_is_due(earliest, expected):
    desk = _confirmed_desk(payment_day=8)
    instruction = desk.instruct_collection(CID, "2024-02-29", 123.45, earliest)
    assert instruction.collection_date == expected
    assert instruction.amount_gbp == 123.45  # Variable DD: the bill sizes the collection
    assert instruction.reference.endswith("-2024-02-29")


def test_the_mandates_reference_amount_never_sizes_a_collection():
    """Variable DD. The stored `monthly_amount_gbp` is an estimated reference level
    that only decides when a re-estimation notice fires."""
    desk = _confirmed_desk(monthly=50.0)
    instruction = desk.instruct_collection(CID, "2024-02-29", 321.0, "2024-03-01")
    assert instruction.amount_gbp == 321.0


# ── 9. The desk records what it is TOLD about the money ─────────────────────


@pytest.mark.parametrize("collected,reason,outcome", [
    (True, "", "collected"),
    (False, "ARUDD 0: refer to payer", "failed"),
])
def test_the_outcome_recorded_is_the_one_reported(collected, reason, outcome):
    """The vacuity guard for the property in this module's docstring: both answers are
    reachable and the register stores what the world reported, so a desk that
    concluded its own outcomes would show up here as one of these two failing."""
    desk = _confirmed_desk()
    instruction = desk.instruct_collection(CID, "2024-02-29", 99.5, "2024-03-01")
    desk.record_collection_outcome(
        instruction, attempt_date="2024-03-11", collected=collected, failure_reason=reason
    )
    attempts = desk.collection_register().all_attempts()
    assert len(attempts) == 1
    assert attempts[0].outcome == outcome
    assert attempts[0].failure_reason == reason
    assert attempts[0].attempt_date == "2024-03-11"
    assert attempts[0].amount_gbp == 99.5


# ── 10. Fail CLOSED on a missing mandate ────────────────────────────────────


def test_instructing_or_recording_without_a_mandate_raises():
    """FAIL-OPEN is the R15 pattern that would bite here: silently returning None, or
    dropping the attempt, would lose collections from the register while every
    aggregate still looked plausible."""
    desk = open_collections_desk()
    with pytest.raises(ValueError):
        desk.instruct_collection(CID, "2024-02-29", 10.0, "2024-03-01")

    live = _confirmed_desk()
    instruction = live.instruct_collection(CID, "2024-02-29", 10.0, "2024-03-01")
    with pytest.raises(ValueError):
        open_collections_desk().record_collection_outcome(
            instruction, attempt_date="2024-03-11", collected=True
        )


def test_the_seam_hands_back_a_real_desk():
    assert isinstance(open_collections_desk(), DirectDebitCollectionsDesk)
