"""A household's departure ends its riding leg's term at the departure, and never later than it ran.

The defect (`SEAT_FINDING_A_GAS_SVT_TERM_STARTED_OFF_A_CAP_QUARTER_..._2026-10-25`): the run set a
riding leg's `term_end` to the departure date outright. A declined gas fix splices default segments
that pop after the electricity leg has already left at a later cap boundary, so each segment was
stretched to that day: PROS-2017-0393g carried four rows of term 18 all ending 2024-10-01, settled
four times over, and each month was billed at the mean of the covering rates.
"""

import ast
from pathlib import Path

from simulation.run_phase2b import _riding_leg_term_end

_DEPARTED = "2024-10-01"


def test_the_departure_cuts_a_term_past_it_and_leaves_a_term_that_ends_first():
    # Both branches, asserted together: a rule that always returned the departure (the defect)
    # fails the second line, and one that never cut fails the first.
    assert _riding_leg_term_end("2024-12-20", _DEPARTED) == _DEPARTED
    assert _riding_leg_term_end("2024-04-01", _DEPARTED) == "2024-04-01"
    # A term ending ON the departure is unchanged either way; exclusive ends agree.
    assert _riding_leg_term_end(_DEPARTED, _DEPARTED) == _DEPARTED


def test_the_departure_compares_on_the_date_when_the_term_end_carries_a_time():
    assert _riding_leg_term_end("2024-04-01T00:00:00", _DEPARTED) == "2024-04-01T00:00:00"
    assert _riding_leg_term_end("2024-12-20T00:00:00", _DEPARTED) == _DEPARTED


def test_the_run_loop_never_assigns_the_departure_to_a_term_end_outright():
    """The loop is reachable only by a decade run, so the wiring is read off the source: no
    assignment to `term_end_str` may take `_departed_on[...]` bare."""
    tree = ast.parse(Path("simulation/run_phase2b.py").read_text())
    bare = [
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "term_end_str" for t in node.targets)
        and isinstance(node.value, ast.Subscript)
        and isinstance(node.value.value, ast.Name) and node.value.value.id == "_departed_on"
    ]
    assert not bare, f"term_end_str set to the departure outright at line(s) {bare}"
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "_riding_leg_term_end"
    ]
    assert calls, "the run loop no longer cuts a riding term through `_riding_leg_term_end`"
