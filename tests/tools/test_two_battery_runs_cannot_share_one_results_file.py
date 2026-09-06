"""Two runs of the SAME battery spec must not share one results file.

THE DEFECT THIS NAMES (delivery seat, 2026-09-06). `fingerprint` closed the two-SPEC collision on
the same day: two different specs for one subject can no longer default to one `/var/tmp` path,
and a results file stamped by another spec is refused. It is structurally blind to the other half.
The same spec run from two working trees hashes identically, defaults to the identical global
path, and there was no lock of any kind. `tools/contract_battery.py` reads that file once at the
top of the run and writes it whole from memory at thirteen sites, so the two runs adopt each
other's cells and the last writer publishes a verdict neither of them produced -- the exact class
this instrument exists to find, committed by the instrument, for the second time in one day.

Found by near-miss rather than by damage: a re-run was already in flight from the shared tree and
the seat was one command from starting a second one.

WHAT MAKES THIS ABLE TO FAIL. A refusal that refuses everything passes every test of a refusal,
and this project has walked into that trap three times through three different doors. So the
partition is asserted over, twice and in opposite directions:

  * `test_a_second_run_...` reds if the claim is not taken (delete the `flock`, or make it
    `LOCK_SH`, or drop the `return 3`).
  * `test_the_partition_is_real_...` reds if the claim is taken unconditionally (`return 3` with
    no condition passes the leg above and dies here).
  * `test_a_run_that_CRASHES_...` reds if the claim is acquired and never dropped. Note WHICH
    leg does that work: the clean-exit `test_the_claim_is_released_...` does not, because
    deleting the release entirely leaves it green -- `run` returns, its frame dies, and the
    refcount closes the descriptor for it. That was measured, not assumed, and it is why the
    crash leg exists.

Twelve mutations were applied to the claim and eleven redden a named leg. The twelfth is an
EQUIVALENCE and not a gap: dropping the explicit `LOCK_UN` while keeping `handle.close()`
survives, because the kernel releases an `flock` when the descriptor closes. Recorded so the next
reader does not spend an afternoon re-deriving it.

BOTH PROCESSES ARE REAL, and the contested legs carry a DEADLINE. The holder is a subprocess
because the defect is cross-tree, and a control whose two sides are both values this test owns is
the shape that has fooled us before. The contender is a subprocess because of something sharper:
one of the twelve mutations does not redden anything, it HANGS -- see `_run_contested`.
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import tools.contract_battery as cb
from tools.contract_battery import BatterySpec

SPEC = BatterySpec(
    name="fixture_subject",
    subject="background/ops_repo.py",
    suites=("tests/background/test_ntfy_mirror.py",),
    poison_old="\ndef commit_and_push(",
    poison_new='\nraise RuntimeError("POISON")\n\n\ndef commit_and_push(',
    mutations=(("M1", "the write refuses under a test process", "    if in_test_process():",
                "    if False:"),),
)

#: Holds a real claim on the path in argv[1], announces it, and waits to be told to let go. It
#: takes the claim through the ENGINE'S OWN function, so the identity record under test is the
#: one a real run writes rather than one this file invented.
_HOLDER = textwrap.dedent("""
    import sys
    from pathlib import Path
    sys.path.insert(0, sys.argv[2])
    from tools.contract_battery import claim_the_results_file
    handle, held_by = claim_the_results_file(Path(sys.argv[1]))
    assert handle is not None, held_by
    print("HELD", flush=True)
    sys.stdin.readline()
""")


@pytest.fixture
def holder(tmp_path):
    """A second process holding the claim on `tmp_path/shared.json`, for the life of the test."""
    out = tmp_path / "shared.json"
    proc = subprocess.Popen(
        [sys.executable, "-c", _HOLDER, str(out), str(cb.PROJECT)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        assert proc.stdout.readline().strip() == "HELD", "the holder never took the claim"
        yield out, proc
    finally:
        proc.stdin.close()
        proc.wait(timeout=30)


def test_a_second_run_of_the_same_spec_is_refused_while_the_first_holds_the_file(holder, tmp_path):
    """THE LOAD-BEARING LEG. Before this control both runs proceeded and merged their rows."""
    out, _ = holder
    assert _run_contested(out, tmp_path).returncode == 3, (
        "a run whose results file is held by another run in flight must refuse -- the "
        "fingerprint cannot tell two runs of one spec apart, because they are the same work"
    )


def test_the_refusal_names_the_run_that_holds_it(holder, tmp_path):
    """A refusal that says why is how you find out the refusal itself was wrong. The reader has
    to be able to tell 'another tree is mid-run' from 'something crashed and left a file'."""
    out, proc = holder
    printed = _run_contested(out, tmp_path).stdout
    assert str(proc.pid) in printed and str(cb.PROJECT) in printed, (
        f"the refusal must name the holding run's pid and tree; got:\n{printed}"
    )


def test_a_refused_run_has_not_touched_the_subject_or_written_a_pristine_copy(holder, tmp_path):
    """Ordering, not decoration. The loser reads the subject at a moment the winner may have it
    mutated, and a pristine copy taken then is a mutated copy the next restore would trust."""
    out, _ = holder
    pristine = tmp_path / "pristine.py"
    subject = cb.PROJECT / SPEC.subject
    before = subject.read_text(encoding="utf-8")

    assert _run_contested(out, tmp_path, pristine=pristine).returncode == 3
    assert not pristine.exists(), "the claim must be taken before the pristine copy is written"
    assert subject.read_text(encoding="utf-8") == before


def test_the_partition_is_real_and_an_uncontested_run_proceeds(tmp_path):
    """WITHOUT THIS LEG the refusal above is satisfied by an unconditional `return 3`, and every
    battery in the family is dead while reading exactly like a battery that refuses correctly."""
    assert _run(tmp_path / "own.json", tmp_path) == 0


def test_the_claim_is_released_so_the_next_run_can_take_it(tmp_path):
    """The fail-closed direction still fails. A claim held to process exit passes every leg
    above and refuses the second battery in any pytest session that runs two."""
    out = tmp_path / "sequential.json"
    assert _run(out, tmp_path) == 0
    assert _run(out, tmp_path) == 0, "the claim outlived the run that took it"


def test_a_run_that_CRASHES_still_releases_its_claim(tmp_path, monkeypatch):
    """The leg the clean-exit one above cannot supply, established by mutation and not assumed.

    Deleting the body of `release_the_results_file` leaves the test above GREEN: `run` returns,
    its frame dies, and CPython's refcount closes the descriptor, which drops the `flock`. The
    release reads as load-bearing and is being done for it by the garbage collector.

    That accident is exactly what a crash removes. A raised exception keeps the frame -- and the
    open handle in it -- alive on the traceback for as long as anything holds the exception, which
    in a real session is the reporting layer of whatever ran the battery. So the run that most
    needs the next attempt to be possible is the one that would lock it out. With the body gone
    this leg reds; with `finally: release(...)` it passes.
    """
    out = tmp_path / "crashed.json"

    def _boom(*_a, **_k):
        raise RuntimeError("the battery died mid-grade")

    monkeypatch.setattr(cb, "_grade_under_the_claim", _boom)
    with pytest.raises(RuntimeError) as reported:
        _run(out, tmp_path)
    monkeypatch.undo()

    assert reported.traceback, "the reporting layer holds the crash, and so its frames"
    assert _run(out, tmp_path) == 0, (
        "a crashed battery must not hold its results file against the re-run -- and the "
        "traceback that reports the crash is what keeps the handle alive"
    )


def test_the_claim_is_keyed_to_the_results_file_and_not_to_the_spec(holder, tmp_path):
    """The file is what the two runs share, so the file is what the claim guards. Keyed to the
    spec instead, the documented escape -- `--out` of your own -- would be refused too, and the
    refusal message would be telling the reader to do something that cannot work."""
    _, _ = holder
    assert _run(tmp_path / "elsewhere.json", tmp_path) == 0


def test_the_claim_file_carries_the_holders_identity(tmp_path):
    """Read only by the refusal message. Asserted here because a message that names nobody is
    indistinguishable from a message about a crash, and those have opposite remedies."""
    out = tmp_path / "identity.json"
    handle, held_by = cb.claim_the_results_file(out)
    try:
        assert held_by == ""
        record = json.loads(cb.lock_path(out).read_text(encoding="utf-8"))
        assert record["tree"] == str(cb.PROJECT) and record["pid"] > 0
    finally:
        cb.release_the_results_file(handle)


def _run_contested(out: Path, tmp_path: Path,
                   pristine: Path | None = None) -> subprocess.CompletedProcess:
    """Every leg that runs against a HELD file goes through here: a subprocess, with a deadline.

    NOT ceremony, and not merely for cross-process fidelity. Dropping `LOCK_NB` from the acquire
    does not redden a contested leg -- it HANGS it, and a hang is not a red. In-process, pytest
    waits forever and the suite reads as still running; measured, and it took the restore in the
    mutation harness down with it, leaving the subject patched on disk. The deadline is the only
    thing that turns "never returns" into a verdict, so it belongs on every contested leg rather
    than on one that the first hanging leg would never reach.

    It matters past the harness too. This battery is routinely started, backgrounded and
    forgotten, and a blocking acquire at the top of it produces a silence indistinguishable from
    a long grade.
    """
    driver = textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(cb.PROJECT)!r})
        from tools.contract_battery import run
        from tests.tools.test_two_battery_runs_cannot_share_one_results_file import SPEC
        sys.exit(run(SPEC, ["--out", {str(out)!r},
                            "--pristine", {str(pristine or tmp_path / "d.py")!r},
                            "--only", "NOTHING", "--suites", "no_such_suite"]))
    """)
    try:
        return subprocess.run([sys.executable, "-c", driver], capture_output=True, text=True,
                              timeout=60, cwd=str(cb.PROJECT))
    except subprocess.TimeoutExpired:
        pytest.fail("the contested run BLOCKED instead of refusing -- a battery that waits "
                    "silently at the top is indistinguishable from one that is grading")


def _run(out: Path, tmp_path: Path, pristine: Path | None = None) -> int:
    """SPEC against `out`, graded on no suites and no mutations.

    `--only NOTHING` matches no id and `--suites no_such_suite` selects none, so nothing is
    patched on disk. The claim is taken before either is consulted, which is what the return
    code here reports on.
    """
    subject = cb.PROJECT / SPEC.subject
    original = subject.read_text(encoding="utf-8")
    try:
        return cb.run(SPEC, ["--out", str(out),
                             "--pristine", str(pristine or tmp_path / "p.py"),
                             "--only", "NOTHING", "--suites", "no_such_suite"])
    finally:
        if subject.read_text(encoding="utf-8") != original:
            subject.write_text(original, encoding="utf-8")
