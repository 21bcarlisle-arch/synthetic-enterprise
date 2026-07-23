"""F1 conversation seam tests (the interface-steward step): construction /
roundtrip of both types, the C-S3 strictly-after rule (with its mutation-style
negative case), the required ``product`` field, enum out-of-set rejection, the
no-sim/company import purity check, and the epistemic-wall field guarantee (no
susceptibility / trust / intent / true-scalar leaks across the seam).

Scope: the DATA CONTRACT only. No response model (F1a), generator/estimator
(F1b), or harness (F1c) behaviour is exercised here -- those are later atoms.
"""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
from pathlib import Path

import pytest

from interface.contracts.conversation_seam import (
    CONTRACT_PAYLOAD_TYPES,
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    SCHEMA_VERSION,
    Channel,
    ConversationMessage,
    ConversationMessageWallRequest,
    ConversationResponse,
    ConversationResponseWallResponse,
    Product,
    ResponseAction,
    Situation,
    validate_response_follows_message,
)
from interface.contracts.wall_envelope import WallStatus


def _message(step: int = 10) -> ConversationMessage:
    return ConversationMessage(
        message_id="m1",
        situation=Situation.MISSED_PAYMENT,
        channel=Channel.EMAIL,
        product=Product.ELECTRICITY,
        tone="firm",
        framing="loss",
        emitted_step=step,
        offer=None,
    )


def _response(responds_to: str = "m1", latency: int = 3, responded_step: int = 13) -> ConversationResponse:
    return ConversationResponse(
        response_id="r1",
        responds_to=responds_to,
        action=ResponseAction.PAY,
        channel_chosen=Channel.APP,
        latency=latency,
        responded_step=responded_step,
    )


def test_message_request_roundtrip():
    req = ConversationMessageWallRequest(
        correlation_id="m1", request_type="conversation_message",
        schema_version=SCHEMA_VERSION, as_of=dt.datetime(2024, 1, 10),
        emitted_at=dt.datetime(2024, 1, 10), payload=_message(),
    )
    assert req.payload.situation is Situation.MISSED_PAYMENT
    assert req.payload.channel is Channel.EMAIL
    assert req.payload.product is Product.ELECTRICITY


def test_response_response_roundtrip():
    resp = ConversationResponseWallResponse(
        correlation_id="m1", status=WallStatus.OK, schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2024, 1, 13), valid_time=dt.date(2024, 1, 13),
        payload=_response(),
    )
    assert resp.payload.action is ResponseAction.PAY
    assert resp.payload.channel_chosen is Channel.APP
    assert resp.payload.responds_to == "m1"


def test_product_field_is_required():
    """product carries wherever fuel is one (portability §8) -- it has no
    default, so a message cannot be constructed without it."""
    with pytest.raises(TypeError):
        ConversationMessage(  # type: ignore[call-arg]
            message_id="m1",
            situation=Situation.RENEWAL,
            channel=Channel.EMAIL,
            tone="warm",
            framing="gain",
            emitted_step=1,
        )


def test_enums_reject_out_of_set_value():
    with pytest.raises(ValueError):
        Situation("not_a_situation")
    with pytest.raises(ValueError):
        Channel("carrier_pigeon")
    with pytest.raises(ValueError):
        ResponseAction("ghosted")
    with pytest.raises(ValueError):
        Product("broadband")


def test_response_valid_after_message_c_s3():
    """The happy path: a response strictly after its message passes."""
    msg = _message(step=10)
    resp = _response(responds_to="m1", latency=3, responded_step=13)
    validate_response_follows_message(msg, resp)  # no raise


def test_response_same_step_is_rejected_c_s3():
    """C-S3 mutation: a response landing in the SAME step as its message is
    rejected -- the contract makes same-step resolution impossible."""
    msg = _message(step=10)
    resp = _response(responds_to="m1", latency=1, responded_step=10)
    with pytest.raises(ValueError):
        validate_response_follows_message(msg, resp)


def test_response_before_message_is_rejected_c_s3():
    """C-S3 mutation: a response whose clock precedes its message (a
    time-travelling reply) is rejected."""
    msg = _message(step=10)
    resp = _response(responds_to="m1", latency=1, responded_step=9)
    with pytest.raises(ValueError):
        validate_response_follows_message(msg, resp)


def test_response_wrong_message_is_rejected():
    """A response paired to the wrong message id is rejected."""
    msg = _message(step=10)
    resp = _response(responds_to="OTHER", latency=3, responded_step=13)
    with pytest.raises(ValueError):
        validate_response_follows_message(msg, resp)


def test_nonpositive_latency_rejected_at_construction_c_s3():
    """C-S3 made structural: a ConversationResponse cannot even be
    CONSTRUCTED with a zero or negative latency -- same-step / backwards
    resolution is not representable."""
    with pytest.raises(ValueError):
        ConversationResponse(
            response_id="r1", responds_to="m1", action=ResponseAction.REPLY,
            channel_chosen=Channel.EMAIL, latency=0, responded_step=10,
        )
    with pytest.raises(ValueError):
        ConversationResponse(
            response_id="r1", responds_to="m1", action=ResponseAction.REPLY,
            channel_chosen=Channel.EMAIL, latency=-2, responded_step=8,
        )


def test_wall_guarantee_no_hidden_trait_fields():
    """No payload -- message OR response -- may carry a field that names a
    hidden latent trait (susceptibility / trust / intent / true scalar). The
    company sees only the OBSERVABLE action; it must INFER the trait."""
    for payload_type in CONTRACT_PAYLOAD_TYPES:
        field_names = {f.name for f in dataclasses.fields(payload_type)}
        leaked = field_names & set(FORBIDDEN_TRUTH_FIELDS)
        assert not leaked, f"{payload_type.__name__} leaks hidden-trait fields: {leaked}"


def test_response_carries_no_susceptibility_scalar_structurally():
    """Explicit: the response payload has EXACTLY the observable fields and no
    susceptibility scalar -- asserted structurally, not by convention."""
    field_names = {f.name for f in dataclasses.fields(ConversationResponse)}
    assert field_names == {
        "response_id", "responds_to", "action", "channel_chosen",
        "latency", "responded_step",
    }
    for banned in ("framing_susceptibility", "tone_susceptibility", "susceptibility"):
        assert banned not in field_names
    assert OBSERVABLE_RESPONSE_PAYLOAD_TYPES == (ConversationResponse,)


def test_no_sim_or_company_import():
    """The contract module is PURE -- it imports nothing from sim/simulation/
    company/saas (only the wall envelope + stdlib)."""
    src = Path("interface/contracts/conversation_seam.py").read_text()
    tree = ast.parse(src)
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.append(node.module)
        elif isinstance(node, ast.Import):
            mods.extend(a.name for a in node.names)
    for m in mods:
        assert not m.startswith(("sim", "simulation", "company", "saas")), \
            f"contract must not import {m}"
