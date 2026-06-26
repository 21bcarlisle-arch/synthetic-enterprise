"""Energy theft / loss indicator.

UK suppliers can be penalised by Ofgem for failing to report suspected
energy theft (meter tampering). The company detects anomalies via meter-read
discrepancies — actual kWh significantly below EAC suggests possible tampering,
faulty meter, or non-communication.

This module flags customers whose actual billed consumption deviates materially
from their contracted EAC, using only company-observable data (invoices + EAC).
"""

from __future__ import annotations

_THEFT_THRESHOLD_LOW = 0.40   # actual < 40% of EAC → investigate
_CONCERN_THRESHOLD_LOW = 0.65  # actual 40-65% of EAC → watch


def _consumption_ratio(actual_kwh: float, eac_kwh: float) -> float | None:
    if eac_kwh <= 0:
        return None
    return actual_kwh / eac_kwh


def classify_anomaly(actual_kwh: float, eac_kwh: float) -> dict:
    """Classify consumption anomaly against EAC.

    Returns: status (ok/watch/investigate/no_data), ratio, message.
    """
    ratio = _consumption_ratio(actual_kwh, eac_kwh)
    if ratio is None:
        return {"status": "no_data", "ratio": None, "message": "No EAC to compare against."}
    if ratio < _THEFT_THRESHOLD_LOW:
        return {
            "status": "investigate",
            "ratio": round(ratio, 3),
            "message": (
                f"Actual consumption is {ratio:.0%} of EAC — significantly below expected. "
                "Possible meter fault, tampering, or abandoned property. Report to Ofgem if unresolved."
            ),
        }
    if ratio < _CONCERN_THRESHOLD_LOW:
        return {
            "status": "watch",
            "ratio": round(ratio, 3),
            "message": (
                f"Actual consumption is {ratio:.0%} of EAC — below expected range. "
                "Monitor for further deviation."
            ),
        }
    return {
        "status": "ok",
        "ratio": round(ratio, 3),
        "message": f"Consumption ({ratio:.0%} of EAC) within normal range.",
    }


def screen_portfolio(customers_with_actuals: list[dict]) -> dict:
    """Screen a list of customers for theft/anomaly indicators.

    Each entry must have: customer_id, eac_kwh, actual_kwh_ytd, annualised_actual_kwh.
    Returns: investigate_count, watch_count, results list.
    """
    results = []
    for c in customers_with_actuals:
        cid = c.get("customer_id", "?")
        eac = float(c.get("eac_kwh", 0))
        actual = float(c.get("annualised_actual_kwh", 0))
        classification = classify_anomaly(actual, eac)
        results.append({"customer_id": cid, **classification})

    return {
        "total": len(results),
        "investigate": sum(1 for r in results if r["status"] == "investigate"),
        "watch": sum(1 for r in results if r["status"] == "watch"),
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "results": sorted(results, key=lambda r: (r.get("ratio") or 9999)),
    }
