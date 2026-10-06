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
True unbilled revenue (used and not yet billed) is still not computed. K4-K7 cannot arise in the
run yet (note §5).

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

from collections.abc import Iterable

__all__ = [
    "KINDS", "NO_READ_BILL_RUN", "PUBLISHED_MEDIAN_SUPPLIER_SHARE_NO_READ_BILL_IN_12",
    "account_billing_accuracy", "billing_accuracy_summary", "direct_debit_money_line",
    "estimated_billing_outstanding_grade", "published_view",
]

#: The kinds this module measures, keyed to the knowledge note's ids.
KINDS = {
    "K1": "billed on estimate and not yet trued up at a month end, graded by the later read",
    "K2": "estimated bills and their true-up at the actual read",
    "K3": "energy barred by the 12-month back-billing limit (SLC 21BA)",
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
    """One row per account, in first-seen order, built from that account's bills in period order."""
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


def billing_accuracy_summary(bills: Iterable[dict], direct_debit: dict | None = None) -> dict:
    """The per-account rows plus a total per fuel and kind. A share whose denominator is zero is
    None: no estimates billed or no undercharge to bar says nothing about accuracy.

    `direct_debit` is `direct_debit_money_line`'s output, carried beside the kinds and never mixed
    into `by_fuel`. None publishes as its named absence."""
    bills = list(bills)
    rows = account_billing_accuracy(bills)
    # The snapshot is the last billed month. The accounts in it are the ones still on supply at
    # the end; a leaver's last bill is on a forced final read, so including leavers would
    # flatter the share.
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
    return {
        "kinds": dict(KINDS), "snapshot_month": snapshot, "by_fuel": by_fuel, "accounts": rows,
        "direct_debit_money_line": direct_debit or direct_debit_money_line(None),
        # Per fuel, so a share never adds a kWh of gas to a kWh of electricity.
        "K1_year_end_grades": {
            fuel: [estimated_billing_outstanding_grade(fuel_bills, month)
                   for month in sorted({b["period_end"][:7] for b in fuel_bills
                                        if b["period_end"][5:7] == "12"})]
            for fuel, fuel_bills in _bills_by_fuel(bills).items()
        },
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


def published_view(summary: dict | None, source: str | None = None) -> dict:
    """What a reader of the site meets: the per-fuel figures with their denominators, the K2
    snapshot with a 95% interval set beside the published median supplier, the K1 year-end grades,
    and one named account. A summary that is missing or empty is published as an absence with its
    reason, never as zeros."""
    if not summary or not summary.get("by_fuel"):
        return {"available": False, "source": source, "reason": (
            "the run output this publish read carries no billing-accuracy measure, so there is "
            "nothing to show; it was added to the run output on 2026-10-06 and appears at the "
            "next run")}
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
                {k: g[k] for k in ("as_of", "outstanding_gbp", "outstanding_bills", "graded_runs",
                                   "never_read_runs", "graded_net_true_up_share",
                                   "graded_gross_true_up_share")}
                for g in summary.get("K1_year_end_grades", {}).get(fuel, [])
            ],
        }
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


def estimated_billing_outstanding_grade(bills: Iterable[dict], as_of: str | None = None) -> dict:
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
    """
    bills = list(bills)
    if as_of is None:
        as_of = max((b["period_end"][:7] for b in bills), default=None)
    by_account: dict[str, list[dict]] = {}
    for bill in bills:
        if bill["period_end"][:7] <= (as_of or ""):
            by_account.setdefault(bill["customer_id"], []).append(bill)
    later: dict[str, list[dict]] = {}
    for bill in bills:
        if bill["period_end"][:7] > (as_of or ""):
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
    grade["outstanding_gbp"] = grade["open_gbp"]
    grade["outstanding_bills"] = grade["open_bills"]
    billed = grade["graded_run_billed_kwh"]
    grade["graded_net_true_up_share"] = grade["graded_run_true_up_kwh"] / billed if billed else None
    grade["graded_gross_true_up_share"] = (
        grade["graded_run_abs_true_up_kwh"] / billed if billed else None)
    return grade
