from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Optional

from company.compliance.working_days import add_working_days


class GSOPType(str, Enum):
    MISSED_APPOINTMENT = "missed_appointment"
    #: Reg 6ZB: the NEW supplier completed a transfer without a valid contract. The failure is the
    #: day the two suppliers agree it was erroneous (`SWITCHING_STANDARDS` below).
    ERRONEOUS_TRANSFER = "erroneous_transfer"
    #: Reg 6ZA: the NEW supplier did not complete the transfer in time (`switch_speed_deadline`).
    SWITCH_SPEED = "switch_speed"
    #: Reg 6C: the OLD supplier did not re-register an erroneously transferred customer within 21
    #: working days of the agreement.
    ERRONEOUS_TRANSFER_RETURN = "erroneous_transfer_return"
    WRONGFUL_DISCONNECT = "wrongful_disconnect"
    FINAL_BILL_DELAY = "final_bill_delay"
    REFUND_DELAY = "refund_delay"


# Statutory payment amounts (pence-equivalent in GBP) — Ofgem-set, approximate calendar year
_GSOP_AMOUNT_GBP: Dict[GSOPType, float] = {
    GSOPType.MISSED_APPOINTMENT: 30.0,
    GSOPType.ERRONEOUS_TRANSFER: 30.0,
    GSOPType.SWITCH_SPEED: 30.0,
    GSOPType.ERRONEOUS_TRANSFER_RETURN: 30.0,
    GSOPType.WRONGFUL_DISCONNECT: 30.0,   # per day, capped at 10 days
    GSOPType.FINAL_BILL_DELAY: 30.0,
    GSOPType.REFUND_DELAY: 30.0,
}

#: The standard payment a supplier guaranteed standard owes on a failure: £30 as set in 2015, £40
#: for failures from 2 January 2025. Ofgem, *Supplier Guaranteed Standards of Performance (GSoP)
#: payment uplift* (decision), https://ofgem.gov.uk/decision/supplier-guaranteed-standards-performance-gsop-payment-uplift,
#: and `docs/market_research/home_moves.md` s.8.8. `_GSOP_AMOUNT_GBP` above has not yet moved to it.
GSOP_STANDARD_PAYMENT_2015_GBP = 30.0
GSOP_STANDARD_PAYMENT_UPLIFT_GBP = 40.0
GSOP_STANDARD_PAYMENT_UPLIFT_FROM = date(2025, 1, 2)


def standard_payment_gbp(failed_on: date) -> float:
    """The standard payment in force on the day a guaranteed standard was failed."""
    if failed_on >= GSOP_STANDARD_PAYMENT_UPLIFT_FROM:
        return GSOP_STANDARD_PAYMENT_UPLIFT_GBP
    return GSOP_STANDARD_PAYMENT_2015_GBP


#: Reg 8(2) of S.I. 2015/1544: the standard payment is made "within 10 working days of the
#: supplier's initial failure", for every standard in regs 3 to 6D. Read 21 Nov 2026,
#: `docs/market_research/switching_mechanics_2026-10-25.md` s.6. The erroneous-transfer row was 20
#: until then: that is the reg 6A window for the suppliers to AGREE, not the payment window.
STANDARD_PAYMENT_WINDOW_WORKING_DAYS = 10

# Working days allowed before payment is due (from trigger date)
_GSOP_PAYMENT_DAYS: Dict[GSOPType, int] = {
    GSOPType.MISSED_APPOINTMENT: 10,
    GSOPType.ERRONEOUS_TRANSFER: STANDARD_PAYMENT_WINDOW_WORKING_DAYS,
    GSOPType.SWITCH_SPEED: STANDARD_PAYMENT_WINDOW_WORKING_DAYS,
    GSOPType.ERRONEOUS_TRANSFER_RETURN: STANDARD_PAYMENT_WINDOW_WORKING_DAYS,
    GSOPType.WRONGFUL_DISCONNECT: 2,
    GSOPType.FINAL_BILL_DELAY: 10,
    GSOPType.REFUND_DELAY: 10,
}


@dataclass(frozen=True)
class SwitchingStandard:
    """One switching guaranteed standard: its regulation, the day it came into force, and which
    side of the transfer owes the payment ("new" = gaining supplier, "old" = losing supplier)."""

    regulation: str
    in_force_from: date
    payer: str


#: The switching standards a supplier can owe, from S.I. 2019/218 (in force 1 May 2019) and S.I.
#: 2020/116 (in force 1 May 2020), read on legislation.gov.uk 21 Nov 2026:
#: `docs/market_research/switching_mechanics_2026-10-25.md` s.6. Before its in-force day a standard
#: did not exist, so nothing is owed for a failure on an earlier day.
SWITCHING_STANDARDS: Dict[GSOPType, SwitchingStandard] = {
    GSOPType.ERRONEOUS_TRANSFER: SwitchingStandard("6ZB", date(2020, 5, 1), "new"),
    GSOPType.SWITCH_SPEED: SwitchingStandard("6ZA", date(2020, 5, 1), "new"),
    GSOPType.ERRONEOUS_TRANSFER_RETURN: SwitchingStandard("6C", date(2019, 5, 1), "old"),
}

#: Reg 6ZA as made (S.I. 2020/116): 15 working days. As amended by S.I. 2024/108 from 1 April 2024:
#: 5 working days, 6 if the contract was made after 5pm on a working day, and (absent an early-start
#: request) the clock starts no earlier than the end of the 14 days beginning with the contract day.
#: `docs/market_research/switching_mechanics_2026-10-25.md` s.6.
SWITCH_SPEED_WORKING_DAYS_2020 = 15
SWITCH_SPEED_WORKING_DAYS_2024 = 5
SWITCH_SPEED_WORKING_DAYS_2024_AFTER_5PM = 6
SWITCH_SPEED_AMENDED_FROM = date(2024, 4, 1)
SWITCH_SPEED_COOLING_OFF_DAYS = 14

#: Reg 6C(3): the old supplier re-registers the customer "within 21 working days of the agreement".
ERRONEOUS_TRANSFER_RETURN_WORKING_DAYS = 21


def _period_end(first_day: date, working_days: int) -> date:
    """The last day of a period of `working_days` working days "beginning with" `first_day`: the
    first day counts when it is a working day, else the period starts at the next working day."""
    return add_working_days(first_day - timedelta(days=1), working_days)


def switch_speed_deadline(
    information_received_on: date,
    contract_on: date,
    *,
    contract_after_5pm: bool = False,
    early_start_requested: bool = False,
) -> Optional[date]:
    """The last day by which reg 6ZA requires the GAINING supplier to complete a transfer, or None
    when the standard was not in force on the day the clock would start.

    Every input is the supplier's own record: the day it held enough information to confirm the
    customer and identify the meter point(s), the contract day, the contract time and whether the
    customer asked to start inside cooling-off. A transfer the customer asked to start on a later
    date is judged on that date, not here.

    NAMED, NOT PICKED: whether a clock that starts before 1 April 2024 but runs past it is judged on
    15 or 5 days is in S.I. 2024/108's transitional text, which has not been read. The regime is
    keyed to the day the clock starts, and the knowledge page says so.
    """
    if information_received_on < SWITCHING_STANDARDS[GSOPType.SWITCH_SPEED].in_force_from:
        return None
    if information_received_on < SWITCH_SPEED_AMENDED_FROM:
        return _period_end(information_received_on, SWITCH_SPEED_WORKING_DAYS_2020)
    clock_starts = information_received_on
    if not early_start_requested:
        cooling_off_ends = contract_on + timedelta(days=SWITCH_SPEED_COOLING_OFF_DAYS - 1)
        clock_starts = max(information_received_on, cooling_off_ends)
    days = (SWITCH_SPEED_WORKING_DAYS_2024_AFTER_5PM if contract_after_5pm
            else SWITCH_SPEED_WORKING_DAYS_2024)
    return _period_end(clock_starts, days)


def switch_speed_failed_on(deadline: Optional[date], completed_on: date) -> Optional[date]:
    """The day reg 6ZA was first failed -- the day after the deadline -- or None if the transfer
    completed in time or no standard applied."""
    if deadline is None or completed_on <= deadline:
        return None
    return deadline + timedelta(days=1)


def erroneous_transfer_return_failed_on(agreed_on: date, returned_on: Optional[date],
                                        as_of: date) -> Optional[date]:
    """The day the OLD supplier first failed reg 6C, or None. `returned_on` is None while the
    customer has not been re-registered; the failure is then judged at `as_of`."""
    if agreed_on < SWITCHING_STANDARDS[GSOPType.ERRONEOUS_TRANSFER_RETURN].in_force_from:
        return None
    deadline = _period_end(agreed_on, ERRONEOUS_TRANSFER_RETURN_WORKING_DAYS)
    judged_on = returned_on if returned_on is not None else as_of
    return deadline + timedelta(days=1) if judged_on > deadline else None


@dataclass
class GSOPPayment:
    payment_id: int
    customer_id: str
    gsop_type: GSOPType
    trigger_date: date
    payment_due_date: date
    amount_gbp: float
    paid_date: Optional[date] = None

    @property
    def is_paid(self) -> bool:
        return self.paid_date is not None

    def is_overdue(self, as_of: date) -> bool:
        return not self.is_paid and as_of > self.payment_due_date


@dataclass
class GSOPBook:
    """Tracks GSOP triggers and auto-payments for Ofgem compliance."""

    _payments: List[GSOPPayment] = field(default_factory=list)
    _next_id: int = field(default=1)

    def record_trigger(
        self,
        customer_id: str,
        gsop_type: GSOPType,
        trigger_date: date,
    ) -> GSOPPayment:
        standard = SWITCHING_STANDARDS.get(gsop_type)
        if standard is not None:
            if trigger_date < standard.in_force_from:
                raise ValueError(
                    f"reg {standard.regulation} ({gsop_type.value}) came into force on "
                    f"{standard.in_force_from}; a failure on {trigger_date} owes nothing"
                )
            amount = standard_payment_gbp(trigger_date)
        else:
            amount = _GSOP_AMOUNT_GBP[gsop_type]
        due_date = add_working_days(trigger_date, _GSOP_PAYMENT_DAYS[gsop_type])
        payment = GSOPPayment(
            payment_id=self._next_id,
            customer_id=customer_id,
            gsop_type=gsop_type,
            trigger_date=trigger_date,
            payment_due_date=due_date,
            amount_gbp=amount,
        )
        self._payments.append(payment)
        self._next_id += 1
        return payment

    def pay(self, payment_id: int, paid_date: date) -> bool:
        for p in self._payments:
            if p.payment_id == payment_id:
                p.paid_date = paid_date
                return True
        return False

    def overdue(self, as_of: date) -> List[GSOPPayment]:
        return [p for p in self._payments if p.is_overdue(as_of)]

    def total_liability_gbp(self, year: Optional[int] = None) -> float:
        payments = self._payments
        if year is not None:
            payments = [p for p in payments if p.trigger_date.year == year]
        return sum(p.amount_gbp for p in payments)

    def annual_report(self, year: int) -> dict:
        year_payments = [p for p in self._payments if p.trigger_date.year == year]
        if not year_payments:
            return {
                "year": year,
                "total_triggers": 0,
                "total_paid": 0,
                "total_liability_gbp": 0.0,
                "auto_pay_rate_pct": 100.0,
                "overdue_count": 0,
                "by_type": {},
            }
        cutoff = date(year, 12, 31)
        paid = [p for p in year_payments if p.is_paid]
        overdue = [p for p in year_payments if p.is_overdue(cutoff)]
        by_type: Dict[str, int] = {}
        for p in year_payments:
            by_type[p.gsop_type.value] = by_type.get(p.gsop_type.value, 0) + 1
        auto_pay_rate = len(paid) / len(year_payments) * 100.0
        return {
            "year": year,
            "total_triggers": len(year_payments),
            "total_paid": len(paid),
            "total_liability_gbp": round(sum(p.amount_gbp for p in year_payments), 2),
            "auto_pay_rate_pct": round(auto_pay_rate, 1),
            "overdue_count": len(overdue),
            "by_type": by_type,
        }
