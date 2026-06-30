"""Porting Loss Register (Phase FL).

When a customer switches energy supplier, the company suffers a 'porting loss':
the loss of the customer's revenue, CLV, and any bundled services.

This module tracks:
1. Confirmed switch-away events (supply end notifications via MPAS/Xoserve)
2. The financial impact of each switch (revenue, margin, CLV lost)
3. Portfolio-level porting loss trend (churn rate by revenue cohort)
4. Winback eligibility assessment (can we target this lost customer?)

UK Switching Rules:
- Economy 7 / Domestic: next day switching (MPAS day-ahead process)
- I&C/HH: up to 28-day notice period
- Customer must receive accurate final bill within 6 weeks (SLC 14C)
- Former customer's data must be retained for billing/dispute resolution

Winback Rules:
- Can contact former customer immediately after switch completes
- Must honour any DNI (Do Not Induct) flag in sales systems
- GDPR: marketing consent required (customer may have withdrawn)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class SwitchReason(str, Enum):
    CHEAPER_TARIFF = "cheaper_tariff"
    POOR_SERVICE = "poor_service"
    TARIFF_COMPLEXITY = "tariff_complexity"
    MOVING_HOME = "moving_home"
    BUNDLED_DEAL_ELSEWHERE = "bundled_deal_elsewhere"
    SMART_METER_ISSUES = "smart_meter_issues"
    UNKNOWN = "unknown"


class WinbackEligibility(str, Enum):
    ELIGIBLE = "eligible"
    DNI_FLAG = "dni_flag"           # Do Not Induct
    GDPR_OPT_OUT = "gdpr_opt_out"
    TOO_SOON = "too_soon"           # <6m since switch
    NOT_ELIGIBLE = "not_eligible"


_WINBACK_ELIGIBILITY_MONTHS = 6     # re-approach after 6 months


@dataclass(frozen=True)
class PortingLossRecord:
    account_id: str
    switch_date: dt.date
    reason: SwitchReason
    annual_revenue_gbp: float
    annual_margin_gbp: float
    h3_clv_gbp: float
    has_dni_flag: bool = False
    has_gdpr_opt_out: bool = False

    @property
    def is_margin_positive(self) -> bool:
        return self.annual_margin_gbp > 0

    def winback_eligibility(self, as_of: dt.date) -> WinbackEligibility:
        if self.has_dni_flag:
            return WinbackEligibility.DNI_FLAG
        if self.has_gdpr_opt_out:
            return WinbackEligibility.GDPR_OPT_OUT
        months_since = (as_of.year - self.switch_date.year) * 12 + (
            as_of.month - self.switch_date.month
        )
        if months_since < _WINBACK_ELIGIBILITY_MONTHS:
            return WinbackEligibility.TOO_SOON
        if not self.is_margin_positive:
            return WinbackEligibility.NOT_ELIGIBLE
        return WinbackEligibility.ELIGIBLE

    def loss_summary(self) -> str:
        return (
            "PortingLoss " + self.account_id + " " + str(self.switch_date) + ": "
            "reason=" + self.reason.value + " "
            "margin=GBP" + str(round(self.annual_margin_gbp, 0))
        )


class PortingLossRegister:

    def __init__(self) -> None:
        self._losses: List[PortingLossRecord] = []

    def record(self, loss: PortingLossRecord) -> PortingLossRecord:
        self._losses.append(loss)
        return loss

    def losses_in_period(
        self, start: dt.date, end: dt.date
    ) -> List[PortingLossRecord]:
        return [l for l in self._losses if start <= l.switch_date <= end]

    def winback_eligible(self, as_of: dt.date) -> List[PortingLossRecord]:
        return [
            l for l in self._losses
            if l.winback_eligibility(as_of) == WinbackEligibility.ELIGIBLE
        ]

    def by_reason(self, reason: SwitchReason) -> List[PortingLossRecord]:
        return [l for l in self._losses if l.reason == reason]

    def total_margin_lost_gbp(
        self, start: Optional[dt.date] = None, end: Optional[dt.date] = None
    ) -> float:
        losses = self._losses
        if start and end:
            losses = self.losses_in_period(start, end)
        return sum(l.annual_margin_gbp for l in losses if l.is_margin_positive)

    def total_clv_lost_gbp(self) -> float:
        return sum(l.h3_clv_gbp for l in self._losses)

    def porting_loss_summary(self, as_of: dt.date) -> str:
        n = len(self._losses)
        n_winback = len(self.winback_eligible(as_of))
        margin_lost = self.total_margin_lost_gbp()
        return (
            "Porting Loss Register: " + str(n) + " switches. "
            "Winback eligible: " + str(n_winback) + ". "
            "Margin lost: GBP" + str(round(margin_lost, 0)) + "/yr."
        )
