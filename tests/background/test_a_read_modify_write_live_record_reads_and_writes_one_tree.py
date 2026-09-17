#!/usr/bin/env python3
"""A READ-MODIFY-WRITE OVER A LIVE RECORD MUST READ AND WRITE THE SAME TREE'S COPY.

THE CLASS, AND WHY IT NEEDED ITS OWN CONTROL. `live_ledger_guard.shared_tree_live_record` fixes
the READ side of the stale-checkout defect, and `e9ad946cd` wired the five readers proven
flattering. It deliberately left two alone, for one shared reason: both are read-modify-writes
over a TRACKED live record. `launch_liveness.record()` is `load()` then `save()`;
`seat_continuity.note_activity()` is `_read(p)` then replace. **Resolving the READ of either
without its WRITE does not stale a read -- it LOSES a write**, which is strictly worse: the
worktree reads the shared book, appends to it, and writes the result into its own copy, where
the next read never looks. The sibling file
`test_a_live_record_read_from_a_linked_worktree_reads_the_shared_tree.py` grades the read side;
this one grades the property that makes wiring a read SAFE.

THE PROPERTY IS "THE TWO SIDES AGREE", NOT "BOTH ARE REDIRECTED", and the difference is the
reason this file exists rather than five more wiring legs. The two subjects were originally
decided OPPOSITE ways on the evidence: `.launch_records.json` redirected to the shared tree,
because its subject is a `systemctl --user` unit and there is one user manager per machine;
`.seat_heartbeat.json` REFUSED, because two concurrent seats were measured beating in two trees
at once and merging them onto a SINGLE-VALUED record lets the survivor mask the dead one's
handoff. A control keyed to "both must redirect" would have been keyed to today's answer and
would have gone red on the day the heartbeat was correctly fixed with a per-seat keyed store.

THAT DAY WAS 2026-09-16, AND THE PREDICTION HELD -- which is the only reason this paragraph is
worth keeping. The keyed store landed, the refusal was withdrawn, and this file needed no change
of key: the agreement clause went red exactly where the shape changed and nowhere else. The
heartbeat leg has since GAINED the "redirect is taken" clause the launch leg always had, because
that clause is now true of both; the agreement clause underneath it is untouched.

NO MOCKS, AND THAT IS DELIBERATE. The fixture builds a real git main tree and a real linked
worktree, copies the REAL modules into it, and drives them from a real NON-TEST python process.
Nothing here substitutes a resolver or a guard for a stand-in. Two things follow that a mocked
version could not have: `guard_live_ledger_write` behaves as it does in production (a no-op
outside a test process) instead of having to be faked away, and `git rev-parse --git-common-dir`
is answered by git about a worktree git actually created.

PRE-REGISTERED before these were run. Unwiring EITHER side of `launch_liveness` fails the
launch-register leg and not the heartbeat one; adding a resolver to EITHER side of
`seat_continuity` alone fails the heartbeat leg and not the launch one; swapping the guard and
the redirect in `save()` fails only the ordering leg. A mutation that fires nothing means the leg
is a tautology; one that fires everything means the legs grade one thing while claiming three.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT))

from background.live_ledger_guard import LiveLedgerWriteUnderTest  # noqa: E402

#: The real modules the fixture trees DRIVE -- the three whose behaviour this file grades.
#: `background/` is a namespace package here as it is in the repository, so no `__init__.py` is
#: copied or created -- a fixture that differs from its subject in how it is IMPORTED is a
#: fixture that can disagree with it for free.
_ROOTS = ("live_ledger_guard.py", "launch_liveness.py", "seat_continuity.py")


def _background_imports(name: str) -> set[str]:
    """The MODULE-LEVEL `background.*` imports of `background/<name>`, read by AST.

    THIS LIST WAS HAND-KEPT AND WENT RED TWICE ON IT (2026-09-17 is the second). `launch_liveness`
    gained `from background.episode_prior import ...` at module level in `5f6a4f15f`; the tuple
    above was not updated, and from then on this control reported `ModuleNotFoundError: No module
    named 'background.episode_prior'` -- an ImportError raised in the FIXTURE, standing in for a
    verdict about its subject, which never ran at all. A stand-in repo whose contents are kept by
    hand fails on the next import anyone adds, and it fails as a red that looks like the subject's.

    DERIVED FROM THE SUBJECT, so there is nothing left to keep. The roots above are a real fact
    about this file (they are what the child processes below actually call); everything else the
    subject needs in order to IMPORT is closed over from the subject's own source.

    MODULE-LEVEL ONLY, deliberately. That is precisely the failure this closes: the child
    ImportErrors before a line of the subject runs. A lazy in-function import -- `seat_continuity`
    has four -- fails inside the code path that reached it, on the assertion that reached it, in
    its own words; it is a different and self-announcing shape, and pulling the whole lazy graph
    in would copy half of `background/` into every fixture tree to close a hole nobody has.

    Raises rather than degrades. A root that cannot be parsed, or an import naming a module that
    is not on disk, is a fact about the tree the reader needs -- silently copying fewer files is
    how this got here.
    """
    out: set[str] = set()
    tree = ast.parse((PROJECT / "background" / name).read_text(encoding="utf-8"), filename=name)
    for node in tree.body:  # module level only -- see the docstring
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            if node.module == "background":  # `from background import x, y`
                out.update(alias.name + ".py" for alias in node.names)
            else:
                parts = node.module.split(".")
                if parts[0] == "background" and len(parts) > 1:
                    out.add(parts[1] + ".py")
        elif isinstance(node, ast.Import):  # `import background.x`
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == "background" and len(parts) > 1:
                    out.add(parts[1] + ".py")
    return out


def _module_closure(roots: tuple[str, ...]) -> tuple[str, ...]:
    """`roots` plus everything they need at import time, transitively."""
    seen: set[str] = set()
    queue = list(roots)
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        if not (PROJECT / "background" / name).exists():
            raise AssertionError(
                "the fixture's subject imports background/{} at module level and no such module "
                "exists -- this tree cannot import its own daemon".format(name))
        seen.add(name)
        queue.extend(_background_imports(name))
    return tuple(sorted(seen))


#: Everything a fixture tree needs on disk for the roots to IMPORT. Derived, never listed.
_MODULES = _module_closure(_ROOTS)


def _git(*args, cwd):
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), capture_output=True, text=True, check=True)


def _run_outside_pytest(code: str, *, cwd: Path) -> dict:
    """Run `code` in a REAL non-test interpreter rooted at `cwd`, and return what it printed.

    `PYTEST_CURRENT_TEST` is stripped from the environment, and `PYTHONPATH` names ONLY the
    fixture tree. Both matter. Inheriting the variable would make `in_test_process()` true in the
    child and `guard_live_ledger_write` would refuse the very write this grades -- the control
    would then be measuring the guard rather than the redirect. Inheriting the repository root
    would let `import background.launch_liveness` resolve to the module under test instead of the
    fixture's copy of it, so the child would resolve paths against the REAL tree.
    """
    import os

    env = {k: v for k, v in os.environ.items() if k != "PYTEST_CURRENT_TEST"}
    env["PYTHONPATH"] = str(cwd)
    out = subprocess.run([sys.executable, "-c", code], cwd=str(cwd), env=env,
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, f"the fixture process failed:\n{out.stdout}\n{out.stderr}"
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.fixture
def trees(tmp_path):
    """`(main, linked)` -- a real shared tree and a real linked worktree whose checkout of both
    live records is deliberately stale, which is the shape git actually produces."""
    now = time.time()
    main = tmp_path / "main"
    (main / "background").mkdir(parents=True)
    obs = main / "docs" / "observability"
    obs.mkdir(parents=True)

    for name in _MODULES:
        (main / "background" / name).write_text(
            (PROJECT / "background" / name).read_text(encoding="utf-8"), encoding="utf-8")

    # WHAT GETS COMMITTED is what every linked worktree checks out and keeps for ever.
    (obs / ".launch_records.json").write_text(json.dumps(
        [{"job": "stale-checkout-only", "unit": "s.service", "artefact": "", "log": None,
          "rc_path": None, "launched_at": "2026-09-01T00:00:00Z", "asserted_live_by": [],
          "claim": "live", "settled_at": None, "evidence": None}]))
    (obs / ".seat_heartbeat.json").write_text(json.dumps(
        {"ts": now, "pid": 1, "session_id": "sess-STALE", "tool_count": 1,
         "recent_tools": [{"tool": "StaleCheckoutTool", "at": now}]}))

    _git("init", "-q", "-b", "main", cwd=main)
    _git("add", "-A", cwd=main)
    _git("commit", "-qm", "the checkout a worktree keeps", cwd=main)

    linked = tmp_path / "linked"
    _git("worktree", "add", "-q", "--detach", str(linked), cwd=main)

    # ...and the SHARED tree's copies move on, as the daemons move them.
    (obs / ".launch_records.json").write_text(json.dumps([
        {"job": "shared-only-A", "unit": "a.service", "artefact": "", "log": None,
         "rc_path": None, "launched_at": "2026-09-10T00:00:00Z", "asserted_live_by": [],
         "claim": "finished", "settled_at": "2026-09-10T01:00:00Z", "evidence": None},
        {"job": "shared-only-B", "unit": "b.service", "artefact": "", "log": None,
         "rc_path": None, "launched_at": "2026-09-10T02:00:00Z", "asserted_live_by": [],
         "claim": "finished", "settled_at": "2026-09-10T03:00:00Z", "evidence": None}]))
    (obs / ".seat_heartbeat.json").write_text(json.dumps(
        {"ts": now, "pid": 2, "session_id": "sess-LIVE", "tool_count": 99,
         "recent_tools": [{"tool": "LiveTreeTool", "at": now}]}))

    stale = json.loads((linked / "docs" / "observability" / ".launch_records.json").read_text())
    assert [r["job"] for r in stale] == ["stale-checkout-only"], \
        "the fixture is not reproducing the defect: the worktree should still hold the checkout"
    return main, linked


def test_the_fixture_tree_holds_whatever_its_subject_imports_rather_than_a_hand_kept_list():
    """A STAND-IN REPO KEPT BY HAND FAILS ON THE NEXT IMPORT ANYONE ADDS, and it fails as a red
    that reads like the subject's (2026-09-17: `ModuleNotFoundError: No module named
    'background.episode_prior'`, from a fixture whose subject never ran).

    KEYED TO THE PROPERTY -- the copied set is CLOSED under its members' module-level imports --
    and not to today's answer. Asserting "episode_prior is in the list" would go red on the day
    that import is correctly removed, which is exactly backwards.
    """
    assert set(_ROOTS) <= set(_MODULES)
    for name in _MODULES:
        missing = _background_imports(name) - set(_MODULES)
        assert not missing, (
            "background/{} imports {} at module level and the fixture tree would not contain "
            "it, so the child ImportErrors before the subject runs".format(name, sorted(missing)))


def test_a_subject_importing_a_module_that_is_not_there_is_loud():
    """Silently copying fewer files is how the hand-kept list got away with being wrong. The
    fail-loud leg has to be reachable or the closure is just a quieter version of the defect."""
    with pytest.raises(AssertionError, match="cannot import its own daemon"):
        _module_closure(("no_such_daemon.py",))


def _book(tree: Path) -> list:
    return [r["job"] for r in json.loads(
        (tree / "docs" / "observability" / ".launch_records.json").read_text())]


def test_a_launch_recorded_from_a_linked_worktree_joins_the_one_book_the_machine_keeps(trees):
    """THE DELIVERY, in its own terms, and it asserts the redirect is TAKEN before asserting
    that the two sides agree -- a module that redirected NOTHING round-trips local-to-local
    perfectly and would satisfy the agreement clause on its own.

    Measured on the real trees on 2026-09-16: the worktree's checkout held 4 records of which 2
    still claimed `live`, against a shared book of 12 in which both had been `finished` for six
    days. A launch recorded from a delivery turn landed in the 4 and was read by nothing."""
    main, linked = trees

    seen = _run_outside_pytest(
        "import json\n"
        "from background import launch_liveness as ll\n"
        "ll.record('probe-job', 'probe.service', '/nonexistent')\n"
        "print(json.dumps([r['job'] for r in ll.load()]))\n",
        cwd=linked)

    assert _book(main) == ["shared-only-A", "shared-only-B", "probe-job"], (
        "the launch was not recorded into the shared tree's book -- a job launched from a "
        "delivery turn is invisible to the deadman and to every reader of the register, which is "
        f"the invisibility launch_liveness exists to abolish. Shared book: {_book(main)}")
    assert _book(linked) == ["stale-checkout-only"], (
        "the worktree's own checkout was written -- a second book describing one machine's "
        "systemd units, which is two answers to a question that has one")
    assert seen == ["shared-only-A", "shared-only-B", "probe-job"], (
        "the read and the write of this read-modify-write disagreed: the register read back "
        f"{seen}. One side of the pair is resolved and the other is not, which loses the write "
        "rather than staling the read")


def _beats(tree: Path) -> dict:
    """`{session_id: [tool, ...]}` from a tree's own copy of the heartbeat store.

    BOTH SHAPES, RE-DERIVED HERE rather than borrowed from `seat_continuity._adopt_legacy`. The
    committed file is still the PRE-KEYED flat record -- that is what the fixture commits because
    it is what HEAD holds, and what every linked worktree therefore checks out -- so this helper
    has to read it. Calling the module's own adopter would mean a defect in that adopter could
    not make any assertion below fail, which is the fake-more-permissive-than-its-subject shape.
    """
    store = json.loads((tree / "docs" / "observability" / ".seat_heartbeat.json").read_text())
    seats = (store["seats"] if isinstance(store.get("seats"), dict)
             else {store.get("session_id", ""): store})
    return {k: [t["tool"] for t in (v.get("recent_tools") or [])] for k, v in seats.items()}


def test_a_seat_beating_in_a_linked_worktree_joins_the_one_book_the_machine_keeps(trees):
    """THE REFUSAL, WITHDRAWN ON THE MEASUREMENT THAT REPLACED IT -- and this is the leg that
    caught the repair landing, so read what it does and does not claim.

    The file-level docstring's prediction held: keyed to "the two sides agree" rather than "both
    are redirected", this leg stayed honest across a reversal of the answer. It went RED the
    moment `_read` returned the keyed store while the probe still asked for a flat record, and
    the agreement clause below is unchanged.

    WHAT IS NEW IS THE "REDIRECT IS TAKEN" CLAUSE, which this leg could not carry while the
    heartbeat was refused and the launch leg has carried all along: a module that redirects
    NOTHING round-trips local-to-local perfectly and satisfies the agreement clause on its own.
    Now that a seat is a thing on this MACHINE -- one row per session, so two live seats are two
    rows and a survivor cannot keep a dead seat's row warm -- the beat must reach the SHARED
    book, and the worktree's stale checkout must be left exactly where git put it.

    THE THIRD CLAUSE IS THE ONE THE KEYED STORE EXISTS FOR. `sess-LIVE` is already beating in
    the shared tree. A seat arriving from a linked worktree must join it, not replace it: on the
    single-valued record the newcomer's write WAS the book, and that is the fail-silent (the
    survivor's answer) that made this redirect refusable until the store was keyed."""
    main, linked = trees

    seen = _run_outside_pytest(
        "import json\n"
        "from background import seat_continuity as sc\n"
        "sc.note_activity('ProbeTool', session_id='sess-FROM-WORKTREE')\n"
        "print(json.dumps(sc._seats(sc._read()).get('sess-FROM-WORKTREE', {})"
        ".get('recent_tools') or []))\n",
        cwd=linked)

    assert [t["tool"] for t in seen] == ["ProbeTool"], (
        "the seat heartbeat did not read back the beat it had just written: one side of this "
        f"read-modify-write resolves to a different tree than the other. Read back: {seen}")
    assert _beats(main) == {"sess-LIVE": ["LiveTreeTool"], "sess-FROM-WORKTREE": ["ProbeTool"]}, (
        "the beat did not join the machine's one book beside the seat already in it: a seat "
        "that dies in a linked worktree is then swept by nobody, which is the gap this repair "
        f"closes. Shared book: {_beats(main)}")
    assert _beats(linked) == {"sess-STALE": ["StaleCheckoutTool"]}, (
        "the worktree's own checkout was written -- a second book describing one machine's "
        "seats, which is two answers to a question that has one")


def test_the_heartbeats_write_guard_is_asked_before_the_redirect_moves_the_path(trees,
                                                                                monkeypatch):
    """THE SAME ORDERING HOLE AS `save()`, on the writer that runs on EVERY tool call.

    `guard_live_ledger_write` refuses on `is_live_record_path`, whose room is derived from THIS
    tree's `LIVE_RECORD_DIR`. A path already redirected to the shared tree is outside it, so a
    `note_activity` that resolved first and guarded second would let a test process stamp the
    real machine's heartbeat -- the guard still called, still passing, and permanently
    unreachable for exactly the callers the redirect applies to.

    Swapping the two lines in `note_activity` makes this leg, and only this leg, fail."""
    import background.live_ledger_guard as g
    import background.seat_continuity as sc
    main, linked = trees

    monkeypatch.setattr(g, "PROJECT_DIR", linked)
    monkeypatch.setattr(g, "LIVE_RECORD_DIR", linked / "docs" / "observability")
    monkeypatch.setattr(sc, "HEARTBEAT_FILE",
                        linked / "docs" / "observability" / ".seat_heartbeat.json")

    with pytest.raises(LiveLedgerWriteUnderTest):
        sc.note_activity("AFixtureTool", session_id="a-test-process")

    assert _beats(main) == {"sess-LIVE": ["LiveTreeTool"]}, (
        "a test process stamped the shared tree's heartbeat: the write guard was asked about a "
        "path the redirect had already moved out of the room it refuses on")


def test_the_registers_write_guard_is_asked_before_the_redirect_moves_the_path(trees,
                                                                               monkeypatch):
    """THE ORDERING, which is a hole the redirect itself opens (R15).

    `guard_live_ledger_write` refuses on `is_live_record_path`, and that room is derived from
    THIS tree's `LIVE_RECORD_DIR`. A path already redirected to the shared tree is OUTSIDE it, so
    a `save()` that resolved first and guarded second would hand a test process the real launch
    register and report nothing -- the guard still called, still passing, and permanently
    unreachable for exactly the callers the redirect applies to.

    Swapping the two lines in `save()` makes this leg, and only this leg, fail."""
    import background.launch_liveness as ll
    import background.live_ledger_guard as g
    main, linked = trees

    monkeypatch.setattr(g, "PROJECT_DIR", linked)
    monkeypatch.setattr(g, "LIVE_RECORD_DIR", linked / "docs" / "observability")
    monkeypatch.setattr(ll, "RECORDS_PATH",
                        linked / "docs" / "observability" / ".launch_records.json")

    with pytest.raises(LiveLedgerWriteUnderTest):
        ll.save([{"job": "a test process's fixture book"}])

    assert _book(main) == ["shared-only-A", "shared-only-B"], (
        "a test process wrote the shared tree's launch register: the write guard was asked about "
        "a path the redirect had already moved out of the room it refuses on")
