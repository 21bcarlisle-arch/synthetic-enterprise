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
from dataclasses import dataclass, fields
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import List, Optional

from interface.contracts.payment_observable_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_PAYLOAD_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    SCHEMA_VERSION,
    BacsArruddOutcome,
    BacsReasonCategory,
    DDOutcomeStatus,
    PaymentRail,
    RemittanceAdvice,
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


# ---------------------------------------------------------------------------
# THE WIRE (atom EP6_wall_protocol_typing, 2026-08-19) -- the counterparty's
# OWN encoder.
#
# WHY THIS LIVES HERE AND NOT IN THE COMPANY'S CODEC. EP6's claim is that "a
# mock counterparty and a real one are indistinguishable to the company". That
# claim is only testable if the mock produces its bytes with its OWN code. If
# this module called `company.interfaces.wall_protocol.encode_response` and the
# consumer decoded with the same module, the round-trip would be a TAUTOLOGY in
# the R15 sense -- the decoder checked against its own arithmetic -- and would
# stay green through a schema change that no real counterparty would have made.
# It is also forbidden outright: this module never imports `company.*`/`saas.*`
# (module docstring), exactly as a real bank never links the supplier's library.
#
# WHAT MAKES THE TWO SIDES AGREE, THEN, IS THE CONTRACT AND ONLY THE CONTRACT:
# both read `interface.contracts.payment_observable_seam` -- the payload
# dataclasses and `OBSERVABLE_RESPONSE_PAYLOAD_TYPES` -- the way a real
# counterparty reads a published schema. A field added to a payload therefore
# reaches both sides at once, and a field one side invents reaches neither.
#
# ABSENCE IS NEVER AGREEMENT applies to the encoder too: every field is written
# including its nulls, `schema_version` is written from the CONTRACT's constant
# (never from a reader's default), and a payload type or field type this seam
# does not define is REFUSED rather than stringified. An encoder that can
# serialise anything is the mirror of a decoder that can accept anything.
# ---------------------------------------------------------------------------

_ENCODABLE_PAYLOAD_TYPES = {t.__name__: t for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES}


class SeamEncodeError(ValueError):
    """This seam refused to put a value on the wire. Deliberately NOT
    `WallProtocolError`: that type is the company's, and a counterparty does
    not raise the receiver's exceptions."""


def _encode_scalar(value, field: str):
    """Encode one payload field. Refuses an unhandled type rather than
    coercing -- `str(value)` here is how a rail silently ships an object's
    repr and the receiver silently accepts a string."""
    if isinstance(value, Enum):
        return value.value
    # datetime is a date subclass; these payloads carry DATES, and a datetime
    # smuggled into one would decode back as a different type on the far side.
    if isinstance(value, datetime):
        raise SeamEncodeError(f"{field}: payload fields are dates, got a datetime")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool):
        raise SeamEncodeError(f"{field}: bool is not a seam payload field type")
    if isinstance(value, (int, float, str)):
        return value
    raise SeamEncodeError(
        f"{field}: {type(value).__name__} has no defined wire form on this seam"
    )


def encode_observable_payload(payload) -> dict:
    """Put one observable payload on the wire, TAGGED with its type.

    The tag is required because `WallResponse.payload` is opaque to the
    envelope codec: six payload types cross this seam, and a receiver that
    guessed from the field set would silently mis-route the day two payloads
    happened to share a shape.

    TWO BELTS, AND ONLY ONE OF THEM IS THE CONTROL.
    `OBSERVABLE_PAYLOAD_FIELDS` is the control: it asks the closed question --
    is every field on this payload one the contract has DECLARED observable --
    so a field added to a dataclass and nothing else is refused HERE, at the
    point of emission, because it was never declared rather than because
    someone predicted its name (R10).
    `FORBIDDEN_TRUTH_FIELDS` is the SECOND belt. It answers the strictly
    narrower "did we think of this name", and is kept for the one case the
    closed set cannot see: a truth field added to the dataclass AND declared
    observable in the same edit, which moves the very thing the control reads.
    """
    payload_type = type(payload)
    if payload_type.__name__ not in _ENCODABLE_PAYLOAD_TYPES or (
        _ENCODABLE_PAYLOAD_TYPES[payload_type.__name__] is not payload_type
    ):
        raise SeamEncodeError(
            f"{payload_type.__name__} is not one of this seam's "
            f"OBSERVABLE_RESPONSE_PAYLOAD_TYPES {sorted(_ENCODABLE_PAYLOAD_TYPES)}"
        )
    names = [f.name for f in fields(payload)]
    # DENYLIST FIRST, deliberately -- the same ordering, for the same reason, that
    # `sim/flex_dispatch.py` states: when a field is both undeclared AND a name the
    # contract already knows leaks truth, the truth-leak message is the more
    # diagnostic of the two. Ordering also keeps the two belts separately
    # observable, so each can have a test that only passes if ITS check fired.
    leaking = sorted(set(names) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise SeamEncodeError(
            f"{payload_type.__name__} declares forbidden truth field(s) {leaking} -- the "
            "world's own hidden quantities (the true failure reason, the hidden "
            "ability/willingness quadrant, the generator's clock) may never cross this "
            "seam, whatever the contract has declared observable"
        )
    declared = OBSERVABLE_PAYLOAD_FIELDS.get(payload_type.__name__)
    if declared is None:
        raise SeamEncodeError(
            f"{payload_type.__name__} has no OBSERVABLE_PAYLOAD_FIELDS declaration -- "
            "a payload type the contract has not certified field-by-field may not cross"
        )
    undeclared = sorted(set(names) - set(declared))
    if undeclared:
        raise SeamEncodeError(
            f"{payload_type.__name__} declares field(s) {undeclared} the contract has not "
            "declared observable -- widen OBSERVABLE_PAYLOAD_FIELDS only after answering "
            "'could a real supplier read this off its own bank/Bacs report alone?'"
        )
    absent = sorted(set(declared) - set(names))
    if absent:
        raise SeamEncodeError(
            f"{payload_type.__name__} omits declared observable field(s) {absent} -- the "
            "contract's declaration has gone stale against the payload it certifies"
        )
    return {
        "payload_type": payload_type.__name__,
        "fields": {
            name: _encode_scalar(getattr(payload, name), f"{payload_type.__name__}.{name}")
            for name in names
        },
    }


def encode_wall_response(response: WallResponse) -> dict:
    """Serialise one `WallResponse` into the wire form this seam publishes.

    Written against the SCHEMA, not against the company's decoder: the key set
    below is the response schema as this seam documents it, and if the company
    widens its own expectation without the schema changing, this encoder keeps
    emitting the old shape and the far side refuses it -- which is the correct
    outcome and the whole reason the two sides are separate code.
    """
    if not isinstance(response, WallResponse):
        raise SeamEncodeError(f"expected a WallResponse, got {type(response).__name__}")
    return {
        "correlation_id": response.correlation_id,
        "status": response.status.value,
        "schema_version": SCHEMA_VERSION,
        "observed_at": response.observed_at.isoformat(),
        "valid_time": None if response.valid_time is None else response.valid_time.isoformat(),
        "payload": (
            None if response.payload is None else encode_observable_payload(response.payload)
        ),
        "error": (
            None
            if response.error is None
            else {"code": response.error.code, "message": response.error.message}
        ),
    }


# ---------------------------------------------------------------------------
# THE TRANSPORT FRAME (atom EP6_wall_protocol_typing, pass 39, 2026-08-20) --
# this counterparty saying who it is.
#
# The 2026-08-20 blind review's Q13 found that the company would decode a
# well-formed envelope from anybody, because no participant identity existed
# anywhere below the port. The repair has two halves and this is the SENDER's:
# every message this seam publishes now travels inside a frame naming the
# participant and presenting its credential. The company holds only a
# FINGERPRINT of that credential, in its own registry, in its own module -- so
# neither side reads the other's value at runtime and the check is a real one
# rather than a handshake with itself.
#
# ROTATING `PARTICIPANT_CREDENTIAL` here without updating the company's
# registry BREAKS THIS SEAM, deliberately. That is what a participant changing
# its key without telling its counterparty does on a real network, and a
# version of this that kept working would not be checking anything.
#
# NOT A SECRET IN THE SECRETS SENSE: this is a stand-in bank's synthetic
# credential inside a simulation, with no real-world counterparty and (by
# `tools/company_network_isolation.py`) no route to one. It is a literal here
# for the same reason the rest of this stand-in's behaviour is: it is world
# state, not configuration.
# ---------------------------------------------------------------------------

#: This counterparty's participant identity, as the company's registry knows it.
PARTICIPANT_ID = "BACS-BUREAU-01"

#: What this participant presents to prove that identity. The company stores
#: sha256 of this string and never the string itself.
PARTICIPANT_CREDENTIAL = "bacs-bureau-01::participant-credential::v1"


def frame_wire_message(envelope_wire: dict) -> dict:
    """Wrap one encoded envelope in this participant's transport frame.

    Written against the frame SCHEMA, not against the company's `decode_frame`
    -- same rule as `encode_wall_response`, and for the same reason: this
    module may not import `company.*`, and a frame built by reading the
    receiver's code would make the round-trip a tautology.
    """
    if not isinstance(envelope_wire, dict):
        raise SeamEncodeError(
            f"expected an encoded envelope dict, got {type(envelope_wire).__name__}"
        )
    return {
        "sender": PARTICIPANT_ID,
        "credential": PARTICIPANT_CREDENTIAL,
        "envelope": envelope_wire,
    }


def emit_wire_responses(
    event: PaymentEvent,
    seam_input: Optional[SeamAdapterInput] = None,
) -> List[dict]:
    """`emit_wall_responses`, but handing over BYTES-shaped wire messages
    instead of in-process objects -- what a real bank feed delivers.

    This is the form the live triad crosses on. The object form remains for
    the offline harness and for constructing the responses in the first place;
    what changed is that the COMPANY no longer receives one.

    Since pass 39 each message is FRAMED (see above), so the company's route to
    a payment observation now runs through a participant check as well as the
    envelope's refusals.
    """
    return [
        frame_wire_message(encode_wall_response(r))
        for r in emit_wall_responses(event, seam_input)
    ]
