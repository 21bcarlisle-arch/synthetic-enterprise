"""Billing accuracy: what the supplier billed against what its reads later showed, by kind.

D48 slice 1 (canon step 2, company half). The kinds are the knowledge note's
(`docs/market_research/unbilled_energy_and_revenue_assurance.md` §1-§2). This slice measures the
two the run can produce today:

- **K2, estimated bills and their true-up.** kWh billed on estimates, and the true-up when an
  actual read ends the run: the register advance less what the estimates billed. Positive is an
  undercharge.
- **K3, the 12-month back-billing limit.** The part of an undercharge true-up the SLC 21BA cap
  bars, apportioned by days as the money cap is (`BackBillingAssessment.barred_fraction`).

Also the Citizens Advice accuracy measure the note cites for K2. It is a SNAPSHOT: of the
accounts on supply at a date, the share with no bill on an actual read in the last 12 months.
It is not "ever went 12 bills without a read". Over a five-year window that second quantity
compounds to about four times the snapshot: 26 of 129 accounts against 3 of 60 on supply at the
end, on the first real run (2016-2020, 2026-10-05).
The longest run is kept per account as a diagnostic, and only the snapshot is set beside the
published figure.

WHAT IT READS. The supplier's own bills and nothing else: each bill's `billing_basis`, its
`total_consumption_kwh` (what that bill charged for), and the `read_true_up_*` fields
`monthly_bill_assembly._resolve_catchup` stamps when an actual read arrives. It does NOT read
`true_consumption_kwh`, which an estimated bill also carries for divergence analytics. That is the
world's use in a month the supplier only estimated. A supplier learns the run total at the read,
not the month-by-month truth, and this module is held to the same limit. The control is
`test_world_truth_on_an_estimated_bill_does_not_move_the_measure`.

An estimated run that has not yet met a read is reported as `open_estimated_kwh`. Its true-up is
not known, so it is not guessed.

K1 (slice 2) is graded, not measured afresh. What the ledger carries for it is
`saas.ledger.estimated_billing_outstanding`: the whole value of every estimated bill no read has
yet ended. `estimated_billing_outstanding_grade` reads that position at a month end and grades
each open run by what its next actual read showed. Beside it, `closed_immaterial` counts the
estimates a read closed with a correction too small to bill. Until 2026-10-05 the ledger kept
those as outstanding, because it keyed only on `catchup_applied`, which only a material
correction sets: 83% of the decade run's figure.
UNBILLED ENERGY (K1 proper, 2026-10-20) is `unbilled_accrual`: per account at a month end, the
company's own figure for each period (the actual read, or the estimate already on the bill: its last
reads shaped by the profile, else the registry EAC/AQ or TDCV, `unread_month_estimate.py`) less what
it ISSUED. Every account is billed each calendar month to the month end, so in this run that is
exactly the bills the pre-bill gate held. A held estimate is unbilled until an actual read ends its
run, the rule `saas.ledger.open_estimated_bills` states once for both figures; a held actual-read
bill, with any catch-up it carried, is never billed. It is not re-estimated with a second
estimator: the gap between two of the company's estimators is not energy used and not billed.
Billed-on-estimate (above) and unbilled are Centrica's two halves of "unread revenue"; they count
different bills and are never summed here. K4-K7 cannot arise in the run yet (note §5).

THE DIRECT-DEBIT MONEY LINE sits beside K3 and is never added to it. For a direct-debit account the
statement is not a demand, so no kWh is barred at a catch-up and K3 is pay-on-bill energy only.
What SLC 21BA bars there is money: at a charge recovery action (the final bill of an account that
left; the annual review only under the review toggle), the part of the balance it seeks that pays
for energy used more than 12 months earlier, the debit's collections paying the oldest charges
first. The figures come from the supplier's own DD balance book
(`simulation/dd_balance_book.back_billing_accounts`: its bills and the debits it set), are in £ gross
of VAT, and are bounded over the accounts that met an action. An open account's figure is an
exposure, not a loss, and is shown apart. The control that it stays apart is
`test_the_dd_money_line_is_never_folded_into_k3`.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable

from company.billing.pre_bill_validation import issued_with_final_bill
from company.billing.read_duty_register import read_duty_summary
from saas.ledger import open_estimated_bills

__all__ = [
    "KINDS", "NO_READ_BILL_RUN", "PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12",
    "account_billing_accuracy", "billing_accuracy_summary", "dd_review_arms", "direct_debit_money_line",
    "estimated_billing_outstanding_grade", "published_view", "unbilled_accrual",
]

#: The kinds this module measures, keyed to the knowledge note's ids.
KINDS = {
    "K1": "billed on estimate and not yet trued up at a month end, graded by the later read",
    "K2": "estimated bills and their true-up at the actual read",
    "K3": "energy barred by the 12-month back-billing limit (SLC 21BA)",
    "K1_unbilled": "energy the company counts as used and has not issued a bill for, at a month end",
}

#: Twelve consecutive bills with none on an actual read. This is the Citizens Advice
#: traditional-meter billing-accuracy window (note §2 K2): a bill on a read in the last 12 months.
#: Monthly billing makes 12 bills the same as 12 months.
NO_READ_BILL_RUN = 12

#: The published K2 comparator (note §2 K2). Ofgem, *Decision: Protecting consumers from
#: backbills*, 5 March 2018, p.10, citing Citizens Advice: at the median supplier with over 5,000
#: accounts, 94.80% (2017 Q1) and 94.40% (Q2) of consumers had a bill reflecting a meter reading in
#: the past year. Held as the share WITHOUT one, the quantity the snapshot measures.
PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12 = (1 - 0.9480, 1 - 0.9440)

_Z95 = 1.959964


def account_billing_accuracy(bills: Iterable[dict]) -> list[dict]:
    """One row per account, in first-seen order, built from that account's bills in period order.
    Pass issued bills: a bill the pre-bill gate held reached nobody, so it was never billed."""
    by_account: dict[str, list[dict]] = {}
    for bill in bills:
        by_account.setdefault(bill["customer_id"], []).append(bill)

    rows = []
    for account_id, account_bills in by_account.items():
        account_bills = sorted(account_bills, key=lambda b: b["period_end"])
        row = {
            "account_id": account_id,
            "fuel": account_bills[0].get("commodity", "electricity"),
            "bills": len(account_bills),
            "billed_kwh": 0.0,
            "estimated_bills": 0,
            "estimated_kwh": 0.0,
            "true_ups": 0,
            "true_up_kwh": 0.0,
            "undercharge_kwh": 0.0,
            "overcharge_kwh": 0.0,
            "barred_kwh": 0.0,
            "barred_true_ups": 0,
            "open_estimated_kwh": 0.0,
            "longest_run_without_read_bill": 0,
        }
        open_run_kwh = 0.0
        run_without_read = 0
        for bill in account_bills:
            kwh = bill["total_consumption_kwh"]
            row["billed_kwh"] += kwh
            if bill["billing_basis"] == "estimated":
                row["estimated_bills"] += 1
                row["estimated_kwh"] += kwh
                open_run_kwh += kwh
                run_without_read += 1
                row["longest_run_without_read_bill"] = max(
                    row["longest_run_without_read_bill"], run_without_read
                )
                continue
            run_without_read = 0
            open_run_kwh = 0.0
            true_up = bill.get("read_true_up_kwh")
            if true_up is None:
                continue
            row["true_ups"] += 1
            row["true_up_kwh"] += true_up
            if true_up > 0:
                row["undercharge_kwh"] += true_up
            else:
                row["overcharge_kwh"] -= true_up
            barred = bill.get("read_true_up_barred_kwh") or 0.0
            if barred > 0:
                row["barred_kwh"] += barred
                row["barred_true_ups"] += 1
        row["open_estimated_kwh"] = open_run_kwh
        row["last_period_end"] = account_bills[-1]["period_end"]
        # At the account's last bill: None when it has fewer than 12 bills, as the window
        # cannot answer.
        row["no_read_bill_in_last_12"] = (
            None if len(account_bills) < NO_READ_BILL_RUN
            else run_without_read >= NO_READ_BILL_RUN
        )
        rows.append(row)
    return rows


def direct_debit_money_line(accounts: list[dict] | None, *, unmeasured_accounts: int = 0,
                            seek_balance_at_review: bool = False) -> dict:
    """The DD back-billing bar over the DD balance book's per-account rows, with its sample bound.

    The population for the share and the mean is the accounts that met a charge recovery action:
    only those could lose anything. The share barred carries a Wilson 95% interval; the mean bar per
    such account a normal-approximation 95% interval, which is rough at this size and says so.
    `accounts` None is an absence (the run output predates the line), never a zero."""
    if accounts is None:
        return {"available": False, "reason": (
            "the run output carries no per-account direct-debit back-billing rows; they were added "
            "on 2026-10-06 and appear at the next run")}
    met = [a for a in accounts if a["met_recovery_action"]]
    barred = [a["barred_gbp"] for a in met]
    n = len(barred)
    hits = sum(1 for b in barred if b > 0)
    mean = sum(barred) / n if n else None
    mean_ci = None
    if n > 1:
        sd = (sum((b - mean) ** 2 for b in barred) / (n - 1)) ** 0.5
        half = _Z95 * sd / n ** 0.5
        mean_ci = [max(0.0, mean - half), mean + half]
    return {
        "available": True,
        "unit": "gbp_gross_of_vat",
        "seek_balance_at_review": seek_balance_at_review,
        "dd_accounts": len(accounts),
        "unmeasured_accounts": unmeasured_accounts,
        "accounts_met_recovery_action": n,
        "accounts_barred": hits,
        "barred_gbp": round(sum(barred), 2),
        "share_barred": hits / n if n else None,
        "share_barred_ci95": _wilson(hits, n),
        "mean_barred_gbp": mean,
        "mean_barred_gbp_ci95": mean_ci,
        "mean_ci_method": "normal_approximation",
        "open_accounts": sum(1 for a in accounts if not a["closed"]),
        "open_exposure_gbp": round(sum(a["exposure_gbp"] for a in accounts
                                       if not a["closed"]), 2),
    }


def _nearest_rank(sorted_values: list[float], q: float) -> float:
    return sorted_values[max(0, math.ceil(len(sorted_values) * q) - 1)]


def dd_review_arms(arms: dict[str, dict] | None) -> dict:
    """The money line on both arms of the review toggle, with what each arm leaves open and, by
    year, what it bars and the step-up it puts on a household's debit.

    `arms` maps "never_seeks" and "seeks" to one DD balance book each, over the same bills:
    `{accounts, bar_actions, review_step_ups}`, the book's own rows. Seeking the balance asks more
    accounts, so its barred SHARE can rise while the money lost falls; the reader is shown the share,
    the open exposure and their sum together, or the share alone reads the wrong way
    (D48, 2026-10-16). A step-up is the monthly amount a review added to recover a debit balance,
    over the reviews that found one. None is an absence, never a zero."""
    if arms is None:
        return {"available": False, "reason": (
            "the publish could not rebuild the direct-debit book on both arms of the review "
            "toggle: the run output carries no bills or no opening debits")}
    out: dict = {"available": True, "unit": "gbp_gross_of_vat", "arms": {}, "by_year": []}
    years: dict[str, dict] = {}
    for name in ("never_seeks", "seeks"):
        book = arms[name]
        line = direct_debit_money_line(book["accounts"], seek_balance_at_review=name == "seeks")
        line["barred_plus_open_exposure_gbp"] = round(line["barred_gbp"]
                                                      + line["open_exposure_gbp"], 2)
        out["arms"][name] = line
        for action in book["bar_actions"]:
            row = years.setdefault(action["date"][:4], {})
            arm = row.setdefault(name, {"barred_gbp": 0.0, "accounts": set()})
            arm["barred_gbp"] += action["amount_gbp"]
            arm["accounts"].add(action["customer_id"])
        if name == "seeks":
            for step in book["review_step_ups"]:
                if step["step_up_gbp"] > 0:
                    years.setdefault(step["date"][:4], {}).setdefault(
                        "step_ups", []).append(step["step_up_gbp"])
    for year in sorted(years):
        row = years[year]
        steps = sorted(row.get("step_ups", []))
        out["by_year"].append({
            "year": year,
            **{f"{name}_barred_gbp": round(row[name]["barred_gbp"], 2) if name in row else 0.0
               for name in ("never_seeks", "seeks")},
            **{f"{name}_accounts_barred": len(row[name]["accounts"]) if name in row else 0
               for name in ("never_seeks", "seeks")},
            "reviews_stepped_up": len(steps),
            "step_up_median_gbp": statistics.median(steps) if steps else None,
            "step_up_mean_gbp": sum(steps) / len(steps) if steps else None,
            "step_up_p90_gbp": _nearest_rank(steps, 0.9) if steps else None,
        })
    return out


def billing_accuracy_summary(bills: Iterable[dict], direct_debit: dict | None = None,
                             held: set[tuple[str, str]] | None = None) -> dict:
    """The per-account rows plus a total per fuel and kind. A share whose denominator is zero is
    None: no estimates billed or no undercharge to bar says nothing about accuracy.

    `direct_debit` is `direct_debit_money_line`'s output, carried beside the kinds and never mixed
    into `by_fuel`. None publishes as its named absence. `held` is the (customer_id, period_end)
    of every bill the pre-bill gate did not issue; None publishes the accrual as an absence.
    Everything but the accrual is read over the issued bills, so billed-on-estimate and unbilled
    never count the same bill."""
    bills = list(bills)
    issued = [b for b in bills if (b["customer_id"], b["period_end"]) not in (held or ())]
    rows = account_billing_accuracy(issued)
    # The snapshot is the last billed month. The accounts in it are the ones still on supply at
    # the end; a leaver's last bill asks for a closing read, which a smart meter in smart mode
    # always answers, so including leavers would flatter the share slightly.
    snapshot = max((row["last_period_end"][:7] for row in rows), default=None)
    by_fuel: dict[str, dict] = {}
    for row in rows:
        fuel = by_fuel.setdefault(row["fuel"], {
            "accounts": 0, "billed_kwh": 0.0, "estimated_kwh": 0.0, "true_ups": 0,
            "true_up_kwh": 0.0, "undercharge_kwh": 0.0, "overcharge_kwh": 0.0,
            "barred_kwh": 0.0, "barred_true_ups": 0, "open_estimated_kwh": 0.0,
            "snapshot_accounts": 0, "snapshot_no_read_bill_in_12": 0,
        })
        fuel["accounts"] += 1
        if row["last_period_end"][:7] == snapshot and row["no_read_bill_in_last_12"] is not None:
            fuel["snapshot_accounts"] += 1
            fuel["snapshot_no_read_bill_in_12"] += int(row["no_read_bill_in_last_12"])
        for key in ("billed_kwh", "estimated_kwh", "true_ups", "true_up_kwh", "undercharge_kwh",
                    "overcharge_kwh", "barred_kwh", "barred_true_ups", "open_estimated_kwh"):
            fuel[key] += row[key]
    for fuel in by_fuel.values():
        fuel["K2_estimated_share_of_billed_kwh"] = (
            fuel["estimated_kwh"] / fuel["billed_kwh"] if fuel["billed_kwh"] else None
        )
        fuel["K2_snapshot_share_no_read_bill_in_12"] = (
            fuel["snapshot_no_read_bill_in_12"] / fuel["snapshot_accounts"]
            if fuel["snapshot_accounts"] else None
        )
        fuel["K3_barred_share_of_undercharge_kwh"] = (
            fuel["barred_kwh"] / fuel["undercharge_kwh"] if fuel["undercharge_kwh"] else None
        )
    late = issued_with_final_bill(bills)
    return {
        "kinds": dict(KINDS), "snapshot_month": snapshot, "by_fuel": by_fuel, "accounts": rows,
        "direct_debit_money_line": direct_debit or direct_debit_money_line(None),
        # Per fuel, so a share never adds a kWh of gas to a kWh of electricity.
        "K1_year_end_grades": _k1_year_end_grades(issued, late),
        "K1_unbilled_accrual": _k1_unbilled_by_month_end(bills, held, late),
    }


def _k1_unbilled_by_month_end(bills: list[dict], held: set[tuple[str, str]] | None,
                              late: dict[tuple[str, str], str]) -> dict:
    """The accrual at every year end inside the run and at its last billed month."""
    if held is None:
        return {"available": False, "reason": (
            "the caller passed no held-bill set, so what was issued cannot be told from what was "
            "assembled")}
    last = max((b["period_end"][:7] for b in bills), default=None)
    months = sorted({b["period_end"][:7] for b in bills if b["period_end"][5:7] == "12"} | (
        {last} if last else set()))
    return {"available": True, "unit_kwh": "kwh", "unit_gbp": "gbp_net_of_vat",
            "month_ends": [unbilled_accrual(bills, held, month, late) for month in months]}


def unbilled_accrual(bills: Iterable[dict], held: set[tuple[str, str]],
                     as_of: str | None = None,
                     issued_late: dict[tuple[str, str], str] | None = None) -> dict:
    """Energy the company counts as used by the end of month `as_of` (YYYY-MM; default the last
    billed month) and has not issued a bill for, per fuel, in kWh and at the held bill's own price
    net of VAT.

    `held` is the (customer_id, period_end) of each bill the pre-bill gate did not issue. A held
    estimate is open while no read billed by `as_of` has ended its run (`open_estimated_bills`, the
    rule the billed-on-estimate figure uses). A held actual-read bill stays open: no catch-up covers
    a read period, and a catch-up the held bill carried went out with nobody, so its chargeable
    true-up is counted with it. `older_than_12_months_kwh` is the part a domestic catch-up could no
    longer recover (SLC 21BA); `closed_account_kwh` the part on accounts with no bill after `as_of`
    and none in the run's last month, which no later bill can carry.

    A held bill in a closed account's closing run goes out on the final bill
    (`pre_bill_validation.issued_with_final_bill`, or `issued_late` where the caller has it), so
    it is held at every month end before the final bill's month and issued from then.
    """
    bills = list(bills)
    if issued_late is None:
        issued_late = issued_with_final_bill(bills)
    last = max((b["period_end"][:7] for b in bills), default="")
    as_of = as_of or last
    held = set(held) | {key for key, final in issued_late.items() if final[:7] > as_of}
    window = [b for b in bills if b["period_end"][:7] <= as_of]
    held_now = [b for b in window if (b["customer_id"], b["period_end"]) in held]
    open_estimates = open_estimated_bills(
        [b for b in held_now if b["billing_basis"] == "estimated"]
        + [b for b in window if b["billing_basis"] != "estimated"])
    open_bills = open_estimates + [b for b in held_now if b["billing_basis"] != "estimated"]
    final_month = {}
    for b in bills:
        final_month[b["customer_id"]] = max(final_month.get(b["customer_id"], ""), b["period_end"][:7])
    year_before = f"{int(as_of[:4]) - 1}{as_of[4:]}" if as_of else ""

    # Every fuel billed by `as_of` gets a row: nothing held is a measured zero, not an absence.
    by_fuel: dict[str, dict] = {
        fuel: {"accounts": set(), "held_estimates": 0, "held_actuals": 0, "kwh": 0.0, "gbp": 0.0,
               "older_than_12_months_kwh": 0.0, "closed_account_kwh": 0.0}
        for fuel in {b.get("commodity", "electricity") for b in window}
    }
    for b in open_bills:
        fuel = by_fuel[b.get("commodity", "electricity")]
        kwh = b["total_consumption_kwh"]
        if b["billing_basis"] == "estimated":
            fuel["held_estimates"] += 1
        else:
            fuel["held_actuals"] += 1
            if b.get("catchup_applied"):
                kwh += (b.get("read_true_up_kwh") or 0.0) - (b.get("read_true_up_barred_kwh") or 0.0)
        fuel["accounts"].add(b["customer_id"])
        fuel["kwh"] += kwh
        fuel["gbp"] += b["total_amount_gbp"] - b.get("vat_gbp", 0.0)
        if b["period_end"][:7] < year_before:
            fuel["older_than_12_months_kwh"] += kwh
        if final_month[b["customer_id"]] <= as_of and final_month[b["customer_id"]] < last:
            fuel["closed_account_kwh"] += kwh
    for fuel in by_fuel.values():
        fuel["accounts"] = len(fuel["accounts"])
        for key in ("kwh", "gbp", "older_than_12_months_kwh", "closed_account_kwh"):
            fuel[key] = round(fuel[key], 2)
    return {"as_of": as_of, "by_fuel": by_fuel}


def _k1_year_end_grades(bills: list[dict], late: dict[tuple[str, str], str]) -> dict:
    return {
        fuel: [estimated_billing_outstanding_grade(fuel_bills, month, late)
               for month in sorted({b["period_end"][:7] for b in fuel_bills
                                    if b["period_end"][5:7] == "12"})]
        for fuel, fuel_bills in _bills_by_fuel(bills).items()
    }


def _wilson(hits: int, n: int) -> list[float] | None:
    if not n:
        return None
    p = hits / n
    centre = (p + _Z95 ** 2 / (2 * n)) / (1 + _Z95 ** 2 / n)
    half = _Z95 * (p * (1 - p) / n + _Z95 ** 2 / (4 * n * n)) ** 0.5 / (1 + _Z95 ** 2 / n)
    # Exact at the edges: in floating point 0 hits gives a lower bound of 1e-19, above the share.
    return [0.0 if hits == 0 else centre - half, 1.0 if hits == n else centre + half]


def _against_published(interval: list[float] | None) -> str:
    """Where the published median band sits relative to this book's 95% interval."""
    if interval is None:
        return "no_accounts"
    low, high = sorted(PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12)
    if interval[1] < low:
        return "fewer_unread_than_the_median_supplier"
    if interval[0] > high:
        return "more_unread_than_the_median_supplier"
    return "cannot_be_told_apart_from_the_median_supplier"


def published_view(summary: dict | None, source: str | None = None,
                   bills: list[dict] | None = None,
                   held: set[tuple[str, str]] | None = None) -> dict:
    """What a reader of the site meets: the per-fuel figures with their denominators, the K2
    snapshot with a 95% interval set beside the published median supplier, the K1 year-end grades,
    and one named account. A summary that is missing or empty is published as an absence with its
    reason, never as zeros.

    `bills`, when given, are the run's own bills: K1 is then graded from them by this code, so a
    run output that predates a grade field (the largest run's share) still publishes it. The SLC
    21B.4 register (`read_duty_register`) is read from the same bills, and is absent without them.
    With `held` (the bills the pre-bill gate did not issue) as well, the whole summary is rebuilt
    from them, so a run output that predates the accrual publishes it and counts no held bill as
    billed."""
    if not summary or not summary.get("by_fuel"):
        return {"available": False, "source": source, "reason": (
            "the run output this publish read carries no billing-accuracy measure, so there is "
            "nothing to show; it was added to the run output on 2026-10-06 and appears at the "
            "next run")}
    if bills and held is not None:
        summary = billing_accuracy_summary(bills, summary.get("direct_debit_money_line"), held)
    k1 = summary.get("K1_year_end_grades", {})
    if bills and held is None:
        k1 = _k1_year_end_grades(bills, issued_with_final_bill(bills))
    fuels = {}
    for fuel, f in sorted(summary["by_fuel"].items()):
        interval = _wilson(f["snapshot_no_read_bill_in_12"], f["snapshot_accounts"])
        fuels[fuel] = {
            "accounts": f["accounts"],
            "billed_kwh": f["billed_kwh"], "estimated_kwh": f["estimated_kwh"],
            "K2_estimated_share_of_billed_kwh": f["K2_estimated_share_of_billed_kwh"],
            "true_ups": f["true_ups"], "undercharge_kwh": f["undercharge_kwh"],
            "overcharge_kwh": f["overcharge_kwh"], "open_estimated_kwh": f["open_estimated_kwh"],
            "barred_kwh": f["barred_kwh"], "barred_true_ups": f["barred_true_ups"],
            "K3_barred_share_of_undercharge_kwh": f["K3_barred_share_of_undercharge_kwh"],
            "snapshot": {
                "accounts": f["snapshot_accounts"], "no_read_bill_in_12": f["snapshot_no_read_bill_in_12"],
                "share": f["K2_snapshot_share_no_read_bill_in_12"], "ci95": interval,
                "against_published": _against_published(interval),
            },
            "K1_year_end_grades": [
                {k: g.get(k) for k in ("as_of", "outstanding_gbp", "outstanding_bills", "graded_runs",
                                   "never_read_runs", "graded_net_true_up_share",
                                   "graded_gross_true_up_share", "graded_largest_run_account",
                                   "graded_largest_run_share_of_net",
                                   "graded_net_true_up_share_without_largest_run")}
                for g in k1.get(fuel, [])
            ],
        }
    # The SLC 21B.4 register, read from the run's own bills at publish time like K1, so the
    # published run carries it without a re-run.
    read_duty = (read_duty_summary(bills) if bills else {"available": False, "reason": (
        "the publish was handed no bills, and the register is read from them")})
    rows = summary.get("accounts") or []
    example = max(rows, key=lambda r: (r["barred_kwh"], abs(r["true_up_kwh"])), default=None)
    return {
        "available": True, "source": source, "kinds": summary["kinds"],
        "snapshot_month": summary["snapshot_month"],
        "published_median_supplier_share_no_read_bill_in_12":
            sorted(PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12),
        "by_fuel": fuels, "example_account": example,
        "direct_debit_money_line": summary.get("direct_debit_money_line")
        or direct_debit_money_line(None),
        "read_duty_register": read_duty,
        # Never added to the billed-on-estimate grades above: they count different bills.
        "K1_unbilled_accrual": summary.get("K1_unbilled_accrual") or {"available": False, "reason": (
            "the run output this publish read predates the accrual, and the publish was handed no "
            "held-bill set to compute it from")},
    }


def _bills_by_fuel(bills: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for bill in bills:
        out.setdefault(bill.get("commodity", "electricity"), []).append(bill)
    return out


def _covers(bill: dict, period_end: str) -> bool:
    return (bill.get("catchup_applied", False)
            and bill.get("catchup_period_start", "") <= period_end
            <= bill.get("catchup_period_end", ""))


def estimated_billing_outstanding_grade(bills: Iterable[dict], as_of: str | None = None,
                                        issued_late: dict[tuple[str, str], str] | None = None
                                        ) -> dict:
    """The ledger's billed-on-estimate position at the end of month `as_of` (YYYY-MM; default the
    last billed month), split by what had happened to each bill by then, and graded by what the
    later reads showed.

    The position (`outstanding`, which is `open`) is every estimated bill billed by `as_of` that
    no actual read billed by `as_of` has ended -- the rule `saas.ledger.estimated_billing_outstanding`
    applies to a whole bill set. Beside it, not in it:

    - `closed_immaterial`: estimates whose run an actual read billed by `as_of` ended with no
      material catch-up. The register advance is known and the correction was under the
      materiality threshold, so nothing rests on the estimate any more.

    An `open` bill has no read yet. Its run is graded by the next actual-read bill after `as_of`, which
      stamps the run's register true-up (`read_true_up_*`). The run there may include estimates
      billed after `as_of`, and its split by month is not known, so the grade is per run, not per
      bill: the run's true-up against the run's billed kWh. A run no read has yet ended is
      `never_read` and is not guessed.

    Money is the bills' `total_amount_gbp`, as the ledger counts it. Energy is billed kWh.

    A bill counts from the month it was ISSUED. A held interim released at an account's closing
    read goes out with the final bill (`pre_bill_validation.issued_with_final_bill`, or
    `issued_late` where the caller has it). Before that month it is the unbilled accrual's, so it
    is not billed on estimate here.
    """
    bills = list(bills)
    if issued_late is None:
        issued_late = issued_with_final_bill(bills)
    if as_of is None:
        as_of = max((b["period_end"][:7] for b in bills), default=None)

    def issued_month(bill: dict) -> str:
        return issued_late.get((bill["customer_id"], bill["period_end"]), bill["period_end"])[:7]

    by_account: dict[str, list[dict]] = {}
    for bill in bills:
        if issued_month(bill) <= (as_of or ""):
            by_account.setdefault(bill["customer_id"], []).append(bill)
    later: dict[str, list[dict]] = {}
    for bill in bills:
        if issued_month(bill) > (as_of or ""):
            later.setdefault(bill["customer_id"], []).append(bill)

    grade = {
        "as_of": as_of,
        "outstanding_gbp": 0.0, "outstanding_bills": 0,
        "closed_immaterial_gbp": 0.0, "closed_immaterial_bills": 0,
        "open_gbp": 0.0, "open_kwh": 0.0, "open_bills": 0, "open_runs": 0,
        "never_read_runs": 0, "never_read_kwh": 0.0,
        "graded_runs": 0, "graded_run_billed_kwh": 0.0,
        "graded_run_true_up_kwh": 0.0, "graded_run_abs_true_up_kwh": 0.0,
    }
    largest: tuple[float, str, float] | None = None  # (true-up kWh, account, its billed kWh)
    for account_id, account_bills in by_account.items():
        account_bills.sort(key=lambda b: b["period_end"])
        materials = [b for b in account_bills if b.get("catchup_applied")]
        open_run: list[dict] = []
        for bill in account_bills:
            if bill["billing_basis"] != "estimated":
                # A read ends the run. What it left uncovered was an immaterial correction.
                for est in open_run:
                    grade["closed_immaterial_gbp"] += est.get("total_amount_gbp", 0.0)
                    grade["closed_immaterial_bills"] += 1
                open_run = []
                continue
            if not any(_covers(m, bill["period_end"]) for m in materials):
                open_run.append(bill)
        if not open_run:
            continue
        grade["open_runs"] += 1
        grade["open_bills"] += len(open_run)
        grade["open_gbp"] += sum(b.get("total_amount_gbp", 0.0) for b in open_run)
        open_kwh = sum(b["total_consumption_kwh"] for b in open_run)
        grade["open_kwh"] += open_kwh
        closing = next(
            (b for b in sorted(later.get(account_id, []), key=lambda b: b["period_end"])
             if b["billing_basis"] != "estimated"), None)
        if closing is None or closing.get("read_true_up_kwh") is None:
            grade["never_read_runs"] += 1
            grade["never_read_kwh"] += open_kwh
            continue
        grade["graded_runs"] += 1
        grade["graded_run_billed_kwh"] += closing["read_true_up_billed_kwh"]
        grade["graded_run_true_up_kwh"] += closing["read_true_up_kwh"]
        grade["graded_run_abs_true_up_kwh"] += abs(closing["read_true_up_kwh"])
        if largest is None or abs(closing["read_true_up_kwh"]) > abs(largest[0]):
            largest = (closing["read_true_up_kwh"], account_id, closing["read_true_up_billed_kwh"])
    grade["outstanding_gbp"] = grade["open_gbp"]
    grade["outstanding_bills"] = grade["open_bills"]
    billed = grade["graded_run_billed_kwh"]
    grade["graded_net_true_up_share"] = grade["graded_run_true_up_kwh"] / billed if billed else None
    grade["graded_gross_true_up_share"] = (
        grade["graded_run_abs_true_up_kwh"] / billed if billed else None)
    # HOW CONCENTRATED THE NET IS. The grade pools kWh across runs, so one run can set it: on the
    # 2248e3baf run one unread EV home (C7, +41,778 kWh at one read) carried electricity's net at
    # +8% to +12% for fifty month ends, and was read as a population bias. Over 100% of the net
    # means the rest of the runs net the other way; the net without it is the population's.
    net = grade["graded_run_true_up_kwh"]
    grade["graded_largest_run_account"] = largest[1] if largest else None
    grade["graded_largest_run_true_up_kwh"] = largest[0] if largest else None
    grade["graded_largest_run_share_of_net"] = largest[0] / net if largest and net else None
    rest_billed = billed - largest[2] if largest else billed
    grade["graded_net_true_up_share_without_largest_run"] = (
        (net - largest[0]) / rest_billed if largest and rest_billed else None)
    return grade
