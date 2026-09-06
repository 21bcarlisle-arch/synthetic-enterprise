"""The settlement timetable Poesys PUBLISHES must be the one Poesys SOURCED.

THE DEFECT THIS NAMES (CONTROLS_THAT_CANNOT_FAIL). On 2026-08-29 a sourced
correction landed against Elexon's own published timetable: the scheduled runs
are SF 1 / R1 2 / R2 4 / R3 7 / RF 14 months, RF being the LAST SCHEDULED run,
and the 28-month figure that had been attached to RF is DF, the disputes-only
rectification run. It reached `company/regulatory/settlement_reconciliation.py`
and `simulation/settlement_timetable.py` and stopped. `tools/generate_world_data.py`
hand-carried its own copy of the pre-correction figures into `site/data/world.json`,
so for nineteen days the SERVED artefact -- public, under Poesys's name -- told a
reader that GB settlement finalises at T+28 months on every settlement day, citing
as its evidence a module it did not import and which was wrong in the same way.

Nothing in the tree could observe two settlement timetables disagreeing. This is
that leg, and it is deliberately ONE leg over the seam that actually reaches the
site rather than a register of every implementation: a register would have to be
maintained, and the maintenance is the thing that failed.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here pins 1/2/4/7/14. The
expectation is re-derived from `ELEXON_RUN_MONTHS` on every run, so the day Elexon
changes the timetable (MHHS takes the whole process to four months as meters
migrate) this control stays GREEN once the feed is regenerated, and the day anyone
re-types a literal into the generator, or the feed goes stale against a corrected
constant, it goes RED. Pinning the numbers would have been green on exactly the day
the published figure became wrong in a new way, which is how the defect survived.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from company.regulatory.settlement_reconciliation import ELEXON_RUN_MONTHS

PROJECT = Path(__file__).resolve().parents[2]
WORLD_JSON = PROJECT / "site" / "data" / "world.json"


def _published_ladder() -> list[dict]:
    """The settlement ladder as SERVED. Fails closed and loudly at every step --
    a missing file, a missing crossing or a missing ladder must not read as
    'nothing to check here', which is the shape that lets a published figure rot."""
    assert WORLD_JSON.exists(), (
        f"{WORLD_JSON} is not on disk. This is the served Door-5 feed and it is "
        f"tracked; its absence is a finding, not a reason to skip."
    )
    world = json.loads(WORLD_JSON.read_text())
    crossings = world.get("wall", {}).get("crossings", [])
    matches = [c for c in crossings if c.get("id") == "meter_reads"]
    assert len(matches) == 1, (
        f"expected exactly one 'meter_reads' wall crossing in the published feed, "
        f"found {len(matches)} among {[c.get('id') for c in crossings]}"
    )
    ladder = matches[0].get("settlement_ladder")
    assert ladder, (
        "the published meter_reads crossing carries no settlement_ladder. The "
        "timetable was dropped from the feed rather than corrected -- that is a "
        "different defect, not a pass."
    )
    return ladder


def test_the_PUBLISHED_settlement_ladder_carries_the_SOURCED_run_timings():
    published = {row["run"]: row["months"] for row in _published_ladder()}
    expected = {run: ELEXON_RUN_MONTHS[run] for run in published}
    assert published == expected, (
        f"the served site/data/world.json publishes settlement run timings that "
        f"are not the sourced ones. Published {published}, sourced {expected}. "
        f"Either the generator has re-acquired a hand-typed copy, or the feed is "
        f"stale against a corrected constant and needs regenerating "
        f"(`python3 tools/generate_world_data.py`). Source: "
        f"docs/market_research/elexon_settlement_run_timetable_verified.md."
    )


def test_the_published_ladder_names_only_runs_the_SOURCE_defines():
    """A run published with a timing the source does not define is the same defect
    wearing a different hat -- 'DF' rendered as a scheduled stage, or an invented
    run name -- and the timings test above cannot see it, because it only compares
    the runs that ARE published."""
    published_runs = [row["run"] for row in _published_ladder()]
    unknown = [r for r in published_runs if r not in ELEXON_RUN_MONTHS]
    assert not unknown, (
        f"the published ladder names run(s) {unknown} that "
        f"ELEXON_RUN_MONTHS does not define"
    )
    assert "DF" not in published_runs, (
        "DF is published as a rung of the scheduled ladder. It is the dispute "
        "rectification run -- an undisputed settlement day never reaches it -- and "
        "presenting it as a scheduled stage IS the original defect, restated."
    )


def test_every_published_rung_actually_carries_a_TIMING():
    """The `months` field is what the two controls above read. A rung that renders
    prose but no number would make both of them vacuous over that rung while the
    page still shows a reader a figure."""
    ladder = _published_ladder()
    for row in ladder:
        assert isinstance(row.get("months"), int), (
            f"published rung {row.get('run')!r} carries months={row.get('months')!r}, "
            f"not an int -- the timing controls cannot see it"
        )
        assert str(row["months"]) in str(row.get("timing", "")), (
            f"published rung {row.get('run')!r} renders timing "
            f"{row.get('timing')!r}, which does not contain its own months value "
            f"{row['months']} -- the prose a reader sees and the number the "
            f"controls check have come apart"
        )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
