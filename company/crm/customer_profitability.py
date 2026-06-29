"""Customer Profitability Register.

Computes per-customer annual contribution margin from observable data:
  contribution = revenue - wholesale_cost - levies - operating_costs

This is the company's view of which customers are net-positive or net-negative.
Flat margin pricing makes some customers net-negative when their cost-to-serve
(volume-driven levies + operating costs) exceeds the margin earned on their tariff.

All inputs are company-observable: billing records, tariff rates, forward costs,
CTS breakdowns. No simulation internals used.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CustomerProfitabilityRecord:
    """Annual profitability for one customer account."""
    account_id: str
    year: int
    annual_revenue_gbp: float
    annual_wholesale_cost_gbp: float
    annual_levy_cost_gbp: float
    annual_operating_cost_gbp: float

    @property
    def gross_margin_gbp(self) -> float:
        return round(self.annual_revenue_gbp - self.annual_wholesale_cost_gbp, 2)

    @property
    def net_contribution_gbp(self) -> float:
        return round(
            self.annual_revenue_gbp
            - self.annual_wholesale_cost_gbp
            - self.annual_levy_cost_gbp
            - self.annual_operating_cost_gbp,
            2,
        )

    @property
    def is_net_negative(self) -> bool:
        return self.net_contribution_gbp < 0.0

    @property
    def gross_margin_pct(self) -> float:
        if self.annual_revenue_gbp == 0:
            return 0.0
        return round(self.gross_margin_gbp / self.annual_revenue_gbp * 100, 2)

    @property
    def net_margin_pct(self) -> float:
        if self.annual_revenue_gbp == 0:
            return 0.0
        return round(self.net_contribution_gbp / self.annual_revenue_gbp * 100, 2)


class CustomerProfitabilityBook:
    """Register of per-customer annual profitability assessments.

    The company records a CustomerProfitabilityRecord for each account/year
    as billing and cost-to-serve data becomes available.
    """

    def __init__(self) -> None:
        self._records: list[CustomerProfitabilityRecord] = []

    def record(self, rec: CustomerProfitabilityRecord) -> CustomerProfitabilityRecord:
        self._records.append(rec)
        return rec

    def latest_for(self, account_id: str) -> Optional[CustomerProfitabilityRecord]:
        matches = [r for r in self._records if r.account_id == account_id]
        return max(matches, key=lambda r: r.year) if matches else None

    def history_for(self, account_id: str) -> list[CustomerProfitabilityRecord]:
        return sorted(
            [r for r in self._records if r.account_id == account_id],
            key=lambda r: r.year,
        )

    def net_negative_accounts(self, year: Optional[int] = None) -> list[str]:
        records = self._for_year(year)
        return sorted({r.account_id for r in records if r.is_net_negative})

    def top_n_by_contribution(self, n: int = 5, year: Optional[int] = None) -> list[CustomerProfitabilityRecord]:
        records = self._for_year(year)
        seen: dict[str, CustomerProfitabilityRecord] = {}
        for r in records:
            if r.account_id not in seen or r.year > seen[r.account_id].year:
                seen[r.account_id] = r
        return sorted(seen.values(), key=lambda r: r.net_contribution_gbp, reverse=True)[:n]

    def total_net_contribution_gbp(self, year: Optional[int] = None) -> float:
        records = self._for_year(year)
        return round(sum(r.net_contribution_gbp for r in records), 2)

    def net_negative_rate_pct(self, year: Optional[int] = None) -> float:
        records = self._for_year(year)
        if not records:
            return 0.0
        net_neg = sum(1 for r in records if r.is_net_negative)
        return round(net_neg / len(records) * 100, 2)

    def profitability_summary(self, year: Optional[int] = None) -> dict:
        records = self._for_year(year)
        if not records:
            return {"accounts_assessed": 0}
        net_neg = [r for r in records if r.is_net_negative]
        total_rev = sum(r.annual_revenue_gbp for r in records)
        total_net = sum(r.net_contribution_gbp for r in records)
        return {
            "accounts_assessed": len(records),
            "net_negative_count": len(net_neg),
            "net_negative_rate_pct": self.net_negative_rate_pct(year),
            "total_net_contribution_gbp": round(total_net, 2),
            "total_revenue_gbp": round(total_rev, 2),
            "portfolio_net_margin_pct": round(total_net / total_rev * 100, 2) if total_rev else 0.0,
        }

    def _for_year(self, year: Optional[int]) -> list[CustomerProfitabilityRecord]:
        if year is None:
            return list(self._records)
        return [r for r in self._records if r.year == year]



# Phase 44a constants for net-negative profitability feedback.
# Applied as a unit-rate uplift at renewal when prior term is net-negative.
MIN_RECORDS_FOR_JUDGEMENT: int = 3  # minimum settlement records to form a view
NET_NEGATIVE_UPLIFT_GBP_PER_MWH: float = 5.0  # uplift applied for net-negative prior term


def estimate_prior_term_net_margin(
    cid: str,
    term_start_str: str,
    all_records: list[dict],
    commodity: str = "electricity",
) -> Optional[float]:
    """Estimate total net margin from the most recent prior completed term.

    Returns the sum of net_margin_gbp for records matching:
      - customer_id == cid
      - commodity == commodity
      - settlement_date < term_start_str (point-in-time blindfold)
    grouped by term_start, using only the most recent such term.

    Returns None if:
      - No matching records exist
      - The most recent prior term has fewer than MIN_RECORDS_FOR_JUDGEMENT records
    """
    eligible = [
        r for r in all_records
        if (r.get("customer_id") == cid
            and r.get("commodity", "electricity") == commodity
            and r.get("settlement_date", "") < term_start_str
            and r.get("net_margin_gbp") is not None)
    ]
    if not eligible:
        return None

    # Find most recent prior term_start
    prior_term_starts = {r.get("term_start", "") for r in eligible if r.get("term_start")}
    if not prior_term_starts:
        return None
    latest_term = max(prior_term_starts)
    term_records = [r for r in eligible if r.get("term_start") == latest_term]

    if len(term_records) < MIN_RECORDS_FOR_JUDGEMENT:
        return None
    return sum(r["net_margin_gbp"] for r in term_records)


def compute_profitability_uplift(
    cid: str,
    term_start_str: str,
    all_records: list[dict],
) -> float:
    """Return a unit-rate uplift (GBP/MWh) for net-negative customers.

    Phase 44a: called at renewal term signing. Returns NET_NEGATIVE_UPLIFT_GBP_PER_MWH
    if the most recent prior term was net-negative; 0.0 otherwise.
    """
    prior_margin = estimate_prior_term_net_margin(cid, term_start_str, all_records)
    if prior_margin is None or prior_margin >= 0.0:
        return 0.0
    return NET_NEGATIVE_UPLIFT_GBP_PER_MWH
