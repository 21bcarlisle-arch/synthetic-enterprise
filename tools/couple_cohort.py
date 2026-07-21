"""COUPLED-TRIAD runner for the segmentation cohort pair (SEGMENTATION_
GENERATOR_BUILD_PLAN.md step 4; template `tools/couple_w2_4_c6.py`).

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the
ONLY layer permitted to hold the hidden SIM truth cohort
(`simulation.population_draw.Cohort`) and the company's observable-only
believed cohort (`company.analytics.cohort_discovery.BelievedCohort`) side by
side to compute the belief-vs-truth GAP (COUPLED_TRIAD_DESIGN.md 1.3; same
role as `background/gap_metric.py` and `tools/couple_w2_4_c6.py`). It lives in
tools/ -- NOT under company/ or saas/ -- so it is not scanned by the epistemic
verifier and may legitimately import `simulation.*`.

THE COUPLED LOOP (3 loops, COUPLED_TRIAD):

  1. SIM adds depth   -- simulation.population_draw.assign_cohort (W2_2) draws
                         each customer's HIDDEN 9-axis cohort: the tenure-
                         conditioned observed block (accommodation/cars/nssec),
                         heating_fuel pinned to region, and the curriculum-
                         drawn attitude/sensitivity axes (green_stance/
                         price_sensitivity/channel_pref). The company NEVER
                         reads any of it directly.
  2. COMPANY copes    -- the hidden price_sensitivity/channel_pref produce
                         NOISY OBSERVABLE signals (a churn-estimate response,
                         actual contact-channel usage) via the INDEPENDENT SIM
                         PHYSICS below; company.analytics.cohort_discovery (the
                         D-SEGMENT twin) infers each customer's believed cohort
                         from those observables + its own public-prior/census
                         tables ALONE. tenure/region/heating_fuel are close to
                         directly observable; accommodation/cars/nssec have NO
                         discovery mechanism at all (the wall map names none) --
                         the belief for those three axes never moves off the
                         company's own flat national prior, regardless of the
                         tenure the company already knows.
  3. HARNESS measures -- belief_gap(truth_dist, belief_dist, prior): per
                         (axis, TRUE-tenure cell), the total-variation distance
                         between the axis's TRUE distribution within that cell
                         and the company's BELIEVED distribution for the same
                         members, normalised to the company's own blind
                         national prior. worst_cell_score = the max gap among
                         cells clearing a minimum-support bar; worst3_mean_gap
                         is reported alongside (redundancy guard,
                         `cohort_schema.json`'s own `worst_cell_redundancy: 3`).

R15 INDEPENDENCE / R12-R13 NO-GOAL-SEEK. Three separately-authored pieces meet
here and none is fitted to the others: the SIM cohort draw (population_draw.py,
director curriculum), the truth->observable SIM PHYSICS below (this harness's
own, independent of both sides), and the company's discovery thresholds
(cohort_discovery.py, set blind to the SIM curriculum). The gap is therefore a
real measurement, not a tautology.

WORST-CELL KNEE, HONEST SIMPLIFICATION (R10, dated 2026-07-21): BUILD_PLAN §4
asks that only cells "clearing the learning-value knee" (`build_learning_
frontier.py` re-derived on the merged schema) count toward worst_cell_score.
Re-deriving that full frontier for this specific per-cell gap is a materially
larger, separate analysis pass (population_coverage's own generator + outcome
model), not attempted here. This harness applies a SUPPORT-ONLY proxy instead
(a cell must have >= N_MIN members to be eligible) -- a necessary but not
sufficient condition for the real knee test, explicitly flagged as a proxy,
not silently presented as the full knee computation.

DETERMINISM (C-S2). Every RNG is seeded from a stable hash of its named
inputs. No unseeded randomness, no wall-clock. `measured_at`/`run_git_commit`
for the ledger are gathered by this harness (not by gap_metric, which never
calls a clock).
"""
from __future__ import annotations

import argparse
import hashlib
import random
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from simulation.population_draw import Cohort, assign_cohort, TENURE_LEVELS

from company.analytics.cohort_discovery import (
    ACCOMMODATION_LEVELS,
    CARS_LEVELS,
    NSSEC_LEVELS,
    BelievedCohort,
    InteractionObservation,
    PublicPriorObservation,
    discover_cohort,
)

from background.gap_metric import belief_gap, write_gap_entry, GapResult

WORLD_ATOM_ID = "W2_2_population_draw"
TWIN_ATOM_ID = "C_cohort_discovery"

# Minimum cell support to be eligible for the worst-cell score (R10 knee proxy,
# see module docstring).
N_MIN = 30

PRICE_SENSITIVITY_LEVELS = ("high", "medium", "low")
CHANNEL_PREF_LEVELS = ("digital", "phone", "assisted")

# Axes this harness scores, each with its own level tuple.
_SCORED_AXES: Dict[str, Tuple[str, ...]] = {
    "accommodation": ACCOMMODATION_LEVELS,
    "cars": CARS_LEVELS,
    "nssec": NSSEC_LEVELS,
    "price_sensitivity": PRICE_SENSITIVITY_LEVELS,
    "channel_pref": CHANNEL_PREF_LEVELS,
}

# accommodation/cars/nssec have NO discovery mechanism in cohort_discovery.py
# (the wall map names none) -- `BelievedCohort` carries a single best-guess
# LABEL for these (the modal category, useful as a per-customer default), but
# the HONEST aggregate belief for a whole cell is the full smooth national
# prior DISTRIBUTION, not a re-aggregated point mass (collapsing every
# customer to the same single label and then re-aggregating would understate
# the company's own stated uncertainty -- a modelling artefact, not a real
# finding). price_sensitivity/channel_pref DO have a discovery mechanism (a
# noisy but genuinely per-customer-differentiated observable), so their
# per-customer BelievedCohort labels are aggregated empirically, same as any
# other coupled-triad belief composition (`couple_w2_4_c6.py`'s own pattern).
_NO_DISCOVERY_AXES = frozenset({"accommodation", "cars", "nssec"})


def _rng(*parts) -> random.Random:
    """Deterministic RNG from a stable sha256 of the given parts (C-S2)."""
    key = ":".join(str(p) for p in parts)
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
    return random.Random(seed)


# ---------------------------------------------------------------------------
# SIM PHYSICS (harness-side, holds theta). Converts the hidden truth cohort
# into NOISY OBSERVABLES -- the only channel the company gets. Independent of
# both the SIM curriculum and the company's discovery thresholds (R15).
# ---------------------------------------------------------------------------

# True price_sensitivity -> the base rate-change churn-estimate response a
# customer of that true sensitivity tends to show. Illustrative (R10), NOT a
# cited table -- exists only so a noisy, genuinely-informative-but-imperfect
# observable exists for the company to threshold.
_CHURN_ESTIMATE_BASE: Dict[str, float] = {"high": 0.65, "medium": 0.35, "low": 0.10}
_CHURN_ESTIMATE_NOISE_SD = 0.15

# True channel_pref -> the pool of actual contact channels a customer of that
# true preference tends to use (weighted by repetition, drawn with replacement).
_CHANNEL_OBS_POOL: Dict[str, List[str]] = {
    "digital": ["app", "app", "app", "web", "phone"],
    "phone": ["phone", "phone", "phone", "app"],
    "assisted": ["post", "branch", "phone", "post"],
}

# Fraction of customers who decline to disclose tenure at signup (C-S1: an
# absent observable is simply absent). Illustrative (R10).
_TENURE_NONDISCLOSURE_RATE = 0.15


def _true_price_sensitivity_to_churn_estimate(true_ps: str, rng: random.Random) -> float:
    base = _CHURN_ESTIMATE_BASE[true_ps]
    noisy = base + rng.gauss(0.0, _CHURN_ESTIMATE_NOISE_SD)
    return max(0.0, min(0.95, noisy))


def _true_channel_pref_to_observed_channels(true_cp: str, rng: random.Random, n: int = 3) -> List[str]:
    pool = _CHANNEL_OBS_POOL[true_cp]
    return [rng.choice(pool) for _ in range(n)]


def _observation_pair_for(truth: Cohort, i: int) -> Tuple[PublicPriorObservation, InteractionObservation]:
    """Build the (public-prior, interaction) observation pair a real supplier
    would hold for this customer, derived from -- but never equal to -- the
    hidden truth cohort."""
    r = _rng("cohort_obs", truth.customer_id, i)
    tenure_disclosed = None if r.random() < _TENURE_NONDISCLOSURE_RATE else truth.tenure
    prior_obs = PublicPriorObservation(
        customer_id=truth.customer_id,
        region=truth.region,
        tenure=tenure_disclosed,
        heating_fuel=truth.heating_fuel,  # EPC/MPRN read -- near-exact per the wall map
    )
    churn_estimate = _true_price_sensitivity_to_churn_estimate(truth.price_sensitivity, r)
    channels = _true_channel_pref_to_observed_channels(truth.channel_pref, r)
    interaction_obs = InteractionObservation(
        customer_id=truth.customer_id, churn_estimate=churn_estimate, contact_channels_used=channels,
    )
    return prior_obs, interaction_obs


def build_scenario(n_customers: int, base_seed: int = 20260721) -> Tuple[List[Cohort], List[BelievedCohort]]:
    """Draw n_customers' TRUE cohorts and the company's BELIEVED cohorts for
    the same population. One customer_id per draw, deterministic in base_seed."""
    truths: List[Cohort] = []
    beliefs: List[BelievedCohort] = []
    for i in range(n_customers):
        cid = f"COHORT{i:06d}"
        truth = assign_cohort(cid, base_seed)
        prior_obs, interaction_obs = _observation_pair_for(truth, i)
        belief = discover_cohort(prior_obs, interaction_obs)
        truths.append(truth)
        beliefs.append(belief)
    return truths, beliefs


def _cell_distribution(values: List[str], levels: Tuple[str, ...]) -> List[float]:
    counts = {lvl: 0 for lvl in levels}
    for v in values:
        if v in counts:
            counts[v] += 1
    total = sum(counts.values())
    if total == 0:
        raise ValueError("empty cell distribution")
    return [counts[lvl] / total for lvl in levels]


def _national_prior_vector(axis: str, levels: Tuple[str, ...]) -> List[float]:
    """The company's OWN blind national prior for `axis` (the belief_gap g0
    normaliser) -- read from cohort_discovery's own duplicated prior tables
    where one exists, else a uniform prior (price_sensitivity/channel_pref
    have no pre-interaction company prior table -- a uniform guess is the
    honest "zero information" baseline for those two)."""
    from company.analytics import cohort_discovery as cd
    table = {
        "accommodation": cd.ACCOMMODATION_PRIOR,
        "cars": cd.CARS_PRIOR,
        "nssec": cd.NSSEC_PRIOR,
    }.get(axis)
    if table is not None:
        return [table[lvl] for lvl in levels]
    return [1.0 / len(levels)] * len(levels)


def score_worst_cell(truths: List[Cohort], beliefs: List[BelievedCohort],
                     n_min: int = N_MIN) -> dict:
    """Per (axis, TRUE-tenure cell) belief_gap; worst_cell_score = max gap
    among cells with support >= n_min (R10 knee proxy, see module docstring);
    worst3_mean_gap = mean of the 3 highest-support-eligible gaps."""
    by_tenure: Dict[str, List[int]] = {t: [] for t in TENURE_LEVELS}
    for idx, truth in enumerate(truths):
        by_tenure[truth.tenure].append(idx)

    cell_results: List[dict] = []
    for tenure_cell, idxs in by_tenure.items():
        n = len(idxs)
        eligible = n >= n_min
        if n == 0:
            # An empty tenure cell (possible only at very small n_customers)
            # can never be eligible and has no distribution to compute --
            # skip it rather than crashing on an empty-population TV call.
            continue
        for axis, levels in _SCORED_AXES.items():
            truth_vals = [getattr(truths[i], axis) for i in idxs]
            truth_dist = _cell_distribution(truth_vals, levels)
            prior = _national_prior_vector(axis, levels)
            if axis in _NO_DISCOVERY_AXES:
                # No discovery mechanism -> the honest cell belief IS the
                # smooth national prior (never a re-aggregated point mass).
                belief_dist = list(prior)
            else:
                belief_vals = [getattr(beliefs[i], axis) for i in idxs]
                belief_dist = _cell_distribution(belief_vals, levels)
            result = belief_gap(truth_dist, belief_dist, prior=prior)
            cell_results.append({
                "axis": axis,
                "tenure_cell": tenure_cell,
                "n_in_cell": n,
                "eligible": eligible,
                "gap": result.gap,
                "raw_tv": result.components.get("tv"),
            })

    eligible_results = [c for c in cell_results if c["eligible"] and c["gap"] is not None]
    if not eligible_results:
        raise ValueError(
            f"score_worst_cell: no cell cleared the n_min={n_min} support bar "
            f"(largest cell(s): {sorted(cell_results, key=lambda c: -c['n_in_cell'])[:1]})"
        )
    ranked = sorted(eligible_results, key=lambda c: -c["gap"])
    worst = ranked[0]
    worst3 = ranked[: min(3, len(ranked))]
    worst3_mean = sum(c["gap"] for c in worst3) / len(worst3)

    return {
        "worst_cell_id": f"{worst['axis']}::tenure={worst['tenure_cell']}",
        "worst_cell_gap": worst["gap"],
        "worst3_mean_gap": round(worst3_mean, 6),
        "n_in_cell": worst["n_in_cell"],
        "n_min": n_min,
        "n_cells_eligible": len(eligible_results),
        "n_cells_total": len(cell_results),
        "all_cells": cell_results,
    }


def measure(n_customers: int = 3000, base_seed: int = 20260721, n_min: int = N_MIN):
    """Run the coupled loop end to end. Returns (GapResult, worst-cell dict)."""
    truths, beliefs = build_scenario(n_customers, base_seed)
    worst = score_worst_cell(truths, beliefs, n_min=n_min)

    result = GapResult(
        metric="belief",
        gap=worst["worst_cell_gap"],
        raw_gap=worst["worst_cell_gap"],
        g0=1.0,
        baseline="per-(axis, true-tenure-cell) TV distance normalised to the company's own blind national prior; worst_cell_score = max gap among cells with support >= n_min (R10 knee-support proxy, see module docstring)",
        components={
            "worst_cell_id": worst["worst_cell_id"],
            "worst3_mean_gap": worst["worst3_mean_gap"],
            "n_in_cell": worst["n_in_cell"],
            "n_min": worst["n_min"],
            "n_cells_eligible": worst["n_cells_eligible"],
            "n_cells_total": worst["n_cells_total"],
            "n_customers": n_customers,
        },
        note=(
            "Worst-cell belief-vs-truth gap over the D-SEGMENT cohort taxonomy "
            "(accommodation/cars/nssec/price_sensitivity/channel_pref), cells "
            "keyed by the company's OWN known tenure (public prior). "
            "accommodation/cars/nssec have NO discovery mechanism company-side "
            "(honest R10 gap) -- their gap sits at/near 1.0 by construction, "
            "correctly reporting zero learned skill; price_sensitivity/"
            "channel_pref have a noisy discovery mechanism and show partial "
            "learning."
        ),
    )
    return result, worst


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=20260721)
    ap.add_argument("--n-min", type=int, default=N_MIN)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    result, worst = measure(args.customers, args.seed, args.n_min)

    print("W2_2 cohort draw <-> C_cohort_discovery coupled segmentation scenario")
    print(f"  customers                : {args.customers}")
    print(f"  cells eligible/total     : {worst['n_cells_eligible']}/{worst['n_cells_total']} (n_min={worst['n_min']})")
    print(f"  WORST CELL               : {worst['worst_cell_id']}  (n={worst['n_in_cell']})")
    print(f"  worst_cell_gap           : {worst['worst_cell_gap']}")
    print(f"  worst3_mean_gap          : {worst['worst3_mean_gap']}")
    print("  per-cell detail:")
    for c in sorted(worst["all_cells"], key=lambda c: -(c["gap"] or 0)):
        flag = "" if c["eligible"] else "  (below n_min, excluded)"
        print(f"    {c['axis']:<18} tenure={c['tenure_cell']:<14} n={c['n_in_cell']:<5} gap={c['gap']}{flag}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
