"""Decompose a folded noise-floor family's per-seed `selection_gbp` against what the shard records.

WHY THIS EXISTS. The 18-seed family at HEAD returned mean +GBP 169.60 on a seed-to-seed sd of
GBP 2,311.64 -- 0.31 standard errors from zero, no sign -- while the published figure from
2026-09-10 was -GBP 959.78 at 2.50 sems. Identical priced decisions produced residuals about
GBP 6,000 apart (`SEAT_FINDING_THE_SERVED_SELECTION_SIGN_DOES_NOT_REPRODUCE_AT_HEAD_AND_THE_
DECISION_FINGERPRINT_DOES_NOT_DETERMINE_THE_RESIDUAL_2026-09-26`). The director's hypothesis for
that, to be TESTED and not assumed, is book depth: too few accounts face enough renewals for a
pricing choice to compound, so luck dominates. This decomposes the residual against every renewal
statistic the shard actually holds, and says which readings it cannot settle.

SAY WHAT THE THING IS BEFORE DIFFERENCING IT. "Renewal count" is three distinct quantities in this
artefact and they answer differently, so they are computed and reported SEPARATELY and never
averaged into one percentage:

  * D1 -- decisions per seed. How many priced renewals the seed scored at all. Seed-level.
  * D2 -- depth per account. How many priced renewals ONE account faces across the window. A
    property of the BOOK's term calendar, which the elasticity re-draw does not move. This is the
    quantity the "too few renewals to compound" hypothesis is about.
  * D3 -- renewals SURVIVED. How many consecutive `retained: true` decisions an account strings
    together before it leaves. The only one of the three the re-draw moves freely, and the only
    one under which a choice can compound.

WHAT THIS DELIBERATELY CANNOT DO, stated here because the shape of the refusal is the result.
`selection_gbp` is a SEED-level scalar: `(value_net - control_net) - (level_net - control_net)`
folded over the whole book. The shard carries no per-account money, so no per-account contribution
to the residual can be attributed from it, and every R2 below is a correlation between two
SEED-level aggregates at n=18. That cannot separate "renewal depth drives selection" from "both
move with the same elasticity draw" -- it can only rule things OUT. `--what-is-missing` prints the
field that would have to be recorded per run to make the attribution possible, derived from what
`simulation/run_phase1e.py` already computes and throws away (`all_records` carries `customer_id`
and `net_margin_gbp`; the arms' per-account sums exist in every run and reach no artefact).

THE MULTIPLICITY IS PRICED, NOT IGNORED. Eleven seed-level regressors over 18 points will produce
an R2 near 0.25 from noise alone roughly half the time. So every R2 carries its own 90% interval
(Fisher z on the correlation, n-3 df, squared with the sign crossing handled -- an interval on r
that contains zero yields an R2 floor of exactly 0.0, never a small positive number), and a
permutation null over the MAXIMUM R2 across the whole pre-registered list is what the headline is
graded against. A per-regressor p-value here would be the R15 fail-open: a number that appears
whatever the inputs were.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

#: The producer's OWN estimator, imported rather than copied. A decomposition whose mean and sd are
#: computed by slightly different code from the family it decomposes is this project's most
#: expensive recurring shape (one rule, several implementations) with the copies one import apart.
from tools.run_value_cycle_ab import _spread

#: The eleven seed-level regressors, FIXED in
#: `docs/staging/records/SEAT_PREREG_HOW_MUCH_OF_THE_SELECTION_RESIDUAL_RENEWAL_COUNT_EXPLAINS_AND_
#: WHETHER_DEPTH_WOULD_FIX_IT_2026-09-27.md` before any of them was computed. The list is the
#: multiplicity the permutation null is taken over, so ADDING one here after reading a result
#: invalidates that null: append only with a dated note saying the null was re-run.
REGRESSOR_READING = {
    "x1_decisions": "D1",
    "x2_distinct_accounts": "D1",
    "x3_retained_decisions": "D3",
    "x4_retained_share": "D3",
    "x5_mean_decisions_per_account": "D2",
    "x6_accounts_with_5_or_more_decisions": "D2",
    "x7_accounts_with_streak_3_or_more": "D3",
    "x8_mean_longest_streak": "D3",
    "x9_total_streak_length": "D3",
    "x10_mean_believed_p_retain": "belief (control arm for X3/X4)",
    "x11_discrimination_auc": "instrument",
}

#: The concentration arm, held apart from the eleven and given its own permutation null. These are
#: the `C<n>` accounts -- the non-synthetic, hand-declared book -- and the question they answer is
#: the one that decides whether DEPTH is the lever at all: if the residual tracks a handful of
#: accounts' coin-flips, a deeper book of small households leaves the variance where it is, because
#: the per-account i.i.d. premise that makes sd/|mean| fall as 1/sqrt(k) is false.
CONCENTRATION_PREFIX = "C"


def _fail(msg: str) -> None:
    raise SystemExit(f"REFUSED: {msg}")


def load_family(path: Path) -> dict:
    """The shard, with every field this reads checked for presence rather than defaulted.

    A `.get(..., 0)` anywhere here would report a clean zero for a field the artefact never had,
    and a zero R2 from an absent regressor is indistinguishable from a real one.
    """
    if not path.exists():
        _fail(f"{path} does not exist -- nothing to decompose")
    fam = json.loads(path.read_text())
    seeds = fam.get("seeds")
    if not isinstance(seeds, list) or len(seeds) < 3:
        _fail("this artefact carries fewer than 3 seeds; a variance decomposition over it would "
              "be an interval wider than any statement it could support")
    for i, s in enumerate(seeds):
        for field in ("seed", "selection_gbp", "scored_decisions", "priced_decision_fingerprint"):
            if field not in s:
                _fail(f"seed {i} carries no {field!r}. This shard predates the field and the "
                      f"decomposition cannot be run on it -- re-fold from members that have it.")
        for d in s["scored_decisions"]:
            for field in ("account", "term_start", "retained", "believed_p_retain"):
                if field not in d:
                    _fail(f"a scored decision in seed {s['seed']} carries no {field!r}")
    return fam


def account_decisions(seed_row: dict) -> dict:
    """`{account: [(term_start, retained), ...]}` in term order, for ONE seed.

    Term order matters and sorting is not cosmetic: D3 is a run of CONSECUTIVE retained decisions,
    and a streak computed over an unsorted list measures the artefact's write order.
    """
    by_account: dict[str, list] = defaultdict(list)
    for d in seed_row["scored_decisions"]:
        by_account[d["account"]].append((d["term_start"], bool(d["retained"])))
    for rows in by_account.values():
        rows.sort(key=lambda r: r[0])
    return dict(by_account)


def longest_retained_streak(rows: list) -> int:
    """The longest run of consecutive `retained: True`. Zero when the account never retained."""
    best = run = 0
    for _term, retained in rows:
        run = run + 1 if retained else 0
        best = max(best, run)
    return best


def regressors_for_seed(seed_row: dict) -> dict:
    """The eleven, for one seed. No transformations beyond those the pre-registration names."""
    decisions = seed_row["scored_decisions"]
    by_account = account_decisions(seed_row)
    depths = [len(rows) for rows in by_account.values()]
    streaks = [longest_retained_streak(rows) for rows in by_account.values()]
    retained = sum(1 for d in decisions if d["retained"])
    auc = seed_row.get("discrimination_auc")
    return {
        "x1_decisions": float(len(decisions)),
        "x2_distinct_accounts": float(len(by_account)),
        "x3_retained_decisions": float(retained),
        "x4_retained_share": retained / len(decisions),
        "x5_mean_decisions_per_account": statistics.mean(depths),
        "x6_accounts_with_5_or_more_decisions": float(sum(1 for d in depths if d >= 5)),
        "x7_accounts_with_streak_3_or_more": float(sum(1 for s in streaks if s >= 3)),
        "x8_mean_longest_streak": statistics.mean(streaks),
        "x9_total_streak_length": float(sum(streaks)),
        "x10_mean_believed_p_retain": statistics.mean(
            float(d["believed_p_retain"]) for d in decisions),
        # None, never a filled value: an absent AUC is an absent regressor and says so downstream.
        "x11_discrimination_auc": None if auc is None else float(auc),
    }


def concentration_regressors(seeds: list) -> dict:
    """Two codings per `C<n>` account, because an account faces SEVERAL decisions.

    `retained_count` is how many of its decisions it survived in this seed; `survived_last` is
    whether its final decision in the window retained. Both are reported: picking one after
    reading the result is how a concentration story gets manufactured.
    """
    names = sorted({d["account"] for s in seeds for d in s["scored_decisions"]
                    if d["account"].startswith(CONCENTRATION_PREFIX)
                    and d["account"][1:].isdigit()})
    out: dict[str, list] = {}
    for name in names:
        counts, lasts = [], []
        for s in seeds:
            rows = account_decisions(s).get(name, [])
            counts.append(float(sum(1 for _t, r in rows if r)))
            lasts.append(float(rows[-1][1]) if rows else 0.0)
        out[f"{name}_retained_count"] = counts
        out[f"{name}_survived_last"] = lasts
    return out


def r_squared(xs: list, ys: list) -> dict:
    """Simple-regression R2 with the 90% interval eighteen points earns, and no more.

    THE STATISTICS ARE SCIPY'S, NOT A SECOND COPY OF THEM. `pearsonr(...).confidence_interval` is
    the Fisher-z interval this needs, and a hand-rolled `atanh(r) +/- 1.645/sqrt(n-3)` was the first
    draft here. It agreed with scipy to fifteen digits, which is exactly why it had to go: a
    hand-rolled estimator that happens to be right today is a second implementation of one rule,
    and this project has paid for that shape repeatedly.

    WHAT IS OURS AND NOT SCIPY'S is the zero floor. When the interval on r straddles zero the R2
    floor is reported as EXACTLY 0.0 -- squaring the nearer endpoint would invent a positive lower
    bound on explained variance for a correlation whose sign is not established, which is the
    direction that misleads a reader into thinking the effect is real.
    """
    from scipy.stats import pearsonr  # CATALOGUE: the interval is scipy's, never hand-rolled

    n = len(xs)
    if n != len(ys):
        _fail("regressor and response differ in length")
    # BEFORE scipy, because `pearsonr` on a constant input warns and returns nan -- and a nan R2
    # formats as a blank cell that reads like a small number rather than like an absent instrument.
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return {"r": None, "r2": None, "r2_low": None, "r2_high": None, "n": n,
                "unavailable_because": "the regressor is constant across every seed in this "
                                       "family, so it has no variance to explain anything with"}
    res = pearsonr(list(map(float, xs)), list(map(float, ys)))
    r = float(res.statistic)
    ci = res.confidence_interval(confidence_level=0.90)
    lo_r, hi_r = float(ci.low), float(ci.high)
    straddles = lo_r <= 0.0 <= hi_r
    r2_low = 0.0 if straddles else min(lo_r ** 2, hi_r ** 2)
    r2_high = max(lo_r ** 2, hi_r ** 2)
    return {"r": r, "r2": r * r, "r2_low": r2_low, "r2_high": r2_high, "n": n,
            "interval_straddles_zero": straddles, "unavailable_because": None}


def permutation_max_r2(columns: dict, ys: list, draws: int, rng: random.Random) -> dict:
    """The null distribution of the MAXIMUM R2 over a whole family of regressors.

    Grading a best-of-eleven against a single-regressor null is the commonest way a table like this
    publishes a finding that is not there.
    """
    live = {k: v for k, v in columns.items() if v is not None and len(set(v)) >= 2}
    if not live:
        return {"available": False, "why_not": "no regressor in this family has any variance"}
    observed = max(r_squared(v, ys)["r2"] for v in live.values())
    shuffled = list(ys)
    hits = 0
    nulls = []
    for _ in range(draws):
        rng.shuffle(shuffled)
        m = max(r_squared(v, shuffled)["r2"] for v in live.values())
        nulls.append(m)
        if m >= observed:
            hits += 1
    nulls.sort()
    return {"available": True, "regressors_in_family": len(live), "draws": draws,
            "observed_max_r2": observed, "p_value": (hits + 1) / (draws + 1),
            "null_median_max_r2": nulls[len(nulls) // 2],
            "null_95th_max_r2": nulls[int(0.95 * len(nulls))]}


def fingerprint_variance_share(seeds: list) -> dict:
    """Between-group share of variance over the priced-decision fingerprints (eta squared).

    A CONTROL on the harness, not a new claim: the 2026-09-26 finding already reported that the
    same priced decisions span about GBP 6,000 of residual. If this share comes out near 1.0 the
    rest of this table is measuring the fingerprint and nothing else, and the reader must be told
    before reading it rather than after.
    """
    groups: dict[str, list] = defaultdict(list)
    for s in seeds:
        groups[s["priced_decision_fingerprint"]].append(s["selection_gbp"])
    ys = [s["selection_gbp"] for s in seeds]
    grand = statistics.mean(ys)
    sst = sum((y - grand) ** 2 for y in ys)
    if sst == 0:
        return {"available": False, "why_not": "every seed returned the same residual"}
    ssb = sum(len(v) * (statistics.mean(v) - grand) ** 2 for v in groups.values())
    return {"available": True, "groups": len(groups),
            "group_sizes": sorted((len(v) for v in groups.values()), reverse=True),
            "between_group_share": ssb / sst,
            "within_group_share": 1.0 - ssb / sst,
            "widest_within_group_range_gbp": max(
                (max(v) - min(v)) for v in groups.values() if len(v) > 1)}


def depth_census(seeds: list) -> dict:
    """D2: how deep the book is, per account, and how stable that is across the 18 seeds.

    Reported as a census over EVERY seed rather than a representative one. A depth distribution
    read off one seed is a claim about that seed's elasticity draw dressed as a claim about the
    book.
    """
    per_seed = []
    for s in seeds:
        depths = sorted(len(rows) for rows in account_decisions(s).values())
        per_seed.append(depths)
    flat = [d for depths in per_seed for d in depths]
    hist = Counter(flat)
    n_acc = statistics.mean(len(d) for d in per_seed)
    return {
        "accounts_scored_per_seed_mean": n_acc,
        "billing_accounts_settled_in_window": seeds[0].get("billing_accounts_settled_in_window"),
        "depth_median": statistics.median(flat),
        "depth_mean": statistics.mean(flat),
        "depth_max": max(flat),
        "share_with_1_decision": hist[1] / len(flat),
        "share_with_2_or_fewer": sum(v for k, v in hist.items() if k <= 2) / len(flat),
        "share_with_5_or_more": sum(v for k, v in hist.items() if k >= 5) / len(flat),
        "histogram": {str(k): hist[k] / len(per_seed) for k in sorted(hist)},
        "depth_is_a_book_property_not_a_draw_property": {
            "min_accounts_over_seeds": min(len(d) for d in per_seed),
            "max_accounts_over_seeds": max(len(d) for d in per_seed),
            "identical_depth_vectors_across_seeds": len({tuple(d) for d in per_seed}) == 1,
        },
    }


def streak_census(seeds: list) -> dict:
    """D3: how far a choice actually compounds, which is the depth the hypothesis needs."""
    flat = []
    for s in seeds:
        flat.extend(longest_retained_streak(rows) for rows in account_decisions(s).values())
    hist = Counter(flat)
    return {"streak_median": statistics.median(flat), "streak_mean": statistics.mean(flat),
            "streak_max": max(flat),
            "share_streak_0": hist[0] / len(flat),
            "share_streak_1_or_less": sum(v for k, v in hist.items() if k <= 1) / len(flat),
            "share_streak_3_or_more": sum(v for k, v in hist.items() if k >= 3) / len(flat),
            "histogram": {str(k): hist[k] / len(seeds) for k in sorted(hist)}}


WHAT_IS_MISSING = {
    "the_question_this_shard_cannot_answer": (
        "which ACCOUNTS the residual came from, and therefore whether a deeper book would shrink "
        "it. `selection_gbp` is one scalar per seed, so depth has no variance to regress against "
        "and per-account contribution has no column at all. TRUE OF THIS SHARD AND NO LONGER TRUE "
        "OF THE INSTRUMENT: the columns below under `now_recorded` were carried on 2026-09-27, so a "
        "family re-run after that date CAN answer it -- `--account-diff` does. The sentence stays "
        "because every shard on disk before that date still cannot, and `load_for_account_diff` "
        "refuses them by name rather than letting the seed-level scalar stand in."),
    # THE FIRST TWO ARE NOW CARRIED, and they are kept here under a `now_recorded` label rather
    # than deleted. A "what is missing" list that silently drops an item cannot be told from one
    # that never asked for it, and the next reader meeting `--what-is-missing` needs to know which
    # gap closed, when, and by what -- otherwise this block rots into a request for work already
    # done, which is how a shard predating the field gets read as if the scalar could answer it.
    "now_recorded": [
        "`selection_by_account_gbp` -- carried 2026-09-27. `run_value_cycle_ab.realised_metrics` "
        "publishes `net_by_billing_account_gbp` per arm (the same settled-realised sum it folds to "
        "`total_net_gbp`, cut by BILLING ACCOUNT rather than by `customer_id`: the arm's decision "
        "log is keyed by account and `C1`/`C1g` are two fuel legs of one, so the join needs the "
        "fold), `level_vs_selection.by_account` differences them with the sum asserted against the "
        "scalar, and the floor row carries the whole column plus both arms' own columns per seed. "
        "Read it with `--account-diff`.",
        "`renewals_priced_by_account` -- carried 2026-09-27 on the same blocks, counted as DISTINCT "
        "priced term starts with declines excluded. So D2 is a per-account regressor and not the "
        "seed-level constant whose R2 of zero was a fact about the instrument.",
    ],
    "what_would_have_to_be_recorded_per_run": [
        "`consumption_mwh_by_account`: without it a concentration reading cannot tell a large "
        "account from an unlucky small one, and the two imply opposite remedies.",
    ],
    "what_would_then_be_computable": (
        "the Herfindahl of per-account selection contribution. That single number decides the "
        "director's question: near 1/N the contributions are near-i.i.d., sd/|mean| falls as "
        "1/sqrt(k) and a k-fold deeper book cuts the seeds needed by k; concentrated, and depth "
        "buys nothing because the variance is a handful of coin-flips."),
    "what_no_field_can_fix": (
        "the mean's own interval. `distance_to_a_sign.seeds_needed_interval` has a denominator "
        "spanning -GBP 375 to +GBP 714, so the required sample has no upper bound at any book "
        "depth. A deeper book can only ever make the sign CHEAPER to state, never certain to be "
        "stateable."),
}


def _largest_gap_cut(ys: list[float]) -> tuple[float, int, list[float]]:
    """`(largest consecutive gap, index of the last element BELOW it, every gap)` over a SORTED list.

    ONE IMPLEMENTATION, TWO CALLERS, and that is the point of extracting four lines.
    `residual_is_a_mixture_or_a_spread` decides whether the residual is a spread or a switch, and
    `account_state_diff` has to cut the SAME seeds into the SAME two states to attribute the switch
    it found. Two copies of this rule one function apart would let the verdict and the attribution
    describe different partitions of the same 18 seeds, with nothing able to notice -- which is this
    project's most expensive recurring shape (one rule, several implementations) at its shortest
    possible range.
    """
    if len(ys) < 2:
        raise AssertionError(
            "a gap needs two points; got {}. One seed is a run, not a partition.".format(len(ys)))
    indexed = [(ys[i + 1] - ys[i], i) for i in range(len(ys) - 1)]
    gap, cut = max(indexed)
    return gap, cut, [g for g, _ in indexed]


def residual_is_a_mixture_or_a_spread(seeds: list, key: str = "selection_gbp") -> dict:
    """Is the residual one noisy quantity, or a switch between two states? They need different bounds.

    WHY THIS LEG EXISTS AND WHY IT COMES BEFORE EVERY OTHER READING. `selection_sem_gbp`,
    `sems_from_zero` and `seeds_needed_to_state_a_sign` are all `sd / sqrt(n)` arithmetic, which
    prices the residual as ONE quantity wobbling around a mean. If instead the seeds fall into two
    tight clusters separated by a gap far larger than either cluster's own width, the sd is not a
    spread at all -- it is the distance between two states multiplied by the mixing rate, and the
    quantity actually unknown is the RATE, whose uncertainty at 18 draws is binomial and not normal.
    Pricing more seeds off the Gaussian sem in that case answers a question the data has refused.

    The test is a gap statistic and it is deliberately crude: sort the residuals, take the largest
    consecutive gap, and compare it to the widest span of the two pieces it separates. `separation`
    below 2 is a spread; well above it is a switch. A crude statistic that a reader can re-derive
    from the printed table beats a mixture likelihood nobody can check.
    """
    ys = sorted(float(s[key]) for s in seeds)
    if len(ys) < 4:
        return {"available": False, "why_not": "fewer than 4 seeds; no gap is meaningful"}
    gap, cut, gaps = _largest_gap_cut(ys)
    low, high = ys[:cut + 1], ys[cut + 1:]
    widest_piece = max(low[-1] - low[0], high[-1] - high[0])
    # A degenerate piece (one seed, zero span) would divide by zero and report infinite separation,
    # which is the flattering direction. Floored at the smallest gap the family shows instead.
    floor = max(widest_piece, min(gaps), 1e-9)
    p_hat = len(low) / len(ys)
    return {
        "available": True,
        "largest_gap_gbp": gap,
        "widest_piece_span_gbp": widest_piece,
        "separation": gap / floor,
        "verdict": ("a SWITCH between two states -- the sd is a state distance times a mixing "
                    "rate, and the Gaussian sem prices the wrong unknown"
                    if gap / floor >= MIXTURE_SEPARATION else
                    "a SPREAD -- one quantity wobbling, and sd/sqrt(n) is the right bound"),
        "state_low": {"n": len(low), "mean_gbp": statistics.mean(low),
                      "span_gbp": low[-1] - low[0]},
        "state_high": {"n": len(high), "mean_gbp": statistics.mean(high),
                       "span_gbp": high[-1] - high[0]},
        "state_distance_gbp": statistics.mean(high) - statistics.mean(low),
        "lower_state_rate": p_hat,
        "rate_90pct_interval": _clopper_pearson(len(low), len(ys), 0.10),
        # SORTED, because the mean falls as the rate rises: reporting the rate's endpoints in the
        # rate's own order prints an interval whose first number is the larger one.
        "mean_interval_from_the_rate_alone_gbp": sorted(
            lo * statistics.mean(low) + (1 - lo) * statistics.mean(high)
            for lo in _clopper_pearson(len(low), len(ys), 0.10)),
        "what_this_replaces": (
            "the Gaussian sem. With two states the family mean is `rate x low + (1-rate) x high`, "
            "so the mean's interval is the RATE's interval carried through -- and the rate's "
            "interval at this many draws is what more seeds actually buys."),
    }


def gaussian_or_mixture_bound(rows: list, key: str = "selection_gbp") -> dict:
    """May this family's error bar be `sd/sqrt(n)`, and if not, what bound replaces it?

    THE ONE DOOR EVERY PRODUCER AND SURFACE ASKS BEFORE PRINTING A STANDARD ERROR (2026-09-28).
    `residual_is_a_mixture_or_a_spread` could tell a switch from a spread, and nothing that
    published a sem asked it: the 18-seed HEAD family went on carrying `sems_from_zero` 0.31 and a
    seed price of ~717 off a separation of 9.4. A check with no caller is a finding, not a control.

    On a SWITCH the Gaussian path is refused outright -- no sem, no `sems_from_zero`, no seed price
    -- and the bound is the rate's exact interval carried through to the mean. The sign is stated
    only when that whole interval sits on one side of zero. Fewer than four readable draws cannot
    be cut into two states, so the Gaussian path stands there and `shape_checked` says it was not
    asked, rather than refusing every small family on a question it cannot pose.
    """
    readable = [r for r in rows if isinstance(r, dict) and isinstance(r.get(key), (int, float))
                and not isinstance(r.get(key), bool)]
    shape = residual_is_a_mixture_or_a_spread(readable, key)
    if not shape.get("available"):
        return {"gaussian_licensed": True, "shape_checked": False,
                "why_unchecked": shape.get("why_not"), "shape": shape}
    if shape["separation"] < MIXTURE_SEPARATION:
        return {"gaussian_licensed": True, "shape_checked": True, "shape": shape}
    lo, hi = shape["mean_interval_from_the_rate_alone_gbp"]
    sign = "positive" if lo > 0 else "negative" if hi < 0 else None
    return {
        "gaussian_licensed": False,
        "shape_checked": True,
        "shape": shape,
        "mean_interval_gbp": [lo, hi],
        "interval_confidence": 0.90,
        "sign_if_stateable": sign,
        "why_no_sem": (
            "this family is a SWITCH, not a spread: its {n} draws fall into two states "
            "\u00a3{d:,.2f} apart, each at most \u00a3{w:,.2f} wide (separation {sep:.1f}), with "
            "the lower state drawn {k} of {n} times. A standard error prices one quantity wobbling "
            "about a mean; here the unknown is the RATE at which the switch fires, so the bound is "
            "that rate's exact 90% interval ({r0:.3f} to {r1:.3f}) carried through to the mean: "
            "\u00a3{lo:,.2f} to \u00a3{hi:,.2f}, which {verdict}. No standard error and no seed "
            "count is published for it.".format(
                n=len(readable), d=shape["state_distance_gbp"], w=shape["widest_piece_span_gbp"],
                sep=shape["separation"], k=shape["state_low"]["n"],
                r0=shape["rate_90pct_interval"][0], r1=shape["rate_90pct_interval"][1],
                lo=lo, hi=hi,
                verdict=("contains zero, so no sign is stated" if sign is None else
                         "lies wholly on the {} side of zero".format(sign)))),
    }


#: THE CHECK'S OWN CUT, named once so the verdict string and the licence cannot disagree. It is the
#: gap statistic's crude bar -- a largest gap at least twice the wider piece's span -- and it is a
#: convention of this instrument, not an estimate of anything in the world.
MIXTURE_SEPARATION = 2.0


def _clopper_pearson(k: int, n: int, alpha: float) -> list:
    """Exact binomial interval on a rate, by the beta quantiles. No normal approximation.

    A Wald interval on 4/18 reaches below zero, which is not a rate; the exact interval is the only
    one that cannot publish an impossible bound.
    """
    from scipy.stats import beta  # CATALOGUE: the exact interval is scipy's
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def what_separates_the_states(seeds: list, cols: dict) -> dict:
    """Does ANY recorded field tell a seed in one state from a seed in the other?

    This is the question the R2 table cannot ask cleanly. Once the residual is known to be a switch,
    the useful test is not "how much variance does X explain" but "does X separate the two groups at
    all" -- and a field whose ranges OVERLAP between the states separates nothing, whatever its
    correlation came out at.

    A field is recorded as SEPARATING only if its two state ranges are disjoint. That is a strict
    test on purpose: at 4 versus 14 seeds a partial overlap is indistinguishable from chance, and a
    softer threshold here would manufacture an explanation for a switch that has none.
    """
    ys = [float(s["selection_gbp"]) for s in seeds]
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    gaps = [(ys[order[i + 1]] - ys[order[i]], i) for i in range(len(order) - 1)]
    _gap, cut = max(gaps)
    low_ix = set(order[:cut + 1])
    out = {}
    extra = {"level_gbp_per_mwh": [float(s["level_gbp_per_mwh"]) for s in seeds],
             "control_net_gbp": [float(s["control_net_gbp"]) for s in seeds],
             "value_arm_net_gbp": [float(s["value_arm_net_gbp"]) for s in seeds]}
    for name, vals in list(cols.items()) + list(extra.items()):
        if vals is None:
            out[name] = {"separates": None, "why_not": "the field is absent on some seed"}
            continue
        a = [v for i, v in enumerate(vals) if i in low_ix]
        b = [v for i, v in enumerate(vals) if i not in low_ix]
        disjoint = max(a) < min(b) or max(b) < min(a)
        out[name] = {"separates": disjoint,
                     "low_state_range": [min(a), max(a)], "high_state_range": [min(b), max(b)]}
    separating = sorted(k for k, v in out.items() if v.get("separates"))
    return {
        "low_state_seeds": sorted(seeds[i]["seed"] for i in low_ix),
        # NAMED RATHER THAN QUIETLY ABSENT. `level_arm_net_gbp` separates the states perfectly and
        # tells a reader nothing: `selection_gbp = value_arm_net - level_arm_net`, so it IS the
        # response up to a near-constant. Listing it as a separator would dress the definition up
        # as a cause. It is excluded here and said so, because a reader who checks which fields were
        # tested will look for it.
        "excluded_by_construction": {
            "level_arm_net_gbp": ("it is the response's own second term -- `selection_gbp = "
                                  "value_arm_net - level_arm_net` -- so separating on it is the "
                                  "identity, not an explanation"),
            "level_advantage_gbp": "the same term with `control_net` subtracted",
            "level_share_of_advantage": "a monotone function of the response over this family",
        },
        "fields_tested": len(out),
        "fields_that_separate": separating,
        "per_field": out,
        "verdict": ("NOTHING the shard records separates the two states -- the switch is driven by "
                    "something the artefact does not carry"
                    if not separating else
                    "the switch is separated by: " + ", ".join(separating)),
    }


def _no_variance_to_apportion(v_val: float, v_lev: float) -> dict:
    """The pinned-residual answer: a refusal shaped like the block it replaces, never zero shares."""
    return {"identity_reconciles": None,
            "unavailable_because": (
                "every seed returned the same `selection_gbp`, so there is no residual variance to "
                "apportion between the arms. That is itself the finding -- see the pinned-residual "
                "case of 2026-09-24 -- and not a value to report as zero shares."),
            "sd_value_arm_net_gbp": math.sqrt(v_val),
            "sd_level_arm_net_gbp": math.sqrt(v_lev),
            "sd_selection_gbp": 0.0}


def arm_variance_decomposition(seeds: list) -> dict:
    """WHERE the residual's variance actually lives, by the identity that defines the residual.

    `selection_gbp = (value_net - control_net) - (level_net - control_net) = value_net - level_net`,
    so `var(selection) = var(value_net) + var(level_net) - 2 cov` EXACTLY. The identity is asserted
    against the directly computed variance rather than assumed, because a mismatch would mean the
    shard's three net figures do not reconcile with its own residual and every share below would be
    a share of the wrong total.

    WHY THIS IS THE LEG THAT MATTERS. A paired A/B exists to make the DIFFERENCE cheap: both arms
    meet the same seed, so the seed's noise is meant to cancel and `var(difference)` to come out far
    below `var(arm)`. `cancelled_share` is the direct measurement of whether that is happening. A
    value near zero means the pairing is nominal -- the arms are drawn together and their outcomes
    are independent anyway -- and the design's whole variance-reduction claim is unearned.
    """
    ctrl = [float(s["control_net_gbp"]) for s in seeds]
    val = [float(s["value_arm_net_gbp"]) for s in seeds]
    lev = [float(s["level_arm_net_gbp"]) for s in seeds]
    sel = [float(s["selection_gbp"]) for s in seeds]
    v_val, v_lev, v_sel = (statistics.variance(x) for x in (val, lev, sel))
    # A PINNED RESIDUAL IS A STATE THIS PROJECT HAS ACTUALLY BEEN IN, not a guard for tidiness:
    # `SEAT_FINDING_THE_PINNED_SELECTION_RESIDUAL_IS_THE_CONTROL_ARM_CANCELLING_AND_THE_RE_DRAW_
    # MISSING_THE_PRICED_DECISIONS_2026-09-24` is a family whose `selection_gbp` was identical on
    # every seed. There is no variance to apportion, and every share below would be 0/0.
    if v_sel == 0:
        return _no_variance_to_apportion(v_val, v_lev)
    r_arms = r_squared(val, lev)["r"]
    # A CONSTANT ARM NET IS A REACHABLE SHAPE, not a hypothetical: a family drawn over a symbol that
    # one arm never reads returns the same net on every seed, and `r_squared` correctly answers None
    # for it. The covariance of a constant with anything is EXACTLY zero, so this is the arithmetic
    # and not a fallback -- but reaching `None * float` here crashed the whole decomposition, and
    # the crash was the first thing this module's own controls found.
    cov = 0.0 if (r_arms is None or v_val == 0 or v_lev == 0) else r_arms * math.sqrt(v_val * v_lev)
    identity = v_val + v_lev - 2 * cov
    # The reconciliation is a REFUSAL, not a warning: shares of a total that is not the total are
    # the shape this project publishes misleading figures through most often.
    if v_sel > 0 and abs(identity - v_sel) / v_sel > 1e-6:
        _fail("var(value_net) + var(level_net) - 2cov does not reproduce var(selection_gbp) "
              f"({identity:,.0f} vs {v_sel:,.0f}). The shard's arm nets do not reconcile with its "
              "own residual, so no variance share computed from them can be trusted.")
    return {
        "identity_reconciles": True,
        "sd_control_net_gbp": statistics.stdev(ctrl),
        "sd_value_arm_net_gbp": math.sqrt(v_val),
        "sd_level_arm_net_gbp": math.sqrt(v_lev),
        "sd_selection_gbp": math.sqrt(v_sel),
        "level_arm_sd_over_value_arm_sd": math.sqrt(v_lev / v_val) if v_val else None,
        "share_from_value_arm": v_val / v_sel,
        "share_from_level_arm": v_lev / v_sel,
        "share_from_covariance": -2 * cov / v_sel,
        "corr_between_arm_nets": r_arms,
        "corr_unavailable_because": (
            None if r_arms is not None else
            "one arm returned the same net on every seed, so the arms have no correlation to "
            "report and their covariance is exactly zero"),
        "cancelled_share_of_arm_variance": (
            2 * cov / (v_val + v_lev) if (v_val + v_lev) else None),
        "what_cancelled_share_means": (
            "the fraction of the two arms' combined variance that the paired design removes. A "
            "well-paired A/B on a shared seed reaches a large positive value here; near zero means "
            "the arms are independent in outcome despite sharing every draw, and the difference is "
            "as noisy as the sum."),
    }


def book_depth_price(seeds: list, sems_needed: float) -> dict:
    """What a k-fold deeper book buys, and the premise that makes the arithmetic hold.

    Seeds needed scale as `(t * sd / |mean|)^2`. Under a book scaled by k with the same mix, the
    advantage MEAN scales with k while its seed-to-seed sd scales with sqrt(k) -- IF per-account
    contributions are independent. So `sd/|mean|` falls as `1/sqrt(k)` and seeds needed fall as
    `1/k`: seeds and accounts are interchangeable and only their PRODUCT buys resolution.

    THE PREMISE IS NAMED BECAUSE IT IS NOT VERIFIED HERE. Independence of per-account contribution
    cannot be checked without per-account money, which this shard does not carry. The concentration
    arm is the only evidence available either way and it is weak evidence: it rules out the DECLARED
    accounts as the variance's home, and says nothing about the synthetic households.
    """
    sel = [float(s["selection_gbp"]) for s in seeds]
    mean, sd = statistics.mean(sel), statistics.stdev(sel)
    if abs(mean) < 1e-9:
        return {"available": False, "why_not": "the family mean is zero; the ratio has no value"}
    at_the_point_estimate = (sems_needed * sd / abs(mean)) ** 2
    # THE COUNT IS PUBLISHED ONLY WHERE THE MEAN CLEARS ITS OWN BAR. Where it does not, the mean's
    # interval contains zero and the arithmetic above has no upper bound, so a `_needed` figure
    # would tell a reader that buying that many seeds settles a question no finite number settles.
    # The arithmetic stays on the page under `_at_the_point_estimate`, a name that is not a plan.
    clears_its_bar = abs(mean) > sems_needed * sd / math.sqrt(len(sel))
    need = at_the_point_estimate if clears_its_bar else None
    settled = seeds[0].get("billing_accounts_settled_in_window")
    scored = statistics.mean(len({d["account"] for d in s["scored_decisions"]}) for s in seeds)
    ladder = [{"book_multiple": k, "settled_accounts": None if settled is None else int(settled * k),
               "seeds_needed_at_the_point_estimate": at_the_point_estimate / k}
              for k in (1, 2, 5, 10, 50, 100)]
    return {
        "available": True,
        "seeds_needed_at_this_depth": need,
        "seeds_needed_at_the_point_estimate": at_the_point_estimate,
        "seeds_needed_unavailable_because": None if clears_its_bar else (
            "the family mean does not clear {:.3f} of its own standard errors, so its interval "
            "contains zero and the seed count has no upper bound at this depth; the figure at "
            "the point estimate is beside it and is not a plan".format(sems_needed)),
        "settled_accounts_at_this_depth": settled,
        "scored_accounts_at_this_depth": scored,
        "account_draws_invariant": None if settled is None else at_the_point_estimate * settled,
        "what_the_invariant_is": (
            "seeds x settled accounts. Under the independence premise this product, not the seed "
            "count, is what a stateable sign costs -- so a deeper book and more seeds are the same "
            "purchase at different unit prices."),
        "ladder": ladder,
        "premise": "per-account contributions to the residual are independent (UNVERIFIED here)",
        "what_no_depth_can_fix": (
            "the denominator's own interval. The family mean's one-error band spans both signs, so "
            "the required sample has no upper bound at any book depth: depth makes a sign CHEAPER "
            "to state, never certain to be stateable."),
    }


def decompose(fam: dict, draws: int, rng: random.Random) -> dict:
    seeds = fam["seeds"]
    ys = [float(s["selection_gbp"]) for s in seeds]
    cols = {name: [] for name in REGRESSOR_READING}
    for s in seeds:
        row = regressors_for_seed(s)
        for name in cols:
            cols[name].append(row[name])
    cols = {k: (None if any(v is None for v in vals) else vals) for k, vals in cols.items()}
    conc = concentration_regressors(seeds)
    fits = {k: (r_squared(v, ys) if v is not None else
                {"r2": None, "unavailable_because": "a seed carries no value for this regressor"})
            for k, v in cols.items()}
    conc_fits = {k: r_squared(v, ys) for k, v in conc.items()}
    return {
        "shard": fam.get("generated_at"),
        "producing_commit": (fam.get("producing_commit") or {}).get("commit"),
        "world_digest": (fam.get("world_identity") or {}).get("digest"),
        "clock": fam.get("clock"),
        "response": "selection_gbp",
        "response_spread": _spread(ys),
        "readings": REGRESSOR_READING,
        "renewal_count_fits": fits,
        "renewal_count_permutation_null": permutation_max_r2(cols, ys, draws, rng),
        "concentration_fits": conc_fits,
        "concentration_permutation_null": permutation_max_r2(
            {k: v for k, v in conc.items()}, ys, draws, rng),
        "fingerprint_variance": fingerprint_variance_share(seeds),
        "residual_shape": residual_is_a_mixture_or_a_spread(seeds),
        "state_separation": what_separates_the_states(seeds, cols),
        "arm_variance": arm_variance_decomposition(seeds),
        "book_depth_price": book_depth_price(
            seeds, float(fam.get("selection_sems_needed_to_state_a_sign") or 1.96)),
        "depth_census_d2": depth_census(seeds),
        "streak_census_d3": streak_census(seeds),
        "what_is_missing": WHAT_IS_MISSING,
    }


def _fmt(v, width=10, places=4):
    if v is None:
        return "—".rjust(width)
    return f"{v:.{places}f}".rjust(width)


def _render_fit_table(title: str, fits: dict, readings: dict, limit: int | None = None) -> list:
    """One R2 table. Shared by the renewal-count eleven and the concentration arm.

    Sorted by R2 DESCENDING with unavailable rows last, so the eye lands on the biggest claim first
    and an unavailable row cannot be mistaken for the smallest one.
    """
    lines = [title,
             f"{'regressor':<40}{'read':<6}{'r':>9}{'R2':>9}{'R2 low':>9}{'R2 high':>9}"]
    rows = sorted(fits.items(), key=lambda kv: -(kv[1].get("r2") or -1))
    for name, fit in (rows[:limit] if limit else rows):
        read = readings.get(name, "")
        if fit.get("r2") is None:
            lines.append(f"{name:<40}{read:<6}{'—':>9}{'—':>9}{'—':>9}{'—':>9}"
                         f"  {fit['unavailable_because']}")
            continue
        lines.append(f"{name:<40}{read:<6}{_fmt(fit['r'], 9)}{_fmt(fit['r2'], 9)}"
                     f"{_fmt(fit['r2_low'], 9)}{_fmt(fit['r2_high'], 9)}")
    return lines


def _render_null(null: dict) -> list:
    """The permutation line. Printed with the null's MEDIAN, not only the p-value.

    A reader who sees `p=0.82` learns the best regressor is not significant; a reader who also sees
    the null's median best-of-eleven learns the observed best is BELOW chance, which is the stronger
    and more useful statement.
    """
    if not null.get("available"):
        return [f"  permutation null unavailable: {null['why_not']}"]
    return [f"  permutation null over {null['regressors_in_family']} regressors, "
            f"{null['draws']} draws: observed max R2 {null['observed_max_r2']:.4f}, "
            f"p={null['p_value']:.4f}, null median {null['null_median_max_r2']:.4f}, "
            f"null 95th {null['null_95th_max_r2']:.4f}"]


def _render_shape(rs: dict, ss: dict) -> list:
    """The spread-or-switch verdict, and what separates the states. Printed BEFORE any sem."""
    if not rs.get("available"):
        return []
    lo, hi = rs["rate_90pct_interval"]
    mlo, mhi = rs["mean_interval_from_the_rate_alone_gbp"]
    return [
        "",
        "IS IT A SPREAD OR A SWITCH? (read this before any sem below)",
        f"  largest gap £{rs['largest_gap_gbp']:,.2f} vs widest piece span "
        f"£{rs['widest_piece_span_gbp']:,.2f} -> separation {rs['separation']:.1f}x",
        f"  VERDICT: {rs['verdict']}",
        f"  low state  n={rs['state_low']['n']:>2} mean £{rs['state_low']['mean_gbp']:,.2f} "
        f"span £{rs['state_low']['span_gbp']:,.2f}",
        f"  high state n={rs['state_high']['n']:>2} mean £{rs['state_high']['mean_gbp']:,.2f} "
        f"span £{rs['state_high']['span_gbp']:,.2f}",
        f"  state distance £{rs['state_distance_gbp']:,.2f}; lower-state rate "
        f"{rs['lower_state_rate']:.3f} (exact 90% {lo:.3f}..{hi:.3f})",
        f"  family mean from the rate alone: £{mlo:,.2f} .. £{mhi:,.2f}",
        f"  low-state seeds: {ss['low_state_seeds']}",
        f"  of {ss['fields_tested']} recorded fields tested for disjoint ranges between the "
        f"states, {len(ss['fields_that_separate'])} separate them",
        f"  {ss['verdict']}",
    ]


def _render_arms(av: dict) -> list:
    """Where the variance lives. The identity is printed in the heading so a reader can check it."""
    if av.get("identity_reconciles") is None:
        return ["", f"WHERE THE VARIANCE LIVES: {av['unavailable_because']}"]
    return [
        "",
        "WHERE THE VARIANCE ACTUALLY LIVES (exact identity, var(sel)=var(val)+var(lev)-2cov)",
        f"  sd control_net £{av['sd_control_net_gbp']:,.2f} · "
        f"sd VALUE arm net £{av['sd_value_arm_net_gbp']:,.2f} · "
        f"sd LEVEL arm net £{av['sd_level_arm_net_gbp']:,.2f} "
        f"({av['level_arm_sd_over_value_arm_sd']:.1f}x the value arm)",
        f"  share of var(selection): value arm {av['share_from_value_arm']:.4%}, "
        f"level arm {av['share_from_level_arm']:.4%}, "
        f"covariance {av['share_from_covariance']:+.4%}",
        f"  corr between arm nets {av['corr_between_arm_nets']:+.4f} -> the paired design "
        f"cancels {av['cancelled_share_of_arm_variance']:.2%} of the arms' variance",
    ]


def _render_depth(bd: dict, d2: dict, d3: dict) -> list:
    """The depth ladder and the two censuses -- the book's own shape, alongside its price."""
    lines = []
    if bd.get("available"):
        lines += ["", f"PRICE OF A SIGN BY BOOK DEPTH (premise: {bd['premise']})",
                  f"  invariant: {bd['account_draws_invariant']:,.0f} seed-account draws "
                  f"({bd['what_the_invariant_is'].split('.')[0]})"]
        for row in bd["ladder"]:
            lines.append(f"    book x{row['book_multiple']:>3} -> "
                         f"{row['settled_accounts']:>7,} settled accounts, "
                         f"{row['seeds_needed_at_the_point_estimate']:>8.1f} seeds needed")
    lines += [
        "",
        f"D2 DEPTH CENSUS: {d2['accounts_scored_per_seed_mean']:.1f} accounts scored per seed out "
        f"of {d2['billing_accounts_settled_in_window']} settled",
        f"  median depth {d2['depth_median']:.1f}, mean {d2['depth_mean']:.2f}, "
        f"max {d2['depth_max']}; 1 decision {d2['share_with_1_decision']:.1%}, "
        f"<=2 {d2['share_with_2_or_fewer']:.1%}, >=5 {d2['share_with_5_or_more']:.1%}",
        f"  depth vector identical across all seeds: "
        f"{d2['depth_is_a_book_property_not_a_draw_property']['identical_depth_vectors_across_seeds']}",
        f"D3 STREAK CENSUS: median {d3['streak_median']:.1f}, mean {d3['streak_mean']:.2f}, "
        f"max {d3['streak_max']}; never retained {d3['share_streak_0']:.1%}, "
        f"<=1 {d3['share_streak_1_or_less']:.1%}, >=3 {d3['share_streak_3_or_more']:.1%}",
    ]
    return lines


def render(out: dict) -> str:
    """The whole table, at real inputs. Order is deliberate: the SHAPE verdict precedes every sem."""
    sp = out["response_spread"]
    lines = [
        f"SELECTION RESIDUAL DECOMPOSITION — {out['shard']} @ {out['producing_commit'][:9]}",
        f"world {out['world_digest']} · clock {out['clock']} · n={sp['n']} seeds",
        f"selection_gbp: mean £{sp['mean']:,.2f}  sd £{sp['stdev']:,.2f}  "
        f"min £{sp['min']:,.2f}  max £{sp['max']:,.2f}",
        "",
    ]
    lines += _render_fit_table("RENEWAL-COUNT REGRESSORS (the pre-registered eleven)",
                              out["renewal_count_fits"], out["readings"])
    lines += _render_null(out["renewal_count_permutation_null"])
    lines.append("")
    lines += _render_fit_table("CONCENTRATION ARM (the declared C-accounts, held apart)",
                               out["concentration_fits"], {}, limit=12)
    lines += _render_null(out["concentration_permutation_null"])
    fv = out["fingerprint_variance"]
    if fv.get("available"):
        lines += ["", f"FINGERPRINT (control): {fv['groups']} groups {fv['group_sizes']}, "
                      f"between-group share {fv['between_group_share']:.4f}, "
                      f"widest within-group range £{fv['widest_within_group_range_gbp']:,.2f}"]
    lines += _render_shape(out["residual_shape"], out["state_separation"])
    lines += _render_arms(out["arm_variance"])
    lines += _render_depth(out["book_depth_price"], out["depth_census_d2"], out["streak_census_d3"])
    return "\n".join(lines)


#: The three per-account columns `account_state_diff` needs, all added to the floor row on
#: 2026-09-27. Named as a constant because the loader refuses on them and the refusal has to name
#: WHICH field and WHICH seed -- a shard folded from members either side of that date will carry
#: some and not others, and "the decomposition returned nothing" would be indistinguishable from
#: "no account moved".
ACCOUNT_DIFF_REQUIRED = ("selection_by_account_gbp", "value_arm_net_by_account_gbp",
                         "level_arm_net_by_account_gbp")

#: How many accounts the state-diff table names individually. A print bound and nothing else --
#: every count, share and Herfindahl below is taken over the whole column.
_STATE_DIFF_ROWS_SHOWN = 15


def load_for_account_diff(path: Path) -> dict:
    """A shard the per-account state diff can be taken over, or a refusal naming the missing field.

    A SEPARATE LOADER FROM `load_family`, AND DELIBERATELY A LOOSER ONE ON n. `load_family` refuses
    under three seeds because a variance decomposition over two points is an interval wider than
    anything it could say. This reading is not a variance decomposition: the designed experiment is
    a TWO-SEED diff, one draw from each state on a world where the value arm's net is identical, and
    two points is exactly the right number for it. What it cannot tolerate is a MISSING COLUMN, so
    that is what it refuses on, per seed and per field.
    """
    if not path.exists():
        _fail(f"{path} does not exist -- nothing to diff")
    fam = json.loads(path.read_text())
    seeds = fam.get("seeds")
    if not isinstance(seeds, list) or len(seeds) < 2:
        _fail("this artefact carries fewer than 2 seeds; there are no two states to diff")
    for row in seeds:
        if "selection_gbp" not in row:
            _fail(f"seed {row.get('seed')!r} carries no `selection_gbp`")
        for field in ACCOUNT_DIFF_REQUIRED:
            if not isinstance(row.get(field), dict):
                _fail(
                    "seed {!r} carries no `{}` ({}). This shard predates the per-account column "
                    "added 2026-09-27 and the residual cannot be attributed to accounts from it -- "
                    "re-run the seeds rather than reading the seed-level scalar as if it could "
                    "answer this.".format(row.get("seed"), field,
                                          row.get(field + "_unavailable_because") or "absent"))
    return fam


def _state_means(rows: list, field: str) -> tuple[dict, dict]:
    """Mean per-account value over a set of seeds, and how many seeds each account was ABSENT from.

    ABSENCE IS COUNTED, NOT JUST DEFAULTED. An account missing from a seed's column settled nothing
    in that arm on that draw, which is a real zero for the mean -- but it is also the roster event
    that the two-state switch is most likely to BE, so a mean that silently absorbed it would hide
    the very mechanism. The absence count travels with the mean.
    """
    accounts: set = set()
    for row in rows:
        accounts |= set(row[field])
    means, absences = {}, {}
    for account in accounts:
        values = [float(row[field].get(account, 0.0)) for row in rows]
        means[account] = sum(values) / len(rows)
        absences[account] = sum(1 for row in rows if account not in row[field])
    return means, absences


def account_state_diff(fam: dict) -> dict:
    """WHICH ACCOUNTS the two-state selection switch lives in, and WHICH ARM moved inside them.

    THE QUESTION, AND WHY NOTHING ON DISK COULD ANSWER IT BEFORE.
    `SEAT_RESULT_RENEWAL_COUNT_EXPLAINS_NONE_OF_THE_SELECTION_RESIDUAL_AND_THE_VARIANCE_IS_ONE_
    DISCRETE_EVENT_IN_THE_LEVEL_ARM_2026-09-27` (commit `d678f063a`) established three things about
    the 18-seed family at HEAD: renewal count explains none of the residual's variance (best of
    eleven pre-registered regressors R2 0.0284 against a permutation null median of 0.0971,
    p 0.8245); 99.84% of the variance is the LEVEL arm's own net; and the residual is not a spread
    but a two-state SWITCH, GBP 5,387.65 apart, firing in 4 of 18 draws. It also established that
    **none of the 14 fields the shard recorded separates the two states**. The switch was driven by
    something no artefact carried, and `selection_gbp` was a per-seed scalar with no per-account
    column anywhere.

    WHAT THIS DOES. Cuts the seeds into the same two states `residual_is_a_mixture_or_a_spread`
    cuts them into -- the SAME helper, not a second copy of the rule -- and differences the two
    states' mean per-account columns. Then, because the residual is `value_net - level_net` per
    account, it splits each account's state move into the part that came from the value arm and the
    part that came from the level arm, and reconciles the two against the state distance. That
    reconciliation is what makes the attribution a decomposition rather than two tables.

    IT REPORTS CONCENTRATION OF THE STATE DIFF, NOT OF THE RESIDUAL, and the two are different
    questions. `run_value_cycle_ab.selection_by_account` publishes the concentration of ONE seed's
    residual; that says whether the residual's LEVEL is carried by a few accounts. This says
    whether the residual's MOVEMENT BETWEEN STATES is -- which is the one that decides whether the
    1/k book-depth ladder's independence premise holds, because the ladder is about variance.
    """
    seeds = sorted(fam["seeds"], key=lambda r: float(r["selection_gbp"]))
    ys = [float(r["selection_gbp"]) for r in seeds]
    gap, cut, _ = _largest_gap_cut(ys)
    low_rows, high_rows = seeds[:cut + 1], seeds[cut + 1:]

    per_state = {}
    for label, rows in (("low", low_rows), ("high", high_rows)):
        per_state[label] = {
            field: _state_means(rows, field) for field in ACCOUNT_DIFF_REQUIRED}

    def mean_of(rows, key):
        return sum(float(r[key]) for r in rows) / len(rows)

    state_distance = mean_of(low_rows, "selection_gbp") - mean_of(high_rows, "selection_gbp")
    value_move = (mean_of(low_rows, "value_arm_net_gbp")
                  - mean_of(high_rows, "value_arm_net_gbp"))
    level_move = (mean_of(low_rows, "level_arm_net_gbp")
                  - mean_of(high_rows, "level_arm_net_gbp"))
    # THE IDENTITY, ASSERTED AND NOT ASSUMED. `selection = value - level`, so the state distance
    # must be the value arm's move minus the level arm's. A gap here means the two states were cut
    # differently for the scalar and the columns, which is the one defect this whole block would
    # otherwise publish as an attribution.
    if abs(state_distance - (value_move - level_move)) > 0.01:
        raise AssertionError(
            "the state distance is GBP {:,.2f} but `value_move - level_move` is GBP {:,.2f}. The "
            "scalar and the arms disagree about what moved between the states, so no per-account "
            "attribution taken over them can be trusted.".format(
                state_distance, value_move - level_move))

    sel_low, absent_low = per_state["low"]["selection_by_account_gbp"]
    sel_high, absent_high = per_state["high"]["selection_by_account_gbp"]
    val_low, _ = per_state["low"]["value_arm_net_by_account_gbp"]
    val_high, _ = per_state["high"]["value_arm_net_by_account_gbp"]
    lev_low, lev_absent_low = per_state["low"]["level_arm_net_by_account_gbp"]
    lev_high, lev_absent_high = per_state["high"]["level_arm_net_by_account_gbp"]

    accounts = sorted(set(sel_low) | set(sel_high))
    diff = {a: sel_low.get(a, 0.0) - sel_high.get(a, 0.0) for a in accounts}
    gross = sum(abs(d) for d in diff.values())
    if abs(sum(diff.values()) - state_distance) > 0.01:
        raise AssertionError(
            "the per-account state diff sums to GBP {:,.2f} against a state distance of "
            "GBP {:,.2f}".format(sum(diff.values()), state_distance))

    ranked = sorted(accounts, key=lambda a: -abs(diff[a]))
    cumulative, n90 = 0.0, 0
    for account in ranked:
        if gross <= 0 or cumulative >= 0.9 * gross:
            break
        cumulative += abs(diff[account])
        n90 += 1
    herfindahl = sum((abs(d) / gross) ** 2 for d in diff.values()) if gross > 0 else None

    def row_of(account):
        v_move = val_low.get(account, 0.0) - val_high.get(account, 0.0)
        l_move = lev_low.get(account, 0.0) - lev_high.get(account, 0.0)
        return {
            "account": account,
            "selection_state_diff_gbp": diff[account],
            "share_of_gross": (abs(diff[account]) / gross if gross > 0 else None),
            "value_arm_move_gbp": v_move,
            "level_arm_move_gbp": l_move,
            # WHICH ARM MOVED, as the two numbers and not as a verdict. A label would need a
            # threshold nothing establishes; the reader can compare GBP 5,351 against GBP 0.
            "moved_mostly_by": ("the level arm" if abs(l_move) > abs(v_move)
                                else ("the value arm" if abs(v_move) > abs(l_move)
                                      else "neither more than the other")),
            # THE ROSTER FACT, which is the mechanism the level arm's own net is most likely to
            # move by: an account that settles in the level arm on one state's draws and not the
            # other's has left at a different time, and that is one coin flip, not a repricing.
            # DEFAULTED TO "ABSENT FROM EVERY SEED IN THAT STATE", not to None. `_state_means`
            # only has keys for accounts that appeared at least once, so an account missing from a
            # whole state is missing from its absence map too -- and a `None` there would read as
            # "not measured" for the one case this field exists to report. The default is the
            # state's own seed count, which is what absent-from-all-of-them means.
            "seeds_absent_from_the_level_arm_low_state": lev_absent_low.get(
                account, len(low_rows)),
            "seeds_absent_from_the_level_arm_high_state": lev_absent_high.get(
                account, len(high_rows)),
            "seeds_absent_from_the_column_low_state": absent_low.get(account, len(low_rows)),
            "seeds_absent_from_the_column_high_state": absent_high.get(account, len(high_rows)),
        }

    return {
        "states": {
            "low": {"seeds": [r["seed"] for r in low_rows],
                    "mean_selection_gbp": mean_of(low_rows, "selection_gbp"),
                    "mean_level_arm_net_gbp": mean_of(low_rows, "level_arm_net_gbp"),
                    "mean_value_arm_net_gbp": mean_of(low_rows, "value_arm_net_gbp")},
            "high": {"seeds": [r["seed"] for r in high_rows],
                     "mean_selection_gbp": mean_of(high_rows, "selection_gbp"),
                     "mean_level_arm_net_gbp": mean_of(high_rows, "level_arm_net_gbp"),
                     "mean_value_arm_net_gbp": mean_of(high_rows, "value_arm_net_gbp")},
            "gap_between_the_states_gbp": gap,
        },
        "state_distance_gbp": state_distance,
        "of_which_the_value_arm_moved_gbp": value_move,
        "of_which_the_level_arm_moved_gbp": level_move,
        "accounts_in_the_union": len(accounts),
        "gross_absolute_state_movement_gbp": gross,
        "herfindahl_of_absolute_state_movement": herfindahl,
        "effective_accounts": (1.0 / herfindahl) if herfindahl else None,
        "accounts_holding_90pc_of_the_state_movement": n90,
        "largest_single_account": (ranked[0] if ranked else None),
        "largest_single_state_move_gbp": (diff[ranked[0]] if ranked else None),
        "movers": [row_of(a) for a in ranked[:_STATE_DIFF_ROWS_SHOWN]],
        "movers_shown": min(len(ranked), _STATE_DIFF_ROWS_SHOWN),
        "how_to_read_this": (
            "`state_distance_gbp` is the mean residual in the low state minus the mean in the high "
            "state, and it is asserted equal to `of_which_the_value_arm_moved_gbp` minus "
            "`of_which_the_level_arm_moved_gbp`. `effective_accounts` against "
            "`accounts_in_the_union` is the independence reading the 1/k book-depth ladder rests "
            "on: near the union the per-account contributions are near-i.i.d. and a k-fold deeper "
            "book cuts the seeds needed by k; a handful, and depth buys almost nothing because the "
            "variance is a few coin flips."),
    }


def render_account_diff(out: dict) -> str:
    """The table, printed before any of it is believed -- this file's own rule, one mode along."""
    low, high = out["states"]["low"], out["states"]["high"]
    lines = [
        "=== which accounts the two-state selection switch lives in ===",
        "",
        "low  state: seeds {}  mean selection GBP {:+,.2f}  level arm GBP {:,.2f}  "
        "value arm GBP {:,.2f}".format(low["seeds"], low["mean_selection_gbp"],
                                       low["mean_level_arm_net_gbp"],
                                       low["mean_value_arm_net_gbp"]),
        "high state: seeds {}  mean selection GBP {:+,.2f}  level arm GBP {:,.2f}  "
        "value arm GBP {:,.2f}".format(high["seeds"], high["mean_selection_gbp"],
                                       high["mean_level_arm_net_gbp"],
                                       high["mean_value_arm_net_gbp"]),
        "",
        "state distance        GBP {:+,.2f}".format(out["state_distance_gbp"]),
        "  of which value arm GBP {:+,.2f}".format(out["of_which_the_value_arm_moved_gbp"]),
        "  of which level arm GBP {:+,.2f}".format(out["of_which_the_level_arm_moved_gbp"]),
        "",
        "accounts in the union                {}".format(out["accounts_in_the_union"]),
        "gross absolute state movement        GBP {:,.2f}".format(
            out["gross_absolute_state_movement_gbp"]),
        "Herfindahl of the state movement     {}".format(
            "n/a" if out["herfindahl_of_absolute_state_movement"] is None
            else "{:.4f}".format(out["herfindahl_of_absolute_state_movement"])),
        "effective accounts                   {}".format(
            "n/a" if out["effective_accounts"] is None
            else "{:.2f}".format(out["effective_accounts"])),
        "accounts holding 90% of the movement {}".format(
            out["accounts_holding_90pc_of_the_state_movement"]),
        "",
        "{:<22}{:>14}{:>14}{:>14}  {}".format(
            "account", "state diff", "value arm", "level arm", "moved mostly by"),
    ]
    for row in out["movers"]:
        lines.append("{:<22}{:>14,.2f}{:>14,.2f}{:>14,.2f}  {}".format(
            row["account"], row["selection_state_diff_gbp"], row["value_arm_move_gbp"],
            row["level_arm_move_gbp"], row["moved_mostly_by"]))
    lines += ["", "showing {} of {} accounts".format(out["movers_shown"],
                                                     out["accounts_in_the_union"]),
              "", out["how_to_read_this"]]
    return "\n".join(lines)


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("shard", type=Path, nargs="?",
                    help="a folded noise-floor family JSON")
    ap.add_argument("--permutations", type=int, default=20000)
    ap.add_argument("--rng-seed", type=int, default=20260927)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--what-is-missing", action="store_true",
                    help="print only the fields that would have to be recorded per run")
    ap.add_argument(
        "--account-diff", action="store_true",
        help=("ACCOUNT-DIFF mode: cut the shard's seeds into the two states at their largest "
              "`selection_gbp` gap and difference the two states' per-account columns, naming "
              "which accounts the switch lives in and which ARM moved inside them. Needs the "
              "three per-account columns added to the floor row on 2026-09-27, refuses per seed "
              "and per field without them, and accepts TWO seeds -- the designed contrast is one "
              "draw from each state, not a variance decomposition."))
    args = ap.parse_args(argv)
    if args.what_is_missing:
        print(json.dumps(WHAT_IS_MISSING, indent=2))
        return 0
    if args.shard is None:
        _fail("no shard given. Pass a folded family JSON, or --what-is-missing to read the "
              "fields this decomposition needs and the artefact does not carry.")
    if args.account_diff:
        out = account_state_diff(load_for_account_diff(args.shard))
        print(render_account_diff(out))
        if args.json:
            args.json.write_text(json.dumps(out, indent=1))
            print(f"\nwrote {args.json}")
        return 0
    fam = load_family(args.shard)
    out = decompose(fam, args.permutations, random.Random(args.rng_seed))
    print(render(out))
    if args.json:
        args.json.write_text(json.dumps(out, indent=1))
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
