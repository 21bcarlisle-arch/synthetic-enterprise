"""Every lane's reading of the GB domestic switching rate sits inside the PUBLISHED band.

Commons: `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`.
Write-up: `docs/market_research/gb_switching_rate_denominators.md`.
Opened by: `docs/staging/done/WORKER_FINDING_THE_WORLDS_DEPARTURE_LEVEL_HAS_NEVER_BEEN_CHECKED_AGAINST_A_PUBLISHED_RATE_2026-08-30.md`.

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

import ast
import importlib
import json
import re
import sys
from pathlib import Path

import pytest

import simulation.departure_level_anchor as anchor_module
import simulation.departure_risks as departure_risks
import simulation.market_switching_propensity as propensity
import tools.departure_population as departure_population
import tools.fit_year_level_anchor as fitter
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
    # Added 2026-08-31 with the scope widening below. The BOARD's reading, and it was outside
    # every census in the repository: `tools/population_anchor.py` ran on every sim run, wrote
    # `site/state/population_anchoring.json` and reached the annual report, carrying ten
    # hand-authored rates (2020 at 14% against 22.5-23.0) under a comment claiming a dual-fuel
    # denominator. One published series, three implementations, one of them repaired -- the VAT
    # class, reproduced inside twenty-four hours of the rule being written.
    "tools.population_anchor": "OFGEM_SWITCHING_RATE_PCT_BY_YEAR",
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
#:
#: THE NAME CARRIES THE ROUTE, AND IT DID NOT UNTIL 2026-08-31. It read *"the world's own realised
#: departure rate"* -- a WHOLE-BOOK name on a reading that is a mean over renewal DECISIONS. C1b
#: gave the world a second way to leave and the register kept the old name, so every green in this
#: file read as a statement about the book when it was a statement about the households that reach
#: a renewal roll: 39% of the departures on the two-route capture. The band it is judged against
#: counts every domestic electricity account. Those are different quantities and the register was
#: the only place a reader would have seen which one they had.
#:
#: `_SUBJECT_ROUTE_QUALIFIERS` below is what holds the name honest, and the leg that reads it takes
#: its cue from the INSTRUMENT'S OWN DECLARATION rather than from this string -- so the day a
#: two-route capture becomes the subject, the requirement lifts by construction instead of needing
#: someone to remember it.
_PRINCIPAL_SUBJECT = (
    "the world's own realised departure rate, RENEWAL DECISIONS ONLY "
    "(tools.measure_departure_level)"
)

#: Any one of these in the principal subject's register key counts as naming the route. A LIST and
#: not one exact string: pinning the key to today's wording would make every honest re-phrasing a
#: red, which is the pinned-to-the-answer shape this file exists to avoid. What must not be
#: possible is a whole-book name on a partial-route reading.
_SUBJECT_ROUTE_QUALIFIERS = ("renewal decision", "renewal-decision", "renewal route")

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
    # The board-facing twin, and it was a BYTE-IDENTICAL COPY of the company's refuted table
    # until 2026-08-31 -- 2016: 2.17, 2020: 0.95, 2022: 0.44. The old docstring in
    # `company/crm/market_conditions.py` said the multiplier "matches the calibration already
    # published for board-facing population anchoring", and it did. That was the defect, not the
    # reassurance: correcting one copy leaves the other asserting the opposite shape about one
    # published series. It now derives from `OFGEM_SWITCHING_RATE_PCT_BY_YEAR` and leg (b3) holds
    # it to that derivation, so a hand-authored ratio cannot come back silently.
    "tools.population_anchor:CALIBRATED_MULTIPLIER": (
        "tools.population_anchor", "CALIBRATED_MULTIPLIER", 2024,
        "OFGEM_SWITCHING_RATE_PCT_BY_YEAR",
    ),
}


#: THE THIRD SHAPE, and it is the one both registers above were structurally unable to hold
#: (added 2026-08-31). `_LANE_READINGS` and `_MULTIPLIER_READINGS` are both keyed to MODULE
#: CONSTANTS. A module that serves the switching level through a FUNCTION and keeps no constant at
#: all is invisible to both -- and that is not hypothetical, it is where the world's own reading
#: lives: `simulation/market_switching_propensity` loads the commons inside a cached function and
#: exposes `market_departure_rate_pct(year)`. It was held by nothing here.
#:
#: `{name: (dotted, callable_attr, to_pct)}` -- callables of one year returning a rate, with the
#: factor that puts it in PER CENT. The factor is declared per entry rather than inferred, because
#: inferring it from the magnitude is exactly the mistake that makes a 100x error look like a
#: units convention: `market_departure_rate` returns 0.176 and `market_departure_rate_pct` returns
#: 17.6, and a checker that guessed would report both as fine forever.
_CALLABLE_READINGS: dict[str, tuple[str, str, float]] = {
    "company.market.market_report:get_switching_rate": (
        "company.market.market_report", "get_switching_rate", 1.0,
    ),
    "simulation.market_switching_propensity:market_departure_rate_pct": (
        "simulation.market_switching_propensity", "market_departure_rate_pct", 1.0,
    ),
    # The FRACTION form of the line above, and the census found it unregistered on its first run
    # (2026-08-31) -- a sibling accessor for the same quantity in different units. Registered
    # rather than exempted: it is the form `simulation/renewals.py` actually consumes, so it is
    # the one a defect would travel through.
    "simulation.market_switching_propensity:market_departure_rate": (
        "simulation.market_switching_propensity", "market_departure_rate", 100.0,
    ),
}

#: `{name: (dotted, callable_attr, reference_year, level_attr)}` -- callables returning a
#: MULTIPLIER, each naming the attribute on the SAME module that carries the level it normalises
#: by. Same doctrine as `_MULTIPLIER_READINGS`: a ratio is only checkable against a publication
#: once the level it is a ratio OF is named. `level_attr` may be a dict or a callable -- the
#: company declares its level as a table and the world as a function, and forcing either into the
#: other's shape would mean adding production code to satisfy a test.
_CALLABLE_MULTIPLIER_READINGS: dict[str, tuple[str, str, int, str]] = {
    "company.crm.market_conditions:market_conditions_multiplier": (
        "company.crm.market_conditions", "market_conditions_multiplier", 2024,
        "MARKET_SWITCHING_RATE_PCT_BY_YEAR",
    ),
    "simulation.market_switching_propensity:market_switching_multiplier": (
        "simulation.market_switching_propensity", "market_switching_multiplier", 2024,
        "market_departure_rate_pct",
    ),
}


#: THE FOURTH SHAPE (added 2026-08-31): a table that is another registered table in DIFFERENT
#: UNITS. `_CALLABLE_READINGS` already carries an explicit `to_pct` factor for exactly this, with
#: the reason stated there -- inferring units from magnitude is what makes a 100x error look like
#: a convention -- but the dict registers had no equivalent, so a fraction-shaped table had
#: nowhere to go but `_NOT_A_LEVEL_READING`, and calling a switching rate "not a level reading"
#: because it is written as 0.228 rather than 22.8 would be false in the register that exists to
#: stop exactly that.
#:
#: `{name: (dotted, derived_attr, source_attr, factor)}` -- `derived[y] == source[y] * factor`.
#: Held by the DERIVATION rather than by the band, because a fraction cannot be compared with a
#: per-cent band without picking a factor, and picking one is the mistake. The source is held to
#: the band by `_LANE_READINGS`, so the pair is closed.
_UNIT_DERIVED_READINGS: dict[str, tuple[str, str, str, float]] = {
    "tools.population_anchor:OFGEM_SWITCHING_RATE": (
        "tools.population_anchor", "OFGEM_SWITCHING_RATE",
        "OFGEM_SWITCHING_RATE_PCT_BY_YEAR", 0.01,
    ),
}


def _lane_callable(dotted: str, attr: str):
    return getattr(importlib.import_module(dotted), attr)


def _level_at(dotted: str, level_attr: str, year: int) -> float:
    """The declared level for `year`, whether the module declares it as a table or a function."""
    level = getattr(importlib.import_module(dotted), level_attr)
    return float(level(year)) if callable(level) else float(dict(level)[year])


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


def _capture_decisions_by_year() -> dict[int, int]:
    """Renewal decisions per year, counted STRAIGHT OFF THE CAPTURE.

    THE SECOND READER, and it is deliberately not `instrument.world_outcome`. The legs that accept
    a refused year need something the refusing module did not also produce, or the corroboration is
    the producer agreeing with itself. This is the cheapest independent statement of the same fact:
    one row is one renewal decision, so the count is a length.
    """
    rows = json.loads(instrument.DEFAULT_TABLE.read_text())
    counts: dict[int, int] = {}
    for row in rows:
        year = int(row["event_date"][:4])
        counts[year] = counts.get(year, 0) + 1
    return counts


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


@pytest.mark.xfail(strict=True, reason=(
    "RE-INSTATED 2026-09-01, having been discharged on 2026-08-30. The world is OUT OF BAND in "
    "7 of the 7 readable years -- 2017 -1.10pp, 2018 -5.80pp, 2019 -6.80pp, 2020 -15.90pp, "
    "2021 -5.00pp, 2023 -6.10pp, 2024 -6.20pp. It is held open STRICT so the re-fit that repairs "
    "it breaks this loudly instead of leaving it quietly green, which is the same reason the "
    "marker was written strict the first time. "
    "AND THE DIRECTION IS SIX ABOVE AND ONE BELOW, ADDED 2026-09-02 -- the seven margins above "
    "are correct and are UNCHANGED, but they were quoted as bare negatives and a bare negative "
    "does not say which edge. `band_margins` returns `(value-lo, hi-value)`, so this list is "
    "whichever element came back negative, and it is the HIGH element in six years and the LOW "
    "element only in 2023. Measured at this marker's own commit f97c34eb0 and again at HEAD, from "
    "the same byte-identical capture: 2017 15.12%, 2018 25.77%, 2019 28.10%, 2020 38.89%, 2021 "
    "23.40%, 2024 22.34% all sit ABOVE their high edge, and only 2023 at 2.81% sits below its "
    "low edge. THIS IS WHY THE DIRECTION MATTERS MORE THAN THE MAGNITUDE HERE: every surrounding "
    "narrative in this tree -- the anchor module's docstring, the 3.45x-short framing, the whole "
    "argument that the block moves the world AGAINST the company -- primes a reader to read "
    "'-15.90pp' as 15.9pp SHORT of the record. It is 15.9pp OVER it. A re-fit that discharges "
    "this leg must LOWER the anchor in six years and raise it in one; a reader who took the "
    "sign on trust would move all seven the wrong way in six cases. "
    "THE CAUSE IS A CAPTURE SWAP, NOT A WORLD DRIFT, AND IT IS ATTRIBUTABLE. On the capture this "
    "control was discharged against (465 rows, b46318106^) all EIGHT comparison years are inside "
    "the band, each sitting exactly on its high endpoint -- the anchor's own fit. b46318106 "
    "replaced it with the 148-row anchored capture, on which the same code fails every year. That "
    "one commit ALSO emptied 2022 (C1b routes the crisis year's forced-passive rolls to the SVT "
    "table), which made the file's old `assert len(world) >= 8` fire FIRST -- so the commit that "
    "broke this verdict installed, in the same change, the assertion that hid the break. "
    "DISCHARGED BY: re-fitting YEAR_LEVEL_ANCHOR against the committed capture, and 2022 must be "
    "excluded from that fit because it is unidentified (see _HELD_INDIRECTLY). NEVER by widening "
    "the band and never by re-keying this leg to today's readings. "
    "Finding: docs/staging/done/WORKER_FINDING_THE_ANCHORS_ONLY_ACCOUNTABILITY_ROUTE_HAS_BEEN_"
    "BLIND_TO_2022_SINCE_THE_CAPTURE_WAS_SWAPPED_2026-09-01.md "
    "(citation corrected 2026-09-01: this reason cited a filename that was never written, and "
    "because it is SPLIT ACROSS TWO STRING LITERALS no grep of this file's source could see the "
    "path. `test_every_document_this_file_cites_is_a_document_that_exists` reads the assembled "
    "marker reasons at runtime and now holds it.)"
))
def test_the_worlds_realised_departure_rate_is_inside_the_published_band():
    """THE ONE THE ANCHOR EXISTS FOR. GREEN 2026-08-30, RE-MARKED XFAIL 2026-09-01.

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

    WHY THE MARKER CAME BACK, AND IT IS NOT THE COVERAGE DEFECT NEXT DOOR. Until this commit the
    leg opened with `assert len(world) >= 8`, which fired first on every run because 2022 is
    unreadable. Re-keying that assertion to the property did NOT turn this green -- it revealed
    what the count had been standing in front of: **7 of the 7 readable years are OUT OF BAND**,
    2017 by -1.10pp through 2020 by -15.90pp.

    AND THE TWO ARE THE SAME COMMIT, WHICH IS THE PART WORTH CARRYING. `b46318106` swapped the
    465-row capture for the 148-row anchored one. On the old capture all eight comparison years are
    INSIDE the band, each exactly on its high endpoint. On the new one every year is outside. The
    same swap emptied 2022 -- so the change that broke this verdict also installed the assertion
    that hid the break, and the file's red said "the subject shrank" for as long as the real answer
    was "the anchor is stale against the capture it is now read with".

    So the drawn premise -- that the count keying was the defect -- is refuted here. It was ONE of
    two defects and the smaller one. The coverage property now has its own control
    (`test_every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause`), green and
    mutation-proven. This leg is held open STRICT rather than left failing, for the reason its own
    first marker gave: a verdict that cannot yet be taken should break loudly the day it can be.
    Do NOT widen the band and do NOT re-key this to today's readings.
    """
    bands = _bands()
    readings, refusals = instrument.realised_rate_coverage()
    expected = [y for y in instrument.COMPARISON_YEARS if y in bands]
    assert expected, "no comparison year carries a published band -- an empty subject is not a pass"

    # AN INDEPENDENT READ OF THE CAPTURE, and the whole non-tautology of the leg below rests on it.
    # `realised_rate_coverage` both decides a year is unreadable AND supplies the reason; a leg that
    # accepted its own subject's excuse would let the producer retire any year it liked by naming it
    # refused. So the excuse is checked against the artefact, through a different reader.
    decisions = _capture_decisions_by_year()

    for year in expected:
        if year in refusals:
            # A REFUSED YEAR IS CORROBORATED, NEVER TAKEN ON TRUST. The only refusal this leg
            # accepts is one the capture itself demonstrates: no renewal decision to average.
            # A year with decisions that the producer declines to read is a subject being
            # narrowed, which is the exact shape this leg exists to catch.
            assert decisions.get(year, 0) == 0, (
                f"{year} is refused a reading -- {refusals[year]} -- but the capture carries "
                f"{decisions[year]} renewal decisions for it. A refusal whose stated cause the "
                f"artefact contradicts is a subject being narrowed under cover of a reason."
            )
            continue
        assert year in readings, (
            f"{year} is a comparison year with a published band and it is in NEITHER the readings "
            f"nor the refusals -- it was dropped silently. That is the emptied-subject fail-open: "
            f"the loop below would simply have run one year shorter and still reported PASS."
        )
        value = readings[year]
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


def _capture_anchor_column() -> dict[int, set[float]]:
    """`{market year: the distinct `sim_level_anchor` values the capture recorded for it}`.

    A SET AND NOT A VALUE, because collapsing it to one would hide the case worth catching: a
    capture assembled from two runs under different tables carries both, and a reader taking
    `[0]` or the mean would report a clean number for a mixed artefact.
    """
    column: dict[int, set[float]] = {}
    for row in json.loads(instrument.DEFAULT_TABLE.read_text()):
        column.setdefault(int(row["market_year"]), set()).add(round(row["sim_level_anchor"], 6))
    return column


def test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor():
    """THE ANCHOR'S ONLY CONTROL THAT DOES NOT NEED A RE-CAPTURE TO NOTICE AN EDIT.

    THE HOLE THIS CLOSES, MEASURED TWICE. `4871e53ee` established 2026-09-01 that halving every
    `YEAR_LEVEL_ANCHOR` entry -- a 2x error, larger than the 1.98x fallback that started the
    thread -- leaves this whole file green. Re-measured on a clean `4013b1de1` stem 2026-09-02,
    after `d374b1977` added five legs: still `81 passed, 2 xfailed`, byte-identical to unmutated.
    Five new legs and the table was still holdable by nothing.

    The cause is not a fail-open in the band leg above and that leg is not weakened here. Its
    subject is the STORED capture `docs/reports/c2_departure_factors.json`, which carries the
    `sim_level_anchor` of the run that produced it, so `departure_level_anchor` is not in its read
    path at all. Every document in this thread says so correctly. What none of them noticed is that
    a capture recording the anchor it ran under is not opaque about it: it states, per row, which
    table produced it. **The band verdict cannot be attributed to the live table unless the live
    table is the one that produced the capture it is read from**, and that is checkable here, now,
    with no re-capture and no re-fit.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER, and the distinction is the reason this is not the
    re-keying the anchor's xfail markers forbid. It pins no anchor to a number. A re-fit that lands
    a new block AND the re-capture it was fitted on moves both sides together and passes. An edit
    to the table without a re-capture fails, which is exactly the state in which the band leg's
    verdict is being read off a run some other table produced -- `figures_on_a_superseded_clock`,
    the class this thread already found twice on this same file: the ten-year block's citation
    resolved to a capture its own successor produced, under a stable path over a moving run.

    IT DRIVES THE ACCESSOR, NOT THE TABLE, and that is deliberate. `year_level_anchor` is what the
    world calls on its hot path (`customer_events:610`, `run_phase2b:1634/1667/1719`), so comparing
    against it covers the fitted years and the declared-unfitted ones in one statement, and a
    change to the PARTITION -- a year moving between `YEAR_LEVEL_ANCHOR` and `UNFITTED_YEARS`, or
    `NO_LEVEL_CORRECTION` changing value -- is caught by the same leg rather than needing another.

    WHAT IT DOES NOT CLAIM. It does not say the anchor is well fitted; the band leg above is what
    judges that, and it is held open xfail. It says only that the two artefacts are the same
    generation, which is the precondition for that judgement meaning anything. Scope, measured
    2026-09-02: the capture carries 9 of the 10 record years (2016 n=1, 2017 n=20, 2018 n=20,
    2019 n=16, 2020 n=18, 2021 n=23, 2023 n=17, 2024 n=17, 2025 n=16). **2022 is absent entirely**,
    so this leg says nothing about it -- and cannot, for the reason `6fc06b535` established: the
    year is 100% crisis-forced-passive, C1b routes every roll to the SVT table, and the slot is
    inert. A control cannot hold a year the artefact does not contain, and saying so here is
    cheaper than a reader inferring coverage this leg does not have.

    MUTATION, both sides proven under `python3 -B` rather than argued:
      * halve any `YEAR_LEVEL_ANCHOR` entry -- fires on that year (the case the whole file was
        blind to);
      * move a year between `YEAR_LEVEL_ANCHOR` and `UNFITTED_YEARS` -- fires;
      * edit one row's `sim_level_anchor` in the capture -- fires, so the verdict is not driven
        from the module side alone;
      * unmutated -- green, so the pass branch is reachable and this is not a constant verdict.
    """
    column = _capture_anchor_column()
    assert column, (
        f"the capture at {instrument.DEFAULT_TABLE} carries no `sim_level_anchor` column at all, "
        f"so nothing here can tell which anchor produced the band verdict read from it. An empty "
        f"subject is not a pass: this leg exists because the module is otherwise unheld."
    )
    assert len(column) >= 8, (
        f"only {len(column)} years carry an anchor column ({sorted(column)}) -- a subject narrowed "
        f"to a handful of years is the scope-shrink fail-open this file's leg (c) exists for."
    )

    for year, recorded in sorted(column.items()):
        assert len(recorded) == 1, (
            f"the capture records {len(recorded)} different anchors for {year} -- "
            f"{sorted(recorded)}. It is not one run under one table, so no single verdict read "
            f"from it can be attributed to any anchor at all."
        )
        was_run_under = next(iter(recorded))
        live = anchor_module.year_level_anchor(year)
        assert abs(was_run_under - live) < 1e-6, (
            f"the capture the band verdict is read from ran {year} at an anchor of "
            f"{was_run_under}, and `year_level_anchor({year})` returns {live} today. The band leg "
            f"reads that stored capture, so its verdict for {year} is a measurement of a world "
            f"the live table did not produce -- a stable path over a moving run. Re-capture with "
            f"`tools/capture_departure_factors.py` so the two are one generation again; do NOT "
            f"edit this expectation to the capture, and do NOT widen the band."
        )


def test_the_anchors_fit_window_is_the_window_the_comparison_is_taken_over():
    """THE DEFECT: one requirement, two declarations, and nothing able to notice them diverge.

    `simulation.departure_level_anchor.FIT_COMPARISON_WINDOW` duplicates
    `tools.measure_departure_level.COMPARISON_YEARS` on purpose -- `simulation/` must not acquire a
    `tools/` edge on its import graph, and the world layer cannot ask a publishing tool what its own
    fit is scoped to. Duplication is the right call and the unheld duplicate is not: this project's
    most expensive recurring shape is one legal requirement with five implementations and a defect
    fixed in one of them.

    AND THIS PAIR IS LOAD-BEARING IN BOTH DIRECTIONS. The anchor uses the window to decide whether
    an unfitted record year applies NO level correction (inside: the fit claimed it and could not
    identify it) or takes the reference year's anchor (outside: the fit never claimed it). The
    instrument uses it to decide which years the band comparison averages over. If they drift, a
    year is judged by a comparison the fit never targeted, or excused by a scope the comparison
    does not grant -- and 2016 and 2025 are exactly the years that turn on it.

    MUTATION: change either constant's endpoints and this fires naming both. Proven with `python3
    -B`.
    """
    assert list(anchor_module.FIT_COMPARISON_WINDOW) == list(instrument.COMPARISON_YEARS), (
        f"the anchor's fit window {anchor_module.FIT_COMPARISON_WINDOW} and the comparison window "
        f"{instrument.COMPARISON_YEARS} have diverged. One of them was edited and the other was "
        f"not; the anchor decides 2016/2025's fallback by the first and the band comparison "
        f"selects its years by the second, so they cannot be allowed to disagree."
    )


def test_every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause():
    """THE COVERAGE PROPERTY, keyed to the property and NEVER to how many years there are today.

    MUTATION: make `realised_rate_coverage` drop an unreadable year from BOTH returns instead of
    refusing it (the state `world_realised_rate_pct` is in, and the state this whole file was in
    until 2026-09-01) and this fires by name. Mutation-proven with `python3 -B`.

    WHAT THE OLD SHAPE WAS AND WHY IT COULD NOT WORK. The leg above used to open with
    `assert len(world) >= 8`. That is keyed to today's subject size, so it goes red when the world
    honestly loses a year and green again the moment someone edits the 8 -- backwards on both
    sides. Worse, it answers a question nobody asked: eight is not a property of anything, it is
    the number of years the capture happened to carry the day it was written.

    THE PROPERTY IS: every year the published record bands AND the comparison window covers either
    has a reading, or is REFUSED BY NAME with a cause the artefact itself corroborates. Nothing is
    dropped. A year cannot leave the subject quietly, which is the only way an emptied subject can
    reach a constant PASS.

    AND THE CORROBORATION IS THE LOAD-BEARING HALF. `realised_rate_coverage` both decides a year is
    unreadable and writes the reason, so a leg that accepted the reason on trust would let the
    producer retire any inconvenient year by naming it refused -- the refusal-names-a-cause-never-
    observed shape this repository has a catalogue entry for. The count comes off the capture
    through a second reader (`_capture_decisions_by_year`), so a refusal is only honoured when the
    artefact shows there was genuinely nothing to average.

    TODAY THE ONE REFUSED YEAR IS 2022, AND ITS CAUSE IS A MECHANISM, NOT AN ACCIDENT. 2022 is
    100% crisis-forced-passive (`simulation.renewal_engagement.CRISIS_PASSIVE_YEARS`); since C1b
    every passive roll is settled on the SVT segment route instead of a renewal roll; so the
    renewal capture carries ZERO 2022 decisions. It is permanent while those two hold, not a gap
    a re-capture fills -- `b46318106`'s predecessor capture carried 54 decisions that year.
    """
    bands = _bands()
    readings, refusals = instrument.realised_rate_coverage()
    expected = [y for y in instrument.COMPARISON_YEARS if y in bands]
    assert expected, "no comparison year carries a published band -- an empty subject is not a pass"

    decisions = _capture_decisions_by_year()
    assert not (set(readings) & set(refusals)), (
        f"{sorted(set(readings) & set(refusals))} are BOTH read and refused -- the two returns are "
        f"a partition of the comparison window, and a year in both makes the coverage count "
        f"unreadable in either direction"
    )
    for year in expected:
        assert year in readings or year in refusals, (
            f"{year} is inside the comparison window and the published record bands it, and it is "
            f"in neither the readings nor the refusals. It left the subject SILENTLY -- which is "
            f"the whole defect: every consumer keeps iterating what is left, and a control that "
            f"counts what it checked reports a smaller PASS instead of a failure."
        )
        if year in refusals:
            assert decisions.get(year, 0) == 0, (
                f"{year} is refused with the cause {refusals[year]!r}, but the capture carries "
                f"{decisions[year]} renewal decisions for it. The refusal's stated cause is "
                f"contradicted by the artefact it claims to describe."
            )
            assert str(year) in refusals[year], (
                f"{year}'s refusal does not name the year it is about: {refusals[year]!r}. A "
                f"refusal a reader cannot attribute to a year is not on the surface in any useful "
                f"sense."
            )


#: The PRESENT-TENSE grammar for a live floor claim inside an `UNFITTED_YEARS` cause. A superseded
#: claim is quoted in the PAST tense (`floor was X%`) and is deliberately outside this pattern:
#: the entries keep their own corrected history beside them, and a leg that could not tell a
#: quotation from a claim would force the history to be deleted to stay green.
_LIVE_FLOOR_CLAIM = re.compile(r"SVT floor is ([0-9.]+)% against a published ([0-9.]+)%")

#: The capture this leg re-drives, and it is deliberately NOT `instrument.DEFAULT_TABLE`.
#:
#: THIS LEG NEEDS A PAIR AND THE BAND LEG NEEDS A TABLE, WHICH IS WHY THEY READ DIFFERENT FILES.
#: `_live_svt_floor_pct` below needs the renewal rows AND the SVT sibling, because the floor is a
#: numerator on one route over an account denominator that spans both. `instrument.DEFAULT_TABLE`
#: (`c2_departure_factors.json`) has **no committed sibling** -- it never did; the run that produced
#: it carried no SVT recorder. Until 2026-09-02 this leg read `svt_sibling(DEFAULT_TABLE)` anyway
#: and was GREEN in the worktree that wrote it and RED at clean HEAD from the instant it landed,
#: because that worktree held an untracked sibling. Re-driving `ladder`'s sibling reproduces its
#: 2.34% exactly, which is what the untracked file was.
#:
#: AND PAIRING `c2`'s RENEWAL ROWS WITH A FOREIGN SIBLING WOULD NOT HAVE BEEN THE REPAIR EITHER.
#: `capture_departure_factors`'s own docstring forbids it: two files from different runs describe
#: different populations, so a cell differenced across them measures the POPULATION and not the
#: hazard -- and the account denominator here is exactly such a cell.
#:
#: So this points at the first capture on disk whose two files describe ONE run with EVERY producer
#: committed (the SVT recorder at `6db30a350`, the SVT assignment at `8bf416115`), taken from a
#: clean `git archive HEAD` stem of `19e68169b`. The band leg is deliberately left on
#: `DEFAULT_TABLE`: moving a control's subject in the commit that repairs a different control is how
#: a moved number becomes unattributable.
_FLOOR_CAPTURE = (
    Path(__file__).resolve().parents[2]
    / "docs" / "reports" / "c4_whole_book_departure_factors.json"
)


def _live_svt_floor_pct() -> dict[int, float]:
    """`{year: SVT-route floor as a % of accounts}`, recomputed under the hazard the world HAS.

    NOT the capture's own `realized_churn_probability` column, and that is the entire point. Those
    probabilities were produced by whatever hazard ran the day the capture was taken, so a claim
    checked against them is checked against the code that made it and can never go stale. The
    inputs -- `sim_years_on_svt`, `sim_segment_days`, `market_year`, `sim_action_propensity` -- are
    arguments the capture recorded and are NOT functions of the hazard, so re-driving the live
    `svt_inertia_hazard` across them asks the one question that matters: what would this population
    do under today's mechanism?

    That is also why this is not the reimplementation `fit_year_level_anchor` refuses to make. It
    fits nothing and emits no constant; it calls the world's own function on the world's own
    recorded inputs, as a DIAGNOSTIC, which is exactly the distinction `fit_whole_book`'s docstring
    draws when it says the SVT contribution must not be recomputed for a FIT.
    """
    sibling = departure_population.svt_sibling(_FLOOR_CAPTURE)
    assert sibling.exists(), (
        f"the SVT sibling {sibling.name} is not on disk, so no floor can be recomputed and this "
        f"leg would fail on a FileNotFoundError rather than on its subject. A capture pair this "
        f"leg re-drives must be COMMITTED -- the sibling that was read here until 2026-09-02 was "
        f"untracked, which made the leg green in one worktree and red in every other."
    )
    svt_rows = json.loads(sibling.read_text())
    renewal_rows = json.loads(_FLOOR_CAPTURE.read_text())
    book = _fit_module().union_by_year(renewal_rows, svt_rows)
    expected: dict[int, float] = {}
    for row in svt_rows:
        year = int(str(row["event_date"])[:4])
        hazard = departure_risks.svt_inertia_hazard(
            years_on_svt=float(row["sim_years_on_svt"]),
            segment_days=float(row["sim_segment_days"]),
            market_switching_multiplier=propensity.market_switching_multiplier(
                int(row["market_year"])
            ),
        )
        expected[year] = expected.get(year, 0.0) + hazard * float(row["sim_action_propensity"])
    return {
        year: 100.0 * expected.get(year, 0.0) / book[year]["accounts"]
        for year in book
        if book[year]["accounts"]
    }


def _fit_module():
    """`tools.fit_year_level_anchor`, imported here and not at the top of the file.

    It is the only `tools` import in this file that pulls the FIT rather than the instrument, and
    the fit reaches `simulation` on import. Keeping it out of the module header keeps the rest of
    this file collectable when the fit is mid-edit in another lane, which is the state the shared
    tree is in most of the time.
    """
    return importlib.import_module("tools.fit_year_level_anchor")


def test_every_declared_svt_floor_reproduces_under_the_hazard_the_world_actually_runs():
    """A NUMBER A REFUSAL STATES IS A DISCLOSURE, AND A DISCLOSURE CAN GO STALE LIKE A GREEN.

    THE DEFECT THIS EXISTS FOR, measured 2026-09-02. `UNFITTED_YEARS[2022]` declared two
    independently binding causes, and the one it called *"the reason that is NOT capture-scoped"* --
    the one a reader is told to trust when the other is scoped away -- was *"its SVT floor is 12.09%
    against a published 4.30% ceiling ... so NO anchor >= 0 brings 2022 to the record"*. On
    2026-09-01 `c628cb37d` gave `svt_inertia_hazard` a required `market_switching_multiplier`. The
    same capture's own rows, re-driven through the new hazard, put that floor at **2.34%** -- BELOW
    the 4.30% target rather than 7.8pp above it. The unreachability argument had inverted, and a
    design document written the FOLLOWING DAY restated 12.09% as current and built the defence of
    2022's declared value on it.

    WHY NOTHING CAUGHT IT, WHICH IS THE PART WORTH KEEPING.
    `test_every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause` above does
    corroborate 2022's refusal -- against the RENEWAL DECISION COUNT, which is cause (i). Cause (ii)
    is a different quantity on a different route and no leg in this file read it. A control over a
    two-cause claim that corroborates one cause reports the OR: the entry stayed green with half of
    it false. The capture is not what changed, either -- it is byte-identical. The CODE moved under
    a stored number, which is why this leg recomputes rather than reads a column.

    KEYED TO THE PROPERTY, NOT TO 2.34. The assertion is *every floor a cause states in the present
    tense reproduces from the committed capture under the live hazard*. A future market term that
    moves the floor again must go red here and be answered in the entry -- that is the disclosure
    working, not a pin breaking. What it forbids is a stated figure the mechanism no longer
    produces.

    AND IT MUST NOT PASS ON AN EMPTY SUBJECT. If every present-tense claim were rewritten away the
    pattern would match nothing and this would be a green over no subject -- the emptied-subject
    fail-open this file's coverage leg exists for -- so the absence of any claim is itself a
    failure, named.

    MUTATION (proven with `python3 -B`): put `2.34%` back to `12.09%` in `UNFITTED_YEARS[2022]` and
    this fires on the value; drop `market_switching_multiplier` back out of `svt_inertia_hazard`'s
    reach and it fires on the same leg from the other side.
    """
    claims: dict[int, tuple[float, float]] = {}
    for year, cause in anchor_module.UNFITTED_YEARS.items():
        found = _LIVE_FLOOR_CLAIM.search(cause)
        if found:
            claims[year] = (float(found.group(1)), float(found.group(2)))

    assert claims, (
        "no year in `UNFITTED_YEARS` states an SVT floor in the present tense, so this leg has no "
        "subject and its PASS means nothing. 2022's cause carried one until it was edited. If a "
        "declared cause genuinely no longer rests on a floor, delete this leg in the same commit "
        "and say so -- do not leave a green over an empty subject."
    )

    live = _live_svt_floor_pct()
    for year, (stated_floor, stated_target) in sorted(claims.items()):
        assert year in live, (
            f"{year}'s cause states an SVT floor of {stated_floor}%, but the committed capture "
            f"carries no accounts that year, so the claim cannot be checked at all. A refusal "
            f"resting on an uncheckable number is the refusal-names-an-unobserved-cause shape."
        )
        assert abs(live[year] - stated_floor) <= 0.05, (
            f"{year}'s declared cause states an SVT floor of {stated_floor}%, and the committed "
            f"capture's own rows re-driven through today's `svt_inertia_hazard` give "
            f"{live[year]:.2f}%. The capture has not changed; the MECHANISM has. Correct the "
            f"stated figure beside its superseded text -- and check whether the CONCLUSION the "
            f"old figure supported still holds, because in 2026-09-02's case it had inverted."
        )
        published_target = 100.0 * propensity.market_departure_rate(year)
        assert abs(published_target - stated_target) <= 0.05, (
            f"{year}'s declared cause states a published ceiling of {stated_target}% and the "
            f"record says {published_target:.2f}%. The comparison the refusal rests on is against "
            f"a number the commons does not carry."
        )


#: A cause's claim about the rows a NAMED capture holds for the year it refuses. The grammar is
#: `<file>.json ... ALL <n> OF THOSE ROWS CARRY \`passive_churn_cap = <v>\``, and the file must be
#: named before the claim in the same cause.
_CITED_ROWS_CLAIM = re.compile(
    r"(?P<capture>[a-z0-9_]+\.json).{0,900}?ALL (?P<rows>\d+) OF THOSE ROWS CARRY "
    r"`passive_churn_cap = (?P<cap>[0-9.]+)`",
    re.S,
)


def test_a_capture_a_refusal_cites_for_its_rows_is_read_for_what_those_rows_actually_are():
    """A CITED ARTEFACT IS A DISCLOSURE TOO, AND THE INFERENCE DRAWN FROM IT CAN BE THE WRONG ONE.

    THE DEFECT THIS EXISTS FOR, measured 2026-09-03. `UNFITTED_YEARS[2022]` cited
    `c3_shown_price_departure_factors.json` as carrying *"53 renewal rows in 2022 under the retired
    ten-year block, so a re-capture CAN close this one"*. The row COUNT was right and was checkable;
    the INFERENCE was not checked by anything, and it is false. All 53 of those rows carry
    `passive_churn_cap = 0.1` — every one is a forced-passive roll that the pre-C1b world settled as
    a fixed term anyway, which is the precise defect C1b was landed to remove. So the artefact cited
    as evidence that a re-capture restores the population is evidence of the retired defect, and
    "re-capture" as a repair means re-introducing it.

    IT COST A LANE 0 DIRECTION. The item *give 2022 a renewal population* was drawn on that sentence
    and would have spent a ten-minute capture proving the absence it was sent to remove. The
    composition that makes the absence structural is now held directly, in
    `tests/simulation/test_svt_assignment.py::test_no_household_can_reach_a_renewal_decision_in_a
    _crisis_year`; this leg holds the historical claim the entry makes about the artefact.

    WHY IT SURVIVED. `..._every_declared_svt_floor_reproduces_under_the_hazard_the_world_actually
    _runs` above holds the FLOOR figure in the same entry, and `..._every_comparison_year_is_either
    _read_or_refused_with_a_corroborated_cause` holds the DECISION COUNT. Neither reads a capture a
    cause NAMES, so a cause could cite any file in the tree for any property and nothing would open
    it — the same mixed-subject OR that let half of this entry be false for two days.

    KEYED TO THE GRAMMAR, NOT TO 2022 OR TO 53. Any cause that names a capture and states what its
    rows for that year are gets opened and checked. Deleting the claim empties the subject and the
    floor below fires rather than passing quietly.

    MUTATION (`python3 -B`): change `ALL 53` to `ALL 54` in `UNFITTED_YEARS[2022]` -> fires on the
    count; change the cap to `0.2` -> fires on the cap; point the citation at
    `c5_refitted_departure_factors.json` (which carries no 2022 rows at all) -> fires on the
    zero-row leg, which is the case where a re-capture claim would be checked against nothing.
    """
    claims: list[tuple[int, str, int, float]] = []
    for year, cause in anchor_module.UNFITTED_YEARS.items():
        found = _CITED_ROWS_CLAIM.search(cause)
        if found:
            claims.append((year, found.group("capture"), int(found.group("rows")),
                           float(found.group("cap"))))

    assert claims, (
        "no `UNFITTED_YEARS` cause states what a named capture's rows for its refused year "
        "actually are, so this leg has no subject and its PASS means nothing. 2022's cause carried "
        "one. If the claim is genuinely gone, delete this leg in the same commit and say so — do "
        "not leave a green over an empty subject."
    )

    reports = Path(__file__).resolve().parents[2] / "docs" / "reports"
    for year, capture, stated_rows, stated_cap in claims:
        path = reports / capture
        assert path.exists(), (
            f"{year}'s cause cites `{capture}` for what its rows are, and no such file is in "
            f"`docs/reports/`. A refusal resting on an artefact nobody can open is the "
            f"refusal-names-an-unobserved-cause shape."
        )
        rows = [r for r in json.loads(path.read_text())
                if str(r.get("event_date", ""))[:4] == str(year)]
        assert rows, (
            f"{year}'s cause cites `{capture}` as carrying {stated_rows} rows for {year}, and that "
            f"file carries NONE. The claim is checked against nothing."
        )
        assert len(rows) == stated_rows, (
            f"{year}'s cause states `{capture}` carries {stated_rows} rows for {year}; it carries "
            f"{len(rows)}. Correct the stated figure beside its superseded text."
        )
        off = [r for r in rows if r.get("passive_churn_cap") != stated_cap]
        assert not off, (
            f"{year}'s cause states ALL {stated_rows} rows in `{capture}` carry "
            f"`passive_churn_cap = {stated_cap}`, and {len(off)} do not "
            f"(e.g. {off[0].get('customer_id')}@{off[0].get('event_date')} at "
            f"{off[0].get('passive_churn_cap')}). If some of those rows are ACTIVE renewals then "
            f"they are not all the retired defect, and the conclusion the entry draws from them "
            f"— that only a change to the world can close this year — has to be re-argued."
        )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (b2) THE POPULATION THE VERDICT ABOVE WAS TAKEN ON — added 2026-08-31
#
# WHAT WENT WRONG, AND IT IS NOT THAT THE ABOVE LEG IS WRONG. It is green, it fires on its own
# subject, and its subject is a real measurement. The defect is that its subject is a mean over
# renewal DECISIONS and the band it is judged against counts every domestic electricity ACCOUNT.
# Before C1b those were merely different denominators. After C1b the renewal route carries 39% of
# the world's departures, so the green above is a statement about the households that reach a
# renewal roll -- the ones who demonstrably shop -- read as a statement about the book.
#
# AND ITS ARTEFACT IS FROM A WORLD THAT NO LONGER EXISTS. `docs/reports/c2_departure_factors.json`
# has no `_svt_segment_decisions.json` sibling, so it was captured before the world had a second
# departure route at all. Nothing above can notice that: the table kept its rows and every field
# populated, because it was the SCOPE of the population that moved and not its size.
#
# Measured 2026-08-31 on the two-route capture `docs/reports/ladder_churn_factors.json`, the
# comparable quantity -- every departure on either route over the accounts on the book -- is OUT
# OF BAND in all eight full years, by -2.17 to +8.50pp. The renewal-only column prints `nan` for
# 2022 because the renewal book has no decisions that year at all.
#
# So these three legs do not re-judge the world. They make it impossible for this file to report a
# whole-book verdict it has not taken.
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_the_register_names_the_route_its_principal_subject_can_see():
    """MUTATION: drop the route qualifier from `_PRINCIPAL_SUBJECT`, or widen
    `world_realised_rate_pct` to mean across both routes, and this fires.

    TWO LEGS, AND THE FIRST IS THE ONE THAT IS NOT A STRING CHECK. Leg (i) establishes WHICH
    population the principal subject is a mean over, by counting it: the decisions the instrument
    means over must equal the RENEWAL decision count in `departure_population`'s declaration, and
    not the total across both routes. Those two counts come from different modules, so this is a
    cross-check and not a parse of the same parse. It is also the leg that catches the failure
    this repository has already paid for -- a mean taken ACROSS two populations, which would make
    the register key honest and the number meaningless.

    Leg (ii) is the string check, and it only means anything because leg (i) pinned the
    population first. A reading over renewal decisions must not be registered under a whole-book
    name; that is exactly how the green above came to read as a statement about the book. The
    qualifier is matched against a LIST of acceptable phrasings rather than one exact string,
    because pinning the key to today's wording would turn every honest re-phrasing red -- the
    keyed-to-the-answer shape this file exists to avoid.
    """
    decl = instrument.reading_population()
    rows = json.loads(instrument.DEFAULT_TABLE.read_text())
    outcome = instrument.world_outcome(rows)

    # (i) WHICH POPULATION IS IT A MEAN OVER? Counted, not assumed.
    meaned_over = sum(n for n, _d, _p in outcome.values())
    renewal_decisions = decl["decisions"][departure_population.ROUTE_RENEWAL]
    assert meaned_over == renewal_decisions, (
        f"the principal subject means over {meaned_over} decisions but the population declaration "
        f"counts {renewal_decisions} renewal decisions "
        f"({decl['decisions']}). If it has widened to span both routes, the mean is taken ACROSS "
        f"two populations -- an SVT segment decision carries no renewal to describe -- and the "
        f"resulting figure is not a quantity. If it has narrowed, the subject is smaller than the "
        f"register says."
    )
    assert meaned_over > 0, "an empty subject is not a pass"

    # (ii) GIVEN THAT, DOES THE REGISTER SAY SO?
    key = _PRINCIPAL_SUBJECT.lower()
    assert any(q in key for q in _SUBJECT_ROUTE_QUALIFIERS), (
        f"the principal subject is a mean over {renewal_decisions} RENEWAL decisions, and it is "
        f"registered as {_PRINCIPAL_SUBJECT!r} -- a name that claims the whole book. The published "
        f"band's denominator is every domestic electricity account; this reading's is the "
        f"households that reached a renewal roll. Post-C1b that is "
        f"{decl['population']!r}. Name the route or the green above will be quoted as a "
        f"whole-book verdict, which is the defect this leg was added for."
    )


@pytest.mark.xfail(strict=True, reason=(
    "SIX OF THE EIGHT ARE IN BAND AND TWO ARE NOT, SO THE MARKER STAYS -- BUT IT IS NOW HELD OPEN "
    "BY ONE STRUCTURAL YEAR AND ONE OVERSHOOT OF A TENTH OF A POINT, NOT BY A WORLD AT THE WRONG "
    "LEVEL. Measured 2026-09-03 on docs/reports/c6_second_pass_departure_factors.json, the capture "
    "of the SECOND whole-book re-fit: 2017 14.00, 2018 20.00, 2019 21.30, 2020 22.97, 2023 12.40 "
    "and 2024 15.96 are all INSIDE their published bands. The two that are not are NOT the same "
    "claim and must not be read as one. "
    "(1) 2021 is 18.53% against 17.9-18.4%, out HIGH by +0.13pp. That is an overshoot of the "
    "re-capture, not a level error: the fit solves onto the band TOP (18.40) on the capture it is "
    "given, and raising the level changes the book, so the next run lands NEAR the solution rather "
    "than on it. A tenth of a point on 51 accounts is inside the draw. "
    "(2) 2022 is 2.50% against 2.9-4.3%, out LOW by -0.40pp, and NO re-fit can move it. 2022 is in "
    "departure_level_anchor.UNFITTED_YEARS running at NO_LEVEL_CORRECTION (1.0) because the "
    "capture family carries ZERO 2022 renewal decisions -- 2022 is 100% crisis-forced-passive and "
    "C1b routes every passive roll to the SVT table, so the anchor multiplies nothing there. "
    "2.50% is what the SVT route alone produces. THIS IS THE THING THAT HAS TO CHANGE for this "
    "marker to come off, and IT IS NOT A CAPTURE-POPULATION QUESTION -- this reason said it was "
    "until 2026-09-03 and so did the register entry it read. NO CAPTURE OF THE LIVE WORLD CAN "
    "CARRY A 2022 RENEWAL DECISION: the forcing and the divert are both unconditional, held by "
    "tests/simulation/test_svt_assignment.py::test_no_household_can_reach_a_renewal_decision_in_a_"
    "crisis_year. What closes it is a change to the WORLD, and the smallest one that reaches the "
    "anchor is on the SVT route: run_phase2b builds every SVT segment with bill_shock_base=0.0, "
    "price_response=0.0 and dissatisfaction_response=0.0, and those three are the only hazards "
    "level_anchor multiplies -- so in a year whose whole book is on SVT there is no lever at all, "
    "and a cap that went 1,277 -> 1,971 -> 3,549 is priced at zero shock. That repair moves every "
    "year and needs the full capture -> fit -> capture loop; scoping it to 2022 would be a "
    "carve-out fitted to this band. See SEAT_FINDING_THE_ARTEFACT_CITED_AS_PROOF_2022_CAN_BE_"
    "RECAPTURED_IS_PROOF_OF_THE_RETIRED_DEFECT_2026-09-03.md. "
    "THE PROGRESSION, so a reader can see the loop converging rather than a verdict flipping: on "
    "c4 1 of 8 was in band, on c5 2 of 8, on c6 6 of 8; mean distance outside the band 0.875pp -> "
    "0.425pp -> 0.066pp; worst year 2.40pp -> 1.32pp -> 0.40pp. "
    "STRICT is unchanged and is what will force this off on the day 2022 gets a renewal "
    "population. "
    "WHAT THIS REASON SAID EARLIER ON 2026-09-03, kept because a superseded reason that is erased "
    "takes with it the evidence that it was ever checked: "
    "THE COMPARABLE QUANTITY IS NOT IN BAND, AND THE MARKER IS THE THING TO DELETE. What this "
    "reason said until 2026-09-03 is kept below the live text, because a superseded reason that is "
    "erased takes with it the evidence that it was ever checked. "
    "WHAT IS TRUE TODAY, MEASURED 2026-09-03 ON BOTH CAPTURES. The subject "
    "instrument.DEFAULT_TABLE names, docs/reports/c2_departure_factors.json, DOES have an SVT "
    "sibling on disk -- and that sibling is in NO COMMIT, so this leg reads a whole-book table in "
    "a working tree and reads a refusal at clean HEAD, for the same source. Worse, c2's SVT half "
    "ran 2022 under sim_level_anchor 3.053619, the reference-year BORROW that "
    "departure_level_anchor.NO_LEVEL_CORRECTION replaced with the identity precisely because that "
    "borrow was wrong on the one year it fired on. c2 is therefore a capture of superseded code. "
    "On docs/reports/c4_whole_book_departure_factors.json -- the only capture whose two files "
    "describe one run with BOTH producers committed, and whose SVT column carries the live 1.0 at "
    "2022 -- the whole book is IN BAND at 2024, high at 2020 by +1.62pp, and LOW in the other six "
    "(-0.22 to -2.41pp). The direction is not the one the previous text asserted. "
    "STRICT because this must break loudly on the day it is fixed rather than sit green -- the "
    "same device that held the pre-anchor 3.15x gap open until departure_level_anchor closed it. "
    "It still fails on either capture, so the marker stays until a re-fit takes the years in. "
    "WHAT THIS REASON SAID BEFORE, AND WHICH HALF MOVED: '(1) ... a PRE-C1b capture with no SVT "
    "sibling, so no whole-book reading can be taken off it at all -- world_book_rate_pct() "
    "refuses. (2) On the two-route capture that does exist, the whole book is out of band in all "
    "eight full years (-2.17 to +8.50pp), and the re-fit that would close that is REFUSED by "
    "tools/fit_year_level_anchor.py for a mechanism reason: svt_inertia_hazard has no parameter "
    "the market could arrive through (18a09617d).' Clause (1) was never a refusal in a tree "
    "carrying the untracked sibling. Clause (2)'s mechanism half was voided by c628cb37d, which "
    "gave svt_inertia_hazard a required market_switching_multiplier; its NUMBERS are c2's, and c2 "
    "is the superseded capture above. "
    "See docs/staging/done/WORKER_FINDING_THE_BAND_CONTROL_IS_GREEN_ON_A_POPULATION_THE_BAND_IS_"
    "NOT_ABOUT_2026-08-31.md and docs/staging/done/SEAT_FINDING_THE_INSTRUMENT_JUDGES_THE_WORLD_"
    "ON_A_SUPERSEDED_CAPTURE_WHOSE_SVT_HALF_IS_IN_NO_COMMIT_2026-09-03.md."
))
def test_the_whole_book_departure_level_is_inside_the_published_band():
    """THE VERDICT THE BAND WAS ALWAYS ABOUT, held open until it can be taken.

    `test_the_worlds_realised_departure_rate_is_inside_the_published_band` above judges the
    renewal route. This judges every departure on either route over the accounts on the book --
    the record's own numerator and its own denominator. Until `b8e6ba32d` nothing in this tree
    could compute it, which is why the file shipped without it.

    IT IS NOT A CONTROL THAT ASSERTS THE MODEL STAYS BAD, and the distinction is the whole reason
    for `strict=True`. A plain xfail would sit quiet forever in either direction. A strict one
    fails the moment the world comes into band, forcing the marker off and the real verdict on.
    The failure mode it cannot have is the flattering one: if `world_book_rate_pct` ever starts
    returning the renewal reading under the whole-book name, this XPASSes and reports a failure
    rather than absorbing it.

    Read the refusal before the numbers. A capture that cannot see both routes does not produce a
    low whole-book rate -- it produces no whole-book rate, which is the only honest answer and the
    reason `world_book_rate_pct` returns its cause rather than raising.
    """
    book, refusal = instrument.world_book_rate_pct()
    assert refusal is None, (
        f"no whole-book departure reading can be taken from this capture: {refusal}"
    )
    assert len(book) >= 8, (
        f"only {len(book)} full years of whole-book reading; a subject narrowed to a handful of "
        f"years is the scope-shrink fail-open this file's leg (c) exists for"
    )
    bands = _bands()
    for year, value in sorted(book.items()):
        lo, hi = bands[year]
        below, above = instrument.band_margins(value, lo, hi)
        assert instrument.inside_band(value, lo, hi), (
            f"the world's WHOLE-BOOK departure level at {year} is {value:.2f}% against a published "
            f"{lo}-{hi}% -- {below:+.2f}pp from the low edge, {above:+.2f}pp from the high edge. "
            f"Re-capture and re-fit; never widen the band."
        )


def test_the_whole_book_reading_refuses_with_a_named_cause_and_never_the_renewal_one():
    """MUTATION: return an empty refusal string, or fall back to `world_realised_rate_pct()` when
    the account denominator is unavailable, and this fires.

    THE FAIL-OPEN THIS GUARDS IS THE FLATTERING ONE, and it is a shape this project has paid for
    repeatedly: a producer that cannot compute the honest quantity returns the quantity it CAN
    compute, under the honest one's name. Here the renewal reading is sitting in band in all eight
    years, so the fallback would buy a green -- and it would be the same figure already judged one
    leg up, counted twice and labelled as the thing it is not.

    A REFUSAL MUST NAME ITS REASON, which is what makes it possible to discover the refusal was
    wrong. A missing whole-book reading with no cause attached is indistinguishable from a reader
    who forgot to ask.
    """
    book, refusal = instrument.world_book_rate_pct()
    renewal = instrument.world_realised_rate_pct()
    assert renewal, "the renewal reading is empty, so this leg cannot tell the two apart"

    if refusal is None:
        assert book, (
            "no refusal and no reading: the whole-book quantity went missing without a cause, "
            "which is the shape a reader cannot act on"
        )
    else:
        assert refusal.strip(), (
            "the whole-book reading was refused with an EMPTY cause. A refusal that does not say "
            "why cannot be checked, and cannot be discovered to have been wrong."
        )
        assert not book, (
            f"the whole-book reading was refused ({refusal}) and still returned "
            f"{len(book)} year(s). A refusal that also answers is not a refusal."
        )

    # BOTH BRANCHES. Exact equality with the renewal reading is the fallback's fingerprint: the
    # two are means over different populations on different denominators, so they agree year for
    # year only when one IS the other.
    assert book != renewal, (
        "the whole-book reading is byte-identical to the renewal-decision reading. Either the "
        "refusal path degrades to the flattering quantity under the comparable one's name, or the "
        "two have been made the same thing -- and the published band is only about one of them."
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


def test_every_unit_derived_reading_is_still_its_source_table_in_other_units():
    """MUTATION: `test_mutation_i_a_unit_derived_reading_cut_loose_from_its_source_is_caught`.

    THE CONSUMERS ARE WHY THE FRACTION FORM EXISTS AND WHY IT IS A RISK.
    `tools/population_anchor` publishes fractions -- `sim_churn_rate`, `ofgem_benchmark`, the
    annual report section -- so the per-cent table it reads from the commons has to be divided
    somewhere. Divided once at the declaration, this leg holds it. Divided at eleven call sites,
    or re-authored as a literal because a comprehension "looked indirect", the band check reaches
    the per-cent table and nothing at all reaches the numbers the board actually reads.
    """
    checked = 0
    for name, (dotted, derived_attr, source_attr, factor) in _UNIT_DERIVED_READINGS.items():
        assert _LANE_READINGS.get(dotted) == source_attr, (
            f"{name} says it derives from {source_attr}, but that table is in no band register, "
            f"so the pair is held to nothing"
        )
        source = _lane_table(dotted, source_attr)
        derived = _lane_table(dotted, derived_attr)
        assert set(source) == set(derived), (
            f"{name} covers {sorted(set(source) ^ set(derived))} differently from {source_attr}; "
            f"a derived table that has drifted in COVERAGE has been authored"
        )
        for year, value in sorted(derived.items()):
            assert value == pytest.approx(source[year] * factor, rel=1e-12), (
                f"{name}[{year}] = {value!r}, but {source_attr}[{year}] * {factor} = "
                f"{source[year] * factor!r}. The units form is no longer a units form -- it is a "
                f"second reading, and a second reading of one published series is this file's "
                f"whole subject."
            )
            checked += 1
    assert checked >= 10, (
        f"only {checked} derived entries compared -- an emptied register reports a constant PASS"
    )


def test_every_callable_shaped_reading_is_inside_the_published_band():
    """THE THIRD SHAPE, AND EVERY ONE OF THEM WAS ALREADY RIGHT (census, 2026-08-31).

    Reported that way deliberately: the direction that opened this census asked for the readings
    that turn out already right to be reported too, and all four callables sit inside the band at
    every one of the ten published years. Finding nothing wrong is the result, not a reason to
    skip the register -- what was wrong is that NOTHING HELD THEM. `market_departure_rate_pct` is
    the world's own level, the quantity `departure_level_anchor` was fitted to reach, and it was
    checkable by no control in this tree because it is a function and both registers above are
    keyed to module constants. A reading that is correct today and held by nothing is one commit
    from being the next `MARKET_SWITCHING_MULTIPLIER_BY_YEAR`.

    The two lanes sit at different points INSIDE the band and that is correct, not a discrepancy:
    the world reads the HIGH endpoint (§6's anti-flattering curriculum tie-break -- more book to
    re-win) and the company reads the MIDPOINT (its own belief, not the director's dial). B3's
    rule holds -- both are held to the record, neither is pinned to the other.

    MUTATION: make either callable return its year's rate times 1.5 and this fires on that year.
    """
    bands = _bands()
    checked = 0
    for name, (dotted, attr, to_pct) in _CALLABLE_READINGS.items():
        fn = _lane_callable(dotted, attr)
        for year, (lo, hi) in sorted(bands.items()):
            value = float(fn(year)) * to_pct
            below, above = instrument.band_margins(value, lo, hi)
            assert instrument.inside_band(value, lo, hi), (
                f"{name}({year}) = {value:.2f}% against a published {lo}-{hi}% "
                f"({below:+.2f}pp from the low edge, {above:+.2f}pp from the high edge)"
            )
            checked += 1
    assert checked >= 30, (
        f"only {checked} (callable, year) pairs compared -- a control over an emptied register "
        f"reports a constant PASS"
    )


def test_every_callable_multiplier_implies_the_level_it_declares():
    """MUTATION: return a hand-picked constant from either multiplier callable and this fires.

    The derivation leg for the callable shape, and it is not the band leg twice. A multiplier
    function could return anything that happens to imply an in-band rate; this asserts it equals
    the declared level over the reference year's level, exactly -- the property that makes the
    ratio a reading of the record rather than a number beside one.
    """
    checked = 0
    for name, (dotted, attr, ref_year, level_attr) in _CALLABLE_MULTIPLIER_READINGS.items():
        fn = _lane_callable(dotted, attr)
        reference = _level_at(dotted, level_attr, ref_year)
        for year in sorted(_bands()):
            expected = _level_at(dotted, level_attr, year) / reference
            assert float(fn(year)) == pytest.approx(expected, rel=1e-9), (
                f"{name}({year}) = {fn(year)!r} but its declared level {level_attr} implies "
                f"{expected!r}. The multiplier has come apart from the level it normalises."
            )
            checked += 1
    assert checked >= 20, f"only {checked} derived entries compared -- an emptied register passes"


# ═══════════════════════════════════════════════════════════════════════════════════════════
# (d) THE CENSUS — the leg that fires when a reading of a NEW SHAPE arrives unregistered
# ═══════════════════════════════════════════════════════════════════════════════════════════

#: WIDENED 2026-08-31 TO INCLUDE `tools/`, and the omission is the same defect one directory
#: over. `test_year_keyed_rate_table_census` was written because "a register of unverified
#: constants inherits the blindness of its own enumerator" -- and this census, written for that
#: lesson, was itself scoped to the three lanes that hold the MODEL, missing the one that holds
#: what the BOARD reads. `tools/population_anchor.py` ran on every sim run with ten hand-authored
#: rates and a copy of the refuted multiplier, and no census in the repository could name it.
#: A gate's readers are not a reason to exempt it; they are the reason not to.
_SCOPE = ("company", "saas", "simulation", "tools")
_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The commons filename. A module that reads it is BY CONSTRUCTION serving the published
#: switching record, whatever it calls the thing it serves -- which is how the census reaches
#: `market_conditions`, whose names carry none of the vocabulary below.
_COMMONS_TOKEN = "gb_domestic_switching_rate"

_VOCABULARY = ("switch", "depart", "churn", "leav", "attrit", "defect")

_YEAR_ARG_NAMES = ("year", "renewal_year", "calendar_year")


def _is_year_key(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, int) and 1990 <= node.value <= 2100


def discover_switching_level_candidates(root: Path = _REPO_ROOT, scope=_SCOPE) -> dict[str, str]:
    """Every module-level name in scope that could be carrying a switching/departure LEVEL.

    Returns `{"<dotted>:<NAME>": "<shape>"}`. DELIBERATELY OVER-INCLUSIVE. It is cheap to
    classify a candidate that turns out to be a price table and expensive to miss one that turns
    out to be a live wrong reading of a published series -- the asymmetry that cost this project
    six weeks. Everything it finds must be registered or classified below.

    TWO INDEPENDENT DISCOVERY LEGS, because either alone has a hole this census already walked
    into:
      * BY NAME -- a name or filename carrying the vocabulary. This leg alone MISSES
        `company/crm/market_conditions.py`, whose module and function names contain none of it,
        which is to say it misses the exact module this census was opened for.
      * BY COMMONS READ -- any module whose source mentions the commons artefact. This leg alone
        misses a hand-authored table that never reads the record, which is precisely what the
        original defect was.

    AND THREE SHAPES, because the register held two and the world's reading was in the third:
    a year-keyed dict LITERAL, a dict built by a COMPREHENSION or a CALL (the shape the repaired
    `market_conditions` has, and invisible to `test_year_keyed_rate_table_census`'s literal
    scanner), and a CALLABLE taking a year.
    """
    found: dict[str, str] = {}
    for package in scope:
        for path in sorted((root / package).rglob("*.py")):
            try:
                source = path.read_text()
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):  # pragma: no cover - none in scope
                continue
            reads_commons = _COMMONS_TOKEN in source
            dotted = path.relative_to(root).with_suffix("").as_posix().replace("/", ".")
            for node in tree.body:
                names: list[str] = []
                shape: str | None = None
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    if node.value is None:
                        continue
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    names = [t.id for t in targets if isinstance(t, ast.Name)]
                    value = node.value
                    if isinstance(value, ast.Dict) and value.keys and all(
                        k is not None and _is_year_key(k) for k in value.keys
                    ):
                        shape = "year-keyed dict literal"
                    elif isinstance(value, ast.DictComp):
                        shape = "year-keyed dict comprehension"
                    elif isinstance(value, ast.Call):
                        shape = "value from a call"
                elif isinstance(node, ast.FunctionDef):
                    if any(a.arg in _YEAR_ARG_NAMES for a in node.args.args):
                        names, shape = [node.name], "callable of a year"
                if shape is None:
                    continue
                for name in names:
                    by_name = any(
                        v in name.lower() or v in path.stem.lower() for v in _VOCABULARY
                    )
                    if by_name or reads_commons:
                        found[f"{dotted}:{name}"] = shape
    return found


#: EVERY CANDIDATE THE DISCOVERER FINDS THAT IS *NOT* A READING OF THE PUBLISHED SWITCHING LEVEL,
#: each with the reason it is not. Classified 2026-08-31 by reading each one. A candidate absent
#: from here and from every register above makes the census leg fire -- which is the whole point:
#: "absent" and "checked" look identical to a register, so absence is made load-bearing.
_NOT_A_LEVEL_READING: dict[str, str] = {
    # --- tools/published_route_split: a WITHIN-SEGMENT hazard, not a book level ---
    "tools.published_route_split:admissible_svt_churn":
        "external changes of supplier per SVT-ACCOUNT-year -- a hazard inside one segment of the "
        "book, not a rate over the book. Registering it would hold it to the published band, and "
        "the band's denominator is ALL GB domestic electricity accounts: the two differ by the "
        "SVT share and comparing them is the before-you-divide defect this file exists over. It "
        "is already held, and held harder, by "
        "`test_the_route_split_identity_closes_at_every_corner`, which recomputes it longhand from "
        "the band and the share it is derived from. It also returns an INTERVAL over an "
        "unestablished quantity rather than a value, so there is no level in it to hold.",
    # --- the level's DENOMINATOR and its neighbours in the same module ---
    "company.market.market_report:_UK_DOMESTIC_ACCOUNTS_M":
        "the DENOMINATOR the switching rate is expressed over, not the rate. It is caught here "
        "only by module co-location. Worth naming rather than filtering: a rate is a ratio, and "
        "the denominator drifting is the other way its level can go wrong.",
    "company.market.market_report:_UK_AVG_ELEC_UNIT_RATE_P_KWH":
        "a published domestic PRICE series, not a switching level. Same module as the rate table.",
    "company.market.market_report:_UK_AVG_GAS_UNIT_RATE_P_KWH":
        "a published domestic PRICE series, not a switching level. Same module as the rate table.",
    "company.market.market_report:get_market_elec_rate":
        "accessor over the electricity PRICE table above.",
    "company.market.market_report:get_market_gas_rate":
        "accessor over the gas PRICE table above.",
    "company.market.market_report:compare_to_market":
        "compares this company's price with the market's; returns a price comparison.",
    "company.market.market_report:market_benchmark":
        "assembles the price benchmark record; carries no switching level of its own.",
    # --- company/crm/market_conditions: the non-switching half of the module ---
    "company.crm.market_conditions:market_rate_move_pct":
        "how far the whole market's PRICE moved into a year, derived from the Ofgem cap. A "
        "different published series entirely; it shares a module with the switching reading.",
    # --- the world's savings curve: DRIVERS of a rate, not a reading of one ---
    "simulation.market_switching_propensity:MARKET_SAVINGS_BY_YEAR":
        "the modelled saving available from switching, in POUNDS. An input to the curve that "
        "produces a rate, not a rate. Inside the published window it does not set the level at "
        "all -- `market_departure_rate` returns the record and ignores the curve there.",
    "simulation.market_switching_propensity:_POST_BAN_STRUCTURAL_FACTOR":
        "a dimensionless structural adjustment to the savings curve, not normalised to a "
        "reference year and not a ratio of any published level. Same override applies: inside "
        "the record the curve is not what sets the rate.",
    "simulation.market_switching_propensity:_curve_rate":
        "the savings curve's own answer BEFORE any level correction, and explicitly not the "
        "world's departure rate -- `market_departure_rate` is, and it is registered.",
    "simulation.market_switching_propensity:_PARITY_RATE":
        "the curve evaluated at zero savings; a scalar reference point for the offer-position "
        "multiplier, not an annual market level.",
    # --- the route attribution's own vocabulary, not readings of anything ---
    "tools.fit_year_level_anchor:_OPPORTUNITY_SCALED_CAUSES":
        "a frozenset of CAUSE NAMES -- the two hazards `build_departure_risks` scales by "
        "`market_opportunity` -- naming which legs the amplification counterfactual may touch. It "
        "carries no rate, no ratio and no year. It is caught here because it sits in the module "
        "that owns the level fit, and it is named rather than filtered because a cause list that "
        "silently lost a member would leave the counterfactual measuring one leg and reporting it "
        "as both.",
    # --- per-household / per-account model parameters, not market levels ---
    "company.crm.churn_model:CRISIS_PASSIVE_YEARS":
        "a frozenset of year LABELS selecting a behavioural regime; it carries no rate.",
    "company.crm.churn_model:estimate_passive_churn_probability":
        "a per-customer conditional probability from the company's fitted churn model. Not a "
        "reading of the market-wide published level; the company is permitted to be wrong about "
        "an individual customer in a way it is not permitted to be wrong about DESNZ.",
    "company.pricing.switching_recommendation:_cap_p_per_kwh":
        "the Ofgem cap in pence per kWh. A price, in a module whose FILENAME carries the "
        "vocabulary -- which is why the name leg alone over-collects and must be classified "
        "rather than filtered.",
    "simulation.churn_journey:_TERMINAL_STATES":
        "the set of absorbing states in the churn journey state machine; carries no rate.",
    # --- tools/, reached from 2026-08-31 when `_SCOPE` widened ---
    "tools.fit_year_level_anchor:outside_comparison_window":
        "a REFUSAL, not a reading: it returns the reason a year may not carry a fitted anchor, or "
        "None. It takes a year and lives in a module whose stem carries the vocabulary, so both "
        "discovery legs reach it, and neither a refusal string nor the anchor it guards is a rate "
        "or a ratio of one. The anchor itself is classified under `_HELD_INDIRECTLY` above, for "
        "the reason given there; this is the gate in front of it. Added by the delivery seat "
        "alongside the whole-book fit, in the working tree rather than in that commit, because "
        "this file's `_SCOPE` widening was another lane's in-flight work at the time -- without "
        "the entry that lane's own commit would have gone red on a function it never wrote.",
    "tools.fit_year_level_anchor:_MARKET_PARAMETER_NAMES":
        "a frozenset of PYTHON PARAMETER NAMES ('market_year', 'market_switching_multiplier', "
        "...), used by `svt_market_invariance_refusal` to ask whether `svt_inertia_hazard` has any "
        "route for the market to reach it. Strings naming a signature, not rates: there is no year "
        "key and no value to compare to a band. Surfaced 2026-09-01 by the union of two lanes -- "
        "one widened `_SCOPE` to `tools/`, the other added this constant -- so neither lane's own "
        "test run could see it and only the merged tree goes red. That is the interconnection "
        "check CLAUDE.md asks the seat for, arriving as a test failure instead of a question.",
    "tools.grade_renewal_churn_belief:DEFAULT_ARTEFACT":
        "a filesystem PATH. Caught because the filename carries 'churn'; the name leg cannot "
        "tell a Path() call from a rate, and classifying is cheaper than narrowing the leg.",
    "tools.grade_renewal_churn_belief:DEFAULT_RUN_OUTPUT":
        "a filesystem PATH, same module and same reason.",
    "tools.measure_departure_level:ACTIVE_ELEC_ACCOUNTS":
        "the DENOMINATOR, in accounts: the active domestic electricity book per year in the "
        "captured run. Not a rate and not a ratio of one. It is the same shape as "
        "`market_report:_UK_DOMESTIC_ACCOUNTS_M` and named for the same reason -- a rate is a "
        "ratio, and the denominator drifting is the other way its level can go wrong.",
    "tools.measure_departure_level:COMPARISON_YEARS":
        "a `range` of year LABELS selecting which years the comparison averages over; carries "
        "no rate.",
    "tools.measure_departure_level:world_curve_pct":
        "the world's savings-elasticity curve read back in per cent, i.e. the instrument's "
        "accessor over `simulation.market_switching_propensity:_curve_rate`, which is already "
        "classified above as the curve's answer BEFORE any level correction. Inside the "
        "published window the curve is not what sets the world's rate; "
        "`market_departure_rate_pct` is, and it is registered.",
    "tools.population_anchor:_PUBLISHED_BAND_PCT":
        "the published BAND itself, `published_bands()` verbatim -- the record, not a reading "
        "of it. Holding it to the band would compare the commons with itself, which is the "
        "tautology shape; leg (a) and mutation (b) are what hold the record.",
}

#: HELD INDIRECTLY, and named here rather than in `_NOT_A_LEVEL_READING` because it IS
#: level-shaped and calling it "not a level reading" would be false.
_HELD_INDIRECTLY: dict[str, str] = {
    "simulation.departure_level_anchor:YEAR_LEVEL_ANCHOR":
        "a fitted per-year CORRECTION FACTOR (~3.2-4.6), not a rate and not a ratio of one: "
        "multiplying it by a published rate yields nothing meaningful, so no band check can be "
        "written for it directly. It is held through its EFFECT -- the world's realised departure "
        "rate, which is `_PRINCIPAL_SUBJECT` above and is band-checked every run. Registering it "
        "as a reading would mean inventing a comparison the quantity does not support. "
        "AND THAT INDIRECTION IS SEVEN YEARS OF TEN, NOT TEN (was NINE until 2026-09-02, and was "
        "written as though it were unconditional before that -- both corrections kept because the "
        "denominator has now moved twice and a reader should see it moving). It holds an entry "
        "only where the world runs renewal decisions that the anchor scales -- AND IT IS HOLDING "
        "NONE OF THEM TODAY, for two reasons neither of which is 2022. "
        "(i) THE HOLDER IS XFAIL. That band leg is `xfail(strict)` as of 2026-09-01: the world is "
        "out of band in 7 of 7 readable years, and a verdict held open can only fire on the world "
        "coming BACK into the band. Any anchor that keeps it outside passes silently, so while "
        "the marker stands the indirection constrains the anchor in one direction only. "
        "(ii) `band-checked every run` OVERSTATED THE PATH, and the holder's own docstring has "
        "said so since 2026-08-31: this control reads the STORED capture "
        "`docs/reports/c2_departure_factors.json`, which carries the `sim_level_anchor` of the run "
        "that produced it, so the module is not in its read path at all. Editing "
        "`YEAR_LEVEL_ANCHOR` here moves nothing until `tools/capture_departure_factors.py` runs "
        "again -- measured 2026-09-01, halving EVERY entry leaves this whole file green. It is "
        "band-checked once per RE-CAPTURE, not once per run, and the register said the stronger "
        "thing while the leg forty lines below said the weaker one. "
        "AND AS OF 2026-09-02 DEFEAT (ii) HAS A PARTIAL REMEDY, which is recorded here because a "
        "register that lists only its defeats reads as though nothing can be done about them. "
        "`test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor` holds "
        "the CO-GENERATION of the two artefacts: the capture records, per row, the anchor it ran "
        "under, so an edit to `YEAR_LEVEL_ANCHOR` that is not followed by a re-capture now fails "
        "immediately. That is what the halving mutation was walking through. **It does not lift "
        "defeat (ii) and must not be read as doing so**: it holds that the band verdict is read "
        "off a run THIS table produced, never that the value is right -- the band leg is still "
        "the only thing that judges the value, and it is still xfail. Nine of the ten record "
        "years are covered; 2022 is absent from the capture, so it is unheld here too. "
        "The two statements have TWO SEPARATE HOLDERS and that is not tidiness -- they go stale "
        "independently, and until 2026-09-02 this sentence claimed one leg held both. Statement "
        "(i) is held by "
        "`test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding`; "
        "statement (ii) by "
        "`test_the_disclosed_read_path_is_checked_against_the_read_path_the_holder_actually_has`. "
        "Neither can go stale in the flattering direction when the re-fit lands. "
        "`YEAR_LEVEL_ANCHOR[2022] = 1.524110` is held by "
        "NOTHING: 2022 is 100% crisis-forced-passive (`renewal_engagement.CRISIS_PASSIVE_YEARS`), "
        "C1b routes every passive roll to the SVT segment table, and `build_departure_risks` "
        "deliberately does not put the anchor on `svt_inertia` -- so the capture carries ZERO 2022 "
        "renewal decisions and the anchor multiplies nothing that year. Measured independently by "
        "the seat on 2026-08-31: sweeping the 2022 anchor from 0 to 10^3 moves the book's 2022 "
        "level by not one basis point (floor == ceiling == 12.09%). The entry is UNIDENTIFIED, not "
        "badly fitted, and it is the one year where a fallback silently ran 1.98x. "
        "AND AS OF 2026-09-02 THE TABLE NO LONGER CARRIES 2022 AT ALL -- the whole-book re-fit "
        "landed and refused it, so the sentence above is kept in the past tense and this is what "
        "replaced it. 2022 is now declared in `departure_level_anchor.UNFITTED_YEARS` and takes "
        "`NO_LEVEL_CORRECTION` (1.0), which is the identity of the parameter rather than the "
        "reference year's borrow that ran 1.98x. THAT IS STILL NOT HELD BY THIS FILE and naming it "
        "is not holding it: no anchor >= 0 reaches 2022's band while `build_departure_risks` "
        "leaves `svt_inertia` unscaled, so there is no value for a band control to discriminate. "
        "THE CONCLUSION IN THAT SENTENCE SURVIVES BUT ITS STATED REASON DOES NOT, corrected "
        "2026-09-02 beside its own text. The unreachability was attributed to the unscaled "
        "`svt_inertia` holding 2022 ABOVE the record, and `c628cb37d`'s required "
        "`market_switching_multiplier` voided that: re-driven through the live hazard the same "
        "capture's 2022 SVT floor is 2.34% against a 4.30% target -- the year runs SHORT of the "
        "record, not over it, so the barrier is no longer that an anchor cannot bring it down. "
        "What still binds is the OTHER cause, one clause earlier in this same entry: ZERO 2022 "
        "renewal decisions, so the anchor multiplies nothing and floor equals ceiling whatever "
        "its value. Unreachable for cause (i), not cause (ii). The dated 12.09% two sentences "
        "above is the pre-multiplier sweep and is kept as the quotation it is; it is NOT the "
        "level the mechanism produces today. This correction is PROSE and this register is not "
        "in the read path of the leg that caught the same staleness in `UNFITTED_YEARS` -- "
        "`test_every_declared_svt_floor_reproduces_under_the_hazard_the_world_actually_runs` "
        "scans the DECLARATION, not this file, which is exactly why the void clause survived "
        "here for a commit after being corrected there. Named as an unheld disclosure rather "
        "than left to read as a held one. "
        "What IS now held is that the year cannot be dropped quietly -- the declaration is "
        "corroborated against `renewal_engagement.CRISIS_PASSIVE_YEARS` and the fit window by "
        "`test_departure_risks.py::test_a_year_inside_the_published_record_with_no_fitted_anchor_"
        "refuses_instead_of_falling_back` leg (d), so a producer cannot retire an inconvenient "
        "year by naming it. See "
        "`SEAT_FINDING_THE_DEPARTURE_LEVEL_UNIONED_ONTO_ACCOUNT_YEARS_AND_2022_HAS_NO_LEVER` "
        "and `docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md`.",
    "simulation.departure_level_anchor:_unfitted_anchor":
        "the declared value for a record year the fit does not carry -- the SAME QUANTITY as the "
        "table above (a correction factor), which is why it is here and not in "
        "`_NOT_A_LEVEL_READING`. Its two branches are held very differently and saying so is the "
        "point of the entry. OUT OF WINDOW (2016, 2025) it returns the reference year's fitted "
        "anchor, held by the same indirection as the table, with the same two defeats. IN WINDOW "
        "(2022 today) it returns 1.0 and is held by NOTHING band-shaped, for the reason in the "
        "entry above: the year is unreachable by any anchor, so there is no verdict to move. It is "
        "held only in the weaker sense that the declaration must be corroborated. Both of the "
        "table's defeats apply to the out-of-window branch unchanged and are disclosed here rather "
        "than inherited silently: the holder is XFAIL, and the anchor module is not in its read "
        "path -- the band leg reads the stored capture, so an edit here moves nothing until "
        "`tools/capture_departure_factors.py` runs again.",
    "simulation.departure_level_anchor:UNFITTED_YEARS":
        "a year-keyed dict of PROSE CAUSES -- the values are strings, not rates, and there is "
        "nothing in it to compare with a band. It is the other half of the coverage partition and "
        "the thing a band control would want is the VALUE, which is `_unfitted_anchor` above.",
    "simulation.departure_level_anchor:FIT_COMPARISON_WINDOW":
        "a `range` of year LABELS declaring which years the fit is SCOPED to; carries no rate, for "
        "the same reason as `tools.measure_departure_level:COMPARISON_YEARS`, which it duplicates "
        "deliberately (`simulation/` must not take a `tools/` import edge) and is coupled to by "
        "`test_the_anchors_fit_window_is_the_window_the_comparison_is_taken_over`.",
    "simulation.departure_level_anchor:year_level_anchor":
        "the accessor over the table above; held by the same indirection -- including its two "
        "current defeats, the XFAIL on the holder and the stored-capture read path -- and unheld "
        "in 2022 for the same reason.",
}


# The phrases a `_HELD_INDIRECTLY` entry uses to name the band leg as its holder. Matching on an
# explicit phrase rather than fuzzily on the whole text is deliberate: a new entry held by some
# OTHER control must not silently inherit this leg's disclosure requirement, and the leg below
# refuses an empty match set rather than passing over one.
_CLAIMS_THE_BAND_LEG_HOLDS_IT = ("held through its EFFECT", "held by the same indirection")


def _holder_xfail_marks() -> list[object]:
    """The `xfail` markers on the band leg that `_HELD_INDIRECTLY` names as its holder."""
    holder = test_the_worlds_realised_departure_rate_is_inside_the_published_band
    return [m for m in getattr(holder, "pytestmark", []) if m.name == "xfail"]


def test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding():
    """MUTATION: delete the word XFAIL from either `_HELD_INDIRECTLY` entry and this fires; delete
    the `@pytest.mark.xfail` from the band leg without editing the entries and it fires the other
    way. Both proven with `python3 -B`, 2026-09-01.

    THE DEFECT THIS EXISTS FOR, and it is one level up from the emptied subject `f97c34eb0` just
    repaired. That commit corrected this register's DENOMINATOR -- ten years to nine, 2022 named
    as held by nothing. In the same tree, on the same day, the leg the entry names as its holder
    was marked `xfail(strict)`. So the entry went on asserting that the anchor is "held through
    its EFFECT ... band-checked every run" while the effect's verdict was held open, and nothing
    anywhere could notice the two had come apart. A quantity classified as held INDIRECTLY is
    held by exactly as much as its holder is holding, and until this leg there was no route by
    which xfailing a holder told its dependants.

    KEYED TO THE PROPERTY AND SYMMETRIC, which is the whole reason it is worth having. It does not
    assert the holder IS xfail -- that would be the catalogued "control asserts the model stays
    bad" shape, and it would go red on the day the re-fit lands and the marker comes off. It
    asserts the entry and the holder AGREE about which state they are in. Xfail the holder and the
    entry must say so; discharge the holder and the entry claiming XFAIL must be corrected. The
    stale-in-the-flattering-direction case is the one that costs, and it is the second branch.

    WHAT THIS LEG DOES NOT CLAIM. It cannot tell whether the holder is a GOOD holder -- that the
    stored-capture read path makes it a per-re-capture drift detector rather than a live assertion
    is not asserted here. This leg's subject is narrower and mechanisable: disclosure of the
    XFAIL, at the place a reader of the register is standing.

    AND THAT DISCLAIMER WAS READ AS A GAP THE REGISTER HAD ALREADY FILLED. Between 2026-09-01 and
    2026-09-02 the entry said *"Both statements are held by"* this leg, while this paragraph said
    the second one is not asserted here. The read-path disclosure now has its own holder,
    `test_the_disclosed_read_path_is_checked_against_the_read_path_the_holder_actually_has`; the
    sentence above is a statement about THIS leg's subject and not about whether that one is held.
    """
    entries = {
        name: text for name, text in _HELD_INDIRECTLY.items()
        if any(phrase in text for phrase in _CLAIMS_THE_BAND_LEG_HOLDS_IT)
    }
    assert entries, (
        "no `_HELD_INDIRECTLY` entry names the band leg as its holder any more. Either the "
        f"register was emptied or the naming phrases {_CLAIMS_THE_BAND_LEG_HOLDS_IT} were "
        "reworded -- and a disclosure leg over an empty subject is the constant PASS this whole "
        "file was rewritten to stop reporting. Re-point the phrases at the new wording."
    )

    marks = _holder_xfail_marks()
    for name, text in sorted(entries.items()):
        if marks:
            assert "XFAIL" in text, (
                f"{name} is classified as held indirectly through "
                f"`test_the_worlds_realised_departure_rate_is_inside_the_published_band`, and that "
                f"leg is xfail -- reason: {marks[0].kwargs.get('reason', '')[:120]!r}... The entry "
                f"does not disclose it, so it claims cover its holder is not currently providing. "
                f"An xfailed holder can only fire on the world returning INTO the band; every "
                f"value that keeps it outside passes silently."
            )
        else:
            assert "XFAIL" not in text, (
                f"{name} still says its holder is held open XFAIL, but the "
                f"`@pytest.mark.xfail` on that band leg is gone -- the re-fit landed and the "
                f"register was not corrected. A stale disclosure of a defect that has been fixed "
                f"understates the cover the quantity now has, and the next reader will re-open a "
                f"finding that is closed."
            )


#: The phrases a `_HELD_INDIRECTLY` entry uses to disclose statement (ii) -- that the anchor MODULE
#: is not in its holder's read path, so editing it moves the holder's verdict only once the capture
#: is retaken. Kept separate from `_CLAIMS_THE_BAND_LEG_HOLDS_IT` because the two disclosures fail
#: independently: an entry can be honest about the XFAIL and stale about the read path, which is
#: precisely the state the register was in for a day.
_DISCLOSES_THE_STORED_CAPTURE_READ_PATH = ("not in its read path", "stored-capture read path")


def _anchor_reaches_the_holders_reading() -> bool:
    """Does perturbing `YEAR_LEVEL_ANCHOR` move what the band leg reads? Measured, not assumed.

    MUTATED IN PLACE, and that is what makes the negative answer worth anything. Rebinding the
    module attribute is invisible to a `from simulation.departure_level_anchor import
    YEAR_LEVEL_ANCHOR` captured at import time, so a re-wire of exactly that shape would read as
    "does not reach" and the disclosure would stay green while going false -- the flattering
    direction. The table is a plain dict, so every binding of it is the same object: module
    attribute, from-import, and the `year_level_anchor` accessor that reads it at call time all see
    the mutation.

    7x AND NOT 2x DELIBERATELY. The register cites a halving as its evidence; a probe that repeated
    the cited perturbation could not distinguish "unreachable" from "reachable but insensitive at
    that size". Seven times every entry moves any reading that is a function of the table at all.
    """
    anchor = importlib.import_module("simulation.departure_level_anchor")
    table = anchor.YEAR_LEVEL_ANCHOR
    original = dict(table)
    before = instrument.world_realised_rate_pct()
    try:
        table.update({year: value * 7.0 for year, value in original.items()})
        # THE PROBE HAS TO BE ABLE TO SHOW ITS OWN PERTURBATION LANDED. A mutation that silently
        # did nothing would report "does not reach" against every possible read path, which is the
        # constant-verdict shape one level below the one this file exists for.
        probe_year = next(iter(original))
        assert anchor.year_level_anchor(probe_year) == pytest.approx(original[probe_year] * 7.0), (
            "the probe's own perturbation is not visible through `year_level_anchor` -- it cannot "
            "tell an unreachable module from a mutation that never happened"
        )
        after = instrument.world_realised_rate_pct()
    finally:
        table.clear()
        table.update(original)
    return after != before


def test_the_disclosed_read_path_is_checked_against_the_read_path_the_holder_actually_has():
    """MUTATION: delete the read-path disclosure from either `_HELD_INDIRECTLY` entry and this
    fires naming the entry; make the reading a function of the anchor module without correcting
    those entries and it fires the other way. Both proven with `python3 -B`, 2026-09-02.

    THE DEFECT THIS EXISTS FOR, and it is the leg above's own defect recursed one level. On
    2026-09-01 `4871e53ee` gave statement (i) -- THE HOLDER IS XFAIL -- a mechanical holder. In the
    same edit the entry acquired the sentence *"Both statements are held by
    `test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding`"*, while that
    leg's own docstring said, under WHAT THIS LEG DOES NOT CLAIM, that the read path is *"recorded
    in the entry's prose ... not asserted here"*. So a register being corrected for claiming cover
    its holder was not providing acquired, in the correction itself, a second claim of cover its
    named holder explicitly disclaimed -- and the two sentences sat ninety lines apart in one file
    with nothing able to compare them. Prose asserting that prose is held is worth nothing.

    WHY STATEMENT (ii) IS THE ONE THAT COSTS. Statement (i) is visible: the marker is on the leg,
    and anyone reading the band control sees it. (ii) is a claim about a path nobody reads --
    `tools.measure_departure_level` never imports the anchor at all, it reads the STORED capture
    `docs/reports/c2_departure_factors.json`, so every edit to `YEAR_LEVEL_ANCHOR` leaves this
    whole file green until `tools/capture_departure_factors.py` runs again. That is exactly how a
    1.98x fallback on 2022 survived a capture, a fit and two preregistrations. A reader who trusts
    the indirection believes an anchor edit is band-checked; it is checked once per RE-CAPTURE.

    KEYED TO THE PROPERTY AND SYMMETRIC, for the same reason as the leg above. It does not assert
    that the anchor is unreachable -- that would pin the control to today's wiring and make it go
    red on the day someone puts the module back in the read path, which is the improvement this
    project wants. It asserts the entry and the measured read path AGREE. Re-wire the instrument to
    read the live table and the entry claiming "not in its read path at all" must be corrected;
    leave it reading the stored capture and the entry must keep saying so.
    """
    entries = {
        name: text for name, text in _HELD_INDIRECTLY.items()
        if any(phrase in text for phrase in _CLAIMS_THE_BAND_LEG_HOLDS_IT)
    }
    assert entries, (
        "no `_HELD_INDIRECTLY` entry names the band leg as its holder any more, so this leg has no "
        f"subject. Either the register was emptied or {_CLAIMS_THE_BAND_LEG_HOLDS_IT} were "
        "reworded -- and a disclosure leg over an empty subject is the constant PASS this file was "
        "rewritten to stop reporting."
    )

    reaches = _anchor_reaches_the_holders_reading()
    for name, text in sorted(entries.items()):
        disclosed = any(phrase in text for phrase in _DISCLOSES_THE_STORED_CAPTURE_READ_PATH)
        if reaches:
            assert not disclosed, (
                f"{name} says the anchor module is not in its holder's read path, but multiplying "
                f"`YEAR_LEVEL_ANCHOR` by seven MOVED what "
                f"`test_the_worlds_realised_departure_rate_is_inside_the_published_band` reads. "
                f"The instrument now sees the live table -- the indirection is stronger than the "
                f"entry admits, and a stale disclosure of a defect that has been fixed sends the "
                f"next reader to re-open a closed finding."
            )
        else:
            assert disclosed, (
                f"{name} is classified as held indirectly through the band leg, and that leg does "
                f"not read this module: multiplying `YEAR_LEVEL_ANCHOR` by seven left its reading "
                f"BIT-IDENTICAL, because it reads the stored capture "
                f"{instrument.DEFAULT_TABLE.name}. The entry does not disclose it, so it claims "
                f"cover that arrives only when the capture is retaken. Say so in the entry with "
                f"one of {_DISCLOSES_THE_STORED_CAPTURE_READ_PATH}, or put the module back in the "
                f"read path."
            )


def _cited_documents() -> dict[str, str]:
    """`{cited docs/ path: where it was cited}`, read from the ASSEMBLED strings, not the source.

    Runtime, and that is the whole point. The citation this leg was written for lives in an
    `xfail` reason built from two adjacent string literals, so the path only exists once Python
    has concatenated them. Every grep over this file's source missed it for exactly that reason.
    """
    import re

    module = sys.modules[__name__]
    texts: dict[str, str] = {}
    if module.__doc__:
        texts["the module docstring"] = module.__doc__
    for name, obj in vars(module).items():
        if callable(obj) and getattr(obj, "__doc__", None) and name.startswith(("test_", "_")):
            texts[f"{name}'s docstring"] = obj.__doc__
        for mark in getattr(obj, "pytestmark", []) or []:
            reason = mark.kwargs.get("reason") if hasattr(mark, "kwargs") else None
            if reason:
                texts[f"the {mark.name} reason on {name}"] = reason
    for register in ("_HELD_INDIRECTLY", "_NOT_A_LEVEL_READING"):
        for key, value in getattr(module, register, {}).items():
            if isinstance(value, str):
                texts[f"{register}[{key!r}]"] = value

    cited: dict[str, str] = {}
    for where, text in texts.items():
        for path in re.findall(r"docs/[A-Za-z0-9_/.-]*\.md", text):
            cited.setdefault(path, where)
    return cited


def test_every_document_this_file_cites_is_a_document_that_exists():
    """MUTATION: point any document citation in this file at a path that is not in the tree and
    this fires, naming the citation site. Proven with `python3 -B`, 2026-09-01 -- and proven the
    first time by accident, on the illustrative fake path this docstring originally carried.
    Prose examples are part of the subject: an example that LOOKS like a citation is checked like
    one, which is the conservative direction for a leg about whether readers can follow a link.

    THE DEFECT THIS EXISTS FOR, found 2026-09-01 while verifying `f97c34eb0`. Two of this file's
    three document citations did not resolve.

    1. The `xfail(strict)` reason on the band leg ended `Finding: docs/staging/done/WORKER_FINDING_
       A_SCOPE_ASSERTION_WAS_STANDING_IN_FRONT_OF_A_SEVEN_OF_SEVEN_OUT_OF_BAND_VERDICT...` — a
       filename that was **never written**. The finding it means landed in the same commit under a
       different name. That reason is not decoration: it carries the DISCHARGE INSTRUCTION for the
       one control this whole file exists to serve, and it sends the reader who needs the evidence
       to a path that has never existed.
    2. The module docstring's `Opened by:` pointed at `docs/staging/...` for a finding that had
       since been archived to `docs/staging/done/`. A correct citation that rots when the filing
       system does its job.

    WHY NOTHING CAUGHT IT, and it generalises past this file. Citation (1) is assembled from two
    adjacent string literals, so the path never appears contiguously in the source and no grep,
    link checker or reviewer reading the diff could see it. The check has to run on the ASSEMBLED
    string. That is why `_cited_documents` walks the loaded module's objects rather than parsing
    the file.

    KEYED TO THE PROPERTY. It asserts every cited path RESOLVES, not that any particular document
    is cited — so archiving a finding to `done/` is still allowed, it just has to be followed
    through into the citation, and a new finding may be cited freely. An empty citation set is
    refused rather than passed: a file that cites no evidence would otherwise make this leg the
    constant PASS it was written to prevent.
    """
    cited = _cited_documents()
    assert cited, (
        "this file cites no document at all. Either the citations were stripped or "
        "`_cited_documents` no longer reaches them -- and a citation checker with an empty "
        "subject is a control that cannot fail, which is the class this file is filed under."
    )
    missing = {
        path: where for path, where in sorted(cited.items())
        if not (_REPO_ROOT / path).is_file()
    }
    assert not missing, (
        "these documents are cited by this file and are not in the tree:\n"
        + "\n".join(f"  {path}\n    cited by {where}" for path, where in missing.items())
        + "\n A citation is how a reader reaches the evidence for a refusal or a discharge "
          "instruction. One that does not resolve sends them nowhere, and the reader most likely "
          "to follow it is the one about to repair the control."
    )


def _registered_names() -> set[str]:
    """Every candidate name any register above already holds."""
    names = {f"{d}:{a}" for d, a in _LANE_READINGS.items()}
    names |= {f"{d}:{a}" for d, a, _ref, _rate in _MULTIPLIER_READINGS.values()}
    names |= {f"{d}:{a}" for d, a, _pct in _CALLABLE_READINGS.values()}
    names |= {f"{d}:{a}" for d, a, _ref, _lvl in _CALLABLE_MULTIPLIER_READINGS.values()}
    names |= {f"{d}:{a}" for d, a, _src, _f in _UNIT_DERIVED_READINGS.values()}
    return names


def _classified_names() -> set[str]:
    return set(_NOT_A_LEVEL_READING) | set(_HELD_INDIRECTLY)


def test_every_discovered_switching_level_candidate_is_registered_or_classified():
    """THE LEG THE DIRECTION ASKED FOR: a NEW SHAPE arriving unregistered must fire.

    Both registers above are hand-maintained, and a hand-maintained register's failure mode is
    not that its entries go wrong -- it is that the next one never gets added. That is exactly
    what happened twice here: a multiplier-shaped reading was invisible to a rate-keyed register
    for six weeks, and the world's own callable reading was invisible to both for as long as it
    has existed. Neither was a bug in a check; both were a subject that no check had.

    So this stops asking "are the registered readings right" and asks "is anything that could be
    a reading NOT registered". A new table, a new accessor, a new module: it lands in the
    discovery set and this goes red until somebody either registers it or writes down why it is
    not a reading. Classifying is cheap and takes one line; the point is that it cannot be
    skipped silently.

    MUTATION: `test_mutation_e_a_new_shape_arriving_unregistered_is_caught` below.
    """
    discovered = discover_switching_level_candidates()
    assert len(discovered) >= 20, (
        f"the discoverer found only {len(discovered)} candidates; it found 26 when it was "
        f"written, and a scanner that has quietly stopped matching reports a constant PASS"
    )
    accounted = _registered_names() | _classified_names()
    unaccounted = sorted(set(discovered) - accounted)
    assert not unaccounted, (
        "these look like they could carry a switching or departure LEVEL and no register holds "
        "them and nothing says why they are exempt:\n  "
        + "\n  ".join(f"{n}  [{discovered[n]}]" for n in unaccounted)
        + "\n\nEither add it to a register above (and it will be held to the published band), or "
        "add it to `_NOT_A_LEVEL_READING` with the reason it is not one. A reading nothing holds "
        "is how `MARKET_SWITCHING_MULTIPLIER_BY_YEAR` asserted 31% switching for 2016 for six "
        "weeks beside the control written for exactly that defect."
    )


def test_the_census_reaches_the_module_the_name_vocabulary_cannot_see():
    """MUTATION: drop the commons-read discovery leg and this fires.

    THE PRECISION OF THE CENSUS, STATED AS A CONTROL RATHER THAN A CLAIM. `market_conditions`
    carries neither "switch" nor "depart" nor "churn" in its module name or in
    `market_conditions_multiplier`, so the vocabulary leg cannot see the module this whole census
    was opened for. Only the commons-read leg reaches it. A future tidy-up that collapses the two
    legs into one would restore precisely the blindness this census exists to remove, and would
    otherwise do so silently -- every other leg here would stay green.
    """
    discovered = discover_switching_level_candidates()
    assert "company.crm.market_conditions:market_conditions_multiplier" in discovered
    assert "company.crm.market_conditions:MARKET_SWITCHING_MULTIPLIER_BY_YEAR" in discovered
    assert not any(
        v in "market_conditions" or v in "market_conditions_multiplier" for v in _VOCABULARY
    ), (
        "the vocabulary now matches `market_conditions` by name, so this leg no longer proves "
        "the commons-read leg is load-bearing -- give it a module the vocabulary still cannot see"
    )


def test_the_repaired_reading_is_invisible_to_the_literal_scanner_and_that_is_why_this_census_exists():
    """MUTATION: none needed -- this ASSERTS A LIMIT of the neighbouring census, and it is a fact
    about the tree, not a preference.

    `test_year_keyed_rate_table_census.discover_year_keyed_tables` matches year-keyed dict
    LITERALS. The repair that closed this defect turned `market_conditions`'s tables into a
    comprehension and a call, which means the older census can no longer see them AT ALL -- and
    its `test_the_switching_reading_has_not_been_re_inlined` leg depends on exactly that (it
    fires when the names come BACK as literals). That is sound, but it leaves the repaired form
    held by nothing in that file, and a reader could reasonably conclude the older census covers
    this series. It does not. This one does, via the comprehension and call shapes.
    """
    from tests.architecture.test_year_keyed_rate_table_census import (
        discover_year_keyed_tables,
    )

    literals = set(discover_year_keyed_tables())
    for name in (
        "company/crm/market_conditions.py::MARKET_SWITCHING_RATE_PCT_BY_YEAR",
        "company/crm/market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR",
    ):
        assert name not in literals, (
            f"{name} is a dict LITERAL again -- see "
            f"test_year_keyed_rate_table_census.test_the_switching_reading_has_not_been_re_inlined"
        )
    discovered = discover_switching_level_candidates()
    assert "company.crm.market_conditions:MARKET_SWITCHING_RATE_PCT_BY_YEAR" in discovered
    assert "company.crm.market_conditions:MARKET_SWITCHING_MULTIPLIER_BY_YEAR" in discovered


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


def test_mutation_e_a_new_shape_arriving_unregistered_is_caught(monkeypatch):
    """THE MUTATION THE DIRECTION NAMED. Add a reading of a shape no register holds and the
    census must fire.

    Mutating the DISCOVERER's output rather than writing a decoy module into the tree: the
    subject under test is whether an unaccounted candidate can reach green, and a real file would
    make this test edit a shared worktree other lanes are committing from.
    """
    real = discover_switching_level_candidates()
    monkeypatch.setattr(
        "tests.architecture.test_switching_rate_commons.discover_switching_level_candidates",
        lambda *a, **k: {
            **real,
            "company.crm.brand_new_module:SWITCHING_INDEX_BY_YEAR": "year-keyed dict literal",
        },
    )
    with pytest.raises(AssertionError, match="brand_new_module"):
        test_every_discovered_switching_level_candidate_is_registered_or_classified()


def test_mutation_f_an_emptied_discovery_set_cannot_read_green(monkeypatch):
    """MUTATION: make the discoverer return nothing and the non-vacuity floor must fire.

    The census's own fail-open: a scanner whose AST matching silently stops working finds zero
    candidates, zero of which are unaccounted, and reports a clean PASS over an empty tree.
    """
    monkeypatch.setattr(
        "tests.architecture.test_switching_rate_commons.discover_switching_level_candidates",
        lambda *a, **k: {},
    )
    with pytest.raises(AssertionError, match="only 0 candidates"):
        test_every_discovered_switching_level_candidate_is_registered_or_classified()


def test_mutation_g_a_callable_reading_moved_off_the_record_is_caught(monkeypatch):
    """MUTATION: inflate the world's own departure rate by half and the callable band leg fires.

    The world's reading is the one that was held by nothing. This proves the new register is a
    control and not a list.
    """
    import simulation.market_switching_propensity as msp

    real = msp.market_departure_rate_pct
    monkeypatch.setattr(msp, "market_departure_rate_pct", lambda year: real(year) * 1.5)
    with pytest.raises(AssertionError, match="market_departure_rate_pct"):
        test_every_callable_shaped_reading_is_inside_the_published_band()


def test_mutation_h_a_multiplier_callable_cut_loose_from_its_level_is_caught(monkeypatch):
    """MUTATION: return a hand-picked constant from the company's multiplier callable.

    It stays inside every band's implied range for several years -- which is exactly why the band
    leg alone is not enough and this derivation leg exists.
    """
    import company.crm.market_conditions as mc

    monkeypatch.setattr(mc, "market_conditions_multiplier", lambda year: 1.0)
    with pytest.raises(AssertionError, match="market_conditions_multiplier"):
        test_every_callable_multiplier_implies_the_level_it_declares()


def test_mutation_i_a_unit_derived_reading_cut_loose_from_its_source_is_caught(monkeypatch):
    """MUTATION: put the old hand-authored 2020 benchmark back into the FRACTION table only.

    0.14 is what `tools/population_anchor` published for 2020 against a record of 22.5-23.0, and
    it is the value a repair that stopped at the per-cent table would leave the board reading.
    The band leg cannot see it -- the per-cent table is still correct -- so this leg is the only
    one that can.
    """
    import tools.population_anchor as anchor

    broken = dict(anchor.OFGEM_SWITCHING_RATE)
    broken[2020] = 0.14
    monkeypatch.setattr(anchor, "OFGEM_SWITCHING_RATE", broken)
    with pytest.raises(AssertionError, match="2020"):
        test_every_unit_derived_reading_is_still_its_source_table_in_other_units()


def test_mutation_j_a_level_shaped_reading_appearing_in_tools_unregistered_is_caught(
    monkeypatch, tmp_path
):
    """THE LEG THE DIRECTION NAMED, and it is distinct from mutation (e).

    (e) proves an unaccounted candidate fires; it plants its decoy in `company/`, which was
    already in scope. This plants one in `tools/` -- the directory that was OUT of scope, where
    the board's own copy of the refuted table lived unseen -- and asserts BOTH that the decoy
    fires AND that it is the SCOPE that carries it: with `tools` removed from `_SCOPE` the
    discoverer never reaches the file at all, so the same decoy goes silent. A widened scope that
    quietly narrowed again would otherwise leave every leg here green.

    The decoy is written into a tmp tree rather than the repo: a real file would edit a shared
    worktree other lanes are committing from.
    """
    decoy_root = tmp_repo = tmp_path
    (decoy_root / "tools").mkdir()
    (decoy_root / "tools" / "board_switching_view.py").write_text(
        "SWITCHING_RATE_BY_YEAR = {2016: 0.20, 2020: 0.14}\n"
    )
    for package in ("company", "saas", "simulation"):
        (decoy_root / package).mkdir()

    widened = discover_switching_level_candidates(root=tmp_repo)
    assert "tools.board_switching_view:SWITCHING_RATE_BY_YEAR" in widened, (
        "the census does not reach `tools/`, which is where the board-facing copy of the "
        "refuted table sat outside every census in this repository"
    )
    narrowed = discover_switching_level_candidates(
        root=tmp_repo, scope=("company", "saas", "simulation")
    )
    assert "tools.board_switching_view:SWITCHING_RATE_BY_YEAR" not in narrowed, (
        "the decoy is found with `tools` out of scope too, so this proves nothing about the "
        "scope -- give it a path only the widened scope reaches"
    )

    real = discover_switching_level_candidates()  # BEFORE the patch, or the lambda recurses
    monkeypatch.setattr(
        "tests.architecture.test_switching_rate_commons.discover_switching_level_candidates",
        lambda *a, **k: {
            **real,
            "tools.board_switching_view:SWITCHING_RATE_BY_YEAR": "year-keyed dict literal",
        },
    )
    with pytest.raises(AssertionError, match="board_switching_view"):
        test_every_discovered_switching_level_candidate_is_registered_or_classified()


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
    readings, refusals = instrument.realised_rate_coverage()
    expected = [y for y in instrument.COMPARISON_YEARS if y in bands]
    assert expected, "no comparison year carries a published band -- an empty subject is not a pass"

    for year in expected:
        line = next((ln for ln in text.splitlines() if ln.strip().startswith(str(year))), None)
        assert line is not None, f"the instrument's table no longer carries a row for {year}"
        if year in refusals:
            # THE REFUSAL IS ONLY DISCHARGED ON THE SURFACE. A year the instrument cannot read is
            # a result about the run, and a result that lives only in a return value is one no
            # reader of this tool ever sees. Both halves are required: the ROW must stop claiming
            # a margin it does not have, and the REASON must be printed where the reader is.
            assert "NO READING" in line, (
                f"{year} has no reading and its row {line.strip()!r} does not say so -- a row that "
                f"prints a margin for a year with nothing behind it is the fabricated-observable "
                f"shape, and `nan` in that cell reads as a rendering accident rather than a fact."
            )
            assert refusals[year] in text, (
                f"{year} is refused with reason {refusals[year]!r} and that reason is nowhere in "
                f"the instrument's output. Dropping it is how a control over an emptied subject "
                f"came to report a constant PASS: the count fell by one and nothing said which."
            )
            continue
        assert year in readings, (
            f"{year} is neither read nor refused -- it left the subject silently, so this leg "
            f"would have checked one row fewer and still reported PASS"
        )
        value = readings[year]
        lo, hi = bands[year]
        below, above = instrument.band_margins(value, lo, hi)
        assert f"{below:+.2f}" in line and f"{above:+.2f}" in line, (
            f"{year}: the row {line.strip()!r} does not carry both margins "
            f"({below:+.2f}, {above:+.2f}) that `band_margins` computes for it"
        )

    # NO `nan` ANYWHERE ON THE SURFACE. This is what the emptying actually did before it was
    # named: 2022 entered every aggregate as `nan`, and the instrument's headline printed
    # `mean world E[depart] : nan%` and `nanx short of the record`. One unread year did not
    # reduce the summary's coverage -- it destroyed the summary, in the shape of a number.
    assert "nan" not in text, (
        "the instrument prints `nan` somewhere. A year with no reading must be REFUSED by name, "
        "not averaged in as a float that poisons every aggregate it touches."
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


# ═════════════════════════════════════════════════════════════════════════════════════════════
# RUNG 1: THE BAND AS A CHECK THE WORLD CAN FAIL
#
# Every leg above this line judges the world as it ran UNDER THE FITTED PER-YEAR ANCHOR. That
# anchor is solved by bisection onto the published rate, so `achieved == published` to four
# decimals in every fitted year BY CONSTRUCTION -- which makes those legs drift detectors (their
# own docstrings say so, at length, and got there before this section did) and NOT a verdict on
# whether the mechanism produces the record's level. `DIRECTOR_CANON_WORLD_VALIDATION_LADDER_
# 2026-08-31` rung 1 requires the second question to have an answer the world can fail.
#
# These legs hold that answer. Their subject is `docs/reports/departure_level_rung1_verdict.json`,
# measured at the multiplicative IDENTITY -- no fitted scalar and no invented one -- and the world
# fails it in six years of seven.
# ═════════════════════════════════════════════════════════════════════════════════════════════


def _declared_rung1() -> dict:
    """The committed rung-1 verdict, or a hard fail naming which of the three states it is in.

    THREE STATES AND NOT TWO, because the third is how this goes quietly fail-open. The file can be
    ABSENT (nobody has run the tool -- and an absent artefact is exactly what an OOM-killed or
    never-wired producer leaves behind, which this repo has now been bitten by twice), it can carry
    a REFUSAL (the capture could not be judged, which is a result and must be read as one rather
    than skipped past), or it can carry a verdict. Only the third is a subject.
    """
    assert fitter.EMERGENT_VERDICT.exists(), (
        f"{fitter.EMERGENT_VERDICT.name} is missing. The world's only band check that is not "
        f"solved onto its own target does not exist on disk, so rung 1 has no verdict at all -- "
        f"which reads from every other green in this file as though the level were established. "
        f"Run `python3 -m tools.fit_year_level_anchor --emergent-verdict`."
    )
    declared = json.loads(fitter.EMERGENT_VERDICT.read_text())
    assert "refused" not in declared, (
        f"the rung-1 verdict is a REFUSAL and not a reading: {declared['refused']}. A refusal is a "
        f"result and it is reported here rather than skipped -- the world currently has no "
        f"unclamped level verdict, and no figure measured over its departure surface is bounded."
    )
    return declared


def _rung1_disagreements(declared: dict, live: dict) -> list[str]:
    """Every way the committed verdict and a fresh measurement of the live world differ.

    A LIST AND NOT A BOOL, and every year is checked rather than the first mismatch returned: a
    comparator that short-circuits reports the cheapest disagreement, and the reader then repairs
    that one and runs again. This is the same reason `fit_whole_book` collects every applicable
    refusal cause instead of the first.
    """
    out: list[str] = []
    declared_years, live_years = set(declared["years"]), set(live["years"])
    for year in sorted(declared_years - live_years):
        out.append(f"{year}: declared, and the live measurement does not carry it at all")
    for year in sorted(live_years - declared_years):
        out.append(
            f"{year}: the live measurement carries it and the committed verdict does not -- a "
            f"year that entered the subject silently is a year nobody has read"
        )
    for year in sorted(declared_years & live_years):
        was, now = declared["years"][year], live["years"][year]
        for key in ("band_pct", "emergent_pct", "pp_outside_band", "verdict"):
            if was[key] != now[key]:
                out.append(f"{year}.{key}: declared {was[key]!r}, live {now[key]!r}")
    if declared.get("years_failing") != live["years_failing"]:
        out.append(
            f"years_failing: declared {declared.get('years_failing')!r}, "
            f"live {live['years_failing']!r}"
        )
    return out


def test_the_rung_1_verdict_is_measured_on_the_world_the_fit_did_not_touch():
    """MUTATION: point `emergent_level_verdict` at a fitted anchor and this fires.

    THE PROPERTY, AND IT CANNOT GO STALE. This says nothing about which years pass, how many do, or
    how far outside the failures sit -- all three are allowed to move the day the mechanism is
    repaired, and a leg keyed to any of them would go red for the world becoming more honest. What
    it says is that the check's SUBJECT is the unclamped world: the anchor the verdict was measured
    at is the multiplicative identity, and identically not one of the values the solver produced.

    WHY THAT IS THE THING WORTH HOLDING. The failure this whole section exists for is a check
    solved onto its own target. A future session repairing the compression will be tempted to
    re-measure "the emergent level" at the best single constant, because 2 of 7 reads better than 1
    of 7 -- and k=2.8 is a number with no source, so that would be trading a clamp for a
    placeholder and calling it a rung-1 pass. This leg refuses it by construction rather than by
    anybody remembering the argument.
    """
    declared = _declared_rung1()
    assert declared["measured_at_anchor"] == anchor_module.NO_LEVEL_CORRECTION, (
        f"the rung-1 verdict was measured at an anchor of {declared['measured_at_anchor']}, and "
        f"`NO_LEVEL_CORRECTION` is {anchor_module.NO_LEVEL_CORRECTION}. Any other value is a "
        f"scalar somebody chose, and a level measured at a chosen scalar is the clamp again under "
        f"a different name -- whether it was fitted per year or picked once for all of them."
    )
    fitted = set(anchor_module.YEAR_LEVEL_ANCHOR.values())
    assert declared["measured_at_anchor"] not in fitted, (
        f"the rung-1 verdict's anchor is one of the FITTED values {sorted(fitted)}. A verdict "
        f"measured at the anchor that was solved onto the published rate cannot fail the band."
    )
    assert declared["capture"] == str(
        instrument.DEFAULT_TABLE.relative_to(instrument.PROJECT)
    ), (
        f"the rung-1 verdict was measured on {declared['capture']} and the instrument's live "
        f"capture is {instrument.DEFAULT_TABLE.name}. Two band verdicts read off two different "
        f"captures are two different worlds, and the reader is shown one page."
    )


def test_the_committed_rung_1_verdict_still_reproduces_and_names_every_year_it_fails():
    """MUTATION: perturb any year in the committed verdict, or move the world under it, and this
    fires -- both are exercised below, because they are different wirings and only one of them is
    the comparator.

    THIS IS A DRIFT DETECTOR OVER A DECLARATION, the same shape as
    `test_every_declared_svt_floor_reproduces_under_the_hazard_the_world_actually_runs`. The tree
    states which years the world's unclamped level fails the band in and by how much; this
    re-derives it from the live code and the live capture and refuses a declaration that has
    stopped being true. It fires IN EITHER DIRECTION -- a mechanism repair that brings 2019 into
    band reds this exactly as hard as a regression that pushes 2023 out, and that is correct: the
    record is wrong in both cases and the repair in both cases is to re-run the tool and land the
    file. A record of failures nobody updates is worth less than no record, because it is read as
    current.

    WHAT IT IS NOT: it is not an assertion that the world PASSES rung 1. It does not. Six of seven
    years are outside their band, by 3.3pp to 9.0pp, all of them LOW, and this leg is green with
    that written down. The canon's repair goes to the individual model's hazards -- never to the
    band, never to the target, and never by fitting a scalar to close the gap.
    """
    declared = _declared_rung1()
    svt_rows, reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    assert svt_rows is not None, (
        f"the live capture has no SVT half ({reason}), so the whole-book level cannot be measured "
        f"and the committed verdict cannot be checked against anything."
    )
    live = fitter.emergent_level_verdict(
        json.loads(instrument.DEFAULT_TABLE.read_text()), svt_rows
    )
    disagreements = _rung1_disagreements(declared, live)
    assert not disagreements, (
        "the committed rung-1 verdict no longer reproduces on the live world:\n  "
        + "\n  ".join(disagreements)
        + f"\nRe-run `{declared['how_to_regenerate']}` and land the artefact with whatever moved "
        f"it. Do NOT edit the file by hand and do NOT reach for the band."
    )

    # THE PARTITION, CHECKED SEPARATELY FROM THE REPRODUCTION. Both sides above could agree
    # perfectly while `years_failing` disagreed with the per-year verdicts it summarises -- a
    # summary that has come loose from its own rows is how a page reports zero failures over a
    # subject that has six.
    from_rows = sorted(
        int(y) for y, row in declared["years"].items() if row["verdict"] != "IN BAND"
    )
    assert declared["years_failing"] == from_rows, (
        f"the verdict's headline list of failing years is {declared['years_failing']} and its own "
        f"per-year rows say {from_rows}. The summary and the rows have come apart."
    )
    assert declared["in_band"] + len(from_rows) == declared["n_years"], (
        f"{declared['in_band']} in band plus {len(from_rows)} failing does not account for all "
        f"{declared['n_years']} years -- a year in neither side has left the subject silently."
    )
    for year, row in declared["years"].items():
        lo, hi = _bands()[int(year)]
        assert row["band_pct"] == [lo, hi], (
            f"{year}'s verdict was taken against a band of {row['band_pct']} and the commons "
            f"publishes {[lo, hi]}. The band moved under the verdict."
        )
        inside = instrument.inside_band(row["emergent_pct"], lo, hi)
        assert inside == (row["verdict"] == "IN BAND"), (
            f"{year} is recorded {row['verdict']} at {row['emergent_pct']}% against {lo}-{hi}%, "
            f"and the instrument's own containment test says {'inside' if inside else 'outside'}."
        )


def test_mutation_k_a_stale_rung_1_declaration_is_caught():
    """The comparator's own mutation, and it holds the leg above from both sides.

    A verdict edited to hide a failure and a verdict left behind by a world that moved are the same
    defect to a reader, so both are exercised: one year's distance nudged, and one year moved from
    LOW to IN BAND. If either passed, the declaration would be a claim nothing checks.
    """
    declared = _declared_rung1()
    live = json.loads(json.dumps(declared))
    assert not _rung1_disagreements(declared, live), "the comparator disagrees with itself"

    year = str(declared["years_failing"][0])
    nudged = json.loads(json.dumps(live))
    nudged["years"][year]["pp_outside_band"] += 0.5
    assert _rung1_disagreements(declared, nudged), (
        "a declared distance moved by half a percentage point -- more than most of these bands are "
        "wide -- reads as reproducing"
    )

    hidden = json.loads(json.dumps(live))
    hidden["years"][year]["verdict"] = "IN BAND"
    hidden["years_failing"] = [y for y in hidden["years_failing"] if str(y) != year]
    assert _rung1_disagreements(declared, hidden), (
        "a failing year quietly relabelled IN BAND reads as reproducing -- which is the clamp "
        "arriving by editing the report instead of the solver"
    )


def test_mutation_l_the_live_rung_1_measurement_is_wired_to_the_world_and_not_to_the_file(
    monkeypatch,
):
    """MUTATION: move the anchor the verdict is measured at, and the live reading must move with it.

    THE HOLE THIS CLOSES. The leg above compares a committed file against a fresh call. If that
    call had drifted loose from the world -- reading a cached artefact, or an anchor constant that
    no longer reaches the hazards -- the comparison would keep passing forever while measuring
    nothing, which is this repo's catalogued *a control whose PASS branch is unreachable reports a
    constant verdict*. So: scale the anchor the measurement is taken at and require the answer to
    change. It is the cheapest thing that proves the reading is a reading.
    """
    svt_rows, _reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    rows = json.loads(instrument.DEFAULT_TABLE.read_text())
    baseline = fitter.emergent_level_verdict(rows, svt_rows)
    monkeypatch.setattr(fitter, "NO_LEVEL_CORRECTION", 3.0)
    moved = fitter.emergent_level_verdict(rows, svt_rows)
    assert moved["measured_at_anchor"] == 3.0
    changed = [
        y for y in baseline["years"]
        if moved["years"][y]["emergent_pct"] != baseline["years"][y]["emergent_pct"]
    ]
    assert len(changed) == len(baseline["years"]), (
        f"tripling the anchor moved the emergent level in only {len(changed)} of "
        f"{len(baseline['years'])} years. The years it did not move are not being measured -- "
        f"whatever this reports for them, it is not a reading of the world's hazards."
    )
    for y in changed:
        assert moved["years"][y]["emergent_pct"] > baseline["years"][y]["emergent_pct"], (
            f"{y}'s emergent level did not RISE when every hazard was scaled up. The anchor is "
            f"reaching this measurement with the wrong sign, or not reaching it at all."
        )


# ═════════════════════════════════════════════════════════════════════════════════════════════
# RUNG 2: WHICH ROUTE CARRIES THE AMPLITUDE
#
# The section above establishes that the unclamped world fails the band in six years of seven and
# does not say WHERE the miss is. `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_...` §4 item 2 guessed --
# "`market_switching_multiplier` and `market_opportunity` ... move them too little" -- and sent the
# tree after the household-level amplitude of switching response so that leg could be amplified
# against evidence. Three declarations of that gap now point at each other and the question is with
# the director.
#
# `route_amplitude_attribution` measures the guess instead of extending it, and refutes it: the
# route where `market_opportunity` acts supplies NO year-to-year amplitude (relative slope -0.08,
# interval excluding 1.0) and the route it cannot reach supplies essentially all of it (+0.99,
# interval containing 1.0). These legs hold that reading to the world.
# ═════════════════════════════════════════════════════════════════════════════════════════════


def _declared_attribution() -> dict:
    """The committed route attribution, or a hard fail naming which of the three states it is in.

    Same three states and the same reason as `_declared_rung1`: absent, refused, or a reading. The
    middle one is a result and is reported rather than skipped.
    """
    assert fitter.ROUTE_ATTRIBUTION.exists(), (
        f"{fitter.ROUTE_ATTRIBUTION.name} is missing. The tree then carries the rung-1 FAILURE "
        f"with no attribution beside it, and the only written account of where the miss comes "
        f"from is the guess in §4 of the finding -- which this measurement refutes. Run "
        f"`python3 -m tools.fit_year_level_anchor --route-attribution`."
    )
    declared = json.loads(fitter.ROUTE_ATTRIBUTION.read_text())
    assert "refused" not in declared, (
        f"the route attribution is a REFUSAL and not a reading: {declared['refused']}. Which route "
        f"carries the record's amplitude is currently unknown, and the finding's prescribed repair "
        f"is unrefuted rather than confirmed."
    )
    return declared


def test_the_route_attribution_partitions_the_level_it_attributes():
    """MUTATION: drop either route from the sum and this fires.

    THE PROPERTY, AND IT CANNOT GO STALE. It asserts nothing about which route is responsive, by
    how much, or which way the counterfactual goes -- every one of those is free to move the day
    the mechanism is repaired, and a leg keyed to any of them would red for the world becoming more
    honest. What it holds is that the two routes ADD UP to the level being attributed: an
    attribution whose parts do not sum to its whole has a third route nobody named, or is
    double-counting one, and either way the shares it publishes are not shares of anything.

    This is the leg that would have caught the defect the attribution exists to correct, one layer
    up: the reason nobody knew the renewal route was flat is that the level and the amplitude had
    never been separated, and a decomposition that does not reconcile is how that stays true.
    """
    declared = _declared_attribution()
    routes = declared["routes"]
    assert set(routes) == {"renewal_route", "svt_route"}, (
        f"the attribution names routes {sorted(routes)}. The world has two departure routes and "
        f"the shares below are taken over them; a third would make every published share wrong."
    )
    for year, emergent in declared["emergent_pp_of_book"].items():
        parts = sum(routes[name]["pp_of_book"][year] for name in routes)
        assert parts == pytest.approx(emergent, abs=5e-4), (
            f"{year}: the routes contribute {parts:.4f}pp and the emergent level is "
            f"{emergent:.4f}pp. The decomposition does not reconcile with the thing it decomposes."
        )
        shares = sum(routes[name]["share_of_emergent_level"][year] for name in routes)
        assert shares == pytest.approx(1.0, abs=1e-3), (
            f"{year}: the published route shares sum to {shares:.4f}, not 1.0."
        )


def test_the_committed_route_attribution_still_reproduces_on_the_live_world():
    """MUTATION: perturb the declared file, or move the world under it, and this fires.

    A DRIFT DETECTOR OVER A DECLARATION, the shape this file already uses twice. It reds IN EITHER
    DIRECTION and that is the point: the day somebody wires the record's movement into the renewal
    route, the renewal slope leaves -0.08 and this goes red -- correctly, because the tree's
    written account of why rung 1 fails would have stopped being true and the finding built on it
    needs re-reading. The repair is to re-run the tool and land the file, never to relax the leg.

    THE INTERVAL IS PART OF THE SUBJECT. It is bootstrapped at a committed seed, so it reproduces
    exactly; an interval that wandered between runs would make this flaky and teach a reader to
    re-run until green, which is how a control stops being read at all.
    """
    declared = _declared_attribution()
    svt_rows, reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    assert svt_rows is not None, (
        f"the live capture has no SVT half ({reason}), so the route attribution cannot be checked."
    )
    live = fitter.route_amplitude_attribution(
        json.loads(instrument.DEFAULT_TABLE.read_text()), svt_rows
    )
    disagreements: list[str] = []
    if declared["years"] != live["years"]:
        disagreements.append(
            f"years: declared {declared['years']}, live {live['years']}"
        )
    for name in sorted(set(declared["routes"]) | set(live["routes"])):
        was, now = declared["routes"].get(name), live["routes"].get(name)
        if was is None or now is None:
            disagreements.append(f"{name}: present in one reading and not the other")
            continue
        for key in ("relative_slope", "pp_of_book", "decisions", "interval_95"):
            if was.get(key) != now.get(key):
                disagreements.append(f"{name}.{key}: declared {was.get(key)!r}, live {now.get(key)!r}")
    if declared["household_amplification_counterfactual"]["ladder"] != \
            live["household_amplification_counterfactual"]["ladder"]:
        disagreements.append("the amplification ladder no longer reproduces")
    if declared["household_amplification_counterfactual"]["ceiling_rung"] != \
            live["household_amplification_counterfactual"]["ceiling_rung"]:
        disagreements.append("the ceiling rung no longer reproduces")
    assert not disagreements, (
        "the committed route attribution no longer reproduces on the live world:\n  "
        + "\n  ".join(disagreements)
        + f"\nRe-run `{declared['how_to_regenerate']}` and land it. If the RENEWAL route has "
        f"stopped being flat, that is the mechanism repair landing and the finding that rests on "
        f"this reading must be re-read, not the leg relaxed."
    )


def test_the_attribution_is_measured_on_the_world_the_fit_did_not_touch():
    """MUTATION: measure the attribution under a fitted anchor and this fires.

    THE SAME PROPERTY `test_the_rung_1_verdict_is_measured_on_the_world_the_fit_did_not_touch`
    holds, for a reason specific to this measurement and stronger than there. The per-year anchor
    acts on the RENEWAL ROUTE ONLY. So an attribution taken under the fit would read the renewal
    route carrying exactly the year-to-year movement the solver put there to close the gap -- it
    would report the opposite conclusion, with the same arithmetic, and look entirely reasonable.
    The identity anchor is what makes the renewal route's flatness a fact about the mechanism
    rather than an artefact of which anchor the reader happened to run under.
    """
    declared = _declared_attribution()
    assert declared["measured_at_anchor"] == anchor_module.NO_LEVEL_CORRECTION, (
        f"the attribution was measured at an anchor of {declared['measured_at_anchor']}. Any "
        f"value but the identity puts the solver's per-year compensation inside the renewal "
        f"route's series, and the attribution then measures the fit rather than the world."
    )
    assert declared["measured_at_anchor"] not in set(anchor_module.YEAR_LEVEL_ANCHOR.values()), (
        "the attribution's anchor is one of the FITTED values"
    )
    assert declared["capture"] == str(
        instrument.DEFAULT_TABLE.relative_to(instrument.PROJECT)
    ), (
        f"the attribution was measured on {declared['capture']} and the live capture is "
        f"{instrument.DEFAULT_TABLE.name}. Two readings of two worlds, shown as one page."
    )


def test_mutation_m_the_attribution_is_wired_to_the_hazards_and_not_to_the_file(monkeypatch):
    """MUTATION: scale the anchor the attribution is taken at; every route level must move UP.

    THE HOLE THIS CLOSES is the one `test_mutation_l_...` closes for the rung-1 verdict, and it is
    live here for an extra reason: this reading has a per-route structure, so it can come loose one
    route at a time. If the SVT series were ever taken from a cached column rather than the
    capture, the renewal route would keep responding, the leg above would keep passing, and the
    published shares would drift silently. Requiring BOTH routes to move is what makes that
    impossible -- and the SVT route must move too, because the anchor reaches it through the
    capture's recorded probabilities being combined with hazards that scale.
    """
    svt_rows, _reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    rows = json.loads(instrument.DEFAULT_TABLE.read_text())
    baseline = fitter.route_amplitude_attribution(rows, svt_rows)
    monkeypatch.setattr(fitter, "NO_LEVEL_CORRECTION", 3.0)
    moved = fitter.route_amplitude_attribution(rows, svt_rows)
    assert moved["measured_at_anchor"] == 3.0
    for year in baseline["years"]:
        was = baseline["routes"]["renewal_route"]["pp_of_book"][year]
        now = moved["routes"]["renewal_route"]["pp_of_book"][year]
        assert now > was, (
            f"{year}: tripling the anchor left the renewal route at {now}pp against {was}pp. "
            f"Whatever this series is, it is not a reading of the world's renewal hazards."
        )
        assert moved["emergent_pp_of_book"][year] > baseline["emergent_pp_of_book"][year], (
            f"{year}: the emergent level did not rise when every renewal hazard was scaled up."
        )


def test_mutation_n_a_stale_or_edited_attribution_is_caught():
    """The comparator's own mutation, from both sides, as `test_mutation_k` does for rung 1.

    The edit exercised is the one somebody would actually make: moving the renewal route's slope to
    1.0 so the prescribed household repair reads as on-target after all. If that passed, the
    attribution would be a claim nothing checks, and the refutation it carries would be reversible
    by editing a file.
    """
    declared = _declared_attribution()
    same = json.loads(json.dumps(declared))
    assert same["routes"] == declared["routes"], "the comparator disagrees with itself"

    flattered = json.loads(json.dumps(declared))
    flattered["routes"]["renewal_route"]["relative_slope"] = 1.0
    assert flattered["routes"] != declared["routes"], (
        "the renewal route's slope moved from flat to record-proportional and the comparison "
        "reads as unchanged -- which is the finding's refuted guess reinstated by hand"
    )

    widened = json.loads(json.dumps(declared))
    widened["routes"]["renewal_route"]["interval_95"]["hi"] = 2.0
    assert widened["routes"] != declared["routes"], (
        "an interval widened past 1.0 reads as unchanged, so the claim that it EXCLUDES "
        "record-proportionality is not held by anything"
    )


# ═════════════════════════════════════════════════════════════════════════════════════════════
# WHICH LEG OF THE SVT ROUTE IS SHORT
#
# `route_amplitude_attribution` above moved the rung-1 repair off the renewal route and onto the SVT
# route: the SVT route carries the record's year-to-year SHAPE at about half its LEVEL, and no value
# of the household-amplitude gap can supply the rest. That left the level unattributed WITHIN the SVT
# route, and the finding that commissioned the attribution named three candidates without measuring
# any of them.
#
# `svt_route_shortfall_decomposition` measures the three. Two of the named three are one quantity on
# a capture, there is a fourth nobody named (exposure), and the answer is a BOUND: the two bounded
# factors cannot close rung 1 between them at the most they can ever take, so the hazard per
# SVT-account-year is the leg. These legs hold that reading to the world.
# ═════════════════════════════════════════════════════════════════════════════════════════════


def _declared_shortfall() -> dict:
    """The committed SVT shortfall decomposition, or a hard fail naming which state it is in.

    The same three states and the same reason as `_declared_attribution`: absent, refused, or a
    reading. The middle one is a result and is reported rather than skipped.
    """
    assert fitter.SVT_SHORTFALL.exists(), (
        f"{fitter.SVT_SHORTFALL.name} is missing. The tree then carries an attribution that says "
        f"the SVT route is the leg to repair, and nothing saying WHICH PART of it is short -- "
        f"which is the state the attribution was written to end. Run "
        f"`python3 -m tools.fit_year_level_anchor --svt-shortfall`."
    )
    declared = json.loads(fitter.SVT_SHORTFALL.read_text())
    assert "refused" not in declared, (
        f"the SVT shortfall decomposition is a REFUSAL and not a reading: {declared['refused']}. "
        f"Which leg of the SVT route carries the rung-1 miss is currently unknown, and the next "
        f"repair would be aimed by guess -- which is the failure the attribution beside it exists "
        f"to have stopped."
    )
    return declared


def test_the_shortfall_decomposition_multiplies_out():
    """MUTATION: perturb any one of the three factors and this fires.

    THE PROPERTY, AND IT CANNOT GO STALE. It asserts nothing about which factor is short, by how
    much, or which one has the headroom -- all three are free to move the day the mechanism is
    repaired, and a leg keyed to any of them would red for the world becoming more honest. What it
    holds is that the three factors ARE the contribution: `reach x exposure x hazard` must multiply
    out to the SVT route's own published pp-of-book.

    This is the leg that makes "which factor is short" a question with an answer. A decomposition
    whose parts do not reconstruct its whole has a fourth factor nobody named -- which is precisely
    what the finding's own three-way split turned out to have -- and every headroom below it would
    then be a bound on a quantity that is not the one being bounded.
    """
    declared = _declared_shortfall()
    for year, row in declared["per_year"].items():
        f = row["factors"]
        assert set(f) == {"reach", "exposure", "hazard"}, (
            f"{year}: the decomposition names factors {sorted(f)}. The identity below is stated "
            f"over exactly three, and a fourth would make every headroom a bound on something else."
        )
        product = 100.0 * f["reach"] * f["exposure"] * f["hazard"]
        assert product == pytest.approx(row["svt_pp_of_book"], abs=5e-4), (
            f"{year}: the three factors multiply out to {product:.4f}pp and the SVT route "
            f"contributes {row['svt_pp_of_book']:.4f}pp. The decomposition does not reconstruct "
            f"the thing it decomposes, so there is a factor in the route that it cannot see."
        )


def test_a_factor_closes_a_year_only_if_its_own_ceiling_reaches_that_years_requirement():
    """MUTATION: claim a year for a factor whose headroom is under the requirement, and this fires.

    THE WHOLE READING IS THIS ONE COMPARISON and it is the one a reader would take on trust. Every
    published sentence -- "reach closes 1 of 7", "the hazard is the leg" -- is `headroom >= required`
    evaluated per factor per year, and if the counts were ever written from anything else the
    conclusion would be unfalsifiable in exactly the way §8 of the finding says the guess it replaced
    was.

    KEYED TO THE INEQUALITY AND NOT TO TODAY'S COUNTS. It names no factor, no year and no total: if
    the world's exposure rises until exposure alone can close five years, this stays green and the
    counts move with it. What it forbids is the file claiming a closure its own numbers refuse.
    """
    declared = _declared_shortfall()
    claimed = declared["years_a_factor_could_close_alone"]
    for name, block in claimed.items():
        assert block["of"] == len(declared["years"]), (
            f"{name}: the closure count is stated out of {block['of']} years and the reading covers "
            f"{len(declared['years'])}."
        )
        for year, row in declared["per_year"].items():
            room = row["headroom_to_ceiling"][name]
            need = row["required_multiple"]["at_band_low"]
            reaches = room >= need
            listed = year in block["years"]
            assert reaches == listed, (
                f"{name} in {year}: headroom to its ceiling is x{room:.3f}, the record's least "
                f"demanding endpoint needs x{need:.3f}, and the file "
                f"{'omits' if reaches else 'claims'} the year. The published count of which factor "
                f"can close rung 1 is then not a reading of the factors."
            )


def test_the_saturation_bound_abolishes_the_renewal_route_it_saturates_away():
    """MUTATION: leave the renewal contribution inside the saturated level and this fires.

    THE BOUND IS ONLY DECISIVE IF IT IS HONEST ABOUT WHAT IT ASSUMES. Taking reach and exposure to
    1.0 means every account on the SVT product every day of the year -- a world with no renewal
    decision left to price. Crediting that world with the renewal route's 1.2-3.1pp as well would
    let the two bounded factors close years by keeping departures the counterfactual has just
    abolished, and the resulting "they still cannot do it" would be a weaker claim dressed as a
    stronger one.

    So the saturated level must be the SVT hazard ALONE, at 100 x hazard: reach and exposure are
    both 1.0 by construction there, and the identity above then makes the level exactly the hazard.
    """
    declared = _declared_shortfall()
    reached = []
    for year, row in declared["per_year"].items():
        expected = 100.0 * row["factors"]["hazard"]
        assert row["saturated_pp_of_book"] == pytest.approx(expected, abs=5e-4), (
            f"{year}: the saturated level is published as {row['saturated_pp_of_book']:.4f}pp and "
            f"reach=exposure=1.0 at this hazard gives {expected:.4f}pp. The difference is a "
            f"contribution from a route this counterfactual has abolished."
        )
        assert row["saturated_pp_of_book"] > row["svt_pp_of_book"], (
            f"{year}: saturating both bounded factors LOWERED the SVT route's level. Whatever the "
            f"published figure is, it is not those two factors taken to their ceilings."
        )
        if row["saturated_pp_of_book"] >= row["band_pct"][0]:
            reached.append(year)
    sat = declared["bounded_factor_saturation"]
    assert sorted(reached) == sorted(sat["years_reached"]), (
        f"the saturation block claims {sat['years_reached']} and the per-year figures say "
        f"{sorted(reached)}."
    )
    assert sat["reaches_band_low_in"] == len(reached) and sat["of"] == len(declared["years"])


def test_the_shortfall_is_measured_on_the_world_the_fit_did_not_touch():
    """MUTATION: measure the shortfall under a fitted anchor and this fires.

    STRONGER HERE THAN ANYWHERE ELSE IN THIS FILE, because of what the quantity is. The residual the
    SVT route is asked to cover is the band less the RENEWAL route's contribution, and the per-year
    anchor exists to make exactly that residual zero. Run under the fit, `required_multiple` would
    come out at or below 1.0 in every year, every factor's headroom would clear it, and the reading
    would report the SVT route as not short at all -- with the same arithmetic, and looking entirely
    reasonable. The identity anchor is what makes the shortfall a fact about the mechanism.
    """
    declared = _declared_shortfall()
    assert declared["measured_at_anchor"] == anchor_module.NO_LEVEL_CORRECTION, (
        f"the shortfall was measured at an anchor of {declared['measured_at_anchor']}. Any value "
        f"but the identity puts the solver's per-year compensation into the renewal route, which "
        f"is the term subtracted from the band to get the residual this whole reading is about."
    )
    assert declared["measured_at_anchor"] not in set(anchor_module.YEAR_LEVEL_ANCHOR.values()), (
        "the shortfall's anchor is one of the FITTED values"
    )
    assert declared["capture"] == str(
        instrument.DEFAULT_TABLE.relative_to(instrument.PROJECT)
    ), (
        f"the shortfall was measured on {declared['capture']} and the live capture is "
        f"{instrument.DEFAULT_TABLE.name}. Two readings of two worlds, shown as one page."
    )


def test_the_published_rate_comparison_is_restricted_to_the_window_where_it_is_a_comparison():
    """MUTATION: extend the published comparison past the base window and this fires.

    THE ONE SENTENCE IN THIS READING THAT COULD REACH A CONSTANT is "the record needs 1.7x the
    published 0.20", and it is only a statement ABOUT THE SOURCE in the years where the world runs
    the source close to unmodified. `svt_inertia_hazard` re-references the pair by
    `market_switching_multiplier / svt_inertia_base_multiplier()`, whose divisor is the MEAN of the
    multiplier over `SVT_INERTIA_BASE_WINDOW` -- so the factor is 1.0 ACROSS the window and NOT
    within each of its years. That distinction is not pedantry: the first draft of this leg asserted
    the per-year factor was 1.0, it is 0.962 at 2019, and the leg went red on its own first run.
    What holds is that the window's factors average to 1.0 and that outside the window they do not
    come near it. A ratio quoted in 2023, where the world runs 0.56 x 0.20, would read as "the
    published rate is 2x short" when what it measures is the re-referencing -- two correct figures
    whose ratio is not a quantity.

    Keyed to the window the world declares, so moving `SVT_INERTIA_BASE_WINDOW` moves this with it.
    """
    declared = _declared_shortfall()
    block = declared["base_window_comparison"]
    covered = {int(y) for y in declared["years"]}
    expected = {str(y) for y in departure_risks.SVT_INERTIA_BASE_WINDOW if y in covered}
    assert set(block["window"]) == expected and set(block["years"]) == expected, (
        f"the published-rate comparison covers {sorted(block['years'])} and the window where the "
        f"world runs the published pair unmodified is {sorted(expected)}. Outside it the ratio "
        f"measures the re-referencing and not the source."
    )
    assert block["published_annual_recent"] == departure_risks.SVT_INERTIA_ANNUAL_RECENT
    assert block["published_annual_long_stayer"] == departure_risks.SVT_INERTIA_ANNUAL_LONG_STAYER

    def _factor(year: int) -> float:
        return (
            propensity.market_switching_multiplier(year)
            / departure_risks.svt_inertia_base_multiplier()
        )

    window = departure_risks.SVT_INERTIA_BASE_WINDOW
    mean_factor = sum(_factor(y) for y in window) / len(window)
    assert mean_factor == pytest.approx(1.0, abs=1e-9), (
        f"the re-referencing factor averages {mean_factor} over the declared base window, not 1.0. "
        f"The window is what makes the published rate the rate the world runs, and it does not."
    )
    assert block["window_mean_re_referencing_factor"] == pytest.approx(1.0, abs=1e-9)
    # THE PROPERTY AND NOT A TOLERANCE. What earns the window its place is that every year in it is
    # nearer the published rate than every year outside it -- so a record whose shape moved would
    # move this leg with it, and no distance from 1.0 is written down to go stale.
    outside = [abs(_factor(int(y)) - 1.0) for y in declared["years"] if int(y) not in window]
    for year, row in block["years"].items():
        distance = abs(_factor(int(year)) - 1.0)
        assert row["re_referencing_factor"] == pytest.approx(_factor(int(year)), abs=1e-4)
        assert not outside or distance < min(outside), (
            f"{year} is inside the declared base window and its re-referencing factor sits "
            f"{distance:.4f} from 1.0, further than some year outside the window. The window is "
            f"then not where the world runs the published rate, and the ratio below is a reading "
            f"of the re-referencing rather than of the source."
        )
        assert row["required_over_published_recent"] == pytest.approx(
            row["required_hazard_at_band_low"] / departure_risks.SVT_INERTIA_ANNUAL_RECENT,
            abs=1e-3,
        ), f"{year}: the published ratio is not the required rate over the published rate."
        assert row["required_over_re_referenced_recent"] == pytest.approx(
            row["required_hazard_at_band_low"]
            / (departure_risks.SVT_INERTIA_ANNUAL_RECENT * _factor(int(year))),
            abs=1e-3,
        ), (
            f"{year}: the re-referenced ratio is not the required rate over the rate the world "
            f"actually ran. The two ratios differ and publishing one as the other is the defect "
            f"this block was split in two to avoid."
        )


def test_the_committed_shortfall_still_reproduces_on_the_live_world():
    """MUTATION: perturb the declared file, or move the world under it, and this fires.

    A DRIFT DETECTOR OVER A DECLARATION, and it reds IN EITHER DIRECTION. The day somebody raises
    the SVT hazard toward what the record needs, this goes red -- correctly, because the tree's
    written account of where the rung-1 miss lives would have stopped being true and every finding
    resting on it needs re-reading. The repair is to re-run the tool and land the file, never to
    relax the leg.
    """
    declared = _declared_shortfall()
    svt_rows, reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    assert svt_rows is not None, (
        f"the live capture has no SVT half ({reason}), so the shortfall cannot be checked."
    )
    live = fitter.svt_route_shortfall_decomposition(
        json.loads(instrument.DEFAULT_TABLE.read_text()), svt_rows
    )
    disagreements: list[str] = []
    if declared["years"] != live["years"]:
        disagreements.append(f"years: declared {declared['years']}, live {live['years']}")
    for key in ("years_a_factor_could_close_alone", "bounded_factor_saturation",
                "base_window_comparison", "per_year", "ceilings"):
        if declared.get(key) != live.get(key):
            disagreements.append(f"{key} no longer reproduces")
    assert not disagreements, (
        "the committed SVT shortfall decomposition no longer reproduces on the live world:\n  "
        + "\n  ".join(disagreements)
        + f"\nRe-run `{declared['how_to_regenerate']}` and land it. If the HAZARD factor has moved "
        f"toward what the record needs, that is the mechanism repair landing and the findings that "
        f"rest on this reading must be re-read, not the leg relaxed."
    )


def test_mutation_o_the_shortfall_is_wired_to_the_world_and_not_to_the_file(monkeypatch):
    """MUTATION: scale the anchor the shortfall is taken at; the required multiple must FALL.

    THE HOLE THIS CLOSES is the one `test_mutation_m` closes for the attribution, and the direction
    is the discriminating part. Raising the anchor raises the RENEWAL route's contribution, which is
    subtracted from the band to get the residual the SVT route must cover -- so every required
    multiple must go DOWN. A reading that took its residual from a cached column, or that had lost
    its renewal term altogether, would leave the multiples flat while every other leg above kept
    passing.
    """
    svt_rows, _reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    rows = json.loads(instrument.DEFAULT_TABLE.read_text())
    baseline = fitter.svt_route_shortfall_decomposition(rows, svt_rows)
    monkeypatch.setattr(fitter, "NO_LEVEL_CORRECTION", 3.0)
    moved = fitter.svt_route_shortfall_decomposition(rows, svt_rows)
    assert moved["measured_at_anchor"] == 3.0
    for year in baseline["years"]:
        was = baseline["per_year"][year]
        now = moved["per_year"][year]
        assert now["renewal_pp_of_book"] > was["renewal_pp_of_book"], (
            f"{year}: tripling the anchor left the renewal route at "
            f"{now['renewal_pp_of_book']}pp against {was['renewal_pp_of_book']}pp."
        )
        assert now["required_multiple"]["at_band_low"] < was["required_multiple"]["at_band_low"], (
            f"{year}: the renewal route absorbed more of the band and the SVT route is still "
            f"required to cover x{now['required_multiple']['at_band_low']}. The residual is not "
            f"being taken from the renewal contribution."
        )
        assert now["factors"] == was["factors"], (
            f"{year}: the SVT factors moved when the RENEWAL anchor changed. The anchor does not "
            f"scale the SVT route -- `svt_composition_refusal` is what establishes that -- so a "
            f"factor that moved with it is being recomputed rather than read from the capture."
        )


def test_mutation_p_a_stale_or_edited_shortfall_is_caught():
    """The comparator's own mutation, from both sides, as `test_mutation_n` does for the attribution.

    The edits exercised are the ones somebody would actually make: crediting `reach` with a year it
    cannot close, so the composition question reads as the repair after all; and lifting the hazard
    ceiling's headroom, so the one factor with room reads as having none. If either passed, the
    reading would be a claim nothing checks and its bound would be reversible by editing a file.
    """
    declared = _declared_shortfall()
    same = json.loads(json.dumps(declared))
    assert same["years_a_factor_could_close_alone"] == declared["years_a_factor_could_close_alone"], (
        "the comparator disagrees with itself"
    )

    flattered = json.loads(json.dumps(declared))
    flattered["years_a_factor_could_close_alone"]["reach"]["years"] = declared["years"]
    assert flattered["years_a_factor_could_close_alone"] != \
        declared["years_a_factor_could_close_alone"], (
        "reach was credited with every year and the comparison reads as unchanged -- which is the "
        "bound this reading exists to state, reversed by hand"
    )

    starved = json.loads(json.dumps(declared))
    first = declared["years"][0]
    starved["per_year"][first]["headroom_to_ceiling"]["hazard"] = 1.0
    assert starved["per_year"] != declared["per_year"], (
        "the hazard's headroom was cut to nothing and the comparison reads as unchanged, so the "
        "claim that it is the only factor with room is not held by anything"
    )


# ---------------------------------------------------------------------------------------------
# The composition counterfactual, and the published series it stands on.
# `tools/published_tariff_mix.py` replaced three uncoordinated copies of the same Ofgem series.
# These legs hold the properties that made consolidating it worth doing, not the values it holds.
# ---------------------------------------------------------------------------------------------


def _declared_composition() -> dict:
    """The committed composition counterfactual, or a hard fail naming which state it is in.

    Same three states and same reason as `_declared_shortfall`: absent, refused, or a reading.
    """
    assert fitter.COMPOSITION_COUNTERFACTUAL.exists(), (
        f"{fitter.COMPOSITION_COUNTERFACTUAL.name} is missing. The tree then carries a "
        f"decomposition saying reach and exposure cannot close rung 1 AT THEIR CEILINGS, and "
        f"nothing saying what happens at the value the record actually published -- which is the "
        f"smaller, likelier move a reader would ask about next. Run "
        f"`python3 -m tools.fit_year_level_anchor --composition`."
    )
    declared = json.loads(fitter.COMPOSITION_COUNTERFACTUAL.read_text())
    assert "refused" not in declared, (
        f"the composition counterfactual is a REFUSAL and not a reading: {declared['refused']}."
    )
    return declared


def test_the_counterfactual_credits_itself_with_no_year_it_inherited():
    """MUTATION: report `years_newly_closed` as the raw `closes` set and this fires.

    THE DEFECT THIS EXISTS FOR is a headline that reads "composition reaches the band in 1 of 5
    years" when the one year it names was ALREADY in band before the counterfactual ran. That is
    this repo's recurring misleading-ratio shape -- two correct figures whose difference is not the
    quantity being claimed -- and here it would reverse the finding's conclusion, because "closes
    1 of 5" and "closes 0 of 5" are opposite answers to the question the reading was run to settle.

    THE PROPERTY DOES NOT GO STALE. It says nothing about how many years composition closes. The
    day a world change makes composition close three of them, `years_newly_closed` may hold three
    and this still passes; what it may never hold is a year that needed no help.
    """
    declared = _declared_composition()
    already = set(declared["years_already_reaching_band"])
    for year in already:
        row = declared["per_year"][year]
        assert row["world_total_pp_of_book"] >= row["band_pct"][0], (
            f"{year} is listed as already reaching the band, but the world puts "
            f"{row['world_total_pp_of_book']}pp against a band low of {row['band_pct'][0]}pp."
        )
    for accounting, by_basis in declared["years_newly_closed_by_composition"].items():
        for basis, years in by_basis.items():
            closed = set(declared["closes_rung1_at_published_high"][accounting][basis])
            assert set(years) == closed - already, (
                f"{accounting}/{basis}: newly-closed is {sorted(years)} but the years reaching the "
                f"band are {sorted(closed)} and {sorted(already)} were there already. The "
                f"counterfactual is being credited with a year it inherited."
            )


def test_a_year_with_no_published_share_is_refused_and_never_interpolated():
    """MUTATION: fill 2020 or 2021 by interpolation and this fires from both ends.

    WHY THESE TWO YEARS AND NOT ANY TWO. The gap runs 2019 to 2022 and that interval CONTAINS THE
    CRISIS -- the one stretch of this record known to have moved fast and non-monotonically. An
    interpolated share there is not a slightly-wrong number, it is a manufactured reading in
    precisely the years the world is hardest to check, and it would then be indistinguishable from
    a sourced one in every artefact downstream.

    The leg holds both halves: the series must return None, AND the counterfactual must exclude the
    year from its own denominator rather than scoring it. A reading that refused the year and then
    counted it out of seven would be understating its own coverage in the other direction.
    """
    mix = importlib.import_module("tools.published_tariff_mix")
    declared = _declared_composition()
    for year in (2020, 2021):
        assert mix.default_tariff_share(year) is None, (
            f"{year} now has a published default-tariff share. If that is a real source, it "
            f"belongs in the series with its population named; if it was interpolated across the "
            f"crisis, it is a manufactured reading wearing a source's clothes."
        )
        assert str(year) in declared["years_refused"], (
            f"{year} has no established share and is not in `years_refused`, so the counterfactual "
            f"scored it somehow."
        )
        assert str(year) not in declared["per_year"], f"{year} was refused and also measured."
    assert set(declared["years_measurable"]) | set(declared["years_refused"]) == set(
        declared["fitted_years"]
    ), (
        "the measurable and refused years do not partition the fitted years, so the counterfactual "
        "is silently dropping or inventing a year."
    )


def test_the_two_published_bases_differ_exactly_where_prepayment_was_excluded():
    """MUTATION: drop the prepayment restoration, or apply it to a row that never excluded PPM.

    THE CORRECTION THIS LOCKS IN, and it is the reason the module exists. Ofgem's headline
    default-tariff share for 2017-2019 is published over a population with PREPAYMENT REMOVED, and
    more than 90% of prepayment customers are on a default tariff. All three of the in-tree copies
    this module replaced dropped that qualifier and read the figure as the domestic share. The
    verdict for 2018 and 2019 turns on it: on the as-published basis this world's SVT share reads
    ABOVE the record, and on the restored basis it reads BELOW it.

    THE PROPERTY IS THE RELATION, NOT THE VALUES. It asserts that a row which excludes prepayment
    is restored UPWARD and a row which does not is returned unchanged -- both directions -- so
    correcting any individual band leaves it green and dropping the mechanism does not.
    """
    mix = importlib.import_module("tools.published_tariff_mix")
    checked = 0
    for year, row in mix.DEFAULT_TARIFF_SHARE.items():
        as_pub = row.on_basis("as_published")
        restored = row.on_basis("all_domestic")
        if as_pub is None:
            assert restored is None, f"{year}: no published figure, but a restored one appeared."
            continue
        checked += 1
        if row.excludes_prepayment:
            assert all(r > p for r, p in zip(restored, as_pub)), (
                f"{year}: the source excludes prepayment and the restored band {restored} is not "
                f"above the published one {as_pub}. Prepayment is ~15% of domestic accounts and "
                f">90% of it is on a default tariff, so restoring it can only raise the share."
            )
        else:
            assert restored == as_pub, (
                f"{year}: this figure is already published over the whole domestic book and was "
                f"restored anyway, to {restored} from {as_pub} -- prepayment added twice."
            )
        assert row.population and row.source, (
            f"{year}: a published band with no population or no source is a number whose "
            f"denominator nobody can check."
        )
    assert checked >= 5, f"only {checked} years carry a figure; the series has been emptied."


def test_the_complement_band_keeps_its_endpoints_ordered():
    """MUTATION: write `fixed_share` as `(1 - lo, 1 - hi)` and this fires.

    A SILENT ALWAYS-FAIL, not a crash, which is why it needs a leg of its own. `1 - (lo, hi)` is
    `(1 - hi, 1 - lo)`. Get it backwards and every `lo <= x <= hi` check downstream reads as "no
    value is ever inside the band" -- so the share check would report OUT for every year of a world
    that had just been made correct, and the red would be read as evidence against the repair.
    """
    mix = importlib.import_module("tools.published_tariff_mix")
    for year in mix.years_with_an_established_figure():
        for basis in ("as_published", "all_domestic"):
            lo, hi = mix.fixed_share(year, basis)
            default = mix.default_tariff_share(year, basis)
            assert lo <= hi, f"{year}/{basis}: fixed-share band ({lo}, {hi}) is inverted."
            assert lo == pytest.approx(1.0 - default[1], abs=1e-9)
            assert hi == pytest.approx(1.0 - default[0], abs=1e-9)


def test_the_published_check_band_cannot_be_read_by_the_world_it_judges():
    """MUTATION: import `published_tariff_mix` from anywhere in `simulation/` and this fires.

    THE RULE IS `simulation/svt_product.py`'s OWN, in its own words: the published split is *"a
    CHECK. Never an input: if the split has to be set to land in range, the behaviour is wrong and
    setting it hides that."* A world that could read its own check band could be tuned to it, and
    the generated share would stop being evidence of anything.

    Scanned as imports rather than as text, so a mention in a comment or docstring -- which is how
    the rule gets explained -- does not fire it, and `import tools.published_tariff_mix as x` does.
    """
    offenders: list[str] = []
    for path in sorted((_REPO_ROOT / "simulation").rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            if any(n.startswith("tools.published_tariff_mix") for n in names):
                offenders.append(f"{path.relative_to(_REPO_ROOT)}:{node.lineno}")
    assert not offenders, (
        "the world imports the published band it is judged against: "
        + ", ".join(f"{o}" for o in offenders)
        + ". The check would then be reachable from the thing being checked."
    )


def test_mutation_q_the_composition_reading_is_wired_to_the_world_and_not_to_the_file(monkeypatch):
    """MUTATION: scale the anchor the counterfactual is taken at; the renewal route must RISE.

    THE HOLE THIS CLOSES is the one `test_mutation_o` closes for the shortfall. Every number in the
    reading could be a cached column copied off the decomposition, and every leg above would still
    pass, because they all check the file against itself. This one moves the WORLD underneath and
    requires the reading to follow: raising the anchor raises the renewal route's contribution, and
    both accountings must carry it. The SVT factors must NOT move with it -- the anchor does not
    scale that route -- which is what distinguishes "recomputed from the world" from "recomputed
    from the wrong thing".
    """
    svt_rows, _reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    rows = json.loads(instrument.DEFAULT_TABLE.read_text())
    baseline = fitter.published_composition_counterfactual(rows, svt_rows)
    monkeypatch.setattr(fitter, "NO_LEVEL_CORRECTION", 3.0)
    moved = fitter.published_composition_counterfactual(rows, svt_rows)
    assert moved["measured_at_anchor"] == 3.0
    assert moved["years_measurable"] == baseline["years_measurable"]
    for year in baseline["years_measurable"]:
        was, now = baseline["per_year"][year], moved["per_year"][year]
        assert now["world_renewal_pp_of_book"] > was["world_renewal_pp_of_book"], (
            f"{year}: tripling the anchor left the renewal route at "
            f"{now['world_renewal_pp_of_book']}pp against {was['world_renewal_pp_of_book']}pp."
        )
        assert now["world_svt_account_day_share"] == was["world_svt_account_day_share"], (
            f"{year}: the SVT account-day share moved when the RENEWAL anchor changed. The anchor "
            f"does not scale that route, so a share that followed it is being recomputed wrongly."
        )
        for basis, endpoints in now["bases"].items():
            for name, end in endpoints.items():
                before = was["bases"][basis][name]
                assert end["svt_pp_of_book"] == pytest.approx(before["svt_pp_of_book"], abs=5e-4), (
                    f"{year}/{basis}/{name}: the SVT leg of the counterfactual moved with the "
                    f"renewal anchor."
                )
                assert end["renewal_rescaled"]["renewal_pp_of_book"] > \
                    before["renewal_rescaled"]["renewal_pp_of_book"], (
                    f"{year}/{basis}/{name}: the renewal route absorbed more of the level and the "
                    f"rescaled accounting did not follow. It is reading a cached column."
                )


def test_the_counterfactual_moves_both_routes_together_because_they_are_complements():
    """MUTATION: hold the renewal route fixed in the rescaled accounting and this fires.

    AN ACCOUNT-DAY PUT ONTO SVT IS AN ACCOUNT-DAY TAKEN OFF A FIXED TERM, and the renewal decisions
    priced on those days go with it. A counterfactual that raised the SVT share while keeping every
    renewal decision would be adding a population to the book rather than moving one across it, and
    it would credit composition with departures from accounts that no longer exist in that world --
    which is the flattering direction, and the direction that would have made composition look like
    the repair.

    THE PROPERTY IS THE INEQUALITY AND ITS DEGENERATE CASE: wherever the published share exceeds
    the world's, the rescaled renewal contribution must be strictly SMALLER than the held one; and
    where the two shares coincide, the two accountings must agree exactly. The second half is what
    stops the leg passing on a constant offset.
    """
    declared = _declared_composition()
    compared = 0
    for year, row in declared["per_year"].items():
        world = row["world_svt_account_day_share"]
        for basis, endpoints in row["bases"].items():
            for name, end in endpoints.items():
                rescaled = end["renewal_rescaled"]["renewal_pp_of_book"]
                held = end["renewal_held"]["renewal_pp_of_book"]
                published = end["published_svt_account_day_share"]
                assert held == pytest.approx(row["world_renewal_pp_of_book"], abs=5e-4), (
                    f"{year}/{basis}/{name}: the held accounting moved the renewal route."
                )
                if published > world:
                    compared += 1
                    assert rescaled < held, (
                        f"{year}/{basis}/{name}: the SVT share rises from {world} to {published} "
                        f"and the renewal route stays at {rescaled}pp against {held}pp. The two "
                        f"routes are complements and this one is not moving."
                    )
                elif published == pytest.approx(world, abs=1e-9):
                    assert rescaled == pytest.approx(held, abs=5e-4), (
                        f"{year}/{basis}/{name}: the composition is unchanged and the two "
                        f"accountings still disagree, so the rescaling is an offset."
                    )
    assert compared >= 3, (
        f"only {compared} endpoints have the published share above the world's, so this leg is "
        f"nearly vacuous -- check the series has not been emptied."
    )


def test_the_committed_composition_still_reproduces_on_the_live_world():
    """MUTATION: perturb the declared file, or move the world under it, and this fires.

    A DRIFT DETECTOR THAT REDS IN EITHER DIRECTION, as its sibling over the shortfall does. The day
    somebody settles more of the book onto the SVT product, this goes red -- correctly, because the
    tree's written account of what composition can and cannot do would have stopped being true.
    The repair is to re-run and land, never to relax the leg.
    """
    declared = _declared_composition()
    svt_rows, reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    assert svt_rows is not None, (
        f"the live capture has no SVT half ({reason}), so the counterfactual cannot be checked."
    )
    live = fitter.published_composition_counterfactual(
        json.loads(instrument.DEFAULT_TABLE.read_text()), svt_rows
    )
    disagreements = [
        key for key in (
            "fitted_years", "years_measurable", "years_refused", "years_already_reaching_band",
            "closes_rung1_at_published_high", "years_newly_closed_by_composition", "per_year",
        )
        if declared.get(key) != live.get(key)
    ]
    assert not disagreements, (
        "the committed composition counterfactual no longer reproduces on the live world: "
        + ", ".join(disagreements)
        + f"\nRe-run `{declared['how_to_regenerate']}` and land it. If the world's SVT share has "
        f"moved toward the published one, that is a fidelity repair landing and the findings that "
        f"rest on this reading must be re-read, not the leg relaxed."
    )


# ---------------------------------------------------------------------------------------------
# THE PUBLISHED ROUTE SPLIT — `tools/published_route_split.py`, finding §11.
#
# The readings above all take a captured run as their subject. This one takes three PUBLISHED
# series and composes them against each other, so its legs guard a different failure: not "did the
# world move", but "did the reading quietly acquire a number the record does not supply". The
# unestablished quantity is `phi`, the external share of active fixed-term renewals, and the whole
# reading exists to publish an interval over it rather than a value in it. A leg that let `phi`
# become a float would retire the finding by accident.
# ---------------------------------------------------------------------------------------------


def _split_module():
    return importlib.import_module("tools.published_route_split")


def _declared_route_split() -> dict:
    return json.loads((_REPO_ROOT / "docs" / "reports" / "published_route_split.json").read_text())


def test_the_route_split_identity_closes_at_every_corner():
    """MUTATION: drop a corner from `_corners`, or compose `s * H_fixed` instead of `(1 - s) * H`.

    THE IDENTITY IS BILINEAR, so its extrema over the two published bands sit at corners and
    enumerating them is exact. Doing it by hand -- "s is increasing, take the high end" -- gets the
    sign wrong whenever `H_svt` and `H_fixed` swap order, and they do swap between 2019 and 2022.
    This recomputes the composition longhand from the two published bands and requires the module's
    reported envelope to be exactly the min and max of it.

    THE INVERSION IS CHECKED HERE TOO, AND THAT IS NOT TIDINESS. `forward_composition` never reads
    the departure band's endpoints -- it composes from `s` and `H_svt` alone and only compares
    against the band afterwards -- so dropping a departure-band corner from `_corners` is an
    EQUIVALENCE for the forward leg and was measured to be one: the first draft of this test stayed
    green under exactly that mutation, and only the artefact drift detector fired, which would
    itself go quiet the moment somebody regenerated. `admissible_svt_churn` DOES read both
    endpoints, so recomputing it longhand here is what makes the corner enumeration load-bearing.
    """
    split = _split_module()
    band = split.svt_segment_churn_band()["tenure_composed"]
    for year in sorted(set(split.published_departure_band()) & set(
        split.years_with_an_established_figure()
    )):
        for basis in split.BASES:
            share = split.default_tariff_share(year, basis)
            record = split.published_departure_band()[year]
            longhand = [
                100.0 * (s * h + (1.0 - s) * split.FIXED_ACTIVE_RENEWAL_SHARE * 1.0)
                for s in share for h in band
            ]
            got = split.forward_composition(year, basis, 1.0, svt_band=band)
            assert got["composed_pct"][0] == pytest.approx(min(longhand), abs=1e-4), (
                f"{year}/{basis}: composed low end does not match the identity recomputed longhand."
            )
            assert got["composed_pct"][1] == pytest.approx(max(longhand), abs=1e-4)
            assert got["band_pct"] == list(record)

            at_1 = [
                (r / 100.0 - (1.0 - s) * split.FIXED_ACTIVE_RENEWAL_SHARE) / s
                for r in record for s in share
            ]
            at_0 = [r / 100.0 / s for r in record for s in share]
            admissible = split.admissible_svt_churn(year, basis)
            assert admissible["at_phi_1"] == [
                pytest.approx(min(at_1), abs=1e-6), pytest.approx(max(at_1), abs=1e-6)
            ], f"{year}/{basis}: the phi=1 endpoint does not span both departure-band corners."
            assert admissible["at_phi_0"] == [
                pytest.approx(min(at_0), abs=1e-6), pytest.approx(max(at_0), abs=1e-6)
            ]
            assert admissible["admissible"] == [
                pytest.approx(min(at_1), abs=1e-6), pytest.approx(max(at_0), abs=1e-6)
            ]


def test_the_admissible_svt_churn_falls_as_the_external_share_rises():
    """MUTATION: flip the sign on the `(1 - s) * FIXED_ACTIVE_RENEWAL_SHARE` term and this fires.

    THE ONE DIRECTION THAT SEPARATES A COMPUTED READING FROM A CACHED COLUMN, and it is the same
    shape as `test_mutation_o` and `test_mutation_q` for the capture-backed readings. Every
    departure the fixed route is credited with is one the SVT route no longer has to supply, so
    `H_svt` must FALL as `phi` rises. A reading that had frozen its numbers would satisfy every
    other leg here and not this one, because this one sweeps an argument nothing is cached against.
    """
    split = _split_module()
    for year in split.years_with_an_established_figure():
        for basis in split.BASES:
            if split.admissible_svt_churn(year, basis) is None:
                continue
            swept = [
                split.phi_admitting(year, basis, h) for h in (0.05, 0.10, 0.20, 0.30)
            ]
            lows = [interval[0] for interval in swept]
            assert lows == sorted(lows, reverse=True), (
                f"{year}/{basis}: the phi the record needs must FALL as the SVT hazard rises; "
                f"got {lows}. A rising series means the fixed term carries the wrong sign."
            )
            admissible = split.admissible_svt_churn(year, basis)
            assert admissible["at_phi_1"][1] <= admissible["at_phi_0"][1] + 1e-9, (
                f"{year}/{basis}: giving the fixed route its ceiling must not RAISE the SVT "
                f"churn the record admits."
            )


def test_a_negative_admissible_endpoint_is_reported_and_never_clipped():
    """MUTATION: wrap `at_phi_1` in `max(0.0, ...)` and this fires on 2017 and 2022.

    A CLIP TURNS A REFUSAL INTO A BOUNDARY. Where `H_svt` at `phi = 1` comes out negative, the
    record is saying the fixed route alone at its published ceiling already exceeds the whole
    published band -- so the record REFUSES `phi = 1` in that year, which is the only place this
    identity constrains `phi` from above at all. Clipped to 0.0 it reads as "the SVT route
    contributes nothing", which is a different and much weaker statement, and the reader cannot
    tell the two apart. At least one scored year must carry the refusal or this leg is asserting
    nothing.
    """
    split = _split_module()
    refusing = [
        (year, basis)
        for year in split.years_with_an_established_figure()
        for basis in split.BASES
        if (row := split.admissible_svt_churn(year, basis)) is not None
        and row["at_phi_1"][0] < 0.0
    ]
    assert refusing, (
        "no scored year reports a negative admissible endpoint. Either the record stopped "
        "refusing phi=1 anywhere -- which is a finding and this leg should be re-read, not "
        "relaxed -- or an endpoint is being clipped and the refusal has been hidden."
    )
    for year, basis in refusing:
        row = split.admissible_svt_churn(year, basis)
        assert row["record_refuses_phi_1"] == (row["at_phi_1"][1] < 0.0), (
            f"{year}/{basis}: `record_refuses_phi_1` must be derived from the interval's HIGH "
            f"end -- the record only refuses phi=1 when NO corner admits it."
        )


def test_the_route_split_refuses_every_year_with_no_published_share():
    """MUTATION: interpolate 2020/2021, or score them off the band alone, and this fires.

    THE SAME REFUSAL `test_a_year_with_no_published_share_is_refused_and_never_interpolated` holds
    for the composition counterfactual, re-asserted here because this reading has its own
    denominator and a second consumer is a second place the gap can be filled by accident. The
    denominator is reported as what it is: `n_years_scored` must equal the years actually scored,
    never the years the band covers.
    """
    split = _split_module()
    reading = split.published_route_split()
    established = set(split.years_with_an_established_figure())
    for year in sorted(set(split.published_departure_band()) - established):
        assert str(year) not in reading["per_year"], (
            f"{year} has no established default-tariff share and must not be scored."
        )
        assert str(year) in reading["years_refused"], f"{year} is dropped silently, not refused."
        for basis in split.BASES:
            assert split.admissible_svt_churn(year, basis) is None
            assert split.phi_admitting(year, basis, 0.2) is None
    assert reading["n_years_scored"] == len(reading["per_year"]) == len(reading["years_scored"])
    assert set(reading["years_refused"]) == {"2020", "2021"}


def test_the_external_share_of_active_renewals_stays_a_declared_gap():
    """MUTATION: set `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS = 0.5` and this fires.

    THIS IS THE FINDING, AND A NUMBER HERE WOULD RETIRE IT SILENTLY. The published ~35% counts
    households actively renewing onto a new FIXED DEAL, which includes staying with the same
    supplier; the published numerator counts external changes of supplier only. Nothing published
    establishes the split. A float in this slot would be read as established within a week and be
    unattributable within a month, and every interval this module publishes would collapse to a
    point that looks like a measurement.

    Keyed to the PROPERTY (the slot is empty and the artefact says why), not to today's answer: if
    somebody sources it, this leg goes red, and the correct repair is to rewrite the leg around the
    citation -- which is the red a control is supposed to produce.
    """
    split = _split_module()
    assert split.EXTERNAL_SHARE_OF_ACTIVE_RENEWALS is None, (
        "phi has acquired a value. If it was sourced, cite it here and re-aim this leg at the "
        "citation; if it was picked because a number was needed, it is the defect CLAUDE.md's "
        "knowledge-first rule exists for."
    )
    declared = split.published_route_split()["the_unestablished_quantity"]
    assert declared["value"] is None
    assert declared["why_it_is_none"].strip() and declared["what_would_close_it"].strip(), (
        "a gap must carry its reason and its route to closing it, or it is indistinguishable "
        "from an oversight."
    )


def test_the_route_split_does_not_read_the_worlds_clipped_constants():
    """MUTATION: import `SVT_INERTIA_ANNUAL_RECENT` into the split and compose with it.

    `simulation/departure_risks.py` holds the TOP of each published band clipped to a point, wired
    as a world INPUT under the director's anti-flattering tie-break. That is a defensible choice
    for a world and an inadmissible one for a check: composing the record against the world's own
    choice of where to sit inside the record would make the check agree with the world by
    construction. The bands are re-declared in the split from the same source section, and this
    leg holds both directions -- the split may not read the world, and the world may not read the
    split.
    """
    split_path = _REPO_ROOT / "tools" / "published_route_split.py"
    tree = ast.parse(split_path.read_text())
    read_from_world: list[str] = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        if any(n.startswith("simulation.departure_risks") for n in names):
            read_from_world.append(f"published_route_split.py:{node.lineno}")
    assert not read_from_world, (
        "the published check imports the world's clipped constants: "
        + ", ".join(read_from_world)
        + ". The check would then agree with the world wherever the world chose its endpoint."
    )
    split = _split_module()
    assert split.SVT_CHURN_RECENT == (0.15, 0.20) and split.SVT_CHURN_LONG_STAYER == (0.05, 0.10), (
        "the split must carry the published BANDS, not a point inside them."
    )
    offenders: list[str] = []
    for path in sorted((_REPO_ROOT / "simulation").rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            if any(n.startswith("tools.published_route_split") for n in names):
                offenders.append(f"{path.relative_to(_REPO_ROOT)}:{node.lineno}")
    assert not offenders, "the world imports the split it is judged against: " + ", ".join(offenders)


def test_a_verdict_that_turns_on_the_one_tenure_survey_says_so():
    """MUTATION: hard-code `verdict_is_mix_dependent` to False and this fires on 2018.

    THE TENURE SPLIT IS ONE SURVEY YEAR CARRIED ACROSS NINE. A verdict that holds only at the 2018
    mix is a verdict about 2018, and the honest form is to say which years those are rather than to
    widen every band until nothing can be said. 2018's own overshoot is mix-dependent -- it is
    `above` at the composed band and `overlaps` at the mix-free envelope -- which is not what the
    leg was written expecting, and is exactly why the flag is DERIVED from the two verdicts here
    rather than copied from the artefact.
    """
    split = _split_module()
    reading = split.published_route_split()
    for year, row in reading["per_year"].items():
        for basis in split.BASES:
            cell = row[basis]
            assert cell["verdict_is_mix_dependent"] == (
                cell["forward_at_phi_1"]["verdict"] != cell["forward_at_phi_1_mix_free"]["verdict"]
            ), f"{year}/{basis}: the mix-dependence flag is not derived from the two verdicts."
        robust = reading["years_above_the_band_on_every_tenure_mix"]
        for basis in split.BASES:
            above_both = (
                row[basis]["forward_at_phi_1"]["verdict"] == "above"
                and row[basis]["forward_at_phi_1_mix_free"]["verdict"] == "above"
            )
            assert (year in robust[basis]) == above_both, (
                f"{year}/{basis}: the mix-independent overshoot set disagrees with the two "
                f"verdicts it is supposed to be the intersection of."
            )
    assert any(
        row[basis]["verdict_is_mix_dependent"]
        for row in reading["per_year"].values() for basis in split.BASES
    ), (
        "no year's verdict depends on the tenure mix. Either the two bands stopped differing -- "
        "which would mean the envelope is no longer wider than the composed band and this leg is "
        "asserting nothing -- or the flag has been frozen."
    )


def test_the_committed_route_split_still_reproduces():
    """MUTATION: perturb the declared file, or move any of the three published series under it.

    A DRIFT DETECTOR THAT REDS IN EITHER DIRECTION, as its siblings over the shortfall and the
    composition do. If the commons band is corrected, or a default-tariff share is sourced for 2020,
    this goes red -- correctly, because the tree's written account of what the record can bear would
    have stopped being true. The repair is to re-run and land, never to relax the leg.
    """
    declared = _declared_route_split()
    live = _split_module().published_route_split()
    disagreements = [
        key for key in (
            "years_scored", "n_years_scored", "years_refused", "per_year",
            "published_svt_segment_churn", "published_fixed_active_renewal_share",
            "years_above_the_band_on_every_tenure_mix", "the_unestablished_quantity",
            # The joint section drifts for its own reasons -- either committed world artefact
            # being regenerated moves it -- and a section left out of this list is a published
            # figure with no drift detector on it at all.
            "where_the_worlds_joint_point_falls",
            # §13's two no-world readings. They cannot move when a world artefact is regenerated,
            # so drift here is always a published series having moved -- which is exactly the
            # event the tree's account of the record needs to go red on.
            "whether_a_constant_phi_survives_the_record_alone",
            "how_much_of_the_records_move_the_share_series_can_carry",
        )
        if declared.get(key) != live.get(key)
    ]
    assert not disagreements, (
        "the committed published route split no longer reproduces: " + ", ".join(disagreements)
        + f"\nRe-run `{declared['how_to_regenerate']}` and land it."
    )


# ---------------------------------------------------------------------------------------------
# §12 -- the JOINT reading. §9's hazard and §10's share moved together, judged at the same share.
# ---------------------------------------------------------------------------------------------


def _joint() -> dict:
    reading = _split_module().where_the_worlds_joint_point_falls()
    assert reading is not None, (
        "the joint reading returned None, which means a committed world artefact is absent. "
        "Regenerate with `python3 -m tools.fit_year_level_anchor --svt-shortfall --composition`."
    )
    return reading


def test_the_pinned_share_is_used_and_not_merely_accepted():
    """MUTATION: make `_corners` ignore `at_share` and this fires.

    THE DEFECT THIS EXISTS FOR is a refusal keyed to a signature that lifts on a parameter which is
    accepted and ignored. `at_share` is the entire mechanism by which the joint reading avoids the
    mixed comparison it was written to correct; a version that takes the argument and sweeps the
    published pair anyway would produce a plausible artefact, a green suite, and exactly the defect
    §11 shipped. So the parameter is checked at the corner enumeration itself and not through a
    caller that might not be reading it.
    """
    split = _split_module()
    year, basis = 2017, "as_published"
    swept = split._corners(year, basis)
    pinned = split._corners(year, basis, at_share=0.59)
    assert pinned is not None and swept is not None
    assert {s for _r, s in pinned} == {0.59}, (
        "`at_share` was accepted and ignored: the pinned corners still carry more than one share."
    )
    assert len({s for _r, s in swept}) == 2, (
        "the unpinned corners no longer sweep two published share endpoints, so this leg cannot "
        "tell a pinned enumeration from an unpinned one and is asserting nothing."
    )
    assert pinned != swept
    # A year with no published share is still refused WITH a share pinned: the gap is about the
    # band's year, not about `s`, and letting `at_share` manufacture a corner would score 2020.
    assert split._corners(2020, basis, at_share=0.75) is None, (
        "pinning a share scored a year the published series declares a gap in."
    )


def test_the_joint_hazard_is_judged_at_the_share_that_produced_it():
    """MUTATION: drop `at_share=share` from either reader and this fires.

    THIS IS THE WHOLE CORRECTION. §11's `phi_admitting_required` feeds a hazard solved at the
    world's share into a composition swept over both published share endpoints, and that mixture is
    what produced its "the record refuses the pair". A joint reading that repeated the mixture one
    level down -- deriving `H_joint` at `at_published_high` and then judging it over both endpoints
    -- would be the same defect wearing the fix's name, and would still be wrong in the flattering
    direction, because the swept interval is strictly wider.

    Held longhand rather than by calling the same helper the reading calls: a leg that recomputes
    with the module's own pinned call would stay green on a mutation that unpinned both of them.
    """
    split = _split_module()
    joint = _joint()
    band = split.published_departure_band()
    narrowed = 0
    for year_s, row in joint["per_year"].items():
        year = int(year_s)
        lo_r, hi_r = band[year][0] / 100.0, band[year][1] / 100.0
        for basis in split.BASES:
            for endpoint, cell in row[basis].items():
                s = cell["published_svt_account_day_share"]
                at_1 = [(r - (1.0 - s) * split.FIXED_ACTIVE_RENEWAL_SHARE) / s for r in (lo_r, hi_r)]
                at_0 = [r / s for r in (lo_r, hi_r)]
                assert cell["admissible_svt_churn_at_this_share"] == [
                    round(min(at_1), 6), round(max(at_0), 6)
                ], (
                    f"{year_s}/{basis}/{endpoint}: the admissible interval was not computed at the "
                    f"share {s} that produced the joint hazard."
                )
                for accounting, acc in cell["accountings"].items():
                    phis = [
                        (r - s * acc["joint_required_hazard"])
                        / ((1.0 - s) * split.FIXED_ACTIVE_RENEWAL_SHARE)
                        for r in (lo_r, hi_r)
                    ]
                    assert acc["phi_admitting_joint"] == [
                        round(min(phis), 6), round(max(phis), 6)
                    ], (
                        f"{year_s}/{basis}/{endpoint}/{accounting}: phi was not taken at the share "
                        f"the hazard was solved at."
                    )
                swept = split.admissible_svt_churn(year, basis)
                if swept["admissible"] != cell["admissible_svt_churn_at_this_share"]:
                    narrowed += 1
    assert narrowed, (
        "pinning the share never narrowed the admissible interval anywhere in the reading, so this "
        "leg cannot distinguish the pinned computation from the swept one it exists to refuse. "
        "Either the published shares have collapsed to a point in every year or the pin is inert."
    )


def test_the_joint_reading_never_crosses_a_basis():
    """MUTATION: judge one basis's hazard against the other basis's interval and this fires.

    The two bases are two different published POPULATIONS -- Ofgem's headline default share excludes
    prepayment and the restored one does not -- and §10 left which of them this world belongs to
    deliberately open. Taking the requirement from one and the admissible interval from the other
    would be comparing a world against a record it was not measured on, silently, and in a reading
    whose entire subject is a comparison that was mixed.
    """
    split = _split_module()
    joint = _joint()
    from tools.published_tariff_mix import default_tariff_share

    crossed = 0
    for year_s, row in joint["per_year"].items():
        year = int(year_s)
        for basis in split.BASES:
            published = default_tariff_share(year, basis)
            for endpoint, cell in row[basis].items():
                idx = split.SHARE_ENDPOINTS.index(endpoint)
                assert cell["published_svt_account_day_share"] == published[idx], (
                    f"{year_s}/{basis}/{endpoint}: the share is not this basis's {endpoint}."
                )
            other = [b for b in split.BASES if b != basis][0]
            if default_tariff_share(year, other) != published:
                crossed += 1
    assert crossed, (
        "the two bases carry identical shares in every year, so a crossed basis would be "
        "undetectable here and this leg is asserting nothing. The prepayment restoration that "
        "makes them differ has been dropped."
    )


def test_a_year_the_mixed_pair_never_refused_cannot_be_reported_as_a_flip():
    """MUTATION: report every admitted year as a flip and this fires.

    `years_the_mixed_pair_refused_and_the_joint_pair_admits` is the set §12 uses to withdraw §11's
    result 2, and a set that credited the joint reading with years the mixed reading never refused
    would be the "counterfactual crediting itself with a year it inherited" shape that §10's own
    controls exist over. It is DERIVED from the two sections here, longhand, so it cannot be
    written down.
    """
    split = _split_module()
    reading = split.published_route_split()
    joint, mixed = reading["where_the_worlds_joint_point_falls"], reading["where_the_worlds_point_falls"]
    for basis in split.BASES:
        claimed = joint["years_the_mixed_pair_refused_and_the_joint_pair_admits"][basis]
        for year_s in claimed:
            was = mixed["per_year"][year_s][basis]["phi_admitting_required"]
            assert was is not None and was[1] < 0.0, (
                f"{year_s}/{basis} is reported as a flip and the mixed pair never refused it: "
                f"phi_admitting_required = {was}."
            )
            assert all(
                not acc["record_refuses_the_joint_pair"]
                for ep in joint["per_year"][year_s][basis].values()
                for acc in ep["accountings"].values()
            ), f"{year_s}/{basis} is reported as a flip and the joint pair is refused somewhere."
        recomputed = [
            y for y, row in joint["per_year"].items()
            if (mixed["per_year"].get(y, {}).get(basis, {}).get("phi_admitting_required") or [0, 0])[1] < 0.0
            and all(
                not acc["record_refuses_the_joint_pair"]
                for ep in row[basis].values() for acc in ep["accountings"].values()
            )
        ]
        assert claimed == recomputed, (
            f"{basis}: the flip set disagrees with the two verdicts it is the intersection of."
        )


def test_a_joint_phi_above_one_is_not_reported_as_a_refusal():
    """MUTATION: flag `phi[1] > 1` as a refusal, or clip phi into [0, 1], and this fires.

    THE RECORD REFUSES THE PAIR IN TWO DIFFERENT SENTENCES AND THEY ARE NOT THE SAME FINDING. A phi
    interval entirely below zero says the fixed route would have to contribute negative departures.
    A phi interval entirely above one says the record needs more external switching from fixed
    households than the published active-renewal share can supply. Collapsing them into one boolean
    would make §12's "the record refuses the pair in no year" unreadable -- and 2023 and 2024 carry
    phi intervals whose UPPER end exceeds 1.0 while their lower end does not, which is neither
    refusal and would be miscounted as one under either collapse.
    """
    joint = _joint()
    split = _split_module()
    straddles_one = 0
    for year_s, row in joint["per_year"].items():
        for basis in split.BASES:
            for endpoint, cell in row[basis].items():
                for accounting, acc in cell["accountings"].items():
                    lo, hi = acc["phi_admitting_joint"]
                    where = f"{year_s}/{basis}/{endpoint}/{accounting}"
                    assert acc["record_refuses_the_joint_pair"] == (hi < 0.0), (
                        f"{where}: the refusal flag is not 'the whole phi interval is negative'."
                    )
                    assert acc["record_needs_more_than_the_fixed_route_can_supply"] == (lo > 1.0), (
                        f"{where}: the over-supply flag is not 'the whole phi interval exceeds 1'."
                    )
                    assert not (
                        acc["record_refuses_the_joint_pair"]
                        and acc["record_needs_more_than_the_fixed_route_can_supply"]
                    ), f"{where}: both refusals are flagged at once, which no interval can be."
                    if lo <= 1.0 < hi:
                        straddles_one += 1
    assert straddles_one, (
        "no phi interval straddles 1.0 anywhere in the reading, so a flag that fired on 'phi "
        "reaches above 1' would be indistinguishable from one that fires on 'phi exceeds 1' and "
        "this leg is asserting nothing."
    )


def test_the_joint_reading_is_wired_to_the_two_readings_and_not_to_a_column(tmp_path, monkeypatch):
    """MUTATION: return §9's required hazard as the joint one, or cache the column, and this fires.

    THE ONE DIRECTION THAT SEPARATES A RECOMPUTED READING FROM A CACHED ONE. Moving the composition
    artefact's still-required multiple must move `joint_required_hazard` proportionally and must
    leave `required_hazard_holding_the_worlds_share_fixed` -- which comes from the OTHER artefact --
    exactly where it was. A joint hazard copied from §9's column would fail the first half; one
    frozen into the committed file would fail both.

    2018 on the all-domestic basis is why this is held by perturbation and not by asserting the two
    hazards DIFFER: there the published share equals the world's to three decimals, the composition
    multiple is 1.000, and the joint hazard is legitimately identical to §9's. A leg asserting
    inequality would have been an equivalence in one year and a false red in the next world.

    The absent-artefact branch is held here too: a published reading that needs no world must not
    crash when the world's files are missing, and `None` is the declared result.
    """
    split = _split_module()
    before = split.where_the_worlds_joint_point_falls()

    perturbed = json.loads(split.COMPOSITION_ARTEFACT.read_text())
    for row in perturbed["per_year"].values():
        for basis in row["bases"].values():
            for endpoint in basis.values():
                for accounting in ("renewal_rescaled", "renewal_held"):
                    endpoint[accounting]["hazard_multiple_still_required_at_band_low"] *= 1.5
    moved = tmp_path / "composition.json"
    moved.write_text(json.dumps(perturbed))
    monkeypatch.setattr(split, "COMPOSITION_ARTEFACT", moved)
    after = split.where_the_worlds_joint_point_falls()

    for year_s, row in before["per_year"].items():
        assert (
            after["per_year"][year_s]["required_hazard_holding_the_worlds_share_fixed"]
            == row["required_hazard_holding_the_worlds_share_fixed"]
        ), f"{year_s}: §9's required hazard moved when only §10's artefact was perturbed."
        for basis in split.BASES:
            for endpoint, cell in row[basis].items():
                for accounting, acc in cell["accountings"].items():
                    now = after["per_year"][year_s][basis][endpoint]["accountings"][accounting]
                    # abs, not rel: both sides are published to six decimals and one of them is
                    # then multiplied, so the tolerance is TWO units in that last place. Every
                    # mutation this leg exists to catch -- §9's column copied in, or the reading
                    # frozen against the file -- moves the value by 1e-2 or more, four orders up.
                    assert now["joint_required_hazard"] == pytest.approx(
                        acc["joint_required_hazard"] * 1.5, abs=2e-6
                    ), (
                        f"{year_s}/{basis}/{endpoint}/{accounting}: the joint hazard did not follow "
                        f"the composition multiple. It is a cached column or it is §9's number."
                    )

    monkeypatch.setattr(split, "COMPOSITION_ARTEFACT", tmp_path / "absent.json")
    assert split.where_the_worlds_joint_point_falls() is None, (
        "the joint reading did not return a declared None with its world artefact absent."
    )
    assert split.published_route_split()["per_year"], (
        "the published reading, which needs no world at all, stopped producing one when a world "
        "artefact went missing."
    )


def test_the_one_phi_question_is_asked_of_the_unrepaired_world_too():
    """MUTATION: drop the current-hazard companion, or write the intersection down, and this fires.

    `one_phi_for_every_year` is EMPTY at the joint hazard, and §12 would have been entitled to call
    that a fact about the repair -- except that it is empty at the world's CURRENT hazard as well,
    which makes it a fact about the world's shape that predates every repair in this finding. That
    companion reading is the only thing standing between §12 and an attribution error, so it is held
    here: the field must be present, derived from the same per-year spans, and computed for both.

    THE LEG IS KEYED TO THE DERIVATION AND NOT TO TODAY'S EMPTINESS. If a future world made either
    intersection non-empty, `is_non_empty` flips and this stays green -- which is right, because the
    property being held is that the question is asked of both worlds and answered from the spans,
    not that the answer is the one §12 happened to get.
    """
    split = _split_module()
    joint = _joint()
    block = joint["one_phi_for_every_year"]
    assert "derived after the fact" in block["status"], (
        "the post-hoc label has gone. It is what stops a derivation made after the numbers were "
        "seen being read as a prediction that survived them."
    )
    for basis in split.BASES:
        companion = block["at_the_worlds_current_hazard"][basis]
        assert companion["years"], f"{basis}: the unrepaired world's companion reading is empty."
        for accounting in split.ACCOUNTINGS:
            cell = block["at_the_joint_hazard"][basis][accounting]
            assert set(cell["years"]) == set(companion["years"]), (
                f"{basis}/{accounting}: the joint and current-hazard readings cover different "
                f"years, so the comparison §12 draws from them is not like-for-like."
            )
            for name, section, key in (
                ("joint", cell, None),
                ("current", companion, "phi_admitting_the_worlds_current_hazard"),
            ):
                for year_s, span in section["years"].items():
                    spans = [
                        ep["accountings"][accounting]["phi_admitting_joint"] if key is None
                        else ep[key]
                        for ep in joint["per_year"][year_s][basis].values()
                    ]
                    assert span == [
                        round(min(s[0] for s in spans), 6), round(max(s[1] for s in spans), 6)
                    ], f"{year_s}/{basis}/{accounting}/{name}: the span is not the union over the "
                    "two share endpoints it claims to be."
                lo_i = max(s[0] for s in section["years"].values())
                hi_i = min(s[1] for s in section["years"].values())
                assert section["intersection"] == [round(lo_i, 6), round(hi_i, 6)], (
                    f"{basis}/{accounting}/{name}: the intersection was written down, not derived "
                    f"from the per-year spans."
                )
                assert section["is_non_empty"] == (lo_i <= hi_i), (
                    f"{basis}/{accounting}/{name}: the emptiness verdict disagrees with the "
                    f"interval it is supposed to be read off."
                )

    # BOTH BRANCHES, ON SPANS THIS LEG CONSTRUCTS. Every intersection in the live reading is
    # currently EMPTY, so the checks above are satisfied by `is_non_empty = False` written as a
    # constant -- and the first draft of this leg was, and stayed green under exactly that
    # mutation. The rule is a module-level pure function so the reachable-True branch can be
    # exercised here regardless of what the world says this week.
    assert split.intersect_spans([[0.1, 0.4], [0.2, 0.9], [0.15, 0.5]]) == {
        "intersection": [0.2, 0.4], "is_non_empty": True
    }, "overlapping spans did not intersect. The non-empty branch is not reachable."
    assert split.intersect_spans([[0.06, 0.10], [0.22, 0.25]]) == {
        "intersection": [0.22, 0.1], "is_non_empty": False
    }, (
        "disjoint spans did not report an empty intersection with CROSSED endpoints. The crossing "
        "is how far apart the years are and clipping it would delete the reading."
    )
    assert split.intersect_spans([[0.3, 0.3], [0.3, 0.3]])["is_non_empty"], (
        "spans touching at a single point read as empty; the intersection is closed."
    )


# ---------------------------------------------------------------------------------------------
# §13 -- the same question asked of the RECORD ALONE. No world in any of these legs.
# ---------------------------------------------------------------------------------------------


def _constant_phi() -> dict:
    return _split_module().whether_a_constant_phi_survives_the_record_alone()


def _carrying() -> dict:
    return _split_module().how_much_of_the_records_move_the_share_series_can_carry()


def test_the_phi_span_widens_with_the_segment_band():
    """MUTATION: swap the endpoints in `phi_span_at_a_segment_band` and this fires.

    `phi` is DECREASING in `H_svt`, so the span's low end comes from the band's HIGH endpoint and
    its high end from the band's LOW one. Taking them the other way round inverts every interval
    into `lo > hi`, and an inverted interval intersects with nothing: every verdict in §13 would
    read REFUSES, which is a fail-closed that is indistinguishable from a finding. That is the
    exact shape this file's catalogue calls a silent always-fail, so the direction is held rather
    than trusted to a docstring.

    Held as a PROPERTY and not against today's numbers: a strictly wider band must give a span at
    least as wide, in every year and on both bases, whatever the published series say this week.
    """
    split = _split_module()
    bands = split.svt_segment_churn_band()
    narrow, wide = bands["tenure_composed"], bands["mix_free_envelope"]
    assert wide[0] < narrow[0] and wide[1] > narrow[1], (
        "the mix-free envelope is no longer strictly wider than the tenure-composed band, so this "
        "leg is comparing a band with itself and asserts nothing."
    )
    checked = 0
    for year in sorted(split.published_departure_band()):
        for basis in split.BASES:
            n = split.phi_span_at_a_segment_band(year, basis, narrow)
            w = split.phi_span_at_a_segment_band(year, basis, wide)
            if n is None or w is None:
                continue
            checked += 1
            assert n[0] <= n[1], (
                f"{year}/{basis}: the tenure-composed phi span is INVERTED ({n}). The band's "
                f"endpoints are being read in the wrong order and every verdict below is a "
                f"fail-closed rather than a reading."
            )
            assert w[0] <= n[0] and w[1] >= n[1], (
                f"{year}/{basis}: the wider segment band gave a NARROWER phi span "
                f"({w} against {n}). phi is decreasing in H_svt, so this is the endpoints "
                f"crossed."
            )
    assert checked >= 12, (
        f"only {checked} year/basis cells were reachable; there were 16 when this was written and "
        f"a leg that has quietly stopped finding its subject reports a constant PASS."
    )


def test_the_constant_phi_verdict_is_recomputed_from_the_published_series():
    """MUTATION: write any intersection down, drop a band, or key a verdict to today's answer.

    THE LEG THAT HOLDS §13's HEADLINE. Every verdict is recomputed longhand here from
    `published_departure_band`, `default_tariff_share` and the segment band -- not by calling the
    module's own helper, which is how §12's phi-rounding defect got through its first control.

    AND BOTH BRANCHES ARE LIVE TODAY, which is why this is a control and not a drift detector:
    the tenure-composed band REFUSES a constant phi over the fitted years and the mix-free envelope
    ADMITS one. A leg that only ever saw REFUSES could be satisfied by `is_non_empty = False`
    written as a constant -- the equivalence §12 found in its own first draft -- and here it cannot
    be, because a constant would break the other band in the same run.
    """
    split = _split_module()
    reading = _constant_phi()
    seen_verdicts = set()
    for basis in split.BASES:
        for band_name, band in reading["published_segment_bands"].items():
            for set_name, years in reading["year_sets"].items():
                cell = reading["verdicts"][basis][band_name][set_name]
                assert cell["years"] == years, (
                    f"{basis}/{band_name}/{set_name}: the intersected year set is not the one the "
                    f"reading declares it is."
                )
                spans = []
                for year_s in years:
                    year = int(year_s)
                    r_lo, r_hi = split.published_departure_band()[year]
                    s_band = split.default_tariff_share(year, basis)
                    phis = [
                        (r / 100.0 - s * h)
                        / ((1.0 - s) * split.FIXED_ACTIVE_RENEWAL_SHARE)
                        for r in (r_lo, r_hi) for s in s_band for h in band
                    ]
                    longhand = [round(min(phis), 6), round(max(phis), 6)]
                    assert reading["per_year"][year_s][basis][band_name] == longhand, (
                        f"{year_s}/{basis}/{band_name}: the published phi span is not the one the "
                        f"identity gives at the corners of the two published bands."
                    )
                    spans.append(longhand)
                lo, hi = max(s[0] for s in spans), min(s[1] for s in spans)
                assert cell["intersection"] == [round(lo, 6), round(hi, 6)], (
                    f"{basis}/{band_name}/{set_name}: the intersection was written down rather "
                    f"than taken over the per-year spans."
                )
                assert cell["is_non_empty"] == (lo <= hi), (
                    f"{basis}/{band_name}/{set_name}: the verdict disagrees with the interval it "
                    f"is read off."
                )
                seen_verdicts.add(cell["is_non_empty"])
                for a, b in cell["minimal_refusing_pairs"]:
                    pa = reading["per_year"][str(a)][basis][band_name]
                    pb = reading["per_year"][str(b)][basis][band_name]
                    assert max(pa[0], pb[0]) > min(pa[1], pb[1]), (
                        f"{basis}/{band_name}/{set_name}: {a}/{b} is listed as a refusing pair and "
                        f"its two spans overlap."
                    )
    assert seen_verdicts == {True, False}, (
        f"only {seen_verdicts} appears across every band, basis and year set. One of the two "
        f"branches is unreachable, and a control whose pass branch cannot be reached reports a "
        f"constant verdict."
    )


def test_a_structural_break_is_excluded_by_name_and_still_reported():
    """MUTATION: drop 2022 from the scored set, or from `STRUCTURAL_BREAK_YEARS`, and this fires.

    Excluding a year from a headline is a judgement, and this repository's rule for one is that it
    is NAMED with its reason and its own number published beside it -- the discipline 2020 and 2021
    already get for having no share at all. 2022's exclusion is a stronger claim than theirs
    (the record HAS a figure and it is being set aside), so the bar is higher: the year must still
    appear in `per_year` with its span, its reason must be present, and the headline set must be
    exactly the scored set less the named breaks.
    """
    split = _split_module()
    reading = _constant_phi()
    breaks = reading["structural_breaks"]
    assert breaks, "the structural-break register is empty; an exclusion with no reason is a drop."
    scored = reading["year_sets"]["every_scored_year"]
    headline = reading["year_sets"]["every_scored_year_less_structural_breaks"]
    assert headline == [y for y in scored if y not in breaks], (
        "the headline year set is not the scored set less exactly the NAMED breaks. Either a year "
        "is being excluded without a reason or a named break is still in the headline."
    )
    for year_s, reason in breaks.items():
        assert year_s in reading["per_year"], (
            f"{year_s} is excluded from the headline and its own reading is not published. An "
            f"exclusion the reader cannot check is an assertion."
        )
        assert reading["per_year"][year_s]["is_a_structural_break"], (
            f"{year_s} is in the break register and its own row does not say so."
        )
        assert len(reason) > 80 and "." in reason, (
            f"{year_s}'s exclusion reason is too short to be one."
        )
        for basis in split.BASES:
            span = reading["per_year"][year_s][basis]["tenure_composed"]
            assert span is not None, f"{year_s}/{basis}: the excluded year has no published span."
    # AND THE EXCLUSION HAS TO MATTER. If the break years did not change the verdict there would be
    # nothing to justify, and a register nobody's answer turns on is a register that will rot.
    changed = [
        (basis, band)
        for basis in split.BASES
        for band in reading["published_segment_bands"]
        if reading["verdicts"][basis][band]["every_scored_year"]["is_non_empty"]
        != reading["verdicts"][basis][band]["every_scored_year_less_structural_breaks"][
            "is_non_empty"
        ]
    ]
    assert changed, (
        "excluding the structural break changes no verdict on any band or basis. Either the "
        "exclusion is doing nothing and should go, or the year sets have been wired to the same "
        "list."
    )


def test_the_mix_dependence_flag_is_derived_and_not_frozen():
    """MUTATION: freeze `verdict_is_mix_dependent`, either way, and this fires.

    §11 built this flag and §12's one-phi reading never applied it to itself. §13's headline turns
    on it entirely: the record refuses a constant phi at the tenure-composed band and admits one at
    the mix-free envelope, so the refusal is a statement about ONE 2018 survey and not about the
    record. A frozen flag would let that distinction disappear silently.

    BOTH VALUES ARE LIVE TODAY -- True for the fitted and headline sets, False for every scored
    year, where 2022 refuses on both bands -- so a constant of either polarity breaks this.
    """
    split = _split_module()
    reading = _constant_phi()
    seen = set()
    for basis in split.BASES:
        flags = reading["verdicts"][basis]["verdict_is_mix_dependent"]
        assert set(flags) == set(reading["year_sets"]), (
            f"{basis}: the mix-dependence flag does not cover every year set."
        )
        for set_name, flag in flags.items():
            expected = (
                reading["verdicts"][basis]["tenure_composed"][set_name]["is_non_empty"]
                != reading["verdicts"][basis]["mix_free_envelope"][set_name]["is_non_empty"]
            )
            assert flag == expected, (
                f"{basis}/{set_name}: the mix-dependence flag disagrees with the two verdicts it "
                f"is supposed to be derived from. It has been written down."
            )
            seen.add(flag)
    assert seen == {True, False}, (
        f"the mix-dependence flag takes only {seen} across every basis and year set, so a frozen "
        f"constant would satisfy every assertion above."
    )


def test_the_constant_pair_sweep_reports_its_slack_and_not_only_its_verdict():
    """MUTATION: return the verdict without the slack, or collapse the grid, and this fires.

    A bare `any_constant_pair_admitted: False` cannot be told apart from a sweep that never ran,
    and it does not say whether the refusal is a rounding away from admitting. The MARGIN is the
    reading: at -0.31 to -0.34 the record is refusing a constant pair by a third of phi's whole
    range, and that is a different sentence from refusing it by 0.001.

    THE SLACK IS RECOMPUTED HERE at the grid point the module names, longhand from the published
    series, so a cached number cannot satisfy it.
    """
    split = _split_module()
    reading = _constant_phi()
    for basis in split.BASES:
        pair = reading["constant_pair"][basis]
        lo_g, hi_g, step = pair["h_svt_grid"]
        assert step > 0 and (hi_g - lo_g) / step >= 1000, (
            f"{basis}: the constant-pair grid has {(hi_g - lo_g) / step:.0f} points. A coarse grid "
            f"turns a real admitting interval into a REFUSED, which is the flattering direction "
            f"for a finding that wants the record to refuse."
        )
        assert pair["years"], f"{basis}: the constant-pair sweep covers no years."
        widest = pair["widest_slack"]
        h = widest["at_h_svt"]
        assert lo_g <= h <= hi_g, f"{basis}: the widest-slack point {h} is outside its own grid."
        spans = [split.phi_admitting(int(y), basis, h) for y in pair["years"]]
        lo, hi = max(s[0] for s in spans), min(s[1] for s in spans)
        assert widest["crossed_phi_interval"] == [round(lo, 6), round(hi, 6)], (
            f"{basis}: the widest-slack interval is not the one the identity gives at the H_svt "
            f"the reading names. It is a cached column."
        )
        assert widest["slack"] == round(hi - lo, 6), (
            f"{basis}: the reported slack is not the width of the interval beside it."
        )
        assert pair["any_constant_pair_admitted"] == (
            pair["n_h_values_admitting_a_common_phi"] > 0
        ), f"{basis}: the constant-pair verdict disagrees with its own count."


def test_a_pair_the_record_requires_no_move_from_is_not_counted_as_carried():
    """MUTATION: count every pair in the denominator and this fires.

    THE PASS BRANCH THAT COULD NOT FAIL, caught on this reading's first run and repaired rather
    than recorded. Two of the seven year pairs come out `share_can_carry = True`, and in BOTH the
    record's own move interval contains zero -- the published bands are wide enough that no move is
    required, so anything carries it, including nothing at all. Counting those as evidence that the
    share series can supply the record's movement is a control keyed to an answer that is true by
    construction.

    So the denominator is held, not the verdict: a pair requiring no move must be excluded, must be
    named in the exclusion list, and the count must be over what is left.
    """
    split = _split_module()
    carrying = _carrying()
    vacuous_seen = False
    for band_name, by_basis in carrying["by_band"].items():
        for basis in split.BASES:
            cell = by_basis[basis]
            pairs = cell["pairs"]
            for name, pair in pairs.items():
                lo, hi = pair["record_move_pp"]
                requires = not (lo <= 0.0 <= hi)
                assert pair["record_requires_a_move"] == requires, (
                    f"{band_name}/{basis}/{name}: `record_requires_a_move` disagrees with whether "
                    f"the record's own move interval {pair['record_move_pp']} contains zero."
                )
                if not requires:
                    vacuous_seen = True
                    assert name in cell["pairs_excluded_because_the_record_requires_no_move"], (
                        f"{band_name}/{basis}/{name}: the record requires no move here and the "
                        f"pair is not in the exclusion list. It will be counted as carried."
                    )
            judged = {
                k: v for k, v in pairs.items()
                if v["record_requires_a_move"] and not v["spans_a_gap"]
            }
            assert cell["n_pairs_judged"] == len(judged), (
                f"{band_name}/{basis}: the denominator is not the set of pairs the record requires "
                f"a move from and which do not span the 2020-2021 gap."
            )
            assert cell["n_pairs_the_share_series_can_carry"] == sum(
                1 for v in judged.values() if v["share_can_carry"]
            ), (
                f"{band_name}/{basis}: the numerator counts pairs the denominator excludes, which "
                f"is how a vacuous carry becomes evidence."
            )
            assert cell["n_pairs_the_share_series_can_carry"] <= cell["n_pairs_judged"]
    assert vacuous_seen, (
        "no pair in the whole reading has a record move interval containing zero, so the exclusion "
        "this leg holds is never exercised and a denominator over every pair would pass it."
    )


def test_the_share_carrying_bound_is_recomputed_longhand_from_the_published_series():
    """MUTATION: flip the sign in `(H_svt - 0.35·phi)`, drop a corner, or cache the interval.

    `dV = (s2 - s1)·(H_svt - 0.35·phi)` is bilinear over the box, so the reachable interval is the
    extremes over the four corners and nothing else. Getting the second factor's sign wrong makes
    the bound symmetric about zero and the verdict much more generous -- the direction that would
    quietly let the share series carry steps it cannot.

    The gap pair is held by name too: 2019->2022 is three years, not a step, and a bound over three
    years read as a year-to-year one would be the only pair in the reading whose subject is not
    what the field says it is.
    """
    split = _split_module()
    carrying = _carrying()
    bands = split.svt_segment_churn_band()
    band_r = split.published_departure_band()
    for band_name, by_basis in carrying["by_band"].items():
        h_band = bands[band_name]
        for basis in split.BASES:
            cell = by_basis[basis]
            assert cell["pairs"], f"{band_name}/{basis}: the carrying reading has no pairs."
            for name, pair in cell["pairs"].items():
                y1, y2 = (int(p) for p in name.split("->"))
                s1 = split.default_tariff_share(y1, basis)
                s2 = split.default_tariff_share(y2, basis)
                r1, r2 = band_r[y1], band_r[y2]
                assert pair["record_move_pp"] == [
                    round(r2[0] - r1[1], 6), round(r2[1] - r1[0], 6)
                ], f"{band_name}/{basis}/{name}: the record's move is not the two bands' difference."
                reach = [
                    100.0 * ds * k
                    for ds in (s2[0] - s1[1], s2[1] - s1[0])
                    for k in (h_band[0] - split.FIXED_ACTIVE_RENEWAL_SHARE, h_band[1])
                ]
                assert pair["share_reachable_move_pp"] == [
                    round(min(reach), 6), round(max(reach), 6)
                ], (
                    f"{band_name}/{basis}/{name}: the share-reachable interval is not the corner "
                    f"extremes of (s2 - s1)·(H_svt - 0.35·phi)."
                )
                r_lo, r_hi = pair["record_move_pp"]
                v_lo, v_hi = pair["share_reachable_move_pp"]
                assert pair["share_can_carry"] == (not (v_hi < r_lo or r_hi < v_lo)), (
                    f"{band_name}/{basis}/{name}: the carry verdict is not whether the two "
                    f"intervals meet."
                )
                assert pair["spans_a_gap"] == ((y2 - y1) != 1), (
                    f"{band_name}/{basis}/{name}: the gap flag disagrees with the years in the "
                    f"pair's own name."
                )
            assert any(p["spans_a_gap"] for p in cell["pairs"].values()), (
                f"{band_name}/{basis}: no pair spans the 2020-2021 gap, so either the gap has been "
                f"filled -- which would be a sourcing event this leg should announce -- or the "
                f"consecutive-pair walk has stopped crossing it."
            )


# ---------------------------------------------------------------------------------------------
# §14 — THE SECOND TENURE OBSERVATION.
#
# §13 named the single Ofgem CES 2018 tenure split as its binding weak INPUT and asked for one
# more observation of that quantity, saying it would decide "whether the record refuses a constant
# phi or admits 0.62-0.85 of one". It was already in the tree. These legs guard the three ways
# that reading can go wrong: the register losing the DISAGREEMENT between the two instruments, the
# hull quietly widening into the mix-free envelope, and the observed-mix verdict becoming a
# constant that reads as a finding.
# ---------------------------------------------------------------------------------------------


def _turns_on_one_survey() -> dict:
    return _split_module().whether_the_constant_phi_verdict_turns_on_one_survey_year()


def test_the_tenure_register_holds_two_instruments_and_names_what_each_one_excludes():
    """MUTATION: drop the 2025 observation, blank a `population`, or blank the exclusion direction.

    THE REGISTER'S WHOLE VALUE IS THAT THE TWO OBSERVATIONS DISAGREE, and the disagreement is only
    readable if each one says what it measured. CES 2018 is a consumer survey over all domestic
    customers; RMI October-2025 is supplier-returned stock over NON-PREPAYMENT electricity
    accounts. Two points on two instruments over two populations are not a series, and a register
    that carried four bare percentages would invite the next session to difference them as a trend
    -- which is this project's most expensive recurring shape, and the reason §13's own weakness
    was a single survey year carried across nine.

    THE EXCLUSION DIRECTION IS HELD, AND A CORRECTION FACTOR IS FORBIDDEN. `published_tariff_mix`
    establishes that prepayment is ~15% of domestic accounts and >90% of it sits on a default
    tariff, so restoring it can only move the 2025 long-stayer share UP. That DIRECTION bounds the
    reading; a number would be read as established and nothing publishes one.
    """
    split = _split_module()
    obs = split.SVT_TENURE_OBSERVATIONS
    assert len(obs) >= 2, (
        f"the tenure register holds {len(obs)} observation(s). §13's entire finding was that ONE "
        f"observation cannot tell a refusal about the record from a refusal about 2018, and with "
        f"one row back in the register every §14 verdict below is about one survey year again."
    )
    assert len({o.year for o in obs}) == len(obs), (
        "two observations share a year, so the register is carrying the same reading twice and "
        "the 'observed range' it publishes is narrower than it looks."
    )
    for o in obs:
        assert o.instrument and o.population and o.source, (
            f"{o.year}: an observation with no instrument, population or source is a pair of "
            f"percentages nobody can check the base of."
        )
        assert 0.0 < o.long_stayer_share < 1.0, (
            f"{o.year}: within-segment long-stayer share {o.long_stayer_share} is not a share. "
            f"Reading the raw percentage instead of the ratio composes the segment band with the "
            f"share of ALL accounts that are long-stayer defaulters, which is a different quantity."
        )
    populations = {o.population for o in obs}
    assert len(populations) > 1, (
        "every observation declares the same population, so either the register has lost the "
        "distinction that makes the two instruments incomparable, or a population string was "
        "copied. Either way `they_are_not_a_trend` is now unsupported by the register itself."
    )
    excluding = [o for o in obs if "NON-PREPAYMENT" in o.population.upper()]
    assert excluding, (
        "no observation declares a population exclusion. The 2025 row is non-prepayment and that "
        "is what makes its long-stayer share a LOWER bound; without it the hull is being read as "
        "if both ends were unbiased."
    )
    for o in excluding:
        direction = o.restoring_the_excluded_moves_the_long_stayer_share
        assert direction, (
            f"{o.year}: the population excludes a segment and nothing says which way restoring it "
            f"would move the share. A bound with no direction is not a bound."
        )
        assert direction.split(",")[0].strip() in ("up", "down"), (
            f"{o.year}: the exclusion direction is {direction!r} and does not begin with a named "
            f"direction. A bound whose sign the reader has to infer from prose is not a bound."
        )
        # A YEAR IS A CITATION AND A MAGNITUDE IS A CORRECTION FACTOR, and only the second is
        # forbidden -- the first draft of this leg banned every digit and fired on "2018", which
        # would have pushed the provenance out of the field to keep a control green.
        assert "%" not in direction and not re.search(r"\d+\.\d", direction), (
            f"{o.year}: the exclusion direction carries a MAGNITUDE ({direction!r}). The direction "
            f"is established and the correction factor is not -- a figure here would be read as an "
            f"established one inside a week, which is the failure "
            f"`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` exists to avoid."
        )


def test_composing_at_a_mix_is_monotone_and_reaches_both_published_rows():
    """MUTATION: swap the two published rows in `compose_at_mix`, or read pct instead of the ratio.

    HELD AS A PROPERTY OVER MIXES THE REGISTER DOES NOT CONTAIN, which is what makes it a control
    over the composition rather than over today's two observations. A long-stayer churns LESS than
    a recent switcher, so the composed band must fall as the long-stayer share rises, at both
    endpoints, everywhere on [0, 1] -- and must land exactly on the long-stayer row at 1 and the
    recent row at 0.

    THE UNIT ERROR THIS CATCHES IS NOT HYPOTHETICAL. `long_stayer_share` is a RATIO within the
    segment (29/(29+23)), not the published percentage (29%). Reading the percentage gives 0.29
    where the ratio is 0.5577, which shifts the composed band by nearly 3pp of hazard and would
    have moved §14's verdict without changing a single published input.
    """
    split = _split_module()
    assert split.compose_at_mix(1.0) == split.SVT_CHURN_LONG_STAYER, (
        "a segment that is entirely long-stayer does not compose to the published long-stayer "
        "row. The two rows are the wrong way round."
    )
    assert split.compose_at_mix(0.0) == split.SVT_CHURN_RECENT, (
        "a segment with no long-stayers does not compose to the published recent row."
    )
    grid = [i / 20.0 for i in range(21)]
    for lower, higher in zip(grid, grid[1:]):
        a, b = split.compose_at_mix(lower), split.compose_at_mix(higher)
        assert b[0] < a[0] and b[1] < a[1], (
            f"raising the long-stayer share from {lower} to {higher} did not lower the composed "
            f"band ({a} -> {b}). A long-stayer churns less than a recent switcher, so this is the "
            f"two rows crossed and every band in §14 is composed backwards."
        )
    for o in split.SVT_TENURE_OBSERVATIONS:
        band = split.compose_at_mix(o.long_stayer_share)
        assert split.SVT_CHURN_LONG_STAYER[0] <= band[0] <= split.SVT_CHURN_RECENT[0], (
            f"{o.year}: composed low end {band[0]} is outside the two published low ends. A "
            f"weighted average of two numbers cannot be outside them, so the weight is not a share."
        )
        # THE MUTATION THE PARAGRAPH ABOVE CLAIMED AND THE FIRST DRAFT DID NOT CATCH. Returning
        # `long_stayer_pct / 100` survived every assertion above, because 0.29 is as valid a share
        # as 0.5577 and composes to a band that is still between the two published rows. The
        # property that separates them is that BOTH published rows are fractions of the whole
        # account base and the SVT segment is a strict subset of it -- so the within-segment share
        # must be strictly LARGER than the raw percentage read as a fraction. That is the unit
        # error's own signature and it needs no reference to today's numbers.
        assert o.long_stayer_pct + o.recent_pct < 100.0, (
            f"{o.year}: the two rows sum to {o.long_stayer_pct + o.recent_pct}% of the account "
            f"base, so the SVT segment is the whole book. Either the base has changed -- which "
            f"this leg should announce -- or the two rows are already within-segment and "
            f"re-normalising them divides the mix by itself."
        )
        assert o.long_stayer_share > o.long_stayer_pct / 100.0, (
            f"{o.year}: the within-segment long-stayer share ({o.long_stayer_share}) is not above "
            f"the published percentage read as a fraction ({o.long_stayer_pct / 100.0}). The two "
            f"rows are shares of the WHOLE account base and the segment is a subset, so this is "
            f"the raw percentage being used where the ratio belongs -- a ~3pp shift in the "
            f"composed hazard band with no published input having moved."
        )


def test_the_observed_hull_is_the_observations_hull_and_not_the_mix_free_envelope():
    """MUTATION: set `observed_mix_hull` to `mix_free_envelope`, or to one observation's band.

    THE ONE SUBSTITUTION THAT WOULD REVERSE §14's FINDING SILENTLY. The finding is that the record
    refuses a constant phi at every mix anything has OBSERVED and admits one only in the gap
    between the observed hull and the mix-free envelope. Widen the hull to the envelope and
    `refuses_at_every_observed_mix` flips to False and `admits_only_outside_every_observed_mix`
    flips with it -- the whole section reads as §13 stood, and nothing else in the artefact moves.

    Held as the RELATION, not the values: the hull must contain every observation's composed band,
    must equal the tightest such interval, and must sit strictly inside the mix-free envelope for
    as long as no observation reaches an all-long-stayer or all-recent segment.
    """
    split = _split_module()
    bands = split.svt_segment_churn_band()
    hull, envelope = bands["observed_mix_hull"], bands["mix_free_envelope"]
    composed = [split.compose_at_mix(o.long_stayer_share) for o in split.SVT_TENURE_OBSERVATIONS]
    assert hull == (min(c[0] for c in composed), max(c[1] for c in composed)), (
        f"the observed hull {hull} is not the hull of the observed composed bands {composed}. It "
        f"has been written down, or widened to a band no observation supports."
    )
    for c in composed:
        assert hull[0] <= c[0] and hull[1] >= c[1], (
            f"the hull {hull} does not contain the observed band {c}, so a verdict taken at the "
            f"hull is not a verdict over every observed mix."
        )
    assert envelope[0] < hull[0] and envelope[1] > hull[1], (
        f"the observed hull {hull} is no longer strictly inside the mix-free envelope "
        f"{envelope}. Either an observation now reaches an all-long-stayer or all-recent segment "
        f"-- which would be a sourcing event this leg should announce -- or the hull has been "
        f"replaced by the envelope, which reverses §14's finding without touching a number."
    )
    # EVERY OBSERVATION MUST GET ITS OWN BAND IN THE VERDICT, and not only be folded into the hull.
    # Dropping the per-observation bands survived the first draft of this leg: the hull still
    # spanned both observations, so nothing noticed that the 2025 mix had stopped being scored on
    # its own. §14's claim is that the record refuses at EACH observed mix, which a hull-only
    # reading cannot support -- a hull refusing says nothing about its interior.
    verdict_bands = split.phi_verdict_bands()
    for o in split.SVT_TENURE_OBSERVATIONS:
        own = [n for n, b in verdict_bands.items() if b == split.compose_at_mix(o.long_stayer_share)]
        assert own, (
            f"{o.year}: no band in the phi verdict composes to this observation's mix "
            f"{o.long_stayer_share}. It is inside the hull and scored nowhere on its own, so "
            f"`refuses_at_every_observed_mix` is really 'refuses at the hull', which is weaker."
        )
    assert set(split.observed_mix_bands()) == set(verdict_bands) - {"mix_free_envelope"}, (
        "the observed-mix band list has drifted from the verdict bands. If `mix_free_envelope` "
        "were in it, every §14 flag would read the way §13 expected and the finding would reverse."
    )

    implied = _turns_on_one_survey()["what_each_bands_endpoints_imply_about_the_segment"]
    for band_name, band in split.phi_verdict_bands().items():
        low, high = implied[band_name].values()
        assert split.compose_at_mix(low)[0] == pytest.approx(band[0], abs=1e-9), (
            f"{band_name}: the mix implied by the band's low end does not compose back to it, so "
            f"the inversion published beside the mix-free admission is not an inverse."
        )
        assert split.compose_at_mix(high)[1] == pytest.approx(band[1], abs=1e-9), (
            f"{band_name}: the mix implied by the band's high end does not compose back to it."
        )


def test_the_observed_mix_verdict_flips_when_an_observation_that_would_flip_it_is_injected(
    monkeypatch,
):
    """MUTATION: freeze any of §14's three flags, either way, and this fires.

    THE REACHABILITY LEG, AND IT INJECTS THE MISSING BRANCH RATHER THAN ASSERTING THE DERIVATION.
    All three flags are constant across today's data -- the record refuses at every observed mix on
    both bases and in every year set -- so a leg that only recomputed them from the same dict would
    be testing Python's `all()`, and a leg that only read them would pass against a written-down
    `True`. This file's own catalogue names that failure twice.

    So the branch is MANUFACTURED: two observations are injected at an all-long-stayer and an
    all-recent segment, which are the only mixes whose hull reaches the mix-free envelope. The hull
    then ADMITS while the two real observations still refuse, and all three flags must flip. No
    published number is touched -- only the register -- so a flag that does not move is a flag that
    is not derived from the verdicts it claims to summarise.
    """
    split = _split_module()
    live = _turns_on_one_survey()["by_basis"]
    for basis, by_set in live.items():
        cell = by_set["fitted_years"]
        assert cell["refuses_at_every_observed_mix"] is True, (
            f"{basis}: the record no longer refuses at every observed mix over the fitted years. "
            f"That is §14's headline and it has moved -- report it, do not adjust this leg."
        )
        assert cell["admits_only_outside_every_observed_mix"] is True, (
            f"{basis}: the mix-free envelope no longer admits where every observed mix refuses."
        )
        assert cell["the_verdict_is_the_same_at_every_observed_mix"] is True

    extreme = tuple(split.SVT_TENURE_OBSERVATIONS) + (
        split.TenureObservation(
            year=9001, long_stayer_pct=100.0, recent_pct=0.0,
            instrument="INJECTED BY A CONTROL", population="INJECTED BY A CONTROL",
            source="tests/architecture/test_switching_rate_commons.py",
            restoring_the_excluded_moves_the_long_stayer_share="",
        ),
        split.TenureObservation(
            year=9002, long_stayer_pct=0.0, recent_pct=100.0,
            instrument="INJECTED BY A CONTROL", population="INJECTED BY A CONTROL",
            source="tests/architecture/test_switching_rate_commons.py",
            restoring_the_excluded_moves_the_long_stayer_share="",
        ),
    )
    monkeypatch.setattr(split, "SVT_TENURE_OBSERVATIONS", extreme)
    widened = _turns_on_one_survey()
    assert widened["bands"]["observed_mix_hull"] == widened["bands"]["mix_free_envelope"], (
        "injecting an all-long-stayer and an all-recent observation did not widen the hull to the "
        "mix-free envelope, so this leg is not exercising the branch it claims to."
    )
    for basis, by_set in widened["by_basis"].items():
        cell = by_set["fitted_years"]
        assert cell["is_non_empty_by_band"]["observed_mix_hull"] is True, (
            f"{basis}: the widened hull still refuses, so the injection did not reach the "
            f"admitting branch and the flags below prove nothing."
        )
        assert cell["refuses_at_every_observed_mix"] is False, (
            f"{basis}: an observed mix now ADMITS and `refuses_at_every_observed_mix` is still "
            f"True. The flag is frozen, and §14's headline could not fail."
        )
        assert cell["the_verdict_is_the_same_at_every_observed_mix"] is False, (
            f"{basis}: the observed mixes now disagree with each other and the sameness flag is "
            f"still True."
        )
        assert cell["admits_only_outside_every_observed_mix"] is False, (
            f"{basis}: the admission is now INSIDE an observed mix and the flag still says it is "
            f"only outside one."
        )


def test_a_second_tenure_observation_cannot_move_the_mix_free_envelope_or_the_constant_pair():
    """MUTATION: compose the envelope from the register, or let a band reach the constant-pair sweep.

    THE ISOLATION LEG. The mix-free envelope is the outer hull of the two PUBLISHED CHURN ROWS and
    has no tenure mix in it at all; the constant-pair sweep reads no segment band whatsoever, which
    is exactly what makes it the tightest of §13's three questions. If either could move when the
    tenure register gains a row, then §14's comparison is circular -- the band that is supposed to
    be the fixed comparator would be shifting with the thing being compared -- and the finding's
    claim that phi's [0.618, 0.850] interval is UNCHANGED by the second observation would be false.

    Held by mutating the register to something absurd and requiring both to be identical.
    """
    split = _split_module()
    before_envelope = split.svt_segment_churn_band()["mix_free_envelope"]
    before_pair = _constant_phi()["constant_pair"]
    before_admission = {
        basis: _constant_phi()["verdicts"][basis]["mix_free_envelope"]["fitted_years"]
        for basis in split.BASES
    }

    absurd = (
        split.TenureObservation(
            year=9003, long_stayer_pct=1.0, recent_pct=99.0,
            instrument="INJECTED BY A CONTROL", population="INJECTED BY A CONTROL",
            source="tests/architecture/test_switching_rate_commons.py",
            restoring_the_excluded_moves_the_long_stayer_share="",
        ),
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(split, "SVT_TENURE_OBSERVATIONS", absurd)
        assert split.svt_segment_churn_band()["mix_free_envelope"] == before_envelope, (
            "the mix-free envelope moved when the tenure register changed. It is the outer hull "
            "of the two published churn rows and has no tenure mix in it; if it composes from the "
            "register then §14 is comparing a band against itself."
        )
        assert _constant_phi()["constant_pair"] == before_pair, (
            "the constant-pair sweep moved when the tenure register changed. It sweeps H_svt "
            "freely and reads no segment band -- that independence is the whole reason §13 called "
            "it the tightest of the three questions."
        )
        for basis in split.BASES:
            assert (
                _constant_phi()["verdicts"][basis]["mix_free_envelope"]["fitted_years"]
                == before_admission[basis]
            ), (
                f"{basis}: the mix-free envelope's phi admission moved when the tenure register "
                f"changed. §14 reports that interval as unchanged by the second observation and "
                f"that report would be false."
            )


# --- §15: the CIM switcher split, and the ceiling that survives its non-identification -----------


def _survey_split() -> dict:
    return _split_module().whether_the_survey_split_identifies_phi()


def test_the_sourced_switcher_split_does_not_become_the_unestablished_constant():
    """MUTATION: write phi_survey into `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS`.

    THE DEFECT THIS EXISTS FOR, and it is the one §15 was most at risk of committing. The chain
    asked for a domestic instrument separating "switched supplier" from "switched tariff with the
    same supplier" for four sections, and one arrived. The temptation on arrival is to divide its
    two rows and call the ratio phi. It is not phi: the survey's base is ALL HOUSEHOLDS, so both of
    its rows mix the SVT route with the fixed-renewal route, and phi is defined over active
    renewals at a fixed-term end alone. A number with a real citation attached to the wrong
    population is worse than the declared `None`, because the citation makes it unfalsifiable in
    review.

    Keyed to the PROPERTY -- phi is not identified by this instrument -- and not to today's span,
    so a genuinely identifying source landing later passes here and only a misattribution fails.
    """
    split = _split_module()
    reading = _survey_split()

    assert split.EXTERNAL_SHARE_OF_ACTIVE_RENEWALS is None, (
        "phi has been given a value. If a source now identifies the external share of ACTIVE "
        "FIXED-TERM RENEWALS on that population, this control should be rewritten against it -- "
        "but the CIM split does not, and its ratio must not be what filled the slot."
    )
    assert reading["the_constant_is_still"] is None
    lo, hi = reading["phi_survey_span"]
    assert lo <= hi
    assert reading["phi_survey_is_not_phi"].strip(), (
        "the reading publishes phi_survey without stating what separates it from phi. That "
        "sentence is the whole control at the reader's end."
    )
    for wave in reading["per_wave"]:
        assert wave["phi_survey"] != split.EXTERNAL_SHARE_OF_ACTIVE_RENEWALS


def test_the_renewal_route_ceiling_is_taken_at_the_most_generous_year_and_share():
    """MUTATION: take the ceiling at `min` over the window, or at the fixed band's LOW end.

    Both mutations SHRINK the ceiling, and a smaller ceiling is easier to exceed -- so both push
    §15's verdict toward the flattering answer while looking like a tightening. The verdict claimed
    is *"internal switching exceeds the whole fixed-renewal route even at the most generous
    published fixed share"*, and only the maximum over the window at the band's high end earns that
    sentence.

    Held by construction rather than by re-deriving the arithmetic: 2025's published fixed share is
    the highest in the record, so a window touching it must produce a ceiling strictly larger than
    the same window without it.
    """
    split = _split_module()
    ceiling = split._renewal_route_internal_ceiling

    with_2025 = ceiling((2023, 2025))
    without = ceiling((2023,))
    assert with_2025["ceiling"] > without["ceiling"], (
        "a window that reaches 2025 -- the record's highest published fixed share -- produced a "
        "ceiling no larger than one that does not. The ceiling is not taken at the most generous "
        "year the window touches, so the 'even at the most generous share' claim is unearned."
    )
    for years in ((2023,), (2024,), (2023, 2025)):
        cell = ceiling(years)
        band_his = [
            split.fixed_share(y, "all_domestic")[1]
            for y in years
            if split.fixed_share(y, "all_domestic") is not None
        ]
        assert cell["most_generous_fixed_share"] == max(band_his), (
            f"{years}: the ceiling did not use the HIGH end of the published fixed-share band. "
            f"The low end would understate the renewal route's reach and overstate §15's excess."
        )
        assert cell["ceiling"] == pytest.approx(
            max(band_his) * split.FIXED_ACTIVE_RENEWAL_SHARE
        )


def test_a_window_with_no_established_fixed_share_returns_no_verdict_rather_than_false():
    """MUTATION: collapse the unjudgeable branch into `False`, or drop the wave silently.

    THE MISSING BRANCH IS INJECTED, NOT ASSERTED THROUGH THE OPERATOR. Every one of the six real
    waves touches at least one year with an established fixed share, so today
    `internal_exceeds_the_renewal_routes_ceiling` is `True` in all six and the `None` branch never
    runs. A leg that only read the six would be testing `all()` over a constant. So a wave whose
    recall window touches ONLY 2020 and 2021 -- the two years `published_tariff_mix` declares as
    having no established figure -- is injected, and the reading must come back `None` for it and
    must exclude it from the denominator rather than counting it as a failure to exceed.

    `False` here would be a fail-open of the most expensive kind: it reads as "we checked this wave
    and internal switching did NOT exceed the ceiling", when nothing was checked at all.
    """
    split = _split_module()
    before = _survey_split()
    assert before["judged_waves"] == len(split.SWITCHER_SPLIT_OBSERVATIONS), (
        "some real wave is already unjudged; this control's injection no longer manufactures the "
        "branch it exists to exercise and must be rewritten."
    )

    unjudgeable = split.SwitcherSplitObservation(
        wave=9001, fieldwork="INJECTED BY A CONTROL", recall_window_years=(2020, 2021),
        base_unweighted=1000, base_weighted=1000.0,
        external_weighted=100.0, internal_weighted=900.0, net_switched_weighted=1000.0,
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            split,
            "SWITCHER_SPLIT_OBSERVATIONS",
            split.SWITCHER_SPLIT_OBSERVATIONS + (unjudgeable,),
        )
        after = _survey_split()

    injected = [w for w in after["per_wave"] if w["wave"] == 9001]
    assert len(injected) == 1, "the unjudgeable wave was dropped from the reading entirely."
    cell = injected[0]
    assert cell["internal_exceeds_the_renewal_routes_ceiling"] is None, (
        "a wave whose window has no established fixed share came back with a BOOLEAN verdict. "
        "There is no ceiling to exceed, so there is no verdict -- and `False` would read as a "
        "wave that was checked and passed."
    )
    assert cell["renewal_route_internal_ceiling"]["ceiling"] is None
    assert cell["renewal_route_internal_ceiling"]["years_with_no_established_fixed_share"] == [
        2020, 2021,
    ], "the unestablished years were not NAMED. A dropped year cannot be audited."
    assert after["judged_waves"] == before["judged_waves"], (
        "the unjudgeable wave entered the denominator. A verdict of 'every judged wave exceeds' "
        "must not be diluted or inflated by a wave that could not be judged."
    )
    assert after["internal_exceeds_the_renewal_routes_ceiling_in_every_judged_wave"] is True


def test_the_overlap_comes_from_the_published_union_and_one_wave_has_one():
    """MUTATION: use the SUM of the two rows as phi_survey's denominator instead of the published net.

    The survey's `Net: Have switched` is a UNION, not a sum: a respondent may report both actions.
    In waves 2-6 the two coincide, so a reading that summed would agree with a reading that used
    the net and nothing would notice. **Wave 1 is the one that separates them** -- its sum exceeds
    its published union by 14.4 weighted respondents -- so the register keeps the net as published
    and the overlap is derived from it.

    Requiring a non-zero overlap to EXIST is what stops this leg being satisfied by a register that
    happened to store equal values, which is the shape §13's own pass-branch defect had.
    """
    split = _split_module()
    overlaps = {o.wave: o.both_actions_overlap for o in split.SWITCHER_SPLIT_OBSERVATIONS}
    assert any(v > 1.0 for v in overlaps.values()), (
        "no wave in the register reports both actions from the same respondents. The published "
        "union would then be indistinguishable from the sum and this leg could not fire."
    )
    for obs in split.SWITCHER_SPLIT_OBSERVATIONS:
        assert obs.net_switched_weighted <= obs.external_weighted + obs.internal_weighted + 1e-3, (
            f"wave {obs.wave}: the published union exceeds the sum of its own parts."
        )
        assert obs.external_share_of_switching == pytest.approx(
            obs.external_weighted / obs.net_switched_weighted
        ), (
            f"wave {obs.wave}: phi_survey is not taken over the published union. Summing the rows "
            f"would double-count respondents who did both and understate the external share."
        )


def test_the_ceiling_verdict_is_taken_on_the_un_annualised_recall_window():
    """MUTATION: annualise the internal rate before comparing it with the ceiling.

    The ceiling is an ANNUAL quantity -- `(1 - s) * 0.35` is renewals per account-year -- and the
    survey's rate is over six months. Annualising the survey side would be arithmetically defensible
    and is deliberately NOT done, because every verdict it feeds has the form "internal switching
    already exceeds this ceiling", and annualising only raises the left-hand side. Comparing the raw
    six-month rate against an annual ceiling is therefore the conservative comparison, and it means
    §15's result survives without any annualisation convention being load-bearing.

    Keyed to the property that the comparison is conservative, not to today's multiples.
    """
    split = _split_module()
    reading = _survey_split()
    for obs, cell in zip(split.SWITCHER_SPLIT_OBSERVATIONS, reading["per_wave"], strict=False):
        assert cell["wave"] == obs.wave
        assert cell["internal_rate_of_all_households"] == pytest.approx(
            obs.internal_weighted / obs.base_weighted, abs=1e-6
        ), (
            f"wave {obs.wave}: the rate compared against the ceiling is not the raw recall-window "
            f"rate. Any annualisation inflates the left-hand side of a 'already exceeds' claim."
        )
        if cell["multiple_of_the_ceiling"] is not None:
            assert cell["multiple_of_the_ceiling"] == pytest.approx(
                cell["internal_rate_of_all_households"]
                / cell["renewal_route_internal_ceiling"]["ceiling"],
                rel=1e-3,
            )
