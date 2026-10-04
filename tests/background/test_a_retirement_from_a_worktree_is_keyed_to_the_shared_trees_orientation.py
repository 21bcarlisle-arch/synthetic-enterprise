"""A `--release` run from an isolated worktree must stamp the orientation the executor compares.

THE DEFECT (2026-09-29). `delivery_lane.current_orientation()` read `direction.DIRECTION_PATH`,
which is this checkout's own copy. In an executor worktree that copy is HEAD's, and the orienting
seat's live record sits staged and uncommitted in the shared tree. So the retirement was stamped
11:21:09Z, the executor's guard compared it with 17:22:34Z, and the guard never fired. The next
promotion's `hand_off` then deleted the retired entry. `a-long-job-that-dies-is-shown-dead-in-the-
brief` landed as 8c8fd2e8e, was released, and was drawn twice more.

Mutation: revert `current_orientation` to `read_direction(path)`. The worktree leg then reads the
worktree's stamp and reds.
"""
from __future__ import annotations

from pathlib import Path

from background import delivery_lane, seat_continuation

REAL = Path(__file__).resolve().parents[2] / "docs" / "direction" / "DIRECTION.yaml"
SHARED_STAMP = "2026-09-29T17:22:34.403195+00:00"
WORKTREE_STAMP = "2026-09-29T11:21:09.297754+00:00"


def _direction(tree: Path, stamp: str) -> None:
    lines = REAL.read_text(encoding="utf-8").splitlines()
    lines = [f'oriented_at: "{stamp}"' if ln.startswith("oriented_at:") else ln for ln in lines]
    target = tree / "docs" / "direction" / "DIRECTION.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _trees(tmp_path: Path) -> tuple[Path, Path]:
    main = tmp_path / "main"
    (main / ".git" / "worktrees" / "seat").mkdir(parents=True)
    (main / "docs" / "observability").mkdir(parents=True)
    _direction(main, SHARED_STAMP)
    worktree = tmp_path / "seat"
    worktree.mkdir()
    (worktree / ".git").write_text(f"gitdir: {main / '.git' / 'worktrees' / 'seat'}\n")
    _direction(worktree, WORKTREE_STAMP)
    return main, worktree


def _run_in(monkeypatch, tree: Path) -> None:
    """Be a process started in `tree`: its own `DIRECTION_PATH` and its own `PROJECT_DIR`."""
    monkeypatch.setattr(seat_continuation, "PROJECT_DIR", tree)
    monkeypatch.setattr(delivery_lane.direction_mod, "DIRECTION_PATH",
                        tree / "docs" / "direction" / "DIRECTION.yaml")


def test_the_fixture_is_readable_so_the_worktree_leg_is_not_green_on_two_nones(tmp_path, monkeypatch):
    main, worktree = _trees(tmp_path)
    monkeypatch.setattr(seat_continuation, "PROJECT_DIR", main)
    assert delivery_lane.current_orientation() == SHARED_STAMP
    assert delivery_lane.current_orientation(worktree / "docs" / "direction" / "DIRECTION.yaml") \
        == WORKTREE_STAMP


def test_a_worktree_reads_the_shared_trees_orientation_not_its_own_copy(tmp_path, monkeypatch):
    main, worktree = _trees(tmp_path)
    monkeypatch.setattr(seat_continuation, "PROJECT_DIR", worktree)
    assert delivery_lane.orientation_path() == main / "docs" / "direction" / "DIRECTION.yaml"
    assert delivery_lane.current_orientation() == SHARED_STAMP


def test_a_release_from_the_worktree_blocks_the_executors_re_promotion(tmp_path, monkeypatch):
    main, worktree = _trees(tmp_path)
    store = tmp_path / "continuations.json"
    monkeypatch.setattr(seat_continuation, "STORE", store)
    row = {"id": "a-finished-focus-row", "what": "done already", "why": "it landed"}
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda *a, **k: [dict(row)])
    _run_in(monkeypatch, main)
    delivery_lane.hand_off_focus(row["id"], "landed")          # the executor promotes
    _run_in(monkeypatch, worktree)
    assert seat_continuation.retire(row["id"], orientation=delivery_lane.current_orientation(),
                                    path=store)                # the tick releases from its worktree
    _run_in(monkeypatch, main)
    try:
        delivery_lane.hand_off_focus(row["id"], "landed")      # the executor's next stand-down
    except ValueError as refusal:
        assert "RETIRED" in str(refusal)
    else:
        raise AssertionError("a finished row was re-promoted under the orientation it finished in")


def test_a_shared_record_this_checkouts_schema_refuses_still_names_its_orientation(tmp_path, monkeypatch):
    """2026-10-04: the shared record failed origin's `validate` (an older `for_the_director` row), so
    every worktree release stamped None and a landed focus row was redrawn three times.

    Mutation: drop the raw-stamp fallback in `current_orientation`. The first assertion reds.
    The control below it keeps the fallback from answering for a file it cannot parse at all."""
    main, worktree = _trees(tmp_path)
    shared = main / "docs" / "direction" / "DIRECTION.yaml"
    # Drop the WHOLE `for_the_director` block, not only its key line: with a concern on the list the
    # block spans indented rows, and leaving them would test a malformed file rather than an old row.
    lines, in_block = [], False
    for ln in shared.read_text(encoding="utf-8").splitlines():
        if ln.startswith("for_the_director:"):
            in_block = True
            continue
        if in_block and (ln.startswith((" ", "-")) or not ln.strip()):
            continue
        in_block = False
        lines.append(ln)
    shared.write_text("\n".join(lines) + "\nfor_the_director:\n  - what: a row the schema refuses\n",
                      encoding="utf-8")
    assert delivery_lane.direction_mod.read_direction(shared) is None   # the schema does refuse it
    monkeypatch.setattr(seat_continuation, "PROJECT_DIR", worktree)
    assert delivery_lane.current_orientation() == SHARED_STAMP
    shared.write_text("oriented_at: [unclosed\n", encoding="utf-8")
    assert delivery_lane.current_orientation() is None
