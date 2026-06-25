"""FI3 -- Treasury management: cash position, working capital, MCR headroom,
and forward cash flow projection.

Data source: annual_management_pack() output (balance sheets per year).
No simulation internals accessed -- uses company-layer accounting only.
"""

MCR_PER_ACCOUNT = 130.0  # Ofgem minimum capital requirement per dual-fuel account


def working_capital(balance_sheet: dict) -> float:
    """Current assets minus current liabilities from the balance sheet."""
    current_assets = (
        balance_sheet.get("cash_gbp", 0.0)
        + balance_sheet.get("trade_receivables_gbp", 0.0)
    )
    current_liabilities = (
        balance_sheet.get("vat_payable_gbp", 0.0)
        + balance_sheet.get("total_liabilities_gbp", 0.0)
    )
    return round(current_assets - current_liabilities, 2)


def cash_flow_by_year(management_pack: dict) -> dict:
    """Closing cash balance per year from management accounts balance sheets."""
    result = {}
    for year in sorted(management_pack.keys()):
        bs = management_pack[year].get("balance_sheet", {})
        result[year] = round(bs.get("cash_gbp", 0.0), 2)
    return result


def annual_cash_changes(management_pack: dict) -> dict:
    """Year-over-year change in cash balance."""
    balances = cash_flow_by_year(management_pack)
    years = sorted(balances.keys())
    changes = {}
    for i in range(1, len(years)):
        yr = years[i]
        changes[yr] = round(balances[yr] - balances[years[i - 1]], 2)
    return changes


def project_treasury(management_pack: dict, base_year: str, horizon_years: int = 3) -> dict:
    """Project cash balance forward from base_year.

    Uses the average of the last 3 years of actual cash changes as the trend.
    Returns {projected_year: cash_gbp} for base_year+1 through base_year+horizon.
    """
    changes = annual_cash_changes(management_pack)
    balances = cash_flow_by_year(management_pack)
    recent = sorted(changes.keys())[-3:]
    if not recent:
        return {}
    avg_change = sum(changes[y] for y in recent) / len(recent)
    current = balances.get(base_year, 0.0)
    result = {}
    for i in range(1, horizon_years + 1):
        proj_year = str(int(base_year) + i)
        current = round(current + avg_change, 2)
        result[proj_year] = current
    return result


def treasury_health(
    management_pack: dict,
    year: str,
    customer_count: int = 1,
) -> dict:
    """Treasury health snapshot for a given year.

    Returns cash, working capital, MCR requirement and headroom, status.
    Status: OK (headroom ratio >1x), WATCH (0x--1x), CRITICAL (<0x).
    """
    entry = management_pack.get(year, {})
    bs = entry.get("balance_sheet", {})
    cash = bs.get("cash_gbp", 0.0)
    wc = working_capital(bs)
    mcr = max(customer_count, 1) * MCR_PER_ACCOUNT
    headroom = cash - mcr
    ratio = headroom / mcr if mcr > 0 else 0.0
    if ratio > 1.0:
        status = "OK"
    elif ratio >= 0.0:
        status = "WATCH"
    else:
        status = "CRITICAL"
    return {
        "year": year,
        "cash_gbp": round(cash, 2),
        "working_capital_gbp": round(wc, 2),
        "mcr_requirement_gbp": round(mcr, 2),
        "mcr_headroom_gbp": round(headroom, 2),
        "mcr_headroom_ratio": round(ratio, 2),
        "status": status,
    }
