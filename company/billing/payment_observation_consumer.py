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
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    get_type_hints,
)

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
from company.interfaces.crossing_conversation import (
    ConversationRegister,
    CrossingConversation,
)
from company.interfaces.crossing_silence import (
    SilenceConclusion,
    conclude_silence,
)
from company.interfaces.wall_protocol import (
    DECLARED_POSTURE,
    WallProtocolError,
    assert_registry_fit_for_posture,
    decode_framed_response,
)
from interface.contracts.payment_observable_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    UNSOLICITED_PAYLOAD_TYPES,
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
from interface.contracts.wall_envelope import (
    WallInterim,
    WallNotification,
    WallRequest,
    WallResponse,
    WallStatus,
)

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


@dataclass(frozen=True)
class MisdirectedObservation:
    """A well-formed observation about an account this company DOES NOT SUPPLY.

    WHAT FOUND THIS (atom EP6, pass 42, the blind review's Q6). Pass 42 gave the
    stand-in the ability to emit spec-violating traffic on purpose
    (`simulation.payment_seam_adapter.SpecViolation`). The first thing it emitted
    -- a remittance mis-keyed to another supplier's account reference, the
    payment-seam form of the reviewer's "readings for MPANs you don't supply" --
    went straight through: `LedgerBook.ledger()` creates an account on first
    sight, so the cash CREATED a phantom account and posted into it. Measured on
    three well-formed messages, the company's `portfolio_balance_gbp` came out
    BIT-IDENTICAL to the well-behaved hand-over. The aggregate could not tell
    its own customers' cash from a stranger's.

    THE REAL-WORLD NAME FOR THIS IS SUSPENSE, and that is what this register is:
    cash (or an advice) that arrived, is not refused -- it is a perfectly valid
    message and refusing it would lose the fact -- and may not touch a customer
    ledger, because the company has no customer to touch. A real supplier's
    receivables function books it to an unapplied/suspense account and works it
    off manually.

    SENSING ONLY, same clause as `ExpectedCollectionMiss`: this register
    RECORDS. It returns nothing to the counterparty, raises no query, writes off
    nothing -- those are acting organs, RESERVED to the director's
    dunning/debt/provisioning session (ruling 2026-07-25 §2).

    ONLY POPULATED WHEN THE COMPANY HOLDS A ROSTER. A consumer built without
    `supplied_accounts` cannot ask the question at all, and this register stays
    empty -- see `PaymentObservationConsumer.holds_account_roster`, which exists
    so that "empty" and "unasked" are distinguishable to a reader."""

    correlation_id: str
    account_id: str              # the account named on the wire -- NOT one of ours
    payload_type: str
    amount_gbp: Optional[float]  # None where the payload carries no amount
    observed_at: dt.datetime


@dataclass(frozen=True)
class UnresolvedCrossing:
    """A crossing this company was EXPLICITLY told is not yet resolved -- the
    company-side reading of a non-OK `WallResponse`, and the thing that was
    being thrown away before atom EP6's pass 36.

    WHY IT IS A BELIEF TYPE AND NOT A LOG LINE. `NOT_KNOWABLE_YET` is the one
    answer the envelope's own docstring is proudest of (`WallStatus`: "a
    first-class, honest answer") and the company was collapsing it into the
    same nothing as `TIMEOUT`, `ERROR`, and never hearing at all. Those are
    four different situations for a real accounts-receivable function -- "the
    counterparty says this is under review" is not "the line went quiet" -- and
    a supplier that cannot tell them apart cannot tell an invoice under formal
    dispute from one nobody has answered for. This type is that distinction
    made storable.

    STILL A BELIEF, never truth: it records what the seam SAID and when, never
    why. `status` is the counterparty's word for its own state; nothing here
    claims the underlying fact is a dispute, a delay, or a failure -- that
    reading belongs to whoever consumes it, and the seam does not supply it.

    A crossing leaves this register only when an OK response for the same
    `correlation_id` arrives (see `observe`), which is the envelope's own
    restatement rule -- never by expiry, never by assumption."""

    correlation_id: str
    status: WallStatus           # the counterparty's own word: NOT_KNOWABLE_YET / TIMEOUT / ERROR
    observed_at: dt.datetime     # transaction time of the LATEST non-OK answer for this crossing

    @property
    def awaiting_resolution(self) -> bool:
        """True only for `NOT_KNOWABLE_YET` -- THE distinction this type exists
        to draw, and deliberately the ONLY status branch in this module.

        `NOT_KNOWABLE_YET` is the one non-OK answer that says something about
        the FACT: the counterparty has it and it is not resolvable yet, so an
        answer is still owed and the company is right to keep waiting. The
        others say something about the EXCHANGE (`TIMEOUT`: the answer did not
        arrive, the fact may be perfectly well resolved; `ERROR`: the exchange
        itself failed) and license no such expectation.

        NO BRANCH FOR THOSE TWO *HERE*, and the reason CHANGED at pass 41.
        Until then the honest answer was that nothing in this build could SAY
        `TIMEOUT` or `ERROR` (`tools.wall_channel_census`
        `status_liveness_conformance` reported both UNINHABITED), so a reader
        keyed on either would have been a dead arm. That is no longer true:
        `simulation.payment_seam_adapter.TransportFault` writes both and
        `status_liveness_conformance` now reads 4 of 4.

        The branch still does not belong on THIS property, which is about
        whether the counterparty owes an answer -- and neither of those two
        says it does. What they need is a reader that acts on the difference,
        and it exists: `company.interfaces.crossing_silence.SilenceConclusion`
        (`next_move`), reached from this class via
        `PaymentObservationConsumer.silence_ladder`. This property stays
        deliberately single-branched so the two questions -- "is an answer
        owed?" and "what do I do about it?" -- do not collapse into one."""
        return self.status == WallStatus.NOT_KNOWABLE_YET


@dataclass(frozen=True)
class InboundStreamState:
    """What this company can say about ONE counterparty's unsolicited feed --
    the read-out of the ordering rule `WallNotification.sequence` makes
    possible (blind review Q2, atom EP6).

    WHY THIS EXISTS AT ALL. Every other belief in this module is built from
    messages that ARRIVED. The one question none of them can answer is what
    DIDN'T -- and for a solicited crossing that is tolerable, because the
    company knows what it asked and `crossing_silence` ages the unanswered.
    For unsolicited inbound there is no request to go missing from, so a lost
    ADDACS advice is simply a mandate the company still believes is alive. This
    type is the company noticing.

    `missing_sequences` IS INTERIOR-ONLY, and the limit is real rather than an
    implementation shortcut: gaps are counted strictly BETWEEN the lowest and
    highest sequence observed. A company that joins a feed at sequence 40 has
    not lost 0-39, it was not listening, and reporting them as losses would
    manufacture 40 phantom incidents on the first message of every run.
    THE COST, STATED: a notification lost BEFORE the first one ever seen is
    undetectable here, and no reading of this stream will ever show it.

    `out_of_order_arrivals` is kept SEPARATE from the gap count on purpose. A
    real feed redelivers late far more often than it loses, so a sequence
    arriving below the high-water mark is the NORMAL case, not an incident; a
    single counter mixing the two would read as loss every time the transport
    behaved exactly as expected. A gap that later fills is not a loss at all,
    and `missing_sequences` recomputes from the observed set so it shrinks when
    the straggler lands."""

    sender: str
    received: int
    first_sequence: Optional[int]
    last_sequence: Optional[int]
    missing_sequences: Tuple[int, ...]
    out_of_order_arrivals: int
    duplicates_suppressed: int

    @property
    def has_gap(self) -> bool:
        """Whether this company is missing at least one message it can PROVE
        it was sent -- the question the primitive was built to make askable."""
        return bool(self.missing_sequences)


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
    # Crossings this account was TOLD are unresolved (atom EP6, pass 36), by
    # `observed_at <= as_of` (the Blindfold applies to the register exactly as
    # it applies to every other field here). Attributed to an account ONLY by
    # EXACT equality between a crossing's `correlation_id` and one of this
    # account's own billed `invoice_ref`s -- see `unresolved_crossings`.
    unresolved_crossings: List[UnresolvedCrossing]
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
        posture: Any = DECLARED_POSTURE,
        supplied_accounts: Optional[Iterable[str]] = None,
    ) -> None:
        # THE STARTUP ASSERTION (atom EP6, pass 40 -- the blind review's Q14).
        # This constructor is the startup of the only framed crossing the
        # company has, so it is where "may a stand-in speak to this build"
        # gets asked -- once, before any wire is read, rather than per message.
        # It refuses under a production posture while the counterparty registry
        # still carries a stand-in; see `assert_registry_fit_for_posture` for
        # why an unrecognised posture counts as production.
        assert_registry_fit_for_posture(posture)
        self.ledger_book: LedgerBook = ledger_book if ledger_book is not None else LedgerBook()
        self._dd_failures: Dict[str, List[DDFailureObservation]] = {}
        self._rail_failures: Dict[str, List[RailFailureNote]] = {}
        self._mandate_beliefs: Dict[str, MandateBelief] = {}
        self._recognised_cash_refs: Set[str] = set()
        # SPLIT IN TWO (atom EP6, pass 36), and the split IS the repair: one
        # set for crossings an OK answer has RESOLVED (a fact is in hand, and
        # a re-delivery of it must be a no-op -- C-S2), one map for crossings
        # whose latest answer was non-OK (still open, and a later OK for the
        # same `correlation_id` must still be able to land). A single
        # processed-set could not tell those apart, so the honest "not yet"
        # burned the id and the resolution was silently dropped.
        self._resolved_correlation_ids: Set[str] = set()
        self._unresolved: Dict[str, UnresolvedCrossing] = {}
        self._dd_failure_window_days = dd_failure_window_days
        # THE ACCOUNT ROSTER (atom EP6, pass 42 -- the blind review's Q6).
        # WHO THIS COMPANY SUPPLIES, held as the company's OWN fact and never
        # read off the wire: a message naming an account cannot be the evidence
        # that the account is ours, which is the R15 TAUTOLOGY this check would
        # otherwise be.
        #
        # `None` MEANS UNASKED, NOT EMPTY, and the distinction is the whole of
        # why this is optional. Every caller that existed before pass 42 gets
        # bit-identical behaviour, because a company with no roster has no
        # grounds to reject anything -- but `holds_account_roster` says so, so a
        # reader of an empty `misdirected_observations()` can tell "nothing was
        # misdirected" from "nobody could tell". An empty ROSTER (`set()`) is a
        # different and legitimate statement: a company that supplies nobody,
        # for which every observation is misdirected.
        self._supplied_accounts: Optional[frozenset] = (
            None if supplied_accounts is None else frozenset(supplied_accounts)
        )
        self._misdirected: List[MisdirectedObservation] = []
        # THE CONVERSATION REGISTER (atom EP6, pass 44 -- the blind review's Q3).
        # WHAT THE COMPANY ASKED, held from the moment it asked. Every other
        # register on this consumer is written when something ARRIVES, which is
        # why the company could hold no clock against a crossing whose first
        # message never came (Q5's own row records that as invisible, and Q6's
        # backlog burst has the same missing structure behind it). This one is
        # written on EMISSION. See `company.interfaces.crossing_conversation`.
        self._conversations = ConversationRegister()
        # THE UNSOLICITED INBOUND REGISTER (atom EP6 -- the blind review's Q2).
        # Keyed by SENDER, because `WallNotification.sequence` is a position in
        # one counterparty's stream and comparing two senders' numbering would
        # invent gaps out of nothing. Ids are held per-sender for the same
        # reason: two feeds are entitled to reuse a message id.
        self._notification_ids: Dict[str, Set[str]] = {}
        self._notification_sequences: Dict[str, Set[int]] = {}
        self._notification_out_of_order: Dict[str, int] = {}
        self._notification_duplicates: Dict[str, int] = {}

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

        WHO SENT IT IS CHECKED FIRST (atom EP6, pass 39). The message arrives
        inside a transport frame naming its participant, and
        `decode_framed_response` refuses an unregistered sender, a wrong
        credential, or a release this counterparty is not on -- before the
        envelope is read and long before any belief moves. Until pass 39 this
        line decoded a well-formed envelope from anybody, which is the blind
        review's Q13: the company could not tell a stand-in from a real
        counterparty because the identity check was absent from the path, not
        because the abstraction was good.

        The verified sender is currently DISCARDED here, and that is a stated
        limit rather than an oversight: this consumer has exactly one
        counterparty, so a per-sender belief has nothing to distinguish yet.
        The day a second bank feed exists, the fact is available at this line
        instead of having to be reconstructed.
        """
        _sender, response = decode_framed_response(
            wire, decode_payload=decode_observable_payload
        )
        return self.observe(response)

    def observe(self, response: WallResponse) -> bool:
        """Process one `WallResponse`. Returns True if newly processed,
        False if `response.correlation_id` was already seen (idempotent
        re-delivery is a harmless no-op -- mirrors `AccountLedger.post`'s
        own True/False dedup contract).

        A non-OK response (`NOT_KNOWABLE_YET`/`TIMEOUT`/`ERROR`) carries no
        payload by construction (`WallResponse.__post_init__`) -- an honest
        non-update, never an assumed value. It is RECORDED as an
        `UnresolvedCrossing` (readable via `unresolved_crossings`) and it does
        NOT close the crossing.

        WHAT THIS USED TO DO AND WHY IT WAS WRONG (measured, atom EP6 pass 36).
        Every response marked its `correlation_id` processed, whatever its
        status, and the docstring here claimed that was safe because "a
        resolved response uses a fresh, later `WallResponse`". Fresh RESPONSE,
        yes -- fresh CORRELATION ID, no: `WallResponse` is "matched to its
        request ONLY by `correlation_id`", and a restatement is defined there
        as "a NEW `WallResponse` with a later `observed_at`" for the same
        crossing. So the resolution of a disputed payment arrives on the id
        the "not yet" already burned, and was dropped as a duplicate: an
        `observe` returning False and GBP of received cash never posted, while
        the identical response landed normally on a consumer that had never
        heard the pending answer. The honest answer was the one answer that
        made a fact permanently unhearable.

        THE RULE NOW, and each limb is a different obligation:
          * an id an OK has already resolved -> False, unchanged. C-S2: a
            duplicated delivery of a fact in hand must never post twice.
          * a non-OK whose `observed_at` is not later than the latest non-OK
            already held for that id -> False. Same message redelivered (or
            an older one arriving late, C-S1) is not new information.
          * a later non-OK -> True, and it SUPERSEDES the held one: the
            register carries the counterparty's most recent word, never a
            history (bitemporal restatement, not mutation-in-place of a fact).
          * an OK -> resolves the crossing, clears any unresolved entry, and
            posts as normal, whether or not a non-OK preceded it.

        A non-OK NEVER un-resolves a resolved crossing (limb 1 wins over limb
        3): a response with no payload cannot restate a value, so treating
        "not yet" as revoking cash already observed would be inventing a
        reversal the seam never sent. That is also the conservative direction
        -- it is exactly what this method did before."""
        cid = response.correlation_id
        if cid in self._resolved_correlation_ids:
            return False
        if response.status != WallStatus.OK:
            held = self._unresolved.get(cid)
            if held is not None and response.observed_at <= held.observed_at:
                return False
            self._unresolved[cid] = UnresolvedCrossing(
                correlation_id=cid,
                status=response.status,
                observed_at=response.observed_at,
            )
            return True
        self._unresolved.pop(cid, None)
        self._resolved_correlation_ids.add(cid)
        payload = response.payload
        # THE TERMINAL LEG (Q3). Only an OK closes a conversation, which is the
        # SAME rule this method already applies two branches up: a non-OK is
        # recorded as an `UnresolvedCrossing` and explicitly does not close the
        # crossing, so a register that closed on one would contradict the
        # consumer it lives in.
        #
        # THE LIMIT, named rather than papered over: an input-validation
        # rejection genuinely ends its exchange -- no outcome will ever follow --
        # and it arrives as `WallResponse(status=ERROR)`, which is
        # indistinguishable at this branch from an ERROR the transport raised on
        # a collection still perfectly alive at the bureau. The wire carries an
        # `ErrorDetail.code` that could separate them, but keying the register on
        # a code string would be attribution by spelling, and the company acting
        # on the difference is `crossing_silence`'s question, not this one. So a
        # terminating rejection stays OPEN here and is aged by the ladder, which
        # is the conservative direction: the company keeps expecting an answer
        # it will not get, and can say so, rather than quietly concluding.
        self._conversations.record_terminal(
            correlation_id=cid,
            message_type=type(payload).__name__,
            status=response.status,
            observed_at=response.observed_at,
        )
        if self._is_misdirected(payload):
            # SUSPENSE, not refusal and not a ledger post. The crossing is
            # marked resolved above and stays so: the message arrived, was read
            # and was answered, so a re-delivery of it must remain the same
            # no-op it is for any other observation (C-S2).
            self._misdirected.append(
                MisdirectedObservation(
                    correlation_id=cid,
                    account_id=payload.account_id,
                    payload_type=type(payload).__name__,
                    amount_gbp=getattr(payload, "amount_gbp", None),
                    observed_at=response.observed_at,
                )
            )
            return True
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

    def note_collection_request(self, request: WallRequest) -> None:
        """Record that the company SUBMITTED a collection -- leg 1 (Q3).

        Called at EMISSION, by the caller that sent the request, and this is the
        structural change pass 44 makes: until now every register on this
        consumer was written by an arrival, so a crossing existed, as far as the
        company was concerned, only once something came back about it. A
        collection lost on the way to the bureau and a collection never
        submitted read identically, and so did a collection still in the
        three-day cycle.

        NOT AN OBSERVATION, which is why it is a separate method and not a
        branch of `observe`. Nothing crossed the wall inbound here; this is the
        company writing down its own act, and it is the only admissible evidence
        that the act happened (see `ConversationRegister`'s docstring on why a
        message can never supply it).

        Idempotent on `correlation_id` (C-S2): re-submitting is the same
        exchange, and re-opening would discard legs already heard on it."""
        self._conversations.open_conversation(
            correlation_id=request.correlation_id,
            request_type=request.request_type,
            emitted_at=request.emitted_at,
        )

    def observe_interim(self, interim: WallInterim) -> bool:
        """Process one NON-TERMINAL leg -- leg 2 of a multi-leg exchange (Q3).

        Returns True if newly filed, False for a redelivery of a leg already
        held: the same C-S2 dedup contract `observe`/`observe_unsolicited` use,
        so a transport that delivers twice cannot inflate `leg_count` into a
        measure of itself.

        RAISES `UnaskedLeg` for a `correlation_id` this company never opened.
        That refusal is deliberate and is the R15 clause of this leg -- see
        `ConversationRegister.record_interim`. It does NOT touch the ledger, the
        cash position, or any belief: an acknowledgement resolves nothing, so a
        version of this that moved a figure would be reading a resolution into
        the one message defined by not being one."""
        return self._conversations.record_interim(interim)

    def conversation(self, correlation_id: str) -> Optional[CrossingConversation]:
        """The exchange behind one correlation id, or `None` where this company
        has no record of one at all."""
        return self._conversations.conversation(correlation_id)

    def conversations(self) -> Tuple[CrossingConversation, ...]:
        """Every exchange this company has a record of, oldest first."""
        return self._conversations.conversations()

    def open_conversations(self) -> Tuple[CrossingConversation, ...]:
        """Exchanges asked about and not yet terminally answered -- INCLUDING
        those nothing has come back on, the reading that did not exist before
        the request register."""
        return self._conversations.open_conversations()

    def multi_leg_conversations(self) -> Tuple[CrossingConversation, ...]:
        """Exchanges that got past the trivial ask/answer pair. Q3's own
        subject, made countable on a live run."""
        return self._conversations.multi_leg_conversations()

    def observe_unsolicited(self, notification: WallNotification) -> bool:
        """Process one UNSOLICITED inbound message (blind review Q2).

        Returns True if newly processed, False if this `(sender,
        notification_id)` has been seen before -- the same True/False dedup
        contract `observe` uses, for the same C-S2 reason.

        WHY THIS IS A SEPARATE ENTRY POINT AND NOT A BRANCH IN `observe`. The
        two primitives have genuinely different rules, and collapsing them
        would mean picking one set and being wrong for the other:

          * IDENTITY. `observe` dedups on `correlation_id` -- the company's own
            key for a thing it asked. There is no such key here, so identity is
            the SENDER's `notification_id`, scoped per sender.
          * RESOLUTION. A response can be superseded by a later answer on the
            same id (`_unresolved`); a notification resolves nothing and
            supersedes nothing. It is a fact that happened, not an answer that
            improved.
          * ORDER. A response set is deliberately order-blind. A notification
            stream is ORDERED, and the ordering carries the one fact this
            company could not otherwise have: what it never received.

        BELIEF IS STILL ORDER-INDEPENDENT. The sequence bookkeeping records
        arrival order, but the mandate belief this feeds is updated through
        `_update_mandate_belief`, which is a pure function of the observed set
        by `value_date`. So a stream replayed in any order reaches the same
        belief and the same gap reading -- the sequence tells the company what
        is MISSING, never what is TRUE.

        REFUSES rather than guesses on a notification this seam does not
        define, matching `observe`'s final `else`: a payload type the contract
        never declared unsolicited is a routing error, and accepting it here
        would let any payload skip the response leg's checks by arriving in the
        other envelope.
        """
        payload = notification.payload
        if not isinstance(payload, UNSOLICITED_PAYLOAD_TYPES):
            raise ValueError(
                f"payment_observation_consumer: {type(payload).__name__!r} arrived "
                "as unsolicited inbound but this seam does not declare it so -- "
                "see UNSOLICITED_PAYLOAD_TYPES"
            )
        sender = notification.sender
        seen_ids = self._notification_ids.setdefault(sender, set())
        if notification.notification_id in seen_ids:
            # C-S2: at-least-once delivery. A redelivery is a no-op and must
            # NOT re-count in the stream stats, or a chatty transport would
            # look like a busy counterparty.
            self._notification_duplicates[sender] = (
                self._notification_duplicates.get(sender, 0) + 1
            )
            return False
        seen_ids.add(notification.notification_id)

        sequences = self._notification_sequences.setdefault(sender, set())
        if sequences and notification.sequence < max(sequences):
            # C-S1: late arrival, the expected case. Recorded, never treated
            # as an error -- see `InboundStreamState.out_of_order_arrivals`.
            self._notification_out_of_order[sender] = (
                self._notification_out_of_order.get(sender, 0) + 1
            )
        sequences.add(notification.sequence)

        if self._is_misdirected(payload):
            # Same suspense answer the response leg gives (Q6): the message was
            # read and is accounted for in this stream's numbering -- a gap
            # must not open just because the advice was about a stranger's
            # mandate -- but it moves no belief of ours.
            self._misdirected.append(
                MisdirectedObservation(
                    correlation_id=notification.notification_id,
                    account_id=payload.account_id,
                    payload_type=type(payload).__name__,
                    amount_gbp=getattr(payload, "amount_gbp", None),
                    observed_at=notification.observed_at,
                )
            )
            return True

        self._observe_addacs(payload, notification)
        return True

    def inbound_stream(self, sender: str) -> InboundStreamState:
        """This company's reading of one counterparty's unsolicited feed.

        Recomputed from the observed set on every call rather than maintained
        incrementally, so a late straggler filling a hole makes the gap
        disappear without anyone having to remember to un-count it."""
        sequences = self._notification_sequences.get(sender, set())
        if not sequences:
            return InboundStreamState(
                sender=sender,
                received=0,
                first_sequence=None,
                last_sequence=None,
                missing_sequences=(),
                out_of_order_arrivals=self._notification_out_of_order.get(sender, 0),
                duplicates_suppressed=self._notification_duplicates.get(sender, 0),
            )
        low, high = min(sequences), max(sequences)
        return InboundStreamState(
            sender=sender,
            received=len(sequences),
            first_sequence=low,
            last_sequence=high,
            missing_sequences=tuple(sorted(set(range(low, high + 1)) - sequences)),
            out_of_order_arrivals=self._notification_out_of_order.get(sender, 0),
            duplicates_suppressed=self._notification_duplicates.get(sender, 0),
        )

    def inbound_senders(self) -> Tuple[str, ...]:
        """Every counterparty this company has heard unsolicited traffic from.

        Present so a caller can reach `inbound_stream` without already knowing
        the sender id -- an instrument that has to be told which feed to ask
        about can only ever check the feeds someone remembered to name."""
        return tuple(sorted(self._notification_sequences))

    @property
    def holds_account_roster(self) -> bool:
        """Whether this company can tell its own accounts from a stranger's.

        Public so that an empty `misdirected_observations()` is readable: False
        here means the question was never askable, which is a different fact
        from "nothing arrived for an account we do not supply" and must not be
        reported as the same clean bill."""
        return self._supplied_accounts is not None

    @property
    def supplied_accounts(self) -> Optional[frozenset]:
        """The roster itself, or None where none is held.

        Public for the reason `dd_failure_window_days` was made public: when the
        private attribute is the only route to a value, every instrument that
        needs it reaches for a constant somewhere else and reports the wrong
        company. A supplier knows its own account list; nothing here crosses the
        wall, because it is the company's own fact and not a read of the world."""
        return self._supplied_accounts

    def note_supplied_account(self, account_id: str) -> None:
        """Record that this company now supplies `account_id`.

        THE ROSTER GROWS, because a real supplier's does. The constructor form
        suits a harness that knows its whole book up front; a RUNNING company
        learns of an account when it acquires and bills one, which is what this
        is called at. It is the company writing down its OWN fact -- never a
        read of the world, and never derived from anything that arrived on the
        wire, which is the property that keeps the misdirection check from
        being a tautology.

        CALLING THIS STARTS A ROSTER on a consumer that held none: the company
        moves from "cannot tell whose account this is" to "can", and
        `holds_account_roster` flips with it. That is the intended transition
        and the reason the method exists rather than the roster being
        constructor-only."""
        if not isinstance(account_id, str) or not account_id:
            raise ValueError(
                "payment_observation_consumer: an account this company supplies "
                f"must be a non-empty id, got {account_id!r}"
            )
        current = self._supplied_accounts or frozenset()
        self._supplied_accounts = current | {account_id}

    def misdirected_observations(self) -> Tuple[MisdirectedObservation, ...]:
        """Everything that arrived, well-formed, about an account this company
        does not supply -- the suspense register (atom EP6, Q6). Empty and
        meaningless unless `holds_account_roster`."""
        return tuple(self._misdirected)

    def misdirected_cash_gbp(self) -> float:
        """Cash this company was told about that belongs to nobody it supplies,
        and therefore did NOT post. The figure that was invisible before pass
        42: it used to land in `portfolio_balance_gbp` under a phantom account
        and move no headline at all."""
        return round(
            sum(m.amount_gbp for m in self._misdirected if m.amount_gbp is not None), 2
        )

    def _is_misdirected(self, payload: Any) -> bool:
        """Is this payload about an account we do not supply?

        FAILS CLOSED IN BOTH DIRECTIONS THAT MATTER. With no roster held the
        answer is False -- the company genuinely cannot tell, and inventing a
        rejection would be worse than the gap `holds_account_roster` publishes.
        With a roster held, a payload carrying NO `account_id` RAISES rather
        than passing: every one of this seam's six response payload types
        declares `account_id` (`OBSERVABLE_PAYLOAD_FIELDS`), so an object
        without one is not a payload this consumer understands, and treating it
        as "not misdirected" would be the FAIL-OPEN-on-malformed pattern R15
        names."""
        if self._supplied_accounts is None:
            return False
        account_id = getattr(payload, "account_id", None)
        if not isinstance(account_id, str):
            raise ValueError(
                "payment_observation_consumer: an account roster is held but "
                f"payload {type(payload).__name__!r} carries no account_id -- "
                "this seam's payload types all declare one, so the roster check "
                "cannot be skipped for it"
            )
        return account_id not in self._supplied_accounts

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

    def _observe_addacs(self, payload: AddacsAdvice, envelope: Any = None) -> None:
        # `envelope` is the WallResponse or WallNotification this advice
        # arrived in, and is deliberately UNUSED: the mandate belief is a pure
        # function of the payload's own `advice_type` and `value_date`, so the
        # same advice moves the belief identically whichever primitive carried
        # it. Kept in the signature because the sibling `_observe_*` handlers
        # all take it and a reader comparing them should see one shape.
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

    def unresolved_crossings(
        self,
        account_id: Optional[str] = None,
        as_of: Optional[dt.date] = None,
    ) -> List[UnresolvedCrossing]:
        """Crossings whose latest answer was non-OK -- what the company was
        TOLD it does not yet have, as distinct from what it never heard about.

        `as_of` applies the Blindfold to the register itself: a crossing whose
        answer arrived after the decision clock is not knowable at `as_of` and
        is excluded, exactly as `snapshot`'s other fields are filtered.

        ATTRIBUTION, and its limit stated rather than implied. A non-OK
        response carries NO payload by construction, so it carries no
        `account_id` -- the correlation id is the whole of what arrived. With
        `account_id` given, a crossing is attributed by EXACT equality between
        its `correlation_id` and one of that account's own billed
        `invoice_ref`s. That join is exact where the caller sets
        `correlation_id == invoice_ref` (the DD path in the live triad) and
        matches NOTHING otherwise -- deliberately: a customer-initiated push
        payment quotes no invoice reference, and inferring the account by
        parsing the id would be attribution by substring, which is wrong more
        quietly than it is right. Unattributable crossings are still visible in
        the account-less call, which is the register's complete reading."""
        crossings = [
            c for c in self._unresolved.values()
            if as_of is None or c.observed_at.date() <= as_of
        ]
        if account_id is not None:
            billed_refs = set(_billed_by_invoice(
                self.ledger_book.ledger(account_id),
                as_of if as_of is not None else dt.date.max,
            ))
            crossings = [c for c in crossings if c.correlation_id in billed_refs]
        crossings.sort(key=lambda c: (c.observed_at, c.correlation_id))
        return crossings

    def silence_ladder(
        self,
        as_of: dt.datetime,
        account_id: Optional[str] = None,
    ) -> List[SilenceConclusion]:
        """Every open crossing, AGED -- how long it has been since the company
        last heard anything, and what it therefore owes (atom EP6, pass 41, the
        blind review's Q5).

        THE GAP THIS CLOSES. `unresolved_crossings` answers "what am I waiting
        for"; nothing answered "how long have I been waiting, and is that too
        long". A crossing the counterparty said 'not yet' to and then never
        mentioned again read identically at one minute and at one year, because
        the register has no clock in it. This method is that clock, and
        `company.interfaces.crossing_silence` is where the horizons and the
        obligation at each one are defined -- deliberately not here, because the
        ladder is a property of the WALL and not of payments.

        NOTHING MOVES. This is a pure read: no crossing is evicted, no status is
        rewritten, and calling it twice changes nothing. A crossing does not
        leave the register by expiry (`UnresolvedCrossing`'s own rule, which
        pass 41 preserves deliberately) -- ageing out is not being answered, and
        a company that dropped the crossing at five working days would be
        assuming a resolution the seam never sent.

        THE CONCLUSION IS THE COMPANY'S, NEVER THE COUNTERPARTY'S. At the
        abandonment horizon a `SilenceConclusion` carries
        `concluded_status=WallStatus.TIMEOUT` -- manufactured by this company's
        own clock, because no message will ever bring it. The counterparty's own
        last word stays in `heard_status`, and the register keeps it unaltered.
        A real counterparty that has gone quiet cannot send you a TIMEOUT; if
        the company wrote one into the register it would be inventing a message
        it never received.

        SENSING ONLY (ruling 2026-07-25 s2). The obligations returned are
        strings naming what SHOULD happen. Nothing here dunns, flags, prices,
        provisions, or re-requests -- those remain the director's reserved
        dunning/debt/provisioning decisions.

        `as_of` is a datetime, not a date, because the first horizon is one
        MINUTE and a date cannot express it. It applies the Blindfold exactly as
        `unresolved_crossings` does: a crossing heard after the decision clock
        is not visible here either.
        """
        crossings = self.unresolved_crossings(
            account_id=account_id, as_of=as_of.date()
        )
        return [
            conclude_silence(
                correlation_id=c.correlation_id,
                heard_status=c.status,
                last_heard_at=c.observed_at,
                as_of=as_of,
            )
            for c in crossings
            if c.observed_at <= as_of
        ]

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
            unresolved_crossings=self.unresolved_crossings(account_id, as_of=as_of),
            cash_position_note=_cash_position_note(bal_summary),
        )
