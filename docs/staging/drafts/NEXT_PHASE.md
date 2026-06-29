# Phase G: ASHP Electricity Settlement Wiring

Status: IMPLEMENTING (2026-06-29) -- critical Phase F gap

Phase F built ashp_annual_kwh() but never wired it into settlement.
gas_eac_multiplier_for_date() is called (Phase D). eac_multiplier_for_date() is not.

Fix: _weather_adjusted_shape_fn gains Phase G block after EPC multiplier:
  ashp_hh = hh.ashp_annual_kwh() / 365.25 / 48
  shape = [v + ashp_hh for v in shape] if ashp_hh > 0

Result: 5,500 kWh/yr additive uplift from ASHP install date.
Gas -88% (Phase D) + electricity +5,500 (Phase G) = complete dual-fuel effect.
