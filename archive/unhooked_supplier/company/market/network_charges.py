"""Network Use of System (UoS) charges.

UK energy suppliers pay Distribution Use of System (DUoS) charges to the local
Distribution Network Operator (DNO), and Transmission Network Use of System (TNUoS)
charges to NESO. These are recovered from customers as non-commodity costs.

DUoS rates vary by DNO area and voltage level. TNUoS is based on Triads
(three highest demand half-hours Nov-Feb) for large customers; others pay a
fixed tariff.

This module provides typical DUoS/TNUoS cost estimates from company-observable
published tariff data. Values are approximate UK averages; real suppliers use
their DNO's actual tariff tables.

Sources: Ofgem network access reviews, DNO published tariff statements 2016-2025.
"""

from __future__ import annotations


# DUoS cost (p/kWh) by year and segment — UK average across DNO areas
# Domestic lower due to tranche-based allocation; SME higher; I&C via UoS agreements
_DUOS_PENCE_PER_KWH: dict[int, dict[str, float]] = {
    2016: {"resi": 2.1, "sme": 2.8, "ic": 1.4},
    2017: {"resi": 2.2, "sme": 2.9, "ic": 1.5},
    2018: {"resi": 2.4, "sme": 3.1, "ic": 1.6},
    2019: {"resi": 2.5, "sme": 3.3, "ic": 1.7},
    2020: {"resi": 2.6, "sme": 3.4, "ic": 1.7},
    2021: {"resi": 2.7, "sme": 3.5, "ic": 1.8},
    2022: {"resi": 3.0, "sme": 3.9, "ic": 2.0},
    2023: {"resi": 3.2, "sme": 4.1, "ic": 2.1},
    2024: {"resi": 3.3, "sme": 4.3, "ic": 2.2},
    2025: {"resi": 3.5, "sme": 4.5, "ic": 2.3},
}

# TNUoS residual charge (p/kWh) — same for all segments; Triad-based for HH I&C
_TNUOS_PENCE_PER_KWH: dict[int, float] = {
    2016: 0.45, 2017: 0.48, 2018: 0.52, 2019: 0.54, 2020: 0.56,
    2021: 0.58, 2022: 0.62, 2023: 0.65, 2024: 0.67, 2025: 0.70,
}

_SEGMENT_MAP = {"residential": "resi", "domestic": "resi", "resi": "resi",
                "sme": "sme", "i&c": "ic", "ic": "ic", "i_c": "ic"}


def get_duos_rate(year: int, segment: str) -> float:
    """Return DUoS rate in p/kWh for the given year and segment."""
    seg = _SEGMENT_MAP.get(segment.lower(), "sme")
    rates = _DUOS_PENCE_PER_KWH.get(year, _DUOS_PENCE_PER_KWH[2025])
    return rates.get(seg, rates["sme"])


def get_tnuos_rate(year: int) -> float:
    """Return TNUoS residual rate in p/kWh."""
    return _TNUOS_PENCE_PER_KWH.get(year, _TNUOS_PENCE_PER_KWH[2025])


def network_cost_per_mwh(year: int, segment: str) -> dict:
    """Return total network cost (DUoS + TNUoS) in GBP/MWh for given year and segment."""
    duos_p = get_duos_rate(year, segment)
    tnuos_p = get_tnuos_rate(year)
    total_p = duos_p + tnuos_p
    return {
        "year": year,
        "segment": segment,
        "duos_p_per_kwh": duos_p,
        "tnuos_p_per_kwh": tnuos_p,
        "total_p_per_kwh": round(total_p, 3),
        "total_gbp_per_mwh": round(total_p * 10, 2),  # p/kWh x 10 = GBP/MWh
    }


def annual_network_cost(year: int, segment: str, consumption_mwh: float) -> float:
    """Return total annual DUoS+TNUoS cost in GBP."""
    rate = network_cost_per_mwh(year, segment)
    return round(consumption_mwh * rate["total_gbp_per_mwh"], 2)
