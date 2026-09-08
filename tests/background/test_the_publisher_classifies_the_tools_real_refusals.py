"""The publish commit's four outcomes, decided by driving the REAL tool (2026-09-08).

WHY THIS FILE EXISTS. The publish commit stopped being `git commit -m msg -- <pathspec>` and
became `tools.surgical_land.land`, because a pathspec `git commit` runs the pre-commit hook chain
against the SHARED WORKING TREE -- which routinely holds three other lanes' uncommitted work, and
which is why `last_clean_publish` was null across 24 consecutive cycles that each named a
different gate. A landing builds HEAD-plus-its-own-paths and gates THAT tree, so another lane's
file cannot refuse us.

THE COST OF THE ROUTE, and the reason for this file. The tool signals every failure as one
exception type, `LandingRefused`, whose TEXT is the only thing distinguishing four situations the
publisher must send readers to four different places for:

    already-at-HEAD  -> NOTHING_TO_COMMIT    "nothing changed this cycle" -- a no-op, retryable
    gate killed      -> COMMIT_TIMEOUT       "the chain outran its deadline" -- NO test judged
    lost tree lock   -> TREE_LOCK_UNAVAILABLE"the gate PASSED, another writer held the lock"
    gate red         -> COMMIT_REFUSED       "the gate said no about OUR paths" -- read the reds

So `git_commit_push` matches on sentences owned by another module. That is a two-homes hazard of
exactly the shape this project keeps paying for: reword `_land_once`'s "already at HEAD" and a
no-op cycle starts being published as a REFUSAL, with a spurious blocking-test record attached,
and nothing anywhere goes red. Every other test of this classifier hands it a string a human
typed; this one makes the tool produce the string.

R15 -- WHAT EACH TEST KILLS:
  * `..._a_cycle_that_changed_nothing`  -- reword `_land_once`'s already-at-HEAD refusal, or drop
        the publisher's branch for it: the no-op is filed as COMMIT_REFUSED and the run is never
        published again (COMMIT_REFUSED is not retryable, so the next identical cycle re-attempts
        forever) while the record grows a refusal nothing refused.
  * `..._a_red_gate`                    -- the differential. Same repo, same call, one thing
        changed (the hook's exit code), and the answer must move. Without it the test above
        passes just as well against a classifier that returns NOTHING_TO_COMMIT for everything.
  * `..._names_the_refusing_gate`       -- the hook's own banner has to survive the tool, the
        exception, and the classifier into the log a reader opens.

WHAT IS DELIBERATELY NOT DRIVEN HERE: the lost tree lock (it needs a second process holding an
flock for 900s) and the killed gate (a real 3600s kill). Both are driven from their texts in
`test_process_run_complete.py` and `test_a_refused_publish_commit_reaches_the_wedge_detector.py`;
this file covers the two that a real repo can produce in under a second, which are also the two
that happen every day.
"""
from __future__ import annotations

import contextlib
import subprocess

import pytest

from background import process_run_complete as prc

GATE_GREEN = "#!/bin/sh\nexit 0\n"
GATE_RED = (
    "#!/bin/sh\n"
    "echo '[status-honesty] COMMIT REFUSED -- the staged log carries a stale line.'\n"
    "exit 1\n"
)


def _git(repo, *args):
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, "git {}: {}".format(" ".join(args), r.stderr)
    return r.stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """A real git repository with a real pre-commit hook, and one committed publish surface."""
    root = tmp_path / "repo"
    (root / "tools" / "git-hooks").mkdir(parents=True)
    (root / "site" / "data").mkdir(parents=True)
    hook = root / "tools" / "git-hooks" / "pre-commit"
    hook.write_text(GATE_GREEN)
    hook.chmod(0o755)
    (root / "site" / "data" / "dashboard.json").write_text('{"net": 1}\n')
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


def _publish(repo, monkeypatch, *, log_sink):
    """Drive `git_commit_push` against `repo` with the REAL landing, and return its outcome.

    Everything stubbed here is upstream of the commit and has its own tests; the landing itself
    -- the subject -- is not stubbed, which is the whole point of the file.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", repo)
    monkeypatch.setattr(prc, "LOG_FILE", repo / "log.md")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", repo / "cause.json")
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", repo / "blocking.json")
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", repo / "gate_state.json")
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 0)
    monkeypatch.setattr(prc, "_clear_two_rooms_before_commit", lambda *a, **k: {})
    monkeypatch.setattr(prc, "_record_commit_hook_duration", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_push_due", lambda: False)
    monkeypatch.setattr(prc, "_commit_pathspec",
                        lambda *a, **k: [str(repo / "site" / "data" / "dashboard.json")])
    monkeypatch.setattr(prc, "log", lambda m, *a, **k: log_sink.append(str(m)))

    outcome = {}
    prc.git_commit_push("abc1234", 1000.0, outcome=outcome)
    return outcome.get("reason"), "\n".join(log_sink)


def test_a_cycle_that_changed_nothing_is_a_no_op_and_not_a_refusal(repo, monkeypatch):
    """Nothing on disk differs from HEAD, so the resulting tree IS HEAD's tree.

    The tool refuses -- correctly, there is nothing to commit -- and the publisher must read that
    refusal as the commonest branch on this path rather than as a gate saying no.
    """
    reason, _log = _publish(repo, monkeypatch, log_sink=[])

    assert reason == prc.NOTHING_TO_COMMIT, (
        "a cycle whose surfaces did not change was filed as {!r} -- the run is recorded as a "
        "publish FAILURE, and a refusal nothing refused reaches the record".format(reason))
    assert prc.NOTHING_TO_COMMIT in prc.RETRYABLE_PUBLISH_OUTCOMES
    assert not prc.GATE_BLOCKING_TESTS_FILE.exists(), (
        "a no-op recorded a blocking-test set -- absent must read as absent")


def test_a_red_gate_is_a_refusal_and_names_the_gate_that_refused(repo, monkeypatch):
    """THE DIFFERENTIAL. Same repository, same call, two things changed together -- the surface
    now differs from HEAD, and the hook now exits 1 -- and the answer must move."""
    # THE HOOK IS COMMITTED, not merely written to the working tree -- and that is the tool
    # working, not a fixture detail. The gate runs against the tree the commit WOULD create,
    # which is HEAD plus the pathspec; an uncommitted hook is not in that tree, so a red one left
    # unstaged correctly gates nothing. Writing it and expecting a refusal is how this test first
    # failed, and the failure was the tool being right.
    hook = repo / "tools" / "git-hooks" / "pre-commit"
    hook.write_text(GATE_RED)
    hook.chmod(0o755)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "a gate that refuses")
    (repo / "site" / "data" / "dashboard.json").write_text('{"net": 2}\n')
    head_before = _git(repo, "rev-parse", "HEAD")

    reason, log = _publish(repo, monkeypatch, log_sink=[])

    assert reason == prc.COMMIT_REFUSED, reason
    assert prc.COMMIT_REFUSED not in prc.RETRYABLE_PUBLISH_OUTCOMES
    # The hook's own words survive the tool, the exception and the classifier into the log a
    # reader opens. A refusal that reaches the log without its cause is the fail-silent shape
    # this whole publish-record mechanism exists to end.
    assert "status-honesty" in log, log
    assert "COMMIT REFUSED" in log, log
    # And nothing was committed: the tool refuses BEFORE the compare-and-swap, so HEAD is where
    # it was and the working-tree copy is untouched.
    assert _git(repo, "rev-parse", "HEAD") == head_before, "a red gate landed a commit"
    assert (repo / "site" / "data" / "dashboard.json").read_text() == '{"net": 2}\n'


def test_a_green_gate_over_a_changed_surface_actually_lands(repo, monkeypatch):
    """THE NULL CONTROL, and the reason the two above mean anything: with the surface changed and
    the gate green, the landing must produce a real commit carrying exactly that path.

    MUTATION: make `_land_publish_commit` return a refusal unconditionally -- the two tests above
    still pass (both expect a refusal) and this one reds. Without it a total publishing outage
    reads as a green suite.
    """
    (repo / "site" / "data" / "dashboard.json").write_text('{"net": 3}\n')
    log = []

    reason, _log = _publish(repo, monkeypatch, log_sink=log)

    assert reason not in (prc.COMMIT_REFUSED, prc.NOTHING_TO_COMMIT, prc.COMMIT_TIMEOUT), reason
    assert _git(repo, "log", "--oneline").count("\n") == 1, "the landing did not create a commit"
    assert _git(repo, "show", "--name-only", "--format=", "HEAD") == "site/data/dashboard.json"
    assert _git(repo, "show", "HEAD:site/data/dashboard.json") == '{"net": 3}'
    assert "LANDED" in "\n".join(log)
