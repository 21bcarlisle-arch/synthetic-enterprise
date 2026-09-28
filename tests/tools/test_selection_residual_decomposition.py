"""Controls on `tools.selection_residual_decomposition`.

Every test here names the defect it would catch. The module's whole output is shares and intervals
over a family of 18 points, which is exactly the size at which a fail-open reads like a result: a
constant regressor reporting R2 = 0.0, an interval whose lower bound is invented, a share taken over
the wrong total, or a two-state switch priced as a Gaussian spread. Each of those produces a
well-formed table that no reader downstream can tell from a sound one.
"""
from __future__ import annotations

import json
import math

import pytest

from tools import selection_residual_decomposition as srd


def _decision(account: str, term: str, retained: bool, p: float = 0.5) -> dict:
    return {"account": account, "term_start": term, "retained": retained, "believed_p_retain": p}


def _seed(seed: int, selection: float, *, decisions=None, fingerprint="fp0",
          value_net=180_000.0, control_net=167_000.0, level=26.0) -> dict:
    """One seed row whose three nets RECONCILE with its residual, as the real artefact's do."""
    return {
        "seed": seed,
        "selection_gbp": selection,
        "value_arm_net_gbp": value_net,
        "level_arm_net_gbp": value_net - selection,
        "control_net_gbp": control_net,
        "value_advantage_gbp": value_net - control_net,
        "level_advantage_gbp": (value_net - selection) - control_net,
        "level_gbp_per_mwh": level,
        "priced_decision_fingerprint": fingerprint,
        "discrimination_auc": 0.6,
        "billing_accounts_settled_in_window": 164,
        "scored_decisions": decisions if decisions is not None else [
            _decision("SYN-1", "2017-01-01", True), _decision("SYN-2", "2017-02-01", False)],
    }


def _spread_family(n: int = 18) -> list:
    """A family with NO switch: residuals evenly spread, so `separation` must come out low."""
    return [_seed(1000 + i, -2000.0 + 250.0 * i) for i in range(n)]


def _switch_family() -> list:
    """A family that IS a switch: two tight clusters far apart, the real artefact's shape."""
    low = [_seed(100 + i, -4000.0 + 100.0 * i) for i in range(4)]
    high = [_seed(200 + i, 1200.0 + 100.0 * i) for i in range(14)]
    return low + high


# --- 1. the constant-regressor fail-open -------------------------------------------------------

def test_a_constant_regressor_is_unavailable_and_never_r2_zero():
    """DEFECT: a regressor with no variance reporting `R2 = 0.0`.

    That reading is indistinguishable from "measured, and explains nothing" -- which is a FINDING --
    when the truth is "could not be measured at all", which is a missing instrument. Two of the
    eleven pre-registered regressors are in fact constant on the real 18-seed family, so this is
    the live path and not a hypothetical.
    """
    fit = srd.r_squared([7.0] * 18, list(range(18)))
    assert fit["r2"] is None, "a constant regressor must not report a number"
    assert fit["unavailable_because"], "and it must say why"
    assert "no variance" in fit["unavailable_because"]

    # THE ANTI-TAUTOLOGY ARM: the same call on a regressor that DOES vary must produce a number,
    # or this control would pass on a function that refuses everything.
    live = srd.r_squared([float(i) for i in range(18)], [float(i) * 2 + 1 for i in range(18)])
    assert live["r2"] is not None and live["r2"] > 0.99


# --- 2. the invented lower bound ----------------------------------------------------------------

def test_an_interval_straddling_zero_floors_r2_at_exactly_zero():
    """DEFECT: squaring the nearer endpoint of an r-interval that contains zero.

    That invents a positive lower bound on explained variance for a correlation whose SIGN is not
    established -- the direction that misleads, because a reader takes a non-zero floor as evidence
    the effect is real.
    """
    ys = [0.0, 1.0, -1.0, 0.5, -0.5, 2.0, -2.0, 0.25, -0.25, 1.5,
          -1.5, 0.75, -0.75, 1.25, -1.25, 0.1, -0.1, 0.0]
    xs = [float(i) for i in range(18)]
    fit = srd.r_squared(xs, ys)
    assert abs(fit["r"]) < 0.5, "fixture must be a weak correlation for this control to bite"
    assert fit["interval_straddles_zero"] is True
    assert fit["r2_low"] == 0.0, "a straddling interval must floor at exactly zero"

    # ANTI-TAUTOLOGY: a strong correlation must NOT be floored at zero, or the floor is unconditional.
    strong = srd.r_squared(xs, [x * 3.0 + 0.01 * (i % 3) for i, x in enumerate(xs)])
    assert strong["interval_straddles_zero"] is False
    assert strong["r2_low"] > 0.5


# --- 3. shares of the wrong total ---------------------------------------------------------------

def test_a_constant_arm_net_yields_zero_covariance_rather_than_crashing():
    """DEFECT: `None * float` when one arm returns the same net on every seed.

    `r_squared` answers None for a constant column -- correctly -- and the variance identity then
    multiplied that None by a float and took the whole decomposition down. A family drawn over a
    symbol one arm never reads is exactly that shape, so this is a reachable crash and not a
    hypothetical. The covariance of a constant with anything is exactly zero.
    """
    # The real family's shape taken to its limit: the value arm's net identical on every seed while
    # the level arm's moves, which is what makes the residual move at all.
    flat = [_seed(300 + i, -1000.0 + 400.0 * i, value_net=180_000.0) for i in range(6)]
    out = srd.arm_variance_decomposition(flat)
    assert out["corr_between_arm_nets"] is None
    assert out["corr_unavailable_because"]
    assert out["share_from_value_arm"] == 0.0
    assert out["share_from_level_arm"] == pytest.approx(1.0)


def test_a_pinned_residual_is_reported_as_having_no_variance_to_apportion():
    """DEFECT: dividing by `var(selection_gbp) == 0` -- or worse, reporting 0% shares for it.

    A family whose residual is identical on every seed is a state this project has been in
    (2026-09-24, the pinned residual). Shares of zero variance are 0/0, and a block of zeroes would
    read as "the arms contribute nothing" rather than "the instrument moved nothing".
    """
    pinned = [_seed(400 + i, 0.0, value_net=180_000.0 + 50.0 * i) for i in range(6)]
    out = srd.arm_variance_decomposition(pinned)
    assert out["identity_reconciles"] is None
    assert "no residual variance" in out["unavailable_because"]


def test_the_arm_variance_identity_refuses_when_the_nets_do_not_reconcile():
    """DEFECT: reporting `share_from_level_arm` over a total that is not `var(selection_gbp)`.

    Every share in that block is a fraction of the identity `var(val) + var(lev) - 2cov`. If the
    shard's three net figures do not reproduce its own published residual, the shares are fractions
    of a different quantity and each one is wrong by an unknown factor while still summing to 1.0 --
    the fail-open that cannot be seen from the output.
    """
    # Nets that VARY, so the identity has something to reconcile: a fixture whose value-arm net is
    # constant would exercise the zero-covariance path above instead of this one.
    good = [dict(s, value_net=180_000.0) | {"value_arm_net_gbp": 180_000.0 + 40.0 * i}
            for i, s in enumerate(_switch_family())]
    good = [dict(s, level_arm_net_gbp=s["value_arm_net_gbp"] - s["selection_gbp"]) for s in good]
    out = srd.arm_variance_decomposition(good)
    assert out["identity_reconciles"] is True
    assert out["share_from_value_arm"] + out["share_from_level_arm"] \
        + out["share_from_covariance"] == pytest.approx(1.0, abs=1e-9)

    broken = [dict(s) for s in good]
    broken[0]["level_arm_net_gbp"] += 9_999.0  # nets no longer reconcile with selection_gbp
    with pytest.raises(SystemExit) as caught:
        srd.arm_variance_decomposition(broken)
    assert "do not reconcile" in str(caught.value)


# --- 4. the partition, controlled over BOTH branches in one test --------------------------------

def test_both_verdicts_of_the_spread_or_switch_partition_are_reachable():
    """DEFECT: a verdict that only ever returns one of its two answers.

    A classifier that calls everything a switch passes every test written on a switch fixture, and
    one that calls everything a spread passes every test written on a spread. Asserting the rare
    branch CAN be taken belongs in the SAME control as asserting what it says -- this project has
    entered that trap through three separate doors in one afternoon.
    """
    switch = srd.residual_is_a_mixture_or_a_spread(_switch_family())
    spread = srd.residual_is_a_mixture_or_a_spread(_spread_family())
    assert switch["separation"] >= 2.0 and "SWITCH" in switch["verdict"]
    assert spread["separation"] < 2.0 and "SPREAD" in spread["verdict"]
    # The whole partition in one line: both states are occupied by this call pair.
    assert {"SWITCH" in switch["verdict"], "SPREAD" in spread["verdict"]} == {True}


def test_a_two_cluster_family_is_refused_the_gaussian_path_at_every_producer_door():
    """DEFECT: a standard error published on a family the shape check calls a switch.

    Fires on: dropping the `gaussian_licensed` branch in `gaussian_or_mixture_bound`, or any of the
    three producers (`bound_on_its_shape` from both floor writers, the fold's `_leg`) passing the
    sd/sqrt(n) through regardless. The spread family and the too-small family are in the SAME
    control, because a gate that refused everything would pass a switch-only test.
    """
    from tools.fold_noise_floor_family import _leg
    from tools.run_value_cycle_ab import _spread, bound_on_its_shape

    switch = srd.gaussian_or_mixture_bound(_switch_family())
    spread = srd.gaussian_or_mixture_bound(_spread_family())
    small = srd.gaussian_or_mixture_bound(_switch_family()[:3])
    assert (not switch["gaussian_licensed"]) and spread["gaussian_licensed"] \
        and small["gaussian_licensed"] and small["shape_checked"] is False
    lo, hi = switch["mean_interval_gbp"]
    assert lo < 0 < hi and switch["sign_if_stateable"] is None
    assert "SWITCH" in switch["why_no_sem"] and "90%" in switch["why_no_sem"]

    fam = _switch_family()
    shaped = bound_on_its_shape(fam, "selection_gbp", _spread([r["selection_gbp"] for r in fam]),
                                123.0, True)
    assert shaped["sem_gbp"] is None and shaped["distinguishable_from_zero"] is False
    assert shaped["distance_to_a_sign"]["available"] is False
    assert "seeds_needed_to_state_a_sign" not in shaped["distance_to_a_sign"]

    # The fold's per-leg door, called directly: `summarise` also refuses these synthetic rows for
    # carrying no decision fingerprints, which is a different refusal from the one under test.
    folded = _leg(fam, "selection_gbp")
    assert folded["sem_gbp"] is None and folded["distance_to_a_sign"]["available"] is False
    assert _leg(_spread_family(), "selection_gbp")["sem_gbp"] is not None


def test_a_switch_wholly_one_side_of_zero_states_that_sign():
    """DEFECT: a switch that can never state a sign -- the refusal's rare branch, asserted reachable.

    Both states negative: the rate interval carried through cannot reach zero, so the sign stands.
    """
    fam = [_seed(100 + i, -9000.0 + 100.0 * i) for i in range(4)] + [
        _seed(200 + i, -3000.0 + 100.0 * i) for i in range(14)]
    out = srd.gaussian_or_mixture_bound(fam)
    assert out["gaussian_licensed"] is False and out["sign_if_stateable"] == "negative"


def test_the_two_state_mean_interval_is_printed_low_to_high():
    """DEFECT: reporting the rate's endpoints in the RATE's order.

    The family mean FALLS as the lower state's rate rises, so carrying the rate interval through
    unsorted prints `[+937, -998]` -- an interval whose first number is the larger one, which a
    reader scanning a column of intervals will read as the low end.
    """
    out = srd.residual_is_a_mixture_or_a_spread(_switch_family())
    lo, hi = out["mean_interval_from_the_rate_alone_gbp"]
    assert lo < hi
    assert lo < 0 < hi, "this fixture's rate interval must span both signs for the control to bite"


def test_the_exact_rate_interval_cannot_publish_an_impossible_bound():
    """DEFECT: a Wald interval on 4/18, whose lower bound is below zero -- not a rate."""
    lo, hi = srd._clopper_pearson(4, 18, 0.10)
    assert 0.0 <= lo < 4 / 18 < hi <= 1.0
    wald_low = 4 / 18 - 1.6449 * math.sqrt((4 / 18) * (14 / 18) / 18)
    assert wald_low < lo, "the exact interval must be the one that stays inside [0, 1]"


# --- 5. the streak measured in write order ------------------------------------------------------

def test_a_streak_is_computed_in_term_order_and_not_in_write_order():
    """DEFECT: computing D3 over `scored_decisions` as written.

    A run of CONSECUTIVE retained renewals is only a run in term order. Read in write order the
    same account's history yields a different streak, so the regressor would measure how the
    artefact was serialised -- and it would still look like a plausible renewal statistic.
    """
    shuffled = _seed(1, 0.0, decisions=[
        _decision("A", "2019-01-01", True), _decision("A", "2017-01-01", True),
        _decision("A", "2018-01-01", False), _decision("A", "2020-01-01", True)])
    rows = srd.account_decisions(shuffled)["A"]
    assert [t for t, _r in rows] == ["2017-01-01", "2018-01-01", "2019-01-01", "2020-01-01"]
    # In term order the longest run is 2 (2019, 2020). In the written order it would read 2 as well
    # only by accident, so assert the ordered value directly against the history.
    assert srd.longest_retained_streak(rows) == 2
    assert srd.longest_retained_streak([(t, r) for t, r in
                                        [("2019-01-01", True), ("2017-01-01", True),
                                         ("2018-01-01", False), ("2020-01-01", True)]]) == 2


# --- 6. fail closed on the schema ---------------------------------------------------------------

@pytest.mark.parametrize("missing", ["selection_gbp", "scored_decisions",
                                     "priced_decision_fingerprint"])
def test_a_shard_missing_a_field_refuses_rather_than_defaulting(tmp_path, missing):
    """DEFECT: `.get(field, 0)` anywhere in the loader.

    A zero-filled regressor produces a clean R2 of 0.0 for a column the artefact never had, and
    "this shard predates the field" then reads as "renewal count explains nothing".
    """
    import json
    fam = {"seeds": [dict(s) for s in _switch_family()]}
    del fam["seeds"][0][missing]
    path = tmp_path / "fam.json"
    path.write_text(json.dumps(fam))
    with pytest.raises(SystemExit) as caught:
        srd.load_family(path)
    assert missing in str(caught.value)


def test_a_family_too_small_to_bound_anything_is_refused(tmp_path):
    """DEFECT: decomposing two seeds and publishing an R2 from it."""
    import json
    path = tmp_path / "tiny.json"
    path.write_text(json.dumps({"seeds": _switch_family()[:2]}))
    with pytest.raises(SystemExit) as caught:
        srd.load_family(path)
    assert "fewer than 3 seeds" in str(caught.value)


# --- 7. the multiplicity fail-open --------------------------------------------------------------

def test_the_permutation_null_is_taken_over_the_whole_regressor_family():
    """DEFECT: grading a best-of-eleven R2 against a single-regressor null.

    Eleven regressors over 18 points reach R2 ~ 0.25 from noise alone about half the time. A null
    built from one regressor makes that look significant, and the table would publish a renewal
    effect that is the multiplicity and nothing else.
    """
    import random
    ys = [float(i % 5) for i in range(18)]
    one = {"a": [float(i) for i in range(18)]}
    # ONE Random per column, drawn 18 times. `random.Random(j).random()` inside the comprehension
    # re-seeds on every element and yields 18 IDENTICAL values -- a constant column, filtered out as
    # having no variance, and the assertion below then fails on a missing key rather than on the
    # thing it is testing. This control caught that in its own fixture first.
    many = {}
    for j in range(11):
        rng_j = random.Random(j)
        many[f"r{j}"] = [rng_j.random() for _ in range(18)]
    n1 = srd.permutation_max_r2(one, ys, 400, random.Random(1))
    nm = srd.permutation_max_r2(many, ys, 400, random.Random(1))
    assert n1["regressors_in_family"] == 1 and nm["regressors_in_family"] == 11
    assert nm["null_median_max_r2"] > n1["null_median_max_r2"], \
        "the null over a larger family must sit higher, or the multiplicity is not being priced"


def test_a_regressor_family_with_no_variance_says_so_rather_than_reporting_p_one():
    """DEFECT: an all-constant family returning a tidy p-value instead of refusing."""
    import random
    out = srd.permutation_max_r2({"a": [1.0] * 18}, [float(i) for i in range(18)], 50,
                                random.Random(0))
    assert out["available"] is False and out["why_not"]


# --- 8. the identity dressed as a cause ---------------------------------------------------------

def test_the_responses_own_second_term_is_excluded_from_the_separation_test_by_name():
    """DEFECT: letting `level_arm_net_gbp` appear as a field that 'separates the states'.

    `selection_gbp = value_arm_net - level_arm_net`, so it separates perfectly and explains
    nothing. Silently omitting it is nearly as bad as including it: a reader checking which fields
    were tested will look for it, and its absence without a reason reads as an oversight.
    """
    out = srd.what_separates_the_states(_switch_family(), {"x": [1.0] * 18})
    assert "level_arm_net_gbp" in out["excluded_by_construction"]
    assert "identity" in out["excluded_by_construction"]["level_arm_net_gbp"]
    assert "level_arm_net_gbp" not in out["per_field"]


def test_the_separation_test_can_find_a_separator_when_one_exists():
    """DEFECT: a separation test that reports 'nothing separates them' unconditionally.

    On the real family the answer IS zero fields, which is exactly the reading a broken test would
    also give -- so the positive case has to be controlled or the headline is unearned.
    """
    fam = _switch_family()
    planted = [0.0 if s["selection_gbp"] < 0 else 1.0 for s in fam]
    out = srd.what_separates_the_states(fam, {"planted": planted, "flat": [2.0] * 18})
    assert "planted" in out["fields_that_separate"]
    assert "flat" not in out["fields_that_separate"]
    assert "separated by" in out["verdict"]


# ---------------------------------------------------------------------------
# account_state_diff — which accounts the two-state switch lives in (2026-09-27)
# ---------------------------------------------------------------------------


def _seed_row(seed, selection, *, column, value_col, level_col,
              value_net=None, level_net=None):
    """One floor row carrying the three per-account columns and the two arm nets.

    The nets are DERIVED from the columns by default, because the block asserts the two
    against each other -- a fixture that set them independently would let the assertion pass
    on a pair that disagrees, which is the one defect it exists to catch.
    """
    return {
        "seed": seed,
        "selection_gbp": selection,
        "value_arm_net_gbp": sum(value_col.values()) if value_net is None else value_net,
        "level_arm_net_gbp": sum(level_col.values()) if level_net is None else level_net,
        "selection_by_account_gbp": dict(column),
        "value_arm_net_by_account_gbp": dict(value_col),
        "level_arm_net_by_account_gbp": dict(level_col),
    }


def _two_state_family(state_event=5_387.65):
    """Two seeds, opposite states, IDENTICAL value-arm nets -- the designed contrast.

    This mirrors the real pair the pre-registration picked (11111 and 88888, whose
    `value_arm_net_gbp` are equal to the penny), so the whole state distance sits in the
    level arm and the block has to attribute it there.
    """
    value_col = {"A": 1_000.0, "B": 2_000.0, "BIG": 3_000.0}
    level_low = {"A": 900.0, "B": 1_900.0, "BIG": 3_000.0 + state_event}
    level_high = {"A": 900.0, "B": 1_900.0, "BIG": 3_000.0}
    low_col = {a: value_col[a] - level_low[a] for a in value_col}
    high_col = {a: value_col[a] - level_high[a] for a in value_col}
    return {"seeds": [
        _seed_row(11111, sum(low_col.values()), column=low_col,
                  value_col=value_col, level_col=level_low),
        _seed_row(88888, sum(high_col.values()), column=high_col,
                  value_col=value_col, level_col=level_high),
    ]}


def test_the_state_diff_names_the_account_and_the_ARM_the_switch_moved_in():
    """THE WHOLE POINT. `d678f063a` could say 99.84% of the variance was the level arm's net and
    could not say which account; this must name both, and the arm split is what makes it an
    attribution rather than a ranking."""
    block = srd.account_state_diff(_two_state_family())
    assert block["states"]["low"]["seeds"] == [11111]
    assert block["states"]["high"]["seeds"] == [88888]
    assert block["state_distance_gbp"] == pytest.approx(-5_387.65)
    assert block["of_which_the_value_arm_moved_gbp"] == pytest.approx(0.0)
    assert block["of_which_the_level_arm_moved_gbp"] == pytest.approx(5_387.65)
    assert block["largest_single_account"] == "BIG"
    assert block["largest_single_state_move_gbp"] == pytest.approx(-5_387.65)
    assert block["accounts_holding_90pc_of_the_state_movement"] == 1
    top = block["movers"][0]
    assert top["account"] == "BIG"
    assert top["value_arm_move_gbp"] == pytest.approx(0.0)
    assert top["level_arm_move_gbp"] == pytest.approx(5_387.65)
    assert top["moved_mostly_by"] == "the level arm"


def test_the_arm_split_is_asserted_against_the_scalar_and_REFUSES_when_they_disagree():
    """R15: a per-account attribution taken over two differently-cut states is a plausible table
    of pounds with nothing wrong on its face. `selection = value - level`, so the identity is
    checkable, and it must be checked rather than assumed."""
    fam = _two_state_family()
    fam["seeds"][0]["level_arm_net_gbp"] += 1_000.0     # as if the scalar and the arms disagreed
    with pytest.raises(AssertionError, match="disagree about what moved"):
        srd.account_state_diff(fam)


def test_the_per_account_diff_is_asserted_to_sum_to_the_state_distance():
    fam = _two_state_family()
    fam["seeds"][0]["selection_by_account_gbp"]["BIG"] += 500.0   # a column that lost an account
    with pytest.raises(AssertionError, match="state diff sums to"):
        srd.account_state_diff(fam)


def test_a_shard_missing_the_column_REFUSES_and_names_the_seed_and_the_FIELD(tmp_path):
    """R15 FAIL-OPEN and the reason the loader is separate: a shard folded from members either
    side of 2026-09-27 carries the column on some seeds and not others, and "no account moved" is
    what an empty column produces. The refusal has to name which seed and which field."""
    fam = _two_state_family()
    fam["seeds"][1]["level_arm_net_by_account_gbp"] = None
    fam["seeds"][1]["level_arm_net_by_account_gbp_unavailable_because"] = "predates the column"
    path = tmp_path / "shard.json"
    path.write_text(json.dumps(fam))
    with pytest.raises(SystemExit) as excinfo:
        srd.load_for_account_diff(path)
    assert "88888" in str(excinfo.value) and "level_arm_net_by_account_gbp" in str(excinfo.value)
    assert "predates the column" in str(excinfo.value)


def test_TWO_seeds_are_enough_here_even_though_load_family_refuses_them(tmp_path):
    """The looser bound is a decision, not an oversight. `load_family` needs three seeds because a
    variance decomposition over two points is an interval wider than any statement; this reading is
    a two-state DIFF, and two draws -- one from each state -- is exactly its design."""
    path = tmp_path / "shard.json"
    path.write_text(json.dumps(_two_state_family()))
    assert len(srd.load_for_account_diff(path)["seeds"]) == 2
    with pytest.raises(SystemExit, match="fewer than 3 seeds"):
        srd.load_family(path)


def test_an_account_absent_from_one_states_level_arm_is_counted_not_absorbed():
    """A roster event is the mechanism the level arm's own net is most likely to move by, and a
    mean that silently treated an absence as a zero would hide the very thing being looked for."""
    fam = _two_state_family(state_event=0.0)
    gone = fam["seeds"][0]
    gone["level_arm_net_by_account_gbp"].pop("BIG")
    gone["level_arm_net_gbp"] = sum(gone["level_arm_net_by_account_gbp"].values())
    gone["selection_by_account_gbp"]["BIG"] = gone["value_arm_net_by_account_gbp"]["BIG"]
    gone["selection_gbp"] = sum(gone["selection_by_account_gbp"].values())
    block = srd.account_state_diff(fam)
    row = next(r for r in block["movers"] if r["account"] == "BIG")
    # WHICH state the mutated seed fell into is decided by the cut, not by this fixture's write
    # order -- removing an account from the level arm RAISES that seed's residual, so seed 11111
    # is the HIGH state here. Asserting a fixed side would be pinning the test to the arithmetic
    # it is checking.
    mutated = "high" if 11111 in block["states"]["high"]["seeds"] else "low"
    other = "low" if mutated == "high" else "high"
    assert row[f"seeds_absent_from_the_level_arm_{mutated}_state"] == 1
    assert row[f"seeds_absent_from_the_level_arm_{other}_state"] == 0
    # An account absent from a whole state must report the state's seed count, NEVER None -- a
    # None there reads as "not measured" for the one case this field exists to report.
    assert row[f"seeds_absent_from_the_level_arm_{mutated}_state"] is not None
    assert abs(row["level_arm_move_gbp"]) == pytest.approx(3_000.0)


def test_the_state_cut_is_the_SAME_rule_the_mixture_verdict_uses():
    """ONE IMPLEMENTATION, TWO CALLERS. Two copies of the largest-gap rule one function apart
    would let the switch verdict and the attribution describe different partitions of the same
    seeds, with nothing able to notice."""
    ys = [-4_317.0, -4_091.0, -3_872.0, -3_803.0, 1_034.0, 1_253.0, 1_479.0, 1_548.0]
    gap, cut, gaps = srd._largest_gap_cut(ys)
    assert cut == 3, "the cut must fall at the largest gap, which is the state boundary"
    assert gap == pytest.approx(4_837.0)
    assert len(gaps) == len(ys) - 1
    with pytest.raises(AssertionError, match="a gap needs two points"):
        srd._largest_gap_cut([1.0])


def test_the_concentration_of_the_STATE_MOVEMENT_is_a_different_question_from_the_residuals():
    """And it is the one the 1/k ladder rests on, because the ladder is about VARIANCE. A residual
    carried by many accounts can still MOVE in one of them, and the two readings recommend
    opposite things: buy seeds, or accept that depth buys nothing."""
    block = srd.account_state_diff(_two_state_family())
    assert block["accounts_in_the_union"] == 3
    assert block["herfindahl_of_absolute_state_movement"] == pytest.approx(1.0)
    assert block["effective_accounts"] == pytest.approx(1.0)
    # ...and a state move spread evenly over the three reads as three effective accounts, or the
    # statistic above is one that always reports concentration.
    value_col = {"A": 1_000.0, "B": 2_000.0, "BIG": 3_000.0}
    level_low = {a: v - 100.0 for a, v in value_col.items()}
    level_high = dict(value_col)
    low_col = {a: value_col[a] - level_low[a] for a in value_col}
    high_col = {a: value_col[a] - level_high[a] for a in value_col}
    even = {"seeds": [
        _seed_row(1, sum(low_col.values()), column=low_col,
                  value_col=value_col, level_col=level_low),
        _seed_row(2, sum(high_col.values()), column=high_col,
                  value_col=value_col, level_col=level_high)]}
    spread = srd.account_state_diff(even)
    assert spread["effective_accounts"] == pytest.approx(3.0)
    assert spread["accounts_holding_90pc_of_the_state_movement"] == 3


def test_an_account_the_VALUE_arm_moved_is_named_as_such():
    """The label must be able to say either arm, or it is not a reading.

    `d678f063a` found the level arm carrying 99.84% of the variance, so every fixture drawn from
    that finding moves the level arm -- and a label hard-wired to "the level arm" would pass all of
    them while agreeing with the finding for the wrong reason. This is the anti-tautology leg: the
    same block, an account whose VALUE arm moved and whose level arm did not.
    """
    level_col = {"A": 1_000.0, "B": 2_000.0}
    value_low = {"A": 1_000.0, "B": 2_000.0 + 4_000.0}
    value_high = {"A": 1_000.0, "B": 2_000.0}
    low_col = {a: value_low[a] - level_col[a] for a in level_col}
    high_col = {a: value_high[a] - level_col[a] for a in level_col}
    # The value arm moving UP makes that seed the HIGH state, so the low state is the untouched one.
    block = srd.account_state_diff({"seeds": [
        _seed_row(1, sum(low_col.values()), column=low_col,
                  value_col=value_low, level_col=level_col),
        _seed_row(2, sum(high_col.values()), column=high_col,
                  value_col=value_high, level_col=level_col)]})
    assert block["of_which_the_level_arm_moved_gbp"] == pytest.approx(0.0)
    assert abs(block["of_which_the_value_arm_moved_gbp"]) == pytest.approx(4_000.0)
    top = block["movers"][0]
    assert top["account"] == "B"
    assert top["moved_mostly_by"] == "the value arm", top


def test_a_one_seed_shard_REFUSES_with_its_own_reason_not_an_arithmetic_error(tmp_path):
    """A shard with one seed has no two states, and the refusal has to come from the loader saying
    so -- not from the gap helper's AssertionError three frames down, which reads as a bug in the
    tool rather than a fact about the input."""
    fam = _two_state_family()
    fam["seeds"] = fam["seeds"][:1]
    path = tmp_path / "one.json"
    path.write_text(json.dumps(fam))
    with pytest.raises(SystemExit, match="fewer than 2 seeds"):
        srd.load_for_account_diff(path)


def test_the_movement_statistic_stays_inside_the_range_a_count_of_accounts_can_have():
    """KEYED TO THE PROPERTY, and it is the leg that fixes the DENOMINATOR.

    `effective_accounts` is `1/H` and it is a count of accounts, so it can only lie between 1 and
    the size of the union. Every fixture whose accounts all move the same way has
    `gross == |state_distance|`, so the signed denominator is indistinguishable from the right one
    there; here two accounts move in OPPOSITE directions between the states, the state distance is
    the small difference of two larger flows, and the signed denominator reports a fifth of an
    account.
    """
    level_col = {"A": 1_000.0, "B": 2_000.0}
    value_low = {"A": 1_000.0 + 5_000.0, "B": 2_000.0}
    value_high = {"A": 1_000.0, "B": 2_000.0 + 4_000.0}
    low_col = {a: value_low[a] - level_col[a] for a in level_col}
    high_col = {a: value_high[a] - level_col[a] for a in level_col}
    block = srd.account_state_diff({"seeds": [
        _seed_row(1, sum(low_col.values()), column=low_col,
                  value_col=value_low, level_col=level_col),
        _seed_row(2, sum(high_col.values()), column=high_col,
                  value_col=value_high, level_col=level_col)]})
    assert block["gross_absolute_state_movement_gbp"] == pytest.approx(9_000.0)
    assert abs(block["state_distance_gbp"]) == pytest.approx(1_000.0)
    h = block["herfindahl_of_absolute_state_movement"]
    assert 0.0 < h <= 1.0, h
    assert 1.0 <= block["effective_accounts"] <= block["accounts_in_the_union"], block
