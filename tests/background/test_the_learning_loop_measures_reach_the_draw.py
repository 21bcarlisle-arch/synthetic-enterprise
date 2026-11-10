"""The defect: the learning loop's measures were named in its design and read nowhere the draw is made,
so an area could keep missing predictions with nothing in front of the seat saying so.

MUTATIONS (each must fire): `>= STOP_MISSES` -> `> STOP_MISSES`; count `missed` instead of
code+reader towards the stop; drop a malformed trailer silently; drop `learning_loop` from
`build_brief`; drop the `_render_learning_loop` call from `_prompt`.
"""
import inspect

from background import delivery_seat as seat
from background import learning_loop as loop


def _log(*bodies: str) -> str:
    return "".join(f"\x00{i:07x}\x01{b}\n" for i, b in enumerate(bodies))


def test_the_stop_condition_can_be_met_and_can_be_missed():
    m = loop.measures(log_text=_log(
        "fix one\n\nGraded: level-dd held=5 missed=3 code=2 reader=1",
        "fix two\n\nGraded: closing held=1 missed=4 code=2 reader=0 width=0.4",
    ))
    areas = m["by_area"]
    # The partition first: one area over the line, one under it -- a stop that always fires or
    # never fires fails here before any value is read.
    assert areas["level-dd"]["stop_condition_met"] and not areas["closing"]["stop_condition_met"]
    # Misses from other causes (a multi-change book, the domain) do not count towards the stop.
    assert areas["closing"]["code_or_reader"] == 2 and areas["closing"]["missed"] == 4
    assert areas["level-dd"]["hit_rate"] == 0.625 and areas["closing"]["median_width"] == 0.4


def test_regressions_and_cold_reads_are_counted_per_fix_and_per_read():
    m = loop.measures(log_text=_log(
        "a\n\nGraded: level-dd held=1 missed=0 regressed=1",
        "b\n\nGraded: level-dd held=1 missed=0\nCold-read: explore new-classes=3",
    ))
    assert m["regressions_per_fix"] == 0.5 and m["fixes_graded"] == 2
    assert m["escapes_per_cold_read"] == [3]


def test_a_malformed_grade_is_reported_not_dropped():
    m = loop.measures(log_text=_log(
        "a\n\nGraded: level-dd held=two missed=1",
        "b\n\nGraded: level-dd held=1 missed=1 code=1 reader=1",
        "c\n\nCold-read: explore classes=1",
    ))
    assert m["by_area"] == {} and len(m["unparsed"]) == 3


def test_the_measures_are_in_the_brief_and_printed_where_the_seat_draws():
    assert '"learning_loop": learning_loop.measures()' in inspect.getsource(seat.build_brief)
    assert "_render_learning_loop(" in inspect.getsource(seat._prompt)
    empty = seat._render_learning_loop(loop.measures(log_text=""))
    assert "NOTHING GRADED" in empty
    met = seat._render_learning_loop(loop.measures(
        log_text=_log("x\n\nGraded: level-dd held=0 missed=3 code=3")))
    assert "STOP" in met and "NOTHING GRADED" not in met
