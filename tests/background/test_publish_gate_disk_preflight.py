"""A full disk must not read as a red test (2026-08-09, the third publish wedge).

WHY THIS MODULE EXISTS. The publish gate materialises HEAD into a throwaway directory on
whatever filesystem `tempfile` chooses -- on this box a 7.8GB tmpfs. On 2026-08-09 that tmpfs
was exhausted by 4.4GB of repo checkouts abandoned by the DIAGNOSTIC runs of the two earlier
wedges (the gate itself cleans up in its own `finally`; the debris was ours). The gate then
failed twice, and neither failure named the cause:

    Publish gate: `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir
    Publish gate: could not make the HEAD checkout a git repo: git is not installed

The second is worse than useless -- git was installed and working. Publishing was wedged, a
tick was hunting a red test, and the log pointed at a missing binary. HEAD was green.

WHAT IS UNDER TEST. `_head_checkout`'s pre-flight: it reads free space BEFORE extraction, while
the cause is still legible, and refuses with a line that names DISK. It does not make a red
green -- fail-closed is unchanged and deliberate (R15: an unavailable check is a failed check).
It makes the failure self-describing.

R15, both directions:
  * the guard FIRES on its own named defect -- an exhausted filesystem is refused, and the log
    line names disk rather than git (`test_a_full_tmpfs_is_refused_and_the_log_says_disk`);
  * the guard is NOT vacuous -- with space available the pre-flight lets the checkout proceed
    (`test_ample_space_does_not_short_circuit_the_checkout`), so it cannot pass by refusing
    everything, and an unreadable filesystem does not silently wedge publishing
    (`test_an_unreadable_filesystem_does_not_wedge_publishing`);
  * MUTATION -- with the threshold mutated to zero the same exhausted filesystem is let
    through (`test_mutation_a_zero_threshold_lets_the_full_disk_through`), which is what proves
    the refusal above comes from this guard and not from something else in the path.
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from background import process_run_complete as prc  # noqa: E402


class _Reached(Exception):
    """Raised in place of the real extraction to prove the pre-flight did not short-circuit.

    Asserting "we got past the guard" this way keeps the test to the branch it is about: a real
    materialisation is ~130MB and would make this module pay for the whole checkout to learn one
    boolean."""


@pytest.fixture
def logged(monkeypatch):
    """Capture the gate's log lines instead of appending to the real observability log."""
    lines = []
    monkeypatch.setattr(prc, "log", lines.append)
    return lines


@pytest.fixture
def extraction_tripwire(monkeypatch):
    """Make any attempt to materialise a checkout raise, so passing the guard is observable."""
    def _boom(*args, **kwargs):
        raise _Reached()
    monkeypatch.setattr(prc.tempfile, "mkdtemp", _boom)


def _run_checkout():
    with prc._head_checkout() as path:
        return path


def test_a_full_tmpfs_is_refused_and_the_log_says_disk(monkeypatch, logged):
    """The named defect: free space below the threshold, nothing wrong with the code."""
    monkeypatch.setattr(prc, "_free_mb", lambda _p: 10)

    assert _run_checkout() is None, "an exhausted filesystem must fail closed, not publish"

    said = "\n".join(logged).lower()
    assert "disk" in said, "the operator-facing line must name DISK: {!r}".format(logged)
    assert "10mb free" in said.replace(" mb free", "mb free"), (
        "the line must carry the MEASURED free space, not just a category: {!r}".format(logged))
    # The 2026-08-09 lines sent the reader after git. This one must not.
    assert "git is not installed" not in said


def test_the_refusal_does_not_claim_a_test_failed(monkeypatch, logged):
    """The wedge alarm's reader is looking for a red test. This failure has none, and the log
    must not let it be read as one -- that misreading is the whole cost of the incident."""
    monkeypatch.setattr(prc, "_free_mb", lambda _p: 10)

    _run_checkout()

    said = "\n".join(logged).lower()
    assert "head may be green" in said, (
        "the line must say HEAD may be green, or the next tick hunts a red test that does not "
        "exist: {!r}".format(logged))


def test_ample_space_does_not_short_circuit_the_checkout(
        monkeypatch, logged, extraction_tripwire):
    """Anti-vacuity: a guard that refuses everything would pass the test above for free."""
    monkeypatch.setattr(prc, "_free_mb", lambda _p: 100_000)

    with pytest.raises(_Reached):
        _run_checkout()

    assert not any("disk" in line.lower() for line in logged), (
        "a healthy filesystem must produce no disk complaint: {!r}".format(logged))


def test_an_unreadable_filesystem_does_not_wedge_publishing(
        monkeypatch, logged, extraction_tripwire):
    """`_free_mb` returning None is 'I could not measure', not 'zero bytes free'. Treating it as
    zero would hand the pre-flight a way to wedge publishing on a stat failure -- the fail-open
    /fail-closed choice is made explicitly here rather than falling out of an int comparison."""
    monkeypatch.setattr(prc, "_free_mb", lambda _p: None)

    with pytest.raises(_Reached):
        _run_checkout()


def test_mutation_a_zero_threshold_lets_the_full_disk_through(
        monkeypatch, logged, extraction_tripwire):
    """MUTATION (R15). Same exhausted filesystem, guard disarmed: the refusal disappears. That
    is what shows the refusal in the first test is produced BY this guard."""
    monkeypatch.setattr(prc, "_free_mb", lambda _p: 10)
    monkeypatch.setattr(prc, "HEAD_CHECKOUT_MIN_FREE_MB", 0)

    with pytest.raises(_Reached):
        _run_checkout()

    assert not any("disk" in line.lower() for line in logged)


def test_free_mb_reads_a_real_filesystem():
    """The helper is not a stub: on a directory that exists it returns a plausible number."""
    free = prc._free_mb(REPO)
    assert free is not None and free > 0


def test_free_mb_returns_none_rather_than_raising(monkeypatch):
    """A stat failure must not take the publish path down -- it must be reportable."""
    def _raise(_p):
        raise OSError("no such filesystem")
    monkeypatch.setattr(prc.shutil, "disk_usage", _raise)

    assert prc._free_mb("/nonexistent-path-for-this-test") is None


def test_the_threshold_exceeds_a_real_checkout():
    """A threshold below the size of the thing it is protecting would be theatre. The measured
    extraction is ~130MB; the floor must leave room for it plus git's index and objects."""
    assert prc.HEAD_CHECKOUT_MIN_FREE_MB >= 300
