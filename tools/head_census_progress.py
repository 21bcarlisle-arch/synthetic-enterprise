"""The HEAD-green census's progress stream: one line per test, flushed as it finishes.

Loaded only by `tools/head_green_census.pytest_argv` (`-p tools.head_census_progress`); both hooks
are inert unless their env var is set, so nothing else that imports this sees any change.

WHY (2026-11-16). From 2026-11-04 to 2026-11-16 no census completed: five nights the suite was
killed at its 17400s bound, and the partial stdout was discarded because a FAILED-line list with
no record of what was reached would be read as complete. So the HEAD-red register could not move
for twelve days, however many of its tests were fixed. A line per test survives the kill and names
what the run DID reach; `head_red_register.record(reached=...)` clears only those.
"""
from __future__ import annotations

import os

PROGRESS_ENV = "HEAD_CENSUS_PROGRESS"
#: Module paths (newline-separated) to run FIRST, so the register's own subjects are re-observed
#: every night even when the bound cuts the tail. Pytest 9 merges an explicit file into an
#: enclosing directory argument and runs it in tree order (measured: `tests/tools/
#: test_capability_index.py tests/tools/` runs it at position 902 of 8744), so argv order cannot.
FIRST_ENV = "HEAD_CENSUS_FIRST"
#: The real `open`, bound when pytest loads this plugin and before any test runs. The call-phase
#: report fires BEFORE the test's teardown, so a test that monkeypatches `builtins.open` (the
#: reconciler's fail-closed test does) is still patched when this hook writes. Calling the patched
#: name raised inside a hook, which is an INTERNALERROR that ends the session: the 20 Nov census,
#: admitted at last, stopped at test 6033 of the suite for exactly this reason.
_OPEN = open
#: THE CRASH LINE (2026-11-26). A red's first traceback line, `<path>:<line>: <message>`, kept on
#: its register record. Without it a pollution bisect had to re-run a test only to learn WHICH
#: assertion fired: H40 (7 Oct) could not tell an empty drawn book (`assert drawn`) from a broken
#: identity (`not_shared`) without a 58-minute batch. A display length, not a domain value.
CRASH_CHARS = 200


def crash_line(report) -> str:
    """The report's first crash line, one line, tab-free, at most `CRASH_CHARS`; "" if none."""
    longrepr = getattr(report, "longrepr", None)
    crash = getattr(longrepr, "reprcrash", None)
    if crash is not None:
        # Relative to the run's root: the census runs in a throwaway checkout whose absolute
        # path would spend most of the budget and name nothing a reader can open.
        where = str(crash.path)
        root = os.getcwd() + os.sep
        if where.startswith(root):
            where = where[len(root):]
        text = "{}:{}: {}".format(where, crash.lineno, crash.message)
    else:
        text = str(longrepr or "")
    lines = text.strip().splitlines()
    return lines[0].replace("\t", " ")[:CRASH_CHARS] if lines else ""


def pytest_collection_modifyitems(session, config, items):
    first = {m for m in os.environ.get(FIRST_ENV, "").split("\n") if m}
    if first:
        # A stable sort on a 0/1 key keeps each module's own order and keeps modules contiguous,
        # so module- and class-scoped fixtures see the grouping they always did.
        items.sort(key=lambda it: 0 if it.nodeid.split("::", 1)[0] in first else 1)


def pytest_runtest_logreport(report):
    path = os.environ.get(PROGRESS_ENV)
    if not path:
        return
    if report.when == "call" or report.outcome != "passed":
        with _OPEN(path, "a") as fh:
            row = "{}\t{}\t{}".format(report.when, report.outcome, report.nodeid)
            if report.outcome == "failed":
                row += "\t" + crash_line(report)
            fh.write(row + "\n")
