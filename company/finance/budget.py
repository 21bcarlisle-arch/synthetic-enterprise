"""FI2 — Annual budget model and variance reporting.

Budget is derived at year-start from prior-year actuals * growth targets:
  revenue * 1.10 (10% growth), opex * 1.05 (5% cost growth).
2016 is the baseline year (budget = actuals). Static constants below.
"""

# Derived: 2016 = actuals; each subsequent year from prior actual * growth factor.
# revenue grows 10%/yr; opex grows 5%/yr; gross = net + opex; cogs = revenue - gross.
_BUDGET_BY_YEAR: dict[str, dict[str, float]] = {
    '2016': {"revenue": 14671.69, "cogs": 7181.97, "gross": 7489.73, "opex": 896.73, "net": 6592.99},
    '2017': {"revenue": 16138.86, "cogs": 7945.0, "gross": 8193.86, "opex": 941.57, "net": 7252.29},
    '2018': {"revenue": 386623.75, "cogs": 249658.97, "gross": 136964.78, "opex": 8540.78, "net": 128424.0},
    '2019': {"revenue": 675851.95, "cogs": 379658.11, "gross": 296193.84, "opex": 14858.34, "net": 281335.5},
    '2020': {"revenue": 1816630.04, "cogs": 1034718.53, "gross": 781911.51, "opex": 44947.57, "net": 736963.94},
    '2021': {"revenue": 2028952.42, "cogs": 1146860.98, "gross": 882091.44, "opex": 48442.22, "net": 833649.22},
    '2022': {"revenue": 2607611.88, "cogs": 1750606.19, "gross": 857005.69, "opex": 66070.11, "net": 790935.58},
    '2023': {"revenue": 4508414.67, "cogs": 3324102.87, "gross": 1184311.8, "opex": 154750.8, "net": 1029561.0},
    '2024': {"revenue": 3512844.39, "cogs": 2492608.85, "gross": 1020235.54, "opex": 127129.79, "net": 893105.75},
    '2025': {"revenue": 3145356.42, "cogs": 1706838.08, "gross": 1438518.34, "opex": 123368.01, "net": 1315150.33},
}


def get_annual_budget(year):
    y = str(year)
    return dict(_BUDGET_BY_YEAR[y]) if y in _BUDGET_BY_YEAR else {}


def traffic_light(variance_pct):
    """RAG rating based on magnitude of variance from budget (either direction)."""
    if abs(variance_pct) < 5.0:
        return "GREEN"
    if abs(variance_pct) < 15.0:
        return "AMBER"
    return "RED"


def _var(actual, budget):
    diff = actual - budget
    pct = (diff / abs(budget) * 100.0) if abs(budget) >= 0.01 else 0.0
    return {
        "budget": round(budget, 2),
        "actual": round(actual, 2),
        "variance_gbp": round(diff, 2),
        "variance_pct": round(pct, 1),
    }


def variance_report(management_accounts_pack, year, budget=None):
    """Annual budget vs actual for one year.

    management_accounts_pack: annual_management_pack() output
      {year: {income_statement: {...}, balance_sheet: {...}}}
    Returns {revenue: {budget, actual, variance_gbp, variance_pct},
             gross:   {...}, net: {...}}
    """
    y = str(year)
    b = budget if budget is not None else get_annual_budget(y)
    if not b:
        return {}
    ma = management_accounts_pack.get(y)
    if not ma:
        return {}
    is_ = ma["income_statement"]
    return {
        "revenue": _var(is_.get("revenue_gbp", 0.0), b["revenue"]),
        "gross":   _var(is_.get("gross_margin_gbp", 0.0), b["gross"]),
        "net":     _var(is_.get("net_margin_gbp", 0.0), b["net"]),
    }


def monthly_variance(monthly_accounts, year, budget=None):
    """Monthly budget vs actual breakdown for one year.

    monthly_accounts: build_monthly_accounts() output
      {year: {month: income_statement}}  (month keys like "01".."12")
    Budget is split evenly across 12 months.
    """
    y = str(year)
    b = budget if budget is not None else get_annual_budget(y)
    if not b:
        return {}
    months = monthly_accounts.get(y, {})
    monthly_b = {k: v / 12.0 for k, v in b.items()}
    result = {}
    for month in sorted(months.keys()):
        is_ = months[month]
        result[month] = {
            "revenue": _var(is_.get("revenue_gbp", 0.0), monthly_b["revenue"]),
            "gross":   _var(is_.get("gross_margin_gbp", 0.0), monthly_b["gross"]),
            "net":     _var(is_.get("net_margin_gbp", 0.0), monthly_b["net"]),
        }
    return result
