"""The defect: five contracts came back DIED and no control had asserted anything about any of
them.

MEASURED 2026-09-06 on `tools/grid_intensity_feed_contract_battery`. Rows M3, M4, M7, M9 and M10
were run against `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` and all five said
DIED. All five named the SAME node. Every one was `ERROR at setup`: the module-scoped
`real_publish` fixture publishes off the real caches, each mutation made that publish raise --
`AttributeError`, `TypeError`, `KeyError`, `FuelOutturnUnavailable` -- and no control body ran a
line. One shared fixture scored five different contracts, and the log read exactly like five
contracts being proved, because `-x` prints only the first red.

`died` is `returncode != 0` and that is right: an ERROR is a red and it is a kill. What it is not
is evidence that a CONTROL fired, and the engine could not tell the reader which it had. These
tests are the control on the stamp that tells them apart.

WHY THE STAMP AND NOT A RULE. Refusing to call a setup error a kill would be wrong -- a subject
that can no longer be constructed is a real red, and an honest fail-closed refusal (M9's
`FuelOutturnUnavailable`) arrives by exactly this route. The reader needs the distinction, not a
verdict change, so the cell carries it and `survived_all` is untouched.
"""
from __future__ import annotations

import pytest

from tools import contract_battery as battery
from tools.direction_contract_battery import SPEC

_ASSERT_FAILS = """
def test_it_asserts_and_fails():
    assert 1 == 2
"""

_FIXTURE_RAISES = """
import pytest

@pytest.fixture(scope="module")
def broken():
    raise RuntimeError("the fixture could not be built")

def test_never_runs_a_line_of_its_own_body(broken):
    assert broken
"""

_BOTH = _ASSERT_FAILS + _FIXTURE_RAISES


def _suite(tmp_path, source: str, name: str) -> str:
    path = tmp_path / name
    path.write_text(source, encoding="utf-8")
    return str(path)


def test_run_suite_separates_the_two_RED_WORDS_pytest_prints(tmp_path):
    """`_FAILED` unions FAILED and ERROR deliberately -- both are reds and both have to be
    deselected from the baseline. `_ERRORED` is the half that says no body ran.

    BOTH SIDES IN ONE CONTROL, over the whole partition. A regex that matched everything would
    satisfy an errors-only leg, and one that matched nothing would satisfy a failures-only leg;
    only asserting the two against each other can fail either way.

    MUTATION (must fire): make `_ERRORED` read `^(?:FAILED|ERROR)` -- the union it must not be.
    """
    failing = battery._run_suite(_suite(tmp_path, _ASSERT_FAILS, "test_asserts.py"), (), False)
    erroring = battery._run_suite(_suite(tmp_path, _FIXTURE_RAISES, "test_errors.py"), (), False)

    assert failing["returncode"] != 0 and erroring["returncode"] != 0, (
        "both stand-in suites must be RED, or nothing below is about the distinction"
    )
    assert failing["failed"] and not failing["errored"], (
        f"an assertion failure was recorded as an error: {failing}"
    )
    assert erroring["failed"] and erroring["errored"] == erroring["failed"], (
        f"a setup error was not recorded as one: {erroring}"
    )


def test_a_MIXED_red_is_not_stamped_because_a_control_body_DID_run(tmp_path):
    """The partition's third state, and the one that stops the stamp being a synonym for `died`.

    A suite where one test errored in setup AND another failed its own assertion has evidence in
    it: a control fired. `died_by_setup_error_only` must be False there, or the stamp would read
    "no control body ran" over a round where one did.

    MUTATION (must fire): drop the `set(...) == set(...)` comparison for `bool(r["errored"])`.
    """
    mixed = battery._run_suite(_suite(tmp_path, _BOTH, "test_both.py"), (), False)
    assert len(mixed["failed"]) == 2 and len(mixed["errored"]) == 1, (
        f"the mixed stand-in did not produce one of each: {mixed}"
    )

    row: dict = {"per_suite": {}}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(battery, "_run_suite", lambda suite, deselect, stop_first: mixed)
        battery._score(SPEC, row, ["tests/mixed.py"], {"tests/mixed.py": ()},
                       {"tests/mixed.py": True}, {})
    assert row["per_suite"]["tests/mixed.py"]["died"] is True
    assert row["per_suite"]["tests/mixed.py"]["died_by_setup_error_only"] is False


def test_the_STAMP_partitions_a_setup_error_kill_from_an_assertion_kill_and_from_a_survivor(
        tmp_path):
    """THE CONTROL OVER THE WHOLE PARTITION, written as one test rather than a leg per branch --
    a stamp that fired on everything and a stamp that fired on nothing each pass a single leg.

    All three states are asserted here, and each is REACHABLE by construction: the two red cells
    come from stand-in suites that really run, so neither branch can be dead.

    MUTATION (must fire): stamp `r["died"]` alone, or stamp nothing at all.
    """
    cells = {
        "setup_error": battery._run_suite(
            _suite(tmp_path, _FIXTURE_RAISES, "test_e.py"), (), False),
        "assertion": battery._run_suite(
            _suite(tmp_path, _ASSERT_FAILS, "test_f.py"), (), False),
        "survivor": {"suite": "tests/green.py", "returncode": 0, "failed": [], "errored": [],
                     "seconds": 0.0, "tail": []},
    }
    row: dict = {"per_suite": {}}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(battery, "_run_suite",
                   lambda suite, deselect, stop_first: cells[suite])
        battery._score(SPEC, row, list(cells), dict.fromkeys(cells, ()),
                       dict.fromkeys(cells, True), {})

    stamped = {name: row["per_suite"][name]["died_by_setup_error_only"] for name in cells}
    assert stamped == {"setup_error": True, "assertion": False, "survivor": False}, (
        f"the stamp does not partition the three states: {stamped}"
    )
    # AND THE VERDICT IS UNTOUCHED. The stamp is a caveat on the cell, not a demotion: a setup
    # error is still a kill, and a change that quietly stopped counting it would break every
    # honest fail-closed refusal this family measures.
    assert row["per_suite"]["setup_error"]["died"] is True
