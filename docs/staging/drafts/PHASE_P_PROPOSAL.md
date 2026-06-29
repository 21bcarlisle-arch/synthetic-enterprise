# Phase P: EV Smart Charging Shape (Overnight-Weighted)

**Status:** Draft proposal — 4h opt-out gate.
**Proposed by:** Claude Code autonomous session, 2026-06-29

---

## Context

Phase N wired EV electricity demand as a flat additive across all 48 HH periods:

    _ev_hh_kwh = ev_annual_kwh / 365.25 / 48  # uniform, all periods

This is a first approximation. Real EV charging is strongly overnight-concentrated:
- UK smart charging mandate (EV smart charge point regulations 2021): default mode is
  off-peak overnight charging (23:00-07:00 = periods 47-48, 1-14)
- National Grid ESO: ~85-90% of home EV charging occurs midnight to 08:00
- Daytime charging is rare for home chargers; workplace/rapid charging is separate
- Winter overnight = low tariff for most customers; peak triad is 16:00-19:00 (periods 33-38)

Current flat shape means:
- EV adds demand in triad peak periods (16:00-19:00) — unrealistic, inflates TNUoS charge
- No overnight concentration — misses off-peak cost saving and shape risk
- ToU tariff profitability model is distorted (ToU should see EV customers shift to off-peak)

---

## What Phase P does

In `_weather_adjusted_shape_fn` (run_phase2b.py ~line 268-271), replace:

    _ev_hh_kwh = _ev_annual / 365.25 / 48
    shape = [v + _ev_hh_kwh for v in shape]

With an overnight-weighted distribution:

    OVERNIGHT_PERIODS = set(range(1, 15)) | {47, 48}  # 23:30-07:30 (16 periods)
    OVERNIGHT_FRACTION = 0.90   # 90% overnight
    DAYTIME_FRACTION  = 0.10   # 10% other periods

    ev_daily_kwh = _ev_annual / 365.25
    ev_overnight_per_hh = ev_daily_kwh * OVERNIGHT_FRACTION / len(OVERNIGHT_PERIODS)
    ev_daytime_per_hh   = ev_daily_kwh * DAYTIME_FRACTION / (48 - len(OVERNIGHT_PERIODS))
    shape = [v + (ev_overnight_per_hh if (p+1) in OVERNIGHT_PERIODS
                  else ev_daytime_per_hh)
             for p, v in enumerate(shape)]

Annual total unchanged (conservation check: 0.90 + 0.10 = 1.0 × ev_daily_kwh).

---

## Files

- `simulation/run_phase2b.py`: replace flat EV adder with overnight-weighted (~8 lines)

---

## Tests (~12)

- Overnight periods carry more load than daytime periods
- Annual total unchanged (conservation check within 1%)
- Triad periods (33-38) get daytime (low) fraction — not inflated
- No EV customer: shape unchanged
- EV + solar: both effects still independent
- Winter vs summer: shape identical (EV charging not weather-dependent)
- Phase period 1 (midnight): gets overnight weight
- Period 25 (noon): gets daytime weight
- Solar customer pre/post EV acquisition: solar unchanged
- ASHP + EV: ASHP HDD-weighted, EV overnight-weighted, both additive

---

## Fidelity delta

UK home EV charging is the exemplar of overnight off-peak load. Flat demand overcharges
triad and DUoS peak periods and underestimates overnight network impact. Post-Phase P,
the settlement shape correctly shows EV customers as overnight-heavy — which is why they
are ideal ToU tariff candidates (cheap overnight rate matches their actual load profile).
Ofgem and NESO both model EV in this way for demand forecasting.

---

## Gate

4h opt-out from proposal time (~16:30 UTC 2026-06-29). Auto-proceed at ~20:30 UTC.
