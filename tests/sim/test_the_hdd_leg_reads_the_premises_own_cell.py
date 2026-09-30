"""THE DEFECT: the gas/HDD leg resolved a premise's weather by a STRING RULE over four filenames.

`sim.weather_hdd._resolve_source_cid` stripped a trailing `g` and otherwise passed the
`customer_id` through, then looked for `sim/weather_data/{id}.csv`. Ten of the book's eighteen
premises matched no filename, found no file, and `get_hdd` returned `REFERENCE_MONTHLY_HDD[month]
/ 30.0` -- the 1991-2020 England & Wales monthly normal -- silently, as a plausible HDD nothing
downstream could distinguish from weather. C1 and C7 are the SAME COORDINATE and read annual HDD
12-20% apart purely because one id matched a filename.
(`docs/staging/WORKER_FINDING_THE_HDD_LEG_IS_A_THIRD_RESOLVER_AND_TEN_OF_EIGHTEEN_PREMISES_GET_A_
CLIMATE_NORMAL_INSTEAD_OF_WEATHER_2026-09-21.md`, BLOCKING, W1_14.)

WHY THIS IS ONE TEST OVER THE WHOLE PARTITION AND NOT A LEG PER PREMISE. A resolver that returns
the normal for EVERYTHING satisfies every assertion about what the normal looks like, and a
resolver that returns a cell for everything satisfies every assertion about what weather looks
like. Only a control that binds BOTH SIDES AT ONCE -- a premise the store holds a cell for and a
premise it does not, in a single test -- can go red when the resolver stops discriminating. That
is the `assert plan["restart"] and plan["defer"] and plan["hold"]` shape, and the reason for it is
that this repo has entered the rare-branch-unreachable trap three times through three doors.
"""

import ast
import re
from pathlib import Path

import pytest

from sim.weather_hdd import (
    NORMAL_BASIS_PREFIX,
    REFERENCE_MONTHLY_HDD,
    get_hdd,
    hdd_reading,
)

#: A premise the store holds a cell for. C7 is one of the ten that read the normal before
#: 2026-09-21: resi electricity at 51.5074,-0.1278, the same London coordinate as C1, which DID
#: hold an archive. Measured annual HDD 2018: 2086.1 from the normal against 1560.1 from its own
#: cell (+33.7%); 2022: 2086.1 against 1367.4 (+52.6%).
HELD = "C7"

#: The archived premise at C7's EXACT coordinate. The old resolver gave these two different
#: weather; one cell is one sky, so they must now be identical day for day.
HELD_TWIN = "C1"

#: A premise the store holds NO cell for, ADOPTED into the id door at a coordinate no build of the
#: store reaches: Lerwick, ~317 km from the nearest held cell against a `MAX_SNAP_KM` of 5.0. WAS
#: `"C_IC1"` (Birmingham, 7.4 km, then 5.5 km out) -- today's answer, and it went stale the day its
#: cell was added (2026-09-30). The property is "a premise outside the store", so the subject is
#: one that is outside by construction rather than one that happens to be outside this week.
REFUSED = "TEST-OUTSIDE-THE-STORE"
REFUSED_RECORD = {"customer_id": REFUSED, "commodity": "gas",
                  "location": {"lat": 60.155, "lon": -1.145, "region": "Lerwick"}}

#: Two mid-January days ten degrees of winter apart in the real record. 2022 is a fact, not a
#: scenario: a premise on the normal reads the SAME number in both, which is the whole defect.
COLD_YEAR_DAY = "2018-01-15"
MILD_YEAR_DAY = "2022-01-15"


@pytest.fixture
def _no_adopted_book():
    """`adopt_book` is process state; every control here starts from none and leaves none."""
    from sim import weather_hdd
    from simulation import weather_inputs

    saved = dict(weather_inputs._BOOK)
    weather_inputs._BOOK.clear()
    weather_hdd._WEATHER_CACHE.clear()
    yield
    weather_inputs._BOOK.clear()
    weather_inputs._BOOK.update(saved)
    weather_hdd._WEATHER_CACHE.clear()


def test_the_resolver_discriminates_a_premise_with_a_cell_from_one_without(_no_adopted_book):
    """ONE control over the whole partition. Reds if the resolver answers one way for everything.

    Make `_premise_sky` return an empty series for every id and the HELD leg reds (it reads the
    normal, and its two years collapse to one number). Make it return a cell for every id and the
    REFUSED leg reds (its basis no longer names the substitution). Neither mutation survives.
    """
    from simulation.weather_inputs import adopt_book

    adopt_book([REFUSED_RECORD])
    held_cold = hdd_reading(COLD_YEAR_DAY, HELD)
    held_mild = hdd_reading(MILD_YEAR_DAY, HELD)
    refused_cold = hdd_reading(COLD_YEAR_DAY, REFUSED)
    refused_mild = hdd_reading(MILD_YEAR_DAY, REFUSED)

    # Side one: the store holds this premise's cell, so it reads the WORLD'S weather...
    assert not held_cold.from_normal, (
        f"{HELD} sits in a cell the store holds every day of; reading the normal for it is the "
        f"defect this control exists for. basis={held_cold.basis!r}"
    )
    assert not held_mild.from_normal, f"{HELD} on {MILD_YEAR_DAY}: basis={held_mild.basis!r}"
    assert held_cold.basis.startswith("cell "), held_cold.basis
    # ...and therefore CAN see the difference between two winters. The normal cannot: this is the
    # property, not today's answer -- any two days whose cell temperatures differ satisfy it.
    assert held_cold.hdd != held_mild.hdd, (
        f"{HELD} read the identical HDD on {COLD_YEAR_DAY} and {MILD_YEAR_DAY}, which is what a "
        "climate normal does and what its own cell cannot"
    )

    # Side two: the store holds NO cell for this premise, so the normal stands in -- and SAYS SO.
    assert refused_cold.from_normal, (
        f"{REFUSED} is far outside the store; a reading that claims to be weather for it is "
        f"claiming a cell that does not exist. basis={refused_cold.basis!r}"
    )
    assert refused_cold.basis.startswith(NORMAL_BASIS_PREFIX), refused_cold.basis
    # WAS `"7.4 km" in basis` -- today's answer, and it went red when the store grew and the
    # nearest held cell moved to 5.5 km, though the refusal was as honest as ever. The property is
    # that the reason names a distance and the cell it was measured to.
    assert re.search(r"\d+(\.\d+)? km from the nearest cell the store holds \(E\d+N\d+\)",
                     refused_cold.basis), (
        "the substitution must name its reason, not merely declare itself: "
        f"basis={refused_cold.basis!r}"
    )
    # The substituted number is flat across the record, which is exactly why it must be named.
    assert refused_cold.hdd == refused_mild.hdd == REFERENCE_MONTHLY_HDD[1] / 30.0

    # And the two sides are different answers to the same question, which is the discrimination
    # a one-way resolver cannot make. Written as one assertion so no single leg can carry it.
    assert held_cold.from_normal is not refused_cold.from_normal


def test_two_premises_at_one_coordinate_read_one_sky():
    """C1 and C7 are the same point. The old resolver had them 12-20% apart on annual HDD.

    EQUIVALENCE, NOT A MISSING TEST, under both one-way mutations of `_premise_sky`: a resolver
    that hands every id the same sky satisfies this by construction. Established rather than
    assumed -- the mutations that DO reach it are ones that reintroduce a per-id rule, which is
    the defect this leg is about, and the partition control above is what catches the one-way
    resolvers. Recorded here so the next reader does not take the green as coverage it is not.
    """
    for day in (COLD_YEAR_DAY, MILD_YEAR_DAY):
        assert get_hdd(day, HELD) == get_hdd(day, HELD_TWIN), (
            f"{HELD} and {HELD_TWIN} share a coordinate; a difference between them on {day} is "
            "attributable to nothing in the world"
        )


def test_no_registered_premise_the_store_holds_a_cell_for_reads_the_normal():
    """The whole book, not a sample: the claim is about the partition, so ask every premise.

    FAIL-CLOSED ON AN EMPTY BOOK. A roster this could not read would make the loop vacuous and
    the assertion green, which is the "a control's own filters empty the evidence" shape; the
    count is asserted first so an empty book reds instead.
    """
    from company.interfaces.supply_book import registered_supply_points
    from simulation.weather_inputs import cell_weather_for_customer_id

    book = registered_supply_points()
    assert len(book) >= 18, f"the supply book returned {len(book)} points; nothing to control"

    on_the_normal = []
    for customer in book:
        cid = customer["customer_id"]
        has_cell = bool(cell_weather_for_customer_id(cid).series)
        reading = hdd_reading(COLD_YEAR_DAY, cid)
        if has_cell and reading.from_normal:
            on_the_normal.append((cid, reading.basis))

    assert not on_the_normal, (
        "premises whose cell the store holds are still reading a climate normal: "
        f"{on_the_normal}"
    )


def test_an_unregistered_id_is_refused_by_name_rather_than_answered():
    """A typo'd id used to resolve to itself, find no CSV, and settle on the normal in silence."""
    reading = hdd_reading(COLD_YEAR_DAY, "NOT_A_SUPPLY_POINT")
    assert reading.from_normal
    assert "not a registered supply point" in reading.basis, reading.basis
    assert reading.hdd == pytest.approx(REFERENCE_MONTHLY_HDD[1] / 30.0)


def test_a_drawn_gas_premise_reads_its_cell_once_the_runner_adopts_its_book(_no_adopted_book):
    """THE DEFECT (2026-09-30): the id-only door scanned the 18 registered points and nothing else.

    `run_phase2b` settles 95 gas premises and 91 are drawn `SYN-*`/`PROS-*` households, so every
    one of them read the monthly normal -- 2018 and 2022 identical -- while
    `weather_refusals_for_book` over the same records said 0 refused. Measured: their 2022 HDD
    falls 16.4% on the mean once they read their cells. `test_no_registered_premise_...` above
    asked the roster and was green throughout; this asks the book the run actually settles.

    ONE control over the partition: before adoption the drawn premise MUST read the normal (so the
    adoption is what moved it, not a resolver that answers a cell for everything), after it MUST
    NOT, and the registered-roster premise must be unaffected either way.
    """
    from simulation.run_phase2b import ELEC_CUSTOMERS, GAS_CUSTOMERS, SUCCESSOR_ELEC_CUSTOMERS
    from simulation.weather_inputs import adopt_book, cell_weather_for_customer

    drawn = [c for c in GAS_CUSTOMERS if c["customer_id"] not in {HELD, HELD_TWIN, REFUSED}
             and not c["customer_id"].startswith("C")]
    assert len(drawn) >= 50, f"{len(drawn)} drawn gas premises; nothing to control"
    held = [c for c in drawn if cell_weather_for_customer(c).series]
    assert held, "the store holds a cell for none of the drawn gas premises"
    subject = held[0]["customer_id"]

    before = hdd_reading(COLD_YEAR_DAY, subject)
    assert before.from_normal, f"{subject} read weather before any book was adopted: {before}"

    adopt_book(ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS)

    on_the_normal = [c["customer_id"] for c in held
                     if hdd_reading(COLD_YEAR_DAY, c["customer_id"]).from_normal]
    assert not on_the_normal, (
        f"{len(on_the_normal)} of {len(held)} drawn gas premises whose cell the store holds still "
        f"read the normal after adoption: {on_the_normal[:5]}"
    )
    assert hdd_reading(COLD_YEAR_DAY, subject).hdd != hdd_reading(MILD_YEAR_DAY, subject).hdd
    assert not hdd_reading(COLD_YEAR_DAY, HELD).from_normal


def test_the_runner_adopts_the_gas_book_it_settles():
    """The door above is inert unless the runner calls it with the records it settles gas for.

    An AST call, not a text grep: the comment beside the call names `adopt_book` too, and a grep
    would stay green on the comment after the call was deleted.
    """
    tree = ast.parse(Path("simulation/run_phase2b.py").read_text())
    adopted = [
        {n.id for n in ast.walk(call) if isinstance(n, ast.Name)}
        for call in ast.walk(tree)
        if isinstance(call, ast.Call) and getattr(call.func, "id", None) == "adopt_book"
    ]
    assert any("GAS_CUSTOMERS" in names for names in adopted), (
        f"run_phase2b never calls adopt_book with GAS_CUSTOMERS (calls found: {adopted}); every "
        "drawn gas premise's HDD would read the 1991-2020 monthly normal"
    )


def test_every_registered_premise_has_a_cell_whatever_the_curriculum_serves():
    """The world's weather covers the whole registered roster, not the segments sold to today.

    THE DEFECT (2026-09-30): `tools.build_weather_world.book_cells` built the store from
    `run_phase2b.CUSTOMERS`, which the served-segments CURRICULUM filters to resi and SME. So
    C_IC1/C_IC2 (Birmingham, I&C) had no cell, and a curriculum that turned I&C on would have met
    a world that refused them. The world is decided blind to the curriculum. Red at the store as it
    stood before the Birmingham cell was added; asked of the roster, not the served book, so a
    curriculum change cannot empty it.
    """
    from company.interfaces.supply_book import registered_supply_points
    from simulation.weather_inputs import cell_weather_for_customer_id

    book = registered_supply_points()
    assert len(book) >= 18, f"the supply book returned {len(book)} points; nothing to control"
    assert any(c.get("segment") == "I&C" for c in book), "no I&C premise on the roster to ask"

    no_cell = [(c["customer_id"], cell_weather_for_customer_id(c["customer_id"]).refusal)
               for c in book if not cell_weather_for_customer_id(c["customer_id"]).series]
    assert not no_cell, f"registered premises the world holds no weather for: {no_cell}"
