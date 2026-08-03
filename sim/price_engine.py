"""Phase 3b (Epoch-2 recalibration) — merit-order wholesale price model
(Regime-3 generative physics engine).

This is the synthetic *price* physics engine: a structural model of how the
System Sell Price emerges from gas, carbon, demand, and renewable supply,
rather than a re-sampling of historical SSP itself. It remains gated OFF in
every production simulation phase — every phase continues to use real
historical SSP (sim/system_prices_history.py) for the historical window, and
the statistical OLS regression (simulation/run_phase3b_regression.py) for
beyond-history (Regime 3) projection. This module is a candidate physics-based
alternative to that OLS regression, not yet wired into any live phase.

Because it is gated off, recalibrating it changes only a code path nothing
currently reads from — it cannot perturb current P&L. That is exactly why
this recalibration is safe to do blind to company P&L (R12/R13).

--- History: the original raw-ratio form failed calibration ---
The original spec (`P_HH = gas_floor * (demand/renewable)^gamma`, raw
national-MW inputs, gamma in [1.5, 2.5]) overestimated real Elexon SSP by
roughly 10x even at gamma=1.5 (see docs/calibration/price-engine.md for the
full original report, preserved as the record of why that form failed). Two
root causes were diagnosed: (a) the raw demand/renewable RATIO has a median
around 3.5, so even a low gamma explodes the gas floor by several times; (b)
the gas floor had no carbon (UK ETS) term, so it understated the true
marginal-cost floor.

--- The 2026-07-19 recalibration (docs/calibration/price-engine.md addendum) ---
Two structural changes, both fit against the full real 2016-03-01..2025-06-07
Elexon SSP window (n=157,106 settlement periods, sim/cache/elexon_ssp_full.json)
via `simulation/run_phase3b_recalibration.py`:

1. Carbon term added to the gas floor:
     P_gas_floor = (gas_price + carbon_price * EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency
   `carbon_price_gbp_per_tonne` defaults to 0.0 (no real UK-ETS historical
   series is wired into this recalibration pass — the term is structurally
   present and unit-tested, but inactive by default; see the R10 note below).

2. The margin term is now a RESIDUAL-DEMAND SCARCITY form, replacing the raw
   demand/renewable ratio:
     RD = demand_mw - renewable_generation_mw          (residual demand: the
                                                          load thermal plant
                                                          must actually serve)
     x  = RD / DISPATCHABLE_CAPACITY_MW                (normalized against
                                                          the GB dispatchable
                                                          fleet)
     multiplier = A0 + A1*x + A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
     P_HH = P_gas_floor * multiplier
   This multiplier is ≈1 (near the floor) at typical (median) residual
   demand, falls toward/below zero when renewables flood the system
   (x very negative), and rises convexly only once the margin gets
   unusually tight (x > X_TIGHT) — matching the real merit-order intuition
   that a small extra increment of demand near full dispatch jumps to a much
   dearer plant, without the raw-ratio form's runaway explosion in typical
   conditions.

   Calibrated fit (full window, MAE-minimizing grid search over
   X_TIGHT/SCARCITY_EXPONENT, then closed-form least-squares for A0/A1/A2 at
   each grid point): MAE=£32.79/MWh, R^2=0.419, beating both the naive
   gas-floor-alone baseline (MAE=£35.78) and the 3-feature OLS regression
   (MAE=£33.96, docs/calibration/price-engine.md) on the same window. Full
   distribution and per-year table: docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md.

3. Wind cubic physics (`wind_power_output_fraction`) is unchanged — the
   idealised turbine power curve was never the part of the model that failed
   calibration.

--- R10 simplifications (hand-set, not fit to data) ---
- `EF_GAS_TCO2_PER_MWH_TH = 0.184` — standard natural-gas combustion
  emissions factor (tCO2 per MWh thermal), DESNZ/DEFRA convention. Would be
  grounded by pulling the specific published DESNZ/DEFRA conversion-factor
  table for the relevant year (the factor drifts slightly year to year).
- `DISPATCHABLE_CAPACITY_MW = 35000.0` — approximate GB dispatchable
  generation fleet capacity (CCGT/OCGT/coal/nuclear/interconnector import
  capacity), asserted as a round-number physical scale, not fit to SSP data.
  Would be grounded by a National Grid ESO capacity-register figure for the
  specific year (this fleet has shrunk over 2016-2025 as coal exited).
- `carbon_price_gbp_per_tonne` defaults to 0.0 in every call in this
  recalibration — no real historical UK-ETS/EU-ETS carbon price series is
  wired into `simulation/run_phase3b_recalibration.py` yet. UK ETS has been
  effective since Jan 2021; a real carbon series would need to be
  time-indexed (pre-2021 the term should not apply, or should use the EU ETS
  price GB was under). Grounding this is future work, out of scope for this
  recalibration pass (which only had to fix the ~10x overestimate).

Generated by qwen2.5-coder:14b (original Phase 3b), recalibrated and
integrated by the frontier orchestrator (Epoch-2 recalibration, 2026-07-19).
"""

THERMAL_EFFICIENCY = 0.50  # MWh(e) per MWh(th), starting assumption per spec

EF_GAS_TCO2_PER_MWH_TH = 0.184  # tCO2 per MWh(th) — R10 simplification, see module docstring

# --- Residual-demand scarcity form: calibrated constants (2026-07-19) ---
# Fit via simulation/run_phase3b_recalibration.py against real Elexon SSP,
# full window 2016-03-01..2025-06-07 (n=157,106). See
# docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md for the full
# calibration report (MAE, R^2, distribution match, per-year table).
DISPATCHABLE_CAPACITY_MW = 35000.0  # R10 simplification, see module docstring
X_TIGHT = 0.70  # scarcity kicks in once residual demand exceeds 70% of DISPATCHABLE_CAPACITY_MW
SCARCITY_EXPONENT = 2.0  # convexity of the tight-margin kicker (p)
A0 = 0.326998  # multiplier intercept
A1 = 1.334629  # multiplier slope in x
A2 = 3.828327  # convex tight-margin coefficient

WIND_CUT_IN_MS = 3.0
WIND_RATED_MS = 12.0
WIND_CUT_OUT_MS = 25.0


# --- W1_7 (2026-08-03): the coal->gas->wind merit-order RE-STACKING seam ---
# FRAME §4 L2 for `W1_7_renewable_capacity_trends` asks for "the coal->gas->wind
# merit-order re-stacking so the marginal plant (and hence the gas-floor vs
# system-margin blend price_engine.py already models) shifts over tau. Coal exits
# the stack on its real retirement schedule."
#
# The R10 note above already concedes the defect: DISPATCHABLE_CAPACITY_MW is a flat
# hand-set 35000 and "this fleet has shrunk over 2016-2025 as coal exited". It has:
# real UK coal capacity went 13.7 GW (2016) -> 0 (2025) and the whole dispatchable
# stack contracted ~18%, so the convex scarcity tail A2*max(0, x - X_TIGHT)**p bites
# at the same ABSOLUTE residual demand in 2025 as in 2016. False to reality.
#
# THE SEAM, and its wall. Passing `year=tau` to `system_margin_price`/`synthetic_price`
# swaps the flat constant for the real year-indexed dispatchable fleet, sourced in
# `sim/renewable_capacity_trend.dispatchable_capacity_mw` from DUKES 5.7.A. That
# function returns `DISPATCHABLE_CAPACITY_MW * (D_real(tau) / mean_2016_2025(D_real))`
# -- SHAPE ONLY. The window-mean denominator therefore remains EXACTLY the calibrated
# 35000, and A0/A1/A2/X_TIGHT/SCARCITY_EXPONENT/THERMAL_EFFICIENCY are not re-opened,
# re-fit or even read by the trend layer (R12/S8: a time-varying input is a fidelity
# fix; re-fitting the multiplier to chase a nicer MAE would be goal-seeking).
#
# `year=None` (the default) is BYTE-IDENTICAL to the pre-W1_7 behaviour -- no import
# happens, no file is read, no arithmetic changes. The import is lazy and inside the
# function purely to keep this module dependency-free at import time, exactly as
# `weather_price_chain._wind_fleet_mw` already does for the renewable side.
_USE_CALIBRATED_CONSTANT = object()  # sentinel: "caller did not name a capacity"


def _resolve_dispatchable_capacity_mw(dispatchable_capacity_mw, year) -> float:
    """Pick the merit-order denominator. Explicit capacity wins; `year` selects the
    real year-indexed fleet; neither gives the calibrated constant.

    Naming BOTH is a caller bug and raises -- silently preferring one would make a
    year-aware call quietly fall back to the flat constant, i.e. the re-stacking
    disappearing while everything still looked green (R15 FAIL-SILENT)."""
    explicit = dispatchable_capacity_mw is not _USE_CALIBRATED_CONSTANT
    if explicit and year is not None:
        raise ValueError(
            "pass either dispatchable_capacity_mw or year, not both — an explicit "
            "capacity would silently override the year-indexed re-stacked fleet")
    if explicit:
        return float(dispatchable_capacity_mw)
    if year is None:
        return DISPATCHABLE_CAPACITY_MW
    from sim.renewable_capacity_trend import dispatchable_capacity_mw as _fleet
    return float(_fleet(int(year)))


def gas_floor_price(
    gas_price_gbp_per_mwh: float,
    thermal_efficiency: float = THERMAL_EFFICIENCY,
    carbon_price_gbp_per_tonne: float = 0.0,
) -> float:
    """The marginal cost (£/MWh(e)) of gas-fired generation at gas_price,
    including the carbon (UK-ETS) cost of combustion.

    P_gas_floor = (gas_price + carbon_price * EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency

    `carbon_price_gbp_per_tonne` defaults to 0.0 — with the default, this
    reduces exactly to the original `gas_price / thermal_efficiency` form
    (back-compat with the pre-recalibration tests). UK ETS has applied since
    Jan 2021; a real time-indexed carbon price series is not yet wired in
    (see module docstring R10 note) — pass a non-zero value explicitly to
    exercise the carbon term.
    """
    carbon_cost_per_mwh_th = carbon_price_gbp_per_tonne * EF_GAS_TCO2_PER_MWH_TH
    return (gas_price_gbp_per_mwh + carbon_cost_per_mwh_th) / thermal_efficiency


def system_margin_price(
    gas_floor_price_gbp_per_mwh: float,
    demand_mw: float,
    renewable_generation_mw: float,
    dispatchable_capacity_mw: float = _USE_CALIBRATED_CONSTANT,
    year: int | None = None,
) -> float:
    """The merit-order system price (£/MWh): the gas floor scaled by a
    residual-demand scarcity multiplier.

    RD = demand_mw - renewable_generation_mw      (residual/thermal demand)
    x  = RD / dispatchable_capacity_mw             (normalized scarcity)
    multiplier = A0 + A1*x + A2 * max(0, x - X_TIGHT) ** SCARCITY_EXPONENT
    P_HH = gas_floor_price_gbp_per_mwh * multiplier

    Replaces the pre-recalibration raw-ratio form
    `gas_floor * (demand/renewable)^gamma`, which overestimated real SSP by
    ~10x (docs/calibration/price-engine.md). This form:
      - is ≈ the gas floor at typical (median) residual demand,
      - rises convexly, supralinearly, only once the margin is unusually
        tight (x > X_TIGHT) — a small extra demand increment near full
        dispatch jumps to a much dearer marginal plant,
      - can fall BELOW the floor, toward and below zero, when renewable
        generation is abundant relative to demand (x very negative,
        i.e. renewables flooding the system) — real SSP goes as low as
        -£185/MWh in oversupply periods.

    A0, A1, A2, X_TIGHT, SCARCITY_EXPONENT are calibrated constants (module
    level) fit against real Elexon SSP — see module docstring. No longer
    requires renewable_generation_mw > 0 (residual demand handles a
    zero-renewables period gracefully; it is simply RD = demand_mw).

    `year` (W1_7 re-stacking): when given, `dispatchable_capacity_mw` comes from the
    REAL year-indexed DUKES dispatchable fleet (coal exiting on its real schedule)
    instead of the flat calibrated constant — see the module-level seam note. Default
    None is byte-identical to the pre-W1_7 behaviour. Naming both `year` and an
    explicit `dispatchable_capacity_mw` raises.
    """
    capacity = _resolve_dispatchable_capacity_mw(dispatchable_capacity_mw, year)
    residual_demand_mw = demand_mw - renewable_generation_mw
    x = residual_demand_mw / capacity
    tight_excess = max(0.0, x - X_TIGHT)
    multiplier = A0 + A1 * x + A2 * (tight_excess ** SCARCITY_EXPONENT)
    return gas_floor_price_gbp_per_mwh * multiplier


def wind_power_output_fraction(wind_speed_ms: float, rated_power_mw: float = 1.0) -> float:
    """Idealised turbine power curve: fraction of rated_power_mw delivered
    at wind_speed_ms.

    - < 3 m/s (cut-in): 0
    - 3-12 m/s: cubic ramp, P proportional to v^3, continuous from 0 at
      3 m/s to rated_power_mw at 12 m/s
    - 12-25 m/s (rated): rated_power_mw
    - > 25 m/s (cut-out): 0
    """
    if wind_speed_ms < WIND_CUT_IN_MS or wind_speed_ms > WIND_CUT_OUT_MS:
        return 0.0
    if wind_speed_ms <= WIND_RATED_MS:
        ramp_fraction = (wind_speed_ms ** 3 - WIND_CUT_IN_MS ** 3) / (
            WIND_RATED_MS ** 3 - WIND_CUT_IN_MS ** 3
        )
        return ramp_fraction * rated_power_mw
    return rated_power_mw


def synthetic_price(
    gas_price_gbp_per_mwh: float,
    demand_mw: float,
    renewable_generation_mw: float,
    thermal_efficiency: float = THERMAL_EFFICIENCY,
    carbon_price_gbp_per_tonne: float = 0.0,
    dispatchable_capacity_mw: float = _USE_CALIBRATED_CONSTANT,
    year: int | None = None,
) -> float:
    """Convenience wrapper chaining gas_floor_price -> system_margin_price —
    the full merit-order price for one settlement period.

    `year` (W1_7 re-stacking): passthrough to `system_margin_price` — the real
    year-indexed dispatchable fleet replaces the flat calibrated constant. Default
    None is byte-identical to the pre-W1_7 behaviour."""
    floor = gas_floor_price(gas_price_gbp_per_mwh, thermal_efficiency, carbon_price_gbp_per_tonne)
    return system_margin_price(floor, demand_mw, renewable_generation_mw,
                               dispatchable_capacity_mw, year)
