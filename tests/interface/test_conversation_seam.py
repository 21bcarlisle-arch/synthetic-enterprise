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


# ── THE MEASURED HALF OF THE BELT (EP6 pass 29) ──────────────────────────────
# `FORBIDDEN_TRUTH_FIELDS` is not the control -- `OBSERVABLE_PAYLOAD_FIELDS` is, and the
# tests that prove the belt FIRES live with the two codecs. These tests are about whether
# the LIST is real: a denylist of invented names is indistinguishable from a good one
# until the day it is needed.
#
# WHY THIS SEAM COULD NOT COPY ITS SIBLING. The payment belt is checked against the
# `dataclasses.fields` of the producers it cites. Nothing behind THIS seam stores a hidden
# trait on a record -- every one is computed on demand from a named SEED string. So the
# seed literal is the citable thing, and these tests read the producers' source rather
# than importing their state.
#
# WRITTEN OUT HERE, IN THE TEST, and never imported from the producers: a list checked
# against the thing it was generated from could never disagree with it (R15 TAUTOLOGY),
# and disagreement is the entire signal.

#: The two helpers that draw a hidden per-customer scalar. A trait that is not drawn
#: through one of these is not a per-customer latent trait behind this seam.
_HIDDEN_TRAIT_DRAW_HELPERS = ("_stable_fraction", "_stable_unit")

#: Every hidden-trait draw behind this seam, keyed by the producer that owns it, mapping
#: the SEED the world uses -> the belt name that forbids it crossing. Both directions are
#: checked: a seed with no belt name is an unnamed leak, and a belt name whose seed has
#: been renamed is a hollow entry that still looks full.
_MEASURED_SEEDS = {
    "simulation/nudge_physics.py": {
        "nudge_susceptibility_": "framing_susceptibility",
        "tone_susceptibility_": "tone_susceptibility",
        "nudge_uplift_": "nudge_uplift",
        "tone_uplift_": "tone_uplift",
    },
    "simulation/conversation_response.py": {
        "conv_trust": "trust",
        "conv_budget_stress": "budget_stress",
        "conv_true_intent_switch": "true_intent",
    },
}

#: Hidden scalars that are DERIVED from the seeded traits above rather than drawn, cited
#: by the function that computes them. These have no seed to rename, so the function name
#: is the citation.
_MEASURED_FUNCTIONS = {
    "simulation/conversation_response.py": {
        "positive_action_probability": "positive_action_probability",
        "_adverse_share": "adverse_share",
    },
}

#: Named RNG substreams in `conversation_response` that are DELIBERATELY not subjects:
#: they seed the draw of the OBSERVABLE response, not a latent trait of the customer. If
#: the belt named these it would be forbidding the seam's own product.
_NON_SUBJECT_SUBSTREAMS = {
    "conversation_positive": "draws the observable action, not the hidden propensity",
    "conversation_adverse": "draws which non-positive outcome was OBSERVED",
    "conversation_channel": "draws the channel the customer answered on -- observable",
    "conversation_latency": "draws the observed response lag -- observable",
}


def _producer_source(module_path: str) -> ast.Module:
    return ast.parse(Path(module_path).read_text(encoding="utf-8"))


def _hidden_trait_seeds(module_path: str) -> set[str]:
    """Every seed literal handed to a hidden-trait draw helper in this module, read from
    the CALL SITES. Deliberately not a substring scan of the source: the module's own
    docstrings name most of these traits in prose, and a text search would score the
    documentation as evidence of the mechanism."""
    seeds: set[str] = set()
    for node in ast.walk(_producer_source(module_path)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        called = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        if called not in _HIDDEN_TRAIT_DRAW_HELPERS:
            continue
        for arg in node.args:
            # `_stable_unit(customer_id, "conv_trust")`
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                seeds.add(arg.value)
            # `_stable_fraction("nudge_uplift_" + customer_id)`
            elif (
                isinstance(arg, ast.BinOp)
                and isinstance(arg.left, ast.Constant)
                and isinstance(arg.left.value, str)
            ):
                seeds.add(arg.left.value)
    return seeds


def test_the_draw_helpers_the_measurement_rests_on_are_still_defined_where_it_looks():
    """FAIL-OPEN GUARD, and the first thing to check because everything below inherits
    it. `_hidden_trait_seeds` finds seeds by matching the helper's NAME at the call site,
    so renaming the helper would make it return the empty set -- and an empty subject is
    how a census passes while measuring nothing."""
    # POPULATION FLOOR (2026-08-27). This test's own docstring names the risk -- "an empty
    # subject is how a census passes while measuring nothing" -- and then loops with every
    # assertion inside, so an empty _MEASURED_SEEDS passes it. Naming a hazard is not
    # guarding against it.
    assert _MEASURED_SEEDS, (
        "_MEASURED_SEEDS is empty -- this census asserts nothing about the draw helpers")
    for module_path in _MEASURED_SEEDS:
        defined = {
            n.name for n in ast.walk(_producer_source(module_path))
            if isinstance(n, ast.FunctionDef)
        }
        assert defined & set(_HIDDEN_TRAIT_DRAW_HELPERS), (
            f"{module_path} defines none of {_HIDDEN_TRAIT_DRAW_HELPERS} -- the draw "
            "helper was renamed and every seed measurement below is now vacuous"
        )


def test_every_hidden_trait_the_world_draws_is_named_by_the_belt():
    """THE DIRECTION THAT MATTERS, and the one this belt did not have until pass 29.
    Reading the belt tells you which leaks were thought of; reading the PRODUCERS tells
    you which exist. This asserts set EQUALITY, so it reds in both directions: a hidden
    trait added to the SIM with no belt name fails here rather than crossing unrefused,
    and a seed renamed out from under a belt entry fails rather than hollowing it."""
    assert _MEASURED_SEEDS, (
        "_MEASURED_SEEDS is empty -- the loop below asserts nothing and the draw helpers this "
        "measurement rests on could all be gone (population floor, 2026-08-27)")
    for module_path, cited in _MEASURED_SEEDS.items():
        found = _hidden_trait_seeds(module_path)
        assert found == set(cited), (
            f"{module_path}: the hidden-trait draws in the source and the seeds the belt "
            f"cites have diverged.\n  drawn but not cited: {sorted(found - set(cited))}\n"
            f"  cited but no longer drawn: {sorted(set(cited) - found)}"
        )
        for seed, belt_name in cited.items():
            assert belt_name in FORBIDDEN_TRUTH_FIELDS, (
                f"{module_path} draws the hidden trait {seed!r} and the belt does not "
                f"name {belt_name!r} -- a payload could carry it across the wall"
            )


def test_the_MEASURED_functions_still_exist_and_the_belt_still_names_them():
    """The derived hidden scalars have no seed, so the function IS the citation. Reds if
    a producer renames the function (the belt entry goes hollow) or if the belt entry is
    dropped (the scalar goes unnamed)."""
    assert _MEASURED_FUNCTIONS, (
        "_MEASURED_FUNCTIONS is empty -- every function this belt claims to have measured could "
        "be gone and this test would still pass (population floor, 2026-08-27)")
    for module_path, cited in _MEASURED_FUNCTIONS.items():
        defined = {
            n.name for n in ast.walk(_producer_source(module_path))
            if isinstance(n, ast.FunctionDef)
        }
        for func_name, belt_name in cited.items():
            assert func_name in defined, (
                f"the belt files {belt_name!r} as measured on {module_path}::{func_name}, "
                "which no longer exists -- either it was renamed (and the belt is now "
                "hollow) or the citation was never true"
            )
            assert belt_name in FORBIDDEN_TRUTH_FIELDS, (
                f"{module_path}::{func_name} computes hidden truth and the belt does not "
                f"name {belt_name!r}"
            )


def test_the_observable_substreams_are_NOT_treated_as_hidden_traits():
    """THE NULL CONTROL ON THE SUBJECT SET. Without this, "the belt names every seed"
    could be satisfied by a belt that forbids the seam's own observable product -- which
    is the shape of a control that reds on a legal payload and then gets relaxed. These
    four seeds draw the OBSERVED response and must stay off the belt."""
    for seed, why in _NON_SUBJECT_SUBSTREAMS.items():
        assert seed not in _MEASURED_SEEDS["simulation/conversation_response.py"], (
            f"{seed} is not a latent trait: {why}"
        )
        assert seed not in FORBIDDEN_TRUTH_FIELDS, f"{seed} must stay observable: {why}"


def test_the_belt_is_a_LITERAL_and_not_derived_from_the_payloads_it_guards():
    """R15 TAUTOLOGY, the guard its payment sibling has carried since pass 27. A denylist
    computed from the dataclasses it guards would move with them and could never fire."""
    src = Path("interface/contracts/conversation_seam.py").read_text(encoding="utf-8")
    node = next(
        n for n in ast.walk(ast.parse(src))
        if isinstance(n, ast.AnnAssign)
        and getattr(n.target, "id", None) == "FORBIDDEN_TRUTH_FIELDS"
    )
    assert isinstance(node.value, ast.Tuple), "FORBIDDEN_TRUTH_FIELDS must be a literal"
    assert node.value.elts, "an empty belt refuses nothing"
    assert all(
        isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.value.elts
    ), "a computed entry would widen with its own subject"


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
    assert mods, (
        "this module parsed to ZERO imports, so the loop below asserts nothing -- an\n"
        "empty population is not a clean wall, it is a scan that stopped working "\
        "(population floor, 2026-08-27)")
    for m in mods:
        assert not m.startswith(("sim", "simulation", "company", "saas")), \
            f"contract must not import {m}"
