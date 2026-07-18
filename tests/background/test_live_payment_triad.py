"""Tests for the LIVE per-run payment coupled triad
(`background.live_payment_triad`) -- the L3 escalation that runs the W2_11 <->
D5 belief-vs-truth flow inside run_phase2b and writes the gap per run.

These cover: (1) the live measurement is non-trivial and exhibits the
no-remittance blind-spot witness; (2) R15 MUTATION -- the live gap must be able
to FAIL AND to collapse: neutering the wall so the company sees every failure
(belief == truth) collapses the detection gap to 0, proving the live
measurement genuinely fires on its own defect rather than sitting at a constant;
(3) determinism (C-S2); (4) the single-truth derivation feeds analytics
coherently.
"""
from __future__ import annotations

from datetime import date

import pytest

from background import live_payment_triad as lpt
from background.live_payment_triad import LivePaymentTriad, _derive_analytics_record
from simulation.payment_behaviour_source import PaymentEvent
from interface.contracts.payment_observable_seam import (
    BacsArruddOutcome,
    BacsReasonCategory,
    DDOutcomeStatus,
    SCHEMA_VERSION,
)
from interface.contracts.wall_envelope import WallResponse, WallStatus


# A population large + stressed enough to guarantee a real mixture of DD and
# non-DD failures (the blind spot needs genuine non-DD failures to witness).
_N_CUSTOMERS = 150
_MONTHS = 6


def _build_triad(**kwargs) -> LivePaymentTriad:
    triad = LivePaymentTriad(**kwargs)
    for i in range(_N_CUSTOMERS):
        cid = f"RESI{i:05d}"
        for m in range(1, _MONTHS + 1):
            triad.record_period(
                customer_id=cid,
                due_date=date(2020, m, 28),
                amount_gbp=120.0,
                income_stress_value="high",   # high stress -> plenty of failures
                segment="resi",
            )
    return triad


def test_live_gap_is_non_trivial_and_exhibits_the_blind_spot():
    triad = _build_triad()
    result = triad.measure()
    assert result is not None

    det = result["detection"]
    bel = result["belief"]
    age = result["ageing"]
    assert det.gap is not None and det.gap > 0.0, det
    assert bel.gap is not None and bel.gap > 0.0, bel
    assert age.gap is not None

    stats = result["stats"]
    # The blind-spot witness: genuine non-DD failures MUST exist and NONE of them
    # may ever be flagged (a non-zero flagged-non-DD count would be a wall leak).
    assert stats["n_true_non_dd_failures"] > 0, "population didn't exercise the blind spot"
    assert stats["n_flagged_non_dd_failures"] == 0
    assert 0 < stats["n_flagged_failures"] < stats["n_true_failures"]


def test_R15_mutation_leaking_the_wall_collapses_the_live_gap(monkeypatch):
    """R15: the live gap must be able to FAIL on its own defect.

    Baseline: the honest live detection gap is > 0 (the company cannot see
    non-DD failures across the wall). MUTATION: neuter the wall so the company
    observes EVERY true failure -- including the non-DD ones that structurally
    should emit nothing -- i.e. belief == truth. If the live measurement is
    real, the detection gap must COLLAPSE toward 0. A gap that stayed put under
    this mutation would be theatre (CONTROLS_THAT_CANNOT_FAIL.md)."""
    baseline = _build_triad().measure()
    assert baseline is not None
    baseline_gap = baseline["detection"].gap
    assert baseline_gap > 0.0

    # Neuter emit_wall_responses INSIDE the live module: for a failed event of
    # ANY payment method, leak a DD-failure WallResponse (the observable the
    # blind spot should have withheld). Success/dispute unchanged.
    def _leaky_emit(event, seam_input=None):
        if event.result == "failed":
            corr = seam_input.correlation_id if seam_input is not None else f"{event.customer_id}::{event.period_index}"
            acct = seam_input.account_id if seam_input is not None else f"ACC-{event.customer_id}"
            due = date.fromisoformat(event.due_date)
            payload = BacsArruddOutcome(
                mandate_ref=f"MANDATE-{acct}",
                account_id=acct,
                amount_gbp=event.amount_gbp,
                outcome=DDOutcomeStatus.FAILURE,
                reason_category=BacsReasonCategory.INSUFFICIENT_FUNDS,
                reason_text="Refer to Payer",
                value_date=due,
            )
            import datetime as _dt
            return [WallResponse(
                correlation_id=corr,
                status=WallStatus.OK,
                schema_version=SCHEMA_VERSION,
                observed_at=_dt.datetime.combine(due, _dt.time(6, 0)),
                valid_time=due,
                payload=payload,
            )]
        # non-failed: fall through to the real adapter for coherent success/dispute
        return _real_emit(event, seam_input)

    _real_emit = lpt.emit_wall_responses
    monkeypatch.setattr(lpt, "emit_wall_responses", _leaky_emit)

    neutered = _build_triad().measure()
    assert neutered is not None
    neutered_gap = neutered["detection"].gap

    # The wall leaked -> the company now flags every true failure -> the
    # detection gap collapses to 0. The measurement demonstrably FIRED.
    assert neutered_gap == 0.0, neutered_gap
    assert neutered_gap < baseline_gap
    assert neutered["stats"]["n_flagged_non_dd_failures"] > 0, (
        "the mutation should have made the (formerly blind) non-DD failures visible"
    )


def test_deterministic_same_population_same_gap():
    r1 = _build_triad().measure()
    r2 = _build_triad().measure()
    for name in ("detection", "belief", "ageing"):
        assert r1[name].gap == r2[name].gap, name
        assert r1[name].raw_gap == r2[name].raw_gap, name
    assert r1["stats"] == r2["stats"]


def test_measure_returns_none_when_no_failures():
    """A defensible empty-failure population must be guarded, never crash the
    run (detection_gap raises on an empty truth set)."""
    triad = LivePaymentTriad()
    # A single on-time low-stress period is overwhelmingly unlikely to fail; but
    # to be deterministic, assert the guard path directly with an empty record set.
    assert triad.measure() is None


def test_single_truth_derivation_maps_all_result_classes():
    due = date(2021, 3, 28)
    failed = PaymentEvent(
        customer_id="C1", period_index=1, due_date=due.isoformat(), amount_gbp=100.0,
        payment_method="direct_debit", result="failed", days_late=0,
        payment_date=None, dd_failure_reason="insufficient_funds",
    )
    on_time = PaymentEvent(
        customer_id="C1", period_index=2, due_date=due.isoformat(), amount_gbp=100.0,
        payment_method="direct_debit", result="success", days_late=0,
        payment_date=due.isoformat(), dd_failure_reason=None,
    )
    late = PaymentEvent(
        customer_id="C1", period_index=3, due_date=due.isoformat(), amount_gbp=100.0,
        payment_method="direct_debit", result="success", days_late=9,
        payment_date=(date(2021, 4, 6)).isoformat(), dd_failure_reason=None,
    )
    dispute = PaymentEvent(
        customer_id="IC1", period_index=4, due_date=due.isoformat(), amount_gbp=9000.0,
        payment_method="direct_debit", result="dispute", days_late=0,
        payment_date=None, dd_failure_reason=None,
    )

    assert _derive_analytics_record("C1", due, 100.0, failed)["result"] == "DD_FAILED"
    assert _derive_analytics_record("C1", due, 100.0, on_time)["result"] == "ON_TIME"
    r_late = _derive_analytics_record("C1", due, 100.0, late)
    assert r_late["result"] == "LATE"
    assert r_late["days_late"] == 9
    # dispute (I&C bacs contested collection) maps to DD_FAILED (documented
    # simplification -- legacy analytics vocabulary has no 'dispute').
    assert _derive_analytics_record("IC1", due, 9000.0, dispute)["result"] == "DD_FAILED"
