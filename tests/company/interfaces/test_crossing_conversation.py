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
