"""THE CLASS CONTROL for "a new deadman-cycle check leaks live disk into the no-page proofs".

THE SAME CLASS AS `test_rest_ladder_isolation.py`, ONE MODULE ALONG, and it has now cost the
operational-layer signal three separate multi-check RED episodes. `deadmans_switch.run_cycle()` is
a fixed sequence of zero-argument `_check_*()` calls, and each one reads some REAL file, remote or
working tree in this checkout. Roughly thirty tests in `test_deadmans_switch.py` set up a hermetic
world (recent commit, empty staging) and assert `calls == []` -- nothing paged. A check whose live
input happens to be non-empty puts a message in every one of those lists at once.

THREE INSTANCES, EACH PATCHED ALONE:
  1. `_flush_notification_digest`   (2026-08-14) -- 27 tests red, signal RED for 9 hourly checks
  2. `_check_origin_fork`           (2026-09-02) -- 28 tests red, and again an hour later when the
                                     rung grew a second world-read the pin did not cover
  3. `_check_launch_artefacts_landed` (2026-09-10) -- 28 tests red, signal RED for 8 hourly checks,
                                     and this time the red was CONCEALED: these tests run before
                                     `test_supervisor.py` in file order, so the suite failed early
                                     and the (then-unbudgeted) run never reported what it found

R10 forbids closing an absurdity-class defect with a fourth instance fix. This is the class fix:
the check set is DERIVED from the shipped source of `run_cycle`, so a check added tomorrow is
enumerated on the day it lands, and if it leaks THIS test names it -- instead of twenty-eight
unrelated assertions failing with a digest blob and no clue which check spoke.

WHY IT IS NOT A TAUTOLOGY (R15). The check set is parsed from the real function's source, not
declared here (proved by `test_check_enumeration_is_derived_not_declared`, which adds and removes
calls in a synthetic source and watches the answer move). The silence check calls the real shipped
functions through the real autouse fixtures (proved to FIRE by
`test_the_control_fires_when_a_real_check_leaks`, which reinstates the 2026-09-10 defect on the
shipped check and watches this control catch it).

WHAT IT DELIBERATELY DOES NOT DO. It does not assert the checks are silent in the WORLD -- the
unlanded artefact of 2026-09-10 was real, the drift alarm was correct, and the director should
have been told. It asserts only that a pytest process in this directory cannot be made to see it.

THE MARKER IS SPLIT, ON PURPOSE. The three tests that touch the shipped checks carry
`operational`: a lost pin is a test-ISOLATION defect, and wedging the live-site publish on one is
the 2026-07-16 overnight-wedge class the marker exists to refuse. The three pure-source tests
below carry no marker and therefore stay BLOCKING -- they touch no live state, cannot flake, and a
broken enumeration is the one failure here that makes every other assertion in this file vacuous.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

import background.deadmans_switch as dms
from background import launch_liveness

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _the_operational_signal_must_not_recurse(monkeypatch):
    """`_check_operational_layer_signal` is one of the enumerated checks, and calling it for real
    from inside `pytest -m operational` SPAWNS `pytest -m operational`.

    It self-throttles on the live `.operational_layer_signal.json`, so it is a no-op for most of
    every hour and this file passed in 0.10s the first time it ran -- which is precisely the
    "weather as its subject" shape this whole file exists to refuse. An hour later it would fork a
    twenty-minute suite run inside a suite run. `test_deadmans_switch.py::_isolate` carries the
    same stub for the same reason; this is not a new judgement.

    THE CONTROL CANNOT GRADE THIS CHECK EITHER WAY, and that is stated here rather than hidden by
    quietly dropping it from the enumeration: the signal pages through `process_run_complete`'s own
    notify route, not through `deadmans_switch.notify`, so it is invisible to `leaking_checks` with
    or without this stub. It keeps its place in the count so the vacuity guard stays honest, and
    its real coverage lives in test_operational_layer_signal.py.
    """
    monkeypatch.setattr(
        "background.process_run_complete.run_operational_layer_signal",
        lambda **k: {"ran": False, "reason": "isolated"},
    )


# --------------------------------------------------------------------------- #
# PURE helpers (mutation-testable without touching disk)
# --------------------------------------------------------------------------- #

def cycle_checks(source: str) -> list[str]:
    """Zero-argument calls made as bare STATEMENTS in the given function source.

    That shape IS the definition of a cycle check: `run_cycle` opens with an unconditional
    sequence of them and each may page. Deliberately EXCLUDES calls that take arguments
    (`_check_open_mint_escalation(since_commit)` and its sibling are guarded by a clock this
    control has no business synthesising, and they have their own tests), calls inside an `if`
    (same reason), and anything whose result is used, since a value that is read is not a page.
    """
    tree = ast.parse(inspect.cleandoc(source) if source.startswith(" ") else source)
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    body = functions[0].body if functions else tree.body
    found: list[str] = []
    for node in body:
        if not isinstance(node, ast.Expr):
            continue
        call = node.value
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)):
            continue
        if call.args or call.keywords:
            continue
        if call.func.id not in found:
            found.append(call.func.id)
    return found


def leaking_checks(namespace, names, monkeypatch) -> dict[str, str]:
    """Checks that reach `notify` when called in the current process state -> {name: what it said}.

    A check that pages under a hermetic fixture is reading live disk. A check that is absent or
    RAISES is not reported: every one of them is written to swallow its own exception (an error
    means "we did not look"), so a broken check cannot invent a page, and a crash is a different
    defect with its own tests.
    """
    leaks: dict[str, str] = {}
    for name in names:
        fn = getattr(namespace, name, None)
        if not callable(fn):
            continue
        said: list[str] = []
        with monkeypatch.context() as m:
            m.setattr(namespace, "notify", lambda msg, **kw: said.append(msg))
            try:
                fn()
            except Exception:
                continue
        if said:
            leaks[name] = " | ".join(said)[:400]
    return leaks


# --------------------------------------------------------------------------- #
# R15: the enumeration is DERIVED from the shipped source, not declared here
# --------------------------------------------------------------------------- #

_SYNTHETIC = """
def run_cycle():
    _reping()
    _check_alpha()
    _check_beta(since_commit)
    verdict = _check_gamma()
    if flag:
        _check_delta()
    _flush()
"""


def test_check_enumeration_is_derived_not_declared():
    """MUTATE THE SOURCE, watch the answer move -- proves nothing is hard-coded."""
    assert cycle_checks(_SYNTHETIC) == ["_reping", "_check_alpha", "_flush"]

    added = _SYNTHETIC.replace("    _flush()", "    _check_epsilon()\n    _flush()")
    assert cycle_checks(added) == ["_reping", "_check_alpha", "_check_epsilon", "_flush"], (
        "a check ADDED to the cycle was not enumerated -- this control would go blind to exactly "
        "the change it exists to catch"
    )

    removed = _SYNTHETIC.replace("    _check_alpha()\n", "")
    assert cycle_checks(removed) == ["_reping", "_flush"]


def test_argument_taking_and_conditional_calls_are_not_enumerated():
    """The three exclusions, asserted rather than described. Each would make this control demand
    silence from something it cannot legitimately set up, and red the honest cycle."""
    names = cycle_checks(_SYNTHETIC)
    assert "_check_beta" not in names, "a clock-guarded escalation was enumerated"
    assert "_check_gamma" not in names, "a call whose value is READ is not a page"
    assert "_check_delta" not in names, "a conditional call was enumerated"


def test_leak_detector_separates_paging_from_silent(monkeypatch):
    class _Ns:
        notify = staticmethod(lambda msg, **kw: None)
        _loud = staticmethod(lambda: _Ns.notify("[LAUNCH UNLANDED] 1 file(s) in no commit"))
        _quiet = staticmethod(lambda: None)
        _explodes = staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    leaks = leaking_checks(_Ns, ["_loud", "_quiet", "_explodes", "_absent"], monkeypatch)
    assert list(leaks) == ["_loud"]
    assert "LAUNCH UNLANDED" in leaks["_loud"]


# --------------------------------------------------------------------------- #
# THE CONTROL ITSELF -- run against the shipped cycle under this directory's fixtures
# --------------------------------------------------------------------------- #

def _real_cycle_checks() -> list[str]:
    checks = cycle_checks(inspect.getsource(dms.run_cycle))
    # VACUITY GUARD (R15): a parse that silently returned [] would make the control below pass
    # unconditionally -- the fail-silent pattern. The cycle has opened with ten or more such calls
    # since 2026-08 and only ever grows.
    assert len(checks) >= 10, (
        f"only {len(checks)} cycle check(s) parsed out of run_cycle: {checks}. Either the cycle "
        "was rewritten into a different statement shape (update `cycle_checks` to match it) or "
        "this control is now vacuous. Do not delete this guard to make it pass."
    )
    return checks


@pytest.mark.operational
def test_every_cycle_check_is_silent_under_this_directorys_fixtures(monkeypatch):
    """THE CLASS CONTROL. Call each shipped check individually with `notify` captured, under
    nothing but this directory's autouse conftest fixtures -- exactly the world the ~30 `assert
    calls == []` tests in test_deadmans_switch.py run in.

    FAILS BY NAME on the check that leaks, instead of leaving twenty-eight tests to fail with a
    digest blob (which is what cost the 2026-09-10 episode its eight hourly checks)."""
    leaks = leaking_checks(dms, _real_cycle_checks(), monkeypatch)
    assert not leaks, (
        "DEADMAN-CYCLE ISOLATION LEAK -- {} check(s) in `run_cycle` read LIVE state that this "
        "directory's fixtures do not neutralise, so every 'nothing paged' assertion in "
        "test_deadmans_switch.py is now a function of what other lanes have left in this working "
        "tree:\n{}\n\n"
        "This is the fourth-plus instance of one class. The fix is NOT to stub the check in one "
        "test file: pin its live INPUT to an absent tmp path in tests/background/conftest.py's "
        "autouse fixture, beside the digest / origin-fork / launch-register pins already there, "
        "so the whole directory is isolated by default and the check's own tests (which set their "
        "state in the test body, after the fixture) still exercise it for real. Note that pinning "
        "the DIGEST QUEUE is not enough on its own: the queue is append-only and a check firing "
        "inside the cycle refills it before the same cycle flushes it."
        .format(len(leaks), "\n".join(f"  {k} -> {v}" for k, v in leaks.items()))
    )


@pytest.mark.operational
def test_the_control_fires_when_a_real_check_leaks(monkeypatch):
    """R15 BOTH WAYS: reinstate the 2026-09-10 defect on the SHIPPED cycle -- the launch register
    naming an artefact git has never seen -- and prove this control catches it. Uses the real
    check name and the real enumeration, so it also proves the enumeration REACHES the shipped
    functions rather than a set of names that resolve to nothing."""
    checks = _real_cycle_checks()
    assert "_check_launch_artefacts_landed" in checks, (
        "the check that held the operational signal red for eight hourly checks is no longer "
        "enumerated -- if it was deliberately removed from the cycle, re-point this mutation at "
        "another live-disk check"
    )
    monkeypatch.setattr(
        launch_liveness, "landed_check",
        lambda *a, **k: (1, ["a-lane [artefact]: UNTRACKED -- git has never seen it"]),
    )

    leaks = leaking_checks(dms, checks, monkeypatch)
    assert "_check_launch_artefacts_landed" in leaks, (
        "the control cannot see a leaking check -- it is theatre")
    assert "UNTRACKED" in leaks["_check_launch_artefacts_landed"]


@pytest.mark.operational
def test_the_launch_register_is_pinned_away_from_the_live_checkout():
    """THE INSTANCE, asserted rather than assumed: the ELEVENTH conftest pin must actually be in
    force. Both directions are checked so it cannot rot into a no-op -- with `RECORDS_PATH` absent
    the check is silent here; the assertion that it CAN speak is the mutation above.

    The second leg is the one that matters: the pin also stops `check()` WRITING. It settles live
    claims and saves them, so before this pin every run_cycle test in this directory rewrote the
    real `.launch_records.json`."""
    with pytest.raises(ValueError):
        # relative_to raises == the pinned path is OUTSIDE the checkout.
        Path(launch_liveness.RECORDS_PATH).relative_to(REPO_ROOT)
    assert not launch_liveness.RECORDS_PATH.exists()
    assert launch_liveness.load() == []
    assert launch_liveness.landed_check() == (0, [])


@pytest.mark.operational
def test_the_worktree_scan_is_pinned_and_the_reaper_therefore_cannot_reach_the_real_repo():
    """THE TWELFTH conftest pin, and the only one in this directory found by a control rather than
    by a red: the class test above named `_check_worktree_reconcile` on its first run.

    THE PIN IS ON `_git`, NOT ON THE SCANS, and this test asserts the CONSEQUENCE at both scans
    rather than the pin's own name -- because the pin's first draft replaced the two scan functions
    and broke the four tests in test_fork_reconciler.py whose subject IS the scan. Keyed to the
    property, so the honest repair (a third scan, a different seam) still satisfies it.

    THE SECOND LEG IS A SAFETY LEG, not an isolation one. `run_cycle` calls `_check_worktree_reap`,
    whose own docstring says never to run it in enforce mode against the real repo's worktrees --
    and the enforce flag is armed on this machine. With the scan empty there is nothing for it to
    remove by CONSTRUCTION, rather than nothing only because the live/locked/dirty refusal set kept
    saying no.
    """
    from background import fork_reconciler

    assert fork_reconciler.scan_worktrees() == [], (
        "tests/background/conftest.py no longer pins fork_reconciler.scan_worktrees -- every test "
        "here that drives run_cycle is reading this machine's real worktree set, and the reaper "
        "is running against it in enforce mode"
    )
    assert fork_reconciler.scan_fork_branches() == [], (
        "the second seam is unpinned -- the fork-lifecycle check is reading real branches"
    )
    assert fork_reconciler.evaluate_worktree_reconcile()["alarm"] is False
    assert fork_reconciler.evaluate_worktree_reap()["kept"] == []


@pytest.mark.operational
def test_the_register_and_the_publish_clock_are_pinned_and_neither_pin_is_absent_shaped():
    """THE THIRTEENTH AND FOURTEENTH pins, and the pair that proves "pin it at an absent path" is
    a habit rather than a rule.

    Neither was visible in the working tree. Both were named by the class control above when the
    pre-commit gate ran it in a clean HEAD extract: HEAD's committed action-needed register holds
    an open `publish_gate_wedged` item, and a `git archive` extract has no publish clock at all --
    which is the LOUDEST branch `_check_content_publishing` has, not its quietest.

    So the two pins point in opposite directions and the test asserts that difference directly.
    The register is ABSENT (absent reads as empty, which is silence). The publish clock is SEEDED
    (absent reads as "no verified publish has EVER been recorded", which pages every run). A future
    reader normalising the second one onto the first would reinstate the defect, and this fails.
    """
    from background import action_needed, publish_freshness

    with pytest.raises(ValueError):
        Path(action_needed.REGISTER_PATH).relative_to(REPO_ROOT)
    assert not action_needed.REGISTER_PATH.exists(), (
        "the action-needed register pin must be ABSENT -- an empty register is what silence is"
    )
    assert action_needed.load_register() == {}

    with pytest.raises(ValueError):
        Path(publish_freshness.STATE_FILE).relative_to(REPO_ROOT)
    assert publish_freshness.STATE_FILE.exists(), (
        "the publish clock pin must be SEEDED, not absent -- an absent clock is `unpublished`, "
        "which is the alarm this pin exists to stop, fired on every run in every extract"
    )
    assert publish_freshness.last_published_ts() is not None
    assert publish_freshness.snapshot().get("state") in ("publishing", "unknown"), (
        "the seeded clock must read healthy-or-unmeasurable; anything else pages"
    )


def test_this_directorys_fixtures_put_no_FILE_at_the_root_of_tmp_path(tmp_path):
    """The seeded pin above is the only autouse fixture here that WRITES rather than redirects,
    and its first version wrote into `tmp_path` itself. That red-ed EIGHT tests at HEAD.

    `test_staging_watcher.py` points `watcher.STAGING_DIR` at its own `tmp_path`, so a file seeded
    at that root lands inside eight "the staging directory is empty" assertions and every one of
    them notifies about it. The conftest already states this rule three fixtures higher, about
    directories -- *a fixture that materialises things inside another test's `tmp_path` is changing
    the world it is supposed to be isolating* -- and a FILE is the worse case, because the
    watcher's `current_files` skips directories by construction and cannot skip this.

    So the property, asserted directly and cheaply: after every autouse fixture in this directory
    has run, the root of a fresh `tmp_path` holds no FILES. Subdirectories are fine and several
    fixtures legitimately create them. This is not marked `operational` -- it touches no live
    state, cannot flake, and a violation is a real defect that should block.
    """
    files = [p.name for p in tmp_path.iterdir() if p.is_file()]
    assert files == [], (
        "an autouse fixture in tests/background/conftest.py seeded {} at the ROOT of tmp_path. "
        "Any test in this directory that treats its own tmp_path as a scanned directory (the "
        "staging watcher points STAGING_DIR at exactly that) now sees a file it did not put "
        "there. Put it in a subdirectory of tmp_path instead.".format(files)
    )
