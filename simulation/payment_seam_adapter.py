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
from copy import deepcopy
from dataclasses import dataclass, fields
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import List, Optional, Sequence, Tuple

from interface.contracts.payment_observable_seam import (
    ADDACS_NOTIFICATION_TYPE,
    BACS_INPUT_REPORT_INTERIM_TYPE,
    BACS_INPUT_REPORT_LEG,
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_PAYLOAD_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    SCHEMA_VERSION,
    AddacsAdvice,
    AddacsAdviceType,
    BacsArruddOutcome,
    BacsInputReport,
    BacsReasonCategory,
    CollectionRequest,
    DDOutcomeStatus,
    PaymentRail,
    RemittanceAdvice,
)
from interface.contracts.wall_envelope import (
    ErrorDetail,
    WallInterim,
    WallNotification,
    WallRequest,
    WallResponse,
    WallStatus,
)
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


def mandate_ref_for(account_id: str) -> str:
    """The mandate reference this build uses for an account -- ONE spelling,
    exported because the company side has to construct a `CollectionRequest`
    naming the same mandate the ARUDD line will later report against, and two
    modules each spelling their own literal is the producer/consumer drift class
    this file already guards elsewhere (`ADDACS_NOTIFICATION_TYPE`)."""
    return f"MANDATE-{account_id}"


def _default_mandate_ref(event: PaymentEvent, account_id: str) -> str:
    return mandate_ref_for(account_id)


class TransportFault(Enum):
    """WHAT THE WIRE DID TO THIS CROSSING, as distinct from what the payment did.

    THE QUESTION THIS ANSWERS. The blind review's Q5 asks whether the stand-in
    "can produce a response that *never arrives*". Until this enum it could not
    -- not as a modelled outcome. The one silence it had
    (`FAILED` + non-DD rail -> `[]`) is a statement about the BANKING WORLD:
    real supplier systems receive no report for a missed push payment, so the
    absence is a faithful observable and always occurs. That is the no-remittance
    blind spot, and it is not a transport failure at all. Nothing here could
    model the wire itself failing on a crossing that should have been answered.

    WHY IT SITS AFTER THE TRUTH -> OBSERVABLE MAPPING. A transport failure is
    INDEPENDENT of what the message would have said: a network that drops a
    packet does not first read it. So these are applied to whatever the mapping
    produced, never woven into it, and the wall property is untouched -- a
    dropped `RemittanceAdvice` and a dropped `BacsArruddOutcome` are the same
    silence, which is exactly the information a real company loses.

    WHY IT IS CALLER-DRIVEN AND NOT DRAWN, which is a deliberate call and the
    conservative one. Giving this a probability would make it a property of the
    BASELINE WORLD, and R13 binds: the baseline changes only for
    fidelity-to-reality reasons, decided blind to company P&L, and a transport
    failure rate is a number this pass has no external anchor for. Defaulting to
    `NONE` means no committed run's results move by a penny. What a real rate
    should be is a curriculum question and therefore the director's, not a
    constant this module is entitled to invent.

    THE THREE FAULTS ARE THREE DIFFERENT FACTS, and the point of the enum is
    that a company must tell them apart:

      * `SILENCE` -- nothing arrives, ever. No envelope, no bytes, no handler
        call. The company can only notice this by holding a clock against a
        crossing it already knows is open (`company.interfaces.crossing_silence`),
        because absence is detectable only against an expectation.
      * `TIMEOUT` -- a `WallResponse(status=TIMEOUT)` DOES arrive. This is the
        transport's own report that it gave up waiting, which is how a real
        client library surfaces one; the counterparty itself never sends this.
        Distinct from `SILENCE` in the only way that matters: the company is
        TOLD, so it need not infer.
      * `ERROR` -- the crossing itself failed, carrying a structured
        `ErrorDetail`. Says nothing about whether the payment happened.

    `TIMEOUT` and `ERROR` were both UNINHABITED in the status vocabulary at pass
    40 (`tools.wall_channel_census.status_liveness_conformance`) -- no writer
    anywhere in the build. This is their writer. Both are named here rather than
    only the one the blocker mentioned, because that census's own commentary
    records the class: a list assembled by noticing gets the member someone was
    looking at.
    """

    NONE = "NONE"
    SILENCE = "SILENCE"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


#: The `ErrorDetail.code` a transport-level failure carries. One code, because
#: this stand-in models the wire failing and not a counterparty's error taxonomy
#: -- inventing a rich set of codes here would be fabricating an observable
#: vocabulary no real feed has agreed to.
TRANSPORT_ERROR_CODE = "TRANSPORT_FAILURE"


def _apply_transport_fault(
    responses: List[WallResponse],
    fault: "TransportFault",
    *,
    correlation_id: str,
    observed_at: datetime,
) -> List[WallResponse]:
    """Apply `fault` to whatever the truth -> observable mapping produced.

    `NONE` returns `responses` UNCHANGED and is the only path any existing
    caller takes. `SILENCE` returns `[]` -- the response never arrives, which is
    the whole of Q5's first clause. The other two REPLACE the responses with a
    single payload-free envelope: a transport that failed did not deliver the
    fact, so carrying the payload through would be the stand-in leaking a truth
    the company never received, and `WallResponse.__post_init__` refuses it
    anyway.

    `observed_at` is the transport's own clock -- when the failure was noticed,
    not when the payment was due. `valid_time` is `None` for both: a failed
    exchange is about no real-world period at all.
    """
    if fault == TransportFault.NONE:
        return responses
    if fault == TransportFault.SILENCE:
        return []
    if fault == TransportFault.TIMEOUT:
        return [
            WallResponse(
                correlation_id=correlation_id,
                status=WallStatus.TIMEOUT,
                schema_version=SCHEMA_VERSION,
                observed_at=observed_at,
                valid_time=None,
                payload=None,
            )
        ]
    if fault == TransportFault.ERROR:
        return [
            WallResponse(
                correlation_id=correlation_id,
                status=WallStatus.ERROR,
                schema_version=SCHEMA_VERSION,
                observed_at=observed_at,
                valid_time=None,
                payload=None,
                error=ErrorDetail(
                    code=TRANSPORT_ERROR_CODE,
                    message=(
                        f"the crossing {correlation_id} failed in transport and "
                        "carries no observation"
                    ),
                ),
            )
        ]
    raise ValueError(
        f"payment_seam_adapter: unrecognised TransportFault {fault!r} -- a fault this "
        "adapter cannot apply must refuse, never fall through as a clean delivery"
    )


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
    #: What the TRANSPORT does to this crossing (atom EP6, Q5). Defaults to
    #: `NONE`, so every existing caller and every committed run is bit-identical
    #: -- see `TransportFault` for why this is caller-driven rather than drawn.
    transport_fault: TransportFault = TransportFault.NONE


def _map_event_to_responses(
    event: PaymentEvent,
    seam_input: SeamAdapterInput,
) -> List[WallResponse]:
    """THE TRUTH -> OBSERVABLE MAPPING, and the whole of the wall property.

    Split out of `emit_wall_responses` at pass 41 so that the mapping and the
    TRANSPORT are separately testable. The separation is the design point rather
    than tidiness: the wall's guarantee ("could a real bank/Bacs feed have
    reported this?") is a property of THIS function alone, and a transport fault
    applied afterwards cannot weaken it -- dropping or replacing a message can
    only ever remove information the company would have had.

    Returns:
      * SUCCESS  -> [WallResponse[RemittanceAdvice]]
      * FAILED + DIRECT_DEBIT rail -> [WallResponse[BacsArruddOutcome]]
      * FAILED + any other rail -> []  (the no-remittance blind spot, C-S3)
      * DISPUTE -> [WallResponse(status=NOT_KNOWABLE_YET, payload=None)]
    """
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


def emit_wall_responses(
    event: PaymentEvent,
    seam_input: Optional[SeamAdapterInput] = None,
) -> List[WallResponse]:
    """THE adapter function: map one generator `PaymentEvent` (truth) to the
    list of `WallResponse` objects a real bank/Bacs feed would produce
    (observable), then apply whatever the TRANSPORT did to them.

    Two stages, deliberately (pass 41):
      1. `_map_event_to_responses` -- the wall property, unchanged.
      2. `_apply_transport_fault` -- what the wire did, independent of what the
         message said. `TransportFault.NONE` (the default) makes this stage the
         identity, so every existing caller and every committed run is
         bit-identical to pass 40.

    The transport's clock is the LATEST `observed_at` among the responses it is
    replacing, falling back to the due date when the mapping produced none. A
    failure is noticed no earlier than the message it failed to deliver would
    have arrived, and inventing a fixed timestamp here would let a fault land
    before the crossing it belongs to.
    """
    seam_input = seam_input or SeamAdapterInput()
    mapped = _map_event_to_responses(event, seam_input)
    fault = seam_input.transport_fault
    if fault == TransportFault.NONE:
        return mapped
    correlation_id = seam_input.correlation_id or _default_correlation_id(event)
    observed_at = (
        max(r.observed_at for r in mapped)
        if mapped
        else _observed_at(date.fromisoformat(event.due_date))
    )
    return _apply_transport_fault(
        mapped, fault, correlation_id=correlation_id, observed_at=observed_at
    )


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
# THE INTERIM LEG -- the Bacs input report (blind review Q3, EP6).
#
# WHAT WAS WRONG BEFORE THIS EXISTED: this seam had exactly two legs and could
# only ever have two, because `correlation_id` bound one answer to one question
# and there was no shape for a message that resolved nothing. The reviewer's Q3
# is one sentence -- "show me a conversation with more than two legs" -- and its
# fail condition is that the layer then "covers only the trivial exchanges".
#
# WHY THIS IS NOT A CURRICULUM CHANGE (R13), which a new world message otherwise
# would be. The input report tells the company NOTHING the company did not
# already send: it echoes back its own submission and says it validated. No
# parameter, no difficulty value, no draw, no substream, no generator event. The
# world is not deciding anything here -- it is acknowledging. That is precisely
# why it can be built by this seat, and it is also why a REJECTION is not drawn
# below: which submissions a bureau rejects at input validation IS a world
# behaviour with a rate, so it is caller-supplied (the `SpecViolation` /
# `TransportFault` pattern -- default empty, so every committed run is
# bit-identical) rather than invented here.
# ---------------------------------------------------------------------------

#: The exact key set of a REQUEST on the wire, MIRRORED from the published
#: contract rather than imported from the company's codec -- `simulation/` may
#: not import `company.*` at all, so a counterparty refuses against the schema as
#: published, which is what a foreign participant reading a spec actually does.
#: Same shape, same reason, as `simulation/conversation_response.py`'s own
#: `_REQUEST_WIRE_FIELDS`. Two independent statements of one key set: if they
#: ever disagree the crossing breaks loudly, which is the point.
_REQUEST_WIRE_FIELDS: frozenset = frozenset(
    {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
)

_COLLECTION_PAYLOAD_WIRE_FIELDS: frozenset = frozenset(
    {"account_id", "mandate_ref", "amount_gbp", "rail", "requested_collection_date"}
)


class SeamDecodeError(ValueError):
    """This counterparty refused a message that arrived. Deliberately NOT
    `WallProtocolError`: that type is the COMPANY's, and a bureau does not raise
    its customer's exceptions."""


def decode_collection_request(wire) -> WallRequest:
    """Leg 1 read off the wire by the BUREAU, or refused.

    ABSENCE IS NEVER AGREEMENT, which is the whole of why every field is
    required in both directions: a missing key is refused rather than defaulted,
    and an unknown key is refused rather than ignored. A decoder that ignored
    what it did not recognise would let the company believe it had asked for
    something this build never read.

    THE VERSION IS CHECKED AND THE CHECK IS NOT A FORMALITY. A submission
    stamped with a release this bureau does not speak is refused by number,
    which is the one thing a version exists to make possible."""
    if not isinstance(wire, dict):
        raise SeamDecodeError(
            f"a request must arrive as a mapping, got {type(wire).__name__}"
        )
    present = set(wire)
    missing = sorted(_REQUEST_WIRE_FIELDS - present)
    if missing:
        raise SeamDecodeError(
            f"request omits required field(s) {missing} -- an absent field is "
            "never read as agreement with this process's own defaults"
        )
    unknown = sorted(present - _REQUEST_WIRE_FIELDS)
    if unknown:
        raise SeamDecodeError(
            f"request carries field(s) {unknown} that schema version "
            f"{SCHEMA_VERSION} does not define"
        )
    version = wire["schema_version"]
    if not isinstance(version, int) or isinstance(version, bool):
        raise SeamDecodeError(f"schema_version must be an int, got {version!r}")
    if version != SCHEMA_VERSION:
        raise SeamDecodeError(
            f"schema_version {version} is not the {SCHEMA_VERSION} this seam speaks"
        )
    payload = wire["payload"]
    if not isinstance(payload, dict):
        raise SeamDecodeError(
            f"a collection payload must be a mapping, got {type(payload).__name__}"
        )
    payload_present = set(payload)
    payload_missing = sorted(_COLLECTION_PAYLOAD_WIRE_FIELDS - payload_present)
    if payload_missing:
        raise SeamDecodeError(
            f"collection payload omits required field(s) {payload_missing}"
        )
    payload_unknown = sorted(payload_present - _COLLECTION_PAYLOAD_WIRE_FIELDS)
    if payload_unknown:
        raise SeamDecodeError(
            f"collection payload carries field(s) {payload_unknown} that schema "
            f"version {SCHEMA_VERSION} does not define"
        )
    try:
        collection = CollectionRequest(
            account_id=str(payload["account_id"]),
            mandate_ref=str(payload["mandate_ref"]),
            amount_gbp=float(payload["amount_gbp"]),
            rail=PaymentRail(payload["rail"]),
            requested_collection_date=date.fromisoformat(
                str(payload["requested_collection_date"])
            ),
        )
        return WallRequest(
            correlation_id=str(wire["correlation_id"]),
            request_type=str(wire["request_type"]),
            schema_version=version,
            as_of=datetime.fromisoformat(str(wire["as_of"])),
            emitted_at=datetime.fromisoformat(str(wire["emitted_at"])),
            payload=collection,
        )
    except (TypeError, ValueError) as exc:
        raise SeamDecodeError(f"collection request is malformed: {exc}") from exc


# Real Bacs makes the input report available the working day after submission --
# day 1 of the three-day cycle, ahead of the day-3 outcome. Fixed, not drawn: the
# exact lag carries no information a company system acts differently on, and the
# ORDERING (ack before outcome) is the fact that matters.
BACS_INPUT_REPORT_LAG_DAYS = 1

INPUT_VALIDATION_ERROR_CODE = "INPUT_VALIDATION_REJECTED"


@dataclass(frozen=True)
class SubmissionAcknowledgement:
    """What one Bacs submission produced: an interim per ACCEPTED collection and
    a terminal error per REJECTED one.

    TWO PRIMITIVES OUT OF ONE SUBMISSION, and the split is `WallInterim`'s own
    rule rather than a preference here: acceptance leaves something still owed
    (leg 3 is coming), so it is an interim; rejection at input validation ends
    the exchange and no outcome will ever follow, so it is a `WallResponse` with
    a status. Modelling the rejection as an interim carrying an `accepted=False`
    flag would give the interim a resolution, which is the exact move that
    collapses a three-leg conversation back into two."""

    interims: Tuple[WallInterim, ...]
    rejections: Tuple[WallResponse, ...]


def emit_input_reports(
    requests: Sequence[WallRequest],
    submission_ref: str,
    rejected_correlation_ids: frozenset = frozenset(),
) -> SubmissionAcknowledgement:
    """Leg 2 for one submission of `WallRequest[CollectionRequest]`.

    THE FILE-LEVEL COUNTS ARE THE SAME ON EVERY LEG OF THE SUBMISSION, which is
    the whole reason `submission_ref` and the counts are on the payload at all.
    Real Bacs acknowledges a FILE; this wall's correlation unit is one
    collection, so the message is delivered per collection and the file-level
    fact rides along on each. A company that submitted 40 and is acknowledged
    for 38 can see that from any one of the 38 reports -- which is a check it
    could not make if the counts were dropped for being redundant.

    REFUSES rather than skips a request whose payload is not a
    `CollectionRequest`: a bureau acknowledging a message it cannot read is the
    fail-open shape, and silently returning fewer interims than there were
    requests would make a wrong payload type indistinguishable from a rejection.
    """
    if not submission_ref:
        raise ValueError(
            "a submission must carry a submission_ref -- it is the file-level "
            "identity every leg of the submission quotes"
        )
    ordered = list(requests)
    for request in ordered:
        if not isinstance(request.payload, CollectionRequest):
            raise ValueError(
                f"emit_input_reports got a {type(request.payload).__name__} on "
                f"correlation_id {request.correlation_id!r}; the input report "
                "acknowledges collection submissions only"
            )
    unknown = set(rejected_correlation_ids) - {r.correlation_id for r in ordered}
    if unknown:
        raise ValueError(
            f"cannot reject {sorted(unknown)}: not in this submission -- a "
            "rejection for an item that was never sent is not a rejection"
        )

    items_in_submission = len(ordered)
    items_rejected = len(rejected_correlation_ids)
    interims: List[WallInterim] = []
    rejections: List[WallResponse] = []

    for request in ordered:
        collection: CollectionRequest = request.payload
        observed_at = _observed_at(
            request.emitted_at.date(), lag_days=BACS_INPUT_REPORT_LAG_DAYS
        )
        if request.correlation_id in rejected_correlation_ids:
            rejections.append(
                WallResponse(
                    correlation_id=request.correlation_id,
                    status=WallStatus.ERROR,
                    schema_version=SCHEMA_VERSION,
                    observed_at=observed_at,
                    valid_time=collection.requested_collection_date,
                    payload=None,
                    error=ErrorDetail(
                        code=INPUT_VALIDATION_ERROR_CODE,
                        message=(
                            f"item rejected at input validation in submission "
                            f"{submission_ref}"
                        ),
                    ),
                )
            )
            continue
        interims.append(
            WallInterim(
                correlation_id=request.correlation_id,
                leg=BACS_INPUT_REPORT_LEG,
                interim_type=BACS_INPUT_REPORT_INTERIM_TYPE,
                schema_version=SCHEMA_VERSION,
                observed_at=observed_at,
                payload=BacsInputReport(
                    submission_ref=submission_ref,
                    account_id=collection.account_id,
                    mandate_ref=collection.mandate_ref,
                    amount_gbp=collection.amount_gbp,
                    items_in_submission=items_in_submission,
                    items_rejected=items_rejected,
                    value_date=collection.requested_collection_date,
                ),
            )
        )
    return SubmissionAcknowledgement(
        interims=tuple(interims), rejections=tuple(rejections)
    )


# ---------------------------------------------------------------------------
# UNSOLICITED INBOUND -- the ADDACS stream (blind review Q2, EP6).
#
# WHAT WAS WRONG BEFORE THIS EXISTED: `AddacsAdvice` was a payload the contract
# declared, the company's consumer had a reader for (`_observe_addacs`, feeding
# mandate belief), and NO MODULE ANYWHERE EVER SENT. A reader with no writer.
# The only way to deliver one was as a `WallResponse` correlated to a
# `CollectionRequest` that is likewise constructed nowhere -- the reviewer's
# named fail shape exactly, "we model it as a response to a synthetic request".
#
# WHY THE TRIGGER IS NOT A NEW WORLD BEHAVIOUR, which matters under R13: this
# emits nothing the generator did not already decide. A DD failing with the
# generator's `CANCELLED_OTHER` reason IS the payer having cancelled their
# instruction at their bank -- already drawn, already observable as the ARUDD
# line's `INSTRUCTION_CANCELLED` category. Real Bacs reports that one truth
# through TWO independent channels: ARUDD says the collection failed, ADDACS
# says the mandate is gone. Building the second channel adds no parameter, no
# difficulty value and no new draw -- it stops the world under-reporting a fact
# it had already generated.
#
# THE SEQUENCE IS THE STREAM'S, NOT THE EVENT'S, which is why this is a class
# and not a pure function. A per-event counter would restart on every caller
# and make gaps undetectable -- the one thing the primitive exists to expose.
# ---------------------------------------------------------------------------

# The ARUDD reason categories that, in the real rails, are ALSO reported down
# the ADDACS channel as a mandate-lifecycle advice. DECLARED, not derived from
# the failure map: a reason category added to the seam tomorrow must be ruled
# on here by hand, rather than silently joining or silently missing the ADDACS
# stream depending on how some other table happened to be written.
_ADDACS_ADVICE_FOR_REASON = {
    BacsReasonCategory.INSTRUCTION_CANCELLED: AddacsAdviceType.PAYER_CANCELLED,
    BacsReasonCategory.ACCOUNT_CLOSED: AddacsAdviceType.ACCOUNT_CLOSED,
    BacsReasonCategory.PAYER_DECEASED: AddacsAdviceType.PAYER_DECEASED,
}

_ADDACS_ADVICE_TEXT = {
    AddacsAdviceType.PAYER_CANCELLED: "Instruction Cancelled By Payer",
    AddacsAdviceType.ACCOUNT_CLOSED: "Account Closed",
    AddacsAdviceType.PAYER_DECEASED: "Payer Deceased",
}

# A mandate advice reaches the supplier a working-day or so behind the failed
# collection it relates to. Fixed, not drawn: the exact lag carries nothing a
# company system acts differently on, and drawing it would be a new random
# stream for no observable gain.
_ADDACS_ADVICE_LAG_DAYS = 1


class MandateNotificationStream:
    """The counterparty's OWN ADDACS feed -- a monotonic, gap-free-at-source
    stream of unsolicited mandate advices.

    Stateful on purpose. `sequence` is the counterparty's position counter, so
    it belongs to the FEED and not to any one message; a caller that had to
    supply it would be numbering the sender's stream on the sender's behalf,
    and every caller would start again at zero.

    THE SOURCE NEVER SKIPS. This emits 0, 1, 2, ... with no holes, which is
    what makes the company-side gap detector meaningful: any hole the company
    observes was introduced by the TRANSPORT (loss), never by the sender. A
    stand-in that numbered with holes would make a lost message and a normal
    one indistinguishable, and the detector would be measuring the fixture.
    """

    def __init__(self, sender: Optional[str] = None) -> None:
        # Resolved at call time, not as a default: `PARTICIPANT_ID` is defined
        # further down this module, and duplicating its literal here is the
        # producer/consumer spelling-drift class. One counterparty, one id.
        self._sender = sender if sender is not None else PARTICIPANT_ID
        self._next_sequence = 0

    @property
    def sender(self) -> str:
        return self._sender

    @property
    def next_sequence(self) -> int:
        return self._next_sequence

    def emit_for_event(
        self,
        event: PaymentEvent,
        seam_input: Optional[SeamAdapterInput] = None,
    ) -> List[WallNotification]:
        """Zero or one ADDACS advice for one generator event.

        Returns `[]` for everything that is not a mandate-lifecycle failure --
        a successful collection, a dispute, a non-DD rail, and an
        INSUFFICIENT_FUNDS failure (the payer had no money; the instruction is
        untouched and a real ADDACS would not fire). Emitting on every failure
        would make the advice a duplicate of the ARUDD line rather than the
        separate fact it is.
        """
        seam_input = seam_input or SeamAdapterInput()
        if event.result != "failed" or event.payment_method != DIRECT_DEBIT:
            return []
        reason_category = bacs_reason_category_for(event.dd_failure_reason)
        advice_type = _ADDACS_ADVICE_FOR_REASON.get(reason_category)
        if advice_type is None:
            return []

        account_id = seam_input.account_id or _default_account_id(event)
        mandate_ref = seam_input.mandate_ref or _default_mandate_ref(event, account_id)
        due = date.fromisoformat(event.due_date)
        payload = AddacsAdvice(
            mandate_ref=mandate_ref,
            account_id=account_id,
            advice_type=advice_type,
            advice_text=_ADDACS_ADVICE_TEXT[advice_type],
            value_date=due,
        )
        sequence = self._next_sequence
        self._next_sequence += 1
        return [
            WallNotification(
                # The SENDER's own message identity, not the company's
                # correlation id: a notification answers nothing, so borrowing
                # the correlation key would re-assert the link this primitive
                # exists to deny.
                notification_id=f"ADDACS-{self._sender}-{sequence}",
                notification_type=ADDACS_NOTIFICATION_TYPE,
                schema_version=SCHEMA_VERSION,
                sender=self._sender,
                sequence=sequence,
                observed_at=_observed_at(due, lag_days=_ADDACS_ADVICE_LAG_DAYS),
                valid_time=due,
                payload=payload,
            )
        ]

    def emit_for_events(self, events, seam_input_for=None) -> List[WallNotification]:
        """Batch form, mirroring `emit_wall_responses_batch`. The stream's
        numbering runs ACROSS the batch -- that is the point of holding it."""
        out: List[WallNotification] = []
        for event in events:
            seam_input = seam_input_for(event) if seam_input_for is not None else None
            out.extend(self.emit_for_event(event, seam_input))
        return out


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
        # THE MESSAGE'S OWN VINTAGE, NOT THIS MODULE'S CURRENT ONE (EP6 pass 44).
        # This read was `SCHEMA_VERSION` -- the encoder's own constant -- in all
        # THREE world-side seam encoders, while the company's codec
        # (`wall_protocol.encode_response`) had always preserved the field. The
        # defect was invisible for as long as exactly one version existed, and
        # the payment seam going to v2 is what made the two able to disagree.
        # An encoder that overwrites the stamp makes the vintage field unable to
        # differ from the reader's constant, so the decoder's version check --
        # the one thing a version number is FOR -- could never fire on anything
        # this seam emitted. Live behaviour is unchanged either way, because
        # every construction site here already stamps `SCHEMA_VERSION`; what is
        # removed is the latent relabelling.
        "schema_version": response.schema_version,
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


# ---------------------------------------------------------------------------
# THE STAND-IN MISBEHAVING ON PURPOSE (atom EP6_wall_protocol_typing, pass 42,
# 2026-08-20) -- the blind review's Q6.
#
# THE QUESTION. "Can it emit spec-violating traffic -- duplicate flow
# references, readings for MPANs you don't supply, out-of-order revisions, a
# backlog burst?" The answer needed was "yes, and it's used in regression",
# with the reviewer's own gloss on why: "if the fake can only be well-behaved,
# it rehearses nothing worth rehearsing."
#
# WHAT WAS ALREADY TRUE AND WHY IT WAS NOT THE ANSWER. Pass 37 recorded that
# the company REFUSES spec-violating input (`wall_protocol`'s envelope and
# payload refusals) and that the consumer handles duplicates and out-of-order
# revisions. Both are tested. Neither is Q6's subject: those tests hand the
# company a hand-built bad message, which asks whether the RECEIVER copes and
# never whether the STAND-IN can produce one. A rehearsal partner that can only
# be well-behaved leaves the receiver's tolerances exercised solely by the
# imagination of whoever wrote the test.
#
# WHY THESE ARE APPLIED AT THE WIRE AND NOT TO THE TYPED OBJECTS. `WallResponse`
# and the payload dataclasses refuse their own invalid constructions, and
# rightly: they are the CONTRACT. A misbehaving counterparty is precisely one
# whose bytes its own encoder would not have produced, so the violation is
# applied to the encoded wire form -- after `encode_wall_response` has done its
# honest job. Weakening the encoder to let a violation through would break the
# well-behaved path to model the badly-behaved one.
#
# WHAT IS DELIBERATELY *NOT* HERE: structurally malformed bytes -- a missing
# field, a bad `schema_version`, a payload type off the contract. Those are the
# decoder's business and `tests/company/interfaces/test_wall_protocol.py`
# already exercises them from a hand-built message; a fault mode here would
# only re-test the refusals. Every violation below is STRUCTURALLY VALID and
# SEMANTICALLY WRONG, which is the class nothing could produce before.
#
# CALLER-DRIVEN, NOT DRAWN -- the same call, for the same reason, as
# `TransportFault`: a violation RATE would be a property of the baseline world
# and R13 makes that the director's. Default `NONE`, identity asserted, so no
# committed run moves by a penny.
# ---------------------------------------------------------------------------


class SpecViolation(Enum):
    """HOW THIS STAND-IN CAN BREAK THE AGREED SPEC WHILE STAYING WELL-FORMED.

    Each member is a SEQUENCE-level transform (see `apply_spec_violation`),
    because three of the reviewer's four named violations are not properties of
    any one message: a duplicate, an ordering and a burst only exist across a
    hand-over.

      * `DUPLICATE_REFERENCE` -- the same flow reference delivered twice in one
        hand-over. The real shape is a Bacs bureau re-sending a file, or the
        same D0018 arriving on two routes.
      * `FOREIGN_ACCOUNT` -- a message about an account this company does not
        supply. The payment-seam analogue of the reviewer's "readings for MPANs
        you don't supply"; on a real bank feed it is a remittance mis-keyed to
        the wrong supplier's account reference.
      * `OUT_OF_ORDER_REVISION` -- a restatement handed over BEFORE the message
        it restates, which is what a rail that fans out across two queues does.
      * `BACKLOG_BURST` -- a quiet period and then everything at once, every
        message stale on arrival.

    A REFUSAL, NEVER A NO-OP. Every transform below raises when it cannot
    actually be applied to the messages it was given. A violation that silently
    declined to happen would make any regression built on it FAIL-OPEN in the
    R15 sense -- green because nothing misbehaved, read as green because the
    company coped.
    """

    NONE = "NONE"
    DUPLICATE_REFERENCE = "DUPLICATE_REFERENCE"
    FOREIGN_ACCOUNT = "FOREIGN_ACCOUNT"
    OUT_OF_ORDER_REVISION = "OUT_OF_ORDER_REVISION"
    BACKLOG_BURST = "BACKLOG_BURST"


#: The account reference a `FOREIGN_ACCOUNT` violation names. A FIXED synthetic
#: literal, and that is a wall decision rather than laziness: keying it off some
#: other customer drawn from the generator would put a real (hidden) identity on
#: the wire, which is the one thing this module exists to prevent. A company
#: that does not supply this account cannot learn anything from it beyond the
#: fact that it does not supply it.
FOREIGN_ACCOUNT_ID = "ACC-NOT-SUPPLIED-BY-THIS-COMPANY"


class SpecViolationNotApplicable(ValueError):
    """This hand-over could not carry the requested violation. Raised rather
    than returned-unchanged: see `SpecViolation`'s closing paragraph."""


def _envelope_of(message: dict) -> dict:
    envelope = message.get("envelope") if isinstance(message, dict) else None
    if not isinstance(envelope, dict):
        raise SpecViolationNotApplicable(
            "expected a framed wire message with an 'envelope' dict, got "
            f"{message!r}"
        )
    return envelope


def apply_spec_violation(
    wire_messages: List[dict],
    violation: "SpecViolation",
) -> List[dict]:
    """Return the hand-over this stand-in makes when it is misbehaving.

    Takes and returns FRAMED wire messages (`emit_wire_responses`' output), and
    never mutates its input -- a caller holding the well-behaved hand-over for
    comparison must still have it afterwards, which is what makes the null
    control in every regression below possible.
    """
    if violation == SpecViolation.NONE:
        return list(wire_messages)
    if not wire_messages:
        raise SpecViolationNotApplicable(
            f"{violation.value}: an empty hand-over carries no violation -- a "
            "stand-in that emitted nothing did not misbehave, it was silent "
            "(that is TransportFault.SILENCE)"
        )
    if violation == SpecViolation.DUPLICATE_REFERENCE:
        # Each message delivered twice, adjacently: the same flow reference,
        # the same everything. Deep-copied so a consumer that mutates what it
        # is handed cannot make the two deliveries differ.
        out: List[dict] = []
        for message in wire_messages:
            out.append(deepcopy(message))
            out.append(deepcopy(message))
        return out
    if violation == SpecViolation.FOREIGN_ACCOUNT:
        out = []
        for message in wire_messages:
            message = deepcopy(message)
            payload = _envelope_of(message).get("payload")
            if not isinstance(payload, dict) or "account_id" not in payload.get(
                "fields", {}
            ):
                raise SpecViolationNotApplicable(
                    "FOREIGN_ACCOUNT: this message carries no account_id to "
                    "mis-key -- a payload-free envelope (a non-OK status) is "
                    "about no account at all"
                )
            payload["fields"]["account_id"] = FOREIGN_ACCOUNT_ID
            out.append(message)
        return out
    if violation == SpecViolation.OUT_OF_ORDER_REVISION:
        if len(wire_messages) < 2:
            raise SpecViolationNotApplicable(
                "OUT_OF_ORDER_REVISION: one message cannot arrive out of order "
                "-- an ordering is a property of at least two"
            )
        # Handed over newest-first, by the counterparty's OWN clock. Reversal is
        # the strongest form: no message arrives before anything it precedes.
        return [
            deepcopy(m)
            for m in sorted(
                wire_messages,
                key=lambda m: str(_envelope_of(m).get("observed_at")),
                reverse=True,
            )
        ]
    if violation == SpecViolation.BACKLOG_BURST:
        if len(wire_messages) < 2:
            raise SpecViolationNotApplicable(
                "BACKLOG_BURST: a burst is many messages held back and released "
                "together; one message is a delivery"
            )
        # THE BURST IS THE HAND-OVER ITSELF, and this is the honest modelling
        # rather than a shortcut. Nothing on this wire records when a message
        # was HANDED OVER, only when the counterparty says it observed the fact
        # (`observed_at`). So a burst differs from an ordinary batch in exactly
        # one respect the company can see -- every message in it is stale -- and
        # in one it cannot: that they all arrived at once. What this transform
        # therefore produces is the whole backlog in one list, oldest first,
        # which is what a rail releases after a queue clears.
        return [
            deepcopy(m)
            for m in sorted(
                wire_messages, key=lambda m: str(_envelope_of(m).get("observed_at"))
            )
        ]
    raise SpecViolationNotApplicable(
        f"payment_seam_adapter: unrecognised SpecViolation {violation!r} -- a "
        "violation this stand-in cannot emit must refuse, never fall through as "
        "well-behaved traffic"
    )


def emit_wire_responses_batch(
    events,
    seam_input_for=None,
    *,
    spec_violation: "SpecViolation" = SpecViolation.NONE,
) -> List[dict]:
    """The batch hand-over a real bank/Bacs feed makes: `emit_wire_responses`
    flattened across a sequence of `PaymentEvent`s, then whatever the
    counterparty did wrong to the batch as a whole.

    `spec_violation=NONE` (the default) makes the second stage the identity, so
    this is exactly `emit_wire_responses` per event concatenated.
    """
    wire: List[dict] = []
    for event in events:
        seam_input = seam_input_for(event) if seam_input_for is not None else None
        wire.extend(emit_wire_responses(event, seam_input))
    return apply_spec_violation(wire, spec_violation)
