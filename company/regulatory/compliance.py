"""M2 -- Regulatory reporting: Ofgem license condition compliance.

Tracks key UK energy retail obligations:
- Domestic price cap compliance (Ofgem cap, Phase 47a)
- Smart meter rollout targets (SMETS2 mandate, Phase 50)
- Customer service standards (complaints, vulnerability flags)
- CSS filing (annual returns)

No simulation internals -- uses company-layer data only.
"""

from datetime import date

# Ofgem smart meter installation targets (% of relevant meters)
_SMART_METER_TARGETS = {
    2019: 0.53,
    2020: 0.60,
    2021: 0.65,
    2022: 0.70,
    2023: 0.74,
    2024: 0.80,
    2025: 0.86,
}

# Complaint resolution SLA: 80% within 8 weeks (Ofgem Standard Licence Condition 37)
COMPLAINT_RESOLUTION_SLA_DAYS = 56
COMPLAINT_RESOLUTION_TARGET = 0.80

# Maximum time to acknowledge complaint: 2 working days
COMPLAINT_ACKNOWLEDGEMENT_SLA_DAYS = 2

# Ofgem annual turnover fee band (GBP, approximate)
ANNUAL_TURNOVER_FEE_PCT = 0.0007  # ~0.07% of eligible annual turnover


def smart_meter_target(year: int, segment: str = "resi") -> float:
    """Regulatory smart meter penetration target for a given year.

    Returns target as a fraction (0-1). I&C: always 1.0 (BSC P272 mandate, 2017).
    SME: 0.75 of resi target (later adopter). Resi: Ofgem statutory target.
    Missing years: interpolate nearest boundary.
    """
    if segment == "ic":
        return 1.0
    base = _SMART_METER_TARGETS.get(year)
    if base is None:
        years = sorted(_SMART_METER_TARGETS.keys())
        if year < years[0]:
            base = _SMART_METER_TARGETS[years[0]] * 0.5
        else:
            base = _SMART_METER_TARGETS[years[-1]]
    return base if segment == "resi" else base * 0.75


def smart_meter_compliance_status(actual_penetration: float, year: int, segment: str = "resi") -> str:
    """COMPLIANT / AT_RISK / BREACH based on penetration vs target.

    AT_RISK: >5pp below target but not yet a formal breach.
    BREACH: >10pp below target (triggers regulatory investigation).
    """
    target = smart_meter_target(year, segment)
    gap = target - actual_penetration
    if gap <= 0:
        return "COMPLIANT"
    if gap <= 0.05:
        return "AT_RISK"
    return "BREACH"


def check_price_cap_compliance(
    tariff_records: list[dict],
    cap_unit_rate_p_per_kwh: float,
    cap_standing_charge_p_per_day: float,
) -> dict:
    """Check whether any tariff record exceeds the Ofgem domestic price cap.

    tariff_records: list of dicts with at least 'unit_rate_p_per_kwh' and
      optionally 'standing_charge_p_per_day', 'customer_id', 'period'.
    Returns {compliant: bool, breaches: list[dict], checked: int}.
    """
    breaches = []
    for r in tariff_records:
        unit = r.get("unit_rate_p_per_kwh", 0.0)
        sc = r.get("standing_charge_p_per_day", 0.0)
        if unit > cap_unit_rate_p_per_kwh or (sc and sc > cap_standing_charge_p_per_day):
            breaches.append({
                "customer_id": r.get("customer_id"),
                "period": r.get("period"),
                "unit_rate_p_per_kwh": unit,
                "cap_unit_rate": cap_unit_rate_p_per_kwh,
                "standing_charge_p_per_day": sc,
                "cap_standing_charge": cap_standing_charge_p_per_day,
            })
    return {
        "compliant": len(breaches) == 0,
        "breaches": breaches,
        "checked": len(tariff_records),
    }


def generate_css_filing(service_log_data: list[dict], year: int) -> dict:
    """Generate annual CSS (Customer Service Standards) filing summary.

    service_log_data: list of service_event dicts (from ServiceLog.as_dicts()).
    Returns Ofgem-required metrics for the CSS annual return.
    """
    yr = str(year)
    year_events = [e for e in service_log_data if e.get("event_date", "").startswith(yr)]
    total = len(year_events)
    complaints = [e for e in year_events if e.get("complaint_flag")]
    vulnerable = [e for e in year_events if e.get("vulnerability_flag")]
    resolved = [e for e in complaints if e.get("outcome") == "resolved"]

    complaint_resolution_rate = len(resolved) / len(complaints) if complaints else 1.0

    return {
        "year": year,
        "total_contacts": total,
        "total_complaints": len(complaints),
        "complaints_resolved": len(resolved),
        "complaint_resolution_rate": round(complaint_resolution_rate, 4),
        "resolution_target_met": complaint_resolution_rate >= COMPLAINT_RESOLUTION_TARGET,
        "vulnerable_customers_contacted": len(vulnerable),
        "regulatory_filing_required": True,
    }


def annual_turnover_fee(revenue_gbp: float) -> float:
    """Ofgem annual fee based on eligible annual turnover."""
    return round(revenue_gbp * ANNUAL_TURNOVER_FEE_PCT, 2)
