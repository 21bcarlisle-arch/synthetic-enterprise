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
    rng = np.random.default_rng(seed)
    gas = rng.lognormal(9.2, 0.6, size=n)
    swing = rng.uniform(0.55, 0.75, size=n)
    insulation = gas * rng.uniform(0.05, 0.45, size=n)
    turndown = gas * rng.uniform(0.04, 0.09, size=n)
    return np.stack([gas, swing, insulation, turndown], axis=1)


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
    rng = np.random.default_rng(2)
    n = 4000
    gas = rng.lognormal(9.2, 0.6, size=n)
    ceiling = rng.uniform(200.0, 6000.0, size=n)
    swing = rng.uniform(0.55, 0.75, size=n)
    turndown = rng.uniform(150.0, 900.0, size=n)

    aligned = np.stack([np.sort(gas), swing, np.sort(ceiling), turndown], axis=1)
    opposed = np.stack([np.sort(gas), swing, np.sort(ceiling)[::-1], turndown], axis=1)

    for j in range(4):
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


def test_THE_ELECTRICITY_AXES_ARE_DECLARED_ABSENT_and_every_N_is_a_floor():
    """The director's sequencing decision is to measure now on the heat-driven axes and re-measure
    when `W2_19` lands. An N reported without that caveat reads as a final answer, and adding axes
    can only raise it."""
    import re

    source = (dvc.PROJECT / "tools" / "demand_vector_coverage.py").read_text(encoding="utf-8")
    flat = re.sub(r"\s*#:?\s+", " ", source)

    assert "annual_electricity_kwh" not in dvc.AXES
    assert "NAMED ABSENT" in flat
    assert "every N here is a FLOOR" in flat, (
        "the floor caveat must sit in the module, not only in a report that gets summarised away")
