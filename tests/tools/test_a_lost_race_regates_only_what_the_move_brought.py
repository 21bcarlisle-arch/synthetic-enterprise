"""A landing that loses the race re-gates its tests on what the move brought, not on everything.

The defect this names (docs/staging/SEAT_FINDING_THE_COMMIT_GATE_LOSES_ITS_HOUR_2026-11-22.md):
`surgical_land` re-ran the WHOLE pytest selection after every lost compare-and-swap. Reg 6C's gate
ran ~50 minutes while the trunk moved every 15-30, so each lost race bought another 50 minutes on a
tree that differed from the one already gated green only in paths the mover brought -- and the
landing could never win.

The repair hands the next attempt the commit of the tree it gated green, through the same variable
a merge uses, so `pre_commit_test_gate.selection_paths` keys on the paths that differ from BOTH
the new base and that green tree. Each leg below fails on a named defect:

  * NOT THREADED: the second attempt's gate gets no green commit -> the full selection again.
  * WRONG TREE: the token names something other than the tree that actually passed.
  * A RED VERDICT CARRIED: a red gate is still terminal, never a token.
  * TOO NARROW: a path the lane rewrote between attempts is still selected.
  * SILENT: the receipt names the green tree it narrowed against.
  * NOT IN THE ENV: `run_gate` must put the token where the gate reads it, and a real merge's
    own token wins.
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import pytest

from tools import pre_commit_test_gate as gate_mod
from tools import surgical_land as sl

HOOK = textwrap.dedent(
    """\
    #!/bin/sh
    if [ -f gate_verdict ] && [ "$(cat gate_verdict)" = "red" ]; then
        echo "1 failed"
        exit 1
    fi
    echo "3 passed in 0.01s"
    exit 0
    """
)
MSG_HOOK = "#!/bin/sh\nexit 0\n"


def _run(repo: Path, *args: str) -> str:
    r = subprocess.run(args, cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, "{} failed: {}".format(args, r.stderr)
    return r.stdout.strip()


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    (r / "tools" / "git-hooks").mkdir(parents=True)
    _run(r.parent, "git", "init", "-q", "-b", "main", str(r))
    _run(r, "git", "config", "user.email", "t@example.com")
    _run(r, "git", "config", "user.name", "T")
    (r / "tools" / "git-hooks" / "pre-commit").write_text(HOOK)
    (r / "tools" / "git-hooks" / "commit-msg").write_text(MSG_HOOK)
    (r / "gate_verdict").write_text("green")
    (r / "code.py").write_text("VALUE = 1\n")
    _run(r, "git", "add", "-A")
    _run(r, "git", "commit", "-q", "-m", "base")
    return r


def _racing(repo: Path, lose_until: int, seen: list[dict], between=None):
    """Run the real gate, then land a colleague's commit on a DISJOINT path for the first
    `lose_until` calls, recording what each call was handed and the tree it gated."""
    real = sl.run_gate

    def gate(checkout, hook_rel=sl.HOOK_REL, gated_tree=None, merge_parent=None,
             prior_green=None):
        rc, out, err = real(checkout, hook_rel, gated_tree, merge_parent, prior_green)
        seen.append({"prior_green": prior_green, "tree": gated_tree,
                     "base": _run(repo, "git", "rev-parse", "HEAD")})
        if len(seen) <= lose_until:
            name = "colleague_{}.txt".format(len(seen))
            (repo / name).write_text("landed mid-gate\n")
            _run(repo, "git", "add", name)
            _run(repo, "git", "commit", "-q", "--no-verify", "-m", "colleague")
            if between is not None:
                between()
        return rc, out, err

    return gate


def _combined(repo: Path, sha: str, token: str) -> set[str]:
    """What `selection_paths` would select on: staged (commit vs its parent) AND differing from
    the token -- the gate's own merge rule, re-derived here from git."""
    staged = set(_run(repo, "git", "diff", "--name-only", sha + "^", sha).splitlines())
    differs = set(_run(repo, "git", "diff", "--name-only", token, sha).splitlines())
    return staged & differs


def test_the_second_attempt_is_handed_the_tree_the_first_gated_green(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    (repo / "code.py").write_text("VALUE = 2\n")
    seen: list[dict] = []
    monkeypatch.setattr(sl, "run_gate", _racing(repo, lose_until=1, seen=seen))

    sha = sl.land(repo, ["code.py"], "lands on the second", attempts=3)

    assert len(seen) == 2
    assert seen[0]["prior_green"] is None, "the first attempt had no verdict to carry"
    token = seen[1]["prior_green"]
    assert token, "NOT THREADED: the re-gate was handed no green commit and re-ran everything"
    assert _run(repo, "git", "rev-parse", token + "^{tree}") == seen[0]["tree"], \
        "WRONG TREE: the token does not name the tree the first attempt gated"
    assert _run(repo, "git", "rev-parse", token + "^") == seen[0]["base"], \
        "the green commit must sit on the base it was gated on"
    assert _combined(repo, sha, token) == set(), \
        "a disjoint move must leave nothing for the test selection to re-run"
    assert "prior-green: {}".format(token) in _run(repo, "git", "log", "-1", "--format=%B", sha), \
        "SILENT: the receipt does not name the green tree the re-gate narrowed against"
    assert sl.verify(repo, sha)[0] == 0, "the receipt with a prior-green line must still verify"


def test_a_path_the_lane_rewrote_between_attempts_is_still_selected(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    (repo / "code.py").write_text("VALUE = 2\n")
    seen: list[dict] = []

    def rewrite():
        (repo / "code.py").write_text("VALUE = 3  # rewritten while the gate ran\n")

    monkeypatch.setattr(sl, "run_gate", _racing(repo, lose_until=1, seen=seen, between=rewrite))
    sha = sl.land(repo, ["code.py"], "worktree-sourced retry", attempts=3)

    assert _combined(repo, sha, seen[1]["prior_green"]) == {"code.py"}, \
        "TOO NARROW: bytes no green gate ever saw were deselected"


def test_a_red_verdict_is_never_carried_and_never_retried(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    (repo / "gate_verdict").write_text("red")
    (repo / "code.py").write_text("VALUE = 2\n")
    seen: list[dict] = []
    monkeypatch.setattr(sl, "run_gate", _racing(repo, lose_until=99, seen=seen))
    with pytest.raises(sl.LandingRefused, match="GATE RED"):
        sl.land(repo, ["code.py", "gate_verdict"], "red tree", attempts=5)
    assert len(seen) == 1, "A RED VERDICT CARRIED: a red gate was retried"


def test_run_gate_puts_the_token_where_the_gate_reads_it_and_a_merge_wins(tmp_path: Path):
    (tmp_path / "hook.sh").write_text(
        'echo "TOKEN=${{{}:-unset}}"\n'.format(gate_mod.MERGE_PARENT_ENV))
    rc, out, _ = sl.run_gate(tmp_path, "hook.sh", prior_green="green123")
    assert rc == 0 and "TOKEN=green123" in out, "NOT IN THE ENV: the gate never saw the token"
    rc, out, _ = sl.run_gate(tmp_path, "hook.sh", merge_parent="merge456", prior_green="green123")
    assert "TOKEN=merge456" in out, "a real merge's own parent must keep its say"
    rc, out, _ = sl.run_gate(tmp_path, "hook.sh")
    assert "TOKEN=unset" in out
