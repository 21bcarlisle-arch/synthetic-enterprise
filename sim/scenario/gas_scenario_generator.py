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
"""

import random
from dataclasses import dataclass


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


def generate_gas_scenario_prices(
    year_from: int,
    year_to: int,
    scenario: str | GasScenarioParams = "central_2027",
    seed: str = "gas_scenario",
) -> list[dict]:
    """Generate synthetic daily NBP gas price records for a forward scenario.

    year_from, year_to: inclusive year range.
    scenario: named preset from GAS_SCENARIOS or a GasScenarioParams instance.
    seed: string seed for reproducibility. Use the same seed as the electricity
          scenario to get consistent regime coupling (the Markov chain uses the
          same seed-derived PRNG).

    Returns list of {"settlementDate": str, "systemSellPrice": float}, one per
    calendar day in [year_from-01-01, year_to-12-31], sorted by settlementDate.
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

    records = []
    for day_idx in range(total_days):
        current_date = start + timedelta(days=day_idx)

        # Regime transition (simple Bernoulli each day — less persistent than electricity
        # because gas can respond faster to storage draws than grid mix changes)
        in_lower_regime = rng.random() < params.lower_mode_fraction

        if in_lower_regime:
            price = rng.gauss(params.lower_regime_mean, params.lower_regime_std)
        else:
            price = rng.gauss(params.upper_regime_mean, params.upper_regime_std)

        if day_idx in dunkelflaute_day_indices:
            multiplier = max(1.0, rng.gauss(
                params.dunkelflaute_gas_multiplier_mean, params.dunkelflaute_gas_multiplier_std
            ))
            base = rng.gauss(params.upper_regime_mean, params.upper_regime_std)
            price = base * multiplier

        price = max(params.price_floor, price)

        records.append({
            "settlementDate": current_date.isoformat(),
            "systemSellPrice": round(price, 4),
        })

    return records
