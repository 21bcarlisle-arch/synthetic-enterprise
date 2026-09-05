#!/usr/bin/env python3
"""The HadUK pull receipt must record every tier on disk, not only the last one pulled.

THE DEFECT, caught on 2026-09-05 with the bulk pull already running, and killed to fix it.
`tools/fetch_haduk_grid.py` writes `docs/market_research/haduk_grid_pull_receipt.json` --
the only committed evidence of what was pulled, since the ruling forbids the ~20GB of raw
grids from entering the repo. `run()` builds its summary from the manifest of the tiers
THIS invocation was asked for. The pull is deliberately staged: the three 30-year normals
first (a minute), then the 315 monthly and daily files (hours, detached). So:

    fetch --tiers normals --receipt          -> receipt: 3 files, tiers [normals]
    fetch --tiers monthly,daily --receipt    -> receipt: 315 files, tiers [monthly, daily]

and the normals -- the WMO 1991-2020 climatology that the whole "level" half of the cell
derivation rests on -- are gone from the record, while three 41MB files sit on disk being
read by the analysis.

WHY THAT IS DANGEROUS RATHER THAN UNTIDY. The receipt is not a log; it is the provenance
artefact. It carries the source URL, the pinned release directory, the licence and the
sha256 for each grid, and it is what a later reader -- or the annual HadUK refresh -- uses
to answer "where did this number come from". A receipt that omits a file the analysis
consumed does not look broken: it looks like a complete record of a smaller pull. The
figure derived from the normals would then trace to nothing, which is exactly the
unattributable-constant failure the knowledge-first rule exists to prevent.

It is also the shape that hides best. Nothing reds. The file count is plausible, the
bytes are plausible, every row present is correct, and the omission is only visible to
someone who already knows a normals tier was pulled.

THE REPAIR: `merge_into_receipt()` folds the run into the receipt already on disk, keyed
by archive path, and recomputes the counts from the merged set rather than adding them.

MUTATION: make `merge_into_receipt` return `summary` unchanged (the pre-repair behaviour)
and `test_a_second_tiers_receipt_keeps_the_first_tiers_files` fails. Make it merge with
`previous` winning over `summary` and the re-pull test fails. Make `requested`/`complete`
the sum of the two runs rather than a recount of the merge, and the idempotence test
fails.
"""

import pytest

from tools.fetch_haduk_grid import (
    HEATING_SEASON_MONTHS,
    PHASE1_VARIABLES,
    SERIES_FIRST_YEAR,
    SERIES_LAST_YEAR,
    _jwt_expiry,
    build_manifest,
    merge_into_receipt,
)


def _summary(tiers, files):
    failed = [f for f in files if f["status"] == "failed"]
    return {
        "tiers": list(tiers),
        "requested": len(files),
        "complete": len(files) - len(failed),
        "failed": len(failed),
        "bytes_on_disk": sum(f.get("bytes", 0) for f in files),
        "files": files,
    }


def _row(path, status="fetched", size=100, sha="a"):
    return {"path": path, "status": status, "bytes": size, "sha256": sha}


NORMALS = _summary(["normals"], [_row("tas/mon-30y/n.nc"), _row("sun/mon-30y/n.nc")])


def test_a_second_tiers_receipt_keeps_the_first_tiers_files():
    """THE DEFECT ITSELF: pulling monthly must not erase the normals already on disk."""
    monthly = _summary(["monthly"], [_row("tas/mon/1991.nc"), _row("tas/mon/1992.nc")])

    merged = merge_into_receipt(monthly, NORMALS)

    paths = {row["path"] for row in merged["files"]}
    assert "tas/mon-30y/n.nc" in paths, "the normals tier was dropped from the receipt"
    assert "sun/mon-30y/n.nc" in paths
    assert paths == {
        "tas/mon-30y/n.nc",
        "sun/mon-30y/n.nc",
        "tas/mon/1991.nc",
        "tas/mon/1992.nc",
    }
    assert merged["tiers"] == ["monthly", "normals"]
    assert merged["requested"] == 4
    assert merged["complete"] == 4
    assert merged["bytes_on_disk"] == 400


def test_re_pulling_a_tier_updates_its_rows_instead_of_duplicating_them():
    """Resumption means a tier gets re-run. The receipt must not grow each time."""
    first = _summary(["monthly"], [_row("tas/mon/1991.nc", status="fetched", sha="old")])
    second = _summary(
        ["monthly"], [_row("tas/mon/1991.nc", status="present", sha="new")]
    )

    merged = merge_into_receipt(second, merge_into_receipt(first, NORMALS))

    rows = [row for row in merged["files"] if row["path"] == "tas/mon/1991.nc"]
    assert len(rows) == 1, "a re-pulled file was recorded twice"
    assert rows[0]["sha256"] == "new", "the stale row won over the fresh one"
    assert merged["requested"] == 3
    assert merged["bytes_on_disk"] == 300


def test_a_failure_carried_forward_still_counts_as_failed_after_the_merge():
    """A file that failed in an earlier tier must not read as complete once merged.

    Recounting from the merged set is what makes this hold; summing the two runs'
    `failed` fields would also work here, but summing `complete` would not, and a
    receipt whose completeness disagrees with its own rows is the severity-column
    failure in another costume.
    """
    broken = _summary(
        ["monthly"], [_row("tas/mon/1991.nc", status="failed", size=0)]
    )

    merged = merge_into_receipt(broken, NORMALS)

    assert merged["failed"] == 1
    assert merged["complete"] == 2
    assert merged["requested"] == 3
    assert merged["complete"] + merged["failed"] == merged["requested"]


def test_the_first_tier_writes_a_receipt_with_no_previous_to_merge():
    assert merge_into_receipt(NORMALS, None) is NORMALS
    assert merge_into_receipt(NORMALS, {}) is NORMALS


def test_the_manifest_covers_every_phase_one_variable_and_the_declared_window():
    """The pull's subject is what the ruling named, and the code is where that is said.

    Keyed to the ruling's own constants rather than to today's file count, so widening
    the window moves the expectation with it instead of reddening.
    """
    monthly = build_manifest(("monthly",))
    years = SERIES_LAST_YEAR - SERIES_FIRST_YEAR + 1

    assert {entry["variable"] for entry in monthly} == set(PHASE1_VARIABLES)
    assert len(monthly) == len(PHASE1_VARIABLES) * years
    for variable in PHASE1_VARIABLES:
        got = sorted(e["year"] for e in monthly if e["variable"] == variable)
        assert got == list(range(SERIES_FIRST_YEAR, SERIES_LAST_YEAR + 1))

    normals = build_manifest(("normals",))
    assert {entry["variable"] for entry in normals} == set(PHASE1_VARIABLES)

    daily = build_manifest(("daily",))
    assert {entry["variable"] for entry in daily} == {"tas"}
    assert len(daily) == len(HEATING_SEASON_MONTHS) * years


def test_the_daily_pull_covers_the_whole_heating_season_in_every_year():
    """Narrowing the season must red, and this may not be keyed to the constant itself.

    Written first as `{months in the manifest} == set(HEATING_SEASON_MONTHS)`, which
    passed happily when the constant was mutated from (1,2,3,10,11,12) to (1,2,3,11,12)
    -- both sides moved together, so it asserted only that build_manifest reads its own
    constant. The requirement is stated here independently instead.

    October to March is the GB heating season the persistence question lives in: the
    ruling's subject is a five-day cold snap costing more than the same degree-days
    spread thin, and dropping a shoulder month drops the spells that start or end in it.
    A wider season is permitted -- it only costs disk -- so this is a floor, not equality.
    """
    months = {entry["month"] for entry in build_manifest(("daily",))}

    assert {10, 11, 12, 1, 2, 3} <= months, (
        f"the daily pull skips heating-season month(s) "
        f"{sorted({10, 11, 12, 1, 2, 3} - months)}"
    )

    # ...and every year gets the whole season, not just the span in aggregate.
    by_year = {}
    for entry in build_manifest(("daily",)):
        by_year.setdefault(entry["year"], set()).add(entry["month"])
    assert set(by_year) == set(range(SERIES_FIRST_YEAR, SERIES_LAST_YEAR + 1))
    thin = {year: sorted(got) for year, got in by_year.items()
            if not {10, 11, 12, 1, 2, 3} <= got}
    assert not thin, f"year(s) missing heating-season months: {thin}"


def test_the_manifest_asks_for_february_29_only_in_leap_years():
    """A wrong filename is a 404, and 210 daily files is where an off-by-one hides."""
    daily = {entry["year"]: entry for entry in build_manifest(("daily",))
             if entry["month"] == 2}

    assert daily[2020]["url"].endswith("20200201-20200229.nc")
    assert daily[2021]["url"].endswith("20210201-20210228.nc")
    assert daily[2000]["url"].endswith("20000201-20000229.nc") if 2000 in daily else True


@pytest.mark.parametrize("token", ["", "not-a-jwt", "a.b", "a.!!!.c", "a.e30.c"])
def test_an_unreadable_token_expiry_is_none_so_the_puller_re_mints(token):
    """None means 'refresh', not 'fresh'.

    `Token.value()` treats a None expiry as already spent. If `_jwt_expiry` guessed a
    far-future time instead, a 20-hour pull would keep presenting a dead token and every
    remaining file would 401 -- fetch_one records that as `failed`, so the pull would
    complete, report failures, and look like an archive problem.
    """
    assert _jwt_expiry(token) is None


def test_a_readable_expiry_is_returned_so_a_live_token_is_not_thrown_away():
    # {"exp": 1788867671} base64url, unpadded -- the shape CEDA actually returns.
    assert _jwt_expiry("h.eyJleHAiOiAxNzg4ODY3NjcxfQ.s") == 1788867671.0
