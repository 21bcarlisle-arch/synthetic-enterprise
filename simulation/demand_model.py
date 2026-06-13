"""Weather-driven demand model — Phase 4c-2 (physical simulation layer).

Replaces the flat assumption that every customer on a given Profile Class
consumes exactly the population-average shape (`sim/profile_class_1.py` /
`sim/profile_class_3.py`) with a physical adjustment layer on top of that
base shape:

  demand_shape = (base_shape + heating_load + cooling_load) * occupancy_multiplier
                 + ev_charging_load - solar_generation

- **Heating/cooling degree days**: standard UK 15.5C heating base
  temperature (the threshold below which buildings need supplementary
  heating — the conventional value used in UK degree-day data, e.g.
  gov.uk/government/statistics/degree-days) and a 22C cooling base. Extra
  load from degree days is spread across the settlement periods a household
  actually runs heating/cooling (`HEATING_PERIOD_WEIGHTS`,
  `COOLING_PERIOD_WEIGHTS`) — morning and evening for heating, afternoon for
  cooling.
- **Occupancy pattern**: `saas/property_model.py`'s occupancy_pattern
  (single/family/elderly) shifts when load is consumed within the day via
  `occupancy_multiplier()`.
- **Asset adjustments**: an EV (`assets.ev`) adds an overnight charging
  block; solar (`assets.solar`) subtracts daytime generation (estimated from
  half-hourly irradiance, e.g. `sim.weather_engine.half_hourly_solar_irradiance`)
  from net demand, floored at zero (this models net import only — export is
  out of scope for this sub-phase).

All per-degree-day and per-asset constants below are seed estimates pending
the `customer-archetype-data-enrichment` background task — see
`saas/property_model.py`'s module docstring for the same caveat.

This module is pure: plain values in, plain list-of-48-floats out. It
consumes weather *outputs* (a daily mean temperature, optional half-hourly
irradiance) rather than importing `sim.weather_engine` directly, so it can
be unit-tested without the weather engine's numpy/RNG machinery.
"""

PERIODS_PER_DAY = 48

# --- Heating/cooling degree days (UK convention) ---
HEATING_BASE_TEMP_C = 15.5
COOLING_BASE_TEMP_C = 22.0


def heating_degree_days(mean_temp_c: float) -> float:
    """Degrees below the 15.5C UK heating base temperature, floored at 0."""
    return max(0.0, HEATING_BASE_TEMP_C - mean_temp_c)


def cooling_degree_days(mean_temp_c: float) -> float:
    """Degrees above the 22C cooling base temperature, floored at 0."""
    return max(0.0, mean_temp_c - COOLING_BASE_TEMP_C)


# --- Extra load per degree-day (seed estimates) ---
GAS_HEATING_KWH_PER_DEGREE_DAY = 8.0
ELEC_HEATING_KWH_PER_DEGREE_DAY = {
    "electric_storage": 3.0,
    "heat_pump": 1.2,  # heat pumps are more efficient per degree-day than resistive storage heaters
}
ELEC_COOLING_KWH_PER_DEGREE_DAY = 0.5


def _period_weights(active_periods: range) -> list[float]:
    """A 48-length list, equal weight on `active_periods` (1-48 inclusive,
    settlement period numbering), 0 elsewhere, summing to 1."""
    active = set(active_periods)
    weight = 1.0 / len(active)
    return [weight if p in active else 0.0 for p in range(1, PERIODS_PER_DAY + 1)]


# Heating: morning warm-up (06:00-10:00, periods 13-20) and evening
# (16:30-22:00, periods 34-44) — the two periods a household typically runs
# heating.
# Each _period_weights() call sums to 1 individually, so the combined
# morning+evening weights sum to 2 — halve to renormalise to 1.
HEATING_PERIOD_WEIGHTS = [
    (w1 + w2) / 2.0
    for w1, w2 in zip(_period_weights(range(13, 21)), _period_weights(range(34, 45)))
]

# Cooling: early afternoon (11:30-18:00, periods 24-36) — peak temperature
# window.
COOLING_PERIOD_WEIGHTS = _period_weights(range(24, 37))

# --- Occupancy pattern: when load is consumed within the day ---
# Settlement periods 1-48 map to 00:00-24:00 in 30-minute steps; period p
# covers [(p-1)*0.5h, p*0.5h).
_MORNING_PERIODS = range(13, 21)  # 06:00-10:00
_EVENING_PERIODS = range(34, 45)  # 16:30-22:00


def occupancy_multiplier(occupancy_pattern: str, period: int) -> float:
    """Multiplier (around 1.0) applied to a settlement period's demand,
    reflecting when an occupancy pattern is typically home and using energy.

    period is 1-48 (settlement period numbering). Unknown occupancy_pattern
    values default to the "single" multipliers.
    """
    morning = period in _MORNING_PERIODS
    evening = period in _EVENING_PERIODS

    if occupancy_pattern == "elderly":
        # Home most of the day — flatter profile, daytime load close to peak.
        return 1.1 if (morning or evening) else 1.2
    if occupancy_pattern == "family":
        # Out at work/school during the day, sharp evening peak.
        if evening:
            return 1.4
        if morning:
            return 1.1
        return 0.85

    # "single" (default): out most of the day, moderate evening peak.
    if evening:
        return 1.25
    if morning:
        return 1.0
    return 0.75


# --- Asset adjustments ---
EV_CHARGING_KWH_PER_NIGHT = 8.0
EV_CHARGING_PERIODS = range(1, 9)  # 00:00-04:00, off-peak overnight charging

SOLAR_KWP = 3.5  # typical UK residential rooftop array size
SOLAR_PERFORMANCE_FACTOR = 0.85  # inverter/system losses


def solar_generation_shape(irradiance_w_m2_periods: list[float], kwp: float = SOLAR_KWP) -> list[float]:
    """Convert 48 half-hourly irradiance values (W/m^2, e.g. from
    `sim.weather_engine.half_hourly_solar_irradiance`) to kWh generated by a
    `kwp`-rated rooftop array over each half-hour period."""
    return [(irr / 1000.0) * kwp * SOLAR_PERFORMANCE_FACTOR * 0.5 for irr in irradiance_w_m2_periods]


def build_demand_shape(
    base_shape: list[float],
    mean_temp_c: float,
    commodity: str,
    property: dict,
    irradiance_w_m2_periods: list[float] | None = None,
) -> list[float]:
    """Apply weather, occupancy, and asset adjustments to a 48-period base
    consumption shape (e.g. `sim.profile_class_1.load_pc1_shape()`).

    commodity: "electricity" or "gas".
    property: a `saas.property_model.build_properties()` record —
        `heating_system`, `occupancy_pattern`, and `assets` are used.
    irradiance_w_m2_periods: 48 half-hourly irradiance values, required only
        if `property["assets"]["solar"]` is set and commodity is
        "electricity" — ignored otherwise.

    Returns a new 48-length list of kWh values, floored at 0. `base_shape`
    is not mutated.
    """
    hdd = heating_degree_days(mean_temp_c)
    cdd = cooling_degree_days(mean_temp_c)
    shape = list(base_shape)
    heating_system = property["heating_system"]

    if commodity == "gas":
        if heating_system == "gas_boiler" and hdd > 0:
            extra = hdd * GAS_HEATING_KWH_PER_DEGREE_DAY
            shape = [s + extra * w for s, w in zip(shape, HEATING_PERIOD_WEIGHTS)]
    else:
        if hdd > 0 and heating_system in ELEC_HEATING_KWH_PER_DEGREE_DAY:
            extra = hdd * ELEC_HEATING_KWH_PER_DEGREE_DAY[heating_system]
            shape = [s + extra * w for s, w in zip(shape, HEATING_PERIOD_WEIGHTS)]
        if cdd > 0:
            extra = cdd * ELEC_COOLING_KWH_PER_DEGREE_DAY
            shape = [s + extra * w for s, w in zip(shape, COOLING_PERIOD_WEIGHTS)]

    occupancy_pattern = property["occupancy_pattern"]
    shape = [s * occupancy_multiplier(occupancy_pattern, p) for p, s in enumerate(shape, start=1)]

    if commodity == "electricity":
        assets = property.get("assets", {})
        if assets.get("ev"):
            per_period = EV_CHARGING_KWH_PER_NIGHT / len(EV_CHARGING_PERIODS)
            for p in EV_CHARGING_PERIODS:
                shape[p - 1] += per_period
        if assets.get("solar") and irradiance_w_m2_periods is not None:
            generation = solar_generation_shape(irradiance_w_m2_periods)
            shape = [max(0.0, s - g) for s, g in zip(shape, generation)]

    return [max(0.0, s) for s in shape]
