"""Two battery runs must not mutate one SUBJECT file at the same time.

THE DEFECT THIS NAMES (delivery seat, 2026-09-06). Two lanes independently built the battery's
results-file lock on the same day, from the same parent, and NEITHER touched the subject. They are
two resources at two scopes: the results file is a global `/var/tmp` path shared across working
trees; the subject is a per-tree source file that every battery PATCHES IN PLACE and restores at
the end. A lock keyed to the results file correctly does not refuse two runs whose results files
differ -- and those two runs then interleave one's mutation with the other's restore, each grading
cells against a file the other wrote.

IT IS LIVE, NOT LATENT, and by the results refusal's own words. That refusal ends *"or pass a
--out of your own"*; take that advice in the tree the other run is already grading and you have
built this collision on purpose, each run holding an uncontested claim on a results file nobody
else wants. The two-specs-for-one-subject case is the latent one -- the five live specs have five
distinct subjects today.

It was never wholly unguarded: `held_through_run` VOIDS a row whose subject did not hold. That is
detection after the fact, and the cost of it is a whole battery run discarded, where the cost of a
refusal is a wait. A control that can only report the damage is not the control.

WHAT MAKES THIS ABLE TO FAIL. A refusal that refuses everything passes every test of a refusal, so
the partition is asserted over in both directions, and the two things this claim is keyed to are
separated from the two things it is NOT keyed to:

  * `test_a_run_whose_subject_is_held_...` reds if the claim is not taken (delete the `flock`, make
    it `LOCK_SH`, or drop the `return 4`).
  * `test_the_partition_is_real_...` reds if the claim is taken unconditionally -- the shape that
    passes the leg above while killing every battery in the family.
  * `test_the_claim_is_keyed_to_the_SUBJECT_and_a_--out_of_your_own_does_not_escape_it` is the leg
    that would have been GREEN at HEAD before this repair, and it is the whole point: same subject,
    different results file, still refused.
  * `test_a_run_over_a_DIFFERENT_subject_...` is its opposite number: keyed to the subject means
    keyed to THAT subject, not to "a battery is running".
  * `test_a_run_that_CRASHES_...` reds if the claim is acquired and never dropped. The clean-exit
    leg cannot do that work -- deleting the release outright leaves it green, because `run`
    returns, its frame dies and refcounting closes the descriptor. Measured on the sibling control
    and re-measured here.

BOTH PROCESSES ARE REAL, and every contested leg carries a DEADLINE -- see `_run_contested`. A
mutation that drops `LOCK_NB` does not redden a contested leg, it HANGS it, and a hang is not a
red.

TWELVE MUTATIONS, ELEVEN KILLS, AND ONE LEG DELETED FOR SURVIVING. The twelfth asked whether the
subject refusal -- a NEW early return from inside the block holding the results claim -- can strand
that claim. It cannot, and the leg that asked was withdrawn rather than kept green: `return 4`
unwinds the frame, the handle's refcount drops, and CPython closes the descriptor, so emptying the
results release changes nothing any assertion here can see. Asked from outside it is worse than
useless, because the contested run is a subprocess and its exit hands every lock back whatever the
code does -- the leg was written that way first and it was re-stating the refusal in other words.
The one case where that release IS load-bearing is a CRASH, which is the sibling control's leg, and
emptying it was measured to redden exactly there. An equivalence, established rather than assumed,
and recorded here so the next reader does not re-derive it or, worse, restore the leg.
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import tools.contract_battery as cb
from tools.contract_battery import BatterySpec

#: `--only NOTHING` and `--suites no_such_suite` mean nothing is ever patched on disk by these
#: legs. The claims are taken before either is consulted, which is what every return code here
#: reports on.
SPEC = BatterySpec(
    name="fixture_subject_lock",
    subject="background/ops_repo.py",
    suites=("tests/background/test_ntfy_mirror.py",),
    poison_old="\ndef commit_and_push(",
    poison_new='\nraise RuntimeError("POISON")\n\n\ndef commit_and_push(',
    mutations=(("M1", "the write refuses under a test process", "    if in_test_process():",
                "    if False:"),),
)

#: A SECOND subject, so "keyed to the subject" can be told apart from "refuses while any battery
#: runs". Different module, different inode, and never patched by any leg here.
OTHER_SPEC = BatterySpec(
    name="fixture_other_subject_lock",
    subject="background/boot_sha.py",
    suites=("tests/background/test_ntfy_mirror.py",),
    poison_old="\ndef ",
    poison_new='\nraise RuntimeError("POISON")\n\n\ndef ',
    mutations=(("M1", "unused: no suite is selected in these legs", "x", "y"),),
)

#: Holds a real claim on the subject named in argv[1], announces it, and waits to be told to let
#: go. It takes the claim through THE ENGINE'S OWN function, so what is contested is the claim a
#: real run takes rather than one this file invented.
_HOLDER = textwrap.dedent("""
    import sys
    from pathlib import Path
    sys.path.insert(0, sys.argv[2])
    from tools.contract_battery import claim_the_subject_file
    handle, held_by = claim_the_subject_file(Path(sys.argv[1]))
    assert handle is not None, held_by
    print("HELD", flush=True)
    sys.stdin.readline()
""")


@pytest.fixture
def holder():
    """A second process holding the claim on SPEC's subject, for the life of the test."""
    subject = cb.PROJECT / SPEC.subject
    proc = subprocess.Popen(
        [sys.executable, "-c", _HOLDER, str(subject), str(cb.PROJECT)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        assert proc.stdout.readline().strip() == "HELD", (
            "the holder never took the claim -- and the likeliest reason is not this fixture. An "
            "earlier leg in this file runs the battery IN PROCESS, so a release that stopped "
            "working leaves THIS pytest process holding the subject, and every later holder is "
            "refused by us. Read the first red in the file, not this one."
        )
        yield proc
    finally:
        proc.stdin.close()
        proc.wait(timeout=30)


def test_a_run_whose_subject_is_held_by_another_run_is_refused(holder, tmp_path):
    """THE LOAD-BEARING LEG. Before this control both runs proceeded and patched one file."""
    assert _run_contested(tmp_path / "mine.json", tmp_path).returncode == 4, (
        "a run whose subject is being mutated by another run in flight must refuse -- the two "
        "interleave one's patch with the other's restore, and every row of both is void"
    )


def test_the_claim_is_keyed_to_the_SUBJECT_and_a_out_of_your_own_does_not_escape_it(holder,
                                                                                   tmp_path):
    """THE LEG THAT WAS GREEN AT HEAD, and the reason this exists beside the results-file lock.

    The results refusal tells the reader to *"pass a --out of your own"*. Doing that in this tree
    leaves both runs uncontested on their results files and contesting the source. Every leg here
    already passes a private `--out`, so this asserts the same thing they do -- it is written out
    separately because it is the CLAIM about the repair, and a reader looking for what the second
    lock buys should not have to infer it from a fixture argument.
    """
    own = tmp_path / "a_out_of_my_own.json"
    assert not own.exists(), "the contended thing must not be the results file"
    assert _run_contested(own, tmp_path).returncode == 4


def test_a_run_over_a_DIFFERENT_subject_proceeds_while_this_one_is_held(holder, tmp_path):
    """Keyed to THAT file, not to 'a battery is running'. Without this leg a claim taken over the
    whole family -- one lock for all five specs -- passes every leg above, and serialises work
    that never contended for anything."""
    assert _run(OTHER_SPEC, tmp_path / "other.json", tmp_path) == 0


def test_the_partition_is_real_and_an_uncontested_run_proceeds(tmp_path):
    """WITHOUT THIS LEG the refusal above is satisfied by an unconditional `return 4`, and every
    battery in the family is dead while reading exactly like a battery that refuses correctly."""
    assert _run(SPEC, tmp_path / "own.json", tmp_path) == 0


def test_the_refusal_names_the_run_that_holds_it(holder, tmp_path):
    """The holder's identity comes from `/proc/locks` and CAN come back empty, by design -- the
    subject is a source file and there is nowhere to write an identity record into it. So the
    honest-degradation path must be proved not to be the only path: an unavailable check that has
    quietly become permanently unavailable reports 'cannot tell' forever and reads as working."""
    printed = _run_contested(tmp_path / "named.json", tmp_path).stdout
    assert f"pid {holder.pid}" in printed, (
        f"the refusal must name the holding run's pid, and the kernel can say it here; "
        f"got:\n{printed}"
    )
    assert SPEC.subject in printed, "and the subject, which is what the reader has to wait for"


def test_the_kernel_lookup_answers_for_a_HELD_inode_and_not_for_a_free_one(holder):
    """The lookup itself, over the partition it has to separate. A parser that matched every row
    would name a holder for a file nobody holds, and `_the_kernel_names_the_holder` is the one
    piece here that is a text format someone else owns."""
    held = (cb.PROJECT / SPEC.subject).open("r", encoding="utf-8")
    free = (cb.PROJECT / OTHER_SPEC.subject).open("r", encoding="utf-8")
    try:
        assert cb._the_kernel_names_the_holder(held) == f"pid {holder.pid}"
        assert cb._the_kernel_names_the_holder(free) == "", (
            "an unheld inode has no holder, and a lookup that names one for it would put a "
            "pid into a refusal that never happened"
        )
    finally:
        held.close()
        free.close()


def test_a_refused_run_has_not_written_a_pristine_copy_or_touched_the_subject(holder, tmp_path):
    """Ordering, not decoration -- and sharper here than for the results file. The loser reads the
    subject at a moment the winner has it PATCHED, and a pristine copy taken then is a mutated
    copy that the loser's own restore would later write over the real source."""
    pristine = tmp_path / "pristine.py"
    subject = cb.PROJECT / SPEC.subject
    before = subject.read_text(encoding="utf-8")

    assert _run_contested(tmp_path / "refused.json", tmp_path, pristine=pristine).returncode == 4
    assert not pristine.exists(), "the claim must be taken before the pristine copy is written"
    assert subject.read_text(encoding="utf-8") == before


def test_the_claim_is_released_so_the_next_run_can_take_it(tmp_path):
    """The fail-closed direction still fails. A claim held to process exit passes every leg above
    and refuses the second battery in any pytest session that runs two."""
    assert _run(SPEC, tmp_path / "first.json", tmp_path) == 0
    assert _run(SPEC, tmp_path / "second.json", tmp_path) == 0, (
        "the claim on the subject outlived the run that took it"
    )


def test_a_run_that_CRASHES_still_releases_its_claim(tmp_path, monkeypatch):
    """The leg the clean-exit one above cannot supply, established by mutation and not assumed.

    Emptying `release_the_subject_file` leaves the test above GREEN: `run` returns, its frame
    dies, and CPython's refcount closes the descriptor, which drops the `flock`. That accident is
    exactly what a crash removes -- a raised exception keeps the frame, and the open handle in it,
    alive on the traceback for as long as the reporting layer holds the exception. The run that
    most needs the next attempt to be possible is the one that would lock the subject out.
    """
    def _boom(*_a, **_k):
        raise RuntimeError("the battery died mid-grade")

    monkeypatch.setattr(cb, "_grade_under_the_claim", _boom)
    with pytest.raises(RuntimeError) as reported:
        _run(SPEC, tmp_path / "crashed.json", tmp_path)
    monkeypatch.undo()

    assert reported.traceback, "the reporting layer holds the crash, and so its frames"
    assert _run(SPEC, tmp_path / "after_crash.json", tmp_path) == 0, (
        "a crashed battery must not hold its subject against the re-run"
    )


def _run_contested(out: Path, tmp_path: Path,
                   pristine: Path | None = None) -> subprocess.CompletedProcess:
    """Every leg that runs against a HELD subject goes through here: a subprocess, with a deadline.

    NOT ceremony. Dropping `LOCK_NB` from the acquire does not redden a contested leg -- it HANGS
    it, in-process, forever, and takes the mutation harness's own restore down with it, leaving
    the subject patched on disk. A hang is not a red, and a control whose mutation hangs has not
    been graded. The deadline is the only thing that turns "never returns" into a verdict, so it
    belongs on every contested leg rather than on one the first hanging leg would never reach.
    """
    driver = textwrap.dedent(f"""
        import sys
        sys.path.insert(0, {str(cb.PROJECT)!r})
        from tools.contract_battery import run
        from tests.tools.test_two_battery_runs_cannot_mutate_one_subject_file import SPEC
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


def _run(spec: BatterySpec, out: Path, tmp_path: Path) -> int:
    """`spec` against `out`, graded on no suites and no mutations, with the subject restored if
    anything patched it anyway."""
    subject = cb.PROJECT / spec.subject
    original = subject.read_text(encoding="utf-8")
    try:
        return cb.run(spec, ["--out", str(out), "--pristine", str(tmp_path / "p.py"),
                             "--only", "NOTHING", "--suites", "no_such_suite"])
    finally:
        if subject.read_text(encoding="utf-8") != original:
            subject.write_text(original, encoding="utf-8")
