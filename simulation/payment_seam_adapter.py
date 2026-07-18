"""W2_11 payment SEAM ADAPTER -- the SIM-SIDE implementation that FILLS the
just-landed W4_4 seam contract (`interface/contracts/payment_observable_seam.py`)
from the W2_11 generator's ground truth (`simulation/payment_behaviour_source.py`).
Coupled-triad piece: W2_11 source / **W4_4 seam (this module fills it)** / D5
consumption / H27 gap.

WHAT THIS IS
------------
The ONE place in the whole system allowed to see BOTH the generator's hidden
TRUTH (`PaymentEvent.result`, `.dd_failure_reason`, and -- via the caller's
own context, never through this module -- the customer's true stress/segment)
AND produce the OBSERVABLE `WallResponse` payloads a real bank/Bacs feed
would actually report. That makes it the wall's single most sensitive piece
of code: everything it EMITS must answer YES to "could a real UK energy
supplier's bank/Bacs systems have reported this?" -- never carry the
generator's internal reasoning, segment, pattern classification, or a
probability (`interface/contracts/payment_observable_seam.py`'s own
docstring states this guarantee; this module is the one place obligated to
honour it in code, not just in the contract's prose).

THE MAPPING (truth -> observable) -- THIS IS THE WALL
------------------------------------------------------
* SUCCESS (any payment method) -> `RemittanceAdvice`. Rail-agnostic "money
  landed" observation; `value_date` is the REAL clearing date
  (`PaymentEvent.payment_date`, which may be late), never the due date.
  DELIBERATELY no `BacsArruddOutcome(outcome=SUCCESS)` is also emitted for a
  successful DD -- real ARUDD is a RETURN-only report (per
  `simulation/bacs_rails.py`'s own documented mechanics: "a successful
  collection is confirmed on collection day itself" with no separate ARUDD
  line); fabricating a `BacsArruddOutcome` for a non-failure would force an
  artificial `reason_category` onto a dataclass whose every enum member is a
  FAILURE reason -- less honest than simply relying on `RemittanceAdvice`
  (see module honesty note in the returned report for this deviation from a
  literal "and/or" reading of the FRAME).
* FAILED Direct Debit -> `BacsArruddOutcome(outcome=FAILURE,
  reason_category=<mapped code>)`. `dd_failure_reason` (the generator's own
  ANCHORED-estimate binary split, see that module's docstring) maps to the
  seam's `BacsReasonCategory` via `_DD_FAILURE_REASON_TO_BACS_CATEGORY`
  below -- see that mapping's own docstring for the many-to-one collapse
  argument (the wall point).
* FAILED non-DD (standing_order / card / prepayment) -> **NO RESPONSE**
  (the no-remittance blind spot, C-S3). Real DD collection is a
  company-INITIATED PULL with an explicit ARUDD return; a missed
  standing-order or card top-up is a customer-INITIATED PUSH with no
  equivalent "your customer's payment failed" report arriving at the
  supplier -- the supplier only ever observes the absence of the expected
  remittance. Modelling a synthetic decline notice for these rails would be
  fabricating an observable that no real UK supplier's systems receive.
* DISPUTE (any rail) -> `WallResponse(status=NOT_KNOWABLE_YET, payload=None)`.
  Distinct from the blind spot above: a dispute is an ACTIVELY CONTESTED
  collection (arrears_engine's I&C/SME "dispute" outcome), so the bank feed
  genuinely has *something* open on it, but this generator, honestly, has no
  further resolution to report at generation time -- `NOT_KNOWABLE_YET` is
  the envelope's own first-class "honest not-yet-known" answer
  (`wall_envelope.WallStatus`), carrying zero payload, so it cannot leak
  anything even in principle (`WallResponse.__post_init__` enforces
  payload=None off any non-OK status).

NON-INVERTIBILITY (the wall's load-bearing property)
-----------------------------------------------------
`PaymentEvent` itself never carries the customer's true stress tier,
segment, or `classify_payment_pattern()` classification -- those live only
in the generator's OWN inputs/derived objects
(`generate_payment_event`'s `stress`/`segment` args,
`CustomerPaymentProfile.pattern`), which this module never receives and
never touches. Structurally, this adapter CANNOT leak them. Additionally,
`payment_behaviour_source._DD_FAILURE_REASON_SPLIT` is drawn from a fixed
85/15 probability applied IDENTICALLY regardless of the customer's stress
tier (the reason substream is keyed only by customer_id + period_index, not
by stress -- see that module's `generate_payment_event`) -- so two
customers in genuinely different true circumstances (e.g. one in real
income hardship, one having a one-off unrelated blip) that both happen to
draw `dd_failure_reason=INSUFFICIENT_FUNDS` are, by the generator's own
construction, INDISTINGUISHABLE at that point -- this module's mapping only
makes that pre-existing collapse visible at the seam, it does not invent it.

ASYNC / BITEMPORAL (C-S3)
--------------------------
`observed_at` (when the bank feed reports the fact) is kept separate from
`value_date` (what date the payload is about), reusing
`simulation.bacs_rails.ARUDD_NOTIFICATION_LAG_DAYS` (the real, already-cited
Pay.UK-anchored ~2-working-day ARUDD reporting lag) rather than re-deriving
a duplicate constant (R13 reuse discipline). A DD FAILURE's `observed_at`
lands `0..ARUDD_NOTIFICATION_LAG_DAYS` after `value_date`; a SUCCESS
(any rail) is observed same-day as its `value_date` (confirmed on the bank
statement the day money moves, no extra lag -- matching bacs_rails.py's own
documented "a successful collection is confirmed on collection day itself").

DETERMINISM (C-S2)
-------------------
The one random draw this module makes (which exact day, within the real
ARUDD lag window, a failure is reported) comes from its OWN named, seeded
substream (`_adapter_substream`), mirroring the exact stable-sha256 pattern
`payment_behaviour_source._substream` uses, under this module's OWN
`_STREAM_NAMESPACE` (never payment_behaviour_source's, never the shared
`random` module) -- keyed by `(customer_id, period_index)`, so this
module's draws can never shift, or be shifted by, any other subsystem's
sequence. Because the key is derived entirely from stable fields already on
`PaymentEvent`, this module needs no external `seed` argument threaded
through calls to be deterministic: the same `PaymentEvent` always produces
the same lag draw, and therefore the same `WallResponse` -- idempotent
replay (C-S2) falls out of the design rather than needing a separate seed
parameter to be remembered/passed correctly.

WALL DISCIPLINE (.claude/rules/epistemic-wall-sim.md)
------------------------------------------------------
Pure WORLD/sim code. Reads `simulation.payment_behaviour_source` and
`simulation.bacs_rails` (both read-only imports, unmodified) and the
`interface.contracts.*` seam types (read-only import; this module fills the
contract, it does not define it). Never imports `company.*` / `saas.*`.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import List, Optional

from interface.contracts.payment_observable_seam import (
    BacsArruddOutcome,
    BacsReasonCategory,
    DDOutcomeStatus,
    PaymentRail,
    RemittanceAdvice,
    SCHEMA_VERSION,
)
from interface.contracts.wall_envelope import WallResponse, WallStatus
from simulation.bacs_rails import ARUDD_NOTIFICATION_LAG_DAYS
from simulation.payment_behaviour_source import (
    CANCELLED_OTHER,
    CARD,
    DIRECT_DEBIT,
    INSUFFICIENT_FUNDS,
    PREPAYMENT,
    STANDING_ORDER,
    PaymentEvent,
)

_STREAM_NAMESPACE = "W2_11_payment_seam_adapter"

# The hour-of-day a bank/Bacs feed is treated as reporting at -- an early
# morning batch file drop, the real-world norm for bank statement/Bacs
# report feeds. Fixed (not drawn), since the exact hour carries no
# information a company system would act differently on.
_BANK_FEED_REPORT_HOUR = 6


def _adapter_substream(customer_id: str, period_index: int, name: str) -> random.Random:
    """Isolated, stable substream for this adapter's own draws (C-S2).
    Mirrors `payment_behaviour_source._substream`'s sha256-stable-seed
    pattern exactly, under this module's OWN namespace, so a draw here can
    never collide with, or shift, any other subsystem's sequence."""
    key = f"{_STREAM_NAMESPACE}::{name}::{customer_id}::{period_index}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _observed_at(value_date: date, *, lag_days: int = 0) -> datetime:
    return datetime.combine(value_date + timedelta(days=lag_days), time(hour=_BANK_FEED_REPORT_HOUR))


# ---------------------------------------------------------------------------
# Payment-method -> rail. PREPAYMENT has no dedicated `PaymentRail` member
# (the seam contract enumerates rail MECHANISMS, not payment instruments);
# mapped honestly to `PaymentRail.OTHER` rather than inventing/overloading an
# existing member (this module may not edit the contract to add one).
# ---------------------------------------------------------------------------
_PAYMENT_METHOD_TO_RAIL = {
    DIRECT_DEBIT: PaymentRail.BACS_DIRECT_DEBIT,
    STANDING_ORDER: PaymentRail.STANDING_ORDER,
    CARD: PaymentRail.CARD,
    PREPAYMENT: PaymentRail.OTHER,
}


def payment_rail_for_method(payment_method: str) -> PaymentRail:
    """Map the generator's payment-method label to the seam's rail enum."""
    return _PAYMENT_METHOD_TO_RAIL.get(payment_method, PaymentRail.OTHER)


# ---------------------------------------------------------------------------
# Truth -> observable reason-code mapping -- THE WALL.
#
# The generator (`payment_behaviour_source._DD_FAILURE_REASON_SPLIT`) only
# distinguishes two ANCHORED-estimate reasons (see that module's own
# docstring: direction sourced from bacs_rails.py's ARUDD-dominant-code
# citation, exact split an estimate). Real Bacs ARUDD covers a wider code
# set than either module reproduces (R10 gap, honestly labelled, not
# fabricated -- see `BacsReasonCategory`'s own docstring). This mapping is
# deliberately NARROW (2 -> 2, not fanned out to invent unsourced precision)
# -- the many-to-one collapse this atom's wall guarantee rests on is NOT
# "many generator reasons -> one code" (the generator itself only has two),
# it is "many different TRUE CUSTOMER CIRCUMSTANCES (stress tier, segment,
# life event, chronic-vs-transient pattern) that are NEVER PART OF
# `PaymentEvent` AND NEVER CONDITION THE REASON DRAW ITSELF (the reason
# substream is keyed only by customer_id + period_index, independent of
# stress) -> the SAME observable code". See module docstring
# "NON-INVERTIBILITY" section and the adapter test's many-to-one assertion.
# ---------------------------------------------------------------------------
_DD_FAILURE_REASON_TO_BACS_CATEGORY = {
    INSUFFICIENT_FUNDS: BacsReasonCategory.INSUFFICIENT_FUNDS,
    CANCELLED_OTHER: BacsReasonCategory.INSTRUCTION_CANCELLED,
}

# Bank-observable report TEXT per category -- describes the OBSERVABLE code
# itself (what a real Bacs report line would say), never the generator's
# internal reason label or any customer circumstance.
_REASON_CATEGORY_TEXT = {
    BacsReasonCategory.INSUFFICIENT_FUNDS: "Refer to Payer",
    BacsReasonCategory.INSTRUCTION_CANCELLED: "Instruction Cancelled",
    BacsReasonCategory.ACCOUNT_CLOSED: "Account Closed",
    BacsReasonCategory.NO_ACCOUNT: "No Account",
    BacsReasonCategory.PAYER_DECEASED: "Payer Deceased",
    BacsReasonCategory.MANDATE_DISPUTED: "Mandate Disputed",
    BacsReasonCategory.AMOUNT_DIFFERS: "Amount Differs",
    BacsReasonCategory.ADVANCE_NOTICE_INVALID: "Advance Notice Invalid",
    BacsReasonCategory.OTHER: "Other",
}


def bacs_reason_category_for(dd_failure_reason: Optional[str]) -> BacsReasonCategory:
    """Map the generator's `dd_failure_reason` to the seam's
    `BacsReasonCategory`. Fail-closed-safe: an unrecognised/missing value
    maps to `OTHER` rather than raising or fabricating a specific code --
    never crash the seam on an unexpected generator value, never invent
    unlabelled precision either."""
    return _DD_FAILURE_REASON_TO_BACS_CATEGORY.get(dd_failure_reason, BacsReasonCategory.OTHER)


def _default_correlation_id(event: PaymentEvent) -> str:
    return f"{event.customer_id}::{event.period_index}"


def _default_account_id(event: PaymentEvent) -> str:
    return f"ACC-{event.customer_id}"


def _default_mandate_ref(event: PaymentEvent, account_id: str) -> str:
    return f"MANDATE-{account_id}"


@dataclass(frozen=True)
class SeamAdapterInput:
    """Optional caller-supplied identifiers a real Bacs/bank feed would
    carry (account/mandate references) -- these are COMPANY-owned data the
    adapter does not invent from generator internals; if omitted, a
    deterministic placeholder derived from `customer_id` is used (test/dev
    convenience only -- a real caller normally supplies its own account and
    mandate references)."""

    account_id: Optional[str] = None
    mandate_ref: Optional[str] = None
    correlation_id: Optional[str] = None


def emit_wall_responses(
    event: PaymentEvent,
    seam_input: Optional[SeamAdapterInput] = None,
) -> List[WallResponse]:
    """THE adapter function: map one generator `PaymentEvent` (truth) to the
    list of `WallResponse` objects a real bank/Bacs feed would produce
    (observable) -- zero, one, or (in principle, not currently) more than
    one response. Never mutates or reads anything beyond the `PaymentEvent`
    and the optional caller-supplied identifiers.

    Returns:
      * SUCCESS  -> [WallResponse[RemittanceAdvice]]
      * FAILED + DIRECT_DEBIT rail -> [WallResponse[BacsArruddOutcome]]
      * FAILED + any other rail -> []  (the no-remittance blind spot, C-S3)
      * DISPUTE -> [WallResponse(status=NOT_KNOWABLE_YET, payload=None)]
    """
    seam_input = seam_input or SeamAdapterInput()
    account_id = seam_input.account_id or _default_account_id(event)
    mandate_ref = seam_input.mandate_ref or _default_mandate_ref(event, account_id)
    correlation_id = seam_input.correlation_id or _default_correlation_id(event)
    rail = payment_rail_for_method(event.payment_method)
    due = date.fromisoformat(event.due_date)

    if event.result == "success":
        value_date = date.fromisoformat(event.payment_date) if event.payment_date else due
        payload = RemittanceAdvice(
            bank_reference=correlation_id,
            account_id=account_id,
            amount_gbp=event.amount_gbp,
            rail=rail,
            value_date=value_date,
        )
        return [
            WallResponse(
                correlation_id=correlation_id,
                status=WallStatus.OK,
                schema_version=SCHEMA_VERSION,
                observed_at=_observed_at(value_date),
                valid_time=value_date,
                payload=payload,
            )
        ]

    if event.result == "dispute":
        return [
            WallResponse(
                correlation_id=correlation_id,
                status=WallStatus.NOT_KNOWABLE_YET,
                schema_version=SCHEMA_VERSION,
                observed_at=_observed_at(due),
                valid_time=None,
                payload=None,
            )
        ]

    # event.result == "failed"
    if event.payment_method != DIRECT_DEBIT:
        # No-remittance blind spot: a real supplier's systems see nothing at
        # all for a missed push-payment rail -- absence, never a placeholder.
        return []

    reason_category = bacs_reason_category_for(event.dd_failure_reason)
    lag_rng = _adapter_substream(event.customer_id, event.period_index, "arudd_lag")
    lag_days = lag_rng.randint(0, ARUDD_NOTIFICATION_LAG_DAYS)
    payload = BacsArruddOutcome(
        mandate_ref=mandate_ref,
        account_id=account_id,
        amount_gbp=event.amount_gbp,
        outcome=DDOutcomeStatus.FAILURE,
        reason_category=reason_category,
        reason_text=_REASON_CATEGORY_TEXT[reason_category],
        value_date=due,
    )
    return [
        WallResponse(
            correlation_id=correlation_id,
            status=WallStatus.OK,
            schema_version=SCHEMA_VERSION,
            observed_at=_observed_at(due, lag_days=lag_days),
            valid_time=due,
            payload=payload,
        )
    ]


def emit_wall_responses_batch(
    events,
    seam_input_for=None,
) -> List[WallResponse]:
    """Batch form: flattens `emit_wall_responses` across a sequence of
    `PaymentEvent`s. `seam_input_for`, if given, is a callable
    `PaymentEvent -> Optional[SeamAdapterInput]` (defaults applied per-event
    when it returns `None` or is itself `None`)."""
    responses: List[WallResponse] = []
    for event in events:
        seam_input = seam_input_for(event) if seam_input_for is not None else None
        responses.extend(emit_wall_responses(event, seam_input))
    return responses
