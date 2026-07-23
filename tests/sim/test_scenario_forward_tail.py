"""Failable control on the ACTUAL forward SSP settlement path (SPIKE_TAIL_SSP_RESIDUAL).

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


def test_forward_tail_gap_is_real_today():
    """The forward SSP generator that settles the residual STARVES the scarcity-spike tail RIGHT NOW.
    Real SSP reached GBP4,038 (8 Jan 2021 SP39); the generator's heaviest preset cannot clear GBP1,000.
    Flip this the moment the crisis-spike overlay lands (register closes_when)."""
    t = _worst_preset_tail()
    assert t["max"] < 1000.0, (
        f"forward generator max is {t['max']:.0f} -- if it now reaches the real >GBP1,000 scarcity "
        "regime the crisis-spike overlay has landed: set SPIKE_TAIL_SSP_RESIDUAL status: closed and "
        "flip this assertion to a real tolerance check in the SAME commit (register closes_when)"
    )
    assert t["exceedance_gbp"]["frac_gt_2000"] == 0.0, "generator still cannot reach the >GBP2,000 spike"


def test_measurement_can_see_a_spike():
    """R15 killer-mutation companion: the tail measurement is NOT fail-blind. A distribution that DOES
    contain a GBP4,000 scarcity spike is reported with max>3000 and a non-zero >GBP2,000 exceedance --
    so a GREEN gap-is-real above means 'the generator has no spike', never 'the measurement is broken'."""
    with_spike = tail_stats([50.0] * 999 + [4000.0])
    assert with_spike["max"] > 3000.0
    assert with_spike["exceedance_gbp"]["frac_gt_2000"] > 0.0


def test_crisis_spike_overlay_not_yet_implemented():
    """The doc-vs-code gap made mechanical: the module docstring promises a crisis-spike overlay, but
    generate_scenario_prices does not implement one. When it does (a variable/branch named for the
    crisis/scarcity spike appears in the generate loop), this fails -- a reminder to close the register."""
    gen_src = inspect.getsource(bg.generate_scenario_prices).lower()
    assert "crisis" not in gen_src and "scarcity" not in gen_src, (
        "generate_scenario_prices now references a crisis/scarcity spike -- if the overlay is implemented "
        "and the tail reaches real, close SPIKE_TAIL_SSP_RESIDUAL and flip test_forward_tail_gap_is_real_today"
    )
