"""W1_9 flex-observable seam tests (L1): roundtrip, no-sim/company import,
async (C-S3) separability, and the epistemic-wall field guarantee (no true
baseline / true need leaks across the seam).
"""
from __future__ import annotations

import ast
import datetime as dt
import dataclasses
from pathlib import Path

import pytest

from interface.contracts.flex_observable_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    SCHEMA_VERSION,
    FlexDirection,
    FlexDispatchInstruction,
    FlexDispatchWallResponse,
    FlexEnrolment,
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
    for m in mods:
        assert not m.startswith(("sim", "simulation", "company", "saas")), \
            f"contract must not import {m}"
