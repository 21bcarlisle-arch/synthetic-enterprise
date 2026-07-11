"""Bacs Direct Debit rails physics -- the "rails sim first" step of M2
(THE_VALUE_CYCLE_FRAMING.md, Banking & Payment Rails simulator,
maturity_map.yaml W5_1_banking_payment_rails).

Real UK Bacs mechanics (WebSearch-verified, 2026-07-11, sources:
Pay.UK's own "Bacs System Principles" guide + AccessPaySuite/Hafiz Didarali
reason-code references -- not invented):

- Bacs runs a fixed 3-working-day processing cycle for a Direct Debit
  collection: Day 1 the instruction is picked up and submitted; Day 2 it
  processes at Bacs; Day 3 is collection day, when money actually moves.
- AUDDIS (Automated Direct Debit Instruction Service): electronic mandate
  SETUP. Confirmation/rejection responses arrive on Day 2 of that
  instruction's own cycle.
- ADDACS (Automated Direct Debit Amendment and Cancellation Service):
  mandate AMENDMENTS/cancellations after setup, same 3-day cycle.
- ARUDD (Automated Return of Unpaid Direct Debit): a FAILED collection is
  reported back up to 2 working days AFTER the collection day (i.e. the
  company doesn't learn a DD failed until collection_date + up to 2 days),
  not instantly -- this lag is the actual "cash lands when the rails say"
  physics the framing names.

This module does NOT decide WHETHER a payment succeeds or fails -- that
real, calibrated, stress-tier-anchored behavioural model already exists
(simulation/arrears_engine.py::payment_outcome()) and duplicating it here
would violate R13 (the baseline/curriculum split: behavioural probability
belongs to that anchored model, not a second one invented for this rails
layer). This module's job is strictly the RAILS PHYSICS around an
ALREADY-DECIDED outcome: realistic multi-day timing, and (for failures) a
realistic AUDDIS/ARUDD reason code -- the part that was "entirely absent"
per the M2 payments-maturity audit finding
(docs/design/M2_PAYMENTS_AUDIT_DD_RAILS.md).

Adapter-shaped (THE_VALUE_CYCLE_FRAMING.md's own instruction): company-side
code calls submit_*() to get a pending submission (only a reference +
expected-outcome-date -- no early knowledge of the result), then later
resolve_due_submissions() to find out what actually happened, exactly
mirroring what a real supplier's Bacs integration would see. Full
typed/versioned hardening of this seam is registered Epoch-3 work (already
noted on W5_1_banking_payment_rails's own wall-adapter-inventory entry);
this is the physics engine behind that future seam, not the seam itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal, Optional

BACS_PROCESSING_DAYS = 3          # submission -> collection day
ARUDD_NOTIFICATION_LAG_DAYS = 2   # collection day -> failure known, at most
AUDDIS_CONFIRMATION_DAYS = 2      # mandate submission -> setup confirmed/rejected

SubmissionType = Literal["mandate_setup", "collection", "amendment"]
SubmissionStatus = Literal["pending", "success", "failed"]

# Real AUDDIS/ARUDD reason codes (WebSearch-verified against AccessPaySuite's
# and Hafiz Didarali's Bacs reason-code references, 2026-07-11) -- not
# invented. ARUDD 0 ("Refer to Payer") is the real-world dominant failure
# code for ordinary insufficient-funds-class DD failures; the existing
# behavioural model (payment_outcome()) does not carry a "why" signal
# beyond success/failed/dispute, so failures are mapped to this dominant
# real code rather than a fabricated even split across all real codes --
# an honest approximation, not false precision.
ARUDD_REASON_CODES = {
    0: "Refer to Payer",       # insufficient funds -- real-world dominant cause
    1: "Instruction Cancelled",
    2: "Payer Deceased",
    3: "Account Transferred",
}
AUDDIS_REASON_CODES = {
    1: "Instruction Cancelled By Payer",
    2: "Payer Deceased",
    3: "Account Transferred",
    5: "No Account",
}


@dataclass(frozen=True)
class BacsSubmission:
    """One item submitted into the rails -- a mandate setup, a collection
    attempt, or an amendment. `outcome`/`reason_code` are None until
    resolve_due_submissions() processes it; a caller reading this object
    before its own expected_outcome_date is looking at exactly what a real
    supplier would see: submitted, not yet known."""
    reference: str
    submission_type: SubmissionType
    customer_id: str
    submission_date: date
    amount_gbp: Optional[float]  # None for mandate_setup/amendment
    expected_outcome_date: date
    status: SubmissionStatus = "pending"
    reason_code: Optional[int] = None


def _outcome_date(submission_type: SubmissionType, submission_date: date) -> date:
    if submission_type == "mandate_setup":
        return submission_date + timedelta(days=AUDDIS_CONFIRMATION_DAYS)
    if submission_type == "amendment":
        return submission_date + timedelta(days=AUDDIS_CONFIRMATION_DAYS)
    # collection: money moves on Day 3; a FAILURE isn't known until up to
    # ARUDD_NOTIFICATION_LAG_DAYS after that -- resolve_due_submissions()
    # applies the extra lag only when the underlying outcome is a failure,
    # since a successful collection is confirmed on collection day itself.
    return submission_date + timedelta(days=BACS_PROCESSING_DAYS)


def submit_mandate_setup(reference: str, customer_id: str, submission_date: date) -> BacsSubmission:
    return BacsSubmission(
        reference=reference, submission_type="mandate_setup", customer_id=customer_id,
        submission_date=submission_date, amount_gbp=None,
        expected_outcome_date=_outcome_date("mandate_setup", submission_date),
    )


def submit_amendment(reference: str, customer_id: str, submission_date: date) -> BacsSubmission:
    return BacsSubmission(
        reference=reference, submission_type="amendment", customer_id=customer_id,
        submission_date=submission_date, amount_gbp=None,
        expected_outcome_date=_outcome_date("amendment", submission_date),
    )


def submit_collection(reference: str, customer_id: str, amount_gbp: float, submission_date: date) -> BacsSubmission:
    return BacsSubmission(
        reference=reference, submission_type="collection", customer_id=customer_id,
        submission_date=submission_date, amount_gbp=amount_gbp,
        expected_outcome_date=_outcome_date("collection", submission_date),
    )


def resolve_submission(submission: BacsSubmission, decided_outcome: Literal["success", "failed"],
                        rng=None) -> BacsSubmission:
    """Apply an ALREADY-DECIDED behavioural outcome (from
    simulation/arrears_engine.py::payment_outcome() for a collection, or the
    caller's own mandate-setup/amendment logic) and return the resolved
    BacsSubmission with realistic rails timing + reason code.

    For a failed collection, the true notification date is later than
    `expected_outcome_date` (which is collection day) by up to
    ARUDD_NOTIFICATION_LAG_DAYS -- this is the actual "cash lands when the
    rails say" lag the framing names. `rng` (a random.Random, optional)
    picks the exact lag within that real window; omit for a deterministic
    worst-case (full lag applied), never a fabricated instant-fail."""
    if decided_outcome == "success":
        return BacsSubmission(
            reference=submission.reference, submission_type=submission.submission_type,
            customer_id=submission.customer_id, submission_date=submission.submission_date,
            amount_gbp=submission.amount_gbp, expected_outcome_date=submission.expected_outcome_date,
            status="success", reason_code=None,
        )

    reason_codes = AUDDIS_REASON_CODES if submission.submission_type in ("mandate_setup", "amendment") else ARUDD_REASON_CODES
    # Always the documented dominant real-world code (see module docstring),
    # deliberately NOT `rng`-randomised across the full code set: no sourced
    # real-world frequency split between "Refer to Payer"/"Payer Deceased"/
    # etc. exists in this codebase, and a uniform random pick would make a
    # genuinely rare code (Payer Deceased) appear far more often than real
    # life -- less honest than a fixed dominant code, not more (R12/R13:
    # never fabricate a distribution that can't be anchored).
    reason_code = 0 if 0 in reason_codes else next(iter(reason_codes))

    outcome_date = submission.expected_outcome_date
    if submission.submission_type == "collection":
        lag_days = rng.randint(0, ARUDD_NOTIFICATION_LAG_DAYS) if rng is not None else ARUDD_NOTIFICATION_LAG_DAYS
        outcome_date = outcome_date + timedelta(days=lag_days)

    return BacsSubmission(
        reference=submission.reference, submission_type=submission.submission_type,
        customer_id=submission.customer_id, submission_date=submission.submission_date,
        amount_gbp=submission.amount_gbp, expected_outcome_date=outcome_date,
        status="failed", reason_code=reason_code,
    )


def resolve_due_submissions(submissions: list[BacsSubmission], decided_outcomes: dict[str, Literal["success", "failed"]],
                             rng=None) -> list[BacsSubmission]:
    """Batch form of resolve_submission() -- resolves every submission in
    `submissions` whose reference has a decided outcome in `decided_outcomes`
    (keyed by reference), leaving anything not yet decided untouched
    (still "pending", exactly as a real Bacs integration's unresolved queue
    would look)."""
    resolved = []
    for sub in submissions:
        if sub.reference in decided_outcomes:
            resolved.append(resolve_submission(sub, decided_outcomes[sub.reference], rng=rng))
        else:
            resolved.append(sub)
    return resolved
