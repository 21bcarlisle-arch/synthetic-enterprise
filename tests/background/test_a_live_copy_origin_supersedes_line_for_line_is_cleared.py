"""A live draft whose every line origin already holds no longer holds the whole fleet behind origin.

THE DEFECT, 2026-10-09. A lane drafted `canon_claims.yaml` and `test_canon_drift_check.py` in the
shared tree, then landed a LATER revision of both from a worktree. The drafts stayed: every line of
each was on origin, but neither equalled any origin revision, `refresh_to_head` reads only Python,
and both were hours old, not 48. No class took them, and the all-or-nothing rule held the fleet 93
commits stale until a tick cleared them by hand (0c7389aa9, preserved at b84ae812e).

THE REPAIR is the ninth class, `superseded_live_verdicts`: a tracked edit with no line origin lacks
(as a multiset), whose every deletion origin also made, is preserved on a ref and restored.

The fixtures reproduce those two copies' shapes: HEAD, then a draft adding one block, then origin
holding that block and more.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path

from background import origin_reconcile as orc

_CANON = "docs/design/canon_claims.yaml"
_DRIFT = "tests/tools/test_canon_drift_check.py"
_LIVE = "docs/institutional/knowledge_map.md"
_DELETED = "docs/design/maturity_map.yaml"

_CANON_HEAD = ("claims:\n  - id: SITE_the_schematic_says_survival_is_not_yet_at_risk\n"
               "    expects: absent\n\n")
_CANON_DRAFT = _CANON_HEAD + ("  - id: SITE_the_company_card_says_survival_is_not_yet_at_risk\n"
                              "    expects: absent\n\n")
_CANON_ORIGIN = _CANON_DRAFT + "  - id: MISSION_advice_has_a_recipient\n    expects: present\n\n"

_DRIFT_HEAD = ('EXPECTED = frozenset({\n    "SITE_the_schematic_says_only_one_trait_expresses",\n'
               '    "SITE_the_schematic_says_survival_is_not_yet_at_risk",\n})\n')
_DRIFT_DRAFT = _DRIFT_HEAD.replace(
    "})\n", '    "SITE_the_company_card_says_survival_is_not_yet_at_risk",\n})\n')
_DRIFT_ORIGIN = _DRIFT_DRAFT.replace("})\n", '    "MISSION_advice_has_a_recipient",\n})\n')

_LIVE_HEAD = "| topic | status |\n| debt | gap |\n"
_LIVE_ORIGIN = _LIVE_HEAD + "| voids | gap |\n"
_LIVE_DRAFT = _LIVE_HEAD + "| retention | a lane's new row |\n"

_DELETED_HEAD = "atoms:\n  - B8: level 2\n  - W2_38: level 1\n"
_DELETED_ORIGIN = _DELETED_HEAD + "  - H9: level 0\n"
_DELETED_DRAFT = "atoms:\n  - B8: level 2\n"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True,
                          text=True).stdout


def _write(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)


def _repo(tmp_path: Path) -> Path:
    """A bare origin, the shared tree cloned at HEAD, and origin moved on to its later revisions."""
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", str(origin), str(seed))
    for repo in (seed,):
        _git(repo, "config", "user.email", "t@t")
        _git(repo, "config", "user.name", "t")
    _write(seed, {_CANON: _CANON_HEAD, _DRIFT: _DRIFT_HEAD, _LIVE: _LIVE_HEAD,
                  _DELETED: _DELETED_HEAD})
    _git(seed, "add", ".")
    _git(seed, "commit", "-m", "seed")
    _git(seed, "push", "origin", "main")
    shared = tmp_path / "shared"
    _git(tmp_path, "clone", str(origin), str(shared))
    _git(shared, "config", "user.email", "t@t")
    _git(shared, "config", "user.name", "t")
    _write(seed, {_CANON: _CANON_ORIGIN, _DRIFT: _DRIFT_ORIGIN, _LIVE: _LIVE_ORIGIN,
                  _DELETED: _DELETED_ORIGIN})
    _git(seed, "commit", "-am", "origin lands the later revisions")
    _git(seed, "push", "origin", "main")
    _git(shared, "fetch", "origin")
    return shared


def _advance(shared: Path) -> dict:
    refuse = lambda _p, paths: {p: (False, "fixture") for p in paths}  # noqa: E731
    return orc.advance_shared_tree(
        shared, earlier_fn=lambda _p, _b: {}, stale_fn=refuse, generated_fn=refuse,
        orphans_fn=refuse, abandoned_fn=refuse, append_fn=refuse, locker=contextlib.nullcontext)


def test_the_superseded_partition_takes_the_two_drafts_and_refuses_live_work(tmp_path):
    shared = _repo(tmp_path)
    _write(shared, {_CANON: _CANON_DRAFT, _DRIFT: _DRIFT_DRAFT, _LIVE: _LIVE_DRAFT,
                    _DELETED: _DELETED_DRAFT})

    verdicts = orc.superseded_live_verdicts(shared, [_CANON, _DRIFT, _LIVE, _DELETED])

    taken = {p for p, (ok, _) in verdicts.items() if ok}
    refused = {p for p, (ok, _) in verdicts.items() if not ok}
    # The control over the whole partition first: a guard that refuses everything fails here.
    assert taken and refused, verdicts
    assert taken == {_CANON, _DRIFT}, verdicts
    assert "not on origin" in verdicts[_LIVE][1]
    assert "deleted" in verdicts[_DELETED][1]


def test_two_superseded_drafts_are_preserved_restored_and_the_tree_advances(tmp_path):
    shared = _repo(tmp_path)
    _write(shared, {_CANON: _CANON_DRAFT, _DRIFT: _DRIFT_DRAFT})

    result = _advance(shared)

    assert result["advanced"], result["reason"]
    assert _git(shared, "rev-parse", "HEAD") == _git(shared, "rev-parse", "origin/main")
    assert (shared / _CANON).read_text() == _CANON_ORIGIN
    ref = _git(shared, "for-each-ref", "--format=%(refname)",
               orc.SUPERSEDED_PRESERVED_PREFIX).split()
    assert ref, "no preservation ref was written"
    assert _git(shared, "show", "{}:{}".format(ref[0], _CANON)) == _CANON_DRAFT
    assert _git(shared, "show", "{}:{}".format(ref[0], _DRIFT)) == _DRIFT_DRAFT


def test_one_live_edit_beside_them_still_refuses_and_touches_nothing(tmp_path):
    shared = _repo(tmp_path)
    _write(shared, {_CANON: _CANON_DRAFT, _DRIFT: _DRIFT_DRAFT, _LIVE: _LIVE_DRAFT})

    result = _advance(shared)

    assert not result["advanced"]
    assert _LIVE in result["reason"] and "not on origin" in result["reason"]
    assert (shared / _CANON).read_text() == _CANON_DRAFT
    assert (shared / _LIVE).read_text() == _LIVE_DRAFT
