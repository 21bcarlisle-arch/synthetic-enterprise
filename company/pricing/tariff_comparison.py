"""Portal Phase 2: tariff comparison engine (company-observable only).

Computes estimated annual cost for available tariff options using:
- Forward price from sim_interface (company-observable market data)
- Published Ofgem standing charges (public regulatory data)
- A markup applied per-option to cover wholesale risk and margin

Epistemic constraint: uses only observable forward prices. No simulation
internals, no SIM cost parameters, no hedge fraction knowledge.
"""

STANDING_CHARGE_RESI_P_PER_DAY = 53.0   # Ofgem average 2024 (published)
STANDING_CHARGE_SME_P_PER_DAY = 60.0
STANDING_CHARGE_IC_P_PER_DAY = 0.0       # I&C bespoke, no published default
VAT_RATE_DOMESTIC = 0.05
VAT_RATE_BUSINESS = 0.20

_TARIFF_OPTIONS = [
    ("Fixed 1 Year", 12, 8.0),
    ("Fixed 2 Year", 24, 9.0),
    ("Variable SVT", 1, 5.0),
]


def _standing_charge(segment: str) -> float:
    if segment == "sme":
        return STANDING_CHARGE_SME_P_PER_DAY
    if segment in ("ic", "ic_gas"):
        return STANDING_CHARGE_IC_P_PER_DAY
    return STANDING_CHARGE_RESI_P_PER_DAY


def _vat_rate(segment: str) -> float:
    return VAT_RATE_DOMESTIC if segment == "resi" else VAT_RATE_BUSINESS


def unit_rate_from_forward(
    forward_gbp_per_mwh: float,
    markup_pct: float = 8.0,
    vat_rate: float = VAT_RATE_DOMESTIC,
) -> float:
    """Unit rate in pence per kWh (inc VAT) from a forward price in £/MWh."""
    base_gbp_per_kwh = forward_gbp_per_mwh / 1000.0
    with_markup = base_gbp_per_kwh * (1 + markup_pct / 100.0)
    with_vat = with_markup * (1 + vat_rate)
    return round(with_vat * 100.0, 2)


def annual_cost_gbp(unit_rate_p: float, standing_charge_p: float, eac_kwh: float) -> float:
    """Estimated annual electricity cost in £ (inc VAT)."""
    energy = (unit_rate_p / 100.0) * eac_kwh
    sc = (standing_charge_p / 100.0) * 365.0
    return round(energy + sc, 2)


def compare_tariffs(
    eac_kwh: float,
    sim_interface,
    as_of_date: str,
    segment: str = "resi",
) -> list[dict]:
    """Return tariff options sorted by estimated annual cost (cheapest first).

    Each option dict: name, term_months, forward_gbp_per_mwh, unit_rate_p_per_kwh,
    standing_charge_p_per_day, estimated_annual_cost_gbp.
    """
    sc = _standing_charge(segment)
    vat = _vat_rate(segment)
    results = []
    for name, term_months, markup_pct in _TARIFF_OPTIONS:
        fwd = sim_interface.get_forward_price("electricity", as_of_date, term_months=term_months)
        ur = unit_rate_from_forward(fwd, markup_pct, vat)
        cost = annual_cost_gbp(ur, sc, eac_kwh)
        results.append({
            "name": name,
            "term_months": term_months,
            "forward_gbp_per_mwh": round(fwd, 2),
            "unit_rate_p_per_kwh": ur,
            "standing_charge_p_per_day": sc,
            "estimated_annual_cost_gbp": cost,
        })
    return sorted(results, key=lambda x: x["estimated_annual_cost_gbp"])
