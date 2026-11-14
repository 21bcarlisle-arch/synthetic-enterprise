"""The defect: the learning loop's measures were named in its design and read nowhere the draw is made,
so an area could keep missing predictions with nothing in front of the seat saying so.

MUTATIONS (each must fire): `>= STOP_MISSES` -> `> STOP_MISSES`; count `missed` instead of
code+reader towards the stop; drop a malformed trailer silently; drop `learning_loop` from
`build_brief`; drop the `_render_learning_loop` call from `_prompt`; read the map's existence
alone (or never) instead of which grades came after it; print STOP for a mapped area.
"""
import inspect

from background import delivery_seat as seat
from background import learning_loop as loop


def _log(*bodies: str) -> str:
    return "".join(f"\x00{i:07x}\x01{b}\n" for i, b in enumerate(bodies))


def test_the_stop_condition_can_be_met_and_can_be_missed():
    m = loop.measures(maps=_no_maps, log_text=_log(
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


def _no_maps(area):
    return None


def test_a_landed_map_spends_the_stop_and_the_line_counts_the_misses_after_it():
    """The defect: the brief printed "STOP: map the area first" for level-dd and repayment-posting
    with both maps on origin, steering every draw to redo finished work."""
    log = _log("a\n\nGraded: level-dd held=0 missed=1 code=1",
               "b\n\nGraded: level-dd held=0 missed=1 reader=1",
               "c\n\nGraded: level-dd held=2 missed=1 code=1")
    unmapped = loop.measures(log_text=log, maps=_no_maps)["by_area"]["level-dd"]
    # Map landed after all three misses: commits 0-2 are not its descendants.
    mapped = loop.measures(log_text=log, maps=lambda area: {
        "path": "docs/design/LEVEL_DD_AREA_MAP_x.md", "sha": "m", "after": set()})["by_area"]
    # Map landed between them: only commit 0000000 (newest in `_log`'s order) came after it.
    between = loop.measures(log_text=log, maps=lambda area: {
        "path": "p", "sha": "m", "after": {"0000000"}})["by_area"]["level-dd"]
    # The partition first: the same three misses read STOP with no map and not with one.
    assert unmapped["stop_condition_met"] and not mapped["level-dd"]["stop_condition_met"]
    assert mapped["level-dd"]["misses_since_map"] == 0
    assert between["misses_since_map"] == 1 and between["graded_since_map"] == 1
    stop = seat._render_learning_loop(loop.measures(log_text=log, maps=_no_maps))
    landed = seat._render_learning_loop({**loop.measures(log_text=log), "by_area": mapped})
    assert "-- STOP" in stop and "map landed" not in stop
    assert "-- STOP" not in landed and "map landed m; misses since: 0 of 0 graded" in landed


def test_the_live_maps_are_found_by_their_convention():
    # HEAD, not origin/main: the commit gate runs in a scratch tree with no remote refs.
    assert loop.area_map("no-such-area-ever", rev="HEAD") is None
    m = loop.area_map("repayment-posting", rev="HEAD")
    assert m and m["path"].startswith("docs/design/REPAYMENT_POSTING_AREA_MAP") and m["sha"]


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
    met = seat._render_learning_loop(loop.measures(maps=_no_maps,
        log_text=_log("x\n\nGraded: level-dd held=0 missed=3 code=3")))
    assert "STOP" in met and "NOTHING GRADED" not in met
