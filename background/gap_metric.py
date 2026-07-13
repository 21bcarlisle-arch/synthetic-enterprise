"""COUPLED-TRIAD belief-vs-truth GAP computation -- the WRITE side of the
coupled triad (atom A6_coupled_triad_gap_metric, director P0
BUILD_THE_BACKLOG.md).

`background/coupled_triad.py` is the READ side: it gates world-atom L3 BUILD
draws on whether a non-null gap exists in the ledger. THIS module is the WRITE
side: given a coupled pair (a WORLD/SIM atom holding the hidden truth theta, and
a COMPANY twin holding a belief/action b over a population P), it computes the
pair's normalised gap per COUPLED_TRIAD_DESIGN.md section 1 and writes the entry
into `docs/observability/coupled_gap_ledger.json` via the existing contract.

THE WALL (CLAUDE.md Architectural Laws). This is HARNESS code -- it sits OUTSIDE
the epistemic wall by design and is the ONLY layer permitted to hold theta and b
side by side (design section 1.3). It reads the hidden SIM truth AND the
company's observable-only belief to compute the GAP. It NEVER writes theta or the
gap back into any company/ path; the company never sees its own score. Callers
must pass theta already extracted SIM-side and b already computed COMPANY-side --
this module does not reach across the wall itself.

THE GAP, in one line (design section 1.2):

    gap(w, c) = raw_gap(w, c) / g0(w)

normalised to a NO-SKILL baseline g0 (majority-class / blind prior) so the
reading is identical for every pair:

    gap = 0   -> perfect recovery of the hidden truth. For a wall-respecting pair
                this is structurally UNREACHABLE -- reaching it means the
                observables leaked theta (an epistemic-wall violation), a defect
                not a triumph.
    gap = 1   -> the company does no better than the blind prior. Not coping.
    0<gap<1   -> learned some, not all. The honest steady state.
    gap > 1   -> worse than blind (actively harmful model). Red.

METRIC FAMILIES (design section 1.4), all implemented here:
    (a) classification  -- cost-weighted 2x2 ability x willingness error (W2_7)
    (b) attribution     -- |d_naive - d_true| / |d_naive|, the DD confound (W2_10)
    (c) belief          -- total-variation distance TV(belief, truth) (W2_2/budget)
    (d) detection       -- detection-rate + false-negative-harm (W2_8 self-rationing)

R13 CURRICULUM (director-authored, NEVER agent-tuned toward a gap number). The
harm-cost weights below are the director-signed 8:1 ratio. They are read as a
CONSTANT. This module MUST NOT adjust them to move a gap toward any target
(CLAUDE.md R12 anti-goal-seek / R13 curriculum wall).

DETERMINISM (C-S2). No wall-clock, no unseeded randomness. `measured_at` and
`run_git_commit` are passed IN by the caller (default None) -- this module never
calls a clock. The optional bootstrap CI seeds a numpy Generator from a NAMED RNG
substream so a resample is reproducible and cannot perturb any other subsystem.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

from background.coupled_triad import GAP_LEDGER_PATH

# ---------------------------------------------------------------------------
# R13 CURRICULUM CONSTANTS -- director-signed, do NOT tune toward a gap number.
# ---------------------------------------------------------------------------

# The can't-pay / won't-pay harm asymmetry (design section 1.4a). Treating a
# genuinely-CANNOT-pay household as a strategic WON'T-pay (pressure/disconnect a
# vulnerable customer) carries customer-harm + a compliance breach; the mirror
# (giving forbearance to a strategic defaulter) carries only moral hazard + loss.
# Director-signed ratio R = 8:1. This is CURRICULUM (R13): it encodes how much the
# director cares, and is frozen here, never fitted.
HARM_RATIO_R: float = 8.0
HARM_RATIO_PROVENANCE: str = (
    "R13 curriculum, director-signed 8:1 "
    "(COUPLED_TRIAD_DESIGN.md 1.4a / CONTROLS_THAT_CANNOT_FAIL.md)"
)

# The 2x2 truth space: ABILITY x WILLINGNESS.
_ABILITY = ("can", "cannot")
_WILLINGNESS = ("will", "wont")
QUADRANTS = tuple((a, w) for a in _ABILITY for w in _WILLINGNESS)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class GapResult:
    """The computed gap for one coupled pair. `gap` is the normalised,
    dimensionless score (raw_gap / g0). `raw_gap` and `g0` are kept for audit so
    a reviewer can see the normalisation was not fudged (R15 independence)."""

    metric: str                      # classification|attribution|belief|detection
    gap: Optional[float]             # normalised; None only if g0 is degenerate
    raw_gap: float
    g0: float
    baseline: str                    # human-readable g0 description
    components: dict = field(default_factory=dict)
    note: str = ""

    def to_ledger_entry(self, twin_atom_id: str,
                        measured_at: Optional[str] = None,
                        run_git_commit: Optional[str] = None) -> dict:
        """Shape a ledger entry matching the contract that coupled_triad.py
        reads. `measured_at`/`run_git_commit` are passed IN (this module never
        calls a clock or git itself)."""
        return {
            "twin_atom_id": twin_atom_id,
            "gap": self.gap,
            "metric": self.metric,
            "raw_gap": self.raw_gap,
            "g0": self.g0,
            "baseline": self.baseline,
            "measured_at": measured_at,
            "run_git_commit": run_git_commit,
            "components": self.components,
            "note": self.note or self.baseline,
        }


def _normalise(raw_gap: float, g0: float, baseline: str, metric: str,
               components: dict, note: str = "") -> GapResult:
    """gap = raw_gap / g0, with the degenerate-baseline guard. A g0 of 0 means
    the blind prior is already perfect (no discrimination possible on this
    population) -- the gap is then 0.0 if the company is also perfect, else None
    (undefined, flagged) rather than a divide-by-zero or a fabricated number."""
    if g0 == 0:
        gap: Optional[float] = 0.0 if raw_gap == 0 else None
    else:
        gap = raw_gap / g0
    return GapResult(metric=metric, gap=gap, raw_gap=float(raw_gap),
                     g0=float(g0), baseline=baseline, components=components,
                     note=note)


# ---------------------------------------------------------------------------
# (a) Classification-accuracy gap -- can't-pay vs won't-pay 2x2 (W2_7)
# ---------------------------------------------------------------------------

def _as_quadrant(q) -> tuple:
    """Coerce a quadrant into a canonical (ability, willingness) tuple. Accepts
    a 2-tuple/list, or a string like 'cannot_wont' / 'cannot-wont'."""
    if isinstance(q, (tuple, list)):
        if len(q) != 2:
            raise ValueError(f"quadrant must be (ability, willingness): {q!r}")
        a, w = q[0], q[1]
    elif isinstance(q, str):
        parts = q.replace("-", "_").split("_")
        if len(parts) != 2:
            raise ValueError(f"quadrant string must be 'ability_willingness': {q!r}")
        a, w = parts
    else:
        raise ValueError(f"unrecognised quadrant: {q!r}")
    if a not in _ABILITY or w not in _WILLINGNESS:
        raise ValueError(
            f"quadrant ({a!r},{w!r}) not in ABILITY{_ABILITY} x WILLINGNESS{_WILLINGNESS}"
        )
    return (a, w)


def harm_cost(true_q, pred_q, harm_ratio: float = HARM_RATIO_R) -> float:
    """The R13 harm-cost matrix C[true, pred], diagonal 0 (design 1.4a).

    Two independent error axes, summed:
      * ABILITY error is asymmetric. Truth=cannot predicted=can (treat a
        vulnerable household as able-to-pay -> harm/compliance) costs `harm_ratio`
        (the 8). Truth=can predicted=cannot (needless forbearance -> loss) costs 1.
      * WILLINGNESS error costs a flat 1 either direction.
    The asymmetry lives on ability because that is where the customer-harm sits.
    """
    a_t, w_t = _as_quadrant(true_q)
    a_p, w_p = _as_quadrant(pred_q)
    cost = 0.0
    if a_t == "cannot" and a_p == "can":
        cost += float(harm_ratio)          # vulnerable treated as able -> HARM
    elif a_t == "can" and a_p == "cannot":
        cost += 1.0                        # able treated as vulnerable -> loss
    if w_t != w_p:
        cost += 1.0                        # willingness error, symmetric
    return cost


def classification_gap(truth: Sequence, belief: Sequence,
                       harm_ratio: float = HARM_RATIO_R) -> GapResult:
    """Cost-weighted 2x2 classification gap (formula a).

    truth[i], belief[i] are quadrants (ability, willingness). Baseline g0 =
    always predict the majority (argmax-prior) quadrant. Also reports the two
    directional false-negative components separately (design: "two test paths,
    not one accuracy score").
    """
    truth = [_as_quadrant(t) for t in truth]
    belief = [_as_quadrant(b) for b in belief]
    if not truth:
        raise ValueError("classification_gap: empty population")
    if len(truth) != len(belief):
        raise ValueError("truth and belief must be the same length")

    n = len(truth)
    raw_gap = sum(harm_cost(t, b, harm_ratio) for t, b in zip(truth, belief)) / n

    # Majority quadrant = the mode of the truth labels (the blind prior).
    counts: dict = {}
    for t in truth:
        counts[t] = counts.get(t, 0) + 1
    majority = max(counts, key=lambda q: counts[q])
    g0 = sum(harm_cost(t, majority, harm_ratio) for t in truth) / n

    # Directional false-negative rates (design 1.4a: "two test paths, not one
    # accuracy score"). fn_ability = the HARM path -- among the truly-cannot-pay
    # (vulnerable), the fraction the company believes CAN pay (ability=can), i.e.
    # treated as strategic and liable to be pressured/disconnected. fn_willingness
    # = the mirror LOSS path -- among the truly-won't-pay (strategic), the fraction
    # believed willing (willingness=will), i.e. given undue forbearance. Both are
    # 0 under perfect prediction by construction (a correct label is never an FN).
    n_cannot = sum(1 for a, _ in truth if a == "cannot")
    n_wont = sum(1 for _, w in truth if w == "wont")
    fn_ability = (
        sum(1 for (t, b) in zip(truth, belief)
            if t[0] == "cannot" and b[0] == "can") / n_cannot
        if n_cannot else 0.0
    )
    fn_willingness = (
        sum(1 for (t, b) in zip(truth, belief)
            if t[1] == "wont" and b[1] == "will") / n_wont
        if n_wont else 0.0
    )

    baseline = (
        f"always-predict-majority quadrant {majority[0]}/{majority[1]} "
        f"(harm ratio R={harm_ratio}:1, {HARM_RATIO_PROVENANCE})"
    )
    return _normalise(
        raw_gap, g0, baseline, "classification",
        components={"fn_ability": round(fn_ability, 6),
                    "fn_willingness": round(fn_willingness, 6),
                    "majority_quadrant": f"{majority[0]}_{majority[1]}",
                    "harm_ratio_R": harm_ratio},
        note="cost-weighted can't-pay/won't-pay 2x2; directional FN rates alongside",
    )


# ---------------------------------------------------------------------------
# (b) Attribution-error gap -- DD confound (W2_10)
# ---------------------------------------------------------------------------

def attribution_gap(delta_naive: float, delta_true: float) -> GapResult:
    """DD-confound attribution gap (formula b): the fraction of the company's
    claimed effect that is confound.

        gap = |delta_naive - delta_true| / |delta_naive|

    delta_naive is the company's OBSERVABLE-ONLY effect estimate; delta_true is
    the harness's causal effect (do-operator, using SIM ground truth). g0 is the
    full confound magnitude (|delta_naive| against delta_true=0), so this is
    already normalised: gap->0 fully de-confounded, gap->1 wholly naive.
    """
    dn = float(delta_naive)
    dt = float(delta_true)
    raw_gap = abs(dn - dt)
    g0 = abs(dn)          # baseline: the whole naive effect is confound (dt=0)
    baseline = (
        f"full naive effect is confound (delta_true=0); "
        f"delta_naive={dn:g}, delta_true={dt:g}"
    )
    return _normalise(
        raw_gap, g0, baseline, "attribution",
        components={"delta_naive": dn, "delta_true": dt},
        note="fraction of the company's DD business case that is confound artefact",
    )


# ---------------------------------------------------------------------------
# (c) Belief-error gap -- population / budget (TV distance) (W2_2)
# ---------------------------------------------------------------------------

def _tv(p: Sequence[float], q: Sequence[float]) -> float:
    """Total-variation distance = 1/2 * sum |p_k - q_k| over two distributions."""
    if len(p) != len(q):
        raise ValueError("TV: vectors must be the same length")
    return 0.5 * sum(abs(float(pk) - float(qk)) for pk, qk in zip(p, q))


def _check_distribution(v: Sequence[float], name: str) -> None:
    if not v:
        raise ValueError(f"{name}: empty distribution")
    if any(float(x) < 0 for x in v):
        raise ValueError(f"{name}: negative probability")
    s = sum(float(x) for x in v)
    if abs(s - 1.0) > 1e-6:
        raise ValueError(f"{name}: does not sum to 1 (sum={s:g})")


def belief_gap(truth: Sequence[float], belief: Sequence[float],
               prior: Optional[Sequence[float]] = None) -> GapResult:
    """Belief-error gap (formula c): total-variation distance between the SIM's
    true segment/budget distribution `truth` and the company's inferred
    distribution `belief`.

    TV is already in [0,1]. If a blind `prior` (national prior the company would
    assume with zero book-specific info) is given, the gap is normalised
    TV(truth,belief)/TV(truth,prior) for cross-pair comparability (raw TV kept in
    components). Without a prior, the gap IS the raw TV (design 1.4c).
    """
    _check_distribution(truth, "truth")
    _check_distribution(belief, "belief")
    raw_tv = _tv(truth, belief)

    if prior is None:
        # TV is self-normalised; g0 is the [0,1] ceiling.
        return GapResult(
            metric="belief", gap=raw_tv, raw_gap=raw_tv, g0=1.0,
            baseline="total-variation distance (self-normalised to [0,1])",
            components={"tv": round(raw_tv, 6)},
            note="TV(belief, truth); no blind prior supplied, gap = raw TV",
        )

    _check_distribution(prior, "prior")
    g0 = _tv(truth, prior)
    baseline = "TV(truth, national/blind prior) -- the no-book-info belief"
    return _normalise(
        raw_tv, g0, baseline, "belief",
        components={"tv": round(raw_tv, 6), "tv_prior": round(g0, 6)},
        note="belief-error normalised to the blind-prior TV",
    )


# ---------------------------------------------------------------------------
# (d) Detection-rate + false-negative-harm gap -- self-rationing (W2_8)
# ---------------------------------------------------------------------------

def detection_gap(truth_set: Iterable, flagged_set: Iterable,
                  harm: Optional[Mapping] = None) -> GapResult:
    """Self-rationing detection gap (formula d).

    truth_set S = accounts truly self-rationing (SIM label). flagged_set D =
    accounts the company flagged (observable-only). Two numbers, the
    harm-weighted one is the score:

        miss_rate = 1 - |S & D| / |S|                       # plain recall gap
        gap       = sum_{i in S\\D} harm_i / sum_{i in S} harm_i  # harm missed

    `harm` maps account -> severity (e.g. TDCV shortfall x duration). Omitted ->
    uniform harm (gap == miss_rate). g0 = flagging nobody (gap == 1 when D=empty).
    """
    S = set(truth_set)
    D = set(flagged_set)
    if not S:
        raise ValueError("detection_gap: empty truth set (no self-rationing accounts)")

    caught = S & D
    missed = S - D
    miss_rate = 1.0 - len(caught) / len(S)

    if harm is None:
        harm_map = {i: 1.0 for i in S}
    else:
        harm_map = {i: float(harm.get(i, 0.0)) for i in S}
    total_harm = sum(harm_map.values())
    missed_harm = sum(harm_map[i] for i in missed)

    if total_harm == 0:
        # Every truly-rationing account carries zero harm -> nothing at stake.
        gap: Optional[float] = 0.0
        g0 = 0.0
    else:
        gap = missed_harm / total_harm     # already normalised: D=empty -> 1.0
        g0 = 1.0

    baseline = "flag nobody (all detectable harm missed -> gap = 1)"
    return GapResult(
        metric="detection", gap=gap, raw_gap=missed_harm,
        g0=(total_harm if total_harm else 0.0),
        baseline=baseline,
        components={"miss_rate": round(miss_rate, 6),
                    "caught": len(caught), "missed": len(missed),
                    "truth_size": len(S), "flagged_size": len(D),
                    "missed_harm": missed_harm, "total_harm": total_harm},
        note="harm-weighted fraction of detectable self-rationing harm missed",
    )


# ---------------------------------------------------------------------------
# Deterministic bootstrap CI (C-S2: named RNG substream, reproducible)
# ---------------------------------------------------------------------------

def _substream_seed(name: str) -> int:
    """Derive a stable 63-bit seed from a NAMED substream string (C-S2). Same
    name -> same seed on every machine/run, so a resample is reproducible and a
    draw here can never shift another subsystem's stream."""
    h = hashlib.sha256(name.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") & 0x7FFFFFFFFFFFFFFF


def bootstrap_gap_ci(metric_fn, truth: Sequence, belief: Sequence,
                     *, substream: str, n_resamples: int = 1000,
                     alpha: float = 0.05):
    """Percentile bootstrap CI for a per-entity gap (classification only, where
    truth/belief are aligned per-entity sequences). Addresses design section 6's
    "small-cast statistical power": at ~31 accounts a gap is noisy; this reports
    the band. Deterministic -- the Generator is seeded from `substream` (C-S2),
    never from a clock or the global RNG.

    Returns (point_gap, lo, hi). Requires numpy.
    """
    import numpy as np

    if len(truth) != len(belief):
        raise ValueError("truth and belief must be the same length")
    n = len(truth)
    if n == 0:
        raise ValueError("bootstrap_gap_ci: empty population")

    point = metric_fn(truth, belief).gap
    rng = np.random.default_rng(_substream_seed(substream))
    samples = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        rt = [truth[j] for j in idx]
        rb = [belief[j] for j in idx]
        g = metric_fn(rt, rb).gap
        if g is not None:
            samples.append(g)
    if not samples:
        return point, None, None
    samples.sort()
    lo = samples[int((alpha / 2) * len(samples))]
    hi = samples[min(len(samples) - 1, int((1 - alpha / 2) * len(samples)))]
    return point, lo, hi


# ---------------------------------------------------------------------------
# Ledger write (the WRITE side of the contract coupled_triad.py reads)
# ---------------------------------------------------------------------------

def write_gap_entry(world_atom_id: str, twin_atom_id: str, result: GapResult,
                    *, measured_at: Optional[str] = None,
                    run_git_commit: Optional[str] = None,
                    ledger_path=None) -> dict:
    """Merge one pair's gap into the coupled gap ledger and persist it.

    Contract (matches background/coupled_triad.py's reader):
        { "<world_atom_id>": {"twin_atom_id", "gap", "measured_at",
                              "run_git_commit", "baseline", "note", ...} }

    `measured_at` and `run_git_commit` are passed IN (default None) -- this
    function NEVER calls a clock or git (C-S2 determinism / forbidden-clock
    rule). Returns the full ledger dict after the merge.

    An existing malformed/unreadable ledger is treated as empty and overwritten
    with a well-formed object -- it never crashes the write. Other entries are
    preserved (read-merge-write).
    """
    path = Path(ledger_path) if ledger_path is not None else GAP_LEDGER_PATH
    ledger: dict = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                ledger = loaded
        except (OSError, json.JSONDecodeError, ValueError):
            ledger = {}

    ledger[world_atom_id] = result.to_ledger_entry(
        twin_atom_id, measured_at=measured_at, run_git_commit=run_git_commit)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return ledger
