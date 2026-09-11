"""Which of the company's wins this machine settles, chosen for DIFFERENCE and carrying a weight.

WHAT THIS REPLACES, AND WHY A COUNT RULE WAS THE WRONG SHAPE
------------------------------------------------------------
`net_new_acquisition`'s sampling pass took every 1-in-5.57 of the campaign's wins by position:
`int((i+1)*r) > int(i*r)`. That is a correct and unbiased estimator of a COUNT — each year's
booked wins come out proportional to that year's funnel wins, and one scalar (`1/r`) inflates the
settled book back to the commercial one. It is also completely blind to what the homes are. It
refused 412 of 502 wins on this base by a rule that could not see a single attribute of any of
them, and the director's words are that the settlement budget should be the constraint we argue
about rather than one that silently refuses.

Two things follow, and only the second is obvious.

**The book we settle is a SAMPLE and it is the only population most figures are computed over.**
Margin, carbon, the intervention ranking — all of them sum over the settled accounts. A sample
that reproduces the population's *count* by year but not its *distribution* over the demand axes
is a sample every one of those figures is biased on, in a direction nobody has measured.

**And at this size, choosing beats counting.** The settled book is ~90 accounts out of ~500
candidates. That is exactly the regime where deliberate choice earns something and where the
world's 4,400-home stock does not (`0d86d6dfe` measured 1.04x there and REFUSED the same design
into `premise_population`; that refusal stands and this is not it).

WHAT IS CHOSEN OVER, AND IT IS NOT A COMMIT
--------------------------------------------
The feature matrix is read off `fabric_physics.fabric_parameters(household)` — the five fabric
quantities the demand model is actually a function of — plus `customer_years`. Nothing here names
`floor_area_band` or any other attribute added by one commit, and that is deliberate rather than
incidental: the demand axes evaluate on any `Household` this repository can draw, and they resolve
a RICHER home the moment the draw carries more. A module keyed to "has the fitted-joint draw
landed" would be a module that has to be edited when it does.

`tools/demand_vector_coverage` supplies the choosing and the weighting and neither is reimplemented
here. What is here is the part that module cannot know: a customer-year BUDGET is not a count, so
the number of cases is not given — it is solved for.

THE SIXTH AXIS IS TIME, AND IT IS WHAT REPLACES PER-YEAR PROPORTIONALITY
------------------------------------------------------------------------
Chosen-for-difference and proportional-by-count are OPPOSED criteria — the same opposition the
demand-vector canon names between spanning a support and reproducing a distribution. So the count
proportionality the old rule gave by construction cannot be kept, and culling within each year to
recover it would put the count rule straight back.

`customer_years` therefore enters the FIT as an axis. Within one campaign it is a strictly
decreasing function of the in-market date, so matching its CDF is matching the campaign's own time
marginal: each year's summed weight estimates that year's funnel wins. The reconstruction is then a
property that can be MEASURED AND CAN FAIL, where the old arithmetic's version could not be wrong.

It is also the whole of why the inflation stops being one number. `1/0.1796` multiplies every
settled account by 5.57 whatever it is; a per-account weight can be disagreed with.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

#: The axes a settled account is chosen and weighted over: three physical, one temporal. Named here
#: rather than inlined because the choosing, the fit and the published diagnostic must all be over
#: the SAME list, and three copies of a tuple is how they come to differ.
#:
#: THIS LIST WAS SIX AXES FOR ONE AFTERNOON AND THREE OF THEM WERE THE SAME NUMBER. The first draft
#: took the whole of `fabric_parameters` — `volume_m3`, `solar_aperture_m2` and `internal_gain_kw`
#: alongside these. Printed at real inputs over the 502 candidates, those three came back with a
#: pairwise correlation of **exactly 1.000** and identical KS distances to five decimal places in
#: both arms. They are not three measurements that happen to agree on this base: they are
#: `area * _STOREY_HEIGHT_M`, `area * _WINDOW_AREA_RATIO * _SOLAR_TRANSMITTANCE * _FRAME_FACTOR`
#: and `area * _INTERNAL_GAIN_W_PER_M2 / 1000` — one quantity in three units, by construction, for
#: every household on every base.
#:
#: Carrying all three would have weighted FLOOR AREA three times against infiltration's once, in
#: both the standardised distance the medoids are chosen by and the least squares the mass is
#: solved from — so the sample would have been chosen for difference in size while reporting that
#: it was chosen for difference in behaviour. `floor_area_m2` is carried once, under its own name,
#: because that is what the axis is.
#:
#: Caught by printing the table before shipping the formula, which is the only thing that could
#: have caught it: every test I would have written would have passed.
CHOICE_AXES = (
    "floor_area_m2",
    "fabric_w_per_k",
    "raw_infiltration_ach",
    "customer_years",
)


def demand_vector(prospect, customer_years: float):
    """This candidate's position on `CHOICE_AXES`, or `None` if it has no home to place.

    `None` IS A REFUSAL AND NEVER A ZERO. A prospect with no premise — an SME or I&C draw, or any
    draw made without a premise stock — is not a household at the origin of the fabric space; it is
    a household this instrument cannot see. Returning a zero vector for it would put every such
    candidate at one point and make it the densest cluster in the population.
    """
    premise = getattr(prospect, "premise", None)
    if premise is None:
        return None
    household = getattr(premise, "household", None)
    if household is None:
        return None

    from simulation import fabric_physics as fp

    p = fp.fabric_parameters(household)
    return (float(p.floor_area_m2), float(p.fabric_w_per_k), float(p.raw_infiltration_ach),
            float(customer_years))


def _fuel_of(prospect) -> str:
    """The fuel whose register is read for heat, for the WITHIN-FUEL extremes.

    The chooser takes each axis's extreme inside every fuel as well as overall, because the
    minority fuel's tail is not the population's tail — the canon's own reason, and it is why this
    is passed rather than left to the clustering to rediscover.
    """
    premise = getattr(prospect, "premise", None)
    return getattr(premise, "commodity", "unknown") if premise is not None else "unknown"


def _with_year_cover(values, chosen, years, seed: int):
    """The chosen set, plus one representative of every year it left out entirely.

    A YEAR WITH NO CHOSEN ACCOUNT CANNOT BE RECONSTRUCTED AT ANY WEIGHT, and that is a structural
    hole rather than a bad fit. The weights are solved over the chosen accounts only, so a year
    none of them belongs to has no column to put mass on: its published bar is zero, whatever the
    company won that year, and no amount of fitting can move it.

    FOUND BY A CONTROL AND NOT BY THE REAL RUN (2026-09-11). On the shipped campaign every one of
    the ten years happened to get an account and the hole never opened.
    `test_the_sample_is_PROPORTIONAL_in_every_year_and_not_merely_non_empty`'s ten-year fixture put
    2022's 40 funnel wins against a settled estimate of 0.0 on its first run after the wiring.

    The representative is that year's MEDOID -- the real candidate closest to the year's own centre
    in the standardised space -- and not its cheapest or its first. Cheapest would load every
    covered year onto its shortest tail, which is the first-come bias the whole two-pass design
    exists to remove; first would make the answer depend on the pool's ordering.
    """
    import numpy as np

    years = np.asarray(years)
    chosen = np.asarray(chosen)
    mean = values.mean(axis=0)
    sd = values.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    z = (values - mean) / sd

    covered = set(years[chosen].tolist())
    extra = []
    for year in sorted(set(years.tolist())):
        if year in covered:
            continue
        members = np.flatnonzero(years == year)
        centre = z[members].mean(axis=0)
        extra.append(int(members[int(np.argmin(np.sum((z[members] - centre) ** 2, axis=1)))]))
    if not extra:
        return chosen
    return np.array(sorted(set(chosen.tolist()) | set(extra)))


def _largest_affordable_k(values, fuel, costs, headroom_cy: float, seed: int, years=None):
    """The biggest `k` whose chosen set fits inside the customer-year headroom.

    THE BUDGET IS IN CUSTOMER-YEARS AND THE CHOOSER SELECTS BY COUNT, so `k` is not given by the
    budget the way `1/r` was — it has to be solved for. Bisection, because the cost is monotone
    ENOUGH in `k` and each probe costs one k-means fit.

    "MONOTONE ENOUGH" IS NOT "MONOTONE", and saying so is the point of this sentence. A chosen set
    is medoids PLUS a fixed frame of axis and within-fuel extremes; raising `k` moves the medoids
    and can, in principle, land on a cheaper set. So the bisection finds a large affordable `k`
    rather than provably the largest, and the value that is load-bearing — never exceeding the
    ceiling — is checked on the returned set rather than inferred from the search. A search that
    reports the ceiling it was solving for, on the strength of the property it assumed, is the
    shape that publishes a bound nobody tested.
    """
    import numpy as np

    from tools.demand_vector_coverage import choose_for_difference

    lo, hi = 1, len(values)
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        chosen = choose_for_difference(values, mid, seed=seed, fuel=fuel)
        if years is not None:
            # COVERED BEFORE THE COST IS CHECKED, never after. The cover can only ADD accounts, so
            # pricing the uncovered set and then covering it would report a bound the returned set
            # does not meet -- the ceiling would be crossed by exactly the repair that made the
            # sample publishable.
            chosen = _with_year_cover(values, chosen, years, seed)
        if float(np.asarray(costs)[chosen].sum()) <= headroom_cy:
            best = (mid, chosen)
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def choose_settled_sample(candidate_vectors, candidate_costs_cy, candidate_fuels,
                          *, headroom_cy: float, seed: int = 0, candidate_years=None):
    """Which candidates to settle, and the mass of commercial wins each one stands for.

    Returns `None` when the sample cannot be chosen, and every `None` is a REFUSAL WITH A REASON
    the caller is expected to say out loud:

      * any candidate has no home to place (`demand_vector` returned `None`) — a partly-chosen,
        partly-culled book would be a third population nobody named;
      * not even `k=1` fits the headroom — the fixed frame of extremes alone costs more than the
        budget, which is a real operating state (a deep enough opening book leaves no headroom at
        all) and not a hypothetical.

    On success: `{"positions", "weights", "k", "chosen_cost_cy", "zero_weight"}`. `weights` are in
    COMMERCIAL WINS — they sum to the candidate count, so a settled account's weight is directly
    the number of the company's own wins it stands in for, and the old scalar `1/rate` is the value
    every weight would take if the sample were still uniform.
    """
    import numpy as np

    from tools.demand_vector_coverage import _Reference, fit_weights

    if any(v is None for v in candidate_vectors):
        return None

    values = np.asarray(candidate_vectors, dtype=float)
    costs = np.asarray(candidate_costs_cy, dtype=float)
    fuel = np.asarray(candidate_fuels)

    solved = _largest_affordable_k(values, fuel, costs, headroom_cy, seed,
                                   years=candidate_years)
    if solved is None:
        return None
    k, chosen = solved

    reference = _Reference(values, CHOICE_AXES)
    # THE YEAR MARGINAL IS A CONSTRAINT, NOT AN AXIS, and this is a REPAIR of what was measured
    # rather than a design decision taken in advance. `customer_years` alone, as one CDF axis among
    # the others, reconstructed 2017 at +84.9% against its funnel wins -- the campaign total was
    # exact and the composition inside it was not, which is precisely the shape that publishes a
    # correct headline over a wrong growth curve. A per-year row states the quantity the page
    # actually renders; a CDF over customer-years only implies it, and an implication that has to
    # win against every other axis for 89 free parameters loses.
    #
    # `customer_years` STAYS on `CHOICE_AXES` regardless, because the CHOOSING has no constraint
    # rows -- it is the only thing that stops the medoids collapsing onto one year of the campaign.
    weights = fit_weights(values, chosen, reference, groups=candidate_years)
    total = float(weights.sum())
    if total <= 0:
        # NNLS RETURNED NOTHING, which `fit_weights` already guards by falling back to ones --
        # this is the belt on that brace and it is here because a zero-weight book publishes a
        # commercial figure of zero rather than failing.
        return None
    # In COMMERCIAL WINS, not in probability: the sum is the candidate count, so each weight reads
    # as "this account stands for N of the company's own wins" on the page without a second
    # multiplication that some reader has to know about.
    weights = weights / total * len(values)

    chosen_cost = float(costs[chosen].sum())
    # THE INVARIANT IS CHECKED ON THE ANSWER, not assumed from the search. See
    # `_largest_affordable_k`'s note on why the two are different claims.
    if chosen_cost > headroom_cy:
        return None

    return {
        "positions": [int(i) for i in chosen],
        "weights": [float(w) for w in weights],
        "k": int(k),
        "chosen_cost_cy": chosen_cost,
        # A SETTLED ACCOUNT THE FIT GAVE ZERO MASS spent budget and stands for nothing. It is a
        # real outcome of a non-negative least squares — the case is on the book because it was
        # chosen as a distinct region, and the fit found the population reproducible without it --
        # and it is counted here rather than dropped, because dropping it would change the fit
        # that produced it and reporting it is how the count can be argued with.
        "zero_weight": int((np.asarray(weights) <= 0.0).sum()),
    }
