# W1_11 fabric physics core — BUILD note

**Date:** 2026-08-03 · **Atom:** `W1_11_fabric_physics_core` (lane `W1_market_weather`, dial 3)
**Artefacts:** `simulation/fabric_physics.py`, `tests/simulation/test_fabric_physics.py`
**FRAME this discharges:** `docs/design/PREMISE_FABRIC_PHYSICS_DISCOVER.md` §2.1

---

## 1. The blocking question the FRAME told us to answer first — answered

The FRAME said, verbatim:

> THE FIRST QUESTION ANY BUILD ON THIS ATOM MUST ANSWER is whether W1_3/W1_4 already
> expose sub-daily LOCAL weather (temperature, irradiance, wind) or need extending —
> not established this pass, and it materially changes this atom's size.

**Answer: they do not. `observed-on-disk`.**

`sim/weather_data/{C1..C4}.csv` — the real Open-Meteo reanalysis archive, and the only
real weather in the tree — is **daily**:

```
date,location_id,temperature_max_c,temperature_min_c,temperature_mean_c,wind_speed_mean_ms,cloud_cover_pct,precipitation_mm
2016-01-01,C1,7.8,-0.4,4.6,4.37,76,1.1
```

`simulation/weather_inputs.py` exposes exactly two readers off it — `load_weather_means`
(date → `temperature_mean_c`) and `load_weather_cloud_cover` — and
`demand_model.build_demand_shape` consumes a daily mean to derive a daily HDD scalar.
There is no sub-daily temperature or irradiance series anywhere. Grep-confirmed: no
half-hourly weather field exists in `sim/` or `simulation/`.

**Consequence for sizing.** Extending W1_3/W1_4 to a genuinely sub-daily field is a much
larger atom, and it would not make the *archive* sub-daily either — the observations
themselves are daily aggregates. So this build **reconstructs** the sub-daily driver from
the daily statistics that are actually observed, rather than inventing a new data source
or blocking on a bigger atom.

## 2. What "reconstruct" means here, and why it is not fabrication

The reconstruction has **exactly three free parameters constrained by exactly three
observations**, so it adds no information that the archive does not already contain:

| Observation (real, daily) | Constraint on the reconstructed half-hourly profile |
|---|---|
| `temperature_min_c` | the profile's **minimum**, placed at sunrise — exact by construction |
| `temperature_max_c` | the profile's **maximum**, placed at solar noon + a thermal lag — exact by construction |
| `temperature_mean_c` | the profile's **mean**, matched by solving the one remaining parameter (the overnight decay rate) |

Timing comes from **solar geometry** (Cooper declination → sunrise/sunset), not from a
stored diurnal shape — so a January and a July day with identical min/max/mean still peak
at different hours. Solar gain is reconstructed the same way: clear-sky global horizontal
irradiance from solar geometry, attenuated by the observed daily `cloud_cover_pct`
(Kasten–Czeplak).

`reconstruction_residual_c` reports whatever the solve could not absorb, and
`reconstruction_reconciles` is the R15-failable control on it: the interpolation can never
quietly disagree with the archive it was built from.

## 3. What was built

A 2R2C grey-box model exactly as the FRAME specified —

```
C_i dT_i/dt = (T_a − T_i)/R_ia + (T_m − T_i)/R_im + Φ_h + Φ_p + f_i·Φ_s
C_m dT_m/dt = (T_i − T_m)/R_im                              + (1−f_i)·Φ_s
```

integrated at **1-minute sub-steps inside each settlement period**, which is what lets a
burner start *and* stop inside one half hour and therefore produces a partial duty cycle
that varies period to period.

**The deadband is the mechanism.** Two control modes, because they produce different
texture and the design must not give one texture to all systems:

- `ON_OFF_DEADBAND` — room thermostat with hysteresis, two-level modulation (rated output
  below setpoint, minimum modulation as the air node closes in). Gas boilers, resistive
  electric. **Cycles.**
- `WEATHER_COMPENSATED` — continuous modulation off an ambient-driven curve. Heat pumps,
  district heat. **Near-continuous, materially smoother** — and with a temperature-dependent
  COP, so heat-pump electricity rises *super-linearly* as ambient falls. That mechanism is
  invisible in today's flat `ELEC_HEATING_KWH_PER_DEGREE_DAY["heat_pump"] = 1.2`.

**Parameterisation** is the RdSAP-class step the FRAME asked for: `(built form, age band,
walls/insulation, floor area) → (R_ia, R_im, C_i, C_m)`, a small deterministic function
over fields already carried on `simulation/household.py::Household`.

**Character emerges, it is not asserted.** `τ_m = R_im·C_m` sets cycle length and setback
drift depth. Between-home timing diversity comes from fabric variation plus a
per-premise **structural** schedule (setpoint, setback offset, on/off times) drawn **once**
from this module's own named substream — **nothing injects per-period noise into the
output**. Injected noise would satisfy the letter of the diversity requirement while
failing its spirit, and L1.5 is designed to catch exactly that.

## 4. Two model defects caught and fixed during the build

Recorded because they were caught by looking at the numbers, not by the tests:

1. **Insulation double-counted against the age band.** Applying the retrofit multiplier on
   top of an already-modern `POST_2000` U-value produced a heat loss coefficient of
   0.059 kW/K — a 1.4 kW design load for an 82 m² semi, unphysical. Fixed with Part-L
   achievable U-value floors (`_retrofitted_u`), plus a Part-F minimum ventilation rate:
   a dwelling cannot be sealed below its indoor-air-quality requirement, so airtightness
   stops buying heat savings there. Pinned by
   `test_modern_insulation_cannot_drive_u_values_below_what_can_be_built`.
2. **The L1.5 control fired on correct physics.** As first written it counted *every*
   repeat of a rescaled fraction, so overnight off-periods (all zero) and within-day
   saturation plateaus (source flat out) tripped it. Both are real physical features. The
   control now counts **distinct days sharing a fraction** — which is what the artefact
   actually looks like — with zeros excluded. Both exclusions are visible in the mutation
   test: a rescaled base shape still fires.

## 5. Controls, and the mutation that makes each one fail (R15)

| Control | Named defect it must fire on | Test |
|---|---|---|
| `texture_is_not_a_rescaled_shape` (L1.5) | one stored base shape rescaled per day | `test_L15_control_fires_on_a_rescaled_base_shape` |
| `mass_damps_intraday_swing` | `C_m` not actually driving character | same control on **swapped** arguments must fail |
| `reconstruction_reconciles` | a profile disagreeing with the daily archive | `..._fires_on_an_unreconciled_profile`, plus NaN/inf rejected **first** |

Fail-open patterns explicitly closed: empty inputs raise rather than pass vacuously
(`mass_damps_intraday_swing`, `texture_is_not_a_rescaled_shape` with <2 days); non-finite
residuals are rejected before any comparison, since `abs(nan) <= tol` is False by luck
rather than by design.

**Threshold basis, measured not guessed** (`observed 2026-08-03`): across twelve archetypes
this generator's worst across-day fraction recurrence is 3/7, 4/30, 4/90, 31/365 days —
under ~9% even over a full year, against 100% for the artefact.

## 6. R12 / R13 pre-commitment, recorded before the numbers move

This is a **BASELINE fidelity change decided blind to company P&L**. More realistic peaks
will very likely **worsen** imbalance costs and margin. That is the CORRECT consequence of
removing a smoothing artefact and **must not be treated as a regression or tuned back**.

**Anchor independence:** SAP-class fields *parameterise* the fabric. They must never also
*judge* the output — calibrating against a source and validating against the same source is
theatre. NEED and SERL stay outside this module as independent judges. Nothing in the test
suite pins a generated value; every assertion is a relationship or a physical band.

Indicative annual heating output, for sense only — **not a calibration target**: an
uninsulated solid-wall Victorian semi ≈ 15.7 MWh heat / 18.2 MWh gas; a partially-insulated
1965–80 semi ≈ 5.8 / 6.7 MWh; a modern fully-insulated build ≈ 2.2 / 2.5 MWh; an ASHP on a
1981–2000 fully-insulated semi ≈ 3.2 MWh heat on 1.1 MWh electricity.

## 7. Level claimed, and what it is NOT

**L0 → L2.** The engine exists, is deterministic, carries its own named RNG substream, and
its three claims (level, character, texture) each have an R15-failable control with a
proven mutation. 48 tests, all passing.

**It is not L3, and this build does not claim L3.** The COUPLED TRIAD is binding: no
world/SIM atom reaches L3 until the company has been tested against it and the gap
measured. This module is not yet wired into `demand_model.build_demand_shape` or the
settlement path, so no company capability has faced it and no belief-vs-truth gap exists to
report. That wiring — and the gap measurement — is the L2→L3 step, and it is where the
harness spec's remaining L1/L2 checks get run against the live generator.

Remaining, honestly listed:

- **Not wired into the demand path.** `build_demand_shape` still takes a daily mean and a
  daily HDD scalar. Swapping it is a separate, larger touch with settlement-wide blast
  radius.
- **Latitude is a module input** (`DEFAULT_LATITUDE_DEG = 53.0`, UK population-weighted),
  not a per-premise field — `Household` carries no location. Callers with a real location
  pass their own.
- **Hot water, cooking and appliances are out of scope** — this is Layer 1, the *fabric*.
  Layer 2 (behaviour) supplies occupancy-driven gains through the existing
  `internal_gain_kw` seam.
- **EV and PV rewiring** named in FRAME §2.1 stays with their own atoms.
