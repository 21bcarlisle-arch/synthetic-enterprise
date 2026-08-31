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

#: `{dotted module path: attribute}` -- every MODULE-CONSTANT lane reading of the GB domestic
#: switching rate. The register exists so the second one cannot arrive unheld, which is exactly
#: how the first one got nine years wrong.
_LANE_READINGS: dict[str, str] = {
    "company.market.market_report": "_UK_SWITCHING_RATE_PCT",
    # Added 2026-08-31 when `market_conditions` stopped carrying a normalised ratio as its
    # primary form. This entry is the repair: the reading now HAS units, so the band check
    # below can reach it. It could not before, and that is the whole defect.
    "company.crm.market_conditions": "MARKET_SWITCHING_RATE_PCT_BY_YEAR",
}

#: THE PRINCIPAL SUBJECT, and it was not in the register when the register was written
#: (2026-08-30). `_LANE_READINGS` held exactly one entry: a company-side table with zero callers.
#: The thing this whole anchor was built to judge -- the rate at which households actually leave
#: in the world the company lives in -- was not a subject of the control at all. So the control
#: was GREEN on the day the instrument measured the world 3.15x outside the band, and leg (c)
#: below could only see the register being EMPTIED, never the register never having held the one
#: reading that mattered. A control whose scope omits its own principal subject is a control that
#: stays green through exactly the defect it exists for.
#:
#: It is not a module constant, so it cannot be a `_LANE_READINGS` entry: it is what the RUN did,
#: read from the captured factor table through the same instrument the gap was measured with.
_PRINCIPAL_SUBJECT = "the world's own realised departure rate (tools.measure_departure_level)"

#: `{name: (dotted, attribute, reference_year)}` -- readings held as a MULTIPLIER TABLE rather
#: than as a rate. A multiplier normalised to a reference year IS a switching-rate reading: it
#: states every year's rate as a fraction of the reference year's, so multiplying it back by the
#: record's rate for that year recovers the rate the table asserts. Holding only the rate-shaped
#: tables is how a reading hides in plain sight -- which is where this one was found, on
#: 2026-08-30, by following the thread from the world's own multiplier.
#: `{name: (dotted, multiplier_attr, reference_year, rate_attr_or_None)}` -- readings held as a
#: MULTIPLIER TABLE rather than as a rate. A multiplier normalised to a reference year IS a
#: switching-rate reading: it states every year's rate as a fraction of the reference year's, so
#: multiplying it back by that year's rate recovers the rate the table asserts. Holding only the
#: rate-shaped tables is how a reading hides in plain sight -- which is where this one was found,
#: on 2026-08-30, by following the thread from the world's own multiplier.
#:
#: `rate_attr` NAMES THE LEVEL THE RATIO IS A RATIO OF, and it is the difference between a
#: reading that can be checked and one that cannot. A module that derives its multiplier from a
#: declared absolute table is held to that derivation (leg b3) AND to the band through the
#: absolute table's own `_LANE_READINGS` entry. A module that carries a bare ratio and declares
#: no level has nothing to be multiplied back by, so it is held to the widest thing the record
#: can say -- and that weakness is the reason to declare a level, stated rather than hidden.
_MULTIPLIER_READINGS: dict[str, tuple[str, str, int, str | None]] = {
    "company.crm.market_conditions:MARKET_SWITCHING_MULTIPLIER_BY_YEAR": (
        "company.crm.market_conditions", "MARKET_SWITCHING_MULTIPLIER_BY_YEAR", 2024,
        "MARKET_SWITCHING_RATE_PCT_BY_YEAR",
    ),
}


def _reference_rate(dotted: str, reference_year: int, rate_attr: str | None) -> float:
    """The absolute rate a normalised table is normalised BY.

    THE MODULE'S OWN DECLARATION WHEN IT HAS ONE. The first version of this helper used the HIGH
    ENDPOINT of the reference year's band, which is an arbitrary point inside a 12.5-16.1 range
    and inflates every implied rate by 1.13x -- enough on its own to push a correctly-derived
    2016 reading (19.5%) outside a 17.0-17.6 band and report a defect that is the checker's. The
    endpoint was not a considered choice; it was `[1]`. Where the module declares the level it
    normalised by, that is the only rate the ratio is a ratio of. Where it does not, the midpoint
    is the non-arbitrary point and the check is correspondingly weaker -- see leg (b2).
    """
    if rate_attr is not None:
        return _lane_table(dotted, rate_attr)[reference_year]
    lo, hi = _bands()[reference_year]
    return (lo + hi) / 2.0


def _implied_rate_table(
    dotted: str, attr: str, reference_year: int, rate_attr: str | None = None
) -> dict[int, float]:
    """A normalised multiplier table read back as the rate table it asserts."""
    reference_rate = _reference_rate(dotted, reference_year, rate_attr)
    return {y: m * reference_rate for y, m in _lane_table(dotted, attr).items()}


def _world_realised_reading() -> dict[int, float]:
    """The world's realised per-renewal departure probability by year, as a percentage."""
    return instrument.world_realised_rate_pct()


def _all_readings() -> dict[str, dict[int, float]]:
    """Every reading the control holds, module constants and the world's outcome alike.

    NAME-KEYED rather than module-keyed, because the principal subject has no module attribute to
    point at and forcing it into that shape is how it got left out the first time.
    """
    readings = {
        f"{dotted}.{attr}": _lane_table(dotted, attr)
        for dotted, attr in _LANE_READINGS.items()
    }
    readings[_PRINCIPAL_SUBJECT] = _world_realised_reading()
    return readings

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


def test_the_register_names_the_worlds_own_realised_departure_rate():
    """MUTATION: remove `_PRINCIPAL_SUBJECT` from `_all_readings()` and this fires.

    THE LEG THE FIRST VERSION OF THIS FILE DID NOT HAVE. Leg (c) fires when the register is
    EMPTIED, which is the shrink-to-zero failure. It cannot see a register that was never widened
    to its principal subject -- and that, not emptying, is what actually happened here: the
    control shipped holding one company-side table with zero callers while the world's own
    departure rate, the quantity the anchor was written to judge, was outside the band and
    outside the register.

    So this asserts PRESENCE and NON-EMPTINESS of the principal subject by name. A future pass
    that finds the world's rate inconvenient has to delete a named assertion rather than quietly
    fail to add one.
    """
    readings = _all_readings()
    assert _PRINCIPAL_SUBJECT in readings, (
        "the switching-rate register no longer names the world's own realised departure rate; "
        "that omission is the defect this file was written for, not a tidy-up"
    )
    world = readings[_PRINCIPAL_SUBJECT]
    assert len(world) >= 5, (
        f"the world's realised rate covers only {len(world)} years; a principal subject narrowed "
        f"to a handful of years is the scope-shrink fail-open leg (c) guards against"
    )
    for year, value in world.items():
        assert 0.0 <= value < 100.0, f"{year}: realised departure rate {value} is not a rate"


def test_the_worlds_realised_departure_rate_is_inside_the_published_band():
    """THE ONE THE ANCHOR EXISTS FOR, AND IT IS GREEN AS OF 2026-08-30.

    IT WAS A STRICT XFAIL AND THE MARKER IS GONE, WHICH IS THE POINT OF HAVING WRITTEN IT STRICT.
    The world ran 3.15x -- then 3.45x -- below the published GB domestic switching record for the
    whole of this project's history, and the marker held that open in a form that had to break
    loudly the day the level landed rather than sit green forever. It broke on the day, and this
    is what replaced it. The reason it carried, kept here because a discharged xfail whose reason
    is deleted takes the evidence with it: no single multiplicative scale on the market term could
    reach the band, because the non-market factor product varies ~6x across years with a shape
    unrelated to the record, and the per-year divisors that would fix each year have an empty
    intersection. `simulation/departure_level_anchor.py` is what closed it.

    NOW IT IS A DRIFT DETECTOR, AND THAT IS NOT A TAUTOLOGY. The anchor is fitted, so of course the
    run it was fitted to sits in the band -- the question this asks is whether it STILL does. A
    change to the churn model, the pricing desk or the population draw moves the factor population
    out from under a fitted anchor, and nothing else in the tree would notice. The repair when it
    fires is to re-capture and re-fit (`tools/capture_departure_factors.py`,
    `tools/fit_year_level_anchor.py`), never to widen the band.

    MUTATION: halve any year in `world_realised_rate_pct()` -- the CAPTURED table's realised
    probabilities -- and this fires on that year with the margin in the message.

    AND THE MUTATION THIS DOCSTRING USED TO NAME CANNOT FIRE, established 2026-08-31 rather than
    assumed. It said *"divide any `YEAR_LEVEL_ANCHOR` entry by two"*. It does nothing: this
    control's subject is `docs/reports/c2_departure_factors.json`, a captured artefact, and the
    anchor module is not in its read path. Halving `YEAR_LEVEL_ANCHOR[2020]` leaves the control
    green because the captured table still carries `sim_level_anchor: 4.425742` from the run that
    produced it. That is not a fail-open -- the control does fire on the quantity it actually
    reads, proven above -- but a reader following the old instruction would have concluded the
    control was broken, or worse, that the anchor was safe to edit. The anchor only reaches this
    control through a RE-CAPTURE (`tools/capture_departure_factors.py`), and that indirection is
    the thing to know: this is a drift detector over a stored measurement, not a live assertion
    about the module.

    Containment is judged by the instrument's own `inside_band`, at the precision the commons
    publishes its endpoints to. See that function for why a strict float comparison here was a
    coin flip and not a control.

    ══ READ THIS BEFORE YOU READ A RED FROM IT. THIS CONTROL IS ONE-SIDED, AND THE ASYMMETRY
    FAVOURS US. ══

    `YEAR_LEVEL_ANCHOR` is fitted to each band's HIGH endpoint -- §6's deliberate anti-flattering
    tie-break, and the right choice. Its unnoticed consequence is that the world sits ON the
    ceiling in ALL TEN YEARS, so as measured 2026-08-31:

      * room ABOVE the level is 0.00pp in every year. ANY upward movement fails this, of any
        size. A +0.11pp move in the C3 arm that shifted ZERO departures -- 79 either way --
        exits the band and reads identically to a move ten times larger.
      * room BELOW is 0.50pp (2017) to 3.60pp (2023, 2024, 2025), i.e. year-dependent and set by
        how wide that year's published band happens to be. So the same size of downward change is
        caught or missed by the calendar -- and downward means FEWER departures, a stickier book,
        which is the direction that flatters us.

    So this control answers *"is the world still on its anchor"* and reads as though it answered
    *"is the world still lawful"*. Those are different questions. A red here is a threshold
    crossing and NOT a magnitude: go to `tools/measure_departure_level.py`, whose `room to LOW/HIGH`
    columns give the size, before concluding anything about how far the world moved. The failure
    message below carries those margins for the same reason.

    It is stated here rather than in a finding because this docstring is where the next reader
    hits it -- and the seat over-read exactly this red an hour after the anchor was built.
    """
    bands = _bands()
    world = _world_realised_reading()
    assert world, "no realised rate to judge -- an empty subject is not a pass"
    assert len(world) >= 8, (
        f"only {len(world)} years of realised rate to judge; a subject narrowed to a handful of "
        f"years is the scope-shrink fail-open this file's leg (c) exists for"
    )
    for year, value in sorted(world.items()):
        lo, hi = bands[year]
        below, above = instrument.band_margins(value, lo, hi)
        assert instrument.inside_band(value, lo, hi), (
            f"the world's realised departure rate at {year} is {value:.2f}% against a published "
            f"{lo}-{hi}% -- {below:+.2f}pp from the low edge, {above:+.2f}pp from the high edge. "
            f"READ THAT MARGIN BEFORE ACTING ON THIS: the anchor is fitted to the HIGH endpoint, "
            f"so room above is 0.00pp and a move of ANY size upward lands here. The level anchor "
            f"may have gone stale against a world that moved under it -- re-capture and re-fit, "
            f"do not widen the band."
        )


def test_every_multiplier_shaped_reading_implies_a_rate_inside_the_published_band():
    """THE SECOND SHAPE, AND IT IS GREEN AS OF 2026-08-31.

    IT WAS A STRICT XFAIL AND THE MARKER IS GONE, WHICH IS THE POINT OF HAVING WRITTEN IT STRICT.
    The reason it carried, kept here because a discharged xfail whose reason is deleted takes the
    evidence with it: `company/crm/market_conditions.py` carried a SECOND company-side reading of
    the same published series, shaped as a 2024-normalised multiplier and therefore invisible to
    a register that only held rate tables. Its docstring said it was "derived from the same public
    switching-rate series"; read back against the record it asserted 31.0% for 2016 (published
    17.0-17.6%) and 13.6% for 2020 (published 22.5-23.0%), and it correlated with the record at
    0.40 over 2016-2025 and at MINUS 0.47 over 2016-2021 -- falling monotonically to 2022 while
    the record rose to its 2020 peak. It was a LIVE prior: `competitive_pressure` scales every
    enriched churn estimate by it and derives `PRIOR_LOG_VARIANCE` from its dispersion.

    THE CLASS THIS FILE WAS WRITTEN FOR, ONE SHAPE ALONG. The opening defect was a rate table
    nobody compared with the record. That was the same defect wearing a ratio: a table whose
    numbers looked like 0.95 and 2.17 rather than 14.2 and 17.0, and which therefore passed every
    eye that knew to check percentages against a published band.

    MUTATION: give any multiplier entry a hand-authored value off the record -- 2020 back to 0.95
    -- and this fires on that year.
    """
    bands = _bands()
    checked = 0
    for name, (dotted, attr, reference_year, rate_attr) in _MULTIPLIER_READINGS.items():
        implied = _implied_rate_table(dotted, attr, reference_year, rate_attr)
        for year, value in sorted(implied.items()):
            if year not in bands:
                continue
            lo, hi = bands[year]
            assert instrument.inside_band(value, lo, hi), (
                f"{name}[{year}] implies {value:.1f}% against a published {lo}-{hi}%"
            )
            checked += 1
    assert checked >= 10, (
        f"only {checked} (multiplier, year) pairs compared -- a control over an emptied register "
        f"reports a constant PASS"
    )


def test_a_multiplier_reading_that_declares_a_level_is_the_normalisation_of_that_level():
    """MUTATION: replace the derived comprehension in `market_conditions` with the ten literals it
    replaced -- or with any nine of them plus one hand-edited entry -- and this fires.

    WHY THIS LEG EXISTS AND WHY IT IS NOT A TAUTOLOGY. Above holds the implied rate to the band.
    On a module that DECLARES the level it normalised by, that check reads the declared level
    back through its own reference year, so it would still pass if somebody replaced the derived
    ratios with hand-authored ones that happened to land in band -- the band is 12.5-16.1 wide at
    2024 and 8.9-12.5 at 2023, which is room for a lot of authored numbers. This asserts the
    DERIVATION instead: every entry equals the declared rate over the reference year's rate,
    exactly. It has a real FAIL branch -- the pre-2026-08-31 literals fail it at every year but
    2024 -- and it is the only leg that can see the repair being undone, because undoing it means
    replacing a comprehension with a literal, which no band check can notice.

    It also asserts the declared level is itself registered as a lane reading. A module could
    otherwise satisfy this leg by declaring a level nothing holds to the record, which would move
    the defect one hop rather than close it.
    """
    checked = 0
    for name, (dotted, attr, reference_year, rate_attr) in _MULTIPLIER_READINGS.items():
        if rate_attr is None:
            continue
        assert _LANE_READINGS.get(dotted) == rate_attr, (
            f"{name} declares {rate_attr} as the level it normalises by, but that table is not "
            f"in `_LANE_READINGS` and so is held to no published band. A declared level nothing "
            f"checks moves the defect one hop instead of closing it."
        )
        rates = _lane_table(dotted, rate_attr)
        multipliers = _lane_table(dotted, attr)
        assert set(rates) == set(multipliers), (
            f"{name} covers {sorted(set(multipliers) ^ set(rates))} differently from the level it "
            f"claims to normalise; a ratio table that has drifted in COVERAGE has been authored"
        )
        reference_rate = rates[reference_year]
        for year, m in sorted(multipliers.items()):
            assert m == pytest.approx(rates[year] / reference_rate, rel=1e-12), (
                f"{name}[{year}] = {m!r} but {rate_attr}[{year}]/{rate_attr}[{reference_year}] "
                f"= {rates[year] / reference_rate!r}. The multiplier is no longer the "
                f"normalisation of the level it declares -- a hand-authored ratio is back, which "
                f"is exactly how this module got six years of the record's shape inverted."
            )
            checked += 1
    assert checked >= 10, (
        f"only {checked} derived entries compared -- an emptied register reports a constant PASS"
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


def test_mutation_d_dropping_the_principal_subject_from_the_register_is_caught(monkeypatch):
    """MUTATION: return a register WITHOUT the world's own rate -- the state this file actually
    shipped in -- and the presence leg must fire.

    Distinct from leg (c) and that distinction is the point. (c) mutates the register to EMPTY,
    which a non-vacuity floor catches. This mutates it to a register that is full, plausible, and
    silent about the one subject the anchor was built for. The first version of this file passed
    that mutation, which is why it was green on the day the world was measured 3.15x out.
    """
    monkeypatch.setattr(
        instrument, "world_realised_rate_pct", lambda *a, **k: {},
    )
    monkeypatch.setattr(
        "tests.architecture.test_switching_rate_commons._all_readings",
        lambda: {
            f"{d}.{a}": _lane_table(d, a) for d, a in _LANE_READINGS.items()
        },
    )
    with pytest.raises(AssertionError, match="no longer names the world's own"):
        test_the_register_names_the_worlds_own_realised_departure_rate()


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (e) THE MARGIN — a threshold crossing is not a magnitude, and the instrument must say which
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_the_instrument_prints_the_distance_to_both_band_edges_and_not_only_the_verdict():
    """MUTATION: delete either margin column from `measure_departure_level.main()`'s table, or
    drop the RESOLUTION paragraph, and this fires.

    THE DEFECT THIS EXISTS FOR, found 2026-08-31 as a by-product of the C3 counterfactual. The
    anchor is fitted to each band's HIGH endpoint, so the world sits on the ceiling in all ten
    years and there is ZERO room above. `inside_band` therefore returns the same verdict for a
    +0.11pp move that shifted no departures at all and for one ten times larger, and a reader --
    including the seat, an hour after the anchor was built -- over-reads the red as "the world
    left the lawful range". The distance is the only thing that can tell those apart, and until
    this landed nothing in the tree printed it.

    Keyed to the PROPERTY, not to today's answer: it asserts the margins are PRESENT, are the
    ones `band_margins` computes, and that the summary states the resolution in both directions.
    It does not assert the room above is 0.00 -- that would be a control pinned to the current
    fit, which would go red the day somebody re-aims the anchor at the band midpoint and give
    exactly the backwards signal this project has repaired repeatedly.

    WHAT THIS LEG CANNOT SEE, and it is why the next test exists. It compares the printed row
    against `band_margins`, and `main()` computes the row with that same function -- so a change
    to `band_margins` ITSELF moves both sides together and passes here. Proven, not assumed:
    making `band_margins` return unsigned distances leaves this green. That is a bounded
    tautology rather than a defect -- this leg's subject is whether the instrument still PRINTS
    the distance -- but the signedness needs a leg with an independent expectation, and
    `test_band_margins_are_signed_distances_and_go_negative_outside_the_band` is it.
    """
    import io
    from contextlib import redirect_stdout

    out = io.StringIO()
    with redirect_stdout(out):
        instrument.main(["measure_departure_level"])
    text = out.getvalue()

    assert "room to" in text and "LOW" in text and "HIGH" in text, (
        "the instrument's table no longer names a distance to each band edge; a verdict without "
        "its magnitude is the defect this leg exists for"
    )
    assert "RESOLUTION OF THIS CONTROL" in text, (
        "the instrument no longer states what size of movement it could have detected -- the "
        "one-sidedness is back to being invisible"
    )

    bands = _bands()
    world = _world_realised_reading()
    checked = 0
    for year, value in sorted(world.items()):
        lo, hi = bands[year]
        below, above = instrument.band_margins(value, lo, hi)
        line = next((ln for ln in text.splitlines() if ln.strip().startswith(str(year))), None)
        assert line is not None, f"the instrument's table no longer carries a row for {year}"
        assert f"{below:+.2f}" in line and f"{above:+.2f}" in line, (
            f"{year}: the row {line.strip()!r} does not carry both margins "
            f"({below:+.2f}, {above:+.2f}) that `band_margins` computes for it"
        )
        checked += 1
    assert checked >= 8, (
        f"only {checked} years had their margins checked -- a control over an emptied subject "
        f"reports a constant PASS"
    )


def test_band_margins_are_signed_distances_and_go_negative_outside_the_band():
    """MUTATION: return `abs()` of either margin, or clamp them at zero, and this fires.

    The sign is load-bearing. A margin reported as an unsigned distance cannot distinguish "0.4pp
    of room left" from "0.4pp outside already", which is the whole quantity the caller needs. It
    is the containment-check-degrading-into-a-range-check shape one level down.
    """
    assert instrument.band_margins(15.0, 12.5, 16.1) == (2.5, 1.1)
    assert instrument.band_margins(16.1, 12.5, 16.1) == (3.6, 0.0)   # on the ceiling: no room up
    assert instrument.band_margins(12.5, 12.5, 16.1) == (0.0, 3.6)   # on the floor: no room down
    below, above = instrument.band_margins(16.6, 12.5, 16.1)
    assert above < 0.0, "a level ABOVE the band must report negative room above, not a distance"
    assert below > 0.0
    below, above = instrument.band_margins(11.0, 12.5, 16.1)
    assert below < 0.0, "a level BELOW the band must report negative room below, not a distance"
    assert above > 0.0
