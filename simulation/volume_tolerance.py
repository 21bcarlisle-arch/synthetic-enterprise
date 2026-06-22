"""Phase 27c: Volume tolerance tracking for I&C contracts.

UK I&C energy contracts specify a contracted annual volume (EAC). The customer
may consume within ±10% of that contracted volume at the fixed tariff rate.
Consumption above the +10% band settles at spot price (the supplier didn't
hedge it). Consumption below the -10% band means the supplier over-hedged;
the unused hedge volume is unwound at spot.

Volume tolerance only applies to I&C segment customers. Residential and SME
fixed-tariff customers have no explicit volume tolerance clause — they pay their
unit rate on whatever they actually consume.
"""

VOLUME_TOLERANCE_FRACTION = 0.10  # ±10% of contracted volume


def compute_term_volume_tolerance(
    actual_kwh: float,
    contracted_kwh: float,
    avg_spot_gbp_per_mwh: float,
    hedge_price_gbp_per_mwh: float,
    hedge_fraction: float,
) -> dict:
    """Compute volume tolerance metrics for one contract term.

    Returns a dict with:
      contracted_kwh: the EAC-derived contracted volume for the term
      actual_kwh: total settled consumption
      variance_pct: (actual - contracted) / contracted × 100
      band_high_kwh: contracted × 1.10
      band_low_kwh: contracted × 0.90
      excess_kwh: volume above band_high (0 if within band)
      deficit_kwh: volume below band_low (0 if within band)
      excess_spot_cost_gbp: cost of procuring excess at spot
      deficit_unwind_gbp: P&L impact of unwinding over-hedged volume at spot
        positive when spot > hedge_price (supplier gains from unwind)
        negative when spot < hedge_price (supplier loses on unwind)
      within_band: bool — True if actual is within ±10% of contracted
    """
    band_high = contracted_kwh * (1 + VOLUME_TOLERANCE_FRACTION)
    band_low = contracted_kwh * (1 - VOLUME_TOLERANCE_FRACTION)

    excess_kwh = max(0.0, actual_kwh - band_high)
    deficit_kwh = max(0.0, band_low - actual_kwh)

    # Excess: supplier must buy at spot what it didn't hedge
    excess_spot_cost_gbp = excess_kwh * avg_spot_gbp_per_mwh / 1000.0

    # Deficit: supplier over-hedged by deficit_kwh × hedge_fraction
    # The hedged portion of the unused volume must be unwound:
    # bought at hedge_price, sold at spot → (spot - hedge_price) × hedged_deficit_kwh
    hedged_deficit_kwh = deficit_kwh * hedge_fraction
    deficit_unwind_gbp = hedged_deficit_kwh * (avg_spot_gbp_per_mwh - hedge_price_gbp_per_mwh) / 1000.0

    variance_pct = (actual_kwh - contracted_kwh) / contracted_kwh * 100.0 if contracted_kwh > 0 else 0.0

    return {
        "contracted_kwh": round(contracted_kwh, 1),
        "actual_kwh": round(actual_kwh, 1),
        "variance_pct": round(variance_pct, 2),
        "band_high_kwh": round(band_high, 1),
        "band_low_kwh": round(band_low, 1),
        "excess_kwh": round(excess_kwh, 1),
        "deficit_kwh": round(deficit_kwh, 1),
        "excess_spot_cost_gbp": round(excess_spot_cost_gbp, 2),
        "deficit_unwind_gbp": round(deficit_unwind_gbp, 2),
        "within_band": (excess_kwh == 0.0 and deficit_kwh == 0.0),
    }
