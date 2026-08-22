"""Coupled-triad tests for the W2_11 <-> D5 pair (payment belief-vs-truth,
atom H27_payment_belief_gap).

These test the GAP MEASUREMENT, not the company inference in isolation. The
central R15 concern: the gap must be a real, mutation-sensitive measurement --
it hits exactly the no-skill baseline (gap == 1) when the belief is totally
blind and exactly 0 when the belief matches truth, so a mid-range reading is a
real measurement, never a value the metric is stuck at.
"""

from __future__ import annotations

import ast
import contextlib
import inspect
import copy
import dataclasses
import shutil
import subprocess
import json
import textwrap
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

import tools.couple_w2_11_d5 as pair
from tools.couple_w2_11_d5 import BILL_AMOUNT_GBP, DD_FAILURE_WINDOW_DAYS

from background.gap_metric import (
    GapResult,
    ageing_gap,
    belief_gap,
    belief_measures,
    detection_gap,
    detection_measures,
    format_belief_summary,
    format_detection_summary,
    misapplication_gap,
    write_gap_entry,
)
from company.billing import arrears_engine, payment_observation_consumer
from company.billing.account_ledger import LedgerEvent
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from interface.contracts.wall_envelope import WallResponse
from simulation.payment_behaviour_source import PaymentEvent

# Small-but-real population: enough for both DD and non-DD failures to occur
# reliably (see test_non_dd_failures_occur_and_are_never_flagged) while
# keeping the suite fast.
_N = 900
_SEED = 101


def _ever_flagged(records, consumer, as_of, dd_channel_only: bool = False):
    """The company's EVER-FLAGGED set, taken from the scorer's OWN sweep rather
    than re-derived here (R15 independence, the other way round from usual): a
    second implementation of the ever-flagged loop in this file would let a
    mutation test assert one copy against another and pass while the real
    scorer was broken. `dd_channel_only` is the MUTATION -- the reconciliation
    channel deleted, leaving the rail-event channel alone."""
    sets = pair.score_triad(records, consumer, as_of)["sets"]
    if dd_channel_only:
        return set(sets["flagged_via_dd_channel"])
    return set(sets["flagged"])


# ---------------------------------------------------------------------------
# Wall: the company side of this pair reads no SIM internals (module-level,
# mirrors the AST check every other coupled-triad test file runs).
# ---------------------------------------------------------------------------

def test_company_twin_respects_wall():
    import company.billing.payment_observation_consumer as consumer_mod
    tree = ast.parse(inspect.getsource(consumer_mod))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert not a.name.startswith(("simulation", "sim")), a.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith(("simulation", "sim")), node.module


def test_consumer_never_receives_theta(monkeypatch):
    """R15 independence: every call this harness makes into
    `PaymentObservationConsumer.observe` carries a `WallResponse`, never a
    `PaymentEvent` or any of its truth-only fields (stress, dd_failure_reason,
    segment, pattern). Proves OUR usage, on top of the consumer module's own
    AST-based import-freedom test above."""
    seen = []
    original = PaymentObservationConsumer.observe

    def spy(self, response):
        seen.append(response)
        assert isinstance(response, WallResponse), type(response)
        assert not isinstance(response, PaymentEvent)
        assert not hasattr(response, "stress")
        assert not hasattr(response, "dd_failure_reason")
        assert not hasattr(response, "segment")
        payload = response.payload
        if payload is not None:
            assert not isinstance(payload, PaymentEvent)
            assert not hasattr(payload, "stress")
            assert not hasattr(payload, "segment")
        return original(self, response)

    monkeypatch.setattr(PaymentObservationConsumer, "observe", spy)
    records, consumer, ledger_book, as_of = pair.build_scenario(300, seed=11)
    assert len(seen) > 0
    assert len(records) == 300 * pair.N_PERIODS


# ---------------------------------------------------------------------------
# Non-triviality: DETECTION and BELIEF gaps must be > 0 (R12/R13 -- a ~0 gap
# here would be a leak, never a success).
# ---------------------------------------------------------------------------

def test_detection_and_belief_gaps_non_trivial():
    result = pair.measure(_N, seed=_SEED)
    det, bel, age = result["detection"], result["belief"], result["ageing"]

    assert det.gap is not None and det.gap > 0.0, det
    assert bel.gap is not None and bel.gap > 0.0, bel
    # ageing is reported honestly whatever it reads (see module note); it
    # must still be a well-formed gap, not degenerate/None.
    assert age.gap is not None

    stats = result["stats"]
    assert stats["n_true_failures"] > 0
    assert stats["n_flagged_failures"] > 0
    # Detection is now TWO paths (DD-failure events + expected-collection
    # reconciliation, ruling 2026-07-25 §2), so flagged can EXCEED true (the
    # reconciliation path also picks up mis-allocated/late-boundary invoices as
    # false positives). The honest invariant is the RESIDUAL gap: it must stay
    # strictly positive (R12 -- latency/mis-allocation never reach zero).
    assert 0.0 < det.gap < 1.0, det


def test_dd_channel_never_leaks_non_dd_but_reconciliation_detects_it():
    """Witness split (ruling 2026-07-25 §2, R15 both-ways). This population MUST
    contain genuine non-DD failures (or neither path is exercised). The
    DD-FAILURE-EVENT channel must NEVER carry one (the adapter emits nothing for
    a missed push payment -> a non-zero count there is a wall leak). The NEW
    expected-collection reconciliation path MUST detect some of them (own bills
    vs own cash, no rail event) -- that is the carve-out working, not a leak."""
    result = pair.measure(_N, seed=_SEED)
    stats = result["stats"]
    assert stats["n_true_non_dd_failures"] > 0, "population shape didn't exercise the blind spot"
    # VACUITY GUARD (2026-08-08 HARDEN, R15 fail-silent). The leak witness below
    # is an `== 0` assertion, which a DEAD DD channel satisfies just as happily
    # as a clean one. Without this line the whole test passes while the organ it
    # claims to watch observes nothing at all -- proven by
    # test_leak_witness_is_vacuous_without_its_channel_guard.
    assert stats["n_flagged_via_dd_channel"] > 0, "DD-failure channel observed nothing -- leak witness would be vacuous"
    # LEAK witness: a non-DD case reaching belief via the DD-failure channel.
    assert stats["n_flagged_non_dd_failures"] == 0
    # CARVE-OUT witness: reconciliation legitimately detects non-DD misses.
    assert stats["n_flagged_non_dd_via_reconciliation"] > 0


# ---------------------------------------------------------------------------
# 2026-08-08 HARDEN (R15 fail-silent). Three controls in this module were
# satisfiable while the thing they watch was dead or disconnected. Each is
# proven below to FIRE on its own named defect, per R15 -- a control that
# cannot fail is worse than none.
# ---------------------------------------------------------------------------

def _dd_channel_dead(monkeypatch):
    """Named defect #1: the DD-failure observation channel goes completely dark
    (a renamed field, a mis-set recency window, a broken adapter emit). The
    company observes NO rail failures at all."""
    original = PaymentObservationConsumer.snapshot

    def blind(self, *args, **kwargs):
        snap = original(self, *args, **kwargs)
        try:
            snap.recent_dd_failures = []
        except Exception:  # frozen dataclass
            snap = dataclasses.replace(snap, recent_dd_failures=[])
        return snap

    monkeypatch.setattr(PaymentObservationConsumer, "snapshot", blind)


def test_leak_witness_is_vacuous_without_its_channel_guard(monkeypatch):
    """The `n_flagged_non_dd_failures == 0` leak witness passes just as happily
    when the DD channel observes NOTHING as when it observes cleanly. Proves the
    vacuity guard added to test_dd_channel_never_leaks_non_dd_but_reconciliation
    _detects_it is load-bearing, not decoration."""
    _dd_channel_dead(monkeypatch)
    stats = pair.measure(_N, seed=_SEED)["stats"]

    # The bare leak witness is still perfectly happy -- that is the defect.
    assert stats["n_flagged_non_dd_failures"] == 0
    assert stats["n_true_non_dd_failures"] > 0
    assert stats["n_flagged_non_dd_via_reconciliation"] > 0
    # ...and ONLY the vacuity guard catches it.
    assert stats["n_flagged_via_dd_channel"] == 0, (
        "mutation did not actually kill the DD channel"
    )


def test_dd_channel_contributes_no_unique_detections_and_headline_is_insensitive(monkeypatch):
    """CHARACTERIZATION of a measured limit, not an aspiration (R12: reported,
    never tuned). `flagged_set` is a UNION, so the headline DETECTION gap only
    moves for detections a channel makes UNIQUELY. Today the DD channel makes
    none: every rail failure is also a cash shortfall reconciliation sees. The
    consequence -- deleting the entire DD channel leaves the published gap
    bit-identical -- is asserted here so that if the channel ever does start
    contributing, this test fires and the module's `channel_contribution` note
    must be re-derived rather than silently rotting."""
    baseline = pair.measure(_N, seed=_SEED)
    assert baseline["stats"]["n_flagged_via_dd_channel"] > 0
    assert baseline["stats"]["n_flagged_via_dd_channel_only"] == 0
    assert baseline["stats"]["n_flagged_via_reconciliation_only"] > 0

    _dd_channel_dead(monkeypatch)
    without = pair.measure(_N, seed=_SEED)

    assert without["detection"].gap == baseline["detection"].gap, (
        "the DD channel now moves the headline gap -- update the module's "
        "channel_contribution note; it no longer describes the measurement"
    )

    # D10, the closure: the SAME deletion that leaves the set-membership
    # headline bit-identical MUST move the latency dimension. This is the pair
    # of assertions the atom exists for -- one alone is half the finding.
    assert without["detection_latency"].gap > baseline["detection_latency"].gap, (
        "killing the DD-observation channel did not make the company learn "
        "LATER -- the detection_latency dimension is not measuring the channel "
        "it claims to measure"
    )
    assert baseline["detection_latency"].components["dd_channel_days_earlier"] > 0
    assert without["detection_latency"].components["dd_channel_days_earlier"] == 0.0, (
        "the counterfactual is not a counterfactual: with the channel already "
        "dead, deleting it again must buy exactly nothing"
    )


# ---------------------------------------------------------------------------
# DETECTION LATENCY (atom D10_detection_headline_is_single_channel).
# ---------------------------------------------------------------------------

def test_detection_latency_is_the_real_thing_and_not_an_as_of_artefact():
    """The RETIRED `detection_latency_days` key was days-overdue at whatever
    `as_of` the scorer happened to ask at -- on this scenario's fixed period
    grid it read exactly {30, 51, 72} days, a pure artefact carrying no
    information about WHEN the company first knew. Mutate `as_of` and assert
    the two behave oppositely: the retired quantity marches with the clock, the
    latency dimension does not move at all."""
    import datetime as _dt

    records, consumer, _ledger, as_of = pair.build_scenario(400, seed=_SEED)
    early = pair.score_triad(records, consumer, as_of)
    later = pair.score_triad(records, consumer, as_of + _dt.timedelta(days=30))

    # The retired quantity IS the artefact -- it moves one-for-one with as_of.
    assert (later["stats"]["reconciliation_days_overdue_at_as_of"]["median_days"]
            - early["stats"]["reconciliation_days_overdue_at_as_of"]["median_days"]) == 30

    # The real latency is a property of the OBSERVATION, not of the question's
    # timing, so it does not move.
    assert later["detection_latency"].gap == early["detection_latency"].gap
    assert (later["detection_latency"].components["dd_channel_days_earlier"]
            == early["detection_latency"].components["dd_channel_days_earlier"])
    assert "detection_latency_days" not in early["stats"], (
        "the retired key is back -- it never measured a latency"
    )


def test_detection_latency_reads_the_bank_feed_report_date_not_the_value_date():
    """The 2026-08-08 residual claimed DD latency was unmeasurable here because
    the adapter emits `value_date == due_date`. That was the wrong field:
    `DDFailureObservation.observed_at` is the bank-feed REPORT date and the seam
    already lags it 0..ARUDD_NOTIFICATION_LAG_DAYS. Pin the correction --
    measured DD lags must be a REAL spread inside that window, not a flat zero
    (a flat zero would mean the scorer went back to reading `value_date`)."""
    from simulation.bacs_rails import ARUDD_NOTIFICATION_LAG_DAYS

    result = pair.measure(_N, seed=_SEED)
    c = result["detection_latency"].components

    # With the DD channel present the mean sits strictly below the
    # reconciliation grace it replaces.
    assert 0 < c["mean_lag_days"] < c["mean_lag_days_without_dd_channel"]
    assert c["n_earliest_via_dd_channel"] > 0

    # The DD channel's OWN lag must be a real spread inside the ARUDD window.
    # `value_date` == the collection date, so a scorer reading it would show a
    # DEGENERATE all-zero distribution -- this is the assertion that catches
    # the misread, and `max == 0` is precisely what the 2026-08-08 residual
    # believed was the only thing available.
    assert c["dd_lag_days_min"] == 0
    assert c["dd_lag_days_max"] == ARUDD_NOTIFICATION_LAG_DAYS, (
        "the DD lag distribution is degenerate or outside the ARUDD window -- "
        "the scorer is reading `value_date`, not the bank-feed report date"
    )
    assert 0 < c["dd_lag_days_mean"] < ARUDD_NOTIFICATION_LAG_DAYS


def test_detection_latency_coverage_witnesses_ride_beside_the_mean(monkeypatch):
    """FAIL-OPEN guard (R15): a mean over the DETECTED population improves as
    detection gets worse if the undetected are silently dropped. They are
    counted, never imputed -- and the counts must add up to the truth."""
    result = pair.measure(_N, seed=_SEED)
    c = result["detection_latency"].components
    assert (c["n_latency_population"] + c["n_undetected"]
            + c["n_detected_dd_channel_only"]) == c["n_true_failures"]
    assert c["n_recon_detected_undated"] == 0
    assert c["n_dd_observed_after_as_of"] == 0

    # `n_undetected` reads 0 on this population (see the characterization test
    # below), so on its own it is a witness that has never been seen to fire --
    # exactly the vacuity R15 calls a failed control. Kill BOTH channels and it
    # must account for the whole truth, or it is not counting anything.
    _dd_channel_dead(monkeypatch)
    monkeypatch.setattr(
        PaymentObservationConsumer, "expected_collection_misses",
        lambda self, *a, **k: [],
    )
    blind = pair.measure(_N, seed=_SEED)["detection_latency"]
    assert blind.gap is None
    assert blind.components["n_undetected"] == blind.components["n_true_failures"] > 0
    assert blind.components["n_latency_population"] == 0


def test_detection_residual_is_misallocation_not_a_never_observed_blind_spot():
    """CHARACTERIZATION of a measured finding (D10), not an aspiration. The
    detection residual was published as 'failures the company never observes --
    the no-remittance blind spot'. Asking the company's OWN reconciliation organ
    at each invoice's due+grace shows otherwise: nothing goes unobserved. The
    misses the headline counts are detections the company later UN-made, when a
    later ambiguous non-DD payment was allocated oldest-first onto the failed
    invoice (Clayton's Case, atom D8).

    If `n_undetected` ever becomes non-zero this fires, and the module's
    `detection_residual_is_misallocation_not_blindness` note -- and the live
    ledger note that repeats it -- must be re-derived rather than rot."""
    result = pair.measure(_N, seed=_SEED)
    c = result["detection_latency"].components

    assert result["detection"].gap > 0, "no residual to characterise"
    assert c["n_undetected"] == 0, (
        "some true failure now escapes BOTH channels entirely -- the detection "
        "residual is no longer purely misallocation; re-derive the module's "
        "detection_residual_is_misallocation_not_blindness note"
    )
    # The two statements are about the same population, so they must reconcile:
    # everything truly failed was dated by a channel.
    assert c["n_latency_population"] == c["n_true_failures"]
    for phrase in ("never observes", "Clayton"):
        assert phrase in result["notes"]["detection_residual_is_misallocation_not_blindness"]


# ---------------------------------------------------------------------------
# THE as_of CLASS CONTROL (atom D11, H27 Expert-Hour pass 2026-08-09)
#
# R10: the artefact class -- a published figure that moves for a reason having
# nothing to do with the company's skill -- had already been fixed TWICE by
# instance (D7's prevalence scalar, D10's retired `detection_latency_days` key)
# and each time the dimension next door kept it. So it is closed here at the
# CLASS: every dimension declares whether its TRUTH moves with `as_of`, and
# this control MEASURES the declaration by moving `as_of` for real.
#
# The invariant is DIFFERENTIAL on purpose. A blanket "no dimension may move
# with as_of" would fire on ageing, where moving is correct -- a false positive
# that jams the gate teaches everyone to skip the gate.
# ---------------------------------------------------------------------------

_CONTRACT_SWEEP_DAYS = 60


def _independent_truth_signatures(records, as_of):
    """The harness-held TRUTH each dimension is scored against, derived HERE
    from `records` alone (R15 independence -- reusing the module's own
    intermediate would make this a tautology that cannot fail)."""
    failed = [r for r in records if r.result == "failed"]
    belief_truth = tuple(sorted(
        (cid, sum(1 for r in failed if r.customer_id == cid))
        for cid in {r.customer_id for r in records}))
    return {
        "detection": frozenset((r.customer_id, r.period_index) for r in failed),
        "detection_latency": frozenset(
            (r.customer_id, r.period_index, r.due_date) for r in failed),
        "belief": belief_truth,
        # The SAME truth, because the two dimensions are two questions about one
        # set of per-case labels (atom D19). Sharing it here is deliberate: it
        # means the sweep can only ever tell them apart by what the SCORERS do,
        # never by feeding them different facts.
        "belief_population_mix": belief_truth,
        "ageing": tuple(sorted(
            (r.invoice_ref,
             # Through the ownership register (atom D21), which is what the
             # scorer resolves too -- so a truth side quietly re-pointed at the
             # company organ moves this signature with it rather than leaving
             # the sweep comparing against a stale independent copy.
             pair.truth_side_rule("ageing")((as_of - r.due_date).days)
             if r.result == "failed" else "current")
            for r in records)),
    }


def _as_of_contract_report(records, consumer, as_of, contract, score=None):
    """Run the sweep and return, per dimension, what was MEASURED against what
    was DECLARED. Pure measurement -- the judging lives in the callers so the
    mutants can drive the same code."""
    import datetime as _dt

    score = score or pair.score_triad
    later = as_of + _dt.timedelta(days=_CONTRACT_SWEEP_DAYS)
    early_res, later_res = score(records, consumer, as_of), score(records, consumer, later)
    early_truth = _independent_truth_signatures(records, as_of)
    later_truth = _independent_truth_signatures(records, later)

    report = {}
    for dim, declared in contract.items():
        a, b = early_res[dim].gap, later_res[dim].gap
        gap_moved = ((a is None) != (b is None)) or (
            a is not None and abs(a - b) > 1e-9)
        report[dim] = {
            "truth_moved": early_truth[dim] != later_truth[dim],
            "gap_moved": gap_moved,
            "declared_truth_invariant": bool(declared["truth_is_as_of_invariant"]),
            "declared_gap_invariant": bool(declared["gap_is_as_of_invariant"]),
            "early": a, "later": b,
        }
    return report


def test_every_dimension_declares_its_as_of_contract_and_the_declaration_is_measured():
    """THE CLASS CONTROL. Hold the company and the world literally fixed --
    same `records`, same `consumer`, nothing re-simulated -- and move only the
    date the scorer asks on. Every dimension's DECLARED as_of behaviour must
    match what actually happens, and the invariant must hold:

        truth invariant under as_of  =>  gap invariant under as_of

    A dimension allowed to break it must say so in its own declaration AND name
    the atom that fixes it, so the exemption is a dated debt rather than a
    silent one."""
    records, consumer, _ledger, as_of = pair.build_scenario(250, seed=_SEED)
    contract = pair.DIMENSION_AS_OF_CONTRACT
    report = _as_of_contract_report(records, consumer, as_of, contract)

    assert set(contract) == {"detection", "detection_latency", "belief",
                             "belief_population_mix", "ageing"}, (
        "a dimension was added or renamed without an as_of declaration -- the "
        "whole point of this control is that no published number escapes it"
    )

    # VACUITY GUARD. A sweep in which nothing moved at all would pass every
    # assertion below while proving nothing (the population might carry no
    # failures, or `_CONTRACT_SWEEP_DAYS` might land inside a dead window).
    # Both sides of the differential must be genuinely exercised.
    assert any(v["truth_moved"] for v in report.values()), (
        "no dimension's truth moved over the sweep -- the differential half of "
        "this control was not exercised, so a pass here is vacuous"
    )
    assert any(not v["truth_moved"] for v in report.values())
    assert any(v["gap_moved"] for v in report.values()), (
        "not one published gap moved -- the sweep did nothing"
    )

    for dim, m in report.items():
        assert m["truth_moved"] == (not m["declared_truth_invariant"]), (
            f"{dim}: declared truth_is_as_of_invariant="
            f"{m['declared_truth_invariant']} but measurement says otherwise"
        )
        assert m["gap_moved"] == (not m["declared_gap_invariant"]), (
            f"{dim}: declared gap_is_as_of_invariant="
            f"{m['declared_gap_invariant']} but the gap went "
            f"{m['early']} -> {m['later']} over {_CONTRACT_SWEEP_DAYS} days"
        )
        if m["declared_truth_invariant"] and not m["declared_gap_invariant"]:
            # The exemption is allowed, but only as a NAMED, dated debt.
            why = str(contract[dim]["why"])
            assert "VIOLATES THE INVARIANT" in why, dim
            assert "D11" in why, (
                f"{dim} is exempt from the as_of invariant without naming the "
                f"atom that closes it -- an unblockable reason living only in "
                f"prose is how a hold outlives its cause"
            )


def test_the_as_of_class_control_fires_when_a_clean_dimension_starts_drifting():
    """R15 MUST-FIRE #1. `belief` is declared invariant on both sides and
    measures clean today. Poison ONLY its gap so it drifts with the clock while
    its truth stands still -- the exact defect class -- and the control must
    catch it. A control that only ever passes is not evidence."""
    import datetime as _dt

    records, consumer, _ledger, as_of = pair.build_scenario(250, seed=_SEED)

    def _poisoned_score(recs, cons, when, **kw):
        res = pair.score_triad(recs, cons, when, **kw)
        # Nothing about the world changed; only the question's timing.
        res["belief"].gap = res["belief"].gap + 0.001 * (when - as_of).days
        return res

    report = _as_of_contract_report(
        records, consumer, as_of, pair.DIMENSION_AS_OF_CONTRACT, score=_poisoned_score)

    assert report["belief"]["gap_moved"] is True
    assert report["belief"]["truth_moved"] is False
    # ...and that combination is precisely what the real test forbids.
    with pytest.raises(AssertionError):
        m = report["belief"]
        assert m["gap_moved"] == (not m["declared_gap_invariant"])


def test_the_as_of_class_control_fires_on_a_declaration_that_lies():
    """R15 MUST-FIRE #2, aimed at the DECLARATION rather than the measurement,
    and it must be falsifiable in BOTH directions.

    Before D11 only one direction was tested: `detection` really did drift, so
    the only lie the control could catch was "it is clean". Now that every
    truth-invariant dimension is also gap-invariant, the remaining lie is the
    opposite one -- claiming a clean dimension is dirty, which would quietly buy
    a permanent exemption for a dimension that does not need one. Both lies must
    fail the control, or the declaration is unfalsifiable one way round."""
    records, consumer, _ledger, as_of = pair.build_scenario(250, seed=_SEED)
    real = _as_of_contract_report(
        records, consumer, as_of, pair.DIMENSION_AS_OF_CONTRACT)

    # LIE A -- claim a genuinely-drifting dimension is clean. `ageing` really
    # does move with the clock (an invoice ages), which is why it is exempt.
    assert real["ageing"]["gap_moved"] is True, "ageing stopped moving -- re-derive"
    lying_clean = {k: dict(v) for k, v in pair.DIMENSION_AS_OF_CONTRACT.items()}
    lying_clean["ageing"]["gap_is_as_of_invariant"] = True
    m = _as_of_contract_report(records, consumer, as_of, lying_clean)["ageing"]
    with pytest.raises(AssertionError):
        assert m["gap_moved"] == (not m["declared_gap_invariant"])

    # LIE B -- claim a genuinely-clean dimension drifts, i.e. take an exemption
    # that is not needed. `detection` has been invariant since D11 landed.
    assert real["detection"]["gap_moved"] is False, (
        "the detection headline is drifting with as_of again -- D11 regressed"
    )
    lying_dirty = {k: dict(v) for k, v in pair.DIMENSION_AS_OF_CONTRACT.items()}
    lying_dirty["detection"]["gap_is_as_of_invariant"] = False
    m = _as_of_contract_report(records, consumer, as_of, lying_dirty)["detection"]
    with pytest.raises(AssertionError):
        assert m["gap_moved"] == (not m["declared_gap_invariant"])


def test_detection_headline_is_no_longer_an_as_of_artefact():
    """THE D11 ACCEPTANCE CRITERION, and it REPLACES the characterization that
    used to sit here (which asserted the drift, as the defect it then was).

    Hold the company and the world literally fixed -- same `records`, same
    `consumer`, nothing re-simulated -- and move only the date the scorer asks
    on. The old headline walked 0.0725 -> 0.1232 over 60 days. The reshaped one
    must not move at all, because its population is EVER-FLAGGED and a detection
    is a fact about the day it happened."""
    import datetime as _dt

    records, consumer, _ledger, as_of = pair.build_scenario(400, seed=7)
    swept = {
        d: pair.score_triad(records, consumer, as_of + _dt.timedelta(days=d))
        for d in (0, 7, 14, 30, 60, 90)
    }
    base = swept[0]["detection"]

    # VACUITY GUARD: a sweep over a population with nothing in it would pass
    # every assertion below while proving nothing.
    assert base.components["truth_size"] > 0
    assert base.components["n_negatives"] > 0
    assert base.gap is not None

    for d, res in swept.items():
        det = res["detection"]
        assert det.components["truth_size"] == base.components["truth_size"], d
        assert det.gap == base.gap, (
            f"the detection headline moved to {det.gap} at as_of+{d} while the "
            f"company and the world stood still -- D11 regressed"
        )
        assert det.components["false_flag_rate"] == base.components["false_flag_rate"], d
        assert det.components["missed_failure_rate"] == base.components["missed_failure_rate"], d

    # The dimension D10 built on an EVER-KNEW population is invariant too -- the
    # headline has now joined it rather than being the odd one out.
    assert swept[90]["detection_latency"].gap == swept[0]["detection_latency"].gap
    # ...and the sweep is not a no-op: `ageing`, whose truth genuinely moves,
    # still moves. Otherwise the flatness above would prove only that nothing
    # in this scorer responds to `as_of` at all.
    assert swept[90]["ageing"].gap != swept[0]["ageing"].gap, (
        "not one dimension moved over the sweep -- the sweep did nothing, so the "
        "invariance asserted above is vacuous"
    )


def test_flag_everything_no_longer_buys_a_perfect_detection_score():
    """R15 MUST-FIRE, and the second half of what D11 was for. The retired
    headline gave a company that flagged EVERY invoice a perfect 0.0. The
    reshaped one must give both degenerate strategies exactly the no-skill
    baseline, and must score the real company strictly better than both -- or
    the reshape bought nothing."""
    records, consumer, _ledger, as_of = pair.build_scenario(400, seed=7)
    truth = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    universe = {(r.customer_id, r.period_index) for r in records}
    negatives = {
        (r.customer_id, r.period_index) for r in records
        if r.result == "success" and r.days_late is not None and r.days_late <= 5
    }
    assert truth and negatives and len(truth) < len(universe), "vacuous population"
    kw = dict(universe=universe, negative_set=negatives,
              exclusion_reason="late-past-grace successes and disputes")

    everything = detection_measures(truth, universe, **kw)
    nobody = detection_measures(truth, set(), **kw)
    perfect = detection_measures(truth, truth, **kw)

    assert everything.gap == 0.5 == nobody.gap, (
        "a degenerate strategy is no longer scoring the no-skill baseline -- the "
        "balanced shape has been lost"
    )
    assert everything.g0 == 0.5
    assert perfect.gap == 0.0, "a perfect detector must still be able to score 0"

    # ...and the retired measure is the falsifier: on the SAME sets it hands the
    # indiscriminate company the perfect score that made D11 necessary.
    assert detection_gap(truth, universe).gap == 0.0

    # The real company sits strictly between the degenerates and perfection.
    real = pair.score_triad(records, consumer, as_of)["detection"]
    assert 0.0 < real.gap < 0.5, real.gap


def test_the_detection_headline_never_prints_alone():
    """R11-in-spirit: BOTH directions must reach the surface a human actually
    reads, not only the module docstring. The witnesses ride in `stats` and in
    the rendered summary the CLI and the live ledger note both use."""
    result = pair.measure(300, seed=_SEED)
    stats = result["stats"]
    det = result["detection"]

    assert stats["n_flagged_not_truly_failed"] is not None
    assert stats["false_flag_rate_over_truly_current"] is not None
    assert stats["n_flagged_not_truly_failed"] > 0, (
        "no false flags on this population -- this witness is vacuous here"
    )
    for phrase in ("EVER-FLAGGED", "BALANCED error", "D11", "n_excluded"):
        assert phrase in det.note, phrase

    rendered = format_detection_summary(det)
    assert "missed_failure_rate" in rendered and "false_flag_rate" in rendered
    assert "wrongful-dunning exposure" in rendered
    assert f"{det.components['n_false_flags']} of {det.components['n_negatives']}" in rendered
    assert str(det.components["n_excluded"]) in rendered, (
        "the excluded population is not printed -- an unpublished exclusion is "
        "how a denominator gets quietly shrunk"
    )


def test_the_false_flag_denominator_excludes_legitimately_flagged_late_payers():
    """THE DENOMINATOR IS THE MEASURE. D11's own first draft used
    `universe - truth_set` as the negative population, which charged the company
    for flagging invoices that really were unpaid past grace and merely got paid
    later. On this population that inflated the false-flag rate 0.0269 -> 0.2834
    -- a tenfold error, entirely inside the denominator.

    A late-past-grace payment must therefore be in NEITHER population, and the
    exclusion must be counted and explained."""
    records, consumer, _ledger, as_of = pair.build_scenario(400, seed=7)
    det = pair.score_triad(records, consumer, as_of)["detection"]
    c = det.components

    late_past_grace = [
        r for r in records
        if r.result == "success" and r.days_late is not None and r.days_late > 5
    ]
    assert late_past_grace, (
        "no late-past-grace payments in this population -- the distinction this "
        "test exists to protect is not exercised, so a pass proves nothing"
    )
    assert c["n_excluded"] >= len(late_past_grace)
    assert c["exclusion_reason"] and "grace" in c["exclusion_reason"]
    assert c["truth_size"] + c["n_negatives"] + c["n_excluded"] == c["universe_size"]

    # THE MUTATION: put them back in the negative population (the draft's bug)
    # and the measured wrongful-dunning rate must jump. If it did not, the
    # distinction would be decorative.
    universe = {(r.customer_id, r.period_index) for r in records}
    truth = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    naive = detection_measures(truth, _ever_flagged(records, consumer, as_of),
                               universe=universe)
    assert naive.components["false_flag_rate"] > c["false_flag_rate"] * 5, (
        "collapsing the excluded population into the negatives no longer moves "
        "the score -- either the population changed or the exclusion is a no-op"
    )


def test_detection_measures_fails_loud_on_a_bad_population():
    """R15 FAIL-LOUD. Every way of handing this measure an incoherent population
    must RAISE, because each one silently moves a denominator: a flag outside
    the scored universe is a join-key drift, an overlap makes a case both
    must-flag and must-not-flag, and an unexplained exclusion is the cheapest
    possible way to make either direction look better than it is."""
    U = {1, 2, 3, 4}
    S = {1}
    N = {2, 3}
    reason = "case 4 was neither"

    with pytest.raises(ValueError, match="outside the scored universe"):
        detection_measures(S, {1, 99}, universe=U, negative_set=N, exclusion_reason=reason)
    with pytest.raises(ValueError, match="outside the scored universe"):
        detection_measures({1, 99}, {1}, universe=U, negative_set=N, exclusion_reason=reason)
    with pytest.raises(ValueError, match="in BOTH"):
        detection_measures(S, {1}, universe=U, negative_set={1, 2}, exclusion_reason=reason)
    with pytest.raises(ValueError, match="no `exclusion_reason`"):
        detection_measures(S, {1}, universe=U, negative_set=N)
    with pytest.raises(ValueError, match="empty truth set"):
        detection_measures(set(), {1}, universe=U, negative_set=N, exclusion_reason=reason)
    with pytest.raises(ValueError, match="empty universe"):
        detection_measures(S, {1}, universe=set())

    # VACUITY IS EXPLICIT, never a silent fallback to the recall number: with no
    # negative population the false-flag direction and the headline are None.
    vacuous = detection_measures(S, {1}, universe=U, negative_set=set(),
                                 exclusion_reason=reason)
    assert vacuous.components["false_flag_rate"] is None
    assert vacuous.gap is None
    assert "vacuity" in vacuous.components
    # ...and the miss direction is still measured, so the None above is a
    # statement about the denominator, not about the whole measurement failing.
    assert vacuous.components["missed_failure_rate"] == 0.0


def test_the_miss_direction_can_still_fire():
    """R15: a direction that is 0 on every population this repo scores is a
    control that cannot fail, and `missed_failure_rate` IS 0 here -- expected-
    collection reconciliation catches every truly-failed invoice at due+grace
    (D10 measured `n_undetected == 0` on seeds 7/11/23).

    So it is proven by MUTATION rather than by observation: delete the
    reconciliation channel, leaving the DD-event channel alone, and the non-DD
    blind spot must reappear as a non-zero miss rate."""
    records, consumer, _ledger, as_of = pair.build_scenario(400, seed=7)
    honest = pair.score_triad(records, consumer, as_of)["detection"]
    assert honest.components["missed_failure_rate"] == 0.0

    truth = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    universe = {(r.customer_id, r.period_index) for r in records}
    negatives = {
        (r.customer_id, r.period_index) for r in records
        if r.result == "success" and r.days_late is not None and r.days_late <= 5
    }
    dd_only = _ever_flagged(records, consumer, as_of, dd_channel_only=True)
    crippled = detection_measures(
        truth, dd_only, universe=universe, negative_set=negatives,
        exclusion_reason="late-past-grace successes and disputes")

    assert crippled.components["missed_failure_rate"] > 0.0, (
        "deleting the reconciliation channel left the miss direction at zero -- "
        "then it cannot fire at all and is not evidence of anything"
    )
    assert crippled.gap > honest.gap


def test_detection_latency_vacuity_is_none_never_zero():
    """A population nothing was detected in is not one that was detected
    instantly. Vacuity must be explicit (the D7 rule, applied here)."""
    empty = pair.detection_latency_gap({}, {}, n_true_failures=7)
    assert empty.gap is None
    assert empty.components["mean_lag_days"] is None
    assert empty.components["mean_lag_days_without_dd_channel"] is None
    assert empty.components["dd_channel_days_earlier"] is None
    assert empty.components["n_undetected"] == 7
    assert "vacuity" in empty.components
    rendered = pair.format_detection_latency_summary(empty)
    assert "UNDEFINED" in rendered and "not 0 days" in rendered


# --- R15 mutants of the metric SHAPE itself (the D7 trap, applied early) ----
# Each mutant must FAIL an assertion the real measure passes. The real measure
# is invariant to how many failures went undetected -- because the undetected
# are counted beside it, never inside it. Every mutant re-imports a denominator
# that counts the population's class balance, which is exactly the defect D7
# was minted to remove; if one of these ever passes, the shape has rotted back.

_CASES_DETECTED = {("c", 0): 5, ("c", 1): 5, ("c", 2): 5}
_DD = {("c", 0): 1, ("c", 1): 1, ("c", 2): 1}


def _real_mean(n_true_failures):
    return pair.detection_latency_gap(
        _DD, _CASES_DETECTED, n_true_failures=n_true_failures
    ).components["mean_lag_days"]


def _MUTANT_mean_over_all_true_failures(n_true_failures):
    """Divide by the TRUTH count instead of the detected count -- the D7 trap
    wearing a latency hat: prevalence of the undetected then moves a number
    that is supposed to be about timing."""
    lags = [min(_DD[c], _CASES_DETECTED[c]) for c in _CASES_DETECTED]
    return round(sum(lags) / n_true_failures, 6)


def _MUTANT_impute_undetected_at_a_cap(n_true_failures, cap=90):
    """Impute every undetected failure into the mean at an invented cap. Looks
    conservative; is a fabricated number, and lets the mean be moved by how many
    failures were MISSED rather than by how late the found ones were."""
    lags = [min(_DD[c], _CASES_DETECTED[c]) for c in _CASES_DETECTED]
    lags += [cap] * (n_true_failures - len(_CASES_DETECTED))
    return round(sum(lags) / len(lags), 6)


def test_latency_mean_is_invariant_to_how_many_failures_went_undetected():
    """Hold the DETECTED cases and their timings LITERALLY fixed and move only
    how many failures were missed. The real mean does not budge; both mutants
    swing. R12: this is a shape criterion, not a nicer number."""
    fixed = _real_mean(3)
    assert _real_mean(30) == fixed == 1.0
    assert _real_mean(300) == fixed

    assert _MUTANT_mean_over_all_true_failures(3) != _MUTANT_mean_over_all_true_failures(30), (
        "mutant did not exhibit the prevalence defect it was written to exhibit"
    )
    assert _MUTANT_impute_undetected_at_a_cap(3) != _MUTANT_impute_undetected_at_a_cap(30), (
        "mutant did not exhibit the imputation defect"
    )


def test_counterfactual_compares_the_same_population_not_a_bigger_one():
    """The headline and its DD-deleted counterfactual must differ ONLY in the
    channel. A case only the DD channel sees would vanish entirely in the
    counterfactual world, so it is excluded from BOTH means and reported --
    otherwise the 'days earlier' figure would silently mix a timing change with
    a population change."""
    dd_only_case = ("c", 9)
    result = pair.detection_latency_gap(
        {**_DD, dd_only_case: 0}, _CASES_DETECTED, n_true_failures=4
    )
    c = result.components
    assert c["n_detected_dd_channel_only"] == 1
    assert c["n_latency_population"] == 3
    # The dd-only case (lag 0) is NOT in the mean -- if it were, the headline
    # would read 0.75 rather than 1.0 and the counterfactual would be measuring
    # a different set of invoices.
    assert c["mean_lag_days"] == 1.0
    assert c["mean_lag_days_without_dd_channel"] == 5.0
    assert c["n_undetected"] == 0


def test_join_witnesses_fire_on_a_key_convention_drift():
    """Named defect #3: the belief-side observations are joined back to truth by
    KEY (`value_date` -> due date, `invoice_ref`/`reference` -> the harness's
    invoice_ref) and every join is a `.get()` whose miss silently DROPS the
    observation. A drift in either convention would push the measured gap toward
    the no-skill baseline with nothing firing. Mutate the truth-side keys and
    assert the witnesses -- not the gap -- are what notice."""
    records, consumer, _ledger, as_of = pair.build_scenario(400, seed=13)

    clean = pair.score_triad(records, consumer, as_of)["stats"]
    assert clean["n_unjoined_dd_failures"] == 0
    assert clean["n_unjoined_collection_misses"] == 0
    assert clean["n_ageing_refs_matched"] > 0

    import datetime as _dt

    for r in records:
        r.due_date = r.due_date + _dt.timedelta(days=1)   # value_date no longer lines up
        r.invoice_ref = r.invoice_ref + "::drifted"       # reference convention changed

    drifted = pair.score_triad(records, consumer, as_of)["stats"]
    assert drifted["n_unjoined_dd_failures"] > 0, "dd-failure join drift went unwitnessed"
    assert drifted["n_unjoined_collection_misses"] > 0, "collection-miss join drift went unwitnessed"
    assert drifted["n_ageing_refs_matched"] == 0, "ageing join drift went unwitnessed"


# ---------------------------------------------------------------------------
# Determinism (C-S2): same seed/population -> byte-identical gap results.
# ---------------------------------------------------------------------------

def test_deterministic():
    r1 = pair.measure(_N, seed=_SEED)
    r2 = pair.measure(_N, seed=_SEED)
    for name in ("detection", "belief", "ageing"):
        a, b = r1[name], r2[name]
        assert a.gap == b.gap, name
        assert a.raw_gap == b.raw_gap, name
        assert a.g0 == b.g0, name
        assert a.components == b.components, name
    assert r1["stats"] == r2["stats"]


def test_different_seed_changes_the_population():
    r1 = pair.measure(400, seed=1)
    r2 = pair.measure(400, seed=2)
    changed = (
        r1["stats"]["n_true_failures"] != r2["stats"]["n_true_failures"]
        or r1["detection"].gap != r2["detection"].gap
        or r1["belief"].gap != r2["belief"].gap
    )
    assert changed, "changing --seed had no observable effect on the drawn population"


# ---------------------------------------------------------------------------
# R15 mutation checks: the scorers this pairing uses must be able to FAIL
# (hit their own worst-case) as well as pass (hit 0), not sit at one number.
# ---------------------------------------------------------------------------

def test_detection_gap_hits_the_no_skill_baseline_when_belief_is_blind():
    records, _consumer, _ledger, _as_of = pair.build_scenario(_N, seed=_SEED)
    truth_set = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    blind = detection_gap(truth_set, set())
    assert blind.gap == 1.0

    result = pair.measure(_N, seed=_SEED)
    assert result["detection"].gap < blind.gap


def test_detection_gap_zero_on_perfect_flagging():
    records, _consumer, _ledger, _as_of = pair.build_scenario(400, seed=5)
    truth_set = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    perfect = detection_gap(truth_set, truth_set)
    assert perfect.gap == 0.0


# ---------------------------------------------------------------------------
# R15 both-ways for the expected-collection reconciliation carve-out (director
# ruling 2026-07-25 §2): the detector must FIRE (narrow the gap on the fix) and
# must be able to STILL MISS (never fail open to "all detected").
# ---------------------------------------------------------------------------

def test_reconciliation_fires_and_narrows_the_detection_gap():
    """MUST-FIRE half. With expected-collection reconciliation the company
    detects missed push payments it was structurally blind to before, so the
    detection gap is strictly SMALLER than a DD-failure-event-only belief scored
    over the same population. Independent of the metric (recall over the same
    truth set), so this is a real narrowing, not a re-labelled number."""
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    truth_set = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}

    by_customer: dict = {}
    for r in records:
        by_customer.setdefault(r.customer_id, []).append(r)

    dd_only: set = set()
    both: set = set()
    for cid, periods in by_customer.items():
        snap = consumer.snapshot(periods[0].account_id, as_of=as_of)
        due_to_period = {r.due_date: r.period_index for r in periods}
        ref_to_period = {r.invoice_ref: r.period_index for r in periods}
        for f in snap.recent_dd_failures:
            p = due_to_period.get(f.value_date)
            if p is not None:
                dd_only.add((cid, p)); both.add((cid, p))
        for m in snap.detected_collection_misses:
            p = ref_to_period.get(m.invoice_ref)
            if p is not None:
                both.add((cid, p))

    gap_dd_only = detection_gap(truth_set, dd_only).gap
    gap_both = detection_gap(truth_set, both).gap
    assert gap_both < gap_dd_only, (gap_both, gap_dd_only)
    # and it FIRED on genuine non-DD misses (not just DD ones it already saw)
    assert both - dd_only, "reconciliation added no new detections"


def test_reconciliation_cannot_fail_open():
    """MUST-STILL-MISS half. Because the detection metric is pure RECALL,
    flagging every ever-overdue invoice regardless of received cash would drive
    the gap to zero by flagging everyone -- the fail-open failure mode the ruling
    forbids. The honest detector reads the ledger's ACTUAL outstanding, so a
    payment that arrived LATE (cash by as_of) is NOT flagged. This test builds a
    paid-late invoice and proves: (a) the real detector does not flag it, while
    (b) a cash-blind mutant (flag any overdue invoice) WRONGLY does -- the
    mutation is caught by reading real cash."""
    import datetime as dt
    from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType

    lb = LedgerBook()
    consumer = PaymentObservationConsumer(ledger_book=lb)
    acc = "ACC-LATE"
    issue = dt.date(2024, 1, 1)
    # One invoice, billed then PAID LATE (cash arrives well after due, before as_of).
    lb.post(LedgerEvent(event_id="b", account_id=acc, event_type=LedgerEventType.BILL_DEBIT,
                        amount_gbp=120.0, valid_time=issue,
                        transaction_time=dt.datetime(2024, 1, 1), invoice_ref="INV"))
    lb.post(LedgerEvent(event_id="p", account_id=acc, event_type=LedgerEventType.PAYMENT_CREDIT,
                        amount_gbp=120.0, valid_time=dt.date(2024, 2, 10),
                        transaction_time=dt.datetime(2024, 2, 10), remittance=("INV",)))
    as_of = dt.date(2024, 3, 1)

    # (a) real detector: reads actual outstanding == 0 -> does NOT flag the paid invoice
    real = consumer.expected_collection_misses(acc, as_of=as_of)
    assert real == [], "fail-open: flagged an invoice whose cash was reconciled"

    # (b) cash-blind mutant: flag every BILLED invoice past due+grace, IGNORING
    # whether cash arrived (reads raw bill events, never the reconciled balance).
    mutant_flags = [
        e.invoice_ref for e in lb.ledger(acc).events()
        if e.event_type == LedgerEventType.BILL_DEBIT
        and (as_of - (e.valid_time + dt.timedelta(days=14))).days >= 5
    ]
    assert mutant_flags == ["INV"], "mutant did not exhibit the fail-open defect"
    # The real detector diverges from the mutant on exactly this case -> guarded.
    assert [m.invoice_ref for m in real] != mutant_flags


def test_detection_residual_lag_is_registered_not_zero():
    """Ruling §1: the residual is a lag, registered with its measured
    distribution, never compressed to zero.

    REPLACED, NOT REPAIRED (D10). This used to assert on
    `stats["detection_latency_days"]`, which was days-overdue at `as_of` and
    not a latency at all. The ruling's actual requirement -- the lag exists and
    is registered -- now rests on the `detection_latency` DIMENSION; the
    days-overdue summary is kept under a name that says what it is."""
    result = pair.measure(_N, seed=_SEED)

    lat = result["detection_latency"]
    assert lat.gap is not None and lat.gap > 0, "the lag was compressed to zero"
    assert lat.g0 == 0.0 and "NONE" in lat.baseline, (
        "a days-valued latency must carry no no-skill divisor (D7's lesson)"
    )
    assert lat.components["headline_units"].startswith("days")

    overdue = result["stats"]["reconciliation_days_overdue_at_as_of"]
    assert overdue["n"] > 0
    assert overdue["max_days"] >= overdue["median_days"] >= overdue["min_days"]


def test_belief_gap_zero_when_distributions_match():
    dist = [0.7, 0.2, 0.05, 0.05]
    result = belief_gap(dist, dist)
    assert result.gap == 0.0


def test_ageing_gap_zero_when_truth_equals_belief():
    labels = ["current"] * 90 + ["30-60"] * 10
    result = misapplication_gap(labels, labels)
    assert result.gap == 0.0


# ---------------------------------------------------------------------------
# Per-cell partition (SOURCE 2 of PLANNER_MINTED_payment_grid_coverage): the
# DETECTION dimension partitioned by a WORLD-side classifier lights each cell
# with its OWN measured gap, conserves the whole, and never double-counts a
# customer whose life spans two partitions.
# ---------------------------------------------------------------------------

def _regime_of_period(rec) -> str:
    """A synthetic WORLD-side regime classifier for the offline (single-year)
    scenario: even billing periods -> 'G1' (calm), odd -> 'G2' (crisis). Every
    customer has N_PERIODS periods, so each customer SPANS both partitions --
    exactly the spanning-customer case the belief-contamination residual is
    about."""
    return "G1" if rec.period_index % 2 == 0 else "G2"


def test_partition_lights_distinct_cells_and_conserves_the_whole():
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    per_cell = pair.score_detection_by_partition(
        records, consumer, as_of, _regime_of_period
    )
    # Both regimes get lit (the population spans even and odd periods).
    assert set(per_cell) == {"G1", "G2"}, per_cell
    for key, res in per_cell.items():
        assert res.gap is not None, key

    # CONSERVATION: the union of the partitions' TRUE-failure cases is exactly
    # the whole run's true-failure set, partitioned disjointly by period (no
    # case lost, none double-counted).
    whole_truth = {
        (r.customer_id, r.period_index) for r in records if r.result == "failed"
    }
    g1_truth = {
        (r.customer_id, r.period_index)
        for r in records
        if r.result == "failed" and _regime_of_period(r) == "G1"
    }
    g2_truth = whole_truth - g1_truth
    assert g1_truth and g2_truth, "both partitions must carry real failures"
    assert g1_truth.isdisjoint(g2_truth)
    assert g1_truth | g2_truth == whole_truth


def test_partition_detection_gap_matches_a_manual_subset_score():
    """R15 independence: the per-cell gap is the SAME shared scorer applied to
    just that cell's cases -- prove it by reconstructing one cell's gap by hand
    and asserting equality (the partition adds no bespoke metric, it only routes
    cases to the right cell).

    D12: the shared scorer is now `detection_measures`, so the manual rebuild
    reconstructs the NEGATIVE population by hand too. That is the half worth
    reconstructing: the miss direction was already proven equal, and the way
    this cell grid could go wrong is a negative set that is silently the
    complement of the truth rather than the never-flaggable cases."""
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    per_cell = pair.score_detection_by_partition(
        records, consumer, as_of, _regime_of_period
    )

    # Manually rebuild G1's truth/flagged sets exactly as the function should.
    by_customer = {}
    for r in records:
        by_customer.setdefault(r.customer_id, []).append(r)
    manual_truth, manual_flagged = set(), set()
    manual_universe, manual_negatives = set(), set()
    for cid, periods in by_customer.items():
        snap = consumer.snapshot(periods[0].account_id, as_of=as_of,
                                 payment_terms_days=pair.PAYMENT_TERMS_DAYS)
        due_to_period = {r.due_date: r.period_index for r in periods}
        rec_by_period = {r.period_index: r for r in periods}
        for r in periods:
            if _regime_of_period(r) != "G1":
                continue
            manual_universe.add((cid, r.period_index))
            if r.result == "failed":
                manual_truth.add((cid, r.period_index))
            elif (r.result == "success" and r.days_late is not None
                    and r.days_late <= pair.DEFAULT_RECONCILIATION_GRACE_DAYS):
                # Rebuilt from the RECORD, deliberately: a negative set derived
                # as `universe - truth` would pass this test while charging the
                # company for correctly flagging a late-past-grace payment.
                manual_negatives.add((cid, r.period_index))
        ref_to_period = {r.invoice_ref: r.period_index for r in periods}
        for dd in snap.recent_dd_failures:
            p = due_to_period.get(dd.value_date)
            if p is not None and _regime_of_period(rec_by_period[p]) == "G1":
                manual_flagged.add((cid, p))
        # Reconciliation path now also flags (ruling §2) -- must be in the manual
        # reconstruction too, else the "matches" claim is stale.
        for m in snap.detected_collection_misses:
            p = ref_to_period.get(m.invoice_ref)
            if p is not None and _regime_of_period(rec_by_period[p]) == "G1":
                manual_flagged.add((cid, p))
    expected = detection_measures(
        manual_truth, manual_flagged,
        universe=manual_universe, negative_set=manual_negatives,
        exclusion_reason="manual reconstruction of the cell's excluded cases",
    )
    assert per_cell["G1"].gap == expected.gap
    # Both directions, not just the headline they average into: a headline can
    # match by coincidence when the two directions are individually wrong.
    assert (per_cell["G1"].components["missed_failure_rate"]
            == expected.components["missed_failure_rate"])
    assert (per_cell["G1"].components["false_flag_rate"]
            == expected.components["false_flag_rate"])
    # The negative set is NOT the complement of the truth set. Without this the
    # test would still pass against a scorer that made D11's tenfold error.
    assert manual_negatives < (manual_universe - manual_truth)
    assert per_cell["G1"].components["n_excluded"] > 0


# ---------------------------------------------------------------------------
# D12 -- THE CELL GRID SCORES BOTH DIRECTIONS (R15 must-fire)
# ---------------------------------------------------------------------------

def test_cell_grid_refuses_a_perfect_score_to_a_company_that_flags_everything():
    """THE NAMED DEFECT D12 EXISTS TO KILL. Under the recall-only scorer a
    company that flagged EVERY case in a partition scored that cell a perfect
    0.0, so the grid could not tell a precise supplier from one that dunned its
    whole book. Scored through the REAL entry point, not a re-implementation."""
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    per_cell = pair.score_detection_by_partition(
        records, _FlagEverythingConsumer(records, consumer), as_of,
        _regime_of_period,
    )
    assert per_cell, "no cell measured -- the control would be vacuous"
    for key, res in per_cell.items():
        assert res.gap is not None and res.gap > 0.0, (
            f"cell {key}: flagging every case still scores {res.gap} -- the "
            "cell grid is recall-only again"
        )
        # It is specifically the FALSE-FLAG direction that catches it: the
        # indiscriminate company misses nothing, so a miss-only score is 0.
        assert res.components["missed_failure_rate"] == 0.0
        assert res.components["false_flag_rate"] == 1.0


def test_cell_negative_population_is_not_the_complement_of_truth():
    """R15 MUTATION on the DENOMINATOR -- the half D11 got wrong by a factor of
    ten and the reason this atom was not a copy-paste. Collapse the excluded
    (late-past-grace / disputed / unknown) cases back into the negatives, the
    'obvious' complement-of-truth denominator, and the measured wrongful-dunning
    rate must move MATERIALLY. If it does not, the exclusion is decorative and
    the published rate is charging the company for being right."""
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    honest = pair.score_detection_by_partition(
        records, consumer, as_of, _regime_of_period
    )["G1"]

    truth, flagged, universe, negatives = pair._detection_sets_by_partition(
        records, consumer, as_of, _regime_of_period, pair.PAYMENT_TERMS_DAYS
    )
    mutated = detection_measures(
        truth["G1"], flagged["G1"],
        universe=universe["G1"],
        negative_set=universe["G1"] - truth["G1"],   # THE MUTATION
        exclusion_reason=None,
    )
    honest_rate = honest.components["false_flag_rate"]
    mutated_rate = mutated.components["false_flag_rate"]
    assert honest_rate > 0.0, "vacuity guard: nothing measured to move"
    assert mutated_rate > honest_rate * 5, (
        f"the complement-of-truth denominator ({mutated_rate}) barely differs "
        f"from the never-flaggable one ({honest_rate}) -- on this population "
        "the distinction must dominate, or the exclusion is a no-op"
    )
    # And the excluded cases are the whole difference, published not silent.
    assert honest.components["n_excluded"] > 0
    assert honest.components["exclusion_reason"]


def test_a_cell_with_no_negative_cases_stays_dark_rather_than_fail_open():
    """FAIL-OPEN is the R15 pattern this shape invites: with no never-flaggable
    cases there is no false-flag denominator, and publishing the recall half
    alone under the same field name would silently restore the one-directional
    measure for that cell. It must go DARK instead, leaving the grid's fail-open
    floor to score it at least as badly as the worst measured cell."""
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    # Every non-failed case becomes late-past-grace -> excluded, no negatives.
    stripped = []
    for r in records:
        if r.result == "failed":
            stripped.append(r)
            continue
        clone = copy.copy(r)
        clone.days_late = 999
        stripped.append(clone)
    cells = pair.detection_cell_measurements(stripped, consumer, as_of)
    assert cells == {}, (
        f"a cell with no false-flag denominator was still published: {cells} "
        "-- that is the recall-only measure returning under the new name"
    )


def test_uk_price_regime_marks_the_gas_crisis_window():
    import datetime as _dt
    # Calm years -> G1.
    assert pair.uk_price_regime(_dt.date(2018, 6, 1)) == "G1"
    assert pair.uk_price_regime(_dt.date(2025, 1, 1)) == "G1"
    # The 2021-22 gas crisis -> G2 (historical fact, not a knob).
    assert pair.uk_price_regime(_dt.date(2021, 10, 1)) == "G2"
    assert pair.uk_price_regime(_dt.date(2022, 6, 1)) == "G2"
    # Just before/after the window -> back to calm.
    assert pair.uk_price_regime(_dt.date(2021, 8, 1)) == "G1"
    assert pair.uk_price_regime(_dt.date(2023, 4, 1)) == "G1"


def test_detection_cell_measurements_map_to_grid_cells_with_counts():
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    cells = pair.detection_cell_measurements(
        records, consumer, as_of, regime_of=_regime_of_period
    )
    # Even/odd period split -> both A1_G1 and A1_G2 cells lit.
    assert set(cells) == {"A1_G1", "A1_G2"}, cells
    for cell_id, m in cells.items():
        assert cell_id.startswith("A1_")
        assert m.true_failures > 0
        # believed (flagged) can now EXCEED true: the reconciliation path (ruling
        # §2) also picks up mis-allocated/late-boundary invoices as false
        # positives. The detection gap stays a well-formed recall in [0, 1].
        assert m.believed_failures >= 0
        assert 0.0 <= m.detection_gap <= 1.0
        assert m.regime_label in ("G1", "G2")


def test_partition_classifier_reads_only_harness_truth_never_the_consumer():
    """WALL: the partition_of callable is handed ONLY PeriodRecord (harness
    truth). A classifier that tried to reach a company-belief attribute off the
    record finds nothing there -- PeriodRecord carries no belief field."""
    records, _consumer, _ledger, _as_of = pair.build_scenario(50, seed=3)
    r = records[0]
    for forbidden in ("arrears_risk_belief", "snapshot", "observed_failures",
                      "recent_dd_failures", "belief"):
        assert not hasattr(r, forbidden), (
            f"PeriodRecord must not expose company-belief field {forbidden!r} "
            "to the world-side partition classifier"
        )


# ---------------------------------------------------------------------------
# End-to-end: valid GapResults written to a TEMP ledger (never the real one).
# ---------------------------------------------------------------------------

def test_end_to_end_writes_valid_gap_entries_to_temp_ledger(tmp_path):
    result = pair.measure(_N, seed=_SEED)
    ledger_path = tmp_path / "gap.json"
    commit = "deadbeef"
    measured_at = "2026-07-18T00:00:00+00:00"

    written_keys = set()
    for name in ("detection", "belief", "ageing"):
        r = result[name]
        world_key = f"{pair.WORLD_ATOM_ID}::{name}"
        ledger = write_gap_entry(
            world_key, pair.TWIN_ATOM_ID, r,
            measured_at=measured_at, run_git_commit=commit,
            ledger_path=ledger_path,
        )
        entry = ledger[world_key]
        assert entry["twin_atom_id"] == pair.TWIN_ATOM_ID
        assert entry["metric"] == r.metric
        assert entry["measured_at"] == measured_at
        assert entry["run_git_commit"] == commit
        assert isinstance(entry["gap"], float)
        written_keys.add(world_key)

    reloaded = json.loads(ledger_path.read_text())
    assert set(reloaded.keys()) == written_keys
    assert reloaded[f"{pair.WORLD_ATOM_ID}::detection"]["gap"] > 0.0
    assert reloaded[f"{pair.WORLD_ATOM_ID}::belief"]["gap"] > 0.0


def test_gap_measured_reader_accepts_written_entries(tmp_path):
    from background.coupled_triad import gap_measured

    result = pair.measure(_N, seed=_SEED)
    ledger_path = tmp_path / "gap.json"
    for name in ("detection", "belief", "ageing"):
        world_key = f"{pair.WORLD_ATOM_ID}::{name}"
        ledger = write_gap_entry(
            world_key, pair.TWIN_ATOM_ID, result[name],
            measured_at="2026-07-18T00:00:00+00:00", run_git_commit="abc123",
            ledger_path=ledger_path,
        )
        assert gap_measured(world_key, ledger) is True


# ---------------------------------------------------------------------------
# CLI wiring (no --write-ledger here -- that path touches the real ledger and
# is exercised by the orchestrator post-merge, per the atom's own scope).
# ---------------------------------------------------------------------------

def test_cli_runs_and_prints_all_three_gaps(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["couple_w2_11_d5.py", "--customers", "300", "--seed", "3"])
    pair.main()
    out = capsys.readouterr().out
    assert "W2_11 <-> D5" in out
    assert "[detection]" in out
    assert "[belief]" in out
    assert "[ageing]" in out
    assert "allocation note:" in out
    # D11: the CLI is a surface a human reads, and the headline must never reach
    # it as a bare scalar -- both directions, with their own denominators.
    assert "missed_failure_rate" in out and "false_flag_rate" in out
    assert "wrongful-dunning exposure" in out


# ---------------------------------------------------------------------------
# THE ERROR-DIRECTION CLASS CONTROL (atom D11, the R10 half)
# ---------------------------------------------------------------------------

class _FlagEverythingSnapshot:
    """A belief snapshot for an account that flags EVERY one of its cases as a
    collection miss. Uses the reconciliation channel (`invoice_ref`) rather than
    the DD channel because reconciliation legitimately covers every payment
    method -- a degenerate that could only flag DD cases would understate its
    own indiscriminacy on exactly the non-DD cases the pair cares about."""

    def __init__(self, periods):
        self.recent_dd_failures = ()
        self.detected_collection_misses = tuple(
            SimpleNamespace(invoice_ref=r.invoice_ref) for r in periods
        )


class _FlagEverythingConsumer:
    """The indiscriminate company, wearing the real consumer's interface. It is
    a WRAPPER rather than a patched real consumer so the degenerate cannot
    accidentally inherit any real belief -- what it flags is a property of the
    truth records alone."""

    def __init__(self, records, _real_consumer):
        self._by_account = {}
        for r in records:
            self._by_account.setdefault(r.account_id, []).append(r)

    def snapshot(self, account_id, as_of=None, payment_terms_days=None, **_kw):
        return _FlagEverythingSnapshot(self._by_account.get(account_id, []))


def _flag_everything_score(entry_key, records, consumer, as_of):
    """Score the flag-EVERYTHING degenerate through the scorer THAT ENTRY
    actually uses. Returns the headline that scorer gives an indiscriminate
    company -- the one number that tells a two-directional measure from a
    recall-only one."""
    truth = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    universe = {(r.customer_id, r.period_index) for r in records}
    if entry_key == "score_triad.detection":
        sets = pair.score_triad(records, consumer, as_of)["sets"]
        return detection_measures(
            truth, universe, universe=universe,
            negative_set=sets["never_flaggable"],
            exclusion_reason="late-past-grace successes and disputes").gap
    if entry_key == "score_detection_by_partition":
        # THE CELL GRID, scored through its OWN entry point with a company that
        # flags every case in every partition (D12). Routed through
        # `score_detection_by_partition` itself rather than a hand-rolled
        # `detection_measures` call, so the control measures the code the
        # register names -- a test that re-implemented the scorer would pass
        # even if the real one regressed to recall-only (the R15 tautology).
        per_cell = pair.score_detection_by_partition(
            records, _FlagEverythingConsumer(records, consumer), as_of,
            partition_of=lambda rec: pair.uk_price_regime(rec.due_date),
        )
        assert per_cell, "the cell grid scored no partitions -- nothing measured"
        # The grid's published headline is its WORST cell; a degenerate that
        # scored 0 anywhere would be the defect, so take the best (min) case
        # for the company and let the caller assert it is still not perfect.
        return min(r.gap for r in per_cell.values() if r.gap is not None)
    if entry_key == "couple_w2_5_c7.detection":
        # THE LIFE-EVENT PAIR IS SCORED ON ITS OWN WORLD (atom D15), not on the
        # payment records above: its universe is customer-YEARS and its negative
        # population is an income_stress state, so scoring it here through the
        # triad's records would measure nothing about the register entry. The
        # degenerate is the SAME world with the company replaced by one that
        # flags every instance -- and it is routed through `false_flag_measures`,
        # the function the entry names, so a regression back to recall-only in
        # the real code fails this control rather than passing a re-implementation
        # of it (the R15 tautology).
        from tools import couple_w2_5_c7 as lifepair
        pops = lifepair.partition_populations(120, 2016, 2020)
        measures = lifepair.false_flag_measures(pops.with_flagged(pops.universe))
        return measures[lifepair.PUBLISHED_EXCLUSION_BASIS].gap
    if entry_key == "couple_w2_8_c10.detection":
        # THE SELF-RATIONING PAIR IS ALSO SCORED ON ITS OWN WORLD (atom D14):
        # its universe is households and its negative population is the settled
        # `RationingLabel.NOT_RATIONING` outcome, so the triad's payment records
        # would measure nothing about this entry. Routed through
        # `false_flag_measures` -- the function the entry names -- so a
        # regression to recall-only fails this control instead of passing a
        # re-implementation of it (the R15 tautology).
        from tools import couple_w2_8_c10 as rationpair
        pops = rationpair.build_populations(600)
        flag_everything = dataclasses.replace(pops, flagged=pops.universe)
        measures = rationpair.false_flag_measures(flag_everything)
        return measures[rationpair.PUBLISHED_NEGATIVE_BASIS].gap
    # Every other registered entry is still on the recall-only scorer.
    return detection_gap(truth, universe).gap


def _reference_recall_only_score(records):
    """The OTHER side of the differential, held independently of the register.

    The control compares two shapes: a two-directional scorer must not hand the
    flag-EVERYTHING degenerate a perfect score, a recall-only one must. Sourcing
    the recall-only side from whichever entry HAPPENS to still be unpaid debt
    made the control weaker the closer the register got to clean -- and it would
    have broken outright on the day the last debt was paid, which is the one day
    it must still work (atom D14 paid it). So the recall-only side is scored
    from `detection_gap` DIRECTLY, on this test's own records: the differential
    stays exercised whether or not any entry is still debt.
    """
    truth = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    universe = {(r.customer_id, r.period_index) for r in records}
    return detection_gap(truth, universe).gap


def test_every_published_detection_dimension_declares_its_error_directions():
    """THE CLASS CONTROL (R10 -- an absurdity-class defect may not be closed
    with an instance fix). The instance was the payment triad's headline scoring
    0.0725 while 44-51% of what the company flagged had been paid. The class is
    every published set-membership detection score in this repo.

    The register is not trusted, it is MEASURED: each entry's own scorer is
    handed the flag-EVERYTHING degenerate, and a dimension claiming to count
    both directions must NOT hand it a perfect score -- while one registered as
    recall-only MUST, because that is precisely what makes it debt."""
    records, consumer, _ledger, as_of = pair.build_scenario(250, seed=_SEED)
    contract = pair.DETECTION_DIRECTION_CONTRACT

    assert contract, "the register is empty -- it cannot fail on anything"
    # VACUITY GUARD: both sides of the differential must be exercised, or a pass
    # here proves only that one shape exists. The two-directional side comes
    # from the register; the recall-only side comes from `detection_gap` itself,
    # NOT from whichever entry is still unpaid -- see
    # `_reference_recall_only_score`.
    assert any(v["counts_both_error_directions"] for v in contract.values())
    assert _reference_recall_only_score(records) == 0.0, (
        "the recall-only reference no longer hands the flag-EVERYTHING "
        "degenerate a perfect score -- the differential this control rests on "
        "is gone, so a two-directional pass below would prove nothing"
    )

    for key, declared in contract.items():
        degenerate = _flag_everything_score(key, records, consumer, as_of)
        if declared["counts_both_error_directions"]:
            assert degenerate != 0.0, (
                f"{key} declares it counts both error directions, but a company "
                f"that flagged EVERY case still scores {degenerate} through its "
                "own scorer -- the declaration is false"
            )
            assert declared["debt_atom"] is None, key
        else:
            assert degenerate == 0.0, (
                f"{key} is registered as recall-only debt but flagging "
                "everything no longer scores perfectly -- if it was fixed, "
                "update the register rather than leaving a stale liability"
            )
            assert declared["debt_atom"], (
                f"{key} counts one error direction and names no atom to fix it "
                "-- an unowned limitation is how a defect becomes a convention"
            )
            assert str(declared["why"]).strip(), key


def test_the_error_direction_control_fires_on_a_declaration_that_lies():
    """R15 MUST-FIRE on the register itself. If an entry could simply claim to
    count both directions, the register would be a fail-open switch anyone could
    flip -- the same shape as the as_of contract's exemption."""
    records, consumer, _ledger, as_of = pair.build_scenario(250, seed=_SEED)

    # The lie: a recall-only entry declaring itself two-directional. The example
    # is chosen from the register at RUNTIME, not hardcoded -- D12 fixed the
    # entry this test used to name, and a hardcoded example turns a fixed
    # dimension into a broken control instead of a passing one. When the
    # register carries NO recall-only entry left (D14 paid the last one), the
    # recall-only scorer itself stands in: the control must keep proving it can
    # catch a false declaration on a clean register, which is exactly when a
    # future entry is most likely to be waved through.
    key = next((k for k, v in pair.DETECTION_DIRECTION_CONTRACT.items()
                if not v["counts_both_error_directions"]), None)
    if key is None:
        key = "detection_gap (reference recall-only scorer, no debt left)"
        degenerate = _reference_recall_only_score(records)
    else:
        degenerate = _flag_everything_score(key, records, consumer, as_of)
    assert degenerate == 0.0, f"{key} stopped being recall-only"
    with pytest.raises(AssertionError):
        assert degenerate != 0.0, "declared two-directional but scores a degenerate 0"


# ---------------------------------------------------------------------------
# THE SHARED-QUANTITY CLASS CONTROL (H27 Expert Hour 2026-08-09, the R10 half)
# ---------------------------------------------------------------------------
# The instance it closes: this triad published "the wrongful-dunning exposure"
# from TWO dimensions, in one output block, as 0.0269 and 0.0951 -- 3.5x apart,
# sharing seven cases -- while `background.gap_metric` asserted in prose that
# they were "literally the same numerator". Nothing compared them, so nothing
# could notice. These tests make the comparison a MEASUREMENT.

def _scored(seed: int = _SEED, n: int = 300, grace: int | None = None):
    records, consumer, _ledger, as_of = pair.build_scenario(n, seed=seed)
    kwargs = {} if grace is None else {"reconciliation_grace_days": grace}
    return pair.score_triad(records, consumer, as_of, **kwargs)


def _rendered_dimension_text(result) -> dict:
    """Every published dimension as the text a HUMAN actually reads -- the
    formatter output where there is one, the note otherwise. The phrase sweep
    below runs over this rather than over the contract, because the defect was a
    phrase reaching a reader from a dimension nobody had compared."""
    rendered = {
        "detection": format_detection_summary(result["detection"]),
        "ageing": pair.format_ageing_summary(result["ageing"]),
        "detection_latency": pair.format_detection_latency_summary(
            result["detection_latency"]),
        "belief": format_belief_summary(result["belief"]),
        "belief_population_mix": str(result["belief_population_mix"].note or ""),
    }
    # THIS MAP WAS HAND-MAINTAINED AND THEREFORE FAIL-SILENT (caught 2026-08-10
    # while landing D19). A newly published dimension simply would not appear
    # here, so the phrase sweep -- the whole point of which is that no phrase
    # reaches a reader from a dimension nobody compared -- would skip it and
    # still pass. The set is now DERIVED from the result and asserted, so
    # forgetting a dimension fails loudly instead of quietly shrinking the sweep.
    published = {k for k, v in result.items() if isinstance(v, GapResult)}
    assert set(rendered) == published, (
        f"published dimensions {sorted(published)} but the phrase sweep renders "
        f"{sorted(rendered)} -- an unrendered dimension is invisible to every "
        "control built on this helper"
    )
    return rendered


@pytest.mark.parametrize("seed,grace", [(7, None), (11, None), (23, 12)])
def test_shared_quantity_declarations_are_measured_not_asserted(seed, grace):
    """Each registered quantity's declared population relationship is checked
    against what the two SCORERS actually returned.

    Independence (R15 tautology): the two sides come from
    `gap_metric.ageing_gap` and `gap_metric.detection_measures`, two separate
    measurements over separately built populations. Neither is recomputed here.

    The grace window is varied deliberately: it moves the exclusion band for
    real, through the real code path, so a declaration that only held on one
    fixture would fail rather than pass by coincidence.
    """
    result = _scored(seed=seed, grace=grace)
    measured = pair.shared_quantity_measurements(result)
    assert measured, "the register is empty -- a control over nothing cannot fail"

    for name, spec in pair.SHARED_QUANTITY_CONTRACT.items():
        sides = measured[name]
        det, age = sides["detection"], sides["ageing"]

        # No side may be vacuous: a missing denominator would make the
        # comparison undefined and the control fail-open.
        for dim, side in sides.items():
            assert side["denominator"], f"{name}/{dim} has no denominator"
            assert side["rate"] is not None, f"{name}/{dim} publishes no rate"

        # COINCIDENCE IS SET IDENTITY, NOT EQUAL SIZE (D16). Two different
        # 782-case populations would pass a count check, and "the same size read
        # as the same population" is the shape of the defect this register was
        # minted for. The cases come from the scorers' own returned sets.
        for dim, side in sides.items():
            assert side["denominator_cases"] is not None, (
                f"{name}/{dim}: no denominator CASES -- a count-only comparison "
                "cannot tell two same-sized populations apart"
            )
            assert len(side["denominator_cases"]) == side["denominator"], (
                f"{name}/{dim}: the published denominator {side['denominator']} "
                f"and the cases behind it ({len(side['denominator_cases'])}) "
                "disagree, so one of them is not what the scorer counted"
            )
            assert len(side["numerator_cases"]) == side["numerator"], (
                f"{name}/{dim}: numerator {side['numerator']} vs "
                f"{len(side['numerator_cases'])} cases"
            )

        coincide = age["denominator_cases"] == det["denominator_cases"]
        assert coincide is spec["populations_coincide"], (
            f"{name}: the register declares populations_coincide="
            f"{spec['populations_coincide']} but the measured populations are "
            f"ageing {age['denominator']} vs detection {det['denominator']} "
            f"cases, differing on "
            f"{len(age['denominator_cases'] ^ det['denominator_cases'])}. "
            "A register that can disagree with the run and still pass is the "
            "prose this contract replaced."
        )

        # THE DECLARED RELATIONSHIP, MEASURED. Exact on purpose, exactly as the
        # pre-D16 containment was: the next move on either side breaks it rather
        # than slipping past a phrase loose enough to cover two worlds.
        assert spec["relationship"] == (
            "ageing_denominator_cases == detection_denominator_cases (identical "
            "sets) AND ageing_numerator_cases STRICT SUBSET OF "
            "detection_numerator_cases"
        ), f"{name}: unrecognised relationship -- add its measurement here"
        # VACUITY GUARD: an empty numerator is a subset of anything, so the
        # subset half would pass on a population where the company never
        # overstated at all -- proving nothing.
        assert age["numerator_cases"], (
            f"{name}: the ageing numerator is EMPTY on this population, so the "
            "declared subset holds vacuously and this control measured nothing"
        )
        assert age["numerator_cases"] < det["numerator_cases"], (
            f"{name}: declared STRICT subset broken -- ageing's "
            f"{len(age['numerator_cases'])} case(s) are not a strict subset of "
            f"detection's {len(det['numerator_cases'])}; "
            f"{len(age['numerator_cases'] - det['numerator_cases'])} case(s) "
            "are overstated in the ageing report but were never chased, which "
            "the belief populations say cannot happen"
        )

        # TWO QUANTITIES, TWO NAMES (D16). Rates that differ under ONE name is
        # the original defect; the register must say which quantity each side
        # publishes, and they must not be the same words.
        names = {dim: side["quantity_name"] for dim, side in sides.items()}
        assert all(names.values()), f"{name}: a side publishes an unnamed quantity"
        if age["rate"] != det["rate"]:
            assert len(set(names.values())) == len(names), (
                f"{name}: the sides publish {age['rate']} and {det['rate']} "
                f"under the same name {names} -- two numbers under one name is "
                "the defect this register exists for"
            )

        # An undeclared divergence is the defect; an OWNED one is debt; a
        # DECLARED-AND-DELIBERATE one carries no atom and must say why.
        assert str(spec["why_they_differ"]).strip(), name
        assert str(spec["which_to_read"]).strip(), name


def _phrase_emitters(spec, rendered: dict) -> tuple:
    """Split the dimensions whose RENDERED text contains a registered phrase into
    the ones that PUBLISH the quantity under that name and the ones that only
    DISCLAIM it.

    The distinction is the point (D16). A bare substring sweep cannot tell "this
    rate IS the wrongful-dunning exposure" from "this rate is NOT the
    wrongful-dunning exposure" -- and the second sentence is one a reader who
    remembers the old label needs. Banning the substring outright would refuse
    the honest correction: the AO2 `"none"` shape, which this repo has now been
    bitten by twice, once inside this very atom's predecessor. So the
    disclaimer's FORM is registered and checked, and what is measured is the
    text left over once the disclaimer is removed.
    """
    phrase = str(spec["phrase"])
    disclaimers = dict(spec.get("phrase_disclaimed_by") or {})
    publishers, disclaimers_seen = set(), set()
    for dim, text in rendered.items():
        if phrase not in text:
            continue
        form = disclaimers.get(dim)
        if form and form in text:
            disclaimers_seen.add(dim)
            # What is left after the registered disclaimer is removed. A
            # dimension that both disclaims the name AND uses it affirmatively
            # is still publishing it -- doublespeak must not buy an exemption.
            if phrase in text.replace(form, ""):
                publishers.add(dim)
        else:
            publishers.add(dim)
    return publishers, disclaimers_seen


def test_every_dimension_publishing_a_registered_phrase_is_registered():
    """R10, the half that catches the NEXT instance rather than this one: a
    dimension that starts printing a registered quantity's phrase to a reader
    must appear in that quantity's `phrase_published_by`, or it joins the
    ambiguity with nothing comparing it -- exactly how the ageing/detection pair
    got a fortnight of being two numbers under one name."""
    rendered = _rendered_dimension_text(_scored())

    for name, spec in pair.SHARED_QUANTITY_CONTRACT.items():
        phrase = str(spec["phrase"])
        publishers, disclaimed = _phrase_emitters(spec, rendered)
        assert publishers, (
            f"{name}: no dimension prints {phrase!r} any more -- if the quantity "
            "stopped being published, retire the register entry rather than "
            "leaving a control with nothing to check (it can no longer fail)"
        )
        registered = set(spec["phrase_published_by"])   # type: ignore[arg-type]
        assert publishers == registered, (
            f"{name}: the register says {sorted(registered)} publish {phrase!r} "
            f"and the rendered text says {sorted(publishers)}. A dimension "
            "printing the name unregistered joins the ambiguity with nothing "
            "comparing it; a registered one that stopped printing it leaves a "
            "declaration nothing measures."
        )
        # THE DISCLAIMER IS ITSELF REQUIRED, not merely tolerated: every
        # dimension registered as disclaiming the name must actually say so, or
        # a reader carrying the old label away from the old output block is
        # never told it moved.
        assert disclaimed == set(spec.get("phrase_disclaimed_by") or {}), (
            f"{name}: registered disclaimers {sorted(spec.get('phrase_disclaimed_by') or {})} "
            f"but measured {sorted(disclaimed)} -- a dimension that used to "
            "publish this name must keep saying it no longer does"
        )


def test_the_two_dimensions_score_the_same_cases_and_the_residual_is_belief_side():
    """REPLACES `test_the_two_wrongful_dunning_numbers_are_not_one_number`, which
    pinned the pre-alignment divergence and was written to fail when
    `D16_ageing_negative_population_is_unexcluded` landed. It landed; the
    characterization is replaced, never repaired (the D7 rule).

    What is asserted now is what D16 established, and both halves matter: the
    two dimensions score the IDENTICAL population, and what still differs is
    entirely the belief side -- every case the ageing report overstates was
    chased, and more were chased and then dropped from the report before
    `as_of`. That residual is a property of two honest questions, not leftover
    work, which is why no atom owns it.
    """
    result = _scored()
    sides = pair.shared_quantity_measurements(result)["wrongful_dunning_exposure"]
    det, age = sides["detection"], sides["ageing"]

    assert det["n_excluded"] > 0 and age["n_excluded"] > 0, (
        "a dimension excludes nothing -- the alignment is only meaningful if "
        "BOTH sides carry the band, and one side carrying it was the defect"
    )
    assert det["n_excluded"] == age["n_excluded"], (
        f"the two dimensions exclude different numbers of cases "
        f"({det['n_excluded']} vs {age['n_excluded']}), so they are applying "
        "two rules again rather than reading one set"
    )
    assert age["denominator_cases"] == det["denominator_cases"]

    # THE RESIDUAL IS BELIEF-SIDE, AND IT IS REAL (not a rounding leftover):
    # cases the company chased and later dropped from the ageing report.
    chased_then_dropped = det["numerator_cases"] - age["numerator_cases"]
    assert chased_then_dropped, (
        "detection and ageing now count the same cases as well as the same "
        "population -- if the belief sides have converged, the two-questions "
        "reading in the register is wrong and needs rewriting, not asserting"
    )
    assert age["rate"] < det["rate"], (
        f"the ageing report's overstatement ({age['rate']}) is no longer below "
        f"the wrongful-dunning exposure ({det['rate']}), which the subset "
        "relation between the numerators requires"
    )


def test_shared_quantity_measurements_raises_on_a_missing_dimension():
    """FAIL-OPEN guard (R15): if a registered dimension silently stopped being
    published, comparing whatever was left would pass while the quantity went
    unchecked."""
    result = _scored()
    partial = {k: v for k, v in result.items() if k != "ageing"}
    with pytest.raises(KeyError, match="does not publish"):
        pair.shared_quantity_measurements(partial)


def test_the_shared_quantity_control_fires_on_a_register_that_lies():
    """R15 MUST-FIRE, mutating the DECLARATION both ways. A register anyone can
    write anything into is a switch, not a control -- the same shape the as_of
    contract's exemption and the direction contract's `counts_both_error_
    directions` are each held to."""
    measured = pair.shared_quantity_measurements(_scored())
    det = measured["wrongful_dunning_exposure"]["detection"]
    age = measured["wrongful_dunning_exposure"]["ageing"]

    # Lie 1: declare the populations DIFFERENT now that D16 has aligned them.
    # The pre-D16 register declared exactly this and was true; the same
    # declaration is now false, and the control must notice which world it is in
    # rather than accepting whichever the register asserts.
    with pytest.raises(AssertionError):
        assert (age["denominator_cases"] == det["denominator_cases"]) is False, (
            "declared divergent, but the populations are the same set")

    # Lie 2: declare the numerators identical -- the shape the retired prose
    # claim implied ("literally the same numerator"). Alignment made the
    # denominators one population; it did NOT make the numerators one set, and a
    # register saying otherwise must fail.
    with pytest.raises(AssertionError):
        assert age["numerator_cases"] == det["numerator_cases"], (
            "declared the same numerator, but the belief sides differ")

    # Lie 3: declare the subset in the WRONG DIRECTION. A control that only
    # checked "the two overlap" would pass on this.
    with pytest.raises(AssertionError):
        assert det["numerator_cases"] < age["numerator_cases"], (
            "declared detection's cases inside ageing's; it is the other way")


def test_the_phrase_sweep_fires_on_an_unregistered_publisher():
    """R15 MUST-FIRE on the sweep half: a dimension that really does print the
    phrase, de-registered, must be caught. Without this the sweep could be an
    empty loop that never had an emitter to find."""
    rendered = _rendered_dimension_text(_scored())
    spec = pair.SHARED_QUANTITY_CONTRACT["wrongful_dunning_exposure"]
    publishers, _ = _phrase_emitters(spec, rendered)
    assert publishers, "no dimension publishes the phrase -- nothing to sweep"

    de_registered = set(spec["phrase_published_by"]) - {"detection"}
    with pytest.raises(AssertionError):
        assert publishers == de_registered, "detection prints the phrase unregistered"


def test_the_phrase_sweep_tells_publishing_the_name_from_disclaiming_it():
    """R15 MUST-FIRE on the D16 half, in BOTH directions -- and this is the test
    that stops the sweep degenerating back into a substring ban.

    The ageing summary mentions the phrase, deliberately, to say the rate is NOT
    that quantity. A bare `phrase in text` sweep counts that as publishing it
    (it did, on the first run of this build) and would force the honest sentence
    to be deleted to satisfy a control -- the AO2 `"none"` shape. So: the real
    disclaimed text must NOT read as a publisher, and text that both disclaims
    and then uses the name affirmatively MUST.
    """
    rendered = _rendered_dimension_text(_scored())
    spec = pair.SHARED_QUANTITY_CONTRACT["wrongful_dunning_exposure"]
    phrase = str(spec["phrase"])
    form = spec["phrase_disclaimed_by"]["ageing"]        # type: ignore[index]

    assert phrase in rendered["ageing"] and form in rendered["ageing"], (
        "the ageing summary no longer mentions the name it used to publish, so "
        "this test is measuring nothing and a reader is never told it moved"
    )
    publishers, disclaimed = _phrase_emitters(spec, rendered)
    assert "ageing" in disclaimed and "ageing" not in publishers

    # DOUBLESPEAK MUST NOT BUY AN EXEMPTION: disclaim the name once, then use it
    # affirmatively, and the dimension is publishing it again.
    doublespeak = dict(rendered)
    doublespeak["ageing"] = rendered["ageing"] + f" = {phrase}"
    publishers_2, _ = _phrase_emitters(spec, doublespeak)
    assert "ageing" in publishers_2, (
        "a summary that disclaims the name and then uses it anyway reads as "
        "disclaimed -- the sweep is checking for the disclaimer, not for the "
        "absence of the claim"
    )

    # And the disclaimer being DROPPED is caught too: the phrase without its
    # registered form is a publisher.
    dropped = dict(rendered)
    dropped["ageing"] = rendered["ageing"].replace(form, phrase)
    publishers_3, disclaimed_3 = _phrase_emitters(spec, dropped)
    assert "ageing" in publishers_3 and "ageing" not in disclaimed_3


def test_cli_write_ledger_publishes_the_measured_note_not_a_retired_one(monkeypatch):
    """The `--write-ledger` branch had NO test, and that is exactly how it kept
    publishing a REFUTED sentence for a day after the sentence was refuted.

    It overwrote the measured `det.note` with "the fraction of true payment
    failures the company NEVER OBSERVES through the seam -- the no-remittance
    blind spot": D10 measured that false (`n_undetected` == 0 on seeds 7/11/23 --
    the residual is detections the company UN-made under oldest-first
    allocation), and D11 then made it wrong a second way (the headline is a
    balanced error over two directions, not a fraction of failures). Both this
    path and `background.live_payment_triad.measure_and_write` write the SAME
    bare ledger key the Proof door reads, so whichever ran last decided what a
    reader saw -- the live one was corrected on 2026-08-09 and this offline
    sibling was left behind (the sibling-half class, again).

    The ledger is not touched: the writer is captured, so what is under test is
    the NOTE, which is the thing that rotted.
    """
    captured = {}

    def _capture(world, twin, result, **kwargs):
        captured["result"] = result
        return {world: {"gap": result.gap}}

    monkeypatch.setattr(pair, "write_gap_entry", _capture)
    monkeypatch.setattr(
        "sys.argv",
        ["couple_w2_11_d5.py", "--customers", "250", "--seed", "3", "--write-ledger"],
    )
    pair.main()

    note = captured["result"].note
    # ASSERT ON THE CLAIM, NOT ON THE WORDS. A bare ban on "never observes"
    # refuses the honest sentence that NEGATES it, which is the shape that has
    # already bitten this repo once (an AO2 gate tripping on the word "none").
    # What must be absent is the AFFIRMATIVE description; what must be present
    # is its correction.
    retired_claim = (
        "fraction of true payment failures the company never observes"
    )
    assert retired_claim not in note, (
        "the retired, measured-false description of the headline is back in the "
        "published note"
    )
    assert "never observes" in note and "NOT" in note, (
        "the note should name the retired description and say it is wrong -- a "
        "reader comparing this entry with a pre-2026-08-09 one needs to be told "
        "the description changed, not just handed a different sentence"
    )
    # It must publish what the headline actually IS, with both directions.
    assert "BALANCED" in note and "missed_failure_rate" in note
    assert "false_flag_rate" in note
    # And it must not silently drop the measured note it used to clobber.
    assert "THE MEASURED NOTE FOLLOWS" in note
    assert "atom D11" in note or "D11" in note
    # The two same-named exposures must be flagged as different measurements
    # wherever both are printed together (the shared-quantity finding).
    assert "SHARED_QUANTITY_CONTRACT" in note


# ---------------------------------------------------------------------------
# THE AGEING EXCLUSION BAND (atom D16) -- R15 both ways
# ---------------------------------------------------------------------------
# The band is the whole of this atom's mechanism, so it gets the two mutations
# the atom's own brief demanded: prove it is not a no-op (fold it back in and
# the rate must move), and prove it cannot fail OPEN on a record whose
# `days_late` truth is unknown -- the case where "assume it was paid on time"
# would quietly count a company error that may not be one.

def test_the_ageing_exclusion_is_not_a_no_op():
    """R15 MUST-MOVE. Re-score the ageing dimension's OWN inputs through the SAME
    scorer with the mask removed: if the band changed nothing, the alignment is
    decoration and the two dimensions were never really brought together."""
    result = _scored()
    inputs = result["ageing_inputs"]
    assert any(inputs["excluded"]), "nothing was excluded -- the band is empty here"

    aligned = result["ageing"].components["overstated_arrears_rate"]
    unaligned = ageing_gap(
        inputs["truth_labels"], inputs["belief_labels"],
    ).components["overstated_arrears_rate"]

    assert unaligned != aligned, (
        "folding the excluded band back into the denominator leaves the rate "
        "unchanged, so the band contains no case the company is scored on and "
        "this atom moved nothing"
    )
    # DIRECTION, not a pinned value: the band can only ADD truly-current cases
    # (and the false ageings among them), and the finding is that it added
    # proportionally more numerator than denominator.
    assert unaligned > aligned, (
        f"the unaligned rate {unaligned} is not above the aligned {aligned}; "
        "the excluded band is made of cases the company was RIGHT about, so "
        "counting them against it can only inflate the rate"
    )


def test_the_ageing_exclusion_does_not_fail_open_on_unknown_days_late():
    """R15 FAIL-OPEN. A record whose `days_late` truth is missing is UNKNOWN, and
    the fail-open reading -- 'no lateness recorded, so it was paid on time' --
    would drop it into the truly-current population and score the company for a
    belief nobody can adjudicate.

    Measured through the real path: blank `days_late` on the within-grace
    successes and they must LEAVE the scored population entirely, not join it.
    """
    records, consumer, _ledger, as_of = pair.build_scenario(300, seed=_SEED)
    clean = pair.score_triad(records, consumer, as_of)
    before = clean["ageing"].components

    grace = pair.DEFAULT_RECONCILIATION_GRACE_DAYS
    blanked = 0
    for r in records:
        if r.result == "success" and r.days_late is not None and r.days_late <= grace:
            r.days_late = None
            blanked += 1
    assert blanked, "no within-grace success to blank -- the mutation is vacuous"

    after = pair.score_triad(records, consumer, as_of)["ageing"].components
    assert after["n_truly_current"] == before["n_truly_current"] - blanked, (
        "an unknown `days_late` did not leave the truly-current population -- "
        "the band is reading missing truth as 'paid on time', which is the "
        "fail-open shape this exclusion exists to avoid"
    )
    assert after["n_excluded"] == before["n_excluded"] + blanked


def test_the_two_dimensions_read_ONE_exclusion_set_not_two_copies():
    """The defect this atom closes was born of one rule living in one dimension.
    A second copy of the rule for the ageing side would have been the same shape
    again, one file over -- so the set is built once and both read it.

    Asserted structurally as well as numerically: the module must construct
    `never_flaggable` exactly once.

    THE SUBJECT MOVED 2026-08-18 AND THE ASSERTION HAD TO MOVE WITH IT. This
    counted the string `    never_flaggable = {` -- the assignment inside
    `score_triad`. The band was then lifted into `never_flaggable_band` so the
    population-side predictor could read the SAME rule instead of writing a
    second copy of it, which is this test's own subject; counting the old
    assignment would have read 0 and failed the extraction that satisfies it.
    So it counts the RULE now rather than one site's assignment statement,
    which is what it was always about and is the stronger check: a second copy
    anywhere in the module trips it, including one that never binds the name."""
    src = Path(pair.__file__).read_text()
    assert src.count("r.days_late <= reconciliation_grace_days") == 1, (
        "the never-flaggable band is constructed more than once in this module; "
        "two copies of one rule is how the detection and ageing dimensions came "
        "to disagree about the same cases"
    )
    assert "never_flaggable_band" in pair._names_in(pair.score_triad), (
        "`score_triad` must READ the shared band, not rebuild it"
    )
    result = _scored()
    sets = result["sets"]
    assert sets["ageing_truly_current"] == sets["never_flaggable"], (
        "the ageing dimension's scored-current population is not the detection "
        "dimension's negative set, so the two are applying different rules again"
    )


def test_the_pair_reexports_the_class_register_it_does_not_copy_it():
    """The register was lifted OUT of this triad's module on 2026-08-09 because
    it is a CLASS register (R10) and living inside the one pair that tripped the
    defect is how the previous ones ended up triad-local. The pair re-exports it
    for its consumers -- this asserts the re-export is the SAME OBJECT, not a
    second copy that could drift, and gives the new module its own direct test
    evidence (the capability index reads it as untested otherwise, which is the
    no-caller shape this repo keeps auditing)."""
    import background.shared_quantity_contract as reg

    assert pair.SHARED_QUANTITY_CONTRACT is reg.SHARED_QUANTITY_CONTRACT
    assert pair.shared_quantity_measurements is reg.shared_quantity_measurements


# ===========================================================================
# THE AGGREGATE-SCORING CLASS (atom D19, H27 Expert-Hour pass #3, 2026-08-10)
#
# The class the four DETECTION registers never swept: a dimension scored on
# POPULATION AGGREGATES is blind to per-case assignment. `belief` is a total-
# variation distance between two severity distributions, so a company that gets
# the population MIX right and every INDIVIDUAL wrong scores exactly what the
# real company scores.
#
# These are MEASUREMENT tests, not declaration-reading tests: each one actually
# permutes the company's per-case labels and re-scores through the dimension's
# OWN shipped scorer. R15 independence -- a test carrying its own copy of the
# TV formula could not fail if the shipped one changed.
# ===========================================================================

def test_the_belief_headline_moves_under_a_permutation_since_d19():
    """THE FIX, measured rather than declared. Until 2026-08-10 this assertion
    was its own inverse: destroying every correct per-case assignment while
    leaving the label multiset alone moved the published belief figure by
    exactly zero, so the degenerate 'right mix, every individual wrong' scored
    what the real company scored.

    D19 reshaped the headline to a balanced PER-CASE error, and this is the
    acceptance criterion the finding wrote down: the permutation sweep must
    come out MOVED. It must also come out moved to somewhere USELESS -- a
    degenerate that still beat the no-skill baseline would mean the reshape
    changed the number without closing the hole."""
    result = _scored()
    report = pair.measure_permutation_sensitivity(result)
    bel = report["belief"]

    assert bel["probe_bit"], "vacuous probe -- per-case agreement did not fall"
    assert bel["gap_moved"], (
        "the belief headline did not move under a pure permutation -- the D19 "
        "reshape has regressed to the population-distribution shape"
    )
    assert bel["gap_after"] > bel["gap_before"], (
        f"permuting every belief IMPROVED the score "
        f"({bel['gap_before']} -> {bel['gap_after']})"
    )
    g0 = result["belief"].g0
    assert bel["gap_after"] >= g0 * 0.9, (
        f"'right mix, every individual wrong' scored {bel['gap_after']}, "
        f"comfortably better than the no-skill baseline {g0} -- the degenerate "
        "still buys something"
    )


def test_the_population_mix_dimension_is_blind_by_design_and_says_so():
    """The retired headline's own number, kept and RENAMED (D19). Its blindness
    is not a defect here -- 'does the company have the right MIX?' is a real
    question and a distribution distance is the right shape for it. What was
    the defect was publishing it under a name that reads as a per-case error
    rate. So the blindness must stay MEASURED and DECLARED, and this dimension
    is now the side of the differential that must NOT move."""
    result = _scored()
    report = pair.measure_permutation_sensitivity(result)
    bel = report["belief_population_mix"]

    # VACUITY GUARD FIRST. A permutation that changed no per-case assignment
    # would make "the gap did not move" prove exactly nothing.
    assert bel["probe_bit"], (
        "the permutation did not reduce per-case agreement at all, so this "
        "control is vacuous -- it would pass on a dimension that IS per-case"
    )
    assert bel["agreement_before"] - bel["agreement_after"] > 0.10, (
        "the probe barely moved per-case assignment; a near-identity "
        "permutation cannot distinguish blind from sensitive"
    )

    assert bel["gap_after"] == bel["gap_before"], (
        "the belief gap moved under a pure permutation -- if that is a real "
        "change the AGGREGATE_SCORING_CONTRACT declaration is now wrong"
    )
    assert not bel["gap_moved"]


def test_the_aggregate_scoring_contract_is_differential_not_a_blanket_ban():
    """The DIMENSION_AS_OF_CONTRACT lesson, applied: a blanket rule that fired
    on every dimension would jam the gate and teach everyone to skip it. Both
    sides of the differential must be genuinely exercised -- an aggregate-only
    dimension that really does not move, AND per-case dimensions that really
    do."""
    result = _scored()
    report = pair.measure_permutation_sensitivity(result)

    assert set(report) == {"belief", "belief_population_mix", "ageing",
                           "detection"}, (
        "a scored dimension was added or renamed without an aggregate-scoring "
        "declaration -- no published number escapes this control"
    )

    blind = {d for d, v in report.items() if v["declared_aggregate_only"]}
    sensitive = set(report) - blind
    assert blind and sensitive, (
        "the control is not differential: every dimension landed on one side, "
        "so it is a blanket rule wearing a register's clothes"
    )

    for dim, v in report.items():
        assert v["probe_bit"], f"{dim}: permutation probe was inert (vacuous)"
        assert v["gap_moved"] is not v["declared_aggregate_only"], (
            f"{dim}: AGGREGATE_SCORING_CONTRACT declares "
            f"is_aggregate_only={v['declared_aggregate_only']} but the measured "
            f"gap {'moved' if v['gap_moved'] else 'did not move'} "
            f"({v['gap_before']} -> {v['gap_after']})"
        )


def test_the_rescored_before_value_is_the_published_one():
    """R15 independence/tautology guard. If the control's `gap_before` were its
    own re-derivation rather than the shipped scorer's answer, it could agree
    with itself while the published number said something else -- and this whole
    control would be measuring a copy. Every dimension's unpermuted rescore must
    reproduce the headline exactly."""
    result = _scored()
    report = pair.measure_permutation_sensitivity(result)
    for dim in report:
        assert report[dim]["gap_before"] == result[dim].gap, (
            f"{dim}: the control's rescore ({report[dim]['gap_before']}) is not "
            f"the published gap ({result[dim].gap}) -- it is scoring a copy"
        )


def test_a_lying_aggregate_declaration_fails_the_control():
    """R15, mutating the SOURCE register rather than the test's own copy: flip
    each declaration in turn and the control must catch every one."""
    result = _scored()

    for dim in ("belief", "ageing", "detection"):
        lying = {k: dict(v) for k, v in pair.AGGREGATE_SCORING_CONTRACT.items()}
        lying[dim]["is_aggregate_only"] = not lying[dim]["is_aggregate_only"]
        report = pair.measure_permutation_sensitivity(result, contract=lying)
        v = report[dim]
        assert v["gap_moved"] is v["declared_aggregate_only"], (
            f"{dim}: the declaration was inverted and the control did not "
            f"notice -- it cannot fail on a false claim"
        )


def test_a_declared_dimension_with_no_labels_raises_rather_than_skipping():
    """FAIL-SILENT is the killer pattern here: a dimension whose labels the
    scorer stopped publishing would silently drop OUT of the sweep, and a
    register with an unreachable entry reads exactly like a clean one."""
    result = _scored()
    stripped = dict(result)
    stripped["labels"] = {
        k: v for k, v in result["labels"].items()
        if not k.startswith("belief_")
    }
    with pytest.raises(ValueError, match="published no per-case labels"):
        pair.measure_permutation_sensitivity(stripped)


def test_the_per_case_witness_rides_beside_the_population_mix_score():
    """The direction the distance cannot see must travel WITH the number, at
    source, so it lands on all three pairs calling `belief_gap` rather than only
    where the defect was found. Still required AFTER the D19 reshape: this
    dimension is still blind, and a reader who takes the mix figure alone must
    meet that fact in the same breath rather than one dimension over."""
    result = _scored()
    c = result["belief_population_mix"].components

    assert c["permutation_invariant"] is True
    assert c["n_cases"] == len(result["labels"]["belief_truth"])
    assert 0.0 <= c["per_case_disagreement_rate"] <= 1.0
    assert c["n_cases_misassigned"] == sum(
        1 for a, b in zip(result["labels"]["belief_truth"],
                          result["labels"]["belief_belief"]) if a != b)

    # The caveat is stamped at SOURCE, not typed into this pair's note.
    from background.gap_metric import BELIEF_GAP_PERMUTATION_CAVEAT
    assert BELIEF_GAP_PERMUTATION_CAVEAT in result["belief_population_mix"].baseline
    # ...and the published note interpolates the witness FROM the measurement,
    # so it cannot rot into a claim about a run that has already ended.
    note = result["belief_population_mix"].note
    assert str(c["n_cases_misassigned"]) in note
    assert "PERMUTATION-INVARIANT" in note


def test_an_unavailable_per_case_witness_is_none_never_zero():
    """A caller that cannot supply per-case labels must get `None`, never 0 --
    a 0 there is the strongest possible claim ('the company got every case
    right') handed out for free to a caller that simply did not measure. The
    two other pairs calling `belief_gap` are exactly such callers today."""
    r = belief_gap([0.5, 0.3, 0.2], [0.4, 0.4, 0.2])
    assert r.components["per_case_disagreement_rate"] is None
    assert r.components["n_cases"] is None
    assert r.components["permutation_invariant"] is True
    assert "UNKNOWN" in pair._belief_permutation_note(r)

    # An empty population is not a perfect one either.
    empty = belief_gap([0.5, 0.5], [0.5, 0.5], truth_labels=[], belief_labels=[])
    assert empty.components["n_cases"] == 0
    assert empty.components["per_case_disagreement_rate"] is None


def test_mismatched_label_populations_raise_rather_than_zip_short():
    """`zip` truncates silently, which would score the company on a prefix of
    its own book and report a confident rate over the wrong denominator."""
    with pytest.raises(ValueError, match="not the same population"):
        belief_gap([0.5, 0.5], [0.5, 0.5],
                   truth_labels=["a", "b", "a"], belief_labels=["a", "b"])


# ===========================================================================
# THE D19 RESHAPE -- the belief headline scores PER-CASE assignment
# (atom D19_belief_gap_is_distribution_only, landed 2026-08-10)
# ===========================================================================
# The reshape is only worth the discontinuity it causes if the new shape
# actually closes the hole, so these tests are about the SHAPE, not the value:
# neither degenerate strategy may buy a score, each direction carries the
# population on which its error is possible, and the direction that reads
# 0.0000 on this book must be PROVEN able to fire rather than assumed dead.

_SEVERITY = pair._SEVERITY_ORDER


def test_neither_belief_degenerate_can_buy_a_score():
    """The D11 property, carried across. A recall-only detection score gave a
    perfect 0.0 to a company that flagged everything; the population-TV belief
    score gave the real company's own number to a company that got the mix
    right and every account wrong. A balanced two-direction measure must hand
    every severity-blind rule the SAME no-skill baseline."""
    truth = ["normal"] * 60 + ["watch"] * 20 + ["elevated"] * 10 + ["high"] * 10

    all_normal = belief_measures(truth, ["normal"] * 100, order=_SEVERITY)
    all_high = belief_measures(truth, ["high"] * 100, order=_SEVERITY)

    # Call everyone `normal`: every account that could be under-called is.
    assert all_normal.components["undercall_rate"] == 1.0
    assert all_normal.components["overcall_rate"] == 0.0
    assert all_normal.gap == pytest.approx(0.5)
    # Call everyone `high`: the mirror image.
    assert all_high.components["overcall_rate"] == 1.0
    assert all_high.components["undercall_rate"] == 0.0
    assert all_high.gap == pytest.approx(0.5)
    # ...and both land exactly on the declared no-skill baseline.
    assert all_normal.g0 == all_high.g0 == 0.5

    perfect = belief_measures(truth, list(truth), order=_SEVERITY)
    assert perfect.gap == 0.0


def test_the_overcall_direction_reads_zero_here_and_can_still_fire():
    """R15 MUST-FIRE on a structurally-quiet direction. This book's company
    UNDER-calls severity and nothing else -- `overcall_rate` is 0.0000 on every
    seed -- which is exactly the shape that lets a dead measure pass for a clean
    one (D11's `missed_failure_rate` is the same shape one dimension over, and
    its registered open question). A direction that reads 0 must be shown to be
    measuring, not merely quiet: hand the same scorer a company that over-calls
    and the rate must move."""
    result = _scored()
    c = result["belief"].components
    assert c["overcall_rate"] == 0.0, (
        "this book's company now over-calls severity -- the premise of the "
        "test below has changed and the reading needs re-deriving, not the "
        "assertion relaxing"
    )
    assert c["n_overcall_population"] > 0, (
        "the over-call DENOMINATOR is empty, so the 0.0 above is vacuity "
        "wearing a measurement's clothes -- it must publish None, not 0"
    )

    truth = list(result["labels"]["belief_truth"])
    # One account escalated a step it did not earn, and nothing else changed.
    over = list(result["labels"]["belief_belief"])
    idx = next(i for i, (t, b) in enumerate(zip(truth, over))
               if t == b == "normal")
    over[idx] = "watch"
    moved = belief_measures(truth, over, order=_SEVERITY)
    assert moved.components["n_overcalled"] == 1
    assert moved.components["overcall_rate"] > 0.0
    assert moved.gap > result["belief"].gap, (
        "over-calling one account did not worsen the balanced error -- the "
        "second direction is not reaching the headline"
    )


def test_each_direction_is_scored_on_the_population_where_it_is_possible():
    """The D7 rule, applied at birth. An account already at the bottom of the
    scale CANNOT be under-called; counting it in that denominator would move the
    rate with the shape of the book rather than the company's judgement -- the
    prevalence dependence D6 measured and D7 removed one dimension over."""
    truth = ["normal"] * 90 + ["high"] * 10
    belief = ["normal"] * 90 + ["normal"] * 10   # every `high` under-called

    r = belief_measures(truth, belief, order=_SEVERITY)
    assert r.components["n_undercall_population"] == 10, (
        "the 90 bottom-of-scale accounts leaked into the under-call "
        "denominator, which is the prevalence dependence this shape exists to "
        "avoid"
    )
    assert r.components["undercall_rate"] == 1.0
    # ...and the whole-book rate would have said 0.10 -- the number the company
    # would have been judged on if the denominator were the population.
    assert r.components["per_case_disagreement_rate"] == pytest.approx(0.10)
    # Magnitude rides beside the rate: three steps, not one.
    assert r.components["mean_undercall_steps"] == pytest.approx(3.0)


def test_a_direction_with_no_population_is_none_never_zero():
    """FAIL-OPEN is the killer pattern for a balanced measure: with nothing to
    get wrong in one direction, scoring that direction 0 would halve a real
    error into a flattering headline. Undefined must stay undefined."""
    # Everyone truly at the top: over-calling is impossible.
    r = belief_measures(["high"] * 5, ["watch"] * 5, order=_SEVERITY)
    assert r.components["overcall_rate"] is None
    assert r.gap is None, (
        "the headline fell back to the surviving direction alone -- a book on "
        "which an error is impossible is not one the company got right"
    )
    assert "UNDEFINED" in str(r.components["vacuity"])
    assert "undefined" in format_belief_summary(r)


def test_belief_measures_fails_loud_on_every_input_it_cannot_score():
    """R15 fail-loud. Each of these would otherwise produce a confident number
    over the wrong population."""
    with pytest.raises(ValueError, match="not the same population"):
        belief_measures(["normal", "high"], ["normal"], order=_SEVERITY)
    with pytest.raises(ValueError, match="empty population"):
        belief_measures([], [], order=_SEVERITY)
    with pytest.raises(ValueError, match="outside the declared scale"):
        belief_measures(["normal", "critical"], ["normal", "normal"],
                        order=_SEVERITY)
    with pytest.raises(ValueError, match="at least two severity levels"):
        belief_measures(["normal"], ["normal"], order=("normal",))
    with pytest.raises(ValueError, match="duplicate level"):
        belief_measures(["normal"], ["normal"], order=("normal", "normal"))


def test_the_scale_is_declared_never_inferred_from_the_labels_present():
    """A scale inferred from the labels a run happened to produce would make
    'over-called' mean something different on every population -- a run where
    nobody reached the top of the scale would silently redefine the ceiling.
    The same two labels score differently under two declared scales, and that
    is the point."""
    truth, belief = ["watch", "watch"], ["high", "high"]

    full = belief_measures(truth, belief, order=_SEVERITY)
    assert full.components["overcall_rate"] == 1.0      # `watch` < `high`

    topped = belief_measures(truth, belief, order=("normal", "watch", "high"))
    assert topped.components["overcall_rate"] == 1.0
    assert topped.components["mean_overcall_steps"] == pytest.approx(1.0)
    assert full.components["mean_overcall_steps"] == pytest.approx(2.0), (
        "the scale's step size did not reach the magnitude witness, so two "
        "different scales report the same distance"
    )


def test_the_belief_headline_never_prints_as_a_bare_scalar():
    """The anti-decay mechanism `format_ageing_summary` and
    `format_detection_summary` carry, for the same reason: this dimension went
    wrong the moment a bare `belief 0.0700` could be read as a per-case error
    rate. Both directions, both denominators, every render."""
    result = _scored()
    rendered = format_belief_summary(result["belief"])
    c = result["belief"].components

    assert "under-called severity" in rendered
    assert "over-called severity" in rendered
    assert str(c["n_undercall_population"]) in rendered
    assert str(c["n_overcall_population"]) in rendered
    assert "0.5 = every severity-blind rule" in rendered
    # The nouns are parameters (the D15 rule) -- a second pair scoring an
    # ordinal belief is not measuring arrears severity.
    other = format_belief_summary(result["belief"],
                                  undercall_name="under-graded risk",
                                  overcall_name="over-graded risk")
    assert "under-graded risk" in other and "under-called severity" not in other


def test_the_published_belief_headline_is_the_per_case_measure():
    """The reshape must reach the PUBLISHED surface, not just the module. A
    scorer swapped in while the triad still publishes the old dimension is the
    half-cut this project has caught before."""
    result = _scored()
    c = result["belief"].components

    assert "undercall_rate" in c and "overcall_rate" in c
    assert result["belief"].g0 == 0.5
    assert "BALANCED PER-CASE" in result["belief"].note
    assert "D19" in result["belief"].note
    # The retired figure is not restated inside the new measure (D16: one name,
    # one number) -- it is its own dimension, on the same labels.
    assert "tv" not in c
    assert result["belief_population_mix"].components["tv"] == pytest.approx(
        result["belief_population_mix"].raw_gap, abs=1e-6)
    assert result["belief"].gap != result["belief_population_mix"].gap


# ---------------------------------------------------------------------------
# THE COVERAGE-ONLY CLAIM (atom D20_belief_truth_rule_is_an_unmeasured_mirror)
# ---------------------------------------------------------------------------
# H27 Expert Hour #4, 2026-08-10. The belief dimension publishes its two sides
# as "same threshold shape, different-coverage inputs" -- and that claim, not
# the arithmetic, is what makes the number a measure of the WALL. It lived in a
# docstring: `pair._severity_label` is a HAND-COPY of the company organ's
# `_arrears_risk_belief` thresholds and no test named the pair. Three plausible
# organ-only drifts moved the published headline by up to 2.9x; exactly one
# test fired each time and none named the divergence.


def _organ_drift(monkeypatch, transform):
    """Mutate the COMPANY ORGAN's own thresholding rule and nothing else.

    The world, the seam and the harness's truth-side rule are untouched, so any
    movement in a coverage-only dimension is rule divergence by construction --
    which is exactly what these controls have to be able to see."""
    original = PaymentObservationConsumer._arrears_risk_belief

    def drifted(self, account_id, as_of):
        return transform(original(self, account_id, as_of))

    monkeypatch.setattr(
        PaymentObservationConsumer, "_arrears_risk_belief", drifted)


@pytest.mark.parametrize("seed", [7, 11, 23])
def test_the_coverage_only_claim_is_measured_not_asserted(seed):
    """Equalise the coverage and the residual IS the rule divergence.

    INDEPENDENCE (R15 tautology): nothing here reads, copies or compares either
    side's thresholds. Both labels come out of the shipped paths over a real
    population fed through the real seam, so the only way to pass is for the
    two rules to actually agree on inputs they both fully saw."""
    cov = pair.measure_coverage_only_residual(n_customers=600, seed=seed)
    w = cov["witnesses"]

    # VACUITY FIRST -- a zero on a population with no coverage loss to remove,
    # or with no possible-error population, is the strongest possible claim
    # handed out for free.
    assert not cov["is_vacuous"], f"vacuous counterfactual: {w}"
    assert w["coverage_loss_removed"] > 0, (
        "the scored book carried no non-DD true failures, so equalising "
        "coverage removed nothing and a zero residual means nothing")
    assert w["cf_non_dd_failures"] == 0, (
        "the counterfactual still contains push-channel failures -- coverage "
        "was not actually equalised")
    assert w["cf_undercall_population"] > 0 and w["cf_overcall_population"] > 0
    # THE DIFFERENTIAL. If every dimension read 0 the zeros below would be a
    # property of the run, not of the rules.
    assert w["n_exempt_dimensions_nonzero"] > 0, (
        "no exempt dimension read non-zero on this population -- a build that "
        "collapsed every gap to 0 would pass this control as agreement")

    for dim, v in cov["residuals"].items():
        if not v["claims_coverage_only"]:
            continue
        assert v["residual"] == 0, (
            f"{dim} publishes its two sides as differing ONLY in coverage, but "
            f"with coverage equalised {v['residual']} survives -- the "
            "truth-side rule and the company organ's rule have diverged, and "
            f"the number published on the scored book "
            f"({v['gap_on_the_scored_book']}) is a mixture of coverage loss "
            "and rule divergence being read as coverage")


def test_the_coverage_only_contract_reaches_every_published_dimension():
    """The register is DERIVED from what is published, not hand-maintained.

    The same fail-silent shape D19 closed on the phrase sweep: a newly
    published dimension that is simply absent from the contract is a dimension
    this control skips while still passing."""
    published = {k for k, v in _scored().items() if isinstance(v, GapResult)}
    declared = set(pair.COVERAGE_ONLY_CLAIM_CONTRACT)
    assert declared == published, (
        f"published dimensions {sorted(published)} but the coverage-only "
        f"contract declares {sorted(declared)} -- an undeclared dimension is "
        "invisible to this control")
    for dim, decl in pair.COVERAGE_ONLY_CLAIM_CONTRACT.items():
        assert isinstance(decl["claims_coverage_only"], bool)
        assert decl["why"].strip(), f"{dim} declares nothing about why"


def test_a_dimension_whose_published_text_makes_the_claim_must_declare_it():
    """THE CLASS, not the instance (R10). The defect was a coverage-only claim
    reaching a reader from a dimension nobody had measured for it. So the sweep
    runs over the text a reader ACTUALLY SEES, and any dimension making the
    claim there must carry it in the contract -- which is what puts it under
    the measurement above.

    THE SWEPT TEXT IS THE SUMMARY *AND* THE NOTE, and the first draft of this
    control got that wrong -- it swept the formatter output alone, where the
    phrase does not appear, so it was vacuous on its own headline dimension.
    Its vacuity guard caught it on first run, which is the whole reason the
    guard is there. The NOTE is the surface the ledger and the Proof door
    carry, so a claim reaching a reader there is every bit as published as one
    in the CLI summary."""
    result = _scored()
    rendered = {
        dim: text + " " + str(result[dim].note or "")
        for dim, text in _rendered_dimension_text(result).items()
    }
    for dim, text in rendered.items():
        makes_claim = pair.COVERAGE_ONLY_CLAIM_PHRASE in text
        declared = bool(
            pair.COVERAGE_ONLY_CLAIM_CONTRACT[dim]["claims_coverage_only"])
        if makes_claim:
            assert declared, (
                f"{dim}'s published text tells a reader its two sides differ "
                f"only in coverage ({pair.COVERAGE_ONLY_CLAIM_PHRASE!r}) but "
                "the contract does not declare the claim, so nothing measures "
                "it -- this is the exact shape of the D20 defect")
    # VACUITY: a sweep over text that never contains the phrase would pass on
    # an instrument that had quietly stopped publishing the claim at all.
    assert any(pair.COVERAGE_ONLY_CLAIM_PHRASE in t for t in rendered.values()), (
        "no published dimension makes the coverage-only claim any more -- this "
        "control is now vacuous and either the claim moved or it was dropped")


@pytest.mark.parametrize("label,transform", [
    # (1) the company decides a single observed failure is noise
    ("one failure no longer raises WATCH",
     lambda v: type(v).NORMAL if v is type(v).WATCH else v),
    # (2) the hardship amplification fires on one observation instead of two
    ("hardship amplification 2 -> 1",
     lambda v: type(v).HIGH if v is type(v).ELEVATED else v),
    # (3) the organ raises its HIGH bar
    ("HIGH bar raised",
     lambda v: type(v).ELEVATED if v is type(v).HIGH else v),
])
def test_R15_an_organ_only_rule_drift_breaks_the_coverage_only_residual(
        label, transform, monkeypatch):
    """MUTATE THE SOURCE OF THE CLAIM, not the test's copy of it.

    Each drift changes the COMPANY's own thresholding rule and nothing else --
    no world change, no truth-side change, so the coverage-only claim becomes
    FALSE and the residual must say so. Before this control existed each of
    these moved the published headline (up to 2.9x) while exactly one unrelated
    test fired, blaming a weak permutation probe or an epistemic-wall leak."""
    _organ_drift(monkeypatch, transform)
    cov = pair.measure_coverage_only_residual(n_customers=600, seed=7)

    assert not cov["is_vacuous"], (
        f"{label}: the counterfactual went vacuous, so this mutation proves "
        "nothing about the control")
    claiming = {d: v["residual"] for d, v in cov["residuals"].items()
                if v["claims_coverage_only"]}
    assert any(r != 0 for r in claiming.values()), (
        f"{label}: the company's own severity rule changed with the truth-side "
        f"rule untouched and every coverage-only residual stayed 0 ({claiming})"
        " -- the control cannot see rule divergence, which is the only thing "
        "it exists to see")


# ---------------------------------------------------------------------------
# WHO OWNS THE TRUTH SIDE (atom D21, H27 Expert Hour #5, 2026-08-10)
# ---------------------------------------------------------------------------
# THE DEFECT. The ageing dimension's truth side was
# `company.billing.arrears_engine.age_bucket` -- the company organ's own
# function -- applied to a `days_overdue` the scenario constructs to be the
# same integer the organ computes. Same rule, same input, so the two sides
# could not disagree about the bucket of an invoice they both held open:
# `wrong_bucket` measured 0 at every seed and under every drift tried, by
# construction rather than by luck, and the dimension whose whole subject is
# debt DATING could not see a company dating error at all.
#
# It sat under a COVERAGE_ONLY_CLAIM_CONTRACT exemption reading "two different
# rules, not one rule over two coverages" -- while the module's own docstring
# four hundred lines up said "Both sides use the IDENTICAL bucket function".
# The control believed the exemption, so the one mechanism in the repository
# able to catch the D20 class was switched off for the dimension with the
# strongest mirror of the three.


def test_the_truth_side_of_every_published_dimension_is_harness_owned():
    """THE CLASS CONTROL (R10): no dimension's TRUTH-side labelling rule may be
    owned by `company.*`.

    This is the epistemic wall in the direction nobody checks. The usual
    enforcement is company -> sim: can the company see something a real
    supplier could not? This is harness -> company: the ground truth a
    dimension grades against being computed by the thing it is grading, which
    is R15's TAUTOLOGY pattern (the checked value derived from the source it
    checks).

    INDEPENDENCE: it reads `__module__` off the callable `score_triad` actually
    resolves through `truth_side_rule`, so it is a fact about what ran, not
    about what an author wrote down.

    COMPLETENESS: the dimension set is DERIVED from what is published, the D19
    lesson -- a hand-maintained register skips exactly the entry nobody added.
    """
    published = {k for k, v in _scored().items() if isinstance(v, GapResult)}
    declared = set(pair.TRUTH_SIDE_RULE_OWNERSHIP)
    assert declared == published, (
        f"published dimensions {sorted(published)} but the truth-side "
        f"ownership register declares {sorted(declared)} -- an undeclared "
        "dimension is one this control silently skips while still passing")

    for dim in sorted(published):
        entry = pair.TRUTH_SIDE_RULE_OWNERSHIP[dim]
        assert entry["why"].strip(), f"{dim}: ownership declared with no reason"
        rule = entry["rule"]
        if rule is None:
            # The honest "no labelling rule to own" entry -- spelled out rather
            # than omitted, because an absent entry is how a register fails
            # silent. It must still say what the truth actually is.
            assert entry["labels"].strip(), (
                f"{dim}: declares no rule and does not say what its truth is")
            continue
        owner = rule.__module__
        assert not owner.startswith("company."), (
            f"{dim}: its TRUTH-side labelling rule is `{owner}."
            f"{rule.__name__}` -- the harness is grading the company against "
            "the company's own code, so an edit to that rule moves the ground "
            "truth with it and the dimension certifies the company correct by "
            "definition (R15 tautology). This is the D21 defect exactly")


def test_R15_pointing_the_ageing_truth_rule_at_the_organ_fires_the_control(
        monkeypatch):
    """MUTATE THE SOURCE: put the defect back and the control must fire.

    And the second assertion is the whole reason this control has to be about
    OWNERSHIP rather than about a value: reinstating the defect moves NO
    published number at all, because the two rules are logically identical at
    HEAD. That is why nothing caught it for the instrument's whole life -- no
    number was ever wrong, only unable to become wrong.
    """
    from company.billing.arrears_engine import age_bucket as organ_rule

    before = _scored()["ageing"].components

    monkeypatch.setitem(
        pair.TRUTH_SIDE_RULE_OWNERSHIP["ageing"], "rule", organ_rule)

    with pytest.raises(AssertionError, match="own code"):
        test_the_truth_side_of_every_published_dimension_is_harness_owned()

    after = _scored()["ageing"].components
    for key in ("mean_bucket_displacement", "understated_arrears_rate",
                "overstated_arrears_rate", "misses", "false_ageings",
                "wrong_bucket", "n_truly_overdue", "n_truly_current"):
        assert before[key] == after[key], (
            f"{key} moved when the truth side was pointed back at the organ "
            "-- if a published number CAN see this defect, the ownership "
            "control is not the only thing standing between it and a reader, "
            "and this test's premise needs re-measuring")


def test_R15_an_unregistered_or_ruleless_dimension_cannot_be_scored_silently():
    """The register is the CALL PATH, so the two ways it could fail open --
    a dimension not in it, and a dimension declaring no rule -- must RAISE at
    the point of use rather than fall back to some default."""
    with pytest.raises(KeyError, match="no TRUTH_SIDE_RULE_OWNERSHIP entry"):
        pair.truth_side_rule("a_dimension_nobody_registered")
    # `detection`'s truth is a raw world fact; asking it for a labelling rule
    # means the scorer and the register disagree about what it does.
    with pytest.raises(ValueError, match="raw world fact"):
        pair.truth_side_rule("detection")


@pytest.mark.parametrize("days_overdue", list(range(-5, 121)))
def test_the_truth_side_dating_rule_is_pinned_against_the_organs(days_overdue):
    """The `AGEING_BUCKET_ORDER` discipline, finally applied to the RULE.

    `background.gap_metric` already wrote this down for the bucket ORDER --
    "Redeclared here rather than imported: `background/` is harness code and
    must not take a company import for a constant", pinned against the
    company's so a drift on either side fails loudly -- and the same dimension
    imported the bucket RULE anyway.

    Harness-owned does NOT mean free to drift: the two sides are MEANT to run
    the same rule (that is what makes the residual a coverage measurement).
    What they may not do is run the SAME OBJECT, because then a divergence is
    unrepresentable. So they are pinned, and the pin NAMES the divergence.
    """
    from company.billing.arrears_engine import age_bucket as organ_rule

    harness = pair._ageing_bucket(days_overdue)
    organ = organ_rule(max(0, days_overdue))
    assert harness == organ, (
        f"at {days_overdue} days overdue the harness's truth-side dating rule "
        f"says '{harness}' and the company organ's says '{organ}'. The ageing "
        "dimension's residual is published as pure coverage loss; a rule "
        "divergence makes it a mixture read under the coverage name (atom "
        "D20's defect, in the dimension D21 found it in). Either the organ's "
        "ageing vocabulary changed -- in which case decide whether the "
        "harness's ground truth should follow it, deliberately -- or one of "
        "the two is now wrong")


@pytest.mark.parametrize("seed", [7, 11, 23])
def test_the_ageing_dimension_measures_a_zero_coverage_only_residual(seed):
    """The enrolment's forward half, asserted PER DIMENSION.

    The suite-wide coverage-only test asserts over every dimension that claims
    coverage-only, and the R15 organ-drift test passes on `any()` of them --
    so with `belief` in the set, `ageing` could be enrolled and never actually
    exercised. This names it.
    """
    cov = pair.measure_coverage_only_residual(n_customers=600, seed=seed)
    assert not cov["is_vacuous"], f"vacuous counterfactual: {cov['witnesses']}"
    entry = cov["residuals"]["ageing"]
    assert entry["claims_coverage_only"] is True, (
        "ageing was un-enrolled from the coverage-only control -- it was "
        "exempt on a false premise until D21 and the exemption is what hid "
        "the mirror")
    assert entry["residual"] == 0, (
        f"ageing residual {entry['residual']} survives on the all-DD "
        "counterfactual, where the company observes every failure -- so the "
        "surviving gap is the truth-side dating rule and the organ's dating "
        "rule disagreeing, published under the name of coverage loss")


@pytest.mark.parametrize("seed", [7, 11, 23])
def test_R15_an_organ_only_dating_drift_breaks_the_ageing_residual(
        seed, monkeypatch):
    """The enrolment's reverse half, on the ageing dimension BY NAME.

    An organ-only drift of the 60-day boundary to 75 -- a supplier ageing on
    calendar months -- with the world and the harness's truth-side rule
    untouched. Measured 0.0 -> 0.3627 / 0.3194 / 0.3333 at seeds 7 / 11 / 23.

    HONEST LIMIT, recorded rather than left for a reader to discover: a drift
    that shifts EVERY boundary by 7 days is invisible to this control on this
    book, because `build_scenario` exposes only three distinct ages (30, 51
    and 72 days) and that drift crosses none of their boundaries. The control
    sees a dating drift only where the book has an invoice near the boundary
    that moved. See `test_the_ageing_headline_is_entirely_miss_driven_here`.
    """
    import company.billing.arrears_engine as arrears_engine

    def drifted(days_overdue: int) -> str:
        if days_overdue >= 90:
            return "90+"
        if days_overdue >= 75:
            return "60-90"
        if days_overdue >= 30:
            return "30-60"
        return "current"

    monkeypatch.setattr(arrears_engine, "age_bucket", drifted)

    cov = pair.measure_coverage_only_residual(n_customers=600, seed=seed)
    assert not cov["is_vacuous"], (
        "the counterfactual went vacuous, so this mutation proves nothing")
    assert cov["residuals"]["ageing"]["residual"] != 0, (
        "the company's own dating rule moved its 60-day boundary to 75 with "
        "the truth side untouched, and the ageing residual stayed 0 -- the "
        "dimension cannot see a company dating error, which before D21 it "
        "structurally could not")


@pytest.mark.parametrize("seed", [7, 11, 23])
def test_the_ageing_headline_is_entirely_miss_driven_here(seed):
    """A WITNESS, not a target (R12): record what the ordinal headline is
    actually made of on this book, so no reader takes it for an independent
    second reading of the dimension.

    `mean_bucket_displacement` is published as the measure that "distinguishes
    off-by-one from stone-blind, which an error rate cannot". On this book
    there is no off-by-one to distinguish: `wrong_bucket` is 0, so every unit
    of displacement comes from a MISS -- the same cases
    `understated_arrears_rate` reports, rank-weighted. Before D21 that was true
    BY CONSTRUCTION (one rule, one input). It is now a property of the book and
    of the two rules agreeing, which is a different and checkable thing -- and
    if it ever stops being true, this test says so rather than a reader
    noticing a headline that quietly started measuring something new.
    """
    result = _scored(seed=seed, n=600)
    c = result["ageing"].components
    rank = {b: i for i, b in enumerate(c["bucket_order"])}

    assert c["wrong_bucket"] == 0, (
        f"seed {seed}: {c['wrong_bucket']} truly-overdue invoice(s) are now "
        "dated into the WRONG OVERDUE bucket. That is a real ordinal error, "
        "which this dimension could not previously represent -- the headline "
        "is no longer a rank-weighted miss count and the D21 witness needs "
        "rewriting, not silencing")

    # The arithmetic identity, derived independently of the scorer.
    records, consumer, _ledger, as_of = pair.build_scenario(600, seed=seed)
    ages = {(as_of - r.due_date).days for r in records}
    # ATOM D25 RESHAPED THIS. Until 2026-08-10 the book had exactly THREE debt
    # ages -- every account fell due on the same three dates -- and that made
    # the ageing headline's resolution a property of the harness's calendar.
    # The book is now spread across one billing cycle, so the ages are a
    # CONTIGUOUS span whose ends are still pure arithmetic over the constants.
    lo_age = pair.AS_OF_BUFFER_DAYS
    hi_age = (pair.AS_OF_BUFFER_DAYS
              + pair.PERIOD_SPACING_DAYS * (pair.N_PERIODS - 1)
              + pair.BILLING_CYCLE_SPREAD_DAYS - 1)
    assert ages == set(range(lo_age, hi_age + 1)), (
        f"seed {seed}: the book's debt ages are {sorted(ages)}, not the "
        f"contiguous {lo_age}..{hi_age} the staggered cycle produces. If the "
        "span has holes or has collapsed, the ageing dimension has lost "
        "resolution and `check_ageing_resolution` is the control that says by "
        "how much (atom D25)")
    reachable = {pair._ageing_bucket(d) for d in ages}
    assert reachable == {"30-60", "60-90", "90+"}, (
        f"seed {seed}: the reachable truth-side buckets are {sorted(reachable)}"
        " -- `current` is still never exercised on the truly-overdue side, and "
        "the three that are exercised are what bounds the displacement below")
    # THE CONSEQUENCE, checked rather than described: if every unit of
    # displacement is a miss, and the only reachable truth buckets are 30-60
    # and 60-90, then total displacement must land exactly in
    # [lo x misses, hi x misses], where lo/hi are those buckets' own ranks read
    # off `bucket_order` rather than written in as 1 and 2 -- a re-ordered or
    # re-named bucket space then moves this bound with it instead of leaving a
    # literal that quietly stops matching the dimension it bounds.
    lo = min(rank[b] for b in reachable)
    hi = max(rank[b] for b in reachable)
    total = c["mean_bucket_displacement"] * c["n_truly_overdue"]
    assert lo * c["misses"] - 1e-9 <= total <= hi * c["misses"] + 1e-9, (
        f"seed {seed}: total ordinal displacement {total:.4f} over "
        f"{c['misses']} miss(es) falls outside [{lo} x misses, {hi} x misses] -- the "
        "headline is no longer a rank-weighted restatement of "
        "understated_arrears_rate, so the two published numbers are no longer "
        "the one reading this witness says they are")
    assert (c["misses"] == 0) == (total == 0), (
        f"seed {seed}: misses={c['misses']} but total displacement {total} -- "
        "displacement with no miss, or a miss with no displacement, means the "
        "two are no longer the same cases")


# ---------------------------------------------------------------------------
# THE HEADLINE-DIRECTION CLASS (atom D22, H27 Expert Hour #6, 2026-08-10)
# ---------------------------------------------------------------------------
# The class `DETECTION_DIRECTION_CONTRACT` states -- a one-directional score
# cannot distinguish a precise company from an indiscriminate one -- found for
# the THIRD time somewhere the existing sweeps could not reach. These tests
# MEASURE the new register rather than reading it, and every mutation below
# reinstates a shape in which it would stop covering something.


def _hdc(result=None, contract=None):
    """Measure the register on a real scored result."""
    result = pair.measure(_N, seed=_SEED) if result is None else result
    return result, pair.measure_headline_direction_coverage(result, contract)


@contextlib.contextmanager
def _pre_d22_ageing_scorer():
    """Restore the ONE-DIRECTIONAL ageing headline this register found: `gap`
    taken from the truly-overdue displacement alone.

    Not a hypothetical shape -- it is what `ageing_gap` shipped until 2026-08-10
    and what every gap-ledger entry before that date carries. It is the only
    genuinely one-directional scorer this instrument has ever published, so it
    is what the R15 mutations below use now that no live dimension is blind.
    """
    real = pair.ageing_gap

    def _one_directional(*a, **kw):
        result = real(*a, **kw)
        # BOTH fields move, because on an un-normalised (`none`-kind) measure
        # `raw_gap` IS the headline -- that is what `ageing_gap` actually shipped
        # until 2026-08-10, and D44's construction check now says so. Moving only
        # `gap` would build a mutant no scorer could have written.
        one_way = result.components["mean_bucket_displacement"]
        return dataclasses.replace(result, gap=one_way, raw_gap=one_way)

    pair.ageing_gap = _one_directional
    try:
        yield
    finally:
        pair.ageing_gap = real


def test_the_ageing_headline_now_sees_the_over_ageing_direction():
    """THE FINDING AND ITS FIX (atom D22), pinned as numbers rather than a
    paragraph.

    A company that dates every truly-overdue invoice perfectly and dumps its
    ENTIRE truly-current book into `90+` -- maximal wrongful ageing -- used to
    score the published ageing headline identically to a company that dates
    every invoice right (0.000000, 10,758 cases changed, seeds 7/11/23). It now
    scores 1.5 buckets. Both halves are asserted here: the old shape is still
    exercised, through the pre-D22 scorer, so this test says what CHANGED and
    not merely what is true today.
    """
    result, measured = _hdc()
    row = measured["ageing"]

    assert row["n_cases_changed"] > 0, (
        "the degenerate changed no case at all -- the probe is VACUOUS and "
        "proves nothing in either direction")
    assert row["perfect_gap"] == 0.0
    assert row["degenerate_gap"] == pytest.approx(1.5), (
        "the balanced headline scores maximal wrongful ageing (3 buckets over "
        "the truly-current, 0 over the truly-overdue) at half of 3")
    assert row["distinguishes"] is True

    # THE DEFECT, still exercised: with the pre-D22 headline the same probe on
    # the same population cannot tell them apart at all.
    with _pre_d22_ageing_scorer():
        was = pair.measure_headline_direction_coverage(result)["ageing"]
    assert was["perfect_gap"] == was["degenerate_gap"] == 0.0
    assert was["distinguishes"] is False

    # AND THE OFF-BY-ONE / STONE-BLIND DISTINCTION, which is the claim the
    # ordinal term exists to support, is now available in this direction too:
    # an over-ageing of ONE bucket and one of THREE no longer score the same.
    true_l = list(result["labels"]["ageing_truth"])
    off_by_one = [t if t != "current" else "30-60" for t in true_l]
    stone_blind = [t if t != "current" else "90+" for t in true_l]
    g1 = pair._rescore_dimension("ageing", list(true_l), off_by_one, result)
    g3 = pair._rescore_dimension("ageing", list(true_l), stone_blind, result)
    assert 0.0 < g1 < g3, (
        f"off-by-one over-ageing ({g1}) must score better than stone-blind "
        f"({g3}) and neither may score as a perfect dater")
    with _pre_d22_ageing_scorer():
        was1 = pair._rescore_dimension("ageing", list(true_l), off_by_one, result)
        was3 = pair._rescore_dimension("ageing", list(true_l), stone_blind, result)
    assert was1 == was3 == 0.0


def test_the_register_is_derived_from_what_is_published_not_from_a_list():
    """The keying that let this class escape twice is gone: the sweep's keyset
    IS the published dimension set, so a dimension cannot avoid it by not being
    a detection scorer, by being ordinal, or by being added later."""
    result = pair.measure(_N, seed=_SEED)
    assert set(pair.published_dimensions(result)) == set(
        pair.HEADLINE_DIRECTION_COVERAGE)

    # MUTATION: a dimension published without a register entry must RAISE, not
    # drop silently out of the sweep.
    extra = dict(result)
    extra["a_new_dimension"] = result["ageing"]
    with pytest.raises(ValueError, match="no entry for published dimension"):
        pair.measure_headline_direction_coverage(extra)

    # MUTATION, the other way: a register entry for a dimension nobody
    # publishes reads as coverage that is not being provided.
    ghost = copy.deepcopy(pair.HEADLINE_DIRECTION_COVERAGE)
    ghost["a_retired_dimension"] = dict(ghost["ageing"])
    with pytest.raises(ValueError, match="which `score_triad` does not publish"):
        pair.measure_headline_direction_coverage(result, ghost)


def test_every_declaration_holds_at_head():
    """The control's own verdict, green at HEAD."""
    _result, measured = _hdc()
    assert pair.check_headline_direction_coverage(measured) == []
    # ...and it is DIFFERENTIAL rather than a blanket rule: entries land on
    # both sides. A register where every entry is debt is a blanket ban
    # wearing a register's clothes.
    assert any(v["distinguishes"] for v in measured.values())
    assert any(not v["distinguishes"] for v in measured.values())


def test_a_both_directions_claim_that_is_false_is_caught():
    """R15, direction one: reinstate the defect in the SCORER -- the real
    pre-D22 one-directional ageing headline -- while the register goes on
    declaring both directions, and the control must fire.

    Stronger than the version this replaces, which reinstated the defect as a
    declaration over a scorer that was genuinely blind. Now that D22 has landed,
    nothing this instrument publishes is one-directional, so the mutation has to
    put the blindness back where it actually lived."""
    result, _ = _hdc()
    with _pre_d22_ageing_scorer():
        measured = pair.measure_headline_direction_coverage(result)
    violations = pair.check_headline_direction_coverage(measured)
    assert any("ageing" in v and "BOTH error directions" in v
               for v in violations), violations


def test_a_debt_entry_that_has_been_fixed_must_be_re_derived():
    """R15, direction two: a register entry that outlives the blindness it
    describes misleads worse than none, so declaring a genuinely two-directional
    dimension as debt must also fire."""
    result, _ = _hdc()
    rotted = copy.deepcopy(pair.HEADLINE_DIRECTION_COVERAGE)
    rotted["detection"]["headline_counts_both_directions"] = False
    rotted["detection"]["debt_atom"] = "D_NOT_A_REAL_ATOM"
    measured = pair.measure_headline_direction_coverage(result, rotted)
    violations = pair.check_headline_direction_coverage(measured, rotted)
    assert any("detection" in v and "rotted" in v for v in violations), violations


def test_a_one_directional_entry_must_name_an_owner_or_a_cover():
    """The register's own class statement: measure both directions or NAME the
    atom that will make it. An unowned hole is the third fail-open shape."""
    result, _ = _hdc()
    unowned = copy.deepcopy(pair.HEADLINE_DIRECTION_COVERAGE)
    # The pre-D22 ageing headline, honestly declared one-directional, with
    # nobody named to fix it -- the state the real register was never allowed
    # to be in between the finding and the reshape.
    unowned["ageing"]["headline_counts_both_directions"] = False
    unowned["ageing"]["debt_atom"] = None
    with _pre_d22_ageing_scorer():
        measured = pair.measure_headline_direction_coverage(result, unowned)
    violations = pair.check_headline_direction_coverage(measured, unowned)
    assert any("unowned hole" in v for v in violations), violations


def test_a_cover_claim_is_measured_against_its_sibling():
    """`detection_latency` is honestly truth-conditioned and names the sibling
    that counts the direction it cannot. That is only not a loophole because
    the sibling's behaviour is MEASURED."""
    result, measured = _hdc()
    row = measured["detection_latency"]
    assert row["covered_by"] == "detection"
    assert row["cover_is_two_directional"] is True
    assert row["n_truly_current_in_population"] == 0, (
        "a truly-current case reached the latency population, so the headline "
        "is no longer truth-conditioned and the cover claim no longer holds")
    assert row["probe_bit"] is True, "the latency population is empty"

    # MUTATION: point the cover at a sibling that does NOT count both
    # directions -- a cover claim covering nothing. The sibling has to be
    # genuinely one-directional for this to prove anything, so the pre-D22
    # ageing scorer supplies it.
    bad = copy.deepcopy(pair.HEADLINE_DIRECTION_COVERAGE)
    bad["detection_latency"]["covered_by"] = "ageing"
    with _pre_d22_ageing_scorer():
        m2 = pair.measure_headline_direction_coverage(result, bad)
    assert any("covering nothing" in v
               for v in pair.check_headline_direction_coverage(m2, bad))

    # MUTATION: a cover naming a dimension that does not exist must RAISE.
    ghost = copy.deepcopy(pair.HEADLINE_DIRECTION_COVERAGE)
    ghost["detection_latency"]["covered_by"] = "no_such_dimension"
    with pytest.raises(ValueError, match="not a registered dimension"):
        pair.measure_headline_direction_coverage(result, ghost)


def test_the_latency_population_claim_can_actually_fail():
    """R15 on the conditional-population probe itself: it must fire when a
    truly-current case reaches the latency population, not merely report 0."""
    result, _ = _hdc()
    leaked = dict(result)
    inputs = copy.deepcopy(result["latency_inputs"])
    truly = set(map(tuple, inputs["truly_failed_keys"]))
    intruder = next(k for k in result["labels"]["detection_keys"]
                    if tuple(k) not in truly)
    inputs["recon_lag_days"] = dict(inputs["recon_lag_days"])
    inputs["recon_lag_days"][tuple(intruder)] = 3
    leaked["latency_inputs"] = inputs
    measured = pair.measure_headline_direction_coverage(leaked)
    assert measured["detection_latency"]["n_truly_current_in_population"] == 1
    assert any("no longer truth-conditioned" in v
               for v in pair.check_headline_direction_coverage(measured))


def test_the_probe_has_a_vacuity_guard():
    """A degenerate that changes nothing proves nothing. Without this guard an
    inert strategy would hand a silent PASS to every debt entry -- the exact
    fail-silent shape D19's probe_bit was built for, one register over."""
    result, _ = _hdc()
    inert = dict(pair._DEGENERATE_STRATEGIES)
    inert["age_the_current_book_at_90_plus"] = lambda true_l: list(true_l)
    original = pair._DEGENERATE_STRATEGIES
    try:
        pair._DEGENERATE_STRATEGIES = inert
        measured = pair.measure_headline_direction_coverage(result)
    finally:
        pair._DEGENERATE_STRATEGIES = original
    assert measured["ageing"]["probe_bit"] is False
    assert any("VACUOUS" in v
               for v in pair.check_headline_direction_coverage(measured))


def test_a_declared_strategy_that_does_not_exist_raises():
    """The register names the strategy that RUNS (the D19 call-path lesson): a
    declaration pointing at no code must raise rather than skip."""
    result, _ = _hdc()
    bad = copy.deepcopy(pair.HEADLINE_DIRECTION_COVERAGE)
    bad["ageing"]["degenerate"] = "a_strategy_nobody_wrote"
    with pytest.raises(ValueError, match="not in `_DEGENERATE_STRATEGIES`"):
        pair.measure_headline_direction_coverage(result, bad)


def test_the_over_ageing_term_is_half_the_headline_at_source():
    """Reshaped AT SOURCE in `gap_metric.ageing_gap` (atom D22), so every caller
    of the scorer gets it -- not only the pair whose Expert Hour found it (the
    D19 pattern). The direction the old headline could not see must now move
    it, and must still be readable on its own."""
    truth = ["current"] * 8 + ["30-60", "60-90"]
    right = list(truth)
    over_by_one = ["30-60"] * 8 + ["30-60", "60-90"]
    over_stone_blind = ["90+"] * 8 + ["30-60", "60-90"]

    c_right = ageing_gap(truth, right).components
    c_one = ageing_gap(truth, over_by_one).components
    c_blind = ageing_gap(truth, over_stone_blind).components

    # The OLD headline was blind to all three differences -- the term is still
    # published, and still one-directional, which is why it is no longer the
    # headline.
    assert (c_right["mean_bucket_displacement"]
            == c_one["mean_bucket_displacement"]
            == c_blind["mean_bucket_displacement"] == 0.0)
    # ...and the rate cannot separate the last two either.
    assert c_one["overstated_arrears_rate"] == c_blind["overstated_arrears_rate"]
    # The over-ageing term is what does, and it is half the headline now.
    assert c_right["mean_overstatement_displacement"] == 0.0
    assert c_one["mean_overstatement_displacement"] == 1.0
    assert c_blind["mean_overstatement_displacement"] == 3.0
    assert c_right["balanced_bucket_displacement"] == 0.0
    assert c_one["balanced_bucket_displacement"] == pytest.approx(0.5)
    assert c_blind["balanced_bucket_displacement"] == pytest.approx(1.5)
    assert c_one["n_overaged_beyond_one_bucket"] == 0
    assert c_blind["n_overaged_beyond_one_bucket"] == 8
    assert c_blind["max_overstatement_displacement"] == 3

    # VACUITY IS EXPLICIT, never 0.0: with no truly-current population the
    # over-ageing term is undefined -- and so is the headline, rather than
    # falling back to the half that is defined.
    vac = ageing_gap(["30-60", "60-90"], ["30-60", "60-90"])
    assert vac.components["mean_overstatement_displacement"] is None
    assert vac.gap is None
    assert "UNKNOWN" in vac.components["ordinal_direction_caveat"]


def test_the_ordinal_direction_caveat_is_published_where_a_reader_sees_it():
    """The D7 anti-decay mechanism applied to the reshaped headline: no consumer
    prints it without both of its halves, and no ledger reader can diff a
    pre-D22 entry against a later one without being told they differ."""
    from background.gap_metric import format_ageing_summary

    result = ageing_gap(["current"] * 5 + ["30-60"], ["90+"] * 5 + ["30-60"])
    caveat = result.components["ordinal_direction_caveat"]
    assert "atom D22" in caveat
    assert "TRULY-OVERDUE" in caveat
    assert "not comparable with this headline" in caveat
    summary = format_ageing_summary(result)
    assert "mean_overstatement_displacement" in summary, (
        "the headline is printable without the direction it used not to see -- "
        "the exact shape that let a bare ageing scalar be misread twice")
    assert "BALANCED over both directions" in summary


def test_the_headline_direction_control_runs_in_the_cli_not_only_in_tests():
    """A control that lives only in the test suite is one a reader of the
    instrument's own output never meets -- the same reason the permutation
    control prints every run."""
    src = inspect.getsource(pair.main)
    assert "measure_headline_direction_coverage(result)" in src
    assert "check_headline_direction_coverage" in src


# ---------------------------------------------------------------------------
# ORGAN_QUERY_GRID -- can this instrument RESOLVE what it publishes? (atom D23,
# H27 Expert Hour #7, 2026-08-10). The class: a harness reading taken by asking
# the company's organ on a grid of candidate dates the HARNESS built from the
# organ's own rule is QUANTISED TO THAT GRID, and the resolution is a property
# of the harness, not of the company being graded.
# ---------------------------------------------------------------------------

_GRID_N = 300      # the grid probe re-scores the population once per drift


def test_the_organ_query_grid_register_is_measured_not_asserted():
    """Every declaration in `ORGAN_QUERY_GRID` re-derived from a fresh
    measurement each run. Green at HEAD means the declared blindness is the
    blindness the code has -- not that there is none."""
    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7)
    assert pair.check_organ_query_grid_resolution(measured) == []
    assert set(measured) == set(pair.ORGAN_QUERY_GRID)
    assert all(row["probe_bit"] for row in measured.values()), (
        "an inert drift probe hands every invisibility declaration a free pass")


@pytest.mark.parametrize("seed", (7, 11, 23))
def test_the_latency_arm_resolves_the_company_to_the_day(seed):
    """THE RESHAPE (atom D23). A company whose reconciliation detector runs one
    day faster publishes a first-knowledge arm one day earlier, and one running
    a day slower publishes it one day later -- because the organ is now asked on
    a DAILY grid from the invoice's issue date rather than at the harness's own
    `due + grace` alone.

    This replaces the characterization test that pinned the defect. That one had
    to fail when D23 landed, and this is the re-derivation it demanded: the same
    quantity, asserted from the other side."""
    read = {
        k: pair.measure(n_customers=_GRID_N, seed=seed,
                        organ_reconciliation_drift_days=k
                        )["detection_latency"].components[
                            "mean_lag_days_without_dd_channel"]
        for k in (-1, 0, 1, 7)
    }
    assert read[0] == float(pair.DEFAULT_RECONCILIATION_GRACE_DAYS)
    assert read[-1] == read[0] - 1, (
        "a one-day-FASTER company must publish one day earlier -- the "
        "direction the old grid could not see at all")
    assert read[1] == read[0] + 1, (
        "a one-day-SLOWER company must publish one day later, not a "
        "PERIOD_SPACING_DAYS step")
    assert read[7] == read[0] + 7, (
        "+1 / +7 must be different numbers -- they were one number on the "
        "one-candidate-per-period grid")


def test_the_grid_is_daily_from_the_issue_date_to_as_of():
    """The mechanism the day-for-day resolution rests on, asserted at its
    source: consecutive days, floored at the invoice's own issue date (the
    earliest a supplier can know it billed), ceilinged at `as_of`."""
    import datetime as _dt

    records, _consumer, _book, as_of = pair.build_scenario(2, seed=7)
    periods = [r for r in records if r.customer_id == records[0].customer_id]
    dates = pair.organ_query_dates(periods, as_of)
    assert dates[0] == min(r.issue_date for r in periods)
    assert dates[-1] == as_of
    assert len(dates) == (dates[-1] - dates[0]).days + 1, "not a DAILY grid"
    assert len(set(dates)) == len(dates)
    # The bound is the COMPANY's: it cannot know an unissued bill went unpaid.
    assert pair.organ_query_dates(periods, dates[0] - _dt.timedelta(days=1)) == []


def test_no_case_leaves_the_latency_population_for_want_of_a_candidate():
    """The coarse grid's other casualty: the LAST period had no later candidate,
    so a slower company's cases fell out of the population entirely rather than
    being dated (undated 0 -> 59 at seed 7). A grid running to `as_of` cannot do
    that, and the witness says so rather than a comment claiming it."""
    for drift in (0, 1, 7):
        comps = pair.measure(
            n_customers=_GRID_N, seed=7,
            organ_reconciliation_drift_days=drift)["detection_latency"].components
        assert comps["n_recon_detected_undated"] == 0, (
            f"a {drift:+d}d company has cases reconciliation reports at `as_of` "
            "but at no candidate date -- the grid has holes in it")


def test_the_floor_witness_counts_the_readings_that_are_at_or_before():
    """`n_recon_dated_at_issue_floor` is the honest half of the residual: a case
    first known on the invoice's own ISSUE date is 'at or before', never exact,
    because nothing exists to reconcile until the invoice is issued. Zero on the
    shipped organ, the whole population on one at the floor -- so it is a
    reading, not a constant.

    RE-DERIVED 2026-08-10 (atom D24): this used to say the floor was the organ's
    clamped `days_overdue`. It is not, any more -- the clock is signed and a -15d
    company is now dated 10 days BEFORE the due date without touching this
    witness. What saturates it is a detector reaching past the invoice's own
    existence, which is the bound this witness now carries the evidence for in
    `ORGAN_QUERY_GRID`'s ownership records."""
    shipped = pair.measure(n_customers=_GRID_N, seed=7
                           )["detection_latency"].components
    assert shipped["n_recon_dated_at_issue_floor"] == 0
    floored = pair.measure(
        n_customers=_GRID_N, seed=7,
        organ_reconciliation_drift_days=-20)["detection_latency"].components
    assert floored["n_recon_dated_at_issue_floor"] == floored[
        "n_latency_population"] > 0


def test_the_grid_control_fires_when_the_drift_goes_inert():
    """R15, mutating the PROBE: a counterfactual company that is not actually
    drifted would silently confirm every invisibility declaration. The vacuity
    guard must catch it, and the diagnostic must name the probe rather than the
    reading."""
    frozen = pair.measure(n_customers=_GRID_N, seed=7)
    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, runner=lambda k: frozen)
    violations = pair.check_organ_query_grid_resolution(measured)
    assert violations
    assert any("moved NOTHING anywhere" in v for v in violations)
    assert any("declared VISIBLE but left the reading" in v for v in violations)


def test_the_grid_control_fires_when_the_grid_goes_coarse_again():
    """R15, the regression direction: put the PRE-D23 grid back -- every
    improvement reads the `grace` parameter, a +1d company reads +21 -- and the
    re-derived register must fail by name rather than quietly re-describing a
    coarser instrument.

    This is the mutation the finding said no test in the repository had: seven
    tests fired on a +1d organ drift and not one named latency."""
    real = {k: pair.measure(n_customers=_GRID_N, seed=7,
                            organ_reconciliation_drift_days=k)
            for k in (-20, -5, -1, 0, 1, 7)}

    def coarse_grid(k):
        """One candidate per period at `due + grace`: improvements invisible,
        degradation quantised to PERIOD_SPACING_DAYS."""
        result = copy.deepcopy(real[0])
        lat = result["detection_latency"]
        comps = dict(lat.components)
        comps["mean_lag_days_without_dd_channel"] = float(
            pair.DEFAULT_RECONCILIATION_GRACE_DAYS
            + (pair.PERIOD_SPACING_DAYS if k > 0 else 0))
        result["detection_latency"] = dataclasses.replace(lat, components=comps)
        det = result["detection"]
        result["detection"] = dataclasses.replace(
            det, gap=det.gap + (0.01 if k > 0 else 0.0))
        return result

    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, runner=coarse_grid)
    violations = pair.check_organ_query_grid_resolution(measured)
    assert violations
    assert any("declared VISIBLE but left the reading" in v for v in violations), (
        "-1d is declared visible; a coarse grid leaves it at the baseline")
    assert any("published as 21.0 days, not the declared 1.0" in v
               for v in violations), (
        "the resolution pin is what keeps the published caveat honest")


def test_the_grid_control_fires_when_the_ORGANS_CLOCK_IS_RE_CLAMPED():
    """R15 on the REAL organ, and the direction this register could not check
    until D24 landed.

    Until 2026-08-10 this test simulated the D24 repair with a hand-built runner
    and asserted the then-declared collapse failed as a stale debt. The repair
    is real now, so the mutation is its REVERSION: put `max(0, days)` back into
    `company.billing.arrears_engine.age_open_items` -- the exact code that
    shipped -- and re-score the same population through the same probe.

    A `collapsed_pairs` rule structurally cannot catch this: a collapse rule
    fires when a residual is FIXED. `distinct_pairs` is the declaration that
    fires when a fix is UNDONE, and it must name whose repair it was."""
    def clamped(ledger, as_of, payment_terms_days=14, disputed_refs=()):
        """The organ exactly as it shipped before D24."""
        return [dataclasses.replace(it, days_overdue=max(0, it.days_overdue))
                for it in arrears_engine.age_open_items(
                    ledger, as_of, payment_terms_days, disputed_refs)]
    with mock.patch.object(payment_observation_consumer, "age_open_items", clamped):
        measured = pair.measure_organ_query_grid_resolution(
            n_customers=_GRID_N, seed=7)
    violations = pair.check_organ_query_grid_resolution(measured)
    assert violations
    assert any("declared DISTINCT" in v for v in violations), (
        "-5d and -20d are fifteen days apart; a re-clamped organ publishes one "
        "number for both and nothing else in this register notices"
    )
    assert any(pair.ORGAN_CLOCK_REPAIR_ATOM in v for v in violations), (
        "a reversion must name whose repair it reverted")


def test_a_company_knowledge_bound_that_is_not_at_the_floor_is_refused():
    """R15, mutating the REGISTER: "no atom can close this" is the one claim in
    a register that must never be takeable on trust. A pair collapsing anywhere
    OTHER than the company's own knowledge floor is a DEBT, and the witness --
    the whole population dated at the invoice's issue date -- is what tells them
    apart.

    The mutation moves the declared bound onto a pair that does collapse (+1d
    and +1d read alike trivially) but is nowhere near the floor."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    entry = register["recon_lag_days"]
    entry["collapsed_pairs"] = ((1, 1),)
    entry["distinct_pairs"] = ()
    entry["residual_ownership"] = {
        (1, 1): dict(entry["residual_ownership"][(-20, -30)]),
    }
    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, register=register)
    violations = pair.check_organ_query_grid_resolution(measured, register=register)
    assert any("DEBT wearing a bound's clothes" in v for v in violations)


def test_a_reading_shape_bound_the_sibling_is_blind_to_is_refused():
    """R15, the other ownership kind: "this READING cannot express it" is only
    true if some other reading CAN. The witness is the sibling entry on the same
    grid and the same population -- and if the sibling is blind to the same
    thing, the instrument has gone dead and calling it a property of the reading
    would launder that.

    The mutation points the set entry's shape-bound at a drift the DATE reading
    cannot see either."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    date_entry, set_entry = register["recon_lag_days"], register["flagged_via_reconciliation"]
    # A drift the date reading is blind to as well: zero drift is the baseline,
    # so neither reading moves on it.
    date_entry["visible_drifts"] = (-1,)
    set_entry["invisible_drifts"] = (2,)
    set_entry["residual_ownership"] = {
        2: dict(set_entry["residual_ownership"][1]),
        (-15, -20): set_entry["residual_ownership"][(-15, -20)],
        (-20, -30): set_entry["residual_ownership"][(-20, -30)],
    }

    def blind_sibling(k):
        """Both readings frozen at the baseline for the +2d company."""
        return pair.measure(
            n_customers=_GRID_N, seed=7,
            organ_reconciliation_drift_days=(0 if k == 2 else k))

    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, register=register, runner=blind_sibling)
    violations = pair.check_organ_query_grid_resolution(measured, register=register)
    assert any("dead instrument, not a shape" in v for v in violations)


def test_a_declared_collapse_that_sits_on_the_baseline_is_refused():
    """R15, mutating the REGISTER: `collapsed_pairs` is the falsifiable residual
    that replaced `invisible_drifts` on the date reading, so it must not be
    satisfiable by a pair that simply does not move. Two drifts reading the
    BASELINE are an invisibility -- checked by the rule written for
    invisibilities -- and a register allowed to launder one as the other could
    claim a residual it does not have."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    register["recon_lag_days"]["collapsed_pairs"] = ((99, 98),)
    frozen = pair.measure(n_customers=_GRID_N, seed=7)
    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, register=register,
        runner=lambda k: (frozen if k in (98, 99)
                          else pair.measure(n_customers=_GRID_N, seed=7,
                                            organ_reconciliation_drift_days=k)))
    violations = pair.check_organ_query_grid_resolution(measured, register=register)
    assert any("that is an INVISIBILITY, not a collapse" in v for v in violations)


def test_an_entry_declaring_no_residual_at_all_is_refused():
    """R15, the vacuity guard from the other end. The pre-reshape rule was 'not
    all-invisible'; the reshape needs its mirror, because an entry that declares
    nothing it cannot see is a register that cannot fail."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    register["recon_lag_days"]["invisible_drifts"] = ()
    register["recon_lag_days"]["collapsed_pairs"] = ()
    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, register=register)
    violations = pair.check_organ_query_grid_resolution(measured, register=register)
    assert any("declares NO invisibility and NO collapse" in v for v in violations)


def test_the_grid_register_cannot_declare_a_blindness_with_no_owner():
    """R15, mutating the REGISTER: an unowned blindness is a hole nobody has
    promised to close -- or, since D24, one nobody has explained why nobody can.

    RE-DERIVED 2026-08-10: this used to blank `debt_atom`, which was the only
    ownership shape the register had. Both entries now carry `debt_atom: None`
    honestly, because what is left is a bound rather than a debt, so the
    mutation is to strip the OWNERSHIP RECORD instead. Every declared residual
    must say which kind it is."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    register["recon_lag_days"]["debt_atom"] = None
    register["recon_lag_days"]["residual_ownership"] = {}
    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, register=register)
    violations = pair.check_organ_query_grid_resolution(measured, register=register)
    assert any("no `debt_atom` and no ownership record" in v for v in violations)


def test_every_declared_residual_in_the_shipped_register_is_owned():
    """The register's own shape, asserted rather than assumed: every residual it
    declares carries an ownership record, and every record is a kind the control
    can put on trial. A kind nothing checks is worse than none."""
    checkable = {"debt", "company_knowledge", "reading_shape"}
    for name, entry in pair.ORGAN_QUERY_GRID.items():
        owned = entry["residual_ownership"]
        declared = (list(entry["invisible_drifts"])
                    + list(entry["collapsed_pairs"]))
        assert declared, name
        for res in declared:
            assert res in owned, f"{name}: residual {res!r} is unowned"
            assert owned[res]["kind"] in checkable, f"{name}: {res!r}"
            if owned[res]["kind"] == "debt":
                assert owned[res].get("atom"), f"{name}: {res!r}"


def test_the_grid_register_is_differential_not_a_blanket_claim():
    """Every entry declares BOTH a residual it cannot resolve (an invisibility
    or a collapse) and a drift it must see: an all-invisible register is a
    blanket blindness claim wearing a register's clothes, and an all-visible one
    could not fail on the defect it was built for (the DIMENSION_AS_OF_CONTRACT
    lesson this instrument has now learned four times)."""
    for name, entry in pair.ORGAN_QUERY_GRID.items():
        assert entry["invisible_drifts"] or entry["collapsed_pairs"], name
        assert entry["visible_drifts"], name
    kinds = {e["reading"] for e in pair.ORGAN_QUERY_GRID.values()}
    assert kinds == {"date", "set_membership"}, (
        "the set-membership entry is what makes this a finding about the GRID "
        "rather than about the latency formula")


def test_the_two_readings_part_company_where_the_reshape_put_them():
    """The register earns 'differential' by the two entries DISAGREEING, and
    after D23 they disagree in a way that localises what is left. A +1d company
    moves the DATE reading by a day and leaves the SET reading untouched -- a
    set is not a clock -- while both COLLAPSE together at the organ's zero-floor.
    A residual binding a reading with no days in it is the organ's, not the
    grid's, which is the whole reason D24 owns it rather than this module."""
    assert 1 in pair.ORGAN_QUERY_GRID["recon_lag_days"]["visible_drifts"]
    assert 1 in pair.ORGAN_QUERY_GRID["flagged_via_reconciliation"][
        "invisible_drifts"]
    shared = (set(pair.ORGAN_QUERY_GRID["recon_lag_days"]["collapsed_pairs"])
              & set(pair.ORGAN_QUERY_GRID["flagged_via_reconciliation"][
                  "collapsed_pairs"]))
    assert shared, "the shared collapse is the evidence the floor is the organ's"

    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7)
    assert 1 in measured["recon_lag_days"]["moved"]
    assert 1 in measured["flagged_via_reconciliation"]["unmoved"]
    for name in measured:
        for pair_key in shared:
            assert measured[name]["collapses"][pair_key]["collapsed"]


def test_the_grid_resolution_caveat_travels_with_the_number():
    """The caveat is stamped AT SOURCE in `detection_latency_gap`, so it reaches
    every coupled pair calling this scorer -- not only the one whose Hour found
    it -- and its step is INTERPOLATED from the register, never retyped."""
    result = pair.detection_latency_gap(
        {("c", 0): 1}, {("c", 0): 5}, n_true_failures=1)
    caveat = result.components["organ_query_grid_caveat"]
    assert "atom D23" in caveat
    assert "DAILY grid" in caveat
    assert "1.0 days" in caveat
    assert "atom D24" in caveat, (
        "the caveat must carry the residual it still has, not only the one it "
        "closed")
    assert result.components["organ_improvement_is_visible"] is True
    assert result.components["organ_query_grid_step_days"] == 1.0
    # READ FROM the register, never retyped: flipping the register flips the
    # published claim, so the two cannot drift apart the way a prose caveat did.
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    register["recon_lag_days"]["visible_drifts"] = (1,)
    with mock.patch.object(pair, "ORGAN_QUERY_GRID", register):
        blinded = pair.detection_latency_gap(
            {("c", 0): 1}, {("c", 0): 5}, n_true_failures=1)
    assert blinded.components["organ_improvement_is_visible"] is False


def test_the_grid_resolution_control_runs_in_the_cli_not_only_in_tests():
    """Same reason as the direction control: the reader about to quote a latency
    in days is exactly the one who needs to be told what it can resolve."""
    src = inspect.getsource(pair.main)
    assert "measure_organ_query_grid_resolution(" in src
    assert "check_organ_query_grid_resolution" in src


# ---------------------------------------------------------------------------
# DIMENSION_DRIFT_RESOLUTION -- how wrong must the company be before each
# published headline notices? (atom D25, H27 Expert Hour #8, 2026-08-10)
#
# One keying wider than D23's register, which asked this of the two readings
# off the reconciliation candidate grid alone. The ageing dimension's grid is
# not made of dates: it is where this population's invoices SIT relative to the
# 30/60/90 boundaries, and that placement is built from harness constants.
# ---------------------------------------------------------------------------

_RES_N = 300


@pytest.fixture(scope="module")
def drift_resolution():
    """Measured ONCE for the module: the sweep re-scores three populations
    against every declared counterfactual company, and every register mutation
    below is a trial of a DECLARATION against this same measurement."""
    return pair.measure_dimension_drift_resolution(n_customers=_RES_N)


def test_the_drift_resolution_register_is_measured_not_asserted(drift_resolution):
    """Every declaration re-derived from a fresh measurement each run. Green
    means the declared blindness is the blindness the code has -- not that
    there is none."""
    assert pair.check_dimension_drift_resolution(drift_resolution) == []
    assert set(drift_resolution) == set(pair.DIMENSION_DRIFT_RESOLUTION)
    assert all(row["probe_bit"] for row in drift_resolution.values()), (
        "an inert counterfactual company hands every invisibility a free pass")


def test_the_ageing_headline_now_sees_the_week_of_over_ageing_it_could_not(
        drift_resolution):
    """THE ATOM D25 DELIVERABLE, on the drifts that named it. A supplier dating
    every debt one to eight days OLDER than the world did -- over-ageing, the
    direction that posts an early dunning letter -- published a BIT-IDENTICAL
    ageing headline on the flat book. On the staggered book every one of the
    four drifts that band and its collapse were built from moves the reading,
    on every seed.

    The drifts stay declared as `visible_drifts` rather than being dropped once
    fixed, so a future flattening of the book fails HERE, by name, instead of
    quietly narrowing the caveat."""
    row = drift_resolution["ageing"]
    band = tuple(pair.DIMENSION_DRIFT_RESOLUTION["ageing"]["visible_drifts"])
    assert set(band) >= {-8, -1, 1, 12}, (
        "the four drifts the flat book could not tell apart are the band this "
        "atom exists to have made visible; dropping one from the register "
        "removes the only thing that would catch its return")
    assert tuple(pair.DIMENSION_DRIFT_RESOLUTION["ageing"]
                 ["invisible_drifts"]) == ()
    assert row["unmoved"] == []
    for k in band:
        assert k in row["moved"], k
        for s in row["seeds"]:
            assert (row["by_seed"][s]["by_drift"][k]
                    != row["by_seed"][s]["baseline"]), (s, k)


def test_the_ageing_reading_no_longer_collapses_in_the_other_direction(
        drift_resolution):
    """The other half of the flat book's defect: a company one day out and one
    twelve days out published ONE number, so a movement could not be read as
    days in either direction. They are now distinct readings on every seed."""
    row = drift_resolution["ageing"]
    assert tuple(pair.DIMENSION_DRIFT_RESOLUTION["ageing"]
                 ["collapsed_pairs"] or ()) == ()
    got = pair._collapse_state(row, (1, 12))
    assert got is not None and not got["collapsed"], got


def test_the_book_is_spread_across_the_billing_cycle_not_three_dates():
    """WHY it can now see it, asserted rather than narrated. The flat book put
    every truly-overdue invoice at 30, 51 or 72 days overdue -- three distances,
    all arithmetic over the harness's own constants -- so a dating error was
    visible only where it carried an invoice across a 30/60/90 boundary. The
    staggered book spans those boundaries continuously.

    Measured on BOTH books through the same declared parameter, so this is a
    differential and not an assertion about the shipped one."""
    flat, _c, _l, flat_as_of = pair.build_scenario(
        120, seed=7, cycle_spread_days=1)
    flat_ages = {(flat_as_of - r.due_date).days
                 for r in flat if r.result == "failed"}
    assert flat_ages == {
        pair.AS_OF_BUFFER_DAYS + pair.PERIOD_SPACING_DAYS * i
        for i in range(pair.N_PERIODS)
    } == {30, 51, 72}

    records, _consumer, _ledger, as_of = pair.build_scenario(300, seed=7)
    ages = sorted({(as_of - r.due_date).days
                   for r in records if r.result == "failed"})
    assert len(ages) > 3 * len(flat_ages)

    # The property that actually buys the resolution, and it is a property of
    # SOME boundary rather than of every one: a one-day dating error is visible
    # as soon as ONE invoice sits within a day of a boundary the rule has --
    # which is exactly what the predictor minimises over. Boundaries are
    # derived from the rule, never retyped.
    bounds = pair.ageing_bucket_boundaries()
    assert any(b in ages for b in bounds), (
        f"no invoice in {ages} sits ON any of the {bounds} boundaries, so one "
        "day of UNDER-ageing carries nothing across")
    assert any(b - 1 in ages for b in bounds), (
        f"no invoice in {ages} sits one day BELOW any of the {bounds} "
        "boundaries, so one day of OVER-ageing carries nothing across -- the "
        "flat book's defect exactly")


def test_the_two_dimensions_no_longer_share_a_blind_direction(drift_resolution):
    """The DIFFERENTIAL, kept and re-derived. Before D25 the same one-day
    company error was seen by exactly ONE of `ageing`/`detection` in each
    direction, which is what localised the defect to the population's
    placement rather than to one formula. The placement is fixed, so `ageing`
    now sees both directions while `detection` -- whose blindness is its GRACE
    LINE, not the bucket grid -- is unchanged. A reader must still not take
    either headline as covering the other (the D16 rule)."""
    assert 1 in drift_resolution["ageing"]["moved"]
    assert -1 in drift_resolution["ageing"]["moved"]
    # Unchanged by the reshape, and it must be: every invoice here is 30+ days
    # overdue, so holding terms one day LONGER still finds all of them past
    # grace. This is the register's remaining on-path-and-BLIND entry, without
    # which the differential check would have nothing to hold.
    assert 1 in drift_resolution["detection"]["unmoved"]
    assert -1 in drift_resolution["detection"]["moved"]


def test_the_off_path_dimensions_are_exercised_not_merely_exempt(drift_resolution):
    """`belief` and `belief_population_mix` cannot be reached by a terms drift
    at all -- their organ counts observed FAILURE EVENTS and never reads the
    ledger's dating. That is the exemption shape D21 hid behind, so the
    register makes each name a probe that DOES move it, and the sweep measures
    that probe rather than believing the declaration."""
    for dim in ("belief", "belief_population_mix"):
        assert drift_resolution[dim]["moved"] == []
        assert pair.DIMENSION_DRIFT_RESOLUTION[dim]["exercised_by"]
        assert drift_resolution[dim]["exercised"] is True
    src = inspect.getsource(pair.PaymentObservationConsumer._arrears_risk_belief)
    assert "days_overdue" not in src and "aged" not in src, (
        "the off-path claim is about this organ's inputs; if it starts reading "
        "the ledger's dating the register entry is a lie")


@pytest.mark.parametrize("mutate,expected", (
    (lambda r: r["detection"].__setitem__("invisible_drifts", ()),
     "understates the blindness"),
    (lambda r: r["detection"].__setitem__("visible_drifts", (-1, 1)),
     "blinder than this register admits"),
    # THE POST-D25 ROT, and the one this atom adds: the register going back to
    # claiming the ageing headline cannot see a drift it now sees. An entry
    # that outlives its debt misleads worse than no entry at all.
    (lambda r: (r["ageing"].__setitem__("invisible_drifts", (-1,)),
                r["ageing"].__setitem__("debt_atom", "D25_x")),
     "declared INVISIBLE but moved the reading"),
    (lambda r: r["ageing"].__setitem__("collapsed_pairs", ((1, 99),)),
     "readings nobody took"),
    (lambda r: (r["belief"].__setitem__("in_causal_path", True),
                r["belief"].__setitem__("collapsed_pairs", ((-1, 1),)),
                r["belief"].__setitem__("debt_atom", "D25_x")),
     "INVISIBILITY, not a collapse"),
    (lambda r: r["detection"].__setitem__("debt_atom", None),
     "unowned hole"),
    (lambda r: (r["belief"].__setitem__("in_causal_path", True),
                r["belief"].__setitem__("visible_drifts", (1,))),
     "blinder than this register admits"),
    (lambda r: r["belief"].pop("exercised_by"),
     "unfalsifiable, not exempt"),
    (lambda r: (r["detection_latency"].__setitem__("invisible_drifts", (1,)),
                r["detection_latency"].__setitem__("debt_atom", "D25_x"),
                r["ageing"].__setitem__("invisible_drifts", (-1,)),
                r["ageing"].__setitem__("debt_atom", "D25_x")),
     "no on-path and SIGHTED entry"),
    # The mirror of the one above, and it only became reachable when D25 made
    # a second entry sighted: a register with nothing blind left is as much a
    # blanket claim as one with nothing sighted.
    (lambda r: (r["detection"].__setitem__("invisible_drifts", ()),
                r["detection"].__setitem__("debt_atom", None)),
     "no on-path and BLIND entry"),
))
def test_a_lying_resolution_declaration_fires_by_name(drift_resolution, mutate,
                                                      expected):
    """R15 BOTH WAYS on the register itself. Each mutation is a way this
    register could stop describing the code -- an understated band (which the
    caveat interpolates), an overstated sight, a debt entry that outlived its
    debt, a collapse checked against readings nobody took, a collapse that is
    really an invisibility, an unowned hole, a rotted off-path claim, a
    believed exemption, and an all-blind or all-sighted register that would
    pass whatever the instrument did."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    mutate(register)
    violations = pair.check_dimension_drift_resolution(
        drift_resolution, register=register)
    assert any(expected in v for v in violations), violations


def test_a_dimension_with_no_entry_raises_rather_than_passing(drift_resolution):
    """The keyset is DERIVED from what `score_triad` publishes, in both
    directions: a published dimension nothing sweeps is exactly how this class
    escaped the register before it, and an entry nobody publishes reads like a
    clean one."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    register.pop("ageing")
    with pytest.raises(AssertionError, match="no DIMENSION_DRIFT_RESOLUTION"):
        pair.check_dimension_drift_resolution(drift_resolution, register=register)
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    register["invented_dimension"] = dict(register["ageing"])
    with pytest.raises(AssertionError, match="nobody publishes"):
        pair.check_dimension_drift_resolution(drift_resolution, register=register)


def test_an_inert_counterfactual_company_is_not_a_pass():
    """THE VACUITY GUARD, on the probe rather than on the instrument: a drift
    parameter that had silently stopped drifting would hand every invisibility
    declaration a free pass -- the fail-silent shape this instrument has now
    produced six times, twice inside the control written to close the previous
    one."""
    inert = pair.measure_dimension_drift_resolution(
        n_customers=120, seeds=(7,),
        runner=lambda s, k: pair.measure(n_customers=120, seed=s))
    assert all(not row["probe_bit"] for row in inert.values())
    violations = pair.check_dimension_drift_resolution(inert)
    assert any("moved NOTHING anywhere" in v for v in violations), violations


def test_the_terms_drift_reaches_the_company_and_not_the_world():
    """The counterfactual is a second COMPANY over ONE world (R13), and it is a
    DECLARED `score_triad` parameter rather than a test monkeypatch (the D20
    rule: a counterfactual a reader cannot find in the repo is not part of the
    design). The truth side is untouched, so every movement under it is the
    company's dating moving."""
    records, consumer, _ledger, as_of = pair.build_scenario(120, seed=7)
    base = pair.score_triad(records, consumer, as_of)
    drifted = pair.score_triad(records, consumer, as_of,
                               organ_terms_drift_days=-9)
    assert drifted["ageing"].gap != base["ageing"].gap
    # The world's own records are the same objects, unmutated.
    assert [(r.customer_id, r.due_date, r.result) for r in records] == [
        (r.customer_id, r.due_date, r.result) for r in records]
    assert base["stats"]["n_true_failures"] == drifted["stats"]["n_true_failures"]
    assert base["stats"]["as_of"] == drifted["stats"]["as_of"]
    assert "organ_terms_drift_days" in inspect.signature(
        pair.score_triad).parameters


# ---------------------------------------------------------------------------
# THE GRID THE REGISTER DID NOT CHOOSE
# (atom D28_the_detection_gap_is_quantised_by_this_books_placement,
#  H27 Expert Hour #10)
# ---------------------------------------------------------------------------
# The register above DERIVES ITS KEYSET from what `score_triad` publishes and
# built its GRID from its own declarations, so the exactness rule was applied
# exactly where the band had already answered. On a grid derived from the BOOK
# the detection dimension turns out to saturate in BOTH tails.
# ---------------------------------------------------------------------------


def test_the_resolution_grid_is_derived_from_the_book_not_the_register():
    """THE ATOM D28 FIX, at its source. `dense_drift_grid` must be computable
    from the scenario calendar alone -- if its code can reach
    `DIMENSION_DRIFT_RESOLUTION` then the register is again choosing where it
    gets asked, which is the defect and not a style point.

    The declared drifts stay UNIONED into the swept set (a declaration outside
    the grid must still be scored, never skipped into a free pass) -- so the
    test is about what the grid is DERIVED from, not about what is swept."""
    src = inspect.getsource(pair.dense_drift_grid)
    tree = ast.parse(textwrap.dedent(src))
    ast.get_docstring(tree.body[0]) and tree.body[0].body.pop(0)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "DIMENSION_DRIFT_RESOLUTION" not in names, (
        "a grid derived from the register can only ask it what it already "
        "answered")
    # AND ITS EXTENT IS THE BOOK'S TOO (the 2026-08-13 grid-extent finding).
    # `DRIFT_GRID_SPAN_DAYS` is GONE: while the width was a harness constant,
    # `_measure_collapse_runs` -- which reads saturation off a run touching an
    # END of the grid -- was reading a property of where the sweep stopped.
    # The signature is the control: a grid that cannot be computed without a
    # book cannot be a declaration.
    assert not hasattr(pair, "DRIFT_GRID_SPAN_DAYS"), (
        "the declared width is the defect; leaving it as an unused constant "
        "leaves the next grid something to reach for")
    params = inspect.signature(pair.dense_drift_grid).parameters
    assert "records" in params and "as_of" in params
    recs, _cons, _ledger, as_of = pair.build_scenario(120, seed=7)
    grid = pair.dense_drift_grid(recs, as_of)
    # ONE DERIVATION FOR BOTH KNOBS, because it is one identity: the recon
    # drift moves the detector's fire date to `due + grace + k` and the terms
    # drift moves the believed due date by `k`, putting it at `due + k +
    # grace`. Same line, same book, so the same range of answerable drifts.
    assert grid == pair.book_recon_drift_grid(recs, as_of)
    assert grid[0] == min((r.issue_date - r.due_date).days for r in recs) \
        - pair.DEFAULT_RECONCILIATION_GRACE_DAYS - 1
    assert grid[-1] == max((as_of - r.due_date).days for r in recs) \
        - pair.DEFAULT_RECONCILIATION_GRACE_DAYS + 1


def test_the_detection_gap_saturates_in_both_tails(drift_resolution):
    """THE ATOM D28 FINDING, RE-MEASURED ON THE BOOK'S OWN EXTENT (the
    2026-08-13 grid-extent finding). Sixteen groups of counterfactual suppliers
    publish one bit-identical figure each, and both tails are saturated: below
    -6d every invoice in the book is already past the company's grace line
    however much shorter its terms get, above +82d none of them is before
    `as_of`.

    The witness that this was UNREACHABLE before: -8d -- which the old
    register-derived grid swept (it was in the *ageing* band) and read as
    MOVED, i.e. as evidence of resolution -- sits inside the saturated tail,
    publishing the same figure as -20d."""
    row = drift_resolution["detection"]
    assert row["saturates_below"] == -6 and row["saturates_above"] == 82
    tail = next(r for r in row["collapsed_runs"] if row["drifts"][0] in r)
    assert tail == tuple(range(-20, -5)) and len(tail) == 15
    assert -8 in tail and -8 in row["moved"], (
        "the old grid scored -8 as movement; it is indistinguishable from -20")
    for seed in row["seeds"]:
        by = row["by_seed"][seed]["by_drift"]
        assert len({by[k] for k in tail}) == 1
    assert len(row["collapsed_runs"]) == 16


def test_the_upper_edge_was_the_grids_own_end_and_the_caveat_shipped_it():
    """THE 2026-08-13 GRID-EXTENT FINDING, at the value that shipped.

    D28 derived this grid's DENSITY from the book and left its WIDTH at
    `PERIOD_SPACING_DAYS = 21`. The run `(17..21)` ends at +21 because the SWEEP
    ends at +21, and `_measure_collapse_runs` calls a run touching the grid's
    end SATURATION -- so `detection` declared `saturates_above: 17` and
    `detection_resolution_caveat` interpolated it into a sentence stamped on
    every published detection figure: a movement here 'is not readable as days
    of company error'. Across +17..+82 it is readable, and the caveat was
    therefore worse than none.

    Scored HERE rather than asserted from the register, so this test fails if
    the reading ever stops moving in that region for some other reason."""
    recs, cons, _ledger, as_of = pair.build_scenario(300, seed=7)
    at = {k: pair.score_triad(recs, cons, as_of,
                              organ_terms_drift_days=k)["detection"].gap
          for k in (17, 21, 30, 60, 82, 88)}
    assert at[17] == at[21], "the old grid's last two points do agree"
    assert len({at[17], at[30], at[60], at[82]}) == 4, (
        "four companies the shipped caveat said were one figure")
    assert at[82] == at[88], "and the real edge holds to the book's end"
    # THE EDGE THE SIBLING REGISTER HAD ALL ALONG. `flagged_via_reconciliation`
    # is the SAME reading off the SAME book, swept by the sibling knob on a
    # grid whose ends come from the records -- and it has declared +82 since
    # D31. Two registers over one quantity in one module, agreeing on the edge
    # only where the grid was allowed to reach it.
    assert (pair.ORGAN_QUERY_GRID["flagged_via_reconciliation"]
            ["saturates_above"] == 82)
    assert (pair.DIMENSION_DRIFT_RESOLUTION["detection"]["saturates_above"]
            == 82)
    caveat = pair.detection_resolution_caveat()
    assert "SATURATES below -6d and above +82d" in caveat
    assert "+17" not in caveat.split("quantised")[0], (
        "the false edge must not survive anywhere in the saturation clause")


def test_the_differential_witness_was_bought_by_the_narrow_grid(
        drift_resolution):
    """WHAT THE HONEST EXTENT COST, stated rather than quietly absorbed.

    `_check_register_is_differential` demanded an on-path dimension that
    collapses NOWHERE, and `ageing` supplied it: 43 distinct readings across
    +/-21. On the book's own extent ageing saturates above +63 -- a company
    under-ageing by more than nine weeks has carried every invoice below the
    30-day bucket floor -- so the clean sheet was bought by the same width that
    made detection's caveat false. A rule whose only satisfying state is an
    under-swept grid rewards under-sweeping, so the witness is now INTERIOR
    resolution, and `detection_latency` meets it: its only collapse is its own
    saturated tail."""
    age = drift_resolution["ageing"]
    assert age["saturates_above"] == 63 and age["saturates_below"] is None
    assert len(age["collapsed_runs"]) == 1
    assert min(age["collapsed_runs"][0]) == 63

    lat = drift_resolution["detection_latency"]
    assert lat["collapsed_runs"] == ((-20, -19),)
    assert lat["saturates_below"] == -19
    # ITS ONLY RUN IS ITS OWN TAIL -- 105 adjacent pairs read apart.
    assert not pair._interior_collapsed_runs(
        pair.DIMENSION_DRIFT_RESOLUTION["detection_latency"])
    assert pair._interior_collapsed_runs(
        pair.DIMENSION_DRIFT_RESOLUTION["detection"]), (
        "detection is the entry that does NOT witness interior resolution")


def test_the_saturation_rule_is_not_keyed_to_a_register_state():
    """THE CLASS FIX (R10). D27 built the saturation rule inside
    `_check_own_band`, reachable only for entries declaring an `own_drift` --
    the OFF-path ones -- so the register refused an unbounded-blind band off
    the causal path and accepted one ON it. There is now ONE function and both
    checkers call it; a rule that exists only once cannot exist on one side of
    `in_causal_path` and not the other."""
    for fn in (pair._check_on_path_entry, pair._check_own_band):
        assert "_check_saturation_and_collapse(" in inspect.getsource(fn), (
            f"{fn.__name__} no longer goes through the shared rule -- this is "
            "the keying that has now escaped six times")
    # And it really runs on the off-path side: the shared rule re-derives
    # D27's saturation edge from the readings alone, knowing nothing about
    # failure events, windows or `measure_belief_window_resolution`.
    # ATOM D29 re-derived these on a grid the register did not choose, and the
    # two ceilings turned out NOT to be the same number: the mix dimension is
    # one day blinder, which the register had asserted away by copying its
    # sibling's edge to a point nobody scored.
    assert pair.DIMENSION_DRIFT_RESOLUTION["belief"]["own_saturates_above"] \
        == -308
    assert pair.DIMENSION_DRIFT_RESOLUTION["belief_population_mix"][
        "own_saturates_above"] == -309
    for dim in ("belief", "belief_population_mix"):
        e = pair.DIMENSION_DRIFT_RESOLUTION[dim]
        assert e["own_saturation_atom"] == e["own_debt_atom"]


@pytest.mark.parametrize("mutate,expected", (
    # An undeclared collapse -- the defect itself, and what the register looked
    # like before this atom.
    (lambda r: r["detection"].__setitem__(
        "collapsed_runs", tuple(x for x in r["detection"]["collapsed_runs"]
                                if -20 not in x)),
     "publish ONE bit-identical reading"),
    # A declared collapse the sweep reads apart: a debt entry outliving its
    # debt, which is how a register decays after the reshape lands.
    (lambda r: r["detection"].__setitem__(
        "collapsed_runs", r["detection"]["collapsed_runs"] + ((2, 3),)),
     "the sweep reads them apart"),
    # An UNDERSTATED saturation edge -- the caveat interpolates it, so this is
    # the shape that publishes a narrower blind spot than the instrument has.
    (lambda r: r["detection"].__setitem__("saturates_below", -12),
     "measured saturates_below=-6"),
    (lambda r: r["detection"].__setitem__("saturates_above", None),
     "measured saturates_above=82"),
    # THE SHIPPED EDGE ITSELF (the 2026-08-13 grid-extent finding): put back
    # the number that was in this register for three days and the check fires
    # by name. It is the one mutation here that reproduces a real published
    # defect rather than an invented one.
    (lambda r: r["detection"].__setitem__("saturates_above", 17),
     "measured saturates_above=82 and declares 17"),
    (lambda r: r["detection"].__setitem__("saturation_atom", None),
     "names no `saturation_atom`"),
    # THE DIFFERENTIAL, re-derived on the book's own extent. A register in
    # which every on-path dimension is quantised INSIDE its own tails is an
    # "everything is quantised" claim that would pass whatever the instrument
    # did. Both interior witnesses must be broken for it to fire -- which is
    # the point: one surviving witness is enough, and there are two.
    (lambda r: [r[d].__setitem__("collapsed_runs",
                                 r[d]["collapsed_runs"] + ((1, 2),))
                for d in ("ageing", "detection_latency")],
     "collapses somewhere INSIDE its own saturated tails"),
    # AND THE UNDEFINED REGION, which only the book's extent can reach: an
    # absent reading compares unequal to the baseline, so an undeclared one is
    # counted as RESOLUTION by every band below it.
    (lambda r: r["detection_latency"].__setitem__("undefined_drifts", ()),
     "published NO reading at drifts"),
))
def test_a_lying_saturation_declaration_fires_by_name(drift_resolution, mutate,
                                                      expected):
    """R15 on the new register fields, both ways: an undeclared collapse, a
    collapse that is not there, an understated edge in each direction, an
    unowned hole, and an all-collapsed register."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    mutate(register)
    violations = pair.check_dimension_drift_resolution(
        drift_resolution, register=register)
    assert any(expected in v for v in violations), violations


def test_the_off_path_saturation_declaration_is_tried_too(own_drift_resolution):
    """The same mutations on the OTHER side of `in_causal_path`, through the
    same shared function -- the point of the class fix is that this test and
    the one above are testing one rule."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    register["belief"]["own_collapsed_runs"] = ()
    register["belief"]["own_saturates_above"] = None
    violations = pair.check_own_drift_resolution(
        own_drift_resolution, register=register)
    assert any("publish ONE bit-identical reading" in v for v in violations)
    assert any("measured saturates_above=-308" in v for v in violations)


def test_the_registers_own_grid_cannot_see_six_of_the_seven_collapses(
        monkeypatch):
    """THE SOURCE MUTATION (R15 the other way): put the grid back the way it
    was -- derived from the register's own declarations -- and the finding
    disappears. Six of `detection`'s seven collapsed runs become unreachable,
    including the sixteen-company saturated tail, and they surface only as
    declarations the sweep can no longer confirm.

    This is the whole of atom D28 in one assertion: the register was being
    asked exactly where it had already answered."""
    monkeypatch.setattr(pair, "dense_drift_grid", lambda *a, **k: (0,))
    sparse = pair.measure_dimension_drift_resolution(
        n_customers=_RES_N, seeds=(7,))
    assert sorted(sparse["detection"]["drifts"]) == [-8, -1, 0, 1, 12], (
        "this is the grid the register chose for itself")
    assert sparse["detection"]["collapsed_runs"] == ((0, 1),)
    assert sparse["detection"]["saturates_below"] is None
    violations = pair.check_dimension_drift_resolution(sparse)
    unreachable = [v for v in violations if "reads them apart" in v]
    mine = [v for v in unreachable if v.startswith("detection:")]
    assert len(mine) == 15 and any("-20" in v for v in mine), (
        "on its own grid the register can confirm exactly one of detection's "
        "sixteen collapses -- the (0,+1) pair, because +1 is the one drift it "
        "already declared")
    # The sighted witness's own tail was equally unreachable there.
    assert any(v.startswith("detection_latency:") for v in unreachable)


def test_an_absent_reading_is_not_counted_as_resolution():
    """THE FAIL-OPEN this measurement would otherwise have. A dimension whose
    population empties under a drift publishes `None`, and `None != baseline`
    reads as MOVEMENT -- an instrument that has stopped reading at all, scored
    as though it had resolved the company. It is reachable: at large positive
    terms drifts `detection_latency` dates nothing and its gap goes None.

    AND SINCE THE GRID'S EXTENT CAME FROM THE BOOK (the 2026-08-13 grid-extent
    finding) it is reached by the REAL sweep, not only by an injected blank.
    The 21-day grid stopped 66 days short of the drift that empties the latency
    population, so this fail-open was live and unreachable at the same time --
    the region where the instrument stops reading was outside the only sweep
    that could have noticed. It is now declared AND WITNESSED: absent exactly
    where the population is empty."""
    class _Blank:
        gap = None
        components: dict = {}
        note = ""

    real = pair.measure_dimension_drift_resolution(
        n_customers=120, seeds=(7,))
    assert real["detection_latency"]["undefined_readings"] == (87, 88)
    assert not any(row["undefined_readings"] for dim, row in real.items()
                   if dim != "detection_latency")
    # THE WITNESS IS A PAIR, and that is what makes it a control: an absent
    # reading over a NON-empty population would be an instrument that stopped
    # for some other reason, and it would fail here.
    assert real["detection_latency"]["undefined_witness"] == {
        87: ((True, 0),), 88: ((True, 0),)}
    # AND THE UNDEFINED CLASS ALONE IS WHAT THIS SWEEP MAY BE ASKED, because
    # THIS sweep is not the register's population (H27 Expert Hour #24). The
    # register's collapse runs and saturation edges are DECLARED at `_RES_N`
    # with the default seeds, and every one of them moves with the population
    # -- at n=120/seed 7 the ageing collapse sits at (-19,-18) where the
    # register, measured at n=300 on three seeds, declares (-20,-19). Asserting
    # the WHOLE check clean here asks the register about a book it was never
    # measured on; `test_the_drift_resolution_register_is_measured_not_asserted`
    # makes that global assertion, on the fixture the register is declared from.
    # What IS population-invariant, and what this test is about, is that the two
    # empty-population drifts are DECLARED: they raise no absent-reading
    # violation, which is the half the `holed` witness below proves fires.
    assert not [v for v in pair.check_dimension_drift_resolution(real)
                if "published NO reading at drifts" in v]

    def runner(seed, k):
        scored = dict(pair.measure(n_customers=120, seed=seed))
        if k == 12:
            scored["detection_latency"] = _Blank()
        return scored

    holed = pair.measure_dimension_drift_resolution(
        n_customers=120, seeds=(7,), runner=runner)
    # (12,) AND NOT (12, 87, 88): this runner re-scores the BASELINE at every
    # drift -- it takes `k` only to punch the hole -- so the real emptiness at
    # +87/+88 cannot appear here. It is witnessed on the REAL sweep above, and
    # this half stays what it was built to be: an INJECTED absence, over a
    # population that is not empty (H27 Expert Hour #24).
    assert holed["detection_latency"]["undefined_readings"] == (12,)
    assert 12 in holed["detection_latency"]["moved"], (
        "this is the fail-open: an absent reading compares unequal and is "
        "counted as movement by every band")
    violations = pair.check_dimension_drift_resolution(holed)
    assert any("published NO reading at drifts" in v for v in violations)


def test_the_saturation_caveat_travels_with_the_detection_number():
    """A control the reader about to quote the detection gap never meets is one
    that protects the test suite rather than the figure (the D25 rule). The
    caveat is stamped on `components` as well as the prose -- the ledger
    writer, live wiring and dashboard read components and never the note (D22)
    -- and is INTERPOLATED from the register on every call, so a register that
    flips flips the published claim with it."""
    result = pair.measure(n_customers=120, seed=7)
    caveat = result["detection"].components["drift_resolution_caveat"]
    assert "atoms D28" in caveat and caveat in result["detection"].note
    assert "SATURATES below -6d and above +82d" in caveat
    assert "D28_the_detection_gap_is_quantised_by_this_books_placement" in caveat

    # INTERPOLATED, NEVER RETYPED: move the register and the sentence moves.
    entry = pair.DIMENSION_DRIFT_RESOLUTION["detection"]
    saved = dict(entry)
    try:
        entry["saturates_below"], entry["saturates_above"] = -3, 9
        assert "SATURATES below -3d and above +9d" in (
            pair.detection_resolution_caveat())
        entry["collapsed_runs"] = ()
        entry["saturates_below"] = entry["saturates_above"] = None
        assert "publishes a distinct figure" in pair.detection_resolution_caveat()
    finally:
        entry.clear()
        entry.update(saved)


# ---------------------------------------------------------------------------
# WHY THE INTERIOR IS QUANTISED -- this headline's DENOMINATORS, not the book's
# placement (2026-08-14 BLOCKING finding, atom D28, H27 Expert Hour #31)
#
# The caveat and the register both blamed placement: "the number of invoices
# sitting BESIDE the grace line at any one distance is small". Checkable, and
# false -- 212 of 900 invoices sit past the line at 63 distinct distances. What
# is small is the part of that traffic the headline's own denominators count.
# The sentence shipped inside `components["drift_resolution_caveat"]`, which
# the ledger writer, the live wiring and the dashboard all read, so a published
# claim was wrong while every published NUMBER was right.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def interior_change_points():
    """Measured ONCE for the module: the sweep re-scores three books across the
    whole readable interior, and every mutation below is a trial of a
    DECLARATION against this same measurement."""
    return pair.measure_detection_interior_change_points(n_customers=_RES_N)


def test_the_interior_cause_is_the_denominators_not_the_books_placement(
        interior_change_points):
    """THE FINDING'S OWN CLAIM, re-derived rather than quoted.

    Two premises are asserted first because the decomposition is void without
    them and both fail silently: the truth-side sets must not move under the
    company drift (R13 -- a counterfactual COMPANY over one world), and the
    published figure must move exactly where the flagged step touches `S u N`.
    That second one is the corrected caveat's whole inference licence, and it
    is checked against the SHIPPED scorer's gap, not a re-derivation of it.

    CHARACTERIZATION on the inequality: that the excluded band out-steps the
    counted populations is TODAY'S reading, not a contract. The declared
    residual is a reshape that makes `S u N` dense across the interior; when it
    lands this test is EXPECTED to fire, and re-deriving the band it fires on
    is the point."""
    m = interior_change_points
    assert pair.check_detection_interior_change_points(m) == []
    for s in m["seeds"]:
        row = m["by_seed"][s]
        assert row["sets_drifted_at"] == (), (
            "the drift moved a truth-side set -- the counterfactual is a "
            "COMPANY, and every count here would be comparing two populations")
        assert row["predicate_disagreements"] == (), (
            "the figure moved without the counted sets stepping, or the "
            "reverse -- the caveat's licence is broken")
        # THE EXCLUSION IS THE INTERIOR'S TRAFFIC, and the headline cannot see
        # it: ~23% of the book, stepping at ~3/4 of the interior's pairs.
        assert row["n_excluded"] / row["n_universe"] > 0.20
        assert len(row["excluded_change_points"]) > len(
            row["counted_change_points"]), (
            "the placement explanation would need the reverse of this")
        # AND THE READER'S BACKWARDS INFERENCE IS WRONG THIS OFTEN.
        assert len(row["silent_set_moves"]) > 30


def test_the_placement_explanation_is_gone_from_the_surfaces_it_shipped_on():
    """R11's shape on a sentence: the false clause is checked ABSENT from the
    artefact a reader is handed, not merely absent from the source line that
    was edited. `components` is the surface -- the ledger writer, live wiring
    and dashboard read it and never the note."""
    result = pair.measure(n_customers=120, seed=7)
    caveat = result["detection"].components["drift_resolution_caveat"]
    why = pair.DIMENSION_DRIFT_RESOLUTION["detection"]["why"]
    for surface, name in ((caveat, "the published component"),
                          (result["detection"].note, "the note"),
                          (why, "the register's own `why`")):
        assert "BESIDE the grace line at any one distance is small" not in \
            surface, f"the false clause survives in {name}"
    # AND THE CORRECTION IS PRESENT, both halves of it.
    assert "NECESSARY, NOT SUFFICIENT" in caveat
    assert "DO NOT RUN THAT BACKWARDS" in caveat
    assert "DENOMINATORS, NOT THE BOOK'S PLACEMENT" in caveat
    assert "NOT thin beside the grace line" in caveat
    assert "DENOMINATORS, NOT THE BOOK'S" in why


def test_the_interior_cause_numbers_are_interpolated_never_retyped():
    """Move the register and the sentence moves with it -- the D19/D20/D22/D23/
    D25 rule that made this correction necessary in the first place: the clause
    it replaces was typed once and re-read by nothing."""
    entry = pair.DIMENSION_DRIFT_RESOLUTION["detection"]
    saved = dict(entry)
    try:
        entry["interior_excluded_change_points"] = (5, 5)
        entry["interior_counted_change_points"] = (77, 79)
        caveat = pair.detection_resolution_caveat()
        assert "steps at 5 on the EXCLUDED band" in caveat
        assert "at only 77-79 on the two populations" in caveat
    finally:
        entry.clear()
        entry.update(saved)


def test_an_unmeasured_cause_is_published_as_unmeasured_not_as_a_small_one():
    """R15's third shape, on a sentence. An entry that has not declared the
    bands must SAY the cause is unmeasured -- silently falling back to the
    placement story, or to no clause at all, is how the false one shipped for a
    day inside a caveat that reads as complete."""
    entry = pair.DIMENSION_DRIFT_RESOLUTION["detection"]
    saved = dict(entry)
    try:
        for k in ("interior_pairs", "interior_counted_change_points",
                  "interior_excluded_change_points",
                  "interior_silent_set_moves"):
            entry.pop(k, None)
        caveat = pair.detection_resolution_caveat()
        assert "NOT MEASURED on this entry" in caveat
        assert "BESIDE the grace line at any one distance is small" not in caveat
    finally:
        entry.clear()
        entry.update(saved)


@pytest.mark.parametrize("field,bad,expected", (
    ("interior_pairs", 42, "adjacent pairs and this book measures"),
    ("interior_counted_change_points", (60, 70),
     "pairs where the COUNTED populations"),
    ("interior_excluded_change_points", (1, 2),
     "pairs where the EXCLUDED band changes"),
    ("interior_silent_set_moves", (0, 1),
     "pairs where the flagged set moves and the figure does not"),
))
def test_a_declared_interior_band_that_stopped_describing_the_book_fires(
        interior_change_points, field, bad, expected):
    """R15 BOTH WAYS on the declaration. Each band is the register's claim
    about THIS book; move it and the control must name it. A band nobody
    re-derives is exactly what the corrected sentence used to be."""
    entry = dict(pair.DIMENSION_DRIFT_RESOLUTION["detection"])
    entry[field] = bad
    violations = pair.check_detection_interior_change_points(
        interior_change_points, entry=entry)
    assert any(expected in v for v in violations), violations
    assert any("never widen the band to fit" in v or "re-derive" in v
               for v in violations)


@pytest.mark.parametrize("field,wide,expected", (
    ("interior_counted_change_points", (0, 86),
     "pairs where the COUNTED populations"),
    ("interior_excluded_change_points", (0, 86),
     "pairs where the EXCLUDED band changes"),
    ("interior_silent_set_moves", (0, 86),
     "pairs where the flagged set moves and the figure does not"),
))
def test_a_declared_interior_band_WIDENED_to_fit_fires(
        interior_change_points, field, wide, expected):
    """THE DIRECTION THE CONTROL COULD NOT SEE (BLOCKING 2, 2026-08-15 Expert
    Hour). Every mutation case above narrows or shifts; NONE widened, so "R15
    both ways" was proven only in the direction that cannot hide a defect. The
    check was CONTAINMENT while its docstring said it "requires that the
    DECLARATION match the BOOK", so declaring the whole interior `(0, 86)`
    returned no violation at all -- and the caveat then published the widened
    band as its own cause, destroying the "61-63 ... and at ONLY 32-38"
    contrast the sentence exists to draw. The violation string it could not
    emit ends "never widen the band to fit"."""
    entry = dict(pair.DIMENSION_DRIFT_RESOLUTION["detection"])
    measured = tuple(interior_change_points[field[len("interior_"):]])
    assert measured != wide, "the fixture must not already read the wide band"
    assert wide[0] <= measured[0] and measured[1] <= wide[1], (
        "this case must WIDEN -- a shift or a narrowing is already covered")
    entry[field] = wide
    violations = pair.check_detection_interior_change_points(
        interior_change_points, entry=entry)
    assert any(expected in v for v in violations), violations
    assert any("WIDER than the book" in v for v in violations), violations
    assert any("never widen the band to fit" in v for v in violations)


@pytest.mark.parametrize("field,expected", (
    ("interior_counted_change_points",
     "pairs where the COUNTED populations"),
    ("interior_excluded_change_points",
     "pairs where the EXCLUDED band changes"),
    ("interior_silent_set_moves",
     "pairs where the flagged set moves and the figure does not"),
))
def test_an_omitted_interior_band_is_a_violation_not_a_clean_sheet(
        interior_change_points, field, expected):
    """R15's SECOND killer pattern on the same loop (BLOCKING 2, 2026-08-15).
    `declared = e.get(field)` followed by `if declared is None: continue` meant
    an entry that simply omitted a band passed -- the missing-value fail-open,
    verbatim. `detection_resolution_caveat` publishes "NOT MEASURED on this
    entry" in that case, so a reader is told; this control said nothing, which
    is what let a band be dropped rather than re-derived."""
    entry = dict(pair.DIMENSION_DRIFT_RESOLUTION["detection"])
    entry.pop(field)
    violations = pair.check_detection_interior_change_points(
        interior_change_points, entry=entry)
    assert any(expected in v for v in violations), violations
    assert any("an absent declaration is not a clean sheet" in v
               for v in violations), violations


def _cp_with(measurement, seed_patch=None, **top):
    """A copy of the measurement with one seed's row (or a top-level band)
    mutated -- the R15 probe for the fail-open shapes, applied to the
    MEASUREMENT rather than the declaration."""
    out = {k: (dict(v) if isinstance(v, dict) else v)
           for k, v in measurement.items()}
    out["by_seed"] = {s: dict(r) for s, r in measurement["by_seed"].items()}
    if seed_patch:
        first = measurement["seeds"][0]
        out["by_seed"][first].update(seed_patch)
    out.update(top)
    return out


@pytest.mark.parametrize("patch,top,expected", (
    (None, {"by_seed": {}}, "measured over NO seeds"),
    ({"interior_pairs": 0}, {}, "holds NO adjacent pair"),
    ({"sets_drifted_at": (3, 4)}, {}, "truth-side sets MOVED"),
    ({"predicate_disagreements": ((3, 4),)}, {}, "DISAGREE at"),
    ({"n_truth": 0}, {}, "`S, the true failures` is EMPTY"),
    ({"n_negatives": 0}, {},
     "`N, the never-flaggable negatives` is EMPTY"),
))
def test_the_interior_control_fires_on_its_own_named_fail_open(
        interior_change_points, patch, top, expected):
    """R15: the four ways this measurement could pass while measuring nothing.
    An empty sweep, an empty interior, a drifting world and an empty counted
    population all read EXACTLY like a clean sheet unless each is named."""
    violations = pair.check_detection_interior_change_points(
        _cp_with(interior_change_points, patch, **top))
    assert any(expected in v for v in violations), violations


def test_the_resolution_caveat_travels_with_the_ageing_number():
    """The limit is published WITH the figure -- in `components` as well as the
    prose, because the ledger writer and the live wiring never read `note` --
    and its band is INTERPOLATED from the register, never retyped. Flip the
    register and the published claim flips with it, so the two cannot drift
    apart the way a hand-typed caveat did."""
    result = pair.measure(n_customers=120, seed=7)
    caveat = result["ageing"].components["drift_resolution_caveat"]
    assert "atom D25" in caveat
    assert result["ageing"].components["drift_blind_band_days"] == ()
    assert caveat in result["ageing"].note

    # SINCE D25 THE CAVEAT DESCRIBES THE BOOK THE FIGURE CAME FROM, not the
    # offline scenario -- `score_triad` also scores live run_phase2b
    # populations whose calendar no sweep has visited, and until this atom
    # those readings carried a caveat written about three fixed due dates.
    res = result["ageing"].components["ageing_resolution_days"]
    assert res == {"over_ageing": 1, "under_ageing": 1}
    assert f"{res['over_ageing']}d of OVER-ageing" in caveat
    assert str(result["ageing"].components["ageing_resolution_book"]
               ["n_distinct_ages"]) in caveat

    # And it is INTERPOLATED, never retyped: a book with a worse resolution
    # publishes the worse number rather than this one.
    flat, _c, _l, flat_as_of = pair.build_scenario(
        120, seed=7, cycle_spread_days=1)
    flat_res = pair.measure_ageing_resolution(flat, flat_as_of)
    assert "9d of OVER-ageing" in pair.ageing_resolution_caveat(flat_res)

    # The register-only fallback (no book in hand) interpolates the declared
    # band the same way, so a register that rots back to a blind claim
    # publishes that claim rather than this atom's.
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    register["ageing"]["invisible_drifts"] = (-3, -2, -1)
    with mock.patch.object(pair, "DIMENSION_DRIFT_RESOLUTION", register):
        assert "1 to 3 days" in pair.ageing_resolution_caveat()


def test_the_drift_resolution_control_runs_in_the_cli_not_only_in_tests():
    """Same reason as the two controls before it: a limit a reader has to go
    looking for is one they will read past, and the reader about to quote an
    ageing displacement is exactly who needs the step beside it."""
    src = inspect.getsource(pair.main)
    assert "measure_dimension_drift_resolution(" in src
    assert "check_dimension_drift_resolution" in src
    assert "check_ageing_resolution(" in src


# ---------------------------------------------------------------------------
# THE RESHAPE ITSELF (atom D25_ageing_resolution_is_the_harness_calendar)
# ---------------------------------------------------------------------------
# The register above ANSWERS "did drift k move the reading" by re-scoring, and
# can only ever report on the drifts somebody declared. `measure_ageing_
# resolution` PREDICTS the same quantity from the population and the truth-side
# bucket rule alone -- no scorer, no consumer, no organ -- so the two are
# independent computations of one thing and can be put against each other.
# These tests are the D25 deliverable's own R15 pass.


@pytest.fixture(scope="module")
def _books():
    """The shipped (staggered) book and the DECLARED flat counterfactual, one
    build each -- every claim below is differential across the two."""
    out = {}
    for label, spread in (("staggered", None), ("flat", 1)):
        recs, _c, _l, as_of = pair.build_scenario(
            300, seed=7, cycle_spread_days=spread)
        out[label] = pair.measure_ageing_resolution(recs, as_of)
    return out


def test_the_predicted_resolution_reproduces_the_flat_books_measured_asymmetry(
        _books):
    """THE INDEPENDENCE EVIDENCE, and it is what makes the predictor worth
    trusting on a book no sweep has visited. Expert Hour #8 measured the flat
    book by RE-SCORING: 9 days of over-ageing invisible, 1 day of under-ageing
    visible -- an asymmetry nobody designed. The predictor, which never runs
    the scorer, derives exactly that pair from the population and the bucket
    rule."""
    assert _books["flat"]["over_ageing_days"] == 9
    assert _books["flat"]["under_ageing_days"] == 1
    assert _books["flat"]["n_distinct_ages"] == 3
    assert _books["staggered"]["over_ageing_days"] == 1
    assert _books["staggered"]["under_ageing_days"] == 1


def test_the_flat_book_fails_the_resolution_target_by_name(_books):
    """R15: the control fires on its OWN named defect. The book this atom
    replaced -- still reachable as a declared parameter, not deleted -- is
    refused, and the refusal names the direction and the remedy."""
    violations = pair.check_ageing_resolution(_books["flat"])
    assert any("OVER-ageing" in v and "9d" in v for v in violations), violations
    assert pair.check_ageing_resolution(_books["staggered"]) == []


def test_the_predictor_and_the_drift_sweep_must_agree(drift_resolution, _books):
    """The cross-check that stops either computation being the one believed.
    Green on the shipped pair; and a predictor that lied about the resolution
    would be caught by the sweep's own readings rather than by nobody."""
    assert pair.check_ageing_resolution(
        _books["staggered"], drift_resolution) == []
    lying = {**_books["staggered"], "over_ageing_days": 20,
             "under_ageing_days": 20}
    violations = pair.check_ageing_resolution(lying, drift_resolution)
    assert any("PREDICTED invisible" in v and "MEASURED visible" in v
               for v in violations), violations


def test_an_empty_or_boundaryless_book_is_a_violation_not_a_pass():
    """The two fail-open shapes R15 names. A resolution claim measured over no
    invoices, or over a book with no bucket boundary anywhere near it, must
    RAISE rather than sail through on a `None` nobody looked at."""
    empty = pair.measure_ageing_resolution([], date(2024, 4, 16))
    assert empty["n_aged"] == 0
    assert any("vacuous" in v for v in pair.check_ageing_resolution(empty))

    records, _c, _l, as_of = pair.build_scenario(120, seed=7)
    # A rule with no boundary below the book at all: nothing can cross
    # downwards, so no amount of under-ageing is visible.
    far = pair.measure_ageing_resolution(records, as_of, boundaries=(400,))
    assert far["under_ageing_days"] is None
    assert any("NO invoice with a bucket boundary" in v
               for v in pair.check_ageing_resolution(far))


def test_the_boundaries_are_derived_from_the_rule_not_retyped():
    """The D21 tautology in miniature, refused: hand-listing (30, 60, 90) would
    let an edit to the truth-side bucket rule move the boundaries the
    resolution is measured against while this list went on certifying a
    resolution the instrument no longer has."""
    assert pair.ageing_bucket_boundaries() == (30, 60, 90)
    # Moved at the OWNERSHIP REGISTER (atom D21), which is the call path the
    # truth side actually takes -- patching the bare function name would prove
    # nothing about what runs.
    with mock.patch.object(
            pair, "truth_side_rule",
            lambda dim: (lambda d: "90+" if d >= 45 else "current")):
        assert pair.ageing_bucket_boundaries() == (45,)


def test_the_staggered_book_never_perturbed_the_other_substreams():
    """C-S2, the reason the cycle offset draws from its own named substream:
    adding a draw must not shift the draws that were already there. The stress
    tier and payment method of every customer are unchanged by the reshape,
    which is what keeps this a change to WHEN the book is billed rather than a
    silent change of population."""
    staggered, _c, _l, _a = pair.build_scenario(200, seed=7)
    flat, _c2, _l2, _a2 = pair.build_scenario(200, seed=7, cycle_spread_days=1)
    by_ref = {(r.customer_id, r.period_index): r for r in flat}
    assert len(by_ref) == len(staggered)
    for r in staggered:
        was = by_ref[(r.customer_id, r.period_index)]
        assert r.payment_method == was.payment_method
        assert r.result == was.result
        assert r.dd_failure_reason == was.dd_failure_reason


def test_the_cycle_spread_is_the_cycle_and_a_flat_book_is_reachable():
    """The spread is `PERIOD_SPACING_DAYS` -- the cycle length itself, the only
    non-arbitrary choice -- and `cycle_spread_days=1` reproduces the pre-D25
    book exactly, so the counterfactual lives in the repo rather than in a
    test's monkeypatch (the D20 rule)."""
    assert pair.BILLING_CYCLE_SPREAD_DAYS == pair.PERIOD_SPACING_DAYS
    flat, _c, _l, flat_as_of = pair.build_scenario(
        60, seed=7, cycle_spread_days=1)
    assert {r.due_date for r in flat} == {
        pair.FIRST_DUE_DATE + timedelta(days=pair.PERIOD_SPACING_DAYS * p)
        for p in range(pair.N_PERIODS)}
    assert (flat_as_of - max(r.due_date for r in flat)).days == \
        pair.AS_OF_BUFFER_DAYS
    with pytest.raises(ValueError, match="must be >= 1"):
        pair.build_scenario(10, seed=7, cycle_spread_days=0)


def test_as_of_clears_the_buffer_for_every_account_not_just_the_average():
    """`AS_OF_BUFFER_DAYS` means "every account's newest invoice is at least
    this far past due" -- its stated job. Taking `as_of` from the latest due
    date the CYCLE can produce rather than the latest this DRAW produced keeps
    that true at every population size, so the reading does not depend on how
    many customers were sampled."""
    for n in (10, 60, 300):
        records, _c, _l, as_of = pair.build_scenario(n, seed=7)
        newest = max((as_of - r.due_date).days for r in records)
        assert newest >= pair.AS_OF_BUFFER_DAYS, (n, newest)
    small = pair.build_scenario(10, seed=7)[3]
    large = pair.build_scenario(300, seed=7)[3]
    assert small == large, (
        "`as_of` moved with the sample size -- the ageing reading would then "
        "depend on how many customers were drawn, not on the company")


# ---------------------------------------------------------------------------
# THE OFF-PATH ENTRIES' OWN GRADED KNOB
# (atom D27_belief_window_saturates_on_this_book, H27 Expert Hour #9)
#
# D25's register asks what the smallest company error each published dimension
# can see. It answered that for the three dimensions its single drift reaches;
# the other STATE -- off-path -- discharged itself with `exercised_by`, a
# binary reading against an indiscriminate degenerate. A degenerate is the
# LARGEST error there is: it establishes that a dimension is not inert and
# measures no resolution whatever. Both belief dimensions sat there, so two of
# five published dimensions had no measured resolution -- the hole in the shape
# the register was built to close.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def own_drift_resolution():
    """Measured ONCE for the module. Unlike the terms sweep this one BUILDS a
    company per drift (the lookback window is a constructor argument), so the
    world it is built over is compared record by record inside the measurement
    itself."""
    return pair.measure_own_drift_resolution(n_customers=_RES_N)


def test_every_off_path_entry_now_owes_a_graded_band(own_drift_resolution):
    """THE CLASS FIX. Off-path is no longer a state that escapes resolution
    measurement: every entry declaring it must name a knob on its OWN organ's
    path and have the band measured. Green means the declared memory blindness
    is the blindness the code has -- not that there is none."""
    assert pair.check_own_drift_resolution(own_drift_resolution) == []
    off_path = {d for d, e in pair.DIMENSION_DRIFT_RESOLUTION.items()
                if not e["in_causal_path"]}
    assert off_path, "the register has no off-path entry left to protect"
    assert off_path <= set(own_drift_resolution), (
        f"off-path dimensions with no measured graded band: "
        f"{sorted(off_path - set(own_drift_resolution))} -- an indiscriminate "
        "degenerate is not a resolution measurement")


def test_the_belief_memory_band_is_unbounded_above(own_drift_resolution):
    """THE FINDING, kept as a live measurement rather than a note. Both belief
    dimensions read exactly one company parameter -- how far back
    `_arrears_risk_belief` still counts an observed failure -- and this book's
    oldest failure event is ~91d old against a 400d memory. So no event can
    fall out: every window from the book's span to INFINITY publishes a
    bit-identical figure, and the dimension cannot distinguish this company
    from one that never forgets a failure (the direction that keeps a recovered
    customer in collections).

    The drifts stay declared rather than dropped when D27's reshape lands, so a
    book that goes back to fitting inside the company's memory fails HERE, by
    name, instead of quietly re-widening the caveat."""
    for dim in ("belief", "belief_population_mix"):
        row = own_drift_resolution[dim]
        entry = pair.DIMENSION_DRIFT_RESOLUTION[dim]
        assert row["book"]["saturated"] is True
        assert row["book"]["headroom_days"] > 300, row["book"]
        # LENGTHENING the memory is invisible at every magnitude swept --
        # including +500d, a company that has more than doubled how long it
        # holds a failure against a customer.
        assert [k for k in row["unmoved"] if k > 0] == \
            sorted(k for k in entry["own_invisible_drifts"] if k > 0)
        assert 500 in row["unmoved"] and 1 in row["unmoved"]
        assert not [k for k in row["moved"] if k > 0], (
            f"{dim}: a LONGER memory moved the reading -- the saturation claim "
            "in this band and in the published caveat is wrong")


def test_the_shipped_company_sits_inside_its_own_blind_band(own_drift_resolution):
    """And it is not a near miss. The harness builds the company with
    `DD_FAILURE_WINDOW_DAYS`, 4.4x the organ's OWN shipped default, which puts
    the scored company ~300d deep inside the band this dimension cannot see --
    while the organ's default sits just BELOW the edge, publishing a different
    number. The 400 was deliberate (the constant's comment gives the reason);
    what was never measured is what it costs the dimension's resolution."""
    import inspect as _inspect
    default = _inspect.signature(
        pair.PaymentObservationConsumer.__init__
    ).parameters["dd_failure_window_days"].default
    assert pair.DD_FAILURE_WINDOW_DAYS > default, (
        "the harness no longer widens the window past the organ's default -- "
        "re-derive D27's band, this test and the caveat")
    book = own_drift_resolution["belief"]["book"]
    assert book["window_days"] - book["oldest_event_age_days"] > 250, book
    # The organ's own default is NOT in the blind band: the difference between
    # the shipped harness company and the shipped organ is a real published
    # difference this dimension can see, which is why 400 is a CHOICE.
    at_default = pair.build_scenario(
        _RES_N, seed=7,
        organ_failure_window_drift_days=default - pair.DD_FAILURE_WINDOW_DAYS)
    shipped = pair.build_scenario(_RES_N, seed=7)
    assert pair.score_triad(at_default[0], at_default[1], at_default[3])[
        "belief"].gap != pair.score_triad(
            shipped[0], shipped[1], shipped[3])["belief"].gap


def test_the_book_predicts_the_band_the_sweep_measured(own_drift_resolution):
    """INDEPENDENCE, and this is the evidence the control is not re-deriving
    the organ. `measure_belief_window_resolution` predicts the smallest visible
    memory error from the WORLD's event dates and the harness's declared window
    alone -- it never touches `_arrears_risk_belief`'s severity thresholds,
    whose hand-copy was the D20 defect. The drift sweep re-scores through the
    dimension's own shipped scorer. They agree on the number."""
    row = own_drift_resolution["belief"]
    predicted = row["book"]["smallest_visible_shortening_days"]
    measured = min(-k for k in row["moved"]) if row["moved"] else None
    assert measured == predicted, (predicted, measured, row["book"])
    # THE CODE, not the prose: the docstring names the organ on purpose (it is
    # explaining what the predictor deliberately does NOT read), so a bare
    # substring ban over the whole source would refuse the honest sentence that
    # states the property -- the AO2 "none" shape.
    fn = ast.parse(textwrap.dedent(
        inspect.getsource(pair.measure_belief_window_resolution))).body[0]
    code = "\n".join(
        ast.unparse(node) for node in fn.body
        if not (isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)))
    assert "arrears_risk" not in code and "severity" not in code, (
        "the population-side predictor has started reading the organ it "
        "grades -- that is the D20/D21 tautology, in the direction nobody "
        "checks")


def test_the_memory_knob_reaches_this_organ_and_no_other(own_drift_resolution):
    """THE DIFFERENTIAL, which is what makes the knob evidence about one organ
    rather than a second global perturbation -- and the R13 witness: a
    counterfactual COMPANY, never a counterfactual world."""
    for dim, row in own_drift_resolution.items():
        assert row["off_target"] == {}, (dim, row["off_target"])
        assert row["world_identical"] is True
        assert row["probe_bit"] is True


def test_the_memory_resolution_caveat_travels_with_both_numbers():
    """Stamped AT SOURCE on both belief dimensions, in the prose AND as
    components -- the ledger writer, the live wiring and the dashboard take
    `components` and never read `note` (the D22 stamping lesson). And it is
    re-derived from the book each call, so a LIVE population no sweep has
    visited carries its own resolution rather than the offline scenario's."""
    records, consumer, _l, as_of = pair.build_scenario(_RES_N, seed=7)
    result = pair.score_triad(records, consumer, as_of)
    for dim in ("belief", "belief_population_mix"):
        c = result[dim].components
        assert c["belief_window_resolution"]["saturated"] is True
        assert c["memory_blind_band_days"]
        for text in (c["belief_resolution_caveat"], result[dim].note):
            assert "SATURATED" in text
            assert "NEVER forgets" in text
            assert str(c["belief_window_resolution"]["window_days"]) in text
    # A DIFFERENT BOOK, a different caveat -- the number that travels is the
    # one this population earned, not a constant.
    short = pair.measure_belief_window_resolution(
        records, as_of, window_days=10)
    assert short["saturated"] is False
    assert "NOT saturated" in pair.belief_resolution_caveat(short)


def test_the_memory_resolution_control_runs_in_the_cli_not_only_in_tests():
    """A control a reader about to quote a belief gap never meets is one that
    protects the test suite, not the figure (the D25 rule)."""
    src = inspect.getsource(pair.main)
    assert "measure_own_drift_resolution" in src
    assert "check_own_drift_resolution" in src


@pytest.mark.parametrize("mutate,expected", (
    # THE DEFECT ITSELF, reinstated: the off-path entry going back to
    # discharging itself with an indiscriminate degenerate.
    (lambda r: r["belief"].pop("own_drift"),
     "measures NO resolution"),
    (lambda r: r["belief"].__setitem__("own_invisible_drifts", (1, 500)),
     "understates the blindness"),
    (lambda r: r["belief"].__setitem__("own_visible_drifts", (-380, -1)),
     "blinder than this register admits"),
    (lambda r: r["belief"].__setitem__(
        "own_invisible_drifts", (-320, -308, -100, -1, 1, 500)),
     "declared INVISIBLE but moved"),
    (lambda r: r["belief"].__setitem__("own_debt_atom", None),
     "unowned hole"),
    (lambda r: r["belief"].__setitem__("own_visible_drifts", (-380, -999)),
     "never scored"),
    (lambda r: (r["belief"].__setitem__("own_invisible_drifts", ()),
                r["belief"].__setitem__("own_debt_atom", None)),
     "understates the blindness"),
))
def test_a_lying_memory_band_fires_by_name(own_drift_resolution, mutate,
                                           expected):
    """R15 BOTH WAYS on the band. Each mutation is a way this declaration could
    stop describing the code: the off-path exemption returning, an understated
    band (which the published caveat interpolates), an overstated sight, a debt
    entry outliving its debt, an unowned hole, and a declaration checked
    against a reading nobody took."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    mutate(register)
    if not register["belief"].get("own_drift"):
        # The off-path rule lives in the sibling control -- that is where the
        # exemption is granted, so that is where its return must fire.
        measured = pair.measure_dimension_drift_resolution(
            n_customers=60, seeds=(7,))
        violations = pair.check_dimension_drift_resolution(
            measured, register=register)
    else:
        violations = pair.check_own_drift_resolution(
            own_drift_resolution, register=register)
    assert any(expected in v for v in violations), violations


@pytest.mark.parametrize("bad_runner,expected", (
    # AN INERT PROBE. The knob silently stops drifting and every invisibility
    # declaration below it is handed a free pass -- the fail-silent shape this
    # instrument has now produced seven times.
    (lambda knob, seed, k: _run_window(seed, 0), "moved NOTHING"),
    # A KNOB THAT MOVES EVERYTHING is a second global perturbation, not
    # evidence about this organ.
    (lambda knob, seed, k: _run_window(seed, k, terms=k), "off its own organ"),
    # A COUNTERFACTUAL WORLD, not a counterfactual company (R13).
    (lambda knob, seed, k: _run_window(seed, k, spread=1 if k else None),
     "CHANGED THE WORLD"),
))
def test_a_broken_memory_probe_fires_by_name(bad_runner, expected):
    """R15 ON THE SOURCE, not only on the register. A band is only as good as
    the probe that measured it, and all three of these would leave every
    declaration above passing."""
    measured = pair.measure_own_drift_resolution(
        n_customers=60, seeds=(7,), runner=bad_runner)
    violations = pair.check_own_drift_resolution(measured)
    assert any(expected in v for v in violations), violations


def _run_window(seed, k, terms=0, spread=None):
    """A deliberately-broken stand-in for the measurement's own runner."""
    records, consumer, _l, as_of = pair.build_scenario(
        60, seed=seed, organ_failure_window_drift_days=k,
        cycle_spread_days=spread)
    return records, pair.score_triad(
        records, consumer, as_of, organ_terms_drift_days=terms), as_of


def test_the_memory_knob_is_a_declared_company_not_a_monkeypatch():
    """It lives on `build_scenario` for the D20 reason -- a counterfactual a
    reader cannot find in the repo is not part of the design -- and it refuses
    a company it cannot build rather than constructing a negative memory."""
    src = inspect.getsource(pair.build_scenario)
    assert "organ_failure_window_drift_days" in src
    with pytest.raises(ValueError, match="negative memory"):
        pair.build_scenario(10, seed=7,
                            organ_failure_window_drift_days=-10_000)


# ---------------------------------------------------------------------------
# THE MEMORY GRID THE REGISTER DID NOT CHOOSE
# (atom D29_the_as_of_buffer_floors_the_memory_grid, H27 Expert Hour #11)
# ---------------------------------------------------------------------------
# D28 fixed the provenance of the TERMS grid and left its own lead standing:
# `measure_own_drift_resolution` still swept `own_invisible_drifts |
# own_visible_drifts`, so the belief saturation edge was a property of where
# D27 happened to look. On a grid derived from the BOOK -- every window value
# either side of every observed failure age, plus total amnesia -- the low tail
# saturates too, and it saturates because `as_of` sits AS_OF_BUFFER_DAYS past
# the last event, which is a second harness constant chosen to remove a
# confounder. Seventh escape of a register's own keying.
# ---------------------------------------------------------------------------


def test_the_memory_grid_is_derived_from_the_book_not_the_register():
    """THE ATOM D29 FIX, at its source, and the same assertion D28 earned one
    grid over: if `book_memory_grid`'s code can reach the register then the
    register is again choosing where it gets asked.

    It is also COMPLETE, not merely dense: an event at age `a` is counted iff
    `a <= window`, so the reading can only change as the window crosses an
    event age. Scoring `{a, a-1}` for every age therefore measures resolution
    over the whole real line, which no integer sweep of a bounded span does."""
    src = inspect.getsource(pair.book_memory_grid)
    tree = ast.parse(textwrap.dedent(src))
    ast.get_docstring(tree.body[0]) and tree.body[0].body.pop(0)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "DIMENSION_DRIFT_RESOLUTION" not in names, (
        "a grid derived from the register can only ask it what it already "
        "answered -- the defect D28 fixed one grid over")
    assert "OWN_DRIFT_BOOK_GRIDS" not in names

    records, _consumer, _ledger, as_of = pair.build_scenario(60, seed=7)
    ages = sorted({(as_of - r.due_date).days
                   for r in records if r.result == "failed"})
    grid = pair.book_memory_grid(records, as_of)
    w = pair.DD_FAILURE_WINDOW_DAYS
    assert set(grid) == {0, -w} | {a - w for a in ages} | {
        a - 1 - w for a in ages} | {ages[-1] - w + 1}
    # THE THREE EXTREMES, which are what a run needs two of at each end. D27's
    # grid held one point below the book and a collapsed run needs two, which
    # is exactly how a saturating tail was measured as `None` -- and the same
    # arithmetic at the top is the never-forgets witness (atom D27 pass 4,
    # tried by name in the next test).
    assert -w in grid, "total amnesia is the extreme of this parameter"
    assert min(grid) == -w
    assert max(grid) == max(0, ages[-1] - w + 1)


def test_the_memory_grid_carries_a_witness_above_its_saturation_point():
    """THE SAME DEFECT D29 NAMED AT THE BOTTOM, at the TOP -- and this grid
    INTRODUCES it rather than inheriting it (atom D27, BUILD pass 4).

    `oldest - window` is the grid's own top point AND the saturation drift: the
    first window that covers the whole book. A collapsed run needs two points,
    so with nothing above it the sweep can only ever report
    `saturates_above = None` about a book that provably saturates above. At the
    SHIPPED origin the register's `+1`/`+500` declarations are unioned into the
    sweep and supply that second point by accident, which is why this stayed
    invisible; at the organ's OWN default -- D27's candidate origin, where the
    declarations sit below the edge -- nothing does.

    The witness rests on a construction, not on a sweep: an event at age `a` is
    counted iff `a <= window`, and no event is older than `oldest`, so every
    window at or above `oldest` counts the SAME events. That equality is
    asserted here rather than assumed."""
    default = inspect.signature(
        pair.PaymentObservationConsumer.__init__
    ).parameters["dd_failure_window_days"].default
    records, _consumer, _ledger, as_of = pair.build_scenario(_RES_N, seed=7)
    ages = sorted({(as_of - r.due_date).days
                   for r in records if r.result == "failed"})
    assert ages and ages[-1] > default, (
        "this book no longer outruns the organ's own memory -- the edge this "
        "witness is about has moved and D27's band needs re-deriving")

    def counted(window):
        return tuple(a for a in ages if a <= window)

    for w in (pair.DD_FAILURE_WINDOW_DAYS, default):
        grid = pair.book_memory_grid(records, as_of, window_days=w)
        saturation_drift = ages[-1] - w
        assert saturation_drift in grid
        # `!= 0` because the sweep scores drift 0 as the BASELINE every other
        # company is compared against -- it is never a member of a run, so a
        # grid whose only point above the edge is 0 has none.
        witnesses = [k for k in grid if k > saturation_drift and k != 0]
        assert witnesses, (
            f"window {w}: the grid stops AT its saturation drift "
            f"{saturation_drift}, so the top run has one member and this "
            "instrument must measure `saturates_above = None` on a book that "
            "saturates above")
        for k in witnesses:
            assert counted(w + k) == counted(w + saturation_drift), (
                f"window {w}: drift {k} is offered as a never-forgets witness "
                "and counts a different set of events")

        # THE MUTATION (R15): the grid as D29 left it, on the same book. It has
        # nothing above the edge at EITHER origin -- at the shipped one the
        # downstream union hid that, at the organ's default nothing would.
        pre_witness = {0, -w} | {a - w for a in ages} | {
            a - 1 - w for a in ages}
        assert not [k for k in pre_witness if k > saturation_drift and k != 0]
        assert max(pre_witness) == max(0, saturation_drift)

    # AND IT IS NOT THE CLAMPED HELPER. `never_forgets_drift_days` floors at 0
    # to say something about the SCORED company, so at the shipped origin it
    # answers 0 and `+ 1` would put the witness at +1 -- above the edge, but
    # 309 days above it, which is the accident this test exists to replace.
    assert pair.never_forgets_drift_days(records, as_of) == 0
    assert 1 not in pair.book_memory_grid(records, as_of)


def test_a_knob_with_no_book_grid_raises_rather_than_asking_the_register():
    """THE FAIL-CLOSED (atom D29). The next off-path entry to name a knob must
    bring a book-derived grid with it; falling back to the declarations is the
    defect itself, and a silent fallback would put it straight back."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    register["belief"]["own_drift"] = "organ_terms_drift_days"
    with pytest.raises(AssertionError, match="no book-derived grid"):
        pair.measure_own_drift_resolution(
            n_customers=60, seeds=(7,), register=register,
            runner=lambda knob, seed, k: _run_window(seed, k))


def test_the_belief_memory_saturates_below_as_well_as_above(
        own_drift_resolution):
    """THE ATOM D29 FINDING, measured. The book's YOUNGEST observed failure is
    ~30d old (`AS_OF_BUFFER_DAYS`), so every company memory of 29d or less
    counts nothing at all: a supplier that forgets a failed collection after
    three weeks and one that never remembers it are ONE number here. D27
    declared `own_saturates_below = None` on this same instrument because the
    grid it swept held a single point down there."""
    for dim in ("belief", "belief_population_mix"):
        row, entry = (own_drift_resolution[dim],
                      pair.DIMENSION_DRIFT_RESOLUTION[dim])
        assert row["saturates_below"] is not None, (
            f"{dim}: the low tail reads as bounded -- which is what a grid of "
            "the register's own claims could not tell you")
        assert row["saturates_below"] == entry["own_saturates_below"]
        floor = min(b["amnesia_floor_window_days"]
                    for b in row["books"].values())
        assert row["saturates_below"] == floor - pair.DD_FAILURE_WINDOW_DAYS
        # THE COMPANIES THAT COLLAPSE INTO IT, named rather than counted.
        run = next(r for r in row["collapsed_runs"]
                   if min(row["drifts"]) in r)
        assert -pair.DD_FAILURE_WINDOW_DAYS in run and len(run) >= 2, run
        # AND THE TWO TAILS HAVE TWO OWNERS. One field named the one that had
        # been looked at.
        assert (entry["own_saturation_atom_below"]
                != entry["own_saturation_atom_above"]), (
            f"{dim}: both tails point at one atom -- they stop for different "
            "reasons (the company outruns the book above; `as_of` outruns it "
            "below)")


def test_the_book_predicts_both_edges_and_the_sweep_measured_them(
        own_drift_resolution):
    """R15 INDEPENDENCE, on both edges now. The predictor reads the WORLD's
    event dates and the declared window; the sweep re-scores through the
    dimension's own shipped scorer. D27 had this pair on the upper edge only,
    which is why the lower one could read `None` with nothing to disagree.

    The claim is ONE-DIRECTIONAL, as the predictor's own docstring says:
    beyond the predicted edge no event changes side, so the sweep must not
    read movement there. Inside it a dimension may saturate EARLIER -- and one
    does, which is a real difference between two published numbers."""
    for dim in ("belief", "belief_population_mix"):
        row = own_drift_resolution[dim]
        below = min(b["predicted_saturates_below_drift"]
                    for b in row["books"].values())
        above = max(b["predicted_saturates_above_drift"]
                    for b in row["books"].values())
        assert row["saturates_below"] >= below
        assert row["saturates_above"] <= above
        # Beyond either edge no event changes side, so every company out there
        # must land in ONE run -- not merely differ from the baseline, which
        # a company that counts nothing obviously does.
        for edge, beyond in ((below, lambda k: k <= below),
                             (above, lambda k: k >= above)):
            out_there = [k for k in row["drifts"] if beyond(k)]
            run = next(r for r in row["collapsed_runs"] if edge in r)
            assert set(out_there) <= set(run), (
                f"{dim}: {sorted(set(out_there) - set(run))} sit beyond "
                f"{edge:+d}d, where no event can change side, and the sweep "
                "reads them apart")
    # THE DIFFERENTIAL the register asserted away by never scoring -309: the
    # mix dimension is one day BLINDER than its sibling, because dropping the
    # oldest events moves an account's tier without moving the population mix.
    assert (own_drift_resolution["belief_population_mix"]["saturates_above"]
            < own_drift_resolution["belief"]["saturates_above"])


def test_a_visible_drift_inside_a_collapsed_run_fires_by_name(
        own_drift_resolution):
    """D28 saw this in prose -- "the -8 the old grid read as MOVED sits inside
    the saturated tail" -- and built no rule, so `belief` went on declaring
    -380d VISIBLE while a company that forgets everything and one that
    remembers 20 days publish one number. Differing from the baseline is not
    resolution; being read apart from your NEIGHBOURS is."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    entry = register["belief"]
    run = next(r for r in entry["own_collapsed_runs"]
               if min(own_drift_resolution["belief"]["drifts"]) in r)
    # THE PRE-D29 DECLARATION, restored: a drift inside the low saturated run.
    entry["own_visible_drifts"] = tuple(
        [max(run)] + [k for k in entry["own_visible_drifts"]])
    violations = pair.check_own_drift_resolution(
        own_drift_resolution, register=register)
    assert any("sits inside the collapsed run" in v for v in violations), \
        violations
    # And the shipped declaration does NOT trip it.
    assert not [v for v in pair.check_own_drift_resolution(own_drift_resolution)
                if "sits inside the collapsed run" in v]


@pytest.mark.parametrize("mutate,expected", (
    # THE EDGE THAT WAS MEASURED AS ABSENT. A register that forgets the low
    # tail is exactly the pre-D29 state.
    (lambda r: r["belief"].update(own_saturates_below=None),
     "measured saturates_below"),
    # AN OWNER FOR ONE TAIL ONLY -- the field D29 split in two.
    (lambda r: r["belief"].pop("own_saturation_atom_below"),
     "own_saturation_atom_below"),
    # A COLLAPSE THE DENSE GRID FOUND, un-declared.
    (lambda r: r["belief"].update(own_collapsed_runs=(
        (-308, -100, -1, 0, 1, 500),)),
     "publish ONE bit-identical reading"),
    # A DRIFT THE SWEEP READS APART, declared collapsed.
    (lambda r: r["belief"].update(
        own_collapsed_runs=tuple(r["belief"]["own_collapsed_runs"])
        + ((-350, -320),)),
     "COLLAPSE and the sweep reads them apart"),
))
def test_a_lying_memory_saturation_fires_by_name(own_drift_resolution, mutate,
                                                 expected):
    """R15 ON THE REGISTER, for the fields atom D29 added. Each of these left
    the suite green before this Hour."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    mutate(register)
    violations = pair.check_own_drift_resolution(
        own_drift_resolution, register=register)
    assert any(expected in v for v in violations), violations


@pytest.mark.parametrize("edge,field,delta", (
    ("saturates_below", "predicted_saturates_below_drift", -1),
    ("saturates_above", "predicted_saturates_above_drift", +1),
))
def test_a_sweep_that_outruns_the_book_fires_by_name(own_drift_resolution,
                                                     edge, field, delta):
    """R15 ON THE SOURCE. If the sweep reads resolution beyond the edge the
    BOOK proves, one of the two describes an instrument that is not there --
    and the caveat published beside the figure quotes the book."""
    row = copy.deepcopy(own_drift_resolution["belief"])
    row[edge] = row[edge] + delta * 40
    violations = pair._check_book_predicts_both_edges("belief", row)
    assert any("the book proves it stops by" in v for v in violations), \
        violations


def test_the_memory_caveat_names_both_edges():
    """STAMPED AT SOURCE, both edges (D22: the ledger writer, the live wiring
    and the dashboard read `components` and never the prose). A caveat that
    names only the tail somebody swept is the D27 state."""
    records, _c, _l, as_of = pair.build_scenario(60, seed=7)
    book = pair.measure_belief_window_resolution(records, as_of)
    caveat = pair.belief_resolution_caveat(book)
    assert "NEVER forgets" in caveat and "total amnesia" in caveat
    assert str(book["amnesia_floor_window_days"]) in caveat
    assert book["amnesia_floor_window_days"] == book[
        "newest_event_age_days"] - 1


# ---------------------------------------------------------------------------
# THE CENSUS OF CONFOUNDER-REMOVING CONSTANTS
# (atom D30_the_belief_band_is_this_books_length, H27 Expert Hour #12)
# ---------------------------------------------------------------------------
# R15 both ways. The census is only worth having if it can fail on its own
# named defect: an uncensused scenario constant, a constant whose declared
# effect is not the one it has, a predictor that has drifted off the book it
# claims to describe, and a saturation edge owned by an atom outside the
# census -- which is the defect this Hour actually found.


@pytest.fixture(scope="module")
def constant_census():
    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    return pair.measure_scenario_constant_census(records, as_of)


def test_the_census_holds_on_every_resolution_seed():
    """THE SHIPPED STATE. All three seeds, because the band is an all-seed
    claim: a book whose span depended on the draw would make every ownership
    claim below a property of which seed came first."""
    for seed in pair.RESOLUTION_SEEDS:
        records, _c, _l, as_of = pair.build_scenario(300, seed=seed)
        measured = pair.measure_scenario_constant_census(records, as_of)
        assert pair.check_scenario_constant_census(measured) == [], seed
        assert measured["describes_this_book"], seed
        assert measured["predicted"] == {
            "youngest_age_days": 30, "oldest_age_days": 92, "span_days": 62}


def test_the_census_subject_comes_off_build_scenario_not_a_hand_typed_list():
    """THE KEYSET IS DERIVED. Hand-typing it would supply the very defect --
    the constant nobody thought of is the one silently setting an edge -- so
    `scenario_constants` reads `build_scenario`'s AST and the census may never
    name its own subject."""
    src = inspect.getsource(pair.scenario_constants)
    assert "build_scenario" in src and "ast.walk" in src
    # ON THE AST, not on the text: the docstring names the census on purpose
    # (it says what raises), and a text match would read that mention as a
    # read. What must not happen is the CODE reaching the register.
    derived = ast.parse(textwrap.dedent(src)).body[0]
    assert "SCENARIO_CONSTANT_CENSUS" not in {
        n.id for n in ast.walk(derived) if isinstance(n, ast.Name)}, (
        "the census's subject must not be derived from the census -- that is "
        "the register-asked-where-it-answered class (D28/D29)")
    tree = ast.parse(inspect.getsource(pair.build_scenario))
    read = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert set(pair.scenario_constants()) <= read


def test_an_uncensused_scenario_constant_fires(constant_census):
    """R15 MUTATION 1, and it is the class this Hour closes: D27 and D29 were
    each found by an Hour tripping over a constant. A ninth constant added to
    the scenario and left uncensused must raise instead of waiting."""
    census = copy.deepcopy(pair.SCENARIO_CONSTANT_CENSUS)
    del census["N_PERIODS"]
    violations = pair.check_scenario_constant_census(constant_census, census=census)
    assert any(v.startswith("N_PERIODS: `build_scenario` reads it")
               for v in violations), violations


def test_a_census_entry_outliving_its_constant_fires(constant_census):
    """R15 MUTATION 2, the other direction. A census claim about a constant the
    scenario no longer builds from is a debt entry outliving its debt."""
    census = copy.deepcopy(pair.SCENARIO_CONSTANT_CENSUS)
    census["RETIRED_CONSTANT_DAYS"] = {
        "bounds_resolution": False, "sets_edges": (), "owning_atom": None,
        "why": "not read by build_scenario"}
    violations = pair.check_scenario_constant_census(constant_census, census=census)
    assert any("no longer reads it" in v for v in violations), violations


@pytest.mark.parametrize("name", ["N_PERIODS", "PERIOD_SPACING_DAYS",
                                  "BILLING_CYCLE_SPREAD_DAYS",
                                  "AS_OF_BUFFER_DAYS"])
def test_a_band_constant_declared_inert_fires(constant_census, name):
    """R15 MUTATION 3, on every constant that sets an edge. The effect is
    MEASURED by perturbing the predictor, so declaring a band constant inert
    cannot buy it a pass -- which is exactly what the register did to the upper
    edge for three Hours."""
    census = copy.deepcopy(pair.SCENARIO_CONSTANT_CENSUS)
    census[name] = dict(census[name], bounds_resolution=False, sets_edges=())
    violations = pair.check_scenario_constant_census(constant_census, census=census)
    assert any(v.startswith(f"{name}: bounds_resolution=False")
               for v in violations), violations


def test_an_inert_constant_declared_to_bound_the_band_fires(constant_census):
    """R15 MUTATION 4, and the differential half. A census on which every entry
    answers the same way cannot discriminate: claiming an edge for a constant
    that moves neither must fail too, or `bounds_resolution` is free."""
    census = copy.deepcopy(pair.SCENARIO_CONSTANT_CENSUS)
    census["BILL_AMOUNT_GBP"] = dict(
        census["BILL_AMOUNT_GBP"], bounds_resolution=True,
        sets_edges=("oldest_age_days",), owning_atom="D30_the_belief_band_is_this_books_length")
    violations = pair.check_scenario_constant_census(constant_census, census=census)
    assert any(v.startswith("BILL_AMOUNT_GBP: declared to set")
               for v in violations), violations


def test_an_unowned_band_constant_fires(constant_census):
    """R15 MUTATION 5. An unowned resolution constant is a silent one, which is
    the whole class -- the census may not record an edge with nobody's name
    against it."""
    census = copy.deepcopy(pair.SCENARIO_CONSTANT_CENSUS)
    census["PERIOD_SPACING_DAYS"] = dict(
        census["PERIOD_SPACING_DAYS"], owning_atom=None)
    violations = pair.check_scenario_constant_census(constant_census, census=census)
    assert any("no atom owns it" in v for v in violations), violations


def test_an_edge_owner_outside_the_census_fires(constant_census):
    """R15 MUTATION 6 -- THE DEFECT THIS HOUR FOUND, pinned as a rule. Before
    this Hour both belief entries owned their upper edge with
    `D27_belief_window_saturates_on_this_book`: "the company's memory outruns
    the book", which names no constant and attributes the harness's own
    calendar to the company being graded."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    for dim in ("belief", "belief_population_mix"):
        register[dim]["own_saturation_atom_above"] = (
            "D27_belief_window_saturates_on_this_book")
    violations = pair.check_scenario_constant_census(
        constant_census, register=register)
    assert len(violations) == 2, violations
    assert all("names an atom the census does not put on the "
               "oldest_age_days edge" in v for v in violations)


def test_the_shipped_register_owns_both_edges_from_the_census():
    """THE POST-FIX STATE, asserted rather than assumed. Both belief entries'
    edge owners must be atoms the census puts on that edge."""
    for dim in ("belief", "belief_population_mix"):
        entry = pair.DIMENSION_DRIFT_RESOLUTION[dim]
        assert entry["own_saturation_atom_above"] == (
            "D30_the_belief_band_is_this_books_length")
        assert entry["own_saturation_atom_below"] == (
            "D29_the_as_of_buffer_floors_the_memory_grid")


def test_the_predictor_reads_constants_and_never_the_book():
    """INDEPENDENCE (R15). The cross-check is only a second opinion if the two
    sides are computed from different things: the predictor takes no records,
    no seed and no draw -- asserted against its own AST."""
    tree = ast.parse(textwrap.dedent(
        inspect.getsource(pair.predict_event_age_span_from_constants))).body[0]
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert not (names & {"records", "PeriodRecord", "build_scenario",
                         "score_triad", "DIMENSION_DRIFT_RESOLUTION"})
    assert "records" not in {a.arg for a in tree.args.kwonlyargs + tree.args.args}


@pytest.mark.parametrize("knob,delta", (
    ("as_of_buffer_days", 5), ("n_periods", 1),
    ("period_spacing_days", 3), ("cycle_spread_days", 4),
))
def test_a_predictor_that_drifts_off_the_book_fires(constant_census, knob, delta):
    """R15 SOURCE MUTATION. Move the arithmetic away from `build_scenario` and
    the cross-check against the BUILT book must catch it -- otherwise every
    ownership claim in the census is being made about a band nobody presents.
    """
    current = pair.predict_event_age_span_from_constants()
    drifted = dict(constant_census)
    drifted["predicted"] = pair.predict_event_age_span_from_constants(
        **{knob: getattr(pair, {
            "as_of_buffer_days": "AS_OF_BUFFER_DAYS",
            "n_periods": "N_PERIODS",
            "period_spacing_days": "PERIOD_SPACING_DAYS",
            "cycle_spread_days": "BILLING_CYCLE_SPREAD_DAYS"}[knob]) + delta})
    assert drifted["predicted"] != current
    violations = pair.check_scenario_constant_census(drifted)
    assert any("has drifted off `build_scenario`" in v
               for v in violations), violations


def test_an_empty_book_cannot_read_as_an_agreeing_one(constant_census):
    """FAIL-CLOSED ON VACUITY. A population presenting no invoice has no band
    to cross-check, and an unmeasured band that reads like an agreeing one is
    the fail-open shape D29 closed on the saturation edges."""
    empty = dict(constant_census, measured_youngest_age_days=None,
                 measured_oldest_age_days=None)
    violations = pair.check_scenario_constant_census(empty)
    assert any("cannot be cross-checked" in v for v in violations), violations


def test_the_scored_company_sits_outside_the_band_it_is_graded_on():
    """THE HOUR'S FINDING, measured not asserted (R12: reported, never tuned).
    The band tops out at the book's oldest invoice age; the scored company
    holds `DD_FAILURE_WINDOW_DAYS` of memory, far above it -- so every belief
    figure is read where that parameter is inert by construction."""
    for seed in pair.RESOLUTION_SEEDS:
        records, _c, _l, as_of = pair.build_scenario(300, seed=seed)
        measured = pair.measure_scenario_constant_census(records, as_of)
        assert measured["scored_company_is_inert"] is True, seed
        assert measured["scored_company_headroom_days"] == 308, seed
        assert measured["scored_company_window_days"] == pair.DD_FAILURE_WINDOW_DAYS


def test_the_census_caveat_travels_with_both_belief_figures():
    """STAMPED AT SOURCE, on the NOTE and on the COMPONENTS (D22): the ledger
    writer, the live wiring and the dashboard read `components` and never the
    prose, so a limit only the prose carries is one the machine strips off."""
    records, consumer, _l, as_of = pair.build_scenario(300, seed=7)
    result = pair.score_triad(records, consumer, as_of)
    for dim in ("belief", "belief_population_mix"):
        got = result[dim]
        assert "THE BAND IS THE BOOK'S LENGTH" in got.note
        assert got.components["scenario_constant_census_caveat"] in got.note
        assert got.components["scored_company_is_inert"] is True
        assert set(got.components["band_owning_constants"]) == {
            "AS_OF_BUFFER_DAYS", "N_PERIODS", "PERIOD_SPACING_DAYS",
            "BILLING_CYCLE_SPREAD_DAYS"}
        assert "308d past the top of the band" in got.note


def test_the_caveat_refuses_to_attribute_a_book_the_constants_do_not_describe():
    """THE LIVE-POPULATION FAIL-OPEN, closed. `score_triad` also scores
    `run_phase2b` populations, whose book these constants do not build --
    quoting this scenario's [30, 92] over somebody else's population would be
    publishing one book's limit against another's figure."""
    flat, _c, _l, flat_as_of = pair.build_scenario(300, seed=7, cycle_spread_days=1)
    measured = pair.measure_scenario_constant_census(flat, flat_as_of)
    assert measured["describes_this_book"] is False
    caveat = pair.scenario_constant_census_caveat(measured)
    assert "NOT the offline scenario's book" in caveat
    assert "do not attribute these edges" in caveat
    # The band it DOES report is the flat book's own, measured here.
    assert f"between {measured['measured_youngest_age_days']}d and " \
           f"{measured['measured_oldest_age_days']}d" in caveat


# ---------------------------------------------------------------------------
# THE BELIEF EDGES' POPULATION AXIS, and the census's own subject -- atom D30,
# 2026-08-18, closing
# WORKER_FINDING_THE_BELIEF_BAND_CENSUS_IS_BLIND_TO_THE_POPULATION_THAT_SETS_THE_EDGE
#
# THE SIBLING HALF OF WHAT D28 REPAIRED THAT MORNING. The detection register's
# edges got a scope, an axis, a sweep, a control and a per-run derivation on
# 2026-08-18; the two BELIEF entries sat one register over with four unscoped
# literals and got none of them -- while both their edges move 20d (above) and
# 29d (below) on the DRAW SIZE alone.
#
# And the control that was meant to stop exactly that rot was FAIL-OPEN: the
# census ages EVERY record while the edges are read off OBSERVED FAILURES only,
# so `describes_this_book` answered True with zero violations on books whose
# failure-side edge was twenty days off the declaration. Three legs, three
# repairs, each with its own mutation below.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def belief_band_axis():
    """The two belief edges on 21 books: 7 draw sizes x 3 seeds,
    predictor-only."""
    return pair.measure_belief_band_population_axis()


def test_the_belief_edges_move_on_the_draw_size_alone(belief_band_axis):
    """THE FINDING ITSELF, reproduced as a control rather than a table in a
    document. Until 2026-08-18 the register declared one pair of numbers for
    both edges and named no population -- and the pair is the LARGE-n
    asymptote of a quantity the draw size moves by three weeks."""
    assert len(belief_band_axis["above_edges"]) > 1, (
        "a single distinct upper edge would mean the finding was wrong and the "
        "literal was a property of the instrument after all")
    assert len(belief_band_axis["below_edges"]) > 1
    above_spread = max(v for v in belief_band_axis["above_spread_by_seed"].values())
    below_spread = max(v for v in belief_band_axis["below_spread_by_seed"].values())
    assert above_spread >= 20, above_spread
    assert below_spread >= 29, below_spread
    # And the declared asymptote is at the EDGE of what the axis reads, never
    # in the middle of it -- which is what "asymptote" has to mean here.
    declared = pair.DIMENSION_DRIFT_RESOLUTION["belief"]["own_saturates_above"]
    assert declared == belief_band_axis["above_edge_range"][1]


def test_the_invoice_span_is_the_null_control_and_does_not_move(belief_band_axis):
    """THE NULL CONTROL the finding owed, and it must stay GREEN or every
    reading above is draw noise: the sweep moves the SAMPLE, not the LAW. The
    invoice-side span is dense by construction -- every account draws every
    period -- so it reaches the constants' band at every draw size on this axis
    while the failure span, which needs a failure to LAND on the extreme
    invoice, does not."""
    assert belief_band_axis["invoice_spans"] == ((30, 92),), (
        "if the population the edges are NOT read from moved too, this sweep "
        "would be perturbing the law and the failure-side movement would be "
        "evidence of nothing")
    predicted = pair.predict_event_age_span_from_constants()
    assert (predicted["youngest_age_days"],
            predicted["oldest_age_days"]) == (30, 92)
    assert pair.check_belief_band_population_axis(belief_band_axis) == []


@pytest.mark.parametrize("mutate,expected", [
    (lambda r: r["belief"].pop("own_saturation_scope"),
     "declares its saturation edges and no `own_saturation_scope`"),
    (lambda r: r["belief_population_mix"].pop("own_saturation_scope"),
     "belief_population_mix: declares its saturation edges and no"),
    (lambda r: r["belief"]["own_saturation_scope"].__setitem__(
        "n_customers", 999),
     "which this axis never visits"),
    (lambda r: r["belief"]["own_draw_size_axis"].__setitem__(
        "above_edge_range", (-320, -308)),
     "declares its above edge inside [-320, -308]"),
    (lambda r: r["belief"]["own_draw_size_axis"].__setitem__(
        "below_edge_range", (-371, -360)),
     "declares its below edge inside [-371, -360]"),
    (lambda r: r["belief"].__setitem__("own_saturates_above", -200),
     "a declaration outside every measurement is a number from nowhere"),
    (lambda r: r["belief"]["own_draw_size_axis"].__setitem__(
        "invoice_span_invariant", (30, 88)),
     "NULL CONTROL"),
])
def test_the_belief_axis_control_fires_on_its_own_named_defects(
        belief_band_axis, mutate, expected):
    """R15: a control counts as evidence only once a mutation proves it fires.
    The first case is the SHIPPED DEFECT itself -- edges declared with no
    scope -- and the second proves the rule reaches the SIBLING entry, which is
    the half D28's repair left behind one register over."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    mutate(register)
    violations = pair.check_belief_band_population_axis(
        belief_band_axis, register=register)
    assert any(expected in v for v in violations), violations


def test_pinning_the_population_hides_the_belief_draw_size_defect():
    """THE MUTATION THE FINDING SPECIFIED, and the one that names the class:
    pin the sweep to a single `n_customers` -- exactly what
    `measure_own_drift_resolution(n_customers=300)` does at its sole call site
    in `main()`, whose own `--customers` defaults to 4000 -- and the spread
    the finding rests on vanishes with the defect untouched.

    Nothing about the register or the book changed between these two calls;
    only which populations the control was allowed to look at. That is why this
    is filed as a CONTROL finding and not merely a number finding."""
    pinned = pair.measure_belief_band_population_axis(n_customers=(300,))
    assert set(pinned["above_spread_by_seed"].values()) == {0}
    assert set(pinned["below_spread_by_seed"].values()) == {0}, (
        "at one draw size there is no spread to see -- the harness default "
        "chose the subject")
    violations = pair.check_belief_band_population_axis(pinned)
    assert any("no seed's edge moved" in v for v in violations), (
        "and the control must SAY it was asked at one draw size rather than "
        "passing quietly -- a pinned axis is an unasked question, not a green "
        "one")


def test_widening_the_axis_below_its_floor_turns_the_verdict_red():
    """THE MUTATION LEG 3 OWED, and the one the seven-case matrix above cannot
    contain: those cases all mutate the REGISTER and evaluate against a fixed
    shipped-axis fixture, so the AXIS -- the input that actually decides the
    verdict -- was never moved. Widen it downward and the sweep stops being
    sound: at n = 14 seed 23's invoice span reads (31, 91) and the NULL CONTROL
    fires, which is the whole reason the floor is where it is."""
    widened = pair.measure_belief_band_population_axis(
        n_customers=(14, 17, 24, 40, 60, 120, 300), seeds=(7, 11, 23))
    violations = pair.check_belief_band_population_axis(widened)
    assert any("NULL CONTROL" in v for v in violations), (
        "an axis floor that can be moved with no control noticing is a subject "
        "chosen rather than derived")


def test_the_band_shipped_before_this_repair_is_false_at_the_derived_floor():
    """LEG 1 OF THE FINDING, kept as a control so it cannot be reintroduced.
    D30 declared (-328, -308) and floored the axis at 24; at the DERIVED floor
    of 17 the sweep reads -333 on seed 23 while the null control stays green,
    so the old band is false over books its own soundness criterion admits. The
    floor decided the verdict, and nothing else did."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    for dim in ("belief", "belief_population_mix"):
        register[dim]["own_draw_size_axis"]["above_edge_range"] = (-328, -308)
    measured = pair.measure_belief_band_population_axis()
    assert measured["above_edge_range"] == (-333, -308)
    assert measured["invoice_spans"] == ((30, 92),), (
        "and the null control is GREEN in the red case -- if it were not, the "
        "reading would be draw noise rather than a false declaration")
    violations = pair.check_belief_band_population_axis(
        measured, register=register)
    assert 2 == len([v for v in violations
                     if "declares its above edge inside [-328, -308]" in v]), (
        violations)


def test_the_axis_floor_is_derived_and_not_declared():
    """THE REPAIR ITSELF: the floor is the smallest n at which the null control
    holds and keeps holding, computed from the constants-side span predictor --
    which reads no book, no draw and no register entry, so this is a trial and
    not a comparison of the register with itself."""
    measured = pair.measure_belief_axis_null_control_floor()
    assert measured["predicted_span"] == (30, 92)
    assert measured["floor"] == 17
    assert measured["green_by_n"][16] is False, (
        "16 is the last book on which the sweep would be perturbing the law")
    assert all(measured["green_by_n"][n] for n in measured["candidates"]
               if n >= 17)
    assert pair.check_belief_axis_floor_is_derived(measured) == []
    for dim in ("belief", "belief_population_mix"):
        axis = pair.DIMENSION_DRIFT_RESOLUTION[dim]["own_draw_size_axis"]
        assert min(axis["n_customers"]) == measured["floor"], (
            f"{dim} declares a floor the derivation does not produce")


@pytest.mark.parametrize("mutate,expected", [
    # THE SHIPPED DEFECT: 24 was the floor D30 chose, seven customers above
    # where its own stated reason runs out.
    (lambda r: [r[d]["own_draw_size_axis"].__setitem__(
        "n_customers", (24, 40, 60, 120, 300, 600, 1200))
        for d in ("belief", "belief_population_mix")],
     "ABOVE the derivation"),
    # And the sibling half alone, which is how D28's repair left this class
    # standing one register over.
    (lambda r: r["belief_population_mix"]["own_draw_size_axis"].__setitem__(
        "n_customers", (24, 40, 300)),
     "belief_population_mix: declares an axis floor of n = 24"),
    (lambda r: r["belief"]["own_draw_size_axis"].__setitem__(
        "n_customers", (14, 17, 24, 300)),
     "BELOW the derivation"),
])
def test_the_floor_control_fires_on_a_floor_that_was_chosen(mutate, expected):
    """R15 on the new rule, both directions. A floor above the derivation hides
    the books where the declaration is false; a floor below it admits books
    where the sweep moves the law."""
    register = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    mutate(register)
    measured = pair.measure_belief_axis_null_control_floor()
    violations = pair.check_belief_axis_floor_is_derived(
        measured, register=register)
    assert any(expected in v for v in violations), violations


def test_the_floor_derivation_cannot_pass_by_being_unavailable():
    """R15's FAIL-OPEN and FAIL-SILENT patterns on the derivation itself.

    A probe range that starts ABOVE the break returns its own first element and
    would certify any floor equal to it; a probe range where the null control is
    never green returns nothing at all, and 'nothing' must be a violation rather
    than a quiet pass on the declared literal."""
    truncated = pair.measure_belief_axis_null_control_floor(probe_range=(20, 30))
    assert truncated["floor"] == 20 and truncated["lowest_candidate_green"]
    assert any("TRUNCATED" in v for v in
               pair.check_belief_axis_floor_is_derived(truncated)), (
        "a search that starts above the break has not found it")

    dead = pair.measure_belief_axis_null_control_floor(probe_range=(10, 13))
    assert dead["floor"] is None
    assert any("could not be DERIVED" in v for v in
               pair.check_belief_axis_floor_is_derived(dead)), (
        "an unavailable derivation is a FAILED derivation")


def test_the_floor_derivation_reads_no_declaration_it_grades():
    """INDEPENDENCE (R15's TAUTOLOGY pattern). The derivation may read the
    probe range and the seeds -- which say where to look -- and must NOT read
    the declared band, the declared invariant or the declared floor, which are
    what it is grading. Its target comes from the constants alone.

    GRADED WHERE THE WORK IS (2026-08-19). The derivation moved into
    `measure_axis_null_control_floor`, which takes its axis as an argument
    instead of naming one; `measure_belief_axis_null_control_floor` is now the
    thin selector that points it at the belief entry. Both are asserted --
    grading only the wrapper would let the body read anything it liked."""
    names = pair._names_in(pair.measure_axis_null_control_floor)
    assert "predict_event_age_span_from_constants" in names
    for forbidden in ("invoice_span_invariant", "above_edge_range",
                      "below_edge_range"):
        assert forbidden not in names, (
            f"the derivation reads {forbidden}, so it would agree with the "
            "register by construction")
    assert "score_triad" not in names
    wrapper = pair._names_in(pair.measure_belief_axis_null_control_floor)
    assert "measure_axis_null_control_floor" in wrapper
    for forbidden in ("invoice_span_invariant", "above_edge_range",
                      "below_edge_range", "score_triad"):
        assert forbidden not in wrapper


# ---------------------------------------------------------------------------
# THE CLASS CONTROL: WHICH AXES GET GRADED
# (2026-08-19, the repair
#  WORKER_FINDING_THE_SIBLING_AXIS_FLOOR_IS_A_FREE_LITERAL_AND_ITS_CONTROL_
#  CANNOT_FAIL_ON_IT asked for; H27 Expert Hour #41)
# ---------------------------------------------------------------------------
# The tests above grade the floors the checker is HANDED. These grade which
# axes it is handed at all -- the question that let the detection floor keep a
# free literal through three consecutive repairs of exactly that defect.


@pytest.fixture(scope="module")
def axis_floors():
    """Every declared axis's floor, derived. ~3s, predictor-only."""
    return pair.measure_axis_null_control_floors()


def test_the_axis_population_is_walked_and_holds_the_sibling(axis_floors):
    """THE HOLE, named. `check_belief_axis_floor_is_derived` shipped iterating
    a hand-written `("belief", "belief_population_mix")` while a THIRD entry
    one register over declared an axis of the same shape with the same failure
    mode -- and kept the free literal the pair had just had derived away.

    The population is now walked, so the sibling is in it by declaration."""
    ids = {r["id"] for r in pair.draw_size_axis_population()}
    assert ids == {
        "DIMENSION_DRIFT_RESOLUTION[belief].own_draw_size_axis",
        "DIMENSION_DRIFT_RESOLUTION[belief_population_mix].own_draw_size_axis",
        "ORGAN_QUERY_GRID[flagged_via_reconciliation].draw_size_axis",
    }, "the walk must find all three, under BOTH key spellings"
    assert set(axis_floors) == ids, "and every one of them must be measured"
    assert pair.check_axis_floors_are_derived(axis_floors) == []


def test_the_detection_floor_is_derived_and_the_band_is_what_it_admits(
        axis_floors):
    """THE INSTANCE REPAIR, and the ORDER it was done in (R12).

    150 was a free literal: nothing derived it and no note said what it was the
    smallest n OF. The law-side null control -- the constants-side invoice span,
    which reads no draw, no seed and no register -- first holds and keeps
    holding at n = 51 on these five seeds. The declared band is then whatever
    that floor ADMITS: (70, 88) -> (49, 88), because 49 and 55 sit on books the
    null control passes and the shipped floor was excluding them.

    Never the other way round. A floor chosen to make a band true is the defect
    this whole block exists to close."""
    measured = axis_floors[
        "ORGAN_QUERY_GRID[flagged_via_reconciliation].draw_size_axis"]
    assert measured["floor"] == 51
    assert measured["green_by_n"][50] is False, (
        "50 is the last book on which the sweep would be perturbing the law")
    axis = pair.ORGAN_QUERY_GRID["flagged_via_reconciliation"]["draw_size_axis"]
    assert min(axis["n_customers"]) == measured["floor"]
    swept = pair.measure_recon_band_population_axis(
        n_customers=axis["n_customers"])
    assert swept["upper_edge_range"] == tuple(axis["upper_edge_range"]) == (49, 88)
    assert swept["lower_edges"] == (axis["lower_edge_invariant"],), (
        "the soundness null control must stay GREEN over the books the new "
        "floor admits, or the widened band is draw noise rather than a "
        "measurement the old floor was hiding")
    assert pair.check_recon_band_population_axis(swept) == []


def test_the_declared_null_control_cannot_derive_the_detection_floor():
    """THE PART THE FINDING GOT WRONG, pinned so it is not retried.

    The finding proposed deriving the detection floor off `lower_edge_invariant`
    -- this axis's own declared null control. It cannot: that edge is a BOUND
    attained by any invoice paid on its due date, so every book has hundreds of
    witnesses and it is green from n = 4. A control that never breaks inside the
    probe range has no break for a search to find, and the derivation would have
    returned its own starting point.

    That is why the law-side span invariant floors this axis instead, and why
    `lower_edge_invariant` stays what it always was: the soundness control."""
    closed_form = -(pair.DEFAULT_RECONCILIATION_GRACE_DAYS + 1)
    for n in (4, 8, 20):
        for seed in pair.ORGAN_QUERY_GRID[
                "flagged_via_reconciliation"]["draw_size_axis"]["seeds"]:
            records, consumer, _lb, as_of = pair.build_scenario(n, seed=seed)
            band = pair.predict_recon_saturation_band(records, consumer, as_of)
            assert band["saturates_below"] == closed_form, (
                f"n={n} seed={seed}: the declared null control is green here, "
                "which is exactly why it cannot locate a floor")
    # And a book that far below the derived floor is NOT one the declaration
    # holds on -- so a floor derived off it would have certified nonsense.
    tiny = pair.measure_recon_band_population_axis(n_customers=(4, 8))
    lo, hi = pair.ORGAN_QUERY_GRID[
        "flagged_via_reconciliation"]["draw_size_axis"]["upper_edge_range"]
    assert any(not (lo <= u <= hi) for u in tiny["upper_edges"]), (
        "books below the derived floor read edges outside the declared band -- "
        "an unbreakable null control would have admitted them")


@pytest.mark.parametrize("mutate,drop,expected", [
    # THE SHIPPED DEFECT: the detection floor as it was actually written.
    (lambda r: r["ORGAN_QUERY_GRID"]["flagged_via_reconciliation"][
        "draw_size_axis"].__setitem__(
            "n_customers", (150, 300, 600, 1200, 2400)),
     None,
     "declares an axis floor of n = 150 and the null control derives n = 51"),
    # THE MUTATION THE FINDING SPECIFIED, and the one no existing test asks:
    # every other mutation in this battery perturbs an entry the loop already
    # visits. This one perturbs WHICH ENTRIES THE LOOP VISITS.
    (lambda r: None, "ORGAN_QUERY_GRID",
     "declares a draw-size axis with floor n = 51 and NO derivation measured it"),
    # An axis nobody can floor must be a finding, never a silent skip.
    (lambda r: r["ORGAN_QUERY_GRID"]["flagged_via_reconciliation"][
        "draw_size_axis"].pop("floor_probe_range"),
     None, "and no `floor_probe_range`, so its floor cannot be derived at all"),
    # A FOURTH AXIS ADDED LATER is covered by construction -- the whole point of
    # deriving the population rather than extending a tuple.
    (lambda r: r["DIMENSION_DRIFT_RESOLUTION"]["ageing"].__setitem__(
        "own_draw_size_axis", {"n_customers": (9, 300), "seeds": (7, 11, 23)}),
     None, "DIMENSION_DRIFT_RESOLUTION[ageing].own_draw_size_axis"),
])
def test_the_class_control_fires_on_its_own_named_defects(
        axis_floors, mutate, drop, expected):
    """R15 on the class rule. A control counts as evidence only once a mutation
    proves it fires on the defect it exists for."""
    registers = {
        "DIMENSION_DRIFT_RESOLUTION": copy.deepcopy(
            pair.DIMENSION_DRIFT_RESOLUTION),
        "ORGAN_QUERY_GRID": copy.deepcopy(pair.ORGAN_QUERY_GRID),
    }
    mutate(registers)
    measured = ({k: v for k, v in axis_floors.items() if drop not in k}
                if drop else pair.measure_axis_null_control_floors(registers))
    violations = pair.check_axis_floors_are_derived(
        measured, registers=registers)
    assert any(expected in v for v in violations), violations


def test_an_empty_axis_population_is_a_violation_and_not_a_pass():
    """R15's FAIL-OPEN pattern on the walk itself. A derived population that
    derives nothing passes every downstream rule vacuously -- the enumerated
    loop's own failure shape with a walk in front of it, which would be a
    strictly worse place to leave this class than where it was found."""
    empty = {"DIMENSION_DRIFT_RESOLUTION": {}, "ORGAN_QUERY_GRID": {}}
    assert pair.draw_size_axis_population(empty) == ()
    violations = pair.check_axis_floors_are_derived({}, registers=empty)
    assert any("population is EMPTY" in v for v in violations)


def test_the_axis_walk_reads_both_key_spellings():
    """`draw_size_axis` and `own_draw_size_axis` diverged for no reason either
    declaration states. They are deliberately NOT renamed -- nine call sites to
    buy nothing the walk does not already buy -- so the walk accepting both is
    what makes the divergence harmless, and it is pinned rather than left to
    inspection."""
    assert set(pair._DRAW_SIZE_AXIS_KEYS) == {
        "draw_size_axis", "own_draw_size_axis"}
    for key in pair._DRAW_SIZE_AXIS_KEYS:
        found = pair.draw_size_axis_population(
            {"R": {"d": {key: {"n_customers": (5, 10), "seeds": (7,)}}}})
        assert [r["key"] for r in found] == [key]
    # An entry with the key but no draw sizes declares no axis, and must not
    # enter the population as a floorless member that can never go green.
    assert pair.draw_size_axis_population(
        {"R": {"d": {"draw_size_axis": {"seeds": (7,)}}}}) == ()


def test_the_belief_axis_predictor_never_calls_the_scorer():
    """The axis is affordable ONLY because it predicts. A sweep that reached
    `score_triad` would cost ~35 minutes instead of ~2 seconds, which is
    exactly why this question had never been asked of these two entries."""
    assert "score_triad" not in pair._names_in(
        pair.measure_belief_band_population_axis)
    assert "score_triad" not in pair._names_in(
        pair.measure_belief_window_resolution)


def test_the_census_measures_the_population_that_sets_the_edge():
    """LEG 3, THE FAIL-OPEN, pinned at a book that exhibits it. The census ages
    every record; the belief edges are read off observed FAILURES. At n=300
    seed 7 the two disagree -- invoices reach 92d, failures only 91d -- and
    before this repair the census reported `describes_this_book` True with ZERO
    violations, a green verdict about a band it had never looked at."""
    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    measured = pair.measure_scenario_constant_census(records, as_of)
    assert measured["describes_this_book"] is True
    assert measured["measured_oldest_age_days"] == 92
    assert measured["measured_failure_oldest_age_days"] == 91, (
        "this test is worthless on a book where the two spans coincide -- it "
        "must be pinned to one that exhibits the divergence")
    assert measured["describes_this_books_failure_span"] is False
    # The edge-setting population is the one `measure_belief_window_resolution`
    # reads, not a second implementation of it (the sibling-half class).
    resolution = pair.measure_belief_window_resolution(records, as_of)
    assert (measured["measured_failure_oldest_age_days"]
            == resolution["oldest_event_age_days"])
    assert measured["n_failure_events"] == resolution["n_events"]


def test_a_census_that_measures_only_the_invoice_span_fires():
    """R15 FAIL-OPEN ("passes on missing/zero/empty"), against the census's own
    subject: the SHIPPED measurement is the mutation here -- strip the
    failure-side keys and you have exactly what this module published until
    2026-08-18. It must raise rather than pass quietly."""
    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    measured = pair.measure_scenario_constant_census(records, as_of)
    assert pair.check_scenario_constant_census(measured) == []
    shipped = {k: v for k, v in measured.items()
               if not k.startswith(("n_failure", "measured_failure",
                                    "describes_this_books_failure"))}
    violations = pair.check_scenario_constant_census(shipped)
    assert any("green about a band it never looked at" in v
               for v in violations), violations


def test_a_book_with_invoices_and_no_failure_cannot_read_as_an_agreeing_one():
    """VACUITY, on the edge-setting side. A book presenting invoices and no
    observed failure sets NO belief edge at all -- and its invoice span still
    matches the constants perfectly, so the invoice-side cross-check would
    report agreement about a band that does not exist."""
    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    clean = [r for r in records if r.result != "failed"]
    assert clean, "a book with no records at all proves something else"
    measured = pair.measure_scenario_constant_census(clean, as_of)
    assert measured["n_failure_events"] == 0
    assert measured["measured_oldest_age_days"] is not None
    violations = pair.check_scenario_constant_census(measured)
    assert any("sets no belief edge at all" in v for v in violations), violations


def test_the_census_caveat_names_the_edge_setting_population():
    """R11-shaped: the repair has to reach the SENTENCE the reader meets, not
    only the measurement. The caveat published the INVOICE span as the band
    'both belief dimensions resolve a company memory error only between' --
    which is false on every book where a failure misses the extreme invoice."""
    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    measured = pair.measure_scenario_constant_census(records, as_of)
    caveat = pair.scenario_constant_census_caveat(measured)
    assert "OBSERVED FAILURES only" in caveat
    assert "30d to 91d" in caveat
    assert "THAT IS NOT THE INVOICE SPAN" in caveat
    # And the invoice band is still reported -- as the INVOICES', not as the
    # belief dimensions' resolution.
    assert "This book's INVOICES span ages between 30d and 92d" in caveat

    # On the book the module actually publishes from, the two coincide, so the
    # divergence clause must NOT fire (R12: no published figure moved here).
    big, _c2, _l2, big_as_of = pair.build_scenario(4000, seed=7)
    big_measured = pair.measure_scenario_constant_census(big, big_as_of)
    assert big_measured["describes_this_books_failure_span"] is True
    assert "THAT IS NOT THE INVOICE SPAN" not in (
        pair.scenario_constant_census_caveat(big_measured))


# ---------------------------------------------------------------------------
# atom D31_the_recon_grid_saturates_beyond_this_books_window (H27 Expert Hour
# #13, 2026-08-11): the register that FOUND the grid class was the last one
# still swept on its own declarations, and the shared saturation rule D29 built
# "so it cannot exist on one side and not the other" reached two of three knobs.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def recon_saturation():
    """Measured ONCE for the module: 110 counterfactual companies x 3 seeds on
    a grid derived from the BOOK (-30..+88, the declared drifts unioned in),
    against the 8 points the register's own declarations produced."""
    return pair.measure_organ_query_grid_saturation(n_customers=_RES_N)


def test_the_recon_grid_is_derived_from_the_book_not_the_register():
    """THE ATOM D31 FIX at its source, and the third time this assertion has
    had to be earned (D28 for the terms grid, D29 for the memory grid). If
    `book_recon_drift_grid` can reach a register then the register is again
    choosing where it gets asked.

    It is COMPLETE, not merely dense: `organ_query_dates` asks the organ daily
    from the invoice's ISSUE date to `as_of`, so below `issue - due - grace`
    every reading is the floor and above `as_of - due - grace` there is no
    reading at all. One integer per day between those crossings measures
    resolution over the whole real line."""
    names = pair._names_in(pair.book_recon_drift_grid)
    assert "ORGAN_QUERY_GRID" not in names, (
        "a grid derived from the register can only ask it what it already "
        "answered -- the defect D28 and D29 each fixed one grid over")
    assert "COUNTERFACTUAL_KNOB_ROUTE" not in names

    records, _c, _l, as_of = pair.build_scenario(60, seed=7)
    grid = pair.book_recon_drift_grid(records, as_of)
    lo = min((r.issue_date - r.due_date).days for r in records) - \
        pair.DEFAULT_RECONCILIATION_GRACE_DAYS - 1
    hi = max((as_of - r.due_date).days for r in records) - \
        pair.DEFAULT_RECONCILIATION_GRACE_DAYS + 1
    assert grid == tuple(range(lo, hi + 1))
    assert grid[0] == -(pair.PAYMENT_TERMS_DAYS
                        + pair.DEFAULT_RECONCILIATION_GRACE_DAYS) - 1


def test_every_counterfactual_knob_reaches_the_one_saturation_rule():
    """THE CLASS FIX (atom D31). D29 put the terms and memory sweeps through
    ONE `_check_saturation_and_collapse` so the rule could not exist on one
    side of `in_causal_path` and not the other -- and the RECONCILIATION knob,
    whose register started this line, was outside both. The route's keyset is
    DERIVED from the harness's own signatures, so a fourth knob cannot arrive
    without a book-derived grid and a checker that runs the rule."""
    knobs = pair.counterfactual_knobs()
    assert set(knobs) == {"organ_reconciliation_drift_days",
                          "organ_terms_drift_days",
                          "organ_failure_window_drift_days"}
    assert set(knobs) == set(pair.COUNTERFACTUAL_KNOB_ROUTE)
    assert pair.check_counterfactual_knob_route() == []
    # DERIVED, not typed: the subject comes off the signatures themselves.
    src = pair._names_in(pair.counterfactual_knobs)
    assert "COUNTERFACTUAL_KNOB_ROUTE" not in src


def test_a_knob_with_no_route_raises_rather_than_sweeping_the_declarations():
    """THE FAIL-CLOSED, one level up from D29's. A knob left out of the route
    would be swept on its register's own claims, which IS the defect, so the
    absence raises instead of returning a violation somebody can triage."""
    route = {k: v for k, v in pair.COUNTERFACTUAL_KNOB_ROUTE.items()
             if k != "organ_terms_drift_days"}
    with mock.patch.object(pair, "COUNTERFACTUAL_KNOB_ROUTE", route):
        with pytest.raises(AssertionError, match="no entry in"):
            pair.check_counterfactual_knob_route()


def test_a_checker_that_only_names_the_shared_rule_is_a_violation():
    """R15 on the route itself: naming a checker is not running one. This is
    the pre-D31 state written down -- `ORGAN_QUERY_GRID` had a checker, and it
    never reached the saturation rule, which is how sixteen collapses and two
    saturated tails sat undeclared under a green suite."""
    route = copy.deepcopy(pair.COUNTERFACTUAL_KNOB_ROUTE)
    route["organ_reconciliation_drift_days"]["checker"] = "check_ageing_resolution"
    with mock.patch.object(pair, "COUNTERFACTUAL_KNOB_ROUTE", route):
        violations = pair.check_counterfactual_knob_route()
    assert any("never calls `_check_saturation_and_collapse`" in v
               for v in violations), violations


def test_the_recon_register_is_measured_not_asserted(recon_saturation):
    """Every collapse, edge and undefined region re-derived from a fresh sweep
    each run. Green means the declared blindness is the blindness the code
    has -- not that there is none."""
    assert pair.check_organ_query_grid_saturation(recon_saturation) == []
    assert set(recon_saturation) == set(pair.ORGAN_QUERY_GRID)


def test_the_set_reading_saturates_in_both_tails(recon_saturation):
    """THE FINDING (atom D31), measured not asserted. The SET reading is the
    published `detection` gap, and on a grid it did not choose it has SIXTEEN
    groups of companies publishing one bit-identical figure on every seed.

    Below -6 every company has already flagged every invoice by `as_of` and
    the gap is the no-skill 0.5: a supplier flagging a week early and one
    flagging three weeks early are one number, and the register's two declared
    PAIRS were a 2-point sample of that fifteen-company tail."""
    row = recon_saturation["flagged_via_reconciliation"]
    assert len(row["collapsed_runs"]) == 16
    assert row["saturates_below"] == -6 and row["saturates_above"] == 82
    tail = next(r for r in row["collapsed_runs"] if row["drifts"][0] in r)
    assert len(tail) == 16 and max(tail) == -6
    for seed in row["seeds"]:
        assert row["by_seed"][seed]["by_drift"][-6] == 0.5, (
            "the flag-everything gap -- the no-skill baseline, reached by a "
            "company only six days early")
    # THE DATE READING IS THE DIFFERENTIAL: same grid, same knob, ONE run.
    date_row = recon_saturation["recon_lag_days"]
    assert len(date_row["collapsed_runs"]) == 1
    assert date_row["saturates_below"] == -19


def test_the_declared_evidence_of_resolution_was_inside_a_collapse(
        recon_saturation):
    """THE PRE-HOUR STATE, and it fires. `flagged_via_reconciliation` offered
    +7 as its evidence that the reading resolves the company; the book-derived
    sweep reads +6 and +7 as ONE number on every seed. Differing from the
    baseline is not resolution -- resolution is being told apart from your
    NEIGHBOURS (D29's rule, one register over, unenforced until D31)."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    register["flagged_via_reconciliation"]["visible_drifts"] = (-1, 7)
    violations = pair.check_organ_query_grid_saturation(
        recon_saturation, register=register)
    assert any("+7d is declared VISIBLE and sits inside the collapsed run"
               in v for v in violations), violations
    # And the replacement is read APART from both its neighbours.
    row = recon_saturation["flagged_via_reconciliation"]
    assert not any(8 in run for run in row["collapsed_runs"])


@pytest.mark.parametrize("mutate,expected", (
    (lambda r: r["flagged_via_reconciliation"].__setitem__(
        "collapsed_runs", pair._RECON_SET_COLLAPSED_RUNS[:1]),
     "publish ONE bit-identical reading"),
    (lambda r: r["recon_lag_days"].__setitem__(
        "collapsed_runs", ((-30, -20, -19), (3, 4))),
     "reads them apart"),
    (lambda r: r["recon_lag_days"].__setitem__("saturates_below", -18),
     "measured saturates_below=-19"),
    (lambda r: r["flagged_via_reconciliation"].__setitem__(
        "saturation_atom_above", None),
     "names no `saturation_atom_above`"),
    (lambda r: r["recon_lag_days"].__setitem__("undefined_drifts", ()),
     "published NO reading at drifts"),
    (lambda r: r["recon_lag_days"].__setitem__("undefined_drifts", (87, 88, 50)),
     "declares NO reading at drift +50d and the sweep read one"),
    (lambda r: r["recon_lag_days"].__setitem__("edge_constants", ("N_PERIODS",)),
     "reach no knob of"),
    (lambda r: r["recon_lag_days"].__setitem__(
        "edge_constants", ("PAYMENT_TERMS_DAYS",)),
     "attributed to a SUBSET of its owners"),
))
def test_a_lying_recon_declaration_fires_by_name(recon_saturation, mutate,
                                                 expected):
    """R15 both ways on the new fields: an undeclared collapse, a collapse the
    sweep reads apart, an understated edge, an unowned tail, a fail-open
    undefined region, a declared blank the sweep can read, and an attribution
    to constants that no longer reproduce the edge."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    mutate(register)
    violations = pair.check_organ_query_grid_saturation(
        recon_saturation, register=register)
    assert any(expected in v for v in violations), violations


def test_an_absent_reading_is_a_bound_only_with_its_witness(recon_saturation):
    """THE FAIL-OPEN D28 CLOSED FOR THE OTHER TWO KNOBS, live on this one. At
    +87/+88 no failure is detected before `as_of` at all, the latency
    population empties and the mean is None -- and `None != baseline` reads as
    MOVEMENT, so the instrument that had stopped reading was counted as
    resolution.

    Declaring the region is not enough: D24's distinction is that a bound is
    only a bound with a witness, so the population itself must be empty exactly
    where the reading is absent."""
    row = recon_saturation["recon_lag_days"]
    assert row["undefined_readings"] == (87, 88)
    witness = row["undefined_witness"]
    assert all(is_none == (pop == 0)
               for k in witness for is_none, pop in witness[k])
    # THE SEED THAT KEEPS THIS HONEST: at +87 one book still has a case, reads
    # a number, and its witness is a NON-empty population.
    assert (False, 1) in witness[87]

    lying = copy.deepcopy(recon_saturation)
    lying["recon_lag_days"]["undefined_witness"] = {
        87: ((True, 4),) * 3, 88: ((True, 4),) * 3}
    violations = pair.check_organ_query_grid_saturation(lying)
    assert any("is a BOUND only while" in v for v in violations), violations


def test_the_latency_floor_is_two_constants_the_census_pointed_at(
        recon_saturation):
    """HOUR #13's LEAD 1, ANSWERED. `SCENARIO_CONSTANT_CENSUS` censuses
    `PAYMENT_TERMS_DAYS` as `bounds_resolution: False` -- true of the invoice
    AGE band -- and discharges it with "it bounds the DETECTION-LATENCY
    dimension instead ... and is registered there". It was not registered
    there: this register named no constant at all, and the other half of the
    edge is not even in the census's subject (that keyset comes off
    `build_scenario`'s AST, and the grace window enters at `score_triad`).

    Now the edge is arithmetic, predicted from the constants alone and
    cross-checked against the sweep."""
    entry = pair.ORGAN_QUERY_GRID["recon_lag_days"]
    census = pair.SCENARIO_CONSTANT_CENSUS["PAYMENT_TERMS_DAYS"]
    assert census["bounds_resolution"] is False
    assert "PAYMENT_TERMS_DAYS" in entry["edge_constants"]
    assert "DEFAULT_RECONCILIATION_GRACE_DAYS" in entry["edge_constants"]
    assert pair.predict_recon_floor_from_constants() == \
        recon_saturation["recon_lag_days"]["saturates_below"] == -19
    # PREDICTED FROM CONSTANTS, NEVER FROM THE BOOK OR THE SWEEP.
    names = pair._names_in(pair.predict_recon_floor_from_constants)
    assert "ORGAN_QUERY_GRID" not in names and "records" not in names
    # ... and it MOVES with each of them, in the direction the identity says.
    assert pair.predict_recon_floor_from_constants(terms_days=20) == -25
    assert pair.predict_recon_floor_from_constants(grace_days=0) == -14


def test_the_registers_own_grid_could_confirm_neither_edge(monkeypatch):
    """THE SOURCE MUTATION (R15 the other way): put the grid back the way it
    was -- derived from the register's own declarations -- and the finding
    disappears. This is the whole of atom D31 in one assertion, and it is the
    third time the same assertion has had to be written."""
    monkeypatch.setattr(pair, "book_recon_drift_grid", lambda *a, **k: (0,))
    sparse = pair.measure_organ_query_grid_saturation(n_customers=_RES_N)
    assert set(sparse["recon_lag_days"]["drifts"]) == {
        -30, -20, -15, -5, -1, 0, 1, 8}, (
        "this is the grid the register chose for itself: the four declaration "
        "fields it had before D31, and nothing else. `collapsed_runs` and "
        "`undefined_drifts` are deliberately NOT unioned into the sweep -- "
        "they are what it is FOR, and adopting them would put the answer back "
        "into the question")
    # NEITHER EDGE IS REACHABLE THERE, and the undefined region is invisible.
    assert sparse["flagged_via_reconciliation"]["saturates_above"] is None
    assert sparse["recon_lag_days"]["undefined_readings"] == ()
    assert len(sparse["flagged_via_reconciliation"]["collapsed_runs"]) < 16
    violations = pair.check_organ_query_grid_saturation(sparse)
    unconfirmable = [v for v in violations if "reads them apart" in v]
    assert len(unconfirmable) >= 14, (
        "on its own grid the register can confirm almost none of what it now "
        "declares -- which is what makes the provenance the fix")
    assert any("declares NO reading at drift +87d and the sweep never scored "
               "it" in v for v in violations)


def test_the_recon_saturation_caveat_travels_with_both_numbers():
    """A limit only an Expert-Hour register carries is one no reader of the
    number ever sees (the D25 rule). Stamped on the note AND the components of
    both dimensions this knob reads, and INTERPOLATED from the register on
    every call so a reshape that moved the edges cannot leave the sentence
    standing."""
    result = pair.measure(n_customers=120, seed=7)
    det = result["detection"]
    assert det.components["recon_saturation_caveat"] in det.note
    assert "atom D31" in det.components["recon_saturation_caveat"]
    # THE BAND IS THIS BOOK'S, NOT THE REGISTER'S LITERAL (atom D28). This
    # assertion read `== (-6, 82)` -- the register's n=300 pair -- until
    # 2026-08-18, and it passed on a 120-account book whose own upper edge is
    # +70. That is the shipped defect in one line: the assertion could not tell
    # the two populations apart because neither could the component.
    band = det.components["recon_saturation_band_days"]
    assert band[0] == -pair.DEFAULT_RECONCILIATION_GRACE_DAYS - 1
    assert band == (-6, 70), (
        "the 120-account book's own band, and NOT the register's (-6, 82)")
    scope = det.components["recon_saturation_band_measured_on"]
    assert scope["source"] == "predicted_from_this_book"
    assert scope["n_accounts"] == 120 and scope["n_scored"] > 0
    assert "+70d" in det.components["recon_saturation_caveat"], (
        "the prose half must state the same band the machine-readable half "
        "does -- two numbers claiming one label is what this was")
    lat = result["detection_latency"]
    assert lat.components["organ_query_floor_drift_days"] == -19
    assert set(lat.components["organ_query_floor_constants"]) == {
        "PAYMENT_TERMS_DAYS", "DEFAULT_RECONCILIATION_GRACE_DAYS"}
    assert "-19d and no further" in lat.components[
        "organ_query_saturation_caveat"]


# ---------------------------------------------------------------------------
# THE POPULATION-SIDE PREDICTOR AND THE DRAW-SIZE AXIS -- atom D28, 2026-08-18,
# closing WORKER_FINDING_THE_SATURATION_EDGE_IS_A_PROPERTY_OF_THE_DRAW_SIZE.
#
# The register declared `saturates_above: 82`, `score_triad` stamped it onto
# EVERY book it ever scored, and `measure_organ_query_grid_saturation` -- the
# control over that declaration -- defaults to `n_customers=300`, the draw size
# the declaration was authored at. Not a tautology and not fail-open: the
# control genuinely measures, and would genuinely fire, AT n=300. Its subject
# was chosen by a harness convenience, so the only population it could fail on
# was the one that produced the declaration.
#
# The predictor is what makes the other populations askable: arithmetic over
# one book instead of 109 re-scorings, so 25 books cost ~3s against ~100s for
# one. Its own honesty rests on the first test below -- an independent
# implementation is worth nothing until it has been put against the shipped one
# point for point.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def band_population_axis():
    """The band on 25 books: 5 draw sizes x 5 seeds, predictor-only."""
    return pair.measure_recon_band_population_axis()


def test_the_predictor_reproduces_the_published_curve_with_no_scorer_call():
    """R15 INDEPENDENCE, and the control the whole atom rests on. The predictor
    reads the LEDGER's own cover dates and the consumer's own snapshot; it does
    not call `score_triad` and is not a copy of `expected_collection_misses`.
    So it is scored against the shipped scorer at every point of the book's own
    grid -- `gap` to float equality and both components to the published 6 d.p.

    A predictor agreeing on the interior and not at the edges would be the
    worst possible outcome here (the edges are the published claim), which is
    why the grid spans both tails rather than sampling the middle."""
    n, seed = 60, 7
    records, consumer, _lb, as_of = pair.build_scenario(n, seed=seed)
    thresholds = pair.predict_recon_exit_thresholds(records, consumer, as_of)
    dd_held = pair.observed_dd_flagged_set(records, consumer, as_of)
    truth = {(r.customer_id, r.period_index)
             for r in records if r.result == "failed"}
    never = pair.never_flaggable_band(records)
    scored = truth | never
    assert truth and never, "a book with an empty direction proves nothing"

    disagreements = []
    for k in range(-20, 89):
        det = pair.score_triad(
            records, consumer, as_of, organ_reconciliation_drift_days=k,
        )["detection"]
        flagged = {c for c in scored if c in dd_held or k < thresholds[c]}
        missed = len(truth - flagged) / len(truth)
        false_flag = len(flagged & never) / len(never)
        predicted_gap = (missed + false_flag) / 2
        if (predicted_gap != det.gap
                or round(missed, 6) != round(
                    det.components["missed_failure_rate"], 6)
                or round(false_flag, 6) != round(
                    det.components["false_flag_rate"], 6)):
            disagreements.append((k, predicted_gap, det.gap))
    assert disagreements == [], (
        "the predictor and the shipped scorer part company at these drifts -- "
        "every declaration the predictor is now trusted for is void until they "
        "agree again")


def test_the_standalone_dd_read_is_the_scorers_own_dd_set():
    """`observed_dd_flagged_set` is a SECOND read of the surface `score_triad`
    reads, and two reads of one surface drifting apart is the sibling-half
    class this module has already been bitten by twice. It is not left to
    inspection."""
    records, consumer, _lb, as_of = pair.build_scenario(120, seed=11)
    standalone = pair.observed_dd_flagged_set(records, consumer, as_of)
    scorer = pair.score_triad(records, consumer, as_of)[
        "sets"]["flagged_via_dd_channel"]
    assert standalone == scorer and standalone, (
        "an empty set would make this assertion vacuous, so it must also be "
        "non-empty")


def test_the_published_band_is_the_scored_books_and_not_a_literal(
        band_population_axis):
    """THE SHIPPED DEFECT, both halves.

    (a) Two books of different draw size must publish DIFFERENT upper edges
        through the shipped scorer. Until 2026-08-18 they published the
        register's `82` whatever they were.
    (b) The register's literal must no longer be reachable from the stamp at
        all -- a per-run derivation that happened to coincide on the register's
        own book would leave the class alive everywhere else."""
    small = pair.measure(n_customers=120, seed=7)["detection"]
    large = pair.measure(n_customers=600, seed=7)["detection"]
    small_band = small.components["recon_saturation_band_days"]
    large_band = large.components["recon_saturation_band_days"]
    assert small_band[1] != large_band[1], (
        "the same book shape at two draw sizes published one upper edge -- "
        "which is the defect, not the fix")
    declared = pair.ORGAN_QUERY_GRID["flagged_via_reconciliation"][
        "saturates_above"]
    assert {small_band[1], large_band[1]} != {declared}
    assert "recon_saturation_band_days" not in pair._names_in(
        pair.organ_query_grid_saturation_caveat)
    # And the axis says the same thing over 25 books rather than 2.
    assert band_population_axis["upper_edge_range"][0] < declared


def test_the_lower_edge_is_the_grace_closed_form_on_every_book(
        band_population_axis):
    """THE NULL CONTROL the finding owed, and it must stay GREEN or the
    measurement above is reading draw noise rather than a scope error: the
    LOWER edge is `-(grace + 1)`, attained by any invoice paid on its due date,
    and it does not move with the draw size on any of the 25 books."""
    closed_form = -(pair.DEFAULT_RECONCILIATION_GRACE_DAYS + 1)
    assert band_population_axis["lower_edges"] == (closed_form,), (
        "if the lower edge moved with the draw size too, the upper edge's "
        "movement would be evidence of nothing")
    assert all(b["below_closed_form"] == closed_form
               for b in band_population_axis["by_book"].values())
    assert pair.check_recon_band_population_axis(band_population_axis) == []


@pytest.mark.parametrize("mutate,expected", [
    (lambda e: e["draw_size_axis"].__setitem__("lower_edge_invariant", -12),
     "not a bound"),
    (lambda e: e["draw_size_axis"].__setitem__("upper_edge_range", (70, 80)),
     "declares its upper edge inside [70, 80]"),
    (lambda e: e.__setitem__("saturates_above_scope", {}),
     "declares `saturates_above` and no scope"),
    (lambda e: e.__setitem__("saturates_above_scope",
                             {"n_customers": 999, "seeds": (7,)}),
     "which this axis never visits"),
])
def test_the_draw_size_control_fires_on_its_own_named_defects(
        band_population_axis, mutate, expected):
    """R15: a control counts as evidence only once a mutation proves it fires.
    The fourth case is the SHIPPED defect itself -- an upper edge declared with
    no scope."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    mutate(register["flagged_via_reconciliation"])
    violations = pair.check_recon_band_population_axis(
        band_population_axis, register=register)
    assert any(expected in v for v in violations), violations


def test_pinning_the_population_hides_the_draw_size_defect():
    """THE MUTATION THE FINDING SPECIFIED, and the one that names the class:
    pin the sweep to a single `n_customers` -- exactly what
    `measure_organ_query_grid_saturation` does by default -- and the control
    goes GREEN with the defect untouched.

    That is why this is filed as a CONTROL finding and not only a number
    finding: nothing about the register or the book changed between these two
    calls, only which populations the control was allowed to look at."""
    pinned = pair.measure_recon_band_population_axis(n_customers=(300,))
    assert set(pinned["upper_spread_by_seed"].values()) == {0}, (
        "at one draw size there is no spread to see -- the harness default "
        "chose the subject")
    violations = pair.check_recon_band_population_axis(pinned)
    assert any("no seed's edge moved" in v for v in violations), (
        "and the control must SAY it was asked at one draw size rather than "
        "passing quietly -- a pinned axis is an unasked question, not a green "
        "one")


def test_the_predictor_never_calls_the_scorer():
    """The 250x is only worth having if it is real: a predictor that reached
    `score_triad` would be the sweep with extra steps, and the population axis
    would cost ~40 minutes instead of 3 seconds."""
    for fn in (pair.predict_recon_exit_thresholds,
               pair.predict_recon_saturation_band,
               pair.recon_cover_dates,
               pair.measure_recon_band_population_axis,
               pair.measure_recon_collapsed_runs_stress_axis,
               pair.collapsed_runs_from_thresholds):
        assert "score_triad" not in pair._names_in(fn), fn.__name__


# ---------------------------------------------------------------------------
# THE INTERIOR AND THE STRESS-MIX AXIS -- atom D28, 2026-08-18, closing
# WORKER_FINDING_THE_DECLARED_QUANTISATION_IS_FALSE_ON_THE_MODULES_OWN_LIVE_BOOK
#
# The two EDGES of `ORGAN_QUERY_GRID["flagged_via_reconciliation"]` got five
# things that morning: a scope, a population axis, a sweep, a control that puts
# the declaration on trial, and a per-run derivation. `collapsed_runs` sat in
# the same dict literal and got none of them -- while it, not the edges, is
# what the stamped sentence sends the reader to ("not readable as days of
# company error outside the declared runs").
#
# Same class as the edges, one field over, and the axis it is false along is
# not the one the draw-size sweep walks: `collapsed_runs` is INVARIANT in
# `n_customers` and false in the STRESS MIX. A book pinning every customer to
# one tier has a hole in `days_late`, and `k*` on a negative is
# `days_late - grace`, so a hole in `days_late` is a hole in the resolution.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def stress_axis():
    """The interior on 12 books: 4 stress tiers x 3 seeds, predictor-only."""
    return pair.measure_recon_collapsed_runs_stress_axis()


def _score_book(n, seed, stress=None):
    """Score one book through the SHIPPED scorer, optionally pinning the stress
    tier. `measure` is not used because it is the entry point for the SCORED
    population and must not grow a counterfactual knob -- the same reason
    `force_payment_method` and `cycle_spread_days` live on `build_scenario`."""
    records, consumer, _ledger, as_of = pair.build_scenario(
        n, seed=seed, force_income_stress=stress)
    return pair.score_triad(records, consumer, as_of)


def test_the_predicted_runs_are_the_shipped_sweeps_runs():
    """R15 INDEPENDENCE, and the control this whole half rests on: the runs are
    claimed to be the GAPS in the scored movable `k*` multiset, so they are
    scored against the SHIPPED scorer over the book's own full grid, drift by
    drift, with the grouping done exactly as `_measure_collapse_runs` does it.

    An independent implementation is worth nothing until it has been put
    against the shipped one point for point -- and this is the assertion that
    would fail if the derivation were merely plausible."""
    records, consumer, _ledger, as_of = pair.build_scenario(120, seed=7)
    grid = pair.book_recon_drift_grid(records, as_of)

    groups = {}
    for k in grid:
        scored = pair.score_triad(records, consumer, as_of,
                                  organ_reconciliation_drift_days=k)
        groups.setdefault(
            pair._reading_key(scored["detection"].gap), []).append(k)
    swept = tuple(sorted(tuple(v) for v in groups.values() if len(v) > 1))

    predicted = pair.predict_recon_saturation_band(
        records, consumer, as_of)["collapsed_runs"]
    assert predicted == swept, (
        "the predictor's runs and the shipped scorer's runs must be the SAME "
        "object -- anything else and the published component is a second "
        "implementation quietly disagreeing with the number beside it")
    assert len(swept) > 1, "a book with one run cannot witness this"


def test_the_published_runs_are_this_books_and_not_the_registers_literal():
    """THE SHIPPED DEFECT, both halves -- the same pair the band's own test
    makes, one field over.

    (a) Two books whose stress mix differs must publish DIFFERENT runs through
        the shipped scorer. Until this tick every book published the register's
        sixteen, whatever it was.
    (b) The register's literal must not be reachable from the stamp at all: a
        per-run derivation that happened to coincide on the register's own book
        would leave the class alive everywhere else."""
    mixed = _score_book(300, 7)["detection"]
    pinned = _score_book(300, 7, stress="high")["detection"]
    mixed_runs = mixed.components["recon_collapsed_runs"]
    pinned_runs = pinned.components["recon_collapsed_runs"]
    assert mixed_runs != pinned_runs, (
        "the same book at two stress mixes published one run list -- which is "
        "the defect, not the fix")
    declared = pair.ORGAN_QUERY_GRID["flagged_via_reconciliation"][
        "collapsed_runs"]
    assert pinned_runs != declared and mixed_runs != declared
    for det in (mixed, pinned):
        assert det.components["recon_collapsed_runs_measured_on"][
            "source"] == "predicted_from_this_book"
    # AND THE READER IS SENT TO THE STAMPED LIST, not to the declaration.
    assert "outside the runs stamped beside it" in mixed.components[
        "recon_saturation_caveat"]
    assert "outside the declared runs" in (
        pair.organ_query_grid_saturation_caveat())


def test_the_run_at_the_origin_is_the_one_a_reader_is_standing_in():
    """The published component must name the run the BASELINE company sits in.
    That is the whole reader-facing content of the claim: someone moving this
    headline by a day needs to know whether a day is visible AT ALL from where
    they are standing, and on an all-high book it is not -- the register says
    the run at the origin is 2 days wide and this module builds books where it
    is 7 and 14."""
    det = _score_book(300, 7)["detection"]
    meta = det.components["recon_collapsed_runs_measured_on"]
    assert meta["source"] == "predicted_from_this_book"
    assert meta["run_at_origin"] == (0, 1)
    assert meta["n_collapsed_runs"] == len(
        det.components["recon_collapsed_runs"])
    pinned = _score_book(300, 7, stress="high")["detection"]
    pinned_origin = pinned.components[
        "recon_collapsed_runs_measured_on"]["run_at_origin"]
    assert pinned_origin is not None and len(pinned_origin) > 2, (
        "the all-high book's baseline sits in a run WIDER than the declared "
        "pair -- the finding's own headline, asserted on the shipped stamp")


def test_the_stress_axis_null_control_reproduces_the_declaration(stress_axis):
    """THE NULL CONTROL, and it must stay GREEN or everything above is reading
    draw noise rather than a scope error: on `build_scenario`'s own shipped mix
    -- the population the declaration was authored on -- the register's runs
    must reproduce EXACTLY inside the window, in BOTH directions, and the
    baseline company must sit in the declared `(0, 1)`.

    What moved in the three pinned tiers is the SAMPLE, not the law."""
    null_tier = stress_axis["null_control_tier"]
    row = stress_axis["by_tier"][null_tier]
    assert row["split_boundaries"] == ()
    assert row["joined_boundaries"] == ()
    assert row["reproduces_declaration_in_window"] is True
    assert row["run_at_origin"] == (0, 1)
    assert pair.check_recon_collapsed_runs_stress_axis(stress_axis) == []


def test_every_pinned_stress_tier_falsifies_the_declaration(stress_axis):
    """AND THE AXIS MUST ACTUALLY BITE. A scope nobody can fail on is a label,
    so the claim `collapsed_runs` is mix-dependent has to be witnessed -- and
    it is, in both directions and on all three pinned tiers:

      * `moderate` SPLITS, reading 6 of the 7 declared runs apart and leaving
        the baseline company in no run at all;
      * `low` and `high` JOIN, collapsing boundaries the register says resolve
        two companies -- which is the direction the finding's headline is in
        and the one a split-only predicate would have passed on.
    """
    assert set(stress_axis["disagreeing_tiers"]) == {"low", "moderate", "high"}
    moderate = stress_axis["by_tier"]["moderate"]
    assert moderate["n_declared_read_apart"] == 6
    assert moderate["run_at_origin"] is None
    for tier in ("low", "high"):
        assert stress_axis["by_tier"][tier]["joined_boundaries"], (
            f"`{tier}` must witness the JOIN direction -- a run wider than the "
            "register declares is as much a falsification as one split apart")
    assert stress_axis["by_tier"]["low"]["split_boundaries"] == (), (
        "and it must witness it CLEANLY: `low` splits nothing, so a split-only "
        "predicate reads it as agreement")


@pytest.mark.parametrize("mutate,expected", [
    (lambda e: e.pop("collapsed_runs_scope"),
     "declares `collapsed_runs` and no scope"),
    (lambda e: e["stress_mix_axis"].__setitem__(
        "tiers_disagreeing_with_the_declaration",
        ("low", "moderate", "high", "mix")),
     "outliving its debt"),
    (lambda e: e["stress_mix_axis"].__setitem__(
        "tiers_disagreeing_with_the_declaration", ("moderate",)),
     "undeclared disagreement is the blindness"),
    (lambda e: e["stress_mix_axis"].__setitem__(
        "run_at_origin_on_mix", (0, 1, 2)),
     "STANDING IN"),
    (lambda e: e["collapsed_runs_scope"].__setitem__("worst_tier", "high"),
     "the wrong book"),
    (lambda e: e["collapsed_runs_scope"].__setitem__(
        "read_apart_on_worst_tier", 2),
     "must be the measured one"),
    (lambda e: e["collapsed_runs_scope"].__setitem__("declared_in_window", 99),
     "a count nobody re-derives"),
])
def test_the_stress_axis_control_fires_on_its_own_named_defects(
        stress_axis, mutate, expected):
    """R15: a control counts as evidence only once a mutation proves it fires.
    The first case is the SHIPPED defect itself -- a run list declared with no
    scope."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    mutate(register["flagged_via_reconciliation"])
    violations = pair.check_recon_collapsed_runs_stress_axis(
        stress_axis, register=register)
    assert any(expected in v for v in violations), violations


@pytest.mark.parametrize("mutate,expected", [
    (lambda m: m["by_tier"]["mix"].update(
        reproduces_declaration_in_window=False, n_declared_read_apart=3,
        n_joined_boundaries=2),
     "THE NULL CONTROL IS RED"),
    (lambda m: ([m["by_tier"][t].__setitem__(
        "reproduces_declaration_in_window", True) for t in m["by_tier"]],
        m.__setitem__("disagreeing_tiers", ())),
     "is a label, not a claim"),
])
def test_the_stress_axis_control_fires_on_a_bad_measurement(
        stress_axis, mutate, expected):
    """The other half of R15 on this control: it must fire on what the SWEEP
    returns, not only on what the register declares. A red null control and an
    axis where nothing disagrees are both silent failures otherwise."""
    measured = copy.deepcopy(stress_axis)
    mutate(measured)
    violations = pair.check_recon_collapsed_runs_stress_axis(measured)
    assert any(expected in v for v in violations), violations


def test_pinning_the_axis_to_one_stress_tier_hides_the_defect():
    """THE MUTATION THAT NAMES THE CLASS, and the exact shape its sibling has:
    ask the axis at ONE stress tier -- the shipped mix, which is what every
    other sweep in this module does by default -- and nothing disagrees, so
    the control goes green with the defect untouched.

    Nothing about the register or the book changed between these two calls,
    only which populations the control was allowed to look at."""
    pinned = pair.measure_recon_collapsed_runs_stress_axis(tiers=("mix",))
    assert pinned["disagreeing_tiers"] == ()
    violations = pair.check_recon_collapsed_runs_stress_axis(pinned)
    assert any("is a label, not a claim" in v for v in violations), (
        "a pinned axis is an unasked question, not a green one")


def test_the_collapsed_runs_derivation_is_the_gaps_in_the_threshold_multiset():
    """The derivation stated as arithmetic, on a hand-built multiset, so the
    rule is legible without a 300-account book: a boundary `k` splits a run iff
    some scored movable case exits at `k`."""
    runs = pair.collapsed_runs_from_thresholds(range(0, 10), {3, 4, 8})
    assert runs == ((0, 1, 2), (4, 5, 6, 7), (8, 9))
    assert pair.collapsed_runs_from_thresholds(range(0, 4), set()) == (
        (0, 1, 2, 3),), "no exits at all is ONE run, not four"
    assert pair.collapsed_runs_from_thresholds(
        range(0, 4), {1, 2, 3}) == (), "an exit at every boundary is NO runs"
    assert pair.collapsed_runs_from_thresholds((), {1}) == ()


# ---------------------------------------------------------------------------
# PUBLISHED_FIGURE_CAVEAT_CONTRACT -- atom D32, H27 Expert Hour #14.
#
# D31's route proved every counterfactual knob is SWEPT on a book-derived grid
# and reaches the one saturation rule. Nobody had asked whether the resolution
# those sweeps measure ever reaches the READER of the number. It did not, twice
# over, in the same dimension: the recon caveat stamped on `detection_latency`
# reported the step of `mean_lag_days_without_dd_channel` (the DD-deleted
# SUB-READING the register names in `headline_key`, 1.0/day) as what "is
# published", while the published `mean_lag_days` moves about a third of that;
# and the TERMS knob, declared on-path since D28, was stamped on nothing.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def caveat_coverage():
    """One sweep of all three knobs across all five published dimensions, on
    the seeds every other resolution control in this module uses."""
    return pair.measure_published_figure_caveat_coverage(n_customers=_RES_N)


@pytest.fixture(scope="module")
def resolution_floors():
    """The per-figure resolution floors (atom D33), measured through each
    dimension's OWN shipped scorer on a book-derived grid -- the independent
    side of the caveat-number check."""
    return pair.measure_published_resolution_floor(n_customers=_RES_N)


def test_the_caveat_coverage_register_is_measured_not_asserted(
        caveat_coverage, resolution_floors):
    """Green means every cell's declaration is the reach the code HAS -- not
    that every dimension is covered. The keyset is derived both ways."""
    assert pair.check_published_figure_caveat_coverage(
        caveat_coverage, floors=resolution_floors) == []
    assert set(caveat_coverage) == set(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    # DERIVED from what `score_triad` publishes, not from the register -- the
    # keying that let this class escape six registers before it.
    records, consumer, _b, as_of = pair.build_scenario(60, seed=7)
    assert set(caveat_coverage) == set(
        pair.published_dimensions(pair.score_triad(records, consumer, as_of)))
    for dim, row in pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT.items():
        assert set(row) == set(pair.counterfactual_knobs()), dim


def test_seven_of_fifteen_cells_move_and_each_carries_a_caveat(caveat_coverage):
    """THE MEASUREMENT (atom D32). Three knobs x five published dimensions;
    seven cells move. The nine inert ones are MEASURED inert -- an unmeasured
    cell reads exactly like an inert one, which is the whole finding."""
    moving = {(d, k) for d in caveat_coverage
              for k in pair.counterfactual_knobs()
              if caveat_coverage[d][k]["moves"]}
    assert moving == {
        ("detection", "organ_terms_drift_days"),
        ("detection", "organ_reconciliation_drift_days"),
        ("detection_latency", "organ_terms_drift_days"),
        ("detection_latency", "organ_reconciliation_drift_days"),
        ("ageing", "organ_terms_drift_days"),
        ("belief", "organ_failure_window_drift_days"),
        ("belief_population_mix", "organ_failure_window_drift_days"),
    }
    for dim, knob in moving:
        assert pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT[dim][knob][
            "caveat_component"]


def test_the_published_headline_moves_a_third_of_the_sub_readings_step(
        caveat_coverage):
    """THE FINDING, measured not asserted. `ORGAN_QUERY_GRID` declares the
    recon reading resolves the company day for day, and that is TRUE of
    `mean_lag_days_without_dd_channel`, the reading it names. It is not true of
    the published figure, and the caveat said it was."""
    row = caveat_coverage["detection_latency"]["organ_reconciliation_drift_days"]
    declared = pair.ORGAN_QUERY_GRID["recon_lag_days"][
        "reported_days_for_a_one_day_drift"]
    assert declared == 1.0
    assert pair.ORGAN_QUERY_GRID["recon_lag_days"]["headline_key"] == \
        "mean_lag_days_without_dd_channel"
    # The published headline is a DIFFERENT number, on every seed, and always
    # far below the sub-reading's step.
    for seed, step in row["step_days"].items():
        assert 0.2 < step < 0.4, (seed, step)
        assert declared - step > 0.5

    # ...and the SUB-READING really does move 1.0/day, which is what makes the
    # register honest about itself and the caveat wrong about the headline.
    records, consumer, _b, as_of = pair.build_scenario(_RES_N, seed=7)
    base = pair.score_triad(records, consumer, as_of)["detection_latency"]
    up = pair.score_triad(records, consumer, as_of,
                          organ_reconciliation_drift_days=1)["detection_latency"]
    assert (up.components["mean_lag_days_without_dd_channel"]
            - base.components["mean_lag_days_without_dd_channel"]) == 1.0


def test_the_published_step_is_predicted_from_the_book_not_the_sweep(
        caveat_coverage):
    """The number stamped beside the sentence reads no sweep, no seed and no
    re-scoring -- it is this book's own coverage witnesses (the D25/D30
    population-side-predictor pattern) -- and it AGREES with the sweep."""
    names = pair._names_in(pair.predict_published_latency_step_days)
    for forbidden in ("score_triad", "build_scenario", "ORGAN_QUERY_GRID",
                      "PUBLISHED_FIGURE_CAVEAT_CONTRACT"):
        assert forbidden not in names, forbidden
    row = caveat_coverage["detection_latency"]["organ_reconciliation_drift_days"]
    for seed, step in row["step_days"].items():
        records, consumer, _b, as_of = pair.build_scenario(_RES_N, seed=seed)
        c = pair.score_triad(records, consumer, as_of)[
            "detection_latency"].components
        assert abs(c["published_headline_step_days"] - step) < pair._ROUNDING_SLACK
    # An empty latency population has NO step -- a 0.0 there would read as
    # "the headline is inert", the strongest claim handed out for free.
    assert pair.predict_published_latency_step_days(0, 0) is None


def test_the_caveat_states_the_published_figures_own_step(caveat_coverage):
    """R11-shaped: the sentence a consumer RENDERS must carry this figure's
    number, not the sub-reading's. Both are present and each says which it
    is."""
    records, consumer, _b, as_of = pair.build_scenario(_RES_N, seed=7)
    c = pair.score_triad(records, consumer, as_of)[
        "detection_latency"].components
    caveat = c["organ_query_grid_caveat"]
    assert "mean_lag_days_without_dd_channel" in caveat
    assert "NOT OF THE FIGURE THIS CAVEAT IS STAMPED ON" in caveat
    assert f"{c['published_headline_step_days']:.6f}" in caveat
    # ...and the TERMS knob, which moves this figure identically and reached
    # the reader nowhere before this atom.
    terms = c["terms_resolution_caveat"]
    assert "organ_terms_drift_days" in terms
    assert "does not attribute" in terms


def test_the_two_knobs_are_indistinguishable_in_the_latency_headline():
    """WHY THE MISSING TERMS CAVEAT MATTERS. A supplier holding terms k days
    long and one whose detector fires k days late publish a BIT-IDENTICAL
    latency figure, so a reader given only the recon caveat attributes the
    whole reading to a detector fault it may have no part in."""
    records, consumer, _b, as_of = pair.build_scenario(_RES_N, seed=7)
    for k in (-3, -1, 1, 3, 5):
        recon = pair.score_triad(records, consumer, as_of,
                                 organ_reconciliation_drift_days=k)
        terms = pair.score_triad(records, consumer, as_of,
                                 organ_terms_drift_days=k)
        assert recon["detection_latency"].gap == terms["detection_latency"].gap, k


# --- R15: the control fires on each defect it names ------------------------


def test_the_pre_hour_step_fires_the_control(caveat_coverage):
    """THE DEFECT ITSELF, put back: publish the SUB-READING's 1.0 as this
    figure's step. This is the state every ledger note and Proof-door reading
    carried until 2026-08-11, and it must not pass."""
    rendered = copy.deepcopy(caveat_coverage["detection_latency"]["_rendered"])
    for seed in rendered:
        rendered[seed]["published_headline_step_days"] = 1.0
    view = {d: dict(caveat_coverage[d].get("_rendered", {}))
            for d in caveat_coverage}
    view["detection_latency"] = rendered
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, rendered=view)
    assert any("publishes step 1.0 while the PUBLISHED headline" in v
               for v in violations), violations


def test_a_moving_cell_with_no_caveat_fires_the_control(caveat_coverage):
    """THE OTHER PRE-HOUR STATE: `detection_latency` moved under the terms
    knob, was declared on-path in `DIMENSION_DRIFT_RESOLUTION`, and carried no
    terms caveat at all."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    del reg["detection_latency"]["organ_terms_drift_days"]["caveat_component"]
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, register=reg)
    assert any("names no caveat component" in v for v in violations), violations


def test_a_caveat_the_consumer_never_renders_fires_the_control(caveat_coverage):
    """Naming a component is not stamping one -- Hour #11's `a lead is not a
    control`, in the shape this register could itself have taken. The subject
    is what `score_triad` publishes, never the register's own word."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    reg["detection_latency"]["organ_terms_drift_days"]["caveat_component"] = \
        "a_caveat_nobody_publishes"
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, register=reg)
    assert any("publishes no such key" in v for v in violations), violations


def test_declaring_a_moving_cell_inert_fires_the_control(caveat_coverage):
    """A cell declared inert is a CLAIM, measured every run. This is the
    fail-open the nine inert cells would otherwise be."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    reg["ageing"]["organ_terms_drift_days"] = {"moves": False}
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, register=reg)
    assert any("declared moves=False but MEASURED moves=True" in v
               for v in violations), violations


def test_declaring_an_inert_cell_moving_fires_the_control(caveat_coverage):
    """...and the other direction, or the register could buy coverage by
    declaring everything moves."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    reg["ageing"]["organ_reconciliation_drift_days"] = {
        "moves": True, "caveat_component": "drift_resolution_caveat"}
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, register=reg)
    assert any("declared moves=True but MEASURED moves=False" in v
               for v in violations), violations


def test_an_undeclared_cell_raises_rather_than_passing(caveat_coverage):
    """THE FAIL-CLOSED (the D29/D31 rule, one layer up). A cell nobody declared
    is not an inert one -- it is an unasked one, and it reads identically to a
    clean cell, which is exactly how this class survived thirteen Hours."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    del reg["detection_latency"]["organ_terms_drift_days"]
    with pytest.raises(AssertionError, match="no caveat-coverage declaration"):
        pair.check_published_figure_caveat_coverage(caveat_coverage, register=reg)


def test_a_dimension_with_no_entry_raises(caveat_coverage):
    """Both keyset directions raise: a published dimension nothing asks about,
    and an entry for a dimension nobody publishes."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    del reg["ageing"]
    with pytest.raises(AssertionError, match="no PUBLISHED_FIGURE_CAVEAT"):
        pair.check_published_figure_caveat_coverage(caveat_coverage, register=reg)
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    reg["a_dimension_nobody_publishes"] = {
        k: {"moves": False} for k in pair.counterfactual_knobs()}
    with pytest.raises(AssertionError, match="nobody\\s+publishes"):
        pair.check_published_figure_caveat_coverage(caveat_coverage, register=reg)


def test_an_inert_probe_cannot_certify_its_column(caveat_coverage):
    """THE VACUITY GUARD on the probe itself. A knob that had silently stopped
    drifting the company would certify every `moves: False` cell in its column
    for free -- the fail-silent shape this instrument has now produced six
    times, most recently inside a control written to close the previous one."""
    probes = dict(pair.CAVEAT_COVERAGE_PROBES)
    # A memory drift of +1 is inside the saturated band D29/D30 measured, so
    # the knob is real and the PROBE is inert -- which is the situation the
    # guard exists for, not a broken parameter.
    probes["organ_failure_window_drift_days"] = (1,)
    measured = pair.measure_published_figure_caveat_coverage(
        n_customers=60, seeds=(7,), probes=probes)
    violations = pair.check_published_figure_caveat_coverage(measured)
    assert any("the probe moved NOTHING on any published dimension" in v
               for v in violations), violations


# ---------------------------------------------------------------------------
# ATOM D33 -- H27 EXPERT HOUR #15 (2026-08-11): THE CAVEAT'S NUMBER WAS THE
# BOOK'S, ON TWO FIGURES THAT DO NOT SHARE A RESOLUTION.
#
# Hour #14 built the caveat contract and left LEAD 2: its step check reached
# exactly one cell -- `detection_latency`/recon, the only day-linear one -- and
# the other six moving cells carry caveats whose numbers are BANDS and EDGES
# that nothing compares against the figure they ride on. Asked of the two belief
# cells: the number is not either figure's. `belief_resolution_caveat` published
# `measure_belief_window_resolution`'s book bound (headroom + 1) in the sentence
# "the smallest memory error IT can resolve at all", byte-identically on both
# belief dimensions. Measured through the organ: the bound is 310/309/309 on
# seeds 7/11/23 while `belief` resolves 310/310/309 and `belief_population_mix`
# resolves 310/314/312 -- so the sentence is five days out on one figure, and the
# register's own `own_why` had already NOTICED the sibling was blunter without
# anything turning that into the number the reader gets.
# ---------------------------------------------------------------------------


def test_the_two_belief_figures_do_not_share_a_resolution(resolution_floors):
    """THE FINDING, measured not asserted. One sentence, two figures, four days
    apart -- and the book's bound is neither."""
    bel = resolution_floors["belief"]
    mix = resolution_floors["belief_population_mix"]
    assert bel["floor_days"] == 310
    assert mix["floor_days"] == 314
    assert bel["floor_days"] != mix["floor_days"]
    # THE BOOK BOUND the caveat used to publish as each figure's own resolution.
    assert bel["book_bound_days"] == mix["book_bound_days"] == {
        7: 310, 11: 309, 23: 309}
    # Five days out on seed 11 for the mix figure, which is the whole finding:
    # the bound is a BOUND, and every figure here is at least as blind as it.
    assert mix["per_seed_floor_days"][11] - mix["book_bound_days"][11] == 5
    for row in (bel, mix):
        for seed, bound in row["book_bound_days"].items():
            assert row["per_seed_floor_days"][seed] >= bound, (seed, row)


def test_each_belief_figure_publishes_its_own_floor_and_the_sentence_says_it():
    """R11-shaped, on the artefact the consumer renders: the two caveats are no
    longer byte-identical, each states ITS figure's floor, and the book bound is
    labelled as a bound. Components too -- the ledger writer, the live wiring
    and the dashboard read `components` and never the prose (D22)."""
    records, consumer, _b, as_of = pair.build_scenario(_RES_N, seed=7)
    result = pair.score_triad(records, consumer, as_of)
    bel = result["belief"].components
    mix = result["belief_population_mix"].components
    assert bel["belief_resolution_caveat"] != mix["belief_resolution_caveat"]
    assert bel["measured_resolution_floor_days"] == 310
    assert mix["measured_resolution_floor_days"] == 314
    for comps, own, other in ((bel, 310, 314), (mix, 314, 310)):
        caveat = comps["belief_resolution_caveat"]
        assert f"{own}d of forgetting" in caveat
        assert f"{other}d" in caveat            # names the sibling's, as the sibling's
        assert "do NOT share a resolution" in caveat
        # ...and the book bound is stated as a bound on ANY figure here.
        assert "can move ANY figure here" in caveat
        assert comps["book_bound_floor_days"] == 310
    # The retired sentence -- the bound presented as the figure's own -- is gone
    # from both, and from the notes the callers may replace.
    for dim in ("belief", "belief_population_mix"):
        for text in (result[dim].note,
                     result[dim].components["belief_resolution_caveat"]):
            assert "smallest memory error it can resolve at all" not in text


def test_the_epsilon_is_the_readers_own_precision_not_a_tolerance():
    """INDEPENDENCE, and PER FIGURE (atom D34). The precision is a claim about
    somebody else's format string, so it is read back off the spec that renders
    THAT DIMENSION'S GAP -- and the five published figures do not share one."""
    measured = pair.measure_published_reading_precision(
        result=_precision_scoring())
    assert pair.check_published_reading_precision(
        measured, published=pair.published_dimensions(_precision_scoring())) == []
    # THE NUMBERS, MEASURED OFF THE SHIPPED RENDERERS. A global constant was
    # 10x too fine for the ageing figure and 100x too fine for the latency one.
    assert {d: row["decimals"] for d, row in measured.items()} == {
        "belief": (4,),
        "belief_population_mix": (4,),
        "detection": (4,),
        "ageing": (3,),
        "detection_latency": (2,),
    }
    assert pair.published_reading_epsilon("belief") == 5e-05
    # 5e-07 BETWEEN HOURS #17 AND #20, AND THAT READER DID NOT EXIST (atom D36).
    # Hour #17 moved this figure to 6dp on `ageing.ordinal_direction_caveat`,
    # which `_ageing_direction_note` really does render at `.6f` -- into a
    # component of the AGEING result, which nothing publishes: the ledger entry
    # carries `to_ledger_entry(result["detection"])`, the HEADLINE's components
    # and no others. Hour #20 walked the artefact a reader is handed and found
    # this figure rendered once, at 3dp, in the composed note. The AST row above
    # read 3dp throughout and was right throughout.
    assert pair.published_reading_epsilon("ageing") == 5e-04
    assert pair.published_reading_decimals("ageing") == 3
    assert "also_rendered_at" not in pair.PUBLISHED_GAP_CONSUMERS["ageing"]
    assert pair.published_reading_epsilon("detection_latency") == 5e-03
    # And it is HALF a step of that precision -- a difference of one full step
    # is readable, half of one is the boundary.
    assert pair.published_reading_epsilon(decimals=2) == 0.005


def test_a_caller_that_will_not_name_a_figure_is_refused_an_epsilon():
    """THE `_own_floor_clause` PRECEDENT (atom D34). A default epsilon is how
    the belief reader's 4dp came to certify a figure published at 2dp, so an
    unnamed caller gets a refusal rather than a house number."""
    with pytest.raises(AssertionError, match="without naming a figure"):
        pair.published_reading_epsilon()
    with pytest.raises(AssertionError, match="no entry in PUBLISHED_GAP_CONSUMERS"):
        pair.published_reading_decimals("no_such_dimension")


def test_the_gap_reaches_two_readers_through_a_component_not_a_gap_attribute():
    """WHY THE CARRIER IS DECLARED AND THEN MEASURED. Neither the ageing nor the
    latency renderer formats `.gap` at all -- both publish a COMPONENT -- so a
    walker looking only for `.gap` would find no render for two of the five
    figures and have to fall back on a default. That the component IS the gap is
    checked against a real scoring, never taken on the name."""
    measured = pair.measure_published_reading_precision(
        result=_precision_scoring())
    assert measured["ageing"]["carrier"] == (
        "component", "balanced_bucket_displacement")
    assert measured["detection_latency"]["carrier"] == (
        "component", "mean_lag_days")
    for dim in ("ageing", "detection_latency"):
        assert measured[dim]["carrier_is_the_gap"] is True
        assert measured[dim]["carrier_gap_delta"] < pair.published_reading_epsilon(dim)
    # AND THE MARGIN IS WIDE, not thin (atom D36). Hour #17 read this as a
    # claim holding "within a hair of its own epsilon" because it had just set
    # that epsilon to 5e-7 off a render nobody is handed. The ageing component
    # is `round(gap, 6)`, so its distance from the gap is bounded by 5e-7 --
    # three orders INSIDE the 5e-4 step this figure's reader is actually given.
    assert 1e-7 < measured["ageing"]["carrier_gap_delta"] <= 5e-07
    assert measured["ageing"]["carrier_gap_delta"] < (
        pair.published_reading_epsilon("ageing") / 100)
    # The latency figure arrives at its render through a LOCAL ALIAS
    # (`mean = c.get("mean_lag_days")`), which is the second way a render site
    # hides from a walker that only matches the carrier expression itself.
    assert measured["detection_latency"]["sites"] == {2: ("f-string",)}
    assert measured["ageing"]["sites"] == {3: ("helper",)}


def test_bit_equality_counts_a_difference_no_consumer_can_render(
        resolution_floors):
    """WHY THE PREDICATE IS ATOM D33's RESHAPE. The mix figure "moves" at
    -310..-313 on seed 11 by 1.4e-17, which is what put its declared saturation
    edge at -309 rather than -313 -- and every collapse run and saturation edge
    in this module is derived with the same `repr()` comparison."""
    mix = resolution_floors["belief_population_mix"]
    assert mix["bit_equality_floor_days"] == 312
    assert mix["floor_days"] == 314
    assert mix["bit_equality_per_seed_floor_days"][11] == 310
    assert mix["per_seed_floor_days"][11] == 314
    # The witness, taken live rather than quoted: the reading at -310 differs
    # from the baseline by less than one part in 1e16.
    records, consumer, _b, as_of = pair.build_scenario(_RES_N, seed=11)
    base = pair.score_triad(records, consumer, as_of)[
        "belief_population_mix"].gap
    drifted_records, drifted_consumer, _bk, drifted_as_of = pair.build_scenario(
        _RES_N, seed=11, organ_failure_window_drift_days=-310)
    drifted = pair.score_triad(drifted_records, drifted_consumer,
                              drifted_as_of)["belief_population_mix"].gap
    assert drifted != base
    assert abs(drifted - base) < pair.published_reading_epsilon(
        "belief_population_mix")
    # ...and the register says so, with the owning atom, on the dimension where
    # the two predicates disagree and NOT on the one where they agree.
    assert pair.DIMENSION_DRIFT_RESOLUTION["belief_population_mix"][
        "own_floor_predicate_atom"] == pair.BIT_EQUALITY_FLOOR_ATOM
    assert pair.DIMENSION_DRIFT_RESOLUTION["belief"][
        "own_floor_predicate_atom"] is None


def test_every_moving_cell_declares_whose_number_its_caveat_states(
        caveat_coverage):
    """THE CLASS (R10), and it is the coverage question one level in from D32's:
    a moving cell must say WHERE its caveat's number comes from, and a source
    that cannot be about this figure (a sub-reading, or the book) owes a number
    measured on the published figure."""
    for dim, row in pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT.items():
        for knob, entry in row.items():
            if not entry.get("moves"):
                continue
            kind, key = entry["number_source"]
            assert kind in pair._CAVEAT_NUMBER_SOURCE_KINDS, (dim, knob)
            if kind == "DIMENSION_DRIFT_RESOLUTION":
                assert key == dim, (dim, knob, key)
            elif kind == "ORGAN_QUERY_GRID":
                assert pair.ORGAN_QUERY_GRID[key]["feeds"] == dim
                if pair.ORGAN_QUERY_GRID[key]["headline_key"] is not None:
                    assert entry["published_step_component"], (dim, knob)
            else:
                assert entry["published_floor_component"], (dim, knob)
    # The two BOOK-sourced cells are the belief pair, and only they.
    book_sourced = {(d, k) for d, r in pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT.items()
                    for k, e in r.items()
                    if e.get("moves") and e["number_source"][0] == "BOOK"}
    assert book_sourced == {
        ("belief", "organ_failure_window_drift_days"),
        ("belief_population_mix", "organ_failure_window_drift_days")}


def test_the_floor_register_is_measured_not_asserted(resolution_floors):
    """Green means the declared floors are the ones the ORGAN publishes, and the
    grid they were found on is the BOOK's (the D29/D31 rule), not the
    register's own claims."""
    assert pair.check_published_resolution_floor(resolution_floors) == []
    for dim, row in resolution_floors.items():
        # One day INSIDE the book's own provable bound, out by the book's own
        # event-age span -- no drift in it was chosen by a declaration.
        assert row["grid"][0] == -(min(row["book_bound_days"].values()) - 1)
        assert row["readable_at_every_drift_beyond_floor"] is True
        assert row["undefined_readings"] == ()
        # PER FIGURE (atom D34): both belief figures are rendered at 4dp, so
        # this is the same number it always was -- read off each figure's own
        # consumer rather than off a constant that spoke for all five.
        assert row["epsilon"] == pair.published_reading_epsilon(dim)


# --- R15: the reader-precision control fires on each defect it names --------

_PRECISION_CONSUMER_FILES = (
    "background/gap_metric.py",
    "background/live_payment_triad.py",
    "tools/couple_w2_11_d5.py",
)


def _precision_scoring():
    """One real scoring, cached for the module: the component carriers are
    checked against the GAP numerically, which needs a scored population and not
    a fixture of hand-typed numbers (D11/D16 -- a hand-typed witness is a claim
    about a run that has already ended)."""
    if not hasattr(_precision_scoring, "_cached"):
        records, consumer, _b, as_of = pair.build_scenario(_RES_N, seed=7)
        _precision_scoring._cached = pair.score_triad(records, consumer, as_of)
    return _precision_scoring._cached


def _consumer_tree(tmp_path, edits=()):
    """A repo root holding ONLY the three consumer modules, so a mutation can be
    made to a renderer's source without touching the tree the suite runs in."""
    root = Path(__file__).resolve().parents[2]
    for rel in _PRECISION_CONSUMER_FILES:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text((root / rel).read_text())
    for rel, old, new in edits:
        path = tmp_path / rel
        text = path.read_text()
        assert old in text, (rel, old[:60])
        path.write_text(text.replace(old, new, 1))
    return tmp_path


def _precision_violations(tmp_path, edits=(), **kwargs):
    measured = pair.measure_published_reading_precision(
        repo_root=_consumer_tree(tmp_path, edits),
        result=kwargs.pop("result", _precision_scoring()), **kwargs)
    return pair.check_published_reading_precision(measured)


_BELIEF_GAP_RENDER = 'else format(result.gap, ".4f"))'
_AGEING_GAP_RENDER = '_num("balanced_bucket_displacement", ".3f")'
_LATENCY_GAP_RENDER = 'f"detection latency {mean:.2f} days mean "'


def test_a_gap_render_moving_off_its_declared_precision_fires(tmp_path):
    """THE MUTATION THE PRE-HOUR CONTROL COULD NOT FAIL ON (atom D34). Hour #15
    installed the re-read so that "a consumer that starts publishing 6dp fails
    the control"; it collected every `.Nf` in the function and asked only
    whether 4 was among them, and `format_belief_summary` renders three other
    rates at `.4f`. Moving the GAP's own render to 6dp left the set {2, 4, 6},
    which still contained 4."""
    got = _precision_violations(tmp_path, [(
        "background/gap_metric.py", _BELIEF_GAP_RENDER,
        'else format(result.gap, ".6f"))')])
    assert any("belief: declares [4]dp" in v and "[6] is a reader precision "
               "nobody declared" in v for v in got), got
    # And on BOTH figures the global constant was wrong about, by name.
    assert any("ageing: declares [3]dp" in v for v in _precision_violations(
        tmp_path, [("background/gap_metric.py", _AGEING_GAP_RENDER,
                    '_num("balanced_bucket_displacement", ".4f")')]))
    assert any("detection_latency: declares [2]dp" in v
               for v in _precision_violations(tmp_path, [(
                   "tools/couple_w2_11_d5.py", _LATENCY_GAP_RENDER,
                   'f"detection latency {mean:.4f} days mean "')]))


def test_one_figure_rendered_at_two_precisions_owes_both(tmp_path):
    """THE GUARD MOVED, NOT DROPPED (atom D35). D34's rule was "two precisions
    -> no epsilon, refuse to guess"; the reshape is that there is no guess to
    make -- a reader given 6dp somewhere can separate two companies at 1e-6
    whatever a second site rounds to -- so the epsilon is half a step of the
    FINEST and the guard moves onto the declared SET. An UNDECLARED second
    precision still fires, and by name."""
    got = _precision_violations(tmp_path, [(
        "background/gap_metric.py",
        '+ "; per-case disagreement " + _num("per_case_disagreement_rate", ".4f")',
        '+ "; again " + format(result.gap, ".2f")\n'
        '        + "; per-case disagreement " + _num("per_case_disagreement_rate", ".4f")')])
    assert any("belief: declares [4]dp" in v and "[2] is a reader precision "
               "nobody declared" in v for v in got), got
    # A SECOND site that IS declared passes -- and the epsilon follows the
    # finest of the two, never the one the register names first.
    finer = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    finer["belief"]["also_rendered_at"] = (6,)
    got = _precision_violations(tmp_path, [(
        "background/gap_metric.py", _BELIEF_GAP_RENDER,
        'else format(result.gap, ".6f"))')], register=finer)
    assert any("sets its epsilon from 4dp while the finest render its reader "
               "is given is 6dp" in v for v in got), got


def test_an_unreadable_consumer_is_a_failed_check_not_an_agreeing_one(tmp_path):
    """FAIL-SILENT, the third R15 killer. The pre-Hour re-read returned an empty
    tuple for a missing consumer file and its caller read that as agreement."""
    tree = _consumer_tree(tmp_path)
    (tree / "background/gap_metric.py").unlink()
    with pytest.raises(AssertionError, match="that file is not there"):
        pair.measure_published_reading_precision(
            repo_root=tree, result=_precision_scoring())


def test_a_renderer_that_is_not_there_raises(tmp_path):
    with pytest.raises(AssertionError, match="no such function exists"):
        _precision_violations(tmp_path, [(
            "background/gap_metric.py",
            "def format_ageing_summary(result: GapResult) -> str:",
            "def format_ageing_summary_RENAMED(result: GapResult) -> str:")])


def test_a_gap_with_no_fixed_point_render_raises(tmp_path):
    """An UNMEASURED precision reads exactly like a measured one -- the fail-open
    this instrument has now produced in seven registers."""
    with pytest.raises(AssertionError, match="no fixed-point render of its gap"):
        _precision_violations(tmp_path, [(
            "background/gap_metric.py", _AGEING_GAP_RENDER,
            'str(c.get("balanced_bucket_displacement"))')])


def test_the_keyset_is_derived_from_what_is_published_both_ways(tmp_path):
    """DERIVED, so both ways the register stops describing the code RAISE: a
    published figure with no entry would be handed the house default (this
    atom's defect), and an entry for a figure nobody publishes reads exactly
    like a live one."""
    published = pair.published_dimensions(_precision_scoring())
    tree = _consumer_tree(tmp_path)
    short = {k: v for k, v in pair.PUBLISHED_GAP_CONSUMERS.items() if k != "ageing"}
    with pytest.raises(AssertionError, match=r"published \['ageing'\]"):
        pair.check_published_reading_precision(
            pair.measure_published_reading_precision(
                repo_root=tree, register=short, result=_precision_scoring()),
            published=published)
    ghost = dict(pair.PUBLISHED_GAP_CONSUMERS)
    ghost["ghost"] = dict(pair.PUBLISHED_GAP_CONSUMERS["belief"])
    with pytest.raises(AssertionError, match=r"declares \['ghost'\]"):
        pair.check_published_reading_precision(
            pair.measure_published_reading_precision(
                repo_root=tree, register=ghost, result=_precision_scoring()),
            published=published)


def test_a_component_carrier_is_checked_against_the_gap_both_ways(tmp_path):
    """"`balanced_bucket_displacement` IS the ageing gap" is a claim about
    arithmetic in another module. A component that is NOT the gap puts this
    precision on a number nobody is shown -- and nothing checking it at all is
    an unavailable check, which is a failed one."""
    wrong = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    wrong["ageing"]["carrier"] = ("component", "mean_bucket_displacement")
    got = _precision_violations(tmp_path, register=wrong)
    assert any("differs from the gap by" in v for v in got), got
    unchecked = _precision_violations(tmp_path, result=None)
    assert any("NOTHING checked that component against the gap" in v
               for v in unchecked), unchecked


def test_the_declared_precisions_are_not_a_blanket_claim(tmp_path):
    """VACUITY. A register that gave every figure the same number would be the
    pre-Hour constant wearing a dict, and could not fail on the finding that
    produced it -- so the spread itself is pinned."""
    declared = {d: pair.published_reading_decimals(d)
                for d in pair.PUBLISHED_GAP_CONSUMERS}
    assert len(set(declared.values())) >= 3, declared
    # 2..6 BETWEEN HOURS #17 AND #20, on a 6dp site nobody is handed (D36).
    assert min(declared.values()) == 2 and max(declared.values()) == 4
    assert _precision_violations(tmp_path) == []


# --- R15: the component render-site sweep fires on each defect it names -----
#
# Atom D35, H27 Expert Hour #17. This half of the control reads NO source: it
# scores the book and looks for each figure's own value in the strings the
# consumer is handed, which is the independence D34's AST walk cannot have.


def _fake_result(values, strings):
    """A scoring-shaped object: {dim: obj with .gap and .components}."""
    return {dim: SimpleNamespace(gap=v, components=dict(strings.get(dim, {}),
                                                        **{"gap_echo": v}))
            for dim, v in values.items()}


_SITE_REGISTER = {"solo": {"module": "background/gap_metric.py",
                           "renderer": "format_ageing_summary",
                           "carrier": ("gap", None), "decimals": 4}}


def _fake_book(values, entry, n_customers=1):
    """A published book: the scoring, and the ARTEFACT it published.

    The two are separate arguments on purpose (atom D36). Until Hour #20 the
    sweep took only the scoring and derived its own population of "published"
    strings from it, which is precisely how a component of a result nobody
    publishes came to set a figure's epsilon.
    """
    return {"result": _fake_result(values, {}), "entry": entry,
            "spec": {"n_customers": n_customers, "months": 6}}


def test_the_shipped_render_sites_are_found_in_the_published_artefact():
    """THE DEFECT ITSELF (atom D36). Hour #17 moved the ageing figure's declared
    precision 3dp -> 6dp on `ageing.ordinal_direction_caveat`, a component of
    the AGEING result -- and `measure_and_write` publishes
    `to_ledger_entry(result["detection"])`, the HEADLINE's components and no
    others. The sweep now walks the entry the composer wrote, so the 6dp site
    is simply not in the population, and the Hour-#17 register FAILS on it."""
    measured = pair.measure_component_render_sites()
    # ONE published string renders this figure, at the 3dp its own renderer
    # produces -- not the 6dp of a caveat nobody is handed.
    assert measured["ageing"]["sites"] == (("note", 3),)
    # And the mix figure, whose only reader site is the composer's own inline
    # render in that same note -- the surface no sweep could see before,
    # because the composer is a method.
    assert measured["belief_population_mix"]["sites"] == (("note", 4),)
    assert pair.check_component_render_sites(measured) == []
    hour_17 = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    hour_17["ageing"] = dict(hour_17["ageing"], decimals=6, also_rendered_at=(3,),
                             component_renders=(("ageing.ordinal_direction_caveat", 6),))
    got = pair.check_component_render_sites(measured, register=hour_17)
    assert any("declares a 6dp render into `ageing.ordinal_direction_caveat` "
               "that this scoring does not produce" in v for v in got), got


def test_a_declared_render_site_the_sweep_cannot_find_fires():
    """BOTH WAYS. A declared site nobody can find is a debt entry outliving its
    debt -- the shape this module has already fallen into twice."""
    measured = pair.measure_component_render_sites()
    ghost = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    ghost["detection"] = dict(ghost["detection"],
                              component_renders=(("components.nowhere", 4),))
    got = pair.check_component_render_sites(measured, register=ghost)
    assert any("declares a 4dp render into `components.nowhere` that this "
               "scoring does not produce" in v for v in got), got


def test_a_string_the_scorer_builds_but_nobody_publishes_is_not_a_site():
    """THE POPULATION IS THE ARTEFACT (atom D36). A component of a result the
    ledger writer never carries is exactly the string Hour #17's 6dp came off,
    so the sweep must not find a figure in one -- proven by handing it a book
    whose SCORING renders the figure at 6dp and whose published ENTRY does
    not."""
    books = [_fake_book({"a": 0.12}, {"note": "headline 0.1200"}, 1),
             _fake_book({"a": 0.23}, {"note": "headline 0.2300"}, 2)]
    for b, v in zip(books, (0.12, 0.23)):
        b["result"]["a"].components["unpublished_caveat"] = f"headline {v:.6f}"
    got = pair.measure_component_render_sites(
        books=books, register={"a": dict(_SITE_REGISTER["solo"])})
    assert got["a"]["sites"] == (("note", 4),)


def test_a_literal_that_does_not_move_with_the_figure_is_not_a_render_site():
    """THE DISCRIMINATION RULE, and the false positive it exists to refuse.
    `0.0` is in half the strings this module publishes and is a render of
    nothing; a one-book sweep would report it as this figure's reader
    precision and hand every band a 0.05 epsilon."""
    entry = {"note": "miss_rate 0.0 over 1408 negatives"}
    books = [_fake_book({"a": 0.0145}, entry, 1),
             _fake_book({"a": 0.0218}, entry, 2)]
    with pytest.raises(AssertionError, match="found NO figure rendered"):
        pair.measure_component_render_sites(
            books=books, register={"a": dict(_SITE_REGISTER["solo"])})
    # ... and the SAME sweep does find a site once the literal moves with it.
    moving = [_fake_book({"a": 0.0145}, {"note": "headline 0.0145"}, 1),
              _fake_book({"a": 0.0218}, {"note": "headline 0.0218"}, 2)]
    got = pair.measure_component_render_sites(
        books=moving, register={"a": dict(_SITE_REGISTER["solo"])})
    assert got["a"]["sites"] == (("note", 4),)


def test_one_scoring_cannot_tell_a_render_from_a_constant():
    with pytest.raises(AssertionError, match="needs TWO published books"):
        pair.measure_component_render_sites(
            books=[_fake_book({"a": 0.5}, {"note": ""})],
            register={"a": dict(_SITE_REGISTER["solo"])})


def test_a_carrier_quantised_coarser_than_its_render_fires():
    """HOUR #17's LEAD 2, MECHANISED. Two roundings sit between the scorer and
    the reader and D34 measured only the outer one. Measured on the shipped
    figures the inner one is never the coarser (ageing 6dp/6dp, latency 6dp/2dp,
    the rest unquantised) -- so the control is proven on a book where it is."""
    books = [_fake_book({"a": 0.12}, {"note": "headline 0.120000"}, 1),
             _fake_book({"a": 0.23}, {"note": "headline 0.230000"}, 2)]
    reg = {"a": dict(_SITE_REGISTER["solo"], decimals=6,
                     component_renders=(("note", 6),))}
    measured = pair.measure_component_render_sites(books=books, register=reg)
    assert measured["a"]["carrier_quantum_decimals"] == 2
    got = pair.check_component_render_sites(measured, register=reg)
    assert any("already quantised at 2dp before any render" in v
               for v in got), got


def test_the_shipped_carriers_inner_quantum_is_never_coarser_than_its_render():
    """THE MEASURED NEGATIVE (Hour #17's lead 2, answered rather than assumed).
    Recorded so a future coarsening of any carrier fires here."""
    measured = pair.measure_component_render_sites()
    assert {d: row["carrier_quantum_decimals"]
            for d, row in measured.items()} == {
        "ageing": 6, "detection_latency": 6,
        "belief": 17, "belief_population_mix": 17, "detection": 17}
    for dim, row in measured.items():
        assert pair.published_reading_decimals(dim) <= row[
            "carrier_quantum_decimals"], dim


def test_the_render_site_sweep_runs_in_the_cli_not_only_in_tests():
    """A control that lives only in the test suite is one a reader of the
    instrument's own output never meets."""
    src = inspect.getsource(pair.main)
    assert "measure_component_render_sites" in src
    assert "check_component_render_sites" in src


# --- R15: the control fires on each defect it names -------------------------


def test_the_pre_hour_caveat_fires_the_control(caveat_coverage,
                                               resolution_floors):
    """THE DEFECT ITSELF, put back: the BOOK's bound republished as each
    figure's own resolution. This is the state every ledger note and Proof-door
    reading carried from Hour #9 to Hour #15, and it must not pass."""
    view = {d: copy.deepcopy(caveat_coverage[d].get("_rendered", {}))
            for d in caveat_coverage}
    for dim in ("belief", "belief_population_mix"):
        for seed, comps in view[dim].items():
            comps["measured_resolution_floor_days"] = comps[
                "book_bound_floor_days"]
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, rendered=view, floors=resolution_floors)
    assert any("publishes a resolution floor of 310d and the sweep measures "
               "314d" in v for v in violations), violations


def test_stamping_the_siblings_floor_fires_the_control(caveat_coverage,
                                                       resolution_floors):
    """THE SHARED SENTENCE, in its exact shape: the mix figure carrying
    `belief`'s 310d. One function rendered one sentence for both figures for six
    Hours, and nothing could see it."""
    view = {d: copy.deepcopy(caveat_coverage[d].get("_rendered", {}))
            for d in caveat_coverage}
    for seed, comps in view["belief_population_mix"].items():
        comps["measured_resolution_floor_days"] = pair.DIMENSION_DRIFT_RESOLUTION[
            "belief"]["own_readable_resolution_floor_days"]
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, rendered=view, floors=resolution_floors)
    assert any("is atom D33's finding" in v for v in violations), violations


def test_a_floor_the_sentence_never_states_fires_the_control(caveat_coverage,
                                                            resolution_floors):
    """A component beside a sentence that contradicts it is not a stamped
    caveat -- Hour #11's `a lead is not a control`, in the shape this cell could
    itself have taken."""
    view = {d: copy.deepcopy(caveat_coverage[d].get("_rendered", {}))
            for d in caveat_coverage}
    for seed, comps in view["belief"].items():
        comps["belief_resolution_caveat"] = (
            "a caveat that states no number at all")
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, rendered=view, floors=resolution_floors)
    assert any("never states it" in v for v in violations), violations


def test_a_book_sourced_cell_with_no_floor_fires_the_control(caveat_coverage,
                                                            resolution_floors):
    """The PRE-HOUR REGISTER STATE: the belief cells named a caveat component
    and nothing else, so a population-side bound stood where the figure's own
    resolution goes."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    del reg["belief"]["organ_failure_window_drift_days"][
        "published_floor_component"]
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, register=reg, floors=resolution_floors)
    assert any("a bound on what ANY figure here could resolve stands where" in v
               for v in violations), violations


def test_a_caveat_number_from_another_dimensions_register_fires_the_control(
        caveat_coverage, resolution_floors):
    """D32's WRONG SUBJECT, generalised: a cell sourcing its number from a
    register keyed BY dimension and pointing it at a different one."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    reg["ageing"]["organ_terms_drift_days"]["number_source"] = (
        "DIMENSION_DRIFT_RESOLUTION", "detection")
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, register=reg, floors=resolution_floors)
    assert any("pointed at a different one" in v for v in violations), violations


def test_a_sub_reading_source_with_no_published_number_fires_the_control(
        caveat_coverage, resolution_floors):
    """The `ORGAN_QUERY_GRID` half: an entry whose `headline_key` names a
    sub-reading owes a number measured on the PUBLISHED headline. Dropping that
    is exactly the state D32 found."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    del reg["detection_latency"]["organ_reconciliation_drift_days"][
        "published_step_component"]
    violations = pair.check_published_figure_caveat_coverage(
        caveat_coverage, register=reg, floors=resolution_floors)
    assert any("measured on the SUB-READING" in v for v in violations), violations


def test_a_moving_cell_with_no_number_source_raises(caveat_coverage,
                                                    resolution_floors):
    """THE FAIL-CLOSED. A cell that does not say whose number it publishes is
    not a clean cell -- it is an unasked one, and it reads identically, which is
    how this class survived fifteen Hours."""
    reg = copy.deepcopy(pair.PUBLISHED_FIGURE_CAVEAT_CONTRACT)
    del reg["belief"]["organ_failure_window_drift_days"]["number_source"]
    with pytest.raises(AssertionError, match="no usable `number_source`"):
        pair.check_published_figure_caveat_coverage(
            caveat_coverage, register=reg, floors=resolution_floors)


def test_an_unavailable_floor_sweep_is_a_failed_check(caveat_coverage):
    """R15 FAIL-SILENT: the floor claim compared against nothing must not read
    as verified. This is why the green test supplies the sweep."""
    violations = pair.check_published_figure_caveat_coverage(caveat_coverage)
    assert any("compared against NOTHING" in v for v in violations), violations


def test_a_declared_floor_the_sweep_contradicts_fires_the_control(
        resolution_floors):
    """The register side of the same claim, EXACTLY (the D25/D30 rule): a floor
    declared loosely is a sentence that survives any reshape."""
    reg = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    reg["belief_population_mix"]["own_readable_resolution_floor_days"] = 310
    violations = pair.check_published_resolution_floor(resolution_floors, reg)
    assert any("the sweep measures 314d" in v for v in violations), violations


def test_a_predicate_divergence_with_no_owner_fires_the_control(
        resolution_floors):
    """A measured divergence between bit-equality and the reader's own precision
    OWES an atom -- and a named owner the sweep cannot find is a debt entry
    outliving its debt, so both directions fire."""
    reg = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    reg["belief_population_mix"]["own_floor_predicate_atom"] = None
    violations = pair.check_published_resolution_floor(resolution_floors, reg)
    assert any("no atom owns it" in v for v in violations), violations

    reg = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    reg["belief"]["own_floor_predicate_atom"] = pair.BIT_EQUALITY_FLOOR_ATOM
    violations = pair.check_published_resolution_floor(resolution_floors, reg)
    assert any("outliving its debt" in v for v in violations), violations


def test_an_undeclared_or_unmeasured_floor_raises(resolution_floors):
    """Both keyset directions raise: a measured dimension the register declares
    no floor for, and a declared floor nothing sweeps."""
    reg = copy.deepcopy(pair.DIMENSION_DRIFT_RESOLUTION)
    reg["belief"]["own_readable_resolution_floor_days"] = None
    with pytest.raises(AssertionError, match="register declares none"):
        pair.check_published_resolution_floor(resolution_floors, reg)
    with pytest.raises(AssertionError, match="that nothing measured"):
        pair.check_published_resolution_floor(
            {d: r for d, r in resolution_floors.items() if d != "belief"})


def test_an_unnamed_caller_gets_a_refusal_not_the_siblings_number():
    """The caveat function's own fail-closed: a caller that will not say which
    figure it is stamping gets an explicit refusal, never a default. A silent
    default is the defect this atom closes."""
    text = pair.belief_resolution_caveat(None, None)
    assert "NO FIGURE WAS NAMED" in text
    assert "do NOT share one" in text
    for dim in ("belief", "belief_population_mix"):
        assert f"`{dim}`" in text


def test_the_floor_sweep_refuses_an_inert_probe():
    """THE VACUITY GUARD on the measurement itself: a knob that had stopped
    drifting the company would put every floor at None and certify nothing."""
    records, consumer, _b, as_of = pair.build_scenario(60, seed=7)
    frozen = (records, pair.score_triad(records, consumer, as_of), as_of)
    with pytest.raises(AssertionError, match="inert probe cannot measure"):
        pair.measure_published_resolution_floor(
            n_customers=60, seeds=(7,), runner=lambda knob, seed, k: frozen)


def test_the_floor_sweep_refuses_a_book_with_no_bound():
    """...and a population with no observed failure event has no bound to search
    outward from, so measuring a floor against it would be a free pass."""
    records, consumer, _b, as_of = pair.build_scenario(60, seed=7)
    empty = [r for r in records if r.result != "failed"]
    scored = pair.score_triad(records, consumer, as_of)
    with pytest.raises(AssertionError, match="no book bound"):
        pair.measure_published_resolution_floor(
            n_customers=60, seeds=(7,),
            runner=lambda knob, seed, k: (empty, scored, as_of))


# ---------------------------------------------------------------------------
# THE READER WALK -- atom D35, H27 Expert Hour #19
# ---------------------------------------------------------------------------
# Hour #18 left two leads and they turned out to be one repair. Lead 1: the
# component sweep stops at this process's edge, so the register cannot declare
# the Proof door's own render without the control immediately firing on a
# declared site nobody can find. Lead 2: the walk out to that door crosses
# `coupled_gap_ledger.json`, where the headline is written UNROUNDED, and the
# rule "the epsilon is half a step of the finest render" applied to serialised
# bytes collapses every epsilon this instrument publishes to 1e-18.
#
# THE DEFECT THIS HOUR FOUND while building that walk: the component sweep finds
# ZERO sites for three of the five published figures and its control says
# nothing, because every finding it can emit is keyed to a site it FOUND or a
# site the register DECLARED. Its only vacuity guard is a global
# `any(row["sites"])`, which is Hour #18's own panel-wide-substring shape one
# level up inside the instrument that found it.

NODE_AVAILABLE = shutil.which("node") is not None
needs_node = pytest.mark.skipif(
    not NODE_AVAILABLE,
    reason="the reader walk drives the door's real JavaScript; with no node the "
           "door stage reports UNAVAILABLE and the control FIRES (R15) -- which "
           "is the correct behaviour, but not a thing this assertion can show")


# ---------------------------------------------------------------------------
# THE DOOR WAS RETIRED, AND ITS MACHINERY STILL HAS TO WORK -- the door retirement, 2026-08-21
# ---------------------------------------------------------------------------
# The director's five-tabs ruling (`03dd8c49e`) deleted `site/proof/`. Everything
# below this line used to read the shipped door off the working tree; for a day
# after that ruling all of it errored with `Cannot find module`, which wedged
# every commit touching this file because the gate selects tests by filename
# stem.
#
# The repair is NOT to re-point these at a live surface. `/harness/` inherited
# the proof content but renders four aggregate counts, not a per-pair row, and
# `https://poesys.net/proof/` still answers 200 only because the edge is serving
# a cache the deployment no longer backs (`retired_paths_served.json`). Greening
# a control against either would be the "green suite achieved by deleting the
# subject" this section exists to catch.
#
# So the tests split in two, and the split is the point:
#   * the SHIPPED walk (`reader_walk`) sees what a reader sees -- a retired
#     door and withdrawn sites -- and that is asserted, not worked around;
#   * the walk's MACHINERY is still put on trial, against the retired door's own
#     bytes read out of git at `03dd8c49e^`. That artefact is in a tree and is
#     rebuildable by anyone with this repo, which is exactly what the live 200
#     is not. Every mutation below therefore still proves what it always did --
#     that this instrument fires on its own named defect if a door comes back --
#     while no test claims a reader is being shown anything.
_RETIRED_DOOR_FILES = ("index.html", "_render_harness.mjs")


def _git_show(rev_path: str) -> str:
    proc = subprocess.run(["git", "show", rev_path],
                          cwd=str(Path(pair.__file__).resolve().parent.parent),
                          capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else ""


@pytest.fixture(scope="module")
def retired_door(tmp_path_factory):
    """The retired door's own bytes, materialised out of git history.

    Skipped rather than faked where the history is unavailable (a shallow
    clone): a hand-written stand-in for the door would make every mutation
    below a test of the fixture, which is the D30 defect this module has been
    caught by before.
    """
    root = tmp_path_factory.mktemp("retired_proof_door")
    for name in _RETIRED_DOOR_FILES:
        text = _git_show(f"{pair._DOOR_RETIRING_RULING}^:site/proof/{name}")
        if not text:
            pytest.skip(
                f"the retired door's `{name}` is not reachable at "
                f"{pair._DOOR_RETIRING_RULING}^ -- this needs the repo's history")
        (root / name).write_text(text, encoding="utf-8")
    return {"index": root / "index.html", "harness": root / "_render_harness.mjs"}


@contextlib.contextmanager
def door_restored(retired_door, index_path=None):
    """Point the module at the retired door for the duration of one mutation.

    BOTH constants move together. Moving only `_DOOR_INDEX` -- which is what
    every mutation here used to do, when the harness happened to be on disk --
    would leave the walk reading a harness that is no longer there, and the
    mutation would "pass" on an error that has nothing to do with its subject.
    """
    previous = (pair._DOOR_INDEX, pair._DOOR_HARNESS)
    pair._DOOR_INDEX = index_path if index_path is not None else retired_door["index"]
    pair._DOOR_HARNESS = retired_door["harness"]
    try:
        yield
    finally:
        pair._DOOR_INDEX, pair._DOOR_HARNESS = previous


# What the register declared while the door was live (Hour #21's shipped state).
# Kept HERE rather than in the module: the withdrawal is the module's answer,
# and a mutation that restores the door has to restore the declarations with it
# or it is measuring the withdrawal instead of the machinery.
_WITHDRAWN_DOOR_RENDERS = {
    "ageing": (("door:coupled-gaps#note", 3),),
    "belief": (("door:coupled-gaps#note", 4),),
    "belief_population_mix": (("door:coupled-gaps#note", 4),),
    "detection": (("door:coupled-gaps#gap-val", 3), ("door:coupled-gaps#note", 4)),
    "detection_latency": (("door:coupled-gaps#note", 2),),
}


def _register_with_the_door_back():
    reg = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    for dim, restored in _WITHDRAWN_DOOR_RENDERS.items():
        reg[dim] = dict(reg[dim], reader_renders=tuple(sorted(
            set(reg[dim].get("reader_renders") or ()) | set(restored))))
    return reg


@pytest.fixture(scope="module")
def reader_walk():
    """THE SHIPPED WALK -- against the site as it is, with the door retired."""
    return pair.measure_reader_render_sites()


@pytest.fixture(scope="module")
def door_walk(retired_door):
    """The same walk with the retired door put back, so the machinery that
    measured it can still be held to what it claims."""
    with door_restored(retired_door):
        return pair.measure_reader_render_sites()


@pytest.fixture(scope="module")
def component_walk():
    return pair.measure_component_render_sites()


def test_all_five_figures_are_rendered_in_the_published_note(component_walk):
    """WHERE THE FIGURES ACTUALLY MEET A READER (atom D36). Hour #19 recorded
    that three of the five had no component site at all; that was a fact about
    a population -- every string the SCORER builds -- in which the one artefact
    a reader is handed did not appear. Walking the published entry instead, all
    five are rendered in its note, each at its own declared precision."""
    assert {d: component_walk[d]["sites"] for d in sorted(component_walk)} == {
        "ageing": (("note", 3),),
        "belief": (("note", 4),),
        "belief_population_mix": (("note", 4),),
        "detection": (("note", 4),),
        "detection_latency": (("note", 2),),
    }
    assert pair.check_component_render_sites(component_walk) == []


def test_the_shipped_walk_records_the_door_as_RETIRED_not_as_broken(reader_walk):
    """THE SENTENCE THAT WEDGED THIS FILE (the door retirement, 2026-08-21). For a day after the
    five-tabs ruling the walk raised `Cannot find module`, which asserts the
    tool is broken. Nothing was broken: the surface was deleted on purpose, and
    the difference is what sent the previous taker looking for a moved path.

    So the retirement is now a STATE the control can read, carrying the ruling
    that caused it -- and it is reached only when the door is wholly absent, a
    half-present door being a broken one (proven below)."""
    walk = reader_walk["_walk"]
    assert walk["retired"] is True, walk
    assert walk["retired_by"] == pair._DOOR_RETIRING_RULING
    assert walk["available"] is False
    assert "RETIRED" in str(walk["reason"])
    assert "Cannot find module" not in str(walk["reason"])
    # ...and the four regions are recorded as WITHDRAWN rather than forgotten:
    # the walk still names the surfaces it can no longer measure.
    assert set(walk["withdrawn_sites"]) == {
        f"door:coupled-gaps#{r}" for r in pair._DOOR_REGIONS}
    # No figure reaches a door site any more, and no register entry claims one.
    for dim in sorted(d for d in reader_walk if d != "_walk"):
        assert not any(k.startswith("door:") for k, _dp in reader_walk[dim]["sites"])
        assert reader_walk[dim]["reaches_the_door"] is False
        assert not any(str(k).startswith("door:") for k, _dp
                       in (pair.PUBLISHED_GAP_CONSUMERS[dim].get("reader_renders") or ()))


def test_the_ruling_really_deleted_the_door_this_walk_says_it_did():
    """THE RETIREMENT IS EVIDENCE, NOT A STORY SOMEBODY TYPED. `03dd8c49e` is a
    string in the module; this is the check that the commit it names is the one
    that removed the door, so a wrong SHA cannot sit there being reassuring."""
    proc = subprocess.run(
        ["git", "show", "--name-status", "--format=", pair._DOOR_RETIRING_RULING,
         "--", "site/proof/"],
        cwd=str(Path(pair.__file__).resolve().parent.parent),
        capture_output=True, text=True)
    if proc.returncode != 0:
        pytest.skip("this needs the repo's history")
    deleted = {line.split("\t", 1)[1] for line in proc.stdout.splitlines()
               if line.startswith("D\t")}
    for name in _RETIRED_DOOR_FILES:
        assert f"site/proof/{name}" in deleted, proc.stdout
    # ...and it is still gone. A door quietly restored would make every
    # withdrawal below false, which is the first thing the guard checks.
    assert pair._door_retirement() is not None


def test_a_half_present_door_is_BROKEN_and_never_retired(tmp_path, monkeypatch):
    """R15's fail-open direction, on the retirement itself. If "some file is
    missing" counted as retirement, any future breakage that happened to remove
    a file would launder itself into an accepted limitation. Retirement needs
    the door wholly gone; one file present is a broken door and must be one."""
    monkeypatch.setattr(pair, "_DOOR_INDEX", tmp_path / "index.html")
    monkeypatch.setattr(pair, "_DOOR_HARNESS", tmp_path / "_render_harness.mjs")
    assert pair._door_retirement() is not None          # both absent: retired
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    assert pair._door_retirement() is None              # one present: NOT retired
    with pytest.raises(RuntimeError) as exc:
        pair._door_render({"pairs": []})
    assert not isinstance(exc.value, pair.DoorRetired)


def test_the_withdrawal_is_silent_only_while_it_is_true(reader_walk, component_walk):
    """THE NULL CONTROL FOR THE WITHDRAWAL. On the site as it stands the door is
    retired, no page renders the rows, no entry declares a door site -- so the
    control says nothing, and every figure still meets an artefact through the
    published note. That silence is what the three mutations below have to be
    read against: a guard that is quiet everywhere proves nothing."""
    assert pair.check_door_retirement_still_holds() == []
    assert pair.check_reader_render_sites(reader_walk, component_walk) == []
    # The withdrawal did NOT cost any figure its coverage: the per-dimension
    # vacuity guard is the one that would say so, and it is silent.
    for dim in sorted(pair.PUBLISHED_GAP_CONSUMERS):
        assert (set(reader_walk[dim]["sites"])
                | set(component_walk[dim]["sites"])), dim


def test_a_door_that_comes_back_makes_the_withdrawal_fire(retired_door):
    """FALSIFIER 1. The withdrawal rests on the door being gone. Put its files
    back and the retirement is false -- those reader surfaces are owed a
    measurement again, not an accepted limitation."""
    with door_restored(retired_door):
        got = pair.check_door_retirement_still_holds()
    assert any("retirement every withdrawal below rests on is FALSE" in v
               for v in got), got


def test_a_successor_that_renders_the_rows_again_makes_the_withdrawal_fire(tmp_path):
    """FALSIFIER 2, AND THE ONE THAT MATTERS. The withdrawal is a claim about
    the SITE -- that no page shows these figures to a reader. A successor door
    growing the row back would make it false silently, and this is what refuses
    to let that happen: it names the page and says re-point the walk at THAT
    one, never at the retired path and never at the cached 200."""
    (tmp_path / "successor").mkdir()
    (tmp_path / "successor" / "index.html").write_text(
        '<div class="gap-row"><div class="gap-val">0.014</div></div>',
        encoding="utf-8")
    got = pair.check_door_retirement_still_holds(site_root=tmp_path)
    assert any("renders coupled-gap rows again" in v for v in got), got
    assert any("successor/index.html" in v for v in got), got
    assert any("never at the cached 200" in v for v in got), got


def test_the_successor_sweep_does_not_fire_on_the_aggregate_panel_that_did_inherit():
    """THE SWEEP'S OWN DISCRIMINATION, MEASURED ON THE REAL SUCCESSOR. `/harness/`
    inherited the proof content and does read `d.coupled_gaps` -- so a sweep for
    the word "gap" would call it a restored door and the withdrawal would be
    permanently, wrongly red. It renders four aggregate counts and fixed prose,
    not a per-pair row, and this asserts the sweep tells those apart on the
    shipped file rather than on a fixture."""
    harness = Path(pair.__file__).resolve().parent.parent / "site" / "harness" / "index.html"
    text = harness.read_text(encoding="utf-8")
    assert "coupled_gaps" in text and "gap-note" in text     # it really is the heir
    assert pair.door_successors_rendering_coupled_gap_rows() == ()


def test_a_register_that_re_declares_a_withdrawn_door_site_fires():
    """FALSIFIER 3. The other way the withdrawal goes wrong is quietly, in the
    register: a figure's epsilon set from a surface this module has just said no
    reader is shown."""
    reg = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    reg["detection"] = dict(reg["detection"],
                            reader_renders=(("door:coupled-gaps#gap-val", 3),))
    got = pair.check_door_retirement_still_holds(register=reg)
    assert any("detection: still declares the withdrawn door site" in v
               for v in got), got


@needs_node
def test_the_walks_machinery_still_measures_a_door_that_comes_back(door_walk):
    """HOUR #18's LEAD 1, KEPT ALIVE PAST ITS SUBJECT. The retired door renders
    the ledger carrier at 3dp via `fmtGap` -- the first render site any sweep of
    this module found outside its own process. Nobody is shown it any more, and
    that is asserted above; what this asserts is that the instrument which
    measured it has not rotted, so a door that comes back is measured rather
    than trusted."""
    walk = door_walk["_walk"]
    assert walk["available"] is True, walk
    assert walk.get("retired") is not True
    assert ("door:coupled-gaps#gap-val", 3) in door_walk["detection"]["sites"]
    assert door_walk["detection"]["reaches_the_door"] is True
    # ONE figure is CARRIED to the door as a number and re-rendered there by
    # `fmtGap`; the other four ride inside the printed note as digits already
    # chosen. Since Hour #21 that answer comes from the identity of the object
    # the composer handed the ledger writer, not from a float comparison.
    assert walk["headline_dimension"] == "detection"
    assert [d for d in sorted(door_walk) if d != "_walk"
            and door_walk[d]["reaches_the_door"]] == ["detection"]


def test_every_published_figure_now_meets_an_artefact_and_no_epsilon_moved(
        reader_walk, component_walk):
    """R12: this Hour changed what is MEASURED, never what is computed.

    Needs no node since the door retirement, 2026-08-21: with the door retired there is no JavaScript
    left to drive, and every surface these figures have is inside this process.
    That is the withdrawal stated as a fact about the suite."""
    assert pair.check_reader_render_sites(reader_walk, component_walk) == []
    assert pair.check_component_render_sites(component_walk) == []
    # ageing was 6 between Hours #17 and #20, on a site nobody is handed (D36).
    assert {d: pair.published_reading_decimals(d)
            for d in pair.PUBLISHED_GAP_CONSUMERS} == {
        "ageing": 3, "belief": 4, "belief_population_mix": 4,
        "detection": 4, "detection_latency": 2}


def test_an_epsilon_finer_than_every_surface_fires(reader_walk, component_walk):
    """R15, THE GUARD THIS HOUR ADDS. Both checks asked only whether some site
    is FINER than the declaration. Neither asked the other direction, so a
    figure whose epsilon had been moved onto a string nobody publishes passed
    both in silence -- which is exactly what `ageing` did for three Hours.
    Mutated to Hour #17's shipped state, the guard names it and the factor."""
    hour_17 = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    hour_17["ageing"] = dict(hour_17["ageing"], decimals=6,
                             component_renders=(("note", 3),))
    got = pair.check_reader_render_sites(reader_walk, component_walk,
                                         register=hour_17)
    assert any("ageing: sets its epsilon from 6dp while the FINEST site either "
               "sweep can find renders it at 3dp" in v and "1000x too fine" in v
               for v in got), got
    # ...and it does NOT fire on the shipped register, where every declaration
    # equals its own finest measured surface.
    assert pair.check_reader_render_sites(reader_walk, component_walk) == []


# --- R15: the reader walk fires on each defect it names ---------------------

@needs_node
def test_a_carrier_read_as_text_collapses_every_epsilon_to_the_doubles_width():
    """HOUR #18's LEAD 2, MECHANISED AND PROVEN LOAD-BEARING.

    The walk classifies a hand-off by the TYPE it is holding and never searches
    serialised text. This mutation restores the search the rule's literal
    reading demands -- look for the figure in the ledger's BYTES -- and asserts
    the 18dp site comes straight back. Nobody chose those digits; they are the
    double's. An epsilon set from them is 1e-18, which no reader can ever be
    shown a difference at, and every band, floor and collapse this instrument
    certifies rests on it."""
    results = [pair.score_triad(*pair._resolution_population(300, s)[:2],
                                pair._resolution_population(300, s)[3])
               for s in pair._RENDER_SITE_SEEDS]
    texts, values = [], []
    for res in results:
        headline = res["detection"]
        entry = headline.to_ledger_entry(pair.TWIN_ATOM_ID)
        texts.append(json.dumps({pair.WORLD_ATOM_ID: entry}))
        values.append(float(headline.gap))
    # The type-classified walk finds NO site in a hand-off: `gap` is a number.
    assert all(isinstance(json.loads(t)[pair.WORLD_ATOM_ID]["gap"], float)
               for t in texts)
    # The text-searched one finds the figure far past any declared precision.
    deep = [dp for dp in range(1, 19)
            if len({format(v, f".{dp}f") for v in values}) == len(values)
            and all(pair._rendered_at(v, dp, t) for v, t in zip(values, texts))]
    assert max(deep) >= 17, deep
    assert 0.5 * 10 ** -max(deep) < 1e-16
    # ...and that is smaller than the shipped epsilon by 13 orders of magnitude.
    assert pair.published_reading_epsilon("detection") / (0.5 * 10 ** -max(deep)) > 1e12


@needs_node
def test_a_door_rendering_finer_than_the_declared_epsilon_fires(tmp_path, retired_door):
    """THE ALARM THE DOOR SITE EXISTS FOR. `fmtGap` at 3dp is coarser than the
    declared 4dp; the moment it is not, the reader can separate two companies
    the epsilon calls identical -- and before Hour #19 nothing would have said
    so.

    Run against the retired door's own bytes and the declarations that were live
    with it (the door retirement, 2026-08-21). Restoring the door WITHOUT restoring the declarations
    would measure the withdrawal instead of this alarm."""
    mutated = tmp_path / "index.html"
    original = retired_door["index"].read_text(encoding="utf-8")
    assert 'Number(v).toFixed(3); }' in original
    mutated.write_text(
        original.replace("function fmtGap(v){ return v==null?\"—\":Number(v).toFixed(3); }",
                         "function fmtGap(v){ return v==null?\"—\":Number(v).toFixed(6); }"),
        encoding="utf-8")
    with door_restored(retired_door, index_path=mutated):
        measured = pair.measure_reader_render_sites()
    assert ("door:coupled-gaps#gap-val", 6) in measured["detection"]["sites"]
    got = pair.check_reader_render_sites(measured, pair.measure_component_render_sites(),
                                         register=_register_with_the_door_back())
    assert any("sets its epsilon from 4dp while a reader surface renders it at "
               "6dp" in v for v in got), got


@needs_node
def test_a_door_that_stops_printing_the_note_verbatim_fires(tmp_path, retired_door):
    """THE SEAM THE RENDERER STAGE RESTED ON WHILE THERE WAS A DOOR. Four of the
    five figures were measured on their renderer's OUTPUT, and that string was a
    reader surface only because the door concatenated it unchanged.

    Since the retirement (the door retirement, 2026-08-21) those `renderer:` sites are evidence of a
    chosen PRECISION in a published string and no longer evidence of a reader --
    which is written down in the register rather than left to be inferred. This
    keeps the seam's alarm alive for the door that comes back."""
    mutated = tmp_path / "index.html"
    original = retired_door["index"].read_text(encoding="utf-8")
    assert "esc(p.note)" in original
    mutated.write_text(original.replace("esc(p.note)", '"[note withheld]"'),
                       encoding="utf-8")
    with door_restored(retired_door, index_path=mutated):
        measured = pair.measure_reader_render_sites()
    assert measured["_walk"]["note_verbatim"] is False
    got = pair.check_reader_render_sites(measured, pair.measure_component_render_sites(),
                                         register=_register_with_the_door_back())
    assert any("no longer prints the carried note verbatim" in v for v in got), got


def test_a_composer_that_stops_carrying_a_renderers_string_fires(monkeypatch):
    """THE REAL SHAPE OF THE renderer -> NOTE DEFECT, MUTATED ON THE COMPOSER'S
    SIDE (atom D38, H27 Expert Hour #22).

    Until this Hour this control mutated the WALK's renderer and read the
    resulting divergence as the composer's -- a mutation of one side used as
    proof about the other, which is what Hour #20 named at the ledger seam and
    Hour #21 named in `has_door_carrier`, recurring here in the module system.
    The defect it exists for is a composer that reformats, re-rounds or drops
    the render it is handed, so THAT is what moves: the renderer object stays
    the shipped one and the note the reader is handed loses its string."""
    import background.gap_metric as gap_metric
    import background.live_payment_triad as lpt
    real_writer = lpt.write_gap_entry

    def reformatting_composer(world_atom, twin_atom, headline, **kw):
        headline.note = str(headline.note).replace("ageing displacement",
                                                   "ageing gap")
        return real_writer(world_atom, twin_atom, headline, **kw)

    monkeypatch.setattr(lpt, "write_gap_entry", reformatting_composer)
    monkeypatch.setattr(pair, "_PUBLISHED_BOOKS", {})
    books = pair.published_books()
    measured = pair.measure_reader_render_sites(books=books, door=False)
    # THE MUTATION IS ONE-SIDED, AND THAT IS MEASURED RATHER THAN ASSUMED: the
    # renderer the walk executed is the object the composer held.
    assert measured["ageing"]["renderer_provenance"] == "the_composers"
    assert gap_metric.format_ageing_summary is lpt.format_ageing_summary
    assert measured["ageing"]["renderer_in_note"] is False
    got = pair.check_reader_render_sites(measured,
                                         pair.measure_component_render_sites())
    assert any("its declared renderer's output is NOT in the composed note" in v
               for v in got), got


def test_a_walk_that_swapped_the_renderer_measures_the_swap_not_the_seam(
        monkeypatch):
    """THE CONTROL THIS HOUR EXISTS FOR, AND IT IS THE OLD CONTROL'S OWN
    MUTATION TURNED INTO A REFUSAL (atom D38).

    Patching the renderer at its source module moves what the WALK calls; the
    composer bound that name at ITS import time, so what it already wrote does
    not move with it -- UNLESS the composer's module had not been imported when
    the patch landed, in which case both sides move together and the seam is
    not measured at all. Which of those two happened depended on whether an
    earlier test in the file had imported the composer, i.e. on test ORDER: run
    alone, the old control asserted a divergence that could not occur (proven
    pre-existing at HEAD 43a456cba). The walk now records whose renderer it
    executed, so both outcomes are loud and neither is attributed to the
    composer."""
    import background.gap_metric as gap_metric
    import background.live_payment_triad as lpt  # BEFORE the patch
    original = gap_metric.format_ageing_summary
    monkeypatch.setattr(
        gap_metric, "format_ageing_summary",
        lambda r: original(r).replace("ageing displacement", "ageing gap"))
    # The composer's binding did NOT move -- the one fact the old control
    # depended on and never checked.
    assert lpt.format_ageing_summary is original
    measured = pair.measure_reader_render_sites(door=False)
    assert measured["ageing"]["renderer_provenance"] == "not_the_composers"
    got = pair.check_reader_render_sites(measured,
                                         pair.measure_component_render_sites())
    assert any("executed a renderer object the composer did not hold" in v
               and "an unavailable check is a failed check" in v
               for v in got), got
    # AND THE DIVERGENCE IS NOT ATTRIBUTED TO THE COMPOSER. `renderer_in_note`
    # is False here too, and reading that as a composer defect is precisely the
    # wrong-side attribution this Hour is about.
    assert measured["ageing"]["renderer_in_note"] is False
    assert not any("its declared renderer's output is NOT in the composed note"
                   in v for v in got), got


def test_the_composer_mutation_control_does_not_depend_on_an_empty_cache(
        monkeypatch):
    """R15 STANDING REGRESSION GUARD ON HOUR #21'S OWN FINDING (H27 Expert Hour
    #38, on owed item (C)/#21's "vacuous-in-isolation sibling control").

    Hour #21 found the PRE-D38 composer control vacuous under exactly one
    precondition: `_PUBLISHED_BOOKS` was already warm from an earlier test in
    the file, so the composer's mutation landed after the books it measured
    had already been composed, and the divergence it exists to prove could
    not occur. Hour #23 built the fix -- the `_PUBLISHED_BOOKS` reset inside
    `test_a_composer_that_stops_carrying_a_renderers_string_fires` -- and
    verified it by running that one node id ALONE.

    THAT VERIFICATION COULD NEVER HAVE CAUGHT A REGRESSION OF ITS OWN FIX,
    which is why the finding survived unverified in every "STILL OWED" list
    from Hour #28 through Hour #37 (re-checked at HEAD before this Hour wrote
    a line of code: both node ids still pass alone today). A fresh process
    running a single node id starts with an EMPTY `_PUBLISHED_BOOKS`
    regardless of whether the reset line is present at all -- so "run alone"
    can never manufacture the one precondition the original defect needed,
    and a future edit that deletes the reset line would pass every existing
    check in this file while silently reintroducing Hour #21's defect,
    discoverable again only by luck of full-suite test order.

    This test manufactures that precondition directly -- it warms the cache
    itself, standing in for "an earlier test already ran" -- and then calls
    the SHIPPED control as a plain function rather than re-deriving its
    steps, so a future edit to that function's own reset is what this test
    is actually exercising, not a parallel copy of its logic that could drift
    from it.
    """
    import tools.couple_w2_11_d5 as pair_module
    monkeypatch.setattr(pair_module, "_PUBLISHED_BOOKS", {})
    warm = pair_module.published_books()
    assert warm, ("the warm-up itself produced no books to warm the cache "
                  "with -- this test cannot manufacture the precondition it "
                  "exists to test")
    # THE SHIPPED CONTROL, CALLED WITH THE CACHE ALREADY WARM. If its own
    # `_PUBLISHED_BOOKS` reset is ever removed, this call -- not a fresh
    # "run alone" -- is what catches it.
    test_a_composer_that_stops_carrying_a_renderers_string_fires(monkeypatch)


def test_a_book_that_records_no_renderer_provenance_fails_closed():
    """R15's third killer pattern, on this Hour's own field. A book carrying no
    record of what the composer held leaves the seam unmeasured -- which must
    read as a FAILED check, never as a clean one."""
    # THE POSITIVE SIDE FIRST, on the shipped walk: all four walkable renderers
    # ARE the composer's own objects -- including the one it imports under an
    # alias, which a name-only lookup would report as held by nobody.
    shipped = pair.measure_reader_render_sites(door=False)
    assert {d: shipped[d]["renderer_provenance"] for d in sorted(shipped)
            if d != "_walk"} == {
        "ageing": "the_composers", "belief": "the_composers",
        "belief_population_mix": None, "detection": "the_composers",
        "detection_latency": "the_composers"}
    books = [{k: v for k, v in b.items() if k != "composer_renderers"}
             for b in pair.published_books()]
    measured = pair.measure_reader_render_sites(books=books, door=False)
    assert measured["ageing"]["renderer_provenance"] == "unrecorded"
    got = pair.check_reader_render_sites(measured,
                                         pair.measure_component_render_sites())
    for dim in ("ageing", "belief", "detection", "detection_latency"):
        assert any(v.startswith(f"{dim}: this walk executed a renderer object "
                                "the composer did not hold") for v in got), dim


def test_an_unreachable_door_is_a_failed_check_never_a_clean_one():
    """R15's third killer pattern. A walk that could not reach the door must not
    degrade to "no sites found", which reads exactly like a clean door."""
    measured = pair.measure_reader_render_sites(door=False)
    assert measured["_walk"]["available"] is False
    assert measured["detection"]["reaches_the_door"] is False
    got = pair.check_reader_render_sites(measured, pair.measure_component_render_sites())
    assert any("never reached the Proof door" in v
               and "an unavailable check is a failed check" in v for v in got), got


@needs_node
def test_a_declared_reader_site_the_walk_cannot_find_fires(reader_walk):
    """BOTH DIRECTIONS, as the component control already does."""
    ghost = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    ghost["ageing"] = dict(ghost["ageing"],
                           reader_renders=(("door:coupled-gaps", 3),))
    got = pair.check_reader_render_sites(reader_walk, register=ghost)
    assert any("declares a 3dp reader site `door:coupled-gaps` that this walk "
               "cannot find" in v for v in got), got


@needs_node
def test_a_figure_rendered_at_no_site_anywhere_fires(reader_walk, component_walk):
    """THE GUARD THIS HOUR EXISTS FOR, and it is PER DIMENSION. The shipped
    global `any()` passes while three of five figures are unmeasured; this one
    names each of them."""
    blanked = {k: (dict(v) if k != "_walk" else v) for k, v in reader_walk.items()}
    blanked_components = {k: dict(v) for k, v in component_walk.items()}
    for dim in ("belief", "detection", "detection_latency"):
        blanked[dim]["sites"] = ()
        blanked_components[dim]["sites"] = ()
    got = pair.check_reader_render_sites(blanked, blanked_components)
    for dim in ("belief", "detection", "detection_latency"):
        assert any(v.startswith(f"{dim}: is rendered at NO site either sweep "
                                "can find") for v in got), (dim, got)
    # AND THE UNION IS REAL, in both directions. A figure the reader walk finds
    # nowhere still passes on the component sweep's site (and the reverse), so
    # the guard is over the union and not over either sweep alone.
    reader_only_blank = {k: (dict(v) if k != "_walk" else v)
                         for k, v in reader_walk.items()}
    reader_only_blank["ageing"]["sites"] = ()
    ok = pair.check_reader_render_sites(reader_only_blank, component_walk)
    assert not any(v.startswith("ageing: is rendered at NO site") for v in ok), ok
    # ...and with BOTH halves gone, it fires.
    both_blank = {k: dict(v) for k, v in component_walk.items()}
    both_blank["ageing"]["sites"] = ()
    gone = pair.check_reader_render_sites(reader_only_blank, both_blank)
    assert any(v.startswith("ageing: is rendered at NO site either sweep can find")
               for v in gone), gone


def test_a_sibling_quantity_that_moves_with_the_figure_is_not_a_render_of_it(
        reader_walk, component_walk):
    """EXPERT HOUR #19's SECOND FINDING. The two-seed rule tells a figure from a
    CONSTANT -- it cannot tell it from a sibling quantity that moves with it.

    `belief_population_mix` (a population TV distance) equals belief's PER-CASE
    DISAGREEMENT rate on every book measured, so its digits appear at 4dp inside
    `format_belief_summary`, which does not render it. They are different
    quantities: the D19 note records that they separate under a permutation of
    which account holds which severity belief, and no real book performs that
    permutation. A value-only sweep would have moved this figure's epsilon on
    the strength of another figure's render precision."""
    site = "renderer:background/gap_metric.py::format_belief_summary"
    assert (site, 4) in reader_walk["belief_population_mix"]["cross_attributed"]
    assert (site, 4) not in reader_walk["belief_population_mix"]["sites"]
    # Its own door site -- the printed note, where the composer's inline `.4f`
    # rendered it (atom D37, Hour #21) -- was WITHDRAWN with the door (the door retirement, 2026-08-21), so
    # this figure now has an EMPTY `reader_renders` and its whole coverage is
    # the component sweep's. The collision never touched that surface, and this
    # asserts the withdrawal did not silently take it too.
    assert pair.PUBLISHED_GAP_CONSUMERS["belief_population_mix"]["reader_renders"] == ()
    assert ("note", 4) in component_walk["belief_population_mix"]["sites"]
    # THE COINCIDENCE IS REAL, on more books than the walk itself uses.
    for seed in (23, 101, 999):
        records, consumer, _b, as_of = pair._resolution_population(300, seed)
        scored = pair.score_triad(records, consumer, as_of)
        rendered = format_belief_summary(scored["belief"])
        mix = format(scored["belief_population_mix"].gap, ".4f")
        assert f"per-case disagreement {mix} " in rendered, (seed, mix)
    # AND THE DECLARATION IS LOAD-BEARING: without it the walk refuses to guess.
    undeclared = {k: dict(v) for k, v in pair.PUBLISHED_GAP_CONSUMERS.items()}
    undeclared["belief_population_mix"] = dict(
        undeclared["belief_population_mix"], value_collisions=())
    got = pair.check_reader_render_sites(reader_walk, component_walk,
                                         register=undeclared)
    assert any("ANOTHER figure's declared renderer" in v
               and "never from a sibling quantity that moves with it" in v
               for v in got), got


def test_an_uncallable_declared_renderer_is_recorded_not_skipped(reader_walk):
    """A register naming a renderer nobody can call must say so: a silent skip
    is a dimension whose surface was never looked at, reading as one that was."""
    assert reader_walk["belief_population_mix"]["renderer_status"].startswith(
        "background.live_payment_triad has no module-level `measure_and_write`")
    assert all(reader_walk[d]["renderer_status"] == "called"
               for d in ("ageing", "belief", "detection", "detection_latency"))


def test_the_reader_walk_runs_in_the_cli_not_only_in_tests():
    """A control that lives only in the test suite is one a reader of the
    instrument's own output never meets."""
    src = inspect.getsource(pair.main)
    assert "measure_reader_render_sites" in src
    assert "check_reader_render_sites" in src


# ---------------------------------------------------------------------------
# THE DOOR IS FOUR SURFACES, AND WHOSE THEY ARE IS A PROVENANCE QUESTION
# (atom D37, H27 Expert Hour #21 -- Hour #20's leads 1 and 2, one repair)
# ---------------------------------------------------------------------------
# THE DEFECT. `has_door_carrier` admitted a dimension to the door surface only
# where its carrier EQUALLED the panel row's value -- a VALUE test doing
# PROVENANCE work, the exact shape Hour #19 named for `cross_attributed` and
# then left standing in the gate one level up. Two consequences, and they point
# opposite ways: it EXCLUDED the four companion figures from a surface that
# demonstrably renders them (the panel prints the composed note, and every
# companion's own renderer's digits are in it), and it would have handed the
# WHOLE panel -- `fmtGap`'s 3dp and every 4dp numeric component -- to any
# companion that happened to equal the headline.

@needs_node
def test_every_figure_reaches_the_door_and_the_headline_is_known_by_identity(
        door_walk, component_walk):
    """WHAT THE VALUE GATE WAS HIDING. All five figures are rendered on the
    door, inside the note it prints verbatim, each at its own declared
    precision; ONE of them is additionally carried there as a number and
    re-rendered by `fmtGap`, and which one is answered by the identity of the
    object the composer handed the ledger writer.

    On the RETIRED door's own bytes since the door retirement, 2026-08-21 -- this is the property that
    would have to hold again if a successor rendered these rows, and the exact
    map of door sites the register withdrew."""
    assert door_walk["_walk"]["headline_dimension"] == "detection"
    assert {d: sorted(s for s in door_walk[d]["sites"]
                      if s[0].startswith("door:"))
            for d in sorted(d for d in door_walk if d != "_walk")} == {
        "ageing": [("door:coupled-gaps#note", 3)],
        "belief": [("door:coupled-gaps#note", 4)],
        "belief_population_mix": [("door:coupled-gaps#note", 4)],
        "detection": [("door:coupled-gaps#gap-val", 3),
                      ("door:coupled-gaps#note", 4)],
        "detection_latency": [("door:coupled-gaps#note", 2)],
    }
    # ...and it is EXACTLY what the register withdrew -- the map above is the
    # `_WITHDRAWN_DOOR_RENDERS` this file declares, measured off the artefact
    # rather than copied from it, so a withdrawal that took too much or too
    # little would show up here.
    assert {d: sorted(s for s in door_walk[d]["sites"] if s[0].startswith("door:"))
            for d in sorted(_WITHDRAWN_DOOR_RENDERS)} == {
        d: sorted(v) for d, v in _WITHDRAWN_DOOR_RENDERS.items()}
    # R12: no epsilon moved in either direction. Every door site was at a
    # precision the figure already had, which is why withdrawing them costs no
    # figure its declared precision.
    assert {d: pair.published_reading_decimals(d)
            for d in pair.PUBLISHED_GAP_CONSUMERS} == {
        "ageing": 3, "belief": 4, "belief_population_mix": 4,
        "detection": 4, "detection_latency": 2}
    assert pair.check_reader_render_sites(
        door_walk, component_walk, register=_register_with_the_door_back()) == []


@needs_node
def test_the_headline_is_not_decided_by_comparing_floats(door_walk):
    """R15, THE MUTATION HOUR #21 EXISTS FOR. Restore the value gate and point
    it at a companion whose carrier has been made equal to the headline's: the
    value test hands that companion the door's `gap-val` and `components`
    regions, and the provenance test does not."""
    books = pair.published_books()
    values = [float(b["result"]["detection"].gap) for b in books]
    row_values = list(door_walk["_walk"]["carrier_by_book"])
    # The gate that shipped until this Hour, restated.
    def value_gate(carriers):
        return all(a is not None and float(a) == float(b)
                   for a, b in zip(carriers, row_values))
    assert value_gate(values)                      # the headline passes it
    mix = list(door_walk["belief_population_mix"]["carrier_by_seed"].values())
    assert not value_gate(mix)                     # today, so does nothing else
    # BUT IT IS A COINCIDENCE THAT NOTHING ELSE DOES. A companion equal to the
    # headline on both books is admitted by the value gate to the whole panel.
    assert value_gate(row_values)
    # The provenance answer does not move with the digits at all: it is the
    # object the composer passed, and every book agrees on it.
    assert {b["headline_dimension"] for b in books} == {"detection"}
    # ...and the regions it owns cross-attribute everyone else, rather than
    # silently crediting them with `fmtGap`'s precision.
    for dim in ("ageing", "belief", "belief_population_mix", "detection_latency"):
        assert not any(k.endswith(("#gap-val", "#components", "#basis"))
                       for k, _dp in door_walk[dim]["sites"]), dim


def test_a_composer_that_routes_around_the_ledger_seam_fails_the_walk(monkeypatch):
    """R15: an unmeasured provenance is an unmeasured reader step. With nothing
    captured at the seam, the walk must refuse -- never fall back to the digits.

    THE MUTATION IS THE CALL SITE, NOT THE ATTRIBUTE, and the difference is the
    whole test. `write_gap_entry` is a module GLOBAL of the composer's module,
    so `_publish_one_book`'s spy wraps whatever that name currently holds --
    including a neutralising stand-in. Replacing the attribute therefore
    suppresses the WRITE while the spy still counts one crossing, and the run
    dies on the absent ledger file rather than on this refusal: a mutation that
    proves nothing about the provenance capture. What the check actually defends
    is a refactor that moves the write OFF the name the walk spies on -- the
    ledger still written, the seam no longer crossed -- so that is what is
    mutated here, and the ledger is written through the function object directly.
    """
    import background.live_payment_triad as lpt
    original = lpt.LivePaymentTriad.measure_and_write

    def routed_around_the_seam(self, *a, **k):
        # `write_gap_entry` here is this test module's OWN binding to the real
        # function, taken at import time -- the same object, reached by a name
        # the spy does not own.
        spied, lpt.write_gap_entry = lpt.write_gap_entry, write_gap_entry
        try:
            return original(self, *a, **k)
        finally:
            lpt.write_gap_entry = spied

    monkeypatch.setattr(lpt.LivePaymentTriad, "measure_and_write",
                        routed_around_the_seam)
    monkeypatch.setattr(pair, "_PUBLISHED_BOOKS", {})
    with pytest.raises(AssertionError) as exc:
        pair.published_books(specs=({"n_customers": 60, "months": 4},
                                    {"n_customers": 70, "months": 4}))
    assert "handed 0 result(s) to the ledger writer" in str(exc.value)
    assert "an unavailable check is a failed check" in str(exc.value)


@needs_node
def test_a_door_region_the_walk_cannot_name_fails_closed(tmp_path, retired_door):
    """R15. The whole subject of this instrument is reader surfaces nobody
    searched. A door that grows a fifth region must fail the walk rather than
    render a figure into a region no sweep looks at.

    AND IT MUST FAIL AS BROKEN, NOT AS RETIRED (the door retirement, 2026-08-21). A present door that
    the walk cannot read is the failed check R15 names; only a wholly absent one
    is the withdrawal. This asserts the two states do not collapse into each
    other, which is the fail-open a retirement flag invites."""
    mutated = tmp_path / "index.html"
    original = retired_door["index"].read_text(encoding="utf-8")
    assert "'<div class=\"gap-basis\">'" in original
    mutated.write_text(
        original.replace("'<div class=\"gap-basis\">'",
                         "'<div class=\"gap-audit\">audit '+esc(fmtGap(p.value))+"
                         "'</div><div class=\"gap-basis\">'"),
        encoding="utf-8")
    with door_restored(retired_door, index_path=mutated):
        measured = pair.measure_reader_render_sites()
    assert measured["_walk"]["available"] is False
    assert measured["_walk"]["retired"] is False
    assert "gap-audit" in str(measured["_walk"]["reason"])
    got = pair.check_reader_render_sites(measured,
                                         pair.measure_component_render_sites())
    assert any("never reached the Proof door" in v for v in got), got


@needs_node
def test_a_door_region_that_vanishes_is_not_a_region_that_renders_nothing(
        tmp_path, retired_door):
    """R15's fail-silent pattern, on the region split itself. A region the door
    stopped rendering reads to a value sweep exactly like a region in which the
    figure does not appear.

    This is the same distinction the retirement rests on, one level down: a
    region that VANISHED is a defect, an absent DOOR is a withdrawal, and
    neither may be read as the other."""
    mutated = tmp_path / "index.html"
    original = retired_door["index"].read_text(encoding="utf-8")
    assert "+fmtGap(p.value)+'</div>'" in original
    mutated.write_text(original.replace("+fmtGap(p.value)+'</div>'",
                                        "+''+'</div>'"), encoding="utf-8")
    with door_restored(retired_door, index_path=mutated):
        measured = pair.measure_reader_render_sites()
    assert measured["_walk"]["available"] is False
    assert measured["_walk"]["retired"] is False
    assert "rendered no ['gap-val'] region" in str(measured["_walk"]["reason"])


@needs_node
def test_a_door_note_that_diverges_from_the_entrys_note_fires(
        door_walk, component_walk):
    """THE VERBATIM SEAM IN THIS INSTRUMENT'S OWN UNITS. Four of the five
    figures' door coverage rested entirely on the panel printing the entry's
    note unchanged. `note_verbatim` tests that on the note's first 60
    characters; this tests it where it is load-bearing -- at every precision the
    note renders each figure. Held against the retired door's bytes (the door retirement, 2026-08-21)."""
    register = _register_with_the_door_back()
    diverged = {k: (dict(v) if k != "_walk" else v)
                for k, v in door_walk.items()}
    diverged["detection_latency"]["sites"] = tuple(
        s for s in diverged["detection_latency"]["sites"]
        if s[0] != "door:coupled-gaps#note")
    got = pair.check_reader_render_sites(diverged, component_walk, register=register)
    assert any("detection_latency: the door's printed note renders it at no "
               "precision while the entry's own note renders it at [2]" in v
               for v in got), got
    # ...and it is SILENT on the unmutated walk, where the two agree everywhere.
    assert pair.check_reader_render_sites(
        door_walk, component_walk, register=register) == []


@needs_node
def test_the_doors_numeric_component_render_is_now_a_searched_surface(
        door_walk, retired_door):
    """HOUR #20's LEAD 2. `fmtComponent`/`flattenNumbers` re-render every finite
    numeric leaf of the HEADLINE's components at 4dp -- a surface the component
    sweep structurally cannot see (it searches the entry's STRINGS) and the old
    door search could not reach (it was open to one dimension, as one string).
    It is a named region with an owner. Measured: it rendered none of the five
    published figures, so no epsilon rested on it -- and that is a measurement
    rather than an absence of one, which is why withdrawing it costs nothing."""
    assert "door:coupled-gaps#components" in door_walk["_walk"]["regions"]
    assert not any(k == "door:coupled-gaps#components"
                   for d in door_walk if d != "_walk"
                   for k, _dp in (tuple(door_walk[d]["sites"])
                                  + tuple(door_walk[d]["cross_attributed"])))
    # The region is REAL and does render numbers at 4dp -- an empty region would
    # produce the same "no sites" answer, which is why the walk refuses one.
    assert "Number(v).toFixed(4)" in retired_door["index"].read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# THE ROW'S OWN POPULATION -- atom D40, H27 Expert Hour #27
# ---------------------------------------------------------------------------
# Hour #21 built the door's four named regions and minted two leads it did not
# take: D40, that `_DOOR_ROW_KNOWN_CLASSES` is a hand-typed keyset ("the open
# question is whether the row's regions can be derived from the door's own
# render instead of enumerated"), and D39, that the bar is a scaled render no
# sweep here can express. They are one repair, for the same reason Hour #21's
# own two leads were: the scaled render lives on a CLASSLESS span, so it is not
# merely unexpressed by the literal sweeps -- it is not in the census's
# population at all. A census keyed on `class` cannot see an element that does
# not carry one, and this row has five of those.
#
# What replaces the enumeration is not a derivation from the door (that would
# make the subject its own population -- every class the door renders would be
# known by construction, which is the fail-open direction of the same mistake).
# The population is the RENDERED ELEMENTS; the register says what each one IS;
# and the two-book rule this module already turns on decides who is right.


def _fixture_row_htmls(
    retired_door,
    values=(0.118, 0.129),
    notes=("note A 0.118", "note B 0.129"),
    components=({"n": 1.0}, {"n": 2.0}),
    raw_gaps=(0.0, 0.0),
    index_path=None,
):
    """Two rendered rows, produced by the door's OWN JavaScript.

    Synthetic payloads, not published books: the subject of this control is the
    row's SHAPE, which is the door's and not the scoring's, and driving two
    real books through the composer to measure it would pay two scorings for a
    property neither of them decides. That the fixture reproduces the shipped
    population EXACTLY is asserted below rather than assumed.

    THE DOOR IS THE RETIRED ONE, READ OUT OF GIT (the door retirement, 2026-08-21). The row census is a
    property of that artefact, and the artefact is in a tree; what is no longer
    true -- that a reader is shown any of it -- is asserted directly one section
    up rather than smuggled in by keeping these green.
    """
    previous = (pair._DOOR_INDEX, pair._DOOR_HARNESS)
    pair._DOOR_INDEX = index_path if index_path is not None else retired_door["index"]
    pair._DOOR_HARNESS = retired_door["harness"]
    try:
        out = []
        for v, note, comp, raw in zip(values, notes, components, raw_gaps):
            out.append(pair._door_render({"pairs": [{
                "world_atom": pair.WORLD_ATOM_ID,
                "company_atom": pair.TWIN_ATOM_ID,
                "metric": "detection", "value": v, "baseline_g0": 0.5,
                "raw_gap": raw, "note": note, "components": comp,
                "measured_at": "2026-08-13T00:00:00Z",
                "run_git_commit": "abcdef1234",
                "world_level": 3, "company_level": 3, "blocks_l3": False,
            }]}))
        return out
    finally:
        pair._DOOR_INDEX, pair._DOOR_HARNESS = previous


def _census(htmls, values=(0.118, 0.129), headline="detection"):
    measured = pair.measure_door_row_surfaces(htmls, values)
    return pair.check_door_row_surfaces(
        {"available": True, "row_surfaces": measured,
         "headline_dimension": headline}), measured


@needs_node
def test_the_row_census_is_the_rendered_elements_and_the_register_is_clean(retired_door):
    """NOT ALWAYS-RED, and the population is the ARTEFACT's. Every element the
    door renders has a declaration, every declaration has an element, and the
    shipped register describes the shipped door exactly."""
    got, measured = _census(_fixture_row_htmls(retired_door))
    assert got == [], got
    assert set(measured["surfaces"]) == set(pair._DOOR_ROW_SURFACES)
    # THE POPULATION THE CLASS CENSUS COULD NOT EXPRESS, counted: five elements
    # of this row carry no class at all, and one of them renders the headline.
    classless = sorted(p for p in measured["surfaces"]
                       if "." not in p.rsplit("/", 1)[-1])
    assert len(classless) == 5, classless
    assert "div.gap-row[0]/div.gap-bar[0]/span[0]" in classless
    for path in classless:
        assert path not in pair._DOOR_ROW_KNOWN_CLASSES
    # ...and the movement classification is a MEASUREMENT, not a restatement of
    # the declaration: the surfaces really do split three ways on this book pair.
    moving = {p for p, s in measured["surfaces"].items() if s["text_moves"]}
    assert len(moving) == 3, sorted(moving)
    assert measured["surfaces"]["div.gap-row[0]/div.gap-bar[0]/span[0]"][
        "attrs_moved"] == ("style",)


@needs_node
def test_a_classless_element_the_door_grows_fires(tmp_path, retired_door):
    """THE HOLE THE CLASS CENSUS CANNOT EXPRESS. `_DOOR_ROW_KNOWN_CLASSES`
    refuses any class it cannot name -- and an element with no class attribute
    is not a class it cannot name, it is an element it never looked at. The
    door is mutated to grow one, rendering the figure, and the class census
    stays SILENT while the element census fires."""
    original = retired_door["index"].read_text(encoding="utf-8")
    mutated = tmp_path / "index.html"
    assert "'<div class=\"gap-basis\">'" in original
    mutated.write_text(
        original.replace("'<div class=\"gap-basis\">'",
                         "'<span>'+fmtGap(p.value)+'</span>'+"
                         "'<div class=\"gap-basis\">'"),
        encoding="utf-8")
    htmls = _fixture_row_htmls(retired_door, index_path=mutated)
    # THE OLD CENSUS IS SILENT ON IT -- proven, not asserted.
    assert pair._door_row_regions(htmls[0])
    got, _ = _census(htmls)
    assert any("carries no class at all, which is the hole the class census "
               "cannot express" in v for v in got), got
    assert any("div.gap-row[0]/span[0]" in v for v in got), got


@needs_node
def test_a_wrapper_that_starts_rendering_the_figure_fires(tmp_path, retired_door):
    """A DECLARED STRUCTURAL WRAPPER THAT MOVES. The class census's answer to
    any door change is the same refusal whichever it was, discharged by
    appending a string; this one states what the surface IS and is wrong when
    the surface stops being it."""
    original = retired_door["index"].read_text(encoding="utf-8")
    mutated = tmp_path / "index.html"
    assert "'<div class=\"gap-bar\"><span style=\"width:'" in original
    mutated.write_text(
        original.replace("'<div class=\"gap-bar\"><span style=\"width:'",
                         "'<div class=\"gap-bar\">'+fmtGap(p.value)+"
                         "'<span style=\"width:'"),
        encoding="utf-8")
    got, _ = _census(_fixture_row_htmls(retired_door, index_path=mutated))
    assert any("div.gap-bar[0]` is declared structural and INERT, and its text "
               "moves between books" in v for v in got), got


@needs_node
def test_a_searched_region_gone_constant_fires(tmp_path, retired_door):
    """AN INERT REGION IS NOT AN EMPTY ONE. The walk one level up refuses a
    region that came back EMPTY; a region that renders the same string on both
    books is not empty, and to the two-book rule it is indistinguishable from a
    region that does not render the figure at all."""
    original = retired_door["index"].read_text(encoding="utf-8")
    mutated = tmp_path / "index.html"
    assert "'<div class=\"gap-note\">'+esc(p.note)+'</div>'" in original
    mutated.write_text(
        original.replace("'<div class=\"gap-note\">'+esc(p.note)+'</div>'",
                         "'<div class=\"gap-note\">a fixed sentence</div>'"),
        encoding="utf-8")
    htmls = _fixture_row_htmls(retired_door, index_path=mutated)
    # The region is PRESENT and non-empty, so the shipped guard is silent.
    assert pair._door_row_regions(htmls[0])["door:coupled-gaps#note"].strip()
    got, _ = _census(htmls)
    assert any("declared a searched region (`note`) and renders the SAME text "
               "on both books" in v for v in got), got


@needs_node
def test_a_declaration_that_outlived_its_element_fires(tmp_path, retired_door):
    """THE OTHER DIRECTION. A door that stops rendering a declared surface
    reads to every sweep here exactly like a surface that renders nothing."""
    original = retired_door["index"].read_text(encoding="utf-8")
    mutated = tmp_path / "index.html"
    mutated.write_text(
        original.replace("'<div class=\"gap-basis\">'",
                         "'<div class=\"gap-DELETED\">'"),
        encoding="utf-8")
    got, _ = _census(_fixture_row_htmls(retired_door, index_path=mutated))
    assert any("div.gap-basis[0]` is declared as a door surface and the "
               "rendered row does not contain it" in v for v in got), got


@needs_node
def test_a_render_that_arrives_in_an_attribute_fires(tmp_path, retired_door):
    """A RENDER NEED NOT BE TEXT (atom D39's class). Every literal sweep in
    this module reads text; the one surface of this row that renders the
    headline outside its text was invisible to all of them."""
    original = retired_door["index"].read_text(encoding="utf-8")
    mutated = tmp_path / "index.html"
    mutated.write_text(
        original.replace("'<div class=\"gap-basis\">'",
                         "'<div class=\"gap-basis\" title=\"'+fmtGap(p.value)+"
                         "'\">'"),
        encoding="utf-8")
    got, _ = _census(_fixture_row_htmls(retired_door, index_path=mutated))
    assert any("moves in attribute(s) ['title'] that its declaration does not "
               "allow" in v for v in got), got


@needs_node
def test_a_bar_that_stops_matching_its_declared_scaling_fires(tmp_path, retired_door):
    """THE SCALED RENDER, HELD TO THE PIXEL (atom D39). The declaration is what
    makes this surface expressible at all -- so the check is that it PREDICTS
    the rendered literal from the carrier, on every book."""
    original = retired_door["index"].read_text(encoding="utf-8")
    mutated = tmp_path / "index.html"
    assert "barPct.toFixed(0)" in original
    mutated.write_text(original.replace("barPct.toFixed(0)", "barPct.toFixed(2)"),
                       encoding="utf-8")
    got, _ = _census(_fixture_row_htmls(retired_door, index_path=mutated))
    assert any("declared scaling (100x at 0dp) predicts `12`" in v
               for v in got), got


@needs_node
def test_a_scaled_render_finer_than_the_epsilon_fires(tmp_path, retired_door):
    """THE ALARM THE SCALED SURFACE EXISTS FOR. 100x at 0dp is 2dp of the
    figure, coarser than the 4dp detection's epsilon is set from, so nothing
    moves today. At 100x/3dp -- 5dp of the figure -- the reader can separate
    two companies the epsilon calls identical, and before this Hour no sweep in
    this module could have said so, because they all search UNSCALED digits."""
    original = retired_door["index"].read_text(encoding="utf-8")
    mutated = tmp_path / "index.html"
    mutated.write_text(original.replace("barPct.toFixed(0)", "barPct.toFixed(3)"),
                       encoding="utf-8")
    declared = dict(pair._DOOR_ROW_SURFACES)
    key = "div.gap-row[0]/div.gap-bar[0]/span[0]"
    declared[key] = dict(declared[key], decimals=3)
    original_reg = pair._DOOR_ROW_SURFACES
    try:
        pair._DOOR_ROW_SURFACES = declared
        got, _ = _census(_fixture_row_htmls(retired_door, index_path=mutated))
    finally:
        pair._DOOR_ROW_SURFACES = original_reg
    # The declaration now DESCRIBES the door -- this is not a prediction miss.
    assert not any("predicts" in v for v in got), got
    assert any("renders detection at an effective 5dp (100x scaled, 3dp) while "
               "its epsilon is set from 4dp" in v for v in got), got


@needs_node
def test_a_row_whose_shape_is_the_books_refuses(retired_door):
    """FAIL CLOSED ON A POPULATION THAT IS NOT ONE. Aligning what two books
    have in common and measuring that would report the elements they agree
    about and stay silent about an element only one of them renders -- which is
    this walk's own subject, one level down."""
    # A book the door renders as UNTESTED: no bar span, a different chip, so
    # the element paths are not the same set. The real instance of this is a
    # ledger entry with no measured gap, which the door renders every day.
    got, measured = _census(
        _fixture_row_htmls(retired_door, values=(0.118, None)), values=(0.118, None))
    assert measured["available"] is False
    assert any("is not the same SHAPE on both books" in v for v in got), got
    assert any("an unavailable check is a failed check" in v for v in got), got


def test_a_reached_door_with_no_row_census_fires():
    """FAIL-SILENT. An unrun census reads exactly like a clean row -- and a
    walk that reached the door and recorded none is exactly that."""
    got = pair.check_door_row_surfaces(
        {"available": True, "headline_dimension": "detection"})
    assert any("reached the door and recorded no row census at all" in v
               for v in got), got
    # ...and where the door was never reached, the caller's own finding covers
    # it and this one stays quiet rather than doubling it.
    assert pair.check_door_row_surfaces({"available": False}) == []


def test_the_row_census_refuses_a_single_book():
    """ONE BOOK CANNOT CLASSIFY A SURFACE. With one row, a wrapper holding a
    constant and a region rendering the figure are the same observation."""
    with pytest.raises(AssertionError, match="needs TWO books"):
        pair.measure_door_row_surfaces(["<div class=\"gap-row\"></div>"])


# ---------------------------------------------------------------------------
# THE CHECK-CALL CENSUS (R10 closure for the no-caller class, 2026-08-15)
# ---------------------------------------------------------------------------
# Three `check_*` functions in this module shipped with no caller in three
# consecutive Expert Hours, and each was closed by adding the missing call. R10
# forbids exactly that: the class is closed by a control that makes the whole
# class fail automatically, and these are that control's own R15 pass. Every
# mutation below leaves the module itself untouched -- the census reads a
# SOURCE STRING, so each defect can be built rather than described.

_CENSUS_SRC_WIRED = '''
def check_alpha(x):
    return []


def check_beta(x):
    return []


def main():
    args = _parse()
    check_alpha(1)
    if args.beta_sweep:
        check_beta(2)
'''


def test_every_check_this_module_defines_is_reachable_from_main():
    """THE SHIPPED STATE, and the reason this control exists. On 2026-08-15 the
    census's first population was 15 defined `check_*` functions with 10 called
    from `main()`: `check_detection_interior_change_points`,
    `check_door_row_surfaces`, `check_scenario_constant_census`,
    `check_published_figure_caveat_coverage` and
    `check_published_resolution_floor` were unreachable from the run that
    publishes, while two shipped comments said the first of them re-derived its
    bands "every run"."""
    measured = pair.measure_check_call_census()
    assert measured["main_found"] is True
    # A census over a handful of functions would be a control that had lost its
    # subject; this module really does define this many.
    assert len(measured["defined"]) >= 15, measured["defined"]
    assert pair.check_check_call_census(measured) == []
    assert measured["uncalled"] == ()
    assert measured["conditional_unflagged"] == ()
    # The five that were unreachable are each accounted for BY NAME, so a
    # silent un-wiring cannot pass as a population change.
    for name in ("check_detection_interior_change_points",
                 "check_door_row_surfaces",
                 "check_scenario_constant_census"):
        assert name in measured["default_path"], name
    for name in ("check_published_figure_caveat_coverage",
                 "check_published_resolution_floor"):
        assert name in measured["behind_a_flag"], name
        assert pair.CHECKS_BEHIND_A_FLAG[name]["reason"].strip()
    # INSTANCE FOUR GUARD: a reachability census that itself had no caller
    # would be the defect it exists to close.
    assert "check_check_call_census" in measured["default_path"]


def test_the_census_is_clean_on_a_wired_module():
    """The control must be able to say YES. A census that fires on a correctly
    wired module would be re-derived into uselessness the first time it did."""
    measured = pair.measure_check_call_census(_CENSUS_SRC_WIRED)
    assert measured["default_path"] == ("check_alpha",)
    assert measured["behind_a_flag"] == {"check_beta": ("beta_sweep",)}
    register = {"check_beta": {"flag": "beta_sweep", "reason": "expensive"}}
    assert pair.check_check_call_census(measured, register=register) == []


def test_a_check_with_no_caller_in_main_fires_by_name():
    """THE CLASS ITSELF (R10). This is what shipped three Hours running, and
    what nothing in the repo could say out loud until this census existed."""
    src = _CENSUS_SRC_WIRED.replace("    check_alpha(1)\n", "")
    measured = pair.measure_check_call_census(src)
    assert measured["uncalled"] == ("check_alpha",)
    violations = pair.check_check_call_census(
        measured, register={"check_beta": {"flag": "beta_sweep", "reason": "x"}})
    assert any("`check_alpha` is DEFINED in this module and called from "
               "NOWHERE in `main()`" in v for v in violations), violations


def test_a_check_hidden_behind_an_undeclared_flag_fires():
    """The escape hatch, closed. Moving a control behind an opt-in flag is
    legitimate and cheap; doing it without declaring the flag makes an
    unreachable control indistinguishable from a deliberately opt-in one."""
    measured = pair.measure_check_call_census(_CENSUS_SRC_WIRED)
    violations = pair.check_check_call_census(measured, register={})
    assert any("only inside `if args.beta_sweep:` and nothing declares why" in v
               for v in violations), violations


def test_a_check_reachable_only_under_a_conditional_with_no_flag_fires():
    """`if False:` reads EXACTLY like a wired control to any census that only
    asks whether the name appears in `main()` -- so this one asks whether there
    is a flag a reader could pass to make it run."""
    src = _CENSUS_SRC_WIRED.replace("    check_alpha(1)\n",
                                    "    if _never():\n        check_alpha(1)\n")
    measured = pair.measure_check_call_census(src)
    assert measured["conditional_unflagged"] == ("check_alpha",)
    assert measured["uncalled"] == ()
    violations = pair.check_check_call_census(
        measured, register={"check_beta": {"flag": "beta_sweep", "reason": "x"}})
    assert any("names no `args.<flag>`" in v for v in violations), violations


@pytest.mark.parametrize("register,expected", (
    ({"check_beta": {"flag": "other_flag", "reason": "x"}},
     "the declaration has come apart from the code it describes"),
    ({"check_beta": {"flag": "beta_sweep", "reason": "   "}},
     "declared off the default path with NO reason"),
    ({"check_beta": {"flag": "beta_sweep", "reason": "x"},
      "check_gone": {"flag": "z", "reason": "x"}},
     "a declaration outliving its subject"),
    ({"check_beta": {"flag": "beta_sweep", "reason": "x"},
      "check_alpha": {"flag": "alpha_flag", "reason": "x"}},
     "the exemption is false"),
))
def test_a_rotted_exemption_fires_in_both_directions(register, expected):
    """R15 ON THE REGISTER, not just on the code. An allowlist nobody re-reads
    becomes the place controls go to stop running -- so a declaration that has
    come apart from the code fires whichever side moved."""
    measured = pair.measure_check_call_census(_CENSUS_SRC_WIRED)
    violations = pair.check_check_call_census(measured, register=register)
    assert any(expected in v for v in violations), violations


@pytest.mark.parametrize("src,expected", (
    ("def main():\n    pass\n", "found NO `check_*` functions"),
    ("def check_alpha(x):\n    return []\n", "could not find `main()`"),
))
def test_the_census_fails_closed_on_its_own_missing_subject(src, expected):
    """R15's THIRD pattern, on the control that closes the class: a census over
    no functions, and one that never found the caller it measures against, both
    read exactly like a fully wired module. An unavailable check is a failed
    check."""
    measured = pair.measure_check_call_census(src)
    violations = pair.check_check_call_census(measured, register={})
    assert any(expected in v for v in violations), violations


def test_the_interior_control_now_runs_on_the_run_that_publishes():
    """BLOCKING 3's wiring half, pinned separately from the census: the caveat
    is written into the ledger by `main()`, and until 2026-08-15 that run
    executed every SIBLING resolution check and not this one -- while two
    shipped comments claimed the bands were "re-derived every run" by it."""
    src = inspect.getsource(pair.main)
    assert "measure_detection_interior_change_points(" in src
    assert "check_detection_interior_change_points(" in src
    # ...and the verdict is PRINTED, because a control whose result nobody
    # renders is a control the reader of the figure never meets (the D25 rule).
    assert "_icp_violations" in src


# ---------------------------------------------------------------------------
# THE DOOR AGAINST THE LEDGER OF RECORD (H27 Expert Hour #33, 2026-08-17)
# ---------------------------------------------------------------------------
# These are HERMETIC on purpose. The live pair of artefacts is asserted by the
# SITE-lane tripwire (`site/proof/test_door_reproduces_the_ledger_of_record.py`),
# whose gate fires on a `site/data` change -- i.e. on a regeneration, which is
# the moment the substitution lands. Asserting the live files HERE would put a
# control whose whole subject is "a test process rewrote the live ledger" inside
# a test process that can be raced by exactly that, so a true finding would
# arrive as a flake. What belongs here is the control's own failure behaviour.

def _door_payload(atom, *, value, components, generated_at="2026-08-17T00:00:00Z"):
    return {
        "generated_at": generated_at,
        "coupled_gaps": {"pairs": [
            {"world_atom": "W1_5_premise_demand_shape", "value": 1.0,
             "components": {"caught": 1}},
            {"world_atom": atom, "value": value, "components": dict(components)},
        ]},
    }


def _ledger_payload(atom, *, gap, components,
                    measured_at="2026-08-17T00:00:00+00:00"):
    return {atom: {"gap": gap, "measured_at": measured_at,
                   "components": dict(components)}}


# The real 2026-08-17 numbers: the production book, and the fixture book that
# stood in for it on the regenerated door. Used verbatim so these tests are
# pinned to the incident rather than to invented digits.
# `missed_failure_rate` carried on both since 2026-08-18 (Expert Hour #37). It
# is 0.0 on each -- `missed` is 0 in both books, and the live door serves
# exactly that -- so the pinning is unchanged; what changed is that these
# fixtures now carry the SAME required floor the real artefacts do, instead of
# omitting one of the ten and modelling a door that could not exist.
_PRODUCTION_BOOK = {
    "caught": 31, "flagged_size": 391, "missed": 0, "truth_size": 31,
    "universe_size": 1600, "n_negatives": 1451, "n_excluded": 118,
    "n_false_flags": 242, "false_flag_rate": 0.166782,
    "missed_failure_rate": 0.0,
}
_FIXTURE_BOOK = {
    "caught": 4, "flagged_size": 35, "missed": 0, "truth_size": 4,
    "universe_size": 276, "n_negatives": 257, "n_excluded": 15,
    "n_false_flags": 16, "false_flag_rate": 0.062257,
    "missed_failure_rate": 0.0,
}
_PRODUCTION_GAP = 0.0833907649896623
_FIXTURE_GAP = 0.0311284046692607


def _write_pair(tmp_path, door, ledger):
    door_p, ledger_p = tmp_path / "proof.json", tmp_path / "ledger.json"
    door_p.write_text(json.dumps(door), encoding="utf-8")
    ledger_p.write_text(json.dumps(ledger), encoding="utf-8")
    return door_p, ledger_p


def _check(tmp_path, door, ledger, atom=None):
    atom = pair.WORLD_ATOM_ID if atom is None else atom
    door_p, ledger_p = _write_pair(tmp_path, door, ledger)
    measured = pair.measure_published_door_against_the_ledger(
        door_path=door_p, ledger_path=ledger_p, world_atom_id=atom)
    return measured, pair.check_published_door_reproduces_the_ledger(measured)


def test_a_door_serving_the_ledgers_own_measurement_is_clean(tmp_path):
    """The control must be able to PASS, or its reds mean nothing."""
    atom = pair.WORLD_ATOM_ID
    measured, violations = _check(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components=_PRODUCTION_BOOK),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=_PRODUCTION_BOOK),
    )
    assert violations == [], violations
    # ...and it compared a real population, not an empty one.
    assert len(measured["compared"]) >= 9, measured["compared"]


def test_the_fixture_book_substitution_of_2026_08_17_fires(tmp_path):
    """THE INCIDENT ITSELF, replayed with its own numbers.

    A test process running `run_phase2b` rewrote the live ledger with a
    276-invoice book; `site/data/proof.json` was regenerated inside that window
    and the working tree carried a door publishing this atom's headline as
    0.0311 against the production book's 0.0834. Exactly one of the fourteen
    pairs on that door moved, and nothing fired. This is the state that must
    never read clean again."""
    atom = pair.WORLD_ATOM_ID
    _, violations = _check(
        tmp_path,
        _door_payload(atom, value=_FIXTURE_GAP, components=_FIXTURE_BOOK),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=_PRODUCTION_BOOK),
    )
    blob = " ".join(violations)
    assert any("0.0311" in v and "0.0833" in v for v in violations), violations
    # The HEADLINE is not the only thing wrong, and naming only it would leave a
    # reader thinking one number drifted rather than the whole book changing.
    for name in ("universe_size", "n_negatives", "caught", "false_flag_rate"):
        assert f"components.{name}" in blob, (name, violations)


def test_a_headline_that_agrees_while_the_book_underneath_does_not_fires(tmp_path):
    """R15: the components are not decoration. Two different books can round to
    the same headline -- a balanced error over two directions is a MEAN, so a
    smaller book with proportionally similar rates reproduces it. If only the
    top-line float were compared, the substitution would be invisible whenever
    the fixture happened to score alike."""
    atom = pair.WORLD_ATOM_ID
    _, violations = _check(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components=_FIXTURE_BOOK),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=_PRODUCTION_BOOK),
    )
    assert violations, "an agreeing headline over a different book read clean"
    assert all("components." in v for v in violations), violations


@pytest.mark.parametrize("missing", ["door", "ledger"])
def test_an_absent_artefact_is_a_failed_check_never_a_clean_one(tmp_path, missing):
    """R15 FAIL-SILENT. The pre-Hour shape of this defect is a reader served a
    figure attributable to nothing on disk; a control that passes when one side
    is GONE would report agreement in precisely that state."""
    atom = pair.WORLD_ATOM_ID
    door_p, ledger_p = _write_pair(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components=_PRODUCTION_BOOK),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=_PRODUCTION_BOOK),
    )
    (door_p if missing == "door" else ledger_p).unlink()
    measured = pair.measure_published_door_against_the_ledger(
        door_path=door_p, ledger_path=ledger_p, world_atom_id=atom)
    violations = pair.check_published_door_reproduces_the_ledger(measured)
    assert violations, f"a missing {missing} read as agreement"
    assert "unavailable check is a FAILED check" in " ".join(violations) or \
        "attributable to nothing on disk" in " ".join(violations), violations


@pytest.mark.parametrize("side", ["door", "ledger"])
def test_a_side_that_has_stopped_carrying_this_pair_fires(tmp_path, side):
    """FAIL-OPEN, the second pattern. `[p for p in pairs if ...]` returning
    nothing, and `ledger.get(atom)` returning None, both iterate zero rows and
    every comparison below is vacuously true. A door that has stopped publishing
    this atom is a failed read, not an agreeing one."""
    atom = pair.WORLD_ATOM_ID
    door = _door_payload(atom, value=_PRODUCTION_GAP, components=_PRODUCTION_BOOK)
    ledger = _ledger_payload(atom, gap=_PRODUCTION_GAP, components=_PRODUCTION_BOOK)
    if side == "door":
        door["coupled_gaps"]["pairs"] = [
            p for p in door["coupled_gaps"]["pairs"] if p["world_atom"] != atom]
    else:
        ledger = {}
    _, violations = _check(tmp_path, door, ledger, atom=atom)
    assert violations, f"a {side} with no `{atom}` row read as agreement"


def test_a_pair_sharing_no_comparable_component_is_a_violation(tmp_path):
    """VACUITY, the pattern this instrument's own leak witness shipped in until
    2026-08-08: with nothing in common, every component assertion passes by
    having no subject. Agreement on an empty set is not agreement."""
    atom = pair.WORLD_ATOM_ID
    _, violations = _check(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components={"something_else": 1}),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components={"another": 2}),
    )
    assert violations, "a pair with no shared component reported agreement"
    assert any("compared\nnothing" in v.replace(" ", "\n") or
               "compared nothing" in v for v in violations), violations


def test_malformed_json_on_either_side_is_a_violation(tmp_path):
    """An unreadable file must not be caught into `{}`: an empty dict compares
    equal to nothing and would pass the whole control."""
    atom = pair.WORLD_ATOM_ID
    door_p = tmp_path / "proof.json"
    ledger_p = tmp_path / "ledger.json"
    door_p.write_text("{not json", encoding="utf-8")
    ledger_p.write_text(json.dumps(
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=_PRODUCTION_BOOK)),
        encoding="utf-8")
    measured = pair.measure_published_door_against_the_ledger(
        door_path=door_p, ledger_path=ledger_p, world_atom_id=atom)
    assert pair.check_published_door_reproduces_the_ledger(measured)


def test_the_door_ledger_control_runs_on_the_run_that_publishes():
    """The R10 lesson this instrument has now paid for FOUR times: a control
    with no caller on a publishing run is a control the reader of the figure
    never meets. The check-call census enforces this generically; this pins the
    RENDER too, which the census cannot see."""
    src = inspect.getsource(pair.main)
    assert "measure_published_door_against_the_ledger(" in src
    assert "check_published_door_reproduces_the_ledger(" in src
    assert "_dvl_violations" in src


def test_the_component_population_is_not_a_hand_picked_subset(tmp_path):
    """The control's subject must be the book, not four convenient fields. Every
    component the 2026-08-17 substitution moved is compared -- measured against
    the incident's own two books rather than asserted."""
    moved = {k for k in _PRODUCTION_BOOK
             if _PRODUCTION_BOOK[k] != _FIXTURE_BOOK.get(k)}
    assert moved, "the two incident books should differ"
    uncovered = moved - set(pair._DOOR_LEDGER_COMPONENTS)
    assert not uncovered, (
        f"components that really moved in the incident are outside the "
        f"control's population: {sorted(uncovered)}")


# --------------------------------------------------------------------------- #
# THE SUBJECT IS DERIVED, NOT DECLARED (Expert Hour #37, 2026-08-18)
#
# THE DEFECT, measured on the committed pair at HEAD f72135409 before any repair:
# the door and the ledger of record DISAGREED on two published fields --
# `recon_saturation_band_days` ([-6, 483] vs [-6, 82]) and
# `recon_saturation_caveat` (2,625 chars vs 821, the ledger still carrying the
# pre-D28 sentence) -- and `check_published_door_reproduces_the_ledger` returned
# ZERO violations, because the comparison walked `_DOOR_LEDGER_COMPONENTS` and
# neither name is in it. 2 of 19 shared fields were divergent; 10 were compared.
#
# Neither prior guard could have caught it, and that is the point of the shape
# change rather than a wider tuple. `test_the_component_population_is_not_a_hand_picked_subset`
# above measures coverage against the fields that moved in the 2026-08-17
# incident -- every one numeric -- and the SITE-lane ratchet asserts
# `declared <= compared`, which wedges when a field LEAVES. Both prove the
# subject has not SHRUNK. Neither can ask whether it was ever the whole
# published surface, and the field that went unchecked is the one carrying the
# instrument's own disclosed limits: the same `*_caveat` family that published a
# measurably false claim at Hour #31 and a correction reaching no surface at #32.

def test_a_shared_component_outside_the_declared_tuple_is_still_compared(tmp_path):
    """THE MUTATION THAT PINS #37's DEFECT. A field both artefacts carry, named
    nowhere in `_DOOR_LEDGER_COMPONENTS`, must be on trial.

    Uses the incident's own divergence rather than invented digits: the real
    band the committed door and ledger disagreed on at HEAD."""
    atom = pair.WORLD_ATOM_ID
    assert "recon_saturation_band_days" not in pair._DOOR_LEDGER_COMPONENTS, (
        "this test's subject is a field OUTSIDE the declared tuple -- if it has "
        "been added there, the derivation is no longer what is under test")
    door = dict(_PRODUCTION_BOOK, recon_saturation_band_days=[-6, 483])
    led = dict(_PRODUCTION_BOOK, recon_saturation_band_days=[-6, 82])
    measured, violations = _check(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components=door),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=led))
    assert "recon_saturation_band_days" in measured["compared"]
    assert any("recon_saturation_band_days" in v for v in violations), (
        f"a component both sides publish diverged and nothing fired: "
        f"{violations!r}")


def test_the_old_declared_only_subject_is_blind_to_that_divergence(tmp_path):
    """THE NULL CONTROL for the test above: restore the pre-#37 shape and the
    SAME pair must come back clean.

    Without this, widening the subject could be a change that fixes nothing --
    this is what proves the repair is load-bearing rather than decorative."""
    atom = pair.WORLD_ATOM_ID
    door = dict(_PRODUCTION_BOOK, recon_saturation_band_days=[-6, 483])
    led = dict(_PRODUCTION_BOOK, recon_saturation_band_days=[-6, 82])
    door_p, ledger_p = _write_pair(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components=door),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=led))
    measured = pair.measure_published_door_against_the_ledger(
        door_path=door_p, ledger_path=ledger_p, world_atom_id=atom)
    # The old subject, re-derived here rather than imported: the declared tuple.
    old_compared = [n for n in pair._DOOR_LEDGER_COMPONENTS
                    if n in door and n in led]
    old_mismatched = [n for n in old_compared if door[n] != led[n]]
    assert not old_mismatched, (
        "the pre-#37 subject would have caught this divergence, so it is not "
        "the defect Hour #37 measured")
    assert measured["mismatched"], (
        "the widened subject must catch what the declared-only one could not")


def test_a_required_component_missing_from_the_ledger_fires(tmp_path):
    """FAIL-OPEN, on this control's own subject. With the population derived
    from the intersection, dropping a field from one side REMOVES it from the
    comparison -- so erosion would make the control agree more easily. The floor
    turns that into a violation instead."""
    atom = pair.WORLD_ATOM_ID
    led = {k: v for k, v in _PRODUCTION_BOOK.items() if k != "universe_size"}
    measured, violations = _check(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components=_PRODUCTION_BOOK),
        _ledger_payload(atom, gap=_PRODUCTION_GAP, components=led))
    assert "universe_size" not in measured["compared"]
    assert "universe_size" in measured["required_missing"]
    assert any("universe_size" in v and "REQUIRED" in v for v in violations), (
        f"a required component left the comparison silently: {violations!r}")


def test_a_door_field_the_ledger_does_not_carry_is_recorded_not_judged(tmp_path):
    """The queued lead, pinned so it cannot be quietly dropped OR quietly
    promoted into a violation. A field the door publishes and the ledger has no
    record of is unfalsifiable -- there is nothing to reproduce it from -- but
    firing on it needs a ledger schema change outside this atom's file_scope."""
    atom = pair.WORLD_ATOM_ID
    door = dict(_PRODUCTION_BOOK, dimension_caveats={"belief": "..."})
    measured, violations = _check(
        tmp_path,
        _door_payload(atom, value=_PRODUCTION_GAP, components=door),
        _ledger_payload(atom, gap=_PRODUCTION_GAP,
                        components=_PRODUCTION_BOOK))
    assert measured["door_only"] == ("dimension_caveats",)
    assert violations == [], (
        f"door-only fields are RECORDED, not judged, at #37: {violations!r}")


# --------------------------------------------------------------------------- #
# THE ONE READING PREDICATE (atom D33; discharges
# WORKER_FINDING_A_NAN_GAP_DEFEATS_THE_UNDEFINED_READING_GUARD_2026-08-17,
# BLOCKING, lane H_harness)
#
# THE DEFECT, reproduced on the shipped functions at HEAD 95cc1be06 before any
# repair was written. This module answered "are these two counterfactual
# companies ONE company" in EIGHT places as TWO different predicates --
# `_measure_collapse_runs` grouped on `repr()`, the other seven compared raw
# floats -- and they disagreed on both degenerate float values, in OPPOSITE
# directions:
#
#     (0.0, -0.0):  repr() -> DISTINCT      ==  -> COLLAPSED
#     (nan, nan):   repr() -> COLLAPSED     ==  -> DISTINCT, and
#                                                 distinct_from_baseline: True
#
# The NaN row is the fail-open. `undefined_readings` exists to stop "an
# instrument that has stopped reading" being counted as resolution (the D28
# fail-open) and it tested `is None`; NaN is the other value a stopped
# instrument publishes, so it walked through the guard written to catch it.
#
# R15 BOTH WAYS, and the finding named this constraint explicitly: the fixture
# must use BOTH degenerate values, because a NaN-only fixture passes under a
# repair that fixes only `-0.0` and vice versa. Every test below is therefore
# parametrised over both, or asserts on both.
# --------------------------------------------------------------------------- #
_NAN = float("nan")
_DEGENERATE_PAIRS = [
    pytest.param((_NAN, _NAN), id="nan-nan"),
    pytest.param((0.0, -0.0), id="pos-zero-neg-zero"),
]


def _degenerate_row(values, seeds=(7, 11)):
    """A minimal two-point book: drift 0 (baseline) and drift 1, on every seed."""
    by_seed = {s: {"baseline": values[0], "by_drift": {1: values[1]}}
               for s in seeds}
    return by_seed, {"seeds": seeds, "by_seed": by_seed}


@pytest.mark.parametrize("values", _DEGENERATE_PAIRS)
def test_the_two_collapse_derivations_cannot_disagree(values):
    """THE MUTATION THIS EXISTS FOR. Revert either site to its own old predicate
    -- `repr()` in `_measure_collapse_runs`, or raw `==` in `_collapse_state` --
    and one of these two assertions goes red for one of the two values. That is
    the R15 proof: the control fires on its own named defect, and it needs both
    parametrisations to do it."""
    by_seed, row = _degenerate_row(values)
    runs = pair._measure_collapse_runs(by_seed, (0, 1), row["seeds"])
    grouped_as_one = (0, 1) in runs["collapsed_runs"]
    state = pair._collapse_state(row, (0, 1))

    if pair._is_undefined_reading(values[0]):
        # An undefined reading is not a collapse claim in EITHER derivation.
        assert runs["undefined_readings"] == (0, 1), (
            "an absent measurement was not routed to `undefined_readings`")
        assert state is None, (
            f"`_collapse_state` published a resolution claim {state!r} from "
            "readings that are not numbers -- the D28 fail-open")
    else:
        assert state is not None
        assert grouped_as_one == state["collapsed"], (
            f"the two derivations disagree on {values!r}: "
            f"_measure_collapse_runs says collapsed={grouped_as_one}, "
            f"_collapse_state says collapsed={state['collapsed']}")


def test_a_nan_reading_is_undefined_and_never_movement():
    """The finding's headline, pinned directly. Before the repair a NaN drift
    reading was recorded as DISTINCT FROM BASELINE -- resolution manufactured
    out of an absent measurement -- while `undefined_readings` stayed empty."""
    by_seed, row = _degenerate_row((_NAN, _NAN))
    runs = pair._measure_collapse_runs(by_seed, (0, 1), row["seeds"])
    assert runs["undefined_readings"] == (0, 1)
    assert pair._collapse_state(row, (0, 1)) is None

    # ...and the same is true when only the DRIFT reading is NaN, which is the
    # shape a population emptying under one drift actually produces.
    by_seed, row = _degenerate_row((0.25, _NAN))
    runs = pair._measure_collapse_runs(by_seed, (0, 1), row["seeds"])
    assert runs["undefined_readings"] == (1,), (
        "a dimension that stopped reading at one drift was not witnessed")
    assert pair._collapse_state(row, (0, 1)) is None


def test_the_sign_of_a_zero_does_not_mint_a_counterfactual_company():
    """`repr(-0.0) != repr(0.0)`, so the old grouping split ONE company into two
    on a signed zero -- a declared collapse that reads as a real distinction."""
    by_seed, row = _degenerate_row((0.0, -0.0))
    runs = pair._measure_collapse_runs(by_seed, (0, 1), row["seeds"])
    assert (0, 1) in runs["collapsed_runs"], (
        "+0.0 and -0.0 were counted as two counterfactual companies")
    assert runs["undefined_readings"] == (), "a signed zero IS a reading"
    assert pair._collapse_state(row, (0, 1))["collapsed"] is True


@pytest.mark.parametrize("value,undefined", [
    (_NAN, True),
    (float("inf"), True),
    (float("-inf"), True),
    (None, True),
    (0.0, False),
    (-0.0, False),
    (0.25, False),
])
def test_the_undefined_reading_guards_subject_is_every_absent_reading(
        value, undefined):
    """FAIL-OPEN (R15). The guard's subject was `None` alone for nine months.
    Widening it to `None` OR non-finite is the repair; a signed or ordinary zero
    must stay a READING, or the guard would swallow a real measurement and the
    fix would be a fail-CLOSED outage instead."""
    assert pair._is_undefined_reading(value) is undefined


def test_the_predicate_has_exactly_one_implementation():
    """R10 -- the class, not the instance. The finding's own closure condition
    was "one derivation shared by all eight comparison sites", so this asserts
    the SITES, not just the behaviour: a ninth site added tomorrow with a raw
    `==` on a reading is how this defect comes back."""
    src = inspect.getsource(pair)
    # `repr()` as a reading-comparison key is the predicate that drifted.
    assert "repr(reading(" not in src, (
        "`repr()` is back as a reading key -- that is the predicate that "
        "disagreed with `==` on -0.0 and on nan")
    for fn in (pair._measure_collapse_runs, pair._collapse_state):
        body = inspect.getsource(fn)
        assert "_same_reading" in body or "_reading_key" in body, (
            f"{fn.__name__} no longer routes through the shared predicate")
    # Both derivations must consult the SAME undefined-reading definition.
    assert "_is_undefined_reading" in inspect.getsource(pair._measure_collapse_runs)
    assert "_is_undefined_reading" in inspect.getsource(pair._collapse_state)


def test_the_shared_predicate_still_reads_ordinary_numbers_as_before():
    """The guard against a fix that fires on everything. On the readings this
    book actually produces -- finite, non-zero, 7x-17x apart in the reader's own
    step (the 2026-08-17 D33 sweep, 2,264 comparisons) -- the new predicate must
    be exactly the old `==`, or the repair would move declared edges."""
    for left, right in [(0.25, 0.25), (0.25, 0.26), (1.0, 1), (0.0, 0.0),
                        (0.1 + 0.2, 0.3), (-1.5, -1.5), (-1.5, 1.5)]:
        assert pair._same_reading(left, right) is (left == right), (
            f"the shared predicate disagrees with `==` on a defined pair "
            f"({left!r}, {right!r}) -- that is a moved edge, not a repair")


# ---------------------------------------------------------------------------
# THE CENSUS'S `scored_company_*` FIELDS READ THE SCORED COMPANY
# (WORKER_FINDING_THE_SCORED_COMPANY_CLAUSE_IS_BLIND_TO_THE_COMPANY_IT_NAMES,
# leg 1, 2026-08-18)
#
# Three published fields -- `scored_company_window_days`,
# `scored_company_headroom_days`, `scored_company_is_inert` -- were read off
# `DD_FAILURE_WINDOW_DAYS`, a module constant, inside a function whose signature
# never received the consumer. `score_triad` has held that consumer as its
# second positional argument all along. Measured (n=300, seed 7) through the
# DECLARED `organ_failure_window_drift_days` counterfactual, never a
# monkeypatch: the company's memory moved over a 120x range and all three fields
# were bit-identical on every row, while the belief headline moved up to 3.0x.
#
# The caveat those fields render says "the one company parameter these
# dimensions depend on is inert by construction" -- i.e. "you may ignore this
# parameter" -- and it was published byte-identically for a company 42 days
# INSIDE the band. The repo really runs three different companies here: the
# shipped default is 90 (`payment_observation_consumer.py`), the offline fixture
# 400, the live publisher 6000.
# ---------------------------------------------------------------------------

_MEMORY_DRIFTS = (0, -320, -350, +200, +5600)


def test_the_census_reads_the_window_off_the_scored_company_not_the_constant():
    """THE AXIS THE DEFECT WAS INVARIANT ALONG. One book, five companies: the
    three `scored_company_*` fields must MOVE with the company, and only with
    the company."""
    seen = {}
    for drift in _MEMORY_DRIFTS:
        records, consumer, _l, as_of = pair.build_scenario(
            300, seed=7, organ_failure_window_drift_days=drift)
        measured = pair.measure_scenario_constant_census(
            records, as_of, window_days=consumer.dd_failure_window_days)
        seen[drift] = measured
        assert measured["scored_company_window_days"] == (
            pair.DD_FAILURE_WINDOW_DAYS + drift), drift
        assert measured["scored_company_window_source"] == "scored_consumer"
        assert measured["scored_company_headroom_days"] == (
            measured["scored_company_window_days"]
            - measured["measured_oldest_age_days"]), drift

    # NULL CONTROL: the perturbation moved the COMPANY, not the population --
    # so a field that failed to move was blind to its named subject, not
    # correctly reporting an unchanged book.
    oldest = {d: m["measured_oldest_age_days"] for d, m in seen.items()}
    assert len(set(oldest.values())) == 1, oldest
    assert len({m["scored_company_window_days"] for m in seen.values()}) == len(
        _MEMORY_DRIFTS), "the fields are still bit-identical across a 120x sweep"


def test_the_inert_verdict_is_falsifiable_in_both_directions():
    """`is_inert` is a SWITCH, and a switch that only ever reads True is not
    one. Both directions on the same book."""
    inside, _ci, _l, as_of_in = pair.build_scenario(
        300, seed=7, organ_failure_window_drift_days=-320)   # window 80
    cen_in = pair.measure_scenario_constant_census(
        inside, as_of_in, window_days=_ci.dd_failure_window_days)
    assert cen_in["scored_company_is_inert"] is False
    assert cen_in["scored_company_headroom_days"] < 0

    outside, _co, _l2, as_of_out = pair.build_scenario(
        300, seed=7, organ_failure_window_drift_days=+200)   # window 600
    cen_out = pair.measure_scenario_constant_census(
        outside, as_of_out, window_days=_co.dd_failure_window_days)
    assert cen_out["scored_company_is_inert"] is True

    # AND THE PROSE SWITCHES WITH IT. The rendered caveat carried one sentence
    # and no other, so a company inside the band was published as outside it.
    caveat_in = pair.scenario_constant_census_caveat(cen_in)
    caveat_out = pair.scenario_constant_census_caveat(cen_out)
    assert "SITS INSIDE IT" in caveat_in and "SITS OUTSIDE IT" not in caveat_in
    assert "SITS OUTSIDE IT" in caveat_out and "SITS INSIDE IT" not in caveat_out
    assert "MOVE with that parameter" in caveat_in, (
        "the caveat for a company whose memory is doing work on the figure "
        "still says nothing about it")
    assert f"{cen_in['scored_company_window_days']}d of memory" in caveat_in


def test_the_shipped_default_company_is_inside_this_books_band():
    """NOT A HYPOTHETICAL. The consumer's own shipped default is 90 days and
    this book's top is 92 -- so the company the repo ships was being published
    as inert-by-construction with 308 days of headroom it does not have."""
    import inspect as _inspect

    from company.billing.payment_observation_consumer import (
        PaymentObservationConsumer,
    )
    shipped = _inspect.signature(
        PaymentObservationConsumer.__init__
    ).parameters["dd_failure_window_days"].default
    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    measured = pair.measure_scenario_constant_census(
        records, as_of, window_days=shipped)
    assert measured["measured_oldest_age_days"] > shipped, (
        "the premise moved: this book no longer outruns the shipped window")
    assert measured["scored_company_is_inert"] is False
    assert measured["scored_company_headroom_days"] == (
        shipped - measured["measured_oldest_age_days"])


def test_the_live_publishers_company_is_reported_at_its_own_window():
    """The live path constructs at 6000 days and was published at 400 -- 5,600
    days understated, on the only entry with a public reader."""
    from background.live_payment_triad import _RUN_SPANNING_WINDOW_DAYS

    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    measured = pair.measure_scenario_constant_census(
        records, as_of, window_days=_RUN_SPANNING_WINDOW_DAYS)
    assert measured["scored_company_window_days"] == _RUN_SPANNING_WINDOW_DAYS
    assert measured["scored_company_window_days"] != pair.DD_FAILURE_WINDOW_DAYS
    assert measured["scored_company_is_inert"] is True


def test_R15_the_census_goes_green_on_the_constant_with_the_defect_untouched():
    """THE OTHER HALF OF R15. Called WITHOUT a company -- the shape every
    caller had until 2026-08-18 -- the census must still answer, still pass its
    own rules, and must SAY that no company was read. Silence there is what made
    a defaulted 400 indistinguishable from a real 400 on the artefact."""
    records, _c, _l, as_of = pair.build_scenario(300, seed=7)
    defaulted = pair.measure_scenario_constant_census(records, as_of)
    assert defaulted["scored_company_window_days"] == pair.DD_FAILURE_WINDOW_DAYS
    assert defaulted["scored_company_window_source"] == "harness_constant"
    assert pair.check_scenario_constant_census(defaulted) == [], (
        "the repair made the census's own rules fail on the shipped scenario")

    # A REAL 400d company and a DEFAULTED one agree on every number and differ
    # only in the field that says which they are -- so the provenance field is
    # the whole of the distinction, and it is published.
    real = pair.measure_scenario_constant_census(
        records, as_of, window_days=_c.dd_failure_window_days)
    assert _c.dd_failure_window_days == pair.DD_FAILURE_WINDOW_DAYS
    differing = {k for k in real if real[k] != defaulted[k]}
    assert differing == {"scored_company_window_source"}, differing


def test_score_triad_threads_the_scored_company_into_both_predictors():
    """AT THE CALL SITE, on the shipped scorer. Two companies over ONE book:
    the census's window and the belief-resolution caveat must differ, which they
    could not while both predictors defaulted to the module constant."""
    records, consumer, _l, as_of = pair.build_scenario(
        300, seed=7, organ_failure_window_drift_days=-320)
    result = pair.score_triad(records, consumer, as_of)
    bel = result["belief"]
    assert bel.components["scored_company_window_days"] == 80
    assert bel.components["scored_company_is_inert"] is False
    assert result["belief_population_mix"].components[
        "scored_company_window_days"] == 80
    assert "SITS INSIDE IT" in bel.components["scenario_constant_census_caveat"]
    # The memory-resolution predicate is the sibling half of the same call site
    # and was blind in the same way.
    assert bel.components["belief_window_resolution"]["window_days"] == 80

    # THE UNDRIFTED COMPANY over the same seed, so the assertion above is a
    # DIFFERENCE between two companies and not a property of the book.
    base_recs, base_consumer, _bl, base_as_of = pair.build_scenario(300, seed=7)
    baseline = pair.score_triad(base_recs, base_consumer, base_as_of)
    assert baseline["belief"].components["scored_company_window_days"] == 400
    assert baseline["belief"].components["scored_company_is_inert"] is True


# ---------------------------------------------------------------------------
# THE DETECTION DIMENSION'S OWN READING DATE -- atom
# D26_detection_grace_line_has_no_book_beside_it, 2026-08-19
#
# THE ATOM'S OWN NAME IS THE CLAIM THIS SECTION REFUTES, and the id is left
# alone on purpose: it is the live value
# `DIMENSION_DRIFT_RESOLUTION["detection"]["debt_atom"]` points at, and renaming
# it would break the debt pointer the register's mutation suite fires on.
#
# The register said the +1d blindness was the book having nothing beside the
# grace line. Measured: the book sits AGAINST the line and the flagged SET moves
# there; what does not move is the headline, because the exclusion boundary and
# the detector line are keyed on the same quantity. What buys resolution is the
# READING DATE, which is free, and the four traps below are the ones the FRAME
# pass named:
#   * not "the book has cases beside the line" -- it already does, and a test
#     asserting it greens on HEAD;
#   * not "`flagged_size` moves at +1" -- that greens on HEAD too;
#   * not a change to `AS_OF_BUFFER_DAYS` -- that greens this criterion by
#     breaking the ageing atom it depends on;
#   * R15 both ways: the shipped reading date must be REFUSED BY NAME, and a
#     lying predictor must be caught by the sweep's own readings.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def detection_resolution():
    """One book, both readings. Module-scoped: each measurement re-scores the
    triad ~25 times."""
    records, consumer, _l, as_of = pair.build_scenario(300, seed=7)
    return pair.measure_detection_resolution(records, consumer, as_of)


def test_the_reading_date_is_derived_from_the_grace_window_not_chosen(
        detection_resolution):
    """THE FLOOR IS DERIVED (the class this module has now found four times:
    `draw_size_axis`'s 150, the belief axis's 24). The reading date is
    `max(due) + DEFAULT_RECONCILIATION_GRACE_DAYS` -- the earliest date every
    invoice has reached its own line -- and it moves WITH the constant, so it
    is not a literal somebody liked the size of."""
    m = detection_resolution
    assert m["own_reading_buffer_days"] == pair.DEFAULT_RECONCILIATION_GRACE_DAYS
    assert m["shipped_reading_buffer_days"] == pair.AS_OF_BUFFER_DAYS
    records, _c, _l, _a = pair.build_scenario(300, seed=7)
    last_due = max(r.due_date for r in records)
    for grace in (2, 5, 10):
        assert pair.detection_reading_date(records, grace) == (
            last_due + timedelta(days=grace)), grace


def test_the_own_reading_date_resolves_the_error_the_shipped_one_cannot(
        detection_resolution):
    """THE DELIVERABLE, on the shipped book. +2d at the shipped `as_of`, +1d at
    the dimension's own -- and the atom's target is that 1-day terms error."""
    m = detection_resolution
    assert m["shipped_smallest_visible_over_drift"] == 2
    assert m["own_smallest_visible_over_drift"] == 1
    assert m["own_smallest_visible_over_drift"] <= (
        pair.DETECTION_RESOLUTION_CEILING_DAYS)
    assert pair.check_detection_resolution(m) == []


def test_the_reshape_moves_no_published_figure(detection_resolution):
    """R12/R13 IN THE CLEAREST AVAILABLE FORM. Every dimension
    `DIMENSION_AS_OF_CONTRACT` declares as_of-invariant publishes a
    BIT-IDENTICAL figure at both dates -- the resolution improves and the
    numbers do not move. That contract is also what makes a second reading date
    legal at all, so it is re-measured here rather than assumed."""
    m = detection_resolution
    assert set(m["co_read_dimensions_identical"]) == set(
        pair.DETECTION_CO_READ_DIMENSIONS)
    assert all(m["co_read_dimensions_identical"].values())
    assert m["own_detection_gap"] == m["shipped_detection_gap"]
    for dim in pair.DETECTION_CO_READ_DIMENSIONS:
        assert pair.DIMENSION_AS_OF_CONTRACT[dim]["gap_is_as_of_invariant"]


def test_the_ageing_dimension_forbids_the_global_buffer_change(
        detection_resolution):
    """THE EXIT CRITERION GREENABLE BY THE MOVE IT FORBIDS (the D29 shape, one
    atom over). Lowering `AS_OF_BUFFER_DAYS` would green this atom by breaking
    D25's: at the earlier date the whole book sits below the 30-day bucket floor
    and the ageing headline MOVES. So the reshape is a per-dimension reading
    date -- and this movement is the null control that proves the two dates are
    genuinely different."""
    assert detection_resolution["ageing_moves_between_readings"] is True
    assert pair.DIMENSION_AS_OF_CONTRACT["ageing"][
        "gap_is_as_of_invariant"] is False
    records, consumer, _l, as_of = pair.build_scenario(300, seed=7)
    own = pair.detection_reading_date(records)
    shipped = pair.score_triad(records, consumer, as_of)["ageing"].gap
    early = pair.score_triad(records, consumer, own)["ageing"].gap
    assert shipped != early
    assert shipped == pytest.approx(0.11296259117981663)
    assert early == pytest.approx(0.08016507936507936)


def test_the_book_does_sit_beside_the_line_and_the_set_moves_there():
    """THE REFUTATION, MEASURED. The atom's own name says the book has nothing
    beside the grace line. Four invoices sit one day past it on this seed and
    the company's flagged SET moves on exactly them -- while the headline does
    not, because those cases are the ones the headline declines to score. Both
    halves asserted, because either alone is the mistake that produced the
    atom."""
    records, consumer, _l, as_of = pair.build_scenario(300, seed=7)
    assert sum(1 for r in records if r.days_late is not None
               and r.days_late - pair.DEFAULT_RECONCILIATION_GRACE_DAYS == 1) == 4
    base = pair.score_triad(records, consumer, as_of)["detection"]
    drifted = pair.score_triad(records, consumer, as_of,
                               organ_terms_drift_days=1)["detection"]
    assert base.components["flagged_size"] == 331
    assert drifted.components["flagged_size"] == 327
    assert drifted.gap == base.gap, (
        "the SET moves and the HEADLINE does not -- the partition, not the "
        "placement")
    # AND THE PARTITION IS THE REASON: every excluded case is flagged, so the
    # cases a small over-drift can carry across the line are by construction
    # the ones this headline does not count.
    c = base.components
    assert c["caught"] + c["n_false_flags"] + c["n_excluded"] == c["flagged_size"]


def test_the_lower_edge_is_arithmetic_over_the_grace_window():
    """FINDING 3, DIFFERENTIALLY. `-(grace + 1)` is not a property of this book
    -- it is where the company's line falls on `due - 1` and every invoice in
    any book flags. Exercised over grace in {2, 5, 10}: a predictor that only
    ever answers at the shipped window is the D21 tautology in miniature."""
    records, consumer, _l, _a = pair.build_scenario(300, seed=7)
    own = pair.detection_reading_date(records)
    for grace in (2, 5, 10):
        assert pair.predict_detection_saturates_below(grace) == -(grace + 1)
        gaps = {k: pair.score_triad(
            records, consumer, own, reconciliation_grace_days=grace,
            organ_terms_drift_days=k)["detection"].gap
            for k in range(-(grace + 3), 1)}
        edge = -(grace + 1)
        assert len({v for k, v in gaps.items() if k <= edge}) == 1, grace
        assert gaps[edge + 1] != gaps[edge], grace


def test_the_shipped_reading_date_is_refused_by_name(detection_resolution):
    """R15 MUST-FIRE 1, and it is the atom's own premise. If the SHIPPED
    reading ever resolves the 1-day error, the blindness the register declares
    is stale -- a control that goes quiet when its subject changes state is how
    a debt entry outlives its debt."""
    stale = dict(detection_resolution,
                 shipped_smallest_visible_over_drift=1)
    violations = pair.check_detection_resolution(stale)
    assert any("SHIPPED reading date now resolves +1d" in v
               for v in violations), violations


def test_a_reshape_that_costs_resolution_fires(detection_resolution):
    """R15 MUST-FIRE 2. The own reading date resolving WORSE than the shipped
    one is the opposite of the atom, and a control that only checks the
    ceiling would pass it whenever the shipped book happened to be worse
    still."""
    worse = dict(detection_resolution,
                 own_smallest_visible_over_drift=2,
                 shipped_smallest_visible_over_drift=1)
    violations = pair.check_detection_resolution(worse)
    assert any("costs resolution on this book" in v for v in violations)
    ceiling = dict(detection_resolution, own_smallest_visible_over_drift=3)
    assert any("worse than the 2d ceiling" in v
               for v in pair.check_detection_resolution(ceiling))


def test_a_lying_lower_edge_predictor_is_caught_by_the_sweep(
        detection_resolution):
    """R15 MUST-FIRE 3, the INDEPENDENCE leg. The closed form and the re-scored
    edge are two computations of one quantity; the control must fire when they
    disagree, in either direction, rather than believing the declaration."""
    for patch in ({"saturates_below_predicted": -7},
                  {"saturates_below_measured": -9}):
        violations = pair.check_detection_resolution(
            dict(detection_resolution, **patch))
        assert any("closed form over `reconciliation_grace_days` predicts" in v
                   for v in violations), patch


def test_a_second_reading_publishing_a_different_number_fires(
        detection_resolution):
    """R15 MUST-FIRE 4. A dimension declared as_of-invariant whose figure moves
    between the two dates means the second reading is publishing a DIFFERENT
    number, not the same number better resolved -- the whole licence for a
    per-dimension reading date."""
    moved = dict(detection_resolution,
                 co_read_dimensions_identical=dict(
                     detection_resolution["co_read_dimensions_identical"],
                     belief=False))
    violations = pair.check_detection_resolution(moved)
    assert any("`belief` is DECLARED as_of-invariant" in v
               for v in violations), violations


def test_the_two_dates_being_one_date_fires(detection_resolution):
    """R15 MUST-FIRE 5, THE NULL CONTROL, and it is the one that stops every
    identity above being a number compared with itself. If the ageing figure
    does not move between the two dates they are not distinguishable, and the
    bit-identity result is vacuous."""
    same = dict(detection_resolution, ageing_moves_between_readings=False)
    violations = pair.check_detection_resolution(same)
    assert any("not distinguishable on the one dimension" in v
               for v in violations), violations


def test_an_empty_book_fails_closed(detection_resolution):
    """R15's THIRD SHAPE. A book with no true failures, or no reading date, has
    no resolution to certify -- a resolution claim over an empty population is
    vacuous, and a silent pass here is exactly how one fail-opens."""
    for patch in ({"n_true_failures": 0}, {"own_as_of": None}):
        violations = pair.check_detection_resolution(
            dict(detection_resolution, **patch))
        assert any("vacuous, not satisfied" in v for v in violations), patch
    assert pair.detection_reading_date([]) is None


def test_the_register_entry_carries_the_reshape_and_the_caveat_publishes_it():
    """STAMPED AT SOURCE (D22): the ledger writer, the live wiring and the
    dashboard read `components`, so a limit only a docstring carries is one the
    machine strips off. And the sentence is INTERPOLATED -- move the register
    and it moves."""
    e = pair.DIMENSION_DRIFT_RESOLUTION["detection"]
    assert e["own_reading_buffer_days_closed_form"] == (
        "DEFAULT_RECONCILIATION_GRACE_DAYS")
    assert e["own_smallest_visible_over_drift_band"] == (1, 2)
    assert e["shipped_smallest_visible_over_drift_band"] == (2, 8)
    assert e["saturates_below_closed_form"] == (
        "-(DEFAULT_RECONCILIATION_GRACE_DAYS + 1)")
    assert e["saturation_atom_below"] == "BOUND:the flag-everything set"
    assert e["saturates_above_scope"]["is_the_seed_intersection"] is True
    assert e["debt_atom"] == "D26_detection_grace_line_has_no_book_beside_it"
    caveat = pair.detection_resolution_caveat()
    assert "+2..+8d at the SHIPPED `as_of` and +1..+2d" in caveat
    assert "BELOW is ARITHMETIC over the grace window" in caveat
    # THE REFUTED SENTENCES MUST NOT COME BACK.
    assert "BOTH EDGES ARE THE BOOK'S OWN END" not in caveat
    assert "the book sits nowhere near the grace line" not in e["why"]


def test_the_new_control_is_reachable_from_the_run_that_publishes():
    """A CONTROL NOBODY RUNS IS NOT ONE, and this module's own check-call census
    caught this build trying to ship one. `check_detection_resolution` re-scores
    the triad ~25 times, which is a full drift grid of its own -- so it is
    declared in `CHECKS_BEHIND_A_FLAG` with that reason and called from `main()`
    inside its flag's branch, the same shape as the two sweeps beside it."""
    assert "check_detection_resolution" in pair.CHECKS_BEHIND_A_FLAG
    entry = pair.CHECKS_BEHIND_A_FLAG["check_detection_resolution"]
    assert entry["flag"] == "detection_reading_date"
    assert "~25" in entry["reason"]
    census = pair.measure_check_call_census()
    assert "check_detection_resolution" not in census["uncalled"]
    assert census["behind_a_flag"]["check_detection_resolution"] == (
        "detection_reading_date",)
    assert pair.check_check_call_census(census) == []


def test_an_undeclared_reshape_is_published_as_undeclared_not_as_a_small_one():
    """R15's THIRD SHAPE, on the sentence. An entry that drops the reshape
    fields must SAY the reading date is undeclared -- silently falling back to
    quoting the shipped band as a property of the instrument is exactly the
    decay this atom corrected."""
    entry = pair.DIMENSION_DRIFT_RESOLUTION["detection"]
    saved = dict(entry)
    try:
        for k in ("own_smallest_visible_over_drift_band",
                  "shipped_smallest_visible_over_drift_band",
                  "own_reading_buffer_days_closed_form"):
            entry.pop(k, None)
        caveat = pair.detection_resolution_caveat()
        assert "WHICH READING DATE this band belongs to is NOT DECLARED" in caveat
        assert "at the SHIPPED `as_of`" not in caveat
    finally:
        entry.clear()
        entry.update(saved)


def test_the_structural_flag_names_its_provenance_per_edge():
    """ONE FLAG WAS COVERING TWO PROVENANCES. `structural` means "follows from
    the scenario calendar" and only the +1 EDGE does -- the band behind it is
    the D8 mis-allocation draw, varying +2..+8 over the same seeds the edge
    holds on 10/10."""
    e = pair.DIMENSION_DRIFT_RESOLUTION["detection"]
    scope = e["structural_scope"]
    assert "calendar" in scope["+1_edge"]
    assert "DRAW" in scope["band_behind_it"]
    assert e["own_reading_scope"]["seeds"] == (7, 11, 23, 1, 2, 3, 5, 13, 29, 31)


def test_the_calendar_term_is_published_as_a_term_not_as_the_answer(
        detection_resolution):
    """THE HONEST RESIDUAL, and the FRAME pass's identity corrected on a wider
    population. `min(as_of - due : failed) - grace + 1` is exact on the three
    RESOLUTION_SEEDS and is NOT a predictor: over ten seeds it over-predicts on
    two (the D8 mis-allocation channel resolves finer) and under-predicts on
    one (the boundary case was DD-observed, and the DD channel is drift-inert
    by D10). The measurement publishes both numbers rather than one dressed as
    a prediction."""
    m = detection_resolution
    assert m["calendar_term_days"] == 1
    assert m["shipped_calendar_term_days"] == 26
    assert m["own_smallest_visible_over_drift"] == m["calendar_term_days"]
    # THE COUNTEREXAMPLE, on a book outside the three declared seeds: the
    # calendar says +3 and the reading resolves +1.
    records, consumer, _l, as_of = pair.build_scenario(300, seed=5)
    other = pair.measure_detection_resolution(records, consumer, as_of)
    assert other["calendar_term_days"] == 3
    assert other["own_smallest_visible_over_drift"] == 1
    assert pair.check_detection_resolution(other) == [], (
        "the control must not fire on a book where the calendar term is loose "
        "-- it reports the disagreement, it does not believe either number")


# ---------------------------------------------------------------------------
# ATOM D27 -- THE ORIGIN IS THE ORGAN'S, AND A SHADOWED DEFAULT OWES A COST
# ---------------------------------------------------------------------------
# `DD_FAILURE_WINDOW_DAYS` is not one scenario constant among five: it is the
# ORIGIN both belief dimensions' bands are stated in (`drift == 0` IS this
# value), and it shadows a default the company organ chose for itself. It has
# carried a sound design NOTE and no measurement of what the choice costs for
# its whole life, which is the atom.
#
# The stubs below are AST subjects, never executed: `scenario_organ_default_
# shadows` reads a function's source, so a stub is how the derived rule is put
# on trial against a call shape this scenario does not currently contain.


def _stub_call_shadowing_an_organ_default():
    """Passes a module constant to a company parameter that HAS a default."""
    window = DD_FAILURE_WINDOW_DAYS + 1
    return PaymentObservationConsumer(dd_failure_window_days=window)


def _stub_call_into_a_required_parameter():
    """The NULL CONTROL: same file, same call shape, REQUIRED parameter -- so
    there is no organ default behind it to diverge from."""
    return LedgerEvent(amount_gbp=BILL_AMOUNT_GBP)


def test_the_memory_origin_is_read_off_the_organ_and_fails_closed():
    """CRITERION 2 (D27 FRAME). The organ's own default is DERIVED from its
    signature, and every way of not being able to read it RAISES rather than
    falling back to a literal -- the fallback IS the D20 hand-copy this exists
    to refuse, and it would keep the harness green while the two sides
    diverged."""
    assert pair.organ_default_failure_window_days() == 90
    assert (pair.organ_default_failure_window_days()
            == inspect.signature(PaymentObservationConsumer.__init__)
            .parameters["dd_failure_window_days"].default)

    class _Moved:
        def __init__(self, dd_failure_window_days=137):
            pass

    class _NoParam:
        def __init__(self, ledger_book=None):
            pass

    class _NoDefault:
        def __init__(self, dd_failure_window_days):
            pass

    class _BoolDefault:
        def __init__(self, dd_failure_window_days=True):
            pass

    # THE MUTATION THE FRAME NAMES: move the organ's default. A hand-typed 90
    # would sail past this; the derivation follows it.
    with mock.patch.object(pair, "PaymentObservationConsumer", _Moved):
        assert pair.organ_default_failure_window_days() == 137
    # ...and the three unreadable organs, each of which a literal fallback
    # would have swallowed.
    for stub in (_NoParam, _NoDefault, _BoolDefault):
        with mock.patch.object(pair, "PaymentObservationConsumer", stub):
            with pytest.raises(RuntimeError):
                pair.organ_default_failure_window_days()


def test_the_shadow_finder_is_derived_and_discriminates():
    """R10: the rule finds the NEXT shadowed organ default, not the one this
    atom tripped over. Derived from `build_scenario`'s AST -- and the null
    control is one line away in the same function, so the rule has to tell a
    defaulted parameter from a required one rather than answering `yes` to
    every module constant handed to a company class."""
    shadows = pair.scenario_organ_default_shadows()
    assert shadows == {
        "DD_FAILURE_WINDOW_DAYS": ("PaymentObservationConsumer",
                                   "dd_failure_window_days")}
    # BILL_AMOUNT_GBP is handed to `LedgerEvent(amount_gbp=...)` in the very
    # same function and is NOT a shadow: that parameter is required.
    assert "BILL_AMOUNT_GBP" not in shadows

    # THE TWO CALL SHAPES, ON THEIR OWN. A rule that returned both, or
    # neither, could not discriminate -- and this is where that fails.
    assert pair.scenario_organ_default_shadows(
        _stub_call_shadowing_an_organ_default) == {
        "DD_FAILURE_WINDOW_DAYS": ("PaymentObservationConsumer",
                                   "dd_failure_window_days")}
    assert pair.scenario_organ_default_shadows(
        _stub_call_into_a_required_parameter) == {}


def test_a_shadowed_organ_default_owes_a_measured_divergence():
    """THE CLASS RULE, failing in BOTH directions (R10/R15).

    A constant that shadows an organ default and records no measured
    divergence is atom D27 itself -- a design note standing in for a
    measurement. A `measured_divergence` on a constant that shadows nothing is
    a field sprinkled to buy a pass, which is how a rule like this one stops
    discriminating."""
    records, _consumer, _ledger, as_of = pair.build_scenario(300, seed=7)
    measured = pair.measure_scored_window_provenance(records, as_of)
    assert measured["organ_default_window_days"] == 90
    assert measured["harness_window_days"] == pair.DD_FAILURE_WINDOW_DAYS
    assert measured["divergence_days"] == 310
    assert measured["origin_is_organ_default"] is False
    assert pair.check_scored_window_provenance(measured) == []

    def _census():
        return copy.deepcopy(pair.SCENARIO_CONSTANT_CENSUS)

    # MUTATION 1 -- the shadow declares no cost at all.
    c = _census()
    del c["DD_FAILURE_WINDOW_DAYS"]["measured_divergence"]
    assert any("records no `measured_divergence`" in v
               for v in pair.check_scored_window_provenance(measured, c))

    # MUTATION 2 -- the declared divergence drifts from the organ.
    c = _census()
    c["DD_FAILURE_WINDOW_DAYS"]["measured_divergence"]["divergence_days"] = 311
    assert any("re-derive it" in v
               for v in pair.check_scored_window_provenance(measured, c))

    # MUTATION 3 -- how far, without what it costs. The distance is not the
    # atom; the price of the distance is.
    c = _census()
    del c["DD_FAILURE_WINDOW_DAYS"]["measured_divergence"]["cost"]
    assert any("and no `cost`" in v
               for v in pair.check_scored_window_provenance(measured, c))

    # MUTATION 4 -- a cost with no date or subject reads as live when it is a
    # measurement too expensive to re-derive per run.
    for field in ("measured", "at_head", "how"):
        c = _census()
        del c["DD_FAILURE_WINDOW_DAYS"]["measured_divergence"]["cost"][field]
        assert any(f"omits `{field}`" in v
                   for v in pair.check_scored_window_provenance(measured, c))

    # MUTATION 5 -- THE UNDISCRIMINATING DIRECTION. Sprinkle the field on a
    # constant with no organ behind it.
    c = _census()
    c["BILL_AMOUNT_GBP"]["measured_divergence"] = c[
        "DD_FAILURE_WINDOW_DAYS"]["measured_divergence"]
    assert any("no company constructor default" in v
               for v in pair.check_scored_window_provenance(measured, c))

    # MUTATION 6 -- a shadow declaration outliving its call site.
    c = _census()
    c["FIRST_DUE_DATE"]["shadows_organ_default"] = ("PaymentObservationConsumer",
                                                    "dd_failure_window_days")
    assert any("outliving its call site" in v
               for v in pair.check_scored_window_provenance(measured, c))


def test_never_forgets_drift_is_derived_from_the_book_and_is_zero_today():
    """THE FINDING, IN THE COORDINATE THE RESHAPE WILL MOVE (atom D27).

    `never_forgets_drift_days` is 0 on the shipped origin: the SCORED company
    already never forgets, so the published figure cannot distinguish it from a
    supplier that keeps a recovered customer in collections for ever. It is
    derived from the BOOK -- the oldest observed failure -- and never from the
    number 400, which is what makes it move when the origin does."""
    records, _consumer, _ledger, as_of = pair.build_scenario(300, seed=7)
    assert pair.never_forgets_drift_days(records, as_of) == 0
    assert pair.measure_belief_window_resolution(records, as_of)["saturated"]

    # THE MUTATION: at the organ's OWN default the same book yields a non-zero
    # drift, so the function is reading the book against the window and not
    # returning a constant. Seed 7's oldest observed failure is 91d old.
    assert pair.never_forgets_drift_days(records, as_of, window_days=90) == 1
    assert pair.never_forgets_drift_days(records, as_of, window_days=1) == 90

    # ...and a book with no observed failure bounds nothing, so it gets None
    # rather than 0. Reporting "already saturated" about a book that presents
    # no event is the fail-open one field over (R15).
    clean = [r for r in records if r.result != "failed"]
    assert pair.never_forgets_drift_days(clean, as_of) is None


def test_todays_published_figure_is_the_never_forgets_companys_figure(
        monkeypatch):
    """THE EQUALITY THAT STATES THE ATOM, as a control rather than a table.

    At the organ's own default the NEVER-FORGETS company -- reached by the
    book-derived drift, with the number 400 appearing nowhere -- publishes
    exactly what this pair publishes TODAY, on all five dimensions. D27's
    complaint is usually written as a caveat ("this figure cannot distinguish
    the scored company from one that never forgets"); this is the same claim
    stated as an equality, which is falsifiable and a caveat is not."""
    dims = ("ageing", "belief", "belief_population_mix", "detection",
            "detection_latency")

    def _score(window, drift=0):
        monkeypatch.setattr(pair, "DD_FAILURE_WINDOW_DAYS", window)
        recs, cons, _l, as_of = pair.build_scenario(
            300, seed=7, organ_failure_window_drift_days=drift)
        return {d: pair.score_triad(recs, cons, as_of)[d].gap for d in dims}, recs, as_of

    today, _r, _a = _score(400)
    _b, recs90, as_of90 = _score(90)
    nf_drift = pair.never_forgets_drift_days(recs90, as_of90, window_days=90)
    assert nf_drift == 1
    never_forgets, _r2, _a2 = _score(90, drift=nf_drift)
    assert never_forgets == today, (
        "today's published figures ARE the never-forgets company's figures")

    # THE MUTATION: one day short of never forgetting is a DIFFERENT company,
    # and the two belief dimensions are where it shows -- so the equality above
    # is a measurement and not an artefact of re-scoring the same book.
    one_short, _r3, _a3 = _score(90, drift=nf_drift - 1)
    assert one_short["belief"] != today["belief"]
    # R13 DIFFERENTIAL: the memory knob reaches the belief organ and nothing
    # else, so the other three dimensions do not move even here.
    for d in ("ageing", "detection", "detection_latency"):
        assert one_short[d] == today[d], d
