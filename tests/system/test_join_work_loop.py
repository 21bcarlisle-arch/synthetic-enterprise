"""JOIN 1 — the work loop: a run completes → publishes → the next draw picks up
real work.

Design: `docs/design/JOIN_TEST_TIER.md`. R15 cut-proofs: `test_join_cut_mutation.py`.

The advisor's note on this one: *"this one alone would have caught most of the
last fortnight."* The two properties it watches are the two that actually broke —
Rule 0 (unfinished work present and nothing drawable is a DEFECT, never a rest)
and the publish→draw link (a wedged publish gate must change what the next draw
picks up; the prose rule for that was consumed-not-absorbed twice, and 2h17m of
alarms fired into tick silence on both occasions).

REPORT-ONLY (first landing, director pre-ruled): this module carries
`join_report_only`, so the publish gate deselects it. A red join test alarms; it
cannot wedge the live site. See JOIN_TEST_TIER.md §3 for the promotion condition.
"""

import pytest

from tests.system import chains

pytestmark = pytest.mark.join_report_only


def test_the_work_loop_join_conducts(tmp_path):
    """Unfinished work reaches the draw, finished work does not, and a wedged
    publish gate reaches the draw ladder."""
    chain = chains.run_work_loop_chain(tmp_path)
    chains.assert_work_loop_join(chain)


def test_unfinished_work_is_never_an_empty_draw(tmp_path):
    """Rule 0, stated as its own test so the failure message names the rule.

    A map holding nothing BUT unfinished work must never draw empty — there is no
    dial configuration under which real work present is a legitimate rest.
    """
    chain = chains.run_work_loop_chain(
        tmp_path, atoms=[chains.UNFINISHED_ATOM]
    )
    assert chain["drawn_ids"] == ["JOIN_TIER_UNFINISHED_ATOM"], (
        "an empty feasible set with real work present is a defect in the dials, "
        f"not a reason to hold — drew {chain['drawn_ids']}"
    )


def test_a_map_of_only_finished_work_draws_nothing(tmp_path):
    """The opposite direction, so the draw is not merely a function that always
    returns something. Without this, the test above passes on a draw that offers
    work unconditionally — including re-verification of done atoms."""
    drawn = chains.draw_from_map(
        tmp_path,
        [chains.FINISHED_ATOM, dict(chains.UNFINISHED_ATOM, level_current=2)],
    )
    assert drawn == [], (
        "the draw re-offered work that is already at target: "
        f"{[a.get('id') for a in drawn]}"
    )


def test_no_wall_crossing_in_the_work_loop_participants():
    chains.assert_no_wall_crossing(["background/supervisor.py"])
