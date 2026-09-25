"""The defect: `refresh_to_head` graded a copy `refreshable` -- "origin/main strictly supersedes
it" -- while that copy was the only place in the tree binding two keys of a PUBLICATION WHITELIST.

Found by running the door against real bytes for the first time on 2026-09-24. Over the shared
tree's 430 dirty paths it produced exactly ONE affirmative grade, `saas/reporting/annual_report.py`,
and that grade was wrong: the copy adds `svt_departures` and `svt_decisions` to the dict
`extract_report_data` returns, `origin/main` carries `svt_departures` nowhere in `saas/`, and seven
`tools/` modules already consume `svt_decisions` -- `covers_svt_route: false` is live on the site
precisely because the producer does not emit it.

WHY EVERY READING ABOVE AGREED, which is the part worth controlling rather than the instance. A
string key inside a function body is not a module binding, not a class member and not an import, so
`symbols()` returns the same set for both sides, `gains_over` returns `()`, and empty is the door's
licence to overwrite. Rule 1b cannot see it either -- the lines are code, not a comment block -- and
the clock agreed with the destructive reading, so nothing downstream was going to catch it.

Each test here names a way the new refusal could be useless. The anti-tautology arm is the one that
matters: a guard that withdraws `refreshable` from EVERY copy passes the positive leg and destroys
the door, and this module's whole value is the one grade that still fires.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import refresh_to_head as rth
from tools import stale_copy_refusal as scr


def _run(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True, check=True)


_ALPHA = "def alpha():\n    return 1\n"

#: WHAT THE BASE LANDED: a helper with a line found nowhere else, plus the whitelist itself.
W_LANDED = (
    "def alpha():\n    return 1\n\n\n"
    "def freshly_landed_helper(argument):\n"
    '    """A distinctive line that appears exactly once in this file."""\n'
    "    return argument * 41 + 7\n\n\n"
    "def extract():\n"
    '    return {"landed_key": 1}\n'
)

#: THE DEFECT'S SHAPE. It drops the landed helper -- so it supplies no SYMBOL and the stale-copy
#: control complains, which together is what `refreshable` means here -- and it binds a whitelist
#: key that exists in no commit. Before this guard it graded `refreshable` and the key was the work.
RIVAL_ADDS_A_KEY = (
    "def alpha():\n"
    '    """an alternative wording of exactly the same behaviour"""\n'
    "    return 1\n\n\n"
    "def extract():\n"
    '    return {"landed_key": 1, "key_bound_in_no_commit": 2}\n'
)

#: THE SAME COPY WITHOUT THE KEY, and the reason it is here is the anti-tautology arm below. It is
#: byte-for-byte the shape above but for the one key, so a guard that refuses it too is refusing on
#: something other than the key -- and the test says so by asserting the permissive grade, not by
#: looking for a word the positive case happens to use.
RIVAL_ADDS_NO_KEY = (
    "def alpha():\n"
    '    """an alternative wording of exactly the same behaviour"""\n'
    "    return 1\n\n\n"
    "def extract():\n"
    '    return {"landed_key": 1}\n'
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo. The subject is git trees and blobs; a fake would be more permissive than
    its subject, which is how a fail-open goes green."""
    root = tmp_path / "r"
    root.mkdir()
    _run(root, "init", "-q", "-b", "main")
    _run(root, "config", "user.email", "t@t")
    _run(root, "config", "user.name", "t")
    (root / "w.py").write_text(_ALPHA)
    _run(root, "add", "w.py")
    _run(root, "commit", "-qm", "base")
    (root / "w.py").write_text(W_LANDED)
    _run(root, "add", "w.py")
    _run(root, "commit", "-qm", "lane B lands a helper and the whitelist")
    return root


def test_the_copy_that_adds_only_a_whitelist_key_is_no_longer_graded_refreshable(
    repo: Path,
) -> None:
    """THE DEFECT ITSELF. Before the guard this answered `refreshable` and `--write` would have
    overwritten the only bytes in the tree binding that key."""
    (repo / "w.py").write_text(RIVAL_ADDS_A_KEY)
    verdict = rth.judge_copy(repo, "w.py")
    assert verdict.state == rth.WHITELIST_GAIN, verdict.reason
    assert verdict.refused


def test_a_copy_adding_no_key_is_still_refreshable_so_the_guard_has_not_shut_the_door(
    repo: Path,
) -> None:
    """THE ANTI-TAUTOLOGY ARM, and the only leg here that fails an unconditional refusal.

    `RIVAL_ADDS_NO_KEY` differs from the positive fixture by exactly one dict key. A guard keyed to
    anything else -- the `extract` name, the presence of a dict at all, the dropped helper --
    refuses this too, passes the leg above, and leaves the tool answering REFUSED to every shape it
    was built to repair. The assertion is the PERMISSIVE grade for that reason: it cannot be
    satisfied by a refusal however well-worded."""
    (repo / "w.py").write_text(RIVAL_ADDS_NO_KEY)
    verdict = rth.judge_copy(repo, "w.py")
    assert verdict.state == rth.REFRESHABLE, verdict.reason


def test_the_reason_names_the_key_because_a_refusal_that_does_not_cannot_be_argued_with(
    repo: Path,
) -> None:
    """The operator's next move is to establish which side is the later draft, and they cannot
    start without knowing which key is in dispute."""
    (repo / "w.py").write_text(RIVAL_ADDS_A_KEY)
    assert "key_bound_in_no_commit" in rth.judge_copy(repo, "w.py").reason


def test_the_symbol_reader_is_blind_to_the_key_which_is_why_every_reading_above_agreed() -> None:
    """THE CAUSE, NOT THE SYMPTOM. If this ever stops being true the guard is redundant and should
    be deleted rather than kept as a second opinion -- so the claim is pinned where a reader looking
    at the guard will find it."""
    assert scr.gains_over(W_LANDED, RIVAL_ADDS_A_KEY, "w.py") == ()
    assert scr.dict_key_gains(W_LANDED, RIVAL_ADDS_A_KEY, "w.py") == ("key_bound_in_no_commit",)


def test_a_key_the_base_already_binds_is_not_counted_as_a_gain() -> None:
    """The population is a set DIFFERENCE, not a count. A copy that merely moves a key between two
    dicts in the same file has gained nothing, and refusing it would be the false positive that
    makes an operator start ignoring this state."""
    moved = (
        "def extract():\n"
        "    return {}\n\n\n"
        "def extract_elsewhere():\n"
        '    return {"landed_key": 1}\n'
    )
    assert scr.dict_key_gains(W_LANDED, moved, "w.py") == ()


def test_an_unparseable_side_is_unknown_and_not_no_keys() -> None:
    """`None` is not `()`, for this module's usual reason: nothing is established by a side that
    did not parse, and reading it as 'no keys gained' would hand the licence back."""
    assert scr.dict_key_gains(W_LANDED, "def broken(:\n", "w.py") is None


def test_an_unparseable_copy_graded_refreshable_is_refused_rather_than_written(
    repo: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The `None` leg AT THE DOOR, which is the only place it costs bytes. Reached by forcing the
    unknown rather than by finding a file that both parses for the grade above and does not parse
    here -- the two cannot be true of one blob, and a leg that cannot be entered is not a leg."""
    (repo / "w.py").write_text(RIVAL_ADDS_NO_KEY)
    assert rth.judge_copy(repo, "w.py").state == rth.REFRESHABLE  # the branch IS otherwise open
    monkeypatch.setattr(rth, "dict_key_gains", lambda *a, **k: None)
    verdict = rth.judge_copy(repo, "w.py")
    assert verdict.state == rth.WHITELIST_GAIN
    assert "UNKNOWN" in verdict.reason


def test_a_non_python_path_is_not_touched_by_this_population() -> None:
    """The argument for reading dict keys is about Python producers. A JSON document's every leaf
    already has a reader (`_json_leaf_names`), and asking this question of it would be a second
    opinion on a population that is already answered."""
    assert scr.dict_key_gains('{"a": 1}', '{"a": 1, "b": 2}', "feed.json") == ()
