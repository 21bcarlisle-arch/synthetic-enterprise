"""Is EP1's graded population a sample of the book, or the accounts that lost?

HARNESS. Like `tools/couple_clv.py`, which imports it, this sits OUTSIDE the
epistemic wall and is permitted to hold the company's belief and the world's
outcome side by side.

=============================================================================
WHY THIS MODULE EXISTS: A SCALE ERROR HAS TWO CAUSES AND ONE WAS UNCONSIDERED
=============================================================================

`couple_clv.magnitude_diagnostic` reports `best_single_scale` -- the one
constant that, applied to every belief, minimises the error. On 2026-08-26 it
returned 0.204 with 27 of 33 accounts over-estimated, and its own docstring
read that as pointing "R4 at the horizon, not the ranking". A whole stretch of
work was then aimed at the lifetime term on the strength of that sentence.

The sentence is incomplete, and the omission is not cosmetic. A uniform scale
error has TWO possible causes:

  1. THE ESTIMATOR is systematically too large -- what the docstring assumed.
  2. THE GRADED POPULATION is not a sample of the population the estimator was
     formed over -- and if the two differ in the very quantity being predicted,
     a perfectly calibrated estimator scores as a uniform over-estimate.

Cause 2 is not hypothetical here; it is structural. `build_observations` counts
an account only if its life COMPLETED inside the run, and excludes every
still-supplied account as `right_censored_lifetime`. That is unavoidable -- you
cannot know a realised lifetime for a customer who is still alive -- but it
means the graded population is EXACTLY the accounts that left, selected on the
outcome, and correlated with lifetime value by construction.

So the two causes must be reported together or neither can be read. That is what
this module is for, and `test_clv_gap_selection.py` holds `couple_clv` to it.

=============================================================================
WHAT IS MEASURED, AND WHAT EACH MEASUREMENT CANNOT SAY
=============================================================================

`selection_profile` -- the graded population's realised value against the
excluded population's, LIKE FOR LIKE BY SEGMENT. The segment split is not
decoration: this book's five I&C accounts carry ~500x a domestic account's
lifetime margin and are all still supplied, so a whole-book comparison reports a
45x selection shift that is mostly the absence of I&C from the graded set. The
honest number is the within-segment one.

  THE EXCLUDED SIDE IS CENSORED, and the direction is stated rather than
  discovered: a still-supplied account's realised total is only the part of its
  life the run has seen, and it is still accruing. So the reported shift is a
  LOWER BOUND on the true difference between the two populations.

`hazard_calibration` -- the company's believed per-renewal churn hazard against
the realised churn frequency at that hazard, bucketed. Independent of the CLV
arithmetic entirely: one side is `saas.churn_model`'s output, the other is a
count of `event_type == "churned"` in the world's own event log. This is the
measurement that says which way the lifetime term is wrong, and it can say
"not at all".

  It cannot say anything about buckets the run never populated, and it reports
  `n` per bucket so a reader can see which rows are worth reading.

`lifetime_level` -- the believed hazard recovered from the PUBLISHED horizons.
EP1 publishes `contract_term` and `tenure_expected` for each account-year; both
are the same margin times the same closed form at different terms, so their
RATIO depends on the hazard alone and inverts to it. This needs no re-run and no
private field: it reads the artefact the company published.

  It cannot recover a hazard where `contract_term` is zero or absent, and says
  so per account rather than dropping the row silently.
"""

import statistics
from collections import Counter, defaultdict

#: The horizon terms EP1 publishes, in years. `tenure_expected` uses `1/hazard`;
#: `contract_term` uses the account's contract term, which is one year for every
#: account this simulation writes (`saas.churn_model.CONTRACT_LENGTH_DAYS`).
CONTRACT_TERM_YEARS = 1.0

#: Must match `company.analytics.clv_three_horizon.DISCOUNT_RATE`. Read from the
#: published artefact where the run supplies it -- this is the fallback for a
#: run that predates the field, not the authority.
DEFAULT_DISCOUNT_RATE = 0.10

#: Below this the recovered hazard is at the edge of the invertible range and the
#: account is reported as unrecoverable rather than pinned to the boundary.
_HAZARD_FLOOR = 1e-5
_HAZARD_CEIL = 1.0 - 1e-6

UNAVAILABLE_NO_LIFETIMES = "run publishes no per_customer_lifetime"
UNAVAILABLE_NO_EVENTS = "run publishes no customer_events"
UNAVAILABLE_NO_SNAPSHOTS = "run publishes no three_horizon_clv_snapshots"
UNAVAILABLE_EMPTY = "empty graded population"


def _survival_annuity(margin_multiplier_hazard: float, term_years: float,
                      discount_rate: float) -> float:
    """`clv_three_horizon.survival_discounted_value_gbp` for a unit margin.

    Deliberately re-derived rather than imported. The company-side function is
    the thing being graded; a harness that inverts the graded function by
    calling it would be checking a value against itself (R15 TAUTOLOGY). This is
    the same closed form written independently, and
    `test_clv_gap_selection.py::test_the_harness_annuity_matches_the_company_form`
    asserts the two agree -- an agreement test between two implementations, not
    one implementation checking its own output.
    """
    if term_years <= 0:
        return 0.0
    retention = 1.0 - margin_multiplier_hazard
    if retention <= 0:
        return 0.0
    factor = 1.0 + discount_rate
    ratio = retention / factor
    denom = factor - retention
    if abs(denom) < 1e-12:
        return term_years
    return retention * (1.0 - ratio ** term_years) / denom


def _published_ratio(hazard: float, discount_rate: float) -> float:
    """`tenure_expected / contract_term` for a given hazard.

    Strictly decreasing in `hazard` over (0, 1): raising the hazard shortens
    `1/hazard` faster than it shortens the fixed contract term. That monotonicity
    is what makes the inversion below well-posed, and it is asserted rather than
    assumed in the tests.
    """
    denominator = _survival_annuity(hazard, CONTRACT_TERM_YEARS, discount_rate)
    if denominator <= 0:
        return float("nan")
    return _survival_annuity(hazard, 1.0 / hazard, discount_rate) / denominator


def recover_hazard(contract_term_gbp: float, tenure_expected_gbp: float,
                   discount_rate: float = DEFAULT_DISCOUNT_RATE) -> float | None:
    """The hazard EP1 used, recovered from the two horizons it published.

    Returns `None` -- never a boundary value -- when the ratio falls outside the
    invertible range, so a caller cannot mistake "could not recover" for "the
    hazard is 0.05". Bisection on a strictly monotone function: 200 halvings put
    the answer well inside float precision, with no RNG and no grid.
    """
    if not contract_term_gbp:
        return None
    target = tenure_expected_gbp / contract_term_gbp
    lo, hi = _HAZARD_FLOOR, _HAZARD_CEIL
    if not (_published_ratio(hi, discount_rate) < target
            < _published_ratio(lo, discount_rate)):
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _published_ratio(mid, discount_rate) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _realised(lifetime_entry) -> float | None:
    if not isinstance(lifetime_entry, dict):
        return None
    value = lifetime_entry.get("net_margin_after_cost_to_serve_gbp")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    return float(value)


def _summarise(values):
    return {
        "n": len(values),
        "mean_gbp": statistics.fmean(values) if values else None,
        "median_gbp": statistics.median(values) if values else None,
    }


def selection_profile(run: dict, counted: list) -> dict:
    """The graded population against the excluded one, like for like by segment.

    `counted` is `couple_clv.build_observations(...)["counted"]` -- the accounts
    the gap was actually computed over. Everything else in
    `per_customer_lifetime` is the excluded side.
    """
    lifetimes = run.get("per_customer_lifetime")
    if not isinstance(lifetimes, dict) or not lifetimes:
        return {"available": False, "reason": UNAVAILABLE_NO_LIFETIMES}
    graded_ids = {r["account"] for r in counted}
    if not graded_ids:
        return {"available": False, "reason": UNAVAILABLE_EMPTY}

    graded, excluded = defaultdict(list), defaultdict(list)
    for account_id, entry in lifetimes.items():
        value = _realised(entry)
        if value is None:
            continue
        segment = (entry.get("segment") if isinstance(entry, dict) else None) or "unknown"
        (graded if account_id in graded_ids else excluded)[segment].append(value)

    all_graded = [v for values in graded.values() for v in values]
    all_excluded = [v for values in excluded.values() for v in values]
    if not all_graded:
        return {"available": False, "reason": UNAVAILABLE_EMPTY}

    by_segment = {}
    for segment in sorted(set(graded) | set(excluded)):
        g, e = graded.get(segment, []), excluded.get(segment, [])
        mean_ratio = None
        if g and e and statistics.fmean(g):
            mean_ratio = statistics.fmean(e) / statistics.fmean(g)
        by_segment[segment] = {
            "graded": _summarise(g),
            "excluded_still_supplied": _summarise(e),
            "excluded_over_graded_mean": mean_ratio,
        }

    # The segment the grading actually rests on. Reporting a whole-book ratio as
    # the headline is what turns five I&C accounts into a 45x selection shift.
    dominant = max(graded, key=lambda s: len(graded[s]))
    dominant_row = by_segment[dominant]

    return {
        "available": True,
        "graded": _summarise(all_graded),
        "excluded_still_supplied": _summarise(all_excluded),
        "by_segment": by_segment,
        "dominant_graded_segment": dominant,
        "dominant_segment_share_of_graded": len(graded[dominant]) / len(all_graded),
        "like_for_like_excluded_over_graded": dominant_row["excluded_over_graded_mean"],
        "whole_book_excluded_over_graded": (
            statistics.fmean(all_excluded) / statistics.fmean(all_graded)
            if all_excluded and statistics.fmean(all_graded) else None
        ),
        "excluded_side_is_censored": True,
        "reading": (
            "The graded population is selected ON THE OUTCOME -- an account is "
            "counted only once its life has ENDED. Where the two populations "
            "differ in realised value, a perfectly calibrated estimator scores "
            "as a uniform over-estimate, so `error_decomposition."
            "best_single_scale` cannot be read as an estimator fault without "
            "this row beside it. The excluded side is still accruing, so "
            "`like_for_like_excluded_over_graded` is a LOWER BOUND. Read the "
            "like-for-like ratio, not the whole-book one: segments differ by "
            "orders of magnitude in this book. R12: diagnostic, never a target."
        ),
    }


def hazard_calibration(run: dict) -> dict:
    """The company's believed churn hazard against the frequency it realised.

    One side is `saas.churn_model.churn_probability`'s output as recorded at each
    renewal decision; the other is a COUNT of what happened at those same
    decisions (`event_type`). The two are independent -- a belief and a tally --
    which is what lets this row say which way the lifetime term is wrong.

    Note on the field: `customer_events["churn_probability"]` is the company's
    raw bill-shock base rate, and `simulation/customer_events.py` records in its
    own comment that this "was never the number the dice roll used" -- the roll
    used `realized_churn_probability`, after passive-cap, market, income-stress
    and satisfaction adjustment. That is precisely why this function grades the
    belief against OUTCOMES and not against the sim's other probability field:
    comparing two probabilities produced a spurious ~-80% error pattern once
    already, and counting what happened cannot repeat it.
    """
    events = run.get("customer_events")
    if not isinstance(events, list) or not events:
        return {"available": False, "reason": UNAVAILABLE_NO_EVENTS}

    buckets = defaultdict(lambda: {"decisions": 0, "churned": 0})
    believed = []
    for event in events:
        if not isinstance(event, dict):
            continue
        hazard = event.get("churn_probability")
        if not isinstance(hazard, (int, float)) or isinstance(hazard, bool):
            continue
        believed.append(float(hazard))
        row = buckets[round(float(hazard), 4)]
        row["decisions"] += 1
        if event.get("event_type") == "churned":
            row["churned"] += 1

    if not believed:
        return {"available": False, "reason": UNAVAILABLE_NO_EVENTS}

    decisions = sum(row["decisions"] for row in buckets.values())
    churned = sum(row["churned"] for row in buckets.values())

    table = []
    for hazard in sorted(buckets):
        row = buckets[hazard]
        realised = row["churned"] / row["decisions"] if row["decisions"] else None
        table.append({
            "believed_hazard": hazard,
            "decisions": row["decisions"],
            "churned": row["churned"],
            "realised_rate": realised,
            "believed_over_realised": (hazard / realised) if realised else None,
            "believed_tenure_years": (1.0 / hazard) if hazard else None,
        })

    portfolio_realised = churned / decisions if decisions else None
    return {
        "available": True,
        "decision_points": decisions,
        "churn_events": churned,
        "realised_per_renewal_churn_rate": portfolio_realised,
        "implied_realised_mean_tenure_years": (
            1.0 / portfolio_realised if portfolio_realised else None),
        "mean_believed_hazard": statistics.fmean(believed),
        "mean_believed_tenure_years": statistics.fmean(
            [1.0 / h for h in believed if h > 0]),
        "distinct_believed_hazards": len(buckets),
        "by_believed_hazard": table,
        "reading": (
            "`believed_over_realised` above 1 means the company thinks the "
            "customer is likelier to leave than they proved to be, which makes "
            "its believed tenure -- and therefore its CLV -- too SHORT, not too "
            "long. Compare `mean_believed_tenure_years` with "
            "`implied_realised_mean_tenure_years` for the portfolio-level "
            "direction. Buckets with small `decisions` carry a realised rate "
            "that is mostly noise; `decisions` is published so a reader can see "
            "which rows are worth reading. R12: diagnostic, never a target."
        ),
    }


def lifetime_level(run: dict, counted: list,
                   discount_rate: float | None = None) -> dict:
    """The hazard EP1 actually used on the graded accounts, from its own output.

    The point of this row is DISPERSION as much as level. A tenure horizon whose
    recovered hazard is the same value for every graded account is not carrying
    per-customer lifetime information at all -- whatever ranking that CLV has is
    coming entirely from the margin term -- and that is a different defect from
    a lifetime term that is merely too long.
    """
    snapshots = (run.get("three_horizon_clv_snapshots") or {}).get("years")
    if not isinstance(snapshots, dict) or not snapshots:
        return {"available": False, "reason": UNAVAILABLE_NO_SNAPSHOTS}
    if not counted:
        return {"available": False, "reason": UNAVAILABLE_EMPTY}
    if discount_rate is None:
        published = (run.get("three_horizon_clv_snapshots") or {}).get("discount_rate")
        discount_rate = (
            float(published)
            if isinstance(published, (int, float)) and not isinstance(published, bool)
            else DEFAULT_DISCOUNT_RATE
        )

    recovered, unrecoverable = [], []
    for record in counted:
        account_id, year = record["account"], record["belief_year"]
        entry = ((snapshots.get(year) or {}).get("accounts") or {}).get(account_id)
        if not isinstance(entry, dict):
            unrecoverable.append({"account": account_id, "reason": "no snapshot row"})
            continue
        h1 = (entry.get("contract_term") or {}).get("value_gbp")
        h2 = (entry.get("tenure_expected") or {}).get("value_gbp")
        if not isinstance(h1, (int, float)) or not isinstance(h2, (int, float)):
            unrecoverable.append({"account": account_id, "reason": "horizon blank"})
            continue
        hazard = recover_hazard(float(h1), float(h2), discount_rate)
        if hazard is None:
            unrecoverable.append({"account": account_id, "reason": "ratio not invertible"})
            continue
        recovered.append({
            "account": account_id,
            "belief_year": year,
            "hazard": hazard,
            "believed_tenure_years": 1.0 / hazard,
        })

    if not recovered:
        return {"available": False, "reason": "no hazard recoverable from the horizons",
                "unrecoverable": unrecoverable}

    hazards = [r["hazard"] for r in recovered]
    distinct = Counter(round(h, 4) for h in hazards)
    return {
        "available": True,
        "recovered_accounts": len(recovered),
        "unrecoverable_accounts": len(unrecoverable),
        "unrecoverable": unrecoverable,
        "discount_rate": discount_rate,
        "distinct_hazards": len(distinct),
        "hazard_is_constant_across_graded_population": len(distinct) == 1,
        "hazard_histogram": dict(sorted(distinct.items())),
        "median_believed_tenure_years": statistics.median(
            [r["believed_tenure_years"] for r in recovered]),
        "per_account": recovered,
        "reading": (
            "`hazard_is_constant_across_graded_population` true means the "
            "tenure horizon contributed NO per-account variation to the graded "
            "CLV -- every ranking it produced came from the margin term alone. "
            "Recovered by inverting the published `tenure_expected`/"
            "`contract_term` ratio, which depends on the hazard alone; no "
            "company-side private state is read. R12: diagnostic, never a "
            "target."
        ),
    }
