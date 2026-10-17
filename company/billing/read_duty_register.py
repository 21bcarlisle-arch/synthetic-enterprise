"""The SLC 21B.4 register: each time an account's estimates reach a year without an actual read.

SLC 21B.4 is a duty of effort: "take all reasonable steps to obtain a meter reading ... for each of
its Customers at least once every year", a customer's own read and a smart meter's transmitted read
included, prepayment excluded. The company keeps no record of any step it takes to get a read, so a
year without one is a year it cannot show the duty was met. This register is where that becomes
visible to the company: one dated row each time a run of estimated bills reaches
`READ_DUTY_YEAR_BILLS`, read from the bill's own `consecutive_estimated_count`.
docs/market_research/read_access_and_theft_duties.md §2.6.

WHAT IT DOES NOT DO. It records only. No bill, read or estimate changes, so a run with the register
and a run without it bill identically.

THE STEP BEFORE THE YEAR (2026-10-17, §2.8). `read_instruction_due` names the bill on which the
company instructs a read; `build_monthly_bills(instruct_reads=True)` raises it and asks the read feed
for the visit (`ReadArrivalFeed.instructed_read_for`). When a supplier first asks is a GAP, so the
trigger is the latest one that can still meet the year. The switch defaults off.

A row on a prepayment bill is kept, marked `duty_applies` False, and left out of the duty's count.
"""

from __future__ import annotations

from collections.abc import Iterable

__all__ = ["READ_DUTY_YEAR_BILLS", "READ_INSTRUCTION_AT_ESTIMATES", "read_duty_register",
           "read_duty_summary", "read_instruction_due", "read_instruction_register"]

#: The licence's year, in monthly bills. Monthly billing makes 12 bills the same as 12 months, as
#: `billing_accuracy.NO_READ_BILL_RUN` reads the Citizens Advice window. The 12th estimate in a row
#: means the next read is at least 13 months after the last one.
READ_DUTY_YEAR_BILLS = 12

_OUTSIDE_THE_DUTY = frozenset({"prepayment"})

#: The bill on which the company instructs a read: the 11th estimate in a row, so the visit falls on
#: the 12th bill since the last read, still inside the year. The last bill from which the step can
#: meet the year, so the latest compliant timing, not a chosen one: when a supplier first asks is a
#: GAP (read_access_and_theft_duties.md s.2.8).
READ_INSTRUCTION_AT_ESTIMATES = READ_DUTY_YEAR_BILLS - 1


def read_instruction_due(estimates_in_a_row: int, payment_channel: str | None) -> bool:
    """Whether the bill just billed, the `estimates_in_a_row`-th estimate since the last read, raises
    a read instruction for the next period. Once in each year of a run (the 11th, 23rd, 35th ...),
    and never on prepayment, which 21B.4 excludes."""
    return (payment_channel not in _OUTSIDE_THE_DUTY and estimates_in_a_row > 0
            and estimates_in_a_row % READ_DUTY_YEAR_BILLS == READ_INSTRUCTION_AT_ESTIMATES)


def read_duty_register(bills: Iterable[dict]) -> list[dict]:
    """One row per account per run of estimates that reaches a year, dated by that bill's period end.

    A run's count resets at an actual read, so a run of 30 estimates writes one row, at its 12th."""
    rows = []
    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        if (bill.get("billing_basis") != "estimated"
                or bill.get("consecutive_estimated_count") != READ_DUTY_YEAR_BILLS):
            continue
        channel = bill.get("payment_channel")
        rows.append({
            "account_id": bill["customer_id"],
            "fuel": bill.get("commodity", "electricity"),
            "date": bill["period_end"],
            "estimates_in_a_row": READ_DUTY_YEAR_BILLS,
            "payment_channel": channel,
            "duty_applies": channel not in _OUTSIDE_THE_DUTY,
        })
    return rows


def read_instruction_register(bills: Iterable[dict]) -> list[dict]:
    """The instructions the billing run raised (`build_monthly_bills(instruct_reads=True)`), one row
    each, dated the day it was raised, with the period the visit fell in and what came back."""
    return [{
        "account_id": bill["customer_id"],
        "fuel": bill.get("commodity", "electricity"),
        "raised": bill["read_instruction_raised"],
        "visit_period_end": bill["period_end"],
        "outcome": bill["read_instruction_outcome"],
    } for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"]))
        if bill.get("read_instruction_raised")]


def read_duty_summary(bills: Iterable[dict]) -> dict:
    """The register's counts per fuel over the whole run: rows and accounts where the duty applies,
    and the prepayment rows kept beside them. Unlike K2's snapshot, which asks of the accounts on
    supply in one month whether the last 12 bills held a read, this counts every year that passed."""
    by_fuel: dict[str, dict] = {}
    accounts: dict[str, set[str]] = {}
    for row in read_duty_register(bills):
        fuel = by_fuel.setdefault(row["fuel"], {
            "rows": 0, "accounts": 0, "prepayment_rows": 0})
        if row["duty_applies"]:
            fuel["rows"] += 1
            accounts.setdefault(row["fuel"], set()).add(row["account_id"])
        else:
            fuel["prepayment_rows"] += 1
    for fuel, ids in accounts.items():
        by_fuel[fuel]["accounts"] = len(ids)
    return {"year_bills": READ_DUTY_YEAR_BILLS, "by_fuel": by_fuel}
