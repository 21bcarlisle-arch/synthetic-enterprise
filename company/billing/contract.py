"""Contract end date and renewal window computation (company-layer).

Computes next renewal date from acquisition date and contract type.
Variable tariffs have no fixed end date.
"""

from __future__ import annotations
from datetime import date
from dateutil.relativedelta import relativedelta


_CONTRACT_YEARS: dict[str, int | None] = {
    "fixed_1yr": 1,
    "fixed_2yr": 2,
    "variable": None,
    "svt": None,
    "flex": None,
    "hh": None,
}


def contract_end_date(customer: dict, as_of: date | None = None) -> date | None:
    """Next contract renewal date on or after as_of (default: today).

    Returns None for variable/flex/SVT customers (rolling contract).
    """
    ct = str(customer.get("contract_type", "")).lower()
    term_years = _CONTRACT_YEARS.get(ct)
    if term_years is None:
        return None
    acq_raw = customer.get("acquired_date") or customer.get("acquisition_date") or ""
    if not acq_raw:
        return None
    acq = date.fromisoformat(str(acq_raw))
    pivot = as_of or date.today()
    # Advance from acquisition by N-year steps until we are past pivot
    end = acq + relativedelta(years=term_years)
    while end <= pivot:
        end += relativedelta(years=term_years)
    return end


def days_until_renewal(customer: dict, as_of: date | None = None) -> int | None:
    """Days remaining until next contract renewal date.

    Returns None if no fixed renewal date.
    """
    end = contract_end_date(customer, as_of)
    if end is None:
        return None
    pivot = as_of or date.today()
    return (end - pivot).days


def is_in_notice_window(customer: dict, window_days: int = 30,
                        as_of: date | None = None) -> bool:
    """True if the contract renewal is within window_days days."""
    days = days_until_renewal(customer, as_of)
    if days is None:
        return False
    return days <= window_days


def renewal_summary(customer: dict, as_of: date | None = None) -> dict:
    """Renewal status dict for portal display."""
    end = contract_end_date(customer, as_of)
    days = days_until_renewal(customer, as_of)
    in_window = is_in_notice_window(customer, as_of=as_of)
    ct = str(customer.get("contract_type", "")).lower()
    return {
        "contract_type": ct,
        "is_fixed": _CONTRACT_YEARS.get(ct) is not None,
        "end_date": end.isoformat() if end else None,
        "days_until_renewal": days,
        "in_notice_window": in_window,
    }
