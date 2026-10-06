"""Back-billing compliance: the 12-month cap on retrospective charges, SLC 21BA.

The licence condition is SLC 21BA (Ofgem decision, 5 March 2018), and it protects MICROBUSINESS
customers as well as domestic ones. This module used to call it "SLC 31A" and refuse the cap to every
non-domestic account. The module now applies it to either; whether a given non-domestic account is
a microbusiness is the CALLER'S fact, and no production caller supplies it yet -- the registered gap
`microbusiness_back_billing_cap` in company/compliance/obligations_register.py.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List

# SLC 21BA: domestic and microbusiness customers cannot be back-billed for energy consumed
# more than 12 months before the billing date where the supplier failed to bill.
# Domestic from 1 May 2018; microbusiness (Part B) from 1 November 2018 -- this module applied the
# domestic date to both until 2026-10-06 (docs/market_research/back_billing_and_liability.md §7).
_BACK_BILLING_LIMIT_DAYS = 365
_BACK_BILLING_RULES_START = dt.date(2018, 5, 1)
_MICROBUSINESS_RULES_START = dt.date(2018, 11, 1)


def _rules_start(is_domestic: bool, is_microbusiness: bool) -> dt.date | None:
    """When 21BA starts to protect this customer; None when it never does."""
    if is_domestic:
        return _BACK_BILLING_RULES_START
    if is_microbusiness:
        return _MICROBUSINESS_RULES_START
    return None


class BackBillingReason(str, Enum):
    ESTIMATED_READ_CORRECTED = "estimated_read_corrected"
    SMART_METER_INSTALL_REVEALED = "smart_meter_install_revealed"
    BILLING_SYSTEM_ERROR = "billing_system_error"
    SUPPLIER_ERROR = "supplier_error"


@dataclass(frozen=True)
class BackBillingAssessment:
    account_id: str
    billing_date: dt.date
    consumption_period_start: dt.date  # when the unbilled energy was consumed
    consumption_period_end: dt.date    # end of unbilled period
    billed_amount_gbp: float
    reason: BackBillingReason
    is_domestic: bool = True
    is_microbusiness: bool = False

    @property
    def _protected_start(self) -> dt.date:
        return self.billing_date - dt.timedelta(days=_BACK_BILLING_LIMIT_DAYS)

    @property
    def cap_applies(self) -> bool:
        start = _rules_start(self.is_domestic, self.is_microbusiness)
        if start is None or self.billing_date < start:
            return False
        # Cap applies if any part of the consumption period pre-dates the 12-month window
        return self.consumption_period_start < self._protected_start

    @property
    def barred_fraction(self) -> float:
        """The share of the consumption period, by days, that the cap bars: 0.0 when it does not
        apply. Exposed so an energy figure can be barred by the same rule as the money one."""
        if not self.cap_applies:
            return 0.0
        total_days = (self.consumption_period_end - self.consumption_period_start).days
        if total_days <= 0:
            return 1.0
        allowed_days = max(0, (self.consumption_period_end - self._protected_start).days)
        return 1.0 - min(1.0, allowed_days / total_days)

    @property
    def capped_amount_gbp(self) -> float:
        if not self.cap_applies:
            return self.billed_amount_gbp
        return round(self.billed_amount_gbp * (1.0 - self.barred_fraction), 2)

    @property
    def written_off_gbp(self) -> float:
        return round(self.billed_amount_gbp - self.capped_amount_gbp, 2)


@dataclass(frozen=True)
class RecoveryPeriod:
    """One period of energy used, what it truly cost, and what the supplier recovered for it.

    `recovered_gbp` is the payment method's own recovery: for a customer who pays each bill on
    receipt it is the amount BILLED; for direct debit it is what the direct debit asked or took --
    never the bill, because a direct-debit statement is not a demand (Ombudsman's stance)."""

    period_start: dt.date
    period_end: dt.date
    true_charge_gbp: float
    recovered_gbp: float


def barred_unrecovered_gbp(
    periods: List[RecoveryPeriod],
    demand_date: dt.date,
    is_domestic: bool = True,
    is_microbusiness: bool = False,
) -> float:
    """What SLC 21BA bars at a charge recovery action on `demand_date`: the unrecovered charge for
    energy used more than 12 months before it.

    Each period's shortfall (true charge less recovered) is barred in the share of its days that
    falls before the window, so a shortfall accrued 17 months ago is lost even on accurate bills
    (Ombudsman Scenario A). The result is capped at the total still unrecovered, so where the
    payments taken covered the use nothing is barred however wrong the bills were (Scenario B):
    the cap is not a refund of payments for energy used.

    A period's collection pays its own charge first; whatever it collected ABOVE that charge pays
    the OLDEST shortfall still open. That is the running-account rule (payments discharge the
    earliest debt), and it is what a raised direct debit recovering arrears does. Netting surplus
    only against the total instead left a debt recovered and then re-accrued a year later reading
    as old: on the 2026-10-06 run that barred £20.9k at reviews where this rule bars £12.0k.
    Scenarios A and B are unchanged by it -- neither has a surplus to place.
    """
    start = _rules_start(is_domestic, is_microbusiness)
    if start is None or demand_date < start or not periods:
        return 0.0
    window_start = demand_date - dt.timedelta(days=_BACK_BILLING_LIMIT_DAYS)
    in_order = sorted(periods, key=lambda p: p.period_start)
    open_shortfall = [max(p.true_charge_gbp - p.recovered_gbp, 0.0) for p in in_order]
    surplus = sum(max(p.recovered_gbp - p.true_charge_gbp, 0.0) for p in in_order)
    for i, shortfall in enumerate(open_shortfall):
        paid = min(surplus, shortfall)
        open_shortfall[i] -= paid
        surplus -= paid
    old_shortfall = 0.0
    for p, shortfall in zip(in_order, open_shortfall):
        days = (p.period_end - p.period_start).days
        if p.period_end <= window_start or days <= 0:
            old_share = 1.0 if p.period_start < window_start else 0.0
        else:
            old_share = max(0, (window_start - p.period_start).days) / days
        old_shortfall += shortfall * old_share
    return round(old_shortfall, 2)


def barred_at_charge_recovery(
    periods: List[tuple], demand_date: dt.date, is_domestic: bool = True,
) -> float:
    """`barred_unrecovered_gbp` over plain `(start, end, charge, collected)` tuples: what the
    supplier writes off when it seeks a direct-debit balance on `demand_date`. It is the form the
    billing door publishes (`company/interfaces/bill_assembly.py`), so no company type crosses."""
    return barred_unrecovered_gbp(
        [RecoveryPeriod(s, e, charge, collected) for s, e, charge, collected in periods],
        demand_date, is_domestic=is_domestic,
    )


class BackBillingBook:
    """Tracks back-billing assessments and compliance with SLC 21BA.

    Real context:
    - SLC 21BA effective 01 May 2018: domestic AND microbusiness customers
    - Triggered most often when SMETS2 install reveals years of estimated reads
    - Estimated: suppliers collectively waived ~GBP90M in back-billing 2018-2022
    - Non-compliance: Ofgem enforcement action, restitution order
    - Non-domestic customers that are NOT microbusinesses are not protected (commercial terms)
    """

    def __init__(self) -> None:
        self._assessments: List[BackBillingAssessment] = []

    def record(self, assessment: BackBillingAssessment) -> BackBillingAssessment:
        self._assessments.append(assessment)
        return assessment

    def assessments_for(self, account_id: str) -> List[BackBillingAssessment]:
        return [a for a in self._assessments if a.account_id == account_id]

    def capped_assessments(self) -> List[BackBillingAssessment]:
        return [a for a in self._assessments if a.cap_applies]

    def non_compliant_if_charged_full(self) -> List[BackBillingAssessment]:
        return [a for a in self._assessments if a.cap_applies and a.written_off_gbp > 0]

    def total_written_off_gbp(self) -> float:
        return round(sum(a.written_off_gbp for a in self._assessments), 2)

    def total_billed_gbp(self) -> float:
        return round(sum(a.capped_amount_gbp for a in self._assessments), 2)

    def back_billing_summary(self) -> dict:
        capped = self.capped_assessments()
        return {
            "total_assessments": len(self._assessments),
            "capped_count": len(capped),
            "total_billed_gbp": self.total_billed_gbp(),
            "total_written_off_gbp": self.total_written_off_gbp(),
            "non_domestic_count": sum(1 for a in self._assessments if not a.is_domestic),
        }
