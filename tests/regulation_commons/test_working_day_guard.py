"""R15 mutation tests for the second-definition guard.

The guard is the CLASS mechanism (R10): migrating 24 callers fixes today, the
guard is what stops the 25th. So the guard itself has to be proven capable of
failing, on its own named defect, both ways -- plant a second definition and it
must RED; remove it and it must go GREEN. A guard that has never been seen to
fire is not evidence of anything.

Every mutation is planted in a TEMPORARY tree. The real repository is never
written to by these tests.

The three killer patterns are each covered explicitly:

* TAUTOLOGY  -- ``TestTheGuardIsNotATautology``
* FAIL-OPEN  -- ``TestTheGuardFailsClosed`` (unparseable / unreadable / empty scan)
* FAIL-SILENT -- ``TestTheGuardCannotPassQuietly`` (zero files scanned is a FAIL,
  and the CLI carries its own exit code)
"""

from __future__ import annotations

import textwrap

import pytest

from regulation_commons import working_day_guard as guard
from regulation_commons.working_day_guard import find_violations

# --- planted defects -------------------------------------------------------

NAMED_HELPER = textwrap.dedent(
    """
    import datetime as dt

    def _add_working_days(start: dt.date, n: int) -> dt.date:
        current, added = start, 0
        while added < n:
            current += dt.timedelta(days=1)
            if current.weekday() < 5:
                added += 1
        return current
    """
)

#: The dangerous one: a reimplementation under a name nobody would grep for.
#: A name-only guard passes this happily.
NOVEL_NAME_SAME_SHAPE = textwrap.dedent(
    """
    import datetime as dt

    def _shift_by_business_period(anchor, count):
        cursor, seen = anchor, 0
        while seen < count:
            cursor = cursor + dt.timedelta(days=1)
            if cursor.weekday() < 5:
                seen += 1
        return cursor
    """
)

#: The gsop_tracker shape -- ordinal stepping instead of timedelta.
ORDINAL_STEP_SHAPE = textwrap.dedent(
    """
    import datetime as dt

    def days_the_thing_has_been_open(start, end):
        count, current = 0, start
        while current < end:
            if current.weekday() < 5:
                count += 1
            current = dt.date.fromordinal(current.toordinal() + 1)
        return count
    """
)

CLEAN_MODULE = textwrap.dedent(
    """
    import datetime as dt

    from regulation_commons.working_days import add_working_days

    DEADLINE_WORKING_DAYS = 5

    def deadline(start: dt.date) -> dt.date:
        return add_working_days(start, DEADLINE_WORKING_DAYS)
    """
)

#: Innocent code that touches both ingredients separately. If the guard flags
#: this it is over-broad and will be switched off by the first person it
#: annoys, which is its own kind of failure.
INNOCENT_MODULE = textwrap.dedent(
    """
    import datetime as dt

    def describe(day: dt.date) -> str:
        label = "weekend" if day.weekday() >= 5 else "weekday"
        return f"{label} before {day + dt.timedelta(days=1)}"

    def each_day(start: dt.date, n: int):
        return [start + dt.timedelta(days=i) for i in range(n)]
    """
)


@pytest.fixture()
def tree(tmp_path):
    """A miniature scannable tree: <tmp>/company/<file>.py"""

    def _write(**modules: str):
        package = tmp_path / "company"
        package.mkdir(exist_ok=True)
        (package / "__init__.py").write_text("")
        for name, body in modules.items():
            (package / f"{name}.py").write_text(body)
        return tmp_path

    return _write


def _violations(root):
    return find_violations(root=root, trees=("company",))


# ---------------------------------------------------------------------------
# The guard on the real tree
# ---------------------------------------------------------------------------


def test_the_live_tree_has_exactly_one_working_day_definition():
    """The migration's actual acceptance test."""
    violations = find_violations()
    assert violations == [], "\n".join(v.render() for v in violations)


def test_the_guard_actually_scanned_the_live_tree():
    """A green guard that inspected nothing proves nothing (fail-silent)."""
    scanned = list(guard.iter_python_files(guard.REPO_ROOT, guard.SCANNED_TREES))
    assert len(scanned) > 100, f"guard only saw {len(scanned)} files"
    trees_hit = {rel.split("/")[0] for _path, rel in scanned}
    assert trees_hit == set(guard.SCANNED_TREES), f"guard missed trees: {trees_hit}"


def test_the_canonical_module_is_not_flagged_by_its_own_guard():
    """regulation_commons is exempt -- it is where the one definition lives."""
    assert guard._is_sanctioned("regulation_commons/working_days.py")
    assert not guard._is_sanctioned("company/billing/credit_refund.py")


# ---------------------------------------------------------------------------
# R15: the mutation, both ways
# ---------------------------------------------------------------------------


class TestTheGuardFiresOnItsOwnNamedDefect:
    def test_planting_a_named_helper_reds_the_guard(self, tree):
        root = tree(offender=NAMED_HELPER)
        violations = _violations(root)
        assert len(violations) == 1
        assert violations[0].name == "_add_working_days"
        assert violations[0].path == "company/offender.py"
        assert violations[0].lineno > 0

    def test_removing_the_planted_helper_greens_the_guard(self, tree):
        root = tree(offender=NAMED_HELPER)
        assert _violations(root), "precondition: the guard must be RED first"
        (root / "company" / "offender.py").write_text(CLEAN_MODULE)
        assert _violations(root) == [], "guard stayed red after the defect was removed"

    def test_a_reimplementation_under_a_novel_name_is_still_caught(self, tree):
        """The fail-open a name-only guard would have. This function's name
        appears in no census, no grep and no API -- only its SHAPE gives it
        away."""
        root = tree(offender=NOVEL_NAME_SAME_SHAPE)
        violations = _violations(root)
        assert len(violations) == 1
        assert violations[0].name == "_shift_by_business_period"
        assert "under another name" in violations[0].reason

    def test_the_ordinal_stepping_variant_is_caught(self, tree):
        root = tree(offender=ORDINAL_STEP_SHAPE)
        assert len(_violations(root)) == 1

    def test_a_clean_module_is_not_flagged(self, tree):
        assert _violations(tree(good=CLEAN_MODULE)) == []

    def test_innocent_date_handling_is_not_flagged(self, tree):
        """No false positives: a guard that cries wolf gets disabled."""
        assert _violations(tree(innocent=INNOCENT_MODULE)) == []

    def test_multiple_offenders_are_all_reported(self, tree):
        root = tree(a=NAMED_HELPER, b=NOVEL_NAME_SAME_SHAPE, c=CLEAN_MODULE)
        violations = _violations(root)
        assert len(violations) == 2
        assert {v.path for v in violations} == {"company/a.py", "company/b.py"}


# ---------------------------------------------------------------------------
# R15: FAIL-OPEN
# ---------------------------------------------------------------------------


class TestTheGuardFailsClosed:
    def test_an_unparseable_file_is_a_violation_not_a_skip(self, tree):
        """An unchecked module is a FAILED check. Skipping it would let anyone
        hide a second definition behind a syntax error."""
        root = tree(broken="def oops(:\n    pass\n")
        violations = _violations(root)
        assert len(violations) == 1
        assert violations[0].name == "<unparseable>"
        assert "FAILED" in violations[0].reason

    def test_an_undecodable_file_is_a_violation_not_a_skip(self, tree):
        root = tree(placeholder=CLEAN_MODULE)
        (root / "company" / "binary.py").write_bytes(b"\xff\xfe\x00 def _add_working_days")
        violations = _violations(root)
        assert any(v.name == "<unreadable>" for v in violations), violations

    def test_a_scan_that_saw_no_files_is_a_violation(self, tmp_path):
        """The purest fail-open: point the guard at nothing and it must not
        report success."""
        violations = find_violations(root=tmp_path, trees=("company",))
        assert len(violations) == 1
        assert violations[0].name == "<no-files-scanned>"

    def test_an_empty_file_does_not_crash_or_pass_vacuously(self, tree):
        root = tree(empty="", good=CLEAN_MODULE)
        assert _violations(root) == []


# ---------------------------------------------------------------------------
# R15: FAIL-SILENT
# ---------------------------------------------------------------------------


class TestTheGuardCannotPassQuietly:
    def test_the_cli_exits_nonzero_when_the_live_tree_is_dirty(self, tree, monkeypatch, capsys):
        root = tree(offender=NAMED_HELPER)
        monkeypatch.setattr(guard, "REPO_ROOT", root)
        monkeypatch.setattr(guard, "SCANNED_TREES", ("company",))
        assert guard.main() == 1
        out = capsys.readouterr().out
        assert "FAIL" in out and "company/offender.py" in out

    def test_the_cli_exits_zero_when_clean(self, tree, monkeypatch, capsys):
        root = tree(good=CLEAN_MODULE)
        monkeypatch.setattr(guard, "REPO_ROOT", root)
        monkeypatch.setattr(guard, "SCANNED_TREES", ("company",))
        assert guard.main() == 0
        assert "PASS" in capsys.readouterr().out

    def test_the_cli_exits_nonzero_when_it_can_see_nothing(self, tmp_path, monkeypatch):
        """If the guard is misconfigured or its trees vanish, that is a FAIL,
        not a quiet success."""
        monkeypatch.setattr(guard, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(guard, "SCANNED_TREES", ("company",))
        assert guard.main() == 1


# ---------------------------------------------------------------------------
# R15: TAUTOLOGY
# ---------------------------------------------------------------------------


class TestTheGuardIsNotATautology:
    def test_the_shape_detector_owes_nothing_to_the_canonical_api(self):
        """`_shift_by_business_period` matches no name the canonical module
        exports, yet is caught. The expectation therefore cannot have been
        derived from the thing being checked."""
        from regulation_commons import working_days

        exported = {name for name in dir(working_days) if not name.startswith("_")}
        assert "_shift_by_business_period" not in exported
        assert not (guard.BANNED_NAMES <= exported), (
            "the banned-name list must not be a subset of the canonical module's "
            "exports -- it is the independent census, not a mirror of the API"
        )

    def test_the_guard_flags_the_defect_even_with_the_canonical_import_present(self, tree):
        """Importing the right module does not buy absolution: what matters is
        whether a second definition exists, not whether the file also does the
        right thing somewhere else."""
        root = tree(sneaky=CLEAN_MODULE + NOVEL_NAME_SAME_SHAPE)
        assert len(_violations(root)) == 1

    def test_the_banned_name_list_covers_the_original_census(self):
        """The names the 24 migrated modules actually used, so a straight
        revert of the migration would be caught."""
        for name in ("_add_working_days", "_working_days_between", "working_days_open"):
            assert name in guard.BANNED_NAMES


# ---------------------------------------------------------------------------
# The allowlist must not become a hole
# ---------------------------------------------------------------------------


class TestTheAllowlistIsNotAnEscapeHatch:
    def test_every_allowlist_entry_carries_a_reason(self):
        for key, reason in guard.ALLOWLIST.items():
            assert isinstance(reason, str) and len(reason) > 30, f"{key} has no real reason"

    def test_allowlisted_functions_still_exist_where_claimed(self):
        """A stale allowlist entry is a hole waiting for a name collision."""
        for (rel, func), _reason in guard.ALLOWLIST.items():
            path = guard.REPO_ROOT / rel
            assert path.exists(), f"allowlist points at missing file {rel}"
            assert f"def {func}(" in path.read_text(), f"{rel} no longer defines {func}"

    def test_an_allowlisted_name_is_still_caught_if_it_does_the_arithmetic(self, tree, monkeypatch):
        """The allowlist suppresses the NAME check only. Putting the loop back
        inside an exempt accessor must still RED the guard -- otherwise the
        allowlist would be a way to reintroduce the whole defect class."""
        offender = textwrap.dedent(
            """
            import datetime as dt

            def working_days_open(start, end):
                count, current = 0, start
                while current < end:
                    if current.weekday() < 5:
                        count += 1
                    current += dt.timedelta(days=1)
                return count
            """
        )
        root = tree(exempted=offender)
        monkeypatch.setitem(
            guard.ALLOWLIST,
            ("company/exempted.py", "working_days_open"),
            "test fixture: exempt by name, must still be caught by shape",
        )
        violations = _violations(root)
        assert len(violations) == 1
        assert "under another name" in violations[0].reason
