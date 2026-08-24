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

=============================================================================
WHOSE ESTIMATOR THIS ROW ACTUALLY GRADES -- 2026-08-24, pass 17
=============================================================================

THE LEDGER KEY IS `EP1_clv_three_horizon` AND THE GRADED BELIEF IS NOT EP1'S.
The belief side of this pair is `clv_snapshots`, and that field is built in
`saas/reporting/annual_report.py::_build_clv_snapshots` by calling
`saas/clv_model.py::build_clv` -- a churn-hazard annuity that predates this atom
and is not in `EP1_clv_three_horizon`'s `file_scope`. EP1's own estimator,
`company/analytics/clv_three_horizon.py`, publishes the separate
`three_horizon_clv` table and contributes NOTHING to this measurement.

MEASURED, NOT ARGUED (R15, on the 2026-08-24 20:38 artefact, 80 accounts):

    baseline gap                                     2.595540998141295
    every `three_horizon_clv` value zeroed           2.595540998141295   UNMOVED
    `three_horizon_clv` DELETED from the artefact    2.595540998141295   UNMOVED
    legacy `clv_snapshots` series nudged +1%         2.624227839450484   moved

A control that is bit-identical when its named subject's entire published output
is deleted is not measuring that subject. This is a FOURTH failure shape beside
the three R15 names: the control runs, it can fail, and it fails honestly -- about
something else. Call it MIS-SUBJECTED. It is invisible to a mutation battery aimed
at the checker, because the checker is correct; only a mutation aimed at the
SUBJECT exposes it.

WHY IT IS DECLARED HERE RATHER THAN REPAIRED HERE. EP1's estimator cannot be
backtested today at all: a backtest needs a belief recorded BEFORE the outcome, and
`three_horizon_clv` is a single end-of-run table with no per-year series. Producing
one means writing a snapshot from `run_phase4c_on_phase2b` or the reporting layer,
both OUTSIDE this atom's `file_scope`, and it moves a published surface. So this
pass makes the mis-subjection STATED and MECHANISED instead of leaving it implicit:
`belief_provenance()` resolves the producing callable from the source tree by AST,
`components.grades_atom_estimator` carries the answer onto the ledger entry, and
`tests/tools/test_couple_clv.py` fails the day EP1's estimator IS wired in and this
declaration is not updated with it.

The pre-existing `note` said the live comparison was impossible because of
right-censoring. That is true and it is not the whole truth: it explains why EP1's
CURRENT values cannot be scored, and says nothing about the belief that was scored
instead. A reader of a row keyed `EP1_clv_three_horizon` would reasonably take the
number for EP1's. It is not.
"""
from __future__ import annotations

import argparse
import ast
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

#: Why the whole measurement is unavailable rather than empty.
UNAVAILABLE_NO_ROSTER = "no_ceased_roster_published"


#: WHERE THE GRADED BELIEF COMES FROM. `clv_snapshots` is written by this
#: function, which calls this callable, imported from this module. Every one of
#: the three is CHECKED against the source tree by `belief_provenance()` -- a
#: constant that merely asserts a wiring is the prose-only shape MAKE_IT_STICK
#: says evaporates.
BELIEF_FIELD = "clv_snapshots"
BELIEF_PRODUCER_FILE = "saas/reporting/annual_report.py"
BELIEF_PRODUCER_FUNCTION = "_build_clv_snapshots"
BELIEF_ESTIMATOR_CALLABLE = "build_clv"
BELIEF_ESTIMATOR_MODULE = "saas.clv_model"

#: The atom this ledger row is KEYED to, and whose estimator it does NOT grade.
ATOM_ESTIMATOR_MODULE = "company.analytics.clv_three_horizon"

#: The declaration. `False` is the measured state, not a placeholder: see the
#: mutation table in this module's docstring. Flipping this to `True` without
#: also making the belief come from EP1's estimator is caught by
#: `test_the_declaration_cannot_claim_ep1_while_the_producer_says_otherwise`.
GRADES_ATOM_ESTIMATOR = False

#: Why the measurement is unavailable rather than wrong.
UNAVAILABLE_NO_PROVENANCE = "belief_producer_not_resolvable_from_source"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def belief_provenance(repo_root=None) -> dict:
    """Resolve, from the SOURCE TREE, which estimator produces the graded belief.

    Returns the observed facts plus `verified` -- whether they match this module's
    declared constants. Never returns a cheerful default: an unreadable or
    unparseable producer, or a producer function that is not there, RAISES
    (`FileNotFoundError` / `ValueError`). An unavailable check is a FAILED check
    (R15 fail-silent), and this one exists precisely to notice a wiring change.

    INDEPENDENCE (R15 tautology). The facts are read from
    `saas/reporting/annual_report.py`'s AST -- the call graph as written -- not
    from any string this module or that one declares about itself. Nothing here
    imports the producer: importing it would resolve names through whatever the
    interpreter happens to have loaded, and the question is what the SOURCE says.

    `grades_atom_estimator` is the load-bearing output. It is True only if EP1's
    estimator module is reachable by name inside the producing function, which is
    the checkable form of "this row grades the atom it is keyed to".
    """
    root = Path(repo_root) if repo_root is not None else _repo_root()
    producer = root / BELIEF_PRODUCER_FILE
    if not producer.is_file():
        raise FileNotFoundError(
            f"belief producer {BELIEF_PRODUCER_FILE} is missing -- the provenance "
            "of the graded belief cannot be established, so the measurement is "
            "unavailable rather than clean")
    tree = ast.parse(producer.read_text(encoding="utf-8"), filename=str(producer))

    fn = next((n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == BELIEF_PRODUCER_FUNCTION), None)
    if fn is None:
        raise ValueError(
            f"{BELIEF_PRODUCER_FILE} no longer defines "
            f"{BELIEF_PRODUCER_FUNCTION}; the belief this row grades has moved "
            "and the declaration in tools/couple_clv.py is stale")

    called = {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    called |= {n.func.attr for n in ast.walk(fn)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}

    # Where the called estimator was imported from, read at module scope.
    imported_from = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if any(a.name == BELIEF_ESTIMATOR_CALLABLE for a in node.names):
                imported_from = node.module
                break

    # Is EP1's own estimator reachable by name inside the producing function?
    names_in_fn = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    names_in_fn |= {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
    ep1_leaf = ATOM_ESTIMATOR_MODULE.rsplit(".", 1)[-1]
    ep1_wired = ep1_leaf in names_in_fn or any(
        isinstance(n, ast.ImportFrom) and n.module
        and ATOM_ESTIMATOR_MODULE in n.module
        for n in ast.walk(fn))

    observed = {
        "belief_field": BELIEF_FIELD,
        "produced_by": f"{BELIEF_PRODUCER_FILE}::{BELIEF_PRODUCER_FUNCTION}",
        "estimator_callable": BELIEF_ESTIMATOR_CALLABLE,
        "estimator_imported_from": imported_from,
        "estimator_is_called": BELIEF_ESTIMATOR_CALLABLE in called,
        "atom_estimator_module": ATOM_ESTIMATOR_MODULE,
        "atom_estimator_wired_into_producer": ep1_wired,
    }
    observed["grades_atom_estimator"] = bool(ep1_wired)
    observed["verified"] = (
        observed["estimator_is_called"]
        and imported_from == BELIEF_ESTIMATOR_MODULE
        and observed["grades_atom_estimator"] == GRADES_ATOM_ESTIMATOR
    )
    return observed


def magnitude_diagnostic(counted: list) -> dict:
    """R4 decomposition of the error: is it SCALE, or is it information?

    `gap > 1` is usually read as "the estimate carries less information about the
    individual customer than the portfolio mean". That reading is not safe,
    because a mean-absolute-error ratio CONFLATES two different failures: getting
    the ordering wrong, and getting the ordering right at the wrong size. An
    estimator that ranks every customer correctly but is uniformly three times too
    large scores worse than no-skill here while being far more useful than the
    mean.

    So this reports both, and the two must be read together:

      * `magnitude_inflated_accounts` -- how often |belief| EXCEEDS |realised|.
        Under an unbiased estimator this is a coin flip; a run of them is a
        systematic scale error and points R4 at the horizon, not the ranking.
      * `best_single_scale` -- the ONE constant that, applied to every belief,
        minimises the same mean absolute error, and the gap it would produce.

    `best_single_scale` IS FITTED IN-SAMPLE ON THE COUNTED POPULATION and is
    therefore NOT an estimate of out-of-sample skill; reported as such, it would
    be the tautology pattern. It is an ATTRIBUTION: the share of the headline that
    one scalar can absorb, which is the share not attributable to per-account
    error. R12 APPLIES WITH FULL FORCE -- this number is a diagnostic pointing at
    a mechanism to investigate, and multiplying the estimator by it to move the
    headline would be exactly the goal-seeking R12 forbids.
    """
    if not counted:
        return {"available": False, "reason": "empty population"}
    beliefs = [r["belief_gbp"] for r in counted]
    truths = [r["realised_gbp"] for r in counted]
    mean_truth = statistics.fmean(truths)
    g0 = statistics.fmean([abs(mean_truth - t) for t in truths])

    def mae(scale):
        return statistics.fmean(
            [abs(scale * b - t) for b, t in zip(beliefs, truths)])

    # The MAE-optimal scale lies at one of the points where a term's kink sits,
    # t_i / b_i -- an exact search over the candidate set, no grid and no RNG.
    candidates = sorted({t / b for b, t in zip(beliefs, truths) if b != 0} | {0.0, 1.0})
    best = min(candidates, key=mae)
    return {
        "available": True,
        "magnitude_inflated_accounts": sum(
            1 for b, t in zip(beliefs, truths) if abs(b) > abs(t)),
        "population": len(counted),
        "best_single_scale": best,
        "gap_after_best_single_scale": (mae(best) / g0) if g0 > 0 else None,
        "in_sample": True,
        "reading": (
            "share of the headline one scalar absorbs = the share NOT explained "
            "by per-account error. Fitted in-sample: an attribution, never a "
            "skill estimate and never a correction to apply (R12)."
        ),
    }


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


def known_accounts(run: dict) -> set:
    """Every account this run says ANYTHING about.

    THE POPULATION SOURCE, AND THE REASON IT IS NOT `by_billing_account`
    (2026-08-24, pass 16). This module used to walk `by_billing_account` and so
    could only ever see the accounts that table happens to hold. That table is
    built in `saas/reporting/annual_report.py` by iterating `CUSTOMERS` -- the
    hand-authored SEED roster -- while `clv_snapshots`, `per_customer_lifetime`
    and `churned_billing_accounts` are all built over
    `CUSTOMERS + SUCCESSOR_CUSTOMERS + DRAWN_CUSTOMERS`. So as the drawn book
    grew, the harness grading EP1 stayed pinned to the 13 seed accounts:
    measured on the 2026-08-24 book, 5 accounts counted where 19 were available,
    and the headline came out bit-identical to the reading four passes earlier
    on a book a sixth the size. A gap that cannot move when the book grows is
    not a measurement of the estimator, it is a measurement of the fixture.

    Taking the UNION rather than any one field is deliberate: each of the four
    sources omits accounts the others hold, and a denominator drawn from one of
    them would silently inherit that omission -- which is the defect this
    function exists to close, one field along.
    """
    accounts = set(run.get("by_billing_account") or {})
    for snapshot in (run.get("clv_snapshots") or {}).values():
        if isinstance(snapshot, dict):
            accounts.update(k for k in snapshot if isinstance(k, str))
    accounts.update(k for k in (run.get("per_customer_lifetime") or {})
                    if isinstance(k, str))
    accounts.update(a for a in (run.get("churned_billing_accounts") or [])
                    if isinstance(a, str))
    return accounts


def ceased_roster(run: dict):
    """The world's own statement of who left, or `None` if it did not publish one.

    THE CEASED AUTHORITY, and it is the WORLD's field rather than the reporting
    layer's. `churned_billing_accounts` is written in `simulation/run_phase2b.py`
    when a churn event actually fires in the term loop;
    `by_billing_account[...]["still_supplied"]` is re-derived one layer up from
    settlement quiet, over the seed accounts only. For a belief-vs-OUTCOME
    backtest the outcome side must come from the world, and
    `saas/enterprise_value.py` already frames the pair that way in its own
    comment.

    `None` -- not an empty set -- when the field is absent or malformed. An
    absent authority makes the measurement UNAVAILABLE, and the caller says so
    rather than treating "nobody is on the roster" as "nobody has left", which
    would count the entire book as right-censored and publish a clean empty
    population (R15 fail-open).
    """
    churned = run.get("churned_billing_accounts")
    if not isinstance(churned, list):
        return None
    return {a for a in churned if isinstance(a, str)}


def build_observations(run: dict) -> dict:
    """Split the book into the counted population and the named exclusions.

    Returns a dict with `counted` (list of per-account records), `excluded`
    (list of `{account, reason}`) and `unavailable` (a named reason, or None), so
    the caller never has to infer a denominator.
    """
    accounts = run.get("by_billing_account") or {}
    snapshots = run.get("clv_snapshots") or {}
    lifetimes = run.get("per_customer_lifetime") or {}
    roster = ceased_roster(run)
    if roster is None:
        return {"counted": [], "excluded": [], "unavailable": UNAVAILABLE_NO_ROSTER}

    counted, excluded = [], []
    for account in sorted(known_accounts(run)):
        if account not in roster:
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
    return {"counted": counted, "excluded": excluded, "unavailable": None}


def roster_crosscheck(run: dict, counted: list) -> dict:
    """Independent second derivation of who left, checked against the authority.

    WHICH SIDE IS THE CHECK CHANGED IN PASS 16, AND THAT IS THE POINT. This used
    to compare the roster against a population derived from
    `by_billing_account.still_supplied`. Once the roster becomes the AUTHORITY
    (see `ceased_roster`), comparing it against the population it produced would
    be the TAUTOLOGY pattern -- the check would read its own input. So the check
    is now the signal that was previously unused: an account the SNAPSHOT SERIES
    dropped.

    Independence, stated so it can be argued with: the roster is a churn EVENT in
    the term loop (`simulation/run_phase2b.py`); the snapshot drop is
    `_build_clv_snapshots` excluding an account its own truncated record window
    shows as ceased, via the settlement-quiet rule in `ceased_billing_accounts`.
    An event firing and a meter going quiet are two different derivations, and
    neither is computed from the other.

    COVERAGE IS DECLARED, NOT ASSUMED. The snapshot series can only speak about
    accounts it ever valued; an account that churned before its first year-end
    snapshot is invisible to it and is reported under `never_snapshotted` rather
    than counted as a disagreement. `agrees` is `None` -- never `True` -- when
    the check cannot be run at all, because an unavailable check is a FAILED
    check (R15 fail-silent), and `still_supplied` is reported beside it as a
    third, partial-coverage signal over the accounts that have such a row.
    """
    roster = ceased_roster(run)
    snapshots = run.get("clv_snapshots") or {}
    years = sorted(y for y, snap in snapshots.items() if isinstance(snap, dict))
    if roster is None or not years:
        return {"available": False, "agrees": None, "only_in_roster": [],
                "only_in_snapshot_drop": [], "never_snapshotted": [],
                "snapshot_coverage": 0, "still_supplied_disagrees": []}

    def _valued(year):
        return {a for a, v in snapshots[year].items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)}

    ever = set().union(*(_valued(y) for y in years))
    dropped = ever - _valued(years[-1])
    # Restricted to the accounts the snapshot series can actually speak about.
    roster_seen = roster & ever
    accounts = run.get("by_billing_account") or {}
    return {
        "available": True,
        "agrees": roster_seen == dropped,
        "only_in_roster": sorted(roster_seen - dropped),
        "only_in_snapshot_drop": sorted(dropped - roster_seen),
        "never_snapshotted": sorted(roster - ever),
        "snapshot_coverage": len(ever),
        # Third signal, partial coverage: a seed account whose reporting-layer
        # `still_supplied` contradicts the world's roster. Reported, never used.
        "still_supplied_disagrees": sorted(
            a for a, rec in accounts.items()
            if isinstance(rec, dict) and "still_supplied" in rec
            and bool(rec["still_supplied"]) == (a in roster)),
    }


def measure(run: dict) -> tuple:
    """Compute the belief-vs-outcome gap. Returns `(GapResult, detail)`.

    `raw_gap` is the company's mean absolute error in GBP. `g0` is the SAME error
    for a no-skill predictor that assigns every account the population's mean
    realised value -- a predictor with no per-customer information at all. The
    headline divides one by the other, so `gap > 1` reads "worse than knowing
    nothing about the individual customer".
    """
    # RESOLVED FIRST, AND ALLOWED TO RAISE. If the source tree can no longer say
    # which estimator produced the graded belief, this measurement does not know
    # what it is measuring, and publishing a headline anyway is the fail-silent
    # pattern with the subject rather than the checker as its victim.
    provenance = belief_provenance()

    split = build_observations(run)
    counted, excluded = split["counted"], split["excluded"]
    detail = {"counted": counted, "excluded": excluded,
              "unavailable": split["unavailable"],
              "roster_crosscheck": roster_crosscheck(run, counted),
              "belief_provenance": provenance,
              "error_decomposition": magnitude_diagnostic(counted)}

    if split["unavailable"] is not None:
        # The ceased AUTHORITY is missing, which is not the same as an empty
        # population and must not read like one: without it every account would
        # fall through as right-censored and the pair would report a clean
        # nothing-to-score (R15 fail-open).
        return GapResult(
            metric="belief", gap=None, raw_gap=0.0, g0=0.0,
            baseline=("the run publishes no ceased roster -- who left is unknown, "
                      "so belief cannot be scored against outcome"),
            normalisation=NORMALISATION_DIVISOR, raw_gap_is=DIVISOR_RAW_GAP_IS,
            components={"counted": 0, "excluded": 0,
                        "unavailable_reason": split["unavailable"],
                        # Carried even here: WHOSE estimator this row would have
                        # graded is a fact about the wiring, not about the
                        # population, and a branch that drops it lets an
                        # unmeasurable run hide a mis-subjected key.
                        "belief_provenance": provenance,
                        "grades_atom_estimator": provenance[
                            "grades_atom_estimator"]},
            note=("Measurement UNAVAILABLE, not zero: the ceased authority "
                  f"({split['unavailable']}) is absent from the run artefact."),
        ), detail

    if not counted:
        # No population is an UNDEFINED headline, not a zero one. `None` is the
        # designed representation and every downstream reader tests for it.
        return GapResult(
            metric="belief", gap=None, raw_gap=0.0, g0=0.0,
            baseline="no completed customer lifetime in this run -- nothing to score",
            normalisation=NORMALISATION_DIVISOR, raw_gap_is=DIVISOR_RAW_GAP_IS,
            # The cross-check is reported even with nothing to score: whether the
            # two cessation derivations agree is a fact about the RUN, and a
            # branch that dropped it would report an empty population without
            # saying whether the check that would have found accounts could run.
            components={"counted": 0, "excluded": len(excluded),
                        "roster_sources_agree": detail[
                            "roster_crosscheck"]["agrees"],
                        "belief_provenance": provenance,
                        "grades_atom_estimator": provenance[
                            "grades_atom_estimator"]},
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
            "roster_only_in_snapshot_drop": crosscheck["only_in_snapshot_drop"],
            "roster_never_snapshotted": crosscheck["never_snapshotted"],
            "crosscheck_snapshot_coverage": crosscheck["snapshot_coverage"],
            "still_supplied_disagrees_with_roster": crosscheck[
                "still_supplied_disagrees"],
            "belief_provenance": provenance,
            "grades_atom_estimator": provenance["grades_atom_estimator"],
            "error_decomposition": magnitude_diagnostic(counted),
        },
        note=(
            "Point-in-time backtest of a company CLV belief against realised "
            "lifetime margin, over accounts whose life COMPLETED inside the run. "
            "WHOSE BELIEF: the graded field is `clv_snapshots`, produced by "
            f"{BELIEF_PRODUCER_FILE}::{BELIEF_PRODUCER_FUNCTION} via "
            f"{BELIEF_ESTIMATOR_MODULE}.{BELIEF_ESTIMATOR_CALLABLE}. Despite this "
            "row's key it does NOT grade EP1's estimator "
            "(company/analytics/clv_three_horizon.py): zeroing or deleting EP1's "
            "entire published output leaves this headline bit-identical, measured "
            "2026-08-24. EP1 cannot be backtested yet because it publishes only a "
            "terminal table and a backtest needs a belief recorded before the "
            "outcome. Separately, still-supplied accounts are excluded as "
            "right-censored, so EP1's CURRENT values would be unscoreable even "
            "with a series: the accounts it values are the ones whose outcome is "
            "unknown. R12: diagnostic, never a target."
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

    prov = detail["belief_provenance"]
    print(f"  belief graded         : {prov['belief_field']} "
          f"<- {prov['produced_by']} -> "
          f"{prov['estimator_imported_from']}.{prov['estimator_callable']}")
    print(f"  grades EP1's estimator: {prov['grades_atom_estimator']}"
          + ("" if prov["grades_atom_estimator"]
             else "   <- this row is keyed to EP1 and does not grade it"))
    dec = detail.get("error_decomposition") or {}
    if dec.get("available"):
        print(f"  |belief| > |realised| : "
              f"{dec['magnitude_inflated_accounts']}/{dec['population']}")
        print(f"  one-scalar attribution: scale {dec['best_single_scale']:.3f} "
              f"-> gap {dec['gap_after_best_single_scale']:.4f} "
              f"(IN-SAMPLE; diagnostic, never a correction -- R12)")

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
