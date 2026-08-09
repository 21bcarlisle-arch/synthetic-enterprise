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


# ---------------------------------------------------------------------------
# ATOM D8 -- the ambiguous-remittance counterfactual.
#
# The finding: unreferenced non-DD credits cross the seam with no invoice
# reference, so allocation falls back oldest-first (Clayton's Case) and the
# company's MONEY stays exactly right while its DATES do not. These tests hold
# the attribution to the standard of a control that can fail (R15): a
# counterfactual is the easiest thing in this repo to make un-failable, because
# subtracting a company from itself always yields a tidy zero and subtracting a
# DIFFERENT WORLD always yields an impressive number.
# ---------------------------------------------------------------------------

def test_d8_the_money_is_right_and_the_dates_are_not():
    """The finding, as two numbers on the same population."""
    attr = _build_triad().measure()["remittance_attribution"]

    assert attr["n_ambiguous_credits"] > 0, (
        "no ambiguous credit landed -- the channel this atom is about was never "
        "exercised, so everything below would be vacuous"
    )
    assert attr["vacuity"] is None and attr["premise_violated"] is None

    # THE MONEY. Not approximately: to the penny, both ways.
    assert attr["balance_gbp_delta"] == 0.0
    assert attr["balance_gbp_actual"] == attr["balance_gbp_remittance_complete"]

    # THE DATES. The channel is the whole of the debt-date displacement on this
    # population -- with remittance restored the company dates every overdue
    # invoice exactly right.
    disp = attr["measures"]["ageing.mean_bucket_displacement"]
    assert disp["actual"] > 0.0
    assert disp["remittance_complete"] == 0.0
    assert disp["attributed"] == disp["actual"]


def test_d8_the_counterfactual_discriminates_rather_than_charging_everything():
    """A counterfactual that explained 100% of every measure would be a rubber
    stamp. This one must leave a residual somewhere, because there IS a residual:
    a truly-current invoice can also be believed overdue simply because the cash
    has not arrived yet (detection LATENCY), which no remittance reference fixes."""
    attr = _build_triad().measure()["remittance_attribution"]
    over = attr["measures"]["ageing.overstated_arrears_rate"]

    assert over["attributed"] > 0.0, "the channel contributes nothing at all -- re-derive"
    assert over["remittance_complete"] > 0.0, (
        "the counterfactual charges the ENTIRE wrongful-dunning exposure to the "
        "remittance channel. Payment latency alone overstates arrears and no "
        "invoice reference cures it, so a zero here means the shadow company is "
        "not the same world"
    )
    assert over["attributed"] < over["actual"]


def test_d8_wrongful_non_pursuit_is_measured_where_the_headline_cannot_see_it():
    """D10 widened this atom: the same seam defect makes a REAL arrears case
    vanish from the company's arrears view. D11 then made the detection headline
    EVER-FLAGGED -- correctly, a detection is a fact about the day it happened --
    which leaves that headline structurally blind to the company later UN-knowing
    it. This asserts both halves: the headline cannot see it, and the atom's own
    measure can."""
    attr = _build_triad().measure()["remittance_attribution"]

    headline = attr["measures"]["detection.missed_failure_rate"]
    assert headline["attributed"] == 0.0, (
        "the ever-flagged detection headline moved under the remittance "
        "counterfactual -- if that is real, this test's premise (and D11's) needs "
        "re-deriving; until then it is the reason the measure below has to exist"
    )

    unpursued = attr["measures"]["arrears_view.unpursued_arrears_rate"]
    counts = attr["unpursued_counts"]["actual"]
    assert counts["n_ever_detected"] > 0, "vacuous: nothing was ever detected"
    assert counts["n_unpursued"] > 0, (
        "no detected arrears case was lost again -- the mechanism D10 observed "
        "case by case no longer reproduces"
    )
    assert unpursued["remittance_complete"] == 0.0, (
        "restoring the remittance reference must eliminate wrongful non-pursuit "
        "entirely: oldest-first fallback is the only thing that moves a credit "
        "onto a failed invoice here"
    )
    assert unpursued["attributed"] == unpursued["actual"] > 0.0


def test_d8_counterfactual_differs_from_the_actual_in_the_REFERENCE_ONLY():
    """The load-bearing premise: the shadow company lives in the SAME world.

    Asserted at the seam itself, field by field, rather than trusted. If the
    second emission moved a clearing date or an ARUDD lag draw, every attributed
    figure above would be charging the remittance channel for a different world."""
    import dataclasses

    from simulation.payment_behaviour_source import generate_payment_event
    from simulation.payment_seam_adapter import SeamAdapterInput, emit_wall_responses

    n_compared = 0
    for i in range(60):
        cid = f"RESI{i:05d}"
        for p in range(3):
            due = date(2020, p + 1, 28)
            event = generate_payment_event(
                cid, p, due, 120.0, "high", "standing_order", segment="resi")
            actual = emit_wall_responses(event, SeamAdapterInput(
                account_id=f"ACC-{cid}", correlation_id=f"{cid}::p{p}::ambiguous"))
            shadow = emit_wall_responses(event, SeamAdapterInput(
                account_id=f"ACC-{cid}", correlation_id=f"{cid}::{p}"))
            assert len(actual) == len(shadow)
            for a, s in zip(actual, shadow):
                assert a.observed_at == s.observed_at, "the counterfactual moved a REPORT date"
                assert a.valid_time == s.valid_time, "the counterfactual moved a VALUE date"
                assert a.status == s.status
                if a.payload is None:
                    assert s.payload is None
                    continue
                a_fields = dataclasses.asdict(a.payload)
                s_fields = dataclasses.asdict(s.payload)
                differing = {k for k in a_fields if a_fields[k] != s_fields[k]}
                assert differing <= {"bank_reference"}, (
                    f"the counterfactual changed {differing - {'bank_reference'}} "
                    "-- it may only change which invoice the cash says it pays"
                )
                n_compared += 1
    assert n_compared > 0, "vacuous: no payload was ever compared"


def test_R15_MUTANT_a_counterfactual_identical_to_the_actual_measures_nothing(monkeypatch):
    """MUTATION: make the shadow company carry the SAME ambiguous reference --
    i.e. no counterfactual at all. Every attributed figure must collapse to
    exactly 0.0, and the assertions in the tests above must therefore fail.

    This is the named defect the whole construct can die of: a counterfactual
    that quietly stopped differing would publish 'the remittance channel costs
    nothing' with total confidence and never fire."""
    baseline = _build_triad().measure()["remittance_attribution"]
    assert baseline["measures"]["ageing.mean_bucket_displacement"]["attributed"] > 0.0

    monkeypatch.setattr(
        lpt, "_counterfactual_correlation_id",
        lambda invoice_ref, actual_correlation_id: actual_correlation_id,
    )
    mutated = _build_triad().measure()["remittance_attribution"]

    # The population is untouched -- only the shadow's reference changed.
    assert mutated["n_ambiguous_credits"] == baseline["n_ambiguous_credits"] > 0
    for name, m in mutated["measures"].items():
        assert m["attributed"] == 0.0, (
            f"{name} still attributes {m['attributed']} to a channel the "
            "counterfactual no longer removes"
        )
        assert m["actual"] == m["remittance_complete"], name


def test_R15_MUTANT_a_shadow_fed_a_different_population_RAISES():
    """MUTATION: the 'counterfactual' is scored over a different world.

    The subtraction would then attribute the difference between two populations
    to the remittance channel -- the most flattering possible error, and one no
    reader of the published figure could detect. It must raise, not degrade: there
    is no honest partial answer from two different worlds."""
    triad = _build_triad()
    actual = triad.measure()
    shadow = _build_triad().measure()
    shadow["stats"]["n_true_failures"] = actual["stats"]["n_true_failures"] + 1

    with pytest.raises(ValueError, match="SAME WORLD"):
        lpt.attribute_to_ambiguous_remittance(
            actual, shadow,
            n_ambiguous_records=10, n_ambiguous_credits=5,
            actual_balance_gbp=100.0, counterfactual_balance_gbp=100.0,
        )


def test_R15_MUTANT_a_moved_balance_blanks_every_figure():
    """MUTATION: the shadow portfolio's balance differs.

    Re-allocating cash can never create or destroy any, so a non-zero delta means
    the counterfactual changed something other than attributability -- and the
    finding's own premise ('the balance is exactly right') is then false on this
    population. Fail CLOSED: publish nothing, say why. Not fail-loud: this runs
    inside a live run_phase2b and a diagnostic may not kill the run it measures."""
    triad = _build_triad()
    actual = triad.measure()
    shadow = _build_triad().measure()

    blanked = lpt.attribute_to_ambiguous_remittance(
        actual, shadow,
        n_ambiguous_records=264, n_ambiguous_credits=160,
        actual_balance_gbp=56160.0, counterfactual_balance_gbp=56159.99,
    )
    assert blanked["premise_violated"] and "THE MONEY MOVED" in blanked["premise_violated"]
    assert all(m["attributed"] is None for m in blanked["measures"].values())
    assert "NOT PUBLISHED" in lpt.format_remittance_attribution_summary(blanked)


def test_R15_MUTANT_an_unexercised_channel_reports_undefined_not_zero(monkeypatch):
    """MUTATION: an all-Direct-Debit population. Every credit already carries its
    invoice reference, so the shadow company IS the company and every delta is
    trivially 0.0. Publishing 0.0 would claim the channel was measured and found
    harmless. It must say undefined instead (the D7 vacuity rule)."""
    monkeypatch.setattr(lpt, "generate_payment_method", lambda cid, fuel=None: "direct_debit")
    attr = _build_triad().measure()["remittance_attribution"]

    assert attr["n_ambiguous_credits"] == 0
    assert attr["vacuity"] and "not a channel that costs nothing" in attr["vacuity"]
    assert all(m["attributed"] is None for m in attr["measures"].values())
    assert "UNDEFINED" in lpt.format_remittance_attribution_summary(attr)


def test_d8_attribution_is_published_as_structure_and_as_a_sentence(tmp_path):
    """R11-shaped: the finding is only reported if it reaches the surface a
    reader sees. It travels twice -- in `components` (which survives a caller
    replacing `note`, the D6 lesson) and interpolated into the note itself."""
    triad = _build_triad()
    ledger = tmp_path / "coupled_gap_ledger.json"
    result = triad.measure_and_write(run_git_commit="0" * 40, ledger_path=ledger)

    entry = result["detection"].components["remittance_attribution"]
    assert entry["measures"]["ageing.mean_bucket_displacement"]["attributed"] > 0.0

    note = result["detection"].note
    assert "AMBIGUOUS-REMITTANCE ATTRIBUTION (D8" in note
    disp = entry["measures"]["ageing.mean_bucket_displacement"]["attributed"]
    assert f"{disp:+.4f} buckets attributable" in note, (
        "the published sentence is not interpolated from the measurement -- a "
        "typed-in number outlives the figure it describes"
    )

    import json
    written = json.loads(ledger.read_text())
    assert "AMBIGUOUS-REMITTANCE ATTRIBUTION" in json.dumps(written), (
        "the attribution did not reach the ledger the Proof door reads"
    )
