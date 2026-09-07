"""The CM supplier levy artefact reproduces its own derivation from Annex 9's own rows.

Commons: `docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json`.
Write-up: `docs/market_research/capacity_market_levy_2016_2024.md`.
Opened by: `docs/staging/SEAT_FINDING_THE_CM_LEVY_ARTEFACTS_STATED_DERIVATION_DOES_NOT_REPRODUCE_ITS_2018_ROW_2026-09-07.md`
-- whose headline diagnosis this file REFUTES, and whose step 2 it is.

WHY THIS FILE EXISTS. On 2026-09-07 both lanes were wired to this artefact
(`simulation/policy_costs.py` and `company/regulatory/capacity_market.py`), which is right --
`ro_commons` states the rule, the two lanes may hold different READINGS and may not hold
different LAW. But it moved where the risk lives: before, a bad row was wrong in one lane and
disagreed with the other; after, it is wrong in BOTH, silently, and the annual report's live
reconciliation of the two readings shows nothing. `test_year_keyed_rate_table_census.py`'s
levy legs said so explicitly -- "nothing here re-derives the levy from Annex 9's
GBP/customer/year, so a wrong figure in the commons is wrong in both lanes at once". This file
is the leg that re-derives it, and it is the only control in the tree that can go red because
the LAW is wrong rather than because a lane misread it.

IT FOUND ONE ON ITS FIRST RUN, which is the reach evidence and beats any poison round: obligation
year 2024/25 was carried at GBP7.27/MWh, transcribed from Annex 9 v1.8 where only Apr-Sep 2024 was
published. v1.11 publishes all four quarters and the H2 level is materially lower, so the true
duration-weighted figure is GBP6.99 -- the H1-only reading overstated the year by 4.0%. The
artefact had honestly labelled that row "H1 ONLY ... the least settled figure here"; the label
travelled and the figure was still wrong in both lanes.

AND IT REFUTES THE FINDING THAT ASKED FOR IT. The finding recorded 2018/19 as a transcription slip:
GBP11.36/3.1 = 3.66 against a tabulated 3.67, with every other year implying a divisor of 3.100 and
only that one implying 3.095. The arithmetic was right and the conclusion was wrong. Annex 9 does
not publish a per-year figure at all -- it publishes an annualised level per CAP PERIOD, and the
obligation year is the duration-weighted mean of those. For 2018/19 that mean is 11.364754, and
11.364754/3.1 = 3.6661 -> 3.67. The row was correct; the DERIVATION STATEMENT beside it was
incomplete, and running it against the note's own rounded 11.36 manufactured a defect that was
never in the data. That is the failure this file makes structurally impossible: the artefact now
carries Annex 9's cap-period rows verbatim and the control performs every step of the reading --
the duration weighting, the division and the rounding -- so no step can be assumed.

WHY THE ARTEFACT CARRIES BOTH UNITS, and why that is not the tautology it looks like. The rule
from `ccl_main_rates.json`: the commons holds the PUBLISHER's unit and the control performs the
conversion, so the conversion is under test rather than assumed. Here the publisher's unit is
GBP/customer/year per cap period; `gbp_per_mwh` is our derived column and was transcribed
independently, at Phase 30a, long before the cap-period rows existed in this repo. Asserting one
against the other is therefore a real comparison of two independent transcriptions -- and it fired
on 2024, which is the proof it is one.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. Nothing here pins a levy to a literal. The
assertion is *this row reproduces the published cap periods it claims to summarise*, so correcting
the artefact toward Annex 9 must be able to pass, and drifting away from it must not. When Ofgem
publishes Jan-Mar 2027, adding those rows and the 2026/27 levy is a green change here; promoting
the partial year without them is not.

R15: every control here names the mutation that must make it fire.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

COMMONS = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "capacity_market_supplier_levy.json"
)


def _artefact() -> dict:
    return json.loads(COMMONS.read_text())


def _obligation_year(cap_period: dict) -> int:
    """The Apr-Mar obligation year a cap period opens in.

    Apr-Dec belong to the year they fall in; Jan-Mar belong to the year before. This is the
    artefact's stated `year_key` convention and it is recomputed here rather than read off the
    rows, so a cap period filed under the wrong year fires the coverage legs below.
    """
    year, month = int(cap_period["from"][:4]), int(cap_period["from"][5:7])
    return year if month >= 4 else year - 1


def _cap_periods_by_obligation_year(art: dict) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for period in art["annex9_cap_periods"]:
        grouped[_obligation_year(period)].append(period)
    return dict(grouped)


def _weighted_mean(periods: list[dict]) -> float:
    """Annex 9's levels are ANNUALISED rates in force during each period, so the obligation year
    is the DURATION-weighted mean and not a plain average. 2022/23 is the row that tells them
    apart: one six-month period at 9.217 then two quarterly ones at 11.671. Weighted (6/3/3) it
    is 10.4442 -> GBP3.37; unweighted it is 10.8532 -> GBP3.50. The published figure is 3.37, so
    a plain `mean()` here would fire on that year -- which is the mutation this helper owns.
    """
    months = sum(p["months"] for p in periods)
    return sum(p["months"] * p["gbp_per_customer_year"] for p in periods) / months


def test_every_published_row_reproduces_its_own_derivation():
    """MUTATION: edit any `gbp_per_mwh`, any `gbp_per_customer_year`, any cap-period level, or
    `basis.benchmark_mwh`, and this fires. It is the leg that re-derives the LAW rather than
    comparing two lanes' readings of it, and it fired on 2024/25 (7.27 -> 6.99) the first time
    it ran.

    THE DIVISION IS ON THE UNROUNDED MEAN AND THAT IS LOAD-BEARING. Replacing a row's
    `gbp_per_customer_year` with its own 2dp display value -- the "tidy-up" that looks
    equivalent -- fires here on 2018/19, because 11.36/3.1 rounds to 3.66 and 11.364754/3.1
    rounds to 3.67. That single rounding is what a BLOCKING finding was filed over.
    """
    art = _artefact()
    benchmark = art["basis"]["benchmark_mwh"]
    by_year = _cap_periods_by_obligation_year(art)

    checked = []
    for row in art["levy_gbp_per_mwh"]:
        if row["gbp_per_customer_year"] is None:
            continue
        year = row["obligation_year"]
        periods = by_year.get(year, [])
        assert periods, (
            f"obligation year {year} carries a per-customer figure but no Annex 9 cap periods "
            "to derive it from"
        )
        mean = _weighted_mean(periods)
        # 1e-5, not float-exact. The artefact stores the mean to 6dp, and a rebuild that
        # accumulates the same periods in a different order lands a unit in the last place away
        # -- noise this leg must not red on. It is still 500x tighter than the 0.005 that could
        # change the 2dp rounding below, so every error that reaches a published figure is
        # caught, and the 2dp equality is the assertion that actually guards the money.
        assert mean == pytest.approx(row["gbp_per_customer_year"], abs=1e-5), (
            f"{year}: stated GBP/customer/year {row['gbp_per_customer_year']} is not the "
            f"duration-weighted mean {mean:.6f} of its own cap periods"
        )
        assert round(mean / benchmark, 2) == row["gbp_per_mwh"], (
            f"{year}: {mean:.6f} / {benchmark} = {mean / benchmark:.6f} -> "
            f"{round(mean / benchmark, 2)}, but the row states {row['gbp_per_mwh']}"
        )
        checked.append(year)

    assert len(checked) >= 9, (
        f"only {len(checked)} rows were derivation-checked ({checked}); the record has covered "
        "at least nine obligation years since 2026-09-07 and this leg going quiet is how a "
        "coverage collapse would look"
    )


def test_the_estimated_rows_are_exactly_the_ones_without_a_per_customer_figure():
    """MUTATION: null a `primary` row's `gbp_per_customer_year` and this fires.

    THIS IS THE ESCAPE HATCH, and without it the leg above is fail-open in the cheapest possible
    way: a row that will not reconcile can be made to pass by deleting the figure it fails
    against. `provenance` and the presence of the figure must agree in both directions, so
    dropping the figure forces the row to also claim `estimated` -- which is a visible,
    reviewable claim about Annex 9's coverage rather than a silent skip.
    """
    art = _artefact()
    without_figure = {
        r["obligation_year"] for r in art["levy_gbp_per_mwh"]
        if r["gbp_per_customer_year"] is None
    }
    estimated = {
        r["obligation_year"] for r in art["levy_gbp_per_mwh"]
        if r["provenance"] == "estimated"
    }
    assert without_figure == estimated, (
        f"rows with no per-customer figure {sorted(without_figure)} must be exactly the "
        f"`estimated` rows {sorted(estimated)} -- a `primary` row cannot escape the derivation "
        "check by nulling the figure it would be checked against"
    )


def test_a_complete_obligation_year_has_a_row_and_a_partial_one_does_not():
    """MUTATION: add a levy row for 2026/27 (9 of 12 months published) and this fires; delete the
    2025/26 row and it fires the other way.

    BOTH DIRECTIONS, because the artefact promises both and a one-sided check would let the more
    tempting error through. Promoting a partial year publishes a real-looking number for a year
    nobody has published -- the exact shape of the 2024/25 defect this file found, where a
    six-month reading was carried as a year. Forgetting a completed year silently freezes the
    record and hands the sim's carry-forward a stale rate.
    """
    art = _artefact()
    by_year = _cap_periods_by_obligation_year(art)
    rows = {r["obligation_year"] for r in art["levy_gbp_per_mwh"]}

    complete = {y for y, ps in by_year.items() if sum(p["months"] for p in ps) == 12}
    partial = {y for y, ps in by_year.items() if sum(p["months"] for p in ps) != 12}

    assert complete - rows == set(), (
        f"obligation years {sorted(complete - rows)} have 12 months of published cap periods but "
        "no levy row -- a completed year was forgotten and the record is frozen behind Annex 9"
    )
    assert partial & rows == set(), (
        f"obligation years {sorted(partial & rows)} have an INCOMPLETE cap-period record and a "
        "levy row anyway. A part-year mean is a real-looking number for a year nobody published; "
        "2024/25 was carried at a six-month reading for exactly this reason and was 4.0% out"
    )
    assert partial, (
        "no partial obligation year is present at all, so the second assertion above cannot "
        "fail. Annex 9 always publishes forward cap periods beyond the last complete year; if "
        "that stopped being true this leg has gone vacuous and needs re-founding, not deleting"
    )


def test_months_published_matches_the_cap_periods_actually_carried():
    """MUTATION: change any row's `months_published`, or drop a cap period, and this fires.

    `months_published` is the field a reader trusts to know how settled a row is, and it is the
    field that would have flagged 2024/25 as half a year if anyone had looked at it. Left
    unchecked it is a comment; checked against the rows it summarises, it is a claim.
    """
    art = _artefact()
    by_year = _cap_periods_by_obligation_year(art)
    for row in art["levy_gbp_per_mwh"]:
        year = row["obligation_year"]
        actual = sum(p["months"] for p in by_year.get(year, []))
        assert row["months_published"] == actual, (
            f"{year}: row claims {row['months_published']} months published, cap periods carry "
            f"{actual}"
        )


def test_the_cap_periods_are_contiguous_and_do_not_overlap():
    """MUTATION: duplicate a cap period, or drop one from the middle, and this fires.

    The weighted mean is only the published level if the periods it averages TILE the year. A
    duplicated quarter double-weights itself and a missing one silently reweights its
    neighbours, and neither shows up as a wrong total: `months_published` above would still
    agree with the (corrupted) rows it is computed from, so that leg cannot catch this and this
    one is not redundant with it.
    """
    art = _artefact()
    periods = sorted(art["annex9_cap_periods"], key=lambda p: p["from"])
    for earlier, later in zip(periods, periods[1:]):
        year, month = int(earlier["to"][:4]), int(earlier["to"][5:7])
        month += 1
        if month == 13:
            year, month = year + 1, 1
        assert later["from"] == f"{year:04d}-{month:02d}", (
            f"cap period starting {later['from']} does not directly follow the one ending "
            f"{earlier['to']} -- the record has a gap or an overlap, and a weighted mean over "
            "non-tiling periods is not the published level"
        )
