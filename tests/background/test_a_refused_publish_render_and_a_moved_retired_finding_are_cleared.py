"""A refused publish's render and a retired finding origin moved to `done/` no longer hold the fleet.

THE DEFECT, 2026-11-12. The shared tree sat 65 commits behind origin on 76 copies no class could
prove lossless. 75 were run 6fe7827ab2's pages, rendered at 16:26Z by a publish whose commit was
refused (17:02Z); origin published the same run from a worktree at 20:31Z (e816040ce). A page
re-rendered later differs by keys, so no line count proves it. The 76th was a root staging finding
origin deleted and re-added under `done/` (63ede2e3b) with every line of the shared copy, and the
ninth class compared it only against origin's entry at the SAME path, which no longer existed.

THE REPAIR is two legs in the ninth class (`_superseded_verdict`): provenance for the render (run
finished, render, refusal, origin's later publish of the same run at this path) and a line-for-line
comparison against the moved copy's new home. Both preserve to a ref, then restore.
"""
from __future__ import annotations

import contextlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from background import origin_reconcile as orc

_PAGE = "site/data/customers/SYN-2016-536.json"
_MARKER = "docs/staging/done/run_complete_20261111T160541Z.md"
_FINDING = "docs/staging/WORKER_FINDING_205_OF_238_2026-11-11.md"
_RETIRED = "docs/staging/done/WORKER_FINDING_205_OF_238_2026-11-11.md"

_MARKER_TEXT = ("# Simulation Run Complete\n\nFinished: 2026-11-11T16:05:41+00:00\nGit: 6fe7827ab2\n\n"
                "## Publish outcome: did not land\n\n<!-- publish-outcome: did-not-land "
                "reason=commit_refused at=2026-11-11T17:02:59.355566+00:00 -->\n")
_FINDING_HEAD = "# 205 of 238\n\nThe refunds pay past the credit.\n"
_FINDING_SHARED = _FINDING_HEAD + "\n## A section the shared tree added\n"
_FINDING_ORIGIN = _FINDING_SHARED + "\n## Retired\n\nThe sections above land here unchanged.\n"


def _git(cwd: Path, *args: str, env: dict | None = None) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True, env={**os.environ, **(env or {})}).stdout


def _write(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)


def _ts(text: str) -> float:
    return datetime.fromisoformat(text).replace(tzinfo=timezone.utc).timestamp()


def _repo(tmp_path: Path, extra_marker: str = "",
          published_at: str = "2026-11-11T20:31:46+00:00") -> Path:
    """HEAD holds the page and the root finding; origin publishes the run and retires the finding."""
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", str(origin), str(seed))
    for repo in (seed,):
        _git(repo, "config", "user.email", "t@t")
        _git(repo, "config", "user.name", "t")
    _write(seed, {_PAGE: '{"render": "head"}\n', _FINDING: _FINDING_HEAD})
    _git(seed, "add", ".")
    _git(seed, "commit", "-m", "seed")
    _git(seed, "push", "origin", "main")
    shared = tmp_path / "shared"
    _git(tmp_path, "clone", str(origin), str(shared))
    _git(shared, "config", "user.email", "t@t")
    _git(shared, "config", "user.name", "t")
    (seed / _RETIRED).parent.mkdir(parents=True, exist_ok=True)
    _git(seed, "mv", _FINDING, _RETIRED)
    _write(seed, {_RETIRED: _FINDING_ORIGIN})
    _git(seed, "commit", "-am", "retire the 205-of-238 finding to done/")
    _write(seed, {_PAGE: '{"render": "published", "ledger": []}\n', _MARKER: _MARKER_TEXT})
    if extra_marker:
        _write(seed, {extra_marker: "# Simulation Run Complete\n"})
    _git(seed, "add", ".")
    _git(seed, "commit", "-m",
         "Auto-process run complete: report + LATEST.md + site/ (git=6fe7827ab2, net=£747,410)",
         env={"GIT_COMMITTER_DATE": published_at})
    _git(seed, "push", "origin", "main")
    _git(shared, "fetch", "origin")
    return shared


def _render(shared: Path, at: str) -> None:
    """The refused publish's own render: different keys from origin's, written at `at` (UTC)."""
    _write(shared, {_PAGE: '{"render": "refused", "ledger": [{"level_dd": 1}]}\n'})
    os.utime(shared / _PAGE, (_ts(at), _ts(at)))


def test_both_legs_can_be_taken_and_each_refuses_live_work(tmp_path):
    shared = _repo(tmp_path)
    _render(shared, "2026-11-11T16:26:32")
    _write(shared, {_FINDING: _FINDING_SHARED})

    verdicts = orc.superseded_live_verdicts(shared, [_PAGE, _FINDING])

    # The control over the whole partition first: a leg that refuses everything fails here.
    assert verdicts[_PAGE][0] and verdicts[_FINDING][0], verdicts
    assert "refused" in verdicts[_PAGE][1]
    assert _RETIRED in verdicts[_FINDING][1]

    # Now each refusal, named. A render written AFTER the run's last refusal is not that render.
    _render(shared, "2026-11-11T18:00:00")
    # A line the moved home does not hold is live work.
    _write(shared, {_FINDING: _FINDING_SHARED + "a line a lane is still writing\n"})
    refused = orc.superseded_live_verdicts(shared, [_PAGE, _FINDING])
    assert not refused[_PAGE][0] and not refused[_FINDING][0], refused
    assert "not on origin" in refused[_FINDING][1]


def test_a_render_after_another_run_finished_is_not_this_runs_render(tmp_path):
    shared = _repo(tmp_path, extra_marker="docs/staging/done/run_complete_20261111T162000Z.md")
    _render(shared, "2026-11-11T16:26:32")

    ok, why = orc.superseded_live_verdicts(shared, [_PAGE])[_PAGE]

    assert not ok, why


def test_the_refused_render_and_the_moved_finding_are_preserved_and_the_tree_advances(tmp_path):
    shared = _repo(tmp_path)
    _render(shared, "2026-11-11T16:26:32")
    _write(shared, {_FINDING: _FINDING_SHARED})
    refuse = lambda _p, paths: {p: (False, "fixture") for p in paths}  # noqa: E731

    result = orc.advance_shared_tree(
        shared, earlier_fn=lambda _p, _b: {}, stale_fn=refuse, generated_fn=refuse,
        orphans_fn=refuse, abandoned_fn=refuse, append_fn=refuse, carried_fn=refuse,
        locker=contextlib.nullcontext)

    assert result["advanced"], result["reason"]
    assert _git(shared, "rev-parse", "HEAD") == _git(shared, "rev-parse", "origin/main")
    assert not (shared / _FINDING).exists()
    ref = _git(shared, "for-each-ref", "--format=%(refname)",
               orc.SUPERSEDED_PRESERVED_PREFIX).split()
    assert ref, "no preservation ref was written"
    assert "level_dd" in _git(shared, "show", "{}:{}".format(ref[0], _PAGE))
    assert _git(shared, "show", "{}:{}".format(ref[0], _FINDING)) == _FINDING_SHARED


def test_a_render_written_after_origin_published_the_run_is_not_one_origin_overtook(tmp_path):
    shared = _repo(tmp_path, published_at="2026-11-11T16:20:00+00:00")
    _render(shared, "2026-11-11T16:26:32")

    ok, why = orc.superseded_live_verdicts(shared, [_PAGE])[_PAGE]

    assert not ok, why
