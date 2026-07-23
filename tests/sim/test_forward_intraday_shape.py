"""Fidelity control on the INTRADAY locus of the forward SSP settlement path (SPIKE_TAIL_SSP_RESIDUAL).

HISTORY: this file began (step-3 tick) as a FAILABLE TRIPWIRE asserting the forward expansion was FLAT
(every one of a day's 48 settlement periods carried the same price, so the residual settled with zero
intraday shape). The intraday-shape overlay landed 2026-07-23 (sim/scenario/intraday_shape.py, wired into
simulation/run_scenario.py::_expand_daily_to_hh), so per the register `closes_when` this flips to a
WITHIN-DAY-SHAPE TOLERANCE CHECK in the same commit that closes the defect:

  - the forward residual now carries a real within-day SSP profile whose worst periods reach the scarcity
    regime (calibrated to the half-hourly exceedance curve in docs/design/spike_tail_real_target.json), and
  - the day's MEAN SSP is preserved near the daily generator price (docs/design/spike_tail_real_target_daily.json,
    daily-mean max GBP960) — a daily price tuned toward the HH figure would be the R12 sibling-trap; the fix
    redistributes WITHIN the day, it does not inflate the daily number.

BLIND TO COMPANY P&L (R12/R13): every number here is a structural property of the expansion step over the
generator's own seeds; no company outcome participates. The per-scenario SEVERITY of intraday spikes is
director-reserved CURRICULUM (expressed via the daily generator's per-scenario price level, which the shape
maps to spike frequency); this asserts only the machinery's fidelity — that it CAN carry intraday shape and
its shape is calibrated to real.
"""
from __future__ import annotations

import pytest

from sim.scenario.bimodal_generator import generate_scenario_prices
from simulation.run_scenario import _expand_daily_to_hh


def _per_day_intraday_spread(hh_records: list[dict]) -> list[float]:
    """For each settlement day, the within-day SSP spread (max period price - min period price).
    A flat-expanded day has spread 0.0; any intraday shape makes it positive. FAIL-CLOSED on empty."""
    assert hh_records, "no half-hourly records to measure -- FAIL-CLOSED"
    by_day: dict[str, list[float]] = {}
    for r in hh_records:
        by_day.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
    assert by_day, "no days grouped -- FAIL-CLOSED"
    return [max(prices) - min(prices) for prices in by_day.values()]


def test_forward_residual_carries_intraday_shape():
    """The forward expansion now carries a within-day SSP profile: (near-)every day has a positive
    within-day spread (diurnal + possible spike/trough), so the residual settles against a shape, not a
    single number. This is the direct inverse of the old flat-today tripwire (register closes_when)."""
    daily = generate_scenario_prices(2026, 2029, "stress_dunkelflaute_2027", seed="intraday_shape_control")
    hh = _expand_daily_to_hh(daily, seed="intraday_shape_control")
    spreads = _per_day_intraday_spread(hh)
    # The diurnal profile gives every positive-priced day a spread; allow a small slack for the rare
    # deeply-negative day whose flat base carries only the trough overlay.
    positive_spread_frac = sum(1 for s in spreads if s > 0.0) / len(spreads)
    assert positive_spread_frac > 0.95, (
        f"only {positive_spread_frac:.1%} of forward days carry intraday shape -- the expansion has "
        "regressed toward flat (SPIKE_TAIL_SSP_RESIDUAL would re-open)"
    )
    assert max(spreads) > 100.0, "no day shows a material within-day range -- intraday shape too weak"


def test_forward_intraday_reaches_scarcity_regime_and_preserves_daily_mean():
    """The load-bearing fidelity claim (register closes_when), measured over a representative scenario mix:
      (a) the population half-hourly tail REACHES the scarcity regime calibrated to the real HH exceedance
          curve (the flat expansion structurally could not exceed ~GBP683); AND
      (b) the daily MEAN is preserved near the daily generator price (no R12 daily-number inflation).
    Tolerance band, not a precise fit -- calibration to real shape, blind to P&L; the extreme tail (the
    commercially-biting part, the GBP4,038 that killed suppliers) is required to reach real; the mid-tail is
    looser (diurnal-driven, conservative)."""
    import json
    from statistics import fmean
    from sim.ssp_tail_target import tail_stats

    real = json.load(open("docs/design/spike_tail_real_target.json"))
    scenarios = ["baseline_2025", "central_2027", "stress_dunkelflaute_2027",
                 "low_renewables_2027", "battery_saturation_2029"]
    hh_prices: list[float] = []
    daily_mean_err: list[float] = []
    for sc in scenarios:
        daily = generate_scenario_prices(2026, 2033, sc, seed="calib")
        for r in daily:
            periods = _expand_daily_to_hh([r], seed="calib_" + sc)
            ps = [p["systemSellPrice"] for p in periods]
            hh_prices.extend(ps)
            daily_mean_err.append(abs(fmean(ps) - r["systemSellPrice"]))

    t = tail_stats(hh_prices)
    rex = real["exceedance_gbp"]
    ex = t["exceedance_gbp"]

    # (a) reaches the scarcity regime the flat expansion could not (was structurally 0 above ~GBP683):
    assert t["max"] > 3000.0, f"population HH max {t['max']:.0f} -- did not reach the scarcity regime"
    assert ex["frac_gt_3000"] > 0.0, "no half-hour exceeds GBP3,000 -- extreme tail still starved"
    # extreme tail (the biting part) within a tolerance band of real:
    for thr in ("frac_gt_1000", "frac_gt_2000", "frac_gt_3000"):
        ratio = ex[thr] / rex[thr]
        assert 0.4 <= ratio <= 2.5, f"{thr} ratio-to-real {ratio:.2f} outside [0.4, 2.5] -- recalibrate"
    # mid-tail present (looser band -- diurnal-driven, conservative by design):
    for thr in ("frac_gt_200", "frac_gt_500"):
        ratio = ex[thr] / rex[thr]
        assert 0.3 <= ratio <= 2.5, f"{thr} ratio-to-real {ratio:.2f} outside [0.3, 2.5]"

    # (b) daily mean preserved (R12/R13: the daily-generator calibration is untouched):
    assert max(daily_mean_err) < 1e-3, (
        f"daily mean not preserved (max abs err GBP{max(daily_mean_err):.4f}) -- the intraday shape has "
        "shifted the daily number (R12 sibling-trap)"
    )


def test_measurement_can_see_intraday_shape():
    """R15 killer-mutation companion: the intraday-spread measurement is NOT fail-blind. A day whose 48
    periods DO vary is reported with a positive spread; a genuinely flat day reports 0.0. So a real GREEN
    above means 'the expansion carries intraday shape', never 'the measurement is broken'."""
    spiky_day = (
        [{"settlementDate": "2027-01-08", "settlementPeriod": p, "systemSellPrice": 50.0} for p in range(1, 39)]
        + [{"settlementDate": "2027-01-08", "settlementPeriod": 39, "systemSellPrice": 4000.0}]
        + [{"settlementDate": "2027-01-08", "settlementPeriod": p, "systemSellPrice": 50.0} for p in range(40, 49)]
    )
    assert _per_day_intraday_spread(spiky_day) == pytest.approx([3950.0])
    flat_day = [{"settlementDate": "2027-01-09", "settlementPeriod": p, "systemSellPrice": 42.0}
                for p in range(1, 49)]
    assert _per_day_intraday_spread(flat_day) == pytest.approx([0.0])


def test_measurement_fail_closed_on_empty():
    """FAIL-CLOSED (R15 fail-open guard): an empty half-hourly set RAISES, never silently passes as
    'no shape'."""
    with pytest.raises(AssertionError):
        _per_day_intraday_spread([])


def test_shape_is_deterministic_replay():
    """C-S2: the intraday shape is deterministic in (day, seed) -- a fixed history replays byte-identical,
    so adding it does not introduce non-reproducibility into the forward path."""
    daily = generate_scenario_prices(2026, 2027, "central_2027", seed="replay")
    a = _expand_daily_to_hh(daily, seed="replay")
    b = _expand_daily_to_hh(daily, seed="replay")
    assert [r["systemSellPrice"] for r in a] == [r["systemSellPrice"] for r in b]
