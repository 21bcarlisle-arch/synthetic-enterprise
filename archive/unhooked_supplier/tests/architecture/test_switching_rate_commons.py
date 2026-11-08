# ARCHIVED LEGS of tests/architecture/test_switching_rate_commons.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/architecture/test_switching_rate_commons.py.
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
from simulation.household_segments import engagement_level_for_customer

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







# ═══════════════════════════════════════════════════════════════════════════════════════════
# (b) THE LANE READINGS — inside the band, on the declared denominator
# ═══════════════════════════════════════════════════════════════════════════════════════════







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








#: The PRESENT-TENSE grammar for a live floor claim inside an `UNFITTED_YEARS` cause. A superseded
#: claim is quoted in the PAST tense (`floor was X%`) and is deliberately outside this pattern:
#: the entries keep their own corrected history beside them, and a leg that could not tell a
#: quotation from a claim would force the history to be deleted to stay green.
_LIVE_FLOOR_CLAIM = re.compile(r"SVT floor is ([0-9.]+)% against a published ([0-9.]+)%")


def _floor_claims(causes) -> list[tuple[int, float, float]]:
    """EVERY present-tense floor claim in every cause, not the first one in each.

    READ WITH `finditer`, AND THE YEAR IS NOT A KEY. Until 2026-09-19 the leg below read
    `_LIVE_FLOOR_CLAIM.search(cause)` and stored the result in a dict keyed by year. Both halves
    dropped a second claim, and they drop it the same silent way: a cause that states two floors
    registers one, and the second is not judged WRONGLY -- it is never asked about. A dropped match
    is an ABSENT QUESTION, not a wrong answer, which is why no assertion downstream can notice.
    Returning a flat list rather than a mapping is the half that has to come with the `finditer`:
    keeping the year as a dict key would let the wider read find both and then overwrite one.

    LATENT, NOT LIVE, WHEN THIS LANDED. Measured at `087e3ad58`: each pattern finds exactly one
    match per cause today (2022 only). It becomes live the moment a cause gains a second floor
    sentence or the grammar is widened -- and `087e3ad58` was the widening that made the sibling
    case live in an afternoon.
    """
    return [
        (year, float(found.group(1)), float(found.group(2)))
        for year, cause in causes.items()
        for found in _LIVE_FLOOR_CLAIM.finditer(cause)
    ]

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
            engagement_level=engagement_level_for_customer(row["customer_id"]).value,
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




#: A cause's claim about the rows a NAMED capture holds for the year it refuses. The grammar is
#: `<file>.json ... ALL <n> OF THOSE ROWS CARRY \`passive_churn_cap = <v>\``, and the file must be
#: named before the claim in the same cause, and in practice IMMEDIATELY before it.
#:
#: THE GAP CANNOT DISAMBIGUATE AND NO VARIANT OF IT CAN. Measured 2026-09-19 on
#: `alpha.json and beta.json are both cited. ALL 53 ... ; ALL 7 ...` -- two files named before two
#: claims -- this grammar reads `alpha` and drops the second claim, and a gap tempered against a
#: second `.json` reads `beta` and drops the second claim. Two wrong answers, not one right one.
#: So the tempering was NOT landed: it changes which file a mis-paired claim names without
#: registering the claim that is lost either way. Filed as its own finding rather than half-fixed
#: here; `_cited_rows_claims` below holds the shape that IS expressible.
_CITED_ROWS_CLAIM = re.compile(
    r"(?P<capture>[a-z0-9_]+\.json).{0,900}?ALL (?P<rows>\d+) OF THOSE ROWS CARRY "
    r"`passive_churn_cap = (?P<cap>[0-9.]+)`",
    re.S,
)


def _cited_rows_claims(causes) -> list[tuple[int, str, int, float]]:
    """EVERY cited-rows claim in every cause, on the same rule as `_floor_claims` above.

    WHAT THIS REGISTERS AND WHAT IT STILL CANNOT. A cause that names a capture and then states its
    claim, twice over, now registers both. A cause that names BOTH captures first and then states
    both claims registers one claim bound to one of the two files, and which file it picks is an
    artefact of the gap (see the pattern's own comment). That second shape is a real remaining
    hole, it is not fixed here, and it is filed rather than papered over -- the reason being that
    every candidate repair measured on 2026-09-19 swapped one mis-pairing for another without
    registering the lost claim.
    """
    return [
        (year, found.group("capture"), int(found.group("rows")), float(found.group("cap")))
        for year, cause in causes.items()
        for found in _CITED_ROWS_CLAIM.finditer(cause)
    ]






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
    # --- simulation/arrival_route: the switching rate as a DENOMINATOR TERM, not as a level ---
    "simulation.arrival_route:default_tariff_arrival_share":
        "reads the published switching band as ONE TERM of a ratio, and the ratio is over a "
        "different population in a different direction. The band counts DEPARTURES over all GB "
        "domestic electricity accounts; this returns the share of the accounts a supplier OPENS "
        "in a year that open on the incumbent's default tariff -- `m / (m + s)`, move-ins over "
        "move-ins plus switches. Registering it would hold an arrival share to a departure band, "
        "which is the before-you-divide defect this file exists over. What IS held is that it "
        "moves with the series: `tests/simulation/test_the_default_tariff_arrival_producer.py::"
        "test_the_arrival_share_MOVES_WITH_the_published_switching_record` keys it to the 2022 "
        "switching collapse rather than to any value it returns.",
    "simulation.arrival_route:arrival_tariff_type":
        "the caller of the share above -- turns it into a product label for one drawn arrival. It "
        "carries no series of its own and holds no level; it compares a caller-supplied roll "
        "against the share and returns a string or `None`.",
    # --- tools/run_value_cycle_ab: an ENVIRONMENT-SWITCH regex, not a switching rate ---
    # Not authored here. The world-stamp lane landed it (77a872e01's line) and left this leg red
    # for every lane; classified in the same pass as the C29 landing that met it.
    "tools.run_value_cycle_ab:_SWITCH_NAME":
        "`re.compile(...SE_[A-Z0-9_]+...)` -- the pattern that finds the names of the `SE_*` "
        "environment switches a run reads, for the world stamp. 'Switch' here is a behaviour "
        "flag, not a household changing supplier: it returns strings, reads no published "
        "series, and has no year or rate to hold to the switching band.",
    # --- tools/fit_year_level_anchor: a SWEEP GRID, not a series ---
    # Not authored here. It landed with the exposure-restricted incidence measurement on
    # 2026-09-19 and left this census leg red for every lane, which is why it is classified in
    # the same pass rather than routed around.
    "tools.fit_year_level_anchor:_BASE_RESTRICTION_THRESHOLDS":
        "`tuple(i / 10.0 for i in range(11))` -- the 0.0-to-1.0 grid two restrictions are SWEPT "
        "at, and its own comment says why it is a grid and not a chosen point. It reads no "
        "published series, carries no year, and holding eleven evenly spaced tenths to the "
        "switching band would be holding the x-axis to the y-axis.",
    # --- tools/couple_value_based_pricing: RUN IDENTITY, not a reading of anything ---
    # Not authored here either, and the same shape as the row above: the provenance-stamping lane
    # landed these at c4809c5fc/79f7484f3 and left this census leg red for EVERY lane, so they are
    # classified in the same pass rather than routed around. The discoverer matches them because
    # they are module-level values from a call, which is the right net to cast -- a run identity
    # and a departure level look identical to it, and that is exactly why the reason is written
    # down instead of the shape being excluded.
    "tools.couple_value_based_pricing:PRODUCING_COMMIT":
        "`_git_head()` -- WHICH CODE priced the arms, resolved at import. A commit sha, not a "
        "rate: there is no published band a sha could be held to, and its own comment says a run "
        "that cannot resolve one publishes `None` and the reason rather than a wrong sha.",
    "tools.couple_value_based_pricing:PRODUCING_COMMIT_RESOLVED_AT":
        "the UTC instant the sha above was resolved at. A timestamp carries no level; it exists "
        "so a reader can tell that the commit was bound at process start and not at artefact "
        "assembly, which is a later tree.",
    "tools.couple_value_based_pricing:WORLD_IDENTITY":
        "WHICH WORLD the arms were priced in -- a dict of anchors, not a rate over the book. It "
        "is the thing that makes a departure-level re-fit visible to a later reader, so holding "
        "it to the switching band would hold the LABEL of a world to a quantity measured inside "
        "it. The levels it names are held where they are defined, in "
        "`simulation.departure_level_anchor`.",
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
    # --- company/crm/enriched_churn_estimate: a PER-CHANNEL relative factor, not a book level ---
    # Classified 2026-09-07 by the delivery seat. These three landed with `fdfa0c94f` and were
    # discovered-but-unclassified, which is a standing red at HEAD that wedges every commit
    # selecting this file. Same shape as `admissible_svt_churn` above: a within-segment quantity,
    # not a rate over the book.
    "company.crm.enriched_churn_estimate:payment_method_engagement_reading":
        "a RELATIVE factor for one payment channel -- how much more or less this channel shops "
        "than the market -- blended from a prior as wide as the published CIM spread and this book's own realised "
        "losses. It is a MULTIPLIER around 1.0, not a rate: holding it to the published band "
        "would compare a dimensionless ratio with a per-cent level, which is the "
        "say-what-each-number-counts defect this file exists over. The level it scales IS "
        "registered; this is the scaling.",
    "company.crm.enriched_churn_estimate:derived_payment_method_engagement_factor":
        "the drop-in accessor over `payment_method_engagement_reading` above, returning that "
        "same multiplier. Outside a run scope it returns the prior unchanged, so it "
        "carries no book level of its own at all.",
    "company.crm.enriched_churn_estimate:_CIM_ENGAGEMENT_PRIOR_LOG_VARIANCE":
        "a VARIANCE in log space -- the dispersion the published CIM survey shows ACROSS payment "
        "methods, used as the prior's precision when blending. It is a second moment of a set of "
        "ratios and there is no level in it to hold; the band is a first moment of a rate.",
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




















# ═══════════════════════════════════════════════════════════════════════════════════════════
# (e) THE MARGIN — a threshold crossing is not a magnitude, and the instrument must say which
# ═══════════════════════════════════════════════════════════════════════════════════════════





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










def _assert_the_two_phi_refusals_are_distinct(joint: dict, split) -> tuple[int, int]:
    """Assert both refusal flags over every cell; return (straddling 1.0, wholly above 1.0)."""
    straddles_one = wholly_above_one = 0
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
                    if lo > 1.0:
                        wholly_above_one += 1
    return straddles_one, wholly_above_one








# ---------------------------------------------------------------------------------------------
# §13 -- the same question asked of the RECORD ALONE. No world in any of these legs.
# ---------------------------------------------------------------------------------------------


def _constant_phi() -> dict:
    return _split_module().whether_a_constant_phi_survives_the_record_alone()


def _carrying() -> dict:
    return _split_module().how_much_of_the_records_move_the_share_series_can_carry()


#: A BAND WITH WIDTH, for the reachability arms of the legs below and for nothing else. Since
#: 2026-10-03 the commons states each year as DESNZ QEP 2.7.1 prints it, a published count's
#: rounding about 0.004pp wide, so on the live record the phi spans have almost no width and
#: several branches these legs must prove reachable cannot be reached from live data at all
#: (measured: all six went red on that edit alone). These are the commons' version-1 bands, retired
#: as a RECORD because the publisher refuted them in 8 of 10 years, and kept here only as an input
#: whose width is known to reach both branches. Every value check still runs on the live record.
_A_BAND_WITH_WIDTH = {
    2016: (17.0, 17.6), 2017: (13.5, 14.0), 2018: (19.5, 20.0), 2019: (20.7, 21.3),
    2020: (22.5, 23.0), 2021: (17.9, 18.4), 2022: (2.9, 4.3), 2023: (8.9, 12.5),
    2024: (12.5, 16.1), 2025: (14.3, 17.9),
}


def _band_sources(monkeypatch):
    """Yield `"live"`, then `"with_width"` with the route split reading `_A_BAND_WITH_WIDTH`."""
    yield "live"
    monkeypatch.setattr(
        _split_module(), "published_departure_band", lambda: dict(_A_BAND_WITH_WIDTH)
    )
    yield "with_width"
















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












# --- §15: the CIM switcher split, and the ceiling that survives its non-identification -----------


def _survey_split() -> dict:
    return _split_module().whether_the_survey_split_identifies_phi()












# ═══════════════════════════════════════════════════════════════════════════════════════════════
# §16 — THE WORLD ALREADY RUNS THE INTERNAL RE-CONTRACT ROUTE §15 SAID IT LACKED
# ═══════════════════════════════════════════════════════════════════════════════════════════════
#
# §15 concluded that a default/SVT household re-contracting with its EXISTING supplier is "a route
# `simulation/renewals.py` does not model at all". That was a grep for `same_supplier`, and the grep
# was right. `simulation/renewals.py` bounds a passive stint at the household's next anniversary and
# re-enters its own term loop there, so an active draw at that anniversary builds a fixed term with
# this same supplier. The route is modelled, it was unnamed, and until §16 it was unmeasured.
#
# These legs hold the three things that measurement turns on and that a later session could quietly
# lose: that a stint boundary is a real move and not a recorder artefact, that a return is credited
# to the stint it belongs to, and that the two rates the reading publishes are different quantities
# with different denominators. The two comparisons against the record get one leg each.


def _declared_internal_return() -> dict:
    """The committed internal-return reading, or a hard fail naming which state it is in.

    The same three states and the same reason as `_declared_shortfall`: absent, refused, or a
    reading. The middle one is a result and is reported rather than skipped.
    """
    assert fitter.INTERNAL_RETURN.exists(), (
        f"{fitter.INTERNAL_RETURN.name} is missing. The tree then carries §15's claim that the "
        f"world has no internal re-contract route and nothing measuring the route it does have. "
        f"Run `python3 -m tools.fit_year_level_anchor --internal-return`."
    )
    declared = json.loads(fitter.INTERNAL_RETURN.read_text())
    assert "refused" not in declared, (
        f"the internal-return reading is a REFUSAL and not a reading: {declared['refused']}. "
        f"Whether the world runs the route at all is then unestablished, which is the state §16 "
        f"was written to end."
    )
    return declared


def _live_internal_return() -> dict:
    svt_rows, _reason = departure_population.load_svt_decisions(instrument.DEFAULT_TABLE)
    rows = json.loads(instrument.DEFAULT_TABLE.read_text())
    return fitter.svt_internal_return_and_tenure(rows, svt_rows)




def _date(iso: str):
    import datetime as _dt
    return _dt.date.fromisoformat(iso)














