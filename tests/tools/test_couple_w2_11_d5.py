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
import json

import pytest

import tools.couple_w2_11_d5 as pair

from background.gap_metric import (
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
    import dataclasses

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
    """R15 independence: the per-cell gap is the SAME `detection_gap` scorer
    applied to just that cell's cases -- prove it by reconstructing one cell's
    gap by hand and asserting equality (the partition adds no bespoke metric,
    it only routes cases to the right cell)."""
    records, consumer, _ledger, as_of = pair.build_scenario(_N, seed=_SEED)
    per_cell = pair.score_detection_by_partition(
        records, consumer, as_of, _regime_of_period
    )

    # Manually rebuild G1's truth/flagged sets exactly as the function should.
    by_customer = {}
    for r in records:
        by_customer.setdefault(r.customer_id, []).append(r)
    manual_truth, manual_flagged = set(), set()
    for cid, periods in by_customer.items():
        snap = consumer.snapshot(periods[0].account_id, as_of=as_of,
                                 payment_terms_days=pair.PAYMENT_TERMS_DAYS)
        due_to_period = {r.due_date: r.period_index for r in periods}
        rec_by_period = {r.period_index: r for r in periods}
        for r in periods:
            if r.result == "failed" and _regime_of_period(r) == "G1":
                manual_truth.add((cid, r.period_index))
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
    expected = detection_gap(manual_truth, manual_flagged)
    assert per_cell["G1"].gap == expected.gap


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
    # Every other registered entry is still on the recall-only scorer.
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
    # here proves only that one shape exists.
    assert any(v["counts_both_error_directions"] for v in contract.values())
    assert any(not v["counts_both_error_directions"] for v in contract.values())

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

    # The lie: a recall-only entry declaring itself two-directional.
    key = "score_detection_by_partition"
    assert pair.DETECTION_DIRECTION_CONTRACT[key][
        "counts_both_error_directions"] is False
    degenerate = _flag_everything_score(key, records, consumer, as_of)
    assert degenerate == 0.0, "the cell scorer stopped being recall-only"
    with pytest.raises(AssertionError):
        assert degenerate != 0.0, "declared two-directional but scores a degenerate 0"
