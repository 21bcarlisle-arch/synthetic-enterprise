"""A landing that loses its promotion race is ONE job with ONE outcome, never a died row per retry.

THE DEFECT (01:14-01:21Z, 2026-11-23). The landing unit promoted once and exited 2 when origin had
moved; the next turn folded origin in with `--merge` as a NEW job, which lost again. Three jobs
registered DIED, and their work reached origin through three merges that authored nothing
(f68028b7f, 755536805, 965a59053). The register reads a non-zero unit exit as DIED, so the property
is keyed on the job's exit: it is 0 exactly when the landing's content is on origin.

Real git throughout (a bare origin, a worktree clone, colleagues pushing mid-race), because every
property here is about what git's refs end up holding.
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import pytest

from background import bounded_landing as bl
from tools import promote_worktree_landing as pwl
from tools import surgical_land as sl

HOOK = textwrap.dedent("""\
    #!/bin/sh
    if [ -f gate_verdict ] && [ "$(cat gate_verdict)" = "red" ]; then echo "1 failed"; exit 1; fi
    echo "3 passed in 0.01s"
    exit 0
    """)
MSG_HOOK = "#!/bin/sh\nexit 0\n"
#: Lines far enough apart that git merges an edit at each end without a conflict.
BASE = "VALUE = 1\n\n\n\n\nOTHER = 1\n"


def _code(value: int, other: int = 1) -> str:
    return BASE.replace("VALUE = 1", f"VALUE = {value}").replace("OTHER = 1", f"OTHER = {other}")


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, f"git {args} failed: {r.stderr}"
    return r.stdout.strip()


def _clone(tmp: Path, origin: Path, name: str) -> Path:
    _git(tmp, "clone", "-q", str(origin), name)
    repo = tmp / name
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "T")
    return repo


@pytest.fixture()
def world(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    (seed / "tools" / "git-hooks").mkdir(parents=True)
    _git(tmp_path, "init", "-q", "-b", "main", str(seed))
    _git(seed, "config", "user.email", "t@example.com")
    _git(seed, "config", "user.name", "T")
    (seed / "tools" / "git-hooks" / "pre-commit").write_text(HOOK)
    (seed / "tools" / "git-hooks" / "commit-msg").write_text(MSG_HOOK)
    (seed / "gate_verdict").write_text("green\n")
    (seed / "code.py").write_text(BASE)
    (seed / "other.txt").write_text("base\n")
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "-m", "base")
    _git(seed, "push", "-q", str(origin), "main")
    wt = _clone(tmp_path, origin, "wt")
    colleague = _clone(tmp_path, origin, "colleague")

    # The promotion's guards that read THIS machine's live stores stay out of a scratch repo; the
    # gated-ness guard is kept, asked in-process against the scratch repo's own receipts.
    def gated(worktree, commit):
        for c in pwl._commits_being_promoted(worktree, commit):
            rc, text = sl.verify(worktree, c)
            if rc != 0:
                raise pwl.PromotionRefused(text)
    monkeypatch.setattr(pwl, "_refuse_if_ungated", gated)
    monkeypatch.setattr(pwl, "_refuse_if_duplicated", lambda *a, **k: [])
    monkeypatch.setattr(pwl, "_bind_to_claim", lambda *a, **k: ([], "bound nothing (test)"))
    monkeypatch.setattr(sl, "announce_landing", lambda *a, **k: None)

    pushes: list[str] = []

    def push(path: str, text: str) -> None:
        _git(colleague, "pull", "-q", "--ff-only", "origin", "main")
        (colleague / path).write_text(text)
        _git(colleague, "commit", "-q", "-am", f"colleague {len(pushes) + 1}")
        _git(colleague, "push", "-q", "origin", "main")
        pushes.append(_git(colleague, "rev-parse", "HEAD"))

    return {"origin": origin, "wt": wt, "push": push, "pushes": pushes}


def _land_mine(wt: Path) -> str:
    (wt / "code.py").write_text(_code(2))
    return sl.land(wt, ["code.py"], "my change: VALUE becomes 2")


def _on_origin(world, value: int = 2) -> bool:
    """THE PROPERTY'S SUBJECT: is the landing's content on origin, by whatever commit."""
    shown = subprocess.run(["git", "show", "main:code.py"], cwd=str(world["origin"]),
                           capture_output=True, text=True)
    return f"VALUE = {value}\n" in shown.stdout


def _push_during_gate(world, monkeypatch, times: int, path: str = "other.txt"):
    real = sl.run_gate
    calls: list[int] = []

    def gate(*a, **k):
        calls.append(1)
        out = real(*a, **k)
        if len(calls) <= times:
            world["push"](path, f"colleague edit {len(calls)}\n")
        return out
    monkeypatch.setattr(sl, "run_gate", gate)
    return calls


def _run(world, attempts=3):
    lines: list[str] = []
    rc = bl.promote_until_landed(world["wt"], "test-claim", attempts=attempts, say=lines.append)
    return rc, "\n".join(lines)


def test_a_promotion_race_lost_twice_ends_as_one_success_with_no_empty_merge(world, monkeypatch):
    """The 01:14Z shape: origin moves before the first promotion and again under the re-gate.
    One call, exit 0, the change on origin as ONE single-parent commit carrying its own subject."""
    _land_mine(world["wt"])
    world["push"]("other.txt", "colleague before promotion\n")
    calls = _push_during_gate(world, monkeypatch, times=1)

    rc, said = _run(world)

    assert rc == 0, said
    assert said.count("lost the promotion race") == 2, said
    assert len(calls) == 2, "each replay is gated: two lost races, two gates"
    assert _on_origin(world)
    origin = world["origin"]
    assert _git(origin, "rev-list", "--merges", "main") == "", "a disjoint move was merged"
    tip = _git(origin, "rev-list", "--parents", "-n", "1", "main").split()
    assert tip[1:] == [world["pushes"][-1]], "the replay is not built on the latest origin"
    assert _git(origin, "log", "-1", "--format=%s", "main") == "my change: VALUE becomes 2"
    assert _git(origin, "show", "main:other.txt") == "colleague edit 1", "the mover was reverted"
    rc_v, text = sl.verify(world["wt"], tip[0])
    assert rc_v == 0, text
    assert "prior-green:" in _git(origin, "log", "-1", "--format=%B", "main")


def test_every_outcome_can_be_reached_and_exit_0_is_exactly_content_on_origin(
        world, monkeypatch, tmp_path):
    """One control over the whole partition: replay, merge, already-there, red, exhausted.
    For each, the job's exit is 0 if and only if the landing's content is on origin."""
    seen = {}

    # merge: the move touched the landing's own path, so only a three-way merge may settle it.
    landed = _land_mine(world["wt"])
    world["push"]("code.py", _code(1, other=9))
    rc, said = _run(world)
    seen["merge"] = (rc, "merging" in said, True)
    assert "not replayable" in said, said
    assert rc == 0 and _git(world["origin"], "rev-list", "--merges", "main") != ""
    assert _git(world["origin"], "rev-parse", "main^2") == landed or _on_origin(world)
    assert _git(world["origin"], "show", "main:code.py") + "\n" == _code(2, other=9)

    # already-there: someone else pushed the identical bytes.
    _git(world["wt"], "pull", "-q", "--ff-only", "origin", "main")
    (world["wt"] / "code.py").write_text(_code(3, other=9))
    sl.land(world["wt"], ["code.py"], "to three")
    world["push"]("code.py", _code(3, other=9))
    rc, said = _run(world)
    seen["already"] = (rc, "ON ORIGIN already" in said, True)
    assert rc == 0, said

    # red: the re-gate fails, so the job ends refused once, and nothing is pushed.
    _git(world["wt"], "fetch", "-q", "origin")
    _git(world["wt"], "reset", "-q", "--hard", "origin/main")
    (world["wt"] / "code.py").write_text(_code(4, other=9))
    # --drops: replacing the line the previous step's colleague added is this test's own choice.
    sl.land(world["wt"], ["code.py"], "to four", drops=frozenset({"code.py"}))
    world["push"]("gate_verdict", "red\n")
    rc, said = _run(world)
    seen["red"] = (rc, "REFUSED" in said and "GATE RED" in said, False)
    assert rc == 2 and said.count("lost the promotion race") == 1, said
    assert not _on_origin(world, 4)

    # exhausted: origin moves under every attempt; the job says so once and exits 2.
    world["push"]("gate_verdict", "green\n")
    _push_during_gate(world, monkeypatch, times=99)
    rc, said = _run(world, attempts=2)
    seen["exhausted"] = (rc, "under all 2 attempt(s)" in said, False)
    assert rc == 2, said

    assert all(reached for _rc, reached, _ in seen.values()), seen
    on_origin = {"merge": True, "already": True, "red": _on_origin(world, 4),
                 "exhausted": _on_origin(world, 4)}
    for name, (rc, _reached, _) in seen.items():
        assert (rc == 0) == on_origin[name], (name, rc)
