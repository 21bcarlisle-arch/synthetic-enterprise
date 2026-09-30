"""A landing is a commit on origin/main, and both lane-0 instruments must ask origin, not HEAD.

The defect (direction `the-ledger-and-path-check-read-origin`, 2026-09-30): `_window_hits` ran
`git log --all`, so a commit on any local ref -- a HEAD that may yet be reset, a salvage branch --
credited a claim, and `_path_verdict` graded `already landed` as "identical to HEAD", so a shared
tree 13 commits behind origin read a copy the trunk had moved past as a spent ask.

One synthetic repo holds both legs at once: a binding commit that exists on origin/main and not on
HEAD, and a binding commit that exists on HEAD and not on origin/main. The first must be credited
and the second must not -- the second leg is what proves the refusing branch can be taken.

MUTATION RECORD (2026-09-30). `PUBLISHED_REF` in `_window_hits`'s `git log` replaced by `--all`:
`test_a_binding_commit_only_on_head_is_not_credited` and the named-refusal leg red (`--all` answers
happily in a repo with no origin). `_path_verdict`'s origin blob reads replaced by `HEAD`: `test_a_copy_equal_to_a_stale_head_is_not_already_landed` and
`test_a_copy_equal_to_origin_is_already_landed_while_head_is_behind` red. Removing the
`_published_ref_or_raise` call in `_window_hits`: the named-refusal leg reds (a generic
`GitUnavailable` is raised instead).
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest

from background import delivery_lane as dl

ITEM = "an-item-whose-landing-is-asked-of-origin"
SUBJECT = "pkg/subject.py"


def _run(root: Path, *args: str) -> str:
    return subprocess.run(("git",) + args, cwd=root, check=True, capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch) -> dict:
    """base -> (origin/main: `published` binds ITEM) and (HEAD: `local` binds ITEM), diverged."""
    root = tmp_path / "r"
    (root / "pkg").mkdir(parents=True)
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / SUBJECT).write_text("A = 1\n")
    _run(root, "add", "-A")
    _run(root, "commit", "-qm", "base")
    base = _run(root, "rev-parse", "HEAD")

    (root / SUBJECT).write_text("A = 2\n")
    _run(root, "commit", "-qam", "{}: published landing".format(ITEM))
    published = _run(root, "rev-parse", "HEAD")
    _run(root, "update-ref", dl.PUBLISHED_REF, published)

    _run(root, "reset", "-q", "--hard", base)
    (root / SUBJECT).write_text("A = 3\n")
    _run(root, "commit", "-qam", "{}: local-only commit".format(ITEM))
    local = _run(root, "rev-parse", "HEAD")

    monkeypatch.setattr(dl, "PROJECT_DIR", root)
    monkeypatch.setattr(dl, "_claim_subject_paths", lambda _f, _r: [SUBJECT])
    monkeypatch.setattr(dl, "_liveness_surface_or_raise", lambda: frozenset({"site/x.json"}))
    return {"root": root, "published": published, "local": local, "base": base}


def _hit_shas(drawn: float) -> set[str]:
    _paths, hits, _live = dl._window_hits(ITEM, {}, drawn, until=time.time() + 60)
    return {h[0] for h in hits}


def test_a_binding_commit_on_origin_and_not_head_is_credited(repo) -> None:
    got = _hit_shas(time.time() - 3600)
    assert repo["published"] in got, got


def test_a_binding_commit_only_on_head_is_not_credited(repo) -> None:
    """THE RARE BRANCH, asserted reachable: the same repo, the same window, one commit refused."""
    got = _hit_shas(time.time() - 3600)
    assert repo["published"] in got and repo["local"] not in got, got


def test_no_origin_main_is_a_named_refusal_not_a_fallback_to_head(repo) -> None:
    _run(repo["root"], "update-ref", "-d", dl.PUBLISHED_REF)
    with pytest.raises(dl.NoPublishedRef, match="no origin/main"):
        dl._window_hits(ITEM, {}, time.time() - 3600, until=time.time() + 60)


def test_a_copy_equal_to_a_stale_head_is_not_already_landed(repo) -> None:
    tag, detail = dl._path_verdict(repo["root"], SUBJECT)
    assert tag == "behind origin", (tag, detail)


def test_a_copy_equal_to_origin_is_already_landed_while_head_is_behind(repo) -> None:
    (repo["root"] / SUBJECT).write_text("A = 2\n")
    tag, detail = dl._path_verdict(repo["root"], SUBJECT)
    assert tag == "already landed" and "origin/main" in detail, (tag, detail)


def test_the_path_verdict_names_a_missing_origin_rather_than_grading_against_head(repo) -> None:
    _run(repo["root"], "update-ref", "-d", dl.PUBLISHED_REF)
    tag, detail = dl._path_verdict(repo["root"], SUBJECT)
    assert tag == "ungraded" and "no origin/main" in detail, (tag, detail)
