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
    (e) misapplication  -- wrong-CLASS applied vs the answer key (W2_9)
    (f) prediction      -- continuous MAE vs a climatological baseline (W1_6)
    (g) ageing          -- ORDERED bucket displacement, DELIBERATELY un-normalised
                           (D7). The one family that does NOT divide by a g0: on
                           an ordered space every prevalence-shaped baseline
                           re-imports the D6 defect (AGEING_NO_NORMALISER_REASON).

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
from typing import Dict, Iterable, Mapping, Optional, Sequence

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


# BELIEF_GAP_IS_PERMUTATION_INVARIANT (2026-08-10, H27 Expert-Hour pass #3).
# This gap compares two POPULATION DISTRIBUTIONS, so it is blind to WHICH case
# holds which label. Permuting the company's per-case beliefs among cases --
# destroying every correct per-case assignment while leaving the label multiset
# alone -- moves this number by EXACTLY ZERO. Measured on the W2_11<->D5
# payment triad, seeds 7/11/23 at n=600: per-case agreement 0.9300 -> 0.6333,
# published gap 0.0700 -> 0.0700 (identical to machine precision, all three).
#
# WHY IT HID FOR SO LONG, and the reason this caveat is stamped rather than
# assumed obvious: on a book where the company's errors run ONE WAY (the
# payment triad under-calls severity -- normal 443->485, watch 114->87,
# high 36->25), TV is ARITHMETICALLY EQUAL to the per-case disagreement rate.
# Seed 7: gap 0.0700, disagreement 0.0700. Seed 11: 0.1033 / 0.1033. Seed 23:
# 0.0733 / 0.0733. The number therefore READS as a per-case error rate, and
# happens to equal one, while being a different quantity that a permutation
# leaves untouched. Equality on today's population is a coincidence of the
# error direction, not a property of the metric.
#
# This is the same DUAL-DEGENERATE class D11/D12/D14/D15 closed across the
# four DETECTION dimensions; those registers cover detection scorers only, so
# the belief dimension was never swept. Here the degenerate strategy is not
# "flag everything" but "get the MIX right and every individual wrong".
#
# SUPERSEDED AS A HEADLINE, NOT DELETED (atom D19 landed 2026-08-10).
# `belief_measures` below is the per-case replacement, and the payment triad's
# published belief headline now uses it. This function SURVIVES for two honest
# jobs: (1) callers that hold only two distributions and no per-case pairing
# (`couple_w2_4_c6`, `couple_cohort`) -- REGISTERED NAMED DEBT, not silent
# survivors; (2) the payment triad's own `belief_population_mix` dimension,
# where the question really IS about the mix and permutation-invariance is the
# correct behaviour rather than a defect. What changed is that the number is no
# longer published under a name ("belief gap") that reads as a per-case error
# rate: it is published as what it measures.
BELIEF_GAP_PERMUTATION_CAVEAT = (
    "PERMUTATION-INVARIANT: this is a distance between POPULATION "
    "DISTRIBUTIONS, so it is blind to which case holds which label -- a "
    "company that gets the population MIX right and every INDIVIDUAL wrong "
    "scores exactly what the real company scores. Where the company's errors "
    "run one way it also happens to EQUAL the per-case disagreement rate, "
    "which is a coincidence of the error direction, not the quantity. "
    "SUPERSEDED as a headline by gap_metric.belief_measures (atom "
    "D19_belief_gap_is_distribution_only, landed 2026-08-10), which scores "
    "both per-case error directions on their own denominators; a caller still "
    "publishing THIS as its belief headline must be registered as named debt "
    "in tools.couple_w2_11_d5.AGGREGATE_SCORING_CONTRACT. Read "
    "`per_case_disagreement_rate` beside it."
)


def _per_case_witness(truth_labels: Optional[Sequence],
                      belief_labels: Optional[Sequence]) -> Dict[str, object]:
    """The direction the distribution distance cannot see: how often the
    company put the RIGHT label on the RIGHT case.

    `None`, never 0, when the caller cannot supply per-case labels -- a 0 here
    would be the strongest possible claim ("the company got every case right")
    handed out for free to a caller that simply did not measure (the D11 rule
    for `false_flag_rate`, applied to the same failure shape).
    """
    if truth_labels is None or belief_labels is None:
        return {"n_cases": None, "n_cases_misassigned": None,
                "per_case_disagreement_rate": None}
    t, b = list(truth_labels), list(belief_labels)
    if len(t) != len(b):
        raise ValueError(
            f"per-case witness: truth_labels ({len(t)}) and belief_labels "
            f"({len(b)}) are not the same population")
    if not t:
        # A vacuous population is not a perfect one.
        return {"n_cases": 0, "n_cases_misassigned": None,
                "per_case_disagreement_rate": None}
    wrong = sum(1 for x, y in zip(t, b) if x != y)
    return {"n_cases": len(t), "n_cases_misassigned": wrong,
            "per_case_disagreement_rate": round(wrong / len(t), 6)}


def belief_gap(truth: Sequence[float], belief: Sequence[float],
               prior: Optional[Sequence[float]] = None,
               truth_labels: Optional[Sequence] = None,
               belief_labels: Optional[Sequence] = None) -> GapResult:
    """Belief-error gap (formula c): total-variation distance between the SIM's
    true segment/budget distribution `truth` and the company's inferred
    distribution `belief`.

    TV is already in [0,1]. If a blind `prior` (national prior the company would
    assume with zero book-specific info) is given, the gap is normalised
    TV(truth,belief)/TV(truth,prior) for cross-pair comparability (raw TV kept in
    components). Without a prior, the gap IS the raw TV (design 1.4c).

    `truth_labels`/`belief_labels` are the OPTIONAL per-case labels the two
    distributions were built from, in the same case order. When supplied, the
    per-case witness this gap is structurally blind to
    (`per_case_disagreement_rate`) rides beside the score -- see
    `BELIEF_GAP_PERMUTATION_CAVEAT` for why it is needed and why the headline
    is not being reshaped here.
    """
    _check_distribution(truth, "truth")
    _check_distribution(belief, "belief")
    raw_tv = _tv(truth, belief)
    witness = _per_case_witness(truth_labels, belief_labels)

    if prior is None:
        # TV is self-normalised; g0 is the [0,1] ceiling.
        return GapResult(
            metric="belief", gap=raw_tv, raw_gap=raw_tv, g0=1.0,
            baseline=("total-variation distance (self-normalised to [0,1]); "
                      + BELIEF_GAP_PERMUTATION_CAVEAT),
            components={"tv": round(raw_tv, 6),
                        "permutation_invariant": True, **witness},
            note=("TV(belief, truth); no blind prior supplied, gap = raw TV. "
                  + BELIEF_GAP_PERMUTATION_CAVEAT),
        )

    _check_distribution(prior, "prior")
    g0 = _tv(truth, prior)
    baseline = ("TV(truth, national/blind prior) -- the no-book-info belief; "
                + BELIEF_GAP_PERMUTATION_CAVEAT)
    return _normalise(
        raw_tv, g0, baseline, "belief",
        components={"tv": round(raw_tv, 6), "tv_prior": round(g0, 6),
                    "permutation_invariant": True, **witness},
        note=("belief-error normalised to the blind-prior TV. "
              + BELIEF_GAP_PERMUTATION_CAVEAT),
    )


# ---------------------------------------------------------------------------
# (c2) PER-CASE belief measures -- the D19 reshape
# ---------------------------------------------------------------------------
# WHY THIS EXISTS. `belief_gap` above answers "does the company have the right
# MIX?". H27's Expert Hour #3 measured what that cannot answer: permuting the
# company's per-case labels among cases -- destroying every correct assignment
# while leaving the multiset alone -- moved the published figure by exactly
# zero (0.0713 -> 0.0713, per-case agreement 0.9287 -> 0.6432, n=4000 seed 7).
# The degenerate that scored what the real company scored was "right mix, every
# individual wrong": a collections report whose portfolio risk mix matches the
# auditor's exactly while naming the wrong customers in every bucket.
#
# THE SHAPE IS D11's, DELIBERATELY. That atom fixed the same class one
# dimension over (a recall-only detection score could not tell a precise
# company from an indiscriminate one) by scoring BOTH error directions on their
# OWN denominators, so that neither degenerate strategy can buy a good score.
# Severity is ORDINAL, so the two directions here are UNDER-calling and
# OVER-calling, and each denominator is the population on which that error is
# structurally POSSIBLE -- you cannot under-call an account that is already at
# the bottom of the scale, and counting it in the denominator would reward the
# company for the shape of the book rather than its judgement (the D7 rule:
# each rate carries the denominator it is about, and no rate carries a
# prevalence normaliser).
BELIEF_BALANCED_BASELINE = (
    "0.5 = every severity-blind rule, INCLUDING calling every account `normal` "
    "and calling every account `high` -- and including any rule that gets the "
    "population mix exactly right while assigning it to the wrong accounts. "
    "0 = the right severity on the right account"
)


def belief_measures(truth_labels: Sequence, belief_labels: Sequence, *,
                    order: Sequence) -> GapResult:
    """Two-directional PER-CASE severity-belief measures (formula c2, atom
    `D19_belief_gap_is_distribution_only`). Supersedes `belief_gap` as a
    headline wherever the caller can pair truth and belief case by case.

        undercall_rate = |{i: belief_i < truth_i}| / |{i: truth_i > min(order)}|
        overcall_rate  = |{i: belief_i > truth_i}| / |{i: truth_i < max(order)}|
        gap (headline) = (undercall_rate + overcall_rate) / 2

    `order` is the ORDINAL severity scale, least severe first. It is required,
    never inferred from the labels present: inferring it would make the scale --
    and therefore both directions -- a property of whichever labels a particular
    run happened to produce, so a run where nobody reached the top of the scale
    would silently redefine what over-calling means.

    THE DENOMINATORS ARE THE POSSIBLE-ERROR POPULATIONS, not the whole book.
    A case already at the bottom of the scale cannot be under-called and a case
    at the top cannot be over-called; including them would mean a book of
    mostly-`normal` accounts scored a low under-call rate for a reason that has
    nothing to do with the company (the prevalence dependence D6 measured and D7
    removed one dimension over).

    FAIL LOUD (R15): an empty population, mismatched lengths, a label outside
    `order`, a duplicated or single-valued `order` all RAISE. VACUITY IS
    EXPLICIT: where a direction's population is empty its rate is `None`, never
    0.0, and the headline is `None` rather than silently becoming the other
    direction alone -- a book on which an error is impossible is not one the
    company got right.
    """
    t = list(truth_labels)
    b = list(belief_labels)
    scale = list(order)

    if len(scale) < 2:
        raise ValueError(
            "belief_measures: `order` needs at least two severity levels -- "
            "with one level no error direction exists and both rates would be "
            "vacuously 0 (fail-open)."
        )
    if len(set(scale)) != len(scale):
        raise ValueError(f"belief_measures: duplicate level in `order`: {scale}")
    if len(t) != len(b):
        raise ValueError(
            f"belief_measures: truth_labels ({len(t)}) and belief_labels "
            f"({len(b)}) are not the same population -- the per-case pairing "
            "this measure rests on does not exist."
        )
    if not t:
        raise ValueError(
            "belief_measures: empty population -- scoring it 0 would be the "
            "strongest possible claim handed out for free (R15 fail-open)."
        )
    rank = {lbl: i for i, lbl in enumerate(scale)}
    unknown = {x for x in t + b if x not in rank}
    if unknown:
        raise ValueError(
            f"belief_measures: label(s) outside the declared scale: "
            f"{sorted(unknown)}. A label drift mapped to a rank by guesswork "
            "would move both direction rates with nothing firing."
        )

    lo, hi = 0, len(scale) - 1
    pairs = [(rank[x], rank[y]) for x, y in zip(t, b)]

    undercall_pop = [(tr, be) for tr, be in pairs if tr > lo]
    overcall_pop = [(tr, be) for tr, be in pairs if tr < hi]
    undercalled = [(tr, be) for tr, be in undercall_pop if be < tr]
    overcalled = [(tr, be) for tr, be in overcall_pop if be > tr]

    undercall_rate = (len(undercalled) / len(undercall_pop)
                      if undercall_pop else None)
    overcall_rate = (len(overcalled) / len(overcall_pop)
                     if overcall_pop else None)
    if undercall_rate is None or overcall_rate is None:
        gap: Optional[float] = None
    else:
        gap = (undercall_rate + overcall_rate) / 2.0

    n_wrong = sum(1 for tr, be in pairs if tr != be)

    def _mean_steps(cases) -> Optional[float]:
        if not cases:
            return None
        return round(sum(abs(tr - be) for tr, be in cases) / len(cases), 6)

    components: Dict[str, object] = {
        "undercall_rate": (None if undercall_rate is None
                           else round(undercall_rate, 6)),
        "overcall_rate": (None if overcall_rate is None
                          else round(overcall_rate, 6)),
        "n_undercalled": len(undercalled),
        "n_overcalled": len(overcalled),
        "n_undercall_population": len(undercall_pop),
        "n_overcall_population": len(overcall_pop),
        "n_cases": len(pairs),
        "n_cases_misassigned": n_wrong,
        "per_case_disagreement_rate": round(n_wrong / len(pairs), 6),
        # MAGNITUDE, beside the rates and never instead of them. How FAR wrong
        # the company was when it was wrong, in scale steps -- a company one
        # step out on every case is not the same company as one that called a
        # `high` account `normal`, and a pure rate cannot tell them apart.
        # Named per direction so neither can be read as the other (the D16 law:
        # one name, one number).
        "mean_undercall_steps": _mean_steps(undercalled),
        "mean_overcall_steps": _mean_steps(overcalled),
        "scale": list(scale),
        # CONTINUITY, stated rather than restated. The retired figure is NOT
        # recomputed here: it is a different quantity over the same cases, and a
        # component that looked like it belonged to this measure is how one name
        # comes to carry two numbers (D16). Callers that want it publish it as
        # its own dimension under a name that says it is about the MIX.
        "supersedes": (
            "belief_gap as a HEADLINE (population TV, permutation-invariant -- "
            "atom D19, 2026-08-10). The TV figure is not restated here: it "
            "measures the population MIX, a different question about the same "
            "cases, and belongs to a dimension named for it."
        ),
    }
    if gap is None:
        components["vacuity"] = (
            "one error direction has an EMPTY population on this book "
            f"(undercall population {len(undercall_pop)}, overcall population "
            f"{len(overcall_pop)}), so the balanced headline is UNDEFINED "
            "(None), not 0.0 and not the surviving direction alone."
        )

    return GapResult(
        metric="belief",
        gap=gap,
        raw_gap=(0.0 if undercall_rate is None else float(undercall_rate)),
        g0=0.5,
        baseline=BELIEF_BALANCED_BASELINE,
        components=components,
        note=(
            "BALANCED per-case severity-belief error (atom D19, superseding the "
            "population-TV `belief_gap` as a headline): the mean of "
            "undercall_rate (over the accounts that COULD be under-called) and "
            "overcall_rate (over the accounts that COULD be over-called), each "
            "on its own denominator. Permuting which account holds which belief "
            "MOVES this number, which is the whole reason it exists. R12: a "
            "diagnostic, never a target."
        ),
    )


def format_belief_summary(
    result: GapResult, *,
    undercall_name: str = "under-called severity",
    overcall_name: str = "over-called severity",
) -> str:
    """Render a `belief_measures` result as BOTH directions with their
    denominators, never as a bare scalar -- the `format_detection_summary`
    mechanism, for the same reason: this dimension went wrong the moment a bare
    `belief 0.0700` could be read as "7% of accounts mis-graded" when the
    quantity behind it could not tell which accounts they were.

    THE TWO NOUNS ARE PARAMETERS (the D15 rule): a second pair scoring an
    ordinal belief through this renderer is not measuring arrears severity, and
    hardcoding one pair's wording into a shared renderer is how a name ends up
    describing two different quantities.
    """
    c = result.components

    def _num(key: str, fmt: str) -> str:
        v = c.get(key)
        return "undefined (no such population)" if v is None else format(v, fmt)

    def _steps(key: str) -> str:
        v = c.get(key)
        return "" if v is None else f", mean {v:.2f} steps"

    return (
        "belief balanced error "
        + ("undefined" if result.gap is None else format(result.gap, ".4f"))
        + " [0.5 = every severity-blind rule, incl. right mix / wrong accounts]"
        + f"; {undercall_name} " + _num("undercall_rate", ".4f")
        + f" ({c.get('n_undercalled')} of {c.get('n_undercall_population')}"
        + _steps("mean_undercall_steps") + ")"
        + f"; {overcall_name} " + _num("overcall_rate", ".4f")
        + f" ({c.get('n_overcalled')} of {c.get('n_overcall_population')}"
        + _steps("mean_overcall_steps") + ")"
        + "; per-case disagreement " + _num("per_case_disagreement_rate", ".4f")
        + f" ({c.get('n_cases_misassigned')} of {c.get('n_cases')})"
    )


# ---------------------------------------------------------------------------
# (d) Detection-rate + false-negative-harm gap -- self-rationing (W2_8)
# ---------------------------------------------------------------------------

# D11 CLASS FINDING (2026-08-09, H27 Expert-Hour pass). This gap counts ONE
# ERROR DIRECTION -- missed truth. `flagged_set` appears in the formula only
# through `S & D`, so enlarging D can never make the score worse, and the
# DUAL DEGENERATE strategy -- flag EVERYTHING -- scores a PERFECT 0.0 on any
# population whatsoever. `baseline`/`g0` name only the opposite degenerate
# ("flag nobody -> 1"), which reads as though 0 were earned. It is not: 0 is
# what both a perfect detector AND a company that flags every account score.
#
# This is the D6/D7 defect shape one dimension over. D7 established the remedy
# for the ageing dimension -- report the two error directions on their OWN
# denominators rather than one figure that silently mixes them -- and the same
# reasoning applies here, so the caveat is stamped AT SOURCE (the D6 precedent)
# and lands on every call site: W2_11<->D5, W2_5<->C7, W2_8<->C10.
#
# SUPERSEDED, NOT DELETED (D11 landed 2026-08-09). `detection_measures` below is
# the two-directional replacement and the payment triad's published headline now
# uses it. This function survives ONLY for the callers that cannot (yet) name the
# universe of cases that could have been flagged -- the W2_5<->C7 and W2_8<->C10
# self-rationing pairs, and the regime-partitioned payment CELL grid, whose band
# was calibrated on this shape. Those are REGISTERED NAMED DEBT, not silent
# survivors: `tools.couple_w2_11_d5.DETECTION_DIRECTION_CONTRACT` enumerates every
# published detection-style dimension and its control fails on an unregistered one.
DETECTION_GAP_DUAL_DEGENERATE = (
    "flag EVERYTHING also scores 0.0 -- this gap counts missed truth only, so a "
    "score near 0 is evidence of recall and says NOTHING about how much the "
    "company over-flagged. SUPERSEDED by gap_metric.detection_measures "
    "(atom D11_detection_gap_is_recall_only, landed 2026-08-09), which scores "
    "both directions on their own denominators; a caller still on this function "
    "must be registered as named debt in DETECTION_DIRECTION_CONTRACT"
)


def detection_gap(truth_set: Iterable, flagged_set: Iterable,
                  harm: Optional[Mapping] = None,
                  population_size: Optional[int] = None) -> GapResult:
    """Self-rationing detection gap (formula d).

    truth_set S = accounts truly self-rationing (SIM label). flagged_set D =
    accounts the company flagged (observable-only). Two numbers, the
    harm-weighted one is the score:

        miss_rate = 1 - |S & D| / |S|                       # plain recall gap
        gap       = sum_{i in S\\D} harm_i / sum_{i in S} harm_i  # harm missed

    `harm` maps account -> severity (e.g. TDCV shortfall x duration). Omitted ->
    uniform harm (gap == miss_rate). g0 = flagging nobody (gap == 1 when D=empty).

    READ THE SCORE WITH ITS DUAL (see DETECTION_GAP_DUAL_DEGENERATE above):
    this is a RECALL gap, and flagging everything scores 0. `population_size`
    is the size of the scored universe (truth + non-truth); pass it and the
    over-flagging witnesses `n_false_flags` / `false_flag_rate` (false flags
    over the truly-NEGATIVE population, its own denominator per D7) come back
    in `components`. Omit it and they are None -- explicitly not-measured,
    never a silent 0.
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

    # OVER-FLAGGING witnesses (D11). False flags are counted on their OWN
    # denominator -- the truly-NEGATIVE population -- because a rate over the
    # whole population would re-import exactly the class-balance dependence D7
    # was minted to remove. Unknown universe -> None, never 0: a missing
    # denominator that scored as "no false flags" would be fail-open, and this
    # witness exists precisely because a 0 here is otherwise indistinguishable
    # from a company that flagged everything.
    false_flags = D - S
    if population_size is None:
        n_false_flags: Optional[int] = None
        false_flag_rate: Optional[float] = None
    else:
        n_false_flags = len(false_flags)
        n_negatives = int(population_size) - len(S)
        false_flag_rate = (n_false_flags / n_negatives) if n_negatives > 0 else None

    baseline = ("flag nobody (all detectable harm missed -> gap = 1); "
                + DETECTION_GAP_DUAL_DEGENERATE)
    return GapResult(
        metric="detection", gap=gap, raw_gap=missed_harm,
        g0=(total_harm if total_harm else 0.0),
        baseline=baseline,
        components={"miss_rate": round(miss_rate, 6),
                    "caught": len(caught), "missed": len(missed),
                    "truth_size": len(S), "flagged_size": len(D),
                    "missed_harm": missed_harm, "total_harm": total_harm,
                    # D11: the other error direction, on its own denominator.
                    "n_false_flags": n_false_flags,
                    "false_flag_rate": (round(false_flag_rate, 6)
                                        if false_flag_rate is not None else None)},
        note=("harm-weighted fraction of detectable self-rationing harm missed "
              "-- RECALL ONLY; " + DETECTION_GAP_DUAL_DEGENERATE),
    )


# ---------------------------------------------------------------------------
# (d2) Detection MEASURES -- the two-directional successor (atom D11)
# ---------------------------------------------------------------------------
# WHY THIS REPLACES `detection_gap` FOR ANY DIMENSION THAT CAN NAME ITS UNIVERSE.
# `detection_gap` above is a RECALL gap: `flagged_set` enters only through the
# intersection, so enlarging it can never make the score worse and the dual
# degenerate -- flag EVERYTHING -- scores a perfect 0.0. The 2026-08-09 H27
# Expert Hour measured 44-51% of the payment triad's flags landing on invoices
# that truly SUCCEEDED while the headline read 0.0725, i.e. "nearly perfect".
#
# THE REMEDY IS D7's, APPLIED TO A SECOND DIMENSION (R10 -- the class, not the
# instance). D7 retired the ageing dimension's single scalar and published the
# two error directions on the denominators they are each actually about. The
# same two directions exist here and they are NOT interchangeable in the world:
#
#   * missed_failure_rate -- a true failure the company never flagged. Cash it
#     never chases, provision it never makes.
#   * false_flag_rate     -- an invoice that truly SUCCEEDED and was flagged
#     anyway: the WRONGFUL-DUNNING exposure, a real customer chased for money
#     they already paid.
#
# THAT SECOND DIRECTION IS **NOT** THE SAME NUMBER D7's `overstated_arrears_rate`
# PUBLISHES ONE DIMENSION OVER, and this comment asserted for a day that it was
# ("literally the same numerator"). MEASURED, seed 7 / 400 customers, case by
# case (H27 Expert Hour 2026-08-09): detection counts 21 false flags over 782
# never-flaggable cases (0.0269); ageing counts 101 false ageings over 1062
# truly-current ones (0.0951). They share SEVEN cases. The two populations sit in
# an exact containment -- ageing's truly-current == detection's negatives PLUS
# the 280 cases detection EXCLUDES -- and 94 of ageing's 101 land in that
# excluded band, i.e. on invoices the exclusion rule below holds the company was
# RIGHT to flag. Both numbers are defensible; the claim that they are one
# measurement was not. The two dimensions are held to a DECLARED, measured
# relationship by `tools.couple_w2_11_d5.SHARED_QUANTITY_CONTRACT` rather than by
# this paragraph, and the alignment itself is atom
# `D16_ageing_negative_population_is_unexcluded` (it moves a published number, so
# it is not done on sight).
#
# THE HEADLINE IS THE BALANCED ERROR, and its baseline is honest in a way the
# recall gap's could not be: EVERY prevalence-blind strategy scores exactly
# `g0 = 0.5` -- flag nobody (1, 0), flag everything (0, 1), and any coin-flip at
# any rate. 0.0 has to be earned in BOTH directions; 1.0 is perfectly wrong.
#
# NO CLASS-BALANCE DENOMINATOR ANYWHERE (D7's mutation-caught trap: any
# normaliser counting the truth's class balance re-imports the prevalence defect
# whatever the numerator's shape). Each rate carries its own class's denominator,
# so each is prevalence-invariant, and so is their mean.
#
# VACUITY IS EXPLICIT, NEVER ZERO (R15 fail-open): no truly-negative cases -> the
# false-flag direction is UNDEFINED, so the headline is `None`, not the recall
# number wearing a new name. A universe with nothing to get wrong is not a
# universe the company got right.
DETECTION_BALANCED_BASELINE: str = (
    "0.5 -- the balanced error EVERY prevalence-blind rule scores: flag nobody "
    "(miss 1, false-flag 0), flag EVERYTHING (miss 0, false-flag 1), and any "
    "coin-flip at any rate. Unlike the recall-only `detection_gap` this "
    "supersedes, 0.0 cannot be bought by over-flagging -- it has to be earned in "
    "both directions -- and 1.0 means perfectly wrong, not merely blind."
)


def detection_measures(truth_set: Iterable, flagged_set: Iterable, *,
                       universe: Iterable,
                       negative_set: Optional[Iterable] = None,
                       exclusion_reason: Optional[str] = None,
                       harm: Optional[Mapping] = None) -> GapResult:
    """Two-directional detection measures (formula d2, atom
    `D11_detection_gap_is_recall_only`). Supersedes `detection_gap` wherever the
    caller can name the universe of cases that could have been flagged.

        missed_failure_rate = |S \\ D| / |S|            # harm-weighted if `harm`
        false_flag_rate     = |D & N| / |N|             # the wrongful-dunning side
        gap  (headline)     = (missed_failure_rate + false_flag_rate) / 2

    `universe` U is EVERY case scored. It is a SET, not a count, deliberately: a
    count cannot notice that a flag landed on a case outside the scored universe,
    which is exactly what a join-key drift looks like, and the denominators would
    then be quietly wrong.

    `negative_set` N is the cases a flag would be WRONG on -- NOT simply `U - S`.
    The two differ whenever a case is neither a true positive nor a legitimate
    negative: on the payment triad, an invoice paid three weeks late really was
    unpaid past its grace date, so the company flagging it was RIGHT even though
    the payment eventually succeeded. Counting it as a false flag would score the
    company down for being correct. Omit `negative_set` and it defaults to
    `U - S` -- right only when every non-truth case is one a flag would be wrong
    on. Anything in `U` that is in neither `S` nor `N` is EXCLUDED, counted, and
    `exclusion_reason` must say why: THE EXCLUSION IS PUBLISHED, NOT SILENT (the
    D10 rule), and omitting the reason RAISES rather than shrinking a denominator
    invisibly -- an unexplained exclusion is the cheapest way to make either
    direction look better than it is.

    FAIL LOUD (R15): an empty universe, an empty truth set, `S`/`N`/`D` outside
    `U`, an `S`/`N` overlap, or an unexplained exclusion all RAISE. VACUITY IS
    EXPLICIT: with no negative cases `false_flag_rate` and `gap` are `None`,
    never 0.0 and never a silent fallback to the recall number.

    `harm` weights the MISS direction only (severity of harm missed), matching
    `detection_gap`. There is deliberately no harm weight on the false-flag side
    here: the harm of wrongful dunning is a property of the CUSTOMER contacted,
    not of the invoice's size, and inventing a weight for it would be a curriculum
    change (R13) rather than a measurement.
    """
    S = set(truth_set)
    D = set(flagged_set)
    U = set(universe)
    N = (U - S) if negative_set is None else set(negative_set)

    if not U:
        raise ValueError(
            "detection_measures: empty universe -- the false-flag denominator is "
            "undefined and scoring it as 0 would be fail-open (R15)."
        )
    if not S:
        raise ValueError("detection_measures: empty truth set (nothing to detect)")
    if not S <= U:
        raise ValueError(
            f"detection_measures: {len(S - U)} truth case(s) outside the scored "
            "universe -- the universe is not the population that was scored, so "
            "every rate below would be measured against the wrong denominator."
        )
    if not D <= U:
        raise ValueError(
            f"detection_measures: {len(D - U)} flagged case(s) outside the scored "
            "universe -- a flag on an unscored case is a join-key drift, and "
            "silently dropping it would push the false-flag rate toward 0."
        )
    if not N <= U:
        raise ValueError(
            f"detection_measures: {len(N - U)} negative case(s) outside the "
            "scored universe."
        )
    if S & N:
        raise ValueError(
            f"detection_measures: {len(S & N)} case(s) are in BOTH the truth set "
            "and the negative set -- a case cannot be one the company must flag "
            "and one it must not."
        )

    excluded = U - S - N
    if excluded and not (exclusion_reason or "").strip():
        raise ValueError(
            f"detection_measures: {len(excluded)} case(s) are in neither the "
            "truth set nor the negative set and no `exclusion_reason` was given. "
            "An unexplained exclusion silently shrinks a denominator, which is "
            "the cheapest way to make either direction look better than it is "
            "(the D10 rule: the exclusion is published, not silent)."
        )

    caught = S & D
    missed = S - S.intersection(D)
    false_flags = D & N
    negatives = N

    miss_rate = 1.0 - len(caught) / len(S)
    if harm is None:
        harm_map = {i: 1.0 for i in S}
    else:
        harm_map = {i: float(harm.get(i, 0.0)) for i in S}
    total_harm = sum(harm_map.values())
    missed_harm = sum(harm_map[i] for i in missed)
    # With no harm anywhere there is nothing at stake to miss; the harm-weighted
    # miss direction is 0 by construction, exactly as in `detection_gap`.
    missed_share = (missed_harm / total_harm) if total_harm else 0.0

    if negatives:
        false_flag_rate: Optional[float] = len(false_flags) / len(negatives)
        gap: Optional[float] = (missed_share + false_flag_rate) / 2.0
    else:
        false_flag_rate = None
        gap = None

    components = {
        "missed_failure_rate": round(missed_share, 6),
        "false_flag_rate": (None if false_flag_rate is None
                            else round(false_flag_rate, 6)),
        "miss_rate": round(miss_rate, 6),
        "caught": len(caught),
        "missed": len(missed),
        "n_false_flags": len(false_flags),
        "truth_size": len(S),
        "flagged_size": len(D),
        "universe_size": len(U),
        "n_negatives": len(negatives),
        # THE PUBLISHED EXCLUSION (D10's rule). Cases in neither direction's
        # population, with the reason travelling in the components rather than in
        # prose a ledger reader never sees.
        "n_excluded": len(excluded),
        "exclusion_reason": (exclusion_reason if excluded else None),
        "missed_harm": missed_harm,
        "total_harm": total_harm,
        # NO RESTATEMENT OF THE RETIRED RECALL FIGURE, deliberately. It was
        # scored over a DIFFERENT flagged population (belief held at `as_of`, not
        # ever-flagged), so nothing computable from these sets reproduces it, and
        # a component that looked like it did would be a false continuity -- the
        # reader would compare two numbers that were never the same measurement.
        # Pre-2026-08-09 ledger entries carry the old figure; this one does not
        # pretend to.
        "supersedes": (
            "detection_gap (recall-only, retired 2026-08-09 by atom D11). NOT "
            "restated here: it was scored over a different flagged population, "
            "so no arithmetic on these sets reproduces it."
        ),
    }
    if not negatives:
        components["vacuity"] = (
            "NO case in the scored universe is one a flag would be WRONG on: the "
            "false-flag direction and the headline are UNDEFINED (None), not "
            "0.0. A universe with nothing to get wrong is not one the company "
            "got right."
        )

    return GapResult(
        metric="detection",
        gap=gap,
        raw_gap=float(missed_share),
        g0=0.5,
        baseline=DETECTION_BALANCED_BASELINE,
        components=components,
        note=(
            "BALANCED detection error -- the mean of the two error directions on "
            "their OWN denominators (atom D11, superseding the recall-only "
            "`detection_gap`): missed_failure_rate over the truly-failed cases "
            "and false_flag_rate over the truly-negative ones (the "
            "wrongful-dunning exposure). Neither degenerate strategy can buy a "
            "good score: flag nobody and flag everything both land on 0.5. "
            "R12: a diagnostic, never a target."
        ),
    )


def format_detection_summary(
    result: GapResult, *,
    truth_noun: str = "truly-failed",
    false_flag_name: str = "the wrongful-dunning exposure",
) -> str:
    """Render a `detection_measures` result for a log line / ledger note as BOTH
    directions with their denominators, never as a bare scalar.

    The same anti-decay mechanism as `format_ageing_summary` and
    `format_detection_latency_summary`, and for the same reason: this dimension
    went wrong the moment a bare `detection 0.0725` could be read as "nearly
    perfect detection" when half the company's flags were on invoices that had
    been paid. No consumer of this module prints the headline without both
    directions beside it.

    THE TWO NOUNS ARE PARAMETERS (atom D15, 2026-08-09) and default to the
    payment triad's wording, so every pre-existing render is byte-identical. They
    exist because this renderer stopped being the payment triad's alone the
    moment a second pair scored both directions through it: W2_5<->C7's truth is
    a life-event distress year, not a failed payment, and its false flags are not
    dunning. Hardcoding one pair's nouns into a shared renderer is how a name
    ends up describing two different quantities -- the class D16 closed inside
    the triad, applied here at birth rather than after a reader is misled. A
    caller measuring something else names it."""
    c = result.components

    def _num(key: str, fmt: str) -> str:
        v = c.get(key)
        return "undefined (no such population)" if v is None else format(v, fmt)

    return (
        "detection balanced error " + ("undefined" if result.gap is None
                                       else format(result.gap, ".4f"))
        + " [0.5 = every prevalence-blind rule, incl. flagging everything]"
        + " (missed_failure_rate " + _num("missed_failure_rate", ".4f")
        + " over " + str(c.get("truth_size")) + " " + truth_noun
        + ", false_flag_rate " + _num("false_flag_rate", ".4f")
        + " = " + str(c.get("n_false_flags")) + " of "
        + str(c.get("n_negatives")) + " never-flaggable cases wrongly flagged"
        + " = " + false_flag_name
        + ("" if not c.get("n_excluded") else
           f"; {c.get('n_excluded')} case(s) in neither population: "
           f"{c.get('exclusion_reason')}")
        + ")"
    )


# ---------------------------------------------------------------------------
# (e) Misapplication gap -- wrong-CLASS applied vs the answer key (W2_9)
# ---------------------------------------------------------------------------

# D6 CLASS FINDING (2026-08-08, docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md).
# The majority-class normaliser below makes `gap` a joint statement about the
# company AND the world's class balance -- g0 IS the minority share, so holding
# the company literally fixed and moving prevalence swings the score an order of
# magnitude, and gap>1 does NOT mean worse-than-no-skill. That is a property of
# THIS FUNCTION, so it lands on every call site, not just the ageing dimension
# where it was found. Until `D7_ageing_gap_metric_reshape` lands, the caveat is
# STAMPED INTO EVERY RESULT'S COMPONENTS (R10: the class fails automatically, not
# the instance). Components -- unlike `note`, which callers override -- travel
# through `to_ledger_entry` into the gap ledger and on to site/data/proof.json,
# so a consumer of a published misapplication figure cannot miss it.
MISAPPLICATION_PREVALENCE_CAVEAT: str = (
    "NOT EVIDENCE ON ITS OWN -- this gap is normalised to the majority-class "
    "baseline, so g0 is the minority-class share: prevalence alone moves the "
    "score an order of magnitude with company behaviour held fixed, and gap>1 "
    "does not mean worse-than-no-skill. Read raw_gap (the company's own error "
    "rate) and the directional components instead. Proven in docs/design/"
    "D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md; reshape = atom "
    "D7_ageing_gap_metric_reshape."
)


def misapplication_gap(truth_labels: Sequence, applied_labels: Sequence,
                       *, positive_class=None) -> GapResult:
    """Categorical misapplication gap (formula e): the fraction of cases where
    the company applied the WRONG class, normalised to a no-skill baseline.

    Used by the W2_9 <-> C11 segment-debt pair: `truth_labels[i]` is the
    obligation class the world says is CORRECT for case i (from the TRUE
    segment); `applied_labels[i]` is the class the company actually applied
    (C11 acting on the OBSERVED segment). A mismatch = wrong-segment T&C
    applied (a compliance/fairness error).

        raw_gap = mean( truth[i] != applied[i] )                # error rate
        g0      = mean( truth[i] != majority_class(truth) )     # blind baseline
        gap     = raw_gap / g0

    The blind baseline g0 is a NO-SKILL applier that always applies the single
    majority obligation class -- so gap=1 means the company does no better than
    that, gap=0 means it applied the correct class everywhere (structurally
    reachable here only if segment observation were perfect, i.e. no wall).
    R15 INDEPENDENCE: the truth labels come from a DIFFERENT source than the
    applied labels (world true-segment vs company observed-segment) -- the check
    is not reading its expected value from the thing it grades, so a real
    mislabel produces a real, non-tautological gap.

    FAIL LOUD on empty/mismatched input (a control that cannot see its
    population is unavailable = failed, not a silent pass)."""
    truth = list(truth_labels)
    applied = list(applied_labels)
    if not truth:
        raise ValueError("misapplication_gap: empty population")
    if len(truth) != len(applied):
        raise ValueError("truth_labels and applied_labels must be the same length")

    n = len(truth)
    n_wrong = sum(1 for t, a in zip(truth, applied) if t != a)
    raw_gap = n_wrong / n

    counts: dict = {}
    for t in truth:
        counts[t] = counts.get(t, 0) + 1
    majority = max(counts, key=lambda c: counts[c])
    g0 = sum(1 for t in truth if t != majority) / n

    # Directional error components: for a named positive_class (e.g. the
    # business-terms class), report how often it was wrongly withheld vs wrongly
    # applied -- the two compliance directions have different real-world harm
    # (a domestic account charged business interest is the unlawful direction).
    components: dict = {
        "n": n,
        "n_wrong": n_wrong,
        "error_rate": round(raw_gap, 6),
        "majority_class": str(majority),
        "class_counts": {str(k): v for k, v in sorted(counts.items(), key=lambda kv: str(kv[0]))},
    }
    if positive_class is not None:
        wrongly_applied = sum(
            1 for t, a in zip(truth, applied)
            if a == positive_class and t != positive_class
        )
        wrongly_withheld = sum(
            1 for t, a in zip(truth, applied)
            if t == positive_class and a != positive_class
        )
        components["positive_class"] = str(positive_class)
        components["wrongly_applied"] = wrongly_applied
        components["wrongly_withheld"] = wrongly_withheld

    # D6: the caveat rides in components so it survives a caller replacing
    # `note`, and so the minority share the score is really keyed to is stated
    # as a number rather than left implicit inside g0.
    components["normalisation"] = "majority-class prevalence"
    components["minority_class_share"] = round(g0, 6)
    components["prevalence_caveat"] = MISAPPLICATION_PREVALENCE_CAVEAT

    baseline = (
        f"no-skill applier: always apply the majority class {majority!r} "
        f"(mis-serves {g0:.4f} of the population)"
    )
    return _normalise(
        raw_gap, g0, baseline, "misapplication", components=components,
        note="fraction of accounts on the wrong-class T&C, normalised to the "
             "blind majority-class applier",
    )


# ---------------------------------------------------------------------------
# (g) Ageing measures -- an ORDERED bucket space, deliberately UN-normalised
#     (atom D7_ageing_gap_metric_reshape, from the D6 DISCOVER verdict)
# ---------------------------------------------------------------------------

# The company's own ageing vocabulary (`company.billing.arrears_engine.age_bucket`),
# in ORDER. Redeclared here rather than imported: `background/` is harness code and
# must not take a company import for a constant. `test_d7_ageing_measures.py` pins
# the two against each other so a drift on either side fails loudly.
AGEING_BUCKET_ORDER: tuple = ("current", "30-60", "60-90", "90+")

AGEING_NO_NORMALISER_REASON: str = (
    "NO NORMALISER, DELIBERATELY. Each measure's denominator is the population "
    "that measure is ABOUT (misses over the truly-overdue; false ageings over the "
    "truly-current) and the ordinal severity carries no denominator at all. Any "
    "denominator that counts the TRUTH's class balance -- majority-class share, "
    "no-skill displacement, anything prevalence-shaped -- re-imports the D6 defect "
    "whatever the numerator's shape (mutation-measured: it reproduces the same "
    "twentyfold swing with company behaviour held literally fixed). See "
    "docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md."
)

AGEING_HEADLINE_UNITS: str = (
    "BUCKETS of ordinal displacement (0 = dated right, 3 = a 90+ debt believed "
    "current), BALANCED over the two truth classes: the mean of the "
    "truly-overdue displacement and the truly-current displacement, each taken "
    "on its OWN denominator. NOT a [0,1] no-skill ratio -- do not read 1.0 here "
    "as 'no better than blind'; there is no baseline in this number. What it "
    "cannot say is WHICH direction the displacement came from -- see "
    "`ordinal_direction_caveat` and read the two terms beside it."
)

# ATOM D22 (found H27 Expert Hour #6, 2026-08-10; reshaped here the same day).
# THE DEFECT, measured rather than asserted: the headline used to be
# `mean_bucket_displacement`, a mean over the TRULY-OVERDUE invoices alone, so a
# company that dated every overdue invoice perfectly and dumped EVERY
# truly-current invoice into `90+` scored 0.000000 -- bit-identical to a company
# that dated every invoice right (seeds 7/11/23 on the W2_11<->D5 book, 10,758
# cases changed and the number did not move). So did one that over-aged every
# current invoice by exactly ONE bucket. The over-ageing direction was never
# invisible to the DIMENSION (`overstated_arrears_rate` counted it) but it was
# invisible to the ORDINAL term, which is the whole of what this dimension adds
# over a rate: in that direction the measure degraded to the error rate it was
# built to replace.
#
# THE RESHAPE, and why it is THIS shape. The obvious repair -- average the
# displacement over the WHOLE population -- re-imports the D6 defect the atom
# before this one removed: its denominator counts the truth's class balance, so
# with company behaviour held LITERALLY FIXED (every overdue invoice one bucket
# out, 5% of the current book over-aged by two) it swings 0.1089 -> 0.5500, a
# factor of 5.05, as arrears prevalence moves 1% -> 50%. That shape is pinned as
# a named mutant, `_MUTANT_displacement_over_whole_population`, and it must fail
# the prevalence test. What survives is the shape this module's own detection
# dimension already uses (atom D11): the BALANCED mean of the two directions,
# each on the denominator it is about --
#
#     balanced_bucket_displacement = (mean_bucket_displacement          # overdue
#                                     + mean_overstatement_displacement) / 2
#
# -- which is flat across the same prevalence sweep (swing x1.00), scores both
# indiscriminate degenerates 1.5 against a perfect dater's 0.0, and stays in
# buckets with no baseline. It is UNDEFINED (None), never 0.0, when either truth
# class is empty: with nothing to over-age, a company has not proved it would
# not, which is the same rule `detection_measures` applies to an empty negative
# population.
AGEING_ORDINAL_DIRECTION_CAVEAT: str = (
    "TWO-DIRECTIONAL ORDINAL HEADLINE (atom D22, 2026-08-10). `gap` is "
    "`balanced_bucket_displacement`: the mean of the displacement over the "
    "TRULY-OVERDUE invoices and the displacement over the truly-current ones, "
    "each on its own denominator, so neither direction can hide behind the "
    "other and neither can be bought by the world's arrears prevalence. TWO "
    "THINGS IT STILL DOES NOT SAY. (1) WHICH direction: a company one bucket "
    "out on every overdue invoice and one over-ageing half its current book "
    "score alike -- read the two terms, never the headline alone. (2) "
    "`mean_bucket_displacement` on its own -- the pre-D22 headline, and the "
    "figure carried by every ledger entry written before 2026-08-10 -- is the "
    "TRULY-OVERDUE term only, which no amount of over-ageing can move; it is "
    "not comparable with this headline and must not be quoted as one."
)


def _ageing_direction_note(components: dict) -> str:
    """The caveat with its two terms INTERPOLATED FROM THE MEASUREMENT rather
    than typed once into a sentence and left to rot (the D11/D16/D19 precedent).
    Says UNKNOWN, never zero, where a population cannot supply its term."""
    mean_over = components.get("mean_overstatement_displacement")
    mean_under = components.get("mean_bucket_displacement")
    if mean_over is None or mean_under is None:
        missing = ("truly-current" if mean_over is None else "truly-overdue")
        return (
            AGEING_ORDINAL_DIRECTION_CAVEAT + " On THIS call the headline is "
            f"UNDEFINED: there is no {missing} population, so the "
            "displacement in that direction is UNKNOWN -- never read as none, "
            "and never substituted by the term that IS defined (that "
            "substitution is exactly the one-directional headline D22 removed)."
        )
    return (
        AGEING_ORDINAL_DIRECTION_CAVEAT + " On THIS call the headline "
        f"{components.get('balanced_bucket_displacement'):.6f} is the mean of "
        f"under-dating {mean_under:.6f} buckets over "
        f"{components.get('n_truly_overdue')} truly-overdue invoices and "
        f"over-ageing {mean_over:.6f} buckets over "
        f"{components.get('n_truly_current')} truly-current ones (max "
        f"{components.get('max_overstatement_displacement')}, of which "
        f"{components.get('n_overaged_beyond_one_bucket')} were over-aged by "
        "MORE than one bucket)."
    )


def _ageing_counts(truth_labels: Sequence, belief_labels: Sequence,
                   order: Sequence,
                   excluded: Optional[Sequence] = None) -> dict:
    """The MEASUREMENT half of `ageing_gap`: validate the inputs and count, with
    no packaging, no rounding and no prose. Split out from `ageing_gap` (which
    assembles the GapResult) so the arithmetic can be read and tested without the
    ledger-shaping around it -- and because the numbers, not the presentation, are
    the thing under R15 mutation in `tests/tools/test_d7_ageing_measures.py`.

    `excluded` is a parallel truthy/falsy sequence marking cases that are in
    NEITHER direction's population (atom D16; see `ageing_gap`). An excluded case
    leaves EVERY count -- `n`, both denominators, the displacement population --
    and is counted in `n_excluded`. It is deliberately not "excluded from the
    current side only": a case the caller cannot classify is not evidence in
    either direction, and half-excluding it would leave the displacement mean
    measuring a population the rates do not.

    Returns the raw measures UNROUNDED. `None` (never 0.0) where a denominator is
    empty -- see `ageing_gap`'s docstring for why vacuity must not read as perfect.
    """
    truth = list(truth_labels)
    belief = list(belief_labels)
    if not truth:
        raise ValueError("ageing_gap: empty population")
    if len(truth) != len(belief):
        raise ValueError("truth_labels and belief_labels must be the same length")

    if excluded is None:
        drop = [False] * len(truth)
    else:
        drop = [bool(x) for x in excluded]
        if len(drop) != len(truth):
            raise ValueError(
                f"ageing_gap: `excluded` has {len(drop)} entries for "
                f"{len(truth)} cases -- a mis-aligned mask would exclude "
                "arbitrary rows, so this RAISES rather than zipping short."
            )

    rank = {b: i for i, b in enumerate(order)}
    unknown = sorted({str(x) for x in truth + belief if x not in rank})
    if unknown:
        raise ValueError(
            f"ageing_gap: labels outside the ordered bucket space {list(order)}: "
            f"{unknown} -- an unknown bucket cannot be ranked, and scoring it as "
            "displacement 0 would make a vocabulary drift read as perfect dating "
            "(R15 fail-open)."
        )

    n_excluded = sum(1 for d in drop if d)
    scored = [(t, b) for t, b, d in zip(truth, belief, drop) if not d]
    if not scored:
        raise ValueError(
            f"ageing_gap: all {len(truth)} case(s) were excluded -- there is no "
            "population left to score, and returning measures over nothing would "
            "be the fail-open shape this exclusion exists to avoid."
        )

    current = order[0]
    n = len(scored)
    n_truly_overdue = sum(1 for t, _ in scored if t != current)
    n_truly_current = n - n_truly_overdue

    misses = sum(1 for t, b in scored if t != current and b == current)
    false_ageings = sum(1 for t, b in scored if t == current and b != current)
    wrong_bucket = sum(
        1 for t, b in scored
        if t != current and b != current and t != b
    )
    displacements = [
        abs(rank[b] - rank[t]) for t, b in scored if t != current
    ]
    # THE OVER-AGEING ORDINAL TERM, over the truly-CURRENT population (atom
    # D22). Without it a truly-current invoice dated `30-60` and one dated `90+`
    # are the SAME number to this dimension -- zero -- and the
    # off-by-one/stone-blind distinction it exists to make is unavailable in
    # exactly the direction where wrongful dunning lives. Since D22 it is not a
    # witness beside the headline but HALF OF IT.
    overstatement_displacements = [
        abs(rank[b] - rank[t]) for t, b in scored if t == current
    ]
    over_only = [d for d in overstatement_displacements if d > 0]

    mean_under = (
        sum(displacements) / len(displacements) if displacements else None
    )
    mean_over = (
        sum(overstatement_displacements) / len(overstatement_displacements)
        if overstatement_displacements else None
    )

    return {
        "n": n,
        "n_excluded": n_excluded,
        "n_truly_overdue": n_truly_overdue,
        "n_truly_current": n_truly_current,
        "misses": misses,
        "false_ageings": false_ageings,
        "wrong_bucket": wrong_bucket,
        "understated_arrears_rate": (misses / n_truly_overdue) if n_truly_overdue else None,
        "overstated_arrears_rate": (false_ageings / n_truly_current) if n_truly_current else None,
        # The UNDER-DATING term: debt believed newer (or settled) than it is,
        # over the truly-overdue invoices. This was the headline until D22; it
        # is now one of the two halves.
        "mean_bucket_displacement": mean_under,
        "max_bucket_displacement": max(displacements) if displacements else None,
        # Over the whole truly-current population (the denominator
        # `overstated_arrears_rate` uses), so it is a severity for that RATE and
        # not a mean over the errors alone -- a mean over errors only would rise
        # as the company made FEWER of them. `None`, never 0.0, on a vacuous
        # current population.
        "mean_overstatement_displacement": mean_over,
        "max_overstatement_displacement": (
            max(overstatement_displacements) if overstatement_displacements else None
        ),
        # How many of the over-ageings were worse than off-by-one -- a
        # distinction no rate can draw, stated as a count.
        "n_overaged_beyond_one_bucket": sum(1 for d in over_only if d > 1),
        # THE HEADLINE (atom D22): the two directions balanced on their own
        # denominators, so prevalence cannot move it and neither direction can
        # hide behind the other. UNDEFINED, never 0.0, when either truth class
        # is empty -- a company with nothing to over-age has not shown it would
        # not, the same rule `detection_measures` applies to an empty negative
        # population.
        "balanced_bucket_displacement": (
            None if (mean_under is None or mean_over is None)
            else (mean_under + mean_over) / 2.0
        ),
    }


def ageing_gap(truth_labels: Sequence, belief_labels: Sequence,
               *, bucket_order: Sequence = AGEING_BUCKET_ORDER,
               excluded: Optional[Sequence] = None,
               exclusion_reason: Optional[str] = None) -> GapResult:
    """Debt-DATING measures for an ORDERED ageing space (formula g).

    Replaces the single prevalence-normalised scalar the ageing dimension used to
    borrow from `misapplication_gap` (atom `D7_ageing_gap_metric_reshape`). That
    scalar was refuted three ways in the D6 DISCOVER: gap>1 did not mean
    worse-than-no-skill, prevalence alone moved it twentyfold with the company
    held fixed, and a Hamming error rate is blind to bucket ORDER. Four measures
    replace it, each with the denominator it is actually about:

        understated_arrears_rate = misses        / n_truly_overdue
        overstated_arrears_rate  = false_ageings / n_truly_current
        mean_bucket_displacement = mean |rank(belief) - rank(truth)|
                                   over the TRULY-OVERDUE invoices, absolute
        mean_overstatement_displacement
                                 = the same, over the TRULY-CURRENT invoices
        balanced_bucket_displacement = mean of the two displacements  # HEADLINE

    * **understated** -- debt the company believes settled. What a real supplier
      under-provisions for and never chases.
    * **overstated** -- the AGEING-REPORT OVERSTATEMENT: truly-current invoices
      the company believes are in arrears *at `as_of`*. The old ratio hid this
      inside a denominator normed on the *other* class. It was published under
      the name "the wrongful-dunning exposure" until atom D16 measured that it is
      NOT that quantity and must not carry its name -- see the EXCLUSION note
      below and `background.shared_quantity_contract`.
    * **the two displacements** -- the ORDINAL severity, which is what a dating
      dimension is really about. Distinguishes off-by-one from stone-blind, which
      an error rate cannot. Reported ABSOLUTE, in buckets, with NO baseline
      (see `AGEING_NO_NORMALISER_REASON` -- the ratio version was drafted, mutated,
      and rejected for re-importing the very defect this atom exists to remove).
      ONE PER DIRECTION since atom D22: over-ageing has its own severity term
      because a headline over the truly-overdue alone could not see it at all.

    `GapResult.gap` carries `balanced_bucket_displacement` -- the mean of the two
    -- as the dimension's headline (a dating dimension's headline is date
    displacement, not a classification rate), and `g0` is 0.0 because there IS no
    baseline: `baseline` says so in words so a ledger reader cannot mistake it
    for a normalised score. BEFORE 2026-08-10 the headline was the truly-overdue
    term alone; entries written before that date are a different measurement and
    are not comparable with this one (atom D22, and the comment above it for the
    measurement that convicted the old shape and the one that convicted the
    obvious repair).

    THE EXCLUSION BAND (atom `D16_ageing_negative_population_is_unexcluded`,
    2026-08-09). `excluded` is a parallel truthy/falsy mask marking cases in
    NEITHER direction's population, exactly as `detection_measures` treats
    `universe - truth_set - negative_set`. It exists because the two dimensions
    of the payment triad published one named quantity as two numbers 3.5x apart:
    `detection_measures` applies D11's rule -- an invoice paid past its grace
    date really WAS unpaid past grace, so a flag on it was CORRECT -- and this
    function applied no rule at all, so 94 of its 101 "false ageings" were cases
    the sibling dimension of the same instrument held the company was RIGHT
    about. The band is the CALLER's to define (only the caller knows what its
    cases are), but it is PUBLISHED, NEVER SILENT: excluding any case without an
    `exclusion_reason` RAISES, because an unexplained exclusion shrinking a
    denominator is the cheapest way to make a rate look better than it is (the
    D10 rule, and here it would move a rate the caller is being scored on).

    FAIL LOUD, never fail-open (R15): an empty population, a length mismatch, a
    mis-aligned `excluded` mask, an exclusion with no reason, a fully-excluded
    population, or a label outside `bucket_order` all RAISE. A silently-tolerated
    unknown label would score as displacement 0 -- a bucket-vocabulary drift
    would then read as perfect dating. VACUITY IS EXPLICIT, not zero: with no
    truly-overdue invoices the two overdue-denominated measures are `None`, not
    0.0; with no truly-current invoices the two current-denominated ones are; and
    `gap` is `None` if EITHER class is empty, because a half-population headline
    is the one-directional shape D22 removed.
    """
    order = list(bucket_order)
    measured = _ageing_counts(truth_labels, belief_labels, order, excluded)
    if measured["n_excluded"] and not (exclusion_reason or "").strip():
        raise ValueError(
            f"ageing_gap: {measured['n_excluded']} case(s) are excluded from "
            "both populations and no `exclusion_reason` was given. An "
            "unexplained exclusion silently shrinks a denominator -- the D10 "
            "rule: the exclusion is published, not silent."
        )
    headline = measured["balanced_bucket_displacement"]

    def _r(x: Optional[float]) -> Optional[float]:
        return None if x is None else round(x, 6)

    components = dict(measured)
    for key in ("understated_arrears_rate", "overstated_arrears_rate",
                "mean_bucket_displacement", "mean_overstatement_displacement",
                "balanced_bucket_displacement"):
        components[key] = _r(components[key])
    components["bucket_order"] = order
    components["headline_units"] = AGEING_HEADLINE_UNITS
    # STAMPED AT SOURCE (atom D22), so it reaches every caller of this scorer
    # rather than only the pair whose Expert Hour found it -- the D19 pattern.
    components["ordinal_direction_caveat"] = _ageing_direction_note(components)
    components["normalisation"] = AGEING_NO_NORMALISER_REASON
    # THE PUBLISHED EXCLUSION (D10's rule, carried across by D16), in the
    # components rather than in prose a ledger reader never sees -- and `None`
    # rather than absent when nothing was excluded, so a reader can tell "this
    # dimension applies no band" from "this dimension excluded nothing today".
    components["exclusion_reason"] = (
        exclusion_reason if measured["n_excluded"] else None
    )
    # VACUITY, ONE SIDE OR BOTH (atom D22 widened this from the overdue side
    # alone): the headline needs BOTH classes, so name whichever is missing and
    # say the headline is undefined rather than letting the surviving half be
    # read as the whole measurement.
    empty = [name for name, key in (("truly-overdue", "n_truly_overdue"),
                                    ("truly-current", "n_truly_current"))
             if measured[key] == 0]
    if empty:
        components["vacuity"] = (
            f"NO {' and no '.join(empty)} invoices in this population: the "
            "measures denominated on it are UNDEFINED (None), not 0.0, and so "
            "is the balanced headline -- a company that cannot make an error in "
            "one direction has not been shown not to make it. A vacuous "
            "population is not a perfect one."
        )

    baseline = (
        "NONE -- absolute ordinal displacement in buckets "
        f"{'/'.join(str(b) for b in order)}, balanced over the two truth "
        "classes; there is no no-skill divisor here and 1.0 does not mean 'no "
        "better than blind'."
    )
    return GapResult(
        metric="ageing",
        gap=(None if headline is None else float(headline)),
        raw_gap=float(headline) if headline is not None else 0.0,
        g0=0.0,
        baseline=baseline,
        components=components,
        note=(
            "BALANCED debt-DATE displacement (buckets) -- the mean of the "
            "displacement over the truly-overdue invoices and the displacement "
            "over the truly-current ones, each on its own denominator (atom "
            "D22, superseding the truly-overdue-only headline: an indiscriminate "
            "over-ager scored that one 0.000000). The two error RATES are "
            "reported separately on the same denominators: "
            "understated_arrears_rate (debt believed settled) and "
            "overstated_arrears_rate (the AGEING-REPORT OVERSTATEMENT at `as_of` "
            "-- NOT the wrongful-dunning exposure, which is a different "
            "measurement over a different belief population and is published by "
            "the detection dimension; atom D16). R12: every one of them is a "
            "diagnostic, never a target."
        ),
    )


def format_ageing_summary(result: GapResult) -> str:
    """Render an `ageing_gap` result for a log line / ledger note as THREE
    measures with their units, never as a bare scalar.

    This is the D7 anti-decay mechanism, not decoration: the old dimension went
    wrong the moment a bare `ageing 1.1538` could be read as a normalised score,
    so no consumer of this module prints the headline without its unit and its
    two directional rates beside it. Handles the vacuous population (`None`
    measures) without pretending it scored zero."""
    c = result.components

    def _num(key: str, fmt: str) -> str:
        v = c.get(key)
        return "undefined (no such population)" if v is None else format(v, fmt)

    n_excluded = c.get("n_excluded") or 0
    # THE EXCLUSION RIDES WITH THE RATE IT MOVES (D10's published-not-silent rule,
    # carried across by D16). A denominator that has had a band removed from it
    # must say so wherever it is printed -- otherwise the alignment that made the
    # two dimensions comparable is invisible at exactly the sites where a reader
    # compares them.
    excl = ""
    if n_excluded:
        excl = (
            "; " + str(n_excluded) + " case(s) in neither population: "
            + str(c.get("exclusion_reason"))
        )
    return (
        "ageing displacement " + _num("balanced_bucket_displacement", ".3f")
        + " buckets, BALANCED over both directions"
        + " [no baseline; not a 0-1 ratio]"
        + " (understated_arrears_rate " + _num("understated_arrears_rate", ".4f")
        + " over " + str(c.get("n_truly_overdue")) + " truly-overdue"
        + ", overstated_arrears_rate " + _num("overstated_arrears_rate", ".4f")
        + " over " + str(c.get("n_truly_current")) + " truly-current"
        + " = the ageing-report overstatement at as_of, NOT the wrongful-dunning"
        + " exposure (atom D16)"
        # BOTH HALVES RIDE WITH THE HEADLINE (atom D22), for the same anti-decay
        # reason the two rates do: this dimension went wrong the moment a bare
        # scalar could be read as something it is not, and the balanced headline
        # cannot say WHICH direction it came from.
        + "; the headline's two halves: mean_bucket_displacement "
        + _num("mean_bucket_displacement", ".3f")
        + " buckets of UNDER-dating over the truly-overdue and"
        + " mean_overstatement_displacement "
        + _num("mean_overstatement_displacement", ".3f")
        + " buckets of OVER-ageing over the truly-current -- the headline is"
        + " their mean and cannot say which direction it came from (atom D22)"
        + excl + ")"
    )


# ---------------------------------------------------------------------------
# (f) Prediction-error gap -- a continuous target (W1_6 weather->price)
# ---------------------------------------------------------------------------

def prediction_gap(truth_values: Sequence[float], belief_values: Sequence[float],
                   *, prior_value: Optional[float] = None) -> GapResult:
    """Continuous prediction gap (formula f): how far the company's real-valued
    belief is from the SIM ground truth, normalised to a NO-SKILL baseline.

        raw_gap = mean| belief - truth |                       # company MAE
        g0      = mean| prior  - truth |                       # no-skill MAE
        gap     = raw_gap / g0

    The no-skill `prior` is the climatological mean of `truth` (predict the
    average every time) when not given -- the blind guess a supplier with no
    weather model would make. So:
        gap = 0   perfect recovery (for a wall-respecting pair == a leak, design 1.2)
        gap = 1   no better than the climatological mean
        gap > 1   WORSE than blind (the model actively mis-extrapolates) -- the
                  honest cold-and-still-tail finding for a linear belief facing a
                  convex merit order.

    Used by the W1_6 <-> weather-price-belief pair: `truth_values` is the SIM
    chain's DERIVED price (`sim/weather_price_chain.derive_price`), `belief_values`
    is the company's linear weather->price expectation -- computed from DIFFERENT
    machinery (a convex composed physics chain vs an observables-only linear
    regression), so the gap is a real form-inadequacy measurement, not a
    tautology (R15 independence). FAIL-LOUD on empty/mismatched input."""
    import numpy as np

    truth = np.asarray(list(truth_values), dtype=float)
    belief = np.asarray(list(belief_values), dtype=float)
    if truth.size == 0:
        raise ValueError("prediction_gap: empty population")
    if truth.shape != belief.shape:
        raise ValueError(f"truth/belief length mismatch: {truth.shape} vs {belief.shape}")

    prior = float(np.mean(truth)) if prior_value is None else float(prior_value)
    raw_gap = float(np.mean(np.abs(belief - truth)))
    g0 = float(np.mean(np.abs(prior - truth)))
    baseline = (
        f"no-skill = predict the climatological mean truth ({prior:.3f}); "
        f"MAE_noskill={g0:.4f}"
    )
    return _normalise(
        raw_gap, g0, baseline, "prediction",
        components={"mae_model": round(raw_gap, 6), "mae_noskill": round(g0, 6),
                    "prior": round(prior, 6), "n": int(truth.size),
                    "bias_model": round(float(np.mean(belief - truth)), 6)},
        note="continuous prediction MAE normalised to the climatological-mean baseline",
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
