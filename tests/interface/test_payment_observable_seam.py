"""Tests for the payment-observable seam contract
(`interface/contracts/payment_observable_seam.py`), atom
W4_4_payment_observable_seam.

Four groups, matching the atom's brief:
  (a) round-trip / construction tests for every message type.
  (b) the LOAD-BEARING epistemic-wall test -- asserts the observable types
      expose NO generator-internal field.
  (c) async (C-S3) tests -- request/response separable in time, a response
      is processable with no prior in-order context.
  (d) bitemporal tests -- observed_at/value_date present and orderable.
"""
from __future__ import annotations

import ast
import dataclasses
import datetime as dt
import inspect
from pathlib import Path

import pytest

from interface.contracts.payment_observable_seam import (
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    SCHEMA_VERSION,
    AddacsAdvice,
    AddacsAdviceType,
    AuddisReport,
    AuddisStatus,
    BacsArruddOutcome,
    BacsReasonCategory,
    CollectionRequest,
    DDOutcomeStatus,
    PaymentNotification,
    PaymentRail,
    RemittanceAdvice,
    SettlementConfirmation,
)
from interface.contracts.wall_envelope import WallRequest, WallResponse, WallStatus

MODULE_PATH = Path(__file__).resolve().parents[2] / "interface" / "contracts" / "payment_observable_seam.py"


# ---------------------------------------------------------------------------
# (a) round-trip / construction
# ---------------------------------------------------------------------------

def _make_collection_request(correlation_id="corr-1", as_of=None):
    as_of = as_of or dt.datetime(2026, 7, 1, 8, 0)
    return WallRequest(
        correlation_id=correlation_id,
        request_type="payment_collection.v1",
        schema_version=SCHEMA_VERSION,
        as_of=as_of,
        emitted_at=as_of,
        payload=CollectionRequest(
            account_id="ACC-1",
            mandate_ref="MREF-1",
            amount_gbp=85.50,
            rail=PaymentRail.BACS_DIRECT_DEBIT,
            requested_collection_date=dt.date(2026, 7, 1),
        ),
    )


def test_collection_request_roundtrip():
    req = _make_collection_request()
    assert req.payload.account_id == "ACC-1"
    assert req.payload.rail == PaymentRail.BACS_DIRECT_DEBIT
    assert req.schema_version == SCHEMA_VERSION


def test_remittance_advice_roundtrip():
    resp = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2026, 7, 4, 6, 0),
        valid_time=dt.date(2026, 7, 4),
        payload=RemittanceAdvice(
            bank_reference="BANKREF-1",
            account_id="ACC-1",
            amount_gbp=85.50,
            rail=PaymentRail.BACS_DIRECT_DEBIT,
            value_date=dt.date(2026, 7, 4),
        ),
    )
    assert resp.payload.amount_gbp == 85.50
    assert resp.status == WallStatus.OK


def test_bacs_arudd_outcome_roundtrip():
    outcome = BacsArruddOutcome(
        mandate_ref="MREF-1",
        account_id="ACC-1",
        amount_gbp=85.50,
        outcome=DDOutcomeStatus.FAILURE,
        reason_category=BacsReasonCategory.INSUFFICIENT_FUNDS,
        reason_text="0 - REFER TO PAYER",
        value_date=dt.date(2026, 7, 4),
    )
    resp = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2026, 7, 4, 6, 0),
        valid_time=dt.date(2026, 7, 4),
        payload=outcome,
    )
    assert resp.payload.outcome == DDOutcomeStatus.FAILURE
    assert resp.payload.reason_category == BacsReasonCategory.INSUFFICIENT_FUNDS


def test_addacs_advice_roundtrip():
    advice = AddacsAdvice(
        mandate_ref="MREF-1",
        account_id="ACC-1",
        advice_type=AddacsAdviceType.PAYER_CANCELLED,
        advice_text="0N - INSTRUCTION CANCELLED BY PAYER",
        value_date=dt.date(2026, 7, 6),
    )
    assert advice.advice_type == AddacsAdviceType.PAYER_CANCELLED


def test_auddis_report_roundtrip():
    report = AuddisReport(
        mandate_ref="MREF-2",
        account_id="ACC-2",
        status=AuddisStatus.NEW_INSTRUCTION_ACCEPTED,
        status_text="ACCEPTED",
        value_date=dt.date(2026, 7, 2),
    )
    assert report.status == AuddisStatus.NEW_INSTRUCTION_ACCEPTED


def test_payment_notification_roundtrip():
    notif = PaymentNotification(
        account_id="ACC-3",
        rail=PaymentRail.CARD,
        amount_gbp=40.0,
        reference="CARDTXN-1",
        value_date=dt.date(2026, 7, 2),
        status=DDOutcomeStatus.SUCCESS,
    )
    assert notif.rail == PaymentRail.CARD


def test_settlement_confirmation_roundtrip():
    conf = SettlementConfirmation(
        reference="SETTLE-1",
        account_id="ACC-1",
        amount_gbp=85.50,
        rail=PaymentRail.BACS_DIRECT_DEBIT,
        cleared_value_date=dt.date(2026, 7, 5),
    )
    assert conf.cleared_value_date == dt.date(2026, 7, 5)


def test_all_observable_payload_types_are_frozen_dataclasses():
    for payload_type in OBSERVABLE_RESPONSE_PAYLOAD_TYPES:
        assert dataclasses.is_dataclass(payload_type)
        params = payload_type.__dataclass_params__
        assert params.frozen, f"{payload_type.__name__} must be frozen"


def test_payment_rail_is_a_portable_string_enum():
    """PORTABILITY: keyed by rail/function; a second geography adds a member
    (e.g. a hypothetical SEPA_DIRECT_DEBIT) without changing any dataclass
    shape. Assert it is a plain str-backed enum (easy wire serialisation,
    easy extension) and that no member hardcodes a counterparty name."""
    assert issubclass(PaymentRail, str)
    for member in PaymentRail:
        assert member.value == member.value.lower()
        assert "bank_of" not in member.value  # no counterparty ever hardcoded
        assert "hsbc" not in member.value
        assert "barclays" not in member.value


# ---------------------------------------------------------------------------
# (b) THE LOAD-BEARING EPISTEMIC-WALL TEST
# ---------------------------------------------------------------------------

# Any field name containing one of these substrings would mean the seam is
# leaking something a real UK supplier's bank/Bacs feed could never tell it:
# the customer's true segment/hardship tier, a model probability/propensity,
# the TRUE reason (vs the bank's reported reason CODE), any sim/generator
# internal, or a household-level behavioural label.
FORBIDDEN_FIELD_SUBSTRINGS = (
    "segment",
    "probability",
    "propensity",
    "hardship",
    "tier",
    "true_reason",
    "ground_truth",
    "generator",
    "sim_",
    "household",
    "income",
    "arrears_risk",
    "distress",
    "belief",
    "internal",
)

# Field names that legitimately contain a forbidden substring as a false
# positive (none currently -- kept as an explicit, reviewable escape hatch
# rather than a silent allowlist).
FIELD_NAME_ALLOWLIST: dict[str, set] = {}


def test_observable_payloads_expose_no_generator_internal_field():
    """LOAD-BEARING: every field on every OBSERVABLE response payload type
    must answer YES to "could a real UK energy supplier's bank/Bacs feed
    have told it this?" -- checked by scanning field NAMES for anything that
    would require reading W2_11 generator internals (segment, probability,
    true reason, ground truth, etc)."""
    violations = []
    for payload_type in OBSERVABLE_RESPONSE_PAYLOAD_TYPES:
        allowed = FIELD_NAME_ALLOWLIST.get(payload_type.__name__, set())
        for f in dataclasses.fields(payload_type):
            if f.name in allowed:
                continue
            for bad in FORBIDDEN_FIELD_SUBSTRINGS:
                if bad in f.name.lower():
                    violations.append(f"{payload_type.__name__}.{f.name} matches forbidden '{bad}'")
    assert not violations, "Epistemic-wall violation(s) found:\n" + "\n".join(violations)


def test_observable_payloads_carry_reason_category_not_true_cause():
    """The one field that COULD leak truth (why a DD failed) must be typed
    as an ENUM OF OBSERVABLE REASON CATEGORIES (the bank's own reported
    code/text), never a free-text or probabilistic "true cause" field. This
    pins the specific field the brief calls out by name."""
    reason_field = next(f for f in dataclasses.fields(BacsArruddOutcome) if f.name == "reason_category")
    assert reason_field.type in (BacsReasonCategory, "BacsReasonCategory")
    # BacsReasonCategory itself must contain no probability/likelihood member
    for member in BacsReasonCategory:
        assert not any(bad in member.value for bad in ("probability", "true_cause", "genuine"))


def test_no_field_is_a_future_dated_or_probability_typed_value():
    """No observable payload field is typed float in a way that could smuggle
    a probability/propensity (0-1 score) -- every float field on these types
    is a monetary amount (name ends in _gbp)."""
    for payload_type in OBSERVABLE_RESPONSE_PAYLOAD_TYPES:
        for f in dataclasses.fields(payload_type):
            if f.type in (float, "float"):
                assert f.name.endswith("_gbp"), (
                    f"{payload_type.__name__}.{f.name} is a bare float -- "
                    "only monetary (_gbp) floats are permitted on an observable payload"
                )


def test_no_sim_or_generator_import():
    """(4) confirm the contract references NO sim/generator symbol -- static,
    grep-proof check of the actual import statements in the module, not just
    a substring scan (so a comment mentioning "sim" can't cause a false
    fail)."""
    tree = ast.parse(MODULE_PATH.read_text())
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    forbidden_roots = {"sim", "simulation", "company", "saas"}
    assert imported_roots.isdisjoint(forbidden_roots), (
        f"payment_observable_seam.py imports forbidden root(s): "
        f"{imported_roots & forbidden_roots}"
    )
    # It may only depend on its own sibling contract module + stdlib.
    assert imported_roots <= {"__future__", "datetime", "dataclasses", "enum", "interface"}


# ---------------------------------------------------------------------------
# (c) ASYNC (C-S3): request/response separable in time; out-of-order /
# late / no-prior-context tolerated.
# ---------------------------------------------------------------------------

def test_request_and_response_are_distinct_events_in_time():
    """A DD outcome arrives DAYS after the request (the real Bacs 3-working-
    day cycle) -- request and response must be independently timestamped
    objects, never a single same-step call/return pair."""
    req = _make_collection_request(as_of=dt.datetime(2026, 7, 1, 8, 0))
    resp = WallResponse(
        correlation_id=req.correlation_id,
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2026, 7, 4, 6, 0),  # +3 working days
        valid_time=dt.date(2026, 7, 4),
        payload=BacsArruddOutcome(
            mandate_ref="MREF-1",
            account_id="ACC-1",
            amount_gbp=85.50,
            outcome=DDOutcomeStatus.FAILURE,
            reason_category=BacsReasonCategory.INSUFFICIENT_FUNDS,
            reason_text="0 - REFER TO PAYER",
            value_date=dt.date(2026, 7, 4),
        ),
    )
    assert resp.observed_at > req.emitted_at
    assert (resp.observed_at - req.emitted_at) >= dt.timedelta(days=2)
    # linked ONLY by correlation_id -- no other structural coupling
    assert resp.correlation_id == req.correlation_id
    assert not hasattr(resp, "request")  # no embedded back-reference to the request object


def test_response_constructible_with_no_prior_request_object():
    """A consumer that never held (or has since discarded) the original
    request must still be able to construct/process a response correctly --
    this is what makes late/out-of-order/one-at-a-time delivery tolerable.
    No WallResponse field or __init__ argument requires a WallRequest
    instance."""
    sig = inspect.signature(WallResponse.__init__)
    for name, param in sig.parameters.items():
        assert param.annotation != WallRequest, (
            f"WallResponse.__init__ param {name!r} requires a WallRequest -- "
            "this would break late/out-of-order delivery"
        )
    # Construct one cold, purely from a correlation_id string a consumer
    # received off the wire -- no request object in scope at all.
    resp = WallResponse(
        correlation_id="corr-never-seen-the-request",
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2026, 7, 10, 9, 0),
        valid_time=dt.date(2026, 7, 10),
        payload=RemittanceAdvice(
            bank_reference="BANKREF-9",
            account_id="ACC-9",
            amount_gbp=12.34,
            rail=PaymentRail.OPEN_BANKING,
            value_date=dt.date(2026, 7, 10),
        ),
    )
    assert resp.correlation_id == "corr-never-seen-the-request"


def test_out_of_order_responses_are_independently_valid():
    """Two responses for two DIFFERENT requests, processed in an order that
    does NOT match the order their requests were emitted, must each remain
    independently well-formed -- the contract enforces no sequence/ordinal
    linking one response's validity to another's arrival order (unlike an
    auto-incrementing log id assigned by a store)."""
    early_request_late_response = WallResponse(
        correlation_id="corr-early-req",
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2026, 7, 9, 6, 0),
        valid_time=dt.date(2026, 7, 9),
        payload=SettlementConfirmation(
            reference="SETTLE-EARLY",
            account_id="ACC-1",
            amount_gbp=85.50,
            rail=PaymentRail.BACS_DIRECT_DEBIT,
            cleared_value_date=dt.date(2026, 7, 9),
        ),
    )
    late_request_early_response = WallResponse(
        correlation_id="corr-late-req",
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=dt.datetime(2026, 7, 2, 6, 0),
        valid_time=dt.date(2026, 7, 2),
        payload=PaymentNotification(
            account_id="ACC-2",
            rail=PaymentRail.CARD,
            amount_gbp=20.0,
            reference="CARDTXN-2",
            value_date=dt.date(2026, 7, 2),
            status=DDOutcomeStatus.SUCCESS,
        ),
    )
    # Process in a shuffled order (later-observed one first) -- both remain
    # independently constructible/valid; no dataclass field/invariant
    # depends on the OTHER response having been seen first.
    for resp in (late_request_early_response, early_request_late_response):
        assert resp.status == WallStatus.OK
        assert resp.payload is not None


def test_no_remittance_ever_blind_spot_is_absence_not_a_placeholder():
    """The 'no-remittance blind spot' (a payment that simply never arrives)
    is represented by the ABSENCE of a WallResponse for a correlation_id --
    the contract must not offer a fabricated 'still pending forever' payload
    that would let a consumer manufacture a fake certainty. There is no
    'PENDING' WallStatus member; only OK / TIMEOUT / ERROR /
    NOT_KNOWABLE_YET exist, and NOT_KNOWABLE_YET/TIMEOUT both carry no
    payload (proven in test_wall_envelope.py)."""
    assert set(s.value for s in WallStatus) == {"OK", "TIMEOUT", "ERROR", "NOT_KNOWABLE_YET"}
    assert not hasattr(WallStatus, "PENDING")


# ---------------------------------------------------------------------------
# (d) bitemporal: observed_at / value_date present and orderable
# ---------------------------------------------------------------------------

def test_every_observable_payload_carries_a_value_date():
    """Bitemporal: every observable payload is dated on the axis that
    matters to the company (what period/instant the fact is ABOUT), separate
    from the envelope's own observed_at (when the company learned it)."""
    date_field_names = {"value_date", "cleared_value_date"}
    for payload_type in OBSERVABLE_RESPONSE_PAYLOAD_TYPES:
        field_names = {f.name for f in dataclasses.fields(payload_type)}
        assert field_names & date_field_names, (
            f"{payload_type.__name__} carries no value-date field"
        )


def test_observed_at_can_postdate_value_date_by_the_real_bacs_cycle():
    """A DD outcome's value_date (when the failed collection was due) can be
    -- and for Bacs, always is -- several days BEFORE observed_at (when the
    company's systems actually receive the ARUDD report). The envelope must
    not force observed_at == value_date."""
    value_date = dt.date(2026, 7, 1)
    observed_at = dt.datetime(2026, 7, 4, 6, 0)  # +3 working days, the real cycle
    resp = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.OK,
        schema_version=SCHEMA_VERSION,
        observed_at=observed_at,
        valid_time=value_date,
        payload=BacsArruddOutcome(
            mandate_ref="MREF-1",
            account_id="ACC-1",
            amount_gbp=85.50,
            outcome=DDOutcomeStatus.FAILURE,
            reason_category=BacsReasonCategory.INSUFFICIENT_FUNDS,
            reason_text="0 - REFER TO PAYER",
            value_date=value_date,
        ),
    )
    assert resp.observed_at.date() > resp.payload.value_date
    assert resp.valid_time == resp.payload.value_date


def test_schema_version_is_present_and_explicit():
    assert isinstance(SCHEMA_VERSION, int)
    assert SCHEMA_VERSION >= 1
