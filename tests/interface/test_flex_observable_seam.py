"""W1_9 flex-observable seam tests (L1): roundtrip, no-sim/company import,
async (C-S3) separability, and the epistemic-wall field guarantee (no true
baseline / true need leaks across the seam).
"""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
from pathlib import Path

import pytest

from interface.contracts.flex_observable_seam import (
    ENROLMENT_REFUSAL_CODES,
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_PAYLOAD_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    REQUEST_PAYLOAD_FIELDS,
    SCHEMA_VERSION,
    FlexDirection,
    FlexDispatchInstruction,
    FlexDispatchWallResponse,
    FlexEnrolment,
    FlexEnrolmentOutcome,
    FlexEnrolmentWallRequest,
    FlexSettlementLine,
    FlexSettlementWallResponse,
    FlexVenue,
)
from interface.contracts.wall_envelope import WallStatus


def _enrolment():
    return FlexEnrolment(
        unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM, offered_mw=1.0,
        direction=FlexDirection.TURN_DOWN,
        window_start=dt.datetime(2024, 1, 10, 17, 0),
        window_end=dt.datetime(2024, 1, 10, 18, 0),
    )


def test_enrolment_request_roundtrip():
    req = FlexEnrolmentWallRequest(
        correlation_id="c1", request_type="flex_enrolment",
        schema_version=SCHEMA_VERSION, as_of=dt.datetime(2024, 1, 10),
        emitted_at=dt.datetime(2024, 1, 10), payload=_enrolment(),
    )
    assert req.payload.offered_mw == 1.0
    assert req.payload.venue is FlexVenue.BALANCING_MECHANISM


def test_dispatch_and_settlement_roundtrip():
    instr = FlexDispatchInstruction(
        instruction_id="BOA1", unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM,
        direction=FlexDirection.TURN_DOWN,
        window_start=dt.datetime(2024, 1, 10, 17, 0),
        window_end=dt.datetime(2024, 1, 10, 18, 0),
        cleared_price_gbp_per_mwh=250.0,
    )
    dr = FlexDispatchWallResponse(
        correlation_id="c1", status=WallStatus.OK, schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2024, 1, 10, 17, 0), valid_time=dt.date(2024, 1, 10),
        payload=instr,
    )
    assert dr.payload.cleared_price_gbp_per_mwh == 250.0

    line = FlexSettlementLine(
        settlement_id="S1", unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM,
        window_start=dt.datetime(2024, 1, 10, 17, 0),
        window_end=dt.datetime(2024, 1, 10, 18, 0),
        metered_delivery_mwh=1.0, utilisation_price_gbp_per_mwh=250.0,
        utilisation_payment_gbp=250.0,
    )
    sr = FlexSettlementWallResponse(
        correlation_id="c1", status=WallStatus.OK, schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2024, 1, 26, 17, 0), valid_time=dt.date(2024, 1, 10),
        payload=line,
    )
    assert sr.payload.utilisation_payment_gbp == 250.0


def test_async_dispatch_and_settlement_are_separate_events_c_s3():
    """C-S3: settlement is a SEPARATE, LATER WallResponse than the dispatch,
    matched ONLY by correlation_id -- never same-step resolution."""
    corr = "flex-U1-20240110"
    dr = FlexDispatchWallResponse(
        correlation_id=corr, status=WallStatus.OK, schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2024, 1, 10, 17, 0), valid_time=dt.date(2024, 1, 10),
        payload=FlexDispatchInstruction(
            instruction_id="BOA1", unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM,
            direction=FlexDirection.TURN_DOWN,
            window_start=dt.datetime(2024, 1, 10, 17, 0),
            window_end=dt.datetime(2024, 1, 10, 18, 0),
            cleared_price_gbp_per_mwh=250.0),
    )
    sr = FlexSettlementWallResponse(
        correlation_id=corr, status=WallStatus.OK, schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2024, 1, 26, 17, 0), valid_time=dt.date(2024, 1, 10),
        payload=FlexSettlementLine(
            settlement_id="S1", unit_id="U1", venue=FlexVenue.BALANCING_MECHANISM,
            window_start=dt.datetime(2024, 1, 10, 17, 0),
            window_end=dt.datetime(2024, 1, 10, 18, 0),
            metered_delivery_mwh=1.0, utilisation_price_gbp_per_mwh=250.0,
            utilisation_payment_gbp=250.0),
    )
    assert dr.correlation_id == sr.correlation_id          # matched by id alone
    assert sr.observed_at > dr.observed_at                 # settlement lands LATER


def test_wall_guarantee_no_truth_fields_on_observable_payloads():
    """No observable payload may carry a field that names the SIM's hidden
    truth (residual / true baseline / true need)."""
    for payload_type in OBSERVABLE_RESPONSE_PAYLOAD_TYPES:
        field_names = {f.name for f in dataclasses.fields(payload_type)}
        leaked = field_names & set(FORBIDDEN_TRUTH_FIELDS)
        assert not leaked, f"{payload_type.__name__} leaks truth fields: {leaked}"


def test_no_sim_or_company_import():
    """The contract module is PURE -- it imports nothing from sim/simulation/
    company (only the wall envelope + stdlib)."""
    src = Path("interface/contracts/flex_observable_seam.py").read_text()
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


# ===========================================================================
# EP6 pass 53 -- the enrolment ANSWER's declared surface.
#
# `FlexEnrolmentOutcome` is already inside the existing wall guarantee above
# (it is a member of OBSERVABLE_RESPONSE_PAYLOAD_TYPES, so the truth-field
# scan covers it without an instance test -- R10). What that scan cannot ask
# is whether the DECLARATION still describes the dataclass, which is the fact
# the counterparty's decoder refuses against.
# ===========================================================================


def test_the_DECLARED_surface_matches_the_dataclass_for_every_payload_it_names():
    """The published key set is what both counterparties refuse against, so a
    field added to a payload and not declared is a field that cannot cross.

    Written over the WHOLE table rather than the one type this pass added: a
    per-type assertion is an instance fix wearing a class's clothes, and the
    next payload would arrive undeclared with nothing to catch it (R10)."""
    by_name = {t.__name__: t for t in OBSERVABLE_RESPONSE_PAYLOAD_TYPES}
    for name, declared in OBSERVABLE_PAYLOAD_FIELDS.items():
        assert name in by_name, f"{name} is declared but is not an observable payload type"
        actual = tuple(f.name for f in dataclasses.fields(by_name[name]))
        assert actual == tuple(declared), (
            f"{name}'s declaration {tuple(declared)} no longer describes the dataclass "
            f"{actual} -- one side of the wall would refuse what the other sends"
        )
    undeclared = sorted(set(by_name) - set(OBSERVABLE_PAYLOAD_FIELDS))
    assert not undeclared, f"observable payload(s) with no published key set: {undeclared}"


def test_MUTATION_a_field_added_to_the_payload_and_not_DECLARED_is_caught():
    """The control above must fail on its own named defect. The mutation is the
    realistic one -- somebody widens a payload and forgets the declaration."""
    original = OBSERVABLE_PAYLOAD_FIELDS["FlexEnrolmentOutcome"]
    OBSERVABLE_PAYLOAD_FIELDS["FlexEnrolmentOutcome"] = original[:-1]
    try:
        with pytest.raises(AssertionError):
            test_the_DECLARED_surface_matches_the_dataclass_for_every_payload_it_names()
    finally:
        OBSERVABLE_PAYLOAD_FIELDS["FlexEnrolmentOutcome"] = original
    # NULL CONTROL: restored, the control passes -- so it is not always-red.
    test_the_DECLARED_surface_matches_the_dataclass_for_every_payload_it_names()


def test_an_ACCEPTANCE_says_THAT_you_are_registered_and_never_why_or_against_what_else():
    """The deliberate absences are the design, so they are asserted rather than
    left in a docstring. A volume field would always equal the request's own
    `offered_mw` (a mirror no test could fail on); a queue position, clearing
    price or merit order would be the venue's internals crossing the wall."""
    fields = {f.name for f in dataclasses.fields(FlexEnrolmentOutcome)}
    assert fields == {"enrolment_reference", "unit_id", "venue"}
    # No `accepted` flag: a refusal is the envelope's ERROR path, and a False
    # branch here would duplicate it.
    assert "accepted" not in fields


def test_the_refusal_vocabulary_is_STRUCTURAL_and_carries_no_economic_reason():
    """R13: a venue in this build refuses what it CANNOT register, never what
    it does not fancy. An economic acceptance rule is a difficulty parameter
    and those are the director's."""
    assert set(ENROLMENT_REFUSAL_CODES) == {
        "WINDOW_NOT_A_WINDOW",
        "OFFER_NOT_DELIVERABLE",
        "WINDOW_ALREADY_CLOSED",
        "UNIT_ALREADY_ENROLLED",
    }


def test_the_request_payload_declaration_describes_the_enrolment_dataclass():
    """The outbound direction is not the epistemic wall -- the company owns
    every field here -- but the world may not DEFAULT one of them, which is
    what this declaration exists for."""
    actual = tuple(f.name for f in dataclasses.fields(FlexEnrolment))
    assert actual == tuple(REQUEST_PAYLOAD_FIELDS["FlexEnrolment"])


def test_the_seam_version_moved_with_the_surface():
    """A new payload type under an unchanged version number is the drift the
    census's surface pin exists to catch; the version is bumped in the same
    edit that adds the type."""
    assert SCHEMA_VERSION == 2
