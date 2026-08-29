"""Phase 35b: Gas forward scenario price generator.

Generates synthetic daily NBP gas price records for 2026–2030 forward scenarios,
calibrated to observed UK gas market dynamics and correlated with the electricity
regime (gas demand and price both rise when gas generation fraction is high).

Gas prices follow a single-regime log-normal distribution (no bimodal signature —
gas pricing is dominated by global LNG/storage/seasonal demand rather than merit
order displacement). However, gas prices are regime-conditioned: higher when
electricity is in the upper mode (gas-marginal pricing), lower when renewable-rich.

Output: list of {"settlementDate": str, "systemSellPrice": float} dicts, same
structure as the NBP records used in sim/gas_prices_history.py. Drop-in compatible.

SPINE_1 CONSUMPTION SEAM (FRAME §A.4)
-------------------------------------
This is the FIRST generator to actually consume :meth:`ScenarioSpine.paths_as_of`. Before
this, the spine resolved and bound but nothing read it, so no run ever LIVED through a
non-baseline world -- the accessor had zero production callers and the whole curriculum was
inert (recorded as the open item on SPINE_1's own simplification record).

The spine supplies ``gas_trend`` as an absolute LEVEL in p/therm (director curriculum, R13).
This generator's parameters are regime means in GBP/MWh. The two reconcile through a
published physical constant, not a fitted factor: 1 therm = 29.3071 kWh, so 84 p/therm
(DESNZ Assumption B, 2024) = GBP 28.66/MWh against the generator's own ``baseline_2025``
upper-regime mean of GBP 28.0/MWh. That agreement is a check on the seam, not a calibration
of it -- nothing here was tuned to produce it.

R13 SPLIT, held mechanically: the MAPPING (level-anchoring, below) is SIM mechanism and is
the agent's; every VALUE it reads comes from a committed director-authored artefact. This
module contains no scenario magnitude.

BASELINE DORMANCY: ``spine=None``, or any world whose ``gas_trend`` is ``NO_OVERRIDE`` (which
is every field of the default ``history_replay``), takes an explicit untouched-parameter
branch -- not a multiply-by-1.0. Byte-identity is then structural rather than a floating-point
argument, and the scaling branch is unreachable without a real override.
"""

import random
from dataclasses import dataclass, replace

from sim.scenario.spine import NO_OVERRIDE

# 1 therm = 100,000 BTU = 105.505585262 MJ = 29.3071 kWh (published definition, not fitted).
# Used ONLY to express a director-authored p/therm level in this generator's GBP/MWh units.
THERM_KWH = 29.3071


@dataclass
class GasScenarioParams:
    """Parameters for one gas forward scenario.

    All prices in £/MWh. NBP SAP-equivalent units.
    2016-2024 historical range: ~15-350 £/MWh (2021-22 crisis peak ~350).
    Post-crisis normalisation: 20-60 £/MWh expected 2025-2030.
    """
    # Gas price in high-electricity-demand (upper-mode, high-gas-fraction) regime
    upper_regime_mean: float = 30.0
    upper_regime_std: float = 6.0

    # Gas price in low-electricity-demand (lower-mode, renewable-rich) regime
    lower_regime_mean: float = 22.0
    lower_regime_std: float = 5.0

    # Fraction of days in lower (renewable-rich) electricity regime — must match
    # the electricity scenario's lower_mode_fraction for consistent coupling.
    lower_mode_fraction: float = 0.50

    # Dunkelflaute gas premium (multiplier over upper_regime_mean)
    dunkelflaute_gas_multiplier_mean: float = 1.5
    dunkelflaute_gas_multiplier_std: float = 0.2

    # Dunkelflaute events per year (should match electricity scenario)
    dunkelflaute_events_per_year: float = 5.0
    dunkelflaute_min_days: int = 1
    dunkelflaute_max_days: int = 3

    # Gas price floor (negative gas prices are not realistic)
    price_floor: float = 5.0


GAS_SCENARIOS: dict[str, GasScenarioParams] = {
    "baseline_2025": GasScenarioParams(
        upper_regime_mean=28.0, upper_regime_std=7.0,
        lower_regime_mean=20.0, lower_regime_std=5.0,
        lower_mode_fraction=0.45,
        dunkelflaute_events_per_year=4.0,
    ),

    # 2027 central: gas demand reduced by renewables; global LNG keeps floor ~£20
    "central_2027": GasScenarioParams(
        upper_regime_mean=30.0, upper_regime_std=6.0,
        lower_regime_mean=20.0, lower_regime_std=5.0,
        lower_mode_fraction=0.55,
        dunkelflaute_events_per_year=5.0,
    ),

    # 2027 stress: prolonged dunkelflaute → sustained high gas demand and price
    "stress_dunkelflaute_2027": GasScenarioParams(
        upper_regime_mean=38.0, upper_regime_std=10.0,
        lower_regime_mean=22.0, lower_regime_std=6.0,
        lower_mode_fraction=0.58,
        dunkelflaute_gas_multiplier_mean=2.0,
        dunkelflaute_events_per_year=9.0,
        dunkelflaute_min_days=2,
        dunkelflaute_max_days=5,
    ),

    # 2027 low-renewables: more gas-fired generation → higher baseline gas demand
    "low_renewables_2027": GasScenarioParams(
        upper_regime_mean=35.0, upper_regime_std=7.0,
        lower_regime_mean=26.0, lower_regime_std=5.0,
        lower_mode_fraction=0.42,
        dunkelflaute_events_per_year=3.0,
    ),

    # 2029 battery-saturated: batteries absorb gas demand spikes; lower volatility
    "battery_saturation_2029": GasScenarioParams(
        upper_regime_mean=25.0, upper_regime_std=5.0,
        lower_regime_mean=18.0, lower_regime_std=4.0,
        lower_mode_fraction=0.60,
        dunkelflaute_gas_multiplier_mean=1.3,
        dunkelflaute_events_per_year=5.0,
    ),
}


class GasScenarioLevelError(ValueError):
    """Raised when a scenario/curriculum pair cannot be level-anchored (fail-CLOSED)."""


def p_per_therm_to_gbp_per_mwh(p_per_therm: float) -> float:
    """Convert a p/therm level (curriculum units) to GBP/MWh (this generator's units)."""
    return (p_per_therm / 100.0) * (1000.0 / THERM_KWH)


def implied_regime_mean(params: GasScenarioParams) -> float:
    """The unscaled annual mean this parameter set produces, under the regime mixture.

    Dunkelflaute is deliberately EXCLUDED: it is an event premium applied on top of the
    upper regime, not part of the base level the curriculum is anchoring. Including it
    would make the anchor depend on event frequency, so raising a world's gas trend would
    silently also re-weight its storm days.
    """
    f = params.lower_mode_fraction
    return f * params.lower_regime_mean + (1.0 - f) * params.upper_regime_mean


def level_scaled_params(params: GasScenarioParams, gas_trend_p_per_therm) -> GasScenarioParams:
    """Re-anchor ``params`` so its mixture mean equals the curriculum's gas level.

    Both regime means AND both regime standard deviations are scaled by the same ratio,
    which holds the coefficient of variation fixed. Scaling the means alone would make a
    crisis world quieter in relative terms than the baseline -- the opposite of the 2021-22
    record this curriculum exists to replay.

    ``price_floor`` is NOT scaled: it encodes "negative gas prices are not realistic", an
    absolute physical statement about the commodity rather than a property of the level.

    Fail-CLOSED, never fail-open-to-unscaled: a non-positive curriculum level or a
    non-positive anchor raises. Returning ``params`` unchanged on a malformed level would
    run the baseline world while the manifest claims a crisis, which is the same
    fail-silent mislabel ``resolve_grid_label`` already refuses.
    """
    level = float(gas_trend_p_per_therm)
    if not level > 0:
        raise GasScenarioLevelError(
            f"curriculum gas_trend={gas_trend_p_per_therm!r} is not a positive p/therm level "
            "-- refusing to fall back to the unscaled scenario, which would generate baseline "
            "gas prices while the run claims a non-baseline world"
        )
    anchor = implied_regime_mean(params)
    if not anchor > 0:
        raise GasScenarioLevelError(
            f"scenario params have a non-positive implied mixture mean ({anchor!r}); "
            "there is no level to re-anchor from"
        )
    ratio = p_per_therm_to_gbp_per_mwh(level) / anchor
    return replace(
        params,
        upper_regime_mean=params.upper_regime_mean * ratio,
        upper_regime_std=params.upper_regime_std * ratio,
        lower_regime_mean=params.lower_regime_mean * ratio,
        lower_regime_std=params.lower_regime_std * ratio,
    )


def generate_gas_scenario_prices(
    year_from: int,
    year_to: int,
    scenario: str | GasScenarioParams = "central_2027",
    seed: str = "gas_scenario",
    spine=None,
) -> list[dict]:
    """Generate synthetic daily NBP gas price records for a forward scenario.

    year_from, year_to: inclusive year range.
    scenario: named preset from GAS_SCENARIOS or a GasScenarioParams instance.
    seed: string seed for reproducibility. Use the same seed as the electricity
          scenario to get consistent regime coupling (the Markov chain uses the
          same seed-derived PRNG).
    spine: optional :class:`~sim.scenario.spine.ScenarioSpine` (SPINE_1). When given, the
          world's ``gas_trend`` path re-anchors the regime level day by day, read through
          ``paths_as_of`` so it is Blindfold-clean by construction -- day *t* never sees an
          anchor dated after *t*. ``None``, or a world with no ``gas_trend`` override,
          leaves every parameter untouched.

    Returns list of {"settlementDate": str, "systemSellPrice": float}, one per
    calendar day in [year_from-01-01, year_to-12-31], sorted by settlementDate.

    RNG-NEUTRALITY (FRAME §A.2 "adding the spine shifts no existing draw"): the spine
    changes only the ARGUMENTS to ``rng.gauss``, never the number or order of draws, so a
    world override moves the price level without resequencing the stream.
    """
    from datetime import date, timedelta

    if isinstance(scenario, str):
        if scenario not in GAS_SCENARIOS:
            raise ValueError(f"Unknown gas scenario '{scenario}'. Available: {sorted(GAS_SCENARIOS)}")
        params = GAS_SCENARIOS[scenario]
    else:
        params = scenario

    # Use distinct sub-seed for gas to avoid repeating electricity's exact sequence,
    # while still being deterministically coupled via shared scenario and year range.
    rng = random.Random(f"gas_{seed}_{year_from}_{year_to}_{scenario if isinstance(scenario, str) else 'custom'}")

    start = date(year_from, 1, 1)
    end = date(year_to, 12, 31)
    total_days = (end - start).days + 1

    # Dunkelflaute scheduling (same approach as electricity generator — same event structure
    # means coupled dunkelflaute pressure on both commodities).
    dunkelflaute_events_total = max(0, int(round(params.dunkelflaute_events_per_year * (total_days / 365.25))))
    dunkelflaute_day_indices: set[int] = set()
    safe_range = total_days - params.dunkelflaute_max_days
    if dunkelflaute_events_total > 0 and safe_range > dunkelflaute_events_total:
        start_indices = rng.sample(range(safe_range), min(dunkelflaute_events_total, safe_range))
        for start_idx in start_indices:
            duration = rng.randint(params.dunkelflaute_min_days, params.dunkelflaute_max_days)
            for d in range(duration):
                dunkelflaute_day_indices.add(start_idx + d)

    # Regime state: shared with electricity via same lower_mode_fraction
    # (gas regime state follows electricity regime probabilistically)
    in_lower_regime = rng.random() < params.lower_mode_fraction

    # SPINE_1 consumption cache: the curriculum's gas_trend is a step path with a handful of
    # anchors, so resolve each distinct level once rather than rebuilding params 1,800 times.
    _level_cache: dict = {}

    def _params_for(day: "date") -> GasScenarioParams:
        """The parameters in force on ``day`` under the selected world.

        The no-override branch returns the ORIGINAL object, so the baseline path performs no
        arithmetic on any parameter at all -- byte-identity is structural, not a float claim.
        """
        if spine is None:
            return params
        level = spine.paths_as_of(day)["gas_trend"]
        if level is NO_OVERRIDE:
            return params
        if level not in _level_cache:
            _level_cache[level] = level_scaled_params(params, level)
        return _level_cache[level]

    records = []
    for day_idx in range(total_days):
        current_date = start + timedelta(days=day_idx)
        day_params = _params_for(current_date)

        # Regime transition (simple Bernoulli each day — less persistent than electricity
        # because gas can respond faster to storage draws than grid mix changes)
        in_lower_regime = rng.random() < day_params.lower_mode_fraction

        if in_lower_regime:
            price = rng.gauss(day_params.lower_regime_mean, day_params.lower_regime_std)
        else:
            price = rng.gauss(day_params.upper_regime_mean, day_params.upper_regime_std)

        if day_idx in dunkelflaute_day_indices:
            multiplier = max(1.0, rng.gauss(
                day_params.dunkelflaute_gas_multiplier_mean, day_params.dunkelflaute_gas_multiplier_std
            ))
            base = rng.gauss(day_params.upper_regime_mean, day_params.upper_regime_std)
            price = base * multiplier

        price = max(params.price_floor, price)

        records.append({
            "settlementDate": current_date.isoformat(),
            "systemSellPrice": round(price, 4),
        })

    return records
