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

Kinds K1 and K4-K7 are not measured here. K1 (the accrual) is graded against these true-ups in a
later slice. K4-K7 cannot arise in the run yet (note §5).
"""

from __future__ import annotations

from collections.abc import Iterable

__all__ = ["KINDS", "NO_READ_BILL_RUN", "account_billing_accuracy", "billing_accuracy_summary"]

#: The kinds this module measures, keyed to the knowledge note's ids.
KINDS = {
    "K2": "estimated bills and their true-up at the actual read",
    "K3": "energy barred by the 12-month back-billing limit (SLC 21BA)",
}

#: Twelve consecutive bills with none on an actual read. This is the Citizens Advice
#: traditional-meter billing-accuracy window (note §2 K2): a bill on a read in the last 12 months.
#: Monthly billing makes 12 bills the same as 12 months.
NO_READ_BILL_RUN = 12


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


def billing_accuracy_summary(bills: Iterable[dict]) -> dict:
    """The per-account rows plus a total per fuel and kind. A share whose denominator is zero is
    None: no estimates billed or no undercharge to bar says nothing about accuracy."""
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
    return {"kinds": dict(KINDS), "snapshot_month": snapshot, "by_fuel": by_fuel, "accounts": rows}
