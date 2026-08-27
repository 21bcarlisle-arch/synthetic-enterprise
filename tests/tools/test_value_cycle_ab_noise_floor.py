"""R15 on the NOISE-FLOOR mode: it must be unable to measure a symbol nothing calls.

THE DEFECT THIS SECTION EXISTS FOR, in full. The level-vs-selection split publishes
`selection_gbp` -- a difference between two arms over roughly thirty renewals -- and until
2026-08-27 nobody had measured what that difference does when nothing moves except which
households are drawn elastic. The measurement that was attempted lived in /tmp and patched
`price_sensitivity_for_customer`, which the churn decision had STOPPED CALLING when elasticity
went continuous. So the patch reached nothing, every seed ran a byte-identical world, and the
harness reported a noise floor of exactly zero: the most flattering answer available, produced by
measuring nothing. That is R15's FAIL-SILENT shape -- an unavailable check reading as a passed
check -- and a harness keyed to a structure that moved is where it comes from.

Two controls, and the second is the mutation:
  1. The symbol is RESOLVED from the decision module's own import, so a rename cannot leave this
     tool pointing at a dead name, and a decision that stops importing from the draw module at all
     RAISES here instead of quietly measuring nothing.
  2. Pointing the mode at the retired `price_sensitivity_for_customer` -- the exact defect -- must
     go RED. `test_the_retired_symbol_would_report_a_floor_of_zero` first shows WHY that matters:
     under the old name the runner returns the identical selection figure for every seed, so
     without the fire-counter this tool would publish "spread = 0.00" and call the selection leg
     perfectly stable.

The runner is injected. These controls exercise the noise-floor LOOP -- symbol resolution, the
per-seed rebind, the fire counter, the spread arithmetic -- not the decade-long simulation, which
costs three full passes per seed and would put this suite out of reach of every commit.
"""
from __future__ import annotations

import pytest

from tools.run_value_cycle_ab import (
    ELASTICITY_DECISION_MODULE,
    ELASTICITY_DRAW_MODULE,
    noise_floor,
    resolve_elasticity_symbol,
)

#: Enough accounts that two seeds cannot coincide on the mean by luck, few enough to stay fast.
_ACCOUNTS = [f"ACC-{i:04d}" for i in range(40)]
#: The run's own base seed, standing in for `run_base_seed()`. The patch REPLACES it -- a rebind
#: that reaches the call site makes this value irrelevant, which is the whole mechanism.
_RUN_SEED = 4242


def _fake_runner() -> dict:
    """A three-arm result whose SELECTION leg depends on the drawn elasticity.

    IT RESOLVES THE SYMBOL THE WAY THE DECISION DOES -- a deferred `from ... import ...` executed
    at call time, exactly as `simulation.customer_events.roll_lifecycle_event` does at its line
    313. A module-level import here would bind the original function once and be immune to the
    rebind, so this fake would report a floor of zero for a *correctly* pointed patch and the
    control would be measuring its own import style.
    """
    from simulation.population_draw import price_elasticity_for_customer

    weights = [price_elasticity_for_customer(a, _RUN_SEED) for a in _ACCOUNTS]
    mean_weight = sum(weights) / len(weights)
    # The level arm is flat by construction; only the value arm's advantage moves with who is
    # elastic, so `selection_gbp` inherits the draw -- the dependency being measured.
    level_advantage = 8_000.0
    value_advantage = 8_000.0 + 30_000.0 * (mean_weight - 1.0)
    return {
        "level_vs_selection": {
            "available": True,
            "level_gbp_per_mwh": 44.5,
            "value_advantage_gbp": value_advantage,
            "level_advantage_gbp": level_advantage,
            "selection_gbp": value_advantage - level_advantage,
            "level_share_of_advantage": level_advantage / value_advantage,
        }
    }


# ---------------------------------------------------------------------------
# 1. THE SYMBOL IS READ OFF THE DECISION, NOT WRITTEN DOWN HERE
# ---------------------------------------------------------------------------

def test_the_resolved_symbol_is_the_one_the_churn_decision_imports():
    """And it is resolved from source, so a rename moves this tool with it."""
    name = resolve_elasticity_symbol()
    assert name == "price_elasticity_for_customer"

    # INDEPENDENT of the resolver: the decision module's source really does import this name from
    # the draw module. Asserting the resolver against its own output would be R15's TAUTOLOGY.
    import inspect

    import simulation.customer_events as decision

    src = inspect.getsource(decision)
    assert f"from {ELASTICITY_DRAW_MODULE} import {name}" in src


def test_a_decision_that_imports_nothing_from_the_draw_module_raises_rather_than_guessing():
    """The LOUD disconnect. `tools.run_value_cycle_ab` imports no name from the draw module."""
    with pytest.raises(AssertionError, match="EXACTLY one"):
        resolve_elasticity_symbol(decision_module="tools.run_value_cycle_ab")


# ---------------------------------------------------------------------------
# 2. THE POSITIVE CONTROL -- a correctly resolved patch MOVES the answer
# ---------------------------------------------------------------------------

def test_re_drawing_the_elasticity_moves_the_selection_figure():
    result = noise_floor([11111, 22222, 33333], runner=_fake_runner)

    assert result["symbol_patched"] == (
        f"{ELASTICITY_DRAW_MODULE}.price_elasticity_for_customer")
    assert [r["seed"] for r in result["seeds"]] == [11111, 22222, 33333]
    # THE PATCH FIRED, once per account per seed. A zero here is the defect and raises upstream.
    assert all(r["elasticity_draws"] == len(_ACCOUNTS) for r in result["seeds"])

    spread = result["selection_gbp_spread"]
    assert spread["n"] == 3
    # The seeds must genuinely disagree -- this is the assertion the disconnected patch failed.
    assert spread["range"] > 0.0
    assert spread["stdev"] > 0.0
    assert len({r["selection_gbp"] for r in result["seeds"]}) == 3
    assert result["level_share_spread"]["n"] == 3


def test_the_module_attribute_is_restored_after_the_sweep():
    """A tool that leaves the world patched would poison every later run in the process."""
    import simulation.population_draw as draw

    before = draw.price_elasticity_for_customer
    noise_floor([11111, 22222], runner=_fake_runner)
    assert draw.price_elasticity_for_customer is before


# ---------------------------------------------------------------------------
# 3. THE R15 MUTATION -- point it at the retired symbol and it must go RED
# ---------------------------------------------------------------------------

def test_the_retired_symbol_would_report_a_floor_of_zero():
    """WHY the mutation below matters, shown before it is caught.

    Patching `price_sensitivity_for_customer` by hand and running the same fake produces the
    IDENTICAL selection figure for every seed. Without the fire counter, `noise_floor` would take
    a spread over those and publish 0.00 -- "the selection leg is perfectly stable" -- from a
    sweep that varied nothing at all.
    """
    import simulation.population_draw as draw

    real = draw.price_sensitivity_for_customer
    seen = []
    try:
        for seed in (11111, 22222):
            draw.price_sensitivity_for_customer = (
                lambda cid, _bs, curriculum=None, _s=seed: real(cid, _s, curriculum))
            seen.append(_fake_runner()["level_vs_selection"]["selection_gbp"])
    finally:
        draw.price_sensitivity_for_customer = real

    assert seen[0] == seen[1], (
        "the retired symbol is expected to be disconnected from the price response; if this now "
        "differs, the decision has been re-wired through it and the mutation below needs re-basing")
    assert max(seen) - min(seen) == 0.0


def test_pointing_the_noise_floor_at_the_retired_symbol_raises():
    """THE MUTATION. It must not return a spread of zero -- it must refuse to report at all."""
    with pytest.raises(AssertionError, match="never called"):
        noise_floor([11111, 22222], runner=_fake_runner,
                    symbol="price_sensitivity_for_customer")


def test_a_symbol_that_does_not_exist_raises():
    with pytest.raises(AssertionError, match="no attribute"):
        noise_floor([11111, 22222], runner=_fake_runner, symbol="price_elasticity_for_nobody")


# ---------------------------------------------------------------------------
# 4. ONE SEED IS A RUN, NOT A SPREAD
# ---------------------------------------------------------------------------

def test_a_single_seed_is_refused():
    """A one-seed 'floor' has stdev None and range 0 -- the fail-open reading, refused up front."""
    with pytest.raises(AssertionError, match="at least two seeds"):
        noise_floor([11111], runner=_fake_runner)


def test_the_decision_module_constant_points_at_the_real_decision():
    assert ELASTICITY_DECISION_MODULE == "simulation.customer_events"
