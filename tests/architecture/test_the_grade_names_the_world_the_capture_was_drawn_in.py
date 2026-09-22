"""A grade may only license a DIRECTION when the world its rows were drawn in is the live one.

THE DEFECT THIS EXISTS TO CATCH, and it is the fail-open half of a refusal that was already right.
`site/data/value_arms.json` published `ceiling: 0.6091` against a no-information interval of
`0.4159-0.5850` on 1,266 SVT decisions and `ceiling_clears: null`, because
`generate_value_arms_data._svt_drift_belief` will not state a direction whose world is unknown and
`docs/observability/svt_drift_belief_grade.json` named no world at all. Correct refusal. But the
reader's whole test was `(grade["world_identity"] or {}).get("digest")` -- PRESENCE of a stamp --
so the obvious repair (have the grader call `world_level_identity()` at assembly and write the
answer down) would have discharged the refusal while proving nothing. The grader reads a capture
written weeks earlier; the live block names the world the GRADER ran in and is silent about the
world the FIGURES were measured in. A grade stamped with a world it was not measured in would have
passed every check that existed, and the page would have printed a green "the signal is there".

THE PARTITION IS THE SUBJECT, NOT THE THREE CASES SEPARATELY. `CLAUDE.md`: *when a branch exists to
be taken rarely, assert it CAN be taken before asserting what it does* -- a guard that withholds on
EVERYTHING satisfies every per-branch refusal test ever written, and this area has entered that trap
before. So `test_the_three_worlds_are_all_reachable` is one assertion over the whole partition and
is the load-bearing control here; the per-branch tests below it say what each outcome MEANS and are
worthless without it.

  * LIVE      -- every covered year's `sim_level_anchor` equals the live `year_level_anchor`
  * DIFFERENT -- some covered year disagrees; a measurement, and the years are published
  * ABSENT    -- the rows cannot answer; "we could not ask" is not "we asked and got no"

KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER. Every fixture below builds its rows from whatever
`world_level_identity()` currently says, so a re-fit of the anchor block moves all three fixtures
together and reds nothing. The live capture on disk happens to be a DIFFERENT world today (all ten
covered years disagree, up to +3.41 at 2019); none of these assertions depends on that staying true,
which is exactly the point -- when a fresh capture is taken, the LIVE branch starts firing in
production and this file does not move.

MUTATIONS PROVEN (2026-09-22), each against a green unmutated baseline, each firing on an assertion:
  1. `capture_world_identity` returns the live digest unconditionally (ignore disagreement)
       -> test_the_three_worlds_are_all_reachable AND
          test_a_capture_from_another_world_refuses_with_the_years_that_moved
  2. `capture_world_identity` returns `digest: None` unconditionally (withhold on everything)
       -> test_the_three_worlds_are_all_reachable
  3. drop `years_disagreeing` from the DIFFERENT branch
       -> test_a_capture_from_another_world_refuses_with_the_years_that_moved
  4. collapse ABSENT into the DIFFERENT branch's reason (one shared string)
       -> test_a_capture_that_cannot_be_asked_does_not_read_as_a_capture_that_answered_no
  5. `_svt_drift_belief` reads `grade["world_identity"]` for presence instead of comparing
       -> test_the_page_states_the_direction_only_for_a_grade_measured_in_the_live_world
          (the grade stamped with a foreign digest is the leg that fires)
  6. `_svt_drift_belief` falls back to its own fixed prose instead of the grade's reason
       -> test_the_withheld_reason_is_the_graders_measurement_not_the_readers_guess
  7. round the anchor comparison to 2dp instead of the digest's own 6
       -> test_the_comparison_is_keyed_to_the_precision_the_digest_canonicalises_at

TWO NOTES ON THE SWEEP ITSELF, because the flattering reading was available for both.

  * Mutation 5 was first written as "drop the digest check entirely", and the ABSENT leg caught it.
    That proves only that SOMETHING is checked. Re-written as "check PRESENCE, not identity", it
    reaches no leg unless a fixture carries a stamp that is present AND foreign -- which is the
    whole reason `_grade_stamped_with_a_foreign_world` exists.
  * Mutation 4 SURVIVED on its first run and the survival was the harness's fault, not a missing
    test: the patch replaced only the TAIL of an implicitly-concatenated literal, so the prefix
    naming `sim_level_anchor` was still in the string the assertion greps. Re-written over the
    whole literal it kills on
    `test_a_capture_that_cannot_be_asked_does_not_read_as_a_capture_that_answered_no`. Recorded
    rather than quietly re-run, because "the mutation did not fire" and "the mutation did not
    happen" are the two readings and only one of them is about this file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:  # pragma: no cover - import plumbing
    sys.path.insert(0, str(PROJECT))

from simulation.departure_level_anchor import world_level_identity  # noqa: E402
from tools.measure_churn_heterogeneity import (  # noqa: E402
    _ANCHOR_DP,
    capture_world_identity,
    run_instant,
)


def _live_anchors() -> dict[int, float]:
    return {int(y): v for y, v in (world_level_identity().get("anchors") or {}).items()}


def _rows(anchors: dict[int, float], per_year: int = 3) -> list[dict]:
    """A capture whose rows were drawn at `anchors`. Nothing else here is load-bearing."""
    return [
        {"customer_id": f"C{year}-{i}", "market_year": year, "sim_level_anchor": value}
        for year, value in sorted(anchors.items())
        for i in range(per_year)
    ]


@pytest.fixture
def live_world_rows() -> list[dict]:
    return _rows(_live_anchors())


@pytest.fixture
def other_world_rows() -> list[dict]:
    anchors = _live_anchors()
    # A move that no rounding can absorb, on ONE year, so the refusal is not an artefact of the
    # whole block having been replaced -- a single re-fit is the real-world shape.
    year = sorted(anchors)[0]
    return _rows({**anchors, year: anchors[year] + 1.5})


@pytest.fixture
def unstampable_rows() -> list[dict]:
    return [dict(r, sim_level_anchor=None) for r in _rows(_live_anchors())]


def test_the_three_worlds_are_all_reachable(live_world_rows, other_world_rows, unstampable_rows):
    """THE CONTROL OVER THE WHOLE PARTITION. A grader that withholds on everything fails here.

    This is the assertion the per-branch tests below cannot make for themselves: each of them is
    satisfied by a `capture_world_identity` that answers "cannot name a world" to every input, and
    a refusal that refuses everything is not a refusal. It is also the leg that fires when the
    grader is mutated the other way -- to stamp the live digest unconditionally -- because then the
    two refusing branches become unreachable.
    """
    live = capture_world_identity(live_world_rows)
    other = capture_world_identity(other_world_rows)
    absent = capture_world_identity(unstampable_rows)

    assert live["digest"] and not other["digest"] and not absent["digest"], (
        "all three outcomes must be reachable: a capture in the live world names it, and the two "
        "that cannot must not. Got live={!r} other={!r} absent={!r}".format(
            live["digest"], other["digest"], absent["digest"]))
    # AND THE TWO REFUSALS MUST BE TELLABLE APART. Both are falsy digests; only the reason
    # distinguishes "we asked and the answer was no" from "we could not ask".
    assert other["unavailable_because"] != absent["unavailable_because"]


def test_a_capture_in_the_live_world_names_it_and_says_what_it_does_not_cover(live_world_rows):
    got = capture_world_identity(live_world_rows)
    assert got["digest"] == world_level_identity()["digest"]
    assert got["unavailable_because"] is None
    assert got["years_disagreeing"] == {}
    assert got["years_covered"] == sorted(_live_anchors())
    # The claim is scoped to the covered years, and the scope is published rather than implied.
    assert "what_this_does_not_cover" in got


def test_a_capture_from_another_world_refuses_with_the_years_that_moved(other_world_rows):
    got = capture_world_identity(other_world_rows)
    assert got["digest"] is None
    gap = got["years_disagreeing"]
    assert gap, "a refusal that cannot show which year moved is an assertion, not a measurement"
    for year, moved in gap.items():
        assert moved["captured"] != moved["live"]
        assert moved["difference"] == pytest.approx(moved["live"] - moved["captured"], abs=1e-6)
        assert moved["decisions"] > 0
    # The remedy must be the one that can actually discharge it. Re-running the grader cannot:
    # the world is a property of the capture.
    assert "capture_departure_factors" in got["unavailable_because"]
    assert "measure_churn_heterogeneity" not in got["unavailable_because"]


def test_a_capture_that_cannot_be_asked_does_not_read_as_a_capture_that_answered_no(
        unstampable_rows):
    got = capture_world_identity(unstampable_rows)
    assert got["digest"] is None
    assert not got.get("years_disagreeing"), (
        "rows that carry no anchor cannot have disagreed with one; publishing a gap here would "
        "be manufacturing evidence for a refusal whose cause is an absence")
    assert "sim_level_anchor" in got["unavailable_because"]


def test_a_capture_holding_two_anchors_for_one_year_is_not_one_worlds_book():
    """The stamp only works because one year has one anchor. A capture that breaks that is not a
    world, and averaging the two to get a comparison would invent one that never ran."""
    anchors = _live_anchors()
    year = sorted(anchors)[0]
    rows = _rows(anchors) + [
        {"customer_id": "split", "market_year": year, "sim_level_anchor": anchors[year] + 0.5}]
    got = capture_world_identity(rows)
    assert got["digest"] is None
    assert str(year) in got["unavailable_because"]


def test_the_comparison_is_keyed_to_the_precision_the_digest_canonicalises_at():
    """Two anchors this check calls equal must be two anchors that would digest the same.

    `world_level_identity` canonicalises at `f"{value:.6f}"`. A comparison rounded coarser would
    call two different worlds one; rounded finer, float noise in the capture would refuse a world
    that digests identically. Neither is a judgement call -- the digest's own precision is the
    answer, and this pins the two together rather than pinning a number somebody chose.
    """
    assert _ANCHOR_DP == 6
    anchors = _live_anchors()
    year = sorted(anchors)[0]
    # Below the digest's resolution: same world, and must be named.
    imperceptible = _rows({**anchors, year: anchors[year] + 4e-7})
    assert capture_world_identity(imperceptible)["digest"], (
        "a difference the digest cannot see must not refuse a world the digest calls the same")
    # At the digest's resolution: a different world, and must refuse.
    perceptible = _rows({**anchors, year: round(anchors[year], 6) + 1e-5})
    assert capture_world_identity(perceptible)["digest"] is None


def test_the_run_instant_times_the_grading_and_says_so():
    """The date and the world answer different questions and the artefact must not conflate them.

    The shape this forbids is an artefact whose `generated_at` is fresh and whose figures are six
    re-fits old -- which is exactly the state the live grade is in.
    """
    got = run_instant()
    assert got["generated_at"].endswith("Z")
    assert (got["producing_commit"] is None) == (got["unavailable_because"] is not None)
    assert "not the capture" in got["what_it_times"]


# ---------------------------------------------------------------------------
# The reader's half: what the page is allowed to say about each of the three.
# ---------------------------------------------------------------------------

GRADE = PROJECT / "docs" / "observability" / "svt_drift_belief_grade.json"


def _grade_with(world: dict, tmp_path: Path, monkeypatch) -> dict:
    """Run `_svt_drift_belief` over the real grade with its world block swapped."""
    import tools.generate_value_arms_data as gen

    payload = json.loads(GRADE.read_text(encoding="utf-8"))
    payload["world_identity"] = world
    path = tmp_path / "grade.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(gen, "SVT_BELIEF_GRADE", path)
    return gen._svt_drift_belief()


def _grade_stamped_with_a_foreign_world() -> dict:
    """PRESENT AND FOREIGN -- the fixture mutation 5 needs and the reason it exists.

    A reader that tests for PRESENCE of a stamp passes this and must not.
    """
    return {"digest": None,
            "unavailable_because": "the capture's anchors disagree with the live world at 2019",
            "live_world": world_level_identity()["digest"],
            "years_disagreeing": {"2019": {"captured": 3.228064, "live": 6.637286,
                                           "difference": 3.409222, "decisions": 124}}}


def test_the_page_states_the_direction_only_for_a_grade_measured_in_the_live_world(
        tmp_path, monkeypatch):
    live = _grade_with({"digest": world_level_identity()["digest"], "unavailable_because": None,
                        "years_disagreeing": {}}, tmp_path, monkeypatch)
    foreign = _grade_with(_grade_stamped_with_a_foreign_world(), tmp_path, monkeypatch)
    absent = _grade_with({}, tmp_path, monkeypatch)

    # THE PARTITION AGAIN, ON THE READER. A page that withholds on everything is not fail-closed,
    # it is silent, and it passes each refusal leg below on its own.
    assert live["ceiling_clears"] is not None, (
        "a grade measured in the live world must license the direction, or the whole apparatus is "
        "a refusal nobody can ever discharge")
    assert foreign["ceiling_clears"] is None and absent["ceiling_clears"] is None

    # The numbers survive the refusal; only the direction is withheld. That distinction is the
    # grammar `_leg_in_this_world` established and this block must not re-decide it.
    for reading in (live, foreign, absent):
        assert reading["ceiling"] is not None
        assert reading["ceiling_null_low"] is not None
        assert reading["ceiling_null_high"] is not None
    assert live["ceiling_verdict_withheld_because"] is None
    assert foreign["ceiling_verdict_withheld_because"]
    assert absent["ceiling_verdict_withheld_because"]


def test_the_withheld_reason_is_the_graders_measurement_not_the_readers_guess(
        tmp_path, monkeypatch):
    """When the grade says WHY, the page says what the grade said.

    The string this replaced told the reader to re-run the grader "from a tree that stamps
    `world_identity`" -- a remedy that could never have discharged the refusal, because the world
    is a property of the capture and no grading run touches it. A reader who follows a remedy that
    cannot work has been misled more expensively than by a bare refusal.
    """
    foreign = _grade_with(_grade_stamped_with_a_foreign_world(), tmp_path, monkeypatch)
    assert foreign["ceiling_verdict_withheld_because"] == (
        _grade_stamped_with_a_foreign_world()["unavailable_because"])
    assert foreign["ceiling_world_gap"] == (
        _grade_stamped_with_a_foreign_world()["years_disagreeing"])

    # And a grade with no block at all still refuses, in the reader's own words, with a gap that
    # is EMPTY rather than invented.
    absent = _grade_with({}, tmp_path, monkeypatch)
    assert absent["ceiling_verdict_withheld_because"]
    assert absent["ceiling_world_gap"] == {}


def test_the_published_grade_carries_both_stamps():
    """The artefact on disk, not a fixture -- the two blocks must actually be on it.

    Keyed to presence and shape, never to a digest or a date: a re-capture in the live world will
    change both and must not red this.
    """
    grade = json.loads(GRADE.read_text(encoding="utf-8"))
    world = grade.get("world_identity")
    assert isinstance(world, dict), "the published grade names no world"
    assert (world.get("digest") is None) == bool(world.get("unavailable_because")), (
        "a world block must either name a digest or say why it cannot -- never both, never "
        "neither")
    instant = grade.get("run_instant")
    assert isinstance(instant, dict) and instant.get("generated_at")
