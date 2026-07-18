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
