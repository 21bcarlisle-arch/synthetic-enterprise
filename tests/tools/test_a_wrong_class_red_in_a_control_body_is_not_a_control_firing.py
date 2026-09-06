"""The defect: a control body that dies on the WRONG EXCEPTION CLASS, before it reaches any
assertion, is a `FAILED` -- so it clears `died_by_setup_error_only` and the cell reads clean.

MEASURED 2026-09-06 on `tools/grid_intensity_feed_contract_battery` row M10, at fingerprint
`aa5ce7785789`: DIED, `died_by_setup_error_only` FALSE, `errored` EMPTY, naming a control. Both
control bodies were red on `AttributeError: 'list' object has no attribute 'items'` raised at
`sim/elexon_fuel_outturn.py:845` -- they ran, and neither ever asserted. `ff2dd516d` closed the
setup-error door after five rows had been read as proved and were not; this is the same door one
room over, and it is where the family already knows it is weakest. M2/M11 and M10/M14/M15 are
three rows that exist BECAUSE a wrong-type substitution reddens a suite on the type system rather
than on the property.

WHAT THE ROUND HAD TO CHANGE -- and it was less than the claim assumed. The claim was drawn saying
the exception class "is not in that output at all", so the round itself had to change: a
`--tb=line` pass, or a second pass over the rows that died. Measured, that is false. `-rfE`
already prints `FAILED <node> - <Class>: <message>`. What deletes the class is TERMINAL WIDTH:
pytest truncates the summary line to `COLUMNS`, captured output has no tty so `COLUMNS` defaults
to 80, and every node id in this repository is longer than 80 characters on its own. The class was
printed and then cut off. So the fix is one environment variable and no extra pytest pass -- which
is what makes it affordable on a family whose slowest cell is 655s.

`test_the_class_survives_a_node_id_longer_than_a_default_terminal` is the control on exactly that,
and it is the one that would have caught the real defect. Without the widening every class parses
as `None`, the stamp fails closed to `None`, and the partition below cannot hold.
"""
from __future__ import annotations

import pytest

from tools import contract_battery as battery
from tools.direction_contract_battery import SPEC

#: A control that reaches its verdict and refuses. `died` here IS evidence about the contract.
_ASSERTS_AND_FAILS = """
def test_it_reaches_its_verdict_and_refuses():
    assert 1 == 2, "the control fired"
"""

#: THE SUBJECT OF THIS FILE. The body runs and dies on a class that is not an assertion, exactly
#: as M10's two controls did -- same class, same shape, before anything is asserted.
_WRONG_CLASS_IN_BODY = """
def test_the_body_runs_and_never_reaches_its_assertion():
    series = []
    collapsed = series.items()      # AttributeError, the way M10's mutation reddens the suite
    assert collapsed
"""

#: `ff2dd516d`'s subject, kept here to prove the two stamps are DISJOINT and not two names for
#: one thing: no body ran at all, so this file's stamp must stay False on it.
_SETUP_ERROR = """
import pytest

@pytest.fixture(scope="module")
def broken():
    raise RuntimeError("the fixture could not be built")

def test_never_runs_a_line_of_its_own_body(broken):
    assert broken
"""

_LONG_NAME = (
    "test_a_control_whose_node_id_is_as_long_as_the_ones_this_repository_actually_writes"
    "_every_single_day_of_the_week"
)
_LONG_NODE_WRONG_CLASS = f"""
def {_LONG_NAME}():
    series = []
    assert series.items()
"""


def _suite(tmp_path, source: str, name: str) -> str:
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    return str(path)


def _cell(tmp_path, source: str, name: str) -> dict:
    return battery._run_suite(_suite(tmp_path, source, name), (), False)


def test_the_class_survives_a_node_id_longer_than_a_default_terminal(tmp_path):
    """THE CONTROL ON THE ACTUAL DEFECT, and the reason no second pytest pass was needed.

    pytest prints `FAILED <node> - <Class>: <msg>` and then truncates the whole line to `COLUMNS`.
    Captured, that default is 80, and this repository has no node id shorter than that -- so the
    class was reliably printed and reliably deleted. Asserting a SHORT name here would pass with
    the widening removed and prove nothing.

    MUTATION (must fire): drop `env=` from `_run_suite`'s `subprocess.run`, or set
    `_WIDE_COLUMNS` to "80".
    """
    cell = _cell(tmp_path, _LONG_NODE_WRONG_CLASS, "test_a_long_one.py")
    node = next(n for n in cell["failed"] if n.endswith(_LONG_NAME))
    assert len(node) > 80, (
        f"the stand-in node id is {len(node)} chars -- too short to test truncation at all"
    )
    assert cell["red_classes"][node] == "AttributeError", (
        "the exception class was truncated away by the captured terminal width: "
        f"{cell['red_classes']}"
    )


def test_the_red_class_reader_fails_closed_and_knows_a_bare_rewritten_assert():
    """`None` must mean "the line did not say", never "no control fired".

    A bare `assert x == y` prints with NO class name -- pytest rewrites it and shows the
    expression. Reading that as an unknown class would stamp every honest assertion failure as a
    wrong-class red, which is the exact inversion this file exists to prevent.

    MUTATION (must fire): drop the `_BARE_ASSERT` branch, or return `"Unknown"` instead of `None`.
    """
    assert battery._red_class("assert 1 == 2") == "AssertionError"
    assert battery._red_class("AssertionError: the control fired") == "AssertionError"
    assert battery._red_class("Failed: DID NOT RAISE <class 'TypeError'>") == "Failed"
    assert battery._red_class("AttributeError: 'list' object has no attribute 'items'") == (
        "AttributeError")
    assert battery._red_class(None) is None and battery._red_class("") is None


def test_the_STAMP_partitions_wrong_class_from_a_real_control_firing_from_a_setup_error(tmp_path):
    """THE CONTROL OVER THE WHOLE PARTITION, written as one test rather than a leg per branch.

    A stamp that fired on every death passes a wrong-class-only leg. A stamp that fired on nothing
    passes a control-fired leg and a survivor leg. Only the four states asserted against each
    other can fail in both directions -- and each is REACHABLE by construction here, because the
    three red cells come from stand-in suites that really run.

    The setup-error cell is what proves the two stamps are DISJOINT rather than synonyms.

    MUTATION (must fire): widen `_no_verdict_was_reached` to `return r["died"]`, or narrow it to
    `return False`; either reddens this, and neither reddens a single-leg test.
    """
    cells = {
        "wrong_class": _cell(tmp_path, _WRONG_CLASS_IN_BODY, "test_w.py"),
        "control_fired": _cell(tmp_path, _ASSERTS_AND_FAILS, "test_c.py"),
        "setup_error": _cell(tmp_path, _SETUP_ERROR, "test_s.py"),
        "survivor": {"suite": "tests/green.py", "returncode": 0, "failed": [], "errored": [],
                     "red_classes": {}, "seconds": 0.0, "tail": []},
    }
    for name in ("wrong_class", "control_fired", "setup_error"):
        assert cells[name]["returncode"] != 0, (
            f"the {name} stand-in was GREEN -- nothing below is about the partition"
        )

    row: dict = {"per_suite": {}}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(battery, "_run_suite", lambda suite, deselect, stop_first: cells[suite])
        battery._score(SPEC, row, list(cells), dict.fromkeys(cells, ()),
                       dict.fromkeys(cells, True), {})

    stamped = {n: row["per_suite"][n]["died_by_wrong_class_in_a_control_body"] for n in cells}
    assert stamped == {"wrong_class": True, "control_fired": False,
                       "setup_error": False, "survivor": False}, (
        f"the stamp does not partition the four states: {stamped}"
    )
    # AND THE TWO STAMPS ARE DISJOINT. Read together they say WHERE the red was (a body, or no
    # body) and WHAT it was (a verdict, or a crash). A row that satisfied both would mean the
    # scoping to `failed - errored` had come undone.
    setup = row["per_suite"]["setup_error"]
    assert setup["died_by_setup_error_only"] is True, "the disjointness cell is not a setup error"
    assert not any(row["per_suite"][n]["died_by_setup_error_only"]
                   and row["per_suite"][n]["died_by_wrong_class_in_a_control_body"]
                   for n in cells), "a cell carries both stamps -- the scoping has come undone"
    # AND THE VERDICT IS UNTOUCHED. A caveat on the cell, not a demotion: a wrong-class red is
    # still a red and still a kill, and `survived_all` never sees this field.
    assert row["per_suite"]["wrong_class"]["died"] is True


def test_an_UNREADABLE_class_stamps_None_and_never_False(tmp_path):
    """The fail-closed leg, and it cannot be reached through `_run_suite` any more -- which is
    the point of the widening. It is reachable through a cell whose class the output did not
    carry, and that is what an OLD results file resumed from disk looks like.

    `False` there would be indistinguishable from "a control fired". `None` cannot be misread.

    MUTATION (must fire): make the `any(cls is None ...)` branch `return False`, or drop it so
    the function falls through to `return True`.
    """
    stale = {"suite": "s", "returncode": 1, "died": True, "errored": [],
             "failed": ["tests/x.py::test_y"], "seconds": 0.0, "tail": []}
    assert battery._no_verdict_was_reached(stale) is None, (
        "a cell with no class recorded was given a verdict it cannot support"
    )
