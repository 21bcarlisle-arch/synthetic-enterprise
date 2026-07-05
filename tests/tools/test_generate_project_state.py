"""Tests for tools/generate_project_state.py::_parse_phase_and_tests.

Regression test (Phase QG): the function used to pick the phase entry with
the HIGHEST test count, but the fast-suite total is not monotonic across
phases (it fluctuates with which slow/simulation tests are ignored at write
time) -- so a later phase with a smaller reported count silently regressed
PROJECT_STATE.txt's "Current Phase" label back to an older, higher-count
phase. New phases are always prepended at the top of CLAUDE.md's "## Current
state" section, so the first COMPLETE line is always the current one."""
from tools.generate_project_state import _parse_phase_and_tests


def test_picks_most_recent_phase_even_when_test_count_is_lower(tmp_path, monkeypatch):
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(
        "## Current state\n"
        "**Phase QF COMPLETE (2026-07-04):** something. 15,342 total.\n"
        "**Phase QE COMPLETE (2026-07-04):** something else. 15,393 total.\n"
    )
    monkeypatch.setattr("tools.generate_project_state.CLAUDE_MD", claude_md)
    phase, tests = _parse_phase_and_tests()
    assert phase == "QF"
    assert tests == 15342


def test_picks_most_recent_phase_when_phrased_as_collected_not_total(tmp_path, monkeypatch):
    """Phase QP regression: entries since QL phrase the count as "N collected"
    (not "(N total)"), which the strict total-only regex missed entirely --
    silently falling through to an older "total"-phrased entry further down
    and regressing the reported phase/test count."""
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(
        "## Current state\n"
        "**Phase QP COMPLETE (2026-07-05):** something. 17 new tests, 15,595 collected.\n"
        "**Phase QF COMPLETE (2026-07-04):** something else. 15,342 total.\n"
    )
    monkeypatch.setattr("tools.generate_project_state.CLAUDE_MD", claude_md)
    phase, tests = _parse_phase_and_tests()
    assert phase == "QP"
    assert tests == 15595


def test_returns_unknown_when_no_current_state_section(tmp_path, monkeypatch):
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("no current-state section here")
    monkeypatch.setattr("tools.generate_project_state.CLAUDE_MD", claude_md)
    phase, tests = _parse_phase_and_tests()
    assert phase == "?"
    assert tests == 0


def test_returns_unknown_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.generate_project_state.CLAUDE_MD", tmp_path / "nonexistent.md")
    phase, tests = _parse_phase_and_tests()
    assert phase == "?"
    assert tests == 0
