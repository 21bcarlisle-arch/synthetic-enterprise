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
trigger is the latest one that can still meet the year. Standing policy turns it on (2026-10-21).

WHAT A VISIT COSTS (2026-10-21, §2.9). `read_visit_cost_schedule` charges each instruction in the
month its visit fell in, whether the visit read or not; `accounting_close` posts it to account 6100.
Which visit a supplier sends, a round or an appointment, is a GAP, so the upper bound is published
beside the central figure by `read_duty_summary`.

Each row says whether the step was taken (`step_taken`), and the summary counts the years that
passed without one (`rows_without_step`). A row WITH the step is a visit that found no read, which
the duty of effort allows; one without it is the duty not met (2026-10-26, SEAT_FINDING_A_THIRD_OF_
HOUSEHOLDS_GO_MORE_THAN_A_YEAR_ON_ESTIMATES_WITHOUT_THE_READ_DUTY_FIRING).

A row on a prepayment bill is kept, marked `duty_applies` False, and left out of the duty's count.
That is the licence's test on both fuels. The instruction is the code's on gas too: a gas prepayment
account is instructed although its row is not 21B.4's (2026-10-22, M5.9.14).
"""

from __future__ import annotations

from collections.abc import Iterable

__all__ = ["READ_DUTY_YEAR_BILLS", "READ_INSTRUCTION_AT_ESTIMATES",
           "READ_VISIT_PRICE_GBP_PER_VISIT", "READ_VISIT_PRICE_UPPER_GBP_PER_VISIT",
           "read_duty_register", "read_duty_summary", "read_instruction_due",
           "read_instruction_register", "read_visit_cost_schedule"]

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

#: What one instructed visit costs: a routine read on an area-based round, £3 per meter, from meter
#: operators to DECC, pre-2015 (Ofgem 2015 inspection consultation §1.170-1.172,
#: docs/market_research/read_access_and_theft_duties.md s.2.1). The central figure because the
#: instruction targets an unread meter, not one flagged high-risk (s.2.9). SIMPLIFIED: nominal 2015
#: prices for every year; to do it properly needs a dated series of meter-reading contract prices.
READ_VISIT_PRICE_GBP_PER_VISIT = 3.0
#: The stated upper bound: a scheduled-appointment visit to a high-risk meter, £17.50 per site, same
#: source (docs/market_research/read_access_and_theft_duties.md s.2.1). Which of the two a supplier
#: sends at the 11th estimate is the s.2.6/s.2.9 GAP, so it is published, never charged.
READ_VISIT_PRICE_UPPER_GBP_PER_VISIT = 17.5


def read_instruction_due(estimates_in_a_row: int, payment_channel: str | None, *, fuel: str) -> bool:
    """Whether the bill just billed, the `estimates_in_a_row`-th estimate since the last read, raises
    a read instruction for the next period. Once in each year of a run (the 11th, 23rd, 35th ...).
    Never on electricity prepayment, which 21B.3 excludes; on gas prepayment it is raised, because
    UNC TPD M5.9.14 applies the M5.9.9 annual read to prepayment meters (unbilled_energy_and_revenue_
    assurance.md K2). `fuel` is the bill's `commodity`."""
    exempt = fuel != "gas" and payment_channel in _OUTSIDE_THE_DUTY
    return (not exempt and estimates_in_a_row > 0
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
            # The instruction raised on the 11th estimate is stamped on this, the visit's bill: a
            # 12th estimate is one the visit did not read. False is a year that passed with no step.
            "step_taken": bool(bill.get("read_instruction_raised")),
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
        # None on a bill from before 2026-10-21, which did not say whether a visit went out.
        "visit_sent": bill.get("read_instruction_visit_sent"),
    } for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"]))
        if bill.get("read_instruction_raised")]


def read_visit_cost_schedule(bills: Iterable[dict],
                             price_gbp: float = READ_VISIT_PRICE_GBP_PER_VISIT) -> list[dict]:
    """Each instructed visit's cost, by the month its visit period ended: `[{month, amount_gbp}]`,
    sorted, the shape `accounting_close` posts. A visit that found no access is charged too: the
    round was run. An instruction whose ordinary read came in first sent no visit and costs nothing.
    Empty when the billing run instructed nothing."""
    by_month: dict[str, int] = {}
    for row in read_instruction_register(bills):
        if not row["visit_sent"]:
            continue
        month = row["visit_period_end"][:7]
        by_month[month] = by_month.get(month, 0) + 1
    return [{"month": month, "amount_gbp": round(by_month[month] * price_gbp, 2)}
            for month in sorted(by_month)]


def read_duty_summary(bills: Iterable[dict]) -> dict:
    """The register's counts per fuel over the whole run: rows and accounts where the duty applies,
    and the prepayment rows kept beside them. Unlike K2's snapshot, which asks of the accounts on
    supply in one month whether the last 12 bills held a read, this counts every year that passed."""
    bills = list(bills)
    by_fuel: dict[str, dict] = {}
    accounts: dict[str, set[str]] = {}
    for row in read_duty_register(bills):
        fuel = by_fuel.setdefault(row["fuel"], {
            "rows": 0, "accounts": 0, "prepayment_rows": 0, "rows_without_step": 0})
        if row["duty_applies"]:
            fuel["rows"] += 1
            fuel["rows_without_step"] += not row["step_taken"]
            accounts.setdefault(row["fuel"], set()).add(row["account_id"])
        else:
            fuel["prepayment_rows"] += 1
    for fuel, ids in accounts.items():
        by_fuel[fuel]["accounts"] = len(ids)
    instructions = read_instruction_register(bills)
    if any(row["visit_sent"] is None for row in instructions):
        visit_cost = {"instructions": len(instructions), "visits": None, "reason": (
            "these bills predate 2026-10-21 and do not say which instructions sent a visit; an "
            "instruction whose ordinary read came in first sent none")}
    else:
        visits = sum(1 for row in instructions if row["visit_sent"])
        visit_cost = {
            "instructions": len(instructions), "visits": visits,
            "charged_gbp": round(visits * READ_VISIT_PRICE_GBP_PER_VISIT, 2),
            "upper_bound_gbp": round(visits * READ_VISIT_PRICE_UPPER_GBP_PER_VISIT, 2),
            # Published so the page prints the prices the figures were charged at, not its own copy.
            "price_gbp_per_visit": READ_VISIT_PRICE_GBP_PER_VISIT,
            "upper_price_gbp_per_visit": READ_VISIT_PRICE_UPPER_GBP_PER_VISIT,
            "basis": "an area round per visit, charged; an appointment per visit, the bound "
                     "(read_access_and_theft_duties.md s.2.9: which a supplier sends is a GAP)"}
    return {"year_bills": READ_DUTY_YEAR_BILLS, "by_fuel": by_fuel, "visit_cost": visit_cost}
