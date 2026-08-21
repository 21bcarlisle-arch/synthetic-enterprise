"""The payment-observable seam -- atom W4_4_payment_observable_seam, the
SEAM third of the D5 payment coupled-triad (W2_11 source / W4_4 seam / D5
consumption / H27 gap).

WHAT THIS IS: a typed, versioned request/response contract exposing the
payment world to `saas/` (the company/collections layer) exactly as a real
UK energy supplier's own systems would receive it -- off a bank statement
feed, a Bacs report, a card-acquirer notification, a settlement/clearing
confirmation. It is expressed in the generic `WallRequest`/`WallResponse`
envelope (`wall_envelope.py`) that this atom instantiates for the payment
crossing specifically (design doc
docs/design/GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md §1.3 #4 and §3.3 items
1-2, 4).

THE EPISTEMIC-WALL GUARANTEE (binding on every dataclass below): every
field answers YES to "could a real UK energy supplier's systems know this
from their bank/Bacs feed alone?" None of these types may carry:
  * the customer's true segment / hardship tier / any behavioural label,
  * a probability, propensity, or any other model parameter,
  * the TRUE reason a payment failed (only the bank's own reported
    status/reason CODE -- the observable, never the underlying truth),
  * any future-dated fact relative to `observed_at`.
The company's own INFERENCE of arrears / ability-to-pay / cash position from
the observable pattern these types carry is D5's job, done on the far side
of this seam; the gap between that inference and the W2_11 generator's
ground truth is H27_payment_belief_gap's job to measure. This module carries
neither inference nor ground truth -- only the observation.

ASYNC BY CONSTRUCTION (C-S3, real here, not theoretical): Bacs runs on a
~3-working-day cycle. A `CollectionRequest` (WallRequest) submitted today
resolves via an outcome report (WallResponse) DAYS later, out of order
relative to other events, and SOMETIMES NEVER (the no-remittance blind
spot -- a payment that simply never arrives is not an error status, it is
the absence of a WallResponse; no field here manufactures a fake "still
pending" placeholder for it). Every response type below is matched to its
request by `correlation_id` alone (see `wall_envelope.WallResponse`) and
must be independently constructible/processable with no other context --
proven by the async test in `tests/interface/test_payment_observable_seam.py`.

PORTABILITY: `PaymentRail` is keyed by RAIL/FUNCTION (what the payment
mechanism IS), never by a hardcoded counterparty or a UK-only assumption. A
second geography's Direct-Debit-equivalent rail (e.g. SEPA Direct Debit)
adds a new `PaymentRail` member and reuses every dataclass below unchanged.

GO-LIVE: the SAME types below are what the W2_11 sim adapter fills today and
what a real bank/Bacs/Open-Banking adapter fills at go-live -- swap the
adapter behind this module, D5 and H27 do not change (typed-flow-seam
preference, CLAUDE.md).

NO SIM/GENERATOR SYMBOL: this module imports nothing from `sim`,
`simulation`, or `company` -- it is pure contract, checked by
`tests/interface/test_payment_observable_seam.py::test_no_sim_or_generator_import`.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum

from interface.contracts.wall_envelope import WallNotification, WallRequest, WallResponse

SCHEMA_VERSION = 1


class PaymentRail(str, Enum):
    """The payment mechanism/function, not a counterparty. Portability: a
    second geography adds a member here (e.g. SEPA_DIRECT_DEBIT), never a
    new dataclass shape."""

    BACS_DIRECT_DEBIT = "bacs_direct_debit"
    FASTER_PAYMENTS = "faster_payments"
    CARD = "card"
    STANDING_ORDER = "standing_order"
    OPEN_BANKING = "open_banking"
    CHEQUE = "cheque"
    OTHER = "other"


class DDOutcomeStatus(str, Enum):
    """Rail-agnostic settle/decline status -- reused by both the Bacs DD
    report and the card/SO/open-banking notification below, since a real
    supplier's ops team reads the same binary outcome off every rail even
    though the reporting mechanics differ."""

    SUCCESS = "success"
    FAILURE = "failure"


class BacsReasonCategory(str, Enum):
    """Coarse, portable OBSERVABLE reason categories standing in for the
    real Bacs ARUDD/ADDACS reason-code tables.

    NAMED SIMPLIFICATION (R10): the authoritative numeric Bacs code sets
    (ARUDD's 0-9/A-Z codes, ADDACS' equivalents) are NOT reproduced here --
    sourcing the exact published code table is a research task, not
    something to fabricate (CLAUDE.md "local models confabulate endpoints"
    discipline extends to regulatory/rail code tables). This mirrors the
    calibration gap already registered against W2_11
    ("DD-failure-reason exact %", maturity_map.yaml). These categories are
    the granularity a company's own systems would read off a real Bacs
    report TEXT field today -- a coarser, honest observable, not a
    re-derivation of Bacs' internal numbering. Any consumer building
    logic against the exact numeric code must treat this as the gap to
    close, not assume this enum already closes it."""

    INSUFFICIENT_FUNDS = "insufficient_funds"
    INSTRUCTION_CANCELLED = "instruction_cancelled"
    ACCOUNT_CLOSED = "account_closed"
    NO_ACCOUNT = "no_account"
    PAYER_DECEASED = "payer_deceased"
    MANDATE_DISPUTED = "mandate_disputed"
    AMOUNT_DIFFERS = "amount_differs"
    ADVANCE_NOTICE_INVALID = "advance_notice_invalid"
    OTHER = "other"


class AddacsAdviceType(str, Enum):
    """ADDACS (Advance Direct Debit Amendment and Cancellation Service):
    the payer's bank advising a mandate change the company did not itself
    action."""

    PAYER_CANCELLED = "payer_cancelled"
    PAYER_AMENDED = "payer_amended"
    TRANSFERRED = "transferred"
    ACCOUNT_CLOSED = "account_closed"
    PAYER_DECEASED = "payer_deceased"
    OTHER = "other"


class AuddisStatus(str, Enum):
    """AUDDIS (Automated Direct Debit Instruction Service): mandate/
    instruction lodgement status."""

    NEW_INSTRUCTION_ACCEPTED = "new_instruction_accepted"
    INSTRUCTION_REJECTED = "instruction_rejected"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Request payload -- COLLECTIONS/BILLING asking a rail to attempt a
# collection. Company-owned data only (account/mandate/amount it already
# has); the epistemic wall polices what flows BACK across the seam, not
# what the company already possesses and sends out.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CollectionRequest:
    """Payload of ``WallRequest[CollectionRequest]``: a request to attempt
    collection of ``amount_gbp`` against ``mandate_ref`` on ``rail``. This
    crosses COMPANY -> WORLD; resolution is one or more of the observable
    response types below, arriving asynchronously (C-S3), keyed back to this
    request's ``correlation_id`` alone."""

    account_id: str
    mandate_ref: str
    amount_gbp: float
    rail: PaymentRail
    requested_collection_date: dt.date


# ---------------------------------------------------------------------------
# Observable response payloads -- WORLD -> COMPANY. Every field here is the
# load-bearing epistemic-wall surface: OBSERVATION ONLY, never truth.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RemittanceAdvice:
    """Observable: inbound-cash advice off the bank statement / remittance
    feed -- "payment received GBP X, ref Y, value-date Z." The most basic,
    rail-agnostic observation: money landed."""

    bank_reference: str
    account_id: str
    amount_gbp: float
    rail: PaymentRail
    value_date: dt.date


@dataclass(frozen=True)
class BacsArruddOutcome:
    """Observable: one ARUDD report line -- a Direct Debit collection
    returned unpaid. Carries the bank's own reported reason CATEGORY/TEXT,
    never the customer's true underlying circumstance (e.g. never "genuine
    financial distress" -- that is a D5 inference from the pattern of these
    observations, not something this seam may assert)."""

    mandate_ref: str
    account_id: str
    amount_gbp: float
    outcome: DDOutcomeStatus
    reason_category: BacsReasonCategory
    reason_text: str
    value_date: dt.date


@dataclass(frozen=True)
class AddacsAdvice:
    """Observable: an ADDACS report -- the payer's bank advising a mandate
    amendment or cancellation the company did not itself initiate."""

    mandate_ref: str
    account_id: str
    advice_type: AddacsAdviceType
    advice_text: str
    value_date: dt.date


@dataclass(frozen=True)
class AuddisReport:
    """Observable: an AUDDIS report -- mandate/instruction lodgement status
    (new mandate accepted, rejected, or a previously-lodged instruction
    cancelled)."""

    mandate_ref: str
    account_id: str
    status: AuddisStatus
    status_text: str
    value_date: dt.date


@dataclass(frozen=True)
class PaymentNotification:
    """Observable: a card / standing-order / open-banking payment
    notification -- rails settled/declined near real-time rather than on
    the multi-day Bacs cycle, but still a SEPARATE, later-arriving event
    from the request that provoked it (C-S3 applies to every rail, not
    only Bacs -- only the latency differs)."""

    account_id: str
    rail: PaymentRail
    amount_gbp: float
    reference: str
    value_date: dt.date
    status: DDOutcomeStatus


@dataclass(frozen=True)
class SettlementConfirmation:
    """Observable: a settlement/clearing confirmation -- funds have
    CLEARED (as distinct from merely been notified/advised). The final,
    firmest observation in the chain for a given payment."""

    reference: str
    account_id: str
    amount_gbp: float
    rail: PaymentRail
    cleared_value_date: dt.date


# ---------------------------------------------------------------------------
# Envelope specialisations -- the ONLY sanctioned typed shape crossing this
# seam. `saas/` and `sim/` adapters depend on these, never on each other.
# ---------------------------------------------------------------------------

PaymentCollectionWallRequest = WallRequest[CollectionRequest]
RemittanceAdviceWallResponse = WallResponse[RemittanceAdvice]
BacsArruddWallResponse = WallResponse[BacsArruddOutcome]
AddacsWallResponse = WallResponse[AddacsAdvice]
AuddisWallResponse = WallResponse[AuddisReport]
PaymentNotificationWallResponse = WallResponse[PaymentNotification]
SettlementConfirmationWallResponse = WallResponse[SettlementConfirmation]

# UNSOLICITED leg (Q2): the SAME payload type, carried by the primitive that
# admits nobody asked for it. `AddacsWallResponse` above is retained only
# because deleting a shipped specialisation is a separate change from adding
# the right one; the adapter no longer builds it.
AddacsWallNotification = WallNotification[AddacsAdvice]

# The notification_type string the ADDACS stream stamps on the envelope. A
# constant rather than a literal at the two call sites, because a producer and
# a consumer that spell a routing key differently is a class this project has
# recorded (substring/spelling attribution defects).
ADDACS_NOTIFICATION_TYPE = "addacs_advice"


# ---------------------------------------------------------------------------
# UNSOLICITED INBOUND (blind review Q2) -- the subset of the observables above
# that a real Bacs feed PUSHES at the company rather than sending in answer to
# anything it asked.
#
# WHY ADDACS AND NOT THE OTHERS, since a wrong split here would be the whole
# defect repeated with a new type. ADDACS is defined by its own contract
# docstring above as "the payer's bank advising a mandate change the company
# did not itself action" -- it is unsolicited BY CONSTRUCTION, and there is no
# request it could be an answer to. The rest are answers to something the
# company did:
#   * BacsArruddOutcome -- reports on a collection the company submitted.
#   * AuddisReport      -- reports on an instruction the company lodged. (Its
#                          CANCELLED member is arguably pushed; it is left on
#                          the response leg deliberately rather than split, as
#                          a per-member split of one payload type is a
#                          different and larger question than this one.)
#   * RemittanceAdvice / PaymentNotification / SettlementConfirmation -- for a
#                          PUSH rail (Faster Payments, standing order, cheque)
#                          these are genuinely unsolicited too, and that is
#                          named here as remaining work rather than done
#                          quietly: they are today emitted only for collections
#                          the company requested, so moving them now would
#                          re-label traffic rather than repair it.
#
# DECLARED, NOT DERIVED, for `OBSERVABLE_PAYLOAD_FIELDS`' reason: a set computed
# from "which types does the adapter send as notifications" would agree with the
# adapter by construction and could never catch it sending the wrong one.
UNSOLICITED_PAYLOAD_TYPES: tuple[type, ...] = (AddacsAdvice,)


# Every observable payload type this seam is permitted to carry in a
# WallResponse -- the epistemic-wall test enumerates exactly this list so a
# future payload addition is forced to pass the same field-level scrutiny.
OBSERVABLE_RESPONSE_PAYLOAD_TYPES: tuple[type, ...] = (
    RemittanceAdvice,
    BacsArruddOutcome,
    AddacsAdvice,
    AuddisReport,
    PaymentNotification,
    SettlementConfirmation,
)


# THE CLOSED OBSERVABLE FIELD SET -- the third and last of the wall's codecs to
# get one (EP6 pass 25), and the one that needed it most: this seam's encoder
# had neither a field-level check NOR a FORBIDDEN_TRUTH_FIELDS denylist, so any
# field added to any of the six payloads above crossed to the company unrefused.
# The other two seams were built on this one's pattern, which is why fixing them
# alone would have been an instance fix of a class defect (R10).
#
# The codec asks the closed question: is every field on this payload one the
# contract has DECLARED observable? Adding a field to a dataclass above and
# nothing else now REFUSES at the point of emission (R15 FAIL-CLOSED). Widening
# the wall means editing this map, and that edit is the epistemic act -- where
# a reviewer must answer "could a real supplier read this off its own bank
# statement / Bacs report alone?" out loud.
#
# DECLARED HERE, NOT DERIVED from the dataclasses: a set computed from its own
# subject widens whenever the subject widens and is an R15 TAUTOLOGY for exactly
# this question. The duplication is the independence.
OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "RemittanceAdvice": (
        "bank_reference", "account_id", "amount_gbp", "rail", "value_date",
    ),
    "BacsArruddOutcome": (
        "mandate_ref", "account_id", "amount_gbp", "outcome",
        "reason_category", "reason_text", "value_date",
    ),
    "AddacsAdvice": (
        "mandate_ref", "account_id", "advice_type", "advice_text", "value_date",
    ),
    "AuddisReport": (
        "mandate_ref", "account_id", "status", "status_text", "value_date",
    ),
    "PaymentNotification": (
        "account_id", "rail", "amount_gbp", "reference", "value_date", "status",
    ),
    "SettlementConfirmation": (
        "reference", "account_id", "amount_gbp", "rail", "cleared_value_date",
    ),
}


# THE SECOND BELT -- the last of the wall's three seams to get one (EP6 pass 27), and
# the one where it does the most work, for a reason worth stating rather than assuming.
#
# WHAT THE CLOSED SET ABOVE CANNOT SEE: a truth field added to a dataclass AND declared
# observable in the same edit. That edit passes `OBSERVABLE_PAYLOAD_FIELDS` by
# construction, because it moved the thing the check reads. The denylist is what still
# fires, and it is a SECOND belt and never the control -- a list of names answers "is
# this one of the leaks we already thought of", which is not the header's question.
#
# WHY THIS SEAM NEEDS IT MOST: the two legs are not equally defended. The ENCODE leg
# (`simulation/payment_seam_adapter.encode_observable_payload`) checks the closed set,
# which is declared independently of the dataclasses. The DECODE leg
# (`company/billing/payment_observation_consumer.decode_observable_payload`) does not:
# its permitted key set is `get_type_hints(t)` of the contract's own dataclasses, so it
# WIDENS with its subject and is an R15 TAUTOLOGY for this question. Until this tuple
# existed, the decode leg had no non-derived check of any kind. That matters precisely
# because of what this seam is FOR: at go-live the encoder belongs to a bank, not to us,
# and the decode leg is the only side of the crossing we still own.
#
# MEASURED, NOT IMAGINED. The names below are grouped by whether they exist in the
# world-side payment stack TODAY. Anything in the second group is an anticipated
# spelling of a class the module header already forbids, and is honestly weaker.
FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = (
    # -- MEASURED: each of these is an attribute of a world-side truth producer that
    # sits behind this seam, named with the file it lives in.
    #
    # `simulation/payment_behaviour_source.py::PaymentEvent` -- the generator whose
    # events `payment_seam_adapter` maps into the observables above. It carries 10
    # fields and exactly these 4 are truth: the other 6 (customer_id, due_date,
    # amount_gbp, payment_method, payment_date, days_late) are either company-owned or
    # genuinely observable off a bank feed, and are deliberately NOT listed. A denylist
    # that reds on `days_late` -- which any supplier computes from its own due date and
    # the advised value date -- is a denylist that gets tuned away with the real leak
    # still inside it.
    "result",                          # PaymentEvent.result: the world's own outcome
                                       # label, and it carries "dispute", which this
                                       # seam deliberately withholds as NOT_KNOWABLE_YET
                                       # with no payload at all. The sanctioned
                                       # observable spellings are `outcome`/`status`.
    "dd_failure_reason",               # PaymentEvent.dd_failure_reason: the TRUE reason,
                                       # forbidden by name in this module's header. Only
                                       # the bank's reported `reason_category`/
                                       # `reason_text` may cross.
    "period_index",                    # PaymentEvent.period_index: the SIM's own clock
                                       # index. A bank feed carries dates.
    "data_regime",                     # PaymentEvent / WillingnessProfile: the
                                       # historical-vs-synthetic marker. A company that
                                       # could read this would know which world it is in.
    #
    # `simulation/willingness_classification.py::WillingnessProfile` -- the hidden
    # ability x willingness answer key, the thing D5/C9 must INFER through this seam and
    # are scored on being wrong about. `is_in_arrears` is its one sanctioned observable.
    "ability",
    "willingness",
    "quadrant",
    "discretionary_margin_monthly",
    "discretionary_margin",
    #
    # `simulation/sme_payment_behaviour.py::hardship_tier` and
    # `simulation/household_demand.py` -- behavioural labels and the stress input the
    # generator draws payment outcomes from.
    "hardship_tier",
    "income_stress",
    "stress",
    #
    # -- ANTICIPATED: no such attribute exists in the tree today. These are spellings of
    # the four classes the module header forbids, listed so the obvious rename does not
    # walk straight past the belt. Weaker than the group above by construction.
    "true_reason",
    "true_result",
    "true_outcome",
    "true_segment",
    "segment_true",
    "hardship",
    "archetype",
    "propensity",
    "probability",
    "ability_to_pay",
)
