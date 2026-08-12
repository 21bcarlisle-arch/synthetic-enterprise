"""AO12 — the 10k scale probe's own controls, and the mutation proofs that they can FAIL.

R15 is the reason this file is long. The probe's whole output is a claim about where the
system tears; a probe whose guards cannot fire would manufacture a confident scale claim out
of a run that measured nothing. Each guard below is therefore tested in BOTH directions: the
shipped code holds, and a named mutation of it breaks the assertion.

The three killer patterns R15 names, and where each is answered here:
  TAUTOLOGY   — the prediction register is graded against measurements it never sees, and
                `test_grader_refuses_a_register_written_after_the_run` proves the ordering
                requirement is real rather than decorative.
  FAIL-OPEN   — `test_unmeasured_stage_is_unknown_not_zero` and its mutation twin: the exact
                shape where a stage that never ran sorts harmlessly to the bottom.
  FAIL-SILENT — `test_checkpoints_survive_a_sigkill` runs a REAL child and REALLY kills it;
                an unflushed checkpointer passes every in-process test and loses precisely the
                runs the probe exists to measure.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

from tools import scale_probe_10k as probe  # noqa: E402

# ═════════════════════════════════════════════════════════════════════════════════════════════
# FAIL-CLOSED: an unmeasured stage costs an UNKNOWN amount, never zero
# ═════════════════════════════════════════════════════════════════════════════════════════════

def _measurement(stage: str, **kw) -> probe.StageMeasurement:
    base = dict(stage=stage, status=probe.STATUS_MEASURED, unit="record", units_completed=100,
                wall_s=1.0, peak_rss_bytes=200_000_000, baseline_rss_bytes=100_000_000)
    base.update(kw)
    return probe.StageMeasurement(**base)


BUDGETS = {"rss_bytes": 8e9, "wall_s": 300.0}


def test_unmeasured_stage_is_unknown_not_zero():
    """A stage that never ran must not be priced — the fail-open shape R15 names."""
    never_ran = _measurement("settlement_build", status=probe.STATUS_NOT_REACHED,
                             units_completed=0, peak_rss_bytes=None, baseline_rss_bytes=None)
    probe.project_stage(never_ran, target_units=1_000_000)
    pressure = probe.stage_pressure(never_ran, BUDGETS)

    assert pressure.kind == probe.KIND_UNKNOWN
    assert pressure.value is None, "an unrun stage must carry no value at all, not 0.0"
    assert pressure.hi == float("inf"), "an unknown cost has no upper bound"


def test_mutation_pricing_an_unmeasured_stage_at_zero_changes_the_verdict():
    """THE MUTATION. Price the unknown at zero and the ranking silently decides — proving the
    three-valued algebra is load-bearing rather than ceremony."""
    unknown = probe.Pressure("settlement_build", None, probe.KIND_UNKNOWN, "never ran")
    measured = probe.Pressure("site_publish", 0.5, probe.KIND_MEASURED, "")

    assert probe.compare_pressure(unknown, measured) == "undecided"

    mutant = probe.Pressure("settlement_build", 0.0, probe.KIND_MEASURED, "priced at zero")
    assert probe.compare_pressure(mutant, measured) == "lt", (
        "the mutation must actually flip the comparison — if it did not, the shipped "
        "three-valued handling would be untested decoration")


def test_a_ceiling_death_is_a_lower_bound_not_an_unknown():
    """It died holding something. That something is evidence, and it is a FLOOR."""
    died = _measurement("settlement_build", status=probe.STATUS_CEILING_DEATH,
                        units_completed=50_000, peak_rss_bytes=3_000_000_000,
                        baseline_rss_bytes=400_000_000)
    probe.project_stage(died, target_units=175_200_000)
    pressure = probe.stage_pressure(died, BUDGETS)

    assert pressure.kind == probe.KIND_LOWER_BOUND
    assert pressure.hi == float("inf")
    assert pressure.lo > 1.0, "3GB over 50k records extrapolated to 175M must exceed an 8GB box"


def test_a_lower_bound_can_still_decide_a_comparison():
    """Fail-closed must not collapse into never-deciding — that would be the always-red
    detector, as ignored as a blind one."""
    huge_floor = probe.Pressure("settlement_build", 20.0, probe.KIND_LOWER_BOUND, "")
    small = probe.Pressure("git_transport", 0.01, probe.KIND_MEASURED, "")
    assert probe.compare_pressure(huge_floor, small) == "gt"


def test_zero_per_unit_cost_degrades_to_a_lower_bound():
    """A per-unit cost of exactly 0 is the instrument's floor, not a finding.

    Regression pin for the N=20 rehearsal: 3,600 settlement records grew the resident set by
    0 bytes because a 129MB price-cache parse had already been paid. Certifying that as
    MEASURED would let a deliberately cheap probe underwrite a scale claim it cannot support.
    """
    flat = _measurement("settlement_build", peak_rss_bytes=100_000_000,
                        baseline_rss_bytes=100_000_000)
    probe.project_stage(flat, target_units=1_000_000)

    assert "rss_bytes" in flat.below_resolution
    assert probe.stage_pressure(flat, BUDGETS).kind == probe.KIND_LOWER_BOUND


def test_per_unit_cost_excludes_the_interpreter_and_input_baseline():
    """Without the baseline subtraction every stage's per-unit cost carries ~40MB of
    interpreter plus its inputs, and the probe 'finds' a tear that is its own floor."""
    m = _measurement("settlement_build", units_completed=1000,
                     baseline_rss_bytes=400_000_000, peak_rss_bytes=500_000_000)
    probe.project_stage(m, target_units=1000)

    assert m.per_unit["rss_bytes"] == pytest.approx(100_000)
    assert m.projection["rss_bytes"] == pytest.approx(500_000_000), (
        "the projection is baseline + growth, so at target == measured size it must "
        "reproduce the observed peak")


def test_projection_is_extrapolated_from_completed_units_only():
    m = _measurement("settlement_build", units_completed=1000,
                     baseline_rss_bytes=100_000_000, peak_rss_bytes=200_000_000)
    probe.project_stage(m, target_units=10_000)
    assert m.projection["rss_bytes"] == pytest.approx(100_000_000 + 100_000 * 10_000)


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE PREDICTION REGISTER MUST PREDATE THE RUN
# ═════════════════════════════════════════════════════════════════════════════════════════════

def _pressures(**kv) -> dict[str, probe.Pressure]:
    return {k: probe.Pressure(k, v, probe.KIND_MEASURED, "") for k, v in kv.items()}


def test_grader_refuses_a_register_written_after_the_run():
    graded = probe.grade_prediction(
        _pressures(settlement_build=9.0, run_output_serialization=1.0),
        ["settlement_build", "run_output_serialization"],
        register_written_at=2000.0, first_stage_started_at=1000.0)

    assert graded["verdict"] == "UNGRADED"
    assert "AFTER" in graded["reason"]
    assert graded["pairs"] == [], "an ungraded run must not publish pair verdicts"


def test_grader_grades_a_register_written_before_the_run():
    graded = probe.grade_prediction(
        _pressures(settlement_build=9.0, run_output_serialization=1.0),
        ["settlement_build", "run_output_serialization"],
        register_written_at=1000.0, first_stage_started_at=2000.0)
    assert graded["verdict"] == "CONFIRMED"


def test_a_surprise_ordering_is_reported_as_refuted():
    """The probe must be able to say the advisor was wrong — a grader that can only agree is
    an outcome-free organ."""
    graded = probe.grade_prediction(
        _pressures(settlement_build=0.1, run_output_serialization=9.0),
        ["settlement_build", "run_output_serialization"],
        register_written_at=1.0, first_stage_started_at=2.0)
    assert graded["verdict"] == "REFUTED"


def test_an_undecided_pair_can_never_reach_confirmed():
    graded = probe.grade_prediction(
        {"settlement_build": probe.Pressure("settlement_build", None, probe.KIND_UNKNOWN, ""),
         "run_output_serialization": probe.Pressure("run_output_serialization", 1.0,
                                                    probe.KIND_MEASURED, "")},
        ["settlement_build", "run_output_serialization"],
        register_written_at=1.0, first_stage_started_at=2.0)
    assert graded["verdict"] == "PARTIAL"
    assert graded["pairs"][0]["result"] == "UNDECIDED"


def test_an_undecided_pair_states_what_would_flip_it():
    """Fail-closed must still be decision-useful. An undecided pair reports the multiple by
    which the omitted component would have to exceed the measured one to change the answer."""
    graded = probe.grade_prediction(
        {"settlement_build": probe.Pressure("settlement_build", 6.0, probe.KIND_MEASURED, ""),
         "site_publish": probe.Pressure("site_publish", 0.002, probe.KIND_LOWER_BOUND, "")},
        ["settlement_build", "site_publish"],
        register_written_at=1.0, first_stage_started_at=2.0)

    pair = graded["pairs"][0]
    assert pair["result"] == "UNDECIDED"
    assert pair["flip_requires_factor"] == pytest.approx(3000.0)


def test_a_decided_pair_carries_no_flip_factor():
    graded = probe.grade_prediction(
        _pressures(settlement_build=6.0, site_publish=0.002),
        ["settlement_build", "site_publish"],
        register_written_at=1.0, first_stage_started_at=2.0)
    assert graded["pairs"][0]["result"] == "CONFIRMED"
    assert "flip_requires_factor" not in graded["pairs"][0]


def test_register_records_the_advisor_order_and_a_timestamp(tmp_path):
    path = tmp_path / "register.json"
    register = probe.write_prediction_register(path, predicted_order=probe.ADVISOR_PREDICTED_ORDER,
                                               run_id="test", source="unit test")
    on_disk = json.loads(path.read_text())
    assert on_disk["predicted_order"] == list(probe.ADVISOR_PREDICTED_ORDER)
    assert on_disk["written_at"] == register["written_at"]
    assert on_disk["predicted_order"][0] == "settlement_build"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE SUBJECT IS NOT CHANGED BY THE INSTRUMENT
# ═════════════════════════════════════════════════════════════════════════════════════════════

def test_chunking_does_not_change_the_subject():
    """settlement_build drives the real `run_settlement` in customer chunks so a killed stage
    still reports where it got to. That only measures the real thing if chunked output equals
    whole output — asserted here against the shipped function, not assumed from reading it."""
    from simulation.settlement import run_settlement

    customers = [{"customer_id": f"P{i}", "acquisition_date": "2021-01-01",
                  "unit_rate_gbp_per_mwh": 140.0} for i in range(9)]
    prices = [{"settlementDate": "2021-01-01", "settlementPeriod": p, "systemSellPrice": 50.0}
              for p in range(1, 49)]
    shape = lambda _d: [0.25] * 48  # noqa: E731

    whole = run_settlement(customers, "2021-01-01", "2021-01-01", shape, prices)
    chunked = []
    for start in range(0, len(customers), 4):
        chunked.extend(run_settlement(customers[start:start + 4], "2021-01-01", "2021-01-01",
                                      shape, prices))

    assert whole == chunked, "chunking must be exact, or the probe measures a different subject"
    assert len(whole) == 9 * 48


def test_the_generator_saturates_above_745():
    """PINS THE DEFECT THIS PROBE FOUND, so the workaround has a falsifier.

    `simulation.population_draw._poisson` is Knuth's algorithm; its target is
    `math.exp(-lam)`, which underflows to exactly 0.0 above lambda ~745. With an unreachable
    target the loop exits only when the running product of uniforms denormalises to zero,
    after ~700 multiplications REGARDLESS of lambda — so every request above the saturation
    point returns roughly the same meaningless count, silently.

    THIS TEST DOES NOT ENDORSE THE BEHAVIOUR. It records it, so that when the owning lane fixes
    the generator this test fails and `_draw_book`'s batching is revisited rather than left
    behind as cargo. The finding is filed at
    docs/staging/WORKER_FINDING_THE_POPULATION_DRAW_SATURATES_ABOVE_LAMBDA_745_2026-08-12.md.
    """
    import random

    from simulation.population_draw import _poisson

    rng = random.Random(1)
    small = _poisson(rng, 20.0)
    assert 5 < small < 50, "at a lambda it can honour the draw is a real Poisson draw"

    huge = _poisson(rng, 10_000.0)
    assert huge < 2_000, (
        f"lambda=10000 returned {huge}: if this now returns ~10000 the generator has been "
        "fixed and tools/scale_probe_10k._draw_book should stop batching around it")

    import math
    assert math.exp(-probe._POISSON_SATURATION_LAMBDA) > 0
    assert math.exp(-(probe._POISSON_SATURATION_LAMBDA + 5)) == 0.0, (
        "the constant must sit at the real underflow boundary, not near it")


def test_the_probe_refuses_a_book_it_did_not_get(monkeypatch):
    """The saturation's danger is SILENCE. Whatever the generator does, the probe must never
    report per-customer costs against an N it never had — a short book with the requested N in
    the denominator understates every per-customer cost, in the reassuring direction."""
    monkeypatch.setattr("simulation.population_draw.iter_acquisition_events",
                        lambda *a, **k: iter(()))
    with pytest.raises(RuntimeError, match="refuses to measure a book it did not get"):
        probe._draw_book(5_000, base_seed=1, year=2021)


def test_batched_draw_yields_unique_ids():
    """The generator numbers from 1 within each year, so un-prefixed batches would collide and
    silently shrink the book — the same defect one layer up."""
    book = probe._draw_book(600, base_seed=20260812, year=2021)
    assert len(book) == 600
    assert len({c["customer_id"] for c in book}) == 600


def test_target_units_uses_the_measured_records_per_customer_not_the_arithmetic():
    """days*48 is the arithmetic this probe exists to retire — periods are skipped where no
    price record exists, and DST days carry 46 or 50. The target must come from the
    measurement wherever one exists."""
    args = probe.build_arg_parser().parse_args(["--customers", "10000", "--days", "365"])
    settlement = _measurement("settlement_build", units_completed=1_000_000)
    settlement.extra["records_per_customer"] = 17_000.0

    with_measurement = probe._target_units("run_output_serialization", args, [settlement])
    without = probe._target_units("run_output_serialization", args, [])

    assert with_measurement == 10_000 * 17_000
    assert without == 10_000 * 365 * 48, "with no measurement it falls back and says so"
    assert with_measurement != without


# ═════════════════════════════════════════════════════════════════════════════════════════════
# FAIL-SILENT: the death must reach the disk. A real child, really killed.
# ═════════════════════════════════════════════════════════════════════════════════════════════

def test_checkpoints_survive_a_sigkill(tmp_path):
    """Launch the real child protocol, SIGKILL it mid-stage, and require the checkpoints to be
    on disk anyway.

    This is the probe's central claim — 'it succeeds even if the run dies, provided it dies
    measurably' — and it is not provable in-process: a checkpointer that writes without
    flushing passes every mock-based test and loses the buffer with the process. The mutation
    that breaks this test is removing the `flush()`/`fsync()` pair in `_Checkpointer.write`.
    """
    scratch = tmp_path / "stage"
    scratch.mkdir()
    # settlement_build is the right subject: it checkpoints per customer chunk while holding a
    # growing in-memory working set, and writes no bulk output — so the test proves the
    # death-reporting path without putting a gigabyte of replica documents on the disk.
    argv = [sys.executable, "-m", "tools.scale_probe_10k", "--run-stage", "settlement_build",
            "--scratch", str(scratch), "--shared", str(tmp_path),
            "--customers", "400", "--days", "365", "--chunk-customers", "2",
            "--as-ceiling-mb", "0"]
    proc = subprocess.Popen(argv, cwd=str(PROJECT), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    checkpoints = scratch / probe.CHECKPOINTS_FILENAME
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        if checkpoints.exists() and checkpoints.read_text().strip():
            break
        time.sleep(0.5)
    os.killpg(os.getpgid(proc.pid), 9)
    proc.wait(timeout=60)

    lines = [ln for ln in checkpoints.read_text().splitlines() if ln.strip()]
    assert lines, "a SIGKILLed stage left NO record of how far it got — fail-silent"
    last = json.loads(lines[-1])
    assert last["customers"] > 0 and last["records"] > 0 and last["rss_bytes"] > 0
    assert not (scratch / probe.STAGE_RESULT_FILENAME).exists(), (
        "a SIGKILLed child cannot have written its own self-report — if it did, this test is "
        "not exercising the death path it claims to")


def test_a_ceiling_death_is_recorded_as_one(tmp_path):
    """Give a stage an address-space ceiling it cannot meet and require the probe to name the
    cause. A stage that died must never be reported as `measured`."""
    scratch = tmp_path / "stage"
    argv = [sys.executable, "-m", "tools.scale_probe_10k", "--run-stage", "population_draw",
            "--scratch", str(scratch), "--shared", str(tmp_path),
            "--customers", "2000000", "--as-ceiling-mb", "256"]
    subprocess.run(argv, cwd=str(PROJECT), capture_output=True, timeout=600)

    result = json.loads((scratch / probe.STAGE_RESULT_FILENAME).read_text())
    assert result["outcome"] == probe.STATUS_CEILING_DEATH, (
        "a stage given an address-space ceiling it cannot meet must be reported as having "
        "died at it — reporting `measured` would publish a partial book as a whole one")
    assert "MemoryError" in result["detail"]
    assert result["checkpoints"] > 0, "it must have said how far it got before it died"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# SCRATCH ONLY — the probe never touches canonical state
# ═════════════════════════════════════════════════════════════════════════════════════════════

def test_every_write_target_is_scratch_or_the_declared_artefact():
    """The atom's bound: 'scratch outputs only (canonical files untouched)'.

    Asserted structurally — the only in-repo paths the module writes are the two declared
    artefacts under docs/observability/scale_probe_10k/, and everything else is under the
    scratch root, which is outside the repo entirely.
    """
    assert probe.REPORT_PATH.parent == probe.ARTEFACT_DIR
    assert probe.PREDICTION_REGISTER_PATH.parent == probe.ARTEFACT_DIR
    assert probe.ARTEFACT_DIR.is_relative_to(PROJECT / "docs" / "observability")
    assert not probe.DEFAULT_SCRATCH_ROOT.is_relative_to(PROJECT), (
        "scratch inside the repo would be swept into another lane's commit by the "
        "auto-processor on this shared tree")
    assert "/tmp" not in str(probe.DEFAULT_SCRATCH_ROOT), (
        "/tmp is a tmpfs on this box — publishing 10k files there would consume the RAM the "
        "probe is measuring and report disk numbers that are not disk numbers")


def test_report_names_the_ceiling_in_the_unit_it_is_actually_in():
    """The AS ceiling bounds virtual address space. A report that called it an RSS limit would
    be the sized-in-one-unit / applied-in-another defect, and this figure feeds a downstream
    affordability verdict."""
    args = probe.build_arg_parser().parse_args([])
    report = probe.build_report(run_id="t", args=args, measurements=[], budgets=BUDGETS,
                               register={"predicted_order": [], "written_at": 1.0},
                               first_stage_started_at=2.0, scratch=Path("/nonexistent"))
    assert "ADDRESS SPACE" in report["limits"]["as_ceiling_unit"]
    assert "not RSS" in report["limits"]["as_ceiling_unit"]


def test_report_lists_every_unrun_stage_as_unmeasured():
    """The consumer atom fails CLOSED on an unmeasured stage, which it can only do if the
    report tells it which stages those are."""
    args = probe.build_arg_parser().parse_args([])
    measured = _measurement("population_draw", unit="customer")
    probe.project_stage(measured, target_units=10_000)
    report = probe.build_report(run_id="t", args=args, measurements=[measured], budgets=BUDGETS,
                               register={"predicted_order": [], "written_at": 1.0},
                               first_stage_started_at=2.0, scratch=Path("/nonexistent"))

    unmeasured_stages = {u["stage"] for u in report["unmeasured"]}
    assert unmeasured_stages == set(probe.STAGES) - {"population_draw"}
    assert "never priced at zero" in report["reading_note"]


def test_budgets_come_from_the_box_not_a_constant():
    """MemAvailable, not MemTotal: what a run can actually have is what is free beside the
    daemons already living here."""
    budgets = probe.measure_budgets(300.0)
    assert budgets["wall_s"] == 300.0
    assert budgets["rss_bytes"] > 0
    meminfo = Path("/proc/meminfo").read_text()
    available = next(int(ln.split()[1]) * 1024 for ln in meminfo.splitlines()
                     if ln.startswith("MemAvailable:"))
    total = next(int(ln.split()[1]) * 1024 for ln in meminfo.splitlines()
                 if ln.startswith("MemTotal:"))
    assert budgets["rss_bytes"] != total, "MemTotal would flatter every pressure ratio"
    assert abs(budgets["rss_bytes"] - available) / available < 0.5


def test_a_stage_with_an_unmeasured_component_can_never_come_back_measured():
    """Whatever a stage did not measure can only ADD, so a partial measurement is a FLOOR.

    Pins the defect the 10k run exposed: git_transport packed 10,000 replica documents into
    1.42MB — 1,300x compression, because the replica replays 22 real documents. Read as a
    MEASURED figure it would have REFUTED the advisor's publish-over-transport ordering on a
    number biased low by three orders of magnitude.
    """
    partial = _measurement("git_transport", unit="file",
                           unmeasured=["replica redundancy biases the pack size LOW"])
    probe.project_stage(partial, target_units=10_000)
    pressure = probe.stage_pressure(partial, BUDGETS)

    assert pressure.kind == probe.KIND_LOWER_BOUND
    assert pressure.hi == float("inf")
    assert "unbounded above" in pressure.basis

    complete = _measurement("git_transport", unit="file")
    probe.project_stage(complete, target_units=10_000)
    assert probe.stage_pressure(complete, BUDGETS).kind == probe.KIND_MEASURED, (
        "the mutation twin: with nothing declared unmeasured the same stage certifies as "
        "MEASURED, so the unmeasured list is what is doing the work here")


def test_affordability_cannot_be_talked_into_a_yes():
    """DOES_NOT_FIT on the floor alone, and never FITS while anything is unmeasured."""
    over = probe.Pressure("settlement_build", 4.62, probe.KIND_LOWER_BOUND, "")
    under = probe.Pressure("population_draw", 0.002, probe.KIND_MEASURED, "")
    partial = probe.Pressure("site_publish", 0.002, probe.KIND_LOWER_BOUND, "")
    nothing = probe.Pressure("git_transport", None, probe.KIND_UNKNOWN, "")

    assert probe.affordability(over) == "DOES_NOT_FIT"
    assert probe.affordability(under) == "FITS"
    assert probe.affordability(partial) == "UNDECIDED", (
        "a cheap-looking stage with an unmeasured component must not be certified as fitting")
    assert probe.affordability(nothing) == "UNKNOWN"


def test_a_missing_budget_is_unknown_not_free():
    m = _measurement("settlement_build")
    probe.project_stage(m, target_units=1000)
    assert probe.stage_pressure(m, {}).kind == probe.KIND_UNKNOWN


# ═════════════════════════════════════════════════════════════════════════════════════════════
# REPLICA STAGES MUST DECLARE THEMSELVES, AND MUST NOT INVENT THEIR SUBJECT
# ═════════════════════════════════════════════════════════════════════════════════════════════

def test_git_transport_refuses_to_invent_files(tmp_path):
    """A consuming stage with nothing to consume must fail loudly. Inventing files would
    report a transport cost for a publish that never happened."""
    args = probe.build_arg_parser().parse_args(
        ["--run-stage", "git_transport", "--scratch", str(tmp_path / "s"),
         "--shared", str(tmp_path)])
    cp = probe._Checkpointer(tmp_path / "cp.jsonl")
    try:
        with pytest.raises(RuntimeError, match="UNKNOWN, not zero"):
            probe._stage_git_transport(args, cp)
    finally:
        cp.close()


def test_site_publish_refuses_to_invent_a_document_shape(tmp_path, monkeypatch):
    monkeypatch.setattr(probe, "REAL_CUSTOMER_DOCS_DIR", tmp_path / "empty")
    (tmp_path / "empty").mkdir()
    args = probe.build_arg_parser().parse_args(
        ["--run-stage", "site_publish", "--scratch", str(tmp_path / "s"),
         "--shared", str(tmp_path), "--customers", "5"])
    cp = probe._Checkpointer(tmp_path / "cp.jsonl")
    try:
        with pytest.raises(RuntimeError, match="refuses to invent"):
            probe._stage_site_publish(args, cp)
    finally:
        cp.close()


def test_settlement_refuses_synthetic_prices(monkeypatch):
    """Historical Ground Truth: no cached SSP means no measurement, not a substituted one."""
    monkeypatch.setattr("sim.cache_store.get_cached_prices", lambda *a, **k: None)
    with pytest.raises(RuntimeError, match="refuses to substitute synthetic prices"):
        probe._real_prices("2021-01-01", "2021-01-02")


def test_every_stage_declares_a_binding_resource():
    """A stage with no binding resource would silently get an UNKNOWN pressure forever — a
    control that never fires because it was never wired, not because nothing is wrong."""
    assert set(probe.BINDING_RESOURCE) == set(probe.STAGES)
    assert set(probe.ADVISOR_PREDICTED_ORDER) <= set(probe.STAGES)


def test_stage_funcs_cover_every_declared_stage():
    assert set(probe.STAGE_FUNCS) == set(probe.STAGES)
