"""D5 payment-observation consumer -- the COMPANY-side reader of the payment
seam. Atom D5_payment_observation_consumer, the CONSUMPTION third of the D5
payment coupled-triad (W2_11 source / W4_4 seam / D5 consumption / H27 gap,
COUPLED_TRIAD_DESIGN.md).

WHAT THIS IS: a real UK energy supplier's payment-operations brain, reading
ONLY its own bank/Bacs feed (`interface/contracts/payment_observable_seam.py`,
wrapped in `interface/contracts/wall_envelope.py`'s `WallResponse`) and
turning that feed into the company's BELIEF about cash received, allocation,
ageing and arrears/mandate risk. It never sees the W2_11 generator's ground
truth (true failure cause, segment, hardship state) -- H27_payment_belief_gap
measures the gap between this module's belief and that truth. Every belief
field below is explicitly an INFERENCE, not a fact, and IS ALLOWED TO BE
WRONG -- do not read "plausible" fields here as an attempt to be "correct".

THE EPISTEMIC WALL, enforced by construction:
  * this module imports NOTHING from `sim` or `simulation` -- proven by
    `tests/company/billing/test_payment_observation_consumer.py::
    test_no_sim_or_generator_import` (an AST parse of this file's own
    import statements, not a substring grep).
  * every observation this module reads is a `WallResponse`-wrapped payload
    from `payment_observable_seam.py` -- itself guaranteed (by that module's
    own epistemic test) to carry no generator-internal field. A failed
    `BacsArruddOutcome`'s `reason_category` is the BANK'S own reported code,
    taken here strictly AT FACE VALUE; any arrears-risk inference this module
    forms from a PATTERN of such codes is explicitly tagged `*_belief` /
    `ArrearsRiskBelief` -- the company's own guess, never re-derived truth.

SIMPLICITY GUARD -- reuse, not a second engine: this module holds NO ledger
logic of its own. Cash observations become `company.billing.account_ledger`
`LedgerEvent`s posted through the existing `LedgerBook`/`AccountLedger`
(allocation is `AccountLedger.allocate()`, unchanged); ageing reuses
`company.billing.arrears_engine`'s existing `age_open_items`/`age_balance`/
`ageing_buckets`. This module ADDS: (a) the seam->LedgerEvent translation,
(b) the non-cash beliefs a ledger event can't represent (DD-failure
observations, mandate state) that the ledger has no slot for.

C-S1 (event-arrival tolerance) / C-S3 (async wall contracts): `observe()` is
called once per `WallResponse`, in ANY order, with any gap between calls, and
for a payment that never arrives, simply never called at all for it (the
no-remittance blind spot below). Every belief-producing computation
(`_arrears_risk_belief`, `_update_mandate_belief`'s tie-break, ledger
ageing/allocation itself) is a PURE function of the full observed SET, sorted
by a deterministic key (never by call/arrival order) -- proven by the
order-independence tests.

C-S2 (idempotent + deterministic replay): `observe()` dedups on
`response.correlation_id` (mirrors `AccountLedger.post`'s own event_id dedup
contract: returns True if newly processed, False if already seen) and every
`LedgerEvent` this module posts derives its `event_id` deterministically from
`correlation_id` alone, so double-posting the same seam response is harmless
even if the outer dedup were ever bypassed (defence in depth, same idiom the
ledger already uses).

C-S4 (persistence behind an interface): cash/allocation state lives entirely
in `AccountLedger`'s existing event store; the only state this module adds
(`_dd_failures`, `_mandate_beliefs`) is itself a small append/overwrite-only
observation list read fresh at snapshot time -- no ad-hoc mutable ledger.

THE NO-REMITTANCE BLIND SPOT (binding, C-S1): a payment that never arrives is
not an error status this module can react to -- it is the ABSENCE of a
`WallResponse` (payment_observable_seam.py's own docstring). This module
manufactures NO synthetic "still pending" fact for it. The only degradation
available is what the ledger already gives for free: an invoice with no
`PAYMENT_CREDIT` posted against it simply stays open and ages via
`arrears_engine.age_open_items`/`age_balance` as time passes -- this module
never assumes completeness (a missing payment is never read as "must have
been paid", it is read as "no cash observed yet", full stop). Note the
DELIBERATE gap this leaves open: an unpaid invoice with NO Bacs failure
report at all (e.g. a standing order simply never instructed) ages
identically to one explained by an observed DD failure but carries no DD
failure observation at all, so `arrears_risk_belief` stays NORMAL even
though the account is genuinely arrears-aged -- exactly the kind of
plausible-but-wrong belief H27 is built to catch (see `snapshot()`'s
`cash_position_note` vs `arrears_risk_belief` divergence in that case).

EXPECTED-COLLECTION RECONCILIATION (director ruling 2026-07-25 §2, the narrow
sensing carve-out): the blind spot above is a blind spot of the FAILURE-EVENT
channel only. A real supplier ALSO notices a missed push payment WITHOUT any
rail event -- by reconciling what it billed against what cash arrived: an
invoice due, past a grace window, with no matching credit, is itself the
observable. `expected_collection_misses()` / the snapshot's
`detected_collection_misses` implement exactly this, from the company's OWN
ledger only. It is DETECTION (a sensing organ) and is DELIBERATELY NOT wired
into `arrears_risk_belief` or any action -- dunning, vulnerability/PSR flags,
arrears-driven pricing and bad-debt provisioning are all RESERVED to the
director's forthcoming dunning/debt/provisioning session (ruling §3). It
NARROWS the push-channel detection gap; it never closes it (residual: a
late-but-eventual payment that arrives before `as_of` is correctly NOT flagged
-> detection LATENCY; an ambiguous non-DD `correlation_id` -> oldest-first
allocation can mis-attribute which invoice is the miss; a genuine partial
payment leaves a residual shortfall). R12 honesty guard: a smaller MEASURED
gap, never a company that believes it catches everything.

NAMED SIMPLIFICATIONS (R10):
  * `SettlementConfirmation` is treated as a CONFIRMING note on cash already
    recognised via `RemittanceAdvice`/a successful `BacsArruddOutcome`/a
    successful `PaymentNotification` (matched by `reference`/`bank_reference`
    string equality) -- it does NOT post a second cash event for an
    already-recognised reference, avoiding double counting. If the reference
    was never previously recognised (e.g. a rail whose only advice IS the
    settlement confirmation), it posts its own cash event. Real supplier
    systems vary by rail on which event is THE cash-recognition point; this
    module does not model that per-rail distinction beyond the reference-dedup
    rule above -- future wiring, not asserted here as complete.
  * `PaymentNotification(status=FAILURE)` (card/SO/open-banking decline) has
    no `BacsReasonCategory` on the contract (only Bacs ARUDD carries a reason
    code), so it contributes to `arrears_risk_belief` only as an undifferentiated
    failure count, never a reason-coded `DDFailureObservation` -- a coarser
    signal than a Bacs failure, faithfully reflecting that a real supplier's
    card-decline feed is itself coarser than its Bacs ARUDD report.
  * `arrears_risk_belief`'s thresholds (WATCH/ELEVATED/HIGH at 1/2/3+ recent
    failures, `INSUFFICIENT_FUNDS` treated as the one "hardship-suggestive"
    category) are a DELIBERATELY NAIVE, invented heuristic -- there is no
    externally-calibrated collections-risk model behind it. It exists so
    H27 has a belief surface to score, not because these thresholds are
    claimed realistic.
"""
from __future__ import annotations

import datetime as dt
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, get_type_hints

from company.billing.account_ledger import (
    AccountLedger,
    AllocationResult,
    LedgerBook,
    LedgerEvent,
    LedgerEventType,
)
from company.billing.arrears_engine import (
    AgedItem,
    age_balance,
    age_open_items,
    ageing_buckets,
)
from company.interfaces.wall_protocol import WallProtocolError, decode_response
from interface.contracts.payment_observable_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    AddacsAdvice,
    AddacsAdviceType,
    AuddisReport,
    AuddisStatus,
    BacsArruddOutcome,
    BacsReasonCategory,
    DDOutcomeStatus,
    PaymentNotification,
    RemittanceAdvice,
    SettlementConfirmation,
)
from interface.contracts.wall_envelope import WallResponse, WallStatus

# ---------------------------------------------------------------------------
# Belief types -- every one of these is the COMPANY'S OWN INFERENCE, built
# solely from the observable seam. None is, or may become, ground truth.
# ---------------------------------------------------------------------------


class MandateBeliefState(str, Enum):
    """The company's INFERRED Direct Debit mandate status -- never a read of
    the true mandate state, only what AUDDIS/ADDACS/ARUDD advices imply."""

    UNKNOWN = "unknown"                    # nothing observed yet for this mandate
    ACTIVE_BELIEVED = "active_believed"
    AT_RISK_BELIEVED = "at_risk_believed"       # transient friction observed
    LIKELY_DEAD_BELIEVED = "likely_dead_believed"  # a terminal-sounding advice observed


# Deterministic severity order used ONLY to break a same-value_date tie when
# two conflicting advices carry the identical valid_time -- this makes
# `_update_mandate_belief` a function of the observed SET, never of arrival
# order (C-S1/C-S2).
_MANDATE_SEVERITY: Dict[MandateBeliefState, int] = {
    MandateBeliefState.UNKNOWN: 0,
    MandateBeliefState.ACTIVE_BELIEVED: 1,
    MandateBeliefState.AT_RISK_BELIEVED: 2,
    MandateBeliefState.LIKELY_DEAD_BELIEVED: 3,
}

# ARUDD reason categories this module coarsely reads as mandate-terminal --
# still a GUESS (e.g. ACCOUNT_CLOSED could be temporary account migration in
# truth; this module cannot know that, and must not pretend to).
_MANDATE_TERMINAL_ARRUDD_REASONS: Set[BacsReasonCategory] = {
    BacsReasonCategory.ACCOUNT_CLOSED,
    BacsReasonCategory.NO_ACCOUNT,
    BacsReasonCategory.PAYER_DECEASED,
    BacsReasonCategory.INSTRUCTION_CANCELLED,
}

_ADDACS_TERMINAL: Set[AddacsAdviceType] = {
    AddacsAdviceType.PAYER_CANCELLED,
    AddacsAdviceType.ACCOUNT_CLOSED,
    AddacsAdviceType.PAYER_DECEASED,
    AddacsAdviceType.TRANSFERRED,
}

# The one reason category this module's naive heuristic treats as
# "hardship-suggestive" -- an invented, uncalibrated signal (see module
# docstring's NAMED SIMPLIFICATIONS).
_HARDSHIP_SUGGESTIVE_REASONS: Set[BacsReasonCategory] = {
    BacsReasonCategory.INSUFFICIENT_FUNDS,
}


class ArrearsRiskBelief(str, Enum):
    """COMPANY INFERENCE ONLY, never ground truth: a coarse guess at rising
    payment risk built purely from the PATTERN of observed DD/rail failures.
    This is exactly the belief H27_payment_belief_gap measures against
    W2_11's ground truth -- it is EXPECTED to be wrong sometimes, including
    systematically (e.g. it cannot see a failure with no bounce report at
    all, per the no-remittance blind spot)."""

    NORMAL = "normal"
    WATCH = "watch"
    ELEVATED = "elevated"
    HIGH = "high"


@dataclass(frozen=True)
class DDFailureObservation:
    """One raw, face-value record of an OBSERVED Bacs DD failure -- never a
    ledger event (no cash moved). `reason_category`/`reason_text` are the
    bank's own reported code/text, carried verbatim; this module forms no
    belief about the TRUE cause here, only later, coarsely, in aggregate
    (`ArrearsRiskBelief`)."""

    mandate_ref: str
    account_id: str
    amount_gbp: float
    reason_category: BacsReasonCategory
    reason_text: str
    value_date: dt.date
    observed_at: dt.datetime


@dataclass(frozen=True)
class RailFailureNote:
    """A non-Bacs rail decline (card/SO/open-banking) -- coarser than a
    `DDFailureObservation` because `PaymentNotification` carries no reason
    category on the contract (NAMED SIMPLIFICATION, module docstring)."""

    account_id: str
    reference: str
    amount_gbp: float
    value_date: dt.date
    observed_at: dt.datetime


# The expected-collection reconciliation grace window: a real supplier does not
# declare a collection "missed" the instant a due date passes -- a bank credit
# can be in transit / clearing. It reconciles received cash against issued bills
# and declares a shortfall only once the invoice is `grace_days` past due with
# no matching cash observed. This is a DELIBERATELY UNCALIBRATED bank-clearing
# window (same status as `_arrears_risk_belief`'s invented thresholds), NOT a
# knob tuned toward any gap number (R12) -- the honest number is whatever the
# reconciliation measures, never a target. It sets the detection LATENCY for
# push-channel failures (director ruling 2026-07-25 §1: register the latency,
# do not compress it to zero).
DEFAULT_RECONCILIATION_GRACE_DAYS = 5


@dataclass(frozen=True)
class ExpectedCollectionMiss:
    """A DETECTED expected-collection shortfall (director ruling 2026-07-25 §2,
    the narrow sensing carve-out): an invoice the company ISSUED, now
    `days_latency` past its due date + grace, against which it has observed
    INSUFFICIENT cash on its OWN bank/ledger feed. This is the through-the-wall
    mechanism a real supplier uses to notice a *missed customer-initiated push
    payment* that emits no rail failure event at all (standing order / card /
    prepayment) -- the absence of expected cash by due date is itself the
    observable, no ARUDD/Bacs message required.

    EPISTEMIC WALL: derived PURELY from the company's own `AccountLedger`
    (issued `BILL_DEBIT`s and observed `PAYMENT_CREDIT`s), never from
    `PaymentEvent.result` or any generator internal. It is still a BELIEF -- the
    cash may yet arrive late (the residual latency below), the shortfall may be
    a mis-allocated payment (ambiguous non-DD `correlation_id` -> oldest-first),
    or a genuine partial payment; the detector NARROWS the push-channel blind
    spot, it never closes it (R12 honesty guard: a smaller MEASURED gap, never a
    company that believes it catches everything -- which, because the detection
    metric is pure recall, would be a fail-open flagging-everyone, a WIDER hidden
    gap wearing a better number).

    SENSING ONLY (ruling §2, binding): this is a detection observable. It
    licenses NO acting organ -- no dunning, no vulnerability/PSR flag, no
    arrears-driven pricing or provisioning. Those are RESERVED to the director's
    forthcoming dunning/debt/provisioning session; building an action on top of
    this would foreclose its choices."""

    account_id: str
    invoice_ref: str
    billed_gbp: float
    received_gbp: float          # cash observed & allocated to this invoice by as_of
    shortfall_gbp: float         # billed - received (the observed unpaid amount)
    due_date: dt.date
    detected_as_of: dt.date
    days_latency: int            # detected_as_of - due_date (the observability lag)


@dataclass
class MandateBelief:
    """The company's current inferred state for one mandate, and the single
    observation that most recently justified it (by valid_time, not arrival
    order -- see `_update_mandate_belief`)."""

    mandate_ref: str
    account_id: str
    state: MandateBeliefState = MandateBeliefState.UNKNOWN
    last_advice_text: str = ""
    last_value_date: dt.date = field(default_factory=lambda: dt.date.min)


@dataclass
class PaymentBeliefSnapshot:
    """The full read-out of the company's payment belief for ONE account, as
    of one date -- the surface H27's gap scorer reads and compares against
    W2_11 ground truth. EVERY field is a company inference built only from
    the observable seam (the `allocation`/`aged_items`/`balance_summary`
    fields are downstream of real posted cash events, so they are as
    'factual' as this module's own bookkeeping gets -- but that bookkeeping
    itself only ever reflects what was OBSERVED, never what truly happened;
    `arrears_risk_belief` and `mandate_beliefs` are explicit guesses on top
    of that)."""

    account_id: str
    as_of: dt.date
    allocation: AllocationResult
    aged_items: List[AgedItem]                 # open-item view (empty if none apply)
    balance_aged_item: Optional[AgedItem]       # balance-based view (None if not in arrears)
    ageing_buckets: Dict[str, Dict[str, float]]
    balance_summary: dict
    mandate_beliefs: Dict[str, MandateBelief]
    arrears_risk_belief: ArrearsRiskBelief       # <-- COMPANY GUESS, never truth
    recent_dd_failures: List[DDFailureObservation]
    recent_rail_failures: List[RailFailureNote]
    # DETECTED expected-collection shortfalls (ruling 2026-07-25 §2): the
    # through-the-wall detection of missed push payments (all channels), from
    # own bills vs own observed cash. A BELIEF, not truth (may resolve late).
    detected_collection_misses: List[ExpectedCollectionMiss]
    cash_position_note: str


def _billed_by_invoice(ledger: AccountLedger, as_of: dt.date) -> Dict[str, float]:
    """Total billed (BILL_DEBIT + any debit adjustment) per invoice_ref, as of
    `as_of` -- read from the company's OWN ledger events, for the
    ExpectedCollectionMiss `billed_gbp` context field only. Pure, no beliefs."""
    out: Dict[str, float] = {}
    for e in ledger.events():
        if e.valid_time > as_of or not e.invoice_ref:
            continue
        if e.event_type in (LedgerEventType.BILL_DEBIT, LedgerEventType.ADJUSTMENT_DEBIT):
            out[e.invoice_ref] = round(out.get(e.invoice_ref, 0.0) + e.amount_gbp, 2)
    return out


def _cash_position_note(bal_summary: dict) -> str:
    if bal_summary["in_arrears"]:
        return (
            f"BELIEF: account appears in arrears, GBP {bal_summary['arrears_gbp']:.2f} "
            "outstanding (observed billed-vs-cash-received only; not verified against "
            "true customer circumstance)"
        )
    if bal_summary["in_credit"]:
        return f"BELIEF: account appears in credit, GBP {bal_summary['credit_gbp']:.2f}"
    return "BELIEF: account appears settled/current"


# ---------------------------------------------------------------------------
# OFF THE WIRE (atom EP6_wall_protocol_typing, 2026-08-19) -- the company's
# payload decoder for this crossing.
#
# `company.interfaces.wall_protocol` decodes the ENVELOPE and treats `payload`
# as opaque on purpose: its payload codec is a required function argument with
# no default, so nothing can be deserialised by accident and a new crossing
# never edits it. This function is THIS crossing's half of that bargain.
#
# It is deliberately not the inverse of `simulation.payment_seam_adapter.
# encode_observable_payload` written by reading that function. Both are written
# against `interface.contracts.payment_observable_seam` -- the payload
# dataclasses and their declared field types -- which is what a real supplier
# has: the published schema, not the counterparty's source. So the field set
# and types below come from `get_type_hints`, an INDEPENDENT source from
# anything the sender emitted, and a payload the contract does not define is
# refused rather than accepted as an untyped dict.
#
# ABSENCE IS NEVER AGREEMENT, at payload depth too: the field set must match
# the contract EXACTLY. A missing field is not defaulted (the company would
# then post a belief the bank never advised) and an unknown field is not
# tolerated (a schema that grew is announced by its version, never by a key
# appearing quietly).
# ---------------------------------------------------------------------------

_OBSERVABLE_PAYLOAD_TYPES = {t.__name__: t for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES}
_OBSERVABLE_PAYLOAD_HINTS = {
    t.__name__: get_type_hints(t) for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES
}


def _decode_payload_field(raw: Any, declared: type, where: str) -> Any:
    """Decode one payload field to the type THE CONTRACT declares for it."""
    if isinstance(declared, type) and issubclass(declared, Enum):
        try:
            return declared(raw)
        except ValueError as exc:
            raise WallProtocolError(
                "MALFORMED_FIELD",
                f"{where}: {raw!r} is not one of "
                f"{[m.value for m in declared]}",
            ) from exc
    if declared is dt.date:
        if not isinstance(raw, str):
            raise WallProtocolError(
                "MALFORMED_FIELD", f"{where} must be an ISO-8601 date str, got {raw!r}"
            )
        try:
            return dt.date.fromisoformat(raw)
        except ValueError as exc:
            raise WallProtocolError(
                "MALFORMED_FIELD", f"{where} is not an ISO date: {raw!r}"
            ) from exc
    if declared is str:
        if not isinstance(raw, str):
            raise WallProtocolError(
                "MALFORMED_FIELD", f"{where} must be a str, got {raw!r}"
            )
        return raw
    if declared is float:
        # bool is an int subclass; a True amount is malformed, not 1.0.
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise WallProtocolError(
                "MALFORMED_FIELD", f"{where} must be a number, got {raw!r}"
            )
        return float(raw)
    raise WallProtocolError(
        "CONTRACT_VIOLATION",
        f"{where}: this seam has no decoder for declared type {declared!r} -- a "
        "field type was added to the contract without deciding how it crosses",
    )


def decode_observable_payload(raw: Any) -> Any:
    """Rebuild one observable payload off the wire, or refuse it.

    THE WALL IS CHECKED HERE TOO, AND THIS LEG NEEDS IT MORE THAN THE OTHER ONE.
    `expected` below is `get_type_hints(t)` of the contract's own dataclasses --
    it WIDENS whenever they widen, so it is an R15 TAUTOLOGY for the question
    "could a real supplier know this". The encode leg has a non-derived answer
    (the contract's `OBSERVABLE_PAYLOAD_FIELDS`, declared independently of the
    dataclasses); until EP6 pass 27 this leg had none at all.
    That gap is not theoretical, because of what this seam is FOR: at go-live
    the encoder belongs to a bank and this leg is the only side of the crossing
    the company still owns. A counterparty that started shipping the hidden
    ability/willingness quadrant, or the TRUE reason a Direct Debit failed,
    would produce a perfectly well-formed envelope -- and a company that folded
    those in would be READING the answer key rather than inferring it, which is
    the one thing the D5/H27 gap exists to measure. Refused BY NAME from the
    contract's own `FORBIDDEN_TRUTH_FIELDS`, so the class fails rather than the
    instance somebody remembered (R10).
    """
    if not isinstance(raw, Mapping):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"payload must be a mapping, got {type(raw).__name__}"
        )
    missing = sorted({"payload_type", "fields"} - set(raw))
    if missing:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"payload omits {missing} -- an untagged payload cannot be routed to "
            "one of this seam's six observable types",
        )
    unknown_keys = sorted(set(raw) - {"payload_type", "fields"})
    if unknown_keys:
        raise WallProtocolError(
            "UNKNOWN_FIELD", f"payload carries undefined key(s) {unknown_keys}"
        )
    tag = raw["payload_type"]
    if tag not in _OBSERVABLE_PAYLOAD_TYPES:
        raise WallProtocolError(
            "UNKNOWN_FIELD",
            f"payload_type {tag!r} is not one of this seam's observable types "
            f"{sorted(_OBSERVABLE_PAYLOAD_TYPES)}",
        )
    payload_type = _OBSERVABLE_PAYLOAD_TYPES[tag]
    body = raw["fields"]
    if not isinstance(body, Mapping):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"{tag}.fields must be a mapping, got {type(body).__name__}"
        )
    hints = _OBSERVABLE_PAYLOAD_HINTS[tag]
    expected = set(hints)
    # DENYLIST FIRST -- same ordering, same reason, as the encode leg and as
    # `company/market/flex_participation.py`: the truth-leak message is the more
    # diagnostic of the two, and the ordering keeps each belt separately observable.
    leaking = sorted(set(body) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise WallProtocolError(
            "CONTRACT_VIOLATION",
            f"{tag} carries world-internal truth field(s) {leaking} -- this company "
            "infers ability-to-pay and the reason behind a failed collection from "
            "observables, and may never be handed them",
        )
    absent = sorted(expected - set(body))
    if absent:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"{tag} omits required field(s) {absent} -- never defaulted; the "
            "company would otherwise post a belief the bank did not advise",
        )
    extra = sorted(set(body) - expected)
    if extra:
        raise WallProtocolError(
            "UNKNOWN_FIELD",
            f"{tag} carries field(s) {extra} the contract does not define",
        )
    return payload_type(
        **{
            name: _decode_payload_field(body[name], declared, f"{tag}.{name}")
            for name, declared in hints.items()
        }
    )


class PaymentObservationConsumer:
    """Consumes a stream of `WallResponse`-wrapped payment observables one at
    a time (any order, any lateness, possibly never for a given payment) and
    maintains the company's payment belief across however many accounts
    appear in that stream.

    Public API:
      * `observe(response) -> bool`        -- process one WallResponse.
      * `snapshot(account_id, as_of, ...) -> PaymentBeliefSnapshot`
                                            -- the belief read-out for one
                                               account (H27's scoring surface).
      * `mandate_belief(mandate_ref)`      -- the belief for one mandate.
    """

    def __init__(
        self,
        ledger_book: Optional[LedgerBook] = None,
        dd_failure_window_days: int = 90,
    ) -> None:
        self.ledger_book: LedgerBook = ledger_book if ledger_book is not None else LedgerBook()
        self._dd_failures: Dict[str, List[DDFailureObservation]] = {}
        self._rail_failures: Dict[str, List[RailFailureNote]] = {}
        self._mandate_beliefs: Dict[str, MandateBelief] = {}
        self._recognised_cash_refs: Set[str] = set()
        self._processed_correlation_ids: Set[str] = set()
        self._dd_failure_window_days = dd_failure_window_days

    @property
    def dd_failure_window_days(self) -> int:
        """How far back this company still counts an observed collection
        failure -- the ONE company parameter the belief dimensions depend on.

        Read-only, and public since 2026-08-18 for one measured reason: every
        instrument that published this company's place in the belief band read
        the HARNESS's module constant instead, because the private attribute
        was the only route to the real value. The census then reported 400d of
        memory for the shipped 90d company and for the live 6000d one alike --
        bit-identical across a 120x sweep of the very parameter it named. A
        company knows its own configured lookback; nothing about exposing it
        crosses the wall (it is not a read of the world), and leaving it
        private is what forced the readers to guess."""
        return self._dd_failure_window_days

    # -----------------------------------------------------------------
    # Ingest -- idempotent (C-S2), order-independent (C-S1/C-S3)
    # -----------------------------------------------------------------

    def observe_wire(self, wire: Any) -> bool:
        """Process one observation that arrived AS A WIRE MESSAGE -- the entry
        point a real bank/Bacs feed reaches, and the one the live triad now
        uses (atom EP6_wall_protocol_typing).

        This is the whole of EP6's claim made concrete for this crossing: a
        real counterparty hands over bytes and a mock hands over an object, and
        that is the ONLY place the two observably differ. Coming through here
        they are the same, because the message has passed the same envelope
        refusals and the same payload refusals either way.

        Raises `WallProtocolError` on anything malformed -- one exception type
        at the seam, and never a half-built object reaching the belief code
        below. A refusal is NOT an observation: nothing is marked processed,
        because refusing a message the company could not read is not the same
        as having read it, and a corrected re-delivery of the same
        `correlation_id` must still be able to land.
        """
        response = decode_response(wire, decode_payload=decode_observable_payload)
        return self.observe(response)

    def observe(self, response: WallResponse) -> bool:
        """Process one `WallResponse`. Returns True if newly processed,
        False if `response.correlation_id` was already seen (idempotent
        re-delivery is a harmless no-op -- mirrors `AccountLedger.post`'s
        own True/False dedup contract).

        A non-OK response (`NOT_KNOWABLE_YET`/`TIMEOUT`/`ERROR`) carries no
        payload by construction (`WallResponse.__post_init__`) -- this is an
        honest non-update, never an assumed value, and is still marked
        processed so a later retry of the SAME correlation_id is not
        double-counted once it does resolve OK (a resolved response uses a
        fresh, later `WallResponse` for the same fact per the envelope's own
        bitemporal-restatement rule, never an in-place mutation of this one)."""
        if response.correlation_id in self._processed_correlation_ids:
            return False
        self._processed_correlation_ids.add(response.correlation_id)
        if response.status != WallStatus.OK:
            return True
        payload = response.payload
        if isinstance(payload, RemittanceAdvice):
            self._observe_remittance(payload, response)
        elif isinstance(payload, BacsArruddOutcome):
            self._observe_arrudd(payload, response)
        elif isinstance(payload, PaymentNotification):
            self._observe_notification(payload, response)
        elif isinstance(payload, SettlementConfirmation):
            self._observe_settlement(payload, response)
        elif isinstance(payload, AddacsAdvice):
            self._observe_addacs(payload, response)
        elif isinstance(payload, AuddisReport):
            self._observe_auddis(payload, response)
        else:
            raise ValueError(
                f"payment_observation_consumer: unrecognised observable payload "
                f"type {type(payload)!r} -- not one of "
                "OBSERVABLE_RESPONSE_PAYLOAD_TYPES"
            )
        return True

    def _post_cash(
        self,
        *,
        account_id: str,
        amount_gbp: float,
        value_date: dt.date,
        observed_at: dt.datetime,
        correlation_id: str,
        remittance_ref: Optional[str],
    ) -> None:
        """Post ONE received-cash `LedgerEvent`, allocated via the ledger's
        existing remittance-else-oldest-first logic (`AccountLedger.allocate`,
        unchanged). `event_id` is derived deterministically from
        `correlation_id` alone -- a second post of the identical response is
        harmless (the ledger's own idempotent dedup), defence in depth on top
        of `observe()`'s own correlation-id gate."""
        event = LedgerEvent(
            event_id=f"payobs:{correlation_id}",
            account_id=account_id,
            event_type=LedgerEventType.PAYMENT_CREDIT,
            amount_gbp=round(amount_gbp, 2),
            valid_time=value_date,
            transaction_time=observed_at,
            remittance=(remittance_ref,) if remittance_ref else (),
        )
        self.ledger_book.post(event)
        if remittance_ref:
            self._recognised_cash_refs.add(remittance_ref)

    def _observe_remittance(self, payload: RemittanceAdvice, response: WallResponse) -> None:
        self._post_cash(
            account_id=payload.account_id,
            amount_gbp=payload.amount_gbp,
            value_date=payload.value_date,
            observed_at=response.observed_at,
            correlation_id=response.correlation_id,
            remittance_ref=payload.bank_reference,
        )

    def _observe_arrudd(self, payload: BacsArruddOutcome, response: WallResponse) -> None:
        if payload.outcome == DDOutcomeStatus.SUCCESS:
            self._post_cash(
                account_id=payload.account_id,
                amount_gbp=payload.amount_gbp,
                value_date=payload.value_date,
                observed_at=response.observed_at,
                correlation_id=response.correlation_id,
                remittance_ref=None,   # a DD collection is against the account, not one invoice ref
            )
            return
        # FAILURE: no cash moved. Recorded at FACE VALUE only -- see module
        # docstring on the epistemic-wall guarantee.
        obs = DDFailureObservation(
            mandate_ref=payload.mandate_ref,
            account_id=payload.account_id,
            amount_gbp=payload.amount_gbp,
            reason_category=payload.reason_category,
            reason_text=payload.reason_text,
            value_date=payload.value_date,
            observed_at=response.observed_at,
        )
        self._dd_failures.setdefault(payload.account_id, []).append(obs)
        if payload.reason_category in _MANDATE_TERMINAL_ARRUDD_REASONS:
            self._update_mandate_belief(
                mandate_ref=payload.mandate_ref,
                account_id=payload.account_id,
                state=MandateBeliefState.LIKELY_DEAD_BELIEVED,
                note=payload.reason_text,
                value_date=payload.value_date,
            )

    def _observe_notification(self, payload: PaymentNotification, response: WallResponse) -> None:
        if payload.status == DDOutcomeStatus.SUCCESS:
            self._post_cash(
                account_id=payload.account_id,
                amount_gbp=payload.amount_gbp,
                value_date=payload.value_date,
                observed_at=response.observed_at,
                correlation_id=response.correlation_id,
                remittance_ref=payload.reference,
            )
            return
        self._rail_failures.setdefault(payload.account_id, []).append(
            RailFailureNote(
                account_id=payload.account_id,
                reference=payload.reference,
                amount_gbp=payload.amount_gbp,
                value_date=payload.value_date,
                observed_at=response.observed_at,
            )
        )

    def _observe_settlement(self, payload: SettlementConfirmation, response: WallResponse) -> None:
        # Confirming note only -- do not double-count cash already recognised
        # via RemittanceAdvice/a successful ARUDD/PaymentNotification for the
        # same reference (NAMED SIMPLIFICATION, module docstring).
        if payload.reference in self._recognised_cash_refs:
            return
        self._post_cash(
            account_id=payload.account_id,
            amount_gbp=payload.amount_gbp,
            value_date=payload.cleared_value_date,
            observed_at=response.observed_at,
            correlation_id=response.correlation_id,
            remittance_ref=payload.reference,
        )

    def _observe_addacs(self, payload: AddacsAdvice, response: WallResponse) -> None:
        if payload.advice_type in _ADDACS_TERMINAL:
            state = MandateBeliefState.LIKELY_DEAD_BELIEVED
        else:  # PAYER_AMENDED / OTHER -- friction observed, not (believed) terminal
            state = MandateBeliefState.AT_RISK_BELIEVED
        self._update_mandate_belief(
            mandate_ref=payload.mandate_ref,
            account_id=payload.account_id,
            state=state,
            note=payload.advice_text,
            value_date=payload.value_date,
        )

    def _observe_auddis(self, payload: AuddisReport, response: WallResponse) -> None:
        if payload.status == AuddisStatus.NEW_INSTRUCTION_ACCEPTED:
            state = MandateBeliefState.ACTIVE_BELIEVED
        else:  # INSTRUCTION_REJECTED / CANCELLED
            state = MandateBeliefState.LIKELY_DEAD_BELIEVED
        self._update_mandate_belief(
            mandate_ref=payload.mandate_ref,
            account_id=payload.account_id,
            state=state,
            note=payload.status_text,
            value_date=payload.value_date,
        )

    def _update_mandate_belief(
        self,
        *,
        mandate_ref: str,
        account_id: str,
        state: MandateBeliefState,
        note: str,
        value_date: dt.date,
    ) -> None:
        """Overwrite the mandate belief ONLY if this observation is about a
        later (or equal, more-severe-wins-tie) `value_date` than whatever
        currently holds the belief -- a pure function of the observed SET,
        never of `observe()` call order (C-S1/C-S2 order-independence)."""
        existing = self._mandate_beliefs.get(mandate_ref)
        if existing is None or value_date > existing.last_value_date or (
            value_date == existing.last_value_date
            and _MANDATE_SEVERITY[state] >= _MANDATE_SEVERITY[existing.state]
        ):
            self._mandate_beliefs[mandate_ref] = MandateBelief(
                mandate_ref=mandate_ref,
                account_id=account_id,
                state=state,
                last_advice_text=note,
                last_value_date=value_date,
            )

    # -----------------------------------------------------------------
    # Belief read-out -- pure functions of the observed set (order-independent)
    # -----------------------------------------------------------------

    def mandate_belief(self, mandate_ref: str) -> MandateBelief:
        return self._mandate_beliefs.get(
            mandate_ref,
            MandateBelief(mandate_ref=mandate_ref, account_id="", state=MandateBeliefState.UNKNOWN),
        )

    def _arrears_risk_belief(self, account_id: str, as_of: dt.date) -> ArrearsRiskBelief:
        """COMPANY INFERENCE, never ground truth -- see module docstring's
        NAMED SIMPLIFICATIONS on how naive this heuristic deliberately is."""
        dd_failures = [
            f for f in self._dd_failures.get(account_id, [])
            if f.value_date <= as_of and (as_of - f.value_date).days <= self._dd_failure_window_days
        ]
        rail_failures = [
            f for f in self._rail_failures.get(account_id, [])
            if f.value_date <= as_of and (as_of - f.value_date).days <= self._dd_failure_window_days
        ]
        n = len(dd_failures) + len(rail_failures)
        hardship_suggestive = sum(
            1 for f in dd_failures if f.reason_category in _HARDSHIP_SUGGESTIVE_REASONS
        )
        # Tiered PURELY on repeat count -- a single observed failure (of any
        # reason) is noise, not a pattern (module docstring: "repeated
        # INSUFFICIENT_FUNDS -> rising belief", not a single occurrence).
        # `hardship_suggestive` only AMPLIFIES an already-repeated pattern
        # (n==2) from ELEVATED to HIGH; it never on its own turns a single
        # observation into more than WATCH.
        if n == 0:
            return ArrearsRiskBelief.NORMAL
        if n == 1:
            return ArrearsRiskBelief.WATCH
        if n == 2:
            return ArrearsRiskBelief.HIGH if hardship_suggestive >= 2 else ArrearsRiskBelief.ELEVATED
        return ArrearsRiskBelief.HIGH

    def expected_collection_misses(
        self,
        account_id: str,
        as_of: dt.date,
        grace_days: int = DEFAULT_RECONCILIATION_GRACE_DAYS,
        payment_terms_days: int = 14,
        disputed_refs: Sequence[str] = (),
    ) -> List[ExpectedCollectionMiss]:
        """DETECT missed expected collections by reconciling the company's OWN
        issued bills against its OWN observed cash (ruling 2026-07-25 §2). Returns
        one `ExpectedCollectionMiss` per undisputed open invoice that is
        `grace_days` past its due date with a positive outstanding balance --
        the through-the-wall signal for a missed push payment that emits no rail
        failure event.

        WHY THIS IS THROUGH THE WALL: it reads ONLY `age_open_items`, itself a
        pure function of this account's `AccountLedger` (issued `BILL_DEBIT`s and
        observed `PAYMENT_CREDIT`s posted from `WallResponse`s). It never touches
        `PaymentEvent.result`, channel, stress or segment -- exactly like a real
        supplier that knows what it billed and what cash arrived, and nothing
        about WHY a payment did not turn up.

        WHY IT CANNOT FAIL OPEN (R15, ruling §2): it keys on the ledger's actual
        `outstanding_gbp` at `as_of`, so an invoice paid LATE (cash arrived by
        `as_of`) has `outstanding == 0` and is NOT flagged. A detector that
        flagged every ever-overdue invoice regardless of received cash would
        drive the pure-recall detection gap toward zero by flagging everyone --
        the fail-open failure mode. Reading real cash is the guard; the mutation
        test `test_reconciliation_cannot_fail_open` proves a cash-blind variant
        wrongly flags a paid-late invoice while this one does not.

        DETECTION LATENCY (ruling §1): `grace_days` is the observability lag for
        a push-channel miss -- the detector is deliberately SILENT until an
        invoice is `grace_days` past due, so the residual latency is registered,
        never compressed to zero. Order-independent / replay-deterministic
        (C-S1/C-S2): a pure function of the observed ledger set at `as_of`."""
        ledger = self.ledger_book.ledger(account_id)
        aged = age_open_items(
            ledger,
            as_of=as_of,
            payment_terms_days=payment_terms_days,
            disputed_refs=disputed_refs,
        )
        billed_by_ref = _billed_by_invoice(ledger, as_of)
        misses: List[ExpectedCollectionMiss] = []
        for item in aged:
            if item.disputed:
                continue  # a held dispute does not dun and is not a "miss"
            if item.days_overdue < grace_days:
                continue  # within the reconciliation grace window -- not yet observable
            if item.outstanding_gbp <= 0:
                continue  # cash reconciled -- nothing missed (fail-open guard)
            billed = billed_by_ref.get(item.reference, item.outstanding_gbp)
            misses.append(ExpectedCollectionMiss(
                account_id=account_id,
                invoice_ref=item.reference,
                billed_gbp=billed,
                received_gbp=round(max(0.0, billed - item.outstanding_gbp), 2),
                shortfall_gbp=round(item.outstanding_gbp, 2),
                due_date=item.due_date,
                detected_as_of=as_of,
                days_latency=item.days_overdue,
            ))
        misses.sort(key=lambda m: (m.due_date, m.invoice_ref))
        return misses

    def snapshot(
        self,
        account_id: str,
        as_of: Optional[dt.date] = None,
        disputed_refs: Sequence[str] = (),
        payment_terms_days: int = 14,
        reconciliation_grace_days: int = DEFAULT_RECONCILIATION_GRACE_DAYS,
    ) -> PaymentBeliefSnapshot:
        """The belief read-out for one account -- H27's gap-scoring surface.
        Pure function of everything `observe()`d so far for this account
        (order-independent, replay-deterministic): calling this twice with
        the same `as_of` after the same set of `observe()` calls (in any
        order) returns an equal snapshot."""
        as_of = as_of if as_of is not None else dt.date.today()
        ledger: AccountLedger = self.ledger_book.ledger(account_id)
        allocation = ledger.allocate(disputed_refs=disputed_refs, as_of=as_of)
        aged_items = age_open_items(
            ledger, as_of=as_of, payment_terms_days=payment_terms_days, disputed_refs=disputed_refs
        )
        balance_aged = age_balance(ledger, as_of=as_of, payment_terms_days=payment_terms_days)
        buckets = ageing_buckets(aged_items)
        bal_summary = ledger.balance_summary(as_of=as_of)
        mandates = {
            mr: mb for mr, mb in self._mandate_beliefs.items() if mb.account_id == account_id
        }
        dd_failures = sorted(
            (f for f in self._dd_failures.get(account_id, []) if f.value_date <= as_of),
            key=lambda f: (f.value_date, f.mandate_ref),
        )
        rail_failures = sorted(
            (f for f in self._rail_failures.get(account_id, []) if f.value_date <= as_of),
            key=lambda f: (f.value_date, f.reference),
        )
        collection_misses = self.expected_collection_misses(
            account_id,
            as_of=as_of,
            grace_days=reconciliation_grace_days,
            payment_terms_days=payment_terms_days,
            disputed_refs=disputed_refs,
        )
        return PaymentBeliefSnapshot(
            account_id=account_id,
            as_of=as_of,
            allocation=allocation,
            aged_items=aged_items,
            balance_aged_item=balance_aged,
            ageing_buckets=buckets,
            balance_summary=bal_summary,
            mandate_beliefs=mandates,
            arrears_risk_belief=self._arrears_risk_belief(account_id, as_of),
            recent_dd_failures=dd_failures,
            recent_rail_failures=rail_failures,
            detected_collection_misses=collection_misses,
            cash_position_note=_cash_position_note(bal_summary),
        )
