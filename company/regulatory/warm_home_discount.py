"""Warm Home Discount (WHD) — vulnerability-based rebate obligation.

Ofgem mandatory scheme: suppliers provide a one-off annual rebate to
eligible vulnerable customers. Amounts are set by Ofgem each scheme year.
"""

from __future__ import annotations

_WHD_REBATE_BY_YEAR: dict[int, float] = {
    2017: 135.0,
    2018: 140.0,
    2019: 140.0,
    2020: 140.0,
    2021: 140.0,
    2022: 150.0,
    2023: 150.0,
    2024: 150.0,
    2025: 150.0,
}
_DEFAULT_REBATE = 150.0


def whd_rebate_amount(year: int) -> float:
    """Ofgem WHD rebate for scheme year (£ per eligible customer)."""
    return _WHD_REBATE_BY_YEAR.get(year, _DEFAULT_REBATE)


def whd_eligible_customers(service_log) -> list[str]:
    """Account IDs of customers on vulnerability register.

    WHD Core Group eligibility is determined from DWP pension credit data.
    As a proxy, we treat any customer on the vulnerability register as eligible.
    """
    return [flag.customer_id for flag in service_log.vulnerability_register()]


def compute_whd_liability(eligible_count: int, year: int) -> float:
    """Total WHD rebate obligation for the year (£)."""
    return round(eligible_count * whd_rebate_amount(year), 2)


def whd_summary(service_log, year: int) -> dict:
    """WHD obligation summary for Ofgem annual return."""
    eligible = whd_eligible_customers(service_log)
    rebate = whd_rebate_amount(year)
    liability = compute_whd_liability(len(eligible), year)
    return {
        "year": year,
        "scheme_year": f"WHD {year}/{str(year + 1)[-2:]}",
        "eligible_count": len(eligible),
        "eligible_account_ids": eligible,
        "rebate_per_customer_gbp": rebate,
        "total_liability_gbp": liability,
    }
