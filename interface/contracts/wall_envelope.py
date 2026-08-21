"""The wall envelope — the ONE shared request/response shape for every
crossing of the sim/saas seam (`interface/`), and (per docs/design/
GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md Part 1) the same shape the
company-internal seams reuse. This module defines the generic envelope only
-- no payload lives here. `payment_observable_seam.py` is the first
crossing to be expressed in it (Ordered BUILD task list item 1 + 2 of that
design doc, done together for the payment triad, atom W4_4).

WHY an envelope, not a plain function call: the design doc's §1.1 lists five
ways a real endpoint boundary differs from an in-process call --

  1. request and response are separate events in time (C-S3),
  2. delivery is at-least-once / possibly-duplicated (idempotency, C-S2),
  3. delivery can be late, out of order, or never arrive (C-S1),
  4. the answer can be a well-formed "not yet knowable" rather than a value
     or an exception (the Point-in-Time Blindfold, lifted onto the wire),
  5. a value can later be RESTATED (a bitemporal fact), never mutated.

All five must be representable in the contract NOW even though today's
transport is in-process Python (CLAUDE.md scale-readiness: cheap today,
brutal to retrofit). The shape below mirrors `BitemporalRecord`
(`company/interfaces/bitemporal_event_log.py`) valid_time/transaction_time
split and `ReplayStatus` (`company/interfaces/recorded_sim_interface.py`)
OK/NOT_KNOWABLE_YET/ERROR status enum -- same wall, same idiom, extended
with TIMEOUT for a real network boundary.

Frozen + Generic: every crossing gets its own `WallRequest[Payload]` /
`WallResponse[Payload]` specialisation by parametrising these two generics;
only the payload type differs per crossing (design doc §1.2, "only the
payload type differs").
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Generic, Optional, TypeVar

P = TypeVar("P")
R = TypeVar("R")
N = TypeVar("N")
# `IT`, not `I`: a single-capital-I name is flagged ambiguous (ruff E741).
IT = TypeVar("IT")


class WallStatus(str, Enum):
    """The four-way status a crossing can resolve to. `NOT_KNOWABLE_YET` is
    a first-class, honest answer -- the same discipline as
    `BitemporalEventLog.as_known_at()` returning `None` (never a KeyError,
    never a silently fabricated zero) lifted onto the wire. `TIMEOUT` is
    distinct from `ERROR`: a timeout says nothing about whether the fact
    exists, only that the answer did not arrive in time -- the CALLER'S
    obligation on receipt (e.g. "fall back to the last known price, flagged
    stale") is a company-side reading of the seam, not something this
    contract itself decides."""

    OK = "OK"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    NOT_KNOWABLE_YET = "NOT_KNOWABLE_YET"


@dataclass(frozen=True)
class ErrorDetail:
    """Structured error payload for `WallResponse.error`. Present only when
    `status == WallStatus.ERROR`."""

    code: str
    message: str


@dataclass(frozen=True)
class WallRequest(Generic[P]):
    """One request crossing the wall. `correlation_id` is BOTH the
    idempotency key (C-S2: a resolver that has already answered a
    correlation id must return the same response, never recompute against
    fresh state) and the response-matching key (C-S1: the response can
    arrive on its own, at any later time, matched by this id alone -- never
    by request/response being the same call frame).

    `as_of` is the point-in-time decision clock (the Blindfold): a resolver
    must never answer with a fact whose own `observed_at` is later than the
    requester's `as_of`. `emitted_at` is this request's own transaction time
    (when it was raised), kept separate from `as_of` because a request can
    be raised well after the decision clock it is asking about (e.g. a
    reconciliation job replaying old requests) -- WallRequest never conflates
    "when I asked" with "as of when I want the answer"."""

    correlation_id: str
    request_type: str
    schema_version: int
    as_of: dt.datetime
    emitted_at: dt.datetime
    payload: P


@dataclass(frozen=True)
class WallResponse(Generic[R]):
    """One response crossing the wall -- a SEPARATE event in time from the
    request that provoked it (C-S3: never same-step resolution). Matched to
    its request ONLY by `correlation_id`; nothing else links them, so a
    consumer that has never seen (or has since forgotten) the original
    request can still process this response correctly on arrival --
    tolerating late, out-of-order, one-at-a-time, or (structurally) NEVER
    arrival.

    Bitemporal by construction, mirroring `BitemporalRecord`:
      * `observed_at`  -- transaction_time: when THIS answer became known.
      * `valid_time`   -- what real-world period/instant the answer is
        ABOUT. `None` is valid (not every observable payload is about a
        dated fact); where the payload itself carries its own date field
        (e.g. a payment's `value_date`), `valid_time` should mirror it for
        the *envelope*-level bitemporal read; a restatement (e.g. a
        superseding settlement run) is always a NEW `WallResponse` with a
        later `observed_at` for the same `valid_time`, never an edit to a
        stored response object.

    `payload` is `None` unless `status == OK`; `error` is populated only
    when `status == ERROR`. Enforced in `__post_init__` so a malformed
    envelope (e.g. a payload silently attached to a `NOT_KNOWABLE_YET`
    response) fails at construction, not at some later, quieter read site --
    a contract that CAN leak by construction is worse than one that cannot.
    """

    correlation_id: str
    status: WallStatus
    schema_version: int
    observed_at: dt.datetime
    valid_time: Optional[dt.date]
    payload: Optional[R]
    error: Optional[ErrorDetail] = None

    def __post_init__(self) -> None:
        if self.status == WallStatus.OK and self.payload is None:
            raise ValueError("WallResponse(status=OK) must carry a payload")
        if self.status != WallStatus.OK and self.payload is not None:
            raise ValueError(
                f"WallResponse(status={self.status}) must not carry a payload "
                "-- only an OK response may resolve a fact"
            )
        if self.status == WallStatus.ERROR and self.error is None:
            raise ValueError("WallResponse(status=ERROR) must carry an ErrorDetail")
        if self.status != WallStatus.ERROR and self.error is not None:
            raise ValueError(f"WallResponse(status={self.status}) must not carry an error")


@dataclass(frozen=True)
class WallInterim(Generic[IT]):
    """A NON-TERMINAL leg of a conversation -- the wall's FOURTH primitive, and
    the answer to the blind review's Q3 ("show me a conversation with more than
    two legs"). Its stated fail shape was that if the primitive cannot express a
    worked multi-leg case -- the reviewer's own examples were DCC
    request/ack/response/alert and a switch with objection -- "the layer covers
    only the trivial exchanges", which is exactly what this build had: three
    shapes that between them could say ASK, ANSWER and TELL, and nothing that
    could say NOT YET FINISHED.

    WHY THE EXISTING SHAPES COULD NOT CARRY IT, since a fourth primitive needs
    that argument made rather than assumed.

      * NOT a second `WallResponse`. `correlation_id` on a response is the
        IDEMPOTENCY key -- its own docstring's rule is that a resolver which has
        already answered a correlation id must return the SAME response, never
        recompute. Two different responses on one id is not a long conversation,
        it is a broken contract, and a consumer is entitled to treat the second
        as a restatement of the first.
      * NOT a `WallNotification`. A notification is defined by having NO request
        behind it; giving it a correlation id recreates, in mirror image, the
        very fail Q2 named ("we model it as a response to a synthetic request").
      * NOT a flag on the request. The interim travels WORLD -> COMPANY and
        arrives later; the request has already been sent.

    THE ORDERING CLAIM, and it is what makes this a conversation rather than a
    bag of correlated messages. `leg` is the position of this message in its own
    exchange, and it starts at 2 BY CONSTRUCTION: leg 1 is the `WallRequest`, so
    an interim is never the opening leg -- something was asked, and this says it
    is in progress. Refused below rather than documented, on
    `WallResponse.__post_init__`'s reasoning that a contract which CAN leak by
    construction is worse than one that cannot.

    NO `status`, DELIBERATELY, and this is the load-bearing absence. A status is
    a resolution -- OK, ERROR, NOT_KNOWABLE_YET all close the question one way or
    another, and `TIMEOUT` says the answer will not come. Give an interim a
    status and nothing distinguishes it from a `WallResponse`; the third leg
    collapses back into the second and the conversation is two legs again wearing
    a longer name. An interim's whole content is "received, in progress, here is
    what I can tell you so far", which is why `payload` is MANDATORY -- an
    in-progress report that reports nothing is not a leg.

    A TERMINAL REFUSAL IS STILL A `WallResponse`, which is the corollary worth
    stating because it is where a reader will otherwise put a Bacs input
    rejection. A submission REJECTED at input validation ends the conversation
    at leg 2 and no outcome will ever follow; that is an answer, and
    `WallResponse(status=ERROR)` already says it exactly. Only ACCEPTANCE is an
    interim, because only acceptance leaves something still owed."""

    correlation_id: str
    leg: int
    interim_type: str
    schema_version: int
    observed_at: dt.datetime
    payload: IT

    def __post_init__(self) -> None:
        if self.payload is None:
            raise ValueError(
                "WallInterim must carry a payload -- a leg that says the exchange "
                "is in progress and nothing else is not worth a leg (an interim "
                "has no status to be honestly empty behind)"
            )
        if not self.correlation_id:
            raise ValueError(
                "WallInterim must carry a correlation_id -- an interim is BY "
                "DEFINITION about a request that was made; a message with no "
                "request behind it is a WallNotification"
            )
        if self.leg < 2:
            raise ValueError(
                f"WallInterim leg must be >= 2, got {self.leg} -- leg 1 is the "
                "WallRequest, so an interim can never be the opening leg of its "
                "own conversation"
            )


@dataclass(frozen=True)
class WallNotification(Generic[N]):
    """UNSOLICITED INBOUND -- the wall's THIRD primitive, and the answer to the
    blind review's Q2 ("where does unsolicited inbound live -- pushed D0010s,
    CSS notifications, DCC alerts, AQ updates?"). Its stated fail shape was
    "we model it as a response to a synthetic request", which is exactly what
    this build did until this type existed: an ADDACS advice -- the payer's
    bank telling the company about a mandate the company never touched -- was
    a `WallResponse` carrying a `correlation_id` for a `WallRequest` that no
    module anywhere constructs.

    A notification is NOT a response, and the difference is not cosmetic. Three
    structural consequences, each of which is why this could not be a flag on
    `WallResponse`:

    1. NO `correlation_id`, because there is no request to correlate to.
       Minting a synthetic one would recreate the reviewer's named fail and
       would also be a live lie: `WallResponse` promises its id matches a
       request, and a consumer is entitled to that.

    2. NO `status`, and `payload` is MANDATORY. A status is an answer to a
       question -- `NOT_KNOWABLE_YET` means "you asked, I cannot say yet".
       Nobody asked here, so there is nothing for a payload-less notification
       to be honest ABOUT; a message that arrives unbidden and says nothing is
       not a message. Enforced below rather than documented, for
       `WallResponse.__post_init__`'s reason: a contract that CAN leak by
       construction is worse than one that cannot.

    3. `sender` + `sequence` -- THE ORDERING RULE, and the reason this type
       earns its keep. A response stream is deliberately unordered: matched by
       id alone, C-S1 tolerates late and out-of-order arrival, and the consumer
       reconstructs truth from the SET. An unsolicited stream cannot work that
       way, because the company never knows what it was owed. `sequence` is the
       counterparty's own position counter for ITS stream, which makes two
       things detectable that were previously invisible:
         * a GAP -- the company can tell it MISSED a notification, the one
           question no amount of reading the messages it did receive can
           answer;
         * a REORDER -- distinguishable from a gap, because a real feed
           redelivers late rather than losing.
       `notification_id` is the counterparty's own message identity and is the
       IDEMPOTENCY key (C-S2: at-least-once delivery, so the same advice can
       arrive twice and the second must be a no-op). It is deliberately a
       SEPARATE field from `sequence`: a redelivery keeps its id AND its
       sequence, but a counterparty that renumbers on replay must still be
       deduplicable.

    `observed_at` / `valid_time` carry the same bitemporal meaning as on
    `WallResponse` -- when the counterparty observed the fact, and what period
    the fact is about -- so a restatement is a NEW notification with a later
    `observed_at`, never an edit.
    """

    notification_id: str
    notification_type: str
    schema_version: int
    sender: str
    sequence: int
    observed_at: dt.datetime
    valid_time: Optional[dt.date]
    payload: N

    def __post_init__(self) -> None:
        if self.payload is None:
            raise ValueError(
                "WallNotification must carry a payload -- an unsolicited message "
                "has no question to be honestly silent about (use WallResponse "
                "with a status for that)"
            )
        if not self.notification_id:
            raise ValueError(
                "WallNotification must carry a notification_id -- it is the "
                "idempotency key for an at-least-once stream (C-S2)"
            )
        if not self.sender:
            raise ValueError(
                "WallNotification must name its sender -- `sequence` is a "
                "position in ONE counterparty's stream and is meaningless "
                "without it"
            )
        if self.sequence < 0:
            raise ValueError(
                f"WallNotification sequence must be non-negative, got {self.sequence}"
            )
