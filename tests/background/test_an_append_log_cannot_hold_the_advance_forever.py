"""The test log every run appends to held the shared tree's whole fast-forward, and could never age out.

THE DEFECT, measured 2026-10-09. `docs/observability/test_execution_log.jsonl` is appended to by
every pytest session in the shared tree (2,727 lines there against HEAD's 266). Origin had left it
alone since July until d29dcddc3 (10-08) swept one line in, so the fast-forward now writes it. It is
never a twin, the generated oracles exclude appends on purpose, and every run makes it new, so the
48 h abandoned class never takes it. Under the all-or-nothing rule that one path held the advance
for good, and the daemons kept running code 71 commits old.

THE REPAIR is an eighth class: a DECLARED append log is put on a ref, restored to HEAD for the
fast-forward, then rewritten as origin's lines plus every local line origin lacks.

  * `test_an_append_log_is_merged_and_the_advance_succeeds` -- real git end to end: the advance
    happens, origin's new line is in the file, and so is every local line.
  * `test_the_append_class_partition_is_reachable_both_ways` -- the declared log is taken, an
    undeclared tracked edit beside it is not, so the guard neither refuses nor accepts everything.
  * `test_a_refused_advance_puts_the_local_bytes_back_verbatim` -- the log was restored to HEAD
    before the fast-forward; if git still refuses, the local tail must not stay lost.
  * `test_the_merge_keeps_repeated_lines` -- two runs can write the same line; a set would fold
    them and shrink the sum `tools/test_execution_metric` reads.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

from background import origin_reconcile as orc

_LOG = "docs/observability/test_execution_log.jsonl"
_AUTHORED = "background/some_lane_work.py"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True).stdout


def _repo(tmp_path: Path) -> tuple[Path, Path]:
    """A bare origin, a clone of it (the shared tree), and a second clone that advances origin."""
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", str(origin), str(seed))
    _git(seed, "config", "user.email", "t@t")
    _git(seed, "config", "user.name", "t")
    (seed / _LOG).parent.mkdir(parents=True)
    (seed / _LOG).write_text('{"n": 1}\n{"n": 2}\n')
    (seed / _AUTHORED).parent.mkdir(parents=True)
    (seed / _AUTHORED).write_text("x = 1\n")
    _git(seed, "add", ".")
    _git(seed, "commit", "-m", "seed")
    _git(seed, "push", "origin", "main")
    shared = tmp_path / "shared"
    _git(tmp_path, "clone", str(origin), str(shared))
    _git(shared, "config", "user.email", "t@t")
    _git(shared, "config", "user.name", "t")
    # Origin moves on: one line appended to the log, as d29dcddc3 did.
    (seed / _LOG).write_text('{"n": 1}\n{"n": 2}\n{"n": "origin"}\n')
    _git(seed, "commit", "-am", "origin appends")
    _git(seed, "push", "origin", "main")
    _git(shared, "fetch", "origin")
    return origin, shared


def _advance(shared: Path, **kw) -> dict:
    defaults = dict(
        earlier_fn=lambda _p, _b: {},
        stale_fn=lambda _p, paths: {p: (False, "fixture") for p in paths},
        generated_fn=lambda _p, paths: {p: (False, "fixture") for p in paths},
        orphans_fn=lambda _p, paths: {p: (False, "fixture") for p in paths},
        abandoned_fn=lambda _p, paths: {p: (False, "fixture") for p in paths},
        locker=contextlib.nullcontext,
    )
    defaults.update(kw)
    return orc.advance_shared_tree(shared, **defaults)


def test_an_append_log_is_merged_and_the_advance_succeeds(tmp_path):
    _origin, shared = _repo(tmp_path)
    local = '{"n": 1}\n{"n": 2}\n{"n": "local-a"}\n{"n": "local-b"}\n'
    (shared / _LOG).write_text(local)

    result = _advance(shared)

    assert result["advanced"], result["reason"]
    assert _git(shared, "rev-parse", "HEAD") == _git(shared, "rev-parse", "origin/main")
    lines = (shared / _LOG).read_text().splitlines()
    assert lines == ['{"n": 1}', '{"n": 2}', '{"n": "origin"}', '{"n": "local-a"}',
                     '{"n": "local-b"}']
    # And the fallback ref really holds the local bytes.
    refs = _git(shared, "for-each-ref", "--format=%(refname)", orc.APPEND_PRESERVED_PREFIX)
    assert refs.strip(), "no preservation ref was written"
    assert _git(shared, "show", "{}:{}".format(refs.split()[0], _LOG)) == local


def test_the_append_class_partition_is_reachable_both_ways(tmp_path):
    _origin, shared = _repo(tmp_path)
    verdicts = orc.append_log_verdicts(shared, [_LOG, _AUTHORED])
    assert verdicts[_LOG][0] and not verdicts[_AUTHORED][0]


def test_an_undeclared_edit_beside_the_log_still_refuses_everything(tmp_path):
    _origin, shared = _repo(tmp_path)
    seed = tmp_path / "seed"
    (seed / _AUTHORED).write_text("x = 2\n")
    _git(seed, "commit", "-am", "origin edits the module")
    _git(seed, "push", "origin", "main")
    _git(shared, "fetch", "origin")
    (shared / _LOG).write_text('{"n": 1}\n{"n": 2}\n{"n": "local"}\n')
    (shared / _AUTHORED).write_text("x = 3  # a lane's work\n")

    result = _advance(shared)

    assert not result["advanced"]
    assert _AUTHORED in result["reason"]
    assert (shared / _LOG).read_text() == '{"n": 1}\n{"n": 2}\n{"n": "local"}\n'
    assert (shared / _AUTHORED).read_text() == "x = 3  # a lane's work\n"


def test_a_refused_advance_puts_the_local_bytes_back_verbatim(tmp_path):
    _origin, shared = _repo(tmp_path)
    local = '{"n": 1}\n{"n": 2}\n{"n": "local"}\n'
    (shared / _LOG).write_text(local)
    refused = subprocess.CompletedProcess(args=["git"], returncode=1, stdout="", stderr="no")

    result = _advance(shared, ff_fn=lambda: refused, ahead_fn=lambda _p: 0)

    assert not result["advanced"]
    assert (shared / _LOG).read_text() == local


def test_the_merge_keeps_repeated_lines():
    assert orc.merge_append_log("a\nb\n", "a\nb\nc\nc\n") == "a\nb\nc\nc\n"
    assert orc.merge_append_log("a\nx\n", "a\na\n") == "a\nx\na\n"
    assert orc.merge_append_log("a\n", "a\n") == "a\n"


def test_a_clearing_failure_after_the_log_was_restored_puts_its_bytes_back(tmp_path):
    """The log sorts before a later blocker; if clearing that one fails, the advance is abandoned
    with the log already at HEAD's bytes, and the local tail must come back on that route too."""
    _origin, shared = _repo(tmp_path)
    local = '{"n": 1}\n{"n": 2}\n{"n": "local"}\n'
    (shared / _LOG).write_text(local)
    later = "site/zz_twin.json"

    def restorer(path):
        return "fixture refusal" if path == later else orc.restore_tracked_twin(shared, path)

    result = _advance(
        shared,
        blockers_fn=lambda p: orc.paths_blocking_fast_forward(p) + [
            {"path": later, "kind": orc.FF_MODIFIED}],
        tracked_twins_fn=lambda _p, _b: [later],
        restorer=restorer,
    )

    assert not result["advanced"] and "fixture refusal" in result["reason"]
    assert (shared / _LOG).read_text() == local
