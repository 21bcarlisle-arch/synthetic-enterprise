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

import sim.flex_dispatch as sim_flex_dispatch
from interface.contracts.flex_observable_seam import (
    ENROLMENT_REFUSAL_CODES,
    REQUEST_PAYLOAD_FIELDS,
    SCHEMA_VERSION,
    FlexDispatchInstruction,
    FlexSettlementLine,
)
from sim.flex_dispatch import (
    ENROLMENT_REQUEST_TYPE,
    DegenerateFlexError,
    DeliveryModel,
    EnrolmentRefused,
    SeamCodecError,
    VenueRegistrations,
    answer_enrolment,
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


def _book_covering(
    truth,
    *,
    unit_id="FLEX_UNIT_1",
    venue=None,
    pad_hours=0.0,
):
    """The VENUE's book with one registration spanning this truth's whole
    record -- what a party that had actually enrolled would leave behind.

    Built through `VenueRegistrations.register`, the venue's own API, so a
    fixture cannot register something the desk would have refused.

    The window ENDS at the last DISPATCHED event, not at the last date on the
    record: a period nobody was called in emits nothing, so padding measured
    against it would move a boundary no message sits on. `pad_hours` shortens
    (negative) or lengthens the window against the last event that actually
    crosses, which is how the containment rule is exercised.
    """
    from interface.contracts.flex_observable_seam import (
        FlexDirection,
        FlexEnrolment,
        FlexVenue,
    )
    from sim.flex_dispatch import _base_date

    venue = venue or FlexVenue.BALANCING_MECHANISM
    stamps = [_base_date(d) for d in truth.dates]
    called = [s for s, on in zip(stamps, truth.dispatch_mask) if on]
    assert called, "a book covering nothing proves nothing -- this truth dispatches"
    book = VenueRegistrations()
    book.register(FlexEnrolment(
        unit_id=unit_id,
        venue=venue,
        offered_mw=float(truth.enrolled_mw),
        direction=FlexDirection.TURN_DOWN,
        window_start=min(stamps),
        window_end=(
            max(called)
            + dt.timedelta(hours=truth.period_hours)
            + dt.timedelta(hours=pad_hours)
        ),
    ))
    return book


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


def test_the_version_on_the_wire_comes_from_the_CONTRACT_not_a_literal():
    """MUTATION: move the version the encoder reads and the emitted version
    must move with it. A literal `1` in the encoder passes every other test in
    this file and silently mislabels every message the day the schema moves.

    WHAT MOVED, AND WHY THE MUTATION MOVED WITH IT (EP6 pass 44). Until then the
    encoder wrote this module's OWN `SCHEMA_VERSION` and this test patched that
    name. Both readings are honestly 'not a literal', and only one of them can
    ever fail on a real message: an encoder stamping its own constant makes the
    wire version STRUCTURALLY UNABLE to differ from the reader's, so the
    decoder's version check -- the one thing a version number is for -- could
    never fire on anything this seam emitted. The encoder now preserves
    `response.schema_version`, so the mutation has to move the MESSAGE's vintage,
    which is the only input on which a preserving and a relabelling encoder
    disagree. Patching the module name would now pass against BOTH.

    The contract tie stays as an assertion rather than being dropped with the
    monkeypatch: a seam whose messages stopped being stamped from the contract
    would leave the preservation check green while the vintage on the wire came
    from nowhere in particular.
    """
    import sim.flex_dispatch as fd
    from interface.contracts import flex_observable_seam as seam
    assert fd.SCHEMA_VERSION is seam.SCHEMA_VERSION
    assert fd.encode_wall_response(_a_settlement_response())["schema_version"] == 1
    foreign = _a_settlement_response(schema_version=7)
    assert fd.encode_wall_response(foreign)["schema_version"] == 7
    # NULL CONTROL. 7 is chosen for being a vintage this seam does not itself
    # speak; the day the constant reaches it, the assertion above stops being a
    # test of anything and this line is what says so.
    assert seam.SCHEMA_VERSION != 7


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

    from interface.contracts.flex_observable_seam import FlexVenue

    assert "true_baseline_mwh" in FORBIDDEN_TRUTH_FIELDS
    saved = dict(fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES)
    try:
        fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES.update({"Leaky": Leaky})
        with pytest.raises(fd.SeamCodecError, match="true_baseline_mwh"):
            fd.encode_observable_payload(Leaky("SETT-1", 4.0))
    finally:
        fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES.clear()
        fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES.update(saved)
    # NULL CONTROL: the real declared payload, no forbidden name -> crosses, so
    # what the refusal above detects is the FIELD and not the fixture. It uses
    # the real type because since EP6 pass 25 a fabricated payload type is
    # refused on its own account (the closed set), which is a stronger wall
    # than this test's subject and would mask it.
    clean = fd.encode_observable_payload(
        FlexSettlementLine(
            settlement_id="SETT-1", unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM,
            window_start=dt.datetime(2026, 1, 1),
            window_end=dt.datetime(2026, 1, 1, 0, 30),
            metered_delivery_mwh=4.0, utilisation_price_gbp_per_mwh=50.0,
            utilisation_payment_gbp=200.0,
        )
    )
    assert clean["fields"]["metered_delivery_mwh"] == 4.0
    assert not set(clean["fields"]) & set(FORBIDDEN_TRUTH_FIELDS)


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
    objects, wires = _obj(truth), _wire(truth, registrations=_book_covering(truth))
    assert len(objects) == len(wires) > 0
    assert [r.correlation_id for r in objects] == [w["correlation_id"] for w in wires]


# ---------------------------------------------------------------------------
# The CLOSED observable field set (EP6 pass 25). R15 mutation proofs: each
# asserts the control fires on its own named defect, and the null control
# asserts it still admits the legitimate payload.
#
# The defect these replace was measured, not imagined: FORBIDDEN_TRUTH_FIELDS
# named 2 of FlexDispatchTruth's 11 fields, so `true_delivered_mwh` encoded
# onto the wire unrefused while the codec's docstring claimed the CLASS was
# refused. A denylist cannot answer "is this observable".
# ---------------------------------------------------------------------------


def _settlement_line_shaped(**extra):
    """A FlexSettlementLine-shaped payload, optionally with fields the contract
    never declared. Registered under the real type name because the mutation
    being modelled is someone EDITING the real class, not smuggling a new one."""
    import dataclasses

    from interface.contracts.flex_observable_seam import FlexVenue

    dropped = extra.pop("_drop", ())
    fields = [
        ("settlement_id", str), ("unit_id", str), ("venue", FlexVenue),
        ("window_start", dt.datetime), ("window_end", dt.datetime),
        ("metered_delivery_mwh", float), ("utilisation_price_gbp_per_mwh", float),
        ("utilisation_payment_gbp", float),
    ]
    fields = [f for f in fields if f[0] not in dropped]
    fields += [(name, float) for name in extra]
    mutant = dataclasses.make_dataclass("FlexSettlementLine", fields, frozen=True)
    return mutant


def _encode_with(mutant_type, monkeypatch, **values):
    import sim.flex_dispatch as _fd

    registry = dict(_fd._ENCODABLE_RESPONSE_PAYLOAD_TYPES)
    registry["FlexSettlementLine"] = mutant_type
    monkeypatch.setattr(_fd, "_ENCODABLE_RESPONSE_PAYLOAD_TYPES", registry)
    return _fd.encode_observable_payload(mutant_type(**values))


_BASE_LINE = dict(
    settlement_id="s1", unit_id="u1",
    window_start=dt.datetime(2026, 1, 1), window_end=dt.datetime(2026, 1, 1, 0, 30),
    metered_delivery_mwh=1.0, utilisation_price_gbp_per_mwh=50.0,
    utilisation_payment_gbp=50.0,
)


def test_null_control_the_declared_payload_still_crosses():
    """The control must admit the real thing, or it proves nothing by refusing."""
    from interface.contracts.flex_observable_seam import FlexVenue
    from sim.flex_dispatch import encode_observable_payload

    wire = encode_observable_payload(
        FlexSettlementLine(venue=FlexVenue.BALANCING_MECHANISM, **_BASE_LINE)
    )
    assert set(wire["fields"]) == {
        "settlement_id", "unit_id", "venue", "window_start", "window_end",
        "metered_delivery_mwh", "utilisation_price_gbp_per_mwh",
        "utilisation_payment_gbp",
    }


def test_mutation_an_undeclared_truth_field_is_refused_at_emission(monkeypatch):
    """THE named defect. `true_delivered_mwh` is SIM ground truth off this
    module's own FlexDispatchTruth and is on NO denylist -- the closed set
    refuses it because it was never declared observable, which is the R10 form
    (the class fails, not the instance someone predicted)."""
    from interface.contracts.flex_observable_seam import (
        FORBIDDEN_TRUTH_FIELDS,
        FlexVenue,
    )
    from sim.flex_dispatch import SeamCodecError

    assert "true_delivered_mwh" not in FORBIDDEN_TRUTH_FIELDS, (
        "this test's whole point is a truth field the DENYLIST cannot see; "
        "if it is now listed, pick another off-list FlexDispatchTruth field"
    )
    mutant = _settlement_line_shaped(true_delivered_mwh=float)
    with pytest.raises(SeamCodecError, match="has not declared observable"):
        _encode_with(
            mutant, monkeypatch,
            venue=FlexVenue.BALANCING_MECHANISM, true_delivered_mwh=4.2, **_BASE_LINE,
        )


def test_mutation_a_stale_declaration_is_refused(monkeypatch):
    """FAIL-CLOSED the other way: if the payload loses a field the contract
    still certifies, the declaration has gone stale and the codec says so
    rather than silently emitting a narrower wire form."""
    from interface.contracts.flex_observable_seam import FlexVenue
    from sim.flex_dispatch import SeamCodecError

    values = {k: v for k, v in _BASE_LINE.items() if k != "utilisation_payment_gbp"}
    mutant = _settlement_line_shaped(_drop=("utilisation_payment_gbp",))
    with pytest.raises(SeamCodecError, match="omits declared observable field"):
        _encode_with(mutant, monkeypatch, venue=FlexVenue.BALANCING_MECHANISM, **values)


def test_the_declaration_is_not_derived_from_the_payload_it_certifies():
    """R15 TAUTOLOGY guard. The closed set must be WRITTEN OUT, not computed
    from the dataclass -- a set derived from its own subject widens whenever
    the subject widens and could never have caught the defect above."""
    import ast
    from pathlib import Path

    src = Path("interface/contracts/flex_observable_seam.py").read_text()
    tree = ast.parse(src)
    node = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.AnnAssign)
        and getattr(n.target, "id", None) == "OBSERVABLE_PAYLOAD_FIELDS"
    )
    assert isinstance(node.value, ast.Dict), "must be a literal declaration"
    for entry in node.value.values:
        assert isinstance(entry, ast.Tuple), "each payload's fields must be literal"
        for element in entry.elts:
            assert isinstance(element, ast.Constant) and isinstance(element.value, str)


# ===========================================================================
# EP6 pass 53 -- THE ENROLMENT EXCHANGE, VENUE (WORLD) SIDE.
#
# Controls for the request leg landed untested by pass 52. The venue's codec
# is written against the PUBLISHED schema and never against the company's
# encoder, so these build their wire by hand from the contract's own declared
# key set -- importing the company's encoder to test the venue's decoder would
# make the round trip a handshake with itself.
# ===========================================================================

_E_START = dt.datetime(2026, 3, 1, 16, 0)
_E_END = dt.datetime(2026, 3, 1, 19, 0)
_E_CLOCK = dt.datetime(2026, 2, 20, 10, 0)


def _enrolment_wire(
    *,
    unit_id="UNIT-A",
    venue="dfs_turn_down",
    offered_mw=5.0,
    start=_E_START,
    end=_E_END,
    correlation_id="flex-enrol-1",
    emitted_at=dt.datetime(2026, 2, 20, 9, 0),
):
    """A request built from the CONTRACT's declared key set, not from the
    company's encoder."""
    return {
        "correlation_id": correlation_id,
        "request_type": ENROLMENT_REQUEST_TYPE,
        "schema_version": SCHEMA_VERSION,
        "as_of": dt.datetime(2026, 2, 20, 9, 0).isoformat(),
        "emitted_at": emitted_at.isoformat(),
        "payload": {
            "unit_id": unit_id,
            "venue": venue,
            "offered_mw": float(offered_mw),
            "direction": "turn_down",
            "window_start": start.isoformat(),
            "window_end": end.isoformat(),
        },
    }


def test_the_venue_ACCEPTS_a_well_formed_enrolment_and_mints_its_own_reference():
    """NULL CONTROL for every refusal below: the venue is not always-red."""
    reg = VenueRegistrations()
    answer = answer_enrolment(_enrolment_wire(), venue_clock=_E_CLOCK, registrations=reg)

    assert answer["status"] == "OK"
    assert answer["payload"]["fields"]["enrolment_reference"] == "DFS_TURN_DOWN-REG-000001"


def test_C_S2_a_RESENT_enrolment_returns_the_SAME_reference_and_does_not_mint_a_second():
    """Idempotency. A resolver that recomputed would hand the company two
    references for one registration -- and the venue would have sold the same
    unit's MW twice into the same window."""
    reg = VenueRegistrations()
    wire = _enrolment_wire()

    first = answer_enrolment(wire, venue_clock=_E_CLOCK, registrations=reg)
    second = answer_enrolment(wire, venue_clock=_E_CLOCK, registrations=reg)

    assert first["payload"]["fields"]["enrolment_reference"] == (
        second["payload"]["fields"]["enrolment_reference"]
    )
    assert second["status"] == "OK"  # a redelivery is not read as a double enrolment


def test_an_OVERLAPPING_window_is_refused_but_a_CONSECUTIVE_one_is_not():
    """The half-open boundary is the only value this rule is easy to get wrong
    about: a registration ending exactly when another starts is two consecutive
    availability periods, not a double sale. Both directions asserted, because
    a refusal that also fired here would make the venue unable to hold a book
    at all."""
    reg = VenueRegistrations()
    answer_enrolment(_enrolment_wire(), venue_clock=_E_CLOCK, registrations=reg)

    overlapping = answer_enrolment(
        _enrolment_wire(
            start=dt.datetime(2026, 3, 1, 18, 0),
            end=dt.datetime(2026, 3, 1, 21, 0),
            correlation_id="flex-enrol-2",
        ),
        venue_clock=_E_CLOCK,
        registrations=reg,
    )
    assert overlapping["status"] == "ERROR"
    assert overlapping["error"]["code"] == "UNIT_ALREADY_ENROLLED"

    # NULL CONTROL: butt-jointed, not overlapping -- accepted.
    consecutive = answer_enrolment(
        _enrolment_wire(
            start=_E_END,
            end=dt.datetime(2026, 3, 1, 22, 0),
            correlation_id="flex-enrol-3",
        ),
        venue_clock=_E_CLOCK,
        registrations=reg,
    )
    assert consecutive["status"] == "OK"


def test_the_SAME_unit_may_enrol_at_a_DIFFERENT_venue_over_the_same_window():
    """Overlap is scoped BY VENUE deliberately: a multi-venue book is the
    legitimate stacking case, and the contention it creates is a thing the
    company is supposed to be able to get wrong."""
    reg = VenueRegistrations()
    answer_enrolment(_enrolment_wire(), venue_clock=_E_CLOCK, registrations=reg)

    other = answer_enrolment(
        _enrolment_wire(venue="capacity_market", correlation_id="flex-enrol-4"),
        venue_clock=_E_CLOCK,
        registrations=reg,
    )
    assert other["status"] == "OK"


def test_ABSENCE_IS_NEVER_AGREEMENT_a_missing_payload_key_is_refused_not_defaulted():
    """The fail-open direction. A defaulted `offered_mw` would register the
    company for a volume it never offered and then settle it against that
    volume."""
    wire = _enrolment_wire()
    del wire["payload"]["offered_mw"]

    with pytest.raises(SeamCodecError):
        answer_enrolment(wire, venue_clock=_E_CLOCK, registrations=VenueRegistrations())


def test_MUTATION_the_venue_judges_the_window_on_ITS_OWN_clock_not_the_senders():
    """A refusal keyed on a timestamp the SENDER controls is a refusal the
    sender can switch off.

    The mutation moves `emitted_at` -- the only clock on the wire -- to claim
    the request was sent while the window was open. The refusal must not
    move, because the venue read it after the window closed."""
    closed = dict(
        start=dt.datetime(2026, 1, 1, 1, 0),
        end=dt.datetime(2026, 1, 1, 2, 0),
    )
    honest = answer_enrolment(
        _enrolment_wire(**closed), venue_clock=_E_CLOCK, registrations=VenueRegistrations()
    )
    assert honest["error"]["code"] == "WINDOW_ALREADY_CLOSED"

    forged = answer_enrolment(
        _enrolment_wire(**closed, emitted_at=dt.datetime(2025, 12, 31, 12, 0)),
        venue_clock=_E_CLOCK,
        registrations=VenueRegistrations(),
    )
    assert forged["error"]["code"] == "WINDOW_ALREADY_CLOSED"

    # NULL CONTROL: the same venue, the same clock, an OPEN window -- accepted.
    # Without this the two assertions above would also hold of a venue that
    # refused everything.
    assert answer_enrolment(
        _enrolment_wire(), venue_clock=_E_CLOCK, registrations=VenueRegistrations()
    )["status"] == "OK"


def test_a_request_MISROUTED_to_this_desk_is_refused_as_unreadable_not_as_a_rejection():
    """An unreadable message has no correlation_id to answer on, which is why
    it raises rather than crossing back as a structured refusal."""
    wire = _enrolment_wire()
    wire["request_type"] = "capacity_auction_bid"

    with pytest.raises(SeamCodecError):
        answer_enrolment(wire, venue_clock=_E_CLOCK, registrations=VenueRegistrations())


def test_the_venue_may_not_send_a_refusal_reason_the_company_cannot_branch_on():
    """An undeclared code is one no company could branch on, so it may not be
    sent at all. Both directions: a declared code constructs cleanly."""
    with pytest.raises(ValueError):
        EnrolmentRefused("WE_JUST_DIDNT_FANCY_IT", "no reason the contract publishes")

    assert EnrolmentRefused(ENROLMENT_REFUSAL_CODES[0], "declared").code in (
        ENROLMENT_REFUSAL_CODES
    )


def test_a_REFUSAL_carries_no_payload_and_an_ACCEPTANCE_carries_no_error():
    """The envelope's own invariant, asserted on the bytes this desk actually
    emits: a non-OK response may not carry a payload."""
    reg = VenueRegistrations()
    refused = answer_enrolment(
        _enrolment_wire(offered_mw=-1.0), venue_clock=_E_CLOCK, registrations=reg
    )
    assert refused["error"]["code"] == "OFFER_NOT_DELIVERABLE"
    assert refused.get("payload") is None

    accepted = answer_enrolment(_enrolment_wire(), venue_clock=_E_CLOCK, registrations=reg)
    assert accepted.get("error") is None


def test_the_venue_side_may_not_import_the_company():
    """The wall. The venue's codec is written against the published schema; an
    encoder built by reading the receiver makes the round trip a handshake with
    itself."""
    import sim.flex_dispatch as mod

    src = Path(mod.__file__).read_text()
    assert "import company" not in src and "from company" not in src


def test_the_venues_refusal_set_IS_the_contracts_declaration_and_not_a_copy(monkeypatch):
    """The venue decodes against the CONTRACT's published key set, so a field
    declared on the enrolment is decodable the day it is declared and not a day
    before.

    MUTATED ON THE MODULE'S OWN BINDING, never by reloading the module. An
    earlier draft of this test called `importlib.reload(sim.flex_dispatch)`,
    which redefines every class in it -- and the 22 tests in
    `test_flex_dispatch_stacked.py` that had already imported the old classes
    then failed `isinstance` against the new ones. It passed when this file ran
    alone and redded the gate, which is this project's own rule met live: never
    mutate a shared module while a suite is in flight.
    """
    # The binding is the contract's declaration, restated as a set.
    assert sim_flex_dispatch._ENROLMENT_PAYLOAD_FIELDS == frozenset(
        REQUEST_PAYLOAD_FIELDS["FlexEnrolment"]
    )

    # NULL CONTROL: against the real declaration, a well-formed wire is accepted.
    assert answer_enrolment(
        _enrolment_wire(), venue_clock=_E_CLOCK, registrations=VenueRegistrations()
    )["status"] == "OK"

    # MUTATION: the venue expects a key the company does not publish, so a wire
    # built to the CONTRACT's real set is refused as incomplete.
    monkeypatch.setattr(
        sim_flex_dispatch,
        "_ENROLMENT_PAYLOAD_FIELDS",
        frozenset(REQUEST_PAYLOAD_FIELDS["FlexEnrolment"]) | {"settlement_priority"},
    )
    with pytest.raises(SeamCodecError):
        answer_enrolment(
            _enrolment_wire(), venue_clock=_E_CLOCK, registrations=VenueRegistrations()
        )


# ---------------------------------------------------------------------------
# THE VENUE'S TEETH (EP6 pass 57) -- a dispatch is only lawful against a
# registration this venue holds.
#
# Pass 54 gave the running loop a request leg and the HARNESS compared the unit
# the world settled against the unit the venue registered. That is a real check
# and it is an OBSERVATION: the world could still produce the statement being
# observed. These are the WORLD's own refusals, and each carries the null
# control that says the venue is not simply refusing everything.
# ---------------------------------------------------------------------------


def _venue_and_direction():
    from interface.contracts.flex_observable_seam import FlexVenue
    return FlexVenue


def test_the_registered_unit_CROSSES__the_null_control_for_every_refusal_below():
    """NULL CONTROL. A unit registered over the delivered span settles and is
    instructed exactly as before -- so the refusals below are discriminating and
    not a venue that has stopped speaking."""
    truth = dispatch_and_settle(_synthetic_record())
    book = _book_covering(truth)

    lines = sim_flex_dispatch.emit_settlement_lines_over_wire(truth, registrations=book)
    instructions = sim_flex_dispatch.emit_dispatch_instructions_over_wire(
        truth, registrations=book)

    assert len(lines) == len(instructions) == truth.n_dispatch > 0
    assert all(m["status"] == "OK" for m in lines)


def test_MUTATION_a_unit_this_venue_NEVER_REGISTERED_cannot_be_settled_at_all():
    """The state the world was in until this pass: `unit_id` is a keyword
    default, so the venue settled whoever the caller named. The book is
    consulted against what was EMITTED, not against the argument, so an emitter
    that ignored its own `unit_id` is caught by the same check."""
    truth = dispatch_and_settle(_synthetic_record())
    book = _book_covering(truth, unit_id="FLEX_UNIT_1")

    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch) as exc:
        sim_flex_dispatch.emit_settlement_lines_over_wire(
            truth, unit_id="A_UNIT_NOBODY_ENROLLED", registrations=book)
    assert "A_UNIT_NOBODY_ENROLLED" in str(exc.value)

    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch):
        sim_flex_dispatch.emit_dispatch_instructions_over_wire(
            truth, unit_id="A_UNIT_NOBODY_ENROLLED", registrations=book)


def test_an_EMPTY_book_refuses_rather_than_passing__the_fail_open_case():
    """R15 fail-open, which is where this class of control usually dies: a venue
    that has registered NOBODY must settle nobody. `covers` returns None for an
    empty book and None is a refusal, not a pass."""
    truth = dispatch_and_settle(_synthetic_record())
    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch):
        sim_flex_dispatch.emit_settlement_lines_over_wire(
            truth, registrations=VenueRegistrations())


def test_MUTATION_a_call_running_PAST_the_declared_availability_is_refused():
    """CONTAINMENT, NOT OVERLAP, and this is the boundary the rule is easiest to
    be wrong about.

    The registration is cut HALF a period short, so the last event begins inside
    the declared availability and ENDS outside it: it overlaps, and it is not
    covered. A venue answering `overlapping` here would call the unit over
    minutes it never offered -- and `overlapping` is a real method on this class,
    written for the different question "may I register this?", so collapsing the
    two is the plausible mistake rather than an invented one. Half a period, not
    a whole one: a whole one leaves the window butt-jointed to the registration,
    which overlap ALSO refuses, so it would not discriminate.
    """
    truth = dispatch_and_settle(_synthetic_record())

    exact = _book_covering(truth)
    assert sim_flex_dispatch.emit_settlement_lines_over_wire(
        truth, registrations=exact), "the exactly-covering book must accept"

    part_way = _book_covering(truth, pad_hours=-0.5 * truth.period_hours)
    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch):
        sim_flex_dispatch.emit_settlement_lines_over_wire(truth, registrations=part_way)


def test_MUTATION_a_registration_at_ANOTHER_VENUE_does_not_license_this_one():
    """A unit registered into the Capacity Market has not thereby offered itself
    to the Balancing Mechanism -- the two are different products with different
    obligations, and the multi-venue book `dispatch_and_settle_stacked` models
    is exactly where conflating them would pay twice. Dropping `venue` from the
    book's key passes this."""
    FlexVenue = _venue_and_direction()
    truth = dispatch_and_settle(_synthetic_record())

    elsewhere = _book_covering(truth, venue=FlexVenue.CAPACITY_MARKET)
    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch):
        sim_flex_dispatch.emit_settlement_lines_over_wire(
            truth, venue=FlexVenue.BALANCING_MECHANISM, registrations=elsewhere)

    # NULL CONTROL: the SAME book licenses the venue it was actually made at.
    assert sim_flex_dispatch.emit_settlement_lines_over_wire(
        truth, venue=FlexVenue.CAPACITY_MARKET, registrations=elsewhere)


def test_the_book_is_REQUIRED_and_not_a_defaulted_argument():
    """The fail-open shape this control would otherwise have: a `registrations`
    defaulting to None makes the check pass for every caller who forgot it. Both
    wire legs refuse to be called without one."""
    truth = dispatch_and_settle(_synthetic_record())
    for leg in (
        sim_flex_dispatch.emit_settlement_lines_over_wire,
        sim_flex_dispatch.emit_dispatch_instructions_over_wire,
    ):
        with pytest.raises(TypeError):
            leg(truth)


# ---------------------------------------------------------------------------
# THE VENUE'S TEETH ON THE STACKED (L3) LEGS -- EP6 pass 58.
#
# Pass 57 belted the single-venue wire legs and left these two unbelted for a
# stated reason: the L3 loop registered at no venue at all, so belting them
# would have refused every stacked run. `solicit_registration_stacked` removed
# that reason, so these are the same four proofs at the granularity where the
# multi-venue book is actually load-bearing -- one unit, N SEPARATE
# registrations, and a call licensed only by the registration at ITS OWN venue.
# ---------------------------------------------------------------------------


def _stacked_venues(portfolio_mw=100.0):
    """A CONTENDED two-venue book, matching the triad's own default: both
    venues offer 60% of one portfolio, so the physical ceiling binds."""
    from interface.contracts.flex_observable_seam import FlexVenue
    from sim.flex_dispatch import FlexPaymentBasis, VenueSpec

    offered = 0.6 * float(portfolio_mw)
    return [
        VenueSpec(venue=FlexVenue.BALANCING_MECHANISM,
                  basis=FlexPaymentBasis.UTILISATION, offered_mw=offered, priority=1),
        VenueSpec(venue=FlexVenue.DSO_LOCAL_CONSTRAINT,
                  basis=FlexPaymentBasis.UTILISATION, offered_mw=offered, priority=2,
                  call_pct=sim_flex_dispatch.DEFAULT_AVAILABILITY_CALL_PERCENTILE),
    ]


def _stacked_truth(portfolio_mw=100.0):
    return sim_flex_dispatch.dispatch_and_settle_stacked(
        _synthetic_record(), venues=_stacked_venues(portfolio_mw),
        portfolio_mw=portfolio_mw)


def _stacked_book(truth, *, unit_id="FLEX_UNIT_1", only=None, pad_hours=0.0):
    """The VENUE side's book for a stacked portfolio: ONE registration per
    venue, all for the same unit, each spanning the whole record.

    `only` restricts the book to a subset of venue keys -- the mutation that
    matters here and cannot be expressed on a single-venue book: a party
    correctly registered at one venue and called at another.

    Windows are measured against the last event that ACTUALLY crosses at that
    venue, for the reason `_book_covering` gives: padding against a period
    nobody was called in would move a boundary no message sits on.
    """
    from interface.contracts.flex_observable_seam import FlexDirection, FlexEnrolment
    from sim.flex_dispatch import _base_date

    stamps = [_base_date(d) for d in truth.dates]
    book = VenueRegistrations()
    for v in truth.venues:
        if only is not None and v.key not in only:
            continue
        called = [s for s, on in zip(stamps, truth.call_mask[v.key]) if on]
        assert called, f"a book covering nothing proves nothing -- {v.key} must be called"
        book.register(FlexEnrolment(
            unit_id=unit_id,
            venue=v.venue,
            offered_mw=float(v.offered_mw),
            direction=FlexDirection.TURN_DOWN,
            window_start=min(stamps),
            window_end=(max(called)
                        + dt.timedelta(hours=truth.period_hours)
                        + dt.timedelta(hours=pad_hours)),
        ))
    return book


def test_MUTATION_a_stacked_world_calling_a_unit_NOBODY_enrolled_is_refused():
    """The state the stacked feeds were in until this pass: `unit_id` was a
    keyword default on both, so the portfolio the company formed a STACKING
    belief about need never have registered anywhere. Checked against what was
    EMITTED, so an emitter ignoring its own argument is caught by the same
    check."""
    truth = _stacked_truth()
    book = _stacked_book(truth)

    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch) as exc:
        sim_flex_dispatch.emit_settlement_lines_stacked_over_wire(
            truth, unit_id="A_UNIT_NOBODY_ENROLLED", registrations=book)
    assert "A_UNIT_NOBODY_ENROLLED" in str(exc.value)

    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch):
        sim_flex_dispatch.emit_dispatch_instructions_stacked_over_wire(
            truth, unit_id="A_UNIT_NOBODY_ENROLLED", registrations=book)

    # NULL CONTROL: the full book admits both feeds, so the refusals above are
    # about the unit and not about the legs being broken.
    assert sim_flex_dispatch.emit_settlement_lines_stacked_over_wire(
        truth, registrations=book)
    assert sim_flex_dispatch.emit_dispatch_instructions_stacked_over_wire(
        truth, registrations=book)


def test_MUTATION_a_book_missing_ONE_venue_refuses_only_that_venues_feed():
    """THE DEFECT ONLY A STACKED BOOK CAN HAVE, and the reason this belt is not
    just the single-venue one copied.

    A portfolio registered at the Balancing Mechanism and called at a DSO local
    constraint is a KNOWN unit at an unjoined venue -- a check keyed on the unit
    alone passes it, and the party is then instructed and paid at a market it
    never entered. `covers` is keyed by (unit, venue), so the venue it did join
    still crosses: that half is the null control, and without it this test would
    also pass on a book that refused everything.
    """
    truth = _stacked_truth()
    keys = [v.key for v in truth.venues]
    assert len(keys) == 2, "this proof needs a genuinely multi-venue book"
    partial = _stacked_book(truth, only={keys[0]})

    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch) as exc:
        sim_flex_dispatch.emit_dispatch_instructions_stacked_over_wire(
            truth, registrations=partial)
    assert keys[1] in str(exc.value)

    # NULL CONTROL: that same partial book DOES license its own venue's feed --
    # proven on a truth carrying only the venue it registered, so the refusal
    # above is about the missing registration and not about the book being inert.
    solo = sim_flex_dispatch.dispatch_and_settle_stacked(
        _synthetic_record(), venues=_stacked_venues()[:1], portfolio_mw=100.0)
    assert sim_flex_dispatch.emit_dispatch_instructions_stacked_over_wire(
        solo, registrations=_stacked_book(solo))


def test_an_EMPTY_book_refuses_the_stacked_legs_too__the_fail_open_case():
    """R15 fail-open at the stacked granularity: a venue that has registered
    NOBODY must instruct and settle nobody. `covers` returns None on an empty
    book and None is a refusal."""
    truth = _stacked_truth()
    for leg in (sim_flex_dispatch.emit_settlement_lines_stacked_over_wire,
                sim_flex_dispatch.emit_dispatch_instructions_stacked_over_wire):
        with pytest.raises(sim_flex_dispatch.UnregisteredDispatch):
            leg(truth, registrations=VenueRegistrations())


def test_MUTATION_a_stacked_call_running_PAST_the_declared_availability_is_refused():
    """CONTAINMENT, NOT OVERLAP, on the stacked legs. Cut by HALF a period, the
    only shape where the two rules actually disagree: a whole period leaves the
    window butt-jointed, which overlap refuses as well and so would not
    discriminate."""
    truth = _stacked_truth()

    assert sim_flex_dispatch.emit_settlement_lines_stacked_over_wire(
        truth, registrations=_stacked_book(truth)), "the exactly-covering book must accept"

    part_way = _stacked_book(truth, pad_hours=-0.5 * truth.period_hours)
    with pytest.raises(sim_flex_dispatch.UnregisteredDispatch):
        sim_flex_dispatch.emit_settlement_lines_stacked_over_wire(
            truth, registrations=part_way)


def test_the_stacked_book_is_REQUIRED_and_not_a_defaulted_argument():
    """The fail-open shape this control would otherwise have: a `registrations`
    defaulting to None makes the check pass for every caller who forgot it.
    Every wire leg in this module now refuses to be called without a book."""
    truth = _stacked_truth()
    for leg in (
        sim_flex_dispatch.emit_settlement_lines_stacked_over_wire,
        sim_flex_dispatch.emit_dispatch_instructions_stacked_over_wire,
    ):
        with pytest.raises(TypeError):
            leg(truth)
