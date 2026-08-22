"""W1_9 company flex-participation tests (L1): the belief consumes ONLY the
observed price (a price-derived scarcity proxy), computes expected utilisation
revenue, sums observable settlement lines, and imports no SIM internals.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import numpy as np
import pytest

from company.market.flex_participation import (
    form_participation_belief,
    realised_revenue_from_settlement,
)
from interface.contracts.flex_observable_seam import (
    FlexSettlementLine,
    FlexVenue,
)


def test_belief_predicts_top_price_periods():
    price = np.arange(100.0)
    belief = form_participation_belief(price, enrolled_mw=1.0, period_hours=1.0,
                                       price_percentile=95.0)
    assert belief.n_predicted_dispatch == 5
    assert belief.predicted_dispatch_mask[-1]
    assert not belief.predicted_dispatch_mask[0]
    # revenue zero outside predicted dispatch, price*mw*h inside
    assert np.all(belief.expected_utilised_revenue[~belief.predicted_dispatch_mask] == 0.0)
    assert belief.total_expected_revenue_gbp > 0.0


def test_belief_empty_price_fails_loud():
    with pytest.raises(ValueError):
        form_participation_belief([], enrolled_mw=1.0, period_hours=1.0)


def test_realised_revenue_sums_settlement_lines_and_tolerates_empty():
    assert realised_revenue_from_settlement(None) == 0.0
    assert realised_revenue_from_settlement([]) == 0.0
    lines = [
        FlexSettlementLine(
            settlement_id=f"S{i}", unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM,
            window_start=dt.datetime(2024, 1, i + 1), window_end=dt.datetime(2024, 1, i + 1, 1),
            metered_delivery_mwh=1.0, utilisation_price_gbp_per_mwh=100.0 + i,
            utilisation_payment_gbp=100.0 + i)
        for i in range(3)
    ]
    assert realised_revenue_from_settlement(lines) == pytest.approx(303.0)


def test_no_sim_import():
    """The company flex module reads ONLY the typed observable seam + numpy --
    never sim/simulation (the epistemic wall)."""
    src = Path("company/market/flex_participation.py").read_text()
    tree = ast.parse(src)
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.append(node.module)
        elif isinstance(node, ast.Import):
            mods.extend(a.name for a in node.names)
    for m in mods:
        assert not m.startswith(("sim", "simulation")), f"wall violation: imports {m}"


# ===========================================================================
# EP6 pass 22 -- THE WIRE, company side. The company owns its codec and calls
# it. EVERY fixture below is HAND-WRITTEN against the published schema and
# never produced by the world's encoder: a fixture built by calling the other
# side's codec agrees with itself and never asks whether the two agree.
# ===========================================================================

_LINE_FIELDS = {
    "settlement_id": "SETT-U1-20240101",
    "unit_id": "U1",
    "venue": "balancing_mechanism",
    "window_start": "2024-01-01T00:00:00",
    "window_end": "2024-01-01T01:00:00",
    "metered_delivery_mwh": 2.0,
    "utilisation_price_gbp_per_mwh": 90.0,
    "utilisation_payment_gbp": 180.0,
}


#: The credential the flex system operator holds. Written here as the LITERAL a
#: counterparty presents, never as the fingerprint the company stores: a fixture
#: built from the receiver's own table would prove the receiver agrees with
#: itself. `sim/flex_dispatch.py::SYSTEM_OPERATOR_CREDENTIAL` is the module that
#: really holds it, and this file may not import from `sim/**`.
_SYSTEM_OPERATOR_CREDENTIAL = "system-operator-01::participant-credential::v1"


def _wire(**over):
    """One settlement response inside its transport frame, keyed exactly as the
    published schemas state -- the ENVELOPE's and, since EP6 pass 62, the
    FRAME's.

    HAND-WRITTEN ON BOTH LAYERS, for the reason the header gives about the
    envelope: a frame built by calling the world's `frame_venue_message` would
    agree with the world's idea of a frame and never ask whether the two sides
    agree. The sender, the credential and the hand-over stamp are written out
    here from the published frame form.

    `schema_version` IS 2, and that is a fact about the counterparty rather than
    a fixture detail: the flex seam is on v2 and `COUNTERPARTY_REGISTRY` has
    both flex operators on v2 only, so a v1 line -- readable by this build --
    is refused VERSION_NOT_SPOKEN as a message from a release that does not
    exist. Framing the feed is what made that distinction reachable here.

    Keyword overrides apply to the ENVELOPE (that is what every caller below is
    varying); `frame=` overrides the frame itself.
    """
    fields = dict(_LINE_FIELDS)
    fields.update(over.pop("fields", {}))
    frame_over = over.pop("frame", {})
    msg = {
        "correlation_id": "flex-U1-20240101",
        "status": "OK",
        "schema_version": 2,
        "observed_at": "2024-01-15T00:00:00",
        "valid_time": "2024-01-01",
        "payload": {"payload_type": "FlexSettlementLine", "fields": fields},
        "error": None,
    }
    msg.update(over)
    frame = {
        "sender": "SYSTEM-OPERATOR-01",
        "credential": _SYSTEM_OPERATOR_CREDENTIAL,
        "handed_over_at": "2024-01-15T06:00:00",
        "envelope": msg,
    }
    frame.update(frame_over)
    return frame


def test_a_hand_written_message_decodes_to_the_contracts_own_type():
    """The independence evidence. This dict was written from the SCHEMA, not
    from the world's encoder, and the enum/datetime/float values it names had
    to be right for it to cross at all."""
    from company.market.flex_participation import observe_settlement_wire
    line, = observe_settlement_wire([_wire()])
    assert isinstance(line, FlexSettlementLine)
    assert line.venue is FlexVenue.BALANCING_MECHANISM
    assert line.window_start == dt.datetime(2024, 1, 1)
    assert line.metered_delivery_mwh == 2.0


def test_an_absent_payload_field_is_REFUSED_and_never_defaulted():
    """MUTATION + NULL CONTROL. Defaulting is how a company settles against a
    figure no counterparty sent, and the gap this module is scored on would
    then be measuring the default."""
    from company.interfaces.wall_protocol import WallProtocolError
    from company.market.flex_participation import observe_settlement_wire
    short = dict(_LINE_FIELDS)
    del short["metered_delivery_mwh"]
    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire([_wire(payload={
            "payload_type": "FlexSettlementLine", "fields": short})])
    assert exc.value.reason == "MISSING_FIELD"
    assert "metered_delivery_mwh" in str(exc.value)
    # null control: restore the one field and the identical message crosses
    assert observe_settlement_wire([_wire()])[0].metered_delivery_mwh == 2.0


def test_a_message_that_never_stated_its_version_is_refused_not_relabelled():
    """FAIL-OPEN, the sibling pattern that would silently relabel a foreign
    counterparty's message as the one version this build speaks today. A
    MISSING version and an UNSUPPORTED one are different failures and must
    stay distinguishable -- "you did not say what you speak" and "you speak a
    dialect I do not know" call for different repairs."""
    from company.interfaces.wall_protocol import WallProtocolError
    from company.market.flex_participation import observe_settlement_wire
    versionless = _wire()
    del versionless["envelope"]["schema_version"]
    with pytest.raises(WallProtocolError) as absent:
        observe_settlement_wire([versionless])
    assert absent.value.reason == "MISSING_FIELD"
    with pytest.raises(WallProtocolError) as unknown:
        observe_settlement_wire([_wire(schema_version=99)])
    assert unknown.value.reason == "UNSUPPORTED_VERSION"


def test_a_SIM_TRUTH_FIELD_is_refused_BY_NAME_even_when_the_contract_declares_it():
    """R10, and the reason the named check is not redundant with the generic
    unknown-key rule. MUTATION: give the contract a `true_baseline_mwh` field.
    The generic rule now WELCOMES it -- it is a declared field -- and only the
    name-keyed refusal stops the company being handed the SIM's counterfactual,
    which is the one quantity the flex triad's gap exists to measure the error
    of. NULL CONTROL: the same fake type with an unforbidden field name decodes
    cleanly, so what fires is the name and not the mutation's scaffolding."""
    from dataclasses import dataclass as _dc

    import company.market.flex_participation as fp
    from company.interfaces.wall_protocol import WallProtocolError

    @_dc(frozen=True)
    class Leaky:
        settlement_id: str
        true_baseline_mwh: float

    @_dc(frozen=True)
    class Clean:
        settlement_id: str
        metered_delivery_mwh: float

    saved_types = dict(fp._OBSERVABLE_PAYLOAD_TYPES)
    saved_hints = dict(fp._OBSERVABLE_PAYLOAD_HINTS)
    try:
        fp._OBSERVABLE_PAYLOAD_TYPES.update({"Leaky": Leaky, "Clean": Clean})
        fp._OBSERVABLE_PAYLOAD_HINTS.update({
            "Leaky": {"settlement_id": str, "true_baseline_mwh": float},
            "Clean": {"settlement_id": str, "metered_delivery_mwh": float},
        })
        with pytest.raises(WallProtocolError) as exc:
            fp.decode_observable_payload({
                "payload_type": "Leaky",
                "fields": {"settlement_id": "S1", "true_baseline_mwh": 4.0},
            })
        assert exc.value.reason == "CONTRACT_VIOLATION"
        assert "true_baseline_mwh" in str(exc.value)
        assert fp.decode_observable_payload({
            "payload_type": "Clean",
            "fields": {"settlement_id": "S1", "metered_delivery_mwh": 4.0},
        }) == Clean("S1", 4.0)
    finally:
        fp._OBSERVABLE_PAYLOAD_TYPES.clear()
        fp._OBSERVABLE_PAYLOAD_TYPES.update(saved_types)
        fp._OBSERVABLE_PAYLOAD_HINTS.clear()
        fp._OBSERVABLE_PAYLOAD_HINTS.update(saved_hints)


def test_an_undeclared_key_is_refused_rather_than_tolerated():
    """A schema that grew announces itself by its VERSION, never by a key
    appearing quietly -- otherwise the decoder can no longer tell a v2
    counterparty from a v1 one."""
    from company.interfaces.wall_protocol import WallProtocolError
    from company.market.flex_participation import observe_settlement_wire
    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire([_wire(fields={"availability_fee_gbp": 3.0})])
    assert exc.value.reason == "UNKNOWN_FIELD"


def test_a_bool_where_the_contract_declares_a_number_is_MALFORMED_not_one():
    """BOUNDARY, the value this rule is most easily wrong about: bool is an int
    subclass, so a True metered delivery would decode to a plausible,
    actionable 1.0 and be settled against. NULL CONTROL: a plain int crosses,
    because JSON has no int/float distinction and refusing 2 where 2.0 was
    meant would refuse honest traffic."""
    from company.interfaces.wall_protocol import WallProtocolError
    from company.market.flex_participation import observe_settlement_wire
    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire([_wire(fields={"metered_delivery_mwh": True})])
    assert exc.value.reason == "MALFORMED_FIELD"
    assert observe_settlement_wire(
        [_wire(fields={"metered_delivery_mwh": 2})])[0].metered_delivery_mwh == 2.0


def test_a_MISROUTED_feed_is_refused_because_the_two_payloads_share_field_names():
    """C-S3: the instruction feed and the settlement feed are separate events
    in time. Their payloads share four field names, so an untagged or
    mis-routed message is exactly the one a field-set guess would accept."""
    from company.interfaces.wall_protocol import WallProtocolError
    from company.market.flex_participation import observe_settlement_wire
    instruction = _wire(payload={
        "payload_type": "FlexDispatchInstruction",
        "fields": {
            "instruction_id": "BOA-1", "unit_id": "U1",
            "venue": "balancing_mechanism", "direction": "turn_down",
            "window_start": "2024-01-01T00:00:00",
            "window_end": "2024-01-01T01:00:00",
            "cleared_price_gbp_per_mwh": 90.0,
        },
    })
    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire([instruction])
    assert exc.value.reason == "CONTRACT_VIOLATION"
    assert "FlexDispatchInstruction" in str(exc.value)
    # null control: the same message read by the feed it belongs to
    from company.market.flex_participation import observe_response_wire
    from interface.contracts.flex_observable_seam import FlexDispatchInstruction
    assert observe_response_wire(
        instruction, expect=FlexDispatchInstruction).instruction_id == "BOA-1"


def test_an_untagged_payload_cannot_be_routed_at_all():
    from company.interfaces.wall_protocol import WallProtocolError
    from company.market.flex_participation import observe_settlement_wire
    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire([_wire(payload=dict(_LINE_FIELDS))])
    assert exc.value.reason == "MISSING_FIELD"


def test_an_empty_message_is_not_an_empty_period():
    """A failed feed and a period with no settlement look identical if a
    payload-less envelope is allowed through: the company would under-count its
    own revenue and read the shortfall as the world's."""
    from company.interfaces.wall_protocol import WallProtocolError
    from company.market.flex_participation import observe_settlement_wire
    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire([_wire(status="TIMEOUT", payload=None)])
    assert exc.value.reason == "CONTRACT_VIOLATION"


def test_the_decoder_is_reached_through_the_companys_OWN_codec():
    """Not a style point. One codec for every seam is what makes the envelope
    rules (exact key set, version support, bitemporal coordinates) hold on THIS
    seam without being restated here -- and a restatement is what silently
    drifts. Asserted by patching the codec entry point and requiring the seam
    read to fail: a decoder that had quietly grown its own envelope parser
    would leave this test green."""
    import company.market.flex_participation as fp
    sentinel = RuntimeError("codec reached")

    def _boom(*a, **k):
        raise sentinel

    original = fp.decode_framed_response
    try:
        fp.decode_framed_response = _boom
        with pytest.raises(RuntimeError) as exc:
            fp.observe_settlement_wire([_wire()])
        assert exc.value is sentinel
    finally:
        fp.decode_framed_response = original
    assert fp.observe_settlement_wire([_wire()])[0].unit_id == "U1"
