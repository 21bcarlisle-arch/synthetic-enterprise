#!/usr/bin/env python3
"""AO12 — the 10k scale probe. Find the FIRST seam that tears, with a number on it.

WHY THIS EXISTS
---------------
`docs/design/refs/ADVISOR_REVIEW_DATA_ARCHITECTURE_AND_SCALE_PROBE_2026-08-05.md` §2 answered
the director's "do we scale to 10k / 100k / 1m?" with ARITHMETIC — ~200KB of run output per
customer per decade, therefore ~2GB of JSON at 10k, therefore probably dead. Its own §5 says
the honest thing about that: *"Runtime memory behaviour is entirely unmeasured — every RAM
claim above is arithmetic, not observation."* This tool replaces the arithmetic with a
measurement, and the extrapolation argument with a number.

KNOWLEDGE IS THE SUCCESS CRITERION. The probe succeeds even if the run dies, PROVIDED IT DIES
MEASURABLY — which is a design requirement on this file, not a hope. Every stage runs in its
own child process, under an address-space ceiling and a wall-clock cap, checkpointing its
progress to disk after every chunk with an explicit flush+fsync. A stage that is killed
therefore still leaves behind how many units it completed, how much memory it was holding, and
how long it took to get there — which is the whole measurement. See `_run_stage_child`.

EXPLICITLY NOT IN SCOPE (the atom's own words, kept here because scope creep on a MEASUREMENT
is how a measurement becomes an advocacy exercise): any fix, any database or substrate
adoption, any schema work. Measure first (R4). A storage swap is an architecture door, not a
build; probe findings return to the director before any substrate decision.

WHAT IT MEASURES — five stages, mapped to the advisor's four ranked predictions
------------------------------------------------------------------------------
  population_draw            the book itself         [not predicted — the control stage]
  settlement_build           predicted #1: in-run RAM at settlement build
  run_output_serialization   predicted #2: run-output serialization
  site_publish               predicted #3: per-customer site publish
  git_transport              predicted #4: git transport of outputs

The PREDICTION REGISTER is written BEFORE any stage runs (`write_prediction_register`) and the
report grades the OBSERVED ordering against it. `grade_prediction` REFUSES to grade a register
stamped after the first stage started — a prediction written after the fact is not a
prediction, and a probe that would grade one is a control that cannot fail (R15). A SURPRISE
ORDERING IS THE MOST VALUABLE OUTCOME; nothing here is tuned to make the advisor right.

THE SUBJECTS ARE REAL WHERE THEY CAN BE, AND SAID TO BE REPLICAS WHERE THEY CANNOT
---------------------------------------------------------------------------------
Stages 1-3 drive the SHIPPED code over REAL inputs: `simulation.population_draw`, the real
`simulation.settlement.run_settlement`, the real Profile Class 1 shape from
`sim/data/profile_class_1_gad.csv`, and the real cached Elexon SSP settlement prices from
`sim/cache/elexon_ssp_full.json`. Nothing about those three stages is synthetic except the
size of the book, which is the independent variable.

Stages 4-5 are REPLICAS and are labelled as such in the report (`subject_kind`). A real 10k
site publish would need a 10k-customer run OUTPUT to publish, and stage 2 is expected to prove
that output cannot be built on this box — so the publish stage cannot be fed by the real
producer, and pretending otherwise would be the "hand-typed call list supplies the defect"
shape. What it does instead is replay the byte-shapes of the 22 REAL `site/data/customers/
*.json` documents on disk N times into a scratch directory, and commit them to a scratch git
repo. That measures the FILESYSTEM and TRANSPORT cost of the publish shape at N. It does NOT
measure the cost of COMPUTING 10k customers' worth of content, and the report records that
omission as an explicitly UNMEASURED cost rather than leaving the reader to assume it is zero.

FAIL-CLOSED ON AN UNMEASURED STAGE (R15, and the dependent atom depends on it)
-----------------------------------------------------------------------------
A stage the probe never reached costs an UNKNOWN amount, never zero. `stage_pressure` returns
a three-valued interval — MEASURED [v,v], LOWER_BOUND [v,inf), UNKNOWN [0,inf) — and
`compare_pressure` returns "undecided" whenever the intervals overlap. The consequence is that
an unmeasured stage can never be silently ranked LAST, which is precisely how a fail-open
scale claim ("we never saw it tear, so it doesn't") would be manufactured. A stage killed at
its ceiling is a LOWER_BOUND, not an unknown: it demonstrably needed at least what it was
holding when it died.

SAFETY ON A SHARED BOX
----------------------
This box runs live daemons and a live publisher on ~15.9G with a 4G swap. A stage told to
build 175 million settlement records would drive the whole machine into swap and let the
kernel OOM-killer choose the victim — quite possibly the publisher, not the probe. Every child
therefore runs under an explicit `RLIMIT_AS` ceiling (`--as-ceiling-mb`, default 3072), which
makes the child raise MemoryError at a ceiling WE chose instead of the kernel choosing a
victim at a ceiling the box chose.

Say what that ceiling is in the unit it is actually in: RLIMIT_AS bounds VIRTUAL ADDRESS
SPACE. Peak RSS is what the report projects from, it is measured separately and exactly
(`os.wait4`'s `ru_maxrss`, which survives SIGKILL), and it is always <= the AS ceiling but is
not equal to it. Calling the AS limit an "RSS limit" would be the sized-from-a-process /
applied-to-a-cgroup error one register over; it is not made here.

Scratch output lives OUTSIDE the repo, under `~/.cache/synthetic-enterprise/scale_probe/` on
real disk — deliberately NOT `/tmp`, which is a tmpfs on this box: publishing 10k files to a
RAM-backed filesystem would both consume the RAM the probe is trying to measure and report
publish/transport numbers that have nothing to do with disk. The report records the scratch
filesystem type so a reader can tell which was measured. Canonical files are never touched.

USAGE
    python3 -m tools.scale_probe_10k                    # full probe, defaults, writes report
    python3 -m tools.scale_probe_10k --customers 100    # a cheap end-to-end rehearsal
    python3 -m tools.scale_probe_10k --stages settlement_build
    python3 -m tools.scale_probe_10k --run-stage NAME --scratch DIR ...   # the child protocol
"""
from __future__ import annotations

import argparse
import json
import math
import os
import resource
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

# ── Artefact paths ───────────────────────────────────────────────────────────────────────────
# The report is the atom's DELIVERABLE — `SCALE_10K_PROPOSED_TARGET` (maturity map) reads its
# per-stage cost from this file and is forbidden from re-deriving it. The path is therefore
# part of the contract, not an implementation detail.
ARTEFACT_DIR = PROJECT / "docs" / "observability" / "scale_probe_10k"
REPORT_PATH = ARTEFACT_DIR / "report.json"
PREDICTION_REGISTER_PATH = ARTEFACT_DIR / "prediction_register.json"

# Scratch root: real disk, outside the repo, outside /tmp (see module docstring).
DEFAULT_SCRATCH_ROOT = Path.home() / ".cache" / "synthetic-enterprise" / "scale_probe"

# The real per-customer publish documents whose byte-shapes stage 4 replays.
REAL_CUSTOMER_DOCS_DIR = PROJECT / "site" / "data" / "customers"

STAGES: tuple[str, ...] = (
    "population_draw",
    "settlement_build",
    "run_output_serialization",
    "site_publish",
    "git_transport",
)

# The advisor's ranked guesses, §3 of the review, in the review's own order. This constant is
# the PREDICTION; it is written to the register before the run and graded after. It is not a
# default the measurement can drift toward — nothing downstream reads it except the grader.
ADVISOR_PREDICTED_ORDER: tuple[str, ...] = (
    "settlement_build",
    "run_output_serialization",
    "site_publish",
    "git_transport",
)

# Each stage's BINDING resource: the one whose exhaustion is what "tearing" means for it. The
# pressure ratio is projected-requirement / budget IN THAT RESOURCE, which is what makes the
# five stages comparable at all (they are otherwise in bytes, seconds and inodes).
BINDING_RESOURCE: dict[str, str] = {
    "population_draw": "rss_bytes",
    "settlement_build": "rss_bytes",
    "run_output_serialization": "rss_bytes",
    "site_publish": "wall_s",
    "git_transport": "wall_s",
}

# Status values a stage measurement can carry. `not_reached` and `error` are the two that must
# never be priced at zero.
STATUS_MEASURED = "measured"
STATUS_CEILING_DEATH = "ceiling_death"
STATUS_TIMEOUT = "timeout"
STATUS_ERROR = "error"
STATUS_NOT_REACHED = "not_reached"

# Pressure interval kinds.
KIND_MEASURED = "measured"
KIND_LOWER_BOUND = "lower_bound"
KIND_UNKNOWN = "unknown"

CHECKPOINTS_FILENAME = "checkpoints.jsonl"
STAGE_RESULT_FILENAME = "stage.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ═════════════════════════════════════════════════════════════════════════════════════════════
# THE PRESSURE ALGEBRA — three-valued, so an unmeasured stage cannot be ranked last
# ═════════════════════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Pressure:
    """A stage's projected requirement as a multiple of its budget, WITH its epistemic kind.

    `value` is meaningless without `kind`, which is the entire point: a stage that was never
    run has no value, and the fail-open shape R15 names is exactly the code that would give it
    0.0 and let it sort to the bottom of the ranking.
    """
    stage: str
    value: Optional[float]
    kind: str
    basis: str

    @property
    def lo(self) -> float:
        if self.kind == KIND_UNKNOWN:
            return 0.0
        assert self.value is not None
        return self.value

    @property
    def hi(self) -> float:
        if self.kind == KIND_MEASURED:
            assert self.value is not None
            return self.value
        return math.inf


def compare_pressure(a: Pressure, b: Pressure) -> str:
    """"gt" / "lt" / "undecided" — decided only when the intervals do not overlap."""
    if a.lo > b.hi:
        return "gt"
    if b.lo > a.hi:
        return "lt"
    return "undecided"


def rank_pressures(pressures: Iterable[Pressure]) -> list[str]:
    """A best-effort descending ranking BY LOWER BOUND, for human reading only.

    Deliberately separate from the verdict: this ordering is not evidence of anything, because
    two unknowns tie at 0.0 here. `grade_prediction` is what decides, pair by pair.
    """
    return [p.stage for p in sorted(pressures, key=lambda p: (-p.lo, p.stage))]


def stage_pressure(measurement: "StageMeasurement", budgets: dict[str, float]) -> Pressure:
    """Project this stage's requirement at the probe's TARGET size and divide by its budget."""
    resource_name = BINDING_RESOURCE[measurement.stage]
    budget = budgets.get(resource_name)
    if not budget:
        return Pressure(measurement.stage, None, KIND_UNKNOWN,
                        f"no budget declared for {resource_name}")

    projected = measurement.projection.get(resource_name)
    if projected is None:
        # Never reached, errored before producing a per-unit constant, or produced no units.
        # UNKNOWN, not zero. This branch is the one the mutation test in
        # tests/tools/test_scale_probe_10k.py drives.
        return Pressure(measurement.stage, None, KIND_UNKNOWN,
                        f"status={measurement.status}, no projected {resource_name}")

    value = projected / budget
    if measurement.unmeasured:
        # A STAGE WITH AN OMITTED COMPONENT IS A FLOOR, NOT A FIGURE. Whatever the stage did
        # not measure can only ADD to the true requirement — the omitted work is never
        # negative — so the honest reading of a partial measurement is "at least this much".
        #
        # This is not hypothetical prudence. The 10k run packed 10,000 replica documents into
        # a 1.42MB git repository: 1,300x compression, because the replica replays 22 real
        # documents and delta compression sees redundancy a real 10k book would not have. Read
        # as a MEASURED figure that would have REFUTED the advisor's site-publish-over-git
        # ordering on the strength of a number biased low by three orders of magnitude.
        return Pressure(measurement.stage, value, KIND_LOWER_BOUND,
                        f"projected {resource_name}>={projected:.6g} / budget={budget:.6g} on "
                        f"the measured component ALONE; omitted and therefore unbounded above: "
                        f"{'; '.join(measurement.unmeasured)}")
    if resource_name in measurement.below_resolution:
        return Pressure(measurement.stage, value, KIND_LOWER_BOUND,
                        f"per-unit {resource_name} came out at 0 over "
                        f"{measurement.units_completed} {measurement.unit}s — below this "
                        f"probe's resolution at this size, so the projection is the fixed "
                        f"cost only and the true requirement is at least {value:.6g}x budget")
    if measurement.status == STATUS_MEASURED:
        kind = KIND_MEASURED
        basis = (f"projected {resource_name}={projected:.6g} from "
                 f"{measurement.units_completed} completed {measurement.unit}s / budget={budget:.6g}")
    else:
        # It died. The per-unit constant it produced before dying extrapolates, but the death
        # itself means the true cost is AT LEAST this — a full run pays whatever the stages it
        # never reached would have added on top.
        kind = KIND_LOWER_BOUND
        basis = (f"status={measurement.status} after {measurement.units_completed} "
                 f"{measurement.unit}s; projected {resource_name}>={projected:.6g} / "
                 f"budget={budget:.6g}")
    return Pressure(measurement.stage, value, kind, basis)


def grade_prediction(
    pressures: dict[str, Pressure],
    predicted_order: Iterable[str],
    *,
    register_written_at: Optional[float],
    first_stage_started_at: Optional[float],
) -> dict[str, Any]:
    """Grade the observed pressure ordering against the register's predicted ordering.

    REFUSES (verdict UNGRADED) when the register was not demonstrably written BEFORE the first
    stage started. A prediction register produced after the measurement grades nothing; a
    grader that would accept one is a control that cannot fail.

    Each ADJACENT predicted pair is graded independently — CONFIRMED (observed strictly
    greater), REFUTED (observed strictly less), UNDECIDED (intervals overlap). The overall
    verdict is REFUTED if any pair is refuted, CONFIRMED if every pair is confirmed, and
    PARTIAL otherwise. There is no path from an UNDECIDED pair to CONFIRMED.
    """
    predicted = list(predicted_order)
    if register_written_at is None or first_stage_started_at is None:
        return {"verdict": "UNGRADED", "reason": "register or run start timestamp missing",
                "pairs": [], "predicted_order": predicted}
    if register_written_at > first_stage_started_at:
        return {"verdict": "UNGRADED",
                "reason": (f"prediction register stamped {register_written_at:.3f} AFTER the "
                           f"first stage started {first_stage_started_at:.3f} — a prediction "
                           f"written after the fact is not a prediction"),
                "pairs": [], "predicted_order": predicted}

    pairs: list[dict[str, Any]] = []
    for higher, lower in zip(predicted, predicted[1:]):
        a, b = pressures.get(higher), pressures.get(lower)
        if a is None or b is None:
            pairs.append({"predicted_higher": higher, "predicted_lower": lower,
                          "result": "UNDECIDED", "why": "stage absent from this run"})
            continue
        cmp = compare_pressure(a, b)
        result = {"gt": "CONFIRMED", "lt": "REFUTED", "undecided": "UNDECIDED"}[cmp]
        pair = {"predicted_higher": higher, "predicted_lower": lower, "result": result,
                "why": f"{higher}: {a.kind} {a.value}; {lower}: {b.kind} {b.value}"}
        # HOW FAR OFF IS AN UNDECIDED PAIR? Fail-closed is correct and it is not, by itself,
        # decision-useful: a verdict that says only "undecided" three times is as ignorable as
        # a blind one. This states what it would TAKE to flip the pair — the multiple by which
        # the lower-ranked stage's unbounded component would have to exceed its own measured
        # part to reach the higher-ranked stage's floor. It is derived from the two intervals,
        # not judged, and it is deliberately not a second verdict.
        if result == "UNDECIDED" and b.hi == math.inf and b.lo > 0 and a.lo > b.lo:
            pair["flip_requires_factor"] = a.lo / b.lo
        pairs.append(pair)

    results = {p["result"] for p in pairs}
    if "REFUTED" in results:
        verdict = "REFUTED"
    elif results == {"CONFIRMED"}:
        verdict = "CONFIRMED"
    else:
        verdict = "PARTIAL"
    return {"verdict": verdict, "reason": "", "pairs": pairs, "predicted_order": predicted}


# ═════════════════════════════════════════════════════════════════════════════════════════════
# MEASUREMENT RECORD
# ═════════════════════════════════════════════════════════════════════════════════════════════

@dataclass
class StageMeasurement:
    stage: str
    status: str
    subject_kind: str = "real"          # "real" | "replica" — see module docstring
    unit: str = "unit"
    units_completed: int = 0
    wall_s: float = 0.0
    peak_rss_bytes: Optional[int] = None      # os.wait4 ru_maxrss — exact, survives SIGKILL
    baseline_rss_bytes: Optional[int] = None  # child's own VmRSS after inputs, before work
    output_bytes: Optional[int] = None
    per_unit: dict[str, float] = field(default_factory=dict)
    projection: dict[str, float] = field(default_factory=dict)
    target_units: Optional[int] = None
    detail: str = ""
    unmeasured: list[str] = field(default_factory=list)
    checkpoints: int = 0
    exit_signal: Optional[int] = None
    returncode: Optional[int] = None
    # Resources whose per-unit cost came out at exactly zero. See `project_stage`.
    below_resolution: list[str] = field(default_factory=list)
    # Stage-specific measured figures the generic fields have no home for — notably
    # settlement_build's `records_per_customer`, which is the conversion `_target_units` uses
    # to express the target book in the record-denominated stages' own unit.
    extra: dict[str, float] = field(default_factory=dict)


def project_stage(m: StageMeasurement, target_units: int) -> None:
    """Fill `m.per_unit` and `m.projection` from what the stage actually completed.

    The per-unit constants are INCREMENTAL: the interpreter's own baseline RSS (measured in the
    child after its inputs are loaded and before the working set starts growing) is subtracted
    before dividing. Without that subtraction a stage that completed 10 units would attribute
    ~40MB of interpreter to those 10 units and project a number ~2000x too large — the report
    would then "discover" a tear that is entirely the measurement's own floor.
    """
    m.target_units = target_units
    if m.units_completed <= 0:
        return

    if m.peak_rss_bytes is not None and m.baseline_rss_bytes is not None:
        incremental = max(0, m.peak_rss_bytes - m.baseline_rss_bytes)
        m.per_unit["rss_bytes"] = incremental / m.units_completed
        m.projection["rss_bytes"] = m.baseline_rss_bytes + m.per_unit["rss_bytes"] * target_units
        if incremental <= 0:
            m.below_resolution.append("rss_bytes")

    if m.wall_s > 0:
        m.per_unit["wall_s"] = m.wall_s / m.units_completed
        m.projection["wall_s"] = m.per_unit["wall_s"] * target_units
        if m.per_unit["wall_s"] <= 0:
            m.below_resolution.append("wall_s")
    else:
        m.below_resolution.append("wall_s")

    # A PER-UNIT COST OF EXACTLY ZERO IS THE INSTRUMENT'S FLOOR, NOT A MEASUREMENT, and the
    # difference decides verdicts. The N=20 rehearsal measured 3,600 settlement records whose
    # entire working set fitted underneath a fixed cost already paid (the 129MB price-cache
    # parse), so the growth attributable to them was 0 bytes — true, and emphatically not
    # "settlement records are free". Recording it as a MEASURED zero would let a small,
    # cheap-to-repeat probe certify a scale claim its resolution cannot support; the resource
    # is flagged here and `stage_pressure` degrades that stage to a LOWER BOUND.

    if m.output_bytes is not None:
        m.per_unit["output_bytes"] = m.output_bytes / m.units_completed
        m.projection["output_bytes"] = m.per_unit["output_bytes"] * target_units


# ═════════════════════════════════════════════════════════════════════════════════════════════
# CHILD-SIDE: the stages themselves
# ═════════════════════════════════════════════════════════════════════════════════════════════

def _proc_status_kb(field_name: str) -> int:
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith(field_name + ":"):
            return int(line.split()[1]) * 1024
    return 0


def _vm_rss_bytes() -> int:
    """This process's CURRENT resident set — what it is holding right now."""
    return _proc_status_kb("VmRSS")


def _vm_hwm_bytes() -> int:
    """This process's PEAK resident set so far (VmHWM) — the correct baseline, and the fix for
    a defect the first rehearsal exposed rather than a stylistic preference.

    The peak this probe projects from is `os.wait4`'s `ru_maxrss`, which is a PROCESS-LIFETIME
    high-water mark. Subtracting a point-in-time VmRSS baseline from it charges the stage's
    per-unit cost with every transient spike that happened BEFORE the work started — and one
    of those spikes is enormous here, because loading the real cached Elexon SSP means
    `json.loads` on a 129MB file whose parse peak is several times its final retained size. The
    N=20 rehearsal duly reported 67KB per settlement record, ~100x the true figure, all of it
    the price-cache parse wearing the records' clothes. Subtracting the high-water mark instead
    means only growth ABOVE anything already seen is attributed to the units."""
    return _proc_status_kb("VmHWM")


class _Checkpointer:
    """Append-and-fsync progress, so a SIGKILL still leaves the measurement on disk.

    The flush+fsync is not defensive over-engineering: without it the last N checkpoints sit in
    a userspace buffer that dies with the process, and the exact runs this probe exists to
    measure — the ones that get killed — would be the ones that reported nothing.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.count = 0
        self._fh = open(path, "a", encoding="utf-8")

    def write(self, **fields: Any) -> None:
        self.count += 1
        fields["n"] = self.count
        fields["t"] = time.time()
        fields["rss_bytes"] = _vm_rss_bytes()
        fields["hwm_bytes"] = _vm_hwm_bytes()
        self._fh.write(json.dumps(fields) + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:
            pass


# The largest per-year lambda `simulation.population_draw._poisson` can actually honour. Above
# roughly this value `math.exp(-lam)` underflows to 0.0, the Knuth loop's target becomes
# unreachable, and it exits only when the running product of uniforms denormalises to zero —
# which happens after ~700 iterations REGARDLESS OF LAMBDA. See `_draw_book`.
_POISSON_SATURATION_LAMBDA = 745.0

# Comfortably below the saturation point, so each batch is a real Poisson draw.
_DRAW_BATCH_LAMBDA = 250.0


def _draw_book(n: int, base_seed: int, year: int) -> list[dict]:
    """N synthetic customers from the SHIPPED per-run population draw, IN BATCHES.

    Batching is not a style choice, and the reason is a defect this probe found in the
    generator it was pointed at. `iter_acquisition_events(acquisitions_per_year_lambda=10000)`
    does not return ~10,000 customers. It returns ~733, silently:
    `simulation.population_draw._poisson` is Knuth's algorithm, whose target is
    `math.exp(-lam)`, and that underflows to exactly 0.0 at lambda >~ 745. With an unreachable
    target the loop runs until the running product of uniform draws denormalises to zero, which
    takes ~700 multiplications no matter what lambda was — so every request above the
    saturation point returns the same meaningless number, with no exception and no warning.
    Measured: lambda=750 -> 703, lambda=10000 -> 733. Pinned by
    `tests/tools/test_scale_probe_10k.py::test_the_generator_saturates_above_745`.

    THE PROBE DOES NOT FIX IT. `simulation/population_draw.py` is WORLD code outside this
    atom's file_scope, and its draw is a director-owned CURRICULUM instrument (R13) — a change
    there alters which world every run faces and is not a measurement tool's call to make. The
    finding is filed for the owning lane; here the generator is simply called repeatedly at a
    lambda it can honour, which uses the shipped draw unmodified.

    Each batch gets its own base_seed (deterministic in the caller's seed, C-S2) and its own
    customer-id prefix, because the generator numbers within a year from 1 and would otherwise
    hand back colliding ids across batches — a collision that would silently shrink the book
    again, which is the same class of defect one layer up.
    """
    from simulation.population_draw import iter_acquisition_events

    book: list[dict] = []
    batch = 0
    # Bounded: at ~250 per batch this is ~4x the batches needed, and a generator that stopped
    # yielding entirely must terminate the loop rather than spin.
    max_batches = max(8, int(n / _DRAW_BATCH_LAMBDA * 4) + 8)
    while len(book) < n and batch < max_batches:
        drawn = list(iter_acquisition_events(
            base_seed=base_seed + batch * 7919, start_year=year, end_year=year,
            acquisitions_per_year_lambda=_DRAW_BATCH_LAMBDA,
        ))
        for cust in drawn:
            record = cust.to_customer_dict()
            record["customer_id"] = f"B{batch:04d}-{record['customer_id']}"
            book.append(record)
        batch += 1
        if not drawn:
            break
    if len(book) < n:
        raise RuntimeError(
            f"the population draw yielded {len(book)} customers against a requested {n} after "
            f"{batch} batches — the probe refuses to measure a book it did not get, because "
            f"reporting per-customer costs against an assumed N is how a scale claim becomes "
            f"arithmetic again")
    return book[:n]


def _settlement_inputs(book: list[dict], start: str) -> list[dict]:
    """Project the drawn book down to what `run_settlement` actually consumes.

    Three keys — identity, contract start, unit rate. The unit rate is a fixed probe constant
    (£140/MWh, mid-range of the real book's rates) because settlement's arithmetic cost does
    not vary with it, and drawing one would add a source of variation the probe cannot
    attribute. Recorded as a stated simplification rather than left implicit.
    """
    return [{"customer_id": c["customer_id"],
             "acquisition_date": start,
             "unit_rate_gbp_per_mwh": 140.0} for c in book]


def _real_prices(start: str, end: str) -> list[dict]:
    """Real cached Elexon SSP settlement prices. Never the live API — autonomous runs have no
    network, and a probe that silently fell back to synthetic prices would be measuring a
    different record stream than the one a real run builds."""
    from sim.cache_store import get_cached_prices

    records = get_cached_prices(start, end)
    if records is None:
        raise RuntimeError(
            f"no cached Elexon SSP covering {start}..{end} in sim/cache/elexon_ssp_full.json — "
            "the probe refuses to substitute synthetic prices for the real settlement stream")
    return records


def _stage_population_draw(args, cp: _Checkpointer) -> dict:
    """The control stage: what the book itself costs, before anything is done with it.

    Not one of the advisor's four predictions, and included precisely because of that — if the
    book alone were the binding constraint, every prediction in the register would be wrong in
    a way none of them could express.
    """
    from simulation.population_draw import iter_acquisition_events

    baseline = _vm_hwm_bytes()
    t0 = time.monotonic()
    book: list[dict] = []
    batch = 0
    max_batches = max(8, int(args.customers / _DRAW_BATCH_LAMBDA * 4) + 8)
    while len(book) < args.customers and batch < max_batches:
        drawn = list(iter_acquisition_events(
            base_seed=args.seed + batch * 7919, start_year=args.year, end_year=args.year,
            acquisitions_per_year_lambda=_DRAW_BATCH_LAMBDA))
        if not drawn:
            break
        for cust in drawn:
            record = cust.to_customer_dict()
            record["customer_id"] = f"B{batch:04d}-{record['customer_id']}"
            book.append(record)
        batch += 1
        cp.write(customers=len(book), batches=batch, elapsed_s=time.monotonic() - t0)
    cp.write(customers=len(book), batches=batch, final=True)
    wall = time.monotonic() - t0
    if len(book) < args.customers:
        raise RuntimeError(f"drew {len(book)} of {args.customers} requested customers in "
                           f"{batch} batches — see _draw_book on the generator's saturation")
    return {"unit": "customer", "units_completed": len(book), "wall_s": wall,
            "baseline_rss_bytes": baseline, "subject_kind": "real",
            "detail": (f"drew {len(book)} customers via simulation.population_draw in {batch} "
                       f"batches of lambda={_DRAW_BATCH_LAMBDA:g} (the generator saturates "
                       f"above ~{_POISSON_SATURATION_LAMBDA:g})")}


def _stage_settlement_build(args, cp: _Checkpointer) -> dict:
    """THE stage the advisor ranked #1: the in-run working set at settlement build.

    Driven in CUSTOMER CHUNKS through the real `run_settlement`, accumulating into one list —
    which is what a real run holds. Chunking is exact rather than approximate: `run_settlement`
    loops over customers independently and concatenates, so chunked output equals whole output
    (pinned by `test_chunking_does_not_change_the_subject`). Without chunking, a stage killed
    at the ceiling would report nothing at all; with it, the last checkpoint says exactly how
    far the box got.
    """
    from sim.profile_class_1 import load_pc1_shape
    from simulation.settlement import run_settlement

    book = _draw_book(args.customers, args.seed, args.year)
    customers = _settlement_inputs(book, args.start_date)
    end_date = _add_days(args.start_date, args.days - 1)
    prices = _real_prices(args.start_date, end_date)

    # A per-date shape cache: the real run has one too (the CSV is read once), and without it
    # this stage would measure CSV parsing rather than the settlement working set.
    shape_cache: dict[str, list[float]] = {}

    def consumption_shape(date_str: str) -> list[float]:
        got = shape_cache.get(date_str)
        if got is None:
            got = load_pc1_shape(date_str)
            shape_cache[date_str] = got
        return got

    # Warm the shape cache before the baseline stamp: it is a fixed cost, not a per-record one.
    for offset in range(args.days):
        consumption_shape(_add_days(args.start_date, offset))

    baseline = _vm_hwm_bytes()
    t0 = time.monotonic()
    records: list[dict] = []
    done = 0
    for chunk_start in range(0, len(customers), args.chunk_customers):
        chunk = customers[chunk_start:chunk_start + args.chunk_customers]
        records.extend(run_settlement(chunk, args.start_date, end_date,
                                      consumption_shape, prices))
        done += len(chunk)
        cp.write(customers=done, records=len(records), elapsed_s=time.monotonic() - t0)
    return {"unit": "record", "units_completed": len(records), "wall_s": time.monotonic() - t0,
            "baseline_rss_bytes": baseline, "subject_kind": "real",
            "records_per_customer": (len(records) / done) if done else 0,
            "customers_completed": done,
            "detail": (f"{len(records)} settlement records for {done} customers x {args.days} "
                       f"days from {args.start_date}, real PC1 shape + real cached Elexon SSP")}


def _stage_run_output_serialization(args, cp: _Checkpointer) -> dict:
    """Predicted #2: what it costs to turn the working set into the run-output JSON.

    Measured on a BOUNDED record set (`--serialize-records`) rather than the full 10k working
    set, for one reason stated plainly: stage 2 is expected to die before the full set exists,
    so a serialization stage that waited for it would measure nothing at all. Bytes-per-record
    and the RSS multiple that `json.dumps` costs over the list it is given are both per-unit
    constants; the projection is those constants at the target record count, which is stage 2's
    OWN measured records-per-customer x the target book. Extrapolated, and labelled so.
    """
    from sim.profile_class_1 import load_pc1_shape
    from simulation.settlement import run_settlement

    per_customer_records = args.days * 48
    n_customers = max(1, math.ceil(args.serialize_records / max(1, per_customer_records)))
    book = _draw_book(n_customers, args.seed, args.year)
    customers = _settlement_inputs(book, args.start_date)
    end_date = _add_days(args.start_date, args.days - 1)
    prices = _real_prices(args.start_date, end_date)

    shape_cache: dict[str, list[float]] = {}

    def consumption_shape(date_str: str) -> list[float]:
        got = shape_cache.get(date_str)
        if got is None:
            got = load_pc1_shape(date_str)
            shape_cache[date_str] = got
        return got

    records = run_settlement(customers, args.start_date, end_date, consumption_shape, prices)
    cp.write(records_built=len(records), phase="built")

    baseline = _vm_hwm_bytes()
    t0 = time.monotonic()
    payload = json.dumps(records)
    wall = time.monotonic() - t0
    out_path = Path(args.shared or args.scratch) / "run_output_probe.json"
    out_path.write_text(payload)
    cp.write(records=len(records), bytes=len(payload), elapsed_s=wall, phase="serialized",
             final=True)
    return {"unit": "record", "units_completed": len(records), "wall_s": wall,
            "baseline_rss_bytes": baseline, "output_bytes": len(payload),
            "subject_kind": "real",
            "unmeasured": [
                ("THE REDUCTION. This stage serialises the RAW settlement working set, which "
                 "prices the persist path's INPUT. The shipped run reduces first "
                 "(`saas.reporting.annual_report.extract_report_data`) and persists the "
                 "projection, so these bytes are what the raw set WOULD cost, not what "
                 "run_output_latest.json costs. The reduction's own cost is not measured here "
                 "and the two figures must not be read as the same number"),
            ],
            "detail": (f"json.dumps of {len(records)} real settlement records "
                       f"({len(payload)} bytes) then written to scratch")}


def _stage_site_publish(args, cp: _Checkpointer) -> dict:
    """Predicted #3: per-customer site publish, as a REPLICA (see module docstring).

    Byte-shapes come from the 22 REAL documents in `site/data/customers/`, replayed round-robin
    with a re-keyed customer id. What is NOT measured, and is reported as unmeasured rather
    than as zero: the cost of COMPUTING 10k customers' worth of content, which needs a 10k run
    output that stage 2 exists to show cannot be built here.
    """
    docs = sorted(REAL_CUSTOMER_DOCS_DIR.glob("*.json"))
    if not docs:
        raise RuntimeError(f"no real customer documents under {REAL_CUSTOMER_DOCS_DIR} to "
                           "replay — the replica refuses to invent a document shape")
    templates = [d.read_text() for d in docs]
    # The SHARED run root, not this stage's own scratch: git_transport is a CONSUMER of
    # these files, and a per-stage directory would have handed it an empty tree — which is
    # exactly what the first rehearsal did (git_transport: error, 0 files). The consuming
    # stage refuses rather than inventing files, so the defect surfaced instead of hiding.
    out_dir = Path(args.shared or args.scratch) / "published"
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline = _vm_hwm_bytes()
    t0 = time.monotonic()
    written = 0
    total_bytes = 0
    for i in range(args.customers):
        body = templates[i % len(templates)]
        path = out_dir / f"SYN-{i:06d}.json"
        path.write_text(body)
        written += 1
        total_bytes += len(body)
        if written % max(1, args.customers // 40) == 0:
            cp.write(files=written, bytes=total_bytes, elapsed_s=time.monotonic() - t0)
    cp.write(files=written, bytes=total_bytes, elapsed_s=time.monotonic() - t0, final=True)
    return {"unit": "file", "units_completed": written, "wall_s": time.monotonic() - t0,
            "baseline_rss_bytes": baseline, "output_bytes": total_bytes,
            "subject_kind": "replica",
            "unmeasured": ["cost of COMPUTING per-customer content at 10k (needs a 10k run "
                           "output, which stage settlement_build exists to price)"],
            "detail": (f"wrote {written} per-customer documents replaying {len(docs)} real "
                       f"site/data/customers shapes into scratch")}


def _stage_git_transport(args, cp: _Checkpointer) -> dict:
    """Predicted #4: git transport of the published outputs. REPLICA subject, REAL git.

    A scratch repo, never this one: adding 10k files to the live index would collide with every
    other lane on this shared tree (and `git add` on a shared index is how half-changes get
    swept into someone else's commit). `git gc`/pack size is the transport proxy — a push is
    not attempted, because measuring the network would measure the network.
    """
    src = Path(args.shared or args.scratch) / "published"
    if not src.is_dir() or not any(src.iterdir()):
        raise RuntimeError("git_transport has no published files to transport — site_publish "
                           "did not complete, so its cost here is UNKNOWN, not zero")
    repo = Path(args.scratch) / "transport_repo"
    repo.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@localhost",
           "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@localhost"}
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=env)
    shutil.copytree(src, repo / "data", dirs_exist_ok=True)
    n_files = sum(1 for _ in (repo / "data").iterdir())

    baseline = _vm_hwm_bytes()
    t0 = time.monotonic()
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=env)
    cp.write(phase="added", files=n_files, elapsed_s=time.monotonic() - t0)
    subprocess.run(["git", "commit", "-q", "-m", "probe"], cwd=repo, check=True, env=env)
    cp.write(phase="committed", files=n_files, elapsed_s=time.monotonic() - t0)
    subprocess.run(["git", "gc", "-q", "--aggressive" if args.git_gc_aggressive else "--auto"],
                   cwd=repo, check=True, env=env)
    wall = time.monotonic() - t0
    git_bytes = sum(p.stat().st_size for p in (repo / ".git").rglob("*") if p.is_file())
    distinct, published_bytes = _replica_redundancy(src)
    cp.write(phase="packed", files=n_files, git_bytes=git_bytes, distinct_docs=distinct,
             published_bytes=published_bytes, elapsed_s=wall, final=True)
    return {"unit": "file", "units_completed": n_files, "wall_s": wall,
            "baseline_rss_bytes": baseline, "output_bytes": git_bytes,
            "subject_kind": "replica",
            "unmeasured": [
                "network push time (measuring it would measure the network, not the repository)",
                (f"REPLICA REDUNDANCY, and it dominates this number: the {n_files} documents "
                 f"are replays of {distinct} distinct real ones, so git's delta compression "
                 f"sees a redundancy a real book would not have. Published {published_bytes} "
                 f"bytes packed to {git_bytes} ({published_bytes / max(1, git_bytes):.0f}x) — "
                 f"both pack size and wall time are biased LOW by an unknown factor"),
            ],
            "detail": f"git add+commit+gc of {n_files} files; .git is {git_bytes} bytes"}


def _replica_redundancy(src: Path) -> tuple[int, int]:
    """(distinct documents, total published bytes) — the honest divisor for the caveat above.

    Hashed rather than held: the replica is ~1.8GB at 10k, and a probe that OOMed while
    computing its own caveat would be a fine joke and a lost measurement.
    """
    import hashlib

    seen: set[str] = set()
    total = 0
    for path in src.iterdir():
        if not path.is_file():
            continue
        digest = hashlib.blake2b(digest_size=16)
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                digest.update(block)
                total += len(block)
        seen.add(digest.hexdigest())
    return len(seen), total


STAGE_FUNCS: dict[str, Callable[[Any, _Checkpointer], dict]] = {
    "population_draw": _stage_population_draw,
    "settlement_build": _stage_settlement_build,
    "run_output_serialization": _stage_run_output_serialization,
    "site_publish": _stage_site_publish,
    "git_transport": _stage_git_transport,
}


def _add_days(iso_date: str, days: int) -> str:
    from datetime import date, timedelta
    return (date.fromisoformat(iso_date) + timedelta(days=days)).isoformat()


def run_stage_in_process(args) -> int:
    """The CHILD entry point. Writes `stage.json` next to its checkpoints, always."""
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    cp = _Checkpointer(scratch / CHECKPOINTS_FILENAME)
    result: dict[str, Any] = {"stage": args.run_stage}
    rc = 0
    try:
        if args.as_ceiling_mb:
            limit = args.as_ceiling_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        result.update(STAGE_FUNCS[args.run_stage](args, cp))
        result["outcome"] = STATUS_MEASURED
    except MemoryError as exc:
        result["outcome"] = STATUS_CEILING_DEATH
        result["detail"] = f"MemoryError at the {args.as_ceiling_mb}MB address-space ceiling: {exc}"
        rc = 3
    except Exception as exc:  # noqa: BLE001 — the cause IS the measurement
        result["outcome"] = STATUS_ERROR
        result["detail"] = f"{type(exc).__name__}: {exc}"
        rc = 4
    finally:
        result["checkpoints"] = cp.count
        cp.close()
        (scratch / STAGE_RESULT_FILENAME).write_text(json.dumps(result, indent=2))
    return rc


# ═════════════════════════════════════════════════════════════════════════════════════════════
# PARENT-SIDE: run each stage as its own killable, measurable child
# ═════════════════════════════════════════════════════════════════════════════════════════════

def _run_stage_child(stage: str, scratch: Path, args) -> StageMeasurement:
    """Launch one stage as a child and measure it exactly, INCLUDING when it is killed.

    Peak RSS comes from `os.wait4`'s rusage, not from sampling /proc: the kernel reports the
    reaped child's `ru_maxrss` even when it died to SIGKILL, which is precisely the case a
    poller would miss (the last sample before death is not the peak, and /proc/<pid> is gone
    the moment it is). `start_new_session=True` plus a killpg on timeout means a stage that
    spawns git children takes them with it rather than orphaning them onto the box.
    """
    scratch.mkdir(parents=True, exist_ok=True)
    argv = [sys.executable, "-m", "tools.scale_probe_10k",
            "--run-stage", stage, "--scratch", str(scratch),
            "--customers", str(args.customers), "--days", str(args.days),
            "--start-date", args.start_date, "--year", str(args.year),
            "--seed", str(args.seed), "--chunk-customers", str(args.chunk_customers),
            "--serialize-records", str(args.serialize_records),
            "--as-ceiling-mb", str(args.as_ceiling_mb),
            "--shared", str(scratch.parent)]
    if args.git_gc_aggressive:
        argv.append("--git-gc-aggressive")

    out_path = scratch / "child.out"
    started = time.monotonic()
    timed_out = threading.Event()
    with open(out_path, "wb") as out_fh:
        proc = subprocess.Popen(argv, cwd=str(PROJECT), stdout=out_fh,
                                stderr=subprocess.STDOUT, start_new_session=True)
        killer = threading.Timer(args.stage_timeout_s, _kill_group, args=(proc.pid, timed_out))
        killer.daemon = True
        killer.start()
        try:
            _, status, rusage = os.wait4(proc.pid, 0)
        finally:
            killer.cancel()
            # Popen must be told the child is already reaped, or its finaliser waits forever
            # on a pid that no longer exists.
            proc.returncode = os.waitstatus_to_exitcode(status) if not os.WIFSIGNALED(status) \
                else -os.WTERMSIG(status)
    wall = time.monotonic() - started
    return _assemble_measurement(stage, scratch, status, rusage, wall,
                                 timed_out=timed_out.is_set())


def _assemble_measurement(stage: str, scratch: Path, status: int, rusage, wall: float, *,
                          timed_out: bool) -> StageMeasurement:
    """Reconstruct what the stage did from the three things a dead child still leaves behind:
    its exit status, its rusage, and whatever reached the disk before it stopped."""
    signalled = os.WIFSIGNALED(status)
    exit_signal = os.WTERMSIG(status) if signalled else None
    returncode = None if signalled else os.waitstatus_to_exitcode(status)

    child = {}
    result_path = scratch / STAGE_RESULT_FILENAME
    if result_path.exists():
        try:
            child = json.loads(result_path.read_text())
        except json.JSONDecodeError:
            child = {}

    checkpoints = _read_checkpoints(scratch / CHECKPOINTS_FILENAME)

    if timed_out:
        status_name = STATUS_TIMEOUT
    elif child.get("outcome"):
        status_name = child["outcome"]
    elif signalled:
        # Killed by something that was not our watchdog — on this box that is the OOM killer.
        status_name = STATUS_CEILING_DEATH
    else:
        status_name = STATUS_ERROR

    m = StageMeasurement(
        stage=stage,
        status=status_name,
        subject_kind=child.get("subject_kind", "unknown"),
        unit=child.get("unit", _unit_from_checkpoints(checkpoints)),
        wall_s=float(child.get("wall_s") or wall),
        peak_rss_bytes=int(rusage.ru_maxrss) * 1024,   # Linux reports ru_maxrss in KB
        baseline_rss_bytes=child.get("baseline_rss_bytes"),
        output_bytes=child.get("output_bytes"),
        detail=child.get("detail", ""),
        unmeasured=list(child.get("unmeasured", [])),
        checkpoints=len(checkpoints),
        exit_signal=exit_signal,
        returncode=returncode,
    )
    m.units_completed = int(child.get("units_completed") or
                            _units_from_checkpoints(checkpoints, m.unit))
    _recover_extras(m, child, checkpoints)
    if status_name != STATUS_MEASURED and not m.detail:
        m.detail = (f"died without a self-report; last checkpoint: "
                    f"{checkpoints[-1] if checkpoints else 'none'}")
    if m.baseline_rss_bytes is None and checkpoints:
        # No self-reported baseline (died before stamping it). The first checkpoint's RSS is
        # the closest honest floor — always an OVER-estimate of the baseline, which makes the
        # per-unit constant an UNDER-estimate. Recorded so the direction of the bias is known.
        m.baseline_rss_bytes = int(checkpoints[0].get("rss_bytes", 0)) or None
        m.detail += " [baseline taken from first checkpoint — per-unit cost is under-stated]"
    return m


def _recover_extras(m: StageMeasurement, child: dict, checkpoints: list[dict]) -> None:
    """Recover the stage-specific figures, preferring the self-report and falling back to the
    checkpoints when the child died before writing one.

    `records_per_customer` is the one that matters: it converts the target book into the
    record-denominated stages' own unit, and settlement_build is EXPECTED to die, so it is
    checkpointed alongside the record count precisely so the conversion survives the death.
    """
    for key in ("records_per_customer", "customers_completed"):
        if child.get(key) is not None:
            m.extra[key] = float(child[key])
    if "records_per_customer" in m.extra:
        return
    for cp in reversed(checkpoints):
        if cp.get("records") and cp.get("customers"):
            m.extra["records_per_customer"] = cp["records"] / cp["customers"]
            m.extra["customers_completed"] = float(cp["customers"])
            return


def _kill_group(pid: int, flag: threading.Event) -> None:
    flag.set()
    try:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def _read_checkpoints(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a torn final line is what a SIGKILL mid-write looks like
    return out


def _units_from_checkpoints(checkpoints: list[dict], unit: str) -> int:
    key = {"record": "records", "customer": "customers", "file": "files"}.get(unit)
    for cp in reversed(checkpoints):
        if key and key in cp:
            return int(cp[key])
    return 0


def _unit_from_checkpoints(checkpoints: list[dict]) -> str:
    for cp in reversed(checkpoints):
        for key, unit in (("records", "record"), ("files", "file"), ("customers", "customer")):
            if key in cp:
                return unit
    return "unit"


# ═════════════════════════════════════════════════════════════════════════════════════════════
# BUDGETS, REGISTER, REPORT
# ═════════════════════════════════════════════════════════════════════════════════════════════

def measure_budgets(stage_timeout_s: float) -> dict[str, float]:
    """The denominators, read from the box at probe time — never hardcoded.

    `rss_bytes` is MemAvailable, not MemTotal: what a run can actually have is what is free
    beside the daemons and the publisher already living here, and MemTotal would flatter every
    pressure ratio by the amount the box is already using.
    """
    budgets: dict[str, float] = {"wall_s": float(stage_timeout_s)}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                budgets["rss_bytes"] = float(line.split()[1]) * 1024
                break
    except OSError:
        pass
    return budgets


def _scratch_filesystem(path: Path) -> str:
    """Which filesystem the scratch lives on. tmpfs would make publish/transport numbers about
    RAM rather than disk, so the report states it rather than leaving it to be assumed."""
    try:
        out = subprocess.run(["stat", "-f", "-c", "%T", str(path)],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def write_prediction_register(path: Path, *, predicted_order: Iterable[str], run_id: str,
                              source: str) -> dict:
    """Write the register BEFORE any stage runs. Its `written_at` is what `grade_prediction`
    checks against the first stage's start — see that function for why."""
    register = {
        "run_id": run_id,
        "written_at": time.time(),
        "written_at_utc": _utc_now(),
        "source": source,
        "predicted_order": list(predicted_order),
        "claim": ("Ranked most-likely-to-tear first. Ordering is by PRESSURE = projected "
                  "requirement at the target book / this box's budget in that stage's binding "
                  "resource. A surprise ordering is the most valuable outcome."),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(register, indent=2) + "\n")
    return register


def affordability(pressure: Pressure) -> str:
    """Does this stage FIT on this box at the target size? Decided from the interval, never
    judged — and UNDECIDED wherever the interval straddles 1.0.

    This is the figure the dependent proposal atom consumes, and its whole value is that it
    cannot be talked into a yes: a stage whose floor already exceeds the budget DOES_NOT_FIT
    no matter how the rest of the probe went, and a stage with an unmeasured component can
    never come back FITS, because the omitted work could be anything.
    """
    if pressure.kind == KIND_UNKNOWN:
        return "UNKNOWN"
    if pressure.lo > 1.0:
        return "DOES_NOT_FIT"
    if pressure.hi < 1.0:
        return "FITS"
    return "UNDECIDED"


def build_report(*, run_id: str, args, measurements: list[StageMeasurement],
                 budgets: dict[str, float], register: dict,
                 first_stage_started_at: Optional[float], scratch: Path) -> dict:
    pressures = {m.stage: stage_pressure(m, budgets) for m in measurements}
    grading = grade_prediction(pressures, register.get("predicted_order", []),
                               register_written_at=register.get("written_at"),
                               first_stage_started_at=first_stage_started_at)
    unmeasured = [{"stage": m.stage, "what": w} for m in measurements for w in m.unmeasured]
    for stage in STAGES:
        if stage not in {m.stage for m in measurements}:
            unmeasured.append({"stage": stage, "what": "stage not run in this probe"})
    return {
        "artefact": "AO12 scale probe report",
        "run_id": run_id,
        "generated_at_utc": _utc_now(),
        "target": {"customers": args.customers, "days": args.days,
                   "start_date": args.start_date, "seed": args.seed},
        "limits": {"as_ceiling_mb": args.as_ceiling_mb,
                   "as_ceiling_unit": "RLIMIT_AS — VIRTUAL ADDRESS SPACE, not RSS",
                   "stage_timeout_s": args.stage_timeout_s},
        "box": {"budgets": budgets, "scratch": str(scratch),
                "scratch_filesystem": _scratch_filesystem(scratch.parent)},
        "prediction_register": register,
        "stages": [asdict(m) for m in measurements],
        "pressures": {k: asdict(v) for k, v in pressures.items()},
        "affordability": {k: affordability(v) for k, v in pressures.items()},
        "observed_order_by_lower_bound": rank_pressures(pressures.values()),
        "prediction_verdict": grading,
        "unmeasured": unmeasured,
        "reading_note": (
            "Every projection is per-unit constants measured before the stage stopped, times "
            "the target size. A stage with status != measured projects a LOWER BOUND. A stage "
            "with no projection is UNKNOWN and is never priced at zero — a consumer that "
            "substitutes 0 for an unknown has re-introduced the fail-open shape this report "
            "exists to avoid."),
    }


# ═════════════════════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════════════════════

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--customers", type=int, default=10_000)
    p.add_argument("--days", type=int, default=365)
    p.add_argument("--start-date", default="2021-01-01")
    p.add_argument("--year", type=int, default=2021, help="draw year for the synthetic book")
    p.add_argument("--seed", type=int, default=20260812)
    p.add_argument("--chunk-customers", type=int, default=5,
                   help="settlement checkpoint granularity — smaller means a killed stage "
                        "reports a tighter bound on where it tore")
    p.add_argument("--serialize-records", type=int, default=500_000)
    p.add_argument("--as-ceiling-mb", type=int, default=3072,
                   help="RLIMIT_AS per child. Bounds VIRTUAL ADDRESS SPACE (not RSS) so a "
                        "stage dies at a ceiling we chose rather than letting the kernel pick "
                        "a victim on a shared box")
    p.add_argument("--stage-timeout-s", type=float, default=300.0)
    p.add_argument("--git-gc-aggressive", action="store_true")
    p.add_argument("--stages", nargs="*", default=list(STAGES), choices=list(STAGES))
    p.add_argument("--scratch-root", type=Path, default=DEFAULT_SCRATCH_ROOT)
    p.add_argument("--report", type=Path, default=REPORT_PATH)
    p.add_argument("--register", type=Path, default=PREDICTION_REGISTER_PATH)
    p.add_argument("--keep-scratch", action="store_true")
    p.add_argument("--run-stage", choices=list(STAGES), default=None,
                   help="CHILD PROTOCOL — run exactly this stage in this process")
    p.add_argument("--scratch", default=None, help="child protocol: this stage's scratch dir")
    p.add_argument("--shared", default=None,
                   help="child protocol: the RUN root shared by every stage — where a\nproducing stage leaves output for a consuming stage")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    if args.run_stage:
        return run_stage_in_process(args)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    scratch = Path(args.scratch_root) / run_id
    scratch.mkdir(parents=True, exist_ok=True)

    # BEFORE the run. Ordering here is the control, not a convention.
    register = write_prediction_register(
        Path(args.register), predicted_order=ADVISOR_PREDICTED_ORDER, run_id=run_id,
        source="docs/design/refs/ADVISOR_REVIEW_DATA_ARCHITECTURE_AND_SCALE_PROBE_2026-08-05.md §3")
    budgets = measure_budgets(args.stage_timeout_s)

    measurements: list[StageMeasurement] = []
    first_started: Optional[float] = None
    for stage in args.stages:
        print(f"[probe] {stage} …", flush=True)
        if first_started is None:
            first_started = time.time()
        m = _run_stage_child(stage, scratch / stage, args)
        target_units = _target_units(stage, args, measurements)
        project_stage(m, target_units)
        measurements.append(m)
        print(f"[probe] {stage}: {m.status}, {m.units_completed} {m.unit}s, "
              f"{m.wall_s:.1f}s, peak_rss={_mb(m.peak_rss_bytes)}", flush=True)

    report = build_report(run_id=run_id, args=args, measurements=measurements, budgets=budgets,
                          register=register, first_stage_started_at=first_started,
                          scratch=scratch)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    print(f"[probe] report → {args.report}")
    print(f"[probe] verdict: {report['prediction_verdict']['verdict']}")

    if not args.keep_scratch:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


def _target_units(stage: str, args, done: list[StageMeasurement]) -> int:
    """The target size IN THIS STAGE'S OWN UNIT.

    The record-denominated stages take records-per-customer from `settlement_build`'s OWN
    measurement where it has one, rather than from `days * 48`: the real figure differs
    (settlement periods are skipped where no price record exists, and DST days are 46 or 50
    periods), and using the arithmetic value would quietly replace a measurement with the
    extrapolation this probe exists to retire.
    """
    if stage in ("settlement_build", "run_output_serialization"):
        per_customer: float = args.days * 48
        for m in done:
            if m.stage == "settlement_build" and m.extra.get("records_per_customer"):
                per_customer = m.extra["records_per_customer"]
                break
        return int(args.customers * per_customer)
    return args.customers


def _mb(value: Optional[int]) -> str:
    return "unknown" if value is None else f"{value / (1024 * 1024):.1f}MB"


if __name__ == "__main__":
    raise SystemExit(main())
