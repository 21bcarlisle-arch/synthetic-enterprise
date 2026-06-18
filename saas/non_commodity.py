"""Non-commodity bill components — Phase 9a.

UK retail energy bills contain two broad categories:
  1. Commodity: wholesale cost + hedging capital + margin (already modelled)
  2. Non-commodity: network charges (DUoS/TNUoS/BSUoS), environmental and
     policy levies (RO, FiT, CfD, CM, SM), plus VAT

Non-commodity charges are pass-throughs — the supplier collects them from
the customer and remits them to network operators and government. Zero margin
on these components. They are excluded from gross/net margin calculations but
must appear on customer bills.

Standing charges (£/day) are pure supplier revenue — they cover metering,
data services, and admin. They DO contribute to margin.

All rates are approximate UK averages. They vary by year and distribution
network area, but using period-average constants keeps the model tractable.
Phase 9a uses flat constants; a future phase can add year-varying rates.

Sources: Ofgem Retail Market Monitoring, Cornwall Insight, BEIS energy stats.
"""

# Non-commodity electricity unit rate by segment (£/MWh).
# Includes: DUoS, TNUoS, BSUoS, Renewables Obligation, FiT levy,
#           Contract for Difference levy, Capacity Market, Smart Metering.
# Approximate 2019 values (mid-period, pre-crisis baseline).
NON_COMMODITY_RATE_GBP_PER_MWH: dict[str, float] = {
    "resi": 55.0,   # ~5.5p/kWh domestic — accounts for ~40-50% of typical bill
    "SME": 42.0,    # SME: lower levy burden, higher DUoS in some regions
}

# Non-commodity gas unit rate by segment (£/MWh).
# Includes: Gas Distribution (GDN), NTS Transportation, metering.
# Smaller than electricity (fewer environmental levies on gas in the UK).
NON_COMMODITY_GAS_RATE_GBP_PER_MWH: dict[str, float] = {
    "resi": 10.0,
    "SME": 8.0,
}

# Standing charge by commodity and segment (£/day).
# Covers: metering data collection, supply point admin, network standing.
STANDING_CHARGE_GBP_PER_DAY: dict[str, dict[str, float]] = {
    "electricity": {"resi": 0.27, "SME": 0.55},
    "gas": {"resi": 0.25, "SME": 0.40},
}

# VAT rate by segment.
# UK: 5% reduced rate for domestic energy, 20% standard rate for business.
VAT_RATE: dict[str, float] = {
    "resi": 0.05,
    "SME": 0.20,
}


def non_commodity_rate(commodity: str, segment: str) -> float:
    """Return the non-commodity pass-through unit rate (£/MWh)."""
    if commodity == "gas":
        return NON_COMMODITY_GAS_RATE_GBP_PER_MWH.get(segment, NON_COMMODITY_GAS_RATE_GBP_PER_MWH["resi"])
    return NON_COMMODITY_RATE_GBP_PER_MWH.get(segment, NON_COMMODITY_RATE_GBP_PER_MWH["resi"])


def standing_charge_rate(commodity: str, segment: str) -> float:
    """Return the standing charge (£/day)."""
    return STANDING_CHARGE_GBP_PER_DAY.get(commodity, STANDING_CHARGE_GBP_PER_DAY["electricity"]).get(
        segment, 0.27
    )


def vat_rate(segment: str) -> float:
    """Return the VAT rate (0.05 or 0.20)."""
    return VAT_RATE.get(segment, VAT_RATE["resi"])
