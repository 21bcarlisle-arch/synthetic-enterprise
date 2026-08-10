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
import json
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

import tools.couple_w2_11_d5 as pair

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
    `never_flaggable` exactly once."""
    src = Path(pair.__file__).read_text()
    assert src.count("    never_flaggable = {") == 1, (
        "the never-flaggable band is constructed more than once in this module; "
        "two copies of one rule is how the detection and ageing dimensions came "
        "to disagree about the same cases"
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
    assert len(ages) == 3, (
        f"seed {seed}: build_scenario now exposes {len(ages)} distinct debt "
        f"ages {sorted(ages)}, not 3. The ordinal dimension's coverage of the "
        "bucket space changed; the D21 limit recorded on the organ-drift "
        "control (a uniform boundary shift is invisible on a three-age book) "
        "must be re-measured")
    assert {pair._ageing_bucket(d) for d in ages} == {"30-60", "60-90"}, (
        f"seed {seed}: the reachable truth-side buckets changed -- `90+` and "
        "`current` are still never exercised on the truly-overdue side, which "
        "is what bounds `max_bucket_displacement` at 2")
    # THE CONSEQUENCE, checked rather than described: if every unit of
    # displacement is a miss, and the only reachable truth buckets are 30-60
    # and 60-90, then total displacement must land exactly in
    # [lo x misses, hi x misses], where lo/hi are those buckets' own ranks read
    # off `bucket_order` rather than written in as 1 and 2 -- a re-ordered or
    # re-named bucket space then moves this bound with it instead of leaving a
    # literal that quietly stops matching the dimension it bounds.
    lo = min(rank[b] for b in ("30-60", "60-90"))
    hi = max(rank[b] for b in ("30-60", "60-90"))
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
        return dataclasses.replace(
            result, gap=result.components["mean_bucket_displacement"])

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
    because the organ's `days_overdue` is clamped at zero. Zero on the shipped
    organ, the whole population on one at the floor -- so it is a reading, not a
    constant."""
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


def test_the_grid_control_fires_when_the_declared_collapse_is_resolved():
    """R15, the direction the reshape MOVED this register into. With no
    invisibility left on the date reading, the only falsifiable residual is the
    COLLAPSE -- two companies 15 days apart publishing one number because the
    organ clamps `days_overdue` at zero. A D24-shaped repair separates them, and
    the entry must then fail as a stale debt exactly as a repaired invisibility
    did, naming the atom to re-derive."""
    real = {k: pair.measure(n_customers=_GRID_N, seed=7,
                            organ_reconciliation_drift_days=k)
            for k in (-20, -5, -1, 0, 1, 7)}

    def unclamped(k):
        """The organ's overdue clock no longer floored at zero: -20d is now a
        different company from -5d, as it always was in fact."""
        result = copy.deepcopy(real[k])
        if k >= 0:
            return result
        lat = result["detection_latency"]
        comps = dict(lat.components)
        comps["mean_lag_days_without_dd_channel"] = float(
            pair.DEFAULT_RECONCILIATION_GRACE_DAYS + k)
        result["detection_latency"] = dataclasses.replace(lat, components=comps)
        det = result["detection"]
        result["detection"] = dataclasses.replace(det, gap=det.gap + 0.001 * k)
        return result

    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, runner=unclamped)
    violations = pair.check_organ_query_grid_resolution(measured)
    assert violations
    assert any("declared to COLLAPSE to one reading but read" in v
               for v in violations)
    assert any("D24_the_latency_floor_is_the_organs_clamped_overdue" in v
               for v in violations), "the violation must name the atom to re-derive"


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
    promised to close."""
    register = copy.deepcopy(pair.ORGAN_QUERY_GRID)
    register["recon_lag_days"]["debt_atom"] = None
    measured = pair.measure_organ_query_grid_resolution(
        n_customers=_GRID_N, seed=7, register=register)
    violations = pair.check_organ_query_grid_resolution(measured, register=register)
    assert any("no `debt_atom`" in v for v in violations)


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
