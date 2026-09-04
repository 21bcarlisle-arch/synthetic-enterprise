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
    "docs/staging",        # the director's draw queue: what lands here gets acted on
    "docs/observability",  # the evidence base — see below
    "docs/status",         # the published status surface
)

# WHY `docs/observability` BECAME A SURFACE ON 2026-08-31, and it is this module's own argument
# turned on its own tuple. Until this landed the directory was protected FILE BY FILE -- nine
# hand-listed entries below, every one a dotfile of runtime control state, every one added after a
# test had already written it. The narrative ledgers, the `*.md` files that ARE the record of what
# the machine did, were not protected at all.
#
# MEASURED: `docs/observability/autonomous-runner-log.md` was 27,675 lines and **6,421 of them
# (23%) were written by pytest** -- launches whose pid is a `MagicMock` repr, refusals naming a
# pytest fixture directory as the binary. The module that owns it had not RUN since 2026-07-08.
#
# THE COST WAS NOT A PUBLISHED FIGURE. The delivery seat read that ledger to answer a direct
# question about why autonomous turns were not firing, found 17 "Usage limit active" lines dated
# that day, and reported a usage limit to the director. There was no limit, no runner and no turn;
# there were seventeen unit tests. **A production surface a test can write is not evidence.**
#
# BLAST RADIUS MEASURED OVER THE WHOLE SUITE, not a subset -- the previous attempt measured 102
# tests, repaired them, then found more, twice. The honest figure is **84 refusals**, and they
# concentrate on FOUR writers rather than 84 tests: `book_growth_campaign.json` (40),
# `agent_status.json` (32), `token-log.md` (6), `supervisor-log.md` (4) and
# `.sanctified_consoles.json` (2). Repairing four writers is a different job from repairing 84
# tests, and only measuring the whole suite showed that.
#
# The nine observability dotfiles that used to be listed individually are SUBSUMED by the surface.

#: Individual files under directories that are NOT wholly production. Each was added after a
#: test wrote it, and the incident is recorded beside it -- THIS tuple, not the one that used to
#: sit in `tests/conftest.py`, is what `install()` reads, so this is where a path has to be added
#: and where an R15 mutation has to be made for either to mean anything.
#:
#: G-T2 protects the high-danger RUNTIME CONTROL STATE -- files a live daemon READS to make a
#: control decision, where a test writing a fake value corrupts live behaviour.
PROTECTED_FILES = (
    # ── The nine `docs/observability/...` entries that used to be listed here are SUBSUMED by the
    # `docs/observability` surface above (2026-08-31). Their incidents stay recorded because they
    # are the evidence FOR the surface: `.build_executor_enabled` (the kill switch),
    # `.pull_loop_health.json` (the proven leak), `.notify_transitions.json`, `.daemon_boot`,
    # `.last_gate_blocking_tests.json`, `.last_tested_hash`, `.publish_gate_state.json`.
    #
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
    # PUBLISHED SURFACE, not just internal state (2026-08-10, caught in the act). The publish
    # decoupling made `_process()` stamp this file, and the ordinary publisher tests that drive
    # `_process()` promptly wrote a run id of "abc1234" into the REAL file -- which the live
    # publisher then committed as a public freshness claim. It reached origin only because the
    # branch happened to be diverged. SCOPED TO THE FILE, NOT `site/data/` -- see the module
    # docstring: that blast radius was measured, and protecting the directory reds the generator
    # tests that legitimately rewrite `site/data/*.json` for nothing.
    "site/data/publish_provenance.json",            # the published freshness/provenance claim
    # A MIRROR OF A HUMAN DECISION QUEUE, NOT A GENERATOR OUTPUT (2026-09-04, caught in the act).
    # The `site/data/` file-scoping above is sound for REGENERABLE artefacts: a generator test that
    # rewrites one costs nothing, because the next generator run overwrites it anyway. This file is
    # not that. It is the mirror of `docs/observability/action_needed_register.json` — the items
    # RESERVED FOR THE DIRECTOR, the four classes nothing here may decide — and the only thing that
    # can restore it is the register write that produced it.
    #
    # MEASURED BEFORE ADDING, because the 2026-08-10 blast radius is the reason `site/data/` is
    # file-scoped and it deserved checking rather than quoting: this path has exactly ONE writer,
    # `background/action_needed._mirror_reserved_to_site`. `tools/generate_director_data.py` names
    # `director_reserved.json` in `FEED_FILES`, but `load_feeds` only READS it and that generator's
    # single `out_path.write_text` writes `DELTA_NAME`. The generator argument does not reach this
    # path, so protecting it costs nothing it was raised to protect.
    #
    # WHY THE SINK IS NEEDED WHEN THE CALLER WAS JUST FIXED. 33b54b3ee repaired the mirror's own
    # guard, which had compared two values a test controls and so mirrored a FIXTURE alarm into the
    # real feed, EVICTING the director's live one-way-door escalation (the mirror replaces the item
    # list) while the publish daemon stood ready to commit `site/`. That fix is at the caller, and
    # this module's whole argument is that the caller is never where this class dies. This is the
    # sink for the same defect.
    "site/data/director_reserved.json",             # the director's reserved queue, mirrored
    # A TEST WRITE HERE IS INDISTINGUISHABLE FROM THE DAEMON'S (2026-09-04, caught in the act,
    # and the reason it stayed uncaught for nine days is the whole argument for listing it).
    # `tests/background/test_process_run_complete.py` drove the real publish path in five tests,
    # so the generator wrote this file for real. What it wrote was not corrupt and not obviously
    # a fixture: it was EXACTLY what the live publish daemon writes on every cycle, because it is
    # the same generator reading the same tree. There is no `abc1234`, no epoch-0 stamp, nothing
    # in the content that says a test made it.
    #
    # That is what defeats the `site/data/` file-scoping reasoning here. That scoping is sound and
    # rests on a real property — a rewritten REGENERABLE artefact costs nothing because the next
    # generator run overwrites it anyway. But this path is not covered by the `site/data/*.json`
    # commit glob, so it is NOT rewritten by the publisher on its way past: the committed copy is
    # a hand-landed record, and the only thing standing between a test's write and a committed
    # change to published data is whether a seat happens to look at a dirty tracked file.
    #
    # MEASURED BEFORE ADDING, to the same standard the entry above set. Six test files name this
    # feed: five READ it (`INTENSITY_FEED`/`FEED` constants) or assert on generator SOURCE, and
    # `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` calls `generate()` with its own
    # `out_path`. Exactly one wrote the real path, and it is now redirected at the fixture. So
    # this protects a surface no legitimate test writes, which is what the 2026-08-10 blast-radius
    # measurement asks of any addition here.
    #
    # WHY THE SINK WHEN THE CALLER WAS JUST FIXED: the fixture redirect is a registry, and a
    # registry only covers the generators somebody enumerated. This module's whole argument is
    # that the caller is never where this class dies.
    "docs/market_data/grid_intensity_feed.json",    # published, and outside the publisher's glob
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
