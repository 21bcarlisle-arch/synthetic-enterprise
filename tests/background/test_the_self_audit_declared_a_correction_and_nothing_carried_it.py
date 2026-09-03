"""The seat's `wrong` section had no validator, no grader and no reader for its correction state.

THE REPORT AND WHAT IT ACTUALLY WAS. The director, 2026-09-03: *"DIRECTION.yaml's `wrong` section
is five empty rows. The self-audit isn't being populated, and it's the field that makes the seat
correctable."* Checked against the record rather than taken: the twenty most recent committed
`DIRECTION.yaml` versions carry a non-empty `what` in **every** row, 0 empty of 113, and all 69
recorded orientations in `decisions.jsonl` likewise. The text was populated. But three separate
legs of that section were not, and together they are the defect he named:

  1. `validate()` checked `focus` field by field and `not_now` field by field and said **nothing
     at all** about `wrong`. Five rows of `{}` would have validated, recorded, published and read
     from outside exactly like five errors honestly declared. The failure he described was one the
     tree could not have distinguished from health -- which is the same thing as it not existing.
  2. `corrected` was written faithfully into `DIRECTION.yaml` on every row and then **dropped at
     the first hop**: `delivery_seat` recorded `[r.get("what") for r in ...]`. `git grep corrected`
     over `background/`, `tools/`, `site/` and `tests/` returned no reader of the field anywhere.
     212 declared errors were served on the published page with no correction state on any of them.
  3. The brief handed the seat `previous_focus` and never `previous_wrong`, so the `corrected`
     verdict was RECONSTRUCTED from whatever the orienting session happened to remember rather
     than GRADED against the list it was asked about -- and an error nobody remembered left the
     record with no verdict at all, silently.

Legs 2 and 3 are the same shape as `feedback_counting_events_cannot_see_an_empty_event`: every
surface counted the errors and none of them read one.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from background import delivery_seat as seat
from background import direction as d

NOW = datetime(2026, 9, 3, 5, 20, tzinfo=timezone.utc)


def _record(**over) -> dict:
    base = {
        "version": 1,
        "oriented_at": NOW.isoformat(),
        "focus": [{"id": "C1_pricing", "what": "a credible flat control",
                   "why": "the arm cannot be scored against a straw man"}],
        "not_now": [{"what": "wiring the value arm", "why": "it would be scored against a control"
                                                            " that is not average behaviour"}],
        "wrong": [{"what": "the reconciler manufactured the fork it existed to close",
                   "corrected": True}],
    }
    base.update(over)
    return base


# --------------------------------------------------------------------------- #
# Leg 1: the shape the director described is now REFUSED rather than served    #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("rows, needle", [
    ([{}, {}, {}, {}, {}], "has no what"),
    ([{"corrected": False}], "has no what"),
    ([{"what": "   ", "corrected": False}], "has no what"),
    ([{"what": None, "corrected": False}], "has no what"),
    (["a bare string is not a row"], "has no what"),
])
def test_an_EMPTY_self_audit_row_is_refused_whatever_kind_of_empty_it_is(rows, needle):
    """The exact report: five empty rows. Before this clause existed the record validated, the
    seat committed it, the page served it, and the only thing in the world that could tell the
    difference was a human opening the file.

    MUTATION (must fire): delete the `wrong` clause from `validate()`.
    """
    problems = d.validate(_record(wrong=rows))

    assert any(needle in p for p in problems), problems


@pytest.mark.parametrize("corrected", [None, "yes", 1, 0, "false"])
def test_an_error_with_NO_CORRECTION_STATE_is_refused(corrected):
    """`corrected` is required as a BOOLEAN and not merely present. It is the field the director
    named -- *"it's the field that makes the seat correctable"* -- and a truthy string is not a
    verdict: `corrected: "not yet"` reads as corrected to every consumer that tests it for truth.
    """
    row = {"what": "the count was taken from a grep whose exclusions were never stated"}
    if corrected is not None:
        row["corrected"] = corrected

    problems = d.validate(_record(wrong=[row]))

    assert any("corrected: true|false" in p for p in problems), problems


def test_a_POPULATED_self_audit_passes_and_an_ABSENT_one_is_not_an_error():
    """The section is allowed to be empty -- a stretch can genuinely have got nothing wrong -- and
    it is not allowed to be full of nothing. Those are different, and only the second is a fault.
    """
    assert d.validate(_record()) == []
    assert d.validate(_record(wrong=[])) == []
    record = _record()
    del record["wrong"]
    assert d.validate(record) == []


def test_the_refusal_NAMES_the_row_so_the_seat_can_fix_the_one_that_is_wrong():
    """Four good rows and one empty must not read as "the wrong section is bad". CLAUDE.md: write
    refusals that name their reason."""
    good = {"what": "an error worth recording", "corrected": False}
    problems = d.validate(_record(wrong=[good, good, {}, good]))

    assert len(problems) == 1 and "wrong[2]" in problems[0], problems


# --------------------------------------------------------------------------- #
# Leg 2: `corrected` survives the hop out of the record                        #
# --------------------------------------------------------------------------- #

def test_the_correction_state_TRAVELS_with_the_error_out_of_the_direction_record():
    """The seat's recorded row carried `[what, what, what]` and threw the verdict away. Reading
    the source is the honest test here: the alternative is running a full orientation, and what
    broke was one comprehension, not a behaviour under load.

    MUTATION (must fire): revert the record line to `[r.get("what") for r in parsed.wrong]`.
    """
    import inspect

    source = " ".join(inspect.getsource(seat.orient).split())

    assert '"wrong": [{"what": r.get("what"), "corrected": bool(r.get("corrected"))}' in source, (
        "the seat must record the correction state beside the error, not the error alone"
    )


@pytest.mark.parametrize("stored, expected", [
    # The shape written from 2026-09-03: a graded verdict, kept.
    ([{"what": "an error", "corrected": True}], [{"what": "an error", "corrected": True}]),
    ([{"what": "an error", "corrected": False}], [{"what": "an error", "corrected": False}]),
    # The legacy shape, 69 recorded orientations of it. NOT MIGRATED and NOT GUESSED AT.
    (["an error"], [{"what": "an error", "corrected": None}]),
    # A row that carried the field but not a verdict is unknown, not false.
    ([{"what": "an error", "corrected": "maybe"}], [{"what": "an error", "corrected": None}]),
    ([], []),
    (None, []),
])
def test_the_recorded_audit_reads_in_BOTH_shapes_and_never_invents_a_verdict(stored, expected):
    """`decisions.jsonl` is append-only, so the 69 pre-change rows are read rather than rewritten.
    Their correction state is genuinely UNKNOWN, and "we did not record whether this was fixed" is
    a different claim from "this was not fixed". Folding the first into the second would publish
    a hundred false accusations against the machine's own record.

    MUTATION (must fire): return `bool(item.get("corrected"))` for a legacy string row.
    """
    assert d.wrong_rows({"wrong": stored}) == expected


def test_the_published_panel_SPLITS_open_from_corrected_from_not_recorded(monkeypatch):
    """A reader met 212 declared mistakes with no way to tell a live defect from a closed one,
    which reads as a machine that lists its faults and never repairs them.

    MUTATION (must fire): count `correction_not_recorded` rows as uncorrected.
    """
    from tools import generate_delivery_page as page

    monkeypatch.setattr(page.direction_mod, "read_decisions", lambda limit=50: [
        {"at": "2026-09-03T05:20:12+00:00", "wrong": [
            {"what": "still open", "corrected": False},
            {"what": "fixed", "corrected": True},
        ]},
        {"at": "2026-09-02T20:21:16+00:00", "wrong": ["written before the field survived"]},
    ])

    panel = page.what_it_got_wrong()

    assert [e["corrected"] for e in panel["entries"]] == [False, True, None]
    assert panel["outstanding"] == 1
    assert panel["corrected"] == 1
    assert panel["correction_not_recorded"] == 1


def test_the_RENDERED_page_shows_the_correction_state_and_not_only_the_error():
    """Done means the rendered value changed, and this panel's whole subject is whether the
    machine can be seen correcting itself. A generator that emits the field to a page that drops
    it is the same defect one layer along.
    """
    markup = (seat.PROJECT_DIR / "site" / "harness" / "index.html").read_text(encoding="utf-8")
    body = markup[markup.index("function renderDeliveryWrong"):]
    body = body[:body.index("function renderDeliveryNext")]

    assert "x.corrected === true" in body and "x.corrected === false" in body, (
        "the panel must distinguish corrected from still-open"
    )
    assert "correction not recorded" in body, (
        "the ungraded legacy rows must say they are ungraded rather than borrow either verdict"
    )
    assert "w.outstanding" in body, "the reader gets the count of what is still open"


# --------------------------------------------------------------------------- #
# Leg 3: the correction verdict is GRADED, not remembered                      #
# --------------------------------------------------------------------------- #

def test_the_brief_hands_the_seat_ITS_OWN_LAST_ERRORS_to_grade():
    """The seat was required to write `corrected: true|false` and was never shown the list it was
    grading. Every verdict in the record was therefore reconstructed from what the session
    happened to notice, and an error nobody remembered simply left the record with no verdict --
    the silent half of the failure the director reported.

    This is the same shape as `previous_focus_drawn`, which exists because a steer that quietly
    did nothing looked identical from outside to a steer that was taken.

    MUTATION (must fire): drop `previous_wrong` from `build_brief`.
    """
    import inspect

    source = " ".join(inspect.getsource(seat.build_brief).split())

    assert '"previous_wrong": direction_mod.wrong_rows(previous)' in source, (
        "the brief must carry last stretch's errors, not only last stretch's focus"
    )


def test_the_seat_is_TOLD_that_an_uncorrected_error_may_not_silently_disappear():
    """Handing the rows over is half of it; the instruction that an outstanding error must be
    re-listed or shown fixed is what makes the hand-over bite. Without it the seat may read
    `previous_wrong` and write a fresh list every time, which is what it has been doing.
    """
    spec = " ".join(seat.CHARTER.split())

    assert "previous_wrong" in spec, "the spec must point the seat at the list it is grading"
    assert "has not been fixed; it has been forgotten" in spec, (
        "the spec must say what a silently-vanishing error means"
    )


def test_the_list_to_grade_survives_the_prompt_TRUNCATION_that_would_have_eaten_it():
    """`previous_wrong` is the thirteenth key of the brief, behind `commits` and behind the
    rendered commit list, inside a `json.dumps(...)[:60_000]`. On a long stretch the seat would
    have been told to grade a list that had been cut off the end of its own prompt -- and would
    then do exactly what it did before the field existed: write the errors it remembered.

    An input a truncation can silently remove is not an input. This is the same lesson as the
    commit list above it in `_prompt`, which is why it is one comment and not two.

    MUTATION (must fire): leave `previous_wrong` inside the JSON dump only.
    """
    brief = {
        "commits": [{"subject": "x" * 400} for _ in range(400)],   # comfortably over the 60k cap
        "shape": {"available": True, "rendered": "a stretch"},
        "previous_wrong": [
            {"what": "a needle that must survive the cap", "corrected": False},
            {"what": "one already fixed", "corrected": True},
            {"what": "one written before the field existed", "corrected": None},
        ],
    }

    prompt = seat._prompt(brief)

    assert "a needle that must survive the cap" in prompt
    assert "STILL OPEN" in prompt and "corrected" in prompt
    assert "no verdict recorded" in prompt, (
        "an ungraded legacy row must not be presented as either fixed or open"
    )
    assert "1 of 3 still open." in prompt
    # ...and the proof the cap was actually in play, so this test cannot pass by the brief
    # happening to be small.
    assert len(json_dump_of(brief)) > 60_000


def json_dump_of(brief: dict) -> str:
    import json
    return json.dumps(brief, indent=1)


def test_an_EMPTY_previous_audit_says_which_kind_of_empty_it_is():
    """A machine reporting no mistakes is either not looking or not saying, and those read
    identically from outside. The panel already states which; the prompt now does too."""
    prompt = seat._prompt({"shape": {"available": True, "rendered": ""}, "previous_wrong": []})

    assert "NO PREVIOUS SELF-AUDIT ROWS" in prompt
    assert "a seat that stopped looking" in prompt


def test_the_brief_actually_ASSEMBLES_the_field_against_the_real_record():
    """The source check above pins the call; this one proves it runs and returns the shape the
    seat will read, against this repository's own `decisions.jsonl`."""
    brief = seat.build_brief(now=NOW)

    assert "previous_wrong" in brief
    assert isinstance(brief["previous_wrong"], list)
    for row in brief["previous_wrong"]:
        assert set(row) == {"what", "corrected"}
        assert isinstance(row["what"], str) and row["what"].strip()
        assert row["corrected"] in (True, False, None)
