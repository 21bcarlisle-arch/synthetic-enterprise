"""The seat's direction commit reaches origin/main while the shared HEAD is behind and diverged.

2026-10-04: two orientations (543dcff6d, 7234966b2) committed onto a shared HEAD that sat behind
and diverged from origin, so their push refused and the record the director reads stood still for
two stretches. Divergence is the shared tree's standing state, so the control builds exactly it:
a real bare origin, a clone holding a commit of its own and missing origin's newest. Only the gate
and the receipt check are stubbed -- the worktree cut, the fast-forward check, the push and the
verification that origin moved are the real ones.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from background import delivery_seat as seat
from tools import promote_worktree_landing as promote_mod
from tools import surgical_land

RECORD = "docs/direction/DIRECTION.yaml"
ROWS = "docs/direction/decisions.jsonl"


def _git(cwd: Path, *args: str) -> str:
    out = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=str(cwd),
                         capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(f"git {args[0]} rc={out.returncode}: {(out.stdout + out.stderr)[-300:]}")
    return out.stdout.strip()


def _commit(repo: Path, rel: str, text: str, msg: str) -> None:
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text(text)
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", msg)


def _push_from(origin: Path, tmp: Path, rel: str, text: str) -> None:
    """Another lane lands on origin."""
    other = tmp / f"other-{len(list(tmp.iterdir()))}"
    _git(tmp, "clone", "-q", str(origin), str(other))
    _commit(other, rel, text, "another lane")
    _git(other, "push", "-q", "origin", "HEAD:main")


@pytest.fixture
def world(tmp_path, monkeypatch):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    shared = tmp_path / "shared"
    seed = tmp_path / "seed"
    _git(tmp_path, "init", "-q", "-b", "main", str(seed))
    _commit(seed, RECORD, "oriented_at: old\n", "seed")
    _commit(seed, ROWS, '{"at": "1"}\n', "row 1")
    _git(seed, "push", "-q", str(origin), "main")
    _git(tmp_path, "clone", "-q", str(origin), str(shared))
    # DIVERGED: a commit of the shared tree's own (the stranded direction commit's shape) ...
    _commit(shared, ROWS, '{"at": "1"}\n{"at": "2"}\n', "stranded direction commit")
    # ... and origin has moved past it.
    _push_from(origin, tmp_path, "elsewhere.txt", "origin moved\n")
    _git(shared, "fetch", "-q")
    # The orientation that just ran writes the working copy.
    (shared / RECORD).write_text("oriented_at: new\n")
    (shared / ROWS).write_text('{"at": "1"}\n{"at": "2"}\n{"at": "3"}\n')

    monkeypatch.setattr(seat, "PROJECT_DIR", shared)
    monkeypatch.setattr(seat, "DIRECTION_WORKTREE", tmp_path / "seat-worktree")
    monkeypatch.setattr(seat.direction_mod, "WRITE_SCOPE", (RECORD, ROWS))
    monkeypatch.setattr(seat, "SEAT_WRITTEN", ())
    # The gate and the receipt are the two things a synthetic repo cannot carry. The lander makes an
    # ordinary commit of exactly the bytes it was handed, in the root it was handed.
    monkeypatch.setattr(promote_mod, "_refuse_if_ungated", lambda *a, **k: None)
    calls = []

    def duplicated(*_a, **_k):
        if world_state.get("duplicate"):
            raise promote_mod.PromotionRefused("another live claim holds docs/direction/")
        return []

    monkeypatch.setattr(promote_mod, "_refuse_if_duplicated", duplicated)

    def lander(root, paths, message, attempts, content):
        """Commits `content` by plumbing and leaves the working copy alone, as the real door does."""
        root = Path(root)
        calls.append(root)
        if world_state.get("move_origin_once"):
            world_state["move_origin_once"] = False
            _push_from(origin, tmp_path, "raced.txt", "landed during the gate\n")
        if world_state.get("red"):
            raise surgical_land.LandingRefused("GATE RED: a test failed")
        for rel, data in content.items():
            blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=str(root),
                                  input=data, capture_output=True, check=True).stdout.decode().strip()
            _git(root, "update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}")
        tree = _git(root, "write-tree")
        sha = _git(root, "commit-tree", tree, "-p", "HEAD", "-m", message)
        _git(root, "update-ref", "HEAD", sha)
        return sha

    world_state: dict = {}
    monkeypatch.setattr(surgical_land, "land", lander)
    shared_head = _git(shared, "rev-parse", "HEAD")
    return {"origin": origin, "shared": shared, "calls": calls, "state": world_state,
            "shared_head": shared_head}


def _on_origin(origin: Path, rel: str) -> str:
    return _git(origin, "show", f"main:{rel}")


def test_the_seats_commit_REACHES_ORIGIN_from_a_behind_and_diverged_shared_tree(world):
    """MUTATION (must fire): make `land_direction_on_origin` land into `root` (the shared HEAD)
    instead of the cut worktree -- the push from there is not a fast-forward and origin never
    receives the record, which is the 10-03 defect verbatim."""
    ok, detail = seat.commit_direction()

    assert ok is True, detail
    assert _on_origin(world["origin"], RECORD) == "oriented_at: new"
    assert _on_origin(world["origin"], ROWS).count('"at"') == 3
    # Origin's own move is kept, and the shared HEAD is not touched at all.
    assert _on_origin(world["origin"], "elsewhere.txt") == "origin moved"
    assert _git(world["shared"], "rev-parse", "HEAD") == world["shared_head"]
    assert world["calls"] == [seat.DIRECTION_WORKTREE]
    # The next orientation with nothing new reads it as already landed, not as a fresh landing.
    assert seat.commit_direction() == (True, "nothing changed in the write scope")


def test_every_landing_outcome_is_REACHABLE_and_only_an_origin_move_is_retried(world):
    """THE PARTITION in one control: lands first time, lands after origin moved under the gate,
    refused on a red gate, refused at promotion with origin still, refused for an append-only
    rewrite. A route that retried everything,
    or nothing, or refused everything passes some legs alone.

    MUTATIONS (must fire): drop the loop (the raced leg is refused); loop on any refusal (the red
    or the held leg calls the lander twice); drop the prefix check (the rewrite leg lands)."""
    state, calls = world["state"], world["calls"]

    state["move_origin_once"] = True
    raced = seat.commit_direction()
    raced_calls = len(calls)
    assert raced[0] is True, raced[1]
    assert _on_origin(world["origin"], "raced.txt") == "landed during the gate"
    assert raced_calls == 2

    (world["shared"] / RECORD).write_text("oriented_at: newer\n")
    state["red"] = True
    red = seat.commit_direction()
    assert red[0] is False and "GATE RED" in red[1]
    assert len(calls) == raced_calls + 1

    state["red"] = False
    state["duplicate"] = True
    held = seat.commit_direction()
    assert held[0] is False and "another live claim" in held[1]
    assert len(calls) == raced_calls + 2

    state["duplicate"] = False
    (world["shared"] / ROWS).write_text('{"at": "rewritten"}\n')
    rewrite = seat.commit_direction()
    assert rewrite[0] is False and "not a prefix" in rewrite[1]
    assert len(calls) == raced_calls + 2
    assert _on_origin(world["origin"], ROWS).count('"at"') == 3


def test_the_startup_anchor_page_lands_with_every_record(world, monkeypatch):
    """Defect it names: the page an advisor orients from was refreshed only by the weekly publish, so
    it was a week stale and missed the operating model's anchor (director, 2026-10-04). The seat lands
    it beside the record every orientation; a page that could not be regenerated never costs the
    record."""
    monkeypatch.setattr(seat, "regenerate_startup_anchors", lambda wt: b"# Startup anchors\n")
    ok, detail = seat.commit_direction()
    assert ok is True, detail
    assert _on_origin(world["origin"], seat.STARTUP_ANCHORS_PAGE) == "# Startup anchors"
    assert _on_origin(world["origin"], RECORD) == "oriented_at: new"


def test_a_page_that_cannot_be_regenerated_never_costs_the_record(world, monkeypatch):
    monkeypatch.setattr(seat, "regenerate_startup_anchors", lambda wt: None)
    ok, detail = seat.commit_direction()
    assert ok is True, detail
    assert _on_origin(world["origin"], RECORD) == "oriented_at: new"
    assert subprocess.run(["git", "show", f"main:{seat.STARTUP_ANCHORS_PAGE}"],
                          cwd=str(world["origin"]), capture_output=True).returncode != 0


def test_the_page_is_the_worktrees_own_tool_output_and_only_when_it_changed(tmp_path):
    """Generated by the landing worktree's own copy of the tool, from that tree; an absent tool or a
    run that changed nothing yields None, so an unchanged page is never re-landed."""
    assert seat.regenerate_startup_anchors(tmp_path) is None
    tool = tmp_path / "tools" / "startup_anchor_freshness.py"
    tool.parent.mkdir(parents=True)
    tool.write_text("from pathlib import Path\n"
                    "p = Path('docs/status/STARTUP_ANCHORS.md'); p.parent.mkdir(parents=True, exist_ok=True)\n"
                    "p.write_text('fresh\\n')\n")
    assert seat.regenerate_startup_anchors(tmp_path) == b"fresh\n"
    assert seat.regenerate_startup_anchors(tmp_path) is None
