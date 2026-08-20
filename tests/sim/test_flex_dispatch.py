"""W1_9 SIM flex-dispatch tests (L1): true (residual-driven) scarcity
schedule, perfect-delivery settlement at the observed price, observables-only
seam emission, and C-S3 dispatch/settlement separability.
"""
from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import numpy as np
import pytest

from interface.contracts.flex_observable_seam import (
    FlexDispatchInstruction,
    FlexSettlementLine,
)
from sim.flex_dispatch import (
    DegenerateFlexError,
    DeliveryModel,
    dispatch_and_settle,
    emit_dispatch_instructions,
    emit_settlement_lines,
    true_scarcity_mask,
)


def _synthetic_record(n=200, seed=0):
    """A small deterministic record: residual and price are CORRELATED but not
    identical (price also carries a gas-like term), so the true (residual)
    scarcity set differs from any price-only set -- the honest triad."""
    rng = np.random.default_rng(seed)
    residual = rng.normal(30000, 4000, n)
    gas_noise = rng.normal(0, 15, n)                 # moves price, not residual
    price = 40 + 0.004 * (residual - 30000) + gas_noise
    dates = np.array([f"2024-{1 + i % 12:02d}-{1 + i % 28:02d}" for i in range(n)])
    return {"dates": dates, "residual_mw": residual, "derived_price": price}


def test_true_scarcity_mask_is_top_tail():
    residual = np.arange(100.0)
    mask = true_scarcity_mask(residual, percentile=95.0)
    assert mask.sum() == 5           # top 5% (>= 95th percentile)
    assert mask[-1] and not mask[0]


def test_true_scarcity_mask_empty_fails_loud():
    with pytest.raises(DegenerateFlexError):
        true_scarcity_mask(np.array([]))


def test_dispatch_only_in_scarcity_periods_and_paid_at_price():
    rec = _synthetic_record()
    truth = dispatch_and_settle(rec, enrolled_mw=2.0, period_hours=1.0)
    assert truth.n_dispatch == int(truth.dispatch_mask.sum())
    # revenue is zero outside dispatch and = enrolled*hours*price inside
    assert np.all(truth.true_utilised_revenue[~truth.dispatch_mask] == 0.0)
    inside = truth.dispatch_mask
    expected = 2.0 * 1.0 * truth.outturn_price[inside]
    assert np.allclose(truth.true_utilised_revenue[inside], expected)
    assert truth.total_true_revenue_gbp > 0.0


def test_revenue_is_linear_in_enrolled_mw():
    """Scale-invariance evidence: doubling enrolment doubles revenue (so the
    normalised triad gap is invariant -- no fabricated MW moves the score)."""
    rec = _synthetic_record()
    a = dispatch_and_settle(rec, enrolled_mw=1.0).total_true_revenue_gbp
    b = dispatch_and_settle(rec, enrolled_mw=2.0).total_true_revenue_gbp
    assert b == pytest.approx(2.0 * a)


def test_seam_emission_is_observable_only_and_async():
    rec = _synthetic_record()
    truth = dispatch_and_settle(rec)
    dispatches = emit_dispatch_instructions(truth)
    settlements = emit_settlement_lines(truth)
    assert len(dispatches) == truth.n_dispatch == len(settlements)
    # payload types are the observable seam types
    assert all(isinstance(r.payload, FlexDispatchInstruction) for r in dispatches)
    assert all(isinstance(r.payload, FlexSettlementLine) for r in settlements)
    # C-S3: matched by correlation_id, settlement observed LATER than dispatch
    dmap = {r.correlation_id: r for r in dispatches}
    for s in settlements:
        assert s.correlation_id in dmap
        assert s.observed_at > dmap[s.correlation_id].observed_at
    # no seam payload exposes residual / true need
    for r in dispatches + settlements:
        assert not hasattr(r.payload, "residual_mw")
        assert not hasattr(r.payload, "true_need")


# --- L2: stochastic portfolio delivery -------------------------------------

def test_l1_perfect_delivery_is_byte_identical():
    """delivery=None must reproduce the L1 perfect-delivery truth exactly (no
    regression: ratio all-ones, revenue unchanged)."""
    rec = _synthetic_record()
    l1 = dispatch_and_settle(rec, enrolled_mw=2.0)
    default = dispatch_and_settle(rec, enrolled_mw=2.0, delivery=None)
    assert np.array_equal(l1.true_utilised_revenue, default.true_utilised_revenue)
    assert np.all(l1.true_delivery_ratio == 1.0)
    assert l1.mean_delivery_ratio == pytest.approx(1.0)


def test_l2_delivery_reduces_delivered_below_instructed():
    """L2: a DeliveryModel makes the true delivered reduction a FRACTION of the
    instructed volume in dispatched periods (rebound/non-response)."""
    rec = _synthetic_record()
    dm = DeliveryModel(mean_ratio=0.7, dispersion=0.05, seed=3)
    truth = dispatch_and_settle(rec, enrolled_mw=2.0, delivery=dm)
    disp = truth.dispatch_mask
    # every dispatched event delivers strictly less than instructed, ratio<1
    assert np.all(truth.true_delivered_mwh[disp] < truth.true_baseline_mwh[disp])
    assert 0.0 < truth.mean_delivery_ratio < 1.0
    # true revenue is correspondingly below the perfect-delivery revenue
    perfect = dispatch_and_settle(rec, enrolled_mw=2.0)
    assert truth.total_true_revenue_gbp < perfect.total_true_revenue_gbp
    # ratios stay within [0, 1] (clipped)
    assert truth.true_delivery_ratio.min() >= 0.0
    assert truth.true_delivery_ratio.max() <= 1.0


def test_l2_delivery_is_deterministic_replay_cs2():
    """C-S2: same seed -> byte-identical delivery ratios (deterministic replay);
    a different seed changes them (genuine stochasticity)."""
    rec = _synthetic_record()
    a = dispatch_and_settle(rec, delivery=DeliveryModel(seed=11))
    b = dispatch_and_settle(rec, delivery=DeliveryModel(seed=11))
    c = dispatch_and_settle(rec, delivery=DeliveryModel(seed=12))
    assert np.array_equal(a.true_delivery_ratio, b.true_delivery_ratio)
    assert not np.array_equal(a.true_delivery_ratio, c.true_delivery_ratio)


def test_l2_settlement_meters_the_stochastic_delivery():
    """The OBSERVABLE metered delivery on the settlement line reflects the true
    (stochastic) delivered reduction, not the instructed volume."""
    rec = _synthetic_record()
    truth = dispatch_and_settle(rec, enrolled_mw=2.0, delivery=DeliveryModel(mean_ratio=0.6, seed=5))
    lines = emit_settlement_lines(truth)
    idx = np.nonzero(truth.dispatch_mask)[0]
    for r, i in zip(lines, idx):
        assert r.payload.metered_delivery_mwh == pytest.approx(float(truth.true_delivered_mwh[i]))
        # metered strictly below the instructed 2.0 MWh in a de-rated world
        assert r.payload.metered_delivery_mwh < 2.0


# ===========================================================================
# EP6 pass 22 -- THE WIRE, counterparty side. The world encodes; it may not
# import the company's codec, so it restates the published contract and builds
# the bytes itself. These proofs are about the ENCODER only; the decoder's are
# in tests/company/market/test_flex_participation.py and the two are
# deliberately never exercised against each other here.
# ===========================================================================

#: The response form as the PUBLISHED SCHEMA states it. Restated in the test
#: rather than imported from either codec: a test that asked the encoder what
#: it emits and then asserted it emits that would be a tautology (R15).
_RESPONSE_WIRE_KEYS = {
    "correlation_id", "status", "schema_version",
    "observed_at", "valid_time", "payload", "error",
}


def _a_settlement_response(**over):
    from interface.contracts.flex_observable_seam import (
        FlexSettlementLine as _L,
    )
    from interface.contracts.flex_observable_seam import (
        FlexSettlementWallResponse as _R,
    )
    from interface.contracts.flex_observable_seam import (
        FlexVenue as _V,
    )
    from interface.contracts.wall_envelope import WallStatus
    line = _L(
        settlement_id="SETT-1", unit_id="U1", venue=_V.BALANCING_MECHANISM,
        window_start=dt.datetime(2024, 1, 1), window_end=dt.datetime(2024, 1, 1, 1),
        metered_delivery_mwh=2.0, utilisation_price_gbp_per_mwh=90.0,
        utilisation_payment_gbp=180.0,
    )
    kw = dict(
        correlation_id="flex-U1-20240101", status=WallStatus.OK, schema_version=1,
        observed_at=dt.datetime(2024, 1, 15), valid_time=dt.date(2024, 1, 1),
        payload=line,
    )
    kw.update(over)
    return _R(**kw)


def test_the_encoder_writes_every_declared_key_INCLUDING_its_nulls():
    """Absence is never agreement: `error` is null on every OK response and its
    KEY is still written. An encoder that omitted null keys would hand the far
    side an absence it could only resolve by defaulting -- the tidy-encoder
    edit anyone would make, and the one that quietly re-introduces defaults."""
    from sim.flex_dispatch import encode_wall_response
    wire = encode_wall_response(_a_settlement_response())
    assert set(wire) == _RESPONSE_WIRE_KEYS
    assert wire["error"] is None
    assert "error" in wire


def test_the_version_on_the_wire_comes_from_the_CONTRACT_not_a_literal(monkeypatch):
    """MUTATION: move the version the encoder reads and the emitted version
    must move with it. A literal `1` in the encoder passes every other test in
    this file and silently mislabels every message the day the schema moves.

    The name is patched, NOT the module reloaded: reloading `sim.flex_dispatch`
    rebinds `DeliveryModel`, `VenueSpec` and friends to fresh class objects
    while every other test module in the suite still holds the old ones, so the
    isolation cost lands on siblings that have nothing to do with this check.
    Tying the patched name back to the contract is the second assertion.
    """
    import sim.flex_dispatch as fd
    from interface.contracts import flex_observable_seam as seam
    assert fd.SCHEMA_VERSION is seam.SCHEMA_VERSION
    assert fd.encode_wall_response(_a_settlement_response())["schema_version"] == 1
    monkeypatch.setattr(fd, "SCHEMA_VERSION", 7)
    assert fd.encode_wall_response(_a_settlement_response())["schema_version"] == 7


def test_a_FORBIDDEN_TRUTH_FIELD_is_refused_BY_NAME_at_the_point_of_emission():
    """R10, the CLASS not the instance. The natural edit -- "the settlement line
    should carry the baseline too" -- produces a perfectly well-formed envelope,
    so the refusal has to be at payload depth and keyed on the contract's own
    forbidden list. NULL CONTROL: the identical fake payload type WITHOUT the
    forbidden field encodes cleanly, so what is being detected is the field and
    not the fixture."""
    from dataclasses import dataclass as _dc

    import sim.flex_dispatch as fd
    from interface.contracts.flex_observable_seam import FORBIDDEN_TRUTH_FIELDS

    @_dc(frozen=True)
    class Leaky:
        settlement_id: str
        true_baseline_mwh: float

    @_dc(frozen=True)
    class Clean:
        settlement_id: str
        metered_delivery_mwh: float

    assert "true_baseline_mwh" in FORBIDDEN_TRUTH_FIELDS
    saved = dict(fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES)
    try:
        fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES.update({"Leaky": Leaky, "Clean": Clean})
        with pytest.raises(fd.SeamCodecError, match="true_baseline_mwh"):
            fd.encode_observable_payload(Leaky("SETT-1", 4.0))
        # null control: same shape, unforbidden field name -> crosses
        assert fd.encode_observable_payload(Clean("SETT-1", 4.0))["fields"] == {
            "settlement_id": "SETT-1", "metered_delivery_mwh": 4.0,
        }
    finally:
        fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES.clear()
        fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES.update(saved)


def test_a_payload_type_the_contract_does_not_declare_OBSERVABLE_is_refused():
    """FAIL-CLOSED. A codec with a generic `dataclasses.asdict` fallback can
    serialise anything, which means it can leak anything -- the truth record
    this module holds is a dataclass too."""
    import sim.flex_dispatch as fd
    with pytest.raises(fd.SeamCodecError, match="OBSERVABLE_RESPONSE_PAYLOAD_TYPES"):
        fd.encode_observable_payload(_synthetic_record())


def test_the_encoder_refuses_types_it_has_no_wire_form_for_rather_than_stringifying():
    """`str(value)` is how a platform ships an object's repr and the receiver
    accepts a string. BOUNDARY: bool is an int subclass, so a True metered
    delivery must be refused rather than crossing as a plausible 1."""
    import sim.flex_dispatch as fd
    with pytest.raises(fd.SeamCodecError, match="bool"):
        fd._encode_scalar(True, "FlexSettlementLine.metered_delivery_mwh")
    with pytest.raises(fd.SeamCodecError, match="no defined wire form"):
        fd._encode_scalar([1, 2], "FlexSettlementLine.metered_delivery_mwh")
    # null controls -- the values this seam's payloads actually carry
    assert fd._encode_scalar(2.0, "x") == 2.0
    assert fd._encode_scalar(dt.datetime(2024, 1, 1), "x") == "2024-01-01T00:00:00"


def test_a_non_envelope_is_refused_rather_than_encoded():
    import sim.flex_dispatch as fd
    with pytest.raises(fd.SeamCodecError, match="expected a WallResponse"):
        fd.encode_wall_response({"correlation_id": "flex-1"})


def test_the_worlds_codec_never_imports_the_companys():
    """The wall, asserted from the AST and not by scanning for lines beginning
    `import`: a docstring sentence that happens to wrap onto such a line would
    red a text-matching control, and a control a stray sentence can red is one
    that gets weakened until it means nothing."""
    tree = ast.parse(Path("sim/flex_dispatch.py").read_text())
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.append(node.module)
        elif isinstance(node, ast.Import):
            mods.extend(a.name for a in node.names)
    for m in mods:
        assert not m.startswith(("company", "saas")), f"wall violation: imports {m}"


def test_the_wire_feeds_carry_one_message_per_object_response():
    """The wire wrappers are the object emitters' bytes, not a second source of
    truth: same count, same correlation ids, same order."""
    from sim.flex_dispatch import (
        emit_settlement_lines as _obj,
    )
    from sim.flex_dispatch import (
        emit_settlement_lines_over_wire as _wire,
    )
    truth = dispatch_and_settle(_synthetic_record())
    objects, wires = _obj(truth), _wire(truth)
    assert len(objects) == len(wires) > 0
    assert [r.correlation_id for r in objects] == [w["correlation_id"] for w in wires]
