"""Annualised Customer Revenue Report (Phase EU).

This report answers: for each customer, what was their annualised contribution
to the company in the year just ended? It reconciles:

1. ARR (Annualised Recurring Revenue): contracted revenue annualised from actual billing
2. Net Revenue: ARR minus refunds, adjustments, bad debt provision
3. Cost-to-Serve: regulatory costs, billing costs, metering costs per customer
4. Net Contribution: Net Revenue - Cost-to-Serve

This is distinct from CLV (which is forward-looking) and from margin (which is
about wholesale cost). The Annualised Revenue Report is backward-looking: what
did we actually earn from this customer in the reporting period?

Used for:
- Board reporting (revenue recognition under IFRS 15)
- Customer profitability ranking (bottom quartile candidates for repricing)
- Bad debt analysis (customers with negative net contribution)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class RevenueAdjustmentType(str, Enum):
    CREDIT_NOTE = "credit_note"
    BAD_DEBT_WRITE_OFF = "bad_debt_write_off"
    SEG_EXPORT_PAYMENT = "seg_export_payment"
    WHD_DISCOUNT = "whd_discount"
    BACK_BILLING_WRITE_OFF = "back_billing_write_off"


@dataclass(frozen=True)
class CustomerRevenueRecord:
    account_id: str
    period_year: int
    billed_revenue_gbp: float               # gross billed
    adjustments_gbp: float                  # negative = reduces revenue
    cost_to_serve_gbp: float                # regulatory + ops cost
    bad_debt_provision_gbp: float           # portion expected uncollectable

    @property
    def net_revenue_gbp(self) -> float:
        return self.billed_revenue_gbp + self.adjustments_gbp  # adjustments are negative

    @property
    def net_contribution_gbp(self) -> float:
        return self.net_revenue_gbp - self.cost_to_serve_gbp - self.bad_debt_provision_gbp

    @property
    def is_positive_contribution(self) -> bool:
        return self.net_contribution_gbp > 0

    @property
    def cost_to_serve_ratio(self) -> float:
        if self.net_revenue_gbp <= 0:
            return 0.0
        return self.cost_to_serve_gbp / self.net_revenue_gbp

    def revenue_summary(self) -> str:
        return (
            "Revenue " + str(self.period_year) + " (" + self.account_id + "): "
            "billed=GBP" + str(round(self.billed_revenue_gbp)) + " "
            "adj=GBP" + str(round(self.adjustments_gbp)) + " "
            "c2s=GBP" + str(round(self.cost_to_serve_gbp)) + " "
            "net_contrib=GBP" + str(round(self.net_contribution_gbp))
        )


class AnnualisedRevenueBook:

    def __init__(self) -> None:
        self._records: List[CustomerRevenueRecord] = []

    def record(self, rec: CustomerRevenueRecord) -> CustomerRevenueRecord:
        self._records.append(rec)
        return rec

    def records_for_year(self, year: int) -> List[CustomerRevenueRecord]:
        return [r for r in self._records if r.period_year == year]

    def record_for(self, account_id: str, year: int) -> Optional[CustomerRevenueRecord]:
        for r in self._records:
            if r.account_id == account_id and r.period_year == year:
                return r
        return None

    def positive_contributors(self, year: int) -> List[CustomerRevenueRecord]:
        return [r for r in self.records_for_year(year) if r.is_positive_contribution]

    def negative_contributors(self, year: int) -> List[CustomerRevenueRecord]:
        return [r for r in self.records_for_year(year) if not r.is_positive_contribution]

    def total_billed_revenue_gbp(self, year: int) -> float:
        return sum(r.billed_revenue_gbp for r in self.records_for_year(year))

    def total_net_contribution_gbp(self, year: int) -> float:
        return sum(r.net_contribution_gbp for r in self.records_for_year(year))

    def top_n_by_contribution(self, year: int, n: int) -> List[CustomerRevenueRecord]:
        recs = self.records_for_year(year)
        return sorted(recs, key=lambda r: r.net_contribution_gbp, reverse=True)[:n]

    def bottom_n_by_contribution(self, year: int, n: int) -> List[CustomerRevenueRecord]:
        recs = self.records_for_year(year)
        return sorted(recs, key=lambda r: r.net_contribution_gbp)[:n]

    def revenue_report_summary(self, year: int) -> str:
        n = len(self.records_for_year(year))
        n_pos = len(self.positive_contributors(year))
        total_billed = self.total_billed_revenue_gbp(year)
        net_contrib = self.total_net_contribution_gbp(year)
        return (
            "Annualised Revenue Report (" + str(year) + "): "
            + str(n) + " customers. "
            "Total billed: GBP" + str(round(total_billed)) + ". "
            "Net contribution: GBP" + str(round(net_contrib)) + ". "
            "Positive contributors: " + str(n_pos) + "/" + str(n) + "."
        )
