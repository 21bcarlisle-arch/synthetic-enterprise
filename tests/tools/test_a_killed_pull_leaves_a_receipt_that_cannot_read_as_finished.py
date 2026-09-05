#!/usr/bin/env python3
"""A HadUK pull killed mid-flight must leave a receipt that says so.

THE DEFECT, measured on 2026-09-05. `tools/fetch_haduk_grid.py` wrote its receipt on the
last line of `main()`. The pull is hours long and gets killed routinely -- a bounded
tick's cgroup took the 2026-09-05 run at file 120 of 315. Result: 5.6 GB on disk and a
committed receipt still declaring `tiers: ["normals"], complete: 3, bytes_on_disk:
124079328`. The receipt is the ONLY committed evidence of the pull (the ruling forbids
the grids themselves from entering the repo), so the next reader sees a small, complete,
internally consistent record of a pull that is 5.2 GB short of the disk, and either
re-derives the state by hand or pays for the bytes again.

WHY THE OBVIOUS FIX IS NOT ENOUGH, and what these tests are really keyed to. Writing the
receipt every N files is one line and it introduces a worse failure than the one it
fixes: a summary built from the files done SO FAR has `complete == requested`, which is
the exact signature of a finished pull. A partial receipt that balances is worse than no
receipt, because nothing about it invites a second look. So the run states its whole
manifest, and the files it has not reached carry a `pending` row.

MUTATION, each fires a named test below:
  * `CHECKPOINT_EVERY` never reached / `checkpoint=None`   -> the killed-run test
  * pending rows dropped from `summarise`                  -> the balance test
  * `complete = len(rows) - failed`                        -> the balance test
  * pending allowed to overwrite a held row in the merge   -> the erasure test
  * `cache_walk.reconciles` computed from the rows twice   -> the tautology test
  * season coverage counted by calendar year               -> the straddle test
"""

import json

import pytest

from tools import fetch_haduk_grid as fetch
from tools.fetch_haduk_grid import (
    SERIES_FIRST_YEAR,
    SERIES_LAST_YEAR,
    build_manifest,
    daily_season_coverage,
    finalise_receipt,
    merge_into_receipt,
    summarise,
)

MANIFEST = build_manifest(("daily",))


def _done(entry, status="fetched", size=100):
    return {**entry, "status": status, "bytes": size}


def test_a_pull_killed_part_way_writes_a_receipt_of_what_it_bought():
    """THE DEFECT ITSELF: 120 files on disk, a receipt naming 3.

    Runs `run()` against a fetcher that dies at file 12, the way the cgroup killed the
    real one, and asserts a receipt was written before the death and carries the files.
    """
    written = []

    def dying_fetch(entry, token, *, verify):
        if entry["path"] == MANIFEST[12]["path"]:
            raise KeyboardInterrupt("the tick's cgroup")
        return _done(entry)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(fetch, "fetch_one", dying_fetch)
        patch.setattr(fetch, "_load_credentials", lambda: {"CEDA_TOKEN": "x"})
        patch.setattr(fetch.Token, "value", lambda self: "x")
        with pytest.raises(KeyboardInterrupt):
            fetch.run(
                ("daily",), limit=20, verify=False, checkpoint=written.append
            )

    assert written, "the pull died having written no receipt at all -- the defect"
    last = written[-1]
    assert last["complete"] >= 10, f"only {last['complete']} files recorded"
    assert last["bytes_on_disk"] > 0


def test_a_part_way_receipt_cannot_balance_like_a_finished_one():
    """`complete == requested` must mean finished, at every moment of the pull."""
    part = summarise(("daily",), MANIFEST, [_done(e) for e in MANIFEST[:12]], "minted")

    assert part["requested"] == len(MANIFEST), (
        "the checkpoint shrank the job to the part that is done, so its counts balance"
    )
    assert part["complete"] == 12
    assert part["pending"] == len(MANIFEST) - 12
    assert part["complete"] != part["requested"]
    assert part["pull_status"] == "incomplete"

    whole = summarise(("daily",), MANIFEST, [_done(e) for e in MANIFEST], "minted")
    assert whole["complete"] == whole["requested"] == len(MANIFEST)
    assert whole["pending"] == 0
    assert whole["pull_status"] == "complete"


def test_a_failure_keeps_the_pull_incomplete_even_with_nothing_pending():
    """Pending is not the only way to be unfinished, and `pull_status` is read alone."""
    rows = [_done(e) for e in MANIFEST[:-1]] + [_done(MANIFEST[-1], status="failed")]
    summary = summarise(("daily",), MANIFEST, rows, "minted")

    assert summary["pending"] == 0
    assert summary["pull_status"] == "incomplete"


def test_a_checkpoints_pending_rows_do_not_erase_what_an_earlier_tier_recorded():
    """The merge fix reopened for pending rows.

    Checkpoint one records tas/day/a. Checkpoint two is taken before the run has
    re-reached it, so it offers a `pending` row for the same path. If pending wins, the
    receipt loses the sha256 and the bytes of a file that is sitting on the disk -- the
    tier-erasure defect, arriving through the door its own fix opened.
    """
    held = {
        "tiers": ["daily"],
        "files": [
            {"path": "tas/day/a.nc", "status": "fetched", "bytes": 100, "sha256": "s"}
        ],
    }
    checkpoint = summarise(
        ("daily",),
        [{"path": "tas/day/a.nc"}, {"path": "tas/day/b.nc"}],
        [],
        "minted",
    )

    merged = merge_into_receipt(checkpoint, held)

    row = next(r for r in merged["files"] if r["path"] == "tas/day/a.nc")
    assert row["status"] == "fetched", "a pending row erased a file already on disk"
    assert row["sha256"] == "s"
    assert merged["bytes_on_disk"] == 100
    assert merged["complete"] == 1 and merged["pending"] == 1


def test_the_disk_walk_can_disagree_with_the_receipt_it_checks(tmp_path):
    """A reconciliation that reads the rows twice always agrees, and proves nothing.

    Both legs run against the same merged receipt: one where the cache holds what the
    rows claim and one where it does not. A `reconciles` derived from the rows is green
    in both -- including against an EMPTY cache, which is the case that matters.
    """
    merged = {"bytes_on_disk": 300, "files": []}

    (tmp_path / "tas").mkdir()
    (tmp_path / "tas" / "one.nc").write_bytes(b"x" * 300)
    assert finalise_receipt(merged, walk=fetch._walk_cache(tmp_path))["cache_walk"] == {
        "files": 1,
        "bytes": 300,
        "partials": 0,
        "receipt_bytes": 300,
        "reconciles": True,
    }

    (tmp_path / "tas" / "one.nc").unlink()
    (tmp_path / "tas" / "two.nc.part").write_bytes(b"x" * 300)
    empty = finalise_receipt(merged, walk=fetch._walk_cache(tmp_path))["cache_walk"]
    assert empty["reconciles"] is False, (
        "a receipt claiming 300 bytes reconciled against an empty cache"
    )
    assert empty["files"] == 0, "a half-written .part grid was counted as a file"
    assert empty["partials"] == 1, "the partial was not reported at all"


def test_a_heating_season_is_counted_across_the_new_year_not_within_one():
    """Oct-Mar straddles two calendar years, so a per-year count is the wrong number.

    Twelve daily files spanning Oct 1991 to Mar 1993 are TWO complete seasons. A counter
    keyed to the calendar year sees 1991 (3 months), 1992 (6), 1993 (3) and reports one
    complete year -- half the answer, and it drops exactly the spells that start in
    December, which is the persistence question the daily tier was pulled for.
    """
    rows = []
    for year, month in [(1991, 10), (1991, 11), (1991, 12), (1992, 1), (1992, 2),
                        (1992, 3), (1992, 10), (1992, 11), (1992, 12), (1993, 1),
                        (1993, 2), (1993, 3)]:
        rows.append(
            {
                "path": f"tas/day/{year}{month:02d}.nc",
                "frequency": "day",
                "year": year,
                "month": month,
                "status": "fetched",
            }
        )

    coverage = daily_season_coverage(rows)

    assert coverage["complete_seasons"] == 2
    assert coverage["first_complete"] == "1991/92"
    assert coverage["last_complete"] == "1992/93"


def test_every_season_the_window_touches_is_counted_or_named_as_a_gap():
    """A short file list must not read as completeness. Silence is not the answer.

    The full manifest's two ends can never be complete -- January 1991 has no October
    1990 and December 2025 has no March 2026 -- so they appear as gap rows carrying the
    reason, rather than as a count that quietly starts a year late.
    """
    rows = [
        {**entry, "status": "fetched"} for entry in build_manifest(("daily",))
    ]

    coverage = daily_season_coverage(rows)
    gaps = {gap["season"]: gap for gap in coverage["gaps"]}

    years = SERIES_LAST_YEAR - SERIES_FIRST_YEAR
    assert coverage["complete_seasons"] == years, (
        f"{coverage['complete_seasons']} complete seasons from a full "
        f"{years + 1}-year pull"
    )
    assert coverage["first_complete"] == "1991/92"
    assert coverage["last_complete"] == "2024/25"
    assert set(gaps) == {"1990/91", "2025/26"}
    for season in gaps.values():
        assert season["missing"], "a gap row that names no missing month"
        for missing in season["missing"]:
            assert "outside the pulled window" in missing["reason"]


def test_a_gap_inside_the_window_names_the_status_that_caused_it():
    """A file the archive refused is a different gap from one nobody asked for."""
    rows = []
    for entry in build_manifest(("daily",)):
        status = "failed" if (entry["year"], entry["month"]) == (2000, 1) else "fetched"
        rows.append({**entry, "status": status})

    gaps = {gap["season"]: gap for gap in daily_season_coverage(rows)["gaps"]}

    assert "1999/00" in gaps, "a season with a failed month was counted complete"
    assert gaps["1999/00"]["missing"] == [{"month": "2000-01", "reason": "failed"}]
    assert gaps["1999/00"]["months_held"] == 5


def test_the_written_receipt_is_json_a_later_reader_can_use(tmp_path):
    """The receipt is provenance, so the fields a reader needs must survive the write."""
    summary = summarise(("daily",), MANIFEST, [_done(e) for e in MANIFEST[:5]], "minted")
    written = finalise_receipt(
        merge_into_receipt(summary, None), walk={"files": 5, "bytes": 500, "partials": 0}
    )

    reloaded = json.loads(json.dumps(written))
    assert reloaded["pull_status"] == "incomplete"
    assert reloaded["cache_walk"]["reconciles"] is True
    assert reloaded["daily_heating_seasons"]["definition"].startswith("October-March")
    assert reloaded["licence"] == "Open Government Licence v3.0"
