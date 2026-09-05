"""Does a closed atom's code actually run? Each test names the defect it exists to catch.

Director console, 2026-09-05: *"'Closed' tells a reader nothing about whether code runs. Make that
visible before stage 1 builds on top of another one -- W2_12 nearly cost us exactly that."*
"""
from __future__ import annotations

import pytest

from tools import closed_atom_delivery as cad


@pytest.fixture(scope="module")
def rows():
    return cad.classify()


def test_the_scan_reproduces_THREE_ANSWERS_ESTABLISHED_BY_HAND():
    """THE CONTROL THIS WHOLE TOOL RESTS ON, and the reason it is not optional.

    This scan was wrong twice on the way here, in OPPOSITE directions:

      * counting importers only called 34 atoms dead -- but a tool the commit hook runs as a
        script (`python3 tools/write_time_gate.py`) has no importer anywhere and certainly runs;
      * counting any path-shaped string called none of them dead -- but a path in a docstring or a
        registry list counts, which is exactly how `change_of_tenancy_register` read as having two
        production callers when it has none.

    A measurement that can fail in both directions must be pinned to answers established by
    reading the code, or its output is a number nobody checked. Each of the three below was
    verified by hand on 2026-09-05.
    """
    imports, invoked = cad._scan(cad.PROJECT)

    for rel, expected in cad.CALIBRATION.items():
        got = cad.reached(rel, imports, invoked)
        assert got == expected, (
            f"{rel}: scan says {got!r}, hand-verified answer is {expected!r}. The scan has drifted "
            f"in one of the two directions this control exists to pin."
        )


def test_a_module_is_not_its_own_reacher():
    """The self-reference leg. Without it every module imports something and every atom reads
    DELIVERED, which is the fail-open version of this whole tool."""
    imports = {"a.b": {"a/b.py"}}

    assert cad.reached("a/b.py", imports, set()) is None


def test_an_invocation_counts_only_from_somewhere_that_could_EXECUTE_it():
    """THE DEFECT THAT MADE THE SECOND WRONG ANSWER. A path named in prose, a docstring or a
    registry list is a MENTION. `change_of_tenancy_register.py` appears in three such places and
    is called from none of them."""
    assert cad.reached("x/y.py", {}, set()) is None
    assert cad.reached("x/y.py", {}, {"x/y.py"}) == "invoked"


def test_the_four_verdicts_are_all_reachable_on_the_live_map(rows):
    """REACHABILITY OVER THE WHOLE PARTITION, in one assertion rather than one test per verdict.

    A classifier that returned DELIVERED for everything would pass any single-verdict test. The
    live map has all four, and if it ever stops having one the partition has collapsed and this
    fires -- which is the property, not today's counts.
    """
    seen = {r["verdict"] for r in rows}

    assert seen == {"DELIVERED", "UNREACHED", "FRAMED", "NO-CODE"}, seen
    assert len(rows) > 200, "the closed map did not load -- the scan is measuring nothing"


def test_FRAMED_is_decided_by_the_target_and_never_by_reachability(rows):
    """An atom whose target was 1 did what it was asked; calling it UNREACHED would be a criticism
    of work nobody commissioned. The two verdicts must not be able to swap."""
    for r in rows:
        if r["verdict"] == "FRAMED":
            assert r["level_target"] < cad.BUILD_TARGET
        if r["verdict"] in ("DELIVERED", "UNREACHED"):
            assert r["level_target"] >= cad.BUILD_TARGET


def test_the_prior_art_query_answers_the_question_that_cost_us_W2_12(rows):
    """THE DEFECT, exactly as it happened. Stage 1's people work covers change-of-tenancy ground.
    A closed atom named it, and only the director asking stopped it being built twice.

    The atom-level verdict is NOT enough and this asserts why: W2_12 and W2_13 are BOTH `FRAMED`,
    and the difference a reader needs is per-module -- W2_13's modules are imported by the live run
    loop, three of W2_12's five are reached by nothing at all.
    """
    hits = cad.prior_art("change_of_tenancy", rows)

    assert [h["id"] for h in hits] == ["W2_12_change_of_tenancy_debt_physics"]
    reach = hits[0]["reach"]
    assert reach["company/crm/change_of_tenancy_register.py"] is None
    assert reach["company/billing/account_closure.py"] is None
    assert reach["simulation/final_bill_outcome.py"] is None
    assert reach["simulation/arrears_engine.py"] == "imported"


def test_the_sibling_atom_that_HOLDS_reads_as_reached(rows):
    """The negative leg, and it is the one that stops this tool being a machine for condemning
    everything: W2_13 covers the same lane, closed at the same level, and both its modules run."""
    hits = cad.prior_art("occupancy_consumption", rows)

    assert [h["id"] for h in hits] == ["W2_13_occupancy_consumption_volume_shape"]
    assert all(v == "imported" for v in hits[0]["reach"].values()), hits[0]["reach"]


def test_prior_art_on_untouched_ground_returns_nothing(rows):
    """Without this, a query that matched everything would satisfy the two tests above."""
    assert cad.prior_art("a_subject_no_atom_has_ever_named_xyzzy", rows) == []
