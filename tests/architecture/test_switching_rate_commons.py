"""Every lane's reading of the GB domestic switching rate sits inside the PUBLISHED band.

Commons: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
Write-up: `docs/market_research/gb_switching_rate_denominators.md`.
Opened by: `docs/staging/WORKER_FINDING_THE_WORLDS_DEPARTURE_LEVEL_HAS_NEVER_BEEN_CHECKED_AGAINST_A_PUBLISHED_RATE_2026-08-30.md`.

THE DEFECT THIS EXISTS FOR. `company/market/market_report.py::_UK_SWITCHING_RATE_PCT` carried ten
years of domestic switching rates with no per-line citation, and NINE of the ten sat outside the
published record -- 2021 at 6.1% against a published 17.9-18.4%, 2020 at 14.2% against 22.5-23.0%.
`f5_simulated_competitor_field.md` §9 caught the 2021 value against live Energy UK data in July 2026
and recorded that the table must be "reconciled or retired". Six weeks later nothing had, because
nothing could see it: the repo held the right series in a markdown research file and the wrong one
in an importable accessor, and no control compared them.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ANSWER. The assertion is *inside the published band on a
declared denominator*, not *equal to 18.2%*. A control pinned at today's numbers goes red the moment
the world becomes more honest and stays green while the claim rots -- the shape this project has
repaired repeatedly. Correcting a lane's reading toward the record must be able to pass here;
inventing one must not.

WHY A BAND AND NOT A PIN. `test_year_keyed_rate_table_census.py`'s pin machinery asserts equality to
a published scalar, and there is no published scalar here: the record states switch COUNTS, and a
count over an account total is a range once the account total's own drift is admitted. Forcing a
scalar would mean choosing a point inside the band, which is a number chosen because a number was
needed. So this file owns the switching table and the census keeps it in `published_unpinned` with
its reason updated to point here.

B3's rule holds: the commons holds the record, each lane holds its own reading, and NO test pins two
readings to each other. If a second lane grows a switching-rate table, it is added to
`_LANE_READINGS` below and held to the same band -- not to `market_report`'s numbers.

R15: every control here names the mutation that must make it fire.
"""
from __future__ import annotations

import json

import pytest

import tools.measure_departure_level as instrument

#: ONE READER OF THE COMMONS, and it is the instrument rather than this file. A test that parses
#: the artefact itself would be checking a copy of the parse the measurement uses, so a reader that
#: silently dropped a year would pass here and under-report there. Importing the instrument makes
#: this file exercise the same `published_bands()` the 3.15x gap was measured with.
COMMONS = instrument.COMMONS

#: `{dotted module path: attribute}` -- every lane reading of the GB domestic switching rate.
#: One entry today. The register exists so the second one cannot arrive unheld, which is exactly
#: how the first one got nine years wrong.
_LANE_READINGS: dict[str, str] = {
    "company.market.market_report": "_UK_SWITCHING_RATE_PCT",
}

#: The window the published record covers. A lane year outside it is a hole, not a pass.
_RECORD_YEARS = range(2016, 2026)


def _commons() -> dict:
    return json.loads(instrument.COMMONS.read_text())


def _bands() -> dict[int, tuple[float, float]]:
    """THE INSTRUMENT'S OWN READER, not a second parse of the same file.

    `published_bands()` is what `tools.measure_departure_level` measures the world against, so
    holding the lane readings to anything else would leave the two able to disagree about the band
    without either noticing.
    """
    return instrument.published_bands()


def _lane_table(dotted: str, attr: str) -> dict[int, float]:
    import importlib

    return dict(getattr(importlib.import_module(dotted), attr))


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (a) THE BAND ITSELF — an artefact that does not say what it counts cannot hold anything
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_the_commons_declares_both_a_numerator_and_a_denominator():
    """MUTATION: delete `numerator` or `denominator` from `basis` and this fires.

    A switching rate whose numerator is unstated is the defect this whole area is made of: a
    both-fuel count over an electricity account base reads ~1.8x high and nothing about the
    number says so. An artefact that omits either half is not a record, it is a decoration.
    """
    basis = _commons()["basis"]
    for key in ("numerator", "denominator", "units", "denominator_count_millions"):
        assert basis.get(key), f"the commons basis omits {key!r}: a figure without its basis is R14"
    assert "electricity" in basis["numerator"].lower()
    assert "electricity" in basis["denominator"].lower()


def test_every_year_of_the_record_carries_a_band_and_the_band_is_ordered():
    """MUTATION: drop a year, or swap a lo/hi pair, and this fires.

    A missing year must not read as an unbounded one -- that is the fail-open shape that lets any
    level pass. And `lo > hi` makes every containment check below vacuously false, which would
    look like a very strict control and be an unsatisfiable one.
    """
    bands = _bands()
    missing = [y for y in _RECORD_YEARS if y not in bands]
    assert not missing, f"the commons carries no band for {missing}"
    for year, (lo, hi) in bands.items():
        assert 0.0 < lo <= hi < 100.0, f"{year}: band ({lo}, {hi}) is not an ordered rate range"


def test_the_band_is_narrower_than_the_thing_it_is_meant_to_discriminate():
    """MUTATION: widen any band to span 0-100 and this fires.

    A band wide enough to contain anything passes everything, which is the fail-open a range check
    degrades into. The world's departure level this anchor was written to judge sits at ~5% against
    a 2017-2024 published mean near 15%, so a band wider than 12pp in a non-crisis year could not
    tell the two apart and the control would report a constant.
    """
    for year, (lo, hi) in _bands().items():
        if year == 2022:
            continue  # the crisis trough is genuinely a 2.9-4.3 range; it is the narrowest here
        assert hi - lo <= 12.0, (
            f"{year}: band {lo}-{hi} spans {hi - lo:.1f}pp, wide enough to contain both the "
            f"published record and the level this anchor exists to find wrong"
        )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (b) THE LANE READINGS — inside the band, on the declared denominator
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_every_lane_reading_of_the_switching_rate_is_inside_the_published_band():
    """THE ONE THAT MATTERS. MUTATION: restore any pre-2026-08-30 value of
    `_UK_SWITCHING_RATE_PCT` -- 2021 at 6.1, 2020 at 14.2 -- and this fires.

    Keyed to the property. Moving a reading anywhere inside its year's band passes; moving it out
    fails, in either direction. It cannot be satisfied by pinning today's number, and it does not
    go red when a lane's reading is corrected toward the record.
    """
    bands = _bands()
    checked = 0
    for dotted, attr in _LANE_READINGS.items():
        table = _lane_table(dotted, attr)
        for year, value in sorted(table.items()):
            if year not in bands:
                continue  # out of window; leg (c) owns absence
            lo, hi = bands[year]
            assert lo <= value <= hi, (
                f"{dotted}.{attr}[{year}] = {value}% but the published record bears "
                f"{lo}-{hi}% (external changes of supplier on a domestic electricity meter "
                f"point, over all domestic electricity accounts). Correct the reading, or "
                f"widen the band in the commons with the publication that widens it."
            )
            checked += 1
    assert checked >= 10, (
        f"only {checked} (lane, year) pairs compared -- a control over an emptied register "
        f"reports a constant PASS"
    )


def test_a_lane_reading_covers_the_whole_published_window():
    """MUTATION: delete 2020 and 2021 from `_UK_SWITCHING_RATE_PCT` -- the two years the old table
    was most wrong about -- and this fires.

    Otherwise the cheapest way to go green above is to delete the years that fail, and a shrinking
    subject is the fail-open every parametrised control in this repo has had at least once.
    """
    for dotted, attr in _LANE_READINGS.items():
        table = _lane_table(dotted, attr)
        missing = [y for y in _RECORD_YEARS if y not in table]
        assert not missing, (
            f"{dotted}.{attr} has no entry for {missing}; the published record covers "
            f"{_RECORD_YEARS.start}-{_RECORD_YEARS.stop - 1} and a lane may not go quiet on a "
            f"year it disagrees with"
        )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (c) MUTATION LEGS — the commons is not privileged either
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_mutation_a_a_lane_reading_moved_outside_its_band_is_caught(monkeypatch):
    """Move the READING and the containment leg must fire."""
    import company.market.market_report as mr

    broken = dict(mr._UK_SWITCHING_RATE_PCT)
    broken[2021] = 6.1  # the value f5 §9 disconfirmed live
    monkeypatch.setattr(mr, "_UK_SWITCHING_RATE_PCT", broken)
    with pytest.raises(AssertionError, match="2021"):
        test_every_lane_reading_of_the_switching_rate_is_inside_the_published_band()


def test_mutation_b_a_drifting_band_is_caught(monkeypatch, tmp_path):
    """Move the COMMONS instead of the reading and the same leg must fire.

    Without this, the band is the one number in the comparison nobody checks, and the cheapest
    repair for a wrong reading becomes editing the record it is judged against.
    """
    raw = _commons()
    for row in raw["rates"]:
        if row["year"] == 2020:
            row["rate_pct_lo"], row["rate_pct_hi"] = 30.0, 35.0
    mutated = tmp_path / "gb_domestic_switching_rate.json"
    mutated.write_text(json.dumps(raw))
    # Patched on the INSTRUMENT, because the instrument is the reader. Patching a local copy here
    # would prove only that this file can read a different file.
    monkeypatch.setattr(instrument, "COMMONS", mutated)
    with pytest.raises(AssertionError, match="2020"):
        test_every_lane_reading_of_the_switching_rate_is_inside_the_published_band()


def test_mutation_c_an_emptied_lane_register_cannot_read_green(monkeypatch):
    """MUTATION: empty `_LANE_READINGS` and the non-vacuity floor must fire.

    A control whose subject list is empty passes trivially. This is the leg that makes the
    register's own shrinkage loud rather than silent.
    """
    monkeypatch.setattr(
        "tests.architecture.test_switching_rate_commons._LANE_READINGS", {}
    )
    with pytest.raises(AssertionError, match="only 0"):
        test_every_lane_reading_of_the_switching_rate_is_inside_the_published_band()
