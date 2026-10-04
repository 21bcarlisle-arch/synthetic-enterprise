"""The reconciler resolves ONE kind of conflict itself: the delivery seat's own records, where origin's
copy provably already holds everything the local side wrote. Every other conflict is still refused.

The defect it names (2026-10-03/04): two direction commits made on the shared HEAD were also carried
to origin another way; the shared tree then conflicted with origin on DIRECTION.yaml, decisions.jsonl
and the stretch log, and `origin_reconcile` refused every five minutes for about seventeen hours
while every daemon ran code up to 156 commits stale. The judgement that resolved it -- origin's copy
loses nothing -- was a fact checked line by line, so it is now checked here per path.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from background import origin_reconcile as orc

DIRECTION, ROWS, LOG = ("docs/direction/DIRECTION.yaml", "docs/direction/decisions.jsonl",
                        "docs/status/SEAT_STRETCH_LOG.md")


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          check=True).stdout.strip()


def _write(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)


def _forked(tmp_path: Path, local: dict[str, str], upstream: dict[str, str]) -> Path:
    """A clone whose HEAD and origin/main fork from one base, each side writing its own files."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", "-q", str(origin), str(seed))
    _git(seed, "config", "user.email", "t@t")
    _git(seed, "config", "user.name", "t")
    _write(seed, {DIRECTION: 'oriented_at: "2026-10-03T10:00:00+00:00"\n', ROWS: '{"at": 1}\n',
                  LOG: "# log\n\nentry one\n"})
    _git(seed, "add", "-A")
    _git(seed, "commit", "-qm", "base")
    _git(seed, "push", "-q")
    work = tmp_path / "work"
    _git(tmp_path, "clone", "-q", str(origin), str(work))
    _git(work, "config", "user.email", "t@t")
    _git(work, "config", "user.name", "t")
    _write(seed, upstream)
    _git(seed, "add", "-A")
    _git(seed, "commit", "-qm", "upstream")
    _git(seed, "push", "-q")
    _write(work, local)
    _git(work, "add", "-A")
    _git(work, "commit", "-qm", "local")
    _git(work, "fetch", "-q")
    return work


CONFLICT = ("[surgical-land] REFUSED: MERGE CONFLICT between aaa and bbb -- 3 conflicted path(s), "
            "nothing was committed:\n  docs/direction/DIRECTION.yaml\n  docs/direction/decisions.jsonl"
            "\n  docs/status/SEAT_STRETCH_LOG.md\nA conflict is two lanes disagreeing about one file")


def test_the_conflicted_paths_are_read_from_the_doors_own_refusal():
    assert orc.conflicted_paths(CONFLICT) == [DIRECTION, ROWS, LOG]
    assert orc.conflicted_paths("no conflict here") == []


def test_origin_holding_every_local_line_and_a_later_record_resolves_to_origins_copy(tmp_path):
    work = _forked(
        tmp_path,
        local={DIRECTION: 'oriented_at: "2026-10-03T20:21:00+00:00"\n',
               ROWS: '{"at": 1}\n{"at": 2}\n', LOG: "# log\n\nentry one\nentry two\n"},
        upstream={DIRECTION: 'oriented_at: "2026-10-03T23:21:00+00:00"\n',
                  ROWS: '{"at": 1}\n{"at": 2}\n{"at": 3}\n',
                  LOG: "# log\n\nentry one\nentry two\nentry three\n"})
    got = orc.mechanical_resolutions(work, CONFLICT)
    assert got is not None and set(got) == {DIRECTION, ROWS, LOG}
    assert got[ROWS] == b'{"at": 1}\n{"at": 2}\n{"at": 3}\n'


def test_a_local_line_origin_lacks_or_a_newer_local_record_keeps_it_a_refusal(tmp_path):
    """The rare branch and the common one, both reachable: one missing line, or a local record newer
    than origin's, and the whole merge stays refused."""
    lost_line = _forked(
        tmp_path / "a",
        local={DIRECTION: 'oriented_at: "2026-10-03T20:21:00+00:00"\n', ROWS: '{"at": 1}\n{"at": "only here"}\n',
               LOG: "# log\n\nentry one\n"},
        upstream={DIRECTION: 'oriented_at: "2026-10-03T23:21:00+00:00"\n', ROWS: '{"at": 1}\n{"at": 3}\n',
                  LOG: "# log\n\nentry one\n"})
    assert orc.mechanical_resolutions(lost_line, CONFLICT) is None
    newer_local = _forked(
        tmp_path / "b",
        local={DIRECTION: 'oriented_at: "2026-10-04T05:00:00+00:00"\n', ROWS: '{"at": 1}\n', LOG: "# log\n\nentry one\n"},
        upstream={DIRECTION: 'oriented_at: "2026-10-03T23:21:00+00:00"\n', ROWS: '{"at": 1}\n', LOG: "# log\n\nentry one\n"})
    assert orc.mechanical_resolutions(newer_local, CONFLICT) is None


def test_a_conflict_on_any_other_path_is_never_resolved(tmp_path, monkeypatch):
    """Even when every path's content WOULD pass, a path outside the seat's records keeps the merge a
    refusal: the scope, not the content check, is what this asserts (the content check is pinned)."""
    monkeypatch.setattr(orc, "origin_already_holds", lambda w, rel, kind: True)
    monkeypatch.setattr(orc, "_show", lambda w, rev, rel: "x\n")
    assert orc.mechanical_resolutions(tmp_path, CONFLICT) is not None   # the scope is the only gate
    other = CONFLICT.replace("  docs/status/SEAT_STRETCH_LOG.md", "  background/delivery_seat.py")
    assert orc.mechanical_resolutions(tmp_path, other) is None


class _Proc:
    def __init__(self, rc: int, out: str = "", err: str = ""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def _reconcile(resolver, merges):
    def runner(_w, resolve=None):
        merges.append(resolve)
        return _Proc(1, CONFLICT) if resolve is None else _Proc(0)
    return orc.reconcile(
        state_fn=lambda _p=None: (156, 2) if not merges or merges[-1] is None else (0, 0),
        runner=runner, pusher=lambda _w: _Proc(0), make_worktree=lambda _p, _w: (True, ""),
        drop_worktree=lambda p, w: None, gate_fn=lambda _p=None: False,
        blockers_fn=lambda _p=None: [], fetcher=lambda _w: _Proc(0), resolver=resolver,
        advance_fn=lambda _p=None: {"advanced": True, "reason": "", "cleared": []})


def test_the_reconciler_re_merges_with_the_resolution_and_names_it_or_refuses_without_one():
    """Through `reconcile`, both legs: with a resolution the merge is re-run carrying it and the
    detail says what was resolved; without one the conflict is the refusal it always was."""
    merges: list = []
    r = _reconcile(lambda w, said: {DIRECTION: b"x"}, merges)
    assert merges == [None, {DIRECTION: b"x"}] and r["status"] == orc.RECONCILED, r
    assert "seat record" in r["detail"]
    merges = []
    r = _reconcile(lambda w, said: None, merges)
    assert merges == [None] and r["status"] == orc.REFUSED_CONFLICT, r
