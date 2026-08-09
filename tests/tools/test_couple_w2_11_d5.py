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
import inspect
import copy
import dataclasses
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import tools.couple_w2_11_d5 as pair

from background.gap_metric import (
    ageing_gap,
    belief_gap,
    detection_gap,
    detection_measures,
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
    return {
        "detection": frozenset((r.customer_id, r.period_index) for r in failed),
        "detection_latency": frozenset(
            (r.customer_id, r.period_index, r.due_date) for r in failed),
        "belief": tuple(sorted(
            (cid, sum(1 for r in failed if r.customer_id == cid))
            for cid in {r.customer_id for r in records})),
        "ageing": tuple(sorted(
            (r.invoice_ref,
             pair.company_age_bucket((as_of - r.due_date).days)
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

    assert set(contract) == {"detection", "detection_latency", "belief", "ageing"}, (
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
    return {
        "detection": format_detection_summary(result["detection"]),
        "ageing": pair.format_ageing_summary(result["ageing"]),
        "detection_latency": pair.format_detection_latency_summary(
            result["detection_latency"]),
        "belief": str(result["belief"].note or ""),
    }


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
