"""The half-hourly spine is the market, and a fold in the reporting layer may not erode it.

DIRECTOR, 2026-08-24: *"GB settlement is half-hourly and that is not an implementation detail,
it is the market. So the half-hourly spine stays half-hourly. Aggregate in the reporting and
ledger layers if that's where the memory goes, but the settlement and metering record keeps its
grain. And put a control on it that fails if anything half-hourly-dependent is added while the
fold is live, so this can't be discovered later by a tariff that silently can't be priced."*

THE CONTROL'S SUBJECT IS THE RETAINED BOOK, NOT THE SPINE — and the first two tests below pin
that, because a control that crept onto the spine would be a control against the thing the
constraint protects.

THE CLASS IS REAL AND PREDATES THE FOLD. Four published figures were being re-derived from the
retained book rather than from settlement — the peak/off-peak split, the worst half-hour of each
year, the treasury path and Triad exposure — and every one was found by diffing a generated
report, not by reading the code. A fifth would land the same way.

R15 — each proven by reverting, not asserted:
  * add a half-hourly read to a consumer -> `test_a_new_half_hourly_read_of_the_retained_book_FAILS`.
  * remove a frozen one -> `test_a_frozen_read_that_has_gone_also_fails_so_the_floor_can_only_shrink`.
  * point the scan at nothing -> `test_a_scan_that_reads_nothing_RAISES_rather_than_certifying`.
  * delete the baseline -> `test_a_missing_baseline_RAISES_rather_than_passing`.
"""
from __future__ import annotations

import json

import pytest

from tools import half_hourly_dependency_ratchet as hh


def test_the_spine_is_not_a_subject_of_this_control():
    """The settlement engine, the metering record and the imbalance ledger are half-hourly BY
    DESIGN and the fold never reaches them. Scanning them would count the thing the director's
    constraint exists to protect, and would red on exactly the code that must stay."""
    for spine in ("simulation/hedged_settlement.py", "simulation/hh_consumption.py",
                  "company/market/imbalance_ledger.py", "simulation/tou_periods.py",
                  "tools/generate_hh_data.py"):
        assert spine not in hh.CONSUMERS, (
            "{} is the SPINE. A ratchet over it would fire on the half-hourly code the "
            "constraint requires, which is the control arguing with its own purpose".format(spine))


def test_the_spine_really_is_half_hourly_so_the_distinction_is_not_notional():
    """If settlement had already been coarsened, the line this control draws would be fiction.
    Asserted against the engine itself rather than taken on trust."""
    from pathlib import Path

    src = (Path(hh.PROJECT) / "simulation" / "hedged_settlement.py").read_text(encoding="utf-8")
    assert src.count("for period in range(1, 49):") >= 3, (
        "the settlement engine no longer walks 48 periods per day for every term type — the "
        "spine has been coarsened and this control is guarding a line that has already moved")
    assert "is_peak_period(date_str, period)" in src, (
        "settlement no longer picks a rate per half-hour, so a time-of-use tariff is not "
        "being priced at the grain the market settles on")


def test_the_live_tree_is_at_its_frozen_census():
    added, gone = hh.diff(hh.scan(), hh.load_baseline())
    assert not added, "unrecorded half-hourly read(s) of the retained book: {}".format(added)
    assert not gone, "frozen read(s) no longer present — re-freeze to lower the floor: {}".format(gone)


def test_a_new_half_hourly_read_of_the_retained_book_FAILS(tmp_path):
    """THE CONTROL. A computation that needs the half-hour, added downstream of the fold, gets a
    day and is wrong in a way that looks like an answer."""
    baseline = {"reads": {"saas/reporting/annual_report.py": ["x = r['margin_gbp']"]}}
    current = {"saas/reporting/annual_report.py": [
        "x = r['margin_gbp']",
        "peak = is_peak_period(r['settlement_date'], r['settlement_period'])",
    ]}

    added, gone = hh.diff(current, baseline)

    assert any("is_peak_period" in a for a in added)
    assert not gone


def test_a_frozen_read_that_has_gone_also_fails_so_the_floor_can_only_shrink(tmp_path):
    """RATCHET, not a freeze. A read that has been repaired must be re-frozen deliberately, or
    the baseline drifts into a list of things that are no longer true."""
    baseline = {"reads": {"saas/ledger.py": ["a", "b"]}}
    added, gone = hh.diff({"saas/ledger.py": ["a"]}, baseline)

    assert gone == ["saas/ledger.py: b"]
    assert not added


def test_a_scan_that_reads_nothing_RAISES_rather_than_certifying(tmp_path):
    """FAIL-CLOSED (R15). An under-reporting census authorises exactly what it exists to
    prevent, and it does it while printing a clean result."""
    with pytest.raises(hh.ScanUnavailable):
        hh.scan(root=tmp_path)


def test_a_missing_baseline_RAISES_rather_than_passing(tmp_path):
    with pytest.raises(hh.ScanUnavailable):
        hh.load_baseline(tmp_path / "nope.json")


def test_the_frozen_census_is_not_empty():
    """A baseline of zero reads would make every one of the tests above vacuous — the ratchet
    would pass on a tree it had never looked at."""
    baseline = hh.load_baseline()
    total = sum(len(v) for v in (baseline.get("reads") or {}).values())
    assert total >= 10, (
        "the frozen census holds {} read(s); the four registers alone came from more than that, "
        "so the scan is not seeing the tree".format(total))


def test_the_baseline_is_json_and_says_what_it_is():
    raw = json.loads(hh.BASELINE.read_text(encoding="utf-8"))
    assert "spine" in raw["_doc"].lower()
    assert "reads" in raw
