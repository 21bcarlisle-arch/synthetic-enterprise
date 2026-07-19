"""Scope-of-need SCORING FRAME (Epoch-2 campaign atom A).

WHAT THIS IS. The objective function the whole campaign is measured against: a
5x3 grid of {A1..A5 archetypes} x {G1,G2,G3 regimes} spanning the *range of
need*, whose fidelity is the **WORST-EXPLAINED CELL, not the population
average** (director's requirement, verbatim: "score against the worst-explained
cell of a grid that spans the range of need"). Design: EPOCH2_A_SCOPE_OF_NEED_
SCORING_FRAME_DISCOVER.md (2c3d7c03f).

HOW. This module is the GRID + the worst-cell rule. It owns no gap machinery of
its own -- it composes the already-built grid-scorer (atom G1,
`fidelity_grid_scorer`), which implements the FAIL-OPEN severity resolution
(an unmeasured cell scores >= the worst measured cell, never drops out of the
MAX), the CVaR-generalises-MAX aggregate (q==0 -> pure MAX), and the
first-class map of ignorance. Atom A's job is the SEMANTICS: which 15 cells
exist, what physics each stresses, and the reading rules (worst cell, middle-
to-edge spread, leak guard) the campaign reports.

WALL / METHOD. The frame consumes per-cell belief-vs-truth gaps handed to it by
the harness (SIM answer-key vs observable-only company output, computed
elsewhere on either side of the wall). It NEVER lets the company read SIM
truth; it only structures and scores gaps other atoms measure. Cells directly
comparable because each gap is a fraction of its own no-skill baseline
(COUPLED_TRIAD S1.2): 0 = perfect (structurally unreachable through the wall --
reaching it is a LEAK, a defect), 1 = no better than blind, >1 = worse.

R12 anti-goal-seek. FIDELITY_SCORE is a DIAGNOSTIC. Nothing here is tuned toward
a reading; the two values-call defaults below are R10 simplifications changed
only for a stated reason, never to move a score.

R10 VALUES-CALLS asserted here (conservative defaults, marked, batched for the
director per EPOCH2_VALUES_CALLS_BATCH_1 -- NOT invented, NOT self-approved):
    * WORST_CELL_Q = 0.0  -- pure MAX, exactly the director's written rule
      "FIDELITY_SCORE = MAX over all in-grid cells". The CVaR top-k smoother
      (atom A S3.3) is AVAILABLE via the `q` parameter for when a real run's
      per-cell noise makes the raw MAX jumpy, but the DEFAULT is the strict,
      un-smoothed worst cell (the conservative choice: hardest to pass, never
      dilutes the worst edge). OPEN director call: adopt a smoother and at what
      declared k, read from real per-cell variance (R4), never tuned to flatter.
    * EQUAL_CELL_WEIGHTING = True -- every in-grid cell counts equally for the
      worst-cell rule regardless of its book share pi (A3 at 2% and A5 at 60%
      weigh the same). OPEN director call: equal-cell vs harm-weighted worst
      cell. Conservative default = equal (no harm weighting asserted by the
      agent; the weights are the director's per one-way-door cat-6).

R15. The worst-cell rule is a CONTROL and must be able to FIRE on its own
defects -- proven by mutation tests (a 14-good/1-blind model must score ~blind,
not ~good; a middle-only-green model must not report clean; an untested cell
must not silently exit the MAX; a gap<=0 leak must flag red not green).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from background.fidelity_grid_scorer import (
    CellEvidence,
    GridScore,
    score_grid,
)

# ---------------------------------------------------------------------------
# R10-registered values-call defaults (see module docstring). Changed only for
# a stated fidelity reason (R4/R13), never to move a measurement (R12).
# ---------------------------------------------------------------------------
WORST_CELL_Q: float = 0.0          # pure MAX == director's written rule
EQUAL_CELL_WEIGHTING: bool = True  # every in-grid cell equal (harm-weight = open director call)

# A gap this small is structurally unreachable through the epistemic wall --
# reaching it means the company's belief could see the SIM's truth (a leak),
# which is a DEFECT, not a triumph (S3.4 TAUTOLOGY guard). Flagged, not scored good.
LEAK_GAP_EPS: float = 1e-9


# ===========================================================================
# The grid axes -- 5 archetypes x 3 regimes (atom A S1.2 / S2)
# ===========================================================================

@dataclass(frozen=True)
class Archetype:
    """One row of the grid: an archetype that stresses ONE distinct physics the
    comfortable middle does not (A5 is the reference anchor, stresses none)."""

    id: str
    label: str
    stresses: str
    is_reference: bool = False


@dataclass(frozen=True)
class Regime:
    """One column of the grid: a macro-state stressing an orthogonal price/tail
    physics (S2: calm/soft level, sustained crisis level-shift, acute joint tail)."""

    id: str
    label: str
    stresses: str


# The five archetypes -- the director's five named stressors + the A5 reference
# anchor the worst-cell rule needs (without it "great on the middle" has nothing
# to be measured against). Small set, one physics each (S1.2 merges rejected).
ARCHETYPES: Tuple[Archetype, ...] = (
    Archetype("A1", "Affordability-stressed / prepayment household",
              "collections & affordability: arrears as a hidden budget meeting a shock; "
              "can't-pay vs won't-pay; self-rationing invisible in payment data"),
    Archetype("A2", "Unusual-consumption-shape household (electrified heat + EV)",
              "demand-shape & weather coupling: winter-peaked convex load; volume overshoot vs "
              "hedged EAC exactly in the cold-and-still tail; cost-to-serve is shape-driven"),
    Archetype("A3", "Export & self-generation prosumer (PV +/- battery)",
              "net-settlement & sign-flip: reduced/volatile import, occasional net-export; "
              "feed-in is a supplier cash outflow; response runs opposite a pure consumer"),
    Archetype("A4", "Pass-through commercial (I&C half-hourly, flex / pass-through)",
              "where a price move bites and doesn't: wholesale risk sits with the customer not "
              "the supplier; discrete SME/I&C failure (bad debt + lost supply point), not a slide"),
    Archetype("A5", "The comfortable middle (reference) -- stable DD-paying domestic",
              "the calibration anchor / anti-archetype: stresses no edge physics by design, so the "
              "middle-to-edge spread is explicit; A5 alone green != pass",
              is_reference=True),
)

# The three regimes -- orthogonal price/tail physics (S2 orthogonality argument:
# low&flat / high&sustained level-shift / acute correlated joint tail).
REGIMES: Tuple[Regime, ...] = (
    Regime("G1", "Calm / soft market",
           "low & flat wholesale: the baseline; edge physics present but unstressed by price"),
    Regime("G2", "Crisis / sustained price spike (2021-22 gas-crisis shape)",
           "chronic level-shift: hedge exhaustion, bill-shock->arrears, who-eats-the-spike, "
           "affordability collapse -- level, sustained"),
    Regime("G3", "Acute correlated tail (cold-and-still / dunkelflaute)",
           "acute co-movement / joint tail: demand up, wind down, residual/price/imbalance up "
           "simultaneously; the volume-price double hit -- acute, correlated, mean-reverting"),
)

# Ignorance kind for a cell not yet populated by the SIM cast / with no coupling
# registered. The current cast populates A4/A5 cohorts; A1/A2/A3 are new scoring
# cases (S1.1, S5) -- registered as simplifications, NEVER silently dropped.
_DEFAULT_IGNORANCE = "untested"


def grid_cell_ids() -> Tuple[str, ...]:
    """The canonical 15 cell ids, archetype-major (`A2_G3` = shape x acute tail)."""
    return tuple(f"{a.id}_{g.id}" for a in ARCHETYPES for g in REGIMES)


def is_reference_cell(cell_id: str) -> bool:
    """True for the A5 (comfortable-middle) reference row -- the anchor the
    middle-to-edge spread is measured from, never itself the headline."""
    return cell_id.split("_", 1)[0] == "A5"


# ===========================================================================
# The frame score
# ===========================================================================

@dataclass(frozen=True)
class ScopeOfNeedScore:
    """The frame's verdict. `fidelity_score` is THE headline -- the worst cell
    (S3.3), never the mean. Companion diagnostics travel alongside it, never
    replace it (S3.3): the worst cell to fix, the middle-to-edge spread (the
    'explains the middle not the edges' pathology made numeric), any wall
    leaks, and the full per-cell surface for the Proof door."""

    fidelity_score: float                       # worst in-grid cell severity (lower is better)
    worst_cell: str
    q: float
    middle_to_edge_spread: float                # MAX(edge severities) - mean(A5 severities)
    grid_aggregate: float                        # the CVaR aggregate at q (==fidelity_score when q==0)
    severities: Dict[str, float]
    all_measured: bool                           # every one of the 15 cells has a real gap
    leaks: Tuple[str, ...]                        # cells with gap <= LEAK_GAP_EPS (wall-leak suspects)
    untested_cells: Tuple[str, ...]
    clean: bool                                  # all measured AND no leak -> a headline can be trusted


def build_grid_cells(
    gaps: Mapping[str, float],
    *,
    ignorance: Optional[Mapping[str, str]] = None,
) -> List[CellEvidence]:
    """Build all 15 CellEvidence for the canonical grid from a partial map of
    measured `gaps` (cell_id -> gap). A cell absent from `gaps` is UNMEASURED
    (never dropped) -- it becomes a map-of-ignorance entry that G1's fail-open
    severity scores as >= the worst measured cell. `ignorance` optionally names
    the kind ('missing_physics'|'untested') per cell; default 'untested'.

    Unknown cell ids in `gaps` are a caller error (a typo would silently create
    a 16th cell and dilute the grid) -- raised loud, not ignored."""
    ig = dict(ignorance or {})
    valid = set(grid_cell_ids())
    unknown = set(gaps) - valid
    if unknown:
        raise ValueError(
            f"gaps names cell id(s) not in the 5x3 grid: {sorted(unknown)} "
            f"(valid: {sorted(valid)})"
        )
    cells: List[CellEvidence] = []
    for cid in grid_cell_ids():
        if cid in gaps:
            cells.append(CellEvidence(cell_id=cid, measured=True, gap=float(gaps[cid])))
        else:
            cells.append(CellEvidence(
                cell_id=cid, measured=False,
                ignorance=ig.get(cid, _DEFAULT_IGNORANCE),
            ))
    return cells


def _middle_to_edge_spread(severities: Mapping[str, float]) -> float:
    """MAX(edge cell severities) - mean(A5 reference severities) (S3.3): the
    'explains the middle, not the edges' pathology as a number. A large positive
    spread is that exact pathology. Defined only when both sides are non-empty;
    0.0 when there are no edge cells (structurally there always are)."""
    edge = [s for cid, s in severities.items() if not is_reference_cell(cid)]
    mid = [s for cid, s in severities.items() if is_reference_cell(cid)]
    if not edge or not mid:
        return 0.0
    return max(edge) - (sum(mid) / len(mid))


def score_scope_of_need(
    gaps: Mapping[str, float],
    *,
    q: float = WORST_CELL_Q,
    ignorance: Optional[Mapping[str, str]] = None,
) -> ScopeOfNeedScore:
    """Score the frame from a partial map of measured per-cell gaps.

    The headline `fidelity_score` is the WORST cell (q==0 -> pure MAX, the
    director's rule). An unmeasured OR unavailable cell cannot silently exit the
    worst-cell tail (G1 fail-open), so a frame with any untested in-grid cell
    can never report a clean headline (`clean=False`). A gap <= LEAK_GAP_EPS is
    a suspected wall leak (perfect is structurally unreachable through the wall)
    -- flagged, and `clean=False`, never celebrated."""
    cells = build_grid_cells(gaps, ignorance=ignorance)
    gs: GridScore = score_grid(cells, q=q)

    untested = tuple(sorted(e.cell_id for e in gs.map_of_ignorance))
    all_measured = not untested
    leaks = tuple(sorted(
        cid for cid, s in gs.severities.items() if s <= LEAK_GAP_EPS
    ))
    clean = all_measured and not leaks

    return ScopeOfNeedScore(
        fidelity_score=gs.worst_severity,
        worst_cell=gs.worst_cell,
        q=q,
        middle_to_edge_spread=_middle_to_edge_spread(gs.severities),
        grid_aggregate=gs.grid_aggregate,
        severities=dict(gs.severities),
        all_measured=all_measured,
        leaks=leaks,
        untested_cells=untested,
        clean=clean,
    )
