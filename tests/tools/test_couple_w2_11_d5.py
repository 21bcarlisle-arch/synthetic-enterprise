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

import tools.couple_w2_11_d5 as pair

from background.gap_metric import belief_gap, detection_gap, misapplication_gap, write_gap_entry
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from interface.contracts.wall_envelope import WallResponse
from simulation.payment_behaviour_source import PaymentEvent

# Small-but-real population: enough for both DD and non-DD failures to occur
# reliably (see test_non_dd_failures_occur_and_are_never_flagged) while
# keeping the suite fast.
_N = 900
_SEED = 101


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


def test_detection_latency_is_registered_not_zero():
    """Ruling §1: the residual is a detection LATENCY, registered with its
    measured distribution, never compressed to zero. Every reconciliation
    detection carries a positive latency (days from due date to observation),
    and the population summary exposes the distribution."""
    result = pair.measure(_N, seed=_SEED)
    lat = result["stats"]["detection_latency_days"]
    assert lat["n"] > 0
    assert lat["min_days"] is not None and lat["min_days"] >= 5  # >= grace window
    assert lat["max_days"] >= lat["median_days"] >= lat["min_days"]


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
