"""THE SINK GUARD: a test may not write a production surface, whatever primitive it uses.

REUSE: tests/production_surface_guard.py
CLASS: CUSTOM
INDEX: searched "test isolation", "write guard", "production surface", "PYTEST_CURRENT_TEST".
       This does not replace `tests/conftest.py::_no_real_state_write` (G-T2) -- it IS that
       fixture's body, moved out so its coverage is a testable surface rather than a closure
       inside a fixture, and widened along the two axes proven below. The seven per-module
       `PYTEST_CURRENT_TEST` guards (`ntfy_utils`, `alarm_repetition`, `director_input_log`,
       `tmux_relay`, `live_ledger_guard`, `ntfy_mirror`, `process_run_complete`) stay: they are
       defence in depth at the caller, and this is the sink.

WHY THIS EXISTS
---------------
Director, 2026-08-21: *"the tests-writing-into-production-surfaces class ... that's three
instances I know of. Fix the class."*

It is more than three, and the count is the least interesting part. Every instance was found
IN THE ACT or afterwards, and after each one the repair was made one level down from where it
needed to be:

  * instance -> guard the CALL SITE  (seven modules now carry a `PYTEST_CURRENT_TEST` check)
  * instance -> guard the PATH       (`_PROTECTED_WRITE_PATHS`, eight individually-listed files)

The tuple's own comments say the right thing three times -- *"a guard list only protects the
paths somebody thought of"*, *"the caller was fixed, but a guard list is where the class dies"*,
*"the caller is not the fix, the tuple is"* -- and then the tuple is maintained exactly like the
call sites were: one entry per incident, added after the surface had already been written.

TWO HOLES, PROVEN BY PROBE ON 2026-08-21 RATHER THAN ARGUED
-----------------------------------------------------------
Run against the live guard, inside the real conftest:

  A. `Path.write_text` to a LISTED file            -> correctly BLOCKED.
  B. `open(same_listed_file, "a")`                 -> **ALLOWED**.
  C. `Path.write_text` to `docs/staging/x.md`      -> **ALLOWED**.

**B is the sharper one.** The old guard patched `pathlib.Path.{write_text,write_bytes,open}`
and nothing else, so even the eight paths somebody DID think of were protected against one of
the two ordinary ways to write a file. `background/background_worker.retire_superseded_marker`
writes with `with open(marker, "a")` -- that exact form, on a real production surface.

**C is the wider one.** `docs/staging/` is the director's work queue: what is in it is drawn
and acted on. It was not protected at all, which is why `alarm_repetition.escalate()` had to
grow its own bespoke guard on 2026-08-20 after a test run filed five real findings into it, one
quoting the fixture filename `SOME_DOC.md`.

WHAT CHANGED, AND THE ONE THING THAT DELIBERATELY DID NOT
---------------------------------------------------------
* **Primitive coverage is now closed**, not enumerated: `builtins.open`, `os.open`,
  `os.replace`, `os.rename`, `os.remove`/`unlink`, and `shutil.copy/copy2/copyfile/move` join
  the three `Path` methods. A write that reaches a protected path by any of them raises.
* **Path coverage becomes SURFACES rather than files** for the two surfaces where every file is
  production by definition: `docs/staging/` (the draw queue) and `docs/status/` (the published
  status). The individually-listed files stay listed, because they live under directories that
  are NOT wholly production.
* **`site/data/` stays file-scoped, on purpose.** The 2026-08-10 entry measured the blast radius
  and found that several generator tests legitimately rewrite `site/data/*.json`; protecting the
  directory would red them for nothing. That measurement still holds and is not re-litigated
  here -- `publish_provenance.json` remains the one file in there that is a public claim rather
  than a regenerable artefact.

ESCAPE HATCH, AND WHY IT IS NAMED RATHER THAN INFERRED
-------------------------------------------------------
`@pytest.mark.real_state_write` opts a test out, as before. A marker is greppable and shows up
in review; "the guard did not happen to cover this path" does not.
"""
from __future__ import annotations

import builtins
import os
import pathlib
import shutil

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Whole directories where EVERY file is a production surface. A new file appearing here is
#: covered without anyone remembering to list it -- which is the entire difference between this
#: and the tuple it grew out of.
PROTECTED_SURFACES = (
    "docs/staging",      # the director's draw queue: what lands here gets acted on
    "docs/status",       # the published status surface
)

#: Individual files under directories that are NOT wholly production. Each was added after a
#: test wrote it, and the incident is recorded beside it -- THIS tuple, not the one that used to
#: sit in `tests/conftest.py`, is what `install()` reads, so this is where a path has to be added
#: and where an R15 mutation has to be made for either to mean anything.
#:
#: G-T2 protects the high-danger RUNTIME CONTROL STATE -- files a live daemon READS to make a
#: control decision, where a test writing a fake value corrupts live behaviour.
PROTECTED_FILES = (
    "docs/observability/.build_executor_enabled",   # THE kill switch — a test must never set it
    "docs/observability/.pull_loop_health.json",    # deadman alarms on this (the proven leak)
    "docs/observability/.notify_transitions.json",  # notify() transition-dedup store
    "docs/observability/.daemon_boot",              # boot-SHA drift records (dir)
    # THE WEDGE ALARM'S ONLY NON-GUESSING EVIDENCE (2026-08-10, caught in the act, twelfth
    # publish wedge). `_write_blocking_tests` publishes "which test is blocking publishing"
    # here for the alarm, which runs in a different process and otherwise has only an exit code.
    # `tests/background/test_publish_gate_subject_is_head.py` drives the real `run_fast_tests`
    # against a sandbox repo, and its fixture redirected the three path constants its author
    # thought of -- so every run of it stamped this file with a SANDBOX commit SHA (observed:
    # `1c0414e9f...`, a bad object in this repo) and an empty node list. A fresh-but-empty record
    # does not read as absent: `last_blocking_tests` returns it, and the alarm reports "the gate
    # printed no FAILED line" and falls back to citing findings by mtime -- the 0/8-hit-rate guess
    # this file was built to replace.
    "docs/observability/.last_gate_blocking_tests.json",   # the wedge alarm's diagnostic payload
    # THE ONLY EVIDENCE THAT CAN CLOSE A WEDGE EPISODE (2026-08-13, OPS3, caught in the act).
    # `process_run_complete._green_is_on_record_for()` reads `.last_tested_hash` to answer the one
    # question rc=0 cannot -- did the SUITE pass for exactly this commit -- and that answer is what
    # lets `record_publish_gate_success()` zero `episode_failures`. `.publish_gate_state.json` is
    # the counter itself, and `supervisor._publish_gate_wedge_active` reads it as the TOP draw
    # rung. Both are runtime control state in G-T2's own sense, and neither was covered. The hole
    # was real, not theoretical: `run_fast_tests` and `_process()` write the live
    # `.last_tested_hash`, and the only thing standing between the gate suite and the live file
    # was ~10 per-test `monkeypatch.setattr` calls. Observed 2026-08-13 11:26Z: a publisher test's
    # fixture hash `abc1234` reached the LIVE sim-runner-log through the outcome router while a
    # real publish cycle was mid-flight.
    "docs/observability/.last_tested_hash",         # the suite-pass stamp the episode close rests on
    "docs/observability/.publish_gate_state.json",  # the wedge streak + the RUNG-1 draw's input
    # PUBLISHED SURFACE, not just internal state (2026-08-10, caught in the act). The publish
    # decoupling made `_process()` stamp this file, and the ordinary publisher tests that drive
    # `_process()` promptly wrote a run id of "abc1234" into the REAL file -- which the live
    # publisher then committed as a public freshness claim. It reached origin only because the
    # branch happened to be diverged. SCOPED TO THE FILE, NOT `site/data/` -- see the module
    # docstring: that blast radius was measured, and protecting the directory reds the generator
    # tests that legitimately rewrite `site/data/*.json` for nothing.
    "site/data/publish_provenance.json",            # the published freshness/provenance claim
)

_WRITE_MODES = ("w", "a", "x", "+")


def protected_targets(root: pathlib.Path | None = None) -> list[str]:
    """Resolved absolute paths this guard refuses writes to. Pure, so a test can assert the
    coverage set directly instead of inferring it from behaviour."""
    base = root or REPO_ROOT
    return [str((base / r).resolve()) for r in PROTECTED_SURFACES + PROTECTED_FILES]


def is_protected(target, targets: list[str]) -> bool:
    try:
        resolved = str(pathlib.Path(target).resolve())
    except (OSError, ValueError, TypeError):
        return False
    return any(resolved == t or resolved.startswith(t + os.sep) for t in targets)


class ProductionWriteRefused(RuntimeError):
    """Its own type so no `except RuntimeError` in a test can swallow it by accident."""


def _refuse(target) -> None:
    raise ProductionWriteRefused(
        f"TEST ISOLATION (G-T2): a test tried to write the production surface {target}.\n"
        "Isolate to tmp_path (monkeypatch the module's path constant), or -- if the test is "
        "genuinely exercising the real write -- mark it @pytest.mark.real_state_write."
    )


def install(monkeypatch, root: pathlib.Path | None = None) -> None:
    """Patch every write primitive that can reach a protected path.

    Enumerating primitives is itself the shape that failed here, so the list is deliberately
    wider than the ones known to have been used: the cost of covering a primitive nobody has
    misused yet is zero, and the cost of missing one is a production surface written by a test.
    """
    targets = protected_targets(root)

    real_write_text = pathlib.Path.write_text
    real_write_bytes = pathlib.Path.write_bytes
    real_path_open = pathlib.Path.open
    real_open = builtins.open
    real_os_open = os.open
    real_replace, real_rename = os.replace, os.rename
    real_remove, real_unlink = os.remove, os.unlink
    real_copy, real_copy2 = shutil.copy, shutil.copy2
    real_copyfile, real_move = shutil.copyfile, shutil.move

    def guarded_write_text(self, *a, **k):
        if is_protected(self, targets):
            _refuse(self)
        return real_write_text(self, *a, **k)

    def guarded_write_bytes(self, *a, **k):
        if is_protected(self, targets):
            _refuse(self)
        return real_write_bytes(self, *a, **k)

    def guarded_path_open(self, mode="r", *a, **k):
        if any(m in mode for m in _WRITE_MODES) and is_protected(self, targets):
            _refuse(self)
        return real_path_open(self, mode, *a, **k)

    def guarded_open(file, mode="r", *a, **k):
        # HOLE B, closed. This is the one that let a write reach an explicitly listed file.
        if isinstance(mode, str) and any(m in mode for m in _WRITE_MODES) \
                and is_protected(file, targets):
            _refuse(file)
        return real_open(file, mode, *a, **k)

    def guarded_os_open(path, flags, *a, **k):
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC) \
                and is_protected(path, targets):
            _refuse(path)
        return real_os_open(path, flags, *a, **k)

    def _guard_two_path(fn):
        def guarded(src, dst, *a, **k):
            if is_protected(dst, targets):
                _refuse(dst)
            return fn(src, dst, *a, **k)
        return guarded

    def _guard_one_path(fn):
        def guarded(path, *a, **k):
            # DELETION is a write. A test that unlinks a staged directive removes work the
            # director staged, and nothing about "write guard" should be read to exclude it.
            if is_protected(path, targets):
                _refuse(path)
            return fn(path, *a, **k)
        return guarded

    monkeypatch.setattr(pathlib.Path, "write_text", guarded_write_text)
    monkeypatch.setattr(pathlib.Path, "write_bytes", guarded_write_bytes)
    monkeypatch.setattr(pathlib.Path, "open", guarded_path_open)
    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(os, "open", guarded_os_open)
    monkeypatch.setattr(os, "replace", _guard_two_path(real_replace))
    monkeypatch.setattr(os, "rename", _guard_two_path(real_rename))
    monkeypatch.setattr(os, "remove", _guard_one_path(real_remove))
    monkeypatch.setattr(os, "unlink", _guard_one_path(real_unlink))
    monkeypatch.setattr(shutil, "copy", _guard_two_path(real_copy))
    monkeypatch.setattr(shutil, "copy2", _guard_two_path(real_copy2))
    monkeypatch.setattr(shutil, "copyfile", _guard_two_path(real_copyfile))
    monkeypatch.setattr(shutil, "move", _guard_two_path(real_move))
