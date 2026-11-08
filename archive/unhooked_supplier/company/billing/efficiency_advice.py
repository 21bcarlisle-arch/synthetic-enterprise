"""EPC-based energy efficiency advice for the customer portal.

Provides tailored recommendations and available UK government schemes
based on the customer's Energy Performance Certificate (EPC) rating.
"""

from __future__ import annotations

_EPC_ADVICE: dict[str, list[str]] = {
    "A": [
        "Your home is among the most energy-efficient in the UK.",
        "Consider a battery storage system to maximise solar generation.",
        "You may qualify for the Smart Export Guarantee (SEG) if you have solar panels.",
    ],
    "B": [
        "Your home is very energy-efficient. Great work.",
        "Consider EV charging to take advantage of off-peak electricity rates.",
        "Check whether you qualify for the Smart Export Guarantee (SEG).",
    ],
    "C": [
        "Your home is moderately efficient. A few upgrades could save £100-200/yr.",
        "Loft insulation to 270mm could save up to £150/yr.",
        "A smart thermostat (e.g. Nest, Hive) could save 10-15% on heating bills.",
    ],
    "D": [
        "Significant efficiency improvements are possible for your home.",
        "Cavity wall insulation (if applicable) can save up to £150/yr.",
        "Upgrading to LED lighting can save £40-50/yr.",
        "A smart meter will help you understand and reduce your consumption.",
    ],
    "E": [
        "Your home has significant room for improvement. Upgrades could save £300+/yr.",
        "You may qualify for the ECO4 scheme (free insulation / heat pump funding).",
        "External wall insulation may be the most impactful upgrade for your home type.",
        "The Great British Insulation Scheme may provide free insulation upgrades.",
    ],
    "F": [
        "Your home is in the lower efficiency band. Priority upgrades recommended.",
        "You are likely eligible for the ECO4 scheme (means-tested energy efficiency funding).",
        "The Boiler Upgrade Scheme offers £7,500 towards a heat pump.",
    ],
    "G": [
        "Your home is in the lowest efficiency band. Significant work is needed.",
        "ECO4 scheme: you may qualify for fully-funded upgrades (insulation, heat pump).",
        "Contact your local council — additional fuel poverty support may be available.",
    ],
}

_SCHEMES_BY_EPC: dict[str, list[str]] = {
    "A": ["Smart Export Guarantee (SEG)"],
    "B": ["Smart Export Guarantee (SEG)", "EV Chargepoint Grant"],
    "C": ["EV Chargepoint Grant"],
    "D": ["Great British Insulation Scheme", "Boiler Upgrade Scheme"],
    "E": ["ECO4", "Great British Insulation Scheme", "Boiler Upgrade Scheme"],
    "F": ["ECO4", "Boiler Upgrade Scheme", "Warm Home Discount"],
    "G": ["ECO4", "Warm Home Discount", "Local Authority Flexible Eligibility"],
}


def epc_advice(epc_rating: str | None) -> list[str]:
    """Return tailored efficiency recommendations for the given EPC rating."""
    if not epc_rating:
        return ["EPC rating not on record. Request an EPC assessment to see recommendations."]
    return _EPC_ADVICE.get(epc_rating.upper(), ["No specific advice available for this rating."])


def available_schemes(customer: dict) -> list[str]:
    """Return applicable UK government schemes for the customer."""
    epc = str(customer.get("epc_rating", "")).upper()
    return _SCHEMES_BY_EPC.get(epc, [])


def efficiency_summary(customer: dict) -> dict:
    """Combined efficiency summary for portal display."""
    epc = customer.get("epc_rating")
    advice = epc_advice(epc)
    schemes = available_schemes(customer)
    band = str(epc).upper() if epc else "unknown"
    is_high = band in ("A", "B", "C")
    return {
        "epc_rating": epc,
        "band": band,
        "is_high_efficiency": is_high,
        "advice": advice,
        "available_schemes": schemes,
    }
