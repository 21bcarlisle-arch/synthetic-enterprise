"""Fidelity invariants on the DAILY forward generator (SPIKE_TAIL_SSP_RESIDUAL — reconciled 2026-07-24).

RECONCILED: this file began (step-2) as a failable TRIPWIRE claiming the daily generator starved the
scarcity tail and should be reshaped to reach GBP4,038. The step-3 diagnosis established that was the wrong
locus: the daily generator is a DAILY-MEAN model (real daily-mean max GBP960), and the GBP4,038 tail is a
HALF-HOURLY phenomenon that belongs in the INTRADAY expansion (sim/scenario/intraday_shape.py, where the
fix landed 2026-07-24). So these are now PERMANENT FIDELITY INVARIANTS — the daily generator must STAY a
daily-mean model and NOT itself reach the HH scarcity tail — not tripwires awaiting a daily-generator fix.

WHY THIS EXISTS (step-2 CORRECTION, 2026-07-23 tick): the attack plan's original controls
(tests/sim/test_ssp_tail_model.py) measure `sim/price_engine.py::synthetic_price`. Recon this tick
established that generator is GATED OFF and never settles the residual (its own docstring: "changes
only a code path nothing currently reads from"); it is a conditional-MEAN merit-order model whose tail
is by construction thin -- the scarcity/imbalance tail is such a model's RESIDUAL, not its output, so
reshaping its A0/A1/A2 toward GBP4,038 would be an R12 number-tune that wrecks its MAE fit.

The generator that DOES settle the residual in beyond-history worlds is `sim/scenario/bimodal_generator.py`
(wired via simulation/run_scenario.py). Its tail is where "the residual settled at SSP cannot bite the
company the way 2021-22 bit real suppliers" is actually true. Empirically its reachable max across even
the most extreme built-in preset (stress_dunkelflaute_2027) is ~GBP683 -- it never enters the >GBP1,000
scarcity-spike regime, and the "Crisis spikes: rare, drawn from extreme upper tail" the module docstring
promises is NOT implemented in generate_scenario_prices. That is the truncation, precisely located.

This control makes that gap a LIVE TRIPWIRE (R15), on the RIGHT generator:
  - test_forward_tail_gap_is_real_today  -- GREEN now; FAILS the moment the crisis-spike overlay lands
    and the generator reaches the real tail, forcing SPIKE_TAIL_SSP_RESIDUAL -> closed + this assertion
    flipped in the same commit (the register's closes_when).
  - test_measurement_can_see_a_spike     -- R15 killer-mutation companion: proves the measurement is not
    fail-blind (a series WITH a GBP4,000 spike IS reported as such), so the GREEN above means "no spike",
    not "measurement broken".
  - FAIL-CLOSED is inherited from sim.ssp_tail_target.tail_stats (raises on an empty distribution).

BLIND TO COMPANY P&L (R12/R13): every number here is a property of the BASELINE/curriculum generator
over its own seeds; no company outcome participates. The per-scenario SEVERITY (events/year, spike
magnitude) is director-reserved CURRICULUM (R13) -- this control asserts only the generator's structural
INABILITY to reach the regime at all, which is a fidelity-of-machinery fact, not a difficulty dial.
"""
from __future__ import annotations

import inspect

import pytest

from sim.scenario import bimodal_generator as bg
from sim.ssp_tail_target import tail_stats


def _worst_preset_tail() -> dict:
    """The reachable tail of the most extreme BUILT-IN preset, over a long fixed-seed horizon.
    stress_dunkelflaute_2027 is the heaviest-tailed named scenario; if even it cannot reach the
    scarcity-spike regime, no current preset can (the machinery, not the curriculum, is the limit)."""
    recs = bg.generate_scenario_prices(2026, 2045, "stress_dunkelflaute_2027", seed="spike_tail_control")
    prices = [r["systemSellPrice"] for r in recs]
    assert prices, "generator produced no records -- FAIL-CLOSED"
    return tail_stats(prices)


def test_daily_generator_stays_a_daily_mean_model():
    """RECONCILED 2026-07-24 (step-3 diagnosis): this began as a 'gap-is-real, flip-when-fixed' tripwire
    on the DAILY generator. The step-3 diagnosis established the daily generator is a DAILY-MEAN model and
    the real DAILY-MEAN SSP max is only GBP960 (docs/design/spike_tail_real_target_daily.json) -- the
    GBP4,038 scarcity tail is a HALF-HOURLY phenomenon that lives in the INTRADAY expansion, not the daily
    series (a daily price tuned toward GBP4,038 would be the R12 sibling-trap). So the fix landed in the
    intraday expansion (sim/scenario/intraday_shape.py), NOT here; this assertion is now a PERMANENT
    FIDELITY INVARIANT: the daily generator must stay a daily-mean model and NOT itself reach the
    half-hourly scarcity tail. If it ever does, the daily calibration has drifted (a defect, not progress)."""
    t = _worst_preset_tail()
    assert t["max"] < 1000.0, (
        f"daily generator max is {t['max']:.0f} -- the daily-mean model has drifted into the half-hourly "
        "scarcity tail (real daily-mean max is GBP960); the daily generator must NOT reach the HH tail "
        "(that lives in the intraday expansion). This is a daily-calibration defect, not the spike fix."
    )
    assert t["exceedance_gbp"]["frac_gt_2000"] == 0.0, "daily-mean generator must not reach the >GBP2,000 HH spike"


def test_measurement_can_see_a_spike():
    """R15 killer-mutation companion: the tail measurement is NOT fail-blind. A distribution that DOES
    contain a GBP4,000 scarcity spike is reported with max>3000 and a non-zero >GBP2,000 exceedance --
    so a GREEN gap-is-real above means 'the generator has no spike', never 'the measurement is broken'."""
    with_spike = tail_stats([50.0] * 999 + [4000.0])
    assert with_spike["max"] > 3000.0
    assert with_spike["exceedance_gbp"]["frac_gt_2000"] > 0.0


def test_scarcity_spike_lives_in_intraday_expansion_not_daily_generator():
    """RECONCILED 2026-07-24: the scarcity-spike overlay landed in the INTRADAY expansion
    (sim/scenario/intraday_shape.py, applied by run_scenario._expand_daily_to_hh), NOT in the daily
    generate_scenario_prices -- because the real GBP4,038 spike is a half-hourly (sub-daily) phenomenon,
    not a daily-mean one (step-3 diagnosis). This asserts the SEPARATION holds: the daily generator stays
    a daily-mean model free of intraday scarcity-spike logic. If a crisis/scarcity spike branch ever
    appears in the daily loop, the daily model has absorbed a sub-daily phenomenon it should not carry."""
    gen_src = inspect.getsource(bg.generate_scenario_prices).lower()
    assert "crisis" not in gen_src and "scarcity" not in gen_src, (
        "generate_scenario_prices now references a crisis/scarcity spike -- the scarcity tail belongs in "
        "the intraday expansion (sim/scenario/intraday_shape.py), not the daily-mean generator"
    )
