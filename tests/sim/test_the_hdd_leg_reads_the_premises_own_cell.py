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

#: A premise the store genuinely holds NO cell for: Birmingham, 7.4 km from the nearest held cell
#: against a `MAX_SNAP_KM` of 5.0. The remedy is `fabric_demand_path.ADD_THE_CELL_REMEDY` -- add
#: the cell -- never a per-property pull, which is the design the director refused on 2026-09-16.
REFUSED = "C_IC1"

#: Two mid-January days ten degrees of winter apart in the real record. 2022 is a fact, not a
#: scenario: a premise on the normal reads the SAME number in both, which is the whole defect.
COLD_YEAR_DAY = "2018-01-15"
MILD_YEAR_DAY = "2022-01-15"


def test_the_resolver_discriminates_a_premise_with_a_cell_from_one_without():
    """ONE control over the whole partition. Reds if the resolver answers one way for everything.

    Make `_premise_sky` return an empty series for every id and the HELD leg reds (it reads the
    normal, and its two years collapse to one number). Make it return a cell for every id and the
    REFUSED leg reds (its basis no longer names the substitution). Neither mutation survives.
    """
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
        f"{REFUSED} is 7.4 km outside the store; a reading that claims to be weather for it is "
        f"claiming a cell that does not exist. basis={refused_cold.basis!r}"
    )
    assert refused_cold.basis.startswith(NORMAL_BASIS_PREFIX), refused_cold.basis
    assert "7.4 km" in refused_cold.basis, (
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
