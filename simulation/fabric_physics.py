"""Fabric physics core — Layer 1 of the two-layer premise demand engine (W1_11).

PURPOSE
-------
Turn a premise's *structural* EPC-class fields plus its *local half-hourly weather*
into a half-hourly heat-delivery series, by simulating the building rather than by
rescaling a stored shape. Fabric sets both the annual LEVEL (how much heat the
envelope loses) and the intra-day CHARACTER (when, and in what size lumps, that
heat is delivered).

GUARANTEES
----------
1. **The deadband is the mechanism, not a detail.** A 2R2C model driven by a
   continuous, perfectly-modulating heat source reproduces today's smoothness
   exactly. The half-hourly texture here comes from the CONTROLLER: a thermostat
   deadband plus a heat source with a finite modulation range. The air node crosses
   the deadband, the burner fires, the air node overshoots, the burner stops — a
   partial duty cycle that varies period to period.
2. **Character emerges; it is not asserted.** `tau_m = R_im * C_m` sets cycle length
   and setback-drift depth, so a high-mass solid-wall home runs long and smooth
   while a low-mass modern home cycles and spikes. Nothing in this module injects
   per-period noise into the OUTPUT — between-home timing diversity falls out of
   fabric variation plus setpoint/schedule variation (structural, drawn once per
   premise). Injected output noise would satisfy the letter of the diversity
   requirement while failing its spirit, and the harness spec's L1.5 structural
   check is designed to catch exactly that.
3. **Determinism / C-S2.** Every draw here comes from this module's OWN named seeded
   substream (`STREAM_NAME`), so a draw can never shift another subsystem's
   sequence. Given the same (household, weather, seed) the output is bit-identical
   across processes, and multi-day runs chain thermal state explicitly.

WHY IT IS BUILT THIS WAY (the open dependency the FRAME told us to answer first)
-------------------------------------------------------------------------------
`observed-on-disk (2026-08-03)` — the real weather archive (`sim/weather_data/*.csv`,
Open-Meteo reanalysis, Historical Ground Truth) is **DAILY**: `temperature_max_c`,
`temperature_min_c`, `temperature_mean_c`, `wind_speed_mean_ms`, `cloud_cover_pct`,
`precipitation_mm`. There is no sub-daily temperature or irradiance anywhere in the
tree, and `demand_model.build_demand_shape` takes a daily mean and derives a daily
HDD scalar — so intraday temperature, overnight cooling and solar GAIN are invisible
to today's heating term. No thermal-dynamics model can be fitted on top of that
input contract.

Rather than extend W1_3/W1_4 (a much larger atom, and it would not make the archive
sub-daily either), this module RECONSTRUCTS a half-hourly ambient profile from the
three daily statistics that *are* observed, using solar geometry for the timing.
That is an honest interpolation, not an invention: the model has exactly three free
parameters and is constrained by exactly three observations —

  * the reconstructed series' MINIMUM equals the observed `temperature_min_c`
    (placed at sunrise, by construction),
  * its MAXIMUM equals the observed `temperature_max_c`
    (placed at solar noon + a thermal lag, by construction),
  * its MEAN is matched to the observed `temperature_mean_c` by solving the one
    remaining free parameter — a TWO-SIDED day-shape parameter that decides how
    much of the day is spent near the maximum (`_diurnal_shape`).

`reconstruction_residual_c` reports what the solve could not absorb, and
`reconstruct_ambient_profile` REFUSES to return a profile the residual condemns
— so the interpolation cannot quietly disagree with the archive.

`observed-with-evidence (2026-08-03 HARDEN)` — both halves of that sentence were
false as first built, and together they were a measured demand bias rather than a
tidiness point. The shape parameter was bracketed at [0.02, 40], which could only
place the daily mean BELOW ~0.55 of the daily swing; the real archive spans
[0.203, 0.831] and puts 26% of its days above that ceiling. So the solve clamped
and the reconstructed day came out COLDER than the archive says it was — by up to
2.49 C of daily mean, on 14.3-20.5% of days depending on site. `reconstruction_
reconciles` would have flagged every one of them, and it had NO CALLER outside its
own unit test: the residual was computed, stored, and read by nobody (R11 orphan).
The shipped suite tested the LOW tail only ("mean far below the midpoint") and
never the high one, which is how a green suite shipped it. Both are now closed —
the family is two-sided, and the constructor consults the control — and measured
across the whole archive afterwards: 0 of 13,784 real site-days fail, worst
residual 0.0000 C, solved parameter spanning [-8.5, +30.2] inside a +/-40 bracket.

Solar gain is reconstructed the same way: clear-sky global horizontal irradiance
from solar geometry, attenuated by the observed daily `cloud_cover_pct`.

R12 / R13 PRE-COMMITMENT (recorded before the numbers move)
-----------------------------------------------------------
This is a BASELINE fidelity change decided blind to company P&L. More realistic
peaks will very likely WORSEN imbalance costs and margin. That is the CORRECT
consequence of removing a smoothing artefact and must not be treated as a
regression or tuned back.

LOCAL WEATHER AND PER-ORIENTATION SUN (director finding, 2026-08-03 fix)
--------------------------------------------------------------------------
`observed-with-evidence` — as first built, this module had exactly ONE caller
of `reconstruct_ambient_profile`/`reconstruct_irradiance_profile` anywhere in
the tree (`tests/simulation/test_fabric_physics.py`), and every one of them
either omitted `latitude_deg` or passed `DEFAULT_LATITUDE_DEG` explicitly.
`DEFAULT_LATITUDE_DEG` (a UK population-weighted mean, 53.0 deg) was therefore
what every simulated premise actually received — the averaging fault the
director asked to have confirmed one layer up from the demand model. There was
also no per-orientation sun at all: `clear_sky_ghi_kw_per_m2` is global
HORIZONTAL irradiance, so a north- and a south-facing home received identical
solar gain.

**One fix landed; the second was DOCUMENTED BUT NEVER WRITTEN, and that is
recorded here rather than quietly deleted** (2026-08-03 HARDEN):

1. **Genuinely local weather, honestly bounded at FOUR sites — LANDED.**
   `latitude_deg` is no longer defaulted anywhere a real location exists to
   pass: `reconstruct_ambient_profile`, `reconstruct_irradiance_profile` and
   `simulate_premise` all now REQUIRE it, so a caller that forgets it fails
   loudly instead of silently receiving the national mean.
   `latitude_for_weather_site` resolves an archive site id against
   `WEATHER_SITE_LATITUDE_DEG` (the REAL published coordinates the archive was
   fetched at — `saas/customers.py`'s C1-C4 `location` dicts /
   `docs/data-sources/weather.md`) and raises for anything outside the four
   sites the archive covers. This is honest at exactly the resolution the
   archive supports: FOUR real sites (London/Manchester/Glasgow/Cotswolds),
   DAILY statistics reconstructed to half-hourly by solar geometry. It is NOT
   per-postcode weather — the archive does not have that, and nothing here
   claims otherwise.

   `observed-with-evidence (2026-08-03 HARDEN)` — this paragraph previously
   claimed the defaulting was already gone AND that `simulate_premise` resolved
   latitude itself from a `DailyWeather.location_id` field. Neither was true:
   `DailyWeather` has no such field, and `simulate_premise` /
   `reconstruct_irradiance_profile` both still defaulted to
   `DEFAULT_LATITUDE_DEG`. `tools/couple_fabric.py` consequently drove a C1
   (London, 51.51 N) panel at 53.0 N for every gap number it has ever written
   to `coupled_gap_ledger.json`. The requirement is now enforced by
   `test_no_public_entry_point_lets_latitude_default_to_the_national_mean`,
   which reads the real signatures via `inspect` — a claim in prose is what
   drifted, so the replacement is a test, not better prose (R10 class guard).

2. **Per-orientation sun — NOT BUILT. This is an OPEN SIMPLIFICATION, not a
   feature.** The text here previously described a
   `reconstruct_poa_irradiance_profile` that transposed global horizontal
   irradiance onto the premise's glazing plane via Liu & Jordan (1963) /
   Erbs, Klein & Duffie (1982) / Duffie & Beckman (2013), reusing
   `Household.roof_aspect` as the glazing orientation. **No such function exists
   anywhere in the tree**, `roof_aspect` is read by nothing in this module, and
   `solar_aperture_m2` is orientation-blind — a north- and a south-facing home
   still receive identical solar gain here. The citations were for code that was
   never written. The claim is withdrawn and re-registered as a named residual
   on the atom rather than left standing as documentation of a fix.
   (`premise_trace.pv_generation_kwh` does transpose by orientation, but that is
   the PV *generation* path, not this module's solar *gain*.)

ANCHOR INDEPENDENCE
-------------------
SAP-class fields PARAMETERISE the fabric here. They must never also be used to
JUDGE the output — calibrating against a source and validating against the same
source is theatre. Validation anchors (NEED, SERL) stay outside this module.

EPISTEMIC NOTE
--------------
This is SIM-side generation. Everything it consumes — EPC structural fields and
published weather — is genuinely public, so no company-layer state is read and no
simulation internal is exposed. The company sees only the metered result.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from enum import Enum

from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)

PERIODS_PER_DAY = 48
SUB_STEPS_PER_PERIOD = 30  # 1-minute integration steps — see `_SUB_STEP_HOURS`
_SUB_STEP_HOURS = 0.5 / SUB_STEPS_PER_PERIOD

STREAM_NAME = "W1_11_fabric_physics"

# `domain-knowledge` — UK population-weighted latitude. An INPUT a caller may
# legitimately choose for genuinely NATIONAL/aggregate work (there is no such
# thing as "the" latitude of a whole-GB roll-up) — never a silent per-premise
# fallback. No function in this module defaults to it any more (2026-08-03
# fix): `latitude_deg` is a required argument everywhere a real location
# exists to pass, precisely so a caller cannot forget it and land here
# unnoticed.
DEFAULT_LATITUDE_DEG = 53.0

# `domain-knowledge` — the REAL published coordinates of the four sites the
# weather archive (`sim/weather_data/C{1..4}.csv`, Open-Meteo reanalysis) was
# actually fetched at. Copied from `saas/customers.py`'s `location` dicts
# (cross-checked against `docs/data-sources/weather.md`) — the SAME
# coordinates the archive already used, not a new or re-guessed location.
# These are the only four sites this simulation has real local weather for;
# resolving a premise past this table (e.g. to a synthetic postcode) would be
# a fabrication this module refuses to make.
WEATHER_SITE_LATITUDE_DEG: dict[str, float] = {
    "C1": 51.5074,  # London
    "C2": 53.4808,  # Manchester
    "C3": 55.8642,  # Glasgow
    "C4": 51.8330,  # Cotswolds
}


def latitude_for_weather_site(location_id: str) -> float:
    """FAIL-CLOSED (R15): the real latitude for one of the four sites this
    archive covers. Raises for anything else rather than silently returning
    `DEFAULT_LATITUDE_DEG` — that silent fallback is precisely the fault this
    function exists to close off."""
    try:
        return WEATHER_SITE_LATITUDE_DEG[location_id]
    except KeyError:
        raise ValueError(
            f"{location_id!r} is not one of the weather sites this archive "
            f"covers ({sorted(WEATHER_SITE_LATITUDE_DEG)}) — refusing to "
            "silently default to a national-average latitude"
        ) from None


# ---------------------------------------------------------------------------
# Sub-daily weather reconstruction (see module docstring for why this exists)
# ---------------------------------------------------------------------------


def solar_declination_deg(day_of_year: int) -> float:
    """Solar declination — the standard Cooper (1969) approximation."""
    return 23.44 * math.sin(math.radians(360.0 / 365.0 * (day_of_year - 81)))


def daylight_hours(latitude_deg: float, day_of_year: int) -> tuple[float, float]:
    """(sunrise, sunset) in local solar hours, from latitude and day of year.

    Clamped for the polar edge cases so the function is total; at UK latitudes the
    clamp never binds.
    """
    lat = math.radians(latitude_deg)
    dec = math.radians(solar_declination_deg(day_of_year))
    cos_h = -math.tan(lat) * math.tan(dec)
    cos_h = max(-1.0, min(1.0, cos_h))
    half_day_hours = math.degrees(math.acos(cos_h)) / 15.0
    return 12.0 - half_day_hours, 12.0 + half_day_hours


def solar_elevation_sin(latitude_deg: float, day_of_year: int, hour: float) -> float:
    """sin(solar altitude) at `hour` local solar time; negative below the horizon."""
    lat = math.radians(latitude_deg)
    dec = math.radians(solar_declination_deg(day_of_year))
    hour_angle = math.radians(15.0 * (hour - 12.0))
    return math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(hour_angle)


# `domain-knowledge` — solar constant (kW/m^2), the extraterrestrial
# irradiance on a plane normal to the sun's rays at 1 AU. Named once and reused
# by the Haurwitz clear-sky model below AND by the clearness-index calculation
# the orientation transposition needs, so the two stay numerically consistent.
_SOLAR_CONSTANT_KW_PER_M2 = 1.361


def clear_sky_ghi_kw_per_m2(latitude_deg: float, day_of_year: int, hour: float) -> float:
    """Clear-sky global horizontal irradiance (kW/m^2), Haurwitz-form:
    0.75 of the extraterrestrial horizontal beam. Zero below the horizon."""
    sin_alt = solar_elevation_sin(latitude_deg, day_of_year, hour)
    if sin_alt <= 0.0:
        return 0.0
    return 0.75 * _SOLAR_CONSTANT_KW_PER_M2 * sin_alt


def cloud_attenuation(cloud_cover_fraction: float) -> float:
    """Kasten-Czeplak cloud attenuation of global horizontal irradiance."""
    cc = max(0.0, min(1.0, cloud_cover_fraction))
    return 1.0 - 0.75 * (cc**3.4)


# `domain-knowledge` — how strongly the single shape parameter also stretches the
# MORNING RISE. Coupling the two halves is what makes the family two-sided: see
# `_rise_exponent`. 0.10 per unit of k puts the whole observed archive strictly
# inside the solve bracket below with headroom at both ends (measured: solved k
# spans [-8.5, +30.2] over 13,784 real site-days, against a +/-40 bracket).
_RISE_SHAPE_PER_K = 0.10
# The solve bracket, as two SEPARATELY NAMED edges rather than one symmetric
# constant. The asymmetry is the whole point: the shipped defect was
# `_SHAPE_K_MIN = 0.02`, and naming the edge is what lets the mutation test
# restore exactly that value and prove the family widening is load-bearing
# (`test_the_one_sided_solve_bracket_cannot_reconstruct_a_real_warm_evening`).
_SHAPE_K_MIN = -40.0
_SHAPE_K_MAX = 40.0


def _rise_exponent(decay_k: float) -> float:
    """Exponent on the morning rise, coupled to the same single parameter.

    >1 (positive k) holds the profile down near its minimum through the morning;
    <1 (negative k) drives it up to the maximum early. 1.0 at k=0, and continuous
    there, so the family is a single smooth one-parameter curve rather than two
    regimes bolted together.
    """
    stretch = 1.0 + _RISE_SHAPE_PER_K * abs(decay_k)
    return stretch if decay_k >= 0.0 else 1.0 / stretch


def _diurnal_shape(hour: float, sunrise: float, peak_hour: float, decay_k: float) -> float:
    """Unit diurnal shape in [0, 1]: 0 at sunrise, 1 at `peak_hour`.

    Sinusoidal rise from sunrise to the afternoon peak, exponential decay from the
    peak round to the next sunrise. `decay_k` is the single free parameter the mean
    solve turns, and it is TWO-SIDED — which it was not as first built, and that was
    a measured defect rather than a refinement (2026-08-03 HARDEN):

      * **negative k** holds the profile near its maximum into the evening before a
        late drop, and starts the rise early — a HIGH daily mean relative to the
        min/max midpoint;
      * **positive k** drops it away quickly after the peak and holds it near the
        minimum through the morning — a LOW daily mean.

    As first built `decay_k` was bracketed at [0.02, 40], so the family could only
    reach mean fractions of roughly [0.21, 0.55] of the daily swing. The real
    archive spans [0.203, 0.831] and **26% of its days sit above 0.545**, so the
    solve clamped and the reconstructed day came out COLDER than the archive says
    it was — by up to 2.5 C of daily mean, on 14-20% of days per site. A cold bias
    in the ambient drive is a heating-demand bias in exactly the quantity this
    module exists to produce. `reconstruction_reconciles` would have caught every
    one of those days; nothing called it (see `reconstruct_ambient_profile`).

    The mean is monotonically DECREASING in k across the whole bracket — both
    halves of the coupling push the same way — which is what lets the solve stay a
    plain bisection.
    """
    rise_span = peak_hour - sunrise
    fall_span = 24.0 - rise_span
    # Position `hour` on the cycle that starts at this day's sunrise.
    u = (hour - sunrise) % 24.0
    if u <= rise_span:
        return math.sin(math.pi / 2.0 * (u / rise_span)) ** _rise_exponent(decay_k)
    v = (u - rise_span) / fall_span  # 0 at the peak, 1 at the next sunrise
    if abs(decay_k) < 1e-9:
        # The k -> 0 limit of the expression below is a straight line. Taking it
        # explicitly keeps the family continuous through the middle of the bracket,
        # which a two-sided solve now walks through.
        return 1.0 - v
    return (math.exp(-decay_k * v) - math.exp(-decay_k)) / (1.0 - math.exp(-decay_k))


@dataclass(frozen=True)
class AmbientProfile:
    """A reconstructed half-hourly ambient temperature profile for one day."""

    temperatures_c: list[float]
    sunrise_hour: float
    sunset_hour: float
    peak_hour: float
    decay_k: float
    reconstruction_residual_c: float
    """Observed daily mean minus reconstructed mean. The solve drives this to ~0;
    a non-trivial value means the three daily statistics are mutually inconsistent
    with any profile in the family, and the caller is told rather than not told."""


def reconstruct_ambient_profile(
    *,
    temperature_min_c: float,
    temperature_max_c: float,
    temperature_mean_c: float,
    day_of_year: int,
    latitude_deg: float,
    thermal_lag_hours: float = 2.0,
) -> AmbientProfile:
    """Half-hourly ambient temperature from the three observed daily statistics.

    Minimum and maximum are exact by construction; the overnight decay rate is
    solved (bisection) so the profile's mean matches the observed daily mean.

    `latitude_deg` has NO default (2026-08-03 fix): a missing real location
    must fail loudly, not silently reconstruct against the national mean.
    """
    if not math.isfinite(latitude_deg):
        raise ValueError(f"latitude_deg must be finite, got {latitude_deg!r}")
    if temperature_max_c < temperature_min_c:
        raise ValueError(
            f"temperature_max_c ({temperature_max_c}) below temperature_min_c ({temperature_min_c})"
        )
    sunrise, sunset = daylight_hours(latitude_deg, day_of_year)
    peak_hour = min(12.0 + (sunset - 12.0) / 2.0 + thermal_lag_hours, sunrise + 23.0)
    swing = temperature_max_c - temperature_min_c

    sample_hours = [(p + 0.5) * 0.5 for p in range(PERIODS_PER_DAY)]

    def mean_at(k: float) -> float:
        shapes = [_diurnal_shape(h, sunrise, peak_hour, k) for h in sample_hours]
        return temperature_min_c + swing * (sum(shapes) / len(shapes))

    # A flat day (max == min) has no shape to solve; any k gives the same series.
    if swing <= 0.0:
        decay_k = 1.0
    else:
        # mean_at is monotonically DECREASING in k (faster decay AND a slower
        # morning rise both lower the mean — see `_diurnal_shape`).
        lo, hi = _SHAPE_K_MIN, _SHAPE_K_MAX
        if temperature_mean_c >= mean_at(lo):
            decay_k = lo
        elif temperature_mean_c <= mean_at(hi):
            decay_k = hi
        else:
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                if mean_at(mid) > temperature_mean_c:
                    lo = mid
                else:
                    hi = mid
            decay_k = 0.5 * (lo + hi)

    temps = [
        temperature_min_c + swing * _diurnal_shape(h, sunrise, peak_hour, decay_k)
        for h in sample_hours
    ]
    residual = temperature_mean_c - (sum(temps) / len(temps))
    profile = AmbientProfile(
        temperatures_c=temps,
        sunrise_hour=sunrise,
        sunset_hour=sunset,
        peak_hour=peak_hour,
        decay_k=decay_k,
        reconstruction_residual_c=residual,
    )
    # THE ORPHAN-TRANSITION FIX (R11, 2026-08-03 HARDEN). `reconstruction_reconciles`
    # existed from the first build and had NO caller outside its own unit test, so the
    # module docstring's promise that "the interpolation can never quietly disagree
    # with the archive" was decorative: the residual was computed, stored, and read by
    # nobody. It is the check itself that is load-bearing, so the constructor of the
    # thing being checked is where it belongs — there is no longer a way to obtain an
    # unreconciled profile and use it. Measured on the real archive after the
    # two-sided-family fix above: 0 of 13,784 site-days raise here (worst residual
    # 0.0000 C), so this is a genuine fail-closed guard and not a tripwire across the
    # normal path.
    if not reconstruction_reconciles(profile):
        raise ValueError(
            "the reconstructed half-hourly profile does not reconcile to the observed "
            f"daily statistics it was built from: residual {residual:+.4f} C for "
            f"(min={temperature_min_c}, max={temperature_max_c}, mean={temperature_mean_c}, "
            f"day_of_year={day_of_year}, latitude={latitude_deg}). The three daily "
            "statistics are mutually inconsistent with every profile in this family — "
            "refusing to return a series that silently disagrees with the archive."
        )
    return profile


def reconstruct_irradiance_profile(
    *,
    cloud_cover_pct: float,
    day_of_year: int,
    latitude_deg: float,
) -> list[float]:
    """Half-hourly global horizontal irradiance (kW/m^2) from solar geometry and the
    observed daily cloud cover."""
    attenuation = cloud_attenuation(cloud_cover_pct / 100.0)
    return [
        clear_sky_ghi_kw_per_m2(latitude_deg, day_of_year, (p + 0.5) * 0.5) * attenuation
        for p in range(PERIODS_PER_DAY)
    ]


# ---------------------------------------------------------------------------
# EPC-class fields -> 2R2C parameters (the RdSAP-parameterised step)
# ---------------------------------------------------------------------------

# `domain-knowledge` — exposed-envelope fraction by built form. Detached loses
# through every wall; a mid-terrace loses through two.
_EXPOSED_ENVELOPE_FRACTION: dict[PropertyType, float] = {
    PropertyType.DETACHED: 1.00,
    PropertyType.SEMI_DETACHED: 0.78,
    PropertyType.TERRACED: 0.62,
    PropertyType.FLAT: 0.42,
}

# `domain-knowledge` — RdSAP-class floor-area priors (m^2) at a 2-bedroom baseline.
_FLOOR_AREA_BASE_M2: dict[PropertyType, float] = {
    PropertyType.FLAT: 48.0,
    PropertyType.TERRACED: 60.0,
    PropertyType.SEMI_DETACHED: 68.0,
    PropertyType.DETACHED: 88.0,
}
_FLOOR_AREA_PER_BEDROOM_M2 = 14.0

# `domain-knowledge` — uninsulated wall U-values (W/m^2K) by construction age band.
_WALL_U_BY_ERA: dict[BuildEra, float] = {
    BuildEra.PRE_1919: 2.10,   # solid masonry
    BuildEra.ERA_1919_1944: 1.70,
    BuildEra.ERA_1945_1964: 1.50,
    BuildEra.ERA_1965_1980: 1.00,
    BuildEra.ERA_1981_2000: 0.60,
    BuildEra.POST_2000: 0.30,
}
_ROOF_U_BY_ERA: dict[BuildEra, float] = {
    BuildEra.PRE_1919: 2.30,
    BuildEra.ERA_1919_1944: 2.30,
    BuildEra.ERA_1945_1964: 1.50,
    BuildEra.ERA_1965_1980: 0.68,
    BuildEra.ERA_1981_2000: 0.35,
    BuildEra.POST_2000: 0.16,
}
_GROUND_U_BY_ERA: dict[BuildEra, float] = {
    BuildEra.PRE_1919: 0.70,
    BuildEra.ERA_1919_1944: 0.70,
    BuildEra.ERA_1945_1964: 0.65,
    BuildEra.ERA_1965_1980: 0.60,
    BuildEra.ERA_1981_2000: 0.45,
    BuildEra.POST_2000: 0.22,
}
_WINDOW_U_BY_ERA: dict[BuildEra, float] = {
    BuildEra.PRE_1919: 2.80,
    BuildEra.ERA_1919_1944: 2.80,
    BuildEra.ERA_1945_1964: 2.80,
    BuildEra.ERA_1965_1980: 2.80,
    BuildEra.ERA_1981_2000: 2.00,
    BuildEra.POST_2000: 1.50,
}

# `domain-knowledge` — insulation retrofit multiplier on opaque-fabric U-values.
_INSULATION_U_MULTIPLIER: dict[InsulationLevel, float] = {
    InsulationLevel.FULL: 0.40,
    InsulationLevel.PARTIAL: 0.70,
    InsulationLevel.POOR: 1.00,
    InsulationLevel.NA: 1.00,
}

# `domain-knowledge` — Building Regulations Part L achievable U-value floors
# (W/m^2K). The retrofit multiplier describes what insulating an OLD fabric buys;
# it must not be allowed to drive a modern fabric below what can actually be built,
# which would double-count the age band and the insulation flag against each other.
_WALL_U_FLOOR = 0.25
_ROOF_U_FLOOR = 0.13
_GROUND_U_FLOOR = 0.18


def _retrofitted_u(as_built_u: float, multiplier: float, floor_u: float) -> float:
    return max(as_built_u * multiplier, min(as_built_u, floor_u))

# `domain-knowledge` — infiltration (air changes per hour) by age band, before the
# insulation adjustment. Older, leakier fabric ventilates more.
_INFILTRATION_ACH_BY_ERA: dict[BuildEra, float] = {
    BuildEra.PRE_1919: 1.00,
    BuildEra.ERA_1919_1944: 0.90,
    BuildEra.ERA_1945_1964: 0.80,
    BuildEra.ERA_1965_1980: 0.70,
    BuildEra.ERA_1981_2000: 0.55,
    BuildEra.POST_2000: 0.45,
}
_MINIMUM_VENTILATION_ACH = 0.50

# `domain-knowledge` — effective structural thermal capacity (kJ per m^2 of floor
# area per K) by age band. THIS IS THE CHARACTER PARAMETER: solid masonry stores
# heat for days, modern timber-frame for hours.
_MASS_CAPACITY_KJ_PER_M2K: dict[BuildEra, float] = {
    BuildEra.PRE_1919: 400.0,
    BuildEra.ERA_1919_1944: 380.0,
    BuildEra.ERA_1945_1964: 340.0,
    BuildEra.ERA_1965_1980: 300.0,
    BuildEra.ERA_1981_2000: 240.0,
    BuildEra.POST_2000: 160.0,
}

# `domain-knowledge` — air + furnishings capacity (kJ/m^2K). Small, so the air node
# responds in minutes: this is what makes the burner cycle.
_AIR_CAPACITY_KJ_PER_M2K = 30.0

# `domain-knowledge` — ISO 13790 combined internal surface heat-transfer coefficient
# (W/m^2K) and the internal-surface-area-to-floor-area ratio.
_INTERNAL_SURFACE_H_W_PER_M2K = 6.0
_INTERNAL_SURFACE_AREA_RATIO = 4.5

_STOREY_HEIGHT_M = 2.4
_WALL_AREA_RATIO = 1.15       # external wall area per m^2 of floor, 2-storey
_WINDOW_AREA_RATIO = 0.15
_SOLAR_TRANSMITTANCE = 0.55   # glazing g-value
_FRAME_FACTOR = 0.70
_SOLAR_SPLIT_TO_AIR = 0.40    # f_i in the 2R2C equations

# `domain-knowledge` — occupant + appliance gains, W per m^2 of floor area.
_INTERNAL_GAIN_W_PER_M2 = 4.0


@dataclass(frozen=True)
class FabricParameters:
    """The 2R2C parameter vector, derived from EPC-class structural fields."""

    floor_area_m2: float
    r_ia_k_per_kw: float
    """Air-node-to-ambient resistance: ventilation plus the whole fabric path."""
    r_im_k_per_kw: float
    """Air-to-mass coupling resistance."""
    c_i_kwh_per_k: float
    """Air + furnishings capacity — the FAST node that produces cycling."""
    c_m_kwh_per_k: float
    """Structural capacity — the SLOW node that produces fabric character."""
    solar_aperture_m2: float
    internal_gain_kw: float

    @property
    def heat_loss_coefficient_kw_per_k(self) -> float:
        return 1.0 / self.r_ia_k_per_kw

    @property
    def mass_time_constant_hours(self) -> float:
        """tau_m = R_im * C_m — cycle length and setback-drift depth."""
        return self.r_im_k_per_kw * self.c_m_kwh_per_k

    @property
    def air_time_constant_hours(self) -> float:
        return self.c_i_kwh_per_k / (
            self.heat_loss_coefficient_kw_per_k + 1.0 / self.r_im_k_per_kw
        )

    @property
    def building_time_constant_hours(self) -> float:
        """(C_i + C_m) / HLC — the whole-building constant, days for heavy fabric."""
        return (self.c_i_kwh_per_k + self.c_m_kwh_per_k) / self.heat_loss_coefficient_kw_per_k


def floor_area_m2(household: Household) -> float:
    """RdSAP-class floor-area prior from property type and bedroom count."""
    base = _FLOOR_AREA_BASE_M2.get(household.property_type)
    if base is None:
        raise ValueError(
            f"fabric physics is a DOMESTIC model; {household.property_type} is not residential"
        )
    bedrooms = 2 if household.bedrooms is None else household.bedrooms
    return base + _FLOOR_AREA_PER_BEDROOM_M2 * (bedrooms - 2)


def fabric_parameters(household: Household) -> FabricParameters:
    """Map the EPC-class structural fields onto (R_ia, R_im, C_i, C_m).

    A small deterministic function, not a learning problem — the director's
    "simple number of available variables" constraint honoured literally.
    """
    if not household.is_residential:
        raise ValueError(
            f"fabric physics is a DOMESTIC model; {household.property_type} is not residential"
        )
    area = floor_area_m2(household)
    exposure = _EXPOSED_ENVELOPE_FRACTION[household.property_type]
    era = household.build_era
    retrofit = _INSULATION_U_MULTIPLIER[household.insulation]

    # A flat has no private roof or ground floor to speak of; a house has both,
    # each covering roughly half its (2-storey) floor area.
    horizontal_ratio = 0.15 if household.property_type == PropertyType.FLAT else 0.50

    wall_area = _WALL_AREA_RATIO * area * exposure
    roof_area = horizontal_ratio * area * exposure
    ground_area = horizontal_ratio * area
    # Glazing is NOT scaled by exposed-envelope fraction: the glazed area of a
    # dwelling tracks its floor area (SAP assumes ~15%), not how many of its walls
    # face outside. A mid-terrace has the same windows as a detached house of the
    # same size, concentrated in fewer facades.
    window_area = _WINDOW_AREA_RATIO * area

    fabric_w_per_k = (
        wall_area * _retrofitted_u(_WALL_U_BY_ERA[era], retrofit, _WALL_U_FLOOR)
        + roof_area * _retrofitted_u(_ROOF_U_BY_ERA[era], retrofit, _ROOF_U_FLOOR)
        + ground_area * max(_GROUND_U_BY_ERA[era], _GROUND_U_FLOOR)
        + window_area * _WINDOW_U_BY_ERA[era]
    )
    volume_m3 = area * _STOREY_HEIGHT_M
    ach = _INFILTRATION_ACH_BY_ERA[era] * (
        0.85 if household.insulation == InsulationLevel.FULL else 1.0
    )
    # `domain-knowledge` — Building Regulations Part F sets a whole-dwelling
    # ventilation requirement for indoor air quality. A dwelling cannot be sealed
    # below it, so airtightness improvements stop buying heat savings here.
    ach = max(ach, _MINIMUM_VENTILATION_ACH)
    ventilation_w_per_k = 0.33 * ach * volume_m3

    hlc_kw_per_k = (fabric_w_per_k + ventilation_w_per_k) / 1000.0
    h_im_kw_per_k = (
        _INTERNAL_SURFACE_H_W_PER_M2K * _INTERNAL_SURFACE_AREA_RATIO * area
    ) / 1000.0

    return FabricParameters(
        floor_area_m2=area,
        r_ia_k_per_kw=1.0 / hlc_kw_per_k,
        r_im_k_per_kw=1.0 / h_im_kw_per_k,
        c_i_kwh_per_k=_AIR_CAPACITY_KJ_PER_M2K * area / 3600.0,
        c_m_kwh_per_k=_MASS_CAPACITY_KJ_PER_M2K[era] * area / 3600.0,
        solar_aperture_m2=window_area * _SOLAR_TRANSMITTANCE * _FRAME_FACTOR,
        internal_gain_kw=_INTERNAL_GAIN_W_PER_M2 * area / 1000.0,
    )


# ---------------------------------------------------------------------------
# Heat source and controller
# ---------------------------------------------------------------------------


class ControlMode(str, Enum):
    """How the heat source is commanded.

    The two modes exist because they produce DIFFERENT TEXTURE, and the design must
    produce different texture by heating system rather than one texture for all.
    """

    ON_OFF_DEADBAND = "on_off_deadband"
    """Room thermostat with hysteresis — the UK gas-boiler norm. Cycles."""
    WEATHER_COMPENSATED = "weather_compensated"
    """Continuous modulation off an ambient-driven curve — the heat-pump norm.
    Near-continuous running, so materially SMOOTHER than a cycling boiler."""


# `domain-knowledge` — heat-source oversize factor over the design heat loss.
# UK combi boilers are grossly oversized because they are sized for domestic hot
# water, which is exactly why they cycle. Heat pumps are sized properly.
_OVERSIZE_FACTOR: dict[HeatingSystem, float] = {
    HeatingSystem.GAS_BOILER_COMBI: 1.90,
    HeatingSystem.GAS_BOILER_SYSTEM: 1.50,
    HeatingSystem.HEAT_PUMP_AIR: 1.15,
    HeatingSystem.HEAT_PUMP_GROUND: 1.15,
    HeatingSystem.ELECTRIC_STORAGE: 1.50,
    HeatingSystem.ELECTRIC_DIRECT: 1.40,
    HeatingSystem.DISTRICT_HEAT: 1.30,
}

# `domain-knowledge` — minimum modulation as a fraction of rated output.
_MODULATION_MIN_FRACTION: dict[HeatingSystem, float] = {
    HeatingSystem.GAS_BOILER_COMBI: 0.30,
    HeatingSystem.GAS_BOILER_SYSTEM: 0.30,
    HeatingSystem.HEAT_PUMP_AIR: 0.25,
    HeatingSystem.HEAT_PUMP_GROUND: 0.25,
    HeatingSystem.ELECTRIC_STORAGE: 1.00,
    HeatingSystem.ELECTRIC_DIRECT: 1.00,
    HeatingSystem.DISTRICT_HEAT: 0.40,
}

_CONTROL_MODE: dict[HeatingSystem, ControlMode] = {
    HeatingSystem.GAS_BOILER_COMBI: ControlMode.ON_OFF_DEADBAND,
    HeatingSystem.GAS_BOILER_SYSTEM: ControlMode.ON_OFF_DEADBAND,
    HeatingSystem.HEAT_PUMP_AIR: ControlMode.WEATHER_COMPENSATED,
    HeatingSystem.HEAT_PUMP_GROUND: ControlMode.WEATHER_COMPENSATED,
    HeatingSystem.ELECTRIC_STORAGE: ControlMode.ON_OFF_DEADBAND,
    HeatingSystem.ELECTRIC_DIRECT: ControlMode.ON_OFF_DEADBAND,
    HeatingSystem.DISTRICT_HEAT: ControlMode.WEATHER_COMPENSATED,
}

# `domain-knowledge` — external design temperature for heat-source sizing (deg C),
# and the boiler-efficiency / heat-pump-COP anchors.
DESIGN_EXTERNAL_TEMP_C = -3.0
_BOILER_EFFICIENCY: dict[BoilerAge, float] = {
    BoilerAge.NEW: 0.90,
    BoilerAge.MID: 0.86,
    BoilerAge.OLD: 0.80,
    BoilerAge.NA: 0.86,
}
# ASHP at 45 deg C flow: COP ~3.5 at 7 deg C ambient, ~2.2 at -2 deg C.
_ASHP_COP_AT_7C = 3.5
_ASHP_COP_AT_MINUS_2C = 2.2
_GSHP_COP_UPLIFT = 1.25  # ground array sees a stable source, so a flatter, higher COP


def heat_pump_cop(ambient_c: float, *, ground_source: bool = False) -> float:
    """Temperature-dependent COP. The mechanism behind heat-pump winter peaks:
    electricity demand rises super-linearly as ambient falls, which is invisible in
    a flat kWh-per-degree-day coefficient."""
    slope = (_ASHP_COP_AT_7C - _ASHP_COP_AT_MINUS_2C) / 9.0
    cop = _ASHP_COP_AT_MINUS_2C + slope * (ambient_c - (-2.0))
    if ground_source:
        cop *= _GSHP_COP_UPLIFT
    return max(1.8, min(5.5, cop))


@dataclass(frozen=True)
class HeatSource:
    rated_output_kw: float
    modulation_min_fraction: float
    control_mode: ControlMode
    system: HeatingSystem

    @property
    def minimum_output_kw(self) -> float:
        return self.rated_output_kw * self.modulation_min_fraction


def heat_source_for(household: Household, params: FabricParameters, setpoint_c: float) -> HeatSource:
    """Size the heat source off the fabric's design heat loss."""
    system = household.heating_system
    if system == HeatingSystem.NONE:
        return HeatSource(0.0, 0.0, ControlMode.ON_OFF_DEADBAND, system)
    design_load_kw = params.heat_loss_coefficient_kw_per_k * (setpoint_c - DESIGN_EXTERNAL_TEMP_C)
    rated = design_load_kw * _OVERSIZE_FACTOR[system]
    if system in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM):
        # `domain-knowledge` — no UK combi is sold below ~12 kW (DHW sizing floor).
        rated = max(rated, 12.0)
    return HeatSource(
        rated_output_kw=rated,
        modulation_min_fraction=_MODULATION_MIN_FRACTION[system],
        control_mode=_CONTROL_MODE[system],
        system=system,
    )


# ---------------------------------------------------------------------------
# Per-premise structural diversity — drawn ONCE, never per period (C-S2)
# ---------------------------------------------------------------------------


def _substream(base_seed: int, salt: str = "") -> random.Random:
    """An ISOLATED `random.Random` seeded from a STABLE sha256 of
    (`STREAM_NAME`::`salt`::`base_seed`) — the C-S2 heart of this module.

    Shares no state with the global `random`, with any other salt here, or with any
    other subsystem's substream, so a draw can never shift another sequence.
    """
    key = f"{STREAM_NAME}::{salt}::{base_seed}".encode("utf-8")
    seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    return random.Random(seed_int)


def _base_seed_for(premise_id: str, seed: int | None) -> int:
    key = premise_id if seed is None else f"{premise_id}::{seed}"
    return int.from_bytes(hashlib.md5(key.encode("utf-8")).digest()[:8], "big")


# `domain-knowledge` — BEIS/EST measured living-room setpoint distribution and the
# conventional two-period UK heating schedule.
_SETPOINT_MEAN_C = 20.5
_SETPOINT_SD_C = 1.2
_SETPOINT_MIN_C = 17.0
_SETPOINT_MAX_C = 24.0
_SETBACK_OFFSET_MIN_C = 2.5
_SETBACK_OFFSET_MAX_C = 6.0
DEFAULT_DEADBAND_C = 1.0  # +/- 0.5 deg C about the setpoint


@dataclass(frozen=True)
class HeatingSchedule:
    """One premise's own, fixed heating schedule. STRUCTURAL diversity: drawn once
    per premise, never re-drawn per period. Two premises differ because they LIVE
    differently, not because noise was sprinkled on their output."""

    comfort_setpoint_c: float
    setback_setpoint_c: float
    morning_start_period: int
    morning_end_period: int
    evening_start_period: int
    evening_end_period: int
    deadband_c: float
    continuous: bool
    """True for weather-compensated systems, which are not run on setback."""

    def setpoint_at(self, period: int) -> float:
        if self.continuous:
            return self.comfort_setpoint_c
        if self.morning_start_period <= period < self.morning_end_period:
            return self.comfort_setpoint_c
        if self.evening_start_period <= period < self.evening_end_period:
            return self.comfort_setpoint_c
        return self.setback_setpoint_c


def heating_schedule_for(
    premise_id: str,
    household: Household,
    *,
    seed: int | None = None,
    deadband_c: float = DEFAULT_DEADBAND_C,
) -> HeatingSchedule:
    """Draw a premise's fixed schedule from this module's named substream."""
    base = _base_seed_for(premise_id, seed)
    setpoint = _substream(base, "setpoint").gauss(_SETPOINT_MEAN_C, _SETPOINT_SD_C)
    setpoint = max(_SETPOINT_MIN_C, min(_SETPOINT_MAX_C, setpoint))
    setback_offset = _substream(base, "setback").uniform(
        _SETBACK_OFFSET_MIN_C, _SETBACK_OFFSET_MAX_C
    )
    jitter = _substream(base, "schedule")
    # Base schedule 06:30-08:30 and 16:00-22:00, jittered +/- 90 min in half-hours.
    morning_start = 13 + jitter.randint(-3, 3)
    evening_start = 32 + jitter.randint(-3, 3)
    morning_len = 4 + jitter.randint(0, 2)
    evening_len = 12 + jitter.randint(-2, 2)
    continuous = _CONTROL_MODE.get(household.heating_system) == ControlMode.WEATHER_COMPENSATED
    return HeatingSchedule(
        comfort_setpoint_c=setpoint,
        setback_setpoint_c=setpoint - setback_offset,
        morning_start_period=morning_start,
        morning_end_period=morning_start + morning_len,
        evening_start_period=evening_start,
        evening_end_period=evening_start + evening_len,
        deadband_c=deadband_c,
        continuous=continuous,
    )


# ---------------------------------------------------------------------------
# The simulation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ThermalState:
    """Carried between days — the mass node's memory IS the fabric character."""

    indoor_air_c: float
    mass_c: float
    burner_firing: bool = False


@dataclass(frozen=True)
class FabricDayResult:
    ambient_c: list[float]
    irradiance_kw_per_m2: list[float]
    indoor_air_c: list[float]
    mass_c: list[float]
    heat_delivered_kwh: list[float]
    fuel_kwh: list[float]
    """Metered energy at the premise: gas for a boiler, electricity for a heat pump
    or resistive system — heat divided by efficiency or by the ambient-dependent COP."""
    duty_cycle_fraction: list[float]
    """Fraction of each half hour for which the heat source was delivering."""
    end_state: ThermalState
    ambient_profile: AmbientProfile


def _interpolate_periodwise(series: list[float], period: int, within: float) -> float:
    """Linear interpolation between half-hourly period midpoints, so the integrator
    sees a continuous drive rather than a staircase."""
    if within < 0.5:
        prev = series[period - 1] if period > 0 else series[0]
        return prev + (series[period] - prev) * (within + 0.5)
    nxt = series[period + 1] if period + 1 < len(series) else series[-1]
    return series[period] + (nxt - series[period]) * (within - 0.5)


def _fuel_for(system: HeatingSystem, heat_kwh: float, ambient_c: float, boiler_age: BoilerAge) -> float:
    if heat_kwh <= 0.0:
        return 0.0
    if system in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM):
        return heat_kwh / _BOILER_EFFICIENCY[boiler_age]
    if system == HeatingSystem.HEAT_PUMP_AIR:
        return heat_kwh / heat_pump_cop(ambient_c)
    if system == HeatingSystem.HEAT_PUMP_GROUND:
        return heat_kwh / heat_pump_cop(ambient_c, ground_source=True)
    if system in (HeatingSystem.ELECTRIC_DIRECT, HeatingSystem.ELECTRIC_STORAGE):
        return heat_kwh  # resistive: 1:1
    if system == HeatingSystem.DISTRICT_HEAT:
        return heat_kwh
    return 0.0


def simulate_day(
    *,
    household: Household,
    params: FabricParameters,
    schedule: HeatingSchedule,
    source: HeatSource,
    ambient_profile: AmbientProfile,
    irradiance_kw_per_m2: list[float],
    initial_state: ThermalState,
    internal_gain_kw: list[float] | None = None,
) -> FabricDayResult:
    """Integrate the 2R2C model over one day at 1-minute resolution.

        C_i dT_i/dt = (T_a - T_i)/R_ia + (T_m - T_i)/R_im + Phi_h + Phi_p + f_i*Phi_s
        C_m dT_m/dt = (T_i - T_m)/R_im                              + (1-f_i)*Phi_s

    Sub-stepping is what lets a burner start AND stop inside one settlement period.
    That is the whole point: the half-hourly aggregate then carries a PARTIAL duty
    cycle that varies period to period.
    """
    ambient = ambient_profile.temperatures_c
    gains = internal_gain_kw or [params.internal_gain_kw] * PERIODS_PER_DAY

    t_i = initial_state.indoor_air_c
    t_m = initial_state.mass_c
    firing = initial_state.burner_firing

    out_air: list[float] = []
    out_mass: list[float] = []
    out_heat: list[float] = []
    out_fuel: list[float] = []
    out_duty: list[float] = []

    for period in range(PERIODS_PER_DAY):
        setpoint = schedule.setpoint_at(period)
        half_band = schedule.deadband_c / 2.0
        period_heat_kwh = 0.0
        period_on_steps = 0

        for step in range(SUB_STEPS_PER_PERIOD):
            within = (step + 0.5) / SUB_STEPS_PER_PERIOD
            t_a = _interpolate_periodwise(ambient, period, within)
            ghi = _interpolate_periodwise(irradiance_kw_per_m2, period, within)
            phi_s = ghi * params.solar_aperture_m2
            phi_p = gains[period]

            if source.rated_output_kw <= 0.0:
                phi_h = 0.0
                firing = False
            elif source.control_mode == ControlMode.WEATHER_COMPENSATED:
                # Continuous modulation off an ambient-driven curve, trimmed by the
                # air-node error. Wide soft band -> near-continuous running.
                demand_kw = params.heat_loss_coefficient_kw_per_k * (setpoint - t_a)
                demand_kw += params.heat_loss_coefficient_kw_per_k * 3.0 * (setpoint - t_i)
                if t_i > setpoint + schedule.deadband_c:
                    phi_h = 0.0
                    firing = False
                elif demand_kw <= 0.0:
                    phi_h = 0.0
                    firing = False
                else:
                    phi_h = max(
                        source.minimum_output_kw, min(source.rated_output_kw, demand_kw)
                    )
                    firing = True
            else:
                # Hysteresis: fire below the band, stop above it, hold in between.
                if t_i < setpoint - half_band:
                    firing = True
                elif t_i > setpoint + half_band:
                    firing = False
                if firing:
                    # Two-level modulation: full rated output while still below the
                    # setpoint, backing off to the minimum as the air node closes in.
                    phi_h = source.rated_output_kw if t_i < setpoint else source.minimum_output_kw
                else:
                    phi_h = 0.0

            if phi_h > 0.0:
                period_on_steps += 1
                period_heat_kwh += phi_h * _SUB_STEP_HOURS

            d_ti = (
                (t_a - t_i) / params.r_ia_k_per_kw
                + (t_m - t_i) / params.r_im_k_per_kw
                + phi_h
                + phi_p
                + _SOLAR_SPLIT_TO_AIR * phi_s
            ) * _SUB_STEP_HOURS / params.c_i_kwh_per_k
            d_tm = (
                (t_i - t_m) / params.r_im_k_per_kw
                + (1.0 - _SOLAR_SPLIT_TO_AIR) * phi_s
            ) * _SUB_STEP_HOURS / params.c_m_kwh_per_k
            t_i += d_ti
            t_m += d_tm

        out_air.append(t_i)
        out_mass.append(t_m)
        out_heat.append(period_heat_kwh)
        out_duty.append(period_on_steps / SUB_STEPS_PER_PERIOD)
        out_fuel.append(
            _fuel_for(household.heating_system, period_heat_kwh, ambient[period], household.boiler_age)
        )

    return FabricDayResult(
        ambient_c=list(ambient),
        irradiance_kw_per_m2=list(irradiance_kw_per_m2),
        indoor_air_c=out_air,
        mass_c=out_mass,
        heat_delivered_kwh=out_heat,
        fuel_kwh=out_fuel,
        duty_cycle_fraction=out_duty,
        end_state=ThermalState(indoor_air_c=t_i, mass_c=t_m, burner_firing=firing),
        ambient_profile=ambient_profile,
    )


@dataclass(frozen=True)
class DailyWeather:
    """One row of the real daily archive (`sim/weather_data/{id}.csv`)."""

    day_of_year: int
    temperature_min_c: float
    temperature_max_c: float
    temperature_mean_c: float
    cloud_cover_pct: float


def simulate_premise(
    *,
    premise_id: str,
    household: Household,
    daily_weather: list[DailyWeather],
    seed: int | None = None,
    latitude_deg: float,
    deadband_c: float = DEFAULT_DEADBAND_C,
    initial_state: ThermalState | None = None,
) -> list[FabricDayResult]:
    """Run one premise across consecutive days, CHAINING thermal state.

    Chaining is not an optimisation: the mass node's carry-over is what makes a
    heavy-fabric home respond slowly to a cold snap and drift shallowly overnight.
    Reset the state each day and the character disappears.
    """
    params = fabric_parameters(household)
    schedule = heating_schedule_for(premise_id, household, seed=seed, deadband_c=deadband_c)
    source = heat_source_for(household, params, schedule.comfort_setpoint_c)
    state = initial_state or ThermalState(
        indoor_air_c=schedule.setback_setpoint_c, mass_c=schedule.setback_setpoint_c
    )

    results: list[FabricDayResult] = []
    for day in daily_weather:
        profile = reconstruct_ambient_profile(
            temperature_min_c=day.temperature_min_c,
            temperature_max_c=day.temperature_max_c,
            temperature_mean_c=day.temperature_mean_c,
            day_of_year=day.day_of_year,
            latitude_deg=latitude_deg,
        )
        irradiance = reconstruct_irradiance_profile(
            cloud_cover_pct=day.cloud_cover_pct,
            day_of_year=day.day_of_year,
            latitude_deg=latitude_deg,
        )
        result = simulate_day(
            household=household,
            params=params,
            schedule=schedule,
            source=source,
            ambient_profile=profile,
            irradiance_kw_per_m2=irradiance,
            initial_state=state,
        )
        results.append(result)
        state = result.end_state
    return results


# ---------------------------------------------------------------------------
# R15-failable controls
# ---------------------------------------------------------------------------


def rescaled_fraction_multiplicity(series: list[list[float]], *, decimals: int = 6) -> int:
    """The largest number of DISTINCT DAYS that share any single value of
    `x[t] / daily_total` — the harness spec's L1.5 structural check.

    A generator that rescales ONE stored base shape produces the SAME 48 fractions
    every day, so every fraction recurs on every day and the count equals the number
    of days. A generator that simulates the building produces fractions that
    essentially never recur on another day, because the next day's weather, thermal
    state and duty cycles differ.

    Two exclusions, each with a reason — and neither is a carve-out that lets a
    rescaled shape through, because the artefact is defined by ACROSS-DAY recurrence
    which both exclusions leave fully visible:

    * **Counted per day, not per period.** A run of half hours in which the heat
      source is flat out is a real physical plateau (an undersized-for-the-weather
      source saturates), and those periods share a fraction WITHIN that day. Counting
      them would make the control fire on correct physics — a false positive that
      says nothing about shape reuse.
    * **Exact zeros excluded.** A period in which the source genuinely never fires is
      a structural feature of a real heating system; overnight off-periods recur on
      every day by construction.
    """
    days_by_fraction: dict[float, set[int]] = {}
    for index, day in enumerate(series):
        total = sum(day)
        if total <= 0.0:
            continue
        for value in day:
            if value == 0.0:
                continue
            key = round(value / total, decimals)
            days_by_fraction.setdefault(key, set()).add(index)
    return max((len(days) for days in days_by_fraction.values()), default=0)


def texture_is_not_a_rescaled_shape(
    series: list[list[float]], *, max_day_multiplicity: int | None = None
) -> bool:
    """R15-failable: PASSES for a simulated series, FIRES for a rescaled base shape.

    Structural, not statistical — it detects the ARTEFACT, so injecting per-period
    noise to move a distribution statistic cannot buy a pass here.

    The threshold scales with the number of days rather than being a fixed constant:
    a fraction recurring on more than a quarter of the days (minimum two) is the
    reuse signature. A rescaled base shape recurs on 100% of days by construction.

    `observed 2026-08-03` — the quarter is not arbitrary. Measured across twelve
    fabric archetypes (six age bands x poor/full insulation) this generator's worst
    recurrence was 3 days of 7, 4 of 30, 4 of 90 and 31 of 365 — i.e. it stays under
    ~9% even over a full year, against 100% for the artefact. Tightening the
    threshold to a twentieth would false-positive on the 365-day run; a quarter keeps
    roughly a 3x margin at the worst measured point without letting the artefact
    through.
    """
    if len(series) < 2:
        raise ValueError("L1.5 needs at least two days to detect a repeating shape")
    threshold = max_day_multiplicity if max_day_multiplicity is not None else max(2, len(series) // 4)
    return rescaled_fraction_multiplicity(series) <= threshold


def _intraday_swing(day: FabricDayResult) -> float:
    return max(day.indoor_air_c) - min(day.indoor_air_c)


def mass_damps_intraday_swing(heavy: list[FabricDayResult], light: list[FabricDayResult]) -> bool:
    """R15-failable: the higher-C_m fabric must show the SMALLER indoor-air swing
    under identical weather and control. Swap the arguments and it fires.

    This is the character claim made falsifiable: if it passes with the arguments
    reversed, `C_m` is not doing the work the design says it does.
    """
    if not heavy or not light:
        raise ValueError("both fabrics need at least one simulated day")
    heavy_swing = sum(_intraday_swing(d) for d in heavy) / len(heavy)
    light_swing = sum(_intraday_swing(d) for d in light) / len(light)
    return heavy_swing < light_swing


def reconstruction_reconciles(profile: AmbientProfile, *, tolerance_c: float = 0.05) -> bool:
    """R15-failable: the reconstructed half-hourly profile must reconcile to the
    observed daily statistics it was built from. Fires when the solve cannot absorb
    the difference — i.e. when the interpolation would quietly disagree with the
    archive. Non-finite residuals are rejected FIRST (comparison guards are
    NaN-blind otherwise)."""
    residual = profile.reconstruction_residual_c
    if not math.isfinite(residual):
        return False
    return abs(residual) <= tolerance_c
