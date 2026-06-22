"""Phase 35a: Forward scenario price generator — bimodal distribution at high renewables penetration.

Generates synthetic daily spot price records for 2026–2030+ UK electricity scenarios,
calibrated to the R&D findings in docs/market_research/price_distribution_high_renewables_2027.md.

Two-regime model:
  - Regime 0 (high gas fraction >50%): upper mode ~£100-130/MWh — gas-marginal-cost pricing.
  - Regime 1 (low gas fraction <20%): lower mode ~£30-60/MWh — renewable-depressed pricing.

Three special event overlays:
  - Negative price days: ~7-28 days/year (calibrated to 165-1000 negative hours/year at ~6h/event).
  - Dunkelflaute spells: 2-10 events/year, 1-3 days, upper mode × 1.5-2.5 price premium.
  - Crisis spikes: rare (< 1/year average), drawn from extreme upper tail.

Regime switching uses a first-order Markov chain; transition probabilities are set so the
long-run fraction of low-gas hours matches the scenario's target split.

Output: list of {"settlementDate": str, "systemSellPrice": float} dicts, same shape as
the historical price records used throughout the simulation. Drop-in compatible.
"""

import math
import random
from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class ScenarioParams:
    """Parameters for one forward scenario year.

    All prices in £/MWh. Calibrated to R&D research (June 2026).
    """
    # Upper mode: gas-marginal pricing (high-gas-fraction hours)
    upper_mode_mean: float = 120.0
    upper_mode_std: float = 20.0

    # Lower mode: renewable-suppressed pricing (low-gas-fraction hours)
    lower_mode_mean: float = 50.0
    lower_mode_std: float = 18.0

    # Long-run fraction of days in lower (renewable-rich) regime.
    # 2025 observed ~45% low-gas hours; 2027 central: ~55%.
    lower_mode_fraction: float = 0.50

    # Negative price days per year. Compressed from hourly figures:
    # 165 negative hours/year ≈ 7 days/year (at ~24h/day × occurrence fraction).
    # 1000 negative hours ≈ 28 days/year.
    negative_days_per_year: float = 7.0

    # Negative price distribution: mean and std in £/MWh (negative values).
    # Floor enforced at negative_price_floor.
    negative_price_mean: float = -20.0
    negative_price_std: float = 15.0
    negative_price_floor: float = -75.0

    # Dunkelflaute: events/year and duration distribution.
    # During dunkelflaute, price drawn from upper mode × dunkelflaute_multiplier.
    dunkelflaute_events_per_year: float = 5.0
    dunkelflaute_min_days: int = 1
    dunkelflaute_max_days: int = 3
    dunkelflaute_multiplier_mean: float = 1.8
    dunkelflaute_multiplier_std: float = 0.3

    # Markov chain: daily regime-switching persistence.
    # P(stay lower | in lower), P(stay upper | in upper).
    # Set so long-run fraction = lower_mode_fraction.
    regime_persistence: float = 0.85


# Named scenario presets calibrated to R&D findings.
SCENARIOS: dict[str, ScenarioParams] = {
    # 2025 observed calibration (useful as baseline check against historical tail)
    "baseline_2025": ScenarioParams(
        upper_mode_mean=130.0, upper_mode_std=22.0,
        lower_mode_mean=60.0, lower_mode_std=15.0,
        lower_mode_fraction=0.45,
        negative_days_per_year=7.0,
        dunkelflaute_events_per_year=4.0,
    ),

    # 2027 central case: ~60% renewables, ~700 negative hours → ~20 negative days
    "central_2027": ScenarioParams(
        upper_mode_mean=120.0, upper_mode_std=20.0,
        lower_mode_mean=38.0, lower_mode_std=20.0,
        lower_mode_fraction=0.55,
        negative_days_per_year=20.0,
        dunkelflaute_events_per_year=5.0,
        dunkelflaute_multiplier_mean=2.0,
    ),

    # 2027 stress: prolonged dunkelflaute + high negative-price frequency
    "stress_dunkelflaute_2027": ScenarioParams(
        upper_mode_mean=140.0, upper_mode_std=30.0,
        lower_mode_mean=25.0, lower_mode_std=22.0,
        lower_mode_fraction=0.58,
        negative_days_per_year=28.0,
        negative_price_mean=-30.0,
        dunkelflaute_events_per_year=9.0,
        dunkelflaute_min_days=2,
        dunkelflaute_max_days=5,
        dunkelflaute_multiplier_mean=2.5,
    ),

    # 2027 low-renewables: slower buildout, fewer negatives, prices higher
    "low_renewables_2027": ScenarioParams(
        upper_mode_mean=130.0, upper_mode_std=18.0,
        lower_mode_mean=70.0, lower_mode_std=14.0,
        lower_mode_fraction=0.42,
        negative_days_per_year=5.0,
        dunkelflaute_events_per_year=3.0,
    ),

    # 2029 battery-saturated: negative prices peak then decline as batteries absorb surplus
    "battery_saturation_2029": ScenarioParams(
        upper_mode_mean=100.0, upper_mode_std=18.0,
        lower_mode_mean=20.0, lower_mode_std=25.0,
        lower_mode_fraction=0.60,
        negative_days_per_year=10.0,  # batteries absorb most surpluses; fewer sustained negatives
        negative_price_mean=-15.0,
        dunkelflaute_events_per_year=5.0,
        dunkelflaute_multiplier_mean=1.6,  # batteries blunt the spike
    ),
}


def _markov_transition_probs(lower_fraction: float, persistence: float) -> tuple[float, float]:
    """Return (p_stay_lower, p_stay_upper) for a two-state Markov chain.

    Long-run fraction of time in lower regime = lower_fraction.
    Persistence = diagonal probability (same for both states as starting point,
    adjusted so stationary distribution matches lower_fraction).

    Let π_L = lower_fraction, p_LL = P(lower→lower), p_UU = P(upper→upper).
    Stationary: π_L × (1-p_LL) = (1-π_L) × (1-p_UU)
    We set p_LL = persistence and solve for p_UU.
    """
    pi_L = lower_fraction
    p_LL = persistence
    # π_L × (1-p_LL) = π_U × (1-p_UU)
    # (1-p_UU) = π_L × (1-p_LL) / π_U
    pi_U = 1.0 - pi_L
    if pi_U <= 0:
        return (1.0, 0.0)
    p_UU = 1.0 - pi_L * (1.0 - p_LL) / pi_U
    return (p_LL, max(0.0, min(1.0, p_UU)))


def generate_scenario_prices(
    year_from: int,
    year_to: int,
    scenario: str | ScenarioParams = "central_2027",
    seed: str = "scenario",
) -> list[dict]:
    """Generate synthetic daily electricity price records for a forward scenario.

    year_from, year_to: inclusive year range (e.g., 2026, 2028 gives 3 years of data).
    scenario: named preset from SCENARIOS dict or a ScenarioParams instance.
    seed: string seed for reproducibility; same seed + params always produce the same output.

    Returns list of {"settlementDate": str, "systemSellPrice": float}, one per calendar day
    in [year_from-01-01, year_to-12-31], sorted by settlementDate ascending.
    """
    if isinstance(scenario, str):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario '{scenario}'. Available: {sorted(SCENARIOS)}")
        params = SCENARIOS[scenario]
    else:
        params = scenario

    rng = random.Random(f"{seed}_{year_from}_{year_to}_{scenario if isinstance(scenario, str) else 'custom'}")

    start = date(year_from, 1, 1)
    end = date(year_to, 12, 31)
    total_days = (end - start).days + 1

    # Pre-schedule special events for the full range so they don't cluster year-by-year.
    negative_days_total = int(round(params.negative_days_per_year * (total_days / 365.25)))
    dunkelflaute_events_total = max(0, int(round(params.dunkelflaute_events_per_year * (total_days / 365.25))))

    # Negative price day indices (random, without replacement)
    negative_day_indices: set[int] = set(
        rng.sample(range(total_days), min(negative_days_total, total_days))
    )

    # Dunkelflaute spell day indices: schedule event start points, then expand to full duration.
    dunkelflaute_day_indices: set[int] = set()
    safe_range = total_days - params.dunkelflaute_max_days
    if dunkelflaute_events_total > 0 and safe_range > dunkelflaute_events_total:
        dunkelflaute_start_indices = rng.sample(range(safe_range), min(dunkelflaute_events_total, safe_range))
        for start_idx in dunkelflaute_start_indices:
            duration = rng.randint(params.dunkelflaute_min_days, params.dunkelflaute_max_days)
            for d in range(duration):
                dunkelflaute_day_indices.add(start_idx + d)

    # Markov chain transition probabilities
    p_stay_lower, p_stay_upper = _markov_transition_probs(params.lower_mode_fraction, params.regime_persistence)

    # Initial regime: draw from stationary distribution
    in_lower_regime = rng.random() < params.lower_mode_fraction

    records = []
    for day_idx in range(total_days):
        current_date = start + timedelta(days=day_idx)
        date_str = current_date.isoformat()

        # Determine regime for this day via Markov transition
        if in_lower_regime:
            in_lower_regime = rng.random() < p_stay_lower
        else:
            in_lower_regime = rng.random() >= p_stay_upper

        # Base price from regime distribution
        if in_lower_regime:
            price = rng.gauss(params.lower_mode_mean, params.lower_mode_std)
        else:
            price = rng.gauss(params.upper_mode_mean, params.upper_mode_std)

        # Dunkelflaute overlay: replace with upper-mode × multiplier draw
        if day_idx in dunkelflaute_day_indices:
            multiplier = max(1.0, rng.gauss(
                params.dunkelflaute_multiplier_mean, params.dunkelflaute_multiplier_std
            ))
            price = rng.gauss(params.upper_mode_mean, params.upper_mode_std) * multiplier

        # Negative price overlay: replace with negative draw
        if day_idx in negative_day_indices:
            price = rng.gauss(params.negative_price_mean, params.negative_price_std)
            price = max(params.negative_price_floor, price)

        records.append({
            "settlementDate": date_str,
            "systemSellPrice": round(price, 4),
        })

    return records
