"""R15 for `tools/artefact_rerun_diff.py` -- each test names the defect it would catch.

The subject is a control that REPLACES one which returned a wrong verdict in both directions on
its first live use. So the bar here is not "the new code works": it is that each of the replaced
control's two failure modes is a fixture below, and that the new control still refuses the things
the old one refused for good reason. A comparator that says SAME MEASUREMENT to everything would
pass a test suite built only from the false-negative half.
"""
import json
import math
from pathlib import Path

import pytest

import tools.run_value_cycle_ab as runner
from tools.artefact_rerun_diff import (
    MAX_ULPS,
    compare,
    stale_shape,
    ulp_distance,
)

ROOT = Path(__file__).resolve().parents[2]


def _bump(x: float, n: int) -> float:
    """Return the double `n` representable steps above `x`."""
    for _ in range(n):
        x = math.nextafter(x, math.inf)
    return x


# --- the false POSITIVE the replaced control produced -----------------------------------------

def test_added_keys_are_not_a_remeasurement():
    """THE DEFECT: `strip()` named two new keys; the re-run carried nine, so seven read as a
    changed measurement and a correct run was refused."""
    old = {"a": 1, "nested": {"x": 2}}
    new = {"a": 1, "nested": {"x": 2, "brand_new": [1, 2, 3]}, "another": {"deep": {"k": "v"}}}
    r = compare(old, new)
    assert r["same_measurement"], "additive instrumentation was reported as a re-measurement"
    assert sorted(r["added"]) == ["/another", "/nested/brand_new"]
    assert r["changed"] == [] and r["removed"] == []


def test_no_allowlist_is_needed_for_a_key_nobody_predicted():
    """The staleness that made the replaced control fail: a FOURTH lane lands a key overnight.
    A comparator that needed to be told the key's name would refuse this."""
    new = {"a": 1, "method_skill": {"drop_out": {}, "a_key_invented_tomorrow": 7}}
    assert compare({"a": 1, "method_skill": {}}, new)["same_measurement"]


def test_the_clock_alone_is_excluded_by_name():
    assert compare({"generated_at": "A", "v": 1}, {"generated_at": "B", "v": 1})[
        "same_measurement"
    ]


def test_summation_order_noise_is_not_a_remeasurement():
    """THE DEFECT: the real 08-29/08-30 pair, whose two `*_elsewhere` aggregates moved by 3 and
    22 ULPs while every other figure in 91 KB stayed bit-identical. Exact `==` refused it."""
    old = {"absolute_movement_gbp_elsewhere": 10359.439809000032,
           "net_delta_gbp_elsewhere": -257.1865309999878,
           "net_delta_gbp_on_those_accounts": 864.6014330000032}
    new = {"absolute_movement_gbp_elsewhere": 10359.439809000027,
           "net_delta_gbp_elsewhere": -257.18653099998653,
           "net_delta_gbp_on_those_accounts": 864.6014330000032}
    r = compare(old, new)
    assert r["same_measurement"]
    assert len(r["within_tolerance"]) == 2, "the ULP moves must be REPORTED, not hidden"


# --- the false NEGATIVES: everything the comparator must still refuse -------------------------

def test_a_removed_key_is_a_remeasurement():
    r = compare({"a": 1, "gone": 2}, {"a": 1})
    assert not r["same_measurement"] and r["removed"] == ["/gone"]


def test_a_moved_money_figure_is_a_remeasurement():
    """The tolerance must not have swallowed a quantity. One penny on £10,359 is ~5e6 ULPs."""
    r = compare({"net": 10359.439809}, {"net": 10359.449809})
    assert not r["same_measurement"]


def test_a_moved_count_gets_no_tolerance_at_all():
    """Ints are exact. `decisions_scored: 6 -> 7` is a different measurement, full stop."""
    r = compare({"decisions_scored": 6}, {"decisions_scored": 7})
    assert not r["same_measurement"]
    assert "exact" in r["changed"][0][3]


def test_a_float_just_beyond_the_tolerance_is_refused():
    """The bound must BITE at its own edge -- a tolerance whose failing side is unreachable is
    not a tolerance, it is a pass."""
    base = 10359.439809000032
    inside = _bump(base, MAX_ULPS)
    outside = _bump(base, MAX_ULPS + 1)
    assert ulp_distance(base, inside) == MAX_ULPS
    assert compare({"v": base}, {"v": inside})["same_measurement"]
    assert not compare({"v": base}, {"v": outside})["same_measurement"]


def test_nan_is_never_reported_as_unchanged():
    """FAIL-OPEN class: NaN != NaN, so an equality-based comparator can call two NaNs a change
    and a tolerance-based one can divide its way into calling them equal. Neither is allowed."""
    nan = float("nan")
    assert not compare({"v": nan}, {"v": nan})["same_measurement"]
    assert not compare({"v": 1.0}, {"v": nan})["same_measurement"]


def test_a_changed_string_is_a_remeasurement():
    assert not compare({"basis": "net"}, {"basis": "gross"})["same_measurement"]


def test_a_shortened_list_is_a_remeasurement():
    """A sample that lost rows is a different sample, and comparing element-wise without
    checking length first would compare row 0 to row 0 and report nothing."""
    r = compare({"rows": [1, 2, 3]}, {"rows": [1, 2]})
    assert not r["same_measurement"] and "length" in r["changed"][0][0]


def test_a_changed_row_inside_a_list_is_found():
    assert not compare({"rows": [{"a": 1}, {"a": 2}]}, {"rows": [{"a": 1}, {"a": 9}]})[
        "same_measurement"
    ]


def test_bools_are_not_compared_as_numbers():
    """`True == 1` in Python, so a naive numeric path would call `available: true -> 1` a match
    and an `available` flag flipping is exactly the thing a reader acts on."""
    assert not compare({"available": True}, {"available": False})["same_measurement"]
    assert not compare({"available": True}, {"available": 1})["same_measurement"]


# --- the clause no artefact-to-artefact diff can supply ---------------------------------------

def test_stale_shape_catches_the_pre_fix_book_identity():
    """THE DEFECT THIS WHOLE MODULE EXISTS FOR: the 08-30 artefact is byte-perfect against its
    predecessor and still unpromotable, because its `book_identity` was written before
    `f9866cd2a` landed. No comparison between the two files can see that."""
    pre_fix = {"book_identity": {"control_arm": {}, "value_arm": {}}}
    assert stale_shape(pre_fix) == ["same_book_across_arms"]

    post_fix = {"book_identity": {"control_arm": {}, "value_arm": {},
                                  "same_book_across_arms": {"agree": True}}}
    assert stale_shape(post_fix) == []


def test_stale_shape_fails_closed_on_a_missing_block():
    assert stale_shape({}) == ["book_identity absent entirely"]
    assert stale_shape({"book_identity": None}) == ["book_identity absent entirely"]


def test_the_required_shape_is_read_from_the_runner_not_from_a_literal():
    """Keyed to the property, not to today's answer: if the runner stops emitting
    `same_book_across_arms`, this check must stop requiring it rather than wedge every future
    promotion against a name the code has moved past."""
    assert hasattr(runner, "same_book_across_arms"), (
        "the runner no longer emits the cross-arm book control -- stale_shape() is now keyed to "
        "a function that does not exist, and this test is the notice"
    )


def test_the_real_08_30_artefact_is_refused_for_its_shape_and_not_for_its_numbers(tmp_path):
    """The live case, end to end: SAME MEASUREMENT on the numbers, STALE SHAPE on the provenance.
    Both halves matter -- a control reporting only the first would have promoted it."""
    old_p = ROOT / "docs/observability/value_cycle_ab_s1_three_arm_20260829.json"
    new_p = ROOT / "docs/observability/value_cycle_ab_s1_three_arm_20260830.json"
    if not (old_p.exists() and new_p.exists()):
        pytest.skip("the 08-29/08-30 pair is not in this tree")

    old_doc = json.loads(old_p.read_text(encoding="utf-8"))
    new_doc = json.loads(new_p.read_text(encoding="utf-8"))
    r = compare(old_doc, new_doc)

    assert r["same_measurement"], (
        f"the numbers moved after all: removed={r['removed']} changed={r['changed']}"
    )
    assert len(r["added"]) == 9, "the nine additive keys from four lanes"
    assert stale_shape(new_doc) == ["same_book_across_arms"], (
        "the 08-30 artefact's book_identity is the pre-f9866cd2a shape -- if this passes, "
        "either it was regenerated or stale_shape has stopped looking"
    )
