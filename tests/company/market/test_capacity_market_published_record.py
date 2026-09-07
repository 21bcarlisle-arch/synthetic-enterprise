"""The published CM auction record: one home, two auctions, and a refusal that names its reason.

WHAT THIS FILE EXISTS FOR (2026-09-07,
SEAT_FINDING_THE_CAPACITY_MARKET_PRICE_HAS_TWO_HOMES_THAT_DISAGREE_BY_4_POINT_7X...).
`_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0  # T-4 auction 2023` was multiplied by a household's RATED
asset power, unconditionally, for GBP930/household/year. The 75.0 is real -- it is the T-1 clearing
price for DELIVERY YEAR 2022/23, which cleared at the price cap -- and every word of its label was
wrong. Two further homes held the same publication at different values under different names.

Each test below names the defect it would catch. The legs that matter most are the ones about
REFUSAL, because a refusal that cannot fail is indistinguishable from a lookup that returns
nothing, and this module refuses in four different places.
"""
from __future__ import annotations

import json

import pytest

from company.market import capacity_market_published_record as rec

# ---------------------------------------------------------------------------
# The record itself
# ---------------------------------------------------------------------------

def test_the_mislabelled_75_is_the_t1_for_delivery_year_2022_23():
    """The research answer, pinned where the next reader will find it.

    Both of this repo's mislabelled constants were this figure. The finding that opened this work
    said "Nothing in docs/market_research/ establishes it" and treated its identity as the open
    research question; the repo's own commons DID establish it, in the very file
    `ic_flexibility_revenue.py` cited as its source -- nobody had read the T-1 column.
    """
    assert rec.clearing_price_gbp_per_kw_year(2022, "T-1") == pytest.approx(75.00)
    # ...and it is NOT the T-4 for that year, nor any price for 2023, which is what its two
    # comments claimed ("T-4 auction 2023" and "Crisis year spike").
    assert rec.clearing_price_gbp_per_kw_year(2022, "T-4") == pytest.approx(6.44)
    assert rec.clearing_price_gbp_per_kw_year(2023, "T-4") == pytest.approx(15.97)
    assert rec.clearing_price_gbp_per_kw_year(2023, "T-1") is None


def test_asking_for_the_cm_price_without_naming_an_auction_is_refused():
    """MUTATION: give `price` a default auction and this stops raising.

    The defect: a delivery year has TWO clearing prices and they differed by 11.6x in 2022/23. A
    lookup that lets a caller not choose has chosen for them.
    """
    row = rec.delivery_year(2022)
    with pytest.raises(ValueError, match="T-4"):
        row.price("T4")
    with pytest.raises(ValueError, match="conflation"):
        row.price("whatever")


def test_an_unestablished_year_is_none_and_not_zero_and_not_a_neighbour():
    """Three distinct absences, and a caller that cannot tell them apart will misrepair.

    2016 had no T-4 delivery at all; 2023's T-1 is contested between two sources; 2025's T-4 is
    contested. None of the three is zero, and none may silently borrow the adjacent year -- which
    is exactly what the deleted `.get(year, TABLE[2025])` did.
    """
    assert rec.clearing_price_gbp_per_kw_year(2016, "T-4") is None
    assert rec.clearing_price_gbp_per_kw_year(2023, "T-1") is None
    assert rec.clearing_price_gbp_per_kw_year(2025, "T-4") is None
    # each carries a reason a reader can act on, and they are DIFFERENT reasons: an auction that
    # never ran is repaired by nothing, a contested one by fetching the primary source.
    assert rec.delivery_year(2016).t4_provenance == "not_applicable"
    assert "No T-4 delivery had begun" in rec.delivery_year(2016).note
    assert rec.delivery_year(2023).t1_provenance == "contested"
    assert "45.00" in rec.delivery_year(2023).note and "60" in rec.delivery_year(2023).note
    assert rec.delivery_year(2025).t4_provenance == "contested"


def test_the_record_is_not_uniformly_absent():
    """THE POISON ROUND for every refusal leg above.

    "Returns None" and "refuses correctly" are the same observation on a module that returns None
    for everything, and every refusal test in this file would pass against such a module. This is
    the control over the whole partition: real prices must be reachable, in both auctions.
    """
    t4 = [p for y in range(2016, 2029)
          if (p := rec.clearing_price_gbp_per_kw_year(y, "T-4")) is not None]
    t1 = [p for y in range(2016, 2029)
          if (p := rec.clearing_price_gbp_per_kw_year(y, "T-1")) is not None]
    assert len(t4) >= 8, f"only {len(t4)} established T-4 prices — refusal legs are vacuous"
    assert len(t1) >= 6, f"only {len(t1)} established T-1 prices — refusal legs are vacuous"
    assert min(t4) == pytest.approx(6.44) and max(t4) == pytest.approx(65.00)


def test_no_delivery_year_serves_a_price_it_did_not_fetch():
    """MUTATION: add a row with provenance 'recalled' and a price, and loading raises.

    A figure nobody fetched must not be served as the published record. This artefact has NO
    primary-provenance entries at all -- the EMR Delivery Body register returned 403 to the pass
    that wrote it -- and that limit is stated in the file rather than left for a reader to assume
    the opposite.
    """
    raw = json.loads(rec._COMMONS.read_text())
    for row in raw["clearing_prices"]:
        for price_key, prov_key in (("t4_gbp_per_kw_year", "t4_provenance"),
                                    ("t1_gbp_per_kw_year", "t1_provenance")):
            if row[price_key] is not None:
                assert row[prov_key] in rec._ACCEPTED_PROVENANCE, (
                    f"delivery year {row['delivery_year']} serves a {price_key} under "
                    f"provenance {row[prov_key]!r}"
                )
    assert "403" in raw["primary_not_reached"], (
        "the artefact must keep saying WHY no entry is primary; a limit that stops being stated "
        "reads, one pass later, as a limit that was lifted"
    )


# ---------------------------------------------------------------------------
# The product question: can a household hold a CM agreement?
# ---------------------------------------------------------------------------

def test_a_household_cannot_hold_a_cm_agreement_at_any_size():
    """The refusal is about the AGREEMENT, not about the size of the asset.

    MUTATION: make `household_revenue_gbp_pa` return a number above some kW threshold and this
    fires on the large case. A refusal keyed to size would let a big-enough household through,
    and no household is big enough: the minimum CMU is 1 MW.
    """
    for flex_kw in (0.5, 3.0, 7.4, 12.4, 15.4, 999.0):
        assert rec.household_revenue_gbp_pa(flex_kw) is None, (
            f"{flex_kw} kW household was credited with CM revenue"
        )


def test_the_refusal_names_its_reason_and_the_reason_carries_the_threshold():
    """A refusal that says why is how the refusal itself gets found to be wrong."""
    reason = rec.DOMESTIC_PARTICIPATION_REFUSAL
    assert "cannot hold a Capacity Market agreement" in reason
    assert "1,000 kW minimum CMU" in reason
    assert "aggregator" in reason and "bilateral" in reason


def test_the_threshold_arithmetic_is_exposed_and_checkable():
    """~80 households per minimum CMU at the book's largest asset combination.

    The refusal's claim is quantitative, so the quantity is reachable rather than only asserted in
    prose. 12.4 kW is EV (7.4) + battery (5.0), the largest household in `flexibility_potential`.
    """
    assert rec.households_per_minimum_cmu(12.4) == pytest.approx(80.6, abs=0.1)
    assert rec.households_per_minimum_cmu(3.0) == pytest.approx(333.3, abs=0.1)
    assert rec.households_per_minimum_cmu(0.0) is None
    assert rec.MINIMUM_CMU_CAPACITY_KW == pytest.approx(1000.0)


def test_derating_is_an_honest_gap_and_says_so_for_every_class():
    """MUTATION: return a plausible 0.2 for DSR and this fires.

    The CM pays on DE-RATED capacity and no de-rating factor was fetched. A factor invented to
    fill this slot would be indistinguishable from a published one within a week, which is the
    failure this whole pass was about — so the gap stays a refusal rather than a default.
    """
    for cls in ("dsr", "battery", "ccgt", "interconnector", ""):
        assert rec.derating_factor(cls) is None


# ---------------------------------------------------------------------------
# The seam does not fail open
# ---------------------------------------------------------------------------

def test_a_missing_commons_artefact_raises_rather_than_defaulting(tmp_path, monkeypatch):
    """NO FAIL-OPEN PATH (R15). An unavailable record is not a licence to invent one.

    MUTATION: give `_load` an `except FileNotFoundError: return {}` and this stops raising — and
    every price lookup in the module then returns `None` while reporting no problem, which is the
    fail-silent shape that let GBP75/kW run as a household's annual revenue.
    """
    monkeypatch.setattr(rec, "_COMMONS", tmp_path / "absent.json")
    with pytest.raises(FileNotFoundError, match="no invented default"):
        rec._load()

    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"clearing_prices": []}))
    monkeypatch.setattr(rec, "_COMMONS", empty)
    with pytest.raises(ValueError, match="no clearing_prices"):
        rec._load()
