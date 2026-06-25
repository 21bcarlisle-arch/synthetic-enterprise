"""ToU demand response model — Phase 52.

Models load-shifting behaviour when customers are on Time-of-Use tariffs.
Smart-meter/HH customers receiving ToU price signals shift a fraction of
their peak-window consumption to off-peak windows, reducing grid stress and
(typically) their wholesale cost to serve.

Peak window:    SP 32-38  (16:00-18:30 in standard time convention)
Off-peak window: SP 1-14  (00:00-07:00) + SP 47-48 (23:30-00:00)

Calibration basis:
  - Ofgem Smart Metering Consumer Experience Study (2020): ~13-18% peak
    reduction for active ToU users in GB domestic trials.
  - Octopus Agile / Go customer data (public summaries): 15-25% shift
    for customers with overnight EV charging.
  - Heat-pump trials (EST/BEIS 2022): overnight pre-heat scheduling
    delivers 6-10% additional peak reduction.

This module is pure: list[float] in, list[float] out. No sim/ imports.
"""

from typing import Callable

# Peak settlement periods (1-indexed, each = 30 min).
# SP 32 = 15:30-16:00 start; SP 38 = 18:30-19:00 end.
PEAK_PERIODS: frozenset[int] = frozenset(range(32, 39))

# Off-peak settlement periods — overnight (00:00-07:00) and last slot.
# SP 1-14 = 00:00-07:00, SP 47-48 = 23:30-00:00.
OFFPEAK_PERIODS: frozenset[int] = frozenset(range(1, 15)) | {47, 48}

# Shift fractions calibrated to UK demand-response trials (see docstring).
BASE_SHIFT_FRACTION: float = 0.15   # 15% of peak kWh shifts off-peak
EV_BOOST: float = 0.12              # +12% for EV owners (overnight charging)
HEAT_PUMP_BOOST: float = 0.08       # +8% for heat pump owners (pre-heat scheduling)

_PEAK_INDICES: list[int] = sorted(sp - 1 for sp in PEAK_PERIODS)
_OFFPEAK_INDICES: list[int] = sorted(sp - 1 for sp in OFFPEAK_PERIODS)
_N_OFFPEAK: int = len(_OFFPEAK_INDICES)


def compute_shift_fraction(assets: dict | None = None) -> float:
    """Return the fraction of peak consumption that shifts to off-peak.

    assets: dict from property_model / customer record
    (keys: ev, heat_pump; booleans). Missing keys treated as False.
    Always in [0, 1].
    """
    frac = BASE_SHIFT_FRACTION
    if assets:
        if assets.get("ev"):
            frac += EV_BOOST
        if assets.get("heat_pump"):
            frac += HEAT_PUMP_BOOST
    return min(1.0, frac)


def apply_demand_shift(
    hh_profile: list[float],
    shift_fraction: float,
) -> tuple[list[float], float]:
    """Redistribute peak consumption to off-peak, conserving total kWh.

    hh_profile: 48 floats, index 0 = SP1 (00:00), index 47 = SP48 (23:30).
    shift_fraction: fraction of peak consumption to move, in [0, 1].

    Returns (modified_profile, total_shifted_kwh).
    Total consumption is conserved: sum(modified_profile) == sum(hh_profile).
    """
    shift_fraction = max(0.0, min(1.0, shift_fraction))
    if shift_fraction == 0.0 or len(hh_profile) != 48:
        return list(hh_profile), 0.0

    profile = list(hh_profile)

    total_peak_kwh = sum(profile[i] for i in _PEAK_INDICES)
    shifted_kwh = total_peak_kwh * shift_fraction

    if total_peak_kwh > 0.0:
        scale = 1.0 - shift_fraction
        for i in _PEAK_INDICES:
            profile[i] *= scale

    if _N_OFFPEAK > 0 and shifted_kwh > 0.0:
        per_period = shifted_kwh / _N_OFFPEAK
        for i in _OFFPEAK_INDICES:
            profile[i] += per_period

    return profile, round(shifted_kwh, 6)


def make_shifted_shape_fn(
    base_shape_fn: Callable[[str], list[float]],
    shift_fraction: float,
) -> Callable[[str], list[float]]:
    """Return a wrapper around base_shape_fn that applies demand shifting.

    Used in run_phase2b.py to transparently supply a modified consumption
    profile to run_hedged_term for ToU-eligible customers without changing
    the settlement function's interface.

    base_shape_fn(date_str) -> list[float] (48 kWh values).
    """
    def shifted_fn(date_str: str) -> list[float]:
        profile = base_shape_fn(date_str)
        shifted, _ = apply_demand_shift(profile, shift_fraction)
        return shifted

    return shifted_fn
