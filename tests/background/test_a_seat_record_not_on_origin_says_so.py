"""The seat's record reaches origin or the next brief says so; its concerns are origin's too.

2026-10-09 17:44Z: 167d583a4 was gated green in the seat's worktree, lost the race to 63f429536,
and the merge that should have settled it went red. It never reached origin, and the next brief
named it nowhere. Separately, the brief read the director's open concerns from the shared working
copy, which lags origin: a row only origin held was omitted, and a verbatim carry deletes it.

Real git throughout -- a bare origin, a clone, a linked worktree -- because both defects are about
which copy git holds, and a stub of git would agree with whatever the code assumed.

MUTATIONS (each must fire):
  (a) `seat_commit_not_on_origin` returns None unconditionally -> `..._NAMES_A_COMMIT_ORIGIN_LACKS`.
  (b) drop the `subject.startswith("delivery seat:")` clause -> `..._A_FRESH_CUT_IS_NOT_STRANDED`.
  (c) `page_a_stranded_record` ignores `already_told` -> `..._PAGES_ONCE`.
  (d) drop the stranded clause from `is_material` -> `..._MAKES_THE_STRETCH_MATERIAL`.
  (e) `open_rows_on_either` returns `open_rows(here)` -> `..._ORIGINS_OPEN_ROW_IS_IN_THE_BRIEF`
      and `..._A_RECORD_DROPPING_ORIGINS_ROW_IS_REFUSED`.
  (f) drop the `closed` exclusion -> `..._A_ROW_EITHER_SIDE_RESOLVED_IS_NOT_OPEN`.
  (g) `orient` carries from the working copy alone -> `..._DROPPING_ORIGINS_ROW_IS_REFUSED`.
  (h) drop the `page_a_stranded_record` call from `orient`, or (i) page on `--dry-run` too
      -> `..._ORIENT_PAGES_A_STRANDED_RECORD`.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from background import delivery_seat as seat
from background import direction as d
from background import director_concerns as dc

RECORD = "docs/direction/DIRECTION.yaml"


def _git(cwd: Path, *args: str) -> str:
    out = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=str(cwd),
                         capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(f"git {args[0]} rc={out.returncode}: {(out.stdout + out.stderr)[-300:]}")
    return out.stdout.strip()


def _commit(repo: Path, rel: str, text: str, msg: str) -> str:
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text(text)
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repos(tmp_path, monkeypatch):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    shared = tmp_path / "shared"
    _git(tmp_path, "clone", "-q", str(origin), str(shared))
    _commit(shared, RECORD, "version: 1\n", "seed")
    _git(shared, "push", "-q", "origin", "HEAD:main")
    _git(shared, "fetch", "-q")
    worktree = tmp_path / "seat-worktree"
    _git(shared, "worktree", "add", "-q", "--detach", str(worktree), "origin/main")
    monkeypatch.setattr(seat, "PROJECT_DIR", shared)
    monkeypatch.setattr(seat, "DIRECTION_WORKTREE", worktree)
    return origin, shared, worktree


# ── leg 2: a seat commit origin does not hold ────────────────────────────────


def test_THE_CHECK_NAMES_A_COMMIT_ORIGIN_LACKS_and_clears_once_origin_holds_it(repos):
    """Both branches over one worktree, the rare one first: a gated, unpushed seat commit is
    named with its sha; pushed, the same commit is not."""
    _origin, shared, worktree = repos
    sha = _commit(worktree, RECORD, "version: 1\noriented_at: new\n",
                  "delivery seat: direction for the next stretch")
    stranded = seat.seat_commit_not_on_origin()
    assert stranded is not None, "the not-landed branch must be reachable"
    assert stranded["sha"] == sha and "not an ancestor of origin/main" in stranded["says"]

    _git(worktree, "push", "-q", "origin", "HEAD:main")
    _git(shared, "fetch", "-q")
    assert seat.seat_commit_not_on_origin() is None, "a landed record was reported stranded"


def test_A_FRESH_CUT_IS_NOT_STRANDED_even_when_origin_has_moved_past_nothing(repos, tmp_path):
    """A worktree cut at origin sits on another lane's commit: not the seat's, never named. And
    a worktree that does not exist yet (the seat's first landing) is not a stranded record."""
    _origin, shared, worktree = repos
    _commit(worktree, "elsewhere.txt", "x\n", "another lane's unpushed commit")
    assert seat.seat_commit_not_on_origin() is None
    assert seat.seat_commit_not_on_origin(tmp_path / "never-cut") is None


def test_A_STRANDED_RECORD_PAGES_ONCE_and_not_when_the_refusal_already_paged(monkeypatch):
    pages = []
    monkeypatch.setattr(seat, "_notify", lambda msg, **k: pages.append((msg, k)))
    stranded = {"sha": "167d583a478c5b7c", "says": "not an ancestor of origin/main"}

    seat.page_a_stranded_record(stranded)
    assert len(pages) == 1 and "167d583a4" in pages[0][0], "the silent case must page"
    assert pages[0][1]["transition_key"] == "delivery-seat:record-not-on-origin"
    assert pages[0][1]["state"] == stranded["sha"], "keyed to the sha, so one commit pages once"

    pages.clear()
    seat.page_a_stranded_record(stranded, already_told=True)
    seat.page_a_stranded_record(None)
    assert pages == [], "a refusal record_landing_refused already paged buzzed him twice"


def test_A_STRANDED_RECORD_MAKES_THE_STRETCH_MATERIAL():
    """A quiet stretch would otherwise skip the one orientation that can land a fresh record."""
    quiet = {"substantive_count": 0, "levels_moved": {}, "director_inputs": [],
             "findings": {"available": True, "blocking": []}, "live_direction_age_hours": 1.0}
    assert seat.is_material(quiet)[0] is False, "the control needs a stretch that would skip"
    material, why = seat.is_material(dict(quiet, seat_commit_not_on_origin={
        "sha": "167d583a4" + "0" * 31, "says": "not an ancestor of origin/main"}))
    assert material and "167d583a4" in why and "never reached origin" in why


def test_THE_BRIEF_CARRIES_IT_ahead_of_the_commit_list(monkeypatch):
    """Read through the real `build_brief`, so a key wired to nothing cannot pass. The nested
    level-zero control pass is the one input skipped, as its sibling test does."""
    monkeypatch.setattr("tools.level_zero_contradicted_by_its_own_controls.assess",
                        lambda *a, **k: ([], []))
    marker = {"sha": "f" * 40, "says": "not an ancestor of origin/main"}
    monkeypatch.setattr(seat, "seat_commit_not_on_origin", lambda: marker)
    brief = seat.build_brief(datetime.now(timezone.utc))
    assert brief["seat_commit_not_on_origin"] is marker
    keys = list(brief)
    assert keys.index("seat_commit_not_on_origin") < keys.index("commits"), keys


# ── leg 3: the director's open rows are origin's and the working copy's ──────


def _row(rid: str, status: str = "open") -> dict:
    row = {"id": rid, "kind": "canon_intent", "what": f"what {rid}",
           "proposal": f"investigate: {rid}", "status": status, "resolution": ""}
    if status != "open":
        row["resolution"] = "answered by the director"
    return row


def _record(rows: list[dict]) -> str:
    return yaml.safe_dump({"version": 1, "for_the_director": rows}, sort_keys=False)


def test_ORIGINS_OPEN_ROW_IS_IN_THE_BRIEF_when_the_working_copy_lags(repos, monkeypatch):
    _origin, shared, _wt = repos
    other = shared.parent / "other"
    _git(shared.parent, "clone", "-q", str(repos[0]), str(other))
    _commit(other, RECORD, _record([_row("both"), _row("origin-only")]), "another lane")
    _git(other, "push", "-q", "origin", "HEAD:main")
    _git(shared, "fetch", "-q")
    (shared / RECORD).write_text(_record([_row("both"), _row("here-only")]))
    monkeypatch.setattr(d, "DIRECTION_PATH", shared / RECORD)

    origin_raw = dc.read_origin_raw(shared)
    assert [r["id"] for r in dc.open_rows(origin_raw)] == ["both", "origin-only"]
    ids = [r["id"] for r in dc.open_rows_on_either(dc.read_raw(), origin_raw)]
    assert ids == ["both", "here-only", "origin-only"], ids


def test_A_ROW_EITHER_SIDE_RESOLVED_IS_NOT_OPEN():
    here = {"for_the_director": [_row("answered-on-origin"), _row("answered-here", "answered")]}
    origin = {"for_the_director": [_row("answered-on-origin", "answered"), _row("answered-here")]}
    assert dc.open_rows_on_either(here, origin) == []
    assert [r["id"] for r in dc.open_rows_on_either(here, None)] == ["answered-on-origin"], (
        "with no origin copy the working copy's open rows must still stand")


def test_A_RECORD_DROPPING_ORIGINS_ROW_IS_REFUSED_through_orient(repos, monkeypatch, tmp_path):
    """Through `orient()`: the session carries every row the working copy holds verbatim, and
    drops the one only origin holds. That record is refused, naming the row; carrying both lands."""
    from background import tick_mode
    from tools import generate_delivery_page

    _origin, shared, _wt = repos
    other = shared.parent / "other"
    _git(shared.parent, "clone", "-q", str(repos[0]), str(other))
    _commit(other, RECORD, _record([_row("origin-only")]), "another lane raised a concern")
    _git(other, "push", "-q", "origin", "HEAD:main")
    _git(shared, "fetch", "-q")
    (shared / RECORD).write_text(_record([]))
    monkeypatch.setattr(d, "DIRECTION_PATH", shared / RECORD)
    monkeypatch.setattr(d, "DECISIONS_PATH", tmp_path / "decisions.jsonl")
    monkeypatch.setattr(d, "WRONG_TRIAGE_PATH", tmp_path / "wrong_triage.yaml")

    brief = {"since": "2026-10-09T00:00:00+00:00", "commit_count": 1, "substantive_count": 1,
             "previous_focus_drawn": None}
    written = {}
    monkeypatch.setattr(seat, "build_brief", lambda now: brief)
    monkeypatch.setattr(seat, "is_material", lambda b: (True, "one commit"))
    monkeypatch.setattr(seat, "map_levels", lambda: {})
    monkeypatch.setattr(tick_mode, "gate", lambda route: (True, "normal", ""))
    monkeypatch.setattr(tick_mode, "note_spawn", lambda route: None)
    monkeypatch.setattr(seat, "run_session", lambda b: ((shared / RECORD).write_text(
        yaml.safe_dump(written, sort_keys=False)), (True, "ran"))[1])
    monkeypatch.setattr(seat, "write_stretch_entry", lambda row: True)
    monkeypatch.setattr(generate_delivery_page, "generate", lambda: None)
    monkeypatch.setattr(seat, "commit_direction", lambda: (True, "stubbed"))
    monkeypatch.setattr(seat, "out_of_scope_writes", lambda: [])
    monkeypatch.setattr(seat.direction_path_check, "concerns", lambda raw: [])
    monkeypatch.setattr(seat, "_log", lambda m: None)
    monkeypatch.setattr(seat, "_notify", lambda msg, **k: None)

    base = {"version": 1, "oriented_at": datetime.now(timezone.utc).isoformat(),
            "thesis_read": "reading", "focus": [{"id": "atom-a", "why": "because"}],
            "not_now": [{"what": "x", "why": "y"}], "wrong": []}
    written.update(base, for_the_director=[])
    row = seat.orient()
    assert row["outcome"] == "refused", row
    assert any("'origin-only'" in p for p in row["problems"]), row["problems"]

    written.update(base, for_the_director=[_row("origin-only")])
    row = seat.orient()
    assert row["outcome"] == "oriented", "the carrying branch must stay reachable"


def test_ORIENT_PAGES_A_STRANDED_RECORD_even_on_a_stretch_it_then_skips(monkeypatch, tmp_path):
    """The wiring, through `orient()`: the page is asked before the material check, so a quiet
    stretch still says so; `--dry-run` pages nothing; a refusal already paged is not re-paged."""
    monkeypatch.setattr(d, "DECISIONS_PATH", tmp_path / "decisions.jsonl")
    stranded = {"sha": "e" * 40, "says": "not an ancestor of origin/main"}
    monkeypatch.setattr(seat, "build_brief", lambda now: {
        "since": "2026-10-09T00:00:00+00:00", "commit_count": 0, "substantive_count": 0,
        "previous_focus_drawn": None, "seat_commit_not_on_origin": stranded})
    monkeypatch.setattr(seat, "is_material", lambda b: (False, "quiet"))
    monkeypatch.setattr(seat, "map_levels", lambda: {})
    monkeypatch.setattr(seat, "write_stretch_entry", lambda row: True)
    monkeypatch.setattr(seat, "_log", lambda m: None)
    pages = []
    monkeypatch.setattr(seat, "_notify", lambda msg, **k: pages.append(msg))

    seat.orient(dry_run=True)
    assert pages == [], "a dry run paged him"
    seat.orient()
    assert len(pages) == 1 and "eeeeeeeee" in pages[0]

    pages.clear()
    d.append_decision({"at": "x", "outcome": "refused", "landing_refused": "GATE RED"})
    seat.orient()
    assert pages == []
