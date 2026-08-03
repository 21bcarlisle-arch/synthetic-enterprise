"""R15 both-ways proof for tools/working_day_guard.py.

A guard that cannot fail is worse than no guard, so every test here is either
"plant the defect, assert it FIRES" or "remove it, assert it CLEARS". The
rename-proof rule (rule 2, structural) gets its own fire test, because a name-only
guard is the fail-open this control exists to avoid -- and that is not hypothetical:
the rule found two live `_add_wd` copies the design doc's name-based census missed.
"""

import ast
import textwrap

import pytest

from tools.working_day_guard import (
    BASELINE_ALLOWLIST,
    CANONICAL_MODULE,
    GuardError,
    PROJECT_DIR,
    _has_weekend_skip_shape,
    _iter_python_files,
    main,
    verify,
)


def _plant(tmp_path, monkeypatch, source: str, name: str = "planted.py"):
    """Write a module into a temp tree and point the guard's root at it."""
    target = tmp_path / name
    target.write_text(textwrap.dedent(source))
    monkeypatch.setattr("tools.working_day_guard.PROJECT_DIR", tmp_path)
    return target


NAMED_COPY = """
    import datetime as dt

    def _add_working_days(start, n):
        d = start
        while n > 0:
            d += dt.timedelta(days=1)
            if d.weekday() < 5:
                n -= 1
        return d
"""

RENAMED_COPY = """
    import datetime as dt

    def deadline_for(start, n):
        d = start
        while n > 0:
            d += dt.timedelta(days=1)
            if d.weekday() < 5:
                n -= 1
        return d
"""

INNOCENT = """
    import datetime as dt

    def tomorrow(d):
        return d + dt.timedelta(days=1)

    def weekday_name(d):
        return ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[d.weekday()]
"""


class TestFiresOnASecondDefinition:
    def test_named_copy_is_flagged(self, tmp_path, monkeypatch):
        target = _plant(tmp_path, monkeypatch, NAMED_COPY)
        violations = verify([target])
        assert len(violations) == 1
        assert "planted.py:4" in violations[0]
        assert "_add_working_days" in violations[0]

    def test_renamed_copy_is_STILL_flagged(self, tmp_path, monkeypatch):
        """Rule 2. A name-only guard passes this file -- which is precisely how the
        two live `_add_wd` definitions escaped the design doc's census."""
        target = _plant(tmp_path, monkeypatch, RENAMED_COPY)
        violations = verify([target])
        assert len(violations) == 1
        assert "deadline_for" in violations[0]
        assert "weekend-skip loop shape" in violations[0]

    def test_exit_code_is_1_when_violations_exist(self, tmp_path, monkeypatch, capsys):
        target = _plant(tmp_path, monkeypatch, NAMED_COPY)
        assert main(["--files", str(target)]) == 1
        assert "FAIL" in capsys.readouterr().out


class TestClearsWhenTheDefectIsRemoved:
    def test_innocent_module_passes(self, tmp_path, monkeypatch):
        """The both-ways half. This module uses BOTH timedelta and weekday(), just
        not as weekend-skipping loop arithmetic -- so it also proves the shape rule
        is not merely matching 'file mentions weekday'."""
        target = _plant(tmp_path, monkeypatch, INNOCENT)
        assert verify([target]) == []

    def test_exit_code_is_0_when_clean(self, tmp_path, monkeypatch, capsys):
        target = _plant(tmp_path, monkeypatch, INNOCENT)
        assert main(["--files", str(target)]) == 0
        assert "PASS" in capsys.readouterr().out

    def test_removing_the_planted_definition_clears_it(self, tmp_path, monkeypatch):
        target = _plant(tmp_path, monkeypatch, NAMED_COPY)
        assert verify([target])
        target.write_text(textwrap.dedent(INNOCENT))
        assert verify([target]) == []


class TestNotFailOpen:
    def test_empty_scan_is_an_error_not_a_pass(self):
        """A scan that checked nothing must never report PASS."""
        with pytest.raises(GuardError):
            verify([])

    def test_unparseable_file_raises_rather_than_passing(self, tmp_path, monkeypatch):
        target = _plant(tmp_path, monkeypatch, "def broken(:\n", name="broken.py")
        with pytest.raises(GuardError):
            verify([target])

    def test_canonical_module_is_the_only_exemption(self):
        """The exemption must be the one module, not a directory prefix that would
        silently cover anything added beside it."""
        assert CANONICAL_MODULE == "company/compliance/working_days.py"


class TestBaselineIsHonest:
    def test_live_tree_passes(self):
        """Pass 1 lands the guard with call sites unchanged -- so the tree is green
        by baseline, and any NEW definition fails the build immediately."""
        assert verify(list(_iter_python_files())) == []

    def test_baseline_allowlist_is_accurate(self):
        """The allowlist must SHRINK, never rot. Every entry must still name a real
        definition in the tree -- otherwise a migrated (deleted) caller would leave
        permanent cover behind for anything re-added under that same name."""
        live = set()
        for path in _iter_python_files():
            rel = path.relative_to(PROJECT_DIR).as_posix()
            if rel == CANONICAL_MODULE:
                continue
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    from tools.working_day_guard import FLAGGED_NAMES

                    if node.name in FLAGGED_NAMES or _has_weekend_skip_shape(node):
                        live.add(f"{rel}::{node.name}")
        stale = BASELINE_ALLOWLIST - live
        assert not stale, f"allowlist entries no longer in the tree (delete them): {sorted(stale)}"

    def test_canonical_module_is_not_in_the_baseline(self):
        """The primitive itself is exempt by rule, not by allowlist entry -- an
        allowlist entry would make the exemption invisible to the shrink test."""
        assert not any(e.startswith("company/compliance/working_days.py") for e in BASELINE_ALLOWLIST)
