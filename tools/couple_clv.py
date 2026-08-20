"""COUPLED-TRIAD runner for EP1's customer-value pair: what the company BELIEVED
a customer was worth, against what that customer TURNED OUT to be worth.

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the only
layer permitted to hold the company's forward-looking CLV belief and the world's
realised outcome side by side to compute the gap (COUPLED_TRIAD_DESIGN 1.3; same
role as `background/gap_metric.py` and the other `tools/couple_*.py` runners). It
lives in `tools/` -- NOT under `company/` or `saas/` -- so it is not scanned by the
epistemic verifier and may legitimately read both sides.

`EP1_clv_three_horizon`'s own record has carried "the gap is measured and still not
instrumented" as an open debt for FIVE consecutive passes, described there as
"consumed, not absorbed" (R17). This module is the absorption. What follows is why
it took five passes, which is a finding in its own right rather than an excuse.

=============================================================================
WHY THE OBVIOUS MEASUREMENT HAS AN EMPTY POPULATION
=============================================================================

The natural reading of "measure EP1's estimate against realised value" is: take the
CLV the company publishes for each account today, and compare it with what that
account actually earned. On the live book that comparison has n = 0, and not by
accident -- the two populations are disjoint BY CONSTRUCTION:

  * An account whose realised value is COMPLETE is one that has left. EP1 (and the
    `enterprise_value` roll-up it sits beside) deliberately refuses to value ceased
    accounts -- that refusal IS the `66141b70c` repair, and `still_supplied` is a
    required, defaultless keyword precisely so it cannot be skipped.
  * An account EP1 does value is one that is still supplied, and its realised value
    is therefore RIGHT-CENSORED: the run ends before the customer does.

Measured on `docs/reports/run_output_latest.json`: 5 ceased accounts, all with
`clv_gbp = None`; 8 valued accounts, all `still_supplied`. The intersection is
empty. Comparing a forward-looking estimate against a truncated realised total
would not be a hard measurement, it would be a wrong one -- the censored accounts'
"realised" value is simply the part of it the run happened to see.

=============================================================================
THE MEASUREMENT THAT IS AVAILABLE: A POINT-IN-TIME BACKTEST
=============================================================================

The run publishes `clv_snapshots` -- the company's own CLV estimate per account at
each year end -- and ceased accounts appear in it for every year they were still
supplied. That is a genuine point-in-time belief, recorded before the outcome was
known, and it is what makes the pair measurable at all:

  1. WORLD adds depth  -- the customer lives, consumes, is billed, and eventually
                          leaves. `per_customer_lifetime[...]
                          ['net_margin_after_cost_to_serve_gbp']` is what the
                          relationship actually earned, accumulated from settled
                          records. The company does not get to choose it.
  2. COMPANY copes     -- at each year end the company forms a forward CLV from its
                          own observables (its churn estimate off its own bill-shock
                          history, its own cost-to-serve arithmetic). It is allowed
                          to be wrong.
  3. HARNESS measures  -- for accounts whose lifetime COMPLETED inside the run, the
                          error between the earliest recorded belief and the
                          realised outcome, normalised to a no-skill predictor.

POPULATION, STATED NOT ASSUMED (EP1's own pass-6 constraint, applied to the
harness that grades it). Counted = ceased accounts carrying both a snapshot belief
and a realised total. Excluded = every still-supplied account, under the named
reason `right_censored_lifetime`, because the world has not finished telling us what
they were worth. The entry carries both counts, so a reader sees the denominator
USED and the one AVAILABLE.

=============================================================================
THE TRUTH WINDOW IS WIDER THAN THE BELIEF WINDOW -- DECLARED, WITH ITS SIGN
=============================================================================

This is the honest simplification (R10) in the measurement, and it is stated here
rather than discovered later. The belief is taken at the account's EARLIEST
snapshot, which lands at the end of its first (partial) year. The realised total is
the WHOLE lifetime, including the months before that snapshot. So truth is measured
over a slightly LONGER window than the belief is a forecast for.

The run publishes no per-account-per-year margin, so the pre-snapshot slice cannot
be subtracted; `years` and `management_accounts` are portfolio- and segment-level
only. The direction of the resulting bias is knowable even though its size is not:
for an account earning positive margin before its first snapshot, truth is
OVERSTATED relative to the window the belief covers, which makes an over-estimating
belief look BETTER than it is. The headline gap is therefore CONSERVATIVE for the
over-estimation cases, and this is recorded on the ledger entry rather than left in
a comment.

The sign-agreement component inherits the same caveat unevenly, and the module
reports which accounts survive it (`sign_errors_robust`): where the realised total
is NEGATIVE and the belief POSITIVE, removing positive pre-snapshot earnings can
only make the realised figure more negative, so the disagreement stands whatever the
missing slice contains. Where the realised total is positive and the belief
negative, it does not stand on this evidence alone, and the module says so instead
of counting it.

=============================================================================
R15 INDEPENDENCE, AND R12
=============================================================================

The two sides are not two readings of one number. The belief is the output of the
company's forward CLV model (a churn hazard times a discounted margin annuity); the
truth is an accumulation of SETTLED records over the customer's actual life. Neither
is derived from the other, which is what stops this being the TAUTOLOGY pattern.
The roster is cross-checked against `churned_billing_accounts`, a second and
independently-written field, and a disagreement is reported rather than resolved
silently.

R12 APPLIES HARD. This gap is a DIAGNOSTIC and never a target. Nothing may be tuned
to move it -- not the churn model, not the discount rate, not the cost-to-serve
split. A gap above 1.0 means the company's per-customer estimate carries less
information than guessing the portfolio mean; the correct response is R4 (diagnose
the mechanism), never fitting the estimator to this number.

DETERMINISM (C-S2). No RNG, no wall clock, no git call inside the measurement.
`measured_at` and `run_git_commit` are gathered by `main()` and passed in, because
`gap_metric` never calls a clock.
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from background.gap_metric import (NORMALISATION_DIVISOR, DIVISOR_RAW_GAP_IS,
                                   GapResult, write_gap_entry)

#: The ledger key. EP1 is a COMPANY atom, and the pair it stands in is
#: company-belief vs world-outcome rather than one map world atom -- the ledger
#: already carries a key outside the `W*` family (the recontracting pair, whose
#: id is deliberately NOT spelled here: see below) and the Proof door renders an
#: uncoupled entry through its own defensive branch.
#:
#: THE PRECEDENT IS CITED WITHOUT ITS ID, AND THAT IS NOT SUPERSTITION.
#: `gap_ledger_reconciler.producers_for` attributes a ledger row to every WRITER
#: whose TEXT CONTAINS the row's atom id -- a substring match over the whole
#: file, comments included. Measured 2026-08-19 before this rewording: this
#: module appeared in the recontracting row's producer set on the strength of
#: that one comment alone, so every future commit to THIS file would have marked
#: THAT row stale. The module already holds the right doctrine one layer up --
#: `_WRITE_MARKER`'s own comment says "a WRITE, not a mention ... attributing a
#: row to its reader would make staleness meaningless" -- but it is applied when
#: choosing WHICH FILES are writers, never when choosing WHICH ROW a writer
#: produced. Rewording this comment fixes the instance and NOT the class; the
#: class is filed as
#: WORKER_FINDING_A_GAP_ROW_IS_ATTRIBUTED_TO_ANY_WRITER_THAT_MERELY_NAMES_IT_2026-08-19.
LEDGER_KEY = "EP1_clv_three_horizon"
TWIN_ATOM_ID = "EP1_clv_three_horizon"

DEFAULT_RUN_OUTPUT = Path("docs/reports/run_output_latest.json")

#: Why an account is not in the counted population. Named, never a bare drop.
EXCLUSION_CENSORED = "right_censored_lifetime"
EXCLUSION_NO_SNAPSHOT = "no_point_in_time_belief_recorded"
EXCLUSION_NO_REALISED = "no_realised_lifetime_margin"


def load_run_output(path=None) -> dict:
    """The published run artefact. Missing/unreadable raises -- an unavailable
    input is a FAILED measurement, never an empty one that reads as clean (R15
    fail-silent)."""
    p = Path(path) if path is not None else DEFAULT_RUN_OUTPUT
    return json.loads(p.read_text(encoding="utf-8"))


def _earliest_belief(clv_snapshots: dict, account: str):
    """The company's earliest recorded point-in-time CLV for this account.

    Returns `(year, value)` or `(None, None)`. Years are sorted as STRINGS, which
    is safe for the 4-digit keys the run writes and is checked by the caller's
    population accounting rather than assumed here.
    """
    years = sorted(y for y, snap in clv_snapshots.items()
                   if isinstance(snap, dict) and account in snap
                   and isinstance(snap.get(account), (int, float))
                   and not isinstance(snap.get(account), bool))
    if not years:
        return None, None
    return years[0], float(clv_snapshots[years[0]][account])


def build_observations(run: dict) -> dict:
    """Split the book into the counted population and the named exclusions.

    Returns a dict with `counted` (list of per-account records) and `excluded`
    (list of `{account, reason}`), so the caller never has to infer a denominator.
    """
    accounts = run.get("by_billing_account") or {}
    snapshots = run.get("clv_snapshots") or {}
    lifetimes = run.get("per_customer_lifetime") or {}

    counted, excluded = [], []
    for account in sorted(accounts):
        record = accounts[account] or {}
        if record.get("still_supplied"):
            excluded.append({"account": account, "reason": EXCLUSION_CENSORED})
            continue
        year, belief = _earliest_belief(snapshots, account)
        if belief is None:
            excluded.append({"account": account, "reason": EXCLUSION_NO_SNAPSHOT})
            continue
        realised = (lifetimes.get(account) or {}).get(
            "net_margin_after_cost_to_serve_gbp")
        if not isinstance(realised, (int, float)) or isinstance(realised, bool):
            excluded.append({"account": account, "reason": EXCLUSION_NO_REALISED})
            continue
        counted.append({
            "account": account,
            "belief_year": year,
            "belief_gbp": belief,
            "realised_gbp": float(realised),
            "error_gbp": belief - float(realised),
            "sign_disagrees": (belief > 0) != (float(realised) > 0),
            # Survives the truth-window caveat: a positive belief against a
            # negative realised total cannot be rescued by adding back positive
            # pre-snapshot earnings, because that only lowers the realised side.
            "sign_error_robust": belief > 0 and float(realised) < 0,
        })
    return {"counted": counted, "excluded": excluded}


def roster_crosscheck(run: dict, counted: list) -> dict:
    """Second, independently-written source for who left. Reported, never used to
    silently overrule `still_supplied` -- a disagreement between two fields that
    should agree is a finding, not something for this module to resolve."""
    churned = run.get("churned_billing_accounts")
    if not isinstance(churned, list):
        return {"available": False, "agrees": None, "only_in_roster": [],
                "only_in_counted": []}
    from_counted = {r["account"] for r in counted}
    from_roster = {a for a in churned if isinstance(a, str)}
    return {
        "available": True,
        "agrees": from_counted == from_roster,
        "only_in_roster": sorted(from_roster - from_counted),
        "only_in_counted": sorted(from_counted - from_roster),
    }


def measure(run: dict) -> tuple:
    """Compute the belief-vs-outcome gap. Returns `(GapResult, detail)`.

    `raw_gap` is the company's mean absolute error in GBP. `g0` is the SAME error
    for a no-skill predictor that assigns every account the population's mean
    realised value -- a predictor with no per-customer information at all. The
    headline divides one by the other, so `gap > 1` reads "worse than knowing
    nothing about the individual customer".
    """
    split = build_observations(run)
    counted, excluded = split["counted"], split["excluded"]
    detail = {"counted": counted, "excluded": excluded,
              "roster_crosscheck": roster_crosscheck(run, counted)}

    if not counted:
        # No population is an UNDEFINED headline, not a zero one. `None` is the
        # designed representation and every downstream reader tests for it.
        return GapResult(
            metric="belief", gap=None, raw_gap=0.0, g0=0.0,
            baseline="no completed customer lifetime in this run -- nothing to score",
            normalisation=NORMALISATION_DIVISOR, raw_gap_is=DIVISOR_RAW_GAP_IS,
            components={"counted": 0, "excluded": len(excluded)},
            note="Population empty; the pair is unmeasured, not measured at zero.",
        ), detail

    beliefs = [r["belief_gbp"] for r in counted]
    truths = [r["realised_gbp"] for r in counted]
    mean_truth = statistics.fmean(truths)
    raw_gap = statistics.fmean([abs(b - t) for b, t in zip(beliefs, truths)])
    g0 = statistics.fmean([abs(mean_truth - t) for t in truths])
    # A degenerate no-skill error means every account realised the same value:
    # there is no per-customer variation for skill to find, so the ratio is
    # undefined rather than infinite.
    gap = (raw_gap / g0) if g0 > 0 else None

    crosscheck = detail["roster_crosscheck"]
    result = GapResult(
        metric="belief",
        gap=gap,
        raw_gap=raw_gap,
        g0=g0,
        normalisation=NORMALISATION_DIVISOR,
        raw_gap_is=DIVISOR_RAW_GAP_IS,
        baseline=(
            "no-skill = assign every account the population's MEAN realised "
            f"lifetime margin (GBP {mean_truth:.2f}); g0 = that predictor's mean "
            f"absolute error (GBP {g0:.2f}). gap>1 means the company's "
            "per-customer CLV carries less information than the portfolio mean."
        ),
        components={
            "counted_accounts": len(counted),
            "excluded_accounts": len(excluded),
            "available_accounts": len(counted) + len(excluded),
            "excluded_right_censored": sum(
                1 for e in excluded if e["reason"] == EXCLUSION_CENSORED),
            "mean_belief_gbp": statistics.fmean(beliefs),
            "mean_realised_gbp": mean_truth,
            "mean_absolute_error_gbp": raw_gap,
            "sign_disagreements": sum(1 for r in counted if r["sign_disagrees"]),
            "sign_errors_robust_to_window_bias": sum(
                1 for r in counted if r["sign_error_robust"]),
            "per_account": [
                {k: r[k] for k in ("account", "belief_year", "belief_gbp",
                                   "realised_gbp", "sign_disagrees")}
                for r in counted
            ],
            "truth_window_bias": (
                "realised total spans the WHOLE lifetime; the belief is taken at "
                "the first year-end snapshot. Truth is therefore measured over a "
                "longer window than the belief forecasts, which flatters an "
                "over-estimating belief -- the headline is conservative for those "
                "cases. No per-account-per-year margin is published, so the "
                "pre-snapshot slice cannot be removed."
            ),
            "roster_sources_agree": crosscheck["agrees"],
            "roster_only_in_churn_list": crosscheck["only_in_roster"],
            "roster_only_in_counted": crosscheck["only_in_counted"],
        },
        note=(
            "Point-in-time backtest of the company's own CLV against realised "
            "lifetime margin, over accounts whose life COMPLETED inside the run. "
            "Still-supplied accounts are excluded as right-censored, which is why "
            "the direct comparison against EP1's live output is impossible: the "
            "accounts EP1 values are exactly the ones whose outcome is unknown, "
            "and the ones whose outcome is known are exactly the ones it refuses "
            "to value. R12: diagnostic, never a target."
        ),
    )
    return result, detail


def _git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="EP1 CLV belief-vs-outcome coupled gap")
    ap.add_argument("--run-output", default=None,
                    help="path to run_output_latest.json")
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args(argv)

    run = load_run_output(args.run_output)
    result, detail = measure(run)

    print("EP1 CLV  company belief  <->  realised customer value")
    print(f"  counted / available   : {len(detail['counted'])} / "
          f"{len(detail['counted']) + len(detail['excluded'])}")
    print(f"  excluded (censored)   : "
          f"{sum(1 for e in detail['excluded'] if e['reason'] == EXCLUSION_CENSORED)}")
    for r in detail["counted"]:
        flag = "  SIGN ERROR" if r["sign_disagrees"] else ""
        robust = " (robust)" if r["sign_error_robust"] else ""
        print(f"    {r['account']:<8} {r['belief_year']}  believed "
              f"{r['belief_gbp']:>12.2f}   realised {r['realised_gbp']:>12.2f}"
              f"{flag}{robust}")
    print(f"  raw_gap (MAE, GBP)    : {result.raw_gap:.4f}")
    print(f"  g0 (no-skill MAE)     : {result.g0:.4f}")
    print(f"  gap = raw/g0          : {result.gap}")
    crosscheck = detail["roster_crosscheck"]
    print(f"  roster sources agree  : {crosscheck['agrees']}")

    if args.write_ledger:
        write_gap_entry(
            LEDGER_KEY, TWIN_ATOM_ID, result,
            measured_at=datetime.now(timezone.utc).isoformat(),
            run_git_commit=_git_head(),
        )
        print(f"  ledger written: {LEDGER_KEY} -> gap={result.gap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
