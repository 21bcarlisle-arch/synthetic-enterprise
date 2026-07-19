"""Fidelity grid-scorer -- the measurement core of the Epoch-2 atom-G
fidelity-evidence machinery (atom **G1**, `G_data_learning` lane, HARNESS-side).

Builds the three-measure grid the director's addendum and the campaign
DISCOVER docs specify, **on the IMPROVED constructs** (the advisor's
challenge-response, not the raw sketch):

    1. LIFT over the BEST-OF-a-naive-FAMILY (never a single frozen baseline --
       `EPOCH2_G_CONSTRUCT_CHALLENGE_RESPONSE.md` measure-1 sharpen).
    2. Worst-**q%** CVaR tail-mean over the archetype x regime grid, which
       GENERALISES the sketch's pure MAX (`q=0` recovers MAX exactly --
       CONSTRUCT_CHALLENGE measure-2 sharpen), with the MAP OF IGNORANCE
       (unmeasured cells score top severity, fail-open, never hidden) as a
       first-class output.
    3. CRN-gated ABLATION Delta of a coupling -- a Delta computed without proven
       substream isolation is REJECTED as invalid, never reported as a number
       (`EPOCH2_G_FIDELITY_EVIDENCE_MACHINERY_DISCOVER.md` S1.3 / S5).

Design sources (read this pass, no network):
    docs/design/EPOCH2_G_FIDELITY_EVIDENCE_MACHINERY_DISCOVER.md  (S1-S5)
    docs/design/EPOCH2_G_CONSTRUCT_CHALLENGE_RESPONSE.md          (the sharpens)
    docs/design/EPOCH2_A_SCOPE_OF_NEED_SCORING_FRAME_DISCOVER.md  (S3, the grid
        + worst-cell rule + FAIL-OPEN/TAUTOLOGY/FAIL-SILENT guards this module
        inherits and generalises)

THE WALL (CLAUDE.md Architectural Laws). This is HARNESS code, same standing as
`background/gap_metric.py` / `background/coupled_triad.py`: it sits OUTSIDE the
epistemic wall by design. It never imports `sim.*` / `simulation.*` /
`company.*` -- it operates purely on already-computed per-cell evidence numbers
(errors, gaps, outcomes) handed to it by callers on either side of the wall.
It NEVER decides what the company observes; it only scores the belief-vs-truth
gap machinery that other atoms feed it.

R12 anti-goal-seek: the three measures computed here are DIAGNOSTICS. Nothing
in this module may be tuned toward a target reading, and this module never
adjusts a naive baseline, a `q`, or a decorative threshold to flatter a score
-- those are R13-curriculum / R10-simplification constants, changed only for
stated reasons, never in response to an unfavourable measurement (see the
constants block below, each with its provenance note).

R10 simplifications asserted in this module (registered here, not hidden):
    * `Q_DEFAULT_TAIL = 0.10` -- the worst-decile CVaR tail fraction. Atom A
      S3.3 / atom G S1.2 both flag the honest value needs a real run's
      per-cell noise floor; ship a small default, declare it, let BUILD widen
      on evidence (R4), never silently.
    * `IGNORANCE_FLOOR_NO_MEASURED = 1.0` -- when a grid has ZERO measured
      cells to be ">= the worst measured cell" against, an unmeasured cell's
      severity floor is the "no-better-than-blind" ceiling (matches the
      gap_metric.py convention: gap=1 <=> blind). Asserted, not derived.
    * `ABLATION_DECORATIVE_EPS = 1e-9` -- the |Delta| <= eps threshold below
      which an ablation verdict reads "decorative". A numerical-noise floor,
      not a physics constant; BUILD should replace with a real measured noise
      floor once CRN runs exist (atom G S1.3 note).
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# R10-registered constants (see module docstring). Changed only for a stated
# fidelity/noise-floor reason (R4/R13), never to move a measurement (R12).
# ---------------------------------------------------------------------------

Q_DEFAULT_TAIL: float = 0.10
IGNORANCE_FLOOR_NO_MEASURED: float = 1.0
ABLATION_DECORATIVE_EPS: float = 1e-9

_IGNORANCE_KINDS = ("missing_physics", "untested")

# Private tie-break epsilon (not an R10 values call -- a pure mechanism so an
# unmeasured cell reads STRICTLY worse than a tied measured cell and therefore
# always wins the worst-cell argmax; ">= the worst measured cell" per atom A
# S3.4 is satisfied either way, this only makes the blind spot visibly loudest
# rather than losing a tie to insertion order).
_IGNORANCE_TIEBREAK_EPS: float = 1e-9


# ===========================================================================
# MEASURE 1 -- lift over the BEST-OF-a-naive-FAMILY
# ===========================================================================

@dataclass(frozen=True)
class NaiveBaseline:
    """One member of a driver's naive-baseline FAMILY -- a hash-pinned,
    versioned artefact (atom G S1.1's "un-gameable: FROZEN + INDEPENDENT").

    `content_hash` is derived from (`baseline_id`, `version`, `definition`) so
    a baseline that changes its definition without bumping `version` is
    caught by hash mismatch (`family_hash` below), never silently accepted --
    this is the mechanism half of "changing a baseline bumps its version and
    invalidates every prior lift computed against the old hash" (S1.1.1).
    """

    baseline_id: str
    version: int
    definition: str  # human-readable spec of what this baseline predicts
    content_hash: str = field(init=False, compare=False)

    def __post_init__(self) -> None:
        payload = f"{self.baseline_id}|v{self.version}|{self.definition}"
        h = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        object.__setattr__(self, "content_hash", h)


def family_hash(family: Sequence[NaiveBaseline]) -> str:
    """A stable hash over an entire naive-baseline FAMILY (order-independent),
    so a family's composition (not just one member) is auditable."""
    parts = sorted(f"{b.baseline_id}:{b.version}:{b.content_hash}" for b in family)
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


# The five driver families named in atom G S1.1, each shipped as a FAMILY (the
# advisor-challenge sharpen) rather than one frozen baseline. BUILD grounds the
# exact per-family member list against published UK-supplier/actuarial
# practice (S7 item 2); this registry is the hash-pinned mechanism, not the
# final content -- adding/removing/re-defining a member bumps its `version`.
NAIVE_BASELINE_FAMILIES: Dict[str, Tuple[NaiveBaseline, ...]] = {
    "weather_cascade": (
        NaiveBaseline("independence", 1,
                      "draw each variable from its own marginal, couplings off (L=1)"),
        NaiveBaseline("climatology", 1,
                      "predict the long-run seasonal-day climatological mean"),
        NaiveBaseline("persistence", 1,
                      "predict yesterday's value unchanged"),
    ),
    "affordability_collections": (
        NaiveBaseline("flat_population_prior", 1,
                      "predict the book-average affordability band for every customer"),
        NaiveBaseline("last_observed_band", 1,
                      "predict the customer's own most-recently-observed band"),
    ),
    "demand_shape": (
        NaiveBaseline("single_average_pc_profile", 1,
                      "one smooth load shape (book-average PC profile), no per-customer convexity"),
        NaiveBaseline("persistence", 1,
                      "predict last settlement period's read unchanged"),
    ),
    "price_incidence": (
        NaiveBaseline("uniform_exposure", 1,
                      "assume every customer carries identical price risk"),
        NaiveBaseline("contract_type_only", 1,
                      "predict exposure from contract type alone (fixed vs flex), ignore volume"),
    ),
    "export_self_gen": (
        NaiveBaseline("monotone_importer", 1,
                      "assume volume >= 0, supplier always the seller"),
    ),
}


@dataclass(frozen=True)
class LiftResult:
    """Measure-1 output for one (driver, cell). `err_best_naive` is the MIN
    over the naive FAMILY (best-of-family, S1.1 sharpen) -- never a single
    baseline -- so lift cannot be inflated by only reporting a weak family
    member."""

    driver_family: str
    cell_id: str
    err_model: float
    err_best_naive: float
    best_baseline_id: str
    commercial_weight: float
    lift: float


def best_of_family_error(err_by_baseline: Mapping[str, float]) -> Tuple[str, float]:
    """`err_best_naive(cell) = min over b in NAIVE_FAMILY of err_b(cell)`
    (atom G S1.1 sharpened by the construct-challenge doc). FAIL-OPEN: an
    empty family error map has no defensible minimum -- raise loud rather than
    silently returning 0 (which would fabricate an unbeatable baseline)."""
    if not err_by_baseline:
        raise ValueError(
            "best_of_family_error: empty naive-baseline-family error map -- "
            "a family with no measured member cannot produce a lift"
        )
    best_id = min(err_by_baseline, key=lambda k: err_by_baseline[k])
    return best_id, float(err_by_baseline[best_id])


def cell_lift(driver_family: str, cell_id: str, err_model: float,
              err_by_baseline: Mapping[str, float],
              commercial_weight: float = 1.0) -> LiftResult:
    """Measure 1: `lift(m, cell) = [err_best_naive(cell) - err_model(m, cell)]
    x commercial_weight(cell)`, with `err_best_naive` the BEST-OF-FAMILY
    minimum (S1.1 sharpen), never a single baseline.

    `commercial_weight` defaults to 1.0 (the equal-weight null the DISCOVER
    doc ships pending the director's values call, S1.1/S6 item 1) -- this
    function never invents a weight.
    """
    best_id, err_best = best_of_family_error(err_by_baseline)
    lift = (err_best - float(err_model)) * float(commercial_weight)
    return LiftResult(
        driver_family=driver_family, cell_id=cell_id, err_model=float(err_model),
        err_best_naive=err_best, best_baseline_id=best_id,
        commercial_weight=float(commercial_weight), lift=lift,
    )


def single_baseline_lift(err_model: float, err_single_baseline: float,
                          commercial_weight: float = 1.0) -> float:
    """The UN-improved construct (lift against exactly one named baseline) --
    exposed only so the R15 mutation test can prove best-of-family caps what
    a gamed single-weak-baseline report would show. Not for production use:
    production lift computation is always `cell_lift` (best-of-family)."""
    return (float(err_single_baseline) - float(err_model)) * float(commercial_weight)


# ===========================================================================
# MEASURE 2 -- worst-q% CVaR (generalises MAX) + the MAP OF IGNORANCE
# ===========================================================================

@dataclass(frozen=True)
class CellEvidence:
    """One archetype x regime cell (atom A S3.1's 5x3 grid) as fed to the
    grid-scorer. `measured=False` cells carry no `gap` -- they are the map of
    ignorance's raw material, never silently dropped from the grid."""

    cell_id: str
    measured: bool
    gap: Optional[float] = None
    ignorance: Optional[str] = None  # "missing_physics" | "untested"; required iff not measured

    def __post_init__(self) -> None:
        if self.measured:
            if self.gap is None:
                raise ValueError(f"{self.cell_id}: measured=True requires a gap value")
        else:
            if self.gap is not None:
                raise ValueError(f"{self.cell_id}: measured=False must not carry a gap value")
            if self.ignorance not in _IGNORANCE_KINDS:
                raise ValueError(
                    f"{self.cell_id}: unmeasured cell must declare ignorance in "
                    f"{_IGNORANCE_KINDS}, got {self.ignorance!r}"
                )


@dataclass(frozen=True)
class IgnoranceEntry:
    cell_id: str
    ignorance: str


@dataclass(frozen=True)
class GridScore:
    """The full measure-2 output: the resolved per-cell severity surface, the
    worst cell, the CVaR grid aggregate, and the map of ignorance -- always
    present (possibly empty), never omitted (S1.2's "first-class view")."""

    q: float
    severities: Dict[str, float]
    worst_cell: str
    worst_severity: float
    grid_aggregate: float
    tail_k: int
    map_of_ignorance: Tuple[IgnoranceEntry, ...]


def _resolve_severity(cells: Sequence[CellEvidence]) -> Dict[str, float]:
    """Measured cells score their own gap. Unmeasured cells score
    ``>= the worst measured cell`` (atom A S3.4 FAIL-OPEN, inherited
    verbatim) -- concretely, tied to the worst MEASURED gap, or the
    `IGNORANCE_FLOOR_NO_MEASURED` R10 constant if nothing is measured at all.
    This guarantees an unmeasured cell can never read as good and can never
    silently exit the worst-cell tail."""
    measured_gaps = [c.gap for c in cells if c.measured]
    floor = max(measured_gaps) if measured_gaps else IGNORANCE_FLOOR_NO_MEASURED
    out: Dict[str, float] = {}
    for c in cells:
        out[c.cell_id] = (
            float(c.gap) if c.measured else float(floor) + _IGNORANCE_TIEBREAK_EPS
        )
    return out


def build_map_of_ignorance(cells: Sequence[CellEvidence]) -> Tuple[IgnoranceEntry, ...]:
    """Every unmeasured cell, unconditionally -- the honest, first-class view
    (S1.2). Never filtered, never summarised away."""
    return tuple(
        IgnoranceEntry(cell_id=c.cell_id, ignorance=c.ignorance)
        for c in cells if not c.measured
    )


def assert_map_of_ignorance_complete(
    cells: Sequence[CellEvidence],
    map_of_ignorance: Sequence[IgnoranceEntry],
) -> None:
    """R15 completeness guard: every unmeasured cell in `cells` MUST appear in
    `map_of_ignorance`. Raises loud (FAIL-OPEN doctrine: an omitted blind cell
    is exactly the defect this measure exists to catch) rather than returning
    a bool a caller could ignore."""
    expected = {c.cell_id for c in cells if not c.measured}
    present = {e.cell_id for e in map_of_ignorance}
    missing = expected - present
    if missing:
        raise AssertionError(
            "map-of-ignorance INCOMPLETE -- unmeasured cell(s) omitted from the "
            f"honest view (silently hidden blind spot): {sorted(missing)}"
        )


def grid_cvar(severities: Sequence[float], q: float = Q_DEFAULT_TAIL) -> Tuple[float, int, List[float]]:
    """The worst-q%-tail-mean (CVaR / expected-shortfall) aggregate that
    GENERALISES pure MAX (CONSTRUCT_CHALLENGE measure-2 sharpen).

        q == 0  -> exactly the single worst cell (k=1), i.e. pure MAX --
                   the advisor's original sketch, recovered exactly.
        0 < q <= 1 -> mean of the worst ceil(q * n) cells; good cells never
                   enter the tail and so never dilute it.

    Returns (aggregate, k, tail) so a caller/test can inspect exactly which
    cells were averaged. FAIL-OPEN: an empty `severities` sequence has no
    defensible worst cell -- raise loud rather than return e.g. 0.0 (which
    would read as a perfect, leak-shaped score)."""
    if not severities:
        raise ValueError("grid_cvar: empty severity sequence -- nothing to score")
    if q < 0:
        raise ValueError(f"grid_cvar: q must be >= 0, got {q}")
    n = len(severities)
    ranked = sorted(severities, reverse=True)
    k = 1 if q <= 0 else max(1, math.ceil(q * n))
    k = min(k, n)
    tail = ranked[:k]
    aggregate = sum(tail) / len(tail)
    return aggregate, k, tail


def score_grid(cells: Sequence[CellEvidence], q: float = Q_DEFAULT_TAIL) -> GridScore:
    """Compose measure 2 end-to-end: resolve severities (fail-open on
    ignorance), compute the worst-q% CVaR aggregate, and attach the map of
    ignorance as a first-class field on the result (never a side channel a
    caller can drop)."""
    if not cells:
        raise ValueError("score_grid: empty grid -- nothing to score")
    severities = _resolve_severity(cells)
    ordered_ids = list(severities.keys())
    values = [severities[cid] for cid in ordered_ids]
    aggregate, k, _tail = grid_cvar(values, q=q)
    worst_id = max(ordered_ids, key=lambda cid: severities[cid])
    ignorance_map = build_map_of_ignorance(cells)
    assert_map_of_ignorance_complete(cells, ignorance_map)
    return GridScore(
        q=q, severities=severities, worst_cell=worst_id,
        worst_severity=severities[worst_id], grid_aggregate=aggregate,
        tail_k=k, map_of_ignorance=ignorance_map,
    )


# ===========================================================================
# MEASURE 3 -- CRN-gated ablation Delta
# ===========================================================================

class InvalidAblation(ValueError):
    """Raised when an ablation Delta is requested without proven CRN
    substream isolation, or on a FAIL-SILENT/FAIL-OPEN input (empty samples,
    NaN outcomes). Per S1.3/S5: a Delta computed this way is NOISE, not
    evidence, and must never be reported as a plain number -- it is a FAILED
    check, not a skipped-green one."""


@dataclass(frozen=True)
class AblationResult:
    coupling_id: str
    delta_worst_cell: float
    delta_by_cell: Dict[str, float]
    crn_substream_isolated: bool
    verdict: str  # "load_bearing" | "decorative"


def compute_ablation(
    coupling_id: str,
    outcome_live: Mapping[str, float],
    outcome_cut: Mapping[str, float],
    *,
    crn_substream_isolated: bool,
    decorative_eps: float = ABLATION_DECORATIVE_EPS,
) -> AblationResult:
    """Measure 3: ``ablation_Delta(k, cell) = outcome(cell | k LIVE) -
    outcome(cell | k CUT)`` (atom G S1.3), gated by CRN/substream isolation.

    **CRN is mandatory, not optional** (S1.3/S5 killer-mutation-B): if
    `crn_substream_isolated` is not True, the Delta is Monte-Carlo noise, not
    a causal reading, and this function REJECTS it (`InvalidAblation`) rather
    than returning a number a caller might mistake for evidence.

    FAIL-OPEN/FAIL-SILENT: empty or mismatched cell sets, or any NaN outcome,
    is a FAILED check (raises), never a silently-dropped cell or a 0.0
    stand-in.

    Verdict rule (S1.3): `|Delta| <= decorative_eps` everywhere -> the
    coupling is DECORATIVE (cutting it changes nothing -- flagged honestly,
    never hidden and never silently kept as if load-bearing); otherwise
    LOAD_BEARING, ranked by the worst-cell Delta.
    """
    if not crn_substream_isolated:
        raise InvalidAblation(
            f"{coupling_id}: ablation Delta requested without proven CRN "
            "substream isolation -- Delta is seed-noise-dominated, not causal "
            "evidence (S1.3 killer-mutation-B). REJECTED, not reported."
        )
    if not outcome_live or not outcome_cut:
        raise InvalidAblation(
            f"{coupling_id}: empty LIVE or CUT outcome sample -- an "
            "unavailable run is a FAILED ablation check, not a skip."
        )
    if set(outcome_live) != set(outcome_cut):
        raise InvalidAblation(
            f"{coupling_id}: LIVE and CUT outcome cell sets differ -- "
            f"live={sorted(outcome_live)} cut={sorted(outcome_cut)}"
        )

    delta_by_cell: Dict[str, float] = {}
    for cell_id in outcome_live:
        live_v = float(outcome_live[cell_id])
        cut_v = float(outcome_cut[cell_id])
        if math.isnan(live_v) or math.isnan(cut_v):
            raise InvalidAblation(
                f"{coupling_id}: NaN outcome on cell {cell_id!r} -- FAIL loud, "
                "never a silent skip."
            )
        delta_by_cell[cell_id] = live_v - cut_v

    # Delta worst-cell = MAX-gap(LIVE) - MAX-gap(CUT), i.e. q=0 CVaR (pure
    # MAX) applied to each side, then differenced (S1.3's headline metric).
    live_worst, _, _ = grid_cvar(list(outcome_live.values()), q=0.0)
    cut_worst, _, _ = grid_cvar(list(outcome_cut.values()), q=0.0)
    delta_worst_cell = live_worst - cut_worst

    verdict = "decorative" if all(
        abs(d) <= decorative_eps for d in delta_by_cell.values()
    ) else "load_bearing"

    return AblationResult(
        coupling_id=coupling_id, delta_worst_cell=delta_worst_cell,
        delta_by_cell=delta_by_cell, crn_substream_isolated=True, verdict=verdict,
    )
