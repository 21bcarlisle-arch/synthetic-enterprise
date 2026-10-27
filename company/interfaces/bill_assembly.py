"""Seam: the world asks the company to run its billing.

KNIFE pass 3, `A_composition_lift` step 11, 2026-08-10. Before this, the
simulated world assembled the supplier's bills itself, reaching directly into
`company/billing/back_billing.py`, `company/billing/account_adjustment_register.py`
and `saas/bill_generator.py` — three of `simulation/run_phase4c_on_phase2b.py`'s
thirteen wall crossings, and three modules whose internals a real supplier is
free to change without telling the world anything.

Now the world hands over settled records and its meter-read feed, and receives
bills. The back-billing cap, the write-off register and the bill generator are
unreachable from the SIM; what crosses is this one door.

WHY THE READ FEED GOES THE OTHER WAY. A supplier does not decide whether a meter
read arrives — it observes one. So the company cannot import the world's read
physics, and does not: `assemble_monthly_bills` takes a `ReadArrivalFeed` the
caller supplies (`simulation.meter_reads.SimulatedReadFeed` in the simulation, a
real D0010/DTC adapter at go-live). Moving the bill assembly with its
`simulation.meter_reads` imports intact would have traded three class-(b)
crossings for three class-(a) ones — the STRICTLY FORBIDDEN direction, which is
at zero and stays there. The inversion is the cut; the file move alone would
have been a laundering.

WHAT THIS UNBLOCKS, AND WHAT IT DOES NOT DO. `company/interfaces/collections_communication.py`
(B5) and `company/interfaces/dd_review_outcome.py` (B4) each recorded that they
could deliver a PULL and not the PUSH their design asks for, for one stated
structural reason: no company-side bill emitter existed to stamp an attribute
onto. It exists now. Neither push is built here — that is separate work, and
claiming it in this commit would be exactly the "shape of a push with the
substance of a pull" both modules refused.
"""

from __future__ import annotations

from company.billing.back_billing import barred_at_charge_recovery
from company.billing.billing_accuracy import (
    billing_accuracy_summary,
    direct_debit_money_line,
    move_out_final_bills,
)
from company.billing.monthly_bill_assembly import (
    ReadArrival,
    ReadArrivalFeed,
)
from company.billing.monthly_bill_assembly import (
    build_monthly_bills as assemble_monthly_bills,
)
from company.billing.pre_bill_validation import validate_bills
from company.regulatory.energy_bill_support import ebss_credit_gbp as _scheme_credit


def issued_bills(bills: list) -> list:
    """The bills the supplier actually sends: `bills` less those its pre-bill validation gate
    holds. A held bill never reaches the customer, so the world cannot pay or default on it --
    which is why the world's payment outcomes are drawn over this set, not over `bills`.
    """
    return validate_bills(bills)[0]


def held_bills(bills: list) -> set[tuple[str, str]]:
    """The (customer_id, period_end) of each bill the pre-bill gate holds: assembled, never sent."""
    return {(r.customer_id, r.period_end) for r in validate_bills(bills)[1]}


def billing_accuracy(bills: list, direct_debit: dict | None = None) -> dict:
    """D48: what the supplier billed against what its reads later showed, by kind, read from the
    bills this door returned and nothing the world holds back (`company/billing/billing_accuracy.py`).
    `direct_debit` is the DD money line, carried beside K3 and never folded into it. The bills
    the pre-bill gate held are named here, where issuance is decided, for the unbilled accrual.
    """
    return billing_accuracy_summary(bills, direct_debit, held_bills(bills))


def owed_after_scheme_credit(amount: float, segment: str, commodity: str, month: str,
                             held_from: str | None = None) -> float:
    """What the household owes for a leg-month once the supplier has applied the government's bill
    credit (EBSS, Oct 2022 to Mar 2023). Both of the world's amount paths ask this: the held month
    the household's budget weighs (`run_phase2b`) and the issued bill whose pounds can fail
    (`arrears_engine`). Asking one door is what keeps the two agreeing. May go negative: a credit
    larger than the month's charge leaves the account in credit, which nobody fails.
    """
    return round(amount - _scheme_credit(segment, commodity, month, held_from), 2)


def scheme_credit(segment: str, commodity: str, month: str, held_from: str | None = None) -> float:
    """The month's government bill credit for one account, for the world's occupier window, which
    nets it from a debt rather than from a bill (`run_phase2b`, the 2026-10-27 occupier finding).
    """
    return _scheme_credit(segment, commodity, month, held_from)


__all__ = [
    "ReadArrival", "ReadArrivalFeed", "assemble_monthly_bills", "barred_at_charge_recovery",
    "billing_accuracy", "direct_debit_money_line", "held_bills", "issued_bills",
    "move_out_final_bills", "owed_after_scheme_credit", "scheme_credit",
]
