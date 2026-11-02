"""A gas read is a volume, and the supplier converts it to the kWh it bills.

Built from `docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md` (C2, C3). A GB
gas meter registers cubic metres, or hundreds of cubic feet on an imperial meter (R1). The licence
makes the Gas (Calculation of Thermal Energy) Regulations 1996 the billing method (R2, SLC 22.7):

    kWh = V(m3) x correction factor x CV(MJ/m3) / 3.6                                     (R4)

with the CV the billing period's average of the published daily charging-area values, any amount
under 0.1 MJ/m3 ignored (R5, SI 1996/439 reg 3(2)).

THE CV HERE IS NOT THE REGULATIONS' CV. The daily series per charging area (G1) is not yet in the
commons, so the supplier converts at one fixed figure, and Ofgem's letter says a fixed CV "is not
consistent with the Regulations" (R6). Every converted record says so in `calorific_value_basis`,
so no bill looks as if it applied R5 when it did not. `period_calorific_value` is the R5 rule, ready
for the series when it lands.
"""

from __future__ import annotations

import math

#: 1 kWh = 3.6 MJ, by definition of the units.
MJ_PER_KWH = 3.6
#: The standard volume correction factor for a domestic meter: GOV.UK, "Gas meter readings and bill
#: calculation" (https://www.gov.uk/gas-meter-readings-and-bill-calculation), which calls it
#: prescribed; the instrument that fixes the figure is GAP G4 of the page above.
GAS_VOLUME_CORRECTION_FACTOR = 1.02264
#: SIMPLIFICATION: one CV for every day and charging area, GOV.UK's worked example (39.5 MJ/m3), inside
#: the 38-41 MJ/m3 band transporters must keep (R8). The real thing is the period average of National
#: Gas's published daily CV for the supply point's charging area (R5), owed as G1; until then each
#: bill's CV is off by that day-to-day spread, either way, and the record marks it a stand-in.
STAND_IN_CALORIFIC_VALUE_MJ_PER_M3 = 39.5
#: Cubic metres in a hundred cubic feet: 100 x 0.3048^3, a unit identity (GOV.UK rounds it to 2.83).
M3_PER_HUNDRED_CUBIC_FEET = 100 * 0.3048 ** 3

#: What `calorific_value_basis` says on a record converted at the stand-in, and on one at R5.
FIXED_STAND_IN = "fixed_stand_in"
PERIOD_AVERAGE = "period_average_of_daily"

READ_UNITS = ("m3", "hcf")


def period_calorific_value(daily_cvs) -> float:
    """R5: the mean of the period's daily CVs, any part under 0.1 MJ/m3 ignored (truncated, not rounded)."""
    cvs = list(daily_cvs)
    if not cvs:
        raise ValueError("a period CV needs at least one gas day's published CV")
    # The small epsilon keeps 39.5 from reading as 39.4999... after the division.
    return math.floor(sum(cvs) / len(cvs) * 10 + 1e-9) / 10


def metric_volume(volume: float, read_unit: str) -> float:
    """A register advance in cubic metres: an imperial meter's hundreds of cubic feet converted."""
    if read_unit == "m3":
        return volume
    if read_unit == "hcf":
        return volume * M3_PER_HUNDRED_CUBIC_FEET
    raise ValueError(f"a gas register reads in {READ_UNITS}, not {read_unit!r}")


def kwh_from_volume(volume: float, read_unit: str,
                    calorific_value: float = STAND_IN_CALORIFIC_VALUE_MJ_PER_M3,
                    correction_factor: float = GAS_VOLUME_CORRECTION_FACTOR) -> float:
    """R4: the kWh a volume advance bills."""
    return metric_volume(volume, read_unit) * correction_factor * calorific_value / MJ_PER_KWH


def volume_from_kwh(kwh: float, read_unit: str,
                    calorific_value: float = STAND_IN_CALORIFIC_VALUE_MJ_PER_M3,
                    correction_factor: float = GAS_VOLUME_CORRECTION_FACTOR) -> float:
    """The register advance an ESTIMATED kWh implies: what an estimated gas bill prints as its reading."""
    m3 = kwh * MJ_PER_KWH / (correction_factor * calorific_value)
    return m3 if read_unit == "m3" else m3 / M3_PER_HUNDRED_CUBIC_FEET


def conversion_terms() -> dict:
    """The CV and correction factor a gas record was converted at, and what the CV is."""
    return {"calorific_value_mj_per_m3": STAND_IN_CALORIFIC_VALUE_MJ_PER_M3,
            "calorific_value_basis": FIXED_STAND_IN,
            "correction_factor": GAS_VOLUME_CORRECTION_FACTOR}
