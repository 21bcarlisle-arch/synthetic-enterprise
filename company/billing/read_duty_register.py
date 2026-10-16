"""The SLC 21B.4 register: each time an account's estimates reach a year without an actual read.

SLC 21B.4 is a duty of effort: "take all reasonable steps to obtain a meter reading ... for each of
its Customers at least once every year", a customer's own read and a smart meter's transmitted read
included, prepayment excluded. The company keeps no record of any step it takes to get a read, so a
year without one is a year it cannot show the duty was met. This register is where that becomes
visible to the company: one dated row each time a run of estimated bills reaches
`READ_DUTY_YEAR_BILLS`, read from the bill's own `consecutive_estimated_count`.
docs/market_research/read_access_and_theft_duties.md §2.6.

WHAT IT DOES NOT DO. It records only. No bill, read or estimate changes, so a run with the register
and a run without it bill identically. What should come before the year, when a supplier first asks
for a read and by what means, is a GAP the knowledge page names; it waits for the world to answer a
request, which today it cannot.

A row on a prepayment bill is kept, marked `duty_applies` False, and left out of the duty's count.
"""

from __future__ import annotations

from collections.abc import Iterable

__all__ = ["READ_DUTY_YEAR_BILLS", "read_duty_register", "read_duty_summary"]

#: The licence's year, in monthly bills. Monthly billing makes 12 bills the same as 12 months, as
#: `billing_accuracy.NO_READ_BILL_RUN` reads the Citizens Advice window. The 12th estimate in a row
#: means the next read is at least 13 months after the last one.
READ_DUTY_YEAR_BILLS = 12

_OUTSIDE_THE_DUTY = frozenset({"prepayment"})


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
