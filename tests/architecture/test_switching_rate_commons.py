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
    "marker to come off, and it is a capture-population question, not a calibration one. "
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
    "NOT_ABOUT_2026-08-31.md and docs/staging/SEAT_FINDING_THE_INSTRUMENT_JUDGES_THE_WORLD_ON_A_"
    "SUPERSEDED_CAPTURE_WHOSE_SVT_HALF_IS_IN_NO_COMMIT_2026-09-03.md."
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
