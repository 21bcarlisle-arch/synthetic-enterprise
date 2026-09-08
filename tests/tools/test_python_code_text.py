"""The discriminator that source-scanning controls stand on, exercised in BOTH directions.

A control that reads Python by substring is wrong two ways at once, and this project has paid for
both inside one subsystem on one day (2026-09-08): the seat-executor schedule control was RED AT
HEAD because `launch_long_job.py` names the cgroup in prose, and FAIL-OPEN against the argv-list
`subprocess.run` its own docstring offered as its mutation proof. One direction is noisy; the
other is silent, and the silent one is why this is a module rather than a fourth patch.

Every leg below names the defect it would catch. The reachability legs come FIRST, because
"the poison was not found" and "nothing was looked at" are the same green.
"""

from __future__ import annotations

import pytest

from tools.python_code_text import code_strings, code_text, imported_modules, searchable

# The argv form every subprocess call in this repository is written in, and the one that made the
# seat-executor control fail open: no shell spelling appears in it contiguously.
_ARGV_LIST = 'subprocess.run(["python3", "-m", "background.seat_executor", "--once"])'

# The comment that made the same control red at HEAD. Accurate, harmless, and indistinguishable
# from a call to any substring check.
_PROSE = '''"""The cgroup is user.slice/seat-executor.service, so setsid does not survive it."""
# background.seat_executor --once is what the timer runs
x = 1
'''


# ── reachability: the naive reading really does fail, both ways ──────────────────────────────

def test_the_defect_this_module_exists_for_is_present_in_the_samples():
    """POISON ROUND. If the samples did not carry the defect, every leg below would pass on a
    module that does nothing at all -- which is exactly how a control reads when it is vacuous."""
    assert "-m background.seat_executor" not in _ARGV_LIST, (
        "the argv sample no longer demonstrates the fail-open: a naive substring check finds it"
    )
    assert "background.seat_executor" in _PROSE, (
        "the prose sample no longer demonstrates the false positive: nothing to blank"
    )


# ── direction one: prose is not code ─────────────────────────────────────────────────────────

def test_a_docstring_naming_a_module_is_not_a_use_of_it():
    """MUTATION: stop blanking bare string expressions and this fires. The defect: an accurate
    docstring about a module is reported as the module being invoked."""
    assert "seat-executor.service" not in searchable(_PROSE)


def test_a_comment_naming_a_module_is_not_a_use_of_it():
    """MUTATION: drop `_comment_regions` and this fires. The defect that was live at HEAD."""
    assert "background.seat_executor --once" not in searchable(_PROSE)


def test_blanking_preserves_line_numbers_and_the_code_around_it():
    """MUTATION: delete the prose span instead of blanking it and this fires. A caller that
    reports `path:lineno` must keep reporting the line the token is really on."""
    out = searchable(_PROSE)
    assert out.splitlines()[2] == "x = 1", "the code line moved or was damaged"
    assert len(out.splitlines()[0]) == len(_PROSE.splitlines()[0]), "column offsets shifted"


def test_a_string_that_reaches_code_is_not_blanked():
    """THE NARROWING MUST NOT BE A HOLE. Only a BARE string expression is prose; a string handed
    to a call, an assignment or a collection is live. MUTATION: blank every Constant and this
    fires, taking every argv literal in the repo with it."""
    src = 'CMD = "background.seat_executor --once"\nrun(cmd="seat-executor.service")\n'
    out = searchable(src)
    assert "background.seat_executor --once" in out
    assert "seat-executor.service" in out


# ── direction two: an argv list is code, and the dangerous half ──────────────────────────────

def test_an_argv_list_is_read_the_way_a_shell_receives_it():
    """MUTATION: drop `_argv_joins` and this fires. THE FAIL-OPEN: the one control guarding this
    project's only unattended writer was blind to the shape its own prose called its proof."""
    out = searchable(_ARGV_LIST)
    assert "python3 -m background.seat_executor --once" in out


def test_the_list_keeps_its_own_spelling_too():
    """The join is APPENDED, not substituted. MUTATION: return only the joins and this fires --
    a control looking for the bare module name would stop finding it."""
    assert '"background.seat_executor"' in searchable(_ARGV_LIST)


def test_a_list_with_a_non_string_element_is_not_joined():
    """A join across a variable would invent a spelling nobody wrote. MUTATION: join partial
    lists and this fires with a command line that does not exist in the source."""
    assert "python3 -m" not in searchable('run(["python3", "-m", module, "--once"])')


# ── the list form: the same two directions, for a caller that searches string by string ──────

def test_the_list_form_carries_both_directions_the_blob_form_does():
    """`code_strings` is the shape `test_the_seat_executor_stands_down` reads the tree with, and it
    was a THIRD private copy of this rule until 2026-09-08. MUTATION: drop the `_argv_joins` call
    and the fail-open half returns; drop `prose_string_ids` and the false-positive half does."""
    import ast

    assert "python3 -m background.seat_executor --once" in code_strings(ast.parse(_ARGV_LIST)), (
        "the argv list is not being rejoined: a wall keyed to the shell spelling is fail-open"
    )
    assert not any("seat-executor.service" in s for s in code_strings(ast.parse(_PROSE))), (
        "prose reached the list: an accurate comment reads as an invocation"
    )


def test_the_list_form_is_not_the_blob_form_flattened():
    """WHY IT IS A SEPARATE FUNCTION AND NOT `searchable(...).split()`. Each item must be a string
    some running line could really produce, because the caller runs a REGEX over each one. MUTATION:
    implement it as `[searchable(src)]` and this fires -- a pattern would be free to straddle two
    adjacent constructs and match text no line ever emits, which on a wall is a false red."""
    import ast

    src = 'a = "start seat-executor"\nb = ".service and then some"\n'
    items = code_strings(ast.parse(src))
    assert "seat-executor.service" in "".join(items), (
        "POISON ROUND: the sample no longer demonstrates the straddle, so the leg below would pass "
        "on a flattening implementation too"
    )
    assert not any("seat-executor.service" in s for s in items)


def test_the_list_form_drops_a_bare_string_that_is_not_a_docstring():
    """The copy this replaced dropped only a body's FIRST statement. A bare `Expr(Constant(str))`
    anywhere is discarded by the interpreter and can invoke nothing, so it is prose too. MUTATION:
    narrow back to first-statement-only and this fires."""
    import ast

    src = 'x = 1\n"""background.seat_executor --once is what the timer runs"""\n'
    assert not any("background.seat_executor --once" in s for s in code_strings(ast.parse(src)))


# ── unparseable source fails closed ──────────────────────────────────────────────────────────

def test_source_that_will_not_parse_keeps_its_original_reading():
    """MUTATION: return "" (or the blanked text) on SyntaxError and every scanning control goes
    quiet on exactly the files it could not read. Not looking is never evidence of absence."""
    broken = 'def f(:\n    "background.seat_executor --once"\n'
    assert code_text(broken) is None
    assert searchable(broken) == broken


# ── the import half ──────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("spelling", [
    "from sim.scenario.spine import ScenarioSpine",
    "import sim.scenario.spine",
    "from sim.scenario import spine",
    "from sim.scenario import (spine)",
    "from sim.scenario import (\n    spine,\n)",
    "from sim.scenario import spine as sp",
    "import sim.scenario.spine as sp",
])
def test_every_spelling_of_an_import_is_the_same_import(spelling):
    """MUTATION: match imports by line spelling and the parenthesised and line-broken forms walk
    straight through. A wall keyed to how somebody typed an import is not keyed to the import."""
    assert "sim.scenario.spine" in imported_modules(spelling)


def test_a_deeper_import_is_visible_to_a_wall_keyed_to_the_package():
    """MUTATION: drop `_prefixes` and a wall on `sim.scenario` stops seeing `sim.scenario.spine`."""
    assert "sim.scenario" in imported_modules("import sim.scenario.spine.detail")


def test_prose_naming_a_module_is_not_an_import_of_it():
    """The other direction again, on the import half. MUTATION: fall back to a substring scan
    here and an accurate docstring becomes a wall breach."""
    assert imported_modules('"""Must never import sim.scenario.spine."""\n') == set()


def test_unparseable_source_reports_that_it_could_not_look():
    """MUTATION: return an empty set on SyntaxError and an unreadable file reads as a clean one --
    the caller can no longer tell "imports nothing" from "was not parsed"."""
    assert imported_modules("def f(:\n") is None
