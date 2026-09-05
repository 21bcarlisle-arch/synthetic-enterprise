"""PROJECT_STATE.txt is a startup anchor, and this is what it may never publish.

REWRITTEN 2026-09-05. The previous version of this file is why the defect lasted eight days:

    def test_returns_unknown_when_no_current_state_section(...):
        assert phase == "?"
        assert tests == 0

It PINNED THE FAIL-SILENT AS CORRECT. When the 2026-08-28 CLAUDE.md rewrite removed the
`## Current state` heading, that test stayed green -- it was asserting the very branch that had
just started firing -- and the published mirror served `Current Phase: ?` and `Test Suite: 0 tests
passing` until the director's console reported it on 2026-09-05.

That is a control keyed to today's answer rather than to the property, which CLAUDE.md names as
this project's recurring shape: it goes red when the code becomes more honest and stays green when
the claim rots. The property is that a startup anchor never renders a missing measurement as a
number. These tests are keyed to that.

The phase-selection logic these tests used to cover moved with the parser itself; it is covered
against the real CLAUDE.md by `tests/tools/test_website_integrity_fix.py`.
"""
from __future__ import annotations

from tools import generate_project_state as gps


def test_the_published_anchor_never_renders_a_missing_test_count_as_a_number(monkeypatch):
    """THE DEFECT, exactly as it published. `0 tests passing` is not a wrong figure a reader can
    argue with -- it is a missing figure wearing a measurement's formatting, and against a project
    whose real count is 26,731 it reads as a total collapse of the build."""
    monkeypatch.setattr(gps, "_parse_phase_and_tests", lambda: (None, None))
    written = {}
    monkeypatch.setattr(gps, "OUT_PATH", _Spy(written, "site"))
    monkeypatch.setattr(gps, "DOCS_STATUS_PATH", _Spy(written, "docs"))

    gps.generate()

    for text in written.values():
        assert "Test Suite: 0 tests" not in text
        assert "Current Phase: ?" not in text
        assert "not stated in CLAUDE.md" in text


def test_an_available_count_is_still_rendered_as_a_number(monkeypatch):
    """THE OTHER BRANCH, without which the test above is satisfied by a generator that has stopped
    reporting the figure at all -- a refusal that always refuses passes every test of refusing."""
    monkeypatch.setattr(gps, "_parse_phase_and_tests", lambda: ("ZZ", 26731))
    written = {}
    monkeypatch.setattr(gps, "OUT_PATH", _Spy(written, "site"))
    monkeypatch.setattr(gps, "DOCS_STATUS_PATH", _Spy(written, "docs"))

    gps.generate()

    for text in written.values():
        assert "Test Suite: 26,731 tests passing" in text
        assert "Current Phase: ZZ" in text
        assert "not stated in CLAUDE.md" not in text


def test_there_is_exactly_one_claude_md_build_parser_and_it_works_on_the_real_file():
    """THE CLASS, not the instance. Two implementations of one rule, repaired in one and still
    live in the other, is what made an eight-day null possible -- and CLAUDE.md names that shape
    (the VAT rule: one requirement, five implementations, fixed in one in July and still broken in
    another in August) as the defect the delivery seat exists to catch.

    The duplicate is deleted rather than guarded, so this asserts the delegation is real AND that
    it answers on the live CLAUDE.md. `is` on the function object is what makes a reintroduced
    second parser fail here rather than quietly agreeing until it drifts.
    """
    from tools.generate_dashboard_data import _derive_build_from_claude_md

    _, tests = gps._parse_phase_and_tests()
    _, twin_tests = _derive_build_from_claude_md()

    assert tests is not None, (
        "the live CLAUDE.md build stamp is unparseable -- this is the eight-day defect recurring, "
        "and PROJECT_STATE.txt is publishing 'not stated in CLAUDE.md' to the startup surface"
    )
    assert tests == twin_tests
    assert tests > 20_000, f"implausible full-suite count {tests}: parsed a scoped figure"


def test_the_parser_answers_when_the_module_is_run_AS_A_SCRIPT():
    """THE DEFECT THIS SHIPPED WITH FOR ONE INVOCATION, and the one every other test here missed.

    `python3 tools/generate_project_state.py` runs the file as a SCRIPT, so the repo root is not
    on `sys.path`, the delegated `from tools.generate_dashboard_data import ...` raises
    ModuleNotFoundError, and the fallback published "not stated in CLAUDE.md" over a figure that
    was right there in the file -- replacing an eight-day `0` with an eight-day `unavailable`.

    SECOND OCCURRENCE IN TWO DAYS: `tools/next_step_gate.py` shipped dead the same way (its hook
    runs it as a script) and carries the same guard and the same control. Both times every other
    test was green, because pytest has already fixed `sys.path` -- so an import-path defect is
    structurally invisible to any test that imports the module, which is all of them. Only running
    it the way its caller runs it can fail for this reason.
    """
    import os
    import subprocess
    import sys as _sys

    from tools.generate_project_state import PROJECT

    # `sys.path[0] = "tools"` is what makes this faithful and is the whole point. A plain
    # `python3 -c` leaves the CWD on sys.path, so `tools.generate_dashboard_data` imports whether
    # or not the guard exists -- the first version of this test did exactly that and survived
    # mutation of the guard it claims to prove. A real script run puts the SCRIPT'S DIRECTORY
    # there instead of the CWD, which is the entire difference.
    #
    # `run_name` deliberately not "__main__": this must exercise the import path without letting
    # generate() overwrite the real published PROJECT_STATE.txt in a tree other lanes are using.
    done = subprocess.run(
        [_sys.executable, "-c",
         "import sys; sys.path[0] = 'tools';"
         "import runpy;"
         "m = runpy.run_path('tools/generate_project_state.py', run_name='probe');"
         "print(m['_parse_phase_and_tests']()[1])"],
        cwd=str(PROJECT), capture_output=True, text=True, timeout=180,
        env={**os.environ, "PYTHONPATH": ""},
    )

    assert done.returncode == 0, done.stderr
    count = done.stdout.strip()
    assert count != "None", (
        "the parser answered None when run as a script -- it cannot import its own dependency, "
        f"and PROJECT_STATE.txt publishes 'not stated in CLAUDE.md'. stderr: {done.stderr!r}"
    )
    assert int(count) > 20_000, f"implausible full-suite count {count}"


class _Spy:
    """A Path stand-in that captures what the generator writes, so these tests never touch the
    real published files (another lane publishes them concurrently)."""

    def __init__(self, sink, key):
        self._sink, self._key = sink, key
        self.parent = self

    def mkdir(self, **_kw):
        return None

    def write_text(self, text, *a, **kw):
        self._sink[self._key] = text

    def __str__(self):
        return f"<spy {self._key}>"
