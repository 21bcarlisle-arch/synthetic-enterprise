"""Energy theft / loss indicator.

A supplier's own consumption analytics are a legitimate theft LEAD source: tip-offs and
suppliers' own analysis gave 85% of suspected gas theft incidents (Ofgem 2015 §1.93, in
`docs/market_research/read_access_and_theft_duties.md` §3.2). Actual kWh far below EAC can mean
tampering -- or a vacant property, a faulty meter, or non-communication (the TEM's H4); it is a
reason to look, not a finding.

Corrected 2026-10-06: this said suppliers "can be penalised by Ofgem for failing to report
suspected energy theft" and told the user to "report to Ofgem". No source read requires reporting
theft to Ofgem. The duties are SLC 12A: investigate where there are reasonable grounds (12A.6),
enter detected theft into settlement, and work through REC Schedule 7 (TRAS risk scores, ETTOS
tip-offs, TDIS) under the Revenue Protection Code of Practice.

This flags customers whose annualised actual consumption deviates from their EAC, using only
company-observable data (invoices + EAC).
"""

from __future__ import annotations

#: UNSOURCED, so None. The 0.40 ("investigate") and 0.65 ("watch") ratios this held were typed
#: with no source, and no published actual/EAC screening threshold was found
#: (read_access_and_theft_duties.md §5). A screen tuned to a supplier's own investigation
#: outcomes would be a graded BELIEF; until one exists the caller supplies the cut-offs, and
#: without them a customer is reported "unscreened" rather than classified on an invented number.
_THEFT_THRESHOLD_LOW: float | None = None
_CONCERN_THRESHOLD_LOW: float | None = None


def _consumption_ratio(actual_kwh: float, eac_kwh: float) -> float | None:
    if eac_kwh <= 0:
        return None
    return actual_kwh / eac_kwh


def classify_anomaly(
    actual_kwh: float,
    eac_kwh: float,
    investigate_below: float | None = None,
    watch_below: float | None = None,
) -> dict:
    """Classify consumption anomaly against EAC.

    Returns: status (ok/watch/investigate/no_data/unscreened), ratio, message.
    """
    ratio = _consumption_ratio(actual_kwh, eac_kwh)
    if ratio is None:
        return {"status": "no_data", "ratio": None, "message": "No EAC to compare against."}
    investigate = investigate_below if investigate_below is not None else _THEFT_THRESHOLD_LOW
    watch = watch_below if watch_below is not None else _CONCERN_THRESHOLD_LOW
    if investigate is None or watch is None:
        return {
            "status": "unscreened",
            "ratio": round(ratio, 3),
            "message": (
                f"Actual consumption is {ratio:.0%} of EAC. Not classified: no sourced "
                "screening threshold exists and none was supplied."
            ),
        }
    if investigate > watch:
        raise ValueError(f"investigate_below ({investigate}) must not exceed watch_below ({watch})")
    if ratio < investigate:
        return {
            "status": "investigate",
            "ratio": round(ratio, 3),
            "message": (
                f"Actual consumption is {ratio:.0%} of EAC — significantly below expected. "
                "Possible meter fault, tampering, or vacant property. Where there are reasonable "
                "grounds to suspect theft, investigate under SLC 12A and the Revenue Protection "
                "Code of Practice, alongside the TRAS score (REC Schedule 7)."
            ),
        }
    if ratio < watch:
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


def screen_portfolio(
    customers_with_actuals: list[dict],
    investigate_below: float | None = None,
    watch_below: float | None = None,
) -> dict:
    """Screen a list of customers for theft/anomaly indicators.

    Each entry must have: customer_id, eac_kwh, actual_kwh_ytd, annualised_actual_kwh.
    Returns: investigate/watch/ok/unscreened counts and the results list.
    """
    results = []
    for c in customers_with_actuals:
        cid = c.get("customer_id", "?")
        eac = float(c.get("eac_kwh", 0))
        actual = float(c.get("annualised_actual_kwh", 0))
        classification = classify_anomaly(actual, eac, investigate_below, watch_below)
        results.append({"customer_id": cid, **classification})

    return {
        "total": len(results),
        "investigate": sum(1 for r in results if r["status"] == "investigate"),
        "watch": sum(1 for r in results if r["status"] == "watch"),
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "unscreened": sum(1 for r in results if r["status"] == "unscreened"),
        "results": sorted(results, key=lambda r: (r.get("ratio") or 9999)),
    }
