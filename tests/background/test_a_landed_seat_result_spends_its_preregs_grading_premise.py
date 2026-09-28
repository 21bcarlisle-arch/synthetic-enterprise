"""A landed SEAT_RESULT spends the grading premise of the SEAT_PREREG an item names.

THE INSTANCE (2026-09-28). `grade-the-balance-rule-two-state-diff-against-the-cefd2c04a-baseline`
was written 22:48 naming `SEAT_PREREG_THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_CLOSE_RULE_
2026-09-27.md`; `7dc8f150d` landed `SEAT_RESULT_THE_TWO_STATE_DIFF_RERUN_..._2026-09-28.md` at
03:57; the draw handed the finished grading to a worker tick at 04:27. The prereg is the file that
does not change when the work is done, so nothing that read the item's paths could see it.

MUTATIONS (each must fire):
  (a) `_result_landed` returns False always -> the spent item is handed out;
  (b) `_result_landed` returns True always -> the unresulted item is withheld (the partition leg);
  (c) drop the `written_at` comparison -> the context-citation case is withheld;
  (d) drop the `prereg_result` branch from `_disposition` -> the live row reads not_done;
  (e) drop the `done["at"] <= drawn` guard -> a result landing INSIDE the window reads as spent.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
import yaml

from background import delivery_lane as dl
from background import direction as d
from background import seat_continuation as sc

NOW = datetime(2026, 9, 28, 3, 27, tzinfo=timezone.utc)
NOW_EPOCH = NOW.timestamp()

STEM = "THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_CLOSE_RULE"
PREREG = f"docs/staging/records/SEAT_PREREG_{STEM}_2026-09-27.md"
RESULT = f"docs/staging/records/SEAT_RESULT_{STEM}_2026-09-28.md"
RESULT_SHA = "7dc8f150dd7a9fa2c27d4268bab40ecd233847af"
RESULT_AT = 1790564222.0      # 7dc8f150d's own %ct, 2026-09-28 03:57 BST
WRITTEN_AT = 1790545703.4     # the continuation's written_at, 2026-09-27 22:48 BST
DRAWN_AT = 1790566020.7       # the 04:27 draw

UNRESULTED = "docs/staging/records/SEAT_PREREG_THE_C1_BRACKET_THREE_RUNS_AT_ONE_COMMIT_2026-09-28.md"


@pytest.fixture()
def git(monkeypatch):
    """Origin holds a result at STEM and none at the C1 bracket's stem. Every other git question
    is answered by the real git, so the draw's other readers run as they do in production."""
    real = dl._git

    def fake(*args, cwd=None):
        if args[:1] == ("log",) and args[-1].startswith("docs/staging/*SEAT_RESULT_"):
            return f"{RESULT_SHA} {RESULT_AT:.0f}\n" if f"SEAT_RESULT_{STEM}_" in args[-1] else ""
        if args[:2] == ("show", "--name-only") and args[-1] == RESULT_SHA:
            return RESULT + "\n"
        return real(*args, cwd=cwd)

    monkeypatch.setattr(dl, "_git", fake)


@pytest.fixture()
def tree(tmp_path, monkeypatch, git):
    direction_path = tmp_path / "DIRECTION.yaml"
    map_path = tmp_path / "maturity_map.yaml"
    map_path.write_text(yaml.safe_dump([{"id": "EP1_real_atom", "level_current": 1}]),
                        encoding="utf-8")
    monkeypatch.setattr(dl, "MATURITY_MAP", map_path)
    monkeypatch.setattr(d, "DIRECTION_PATH", direction_path)
    monkeypatch.setattr(sc, "STORE", tmp_path / ".seat_continuation.json")

    def _write(focus):
        direction_path.write_text(yaml.safe_dump({
            "version": 1, "oriented_at": NOW.isoformat(), "focus": focus,
            "not_now": [{"what": "something", "why": "it loses to the above"}]}), encoding="utf-8")

    return {"write": _write, "claims": tmp_path / "claims.json"}


def test_BOTH_BRANCHES_the_spent_prereg_is_skipped_and_the_unresulted_one_is_still_handed_out(tree):
    """One control over the whole partition: the head is skipped AND the tail is handed out, so a
    `_result_landed` that withheld everything fails here as surely as one that withheld nothing."""
    tree["write"]([
        {"id": "grade-the-two-state-diff", "what": f"grade it against {PREREG}", "why": "b1-b5"},
        {"id": "run-the-c1-bracket", "what": f"run the three runs in {UNRESULTED}", "why": "c1"},
    ])

    item = dl.next_item(now=NOW_EPOCH, path=tree["claims"])

    assert item is not None and item["id"] == "run-the-c1-bracket"


def test_prereg_result_names_the_commit_that_first_put_the_result_on_origin(git):
    done = dl.prereg_result(f"grade it against {PREREG}", WRITTEN_AT)

    assert done is not None
    assert done["commit"] == RESULT_SHA and done["path"] == RESULT and done["prereg"] == STEM
    assert dl.prereg_result(f"run {UNRESULTED}", WRITTEN_AT) is None


def test_a_result_OLDER_than_the_item_is_context_and_does_not_spend_it(git):
    """An item written after the result landed was written with it in view."""
    assert dl.prereg_result(f"repair what {PREREG} refuted", RESULT_AT + 3600) is None


def test_the_live_row_reads_PREMISE_SPENT_with_the_results_commit(git):
    row = {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT, "source": "continuation",
           "source_written_at": WRITTEN_AT,
           "named_paths": [PREREG, "simulation/arrears_engine.py"]}

    got = dl._disposition(row, DRAWN_AT, focus_id="grade-the-two-state-diff")

    assert got["disposition"] == dl.PREMISE_SPENT
    assert got["evidence"].startswith(RESULT_SHA[:9])


def test_a_result_landing_INSIDE_the_window_is_the_windows_work_not_a_spent_premise(git):
    row = {"first_drawn_at": RESULT_AT - 60, "last_drawn_at": RESULT_AT - 60,
           "source_written_at": WRITTEN_AT, "named_paths": [PREREG]}

    got = dl._disposition(row, RESULT_AT - 60, focus_id="grade-the-two-state-diff")

    assert got["disposition"] != dl.PREMISE_SPENT
