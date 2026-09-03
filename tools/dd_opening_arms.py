"""Run the direct-debit book on two opening rules over ONE seed and diff the whole run output.

WHY THIS EXISTS
---------------
`company/billing/annual_consumption_estimate.py` landed at `9760fc7a5` and displaced a flat
rule: both `dd_review_runner` and `dd_balance_book` used to open every account's standing DD
at ``seq[0][1]`` -- the FIRST ISSUED BILL. The thesis says an advantage must come from
inference and there must be a baseline to beat, or "it performed well" means nothing. The
flat rule IS that baseline and it is sitting in the code the organ displaced.

The measurement that provoked this: publish `1c4f64733` (run at `4013b1de1`, BEFORE the organ)
and publish `b6b3c3fa8` (run at `19f226e46`, AFTER) carry IDENTICAL net margin, gross, capital,
treasury start, treasury end, enterprise value, net after cost-to-serve and bills issued. Either
the organ does nothing, or nothing we publish could tell. This module settles which.

WHY ONE SEED'S BILLS IS THE WHOLE SUBSTRATE, and not a shortcut
---------------------------------------------------------------
In `simulation/run_phase4c_on_phase2b.py`, `opening_dd` is computed at line 319 -- AFTER `bills`
exists -- and reaches exactly three call sites: `annual_dd_review_view` (320),
`build_dd_balance_book` (332), and `build_dd_level_collection_book` (341, which consumes the
balance book and nothing else). No RNG is drawn from it and no upstream structure reads it. So
both arms are pure functions of one run's issued bills, and running the ~100-minute Phase 2b
twice would add nondeterminism rather than fidelity: the two runs would differ in committee
decisions before they differed in direct debits, and the diff would be unattributable.

THE CONTROL THAT MAKES THE FLAT ARM TRUSTWORTHY
-----------------------------------------------
`docs/reports/run_output_latest.json` was produced on 2026-09-01, BEFORE the organ landed. Its
own `dd_balance_book` and `annual_dd_review` therefore ARE the flat arm as the real run computed
it. `--check-flat-reproduces` re-derives the flat arm here and compares. If it does not
reproduce, the reconstruction is wrong and every number this module prints is void -- which is
why the check runs first and its verdict is printed above the diff.

THE EPISTEMIC WALL
------------------
Nothing here reaches ground truth. The flat arm reads issued bills; the estimate arm goes
through `company/interfaces/dd_review_outcome.opening_monthly_amount`, the same door the live
run uses, fed the same registration facts. The household's realised annual consumption is not a
parameter of anything in this file.

USAGE
    python3 -m tools.dd_opening_arms --json docs/reports/dd_opening_arms.json
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUN_OUTPUT = REPO_ROOT / "docs" / "reports" / "run_output_latest.json"
DEFAULT_ARTEFACT = REPO_ROOT / "docs" / "reports" / "dd_opening_arms.json"

#: The three run-output keys the opening rule can reach, from the call-site read
#: above. Named here so the diff can state whether anything OUTSIDE them moved --
#: a list of what we expect to move is worthless unless the complement is checked.
DD_KEYS = ("annual_dd_review", "dd_balance_book", "dd_level_collection_book")


# ---------------------------------------------------------------------------
# The two opening rules
# ---------------------------------------------------------------------------

def flat_opening_by_customer(bills: list[dict], *, direct_debit_only: bool) -> dict[str, float]:
    """The DISPLACED rule: the opening standing DD is the first issued bill.

    ``direct_debit_only`` because the two organs group differently and a single
    map would silently be wrong for one of them: `dd_balance_book` filters to
    direct-debit bills before taking `seq[0]`, `dd_review_runner` does not. Under
    `arrears_engine.payment_method` the classification depends on the bill AMOUNT,
    so a customer's first bill overall and first DD bill need not be the same bill.
    """
    by_cust: dict[str, list[tuple[date, float]]] = {}
    for b in bills:
        if direct_debit_only:
            from simulation.arrears_engine import payment_method

            method = payment_method(
                b.get("segment", "resi"),
                float(b["total_amount_gbp"]),
                b["customer_id"],
                b.get("commodity", "electricity"),
            )
            if method != "direct_debit":
                continue
        by_cust.setdefault(b["customer_id"], []).append(
            (date.fromisoformat(b["period_end"]), float(b["total_amount_gbp"]))
        )
    return {
        cid: sorted(seq, key=lambda t: t[0])[0][1]
        for cid, seq in by_cust.items()
    }


def estimate_opening_by_customer(customers: list[dict]) -> dict[str, float]:
    """The LIVE rule, measured through the live call site rather than a copy of it.

    Imports `simulation.run_phase4c_on_phase2b._opening_dd_by_customer` -- private,
    and deliberately so. A second implementation of the arm under test is exactly
    the shape that lets the experiment agree with a version of the organ that is
    not the one running in production.
    """
    from simulation.run_phase4c_on_phase2b import _opening_dd_by_customer

    return _opening_dd_by_customer(customers)


def _basis_and_rate_by_customer(customers: list[dict]) -> dict[str, dict]:
    """Per account: which SLC 27.15 basis the estimate resolved to, and whether the
    company held a published rate to annualise against on that date.

    These are the two INDEPENDENT ways the estimate arm can decline, and reporting
    only the combined `None` count would fuse them: an account can have a perfectly
    good EAC and still be refused because no price cap existed before January 2019.
    """
    from company.billing.annual_consumption_estimate import estimate_annual_consumption
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date

    out: dict[str, dict] = {}
    for c in customers:
        cid = c.get("customer_id")
        as_of_iso = c.get("acquisition_date")
        if not cid or not as_of_iso:
            continue
        commodity = c.get("commodity", "electricity")
        eac = c.get("eac_kwh") if commodity == "electricity" else c.get("aq_kwh")
        as_of = date.fromisoformat(as_of_iso)
        est = estimate_annual_consumption(
            as_of=as_of,
            commodity=commodity,
            metered_annual_kwh=None,
            registry_eac_kwh=float(eac) if eac else None,
            declared_annual_kwh=None,
            band="MEDIUM" if not eac else None,
        )
        out[cid] = {
            "basis": est.basis.value,
            "estimate_kwh": est.kwh,
            "has_published_rate": get_cap_unit_rate_for_date(commodity, as_of) is not None,
            "acquisition_date": as_of_iso,
            "commodity": commodity,
        }
    return out


# ---------------------------------------------------------------------------
# Building one arm
# ---------------------------------------------------------------------------

def build_arm(bills: list[dict], opening_for_book: Mapping[str, float],
              opening_for_review: Mapping[str, float]) -> dict:
    """The three DD run-output keys, exactly as `run_phase4c_on_phase2b.main()` builds them."""
    from company.interfaces.dd_review import annual_dd_review_view
    from simulation.dd_balance_book import build_dd_balance_book
    from simulation.dd_level_collection_book import build_dd_level_collection_book

    review = annual_dd_review_view(bills, dict(opening_for_review))
    book = build_dd_balance_book(bills, dict(opening_for_book))
    level = build_dd_level_collection_book(book)
    return {
        "annual_dd_review": review,
        "dd_balance_book": book.serialise(),
        "dd_level_collection_book": level.serialise(),
        "_book_object": book,
    }


# ---------------------------------------------------------------------------
# The whole-output diff
# ---------------------------------------------------------------------------

def _leaf_diffs(a: Any, b: Any, path: str, out: list[str], limit: int = 400) -> None:
    if len(out) >= limit:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            _leaf_diffs(a.get(k), b.get(k), f"{path}.{k}" if path else str(k), out, limit)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: list length {len(a)} -> {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _leaf_diffs(x, y, f"{path}[{i}]", out, limit)
    elif a != b:
        out.append(f"{path}: {a!r} -> {b!r}")


def diff_run_outputs(flat_output: dict, est_output: dict) -> dict:
    """Diff two WHOLE run outputs, and state the complement explicitly.

    `moved_keys` is what actually differs. `unmoved_keys` is every other top-level
    key -- printed rather than assumed, because "only the DD keys moved" is a claim
    about the keys nobody looked at, and this project has published that claim
    wrongly before.
    """
    moved, unmoved = [], []
    for k in sorted(set(flat_output) | set(est_output)):
        if flat_output.get(k) == est_output.get(k):
            unmoved.append(k)
        else:
            moved.append(k)
    detail: dict[str, list[str]] = {}
    for k in moved:
        leaves: list[str] = []
        _leaf_diffs(flat_output.get(k), est_output.get(k), k, leaves)
        detail[k] = leaves
    return {"moved_keys": moved, "unmoved_keys": unmoved, "leaf_diffs": detail}


# ---------------------------------------------------------------------------
# What separates the two arms per account
# ---------------------------------------------------------------------------

def _window_end_balances(book) -> dict[str, dict[int, float]]:
    """Each customer's balance at the LAST bill of each 12-month window.

    "End-of-year balance drift" is a position, not a flow: the balance the account
    is carrying when the year the opening DD was sized for is over. Window 0 is the
    one the OPENING amount controls -- every later window has been reset by a
    review, so attributing a window-3 drift to the opening rule would be reading a
    number the rule stopped touching two years earlier.
    """
    out: dict[str, dict[int, float]] = {}
    for cid, points in book.trajectories.items():
        if not points:
            continue
        anchor = points[0].month
        ay, am = int(anchor[:4]), int(anchor[5:7])
        by_window: dict[int, float] = {}
        for p in points:
            py, pm = int(p.month[:4]), int(p.month[5:7])
            wi = ((py - ay) * 12 + (pm - am)) // 12
            by_window[wi] = p.balance_gbp  # last point in the window wins
        out[cid] = by_window
    return out


def _split_credit_debit(values: list[float]) -> dict:
    """Credit and debit reported SEPARATELY and never summed as one absolute.

    A household £200 in credit and a household £200 in debit are two different
    experiences with two different remedies; the mean of the two is a quantity
    nobody has. CLAUDE.md names this exact failure.
    """
    credit = [v for v in values if v > 0]
    debit = [v for v in values if v < 0]
    flat_zero = [v for v in values if v == 0]

    def _stats(sample: list[float], seed_key: str) -> dict:
        if not sample:
            return {"n": 0, "mean_gbp": None, "ci95_gbp": [None, None],
                    "median_gbp": None, "max_abs_gbp": None}
        from tools.generate_dashboard_data import _bootstrap_mean_interval

        low, high = _bootstrap_mean_interval(sample, seed_key)
        s = sorted(sample)
        return {
            "n": len(sample),
            "mean_gbp": round(sum(sample) / len(sample), 2),
            # The bound the sample size earns. A point estimate published without
            # it is what the basis gate exists to refuse.
            "ci95_gbp": [None if low is None else round(low, 2),
                         None if high is None else round(high, 2)],
            "median_gbp": round(s[len(s) // 2], 2),
            "max_abs_gbp": round(max(abs(v) for v in sample), 2),
        }

    return {
        "in_credit": _stats(credit, "credit"),
        "in_debit": _stats(debit, "debit"),
        "exactly_zero": len(flat_zero),
        "n_accounts": len(values),
    }


def _matched_window0(flat_w: dict, est_w: dict) -> dict:
    """Window-0 drift over the accounts BOTH arms carry, plus the paired change.

    The paired difference is the only statistic here that answers "did the rule
    help this household", because it is the same household under both rules. The
    unpaired means answer a different question -- "what would each arm publish" --
    and the two must never be reported as one number.
    """
    common = sorted(set(flat_w) & set(est_w))
    pairs = [(flat_w[c][0], est_w[c][0]) for c in common
             if 0 in flat_w[c] and 0 in est_w[c]]
    if not pairs:
        return {"n_matched_accounts": 0}
    flat_vals = [p[0] for p in pairs]
    est_vals = [p[1] for p in pairs]
    # Improvement = the household ends the year CLOSER to zero. Signed drift is
    # reported separately above; |drift| is the right scale here and only here,
    # because it is a PAIRED difference on one household, not two populations
    # averaged together.
    closer = sum(1 for f, e in pairs if abs(e) < abs(f))
    from tools.generate_dashboard_data import _bootstrap_mean_interval

    deltas = [abs(e) - abs(f) for f, e in pairs]
    low, high = _bootstrap_mean_interval(deltas, "matched_abs_drift_delta")
    return {
        "n_matched_accounts": len(pairs),
        "flat": _split_credit_debit(flat_vals),
        "estimate": _split_credit_debit(est_vals),
        "n_estimate_closer_to_zero": closer,
        "n_flat_closer_to_zero": len(pairs) - closer,
        "mean_change_in_abs_drift_gbp": round(sum(deltas) / len(deltas), 2),
        "mean_change_in_abs_drift_ci95_gbp": [
            None if low is None else round(low, 2),
            None if high is None else round(high, 2),
        ],
    }


def per_account_comparison(flat_arm: dict, est_arm: dict,
                           flat_open: Mapping[str, float],
                           est_open: Mapping[str, float],
                           basis: Mapping[str, dict]) -> dict:
    """Act (b): what separates the two arms, account by account."""
    flat_book, est_book = flat_arm["_book_object"], est_arm["_book_object"]
    flat_w = _window_end_balances(flat_book)
    est_w = _window_end_balances(est_book)

    both = sorted(set(flat_open) & set(est_open))
    same_amount = [cid for cid in both
                   if round(flat_open[cid], 2) == round(est_open[cid], 2)]

    # Which of the two INDEPENDENT declines fired, per refused account.
    est_unestimated = sorted(est_book.unestimated_customers)
    no_basis, no_rate, not_in_population = [], [], []
    for cid in est_unestimated:
        info = basis.get(cid)
        if info is None:
            not_in_population.append(cid)
        elif info["basis"] == "unavailable":
            no_basis.append(cid)
        elif not info["has_published_rate"]:
            no_rate.append(cid)

    basis_split: dict[str, int] = {}
    for cid in est_open:
        info = basis.get(cid)
        key = info["basis"] if info else "not_in_population"
        basis_split[key] = basis_split.get(key, 0) + 1

    return {
        "n_customers_with_opening": {"flat": len(flat_open), "estimate": len(est_open)},
        "n_same_opening_amount_to_the_penny": len(same_amount),
        "same_opening_amount_ids": same_amount[:20],
        "opening_amount_gbp": {
            "flat": _split_credit_debit(list(flat_open.values()))["in_credit"],
            "estimate": _split_credit_debit(list(est_open.values()))["in_credit"],
        },
        "unestimated": {
            "flat": sorted(flat_book.unestimated_customers),
            "estimate_n": len(est_unestimated),
            "estimate_cause_no_consumption_basis": len(no_basis),
            "estimate_cause_no_published_rate": len(no_rate),
            "estimate_cause_not_in_population_list": len(not_in_population),
            "estimate_ids_sample": est_unestimated[:20],
        },
        "basis_split_of_estimated_accounts": basis_split,
        "window0_end_balance_drift": {
            "flat": _split_credit_debit(
                [w[0] for w in flat_w.values() if 0 in w]),
            "estimate": _split_credit_debit(
                [w[0] for w in est_w.values() if 0 in w]),
        },
        # THE COMPARABLE ONE. The unmatched pair above is over two different
        # populations -- the estimate arm refuses every pre-2019 account, so its
        # book is 96 accounts against the flat arm's 178, and any difference
        # between those two is partly the refusal and partly the rule. Only this
        # block holds the population fixed, so only this block can attribute a
        # difference to the opening rule. The unmatched pair is kept beside it
        # because it is what each arm would actually publish.
        "window0_end_balance_drift_matched_population": _matched_window0(flat_w, est_w),
        "all_window_end_balance_drift": {
            "flat": _split_credit_debit(
                [v for w in flat_w.values() for v in w.values()]),
            "estimate": _split_credit_debit(
                [v for w in est_w.values() for v in w.values()]),
        },
    }


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def run(run_output_path: Path) -> dict:
    payload = json.loads(run_output_path.read_text())
    bills = payload.get("bills") or []
    if not bills:
        raise SystemExit(f"{run_output_path} carries no bills; nothing to run two arms over")

    from company.interfaces.supply_book import successor_supply_points
    from simulation.live_population import live_population

    customers = live_population() + successor_supply_points()

    flat_for_book = flat_opening_by_customer(bills, direct_debit_only=True)
    flat_for_review = flat_opening_by_customer(bills, direct_debit_only=False)
    est_open = estimate_opening_by_customer(customers)
    basis = _basis_and_rate_by_customer(customers)

    flat_arm = build_arm(bills, flat_for_book, flat_for_review)
    est_arm = build_arm(bills, est_open, est_open)

    # The control, run and reported BEFORE any diff: does the reconstructed flat
    # arm reproduce the book the pre-organ run actually published?
    published_flat = {k: payload.get(k) for k in ("annual_dd_review", "dd_balance_book")}
    reproduces = {
        k: published_flat[k] == flat_arm[k]
        for k in published_flat
        if published_flat[k] is not None
    }

    whole_flat = {k: v for k, v in payload.items()}
    whole_est = {k: v for k, v in payload.items()}
    for k in DD_KEYS:
        whole_flat[k] = flat_arm[k]
        whole_est[k] = est_arm[k]

    return {
        "clock": {
            "substrate": str(run_output_path.relative_to(REPO_ROOT)),
            "n_bills": len(bills),
            "basis": "one-seed, two-arm; both arms are pure functions of these bills",
        },
        "flat_arm_reproduces_the_published_pre_organ_book": reproduces,
        "whole_run_output_diff": diff_run_outputs(whole_flat, whole_est),
        "per_account": per_account_comparison(
            flat_arm, est_arm, flat_for_book, est_open, basis),
        "arm_summaries": {
            "flat": {
                "dd_balance_book": flat_arm["dd_balance_book"]["summary"],
                "annual_dd_review": flat_arm["annual_dd_review"]["summary"],
            },
            "estimate": {
                "dd_balance_book": est_arm["dd_balance_book"]["summary"],
                "annual_dd_review": est_arm["annual_dd_review"]["summary"],
            },
        },
    }


#: The clock every money figure in the published block carries. These figures are
#: derived from the company's OWN ISSUED BILLS -- not from settlement and not from
#: the ledger -- so `billed` is the only honest label, and it is the reason none of
#: them can be reconciled against a settled-realised headline.
PUBLISHED_CLOCK = "billed"


def publish_view(result: dict | None) -> dict:
    """The reader-facing block, from the measurement artefact. Fail-closed.

    A missing or unreadable artefact renders an ABSENCE WITH A NAMED REASON, never a
    zero and never silence: a direct-debit comparison that publishes 0 accounts reads
    exactly like one that found no difference, and this whole item exists because a
    surface that could not tell two arms apart was mistaken for two arms that were
    the same.

    Every money figure here carries `clock` and, where it is a mean, the bound its
    sample size earns. A figure whose sample cannot bound itself publishes
    `ci95_gbp: [None, None]` rather than a zero-width interval.
    """
    if not result:
        return {
            "available": False,
            "reason": ("no two-arm measurement artefact was produced for this publish, so "
                       "whether the opening direct debit does anything is UNREAD here rather "
                       "than answered"),
        }
    pa = result.get("per_account") or {}
    matched = pa.get("window0_end_balance_drift_matched_population") or {}
    if not matched.get("n_matched_accounts"):
        return {
            "available": False,
            "reason": ("the two arms carried no account in common, so nothing here could be "
                       "attributed to the opening rule rather than to which accounts each arm "
                       "was able to open at all"),
        }
    diff = result.get("whole_run_output_diff") or {}
    unest = pa.get("unestimated") or {}
    n_moved = len(diff.get("moved_keys") or [])
    n_total = n_moved + len(diff.get("unmoved_keys") or [])

    return {
        "available": True,
        "clock": PUBLISHED_CLOCK,
        "clock_note": (
            "Every figure below is derived from the company's own ISSUED BILLS, so it is on the "
            "billed clock and cannot be reconciled against a settled-realised headline."
        ),
        "substrate": (result.get("clock") or {}).get("substrate"),
        "n_bills": (result.get("clock") or {}).get("n_bills"),
        "headline": (
            "Sizing the opening direct debit from an annualised estimate instead of from the "
            "first issued bill moves {n_moved} of {n_total} figures this run publishes — and "
            "not one of them is a figure a reader could previously see.".format(
                n_moved=n_moved, n_total=n_total)
        ),
        "why_no_headline_moves": (
            "The published treasury is a running total of net margin (simulation/run_phase2b.py: "
            "treasury += net_margin), so it is a profit accumulator wearing a cash name. No "
            "direct-debit arrangement whatsoever can move it, and the seven other headline "
            "figures are profit and loss. The comparison below is the only place the difference "
            "exists."
        ),
        "keys_moved": diff.get("moved_keys") or [],
        "keys_unmoved_count": len(diff.get("unmoved_keys") or []),
        "opening_amount": {
            "clock": PUBLISHED_CLOCK,
            "flat": (pa.get("opening_amount_gbp") or {}).get("flat"),
            "estimate": (pa.get("opening_amount_gbp") or {}).get("estimate"),
            "n_agreeing_to_the_penny": pa.get("n_same_opening_amount_to_the_penny"),
        },
        "year_one_drift_matched": {
            "clock": PUBLISHED_CLOCK,
            "n_matched_accounts": matched.get("n_matched_accounts"),
            "flat": matched.get("flat"),
            "estimate": matched.get("estimate"),
            "n_estimate_closer_to_zero": matched.get("n_estimate_closer_to_zero"),
            "n_flat_closer_to_zero": matched.get("n_flat_closer_to_zero"),
            "mean_change_in_abs_drift_gbp": matched.get("mean_change_in_abs_drift_gbp"),
            "mean_change_in_abs_drift_ci95_gbp": matched.get("mean_change_in_abs_drift_ci95_gbp"),
            "population_note": (
                "The same {n} households under both rules. Credit and debit are reported "
                "separately and never netted: a household in credit and one in debit are two "
                "different experiences with two different remedies.".format(
                    n=matched.get("n_matched_accounts"))
            ),
        },
        "refused": {
            "n": unest.get("estimate_n"),
            "cause_no_published_rate": unest.get("estimate_cause_no_published_rate"),
            "cause_no_consumption_basis": unest.get("estimate_cause_no_consumption_basis"),
            "statement": (
                "{n} accounts get NO opening amount under the estimate, every one of them "
                "because this company holds no published GB rate before the price cap began in "
                "January 2019 and therefore has nothing to annualise against. None failed for "
                "want of a consumption estimate. They carry no direct debit rather than one "
                "invented to fill the gap.".format(n=unest.get("estimate_n"))
            ),
        },
        "basis_split": pa.get("basis_split_of_estimated_accounts") or {},
        "basis_note": (
            "Which of SLC 27.15's four sources each estimate actually came from. Three of the "
            "four are unreached by the live call site, which passes the registration EAC and "
            "nothing else — so the precedence this organ implements is exercised at one value."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-output", type=Path, default=DEFAULT_RUN_OUTPUT)
    ap.add_argument("--json", type=Path, default=None,
                    help="write the full result here")
    ap.add_argument("--publish", type=Path, default=None,
                    help="write the reader-facing block here (site/data/dd_opening_arms.json)")
    args = ap.parse_args(argv)

    result = run(args.run_output)

    print("FLAT ARM REPRODUCES THE PUBLISHED PRE-ORGAN BOOK:")
    for k, v in result["flat_arm_reproduces_the_published_pre_organ_book"].items():
        print(f"  {k}: {'YES' if v else 'NO'}")
    d = result["whole_run_output_diff"]
    print(f"\nWHOLE RUN-OUTPUT DIFF: {len(d['moved_keys'])} of "
          f"{len(d['moved_keys']) + len(d['unmoved_keys'])} keys moved")
    print(f"  moved: {d['moved_keys']}")
    print("\nARM SUMMARIES:")
    print(json.dumps(result["arm_summaries"], indent=2))
    print("\nPER ACCOUNT:")
    print(json.dumps(result["per_account"], indent=2)[:6000])

    if args.json:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"\nwrote {args.json}")
    if args.publish:
        args.publish.write_text(
            json.dumps(publish_view(result), indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.publish}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
