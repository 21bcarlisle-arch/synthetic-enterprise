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


# ---------------------------------------------------------------------------
# 6. THE FLOOR SAYS WHICH CLOCK ITS SPREAD IS ON
# ---------------------------------------------------------------------------
#
# THE DEFECT. This artefact published four contrasts and no clock. `site/data/value_arms.json`
# bounds its headline's directional claims with them, and could only say "this floor declares no
# clock of its own" -- a caveat with no way to empty, on a spread that has been on the realised
# clock since the split was repaired. The consumer was right to fail closed; the producer was the
# one withholding the fact.
#
# READ, NEVER WRITTEN DOWN. The same block was on `settled-provisioned` before that repair, with
# no change of key or shape, so a floor that named its own clock would have gone on naming the
# wrong one. It is taken from `level_vs_selection`'s own label, per seed.


def _runner_declaring(clock):
    """A three-arm result whose split declares `clock`, and which still moves with the draw."""
    def _run() -> dict:
        result = _fake_runner()
        result["level_vs_selection"] = dict(result["level_vs_selection"], clock=clock)
        return result
    return _run


def test_the_floor_carries_the_clock_ITS_OWN_SPLIT_declares():
    """Fires on: hard-coding the label, or dropping it back to unlabelled."""
    for clock in ("settled-realised", "settled-provisioned"):
        result = noise_floor([11111, 22222], runner=_runner_declaring(clock))
        assert result["clock"] == clock, (
            "the floor published {!r} where its own split declared {!r}".format(
                result.get("clock"), clock))
        assert all(row["clock"] == clock for row in result["seeds"])


def test_a_split_that_declares_no_clock_leaves_the_floor_unlabelled_not_guessed():
    """An unlabelled split must not be promoted to the flattering label. The consumer's own "this
    floor carries no clock" caveat is the correct outcome, and it can only fire on a None."""
    assert noise_floor([11111, 22222], runner=_fake_runner)["clock"] is None


def test_seeds_on_DIFFERENT_clocks_are_refused_rather_than_averaged():
    """A spread across rows on two clocks is not the spread of one quantity. This run's two clocks
    are £39,962.17 apart -- larger than every contrast the spread bounds -- so a mixed floor would
    publish that gap as seed noise, which is the most decisive-looking error bar available."""
    seen = {"n": 0}

    def _alternating():
        seen["n"] += 1
        clock = "settled-realised" if seen["n"] == 1 else "settled-provisioned"
        return _runner_declaring(clock)()

    with pytest.raises(AssertionError, match="different clocks"):
        noise_floor([11111, 22222], runner=_alternating)


# ---------------------------------------------------------------------------
# 5. THE FLOOR CUT IN TWO -- and the same fail-silent shape one level down
# ---------------------------------------------------------------------------
#
# The undecomposed floor re-draws ~2,050 households while the arm prices 20 renewals, so its
# spread has two sources with OPPOSITE remedies. `site/data/value_arms.json` published one of them
# as the remedy before anybody separated them. The `only`/`except` legs are the separation, and
# every way they can lie is the way the original defect lied: a leg that reaches nothing returns a
# spread of zero, and the decomposition then hands the WHOLE variance to the other half -- which
# is a conclusion, not a measurement.

_PRICED = _ACCOUNTS[:4]


def test_the_two_legs_partition_the_call_stream():
    """`redrawn + held == draws` on every row, and the two legs' rosters are complementary.
    Without this the halves could overlap or leave a gap and still look like a decomposition."""
    only = noise_floor([11111, 22222], runner=_fake_runner,
                       redraw_accounts=_PRICED, redraw_mode="only")
    rest = noise_floor([11111, 22222], runner=_fake_runner,
                       redraw_accounts=_PRICED, redraw_mode="except")
    for leg in (only, rest):
        for row in leg["seeds"]:
            assert row["elasticity_redrawn"] + row["elasticity_held_fixed"] == \
                row["elasticity_draws"], row
    for a, b in zip(only["seeds"], rest["seeds"]):
        assert a["elasticity_redrawn"] == b["elasticity_held_fixed"], (
            "the two legs do not cut the same population along the same line")
        assert a["accounts_redrawn"] == len(_PRICED)


def test_a_leg_whose_roster_matches_NOBODY_raises_rather_than_reporting_a_floor_of_zero():
    """THE MUTATION, one level down from the retired-symbol one. An `only` leg naming accounts the
    world never prices re-draws nothing, runs the base world every seed, and reports a spread of
    zero -- from which the decomposition concludes the priced households contribute NOTHING and a
    larger book is useless. The most consequential answer available, from measuring nothing."""
    with pytest.raises(AssertionError, match="re-drew NO household"):
        noise_floor([11111, 22222], runner=_fake_runner,
                    redraw_accounts=["NOT-AN-ACCOUNT"], redraw_mode="only")


def test_a_leg_that_holds_NOBODY_fixed_is_the_undecomposed_floor_wearing_a_label():
    """The mirror: an `except` leg whose roster misses everybody re-draws the whole book and would
    be published as the rest-of-book half, handing it the entire variance."""
    with pytest.raises(AssertionError, match="held NO household fixed"):
        noise_floor([11111, 22222], runner=_fake_runner,
                    redraw_accounts=["NOT-AN-ACCOUNT"], redraw_mode="except")


def test_a_decomposed_mode_without_a_roster_is_refused():
    with pytest.raises(AssertionError, match="needs the roster"):
        noise_floor([11111, 22222], runner=_fake_runner, redraw_mode="only")


def test_the_held_half_keeps_the_runs_own_seed_and_not_a_third_world():
    """The `only` leg must leave every unpriced household on exactly the elasticity the base run
    gave it. A leg that substituted a constant would move the held half onto a third world and
    call the difference the priced half's."""
    from simulation.population_draw import price_elasticity_for_customer as real

    seen = {}

    def _recording_runner():
        from simulation.population_draw import price_elasticity_for_customer
        for account in _ACCOUNTS:
            seen[account] = price_elasticity_for_customer(account, _RUN_SEED)
        return _fake_runner()

    noise_floor([11111, 22222], runner=_recording_runner,
                redraw_accounts=_PRICED, redraw_mode="only")
    for account in _ACCOUNTS:
        if account in _PRICED:
            continue
        assert seen[account] == real(account, _RUN_SEED), (
            "an unpriced household was moved off the run's own seed, so the `only` leg is not "
            "measuring the priced households' contribution: {}".format(account))


# ---------------------------------------------------------------------------
# 6. THE VERDICT THE PAGE'S REMEDY SENTENCE TURNS ON
# ---------------------------------------------------------------------------

def _leg(mode, values, seeds=(11111, 22222, 33333)):
    """A floor artefact carrying exactly `values` as its per-seed selection figures."""
    return {"redraw_scope": {"mode": mode},
            "seeds": [{"seed": s, "selection_gbp": v} for s, v in zip(seeds, values)]}


def _three_arm(contrast, priced=20, accounts=("C1", "C2")):
    return {"level_vs_selection": {"selection_gbp": contrast},
            "renewal_funnel": {"value_arm": {
                "priced": priced, "renewals_the_world_offered": 1369,
                "priced_share_of_renewals_offered": 0.0146,
                "accounts_the_arm_priced": list(accounts)}}}


def test_the_verdict_is_the_REST_OF_BOOK_leg_against_the_contrast():
    """The remedy is true only when the half no book size shrinks is ALREADY under the contrast.

    Both cases here hold the priced half identical and move only the rest-of-book half, so a
    verdict that read the wrong leg -- or read the undecomposed total -- flips.
    """
    from tools.run_value_cycle_ab import decompose_floor

    # PRINTED BEFORE IT WAS ASSERTED. sd(n)^2 = V_except + V_only*(20/n): at V_only = 1,300^2 and
    # V_except = 500^2 the bar reaches GBP 1,000 at n = 46, and the first draft of this fixture
    # (900/400) landed on exactly n = 20 -- a "remedy" already paid for by today's book, which
    # would have passed a `> 0` assertion and asserted nothing.
    tight = decompose_floor(_leg("all", (-1400.0, 0.0, 1400.0)),
                            _leg("only", (-1300.0, 0.0, 1300.0)),
                            _leg("except", (-500.0, 0.0, 500.0)), _three_arm(1000.0))
    assert tight["larger_settled_book_would_resolve_it"] is True
    assert tight["priced_decisions_needed"] == 46, (
        "a remedy priced at or below today's book is not a remedy")

    wide = decompose_floor(_leg("all", (-1400.0, 0.0, 1400.0)),
                           _leg("only", (-1300.0, 0.0, 1300.0)),
                           _leg("except", (-1400.0, 0.0, 1400.0)), _three_arm(1000.0))
    assert wide["larger_settled_book_would_resolve_it"] is False
    assert wide["priced_decisions_needed"] is None, (
        "an unreachable remedy was still given a price, which reads as reachable")


def test_legs_that_do_not_name_their_own_half_are_refused():
    """A leg read as the other one hands the whole variance to the wrong side. Never inferred."""
    from tools.run_value_cycle_ab import decompose_floor

    swapped = decompose_floor(_leg("all", (-1000.0, 0.0, 1000.0)),
                              _leg("except", (-900.0, 0.0, 900.0)),
                              _leg("except", (-400.0, 0.0, 400.0)), _three_arm(1000.0))
    assert swapped["available"] is False and "only" in swapped["why_not"]


def test_legs_run_on_DIFFERENT_seeds_are_not_a_decomposition():
    from tools.run_value_cycle_ab import decompose_floor

    out = decompose_floor(_leg("all", (-1000.0, 0.0, 1000.0)),
                          _leg("only", (-900.0, 0.0, 900.0)),
                          _leg("except", (-400.0, 0.0, 400.0), seeds=(7, 8, 9)),
                          _three_arm(1000.0))
    assert out["available"] is False and "different seeds" in out["why_not"]


def test_the_reconciliation_is_published_even_when_it_disagrees():
    """The two halves against the whole is the ONLY thing saying the split is real rather than
    two unrelated runs. A tool that reported it only when it was flattering would be no control."""
    from tools.run_value_cycle_ab import decompose_floor

    out = decompose_floor(_leg("all", (-1000.0, 0.0, 1000.0)),
                          _leg("only", (-3000.0, 0.0, 3000.0)),
                          _leg("except", (-3000.0, 0.0, 3000.0)), _three_arm(1000.0))
    assert out["available"] is True, "a bad reconciliation must be PUBLISHED, not withheld"
    assert out["reconciliation_ratio"] > 3, out["reconciliation_ratio"]


def test_a_priced_roster_with_no_drawn_household_says_the_lever_is_a_product():
    """`more renewals actually priced` reads as a book-SIZE lever. When every priced decision is a
    static-roster account it is not one, and growing the drawn book makes the floor worse."""
    from tools.run_value_cycle_ab import where_the_priced_decisions_come_from

    static = where_the_priced_decisions_come_from(_three_arm(1.0, accounts=("C1", "C2")))
    assert static["of_those_drawn"] == 0
    assert "PRODUCT, not a size" in static["reading"]

    mixed = where_the_priced_decisions_come_from(
        _three_arm(1.0, accounts=("C1", "SYN-2021-001")))
    assert mixed["of_those_drawn"] == 1
    assert "PRODUCT, not a size" not in mixed["reading"], (
        "the reading is a constant, so it would say the lever is a product on a book where "
        "drawn households ARE priced")


def test_the_price_table_says_UNREACHABLE_rather_than_quoting_a_huge_book():
    """Below the threshold there is no book that resolves it. A table that answered with a very
    large number instead would read as expensive-but-possible, which is the opposite finding."""
    from tools.run_value_cycle_ab import remedy_price_table

    rows = remedy_price_table(2577.80 ** 2, 1815.79, 20, 0.0146)
    below = [r for r in rows if r["priced_share_of_variance"] <= 0.5]
    assert below and all(r["priced_decisions_needed"] is None for r in below), (
        "a share under the 50.4% threshold was given a finite price")
    above = [r for r in rows if r["priced_share_of_variance"] >= 0.6]
    assert all(r["priced_decisions_needed"] for r in above)
    assert [r["priced_decisions_needed"] for r in above] == \
        sorted((r["priced_decisions_needed"] for r in above), reverse=True), (
            "the price must FALL as the priced half grows -- a table that did not is not this "
            "arithmetic")
