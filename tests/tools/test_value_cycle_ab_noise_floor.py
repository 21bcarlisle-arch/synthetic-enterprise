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

import math

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

#: ONE WORLD, SO THAT THESE FIXTURES REACH THEIR OWN SUBJECT. `decompose_floor` grew a
#: world-identity refusal (`dda5a27b2`) that runs BEFORE the mode, seed and reconciliation
#: verdicts. These fixtures predate the stamp, so every one of them was answered "these legs do
#: not say which world they ran in" and six controls below silently stopped measuring what they
#: name -- a scope guard ahead of the verdict turning a substantive red into a procedural one.
#: The production path was never affected: real legs have carried the stamp since the same commit.
#: Fixtures that mean to exercise the world refusal set their digests EXPLICITLY and do not use
#: this default.
_ONE_WORLD = "39a192ce04c1eda8"


def _leg(mode, values, seeds=(11111, 22222, 33333), world=_ONE_WORLD):
    """A floor artefact carrying exactly `values` as its per-seed selection figures."""
    return {"redraw_scope": {"mode": mode},
            "world_identity": {"digest": world, "unavailable_because": None},
            "seeds": [{"seed": s, "selection_gbp": v} for s, v in zip(seeds, values)]}


def _three_arm(contrast, priced=20, accounts=("C1", "C2"), world=_ONE_WORLD):
    return {"level_vs_selection": {"selection_gbp": contrast},
            "world_identity": {"digest": world, "unavailable_because": None},
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


def test_the_remedy_carries_a_price_against_the_PUBLISHED_floor_too():
    """THE DEFECT: `times_this_book` is priced on `v_only + v_except` -- the two legs' own sum --
    while the page prints `undecomposed_sd_gbp` as its +- figure. The reconciliation tolerance is
    0.3-3.0, so those two can differ by a factor of three in the variance and nobody would see it
    in the price. A remedy has to bring the bound a reader is SHOWN under the contrast.

    PRINTED AT REAL INPUTS FIRST. On the 2026-08-30 legs: v_only = 2092.29^2, v_except = 0.21^2,
    v_all = 2577.80^2, contrast 1815.79 -> 1.328x against the legs and 2.015x against the
    published floor. The fixture below is the same shape with round numbers.

    R15 -- the mutations, each run and reverted:
      * price the published-floor figure on `total` instead of `v_all` -> the two assertions
        collapse to one number and `undershot` reds.
      * emit it only when the legs OVERSHOOT -> `undershot` reds.
    The null rung is `reconciled`, where the legs sum to the whole and the two prices must AGREE:
    without it this test is satisfied by any formula that returns a bigger number.
    """
    from tools.run_value_cycle_ab import decompose_floor

    # The legs undershoot the whole: 900^2 + 300^2 = 0.72 * (1000^2 + 61^2)... printed, not argued.
    undershot = decompose_floor(_leg("all", (-1400.0, 0.0, 1400.0)),
                                _leg("only", (-1000.0, 0.0, 1000.0)),
                                _leg("except", (-100.0, 0.0, 100.0)), _three_arm(1000.0))
    assert undershot["reconciliation_ratio"] < 1.0, undershot["reconciliation_ratio"]
    assert undershot["times_this_book_on_the_published_floor"] > undershot["times_this_book"], (
        "the legs summed to less than the published floor, so the remedy priced against that "
        "floor must be DEARER -- pricing it on the legs alone is fail-open in the flattering "
        "direction: {} vs {}".format(undershot["times_this_book_on_the_published_floor"],
                                     undershot["times_this_book"]))
    assert (undershot["priced_decisions_needed_on_the_published_floor"]
            > undershot["priced_decisions_needed"]), "the multiplier moved and the count did not"

    # THE NULL RUNG. Legs that sum to the whole must give ONE price, or the field above is just a
    # bigger number rather than the same arithmetic against a different bound.
    reconciled = decompose_floor(_leg("all", (-1000.0, 0.0, 1000.0)),
                                 _leg("only", (-1000.0, 0.0, 1000.0)),
                                 _leg("except", (0.0, 0.0, 0.0)), _three_arm(1000.0))
    assert reconciled["reconciliation_ratio"] == pytest.approx(1.0)
    assert reconciled["times_this_book_on_the_published_floor"] == pytest.approx(
        reconciled["times_this_book"]), (
        "at a reconciliation of 1.0 the two prices are the same quantity against the same "
        "variance, and a difference means the second is not the same arithmetic")


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


# ---------------------------------------------------------------------------
# 7. WHICH COUNT THE 1/n ARGUMENT INDEXES ON
#
# One leg produces three counts an order of magnitude apart -- 10 accounts re-drawn, 20 decisions
# priced, ~97 elasticity calls -- and the price table ran a 1/sqrt(n) argument through them and
# then divided again into "renewals the world must offer". Only the account count is a sample
# size: `price_elasticity_for_customer` is a pure function of (customer_id, seed), so the ~97
# calls are re-reads of the same 10 numbers and the two decisions on one account share one draw.
# ---------------------------------------------------------------------------

def test_the_elasticity_draw_is_a_pure_function_so_CALLS_are_not_draws():
    """The premise the whole denominator argument rests on, asserted rather than assumed.

    If the draw ever became per-call random, `elasticity_redrawn` WOULD be a sample size and the
    table should index on it. This test is what would notice.
    """
    from simulation.population_draw import price_elasticity_for_customer

    for account in ("C1", "C2", "C9"):
        repeats = {price_elasticity_for_customer(account, 11111) for _ in range(5)}
        assert len(repeats) == 1, (
            "{} returned {} distinct elasticities across five calls at one seed, so a call count "
            "IS a draw count and `remedy_price_table` is indexing on the wrong number".format(
                account, len(repeats)))


def test_the_growth_MULTIPLIER_is_invariant_to_the_unit_and_the_COUNTS_are_not():
    """`needed/n0` cancels n0, so all three candidate denominators agree this book must grow by the
    same factor and disagree wildly on the absolute count. A table that published a count without
    naming its unit let a reader compare 413 against a funnel measured in decisions."""
    from tools.run_value_cycle_ab import remedy_price_table

    common = (2577.80 ** 2, 1815.79, 20, 0.0146)
    on_accounts = remedy_price_table(*common, priced_accounts=10)
    on_decisions = remedy_price_table(*common, priced_accounts=None)

    priced_rows = [(a, d) for a, d in zip(on_accounts, on_decisions)
                   if a["times_this_book"] is not None]
    assert priced_rows, "no row was priced, so this test asserts nothing"
    for account_row, decision_row in priced_rows:
        assert account_row["times_this_book"] == pytest.approx(
            decision_row["times_this_book"]), (
                "the growth multiplier moved when only the UNIT changed, so it is not the "
                "scale-free quantity it is published as")
        # The counts must NOT agree: 10 independent draws is half of 20 decisions.
        assert account_row["priced_accounts_needed"] < account_row["priced_decisions_needed"], (
            "`priced_accounts_needed` equals the decision count, so it was indexed on `priced` "
            "and the accounts column is the decisions column wearing another name")
        assert account_row["priced_decisions_needed"] == decision_row["priced_decisions_needed"], (
            "the decisions column moved when the independence unit changed; it is the same "
            "measurement in the same unit and must not")


def test_renewals_the_world_must_offer_is_reached_from_the_DECISION_count():
    """`priced_share_of_renewals_offered` is 20/1369 -- decisions over decisions. Dividing an
    ACCOUNT count by it is a ratio of two different things, and it would halve the answer."""
    from tools.run_value_cycle_ab import remedy_price_table

    rows = [r for r in remedy_price_table(2577.80 ** 2, 1815.79, 20, 0.0146, priced_accounts=10)
            if r["renewals_the_world_must_offer"] is not None]
    assert rows, "no row carried the column this test exists to check"
    for row in rows:
        assert row["renewals_the_world_must_offer"] == math.ceil(
            row["priced_decisions_needed"] / 0.0146), (
                "the offered-renewals column was not reached from the decision count; at share "
                "{} it reads {} against {} decisions".format(
                    row["priced_share_of_variance"], row["renewals_the_world_must_offer"],
                    row["priced_decisions_needed"]))


def test_every_row_NAMES_the_unit_it_was_computed_on():
    """A count whose unit is inferred from whether a caller passed an argument is a count a reader
    can misread in exactly the way that produced this test."""
    from tools.run_value_cycle_ab import remedy_price_table

    assert {r["independence_unit"] for r in
            remedy_price_table(2577.80 ** 2, 1815.79, 20, 0.0146, priced_accounts=10)} == \
        {"priced_accounts"}
    assert {r["independence_unit"] for r in
            remedy_price_table(2577.80 ** 2, 1815.79, 20, 0.0146)} == {"priced_decisions"}


def test_the_decomposition_reads_its_sample_size_off_the_LEG_not_the_funnel():
    """The funnel counts decisions; the leg counts what it re-rolled. Seeds that disagree about
    their own sample size are withheld rather than averaged into one."""
    from tools.run_value_cycle_ab import decompose_floor

    def _legs(accounts_redrawn):
        only = _leg("only", [1947.6, -2167.5, -767.4])
        for row, count in zip(only["seeds"], accounts_redrawn):
            row["accounts_redrawn"] = count
            row["elasticity_redrawn"] = 97
        return only

    agreed = decompose_floor(_leg("all", [1500.0, -2000.0, 900.0]), _legs((10, 10, 10)),
                             _leg("except", [400.0, -300.0, 250.0]), _three_arm(1815.79))
    assert agreed["independent_draws_this_book"] == 10, (
        "the sample size was not read off the leg that re-rolled it")
    assert agreed["priced_decisions_this_book"] == 20
    assert agreed["elasticity_calls_per_seed"] == [97]

    disagreed = decompose_floor(_leg("all", [1500.0, -2000.0, 900.0]), _legs((10, 9, 10)),
                                _leg("except", [400.0, -300.0, 250.0]), _three_arm(1815.79))
    assert disagreed["independent_draws_this_book"] is None, (
        "seeds that re-rolled DIFFERENT numbers of households were averaged into one sample size")


def test_the_split_publishes_the_MARGIN_and_the_BAR_not_only_the_boolean():
    """`share_is_decisive` cannot distinguish a rout from a photo finish, and the consumer has to
    print the distance beside any price it states. A producer that published only the boolean
    forced the consumer to hardcode the bar, which is the same constant in two places drifting."""
    from tools.run_value_cycle_ab import SHARE_DECISIVE_BAR, decompose_floor

    split = decompose_floor(_leg("all", [1500.0, -2000.0, 900.0]),
                            _leg("only", [1400.0, -1800.0, 800.0]),
                            _leg("except", [400.0, -300.0, 250.0]), _three_arm(1815.79))
    margin = split["share_margin_over_threshold"]
    assert margin is not None and margin >= 0.0
    assert split["share_decisive_bar"] == SHARE_DECISIVE_BAR
    # THE TWO MUST AGREE. A boolean that is not the margin against the bar is a second opinion.
    assert split["share_is_decisive"] == (margin > split["share_decisive_bar"]), (
        "`share_is_decisive` disagrees with its own published margin and bar, so a reader "
        "recomputing the verdict from the numbers beside it gets a different answer")
    assert margin == pytest.approx(abs(
        split["priced_share_of_variance"]
        - split["share_at_which_a_bigger_book_could_resolve_it"]))


def _obs(available_mb, total_mb=24032.1, swap_free_mb=149.4):
    return {"total_mb": total_mb, "available_mb": available_mb, "swap_free_mb": swap_free_mb}


def test_a_floor_run_is_refused_when_the_legs_already_running_cannot_all_peak():
    """The 2026-09-03 OOM, as arithmetic, on the numbers that actually occurred.

    SOLE WITNESS FOR THE REFUSE BRANCH. Two legs already running and holding ~1 GB each, with
    ~15 GB available -- the state at the third launch. Three legs at the measured 6.4 GB peak need
    19.2 GB and this guest can offer 17 GB, so the third must not start. It did, and the
    undecomposed leg -- the one that produces the PUBLISHED bound -- was OOM-killed after 1h 09m
    having written no artefact at all.

    THE FREE-MEMORY QUESTION IS THE WRONG ONE and this is what pins that. `available_mb` here is
    15,000 -- more than twice a single leg's peak -- so a refusal keyed to free memory at launch
    would wave this through, which is exactly what happened.

    Fires on: counting only the caller's own peak instead of every running leg's; dropping the
    running-leg term; keying the comparison to free memory alone.
    """
    from tools.run_value_cycle_ab import floor_run_headroom_refusal

    refusal = floor_run_headroom_refusal(
        sample_fn=lambda: _obs(15000.0),
        legs_fn=lambda: [(101, 1000.0), (102, 1000.0)])
    assert refusal is not None, (
        "a third floor leg was allowed to start beside two that were already growing -- the "
        "launch that cost 1h 09m of compute and produced no artefact")
    assert "19,200" in refusal and "OOM-killed" in refusal, refusal


def test_a_lone_floor_run_on_an_idle_guest_is_allowed():
    """THE PASS BRANCH MUST BE REACHABLE, or the refusal is a constant that stops all floor work.

    SOLE WITNESS FOR THE PASS BRANCH: no other leg running, ample memory. A guard that refused
    here would make the noise floor unrunnable and would be discovered only as "the bound can
    never be re-measured", which is indistinguishable from the defect it exists to prevent.

    Fires on: returning a refusal unconditionally; requiring headroom for a leg that is not there.
    """
    from tools.run_value_cycle_ab import floor_run_headroom_refusal

    assert floor_run_headroom_refusal(sample_fn=lambda: _obs(18000.0),
                                      legs_fn=lambda: []) is None


def test_a_machine_that_cannot_report_its_memory_refuses_rather_than_assuming_room():
    """ABSENCE REFUSES. "We cannot tell" is a result, and a guard that treats an unreadable
    /proc/meminfo as a clean bill of health fails open on exactly the loaded machine where the
    reading is most likely to fail.

    Fires on: swallowing the exception and returning None; treating a missing `available_mb` as
    unlimited.
    """
    from tools.run_value_cycle_ab import floor_run_headroom_refusal

    def _boom():
        raise OSError("/proc/meminfo is not readable")

    assert floor_run_headroom_refusal(sample_fn=_boom, legs_fn=lambda: []) is not None
    assert floor_run_headroom_refusal(sample_fn=lambda: _obs(None),
                                      legs_fn=lambda: []) is not None


def test_the_leg_census_does_not_count_the_process_asking_the_question(tmp_path):
    """A cmdline grep matches the agent whose own prompt quotes the subject.

    The string that identifies a floor leg is the string a session writes when it talks about one,
    so `pgrep -f` reports a leg that does not exist and the refusal then fires forever on an idle
    guest -- making the bound unmeasurable, which is indistinguishable from the defect the refusal
    exists to prevent.

    DRIVEN ON A FAKE /proc, because the real one cannot witness this. The first version of this
    test asserted `os.getpid()` was absent from the census on the live /proc and claimed in its
    docstring that this process's command line contains the pattern. It does not -- pytest's
    cmdline carries neither `run_value_cycle_ab` nor `--noise-floor-seeds` -- so the assertion was
    vacuous and the mutation that drops the exclusion survived it. Here this process's own entry
    is written to MATCH, which is the only way the exclusion is the thing being measured.

    Fires on: dropping the self/ancestor exclusion from `running_floor_legs`.
    """
    import os

    from tools.run_value_cycle_ab import running_floor_legs

    matching = "python3\x00-m\x00tools.run_value_cycle_ab\x00--noise-floor-seeds\x0011111\x00"
    for pid, rss in ((os.getpid(), 4096), (999001, 8192)):
        d = tmp_path / str(pid)
        d.mkdir()
        (d / "cmdline").write_bytes(matching.encode())
        (d / "status").write_text("PPid:\t1\nVmRSS:\t{} kB\n".format(rss), encoding="utf-8")

    census = running_floor_legs(proc_root=tmp_path)
    assert [pid for pid, _ in census] == [999001], (
        "the census counted the process asking the question, so an idle guest reports a floor leg "
        "that does not exist: " + repr(census))
    assert census[0][1] == pytest.approx(8.0)


def test_the_leg_census_does_not_count_a_sibling_shell_quoting_the_command(tmp_path):
    """A shell carries the whole pipeline as ONE argv element, and it is nobody's ancestor.

    SOLE WITNESS FOR THE TOKEN TEST, distinct from the self/ancestor exclusion above: this entry
    is neither this process nor an ancestor of it, so only the argv-token discriminator can reject
    it.

    FOUND BY RUNNING THE REFUSAL, NOT BY READING IT. On its first live invocation the census
    reported THREE legs on a machine running two -- the third being the shell of the very command
    asking. Over-counting is the dangerous direction: it refuses floor runs that would have
    fitted, so the bound can never be re-measured, which is the failure the refusal exists to
    prevent. Same class as `pgrep -f` matching the agent whose prompt quotes the subject.

    Fires on: matching `--noise-floor-seeds` as a substring of the joined cmdline rather than as
    its own argv token.
    """
    from tools.run_value_cycle_ab import running_floor_legs

    entries = {
        999002: ["bash", "-c",
                 "timeout 300 python3 -m tools.run_value_cycle_ab --level-arm "
                 "--noise-floor-seeds 11111,22222 --out /tmp/x.json | grep -v WARNING"],
        999003: ["python3", "-m", "tools.run_value_cycle_ab", "--level-arm",
                 "--noise-floor-seeds", "11111,22222"],
    }
    for pid, argv in entries.items():
        d = tmp_path / str(pid)
        d.mkdir()
        (d / "cmdline").write_bytes(("\x00".join(argv) + "\x00").encode())
        (d / "status").write_text("PPid:\t1\nVmRSS:\t4096 kB\n", encoding="utf-8")

    census = running_floor_legs(proc_root=tmp_path)
    assert [pid for pid, _ in census] == [999003], (
        "a sibling shell quoting the command was counted as a running floor leg, so the refusal "
        "fires on a guest that has room: " + repr(census))
