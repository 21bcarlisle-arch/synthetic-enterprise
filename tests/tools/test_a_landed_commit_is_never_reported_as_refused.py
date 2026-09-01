#!/usr/bin/env python3
"""`surgical_land` must never let a caller conclude that a landed commit did not land.

THE DEFECT, observed 2026-09-01 on a real landing. The tool printed:

    [surgical-land] REFUSED: the commit LANDED but refreshing the index for its paths failed
    rc=128: ...index.lock': File exists.

— honest and self-contradictory in one sentence — while its commit sat on HEAD as `396bb09ba`. The
post-commit index refresh had raised `LandingRefused`, the same type the tool raises for a RED GATE.

WHY THAT IS DANGEROUS RATHER THAN UNTIDY. `land()`'s documented contract is "returns the new commit
sha, or raises LandingRefused". A daemon or an executor keying on that type concludes the work is
unlanded, and then does one of the two harmful things: re-lands it (a second commit of a tree that
is already the parent), or reports failure for work that shipped. The human failure mode is the same
— the word REFUSED is what a reader takes away, and only checking HEAD reveals otherwise.

AND THE WINDOW IS NOT NARROW. `.git/index.lock` is held by another lane's `git commit`, and a commit
in this repository is ten to fifteen minutes of gate. So this failure was available for a quarter of
an hour every time any lane committed — which is most of the working day, on a tree with six
concurrent lanes. The instance that produced this file waited 75 seconds for the holder to finish.

THE REPAIR, in two parts, and both are tested below:
  1. `_refresh_with_retry` outlasts the lock holder rather than failing beside it, bounded by a
     deadline it cannot outlive. It runs AFTER the commit is on HEAD, so waiting costs nobody.
  2. If it still fails, the type raised is `IndexNotRefreshed`, carrying the landed `sha`. It is a
     `LandingRefused` subclass so existing fail-closed handlers keep working, but it is separable,
     it says THE COMMIT LANDED first, and it says "do NOT re-land".

MUTATION: make `_refresh_with_retry` return the first failure and
`test_a_held_lock_is_waited_out` reds. Retry on every failure and
`test_a_real_error_is_not_retried_into_silence` reds. Raise the base `LandingRefused` again, or drop
the sha, and the two contract tests red.
"""
from __future__ import annotations

import time

import pytest

from tools import surgical_land as sl


class _Result:
    """The shape `_git` returns: a returncode and bytes stderr."""

    def __init__(self, returncode: int, stderr: bytes = b""):
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = b""


LOCK_ERR = (
    b"fatal: Unable to create '/repo/.git/index.lock': File exists.\n\n"
    b"Another git process seems to be running in this repository"
)


def test_a_held_lock_is_waited_out(monkeypatch):
    """THE CASE. The holder is a process that will finish; the only thing worth doing is outlast
    it. Three failures then a success must come back as a success, not as a refusal."""
    calls = {"n": 0}

    def fake_git(root, *args, **kwargs):
        calls["n"] += 1
        return _Result(0) if calls["n"] > 3 else _Result(128, LOCK_ERR)

    monkeypatch.setattr(sl, "_git", fake_git)
    monkeypatch.setattr(sl, "_INDEX_LOCK_POLL_S", 0.0)
    result = sl._refresh_with_retry(sl.Path("/repo"), b"payload")
    assert result.returncode == 0
    assert calls["n"] == 4, "the lock failure must be retried until it clears"


def test_a_real_error_is_not_retried_into_silence(monkeypatch):
    """The other direction, and it is the one that would make this repair worse than the defect.
    Only a HELD LOCK is retryable. rc=128 also covers a corrupt object and a bad payload, and
    retrying those would turn one bad landing into twenty minutes of nothing happening."""
    calls = {"n": 0}

    def fake_git(root, *args, **kwargs):
        calls["n"] += 1
        return _Result(128, b"fatal: unable to read tree deadbeef")

    monkeypatch.setattr(sl, "_git", fake_git)
    monkeypatch.setattr(sl, "_INDEX_LOCK_POLL_S", 0.0)
    result = sl._refresh_with_retry(sl.Path("/repo"), b"payload")
    assert result.returncode == 128
    assert calls["n"] == 1, "a non-lock failure must return on the first attempt"


def test_the_wait_cannot_outlive_its_deadline(monkeypatch):
    """A waiter without a deadline hangs a daemon behind a crashed git. This one is bounded, and
    the bound is wall-clock rather than a retry count so a fast poll cannot smuggle in an
    unbounded wait."""
    monkeypatch.setattr(sl, "_git", lambda root, *a, **k: _Result(128, LOCK_ERR))
    monkeypatch.setattr(sl, "_INDEX_LOCK_POLL_S", 0.0)
    monkeypatch.setattr(sl, "_INDEX_LOCK_DEADLINE_S", 0.05)
    started = time.monotonic()
    result = sl._refresh_with_retry(sl.Path("/repo"), b"payload")
    assert result.returncode == 128
    assert time.monotonic() - started < 5.0, "the retry loop outlived its own deadline"


def test_MUTATION_a_landed_commit_is_not_reported_with_the_type_used_for_a_red_gate(monkeypatch):
    """THE CONTRACT. A red gate and a landed-but-unrefreshed commit mean opposite things to a
    caller and were sharing one exception type and one word."""
    monkeypatch.setattr(sl, "_git", lambda root, *a, **k: _Result(128, LOCK_ERR))
    monkeypatch.setattr(sl, "_git_text", lambda root, *a, **k: "")
    monkeypatch.setattr(sl, "_INDEX_LOCK_POLL_S", 0.0)
    monkeypatch.setattr(sl, "_INDEX_LOCK_DEADLINE_S", 0.0)

    with pytest.raises(sl.IndexNotRefreshed) as caught:
        sl._refresh_index_for(sl.Path("/repo"), "tree", ["a.py"], sha="cafebabe")

    assert type(caught.value) is not sl.LandingRefused, (
        "a landed commit must not raise the same type as a refused one"
    )
    assert isinstance(caught.value, sl.LandingRefused), (
        "it must stay a LandingRefused subclass so existing fail-closed handlers keep working"
    )
    assert caught.value.sha == "cafebabe", (
        "the landed sha must travel with the exception, or a caller that catches it has no way "
        "to record what actually happened"
    )
    message = str(caught.value)
    assert "LANDED" in message and message.index("LANDED") < 40, (
        "the message must say the commit landed FIRST -- a reader takes away the first clause"
    )
    assert "do NOT re-land" in message or "Do NOT re-land" in message, (
        "the message must name the one thing a caller must not do"
    )


def test_the_landed_sha_reaches_the_exception_from_the_real_call_sites():
    """Keyed to the call sites rather than to the helper, because the sha is threaded through and
    a refactor that dropped the argument would leave every message saying "(sha unavailable)"
    while every test above still passed."""
    import inspect

    source = inspect.getsource(sl)
    calls = [ln for ln in source.splitlines() if "_refresh_index_for(root, result_tree" in ln]
    assert len(calls) == 2, f"expected the two known call sites, found {len(calls)}"
    for line in calls:
        assert "sha=" in line, f"call site does not pass the landed sha: {line.strip()}"
