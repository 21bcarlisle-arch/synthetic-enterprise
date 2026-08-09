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
    # The blind-spot witness: genuine non-DD failures MUST exist, and none may
    # ever reach belief via the DD-FAILURE-EVENT channel (a non-zero count there
    # is a wall leak). Expected-collection reconciliation (ruling 2026-07-25 §2)
    # now legitimately detects some non-DD misses from own bills vs own cash --
    # so flagged can EXCEED true (the reconciliation path also picks up
    # mis-allocated/late-boundary invoices). The honest invariant is the RESIDUAL
    # detection gap staying strictly positive (asserted above), never that belief
    # undercounts truth.
    assert stats["n_true_non_dd_failures"] > 0, "population didn't exercise the blind spot"
    assert stats["n_flagged_non_dd_failures"] == 0
    assert stats["n_flagged_via_reconciliation"] > 0
    assert stats["n_flagged_failures"] > 0


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

    # The mutation reached the company: non-DD failures, which the adapter
    # structurally emits nothing for, are now visible on the DD-event channel.
    assert neutered["stats"]["n_flagged_non_dd_failures"] > 0, (
        "the mutation should have made the (formerly blind) non-DD failures visible"
    )

    # WHICH DIMENSION THE WALL ACTUALLY MOVES (rewritten 2026-08-09, atom D11).
    # Until D11 this test asserted the DETECTION headline collapsed to 0. It did
    # -- but for the wrong reason, and the reason is the defect D11 fixed: the
    # headline scored a belief held AT `as_of`, so leaking the wall was papering
    # over cases reconciliation had detected on time and then UN-flagged when a
    # later ambiguous payment was allocated oldest-first (Clayton's Case). With
    # an EVER-FLAGGED population those cases are already counted as detected, so
    # the headline is insensitive to this channel -- which is exactly what D10
    # measured directly (`n_flagged_via_dd_channel_only == 0`) and what the
    # `detection_latency` dimension exists to express instead.
    #
    # The dimension the DD-observation channel really feeds is BELIEF: the
    # company's arrears severity is counted from rail-observed failures, so
    # leaking every failure onto that channel must collapse the belief gap.
    assert neutered["belief"].gap < baseline["belief"].gap, (
        "leaking the wall left the BELIEF gap where it was -- that dimension is "
        "built on the DD-observed failure count, so this mutation must move it"
    )
    assert baseline["belief"].gap > 0.0, "vacuous: the belief gap was already 0"

    assert neutered["detection"].gap == baseline["detection"].gap, (
        "the detection headline moved under a pure DD-channel mutation -- either "
        "the ever-flagged population regressed to a belief held at `as_of`, or "
        "D10's measured 'this headline is reconciliation-determined' no longer "
        "holds and must be re-derived"
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


# ---------------------------------------------------------------------------
# `measure_and_write` -- the path that actually PUBLISHES. Until 2026-08-09 no
# test in this file reached it, so every word of the note it stamps into
# `coupled_gap_ledger.json` (which the Proof door reads) was unexercised: a
# KeyError or a rotted sentence there would have surfaced only in a live
# run_phase2b. Found by the H27 Expert-Hour pass; closed here.
# ---------------------------------------------------------------------------

def test_measure_and_write_renders_its_published_note_with_both_directions(tmp_path):
    """The live note is a PUBLISHED surface -- the Proof door reads it. It must
    RENDER (not merely exist in source) and must carry both error directions
    with their own denominators, interpolated from the measurement rather than
    typed into a sentence once.

    REPLACED, not repaired (2026-08-09, atom D11). Until this tick it asserted
    the note carried the two Expert-Hour LIMITS as caveats. Those limits are now
    fixed at the measure, so a note still advertising them would be describing a
    metric this module no longer computes."""
    triad = _build_triad()
    ledger = tmp_path / "coupled_gap_ledger.json"
    result = triad.measure_and_write(run_git_commit="0" * 40, ledger_path=ledger)
    assert result is not None

    note = result["detection"].note
    for phrase in ("EVER-FLAGGED", "BALANCED error", "D11",
                   "missed_failure_rate", "false_flag_rate",
                   "NOT COMPARABLE WITH ANY LEDGER ENTRY WRITTEN BEFORE"):
        assert phrase in note, f"published note lost: {phrase}"
    # The two limits must appear only in the PAST tense, as what was fixed. The
    # exact present-tense bullets the pre-D11 note carried are the falsifier: if
    # either comes back, a caveat has outlived its defect.
    for stale in ("(1) as_of ARTEFACT:", "(2) RECALL ONLY:"):
        assert stale not in note, (
            f"the note still advertises {stale!r} as a LIVE limit -- D11 closed "
            "it at the measure, so this is a caveat outliving its defect"
        )
    assert "It was an as_of ARTEFACT" in note, (
        "the note stopped saying what was wrong before -- a reader comparing "
        "against a pre-D11 ledger entry has no way to understand the jump"
    )

    # The witnesses are INTERPOLATED from the components, so they must agree
    # with what was actually measured.
    comp = result["detection"].components
    assert f"{comp['n_false_flags']} of {comp['n_negatives']}" in note
    assert comp["n_false_flags"] > 0, (
        "no false flags on this population -- the witness is vacuous here, so "
        "this test would pass without proving the sentence is true"
    )
    assert ledger.exists(), "the ledger entry the Proof door reads was not written"


def test_live_over_flagging_decomposes_and_is_not_all_wrongful():
    """The excess of flags over true failures is REAL, and it is not all error.

    This file once noted that 'flagged can EXCEED true' and declined to assert
    on it. D11's first draft then over-corrected and charged the WHOLE excess to
    wrongful dunning, which inflated the measured false-flag rate 30x: an
    invoice paid three weeks late genuinely WAS unpaid past its grace date, so
    the company flagging it was right. The excess must decompose exactly, with
    each part landing where it belongs."""
    result = _build_triad().measure()
    comp = result["detection"].components

    excess = comp["flagged_size"] - comp["caught"]
    assert excess > 0, "the population no longer over-flags -- re-derive this"

    # Every flag is on a true failure, a never-flaggable case (WRONG), or an
    # excluded one (legitimately flaggable but eventually paid). No fourth kind.
    assert comp["n_false_flags"] > 0, "no wrongful flags at all -- vacuous"
    assert comp["n_false_flags"] < excess, (
        "the whole excess is being charged as wrongful dunning -- that is the "
        "denominator error D11's first draft made; late-past-grace payments were "
        "genuinely unpaid past grace and flagging them was correct"
    )
    assert comp["n_excluded"] > 0 and comp["exclusion_reason"], (
        "cases in neither direction's population must be counted AND explained "
        "-- an unexplained exclusion silently shrinks a denominator"
    )
    assert (comp["truth_size"] + comp["n_negatives"] + comp["n_excluded"]
            == comp["universe_size"]), "the three populations must partition the universe"
    assert 0.0 < result["stats"]["false_flag_rate_over_truly_current"] < 1.0
