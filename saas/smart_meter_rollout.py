"""Smart meter rollout model — Phase 50.

Models the UK smart meter rollout 2016-2025, giving the company an observable
basis for estimating which customers can be offered HH-eligible (ToU) tariffs.

Sources:
  - BEIS/OFGEM Smart Meter Statistics Q4 2024: ~34.5M domestic smart meters
    installed by end-2024, out of ~29M UK households (~72% penetration).
  - OFGEM Smart Meter Rollout Progress quarterly bulletins 2016-2024.
  - I&C customers >100kW: mandated HH settlement (BSC P272/P322, 2014 onwards)
    — effectively 100% HH-metered before the domestic rollout.
  - SME <100kW: follows domestic rollout with ~5-year lag (office/commercial
    meter programs slower than domestic).

The 'adoption_rate' is the annual probability a NHH customer gets a smart meter
in a given year. It does NOT include SMETS1-to-SMETS2 transitions (partial
functionality loss on supplier switch — not modelled here).

This module is observable by the company: suppliers received OFGEM rollout
statistics and their own meter installation data annually.
"""

from typing import Literal

Segment = Literal["resi", "SME", "IC"]

# Annual smart meter STOCK penetration by segment.
# Penetration = fraction of customers with smart meters installed.
# New-customer adoption rate is derived from the year-on-year penetration delta.
# I&C: mandated HH settlement, treated as 100% HH from 2016 (BSC P272).
_PENETRATION_BY_YEAR: dict[str, dict[int, float]] = {
    "resi": {
        2016: 0.10,
        2017: 0.22,
        2018: 0.35,
        2019: 0.47,
        2020: 0.54,
        2021: 0.60,
        2022: 0.65,
        2023: 0.69,
        2024: 0.72,
        2025: 0.75,
    },
    "SME": {
        2016: 0.05,
        2017: 0.10,
        2018: 0.18,
        2019: 0.26,
        2020: 0.33,
        2021: 0.39,
        2022: 0.44,
        2023: 0.49,
        2024: 0.54,
        2025: 0.57,
    },
    "IC": {
        # Mandated HH settlement for all I&C >100kW from BSC P272 (effective 2014).
        2016: 1.0,
        2017: 1.0,
        2018: 1.0,
        2019: 1.0,
        2020: 1.0,
        2021: 1.0,
        2022: 1.0,
        2023: 1.0,
        2024: 1.0,
        2025: 1.0,
    },
}

_MIN_YEAR = 2016
_MAX_YEAR = 2025


def _clamp_year(year: int) -> int:
    return max(_MIN_YEAR, min(_MAX_YEAR, year))


def get_penetration(year: int, segment: str) -> float:
    """Fraction of customers in this segment with smart meters installed by year-end."""
    seg = segment if segment in _PENETRATION_BY_YEAR else "resi"
    return _PENETRATION_BY_YEAR[seg][_clamp_year(year)]


def get_new_install_probability(year: int, segment: str) -> float:
    """Probability a NHH customer gets a smart meter installed during `year`.

    Derived from the year-on-year change in stock penetration, normalised by
    the fraction that are still NHH. Represents the company's rollout obligation
    to install meters in its NHH portfolio during the year.

    Returns 0.0 for years outside the rollout window or for I&C (always HH).
    """
    if segment == "IC":
        return 0.0  # already mandated HH

    seg = segment if segment in _PENETRATION_BY_YEAR else "resi"
    cy = _clamp_year(year)
    py = _clamp_year(year - 1)

    current = _PENETRATION_BY_YEAR[seg][cy]
    prior = _PENETRATION_BY_YEAR[seg][py]

    penetration_increase = max(0.0, current - prior)
    nhh_fraction = 1.0 - prior  # customers that were still NHH at start of year

    if nhh_fraction <= 0.0:
        return 0.0

    # Probability of getting a meter = incremental installs / NHH base
    return min(1.0, penetration_increase / nhh_fraction)


def is_hh_eligible(metering: str) -> bool:
    """True if a customer with this metering type can be offered HH (ToU) tariffs."""
    return metering == "HH"


def is_tou_eligible(customer: dict) -> bool:
    """True if a customer is eligible for Time-of-Use tariff pricing.

    Phase 51: broadens the ToU gate beyond original HH-metered customers to
    include acquired customers who have been allocated a smart meter via the
    rollout model (smart_meter=True stamped at acquisition in make_acquired_customer).

    Two paths to eligibility:
    - metering == "HH": original I&C and early-HH-resi customers (C7, C8, C9,
      C_IC1, C_IC2) — mandated HH settlement, always eligible.
    - smart_meter == True: NHH customers who have had a smart meter installed.
      These receive ToU PRICING on their contracted bill, but may still have their
      consumption ESTIMATED from profile class (not actual HH reads) if no HH data
      exists. Revenue-neutral at the 30/70 peak/off-peak assumption.
    """
    return customer.get("metering") == "HH" or customer.get("smart_meter", False) is True


def should_upgrade_to_hh(year: int, segment: str, rng_value: float) -> bool:
    """Return True if a NHH customer should be upgraded to HH this year.

    rng_value: a uniform [0, 1) random draw from the simulation's RNG.
    """
    p = get_new_install_probability(year, segment)
    return rng_value < p
