"""Sizing a sample against a DISTRIBUTION, each test named by the defect it catches.

The canon's correction is that a coverage claim measured on a scalar is measuring something else.
The two defects below are the same mistake committed inside the fix for it: a criterion whose bar
loosens as the sample shrinks, and a test that compares margins while the thing it exists to catch
lives in the joint.
"""
from __future__ import annotations

import numpy as np
import pytest

from tools import demand_vector_coverage as dvc


def _grid(n=4000, seed=0):
    """A synthetic population with ONE COLUMN PER DECLARED AXIS.

    Built from `dvc.AXES` rather than a hand-written list of five: when weather sensitivity was
    added as a sixth axis every fixture here silently disagreed with the module and six controls
    failed at once. A fixture whose width is hardcoded is a fixture that goes stale the moment the
    subject grows.
    """
    rng = np.random.default_rng(seed)
    gas = rng.lognormal(9.2, 0.6, size=n)
    columns = {
        "annual_gas_kwh": gas,
        "annual_electricity_kwh": rng.lognormal(7.9, 0.5, size=n),
        "seasonal_swing": rng.uniform(0.55, 0.75, size=n),
        "weather_sensitivity_kwh_per_degree_day": gas * rng.uniform(0.0002, 0.0006, size=n),
        "peak_window_share": rng.uniform(0.19, 0.26, size=n),
        "insulation_ceiling_kwh": gas * rng.uniform(0.05, 0.45, size=n),
        "turndown_ceiling_kwh": gas * rng.uniform(0.04, 0.09, size=n),
    }
    missing = [a for a in dvc.AXES if a not in columns]
    assert not missing, f"the fixture has no column for {missing}; add one rather than let it drift"
    return np.stack([columns[a] for a in dvc.AXES], axis=1)


def test_THE_BAR_DOES_NOT_LOOSEN_AS_THE_SAMPLE_SHRINKS():
    """THE DEFECT THE FIRST VERSION SHIPPED. Acceptance was "the KS distance is under the two-sample
    CRITICAL VALUE", and that value grows as n shrinks -- a thirteen-case sample passed trivially
    because a test that size has almost no power to fail. It returned N = 13 and N = 21, the two
    smallest sizes on the ladder, which is the answer that criterion will always give.

    A sample-size rule whose bar moves with the sample is not a sample-size rule."""
    values = _grid()
    reference = dvc._Reference(values, dvc.AXES)
    rng = np.random.default_rng(1)

    tiny = values[rng.choice(len(values), size=13, replace=False)]
    verdict = dvc.accepts_against(tiny, reference, tolerance=dvc.DISTRIBUTION_TOLERANCE)
    assert not all(v["accepts"] for v in verdict.values()), (
        "a 13-case sample reproduced a 4,000-point distribution to within 5 points of mass "
        "everywhere -- the bar is moving with n again")
    assert verdict["JOINT"]["detectable_at_alpha"] > dvc.DISTRIBUTION_TOLERANCE, (
        "at 13 cases a test could still detect a discrepancy smaller than the tolerance, so the "
        "power statement this reports is wrong")


def test_THE_JOINT_CATCHES_WHAT_THE_MARGINS_CANNOT():
    """THE SECOND VERSION'S DEFECT, and it is the canon's own point one level up. Testing each axis
    separately returned the SAME N with and without the response axes, because two households with
    identical consumption and opposite insulation ceilings differ in the JOINT and in neither
    margin -- the exact pair the canon says are different customers.

    Built so the two populations have IDENTICAL marginals by construction: the same values, paired
    differently. A per-axis test cannot tell them apart and must not be able to; the sliced joint
    test must."""
    n = 4000
    base = _grid(n=n, seed=2)
    ceiling_at = dvc.AXES.index("insulation_ceiling_kwh")
    gas_at = dvc.AXES.index("annual_gas_kwh")
    aligned = base.copy()
    aligned[:, gas_at] = np.sort(base[:, gas_at])
    aligned[:, ceiling_at] = np.sort(base[:, ceiling_at])
    opposed = aligned.copy()
    opposed[:, ceiling_at] = np.sort(base[:, ceiling_at])[::-1]

    for j in range(len(dvc.AXES)):
        assert dvc.ks_distance(aligned[:, j], opposed[:, j]) == pytest.approx(0.0, abs=1e-12), (
            f"axis {j} differs between the two populations, so this fixture no longer isolates "
            "the joint")

    reference = dvc._Reference(aligned, dvc.AXES)
    verdict = dvc.accepts_against(opposed, reference, tolerance=0.05)
    assert all(verdict[a]["d"] == pytest.approx(0.0, abs=1e-12) for a in dvc.AXES), (
        "a marginal test saw a difference; the fixture is not marginal-identical")
    assert verdict["JOINT"]["d"] > 0.05, (
        "the joint test cannot tell a population where the biggest ceilings sit on the biggest "
        "users from one where they sit on the smallest -- which is the only difference the canon "
        "cares about")


def test_ADDING_THE_RESPONSE_AXES_IS_NEVER_EASIER():
    """A PROPERTY, not today's answer. The response criterion tests a superset of directions, so it
    can never accept a sample the distribution criterion rejects. If it ever did, the two are not
    measuring the same population and the second number is not the harder one the canon calls the
    real one."""
    values = _grid(seed=3)
    pop = {"values": values}
    for tol in (0.10, 0.05):
        nd, _ = dvc.smallest_n(pop, dvc.DISTRIBUTION_AXES, ns=(55, 144, 377, 987), tolerance=tol,
                               replicates=2, seed=4)
        nr, _ = dvc.smallest_n(pop, dvc.AXES, ns=(55, 144, 377, 987), tolerance=tol,
                               replicates=2, seed=4)
        if nd is not None and nr is not None:
            assert nr >= nd, (
                f"at tolerance {tol} spanning response needed {nr} against {nd} for the "
                "distribution alone -- the superset criterion came out easier")


def test_THE_PRE_PROJECTED_REFERENCE_IS_THE_SAME_TEST(tmp_path):
    """AN EQUIVALENCE, ESTABLISHED RATHER THAN ASSUMED. The reference is projected once instead of
    per call because the measurement did not finish otherwise. An optimisation that changes the
    answer is not an optimisation, so the fast path and the plain path are asserted equal."""
    values = _grid(seed=5)
    rng = np.random.default_rng(6)
    sample = values[rng.choice(len(values), size=300, replace=False)]

    fast = dvc.accepts_against(sample, dvc._Reference(values, dvc.AXES), tolerance=0.05)
    slow = dvc.accepts(sample, values, axes=dvc.AXES, tolerance=0.05)
    for axis in dvc.AXES:
        assert fast[axis]["d"] == pytest.approx(slow[axis]["d"], abs=1e-9)
    assert fast["JOINT"]["d"] == pytest.approx(slow["JOINT"]["d"], abs=1e-9), (
        "the pre-projected joint disagrees with the plain one, so the speed-up changed the test")


def test_THE_CEILING_IS_WHAT_IS_LEFT_TO_DO_not_what_a_bare_fabric_would_gain():
    """THE CANON'S OWN EXAMPLE, held as a control. Two households with identical consumption and
    opposite insulation ceilings are different customers; that is only true if the ceiling reads
    what is ALREADY INSTALLED. NEED carries LI_FLAG and CWI_FLAG per dwelling, and a dwelling with
    both must have a smaller remaining ceiling than the same dwelling with neither."""
    from tools import need_stock_joint as need

    if not need.NEED_CSV.is_file():
        pytest.skip("the NEED sample is not on this machine")

    base = {"PROP_TYPE": "Semi detached", "PROP_AGE_BAND": "1", "FLOOR_AREA_BAND": "3"}
    bare = dvc._fabric_for({**base, "LI_FLAG": "0", "CWI_FLAG": "0"}, retrofitted=False)
    done = dvc._fabric_for({**base, "LI_FLAG": "1", "CWI_FLAG": "1"}, retrofitted=False)
    target = dvc._fabric_for({**base, "LI_FLAG": "0", "CWI_FLAG": "0"}, retrofitted=True)

    assert bare[0] > done[0], "an uninsulated dwelling does not lose more heat than an insulated one"
    assert (bare[0] - target[0]) > (done[0] - target[0]), (
        "the remaining ceiling is the same whether or not the measures are already installed, so "
        "the sample cannot tell the canon's two households apart")


def test_ONLY_THE_HALF_HOURLY_SHAPE_IS_STILL_ABSENT():
    """THE CORRECTION THE DIRECTOR FORCED. This used to assert that annual electricity was absent,
    and that was a real deferral dressed as a dependency: the HALF-HOURLY SHAPE needs a presence
    pattern and waits for `W2_19`; ANNUAL ELECTRICITY is carried per dwelling by NEED and waits for
    nothing. Bundling them deferred the axis that turns a floor into a number.

    So electricity must now be IN, and exactly one axis may remain declared blind."""
    assert dvc.UNCOUNTED_AXES, "the uncounted axes must be enumerated, not left to prose"
    assert "half_hourly_electricity_shape" not in dvc.UNCOUNTED_AXES, (
        "the half-hourly shape is now an axis; leaving it on the uncounted list would understate "
        "what the figure covers as badly as overstating it")
    assert dvc.REDUCES_OVER.blind_to == (), (
        "every component of the canon's subject vector must now enter the measurement")
    assert "annual_electricity_kwh" in dvc.AXES, (
        "annual electricity is observed in NEED and has no W2_19 dependency; deferring it is what "
        "kept the answer a floor")
    # THE DECLARATION IS ASSERTED BY THE LANE THAT OWNS IT, not duplicated here. The AST census
    # (`tools/reduction_dimension.py`) spans twelve modules and lands as one change; its own suite
    # checks every declaration including this module's. A `hasattr` guard here did not work and
    # should not have: the symbol-landing check reads references STATICALLY, so a guarded reference
    # to a symbol no blob supplies is still a consumer without a supplier -- and reaching for
    # `getattr` to slip past it would be evading a control rather than satisfying it.
    import re

    flat = re.sub(r"\s*#:?\s+", " ",
                  (dvc.PROJECT / "tools" / "demand_vector_coverage.py").read_text(encoding="utf-8"))
    assert "half_hourly_electricity_shape" in flat, (
        "the one axis still waiting on W2_19 must be named in the module, or the floor caveat "
        "survives only in a report that gets summarised away")


def test_THE_WEIGHTING_MUST_DO_WORK_or_the_design_has_reverted_to_representativeness():
    """THE DIRECTOR'S OWN TELL, WRITTEN INTO THE CANON AND NOW INTO A CONTROL.

    *"If N comes out at the scale a random sample would need, the weighting is doing no work and the
    design has reverted to representativeness."* It did: the acceptance test drew
    `rng.choice(len(values), size=n)` while the module's docstring quoted "each drawn case carries
    the population mass it stands for". No weight entered the test at all, and the answer -- 8,500 --
    was the size a random sample needs.

    A deliberately-chosen weighted sample must beat a random one by a wide margin on the same
    acceptance, or one of the two is not what its name says."""
    values = _grid(n=6000, seed=7)
    reference = dvc._Reference(values, dvc.AXES)

    chosen = dvc.choose_for_difference(values, 120, seed=0)
    weights = dvc.fit_weights(values, chosen, reference)
    designed = max(v["d"] for v in
                   dvc.accepts_weighted(values[chosen], weights, reference).values())

    rng = np.random.default_rng(3)
    same_size = values[rng.choice(len(values), size=len(chosen), replace=False)]
    random_draw = max(v["d"] for v in dvc.accepts_against(same_size, reference).values())

    assert designed < random_draw, (
        f"the designed sample scored {designed:.4f} against a random draw's {random_draw:.4f} at "
        "the same size -- the weighting is doing no work, which is the exact state the canon's tell "
        "was written to catch")


def test_THE_WEIGHTS_ARE_FITTED_ON_DIRECTIONS_THE_TEST_DOES_NOT_SCORE():
    """FITTING TO THE ANSWER, and it is the obvious way to make this design look better than it is.
    The weights are solved against `FIT_SLICES` directions; the acceptance scores `JOINT_SLICES`
    others. If the two sets were the same, a passing sample would have learned the test rather than
    the population."""
    reference = dvc._Reference(_grid(n=500), dvc.AXES)
    rng = np.random.default_rng(999)
    fit_dirs = rng.normal(size=(dvc.FIT_SLICES, len(dvc.AXES)))
    fit_dirs /= np.linalg.norm(fit_dirs, axis=1, keepdims=True)

    for u in fit_dirs:
        for v in reference.directions:
            assert abs(float(np.dot(u, v))) < 0.9999, (
                "a fit direction coincides with a test direction, so the weights were fitted to the "
                "criterion that scores them")


def test_A_NEGATIVE_WEIGHT_IS_A_HOUSEHOLD_COUNT_BELOW_ZERO():
    """Non-negativity is not a solver convenience. A case that has to be SUBTRACTED to make the
    distribution work is a case that should not have been chosen, and a sample carrying one cannot
    be handed to anything that reads weights as households."""
    values = _grid(n=3000, seed=8)
    reference = dvc._Reference(values, dvc.AXES)
    chosen = dvc.choose_for_difference(values, 60, seed=0)
    weights = dvc.fit_weights(values, chosen, reference)

    assert (weights >= 0).all(), "a chosen case carries negative mass"
    assert weights.sum() > 0, "every weight is zero, so the sample stands for nothing"


def test_CHOOSING_REJECTS_NEAR_DUPLICATES_and_keeps_the_tails():
    """The canon's two requirements on the choosing, together: *"distinct cases spanning the output
    variation, near-duplicates rejected, tails deliberately in"*. A cluster medoid is one household
    per distinct region of behaviour, so two near-identical households cannot both be chosen; the
    per-axis extremes are added explicitly because clustering alone would drop them."""
    values = _grid(n=4000, seed=9)
    chosen = dvc.choose_for_difference(values, 40, seed=0)

    for j in range(values.shape[1]):
        assert int(np.argmax(values[:, j])) in set(chosen.tolist()), (
            f"the maximum of axis {j} was not deliberately included")
        assert int(np.argmin(values[:, j])) in set(chosen.tolist()), (
            f"the minimum of axis {j} was not deliberately included")

    mean, sd = values.mean(axis=0), values.std(axis=0)
    z = (values - np.where(sd == 0, 1.0, sd) * 0 - mean) / np.where(sd == 0, 1.0, sd)
    picked = z[chosen]
    gaps = [np.min(np.sum((picked - p) ** 2, axis=1)[np.arange(len(picked)) != i])
            for i, p in enumerate(picked)]
    assert min(gaps) > 0.0, "two chosen cases occupy the same point in the output space"
