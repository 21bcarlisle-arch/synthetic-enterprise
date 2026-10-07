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
    calls, gates, merges = [], [], []

    def duplicated(*_a, **_k):
        if world_state.get("duplicate"):
            raise promote_mod.PromotionRefused("another live claim holds docs/direction/")
        return []

    monkeypatch.setattr(promote_mod, "_refuse_if_duplicated", duplicated)

    def lander(root, paths, message, attempts, content=None, merge=None):
        """Commits `content` by plumbing and leaves the working copy alone, as the real door does.
        With `merge`, merges that ref into HEAD and refuses on conflict, as the door's `--merge`."""
        root = Path(root)
        calls.append(root)
        (merges if merge else gates).append(root)
        if world_state.get("move_origin_once"):
            world_state["move_origin_once"] = False
            _push_from(origin, tmp_path, "raced.txt", "landed during the gate\n")
        if world_state.get("move_origin_times"):
            world_state["move_origin_times"] -= 1
            _push_from(origin, tmp_path, f"raced-{len(calls)}.txt", "landed during the gate\n")
        if world_state.get("edit_record_once"):
            world_state["edit_record_once"] = False
            _push_from(origin, tmp_path, RECORD, "oriented_at: someone else\n")
        if world_state.get("red") or (merge and world_state.get("red_merge")):
            raise surgical_land.LandingRefused("GATE RED: a test failed")
        if merge:
            done = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "merge",
                                   "-q", "--no-ff", "-m", message, merge], cwd=str(root),
                                  capture_output=True, text=True)
            if done.returncode:
                subprocess.run(["git", "merge", "--abort"], cwd=str(root), capture_output=True)
                raise surgical_land.LandingRefused(f"the merge of {merge} conflicts")
            return _git(root, "rev-parse", "HEAD")
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
    # The real deadline is what is left of the unit's budget since the PROCESS started, which in a
    # long pytest run is nothing. Generous here; the deadline leg below drives its own clock.
    monkeypatch.setattr(seat, "direction_land_deadline_s", lambda now=None: 3600.0)
    shared_head = _git(shared, "rev-parse", "HEAD")
    return {"origin": origin, "shared": shared, "calls": calls, "state": world_state,
            "shared_head": shared_head, "gates": gates, "merges": merges}


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
    assert rewrite[0] is False and "not kept whole" in rewrite[1]
    assert len(calls) == raced_calls + 2
    assert _on_origin(world["origin"], ROWS).count('"at"') == 3


def test_a_stretch_entry_PREPENDED_under_the_header_lands_and_a_dropped_one_is_refused(
        world, monkeypatch):
    """Defect it names: the append-only rule asked that origin's copy be a PREFIX of the tree's,
    and `tools/stretch_log.append` prepends under the header, so every orientation that wrote an
    entry was refused (02:30Z and 08:25Z, 2026-10-04) and the delivery feed never reached origin.

    MUTATIONS (must fire): restore `startswith` (the prepended leg is refused); make
    `keeps_all_of` always true (the dropped leg lands and deletes origin's entry)."""
    log = "docs/status/SEAT_STRETCH_LOG.md"
    header = "# Stretch log\n\n---\n"
    _push_from(world["origin"], world["origin"].parent, log, header + "\n## old entry\n\n---\n")
    _git(world["shared"], "fetch", "-q")
    monkeypatch.setattr(seat.direction_mod, "WRITE_SCOPE", (RECORD, ROWS, log))
    (world["shared"] / log).parent.mkdir(parents=True, exist_ok=True)

    (world["shared"] / log).write_text(header + "\n## new entry\n\n---\n\n## old entry\n\n---\n")
    ok, detail = seat.commit_direction()
    assert ok is True, detail
    on_origin = _on_origin(world["origin"], log)
    assert "## new entry" in on_origin and "## old entry" in on_origin

    (world["shared"] / RECORD).write_text("oriented_at: newest\n")
    (world["shared"] / log).write_text(header + "\n## newest entry\n\n---\n")
    dropped = seat.commit_direction()
    assert dropped[0] is False and "not kept whole" in dropped[1]
    assert "## old entry" in _on_origin(world["origin"], log)


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


def test_origin_moving_TWICE_under_the_gate_still_lands_and_only_the_deadline_or_another_writer_stops_it(
        world, monkeypatch):
    """Defect it names: on 2026-10-07 origin moved twice in 50 minutes, the second attempt lost too,
    and the seat gave up -- origin's record, the one the director reads, three hours stale.

    THE PARTITION: lands after two moves; refused once the deadline has passed, after exactly one
    more attempt than none; refused by name when origin's DIRECTION.yaml itself changed, rather than
    overwritten. MUTATIONS (must fire): restore a two-attempt give-up (the twice leg is refused);
    drop the deadline check (the deadline leg loops on a moving origin); drop the base check (the
    other-writer leg overwrites their record)."""
    state, calls, origin = world["state"], world["calls"], world["origin"]

    state["move_origin_times"] = 2
    twice = seat.commit_direction()
    assert twice[0] is True, twice[1]
    assert len(calls) == 3
    assert _on_origin(origin, RECORD) == "oriented_at: new"
    assert _on_origin(origin, "raced-1.txt") == _on_origin(origin, "raced-2.txt")

    (world["shared"] / RECORD).write_text("oriented_at: newer\n")
    ticks = iter([0.0, 100.0, 200.0, 300.0])
    monkeypatch.setattr(seat, "direction_land_deadline_s", lambda now=None: 150.0)
    monkeypatch.setattr(seat, "_monotonic", lambda: next(ticks))
    state["move_origin_times"] = 99
    expired = seat.commit_direction()
    assert expired[0] is False and "inside 150s" in expired[1], expired[1]
    assert len(calls) == 3 + 2
    assert _on_origin(origin, RECORD) == "oriented_at: new"

    monkeypatch.setattr(seat, "direction_land_deadline_s", lambda now=None: 3600.0)
    monkeypatch.setattr(seat, "_monotonic", lambda: 0.0)
    state["move_origin_times"] = 0
    state["edit_record_once"] = True
    other = seat.commit_direction()
    assert other[0] is False and "another writer edited it" in other[1], other[1]
    assert _on_origin(origin, RECORD) == "oriented_at: someone else"


def test_origin_moving_under_the_gate_costs_a_MERGE_not_a_second_full_gate_and_a_real_refusal_holds(
        world):
    """Defect it names: the 17:22Z record of 2026-10-07 lost all 3 attempts in 2637 s, because a
    lost race re-cut the landing and re-ran the full ~880 s gate while origin gained 2-4 commits an
    hour. When origin's new commits do not touch the record's paths, the gated commit stands and
    origin is merged into it through the door.

    THE PARTITION: a disjoint move lands on one full gate and one merge; another writer's edit to
    the record under the gate is refused by name with no merge tried; a red merge gate is refused
    and not retried. MUTATIONS (must fire): `_origin_touched` always names the landing (the
    disjoint leg spends a second full gate); `_origin_touched` names nothing (the edit leg merges
    and is refused for a conflict, not by name); retry a refused merge (the red leg merges twice)."""
    state, gates, merges, origin = world["state"], world["gates"], world["merges"], world["origin"]

    state["move_origin_once"] = True
    raced = seat.commit_direction()
    assert raced[0] is True, raced[1]
    assert (len(gates), len(merges)) == (1, 1)
    assert _on_origin(origin, RECORD) == "oriented_at: new"
    assert _on_origin(origin, "raced.txt") == "landed during the gate"

    (world["shared"] / RECORD).write_text("oriented_at: newer\n")
    state["edit_record_once"] = True
    other = seat.commit_direction()
    assert other[0] is False and "another writer edited it" in other[1], other[1]
    assert (len(gates), len(merges)) == (2, 1)
    assert _on_origin(origin, RECORD) == "oriented_at: someone else"

    (world["shared"] / ROWS).write_text(_on_origin(origin, ROWS) + '\n{"at": "4"}\n')
    state["move_origin_times"] = 1
    state["red_merge"] = True
    red = seat.commit_direction()
    assert red[0] is False and "GATE RED" in red[1], red[1]
    assert (len(gates), len(merges)) == (3, 2)


def test_a_refused_landing_is_RECORDED_as_refused_and_PAGED(tmp_path, monkeypatch):
    """Defect it names: the orientation row is appended as `oriented` before the landing, and a
    refused landing left it reading `oriented` with nobody told. MUTATIONS (must fire): skip the
    appended row (the last row reads `oriented`); skip the page (nothing is sent)."""
    rows = tmp_path / "decisions.jsonl"
    monkeypatch.setattr(seat.direction_mod, "DECISIONS_PATH", rows)
    pages = []
    monkeypatch.setattr(seat, "_notify", lambda msg, topic_class: pages.append((msg, topic_class)))
    row = {"at": "2026-10-07T09:20:00+00:00", "outcome": "oriented", "focus": ["x"],
           "for_the_director": [{"id": "c1"}]}
    seat.direction_mod.append_decision(row)

    seat.record_landing_refused(row, "landing refused (DirectionNotLanded): origin moved")

    last = seat.direction_mod.read_decisions(limit=1)[0]
    assert last["outcome"] == "refused" and "origin moved" in last["landing_refused"]
    assert last["at"] == row["at"] and last["focus"] == ["x"]
    assert len(pages) == 1 and "did NOT reach origin" in pages[0][0]
    # The copy carries the oriented row's concerns, so they are not re-paged next stretch.
    assert seat._previous_concern_ids() == ["c1"]


def test_the_deadline_is_the_units_budget_less_one_gate_run(tmp_path, monkeypatch):
    unit = tmp_path / "delivery-seat.service"
    unit.write_text("[Service]\nTimeoutStartSec=3000\n")
    assert seat.direction_unit_budget_s(unit) == 3000.0
    assert seat.direction_unit_budget_s(tmp_path / "absent") == seat.DIRECTION_UNIT_FALLBACK_BUDGET_S
    monkeypatch.setattr(seat, "DIRECTION_UNIT", unit)
    start = seat._PROCESS_STARTED
    assert seat.direction_land_deadline_s(start + 1000) == 3000 - 1000 - seat.DIRECTION_GATE_RUN_S
    assert seat.direction_land_deadline_s(start + 2000) == 0.0
