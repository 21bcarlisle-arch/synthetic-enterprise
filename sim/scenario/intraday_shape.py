"""Intraday (SP-level) SSP shaping for the FORWARD scenario settlement path (SPIKE_TAIL_SSP_RESIDUAL fix).

WHY THIS EXISTS (step-3 diagnosis, redirected fix — 2026-07-23):
`simulation/run_scenario.py::_expand_daily_to_hh` used to write each daily generator price to ALL 48
settlement periods of the day, identically. So in forward/curriculum worlds the residual settled at DAILY
granularity with ZERO intraday shape — and the block-vs-shape mismatch that killed real suppliers in
2021-22 (a flat block hedge meeting a spiky half-hourly SSP) was STRUCTURALLY ABSENT regardless of the
daily number. This module produces the missing within-day SSP profile.

THE PHYSICS (so the fix is shape, not a number — R10/R12):
The real GBP4,038 tail is NOT merit-order marginal cost; it is Balancing-Mechanism cash-out / scarcity
pricing — the imbalance price formed from the marginal balancing action when the system is short in a
single half-hour (a sub-daily phenomenon). The deep negatives are oversupply / curtailment cash-out in a
single period. So the shape has three components, ALL applied as MEAN-PRESERVING perturbations around the
day's generated price:
  1. a deterministic DIURNAL profile (overnight trough, evening peak) — real SSP always has one;
  2. a stochastic SCARCITY SPIKE in one peak period, drawn from a heavy-tailed distribution, whose
     probability rises with the day's price level (system tightness proxy — tight days spike more);
  3. a stochastic OVERSUPPLY TROUGH in one off-peak period (single-period deep negative).

MEAN-PRESERVING BY CONSTRUCTION: every perturbation sums to zero across the 48 periods, so the day's MEAN
SSP is unchanged (within a small rounding/cap residual). This is load-bearing for two reasons:
  - the daily-generator calibration (daily-mean tail vs docs/design/spike_tail_real_target_daily.json,
    daily-mean max GBP960) is UNTOUCHED — a daily price tuned toward the HH figure would be an R12
    sibling-trap; we do not tune the daily number at all, we only redistribute WITHIN the day;
  - it is impossible for this step to inflate daily means past anything real.

CALIBRATION IS FIDELITY, NOT CURRICULUM (R13):
The spike/trough parameters are calibrated so the POPULATION half-hourly exceedance curve approaches the
REAL one (docs/design/spike_tail_real_target.json) — reproducing observed reality, decided BLIND to company
P&L. That is baseline fidelity. The per-scenario SEVERITY of crisis spikes for a NAMED world ("2021-style
gas crisis" vs "2027 central") is director-reserved CURRICULUM: it is expressed through the daily
generator's per-scenario price level (already director-owned via bimodal_generator SCENARIOS), which this
module faithfully maps to intraday spike frequency via the tightness relationship. This module adds NO new
per-scenario dial; it ships one baseline-calibrated relationship.

BLIND TO COMPANY P&L / EPISTEMIC WALL: this is SIM/world code. No company/saas import; every draw is from a
day-and-seed-keyed substream (C-S2 RNG discipline) independent of the daily generator's RNG, so adding it
does not shift any other subsystem's outputs.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Deterministic diurnal profile: 48 multipliers, one per settlement period
# (SP1 = 00:00-00:30 ... SP48 = 23:30-24:00), normalised to mean 1.0 so applying
# it preserves the daily mean. Shape: overnight trough, morning ramp, midday
# solar dip, evening peak (~18:00-19:00), late-evening fall. Values are a plausible
# GB half-hourly demand/price shape; the exact curve is not load-bearing (the tail
# is set by the spike overlay), but a real diurnal shape is itself fidelity.
# ---------------------------------------------------------------------------
def _raw_diurnal() -> list[float]:
    prof: list[float] = []
    for p in range(48):  # p = 0..47 -> SP 1..48
        hour = p / 2.0  # 0.0 .. 23.5
        if hour < 5.0:            # overnight trough
            v = 0.72
        elif hour < 7.0:          # early morning ramp
            v = 0.72 + (hour - 5.0) * 0.14
        elif hour < 10.0:         # morning shoulder
            v = 1.00
        elif hour < 15.0:         # midday solar dip
            v = 0.88
        elif hour < 16.0:         # afternoon recovery
            v = 1.00
        elif hour < 19.0:         # evening ramp to peak
            v = 1.00 + (hour - 16.0) * 0.15  # up to ~1.45 at 19:00
        elif hour < 21.0:         # peak plateau easing
            v = 1.35 - (hour - 19.0) * 0.10
        else:                     # late evening fall
            v = 1.10 - (hour - 21.0) * 0.12
        prof.append(v)
    mean = sum(prof) / len(prof)
    return [v / mean for v in prof]  # normalise to mean 1.0


_DIURNAL = _raw_diurnal()

# Evening-peak periods (SP ~33-42, 16:00-21:00) — where a scarcity half-hour is most
# likely to land (system tightest at peak demand). Overnight periods (SP 1-12) — where
# an oversupply trough is most likely (low demand + high wind).
_PEAK_PERIODS = [p for p in range(48) if 16.0 <= p / 2.0 < 21.0]
_TROUGH_PERIODS = [p for p in range(48) if p / 2.0 < 6.0 or 11.0 <= p / 2.0 < 14.0]


@dataclass(frozen=True)
class IntradayShapeParams:
    """Baseline (fidelity) calibration of the intraday shape. NOT a per-scenario severity dial (R13):
    these reproduce the REAL half-hourly exceedance curve, decided blind to company P&L."""
    # Scarcity spike (single peak period on a spike day). Calibrated 2026-07-23 so the POPULATION
    # half-hourly exceedance curve over a representative scenario mix matches the real one within tolerance
    # (frac_gt_1000 ~0.96x, frac_gt_2000 ~1.01x, frac_gt_3000 ~1.10x of docs/design/spike_tail_real_target.json).
    spike_base_rate: float = 0.06          # P(spike) at the reference tightness price
    spike_ref_price: float = 120.0         # daily price at which spike prob == spike_base_rate
    spike_tightness_exp: float = 1.35      # P(spike) scales ~ (daily_price / ref) ** this (tight days spike more)
    spike_rate_cap: float = 0.55           # never spike more than this fraction of days
    spike_target_median: float = 900.0     # median spike PEAK price (GBP/MWh), lognormal
    spike_target_sigma: float = 1.35       # lognormal sigma — heavy upper tail toward the cap
    spike_target_cap: float = 4100.0       # just above the real max (GBP4,038); a single SP can reach here
    # Oversupply trough (single off-peak period on a trough day).
    trough_base_rate: float = 0.02         # P(a single deep-negative half-hour), roughly daily-level independent
    trough_target_mean: float = -55.0      # mean trough PEAK-negative price (GBP/MWh)
    trough_target_std: float = 45.0
    trough_floor: float = -190.0           # just below the real min (-GBP185.33)


DEFAULT_PARAMS = IntradayShapeParams()


def _lognormal_capped(rng: random.Random, median: float, sigma: float, cap: float) -> float:
    # median of a lognormal is exp(mu); draw exp(mu + sigma*z), cap the upper tail.
    import math

    mu = math.log(median)
    val = math.exp(mu + sigma * rng.gauss(0.0, 1.0))
    return min(val, cap)


def shape_day(daily_price: float, date_str: str, seed: str,
              params: IntradayShapeParams = DEFAULT_PARAMS) -> list[float]:
    """Return 48 half-hourly SSP prices (SP1..48) whose MEAN equals `daily_price` (within a small cap
    residual), carrying a within-day shape: diurnal profile + a possible scarcity spike + a possible
    oversupply trough. Deterministic in (daily_price, date_str, seed) — replayable (C-S2).

    Mean-preserving: the diurnal profile has mean 1.0, and the spike/trough are added as zero-sum
    perturbations (the peak period gets +delta, the other 47 share -delta/47), so sum(prices)/48 ==
    daily_price up to the effect of the target caps.
    """
    rng = random.Random(f"{seed}|intraday|{date_str}")

    # 1) diurnal base (mean == daily_price). For non-positive daily prices the multiplicative diurnal
    #    would invert the shape; fall back to a flat base there (a deeply-negative surplus day has little
    #    meaningful positive diurnal structure), the trough overlay still adds sub-period variation.
    if daily_price > 0:
        prices = [daily_price * g for g in _DIURNAL]
    else:
        # negative/zero-mean day: the multiplicative diurnal would invert the shape, but a real low/negative
        # day still has within-day variation (wind ramps, demand shape). Apply a modest MEAN-ZERO additive
        # diurnal instead so the day is not flat (mean preserved: mean(g)==1 so mean(g-1)==0).
        _NEG_DAY_AMP_GBP = 20.0
        prices = [daily_price + _NEG_DAY_AMP_GBP * (g - 1.0) for g in _DIURNAL]

    def _redistribute(idx: int, target: float) -> None:
        """Set period idx to `target` and spread the opposite change across the other 47 (zero-sum)."""
        delta = target - prices[idx]
        comp = delta / 47.0
        for i in range(48):
            if i == idx:
                prices[i] = target
            else:
                prices[i] -= comp

    # 2) scarcity spike — probability rises with tightness (daily price level).
    tightness = (daily_price / params.spike_ref_price) if params.spike_ref_price > 0 else 1.0
    spike_prob = params.spike_base_rate * (max(tightness, 0.0) ** params.spike_tightness_exp)
    spike_prob = min(spike_prob, params.spike_rate_cap)
    if daily_price > 0 and rng.random() < spike_prob:
        j = rng.choice(_PEAK_PERIODS)
        target = _lognormal_capped(rng, params.spike_target_median, params.spike_target_sigma,
                                   params.spike_target_cap)
        # only apply as a spike if it actually raises the chosen period (else it is noise)
        if target > prices[j]:
            _redistribute(j, target)

    # 3) oversupply trough — a single deep-negative half-hour (curtailment/oversupply cash-out).
    if rng.random() < params.trough_base_rate:
        k = rng.choice(_TROUGH_PERIODS)
        target = rng.gauss(params.trough_target_mean, params.trough_target_std)
        target = max(params.trough_floor, target)
        if target < prices[k]:
            _redistribute(k, target)

    return [round(p, 4) for p in prices]
