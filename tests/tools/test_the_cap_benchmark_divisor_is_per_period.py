"""The cap composition's divisor is dated, and the model is re-asked whether it still is.

Subject: `tools/ofgem_cap_unit_rate_composition.py` — `benchmark_kwh` and
`_verify_benchmark_schedule`.

THE DEFECT THIS NAMES. Ofgem's v1.31 cap level model carries THREE benchmark consumptions under ONE
header cell: 3,100 kWh to December 2025, 2,700 from January 2026 (P15b), 2,500 from July 2026
(P16b) — and the header cell states only the last of them. A reader that takes the header divides 29
of the 33 periods by 2,500 rather than 3,100 and publishes every historical unit rate 24% high.

**Why that would not have been noticed.** The artefact's headline is a SHARE, and a share is a ratio
in which the divisor cancels. Every share stays exactly right while every published p/kWh is wrong.
So the failure is silent in precisely the figure a reader would check.

WHY BOTH LEGS ARE HERE. The dated schedule is a claim about a publisher; a claim about a publisher
that nothing re-asks is what put this artefact twelve editions behind in the first place. So one leg
proves the schedule DISCRIMINATES (all three bases are reachable, not one basis wearing a table's
clothes) and the other proves the witness can REFUSE (a model stating a different consumption stops
the publish). A witness that accepted everything would pass a test written only the first way.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here pins 2,700 or 2,500 as correct policy;
Ofgem may revise the benchmark again and the schedule should then move. What is pinned is that the
schedule is not a constant, that each date boundary is load-bearing, and that a workbook disagreeing
with it refuses rather than publishes.
"""
from __future__ import annotations

import json

import pytest

openpyxl = pytest.importorskip("openpyxl")

from tools import ofgem_cap_unit_rate_composition as subject  # noqa: E402


def test_every_benchmark_basis_in_the_schedule_is_actually_reachable():
    """The whole partition, in one control, not a leg per basis.

    A `benchmark_kwh` that returned 3,100 for everything passes any test that only asks "is a
    pre-2026 period on 3,100". This asks the opposite question first: does the schedule ever produce
    anything else? A schedule collapsed to one value fails here and nowhere else.
    """
    produced = {subject.benchmark_kwh(start) for start in
                ("2015-04-01", "2023-10-01", "2025-10-01", "2026-01-01", "2026-04-01",
                 "2026-07-01", "2026-10-01", "2027-01-01")}
    declared = {kwh for _, kwh in subject.BENCHMARK_KWH_SCHEDULE}
    assert produced == declared, (
        f"the schedule declares bases {sorted(declared)} but only {sorted(produced)} are reachable "
        "across the cap periods the model carries; a basis nothing reaches is a basis nothing checks"
    )
    assert len(declared) > 1, "a one-value schedule is the header-cell defect wearing a table"


def test_each_boundary_in_the_schedule_moves_the_divisor():
    """Every dated boundary is load-bearing — the day before it differs from the day of it."""
    for starts_from, kwh in subject.BENCHMARK_KWH_SCHEDULE[1:]:
        year, month, day = (int(part) for part in starts_from.split("-"))
        day_before = f"{year}-{month:02d}-{day - 1:02d}" if day > 1 else None
        assert subject.benchmark_kwh(starts_from) == kwh
        if day_before:
            assert subject.benchmark_kwh(day_before) != kwh, (
                f"the boundary at {starts_from} does not change the divisor, so it is decoration"
            )


def test_an_unparseable_period_gets_the_earliest_basis_not_the_latest():
    """The model's unlabelled columns are its pre-2019 back-casts and they are all pre-revision.

    Defaulting them to the LATEST basis — the natural way to write this — is the header-cell defect
    reintroduced through the fallback path.
    """
    assert subject.benchmark_kwh(None) == subject.BENCHMARK_KWH_SCHEDULE[0][1]


def test_electricity_vat_is_not_a_constant_across_the_published_periods():
    """Zero-rated from October 2026 to March 2027; 5% either side of it.

    Same shape as the divisor: a flat 1.05 is right for 31 of the 33 periods and silently wrong for
    the other two, and only the derived INCLUDING-VAT figure moves.
    """
    assert subject.vat_multiplier("2025-10-01") == subject.VAT_MULTIPLIER_DEFAULT
    assert subject.vat_multiplier("2026-10-01") != subject.VAT_MULTIPLIER_DEFAULT
    assert subject.vat_multiplier("2027-04-01") == subject.VAT_MULTIPLIER_DEFAULT


def _windows(tmp_path, monkeypatch, rows):
    path = tmp_path / "ofgem_default_tariff_cap_windows.json"
    path.write_text(json.dumps({"windows": rows}))
    monkeypatch.setattr(subject, "CAP_WINDOWS", path)
    return path


SELF_DERIVED = subject.SELF_DERIVED_WINDOW_SOURCE + "_v1.31"


def test_a_window_derived_from_the_cap_model_cannot_corroborate_the_cap_model(
        tmp_path, monkeypatch):
    """The cross-check must not quietly start comparing the workbook with itself.

    THE DANGER IS THAT THIS LOOKS LIKE AN IMPROVEMENT. `ofgem_default_tariff_cap_windows.json` was
    extended past 2025-12-31 with rows derived from the same cap level model this module reads.
    Admitting them would make the reported worst relative error BETTER, because they agree almost
    exactly — and the cross-check is the only evidence the benchmark-minus-nil decomposition is
    right, so a self-agreeing row does not strengthen it, it empties it.
    """
    _windows(tmp_path, monkeypatch,
             [{"from": "2026-01-01", "to": "2026-03-31", "elec": 276.9, "source": SELF_DERIVED}])
    with pytest.raises(subject.CapModelUnavailable, match="no cap period"):
        subject.cross_check([{"cap_period": "January 2026 - March 2026", "starts": "2026-01-01",
                              "unit_rate_p_per_kwh_ex_vat": 26.37}])


def test_an_independently_published_window_still_corroborates(tmp_path, monkeypatch):
    """The other leg. An exclusion that dropped EVERY row would pass the test above and leave the
    module permanently unable to publish, and the two are indistinguishable without this."""
    _windows(tmp_path, monkeypatch,
             [{"from": "2026-01-01", "to": "2026-03-31", "elec": 276.9,
               "source": "third_party_cap_history_compilation"}])
    result = subject.cross_check([{"cap_period": "January 2026 - March 2026",
                                   "starts": "2026-01-01",
                                   "unit_rate_p_per_kwh_ex_vat": 276.9 / 10.0 / 1.05}])
    assert result["periods_checked"] == 1


def test_a_window_with_no_source_at_all_is_kept(tmp_path, monkeypatch):
    """Absence of a `source` is not evidence of self-derivation, and dropping unmarked rows would
    silently empty the cross-check the first time a lane adds a row without the field."""
    _windows(tmp_path, monkeypatch,
             [{"from": "2026-01-01", "to": "2026-03-31", "elec": 276.9}])
    assert subject.cross_check([{"cap_period": "January 2026 - March 2026",
                                 "starts": "2026-01-01",
                                 "unit_rate_p_per_kwh_ex_vat": 276.9 / 10.0 / 1.05}
                                ])["periods_checked"] == 1


def _witness_workbook(values: dict[str, float] | None, *, sheet_name: str | None = None):
    """A workbook carrying just the consumption table `_verify_benchmark_schedule` reads.

    `values` maps the header phrase to the MWh stated against it. `None` builds a workbook with no
    witness sheet at all.
    """
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)
    if values is None:
        workbook.create_sheet("Notes")
        return workbook
    sheet = workbook.create_sheet(sheet_name or subject.BENCHMARK_WITNESS_SHEET)
    sheet.cell(row=6, column=2, value="Fuel/Metering arrangement")
    sheet.cell(row=7, column=2, value=f"{subject.BENCHMARK_WITNESS_ROW_LABEL} ")
    for offset, (phrase, mwh) in enumerate(values.items()):
        sheet.cell(row=6, column=3 + offset,
                   value=f"Revised benchmark consumption (MWh)\n{phrase}")
        sheet.cell(row=7, column=3 + offset, value=mwh)
    return workbook


def _agreeing_values() -> dict[str, float]:
    return {phrase: mwh for phrase, mwh in subject.BENCHMARK_SCHEDULE_WITNESS}


REVISED_PERIODS = ["2025-10-01", "2026-01-01", "2026-07-01"]


def test_the_witness_accepts_a_model_that_still_agrees():
    """The poison round's control arm. Without this, every refusal below is unattributable.

    A `_verify_benchmark_schedule` that raised unconditionally would pass every refusal test on this
    page, and "the witness refuses" would mean "the witness is broken" rather than "the model moved".
    """
    witnessed = subject._verify_benchmark_schedule(
        _witness_workbook(_agreeing_values()), REVISED_PERIODS)
    assert [row["kwh"] for row in witnessed] == [
        int(round(mwh * 1000)) for _, mwh in subject.BENCHMARK_SCHEDULE_WITNESS]


def test_the_witness_refuses_when_the_model_states_a_different_consumption():
    """A fourth revision must stop the publish, not be averaged into it.

    This is the mutation the whole schedule exists to survive: Ofgem revises the benchmark again,
    the module's dates go stale, every share stays right and every unit rate is quietly wrong.
    """
    moved = _agreeing_values()
    first = next(iter(moved))
    moved[first] = moved[first] + 0.4
    with pytest.raises(subject.CapModelUnavailable, match="revised again"):
        subject._verify_benchmark_schedule(_witness_workbook(moved), REVISED_PERIODS)


def test_the_witness_refuses_when_the_model_stops_stating_the_period_at_all():
    """A renamed or dropped column is not silently treated as agreement."""
    dropped = {"some other date range": 2.7}
    with pytest.raises(subject.CapModelUnavailable, match="does not state"):
        subject._verify_benchmark_schedule(_witness_workbook(dropped), REVISED_PERIODS)


def test_a_model_carrying_revised_periods_with_no_witness_sheet_refuses():
    """Fail CLOSED, not back onto the pre-revision basis, which would be 24% wrong and silent."""
    with pytest.raises(subject.CapModelUnavailable, match="benchmark consumption"):
        subject._verify_benchmark_schedule(_witness_workbook(None), REVISED_PERIODS)


def test_an_older_model_with_no_revised_period_needs_no_witness():
    """v1.19 predates the revision entirely; demanding a table it cannot have would refuse the past.

    This is the leg that stops the control above from being a blanket refusal.
    """
    assert subject._verify_benchmark_schedule(
        _witness_workbook(None), ["2019-01-01", "2023-10-01", None]) == []
