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
    assert rec.clearing_price_gbp_per_kw_year(2023, "T-1") == pytest.approx(60.00)
    # The label "T-4 auction 2023" named an auction and a year. 75.00 is the price of NEITHER of
    # that label's two prices, and this leg is the one that survives the record improving: it was
    # first written when 2023's T-1 was contested and null, and a null is not evidence that the
    # mislabelled constant was elsewhere. Now that the primary register has settled it at 60.00,
    # the claim is finally load-bearing rather than vacuously true.
    for auction in ("T-4", "T-1"):
        assert rec.clearing_price_gbp_per_kw_year(2023, auction) != pytest.approx(75.00)


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
    """Distinct absences, and a caller that cannot tell them apart will misrepair.

    KEYED TO THE PROPERTY, NOT TO WHICH YEARS ARE ABSENT. The first draft of this test named
    2016's T-4, 2023's T-1 and 2025's T-4 as its three subjects, and two of the three stopped
    being absent the moment the primary register was reached -- so it went red because the record
    got BETTER, which is exactly backwards. What must hold is that an absence is never zero and
    never a neighbour's number, and that its REASON is recoverable; which years are absent is the
    record's business and moves.
    """
    absences = [
        (y, a) for y in range(2016, 2030) for a in ("T-4", "T-1")
        if rec.clearing_price_gbp_per_kw_year(y, a) is None
    ]
    assert absences, "no absent price anywhere -- this test's whole partition is empty"

    for year, auction in absences:
        row = rec.delivery_year(year)
        prov = row.t4_provenance if auction == "T-4" else row.t1_provenance
        # An absence must SAY which kind it is. Silence here is the fail-silent shape.
        assert prov in ("not_applicable", "contested", "not_yet_held"), (
            f"{year} {auction} is absent under an unexplained provenance {prov!r}"
        )
        assert not row.established(auction)
        # ...and it is not zero, which is the reading that would book a real auction as paying
        # nothing, and not a neighbour's, which is what `.get(year, TABLE[2025])` used to do.
        neighbours = {
            rec.clearing_price_gbp_per_kw_year(year + d, a)
            for d in (-1, 1) for a in ("T-4", "T-1")
        } - {None}
        assert rec.clearing_price_gbp_per_kw_year(year, auction) not in ({0.0} | neighbours)

    # The three kinds are DIFFERENT repairs and must stay distinguishable: an auction that never
    # ran is repaired by nothing, one not yet held by waiting, a contested one by fetching the
    # primary source. At least the first two are live in the record today.
    assert rec.delivery_year(2016).t4_provenance == "not_applicable"
    assert "No T-4 or T-1 procured" in rec.delivery_year(2016).note
    assert rec.delivery_year(2027).t1_provenance == "not_yet_held"


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

    A figure nobody fetched must not be served as the published record.

    THE FIRST DRAFT ASSERTED `"403" in raw["primary_not_reached"]` -- that the artefact keep
    saying why NO entry was primary. That was right when every entry was an analyst's restatement
    and wrong the moment the register was actually reached, and it is worth keeping the wreckage
    named: a control that pins the CURRENT LIMIT goes red when the limit is lifted, which is the
    one direction nobody needs warning about. The durable property is that every served figure
    carries an accepted provenance AND names a route by which a reader could re-fetch it.
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
    # Re-fetchability is what makes "primary" checkable by the next reader rather than a word.
    urls = raw["source_urls"]
    assert urls["clearing_prices_and_volumes"].startswith("https://")
    assert urls["derating_factors"].startswith("https://")
    # The 403 that never was. Recorded because "the publisher blocks us" and "the publisher moved"
    # look identical in a status code's first digit and lead to opposite next actions -- one is a
    # dead end, the other is a redirect nobody followed for a whole pass.
    assert "404" in raw["primary_reached"] and "retired" in raw["primary_reached"]


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
    """A refusal that says why is how the refusal itself gets found to be wrong.

    AND IT WAS, BY THIS TEST, ON 2026-09-07 -- recorded here because the way it failed is the
    point. This leg used to read `assert "1,000 kW minimum CMU" in reason`, and it went RED when
    the refusal was rewritten to "the minimum CMU is 1,000 kW and the smallest awarded DSR CMU in
    the record sits at exactly that", i.e. when the claim acquired evidence and got NARROWER. A
    control keyed to today's word order goes red when the code becomes more honest and stays green
    when the claim rots -- exactly backwards. It now asserts the THRESHOLD IS PRESENT AND IS THE
    PUBLISHED ONE, which is the property, and says nothing about how the sentence is arranged.
    """
    reason = rec.DOMESTIC_PARTICIPATION_REFUSAL
    assert "cannot hold a Capacity Market agreement" in reason
    assert f"{rec.MINIMUM_CMU_CAPACITY_KW:,.0f} kW" in reason, (
        "the refusal must carry the published threshold as a number a reader can check")
    assert "aggregator" in reason and "bilateral" in reason


def test_the_threshold_arithmetic_is_exposed_and_checkable():
    """The quantity is reachable rather than only asserted in prose.

    THESE ARE THE ANSWERS AT RATED FLEX AND THEY ARE NO LONGER WHAT THE REFUSAL PUBLISHES. 12.4 kW
    is EV (7.4) + battery (5.0), the largest household in `flexibility_potential`, and 80.6 is
    what the refusal used to assert. The register says an aggregator contracts ~1.17 kW per
    domestic component, so the published figure is `HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED` (~858).
    The function still answers the rated question correctly; kept green here so the withdrawal is
    visible as a change of QUESTION rather than looking like a corrected division.
    """
    assert rec.households_per_minimum_cmu(12.4) == pytest.approx(80.6, abs=0.1)
    assert rec.households_per_minimum_cmu(3.0) == pytest.approx(333.3, abs=0.1)
    assert rec.households_per_minimum_cmu(0.0) is None
    assert rec.MINIMUM_CMU_CAPACITY_KW == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# De-rating: the gap the second pass filled from the publisher's own register
# ---------------------------------------------------------------------------

def test_derating_is_reachable_and_is_a_real_fraction():
    """THE POISON ROUND for every de-rating leg below.

    `derating_factor` returned `None` for every argument until the primary pass, and every test
    that asserts "unknown class is None" or "missing factor refuses" passes against a function
    that still does. So establish first that real factors come out, in quantity, before asserting
    anything about what does not.
    """
    got = [
        f for y in range(2016, 2030) for a in ("T-4", "T-1")
        if (f := rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, y, a)) is not None
    ]
    assert len(got) >= 20, f"only {len(got)} DSR factors -- the refusal legs below are vacuous"
    # A de-rating factor is a fraction of rated capacity. 1.0 would BE the defect this closed.
    assert all(0.0 < f < 1.0 for f in got)
    assert min(got) == pytest.approx(0.7145) and max(got) == pytest.approx(0.897)


def test_a_derating_factor_needs_an_auction_because_it_belongs_to_an_auction_round():
    """MUTATION: give `derating_factor` a default auction and this stops being checkable.

    The published factor is set per auction ROUND. A T-N auction for delivery year Y and the T-1
    auction for delivery year Y-N+1 are held in the SAME round against the same Electricity
    Capacity Report, so they carry the SAME factor. That identity is the evidence for the keying,
    and it is why a delivery year alone cannot name a factor.

    THE OFFSET IS N-1, AND THE PASS THAT WROTE THIS TEST FIRST GUESSED N. It predicted T-4[Y] ==
    T-1[Y-4] and this control refuted it on the first run: the true pairing is T-4[Y] ==
    T-1[Y-3], because a T-4 held in February of year H delivers from October H+3. Nine of ten
    pairs matched at Y-3 and none at all matched at Y-4, so the guess was not marginal -- and it
    was made while writing a warning about a four-year offset, which is how it survived being
    read three times. Left named because an off-by-one inside a caution about an off-by-one is
    the most re-enterable trap in this file.
    """
    offset_by_auction = {"T-4": 3, "T-3": 2}
    pairs = 0
    for year in range(2018, 2030):
        held = rec.auction_actually_held(year, "T-4")
        bulk = rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, year, "T-4")
        partner_year = year - offset_by_auction[held]
        partner = rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, partner_year, "T-1")
        if bulk is None or partner is None:
            continue
        pairs += 1
        assert bulk == pytest.approx(partner), (
            f"{held} DY{year} and T-1 DY{partner_year} are one auction round and must carry one "
            f"factor: {bulk} vs {partner}"
        )
    assert pairs >= 8, f"only {pairs} round-pairs checked -- the identity is barely exercised"

    # The substituted T-3 of DY 2022/23 obeys the SAME rule at its own N, which is the evidence
    # that the rule is about auction rounds and not a coincidence of the T-4 series.
    assert rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, 2022, "T-4") == pytest.approx(
        rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, 2020, "T-1"))

    # And the two auctions for ONE delivery year are different rounds, so they generally differ.
    # If this ever passed for every year, the auction argument would be doing nothing.
    differing = [
        y for y in range(2018, 2027)
        if (a := rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, y, "T-4")) is not None
        and (b := rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, y, "T-1")) is not None
        and a != pytest.approx(b)
    ]
    assert len(differing) >= 5, "T-4 and T-1 factors never differ -- the auction argument is inert"


def test_the_suspended_t4_of_2022_takes_its_factor_from_the_t3_that_replaced_it():
    """THE ONE PLACE A PRICE AND A FACTOR COULD COME FROM TWO DIFFERENT AUCTIONS.

    MUTATION: make `auction_actually_held` return its argument unchanged, and this fires -- the
    de-rated price silently becomes 6.44 x 0.8428 instead of 6.44 x 0.8614.

    DY 2022/23's T-4 was suspended and replaced by a T-3. The T-3's price sits in the row's `t4`
    field, so the price lookup returns a T-3 number under a T-4 label; the register publishes
    factors for BOTH auctions and they differ. A caller multiplying this module's price by this
    module's factor would have crossed two auctions and produced a number with no auction behind
    it at all -- which is this module's founding defect in miniature.
    """
    assert rec.auction_actually_held(2022, "T-4") == "T-3"
    assert rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, 2022, "T-4") == pytest.approx(0.8614)
    # The suspended T-4's own factor IS published and is NOT the one used. If these were equal the
    # test above would prove nothing, so assert they are genuinely different numbers.
    suspended = rec._DERATING[(2022, "T-4")][rec.DSR_TECHNOLOGY_CLASS]
    assert suspended == pytest.approx(0.8428)
    assert suspended != pytest.approx(0.8614)
    assert rec.derated_price_gbp_per_kw_year(2022, "T-4", rec.DSR_TECHNOLOGY_CLASS) == (
        pytest.approx(round(6.44 * 0.8614, 4))
    )
    # Every other year in the record is its own auction; the substitution is not a general rule.
    for year in (2021, 2023, 2024, 2025):
        assert rec.auction_actually_held(year, "T-4") == "T-4"


def test_a_de_rated_price_is_strictly_below_the_rated_one_for_every_established_year():
    """The property, not a number: de-rating REDUCES, always, everywhere.

    MUTATION: drop the multiplication in `derated_price_gbp_per_kw_year` and every year fires.
    Keyed to the relationship so it survives the register being re-fetched with new factors, and
    stated over the whole partition rather than a leg per year, so a factor that crept to 1.0 for
    one technology class in one auction cannot hide behind the others.
    """
    checked = 0
    for year in range(2016, 2030):
        for auction in ("T-4", "T-1"):
            rated = rec.clearing_price_gbp_per_kw_year(year, auction)
            derated = rec.derated_price_gbp_per_kw_year(
                year, auction, rec.DSR_TECHNOLOGY_CLASS)
            if rated is None or derated is None:
                continue
            checked += 1
            assert 0.0 < derated < rated, f"{year} {auction}: {derated} not below {rated}"
    assert checked >= 20, f"only {checked} year-auctions checked"


def test_a_missing_factor_refuses_the_whole_answer_rather_than_returning_the_rated_price():
    """MUTATION: `factor or 1.0` anywhere in the chain and this fires.

    HALF AN ANSWER IS THE DEFECT, not a degraded version of it. A price with no factor IS the
    rated-capacity overstatement that this whole pass existed to end, so `None` for the factor
    must take the price down with it rather than falling through to the undiscounted number.
    """
    unlisted = "Fusion"
    assert rec.derating_factor(unlisted, 2024, "T-4") is None
    assert rec.derated_price_gbp_per_kw_year(2024, "T-4", unlisted) is None
    # ...specifically NOT the rated price, which is what a `or 1.0` fallback would return.
    assert rec.clearing_price_gbp_per_kw_year(2024, "T-4") == pytest.approx(18.00)

    # A year the register does not cover refuses on both legs, and outside the record entirely.
    assert rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, 2040, "T-4") is None
    assert rec.derated_price_gbp_per_kw_year(2040, "T-4", rec.DSR_TECHNOLOGY_CLASS) is None
    # A year with a factor but no price refuses too: 2016 is in the de-rating register (the TR
    # auction) and has no T-4 clearing price at all.
    assert rec.derated_price_gbp_per_kw_year(2016, "T-4", rec.DSR_TECHNOLOGY_CLASS) is None


def test_dsr_is_not_duration_split_but_storage_is():
    """The artefact's v1 prose said de-rating was duration-dependent "for DSR and storage".

    The publisher's register says that is true of STORAGE alone: DSR carries one factor per
    auction. This matters to the I&C leg, which would otherwise need a duration model it cannot
    source -- and it is the kind of claim that gets copied forward as received wisdom, so it is
    pinned against the register rather than against the sentence that asserted it.
    """
    latest = rec._DERATING[(2029, "T-4")]
    dsr_classes = [c for c in latest if "DSR" in c]
    assert dsr_classes == [rec.DSR_TECHNOLOGY_CLASS], f"DSR appears as {dsr_classes}"
    storage_durations = [c for c in latest if c.startswith("Storage (Duration")]
    assert len(storage_durations) >= 10, "storage duration classes missing -- is this the register?"


def test_a_missing_derating_block_raises_rather_than_defaulting_to_no_de_rating(
        tmp_path, monkeypatch):
    """NO FAIL-OPEN PATH (R15), and this one is the subtlest in the module.

    MUTATION: `return {}` instead of raising, and every factor becomes `None`... which, in a
    caller written with `or 1.0`, is arithmetically identical to NO DE-RATING. An absent register
    is not a factor of 1.0, and the failure has to be loud at load rather than quiet at each call.
    """
    bad = tmp_path / "no_derating.json"
    bad.write_text(json.dumps({"clearing_prices": [{"delivery_year": 2024}]}))
    monkeypatch.setattr(rec, "_COMMONS", bad)
    with pytest.raises(ValueError, match="not a factor of 1.0"):
        rec._load_derating()


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


# --- The DSR CMU shape pass, 2026-09-07 (a51). What the publisher's own register said about the
# --- refusal, and the controls that stop it drifting back to the arithmetic it used to rest on.


def test_the_refusal_no_longer_claims_a_household_cannot_reach_the_capacity_market():
    """The defect: the refusal asserted a participation impossibility the register refutes.

    Keyed to the PROPERTY -- the refusal must rest on the unpublished pass-through -- not to
    today's wording. A refusal that says "cannot hold an agreement in its own right" is fine; one
    that says a household does not reach the market at all is the refuted claim, and the register
    names eight GB operators aggregating domestic turn-down into awarded CMUs.
    """
    refusal = rec.DOMESTIC_PARTICIPATION_REFUSAL.lower()
    assert "in its own right" in refusal, (
        "the threshold claim must be narrowed to holding an agreement DIRECTLY; the register "
        "refutes the unqualified version")
    assert "passes through" in refusal or "pass-through" in refusal, (
        "the pass-through is now the ONLY ground the refusal stands on and must be stated")
    assert "~80" not in rec.DOMESTIC_PARTICIPATION_REFUSAL, (
        "the ~80 households figure divided by RATED flex and is withdrawn; the register's own "
        f"figure is ~{rec.HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED:.0f}")


def test_the_observed_component_scale_is_far_below_this_books_rated_household_flex():
    """The defect: publishing a household count computed from rated asset power.

    This is the whole finding in one assertion. `flexibility_potential` calls a whole flexible
    house 3.0-15.4 kW of RATED power; the register says an aggregator contracts ~1.17 kW per
    domestic component. Both numbers are right and their ratio is the error that was published.
    """
    rated_whole_house_kw = 15.4  # the largest in flexibility_potential (EV + ASHP + battery)
    observed = rec.OBSERVED_DOMESTIC_COMPONENT_KW
    assert 0.3 < observed < 3.0, (
        f"observed domestic component scale {observed} kW is outside anything the register "
        "supports; a value near the rated figure means the join picked up industrial CMUs")
    assert observed < rated_whole_house_kw / 5, (
        "the observed and rated figures must stay far apart -- if they converge, either the "
        "register changed or this constant stopped measuring contracted capacity")
    # ...and the household count moves the same way, by the same ratio.
    at_rated = rec.households_per_minimum_cmu(rated_whole_house_kw)
    assert rec.HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED > at_rated * 5, (
        f"{rec.HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED} observed vs {at_rated} at rated flex -- the "
        "gap between the two questions is the finding, and a control that let them converge "
        "would go green exactly when the error came back")


def test_the_observed_household_count_is_the_threshold_over_the_observed_scale():
    """The defect: two published constants that could drift apart into disagreement.

    Not a tautology -- the two are loaded from separate keys of the commons artefact, computed
    from different aggregations of the register, and nothing in the loader ties them together.
    """
    implied = rec.MINIMUM_CMU_CAPACITY_KW / rec.OBSERVED_DOMESTIC_COMPONENT_KW
    assert abs(implied - rec.HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED) < 1.0, (
        f"{implied:.1f} implied vs {rec.HOUSEHOLDS_PER_MINIMUM_CMU_OBSERVED} published")


def test_domestic_aggregation_is_observed_inside_the_run_window_not_only_after_it():
    """The defect: refuting the refusal with evidence the company could not have seen.

    If domestic DSR CMUs only appeared in DY2026+ the refutation would sit outside the 2016-2025
    run window and a supplier living through it could not have read them. The register's first
    domestic-shaped awarded CMU is DY2023, which is inside -- and that is what makes this a
    finding about the company's world rather than about the future.
    """
    first = rec.DOMESTIC_AGGREGATION_FIRST_OBSERVED_DELIVERY_YEAR
    assert first <= rec.RUN_WINDOW_LAST_DELIVERY_YEAR, (
        f"first observed domestic aggregation is DY{first}, outside the run window ending "
        f"{rec.RUN_WINDOW_LAST_DELIVERY_YEAR} -- the refutation would not be company-observable")
    assert first >= rec.FIRST_DELIVERY_YEAR
