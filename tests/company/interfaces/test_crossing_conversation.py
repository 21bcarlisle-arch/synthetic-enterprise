"""The company's multi-leg conversation register (atom EP6_wall_protocol_typing, Q3).

The blind review asked to be SHOWN a conversation with more than two legs, and
said that if the primitive cannot express one "the layer covers only the trivial
exchanges". These tests are the showing. The worked case is the Bacs collection
cycle -- request, input report, outcome -- and the mutations below are pointed at
the two ways a register like this stops being a check: by believing the wire
about what the company asked, and by counting the transport's behaviour as the
exchange's shape.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.interfaces.crossing_conversation import (
    REQUEST_LEG_NO,
    ConversationRegister,
    LegKind,
    UnaskedLeg,
)
from interface.contracts.wall_envelope import WallInterim, WallStatus

EMITTED = dt.datetime(2026, 3, 2, 9, 0)
ACKED = dt.datetime(2026, 3, 3, 6, 0)
ANSWERED = dt.datetime(2026, 3, 5, 6, 0)


def _interim(correlation_id="INV-1", leg=2, at=ACKED, interim_type="bacs_input_report"):
    return WallInterim(
        correlation_id=correlation_id,
        leg=leg,
        interim_type=interim_type,
        schema_version=2,
        observed_at=at,
        payload={"submission_ref": "SUB-1"},
    )


def _opened(register=None, correlation_id="INV-1"):
    register = register or ConversationRegister()
    register.open_conversation(correlation_id, "collection_request", EMITTED)
    return register


# ── THE WORKED CASE, which is what Q3 actually asked for ────────────────────────


def test_the_bacs_cycle_is_three_legs_and_the_register_says_so():
    """Request -> input report -> outcome. The number the reviewer wanted to see
    exceed two, produced by the register rather than asserted in prose."""
    reg = _opened()
    reg.record_interim(_interim())
    reg.record_terminal("INV-1", "RemittanceAdvice", WallStatus.OK, ANSWERED)

    conv = reg.conversation("INV-1")
    assert conv.leg_count == 3
    assert conv.is_multi_leg
    assert [leg.kind for leg in conv.legs] == [
        LegKind.REQUEST,
        LegKind.INTERIM,
        LegKind.TERMINAL,
    ]
    assert [leg.leg_no for leg in conv.legs] == [REQUEST_LEG_NO, 2, None]
    assert conv.is_closed and conv.closed_at == ANSWERED
    assert reg.multi_leg_conversations() == (conv,)


def test_a_two_leg_exchange_is_still_two_legs_and_is_not_counted_as_multi():
    """THE NULL CONTROL for the test above. Without it, `is_multi_leg` could be
    a property that is true of everything, and the count above would be proving
    that the register exists rather than that it measures.

    This is also the live shape for every non-DD rail: a customer-initiated push
    payment is a crossing nobody asked for, so it has an outcome and no
    request."""
    reg = ConversationRegister()
    reg.record_terminal("PUSH-1", "RemittanceAdvice", WallStatus.OK, ANSWERED)

    conv = reg.conversation("PUSH-1")
    assert conv.leg_count == 1
    assert not conv.is_multi_leg
    assert reg.multi_leg_conversations() == ()


# ── THE ONE REFUSAL, and its direction ─────────────────────────────────────────


def test_MUTATION_an_interim_for_a_conversation_nobody_opened_is_REFUSED():
    """THE R15 CLAUSE. The company's own request register is the only evidence
    that it asked; if an arriving message could open a conversation, any process
    able to mint a plausible correlation id would be in conversation with us.

    The mutation is the whole point of the test: the SAME interim that is
    refused here is accepted by the same register one line later, once the
    company has written down that it asked. So the refusal is keyed on the
    company's own record and not on anything about the message."""
    reg = ConversationRegister()
    with pytest.raises(UnaskedLeg) as exc:
        reg.record_interim(_interim())
    assert "never opened" in str(exc.value)
    assert reg.conversation("INV-1") is None

    reg.open_conversation("INV-1", "collection_request", EMITTED)
    assert reg.record_interim(_interim()) is True


def test_the_refusal_names_the_leg_and_the_id_so_it_is_diagnosable():
    """A bare raise cannot tell an operator which submission was acknowledged
    out of nowhere, which is the whole content of the incident."""
    reg = ConversationRegister()
    with pytest.raises(UnaskedLeg) as exc:
        reg.record_interim(_interim(correlation_id="INV-77", leg=4))
    assert "INV-77" in str(exc.value)
    assert "4" in str(exc.value)


def test_an_unopened_TERMINAL_is_recorded_rather_than_refused():
    """The deliberate asymmetry with the interim leg, asserted so a later reader
    does not 'fix' it into consistency. This build's world legitimately
    volunteers outcomes for collections no request was minted for -- every
    non-DD rail -- and refusing them would break a live crossing to enforce a
    discipline the emitter does not keep."""
    reg = ConversationRegister()
    assert reg.record_terminal("PUSH-1", "RemittanceAdvice", WallStatus.OK, ANSWERED)
    conv = reg.conversation("PUSH-1")
    assert conv is not None and conv.request_type == ""


# ── C-S2: at-least-once delivery must not become a longer conversation ─────────


def test_MUTATION_a_redelivered_leg_does_not_inflate_the_leg_count():
    """If a repeat counted as a leg, `leg_count` would be measuring the
    TRANSPORT rather than the exchange, and a chatty network would look like a
    richer conversation. The restatement is counted separately instead, so
    "we heard this twice" stays visible without being confused for "this
    happened twice"."""
    reg = _opened()
    assert reg.record_interim(_interim()) is True
    assert reg.record_interim(_interim(at=dt.datetime(2026, 3, 3, 8, 0))) is False

    conv = reg.conversation("INV-1")
    assert conv.leg_count == 2
    assert conv.restatements == 1
    interim_leg = [leg for leg in conv.legs if leg.kind is LegKind.INTERIM][0]
    assert interim_leg.observed_at == dt.datetime(2026, 3, 3, 8, 0), (
        "the register holds the counterparty's most recent transaction time, "
        "which is the envelope's own restatement rule"
    )


def test_reopening_a_conversation_does_not_discard_the_legs_already_heard():
    """`open_conversation` is idempotent because a resend is the same exchange.
    A version that reset the state would lose an acknowledgement every time a
    caller retried."""
    reg = _opened()
    reg.record_interim(_interim())
    reg.open_conversation("INV-1", "collection_request", EMITTED)
    assert reg.conversation("INV-1").leg_count == 2


# ── C-S1: late and out-of-order arrival is legal, and is recorded ──────────────


def test_an_outcome_that_overtakes_its_own_acknowledgement_is_ACCEPTED_and_FLAGGED():
    """A register that refused this would be modelling a reliability the wall's
    own contract says does not exist. It reads in DECLARED order regardless --
    that is a property of the exchange -- while `arrived_out_of_order` records
    what the transport did on the day."""
    reg = _opened()
    reg.record_terminal("INV-1", "BacsArruddOutcome", WallStatus.OK, ANSWERED)
    reg.record_interim(_interim())

    conv = reg.conversation("INV-1")
    assert conv.leg_count == 3
    assert [leg.kind for leg in conv.legs] == [
        LegKind.REQUEST,
        LegKind.INTERIM,
        LegKind.TERMINAL,
    ]
    assert conv.arrived_out_of_order


def test_a_REDELIVERY_is_not_read_as_a_REORDERING():
    """The bug this property had when it was first written: comparing the raw
    arrival log against the declared order reported an exchange whose leg 2
    simply arrived twice as out-of-order. Two different facts about two
    different layers."""
    reg = _opened()
    reg.record_interim(_interim())
    reg.record_interim(_interim())
    reg.record_terminal("INV-1", "RemittanceAdvice", WallStatus.OK, ANSWERED)
    assert reg.conversation("INV-1").arrived_out_of_order is False


# ── what the company is still owed ─────────────────────────────────────────────


def test_a_submitted_collection_is_OPEN_before_anything_comes_back():
    """THE STRUCTURAL CHANGE. Before the request register, a crossing existed
    only once something arrived about it, so a collection lost on the way to the
    bureau and one never submitted read identically. This is the reading that
    did not previously exist."""
    reg = _opened()
    conv = reg.conversation("INV-1")
    assert conv.leg_count == 1
    assert not conv.is_closed
    assert conv.awaiting == ("acknowledgement", "outcome")
    assert reg.open_conversations() == (conv,)


def test_the_acknowledgement_is_not_dropped_from_awaiting_by_a_later_message():
    """An exchange that SKIPPED its own leg 2 is a thing the company should be
    able to notice. Reconciling it away because the outcome turned up would hide
    exactly the case where the bureau never confirmed receipt."""
    reg = _opened()
    conv = reg.conversation("INV-1")
    assert "acknowledgement" in conv.awaiting
    reg.record_interim(_interim())
    assert reg.conversation("INV-1").awaiting == ("outcome",)


def test_a_closed_conversation_is_owed_nothing_and_leaves_the_open_set():
    reg = _opened()
    reg.record_interim(_interim())
    reg.record_terminal("INV-1", "RemittanceAdvice", WallStatus.OK, ANSWERED)
    assert reg.conversation("INV-1").awaiting == ()
    assert reg.open_conversations() == ()
    assert len(reg.conversations()) == 1


def test_a_non_OK_answer_does_not_close_the_exchange():
    """Consistency with the consumer this register lives in: `observe` records a
    non-OK as an `UnresolvedCrossing` and explicitly does not close the
    crossing, so only an OK reaches `record_terminal` at all. Asserted here at
    the register level so the two cannot drift: a conversation nothing terminal
    was recorded against stays open and stays countable."""
    reg = _opened()
    reg.record_interim(_interim())
    assert reg.open_conversations()[0].awaiting == ("outcome",)


# ── fail-closed on the register's own inputs ───────────────────────────────────


def test_an_empty_correlation_id_cannot_open_a_conversation():
    with pytest.raises(ValueError, match="correlation_id"):
        ConversationRegister().open_conversation("", "collection_request", EMITTED)


def test_an_unknown_conversation_reads_as_None_and_never_as_empty():
    """`None` means UNKNOWN. There is no such thing here as a conversation with
    no legs, because opening one files the request -- so a caller can tell "I
    have no record of this" from "I have a record and it is bare", which are
    different facts calling for different repairs."""
    assert ConversationRegister().conversation("NOPE") is None


def test_two_conversations_do_not_share_legs():
    """The register is keyed per exchange. A version that pooled legs would make
    every acknowledgement acknowledge everything."""
    reg = _opened()
    reg.open_conversation("INV-2", "collection_request", EMITTED)
    reg.record_interim(_interim(correlation_id="INV-1"))
    assert reg.conversation("INV-1").leg_count == 2
    assert reg.conversation("INV-2").leg_count == 1


def test_the_interim_primitive_refuses_to_be_leg_one():
    """The contract's own guarantee, asserted from the register's side because
    it is what the ordering rests on: leg 1 is the request, so an interim can
    never be the opening leg of its own conversation."""
    with pytest.raises(ValueError, match="leg must be >= 2"):
        _interim(leg=1)


# ── WHAT THE SILENCE LADDER READS OFF A CONVERSATION (pass 46) ──────────────────
#
# The join these support is in `PaymentObservationConsumer.silence_ladder`; what
# is tested here is the reading, which has to be right about one thing above all:
# the request leg is the COMPANY'S OWN WORD and must never be counted as the
# counterparty having said something. A version that counted it makes every
# exchange look answered the instant it was raised, and an unanswered collection
# then ages from a clock that resets on its own emission -- silence that can
# never be detected, which is the exact defect Q5 names.


def test_the_REQUEST_leg_is_not_something_heard():
    """THE load-bearing distinction. A conversation with only its request leg
    has heard NOTHING, and the null control is the same conversation one
    acknowledgement later."""
    reg = _opened()
    assert reg.conversation("INV-1").last_heard_at() is None
    assert reg.conversation("INV-1").leg_count == 1, (
        "the leg is present -- this is not an empty register, it is a register "
        "holding the company's own act"
    )

    reg.record_interim(_interim())
    assert reg.conversation("INV-1").last_heard_at() == ACKED


def test_silence_runs_from_the_companys_own_emission_until_something_arrives():
    """The fallback is the point of the fallback: an exchange nothing has come
    back on is precisely the one whose silence needs measuring, and the only
    event that exists to measure it from is the company asking."""
    reg = _opened()
    assert reg.conversation("INV-1").silent_since() == EMITTED

    reg.record_interim(_interim())
    assert reg.conversation("INV-1").silent_since() == ACKED, (
        "once the counterparty speaks, the clock restarts from ITS message"
    )


def test_only_an_INTERIM_acknowledges_receipt():
    """A terminal closes the exchange and the request is the company's own word,
    so an acknowledgement is the one leg that can say 'we hold this'."""
    reg = _opened()
    assert reg.conversation("INV-1").acknowledged() is False

    reg.record_interim(_interim())
    assert reg.conversation("INV-1").acknowledged() is True

    push = ConversationRegister()
    push.record_terminal("PUSH-9", "RemittanceAdvice", WallStatus.OK, ANSWERED)
    assert push.conversation("PUSH-9").acknowledged() is False, (
        "a terminal is an outcome, not a confirmation of receipt"
    )


def test_the_readings_are_BLINDFOLDED_by_as_of():
    """A leg that arrives after the decision clock has not been heard AT that
    clock, however firmly it sits in the register now. Without this the ladder
    would age an unanswered crossing from a message the company had not yet
    received -- and could produce a NEGATIVE silence."""
    reg = _opened()
    reg.record_interim(_interim())
    before = ACKED - dt.timedelta(hours=1)

    conv = reg.conversation("INV-1")
    assert conv.last_heard_at(as_of=before) is None
    assert conv.acknowledged(as_of=before) is False
    assert conv.silent_since(as_of=before) == EMITTED
    # the null control: at a clock that HAS reached the interim, all three move.
    assert conv.last_heard_at(as_of=ACKED) == ACKED
    assert conv.acknowledged(as_of=ACKED) is True
    assert conv.silent_since(as_of=ACKED) == ACKED


def test_is_open_at_reads_the_register_at_the_decision_clock_and_not_now():
    """Two ways to be absent and the ladder treats them alike: an exchange
    closed by then is resolved, and one opened after did not exist. The
    interesting case is the middle one -- a conversation closed TODAY was open
    last week, and a reader that only knew `is_closed` would say otherwise."""
    reg = _opened()
    reg.record_terminal("INV-1", "RemittanceAdvice", WallStatus.OK, ANSWERED)
    conv = reg.conversation("INV-1")

    assert conv.is_closed is True
    assert conv.is_open_at(EMITTED + dt.timedelta(hours=1)) is True, (
        "it was open then, and that is what an as-of read is for"
    )
    assert conv.is_open_at(ANSWERED) is False
    assert conv.is_open_at(EMITTED - dt.timedelta(days=1)) is False, (
        "a conversation not yet opened is not an open conversation"
    )


# ===========================================================================
# THE SECOND WORKED CASE (EP6 pass 60): A SWITCH WITH OBJECTION.
#
# Q3 names two examples. The Bacs cycle above is the first and it is a LINE --
# every leg is a later position on one path, which is exactly what `leg`
# numbers. The reviewer's other example is not a line: an objection is an
# ALTERNATIVE CONTINUATION, taken INSTEAD OF the clean one, and both sit at the
# same ordinal.
#
# The defect this closes was measured on this build before `branch` existed, and
# it was not a missing feature -- the register answered, silently, and wrongly.
# Deduplication keyed on (kind, ordinal), so the second continuation was filed
# as a RESTATEMENT of the first and the LATER ARRIVAL won:
#
#     ObjectionRaised then ObjectionWindowClosed
#       -> leg_count 3, restatements 1, surviving leg ObjectionWindowClosed
#
# A company reading that would have started supplying a customer whose switch
# had been objected, and which of the two contradictory outcomes it believed was
# decided by network arrival order. `test_MUTATION_the_BRANCH_IS_IN_THE_KEY_or_a
# _contradiction_is_filed_as_a_restatement` is that measurement, kept as a test.
#
# EVERY LEG BELOW CROSSES A WIRE. The branch is encoded, serialised and decoded
# through `wall_protocol` rather than handed between two objects in one process
# -- a register checked against interims it was passed directly would prove the
# company agrees with itself, which is the R15 TAUTOLOGY for the one question a
# seam is asked.
# ===========================================================================

import json  # noqa: E402

from company.interfaces.crossing_conversation import BranchError  # noqa: E402
from company.interfaces.wall_protocol import (  # noqa: E402
    decode_interim,
    encode_interim,
)

SWITCH = "SWITCH-4471"
SWITCH_BRANCHES = ("objected", "unobjected")
REQUESTED = dt.datetime(2026, 4, 1, 9, 0)


def _day(n: int) -> dt.datetime:
    return REQUESTED + dt.timedelta(days=n)


def _over_the_wire(leg, interim_type, at, branch=None, correlation_id=SWITCH):
    """One interim, put on the wire and read back off it. `json.dumps` is not
    decoration: a branch that survived only as a live Python object would be
    proving something about this process rather than about the crossing."""
    sent = WallInterim(
        correlation_id=correlation_id,
        leg=leg,
        interim_type=interim_type,
        schema_version=3,
        observed_at=at,
        payload={"process": "css"},
        branch=branch,
    )
    wire = json.loads(json.dumps(encode_interim(sent, encode_payload=lambda p: p)))
    return decode_interim(wire, decode_payload=lambda p: p)


def _switch_requested() -> ConversationRegister:
    reg = ConversationRegister()
    reg.open_conversation(SWITCH, "SwitchRequest", REQUESTED, branches=SWITCH_BRANCHES)
    return reg


def test_the_FULL_SWITCH_WITH_OBJECTION_crosses_the_wall_as_FIVE_legs():
    """Q3's own second example, shown rather than argued for. Request, the
    registration both paths share, the divergence, a leg further along the
    branch it diverged onto, and the outcome that path ends in."""
    reg = _switch_requested()
    reg.record_interim(_over_the_wire(2, "css.registration_confirmed", _day(1)))
    reg.record_interim(
        _over_the_wire(3, "css.objection_raised", _day(2), branch="objected")
    )
    reg.record_interim(
        _over_the_wire(4, "css.objection_upheld", _day(9), branch="objected")
    )
    reg.record_terminal(SWITCH, "css.switch_cancelled", WallStatus.OK, _day(10))

    conv = reg.conversation(SWITCH)
    assert conv.leg_count == 5
    assert conv.is_multi_leg is True
    assert conv.branch_taken == "objected"
    assert conv.restatements == 0, "not one of these five is a redelivery"
    assert [(leg.leg_no, leg.branch) for leg in conv.legs] == [
        (1, None),
        (2, None),
        (3, "objected"),
        (4, "objected"),
        (None, None),
    ]


def test_the_OTHER_CONTINUATION_of_the_SAME_declared_process_ends_differently():
    """The branch is a branch because BOTH paths are reachable from one
    declaration. Same `open_conversation` call, same trunk leg, and the exchange
    ends in the opposite market outcome -- which is the thing a register that
    could only express a line was unable to say at all."""
    reg = _switch_requested()
    reg.record_interim(_over_the_wire(2, "css.registration_confirmed", _day(1)))
    reg.record_interim(
        _over_the_wire(3, "css.objection_window_closed", _day(5), branch="unobjected")
    )
    reg.record_terminal(SWITCH, "css.switch_completed", WallStatus.OK, _day(6))

    conv = reg.conversation(SWITCH)
    assert conv.branch_taken == "unobjected"
    assert conv.leg_count == 4
    assert conv.legs[-1].message_type == "css.switch_completed"


def test_MUTATION_the_BRANCH_IS_IN_THE_KEY_or_a_contradiction_is_filed_as_a_restatement():
    """THE MEASURED DEFECT, kept as a test rather than as a sentence in a
    record. Both continuations sit at leg 3; before `branch` joined the
    deduplication key they were the same leg, so the second was a restatement of
    the first and the later arrival survived.

    The assertion is what the register does NOW: it refuses. The mutation that
    reds this is putting the identity back to (kind, ordinal) -- and the failure
    mode it restores is the dangerous one, because nothing raises, `leg_count`
    stays plausible, and the surviving outcome is whichever the transport
    happened to deliver second."""
    reg = _switch_requested()
    reg.record_interim(_over_the_wire(2, "css.registration_confirmed", _day(1)))
    reg.record_interim(
        _over_the_wire(3, "css.objection_raised", _day(2), branch="objected")
    )

    with pytest.raises(BranchError) as caught:
        reg.record_interim(
            _over_the_wire(
                3, "css.objection_window_closed", _day(2), branch="unobjected"
            )
        )
    assert caught.value.reason == "BRANCH_CONFLICT"

    conv = reg.conversation(SWITCH)
    assert conv.branch_taken == "objected", "the refused leg changed nothing"
    assert conv.restatements == 0
    assert [leg.message_type for leg in conv.legs] == [
        "SwitchRequest",
        "css.registration_confirmed",
        "css.objection_raised",
    ]


def test_NULL_CONTROL_a_SECOND_leg_on_the_SAME_branch_is_an_ordinary_leg():
    """Without this the refusal above would be indistinguishable from a register
    that admits exactly one branch leg per exchange -- which would cap every
    branching conversation at four legs and make the five-leg case impossible.
    Same branch, next ordinal, filed."""
    reg = _switch_requested()
    reg.record_interim(
        _over_the_wire(3, "css.objection_raised", _day(2), branch="objected")
    )
    assert (
        reg.record_interim(
            _over_the_wire(4, "css.objection_upheld", _day(9), branch="objected")
        )
        is True
    )
    assert reg.conversation(SWITCH).leg_count == 3


def test_NULL_CONTROL_a_REDELIVERY_of_a_branch_leg_is_still_a_restatement():
    """C-S2 is unchanged by any of this. The same leg arriving twice is the
    transport being at-least-once, not the exchange getting longer -- and a
    branch that turned every redelivery into a conflict would refuse an
    ordinary, correct network event."""
    reg = _switch_requested()
    leg = _over_the_wire(3, "css.objection_raised", _day(2), branch="objected")
    assert reg.record_interim(leg) is True
    assert reg.record_interim(leg) is False

    conv = reg.conversation(SWITCH)
    assert conv.restatements == 1
    assert conv.leg_count == 2


def test_a_LATE_TRUNK_LEG_is_admitted_AFTER_the_paths_have_already_diverged():
    """C-S1 is unchanged too, and this is the case a stricter rule would have
    broken. The registration confirmation belongs to BOTH outcomes, so it is
    legal before the objection and legal after it -- an out-of-order delivery,
    which this wall's own contract says is an ordinary event and not an error."""
    reg = _switch_requested()
    reg.record_interim(
        _over_the_wire(3, "css.objection_raised", _day(2), branch="objected")
    )
    assert (
        reg.record_interim(_over_the_wire(2, "css.registration_confirmed", _day(1)))
        is True
    )

    conv = reg.conversation(SWITCH)
    assert conv.branch_taken == "objected"
    assert conv.arrived_out_of_order is True, "a fact about the transport, not an error"
    assert [leg.leg_no for leg in conv.legs] == [1, 2, 3], "declared order regardless"


def test_MUTATION_a_branch_this_companys_PROCESS_DOES_NOT_HAVE_is_REFUSED():
    """The company names the continuations, the counterparty names the choice.
    A label outside the declared set is evidence the message belongs to a
    different exchange -- so it is refused as UNDECLARED rather than reconciled,
    and distinguishably from a conflict, because the two send a reader to
    different repairs."""
    reg = _switch_requested()
    with pytest.raises(BranchError) as caught:
        reg.record_interim(
            _over_the_wire(3, "css.transfer_disputed", _day(2), branch="disputed")
        )
    assert caught.value.reason == "UNDECLARED_BRANCH"
    assert reg.conversation(SWITCH).leg_count == 1


def test_a_LINEAR_exchange_refuses_EVERY_branch_because_it_declared_none():
    """The default is not the weak case. A collection has one path, so the
    declared set is empty and nothing is in it -- a counterparty that starts
    labelling legs on a process this company believes to be linear is caught
    rather than accommodated, and no special case is needed to catch it."""
    reg = ConversationRegister()
    reg.open_conversation("INV-77", "CollectionRequest", REQUESTED)
    with pytest.raises(BranchError) as caught:
        reg.record_interim(
            _over_the_wire(
                2, "bacs.input_report", _day(1), branch="objected",
                correlation_id="INV-77",
            )
        )
    assert caught.value.reason == "UNDECLARED_BRANCH"


def test_NULL_CONTROL_the_SAME_linear_exchange_takes_its_TRUNK_leg_normally():
    """Moves the sample, not the law: identical but for the label, and it files.
    The refusal above is measuring the branch, not a register that has stopped
    accepting interims on linear exchanges -- which is the whole existing build."""
    reg = ConversationRegister()
    reg.open_conversation("INV-77", "CollectionRequest", REQUESTED)
    assert (
        reg.record_interim(
            _over_the_wire(2, "bacs.input_report", _day(1), correlation_id="INV-77")
        )
        is True
    )
    conv = reg.conversation("INV-77")
    assert conv.is_branching is False
    assert conv.branch_taken is None


def test_an_exchange_that_has_NOT_YET_DIVERGED_says_so_rather_than_guessing():
    """`branch_taken` is `None` on a branching exchange that is still on the
    trunk, and that is a real answer: the paths have not parted, and the company
    is owed the divergence as much as the outcome. A property that PICKED a
    branch here -- the first declared one, say -- would be inventing a market
    event out of a declaration."""
    reg = _switch_requested()
    reg.record_interim(_over_the_wire(2, "css.registration_confirmed", _day(1)))
    conv = reg.conversation(SWITCH)
    assert conv.is_branching is True
    assert conv.branch_taken is None
    assert conv.awaiting == ("outcome",)


@pytest.mark.parametrize("bad", [("objected", ""), ("objected", "  "), ("",)])
def test_a_declared_branch_must_be_NAMED_or_the_trunk_becomes_a_branch(bad):
    """FAIL-OPEN SWEEP on the company's own half. An empty label is the trunk's
    spelling, so declaring one would make an unlabelled leg indistinguishable
    from a branch leg -- and two contradictory continuations both labelled `""`
    would file as one rather than conflicting."""
    reg = ConversationRegister()
    with pytest.raises(ValueError, match="must be named"):
        reg.open_conversation(SWITCH, "SwitchRequest", REQUESTED, branches=bad)


def test_a_REPEATED_declared_branch_is_REFUSED_because_it_is_not_two_paths():
    """A duplicate in the declaration is a typo with consequences: it reads as a
    process with more alternatives than it has, and the extra one can never be
    distinguished from its twin."""
    reg = ConversationRegister()
    with pytest.raises(ValueError, match="must be distinct"):
        reg.open_conversation(
            SWITCH, "SwitchRequest", REQUESTED, branches=("objected", "objected")
        )


def test_MUTATION_a_TRUNK_leg_at_the_SAME_ORDINAL_does_not_OVERWRITE_the_branch():
    """THE HOLE THE CONFLICT CHECK CANNOT COVER, and the reason `branch` is in
    the deduplication key as well as being refused across.

    A trunk leg is admissible on every path by design -- that is what a shared
    leg means, and refusing one after divergence would break C-S1. So the
    conflict check waves it through, and if the key were still (kind, ordinal)
    the register would file it as a RESTATEMENT of whatever branch leg shares
    its number and keep the later arrival. The objection would vanish and
    `branch_taken` would go back to `None`: not a refusal, not an error, just an
    exchange that quietly stopped having diverged.

    Ordinals are per-path in a branching protocol -- the third message of the
    objected path and the third of the clean one are both leg 3 -- so a
    collision with a shared leg is the ordinary case rather than an exotic one.
    The mutation that reds this is dropping `branch` from
    `ConversationLeg.identity`."""
    reg = _switch_requested()
    reg.record_interim(
        _over_the_wire(3, "css.objection_raised", _day(2), branch="objected")
    )
    assert (
        reg.record_interim(_over_the_wire(3, "css.window_notice", _day(4))) is True
    ), "a shared leg is not a redelivery of a branch leg that shares its number"

    conv = reg.conversation(SWITCH)
    assert conv.restatements == 0
    assert conv.branch_taken == "objected", "the objection is still on the record"
    assert [(leg.leg_no, leg.branch) for leg in conv.legs] == [
        (1, None),
        (3, None),
        (3, "objected"),
    ], "the trunk leg sorts before the divergence it precedes"
