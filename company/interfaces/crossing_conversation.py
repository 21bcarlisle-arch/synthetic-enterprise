"""The company's record of a MULTI-LEG crossing (atom EP6_wall_protocol_typing, Q3).

PURPOSE. The blind review's question 3 is four words -- "show me a conversation
with more than two legs" -- and its answer_needed names the fail: "if the
primitive can't express it, the layer covers only the trivial exchanges." At
pass 43 that was exactly true. `interface/contracts/wall_envelope.py` had three
shapes, and between them they could say ASK (`WallRequest`), ANSWER
(`WallResponse`) and TELL (`WallNotification`). Nothing could say NOT YET
FINISHED, and `correlation_id` bound exactly one answer to one question.

`WallInterim` (pass 44) is the missing shape. THIS module is the other half of
the answer, and it is the half a message type cannot supply: a conversation is
not a kind of message, it is a RELATION BETWEEN messages, and the relation has
to be held by somebody. The counterparty cannot hold it -- it does not know what
the company still considers open -- so the company holds it here.

--------------------------------------------------------------------------
THE WORKED CASE, because Q3 asks to be SHOWN one and a primitive is not a
demonstration.
--------------------------------------------------------------------------

The Bacs Direct Debit collection cycle, which `payment_observable_seam.py`'s own
header has described since it was written and which no code in this build could
express until now:

    leg 1  COMPANY -> WORLD   WallRequest[CollectionRequest]
                              "collect GBP X against mandate M on date D"
    leg 2  WORLD -> COMPANY   WallInterim[BacsInputReport]
                              "your submission validated and is in processing"
    leg 3  WORLD -> COMPANY   WallResponse[BacsArruddOutcome | RemittanceAdvice
                              | SettlementConfirmation]
                              "unpaid, reason R" / "paid, value date V"

    alongside, and NOT a leg of this conversation:
           WORLD -> COMPANY   WallNotification[AddacsAdvice]
                              "the payer cancelled the mandate" (pass 43)

That is the reviewer's own DCC request->ack->response->alert shape in this
build's own domain. The ADDACS advice is deliberately NOT folded in as a fourth
leg: it answers no request, arrives on its own sequence, and pulling it into a
correlation it has no part in is the mirror image of the Q2 fail ("we model it
as a response to a synthetic request"). A conversation gets longer by having
more legs, not by annexing the messages next to it.

--------------------------------------------------------------------------
THE SECOND WORKED CASE, AND IT IS THE HALF AN ORDINAL COULD NOT CARRY (pass
60): A SWITCH WITH OBJECTION.
--------------------------------------------------------------------------

Q3 names two examples and this build had only the first. The Bacs cycle above
is a LINE -- every leg is a later position on one path -- and a line is what
`leg` numbers. The reviewer's other example is not:

    leg 1  COMPANY -> WORLD   WallRequest[SwitchRequest]
    leg 2  WORLD -> COMPANY   WallInterim[RegistrationConfirmed]   (trunk)
                              -- and here the paths DIVERGE:
    leg 3  WORLD -> COMPANY   WallInterim[ObjectionRaised]         branch=objected
    leg 4  WORLD -> COMPANY   WallInterim[ObjectionUpheld]         branch=objected
    leg 5  WORLD -> COMPANY   WallResponse[SwitchCancelled]
                        -- OR --
    leg 3  WORLD -> COMPANY   WallInterim[ObjectionWindowClosed]   branch=unobjected
    leg 4  WORLD -> COMPANY   WallResponse[SwitchCompleted]

An objection is not a later position on one path; it is a DIFFERENT path, taken
INSTEAD OF the clean one. Before `branch` existed this register could not say
so, and the failure was not that it lacked expressiveness -- it was that it
answered wrongly and silently. Both continuations sit at leg 3, the
deduplication key was (kind, ordinal), so the second arrival was filed as a
RESTATEMENT of the first and the LATER one won. Measured on this build before
the field was added: an exchange told `ObjectionRaised` and then
`ObjectionWindowClosed` reported three legs, one restatement, and
`ObjectionWindowClosed` as the surviving leg. A company reading that register
would have started supplying a customer whose switch had been objected, and
which of the two contradictory outcomes it believed was decided by network
arrival order.

WHO SAYS WHAT, because the split is the whole design. The COUNTERPARTY names the
branch a leg is on (`WallInterim.branch`) -- which continuation happened is a
fact about the world, learned the way everything else on this wall is learned.
The COMPANY names the branches its process HAS (`open_conversation(branches=)`)
-- it chose which market process to enter, so the shape of the possible answer
is its own knowledge. A label outside that set is refused, which is `UnaskedLeg`'s
reasoning one level up: the wire may report a choice, never extend the menu.

ONLY NON-TERMINAL LEGS CARRY A BRANCH. Paths diverge before they end, so if the
first thing distinguishing two outcomes were the ending itself, that would not be
a branch at all -- it would be two possible answers, which `WallStatus` and the
response's own type already say. `branch_taken` is therefore read off the interim
legs, and a terminal simply closes whichever path the exchange was on.

--------------------------------------------------------------------------
THE ONE REFUSAL, AND IT IS THE R15 CLAUSE OF THE DESIGN.
--------------------------------------------------------------------------

An interim naming a `correlation_id` this company never opened is REFUSED
(`UnaskedLeg`). The company's own request register -- written when it SENT the
request -- is the only evidence that it asked; a message arriving on the wire can
never be that evidence, because then any process able to mint a plausible id
would be in conversation with us. That is the same reasoning, one layer up, as
`PaymentObservationConsumer`'s account roster ("a message naming an account
cannot be the evidence that the account is ours") and as
`wall_protocol.COUNTERPARTY_REGISTRY` holding a fingerprint the sender never
supplies. Absence is never agreement.

--------------------------------------------------------------------------
WHAT IS DELIBERATELY *NOT* REFUSED, which matters just as much.
--------------------------------------------------------------------------

LATE AND OUT-OF-ORDER ARRIVAL IS LEGAL (C-S1). An outcome that overtakes its own
input report is an ordinary event on a real network, and a register that refused
it would be modelling a reliability the wall's own contract says does not exist.
So arrival order is RECORDED (`arrived_out_of_order`) and never enforced: the
conversation reads in DECLARED order -- request, interims by their own `leg`,
terminal last -- which is a property of the exchange, while arrival order is a
property of the transport on the day.

A REPEATED LEG IS AN IDEMPOTENT NO-OP, NOT A LONGER CONVERSATION (C-S2). At-
least-once delivery means the same input report can land twice; counting it
twice would make `leg_count` a measure of the transport rather than of the
exchange. Repeats are deduplicated by leg identity and counted separately in
`restatements`, so "we heard this twice" stays visible without inflating what
happened.

NO EXPIRY, NO ASSUMED CLOSE. A conversation leaves the open set only when a
terminal response arrives -- never by timeout, never by the clock. That is
`UnresolvedCrossing`'s own rule and it is right for the same reason: concluding
a crossing the counterparty never answered is inventing a message. What the
company may do with an open conversation that has gone quiet is
`crossing_silence`'s question, and this module hands it a better subject than it
had -- a crossing is now OPEN FROM THE MOMENT IT WAS ASKED, so a collection
whose FIRST answer never arrives is visible for the first time. Until pass 44
nothing recorded that the company had asked, which is why Q5's own row records
initial silence as invisible.

THAT JOIN IS MADE (pass 46), in `PaymentObservationConsumer.silence_ladder`, and
it is why the three as-of readings below exist -- `last_heard_at`,
`acknowledged`, `silent_since`. It is deliberately NOT made here: this module
imports no ladder and the ladder imports no register, so each stays a thing that
can be reasoned about alone and the consumer that holds both books does the
joining. The one reading the ladder could not do without help is the ANSWER TO
"has the counterparty confirmed it holds this", because an unacknowledged
submission may equally never have arrived or be collecting money right now, and
those license different acts.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from interface.contracts.wall_envelope import WallInterim, WallStatus

# Leg 1 is the request, always and by construction -- `WallInterim.__post_init__`
# refuses any interim numbered below 2 on exactly this ground. Declared once here
# so the register and the contract cannot drift apart by each spelling a literal.
REQUEST_LEG_NO = 1


#: The trunk -- the path every continuation shares, and what `branch is None`
#: means everywhere below. Named rather than spelled `None` at each site so the
#: register and its readers cannot drift apart about what an unlabelled leg is.
TRUNK: Optional[str] = None


class BranchError(ValueError):
    """A leg that cannot belong to the exchange it names -- carrying a REASON.

    Two belts can fire on one leg (an undeclared label and a conflicting one),
    and this atom's own store records what happens when they cannot be told
    apart: pass 53's misrouted-acceptance mutation passed on the key-set belt one
    layer earlier and never reached the refusal it named, and a bare `raises`
    called that a pass. So the reason is asserted, not the type -- the same idiom
    as `wall_protocol.WallProtocolError`, which is where this seam already keeps
    its refusal codes.

    UNDECLARED_BRANCH -- a continuation this company's process does not have.
    BRANCH_CONFLICT   -- a second, different continuation on an exchange that
                         has already taken one.
    """

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(f"{reason}: {message}")
        self.reason = reason


class LegKind(str, Enum):
    """What a leg IS, which is a different question from where it sits.

    Three kinds and not four: the notification primitive is absent on purpose,
    because an unsolicited message belongs to no conversation (see the module
    docstring). A fourth member here would be the only invitation anyone needs
    to start filing ADDACS advices under a collection they have nothing to do
    with."""

    REQUEST = "request"
    INTERIM = "interim"
    TERMINAL = "terminal"


@dataclass(frozen=True)
class ConversationLeg:
    """One leg, as the company recorded it.

    `leg_no` is the position in DECLARED order and is `None` for the terminal
    leg, which is not an oversight: `WallResponse` carries no leg ordinal, and
    manufacturing one at arrival would number it by the order the transport
    happened to deliver in -- so an outcome that overtook its input report would
    be recorded as leg 2 and the input report as leg 2 as well. The terminal leg
    does not need a number; it is last by definition, which is the whole content
    of being terminal."""

    kind: LegKind
    leg_no: Optional[int]
    message_type: str
    observed_at: dt.datetime
    status: Optional[WallStatus] = None   # terminal legs only -- the counterparty's own word
    branch: Optional[str] = TRUNK         # which continuation; None = shared by all paths

    @property
    def identity(self) -> Tuple[str, Optional[int], Optional[str]]:
        """What makes two arrivals THE SAME leg rather than two legs -- the
        deduplication key for at-least-once delivery (C-S2). Kind plus ordinal
        plus BRANCH, never `observed_at`: a redelivery carries a new transaction
        time and is still the same leg, and keying on the time would make every
        retry a new one.

        THE BRANCH IS IN THE KEY BECAUSE THE ORDINAL IS NOT ENOUGH, and this was
        measured rather than reasoned. `leg` orders messages along ONE path, so
        two alternative continuations both arrive at leg 3 -- and without the
        branch they were the same key. The register then filed the second as a
        RESTATEMENT of the first and kept the later arrival, so an exchange told
        `ObjectionRaised` and then `ObjectionWindowClosed` reported one
        restatement and `ObjectionWindowClosed` as the survivor. Two
        contradictory market outcomes, and network arrival order picked which
        one the company believed."""
        return (self.kind.value, self.leg_no, self.branch)


@dataclass(frozen=True)
class CrossingConversation:
    """The whole exchange behind one `correlation_id`.

    `legs` is in DECLARED order (request, interims ascending, terminal last),
    which is a fact about the exchange. `arrival_order` is the order the company
    actually heard them in, which is a fact about the transport. Keeping both is
    the point: a conversation whose legs arrived backwards is correct AND worth
    knowing about, and a type that stored only one of the two could not say so."""

    correlation_id: str
    request_type: str
    legs: Tuple[ConversationLeg, ...]
    arrival_order: Tuple[Tuple[str, Optional[int], Optional[str]], ...]
    opened_at: dt.datetime
    closed_at: Optional[dt.datetime]
    restatements: int
    branches: Tuple[str, ...] = ()

    @property
    def branch_taken(self) -> Optional[str]:
        """Which alternative continuation this exchange went down, or `None` for
        one still on the trunk -- including one that never diverges at all.

        AT MOST ONE, enforced upstream rather than resolved here: a leg on a
        second branch is refused at filing (`BRANCH_CONFLICT`), so this property
        never has to choose between two and never quietly reports the first or
        the loudest. A reading that PICKED would be the defect this whole field
        exists to remove, one layer further in.

        `None` on a branching exchange is a real and useful answer -- the paths
        have not diverged yet, and the company is owed the divergence as much as
        the outcome."""
        for leg in self.legs:
            if leg.branch is not TRUNK:
                return leg.branch
        return TRUNK

    @property
    def is_branching(self) -> bool:
        """Does this exchange's own process HAVE alternative continuations? A
        fact about the market process the company entered, declared when it
        asked -- not about what has arrived since."""
        return bool(self.branches)

    @property
    def leg_count(self) -> int:
        """How many legs this exchange has had. The answer to Q3 for one
        conversation, and the number a reader should be able to see exceed 2."""
        return len(self.legs)

    @property
    def is_closed(self) -> bool:
        return self.closed_at is not None

    @property
    def is_multi_leg(self) -> bool:
        """More than the trivial ask/answer pair -- the reviewer's own bar."""
        return self.leg_count > 2

    @property
    def arrived_out_of_order(self) -> bool:
        """True when the transport delivered these legs in an order other than
        the one they are declared in. Never an error (C-S1); a fact.

        FIRST ARRIVAL WINS, and a redelivery is not a reordering. `arrival_order`
        is the raw arrival log and holds a repeat for every at-least-once
        redelivery (C-S2); comparing it un-deduplicated would report an
        exchange whose leg 2 simply arrived twice as out-of-order, which is a
        different fact about a different layer. Deduplicating on FIRST
        occurrence asks the question this property is named for: when did the
        company first LEARN of each leg?"""
        declared = tuple(leg.identity for leg in self.legs)
        known = set(declared)
        heard: List[Tuple[str, Optional[int], Optional[str]]] = []
        for identity in self.arrival_order:
            if identity in known and identity not in heard:
                heard.append(identity)
        return tuple(heard) != declared

    def is_open_at(self, as_of: dt.datetime) -> bool:
        """Was this exchange open at `as_of` -- the Blindfolded reading of
        `is_closed`, and the one an ageing clock must use.

        Two ways to be absent from this reading and they are deliberately not
        distinguished, because the ladder does the same thing with both: an
        exchange CLOSED at or before `as_of` is resolved, and one OPENED after
        `as_of` did not exist yet. Neither is an open crossing at that clock,
        and reporting either would be the company reading its own register
        ahead of its decision time."""
        if self.opened_at > as_of:
            return False
        return self.closed_at is None or self.closed_at > as_of

    def last_heard_at(self, as_of: Optional[dt.datetime] = None) -> Optional[dt.datetime]:
        """When the counterparty last said ANYTHING on this exchange, or `None`
        if it never has.

        THE REQUEST LEG IS NOT SOMETHING HEARD, which is the whole content of
        this property and the reason it can return `None` at all. Leg 1 is the
        company writing down its own act (see the class docstring on why that
        is the only admissible evidence it happened); counting it here would
        make every exchange look answered the instant it was raised, and an
        unanswered collection would age from a clock that resets on its own
        emission.

        `as_of` applies the Blindfold: a leg that arrives after the decision
        clock has not been heard AT that clock, however firmly it sits in the
        register now."""
        heard = [
            leg.observed_at
            for leg in self.legs
            if leg.kind is not LegKind.REQUEST
            and (as_of is None or leg.observed_at <= as_of)
        ]
        return max(heard) if heard else None

    def acknowledged(self, as_of: Optional[dt.datetime] = None) -> bool:
        """Has the counterparty CONFIRMED it holds this request?

        The distinction is worth a method because it is the difference between
        two situations a company must never conflate. An acknowledged
        collection is demonstrably in the counterparty's cycle: the outcome is
        owed and the submission is not lost. An unacknowledged one may never
        have arrived -- or may have arrived and be collecting money right now,
        and the company has no way to tell which. What may safely be DONE about
        the silence turns on exactly this (`crossing_silence.SilenceOrigin`).

        An interim is the only leg that can say it: a terminal closes the
        exchange, and the request is the company's own word."""
        return any(
            leg.kind is LegKind.INTERIM
            and (as_of is None or leg.observed_at <= as_of)
            for leg in self.legs
        )

    def silent_since(self, as_of: Optional[dt.datetime] = None) -> dt.datetime:
        """When this exchange last produced anything at all -- the moment a
        silence clock should start from.

        The last thing HEARD where something has been, and the company's own
        emission where nothing has. Falling back to `opened_at` rather than
        refusing is the point of the fallback: an exchange nothing has come
        back on is precisely the one whose silence needs measuring, and it is
        measured from the only event that exists -- the company asking."""
        return self.last_heard_at(as_of=as_of) or self.opened_at

    @property
    def awaiting(self) -> Tuple[str, ...]:
        """What the company is still owed on this exchange, in the order it
        expects it. Empty once terminal -- and note that an acknowledgement is
        NOT dropped from this list merely because the outcome arrived: an
        exchange that skipped its own leg 2 is a thing the company should be able
        to notice, not something quietly reconciled away by a later message."""
        if self.is_closed:
            return ()
        owed: List[str] = []
        if not any(leg.kind is LegKind.INTERIM for leg in self.legs):
            owed.append("acknowledgement")
        owed.append("outcome")
        return tuple(owed)


class UnaskedLeg(ValueError):
    """An interim arrived for a conversation this company never opened.

    Raised rather than ignored, and the direction is deliberate: silently
    dropping it would mean a company that lost its own request register would
    read as a company with nothing outstanding, which is the FAIL-OPEN shape in
    the exact named sense. A real receivables function that gets an
    acknowledgement for a submission it has no record of making has a genuine
    incident, not a message to bin."""


@dataclass
class ConversationRegister:
    """The company's own book of open exchanges.

    HELD BY THE COMPANY, WRITTEN AT EMISSION. `open_conversation` is called when
    the company SENDS a request -- not when an answer comes back -- which is the
    structural change pass 44 makes and the reason three earlier questions
    (Q5's invisible initial silence, Q6's undetectable backlog burst, Q2's
    dormant request leg) each named this register as their upstream. A
    response-driven company cannot hold a clock against anything, because it
    learns a crossing existed only from the message that ends it."""

    _open: Dict[str, dict] = field(default_factory=dict)
    _closed: Dict[str, dict] = field(default_factory=dict)

    def open_conversation(
        self,
        correlation_id: str,
        request_type: str,
        emitted_at: dt.datetime,
        branches: Tuple[str, ...] = (),
    ) -> None:
        """Record that the company ASKED. Idempotent on `correlation_id`: a
        resend of the same request is the same exchange (C-S2), and re-opening
        would discard whatever legs had already arrived on it.

        `branches` names the ALTERNATIVE CONTINUATIONS this exchange may take --
        for a switch, ("objected", "unobjected"); for a Bacs collection, nothing,
        because a collection has one path and two ways of ending it. It comes
        from the COMPANY, at the moment it asks, because the company chose which
        market process to enter and therefore knows what shape the answer can
        take. Default `()` is a linear exchange, which is every caller this build
        has today and is not a weaker statement than naming branches: an exchange
        with no alternatives refuses ALL of them, so a counterparty that starts
        labelling legs on a process the company believes to be linear is caught
        rather than accommodated.

        THE SET IS THE COMPANY'S AND THE CHOICE IS THE COUNTERPARTY'S, which is
        the same split `UnaskedLeg` makes one level down. The wire may say which
        continuation happened; it may never say which continuations EXIST, or a
        process able to mint a plausible label would be able to extend our own
        market processes by asserting them."""
        if not correlation_id:
            raise ValueError(
                "a conversation must be opened under a correlation_id -- an "
                "exchange nothing can be matched to is not an exchange"
            )
        if any(not b or not b.strip() for b in branches):
            raise ValueError(
                f"every declared branch must be named, got {branches!r} -- an "
                "empty label is the trunk's spelling, so declaring one would "
                "make an unlabelled leg indistinguishable from a branch leg"
            )
        if len(set(branches)) != len(branches):
            raise ValueError(
                f"declared branches must be distinct, got {branches!r} -- a "
                "repeated continuation is not two ways for an exchange to go"
            )
        if correlation_id in self._open or correlation_id in self._closed:
            return
        request_leg = ConversationLeg(
            kind=LegKind.REQUEST,
            leg_no=REQUEST_LEG_NO,
            message_type=request_type,
            observed_at=emitted_at,
        )
        self._open[correlation_id] = {
            "request_type": request_type,
            "opened_at": emitted_at,
            "branches": tuple(branches),
            "legs": {request_leg.identity: request_leg},
            "arrival": [request_leg.identity],
            "restatements": 0,
            "closed_at": None,
        }

    def record_interim(self, interim: WallInterim) -> bool:
        """File leg `interim.leg` of an exchange this company opened.

        Returns True when the leg was new, False when it was a redelivery of one
        already held -- the C-S2 answer, so a caller can count duplicates without
        the register pretending they were legs.

        RAISES `UnaskedLeg` for an unopened correlation id. See the class
        docstring: the request register is the evidence, the wire never is."""
        state = self._open.get(interim.correlation_id) or self._closed.get(
            interim.correlation_id
        )
        if state is None:
            raise UnaskedLeg(
                f"interim leg {interim.leg} ({interim.interim_type}) arrived for "
                f"correlation_id {interim.correlation_id!r}, which this company "
                "never opened -- an acknowledgement for a request we have no "
                "record of sending is an incident, not a message to file"
            )
        self._require_admissible_branch(state, interim.correlation_id, interim.branch)
        leg = ConversationLeg(
            kind=LegKind.INTERIM,
            leg_no=interim.leg,
            message_type=interim.interim_type,
            observed_at=interim.observed_at,
            branch=interim.branch,
        )
        return self._file(state, leg)

    @staticmethod
    def _require_admissible_branch(
        state: dict, correlation_id: str, branch: Optional[str]
    ) -> None:
        """The two branch refusals, in the order that reports the honest fault.

        A TRUNK LEG IS ALWAYS ADMISSIBLE and is checked for first, deliberately:
        a leg every path shares is legal on a linear exchange and on a branching
        one, before divergence and after it. The CSS registration confirmation
        that arrives LATE -- after the objection has already been raised -- is an
        ordinary C-S1 event and refusing it would model a reliability this wall's
        own contract says does not exist.

        UNDECLARED BEFORE CONFLICT, because a label this company's process does
        not have says nothing about which continuation the exchange took: it is
        evidence the message belongs to a different exchange, and reporting it as
        a conflict would send a reader to reconcile two market outcomes when the
        repair is that one of them is not ours. This is the same ordering choice
        `wall_protocol._require_vocabulary` records for version-before-fields.

        CONFLICT IS REFUSED, NOT RESOLVED, and this is the R15 clause. The two
        available fail-open shapes are keep-the-first and keep-the-last; this
        register did the second by accident for sixteen passes, so an exchange
        that was objected read as clean if the clean message happened to land
        second. Neither is admissible, because the company ACTS differently on
        the two -- one switch completes and the other does not -- and a
        contradiction the counterparty has to be asked about is not a value to be
        picked from a pair by arrival order."""
        if branch is TRUNK:
            return
        declared = state.get("branches", ())
        if branch not in declared:
            raise BranchError(
                "UNDECLARED_BRANCH",
                f"leg on branch {branch!r} arrived for correlation_id "
                f"{correlation_id!r}, whose process declares "
                f"{list(declared) or 'no alternative continuations'} -- the "
                "company names the continuations its own process has, and a "
                "message cannot extend that set by asserting one",
            )
        taken = next(
            (leg.branch for leg in state["legs"].values() if leg.branch is not TRUNK),
            TRUNK,
        )
        if taken is not TRUNK and taken != branch:
            raise BranchError(
                "BRANCH_CONFLICT",
                f"correlation_id {correlation_id!r} is already on branch "
                f"{taken!r} and this leg claims {branch!r} -- these are "
                "ALTERNATIVE continuations, so both cannot have happened; "
                "filing it would make arrival order decide which outcome this "
                "company believes",
            )

    def record_terminal(
        self,
        correlation_id: str,
        message_type: str,
        status: WallStatus,
        observed_at: dt.datetime,
    ) -> bool:
        """Close the exchange on the answer.

        Unlike `record_interim` this does NOT raise on an unknown correlation id,
        and the asymmetry is the honest one rather than an inconsistency: this
        build's world legitimately volunteers outcomes for collections no
        `CollectionRequest` was minted for (every non-DD rail, and the DD path on
        any caller that has not adopted the request leg). Refusing those would
        break a live crossing to enforce a discipline the emitter does not yet
        keep, so an unopened terminal is recorded as a one-leg exchange and shows
        up as exactly that -- countable, not invisible."""
        state = self._open.get(correlation_id) or self._closed.get(correlation_id)
        if state is None:
            state = {
                "request_type": "",
                "opened_at": observed_at,
                "branches": (),
                "legs": {},
                "arrival": [],
                "restatements": 0,
                "closed_at": None,
            }
            self._open[correlation_id] = state
        leg = ConversationLeg(
            kind=LegKind.TERMINAL,
            leg_no=None,
            message_type=message_type,
            observed_at=observed_at,
            status=status,
        )
        is_new = self._file(state, leg)
        state["closed_at"] = observed_at
        self._closed[correlation_id] = self._open.pop(correlation_id, state)
        return is_new

    @staticmethod
    def _file(state: dict, leg: ConversationLeg) -> bool:
        """Deduplicate by leg identity, keeping the LATEST arrival's transaction
        time -- the envelope's own restatement rule (a restatement is a new
        message with a later `observed_at`, never an edit to a stored one)."""
        state["arrival"].append(leg.identity)
        if leg.identity in state["legs"]:
            state["restatements"] += 1
            state["legs"][leg.identity] = leg
            return False
        state["legs"][leg.identity] = leg
        return True

    def conversation(self, correlation_id: str) -> Optional[CrossingConversation]:
        """The exchange behind one id, or `None` if this company has no record of
        one. `None` means UNKNOWN and never EMPTY -- there is no such thing here
        as a conversation with no legs, because opening one files the request."""
        state = self._open.get(correlation_id) or self._closed.get(correlation_id)
        if state is None:
            return None
        return self._render(correlation_id, state)

    def conversations(self) -> Tuple[CrossingConversation, ...]:
        """Every exchange, open and closed, oldest first."""
        rendered = [
            self._render(cid, state)
            for cid, state in list(self._open.items()) + list(self._closed.items())
        ]
        rendered.sort(key=lambda c: (c.opened_at, c.correlation_id))
        return tuple(rendered)

    def open_conversations(self) -> Tuple[CrossingConversation, ...]:
        """Exchanges the company asked about and has had no terminal answer to --
        INCLUDING those where not one byte has come back, which is the reading
        that did not exist before this register."""
        return tuple(c for c in self.conversations() if not c.is_closed)

    def multi_leg_conversations(self) -> Tuple[CrossingConversation, ...]:
        """Exchanges that got past the trivial pair. Q3's own subject, countable
        on the live run rather than argued for in a document."""
        return tuple(c for c in self.conversations() if c.is_multi_leg)

    @staticmethod
    def _render(correlation_id: str, state: dict) -> CrossingConversation:
        def order(item: Tuple[tuple, ConversationLeg]) -> tuple:
            # The trunk sorts BEFORE a branch at the same ordinal, which is the
            # order the exchange actually took them in: a shared leg precedes the
            # divergence it precedes. The tiebreak exists at all because a
            # counterparty may number a branch leg the same as a trunk one, and
            # two legs with equal keys would otherwise render in dict order.
            leg = item[1]
            branch = (1, leg.branch) if leg.branch is not TRUNK else (0, "")
            if leg.kind is LegKind.REQUEST:
                return (0, REQUEST_LEG_NO, branch)
            if leg.kind is LegKind.INTERIM:
                return (1, leg.leg_no if leg.leg_no is not None else 0, branch)
            return (2, 0, branch)

        legs = tuple(leg for _, leg in sorted(state["legs"].items(), key=order))
        return CrossingConversation(
            correlation_id=correlation_id,
            request_type=state["request_type"],
            legs=legs,
            arrival_order=tuple(state["arrival"]),
            opened_at=state["opened_at"],
            closed_at=state["closed_at"],
            restatements=state["restatements"],
            branches=state["branches"],
        )
