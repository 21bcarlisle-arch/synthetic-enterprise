"""A WALL WITH A HOLE IN IT: a conflicting merge had no legal route at all.

Director, 2026-09-02: *"The conflict door needs its design pass, as you say — the next time two
lanes touch one file there's no legal route, and that's a wall with a hole in it."*

The three doors and why each was shut:

  * `surgical_land --merge` — the ONLY sanctioned reconciliation — refused on conflict and offered
    no way to settle one.
  * `git merge` on the shared tree — forbidden, and rightly: that index routinely holds another
    lane's staged work (57 entries the morning this was written), so a merge there commits work
    nobody reviewed.
  * hook-bypass — a wall, never a judgement call.

So a conflicting reconciliation had to be done BY HAND in a worktree. It happened twice in one
morning on one file, each time blocking every landing and the publish path behind it.

`--resolve` closes it. What makes it a RESOLUTION and not a smuggling route is that it may only
touch a path git itself reports as conflicted — without that rule, `--merge --resolve` is a way to
put arbitrary bytes into a commit whose receipt says "merge".
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import surgical_land as sl


def _git(cwd, *args, **kw):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, **kw)


@pytest.fixture
def forked(tmp_path):
    """A repo where two branches changed the SAME line of one file, plus a disjoint file."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "shared.md").write_text("base\n")
    (repo / "untouched.md").write_text("stable\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")

    _git(repo, "checkout", "-q", "-b", "other")
    (repo / "shared.md").write_text("theirs\n")
    (repo / "their_own.md").write_text("only theirs\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "theirs")

    _git(repo, "checkout", "-q", "main")
    (repo / "shared.md").write_text("ours\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "ours")
    return repo


def _heads(repo):
    return (_git(repo, "rev-parse", "main").stdout.strip(),
            _git(repo, "rev-parse", "other").stdout.strip())


# ── the door was shut ───────────────────────────────────────────────────────────────────────
def test_without_a_resolution_a_conflict_still_refuses(forked):
    """Unchanged behaviour, and it must stay: a conflict with nobody choosing is not landable."""
    parent, other = _heads(forked)
    with pytest.raises(sl.LandingRefused) as e:
        sl.build_merge_tree(forked, parent, other)
    assert "MERGE CONFLICT" in str(e.value) and "shared.md" in str(e.value)


def test_the_refusal_now_names_the_way_out(forked):
    """A refusal that names no route is what made this a hole. The message has to carry the door."""
    parent, other = _heads(forked)
    with pytest.raises(sl.LandingRefused) as e:
        sl.build_merge_tree(forked, parent, other)
    assert "--resolve" in str(e.value)


# ── and now it opens, for exactly one thing ─────────────────────────────────────────────────
def test_a_resolved_conflict_produces_a_tree_carrying_the_chosen_bytes(forked):
    """MUTATION: ignore `resolutions` and re-raise, and this fails — the state that had no route.

    The other side's DISJOINT file must still arrive: resolving one path must not quietly drop
    the rest of the merge.
    """
    parent, other = _heads(forked)
    tree = sl.build_merge_tree(forked, parent, other, {"shared.md": b"chosen by a person\n"})
    shown = _git(forked, "show", "{}:shared.md".format(tree)).stdout
    assert shown == "chosen by a person\n"
    assert _git(forked, "show", "{}:their_own.md".format(tree)).stdout == "only theirs\n"
    assert _git(forked, "show", "{}:untouched.md".format(tree)).stdout == "stable\n"


def test_the_resolved_tree_carries_no_conflict_markers(forked):
    """The whole hazard of a partial or careless resolution: git's markers committed as content,
    in a file that then passed a gate."""
    parent, other = _heads(forked)
    tree = sl.build_merge_tree(forked, parent, other, {"shared.md": b"chosen\n"})
    blob = _git(forked, "show", "{}:shared.md".format(tree)).stdout
    assert "<<<<<<<" not in blob and ">>>>>>>" not in blob and "=======" not in blob


# ── THE LOAD-BEARING RULE ───────────────────────────────────────────────────────────────────
def test_a_resolution_may_NOT_touch_a_path_that_did_not_conflict(forked):
    """THE RULE THAT MAKES THIS A RESOLUTION AND NOT A SMUGGLING ROUTE.

    Without it, `--merge --resolve` puts arbitrary bytes into a commit whose receipt says "merge"
    and whose scope a reader would take to be "whatever the other history changed".

    MUTATION: drop the `stray` check and this fails — and `untouched.md`, which neither side
    edited, silently changes inside a merge commit.
    """
    parent, other = _heads(forked)
    with pytest.raises(sl.LandingRefused) as e:
        sl.build_merge_tree(forked, parent, other,
                            {"shared.md": b"ok\n", "untouched.md": b"smuggled\n"})
    assert "did NOT conflict" in str(e.value) and "untouched.md" in str(e.value)


def test_every_conflicted_path_must_be_settled(forked):
    """A partial resolution commits git's markers for the paths nobody chose."""
    (forked / "second.md").write_text("base2\n")
    _git(forked, "add", "-A")
    _git(forked, "commit", "-qm", "add second")
    _git(forked, "checkout", "-q", "other")
    (forked / "second.md").write_text("theirs2\n")
    _git(forked, "add", "-A")
    _git(forked, "commit", "-qm", "theirs2")
    _git(forked, "checkout", "-q", "main")
    (forked / "second.md").write_text("ours2\n")
    _git(forked, "add", "-A")
    _git(forked, "commit", "-qm", "ours2")

    parent, other = _heads(forked)
    with pytest.raises(sl.LandingRefused) as e:
        sl.build_merge_tree(forked, parent, other, {"shared.md": b"ok\n"})
    assert "unresolved" in str(e.value) and "second.md" in str(e.value)


def test_a_resolution_with_nothing_to_resolve_is_refused(forked):
    """"Resolving" a clean merge is a content change wearing a merge's receipt."""
    _git(forked, "checkout", "-q", "-b", "clean", "main")
    (forked / "shared.md").write_text("ours\n")
    _git(forked, "checkout", "-q", "main")
    parent = _git(forked, "rev-parse", "main").stdout.strip()
    _git(forked, "checkout", "-q", "-b", "disjoint", parent)
    (forked / "elsewhere.md").write_text("theirs only\n")
    _git(forked, "add", "-A")
    _git(forked, "commit", "-qm", "disjoint")
    disjoint = _git(forked, "rev-parse", "disjoint").stdout.strip()
    _git(forked, "checkout", "-q", "main")

    with pytest.raises(sl.LandingRefused) as e:
        sl.build_merge_tree(forked, parent, disjoint, {"shared.md": b"x\n"})
    assert "NO conflict" in str(e.value)


# ── the receipt records that a person chose ─────────────────────────────────────────────────
def test_the_receipt_names_the_resolved_paths():
    """A merge whose tree is neither parent's at some path must SAY so, or a later reader finds a
    difference that looks like a third lane. It is also what `--verify` can check the claim of."""
    receipt = sl.build_receipt("p" * 40, "t" * 40, ["shared.md"], 0, "n=1",
                               merge_parent="m" * 40, resolved=["shared.md"])
    assert "conflicts-resolved: shared.md" in receipt
    assert sl.parse_receipt(receipt)["conflicts_resolved"] == ["shared.md"]


def test_a_clean_merge_says_nothing_about_resolutions():
    """Absence has to mean absence: a `conflicts-resolved` line on every merge would train a
    reader to skip it."""
    receipt = sl.build_receipt("p" * 40, "t" * 40, ["a.md"], 0, "n=1", merge_parent="m" * 40)
    assert "conflicts-resolved" not in receipt
    assert "conflicts_resolved" not in sl.parse_receipt(receipt)


# ── and the things it must not become ───────────────────────────────────────────────────────
def test_resolve_outside_a_merge_is_refused():
    """Outside a merge there is no conflict to settle, and the bytes would be an unnamed content
    change — precisely the scope lie the pathspec discipline exists to prevent."""
    import inspect
    src = inspect.getsource(sl._land_once)
    assert "--resolve is only meaningful with --merge" in src


def test_the_resolution_bytes_must_come_from_OUTSIDE_the_repo():
    """Same rule as `--content`, same reason: a resolution read from the working tree brings back
    the swap-and-restore hazard where a landing that never happened leaves a tree indistinguishable
    from one that did (the 2026-08-19 R3 finding).

    MUTATION: drop the `relative_to(ROOT)` refusal in `main` and this fails.
    """
    import inspect
    src = inspect.getsource(sl.main)
    assert "is INSIDE the repository" in src


def test_the_gate_still_runs_on_a_resolved_merge():
    """Resolving a conflict makes a tree expressible. It buys no exemption from anything: the
    resulting tree goes through `materialise` + `run_gate` exactly as before."""
    import inspect
    src = inspect.getsource(sl._land_once)
    after_merge = src.split("build_merge_tree", 1)[1]
    assert "result_tree" in after_merge
    # the gate call is downstream of BOTH tree-building branches, not inside either
    assert "run_gate" not in src.split("elif resolutions:", 1)[0].split("build_merge_tree", 1)[1]


def test_the_conflict_count_is_paths_and_not_gits_commentary(forked):
    """A PRE-EXISTING DEFECT THIS MADE LOAD-BEARING. `merge-tree --name-only` prints the paths,
    then a BLANK LINE, then commentary (`Auto-merging x`, `CONFLICT (content): ...`). The refusal
    took everything after the tree sha, so a ONE-file conflict was reported as **"4 conflicted
    path(s)"** with `Auto-merging ...` listed as a filename — observed live on 2026-09-02.

    Harmless while it was only prose. Fatal once a resolution has to be MATCHED against the set:
    a caller settling the one real path would be told two commentary lines were still unresolved.

    MUTATION: parse `out[1:]` without stopping at the blank line and this fails.
    """
    parent, other = _heads(forked)
    with pytest.raises(sl.LandingRefused) as e:
        sl.build_merge_tree(forked, parent, other)
    assert "1 conflicted path(s)" in str(e.value)
    assert "Auto-merging" not in str(e.value)


def test_the_parser_stops_at_the_blank_line():
    raw = ["treesha", "a.md", "b.md", "", "Auto-merging a.md", "CONFLICT (content): x"]
    assert sl._conflicted_paths(raw) == ["a.md", "b.md"]
