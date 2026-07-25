"""RUN MANIFEST & LEDGER + the three separated scores.

Builds DIRECTOR_RULING_POPULATION_ACTIVATION_AND_RUN_LEDGER_2026-07-25 §3+§4.

WHY THIS EXISTS (director's words, verbatim from the ruling)
------------------------------------------------------------
"Without this the probability-weighted EV and the unweighted worst-case
survival verdicts cannot be computed, and no one can tell whether a change made
the company better or merely luckier."

Every run emits ONE comparable ledger row (§3). The three scores (§4) are
computed FROM THE SAME ROWS and MUST NEVER be conflated:

  ROBUSTNESS   — unweighted, tail-focused: does the machinery cope with what it
                 is shown? (a development signal)
  COMMERCIAL EV — probability-weighted by the TRUE measure: what is the company
                 worth?
  SURVIVAL     — worst-case over the sampled set, unweighted: does it die
                 anywhere?

R15 GUARD (the load-bearing, mutation-testable control)
-------------------------------------------------------
COMMERCIAL EV is on a WEIGHTED basis (true-probability weighting); ROBUSTNESS
and SURVIVAL are UNWEIGHTED. The ruling: "any aggregate that mixes weighted and
unweighted bases must fail loudly." `aggregate_scores()` therefore raises
`MixedBasisError` the instant it is handed scores of differing basis. The three
scores are returned as a `ThreeScores` bundle that keeps them SEPARATE — there
is deliberately no `.blended()` scalar, because a single blended number is
exactly the accidental conflation the ruling forbids. Proven both ways in
`tests/background/test_run_manifest.py` (same-basis reduces; mixed-basis
raises — mutate the guard to `pass` and that test goes red).

IMPORTANCE-SAMPLING DISCIPLINE (restated, not re-decided)
---------------------------------------------------------
The sampling distribution (which cells the run-rotation grid visits, §2) is NOT
the true probability measure. COMMERCIAL EV weights by each row's
`true_probability` (the director-reserved true measure), never by how often the
rotation happened to sample that cell. ROBUSTNESS and SURVIVAL ignore
probability entirely — they are unweighted over the sampled set on purpose.

SCOPE NOTE (honest): this module is ADDITIVE infrastructure. It does not flip
`SE_DRAW_POPULATION` on, wire any run entrypoint, or change any curriculum
value — those are the held activation core (director-reserved, §1) and the
run-rotation build (§2). This module lets an activated run BE JUDGED once it
lands; it is a precondition for activation, not the activation itself.
"""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, List, Optional, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = _REPO_ROOT / "docs" / "observability" / "run_ledger.jsonl"
_CURRICULUM_PATH = _REPO_ROOT / "docs" / "design" / "segmentation_curriculum_v1.json"


# --------------------------------------------------------------------------- #
# §4 scores — the basis is a first-class, checkable property                  #
# --------------------------------------------------------------------------- #
class ScoreBasis(str, Enum):
    """The measure a score is computed against. Mixing these is the R15 defect."""

    WEIGHTED = "weighted"      # probability-weighted by the true measure
    UNWEIGHTED = "unweighted"  # every sampled run counts once


class MixedBasisError(ValueError):
    """Raised when an aggregate would mix weighted and unweighted bases (R15)."""


@dataclass(frozen=True)
class Score:
    name: str
    value: Optional[float]
    basis: ScoreBasis
    n_runs: int
    detail: str = ""


def assert_homogeneous_basis(scores: Sequence[Score]) -> ScoreBasis:
    """R15 control: every score must share one basis, else fail LOUDLY.

    Returns the single shared basis. Raises `MixedBasisError` if the scores
    carry more than one distinct basis — the named defect this control exists
    to catch. Empty input is itself a failure (an aggregate of nothing is not a
    silent pass — fail-closed, R15).
    """
    if not scores:
        raise MixedBasisError("aggregate over zero scores is undefined (fail-closed)")
    bases = {s.basis for s in scores}
    if len(bases) != 1:
        names = ", ".join(f"{s.name}={s.basis.value}" for s in scores)
        raise MixedBasisError(
            f"refusing to aggregate scores of mixed basis ({names}); "
            "weighted and unweighted measures must never be conflated (R15, §4)"
        )
    return next(iter(bases))


def aggregate_scores(scores: Sequence[Score], reducer: Callable[[List[float]], float]) -> Score:
    """Reduce like-basis scores to one. Guarded by `assert_homogeneous_basis`.

    This is the ONLY sanctioned way to combine scores, and it can only ever
    combine scores that already share a basis. There is intentionally no path
    that reduces across bases.
    """
    basis = assert_homogeneous_basis(scores)
    values = [s.value for s in scores if s.value is not None]
    if not values:
        raise MixedBasisError("no defined score values to aggregate (fail-closed)")
    return Score(
        name="+".join(s.name for s in scores),
        value=reducer(values),
        basis=basis,
        n_runs=sum(s.n_runs for s in scores),
        detail=f"reduced {len(scores)} {basis.value} scores",
    )


@dataclass(frozen=True)
class ThreeScores:
    """The three §4 scores, kept SEPARATE. No blended scalar by construction."""

    robustness: Score
    commercial_ev: Score
    survival: Score

    def as_dict(self) -> dict:
        return {
            "robustness": asdict(self.robustness),
            "commercial_ev": asdict(self.commercial_ev),
            "survival": asdict(self.survival),
            "_r15_note": "three separate bases; never blended (weighted EV vs unweighted robustness/survival)",
        }


# --------------------------------------------------------------------------- #
# §3 the one-row manifest                                                     #
# --------------------------------------------------------------------------- #
@dataclass
class RunOutcomes:
    """The outcome half of a §3 ledger row."""

    survived: bool
    ev_gbp: Optional[float] = None
    gbp_per_tco2e: Optional[float] = None
    worst_cell_fidelity: Optional[float] = None
    death_cause: Optional[str] = None   # required iff not survived
    death_date: Optional[str] = None    # ISO date, required iff not survived
    # §6 is REGISTERED-not-built, but the authoritative ruling
    # (DIRECTOR_RULING_GENERATOR_ACTIVATION..., "confirmed this morning") directs:
    # "capture liquidity-minimum and cover-minimum per run FROM THE START" so the
    # §6 margin-of-survival design is computable later without a retrofit. These
    # are recorded from EVERY run (survivors included); the §6 metrics/breaking-
    # strain that consume them stay unbuilt (director-session gated).
    liquidity_headroom_min_gbp: Optional[float] = None   # min liquidity headroom reached in the run
    collateral_cover_min: Optional[float] = None         # min collateral cover ratio reached in the run

    def validate(self) -> None:
        if not self.survived and not self.death_cause:
            raise ValueError("a death must carry a cause (§3: 'cause and date if died')")


@dataclass
class RunManifest:
    """One row per run (§3). Every field the ruling names is present.

    `true_probability` and `population_seed`/`realised_cell_counts` are OPTIONAL
    at the type level because today's un-rotated, un-activated runs do not yet
    carry them (§1 activation and §2 rotation are not built). They are NOT
    silently defaulted to a number — a missing true-probability is `None` and
    COMMERCIAL EV refuses to weight a ledger that contains one (fail-loud),
    rather than pretending an unweighted row is weighted.
    """

    run_id: str
    code_sha: str
    curriculum_version: str
    world_scenario: str
    outcomes: RunOutcomes
    true_probability: Optional[float] = None       # the scenario's true-measure weight (§3, §2)
    population_seed: Optional[int] = None           # (§3)
    realised_cell_counts: dict = field(default_factory=dict)  # from the coverage report (§1.3, §3)
    generated_at: str = ""
    draw_population_enabled: bool = False            # was SE_DRAW_POPULATION on for this run?

    def to_row(self) -> dict:
        self.outcomes.validate()
        row = asdict(self)
        return row


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_REPO_ROOT, text=True
        ).strip()[:12]
    except Exception:
        return "unknown"


def _curriculum_version() -> str:
    try:
        meta = json.loads(_CURRICULUM_PATH.read_text()).get("_meta", {})
        return f"segmentation_curriculum_v{meta.get('version', '?')}"
    except Exception:
        return "unknown"


def build_manifest(
    world_scenario: str,
    outcomes: RunOutcomes,
    *,
    true_probability: Optional[float] = None,
    population_seed: Optional[int] = None,
    realised_cell_counts: Optional[dict] = None,
    draw_population_enabled: bool = False,
    code_sha: Optional[str] = None,
    curriculum_version: Optional[str] = None,
    generated_at: Optional[str] = None,
) -> RunManifest:
    """Assemble a §3 ledger row from a completed run's observables."""
    sha = code_sha or _git_sha()
    gen = generated_at or datetime.now(timezone.utc).isoformat()
    seed_tag = "static" if population_seed is None else str(population_seed)
    run_id = f"run-{sha[:8]}-{world_scenario}-{seed_tag}-{gen[:19]}"
    return RunManifest(
        run_id=run_id,
        code_sha=sha,
        curriculum_version=curriculum_version or _curriculum_version(),
        world_scenario=world_scenario,
        outcomes=outcomes,
        true_probability=true_probability,
        population_seed=population_seed,
        realised_cell_counts=realised_cell_counts or {},
        generated_at=gen,
        draw_population_enabled=draw_population_enabled,
    )


# --------------------------------------------------------------------------- #
# §3 retention policy + append                                               #
# --------------------------------------------------------------------------- #
def retention_class(manifest: RunManifest, *, survivor_sample_stride: int = 10) -> str:
    """Per §3 artifact-retention: what do we keep for this run?

    - every DEATH retained in FULL (rare, information-dense)
    - anything a fidelity trigger flags retained in full
    - a SAMPLE of survivors (every Nth by ledger position)
    - everything else: the ledger row only.

    The stride sample is DETERMINISTIC in the run_id (a stable hash), never a
    fresh random draw — replay-stable (C-S2).
    """
    if not manifest.outcomes.survived:
        return "full_death"
    wcf = manifest.outcomes.worst_cell_fidelity
    if wcf is not None and wcf < 0.5:   # a fidelity trigger flagged this run
        return "full_fidelity_flag"
    # deterministic survivor sample
    h = int.from_bytes(
        __import__("hashlib").sha256(manifest.run_id.encode()).digest()[:4], "big"
    )
    if h % max(1, survivor_sample_stride) == 0:
        return "full_survivor_sample"
    return "row_only"


def append_to_ledger(manifest: RunManifest, ledger_path: Optional[Path] = None) -> dict:
    """Append one row to the append-only JSONL ledger. Returns the row written."""
    path = Path(ledger_path) if ledger_path is not None else LEDGER_PATH
    row = manifest.to_row()
    row["_retention"] = retention_class(manifest)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def read_ledger(ledger_path: Optional[Path] = None) -> List[dict]:
    path = Path(ledger_path) if ledger_path is not None else LEDGER_PATH
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


# --------------------------------------------------------------------------- #
# §4 the three scores, computed from a set of ledger rows                     #
# --------------------------------------------------------------------------- #
def _ev(row: dict) -> Optional[float]:
    return (row.get("outcomes") or {}).get("ev_gbp")


def _survived(row: dict) -> bool:
    return bool((row.get("outcomes") or {}).get("survived"))


def robustness(rows: Sequence[dict], *, tail_fraction: float = 0.1) -> Score:
    """UNWEIGHTED, tail-focused development signal.

    The mean EV of the worst `tail_fraction` of runs (a CVaR-style tail), every
    run counting once regardless of its true probability. Deaths carry an EV of
    their realised (negative) value where present, else 0. This asks "how bad is
    the bad tail of what we were shown", not "what is it worth".
    """
    evs = sorted(_ev(r) if _ev(r) is not None else 0.0 for r in rows)
    n = len(evs)
    if n == 0:
        return Score("robustness", None, ScoreBasis.UNWEIGHTED, 0, "no runs")
    k = max(1, math.ceil(tail_fraction * n))
    tail = evs[:k]
    return Score(
        "robustness", sum(tail) / len(tail), ScoreBasis.UNWEIGHTED, n,
        f"mean EV of worst {k}/{n} runs (unweighted tail)",
    )


def commercial_ev(rows: Sequence[dict]) -> Score:
    """PROBABILITY-WEIGHTED EV by the true measure.

    Weights each row by its `true_probability`. If ANY row lacks a
    true_probability, this fails LOUDLY — an unweighted row cannot silently sit
    in a weighted aggregate (the exact conflation §4's R15 clause forbids).
    """
    rows = list(rows)
    if not rows:
        return Score("commercial_ev", None, ScoreBasis.WEIGHTED, 0, "no runs")
    missing = [r.get("run_id", "?") for r in rows if r.get("true_probability") is None]
    if missing:
        raise MixedBasisError(
            "COMMERCIAL EV needs a true_probability on every row; missing on "
            f"{len(missing)} row(s) e.g. {missing[:3]} — cannot weight an "
            "unweighted row into a weighted score (R15, §4)"
        )
    wsum = sum(float(r["true_probability"]) for r in rows)
    if wsum <= 0:
        raise MixedBasisError("true_probability weights sum to <= 0 (fail-closed)")
    ev = sum(float(r["true_probability"]) * (_ev(r) or 0.0) for r in rows) / wsum
    return Score(
        "commercial_ev", ev, ScoreBasis.WEIGHTED, len(rows),
        "true-probability-weighted mean EV",
    )


def survival(rows: Sequence[dict]) -> Score:
    """UNWEIGHTED worst-case: does the company die ANYWHERE in the sampled set?

    Value 1.0 iff every sampled run survived, else 0.0 (a single death fails the
    worst-case test). Probability is deliberately ignored — a rare death still
    fails survival.
    """
    rows = list(rows)
    if not rows:
        return Score("survival", None, ScoreBasis.UNWEIGHTED, 0, "no runs")
    deaths = [r for r in rows if not _survived(r)]
    value = 0.0 if deaths else 1.0
    detail = "survives everywhere" if not deaths else (
        f"dies in {len(deaths)}/{len(rows)} (e.g. "
        f"{[d.get('run_id') for d in deaths[:3]]})"
    )
    return Score("survival", value, ScoreBasis.UNWEIGHTED, len(rows), detail)


def three_scores(rows: Sequence[dict]) -> ThreeScores:
    """Compute all three §4 scores from the same ledger rows, kept separate."""
    return ThreeScores(
        robustness=robustness(rows),
        commercial_ev=commercial_ev(rows),
        survival=survival(rows),
    )
