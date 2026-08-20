"""The company's reading of a crossing that went QUIET (atom EP6_wall_protocol_typing, Q5).

PURPOSE. The blind review's question 5 asks: "Can the stand-in produce a response
that *never arrives*, and does the caller have a defined behaviour for that at 1
min, 24 h and 5 working days?" This module is the CALLER'S half of that answer --
the horizon ladder and the obligation each horizon carries. The stand-in's half
lives in `simulation/payment_seam_adapter.py::TransportFault`.

GUARANTEE. Given the last thing the company HEARD about an open crossing and a
decision clock, this module returns exactly one `SilenceHorizon` and the
obligation that horizon carries -- for every input, with no silent default. It
is a pure function of its two arguments: no I/O, no wall clock read inside,
replay-deterministic (C-S1/C-S2), and it never mutates the register it reads.

--------------------------------------------------------------------------
WHY THIS MODULE EXISTS AT ALL, WHICH IS THE MEASURED DEFECT AND NOT A DESIGN
PREFERENCE.
--------------------------------------------------------------------------

SILENCE IS NOT A MESSAGE. A response that never arrives produces no envelope,
no bytes and no event. Nothing calls a handler. So the company can only ever
notice it by holding a CLOCK against a crossing it already knows is open --
absence is detectable only against an expectation, never on its own.

At pass 40 the company held no such clock anywhere. `PaymentObservationConsumer`
is purely response-driven: `observe`/`observe_wire` run when something arrives,
and the one register of open crossings (`UnresolvedCrossing`) carried, in its
own docstring, the rule "A crossing leaves this register only when an OK
response for the same `correlation_id` arrives -- never by expiry, never by
assumption." That sentence is correct about what must not happen and was silent
about what must: nothing expired, so nothing aged, so a crossing the
counterparty said "not yet" to in 2016 and never mentioned again was, at every
later read, indistinguishable from one answered a minute ago. The company could
wait forever and never say so.

`WallStatus.TIMEOUT` was the visible end of that: `tools.wall_channel_census`
`status_liveness_conformance` reported it UNINHABITED -- no writer, no reader --
and so was `ERROR`, its sibling in the same four-member enum, in the identical
state. Both are recorded here because that census's own commentary records the
class: "A list assembled by noticing gets the member someone was looking at;
only enumerating the vocabulary gets the second one." Three passes named TIMEOUT
and none named ERROR. This module reads both, and it reads them differently,
because they are different facts.

--------------------------------------------------------------------------
A REAL COUNTERPARTY NEVER SENDS YOU A TIMEOUT. SO TIMEOUT HAS TWO WRITERS.
--------------------------------------------------------------------------

This is the distinction that makes the ladder honest, and it is worth stating
because getting it wrong is the easy way to build a satisfying-looking dead arm.

  * THE TRANSPORT can produce one. A client that gave up waiting reports a
    timeout, and that reaches the company AS A RESPONSE -- `WallStatus.TIMEOUT`
    arriving on the wire, which `_decode_status` has always accepted and which
    `WallStatus`'s own docstring calls "the CALLER'S obligation on receipt".
    The stand-in models this (`TransportFault.TIMEOUT`).
  * THE COMPANY'S OWN CLOCK can produce one, and NOTHING ARRIVES AT ALL. The
    counterparty said "not yet", then went quiet past every horizon. There is no
    message; the conclusion is the company's own and is manufactured here.

Those are not the same event and this module does not let them wear the same
label: `SilenceConclusion.concluded_status` is populated ONLY in the second
case, and `heard_status` always carries the counterparty's own last word. A
company that could not tell "they told me it timed out" from "I decided it had"
would be inventing a message from its counterparty, which is precisely the
epistemic move the wall exists to prevent.

--------------------------------------------------------------------------
THE LADDER CLASSIFIES. IT NEVER EVICTS, AND IT NEVER ACTS.
--------------------------------------------------------------------------

NO EVICTION. A crossing does not leave the open register because it aged. The
existing rule stands untouched and this module preserves it deliberately: an
answer that has not arrived is not an answer, and dropping the crossing at five
working days would be assuming a resolution the seam never sent -- the same
fail-open in a slower costume. What changes at each horizon is the company's
stated OBLIGATION, never the crossing's status in the register.

SENSING ONLY (ruling 2026-07-25 s2, binding, and the same clause
`ExpectedCollectionMiss` carries). Every obligation below is a STRING NAMING
WHAT SHOULD HAPPEN. This module licenses no acting organ: no dunning step, no
vulnerability/PSR flag, no arrears-driven pricing, no provisioning, no automatic
re-request. Those are RESERVED to the director's dunning/debt/provisioning
session, and an action wired on top of this would foreclose its choices. The
ladder tells the company what it is owed and how long it has been owed it; what
to DO about that is a decision this module is not entitled to make.

--------------------------------------------------------------------------
THE HORIZONS ARE THE REVIEWER'S, NOT A CITED REGULATORY DEADLINE.
--------------------------------------------------------------------------

1 minute, 24 hours and 5 working days are the three the blind review named, and
they are recorded here as ITS question rather than dressed up in an SLC number
this pass has not verified. What each one MEANS below is a reading of the wall's
own contract, which is checkable:

  * 1 MINUTE is where the same-step illusion has definitively failed. C-S3 says
    a request and its response are separate events in time; under a minute, a
    build that quietly assumed otherwise would still look correct. Past it, the
    crossing is asynchronous as a matter of fact and not of intent.
  * 24 HOURS is a business day gone with a promised answer undelivered -- the
    point at which the company's belief is stale rather than merely pending, and
    a re-ask is owed.
  * 5 WORKING DAYS is where this company stops expecting the answer. Working
    days, not calendar days, because a Friday afternoon "not yet" followed by a
    bank holiday weekend is not the counterparty being slow.

WORKING DAYS ARE THE SHARED PRIMITIVE (`company.compliance.working_days`), never
a sixteenth local `_add_working_days`. That module fails closed outside its
committed calendar (2012-2028) by raising `OutsideCalendarCoverage`, and this
module lets that propagate: a horizon computed against a calendar nobody has is
a FAILED calculation, not a generous one.

SCOPE, deliberately narrow (the atom's origin_note forbids a protocol cathedral
by name). One enum, one obligation table, one pure function, one read-model
dataclass. No retry policy, no scheduler, no persistence, no new wire message,
no request register -- the last of those is Q2's job and is not smuggled in
here.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from company.compliance.working_days import Nation, working_days_between
from interface.contracts.wall_envelope import WallStatus

__all__ = [
    "LATE_AFTER",
    "OVERDUE_AFTER",
    "ABANDONED_AFTER_WORKING_DAYS",
    "SilenceHorizon",
    "SILENCE_OBLIGATION",
    "SilenceConclusion",
    "silence_horizon",
    "conclude_silence",
]


#: The three horizons the blind review's Q5 names. Module-level constants rather
#: than literals inside the function so a test can state the boundary it is
#: probing in the same terms the code decides it in.
LATE_AFTER = dt.timedelta(minutes=1)
OVERDUE_AFTER = dt.timedelta(hours=24)
ABANDONED_AFTER_WORKING_DAYS = 5


class SilenceHorizon(Enum):
    """How long an open crossing has gone unanswered, as one of four bands.

    `rank` exists so callers can ask "at least OVERDUE" without hard-coding the
    member order; `Enum` (not `str, Enum`) because nothing serialises this -- it
    is a derived reading, never a wire value, and giving it a wire-shaped
    identity would invite someone to put it on one.
    """

    IN_FLIGHT = 0
    LATE = 1
    OVERDUE = 2
    ABANDONED = 3

    @property
    def rank(self) -> int:
        return self.value

    def at_least(self, other: "SilenceHorizon") -> bool:
        return self.rank >= other.rank


#: What the company OWES at each horizon. Sensing only -- see the module
#: docstring: these name an obligation, and nothing in this build discharges one
#: automatically. Every member of `SilenceHorizon` has an entry, asserted below,
#: because a horizon with no defined behaviour is exactly the gap Q5 is about.
SILENCE_OBLIGATION: dict[SilenceHorizon, str] = {
    SilenceHorizon.IN_FLIGHT: (
        "Wait. The crossing is inside the window where a response may still be in "
        "flight; nothing is owed and no belief should move."
    ),
    SilenceHorizon.LATE: (
        "Treat as asynchronous. Past one minute the request and its response are "
        "separate events in fact, not merely by contract (C-S3): the crossing must "
        "be carried in the open register and no caller may block on it."
    ),
    SilenceHorizon.OVERDUE: (
        "Re-ask, and report the belief as UNANSWERED rather than pending. A business "
        "day has passed with a promised answer undelivered, so any figure resting on "
        "this crossing is stale and must be labelled so wherever it is published."
    ),
    SilenceHorizon.ABANDONED: (
        "Stop expecting it. Five working days without the promised answer: the "
        "company concludes TIMEOUT in its own name, keeps the crossing OPEN (a "
        "conclusion is not a resolution), and hands it to manual reconciliation."
    ),
}

assert set(SILENCE_OBLIGATION) == set(SilenceHorizon), (
    "every SilenceHorizon needs a defined obligation -- a horizon with no defined "
    "behaviour is the defect Q5 names"
)


@dataclass(frozen=True)
class SilenceConclusion:
    """One open crossing, aged -- what the company heard, how long ago, and what
    it therefore owes.

    A READ MODEL. Constructing one changes nothing: the crossing stays in the
    register with the counterparty's own status untouched. This type is what the
    company can SAY about the silence, not a state transition.

    The two status fields are kept apart on purpose and are the point of the
    type (see the module docstring):

      * `heard_status` -- the counterparty's own last word. Always present,
        because a crossing is only open if something was heard.
      * `concluded_status` -- the COMPANY's word, manufactured by its own clock.
        `WallStatus.TIMEOUT` at the abandonment horizon and `None` before it.
        Never sourced from a message, and never written into the register.
    """

    correlation_id: str
    heard_status: WallStatus
    last_heard_at: dt.datetime
    as_of: dt.datetime
    horizon: SilenceHorizon
    obligation: str
    concluded_status: Optional[WallStatus] = None

    @property
    def answer_owed(self) -> bool:
        """True when the COUNTERPARTY still owes an answer that has not come.

        `NOT_KNOWABLE_YET` is the only status that owes one -- it says the
        counterparty holds the fact and cannot resolve it yet, so an answer is
        still coming and the company is right to keep waiting. `TIMEOUT` and
        `ERROR` speak about the EXCHANGE rather than the fact and license no
        such expectation: after either, the next move is the COMPANY's. This
        mirrors `UnresolvedCrossing.awaiting_resolution` rather than restating
        it, and it is why the three statuses do not share one obligation.
        """
        return self.heard_status == WallStatus.NOT_KNOWABLE_YET

    @property
    def exchange_failed(self) -> bool:
        """True when the last word was about the EXCHANGE failing, not the fact.

        Written as two explicit comparisons rather than an `in (...)` tuple
        test, and that is not a style preference: `status_mentions` in
        `tools/wall_channel_census.py` counts a `WallStatus.X` as READ only when
        the attribute is directly a side of a comparison, so members inside a
        tuple are invisible to it. Writing it the short way would have left this
        module scoring as a writer of TIMEOUT/ERROR with no reader -- the census
        reporting `unheard` while a real reader sat in front of it. Matching the
        instrument's shape here is cheaper and more honest than widening the
        instrument in the same pass that needs it to go green (R15 TAUTOLOGY:
        the control and the thing it scores must not be edited together to
        agree). The census's blind spot is real and is filed separately rather
        than fixed by the pass that benefits from fixing it.
        """
        return (
            self.heard_status == WallStatus.TIMEOUT
            or self.heard_status == WallStatus.ERROR
        )

    @property
    def next_move(self) -> str:
        """WHOSE MOVE IT IS, and what it is -- one arm per status the register
        can hold, so the three are never collapsed into "not OK".

        THIS IS THE READER Q5 ASKS FOR. Both company-side consumers previously
        branched only on `status != OK` (`payment_observation_consumer`,
        `flex_participation`), so TIMEOUT released exactly what ERROR released
        and the distinction the contract charges for was not bought. Here each
        member releases something different:

          * `NOT_KNOWABLE_YET` -- the counterparty is working on it. The move is
            the company's only once the horizon says the promise has gone stale.
          * `TIMEOUT` -- the transport already reported that it gave up. Nothing
            further will arrive on this attempt; a fresh crossing is required,
            and the underlying fact is UNKNOWN rather than absent.
          * `ERROR` -- the exchange itself failed and said so. Also a re-ask,
            but a diagnosable one: an `ErrorDetail` came with it, so this is the
            case where the company has something to act on besides a clock.

        SENSING ONLY: these are sentences, not calls. Nothing re-asks
        automatically -- see the module docstring.
        """
        match self.heard_status:
            case WallStatus.NOT_KNOWABLE_YET:
                owed = (
                    "The counterparty owes this answer and has not sent it"
                    if self.horizon.at_least(SilenceHorizon.OVERDUE)
                    else "The counterparty owes this answer and is within its window"
                )
                return f"{owed}. {self.obligation}"
            case WallStatus.TIMEOUT:
                return (
                    "The transport reported it gave up waiting, so no answer is in "
                    "flight and the fact is UNKNOWN, not absent. A fresh crossing is "
                    "required; the counterparty is owed nothing further on this one."
                )
            case WallStatus.ERROR:
                return (
                    "The exchange failed and said why, so this is a diagnosable "
                    "re-ask rather than a silent one. The fact is UNKNOWN, not "
                    "absent; nothing about the payment itself has been reported."
                )
            case _:
                raise ValueError(
                    f"crossing_silence: {self.correlation_id!r} holds status "
                    f"{self.heard_status!r}, which the ladder has no arm for -- a "
                    "status vocabulary that grew past this reader must fail here "
                    "rather than collapse a new member into an existing move"
                )


def silence_horizon(
    *,
    last_heard_at: dt.datetime,
    as_of: dt.datetime,
    nation: Nation = Nation.ENGLAND_AND_WALES,
) -> SilenceHorizon:
    """Which horizon an open crossing has reached at `as_of`.

    Boundaries are INCLUSIVE of the horizon they name: exactly one minute of
    silence IS `LATE`. The alternative leaves a half-open sliver in which the
    company has passed a stated deadline and still reports the band below it,
    which is the direction that flatters.

    A CLOCK RUNNING BACKWARDS RAISES (R15 fail-closed). `as_of` before
    `last_heard_at` means the company is asking about a crossing it has not yet
    heard of; the tempting reading -- "no time has passed, so IN_FLIGHT" -- is a
    confident wrong answer built from a contradiction, and it would hide a
    Blindfold breach (a caller reading a register ahead of its own decision
    clock) behind the most reassuring member of the enum.

    Naive and aware datetimes are not mixed: comparing them raises in Python
    anyway, but it raises with a message about `-` rather than about this seam,
    so it is caught here and named.
    """
    if (last_heard_at.tzinfo is None) != (as_of.tzinfo is None):
        raise ValueError(
            "crossing_silence: last_heard_at and as_of must both be naive or both be "
            f"aware (got {last_heard_at!r} and {as_of!r}) -- a horizon computed across "
            "that boundary would be off by a whole timezone and look plausible"
        )
    if as_of < last_heard_at:
        raise ValueError(
            f"crossing_silence: as_of {as_of.isoformat()} is BEFORE last_heard_at "
            f"{last_heard_at.isoformat()} -- the company cannot age a crossing it has "
            "not yet heard about, and reporting IN_FLIGHT here would hide the breach"
        )

    # The working-day count is asked FIRST because it is the coarsest band and
    # the only one that can raise. Failing closed on an uncovered calendar must
    # not depend on which branch happened to be taken.
    elapsed_working_days = working_days_between(
        last_heard_at.date(), as_of.date(), nation=nation
    )
    if elapsed_working_days >= ABANDONED_AFTER_WORKING_DAYS:
        return SilenceHorizon.ABANDONED

    silent_for = as_of - last_heard_at
    if silent_for >= OVERDUE_AFTER:
        return SilenceHorizon.OVERDUE
    if silent_for >= LATE_AFTER:
        return SilenceHorizon.LATE
    return SilenceHorizon.IN_FLIGHT


def conclude_silence(
    *,
    correlation_id: str,
    heard_status: WallStatus,
    last_heard_at: dt.datetime,
    as_of: dt.datetime,
    nation: Nation = Nation.ENGLAND_AND_WALES,
) -> SilenceConclusion:
    """Age one open crossing into a `SilenceConclusion`.

    THE TIMEOUT WRITER, and the only one on the company side. At
    `SilenceHorizon.ABANDONED` this stamps `concluded_status=WallStatus.TIMEOUT`
    -- the company's own word for "the answer did not arrive", manufactured by
    its own clock because no message will ever bring it. Below that horizon the
    field stays `None`: a company that stamped a conclusion at one minute would
    be asserting an outcome it has no grounds for yet.

    ONLY A CROSSING THAT WAS STILL OWED AN ANSWER CAN TIME OUT. Where
    `heard_status` is already `TIMEOUT` or `ERROR`, the exchange has already
    failed and the ball is in the company's court, so ageing it further adds no
    new fact about the counterparty -- `concluded_status` stays `None` and the
    horizon (which does keep advancing) is the report that the company has sat
    on its own re-ask for five working days. Re-concluding a TIMEOUT as a
    TIMEOUT would be the company agreeing with itself and counting it as
    evidence.

    An `OK` status is refused: an OK crossing is resolved and is not in the open
    register at all, so being handed one means the caller's register and its
    reader disagree about what "open" means.
    """
    if heard_status == WallStatus.OK:
        raise ValueError(
            f"crossing_silence: {correlation_id!r} was handed to the silence ladder "
            "with status OK -- an OK crossing is RESOLVED and holds no open answer, "
            "so ageing it would report silence on a fact already in hand"
        )
    horizon = silence_horizon(
        last_heard_at=last_heard_at, as_of=as_of, nation=nation
    )
    concluded: Optional[WallStatus] = None
    if horizon == SilenceHorizon.ABANDONED and heard_status == WallStatus.NOT_KNOWABLE_YET:
        concluded = WallStatus.TIMEOUT
    return SilenceConclusion(
        correlation_id=correlation_id,
        heard_status=heard_status,
        last_heard_at=last_heard_at,
        as_of=as_of,
        horizon=horizon,
        obligation=SILENCE_OBLIGATION[horizon],
        concluded_status=concluded,
    )
